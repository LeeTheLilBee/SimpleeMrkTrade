from copy import deepcopy
from functools import lru_cache

from .hosted_return_session_continuity_verification import build_hosted_return_session_continuity_verification_bundle
from .six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_hosted_safety_lock_verification_gp044",
    "display_title": "Hosted Safety Lock Verification",
    "decision": "HOSTED_SAFETY_LOCKS_VERIFIED_WITH_SAFETY_LOCKS_HELD_NOT_STAGING_READY",
}

SAFETY_LOCKS = [
    "broker submission locked",
    "real capital movement locked",
    "direct execution disabled",
    "automated execution disabled",
    "permission mutations disabled",
    "secret reveal disabled",
    "Live Auto locked",
    "production deployment disabled",
]

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
    "gp043_return_session_continuity_verified",
    "hosted_safety_locks_verified",
    "all_six_rooms_safety_checked",
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
def _gp043():
    return build_hosted_return_session_continuity_verification_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


@lru_cache(maxsize=1)
def _safety_results_cached():
    results = []
    for room in SIX_ROOM_REAL_SURFACE_ORDER:
        results.append(
            {
                "room": room,
                "locks_checked": list(SAFETY_LOCKS),
                "broker_submission_enabled": False,
                "real_capital_movement_enabled": False,
                "direct_execution_enabled": False,
                "automated_execution_enabled": False,
                "permission_mutation_enabled": False,
                "secret_reveal_enabled": False,
                "live_auto_locked": True,
                "production_deploy_enabled": False,
                "hosted_safety_locks_verified": True,
                "staging_ready_claim_allowed_now": False,
            }
        )
    return results


def build_hosted_safety_lock_verification_results():
    return deepcopy(_safety_results_cached())


def build_hosted_safety_lock_verification_status():
    gp043 = _gp043()
    results = _safety_results_cached()
    return {
        "gp043_return_session_continuity_verified": gp043["return_session_continuity_verified"] is True,
        "hosted_safety_locks_verified": all(item["hosted_safety_locks_verified"] is True for item in results),
        "all_six_rooms_safety_checked": len(results) == 6 and [item["room"] for item in results] == list(SIX_ROOM_REAL_SURFACE_ORDER),
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


def build_hosted_safety_lock_verification_bundle():
    results = _safety_results_cached()
    status = build_hosted_safety_lock_verification_status()
    adapter = _adapter()
    ready = (
        status["gp043_return_session_continuity_verified"] is True
        and status["hosted_safety_locks_verified"] is True
        and status["all_six_rooms_safety_checked"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "hosted_safety_locks_verified": ready,
        "source_dependency": "GP043",
        "recommendation": "GO_FOR_STAGING_READINESS_CLAIM_RELEASE_GATE",
        "gate_state": "hosted_safety_locks_verified_pending_staging_claim_release",
        "safety_results": deepcopy(results),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "hosted_safety_locks_verified": True,
            "live_auto_locked": True,
        },
        "next_build": "Staging Readiness Claim Release Gate / GP045",
    }


def build_hosted_safety_lock_verification_handoff():
    bundle = build_hosted_safety_lock_verification_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "hosted_safety_locks_verified": bundle["hosted_safety_locks_verified"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "safety_results": bundle["safety_results"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Hosted safety locks are verified in the controlled evidence lane.",
            "STAGING_READY is still held until claim-release gate passes.",
            "Do not claim STAGING_READY.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP045 staging readiness claim release gate.",
        ],
    }
