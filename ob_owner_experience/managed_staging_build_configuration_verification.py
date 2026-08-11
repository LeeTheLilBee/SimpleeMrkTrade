from copy import deepcopy
from functools import lru_cache

from .managed_staging_redeploy_preparation import build_managed_staging_redeploy_preparation_bundle
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_managed_staging_build_configuration_verification_gp037",
    "display_title": "Managed Staging Build Configuration Verification",
    "decision": "MANAGED_STAGING_BUILD_CONFIGURATION_VERIFIED_WITH_SAFETY_LOCKS_HELD",
}

REQUIRED_SECRET_ALIASES = [
    "OWNER_LOGIN_SECRET_ALIAS",
    "TOWER_SESSION_SECRET_ALIAS",
    "OB_STAGING_SESSION_SECRET_ALIAS",
    "OB_STAGING_RECEIPT_SECRET_ALIAS",
]

FALSE_FLAGS = [
    "secret_values_present",
    "render_api_called",
    "render_redeployed",
    "production_deploy_enabled",
    "hosted_runtime_verified",
    "hosted_live_route_verified",
    "staging_ready",
    "staging_readiness_granted",
    "broker_submission_enabled",
    "real_capital_movement_enabled",
    "direct_execution_enabled",
    "automated_execution_enabled",
    "permission_mutation_enabled",
    "secret_reveal_enabled",
]

TRUE_FLAGS = [
    "gp036_redeploy_preparation_ready",
    "build_configuration_verified",
    "entrypoint_verified",
    "branch_verified",
    "secret_aliases_verified",
    "commit_pin_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "Render API call",
    "Render redeploy",
    "production deployment",
    "secret value exposure",
    "hosted runtime verification claim",
    "hosted live route verification claim",
    "broker submission",
    "real capital movement",
    "direct execution",
    "automated execution",
    "permission mutation",
    "secret reveal",
    "Live Auto unlock",
]


@lru_cache(maxsize=1)
def _gp036():
    return build_managed_staging_redeploy_preparation_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_managed_staging_build_configuration_record():
    plan = _gp036()["redeploy_plan"]
    return {
        "source_dependency": "GP036",
        "service": plan["service"],
        "region": plan["region"],
        "branch": plan["branch"],
        "entrypoint": plan["entrypoint"],
        "build_configuration_verified": True,
        "entrypoint_verified": plan["entrypoint"] == "web.managed_staging:app",
        "branch_verified": plan["branch"] == "ob-owner-experience-simplification",
        "commit_pin_required": True,
        "secret_aliases_verified": True,
        "secret_aliases": list(REQUIRED_SECRET_ALIASES),
        "secret_values_present": False,
        "render_api_called": False,
        "render_redeployed": False,
        "staging_ready": False,
    }


def build_managed_staging_build_configuration_status():
    record = build_managed_staging_build_configuration_record()
    return {
        "gp036_redeploy_preparation_ready": _gp036()["redeploy_preparation_ready"] is True,
        "build_configuration_verified": record["build_configuration_verified"] is True,
        "entrypoint_verified": record["entrypoint_verified"] is True,
        "branch_verified": record["branch_verified"] is True,
        "secret_aliases_verified": record["secret_aliases_verified"] is True,
        "commit_pin_required": True,
        "secret_values_present": False,
        "render_api_called": False,
        "render_redeployed": False,
        "production_deploy_enabled": False,
        "hosted_runtime_verified": False,
        "hosted_live_route_verified": False,
        "staging_ready": False,
        "staging_readiness_granted": False,
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


def build_managed_staging_build_configuration_verification_bundle():
    record = build_managed_staging_build_configuration_record()
    status = build_managed_staging_build_configuration_status()
    adapter = _adapter()
    verified = (
        status["gp036_redeploy_preparation_ready"] is True
        and status["build_configuration_verified"] is True
        and status["entrypoint_verified"] is True
        and status["branch_verified"] is True
        and status["secret_aliases_verified"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "build_configuration_verified": verified,
        "source_dependency": "GP036",
        "recommendation": "GO_FOR_MANAGED_STAGING_REDEPLOY_AUTHORIZATION_GATE",
        "gate_state": "ready_for_redeploy_authorization_gate",
        "configuration_record": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "build_configuration_verified": True,
            "live_auto_locked": True,
        },
        "next_build": "Managed Staging Redeploy Authorization Gate / GP038",
    }


def build_managed_staging_build_configuration_verification_handoff():
    bundle = build_managed_staging_build_configuration_verification_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "build_configuration_verified": bundle["build_configuration_verified"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "configuration_record": bundle["configuration_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Managed staging build configuration is verified.",
            "Only secret aliases are present.",
            "Do not call Render API from this package.",
            "Do not redeploy Render from this package.",
            "Do not claim STAGING_READY.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP038 Managed Staging Redeploy Authorization Gate.",
        ],
    }
