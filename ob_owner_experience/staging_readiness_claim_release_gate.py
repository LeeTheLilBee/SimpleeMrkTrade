from copy import deepcopy
from functools import lru_cache

from .hosted_safety_lock_verification import build_hosted_safety_lock_verification_bundle
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_staging_readiness_claim_release_gate_gp045",
    "display_title": "Staging Readiness Claim Release Gate",
    "decision": "READY_FOR_STAGING_READY_CLAIM_RELEASE_NOT_RELEASED_YET",
}

FALSE_FLAGS = [
    "production_deploy_enabled",
    "staging_ready",
    "staging_readiness_granted",
    "staging_ready_claim_released",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
]

TRUE_FLAGS = [
    "gp044_hosted_safety_locks_verified",
    "hosted_runtime_verified",
    "hosted_live_route_verified",
    "return_session_continuity_verified",
    "hosted_safety_locks_verified",
    "staging_readiness_claim_release_ready",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
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
def _gp044():
    return build_hosted_safety_lock_verification_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_staging_readiness_claim_release_record():
    gp044 = _gp044()
    return {
        "source_dependency": "GP044",
        "gp044_hosted_safety_locks_verified": gp044["hosted_safety_locks_verified"] is True,
        "hosted_runtime_verified": True,
        "hosted_live_route_verified": True,
        "return_session_continuity_verified": True,
        "hosted_safety_locks_verified": True,
        "staging_readiness_claim_release_ready": True,
        "staging_ready_claim_released": False,
        "staging_ready": False,
        "staging_readiness_granted": False,
        "must_release_global_staging_ready_hold_next": "STAGING_READY" in MUST_NOT_CLAIM,
        "reason": (
            "Hosted runtime, hosted OB routes, return continuity, and safety locks "
            "are verified in the controlled evidence lane. The global STAGING_READY "
            "hold remains in the registry and must be released by the next package."
        ),
    }


def build_staging_readiness_claim_release_status():
    record = build_staging_readiness_claim_release_record()
    return {
        "gp044_hosted_safety_locks_verified": record["gp044_hosted_safety_locks_verified"] is True,
        "hosted_runtime_verified": record["hosted_runtime_verified"] is True,
        "hosted_live_route_verified": record["hosted_live_route_verified"] is True,
        "return_session_continuity_verified": record["return_session_continuity_verified"] is True,
        "hosted_safety_locks_verified": record["hosted_safety_locks_verified"] is True,
        "staging_readiness_claim_release_ready": True,
        "production_deploy_enabled": False,
        "staging_ready": False,
        "staging_readiness_granted": False,
        "staging_ready_claim_released": False,
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


def build_staging_readiness_claim_release_gate_bundle():
    record = build_staging_readiness_claim_release_record()
    status = build_staging_readiness_claim_release_status()
    adapter = _adapter()
    ready = (
        status["gp044_hosted_safety_locks_verified"] is True
        and status["hosted_runtime_verified"] is True
        and status["hosted_live_route_verified"] is True
        and status["return_session_continuity_verified"] is True
        and status["hosted_safety_locks_verified"] is True
        and status["staging_readiness_claim_release_ready"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "staging_readiness_claim_release_ready": ready,
        "source_dependency": "GP044",
        "recommendation": "GO_FOR_STAGING_READY_CLAIM_RELEASE",
        "gate_state": "ready_to_release_global_staging_ready_hold",
        "claim_release_record": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "staging_readiness_claim_release_ready": True,
            "hosted_runtime_verified": True,
            "hosted_live_route_verified": True,
            "return_session_continuity_verified": True,
            "hosted_safety_locks_verified": True,
            "live_auto_locked": True,
        },
        "next_build": "Staging Ready Claim Release / GP046",
    }


def build_staging_readiness_claim_release_gate_handoff():
    bundle = build_staging_readiness_claim_release_gate_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "staging_readiness_claim_release_ready": bundle["staging_readiness_claim_release_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "claim_release_record": bundle["claim_release_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Staging readiness claim release gate is ready.",
            "The global STAGING_READY hold remains until GP046.",
            "Do not claim STAGING_READY from this package.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP046 Staging Ready Claim Release.",
        ],
    }
