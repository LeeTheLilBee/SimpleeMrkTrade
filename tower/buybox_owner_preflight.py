"""TWR202-206: read-only Tower-derived BuyBox owner preflight.

No route, no token, no session creation, no receiver and no approval.
Never accepts browser booleans or a client-supplied Tower context.
"""
from __future__ import annotations

from tower.app_truth_projection import app_truth_by_id
from tower.identity_authority import hosted_owner_identity_authority
from tower.tower_human_login_ob_launch import (
    owner_session_active,
    step_up_active,
)

PREFLIGHT_VERSION = "tower.buybox.owner.preflight.v1"


def inspect_current_buybox_owner_preflight() -> dict[str, object]:
    """Secret-free blocker inventory; cannot grant a BuyBox handoff."""
    reasons: list[str] = []

    if not owner_session_active():
        reasons.append("CURRENT_TOWER_OWNER_SESSION_REQUIRED")
    elif not step_up_active():
        reasons.append("CURRENT_TOWER_OWNER_STEP_UP_REQUIRED")

    identity = hosted_owner_identity_authority()
    if identity.get("verification_state") != "VERIFIED":
        reasons.append("HOSTED_OWNER_IDENTITY_NOT_VERIFIED")
    else:
        access = identity.get("app_entitlements")
        if not isinstance(access, list) or not any(
            isinstance(row, dict)
            and row.get("app_id") == "buybox"
            and row.get("verification_state") == "VERIFIED"
            and row.get("access_policy") == "GRANTED"
            for row in access
        ):
            reasons.append("BUYBOX_OWNER_ENTITLEMENT_NOT_GRANTED")

    truth = app_truth_by_id("buybox")
    if not truth or truth.get("launchable") is not True:
        reasons.append("BUYBOX_PUBLICATION_HEALTH_OR_LAUNCH_NOT_VERIFIED")

    # This is unconditional until a subsequent separately certified crossing.
    # Source registration and a passing unit test are not a real receiver.
    reasons.append("BUYBOX_HOSTED_RECEIVER_NOT_CONNECTED")

    return {
        "schema_version": PREFLIGHT_VERSION,
        "app_id": "buybox",
        "state": "BLOCKED",
        "reason_codes": reasons,
        "can_issue_handoff": False,
        "owner_authenticated_for_buybox": False,
        "application_access_granted": False,
        "receiver_connected": False,
        "teller_financial_readiness": "UNKNOWN",
        "vault_archival_active": False,
        "sensitive_data_returned": False,
    }
