"""SC039 source-only joint storage/replay/namespace control-plane checkpoint.

This extends the earlier storage+grant-replay authority checkpoint concept by
also binding the durable SC038 namespace-binding ledger. Injected signers and
sinks are synthetic until independently operated and owner-approved.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Mapping, Protocol

from .contracts import CloudError, IntegrityError, valid_sha256
from .journal import SQLiteOperationalJournal
from .namespace_bindings import SQLiteNamespaceBindingLedger
from .tower_grants import SQLiteNonceReplayStore

_SCHEMA_V1 = "simplee.cloud.control-checkpoint.v1"
_SCHEMA_V2 = "simplee.cloud.control-checkpoint.v2"
_FIELDS_V1 = frozenset({
    "schema", "checkpoint_ref", "key_id",
    "storage_event_count", "storage_head_sha256",
    "replay_event_count", "replay_head_sha256",
    "namespace_event_count", "namespace_head_sha256",
    "previous_checkpoint_sha256", "created_at_utc",
})
_FIELDS_V2 = _FIELDS_V1 | frozenset({
    "namespace_binding_key_commitment_sha256",
})
_ID = re.compile(r"[A-Za-z0-9_.:-]{1,64}\Z")
_REF = re.compile(r"control-checkpoints/[0-9a-f]{48}\Z")
_ZERO = "0" * 64


@dataclass(frozen=True)
class SignedControlCheckpoint:
    payload: bytes
    signature: bytes

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.payload + b"." + self.signature).hexdigest()


class ControlCheckpointSink(Protocol):
    def put_if_absent(
        self, reference: str, checkpoint: SignedControlCheckpoint,
    ) -> None: ...

    def get(self, reference: str) -> SignedControlCheckpoint: ...


def _strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise IntegrityError("duplicate control checkpoint property")
        result[key] = value
    return result


def _claims(payload: bytes) -> dict:
    if not isinstance(payload, bytes) or not 1 <= len(payload) <= 4096:
        raise IntegrityError("invalid control checkpoint payload")
    try:
        doc = json.loads(
            payload.decode("utf-8"), object_pairs_hook=_strict_pairs,
        )
        if not isinstance(doc, dict):
            raise IntegrityError("unexpected control checkpoint claims")
        schema = doc.get("schema")
        expected_fields = (
            _FIELDS_V1 if schema == _SCHEMA_V1 else
            _FIELDS_V2 if schema == _SCHEMA_V2 else
            None
        )
        if expected_fields is None or set(doc) != expected_fields:
            raise IntegrityError("unexpected control checkpoint claims")
        canonical = json.dumps(
            doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode()
        if canonical != payload:
            raise IntegrityError("control checkpoint encoding not canonical")
        return doc
    except (UnicodeError, TypeError, ValueError) as exc:
        raise IntegrityError("malformed control checkpoint") from exc


def verify_control_checkpoint(
    signed: SignedControlCheckpoint, *,
    pinned_public_keys: Mapping[str, bytes],
    journal: SQLiteOperationalJournal | None = None,
    replay_store: SQLiteNonceReplayStore | None = None,
    namespace_bindings: SQLiteNamespaceBindingLedger | None = None,
) -> dict:
    if not isinstance(signed, SignedControlCheckpoint):
        raise IntegrityError("signed control checkpoint required")
    doc = _claims(signed.payload)
    if (
        doc["schema"] not in (_SCHEMA_V1, _SCHEMA_V2) or
        not isinstance(doc["checkpoint_ref"], str) or
        _REF.fullmatch(doc["checkpoint_ref"]) is None
    ):
        raise IntegrityError("wrong control checkpoint schema/reference")
    key_id = doc["key_id"]
    if not isinstance(key_id, str) or _ID.fullmatch(key_id) is None:
        raise IntegrityError("invalid control checkpoint key identity")
    if not isinstance(pinned_public_keys, Mapping):
        raise IntegrityError("independent control-checkpoint trust roots required")
    public = pinned_public_keys.get(key_id)
    if (
        not isinstance(public, bytes) or len(public) != 32 or
        not isinstance(signed.signature, bytes) or len(signed.signature) != 64
    ):
        raise IntegrityError("unknown control checkpoint signer or malformed signature")
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        Ed25519PublicKey.from_public_bytes(public).verify(
            signed.signature, signed.payload,
        )
    except (ValueError, InvalidSignature) as exc:
        raise IntegrityError("control checkpoint signature mismatch") from exc

    for field in (
        "storage_event_count", "replay_event_count", "namespace_event_count",
    ):
        if type(doc[field]) is not int or doc[field] < 0:
            raise IntegrityError("invalid control checkpoint event count")
    for field in (
        "storage_head_sha256", "replay_head_sha256", "namespace_head_sha256",
        "previous_checkpoint_sha256",
    ):
        if not valid_sha256(doc[field]):
            raise IntegrityError("invalid control checkpoint hash")
    if (
        doc["schema"] == _SCHEMA_V2 and
        not valid_sha256(doc["namespace_binding_key_commitment_sha256"])
    ):
        raise IntegrityError("invalid namespace binding key commitment hash")
    if (
        not isinstance(doc["created_at_utc"], str) or
        not doc["created_at_utc"].endswith("Z")
    ):
        raise IntegrityError("control checkpoint UTC timestamp required")

    if journal is not None:
        if not isinstance(journal, SQLiteOperationalJournal):
            raise IntegrityError("verified Cloud journal required")
        if journal.checkpoint_head(
            doc["storage_event_count"]
        ) != doc["storage_head_sha256"]:
            raise IntegrityError("control checkpoint storage prefix mismatch")

    if replay_store is not None:
        if not isinstance(replay_store, SQLiteNonceReplayStore):
            raise IntegrityError("verified Tower replay store required")
        try:
            replay_head = replay_store.checkpoint_head(doc["replay_event_count"])
        except Exception as exc:
            raise IntegrityError(
                "control checkpoint replay prefix unavailable"
            ) from exc
        if replay_head != doc["replay_head_sha256"]:
            raise IntegrityError("control checkpoint replay prefix mismatch")

    if namespace_bindings is not None:
        if not isinstance(namespace_bindings, SQLiteNamespaceBindingLedger):
            raise IntegrityError("verified namespace binding ledger required")
        try:
            namespace_head = namespace_bindings.checkpoint_head(
                doc["namespace_event_count"]
            )
        except Exception as exc:
            raise IntegrityError(
                "control checkpoint namespace prefix unavailable"
            ) from exc
        if namespace_head != doc["namespace_head_sha256"]:
            raise IntegrityError("control checkpoint namespace prefix mismatch")
        if doc["schema"] == _SCHEMA_V2:
            key_doc = namespace_bindings.source_binding_key_commitment()
            if not hmac.compare_digest(
                key_doc["binding_key_commitment"],
                doc["namespace_binding_key_commitment_sha256"],
            ):
                raise IntegrityError(
                    "control checkpoint namespace binding-key commitment mismatch"
                )
    return dict(doc)


def seal_source_control_checkpoint(
    *, journal: SQLiteOperationalJournal,
    replay_store: SQLiteNonceReplayStore,
    namespace_bindings: SQLiteNamespaceBindingLedger,
    key_id: str,
    external_signer: Callable[[bytes], bytes],
    pinned_public_keys: Mapping[str, bytes],
    previous: SignedControlCheckpoint | None = None,
    mode: str = "disabled",
) -> SignedControlCheckpoint:
    if mode != "source_test":
        raise CloudError("live control checkpoint signing disabled")
    if (
        not isinstance(journal, SQLiteOperationalJournal) or
        not isinstance(replay_store, SQLiteNonceReplayStore) or
        not isinstance(namespace_bindings, SQLiteNamespaceBindingLedger)
    ):
        raise CloudError("verified storage/replay/namespace ledgers required")
    if (
        not isinstance(key_id, str) or _ID.fullmatch(key_id) is None or
        not callable(external_signer)
    ):
        raise CloudError("approved external control signer callback required")

    storage = journal.verify_chain()
    replay = replay_store.verify_chain()
    namespace = namespace_bindings.verify_chain()
    namespace_key = namespace_bindings.source_binding_key_commitment()
    previous_digest = _ZERO
    if previous is not None:
        prior = verify_control_checkpoint(
            previous, pinned_public_keys=pinned_public_keys,
            journal=journal, replay_store=replay_store,
            namespace_bindings=namespace_bindings,
        )
        current_vector = (
            storage["event_count"], replay["event_count"],
            namespace["event_count"],
        )
        prior_vector = (
            prior["storage_event_count"], prior["replay_event_count"],
            prior["namespace_event_count"],
        )
        if any(now < then for now, then in zip(current_vector, prior_vector)) or (
            current_vector == prior_vector
        ):
            raise CloudError(
                "new control checkpoint requires monotonic ledger progress"
            )
        previous_digest = previous.sha256

    payload = json.dumps({
        "schema": _SCHEMA_V2,
        "checkpoint_ref": "control-checkpoints/" + secrets.token_hex(24),
        "key_id": key_id,
        "storage_event_count": storage["event_count"],
        "storage_head_sha256": storage["head_sha256"],
        "replay_event_count": replay["event_count"],
        "replay_head_sha256": replay["head_sha256"],
        "namespace_event_count": namespace["event_count"],
        "namespace_head_sha256": namespace["head_sha256"],
        "namespace_binding_key_commitment_sha256": namespace_key["binding_key_commitment"],
        "previous_checkpoint_sha256": previous_digest,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()

    sealed = SignedControlCheckpoint(payload, external_signer(payload))
    verify_control_checkpoint(
        sealed, pinned_public_keys=pinned_public_keys,
        journal=journal, replay_store=replay_store,
        namespace_bindings=namespace_bindings,
    )
    return sealed


def deliver_source_control_checkpoint(
    *, signed: SignedControlCheckpoint,
    sink: ControlCheckpointSink,
    pinned_public_keys: Mapping[str, bytes],
    journal: SQLiteOperationalJournal,
    replay_store: SQLiteNonceReplayStore,
    namespace_bindings: SQLiteNamespaceBindingLedger,
    mode: str = "disabled",
) -> str:
    if mode != "source_test":
        raise CloudError("live control checkpoint delivery disabled")
    if sink is None or not all(
        callable(getattr(sink, method, None))
        for method in ("put_if_absent", "get")
    ):
        raise CloudError("control checkpoint sink with verified read-back required")

    doc = verify_control_checkpoint(
        signed, pinned_public_keys=pinned_public_keys,
        journal=journal, replay_store=replay_store,
        namespace_bindings=namespace_bindings,
    )
    sink.put_if_absent(doc["checkpoint_ref"], signed)
    try:
        returned = sink.get(doc["checkpoint_ref"])
    except Exception as exc:
        raise IntegrityError(
            "control checkpoint read-back unavailable; reconcile independently"
        ) from exc
    if (
        not isinstance(returned, SignedControlCheckpoint) or
        not isinstance(returned.payload, bytes) or
        not isinstance(returned.signature, bytes) or
        not hmac.compare_digest(returned.payload, signed.payload) or
        not hmac.compare_digest(returned.signature, signed.signature)
    ):
        raise IntegrityError(
            "externally stored control checkpoint differs from signed original"
        )
    verify_control_checkpoint(
        returned, pinned_public_keys=pinned_public_keys,
        journal=journal, replay_store=replay_store,
        namespace_bindings=namespace_bindings,
    )
    return doc["checkpoint_ref"]


def verify_source_control_checkpoint_sequence(
    *, checkpoints: list[SignedControlCheckpoint] |
                     tuple[SignedControlCheckpoint, ...],
    pinned_public_keys: Mapping[str, bytes],
    journal: SQLiteOperationalJournal,
    replay_store: SQLiteNonceReplayStore,
    namespace_bindings: SQLiteNamespaceBindingLedger,
    mode: str = "disabled",
) -> dict:
    if mode != "source_test":
        raise CloudError("control checkpoint lineage runtime disabled")
    if not isinstance(checkpoints, (list, tuple)) or not 1 <= len(checkpoints) <= 256:
        raise CloudError("bounded control checkpoint history required")

    previous = None
    prior = (-1, -1, -1)
    refs = set()
    tip = None
    for signed in checkpoints:
        doc = verify_control_checkpoint(
            signed, pinned_public_keys=pinned_public_keys,
            journal=journal, replay_store=replay_store,
            namespace_bindings=namespace_bindings,
        )
        expected_link = _ZERO if previous is None else previous.sha256
        if doc["previous_checkpoint_sha256"] != expected_link:
            raise IntegrityError("control checkpoint lineage gap or fork")
        if doc["checkpoint_ref"] in refs:
            raise IntegrityError("duplicate control checkpoint reference")
        current = (
            doc["storage_event_count"], doc["replay_event_count"],
            doc["namespace_event_count"],
        )
        if previous is not None and (
            any(now < then for now, then in zip(current, prior)) or
            current == prior
        ):
            raise IntegrityError("nonmonotonic control checkpoint")
        refs.add(doc["checkpoint_ref"])
        prior = current
        previous, tip = signed, doc

    return {
        "status": "SOURCE_ONLY_CONTROL_LINEAGE_CHECKED",
        "checkpoint_count": len(checkpoints),
        "latest_checkpoint_ref": tip["checkpoint_ref"],
        "latest_storage_event_count": tip["storage_event_count"],
        "latest_replay_event_count": tip["replay_event_count"],
        "latest_namespace_event_count": tip["namespace_event_count"],
        "storage_prefix_matches": True,
        "replay_prefix_matches": True,
        "namespace_prefix_matches": True,
        "namespace_binding_key_commitment_in_tip": (
            tip["schema"] == _SCHEMA_V2
        ),
        "namespace_binding_key_commitment_matches_current": (
            tip["schema"] == _SCHEMA_V2
        ),
        "actual_external_latest_attested": False,
        "independent_offsite_immutability_certified": False,
        "production_authorized": False,
    }
