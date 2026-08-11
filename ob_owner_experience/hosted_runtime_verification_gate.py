from copy import deepcopy
from functools import lru_cache

from .managed_staging_redeploy_execution_receipt import build_managed_staging_redeploy_execution_receipt_bundle
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_hosted_runtime_verification_gate_gp040",
    "display_title": "Hosted Runtime Verification Gate",
    "decision": "READY_FOR_HOSTED_RUNTIME_VERIFICATION_NOT_STAGING_READY",
}

REQUIRED_HOSTED_CHECKS = [
    "hosted /tower/healthz",
    "owner login available",
    "Tower Access Home available",
    "Tower to OB launch available",
    "six OB rooms reachable through Tower",
    "OB to Tower return available",
    "dangerous actions locked",
    "STAGING_READY not claimed before hosted evidence",
]

FALSE_FLAGS = [
    "hosted_runtime_verified",
    "hosted_live_route_verified",
    "staging_ready",
    "staging_readiness_granted",
    "production_deploy_enabled",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
]

TRUE_FLAGS = [
    "gp039_redeploy_execution_receipt_recorded",
    "hosted_runtime_verification_gate_ready",
    "hosted_runtime_checks_declared",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "hosted runtime verified claim before evidence",
    "hosted live route verified claim before evidence",
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
def _gp039():
    return build_managed_staging_redeploy_execution_receipt_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_hosted_runtime_verification_plan():
    gp039 = _gp039()
    return {
        "source_dependency": "GP039",
        "gp039_redeploy_execution_receipt_recorded": gp039["redeploy_execution_receipt_recorded"] is True,
        "hosted_runtime_verification_gate_ready": True,
        "required_hosted_checks": list(REQUIRED_HOSTED_CHECKS),
        "hosted_runtime_checks_declared": True,
        "hosted_runtime_verified": False,
        "hosted_live_route_verified": False,
        "staging_ready": False,
        "staging_readiness_granted": False,
        "safety_statement": (
            "Hosted runtime verification gate is ready. Actual hosted checks must be "
            "performed in the next package before any STAGING_READY claim."
        ),
    }


def build_hosted_runtime_verification_gate_status():
    plan = build_hosted_runtime_verification_plan()
    return {
        "gp039_redeploy_execution_receipt_recorded": plan["gp039_redeploy_execution_receipt_recorded"] is True,
        "hosted_runtime_verification_gate_ready": True,
        "hosted_runtime_checks_declared": len(plan["required_hosted_checks"]) == len(REQUIRED_HOSTED_CHECKS),
        "hosted_runtime_verified": False,
        "hosted_live_route_verified": False,
        "staging_ready": False,
        "staging_readiness_granted": False,
        "production_deploy_enabled": False,
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


def build_hosted_runtime_verification_gate_bundle():
    plan = build_hosted_runtime_verification_plan()
    status = build_hosted_runtime_verification_gate_status()
    adapter = _adapter()
    ready = (
        status["gp039_redeploy_execution_receipt_recorded"] is True
        and status["hosted_runtime_verification_gate_ready"] is True
        and status["hosted_runtime_checks_declared"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "hosted_runtime_verification_gate_ready": ready,
        "source_dependency": "GP039",
        "recommendation": "GO_FOR_HOSTED_RUNTIME_VERIFICATION_EXECUTION",
        "gate_state": "ready_for_hosted_runtime_verification_execution",
        "verification_plan": deepcopy(plan),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "hosted_runtime_verification_gate_ready": True,
            "hosted_runtime_checks_declared": True,
            "live_auto_locked": True,
        },
        "next_build": "Hosted Runtime Verification Execution / GP041",
    }


def build_hosted_runtime_verification_gate_handoff():
    bundle = build_hosted_runtime_verification_gate_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "hosted_runtime_verification_gate_ready": bundle["hosted_runtime_verification_gate_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "verification_plan": bundle["verification_plan"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Hosted runtime verification gate is ready.",
            "Do not claim hosted runtime verification from this package.",
            "Do not claim STAGING_READY.",
            "Run hosted runtime verification execution next.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP041 Hosted Runtime Verification Execution.",
        ],
    }
