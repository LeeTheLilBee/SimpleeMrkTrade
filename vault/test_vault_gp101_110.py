"""
Tests for VAULT GP101-GP110 — Real Provider Recovery Case Workspace Layer
"""

from pathlib import Path
import pytest

from vault.real_provider_recovery_case_workspace_layer_service import (
    BLOCKER_BOARD_ID,
    CASE_SPECS,
    DETAIL_ROOM_ID,
    EVIDENCE_LINK_MAP_ID,
    EXPORT_PREVIEW_ID,
    FALSE_FIELDS,
    OWNER_REVIEW_QUEUE_ID,
    READINESS_ID,
    RECEIPT_LEDGER_ID,
    REDACTED_OBJECT_VIEW_ID,
    RESTORE_PREVIEW_ID,
    WORKSPACE_INDEX_ID,
    ensure_recovery_case_workspace_layer_schema,
    get_gp101_recovery_case_workspace_index,
    get_gp101_status,
    get_gp102_recovery_case_receipt_ledger,
    get_gp102_status,
    get_gp103_recovery_case_owner_review_queue,
    get_gp103_status,
    get_gp104_recovery_case_detail_room,
    get_gp104_status,
    get_gp105_recovery_case_evidence_link_map,
    get_gp105_status,
    get_gp106_redacted_object_reference_view,
    get_gp106_status,
    get_gp107_export_package_lock_preview,
    get_gp107_status,
    get_gp108_restore_job_lock_preview,
    get_gp108_status,
    get_gp109_recovery_case_blocker_review_board,
    get_gp109_status,
    get_gp110_recovery_case_workspace_readiness_checkpoint,
    get_gp110_status,
    get_recovery_case_workspace_layer_home,
    initialize_recovery_case_workspace_layer,
    render_recovery_case_workspace_layer_page,
    validate_recovery_case_workspace_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp101_110_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp101_110.sqlite")

def test_gp101_110_schema_and_initialize(gp101_110_db):
    schema = ensure_recovery_case_workspace_layer_schema(gp101_110_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_recovery_case_workspace_components" in schema["tables"]
    assert "vault_recovery_case_workspace_cases" in schema["tables"]
    assert "vault_recovery_case_workspace_receipts" in schema["tables"]
    assert "vault_recovery_case_owner_review_queue" in schema["tables"]
    assert "vault_recovery_case_evidence_links" in schema["tables"]
    assert "vault_recovery_case_redacted_object_references" in schema["tables"]
    assert "vault_recovery_case_blockers" in schema["tables"]
    assert "vault_recovery_case_workspace_readiness" in schema["tables"]

    result = initialize_recovery_case_workspace_layer(gp101_110_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["case_count"] == len(CASE_SPECS)
    assert result["receipt_count"] == len(CASE_SPECS) * 2
    assert result["owner_review_item_count"] == len(CASE_SPECS)
    assert result["evidence_link_count"] == len(CASE_SPECS) * 3
    assert result["redacted_object_reference_count"] == len(CASE_SPECS)
    assert result["blocker_count"] == len(CASE_SPECS) * 4
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp101_workspace_index(gp101_110_db):
    payload = get_gp101_recovery_case_workspace_index(gp101_110_db)
    component = payload["workspace_index"]
    assert payload["pack"]["id"] == "VAULT_GP101"
    assert component["component_id"] == WORKSPACE_INDEX_ID
    assert component["gp_number"] == 101
    assert component["section_range"] == "GP101-GP110"
    assert component["source_gp100_readiness_score"] == 100
    assert component["source_gp100_section_closed"] is True
    assert len(component["source_gp100_readiness_hash"]) == 64
    assert component["component_ready"] is True
    assert component["component_locked"] is True
    assert payload["case_count"] == len(CASE_SPECS)
    assert all(case["case_locked"] is True for case in payload["cases"])
    assert all(case["redacted_only"] is True for case in payload["cases"])
    for field in FALSE_FIELDS:
        assert component[field] is False

def test_gp102_receipt_ledger(gp101_110_db):
    payload = get_gp102_recovery_case_receipt_ledger(gp101_110_db)
    ledger = payload["receipt_ledger"]
    receipts = payload["receipts"]
    assert payload["pack"]["id"] == "VAULT_GP102"
    assert ledger["component_id"] == RECEIPT_LEDGER_ID
    assert ledger["gp_number"] == 102
    assert ledger["receipt_count"] == len(CASE_SPECS) * 2
    assert len(ledger["ledger_hash"]) == 64
    assert len(receipts) == len(CASE_SPECS) * 2
    assert all(len(item["receipt_hash"]) == 64 for item in receipts)
    assert all(item["receipt_locked"] is True for item in receipts)
    for receipt in receipts:
        for field in FALSE_FIELDS:
            assert receipt[field] is False

def test_gp103_owner_review_queue(gp101_110_db):
    payload = get_gp103_recovery_case_owner_review_queue(gp101_110_db)
    queue = payload["items"]
    assert payload["pack"]["id"] == "VAULT_GP103"
    assert payload["owner_review_queue"]["component_id"] == OWNER_REVIEW_QUEUE_ID
    assert payload["owner_review_item_count"] == len(CASE_SPECS)
    assert all(item["owner_review_required"] is True for item in queue)
    assert all(item["tower_review_required"] is True for item in queue)
    assert all(item["review_locked"] is True for item in queue)
    for item in queue:
        assert item["owner_decision_recorded"] is False
        assert item["owner_approval_recorded"] is False
        assert item["owner_rejection_recorded"] is False
        assert item["tower_unlock_granted"] is False

def test_gp104_detail_room(gp101_110_db):
    payload = get_gp104_recovery_case_detail_room(gp101_110_db)
    assert payload["pack"]["id"] == "VAULT_GP104"
    assert payload["detail_room"]["component_id"] == DETAIL_ROOM_ID
    assert payload["detail_room_count"] == len(CASE_SPECS)
    for room in payload["detail_rooms"]:
        assert room["detail_room_status"] == "READY_LOCKED_REDACTED_ONLY"
        assert "object_body" in room["blocked_sections"]
        assert "download" in room["blocked_sections"]
        assert "export" in room["blocked_sections"]
        assert "restore" in room["blocked_sections"]
        assert "provider_api" in room["blocked_sections"]
        assert room["vault_done"] is False

def test_gp105_evidence_link_map(gp101_110_db):
    payload = get_gp105_recovery_case_evidence_link_map(gp101_110_db)
    links = payload["evidence_links"]
    assert payload["pack"]["id"] == "VAULT_GP105"
    assert payload["evidence_link_map"]["component_id"] == EVIDENCE_LINK_MAP_ID
    assert payload["evidence_link_count"] == len(CASE_SPECS) * 3
    assert all(item["evidence_locked"] is True for item in links)
    assert all(item["redacted_only"] is True for item in links)
    assert all(len(item["evidence_hash"]) == 64 for item in links)
    for item in links:
        assert item["object_body_read"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp106_redacted_object_reference_view(gp101_110_db):
    payload = get_gp106_redacted_object_reference_view(gp101_110_db)
    refs = payload["object_references"]
    assert payload["pack"]["id"] == "VAULT_GP106"
    assert payload["redacted_object_reference_view"]["component_id"] == REDACTED_OBJECT_VIEW_ID
    assert payload["redacted_object_reference_count"] == len(CASE_SPECS)
    assert all(item["redacted_only"] is True for item in refs)
    assert all(item["body_locked"] is True for item in refs)
    assert all(item["download_locked"] is True for item in refs)
    assert all(item["object_body_read"] is False for item in refs)
    assert all(item["object_body_view_enabled"] is False for item in refs)
    assert all(item["object_body_download_enabled"] is False for item in refs)
    assert all(item["object_body_plaintext_visible"] is False for item in refs)

def test_gp107_export_preview(gp101_110_db):
    payload = get_gp107_export_package_lock_preview(gp101_110_db)
    assert payload["pack"]["id"] == "VAULT_GP107"
    assert payload["export_package_lock_preview"]["component_id"] == EXPORT_PREVIEW_ID
    assert payload["preview_count"] == len(CASE_SPECS)
    for preview in payload["previews"]:
        assert preview["export_preview_status"] == "LOCKED_PREVIEW_ONLY"
        assert preview["export_package_created"] is False
        assert preview["export_manifest_created"] is False
        assert preview["export_download_enabled"] is False

def test_gp108_restore_preview(gp101_110_db):
    payload = get_gp108_restore_job_lock_preview(gp101_110_db)
    assert payload["pack"]["id"] == "VAULT_GP108"
    assert payload["restore_job_lock_preview"]["component_id"] == RESTORE_PREVIEW_ID
    assert payload["preview_count"] == len(CASE_SPECS)
    for preview in payload["previews"]:
        assert preview["restore_preview_status"] == "LOCKED_PREVIEW_ONLY"
        assert preview["restore_request_created"] is False
        assert preview["restore_job_created"] is False
        assert preview["provider_restore_api_called"] is False

def test_gp109_blocker_board(gp101_110_db):
    payload = get_gp109_recovery_case_blocker_review_board(gp101_110_db)
    blockers = payload["blockers"]
    assert payload["pack"]["id"] == "VAULT_GP109"
    assert payload["blocker_review_board"]["component_id"] == BLOCKER_BOARD_ID
    assert payload["blocker_count"] == len(CASE_SPECS) * 4
    assert all(item["blocker_active"] is True for item in blockers)
    assert all(item["blocks_restore"] is True for item in blockers)
    assert all(item["blocks_export"] is True for item in blockers)
    assert all(item["blocks_provider_api"] is True for item in blockers)
    assert all(item["blocks_object_body"] is True for item in blockers)
    assert all(item["blocks_direct_upload"] is True for item in blockers)
    assert all(item["blocks_tower_unlock"] is True for item in blockers)
    assert all(item["blocks_execution"] is True for item in blockers)
    assert all(item["blocks_vault_done"] is True for item in blockers)
    assert all(item["resolved"] is False for item in blockers)

def test_gp110_readiness_status_home_and_validation(gp101_110_db):
    payload = get_gp110_recovery_case_workspace_readiness_checkpoint(gp101_110_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP110"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["case_count"] == len(CASE_SPECS)
    assert readiness["receipt_count"] == len(CASE_SPECS) * 2
    assert readiness["owner_review_item_count"] == len(CASE_SPECS)
    assert readiness["evidence_link_count"] == len(CASE_SPECS) * 3
    assert readiness["redacted_object_reference_count"] == len(CASE_SPECS)
    assert readiness["blocker_count"] == len(CASE_SPECS) * 4
    assert readiness["safe_to_continue_to_gp111"] is True
    assert readiness["section_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp111"] is True
    assert validation["vault_done"] is False

    status = get_gp110_status(gp101_110_db)["gp110_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp111"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_REDACTED_ARCHIVE_BROWSER_LAYER"
    assert status["next_section_range"] == "GP111-GP120"
    assert status["next_pack"] == "VAULT_GP111_120_REDACTED_ARCHIVE_BROWSER_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp110"

    home = get_recovery_case_workspace_layer_home(gp101_110_db)
    assert home["pack"]["id"] == "VAULT_GP101_110"
    assert home["truth"]["recovery_case_workspace_layer_ready"] is True
    assert home["truth"]["safe_to_continue_to_gp111"] is True
    assert home["truth"]["vault_done"] is False
    assert home["truth"]["clouds_should_continue"] is False
    assert home["truth"]["restore_request_submitted"] is False
    assert home["truth"]["restore_job_created"] is False
    assert home["truth"]["provider_restore_api_called"] is False
    assert home["truth"]["object_body_read"] is False
    assert home["truth"]["export_package_created"] is False
    assert home["truth"]["direct_upload_enabled"] is False
    assert home["truth"]["execution_enabled"] is False

def test_gp101_110_all_status_endpoints(gp101_110_db):
    funcs = [
        (101, get_gp101_status, "gp101_status"),
        (102, get_gp102_status, "gp102_status"),
        (103, get_gp103_status, "gp103_status"),
        (104, get_gp104_status, "gp104_status"),
        (105, get_gp105_status, "gp105_status"),
        (106, get_gp106_status, "gp106_status"),
        (107, get_gp107_status, "gp107_status"),
        (108, get_gp108_status, "gp108_status"),
        (109, get_gp109_status, "gp109_status"),
        (110, get_gp110_status, "gp110_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp101_110_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp111"] is True
        assert status["source_gp100_readiness_score"] == 100
        assert len(status["source_gp100_readiness_hash"]) == 64
        assert status["case_count"] == len(CASE_SPECS)
        assert status["receipt_count"] == len(CASE_SPECS) * 2
        assert status["blocker_count"] == len(CASE_SPECS) * 4
        assert status["case_restore_requested"] is False
        assert status["case_export_requested"] is False
        assert status["owner_decision_recorded"] is False
        assert status["owner_approval_recorded"] is False
        assert status["owner_rejection_recorded"] is False
        assert status["tower_unlock_granted"] is False
        assert status["restore_request_created"] is False
        assert status["restore_request_submitted"] is False
        assert status["restore_job_created"] is False
        assert status["provider_restore_api_called"] is False
        assert status["object_body_read"] is False
        assert status["object_body_view_enabled"] is False
        assert status["object_body_download_enabled"] is False
        assert status["object_body_plaintext_visible"] is False
        assert status["export_package_created"] is False
        assert status["export_manifest_created"] is False
        assert status["export_download_enabled"] is False
        assert status["direct_upload_enabled"] is False
        assert status["export_enabled"] is False
        assert status["execution_enabled"] is False
        assert status["vault_done"] is False

def test_gp101_110_html_is_dark_and_routes_registered(gp101_110_db):
    html = render_recovery_case_workspace_layer_page()
    lowered = html.lower()
    assert "Vault GP101-GP110 Recovery Case Workspace Layer" in html
    assert "GP101-GP110 built" in html
    assert "Recovery cases ready" in html
    assert "Redacted only" in html
    assert "Safe to GP111" in html
    assert "No restore" in html
    assert "No export" in html
    assert "No provider API" in html
    assert "No object body" in html
    assert "No execution" in html
    assert "VAULT_GP111_120_REDACTED_ARCHIVE_BROWSER_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/recovery-case-workspace-layer",
        "/vault/recovery-case-workspace-layer.json",
        "/vault/recovery-case-workspace-index.json",
        "/vault/recovery-case-receipt-ledger.json",
        "/vault/recovery-case-owner-review-queue.json",
        "/vault/recovery-case-detail-room.json",
        "/vault/recovery-case-evidence-link-map.json",
        "/vault/recovery-case-redacted-object-reference-view.json",
        "/vault/recovery-case-export-package-lock-preview.json",
        "/vault/recovery-case-restore-job-lock-preview.json",
        "/vault/recovery-case-blocker-review-board.json",
        "/vault/recovery-case-workspace-readiness-checkpoint.json",
        "/vault/gp101-status.json",
        "/vault/gp102-status.json",
        "/vault/gp103-status.json",
        "/vault/gp104-status.json",
        "/vault/gp105-status.json",
        "/vault/gp106-status.json",
        "/vault/gp107-status.json",
        "/vault/gp108-status.json",
        "/vault/gp109-status.json",
        "/vault/gp110-status.json",
    ]
    for route in required_routes:
        assert route in text
