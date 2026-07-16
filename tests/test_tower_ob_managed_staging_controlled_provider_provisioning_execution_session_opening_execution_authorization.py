from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_opening_execution_authorization import (
    AUTHORIZE_DECISION,
    EXACT_CHALLENGE_PREFIX,
    READY_DECISION,
    REJECT_DECISION,
    REQUIRED_EXECUTION_AUTHORIZATION_ATTESTATIONS,
    SCHEMA_VERSION,
    blank_current_inputs,
    build_completed_session_opening_preparation_handoff,
    build_current_session_opening_execution_authorization_state,
    build_execution_receipt_chain_and_stop_gate,
    build_identity_window_cost_binding,
    build_inert_session_opening_execution_preparation_plan,
    build_session_opening_execution_authorization_challenge,
    build_session_opening_execution_authorization_decision,
    build_session_opening_execution_scope_manifest,
    freeze_session_opening_execution_authorization_record,
    session_opening_execution_authorization_decision_template,
    validate_session_opening_execution_authorization_decision,
    write_session_opening_execution_authorization_worksheets,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "214d0f1042ea1e1959a96e3431080181cd8913e4"


def _synthetic_handoff(*, ready: bool = True) -> dict:
    import hashlib
    commit_sha = hashlib.sha256(SOURCE_COMMIT.encode()).hexdigest()
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "completed_controlled_provider_session_opening_preparation_handoff",
        "frozen_session_opening_preparation_packet_hash": "a" * 64,
        "session_opening_preparation_decision_hash": "b" * 64,
        "authorized_source_commit_sha256": commit_sha,
        "monthly_cost_ceiling_usd": "100.00",
        "provider_slug_sha256": "c" * 64,
        "account_or_team_ref_sha256": "d" * 64,
        "deployment_region_sha256": "e" * 64,
        "owner_session_opening_preparation_receipt_ref_sha256": "f" * 64,
        "session_opening_preparation_valid": ready,
        "preparation_handoff_ready": ready,
        "provider_session_opening_authorized": False,
        "provider_session_opened": False,
        "provider_login_performed": False,
        "provider_calls_performed": False,
        "resources_created": False,
        "secrets_registered": False,
        "build_performed": False,
        "deployment_performed": False,
        "final_decision": READY_DECISION if ready else "NO_GO_HOLD_CONTROLLED_SESSION_OPENING_PREPARATION_REQUIRED",
        "handoff_hash": "1" * 64,
    }


def _complete_decision(handoff: dict | None = None) -> dict:
    handoff = handoff or _synthetic_handoff()
    challenge = build_session_opening_execution_authorization_challenge(handoff)
    payload = session_opening_execution_authorization_decision_template(handoff)
    payload.update({
        "decision": AUTHORIZE_DECISION,
        "owner_id": "tower-owner-session-opening-execution",
        "tower_step_up_receipt_ref": "tower-step-up/session-opening-execution",
        "owner_execution_authorization_receipt_ref": "tower-owner-receipt/session-opening-execution",
        "challenge_id": challenge["challenge_id"],
        "challenge_phrase_confirmation": challenge["challenge_phrase"],
        "authorized_source_commit_ref": SOURCE_COMMIT,
        "execution_window_starts_at": "2026-07-17T00:00:00Z",
        "execution_window_expires_at": "2026-07-17T00:30:00Z",
        "authorization_expires_at": "2026-07-17T00:45:00Z",
        "monthly_cost_ceiling_usd": "100.00",
        "provider_slug_sha256": handoff["provider_slug_sha256"],
        "account_or_team_ref_sha256": handoff["account_or_team_ref_sha256"],
        "deployment_region_sha256": handoff["deployment_region_sha256"],
        "owner_session_opening_preparation_receipt_ref_sha256": handoff[
            "owner_session_opening_preparation_receipt_ref_sha256"
        ],
        "scope_attestations": {
            name: True for name in REQUIRED_EXECUTION_AUTHORIZATION_ATTESTATIONS
        },
    })
    return payload


def _validated(handoff: dict | None = None):
    handoff = handoff or _synthetic_handoff()
    decision = _complete_decision(handoff)
    validation = validate_session_opening_execution_authorization_decision(
        decision, handoff=handoff
    )
    return handoff, decision, validation


def test_blank_completed_preparation_handoff_is_held():
    values = blank_current_inputs(ROOT)
    handoff = build_completed_session_opening_preparation_handoff(ROOT, *values[:9])
    assert handoff["preparation_handoff_ready"] is False
    assert handoff["provider_session_opened"] is False


def test_decision_template_defaults_to_hold():
    payload = session_opening_execution_authorization_decision_template(
        _synthetic_handoff()
    )
    assert payload["decision"] == "HOLD"
    assert not any(payload["scope_attestations"].values())


def test_decision_template_contains_no_secret_values():
    rendered = json.dumps(
        session_opening_execution_authorization_decision_template(
            _synthetic_handoff()
        )
    )
    assert "ghp_" not in rendered
    assert "password=" not in rendered.lower()


def test_blank_decision_fails_closed():
    handoff = _synthetic_handoff()
    report = validate_session_opening_execution_authorization_decision(
        session_opening_execution_authorization_decision_template(handoff),
        handoff=handoff,
    )
    assert report["valid"] is False
    assert report["approved"] is False


def test_complete_authorization_validates():
    _, _, report = _validated()
    assert report["valid"] is True
    assert report["approved"] is True
    assert report["error_count"] == 0


def test_sensitive_material_is_rejected():
    handoff = _synthetic_handoff()
    decision = _complete_decision(handoff)
    decision["owner_id"] = "password=do-not-store"
    report = validate_session_opening_execution_authorization_decision(
        decision, handoff=handoff
    )
    assert any(e["code"] == "sensitive_material_rejected" for e in report["errors"])


def test_frozen_preparation_hash_binding_is_required():
    handoff = _synthetic_handoff()
    decision = _complete_decision(handoff)
    decision["frozen_session_opening_preparation_packet_hash"] = "0" * 64
    report = validate_session_opening_execution_authorization_decision(decision, handoff=handoff)
    assert any(e["field"] == "frozen_session_opening_preparation_packet_hash" for e in report["errors"])


def test_preparation_decision_hash_binding_is_required():
    handoff = _synthetic_handoff()
    decision = _complete_decision(handoff)
    decision["session_opening_preparation_decision_hash"] = "0" * 64
    report = validate_session_opening_execution_authorization_decision(decision, handoff=handoff)
    assert any(e["field"] == "session_opening_preparation_decision_hash" for e in report["errors"])


def test_source_commit_binding_is_required():
    handoff = _synthetic_handoff()
    decision = _complete_decision(handoff)
    decision["authorized_source_commit_ref"] = "0" * 40
    report = validate_session_opening_execution_authorization_decision(decision, handoff=handoff)
    assert any(e["code"] == "source_commit_binding_mismatch" for e in report["errors"])


def test_execution_window_must_be_ordered_and_bounded():
    handoff = _synthetic_handoff()
    decision = _complete_decision(handoff)
    decision["execution_window_expires_at"] = "2026-07-17T02:00:00Z"
    report = validate_session_opening_execution_authorization_decision(decision, handoff=handoff)
    assert any("at_most_45_minutes" in e["code"] for e in report["errors"])


def test_authorization_must_cover_execution_window():
    handoff = _synthetic_handoff()
    decision = _complete_decision(handoff)
    decision["authorization_expires_at"] = "2026-07-17T00:15:00Z"
    report = validate_session_opening_execution_authorization_decision(decision, handoff=handoff)
    assert any(e["code"] == "authorization_must_cover_execution_window" for e in report["errors"])


def test_cost_ceiling_is_required_and_bound():
    handoff = _synthetic_handoff()
    decision = _complete_decision(handoff)
    decision["monthly_cost_ceiling_usd"] = "101.00"
    report = validate_session_opening_execution_authorization_decision(decision, handoff=handoff)
    assert any(e["code"] == "cost_ceiling_mismatch" for e in report["errors"])


def test_provider_fingerprints_are_required():
    handoff = _synthetic_handoff()
    decision = _complete_decision(handoff)
    decision["provider_slug_sha256"] = ""
    report = validate_session_opening_execution_authorization_decision(decision, handoff=handoff)
    assert any(e["field"] == "provider_slug_sha256" for e in report["errors"])


def test_owner_receipts_are_required():
    handoff = _synthetic_handoff()
    decision = _complete_decision(handoff)
    decision["tower_step_up_receipt_ref"] = ""
    decision["owner_execution_authorization_receipt_ref"] = ""
    report = validate_session_opening_execution_authorization_decision(decision, handoff=handoff)
    fields = {e["field"] for e in report["errors"]}
    assert "tower_step_up_receipt_ref" in fields
    assert "owner_execution_authorization_receipt_ref" in fields


def test_exact_challenge_phrase_is_required():
    handoff = _synthetic_handoff()
    decision = _complete_decision(handoff)
    decision["challenge_phrase_confirmation"] = "yes"
    report = validate_session_opening_execution_authorization_decision(decision, handoff=handoff)
    assert any(e["code"] == "exact_challenge_phrase_required" for e in report["errors"])


def test_all_scope_attestations_are_required():
    handoff = _synthetic_handoff()
    decision = _complete_decision(handoff)
    first = REQUIRED_EXECUTION_AUTHORIZATION_ATTESTATIONS[0]
    decision["scope_attestations"][first] = False
    report = validate_session_opening_execution_authorization_decision(decision, handoff=handoff)
    assert any(e["field"] == f"scope_attestations.{first}" for e in report["errors"])


def test_challenge_is_packet_bound():
    challenge = build_session_opening_execution_authorization_challenge(_synthetic_handoff())
    assert challenge["challenge_phrase"].startswith(EXACT_CHALLENGE_PREFIX)
    assert "aaaaaaaaaaaa" in challenge["challenge_phrase"]
    assert "bbbbbbbbbbbb" in challenge["challenge_phrase"]


def test_challenge_contains_no_provider_action():
    challenge = build_session_opening_execution_authorization_challenge(_synthetic_handoff())
    assert challenge["provider_session_opening_authorized"] is False
    assert challenge["provider_calls_performed"] is False


def test_rejection_validates_but_does_not_approve():
    handoff = _synthetic_handoff()
    decision = _complete_decision(handoff)
    decision["decision"] = REJECT_DECISION
    report = validate_session_opening_execution_authorization_decision(decision, handoff=handoff)
    assert report["valid"] is True
    assert report["rejected"] is True
    assert report["approved"] is False


def test_scope_is_empty_without_approval():
    handoff = _synthetic_handoff()
    decision = session_opening_execution_authorization_decision_template(handoff)
    report = validate_session_opening_execution_authorization_decision(decision, handoff=handoff)
    scope = build_session_opening_execution_scope_manifest(decision, report)
    assert not any(scope["future_preparation_scope"].values())


def test_approved_scope_is_one_service_preparation_only():
    _, decision, report = _validated()
    scope = build_session_opening_execution_scope_manifest(decision, report)
    assert scope["future_preparation_scope"]["one_inert_tower_fronted_service_shell_preparation"] is True
    assert scope["provider_session_opening_authorized_now"] is False


def test_scope_blocks_build_and_deployment_now():
    _, decision, report = _validated()
    scope = build_session_opening_execution_scope_manifest(decision, report)
    assert scope["build_authorized_now"] is False
    assert scope["deployment_authorized_now"] is False


def test_scope_blocks_database_storage_and_dns():
    _, decision, report = _validated()
    scope = build_session_opening_execution_scope_manifest(decision, report)
    assert scope["database_creation_authorized"] is False
    assert scope["object_storage_creation_authorized"] is False
    assert scope["dns_changes_authorized"] is False


def test_identity_window_cost_binding_records_fingerprints_only():
    handoff, decision, report = _validated()
    binding = build_identity_window_cost_binding(handoff, decision, report)
    assert len(binding["owner_id_sha256"]) == 64
    assert binding["raw_provider_identity_values_recorded"] is False
    assert binding["raw_credentials_recorded"] is False


def test_receipt_chain_is_ordered():
    _, decision, report = _validated()
    gate = build_execution_receipt_chain_and_stop_gate(decision, report)
    assert gate["future_receipt_order"][0].endswith("start_receipt")
    assert gate["future_receipt_order"][-1].endswith("closeout_receipt")


def test_stop_gate_contains_duplicate_and_secret_stops():
    _, decision, report = _validated()
    gate = build_execution_receipt_chain_and_stop_gate(decision, report)
    rendered = " ".join(gate["mandatory_stop_conditions"])
    assert "duplicate" in rendered
    assert "secret_value_readback" in rendered


def test_frozen_record_is_sanitized():
    handoff, decision, report = _validated()
    scope = build_session_opening_execution_scope_manifest(decision, report)
    binding = build_identity_window_cost_binding(handoff, decision, report)
    receipts = build_execution_receipt_chain_and_stop_gate(decision, report)
    frozen = freeze_session_opening_execution_authorization_record(
        handoff, decision, report, scope, binding, receipts
    )
    rendered = json.dumps(frozen)
    assert decision["owner_id"] not in rendered
    assert decision["tower_step_up_receipt_ref"] not in rendered


def test_frozen_record_performs_no_actions():
    handoff, decision, report = _validated()
    scope = build_session_opening_execution_scope_manifest(decision, report)
    binding = build_identity_window_cost_binding(handoff, decision, report)
    receipts = build_execution_receipt_chain_and_stop_gate(decision, report)
    frozen = freeze_session_opening_execution_authorization_record(
        handoff, decision, report, scope, binding, receipts
    )
    assert frozen["provider_session_opened"] is False
    assert frozen["resources_created"] is False
    assert frozen["deployment_performed"] is False


def test_inert_plan_contains_no_commands_or_requests():
    plan = build_inert_session_opening_execution_preparation_plan({"approved": True})
    assert plan["browser_actions"] == []
    assert plan["provider_cli_commands"] == []
    assert plan["provider_api_requests"] == []
    assert plan["http_requests"] == []
    assert plan["shell_commands"] == []


def test_inert_plan_only_opens_later_preparation():
    plan = build_inert_session_opening_execution_preparation_plan({"approved": True})
    assert plan["ready_for_separate_execution_preparation"] is True
    assert plan["provider_session_opened"] is False


def test_blank_current_state_closes_step_130_fail_closed():
    values = blank_current_inputs(ROOT)
    state = build_current_session_opening_execution_authorization_state(ROOT, *values)
    assert state["closed_through_step"] == 130
    assert state["session_opening_execution_authorization_approved"] is False
    assert state["provider_session_opened"] is False


def test_current_state_preserves_all_operational_locks():
    values = blank_current_inputs(ROOT)
    state = build_current_session_opening_execution_authorization_state(ROOT, *values)
    for field in (
        "provider_session_opening_authorized",
        "provider_login_authorized",
        "provider_calls_authorized",
        "resource_creation_authorized",
        "secret_reference_registration_authorized",
        "database_creation_authorized",
        "object_storage_creation_authorized",
        "dns_changes_authorized",
        "build_authorized",
        "deployment_authorized",
        "production_manual_live_authorized",
        "broker_submission_enabled",
        "real_capital_movement_enabled",
        "direct_vault_upload_enabled",
    ):
        assert state[field] is False
    assert state["live_auto_locked"] is True


def test_current_state_next_boundary_is_execution_preparation():
    values = blank_current_inputs(ROOT)
    state = build_current_session_opening_execution_authorization_state(ROOT, *values)
    assert state["next_boundary"].endswith("session_opening_execution_preparation")


def test_worksheets_must_be_outside_repository(tmp_path):
    with pytest.raises(ValueError):
        write_session_opening_execution_authorization_worksheets(
            ROOT / "unsafe-output", repository_root=ROOT
        )


def test_worksheets_are_written_outside_repository(tmp_path):
    output = tmp_path / "worksheets"
    paths = write_session_opening_execution_authorization_worksheets(
        output, repository_root=ROOT
    )
    assert Path(paths["session_opening_execution_authorization_decision_path"]).is_file()
    assert Path(paths["session_opening_execution_preparation_placeholder_path"]).is_file()


def test_execution_preparation_placeholder_defaults_to_hold(tmp_path):
    output = tmp_path / "worksheets"
    paths = write_session_opening_execution_authorization_worksheets(
        output, repository_root=ROOT
    )
    placeholder = json.loads(
        Path(paths["session_opening_execution_preparation_placeholder_path"]).read_text()
    )
    assert placeholder["decision"] == "HOLD"
    assert placeholder["provider_session_opened"] is False


def test_worksheet_manifest_reports_no_actions(tmp_path):
    output = tmp_path / "worksheets"
    paths = write_session_opening_execution_authorization_worksheets(
        output, repository_root=ROOT
    )
    manifest = json.loads(Path(paths["manifest_path"]).read_text())
    assert manifest["contains_secret_values"] is False
    assert manifest["provider_login_performed"] is False
    assert manifest["resources_created"] is False


def test_schema_and_attestation_contract_are_stable():
    assert SCHEMA_VERSION.endswith(".v1")
    assert len(REQUIRED_EXECUTION_AUTHORIZATION_ATTESTATIONS) >= 40
