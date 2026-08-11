from copy import deepcopy
from functools import lru_cache

from .tower_ob_staging_acceptance_handoff import build_tower_ob_staging_acceptance_handoff_bundle
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_tower_ob_staging_acceptance_review_packet_gp052",
    "display_title": "Tower OB Staging Acceptance Review Packet",
    "decision": "TOWER_OB_STAGING_ACCEPTANCE_REVIEW_PACKET_READY_WITH_SAFETY_LOCKS_HELD",
}

REVIEW_ITEMS = [
    "STAGING_READY claim released by GP046",
    "STAGING_READY evidence sealed by GP047",
    "Owner beta readiness prepared by GP048",
    "Private beta access hold preserved by GP049",
    "OB owner experience staging closeout sealed by GP050",
    "Tower acceptance handoff prepared by GP051",
]

FALSE_FLAGS = [
    "tower_acceptance_decision_recorded",
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
    "gp051_handoff_ready",
    "staging_ready",
    "acceptance_review_packet_ready",
    "review_items_present",
    "tower_acceptance_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "Tower acceptance decision recording",
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
def _gp051():
    return build_tower_ob_staging_acceptance_handoff_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_tower_ob_staging_acceptance_review_packet():
    gp051 = _gp051()
    return {
        "source_dependency": "GP051",
        "review_type": "tower_ob_staging_acceptance_review_packet",
        "gp051_handoff_ready": gp051["staging_acceptance_handoff_ready"] is True,
        "staging_ready": gp051["status"]["staging_ready"] is True,
        "acceptance_review_packet_ready": True,
        "review_items": list(REVIEW_ITEMS),
        "review_items_present": len(REVIEW_ITEMS) == 6,
        "tower_acceptance_required": True,
        "tower_acceptance_decision_recorded": False,
        "private_beta_access_opened": False,
        "tester_credentials_issued": False,
        "production_deploy_enabled": False,
    }


def build_tower_ob_staging_acceptance_review_status():
    packet = build_tower_ob_staging_acceptance_review_packet()
    return {
        "gp051_handoff_ready": packet["gp051_handoff_ready"] is True,
        "staging_ready": packet["staging_ready"] is True,
        "acceptance_review_packet_ready": packet["acceptance_review_packet_ready"] is True,
        "review_items_present": packet["review_items_present"] is True,
        "tower_acceptance_required": True,
        "tower_acceptance_decision_recorded": False,
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


def build_tower_ob_staging_acceptance_review_packet_bundle():
    packet = build_tower_ob_staging_acceptance_review_packet()
    status = build_tower_ob_staging_acceptance_review_status()
    adapter = _adapter()
    ready = (
        status["gp051_handoff_ready"] is True
        and status["staging_ready"] is True
        and status["acceptance_review_packet_ready"] is True
        and status["review_items_present"] is True
        and status["tower_acceptance_required"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "acceptance_review_packet_ready": ready,
        "source_dependency": "GP051",
        "recommendation": "GO_FOR_TOWER_STAGING_ACCEPTANCE_DECISION_GATE",
        "gate_state": "ready_for_tower_staging_acceptance_decision_gate",
        "review_packet": deepcopy(packet),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "staging_ready": True,
            "acceptance_review_packet_ready": True,
            "live_auto_locked": True,
        },
        "next_build": "Tower Staging Acceptance Decision Gate / GP053",
    }


def build_tower_ob_staging_acceptance_review_packet_handoff():
    bundle = build_tower_ob_staging_acceptance_review_packet_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "acceptance_review_packet_ready": bundle["acceptance_review_packet_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "review_packet": bundle["review_packet"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Tower OB staging acceptance review packet is ready.",
            "Tower acceptance decision is not recorded in this package.",
            "Private beta access is not opened.",
            "Tester credentials are not issued.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP053 Tower Staging Acceptance Decision Gate.",
        ],
    }
