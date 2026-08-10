from copy import deepcopy

from .controlled_walkthrough_run_window_preparation import build_controlled_walkthrough_run_window_preparation_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_controlled_walkthrough_run_opening_gate_gp018",
    "display_title": "Controlled Walkthrough Run Opening Gate",
    "decision": "READY_FOR_CONTROLLED_WALKTHROUGH_RUN_OPENING_GATE_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "opening_gate_open",
    "opening_authorized",
    "window_open",
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
    "gp017_window_prepared",
    "opening_gate_prepared",
    "opening_gate_closed",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "opening gate opening",
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


def build_controlled_walkthrough_run_opening_requirements():
    gp017 = build_controlled_walkthrough_run_window_preparation_bundle()
    return [
        {"key": "gp017_window_prepared", "required": True, "satisfied_now": gp017["window_prepared"] is True},
        {"key": "owner_authorization_decision_recorded", "required": True, "satisfied_now": False},
        {"key": "decision_receipt_emitted", "required": True, "satisfied_now": False},
        {"key": "tower_owner_session_active", "required": True, "satisfied_now": False},
        {"key": "step_up_complete", "required": True, "satisfied_now": False},
        {"key": "evidence_capture_armed", "required": True, "satisfied_now": False},
    ]


def build_controlled_walkthrough_run_opening_gate_status():
    gp017 = build_controlled_walkthrough_run_window_preparation_bundle()
    requirements = build_controlled_walkthrough_run_opening_requirements()
    return {
        "gp017_window_prepared": gp017["window_prepared"] is True,
        "opening_gate_prepared": True,
        "opening_gate_closed": True,
        "required_future_authorizations_registered": len(requirements) == 6,
        "opening_gate_open": False,
        "opening_authorized": False,
        "window_open": False,
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


def build_controlled_walkthrough_run_opening_gate_bundle():
    gp017 = build_controlled_walkthrough_run_window_preparation_bundle()
    requirements = build_controlled_walkthrough_run_opening_requirements()
    status = build_controlled_walkthrough_run_opening_gate_status()
    adapter = build_real_surface_adapter_contract()
    prepared = (
        status["gp017_window_prepared"] is True
        and status["opening_gate_prepared"] is True
        and status["opening_gate_closed"] is True
        and len(gp017["room_scope"]) == 6
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "opening_gate_prepared": prepared,
        "source_dependency": "GP017",
        "gate_state": "closed_pending_future_owner_authorization_and_step_up",
        "opening_requirements": requirements,
        "room_scope": deepcopy(gp017["room_scope"]),
        "status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {"live_auto_locked": True},
        "next_build": "OB Six-Room Walkthrough Evidence Capture Plan / GP019",
    }


def build_controlled_walkthrough_run_opening_gate_handoff():
    bundle = build_controlled_walkthrough_run_opening_gate_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "opening_gate_prepared": bundle["opening_gate_prepared"],
        "source_dependency": bundle["source_dependency"],
        "gate_state": bundle["gate_state"],
        "opening_requirements": bundle["opening_requirements"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Treat this as opening gate preparation only.",
            "Do not open the opening gate.",
            "Do not authorize or start the controlled run.",
            "Do not start or accept the walkthrough.",
            "Do not open live routes.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP019 six-room walkthrough evidence capture plan.",
        ],
    }
