"""
Tests for VAULT GIANT PACK 065 — Real Storage Provider Encryption Policy Contract
"""

from pathlib import Path

import pytest

from vault.real_storage_provider_encryption_policy_contract_service import (
    DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,
    ENCRYPTION_POLICIES,
    ENCRYPTION_REQUIREMENT_SPECS,
    ensure_storage_provider_encryption_policy_contract_schema,
    get_gp065_status,
    get_real_storage_provider_encryption_policy_contract_home,
    get_storage_provider_encryption_blockers,
    get_storage_provider_encryption_events,
    get_storage_provider_encryption_next_step,
    get_storage_provider_encryption_policies,
    get_storage_provider_encryption_policy_contract_record,
    get_storage_provider_encryption_requirements,
    initialize_real_storage_provider_encryption_policy_contract,
    record_storage_provider_encryption_event,
    render_real_storage_provider_encryption_policy_contract_page,
    validate_storage_provider_encryption_policy_contract,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROVIDER_CANDIDATES = 5
EXPECTED_REQUIREMENTS = EXPECTED_PROVIDER_CANDIDATES * len(ENCRYPTION_REQUIREMENT_SPECS)
EXPECTED_POLICIES = len(ENCRYPTION_POLICIES)
EXPECTED_BLOCKERS = 140


@pytest.fixture()
def encryption_db(tmp_path, monkeypatch):
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
    return str(tmp_path / "encryption_policy_contract.sqlite")


def test_gp065_schema_is_real_sqlite_backed(encryption_db):
    result = ensure_storage_provider_encryption_policy_contract_schema(encryption_db)
    db_path = Path(result["db_path"])

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert db_path.exists()
    assert "vault_storage_provider_encryption_policy_contracts" in result["tables"]
    assert "vault_storage_provider_encryption_requirements" in result["tables"]
    assert "vault_storage_provider_encryption_policies" in result["tables"]
    assert "vault_storage_provider_encryption_blockers" in result["tables"]
    assert "vault_storage_provider_encryption_events" in result["tables"]


def test_gp065_initialize_creates_real_contract_requirements_policies_blockers_events(encryption_db):
    result = initialize_real_storage_provider_encryption_policy_contract(encryption_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["encryption_policy_contract_id"] == DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID
    assert result["contract_count"] == 1
    assert result["requirement_count"] == EXPECTED_REQUIREMENTS
    assert result["policy_count"] == EXPECTED_POLICIES
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_encryption_policy_contract(encryption_db)
    assert second["contract_count"] == 1
    assert second["requirement_count"] == EXPECTED_REQUIREMENTS
    assert second["policy_count"] == EXPECTED_POLICIES
    assert second["blocker_count"] == EXPECTED_BLOCKERS
    assert second["event_count"] >= 6


def test_gp065_contract_record_is_real_and_sourced_from_gp064(encryption_db):
    contract = get_storage_provider_encryption_policy_contract_record(encryption_db)["encryption_policy_contract"]

    assert contract["encryption_policy_contract_id"] == DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP065"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert contract["section_range"] == "GP061-GP070"
    assert contract["source_endpoint_namespace_contract_id"] == "VSPENC-GP064-001"
    assert contract["source_endpoint_namespace_pack_id"] == "VAULT_GP064"
    assert contract["contract_status"] == "REAL_ENCRYPTION_POLICY_CONTRACT_OPEN_ALIAS_ONLY_TOWER_LOCKED"
    assert contract["tower_authority_status"] == "TOWER_REVIEW_REQUIRED_NOT_GRANTED"

    data = contract["contract_data"]
    assert data["contract_type"] == "REAL_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT"
    assert data["real_durable_encryption_policy_contract"] is True
    assert data["metadata_source"] == "VAULT_GP064_REAL_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT"
    assert data["source_endpoint_namespace_contract_id"] == "VSPENC-GP064-001"
    assert data["source_endpoint_namespace_pack_id"] == "VAULT_GP064"
    assert data["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert data["requirement_code_count"] == len(ENCRYPTION_REQUIREMENT_SPECS)
    assert data["requirement_count"] == EXPECTED_REQUIREMENTS
    assert data["policy_count"] == EXPECTED_POLICIES
    assert data["carried_blocker_count"] == EXPECTED_BLOCKERS
    assert data["safe_to_continue_to_gp066"] is True


def test_gp065_contract_keeps_encryption_key_and_provider_operations_locked(encryption_db):
    contract = get_storage_provider_encryption_policy_contract_record(encryption_db)["encryption_policy_contract"]

    assert contract["encryption_policy_contract_ready"] is True
    assert contract["encryption_requirements_ready"] is True
    assert contract["key_management_policy_ready"] is True
    assert contract["encryption_policy_alias_only"] is True
    assert contract["key_alias_only"] is True
    assert contract["key_material_stored"] is False
    assert contract["kms_key_id_stored"] is False
    assert contract["key_locator_present"] is False
    assert contract["encryption_policy_configured"] is False
    assert contract["encryption_algorithm_configured"] is False
    assert contract["encryption_at_rest_configured"] is False
    assert contract["encryption_in_transit_configured"] is False
    assert contract["customer_managed_key_configured"] is False
    assert contract["provider_managed_key_configured"] is False
    assert contract["actual_secret_values_stored"] is False
    assert contract["secret_values_present"] is False
    assert contract["token_material_present"] is False
    assert contract["encrypted_secret_payload_present"] is False
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


def test_gp065_requirements_are_real_alias_only_and_locked(encryption_db):
    payload = get_storage_provider_encryption_requirements(encryption_db)

    assert payload["pack"]["id"] == "VAULT_GP065"
    assert payload["real_sqlite_backed"] is True
    assert payload["requirement_count"] == EXPECTED_REQUIREMENTS
    assert payload["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert payload["requirement_code_count"] == len(ENCRYPTION_REQUIREMENT_SPECS)
    assert payload["requirement_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["requirement_verified_count"] == 0
    assert payload["encryption_policy_alias_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["key_alias_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["key_material_stored_count"] == 0
    assert payload["kms_key_id_stored_count"] == 0
    assert payload["key_locator_present_count"] == 0
    assert payload["encryption_policy_configured_count"] == 0
    assert payload["encryption_algorithm_configured_count"] == 0
    assert payload["encryption_at_rest_configured_count"] == 0
    assert payload["encryption_in_transit_configured_count"] == 0
    assert payload["customer_managed_key_configured_count"] == 0
    assert payload["provider_managed_key_configured_count"] == 0
    assert payload["credentials_configured_count"] == 0
    assert payload["secret_references_activated_count"] == 0
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
    expected_codes = {item["requirement_code"] for item in ENCRYPTION_REQUIREMENT_SPECS}
    assert codes == expected_codes

    for item in payload["requirements"]:
        assert item["encryption_requirement_id"].startswith("VSPER-")
        assert item["encryption_policy_contract_id"] == DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["requirement_status"] == "REAL_ENCRYPTION_REQUIREMENT_RECORDED_ALIAS_ONLY_TOWER_LOCKED"
        assert item["requirement_required"] is True
        assert item["requirement_verified"] is False
        assert item["encryption_policy_alias_only"] is True
        assert item["key_alias_only"] is True
        assert item["key_material_stored"] is False
        assert item["kms_key_id_stored"] is False
        assert item["key_locator_present"] is False
        assert item["encryption_policy_configured"] is False
        assert item["encryption_algorithm_configured"] is False
        assert item["encryption_at_rest_configured"] is False
        assert item["encryption_in_transit_configured"] is False
        assert item["customer_managed_key_configured"] is False
        assert item["provider_managed_key_configured"] is False
        assert item["provider_connection_tested"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False


def test_gp065_policies_are_real_and_locked(encryption_db):
    payload = get_storage_provider_encryption_policies(encryption_db)

    assert payload["pack"]["id"] == "VAULT_GP065"
    assert payload["real_sqlite_backed"] is True
    assert payload["policy_count"] == EXPECTED_POLICIES
    assert payload["policy_code_count"] == EXPECTED_POLICIES
    assert payload["policy_required_count"] == EXPECTED_POLICIES
    assert payload["policy_verified_count"] == 0
    assert payload["key_material_stored_count"] == 0
    assert payload["kms_key_id_stored_count"] == 0
    assert payload["key_locator_present_count"] == 0
    assert payload["encryption_policy_configured_count"] == 0
    assert payload["encryption_algorithm_configured_count"] == 0
    assert payload["encryption_at_rest_configured_count"] == 0
    assert payload["encryption_in_transit_configured_count"] == 0
    assert payload["customer_managed_key_configured_count"] == 0
    assert payload["provider_managed_key_configured_count"] == 0
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
    expected_codes = {item["policy_code"] for item in ENCRYPTION_POLICIES}
    assert codes == expected_codes

    for item in payload["policies"]:
        assert item["encryption_policy_id"].startswith("VSPEP-")
        assert item["encryption_policy_contract_id"] == DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID
        assert item["policy_status"] == "REAL_ENCRYPTION_POLICY_RECORDED_TOWER_LOCKED"
        assert item["policy_required"] is True
        assert item["policy_verified"] is False
        assert item["key_material_stored"] is False
        assert item["kms_key_id_stored"] is False
        assert item["key_locator_present"] is False
        assert item["encryption_policy_configured"] is False
        assert item["encryption_algorithm_configured"] is False
        assert item["encryption_at_rest_configured"] is False
        assert item["encryption_in_transit_configured"] is False
        assert item["customer_managed_key_configured"] is False
        assert item["provider_managed_key_configured"] is False
        assert item["secret_values_present"] is False
        assert item["token_material_present"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False


def test_gp065_blockers_are_real_and_carried_from_gp064(encryption_db):
    payload = get_storage_provider_encryption_blockers(encryption_db)

    assert payload["pack"]["id"] == "VAULT_GP065"
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
        assert item["encryption_blocker_id"].startswith("VSPEB-")
        assert item["encryption_policy_contract_id"] == DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID
        assert item["source_endpoint_namespace_blocker_id"].startswith("VSPENB-")
        assert item["source_ledger_blocker_id"].startswith("VSPSRLB-")
        assert item["source_credential_blocker_id"].startswith("VSPCBB-")
        assert item["source_config_blocker_id"].startswith("VSPCFGB-")
        assert item["source_readiness_blocker_id"].startswith("VSPPB-")
        assert item["source_receipt_line_id"].startswith("VSPRL-")
        assert item["source_finding_id"].startswith("VSPRCF-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["blocker_status"] == "REAL_ENCRYPTION_BLOCKER_ACTIVE_CARRIED_FROM_GP064"
        assert item["blocks_provider_configuration"] is True
        assert item["blocks_provider_read_write"] is True
        assert item["blocks_object_body_view"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False
        assert item["resolved"] is False


def test_gp065_event_log_is_real_and_seeded(encryption_db):
    events = get_storage_provider_encryption_events(encryption_db)

    assert events["pack"]["id"] == "VAULT_GP065"
    assert events["real_sqlite_backed"] is True
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP064_ENDPOINT_NAMESPACE_CONTRACT_ATTACHED" in event_types
    assert "REAL_ENCRYPTION_REQUIREMENTS_CREATED_ALIAS_ONLY" in event_types
    assert "REAL_KEY_MANAGEMENT_POLICIES_CREATED" in event_types
    assert "REAL_ENCRYPTION_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "ENCRYPTION_POLICY_LOCKS_CONFIRMED" in event_types

    for event in events["events"]:
        assert event["event_id"].startswith("VSPEEVT-")
        assert event["encryption_policy_contract_id"] == DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID
        assert isinstance(event["event_payload"], dict)
        assert event["created_at"]


def test_gp065_can_write_real_event_without_configuring_encryption_or_keys(encryption_db):
    before = get_storage_provider_encryption_events(encryption_db)["event_count"]

    written = record_storage_provider_encryption_event(
        "OWNER_GP065_ENCRYPTION_POLICY_CONTRACT_OBSERVED",
        {"reviewer": "owner", "note": "reviewed real GP065 encryption policy contract"},
        encryption_db,
    )

    after = get_storage_provider_encryption_events(encryption_db)
    contract = get_storage_provider_encryption_policy_contract_record(encryption_db)["encryption_policy_contract"]
    requirements = get_storage_provider_encryption_requirements(encryption_db)
    policies = get_storage_provider_encryption_policies(encryption_db)

    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPEEVT-")
    assert written["encryption_policy_contract_id"] == DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID
    assert written["key_material_stored"] is False
    assert written["kms_key_id_stored"] is False
    assert written["key_locator_present"] is False
    assert written["encryption_policy_configured"] is False
    assert written["encryption_at_rest_configured"] is False
    assert written["encryption_in_transit_configured"] is False
    assert written["provider_connection_tested"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

    assert after["event_count"] == before + 1
    assert "OWNER_GP065_ENCRYPTION_POLICY_CONTRACT_OBSERVED" in {event["event_type"] for event in after["events"]}

    assert contract["key_material_stored"] is False
    assert contract["kms_key_id_stored"] is False
    assert contract["encryption_policy_configured"] is False
    assert contract["encryption_at_rest_configured"] is False
    assert requirements["key_material_stored_count"] == 0
    assert requirements["encryption_policy_configured_count"] == 0
    assert policies["key_material_stored_count"] == 0
    assert policies["encryption_policy_configured_count"] == 0


def test_gp065_validation_passes_real_locked_encryption_policy_contract(encryption_db):
    validation = validate_storage_provider_encryption_policy_contract(encryption_db)

    assert validation["pack"]["id"] == "VAULT_GP065"
    assert validation["validation_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["passed_count"] == validation["check_count"]
    assert validation["real_sqlite_backed"] is True
    assert validation["safe_to_continue_to_gp066"] is True

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_ENCRYPTION_POLICY_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP064_ENDPOINT_NAMESPACE_CONTRACT_ATTACHED" in codes
    assert "ENCRYPTION_POLICY_CONTRACT_READY" in codes
    assert "REAL_ENCRYPTION_REQUIREMENTS_EXIST" in codes
    assert "NO_REQUIREMENT_KEY_MATERIAL_STORED" in codes
    assert "NO_REQUIREMENT_KMS_KEY_ID_STORED" in codes
    assert "NO_REQUIREMENT_ENCRYPTION_POLICY_CONFIGURED" in codes
    assert "NO_REQUIREMENT_ENCRYPTION_AT_REST_CONFIGURED" in codes
    assert "REAL_ENCRYPTION_POLICIES_EXIST" in codes
    assert "REAL_ENCRYPTION_BLOCKERS_CARRIED_FORWARD" in codes
    assert "NO_CONTRACT_KEY_MATERIAL_STORED" in codes
    assert "NO_CONTRACT_KMS_KEY_ID_STORED" in codes
    assert "NO_CONTRACT_ENCRYPTION_POLICY_CONFIGURED" in codes
    assert "NO_CREDENTIALS_CONFIGURED" in codes
    assert "NO_PROVIDER_CONNECTION_TESTED" in codes
    assert "NO_EXPORT" in codes
    assert "NO_EXECUTION" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "EVENT_LOG_EXISTS" in codes


def test_gp065_home_payload_has_truth_routes_and_next_step(encryption_db):
    home = get_real_storage_provider_encryption_policy_contract_home(encryption_db)

    assert home["pack"]["id"] == "VAULT_GP065"
    assert home["encryption_truth"]["real_storage_provider_encryption_policy_contract_ready"] is True
    assert home["encryption_truth"]["real_sqlite_backed"] is True
    assert home["encryption_truth"]["real_schema_ready"] is True
    assert home["encryption_truth"]["real_encryption_policy_contract_exists"] is True
    assert home["encryption_truth"]["real_encryption_requirement_rows_exist"] is True
    assert home["encryption_truth"]["real_key_management_policy_rows_exist"] is True
    assert home["encryption_truth"]["real_encryption_blocker_rows_exist"] is True
    assert home["encryption_truth"]["real_event_log_exists"] is True
    assert home["encryption_truth"]["source_gp064_endpoint_namespace_contract_attached"] is True
    assert home["encryption_truth"]["validation_passed"] is True
    assert home["encryption_truth"]["key_material_stored_count"] == 0
    assert home["encryption_truth"]["kms_key_id_stored_count"] == 0
    assert home["encryption_truth"]["encryption_policy_configured_count"] == 0
    assert home["encryption_truth"]["encryption_at_rest_configured_count"] == 0
    assert home["encryption_truth"]["provider_connection_tested"] is False
    assert home["encryption_truth"]["export_enabled"] is False
    assert home["encryption_truth"]["execution_enabled"] is False
    assert home["encryption_truth"]["vault_done"] is False

    routes = home["routes"]
    assert routes["route"] == "/vault/real-storage-provider-encryption-policy-contract"
    assert routes["json_route"] == "/vault/real-storage-provider-encryption-policy-contract.json"
    assert routes["record_route"] == "/vault/storage-provider-encryption-policy-contract-record.json"
    assert routes["requirements_route"] == "/vault/storage-provider-encryption-requirements.json"
    assert routes["policies_route"] == "/vault/storage-provider-encryption-policies.json"
    assert routes["blockers_route"] == "/vault/storage-provider-encryption-blockers.json"
    assert routes["events_route"] == "/vault/storage-provider-encryption-events.json"
    assert routes["validation_route"] == "/vault/storage-provider-encryption-validation.json"
    assert routes["next_step_route"] == "/vault/storage-provider-encryption-next-step.json"
    assert routes["gp065_status_route"] == "/vault/gp065-status.json"

    assert home["next_step"]["next_pack"] == "VAULT_GP066_REAL_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT"
    assert home["next_step"]["safe_to_continue_to_gp066"] is True
    assert home["next_step"]["vault_done"] is False
    assert home["next_step"]["clouds_should_continue"] is False


def test_gp065_status_ready_real_alias_only_and_locked(encryption_db):
    status = get_gp065_status(encryption_db)
    gp065 = status["gp065_status"]

    assert status["pack"]["id"] == "VAULT_GP065"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert status["pack"]["section_range"] == "GP061-GP070"

    assert gp065["ready"] is True
    assert gp065["real_storage_provider_encryption_policy_contract_ready"] is True
    assert gp065["real_sqlite_backed"] is True
    assert gp065["real_schema_ready"] is True
    assert gp065["real_contract_count"] == 1
    assert gp065["real_requirement_count"] == EXPECTED_REQUIREMENTS
    assert gp065["real_policy_count"] == EXPECTED_POLICIES
    assert gp065["real_blocker_count"] == EXPECTED_BLOCKERS
    assert gp065["source_gp064_endpoint_namespace_contract_attached"] is True
    assert gp065["encryption_policy_contract_ready"] is True
    assert gp065["encryption_requirements_ready"] is True
    assert gp065["key_management_policy_ready"] is True
    assert gp065["encryption_policy_alias_only"] is True
    assert gp065["key_alias_only"] is True
    assert gp065["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert gp065["requirement_code_count"] == len(ENCRYPTION_REQUIREMENT_SPECS)
    assert gp065["policy_code_count"] == EXPECTED_POLICIES
    assert gp065["key_material_stored_count"] == 0
    assert gp065["kms_key_id_stored_count"] == 0
    assert gp065["key_locator_present_count"] == 0
    assert gp065["encryption_policy_configured_count"] == 0
    assert gp065["encryption_algorithm_configured_count"] == 0
    assert gp065["encryption_at_rest_configured_count"] == 0
    assert gp065["encryption_in_transit_configured_count"] == 0
    assert gp065["customer_managed_key_configured_count"] == 0
    assert gp065["provider_managed_key_configured_count"] == 0
    assert gp065["secret_value_present_count"] == 0
    assert gp065["token_material_present_count"] == 0
    assert gp065["secret_references_created_count"] == 0
    assert gp065["secret_references_activated_count"] == 0
    assert gp065["credentials_configured_count"] == 0
    assert gp065["blocks_provider_configuration_count"] == EXPECTED_BLOCKERS
    assert gp065["blocks_provider_read_write_count"] == EXPECTED_BLOCKERS
    assert gp065["blocks_object_body_view_count"] == EXPECTED_BLOCKERS
    assert gp065["blocks_export_count"] == EXPECTED_BLOCKERS
    assert gp065["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert gp065["tower_review_granted_count"] == 0
    assert gp065["resolved_count"] == 0
    assert gp065["validation_ready"] is True
    assert gp065["validation_passed"] is True
    assert gp065["safe_to_continue_to_gp066"] is True
    assert gp065["vault_done"] is False
    assert gp065["foundation_status"] == "encryption_policy_contract_ready_safe_to_continue_not_done"

    assert gp065["key_material_stored"] is False
    assert gp065["kms_key_id_stored"] is False
    assert gp065["key_locator_present"] is False
    assert gp065["encryption_policy_configured"] is False
    assert gp065["encryption_algorithm_configured"] is False
    assert gp065["encryption_at_rest_configured"] is False
    assert gp065["encryption_in_transit_configured"] is False
    assert gp065["customer_managed_key_configured"] is False
    assert gp065["provider_managed_key_configured"] is False
    assert gp065["credentials_configured"] is False
    assert gp065["provider_connection_tested"] is False
    assert gp065["provider_read_enabled"] is False
    assert gp065["provider_write_enabled"] is False
    assert gp065["object_body_view_enabled"] is False
    assert gp065["direct_upload_enabled"] is False
    assert gp065["export_enabled"] is False
    assert gp065["execution_enabled"] is False
    assert gp065["clouds_status"] == "parked_do_not_continue_from_vault_gp065"
    assert gp065["next_pack"] == "VAULT_GP066_REAL_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT"


def test_gp065_next_step_points_to_gp066_connection_test_lock_contract():
    next_step = get_storage_provider_encryption_next_step()["next_step"]

    assert next_step["current_section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert next_step["current_section_range"] == "GP061-GP070"
    assert next_step["next_pack"] == "VAULT_GP066_REAL_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT"
    assert next_step["next_pack_title"] == "Real Storage Provider Connection Test Lock Contract"
    assert next_step["safe_to_continue_to_gp066"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

    note = next_step["owner_notebook_note"].lower()
    assert "connection-test lock contract" in note
    assert "encryption" in note
    assert "keys" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "real sqlite encryption policy contract" in rules
    assert "encryption requirement rows" in rules
    assert "key-management policy rows" in rules
    assert "connection test lock contract" in rules
    assert "do not store key material" in rules
    assert "do not store kms key ids" in rules
    assert "do not configure encryption policy yet" in rules
    assert "do not test provider connection yet" in rules
    assert "do not unlock export" in rules
    assert "do not unlock execution" in rules
    assert "do not treat vault as done" in rules


def test_gp065_html_is_dark_and_mentions_encryption_policy_contract(monkeypatch, tmp_path):
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

    html = render_real_storage_provider_encryption_policy_contract_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Encryption Policy Contract" in html
    assert "Real Storage Provider Configuration Layer" in html
    assert "Archive Vault" in html
    assert "GP065" in html
    assert "Encryption policy contract ready" in html
    assert "Alias-only rows" in html
    assert "Real SQLite-backed" in html
    assert "No keys stored" in html
    assert "No encryption configured" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-encryption-policy-contract.json" in html
    assert "/vault/gp065-status.json" in html

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


def test_gp065_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/real-storage-provider-encryption-policy-contract",
        "/vault/real-storage-provider-encryption-policy-contract.json",
        "/vault/storage-provider-encryption-policy-contract-record.json",
        "/vault/storage-provider-encryption-requirements.json",
        "/vault/storage-provider-encryption-policies.json",
        "/vault/storage-provider-encryption-blockers.json",
        "/vault/storage-provider-encryption-events.json",
        "/vault/storage-provider-encryption-validation.json",
        "/vault/storage-provider-encryption-next-step.json",
        "/vault/gp065-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp065_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
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

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/real-storage-provider-encryption-policy-contract",
        "/vault/real-storage-provider-encryption-policy-contract.json",
        "/vault/storage-provider-encryption-policy-contract-record.json",
        "/vault/storage-provider-encryption-requirements.json",
        "/vault/storage-provider-encryption-policies.json",
        "/vault/storage-provider-encryption-blockers.json",
        "/vault/storage-provider-encryption-events.json",
        "/vault/storage-provider-encryption-validation.json",
        "/vault/storage-provider-encryption-next-step.json",
        "/vault/gp065-status.json",
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
                assert b"Vault Real Storage Provider Encryption Policy Contract" in response.data
