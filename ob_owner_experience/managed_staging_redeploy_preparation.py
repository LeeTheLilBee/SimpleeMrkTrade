from copy import deepcopy
from functools import lru_cache

from .post_walkthrough_staging_readiness_recheck_gate import build_post_walkthrough_staging_readiness_recheck_bundle
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_managed_staging_redeploy_preparation_gp036",
    "display_title": "Managed Staging Redeploy Preparation",
    "decision": "READY_FOR_MANAGED_STAGING_REDEPLOY_PREPARATION_WITH_SAFETY_LOCKS_HELD",
}

STAGING_SERVICE = "simplee-tower-ob-staging"
STAGING_REGION = "Virginia"
STAGING_ENTRYPOINT = "web.managed_staging:app"
STAGING_BRANCH = "ob-owner-experience-simplification"

FALSE_FLAGS = [
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
    "gp035_readiness_recheck_ready",
    "owner_walkthrough_accepted",
    "redeploy_preparation_ready",
    "managed_staging_target_declared",
    "commit_pin_required",
    "secret_alias_only_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "Render API call",
    "Render redeploy",
    "production deployment",
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
def _gp035():
    return build_post_walkthrough_staging_readiness_recheck_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_managed_staging_redeploy_plan():
    gp035 = _gp035()
    return {
        "source_dependency": "GP035",
        "service": STAGING_SERVICE,
        "region": STAGING_REGION,
        "entrypoint": STAGING_ENTRYPOINT,
        "branch": STAGING_BRANCH,
        "gp035_recommendation": gp035["recommendation"],
        "owner_walkthrough_accepted": gp035["status"]["owner_walkthrough_accepted"] is True,
        "managed_staging_redeploy_prep_required": gp035["status"]["managed_staging_redeploy_prep_required"] is True,
        "redeploy_preparation_ready": True,
        "commit_pin_required": True,
        "secret_alias_only_required": True,
        "render_api_call_allowed_now": False,
        "render_redeployed": False,
        "production_deploy_enabled": False,
        "staging_ready": False,
        "required_checks_after_redeploy": [
            "hosted runtime health",
            "Tower owner session",
            "Tower to OB launch",
            "OB six-room route reachability",
            "OB to Tower return",
            "dangerous actions locked",
            "no STAGING_READY claim until hosted evidence passes",
        ],
    }


def build_managed_staging_redeploy_preparation_status():
    plan = build_managed_staging_redeploy_plan()
    return {
        "gp035_readiness_recheck_ready": _gp035()["readiness_recheck_ready"] is True,
        "owner_walkthrough_accepted": plan["owner_walkthrough_accepted"] is True,
        "redeploy_preparation_ready": True,
        "managed_staging_target_declared": plan["service"] == STAGING_SERVICE,
        "commit_pin_required": True,
        "secret_alias_only_required": True,
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


def build_managed_staging_redeploy_preparation_bundle():
    plan = build_managed_staging_redeploy_plan()
    status = build_managed_staging_redeploy_preparation_status()
    adapter = _adapter()
    ready = (
        status["gp035_readiness_recheck_ready"] is True
        and status["owner_walkthrough_accepted"] is True
        and status["redeploy_preparation_ready"] is True
        and status["managed_staging_target_declared"] is True
        and status["commit_pin_required"] is True
        and status["secret_alias_only_required"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "redeploy_preparation_ready": ready,
        "source_dependency": "GP035",
        "recommendation": "GO_FOR_BUILD_CONFIGURATION_VERIFICATION",
        "gate_state": "ready_for_build_configuration_verification",
        "redeploy_plan": deepcopy(plan),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "redeploy_preparation_ready": True,
            "owner_walkthrough_accepted": True,
            "live_auto_locked": True,
        },
        "next_build": "Managed Staging Build Configuration Verification / GP037",
    }


def build_managed_staging_redeploy_preparation_handoff():
    bundle = build_managed_staging_redeploy_preparation_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "redeploy_preparation_ready": bundle["redeploy_preparation_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "redeploy_plan": bundle["redeploy_plan"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Managed staging redeploy preparation is ready.",
            "Do not call Render API from this package.",
            "Do not redeploy Render from this package.",
            "Do not claim hosted runtime verification.",
            "Do not claim STAGING_READY.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP037 Managed Staging Build Configuration Verification.",
        ],
    }
