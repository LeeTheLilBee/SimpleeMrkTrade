from copy import deepcopy

from .six_room_walkthrough_evidence_capture_plan import build_six_room_walkthrough_evidence_capture_plan_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_owner_walkthrough_acceptance_hold_closeout_gp020",
    "display_title": "Owner Walkthrough Acceptance Hold Closeout",
    "decision": "READY_FOR_OWNER_WALKTHROUGH_ACCEPTANCE_HOLD_CLOSEOUT_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "owner_walkthrough_acceptance_allowed",
    "owner_walkthrough_accepted",
    "owner_walkthrough_started",
    "evidence_capture_started",
    "evidence_finalized",
    "controlled_run_gate_open",
    "controlled_run_authorized",
    "controlled_run_started",
    "controlled_run_completed",
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
    "gp019_capture_plan_prepared",
    "acceptance_hold_recorded",
    "walkthrough_prep_lane_closed",
    "integration_handoff_ready",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "owner walkthrough acceptance",
    "owner walkthrough start",
    "evidence capture start",
    "controlled run authorization",
    "controlled run start",
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


def build_owner_walkthrough_acceptance_hold():
    gp019 = build_six_room_walkthrough_evidence_capture_plan_bundle()
    return {
        "hold_type": "owner_walkthrough_acceptance_hold",
        "source_dependency": "GP019",
        "acceptance_hold_recorded": True,
        "acceptance_allowed_now": False,
        "owner_walkthrough_accepted": False,
        "walkthrough_prep_lane_closed": True,
        "integration_handoff_ready": True,
        "room_order": list(SIX_ROOM_REAL_SURFACE_ORDER),
        "room_scope": deepcopy(gp019["capture_matrix"]),
        "hold_reason": (
            "OB has prepared the walkthrough path through GP020, but the real owner "
            "walkthrough must wait for Tower integration, owner session continuity, "
            "controlled route verification, and a future explicit owner run."
        ),
    }


def build_owner_walkthrough_acceptance_hold_status():
    gp019 = build_six_room_walkthrough_evidence_capture_plan_bundle()
    hold = build_owner_walkthrough_acceptance_hold()
    return {
        "gp019_capture_plan_prepared": gp019["capture_plan_prepared"] is True,
        "acceptance_hold_recorded": True,
        "walkthrough_prep_lane_closed": True,
        "integration_handoff_ready": True,
        "all_six_rooms_present": hold["room_order"] == list(SIX_ROOM_REAL_SURFACE_ORDER) and len(hold["room_scope"]) == 6,
        "owner_walkthrough_acceptance_allowed": False,
        "owner_walkthrough_accepted": False,
        "owner_walkthrough_started": False,
        "evidence_capture_started": False,
        "evidence_finalized": False,
        "controlled_run_gate_open": False,
        "controlled_run_authorized": False,
        "controlled_run_started": False,
        "controlled_run_completed": False,
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


def build_owner_walkthrough_acceptance_hold_closeout_bundle():
    hold = build_owner_walkthrough_acceptance_hold()
    status = build_owner_walkthrough_acceptance_hold_status()
    adapter = build_real_surface_adapter_contract()
    closeout_ready = (
        status["gp019_capture_plan_prepared"] is True
        and status["acceptance_hold_recorded"] is True
        and status["walkthrough_prep_lane_closed"] is True
        and status["integration_handoff_ready"] is True
        and status["all_six_rooms_present"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "closeout_ready": closeout_ready,
        "source_dependency": "GP019",
        "acceptance_hold": hold,
        "room_scope": hold["room_scope"],
        "status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {"live_auto_locked": True},
        "next_build": "Tower OB route integration preflight / GP021",
    }


def build_owner_walkthrough_acceptance_hold_closeout_handoff():
    bundle = build_owner_walkthrough_acceptance_hold_closeout_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "closeout_ready": bundle["closeout_ready"],
        "source_dependency": bundle["source_dependency"],
        "acceptance_hold": bundle["acceptance_hold"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "takeover_summary": (
            "GP020 closes the OB owner walkthrough preparation lane with acceptance "
            "held. OB is ready to proceed into Tower/OB integration preflight, but "
            "the real owner walkthrough is not started or accepted."
        ),
        "next_builder_notes": [
            "Treat GP015 through GP020 as the closed OB walkthrough preparation lane.",
            "Owner walkthrough acceptance is held.",
            "Do not start or accept the real owner walkthrough from this package.",
            "Proceed next to Tower OB route integration preflight.",
            "Repair Tower return/session continuity in the integration lane, not here.",
            "Do not redeploy Render from this package.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is Tower OB route integration preflight / GP021.",
        ],
    }
