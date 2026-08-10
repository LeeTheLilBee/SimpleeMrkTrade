from copy import deepcopy

from .owner_authorization_decision_receipt_gate import build_owner_authorization_decision_receipt_gate_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_controlled_walkthrough_run_window_preparation_gp017",
    "display_title": "Controlled Walkthrough Run Window Preparation",
    "decision": "READY_FOR_CONTROLLED_WALKTHROUGH_RUN_WINDOW_PREPARATION_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "window_active",
    "window_open",
    "window_started",
    "controlled_run_gate_open",
    "controlled_run_authorized",
    "controlled_run_started",
    "controlled_run_completed",
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
    "gp016_receipt_gate_prepared",
    "window_template_prepared",
    "bounded_window_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "run window opening",
    "controlled run authorization",
    "controlled run start",
    "owner walkthrough start",
    "owner walkthrough acceptance",
    "live route opening",
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


def build_controlled_walkthrough_run_window_plan():
    gp016 = build_owner_authorization_decision_receipt_gate_bundle()
    return {
        "source_dependency": "GP016",
        "window_type": "future_bounded_owner_walkthrough_window",
        "window_template_prepared": True,
        "window_active": False,
        "window_open": False,
        "window_started": False,
        "bounded_window_required": True,
        "default_duration_minutes": 45,
        "maximum_duration_minutes": 90,
        "room_order": list(SIX_ROOM_REAL_SURFACE_ORDER),
        "room_scope": deepcopy(gp016["room_scope"]),
        "required_before_open": [
            "owner authorization decision recorded in future package",
            "decision receipt emitted in future package",
            "Tower owner session active",
            "step-up complete",
            "evidence capture armed",
            "all safety locks confirmed",
        ],
    }


def build_controlled_walkthrough_run_window_status():
    gp016 = build_owner_authorization_decision_receipt_gate_bundle()
    plan = build_controlled_walkthrough_run_window_plan()
    return {
        "gp016_receipt_gate_prepared": gp016["gate_prepared"] is True,
        "window_template_prepared": True,
        "bounded_window_required": True,
        "room_scope_count": len(plan["room_scope"]),
        "room_scope_order_ok": plan["room_order"] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "window_active": False,
        "window_open": False,
        "window_started": False,
        "controlled_run_gate_open": False,
        "controlled_run_authorized": False,
        "controlled_run_started": False,
        "controlled_run_completed": False,
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


def build_controlled_walkthrough_run_window_preparation_bundle():
    plan = build_controlled_walkthrough_run_window_plan()
    status = build_controlled_walkthrough_run_window_status()
    adapter = build_real_surface_adapter_contract()
    prepared = (
        status["gp016_receipt_gate_prepared"] is True
        and status["window_template_prepared"] is True
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
        "window_prepared": prepared,
        "source_dependency": "GP016",
        "window_plan": plan,
        "room_scope": plan["room_scope"],
        "status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {"live_auto_locked": True},
        "next_build": "OB Controlled Walkthrough Run Opening Gate / GP018",
    }


def build_controlled_walkthrough_run_window_preparation_handoff():
    bundle = build_controlled_walkthrough_run_window_preparation_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "window_prepared": bundle["window_prepared"],
        "source_dependency": bundle["source_dependency"],
        "window_plan": bundle["window_plan"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Treat this as window preparation only.",
            "Do not open the run window.",
            "Do not authorize or start the controlled run.",
            "Do not start or accept the walkthrough.",
            "Do not open live routes.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP018 controlled walkthrough run opening gate.",
        ],
    }
