from __future__ import annotations

import copy
import json
from functools import lru_cache
from pathlib import Path

from tower.tower_ob_managed_staging_provider_authorization import (
    REQUIRED_CAPABILITIES,
    build_owner_authorization_challenge,
    freeze_provider_authorization_packet,
    provider_input_template,
)
from tower.tower_ob_managed_staging_no_call_provisioning_review import (
    REQUIRED_REVIEW_ATTESTATIONS,
    build_authorization_handoff,
    no_call_review_input_template,
)
from tower.tower_ob_managed_staging_provider_provisioning_authorization import (
    AUTHORIZE_DECISION as AUTHORIZE_PREPARATION,
    REQUIRED_SCOPE_ATTESTATIONS,
    build_completed_review_handoff,
    build_provisioning_authorization_challenge,
    provisioning_authorization_decision_template,
)
from tower.tower_ob_managed_staging_no_call_provisioning_execution_preparation import (
    REQUIRED_PREPARATION_ATTESTATIONS,
    build_provisioning_authorization_handoff,
    execution_preparation_input_template,
)
from tower.tower_ob_managed_staging_provider_provisioning_execution_authorization import (
    AUTHORIZE_DECISION,
    REQUIRED_EXECUTION_SCOPE_ATTESTATIONS,
    build_completed_execution_preparation_handoff,
    build_execution_authorization_challenge,
    execution_authorization_decision_template,
)
from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_preparation import (
    NON_SECRET_ENVIRONMENT_NAMES,
    READY_DECISION,
    REQUIRED_SESSION_PREPARATION_ATTESTATIONS,
    SECRET_REFERENCE_NAMES,
    blank_current_inputs,
    build_controlled_session_preparation_decision,
    build_current_controlled_session_preparation_state,
    build_duplicate_resource_lookup_preflight,
    build_environment_and_secret_registration_sequence,
    build_execution_authorization_handoff,
    build_inert_session_opening_authorization_plan,
    build_one_service_shell_request,
    build_operational_control_rehearsal,
    build_provider_session_identity_binding,
    build_receipt_chain_and_stop_gate,
    controlled_session_preparation_input_template,
    freeze_controlled_session_preparation_packet,
    validate_controlled_session_preparation_inputs,
    write_controlled_session_preparation_worksheets,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "0e1bb39ae7e388ff6897ee82b2da12072c856333"


def _complete_provider_inputs() -> dict:
    payload = provider_input_template()
    payload.update({
        "provider_slug": "managed-host-session-preparation",
        "account_or_team_ref": "simplee-staging-team",
        "deployment_region": "us-east-session-preparation",
        "billing_owner_ref": "simplee-owner-billing",
        "service_name": "simplee-tower-ob-staging",
        "repository_ref": "LeeTheLilBee/SimpleeMrkTrade",
        "source_branch": "tower-ob-integration-dev",
    })
    payload["capability_attestations"] = {
        name: True for name in REQUIRED_CAPABILITIES
    }
    return payload


def _complete_review_owner_decision(provider_inputs: dict) -> dict:
    frozen = freeze_provider_authorization_packet(ROOT, provider_inputs)
    challenge = build_owner_authorization_challenge(
        packet_hash=frozen["frozen_packet_hash"]
    )
    return {
        "decision": "APPROVE_FOR_PROVISIONING_REVIEW",
        "owner_id": "tower-owner-review",
        "tower_step_up_receipt_ref": "tower-step-up-review-receipt",
        "challenge_id": challenge["challenge_id"],
        "challenge_phrase_confirmation": challenge["challenge_phrase"],
        "decided_at": "2026-07-16T16:05:00Z",
    }


def _complete_review_inputs(provider_inputs: dict, owner_decision: dict) -> dict:
    handoff = build_authorization_handoff(
        ROOT, provider_inputs, owner_decision
    )
    payload = no_call_review_input_template(handoff)
    payload.update({
        "provider_documentation_ref": "provider-docs/python-service",
        "account_access_evidence_ref": "review/account-access",
        "region_availability_evidence_ref": "review/region-availability",
        "cost_review_ref": "review/staging-cost-boundary",
        "secret_store_evidence_ref": "provider-docs/secret-store",
        "health_check_evidence_ref": "provider-docs/health-checks",
        "deployment_logging_evidence_ref": "provider-docs/deployment-logs",
        "access_logging_evidence_ref": "provider-docs/access-logs",
        "rollback_evidence_ref": "provider-docs/rollback",
        "reviewed_by": "tower-owner-review",
        "reviewed_at": "2026-07-16T16:06:00Z",
    })
    payload["attestations"] = {
        name: True for name in REQUIRED_REVIEW_ATTESTATIONS
    }
    return payload


def _complete_provisioning_decision(handoff: dict) -> dict:
    challenge = build_provisioning_authorization_challenge(handoff)
    payload = provisioning_authorization_decision_template(handoff)
    payload.update({
        "decision": AUTHORIZE_PREPARATION,
        "owner_id": "tower-owner-provisioning",
        "tower_step_up_receipt_ref": "tower-step-up-provisioning-receipt",
        "challenge_id": challenge["challenge_id"],
        "challenge_phrase_confirmation": challenge["challenge_phrase"],
        "decided_at": "2026-07-16T16:07:00Z",
        "authorization_expires_at": "2026-07-16T18:07:00Z",
        "monthly_cost_ceiling_usd": "100.00",
    })
    payload["authorized_scope"] = {
        "provider_console_access": True,
        "create_one_managed_web_service": True,
        "configure_non_secret_environment_names": True,
        "register_secret_references_without_readback": True,
        "configure_health_checks": True,
        "configure_deployment_and_access_logs": True,
        "configure_manual_deployment_control": True,
        "configure_rollback_target": True,
    }
    payload["scope_attestations"] = {
        name: True for name in REQUIRED_SCOPE_ATTESTATIONS
    }
    return payload


def _complete_execution_preparation_inputs(handoff: dict) -> dict:
    payload = execution_preparation_input_template(handoff)
    payload.update({
        "provider_console_session_ref": "prep/provider-console-session",
        "provider_service_form_ref": "prep/one-service-form",
        "source_commit_ref": f"commit/{SOURCE_COMMIT}",
        "runtime_review_ref": "prep/runtime-target-review",
        "environment_name_review_ref": "prep/environment-name-review",
        "secret_reference_custody_ref": "prep/secret-reference-custody",
        "health_logging_review_ref": "prep/health-logging-review",
        "rollback_review_ref": "prep/rollback-review",
        "cost_guardrail_review_ref": "prep/cost-guardrail-review",
        "idempotency_guard_ref": "prep/idempotency-guard-review",
        "prepared_by": "tower-owner-preparation",
        "prepared_at": "2026-07-16T16:08:00Z",
    })
    payload["attestations"] = {
        name: True for name in REQUIRED_PREPARATION_ATTESTATIONS
    }
    return payload


def _complete_execution_authorization(
    handoff: dict,
    provisioning: dict,
    execution_preparation: dict,
) -> dict:
    challenge = build_execution_authorization_challenge(handoff)
    payload = execution_authorization_decision_template(handoff)
    payload.update({
        "decision": AUTHORIZE_DECISION,
        "owner_id": "tower-owner-execution",
        "tower_step_up_receipt_ref": "tower-step-up-execution-receipt",
        "challenge_id": challenge["challenge_id"],
        "challenge_phrase_confirmation": challenge["challenge_phrase"],
        "decided_at": "2026-07-16T16:09:00Z",
        "execution_window_starts_at": "2026-07-16T16:10:00Z",
        "execution_window_expires_at": "2026-07-16T17:10:00Z",
        "authorized_source_commit_ref": execution_preparation[
            "source_commit_ref"
        ],
        "monthly_cost_ceiling_usd": provisioning[
            "monthly_cost_ceiling_usd"
        ],
    })
    payload["authorized_scope"] = {
        "provider_console_login": True,
        "provider_account_team_access": True,
        "provider_region_access": True,
        "duplicate_resource_lookup": True,
        "create_one_inert_managed_web_service_shell": True,
        "bind_authorized_repository_branch_and_commit": True,
        "configure_non_secret_environment_names": True,
        "register_secret_references_without_readback": True,
        "configure_health_checks": True,
        "configure_deployment_and_access_logs": True,
        "configure_manual_deployment_control": True,
        "configure_rollback_target": True,
        "capture_non_secret_provider_resource_references": True,
    }
    payload["scope_attestations"] = {
        name: True for name in REQUIRED_EXECUTION_SCOPE_ATTESTATIONS
    }
    return payload


@lru_cache(maxsize=1)
def _cached_ready_execution_authorization() -> tuple:
    provider = _complete_provider_inputs()
    review_owner = _complete_review_owner_decision(provider)
    review = _complete_review_inputs(provider, review_owner)
    review_handoff = build_completed_review_handoff(
        ROOT, provider, review_owner, review
    )
    assert review_handoff["completed_review_ready"] is True
    provisioning = _complete_provisioning_decision(review_handoff)
    provisioning_handoff = build_provisioning_authorization_handoff(
        ROOT, provider, review_owner, review, provisioning
    )
    assert provisioning_handoff["handoff_ready"] is True
    execution_preparation = _complete_execution_preparation_inputs(
        provisioning_handoff
    )
    execution_preparation_handoff = (
        build_completed_execution_preparation_handoff(
            ROOT,
            provider,
            review_owner,
            review,
            provisioning,
            execution_preparation,
        )
    )
    assert execution_preparation_handoff[
        "completed_execution_preparation_ready"
    ] is True
    execution_authorization = _complete_execution_authorization(
        execution_preparation_handoff,
        provisioning,
        execution_preparation,
    )
    handoff = build_execution_authorization_handoff(
        ROOT,
        provider,
        review_owner,
        review,
        provisioning,
        execution_preparation,
        execution_authorization,
    )
    assert handoff["execution_authorization_ready"] is True
    return (
        provider,
        review_owner,
        review,
        provisioning,
        execution_preparation,
        execution_authorization,
        handoff,
    )


def _ready_execution_authorization() -> tuple:
    return copy.deepcopy(_cached_ready_execution_authorization())


def _complete_session_preparation(handoff: dict) -> dict:
    payload = controlled_session_preparation_input_template(handoff)
    payload.update({
        "owner_execution_session_receipt_ref": "tower/session-prep-receipt",
        "provider_console_access_preflight_ref": "session/provider-console-preflight",
        "provider_account_team_binding_ref": "session/account-team-binding",
        "provider_region_binding_ref": "session/region-binding",
        "duplicate_resource_lookup_plan_ref": "session/duplicate-lookup-plan",
        "service_creation_form_review_ref": "session/one-service-form-review",
        "repository_binding_review_ref": "session/repository-binding-review",
        "non_secret_environment_registration_review_ref": "session/environment-names-review",
        "secret_reference_registration_review_ref": "session/secret-reference-review",
        "health_logging_review_ref": "session/health-logging-review",
        "manual_deployment_control_review_ref": "session/manual-control-review",
        "rollback_review_ref": "session/rollback-review",
        "cost_ceiling_review_ref": "session/cost-ceiling-review",
        "receipt_chain_review_ref": "session/receipt-chain-review",
        "stop_conditions_review_ref": "session/stop-conditions-review",
        "prepared_by": "tower-owner-session-preparation",
        "prepared_at": "2026-07-16T16:09:30Z",
    })
    payload["attestations"] = {
        name: True for name in REQUIRED_SESSION_PREPARATION_ATTESTATIONS
    }
    return payload

from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_opening_authorization import (
    AUTHORIZE_DECISION as AUTHORIZE_SESSION_OPENING,
    READY_DECISION as SESSION_OPENING_READY,
    REQUIRED_OPENING_SCOPE_ATTESTATIONS,
    blank_current_inputs as blank_opening_inputs,
    build_completed_session_preparation_handoff,
    build_current_session_opening_authorization_state,
    build_inert_session_opening_preparation_plan,
    build_session_identity_and_window_manifest,
    build_session_opening_authorization_challenge,
    build_session_opening_authorization_decision,
    build_session_opening_receipt_and_stop_contract,
    build_session_opening_scope_manifest,
    freeze_session_opening_authorization_record,
    session_opening_authorization_decision_template,
    validate_session_opening_authorization_decision,
    write_session_opening_authorization_worksheets,
)


@lru_cache(maxsize=1)
def _cached_ready_session_preparation() -> tuple:
    (
        provider, review_owner, review, provisioning,
        execution_preparation, execution_authorization, execution_handoff,
    ) = _cached_ready_execution_authorization()
    session_preparation = _complete_session_preparation(execution_handoff)
    handoff = build_completed_session_preparation_handoff(
        ROOT, provider, review_owner, review, provisioning,
        execution_preparation, execution_authorization, session_preparation,
    )
    assert handoff["completed_session_preparation_ready"] is True
    return (
        provider, review_owner, review, provisioning,
        execution_preparation, execution_authorization,
        session_preparation, handoff,
    )


def _ready_session_preparation() -> tuple:
    return copy.deepcopy(_cached_ready_session_preparation())


def _complete_opening_decision(handoff: dict) -> dict:
    challenge = build_session_opening_authorization_challenge(handoff)
    payload = session_opening_authorization_decision_template(handoff)
    payload.update({
        "decision": AUTHORIZE_SESSION_OPENING,
        "owner_id": "tower-owner-session-opening",
        "tower_step_up_receipt_ref": "tower-step-up-session-opening-receipt",
        "challenge_id": challenge["challenge_id"],
        "challenge_phrase_confirmation": challenge["challenge_phrase"],
        "decided_at": "2026-07-16T16:09:35Z",
        "authorization_expires_at": "2026-07-16T16:30:00Z",
    })
    payload["authorized_scope"] = {
        "open_one_manual_provider_console_session": True,
        "authenticate_to_bound_provider_account_team": True,
        "perform_duplicate_resource_lookup": True,
        "prepare_one_inert_managed_web_service_shell": True,
        "capture_non_secret_provider_references": True,
    }
    payload["scope_attestations"] = {
        name: True for name in REQUIRED_OPENING_SCOPE_ATTESTATIONS
    }
    return payload



from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_opening_preparation import (
    NON_SECRET_ENVIRONMENT_NAMES as OPENING_ENVIRONMENT_NAMES,
    READY_DECISION as OPENING_PREPARATION_READY,
    REQUIRED_OPENING_PREPARATION_ATTESTATIONS,
    SECRET_REFERENCE_NAMES as OPENING_SECRET_REFERENCE_NAMES,
    blank_current_inputs as blank_opening_preparation_inputs,
    build_credential_custody_and_authorization_window_preflight,
    build_current_session_opening_preparation_state,
    build_duplicate_resource_and_binding_revalidation_preflight,
    build_environment_and_secret_reference_opening_sequence,
    build_inert_session_opening_execution_authorization_plan,
    build_one_inert_service_opening_request,
    build_opening_receipt_chain_close_and_stop_gate,
    build_provider_identity_and_session_isolation_preflight,
    build_session_opening_authorization_handoff,
    build_session_opening_preparation_decision,
    freeze_session_opening_preparation_packet,
    session_opening_preparation_input_template,
    validate_session_opening_preparation_inputs,
    write_session_opening_preparation_worksheets,
)


@lru_cache(maxsize=1)
def _cached_ready_opening_authorization() -> tuple:
    (
        provider, review_owner, review, provisioning,
        execution_preparation, execution_authorization,
        session_preparation, session_preparation_handoff,
    ) = _cached_ready_session_preparation()
    opening_authorization = _complete_opening_decision(session_preparation_handoff)
    handoff = build_session_opening_authorization_handoff(
        ROOT, provider, review_owner, review, provisioning,
        execution_preparation, execution_authorization,
        session_preparation, opening_authorization,
    )
    assert handoff["authorization_handoff_ready"] is True
    return (
        provider, review_owner, review, provisioning,
        execution_preparation, execution_authorization,
        session_preparation, opening_authorization, handoff,
    )


def _ready_opening_authorization() -> tuple:
    return copy.deepcopy(_cached_ready_opening_authorization())


def _complete_opening_preparation(handoff: dict) -> dict:
    payload = session_opening_preparation_input_template(handoff)
    payload.update({
        "owner_session_opening_preparation_receipt_ref": "tower/session-opening-preparation-receipt",
        "provider_console_entrypoint_review_ref": "opening/provider-console-entrypoint-review",
        "provider_identity_revalidation_ref": "opening/provider-identity-revalidation",
        "account_team_revalidation_ref": "opening/account-team-revalidation",
        "region_revalidation_ref": "opening/region-revalidation",
        "authorization_window_revalidation_ref": "opening/authorization-window-revalidation",
        "duplicate_resource_lookup_preflight_ref": "opening/duplicate-resource-lookup-preflight",
        "browser_session_isolation_plan_ref": "opening/browser-session-isolation-plan",
        "credential_custody_preflight_ref": "opening/credential-custody-preflight",
        "one_service_shell_form_preflight_ref": "opening/one-service-shell-form-preflight",
        "repository_binding_preflight_ref": "opening/repository-binding-preflight",
        "non_secret_environment_names_preflight_ref": "opening/environment-names-preflight",
        "secret_reference_custody_preflight_ref": "opening/secret-reference-custody-preflight",
        "receipt_chain_preflight_ref": "opening/receipt-chain-preflight",
        "session_close_and_revocation_plan_ref": "opening/session-close-revocation-plan",
        "prepared_by": "tower-owner-session-opening-preparation",
        "prepared_at": "2026-07-16T16:09:40Z",
    })
    payload["attestations"] = {
        name: True for name in REQUIRED_OPENING_PREPARATION_ATTESTATIONS
    }
    return payload


def test_blank_session_opening_authorization_handoff_is_held():
    prior = blank_opening_preparation_inputs(ROOT)[:-1]
    handoff = build_session_opening_authorization_handoff(ROOT, *prior)
    assert handoff["authorization_handoff_ready"] is False
    assert handoff["provider_session_opened"] is False


def test_complete_session_opening_authorization_handoff_is_ready_for_preparation_only():
    *_, handoff = _ready_opening_authorization()
    assert handoff["authorization_handoff_ready"] is True
    assert handoff["provider_session_opening_authorized"] is False


def test_opening_preparation_template_contains_no_secret_values():
    *_, handoff = _ready_opening_authorization()
    payload = session_opening_preparation_input_template(handoff)
    rendered = json.dumps(payload).lower()
    assert "ghp_" not in rendered
    assert "password=" not in rendered


def test_blank_opening_preparation_inputs_fail_closed():
    *_, handoff = _ready_opening_authorization()
    report = validate_session_opening_preparation_inputs(
        session_opening_preparation_input_template(handoff), handoff=handoff
    )
    assert report["valid"] is False


def test_complete_opening_preparation_inputs_validate():
    *_, handoff = _ready_opening_authorization()
    report = validate_session_opening_preparation_inputs(
        _complete_opening_preparation(handoff), handoff=handoff
    )
    assert report["valid"] is True
    assert report["errors"] == []


def test_sensitive_material_is_rejected():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    payload["credential_custody_preflight_ref"] = "password=hunter2"
    report = validate_session_opening_preparation_inputs(payload, handoff=handoff)
    assert report["valid"] is False
    assert report["checks"]["contains_sensitive_material"] is True


def test_frozen_opening_authorization_hash_binding_is_required():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    payload["frozen_session_opening_authorization_record_hash"] = "0" * 64
    assert validate_session_opening_preparation_inputs(payload, handoff=handoff)["valid"] is False


def test_opening_authorization_decision_hash_binding_is_required():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    payload["session_opening_authorization_decision_hash"] = "1" * 64
    assert validate_session_opening_preparation_inputs(payload, handoff=handoff)["valid"] is False


def test_authorized_source_commit_binding_is_required():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    payload["authorized_source_commit_ref"] = "commit/" + "2" * 40
    assert validate_session_opening_preparation_inputs(payload, handoff=handoff)["valid"] is False


def test_session_window_must_match_authorization():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    payload["authorized_session_expires_at"] = "2026-07-16T17:09:00Z"
    assert validate_session_opening_preparation_inputs(payload, handoff=handoff)["valid"] is False


def test_authorization_expiry_must_match_handoff():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    payload["authorization_expires_at"] = "2026-07-16T16:29:00Z"
    assert validate_session_opening_preparation_inputs(payload, handoff=handoff)["valid"] is False


def test_preparation_must_occur_before_authorization_expiry():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    payload["prepared_at"] = "2026-07-16T16:31:00Z"
    assert validate_session_opening_preparation_inputs(payload, handoff=handoff)["valid"] is False


def test_cost_ceiling_must_match_authorization():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    payload["monthly_cost_ceiling_usd"] = "999.00"
    assert validate_session_opening_preparation_inputs(payload, handoff=handoff)["valid"] is False


def test_owner_opening_preparation_receipt_is_required():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    payload["owner_session_opening_preparation_receipt_ref"] = ""
    assert validate_session_opening_preparation_inputs(payload, handoff=handoff)["valid"] is False


def test_all_preparation_references_are_required():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    payload["provider_identity_revalidation_ref"] = ""
    assert validate_session_opening_preparation_inputs(payload, handoff=handoff)["valid"] is False


def test_all_opening_preparation_attestations_are_required():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    payload["attestations"][REQUIRED_OPENING_PREPARATION_ATTESTATIONS[0]] = False
    assert validate_session_opening_preparation_inputs(payload, handoff=handoff)["valid"] is False


def test_identity_preflight_records_fingerprints_not_raw_provider_values():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    validation = validate_session_opening_preparation_inputs(payload, handoff=handoff)
    preflight = build_provider_identity_and_session_isolation_preflight(handoff, payload, validation)
    assert preflight["provider_slug_sha256"]
    assert "managed-host-session-preparation" not in json.dumps(preflight)
    assert preflight["credentials_recorded"] is False


def test_session_isolation_preflight_requires_private_isolated_browser():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    validation = validate_session_opening_preparation_inputs(payload, handoff=handoff)
    preflight = build_provider_identity_and_session_isolation_preflight(handoff, payload, validation)
    assert preflight["isolated_browser_session_required"] is True
    assert preflight["private_browsing_profile_required"] is True
    assert preflight["provider_session_opened"] is False


def test_duplicate_resource_revalidation_preflight_is_inert():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    validation = validate_session_opening_preparation_inputs(payload, handoff=handoff)
    preflight = build_duplicate_resource_and_binding_revalidation_preflight(handoff, payload, validation)
    assert preflight["provider_calls_performed"] is False
    assert preflight["resources_created"] is False


def test_duplicate_resource_preflight_requires_stop_on_ambiguity():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    validation = validate_session_opening_preparation_inputs(payload, handoff=handoff)
    preflight = build_duplicate_resource_and_binding_revalidation_preflight(handoff, payload, validation)
    assert preflight["stop_on_duplicate_or_ambiguous_result"] is True


def test_credential_custody_preflight_records_no_credentials_or_cookies():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    validation = validate_session_opening_preparation_inputs(payload, handoff=handoff)
    preflight = build_credential_custody_and_authorization_window_preflight(handoff, payload, validation)
    assert preflight["credential_values_recorded"] is False
    assert preflight["credential_readback_authorized"] is False
    assert preflight["session_cookie_capture_authorized"] is False


def test_one_service_request_preserves_tower_front_door():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    validation = validate_session_opening_preparation_inputs(payload, handoff=handoff)
    request = build_one_inert_service_opening_request(payload, validation)
    assert request["runtime_target"] == "web.managed_staging:app"
    assert request["public_ingress_owner"] == "tower_only"
    assert request["observatory_separate_service_required"] is False


def test_one_service_request_blocks_database_storage_dns_build_and_deploy():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    validation = validate_session_opening_preparation_inputs(payload, handoff=handoff)
    request = build_one_inert_service_opening_request(payload, validation)
    assert request["future_resource_ceiling"] == {
        "managed_web_service_shells": 1,
        "databases": 0,
        "object_storage_buckets": 0,
        "dns_changes": 0,
    }
    assert request["build_authorized"] is False
    assert request["deployment_authorized"] is False


def test_environment_sequence_contains_names_not_values():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    validation = validate_session_opening_preparation_inputs(payload, handoff=handoff)
    sequence = build_environment_and_secret_reference_opening_sequence(payload, validation)
    assert tuple(sequence["non_secret_environment_names"]) == OPENING_ENVIRONMENT_NAMES
    assert sequence["secret_values_included"] is False


def test_secret_reference_sequence_prohibits_readback_and_git_values():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    validation = validate_session_opening_preparation_inputs(payload, handoff=handoff)
    sequence = build_environment_and_secret_reference_opening_sequence(payload, validation)
    assert tuple(sequence["secret_reference_names"]) == OPENING_SECRET_REFERENCE_NAMES
    assert sequence["secret_readback_authorized"] is False
    assert sequence["repository_secret_values_authorized"] is False


def test_receipt_chain_requires_close_and_revocation_receipts():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    validation = validate_session_opening_preparation_inputs(payload, handoff=handoff)
    gate = build_opening_receipt_chain_close_and_stop_gate(payload, validation)
    assert "provider_session_close_receipt" in gate["required_receipt_order"]
    assert "provider_session_revocation_or_logout_receipt" in gate["required_receipt_order"]


def test_stop_gate_blocks_resource_secret_build_and_deployment_actions():
    *_, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    validation = validate_session_opening_preparation_inputs(payload, handoff=handoff)
    gate = build_opening_receipt_chain_close_and_stop_gate(payload, validation)
    assert gate["stop_before_resource_creation"] is True
    assert gate["stop_before_secret_registration"] is True
    assert gate["stop_before_build"] is True
    assert gate["stop_before_deployment"] is True


def test_frozen_opening_preparation_packet_is_sanitized():
    *inputs, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    frozen = freeze_session_opening_preparation_packet(ROOT, *inputs, payload)
    assert frozen["opening_preparation_valid"] is True
    assert frozen["raw_secret_values_recorded"] is False
    assert frozen["provider_session_opened"] is False


def test_frozen_opening_preparation_hash_is_stable():
    *inputs, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    first = freeze_session_opening_preparation_packet(ROOT, *inputs, payload)
    second = freeze_session_opening_preparation_packet(ROOT, *inputs, payload)
    assert first["frozen_session_opening_preparation_packet_hash"] == second["frozen_session_opening_preparation_packet_hash"]


def test_blank_current_decision_preserves_prior_hold():
    inputs = blank_opening_preparation_inputs(ROOT)
    decision = build_session_opening_preparation_decision(ROOT, *inputs)
    assert decision["ready_for_separate_controlled_provider_session_opening_execution_authorization"] is False
    assert decision["provider_session_opened"] is False


def test_complete_preparation_opens_only_separate_execution_authorization():
    *inputs, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    decision = build_session_opening_preparation_decision(ROOT, *inputs, payload)
    assert decision["final_decision"] == OPENING_PREPARATION_READY
    assert decision["ready_for_separate_controlled_provider_session_opening_execution_authorization"] is True
    assert decision["provider_session_opening_authorized"] is False


def test_inert_execution_authorization_plan_invokes_nothing():
    *inputs, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    plan = build_inert_session_opening_execution_authorization_plan(ROOT, *inputs, payload)
    assert plan["dry_run_only"] is True
    assert plan["browser_actions"] == []
    assert plan["provider_cli_commands"] == []
    assert plan["provider_api_requests"] == []
    assert plan["http_requests"] == []
    assert plan["shell_commands"] == []


def test_current_blank_state_closes_step_120_fail_closed():
    state = build_current_session_opening_preparation_state(ROOT, *blank_opening_preparation_inputs(ROOT))
    assert state["closed_through_step"] == 120
    assert state["session_opening_preparation_valid"] is False
    assert state["provider_session_opened"] is False


def test_current_complete_state_is_ready_for_separate_authorization_only():
    *inputs, handoff = _ready_opening_authorization()
    payload = _complete_opening_preparation(handoff)
    state = build_current_session_opening_preparation_state(ROOT, *inputs, payload)
    assert state["ready_for_separate_controlled_provider_session_opening_execution_authorization"] is True
    assert state["provider_session_opened"] is False
    assert state["resources_created"] is False


def test_opening_preparation_worksheets_are_outside_repo_and_placeholder_is_hold(tmp_path):
    result = write_session_opening_preparation_worksheets(tmp_path / "worksheets", repository_root=ROOT)
    worksheet = Path(result["session_opening_preparation_path"])
    placeholder = json.loads(Path(result["session_opening_execution_authorization_placeholder_path"]).read_text())
    assert worksheet.is_file()
    assert ROOT not in worksheet.parents
    assert placeholder["decision"] == "HOLD"
    assert placeholder["provider_session_opened"] is False


def test_current_state_preserves_all_operational_locks():
    state = build_current_session_opening_preparation_state(ROOT, *blank_opening_preparation_inputs(ROOT))
    for key in (
        "provider_session_opening_authorized", "provider_login_authorized", "provider_calls_authorized",
        "resource_creation_authorized", "secret_reference_registration_authorized", "build_authorized",
        "deployment_authorized", "provider_session_opened", "provider_login_performed",
        "provider_calls_performed", "resources_created", "secrets_registered", "secrets_created_or_read",
        "build_performed", "deployment_performed", "official_walkthrough_performed",
        "production_manual_live_authorized", "broker_submission_enabled", "real_capital_movement_enabled",
        "direct_vault_upload_enabled",
    ):
        assert state[key] is False
    assert state["live_auto_locked"] is True
