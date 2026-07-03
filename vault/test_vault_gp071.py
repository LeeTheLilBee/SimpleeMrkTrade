"""
Tests for VAULT GP071 — Real Storage Provider Object Catalog Lock Contract
"""

from pathlib import Path
import pytest

from vault.real_storage_provider_object_catalog_lock_contract_service import (
    CATALOG_POLICIES,
    CATALOG_REQUIREMENT_SPECS,
    DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,
    ensure_storage_provider_object_catalog_lock_contract_schema,
    get_gp071_status,
    get_real_storage_provider_object_catalog_lock_contract_home,
    get_storage_provider_object_catalog_blockers,
    get_storage_provider_object_catalog_events,
    get_storage_provider_object_catalog_lock_contract_record,
    get_storage_provider_object_catalog_next_step,
    get_storage_provider_object_catalog_policies,
    get_storage_provider_object_catalog_requirements,
    initialize_real_storage_provider_object_catalog_lock_contract,
    record_storage_provider_object_catalog_event,
    render_real_storage_provider_object_catalog_lock_contract_page,
    validate_storage_provider_object_catalog_lock_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_PACKS = 9
EXPECTED_REQUIREMENTS = EXPECTED_SOURCE_PACKS * len(CATALOG_REQUIREMENT_SPECS)
EXPECTED_POLICIES = len(CATALOG_POLICIES)
EXPECTED_BLOCKERS = 14

@pytest.fixture()
def gp071_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "object_catalog_lock_contract.sqlite")

def test_gp071_schema_is_real_sqlite_backed(gp071_db):
    result = ensure_storage_provider_object_catalog_lock_contract_schema(gp071_db)

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert Path(result["db_path"]).exists()
    assert "vault_storage_provider_object_catalog_lock_contracts" in result["tables"]
    assert "vault_storage_provider_object_catalog_requirements" in result["tables"]
    assert "vault_storage_provider_object_catalog_policies" in result["tables"]
    assert "vault_storage_provider_object_catalog_blockers" in result["tables"]
    assert "vault_storage_provider_object_catalog_events" in result["tables"]

def test_gp071_initialize_creates_real_contract_requirements_policies_blockers_events(gp071_db):
    result = initialize_real_storage_provider_object_catalog_lock_contract(gp071_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["contract_count"] == 1
    assert result["requirement_count"] == EXPECTED_REQUIREMENTS
    assert result["policy_count"] == EXPECTED_POLICIES
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_object_catalog_lock_contract(gp071_db)
    assert second["contract_count"] == 1
    assert second["requirement_count"] == EXPECTED_REQUIREMENTS
    assert second["policy_count"] == EXPECTED_POLICIES
    assert second["blocker_count"] == EXPECTED_BLOCKERS

def test_gp071_contract_sourced_from_gp070_and_locked(gp071_db):
    contract = get_storage_provider_object_catalog_lock_contract_record(gp071_db)["object_catalog_lock_contract"]

    assert contract["object_catalog_lock_contract_id"] == DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP071"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
    assert contract["section_range"] == "GP071-GP080"
    assert contract["previous_section_id"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert contract["previous_section_range"] == "GP061-GP070"
    assert contract["source_configuration_readiness_checkpoint_id"] == "VSPCRC-GP070-001"
    assert contract["source_configuration_pack_id"] == "VAULT_GP070"
    assert contract["contract_status"] == "REAL_OBJECT_CATALOG_LOCK_CONTRACT_OPEN_TOWER_LOCKED"

    assert contract["object_catalog_lock_contract_ready"] is True
    assert contract["object_catalog_requirements_ready"] is True
    assert contract["object_catalog_policies_ready"] is True
    assert contract["object_catalog_blockers_ready"] is True
    assert contract["object_catalog_validation_ready"] is True
    assert contract["object_catalog_locked"] is True
    assert contract["catalog_metadata_only"] is True
    assert contract["catalog_redacted_access_only"] is True
    assert contract["source_configuration_checkpoint_attached"] is True
    assert contract["safe_to_continue_to_gp072"] is True

    assert contract["object_catalog_configured"] is False
    assert contract["object_catalog_attempted"] is False
    assert contract["object_catalog_enabled"] is False
    assert contract["provider_object_listing_configured"] is False
    assert contract["provider_object_list_attempted"] is False
    assert contract["provider_objects_listed"] is False
    assert contract["catalog_entries_created"] is False
    assert contract["provider_object_metadata_imported"] is False
    assert contract["object_id_collected"] is False
    assert contract["object_key_collected"] is False
    assert contract["object_etag_collected"] is False
    assert contract["object_size_collected"] is False
    assert contract["object_last_modified_collected"] is False
    assert contract["object_body_read"] is False
    assert contract["object_body_view_enabled"] is False
    assert contract["direct_upload_enabled"] is False
    assert contract["export_enabled"] is False
    assert contract["execution_enabled"] is False
    assert contract["vault_done"] is False

    assert contract["contract_data"]["safe_to_continue_to_gp072"] is True
    assert contract["contract_data"]["next_pack"] == "VAULT_GP072_REAL_STORAGE_PROVIDER_REDACTED_METADATA_RECEIPT_CONTRACT"

def test_gp071_requirements_are_real_and_locked(gp071_db):
    payload = get_storage_provider_object_catalog_requirements(gp071_db)

    assert payload["requirement_count"] == EXPECTED_REQUIREMENTS
    assert payload["source_pack_count"] == EXPECTED_SOURCE_PACKS
    assert payload["requirement_code_count"] == len(CATALOG_REQUIREMENT_SPECS)
    assert payload["requirement_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["requirement_verified_count"] == 0
    assert payload["catalog_locked_count"] == EXPECTED_REQUIREMENTS
    assert payload["metadata_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["redacted_access_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["tower_review_granted_count"] == 0

    assert payload["object_catalog_configured_count"] == 0
    assert payload["object_catalog_attempted_count"] == 0
    assert payload["object_catalog_enabled_count"] == 0
    assert payload["provider_object_listing_configured_count"] == 0
    assert payload["provider_object_list_attempted_count"] == 0
    assert payload["provider_objects_listed_count"] == 0
    assert payload["catalog_entries_created_count"] == 0
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
        assert item["object_catalog_requirement_id"].startswith("VSPOCLR-")
        assert item["object_catalog_lock_contract_id"] == DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID
        assert item["source_pack_id"].startswith("VAULT_GP")
        assert item["catalog_locked"] is True
        assert item["metadata_only"] is True
        assert item["redacted_access_only"] is True
        assert item["object_catalog_configured"] is False
        assert item["provider_objects_listed"] is False
        assert item["provider_object_metadata_imported"] is False
        assert item["object_body_read"] is False
        assert item["direct_upload_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp071_policies_are_real_and_locked(gp071_db):
    payload = get_storage_provider_object_catalog_policies(gp071_db)

    assert payload["policy_count"] == EXPECTED_POLICIES
    assert payload["policy_code_count"] == EXPECTED_POLICIES
    assert payload["policy_required_count"] == EXPECTED_POLICIES
    assert payload["policy_verified_count"] == 0
    assert payload["tower_review_granted_count"] == 0

    assert payload["object_catalog_configured_count"] == 0
    assert payload["object_catalog_attempted_count"] == 0
    assert payload["object_catalog_enabled_count"] == 0
    assert payload["provider_object_listing_configured_count"] == 0
    assert payload["provider_object_list_attempted_count"] == 0
    assert payload["provider_objects_listed_count"] == 0
    assert payload["catalog_entries_created_count"] == 0
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
        assert item["object_catalog_policy_id"].startswith("VSPOCLP-")
        assert item["object_catalog_lock_contract_id"] == DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID
        assert item["object_catalog_configured"] is False
        assert item["provider_object_list_attempted"] is False
        assert item["provider_objects_listed"] is False
        assert item["provider_object_metadata_imported"] is False
        assert item["object_body_read"] is False
        assert item["object_body_content_exposed"] is False
        assert item["direct_upload_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp071_blockers_are_real_and_carried_from_gp070(gp071_db):
    payload = get_storage_provider_object_catalog_blockers(gp071_db)

    assert payload["blocker_count"] == EXPECTED_BLOCKERS
    assert payload["blocker_active_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_catalog_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_listing_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_metadata_import_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_body_view_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_read_write_count"] == EXPECTED_BLOCKERS
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
        assert item["object_catalog_blocker_id"].startswith("VSPOCLB-")
        assert item["object_catalog_lock_contract_id"] == DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID
        assert item["source_configuration_blocker_id"].startswith("VSPCRC-BLOCK-")
        assert item["blocker_active"] is True
        assert item["blocks_object_catalog"] is True
        assert item["blocks_provider_listing"] is True
        assert item["blocks_metadata_import"] is True
        assert item["blocks_object_body_view"] is True
        assert item["blocks_direct_upload"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["resolved"] is False

def test_gp071_event_log_and_manual_event_write_do_not_unlock(gp071_db):
    events = get_storage_provider_object_catalog_events(gp071_db)
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP070_CONFIGURATION_READINESS_CHECKPOINT_ATTACHED" in event_types
    assert "REAL_OBJECT_CATALOG_REQUIREMENTS_CREATED_LOCKED" in event_types
    assert "REAL_OBJECT_CATALOG_POLICIES_CREATED_LOCKED" in event_types
    assert "REAL_OBJECT_CATALOG_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "OBJECT_CATALOG_LOCKS_CONFIRMED" in event_types

    before = events["event_count"]
    written = record_storage_provider_object_catalog_event(
        "OWNER_GP071_OBJECT_CATALOG_LOCK_REVIEWED",
        {"reviewer": "owner"},
        gp071_db,
    )
    after = get_storage_provider_object_catalog_events(gp071_db)

    assert after["event_count"] == before + 1
    assert written["event_written"] is True
    assert written["object_catalog_locked"] is True
    assert written["object_catalog_configured"] is False
    assert written["provider_object_list_attempted"] is False
    assert written["provider_objects_listed"] is False
    assert written["catalog_entries_created"] is False
    assert written["provider_object_metadata_imported"] is False
    assert written["object_body_read"] is False
    assert written["object_body_view_enabled"] is False
    assert written["direct_upload_enabled"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

def test_gp071_validation_home_status_and_next_step(gp071_db):
    validation = validate_storage_provider_object_catalog_lock_contract(gp071_db)

    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp072"] is True
    assert validation["vault_done"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_OBJECT_CATALOG_LOCK_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP070_CONFIGURATION_READINESS_CHECKPOINT_ATTACHED" in codes
    assert "OBJECT_CATALOG_LOCK_CONTRACT_READY" in codes
    assert "OBJECT_CATALOG_LOCKED" in codes
    assert "REAL_OBJECT_CATALOG_REQUIREMENTS_EXIST" in codes
    assert "REAL_OBJECT_CATALOG_POLICIES_EXIST" in codes
    assert "REAL_OBJECT_CATALOG_BLOCKERS_CARRIED_FORWARD" in codes
    assert "NO_CONTRACT_PROVIDER_OBJECTS_LISTED" in codes
    assert "NO_CONTRACT_CATALOG_ENTRIES_CREATED" in codes
    assert "NO_CONTRACT_PROVIDER_OBJECT_METADATA_IMPORTED" in codes
    assert "NO_CONTRACT_OBJECT_BODY_READ" in codes
    assert "NO_CONTRACT_DIRECT_UPLOAD_ENABLED" in codes
    assert "NO_CONTRACT_EXPORT_ENABLED" in codes
    assert "NO_CONTRACT_EXECUTION_ENABLED" in codes
    assert "NO_CONTRACT_VAULT_DONE" in codes

    home = get_real_storage_provider_object_catalog_lock_contract_home(gp071_db)
    truth = home["object_catalog_truth"]
    assert truth["real_storage_provider_object_catalog_lock_contract_ready"] is True
    assert truth["validation_passed"] is True
    assert truth["object_catalog_locked"] is True
    assert truth["requirement_count"] == EXPECTED_REQUIREMENTS
    assert truth["policy_count"] == EXPECTED_POLICIES
    assert truth["blocker_count"] == EXPECTED_BLOCKERS
    assert truth["provider_objects_listed"] is False
    assert truth["provider_object_metadata_imported"] is False
    assert truth["object_body_read"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["export_enabled"] is False
    assert truth["execution_enabled"] is False
    assert truth["vault_done"] is False

    status = get_gp071_status(gp071_db)
    gp071 = status["gp071_status"]
    assert gp071["ready"] is True
    assert gp071["validation_passed"] is True
    assert gp071["safe_to_continue_to_gp072"] is True
    assert gp071["source_pack_count"] == EXPECTED_SOURCE_PACKS
    assert gp071["requirement_code_count"] == len(CATALOG_REQUIREMENT_SPECS)
    assert gp071["policy_code_count"] == EXPECTED_POLICIES
    assert gp071["blocker_count"] == EXPECTED_BLOCKERS
    assert gp071["provider_object_listing_configured_count"] == 0
    assert gp071["provider_object_list_attempted_count"] == 0
    assert gp071["provider_objects_listed_count"] == 0
    assert gp071["catalog_entries_created_count"] == 0
    assert gp071["provider_object_metadata_imported_count"] == 0
    assert gp071["object_body_read_count"] == 0
    assert gp071["direct_upload_enabled_count"] == 0
    assert gp071["export_enabled_count"] == 0
    assert gp071["execution_enabled_count"] == 0
    assert gp071["vault_done"] is False
    assert gp071["clouds_status"] == "parked_do_not_continue_from_vault_gp071"
    assert gp071["next_pack"] == "VAULT_GP072_REAL_STORAGE_PROVIDER_REDACTED_METADATA_RECEIPT_CONTRACT"

    next_step = get_storage_provider_object_catalog_next_step()["next_step"]
    assert next_step["current_section_range"] == "GP071-GP080"
    assert next_step["next_pack"] == "VAULT_GP072_REAL_STORAGE_PROVIDER_REDACTED_METADATA_RECEIPT_CONTRACT"
    assert next_step["safe_to_continue_to_gp072"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp071_html_is_dark_and_mentions_object_catalog_lock(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_storage_provider_object_catalog_lock_contract_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Object Catalog Lock Contract" in html
    assert "Real Provider Receipt and Redacted Access Layer" in html
    assert "GP071" in html
    assert "Object catalog lock ready" in html
    assert "No provider listing" in html
    assert "No metadata import" in html
    assert "No body read" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-object-catalog-lock-contract.json" in html
    assert "/vault/gp071-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp071_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-storage-provider-object-catalog-lock-contract",
        "/vault/real-storage-provider-object-catalog-lock-contract.json",
        "/vault/storage-provider-object-catalog-lock-contract-record.json",
        "/vault/storage-provider-object-catalog-requirements.json",
        "/vault/storage-provider-object-catalog-policies.json",
        "/vault/storage-provider-object-catalog-blockers.json",
        "/vault/storage-provider-object-catalog-events.json",
        "/vault/storage-provider-object-catalog-validation.json",
        "/vault/storage-provider-object-catalog-next-step.json",
        "/vault/gp071-status.json",
    ]
    for route in required_routes:
        assert route in text

def test_gp071_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()
    routes = [
        "/vault/real-storage-provider-object-catalog-lock-contract",
        "/vault/real-storage-provider-object-catalog-lock-contract.json",
        "/vault/storage-provider-object-catalog-lock-contract-record.json",
        "/vault/storage-provider-object-catalog-requirements.json",
        "/vault/storage-provider-object-catalog-policies.json",
        "/vault/storage-provider-object-catalog-blockers.json",
        "/vault/storage-provider-object-catalog-events.json",
        "/vault/storage-provider-object-catalog-validation.json",
        "/vault/storage-provider-object-catalog-next-step.json",
        "/vault/gp071-status.json",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Real Storage Provider Object Catalog Lock Contract" in response.data
