"""
Tests for VAULT GIANT PACK 064 — Real Storage Provider Endpoint Namespace Contract
"""

from pathlib import Path

import pytest

from vault.real_storage_provider_endpoint_namespace_contract_service import (
    DEFAULT_ENDPOINT_NAMESPACE_CONTRACT_ID,
    ENDPOINT_NAMESPACE_POLICIES,
    ENDPOINT_NAMESPACE_REQUIREMENT_SPECS,
    ensure_storage_provider_endpoint_namespace_contract_schema,
    get_gp064_status,
    get_real_storage_provider_endpoint_namespace_contract_home,
    get_storage_provider_endpoint_namespace_blockers,
    get_storage_provider_endpoint_namespace_contract_record,
    get_storage_provider_endpoint_namespace_events,
    get_storage_provider_endpoint_namespace_next_step,
    get_storage_provider_endpoint_namespace_policies,
    get_storage_provider_endpoint_namespace_requirements,
    initialize_real_storage_provider_endpoint_namespace_contract,
    record_storage_provider_endpoint_namespace_event,
    render_real_storage_provider_endpoint_namespace_contract_page,
    validate_storage_provider_endpoint_namespace_contract,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROVIDER_CANDIDATES = 5
EXPECTED_REQUIREMENTS = EXPECTED_PROVIDER_CANDIDATES * len(ENDPOINT_NAMESPACE_REQUIREMENT_SPECS)
EXPECTED_POLICIES = len(ENDPOINT_NAMESPACE_POLICIES)
EXPECTED_BLOCKERS = 140


@pytest.fixture()
def endpoint_db(tmp_path, monkeypatch):
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
    return str(tmp_path / "endpoint_namespace_contract.sqlite")


def test_gp064_schema_is_real_sqlite_backed(endpoint_db):
    result = ensure_storage_provider_endpoint_namespace_contract_schema(endpoint_db)
    db_path = Path(result["db_path"])

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert db_path.exists()
    assert "vault_storage_provider_endpoint_namespace_contracts" in result["tables"]
    assert "vault_storage_provider_endpoint_namespace_requirements" in result["tables"]
    assert "vault_storage_provider_endpoint_namespace_policies" in result["tables"]
    assert "vault_storage_provider_endpoint_namespace_blockers" in result["tables"]
    assert "vault_storage_provider_endpoint_namespace_events" in result["tables"]


def test_gp064_initialize_creates_real_contract_requirements_policies_blockers_events(endpoint_db):
    result = initialize_real_storage_provider_endpoint_namespace_contract(endpoint_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["endpoint_namespace_contract_id"] == DEFAULT_ENDPOINT_NAMESPACE_CONTRACT_ID
    assert result["contract_count"] == 1
    assert result["requirement_count"] == EXPECTED_REQUIREMENTS
    assert result["policy_count"] == EXPECTED_POLICIES
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_endpoint_namespace_contract(endpoint_db)
    assert second["contract_count"] == 1
    assert second["requirement_count"] == EXPECTED_REQUIREMENTS
    assert second["policy_count"] == EXPECTED_POLICIES
    assert second["blocker_count"] == EXPECTED_BLOCKERS
    assert second["event_count"] >= 6


def test_gp064_contract_record_is_real_and_sourced_from_gp063(endpoint_db):
    contract = get_storage_provider_endpoint_namespace_contract_record(endpoint_db)["endpoint_namespace_contract"]

    assert contract["endpoint_namespace_contract_id"] == DEFAULT_ENDPOINT_NAMESPACE_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP064"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert contract["section_range"] == "GP061-GP070"
    assert contract["source_secret_reference_ledger_id"] == "VSPSRL-GP063-001"
    assert contract["source_secret_reference_ledger_pack_id"] == "VAULT_GP063"
    assert contract["contract_status"] == "REAL_ENDPOINT_NAMESPACE_CONTRACT_OPEN_ALIAS_ONLY_TOWER_LOCKED"
    assert contract["tower_authority_status"] == "TOWER_REVIEW_REQUIRED_NOT_GRANTED"

    data = contract["contract_data"]
    assert data["contract_type"] == "REAL_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT"
    assert data["real_durable_endpoint_namespace_contract"] is True
    assert data["metadata_source"] == "VAULT_GP063_REAL_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER"
    assert data["source_secret_reference_ledger_id"] == "VSPSRL-GP063-001"
    assert data["source_secret_reference_ledger_pack_id"] == "VAULT_GP063"
    assert data["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert data["requirement_code_count"] == len(ENDPOINT_NAMESPACE_REQUIREMENT_SPECS)
    assert data["requirement_count"] == EXPECTED_REQUIREMENTS
    assert data["policy_count"] == EXPECTED_POLICIES
    assert data["carried_blocker_count"] == EXPECTED_BLOCKERS
    assert data["safe_to_continue_to_gp065"] is True


def test_gp064_contract_keeps_endpoint_namespace_and_provider_operations_locked(endpoint_db):
    contract = get_storage_provider_endpoint_namespace_contract_record(endpoint_db)["endpoint_namespace_contract"]

    assert contract["endpoint_namespace_contract_ready"] is True
    assert contract["endpoint_namespace_requirements_ready"] is True
    assert contract["endpoint_namespace_policy_ready"] is True
    assert contract["endpoint_alias_only"] is True
    assert contract["namespace_alias_only"] is True
    assert contract["endpoint_url_stored"] is False
    assert contract["endpoint_value_present"] is False
    assert contract["namespace_value_stored"] is False
    assert contract["namespace_value_present"] is False
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
    assert contract["encryption_configured"] is False
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


def test_gp064_requirements_are_real_alias_only_and_locked(endpoint_db):
    payload = get_storage_provider_endpoint_namespace_requirements(endpoint_db)

    assert payload["pack"]["id"] == "VAULT_GP064"
    assert payload["real_sqlite_backed"] is True
    assert payload["requirement_count"] == EXPECTED_REQUIREMENTS
    assert payload["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert payload["requirement_code_count"] == len(ENDPOINT_NAMESPACE_REQUIREMENT_SPECS)
    assert payload["requirement_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["requirement_verified_count"] == 0
    assert payload["endpoint_alias_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["namespace_alias_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["endpoint_url_stored_count"] == 0
    assert payload["endpoint_value_present_count"] == 0
    assert payload["namespace_value_stored_count"] == 0
    assert payload["namespace_value_present_count"] == 0
    assert payload["credentials_configured_count"] == 0
    assert payload["secret_references_activated_count"] == 0
    assert payload["provider_endpoint_configured_count"] == 0
    assert payload["storage_container_configured_count"] == 0
    assert payload["namespace_configured_count"] == 0
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
    expected_codes = {item["requirement_code"] for item in ENDPOINT_NAMESPACE_REQUIREMENT_SPECS}
    assert codes == expected_codes

    for item in payload["requirements"]:
        assert item["endpoint_namespace_requirement_id"].startswith("VSPENR-")
        assert item["endpoint_namespace_contract_id"] == DEFAULT_ENDPOINT_NAMESPACE_CONTRACT_ID
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["requirement_status"] == "REAL_ENDPOINT_NAMESPACE_REQUIREMENT_RECORDED_ALIAS_ONLY_TOWER_LOCKED"
        assert item["requirement_required"] is True
        assert item["requirement_verified"] is False
        assert item["endpoint_alias_only"] is True
        assert item["namespace_alias_only"] is True
        assert item["endpoint_url_stored"] is False
        assert item["endpoint_value_present"] is False
        assert item["namespace_value_stored"] is False
        assert item["namespace_value_present"] is False
        assert item["provider_endpoint_configured"] is False
        assert item["storage_container_configured"] is False
        assert item["namespace_configured"] is False
        assert item["provider_connection_tested"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False


def test_gp064_policies_are_real_and_locked(endpoint_db):
    payload = get_storage_provider_endpoint_namespace_policies(endpoint_db)

    assert payload["pack"]["id"] == "VAULT_GP064"
    assert payload["real_sqlite_backed"] is True
    assert payload["policy_count"] == EXPECTED_POLICIES
    assert payload["policy_code_count"] == EXPECTED_POLICIES
    assert payload["policy_required_count"] == EXPECTED_POLICIES
    assert payload["policy_verified_count"] == 0
    assert payload["endpoint_url_stored_count"] == 0
    assert payload["endpoint_value_present_count"] == 0
    assert payload["namespace_value_stored_count"] == 0
    assert payload["namespace_value_present_count"] == 0
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
    expected_codes = {item["policy_code"] for item in ENDPOINT_NAMESPACE_POLICIES}
    assert codes == expected_codes

    for item in payload["policies"]:
        assert item["endpoint_namespace_policy_id"].startswith("VSPENP-")
        assert item["endpoint_namespace_contract_id"] == DEFAULT_ENDPOINT_NAMESPACE_CONTRACT_ID
        assert item["policy_status"] == "REAL_ENDPOINT_NAMESPACE_POLICY_RECORDED_TOWER_LOCKED"
        assert item["policy_required"] is True
        assert item["policy_verified"] is False
        assert item["endpoint_url_stored"] is False
        assert item["endpoint_value_present"] is False
        assert item["namespace_value_stored"] is False
        assert item["namespace_value_present"] is False
        assert item["actual_secret_values_stored"] is False
        assert item["secret_values_present"] is False
        assert item["token_material_present"] is False
        assert item["secret_references_created"] is False
        assert item["secret_references_activated"] is False
        assert item["credentials_configured"] is False
        assert item["provider_connection_tested"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False


def test_gp064_blockers_are_real_and_carried_from_gp063(endpoint_db):
    payload = get_storage_provider_endpoint_namespace_blockers(endpoint_db)

    assert payload["pack"]["id"] == "VAULT_GP064"
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
        assert item["endpoint_namespace_blocker_id"].startswith("VSPENB-")
        assert item["endpoint_namespace_contract_id"] == DEFAULT_ENDPOINT_NAMESPACE_CONTRACT_ID
        assert item["source_ledger_blocker_id"].startswith("VSPSRLB-")
        assert item["source_credential_blocker_id"].startswith("VSPCBB-")
        assert item["source_config_blocker_id"].startswith("VSPCFGB-")
        assert item["source_readiness_blocker_id"].startswith("VSPPB-")
        assert item["source_receipt_line_id"].startswith("VSPRL-")
        assert item["source_finding_id"].startswith("VSPRCF-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["blocker_status"] == "REAL_ENDPOINT_NAMESPACE_BLOCKER_ACTIVE_CARRIED_FROM_GP063"
        assert item["blocks_provider_configuration"] is True
        assert item["blocks_provider_read_write"] is True
        assert item["blocks_object_body_view"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False
        assert item["resolved"] is False


def test_gp064_event_log_is_real_and_seeded(endpoint_db):
    events = get_storage_provider_endpoint_namespace_events(endpoint_db)

    assert events["pack"]["id"] == "VAULT_GP064"
    assert events["real_sqlite_backed"] is True
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP063_SECRET_REFERENCE_LEDGER_ATTACHED" in event_types
    assert "REAL_ENDPOINT_NAMESPACE_REQUIREMENTS_CREATED_ALIAS_ONLY" in event_types
    assert "REAL_ENDPOINT_NAMESPACE_POLICIES_CREATED" in event_types
    assert "REAL_ENDPOINT_NAMESPACE_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "ENDPOINT_NAMESPACE_LOCKS_CONFIRMED" in event_types

    for event in events["events"]:
        assert event["event_id"].startswith("VSPENEVT-")
        assert event["endpoint_namespace_contract_id"] == DEFAULT_ENDPOINT_NAMESPACE_CONTRACT_ID
        assert isinstance(event["event_payload"], dict)
        assert event["created_at"]


def test_gp064_can_write_real_event_without_configuring_endpoint_or_namespace(endpoint_db):
    before = get_storage_provider_endpoint_namespace_events(endpoint_db)["event_count"]

    written = record_storage_provider_endpoint_namespace_event(
        "OWNER_GP064_ENDPOINT_NAMESPACE_CONTRACT_OBSERVED",
        {"reviewer": "owner", "note": "reviewed real GP064 endpoint namespace contract"},
        endpoint_db,
    )

    after = get_storage_provider_endpoint_namespace_events(endpoint_db)
    contract = get_storage_provider_endpoint_namespace_contract_record(endpoint_db)["endpoint_namespace_contract"]
    requirements = get_storage_provider_endpoint_namespace_requirements(endpoint_db)
    policies = get_storage_provider_endpoint_namespace_policies(endpoint_db)

    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPENEVT-")
    assert written["endpoint_namespace_contract_id"] == DEFAULT_ENDPOINT_NAMESPACE_CONTRACT_ID
    assert written["endpoint_url_stored"] is False
    assert written["namespace_value_present"] is False
    assert written["provider_endpoint_configured"] is False
    assert written["storage_container_configured"] is False
    assert written["namespace_configured"] is False
    assert written["provider_connection_tested"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

    assert after["event_count"] == before + 1
    assert "OWNER_GP064_ENDPOINT_NAMESPACE_CONTRACT_OBSERVED" in {event["event_type"] for event in after["events"]}

    assert contract["endpoint_url_stored"] is False
    assert contract["provider_endpoint_configured"] is False
    assert contract["storage_container_configured"] is False
    assert contract["namespace_configured"] is False
    assert requirements["provider_endpoint_configured_count"] == 0
    assert requirements["storage_container_configured_count"] == 0
    assert requirements["namespace_configured_count"] == 0
    assert policies["endpoint_url_stored_count"] == 0
    assert policies["namespace_value_present_count"] == 0


def test_gp064_validation_passes_real_locked_endpoint_namespace_contract(endpoint_db):
    validation = validate_storage_provider_endpoint_namespace_contract(endpoint_db)

    assert validation["pack"]["id"] == "VAULT_GP064"
    assert validation["validation_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["passed_count"] == validation["check_count"]
    assert validation["real_sqlite_backed"] is True
    assert validation["safe_to_continue_to_gp065"] is True

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_ENDPOINT_NAMESPACE_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP063_SECRET_REFERENCE_LEDGER_ATTACHED" in codes
    assert "ENDPOINT_NAMESPACE_CONTRACT_READY" in codes
    assert "REAL_ENDPOINT_NAMESPACE_REQUIREMENTS_EXIST" in codes
    assert "NO_REQUIREMENT_ENDPOINT_URL_STORED" in codes
    assert "NO_REQUIREMENT_NAMESPACE_VALUE_PRESENT" in codes
    assert "NO_REQUIREMENT_PROVIDER_ENDPOINT_CONFIGURED" in codes
    assert "NO_REQUIREMENT_STORAGE_CONTAINER_CONFIGURED" in codes
    assert "NO_REQUIREMENT_NAMESPACE_CONFIGURED" in codes
    assert "REAL_ENDPOINT_NAMESPACE_POLICIES_EXIST" in codes
    assert "REAL_ENDPOINT_NAMESPACE_BLOCKERS_CARRIED_FORWARD" in codes
    assert "NO_CONTRACT_ENDPOINT_URL_STORED" in codes
    assert "NO_PROVIDER_ENDPOINT_CONFIGURED" in codes
    assert "NO_STORAGE_CONTAINER_CONFIGURED" in codes
    assert "NO_NAMESPACE_CONFIGURED" in codes
    assert "NO_PROVIDER_CONNECTION_TESTED" in codes
    assert "NO_EXPORT" in codes
    assert "NO_EXECUTION" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "EVENT_LOG_EXISTS" in codes


def test_gp064_home_payload_has_truth_routes_and_next_step(endpoint_db):
    home = get_real_storage_provider_endpoint_namespace_contract_home(endpoint_db)

    assert home["pack"]["id"] == "VAULT_GP064"
    assert home["endpoint_namespace_truth"]["real_storage_provider_endpoint_namespace_contract_ready"] is True
    assert home["endpoint_namespace_truth"]["real_sqlite_backed"] is True
    assert home["endpoint_namespace_truth"]["real_schema_ready"] is True
    assert home["endpoint_namespace_truth"]["real_endpoint_namespace_contract_exists"] is True
    assert home["endpoint_namespace_truth"]["real_endpoint_namespace_requirement_rows_exist"] is True
    assert home["endpoint_namespace_truth"]["real_endpoint_namespace_policy_rows_exist"] is True
    assert home["endpoint_namespace_truth"]["real_endpoint_namespace_blocker_rows_exist"] is True
    assert home["endpoint_namespace_truth"]["real_event_log_exists"] is True
    assert home["endpoint_namespace_truth"]["source_gp063_secret_reference_ledger_attached"] is True
    assert home["endpoint_namespace_truth"]["validation_passed"] is True
    assert home["endpoint_namespace_truth"]["endpoint_url_stored_count"] == 0
    assert home["endpoint_namespace_truth"]["endpoint_value_present_count"] == 0
    assert home["endpoint_namespace_truth"]["namespace_value_stored_count"] == 0
    assert home["endpoint_namespace_truth"]["namespace_value_present_count"] == 0
    assert home["endpoint_namespace_truth"]["provider_endpoint_configured_count"] == 0
    assert home["endpoint_namespace_truth"]["storage_container_configured_count"] == 0
    assert home["endpoint_namespace_truth"]["namespace_configured_count"] == 0
    assert home["endpoint_namespace_truth"]["export_enabled"] is False
    assert home["endpoint_namespace_truth"]["execution_enabled"] is False
    assert home["endpoint_namespace_truth"]["vault_done"] is False

    routes = home["routes"]
    assert routes["route"] == "/vault/real-storage-provider-endpoint-namespace-contract"
    assert routes["json_route"] == "/vault/real-storage-provider-endpoint-namespace-contract.json"
    assert routes["record_route"] == "/vault/storage-provider-endpoint-namespace-contract-record.json"
    assert routes["requirements_route"] == "/vault/storage-provider-endpoint-namespace-requirements.json"
    assert routes["policies_route"] == "/vault/storage-provider-endpoint-namespace-policies.json"
    assert routes["blockers_route"] == "/vault/storage-provider-endpoint-namespace-blockers.json"
    assert routes["events_route"] == "/vault/storage-provider-endpoint-namespace-events.json"
    assert routes["validation_route"] == "/vault/storage-provider-endpoint-namespace-validation.json"
    assert routes["next_step_route"] == "/vault/storage-provider-endpoint-namespace-next-step.json"
    assert routes["gp064_status_route"] == "/vault/gp064-status.json"

    assert home["next_step"]["next_pack"] == "VAULT_GP065_REAL_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT"
    assert home["next_step"]["safe_to_continue_to_gp065"] is True
    assert home["next_step"]["vault_done"] is False
    assert home["next_step"]["clouds_should_continue"] is False


def test_gp064_status_ready_real_alias_only_and_locked(endpoint_db):
    status = get_gp064_status(endpoint_db)
    gp064 = status["gp064_status"]

    assert status["pack"]["id"] == "VAULT_GP064"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert status["pack"]["section_range"] == "GP061-GP070"

    assert gp064["ready"] is True
    assert gp064["real_storage_provider_endpoint_namespace_contract_ready"] is True
    assert gp064["real_sqlite_backed"] is True
    assert gp064["real_schema_ready"] is True
    assert gp064["real_contract_count"] == 1
    assert gp064["real_requirement_count"] == EXPECTED_REQUIREMENTS
    assert gp064["real_policy_count"] == EXPECTED_POLICIES
    assert gp064["real_blocker_count"] == EXPECTED_BLOCKERS
    assert gp064["source_gp063_secret_reference_ledger_attached"] is True
    assert gp064["endpoint_namespace_contract_ready"] is True
    assert gp064["endpoint_namespace_requirements_ready"] is True
    assert gp064["endpoint_namespace_policy_ready"] is True
    assert gp064["endpoint_alias_only"] is True
    assert gp064["namespace_alias_only"] is True
    assert gp064["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert gp064["requirement_code_count"] == len(ENDPOINT_NAMESPACE_REQUIREMENT_SPECS)
    assert gp064["policy_code_count"] == EXPECTED_POLICIES
    assert gp064["endpoint_url_stored_count"] == 0
    assert gp064["endpoint_value_present_count"] == 0
    assert gp064["namespace_value_stored_count"] == 0
    assert gp064["namespace_value_present_count"] == 0
    assert gp064["secret_value_present_count"] == 0
    assert gp064["token_material_present_count"] == 0
    assert gp064["secret_references_created_count"] == 0
    assert gp064["secret_references_activated_count"] == 0
    assert gp064["credentials_configured_count"] == 0
    assert gp064["provider_endpoint_configured_count"] == 0
    assert gp064["storage_container_configured_count"] == 0
    assert gp064["namespace_configured_count"] == 0
    assert gp064["blocks_provider_configuration_count"] == EXPECTED_BLOCKERS
    assert gp064["blocks_provider_read_write_count"] == EXPECTED_BLOCKERS
    assert gp064["blocks_object_body_view_count"] == EXPECTED_BLOCKERS
    assert gp064["blocks_export_count"] == EXPECTED_BLOCKERS
    assert gp064["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert gp064["tower_review_granted_count"] == 0
    assert gp064["resolved_count"] == 0
    assert gp064["validation_ready"] is True
    assert gp064["validation_passed"] is True
    assert gp064["safe_to_continue_to_gp065"] is True
    assert gp064["vault_done"] is False
    assert gp064["foundation_status"] == "endpoint_namespace_contract_ready_safe_to_continue_not_done"

    assert gp064["endpoint_url_stored"] is False
    assert gp064["endpoint_value_present"] is False
    assert gp064["namespace_value_stored"] is False
    assert gp064["namespace_value_present"] is False
    assert gp064["provider_endpoint_configured"] is False
    assert gp064["storage_container_configured"] is False
    assert gp064["namespace_configured"] is False
    assert gp064["credentials_configured"] is False
    assert gp064["provider_connection_tested"] is False
    assert gp064["provider_read_enabled"] is False
    assert gp064["provider_write_enabled"] is False
    assert gp064["object_body_view_enabled"] is False
    assert gp064["direct_upload_enabled"] is False
    assert gp064["export_enabled"] is False
    assert gp064["execution_enabled"] is False
    assert gp064["clouds_status"] == "parked_do_not_continue_from_vault_gp064"
    assert gp064["next_pack"] == "VAULT_GP065_REAL_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT"


def test_gp064_next_step_points_to_gp065_encryption_policy_contract():
    next_step = get_storage_provider_endpoint_namespace_next_step()["next_step"]

    assert next_step["current_section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert next_step["current_section_range"] == "GP061-GP070"
    assert next_step["next_pack"] == "VAULT_GP065_REAL_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT"
    assert next_step["next_pack_title"] == "Real Storage Provider Encryption Policy Contract"
    assert next_step["safe_to_continue_to_gp065"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

    note = next_step["owner_notebook_note"].lower()
    assert "encryption policy contract" in note
    assert "endpoint" in note
    assert "namespace" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "real sqlite endpoint/namespace contract" in rules
    assert "endpoint/namespace requirement rows" in rules
    assert "encryption policy contract" in rules
    assert "do not store actual provider endpoint urls" in rules
    assert "do not store actual bucket/container/namespace values" in rules
    assert "do not configure provider endpoint yet" in rules
    assert "do not configure storage container yet" in rules
    assert "do not configure namespace yet" in rules
    assert "do not unlock export" in rules
    assert "do not unlock execution" in rules
    assert "do not treat vault as done" in rules


def test_gp064_html_is_dark_and_mentions_endpoint_namespace_contract(monkeypatch, tmp_path):
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

    html = render_real_storage_provider_endpoint_namespace_contract_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Endpoint Namespace Contract" in html
    assert "Real Storage Provider Configuration Layer" in html
    assert "Archive Vault" in html
    assert "GP064" in html
    assert "Endpoint/namespace contract ready" in html
    assert "Alias-only rows" in html
    assert "Real SQLite-backed" in html
    assert "No endpoint configured" in html
    assert "No namespace configured" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-endpoint-namespace-contract.json" in html
    assert "/vault/gp064-status.json" in html

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


def test_gp064_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/real-storage-provider-endpoint-namespace-contract",
        "/vault/real-storage-provider-endpoint-namespace-contract.json",
        "/vault/storage-provider-endpoint-namespace-contract-record.json",
        "/vault/storage-provider-endpoint-namespace-requirements.json",
        "/vault/storage-provider-endpoint-namespace-policies.json",
        "/vault/storage-provider-endpoint-namespace-blockers.json",
        "/vault/storage-provider-endpoint-namespace-events.json",
        "/vault/storage-provider-endpoint-namespace-validation.json",
        "/vault/storage-provider-endpoint-namespace-next-step.json",
        "/vault/gp064-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp064_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
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

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/real-storage-provider-endpoint-namespace-contract",
        "/vault/real-storage-provider-endpoint-namespace-contract.json",
        "/vault/storage-provider-endpoint-namespace-contract-record.json",
        "/vault/storage-provider-endpoint-namespace-requirements.json",
        "/vault/storage-provider-endpoint-namespace-policies.json",
        "/vault/storage-provider-endpoint-namespace-blockers.json",
        "/vault/storage-provider-endpoint-namespace-events.json",
        "/vault/storage-provider-endpoint-namespace-validation.json",
        "/vault/storage-provider-endpoint-namespace-next-step.json",
        "/vault/gp064-status.json",
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
                assert b"Vault Real Storage Provider Endpoint Namespace Contract" in response.data
