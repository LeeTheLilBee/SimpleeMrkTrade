"""
Tests for VAULT GIANT PACK 066 — Real Storage Provider Connection Test Lock Contract
"""

from pathlib import Path

import pytest

from vault.real_storage_provider_connection_test_lock_contract_service import (
    CONNECTION_TEST_POLICIES,
    CONNECTION_TEST_REQUIREMENT_SPECS,
    DEFAULT_CONNECTION_TEST_LOCK_CONTRACT_ID,
    ensure_storage_provider_connection_test_lock_contract_schema,
    get_gp066_status,
    get_real_storage_provider_connection_test_lock_contract_home,
    get_storage_provider_connection_test_blockers,
    get_storage_provider_connection_test_events,
    get_storage_provider_connection_test_lock_contract_record,
    get_storage_provider_connection_test_next_step,
    get_storage_provider_connection_test_policies,
    get_storage_provider_connection_test_requirements,
    initialize_real_storage_provider_connection_test_lock_contract,
    record_storage_provider_connection_test_event,
    render_real_storage_provider_connection_test_lock_contract_page,
    validate_storage_provider_connection_test_lock_contract,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROVIDER_CANDIDATES = 5
EXPECTED_REQUIREMENTS = EXPECTED_PROVIDER_CANDIDATES * len(CONNECTION_TEST_REQUIREMENT_SPECS)
EXPECTED_POLICIES = len(CONNECTION_TEST_POLICIES)
EXPECTED_BLOCKERS = 140


@pytest.fixture()
def connection_db(tmp_path, monkeypatch):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "selection_registry.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "capability_contract.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "risk_criteria_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "selection_review_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "prep_readiness.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB", str(tmp_path / "config_contract.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB", str(tmp_path / "credential_boundary.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB", str(tmp_path / "secret_reference_ledger.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT_DB", str(tmp_path / "endpoint_namespace_contract.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT_DB", str(tmp_path / "encryption_policy_contract.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT_DB", str(tmp_path / "connection_test_lock_contract.sqlite"))
    return str(tmp_path / "connection_test_lock_contract.sqlite")


def test_gp066_schema_is_real_sqlite_backed(connection_db):
    result = ensure_storage_provider_connection_test_lock_contract_schema(connection_db)
    db_path = Path(result["db_path"])

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert db_path.exists()
    assert "vault_storage_provider_connection_test_lock_contracts" in result["tables"]
    assert "vault_storage_provider_connection_test_requirements" in result["tables"]
    assert "vault_storage_provider_connection_test_policies" in result["tables"]
    assert "vault_storage_provider_connection_test_blockers" in result["tables"]
    assert "vault_storage_provider_connection_test_events" in result["tables"]


def test_gp066_initialize_creates_real_contract_requirements_policies_blockers_events(connection_db):
    result = initialize_real_storage_provider_connection_test_lock_contract(connection_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["connection_test_lock_contract_id"] == DEFAULT_CONNECTION_TEST_LOCK_CONTRACT_ID
    assert result["contract_count"] == 1
    assert result["requirement_count"] == EXPECTED_REQUIREMENTS
    assert result["policy_count"] == EXPECTED_POLICIES
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_connection_test_lock_contract(connection_db)
    assert second["contract_count"] == 1
    assert second["requirement_count"] == EXPECTED_REQUIREMENTS
    assert second["policy_count"] == EXPECTED_POLICIES
    assert second["blocker_count"] == EXPECTED_BLOCKERS
    assert second["event_count"] >= 6


def test_gp066_contract_record_is_real_and_sourced_from_gp065(connection_db):
    contract = get_storage_provider_connection_test_lock_contract_record(connection_db)["connection_test_lock_contract"]

    assert contract["connection_test_lock_contract_id"] == DEFAULT_CONNECTION_TEST_LOCK_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP066"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert contract["section_range"] == "GP061-GP070"
    assert contract["source_encryption_policy_contract_id"] == "VSPEPC-GP065-001"
    assert contract["source_encryption_policy_pack_id"] == "VAULT_GP065"
    assert contract["contract_status"] == "REAL_CONNECTION_TEST_LOCK_CONTRACT_OPEN_TOWER_LOCKED"
    assert contract["tower_authority_status"] == "TOWER_REVIEW_REQUIRED_NOT_GRANTED"

    data = contract["contract_data"]
    assert data["contract_type"] == "REAL_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT"
    assert data["real_durable_connection_test_lock_contract"] is True
    assert data["metadata_source"] == "VAULT_GP065_REAL_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT"
    assert data["source_encryption_policy_contract_id"] == "VSPEPC-GP065-001"
    assert data["source_encryption_policy_pack_id"] == "VAULT_GP065"
    assert data["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert data["requirement_code_count"] == len(CONNECTION_TEST_REQUIREMENT_SPECS)
    assert data["requirement_count"] == EXPECTED_REQUIREMENTS
    assert data["policy_count"] == EXPECTED_POLICIES
    assert data["carried_blocker_count"] == EXPECTED_BLOCKERS
    assert data["safe_to_continue_to_gp067"] is True


def test_gp066_contract_keeps_connection_and_provider_operations_locked(connection_db):
    contract = get_storage_provider_connection_test_lock_contract_record(connection_db)["connection_test_lock_contract"]

    assert contract["connection_test_lock_contract_ready"] is True
    assert contract["connection_test_requirements_ready"] is True
    assert contract["connection_test_policy_ready"] is True
    assert contract["connection_test_locked"] is True
    assert contract["connection_probe_alias_only"] is True
    assert contract["connection_probe_configured"] is False
    assert contract["connection_test_configured"] is False
    assert contract["connection_test_attempted"] is False
    assert contract["connection_test_passed"] is False
    assert contract["connection_test_failed"] is False
    assert contract["connection_receipt_created"] is False
    assert contract["actual_secret_values_stored"] is False
    assert contract["secret_values_present"] is False
    assert contract["token_material_present"] is False
    assert contract["encrypted_secret_payload_present"] is False
    assert contract["key_material_stored"] is False
    assert contract["kms_key_id_stored"] is False
    assert contract["key_locator_present"] is False
    assert contract["encryption_policy_configured"] is False
    assert contract["secret_references_created"] is False
    assert contract["secret_references_activated"] is False
    assert contract["credentials_configured"] is False
    assert contract["provider_endpoint_configured"] is False
    assert contract["storage_container_configured"] is False
    assert contract["namespace_configured"] is False
    assert contract["provider_configuration_ready"] is False
    assert contract["provider_configured"] is False
    assert contract["provider_read_enabled"] is False
    assert contract["provider_write_enabled"] is False
    assert contract["provider_connection_tested"] is False
    assert contract["object_body_view_enabled"] is False
    assert contract["direct_upload_enabled"] is False
    assert contract["export_enabled"] is False
    assert contract["execution_enabled"] is False
    assert contract["vault_done"] is False


def test_gp066_requirements_are_real_and_locked(connection_db):
    payload = get_storage_provider_connection_test_requirements(connection_db)

    assert payload["pack"]["id"] == "VAULT_GP066"
    assert payload["real_sqlite_backed"] is True
    assert payload["requirement_count"] == EXPECTED_REQUIREMENTS
    assert payload["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert payload["requirement_code_count"] == len(CONNECTION_TEST_REQUIREMENT_SPECS)
    assert payload["requirement_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["requirement_verified_count"] == 0
    assert payload["connection_test_locked_count"] == EXPECTED_REQUIREMENTS
    assert payload["connection_probe_alias_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["connection_probe_configured_count"] == 0
    assert payload["connection_test_configured_count"] == 0
    assert payload["connection_test_attempted_count"] == 0
    assert payload["connection_test_passed_count"] == 0
    assert payload["connection_test_failed_count"] == 0
    assert payload["connection_receipt_created_count"] == 0
    assert payload["credentials_configured_count"] == 0
    assert payload["secret_references_activated_count"] == 0
    assert payload["provider_endpoint_configured_count"] == 0
    assert payload["storage_container_configured_count"] == 0
    assert payload["namespace_configured_count"] == 0
    assert payload["encryption_policy_configured_count"] == 0
    assert payload["provider_connection_tested_count"] == 0
    assert payload["provider_read_enabled_count"] == 0
    assert payload["provider_write_enabled_count"] == 0
    assert payload["object_body_view_enabled_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0
    assert payload["tower_review_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["tower_review_granted_count"] == 0

    codes = {item["requirement_code"] for item in payload["requirements"]}
    expected_codes = {item["requirement_code"] for item in CONNECTION_TEST_REQUIREMENT_SPECS}
    assert codes == expected_codes

    for item in payload["requirements"]:
        assert item["connection_test_requirement_id"].startswith("VSPCTR-")
        assert item["connection_test_lock_contract_id"] == DEFAULT_CONNECTION_TEST_LOCK_CONTRACT_ID
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["requirement_status"] == "REAL_CONNECTION_TEST_REQUIREMENT_RECORDED_LOCKED_TOWER_LOCKED"
        assert item["requirement_required"] is True
        assert item["requirement_verified"] is False
        assert item["connection_test_locked"] is True
        assert item["connection_probe_alias_only"] is True
        assert item["connection_probe_configured"] is False
        assert item["connection_test_configured"] is False
        assert item["connection_test_attempted"] is False
        assert item["provider_connection_tested"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False


def test_gp066_policies_are_real_and_locked(connection_db):
    payload = get_storage_provider_connection_test_policies(connection_db)

    assert payload["pack"]["id"] == "VAULT_GP066"
    assert payload["real_sqlite_backed"] is True
    assert payload["policy_count"] == EXPECTED_POLICIES
    assert payload["policy_code_count"] == EXPECTED_POLICIES
    assert payload["policy_required_count"] == EXPECTED_POLICIES
    assert payload["policy_verified_count"] == 0
    assert payload["connection_probe_configured_count"] == 0
    assert payload["connection_test_configured_count"] == 0
    assert payload["connection_test_attempted_count"] == 0
    assert payload["connection_test_passed_count"] == 0
    assert payload["connection_test_failed_count"] == 0
    assert payload["connection_receipt_created_count"] == 0
    assert payload["actual_secret_values_stored_count"] == 0
    assert payload["secret_values_present_count"] == 0
    assert payload["token_material_present_count"] == 0
    assert payload["secret_references_created_count"] == 0
    assert payload["secret_references_activated_count"] == 0
    assert payload["credentials_configured_count"] == 0
    assert payload["provider_connection_tested_count"] == 0
    assert payload["provider_read_enabled_count"] == 0
    assert payload["provider_write_enabled_count"] == 0
    assert payload["object_body_view_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0
    assert payload["tower_review_required_count"] == EXPECTED_POLICIES
    assert payload["tower_review_granted_count"] == 0

    codes = {item["policy_code"] for item in payload["policies"]}
    expected_codes = {item["policy_code"] for item in CONNECTION_TEST_POLICIES}
    assert codes == expected_codes

    for item in payload["policies"]:
        assert item["connection_test_policy_id"].startswith("VSPCTP-")
        assert item["connection_test_lock_contract_id"] == DEFAULT_CONNECTION_TEST_LOCK_CONTRACT_ID
        assert item["policy_status"] == "REAL_CONNECTION_TEST_POLICY_RECORDED_TOWER_LOCKED"
        assert item["policy_required"] is True
        assert item["policy_verified"] is False
        assert item["connection_probe_configured"] is False
        assert item["connection_test_configured"] is False
        assert item["connection_test_attempted"] is False
        assert item["connection_test_passed"] is False
        assert item["connection_test_failed"] is False
        assert item["connection_receipt_created"] is False
        assert item["provider_connection_tested"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False


def test_gp066_blockers_are_real_and_carried_from_gp065(connection_db):
    payload = get_storage_provider_connection_test_blockers(connection_db)

    assert payload["pack"]["id"] == "VAULT_GP066"
    assert payload["real_sqlite_backed"] is True
    assert payload["blocker_count"] == EXPECTED_BLOCKERS
    assert payload["capability_blocker_count"] == 60
    assert payload["criteria_blocker_count"] == 40
    assert payload["risk_blocker_count"] == 40
    assert payload["blocks_provider_configuration_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_read_write_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_body_view_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_export_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_required_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_granted_count"] == 0
    assert payload["risk_accepted_count"] == 0
    assert payload["risk_waived_count"] == 0
    assert payload["mitigation_approved_count"] == 0
    assert payload["resolved_count"] == 0

    for item in payload["blockers"]:
        assert item["connection_test_blocker_id"].startswith("VSPCTB-")
        assert item["connection_test_lock_contract_id"] == DEFAULT_CONNECTION_TEST_LOCK_CONTRACT_ID
        assert item["source_encryption_blocker_id"].startswith("VSPEB-")
        assert item["source_endpoint_namespace_blocker_id"].startswith("VSPENB-")
        assert item["source_ledger_blocker_id"].startswith("VSPSRLB-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["blocker_status"] == "REAL_CONNECTION_TEST_BLOCKER_ACTIVE_CARRIED_FROM_GP065"
        assert item["blocks_provider_configuration"] is True
        assert item["blocks_provider_read_write"] is True
        assert item["blocks_object_body_view"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False
        assert item["resolved"] is False


def test_gp066_event_log_is_real_and_seeded(connection_db):
    events = get_storage_provider_connection_test_events(connection_db)

    assert events["pack"]["id"] == "VAULT_GP066"
    assert events["real_sqlite_backed"] is True
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP065_ENCRYPTION_POLICY_CONTRACT_ATTACHED" in event_types
    assert "REAL_CONNECTION_TEST_REQUIREMENTS_CREATED_LOCKED" in event_types
    assert "REAL_CONNECTION_TEST_POLICIES_CREATED" in event_types
    assert "REAL_CONNECTION_TEST_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "CONNECTION_TEST_LOCKS_CONFIRMED" in event_types


def test_gp066_can_write_real_event_without_testing_connection(connection_db):
    before = get_storage_provider_connection_test_events(connection_db)["event_count"]

    written = record_storage_provider_connection_test_event(
        "OWNER_GP066_CONNECTION_TEST_LOCK_CONTRACT_OBSERVED",
        {"reviewer": "owner", "note": "reviewed real GP066 connection test lock contract"},
        connection_db,
    )

    after = get_storage_provider_connection_test_events(connection_db)
    contract = get_storage_provider_connection_test_lock_contract_record(connection_db)["connection_test_lock_contract"]
    requirements = get_storage_provider_connection_test_requirements(connection_db)
    policies = get_storage_provider_connection_test_policies(connection_db)

    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPCTEVT-")
    assert written["connection_test_lock_contract_id"] == DEFAULT_CONNECTION_TEST_LOCK_CONTRACT_ID
    assert written["connection_test_locked"] is True
    assert written["connection_probe_configured"] is False
    assert written["connection_test_attempted"] is False
    assert written["provider_connection_tested"] is False
    assert written["provider_read_enabled"] is False
    assert written["provider_write_enabled"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

    assert after["event_count"] == before + 1
    assert "OWNER_GP066_CONNECTION_TEST_LOCK_CONTRACT_OBSERVED" in {event["event_type"] for event in after["events"]}

    assert contract["connection_test_attempted"] is False
    assert contract["provider_connection_tested"] is False
    assert requirements["connection_test_attempted_count"] == 0
    assert requirements["provider_connection_tested_count"] == 0
    assert policies["connection_test_attempted_count"] == 0
    assert policies["provider_connection_tested_count"] == 0


def test_gp066_validation_passes_real_locked_connection_test_contract(connection_db):
    validation = validate_storage_provider_connection_test_lock_contract(connection_db)

    assert validation["pack"]["id"] == "VAULT_GP066"
    assert validation["validation_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["passed_count"] == validation["check_count"]
    assert validation["real_sqlite_backed"] is True
    assert validation["safe_to_continue_to_gp067"] is True

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_CONNECTION_TEST_LOCK_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP065_ENCRYPTION_POLICY_CONTRACT_ATTACHED" in codes
    assert "CONNECTION_TEST_LOCK_CONTRACT_READY" in codes
    assert "CONNECTION_TEST_LOCKED" in codes
    assert "REAL_CONNECTION_TEST_REQUIREMENTS_EXIST" in codes
    assert "NO_REQUIREMENT_CONNECTION_PROBE_CONFIGURED" in codes
    assert "NO_REQUIREMENT_CONNECTION_TEST_ATTEMPTED" in codes
    assert "REAL_CONNECTION_TEST_POLICIES_EXIST" in codes
    assert "REAL_CONNECTION_TEST_BLOCKERS_CARRIED_FORWARD" in codes
    assert "NO_CONTRACT_CONNECTION_PROBE_CONFIGURED" in codes
    assert "NO_CONTRACT_CONNECTION_TEST_ATTEMPTED" in codes
    assert "NO_PROVIDER_CONNECTION_TESTED" in codes
    assert "NO_EXPORT" in codes
    assert "NO_EXECUTION" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "EVENT_LOG_EXISTS" in codes


def test_gp066_home_payload_has_truth_routes_and_next_step(connection_db):
    home = get_real_storage_provider_connection_test_lock_contract_home(connection_db)

    assert home["pack"]["id"] == "VAULT_GP066"
    assert home["connection_test_truth"]["real_storage_provider_connection_test_lock_contract_ready"] is True
    assert home["connection_test_truth"]["real_sqlite_backed"] is True
    assert home["connection_test_truth"]["real_schema_ready"] is True
    assert home["connection_test_truth"]["real_connection_test_lock_contract_exists"] is True
    assert home["connection_test_truth"]["real_connection_test_requirement_rows_exist"] is True
    assert home["connection_test_truth"]["real_connection_test_policy_rows_exist"] is True
    assert home["connection_test_truth"]["real_connection_test_blocker_rows_exist"] is True
    assert home["connection_test_truth"]["real_event_log_exists"] is True
    assert home["connection_test_truth"]["source_gp065_encryption_policy_contract_attached"] is True
    assert home["connection_test_truth"]["validation_passed"] is True
    assert home["connection_test_truth"]["connection_probe_configured_count"] == 0
    assert home["connection_test_truth"]["connection_test_attempted_count"] == 0
    assert home["connection_test_truth"]["provider_connection_tested_count"] == 0
    assert home["connection_test_truth"]["export_enabled"] is False
    assert home["connection_test_truth"]["execution_enabled"] is False
    assert home["connection_test_truth"]["vault_done"] is False

    routes = home["routes"]
    assert routes["route"] == "/vault/real-storage-provider-connection-test-lock-contract"
    assert routes["json_route"] == "/vault/real-storage-provider-connection-test-lock-contract.json"
    assert routes["record_route"] == "/vault/storage-provider-connection-test-lock-contract-record.json"
    assert routes["requirements_route"] == "/vault/storage-provider-connection-test-requirements.json"
    assert routes["policies_route"] == "/vault/storage-provider-connection-test-policies.json"
    assert routes["blockers_route"] == "/vault/storage-provider-connection-test-blockers.json"
    assert routes["events_route"] == "/vault/storage-provider-connection-test-events.json"
    assert routes["validation_route"] == "/vault/storage-provider-connection-test-validation.json"
    assert routes["next_step_route"] == "/vault/storage-provider-connection-test-next-step.json"
    assert routes["gp066_status_route"] == "/vault/gp066-status.json"

    assert home["next_step"]["next_pack"] == "VAULT_GP067_REAL_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT"
    assert home["next_step"]["safe_to_continue_to_gp067"] is True
    assert home["next_step"]["vault_done"] is False
    assert home["next_step"]["clouds_should_continue"] is False


def test_gp066_status_ready_real_locked(connection_db):
    status = get_gp066_status(connection_db)
    gp066 = status["gp066_status"]

    assert status["pack"]["id"] == "VAULT_GP066"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert status["pack"]["section_range"] == "GP061-GP070"

    assert gp066["ready"] is True
    assert gp066["real_storage_provider_connection_test_lock_contract_ready"] is True
    assert gp066["real_sqlite_backed"] is True
    assert gp066["real_schema_ready"] is True
    assert gp066["real_contract_count"] == 1
    assert gp066["real_requirement_count"] == EXPECTED_REQUIREMENTS
    assert gp066["real_policy_count"] == EXPECTED_POLICIES
    assert gp066["real_blocker_count"] == EXPECTED_BLOCKERS
    assert gp066["source_gp065_encryption_policy_contract_attached"] is True
    assert gp066["connection_test_lock_contract_ready"] is True
    assert gp066["connection_test_requirements_ready"] is True
    assert gp066["connection_test_policy_ready"] is True
    assert gp066["connection_test_locked"] is True
    assert gp066["connection_probe_alias_only"] is True
    assert gp066["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert gp066["requirement_code_count"] == len(CONNECTION_TEST_REQUIREMENT_SPECS)
    assert gp066["policy_code_count"] == EXPECTED_POLICIES
    assert gp066["connection_probe_configured_count"] == 0
    assert gp066["connection_test_configured_count"] == 0
    assert gp066["connection_test_attempted_count"] == 0
    assert gp066["connection_test_passed_count"] == 0
    assert gp066["connection_test_failed_count"] == 0
    assert gp066["connection_receipt_created_count"] == 0
    assert gp066["secret_value_present_count"] == 0
    assert gp066["token_material_present_count"] == 0
    assert gp066["credentials_configured_count"] == 0
    assert gp066["provider_connection_tested_count"] == 0
    assert gp066["provider_read_enabled_count"] == 0
    assert gp066["provider_write_enabled_count"] == 0
    assert gp066["blocks_provider_configuration_count"] == EXPECTED_BLOCKERS
    assert gp066["blocks_provider_read_write_count"] == EXPECTED_BLOCKERS
    assert gp066["blocks_object_body_view_count"] == EXPECTED_BLOCKERS
    assert gp066["blocks_export_count"] == EXPECTED_BLOCKERS
    assert gp066["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert gp066["tower_review_granted_count"] == 0
    assert gp066["resolved_count"] == 0
    assert gp066["validation_ready"] is True
    assert gp066["validation_passed"] is True
    assert gp066["safe_to_continue_to_gp067"] is True
    assert gp066["vault_done"] is False
    assert gp066["foundation_status"] == "connection_test_lock_contract_ready_safe_to_continue_not_done"

    assert gp066["connection_probe_configured"] is False
    assert gp066["connection_test_configured"] is False
    assert gp066["connection_test_attempted"] is False
    assert gp066["connection_test_passed"] is False
    assert gp066["connection_test_failed"] is False
    assert gp066["connection_receipt_created"] is False
    assert gp066["credentials_configured"] is False
    assert gp066["provider_connection_tested"] is False
    assert gp066["provider_read_enabled"] is False
    assert gp066["provider_write_enabled"] is False
    assert gp066["object_body_view_enabled"] is False
    assert gp066["direct_upload_enabled"] is False
    assert gp066["export_enabled"] is False
    assert gp066["execution_enabled"] is False
    assert gp066["clouds_status"] == "parked_do_not_continue_from_vault_gp066"
    assert gp066["next_pack"] == "VAULT_GP067_REAL_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT"


def test_gp066_next_step_points_to_gp067_write_path_lock_contract():
    next_step = get_storage_provider_connection_test_next_step()["next_step"]

    assert next_step["current_section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert next_step["current_section_range"] == "GP061-GP070"
    assert next_step["next_pack"] == "VAULT_GP067_REAL_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT"
    assert next_step["next_pack_title"] == "Real Storage Provider Write Path Lock Contract"
    assert next_step["safe_to_continue_to_gp067"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "real sqlite connection-test lock contract" in rules
    assert "connection-test requirement rows" in rules
    assert "write path lock contract" in rules
    assert "do not configure connection probes" in rules
    assert "do not attempt provider connection tests" in rules
    assert "do not enable provider read or write" in rules
    assert "do not unlock export" in rules
    assert "do not unlock execution" in rules
    assert "do not treat vault as done" in rules


def test_gp066_html_is_dark_and_mentions_connection_test_lock_contract(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "html_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "html_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "html_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "html_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "html_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "html_readiness.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB", str(tmp_path / "html_config.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB", str(tmp_path / "html_credential.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB", str(tmp_path / "html_ledger.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT_DB", str(tmp_path / "html_endpoint.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT_DB", str(tmp_path / "html_encryption.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT_DB", str(tmp_path / "html_connection.sqlite"))

    html = render_real_storage_provider_connection_test_lock_contract_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Connection Test Lock Contract" in html
    assert "Real Storage Provider Configuration Layer" in html
    assert "Archive Vault" in html
    assert "GP066" in html
    assert "Connection-test lock ready" in html
    assert "Real SQLite-backed" in html
    assert "No connection probe" in html
    assert "No provider test" in html
    assert "No read/write" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-connection-test-lock-contract.json" in html
    assert "/vault/gp066-status.json" in html

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


def test_gp066_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/real-storage-provider-connection-test-lock-contract",
        "/vault/real-storage-provider-connection-test-lock-contract.json",
        "/vault/storage-provider-connection-test-lock-contract-record.json",
        "/vault/storage-provider-connection-test-requirements.json",
        "/vault/storage-provider-connection-test-policies.json",
        "/vault/storage-provider-connection-test-blockers.json",
        "/vault/storage-provider-connection-test-events.json",
        "/vault/storage-provider-connection-test-validation.json",
        "/vault/storage-provider-connection-test-next-step.json",
        "/vault/gp066-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp066_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "routes_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "routes_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "routes_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "routes_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "routes_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "routes_readiness.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB", str(tmp_path / "routes_config.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB", str(tmp_path / "routes_credential.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB", str(tmp_path / "routes_ledger.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT_DB", str(tmp_path / "routes_endpoint.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT_DB", str(tmp_path / "routes_encryption.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT_DB", str(tmp_path / "routes_connection.sqlite"))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/real-storage-provider-connection-test-lock-contract",
        "/vault/real-storage-provider-connection-test-lock-contract.json",
        "/vault/storage-provider-connection-test-lock-contract-record.json",
        "/vault/storage-provider-connection-test-requirements.json",
        "/vault/storage-provider-connection-test-policies.json",
        "/vault/storage-provider-connection-test-blockers.json",
        "/vault/storage-provider-connection-test-events.json",
        "/vault/storage-provider-connection-test-validation.json",
        "/vault/storage-provider-connection-test-next-step.json",
        "/vault/gp066-status.json",
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
                assert b"Vault Real Storage Provider Connection Test Lock Contract" in response.data
