from copy import deepcopy

from .controlled_walkthrough_run_opening_gate import build_controlled_walkthrough_run_opening_gate_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_six_room_walkthrough_evidence_capture_plan_gp019",
    "display_title": "Six-Room Walkthrough Evidence Capture Plan",
    "decision": "READY_FOR_SIX_ROOM_WALKTHROUGH_EVIDENCE_CAPTURE_PLAN_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "evidence_capture_started",
    "evidence_captured",
    "evidence_finalized",
    "opening_gate_open",
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
    "gp018_opening_gate_prepared",
    "capture_plan_prepared",
    "append_only_required",
    "redaction_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "evidence capture start",
    "walkthrough evidence finalized",
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


def build_six_room_walkthrough_evidence_capture_matrix():
    gp018 = build_controlled_walkthrough_run_opening_gate_bundle()
    matrix = []
    for item in gp018["room_scope"]:
        matrix.append({
            "room": item["room"],
            "step": item["step"],
            "display_title": item["display_title"],
            "route_hint": item["route_hint"],
            "component_hint": item["component_hint"],
            "data_adapter_hint": item["data_adapter_hint"],
            "capture_required": True,
            "capture_started": False,
            "capture_completed": False,
            "evidence_finalized": False,
            "owner_acceptance_recorded": False,
            "required_evidence": [
                "route reached under owner session",
                "room purpose visible",
                "dangerous actions unavailable",
                "STAGING_READY not claimed",
                "Tower return status observed but not repaired by this package",
            ],
        })
    return matrix


def build_six_room_walkthrough_evidence_capture_status():
    gp018 = build_controlled_walkthrough_run_opening_gate_bundle()
    matrix = build_six_room_walkthrough_evidence_capture_matrix()
    return {
        "gp018_opening_gate_prepared": gp018["opening_gate_prepared"] is True,
        "capture_plan_prepared": True,
        "append_only_required": True,
        "redaction_required": True,
        "all_six_rooms_planned": len(matrix) == 6 and [item["room"] for item in matrix] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "evidence_capture_started": False,
        "evidence_captured": False,
        "evidence_finalized": False,
        "opening_gate_open": False,
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


def build_six_room_walkthrough_evidence_capture_plan_bundle():
    matrix = build_six_room_walkthrough_evidence_capture_matrix()
    status = build_six_room_walkthrough_evidence_capture_status()
    adapter = build_real_surface_adapter_contract()
    prepared = (
        status["gp018_opening_gate_prepared"] is True
        and status["capture_plan_prepared"] is True
        and status["all_six_rooms_planned"] is True
        and all(item["capture_required"] is True for item in matrix)
        and all(item["capture_started"] is False for item in matrix)
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "capture_plan_prepared": prepared,
        "source_dependency": "GP018",
        "capture_matrix": matrix,
        "status": status,
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {"live_auto_locked": True},
        "next_build": "OB Owner Walkthrough Acceptance Hold Closeout / GP020",
    }


def build_six_room_walkthrough_evidence_capture_plan_handoff():
    bundle = build_six_room_walkthrough_evidence_capture_plan_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "capture_plan_prepared": bundle["capture_plan_prepared"],
        "source_dependency": bundle["source_dependency"],
        "capture_matrix": bundle["capture_matrix"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Treat this as evidence capture planning only.",
            "Do not start evidence capture from this package.",
            "Do not finalize walkthrough evidence from this package.",
            "Do not start or accept the walkthrough.",
            "Do not open live routes.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP020 owner walkthrough acceptance hold closeout.",
        ],
    }
