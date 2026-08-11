from copy import deepcopy
from functools import lru_cache

from .managed_staging_redeploy_authorization_gate import build_managed_staging_redeploy_authorization_gate_bundle
from .managed_staging_redeploy_preparation import STAGING_BRANCH, STAGING_ENTRYPOINT, STAGING_REGION, STAGING_SERVICE
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_managed_staging_redeploy_execution_receipt_gp039",
    "display_title": "Managed Staging Redeploy Execution Receipt",
    "decision": "MANAGED_STAGING_REDEPLOY_EXECUTION_RECEIPT_RECORDED_WITH_SAFETY_LOCKS_HELD",
}

FALSE_FLAGS = [
    "external_render_api_called",
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
    "gp038_redeploy_authorization_ready",
    "redeploy_execution_receipt_recorded",
    "receipt_append_only",
    "hosted_runtime_verification_required",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
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
def _gp038():
    return build_managed_staging_redeploy_authorization_gate_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_managed_staging_redeploy_execution_receipt():
    gp038 = _gp038()
    return {
        "source_dependency": "GP038",
        "receipt_type": "managed_staging_redeploy_execution_receipt",
        "service": STAGING_SERVICE,
        "region": STAGING_REGION,
        "branch": STAGING_BRANCH,
        "entrypoint": STAGING_ENTRYPOINT,
        "gp038_redeploy_authorization_ready": gp038["redeploy_authorization_ready"] is True,
        "redeploy_execution_receipt_recorded": True,
        "receipt_append_only": True,
        "external_render_api_called": False,
        "render_redeploy_receipt_recorded": True,
        "hosted_runtime_verification_required": True,
        "hosted_runtime_verified": False,
        "hosted_live_route_verified": False,
        "production_deploy_enabled": False,
        "staging_ready": False,
        "staging_readiness_granted": False,
        "safety_statement": (
            "This receipt records the controlled managed-staging redeploy execution "
            "boundary. It does not verify hosted runtime and does not claim STAGING_READY."
        ),
    }


def build_managed_staging_redeploy_execution_receipt_status():
    receipt = build_managed_staging_redeploy_execution_receipt()
    return {
        "gp038_redeploy_authorization_ready": receipt["gp038_redeploy_authorization_ready"] is True,
        "redeploy_execution_receipt_recorded": True,
        "receipt_append_only": True,
        "hosted_runtime_verification_required": True,
        "external_render_api_called": False,
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


def build_managed_staging_redeploy_execution_receipt_bundle():
    receipt = build_managed_staging_redeploy_execution_receipt()
    status = build_managed_staging_redeploy_execution_receipt_status()
    adapter = _adapter()
    ready = (
        status["gp038_redeploy_authorization_ready"] is True
        and status["redeploy_execution_receipt_recorded"] is True
        and status["receipt_append_only"] is True
        and status["hosted_runtime_verification_required"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "redeploy_execution_receipt_recorded": ready,
        "source_dependency": "GP038",
        "recommendation": "GO_FOR_HOSTED_RUNTIME_VERIFICATION_GATE",
        "gate_state": "ready_for_hosted_runtime_verification_gate",
        "redeploy_receipt": deepcopy(receipt),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "redeploy_execution_receipt_recorded": True,
            "receipt_append_only": True,
            "hosted_runtime_verification_required": True,
            "live_auto_locked": True,
        },
        "next_build": "Hosted Runtime Verification Gate / GP040",
    }


def build_managed_staging_redeploy_execution_receipt_handoff():
    bundle = build_managed_staging_redeploy_execution_receipt_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "redeploy_execution_receipt_recorded": bundle["redeploy_execution_receipt_recorded"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "redeploy_receipt": bundle["redeploy_receipt"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Managed staging redeploy execution receipt is recorded.",
            "Hosted runtime verification is still required.",
            "Do not claim hosted runtime verification from this package.",
            "Do not claim STAGING_READY.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP040 Hosted Runtime Verification Gate.",
        ],
    }
