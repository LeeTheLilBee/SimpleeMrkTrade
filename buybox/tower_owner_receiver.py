"""BBX011-015: strict Tower-signed BuyBox owner handoff receiver primitives.

This module DOES NOT register an HTTP route, start a session, accept client
assertions as identity, issue Tower tokens, or activate hosted BuyBox. Only a
future Tower issuer with a distinct shared secret may mint the v1 envelope.
Consumption uses a durable unique constraint: an in-process set is insufficient.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import sqlite3
import time
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

SCHEMA_VERSION = "tower.buybox.owner.handoff.v1"
ISSUER = "tower"
AUDIENCE = "buybox-owner"
PURPOSE = "owner_entry"
PREFIX = "tbh1"
MAX_TOKEN_BYTES = 4096
MAX_LIFETIME_SECONDS = 60
CLOCK_SKEW_SECONDS = 5
HANDOFF_KEYS = frozenset({
    "schema_version", "issuer", "audience", "purpose",
    "handoff_id", "tower_session_ref", "actor_ref", "entity_ref",
    "owner_entitlement_ref", "issued_at_epoch", "expires_at_epoch",
    "target_path", "return_path",
})
TOKEN_RE = re.compile(r"^tbh1\.([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)$")
OPAQUE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{23,127}$")


class TowerBuyBoxHandoffError(ValueError):
    """Generic caller-safe failure. Do not include token or secret in messages."""


@dataclass(frozen=True)
class VerifiedOwnerHandoff:
    claims: Mapping[str, Any]


def _secret(secret: Any) -> bytes:
    if isinstance(secret, str):
        secret = secret.encode("utf-8")
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise TowerBuyBoxHandoffError("HANDOFF_SIGNING_SECRET_NOT_CONFIGURED")
    return secret


def _decode_url(value: str) -> bytes:
    try:
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        if base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=") != value:
            raise ValueError("noncanonical_base64")
        return raw
    except (ValueError, base64.binascii.Error) as exc:
        raise TowerBuyBoxHandoffError("INVALID_HANDOFF_TOKEN") from exc


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise TowerBuyBoxHandoffError("INVALID_HANDOFF_TOKEN")
        obj[key] = value
    return obj


def verify_tower_buybox_owner_handoff(
    token: str, *, shared_secret: str | bytes, now_epoch: int
) -> VerifiedOwnerHandoff:
    """Verify exact protocol, HMAC, issuer, audience, TTL, and all claim types.

    Signature verification happens before JSON parsing. Consuming this object
    is a separate atomic database operation, not an in-memory cache.
    """
    if not isinstance(token, str) or len(token) > MAX_TOKEN_BYTES:
        raise TowerBuyBoxHandoffError("INVALID_HANDOFF_TOKEN")
    match = TOKEN_RE.fullmatch(token)
    if match is None:
        raise TowerBuyBoxHandoffError("INVALID_HANDOFF_TOKEN")
    payload_b64, mac_b64 = match.groups()
    signing_input = (PREFIX + "." + payload_b64).encode("ascii")
    expected = hmac.new(_secret(shared_secret), signing_input, hashlib.sha256).digest()
    actual = _decode_url(mac_b64)
    if not hmac.compare_digest(actual, expected):
        raise TowerBuyBoxHandoffError("INVALID_HANDOFF_TOKEN")
    try:
        claims = json.loads(
            _decode_url(payload_b64).decode("utf-8"), object_pairs_hook=_unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")),
        )
    except (UnicodeDecodeError, ValueError) as exc:
        raise TowerBuyBoxHandoffError("INVALID_HANDOFF_TOKEN") from exc
    if not isinstance(claims, dict) or set(claims) != HANDOFF_KEYS:
        raise TowerBuyBoxHandoffError("INVALID_HANDOFF_CLAIMS")
    if (
        claims["schema_version"] != SCHEMA_VERSION
        or claims["issuer"] != ISSUER
        or claims["audience"] != AUDIENCE
        or claims["purpose"] != PURPOSE
        or claims["target_path"] != "/"
        or claims["return_path"] != "/tower/access-home"
    ):
        raise TowerBuyBoxHandoffError("INVALID_HANDOFF_CLAIMS")
    for key in (
        "handoff_id", "tower_session_ref", "actor_ref", "entity_ref",
        "owner_entitlement_ref",
    ):
        if not isinstance(claims[key], str) or OPAQUE_RE.fullmatch(claims[key]) is None:
            raise TowerBuyBoxHandoffError("INVALID_HANDOFF_CLAIMS")
    issued, expires = claims["issued_at_epoch"], claims["expires_at_epoch"]
    if type(issued) is not int or type(expires) is not int or type(now_epoch) is not int:
        raise TowerBuyBoxHandoffError("INVALID_HANDOFF_TIME")
    if (
        issued > now_epoch + CLOCK_SKEW_SECONDS
        or expires <= now_epoch
        or expires <= issued
        or expires - issued > MAX_LIFETIME_SECONDS
    ):
        raise TowerBuyBoxHandoffError("INVALID_HANDOFF_TIME")
    return VerifiedOwnerHandoff(claims=MappingProxyType(claims))


def consume_verified_handoff(db: sqlite3.Connection, verified: VerifiedOwnerHandoff) -> bool:
    """One successful INSERT per signed handoff ID across shared SQLite workers.

    The file must reside on an independently certified persistent single-writer
    volume. A failed insert never creates an authenticated browser session.
    Caller must commit this transaction before session issuance.
    """
    if not isinstance(verified, VerifiedOwnerHandoff):
        raise TowerBuyBoxHandoffError("VERIFIED_HANDOFF_REQUIRED")
    handoff_id = verified.claims["handoff_id"]
    digest = hashlib.sha256(handoff_id.encode("utf-8")).hexdigest()
    with db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS buybox_tower_consumed_handoffs "
            "(handoff_digest TEXT PRIMARY KEY, consumed_at_epoch INTEGER NOT NULL, "
            "expires_at_epoch INTEGER NOT NULL)"
        )
        try:
            db.execute(
                "INSERT INTO buybox_tower_consumed_handoffs VALUES (?,?,?)",
                (digest, int(time.time()), verified.claims["expires_at_epoch"]),
            )
        except sqlite3.IntegrityError:
            return False
    return True
