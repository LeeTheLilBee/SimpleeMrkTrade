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
    blank_current_inputs,
    build_completed_execution_preparation_handoff,
    build_controlled_execution_scope_manifest,
    build_current_execution_authorization_state,
    build_execution_authorization_challenge,
    build_execution_authorization_decision,
    build_execution_receipt_contract,
    build_execution_session_preconditions_manifest,
    build_execution_window_and_cost_ceiling_manifest,
    build_inert_controlled_execution_session_plan,
    execution_authorization_decision_template,
    freeze_execution_authorization_record,
    validate_execution_authorization_decision,
    write_execution_authorization_worksheets,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "05eae9021f48a55c06b33a0319baea20f01f67e0"


def _complete_provider_inputs() -> dict:
    payload = provider_input_template()
    payload.update({
        "provider_slug": "managed-host-execution-auth",
        "account_or_team_ref": "simplee-staging-team",
        "deployment_region": "us-east-execution-auth",
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


def _complete_preparation_inputs(handoff: dict) -> dict:
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


@lru_cache(maxsize=1)
def _cached_ready_preparation() -> tuple[dict, dict, dict, dict, dict, dict]:
    provider = _complete_provider_inputs()
    review_owner = _complete_review_owner_decision(provider)
    review = _complete_review_inputs(provider, review_owner)
    review_handoff = build_completed_review_handoff(
        ROOT, provider, review_owner, review
    )
    assert review_handoff["completed_review_ready"] is True
    provisioning = _complete_provisioning_decision(review_handoff)
    authorization_handoff = build_provisioning_authorization_handoff(
        ROOT, provider, review_owner, review, provisioning
    )
    assert authorization_handoff["handoff_ready"] is True
    preparation = _complete_preparation_inputs(authorization_handoff)
    handoff = build_completed_execution_preparation_handoff(
        ROOT, provider, review_owner, review, provisioning, preparation
    )
    assert handoff["completed_execution_preparation_ready"] is True
    return provider, review_owner, review, provisioning, preparation, handoff


def _ready_preparation() -> tuple[dict, dict, dict, dict, dict, dict]:
    return copy.deepcopy(_cached_ready_preparation())


def _complete_execution_authorization(
    handoff: dict,
    provisioning: dict,
    preparation: dict,
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
        "authorized_source_commit_ref": preparation["source_commit_ref"],
        "monthly_cost_ceiling_usd": provisioning["monthly_cost_ceiling_usd"],
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


def test_blank_completed_preparation_handoff_is_held():
    provider, review_owner, review, provisioning, preparation, _ = blank_current_inputs(ROOT)
    handoff = build_completed_execution_preparation_handoff(
        ROOT, provider, review_owner, review, provisioning, preparation
    )
    assert handoff["completed_execution_preparation_ready"] is False
    assert handoff["provider_login_authorized"] is False
    assert handoff["provider_calls_authorized"] is False


def test_complete_preparation_handoff_is_ready_for_decision_only():
    *_, handoff = _ready_preparation()
    assert handoff["completed_execution_preparation_ready"] is True
    assert handoff["preparation_inputs_valid"] is True
    assert handoff["resource_creation_authorized"] is False


def test_execution_challenge_is_bound_to_frozen_preparation_packet():
    *_, handoff = _ready_preparation()
    challenge = build_execution_authorization_challenge(handoff)
    assert challenge["frozen_execution_preparation_packet_hash"] == handoff["frozen_execution_preparation_packet_hash"]
    assert challenge["challenge_id"] in challenge["challenge_phrase"].lower()
    assert challenge["provider_calls_performed"] is False


def test_blank_execution_authorization_template_defaults_to_hold():
    payload = execution_authorization_decision_template()
    assert payload["decision"] == "HOLD"
    assert payload["challenge_ready"] is False
    assert all(value is False for value in payload["authorized_scope"].values())
    assert all(value is False for value in payload["scope_attestations"].values())


def test_bound_template_contains_challenge_without_secrets():
    *_, handoff = _ready_preparation()
    payload = execution_authorization_decision_template(handoff)
    rendered = json.dumps(payload).lower()
    assert payload["challenge_ready"] is True
    assert payload["challenge_id"]
    assert "postgresql://" not in rendered
    assert "-----begin private key-----" not in rendered


def test_blank_decision_fails_closed():
    provider, review_owner, review, provisioning, preparation, handoff = _ready_preparation()
    challenge = build_execution_authorization_challenge(handoff)
    report = validate_execution_authorization_decision(
        execution_authorization_decision_template(handoff),
        handoff=handoff,
        challenge=challenge,
        provisioning_decision=provisioning,
        preparation_inputs=preparation,
    )
    assert report["approval_valid"] is False
    assert report["error_count"] > 0


def test_complete_execution_authorization_validates():
    provider, review_owner, review, provisioning, preparation, handoff = _ready_preparation()
    challenge = build_execution_authorization_challenge(handoff)
    decision = _complete_execution_authorization(handoff, provisioning, preparation)
    report = validate_execution_authorization_decision(
        decision,
        handoff=handoff,
        challenge=challenge,
        provisioning_decision=provisioning,
        preparation_inputs=preparation,
    )
    assert report["approval_valid"] is True
    assert report["error_count"] == 0
    assert report["execution_window_seconds"] == 3600


def test_owner_step_up_receipt_is_required():
    *_, provisioning, preparation, handoff = _ready_preparation()
    challenge = build_execution_authorization_challenge(handoff)
    decision = _complete_execution_authorization(handoff, provisioning, preparation)
    decision["tower_step_up_receipt_ref"] = ""
    report = validate_execution_authorization_decision(
        decision, handoff=handoff, challenge=challenge,
        provisioning_decision=provisioning, preparation_inputs=preparation,
    )
    assert report["approval_valid"] is False
    assert report["checks"]["tower_step_up_receipt_ref_present"] is False


def test_exact_challenge_phrase_is_required():
    *_, provisioning, preparation, handoff = _ready_preparation()
    challenge = build_execution_authorization_challenge(handoff)
    decision = _complete_execution_authorization(handoff, provisioning, preparation)
    decision["challenge_phrase_confirmation"] = "wrong phrase"
    report = validate_execution_authorization_decision(
        decision, handoff=handoff, challenge=challenge,
        provisioning_decision=provisioning, preparation_inputs=preparation,
    )
    assert report["approval_valid"] is False
    assert report["checks"]["challenge_phrase_matches"] is False


def test_frozen_preparation_hash_binding_is_required():
    *_, provisioning, preparation, handoff = _ready_preparation()
    challenge = build_execution_authorization_challenge(handoff)
    decision = _complete_execution_authorization(handoff, provisioning, preparation)
    decision["frozen_execution_preparation_packet_hash"] = "0" * 64
    report = validate_execution_authorization_decision(
        decision, handoff=handoff, challenge=challenge,
        provisioning_decision=provisioning, preparation_inputs=preparation,
    )
    assert report["approval_valid"] is False
    assert report["checks"]["frozen_execution_preparation_packet_hash_matches"] is False


def test_execution_window_must_be_ordered_and_bounded():
    *_, provisioning, preparation, handoff = _ready_preparation()
    challenge = build_execution_authorization_challenge(handoff)
    decision = _complete_execution_authorization(handoff, provisioning, preparation)
    decision["execution_window_expires_at"] = "2026-07-16T20:10:00Z"
    report = validate_execution_authorization_decision(
        decision, handoff=handoff, challenge=challenge,
        provisioning_decision=provisioning, preparation_inputs=preparation,
    )
    assert report["approval_valid"] is False
    assert report["checks"]["execution_window_duration_within_120_minutes"] is False


def test_source_commit_must_match_frozen_preparation():
    *_, provisioning, preparation, handoff = _ready_preparation()
    challenge = build_execution_authorization_challenge(handoff)
    decision = _complete_execution_authorization(handoff, provisioning, preparation)
    decision["authorized_source_commit_ref"] = "f" * 40
    report = validate_execution_authorization_decision(
        decision, handoff=handoff, challenge=challenge,
        provisioning_decision=provisioning, preparation_inputs=preparation,
    )
    assert report["approval_valid"] is False
    assert report["checks"]["authorized_source_commit_matches_preparation"] is False


def test_cost_ceiling_must_match_prior_authorization():
    *_, provisioning, preparation, handoff = _ready_preparation()
    challenge = build_execution_authorization_challenge(handoff)
    decision = _complete_execution_authorization(handoff, provisioning, preparation)
    decision["monthly_cost_ceiling_usd"] = "101.00"
    report = validate_execution_authorization_decision(
        decision, handoff=handoff, challenge=challenge,
        provisioning_decision=provisioning, preparation_inputs=preparation,
    )
    assert report["approval_valid"] is False
    assert report["checks"]["monthly_cost_ceiling_matches_provisioning_authorization"] is False


def test_all_scope_attestations_are_required():
    *_, provisioning, preparation, handoff = _ready_preparation()
    challenge = build_execution_authorization_challenge(handoff)
    decision = _complete_execution_authorization(handoff, provisioning, preparation)
    first = REQUIRED_EXECUTION_SCOPE_ATTESTATIONS[0]
    decision["scope_attestations"][first] = False
    report = validate_execution_authorization_decision(
        decision, handoff=handoff, challenge=challenge,
        provisioning_decision=provisioning, preparation_inputs=preparation,
    )
    assert report["approval_valid"] is False
    assert report["attestation_checks"][first] is False


def test_sensitive_material_is_rejected():
    *_, provisioning, preparation, handoff = _ready_preparation()
    challenge = build_execution_authorization_challenge(handoff)
    decision = _complete_execution_authorization(handoff, provisioning, preparation)
    decision["tower_step_up_receipt_ref"] = "token=not-allowed"
    report = validate_execution_authorization_decision(
        decision, handoff=handoff, challenge=challenge,
        provisioning_decision=provisioning, preparation_inputs=preparation,
    )
    assert report["approval_valid"] is False
    assert report["sensitive_material_detected"] is True


def test_controlled_scope_is_empty_without_approval():
    manifest = build_controlled_execution_scope_manifest(
        validation={"approval_valid": False}
    )
    assert manifest["allowed_future_session_actions"] == []
    assert manifest["provider_login_authorized_for_future_session"] is False
    assert manifest["service_count_ceiling"] == 0


def test_approved_scope_allows_one_inert_service_but_no_build_or_deploy():
    manifest = build_controlled_execution_scope_manifest(
        validation={"approval_valid": True}
    )
    assert manifest["service_count_ceiling"] == 1
    assert manifest["public_ingress_owner"] == "tower"
    assert manifest["observatory_public_ingress_allowed"] is False
    assert manifest["build_authorized"] is False
    assert manifest["deployment_authorized"] is False


def test_execution_window_and_cost_manifest_preserves_zero_external_resources():
    manifest = build_execution_window_and_cost_ceiling_manifest(
        {"execution_window_starts_at": "2026-07-16T16:10:00Z", "execution_window_expires_at": "2026-07-16T17:10:00Z"},
        validation={"approval_valid": True, "execution_window_seconds": 3600, "monthly_cost_ceiling_usd": "100.00"},
    )
    assert manifest["managed_web_service_count_ceiling"] == 1
    assert manifest["database_count_ceiling"] == 0
    assert manifest["object_storage_bucket_count_ceiling"] == 0
    assert manifest["dns_change_count_ceiling"] == 0
    assert manifest["deployment_authorized"] is False


def test_execution_receipt_contract_requires_hash_chain_and_stop_receipt():
    contract = build_execution_receipt_contract()
    assert contract["receipt_hash_chain_required"] is True
    assert "execution_session_stopped_before_build_or_deployment" in contract["required_receipts_in_order"]
    assert contract["secret_values_allowed"] is False
    assert contract["deployment_receipt_allowed"] is False


def test_session_preconditions_contain_fail_closed_stop_conditions():
    manifest = build_execution_session_preconditions_manifest(
        validation={"approval_valid": True}
    )
    rendered = " ".join(manifest["mandatory_stop_conditions"]).lower()
    assert "authorization window" in rendered
    assert "duplicate active staging resource" in rendered
    assert "secret value readback" in rendered
    assert manifest["provider_session_opened"] is False


def test_frozen_execution_authorization_record_is_sanitized():
    provider, review_owner, review, provisioning, preparation, handoff = _ready_preparation()
    decision = _complete_execution_authorization(handoff, provisioning, preparation)
    record = freeze_execution_authorization_record(
        ROOT, provider, review_owner, review, provisioning, preparation, decision
    )
    rendered = json.dumps(record).lower()
    assert record["approval_valid"] is True
    assert record["frozen"] is True
    assert len(record["frozen_execution_authorization_record_hash"]) == 64
    assert "tower-owner-execution" not in rendered
    assert "tower-step-up-execution-receipt" not in rendered
    assert record["provider_calls_performed"] is False


def test_blank_current_state_preserves_prior_hold():
    state = build_current_execution_authorization_state(
        ROOT, *blank_current_inputs(ROOT)
    )
    assert state["closed_through_step"] == 90
    assert state["final_decision"] == "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
    assert state["execution_authorization_valid"] is False
    assert state["blocking_requirement_count"] > 0


def test_ready_preparation_without_execution_decision_is_held():
    provider, review_owner, review, provisioning, preparation, handoff = _ready_preparation()
    state = build_current_execution_authorization_state(
        ROOT, provider, review_owner, review, provisioning, preparation,
        execution_authorization_decision_template(handoff),
    )
    assert state["final_decision"] == "NO_GO_HOLD_PROVIDER_PROVISIONING_EXECUTION_AUTHORIZATION_REQUIRED"
    assert state["ready_for_separate_controlled_provider_provisioning_execution_session"] is False


def test_owner_rejection_is_fail_closed():
    provider, review_owner, review, provisioning, preparation, handoff = _ready_preparation()
    decision = execution_authorization_decision_template(handoff)
    decision["decision"] = "REJECT"
    state = build_current_execution_authorization_state(
        ROOT, provider, review_owner, review, provisioning, preparation, decision
    )
    assert state["final_decision"] == "NO_GO_OWNER_REJECTED_PROVIDER_PROVISIONING_EXECUTION_AUTHORIZATION"
    assert state["provider_calls_authorized_for_future_session"] is False


def test_complete_approval_opens_only_separate_controlled_session():
    provider, review_owner, review, provisioning, preparation, handoff = _ready_preparation()
    decision = _complete_execution_authorization(handoff, provisioning, preparation)
    state = build_current_execution_authorization_state(
        ROOT, provider, review_owner, review, provisioning, preparation, decision
    )
    assert state["final_decision"] == "AUTHORIZED_FOR_SEPARATE_CONTROLLED_PROVIDER_PROVISIONING_EXECUTION_SESSION"
    assert state["execution_authorization_valid"] is True
    assert state["ready_for_separate_controlled_provider_provisioning_execution_session"] is True
    assert state["provider_login_performed"] is False
    assert state["provider_calls_performed"] is False
    assert state["resources_created"] is False
    assert state["deployment_performed"] is False


def test_inert_controlled_session_plan_invokes_nothing():
    plan = build_inert_controlled_execution_session_plan(
        ROOT, *blank_current_inputs(ROOT)
    )
    assert plan["provider_cli_commands"] == []
    assert plan["provider_api_requests"] == []
    assert plan["shell_commands"] == []
    assert plan["browser_actions"] == []
    assert plan["dry_run_only"] is True
    assert plan["provider_calls_performed"] is False


def test_current_state_preserves_all_operational_locks():
    state = build_current_execution_authorization_state(
        ROOT, *blank_current_inputs(ROOT)
    )
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


def test_execution_authorization_worksheets_are_outside_repo(tmp_path):
    output = tmp_path / "execution-authorization-worksheets"
    result = write_execution_authorization_worksheets(
        output, repository_root=ROOT
    )
    assert Path(result["execution_authorization_decision_path"]).is_file()
    assert Path(result["controlled_execution_session_placeholder_path"]).is_file()
    assert Path(result["manifest_path"]).is_file()
    assert ROOT not in output.parents
    rendered = "\n".join(
        path.read_text(encoding="utf-8")
        for path in output.iterdir() if path.is_file()
    ).lower()
    assert "postgresql://" not in rendered
    assert "-----begin private key-----" not in rendered


def test_controlled_session_placeholder_defaults_to_hold(tmp_path):
    result = write_execution_authorization_worksheets(
        tmp_path / "worksheets", repository_root=ROOT
    )
    payload = json.loads(
        Path(result["controlled_execution_session_placeholder_path"]).read_text()
    )
    assert payload["decision"] == "HOLD"
    assert payload["provider_session_opened"] is False
    assert payload["resources_created"] is False
    assert payload["deployment_performed"] is False


def test_worksheet_manifest_reports_no_actions(tmp_path):
    result = write_execution_authorization_worksheets(
        tmp_path / "worksheets", repository_root=ROOT
    )
    payload = json.loads(Path(result["manifest_path"]).read_text())
    assert payload["contains_secret_values"] is False
    assert payload["provider_session_opened"] is False
    assert payload["provider_login_performed"] is False
    assert payload["provider_calls_performed"] is False
    assert payload["resources_created"] is False
    assert payload["secrets_registered"] is False
    assert payload["build_performed"] is False
    assert payload["deployment_performed"] is False
