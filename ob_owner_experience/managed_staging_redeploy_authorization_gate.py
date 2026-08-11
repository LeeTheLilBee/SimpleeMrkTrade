from copy import deepcopy
from functools import lru_cache

from .managed_staging_build_configuration_verification import build_managed_staging_build_configuration_verification_bundle
from .ui_surface_registry import MUST_NOT_CLAIM, PROTECTED_ROUTE_POLICY, build_real_surface_adapter_contract

IDENTITY = {
    "package": "ob_managed_staging_redeploy_authorization_gate_gp038",
    "display_title": "Managed Staging Redeploy Authorization Gate",
    "decision": "MANAGED_STAGING_REDEPLOY_AUTHORIZED_FOR_RECEIPT_ONLY_WITH_SAFETY_LOCKS_HELD",
}

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
    "gp037_build_configuration_verified",
    "redeploy_authorization_ready",
    "owner_authorization_recorded",
    "receipt_only_boundary_required",
    "hosted_runtime_verification_required_after_receipt",
    "owner_session_required",
    "live_auto_locked",
]

NOT_AUTHORIZED = [
    "STAGING_READY",
    "Render API call from authorization gate",
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
def _gp037():
    return build_managed_staging_build_configuration_verification_bundle()


@lru_cache(maxsize=1)
def _adapter():
    return build_real_surface_adapter_contract()


def build_managed_staging_redeploy_authorization_record():
    gp037 = _gp037()
    return {
        "source_dependency": "GP037",
        "authorization_type": "managed_staging_redeploy_authorization",
        "gp037_build_configuration_verified": gp037["build_configuration_verified"] is True,
        "owner_authorization_recorded": True,
        "authorized_for_receipt_package": True,
        "external_render_api_call_allowed_in_this_package": False,
        "receipt_only_boundary_required": True,
        "hosted_runtime_verification_required_after_receipt": True,
        "production_deploy_enabled": False,
        "staging_ready": False,
        "safety_statement": (
            "Redeploy is authorized for the next receipt package only. This gate does "
            "not call Render API, does not verify hosted runtime, and does not claim STAGING_READY."
        ),
    }


def build_managed_staging_redeploy_authorization_status():
    record = build_managed_staging_redeploy_authorization_record()
    return {
        "gp037_build_configuration_verified": record["gp037_build_configuration_verified"] is True,
        "redeploy_authorization_ready": True,
        "owner_authorization_recorded": True,
        "receipt_only_boundary_required": True,
        "hosted_runtime_verification_required_after_receipt": True,
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


def build_managed_staging_redeploy_authorization_gate_bundle():
    record = build_managed_staging_redeploy_authorization_record()
    status = build_managed_staging_redeploy_authorization_status()
    adapter = _adapter()
    ready = (
        status["gp037_build_configuration_verified"] is True
        and status["redeploy_authorization_ready"] is True
        and status["owner_authorization_recorded"] is True
        and status["receipt_only_boundary_required"] is True
        and status["hosted_runtime_verification_required_after_receipt"] is True
        and all(status[key] is False for key in FALSE_FLAGS)
        and all(status[key] is True for key in TRUE_FLAGS)
        and "STAGING_READY" in MUST_NOT_CLAIM
    )
    return {
        "package": IDENTITY["package"],
        "display_title": IDENTITY["display_title"],
        "decision": IDENTITY["decision"],
        "redeploy_authorization_ready": ready,
        "source_dependency": "GP037",
        "recommendation": "GO_FOR_MANAGED_STAGING_REDEPLOY_EXECUTION_RECEIPT",
        "gate_state": "authorized_for_redeploy_execution_receipt_package",
        "authorization_record": deepcopy(record),
        "status": deepcopy(status),
        "protected_route_policy": deepcopy(PROTECTED_ROUTE_POLICY),
        "safety_summary": deepcopy(adapter["safety_summary"]),
        "must_not_claim": list(MUST_NOT_CLAIM),
        "not_authorized": list(NOT_AUTHORIZED),
        "release_boundary": {key: False for key in FALSE_FLAGS} | {
            "redeploy_authorization_ready": True,
            "owner_authorization_recorded": True,
            "live_auto_locked": True,
        },
        "next_build": "Managed Staging Redeploy Execution Receipt / GP039",
    }


def build_managed_staging_redeploy_authorization_gate_handoff():
    bundle = build_managed_staging_redeploy_authorization_gate_bundle()
    return {
        "package": bundle["package"],
        "display_title": bundle["display_title"],
        "decision": bundle["decision"],
        "redeploy_authorization_ready": bundle["redeploy_authorization_ready"],
        "source_dependency": bundle["source_dependency"],
        "recommendation": bundle["recommendation"],
        "gate_state": bundle["gate_state"],
        "authorization_record": bundle["authorization_record"],
        "release_boundary": bundle["release_boundary"],
        "must_not_claim": bundle["must_not_claim"],
        "not_authorized": bundle["not_authorized"],
        "next_builder_notes": [
            "Managed staging redeploy authorization is recorded.",
            "This authorization is for the next receipt package only.",
            "Do not claim hosted runtime verification from this package.",
            "Do not claim STAGING_READY.",
            "Keep production deployment disabled.",
            "Keep broker submission locked.",
            "Keep real capital movement locked.",
            "Keep Live Auto locked.",
            "Next build is GP039 Managed Staging Redeploy Execution Receipt.",
        ],
    }
