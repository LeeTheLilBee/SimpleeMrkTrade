"""SC020 source-only joint storage/replay authority checkpoint contract.

The checkpoint signs BOTH the Cloud operational journal prefix and one-use Tower
grant replay prefix. Injected signer/sink are synthetic until independently
operated and owner-approved. No private signing key or live provider is owned
here.
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
from .tower_grants import SQLiteNonceReplayStore

_SCHEMA = "simplee.cloud.authority-checkpoint.v1"
_FIELDS = frozenset({
    "schema", "checkpoint_ref", "key_id",
    "storage_event_count", "storage_head_sha256",
    "replay_event_count", "replay_head_sha256",
    "previous_checkpoint_sha256", "created_at_utc",
})
_ID = re.compile(r"[A-Za-z0-9_.:-]{1,64}\Z")
_REF = re.compile(r"authority-checkpoints/[0-9a-f]{48}\Z")
_ZERO = "0" * 64


@dataclass(frozen=True)
class SignedAuthorityCheckpoint:
    payload: bytes
    signature: bytes

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.payload + b"." + self.signature).hexdigest()


class AuthorityCheckpointSink(Protocol):
    def put_if_absent(
        self, reference: str, checkpoint: SignedAuthorityCheckpoint,
    ) -> None: ...
    def get(self, reference: str) -> SignedAuthorityCheckpoint: ...


def _strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise IntegrityError("duplicate authority checkpoint property")
        result[key] = value
    return result


def _claims(payload: bytes) -> dict:
    if not isinstance(payload, bytes) or not 1 <= len(payload) <= 3072:
        raise IntegrityError("invalid authority checkpoint payload")
    try:
        doc = json.loads(payload.decode("utf-8"), object_pairs_hook=_strict_pairs)
        if not isinstance(doc, dict) or set(doc) != _FIELDS:
            raise IntegrityError("unexpected authority checkpoint claims")
        canonical = json.dumps(
            doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode()
        if canonical != payload:
            raise IntegrityError("authority checkpoint encoding not canonical")
        return doc
    except (UnicodeError, TypeError, ValueError) as exc:
        raise IntegrityError("malformed authority checkpoint") from exc


def verify_authority_checkpoint(
    signed: SignedAuthorityCheckpoint, *,
    pinned_public_keys: Mapping[str, bytes],
    journal: SQLiteOperationalJournal | None = None,
    replay_store: SQLiteNonceReplayStore | None = None,
) -> dict:
    if not isinstance(signed, SignedAuthorityCheckpoint):
        raise IntegrityError("signed authority checkpoint required")
    doc = _claims(signed.payload)
    if (
        doc["schema"] != _SCHEMA or
        not isinstance(doc["checkpoint_ref"], str) or
        not _REF.fullmatch(doc["checkpoint_ref"])
    ):
        raise IntegrityError("wrong authority checkpoint schema/reference")
    key_id = doc["key_id"]
    if not isinstance(key_id, str) or not _ID.fullmatch(key_id):
        raise IntegrityError("invalid authority checkpoint key identity")
    if not isinstance(pinned_public_keys, Mapping):
        raise IntegrityError("independent public-key trust roots required")
    public = pinned_public_keys.get(key_id)
    if (
        not isinstance(public, bytes) or len(public) != 32 or
        not isinstance(signed.signature, bytes) or len(signed.signature) != 64
    ):
        raise IntegrityError("unknown authority signer or malformed signature")
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        Ed25519PublicKey.from_public_bytes(public).verify(
            signed.signature, signed.payload,
        )
    except (ValueError, InvalidSignature) as exc:
        raise IntegrityError("authority checkpoint signature mismatch") from exc

    for field in ("storage_event_count", "replay_event_count"):
        if type(doc[field]) is not int or doc[field] < 0:
            raise IntegrityError("invalid authority checkpoint event count")
    for field in (
        "storage_head_sha256", "replay_head_sha256",
        "previous_checkpoint_sha256",
    ):
        if not valid_sha256(doc[field]):
            raise IntegrityError("invalid authority checkpoint hash")
    if (
        not isinstance(doc["created_at_utc"], str) or
        not doc["created_at_utc"].endswith("Z")
    ):
        raise IntegrityError("authority checkpoint UTC timestamp required")

    if journal is not None:
        if not isinstance(journal, SQLiteOperationalJournal):
            raise IntegrityError("verified Cloud journal required")
        if journal.checkpoint_head(
            doc["storage_event_count"]
        ) != doc["storage_head_sha256"]:
            raise IntegrityError("authority checkpoint storage prefix mismatch")

    if replay_store is not None:
        if not isinstance(replay_store, SQLiteNonceReplayStore):
            raise IntegrityError("verified Tower replay store required")
        try:
            replay_head = replay_store.checkpoint_head(doc["replay_event_count"])
        except Exception as exc:
            raise IntegrityError(
                "authority checkpoint replay prefix unavailable"
            ) from exc
        if replay_head != doc["replay_head_sha256"]:
            raise IntegrityError("authority checkpoint replay prefix mismatch")
    return dict(doc)


def seal_source_authority_checkpoint(
    *, journal: SQLiteOperationalJournal,
    replay_store: SQLiteNonceReplayStore,
    key_id: str,
    external_signer: Callable[[bytes], bytes],
    pinned_public_keys: Mapping[str, bytes],
    previous: SignedAuthorityCheckpoint | None = None,
    mode: str = "disabled",
) -> SignedAuthorityCheckpoint:
    if mode != "source_test":
        raise CloudError("live authority checkpoint signing disabled")
    if (
        not isinstance(journal, SQLiteOperationalJournal) or
        not isinstance(replay_store, SQLiteNonceReplayStore)
    ):
        raise CloudError("verified storage and replay ledgers required")
    if (
        not isinstance(key_id, str) or not _ID.fullmatch(key_id) or
        not callable(external_signer)
    ):
        raise CloudError("approved external authority signer callback required")

    storage = journal.verify_chain()
    replay = replay_store.verify_chain()
    previous_digest = _ZERO
    if previous is not None:
        prior = verify_authority_checkpoint(
            previous,
            pinned_public_keys=pinned_public_keys,
            journal=journal,
            replay_store=replay_store,
        )
        if (
            storage["event_count"] < prior["storage_event_count"] or
            replay["event_count"] < prior["replay_event_count"] or
            (
                storage["event_count"] == prior["storage_event_count"] and
                replay["event_count"] == prior["replay_event_count"]
            )
        ):
            raise CloudError(
                "new authority checkpoint requires monotonic ledger progress"
            )
        previous_digest = previous.sha256

    payload = json.dumps({
        "schema": _SCHEMA,
        "checkpoint_ref": "authority-checkpoints/" + secrets.token_hex(24),
        "key_id": key_id,
        "storage_event_count": storage["event_count"],
        "storage_head_sha256": storage["head_sha256"],
        "replay_event_count": replay["event_count"],
        "replay_head_sha256": replay["head_sha256"],
        "previous_checkpoint_sha256": previous_digest,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()

    sealed = SignedAuthorityCheckpoint(payload, external_signer(payload))
    verify_authority_checkpoint(
        sealed,
        pinned_public_keys=pinned_public_keys,
        journal=journal,
        replay_store=replay_store,
    )
    return sealed


def deliver_source_authority_checkpoint(
    *, signed: SignedAuthorityCheckpoint,
    sink: AuthorityCheckpointSink,
    pinned_public_keys: Mapping[str, bytes],
    journal: SQLiteOperationalJournal,
    replay_store: SQLiteNonceReplayStore,
    mode: str = "disabled",
) -> str:
    if mode != "source_test":
        raise CloudError("live authority checkpoint delivery disabled")
    if sink is None or not all(
        callable(getattr(sink, method, None))
        for method in ("put_if_absent", "get")
    ):
        raise CloudError("authority checkpoint sink with verified read-back required")

    doc = verify_authority_checkpoint(
        signed,
        pinned_public_keys=pinned_public_keys,
        journal=journal,
        replay_store=replay_store,
    )
    sink.put_if_absent(doc["checkpoint_ref"], signed)
    try:
        returned = sink.get(doc["checkpoint_ref"])
    except Exception as exc:
        raise IntegrityError(
            "authority checkpoint read-back unavailable; reconcile independently"
        ) from exc
    if (
        not isinstance(returned, SignedAuthorityCheckpoint) or
        not isinstance(returned.payload, bytes) or
        not isinstance(returned.signature, bytes) or
        not hmac.compare_digest(returned.payload, signed.payload) or
        not hmac.compare_digest(returned.signature, signed.signature)
    ):
        raise IntegrityError(
            "externally stored authority checkpoint differs from signed original"
        )
    verify_authority_checkpoint(
        returned,
        pinned_public_keys=pinned_public_keys,
        journal=journal,
        replay_store=replay_store,
    )
    return doc["checkpoint_ref"]


def verify_source_authority_checkpoint_sequence(
    *, checkpoints: list[SignedAuthorityCheckpoint] |
                     tuple[SignedAuthorityCheckpoint, ...],
    pinned_public_keys: Mapping[str, bytes],
    journal: SQLiteOperationalJournal,
    replay_store: SQLiteNonceReplayStore,
    mode: str = "disabled",
) -> dict:
    if mode != "source_test":
        raise CloudError("authority checkpoint lineage runtime disabled")
    if not isinstance(checkpoints, (list, tuple)) or not 1 <= len(checkpoints) <= 256:
        raise CloudError("bounded authority checkpoint history required")

    previous = None
    prior_storage = -1
    prior_replay = -1
    refs = set()
    tip = None
    for signed in checkpoints:
        doc = verify_authority_checkpoint(
            signed,
            pinned_public_keys=pinned_public_keys,
            journal=journal,
            replay_store=replay_store,
        )
        expected_link = _ZERO if previous is None else previous.sha256
        if doc["previous_checkpoint_sha256"] != expected_link:
            raise IntegrityError("authority checkpoint lineage gap or fork")
        if doc["checkpoint_ref"] in refs:
            raise IntegrityError("duplicate authority checkpoint reference")
        if previous is not None and (
            doc["storage_event_count"] < prior_storage or
            doc["replay_event_count"] < prior_replay or
            (
                doc["storage_event_count"] == prior_storage and
                doc["replay_event_count"] == prior_replay
            )
        ):
            raise IntegrityError("nonmonotonic authority checkpoint")
        refs.add(doc["checkpoint_ref"])
        prior_storage = doc["storage_event_count"]
        prior_replay = doc["replay_event_count"]
        previous, tip = signed, doc

    return {
        "status": "SOURCE_ONLY_AUTHORITY_LINEAGE_CHECKED",
        "checkpoint_count": len(checkpoints),
        "latest_checkpoint_ref": tip["checkpoint_ref"],
        "latest_storage_event_count": tip["storage_event_count"],
        "latest_replay_event_count": tip["replay_event_count"],
        "storage_prefix_matches": True,
        "replay_prefix_matches": True,
        "actual_external_latest_attested": False,
        "independent_offsite_immutability_certified": False,
        "production_authorized": False,
    }
