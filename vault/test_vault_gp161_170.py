"""
Tests for VAULT GP161-GP170 — Controlled Provider Connection Test Lock Layer
"""

from pathlib import Path
import pytest

from vault.controlled_provider_connection_test_lock_layer_service import (
    APPROVAL_GATE_LOCK_ID,
    BLOCKER_BOARD_ID,
    BLOCKER_SPECS,
    DENIAL_REASON_BOARD_ID,
    DENIAL_REASONS,
    EMERGENCY_STOP_LOCK_ID,
    EMERGENCY_STOP_LOCKS,
    FALSE_FIELDS,
    LOCK_SHELL_ID,
    READINESS_ID,
    RECEIPT_DRAFT_LEDGER_ID,
    REQUEST_DRAFT_REGISTRY_ID,
    REQUEST_DRAFTS,
    RESULT_PLACEHOLDER_QUEUE_ID,
    RESULT_PLACEHOLDERS,
    RUN_PLAN_LOCK_ID,
    RUN_PLAN_STEPS,
    ensure_controlled_provider_connection_test_lock_layer_schema,
    get_gp161_controlled_connection_test_lock_shell,
    get_gp161_status,
    get_gp162_connection_test_request_draft_registry,
    get_gp162_status,
    get_gp163_connection_test_approval_gate_lock_contract,
    get_gp163_status,
    get_gp164_connection_test_denial_reason_board,
    get_gp164_status,
    get_gp165_connection_test_run_plan_lock_contract,
    get_gp165_status,
    get_gp166_connection_test_receipt_draft_ledger,
    get_gp166_status,
    get_gp167_connection_test_result_placeholder_queue,
    get_gp167_status,
    get_gp168_connection_test_emergency_stop_lock,
    get_gp168_status,
    get_gp169_controlled_connection_test_blocker_board,
    get_gp169_status,
    get_gp170_controlled_connection_test_readiness_checkpoint,
    get_gp170_status,
    get_controlled_provider_connection_test_lock_layer_home,
    initialize_controlled_provider_connection_test_lock_layer,
    render_controlled_provider_connection_test_lock_layer_page,
    validate_controlled_provider_connection_test_lock_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp161_170_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp161_170.sqlite")

def test_gp161_170_schema_and_initialize(gp161_170_db):
    schema = ensure_controlled_provider_connection_test_lock_layer_schema(gp161_170_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_controlled_connection_test_components" in schema["tables"]
    assert "vault_connection_test_request_drafts" in schema["tables"]
    assert "vault_connection_test_approval_gates" in schema["tables"]
    assert "vault_controlled_connection_test_readiness" in schema["tables"]

    result = initialize_controlled_provider_connection_test_lock_layer(gp161_170_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["request_draft_count"] == len(REQUEST_DRAFTS)
    assert result["approval_gate_count"] == len(REQUEST_DRAFTS)
    assert result["denial_reason_count"] == len(DENIAL_REASONS)
    assert result["run_plan_step_count"] == len(RUN_PLAN_STEPS)
    assert result["receipt_draft_count"] == len(REQUEST_DRAFTS)
    assert result["result_placeholder_count"] == len(RESULT_PLACEHOLDERS)
    assert result["emergency_stop_lock_count"] == len(EMERGENCY_STOP_LOCKS)
    assert result["blocker_count"] == len(BLOCKER_SPECS)
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp161_lock_shell(gp161_170_db):
    payload = get_gp161_controlled_connection_test_lock_shell(gp161_170_db)
    shell = payload["lock_shell"]

    assert payload["pack"]["id"] == "VAULT_GP161"
    assert shell["component_id"] == LOCK_SHELL_ID
    assert shell["gp_number"] == 161
    assert shell["source_gp160_readiness_score"] == 100
    assert len(shell["source_gp160_readiness_hash"]) == 64
    assert shell["component_ready"] is True
    assert shell["component_locked"] is True
    assert shell["controlled_test_locked"] is True
    assert shell["no_provider_contact"] is True

    for field in FALSE_FIELDS:
        assert shell[field] is False

def test_gp162_request_drafts(gp161_170_db):
    payload = get_gp162_connection_test_request_draft_registry(gp161_170_db)
    requests = payload["requests"]

    assert payload["pack"]["id"] == "VAULT_GP162"
    assert payload["request_draft_registry"]["component_id"] == REQUEST_DRAFT_REGISTRY_ID
    assert payload["request_draft_count"] == len(REQUEST_DRAFTS)
    assert all(item["request_draft_ready"] is True for item in requests)
    assert all(item["request_draft_locked"] is True for item in requests)
    assert all(item["controlled_test_locked"] is True for item in requests)
    assert all(item["no_provider_contact"] is True for item in requests)
    assert all(item["connection_test_request_submitted"] is False for item in requests)
    assert all(item["connection_test_request_approved"] is False for item in requests)

def test_gp163_approval_gates(gp161_170_db):
    payload = get_gp163_connection_test_approval_gate_lock_contract(gp161_170_db)
    gates = payload["gates"]

    assert payload["pack"]["id"] == "VAULT_GP163"
    assert payload["approval_gate_lock_contract"]["component_id"] == APPROVAL_GATE_LOCK_ID
    assert payload["approval_gate_count"] == len(REQUEST_DRAFTS)
    assert all(item["approval_gate_locked"] is True for item in gates)
    assert all(item["tower_review_required"] is True for item in gates)
    assert all(item["owner_review_required"] is True for item in gates)
    assert all(item["connection_test_approval_granted"] is False for item in gates)
    assert all(item["connection_test_run_authorized"] is False for item in gates)

def test_gp164_denial_reasons(gp161_170_db):
    payload = get_gp164_connection_test_denial_reason_board(gp161_170_db)
    denials = payload["denial_reasons"]

    assert payload["pack"]["id"] == "VAULT_GP164"
    assert payload["denial_reason_board"]["component_id"] == DENIAL_REASON_BOARD_ID
    assert payload["denial_reason_count"] == len(DENIAL_REASONS)
    assert all(item["denial_active"] is True for item in denials)
    assert all(item["connection_test_request_denied_final"] is False for item in denials)

def test_gp165_run_plan(gp161_170_db):
    payload = get_gp165_connection_test_run_plan_lock_contract(gp161_170_db)
    steps = payload["steps"]

    assert payload["pack"]["id"] == "VAULT_GP165"
    assert payload["run_plan_lock_contract"]["component_id"] == RUN_PLAN_LOCK_ID
    assert payload["run_plan_step_count"] == len(RUN_PLAN_STEPS)
    assert all(item["run_plan_locked"] is True for item in steps)
    assert all(item["controlled_test_locked"] is True for item in steps)
    assert all(item["connection_test_run_started"] is False for item in steps)
    assert all(item["connection_test_run_completed"] is False for item in steps)
    assert all(item["provider_api_called"] is False for item in steps)

def test_gp166_receipts(gp161_170_db):
    payload = get_gp166_connection_test_receipt_draft_ledger(gp161_170_db)
    receipts = payload["receipt_drafts"]

    assert payload["pack"]["id"] == "VAULT_GP166"
    assert payload["receipt_draft_ledger"]["component_id"] == RECEIPT_DRAFT_LEDGER_ID
    assert payload["receipt_draft_count"] == len(REQUEST_DRAFTS)
    assert all(item["receipt_draft_locked"] is True for item in receipts)
    assert all(item["final_receipt_created"] is False for item in receipts)
    assert all(item["connection_test_receipt_finalized"] is False for item in receipts)
    assert all(item["connection_test_receipt_persisted"] is False for item in receipts)

def test_gp167_result_placeholders(gp161_170_db):
    payload = get_gp167_connection_test_result_placeholder_queue(gp161_170_db)
    results = payload["results"]

    assert payload["pack"]["id"] == "VAULT_GP167"
    assert payload["result_placeholder_queue"]["component_id"] == RESULT_PLACEHOLDER_QUEUE_ID
    assert payload["result_placeholder_count"] == len(RESULT_PLACEHOLDERS)
    assert all(item["result_placeholder_locked"] is True for item in results)
    assert all(item["no_provider_result"] is True for item in results)
    assert all(item["connection_test_result_recorded"] is False for item in results)
    assert all(item["provider_status_poll_completed"] is False for item in results)

def test_gp168_emergency_stop_locks(gp161_170_db):
    payload = get_gp168_connection_test_emergency_stop_lock(gp161_170_db)
    stops = payload["stops"]

    assert payload["pack"]["id"] == "VAULT_GP168"
    assert payload["emergency_stop_lock"]["component_id"] == EMERGENCY_STOP_LOCK_ID
    assert payload["emergency_stop_lock_count"] == len(EMERGENCY_STOP_LOCKS)
    assert all(item["emergency_stop_locked"] is True for item in stops)
    assert all(item["connection_test_emergency_stop_triggered"] is False for item in stops)
    assert all(item["connection_test_emergency_stop_released"] is False for item in stops)

def test_gp169_blockers(gp161_170_db):
    payload = get_gp169_controlled_connection_test_blocker_board(gp161_170_db)
    blockers = payload["blockers"]

    assert payload["pack"]["id"] == "VAULT_GP169"
    assert payload["blocker_board"]["component_id"] == BLOCKER_BOARD_ID
    assert payload["blocker_count"] == len(BLOCKER_SPECS)
    assert all(item["blocker_active"] is True for item in blockers)
    assert all(item["blocks_request_submit"] is True for item in blockers)
    assert all(item["blocks_approval"] is True for item in blockers)
    assert all(item["blocks_run_start"] is True for item in blockers)
    assert all(item["blocks_real_connection"] is True for item in blockers)
    assert all(item["blocks_provider_api"] is True for item in blockers)
    assert all(item["blocks_provider_token"] is True for item in blockers)
    assert all(item["blocks_provider_session"] is True for item in blockers)
    assert all(item["blocks_provider_job"] is True for item in blockers)
    assert all(item["blocks_status_poll"] is True for item in blockers)
    assert all(item["blocks_health_call"] is True for item in blockers)
    assert all(item["blocks_secret_read"] is True for item in blockers)
    assert all(item["blocks_endpoint_call"] is True for item in blockers)
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

def test_gp170_readiness_home_status_and_validation(gp161_170_db):
    payload = get_gp170_controlled_connection_test_readiness_checkpoint(gp161_170_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP170"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["request_draft_count"] == len(REQUEST_DRAFTS)
    assert readiness["approval_gate_count"] == len(REQUEST_DRAFTS)
    assert readiness["denial_reason_count"] == len(DENIAL_REASONS)
    assert readiness["run_plan_step_count"] == len(RUN_PLAN_STEPS)
    assert readiness["receipt_draft_count"] == len(REQUEST_DRAFTS)
    assert readiness["result_placeholder_count"] == len(RESULT_PLACEHOLDERS)
    assert readiness["emergency_stop_lock_count"] == len(EMERGENCY_STOP_LOCKS)
    assert readiness["blocker_count"] == len(BLOCKER_SPECS)
    assert readiness["safe_to_continue_to_gp171"] is True
    assert readiness["section_ready"] is True
    assert readiness["controlled_test_locked"] is True
    assert readiness["no_provider_contact"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp171"] is True
    assert validation["vault_done"] is False

    status = get_gp170_status(gp161_170_db)["gp170_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp171"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_CONTROLLED_READ_ONLY_METADATA_TEST_LAYER"
    assert status["next_section_range"] == "GP171-GP180"
    assert status["next_pack"] == "VAULT_GP171_180_CONTROLLED_READ_ONLY_METADATA_TEST_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp170"

    home = get_controlled_provider_connection_test_lock_layer_home(gp161_170_db)
    assert home["pack"]["id"] == "VAULT_GP161_170"
    assert home["truth"]["controlled_provider_connection_test_lock_layer_ready"] is True
    assert home["truth"]["controlled_test_locked"] is True
    assert home["truth"]["safe_to_continue_to_gp171"] is True
    assert home["truth"]["no_provider_contact"] is True
    assert home["truth"]["connection_test_request_submitted"] is False
    assert home["truth"]["connection_test_request_approved"] is False
    assert home["truth"]["connection_test_approval_granted"] is False
    assert home["truth"]["connection_test_run_authorized"] is False
    assert home["truth"]["connection_test_run_started"] is False
    assert home["truth"]["connection_test_run_completed"] is False
    assert home["truth"]["connection_test_result_recorded"] is False
    assert home["truth"]["connection_test_receipt_finalized"] is False
    assert home["truth"]["real_provider_connection_started"] is False
    assert home["truth"]["provider_api_called"] is False
    assert home["truth"]["provider_token_created"] is False
    assert home["truth"]["provider_session_created"] is False
    assert home["truth"]["provider_job_reference_created"] is False
    assert home["truth"]["provider_status_poll_started"] is False
    assert home["truth"]["provider_health_checked"] is False
    assert home["truth"]["provider_credential_value_read"] is False
    assert home["truth"]["provider_secret_value_read"] is False
    assert home["truth"]["provider_endpoint_called"] is False
    assert home["truth"]["provider_objects_listed"] is False
    assert home["truth"]["object_body_read"] is False
    assert home["truth"]["export_package_created"] is False
    assert home["truth"]["restore_job_created"] is False
    assert home["truth"]["direct_upload_enabled"] is False
    assert home["truth"]["tower_unlock_granted"] is False
    assert home["truth"]["execution_enabled"] is False
    assert home["truth"]["vault_done"] is False
    assert home["truth"]["clouds_should_continue"] is False

def test_gp161_170_all_status_endpoints(gp161_170_db):
    funcs = [
        (161, get_gp161_status, "gp161_status"),
        (162, get_gp162_status, "gp162_status"),
        (163, get_gp163_status, "gp163_status"),
        (164, get_gp164_status, "gp164_status"),
        (165, get_gp165_status, "gp165_status"),
        (166, get_gp166_status, "gp166_status"),
        (167, get_gp167_status, "gp167_status"),
        (168, get_gp168_status, "gp168_status"),
        (169, get_gp169_status, "gp169_status"),
        (170, get_gp170_status, "gp170_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp161_170_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp171"] is True
        assert status["source_gp160_readiness_score"] == 100
        assert len(status["source_gp160_readiness_hash"]) == 64
        assert status["component_count"] == 10
        assert status["request_draft_count"] == len(REQUEST_DRAFTS)
        assert status["blocker_count"] == len(BLOCKER_SPECS)
        assert status["controlled_test_locked"] is True
        assert status["no_provider_contact"] is True
        assert status["connection_test_request_submitted"] is False
        assert status["connection_test_request_approved"] is False
        assert status["connection_test_run_started"] is False
        assert status["connection_test_run_completed"] is False
        assert status["real_provider_connection_started"] is False
        assert status["provider_api_called"] is False
        assert status["provider_token_created"] is False
        assert status["provider_session_created"] is False
        assert status["provider_job_reference_created"] is False
        assert status["provider_status_poll_started"] is False
        assert status["provider_health_checked"] is False
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

def test_gp161_170_html_is_dark_and_routes_registered(gp161_170_db):
    html = render_controlled_provider_connection_test_lock_layer_page()
    lowered = html.lower()
    assert "Vault GP161-GP170 Controlled Provider Connection Test Lock Layer" in html
    assert "GP161-GP170 built" in html
    assert "Controlled test locked" in html
    assert "Safe to GP171" in html
    assert "No request submit" in html
    assert "No approval" in html
    assert "No provider contact" in html
    assert "No provider API" in html
    assert "No token/session/job" in html
    assert "No object body" in html
    assert "No execution" in html
    assert "VAULT_GP171_180_CONTROLLED_READ_ONLY_METADATA_TEST_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/controlled-provider-connection-test-lock-layer",
        "/vault/controlled-provider-connection-test-lock-layer.json",
        "/vault/controlled-connection-test-lock-shell.json",
        "/vault/connection-test-request-draft-registry.json",
        "/vault/connection-test-approval-gate-lock-contract.json",
        "/vault/connection-test-denial-reason-board.json",
        "/vault/connection-test-run-plan-lock-contract.json",
        "/vault/connection-test-receipt-draft-ledger.json",
        "/vault/connection-test-result-placeholder-queue.json",
        "/vault/connection-test-emergency-stop-lock.json",
        "/vault/controlled-connection-test-blocker-board.json",
        "/vault/controlled-connection-test-readiness-checkpoint.json",
        "/vault/gp161-status.json",
        "/vault/gp162-status.json",
        "/vault/gp163-status.json",
        "/vault/gp164-status.json",
        "/vault/gp165-status.json",
        "/vault/gp166-status.json",
        "/vault/gp167-status.json",
        "/vault/gp168-status.json",
        "/vault/gp169-status.json",
        "/vault/gp170-status.json",
    ]
    for route in required_routes:
        assert route in text
