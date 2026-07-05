"""
Tests for VAULT GP171-GP180 — Controlled Read-Only Metadata Test Layer
"""

from pathlib import Path
import pytest

from vault.controlled_read_only_metadata_test_layer_service import (
    APPROVAL_GATE_LOCK_ID,
    BLOCKER_BOARD_ID,
    BLOCKER_SPECS,
    BODY_DOWNLOAD_PROHIBITION_ID,
    FALSE_FIELDS,
    METADATA_SCOPE_CONTRACT_ID,
    METADATA_SCOPE_ITEMS,
    METADATA_TEST_SHELL_ID,
    PROHIBITION_ITEMS,
    QUERY_PLAN_LOCK_ID,
    QUERY_PLAN_STEPS,
    READINESS_ID,
    RECEIPT_DRAFT_LEDGER_ID,
    REQUEST_DRAFTS,
    REQUEST_DRAFT_REGISTRY_ID,
    RESULT_PLACEHOLDER_QUEUE_ID,
    RESULT_PLACEHOLDERS,
    ensure_controlled_read_only_metadata_test_layer_schema,
    get_gp171_controlled_read_only_metadata_test_shell,
    get_gp171_status,
    get_gp172_metadata_test_request_draft_registry,
    get_gp172_status,
    get_gp173_metadata_scope_contract,
    get_gp173_status,
    get_gp174_metadata_read_approval_gate_lock,
    get_gp174_status,
    get_gp175_metadata_query_plan_lock_contract,
    get_gp175_status,
    get_gp176_metadata_result_placeholder_queue,
    get_gp176_status,
    get_gp177_metadata_receipt_draft_ledger,
    get_gp177_status,
    get_gp178_object_body_download_prohibition_contract,
    get_gp178_status,
    get_gp179_controlled_metadata_test_blocker_board,
    get_gp179_status,
    get_gp180_controlled_metadata_test_readiness_checkpoint,
    get_gp180_status,
    get_controlled_read_only_metadata_test_layer_home,
    initialize_controlled_read_only_metadata_test_layer,
    render_controlled_read_only_metadata_test_layer_page,
    validate_controlled_read_only_metadata_test_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp171_180_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp171_180.sqlite")

def test_gp171_180_schema_and_initialize(gp171_180_db):
    schema = ensure_controlled_read_only_metadata_test_layer_schema(gp171_180_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_controlled_metadata_test_components" in schema["tables"]
    assert "vault_metadata_test_request_drafts" in schema["tables"]
    assert "vault_metadata_scope_items" in schema["tables"]
    assert "vault_controlled_metadata_test_readiness" in schema["tables"]

    result = initialize_controlled_read_only_metadata_test_layer(gp171_180_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["request_draft_count"] == len(REQUEST_DRAFTS)
    assert result["metadata_scope_count"] == len(METADATA_SCOPE_ITEMS)
    assert result["approval_gate_count"] == len(REQUEST_DRAFTS)
    assert result["query_plan_step_count"] == len(QUERY_PLAN_STEPS)
    assert result["result_placeholder_count"] == len(RESULT_PLACEHOLDERS)
    assert result["receipt_draft_count"] == len(REQUEST_DRAFTS)
    assert result["prohibition_count"] == len(PROHIBITION_ITEMS)
    assert result["blocker_count"] == len(BLOCKER_SPECS)
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp171_shell(gp171_180_db):
    payload = get_gp171_controlled_read_only_metadata_test_shell(gp171_180_db)
    shell = payload["metadata_test_shell"]

    assert payload["pack"]["id"] == "VAULT_GP171"
    assert shell["component_id"] == METADATA_TEST_SHELL_ID
    assert shell["gp_number"] == 171
    assert shell["source_gp170_readiness_score"] == 100
    assert len(shell["source_gp170_readiness_hash"]) == 64
    assert shell["component_ready"] is True
    assert shell["component_locked"] is True
    assert shell["metadata_test_locked"] is True
    assert shell["metadata_only"] is True
    assert shell["body_download_prohibited"] is True
    assert shell["no_provider_contact"] is True

    for field in FALSE_FIELDS:
        assert shell[field] is False

def test_gp172_request_drafts(gp171_180_db):
    payload = get_gp172_metadata_test_request_draft_registry(gp171_180_db)
    requests = payload["requests"]

    assert payload["pack"]["id"] == "VAULT_GP172"
    assert payload["request_draft_registry"]["component_id"] == REQUEST_DRAFT_REGISTRY_ID
    assert payload["request_draft_count"] == len(REQUEST_DRAFTS)
    assert all(item["request_draft_ready"] is True for item in requests)
    assert all(item["request_draft_locked"] is True for item in requests)
    assert all(item["metadata_test_locked"] is True for item in requests)
    assert all(item["metadata_only"] is True for item in requests)
    assert all(item["body_download_prohibited"] is True for item in requests)
    assert all(item["metadata_test_request_submitted"] is False for item in requests)
    assert all(item["metadata_test_request_approved"] is False for item in requests)

def test_gp173_metadata_scope(gp171_180_db):
    payload = get_gp173_metadata_scope_contract(gp171_180_db)
    scopes = payload["scopes"]

    assert payload["pack"]["id"] == "VAULT_GP173"
    assert payload["metadata_scope_contract"]["component_id"] == METADATA_SCOPE_CONTRACT_ID
    assert payload["metadata_scope_count"] == len(METADATA_SCOPE_ITEMS)
    assert all(item["scope_locked"] is True for item in scopes)
    assert all(item["metadata_only"] is True for item in scopes)
    assert all(item["body_download_prohibited"] is True for item in scopes)
    assert all(item["metadata_scope_activated"] is False for item in scopes)
    assert all(item["object_identifier_collected"] is False for item in scopes)
    assert all(item["object_body_read"] is False for item in scopes)

def test_gp174_approval_gates(gp171_180_db):
    payload = get_gp174_metadata_read_approval_gate_lock(gp171_180_db)
    gates = payload["gates"]

    assert payload["pack"]["id"] == "VAULT_GP174"
    assert payload["approval_gate_lock"]["component_id"] == APPROVAL_GATE_LOCK_ID
    assert payload["approval_gate_count"] == len(REQUEST_DRAFTS)
    assert all(item["approval_gate_locked"] is True for item in gates)
    assert all(item["tower_review_required"] is True for item in gates)
    assert all(item["owner_review_required"] is True for item in gates)
    assert all(item["metadata_read_approval_granted"] is False for item in gates)
    assert all(item["metadata_test_authorized"] is False for item in gates)

def test_gp175_query_plan(gp171_180_db):
    payload = get_gp175_metadata_query_plan_lock_contract(gp171_180_db)
    steps = payload["steps"]

    assert payload["pack"]["id"] == "VAULT_GP175"
    assert payload["query_plan_lock_contract"]["component_id"] == QUERY_PLAN_LOCK_ID
    assert payload["query_plan_step_count"] == len(QUERY_PLAN_STEPS)
    assert all(item["query_plan_locked"] is True for item in steps)
    assert all(item["metadata_test_locked"] is True for item in steps)
    assert all(item["metadata_query_executed"] is False for item in steps)
    assert all(item["provider_api_called"] is False for item in steps)
    assert all(item["provider_metadata_read"] is False for item in steps)
    assert all(item["object_body_read"] is False for item in steps)

def test_gp176_results(gp171_180_db):
    payload = get_gp176_metadata_result_placeholder_queue(gp171_180_db)
    results = payload["results"]

    assert payload["pack"]["id"] == "VAULT_GP176"
    assert payload["result_placeholder_queue"]["component_id"] == RESULT_PLACEHOLDER_QUEUE_ID
    assert payload["result_placeholder_count"] == len(RESULT_PLACEHOLDERS)
    assert all(item["result_placeholder_locked"] is True for item in results)
    assert all(item["no_provider_result"] is True for item in results)
    assert all(item["metadata_test_result_recorded"] is False for item in results)
    assert all(item["metadata_query_result_imported"] is False for item in results)
    assert all(item["provider_metadata_imported"] is False for item in results)

def test_gp177_receipts(gp171_180_db):
    payload = get_gp177_metadata_receipt_draft_ledger(gp171_180_db)
    receipts = payload["receipt_drafts"]

    assert payload["pack"]["id"] == "VAULT_GP177"
    assert payload["receipt_draft_ledger"]["component_id"] == RECEIPT_DRAFT_LEDGER_ID
    assert payload["receipt_draft_count"] == len(REQUEST_DRAFTS)
    assert all(item["receipt_draft_locked"] is True for item in receipts)
    assert all(item["final_receipt_created"] is False for item in receipts)
    assert all(item["metadata_test_receipt_finalized"] is False for item in receipts)
    assert all(item["metadata_test_receipt_persisted"] is False for item in receipts)

def test_gp178_prohibitions(gp171_180_db):
    payload = get_gp178_object_body_download_prohibition_contract(gp171_180_db)
    prohibitions = payload["prohibitions"]

    assert payload["pack"]["id"] == "VAULT_GP178"
    assert payload["object_body_download_prohibition_contract"]["component_id"] == BODY_DOWNLOAD_PROHIBITION_ID
    assert payload["prohibition_count"] == len(PROHIBITION_ITEMS)
    assert all(item["prohibition_active"] is True for item in prohibitions)
    assert all(item["object_body_read"] is False for item in prohibitions)
    assert all(item["object_body_view_enabled"] is False for item in prohibitions)
    assert all(item["object_body_download_enabled"] is False for item in prohibitions)
    assert all(item["object_body_plaintext_visible"] is False for item in prohibitions)
    assert all(item["object_download_enabled"] is False for item in prohibitions)
    assert all(item["object_delete_executed"] is False for item in prohibitions)

def test_gp179_blockers(gp171_180_db):
    payload = get_gp179_controlled_metadata_test_blocker_board(gp171_180_db)
    blockers = payload["blockers"]

    assert payload["pack"]["id"] == "VAULT_GP179"
    assert payload["blocker_board"]["component_id"] == BLOCKER_BOARD_ID
    assert payload["blocker_count"] == len(BLOCKER_SPECS)
    assert all(item["blocker_active"] is True for item in blockers)
    assert all(item["blocks_request_submit"] is True for item in blockers)
    assert all(item["blocks_metadata_approval"] is True for item in blockers)
    assert all(item["blocks_metadata_query"] is True for item in blockers)
    assert all(item["blocks_provider_api"] is True for item in blockers)
    assert all(item["blocks_metadata_read"] is True for item in blockers)
    assert all(item["blocks_object_body"] is True for item in blockers)
    assert all(item["blocks_download"] is True for item in blockers)
    assert all(item["blocks_restore"] is True for item in blockers)
    assert all(item["blocks_export"] is True for item in blockers)
    assert all(item["blocks_direct_upload"] is True for item in blockers)
    assert all(item["blocks_delete"] is True for item in blockers)
    assert all(item["blocks_execution"] is True for item in blockers)
    assert all(item["blocks_vault_done"] is True for item in blockers)
    assert all(item["resolved"] is False for item in blockers)

def test_gp180_readiness_home_status_and_validation(gp171_180_db):
    payload = get_gp180_controlled_metadata_test_readiness_checkpoint(gp171_180_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP180"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["request_draft_count"] == len(REQUEST_DRAFTS)
    assert readiness["metadata_scope_count"] == len(METADATA_SCOPE_ITEMS)
    assert readiness["approval_gate_count"] == len(REQUEST_DRAFTS)
    assert readiness["query_plan_step_count"] == len(QUERY_PLAN_STEPS)
    assert readiness["result_placeholder_count"] == len(RESULT_PLACEHOLDERS)
    assert readiness["receipt_draft_count"] == len(REQUEST_DRAFTS)
    assert readiness["prohibition_count"] == len(PROHIBITION_ITEMS)
    assert readiness["blocker_count"] == len(BLOCKER_SPECS)
    assert readiness["safe_to_continue_to_gp181"] is True
    assert readiness["section_ready"] is True
    assert readiness["metadata_test_locked"] is True
    assert readiness["metadata_only"] is True
    assert readiness["body_download_prohibited"] is True
    assert readiness["no_provider_contact"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp181"] is True
    assert validation["vault_done"] is False

    status = get_gp180_status(gp171_180_db)["gp180_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp181"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_REAL_ARCHIVE_INDEX_AND_SEARCH_LAYER"
    assert status["next_section_range"] == "GP181-GP190"
    assert status["next_pack"] == "VAULT_GP181_190_REAL_ARCHIVE_INDEX_AND_SEARCH_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp180"

    home = get_controlled_read_only_metadata_test_layer_home(gp171_180_db)
    assert home["pack"]["id"] == "VAULT_GP171_180"
    assert home["truth"]["controlled_read_only_metadata_test_layer_ready"] is True
    assert home["truth"]["metadata_test_locked"] is True
    assert home["truth"]["metadata_only"] is True
    assert home["truth"]["body_download_prohibited"] is True
    assert home["truth"]["safe_to_continue_to_gp181"] is True
    assert home["truth"]["no_provider_contact"] is True
    assert home["truth"]["metadata_test_request_submitted"] is False
    assert home["truth"]["metadata_test_request_approved"] is False
    assert home["truth"]["metadata_read_approval_granted"] is False
    assert home["truth"]["metadata_test_run_started"] is False
    assert home["truth"]["metadata_query_executed"] is False
    assert home["truth"]["provider_metadata_read"] is False
    assert home["truth"]["object_body_read"] is False
    assert home["truth"]["object_body_download_enabled"] is False
    assert home["truth"]["object_download_enabled"] is False
    assert home["truth"]["object_delete_executed"] is False
    assert home["truth"]["export_package_created"] is False
    assert home["truth"]["restore_job_created"] is False
    assert home["truth"]["direct_upload_enabled"] is False
    assert home["truth"]["execution_enabled"] is False
    assert home["truth"]["vault_done"] is False
    assert home["truth"]["clouds_should_continue"] is False

def test_gp171_180_all_status_endpoints(gp171_180_db):
    funcs = [
        (171, get_gp171_status, "gp171_status"),
        (172, get_gp172_status, "gp172_status"),
        (173, get_gp173_status, "gp173_status"),
        (174, get_gp174_status, "gp174_status"),
        (175, get_gp175_status, "gp175_status"),
        (176, get_gp176_status, "gp176_status"),
        (177, get_gp177_status, "gp177_status"),
        (178, get_gp178_status, "gp178_status"),
        (179, get_gp179_status, "gp179_status"),
        (180, get_gp180_status, "gp180_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp171_180_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp181"] is True
        assert status["source_gp170_readiness_score"] == 100
        assert len(status["source_gp170_readiness_hash"]) == 64
        assert status["component_count"] == 10
        assert status["request_draft_count"] == len(REQUEST_DRAFTS)
        assert status["metadata_scope_count"] == len(METADATA_SCOPE_ITEMS)
        assert status["blocker_count"] == len(BLOCKER_SPECS)
        assert status["metadata_test_locked"] is True
        assert status["metadata_only"] is True
        assert status["body_download_prohibited"] is True
        assert status["no_provider_contact"] is True
        assert status["metadata_test_request_submitted"] is False
        assert status["metadata_test_request_approved"] is False
        assert status["metadata_test_run_started"] is False
        assert status["metadata_query_executed"] is False
        assert status["real_provider_connection_started"] is False
        assert status["provider_api_called"] is False
        assert status["provider_token_created"] is False
        assert status["provider_session_created"] is False
        assert status["provider_job_reference_created"] is False
        assert status["provider_status_poll_started"] is False
        assert status["provider_endpoint_called"] is False
        assert status["provider_objects_listed"] is False
        assert status["provider_metadata_imported"] is False
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
        assert status["execution_enabled"] is False
        assert status["vault_done"] is False

def test_gp171_180_html_is_dark_and_routes_registered(gp171_180_db):
    html = render_controlled_read_only_metadata_test_layer_page()
    lowered = html.lower()
    assert "Vault GP171-GP180 Controlled Read-Only Metadata Test Layer" in html
    assert "GP171-GP180 built" in html
    assert "Metadata only" in html
    assert "Body/download prohibited" in html
    assert "Safe to GP181" in html
    assert "No metadata read" in html
    assert "No provider API" in html
    assert "No object body" in html
    assert "No download" in html
    assert "No restore/export/upload/delete" in html
    assert "No execution" in html
    assert "VAULT_GP181_190_REAL_ARCHIVE_INDEX_AND_SEARCH_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/controlled-read-only-metadata-test-layer",
        "/vault/controlled-read-only-metadata-test-layer.json",
        "/vault/controlled-read-only-metadata-test-shell.json",
        "/vault/metadata-test-request-draft-registry.json",
        "/vault/metadata-scope-contract.json",
        "/vault/metadata-read-approval-gate-lock.json",
        "/vault/metadata-query-plan-lock-contract.json",
        "/vault/metadata-result-placeholder-queue.json",
        "/vault/metadata-receipt-draft-ledger.json",
        "/vault/object-body-download-prohibition-contract.json",
        "/vault/controlled-metadata-test-blocker-board.json",
        "/vault/controlled-metadata-test-readiness-checkpoint.json",
        "/vault/gp171-status.json",
        "/vault/gp172-status.json",
        "/vault/gp173-status.json",
        "/vault/gp174-status.json",
        "/vault/gp175-status.json",
        "/vault/gp176-status.json",
        "/vault/gp177-status.json",
        "/vault/gp178-status.json",
        "/vault/gp179-status.json",
        "/vault/gp180-status.json",
    ]
    for route in required_routes:
        assert route in text
