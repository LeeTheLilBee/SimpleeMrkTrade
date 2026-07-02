"""
Tests for VAULT GIANT PACK 062 — Real Storage Provider Credential Boundary
"""

from pathlib import Path

import pytest

from vault.real_storage_provider_credential_boundary_service import (
    BOUNDARY_RULES,
    DEFAULT_CREDENTIAL_BOUNDARY_ID,
    SECRET_REFERENCE_SLOT_SPECS,
    ensure_storage_provider_credential_boundary_schema,
    get_gp062_status,
    get_real_storage_provider_credential_boundary_home,
    get_storage_provider_credential_boundary_blockers,
    get_storage_provider_credential_boundary_events,
    get_storage_provider_credential_boundary_next_step,
    get_storage_provider_credential_boundary_record,
    get_storage_provider_credential_boundary_rules,
    get_storage_provider_secret_reference_slots,
    initialize_real_storage_provider_credential_boundary,
    record_storage_provider_credential_boundary_event,
    render_real_storage_provider_credential_boundary_page,
    validate_storage_provider_credential_boundary,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROVIDER_CANDIDATES = 5
EXPECTED_RULES = EXPECTED_PROVIDER_CANDIDATES * len(BOUNDARY_RULES)
EXPECTED_SLOTS = EXPECTED_PROVIDER_CANDIDATES * len(SECRET_REFERENCE_SLOT_SPECS)
EXPECTED_BLOCKERS = 140


@pytest.fixture()
def credential_db(tmp_path, monkeypatch):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "selection_registry.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "capability_contract.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "risk_criteria_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "selection_review_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "prep_readiness.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB", str(tmp_path / "config_contract.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB", str(tmp_path / "credential_boundary.sqlite"))
    return str(tmp_path / "credential_boundary.sqlite")


def test_gp062_schema_is_real_sqlite_backed(credential_db):
    result = ensure_storage_provider_credential_boundary_schema(credential_db)
    db_path = Path(result["db_path"])

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert db_path.exists()
    assert "vault_storage_provider_credential_boundaries" in result["tables"]
    assert "vault_storage_provider_credential_boundary_rules" in result["tables"]
    assert "vault_storage_provider_secret_reference_slots" in result["tables"]
    assert "vault_storage_provider_credential_boundary_blockers" in result["tables"]
    assert "vault_storage_provider_credential_boundary_events" in result["tables"]


def test_gp062_initialize_creates_real_boundary_rules_slots_blockers_events(credential_db):
    result = initialize_real_storage_provider_credential_boundary(credential_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["credential_boundary_id"] == DEFAULT_CREDENTIAL_BOUNDARY_ID
    assert result["boundary_count"] == 1
    assert result["rule_count"] == EXPECTED_RULES
    assert result["slot_count"] == EXPECTED_SLOTS
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_credential_boundary(credential_db)
    assert second["boundary_count"] == 1
    assert second["rule_count"] == EXPECTED_RULES
    assert second["slot_count"] == EXPECTED_SLOTS
    assert second["blocker_count"] == EXPECTED_BLOCKERS
    assert second["event_count"] >= 6


def test_gp062_boundary_record_is_real_and_sourced_from_gp061(credential_db):
    boundary = get_storage_provider_credential_boundary_record(credential_db)["credential_boundary"]

    assert boundary["credential_boundary_id"] == DEFAULT_CREDENTIAL_BOUNDARY_ID
    assert boundary["pack_id"] == "VAULT_GP062"
    assert boundary["section_id"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert boundary["section_range"] == "GP061-GP070"
    assert boundary["source_config_contract_id"] == "VSPCCFG-GP061-001"
    assert boundary["source_config_pack_id"] == "VAULT_GP061"
    assert boundary["boundary_status"] == "REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_OPEN_SECRET_FREE_TOWER_LOCKED"
    assert boundary["tower_authority_status"] == "TOWER_REVIEW_REQUIRED_NOT_GRANTED"

    data = boundary["boundary_data"]
    assert data["boundary_type"] == "REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY"
    assert data["real_durable_credential_boundary"] is True
    assert data["metadata_source"] == "VAULT_GP061_REAL_STORAGE_PROVIDER_CONFIG_CONTRACT"
    assert data["source_config_contract_id"] == "VSPCCFG-GP061-001"
    assert data["source_config_pack_id"] == "VAULT_GP061"
    assert data["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert data["boundary_rule_code_count"] == len(BOUNDARY_RULES)
    assert data["boundary_rule_count"] == EXPECTED_RULES
    assert data["secret_reference_slot_code_count"] == len(SECRET_REFERENCE_SLOT_SPECS)
    assert data["secret_reference_slot_count"] == EXPECTED_SLOTS
    assert data["carried_blocker_count"] == EXPECTED_BLOCKERS
    assert data["safe_to_continue_to_gp063"] is True


def test_gp062_boundary_keeps_all_secret_and_provider_operations_locked(credential_db):
    boundary = get_storage_provider_credential_boundary_record(credential_db)["credential_boundary"]

    assert boundary["credential_boundary_ready"] is True
    assert boundary["credential_model_ready"] is True
    assert boundary["secret_reference_slots_ready"] is True
    assert boundary["secret_values_stored"] is False
    assert boundary["secret_values_present"] is False
    assert boundary["token_material_present"] is False
    assert boundary["credentials_configured"] is False
    assert boundary["secret_references_activated"] is False
    assert boundary["provider_endpoint_configured"] is False
    assert boundary["storage_container_configured"] is False
    assert boundary["encryption_configured"] is False
    assert boundary["provider_approval_ready"] is False
    assert boundary["provider_activation_ready"] is False
    assert boundary["provider_configuration_ready"] is False
    assert boundary["provider_read_write_ready"] is False
    assert boundary["provider_approved"] is False
    assert boundary["provider_activated"] is False
    assert boundary["provider_recommended"] is False
    assert boundary["provider_selected"] is False
    assert boundary["provider_configured"] is False
    assert boundary["provider_read_enabled"] is False
    assert boundary["provider_write_enabled"] is False
    assert boundary["provider_object_read_claimed"] is False
    assert boundary["provider_connection_tested"] is False
    assert boundary["risk_accepted"] is False
    assert boundary["risk_waived"] is False
    assert boundary["mitigation_approved"] is False
    assert boundary["official_storage_receipt"] is False
    assert boundary["finalized_storage_receipt"] is False
    assert boundary["closed_storage_receipt"] is False
    assert boundary["object_body_view_enabled"] is False
    assert boundary["direct_upload_enabled"] is False
    assert boundary["export_enabled"] is False
    assert boundary["execution_enabled"] is False
    assert boundary["vault_done"] is False


def test_gp062_boundary_rules_are_real_secret_free_and_locked(credential_db):
    payload = get_storage_provider_credential_boundary_rules(credential_db)

    assert payload["pack"]["id"] == "VAULT_GP062"
    assert payload["real_sqlite_backed"] is True
    assert payload["rule_count"] == EXPECTED_RULES
    assert payload["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert payload["rule_code_count"] == len(BOUNDARY_RULES)
    assert payload["rule_required_count"] == EXPECTED_RULES
    assert payload["rule_verified_count"] == 0
    assert payload["secret_values_stored_count"] == 0
    assert payload["secret_values_present_count"] == 0
    assert payload["token_material_present_count"] == 0
    assert payload["credentials_configured_count"] == 0
    assert payload["tower_review_required_count"] == EXPECTED_RULES
    assert payload["tower_review_granted_count"] == 0
    assert payload["provider_connection_tested_count"] == 0
    assert payload["provider_read_enabled_count"] == 0
    assert payload["provider_write_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    codes = {item["rule_code"] for item in payload["rules"]}
    expected_codes = {item["rule_code"] for item in BOUNDARY_RULES}
    assert codes == expected_codes

    categories = {item["rule_category"] for item in payload["rules"]}
    assert "secret_safety" in categories
    assert "tower_gate" in categories
    assert "reference_model" in categories
    assert "connection_lock" in categories
    assert "export_lock" in categories

    for item in payload["rules"]:
        assert item["boundary_rule_id"].startswith("VSPCBR-")
        assert item["credential_boundary_id"] == DEFAULT_CREDENTIAL_BOUNDARY_ID
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["rule_status"] == "REAL_CREDENTIAL_BOUNDARY_RULE_RECORDED_SECRET_FREE_TOWER_LOCKED"
        assert item["rule_required"] is True
        assert item["rule_verified"] is False
        assert item["secret_values_stored"] is False
        assert item["secret_values_present"] is False
        assert item["token_material_present"] is False
        assert item["credentials_configured"] is False
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False
        assert item["provider_connection_tested"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False


def test_gp062_secret_reference_slots_are_real_but_hold_no_secrets(credential_db):
    payload = get_storage_provider_secret_reference_slots(credential_db)

    assert payload["pack"]["id"] == "VAULT_GP062"
    assert payload["real_sqlite_backed"] is True
    assert payload["slot_count"] == EXPECTED_SLOTS
    assert payload["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert payload["slot_code_count"] == len(SECRET_REFERENCE_SLOT_SPECS)
    assert payload["reference_required_count"] == EXPECTED_SLOTS
    assert payload["reference_created_count"] == 0
    assert payload["reference_activated_count"] == 0
    assert payload["secret_value_stored_count"] == 0
    assert payload["secret_value_present_count"] == 0
    assert payload["token_material_present_count"] == 0
    assert payload["encrypted_secret_present_count"] == 0
    assert payload["redacted_view_only_count"] == EXPECTED_SLOTS
    assert payload["tower_review_required_count"] == EXPECTED_SLOTS
    assert payload["tower_review_granted_count"] == 0

    codes = {item["slot_code"] for item in payload["slots"]}
    expected_codes = {item["slot_code"] for item in SECRET_REFERENCE_SLOT_SPECS}
    assert codes == expected_codes

    for item in payload["slots"]:
        assert item["secret_reference_slot_id"].startswith("VSPSRS-")
        assert item["credential_boundary_id"] == DEFAULT_CREDENTIAL_BOUNDARY_ID
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["slot_status"] == "REAL_SECRET_REFERENCE_SLOT_RESERVED_NO_SECRET_VALUE"
        assert item["reference_required"] is True
        assert item["reference_created"] is False
        assert item["reference_activated"] is False
        assert item["secret_value_stored"] is False
        assert item["secret_value_present"] is False
        assert item["token_material_present"] is False
        assert item["encrypted_secret_present"] is False
        assert item["redacted_view_only"] is True
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False


def test_gp062_blockers_are_real_and_carried_from_gp061(credential_db):
    payload = get_storage_provider_credential_boundary_blockers(credential_db)

    assert payload["pack"]["id"] == "VAULT_GP062"
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
        assert item["credential_blocker_id"].startswith("VSPCBB-")
        assert item["credential_boundary_id"] == DEFAULT_CREDENTIAL_BOUNDARY_ID
        assert item["source_config_blocker_id"].startswith("VSPCFGB-")
        assert item["source_readiness_blocker_id"].startswith("VSPPB-")
        assert item["source_receipt_line_id"].startswith("VSPRL-")
        assert item["source_finding_id"].startswith("VSPRCF-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["blocker_status"] == "REAL_CREDENTIAL_BOUNDARY_BLOCKER_ACTIVE_CARRIED_FROM_GP061"
        assert item["blocks_provider_configuration"] is True
        assert item["blocks_provider_read_write"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False
        assert item["resolved"] is False


def test_gp062_event_log_is_real_and_seeded(credential_db):
    events = get_storage_provider_credential_boundary_events(credential_db)

    assert events["pack"]["id"] == "VAULT_GP062"
    assert events["real_sqlite_backed"] is True
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_CREATED" in event_types
    assert "SOURCE_GP061_CONFIG_CONTRACT_ATTACHED" in event_types
    assert "REAL_CREDENTIAL_BOUNDARY_RULES_CREATED" in event_types
    assert "REAL_SECRET_REFERENCE_SLOTS_CREATED_SECRET_FREE" in event_types
    assert "REAL_CREDENTIAL_BOUNDARY_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "CREDENTIAL_BOUNDARY_LOCKS_CONFIRMED" in event_types

    for event in events["events"]:
        assert event["event_id"].startswith("VSPCBE-")
        assert event["credential_boundary_id"] == DEFAULT_CREDENTIAL_BOUNDARY_ID
        assert isinstance(event["event_payload"], dict)
        assert event["created_at"]


def test_gp062_can_write_real_event_without_storing_or_configuring_secrets(credential_db):
    before = get_storage_provider_credential_boundary_events(credential_db)["event_count"]

    written = record_storage_provider_credential_boundary_event(
        "OWNER_GP062_CREDENTIAL_BOUNDARY_OBSERVED",
        {"reviewer": "owner", "note": "reviewed real GP062 credential boundary"},
        credential_db,
    )

    after = get_storage_provider_credential_boundary_events(credential_db)
    boundary = get_storage_provider_credential_boundary_record(credential_db)["credential_boundary"]
    rules = get_storage_provider_credential_boundary_rules(credential_db)
    slots = get_storage_provider_secret_reference_slots(credential_db)

    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPCBE-")
    assert written["credential_boundary_id"] == DEFAULT_CREDENTIAL_BOUNDARY_ID
    assert written["secret_values_stored"] is False
    assert written["secret_values_present"] is False
    assert written["token_material_present"] is False
    assert written["credentials_configured"] is False
    assert written["secret_references_activated"] is False
    assert written["provider_configured"] is False
    assert written["provider_connection_tested"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

    assert after["event_count"] == before + 1
    assert "OWNER_GP062_CREDENTIAL_BOUNDARY_OBSERVED" in {event["event_type"] for event in after["events"]}

    assert boundary["secret_values_stored"] is False
    assert boundary["secret_values_present"] is False
    assert boundary["credentials_configured"] is False
    assert boundary["provider_configured"] is False
    assert rules["secret_values_present_count"] == 0
    assert rules["credentials_configured_count"] == 0
    assert slots["secret_value_present_count"] == 0
    assert slots["reference_activated_count"] == 0


def test_gp062_validation_passes_real_locked_credential_boundary(credential_db):
    validation = validate_storage_provider_credential_boundary(credential_db)

    assert validation["pack"]["id"] == "VAULT_GP062"
    assert validation["validation_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["passed_count"] == validation["check_count"]
    assert validation["real_sqlite_backed"] is True
    assert validation["safe_to_continue_to_gp063"] is True

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_CREDENTIAL_BOUNDARY_EXISTS" in codes
    assert "SOURCE_GP061_CONFIG_CONTRACT_ATTACHED" in codes
    assert "CREDENTIAL_BOUNDARY_READY" in codes
    assert "REAL_BOUNDARY_RULE_ROWS_EXIST" in codes
    assert "NO_RULE_SECRET_VALUES_PRESENT" in codes
    assert "NO_RULE_TOKEN_MATERIAL_PRESENT" in codes
    assert "REAL_SECRET_REFERENCE_SLOTS_EXIST" in codes
    assert "NO_SECRET_REFERENCES_CREATED" in codes
    assert "NO_SECRET_REFERENCES_ACTIVATED" in codes
    assert "NO_SLOT_SECRET_VALUES_PRESENT" in codes
    assert "NO_SLOT_TOKEN_MATERIAL_PRESENT" in codes
    assert "REAL_CREDENTIAL_BLOCKERS_CARRIED_FORWARD" in codes
    assert "NO_BOUNDARY_SECRET_VALUES_STORED" in codes
    assert "NO_CREDENTIALS_CONFIGURED" in codes
    assert "NO_PROVIDER_CONNECTION_TESTED" in codes
    assert "NO_EXPORT" in codes
    assert "NO_EXECUTION" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "EVENT_LOG_EXISTS" in codes


def test_gp062_home_payload_has_truth_routes_and_next_step(credential_db):
    home = get_real_storage_provider_credential_boundary_home(credential_db)

    assert home["pack"]["id"] == "VAULT_GP062"
    assert home["credential_truth"]["real_storage_provider_credential_boundary_ready"] is True
    assert home["credential_truth"]["real_sqlite_backed"] is True
    assert home["credential_truth"]["real_schema_ready"] is True
    assert home["credential_truth"]["real_credential_boundary_exists"] is True
    assert home["credential_truth"]["real_credential_rule_rows_exist"] is True
    assert home["credential_truth"]["real_secret_reference_slot_rows_exist"] is True
    assert home["credential_truth"]["real_credential_blocker_rows_exist"] is True
    assert home["credential_truth"]["real_event_log_exists"] is True
    assert home["credential_truth"]["source_gp061_config_contract_attached"] is True
    assert home["credential_truth"]["validation_passed"] is True
    assert home["credential_truth"]["secret_values_stored_count"] == 0
    assert home["credential_truth"]["secret_values_present_count"] == 0
    assert home["credential_truth"]["token_material_present_count"] == 0
    assert home["credential_truth"]["reference_created_count"] == 0
    assert home["credential_truth"]["reference_activated_count"] == 0
    assert home["credential_truth"]["credentials_configured"] is False
    assert home["credential_truth"]["provider_configured"] is False
    assert home["credential_truth"]["export_enabled"] is False
    assert home["credential_truth"]["execution_enabled"] is False
    assert home["credential_truth"]["vault_done"] is False

    routes = home["routes"]
    assert routes["route"] == "/vault/real-storage-provider-credential-boundary"
    assert routes["json_route"] == "/vault/real-storage-provider-credential-boundary.json"
    assert routes["record_route"] == "/vault/storage-provider-credential-boundary-record.json"
    assert routes["rules_route"] == "/vault/storage-provider-credential-boundary-rules.json"
    assert routes["slots_route"] == "/vault/storage-provider-secret-reference-slots.json"
    assert routes["blockers_route"] == "/vault/storage-provider-credential-boundary-blockers.json"
    assert routes["events_route"] == "/vault/storage-provider-credential-boundary-events.json"
    assert routes["validation_route"] == "/vault/storage-provider-credential-boundary-validation.json"
    assert routes["next_step_route"] == "/vault/storage-provider-credential-boundary-next-step.json"
    assert routes["gp062_status_route"] == "/vault/gp062-status.json"

    assert home["next_step"]["next_pack"] == "VAULT_GP063_REAL_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER"
    assert home["next_step"]["safe_to_continue_to_gp063"] is True
    assert home["next_step"]["vault_done"] is False
    assert home["next_step"]["clouds_should_continue"] is False


def test_gp062_status_ready_real_secret_free_and_locked(credential_db):
    status = get_gp062_status(credential_db)
    gp062 = status["gp062_status"]

    assert status["pack"]["id"] == "VAULT_GP062"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert status["pack"]["section_range"] == "GP061-GP070"

    assert gp062["ready"] is True
    assert gp062["real_storage_provider_credential_boundary_ready"] is True
    assert gp062["real_sqlite_backed"] is True
    assert gp062["real_schema_ready"] is True
    assert gp062["real_boundary_count"] == 1
    assert gp062["real_rule_count"] == EXPECTED_RULES
    assert gp062["real_slot_count"] == EXPECTED_SLOTS
    assert gp062["real_blocker_count"] == EXPECTED_BLOCKERS
    assert gp062["source_gp061_config_contract_attached"] is True
    assert gp062["credential_boundary_ready"] is True
    assert gp062["credential_model_ready"] is True
    assert gp062["secret_reference_slots_ready"] is True
    assert gp062["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert gp062["rule_code_count"] == len(BOUNDARY_RULES)
    assert gp062["slot_code_count"] == len(SECRET_REFERENCE_SLOT_SPECS)
    assert gp062["rule_verified_count"] == 0
    assert gp062["reference_created_count"] == 0
    assert gp062["reference_activated_count"] == 0
    assert gp062["secret_values_stored_count"] == 0
    assert gp062["secret_values_present_count"] == 0
    assert gp062["token_material_present_count"] == 0
    assert gp062["blocks_provider_configuration_count"] == EXPECTED_BLOCKERS
    assert gp062["blocks_provider_read_write_count"] == EXPECTED_BLOCKERS
    assert gp062["blocks_export_count"] == EXPECTED_BLOCKERS
    assert gp062["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert gp062["tower_review_granted_count"] == 0
    assert gp062["resolved_count"] == 0
    assert gp062["validation_ready"] is True
    assert gp062["validation_passed"] is True
    assert gp062["safe_to_continue_to_gp063"] is True
    assert gp062["vault_done"] is False
    assert gp062["foundation_status"] == "credential_boundary_ready_safe_to_continue_not_done"

    assert gp062["secret_values_stored"] is False
    assert gp062["secret_values_present"] is False
    assert gp062["token_material_present"] is False
    assert gp062["credentials_configured"] is False
    assert gp062["secret_references_activated"] is False
    assert gp062["provider_endpoint_configured"] is False
    assert gp062["storage_container_configured"] is False
    assert gp062["encryption_configured"] is False
    assert gp062["provider_configuration_ready"] is False
    assert gp062["provider_configured"] is False
    assert gp062["provider_read_enabled"] is False
    assert gp062["provider_write_enabled"] is False
    assert gp062["provider_connection_tested"] is False
    assert gp062["object_body_view_enabled"] is False
    assert gp062["direct_upload_enabled"] is False
    assert gp062["export_enabled"] is False
    assert gp062["execution_enabled"] is False
    assert gp062["clouds_status"] == "parked_do_not_continue_from_vault_gp062"
    assert gp062["next_pack"] == "VAULT_GP063_REAL_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER"


def test_gp062_next_step_points_to_gp063_secret_reference_ledger():
    next_step = get_storage_provider_credential_boundary_next_step()["next_step"]

    assert next_step["current_section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert next_step["current_section_range"] == "GP061-GP070"
    assert next_step["next_pack"] == "VAULT_GP063_REAL_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER"
    assert next_step["next_pack_title"] == "Real Storage Provider Secret Reference Ledger"
    assert next_step["safe_to_continue_to_gp063"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

    note = next_step["owner_notebook_note"].lower()
    assert "secret-reference ledger" in note
    assert "storing no actual secret material" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "real sqlite credential boundary" in rules
    assert "secret-reference slot rows" in rules
    assert "real storage provider secret reference ledger" in rules
    assert "do not store actual provider secrets" in rules
    assert "do not store tokens" in rules
    assert "do not activate secret references yet" in rules
    assert "do not configure credentials yet" in rules
    assert "do not unlock export" in rules
    assert "do not unlock execution" in rules
    assert "do not treat vault as done" in rules


def test_gp062_html_is_dark_and_mentions_secret_free_boundary(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "html_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "html_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "html_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "html_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "html_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "html_readiness.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB", str(tmp_path / "html_config.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB", str(tmp_path / "html_credential.sqlite"))

    html = render_real_storage_provider_credential_boundary_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Credential Boundary" in html
    assert "Real Storage Provider Configuration Layer" in html
    assert "Archive Vault" in html
    assert "GP062" in html
    assert "Credential boundary ready" in html
    assert "Secret-reference slots reserved" in html
    assert "Real SQLite-backed" in html
    assert "No secrets stored" in html
    assert "No credentials configured" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-credential-boundary.json" in html
    assert "/vault/gp062-status.json" in html

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


def test_gp062_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/real-storage-provider-credential-boundary",
        "/vault/real-storage-provider-credential-boundary.json",
        "/vault/storage-provider-credential-boundary-record.json",
        "/vault/storage-provider-credential-boundary-rules.json",
        "/vault/storage-provider-secret-reference-slots.json",
        "/vault/storage-provider-credential-boundary-blockers.json",
        "/vault/storage-provider-credential-boundary-events.json",
        "/vault/storage-provider-credential-boundary-validation.json",
        "/vault/storage-provider-credential-boundary-next-step.json",
        "/vault/gp062-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp062_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "routes_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "routes_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "routes_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "routes_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "routes_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "routes_readiness.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB", str(tmp_path / "routes_config.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB", str(tmp_path / "routes_credential.sqlite"))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/real-storage-provider-credential-boundary",
        "/vault/real-storage-provider-credential-boundary.json",
        "/vault/storage-provider-credential-boundary-record.json",
        "/vault/storage-provider-credential-boundary-rules.json",
        "/vault/storage-provider-secret-reference-slots.json",
        "/vault/storage-provider-credential-boundary-blockers.json",
        "/vault/storage-provider-credential-boundary-events.json",
        "/vault/storage-provider-credential-boundary-validation.json",
        "/vault/storage-provider-credential-boundary-next-step.json",
        "/vault/gp062-status.json",
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
                assert b"Vault Real Storage Provider Credential Boundary" in response.data
