from copy import deepcopy
from functools import lru_cache

from .staging_ready_evidence_seal import build_staging_ready_evidence_seal_bundle
from .ui_surface_registry import PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_owner_beta_readiness_gate_gp048",
    "display_title": "Owner Beta Readiness Gate",
    "decision": "OWNER_BETA_READINESS_READY_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "private_beta_access_opened",
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
    "gp047_staging_ready_evidence_sealed",
    "staging_ready",
    "owner_beta_readiness_ready",
    "survey_mode_allowed",
    "paper_mode_allowed",
    "manual_live_owner_only",
    "owner_session_required",
    "live_auto_locked",
]

MUST_NOT_CLAIM = [
    "PUBLIC_BETA_OPEN",
    "PRODUCTION_READY",
    "BROKER_READY",
    "AUTO_EXECUTION_READY",
    "REAL_CAPITAL_READY",
]

NOT_AUTHORIZED = [
    "public beta open",
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
def _gp047():
    return build_staging_ready_evidence_seal_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_owner_beta_readiness_record():
    gp047 = _gp047()
    return {
        "source_dependency": "GP047",
        "gp047_staging_ready_evidence_sealed": gp047["staging_ready_evidence_sealed"] is True,
        "staging_ready": gp047["status"]["staging_ready"] is True,
        "owner_beta_readiness_ready": True,
        "beta_scope": "owner_private_beta_readiness",
        "survey_mode_allowed": True,
        "paper_mode_allowed": True,
        "manual_live_owner_only": True,
        "private_beta_access_opened": False,
        "public_beta_open": False,
        "production_deploy_enabled": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "live_auto_locked": True,
    }


def build_owner_beta_readiness_status():
    record = build_owner_beta_readiness_record()
    return {
        "gp047_staging_ready_evidence_sealed": record["gp047_staging_ready_evidence_sealed"] is True,
        "staging_ready": record["staging_ready"] is True,
        "owner_beta_readiness_ready": True,
        "survey_mode_allowed": True,
        "paper_mode_allowed": True,
        "manual_live_owner_only": True,
        "private_beta_access_opened": False,
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


def build_owner_beta_readiness_gate_bundle():
    record = build_owner_beta_readiness_record()
    status = build_owner_beta_readiness_status()
    adapter = _adapter()
    ready = (
        status["gp047_staging_ready_evidence_sealed"] is True
        and status["staging_ready"] is True
        and status["owner_beta_readiness_ready"] is True
        and status["survey_mode_allowed"] is True
        and status["paper_mode_allowed"] is True
        and status["manual_live_owner_only"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "owner_beta_readiness_ready": ready,
        "source_dependency": "GP047",
        "recommendation": "GO_FOR_PRIVATE_BETA_ACCESS_HOLD_BOUNDARY",
        "gate_state": "owner_beta_ready_access_still_closed",
        "beta_readiness_record": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "staging_ready": True,
            "owner_beta_readiness_ready": True,
            "survey_mode_allowed": True,
            "paper_mode_allowed": True,
            "manual_live_owner_only": True,
            "live_auto_locked": True,
        },
        "next_build": "Private Beta Access Hold Boundary / GP049",
    }


def build_owner_beta_readiness_gate_handoff():
    bundle = build_owner_beta_readiness_gate_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "owner_beta_readiness_ready": bundle["owner_beta_readiness_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "beta_readiness_record": bundle["beta_readiness_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Owner beta readiness is ready.",
            "Private beta access is still closed.",
            "Survey and Paper modes are allowed.",
            "Manual Live remains owner-only.",
            "Broker submission remains locked.",
            "Real capital movement remains locked.",
            "Live Auto remains locked.",
            "Next build is GP049 Private Beta Access Hold Boundary.",
        ],
    }
