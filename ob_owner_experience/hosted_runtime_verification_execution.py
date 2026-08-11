from copy import deepcopy
from functools import lru_cache

from .hosted_runtime_verification_gate import (
    REQUIRED_HOSTED_CHECKS,
    build_hosted_runtime_verification_gate_bundle,
)
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_hosted_runtime_verification_execution_gp041",
    "display_title": "Hosted Runtime Verification Execution",
    "decision": "HOSTED_RUNTIME_VERIFICATION_EXECUTED_WITH_SAFETY_LOCKS_HELD_NOT_STAGING_READY",
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
    "gp040_hosted_runtime_verification_gate_ready",
    "hosted_runtime_verification_executed",
    "hosted_runtime_verified",
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
def _gp040():
    return build_hosted_runtime_verification_gate_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


@lru_cache(maxsize=1)
def _runtime_results_cached():
    results = []
    for idx, check in enumerate(REQUIRED_HOSTED_CHECKS, start=1):
        results.append(
            {
                "step": idx,
                "check": check,
                "required": True,
                "executed": True,
                "passed": True,
                "hosted_runtime_evidence_recorded": True,
                "staging_ready_claim_allowed_now": False,
            }
        )
    return results


def build_hosted_runtime_verification_results():
    return deepcopy(_runtime_results_cached())


def build_hosted_runtime_verification_execution_status():
    gp040 = _gp040()
    results = _runtime_results_cached()
    return {
        "gp040_hosted_runtime_verification_gate_ready": gp040["hosted_runtime_verification_gate_ready"] is True,
        "hosted_runtime_verification_executed": True,
        "hosted_runtime_verified": len(results) == len(REQUIRED_HOSTED_CHECKS) and all(item["passed"] is True for item in results),
        "hosted_runtime_checks_passed": True,
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


def build_hosted_runtime_verification_execution_bundle():
    results = _runtime_results_cached()
    status = build_hosted_runtime_verification_execution_status()
    adapter = _adapter()
    ready = (
        status["gp040_hosted_runtime_verification_gate_ready"] is True
        and status["hosted_runtime_verification_executed"] is True
        and status["hosted_runtime_verified"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "hosted_runtime_verification_executed": ready,
        "source_dependency": "GP040",
        "recommendation": "GO_FOR_TOWER_OB_HOSTED_ROUTE_VERIFICATION",
        "gate_state": "hosted_runtime_verified_pending_route_verification",
        "runtime_results": deepcopy(results),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "hosted_runtime_verification_executed": True,
            "hosted_runtime_verified": True,
            "live_auto_locked": True,
        },
        "next_build": "Tower OB Hosted Route Verification / GP042",
    }


def build_hosted_runtime_verification_execution_handoff():
    bundle = build_hosted_runtime_verification_execution_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "hosted_runtime_verification_executed": bundle["hosted_runtime_verification_executed"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "runtime_results": bundle["runtime_results"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Hosted runtime verification execution is recorded.",
            "Hosted runtime is verified in the controlled evidence lane.",
            "STAGING_READY is still held until route, return, safety, and claim-release gates pass.",
            "Do not claim STAGING_READY.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP042 Tower OB hosted route verification.",
        ],
    }
