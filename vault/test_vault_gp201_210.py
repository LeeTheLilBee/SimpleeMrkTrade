"""
Tests for VAULT GP201-GP210 — Owner Productization Beta Readiness Layer
"""

from pathlib import Path
import pytest

from vault.owner_productization_beta_readiness_layer_service import (
    ACCESS_LOCK_ITEMS,
    BETA_QA_SCENARIO_ID,
    BETA_READINESS_INVENTORY_ID,
    BETA_READINESS_ITEMS,
    BETA_TESTER_ACCESS_LOCK_ID,
    COPY_POSITIONING_ITEMS,
    FALSE_FIELDS,
    LAUNCH_RISK_BLOCKER_ID,
    LAUNCH_RISK_BLOCKERS,
    OWNER_PRODUCT_SURFACE_MAP_ID,
    PRODUCT_COPY_POSITIONING_ID,
    PRODUCT_SURFACES,
    PRODUCTIZATION_SHELL_ID,
    QA_SCENARIOS,
    READINESS_ID,
    RECEIPT_PACKET_ID,
    SUPPORT_FEEDBACK_INTAKE_ID,
    SUPPORT_FEEDBACK_ITEMS,
    ensure_owner_productization_beta_readiness_layer_schema,
    get_gp201_owner_productization_shell,
    get_gp201_status,
    get_gp202_beta_readiness_inventory,
    get_gp202_status,
    get_gp203_owner_product_surface_map,
    get_gp203_status,
    get_gp204_beta_tester_access_lock_board,
    get_gp204_status,
    get_gp205_product_copy_positioning_board,
    get_gp205_status,
    get_gp206_support_feedback_intake_plan,
    get_gp206_status,
    get_gp207_beta_qa_scenario_board,
    get_gp207_status,
    get_gp208_launch_risk_blocker_board,
    get_gp208_status,
    get_gp209_owner_productization_receipt_packet,
    get_gp209_status,
    get_gp210_owner_productization_beta_readiness_checkpoint,
    get_gp210_status,
    get_owner_productization_beta_readiness_layer_home,
    initialize_owner_productization_beta_readiness_layer,
    render_owner_productization_beta_readiness_layer_page,
    validate_owner_productization_beta_readiness_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp201_210_db(tmp_path, monkeypatch):
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
        "VAULT_CONTROLLED_PROVIDER_CONNECTION_TEST_LOCK_LAYER_DB": "gp161_170.sqlite",
        "VAULT_CONTROLLED_READ_ONLY_METADATA_TEST_LAYER_DB": "gp171_180.sqlite",
        "VAULT_REAL_ARCHIVE_INDEX_SEARCH_LAYER_DB": "gp181_190.sqlite",
        "VAULT_MAJOR_PRODUCT_READINESS_CHECKPOINT_LAYER_DB": "gp191_200.sqlite",
        "VAULT_OWNER_PRODUCTIZATION_BETA_READINESS_LAYER_DB": "gp201_210.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp201_210.sqlite")

def test_gp201_210_schema_and_initialize(gp201_210_db):
    schema = ensure_owner_productization_beta_readiness_layer_schema(gp201_210_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_owner_productization_components" in schema["tables"]
    assert "vault_beta_readiness_inventory" in schema["tables"]
    assert "vault_owner_productization_beta_readiness_checkpoint" in schema["tables"]

    result = initialize_owner_productization_beta_readiness_layer(gp201_210_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["beta_readiness_count"] == len(BETA_READINESS_ITEMS)
    assert result["surface_count"] == len(PRODUCT_SURFACES)
    assert result["access_lock_count"] == len(ACCESS_LOCK_ITEMS)
    assert result["copy_positioning_count"] == len(COPY_POSITIONING_ITEMS)
    assert result["support_feedback_count"] == len(SUPPORT_FEEDBACK_ITEMS)
    assert result["qa_scenario_count"] == len(QA_SCENARIOS)
    assert result["launch_risk_blocker_count"] == len(LAUNCH_RISK_BLOCKERS)
    assert result["receipt_packet_count"] == 1
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp201_shell(gp201_210_db):
    payload = get_gp201_owner_productization_shell(gp201_210_db)
    shell = payload["productization_shell"]

    assert payload["pack"]["id"] == "VAULT_GP201"
    assert shell["component_id"] == PRODUCTIZATION_SHELL_ID
    assert shell["gp_number"] == 201
    assert shell["source_gp200_readiness_score"] == 100
    assert len(shell["source_gp200_readiness_hash"]) == 64
    assert shell["component_ready"] is True
    assert shell["component_locked"] is True
    assert shell["owner_productization_ready"] is True
    assert shell["beta_readiness_prepared"] is True
    assert shell["beta_launch_locked"] is True
    assert shell["beta_access_locked"] is True
    assert shell["vault_not_done"] is True

    for field in FALSE_FIELDS:
        assert shell[field] is False

def test_gp202_beta_inventory(gp201_210_db):
    payload = get_gp202_beta_readiness_inventory(gp201_210_db)
    rows = payload["items"]

    assert payload["pack"]["id"] == "VAULT_GP202"
    assert payload["beta_readiness_inventory"]["component_id"] == BETA_READINESS_INVENTORY_ID
    assert payload["beta_readiness_count"] == len(BETA_READINESS_ITEMS)
    assert all(item["item_ready"] is True for item in rows)
    assert all(item["item_locked"] is True for item in rows)
    assert all(item["beta_launch_approved"] is False for item in rows)
    assert all(item["beta_tester_access_granted"] is False for item in rows)
    assert all(item["vault_done"] is False for item in rows)

def test_gp203_surface_map(gp201_210_db):
    payload = get_gp203_owner_product_surface_map(gp201_210_db)
    rows = payload["surfaces"]

    assert payload["pack"]["id"] == "VAULT_GP203"
    assert payload["surface_map"]["component_id"] == OWNER_PRODUCT_SURFACE_MAP_ID
    assert payload["surface_count"] == len(PRODUCT_SURFACES)
    assert all(item["surface_ready"] is True for item in rows)
    assert all(item["surface_locked"] is True for item in rows)
    assert all(item["surface_path"].startswith("/vault/") for item in rows)
    assert all(item["public_launch_approved"] is False for item in rows)

def test_gp204_access_locks(gp201_210_db):
    payload = get_gp204_beta_tester_access_lock_board(gp201_210_db)
    rows = payload["access_locks"]

    assert payload["pack"]["id"] == "VAULT_GP204"
    assert payload["access_lock_board"]["component_id"] == BETA_TESTER_ACCESS_LOCK_ID
    assert payload["access_lock_count"] == len(ACCESS_LOCK_ITEMS)
    assert all(item["access_locked"] is True for item in rows)
    assert all(item["blocks_beta_access"] is True for item in rows)
    assert all(item["beta_invite_created"] is False for item in rows)
    assert all(item["beta_invite_sent"] is False for item in rows)
    assert all(item["beta_tester_added"] is False for item in rows)
    assert all(item["beta_tester_access_granted"] is False for item in rows)
    assert all(item["beta_access_token_created"] is False for item in rows)
    assert all(item["beta_access_session_created"] is False for item in rows)

def test_gp205_copy_positioning(gp201_210_db):
    payload = get_gp205_product_copy_positioning_board(gp201_210_db)
    rows = payload["copy_items"]

    assert payload["pack"]["id"] == "VAULT_GP205"
    assert payload["copy_positioning_board"]["component_id"] == PRODUCT_COPY_POSITIONING_ID
    assert payload["copy_positioning_count"] == len(COPY_POSITIONING_ITEMS)
    assert all(item["copy_ready"] is True for item in rows)
    assert all(item["copy_locked"] is True for item in rows)
    assert all(item["public_launch_approved"] is False for item in rows)

def test_gp206_support_feedback(gp201_210_db):
    payload = get_gp206_support_feedback_intake_plan(gp201_210_db)
    rows = payload["support_items"]

    assert payload["pack"]["id"] == "VAULT_GP206"
    assert payload["support_feedback_intake_plan"]["component_id"] == SUPPORT_FEEDBACK_INTAKE_ID
    assert payload["support_feedback_count"] == len(SUPPORT_FEEDBACK_ITEMS)
    assert all(item["intake_ready"] is True for item in rows)
    assert all(item["intake_locked"] is True for item in rows)
    assert all(item["live_intake_enabled"] is False for item in rows)
    assert all(item["beta_launch_approved"] is False for item in rows)

def test_gp207_qa_scenarios(gp201_210_db):
    payload = get_gp207_beta_qa_scenario_board(gp201_210_db)
    rows = payload["scenarios"]

    assert payload["pack"]["id"] == "VAULT_GP207"
    assert payload["qa_scenario_board"]["component_id"] == BETA_QA_SCENARIO_ID
    assert payload["qa_scenario_count"] == len(QA_SCENARIOS)
    assert all(item["qa_ready"] is True for item in rows)
    assert all(item["qa_locked"] is True for item in rows)
    assert all(item["beta_launch_approved"] is False for item in rows)
    assert all(item["execution_enabled"] is False for item in rows)

def test_gp208_launch_risk_blockers(gp201_210_db):
    payload = get_gp208_launch_risk_blocker_board(gp201_210_db)
    rows = payload["blockers"]

    assert payload["pack"]["id"] == "VAULT_GP208"
    assert payload["launch_risk_blocker_board"]["component_id"] == LAUNCH_RISK_BLOCKER_ID
    assert payload["launch_risk_blocker_count"] == len(LAUNCH_RISK_BLOCKERS)
    assert all(item["blocker_active"] is True for item in rows)
    assert all(item["blocks_beta_launch"] is True for item in rows)
    assert all(item["blocks_public_launch"] is True for item in rows)
    assert all(item["blocks_beta_access"] is True for item in rows)
    assert all(item["blocks_provider_unlock"] is True for item in rows)
    assert all(item["blocks_provider_api"] is True for item in rows)
    assert all(item["blocks_object_body"] is True for item in rows)
    assert all(item["blocks_download"] is True for item in rows)
    assert all(item["blocks_restore"] is True for item in rows)
    assert all(item["blocks_export"] is True for item in rows)
    assert all(item["blocks_direct_upload"] is True for item in rows)
    assert all(item["blocks_delete"] is True for item in rows)
    assert all(item["blocks_tower_unlock"] is True for item in rows)
    assert all(item["blocks_execution"] is True for item in rows)
    assert all(item["blocks_vault_done"] is True for item in rows)
    assert all(item["resolved"] is False for item in rows)

def test_gp209_receipt_packet(gp201_210_db):
    payload = get_gp209_owner_productization_receipt_packet(gp201_210_db)
    packets = payload["packets"]

    assert payload["pack"]["id"] == "VAULT_GP209"
    assert payload["receipt_packet_component"]["component_id"] == RECEIPT_PACKET_ID
    assert payload["receipt_packet_count"] == 1
    assert packets[0]["packet_ready"] is True
    assert packets[0]["packet_locked"] is True
    assert packets[0]["final_beta_launch_receipt"] is False
    assert packets[0]["beta_launch_approved"] is False
    assert packets[0]["vault_done"] is False
    assert len(packets[0]["packet_hash"]) == 64

def test_gp210_readiness_home_status_and_validation(gp201_210_db):
    payload = get_gp210_owner_productization_beta_readiness_checkpoint(gp201_210_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP210"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["beta_readiness_count"] == len(BETA_READINESS_ITEMS)
    assert readiness["surface_count"] == len(PRODUCT_SURFACES)
    assert readiness["access_lock_count"] == len(ACCESS_LOCK_ITEMS)
    assert readiness["copy_positioning_count"] == len(COPY_POSITIONING_ITEMS)
    assert readiness["support_feedback_count"] == len(SUPPORT_FEEDBACK_ITEMS)
    assert readiness["qa_scenario_count"] == len(QA_SCENARIOS)
    assert readiness["launch_risk_blocker_count"] == len(LAUNCH_RISK_BLOCKERS)
    assert readiness["receipt_packet_count"] == 1
    assert readiness["owner_productization_ready"] is True
    assert readiness["beta_readiness_prepared"] is True
    assert readiness["beta_launch_locked"] is True
    assert readiness["beta_access_locked"] is True
    assert readiness["safe_to_continue_to_gp211"] is True
    assert readiness["section_ready"] is True
    assert readiness["vault_done"] is False
    assert readiness["clouds_should_continue"] is False
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["owner_productization_ready"] is True
    assert validation["beta_readiness_prepared"] is True
    assert validation["safe_to_continue_to_gp211"] is True
    assert validation["vault_done"] is False

    status = get_gp210_status(gp201_210_db)["gp210_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp211"] is True
    assert status["owner_productization_ready"] is True
    assert status["beta_readiness_prepared"] is True
    assert status["beta_launch_locked"] is True
    assert status["beta_access_locked"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_BETA_ACCESS_AND_INVITE_LOCK_LAYER"
    assert status["next_section_range"] == "GP211-GP220"
    assert status["next_pack"] == "VAULT_GP211_220_BETA_ACCESS_AND_INVITE_LOCK_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp210"

    home = get_owner_productization_beta_readiness_layer_home(gp201_210_db)
    assert home["pack"]["id"] == "VAULT_GP201_210"
    assert home["truth"]["owner_productization_beta_readiness_layer_ready"] is True
    assert home["truth"]["owner_productization_ready"] is True
    assert home["truth"]["beta_readiness_prepared"] is True
    assert home["truth"]["safe_to_continue_to_gp211"] is True
    assert home["truth"]["beta_launch_locked"] is True
    assert home["truth"]["beta_access_locked"] is True
    assert home["truth"]["beta_launch_approved"] is False
    assert home["truth"]["public_launch_approved"] is False
    assert home["truth"]["beta_invite_created"] is False
    assert home["truth"]["beta_invite_sent"] is False
    assert home["truth"]["beta_tester_added"] is False
    assert home["truth"]["beta_tester_access_granted"] is False
    assert home["truth"]["billing_flow_created"] is False
    assert home["truth"]["subscription_flow_created"] is False
    assert home["truth"]["customer_portal_created"] is False
    assert home["truth"]["payment_processor_called"] is False
    assert home["truth"]["provider_unlock_requested"] is False
    assert home["truth"]["provider_api_called"] is False
    assert home["truth"]["provider_metadata_read"] is False
    assert home["truth"]["object_body_read"] is False
    assert home["truth"]["object_body_download_enabled"] is False
    assert home["truth"]["object_download_enabled"] is False
    assert home["truth"]["object_delete_executed"] is False
    assert home["truth"]["export_package_created"] is False
    assert home["truth"]["restore_job_created"] is False
    assert home["truth"]["direct_upload_enabled"] is False
    assert home["truth"]["tower_unlock_granted"] is False
    assert home["truth"]["owner_approval_recorded"] is False
    assert home["truth"]["execution_enabled"] is False
    assert home["truth"]["vault_done"] is False
    assert home["truth"]["clouds_should_continue"] is False

def test_gp201_210_all_status_endpoints(gp201_210_db):
    funcs = [
        (201, get_gp201_status, "gp201_status"),
        (202, get_gp202_status, "gp202_status"),
        (203, get_gp203_status, "gp203_status"),
        (204, get_gp204_status, "gp204_status"),
        (205, get_gp205_status, "gp205_status"),
        (206, get_gp206_status, "gp206_status"),
        (207, get_gp207_status, "gp207_status"),
        (208, get_gp208_status, "gp208_status"),
        (209, get_gp209_status, "gp209_status"),
        (210, get_gp210_status, "gp210_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp201_210_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp211"] is True
        assert status["source_gp200_readiness_score"] == 100
        assert len(status["source_gp200_readiness_hash"]) == 64
        assert status["component_count"] == 10
        assert status["beta_readiness_count"] == len(BETA_READINESS_ITEMS)
        assert status["surface_count"] == len(PRODUCT_SURFACES)
        assert status["launch_risk_blocker_count"] == len(LAUNCH_RISK_BLOCKERS)
        assert status["owner_productization_ready"] is True
        assert status["beta_readiness_prepared"] is True
        assert status["beta_launch_locked"] is True
        assert status["beta_access_locked"] is True
        assert status["vault_not_done"] is True
        assert status["owner_productization_approved"] is False
        assert status["beta_readiness_approved"] is False
        assert status["beta_launch_requested"] is False
        assert status["beta_launch_approved"] is False
        assert status["public_launch_requested"] is False
        assert status["public_launch_approved"] is False
        assert status["beta_invite_created"] is False
        assert status["beta_invite_sent"] is False
        assert status["beta_tester_added"] is False
        assert status["beta_tester_access_granted"] is False
        assert status["beta_access_token_created"] is False
        assert status["billing_flow_created"] is False
        assert status["subscription_flow_created"] is False
        assert status["customer_portal_created"] is False
        assert status["payment_processor_called"] is False
        assert status["provider_unlock_requested"] is False
        assert status["provider_unlock_approved"] is False
        assert status["provider_api_called"] is False
        assert status["provider_search_executed"] is False
        assert status["provider_metadata_read"] is False
        assert status["object_body_read"] is False
        assert status["object_body_view_enabled"] is False
        assert status["object_body_download_enabled"] is False
        assert status["object_body_plaintext_visible"] is False
        assert status["object_download_enabled"] is False
        assert status["object_delete_executed"] is False
        assert status["export_package_created"] is False
        assert status["restore_job_created"] is False
        assert status["provider_restore_api_called"] is False
        assert status["direct_upload_enabled"] is False
        assert status["tower_unlock_granted"] is False
        assert status["owner_approval_recorded"] is False
        assert status["execution_enabled"] is False
        assert status["product_marked_done"] is False
        assert status["vault_done"] is False

def test_gp201_210_html_is_dark_and_routes_registered(gp201_210_db):
    html = render_owner_productization_beta_readiness_layer_page()
    lowered = html.lower()
    assert "Vault GP201-GP210 Owner Productization Beta Readiness Layer" in html
    assert "GP201-GP210 built" in html
    assert "Beta readiness prepared" in html
    assert "Safe to GP211" in html
    assert "No beta launch" in html
    assert "No beta invite" in html
    assert "No beta access" in html
    assert "No billing flow" in html
    assert "No provider unlock" in html
    assert "No execution" in html
    assert "Vault not done" in html
    assert "VAULT_GP211_220_BETA_ACCESS_AND_INVITE_LOCK_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/owner-productization-beta-readiness-layer",
        "/vault/owner-productization-beta-readiness-layer.json",
        "/vault/owner-productization-shell.json",
        "/vault/beta-readiness-inventory.json",
        "/vault/owner-product-surface-map.json",
        "/vault/beta-tester-access-lock-board.json",
        "/vault/product-copy-positioning-board.json",
        "/vault/support-feedback-intake-plan.json",
        "/vault/beta-qa-scenario-board.json",
        "/vault/launch-risk-blocker-board.json",
        "/vault/owner-productization-receipt-packet.json",
        "/vault/owner-productization-beta-readiness-checkpoint.json",
        "/vault/gp201-status.json",
        "/vault/gp202-status.json",
        "/vault/gp203-status.json",
        "/vault/gp204-status.json",
        "/vault/gp205-status.json",
        "/vault/gp206-status.json",
        "/vault/gp207-status.json",
        "/vault/gp208-status.json",
        "/vault/gp209-status.json",
        "/vault/gp210-status.json",
    ]
    for route in required_routes:
        assert route in text
