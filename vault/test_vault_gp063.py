"""
Tests for VAULT GIANT PACK 063 — Real Storage Provider Secret Reference Ledger
"""

from pathlib import Path

import pytest

from vault.real_storage_provider_secret_reference_ledger_service import (
    DEFAULT_SECRET_REFERENCE_LEDGER_ID,
    LEDGER_POLICIES,
    ensure_storage_provider_secret_reference_ledger_schema,
    get_gp063_status,
    get_real_storage_provider_secret_reference_ledger_home,
    get_storage_provider_secret_reference_ledger_blockers,
    get_storage_provider_secret_reference_ledger_entries,
    get_storage_provider_secret_reference_ledger_events,
    get_storage_provider_secret_reference_ledger_next_step,
    get_storage_provider_secret_reference_ledger_policies,
    get_storage_provider_secret_reference_ledger_record,
    initialize_real_storage_provider_secret_reference_ledger,
    record_storage_provider_secret_reference_ledger_event,
    render_real_storage_provider_secret_reference_ledger_page,
    validate_storage_provider_secret_reference_ledger,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROVIDER_CANDIDATES = 5
EXPECTED_ENTRIES = 30
EXPECTED_POLICIES = len(LEDGER_POLICIES)
EXPECTED_BLOCKERS = 140


@pytest.fixture()
def ledger_db(tmp_path, monkeypatch):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "selection_registry.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "capability_contract.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "risk_criteria_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "selection_review_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "prep_readiness.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB", str(tmp_path / "config_contract.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB", str(tmp_path / "credential_boundary.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB", str(tmp_path / "secret_reference_ledger.sqlite"))
    return str(tmp_path / "secret_reference_ledger.sqlite")


def test_gp063_schema_is_real_sqlite_backed(ledger_db):
    result = ensure_storage_provider_secret_reference_ledger_schema(ledger_db)
    db_path = Path(result["db_path"])

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert db_path.exists()
    assert "vault_storage_provider_secret_reference_ledgers" in result["tables"]
    assert "vault_storage_provider_secret_reference_ledger_entries" in result["tables"]
    assert "vault_storage_provider_secret_reference_ledger_policies" in result["tables"]
    assert "vault_storage_provider_secret_reference_ledger_blockers" in result["tables"]
    assert "vault_storage_provider_secret_reference_ledger_events" in result["tables"]


def test_gp063_initialize_creates_real_ledger_entries_policies_blockers_events(ledger_db):
    result = initialize_real_storage_provider_secret_reference_ledger(ledger_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["secret_reference_ledger_id"] == DEFAULT_SECRET_REFERENCE_LEDGER_ID
    assert result["ledger_count"] == 1
    assert result["entry_count"] == EXPECTED_ENTRIES
    assert result["policy_count"] == EXPECTED_POLICIES
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_secret_reference_ledger(ledger_db)
    assert second["ledger_count"] == 1
    assert second["entry_count"] == EXPECTED_ENTRIES
    assert second["policy_count"] == EXPECTED_POLICIES
    assert second["blocker_count"] == EXPECTED_BLOCKERS
    assert second["event_count"] >= 6


def test_gp063_ledger_record_is_real_and_sourced_from_gp062(ledger_db):
    ledger = get_storage_provider_secret_reference_ledger_record(ledger_db)["secret_reference_ledger"]

    assert ledger["secret_reference_ledger_id"] == DEFAULT_SECRET_REFERENCE_LEDGER_ID
    assert ledger["pack_id"] == "VAULT_GP063"
    assert ledger["section_id"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert ledger["section_range"] == "GP061-GP070"
    assert ledger["source_credential_boundary_id"] == "VSPCB-GP062-001"
    assert ledger["source_credential_boundary_pack_id"] == "VAULT_GP062"
    assert ledger["ledger_status"] == "REAL_SECRET_REFERENCE_LEDGER_OPEN_ALIAS_ONLY_TOWER_LOCKED"
    assert ledger["tower_authority_status"] == "TOWER_REVIEW_REQUIRED_NOT_GRANTED"

    data = ledger["ledger_data"]
    assert data["ledger_type"] == "REAL_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER"
    assert data["real_durable_secret_reference_ledger"] is True
    assert data["metadata_source"] == "VAULT_GP062_REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY"
    assert data["source_credential_boundary_id"] == "VSPCB-GP062-001"
    assert data["source_credential_boundary_pack_id"] == "VAULT_GP062"
    assert data["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert data["slot_code_count"] == 6
    assert data["ledger_entry_count"] == EXPECTED_ENTRIES
    assert data["ledger_policy_count"] == EXPECTED_POLICIES
    assert data["carried_blocker_count"] == EXPECTED_BLOCKERS
    assert data["safe_to_continue_to_gp064"] is True


def test_gp063_ledger_keeps_secret_and_provider_operations_locked(ledger_db):
    ledger = get_storage_provider_secret_reference_ledger_record(ledger_db)["secret_reference_ledger"]

    assert ledger["secret_reference_ledger_ready"] is True
    assert ledger["ledger_entries_ready"] is True
    assert ledger["alias_only_references"] is True
    assert ledger["actual_secret_values_stored"] is False
    assert ledger["secret_values_present"] is False
    assert ledger["token_material_present"] is False
    assert ledger["encrypted_secret_payload_present"] is False
    assert ledger["secret_references_created"] is False
    assert ledger["secret_references_activated"] is False
    assert ledger["credentials_configured"] is False
    assert ledger["provider_endpoint_configured"] is False
    assert ledger["storage_container_configured"] is False
    assert ledger["encryption_configured"] is False
    assert ledger["provider_approval_ready"] is False
    assert ledger["provider_activation_ready"] is False
    assert ledger["provider_configuration_ready"] is False
    assert ledger["provider_read_write_ready"] is False
    assert ledger["provider_approved"] is False
    assert ledger["provider_activated"] is False
    assert ledger["provider_selected"] is False
    assert ledger["provider_configured"] is False
    assert ledger["provider_read_enabled"] is False
    assert ledger["provider_write_enabled"] is False
    assert ledger["provider_object_read_claimed"] is False
    assert ledger["provider_connection_tested"] is False
    assert ledger["risk_accepted"] is False
    assert ledger["risk_waived"] is False
    assert ledger["mitigation_approved"] is False
    assert ledger["object_body_view_enabled"] is False
    assert ledger["direct_upload_enabled"] is False
    assert ledger["export_enabled"] is False
    assert ledger["execution_enabled"] is False
    assert ledger["vault_done"] is False


def test_gp063_ledger_entries_are_real_alias_only_and_secret_free(ledger_db):
    payload = get_storage_provider_secret_reference_ledger_entries(ledger_db)

    assert payload["pack"]["id"] == "VAULT_GP063"
    assert payload["real_sqlite_backed"] is True
    assert payload["entry_count"] == EXPECTED_ENTRIES
    assert payload["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert payload["slot_code_count"] == 6
    assert payload["reference_required_count"] == EXPECTED_ENTRIES
    assert payload["reference_created_count"] == 0
    assert payload["reference_activated_count"] == 0
    assert payload["alias_only_reference_count"] == EXPECTED_ENTRIES
    assert payload["actual_secret_value_stored_count"] == 0
    assert payload["secret_value_present_count"] == 0
    assert payload["token_material_present_count"] == 0
    assert payload["encrypted_secret_payload_present_count"] == 0
    assert payload["credential_material_exposed_count"] == 0
    assert payload["redacted_view_only_count"] == EXPECTED_ENTRIES
    assert payload["tower_review_required_count"] == EXPECTED_ENTRIES
    assert payload["tower_review_granted_count"] == 0
    assert payload["credentials_configured_count"] == 0
    assert payload["provider_connection_tested_count"] == 0
    assert payload["provider_read_enabled_count"] == 0
    assert payload["provider_write_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    for item in payload["entries"]:
        assert item["ledger_entry_id"].startswith("VSPSRLE-")
        assert item["secret_reference_ledger_id"] == DEFAULT_SECRET_REFERENCE_LEDGER_ID
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["source_secret_reference_slot_id"].startswith("VSPSRS-")
        assert item["secret_reference_alias"].startswith("ALIAS-ONLY-")
        assert item["secret_reference_alias"].endswith("-UNCREATED")
        assert item["ledger_entry_status"] == "REAL_LEDGER_ENTRY_ALIAS_ONLY_NO_SECRET_REFERENCE_CREATED"
        assert item["reference_required"] is True
        assert item["reference_created"] is False
        assert item["reference_activated"] is False
        assert item["alias_only_reference"] is True
        assert item["actual_secret_value_stored"] is False
        assert item["secret_value_present"] is False
        assert item["token_material_present"] is False
        assert item["encrypted_secret_payload_present"] is False
        assert item["credential_material_exposed"] is False
        assert item["redacted_view_only"] is True
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False
        assert item["credentials_configured"] is False
        assert item["provider_connection_tested"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False


def test_gp063_ledger_policies_are_real_and_locked(ledger_db):
    payload = get_storage_provider_secret_reference_ledger_policies(ledger_db)

    assert payload["pack"]["id"] == "VAULT_GP063"
    assert payload["real_sqlite_backed"] is True
    assert payload["policy_count"] == EXPECTED_POLICIES
    assert payload["policy_code_count"] == EXPECTED_POLICIES
    assert payload["policy_required_count"] == EXPECTED_POLICIES
    assert payload["policy_verified_count"] == 0
    assert payload["actual_secret_values_stored_count"] == 0
    assert payload["secret_values_present_count"] == 0
    assert payload["token_material_present_count"] == 0
    assert payload["encrypted_secret_payload_present_count"] == 0
    assert payload["secret_references_created_count"] == 0
    assert payload["secret_references_activated_count"] == 0
    assert payload["provider_connection_tested_count"] == 0
    assert payload["provider_read_enabled_count"] == 0
    assert payload["provider_write_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0
    assert payload["tower_review_required_count"] == EXPECTED_POLICIES
    assert payload["tower_review_granted_count"] == 0

    codes = {item["policy_code"] for item in payload["policies"]}
    expected_codes = {item["policy_code"] for item in LEDGER_POLICIES}
    assert codes == expected_codes

    for item in payload["policies"]:
        assert item["ledger_policy_id"].startswith("VSPSRLP-")
        assert item["secret_reference_ledger_id"] == DEFAULT_SECRET_REFERENCE_LEDGER_ID
        assert item["policy_status"] == "REAL_SECRET_REFERENCE_LEDGER_POLICY_RECORDED_TOWER_LOCKED"
        assert item["policy_required"] is True
        assert item["policy_verified"] is False
        assert item["actual_secret_values_stored"] is False
        assert item["secret_values_present"] is False
        assert item["token_material_present"] is False
        assert item["encrypted_secret_payload_present"] is False
        assert item["secret_references_created"] is False
        assert item["secret_references_activated"] is False
        assert item["provider_connection_tested"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False


def test_gp063_blockers_are_real_and_carried_from_gp062(ledger_db):
    payload = get_storage_provider_secret_reference_ledger_blockers(ledger_db)

    assert payload["pack"]["id"] == "VAULT_GP063"
    assert payload["real_sqlite_backed"] is True
    assert payload["blocker_count"] == EXPECTED_BLOCKERS
    assert payload["capability_blocker_count"] == 60
    assert payload["criteria_blocker_count"] == 40
    assert payload["risk_blocker_count"] == 40
    assert payload["blocks_provider_configuration_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_read_write_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_export_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_required_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_granted_count"] == 0
    assert payload["risk_accepted_count"] == 0
    assert payload["risk_waived_count"] == 0
    assert payload["mitigation_approved_count"] == 0
    assert payload["resolved_count"] == 0

    for item in payload["blockers"]:
        assert item["ledger_blocker_id"].startswith("VSPSRLB-")
        assert item["secret_reference_ledger_id"] == DEFAULT_SECRET_REFERENCE_LEDGER_ID
        assert item["source_credential_blocker_id"].startswith("VSPCBB-")
        assert item["source_config_blocker_id"].startswith("VSPCFGB-")
        assert item["source_readiness_blocker_id"].startswith("VSPPB-")
        assert item["source_receipt_line_id"].startswith("VSPRL-")
        assert item["source_finding_id"].startswith("VSPRCF-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["blocker_status"] == "REAL_SECRET_REFERENCE_LEDGER_BLOCKER_ACTIVE_CARRIED_FROM_GP062"
        assert item["blocks_provider_configuration"] is True
        assert item["blocks_provider_read_write"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False
        assert item["resolved"] is False


def test_gp063_event_log_is_real_and_seeded(ledger_db):
    events = get_storage_provider_secret_reference_ledger_events(ledger_db)

    assert events["pack"]["id"] == "VAULT_GP063"
    assert events["real_sqlite_backed"] is True
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_CREATED" in event_types
    assert "SOURCE_GP062_CREDENTIAL_BOUNDARY_ATTACHED" in event_types
    assert "REAL_SECRET_REFERENCE_LEDGER_ENTRIES_CREATED_ALIAS_ONLY" in event_types
    assert "REAL_SECRET_REFERENCE_LEDGER_POLICIES_CREATED" in event_types
    assert "REAL_SECRET_REFERENCE_LEDGER_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "SECRET_REFERENCE_LEDGER_LOCKS_CONFIRMED" in event_types

    for event in events["events"]:
        assert event["event_id"].startswith("VSPSRLEVT-")
        assert event["secret_reference_ledger_id"] == DEFAULT_SECRET_REFERENCE_LEDGER_ID
        assert isinstance(event["event_payload"], dict)
        assert event["created_at"]


def test_gp063_can_write_real_event_without_storing_or_activating_secrets(ledger_db):
    before = get_storage_provider_secret_reference_ledger_events(ledger_db)["event_count"]

    written = record_storage_provider_secret_reference_ledger_event(
        "OWNER_GP063_SECRET_REFERENCE_LEDGER_OBSERVED",
        {"reviewer": "owner", "note": "reviewed real GP063 secret-reference ledger"},
        ledger_db,
    )

    after = get_storage_provider_secret_reference_ledger_events(ledger_db)
    ledger = get_storage_provider_secret_reference_ledger_record(ledger_db)["secret_reference_ledger"]
    entries = get_storage_provider_secret_reference_ledger_entries(ledger_db)
    policies = get_storage_provider_secret_reference_ledger_policies(ledger_db)

    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPSRLEVT-")
    assert written["secret_reference_ledger_id"] == DEFAULT_SECRET_REFERENCE_LEDGER_ID
    assert written["actual_secret_values_stored"] is False
    assert written["secret_values_present"] is False
    assert written["token_material_present"] is False
    assert written["encrypted_secret_payload_present"] is False
    assert written["secret_references_created"] is False
    assert written["secret_references_activated"] is False
    assert written["credentials_configured"] is False
    assert written["provider_configured"] is False
    assert written["provider_connection_tested"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

    assert after["event_count"] == before + 1
    assert "OWNER_GP063_SECRET_REFERENCE_LEDGER_OBSERVED" in {event["event_type"] for event in after["events"]}

    assert ledger["actual_secret_values_stored"] is False
    assert ledger["secret_values_present"] is False
    assert ledger["secret_references_activated"] is False
    assert ledger["provider_configured"] is False
    assert entries["secret_value_present_count"] == 0
    assert entries["reference_activated_count"] == 0
    assert policies["secret_values_present_count"] == 0
    assert policies["secret_references_activated_count"] == 0


def test_gp063_validation_passes_real_locked_secret_reference_ledger(ledger_db):
    validation = validate_storage_provider_secret_reference_ledger(ledger_db)

    assert validation["pack"]["id"] == "VAULT_GP063"
    assert validation["validation_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["passed_count"] == validation["check_count"]
    assert validation["real_sqlite_backed"] is True
    assert validation["safe_to_continue_to_gp064"] is True

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_SECRET_REFERENCE_LEDGER_EXISTS" in codes
    assert "SOURCE_GP062_CREDENTIAL_BOUNDARY_ATTACHED" in codes
    assert "SECRET_REFERENCE_LEDGER_READY" in codes
    assert "REAL_LEDGER_ENTRIES_EXIST" in codes
    assert "ALL_ENTRIES_ALIAS_ONLY" in codes
    assert "NO_LEDGER_REFERENCES_CREATED" in codes
    assert "NO_LEDGER_REFERENCES_ACTIVATED" in codes
    assert "NO_ENTRY_SECRET_VALUES_PRESENT" in codes
    assert "NO_ENTRY_TOKEN_MATERIAL_PRESENT" in codes
    assert "REAL_LEDGER_POLICIES_EXIST" in codes
    assert "REAL_LEDGER_BLOCKERS_CARRIED_FORWARD" in codes
    assert "NO_LEDGER_ACTUAL_SECRET_VALUES_STORED" in codes
    assert "NO_LEDGER_ENCRYPTED_SECRET_PAYLOAD_PRESENT" in codes
    assert "NO_CREDENTIALS_CONFIGURED" in codes
    assert "NO_PROVIDER_CONNECTION_TESTED" in codes
    assert "NO_EXPORT" in codes
    assert "NO_EXECUTION" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "EVENT_LOG_EXISTS" in codes


def test_gp063_home_payload_has_truth_routes_and_next_step(ledger_db):
    home = get_real_storage_provider_secret_reference_ledger_home(ledger_db)

    assert home["pack"]["id"] == "VAULT_GP063"
    assert home["ledger_truth"]["real_storage_provider_secret_reference_ledger_ready"] is True
    assert home["ledger_truth"]["real_sqlite_backed"] is True
    assert home["ledger_truth"]["real_schema_ready"] is True
    assert home["ledger_truth"]["real_secret_reference_ledger_exists"] is True
    assert home["ledger_truth"]["real_secret_reference_ledger_entries_exist"] is True
    assert home["ledger_truth"]["real_secret_reference_policy_rows_exist"] is True
    assert home["ledger_truth"]["real_secret_reference_blocker_rows_exist"] is True
    assert home["ledger_truth"]["real_event_log_exists"] is True
    assert home["ledger_truth"]["source_gp062_credential_boundary_attached"] is True
    assert home["ledger_truth"]["validation_passed"] is True
    assert home["ledger_truth"]["entry_count"] == EXPECTED_ENTRIES
    assert home["ledger_truth"]["policy_count"] == EXPECTED_POLICIES
    assert home["ledger_truth"]["blocker_count"] == EXPECTED_BLOCKERS
    assert home["ledger_truth"]["reference_created_count"] == 0
    assert home["ledger_truth"]["reference_activated_count"] == 0
    assert home["ledger_truth"]["secret_value_present_count"] == 0
    assert home["ledger_truth"]["token_material_present_count"] == 0
    assert home["ledger_truth"]["credentials_configured"] is False
    assert home["ledger_truth"]["provider_configured"] is False
    assert home["ledger_truth"]["export_enabled"] is False
    assert home["ledger_truth"]["execution_enabled"] is False
    assert home["ledger_truth"]["vault_done"] is False

    routes = home["routes"]
    assert routes["route"] == "/vault/real-storage-provider-secret-reference-ledger"
    assert routes["json_route"] == "/vault/real-storage-provider-secret-reference-ledger.json"
    assert routes["record_route"] == "/vault/storage-provider-secret-reference-ledger-record.json"
    assert routes["entries_route"] == "/vault/storage-provider-secret-reference-ledger-entries.json"
    assert routes["policies_route"] == "/vault/storage-provider-secret-reference-ledger-policies.json"
    assert routes["blockers_route"] == "/vault/storage-provider-secret-reference-ledger-blockers.json"
    assert routes["events_route"] == "/vault/storage-provider-secret-reference-ledger-events.json"
    assert routes["validation_route"] == "/vault/storage-provider-secret-reference-ledger-validation.json"
    assert routes["next_step_route"] == "/vault/storage-provider-secret-reference-ledger-next-step.json"
    assert routes["gp063_status_route"] == "/vault/gp063-status.json"

    assert home["next_step"]["next_pack"] == "VAULT_GP064_REAL_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT"
    assert home["next_step"]["safe_to_continue_to_gp064"] is True
    assert home["next_step"]["vault_done"] is False
    assert home["next_step"]["clouds_should_continue"] is False


def test_gp063_status_ready_real_alias_only_and_locked(ledger_db):
    status = get_gp063_status(ledger_db)
    gp063 = status["gp063_status"]

    assert status["pack"]["id"] == "VAULT_GP063"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert status["pack"]["section_range"] == "GP061-GP070"

    assert gp063["ready"] is True
    assert gp063["real_storage_provider_secret_reference_ledger_ready"] is True
    assert gp063["real_sqlite_backed"] is True
    assert gp063["real_schema_ready"] is True
    assert gp063["real_ledger_count"] == 1
    assert gp063["real_entry_count"] == EXPECTED_ENTRIES
    assert gp063["real_policy_count"] == EXPECTED_POLICIES
    assert gp063["real_blocker_count"] == EXPECTED_BLOCKERS
    assert gp063["source_gp062_credential_boundary_attached"] is True
    assert gp063["secret_reference_ledger_ready"] is True
    assert gp063["ledger_entries_ready"] is True
    assert gp063["alias_only_references"] is True
    assert gp063["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert gp063["slot_code_count"] == 6
    assert gp063["policy_code_count"] == EXPECTED_POLICIES
    assert gp063["reference_created_count"] == 0
    assert gp063["reference_activated_count"] == 0
    assert gp063["actual_secret_value_stored_count"] == 0
    assert gp063["secret_value_present_count"] == 0
    assert gp063["token_material_present_count"] == 0
    assert gp063["encrypted_secret_payload_present_count"] == 0
    assert gp063["credential_material_exposed_count"] == 0
    assert gp063["blocks_provider_configuration_count"] == EXPECTED_BLOCKERS
    assert gp063["blocks_provider_read_write_count"] == EXPECTED_BLOCKERS
    assert gp063["blocks_export_count"] == EXPECTED_BLOCKERS
    assert gp063["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert gp063["tower_review_granted_count"] == 0
    assert gp063["resolved_count"] == 0
    assert gp063["validation_ready"] is True
    assert gp063["validation_passed"] is True
    assert gp063["safe_to_continue_to_gp064"] is True
    assert gp063["vault_done"] is False
    assert gp063["foundation_status"] == "secret_reference_ledger_ready_safe_to_continue_not_done"

    assert gp063["actual_secret_values_stored"] is False
    assert gp063["secret_values_present"] is False
    assert gp063["token_material_present"] is False
    assert gp063["encrypted_secret_payload_present"] is False
    assert gp063["secret_references_created"] is False
    assert gp063["secret_references_activated"] is False
    assert gp063["credentials_configured"] is False
    assert gp063["provider_endpoint_configured"] is False
    assert gp063["storage_container_configured"] is False
    assert gp063["encryption_configured"] is False
    assert gp063["provider_configuration_ready"] is False
    assert gp063["provider_configured"] is False
    assert gp063["provider_read_enabled"] is False
    assert gp063["provider_write_enabled"] is False
    assert gp063["provider_connection_tested"] is False
    assert gp063["object_body_view_enabled"] is False
    assert gp063["direct_upload_enabled"] is False
    assert gp063["export_enabled"] is False
    assert gp063["execution_enabled"] is False
    assert gp063["clouds_status"] == "parked_do_not_continue_from_vault_gp063"
    assert gp063["next_pack"] == "VAULT_GP064_REAL_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT"


def test_gp063_next_step_points_to_gp064_endpoint_namespace_contract():
    next_step = get_storage_provider_secret_reference_ledger_next_step()["next_step"]

    assert next_step["current_section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert next_step["current_section_range"] == "GP061-GP070"
    assert next_step["next_pack"] == "VAULT_GP064_REAL_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT"
    assert next_step["next_pack_title"] == "Real Storage Provider Endpoint Namespace Contract"
    assert next_step["safe_to_continue_to_gp064"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

    note = next_step["owner_notebook_note"].lower()
    assert "endpoint/namespace contract" in note
    assert "keeping credentials" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "real sqlite secret-reference ledger" in rules
    assert "alias-only references" in rules
    assert "real storage provider endpoint namespace contract" in rules
    assert "do not store actual provider secrets" in rules
    assert "do not create or activate secret references yet" in rules
    assert "do not configure credentials yet" in rules
    assert "do not unlock export" in rules
    assert "do not unlock execution" in rules
    assert "do not treat vault as done" in rules


def test_gp063_html_is_dark_and_mentions_secret_reference_ledger(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "html_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "html_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "html_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "html_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "html_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "html_readiness.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB", str(tmp_path / "html_config.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB", str(tmp_path / "html_credential.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB", str(tmp_path / "html_ledger.sqlite"))

    html = render_real_storage_provider_secret_reference_ledger_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Secret Reference Ledger" in html
    assert "Real Storage Provider Configuration Layer" in html
    assert "Archive Vault" in html
    assert "GP063" in html
    assert "Secret-reference ledger ready" in html
    assert "Alias-only rows" in html
    assert "Real SQLite-backed" in html
    assert "No secrets stored" in html
    assert "No references activated" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-secret-reference-ledger.json" in html
    assert "/vault/gp063-status.json" in html

    forbidden = [
        "background: #fff",
        "background:#fff",
        "background-color: #fff",
        "background-color:#fff",
        "background: white",
        "background:white",
    ]

    for token in forbidden:
        assert token not in lowered


def test_gp063_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/real-storage-provider-secret-reference-ledger",
        "/vault/real-storage-provider-secret-reference-ledger.json",
        "/vault/storage-provider-secret-reference-ledger-record.json",
        "/vault/storage-provider-secret-reference-ledger-entries.json",
        "/vault/storage-provider-secret-reference-ledger-policies.json",
        "/vault/storage-provider-secret-reference-ledger-blockers.json",
        "/vault/storage-provider-secret-reference-ledger-events.json",
        "/vault/storage-provider-secret-reference-ledger-validation.json",
        "/vault/storage-provider-secret-reference-ledger-next-step.json",
        "/vault/gp063-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp063_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "routes_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "routes_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "routes_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "routes_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "routes_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "routes_readiness.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB", str(tmp_path / "routes_config.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB", str(tmp_path / "routes_credential.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB", str(tmp_path / "routes_ledger.sqlite"))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/real-storage-provider-secret-reference-ledger",
        "/vault/real-storage-provider-secret-reference-ledger.json",
        "/vault/storage-provider-secret-reference-ledger-record.json",
        "/vault/storage-provider-secret-reference-ledger-entries.json",
        "/vault/storage-provider-secret-reference-ledger-policies.json",
        "/vault/storage-provider-secret-reference-ledger-blockers.json",
        "/vault/storage-provider-secret-reference-ledger-events.json",
        "/vault/storage-provider-secret-reference-ledger-validation.json",
        "/vault/storage-provider-secret-reference-ledger-next-step.json",
        "/vault/gp063-status.json",
    ]

    for route in routes:
        response = client.get(route)
        assert response.status_code in (200, 403), (
            f"{route} returned unexpected status {response.status_code}. "
            "Expected 200 direct route or 403 Tower/private guard."
        )

        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Real Storage Provider Secret Reference Ledger" in response.data
