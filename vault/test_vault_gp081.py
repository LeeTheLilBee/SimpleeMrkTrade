"""
Tests for VAULT GP081 — Real Storage Provider Restore Request Lock Contract
"""

from pathlib import Path
import pytest

from vault.real_storage_provider_restore_request_lock_contract_service import (
    DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,
    RESTORE_REQUEST_POLICIES,
    RESTORE_REQUEST_REQUIREMENT_SPECS,
    ensure_storage_provider_restore_request_lock_contract_schema,
    get_gp081_status,
    get_real_storage_provider_restore_request_lock_contract_home,
    get_storage_provider_restore_request_blockers,
    get_storage_provider_restore_request_events,
    get_storage_provider_restore_request_lock_contract_record,
    get_storage_provider_restore_request_next_step,
    get_storage_provider_restore_request_policies,
    get_storage_provider_restore_request_requirements,
    initialize_real_storage_provider_restore_request_lock_contract,
    record_storage_provider_restore_request_event,
    render_real_storage_provider_restore_request_lock_contract_page,
    validate_storage_provider_restore_request_lock_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_COMPONENTS = 9
EXPECTED_REQUIREMENTS = EXPECTED_SOURCE_COMPONENTS * len(RESTORE_REQUEST_REQUIREMENT_SPECS)
EXPECTED_POLICIES = len(RESTORE_REQUEST_POLICIES)
EXPECTED_BLOCKERS = 18

@pytest.fixture()
def gp081_db(tmp_path, monkeypatch):
    envs = {
        "VAULT_STORAGE_PROVIDER_DECISION_DB": "decision.sqlite",
        "VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB": "selection_registry.sqlite",
        "VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB": "capability_contract.sqlite",
        "VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB": "risk_criteria_validation.sqlite",
        "VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB": "selection_review_receipt.sqlite",
        "VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB": "prep_readiness.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB": "config_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB": "credential_boundary.sqlite",
        "VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB": "secret_reference_ledger.sqlite",
        "VAULT_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT_DB": "endpoint_namespace_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT_DB": "encryption_policy_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT_DB": "connection_test_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT_DB": "write_path_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT_DB": "read_path_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT_DB": "object_body_view_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT_DB": "configuration_readiness_checkpoint.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT_DB": "object_catalog_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_METADATA_RECEIPT_CONTRACT_DB": "redacted_metadata_receipt_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_CONTRACT_DB": "receipt_lineage_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_DB": "redacted_access_view_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_PACKET_LOCK_CONTRACT_DB": "owner_review_packet_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_QUEUE_LOCK_CONTRACT_DB": "owner_review_queue_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_LOCK_CONTRACT_DB": "owner_review_decision_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_DB": "owner_review_decision_receipt_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_CLOSEOUT_LOCK_CONTRACT_DB": "owner_review_closeout_lock_contract.sqlite",
        "VAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_DB": "provider_receipt_redacted_access_readiness.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT_DB": "restore_request_lock_contract.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "restore_request_lock_contract.sqlite")

def test_gp081_schema_is_real_sqlite_backed(gp081_db):
    result = ensure_storage_provider_restore_request_lock_contract_schema(gp081_db)

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert Path(result["db_path"]).exists()
    assert "vault_storage_provider_restore_request_lock_contracts" in result["tables"]
    assert "vault_storage_provider_restore_request_requirements" in result["tables"]
    assert "vault_storage_provider_restore_request_policies" in result["tables"]
    assert "vault_storage_provider_restore_request_blockers" in result["tables"]
    assert "vault_storage_provider_restore_request_events" in result["tables"]

def test_gp081_initialize_creates_real_contract_requirements_policies_blockers_events(gp081_db):
    result = initialize_real_storage_provider_restore_request_lock_contract(gp081_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["contract_count"] == 1
    assert result["requirement_count"] == EXPECTED_REQUIREMENTS
    assert result["policy_count"] == EXPECTED_POLICIES
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_restore_request_lock_contract(gp081_db)
    assert second["contract_count"] == 1
    assert second["requirement_count"] == EXPECTED_REQUIREMENTS
    assert second["policy_count"] == EXPECTED_POLICIES
    assert second["blocker_count"] == EXPECTED_BLOCKERS

def test_gp081_contract_sourced_from_gp080_and_locked(gp081_db):
    contract = get_storage_provider_restore_request_lock_contract_record(gp081_db)["restore_request_lock_contract"]

    assert contract["restore_request_lock_contract_id"] == DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP081"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_LAYER"
    assert contract["section_range"] == "GP081-GP090"
    assert contract["previous_section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
    assert contract["previous_section_range"] == "GP071-GP080"
    assert contract["source_readiness_checkpoint_id"] == "VPRRARC-GP080-001"
    assert contract["source_readiness_pack_id"] == "VAULT_GP080"
    assert contract["contract_status"] == "REAL_RESTORE_REQUEST_LOCK_CONTRACT_OPEN_TEMPLATE_ONLY_TOWER_LOCKED"

    assert contract["restore_request_lock_contract_ready"] is True
    assert contract["restore_request_requirements_ready"] is True
    assert contract["restore_request_policies_ready"] is True
    assert contract["restore_request_blockers_ready"] is True
    assert contract["restore_request_validation_ready"] is True
    assert contract["restore_request_locked"] is True
    assert contract["restore_request_template_only"] is True
    assert contract["source_gp080_readiness_checkpoint_attached"] is True
    assert contract["safe_to_continue_to_gp082"] is True

    locked_false_fields = [
        "restore_request_created",
        "restore_request_submitted",
        "restore_request_finalized",
        "restore_request_approved",
        "restore_request_denied",
        "restore_eligibility_checked",
        "provider_restore_api_configured",
        "provider_restore_api_called",
        "restore_job_created",
        "restore_object_selected",
        "provider_object_catalog_unlocked",
        "provider_objects_listed",
        "provider_metadata_imported",
        "object_identifier_collected",
        "object_body_read",
        "object_body_view_enabled",
        "object_body_download_enabled",
        "tower_unlock_requested",
        "tower_unlock_granted",
        "export_package_created",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
        "vault_done",
    ]
    for field in locked_false_fields:
        assert contract[field] is False

    assert contract["contract_data"]["next_pack"] == "VAULT_GP082_REAL_STORAGE_PROVIDER_RESTORE_ELIGIBILITY_LOCK_CONTRACT"
    assert contract["contract_data"]["safe_to_continue_to_gp082"] is True

def test_gp081_requirements_are_real_template_only_and_locked(gp081_db):
    payload = get_storage_provider_restore_request_requirements(gp081_db)

    assert payload["requirement_count"] == EXPECTED_REQUIREMENTS
    assert payload["source_component_count"] == EXPECTED_SOURCE_COMPONENTS
    assert payload["requirement_code_count"] == len(RESTORE_REQUEST_REQUIREMENT_SPECS)
    assert payload["requirement_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["requirement_verified_count"] == 0
    assert payload["restore_request_locked_count"] == EXPECTED_REQUIREMENTS
    assert payload["template_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["restore_redaction_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["tower_review_granted_count"] == 0

    assert payload["restore_request_created_count"] == 0
    assert payload["restore_request_submitted_count"] == 0
    assert payload["restore_request_finalized_count"] == 0
    assert payload["restore_eligibility_checked_count"] == 0
    assert payload["provider_restore_api_configured_count"] == 0
    assert payload["provider_restore_api_called_count"] == 0
    assert payload["restore_job_created_count"] == 0
    assert payload["restore_object_selected_count"] == 0
    assert payload["provider_object_catalog_unlocked_count"] == 0
    assert payload["provider_objects_listed_count"] == 0
    assert payload["provider_metadata_imported_count"] == 0
    assert payload["object_identifier_collected_count"] == 0
    assert payload["object_body_read_count"] == 0
    assert payload["object_body_view_enabled_count"] == 0
    assert payload["object_body_download_enabled_count"] == 0
    assert payload["tower_unlock_granted_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    for item in payload["requirements"]:
        assert item["restore_request_requirement_id"].startswith("VSPRQR-")
        assert item["restore_request_lock_contract_id"] == DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID
        assert item["source_component_id"].startswith("VPRRARC-COMP-")
        assert item["restore_request_locked"] is True
        assert item["template_only"] is True
        assert item["restore_request_created"] is False
        assert item["restore_request_submitted"] is False
        assert item["provider_restore_api_called"] is False
        assert item["object_body_read"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp081_policies_are_real_template_only_and_locked(gp081_db):
    payload = get_storage_provider_restore_request_policies(gp081_db)

    assert payload["policy_count"] == EXPECTED_POLICIES
    assert payload["policy_code_count"] == EXPECTED_POLICIES
    assert payload["policy_required_count"] == EXPECTED_POLICIES
    assert payload["policy_verified_count"] == 0
    assert payload["tower_review_granted_count"] == 0

    assert payload["restore_request_created_count"] == 0
    assert payload["restore_request_submitted_count"] == 0
    assert payload["restore_eligibility_checked_count"] == 0
    assert payload["provider_restore_api_configured_count"] == 0
    assert payload["provider_restore_api_called_count"] == 0
    assert payload["restore_job_created_count"] == 0
    assert payload["restore_object_selected_count"] == 0
    assert payload["object_body_read_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    for item in payload["policies"]:
        assert item["restore_request_policy_id"].startswith("VSPRQP-")
        assert item["restore_request_lock_contract_id"] == DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID
        assert item["restore_request_created"] is False
        assert item["provider_restore_api_called"] is False
        assert item["restore_job_created"] is False
        assert item["object_body_read"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp081_blockers_are_real_and_carried_from_gp080(gp081_db):
    payload = get_storage_provider_restore_request_blockers(gp081_db)

    assert payload["blocker_count"] == EXPECTED_BLOCKERS
    assert payload["blocker_active_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_restore_request_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_restore_submission_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_restore_eligibility_check_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_restore_api_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_restore_job_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_restore_object_selection_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_unlock_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_body_read_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_direct_upload_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_export_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_required_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_granted_count"] == 0
    assert payload["risk_accepted_count"] == 0
    assert payload["risk_waived_count"] == 0
    assert payload["mitigation_approved_count"] == 0
    assert payload["resolved_count"] == 0

    for item in payload["blockers"]:
        assert item["restore_request_blocker_id"].startswith("VSPRQB-")
        assert item["restore_request_lock_contract_id"] == DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID
        assert item["source_readiness_blocker_id"].startswith("VPRRARC-BLOCK-")
        assert item["blocker_active"] is True
        assert item["blocks_restore_request"] is True
        assert item["blocks_restore_submission"] is True
        assert item["blocks_provider_restore_api"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["resolved"] is False

def test_gp081_event_log_and_manual_event_write_do_not_unlock(gp081_db):
    events = get_storage_provider_restore_request_events(gp081_db)
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP080_READINESS_CHECKPOINT_ATTACHED" in event_types
    assert "REAL_RESTORE_REQUEST_REQUIREMENTS_CREATED_TEMPLATE_ONLY" in event_types
    assert "REAL_RESTORE_REQUEST_POLICIES_CREATED_TEMPLATE_ONLY" in event_types
    assert "REAL_RESTORE_REQUEST_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "RESTORE_REQUEST_LOCKS_CONFIRMED" in event_types

    before = events["event_count"]
    written = record_storage_provider_restore_request_event(
        "OWNER_GP081_RESTORE_REQUEST_REVIEWED",
        {"reviewer": "owner"},
        gp081_db,
    )
    after = get_storage_provider_restore_request_events(gp081_db)

    assert after["event_count"] == before + 1
    assert written["event_written"] is True
    assert written["restore_request_lock_contract_ready"] is True
    assert written["restore_request_created"] is False
    assert written["restore_request_submitted"] is False
    assert written["restore_eligibility_checked"] is False
    assert written["provider_restore_api_configured"] is False
    assert written["provider_restore_api_called"] is False
    assert written["restore_job_created"] is False
    assert written["object_body_read"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

def test_gp081_validation_home_status_and_next_step(gp081_db):
    validation = validate_storage_provider_restore_request_lock_contract(gp081_db)

    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp082"] is True
    assert validation["vault_done"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_RESTORE_REQUEST_LOCK_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP080_READINESS_CHECKPOINT_ATTACHED" in codes
    assert "NEW_SECTION_GP081_GP090" in codes
    assert "PREVIOUS_SECTION_GP071_GP080_ATTACHED" in codes
    assert "RESTORE_REQUEST_LOCK_CONTRACT_READY" in codes
    assert "RESTORE_REQUEST_REQUIREMENTS_EXIST" in codes
    assert "RESTORE_REQUEST_POLICIES_EXIST" in codes
    assert "READINESS_BLOCKERS_CARRIED_FORWARD" in codes
    assert "NO_CONTRACT_RESTORE_REQUEST_CREATED" in codes
    assert "NO_CONTRACT_RESTORE_REQUEST_SUBMITTED" in codes
    assert "NO_CONTRACT_RESTORE_ELIGIBILITY_CHECKED" in codes
    assert "NO_CONTRACT_PROVIDER_RESTORE_API_CONFIGURED" in codes
    assert "NO_CONTRACT_PROVIDER_RESTORE_API_CALLED" in codes
    assert "NO_CONTRACT_RESTORE_JOB_CREATED" in codes
    assert "NO_CONTRACT_OBJECT_BODY_READ" in codes
    assert "NO_CONTRACT_DIRECT_UPLOAD_ENABLED" in codes
    assert "NO_CONTRACT_EXPORT_ENABLED" in codes
    assert "NO_CONTRACT_EXECUTION_ENABLED" in codes
    assert "NO_CONTRACT_VAULT_DONE" in codes

    home = get_real_storage_provider_restore_request_lock_contract_home(gp081_db)
    truth = home["restore_request_truth"]
    assert truth["real_storage_provider_restore_request_lock_contract_ready"] is True
    assert truth["validation_passed"] is True
    assert truth["restore_request_locked"] is True
    assert truth["restore_request_template_only"] is True
    assert truth["requirement_count"] == EXPECTED_REQUIREMENTS
    assert truth["policy_count"] == EXPECTED_POLICIES
    assert truth["blocker_count"] == EXPECTED_BLOCKERS
    assert truth["restore_request_created"] is False
    assert truth["restore_request_submitted"] is False
    assert truth["restore_eligibility_checked"] is False
    assert truth["provider_restore_api_configured"] is False
    assert truth["provider_restore_api_called"] is False
    assert truth["restore_job_created"] is False
    assert truth["restore_object_selected"] is False
    assert truth["provider_object_catalog_unlocked"] is False
    assert truth["provider_objects_listed"] is False
    assert truth["object_body_read"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["export_enabled"] is False
    assert truth["execution_enabled"] is False
    assert truth["vault_done"] is False

    status = get_gp081_status(gp081_db)
    gp081 = status["gp081_status"]
    assert gp081["ready"] is True
    assert gp081["validation_passed"] is True
    assert gp081["safe_to_continue_to_gp082"] is True
    assert gp081["source_component_count"] == EXPECTED_SOURCE_COMPONENTS
    assert gp081["requirement_code_count"] == len(RESTORE_REQUEST_REQUIREMENT_SPECS)
    assert gp081["policy_code_count"] == EXPECTED_POLICIES
    assert gp081["blocker_count"] == EXPECTED_BLOCKERS
    assert gp081["restore_request_created_count"] == 0
    assert gp081["restore_request_submitted_count"] == 0
    assert gp081["restore_eligibility_checked_count"] == 0
    assert gp081["provider_restore_api_configured_count"] == 0
    assert gp081["provider_restore_api_called_count"] == 0
    assert gp081["restore_job_created_count"] == 0
    assert gp081["object_body_read_count"] == 0
    assert gp081["direct_upload_enabled_count"] == 0
    assert gp081["export_enabled_count"] == 0
    assert gp081["execution_enabled_count"] == 0
    assert gp081["vault_done"] is False
    assert gp081["clouds_status"] == "parked_do_not_continue_from_vault_gp081"
    assert gp081["next_pack"] == "VAULT_GP082_REAL_STORAGE_PROVIDER_RESTORE_ELIGIBILITY_LOCK_CONTRACT"

    next_step = get_storage_provider_restore_request_next_step()["next_step"]
    assert next_step["current_section_range"] == "GP081-GP090"
    assert next_step["previous_section_range"] == "GP071-GP080"
    assert next_step["next_pack"] == "VAULT_GP082_REAL_STORAGE_PROVIDER_RESTORE_ELIGIBILITY_LOCK_CONTRACT"
    assert next_step["safe_to_continue_to_gp082"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp081_html_is_dark_and_mentions_restore_request(monkeypatch, tmp_path):
    envs = {
        "VAULT_STORAGE_PROVIDER_DECISION_DB": "html_decision.sqlite",
        "VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB": "html_selection.sqlite",
        "VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB": "html_capability.sqlite",
        "VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB": "html_validation.sqlite",
        "VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB": "html_receipt.sqlite",
        "VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB": "html_readiness.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB": "html_config.sqlite",
        "VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB": "html_credential.sqlite",
        "VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB": "html_ledger.sqlite",
        "VAULT_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT_DB": "html_endpoint.sqlite",
        "VAULT_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT_DB": "html_encryption.sqlite",
        "VAULT_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT_DB": "html_connection.sqlite",
        "VAULT_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT_DB": "html_write.sqlite",
        "VAULT_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT_DB": "html_read.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT_DB": "html_obv.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT_DB": "html_gp070.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT_DB": "html_gp071.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_METADATA_RECEIPT_CONTRACT_DB": "html_gp072.sqlite",
        "VAULT_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_CONTRACT_DB": "html_gp073.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_DB": "html_gp074.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_PACKET_LOCK_CONTRACT_DB": "html_gp075.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_QUEUE_LOCK_CONTRACT_DB": "html_gp076.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_LOCK_CONTRACT_DB": "html_gp077.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_DB": "html_gp078.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_CLOSEOUT_LOCK_CONTRACT_DB": "html_gp079.sqlite",
        "VAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_DB": "html_gp080.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT_DB": "html_gp081.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_storage_provider_restore_request_lock_contract_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Restore Request Lock Contract" in html
    assert "Real Provider Restore and Export Governance Layer" in html
    assert "GP081" in html
    assert "New section opened" in html
    assert "Restore request locked" in html
    assert "No restore request" in html
    assert "No provider API" in html
    assert "No object body read" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-restore-request-lock-contract.json" in html
    assert "/vault/gp081-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp081_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-storage-provider-restore-request-lock-contract",
        "/vault/real-storage-provider-restore-request-lock-contract.json",
        "/vault/storage-provider-restore-request-lock-contract-record.json",
        "/vault/storage-provider-restore-request-requirements.json",
        "/vault/storage-provider-restore-request-policies.json",
        "/vault/storage-provider-restore-request-blockers.json",
        "/vault/storage-provider-restore-request-events.json",
        "/vault/storage-provider-restore-request-validation.json",
        "/vault/storage-provider-restore-request-next-step.json",
        "/vault/gp081-status.json",
    ]
    for route in required_routes:
        assert route in text

def test_gp081_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
    envs = {
        "VAULT_STORAGE_PROVIDER_DECISION_DB": "routes_decision.sqlite",
        "VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB": "routes_selection.sqlite",
        "VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB": "routes_capability.sqlite",
        "VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB": "routes_validation.sqlite",
        "VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB": "routes_receipt.sqlite",
        "VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB": "routes_readiness.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB": "routes_config.sqlite",
        "VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB": "routes_credential.sqlite",
        "VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB": "routes_ledger.sqlite",
        "VAULT_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT_DB": "routes_endpoint.sqlite",
        "VAULT_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT_DB": "routes_encryption.sqlite",
        "VAULT_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT_DB": "routes_connection.sqlite",
        "VAULT_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT_DB": "routes_write.sqlite",
        "VAULT_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT_DB": "routes_read.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT_DB": "routes_obv.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT_DB": "routes_gp070.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT_DB": "routes_gp071.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_METADATA_RECEIPT_CONTRACT_DB": "routes_gp072.sqlite",
        "VAULT_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_CONTRACT_DB": "routes_gp073.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_DB": "routes_gp074.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_PACKET_LOCK_CONTRACT_DB": "routes_gp075.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_QUEUE_LOCK_CONTRACT_DB": "routes_gp076.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_LOCK_CONTRACT_DB": "routes_gp077.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_DB": "routes_gp078.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_CLOSEOUT_LOCK_CONTRACT_DB": "routes_gp079.sqlite",
        "VAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_DB": "routes_gp080.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT_DB": "routes_gp081.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()
    routes = [
        "/vault/real-storage-provider-restore-request-lock-contract",
        "/vault/real-storage-provider-restore-request-lock-contract.json",
        "/vault/storage-provider-restore-request-lock-contract-record.json",
        "/vault/storage-provider-restore-request-requirements.json",
        "/vault/storage-provider-restore-request-policies.json",
        "/vault/storage-provider-restore-request-blockers.json",
        "/vault/storage-provider-restore-request-events.json",
        "/vault/storage-provider-restore-request-validation.json",
        "/vault/storage-provider-restore-request-next-step.json",
        "/vault/gp081-status.json",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Real Storage Provider Restore Request Lock Contract" in response.data
