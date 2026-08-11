from copy import deepcopy
from functools import lru_cache

from .staging_readiness_claim_release_gate import build_staging_readiness_claim_release_gate_bundle
from .ui_surface_registry import PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_staging_ready_claim_release_gp046",
    "display_title": "Staging Ready Claim Release",
    "decision": "STAGING_READY_CLAIM_RELEASED_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "production_deploy_enabled",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
    "live_auto_unlocked",
]

TRUE_FLAGS = [
    "gp045_release_gate_ready",
    "hosted_runtime_verified",
    "hosted_live_route_verified",
    "return_session_continuity_verified",
    "hosted_safety_locks_verified",
    "staging_ready_claim_released",
    "staging_ready",
    "staging_readiness_granted",
    "owner_session_required",
    "live_auto_locked",
]

MUST_NOT_CLAIM = [
    "PRODUCTION_READY",
    "LIVE_READY",
    "BROKER_READY",
    "AUTO_EXECUTION_READY",
    "REAL_CAPITAL_READY",
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
def _gp045():
    return build_staging_readiness_claim_release_gate_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_staging_ready_claim_release_record():
    gp045 = _gp045()
    status = gp045["status"]
    return {
        "source_dependency": "GP045",
        "gp045_release_gate_ready": gp045["staging_readiness_claim_release_ready"] is True,
        "gp045_recommendation": gp045["recommendation"],
        "gp045_gate_state": gp045["gate_state"],
        "hosted_runtime_verified": status["hosted_runtime_verified"] is True,
        "hosted_live_route_verified": status["hosted_live_route_verified"] is True,
        "return_session_continuity_verified": status["return_session_continuity_verified"] is True,
        "hosted_safety_locks_verified": status["hosted_safety_locks_verified"] is True,
        "staging_ready_claim_released": True,
        "staging_ready": True,
        "staging_readiness_granted": True,
        "production_deploy_enabled": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "live_auto_locked": True,
        "safety_statement": (
            "STAGING_READY is released for managed staging only. This does not authorize "
            "production, broker submission, real capital movement, execution, permissions, "
            "secret reveal, or Live Auto."
        ),
    }


def build_staging_ready_claim_release_status():
    record = build_staging_ready_claim_release_record()
    return {
        "gp045_release_gate_ready": record["gp045_release_gate_ready"] is True,
        "hosted_runtime_verified": record["hosted_runtime_verified"] is True,
        "hosted_live_route_verified": record["hosted_live_route_verified"] is True,
        "return_session_continuity_verified": record["return_session_continuity_verified"] is True,
        "hosted_safety_locks_verified": record["hosted_safety_locks_verified"] is True,
        "staging_ready_claim_released": True,
        "staging_ready": True,
        "staging_readiness_granted": True,
        "production_deploy_enabled": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_execution_enabled": False,
        "automated_execution_enabled": False,
        "permission_mutation_enabled": False,
        "secret_reveal_enabled": False,
        "live_auto_unlocked": False,
        "anonymous_access_allowed": False,
        "owner_session_required": True,
        "live_auto_locked": True,
    }


def build_staging_ready_claim_release_bundle():
    record = build_staging_ready_claim_release_record()
    status = build_staging_ready_claim_release_status()
    adapter = _adapter()
    released = (
        status["gp045_release_gate_ready"] is True
        and status["hosted_runtime_verified"] is True
        and status["hosted_live_route_verified"] is True
        and status["return_session_continuity_verified"] is True
        and status["hosted_safety_locks_verified"] is True
        and status["staging_ready_claim_released"] is True
        and status["staging_ready"] is True
        and status["staging_readiness_granted"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" not in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "staging_ready_claim_released": released,
        "source_dependency": "GP045",
        "recommendation": "GO_FOR_STAGING_READY_EVIDENCE_SEAL",
        "gate_state": "staging_ready_claim_released_for_managed_staging_only",
        "release_record": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "staging_ready_claim_released": True,
            "staging_ready": True,
            "staging_readiness_granted": True,
            "live_auto_locked": True,
        },
        "next_build": "Staging Ready Evidence Seal / GP047",
    }


def build_staging_ready_claim_release_handoff():
    bundle = build_staging_ready_claim_release_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "staging_ready_claim_released": bundle["staging_ready_claim_released"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "release_record": bundle["release_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "STAGING_READY is released for managed staging only.",
            "Production deployment remains disabled.",
            "Broker submission remains locked.",
            "Real capital movement remains locked.",
            "Direct and automated execution remain disabled.",
            "Live Auto remains locked.",
            "Next build is GP047 Staging Ready Evidence Seal.",
        ],
    }
