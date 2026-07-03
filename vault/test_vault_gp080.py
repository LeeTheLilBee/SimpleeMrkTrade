"""
Tests for VAULT GP080 — Real Provider Receipt and Redacted Access Readiness Checkpoint
"""

from pathlib import Path
import pytest

from vault.real_provider_receipt_redacted_access_readiness_checkpoint_service import (
    COMPONENT_SPECS,
    DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,
    READINESS_BLOCKER_SPECS,
    ensure_provider_receipt_redacted_access_readiness_checkpoint_schema,
    get_gp080_status,
    get_provider_receipt_redacted_access_readiness_blockers,
    get_provider_receipt_redacted_access_readiness_checkpoint_record,
    get_provider_receipt_redacted_access_readiness_components,
    get_provider_receipt_redacted_access_readiness_events,
    get_provider_receipt_redacted_access_readiness_next_step,
    get_real_provider_receipt_redacted_access_readiness_checkpoint_home,
    initialize_real_provider_receipt_redacted_access_readiness_checkpoint,
    record_provider_receipt_redacted_access_readiness_event,
    render_real_provider_receipt_redacted_access_readiness_checkpoint_page,
    validate_provider_receipt_redacted_access_readiness_checkpoint,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COMPONENTS = len(COMPONENT_SPECS)
EXPECTED_BLOCKERS = len(READINESS_BLOCKER_SPECS)

@pytest.fixture()
def gp080_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "provider_receipt_redacted_access_readiness.sqlite")

def test_gp080_schema_is_real_sqlite_backed(gp080_db):
    result = ensure_provider_receipt_redacted_access_readiness_checkpoint_schema(gp080_db)

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert Path(result["db_path"]).exists()
    assert "vault_provider_receipt_redacted_access_readiness_checkpoints" in result["tables"]
    assert "vault_provider_receipt_redacted_access_readiness_components" in result["tables"]
    assert "vault_provider_receipt_redacted_access_readiness_blockers" in result["tables"]
    assert "vault_provider_receipt_redacted_access_readiness_events" in result["tables"]

def test_gp080_initialize_creates_real_checkpoint_components_blockers_events(gp080_db):
    result = initialize_real_provider_receipt_redacted_access_readiness_checkpoint(gp080_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["checkpoint_count"] == 1
    assert result["component_count"] == EXPECTED_COMPONENTS
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_provider_receipt_redacted_access_readiness_checkpoint(gp080_db)
    assert second["checkpoint_count"] == 1
    assert second["component_count"] == EXPECTED_COMPONENTS
    assert second["blocker_count"] == EXPECTED_BLOCKERS

def test_gp080_checkpoint_record_closes_section_but_not_vault(gp080_db):
    checkpoint = get_provider_receipt_redacted_access_readiness_checkpoint_record(gp080_db)["readiness_checkpoint"]

    assert checkpoint["readiness_checkpoint_id"] == DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID
    assert checkpoint["pack_id"] == "VAULT_GP080"
    assert checkpoint["section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
    assert checkpoint["section_range"] == "GP071-GP080"
    assert checkpoint["next_section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_LAYER"
    assert checkpoint["next_section_range"] == "GP081-GP090"
    assert checkpoint["next_pack"] == "VAULT_GP081_REAL_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT"

    assert checkpoint["provider_receipt_redacted_access_readiness_checkpoint_ready"] is True
    assert checkpoint["section_gp071_gp080_ready"] is True
    assert checkpoint["component_registry_ready"] is True
    assert checkpoint["component_validation_ready"] is True
    assert checkpoint["blocker_register_ready"] is True
    assert checkpoint["event_log_ready"] is True
    assert checkpoint["real_sqlite_backed"] is True
    assert checkpoint["real_provider_receipt_redacted_access_layer_closed"] is True
    assert checkpoint["safe_to_continue_to_gp081"] is True
    assert checkpoint["readiness_score"] == 100

    locked_false_fields = [
        "provider_object_catalog_unlocked",
        "provider_object_listing_configured",
        "provider_object_list_attempted",
        "provider_objects_listed",
        "provider_metadata_imported",
        "provider_metadata_read",
        "object_identifier_collected",
        "object_body_read",
        "object_body_view_enabled",
        "object_body_download_enabled",
        "redacted_access_view_enabled",
        "owner_review_packet_created",
        "owner_review_queue_created",
        "owner_decision_recorded",
        "owner_review_decision_receipt_created",
        "owner_review_closeout_created",
        "owner_review_closeout_finalized",
        "closeout_transition_to_readiness_enabled",
        "tower_unlock_requested",
        "tower_unlock_granted",
        "provider_packet_attached",
        "object_identifier_attached",
        "object_body_attached",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
        "vault_done",
    ]
    for field in locked_false_fields:
        assert checkpoint[field] is False

def test_gp080_components_verify_gp071_through_gp079(gp080_db):
    payload = get_provider_receipt_redacted_access_readiness_components(gp080_db)

    assert payload["component_count"] == EXPECTED_COMPONENTS
    assert payload["component_ready_count"] == EXPECTED_COMPONENTS
    assert payload["component_validation_passed_count"] == EXPECTED_COMPONENTS
    assert payload["component_safe_to_continue_count"] == EXPECTED_COMPONENTS
    assert payload["component_real_sqlite_backed_count"] == EXPECTED_COMPONENTS
    assert payload["component_locked_count"] == EXPECTED_COMPONENTS
    assert payload["component_template_only_or_checkpoint_count"] == EXPECTED_COMPONENTS
    assert payload["component_no_provider_unlock_count"] == EXPECTED_COMPONENTS
    assert payload["component_no_direct_upload_count"] == EXPECTED_COMPONENTS
    assert payload["component_no_export_count"] == EXPECTED_COMPONENTS
    assert payload["component_no_execution_count"] == EXPECTED_COMPONENTS
    assert payload["component_vault_not_done_count"] == EXPECTED_COMPONENTS

    pack_ids = [item["pack_id"] for item in payload["components"]]
    assert pack_ids == [
        "VAULT_GP071",
        "VAULT_GP072",
        "VAULT_GP073",
        "VAULT_GP074",
        "VAULT_GP075",
        "VAULT_GP076",
        "VAULT_GP077",
        "VAULT_GP078",
        "VAULT_GP079",
    ]

    for item in payload["components"]:
        assert item["readiness_checkpoint_id"] == DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID
        assert item["component_status"] == "REAL_COMPONENT_READY_LOCKED_SAFE_TO_CONTINUE"
        assert item["component_ready"] is True
        assert item["component_validation_passed"] is True
        assert item["component_safe_to_continue"] is True
        assert item["component_real_sqlite_backed"] is True
        assert item["component_locked"] is True
        assert item["component_no_provider_unlock"] is True
        assert item["component_no_direct_upload"] is True
        assert item["component_no_export"] is True
        assert item["component_no_execution"] is True
        assert item["component_vault_not_done"] is True

def test_gp080_blockers_are_real_active_and_carried_to_next_layer(gp080_db):
    payload = get_provider_receipt_redacted_access_readiness_blockers(gp080_db)

    assert payload["blocker_count"] == EXPECTED_BLOCKERS
    assert payload["blocker_active_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_unlock_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_listing_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_metadata_import_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_identifier_collection_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_body_read_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_owner_review_finalization_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_tower_unlock_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_direct_upload_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_export_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_required_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_granted_count"] == 0
    assert payload["risk_accepted_count"] == 0
    assert payload["risk_waived_count"] == 0
    assert payload["mitigation_approved_count"] == 0
    assert payload["resolved_count"] == 0

    codes = {item["blocker_code"] for item in payload["blockers"]}
    assert "provider_object_catalog_locked" in codes
    assert "provider_metadata_import_locked" in codes
    assert "provider_object_listing_locked" in codes
    assert "provider_object_body_read_locked" in codes
    assert "owner_review_closeout_locked" in codes
    assert "tower_unlock_locked" in codes
    assert "direct_upload_locked" in codes
    assert "export_locked" in codes
    assert "execution_locked" in codes

def test_gp080_event_log_and_manual_event_write_do_not_unlock(gp080_db):
    events = get_provider_receipt_redacted_access_readiness_events(gp080_db)
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_CREATED" in event_types
    assert "GP071_GP079_COMPONENTS_REGISTERED" in event_types
    assert "READINESS_BLOCKERS_REGISTERED" in event_types
    assert "PROVIDER_RECEIPT_REDACTED_ACCESS_LOCKS_CONFIRMED" in event_types
    assert "REAL_PROVIDER_RECEIPT_REDACTED_ACCESS_LAYER_CLOSED" in event_types
    assert "NEXT_LAYER_PREPARED" in event_types

    before = events["event_count"]
    written = record_provider_receipt_redacted_access_readiness_event(
        "OWNER_GP080_READINESS_REVIEWED",
        {"reviewer": "owner"},
        gp080_db,
    )
    after = get_provider_receipt_redacted_access_readiness_events(gp080_db)

    assert after["event_count"] == before + 1
    assert written["event_written"] is True
    assert written["section_gp071_gp080_ready"] is True
    assert written["real_provider_receipt_redacted_access_layer_closed"] is True
    assert written["safe_to_continue_to_gp081"] is True
    assert written["provider_object_catalog_unlocked"] is False
    assert written["provider_metadata_imported"] is False
    assert written["provider_objects_listed"] is False
    assert written["object_body_read"] is False
    assert written["redacted_access_view_enabled"] is False
    assert written["tower_unlock_granted"] is False
    assert written["direct_upload_enabled"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

def test_gp080_validation_home_status_and_next_step(gp080_db):
    validation = validate_provider_receipt_redacted_access_readiness_checkpoint(gp080_db)

    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["section_closed"] is True
    assert validation["safe_to_continue_to_gp081"] is True
    assert validation["vault_done"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_EXISTS" in codes
    assert "SECTION_GP071_GP080_READY" in codes
    assert "REAL_PROVIDER_RECEIPT_REDACTED_ACCESS_LAYER_CLOSED" in codes
    assert "READINESS_SCORE_100" in codes
    assert "REAL_COMPONENTS_EXIST" in codes
    assert "ALL_COMPONENTS_READY" in codes
    assert "ALL_COMPONENTS_VALIDATION_PASSED" in codes
    assert "ALL_COMPONENTS_SAFE_TO_CONTINUE" in codes
    assert "ALL_COMPONENTS_NO_DIRECT_UPLOAD" in codes
    assert "ALL_COMPONENTS_NO_EXPORT" in codes
    assert "ALL_COMPONENTS_NO_EXECUTION" in codes
    assert "READINESS_BLOCKERS_EXIST" in codes
    assert "ALL_BLOCKERS_BLOCK_TOWER_UNLOCK" in codes
    assert "ALL_BLOCKERS_BLOCK_DIRECT_UPLOAD" in codes
    assert "ALL_BLOCKERS_BLOCK_EXPORT" in codes
    assert "ALL_BLOCKERS_BLOCK_EXECUTION" in codes
    assert "NO_CHECKPOINT_PROVIDER_OBJECT_CATALOG_UNLOCKED" in codes
    assert "NO_CHECKPOINT_PROVIDER_OBJECTS_LISTED" in codes
    assert "NO_CHECKPOINT_PROVIDER_METADATA_IMPORTED" in codes
    assert "NO_CHECKPOINT_OBJECT_BODY_READ" in codes
    assert "NO_CHECKPOINT_DIRECT_UPLOAD_ENABLED" in codes
    assert "NO_CHECKPOINT_EXPORT_ENABLED" in codes
    assert "NO_CHECKPOINT_EXECUTION_ENABLED" in codes
    assert "NO_CHECKPOINT_VAULT_DONE" in codes

    home = get_real_provider_receipt_redacted_access_readiness_checkpoint_home(gp080_db)
    truth = home["provider_receipt_redacted_access_truth"]
    assert truth["real_provider_receipt_redacted_access_readiness_checkpoint_ready"] is True
    assert truth["section_closed"] is True
    assert truth["readiness_score"] == 100
    assert truth["validation_passed"] is True
    assert truth["component_count"] == EXPECTED_COMPONENTS
    assert truth["blocker_count"] == EXPECTED_BLOCKERS
    assert truth["provider_object_catalog_unlocked"] is False
    assert truth["provider_object_listing_configured"] is False
    assert truth["provider_objects_listed"] is False
    assert truth["provider_metadata_imported"] is False
    assert truth["provider_metadata_read"] is False
    assert truth["object_identifier_collected"] is False
    assert truth["object_body_read"] is False
    assert truth["object_body_view_enabled"] is False
    assert truth["redacted_access_view_enabled"] is False
    assert truth["owner_review_packet_created"] is False
    assert truth["owner_review_queue_created"] is False
    assert truth["owner_decision_recorded"] is False
    assert truth["owner_review_decision_receipt_created"] is False
    assert truth["owner_review_closeout_created"] is False
    assert truth["tower_unlock_granted"] is False
    assert truth["provider_packet_attached"] is False
    assert truth["object_body_attached"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["export_enabled"] is False
    assert truth["execution_enabled"] is False
    assert truth["safe_to_continue_to_gp081"] is True
    assert truth["vault_done"] is False

    status = get_gp080_status(gp080_db)
    gp080 = status["gp080_status"]
    assert gp080["ready"] is True
    assert gp080["validation_passed"] is True
    assert gp080["section_closed"] is True
    assert gp080["safe_to_continue_to_gp081"] is True
    assert gp080["readiness_score"] == 100
    assert gp080["real_checkpoint_count"] == 1
    assert gp080["real_component_count"] == EXPECTED_COMPONENTS
    assert gp080["real_blocker_count"] == EXPECTED_BLOCKERS
    assert gp080["component_count"] == EXPECTED_COMPONENTS
    assert gp080["component_ready_count"] == EXPECTED_COMPONENTS
    assert gp080["component_validation_passed_count"] == EXPECTED_COMPONENTS
    assert gp080["component_safe_to_continue_count"] == EXPECTED_COMPONENTS
    assert gp080["component_no_direct_upload_count"] == EXPECTED_COMPONENTS
    assert gp080["component_no_export_count"] == EXPECTED_COMPONENTS
    assert gp080["component_no_execution_count"] == EXPECTED_COMPONENTS
    assert gp080["blocker_count"] == EXPECTED_BLOCKERS
    assert gp080["blocks_provider_unlock_count"] == EXPECTED_BLOCKERS
    assert gp080["blocks_direct_upload_count"] == EXPECTED_BLOCKERS
    assert gp080["blocks_export_count"] == EXPECTED_BLOCKERS
    assert gp080["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert gp080["provider_object_catalog_unlocked"] is False
    assert gp080["provider_objects_listed"] is False
    assert gp080["provider_metadata_imported"] is False
    assert gp080["object_body_read"] is False
    assert gp080["tower_unlock_granted"] is False
    assert gp080["direct_upload_enabled"] is False
    assert gp080["export_enabled"] is False
    assert gp080["execution_enabled"] is False
    assert gp080["vault_done"] is False
    assert gp080["clouds_status"] == "parked_do_not_continue_from_vault_gp080"
    assert gp080["next_pack"] == "VAULT_GP081_REAL_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT"

    next_step = get_provider_receipt_redacted_access_readiness_next_step()["next_step"]
    assert next_step["current_section_range"] == "GP071-GP080"
    assert next_step["closed_section"] is True
    assert next_step["next_section_range"] == "GP081-GP090"
    assert next_step["next_pack"] == "VAULT_GP081_REAL_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT"
    assert next_step["safe_to_continue_to_gp081"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp080_html_is_dark_and_mentions_readiness(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_provider_receipt_redacted_access_readiness_checkpoint_page()
    lowered = html.lower()

    assert "Vault Real Provider Receipt and Redacted Access Readiness Checkpoint" in html
    assert "Real Provider Receipt and Redacted Access Layer" in html
    assert "GP080" in html
    assert "Section closed" in html
    assert "Real SQLite-backed" in html
    assert "Safe to GP081" in html
    assert "No provider unlock" in html
    assert "No object body read" in html
    assert "No direct upload" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-provider-receipt-redacted-access-readiness-checkpoint.json" in html
    assert "/vault/gp080-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp080_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-provider-receipt-redacted-access-readiness-checkpoint",
        "/vault/real-provider-receipt-redacted-access-readiness-checkpoint.json",
        "/vault/provider-receipt-redacted-access-readiness-checkpoint-record.json",
        "/vault/provider-receipt-redacted-access-readiness-components.json",
        "/vault/provider-receipt-redacted-access-readiness-blockers.json",
        "/vault/provider-receipt-redacted-access-readiness-events.json",
        "/vault/provider-receipt-redacted-access-readiness-validation.json",
        "/vault/provider-receipt-redacted-access-readiness-next-step.json",
        "/vault/gp080-status.json",
    ]
    for route in required_routes:
        assert route in text

def test_gp080_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()
    routes = [
        "/vault/real-provider-receipt-redacted-access-readiness-checkpoint",
        "/vault/real-provider-receipt-redacted-access-readiness-checkpoint.json",
        "/vault/provider-receipt-redacted-access-readiness-checkpoint-record.json",
        "/vault/provider-receipt-redacted-access-readiness-components.json",
        "/vault/provider-receipt-redacted-access-readiness-blockers.json",
        "/vault/provider-receipt-redacted-access-readiness-events.json",
        "/vault/provider-receipt-redacted-access-readiness-validation.json",
        "/vault/provider-receipt-redacted-access-readiness-next-step.json",
        "/vault/gp080-status.json",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Real Provider Receipt and Redacted Access Readiness Checkpoint" in response.data
