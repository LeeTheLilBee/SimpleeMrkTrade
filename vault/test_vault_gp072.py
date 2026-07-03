"""
Tests for VAULT GP072 — Real Storage Provider Redacted Metadata Receipt Contract
"""

from pathlib import Path
import pytest

from vault.real_storage_provider_redacted_metadata_receipt_contract_service import (
    DEFAULT_REDACTED_METADATA_RECEIPT_CONTRACT_ID,
    REDACTED_METADATA_POLICIES,
    REDACTED_METADATA_REQUIREMENT_SPECS,
    ensure_storage_provider_redacted_metadata_receipt_contract_schema,
    get_gp072_status,
    get_real_storage_provider_redacted_metadata_receipt_contract_home,
    get_storage_provider_redacted_metadata_receipt_blockers,
    get_storage_provider_redacted_metadata_receipt_contract_record,
    get_storage_provider_redacted_metadata_receipt_events,
    get_storage_provider_redacted_metadata_receipt_next_step,
    get_storage_provider_redacted_metadata_receipt_policies,
    get_storage_provider_redacted_metadata_receipt_requirements,
    initialize_real_storage_provider_redacted_metadata_receipt_contract,
    record_storage_provider_redacted_metadata_receipt_event,
    render_real_storage_provider_redacted_metadata_receipt_contract_page,
    validate_storage_provider_redacted_metadata_receipt_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_PACKS = 9
EXPECTED_REQUIREMENTS = EXPECTED_SOURCE_PACKS * len(REDACTED_METADATA_REQUIREMENT_SPECS)
EXPECTED_POLICIES = len(REDACTED_METADATA_POLICIES)
EXPECTED_BLOCKERS = 14

@pytest.fixture()
def gp072_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "redacted_metadata_receipt_contract.sqlite")

def test_gp072_schema_is_real_sqlite_backed(gp072_db):
    result = ensure_storage_provider_redacted_metadata_receipt_contract_schema(gp072_db)

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert Path(result["db_path"]).exists()
    assert "vault_storage_provider_redacted_metadata_receipt_contracts" in result["tables"]
    assert "vault_storage_provider_redacted_metadata_receipt_requirements" in result["tables"]
    assert "vault_storage_provider_redacted_metadata_receipt_policies" in result["tables"]
    assert "vault_storage_provider_redacted_metadata_receipt_blockers" in result["tables"]
    assert "vault_storage_provider_redacted_metadata_receipt_events" in result["tables"]

def test_gp072_initialize_creates_real_contract_requirements_policies_blockers_events(gp072_db):
    result = initialize_real_storage_provider_redacted_metadata_receipt_contract(gp072_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["contract_count"] == 1
    assert result["requirement_count"] == EXPECTED_REQUIREMENTS
    assert result["policy_count"] == EXPECTED_POLICIES
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_redacted_metadata_receipt_contract(gp072_db)
    assert second["contract_count"] == 1
    assert second["requirement_count"] == EXPECTED_REQUIREMENTS
    assert second["policy_count"] == EXPECTED_POLICIES
    assert second["blocker_count"] == EXPECTED_BLOCKERS

def test_gp072_contract_sourced_from_gp071_and_locked(gp072_db):
    contract = get_storage_provider_redacted_metadata_receipt_contract_record(gp072_db)["redacted_metadata_receipt_contract"]

    assert contract["redacted_metadata_receipt_contract_id"] == DEFAULT_REDACTED_METADATA_RECEIPT_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP072"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
    assert contract["section_range"] == "GP071-GP080"
    assert contract["source_object_catalog_lock_contract_id"] == "VSPOCLC-GP071-001"
    assert contract["source_object_catalog_pack_id"] == "VAULT_GP071"
    assert contract["contract_status"] == "REAL_REDACTED_METADATA_RECEIPT_CONTRACT_OPEN_TEMPLATE_ONLY_TOWER_LOCKED"

    assert contract["redacted_metadata_receipt_contract_ready"] is True
    assert contract["redacted_metadata_requirements_ready"] is True
    assert contract["redacted_metadata_policies_ready"] is True
    assert contract["redacted_metadata_blockers_ready"] is True
    assert contract["redacted_metadata_validation_ready"] is True
    assert contract["redacted_metadata_receipt_locked"] is True
    assert contract["receipt_template_only"] is True
    assert contract["metadata_redaction_required"] is True
    assert contract["source_object_catalog_lock_contract_attached"] is True
    assert contract["safe_to_continue_to_gp073"] is True

    locked_false_fields = [
        "redacted_metadata_receipt_configured",
        "redacted_metadata_receipt_attempted",
        "redacted_metadata_receipt_enabled",
        "redacted_metadata_receipt_created",
        "redacted_metadata_receipt_finalized",
        "provider_metadata_imported",
        "provider_metadata_read_attempted",
        "provider_metadata_read",
        "provider_object_listing_configured",
        "provider_object_list_attempted",
        "provider_objects_listed",
        "catalog_entries_created",
        "provider_object_metadata_imported",
        "object_id_collected",
        "object_key_collected",
        "object_etag_collected",
        "object_size_collected",
        "object_last_modified_collected",
        "object_body_read",
        "object_body_view_enabled",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
        "vault_done",
    ]
    for field in locked_false_fields:
        assert contract[field] is False

    assert contract["contract_data"]["safe_to_continue_to_gp073"] is True
    assert contract["contract_data"]["next_pack"] == "VAULT_GP073_REAL_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_CONTRACT"

def test_gp072_requirements_are_real_template_only_and_locked(gp072_db):
    payload = get_storage_provider_redacted_metadata_receipt_requirements(gp072_db)

    assert payload["requirement_count"] == EXPECTED_REQUIREMENTS
    assert payload["source_pack_count"] == EXPECTED_SOURCE_PACKS
    assert payload["requirement_code_count"] == len(REDACTED_METADATA_REQUIREMENT_SPECS)
    assert payload["requirement_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["requirement_verified_count"] == 0
    assert payload["receipt_locked_count"] == EXPECTED_REQUIREMENTS
    assert payload["template_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["metadata_redaction_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["tower_review_granted_count"] == 0

    assert payload["redacted_metadata_receipt_created_count"] == 0
    assert payload["redacted_metadata_receipt_finalized_count"] == 0
    assert payload["provider_metadata_imported_count"] == 0
    assert payload["provider_metadata_read_count"] == 0
    assert payload["provider_object_listing_configured_count"] == 0
    assert payload["provider_object_list_attempted_count"] == 0
    assert payload["provider_objects_listed_count"] == 0
    assert payload["provider_object_metadata_imported_count"] == 0
    assert payload["object_id_collected_count"] == 0
    assert payload["object_key_collected_count"] == 0
    assert payload["object_etag_collected_count"] == 0
    assert payload["object_size_collected_count"] == 0
    assert payload["object_last_modified_collected_count"] == 0
    assert payload["object_body_read_count"] == 0
    assert payload["object_body_view_enabled_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    for item in payload["requirements"]:
        assert item["redacted_metadata_requirement_id"].startswith("VSPRMRR-")
        assert item["redacted_metadata_receipt_contract_id"] == DEFAULT_REDACTED_METADATA_RECEIPT_CONTRACT_ID
        assert item["source_pack_id"].startswith("VAULT_GP")
        assert item["receipt_locked"] is True
        assert item["template_only"] is True
        assert item["metadata_redaction_required"] is True
        assert item["redacted_metadata_receipt_created"] is False
        assert item["provider_metadata_imported"] is False
        assert item["object_id_collected"] is False
        assert item["object_key_collected"] is False
        assert item["object_body_read"] is False
        assert item["direct_upload_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp072_policies_are_real_template_only_and_locked(gp072_db):
    payload = get_storage_provider_redacted_metadata_receipt_policies(gp072_db)

    assert payload["policy_count"] == EXPECTED_POLICIES
    assert payload["policy_code_count"] == EXPECTED_POLICIES
    assert payload["policy_required_count"] == EXPECTED_POLICIES
    assert payload["policy_verified_count"] == 0
    assert payload["tower_review_granted_count"] == 0

    assert payload["redacted_metadata_receipt_created_count"] == 0
    assert payload["redacted_metadata_receipt_finalized_count"] == 0
    assert payload["provider_metadata_imported_count"] == 0
    assert payload["provider_metadata_read_count"] == 0
    assert payload["provider_object_listing_configured_count"] == 0
    assert payload["provider_object_list_attempted_count"] == 0
    assert payload["provider_objects_listed_count"] == 0
    assert payload["provider_object_metadata_imported_count"] == 0
    assert payload["object_id_collected_count"] == 0
    assert payload["object_key_collected_count"] == 0
    assert payload["object_etag_collected_count"] == 0
    assert payload["object_size_collected_count"] == 0
    assert payload["object_last_modified_collected_count"] == 0
    assert payload["object_body_read_count"] == 0
    assert payload["object_body_view_enabled_count"] == 0
    assert payload["object_body_content_exposed_count"] == 0
    assert payload["object_body_plaintext_visible_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    for item in payload["policies"]:
        assert item["redacted_metadata_policy_id"].startswith("VSPRMRP-")
        assert item["redacted_metadata_receipt_contract_id"] == DEFAULT_REDACTED_METADATA_RECEIPT_CONTRACT_ID
        assert item["redacted_metadata_receipt_created"] is False
        assert item["provider_metadata_imported"] is False
        assert item["provider_objects_listed"] is False
        assert item["object_id_collected"] is False
        assert item["object_key_collected"] is False
        assert item["object_body_read"] is False
        assert item["direct_upload_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp072_blockers_are_real_and_carried_from_gp071(gp072_db):
    payload = get_storage_provider_redacted_metadata_receipt_blockers(gp072_db)

    assert payload["blocker_count"] == EXPECTED_BLOCKERS
    assert payload["blocker_active_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_redacted_metadata_receipt_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_metadata_import_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_listing_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_identifier_collection_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_body_view_count"] == EXPECTED_BLOCKERS
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
        assert item["redacted_metadata_blocker_id"].startswith("VSPRM-BLOCK-")
        assert item["redacted_metadata_receipt_contract_id"] == DEFAULT_REDACTED_METADATA_RECEIPT_CONTRACT_ID
        assert item["source_object_catalog_blocker_id"].startswith("VSPOCLB-")
        assert item["blocker_active"] is True
        assert item["blocks_redacted_metadata_receipt"] is True
        assert item["blocks_provider_metadata_import"] is True
        assert item["blocks_provider_listing"] is True
        assert item["blocks_object_identifier_collection"] is True
        assert item["blocks_object_body_view"] is True
        assert item["blocks_direct_upload"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["resolved"] is False

def test_gp072_event_log_and_manual_event_write_do_not_unlock(gp072_db):
    events = get_storage_provider_redacted_metadata_receipt_events(gp072_db)
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_REDACTED_METADATA_RECEIPT_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP071_OBJECT_CATALOG_LOCK_CONTRACT_ATTACHED" in event_types
    assert "REAL_REDACTED_METADATA_REQUIREMENTS_CREATED_TEMPLATE_ONLY" in event_types
    assert "REAL_REDACTED_METADATA_POLICIES_CREATED_TEMPLATE_ONLY" in event_types
    assert "REAL_REDACTED_METADATA_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "REDACTED_METADATA_RECEIPT_LOCKS_CONFIRMED" in event_types

    before = events["event_count"]
    written = record_storage_provider_redacted_metadata_receipt_event(
        "OWNER_GP072_REDACTED_METADATA_RECEIPT_REVIEWED",
        {"reviewer": "owner"},
        gp072_db,
    )
    after = get_storage_provider_redacted_metadata_receipt_events(gp072_db)

    assert after["event_count"] == before + 1
    assert written["event_written"] is True
    assert written["redacted_metadata_receipt_locked"] is True
    assert written["receipt_template_only"] is True
    assert written["redacted_metadata_receipt_created"] is False
    assert written["provider_metadata_imported"] is False
    assert written["provider_metadata_read"] is False
    assert written["provider_objects_listed"] is False
    assert written["object_id_collected"] is False
    assert written["object_key_collected"] is False
    assert written["object_body_read"] is False
    assert written["object_body_view_enabled"] is False
    assert written["direct_upload_enabled"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

def test_gp072_validation_home_status_and_next_step(gp072_db):
    validation = validate_storage_provider_redacted_metadata_receipt_contract(gp072_db)

    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp073"] is True
    assert validation["vault_done"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_REDACTED_METADATA_RECEIPT_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP071_OBJECT_CATALOG_LOCK_CONTRACT_ATTACHED" in codes
    assert "REDACTED_METADATA_RECEIPT_CONTRACT_READY" in codes
    assert "REDACTED_METADATA_RECEIPT_LOCKED" in codes
    assert "RECEIPT_TEMPLATE_ONLY" in codes
    assert "REAL_REDACTED_METADATA_REQUIREMENTS_EXIST" in codes
    assert "REAL_REDACTED_METADATA_POLICIES_EXIST" in codes
    assert "REAL_REDACTED_METADATA_BLOCKERS_CARRIED_FORWARD" in codes
    assert "NO_CONTRACT_REDACTED_METADATA_RECEIPT_CREATED" in codes
    assert "NO_CONTRACT_PROVIDER_METADATA_IMPORTED" in codes
    assert "NO_CONTRACT_OBJECT_ID_COLLECTED" in codes
    assert "NO_CONTRACT_OBJECT_KEY_COLLECTED" in codes
    assert "NO_CONTRACT_OBJECT_BODY_READ" in codes
    assert "NO_CONTRACT_DIRECT_UPLOAD_ENABLED" in codes
    assert "NO_CONTRACT_EXPORT_ENABLED" in codes
    assert "NO_CONTRACT_EXECUTION_ENABLED" in codes
    assert "NO_CONTRACT_VAULT_DONE" in codes

    home = get_real_storage_provider_redacted_metadata_receipt_contract_home(gp072_db)
    truth = home["redacted_metadata_receipt_truth"]
    assert truth["real_storage_provider_redacted_metadata_receipt_contract_ready"] is True
    assert truth["validation_passed"] is True
    assert truth["redacted_metadata_receipt_locked"] is True
    assert truth["receipt_template_only"] is True
    assert truth["requirement_count"] == EXPECTED_REQUIREMENTS
    assert truth["policy_count"] == EXPECTED_POLICIES
    assert truth["blocker_count"] == EXPECTED_BLOCKERS
    assert truth["redacted_metadata_receipt_created"] is False
    assert truth["provider_metadata_imported"] is False
    assert truth["provider_metadata_read"] is False
    assert truth["provider_objects_listed"] is False
    assert truth["object_id_collected"] is False
    assert truth["object_key_collected"] is False
    assert truth["object_body_read"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["export_enabled"] is False
    assert truth["execution_enabled"] is False
    assert truth["vault_done"] is False

    status = get_gp072_status(gp072_db)
    gp072 = status["gp072_status"]
    assert gp072["ready"] is True
    assert gp072["validation_passed"] is True
    assert gp072["safe_to_continue_to_gp073"] is True
    assert gp072["source_pack_count"] == EXPECTED_SOURCE_PACKS
    assert gp072["requirement_code_count"] == len(REDACTED_METADATA_REQUIREMENT_SPECS)
    assert gp072["policy_code_count"] == EXPECTED_POLICIES
    assert gp072["blocker_count"] == EXPECTED_BLOCKERS
    assert gp072["redacted_metadata_receipt_created_count"] == 0
    assert gp072["provider_metadata_imported_count"] == 0
    assert gp072["provider_metadata_read_count"] == 0
    assert gp072["provider_objects_listed_count"] == 0
    assert gp072["object_id_collected_count"] == 0
    assert gp072["object_key_collected_count"] == 0
    assert gp072["object_etag_collected_count"] == 0
    assert gp072["object_size_collected_count"] == 0
    assert gp072["object_last_modified_collected_count"] == 0
    assert gp072["object_body_read_count"] == 0
    assert gp072["direct_upload_enabled_count"] == 0
    assert gp072["export_enabled_count"] == 0
    assert gp072["execution_enabled_count"] == 0
    assert gp072["vault_done"] is False
    assert gp072["clouds_status"] == "parked_do_not_continue_from_vault_gp072"
    assert gp072["next_pack"] == "VAULT_GP073_REAL_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_CONTRACT"

    next_step = get_storage_provider_redacted_metadata_receipt_next_step()["next_step"]
    assert next_step["current_section_range"] == "GP071-GP080"
    assert next_step["next_pack"] == "VAULT_GP073_REAL_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_CONTRACT"
    assert next_step["safe_to_continue_to_gp073"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp072_html_is_dark_and_mentions_redacted_metadata_receipt(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_storage_provider_redacted_metadata_receipt_contract_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Redacted Metadata Receipt Contract" in html
    assert "Real Provider Receipt and Redacted Access Layer" in html
    assert "GP072" in html
    assert "Receipt contract ready" in html
    assert "Template-only" in html
    assert "No metadata import" in html
    assert "No identifiers" in html
    assert "No body read" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-redacted-metadata-receipt-contract.json" in html
    assert "/vault/gp072-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp072_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-storage-provider-redacted-metadata-receipt-contract",
        "/vault/real-storage-provider-redacted-metadata-receipt-contract.json",
        "/vault/storage-provider-redacted-metadata-receipt-contract-record.json",
        "/vault/storage-provider-redacted-metadata-receipt-requirements.json",
        "/vault/storage-provider-redacted-metadata-receipt-policies.json",
        "/vault/storage-provider-redacted-metadata-receipt-blockers.json",
        "/vault/storage-provider-redacted-metadata-receipt-events.json",
        "/vault/storage-provider-redacted-metadata-receipt-validation.json",
        "/vault/storage-provider-redacted-metadata-receipt-next-step.json",
        "/vault/gp072-status.json",
    ]
    for route in required_routes:
        assert route in text

def test_gp072_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()
    routes = [
        "/vault/real-storage-provider-redacted-metadata-receipt-contract",
        "/vault/real-storage-provider-redacted-metadata-receipt-contract.json",
        "/vault/storage-provider-redacted-metadata-receipt-contract-record.json",
        "/vault/storage-provider-redacted-metadata-receipt-requirements.json",
        "/vault/storage-provider-redacted-metadata-receipt-policies.json",
        "/vault/storage-provider-redacted-metadata-receipt-blockers.json",
        "/vault/storage-provider-redacted-metadata-receipt-events.json",
        "/vault/storage-provider-redacted-metadata-receipt-validation.json",
        "/vault/storage-provider-redacted-metadata-receipt-next-step.json",
        "/vault/gp072-status.json",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Real Storage Provider Redacted Metadata Receipt Contract" in response.data
