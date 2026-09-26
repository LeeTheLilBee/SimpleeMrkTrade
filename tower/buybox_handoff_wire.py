"""TWR207-211: exact Tower-side wire format for the sealed BuyBox receiver.

This is a source-level crypto/interop contract, not a live token issuer.
No HTTP route, app entitlement, session creation, Render secret read,
release permission, or BuyBox deployment is added by this module.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
from typing import Any, Mapping

from tower.buybox_owner_preflight import inspect_current_buybox_owner_preflight

SCHEMA_VERSION = "tower.buybox.owner.handoff.v1"
ISSUER = "tower"
AUDIENCE = "buybox-owner"
PURPOSE = "owner_entry"
PREFIX = "tbh1"
MAX_LIFETIME_SECONDS = 60
CLAIM_KEYS = frozenset({
    "schema_version", "issuer", "audience", "purpose",
    "handoff_id", "tower_session_ref", "actor_ref", "entity_ref",
    "owner_entitlement_ref", "issued_at_epoch", "expires_at_epoch",
    "target_path", "return_path",
})
OPAQUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{23,127}$")


class TowerBuyBoxWireError(ValueError):
    """Do not disclose claims or secret in exceptions."""


def _encode_verified_source_contract(
    claims: Mapping[str, Any], *, shared_secret: str | bytes, now_epoch: int
) -> str:
    """Private serializer; callers MUST independently prove server-derived claims.

    This method only verifies wire shape. It cannot prove an owner, entitlement,
    current Tower step-up or real BuyBox receiver. Only the future source-bound
    and separately reviewed issuer may call it in a product route.
    """
    if not isinstance(claims, Mapping) or set(claims) != CLAIM_KEYS:
        raise TowerBuyBoxWireError("HANDOFF_WIRE_FIELDS_INVALID")
    if (
        claims["schema_version"] != SCHEMA_VERSION
        or claims["issuer"] != ISSUER
        or claims["audience"] != AUDIENCE
        or claims["purpose"] != PURPOSE
        or claims["target_path"] != "/"
        or claims["return_path"] != "/tower/access-home"
    ):
        raise TowerBuyBoxWireError("HANDOFF_WIRE_CLAIMS_INVALID")
    for key in (
        "handoff_id", "tower_session_ref", "actor_ref", "entity_ref",
        "owner_entitlement_ref",
    ):
        if not isinstance(claims[key], str) or OPAQUE.fullmatch(claims[key]) is None:
            raise TowerBuyBoxWireError("HANDOFF_WIRE_CLAIMS_INVALID")
    issued, expires = claims["issued_at_epoch"], claims["expires_at_epoch"]
    if any(type(x) is not int for x in (issued, expires, now_epoch)):
        raise TowerBuyBoxWireError("HANDOFF_WIRE_TIME_INVALID")
    if issued > now_epoch + 5 or expires <= now_epoch or not (
        0 < expires - issued <= MAX_LIFETIME_SECONDS
    ):
        raise TowerBuyBoxWireError("HANDOFF_WIRE_TIME_INVALID")
    if isinstance(shared_secret, str):
        shared_secret = shared_secret.encode("utf-8")
    if not isinstance(shared_secret, bytes) or len(shared_secret) < 32:
        raise TowerBuyBoxWireError("HANDOFF_WIRE_SECRET_UNAVAILABLE")

    payload = json.dumps(
        dict(claims), sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")
    segment = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    signing_input = PREFIX + "." + segment
    digest = hmac.new(
        shared_secret, signing_input.encode("ascii"), hashlib.sha256
    ).digest()
    mac = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return signing_input + "." + mac


def issue_current_owner_buybox_handoff() -> None:
    """Fail closed. A source interop test is never permission to issue tokens."""
    inspect_current_buybox_owner_preflight()
    raise TowerBuyBoxWireError("BUYBOX_HOSTED_RECEIVER_NOT_CONNECTED")
