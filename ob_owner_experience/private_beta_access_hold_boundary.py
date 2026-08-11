from copy import deepcopy
from functools import lru_cache

from .owner_beta_readiness_gate import build_owner_beta_readiness_gate_bundle
from .ui_surface_registry import PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_private_beta_access_hold_boundary_gp049",
    "display_title": "Private Beta Access Hold Boundary",
    "decision": "PRIVATE_BETA_ACCESS_HOLD_BOUNDARY_READY_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "private_beta_access_opened",
    "public_beta_open",
    "tester_credentials_issued",
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
    "gp048_owner_beta_readiness_ready",
    "staging_ready",
    "private_beta_access_hold_ready",
    "owner_approval_required_to_open_beta",
    "tester_survey_paper_only_boundary_ready",
    "manual_live_owner_only",
    "owner_session_required",
    "live_auto_locked",
]

MUST_NOT_CLAIM = [
    "PUBLIC_BETA_OPEN",
    "TESTER_ACCESS_OPEN",
    "PRODUCTION_READY",
    "BROKER_READY",
    "AUTO_EXECUTION_READY",
    "REAL_CAPITAL_READY",
]

NOT_AUTHORIZED = [
    "public beta open",
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
def _gp048():
    return build_owner_beta_readiness_gate_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_private_beta_access_hold_record():
    gp048 = _gp048()
    return {
        "source_dependency": "GP048",
        "gp048_owner_beta_readiness_ready": gp048["owner_beta_readiness_ready"] is True,
        "staging_ready": gp048["status"]["staging_ready"] is True,
        "private_beta_access_hold_ready": True,
        "owner_approval_required_to_open_beta": True,
        "tester_survey_paper_only_boundary_ready": True,
        "manual_live_owner_only": True,
        "private_beta_access_opened": False,
        "public_beta_open": False,
        "tester_credentials_issued": False,
        "production_deploy_enabled": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "live_auto_locked": True,
    }


def build_private_beta_access_hold_status():
    record = build_private_beta_access_hold_record()
    return {
        "gp048_owner_beta_readiness_ready": record["gp048_owner_beta_readiness_ready"] is True,
        "staging_ready": record["staging_ready"] is True,
        "private_beta_access_hold_ready": True,
        "owner_approval_required_to_open_beta": True,
        "tester_survey_paper_only_boundary_ready": True,
        "manual_live_owner_only": True,
        "private_beta_access_opened": False,
        "public_beta_open": False,
        "tester_credentials_issued": False,
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


def build_private_beta_access_hold_boundary_bundle():
    record = build_private_beta_access_hold_record()
    status = build_private_beta_access_hold_status()
    adapter = _adapter()
    ready = (
        status["gp048_owner_beta_readiness_ready"] is True
        and status["staging_ready"] is True
        and status["private_beta_access_hold_ready"] is True
        and status["owner_approval_required_to_open_beta"] is True
        and status["tester_survey_paper_only_boundary_ready"] is True
        and status["manual_live_owner_only"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "private_beta_access_hold_ready": ready,
        "source_dependency": "GP048",
        "recommendation": "GO_FOR_OB_OWNER_EXPERIENCE_STAGING_CLOSEOUT",
        "gate_state": "private_beta_ready_but_access_held_for_owner_approval",
        "access_hold_record": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "staging_ready": True,
            "private_beta_access_hold_ready": True,
            "owner_approval_required_to_open_beta": True,
            "tester_survey_paper_only_boundary_ready": True,
            "manual_live_owner_only": True,
            "live_auto_locked": True,
        },
        "next_build": "OB Owner Experience Staging Closeout / GP050",
    }


def build_private_beta_access_hold_boundary_handoff():
    bundle = build_private_beta_access_hold_boundary_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "private_beta_access_hold_ready": bundle["private_beta_access_hold_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "access_hold_record": bundle["access_hold_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Private beta access hold boundary is ready.",
            "Tester access is not open.",
            "Tester credentials are not issued.",
            "Owner approval is required before beta access opens.",
            "Manual Live remains owner-only.",
            "Live Auto remains locked.",
            "Next build is GP050 OB Owner Experience Staging Closeout.",
        ],
    }
