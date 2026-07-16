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
SOURCE_COMMIT = "05eae9021f48a55c06b33a0319baea20f01f67e0"


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


def test_blank_execution_authorization_handoff_is_held():
    *inputs, _ = blank_current_inputs(ROOT)
    handoff = build_execution_authorization_handoff(ROOT, *inputs)
    assert handoff["execution_authorization_ready"] is False
    assert handoff["provider_session_opened"] is False


def test_complete_execution_authorization_handoff_is_ready_for_preparation_only():
    *_, handoff = _ready_execution_authorization()
    assert handoff["execution_authorization_ready"] is True
    assert handoff["provider_login_authorized_for_later_session"] is True
    assert handoff["provider_session_opened"] is False


def test_session_preparation_template_contains_no_secret_values():
    *_, handoff = _ready_execution_authorization()
    payload = controlled_session_preparation_input_template(handoff)
    rendered = json.dumps(payload).lower()
    assert "ghp_" not in rendered
    assert "-----begin" not in rendered
    assert payload["packet_type"].endswith("session_preparation_inputs")


def test_blank_session_preparation_inputs_fail_closed():
    *_, handoff = _ready_execution_authorization()
    payload = controlled_session_preparation_input_template(handoff)
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    assert report["valid"] is False
    assert report["errors"]


def test_complete_session_preparation_inputs_validate():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    assert report["valid"] is True
    assert report["errors"] == []


def test_sensitive_material_is_rejected():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    payload["stop_conditions_review_ref"] = "password=hunter2"
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    assert report["valid"] is False
    assert report["checks"]["contains_sensitive_material"] is True


def test_frozen_execution_authorization_hash_binding_is_required():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    payload["frozen_execution_authorization_record_hash"] = "0" * 64
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    assert report["valid"] is False


def test_execution_authorization_decision_hash_binding_is_required():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    payload["execution_authorization_decision_hash"] = "1" * 64
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    assert report["valid"] is False


def test_authorized_source_commit_binding_is_required():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    payload["authorized_source_commit_ref"] = "commit/" + "2" * 40
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    assert report["valid"] is False


def test_session_window_must_remain_inside_authorization_window():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    payload["session_window_expires_at"] = "2026-07-16T18:10:00Z"
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    assert report["valid"] is False


def test_owner_execution_session_receipt_is_required():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    payload["owner_execution_session_receipt_ref"] = ""
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    assert report["valid"] is False


def test_all_session_preparation_attestations_are_required():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    first = REQUIRED_SESSION_PREPARATION_ATTESTATIONS[0]
    payload["attestations"][first] = False
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    assert report["valid"] is False


def test_provider_session_identity_binding_records_fingerprints_only():
    provider, *rest = _ready_execution_authorization()
    handoff = rest[-1]
    payload = _complete_session_preparation(handoff)
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    binding = build_provider_session_identity_binding(
        provider, payload, validation=report
    )
    assert binding["binding_valid"] is True
    assert binding["provider_slug_sha256"]
    assert "managed-host-session-preparation" not in json.dumps(binding)
    assert binding["raw_secret_values_recorded"] is False


def test_duplicate_resource_lookup_preflight_is_inert():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    plan = build_duplicate_resource_lookup_preflight(validation=report)
    assert plan["ready_for_later_manual_lookup"] is True
    assert plan["provider_api_requests"] == []
    assert plan["browser_actions"] == []
    assert plan["lookup_performed"] is False


def test_one_service_request_preserves_tower_front_door():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    request = build_one_service_shell_request(payload, validation=report)
    assert request["runtime_target"] == "web.managed_staging:app"
    assert request["public_ingress"] == "tower_only"
    assert request["resource_ceiling"]["managed_web_service_shells"] == 1


def test_one_service_request_blocks_build_deploy_database_storage_and_dns():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    request = build_one_service_shell_request(payload, validation=report)
    assert request["resource_ceiling"]["databases"] == 0
    assert request["resource_ceiling"]["object_storage_buckets"] == 0
    assert request["resource_ceiling"]["dns_records"] == 0
    assert request["resource_ceiling"]["builds"] == 0
    assert request["resource_ceiling"]["deployments"] == 0


def test_environment_sequence_contains_names_not_values():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    plan = build_environment_and_secret_registration_sequence(
        validation=report
    )
    assert set(plan["non_secret_environment_names"]) == set(
        NON_SECRET_ENVIRONMENT_NAMES
    )
    assert plan["environment_values"] == {}


def test_secret_reference_sequence_prohibits_readback_and_git_values():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    plan = build_environment_and_secret_registration_sequence(
        validation=report
    )
    assert set(plan["secret_reference_names"]) == set(
        SECRET_REFERENCE_NAMES
    )
    assert plan["secret_values"] == {}
    assert plan["secret_readback_allowed"] is False
    assert plan["secret_values_allowed_in_git"] is False


def test_operational_control_rehearsal_invokes_nothing():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    rehearsal = build_operational_control_rehearsal(validation=report)
    assert rehearsal["provider_api_requests"] == []
    assert rehearsal["browser_actions"] == []
    assert rehearsal["build_performed"] is False
    assert rehearsal["deployment_performed"] is False


def test_cost_ceiling_is_hash_bound_in_frozen_packet():
    (
        provider,
        review_owner,
        review,
        provisioning,
        execution_preparation,
        execution_authorization,
        handoff,
    ) = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    frozen = freeze_controlled_session_preparation_packet(
        ROOT,
        provider,
        review_owner,
        review,
        provisioning,
        execution_preparation,
        execution_authorization,
        payload,
    )
    assert frozen["preparation_valid"] is True
    assert frozen["authorized_source_commit_sha256"]
    assert frozen["raw_secret_values_recorded"] is False


def test_receipt_chain_requires_stop_before_build_and_deployment():
    *_, handoff = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    report = validate_controlled_session_preparation_inputs(
        payload, handoff=handoff
    )
    contract = build_receipt_chain_and_stop_gate(validation=report)
    assert contract["hash_chain_required"] is True
    assert contract["mandatory_stop_receipt"] is True
    assert "stop_before_build_and_deployment_receipt" in contract[
        "required_receipt_order"
    ]
    assert contract["build_receipt_allowed"] is False


def test_frozen_session_preparation_packet_is_sanitized():
    (
        provider,
        review_owner,
        review,
        provisioning,
        execution_preparation,
        execution_authorization,
        handoff,
    ) = _ready_execution_authorization()
    payload = _complete_session_preparation(handoff)
    frozen = freeze_controlled_session_preparation_packet(
        ROOT,
        provider,
        review_owner,
        review,
        provisioning,
        execution_preparation,
        execution_authorization,
        payload,
    )
    rendered = json.dumps(frozen)
    assert frozen["frozen"] is True
    assert frozen["raw_provider_values_recorded"] is False
    assert provider["provider_slug"] not in rendered
    assert payload["prepared_by"] not in rendered


def test_blank_current_state_preserves_prior_hold():
    inputs = blank_current_inputs(ROOT)
    state = build_current_controlled_session_preparation_state(
        ROOT, *inputs
    )
    assert state["final_decision"] == (
        "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
    )
    assert state["provider_session_opened"] is False


def test_authorized_without_session_preparation_evidence_is_held():
    *inputs, handoff = _ready_execution_authorization()
    blank = controlled_session_preparation_input_template(handoff)
    state = build_current_controlled_session_preparation_state(
        ROOT, *inputs, blank
    )
    assert state["execution_authorization_ready"] is True
    assert state["session_preparation_inputs_valid"] is False
    assert state["final_decision"] == (
        "NO_GO_HOLD_CONTROLLED_SESSION_PREPARATION_REQUIRED"
    )


def test_complete_session_preparation_opens_only_separate_authorization():
    *inputs, handoff = _ready_execution_authorization()
    preparation = _complete_session_preparation(handoff)
    decision = build_controlled_session_preparation_decision(
        ROOT, *inputs, preparation
    )
    assert decision["session_preparation_valid"] is True
    assert decision[
        "ready_for_separate_controlled_provider_session_opening_authorization"
    ] is True
    assert decision["provider_session_opening_authorized"] is False
    assert decision["final_decision"] == READY_DECISION


def test_inert_session_opening_authorization_plan_invokes_nothing():
    *inputs, handoff = _ready_execution_authorization()
    preparation = _complete_session_preparation(handoff)
    plan = build_inert_session_opening_authorization_plan(
        ROOT, *inputs, preparation
    )
    assert plan["ready_for_later_separate_authorization"] is True
    assert plan["provider_cli_commands"] == []
    assert plan["provider_api_requests"] == []
    assert plan["browser_actions"] == []
    assert plan["provider_session_opened"] is False


def test_current_blank_state_closes_step_100_fail_closed():
    inputs = blank_current_inputs(ROOT)
    state = build_current_controlled_session_preparation_state(
        ROOT, *inputs
    )
    assert state["closed_through_step"] == 100
    assert state["closed_layer"].endswith("SESSION_PREPARATION")
    assert state["ready_for_separate_controlled_provider_session_opening_authorization"] is False


def test_current_complete_state_is_ready_for_separate_authorization_only():
    *inputs, handoff = _ready_execution_authorization()
    preparation = _complete_session_preparation(handoff)
    state = build_current_controlled_session_preparation_state(
        ROOT, *inputs, preparation
    )
    assert state["session_preparation_inputs_valid"] is True
    assert state[
        "ready_for_separate_controlled_provider_session_opening_authorization"
    ] is True
    assert state["provider_session_opening_authorized"] is False
    assert state["provider_calls_authorized"] is False


def test_current_state_preserves_all_operational_locks():
    *inputs, handoff = _ready_execution_authorization()
    preparation = _complete_session_preparation(handoff)
    state = build_current_controlled_session_preparation_state(
        ROOT, *inputs, preparation
    )
    assert state["database_creation_authorized"] is False
    assert state["object_storage_creation_authorized"] is False
    assert state["dns_changes_authorized"] is False
    assert state["build_authorized"] is False
    assert state["deployment_authorized"] is False
    assert state["production_manual_live_authorized"] is False
    assert state["broker_submission_enabled"] is False
    assert state["real_capital_movement_enabled"] is False
    assert state["direct_vault_upload_enabled"] is False
    assert state["live_auto_locked"] is True


def test_session_preparation_worksheets_are_written_outside_repo(tmp_path):
    provider, review_owner, review, provisioning, execution_preparation, execution_authorization, _ = (
        blank_current_inputs(ROOT)
    )
    result = write_controlled_session_preparation_worksheets(
        tmp_path,
        repository_root=ROOT,
        provider_inputs=provider,
        provider_review_owner_decision=review_owner,
        review_inputs=review,
        provisioning_decision=provisioning,
        execution_preparation_inputs=execution_preparation,
        execution_authorization_decision=execution_authorization,
    )
    assert Path(result["controlled_session_preparation_path"]).is_file()
    assert Path(result["session_opening_authorization_placeholder_path"]).is_file()
    assert Path(result["manifest_path"]).is_file()


def test_session_opening_placeholder_defaults_to_hold(tmp_path):
    provider, review_owner, review, provisioning, execution_preparation, execution_authorization, _ = (
        blank_current_inputs(ROOT)
    )
    result = write_controlled_session_preparation_worksheets(
        tmp_path,
        repository_root=ROOT,
        provider_inputs=provider,
        provider_review_owner_decision=review_owner,
        review_inputs=review,
        provisioning_decision=provisioning,
        execution_preparation_inputs=execution_preparation,
        execution_authorization_decision=execution_authorization,
    )
    placeholder = json.loads(
        Path(result["session_opening_authorization_placeholder_path"]).read_text()
    )
    assert placeholder["decision"] == "HOLD"
    assert placeholder["provider_session_opening_authorized"] is False
    assert placeholder["build_authorized"] is False
    assert placeholder["deployment_authorized"] is False


def test_worksheet_manifest_reports_no_actions(tmp_path):
    provider, review_owner, review, provisioning, execution_preparation, execution_authorization, _ = (
        blank_current_inputs(ROOT)
    )
    result = write_controlled_session_preparation_worksheets(
        tmp_path,
        repository_root=ROOT,
        provider_inputs=provider,
        provider_review_owner_decision=review_owner,
        review_inputs=review,
        provisioning_decision=provisioning,
        execution_preparation_inputs=execution_preparation,
        execution_authorization_decision=execution_authorization,
    )
    manifest = json.loads(Path(result["manifest_path"]).read_text())
    assert manifest["contains_secret_values"] is False
    assert manifest["provider_session_opened"] is False
    assert manifest["provider_calls_performed"] is False
    assert manifest["resources_created"] is False
    assert manifest["deployment_performed"] is False
