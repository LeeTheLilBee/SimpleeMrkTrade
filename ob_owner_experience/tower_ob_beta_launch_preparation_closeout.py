from copy import deepcopy
from functools import lru_cache

from .tower_staging_acceptance_decision_receipt import build_tower_staging_acceptance_decision_receipt_bundle
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_tower_ob_beta_launch_preparation_closeout_gp055",
    "display_title": "Tower OB Beta Launch Preparation Closeout",
    "decision": "TOWER_OB_BETA_LAUNCH_PREPARATION_CLOSEOUT_SEALED_WITH_SAFETY_LOCKS_HELD",
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
    "gp054_acceptance_decision_receipt_recorded",
    "tower_staging_accepted",
    "staging_ready",
    "beta_launch_preparation_closeout_ready",
    "private_beta_access_authorization_required_next",
    "tester_credential_gate_required_next",
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
def _gp054():
    return build_tower_staging_acceptance_decision_receipt_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_tower_ob_beta_launch_preparation_closeout_record():
    gp054 = _gp054()
    return {
        "source_dependency": "GP054",
        "closeout_type": "tower_ob_beta_launch_preparation_closeout",
        "gp054_acceptance_decision_receipt_recorded": gp054["acceptance_decision_receipt_recorded"] is True,
        "tower_staging_accepted": gp054["status"]["tower_staging_accepted"] is True,
        "staging_ready": gp054["status"]["staging_ready"] is True,
        "beta_launch_preparation_closeout_ready": True,
        "private_beta_access_authorization_required_next": True,
        "tester_credential_gate_required_next": True,
        "private_beta_access_opened": False,
        "tester_credentials_issued": False,
        "production_deploy_enabled": False,
        "closed_items": [
            "Tower OB staging acceptance handoff prepared",
            "Tower OB staging review packet prepared",
            "Tower staging acceptance decision gate prepared",
            "Tower staging acceptance decision receipt recorded",
            "Beta launch preparation closeout sealed",
        ],
        "safety_statement": (
            "Tower OB staging acceptance is complete and beta launch preparation is "
            "closed. Private beta access and tester credentials require later gates."
        ),
    }


def build_tower_ob_beta_launch_preparation_closeout_status():
    record = build_tower_ob_beta_launch_preparation_closeout_record()
    return {
        "gp054_acceptance_decision_receipt_recorded": record["gp054_acceptance_decision_receipt_recorded"] is True,
        "tower_staging_accepted": record["tower_staging_accepted"] is True,
        "staging_ready": record["staging_ready"] is True,
        "beta_launch_preparation_closeout_ready": True,
        "private_beta_access_authorization_required_next": True,
        "tester_credential_gate_required_next": True,
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


def build_tower_ob_beta_launch_preparation_closeout_bundle():
    record = build_tower_ob_beta_launch_preparation_closeout_record()
    status = build_tower_ob_beta_launch_preparation_closeout_status()
    adapter = _adapter()
    ready = (
        status["gp054_acceptance_decision_receipt_recorded"] is True
        and status["tower_staging_accepted"] is True
        and status["staging_ready"] is True
        and status["beta_launch_preparation_closeout_ready"] is True
        and status["private_beta_access_authorization_required_next"] is True
        and status["tester_credential_gate_required_next"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "beta_launch_preparation_closeout_ready": ready,
        "source_dependency": "GP054",
        "recommendation": "GO_FOR_PRIVATE_BETA_ACCESS_AUTHORIZATION",
        "gate_state": "tower_ob_beta_launch_preparation_closeout_sealed",
        "closeout_record": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "staging_ready": True,
            "tower_staging_accepted": True,
            "beta_launch_preparation_closeout_ready": True,
            "private_beta_access_authorization_required_next": True,
            "tester_credential_gate_required_next": True,
            "live_auto_locked": True,
        },
        "next_build": "Private Beta Access Authorization / GP056",
    }


def build_tower_ob_beta_launch_preparation_closeout_handoff():
    bundle = build_tower_ob_beta_launch_preparation_closeout_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "beta_launch_preparation_closeout_ready": bundle["beta_launch_preparation_closeout_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "closeout_record": bundle["closeout_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Tower OB beta launch preparation closeout is sealed.",
            "STAGING_READY remains true.",
            "Tower staging is accepted.",
            "Private beta access is still not opened.",
            "Tester credentials are still not issued.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP056 Private Beta Access Authorization.",
        ],
    }
