"""
Tests for VAULT GP111-GP120 — Redacted Archive Browser Layer
"""

from pathlib import Path
import pytest

from vault.redacted_archive_browser_layer_service import (
    BROWSER_BLOCKER_BOARD_ID,
    BROWSER_SHELL_ID,
    CASE_LINK_VIEW_ID,
    FILTER_BOARD_ID,
    FOLDER_NAV_ID,
    FOLDER_SPECS,
    FILTER_SPECS,
    FALSE_FIELDS,
    METADATA_DRAWER_ID,
    OBJECT_CARDS_ID,
    PROOF_PACKET_BROWSER_ID,
    READINESS_ID,
    SEARCH_INDEX_ID,
    ensure_redacted_archive_browser_layer_schema,
    get_gp111_redacted_archive_browser_shell,
    get_gp111_status,
    get_gp112_business_lane_folder_navigation,
    get_gp112_status,
    get_gp113_redacted_archive_object_cards,
    get_gp113_status,
    get_gp114_archive_search_index,
    get_gp114_status,
    get_gp115_receipt_and_proof_packet_browser,
    get_gp115_status,
    get_gp116_case_to_archive_link_view,
    get_gp116_status,
    get_gp117_archive_filter_board,
    get_gp117_status,
    get_gp118_redacted_metadata_detail_drawer,
    get_gp118_status,
    get_gp119_archive_browser_blocker_board,
    get_gp119_status,
    get_gp120_redacted_archive_browser_readiness_checkpoint,
    get_gp120_status,
    get_redacted_archive_browser_layer_home,
    initialize_redacted_archive_browser_layer,
    render_redacted_archive_browser_layer_page,
    validate_redacted_archive_browser_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp111_120_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp111_120.sqlite")

def test_gp111_120_schema_and_initialize(gp111_120_db):
    schema = ensure_redacted_archive_browser_layer_schema(gp111_120_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_redacted_archive_browser_components" in schema["tables"]
    assert "vault_redacted_archive_folders" in schema["tables"]
    assert "vault_redacted_archive_object_cards" in schema["tables"]
    assert "vault_redacted_archive_search_index" in schema["tables"]
    assert "vault_redacted_archive_proof_packet_links" in schema["tables"]
    assert "vault_redacted_archive_case_links" in schema["tables"]
    assert "vault_redacted_archive_filters" in schema["tables"]
    assert "vault_redacted_archive_metadata_drawers" in schema["tables"]
    assert "vault_redacted_archive_browser_blockers" in schema["tables"]
    assert "vault_redacted_archive_browser_readiness" in schema["tables"]

    result = initialize_redacted_archive_browser_layer(gp111_120_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["folder_count"] == len(FOLDER_SPECS)
    assert result["object_card_count"] == 8
    assert result["search_index_count"] == 8
    assert result["proof_packet_count"] == 16
    assert result["case_link_count"] == 8
    assert result["filter_count"] == len(FILTER_SPECS)
    assert result["metadata_drawer_count"] == 8
    assert result["blocker_count"] == 32
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp111_browser_shell(gp111_120_db):
    payload = get_gp111_redacted_archive_browser_shell(gp111_120_db)
    shell = payload["browser_shell"]

    assert payload["pack"]["id"] == "VAULT_GP111"
    assert shell["component_id"] == BROWSER_SHELL_ID
    assert shell["gp_number"] == 111
    assert shell["section_range"] == "GP111-GP120"
    assert shell["source_gp110_readiness_score"] == 100
    assert len(shell["source_gp110_readiness_hash"]) == 64
    assert shell["component_ready"] is True
    assert shell["component_locked"] is True
    assert shell["redacted_only"] is True

    for field in FALSE_FIELDS:
        assert shell[field] is False

def test_gp112_folder_navigation(gp111_120_db):
    payload = get_gp112_business_lane_folder_navigation(gp111_120_db)
    folders = payload["folders"]

    assert payload["pack"]["id"] == "VAULT_GP112"
    assert payload["folder_navigation"]["component_id"] == FOLDER_NAV_ID
    assert payload["folder_count"] == len(FOLDER_SPECS)
    assert len(folders) == len(FOLDER_SPECS)
    assert {item["folder_code"] for item in folders} == {item[0] for item in FOLDER_SPECS}
    assert all(item["folder_ready"] is True for item in folders)
    assert all(item["folder_locked"] is True for item in folders)
    assert all(item["redacted_only"] is True for item in folders)
    for item in folders:
        for field in FALSE_FIELDS:
            assert item[field] is False

def test_gp113_redacted_object_cards(gp111_120_db):
    payload = get_gp113_redacted_archive_object_cards(gp111_120_db)
    cards = payload["cards"]

    assert payload["pack"]["id"] == "VAULT_GP113"
    assert payload["object_cards"]["component_id"] == OBJECT_CARDS_ID
    assert payload["object_card_count"] == 8
    assert all(item["object_card_ready"] is True for item in cards)
    assert all(item["object_card_locked"] is True for item in cards)
    assert all(item["redacted_only"] is True for item in cards)
    assert all(item["metadata_only"] is True for item in cards)
    assert all(len(item["object_card_hash"]) == 64 for item in cards)
    for item in cards:
        assert item["object_body_read"] is False
        assert item["object_body_view_enabled"] is False
        assert item["object_body_download_enabled"] is False
        assert item["object_body_plaintext_visible"] is False
        assert item["object_download_enabled"] is False
        assert item["export_package_created"] is False
        assert item["restore_request_created"] is False
        assert item["provider_api_called"] is False

def test_gp114_archive_search_index(gp111_120_db):
    payload = get_gp114_archive_search_index(gp111_120_db)
    search = payload["search_rows"]

    assert payload["pack"]["id"] == "VAULT_GP114"
    assert payload["search_index"]["component_id"] == SEARCH_INDEX_ID
    assert payload["search_index_count"] == 8
    assert all(item["redacted_only"] is True for item in search)
    assert all(item["metadata_only"] is True for item in search)
    assert all(item["search_scope"] == "REDACTED_METADATA_ONLY" for item in search)
    assert all(isinstance(item["search_terms"], list) and "redacted" in item["search_terms"] for item in search)
    for item in search:
        assert item["object_body_read"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp115_proof_packet_browser(gp111_120_db):
    payload = get_gp115_receipt_and_proof_packet_browser(gp111_120_db)
    proof = payload["proof_packet_links"]

    assert payload["pack"]["id"] == "VAULT_GP115"
    assert payload["proof_packet_browser"]["component_id"] == PROOF_PACKET_BROWSER_ID
    assert payload["proof_packet_count"] == 16
    assert all(item["proof_packet_locked"] is True for item in proof)
    assert all(item["redacted_only"] is True for item in proof)
    assert all(len(item["proof_packet_hash"]) == 64 for item in proof)
    for item in proof:
        assert item["export_package_created"] is False
        assert item["object_body_read"] is False
        assert item["provider_api_called"] is False

def test_gp116_case_link_view(gp111_120_db):
    payload = get_gp116_case_to_archive_link_view(gp111_120_db)
    links = payload["case_links"]

    assert payload["pack"]["id"] == "VAULT_GP116"
    assert payload["case_link_view"]["component_id"] == CASE_LINK_VIEW_ID
    assert payload["case_link_count"] == 8
    assert all(item["case_link_locked"] is True for item in links)
    assert all(item["redacted_only"] is True for item in links)
    assert all(item["evidence_link_count"] == 3 for item in links)
    assert all(item["receipt_link_count"] == 2 for item in links)
    assert all(len(item["case_link_hash"]) == 64 for item in links)

def test_gp117_filter_board(gp111_120_db):
    payload = get_gp117_archive_filter_board(gp111_120_db)
    filters = payload["filters"]

    assert payload["pack"]["id"] == "VAULT_GP117"
    assert payload["filter_board"]["component_id"] == FILTER_BOARD_ID
    assert payload["filter_count"] == len(FILTER_SPECS)
    assert all(item["filter_locked"] is True for item in filters)
    assert all(item["redacted_only"] is True for item in filters)
    assert {item["filter_code"] for item in filters} == {item[0] for item in FILTER_SPECS}

def test_gp118_metadata_detail_drawer(gp111_120_db):
    payload = get_gp118_redacted_metadata_detail_drawer(gp111_120_db)
    drawers = payload["drawers"]

    assert payload["pack"]["id"] == "VAULT_GP118"
    assert payload["metadata_detail_drawer"]["component_id"] == METADATA_DRAWER_ID
    assert payload["metadata_drawer_count"] == 8
    assert all(item["drawer_locked"] is True for item in drawers)
    assert all(item["redacted_only"] is True for item in drawers)
    assert all(item["metadata_only"] is True for item in drawers)
    for item in drawers:
        assert item["redacted_metadata"]["body"] == "LOCKED"
        assert item["redacted_metadata"]["download"] == "LOCKED"
        assert item["redacted_metadata"]["plaintext"] == "LOCKED"
        assert item["object_body_read"] is False
        assert item["object_body_view_enabled"] is False
        assert item["object_body_download_enabled"] is False
        assert item["object_body_plaintext_visible"] is False

def test_gp119_browser_blocker_board(gp111_120_db):
    payload = get_gp119_archive_browser_blocker_board(gp111_120_db)
    blockers = payload["blockers"]

    assert payload["pack"]["id"] == "VAULT_GP119"
    assert payload["browser_blocker_board"]["component_id"] == BROWSER_BLOCKER_BOARD_ID
    assert payload["blocker_count"] == 32
    assert all(item["blocker_active"] is True for item in blockers)
    assert all(item["blocks_provider_api"] is True for item in blockers)
    assert all(item["blocks_object_body"] is True for item in blockers)
    assert all(item["blocks_download"] is True for item in blockers)
    assert all(item["blocks_export"] is True for item in blockers)
    assert all(item["blocks_restore"] is True for item in blockers)
    assert all(item["blocks_direct_upload"] is True for item in blockers)
    assert all(item["blocks_tower_unlock"] is True for item in blockers)
    assert all(item["blocks_execution"] is True for item in blockers)
    assert all(item["blocks_vault_done"] is True for item in blockers)
    assert all(item["resolved"] is False for item in blockers)

def test_gp120_readiness_status_home_and_validation(gp111_120_db):
    payload = get_gp120_redacted_archive_browser_readiness_checkpoint(gp111_120_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP120"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["folder_count"] == len(FOLDER_SPECS)
    assert readiness["object_card_count"] == 8
    assert readiness["search_index_count"] == 8
    assert readiness["proof_packet_count"] == 16
    assert readiness["case_link_count"] == 8
    assert readiness["filter_count"] == len(FILTER_SPECS)
    assert readiness["metadata_drawer_count"] == 8
    assert readiness["blocker_count"] == 32
    assert readiness["safe_to_continue_to_gp121"] is True
    assert readiness["section_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp121"] is True
    assert validation["vault_done"] is False

    status = get_gp120_status(gp111_120_db)["gp120_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp121"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_OWNER_CONSOLE_AND_OPERATING_DASHBOARD_LAYER"
    assert status["next_section_range"] == "GP121-GP130"
    assert status["next_pack"] == "VAULT_GP121_130_OWNER_CONSOLE_AND_OPERATING_DASHBOARD_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp120"

    home = get_redacted_archive_browser_layer_home(gp111_120_db)
    assert home["pack"]["id"] == "VAULT_GP111_120"
    assert home["truth"]["redacted_archive_browser_layer_ready"] is True
    assert home["truth"]["safe_to_continue_to_gp121"] is True
    assert home["truth"]["redacted_only"] is True
    assert home["truth"]["metadata_only"] is True
    assert home["truth"]["provider_api_called"] is False
    assert home["truth"]["provider_objects_listed"] is False
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

def test_gp111_120_all_status_endpoints(gp111_120_db):
    funcs = [
        (111, get_gp111_status, "gp111_status"),
        (112, get_gp112_status, "gp112_status"),
        (113, get_gp113_status, "gp113_status"),
        (114, get_gp114_status, "gp114_status"),
        (115, get_gp115_status, "gp115_status"),
        (116, get_gp116_status, "gp116_status"),
        (117, get_gp117_status, "gp117_status"),
        (118, get_gp118_status, "gp118_status"),
        (119, get_gp119_status, "gp119_status"),
        (120, get_gp120_status, "gp120_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp111_120_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp121"] is True
        assert status["source_gp110_readiness_score"] == 100
        assert len(status["source_gp110_readiness_hash"]) == 64
        assert status["folder_count"] == len(FOLDER_SPECS)
        assert status["object_card_count"] == 8
        assert status["search_index_count"] == 8
        assert status["proof_packet_count"] == 16
        assert status["blocker_count"] == 32
        assert status["provider_api_called"] is False
        assert status["provider_objects_listed"] is False
        assert status["provider_metadata_read"] is False
        assert status["object_body_read"] is False
        assert status["object_body_view_enabled"] is False
        assert status["object_body_download_enabled"] is False
        assert status["object_body_plaintext_visible"] is False
        assert status["object_download_enabled"] is False
        assert status["export_package_created"] is False
        assert status["export_manifest_created"] is False
        assert status["export_download_enabled"] is False
        assert status["restore_request_created"] is False
        assert status["restore_job_created"] is False
        assert status["provider_restore_api_called"] is False
        assert status["direct_upload_enabled"] is False
        assert status["tower_unlock_granted"] is False
        assert status["execution_enabled"] is False
        assert status["vault_done"] is False

def test_gp111_120_html_is_dark_and_routes_registered(gp111_120_db):
    html = render_redacted_archive_browser_layer_page()
    lowered = html.lower()
    assert "Vault GP111-GP120 Redacted Archive Browser Layer" in html
    assert "GP111-GP120 built" in html
    assert "Browser ready" in html
    assert "Redacted only" in html
    assert "Safe to GP121" in html
    assert "No body read" in html
    assert "No download" in html
    assert "No export" in html
    assert "No restore" in html
    assert "No provider API" in html
    assert "VAULT_GP121_130_OWNER_CONSOLE_AND_OPERATING_DASHBOARD_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/redacted-archive-browser-layer",
        "/vault/redacted-archive-browser-layer.json",
        "/vault/redacted-archive-browser-shell.json",
        "/vault/redacted-archive-folder-navigation.json",
        "/vault/redacted-archive-object-cards.json",
        "/vault/redacted-archive-search-index.json",
        "/vault/redacted-archive-proof-packet-browser.json",
        "/vault/redacted-archive-case-link-view.json",
        "/vault/redacted-archive-filter-board.json",
        "/vault/redacted-archive-metadata-detail-drawer.json",
        "/vault/redacted-archive-browser-blocker-board.json",
        "/vault/redacted-archive-browser-readiness-checkpoint.json",
        "/vault/gp111-status.json",
        "/vault/gp112-status.json",
        "/vault/gp113-status.json",
        "/vault/gp114-status.json",
        "/vault/gp115-status.json",
        "/vault/gp116-status.json",
        "/vault/gp117-status.json",
        "/vault/gp118-status.json",
        "/vault/gp119-status.json",
        "/vault/gp120-status.json",
    ]
    for route in required_routes:
        assert route in text
