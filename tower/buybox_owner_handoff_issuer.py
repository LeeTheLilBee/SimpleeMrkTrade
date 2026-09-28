"""Tower-side BuyBox owner handoff issuer / TWR-BBX crossing source.

This is the producer half of BuyBox's exact tower.buybox.owner.handoff.v1.
It never turns registry presence into access. A current owner session, active
step-up, verified hosted identity, explicit BuyBox entitlement, and launchable
publication truth are all required before a token can be issued.

No HTTP launch route is registered here. The receiver host/storage/publication
must be certified separately before Tower exposes a doorway.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from collections.abc import Mapping
from typing import Any

from tower.app_truth_projection import app_truth_by_id
from tower.identity_authority import hosted_owner_identity_authority

SCHEMA_VERSION = "tower.buybox.owner.handoff.v1"
ISSUER = "tower"
AUDIENCE = "buybox-owner"
PURPOSE = "owner_entry"
PREFIX = "tbh1"
MAX_LIFETIME_SECONDS = 60
SIGNING_SECRET_ENV = "TOWER_BUYBOX_HANDOFF_SIGNING_SECRET"
OPAQUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{23,127}$")

HANDOFF_KEYS = frozenset({
    "schema_version", "issuer", "audience", "purpose",
    "handoff_id", "tower_session_ref", "actor_ref", "entity_ref",
    "owner_entitlement_ref", "issued_at_epoch", "expires_at_epoch",
    "target_path", "return_path",
})


class TowerBuyBoxIssuerUnavailable(RuntimeError):
    pass


def _secret(value: str | bytes | None = None) -> bytes:
    raw = value if value is not None else os.getenv(SIGNING_SECRET_ENV, "")
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if not isinstance(raw, bytes) or len(raw) < 32:
        raise TowerBuyBoxIssuerUnavailable(
            "BuyBox handoff signing secret is not configured"
        )
    return raw


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _opaque(value: Any, field: str) -> str:
    if not isinstance(value, str) or OPAQUE.fullmatch(value) is None:
        raise TowerBuyBoxIssuerUnavailable(field + " is not a valid opaque reference")
    return value


def owner_buybox_entitlement(identity: Mapping[str, Any]) -> dict[str, Any] | None:
    rows = identity.get("app_entitlements")
    if not isinstance(rows, list):
        return None
    for row in rows:
        if (
            isinstance(row, Mapping)
            and row.get("app_id") == "buybox"
            and row.get("verification_state") == "VERIFIED"
            and row.get("access_policy") == "GRANTED"
        ):
            return dict(row)
    return None


def inspect_current_buybox_issue_preflight(
    *,
    session_context: Mapping[str, Any],
    identity: Mapping[str, Any] | None = None,
    app_truth: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Read-only current crossing truth; never mints a token."""
    reasons: list[str] = []
    if not isinstance(session_context, Mapping):
        session_context = {}
    if session_context.get("authenticated") is not True:
        reasons.append("CURRENT_TOWER_OWNER_SESSION_REQUIRED")
    if session_context.get("role") != "owner":
        reasons.append("CURRENT_TOWER_OWNER_ROLE_REQUIRED")
    if not session_context.get("owner_id"):
        reasons.append("CURRENT_TOWER_OWNER_ID_REQUIRED")
    if not session_context.get("tower_session_ref"):
        reasons.append("CURRENT_TOWER_SESSION_BINDING_REQUIRED")
    if session_context.get("step_up_active") is not True:
        reasons.append("CURRENT_TOWER_OWNER_STEP_UP_REQUIRED")

    current_identity = (
        hosted_owner_identity_authority() if identity is None else identity
    )
    if current_identity.get("verification_state") != "VERIFIED":
        reasons.append("HOSTED_OWNER_IDENTITY_NOT_VERIFIED")
        entitlement = None
    else:
        entitlement = owner_buybox_entitlement(current_identity)
        if entitlement is None:
            reasons.append("BUYBOX_OWNER_ENTITLEMENT_NOT_GRANTED")

    truth = app_truth_by_id("buybox") if app_truth is None else app_truth
    if not isinstance(truth, Mapping) or truth.get("launchable") is not True:
        reasons.append("BUYBOX_PUBLICATION_HEALTH_OR_LAUNCH_NOT_VERIFIED")

    try:
        _secret()
        signing_ready = True
    except TowerBuyBoxIssuerUnavailable:
        signing_ready = False
        reasons.append("BUYBOX_HANDOFF_SIGNING_SECRET_NOT_CONFIGURED")

    return {
        "schema_version": "tower.buybox.owner.issue-preflight.v1",
        "app_id": "buybox",
        "state": "READY_TO_ISSUE" if not reasons else "BLOCKED",
        "reason_codes": reasons,
        "can_issue_handoff": not reasons,
        "signing_ready": signing_ready,
        "entitlement": entitlement,
        "sensitive_secret_exposed": False,
        "launch_route_opened": False,
    }


def issue_buybox_owner_handoff(
    *,
    session_context: Mapping[str, Any],
    identity: Mapping[str, Any] | None = None,
    app_truth: Mapping[str, Any] | None = None,
    now_epoch: int | None = None,
    shared_secret: str | bytes | None = None,
) -> dict[str, Any]:
    """Issue the exact short-lived BuyBox owner token after all current gates."""
    now = int(time.time()) if now_epoch is None else now_epoch
    if type(now) is not int:
        raise TowerBuyBoxIssuerUnavailable("invalid issuance time")

    current_identity = (
        hosted_owner_identity_authority() if identity is None else identity
    )
    current_truth = app_truth_by_id("buybox") if app_truth is None else app_truth
    preflight = inspect_current_buybox_issue_preflight(
        session_context=session_context,
        identity=current_identity,
        app_truth=current_truth,
    )
    # Tests may inject a distinct secret rather than mutating process env.
    if shared_secret is not None:
        reasons = [
            r for r in preflight["reason_codes"]
            if r != "BUYBOX_HANDOFF_SIGNING_SECRET_NOT_CONFIGURED"
        ]
        preflight = {**preflight, "reason_codes": reasons, "can_issue_handoff": not reasons}
    if preflight["can_issue_handoff"] is not True:
        raise TowerBuyBoxIssuerUnavailable(
            "BuyBox owner handoff preflight is blocked"
        )

    record = current_identity.get("record")
    entitlement = owner_buybox_entitlement(current_identity)
    if not isinstance(record, Mapping) or entitlement is None:
        raise TowerBuyBoxIssuerUnavailable("BuyBox owner identity unavailable")

    tower_session_ref = _opaque(
        str(session_context.get("tower_session_ref", "")),
        "tower_session_ref",
    )
    actor_ref = _opaque(str(record.get("person_id", "")), "actor_ref")

    organization = record.get("organization")
    entity_candidate = (
        organization.get("organization_id")
        if isinstance(organization, Mapping)
        else None
    )
    # If the owner has no configured organization, bind to the verified
    # account reference rather than inventing a company/entity.
    entity_ref = _opaque(
        str(entity_candidate or record.get("account_id", "")),
        "entity_ref",
    )
    entitlement_ref = _opaque(
        "tower_entitlement_buybox_" + hashlib.sha256(
            (
                actor_ref + "\x1f" + entity_ref + "\x1f"
                + str(entitlement.get("source_id", ""))
            ).encode("utf-8")
        ).hexdigest()[:32],
        "owner_entitlement_ref",
    )

    claims = {
        "schema_version": SCHEMA_VERSION,
        "issuer": ISSUER,
        "audience": AUDIENCE,
        "purpose": PURPOSE,
        "handoff_id": "tower_buybox_" + secrets.token_hex(16),
        "tower_session_ref": tower_session_ref,
        "actor_ref": actor_ref,
        "entity_ref": entity_ref,
        "owner_entitlement_ref": entitlement_ref,
        "issued_at_epoch": now,
        "expires_at_epoch": now + MAX_LIFETIME_SECONDS,
        "target_path": "/",
        "return_path": "/tower/access-home",
    }
    if set(claims) != HANDOFF_KEYS:
        raise TowerBuyBoxIssuerUnavailable("BuyBox handoff claims invalid")

    payload = json.dumps(
        claims, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    payload_b64 = _b64(payload)
    signing_input = (PREFIX + "." + payload_b64).encode("ascii")
    signature = hmac.new(
        _secret(shared_secret), signing_input, hashlib.sha256
    ).digest()
    token = PREFIX + "." + payload_b64 + "." + _b64(signature)
    return {
        "schema_version": SCHEMA_VERSION,
        "token": token,
        "claims": claims,
        "expires_at_epoch": claims["expires_at_epoch"],
        "single_use_required_by_receiver": True,
        "return_path": "/tower/access-home",
        "broker_submission_authorized": False,
        "capital_movement_authorized": False,
        "closing_authorized": False,
        "vault_access_authorized": False,
        "secret_exposed": False,
    }
