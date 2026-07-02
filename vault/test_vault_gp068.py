"""
Tests for VAULT GIANT PACK 068 — Real Storage Provider Read Path Lock Contract
"""

from pathlib import Path

import pytest

from vault.real_storage_provider_read_path_lock_contract_service import (
    DEFAULT_READ_PATH_LOCK_CONTRACT_ID,
    READ_PATH_POLICIES,
    READ_PATH_REQUIREMENT_SPECS,
    ensure_storage_provider_read_path_lock_contract_schema,
    get_gp068_status,
    get_real_storage_provider_read_path_lock_contract_home,
    get_storage_provider_read_path_blockers,
    get_storage_provider_read_path_events,
    get_storage_provider_read_path_lock_contract_record,
    get_storage_provider_read_path_next_step,
    get_storage_provider_read_path_policies,
    get_storage_provider_read_path_requirements,
    initialize_real_storage_provider_read_path_lock_contract,
    record_storage_provider_read_path_event,
    render_real_storage_provider_read_path_lock_contract_page,
    validate_storage_provider_read_path_lock_contract,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROVIDER_CANDIDATES = 5
EXPECTED_REQUIREMENTS = EXPECTED_PROVIDER_CANDIDATES * len(READ_PATH_REQUIREMENT_SPECS)
EXPECTED_POLICIES = len(READ_PATH_POLICIES)
EXPECTED_BLOCKERS = 140


@pytest.fixture()
def read_db(tmp_path, monkeypatch):
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
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT_DB", str(tmp_path / "write_path_lock_contract.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT_DB", str(tmp_path / "read_path_lock_contract.sqlite"))
    return str(tmp_path / "read_path_lock_contract.sqlite")


def test_gp068_schema_is_real_sqlite_backed(read_db):
    result = ensure_storage_provider_read_path_lock_contract_schema(read_db)
    db_path = Path(result["db_path"])

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert db_path.exists()
    assert "vault_storage_provider_read_path_lock_contracts" in result["tables"]
    assert "vault_storage_provider_read_path_requirements" in result["tables"]
    assert "vault_storage_provider_read_path_policies" in result["tables"]
    assert "vault_storage_provider_read_path_blockers" in result["tables"]
    assert "vault_storage_provider_read_path_events" in result["tables"]


def test_gp068_initialize_creates_real_contract_requirements_policies_blockers_events(read_db):
    result = initialize_real_storage_provider_read_path_lock_contract(read_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["read_path_lock_contract_id"] == DEFAULT_READ_PATH_LOCK_CONTRACT_ID
    assert result["contract_count"] == 1
    assert result["requirement_count"] == EXPECTED_REQUIREMENTS
    assert result["policy_count"] == EXPECTED_POLICIES
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_read_path_lock_contract(read_db)
    assert second["contract_count"] == 1
    assert second["requirement_count"] == EXPECTED_REQUIREMENTS
    assert second["policy_count"] == EXPECTED_POLICIES
    assert second["blocker_count"] == EXPECTED_BLOCKERS
    assert second["event_count"] >= 6


def test_gp068_contract_record_is_real_and_sourced_from_gp067(read_db):
    contract = get_storage_provider_read_path_lock_contract_record(read_db)["read_path_lock_contract"]

    assert contract["read_path_lock_contract_id"] == DEFAULT_READ_PATH_LOCK_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP068"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert contract["section_range"] == "GP061-GP070"
    assert contract["source_write_path_lock_contract_id"] == "VSPWPLC-GP067-001"
    assert contract["source_write_path_pack_id"] == "VAULT_GP067"
    assert contract["contract_status"] == "REAL_READ_PATH_LOCK_CONTRACT_OPEN_TOWER_LOCKED"

    data = contract["contract_data"]
    assert data["contract_type"] == "REAL_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT"
    assert data["metadata_source"] == "VAULT_GP067_REAL_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT"
    assert data["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert data["requirement_count"] == EXPECTED_REQUIREMENTS
    assert data["policy_count"] == EXPECTED_POLICIES
    assert data["carried_blocker_count"] == EXPECTED_BLOCKERS
    assert data["safe_to_continue_to_gp069"] is True


def test_gp068_contract_keeps_read_write_object_export_execution_locked(read_db):
    contract = get_storage_provider_read_path_lock_contract_record(read_db)["read_path_lock_contract"]

    assert contract["read_path_lock_contract_ready"] is True
    assert contract["read_path_requirements_ready"] is True
    assert contract["read_path_policy_ready"] is True
    assert contract["read_path_locked"] is True
    assert contract["read_path_alias_only"] is True
    assert contract["read_path_configured"] is False
    assert contract["read_path_attempted"] is False
    assert contract["read_path_enabled"] is False
    assert contract["read_receipt_created"] is False
    assert contract["object_listing_configured"] is False
    assert contract["object_list_attempted"] is False
    assert contract["object_listed"] is False
    assert contract["object_body_read_attempted"] is False
    assert contract["object_body_read"] is False
    assert contract["object_body_view_enabled"] is False
    assert contract["credentials_configured"] is False
    assert contract["provider_endpoint_configured"] is False
    assert contract["storage_container_configured"] is False
    assert contract["namespace_configured"] is False
    assert contract["encryption_policy_configured"] is False
    assert contract["provider_connection_tested"] is False
    assert contract["write_path_configured"] is False
    assert contract["write_path_attempted"] is False
    assert contract["object_created"] is False
    assert contract["provider_read_enabled"] is False
    assert contract["provider_write_enabled"] is False
    assert contract["provider_object_read_claimed"] is False
    assert contract["provider_object_write_claimed"] is False
    assert contract["direct_upload_enabled"] is False
    assert contract["export_enabled"] is False
    assert contract["execution_enabled"] is False
    assert contract["vault_done"] is False


def test_gp068_requirements_are_real_and_locked(read_db):
    payload = get_storage_provider_read_path_requirements(read_db)

    assert payload["pack"]["id"] == "VAULT_GP068"
    assert payload["real_sqlite_backed"] is True
    assert payload["requirement_count"] == EXPECTED_REQUIREMENTS
    assert payload["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert payload["requirement_code_count"] == len(READ_PATH_REQUIREMENT_SPECS)
    assert payload["requirement_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["requirement_verified_count"] == 0
    assert payload["read_path_locked_count"] == EXPECTED_REQUIREMENTS
    assert payload["read_path_alias_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["read_path_configured_count"] == 0
    assert payload["read_path_attempted_count"] == 0
    assert payload["read_path_enabled_count"] == 0
    assert payload["read_receipt_created_count"] == 0
    assert payload["object_listing_configured_count"] == 0
    assert payload["object_list_attempted_count"] == 0
    assert payload["object_listed_count"] == 0
    assert payload["object_body_read_attempted_count"] == 0
    assert payload["object_body_read_count"] == 0
    assert payload["object_body_view_enabled_count"] == 0
    assert payload["credentials_configured_count"] == 0
    assert payload["secret_references_activated_count"] == 0
    assert payload["provider_endpoint_configured_count"] == 0
    assert payload["storage_container_configured_count"] == 0
    assert payload["namespace_configured_count"] == 0
    assert payload["encryption_policy_configured_count"] == 0
    assert payload["provider_connection_tested_count"] == 0
    assert payload["write_path_configured_count"] == 0
    assert payload["write_path_attempted_count"] == 0
    assert payload["object_created_count"] == 0
    assert payload["provider_read_enabled_count"] == 0
    assert payload["provider_write_enabled_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0
    assert payload["tower_review_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["tower_review_granted_count"] == 0

    codes = {item["requirement_code"] for item in payload["requirements"]}
    expected_codes = {item["requirement_code"] for item in READ_PATH_REQUIREMENT_SPECS}
    assert codes == expected_codes

    for item in payload["requirements"]:
        assert item["read_path_requirement_id"].startswith("VSPRPR-")
        assert item["read_path_lock_contract_id"] == DEFAULT_READ_PATH_LOCK_CONTRACT_ID
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["requirement_status"] == "REAL_READ_PATH_REQUIREMENT_RECORDED_LOCKED_TOWER_LOCKED"
        assert item["requirement_required"] is True
        assert item["requirement_verified"] is False
        assert item["read_path_locked"] is True
        assert item["read_path_alias_only"] is True
        assert item["read_path_configured"] is False
        assert item["read_path_attempted"] is False
        assert item["read_path_enabled"] is False
        assert item["object_listed"] is False
        assert item["object_body_read"] is False
        assert item["object_body_view_enabled"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["direct_upload_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False


def test_gp068_policies_are_real_and_locked(read_db):
    payload = get_storage_provider_read_path_policies(read_db)

    assert payload["pack"]["id"] == "VAULT_GP068"
    assert payload["real_sqlite_backed"] is True
    assert payload["policy_count"] == EXPECTED_POLICIES
    assert payload["policy_code_count"] == EXPECTED_POLICIES
    assert payload["policy_required_count"] == EXPECTED_POLICIES
    assert payload["policy_verified_count"] == 0
    assert payload["read_path_configured_count"] == 0
    assert payload["read_path_attempted_count"] == 0
    assert payload["read_path_enabled_count"] == 0
    assert payload["read_receipt_created_count"] == 0
    assert payload["object_listing_configured_count"] == 0
    assert payload["object_list_attempted_count"] == 0
    assert payload["object_listed_count"] == 0
    assert payload["object_body_read_attempted_count"] == 0
    assert payload["object_body_read_count"] == 0
    assert payload["object_body_view_enabled_count"] == 0
    assert payload["secret_values_present_count"] == 0
    assert payload["token_material_present_count"] == 0
    assert payload["secret_references_created_count"] == 0
    assert payload["secret_references_activated_count"] == 0
    assert payload["credentials_configured_count"] == 0
    assert payload["provider_read_enabled_count"] == 0
    assert payload["provider_write_enabled_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0
    assert payload["tower_review_required_count"] == EXPECTED_POLICIES
    assert payload["tower_review_granted_count"] == 0

    codes = {item["policy_code"] for item in payload["policies"]}
    expected_codes = {item["policy_code"] for item in READ_PATH_POLICIES}
    assert codes == expected_codes

    for item in payload["policies"]:
        assert item["read_path_policy_id"].startswith("VSPRPP-")
        assert item["read_path_lock_contract_id"] == DEFAULT_READ_PATH_LOCK_CONTRACT_ID
        assert item["policy_status"] == "REAL_READ_PATH_POLICY_RECORDED_TOWER_LOCKED"
        assert item["policy_required"] is True
        assert item["policy_verified"] is False
        assert item["read_path_configured"] is False
        assert item["read_path_attempted"] is False
        assert item["read_path_enabled"] is False
        assert item["object_listed"] is False
        assert item["object_body_read"] is False
        assert item["object_body_view_enabled"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["direct_upload_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False


def test_gp068_blockers_are_real_and_carried_from_gp067(read_db):
    payload = get_storage_provider_read_path_blockers(read_db)

    assert payload["pack"]["id"] == "VAULT_GP068"
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
        assert item["read_path_blocker_id"].startswith("VSPRPB-")
        assert item["read_path_lock_contract_id"] == DEFAULT_READ_PATH_LOCK_CONTRACT_ID
        assert item["source_write_path_blocker_id"].startswith("VSPWPB-")
        assert item["source_connection_test_blocker_id"].startswith("VSPCTB-")
        assert item["source_encryption_blocker_id"].startswith("VSPEB-")
        assert item["source_endpoint_namespace_blocker_id"].startswith("VSPENB-")
        assert item["source_ledger_blocker_id"].startswith("VSPSRLB-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["blocker_status"] == "REAL_READ_PATH_BLOCKER_ACTIVE_CARRIED_FROM_GP067"
        assert item["blocks_provider_configuration"] is True
        assert item["blocks_provider_read_write"] is True
        assert item["blocks_object_body_view"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False
        assert item["resolved"] is False


def test_gp068_event_log_is_real_and_seeded(read_db):
    events = get_storage_provider_read_path_events(read_db)

    assert events["pack"]["id"] == "VAULT_GP068"
    assert events["real_sqlite_backed"] is True
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP067_WRITE_PATH_LOCK_CONTRACT_ATTACHED" in event_types
    assert "REAL_READ_PATH_REQUIREMENTS_CREATED_LOCKED" in event_types
    assert "REAL_READ_PATH_POLICIES_CREATED" in event_types
    assert "REAL_READ_PATH_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "READ_PATH_LOCKS_CONFIRMED" in event_types


def test_gp068_can_write_real_event_without_reading_or_listing(read_db):
    before = get_storage_provider_read_path_events(read_db)["event_count"]

    written = record_storage_provider_read_path_event(
        "OWNER_GP068_READ_PATH_LOCK_CONTRACT_OBSERVED",
        {"reviewer": "owner", "note": "reviewed real GP068 read path lock contract"},
        read_db,
    )

    after = get_storage_provider_read_path_events(read_db)
    contract = get_storage_provider_read_path_lock_contract_record(read_db)["read_path_lock_contract"]
    requirements = get_storage_provider_read_path_requirements(read_db)
    policies = get_storage_provider_read_path_policies(read_db)

    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPRPEVT-")
    assert written["read_path_lock_contract_id"] == DEFAULT_READ_PATH_LOCK_CONTRACT_ID
    assert written["read_path_locked"] is True
    assert written["read_path_configured"] is False
    assert written["read_path_attempted"] is False
    assert written["object_listed"] is False
    assert written["object_body_read"] is False
    assert written["object_body_view_enabled"] is False
    assert written["provider_read_enabled"] is False
    assert written["provider_write_enabled"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

    assert after["event_count"] == before + 1
    assert "OWNER_GP068_READ_PATH_LOCK_CONTRACT_OBSERVED" in {event["event_type"] for event in after["events"]}

    assert contract["read_path_attempted"] is False
    assert contract["object_body_read"] is False
    assert requirements["read_path_attempted_count"] == 0
    assert requirements["object_body_read_count"] == 0
    assert policies["read_path_attempted_count"] == 0
    assert policies["object_body_read_count"] == 0


def test_gp068_validation_passes_real_locked_read_path_contract(read_db):
    validation = validate_storage_provider_read_path_lock_contract(read_db)

    assert validation["pack"]["id"] == "VAULT_GP068"
    assert validation["validation_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["passed_count"] == validation["check_count"]
    assert validation["real_sqlite_backed"] is True
    assert validation["safe_to_continue_to_gp069"] is True

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_READ_PATH_LOCK_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP067_WRITE_PATH_LOCK_CONTRACT_ATTACHED" in codes
    assert "READ_PATH_LOCK_CONTRACT_READY" in codes
    assert "READ_PATH_LOCKED" in codes
    assert "REAL_READ_PATH_REQUIREMENTS_EXIST" in codes
    assert "NO_REQUIREMENT_READ_PATH_CONFIGURED" in codes
    assert "NO_REQUIREMENT_READ_PATH_ATTEMPTED" in codes
    assert "NO_REQUIREMENT_OBJECT_BODY_READ" in codes
    assert "REAL_READ_PATH_POLICIES_EXIST" in codes
    assert "REAL_READ_PATH_BLOCKERS_CARRIED_FORWARD" in codes
    assert "NO_CONTRACT_READ_PATH_CONFIGURED" in codes
    assert "NO_CONTRACT_READ_PATH_ATTEMPTED" in codes
    assert "NO_PROVIDER_READ_WRITE" in codes
    assert "NO_DIRECT_UPLOAD" in codes
    assert "NO_EXPORT" in codes
    assert "NO_EXECUTION" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "EVENT_LOG_EXISTS" in codes


def test_gp068_home_payload_has_truth_routes_and_next_step(read_db):
    home = get_real_storage_provider_read_path_lock_contract_home(read_db)

    assert home["pack"]["id"] == "VAULT_GP068"
    assert home["read_path_truth"]["real_storage_provider_read_path_lock_contract_ready"] is True
    assert home["read_path_truth"]["real_sqlite_backed"] is True
    assert home["read_path_truth"]["real_schema_ready"] is True
    assert home["read_path_truth"]["real_read_path_lock_contract_exists"] is True
    assert home["read_path_truth"]["real_read_path_requirement_rows_exist"] is True
    assert home["read_path_truth"]["real_read_path_policy_rows_exist"] is True
    assert home["read_path_truth"]["real_read_path_blocker_rows_exist"] is True
    assert home["read_path_truth"]["real_event_log_exists"] is True
    assert home["read_path_truth"]["source_gp067_write_path_lock_contract_attached"] is True
    assert home["read_path_truth"]["validation_passed"] is True
    assert home["read_path_truth"]["read_path_configured_count"] == 0
    assert home["read_path_truth"]["read_path_attempted_count"] == 0
    assert home["read_path_truth"]["read_path_enabled_count"] == 0
    assert home["read_path_truth"]["object_listed_count"] == 0
    assert home["read_path_truth"]["object_body_read_count"] == 0
    assert home["read_path_truth"]["provider_read_enabled"] is False
    assert home["read_path_truth"]["provider_write_enabled"] is False
    assert home["read_path_truth"]["object_body_view_enabled"] is False
    assert home["read_path_truth"]["direct_upload_enabled"] is False
    assert home["read_path_truth"]["export_enabled"] is False
    assert home["read_path_truth"]["execution_enabled"] is False
    assert home["read_path_truth"]["vault_done"] is False

    routes = home["routes"]
    assert routes["route"] == "/vault/real-storage-provider-read-path-lock-contract"
    assert routes["json_route"] == "/vault/real-storage-provider-read-path-lock-contract.json"
    assert routes["record_route"] == "/vault/storage-provider-read-path-lock-contract-record.json"
    assert routes["requirements_route"] == "/vault/storage-provider-read-path-requirements.json"
    assert routes["policies_route"] == "/vault/storage-provider-read-path-policies.json"
    assert routes["blockers_route"] == "/vault/storage-provider-read-path-blockers.json"
    assert routes["events_route"] == "/vault/storage-provider-read-path-events.json"
    assert routes["validation_route"] == "/vault/storage-provider-read-path-validation.json"
    assert routes["next_step_route"] == "/vault/storage-provider-read-path-next-step.json"
    assert routes["gp068_status_route"] == "/vault/gp068-status.json"

    assert home["next_step"]["next_pack"] == "VAULT_GP069_REAL_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT"
    assert home["next_step"]["safe_to_continue_to_gp069"] is True
    assert home["next_step"]["vault_done"] is False
    assert home["next_step"]["clouds_should_continue"] is False


def test_gp068_status_ready_real_locked(read_db):
    status = get_gp068_status(read_db)
    gp068 = status["gp068_status"]

    assert status["pack"]["id"] == "VAULT_GP068"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert status["pack"]["section_range"] == "GP061-GP070"

    assert gp068["ready"] is True
    assert gp068["real_storage_provider_read_path_lock_contract_ready"] is True
    assert gp068["real_sqlite_backed"] is True
    assert gp068["real_schema_ready"] is True
    assert gp068["real_contract_count"] == 1
    assert gp068["real_requirement_count"] == EXPECTED_REQUIREMENTS
    assert gp068["real_policy_count"] == EXPECTED_POLICIES
    assert gp068["real_blocker_count"] == EXPECTED_BLOCKERS
    assert gp068["source_gp067_write_path_lock_contract_attached"] is True
    assert gp068["read_path_lock_contract_ready"] is True
    assert gp068["read_path_requirements_ready"] is True
    assert gp068["read_path_policy_ready"] is True
    assert gp068["read_path_locked"] is True
    assert gp068["read_path_alias_only"] is True
    assert gp068["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert gp068["requirement_code_count"] == len(READ_PATH_REQUIREMENT_SPECS)
    assert gp068["policy_code_count"] == EXPECTED_POLICIES
    assert gp068["read_path_configured_count"] == 0
    assert gp068["read_path_attempted_count"] == 0
    assert gp068["read_path_enabled_count"] == 0
    assert gp068["read_receipt_created_count"] == 0
    assert gp068["object_listing_configured_count"] == 0
    assert gp068["object_list_attempted_count"] == 0
    assert gp068["object_listed_count"] == 0
    assert gp068["object_body_read_attempted_count"] == 0
    assert gp068["object_body_read_count"] == 0
    assert gp068["object_body_view_enabled_count"] == 0
    assert gp068["provider_read_enabled_count"] == 0
    assert gp068["provider_write_enabled_count"] == 0
    assert gp068["direct_upload_enabled_count"] == 0
    assert gp068["blocks_provider_configuration_count"] == EXPECTED_BLOCKERS
    assert gp068["blocks_provider_read_write_count"] == EXPECTED_BLOCKERS
    assert gp068["blocks_object_body_view_count"] == EXPECTED_BLOCKERS
    assert gp068["blocks_export_count"] == EXPECTED_BLOCKERS
    assert gp068["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert gp068["tower_review_granted_count"] == 0
    assert gp068["resolved_count"] == 0
    assert gp068["validation_ready"] is True
    assert gp068["validation_passed"] is True
    assert gp068["safe_to_continue_to_gp069"] is True
    assert gp068["vault_done"] is False
    assert gp068["foundation_status"] == "read_path_lock_contract_ready_safe_to_continue_not_done"

    assert gp068["read_path_configured"] is False
    assert gp068["read_path_attempted"] is False
    assert gp068["read_path_enabled"] is False
    assert gp068["read_receipt_created"] is False
    assert gp068["object_listing_configured"] is False
    assert gp068["object_list_attempted"] is False
    assert gp068["object_listed"] is False
    assert gp068["object_body_read_attempted"] is False
    assert gp068["object_body_read"] is False
    assert gp068["object_body_view_enabled"] is False
    assert gp068["provider_read_enabled"] is False
    assert gp068["provider_write_enabled"] is False
    assert gp068["provider_object_read_claimed"] is False
    assert gp068["provider_object_write_claimed"] is False
    assert gp068["direct_upload_enabled"] is False
    assert gp068["export_enabled"] is False
    assert gp068["execution_enabled"] is False
    assert gp068["clouds_status"] == "parked_do_not_continue_from_vault_gp068"
    assert gp068["next_pack"] == "VAULT_GP069_REAL_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT"


def test_gp068_next_step_points_to_gp069_object_body_view_lock_contract():
    next_step = get_storage_provider_read_path_next_step()["next_step"]

    assert next_step["current_section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert next_step["current_section_range"] == "GP061-GP070"
    assert next_step["next_pack"] == "VAULT_GP069_REAL_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT"
    assert next_step["next_pack_title"] == "Real Storage Provider Object Body View Lock Contract"
    assert next_step["safe_to_continue_to_gp069"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "real sqlite read-path lock contract" in rules
    assert "read-path requirement rows" in rules
    assert "object body view lock contract" in rules
    assert "do not configure read paths" in rules
    assert "do not attempt provider reads" in rules
    assert "do not list provider objects" in rules
    assert "do not read object bodies" in rules
    assert "do not unlock export" in rules
    assert "do not unlock execution" in rules
    assert "do not treat vault as done" in rules


def test_gp068_html_is_dark_and_mentions_read_path_lock_contract(monkeypatch, tmp_path):
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
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT_DB", str(tmp_path / "html_write.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT_DB", str(tmp_path / "html_read.sqlite"))

    html = render_real_storage_provider_read_path_lock_contract_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Read Path Lock Contract" in html
    assert "Real Storage Provider Configuration Layer" in html
    assert "Archive Vault" in html
    assert "GP068" in html
    assert "Read-path lock ready" in html
    assert "Real SQLite-backed" in html
    assert "No read path" in html
    assert "No object listing" in html
    assert "No object body read" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-read-path-lock-contract.json" in html
    assert "/vault/gp068-status.json" in html

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


def test_gp068_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/real-storage-provider-read-path-lock-contract",
        "/vault/real-storage-provider-read-path-lock-contract.json",
        "/vault/storage-provider-read-path-lock-contract-record.json",
        "/vault/storage-provider-read-path-requirements.json",
        "/vault/storage-provider-read-path-policies.json",
        "/vault/storage-provider-read-path-blockers.json",
        "/vault/storage-provider-read-path-events.json",
        "/vault/storage-provider-read-path-validation.json",
        "/vault/storage-provider-read-path-next-step.json",
        "/vault/gp068-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp068_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
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
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT_DB", str(tmp_path / "routes_write.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT_DB", str(tmp_path / "routes_read.sqlite"))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/real-storage-provider-read-path-lock-contract",
        "/vault/real-storage-provider-read-path-lock-contract.json",
        "/vault/storage-provider-read-path-lock-contract-record.json",
        "/vault/storage-provider-read-path-requirements.json",
        "/vault/storage-provider-read-path-policies.json",
        "/vault/storage-provider-read-path-blockers.json",
        "/vault/storage-provider-read-path-events.json",
        "/vault/storage-provider-read-path-validation.json",
        "/vault/storage-provider-read-path-next-step.json",
        "/vault/gp068-status.json",
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
                assert b"Vault Real Storage Provider Read Path Lock Contract" in response.data
