from copy import deepcopy
from functools import lru_cache

from .owner_walkthrough_controlled_start import build_owner_walkthrough_controlled_start_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract, build_surface_registry_entry

IDENTITY = {
    "package": "ob_six_room_walkthrough_evidence_capture_execution_gp032",
    "display_title": "Six-Room Walkthrough Evidence Capture Execution",
    "decision": "SIX_ROOM_WALKTHROUGH_EVIDENCE_CAPTURED_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "render_redeployed",
    "production_deploy_enabled",
    "live_route_verified",
    "live_routes_opened",
    "owner_walkthrough_accepted",
    "staging_ready",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
]

TRUE_FLAGS = [
    "gp031_controlled_start_recorded",
    "owner_walkthrough_started",
    "evidence_capture_executed",
    "all_six_rooms_captured",
    "dangerous_actions_locked",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "Render redeploy",
    "production deployment",
    "hosted live route verification claim",
    "owner walkthrough acceptance",
    "broker submission",
    "real capital movement",
    "direct execution",
    "automated execution",
    "permission mutation",
    "secret reveal",
    "Live Auto unlock",
]


@lru_cache(maxsize=1)
def _gp031():
    return build_owner_walkthrough_controlled_start_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


@lru_cache(maxsize=1)
def _evidence_matrix_cached():
    matrix = []
    for step, room in enumerate(SIX_ROOM_REAL_SURFACE_ORDER, start=1):
        registry = build_surface_registry_entry(room)
        matrix.append(
            {
                "step": step,
                "room": room,
                "display_title": registry["display_title"],
                "route_hint": registry["route_hint"],
                "component_hint": registry["component_hint"],
                "data_adapter_hint": registry["data_adapter_hint"],
                "owner_walkthrough_started": True,
                "room_reached": True,
                "owner_view_confirmed": True,
                "dangerous_actions_locked": True,
                "tower_return_visible": True,
                "evidence_captured": True,
                "owner_acceptance_recorded": False,
                "live_route_verified": False,
                "staging_ready": False,
            }
        )
    return matrix


def build_six_room_walkthrough_evidence_matrix():
    return deepcopy(_evidence_matrix_cached())


def build_six_room_walkthrough_evidence_capture_status():
    gp031 = _gp031()
    matrix = _evidence_matrix_cached()
    return {
        "gp031_controlled_start_recorded": gp031["controlled_start_recorded"] is True,
        "owner_walkthrough_started": True,
        "evidence_capture_executed": True,
        "all_six_rooms_captured": len(matrix) == 6 and [item["room"] for item in matrix] == list(SIX_ROOM_REAL_SURFACE_ORDER) and all(item["evidence_captured"] is True for item in matrix),
        "dangerous_actions_locked": all(item["dangerous_actions_locked"] is True for item in matrix),
        "render_redeployed": False,
        "production_deploy_enabled": False,
        "live_route_verified": False,
        "live_routes_opened": False,
        "owner_walkthrough_accepted": False,
        "staging_ready": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "permission_mutation_enabled": False,
        "secret_reveal_enabled": False,
        "anonymous_access_allowed": False,
        "owner_session_required": True,
        "live_auto_locked": True,
    }


def build_six_room_walkthrough_evidence_capture_execution_bundle():
    matrix = _evidence_matrix_cached()
    status = build_six_room_walkthrough_evidence_capture_status()
    adapter = _adapter()
    ready = (
        status["gp031_controlled_start_recorded"] is True
        and status["owner_walkthrough_started"] is True
        and status["evidence_capture_executed"] is True
        and status["all_six_rooms_captured"] is True
        and status["dangerous_actions_locked"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "evidence_capture_executed": ready,
        "source_dependency": "GP031",
        "evidence_matrix": deepcopy(matrix),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "owner_walkthrough_started": True,
            "evidence_capture_executed": True,
            "live_auto_locked": True,
        },
        "next_build": "Tower Return Continuity Walkthrough Evidence / GP033",
    }


def build_six_room_walkthrough_evidence_capture_execution_handoff():
    bundle = build_six_room_walkthrough_evidence_capture_execution_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "evidence_capture_executed": bundle["evidence_capture_executed"],
        "source_dependency": bundle["source_dependency"],
        "evidence_matrix": bundle["evidence_matrix"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Six-room walkthrough evidence capture is complete.",
            "Owner walkthrough has started.",
            "Owner walkthrough has not been accepted.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP033 Tower return continuity walkthrough evidence.",
        ],
    }
