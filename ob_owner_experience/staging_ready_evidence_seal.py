from copy import deepcopy
from functools import lru_cache

from .staging_ready_claim_release import build_staging_ready_claim_release_bundle
from .ui_surface_registry import PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_staging_ready_evidence_seal_gp047",
    "display_title": "Staging Ready Evidence Seal",
    "decision": "STAGING_READY_EVIDENCE_SEALED_WITH_SAFETY_LOCKS_HELD",
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
    "gp046_staging_ready_claim_released",
    "staging_ready",
    "staging_readiness_granted",
    "staging_ready_evidence_sealed",
    "evidence_append_only",
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
def _gp046():
    return build_staging_ready_claim_release_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_staging_ready_evidence_seal_record():
    gp046 = _gp046()
    return {
        "source_dependency": "GP046",
        "gp046_staging_ready_claim_released": gp046["staging_ready_claim_released"] is True,
        "staging_ready": gp046["status"]["staging_ready"] is True,
        "staging_readiness_granted": gp046["status"]["staging_readiness_granted"] is True,
        "staging_ready_evidence_sealed": True,
        "evidence_append_only": True,
        "sealed_evidence_inputs": [
            "GP041 hosted runtime verification execution",
            "GP042 Tower OB hosted route verification",
            "GP043 hosted return session continuity verification",
            "GP044 hosted safety lock verification",
            "GP045 staging readiness claim release gate",
            "GP046 staging ready claim release",
        ],
        "production_deploy_enabled": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "live_auto_locked": True,
    }


def build_staging_ready_evidence_seal_status():
    record = build_staging_ready_evidence_seal_record()
    return {
        "gp046_staging_ready_claim_released": record["gp046_staging_ready_claim_released"] is True,
        "staging_ready": record["staging_ready"] is True,
        "staging_readiness_granted": record["staging_readiness_granted"] is True,
        "staging_ready_evidence_sealed": True,
        "evidence_append_only": True,
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


def build_staging_ready_evidence_seal_bundle():
    record = build_staging_ready_evidence_seal_record()
    status = build_staging_ready_evidence_seal_status()
    adapter = _adapter()
    sealed = (
        status["gp046_staging_ready_claim_released"] is True
        and status["staging_ready"] is True
        and status["staging_readiness_granted"] is True
        and status["staging_ready_evidence_sealed"] is True
        and status["evidence_append_only"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "staging_ready_evidence_sealed": sealed,
        "source_dependency": "GP046",
        "recommendation": "GO_FOR_OWNER_BETA_READINESS_GATE",
        "gate_state": "staging_ready_evidence_sealed",
        "seal_record": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "staging_ready": True,
            "staging_readiness_granted": True,
            "staging_ready_evidence_sealed": True,
            "live_auto_locked": True,
        },
        "next_build": "Owner Beta Readiness Gate / GP048",
    }


def build_staging_ready_evidence_seal_handoff():
    bundle = build_staging_ready_evidence_seal_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "staging_ready_evidence_sealed": bundle["staging_ready_evidence_sealed"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "seal_record": bundle["seal_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Staging ready evidence is sealed.",
            "Staging ready remains managed-staging only.",
            "Production deployment remains disabled.",
            "Broker submission remains locked.",
            "Real capital movement remains locked.",
            "Live Auto remains locked.",
            "Next build is GP048 Owner Beta Readiness Gate.",
        ],
    }
