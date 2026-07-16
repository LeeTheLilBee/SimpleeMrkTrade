from __future__ import annotations

import json
from pathlib import Path

from tower.tower_ob_managed_staging_provider_authorization import (
    REQUIRED_CAPABILITIES,
    build_owner_authorization_challenge,
    freeze_provider_authorization_packet,
    provider_input_template,
)
from tower.tower_ob_managed_staging_no_call_provisioning_review import (
    REQUIRED_REVIEW_ATTESTATIONS,
    build_account_region_cost_review,
    build_authorization_handoff,
    build_current_no_call_provisioning_review_state,
    build_environment_secret_reference_manifest,
    build_external_data_service_boundary,
    build_inert_web_service_manifest,
    build_no_call_console_dry_run_plan,
    build_no_call_provisioning_review_decision,
    build_operational_safeguard_manifest,
    build_provider_documentation_review,
    freeze_no_call_provisioning_review_packet,
    no_call_review_input_template,
    validate_no_call_review_inputs,
    write_no_call_review_worksheets,
)

ROOT = Path(__file__).resolve().parents[1]


def _complete_provider_inputs() -> dict:
    payload = provider_input_template()
    payload.update({
        "provider_slug": "managed-host-review",
        "account_or_team_ref": "simplee-staging-team",
        "deployment_region": "us-east-review",
        "billing_owner_ref": "simplee-owner-billing",
        "service_name": "simplee-tower-ob-staging",
        "repository_ref": "LeeTheLilBee/SimpleeMrkTrade",
        "source_branch": "tower-ob-integration-dev",
    })
    payload["capability_attestations"] = {
        name: True for name in REQUIRED_CAPABILITIES
    }
    return payload


def _complete_owner_decision(provider_inputs: dict) -> dict:
    frozen = freeze_provider_authorization_packet(ROOT, provider_inputs)
    challenge = build_owner_authorization_challenge(
        packet_hash=frozen["frozen_packet_hash"]
    )
    return {
        "decision": "APPROVE_FOR_PROVISIONING_REVIEW",
        "owner_id": "tower-owner-review",
        "tower_step_up_receipt_ref": "tower-step-up-receipt-review",
        "challenge_id": challenge["challenge_id"],
        "challenge_phrase_confirmation": challenge["challenge_phrase"],
        "decided_at": "2026-07-16T15:45:00Z",
    }


def _ready_handoff() -> tuple[dict, dict, dict]:
    provider_inputs = _complete_provider_inputs()
    owner_decision = _complete_owner_decision(provider_inputs)
    handoff = build_authorization_handoff(
        ROOT,
        provider_inputs,
        owner_decision,
    )
    assert handoff["ready_for_no_call_review"] is True
    return provider_inputs, owner_decision, handoff


def _complete_review_inputs(handoff: dict) -> dict:
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
        "reviewed_at": "2026-07-16T15:46:00Z",
    })
    payload["attestations"] = {
        name: True for name in REQUIRED_REVIEW_ATTESTATIONS
    }
    return payload


def test_review_template_contains_no_secret_values():
    payload = no_call_review_input_template()
    rendered = json.dumps(payload).lower()

    assert "postgresql://" not in rendered
    assert "-----begin private key-----" not in rendered
    assert "api_key=" not in rendered
    assert payload["attestations"]
    assert all(value is False for value in payload["attestations"].values())


def test_blank_review_inputs_fail_closed():
    handoff = build_authorization_handoff(ROOT, {}, {})
    payload = no_call_review_input_template(handoff)
    report = validate_no_call_review_inputs(payload, handoff=handoff)

    assert report["valid"] is False
    assert report["error_count"] > 0
    assert report["authorization_handoff_ready"] is False


def test_complete_review_inputs_validate():
    _, _, handoff = _ready_handoff()
    payload = _complete_review_inputs(handoff)
    report = validate_no_call_review_inputs(payload, handoff=handoff)

    assert report["valid"] is True
    assert report["error_count"] == 0
    assert report["completed_attestation_count"] == len(
        REQUIRED_REVIEW_ATTESTATIONS
    )


def test_sensitive_material_is_rejected():
    _, _, handoff = _ready_handoff()
    payload = _complete_review_inputs(handoff)
    payload["provider_documentation_ref"] = "token=not-allowed"
    report = validate_no_call_review_inputs(payload, handoff=handoff)

    assert report["valid"] is False
    assert report["sensitive_material_detected"] is True


def test_authorization_handoff_blank_is_held():
    handoff = build_authorization_handoff(ROOT, {}, {})

    assert handoff["provider_inputs_valid"] is False
    assert handoff["owner_approval_valid"] is False
    assert handoff["ready_for_no_call_review"] is False
    assert handoff["provider_calls_authorized"] is False


def test_authorization_handoff_complete_is_ready_for_review_only():
    _, _, handoff = _ready_handoff()

    assert handoff["provider_inputs_valid"] is True
    assert handoff["owner_approval_valid"] is True
    assert handoff["ready_for_no_call_review"] is True
    assert handoff["resource_creation_authorized"] is False
    assert handoff["deployment_authorized"] is False


def test_review_hash_binding_mismatch_fails():
    _, _, handoff = _ready_handoff()
    payload = _complete_review_inputs(handoff)
    payload["frozen_provider_packet_hash"] = "0" * 64
    report = validate_no_call_review_inputs(payload, handoff=handoff)

    assert report["valid"] is False
    assert any(
        item["code"] == "authorization_packet_hash_mismatch"
        for item in report["errors"]
    )


def test_provider_documentation_record_fingerprints_refs():
    _, _, handoff = _ready_handoff()
    payload = _complete_review_inputs(handoff)
    record = build_provider_documentation_review(
        payload,
        handoff=handoff,
    )

    assert record["documentation_review_complete"] is True
    assert record["provider_documentation_ref_sha256"]
    assert record["raw_documentation_refs_recorded"] is False
    assert record["claims_verified_by_provider_api"] is False


def test_account_region_cost_review_blocks_automatic_spend():
    _, _, handoff = _ready_handoff()
    payload = _complete_review_inputs(handoff)
    record = build_account_region_cost_review(
        payload,
        handoff=handoff,
    )

    assert record["review_complete"] is True
    assert record["budget_amount_recorded"] is False
    assert record["automatic_spend_authorized"] is False
    assert record["production_billing_reuse_authorized"] is False


def test_web_service_manifest_is_one_tower_fronted_service():
    _, _, handoff = _ready_handoff()
    manifest = build_inert_web_service_manifest(handoff)

    assert manifest["service_count"] == 1
    assert manifest["runtime_target"] == "web.managed_staging:app"
    assert manifest["public_ingress_owner"] == "tower"
    assert manifest["observatory_public_ingress_allowed"] is False
    assert manifest["separate_observatory_service_required"] is False


def test_web_service_manifest_does_not_invent_build_command():
    _, _, handoff = _ready_handoff()
    manifest = build_inert_web_service_manifest(handoff)

    assert manifest["build_command"] is None
    assert manifest["build_command_status"] == (
        "provider_specific_review_required"
    )
    assert manifest["manifest_only"] is True


def test_environment_secret_manifest_contains_names_not_values():
    manifest = build_environment_secret_reference_manifest()
    rendered = json.dumps(manifest)

    assert "TOWER_SESSION_SECRET" in rendered
    assert "TOWER_OWNER_PASSWORD_HASH" in rendered
    assert manifest["raw_secret_values_recorded"] is False
    assert manifest["secrets_created"] is False
    assert manifest["secrets_read"] is False


def test_external_data_boundary_creates_nothing():
    boundary = build_external_data_service_boundary()

    assert boundary["database_resource_selected"] is False
    assert boundary["database_resource_created"] is False
    assert boundary["object_storage_resource_selected"] is False
    assert boundary["object_storage_resource_created"] is False
    assert boundary["vault_direct_upload_allowed"] is False


def test_operational_safeguards_preserve_live_locks():
    manifest = build_operational_safeguard_manifest()

    assert manifest["official_walkthrough_authorized"] is False
    assert manifest["production_manual_live_authorized"] is False
    assert manifest["broker_submission_enabled"] is False
    assert manifest["real_capital_movement_enabled"] is False
    assert manifest["direct_vault_upload_enabled"] is False
    assert manifest["live_auto_locked"] is True


def test_frozen_review_packet_is_hash_bound_and_inert():
    provider_inputs, owner_decision, handoff = _ready_handoff()
    review_inputs = _complete_review_inputs(handoff)
    packet = freeze_no_call_provisioning_review_packet(
        ROOT,
        provider_inputs,
        owner_decision,
        review_inputs,
    )

    assert packet["authorization_handoff_ready"] is True
    assert packet["review_inputs_valid"] is True
    assert packet["frozen"] is True
    assert packet["frozen_review_packet_hash"]
    assert packet["provider_calls_authorized"] is False
    assert packet["resource_creation_authorized"] is False


def test_blank_decision_remains_provider_input_hold():
    decision = build_no_call_provisioning_review_decision(
        ROOT,
        {},
        {},
        {},
    )

    assert decision["final_decision"] == (
        "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
    )
    assert decision[
        "ready_for_separate_provider_provisioning_authorization_decision"
    ] is False


def test_complete_provider_without_owner_remains_owner_hold():
    provider_inputs = _complete_provider_inputs()
    decision = build_no_call_provisioning_review_decision(
        ROOT,
        provider_inputs,
        {},
        {},
    )

    assert decision["final_decision"] == (
        "NO_GO_HOLD_OWNER_AUTHORIZATION_REQUIRED"
    )


def test_owner_approved_without_review_evidence_remains_review_hold():
    provider_inputs, owner_decision, handoff = _ready_handoff()
    decision = build_no_call_provisioning_review_decision(
        ROOT,
        provider_inputs,
        owner_decision,
        no_call_review_input_template(handoff),
    )

    assert decision["final_decision"] == (
        "NO_GO_HOLD_NO_CALL_PROVISIONING_REVIEW_EVIDENCE_REQUIRED"
    )


def test_complete_review_opens_only_separate_authorization_decision():
    provider_inputs, owner_decision, handoff = _ready_handoff()
    review_inputs = _complete_review_inputs(handoff)
    decision = build_no_call_provisioning_review_decision(
        ROOT,
        provider_inputs,
        owner_decision,
        review_inputs,
    )

    assert decision["final_decision"] == (
        "READY_FOR_SEPARATE_PROVIDER_PROVISIONING_AUTHORIZATION_DECISION"
    )
    assert decision[
        "ready_for_separate_provider_provisioning_authorization_decision"
    ] is True
    assert decision["provider_calls_authorized"] is False
    assert decision["resource_creation_authorized"] is False
    assert decision["deployment_authorized"] is False


def test_no_call_console_plan_invokes_nothing():
    plan = build_no_call_console_dry_run_plan(ROOT, {}, {}, {})

    assert plan["dry_run_only"] is True
    assert plan["shell_invoked"] is False
    assert plan["provider_api_invoked"] is False
    assert plan["provider_cli_invoked"] is False
    assert plan["provider_calls_performed"] is False
    assert plan["resources_created"] is False


def test_current_blank_state_closes_step_60_fail_closed():
    state = build_current_no_call_provisioning_review_state(
        ROOT,
        {},
        {},
        {},
    )

    assert state["closed_through_step"] == 60
    assert state["closed_layer"] == (
        "MANAGED_STAGING_NO_CALL_PROVIDER_PROVISIONING_REVIEW"
    )
    assert state["final_decision"] == (
        "NO_GO_HOLD_PROVIDER_INPUTS_AND_OWNER_AUTHORIZATION_REQUIRED"
    )
    assert state["blocking_requirement_count"] > 0


def test_current_complete_state_is_ready_for_separate_decision_only():
    provider_inputs, owner_decision, handoff = _ready_handoff()
    review_inputs = _complete_review_inputs(handoff)
    state = build_current_no_call_provisioning_review_state(
        ROOT,
        provider_inputs,
        owner_decision,
        review_inputs,
    )

    assert state["review_inputs_valid"] is True
    assert state[
        "ready_for_separate_provider_provisioning_authorization_decision"
    ] is True
    assert state["provider_calls_authorized"] is False
    assert state["resources_created"] is False
    assert state["deployment_performed"] is False


def test_current_state_preserves_all_operational_locks():
    state = build_current_no_call_provisioning_review_state(
        ROOT,
        {},
        {},
        {},
    )

    assert state["official_walkthrough_performed"] is False
    assert state["production_manual_live_authorized"] is False
    assert state["broker_submission_enabled"] is False
    assert state["real_capital_movement_enabled"] is False
    assert state["direct_vault_upload_enabled"] is False
    assert state["live_auto_locked"] is True


def test_review_worksheets_are_written_outside_repo(tmp_path):
    output = tmp_path / "review-worksheets"
    result = write_no_call_review_worksheets(
        output,
        repository_root=ROOT,
    )

    assert Path(result["review_input_path"]).is_file()
    assert Path(result["authorization_placeholder_path"]).is_file()
    assert Path(result["manifest_path"]).is_file()
    assert ROOT not in output.parents

    rendered = "\n".join(
        path.read_text(encoding="utf-8")
        for path in output.iterdir()
        if path.is_file()
    ).lower()
    assert "postgresql://" not in rendered
    assert "-----begin private key-----" not in rendered
