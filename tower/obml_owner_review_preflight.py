"""TWR-OBML006–010: source-only owner Manual Live L1 *review* preflight.

The existing Tower→Observatory owner launch and receipt remain authoritative.
This module does not issue a new session, token, account entitlement, step-up
event, broker attestation, Manual Live activation, order or capital permission.
Existing generic Tower step-up is NOT an OBML-purpose-bound step-up.
"""
from __future__ import annotations

from tower.app_truth_projection import app_truth_by_id
from tower.identity_authority import hosted_owner_identity_authority
from tower.tower_human_login_ob_launch import (
    operational_ob_access_active,
    owner_session_active,
    step_up_active,
)

SCHEMA_VERSION = "tower.obml.owner.review.preflight.v1"
PURPOSE = "OBML_OWNER_REVIEW"
CANONICAL_OB_ENTRY = "/tower/launch/observatory"
PROTECTED_DESTINATION = "/ob/dashboard"

# These capabilities are not inferred from a normal Tower owner launch.
FORBIDDEN_CAPABILITIES = (
    "trade_intent_creation", "order_authorized", "broker_order_api",
    "automatic_execution", "hybrid_execution", "capital_movement",
    "protected_floor_release", "safety_clearance_override",
)


def inspect_current_obml_owner_review() -> dict[str, object]:
    """Evaluate current authoritative Tower facts; always block OBML clearance.

    Product-specific account identity, fresh purpose-bound step-up, revocation
    ledger and OB effective policy evidence do not currently have a certified
    issuer/receiver path here. Never accept a caller-provided 'verified' flag.
    """
    reasons: list[str] = []
    owner = owner_session_active()
    if not owner:
        reasons.append("NO_CURRENT_TOWER_OWNER_SESSION")
    step_up = owner and step_up_active()
    if owner and not step_up:
        reasons.append("FRESH_TOWER_STEP_UP_REQUIRED")
    if not (owner and step_up and operational_ob_access_active()):
        reasons.append("CURRENT_OPERATIONAL_OB_ACCESS_RECEIPT_REQUIRED")

    identity = hosted_owner_identity_authority()
    if identity.get("verification_state") != "VERIFIED":
        reasons.append("HOSTED_OWNER_IDENTITY_NOT_VERIFIED")
    else:
        entitlements = identity.get("app_entitlements")
        if not isinstance(entitlements, list) or not any(
            isinstance(item, dict)
            and item.get("app_id") == "observatory"
            and item.get("verification_state") == "VERIFIED"
            and item.get("access_policy") == "GRANTED"
            for item in entitlements
        ):
            reasons.append("CURRENT_OWNER_OB_ENTITLEMENT_UNVERIFIED")
    truth = app_truth_by_id("observatory")
    if not truth or truth.get("launchable") is not True:
        reasons.append("CANONICAL_OB_PUBLICATION_OR_HEALTH_UNVERIFIED")

    # Do not confuse the existing generic Tower step-up or operational OB
    # receipt with a fresh, account-specific Manual Live review grant.
    reasons.extend((
        "OBML_PURPOSE_BOUND_STEP_UP_UNIMPLEMENTED",
        "CANONICAL_OB_ACCOUNT_IDENTITY_UNVERIFIED",
        "CURRENT_REVOCATION_AND_REPLAY_PROOF_UNIMPLEMENTED",
        "OB_EFFECTIVE_POLICY_SAFETY_SOURCE_RECHECK_UNVERIFIED",
        "BROKER_PROVENANCE_AND_HUMAN_REVIEW_RECEIPT_NOT_VERIFIED",
        "OBML_TOWER_ISSUER_AND_OB_RECEIVER_NOT_CONNECTED",
    ))
    return {
        "schema_version": SCHEMA_VERSION,
        "app_id": "observatory",
        "purpose": PURPOSE,
        "existing_launch_entry": CANONICAL_OB_ENTRY,
        "protected_destination": PROTECTED_DESTINATION,
        "state": "BLOCKED",
        "reason_codes": reasons,
        "source_status": "SOURCE_ONLY_UNIMPLEMENTED_NO_LIVE_GRANT",
        "review_clearance_issued": False,
        "owner_account_verified_for_obml": False,
        "ob_effective_policy_verified": False,
        "broker_authentication_verified": False,
        "manual_live_activated": False,
        "execution_authorized": False,
        "amount_data_returned": False,
        "issued_token": False,
        "forbidden_capabilities": {name: False for name in FORBIDDEN_CAPABILITIES},
    }
