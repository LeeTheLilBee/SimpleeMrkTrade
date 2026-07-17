from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_opening_execution_preparation import (
    PREPARE_DECISION,
    READY_DECISION,
    REQUIRED_EXECUTION_PREPARATION_ATTESTATIONS,
    SCHEMA_VERSION,
    blank_current_inputs,
    build_current_session_opening_execution_preparation_state,
    build_duplicate_resource_lookup_preparation,
    build_execution_preparation_receipt_chain_and_stop_gate,
    build_inert_execution_session_authorization_plan,
    build_isolated_browser_and_credential_custody_manifest,
    build_one_service_environment_secret_preparation_manifest,
    build_provider_identity_window_cost_revalidation,
    freeze_session_opening_execution_preparation_packet,
    session_opening_execution_preparation_input_template,
    validate_session_opening_execution_preparation_inputs,
    write_session_opening_execution_preparation_worksheets,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "25998b862adf4de28225bbe75aed19540b3b010e"


def _synthetic_handoff(*, ready: bool = True) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "completed_controlled_provider_session_opening_execution_authorization_handoff",
        "frozen_session_opening_execution_authorization_record_hash": "a" * 64,
        "session_opening_execution_authorization_decision_hash": "b" * 64,
        "authorized_source_commit_sha256": hashlib.sha256(SOURCE_COMMIT.encode()).hexdigest(),
        "monthly_cost_ceiling_usd": "100.00",
        "provider_slug_sha256": "c" * 64,
        "account_or_team_ref_sha256": "d" * 64,
        "deployment_region_sha256": "e" * 64,
        "owner_execution_authorization_receipt_ref_sha256": "f" * 64,
        "execution_window_starts_at": "2026-07-17T00:00:00Z",
        "execution_window_expires_at": "2026-07-17T00:45:00Z",
        "authorization_expires_at": "2026-07-17T00:45:00Z",
        "execution_authorization_valid": ready,
        "execution_authorization_approved": ready,
        "execution_authorization_handoff_ready": ready,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "final_decision": READY_DECISION if ready else "NO_GO_HOLD_CONTROLLED_SESSION_OPENING_EXECUTION_AUTHORIZATION_REQUIRED",
        "handoff_hash": "1" * 64,
    }


def _complete_inputs(handoff: dict | None = None) -> dict:
    handoff = handoff or _synthetic_handoff()
    payload = session_opening_execution_preparation_input_template(handoff)
    payload.update({
        "preparation_decision": PREPARE_DECISION,
        "authorized_source_commit_ref": SOURCE_COMMIT,
        "preparation_window_starts_at": "2026-07-17T00:05:00Z",
        "preparation_window_expires_at": "2026-07-17T00:30:00Z",
        "owner_execution_preparation_receipt_ref": "tower-owner/execution-preparation",
        "provider_console_route_ref": "provider-console/services",
        "isolated_browser_session_ref": "browser-session/private-001",
        "duplicate_resource_lookup_receipt_ref": "provider-lookup/no-duplicate-001",
        "one_service_request_ref": "service-request/tower-staging-001",
        "execution_session_nonce_ref": "session-nonce/execution-001",
        "scope_attestations": {name: True for name in REQUIRED_EXECUTION_PREPARATION_ATTESTATIONS},
    })
    return payload


def _validated(handoff: dict | None = None):
    handoff = handoff or _synthetic_handoff()
    inputs = _complete_inputs(handoff)
    report = validate_session_opening_execution_preparation_inputs(inputs, handoff=handoff)
    return handoff, inputs, report


def _parts():
    handoff, inputs, report = _validated()
    identity = build_provider_identity_window_cost_revalidation(handoff, inputs, report)
    browser = build_isolated_browser_and_credential_custody_manifest(report)
    duplicate = build_duplicate_resource_lookup_preparation(report)
    service = build_one_service_environment_secret_preparation_manifest(report)
    receipts = build_execution_preparation_receipt_chain_and_stop_gate(report)
    frozen = freeze_session_opening_execution_preparation_packet(
        handoff, inputs, report, identity, browser, duplicate, service, receipts
    )
    return handoff, inputs, report, identity, browser, duplicate, service, receipts, frozen


def test_blank_handoff_shape_is_fail_closed():
    handoff = _synthetic_handoff(ready=False)
    assert handoff["execution_authorization_handoff_ready"] is False
    assert handoff["provider_session_opened"] is False


def test_ready_handoff_still_performs_no_actions():
    handoff = _synthetic_handoff()
    assert handoff["execution_authorization_handoff_ready"] is True
    assert handoff["provider_calls_performed"] is False


def test_template_defaults_to_hold():
    payload = session_opening_execution_preparation_input_template(_synthetic_handoff())
    assert payload["preparation_decision"] == "HOLD"
    assert not any(payload["scope_attestations"].values())


def test_template_contains_no_secret_values():
    rendered = json.dumps(session_opening_execution_preparation_input_template(_synthetic_handoff()))
    assert "ghp_" not in rendered
    assert "password=" not in rendered.lower()


def test_blank_inputs_fail_closed():
    handoff = _synthetic_handoff()
    report = validate_session_opening_execution_preparation_inputs(
        session_opening_execution_preparation_input_template(handoff), handoff=handoff
    )
    assert report["valid"] is False


def test_complete_inputs_validate():
    _, _, report = _validated()
    assert report["valid"] is True
    assert report["error_count"] == 0


def test_sensitive_material_is_rejected():
    handoff = _synthetic_handoff()
    payload = _complete_inputs(handoff)
    payload["provider_console_route_ref"] = "password=do-not-store"
    report = validate_session_opening_execution_preparation_inputs(payload, handoff=handoff)
    assert any(e["code"] == "sensitive_material_rejected" for e in report["errors"])


def test_frozen_authorization_hash_binding_is_required():
    handoff = _synthetic_handoff()
    payload = _complete_inputs(handoff)
    payload["frozen_session_opening_execution_authorization_record_hash"] = "0" * 64
    report = validate_session_opening_execution_preparation_inputs(payload, handoff=handoff)
    assert any(e["field"].startswith("frozen_session") for e in report["errors"])


def test_authorization_decision_hash_binding_is_required():
    handoff = _synthetic_handoff()
    payload = _complete_inputs(handoff)
    payload["session_opening_execution_authorization_decision_hash"] = "0" * 64
    report = validate_session_opening_execution_preparation_inputs(payload, handoff=handoff)
    assert any(e["field"] == "session_opening_execution_authorization_decision_hash" for e in report["errors"])


def test_source_commit_binding_is_required():
    handoff = _synthetic_handoff()
    payload = _complete_inputs(handoff)
    payload["authorized_source_commit_ref"] = "0" * 40
    report = validate_session_opening_execution_preparation_inputs(payload, handoff=handoff)
    assert any(e["code"] == "source_commit_binding_mismatch" for e in report["errors"])


def test_preparation_window_must_be_ordered_and_bounded():
    handoff = _synthetic_handoff()
    payload = _complete_inputs(handoff)
    payload["preparation_window_expires_at"] = "2026-07-17T00:44:00Z"
    report = validate_session_opening_execution_preparation_inputs(payload, handoff=handoff)
    assert any("at_most_30_minutes" in e["code"] for e in report["errors"])


def test_preparation_window_must_stay_inside_authorization():
    handoff = _synthetic_handoff()
    payload = _complete_inputs(handoff)
    payload["preparation_window_expires_at"] = "2026-07-17T01:00:00Z"
    report = validate_session_opening_execution_preparation_inputs(payload, handoff=handoff)
    assert any(e["code"] == "window_must_be_inside_execution_authorization" for e in report["errors"])


def test_cost_ceiling_is_required_and_bound():
    handoff = _synthetic_handoff()
    payload = _complete_inputs(handoff)
    payload["monthly_cost_ceiling_usd"] = "101.00"
    report = validate_session_opening_execution_preparation_inputs(payload, handoff=handoff)
    assert any(e["code"] == "cost_ceiling_mismatch" for e in report["errors"])


def test_provider_fingerprints_are_required():
    handoff = _synthetic_handoff()
    payload = _complete_inputs(handoff)
    payload["provider_slug_sha256"] = ""
    report = validate_session_opening_execution_preparation_inputs(payload, handoff=handoff)
    assert any(e["field"] == "provider_slug_sha256" for e in report["errors"])


def test_owner_execution_preparation_receipt_is_required():
    handoff = _synthetic_handoff()
    payload = _complete_inputs(handoff)
    payload["owner_execution_preparation_receipt_ref"] = ""
    report = validate_session_opening_execution_preparation_inputs(payload, handoff=handoff)
    assert any(e["field"] == "owner_execution_preparation_receipt_ref" for e in report["errors"])


def test_one_service_request_reference_is_required():
    handoff = _synthetic_handoff()
    payload = _complete_inputs(handoff)
    payload["one_service_request_ref"] = ""
    report = validate_session_opening_execution_preparation_inputs(payload, handoff=handoff)
    assert any(e["field"] == "one_service_request_ref" for e in report["errors"])


def test_duplicate_lookup_receipt_is_required():
    handoff = _synthetic_handoff()
    payload = _complete_inputs(handoff)
    payload["duplicate_resource_lookup_receipt_ref"] = ""
    report = validate_session_opening_execution_preparation_inputs(payload, handoff=handoff)
    assert any(e["field"] == "duplicate_resource_lookup_receipt_ref" for e in report["errors"])


def test_all_scope_attestations_are_required():
    handoff = _synthetic_handoff()
    payload = _complete_inputs(handoff)
    first = REQUIRED_EXECUTION_PREPARATION_ATTESTATIONS[0]
    payload["scope_attestations"][first] = False
    report = validate_session_opening_execution_preparation_inputs(payload, handoff=handoff)
    assert any(e["field"] == f"scope_attestations.{first}" for e in report["errors"])


def test_identity_plan_records_fingerprints_only():
    handoff, inputs, report = _validated()
    record = build_provider_identity_window_cost_revalidation(handoff, inputs, report)
    assert len(record["provider_slug_sha256"]) == 64
    assert record["raw_provider_identity_values_recorded"] is False


def test_browser_manifest_requires_ephemeral_isolation():
    manifest = build_isolated_browser_and_credential_custody_manifest({"valid": True})
    assert manifest["browser_profile"] == "ephemeral_private_isolated"
    assert manifest["provider_session_opened"] is False


def test_browser_manifest_contains_no_automation_authority():
    manifest = build_isolated_browser_and_credential_custody_manifest({"valid": True})
    assert manifest["browser_automation_authorized"] is False
    assert manifest["provider_login_performed"] is False


def test_credential_custody_records_no_values():
    manifest = build_isolated_browser_and_credential_custody_manifest({"valid": True})
    assert manifest["credential_values_recorded"] is False
    assert manifest["cookies_recorded"] is False
    assert manifest["tokens_recorded"] is False


def test_duplicate_plan_is_lookup_only():
    plan = build_duplicate_resource_lookup_preparation({"valid": True})
    assert plan["resource_mutations"] == []
    assert plan["provider_api_requests"] == []


def test_duplicate_plan_stops_on_ambiguity():
    plan = build_duplicate_resource_lookup_preparation({"valid": True})
    assert any("ambiguous" in item for item in plan["mandatory_stop_conditions"])


def test_service_manifest_preserves_tower_front_door():
    manifest = build_one_service_environment_secret_preparation_manifest({"valid": True})
    assert manifest["service_limit"] == 1
    assert manifest["runtime_target"] == "web.managed_staging:app"
    assert manifest["public_ingress_owner"] == "tower"


def test_service_manifest_creates_nothing():
    manifest = build_one_service_environment_secret_preparation_manifest({"valid": True})
    assert manifest["resource_creation_authorized"] is False
    assert manifest["build_authorized"] is False
    assert manifest["deployment_authorized"] is False


def test_environment_plan_contains_names_not_values():
    manifest = build_one_service_environment_secret_preparation_manifest({"valid": True})
    assert manifest["environment_variable_names_only"] is True
    assert manifest["secret_values_included"] is False


def test_secret_reference_plan_prohibits_readback():
    manifest = build_one_service_environment_secret_preparation_manifest({"valid": True})
    assert manifest["secret_references_only"] is True
    assert manifest["secret_readback_authorized"] is False


def test_receipt_chain_is_ordered():
    gate = build_execution_preparation_receipt_chain_and_stop_gate({"valid": True})
    assert gate["future_receipt_order"][0].endswith("start_receipt")
    assert gate["future_receipt_order"][-1].endswith("closeout_receipt")


def test_stop_gate_contains_required_stops():
    gate = build_execution_preparation_receipt_chain_and_stop_gate({"valid": True})
    rendered = " ".join(gate["mandatory_stop_conditions"])
    assert "duplicate" in rendered
    assert "secret_value_readback" in rendered
    assert "stop_before_build" in rendered


def test_frozen_packet_is_sanitized():
    *_, frozen = _parts()
    rendered = json.dumps(frozen)
    assert "tower-owner/execution-preparation" not in rendered
    assert frozen["contains_raw_reference_values"] is False


def test_frozen_packet_performs_no_actions():
    *_, frozen = _parts()
    assert frozen["provider_session_opened"] is False
    assert frozen["resources_created"] is False
    assert frozen["deployment_performed"] is False


def test_inert_plan_contains_no_commands_or_requests():
    plan = build_inert_execution_session_authorization_plan({"valid": True})
    assert plan["browser_actions"] == []
    assert plan["provider_cli_commands"] == []
    assert plan["provider_api_requests"] == []
    assert plan["shell_commands"] == []


def test_inert_plan_only_opens_later_authorization():
    plan = build_inert_execution_session_authorization_plan({"valid": True})
    assert plan["ready_for_separate_execution_session_authorization"] is True
    assert plan["provider_session_opened"] is False


def test_blank_current_state_closes_step_140_fail_closed():
    values = blank_current_inputs(ROOT)
    state = build_current_session_opening_execution_preparation_state(ROOT, *values)
    assert state["closed_through_step"] == 140
    assert state["session_opening_execution_preparation_valid"] is False


def test_current_state_preserves_all_operational_locks():
    values = blank_current_inputs(ROOT)
    state = build_current_session_opening_execution_preparation_state(ROOT, *values)
    for field in (
        "provider_session_opening_authorized", "provider_login_authorized",
        "provider_calls_authorized", "resource_creation_authorized",
        "secret_reference_registration_authorized", "database_creation_authorized",
        "object_storage_creation_authorized", "dns_changes_authorized",
        "build_authorized", "deployment_authorized", "production_manual_live_authorized",
        "broker_submission_enabled", "real_capital_movement_enabled",
        "direct_vault_upload_enabled",
    ):
        assert state[field] is False
    assert state["live_auto_locked"] is True


def test_current_state_next_boundary_is_execution_session_authorization():
    values = blank_current_inputs(ROOT)
    state = build_current_session_opening_execution_preparation_state(ROOT, *values)
    assert state["next_boundary"].endswith("execution_session_authorization")


def test_worksheets_must_be_outside_repository():
    with pytest.raises(ValueError):
        write_session_opening_execution_preparation_worksheets(
            ROOT / "unsafe-output", repository_root=ROOT
        )


def test_worksheets_and_placeholder_are_written(tmp_path):
    paths = write_session_opening_execution_preparation_worksheets(
        tmp_path / "worksheets", repository_root=ROOT
    )
    worksheet = Path(paths["session_opening_execution_preparation_path"])
    placeholder = Path(paths["execution_session_authorization_placeholder_path"])
    assert worksheet.is_file()
    assert placeholder.is_file()
    assert json.loads(placeholder.read_text())["decision"] == "HOLD"


def test_worksheet_manifest_reports_no_actions(tmp_path):
    paths = write_session_opening_execution_preparation_worksheets(
        tmp_path / "worksheets", repository_root=ROOT
    )
    manifest = json.loads(Path(paths["manifest_path"]).read_text())
    assert manifest["contains_secret_values"] is False
    assert manifest["provider_login_performed"] is False
    assert manifest["resources_created"] is False
    assert SCHEMA_VERSION.endswith(".v1")
    assert len(REQUIRED_EXECUTION_PREPARATION_ATTESTATIONS) >= 40
