"""
Tests for VAULT GP089 — Real Storage Provider Restore Export Lock Contract
"""

from pathlib import Path
import pytest

from vault.real_storage_provider_restore_export_lock_contract_service import (
    DEFAULT_RESTORE_EXPORT_LOCK_CONTRACT_ID,
    RESTORE_EXPORT_POLICIES,
    RESTORE_EXPORT_REQUIREMENT_SPECS,
    ensure_storage_provider_restore_export_lock_contract_schema,
    get_gp089_status,
    get_real_storage_provider_restore_export_lock_contract_home,
    get_storage_provider_restore_export_blockers,
    get_storage_provider_restore_export_events,
    get_storage_provider_restore_export_lock_contract_record,
    get_storage_provider_restore_export_next_step,
    get_storage_provider_restore_export_policies,
    get_storage_provider_restore_export_requirements,
    initialize_real_storage_provider_restore_export_lock_contract,
    record_storage_provider_restore_export_event,
    render_real_storage_provider_restore_export_lock_contract_page,
    validate_storage_provider_restore_export_lock_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_REQUIREMENTS = 54
EXPECTED_REQUIREMENTS = EXPECTED_SOURCE_REQUIREMENTS * len(RESTORE_EXPORT_REQUIREMENT_SPECS)
EXPECTED_POLICIES = len(RESTORE_EXPORT_POLICIES)
EXPECTED_BLOCKERS = 18

@pytest.fixture()
def gp089_db(tmp_path, monkeypatch):
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
        "VAULT_STORAGE_PROVIDER_RESTORE_ELIGIBILITY_LOCK_CONTRACT_DB": "restore_eligibility_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_AUTHORITY_LOCK_CONTRACT_DB": "restore_authority_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_SCOPE_LOCK_CONTRACT_DB": "restore_scope_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_TARGET_LOCK_CONTRACT_DB": "restore_target_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_OBJECT_LOCK_CONTRACT_DB": "restore_object_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_JOB_LOCK_CONTRACT_DB": "restore_job_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_API_LOCK_CONTRACT_DB": "restore_api_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_EXPORT_LOCK_CONTRACT_DB": "restore_export_lock_contract.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "restore_export_lock_contract.sqlite")

def test_gp089_schema_and_initialize_are_real_sqlite_backed(gp089_db):
    schema = ensure_storage_provider_restore_export_lock_contract_schema(gp089_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_storage_provider_restore_export_lock_contracts" in schema["tables"]
    assert "vault_storage_provider_restore_export_requirements" in schema["tables"]
    assert "vault_storage_provider_restore_export_policies" in schema["tables"]
    assert "vault_storage_provider_restore_export_blockers" in schema["tables"]
    assert "vault_storage_provider_restore_export_events" in schema["tables"]

    result = initialize_real_storage_provider_restore_export_lock_contract(gp089_db)
    assert result["initialized"] is True
    assert result["contract_count"] == 1
    assert result["requirement_count"] == EXPECTED_REQUIREMENTS
    assert result["policy_count"] == EXPECTED_POLICIES
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

def test_gp089_contract_sourced_from_gp088_and_locked(gp089_db):
    contract = get_storage_provider_restore_export_lock_contract_record(gp089_db)["restore_export_lock_contract"]

    assert contract["restore_export_lock_contract_id"] == DEFAULT_RESTORE_EXPORT_LOCK_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP089"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_LAYER"
    assert contract["section_range"] == "GP081-GP090"
    assert contract["source_restore_api_lock_contract_id"] == "VSPRAPILC-GP088-001"
    assert contract["source_restore_api_pack_id"] == "VAULT_GP088"
    assert contract["contract_status"] == "REAL_RESTORE_EXPORT_LOCK_CONTRACT_OPEN_TEMPLATE_ONLY_TOWER_LOCKED"

    assert contract["restore_export_lock_contract_ready"] is True
    assert contract["restore_export_requirements_ready"] is True
    assert contract["restore_export_policies_ready"] is True
    assert contract["restore_export_blockers_ready"] is True
    assert contract["restore_export_validation_ready"] is True
    assert contract["restore_export_locked"] is True
    assert contract["restore_export_template_only"] is True
    assert contract["source_restore_api_lock_contract_attached"] is True
    assert contract["safe_to_continue_to_gp090"] is True

    locked_false_fields = [
        "restore_export_package_created",
        "restore_export_manifest_created",
        "restore_export_download_enabled",
        "export_package_created",
        "export_manifest_created",
        "export_download_enabled",
        "direct_upload_enabled",
        "export_enabled",
        "provider_restore_api_called",
        "object_body_read",
        "object_body_view_enabled",
        "object_body_download_enabled",
        "execution_enabled",
        "vault_done",
    ]
    for field in locked_false_fields:
        assert contract[field] is False

    assert contract["contract_data"]["next_pack"] == "VAULT_GP090_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_READINESS_CHECKPOINT"
    assert contract["contract_data"]["safe_to_continue_to_gp090"] is True

def test_gp089_requirements_policies_and_blockers_are_locked(gp089_db):
    requirements = get_storage_provider_restore_export_requirements(gp089_db)
    assert requirements["requirement_count"] == EXPECTED_REQUIREMENTS
    assert requirements["source_requirement_count"] == EXPECTED_SOURCE_REQUIREMENTS
    assert requirements["requirement_code_count"] == len(RESTORE_EXPORT_REQUIREMENT_SPECS)
    assert requirements["requirement_required_count"] == EXPECTED_REQUIREMENTS
    assert requirements["requirement_verified_count"] == 0
    assert requirements["restore_export_locked_count"] == EXPECTED_REQUIREMENTS
    assert requirements["template_only_count"] == EXPECTED_REQUIREMENTS
    assert requirements["export_redaction_required_count"] == EXPECTED_REQUIREMENTS
    assert requirements["tower_review_granted_count"] == 0

    assert requirements["restore_export_package_created_count"] == 0
    assert requirements["restore_export_manifest_created_count"] == 0
    assert requirements["restore_export_download_enabled_count"] == 0
    assert requirements["export_package_created_count"] == 0
    assert requirements["export_manifest_created_count"] == 0
    assert requirements["export_download_enabled_count"] == 0
    assert requirements["direct_upload_enabled_count"] == 0
    assert requirements["export_enabled_count"] == 0
    assert requirements["provider_restore_api_called_count"] == 0
    assert requirements["object_body_read_count"] == 0
    assert requirements["execution_enabled_count"] == 0

    policies = get_storage_provider_restore_export_policies(gp089_db)
    assert policies["policy_count"] == EXPECTED_POLICIES
    assert policies["policy_code_count"] == EXPECTED_POLICIES
    assert policies["policy_required_count"] == EXPECTED_POLICIES
    assert policies["policy_verified_count"] == 0
    assert policies["restore_export_package_created_count"] == 0
    assert policies["restore_export_manifest_created_count"] == 0
    assert policies["restore_export_download_enabled_count"] == 0
    assert policies["provider_restore_api_called_count"] == 0
    assert policies["object_body_read_count"] == 0
    assert policies["direct_upload_enabled_count"] == 0
    assert policies["export_enabled_count"] == 0
    assert policies["execution_enabled_count"] == 0

    blockers = get_storage_provider_restore_export_blockers(gp089_db)
    assert blockers["blocker_count"] == EXPECTED_BLOCKERS
    assert blockers["blocker_active_count"] == EXPECTED_BLOCKERS
    assert blockers["blocks_restore_export_package_count"] == EXPECTED_BLOCKERS
    assert blockers["blocks_restore_export_manifest_count"] == EXPECTED_BLOCKERS
    assert blockers["blocks_restore_export_download_count"] == EXPECTED_BLOCKERS
    assert blockers["blocks_restore_export_enablement_count"] == EXPECTED_BLOCKERS
    assert blockers["blocks_direct_upload_count"] == EXPECTED_BLOCKERS
    assert blockers["blocks_provider_restore_api_count"] == EXPECTED_BLOCKERS
    assert blockers["blocks_object_body_read_count"] == EXPECTED_BLOCKERS
    assert blockers["blocks_export_count"] == EXPECTED_BLOCKERS
    assert blockers["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert blockers["tower_review_granted_count"] == 0
    assert blockers["resolved_count"] == 0

def test_gp089_event_log_and_manual_event_write_do_not_unlock(gp089_db):
    events = get_storage_provider_restore_export_events(gp089_db)
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_RESTORE_EXPORT_LOCK_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP088_RESTORE_API_LOCK_CONTRACT_ATTACHED" in event_types
    assert "REAL_RESTORE_EXPORT_REQUIREMENTS_CREATED_TEMPLATE_ONLY" in event_types
    assert "REAL_RESTORE_EXPORT_POLICIES_CREATED_TEMPLATE_ONLY" in event_types
    assert "REAL_RESTORE_EXPORT_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "RESTORE_EXPORT_LOCKS_CONFIRMED" in event_types

    before = events["event_count"]
    written = record_storage_provider_restore_export_event(
        "OWNER_GP089_RESTORE_EXPORT_REVIEWED",
        {"reviewer": "owner"},
        gp089_db,
    )
    after = get_storage_provider_restore_export_events(gp089_db)

    assert after["event_count"] == before + 1
    assert written["event_written"] is True
    assert written["restore_export_lock_contract_ready"] is True
    assert written["restore_export_package_created"] is False
    assert written["restore_export_manifest_created"] is False
    assert written["restore_export_download_enabled"] is False
    assert written["export_package_created"] is False
    assert written["export_manifest_created"] is False
    assert written["direct_upload_enabled"] is False
    assert written["export_enabled"] is False
    assert written["provider_restore_api_called"] is False
    assert written["object_body_read"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

def test_gp089_validation_home_status_and_next_step(gp089_db):
    validation = validate_storage_provider_restore_export_lock_contract(gp089_db)

    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp090"] is True
    assert validation["vault_done"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_RESTORE_EXPORT_LOCK_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP088_RESTORE_API_LOCK_CONTRACT_ATTACHED" in codes
    assert "RESTORE_EXPORT_LOCK_CONTRACT_READY" in codes
    assert "RESTORE_EXPORT_REQUIREMENTS_EXIST" in codes
    assert "RESTORE_EXPORT_POLICIES_EXIST" in codes
    assert "RESTORE_API_BLOCKERS_CARRIED_FORWARD" in codes
    assert "NO_CONTRACT_RESTORE_EXPORT_PACKAGE_CREATED" in codes
    assert "NO_CONTRACT_EXPORT_PACKAGE_CREATED" in codes
    assert "NO_CONTRACT_DIRECT_UPLOAD_ENABLED" in codes
    assert "NO_CONTRACT_EXPORT_ENABLED" in codes
    assert "NO_CONTRACT_EXECUTION_ENABLED" in codes
    assert "NO_CONTRACT_VAULT_DONE" in codes

    home = get_real_storage_provider_restore_export_lock_contract_home(gp089_db)
    truth = home["restore_export_truth"]
    assert truth["real_storage_provider_restore_export_lock_contract_ready"] is True
    assert truth["validation_passed"] is True
    assert truth["restore_export_locked"] is True
    assert truth["restore_export_template_only"] is True
    assert truth["requirement_count"] == EXPECTED_REQUIREMENTS
    assert truth["policy_count"] == EXPECTED_POLICIES
    assert truth["blocker_count"] == EXPECTED_BLOCKERS
    assert truth["restore_export_package_created"] is False
    assert truth["restore_export_manifest_created"] is False
    assert truth["restore_export_download_enabled"] is False
    assert truth["export_package_created"] is False
    assert truth["export_manifest_created"] is False
    assert truth["export_download_enabled"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["export_enabled"] is False
    assert truth["provider_restore_api_called"] is False
    assert truth["object_body_read"] is False
    assert truth["execution_enabled"] is False
    assert truth["vault_done"] is False

    status = get_gp089_status(gp089_db)
    gp089 = status["gp089_status"]
    assert gp089["ready"] is True
    assert gp089["validation_passed"] is True
    assert gp089["safe_to_continue_to_gp090"] is True
    assert gp089["source_requirement_count"] == EXPECTED_SOURCE_REQUIREMENTS
    assert gp089["requirement_code_count"] == len(RESTORE_EXPORT_REQUIREMENT_SPECS)
    assert gp089["policy_code_count"] == EXPECTED_POLICIES
    assert gp089["blocker_count"] == EXPECTED_BLOCKERS
    assert gp089["restore_export_package_created_count"] == 0
    assert gp089["restore_export_manifest_created_count"] == 0
    assert gp089["restore_export_download_enabled_count"] == 0
    assert gp089["export_package_created_count"] == 0
    assert gp089["direct_upload_enabled_count"] == 0
    assert gp089["export_enabled_count"] == 0
    assert gp089["execution_enabled_count"] == 0
    assert gp089["vault_done"] is False
    assert gp089["clouds_status"] == "parked_do_not_continue_from_vault_gp089"
    assert gp089["next_pack"] == "VAULT_GP090_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_READINESS_CHECKPOINT"

    next_step = get_storage_provider_restore_export_next_step()["next_step"]
    assert next_step["current_section_range"] == "GP081-GP090"
    assert next_step["next_pack"] == "VAULT_GP090_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_READINESS_CHECKPOINT"
    assert next_step["safe_to_continue_to_gp090"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp089_html_is_dark_and_mentions_restore_export(monkeypatch, tmp_path):
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
        "VAULT_STORAGE_PROVIDER_RESTORE_ELIGIBILITY_LOCK_CONTRACT_DB": "html_gp082.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_AUTHORITY_LOCK_CONTRACT_DB": "html_gp083.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_SCOPE_LOCK_CONTRACT_DB": "html_gp084.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_TARGET_LOCK_CONTRACT_DB": "html_gp085.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_OBJECT_LOCK_CONTRACT_DB": "html_gp086.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_JOB_LOCK_CONTRACT_DB": "html_gp087.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_API_LOCK_CONTRACT_DB": "html_gp088.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_EXPORT_LOCK_CONTRACT_DB": "html_gp089.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_storage_provider_restore_export_lock_contract_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Restore Export Lock Contract" in html
    assert "Real Provider Restore and Export Governance Layer" in html
    assert "GP089" in html
    assert "Export locked" in html
    assert "Template-only" in html
    assert "No export package" in html
    assert "No manifest" in html
    assert "No download" in html
    assert "No direct upload" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-restore-export-lock-contract.json" in html
    assert "/vault/gp089-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp089_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-storage-provider-restore-export-lock-contract",
        "/vault/real-storage-provider-restore-export-lock-contract.json",
        "/vault/storage-provider-restore-export-lock-contract-record.json",
        "/vault/storage-provider-restore-export-requirements.json",
        "/vault/storage-provider-restore-export-policies.json",
        "/vault/storage-provider-restore-export-blockers.json",
        "/vault/storage-provider-restore-export-events.json",
        "/vault/storage-provider-restore-export-validation.json",
        "/vault/storage-provider-restore-export-next-step.json",
        "/vault/gp089-status.json",
    ]
    for route in required_routes:
        assert route in text
