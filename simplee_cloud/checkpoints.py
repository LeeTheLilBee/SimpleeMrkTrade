"""SC005 source-only externally signed operational journal checkpoint contract.

This module NEVER owns a signing private key or an external checkpoint store.
Its injected signer and sink are test fakes until independently deployed and
approved. A local hash chain without independently held signed anchor is NOT WORM.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Mapping, Protocol

from .contracts import CloudError, IntegrityError, valid_sha256
from .journal import SQLiteOperationalJournal

_SCHEMA = "simplee.cloud.operational-checkpoint.v1"
_FIELDS = frozenset({
    "schema", "checkpoint_ref", "key_id", "event_count", "head_sha256",
    "previous_checkpoint_sha256", "created_at_utc",
})
_ID = re.compile(r"[A-Za-z0-9_.:-]{1,64}\Z")
_REF = re.compile(r"checkpoints/[0-9a-f]{48}\Z")
_ZERO = "0" * 64


@dataclass(frozen=True)
class SignedCheckpoint:
    payload: bytes
    signature: bytes

    @property
    def sha256(self):
        return hashlib.sha256(self.payload + b"." + self.signature).hexdigest()


class CheckpointSink(Protocol):
    """External write-once independently operated storage; NOT implemented here."""
    def put_if_absent(self, reference: str, checkpoint: SignedCheckpoint) -> None: ...
    def get(self, reference: str) -> SignedCheckpoint: ...


def _strict_pairs(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise IntegrityError("duplicate checkpoint property")
        result[k] = v
    return result


def _claims(payload: bytes) -> dict:
    if not isinstance(payload, bytes) or not 1 <= len(payload) <= 2048:
        raise IntegrityError("invalid checkpoint payload")
    try:
        claims = json.loads(payload.decode("utf-8"), object_pairs_hook=_strict_pairs)
        if not isinstance(claims, dict) or set(claims) != _FIELDS:
            raise IntegrityError("unexpected checkpoint claims")
        if json.dumps(
            claims, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode() != payload:
            raise IntegrityError("checkpoint encoding not canonical")
        return claims
    except (UnicodeError, TypeError, ValueError) as exc:
        raise IntegrityError("malformed checkpoint") from exc


def verify_checkpoint(
    signed: SignedCheckpoint, *,
    pinned_public_keys: Mapping[str, bytes],
    journal: SQLiteOperationalJournal | None = None,
) -> dict:
    if not isinstance(signed, SignedCheckpoint):
        raise IntegrityError("signed checkpoint required")
    doc = _claims(signed.payload)
    if doc["schema"] != _SCHEMA or not isinstance(doc["checkpoint_ref"], str) or not (
        _REF.fullmatch(doc["checkpoint_ref"])
    ):
        raise IntegrityError("wrong checkpoint schema/reference")
    key_id = doc["key_id"]
    if not isinstance(key_id, str) or not _ID.fullmatch(key_id):
        raise IntegrityError("invalid checkpoint key identity")
    if not isinstance(pinned_public_keys, Mapping):
        raise IntegrityError("independent public-key trust roots required")
    public = pinned_public_keys.get(key_id)
    if not isinstance(public, bytes) or len(public) != 32 or not isinstance(
        signed.signature, bytes
    ) or len(signed.signature) != 64:
        raise IntegrityError("unknown signer or malformed signature")
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        Ed25519PublicKey.from_public_bytes(public).verify(signed.signature, signed.payload)
    except (ValueError, InvalidSignature) as exc:
        raise IntegrityError("external checkpoint signature mismatch") from exc
    if type(doc["event_count"]) is not int or doc["event_count"] < 0 or not (
        valid_sha256(doc["head_sha256"]) and valid_sha256(doc["previous_checkpoint_sha256"])
    ):
        raise IntegrityError("invalid checkpoint sequence/hash")
    if not isinstance(doc["created_at_utc"], str) or not doc["created_at_utc"].endswith("Z"):
        raise IntegrityError("checkpoint UTC timestamp required")
    if journal is not None:
        # Verifies entire journal first, then checks this checkpoint's exact prefix.
        if journal.checkpoint_head(doc["event_count"]) != doc["head_sha256"]:
            raise IntegrityError("signed checkpoint does not match local journal history")
    return dict(doc)


def seal_source_checkpoint(
    *, journal: SQLiteOperationalJournal,
    key_id: str,
    external_signer: Callable[[bytes], bytes],
    pinned_public_keys: Mapping[str, bytes],
    previous: SignedCheckpoint | None = None,
    mode: str = "disabled",
) -> SignedCheckpoint:
    if mode != "source_test":
        raise CloudError("live checkpoint signing and delivery disabled")
    if not isinstance(key_id, str) or not _ID.fullmatch(key_id) or not callable(external_signer):
        raise CloudError("approved external signer identity/callback required")
    head = journal.verify_chain()
    prev_digest = _ZERO
    if previous is not None:
        before = verify_checkpoint(previous, pinned_public_keys=pinned_public_keys, journal=journal)
        if head["event_count"] <= before["event_count"]:
            raise CloudError("new checkpoint requires additional verified events")
        prev_digest = previous.sha256
    payload = json.dumps({
        "schema": _SCHEMA,
        "checkpoint_ref": "checkpoints/" + secrets.token_hex(24),
        "key_id": key_id,
        "event_count": head["event_count"],
        "head_sha256": head["head_sha256"],
        "previous_checkpoint_sha256": prev_digest,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    signature = external_signer(payload)
    sealed = SignedCheckpoint(payload, signature)
    verify_checkpoint(sealed, pinned_public_keys=pinned_public_keys, journal=journal)
    return sealed


def deliver_source_checkpoint(
    *, signed: SignedCheckpoint, sink: CheckpointSink,
    pinned_public_keys: Mapping[str, bytes],
    journal: SQLiteOperationalJournal, mode: str = "disabled",
) -> str:
    if mode != "source_test":
        raise CloudError("external checkpoint delivery not authorized")
    if sink is None or not callable(getattr(sink, "put_if_absent", None)):
        raise CloudError("separate immutable checkpoint sink required")
    doc = verify_checkpoint(signed, pinned_public_keys=pinned_public_keys, journal=journal)
    sink.put_if_absent(doc["checkpoint_ref"], signed)
    # This means only that an injected sink returned, not that its independent
    # administration, jurisdiction, immutability or offsite placement is proven.
    return doc["checkpoint_ref"]
