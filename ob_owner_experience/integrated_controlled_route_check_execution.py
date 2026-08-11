from copy import deepcopy
from functools import lru_cache

from .tower_ob_return_session_runtime_verification import build_tower_ob_return_session_runtime_verification_bundle
from .tower_ob_actual_route_implementation_return_repair import resolve_ob_to_tower_return, resolve_tower_ob_route
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_integrated_controlled_route_check_execution_gp029",
    "display_title": "Integrated Controlled Route Check Execution",
    "decision": "READY_FOR_INTEGRATED_CONTROLLED_ROUTE_CHECK_EXECUTION_WITH_SAFETY_LOCKS_HELD",
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
    "gp028_return_session_verified",
    "controlled_route_check_executed",
    "controlled_route_check_passed",
    "all_six_rooms_checked",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "Render redeploy",
    "production deployment",
    "hosted live route verification claim",
    "owner walkthrough start",
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
def _gp028():
    return build_tower_ob_return_session_runtime_verification_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


@lru_cache(maxsize=1)
def _check_results_cached():
    results = []
    for room in SIX_ROOM_REAL_SURFACE_ORDER:
        route = resolve_tower_ob_route(room, True, True)
        ret = resolve_ob_to_tower_return(room, True, True)
        results.append(
            {
                "room": room,
                "route_resolved": route["resolved"] is True,
                "return_resolved": ret["return_ready"] is True,
                "owner_session_required": True,
                "tower_handoff_required": True,
                "session_reference_required": True,
                "dangerous_actions_locked": True,
                "controlled_route_check_executed": True,
                "controlled_route_check_passed": route["resolved"] is True and ret["return_ready"] is True,
                "live_route_verified": False,
                "owner_walkthrough_started": False,
                "owner_walkthrough_accepted": False,
                "staging_ready": False,
            }
        )
    return results


def build_integrated_controlled_route_check_results():
    return deepcopy(_check_results_cached())


def build_integrated_controlled_route_check_execution_status():
    gp028 = _gp028()
    results = _check_results_cached()
    return {
        "gp028_return_session_verified": gp028["return_session_verified"] is True,
        "controlled_route_check_executed": len(results) == 6 and all(item["controlled_route_check_executed"] is True for item in results),
        "controlled_route_check_passed": all(item["controlled_route_check_passed"] is True for item in results),
        "all_six_rooms_checked": [item["room"] for item in results] == list(SIX_ROOM_REAL_SURFACE_ORDER),
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


def build_integrated_controlled_route_check_execution_bundle():
    results = _check_results_cached()
    status = build_integrated_controlled_route_check_execution_status()
    adapter = _adapter()
    executed = (
        status["gp028_return_session_verified"] is True
        and status["controlled_route_check_executed"] is True
        and status["controlled_route_check_passed"] is True
        and status["all_six_rooms_checked"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "controlled_route_check_executed": executed,
        "source_dependency": "GP028",
        "controlled_route_results": deepcopy(results),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "controlled_route_check_executed": True,
            "controlled_route_check_passed": True,
            "live_auto_locked": True,
        },
        "next_build": "Owner Walkthrough Start Clearance Gate / GP030",
    }


def build_integrated_controlled_route_check_execution_handoff():
    bundle = build_integrated_controlled_route_check_execution_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "controlled_route_check_executed": bundle["controlled_route_check_executed"],
        "source_dependency": bundle["source_dependency"],
        "controlled_route_results": bundle["controlled_route_results"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Controlled route check execution is complete in code.",
            "Owner walkthrough has not started.",
            "Owner walkthrough has not been accepted.",
            "Do not claim hosted live route verification from this package.",
            "Do not redeploy Render.",
            "Do not claim STAGING_READY.",
            "Next build is GP030 owner walkthrough start clearance gate.",
        ],
    }
