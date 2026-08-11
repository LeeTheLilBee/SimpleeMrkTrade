from copy import deepcopy
from functools import lru_cache

from .integrated_controlled_route_check_execution import build_integrated_controlled_route_check_execution_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_owner_walkthrough_start_clearance_gate_gp030",
    "display_title": "Owner Walkthrough Start Clearance Gate",
    "decision": "READY_FOR_OWNER_WALKTHROUGH_CONTROLLED_START_PENDING_OWNER_ACTION",
}

FALSE_FLAGS = [
    "render_redeployed",
    "production_deploy_enabled",
    "live_route_verified",
    "live_routes_opened",
    "owner_walkthrough_started",
    "owner_walkthrough_accepted",
    "staging_ready",
    "staging_readiness_granted",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
]

TRUE_FLAGS = [
    "gp029_controlled_route_check_executed",
    "gp029_controlled_route_check_passed",
    "walkthrough_start_clearance_ready",
    "owner_action_required_to_start",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "Render redeploy",
    "production deployment",
    "hosted live route verification claim",
    "automatic owner walkthrough start",
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
def _gp029():
    return build_integrated_controlled_route_check_execution_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_owner_walkthrough_start_clearance_record():
    gp029 = _gp029()
    return {
        "recommendation": "GO_FOR_CONTROLLED_OWNER_WALKTHROUGH_START",
        "source_dependency": "GP029",
        "gp029_controlled_route_check_executed": gp029["controlled_route_check_executed"] is True,
        "rooms_cleared": [item["room"] for item in gp029["controlled_route_results"]],
        "room_order": list(SIX_ROOM_REAL_SURFACE_ORDER),
        "walkthrough_start_clearance_ready": True,
        "owner_action_required_to_start": True,
        "owner_walkthrough_started": False,
        "owner_walkthrough_accepted": False,
        "staging_ready": False,
        "staging_readiness_granted": False,
        "safety_statement": (
            "Controlled owner walkthrough may be started next by explicit owner action. "
            "This gate does not start or accept the walkthrough and does not claim STAGING_READY."
        ),
    }


def build_owner_walkthrough_start_clearance_status():
    gp029 = _gp029()
    record = build_owner_walkthrough_start_clearance_record()
    return {
        "gp029_controlled_route_check_executed": gp029["controlled_route_check_executed"] is True,
        "gp029_controlled_route_check_passed": all(item["controlled_route_check_passed"] is True for item in gp029["controlled_route_results"]),
        "walkthrough_start_clearance_ready": True,
        "owner_action_required_to_start": True,
        "all_six_rooms_cleared": record["rooms_cleared"] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "render_redeployed": False,
        "production_deploy_enabled": False,
        "live_route_verified": False,
        "live_routes_opened": False,
        "owner_walkthrough_started": False,
        "owner_walkthrough_accepted": False,
        "staging_ready": False,
        "staging_readiness_granted": False,
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


def build_owner_walkthrough_start_clearance_gate_bundle():
    record = build_owner_walkthrough_start_clearance_record()
    status = build_owner_walkthrough_start_clearance_status()
    adapter = _adapter()
    ready = (
        status["gp029_controlled_route_check_executed"] is True
        and status["gp029_controlled_route_check_passed"] is True
        and status["walkthrough_start_clearance_ready"] is True
        and status["owner_action_required_to_start"] is True
        and status["all_six_rooms_cleared"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "walkthrough_start_clearance_ready": ready,
        "source_dependency": "GP029",
        "recommendation": record["recommendation"],
        "gate_state": "ready_for_explicit_owner_controlled_walkthrough_start",
        "clearance_record": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "walkthrough_start_clearance_ready": True,
            "owner_action_required_to_start": True,
            "live_auto_locked": True,
        },
        "next_build": "Owner Walkthrough Controlled Start / GP031",
    }


def build_owner_walkthrough_start_clearance_gate_handoff():
    bundle = build_owner_walkthrough_start_clearance_gate_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "walkthrough_start_clearance_ready": bundle["walkthrough_start_clearance_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "clearance_record": bundle["clearance_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Controlled owner walkthrough start is cleared for the next package.",
            "Owner action is required to start the walkthrough.",
            "This package does not start the walkthrough.",
            "This package does not accept the walkthrough.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP031 Owner Walkthrough Controlled Start.",
        ],
    }
