from __future__ import annotations

import json
from pathlib import Path

from tower.tower_ob_managed_staging_no_call_provisioning_review import (
    REQUIRED_REVIEW_ATTESTATIONS,
    build_authorization_handoff,
    no_call_review_input_template,
)
from tower.tower_ob_managed_staging_provider_authorization import (
    REQUIRED_CAPABILITIES,
    build_owner_authorization_challenge,
    freeze_provider_authorization_packet,
    provider_input_template,
)
from tower.tower_ob_managed_staging_provider_provisioning_authorization import (
    AUTHORIZE_DECISION,
    HOLD_DECISION,
    REJECT_DECISION,
    REQUIRED_SCOPE_ATTESTATIONS,
    blank_current_inputs,
    build_completed_review_handoff,
    build_current_provisioning_authorization_state,
    build_execution_preconditions_manifest,
    build_no_call_execution_preparation_plan,
    build_provider_action_scope_manifest,
    build_provisioning_authorization_challenge,
    build_provisioning_authorization_decision,
    build_resource_and_cost_ceiling_manifest,
    build_secret_custody_authorization_manifest,
    freeze_provisioning_authorization_record,
    provisioning_authorization_decision_template,
    validate_provisioning_authorization_decision,
    write_provisioning_authorization_worksheets,
)

ROOT = Path(__file__).resolve().parents[1]


def _complete_provider_inputs() -> dict:
    payload = provider_input_template()
    payload.update({
        "provider_slug": "managed-host-authorization",
        "account_or_team_ref": "simplee-staging-team",
        "deployment_region": "us-east-authorization",
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


def _complete_review_inputs(
    provider_inputs: dict,
    owner_decision: dict,
) -> dict:
    handoff = build_authorization_handoff(
        ROOT,
        provider_inputs,
        owner_decision,
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
        ROOT,
        provider_inputs,
        review_owner,
        review_inputs,
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


def test_completed_review_handoff_blank_is_held():
    provider, review_owner, review, _ = blank_current_inputs(ROOT)
    handoff = build_completed_review_handoff(
        ROOT, provider, review_owner, review
    )
    assert handoff["completed_review_ready"] is False
    assert handoff["provider_calls_authorized"] is False
    assert handoff["resources_created"] is False


def test_completed_review_handoff_binds_frozen_hashes():
    _, _, _, handoff = _ready_review()
    assert handoff["completed_review_ready"] is True
    assert len(handoff["frozen_review_packet_hash"]) == 64
    assert len(handoff["review_decision_hash"]) == 64
    assert len(handoff["handoff_hash"]) == 64


def test_authorization_challenge_is_review_packet_bound():
    _, _, _, handoff = _ready_review()
    challenge = build_provisioning_authorization_challenge(handoff)
    assert challenge["frozen_review_packet_hash"] == handoff[
        "frozen_review_packet_hash"
    ]
    assert "AUTHORIZE TOWER OB STAGING" in challenge["challenge_phrase"]
    assert challenge["provider_calls_performed"] is False


def test_blank_template_defaults_to_hold():
    template = provisioning_authorization_decision_template()
    assert template["decision"] == HOLD_DECISION
    assert template["challenge_ready"] is False
    assert template["monthly_cost_ceiling_usd"] == ""
    assert all(
        value is False for value in template["authorized_scope"].values()
    )


def test_bound_template_contains_challenge_without_secrets():
    _, _, _, handoff = _ready_review()
    template = provisioning_authorization_decision_template(handoff)
    rendered = json.dumps(template).lower()
    assert template["challenge_ready"] is True
    assert template["challenge_id"]
    assert "postgresql://" not in rendered
    assert "-----begin private key-----" not in rendered


def test_blank_decision_fails_closed():
    _, _, _, handoff = _ready_review()
    challenge = build_provisioning_authorization_challenge(handoff)
    template = provisioning_authorization_decision_template(handoff)
    report = validate_provisioning_authorization_decision(
        template,
        handoff=handoff,
        challenge=challenge,
    )
    assert report["approval_valid"] is False
    assert report["error_count"] > 0


def test_complete_decision_validates():
    _, _, _, handoff = _ready_review()
    challenge = build_provisioning_authorization_challenge(handoff)
    decision = _complete_provisioning_decision(handoff)
    report = validate_provisioning_authorization_decision(
        decision,
        handoff=handoff,
        challenge=challenge,
    )
    assert report["approval_valid"] is True
    assert report["error_count"] == 0
    assert report["monthly_cost_ceiling_usd"] == "100.00"


def test_step_up_receipt_is_required():
    _, _, _, handoff = _ready_review()
    challenge = build_provisioning_authorization_challenge(handoff)
    decision = _complete_provisioning_decision(handoff)
    decision["tower_step_up_receipt_ref"] = ""
    report = validate_provisioning_authorization_decision(
        decision,
        handoff=handoff,
        challenge=challenge,
    )
    assert report["approval_valid"] is False
    assert report["checks"]["tower_step_up_receipt_ref_present"] is False


def test_exact_challenge_phrase_is_required():
    _, _, _, handoff = _ready_review()
    challenge = build_provisioning_authorization_challenge(handoff)
    decision = _complete_provisioning_decision(handoff)
    decision["challenge_phrase_confirmation"] = "wrong"
    report = validate_provisioning_authorization_decision(
        decision,
        handoff=handoff,
        challenge=challenge,
    )
    assert report["approval_valid"] is False
    assert report["checks"]["challenge_phrase_matches"] is False


def test_review_packet_hash_binding_is_required():
    _, _, _, handoff = _ready_review()
    challenge = build_provisioning_authorization_challenge(handoff)
    decision = _complete_provisioning_decision(handoff)
    decision["frozen_review_packet_hash"] = "0" * 64
    report = validate_provisioning_authorization_decision(
        decision,
        handoff=handoff,
        challenge=challenge,
    )
    assert report["approval_valid"] is False
    assert report["checks"]["frozen_review_packet_hash_matches"] is False


def test_authorization_window_must_be_ordered():
    _, _, _, handoff = _ready_review()
    challenge = build_provisioning_authorization_challenge(handoff)
    decision = _complete_provisioning_decision(handoff)
    decision["authorization_expires_at"] = decision["decided_at"]
    report = validate_provisioning_authorization_decision(
        decision,
        handoff=handoff,
        challenge=challenge,
    )
    assert report["approval_valid"] is False
    assert report["checks"]["authorization_window_ordered"] is False


def test_cost_ceiling_is_required_and_bounded():
    _, _, _, handoff = _ready_review()
    challenge = build_provisioning_authorization_challenge(handoff)
    decision = _complete_provisioning_decision(handoff)
    decision["monthly_cost_ceiling_usd"] = "10001"
    report = validate_provisioning_authorization_decision(
        decision,
        handoff=handoff,
        challenge=challenge,
    )
    assert report["approval_valid"] is False
    assert report["checks"]["monthly_cost_ceiling_valid"] is False


def test_all_scope_attestations_are_required():
    _, _, _, handoff = _ready_review()
    challenge = build_provisioning_authorization_challenge(handoff)
    decision = _complete_provisioning_decision(handoff)
    decision["scope_attestations"]["deployment_not_authorized"] = False
    report = validate_provisioning_authorization_decision(
        decision,
        handoff=handoff,
        challenge=challenge,
    )
    assert report["approval_valid"] is False
    assert report["attestation_checks"]["deployment_not_authorized"] is False


def test_sensitive_material_is_rejected():
    _, _, _, handoff = _ready_review()
    challenge = build_provisioning_authorization_challenge(handoff)
    decision = _complete_provisioning_decision(handoff)
    decision["tower_step_up_receipt_ref"] = "token=not-allowed"
    report = validate_provisioning_authorization_decision(
        decision,
        handoff=handoff,
        challenge=challenge,
    )
    assert report["approval_valid"] is False
    assert report["sensitive_material_detected"] is True


def test_action_scope_is_empty_without_approval():
    manifest = build_provider_action_scope_manifest(
        {},
        validation={"approval_valid": False},
    )
    assert manifest["allowed_future_actions"] == []
    assert manifest[
        "provider_calls_authorized_for_future_execution_preparation"
    ] is False
    assert manifest["deployment_authorized"] is False


def test_approved_action_scope_is_one_tower_fronted_service():
    _, _, _, handoff = _ready_review()
    challenge = build_provisioning_authorization_challenge(handoff)
    decision = _complete_provisioning_decision(handoff)
    validation = validate_provisioning_authorization_decision(
        decision, handoff=handoff, challenge=challenge
    )
    manifest = build_provider_action_scope_manifest(
        decision, validation=validation
    )
    assert manifest["service_count_ceiling"] == 1
    assert manifest["public_ingress_owner"] == "tower"
    assert manifest["observatory_public_ingress_allowed"] is False
    assert manifest["deployment_authorized"] is False


def test_resource_ceiling_prohibits_database_storage_and_dns():
    _, _, _, handoff = _ready_review()
    challenge = build_provisioning_authorization_challenge(handoff)
    decision = _complete_provisioning_decision(handoff)
    validation = validate_provisioning_authorization_decision(
        decision, handoff=handoff, challenge=challenge
    )
    manifest = build_resource_and_cost_ceiling_manifest(
        decision, validation=validation
    )
    assert manifest["managed_web_service_count_ceiling"] == 1
    assert manifest["database_count_ceiling"] == 0
    assert manifest["object_storage_bucket_count_ceiling"] == 0
    assert manifest["dns_change_count_ceiling"] == 0
    assert manifest["automatic_spend_authorized"] is False


def test_secret_custody_allows_references_not_values():
    manifest = build_secret_custody_authorization_manifest(
        validation={"approval_valid": True}
    )
    assert manifest[
        "provider_secret_reference_registration_authorized"
    ] is True
    assert manifest["secret_value_generation_authorized"] is False
    assert manifest["secret_value_readback_authorized"] is False
    assert manifest["raw_secret_values_recorded"] is False


def test_execution_preconditions_preserve_operational_locks():
    manifest = build_execution_preconditions_manifest(
        validation={"approval_valid": True}
    )
    assert manifest["deployment_authorized"] is False
    assert manifest["official_walkthrough_authorized"] is False
    assert manifest["production_manual_live_authorized"] is False
    assert manifest["broker_submission_enabled"] is False
    assert manifest["real_capital_movement_enabled"] is False
    assert manifest["direct_vault_upload_enabled"] is False
    assert manifest["live_auto_locked"] is True


def test_frozen_authorization_record_is_sanitized():
    provider, review_owner, review, handoff = _ready_review()
    decision = _complete_provisioning_decision(handoff)
    record = freeze_provisioning_authorization_record(
        ROOT, provider, review_owner, review, decision
    )
    rendered = json.dumps(record)
    assert record["approval_valid"] is True
    assert record["frozen"] is True
    assert record["frozen_authorization_record_hash"]
    assert decision["owner_id"] not in rendered
    assert record["raw_secret_values_recorded"] is False


def test_blank_current_state_preserves_prior_hold():
    provider, review_owner, review, decision = blank_current_inputs(ROOT)
    state = build_current_provisioning_authorization_state(
        ROOT, provider, review_owner, review, decision
    )
    assert state["closed_through_step"] == 70
    assert state["final_decision"] == (
        "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
    )
    assert state["provider_calls_performed"] is False


def test_ready_review_without_second_owner_decision_is_held():
    provider, review_owner, review, handoff = _ready_review()
    decision = provisioning_authorization_decision_template(handoff)
    result = build_provisioning_authorization_decision(
        ROOT, provider, review_owner, review, decision
    )
    assert result["final_decision"] == (
        "NO_GO_HOLD_PROVIDER_PROVISIONING_AUTHORIZATION_REQUIRED"
    )
    assert result["authorization_valid"] is False


def test_owner_rejection_is_fail_closed():
    provider, review_owner, review, handoff = _ready_review()
    decision = _complete_provisioning_decision(handoff)
    decision["decision"] = REJECT_DECISION
    result = build_provisioning_authorization_decision(
        ROOT, provider, review_owner, review, decision
    )
    assert result["final_decision"] == (
        "NO_GO_OWNER_REJECTED_PROVIDER_PROVISIONING_AUTHORIZATION"
    )
    assert result["authorization_valid"] is False


def test_complete_approval_opens_only_no_call_execution_preparation():
    provider, review_owner, review, handoff = _ready_review()
    decision = _complete_provisioning_decision(handoff)
    result = build_provisioning_authorization_decision(
        ROOT, provider, review_owner, review, decision
    )
    assert result["authorization_valid"] is True
    assert result[
        "ready_for_separate_no_call_provider_provisioning_execution_preparation"
    ] is True
    assert result[
        "provider_calls_authorized_for_future_execution_preparation"
    ] is True
    assert result["deployment_authorized"] is False
    assert result["provider_calls_performed"] is False


def test_no_call_execution_preparation_plan_invokes_nothing():
    provider, review_owner, review, handoff = _ready_review()
    decision = _complete_provisioning_decision(handoff)
    plan = build_no_call_execution_preparation_plan(
        ROOT, provider, review_owner, review, decision
    )
    assert plan["ready"] is True
    assert plan["dry_run_only"] is True
    assert plan["shell_invoked"] is False
    assert plan["provider_api_invoked"] is False
    assert plan["provider_cli_invoked"] is False
    assert plan["provider_login_performed"] is False
    assert plan["resources_created"] is False
    assert plan["deployment_performed"] is False


def test_current_approved_state_has_future_scope_but_no_actions():
    provider, review_owner, review, handoff = _ready_review()
    decision = _complete_provisioning_decision(handoff)
    state = build_current_provisioning_authorization_state(
        ROOT, provider, review_owner, review, decision
    )
    assert state["provisioning_authorization_valid"] is True
    assert state[
        "provider_calls_authorized_for_future_execution_preparation"
    ] is True
    assert state["provider_calls_performed"] is False
    assert state["resources_created"] is False
    assert state["deployment_performed"] is False
    assert state["live_auto_locked"] is True


def test_worksheets_are_written_outside_repository(tmp_path):
    output = tmp_path / "authorization-worksheets"
    result = write_provisioning_authorization_worksheets(
        output,
        repository_root=ROOT,
    )
    assert Path(result["authorization_decision_path"]).is_file()
    assert Path(
        result["execution_preparation_placeholder_path"]
    ).is_file()
    assert Path(result["manifest_path"]).is_file()
    assert ROOT not in output.parents
    rendered = "\n".join(
        path.read_text(encoding="utf-8")
        for path in output.iterdir()
        if path.is_file()
    ).lower()
    assert "postgresql://" not in rendered
    assert "-----begin private key-----" not in rendered
