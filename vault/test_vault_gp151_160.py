"""
Tests for VAULT GP151-GP160 — Real Provider Connection Readiness Layer
"""

from pathlib import Path
import pytest

from vault.real_provider_connection_readiness_layer_service import (
    BLOCKER_SPECS,
    CONFIG_ITEMS,
    CONFIG_STATUS_DASHBOARD_ID,
    CONNECTION_LOCK_VALIDATION_ID,
    CONNECTION_PREFLIGHT_ID,
    CONNECTION_READINESS_SHELL_ID,
    CREDENTIAL_BOUNDARY_PANEL_ID,
    CREDENTIAL_ITEMS,
    ENCRYPTION_ITEMS,
    ENCRYPTION_READINESS_PANEL_ID,
    ENDPOINT_ITEMS,
    ENDPOINT_NAMESPACE_PANEL_ID,
    FALSE_FIELDS,
    HEALTH_PLACEHOLDERS,
    LOCK_VALIDATIONS,
    PROVIDER_HEALTH_PLACEHOLDER_ID,
    READINESS_BLOCKER_BOARD_ID,
    READINESS_ID,
    ensure_real_provider_connection_readiness_layer_schema,
    get_gp151_real_provider_connection_readiness_shell,
    get_gp151_status,
    get_gp152_provider_configuration_status_dashboard,
    get_gp152_status,
    get_gp153_credential_boundary_review_panel,
    get_gp153_status,
    get_gp154_endpoint_namespace_review_panel,
    get_gp154_status,
    get_gp155_encryption_readiness_review_panel,
    get_gp155_status,
    get_gp156_provider_connection_preflight_checklist,
    get_gp156_status,
    get_gp157_provider_health_placeholder_panel,
    get_gp157_status,
    get_gp158_connection_test_lock_validation,
    get_gp158_status,
    get_gp159_real_provider_connection_readiness_blocker_board,
    get_gp159_status,
    get_gp160_real_provider_connection_readiness_checkpoint,
    get_gp160_status,
    get_real_provider_connection_readiness_layer_home,
    initialize_real_provider_connection_readiness_layer,
    render_real_provider_connection_readiness_layer_page,
    validate_real_provider_connection_readiness_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp151_160_db(tmp_path, monkeypatch):
    envs = {
        "VAULT_STORAGE_PROVIDER_DECISION_DB": "gp001.sqlite",
        "VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB": "gp002.sqlite",
        "VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB": "gp003.sqlite",
        "VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB": "gp004.sqlite",
        "VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB": "gp005.sqlite",
        "VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB": "gp006.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB": "gp061.sqlite",
        "VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB": "gp062.sqlite",
        "VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB": "gp063.sqlite",
        "VAULT_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT_DB": "gp064.sqlite",
        "VAULT_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT_DB": "gp065.sqlite",
        "VAULT_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT_DB": "gp066.sqlite",
        "VAULT_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT_DB": "gp067.sqlite",
        "VAULT_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT_DB": "gp068.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT_DB": "gp069.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT_DB": "gp070.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT_DB": "gp071.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_METADATA_RECEIPT_CONTRACT_DB": "gp072.sqlite",
        "VAULT_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_CONTRACT_DB": "gp073.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_DB": "gp074.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_PACKET_LOCK_CONTRACT_DB": "gp075.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_QUEUE_LOCK_CONTRACT_DB": "gp076.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_LOCK_CONTRACT_DB": "gp077.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_DB": "gp078.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_CLOSEOUT_LOCK_CONTRACT_DB": "gp079.sqlite",
        "VAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_DB": "gp080.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT_DB": "gp081.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_ELIGIBILITY_LOCK_CONTRACT_DB": "gp082.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_AUTHORITY_LOCK_CONTRACT_DB": "gp083.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_SCOPE_LOCK_CONTRACT_DB": "gp084.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_TARGET_LOCK_CONTRACT_DB": "gp085.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_OBJECT_LOCK_CONTRACT_DB": "gp086.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_JOB_LOCK_CONTRACT_DB": "gp087.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_API_LOCK_CONTRACT_DB": "gp088.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_EXPORT_LOCK_CONTRACT_DB": "gp089.sqlite",
        "VAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_DB": "gp090.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_DB": "gp091.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_DB": "gp092.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_DB": "gp093.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_DB": "gp094.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_DB": "gp095.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_GOVERNANCE_CLOSEOUT_LAYER_DB": "gp096_100.sqlite",
        "VAULT_RECOVERY_CASE_WORKSPACE_LAYER_DB": "gp101_110.sqlite",
        "VAULT_REDACTED_ARCHIVE_BROWSER_LAYER_DB": "gp111_120.sqlite",
        "VAULT_OWNER_CONSOLE_OPERATING_DASHBOARD_LAYER_DB": "gp121_130.sqlite",
        "VAULT_TOWER_GATED_PERMISSION_STEP_UP_LAYER_DB": "gp131_140.sqlite",
        "VAULT_PROVIDER_READINESS_SIMULATION_DRY_RUN_LAYER_DB": "gp141_150.sqlite",
        "VAULT_REAL_PROVIDER_CONNECTION_READINESS_LAYER_DB": "gp151_160.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp151_160.sqlite")

def test_gp151_160_schema_and_initialize(gp151_160_db):
    schema = ensure_real_provider_connection_readiness_layer_schema(gp151_160_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_real_provider_connection_readiness_components" in schema["tables"]
    assert "vault_real_provider_connection_readiness_items" in schema["tables"]
    assert "vault_real_provider_connection_readiness_blockers" in schema["tables"]
    assert "vault_real_provider_connection_readiness_checkpoint" in schema["tables"]

    result = initialize_real_provider_connection_readiness_layer(gp151_160_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["configuration_item_count"] == len(CONFIG_ITEMS)
    assert result["credential_item_count"] == len(CREDENTIAL_ITEMS)
    assert result["endpoint_item_count"] == len(ENDPOINT_ITEMS)
    assert result["encryption_item_count"] == len(ENCRYPTION_ITEMS)
    assert result["preflight_item_count"] == 6
    assert result["health_placeholder_count"] == len(HEALTH_PLACEHOLDERS)
    assert result["connection_lock_count"] == len(LOCK_VALIDATIONS)
    assert result["readiness_item_count"] == 34
    assert result["blocker_count"] == len(BLOCKER_SPECS)
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp151_shell(gp151_160_db):
    payload = get_gp151_real_provider_connection_readiness_shell(gp151_160_db)
    shell = payload["connection_readiness_shell"]

    assert payload["pack"]["id"] == "VAULT_GP151"
    assert shell["component_id"] == CONNECTION_READINESS_SHELL_ID
    assert shell["gp_number"] == 151
    assert shell["section_range"] == "GP151-GP160"
    assert shell["source_gp150_readiness_score"] == 100
    assert len(shell["source_gp150_readiness_hash"]) == 64
    assert shell["component_ready"] is True
    assert shell["component_locked"] is True
    assert shell["readiness_only"] is True
    assert shell["no_provider_contact"] is True

    for field in FALSE_FIELDS:
        assert shell[field] is False

def test_gp152_configuration_dashboard(gp151_160_db):
    payload = get_gp152_provider_configuration_status_dashboard(gp151_160_db)
    items = payload["items"]

    assert payload["pack"]["id"] == "VAULT_GP152"
    assert payload["configuration_status_dashboard"]["component_id"] == CONFIG_STATUS_DASHBOARD_ID
    assert payload["configuration_item_count"] == len(CONFIG_ITEMS)
    assert all(item["item_group"] == "configuration" for item in items)
    assert all(item["item_ready"] is True for item in items)
    assert all(item["item_locked"] is True for item in items)
    assert all(item["readiness_only"] is True for item in items)
    assert all(item["no_provider_contact"] is True for item in items)
    assert all(item["provider_api_configured"] is False for item in items)
    assert all(item["provider_api_called"] is False for item in items)

def test_gp153_credential_boundary(gp151_160_db):
    payload = get_gp153_credential_boundary_review_panel(gp151_160_db)
    items = payload["items"]

    assert payload["pack"]["id"] == "VAULT_GP153"
    assert payload["credential_boundary_review_panel"]["component_id"] == CREDENTIAL_BOUNDARY_PANEL_ID
    assert payload["credential_item_count"] == len(CREDENTIAL_ITEMS)
    assert all(item["item_group"] == "credential_boundary" for item in items)
    assert all(item["provider_credentials_validated"] is False for item in items)
    assert all(item["provider_credential_value_read"] is False for item in items)
    assert all(item["provider_credential_value_persisted"] is False for item in items)
    assert all(item["provider_secret_value_read"] is False for item in items)
    assert all(item["provider_secret_value_persisted"] is False for item in items)
    assert all(item["credential_material_exposed"] is False for item in items)

def test_gp154_endpoint_namespace(gp151_160_db):
    payload = get_gp154_endpoint_namespace_review_panel(gp151_160_db)
    items = payload["items"]

    assert payload["pack"]["id"] == "VAULT_GP154"
    assert payload["endpoint_namespace_review_panel"]["component_id"] == ENDPOINT_NAMESPACE_PANEL_ID
    assert payload["endpoint_item_count"] == len(ENDPOINT_ITEMS)
    assert all(item["item_group"] == "endpoint_namespace" for item in items)
    assert all(item["provider_endpoint_called"] is False for item in items)
    assert all(item["provider_endpoint_reached"] is False for item in items)
    assert all(item["provider_namespace_activated"] is False for item in items)

def test_gp155_encryption_readiness(gp151_160_db):
    payload = get_gp155_encryption_readiness_review_panel(gp151_160_db)
    items = payload["items"]

    assert payload["pack"]["id"] == "VAULT_GP155"
    assert payload["encryption_readiness_review_panel"]["component_id"] == ENCRYPTION_READINESS_PANEL_ID
    assert payload["encryption_item_count"] == len(ENCRYPTION_ITEMS)
    assert all(item["item_group"] == "encryption" for item in items)
    assert all(item["item_ready"] is True for item in items)
    assert all(item["item_locked"] is True for item in items)
    assert all(item["provider_secret_value_read"] is False for item in items)
    assert all(item["object_body_read"] is False for item in items)

def test_gp156_preflight(gp151_160_db):
    payload = get_gp156_provider_connection_preflight_checklist(gp151_160_db)
    items = payload["items"]

    assert payload["pack"]["id"] == "VAULT_GP156"
    assert payload["provider_connection_preflight_checklist"]["component_id"] == CONNECTION_PREFLIGHT_ID
    assert payload["preflight_item_count"] == 6
    assert all(item["item_group"] == "preflight" for item in items)
    assert all(item["real_provider_connection_started"] is False for item in items)
    assert all(item["provider_api_called"] is False for item in items)
    assert all(item["tower_unlock_granted"] is False for item in items)
    assert all(item["execution_enabled"] is False for item in items)

def test_gp157_health_placeholder(gp151_160_db):
    payload = get_gp157_provider_health_placeholder_panel(gp151_160_db)
    items = payload["items"]

    assert payload["pack"]["id"] == "VAULT_GP157"
    assert payload["provider_health_placeholder_panel"]["component_id"] == PROVIDER_HEALTH_PLACEHOLDER_ID
    assert payload["health_placeholder_count"] == len(HEALTH_PLACEHOLDERS)
    assert all(item["item_group"] == "health_placeholder" for item in items)
    assert all(item["provider_health_checked"] is False for item in items)
    assert all(item["provider_health_passed"] is False for item in items)
    assert all(item["provider_status_poll_started"] is False for item in items)

def test_gp158_connection_lock_validation(gp151_160_db):
    payload = get_gp158_connection_test_lock_validation(gp151_160_db)
    items = payload["items"]

    assert payload["pack"]["id"] == "VAULT_GP158"
    assert payload["connection_test_lock_validation"]["component_id"] == CONNECTION_LOCK_VALIDATION_ID
    assert payload["connection_lock_count"] == len(LOCK_VALIDATIONS)
    assert all(item["item_group"] == "connection_lock_validation" for item in items)
    assert all(item["real_provider_connection_requested"] is False for item in items)
    assert all(item["real_provider_connection_started"] is False for item in items)
    assert all(item["provider_token_created"] is False for item in items)
    assert all(item["provider_session_created"] is False for item in items)
    assert all(item["provider_job_reference_created"] is False for item in items)
    assert all(item["provider_status_poll_started"] is False for item in items)

def test_gp159_blockers(gp151_160_db):
    payload = get_gp159_real_provider_connection_readiness_blocker_board(gp151_160_db)
    blockers = payload["blockers"]

    assert payload["pack"]["id"] == "VAULT_GP159"
    assert payload["readiness_blocker_board"]["component_id"] == READINESS_BLOCKER_BOARD_ID
    assert payload["blocker_count"] == len(BLOCKER_SPECS)
    assert all(item["blocker_active"] is True for item in blockers)
    assert all(item["blocks_real_connection"] is True for item in blockers)
    assert all(item["blocks_provider_api"] is True for item in blockers)
    assert all(item["blocks_credentials"] is True for item in blockers)
    assert all(item["blocks_secret_read"] is True for item in blockers)
    assert all(item["blocks_endpoint_call"] is True for item in blockers)
    assert all(item["blocks_provider_token"] is True for item in blockers)
    assert all(item["blocks_provider_session"] is True for item in blockers)
    assert all(item["blocks_provider_job"] is True for item in blockers)
    assert all(item["blocks_status_poll"] is True for item in blockers)
    assert all(item["blocks_object_catalog"] is True for item in blockers)
    assert all(item["blocks_metadata_import"] is True for item in blockers)
    assert all(item["blocks_object_body"] is True for item in blockers)
    assert all(item["blocks_download"] is True for item in blockers)
    assert all(item["blocks_restore"] is True for item in blockers)
    assert all(item["blocks_export"] is True for item in blockers)
    assert all(item["blocks_direct_upload"] is True for item in blockers)
    assert all(item["blocks_tower_unlock"] is True for item in blockers)
    assert all(item["blocks_execution"] is True for item in blockers)
    assert all(item["blocks_vault_done"] is True for item in blockers)
    assert all(item["resolved"] is False for item in blockers)

def test_gp160_readiness_home_status_and_validation(gp151_160_db):
    payload = get_gp160_real_provider_connection_readiness_checkpoint(gp151_160_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP160"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["configuration_item_count"] == len(CONFIG_ITEMS)
    assert readiness["credential_item_count"] == len(CREDENTIAL_ITEMS)
    assert readiness["endpoint_item_count"] == len(ENDPOINT_ITEMS)
    assert readiness["encryption_item_count"] == len(ENCRYPTION_ITEMS)
    assert readiness["preflight_item_count"] == 6
    assert readiness["health_placeholder_count"] == len(HEALTH_PLACEHOLDERS)
    assert readiness["connection_lock_count"] == len(LOCK_VALIDATIONS)
    assert readiness["readiness_item_count"] == 34
    assert readiness["blocker_count"] == len(BLOCKER_SPECS)
    assert readiness["safe_to_continue_to_gp161"] is True
    assert readiness["section_ready"] is True
    assert readiness["readiness_only"] is True
    assert readiness["no_provider_contact"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp161"] is True
    assert validation["vault_done"] is False

    status = get_gp160_status(gp151_160_db)["gp160_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp161"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_CONTROLLED_PROVIDER_CONNECTION_TEST_LOCK_LAYER"
    assert status["next_section_range"] == "GP161-GP170"
    assert status["next_pack"] == "VAULT_GP161_170_CONTROLLED_PROVIDER_CONNECTION_TEST_LOCK_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp160"

    home = get_real_provider_connection_readiness_layer_home(gp151_160_db)
    assert home["pack"]["id"] == "VAULT_GP151_160"
    assert home["truth"]["real_provider_connection_readiness_layer_ready"] is True
    assert home["truth"]["safe_to_continue_to_gp161"] is True
    assert home["truth"]["readiness_only"] is True
    assert home["truth"]["no_provider_contact"] is True
    assert home["truth"]["real_provider_connection_started"] is False
    assert home["truth"]["provider_api_called"] is False
    assert home["truth"]["provider_token_created"] is False
    assert home["truth"]["provider_session_created"] is False
    assert home["truth"]["provider_job_reference_created"] is False
    assert home["truth"]["provider_status_poll_started"] is False
    assert home["truth"]["provider_health_checked"] is False
    assert home["truth"]["provider_credentials_validated"] is False
    assert home["truth"]["provider_credential_value_read"] is False
    assert home["truth"]["provider_secret_value_read"] is False
    assert home["truth"]["provider_endpoint_called"] is False
    assert home["truth"]["provider_objects_listed"] is False
    assert home["truth"]["provider_metadata_imported"] is False
    assert home["truth"]["provider_metadata_read"] is False
    assert home["truth"]["object_body_read"] is False
    assert home["truth"]["object_body_view_enabled"] is False
    assert home["truth"]["object_body_download_enabled"] is False
    assert home["truth"]["object_body_plaintext_visible"] is False
    assert home["truth"]["export_package_created"] is False
    assert home["truth"]["restore_job_created"] is False
    assert home["truth"]["direct_upload_enabled"] is False
    assert home["truth"]["tower_unlock_granted"] is False
    assert home["truth"]["execution_enabled"] is False
    assert home["truth"]["vault_done"] is False
    assert home["truth"]["clouds_should_continue"] is False

def test_gp151_160_all_status_endpoints(gp151_160_db):
    funcs = [
        (151, get_gp151_status, "gp151_status"),
        (152, get_gp152_status, "gp152_status"),
        (153, get_gp153_status, "gp153_status"),
        (154, get_gp154_status, "gp154_status"),
        (155, get_gp155_status, "gp155_status"),
        (156, get_gp156_status, "gp156_status"),
        (157, get_gp157_status, "gp157_status"),
        (158, get_gp158_status, "gp158_status"),
        (159, get_gp159_status, "gp159_status"),
        (160, get_gp160_status, "gp160_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp151_160_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp161"] is True
        assert status["source_gp150_readiness_score"] == 100
        assert len(status["source_gp150_readiness_hash"]) == 64
        assert status["component_count"] == 10
        assert status["readiness_item_count"] == 34
        assert status["blocker_count"] == len(BLOCKER_SPECS)
        assert status["readiness_only"] is True
        assert status["no_provider_contact"] is True
        assert status["real_provider_connection_requested"] is False
        assert status["real_provider_connection_started"] is False
        assert status["real_provider_connection_completed"] is False
        assert status["provider_api_called"] is False
        assert status["provider_token_created"] is False
        assert status["provider_session_created"] is False
        assert status["provider_job_reference_created"] is False
        assert status["provider_status_poll_started"] is False
        assert status["provider_health_checked"] is False
        assert status["provider_credentials_validated"] is False
        assert status["provider_credential_value_read"] is False
        assert status["provider_secret_value_read"] is False
        assert status["provider_endpoint_called"] is False
        assert status["provider_objects_listed"] is False
        assert status["provider_metadata_imported"] is False
        assert status["provider_metadata_read"] is False
        assert status["object_body_read"] is False
        assert status["object_body_view_enabled"] is False
        assert status["object_body_download_enabled"] is False
        assert status["object_body_plaintext_visible"] is False
        assert status["export_package_created"] is False
        assert status["restore_job_created"] is False
        assert status["provider_restore_api_called"] is False
        assert status["direct_upload_enabled"] is False
        assert status["tower_unlock_granted"] is False
        assert status["execution_enabled"] is False
        assert status["vault_done"] is False

def test_gp151_160_html_is_dark_and_routes_registered(gp151_160_db):
    html = render_real_provider_connection_readiness_layer_page()
    lowered = html.lower()
    assert "Vault GP151-GP160 Real Provider Connection Readiness Layer" in html
    assert "GP151-GP160 built" in html
    assert "Readiness only" in html
    assert "Safe to GP161" in html
    assert "No provider contact" in html
    assert "No provider API" in html
    assert "No secret read" in html
    assert "No token/session/job" in html
    assert "No object body" in html
    assert "No export/restore" in html
    assert "No execution" in html
    assert "VAULT_GP161_170_CONTROLLED_PROVIDER_CONNECTION_TEST_LOCK_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-provider-connection-readiness-layer",
        "/vault/real-provider-connection-readiness-layer.json",
        "/vault/real-provider-connection-readiness-shell.json",
        "/vault/provider-configuration-status-dashboard.json",
        "/vault/credential-boundary-review-panel.json",
        "/vault/endpoint-namespace-review-panel.json",
        "/vault/encryption-readiness-review-panel.json",
        "/vault/provider-connection-preflight-checklist.json",
        "/vault/provider-health-placeholder-panel.json",
        "/vault/connection-test-lock-validation.json",
        "/vault/real-provider-connection-readiness-blocker-board.json",
        "/vault/real-provider-connection-readiness-checkpoint.json",
        "/vault/gp151-status.json",
        "/vault/gp152-status.json",
        "/vault/gp153-status.json",
        "/vault/gp154-status.json",
        "/vault/gp155-status.json",
        "/vault/gp156-status.json",
        "/vault/gp157-status.json",
        "/vault/gp158-status.json",
        "/vault/gp159-status.json",
        "/vault/gp160-status.json",
    ]
    for route in required_routes:
        assert route in text
