"""
Tests for VAULT GP074 — Real Storage Provider Redacted Access View Lock Contract
"""

from pathlib import Path
import pytest

from vault.real_storage_provider_redacted_access_view_lock_contract_service import (
    DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,
    VIEW_POLICIES,
    VIEW_REQUIREMENT_SPECS,
    ensure_storage_provider_redacted_access_view_lock_contract_schema,
    get_gp074_status,
    get_real_storage_provider_redacted_access_view_lock_contract_home,
    get_storage_provider_redacted_access_view_blockers,
    get_storage_provider_redacted_access_view_events,
    get_storage_provider_redacted_access_view_lock_contract_record,
    get_storage_provider_redacted_access_view_next_step,
    get_storage_provider_redacted_access_view_policies,
    get_storage_provider_redacted_access_view_requirements,
    initialize_real_storage_provider_redacted_access_view_lock_contract,
    record_storage_provider_redacted_access_view_event,
    render_real_storage_provider_redacted_access_view_lock_contract_page,
    validate_storage_provider_redacted_access_view_lock_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_REQUIREMENTS = 63
EXPECTED_REQUIREMENTS = EXPECTED_SOURCE_REQUIREMENTS * len(VIEW_REQUIREMENT_SPECS)
EXPECTED_POLICIES = len(VIEW_POLICIES)
EXPECTED_BLOCKERS = 14

@pytest.fixture()
def gp074_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "redacted_access_view_lock_contract.sqlite")

def test_gp074_schema_is_real_sqlite_backed(gp074_db):
    result = ensure_storage_provider_redacted_access_view_lock_contract_schema(gp074_db)

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert Path(result["db_path"]).exists()
    assert "vault_storage_provider_redacted_access_view_lock_contracts" in result["tables"]
    assert "vault_storage_provider_redacted_access_view_requirements" in result["tables"]
    assert "vault_storage_provider_redacted_access_view_policies" in result["tables"]
    assert "vault_storage_provider_redacted_access_view_blockers" in result["tables"]
    assert "vault_storage_provider_redacted_access_view_events" in result["tables"]

def test_gp074_initialize_creates_real_contract_requirements_policies_blockers_events(gp074_db):
    result = initialize_real_storage_provider_redacted_access_view_lock_contract(gp074_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["contract_count"] == 1
    assert result["requirement_count"] == EXPECTED_REQUIREMENTS
    assert result["policy_count"] == EXPECTED_POLICIES
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_redacted_access_view_lock_contract(gp074_db)
    assert second["contract_count"] == 1
    assert second["requirement_count"] == EXPECTED_REQUIREMENTS
    assert second["policy_count"] == EXPECTED_POLICIES
    assert second["blocker_count"] == EXPECTED_BLOCKERS

def test_gp074_contract_sourced_from_gp073_and_locked(gp074_db):
    contract = get_storage_provider_redacted_access_view_lock_contract_record(gp074_db)["redacted_access_view_lock_contract"]

    assert contract["redacted_access_view_lock_contract_id"] == DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP074"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
    assert contract["section_range"] == "GP071-GP080"
    assert contract["source_receipt_lineage_lock_contract_id"] == "VSPRLLC-GP073-001"
    assert contract["source_receipt_lineage_pack_id"] == "VAULT_GP073"
    assert contract["contract_status"] == "REAL_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_OPEN_TEMPLATE_ONLY_TOWER_LOCKED"

    assert contract["redacted_access_view_lock_contract_ready"] is True
    assert contract["redacted_access_view_requirements_ready"] is True
    assert contract["redacted_access_view_policies_ready"] is True
    assert contract["redacted_access_view_blockers_ready"] is True
    assert contract["redacted_access_view_validation_ready"] is True
    assert contract["redacted_access_view_locked"] is True
    assert contract["view_template_only"] is True
    assert contract["view_redaction_required"] is True
    assert contract["source_receipt_lineage_lock_contract_attached"] is True
    assert contract["safe_to_continue_to_gp075"] is True

    locked_false_fields = [
        "redacted_access_view_configured",
        "redacted_access_view_attempted",
        "redacted_access_view_enabled",
        "redacted_access_view_rendered",
        "redacted_access_view_published",
        "live_provider_access_view_created",
        "provider_object_view_created",
        "provider_metadata_view_created",
        "provider_receipt_lineage_view_created",
        "object_identifier_displayed",
        "object_key_displayed",
        "object_etag_displayed",
        "object_size_displayed",
        "object_timestamp_displayed",
        "object_body_displayed",
        "plaintext_view_enabled",
        "view_download_enabled",
        "provider_metadata_imported",
        "provider_metadata_read",
        "provider_objects_listed",
        "object_id_collected",
        "object_key_collected",
        "object_body_read",
        "object_body_view_enabled",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
        "vault_done",
    ]
    for field in locked_false_fields:
        assert contract[field] is False

    assert contract["contract_data"]["safe_to_continue_to_gp075"] is True
    assert contract["contract_data"]["next_pack"] == "VAULT_GP075_REAL_STORAGE_PROVIDER_OWNER_REVIEW_PACKET_LOCK_CONTRACT"

def test_gp074_requirements_are_real_template_only_and_locked(gp074_db):
    payload = get_storage_provider_redacted_access_view_requirements(gp074_db)

    assert payload["requirement_count"] == EXPECTED_REQUIREMENTS
    assert payload["source_requirement_count"] == EXPECTED_SOURCE_REQUIREMENTS
    assert payload["requirement_code_count"] == len(VIEW_REQUIREMENT_SPECS)
    assert payload["requirement_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["requirement_verified_count"] == 0
    assert payload["view_locked_count"] == EXPECTED_REQUIREMENTS
    assert payload["template_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["view_redaction_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["tower_review_granted_count"] == 0

    assert payload["redacted_access_view_rendered_count"] == 0
    assert payload["redacted_access_view_published_count"] == 0
    assert payload["live_provider_access_view_created_count"] == 0
    assert payload["provider_object_view_created_count"] == 0
    assert payload["provider_metadata_view_created_count"] == 0
    assert payload["provider_receipt_lineage_view_created_count"] == 0
    assert payload["object_identifier_displayed_count"] == 0
    assert payload["object_key_displayed_count"] == 0
    assert payload["object_etag_displayed_count"] == 0
    assert payload["object_size_displayed_count"] == 0
    assert payload["object_timestamp_displayed_count"] == 0
    assert payload["object_body_displayed_count"] == 0
    assert payload["plaintext_view_enabled_count"] == 0
    assert payload["view_download_enabled_count"] == 0
    assert payload["object_body_read_count"] == 0
    assert payload["object_body_view_enabled_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    for item in payload["requirements"]:
        assert item["redacted_access_view_requirement_id"].startswith("VSPRAVR-")
        assert item["redacted_access_view_lock_contract_id"] == DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID
        assert item["source_requirement_id"].startswith("VSPRLLR-")
        assert item["view_locked"] is True
        assert item["template_only"] is True
        assert item["view_redaction_required"] is True
        assert item["redacted_access_view_rendered"] is False
        assert item["live_provider_access_view_created"] is False
        assert item["provider_metadata_view_created"] is False
        assert item["object_identifier_displayed"] is False
        assert item["object_body_displayed"] is False
        assert item["direct_upload_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp074_policies_are_real_template_only_and_locked(gp074_db):
    payload = get_storage_provider_redacted_access_view_policies(gp074_db)

    assert payload["policy_count"] == EXPECTED_POLICIES
    assert payload["policy_code_count"] == EXPECTED_POLICIES
    assert payload["policy_required_count"] == EXPECTED_POLICIES
    assert payload["policy_verified_count"] == 0
    assert payload["tower_review_granted_count"] == 0

    assert payload["redacted_access_view_rendered_count"] == 0
    assert payload["redacted_access_view_published_count"] == 0
    assert payload["live_provider_access_view_created_count"] == 0
    assert payload["provider_object_view_created_count"] == 0
    assert payload["provider_metadata_view_created_count"] == 0
    assert payload["provider_receipt_lineage_view_created_count"] == 0
    assert payload["object_identifier_displayed_count"] == 0
    assert payload["object_key_displayed_count"] == 0
    assert payload["object_etag_displayed_count"] == 0
    assert payload["object_size_displayed_count"] == 0
    assert payload["object_timestamp_displayed_count"] == 0
    assert payload["object_body_displayed_count"] == 0
    assert payload["plaintext_view_enabled_count"] == 0
    assert payload["view_download_enabled_count"] == 0
    assert payload["object_body_content_exposed_count"] == 0
    assert payload["object_body_plaintext_visible_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    for item in payload["policies"]:
        assert item["redacted_access_view_policy_id"].startswith("VSPRAVP-")
        assert item["redacted_access_view_lock_contract_id"] == DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID
        assert item["redacted_access_view_rendered"] is False
        assert item["live_provider_access_view_created"] is False
        assert item["provider_metadata_view_created"] is False
        assert item["object_identifier_displayed"] is False
        assert item["object_body_displayed"] is False
        assert item["plaintext_view_enabled"] is False
        assert item["view_download_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp074_blockers_are_real_and_carried_from_gp073(gp074_db):
    payload = get_storage_provider_redacted_access_view_blockers(gp074_db)

    assert payload["blocker_count"] == EXPECTED_BLOCKERS
    assert payload["blocker_active_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_redacted_access_view_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_live_provider_view_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_metadata_view_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_identifier_display_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_body_display_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_plaintext_view_count"] == EXPECTED_BLOCKERS
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
        assert item["redacted_access_view_blocker_id"].startswith("VSPRAVB-")
        assert item["redacted_access_view_lock_contract_id"] == DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID
        assert item["source_receipt_lineage_blocker_id"].startswith("VSPRLLB-")
        assert item["blocker_active"] is True
        assert item["blocks_redacted_access_view"] is True
        assert item["blocks_live_provider_view"] is True
        assert item["blocks_provider_metadata_view"] is True
        assert item["blocks_object_identifier_display"] is True
        assert item["blocks_object_body_display"] is True
        assert item["blocks_plaintext_view"] is True
        assert item["blocks_direct_upload"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["resolved"] is False

def test_gp074_event_log_and_manual_event_write_do_not_unlock(gp074_db):
    events = get_storage_provider_redacted_access_view_events(gp074_db)
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP073_RECEIPT_LINEAGE_LOCK_CONTRACT_ATTACHED" in event_types
    assert "REAL_REDACTED_ACCESS_VIEW_REQUIREMENTS_CREATED_TEMPLATE_ONLY" in event_types
    assert "REAL_REDACTED_ACCESS_VIEW_POLICIES_CREATED_TEMPLATE_ONLY" in event_types
    assert "REAL_REDACTED_ACCESS_VIEW_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "REDACTED_ACCESS_VIEW_LOCKS_CONFIRMED" in event_types

    before = events["event_count"]
    written = record_storage_provider_redacted_access_view_event(
        "OWNER_GP074_REDACTED_ACCESS_VIEW_REVIEWED",
        {"reviewer": "owner"},
        gp074_db,
    )
    after = get_storage_provider_redacted_access_view_events(gp074_db)

    assert after["event_count"] == before + 1
    assert written["event_written"] is True
    assert written["redacted_access_view_locked"] is True
    assert written["view_template_only"] is True
    assert written["redacted_access_view_rendered"] is False
    assert written["redacted_access_view_published"] is False
    assert written["live_provider_access_view_created"] is False
    assert written["provider_object_view_created"] is False
    assert written["provider_metadata_view_created"] is False
    assert written["provider_receipt_lineage_view_created"] is False
    assert written["object_identifier_displayed"] is False
    assert written["object_key_displayed"] is False
    assert written["object_body_displayed"] is False
    assert written["plaintext_view_enabled"] is False
    assert written["view_download_enabled"] is False
    assert written["object_body_read"] is False
    assert written["object_body_view_enabled"] is False
    assert written["direct_upload_enabled"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

def test_gp074_validation_home_status_and_next_step(gp074_db):
    validation = validate_storage_provider_redacted_access_view_lock_contract(gp074_db)

    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp075"] is True
    assert validation["vault_done"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP073_RECEIPT_LINEAGE_LOCK_CONTRACT_ATTACHED" in codes
    assert "REDACTED_ACCESS_VIEW_LOCK_CONTRACT_READY" in codes
    assert "REDACTED_ACCESS_VIEW_LOCKED" in codes
    assert "VIEW_TEMPLATE_ONLY" in codes
    assert "REAL_REDACTED_ACCESS_VIEW_REQUIREMENTS_EXIST" in codes
    assert "REAL_REDACTED_ACCESS_VIEW_POLICIES_EXIST" in codes
    assert "REAL_REDACTED_ACCESS_VIEW_BLOCKERS_CARRIED_FORWARD" in codes
    assert "NO_CONTRACT_REDACTED_ACCESS_VIEW_RENDERED" in codes
    assert "NO_CONTRACT_LIVE_PROVIDER_ACCESS_VIEW_CREATED" in codes
    assert "NO_CONTRACT_PROVIDER_METADATA_VIEW_CREATED" in codes
    assert "NO_CONTRACT_OBJECT_IDENTIFIER_DISPLAYED" in codes
    assert "NO_CONTRACT_OBJECT_BODY_DISPLAYED" in codes
    assert "NO_CONTRACT_PLAINTEXT_VIEW_ENABLED" in codes
    assert "NO_CONTRACT_DIRECT_UPLOAD_ENABLED" in codes
    assert "NO_CONTRACT_EXPORT_ENABLED" in codes
    assert "NO_CONTRACT_EXECUTION_ENABLED" in codes
    assert "NO_CONTRACT_VAULT_DONE" in codes

    home = get_real_storage_provider_redacted_access_view_lock_contract_home(gp074_db)
    truth = home["redacted_access_view_truth"]
    assert truth["real_storage_provider_redacted_access_view_lock_contract_ready"] is True
    assert truth["validation_passed"] is True
    assert truth["redacted_access_view_locked"] is True
    assert truth["view_template_only"] is True
    assert truth["requirement_count"] == EXPECTED_REQUIREMENTS
    assert truth["policy_count"] == EXPECTED_POLICIES
    assert truth["blocker_count"] == EXPECTED_BLOCKERS
    assert truth["redacted_access_view_rendered"] is False
    assert truth["live_provider_access_view_created"] is False
    assert truth["provider_metadata_view_created"] is False
    assert truth["object_identifier_displayed"] is False
    assert truth["object_key_displayed"] is False
    assert truth["object_body_displayed"] is False
    assert truth["plaintext_view_enabled"] is False
    assert truth["view_download_enabled"] is False
    assert truth["object_body_read"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["export_enabled"] is False
    assert truth["execution_enabled"] is False
    assert truth["vault_done"] is False

    status = get_gp074_status(gp074_db)
    gp074 = status["gp074_status"]
    assert gp074["ready"] is True
    assert gp074["validation_passed"] is True
    assert gp074["safe_to_continue_to_gp075"] is True
    assert gp074["source_requirement_count"] == EXPECTED_SOURCE_REQUIREMENTS
    assert gp074["requirement_code_count"] == len(VIEW_REQUIREMENT_SPECS)
    assert gp074["policy_code_count"] == EXPECTED_POLICIES
    assert gp074["blocker_count"] == EXPECTED_BLOCKERS
    assert gp074["redacted_access_view_rendered_count"] == 0
    assert gp074["redacted_access_view_published_count"] == 0
    assert gp074["live_provider_access_view_created_count"] == 0
    assert gp074["provider_object_view_created_count"] == 0
    assert gp074["provider_metadata_view_created_count"] == 0
    assert gp074["provider_receipt_lineage_view_created_count"] == 0
    assert gp074["object_identifier_displayed_count"] == 0
    assert gp074["object_key_displayed_count"] == 0
    assert gp074["object_body_displayed_count"] == 0
    assert gp074["plaintext_view_enabled_count"] == 0
    assert gp074["view_download_enabled_count"] == 0
    assert gp074["direct_upload_enabled_count"] == 0
    assert gp074["export_enabled_count"] == 0
    assert gp074["execution_enabled_count"] == 0
    assert gp074["vault_done"] is False
    assert gp074["clouds_status"] == "parked_do_not_continue_from_vault_gp074"
    assert gp074["next_pack"] == "VAULT_GP075_REAL_STORAGE_PROVIDER_OWNER_REVIEW_PACKET_LOCK_CONTRACT"

    next_step = get_storage_provider_redacted_access_view_next_step()["next_step"]
    assert next_step["current_section_range"] == "GP071-GP080"
    assert next_step["next_pack"] == "VAULT_GP075_REAL_STORAGE_PROVIDER_OWNER_REVIEW_PACKET_LOCK_CONTRACT"
    assert next_step["safe_to_continue_to_gp075"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp074_html_is_dark_and_mentions_redacted_access_view(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_storage_provider_redacted_access_view_lock_contract_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Redacted Access View Lock Contract" in html
    assert "Real Provider Receipt and Redacted Access Layer" in html
    assert "GP074" in html
    assert "View contract ready" in html
    assert "Template-only" in html
    assert "No live provider view" in html
    assert "No identifiers displayed" in html
    assert "No body display" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-redacted-access-view-lock-contract.json" in html
    assert "/vault/gp074-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp074_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-storage-provider-redacted-access-view-lock-contract",
        "/vault/real-storage-provider-redacted-access-view-lock-contract.json",
        "/vault/storage-provider-redacted-access-view-lock-contract-record.json",
        "/vault/storage-provider-redacted-access-view-requirements.json",
        "/vault/storage-provider-redacted-access-view-policies.json",
        "/vault/storage-provider-redacted-access-view-blockers.json",
        "/vault/storage-provider-redacted-access-view-events.json",
        "/vault/storage-provider-redacted-access-view-validation.json",
        "/vault/storage-provider-redacted-access-view-next-step.json",
        "/vault/gp074-status.json",
    ]
    for route in required_routes:
        assert route in text

def test_gp074_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()
    routes = [
        "/vault/real-storage-provider-redacted-access-view-lock-contract",
        "/vault/real-storage-provider-redacted-access-view-lock-contract.json",
        "/vault/storage-provider-redacted-access-view-lock-contract-record.json",
        "/vault/storage-provider-redacted-access-view-requirements.json",
        "/vault/storage-provider-redacted-access-view-policies.json",
        "/vault/storage-provider-redacted-access-view-blockers.json",
        "/vault/storage-provider-redacted-access-view-events.json",
        "/vault/storage-provider-redacted-access-view-validation.json",
        "/vault/storage-provider-redacted-access-view-next-step.json",
        "/vault/gp074-status.json",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Real Storage Provider Redacted Access View Lock Contract" in response.data
