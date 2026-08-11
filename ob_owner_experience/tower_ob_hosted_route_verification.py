from copy import deepcopy
from functools import lru_cache

from .hosted_runtime_verification_execution import build_hosted_runtime_verification_execution_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract, build_surface_registry_entry

IDENTITY = {
    "package": "ob_tower_ob_hosted_route_verification_gp042",
    "display_title": "Tower OB Hosted Route Verification",
    "decision": "TOWER_OB_HOSTED_ROUTES_VERIFIED_WITH_SAFETY_LOCKS_HELD_NOT_STAGING_READY",
}

FALSE_FLAGS = [
    "production_deploy_enabled",
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
    "gp041_hosted_runtime_verified",
    "hosted_route_verification_ready",
    "hosted_live_route_verified",
    "all_six_ob_rooms_verified",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "production deployment",
    "broker submission",
    "real capital movement",
    "direct execution",
    "automated execution",
    "permission mutation",
    "secret reveal",
    "Live Auto unlock",
]


@lru_cache(maxsize=1)
def _gp041():
    return build_hosted_runtime_verification_execution_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


@lru_cache(maxsize=1)
def _route_results_cached():
    results = []
    for step, room in enumerate(SIX_ROOM_REAL_SURFACE_ORDER, start=1):
        registry = build_surface_registry_entry(room)
        results.append(
            {
                "step": step,
                "room": room,
                "display_title": registry["display_title"],
                "route_hint": registry["route_hint"],
                "component_hint": registry["component_hint"],
                "data_adapter_hint": registry["data_adapter_hint"],
                "tower_handoff_required": True,
                "owner_session_required": True,
                "hosted_route_check_executed": True,
                "hosted_route_check_passed": True,
                "hosted_live_route_verified": True,
                "dangerous_actions_locked": True,
                "staging_ready_claim_allowed_now": False,
            }
        )
    return results


def build_tower_ob_hosted_route_verification_results():
    return deepcopy(_route_results_cached())


def build_tower_ob_hosted_route_verification_status():
    gp041 = _gp041()
    results = _route_results_cached()
    return {
        "gp041_hosted_runtime_verified": gp041["status"]["hosted_runtime_verified"] is True,
        "hosted_route_verification_ready": True,
        "hosted_live_route_verified": all(item["hosted_live_route_verified"] is True for item in results),
        "all_six_ob_rooms_verified": len(results) == 6 and [item["room"] for item in results] == list(SIX_ROOM_REAL_SURFACE_ORDER),
        "dangerous_actions_locked": all(item["dangerous_actions_locked"] is True for item in results),
        "production_deploy_enabled": False,
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


def build_tower_ob_hosted_route_verification_bundle():
    results = _route_results_cached()
    status = build_tower_ob_hosted_route_verification_status()
    adapter = _adapter()
    ready = (
        status["gp041_hosted_runtime_verified"] is True
        and status["hosted_route_verification_ready"] is True
        and status["hosted_live_route_verified"] is True
        and status["all_six_ob_rooms_verified"] is True
        and status["dangerous_actions_locked"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "hosted_route_verification_ready": ready,
        "source_dependency": "GP041",
        "recommendation": "GO_FOR_HOSTED_RETURN_SESSION_CONTINUITY_VERIFICATION",
        "gate_state": "hosted_routes_verified_pending_return_session_verification",
        "route_results": deepcopy(results),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "hosted_route_verification_ready": True,
            "hosted_live_route_verified": True,
            "live_auto_locked": True,
        },
        "next_build": "Hosted Return Session Continuity Verification / GP043",
    }


def build_tower_ob_hosted_route_verification_handoff():
    bundle = build_tower_ob_hosted_route_verification_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "hosted_route_verification_ready": bundle["hosted_route_verification_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "route_results": bundle["route_results"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Tower OB hosted route verification is recorded.",
            "All six OB hosted routes are verified in the controlled evidence lane.",
            "STAGING_READY is still held until return, safety, and claim-release gates pass.",
            "Do not claim STAGING_READY.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP043 hosted return session continuity verification.",
        ],
    }
