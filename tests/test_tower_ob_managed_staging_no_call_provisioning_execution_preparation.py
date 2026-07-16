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
    AUTHORIZE_DECISION,
    REQUIRED_SCOPE_ATTESTATIONS,
    build_completed_review_handoff,
    build_provisioning_authorization_challenge,
    provisioning_authorization_decision_template,
)
from tower.tower_ob_managed_staging_no_call_provisioning_execution_preparation import (
    REQUIRED_PREPARATION_ATTESTATIONS,
    blank_current_inputs,
    build_cost_idempotency_guardrail,
    build_current_execution_preparation_state,
    build_execution_preparation_decision,
    build_health_logging_control_plan,
    build_inert_execution_command_manifest,
    build_no_call_execution_rehearsal,
    build_non_secret_environment_registration_plan,
    build_one_service_execution_manifest,
    build_provider_console_session_plan,
    build_provisioning_authorization_handoff,
    build_rollback_and_stop_condition_plan,
    build_secret_reference_registration_plan,
    execution_preparation_input_template,
    freeze_execution_preparation_packet,
    validate_execution_preparation_inputs,
    write_execution_preparation_worksheets,
)

ROOT = Path(__file__).resolve().parents[1]


def _complete_provider_inputs() -> dict:
    payload = provider_input_template()
    payload.update({
        "provider_slug": "managed-host-execution-prep",
        "account_or_team_ref": "simplee-staging-team",
        "deployment_region": "us-east-execution-prep",
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


def _ready_review() -> tuple[dict, dict, dict, dict]:
    provider_inputs = _complete_provider_inputs()
    review_owner = _complete_review_owner_decision(provider_inputs)
    review_inputs = _complete_review_inputs(provider_inputs, review_owner)
    handoff = build_completed_review_handoff(
        ROOT, provider_inputs, review_owner, review_inputs
    )
    assert handoff["completed_review_ready"] is True
    return provider_inputs, review_owner, review_inputs, handoff


def _complete_provisioning_decision(handoff: dict) -> dict:
    challenge = build_provisioning_authorization_challenge(handoff)
    payload = provisioning_authorization_decision_template(handoff)
    payload.update({
        "decision": AUTHORIZE_DECISION,
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


@lru_cache(maxsize=1)
def _cached_ready_authorization() -> tuple[dict, dict, dict, dict, dict]:
    provider, review_owner, review, review_handoff = _ready_review()
    provisioning = _complete_provisioning_decision(review_handoff)
    handoff = build_provisioning_authorization_handoff(
        ROOT, provider, review_owner, review, provisioning
    )
    assert handoff["handoff_ready"] is True
    return provider, review_owner, review, provisioning, handoff


def _ready_authorization() -> tuple[dict, dict, dict, dict, dict]:
    return copy.deepcopy(_cached_ready_authorization())


def _complete_preparation_inputs(handoff: dict) -> dict:
    payload = execution_preparation_input_template(handoff)
    payload.update({
        "provider_console_session_ref": "prep/provider-console-session",
        "provider_service_form_ref": "prep/one-service-form",
        "source_commit_ref": "commit/05eae9021f48a55c06b33a0319baea20f01f67e0",
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


def test_blank_authorization_handoff_is_held():
    provider, review_owner, review, provisioning, _ = blank_current_inputs(ROOT)
    handoff = build_provisioning_authorization_handoff(
        ROOT, provider, review_owner, review, provisioning
    )
    assert handoff["handoff_ready"] is False
    assert handoff["provider_login_authorized"] is False
    assert handoff["provider_calls_authorized"] is False


def test_complete_authorization_handoff_is_ready_for_preparation_only():
    *_, handoff = _ready_authorization()
    assert handoff["provisioning_authorization_valid"] is True
    assert handoff["handoff_ready"] is True
    assert handoff["resource_creation_authorized"] is False


def test_preparation_template_contains_no_secret_values():
    payload = execution_preparation_input_template()
    rendered = json.dumps(payload).lower()
    assert "postgresql://" not in rendered
    assert "-----begin private key-----" not in rendered
    assert all(value is False for value in payload["attestations"].values())


def test_blank_preparation_inputs_fail_closed():
    *_, handoff = _ready_authorization()
    payload = execution_preparation_input_template(handoff)
    report = validate_execution_preparation_inputs(payload, handoff=handoff)
    assert report["valid"] is False
    assert report["error_count"] > 0


def test_complete_preparation_inputs_validate():
    *_, handoff = _ready_authorization()
    payload = _complete_preparation_inputs(handoff)
    report = validate_execution_preparation_inputs(payload, handoff=handoff)
    assert report["valid"] is True
    assert report["error_count"] == 0
    assert report["completed_attestation_count"] == len(REQUIRED_PREPARATION_ATTESTATIONS)


def test_sensitive_material_is_rejected():
    *_, handoff = _ready_authorization()
    payload = _complete_preparation_inputs(handoff)
    payload["provider_service_form_ref"] = "token=not-allowed"
    report = validate_execution_preparation_inputs(payload, handoff=handoff)
    assert report["valid"] is False
    assert report["sensitive_material_detected"] is True


def test_authorization_hash_binding_is_required():
    *_, handoff = _ready_authorization()
    payload = _complete_preparation_inputs(handoff)
    payload["provisioning_authorization_record_hash"] = "0" * 64
    report = validate_execution_preparation_inputs(payload, handoff=handoff)
    assert report["valid"] is False
    assert any(e["code"] == "provisioning_authorization_hash_mismatch" for e in report["errors"])


def test_handoff_hash_binding_is_required():
    *_, handoff = _ready_authorization()
    payload = _complete_preparation_inputs(handoff)
    payload["authorization_handoff_hash"] = "0" * 64
    report = validate_execution_preparation_inputs(payload, handoff=handoff)
    assert report["valid"] is False
    assert any(e["code"] == "authorization_handoff_hash_mismatch" for e in report["errors"])


def test_provider_console_plan_is_manual_and_inert():
    *_, handoff = _ready_authorization()
    plan = build_provider_console_session_plan(handoff)
    assert plan["session_mode"] == "manual_owner_controlled_future_execution_only"
    assert plan["login_performed"] is False
    assert plan["provider_cli_allowed"] is False
    assert plan["provider_api_allowed"] is False


def test_one_service_manifest_preserves_tower_front_door():
    manifest = build_one_service_execution_manifest()
    assert manifest["service_count_ceiling"] == 1
    assert manifest["runtime_target"] == "web.managed_staging:app"
    assert manifest["public_ingress_owner"] == "tower"
    assert manifest["observatory_public_ingress_allowed"] is False


def test_one_service_manifest_creates_nothing():
    manifest = build_one_service_execution_manifest()
    assert manifest["database_creation_allowed"] is False
    assert manifest["object_storage_creation_allowed"] is False
    assert manifest["dns_changes_allowed"] is False
    assert manifest["resource_created"] is False


def test_environment_registration_plan_contains_names_not_values():
    plan = build_non_secret_environment_registration_plan()
    rendered = json.dumps(plan)
    assert "SIMPLEE_ENVIRONMENT" in rendered
    assert plan["environment_values_recorded"] is False
    assert plan["registration_performed"] is False


def test_secret_reference_plan_prohibits_readback_and_git():
    plan = build_secret_reference_registration_plan()
    assert "TOWER_SESSION_SECRET" in plan["secret_environment_names"]
    assert plan["secret_values_recorded"] is False
    assert plan["secret_readback_allowed"] is False
    assert plan["git_storage_allowed"] is False


def test_health_logging_plan_requires_manual_control():
    plan = build_health_logging_control_plan()
    assert plan["health_check_path"] == "/tower/healthz"
    assert plan["deployment_logs_required"] is True
    assert plan["access_logs_required"] is True
    assert plan["manual_deployment_control_required"] is True
    assert plan["automatic_deployment_allowed"] is False


def test_rollback_plan_contains_fail_closed_stop_conditions():
    plan = build_rollback_and_stop_condition_plan()
    rendered = " ".join(plan["stop_conditions"]).lower()
    assert "more than one web service" in rendered
    assert "secret value readback" in rendered
    assert plan["rollback_executed"] is False


def test_cost_guardrail_binds_cost_and_idempotency():
    provider, review_owner, review, provisioning, _ = _ready_authorization()
    record = build_cost_idempotency_guardrail(provisioning)
    assert record["service_count_ceiling"] == 1
    assert record["monthly_cost_ceiling_usd"] == "100.00"
    assert record["duplicate_service_creation_allowed"] is False
    assert len(record["idempotency_key_sha256"]) == 64


def test_execution_command_manifest_contains_no_commands():
    manifest = build_inert_execution_command_manifest()
    assert manifest["provider_cli_commands"] == []
    assert manifest["provider_api_requests"] == []
    assert manifest["shell_commands"] == []
    assert manifest["browser_actions"] == []
    assert manifest["dry_run_only"] is True


def test_frozen_execution_preparation_packet_is_inert():
    provider, review_owner, review, provisioning, handoff = _ready_authorization()
    preparation = _complete_preparation_inputs(handoff)
    packet = freeze_execution_preparation_packet(
        ROOT, provider, review_owner, review, provisioning, preparation
    )
    assert packet["preparation_inputs_valid"] is True
    assert packet["frozen"] is True
    assert len(packet["frozen_execution_preparation_packet_hash"]) == 64
    assert packet["provider_calls_authorized"] is False
    assert packet["resources_created"] is False


def test_blank_current_decision_remains_provider_input_hold():
    provider, review_owner, review, provisioning, preparation = blank_current_inputs(ROOT)
    decision = build_execution_preparation_decision(
        ROOT, provider, review_owner, review, provisioning, preparation
    )
    assert decision["final_decision"] == "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
    assert decision["ready_for_separate_provider_provisioning_execution_authorization"] is False


def test_authorized_without_preparation_evidence_remains_held():
    provider, review_owner, review, provisioning, handoff = _ready_authorization()
    decision = build_execution_preparation_decision(
        ROOT, provider, review_owner, review, provisioning,
        execution_preparation_input_template(handoff),
    )
    assert decision["final_decision"] == "NO_GO_HOLD_NO_CALL_EXECUTION_PREPARATION_EVIDENCE_REQUIRED"


def test_complete_preparation_opens_only_separate_execution_authorization():
    provider, review_owner, review, provisioning, handoff = _ready_authorization()
    preparation = _complete_preparation_inputs(handoff)
    decision = build_execution_preparation_decision(
        ROOT, provider, review_owner, review, provisioning, preparation
    )
    assert decision["final_decision"] == "READY_FOR_SEPARATE_PROVIDER_PROVISIONING_EXECUTION_AUTHORIZATION"
    assert decision["ready_for_separate_provider_provisioning_execution_authorization"] is True
    assert decision["provider_login_authorized"] is False
    assert decision["provider_calls_authorized"] is False
    assert decision["deployment_authorized"] is False


def test_no_call_rehearsal_invokes_nothing():
    provider, review_owner, review, provisioning, preparation = blank_current_inputs(ROOT)
    rehearsal = build_no_call_execution_rehearsal(
        ROOT, provider, review_owner, review, provisioning, preparation
    )
    assert rehearsal["dry_run_only"] is True
    assert rehearsal["shell_invoked"] is False
    assert rehearsal["browser_invoked"] is False
    assert rehearsal["provider_api_invoked"] is False
    assert rehearsal["provider_calls_performed"] is False


def test_current_blank_state_closes_step_80_fail_closed():
    inputs = blank_current_inputs(ROOT)
    state = build_current_execution_preparation_state(ROOT, *inputs)
    assert state["closed_through_step"] == 80
    assert state["closed_layer"] == "MANAGED_STAGING_NO_CALL_PROVIDER_PROVISIONING_EXECUTION_PREPARATION"
    assert state["final_decision"] == "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
    assert state["blocking_requirement_count"] > 0


def test_current_complete_state_is_ready_for_separate_authorization_only():
    provider, review_owner, review, provisioning, handoff = _ready_authorization()
    preparation = _complete_preparation_inputs(handoff)
    state = build_current_execution_preparation_state(
        ROOT, provider, review_owner, review, provisioning, preparation
    )
    assert state["preparation_inputs_valid"] is True
    assert state["ready_for_separate_provider_provisioning_execution_authorization"] is True
    assert state["provider_login_authorized"] is False
    assert state["resources_created"] is False


def test_current_state_preserves_all_operational_locks():
    state = build_current_execution_preparation_state(ROOT, *blank_current_inputs(ROOT))
    assert state["database_creation_authorized"] is False
    assert state["object_storage_creation_authorized"] is False
    assert state["dns_changes_authorized"] is False
    assert state["build_authorized"] is False
    assert state["deployment_authorized"] is False
    assert state["official_walkthrough_performed"] is False
    assert state["production_manual_live_authorized"] is False
    assert state["broker_submission_enabled"] is False
    assert state["real_capital_movement_enabled"] is False
    assert state["direct_vault_upload_enabled"] is False
    assert state["live_auto_locked"] is True


def test_preparation_worksheets_are_written_outside_repo(tmp_path):
    output = tmp_path / "execution-preparation-worksheets"
    result = write_execution_preparation_worksheets(
        output, repository_root=ROOT
    )
    assert Path(result["execution_preparation_path"]).is_file()
    assert Path(result["execution_authorization_placeholder_path"]).is_file()
    assert Path(result["manifest_path"]).is_file()
    assert ROOT not in output.parents
    rendered = "\n".join(
        path.read_text(encoding="utf-8")
        for path in output.iterdir() if path.is_file()
    ).lower()
    assert "postgresql://" not in rendered
    assert "-----begin private key-----" not in rendered


def test_execution_authorization_placeholder_defaults_to_hold(tmp_path):
    result = write_execution_preparation_worksheets(
        tmp_path / "worksheets", repository_root=ROOT
    )
    payload = json.loads(
        Path(result["execution_authorization_placeholder_path"]).read_text()
    )
    assert payload["decision"] == "HOLD"
    assert payload["provider_login_authorized"] is False
    assert payload["resource_creation_authorized"] is False


def test_worksheet_manifest_reports_no_actions(tmp_path):
    result = write_execution_preparation_worksheets(
        tmp_path / "worksheets", repository_root=ROOT
    )
    payload = json.loads(Path(result["manifest_path"]).read_text())
    assert payload["contains_secret_values"] is False
    assert payload["provider_login_performed"] is False
    assert payload["provider_calls_performed"] is False
    assert payload["resources_created"] is False
    assert payload["deployment_performed"] is False
