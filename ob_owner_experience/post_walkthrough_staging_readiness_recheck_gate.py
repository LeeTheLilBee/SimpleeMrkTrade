from copy import deepcopy
from functools import lru_cache

from .owner_walkthrough_acceptance_decision_record import build_owner_walkthrough_acceptance_decision_bundle
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_post_walkthrough_staging_readiness_recheck_gate_gp035",
    "display_title": "Post-Walkthrough Staging Readiness Recheck Gate",
    "decision": "READY_FOR_MANAGED_STAGING_REDEPLOY_PREP_NOT_STAGING_READY",
}

FALSE_FLAGS = [
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
    "gp034_acceptance_decision_recorded",
    "owner_walkthrough_started",
    "owner_walkthrough_accepted",
    "readiness_recheck_ready",
    "managed_staging_redeploy_prep_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
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
def _gp034():
    return build_owner_walkthrough_acceptance_decision_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_post_walkthrough_staging_readiness_record():
    gp034 = _gp034()
    return {
        "source_dependency": "GP034",
        "recommendation": "GO_FOR_MANAGED_STAGING_REDEPLOY_PREP",
        "readiness_recheck_ready": True,
        "owner_walkthrough_started": gp034["status"]["owner_walkthrough_started"] is True,
        "owner_walkthrough_accepted": gp034["status"]["owner_walkthrough_accepted"] is True,
        "managed_staging_redeploy_prep_required": True,
        "hosted_runtime_verification_required_after_redeploy": True,
        "staging_ready": False,
        "staging_readiness_granted": False,
        "reason": (
            "Owner walkthrough is accepted, but managed staging redeploy and hosted "
            "runtime verification have not occurred. Therefore STAGING_READY remains false."
        ),
    }


def build_post_walkthrough_staging_readiness_status():
    record = build_post_walkthrough_staging_readiness_record()
    return {
        "gp034_acceptance_decision_recorded": _gp034()["acceptance_decision_recorded"] is True,
        "owner_walkthrough_started": record["owner_walkthrough_started"] is True,
        "owner_walkthrough_accepted": record["owner_walkthrough_accepted"] is True,
        "readiness_recheck_ready": True,
        "managed_staging_redeploy_prep_required": True,
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


def build_post_walkthrough_staging_readiness_recheck_bundle():
    record = build_post_walkthrough_staging_readiness_record()
    status = build_post_walkthrough_staging_readiness_status()
    adapter = _adapter()
    ready = (
        status["gp034_acceptance_decision_recorded"] is True
        and status["owner_walkthrough_started"] is True
        and status["owner_walkthrough_accepted"] is True
        and status["readiness_recheck_ready"] is True
        and status["managed_staging_redeploy_prep_required"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "readiness_recheck_ready": ready,
        "source_dependency": "GP034",
        "recommendation": record["recommendation"],
        "gate_state": "ready_for_managed_staging_redeploy_preparation",
        "readiness_record": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "owner_walkthrough_started": True,
            "owner_walkthrough_accepted": True,
            "managed_staging_redeploy_prep_required": True,
            "live_auto_locked": True,
        },
        "next_build": "Managed Staging Redeploy Preparation / GP036",
    }


def build_post_walkthrough_staging_readiness_recheck_handoff():
    bundle = build_post_walkthrough_staging_readiness_recheck_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "readiness_recheck_ready": bundle["readiness_recheck_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "readiness_record": bundle["readiness_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Owner walkthrough is accepted.",
            "Staging readiness is still false.",
            "Proceed next to managed staging redeploy preparation.",
            "Do not redeploy Render from this package.",
            "Do not claim hosted runtime verification from this package.",
            "Do not claim STAGING_READY.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP036 Managed Staging Redeploy Preparation.",
        ],
    }
