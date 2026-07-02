"""
Tests for VAULT GP070 — Real Storage Provider Configuration Readiness Checkpoint
"""

from pathlib import Path
import pytest

from vault.real_storage_provider_configuration_readiness_checkpoint_service import (
    CONFIGURATION_COMPONENTS,
    CONFIGURATION_READINESS_BLOCKERS,
    DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,
    ensure_storage_provider_configuration_readiness_checkpoint_schema,
    get_gp070_status,
    get_real_storage_provider_configuration_readiness_checkpoint_home,
    get_storage_provider_configuration_readiness_blockers,
    get_storage_provider_configuration_readiness_checkpoint_record,
    get_storage_provider_configuration_readiness_components,
    get_storage_provider_configuration_readiness_events,
    get_storage_provider_configuration_readiness_next_step,
    initialize_real_storage_provider_configuration_readiness_checkpoint,
    record_storage_provider_configuration_readiness_event,
    render_real_storage_provider_configuration_readiness_checkpoint_page,
    validate_storage_provider_configuration_readiness_checkpoint,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COMPONENTS = len(CONFIGURATION_COMPONENTS)
EXPECTED_BLOCKERS = len(CONFIGURATION_READINESS_BLOCKERS)

@pytest.fixture()
def gp070_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "configuration_readiness_checkpoint.sqlite")

def test_gp070_schema_is_real_sqlite_backed(gp070_db):
    result = ensure_storage_provider_configuration_readiness_checkpoint_schema(gp070_db)
    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert Path(result["db_path"]).exists()
    assert "vault_storage_provider_configuration_readiness_checkpoints" in result["tables"]
    assert "vault_storage_provider_configuration_readiness_components" in result["tables"]
    assert "vault_storage_provider_configuration_readiness_blockers" in result["tables"]
    assert "vault_storage_provider_configuration_readiness_events" in result["tables"]

def test_gp070_initialize_creates_real_checkpoint_components_blockers_events(gp070_db):
    result = initialize_real_storage_provider_configuration_readiness_checkpoint(gp070_db)
    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["checkpoint_count"] == 1
    assert result["component_count"] == EXPECTED_COMPONENTS
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_configuration_readiness_checkpoint(gp070_db)
    assert second["checkpoint_count"] == 1
    assert second["component_count"] == EXPECTED_COMPONENTS
    assert second["blocker_count"] == EXPECTED_BLOCKERS

def test_gp070_checkpoint_record_closes_section_but_does_not_unlock_provider(gp070_db):
    checkpoint = get_storage_provider_configuration_readiness_checkpoint_record(gp070_db)["configuration_readiness_checkpoint"]

    assert checkpoint["configuration_readiness_checkpoint_id"] == DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID
    assert checkpoint["pack_id"] == "VAULT_GP070"
    assert checkpoint["section_id"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert checkpoint["section_range"] == "GP061-GP070"
    assert checkpoint["source_object_body_view_pack_id"] == "VAULT_GP069"
    assert checkpoint["source_object_body_view_lock_contract_id"] == "VSPOBVLC-GP069-001"
    assert checkpoint["checkpoint_status"] == "REAL_CONFIGURATION_READINESS_CHECKPOINT_CLOSED_SAFE_TO_CONTINUE_LOCKED"

    assert checkpoint["configuration_readiness_checkpoint_ready"] is True
    assert checkpoint["configuration_layer_closed"] is True
    assert checkpoint["configuration_components_ready"] is True
    assert checkpoint["configuration_blockers_ready"] is True
    assert checkpoint["configuration_validation_ready"] is True
    assert checkpoint["configuration_locked"] is True
    assert checkpoint["safe_to_continue_to_next_section"] is True

    locked_false_fields = [
        "credentials_configured",
        "secret_values_present",
        "secret_references_created",
        "secret_references_activated",
        "provider_endpoint_configured",
        "storage_container_configured",
        "namespace_configured",
        "encryption_policy_configured",
        "connection_test_attempted",
        "provider_connection_tested",
        "write_path_configured",
        "write_path_attempted",
        "write_path_enabled",
        "read_path_configured",
        "read_path_attempted",
        "read_path_enabled",
        "object_body_view_configured",
        "object_body_view_attempted",
        "object_body_view_enabled",
        "object_body_content_exposed",
        "object_body_plaintext_visible",
        "object_body_download_enabled",
        "provider_configured",
        "provider_read_enabled",
        "provider_write_enabled",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
        "vault_done",
    ]
    for field in locked_false_fields:
        assert checkpoint[field] is False

    data = checkpoint["checkpoint_data"]
    assert data["safe_to_continue_to_next_section"] is True
    assert data["next_pack"] == "VAULT_GP071_REAL_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT"
    assert data["vault_done"] is False

def test_gp070_components_are_real_and_do_not_unlock_anything(gp070_db):
    payload = get_storage_provider_configuration_readiness_components(gp070_db)

    assert payload["component_count"] == EXPECTED_COMPONENTS
    assert payload["component_ready_count"] == EXPECTED_COMPONENTS
    assert payload["component_verified_count"] == EXPECTED_COMPONENTS
    assert payload["component_locked_count"] == EXPECTED_COMPONENTS
    assert payload["component_unlocks_provider_count"] == 0
    assert payload["component_unlocks_credentials_count"] == 0
    assert payload["component_unlocks_secrets_count"] == 0
    assert payload["component_unlocks_endpoint_count"] == 0
    assert payload["component_unlocks_encryption_count"] == 0
    assert payload["component_unlocks_connection_test_count"] == 0
    assert payload["component_unlocks_write_path_count"] == 0
    assert payload["component_unlocks_read_path_count"] == 0
    assert payload["component_unlocks_object_body_view_count"] == 0
    assert payload["component_unlocks_direct_upload_count"] == 0
    assert payload["component_unlocks_export_count"] == 0
    assert payload["component_unlocks_execution_count"] == 0
    assert payload["component_claims_vault_done_count"] == 0

    source_packs = {item["source_pack_id"] for item in payload["components"]}
    expected_source_packs = {item[0] for item in CONFIGURATION_COMPONENTS}
    assert source_packs == expected_source_packs

    for item in payload["components"]:
        assert item["configuration_component_id"].startswith("VSPCRC-COMP-")
        assert item["configuration_readiness_checkpoint_id"] == DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID
        assert item["component_ready"] is True
        assert item["component_verified"] is True
        assert item["component_locked"] is True
        assert item["component_unlocks_provider"] is False
        assert item["component_unlocks_credentials"] is False
        assert item["component_unlocks_secrets"] is False
        assert item["component_unlocks_endpoint"] is False
        assert item["component_unlocks_encryption"] is False
        assert item["component_unlocks_connection_test"] is False
        assert item["component_unlocks_write_path"] is False
        assert item["component_unlocks_read_path"] is False
        assert item["component_unlocks_object_body_view"] is False
        assert item["component_unlocks_direct_upload"] is False
        assert item["component_unlocks_export"] is False
        assert item["component_unlocks_execution"] is False
        assert item["component_claims_vault_done"] is False

def test_gp070_blockers_are_real_and_active(gp070_db):
    payload = get_storage_provider_configuration_readiness_blockers(gp070_db)

    assert payload["blocker_count"] == EXPECTED_BLOCKERS
    assert payload["blocker_active_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_configuration_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_read_write_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_body_view_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_direct_upload_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_export_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_granted_count"] == 0
    assert payload["risk_accepted_count"] == 0
    assert payload["risk_waived_count"] == 0
    assert payload["mitigation_approved_count"] == 0
    assert payload["resolved_count"] == 0

    codes = {item["blocker_code"] for item in payload["blockers"]}
    expected_codes = {item[0] for item in CONFIGURATION_READINESS_BLOCKERS}
    assert codes == expected_codes

    for item in payload["blockers"]:
        assert item["configuration_blocker_id"].startswith("VSPCRC-BLOCK-")
        assert item["configuration_readiness_checkpoint_id"] == DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID
        assert item["blocker_active"] is True
        assert item["blocks_provider_configuration"] is True
        assert item["blocks_provider_read_write"] is True
        assert item["blocks_object_body_view"] is True
        assert item["blocks_direct_upload"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False
        assert item["resolved"] is False

def test_gp070_event_log_and_manual_event_write_do_not_unlock(gp070_db):
    events = get_storage_provider_configuration_readiness_events(gp070_db)
    assert events["event_count"] >= 6
    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT_CREATED" in event_types
    assert "SOURCE_GP069_OBJECT_BODY_VIEW_LOCK_CONTRACT_ATTACHED" in event_types
    assert "REAL_CONFIGURATION_COMPONENTS_REGISTERED_LOCKED" in event_types
    assert "REAL_CONFIGURATION_BLOCKERS_REGISTERED_ACTIVE" in event_types
    assert "CONFIGURATION_LAYER_CLOSED_SAFE_TO_CONTINUE" in event_types
    assert "ALL_PROVIDER_CAPABILITIES_CONFIRMED_LOCKED" in event_types

    before = events["event_count"]
    written = record_storage_provider_configuration_readiness_event(
        "OWNER_GP070_CONFIGURATION_READINESS_REVIEWED",
        {"reviewer": "owner"},
        gp070_db,
    )
    after = get_storage_provider_configuration_readiness_events(gp070_db)
    assert after["event_count"] == before + 1
    assert written["event_written"] is True
    assert written["configuration_readiness_checkpoint_ready"] is True
    assert written["configuration_layer_closed"] is True
    assert written["safe_to_continue_to_next_section"] is True
    assert written["credentials_configured"] is False
    assert written["secret_values_present"] is False
    assert written["provider_connection_tested"] is False
    assert written["write_path_enabled"] is False
    assert written["read_path_enabled"] is False
    assert written["object_body_view_enabled"] is False
    assert written["direct_upload_enabled"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

def test_gp070_validation_home_status_and_next_step(gp070_db):
    validation = validate_storage_provider_configuration_readiness_checkpoint(gp070_db)
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp071"] is True
    assert validation["configuration_layer_closed"] is True
    assert validation["vault_done"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_CONFIGURATION_READINESS_CHECKPOINT_EXISTS" in codes
    assert "SOURCE_GP069_OBJECT_BODY_VIEW_LOCK_CONTRACT_ATTACHED" in codes
    assert "CONFIGURATION_LAYER_CLOSED" in codes
    assert "REAL_CONFIGURATION_COMPONENTS_EXIST" in codes
    assert "REAL_CONFIGURATION_BLOCKERS_EXIST" in codes
    assert "NO_CONTRACT_CREDENTIALS_CONFIGURED" in codes
    assert "NO_CONTRACT_PROVIDER_CONNECTION_TESTED" in codes
    assert "NO_CONTRACT_DIRECT_UPLOAD_ENABLED" in codes
    assert "NO_CONTRACT_EXPORT_ENABLED" in codes
    assert "NO_CONTRACT_EXECUTION_ENABLED" in codes
    assert "NO_CONTRACT_VAULT_DONE" in codes

    home = get_real_storage_provider_configuration_readiness_checkpoint_home(gp070_db)
    truth = home["configuration_readiness_truth"]
    assert truth["real_storage_provider_configuration_readiness_checkpoint_ready"] is True
    assert truth["validation_passed"] is True
    assert truth["configuration_layer_closed"] is True
    assert truth["safe_to_continue_to_gp071"] is True
    assert truth["component_count"] == EXPECTED_COMPONENTS
    assert truth["blocker_count"] == EXPECTED_BLOCKERS
    assert truth["credentials_configured"] is False
    assert truth["provider_connection_tested"] is False
    assert truth["write_path_enabled"] is False
    assert truth["read_path_enabled"] is False
    assert truth["object_body_view_enabled"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["export_enabled"] is False
    assert truth["execution_enabled"] is False
    assert truth["vault_done"] is False

    status = get_gp070_status(gp070_db)
    gp070 = status["gp070_status"]
    assert gp070["ready"] is True
    assert gp070["section_closed"] is True
    assert gp070["validation_passed"] is True
    assert gp070["safe_to_continue_to_gp071"] is True
    assert gp070["configuration_layer_closed"] is True
    assert gp070["component_count"] == EXPECTED_COMPONENTS
    assert gp070["blocker_count"] == EXPECTED_BLOCKERS
    assert gp070["component_unlocks_provider_count"] == 0
    assert gp070["component_unlocks_credentials_count"] == 0
    assert gp070["component_unlocks_secrets_count"] == 0
    assert gp070["component_unlocks_write_path_count"] == 0
    assert gp070["component_unlocks_read_path_count"] == 0
    assert gp070["component_unlocks_object_body_view_count"] == 0
    assert gp070["component_unlocks_direct_upload_count"] == 0
    assert gp070["component_unlocks_export_count"] == 0
    assert gp070["component_unlocks_execution_count"] == 0
    assert gp070["blocks_direct_upload_count"] == EXPECTED_BLOCKERS
    assert gp070["blocks_export_count"] == EXPECTED_BLOCKERS
    assert gp070["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert gp070["vault_done"] is False
    assert gp070["clouds_status"] == "parked_do_not_continue_from_vault_gp070"
    assert gp070["next_pack"] == "VAULT_GP071_REAL_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT"

    next_step = get_storage_provider_configuration_readiness_next_step()["next_step"]
    assert next_step["closed_section_range"] == "GP061-GP070"
    assert next_step["next_section_range"] == "GP071-GP080"
    assert next_step["next_pack"] == "VAULT_GP071_REAL_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT"
    assert next_step["safe_to_continue_to_gp071"] is True
    assert next_step["configuration_layer_closed"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp070_html_is_dark_and_mentions_configuration_readiness(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_storage_provider_configuration_readiness_checkpoint_page()
    lowered = html.lower()
    assert "Vault Real Storage Provider Configuration Readiness Checkpoint" in html
    assert "Real Storage Provider Configuration Layer" in html
    assert "GP070" in html
    assert "Configuration checkpoint ready" in html
    assert "Safe to continue GP071" in html
    assert "No provider configured" in html
    assert "No direct upload" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-configuration-readiness-checkpoint.json" in html
    assert "/vault/gp070-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp070_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-storage-provider-configuration-readiness-checkpoint",
        "/vault/real-storage-provider-configuration-readiness-checkpoint.json",
        "/vault/storage-provider-configuration-readiness-checkpoint-record.json",
        "/vault/storage-provider-configuration-readiness-components.json",
        "/vault/storage-provider-configuration-readiness-blockers.json",
        "/vault/storage-provider-configuration-readiness-events.json",
        "/vault/storage-provider-configuration-readiness-validation.json",
        "/vault/storage-provider-configuration-readiness-next-step.json",
        "/vault/gp070-status.json",
    ]
    for route in required_routes:
        assert route in text

def test_gp070_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()
    routes = [
        "/vault/real-storage-provider-configuration-readiness-checkpoint",
        "/vault/real-storage-provider-configuration-readiness-checkpoint.json",
        "/vault/storage-provider-configuration-readiness-checkpoint-record.json",
        "/vault/storage-provider-configuration-readiness-components.json",
        "/vault/storage-provider-configuration-readiness-blockers.json",
        "/vault/storage-provider-configuration-readiness-events.json",
        "/vault/storage-provider-configuration-readiness-validation.json",
        "/vault/storage-provider-configuration-readiness-next-step.json",
        "/vault/gp070-status.json",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Real Storage Provider Configuration Readiness Checkpoint" in response.data
