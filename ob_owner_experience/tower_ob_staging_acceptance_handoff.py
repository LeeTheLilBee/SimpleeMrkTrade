from copy import deepcopy
from functools import lru_cache

from .ob_owner_experience_staging_closeout import build_ob_owner_experience_staging_closeout_bundle
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_tower_ob_staging_acceptance_handoff_gp051",
    "display_title": "Tower OB Staging Acceptance Handoff",
    "decision": "TOWER_OB_STAGING_ACCEPTANCE_HANDOFF_READY_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "private_beta_access_opened",
    "tester_credentials_issued",
    "production_deploy_enabled",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
]

TRUE_FLAGS = [
    "gp050_staging_closeout_ready",
    "staging_ready",
    "staging_acceptance_handoff_ready",
    "tower_acceptance_required",
    "evidence_packet_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "private beta access opening",
    "tester credential issuance",
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
def _gp050():
    return build_ob_owner_experience_staging_closeout_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def _flag(bundle, key):
    if key in bundle:
        return bundle[key]
    if "status" in bundle and key in bundle["status"]:
        return bundle["status"][key]
    if "release_boundary" in bundle and key in bundle["release_boundary"]:
        return bundle["release_boundary"][key]
    if "closeout_record" in bundle and key in bundle["closeout_record"]:
        return bundle["closeout_record"][key]
    return None


def build_tower_ob_staging_acceptance_handoff_packet():
    gp050 = _gp050()
    return {
        "source_dependency": "GP050",
        "handoff_type": "tower_ob_staging_acceptance_handoff",
        "gp050_staging_closeout_ready": _flag(gp050, "staging_closeout_ready") is True or _flag(gp050, "closeout_ready") is True or _flag(gp050, "ob_owner_experience_staging_closeout_ready") is True,
        "staging_ready": _flag(gp050, "staging_ready") is True,
        "staging_ready_claim_released": _flag(gp050, "staging_ready_claim_released") is True,
        "staging_ready_evidence_sealed": _flag(gp050, "staging_ready_evidence_sealed") is True,
        "owner_beta_readiness_ready": _flag(gp050, "owner_beta_readiness_ready") is True,
        "private_beta_access_hold_ready": _flag(gp050, "private_beta_access_hold_ready") is True,
        "tower_acceptance_required": True,
        "evidence_packet_required": True,
        "staging_acceptance_handoff_ready": True,
        "handoff_evidence_refs": [
            "GP046 Staging Ready Claim Release",
            "GP047 Staging Ready Evidence Seal",
            "GP048 Owner Beta Readiness Gate",
            "GP049 Private Beta Access Hold Boundary",
            "GP050 OB Owner Experience Staging Closeout",
        ],
        "private_beta_access_opened": False,
        "tester_credentials_issued": False,
        "production_deploy_enabled": False,
    }


def build_tower_ob_staging_acceptance_handoff_status():
    packet = build_tower_ob_staging_acceptance_handoff_packet()
    return {
        "gp050_staging_closeout_ready": packet["gp050_staging_closeout_ready"] is True,
        "staging_ready": packet["staging_ready"] is True,
        "staging_acceptance_handoff_ready": packet["staging_acceptance_handoff_ready"] is True,
        "tower_acceptance_required": True,
        "evidence_packet_required": True,
        "private_beta_access_opened": False,
        "tester_credentials_issued": False,
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


def build_tower_ob_staging_acceptance_handoff_bundle():
    packet = build_tower_ob_staging_acceptance_handoff_packet()
    status = build_tower_ob_staging_acceptance_handoff_status()
    adapter = _adapter()
    ready = (
        status["gp050_staging_closeout_ready"] is True
        and status["staging_ready"] is True
        and status["staging_acceptance_handoff_ready"] is True
        and status["tower_acceptance_required"] is True
        and status["evidence_packet_required"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "staging_acceptance_handoff_ready": ready,
        "source_dependency": "GP050",
        "recommendation": "GO_FOR_TOWER_OB_STAGING_ACCEPTANCE_REVIEW_PACKET",
        "gate_state": "ready_for_tower_acceptance_review_packet",
        "handoff_packet": deepcopy(packet),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "staging_ready": True,
            "staging_acceptance_handoff_ready": True,
            "live_auto_locked": True,
        },
        "next_build": "Tower OB Staging Acceptance Review Packet / GP052",
    }


def build_tower_ob_staging_acceptance_handoff_handoff():
    bundle = build_tower_ob_staging_acceptance_handoff_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "staging_acceptance_handoff_ready": bundle["staging_acceptance_handoff_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "handoff_packet": bundle["handoff_packet"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Tower OB staging acceptance handoff is ready.",
            "STAGING_READY remains true from GP050 evidence.",
            "Private beta access is not opened.",
            "Tester credentials are not issued.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP052 Tower OB Staging Acceptance Review Packet.",
        ],
    }
