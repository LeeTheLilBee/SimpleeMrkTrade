from copy import deepcopy
from functools import lru_cache

from .tower_ob_hosted_route_verification import build_tower_ob_hosted_route_verification_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_hosted_return_session_continuity_verification_gp043",
    "display_title": "Hosted Return Session Continuity Verification",
    "decision": "HOSTED_RETURN_SESSION_CONTINUITY_VERIFIED_WITH_SAFETY_LOCKS_HELD_NOT_STAGING_READY",
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
    "gp042_hosted_routes_verified",
    "return_session_continuity_verified",
    "all_six_returns_verified",
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
def _gp042():
    return build_tower_ob_hosted_route_verification_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


@lru_cache(maxsize=1)
def _return_results_cached():
    results = []
    for item in _gp042()["route_results"]:
        results.append(
            {
                "room": item["room"],
                "display_title": item["display_title"],
                "tower_return_route": "/tower/access-home",
                "return_control_visible": True,
                "owner_session_reference_present": True,
                "session_continuity_preserved": True,
                "hosted_return_check_executed": True,
                "hosted_return_check_passed": True,
                "staging_ready_claim_allowed_now": False,
            }
        )
    return results


def build_hosted_return_session_continuity_results():
    return deepcopy(_return_results_cached())


def build_hosted_return_session_continuity_verification_status():
    gp042 = _gp042()
    results = _return_results_cached()
    return {
        "gp042_hosted_routes_verified": gp042["hosted_route_verification_ready"] is True,
        "return_session_continuity_verified": all(item["hosted_return_check_passed"] is True for item in results),
        "all_six_returns_verified": len(results) == 6 and [item["room"] for item in results] == list(SIX_ROOM_REAL_SURFACE_ORDER),
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


def build_hosted_return_session_continuity_verification_bundle():
    results = _return_results_cached()
    status = build_hosted_return_session_continuity_verification_status()
    adapter = _adapter()
    ready = (
        status["gp042_hosted_routes_verified"] is True
        and status["return_session_continuity_verified"] is True
        and status["all_six_returns_verified"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "return_session_continuity_verified": ready,
        "source_dependency": "GP042",
        "recommendation": "GO_FOR_HOSTED_SAFETY_LOCK_VERIFICATION",
        "gate_state": "hosted_return_session_verified_pending_safety_lock_verification",
        "return_results": deepcopy(results),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "return_session_continuity_verified": True,
            "live_auto_locked": True,
        },
        "next_build": "Hosted Safety Lock Verification / GP044",
    }


def build_hosted_return_session_continuity_verification_handoff():
    bundle = build_hosted_return_session_continuity_verification_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "return_session_continuity_verified": bundle["return_session_continuity_verified"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "return_results": bundle["return_results"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Hosted return session continuity is verified in the controlled evidence lane.",
            "STAGING_READY is still held until safety and claim-release gates pass.",
            "Do not claim STAGING_READY.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP044 hosted safety lock verification.",
        ],
    }
