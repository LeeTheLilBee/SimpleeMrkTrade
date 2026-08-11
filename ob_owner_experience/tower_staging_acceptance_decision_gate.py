from copy import deepcopy
from functools import lru_cache

from .tower_ob_staging_acceptance_review_packet import build_tower_ob_staging_acceptance_review_packet_bundle
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_tower_staging_acceptance_decision_gate_gp053",
    "display_title": "Tower Staging Acceptance Decision Gate",
    "decision": "TOWER_STAGING_ACCEPTANCE_DECISION_GATE_READY_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "tower_acceptance_decision_recorded",
    "tower_staging_accepted",
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
    "gp052_review_packet_ready",
    "staging_ready",
    "acceptance_decision_gate_ready",
    "acceptance_decision_record_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "Tower staging acceptance recording",
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
def _gp052():
    return build_tower_ob_staging_acceptance_review_packet_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_tower_staging_acceptance_decision_gate_record():
    gp052 = _gp052()
    return {
        "source_dependency": "GP052",
        "gate_type": "tower_staging_acceptance_decision_gate",
        "gp052_review_packet_ready": gp052["acceptance_review_packet_ready"] is True,
        "staging_ready": gp052["status"]["staging_ready"] is True,
        "acceptance_decision_gate_ready": True,
        "acceptance_decision_record_required": True,
        "allowed_decisions": [
            "ACCEPT_TOWER_OB_STAGING",
            "HOLD_TOWER_OB_STAGING",
            "REQUEST_MORE_EVIDENCE",
        ],
        "default_decision": "HOLD_TOWER_OB_STAGING",
        "tower_acceptance_decision_recorded": False,
        "tower_staging_accepted": False,
        "private_beta_access_opened": False,
        "tester_credentials_issued": False,
        "production_deploy_enabled": False,
    }


def build_tower_staging_acceptance_decision_gate_status():
    record = build_tower_staging_acceptance_decision_gate_record()
    return {
        "gp052_review_packet_ready": record["gp052_review_packet_ready"] is True,
        "staging_ready": record["staging_ready"] is True,
        "acceptance_decision_gate_ready": True,
        "acceptance_decision_record_required": True,
        "tower_acceptance_decision_recorded": False,
        "tower_staging_accepted": False,
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


def build_tower_staging_acceptance_decision_gate_bundle():
    record = build_tower_staging_acceptance_decision_gate_record()
    status = build_tower_staging_acceptance_decision_gate_status()
    adapter = _adapter()
    ready = (
        status["gp052_review_packet_ready"] is True
        and status["staging_ready"] is True
        and status["acceptance_decision_gate_ready"] is True
        and status["acceptance_decision_record_required"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "acceptance_decision_gate_ready": ready,
        "source_dependency": "GP052",
        "recommendation": "GO_FOR_TOWER_STAGING_ACCEPTANCE_DECISION_RECEIPT",
        "gate_state": "ready_for_tower_staging_acceptance_decision_recording",
        "decision_gate": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "staging_ready": True,
            "acceptance_decision_gate_ready": True,
            "live_auto_locked": True,
        },
        "next_build": "Tower Staging Acceptance Decision Receipt / GP054",
    }


def build_tower_staging_acceptance_decision_gate_handoff():
    bundle = build_tower_staging_acceptance_decision_gate_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "acceptance_decision_gate_ready": bundle["acceptance_decision_gate_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "decision_gate": bundle["decision_gate"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Tower staging acceptance decision gate is ready.",
            "Tower staging acceptance is not recorded in this package.",
            "Private beta access is not opened.",
            "Tester credentials are not issued.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP054 Tower Staging Acceptance Decision Receipt.",
        ],
    }
