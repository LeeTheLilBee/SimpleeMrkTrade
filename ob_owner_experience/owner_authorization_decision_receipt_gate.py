from copy import deepcopy

from .owner_authorization_receipt_draft import build_owner_authorization_receipt_draft_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_owner_authorization_decision_receipt_gate_gp016",
    "display_title": "Owner Authorization Decision Receipt Gate",
    "decision": "READY_FOR_OWNER_AUTHORIZATION_DECISION_RECEIPT_GATE_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "receipt_gate_open",
    "receipt_emission_enabled",
    "decision_receipt_emitted",
    "owner_authorization_granted",
    "authorization_decision_recorded",
    "controlled_run_gate_open",
    "controlled_run_authorized",
    "controlled_run_started",
    "owner_walkthrough_started",
    "owner_walkthrough_accepted",
    "live_route_opened",
    "tower_return_repaired",
    "render_redeployed",
    "production_deploy_enabled",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
    "staging_ready",
]

TRUE_FLAGS = [
    "gp015_receipt_draft_prepared",
    "receipt_gate_prepared",
    "receipt_gate_closed",
    "append_only_required",
    "redaction_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "receipt gate opening",
    "receipt emission",
    "owner authorization granted",
    "authorization decision recorded",
    "controlled run authorization",
    "controlled run start",
    "owner walkthrough acceptance",
    "Tower return/session continuity repair",
    "Render redeploy",
    "production deployment",
    "broker submission",
    "real capital movement",
    "direct execution",
    "automated execution",
    "permission mutation",
    "secret reveal",
    "Live Auto unlock",
]


def build_owner_authorization_decision_receipt_schema():
    gp015 = build_owner_authorization_receipt_draft_bundle()
    return {
        "receipt_type": "owner_authorization_decision_receipt",
        "source_dependency": "GP015",
        "draft_source_package": gp015["package"],
        "append_only": True,
        "redaction_required": True,
        "secret_values_forbidden": True,
        "broker_payload_forbidden": True,
        "money_movement_forbidden": True,
        "emission_allowed_now": False,
        "required_fields": [
            "receipt_id",
            "decision_id",
            "decision_value",
            "decision_hash",
            "owner_identity_reference",
            "tower_session_reference",
            "step_up_reference",
            "bounded_window_reference",
            "six_room_scope_hash",
            "safety_lock_hash",
            "created_at",
        ],
    }


def build_owner_authorization_decision_receipt_gate_status():
    gp015 = build_owner_authorization_receipt_draft_bundle()
    return {
        "gp015_receipt_draft_prepared": gp015["draft_prepared"] is True,
        "receipt_gate_prepared": True,
        "receipt_gate_closed": True,
        "append_only_required": True,
        "redaction_required": True,
        "room_scope_count": len(gp015["room_scope"]),
        "room_scope_order_ok": [item["room"] for item in gp015["room_scope"]] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "receipt_gate_open": False,
        "receipt_emission_enabled": False,
        "decision_receipt_emitted": False,
        "owner_authorization_granted": False,
        "authorization_decision_recorded": False,
        "controlled_run_gate_open": False,
        "controlled_run_authorized": False,
        "controlled_run_started": False,
        "owner_walkthrough_started": False,
        "owner_walkthrough_accepted": False,
        "live_route_opened": False,
        "tower_return_repaired": False,
        "render_redeployed": False,
        "production_deploy_enabled": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "permission_mutation_enabled": False,
        "secret_reveal_enabled": False,
        "anonymous_access_allowed": False,
        "owner_session_required": True,
        "staging_ready": False,
        "live_auto_locked": True,
    }


def build_owner_authorization_decision_receipt_gate_bundle():
    gp015 = build_owner_authorization_receipt_draft_bundle()
    schema = build_owner_authorization_decision_receipt_schema()
    status = build_owner_authorization_decision_receipt_gate_status()
    adapter = build_real_surface_adapter_contract()
    prepared = (
        status["gp015_receipt_draft_prepared"] is True
        and status["receipt_gate_prepared"] is True
        and status["receipt_gate_closed"] is True
        and status["room_scope_count"] == 6
        and status["room_scope_order_ok"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "gate_prepared": prepared,
        "source_dependency": "GP015",
        "gate_state": "closed_pending_future_authorized_receipt_emission",
        "receipt_schema": schema,
        "room_scope": deepcopy(gp015["room_scope"]),
        "status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {"live_auto_locked": True},
        "next_build": "OB Controlled Walkthrough Run Window Preparation / GP017",
    }


def build_owner_authorization_decision_receipt_gate_handoff():
    bundle = build_owner_authorization_decision_receipt_gate_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "gate_prepared": bundle["gate_prepared"],
        "source_dependency": bundle["source_dependency"],
        "gate_state": bundle["gate_state"],
        "receipt_schema": bundle["receipt_schema"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Treat this as receipt gate preparation only.",
            "Do not open the receipt gate.",
            "Do not emit a decision receipt.",
            "Do not record authorization.",
            "Do not open the controlled-run gate.",
            "Do not start or accept the walkthrough.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP017 controlled walkthrough run window preparation.",
        ],
    }
