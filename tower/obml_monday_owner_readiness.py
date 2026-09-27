"""OBML026–030: owner-visible Monday readiness desk, NOT a Manual Live issuer.

All evidence below is current Tower preflight truth or published source-contract
requirements. A successful GET does not grant review access or a brokerage order.
No browser supplied checkboxes, claims or GET arguments can close a gate.
"""
from __future__ import annotations

from flask import Flask, jsonify, make_response

from tower.obml_owner_review_preflight import inspect_current_obml_owner_review
from tower.tower_human_login_ob_launch import require_human_owner

SCHEMA_VERSION = "tower.obml.monday.owner.readiness.v1"
READINESS_PATH = "/tower/owner/manual-live-1/readiness.json"
TARGET_DATE = "2026-09-28"
ENTRY_PATH = "/tower/launch/observatory"
REVIEW_PATH = "/ob/review-center"

# These IDs mirror the independent OBML021-025 merged main contract and are
# verified by exact-source CI. This view is not a new policy authority.
PRE_ACCESS = (
    "TOWER_PURPOSE_BOUND_AUTHENTICATION",
    "TOWER_HOSTED_OWNER_CROSSING",
    "PROVIDER_ACCOUNT_AND_OPTIONS_PERMISSIONS",
    "PROVIDER_SETTLEMENT_AND_PROTECTED_FLOORS",
    "CURRENT_SOURCE_RISK_AND_MARKET",
    "PRODUCTION_OPERATING_APPROVAL",
)
BEFORE_EACH_ORDER = (
    "HUMAN_REVIEW_CENTER_DECISION",
    "PROVIDER_ACCOUNT_AND_OPTIONS_PERMISSIONS",
    "PROVIDER_SETTLEMENT_AND_PROTECTED_FLOORS",
    "CURRENT_SOURCE_RISK_AND_MARKET",
)
AFTER_HUMAN_ORDER = ("EXTERNAL_MANUAL_ORDER_RECONCILIATION",)


def owner_monday_readiness_payload() -> dict[str, object]:
    """For an already authenticated owner request; never mint a grant."""
    source = inspect_current_obml_owner_review()
    reason_codes = source.get("reason_codes", [])
    if not isinstance(reason_codes, list) or not all(
        isinstance(code, str) and code.isupper()
        and len(code) <= 100 and code.replace("_", "").isalnum()
        for code in reason_codes
    ):
        reason_codes = ["CANONICAL_TOWER_PREFLIGHT_UNAVAILABLE"]

    return {
        "schema_version": SCHEMA_VERSION,
        "target_date": TARGET_DATE,
        "app_id": "observatory",
        "scope": "OWNER_ONLY_MANUAL_LIVE_LEVEL_1",
        "status": "HOLD_EXTERNAL_PROOF",
        "source": "CURRENT_TOWER_OBML_OWNER_PREFLIGHT_PLUS_PINNED_OB_PHASE_IDS",
        "source_preflight_state": (
            "BLOCKED" if source.get("state") != "BLOCKED" else "BLOCKED"
        ),
        "tower_preflight_reason_codes": reason_codes,
        "existing_tower_entry": ENTRY_PATH,
        "existing_review_center": REVIEW_PATH,
        "before_review_access": list(PRE_ACCESS),
        "before_every_owner_broker_order": list(BEFORE_EACH_ORDER),
        "after_real_human_broker_order": list(AFTER_HUMAN_ORDER),
        "post_order_fill_is_not_required_for_first_review_access": True,
        "owner_places_order_only_in_separate_broker_interface": True,
        "owner_next_actions": [
            "VERIFY_EXISTING_TOWER_OWNER_LOGIN_AND_OB_LAUNCH_PRIVATELY",
            "VERIFY_REAL_BROKER_ACCOUNT_AND_APPROVED_INSTRUMENT_PERMISSIONS_PRIVATELY",
            "VERIFY_AVAILABLE_SETTLED_FUNDS_AND_PROTECTED_FLOORS_WITH_AUTHORITIES",
            "VERIFY_CURRENT_MARKET_POLICY_KILL_SWITCH_AND_OWNER_REVIEW",
            "COMPLETE_AUTHENTICATED_OBML_ISSUER_RECEIVER_AND_OWNER_ACCEPTANCE",
        ],
        "fallback": "SURVEY_PAPER_OR_APPROVED_SYNTHETIC_REHEARSAL_NO_REAL_ORDER",
        "brokerage_account_id_included": False,
        "bank_balance_included": False,
        "credentials_included": False,
        "issuer_receipt_included": False,
        "owner_review_access_granted": False,
        "per_order_permission_granted": False,
        "real_manual_live_activated": False,
        "broker_api_enabled": False,
        "automatic_selection_enabled": False,
        "hybrid_live_auto_enabled": False,
        "capital_movement_authorized": False,
        "protected_floor_released": False,
        "paid_resources_provisioned": False,
    }


def _readiness_view():
    response = make_response(jsonify(owner_monday_readiness_payload()), 200)
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


def register_obml_monday_readiness(app: Flask) -> None:
    """A read-only, authenticated status surface on the existing Tower app."""
    endpoint = "simplee_obml_monday_owner_readiness"
    if endpoint in app.view_functions:
        return
    app.add_url_rule(
        READINESS_PATH,
        endpoint=endpoint,
        view_func=require_human_owner(_readiness_view),
        methods=["GET"],
    )
