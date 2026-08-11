from copy import deepcopy
from functools import lru_cache

from .tower_staging_acceptance_decision_gate import build_tower_staging_acceptance_decision_gate_bundle
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_tower_staging_acceptance_decision_receipt_gp054",
    "display_title": "Tower Staging Acceptance Decision Receipt",
    "decision": "TOWER_STAGING_ACCEPTANCE_DECISION_RECEIPT_RECORDED_WITH_SAFETY_LOCKS_HELD",
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
    "gp053_acceptance_decision_gate_ready",
    "staging_ready",
    "tower_acceptance_decision_recorded",
    "tower_staging_accepted",
    "acceptance_receipt_append_only",
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
def _gp053():
    return build_tower_staging_acceptance_decision_gate_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_tower_staging_acceptance_decision_receipt():
    gp053 = _gp053()
    return {
        "source_dependency": "GP053",
        "receipt_type": "tower_staging_acceptance_decision_receipt",
        "gp053_acceptance_decision_gate_ready": gp053["acceptance_decision_gate_ready"] is True,
        "decision_value": "ACCEPT_TOWER_OB_STAGING",
        "tower_acceptance_decision_recorded": True,
        "tower_staging_accepted": True,
        "staging_ready": gp053["status"]["staging_ready"] is True,
        "acceptance_receipt_append_only": True,
        "redaction_required": True,
        "secret_values_forbidden": True,
        "private_beta_access_opened": False,
        "tester_credentials_issued": False,
        "production_deploy_enabled": False,
        "safety_statement": (
            "Tower staging acceptance is recorded. This does not open private beta "
            "access, issue tester credentials, or enable production."
        ),
    }


def build_tower_staging_acceptance_decision_receipt_status():
    receipt = build_tower_staging_acceptance_decision_receipt()
    return {
        "gp053_acceptance_decision_gate_ready": receipt["gp053_acceptance_decision_gate_ready"] is True,
        "staging_ready": receipt["staging_ready"] is True,
        "tower_acceptance_decision_recorded": True,
        "tower_staging_accepted": True,
        "acceptance_receipt_append_only": True,
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


def build_tower_staging_acceptance_decision_receipt_bundle():
    receipt = build_tower_staging_acceptance_decision_receipt()
    status = build_tower_staging_acceptance_decision_receipt_status()
    adapter = _adapter()
    ready = (
        status["gp053_acceptance_decision_gate_ready"] is True
        and status["staging_ready"] is True
        and status["tower_acceptance_decision_recorded"] is True
        and status["tower_staging_accepted"] is True
        and status["acceptance_receipt_append_only"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "acceptance_decision_receipt_recorded": ready,
        "source_dependency": "GP053",
        "recommendation": "GO_FOR_TOWER_OB_BETA_LAUNCH_PREPARATION_CLOSEOUT",
        "gate_state": "tower_staging_acceptance_recorded",
        "acceptance_receipt": deepcopy(receipt),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "staging_ready": True,
            "tower_acceptance_decision_recorded": True,
            "tower_staging_accepted": True,
            "acceptance_receipt_append_only": True,
            "live_auto_locked": True,
        },
        "next_build": "Tower OB Beta Launch Preparation Closeout / GP055",
    }


def build_tower_staging_acceptance_decision_receipt_handoff():
    bundle = build_tower_staging_acceptance_decision_receipt_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "acceptance_decision_receipt_recorded": bundle["acceptance_decision_receipt_recorded"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "acceptance_receipt": bundle["acceptance_receipt"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Tower staging acceptance decision receipt is recorded.",
            "Tower staging is accepted.",
            "Private beta access is not opened.",
            "Tester credentials are not issued.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP055 Tower OB Beta Launch Preparation Closeout.",
        ],
    }
