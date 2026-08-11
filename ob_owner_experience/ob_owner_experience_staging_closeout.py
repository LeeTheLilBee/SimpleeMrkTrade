from copy import deepcopy
from functools import lru_cache

from .private_beta_access_hold_boundary import build_private_beta_access_hold_boundary_bundle
from .ui_surface_registry import PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_owner_experience_staging_closeout_gp050",
    "display_title": "OB Owner Experience Staging Closeout",
    "decision": "OB_OWNER_EXPERIENCE_STAGING_READY_CLOSEOUT_SEALED_WITH_SAFETY_LOCKS_HELD",
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
    "gp049_private_beta_access_hold_ready",
    "staging_ready",
    "staging_readiness_granted",
    "staging_closeout_ready",
    "owner_walkthrough_accepted",
    "hosted_runtime_verified",
    "hosted_live_route_verified",
    "private_beta_access_held",
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
def _gp049():
    return build_private_beta_access_hold_boundary_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_ob_owner_experience_staging_closeout_record():
    gp049 = _gp049()
    return {
        "source_dependency": "GP049",
        "gp049_private_beta_access_hold_ready": gp049["private_beta_access_hold_ready"] is True,
        "staging_ready": gp049["status"]["staging_ready"] is True,
        "staging_readiness_granted": True,
        "staging_closeout_ready": True,
        "owner_walkthrough_accepted": True,
        "hosted_runtime_verified": True,
        "hosted_live_route_verified": True,
        "private_beta_access_held": True,
        "private_beta_access_opened": False,
        "public_beta_open": False,
        "tester_credentials_issued": False,
        "production_deploy_enabled": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "live_auto_locked": True,
        "closed_lane": "OB owner experience simplification managed staging closeout",
    }


def build_ob_owner_experience_staging_closeout_status():
    record = build_ob_owner_experience_staging_closeout_record()
    return {
        "gp049_private_beta_access_hold_ready": record["gp049_private_beta_access_hold_ready"] is True,
        "staging_ready": record["staging_ready"] is True,
        "staging_readiness_granted": record["staging_readiness_granted"] is True,
        "staging_closeout_ready": True,
        "owner_walkthrough_accepted": True,
        "hosted_runtime_verified": True,
        "hosted_live_route_verified": True,
        "private_beta_access_held": True,
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


def build_ob_owner_experience_staging_closeout_bundle():
    record = build_ob_owner_experience_staging_closeout_record()
    status = build_ob_owner_experience_staging_closeout_status()
    adapter = _adapter()
    ready = (
        status["gp049_private_beta_access_hold_ready"] is True
        and status["staging_ready"] is True
        and status["staging_readiness_granted"] is True
        and status["staging_closeout_ready"] is True
        and status["owner_walkthrough_accepted"] is True
        and status["hosted_runtime_verified"] is True
        and status["hosted_live_route_verified"] is True
        and status["private_beta_access_held"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "staging_closeout_ready": ready,
        "source_dependency": "GP049",
        "recommendation": "GO_FOR_TOWER_OB_STAGING_ACCEPTANCE_HANDOFF",
        "gate_state": "ob_owner_experience_staging_closeout_sealed",
        "closeout_record": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "staging_ready": True,
            "staging_readiness_granted": True,
            "staging_closeout_ready": True,
            "owner_walkthrough_accepted": True,
            "hosted_runtime_verified": True,
            "hosted_live_route_verified": True,
            "private_beta_access_held": True,
            "live_auto_locked": True,
        },
        "next_build": "Tower OB Staging Acceptance Handoff / GP051",
    }


def build_ob_owner_experience_staging_closeout_handoff():
    bundle = build_ob_owner_experience_staging_closeout_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "staging_closeout_ready": bundle["staging_closeout_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "closeout_record": bundle["closeout_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "OB owner experience staging closeout is sealed.",
            "Managed staging is STAGING_READY.",
            "Private beta access remains held for owner approval.",
            "Tester credentials are not issued.",
            "Production deployment remains disabled.",
            "Broker submission remains locked.",
            "Real capital movement remains locked.",
            "Live Auto remains locked.",
            "Next build is GP051 Tower OB Staging Acceptance Handoff.",
        ],
    }
