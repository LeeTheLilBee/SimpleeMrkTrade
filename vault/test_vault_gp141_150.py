"""
Tests for VAULT GP141-GP150 — Provider Readiness Simulation and Dry-Run Layer
"""

from pathlib import Path
import pytest

from vault.provider_readiness_simulation_dry_run_layer_service import (
    CONNECTION_PLAN_ID,
    EXPORT_PLAN_ID,
    FALSE_FIELDS,
    METADATA_PLAN_ID,
    PLAN_GROUPS,
    READINESS_ID,
    RECEIPT_DRAFT_LEDGER_ID,
    RESTORE_PLAN_ID,
    RESULT_REVIEW_QUEUE_ID,
    SCENARIOS,
    SCENARIO_REGISTRY_ID,
    SIMULATION_BLOCKER_BOARD_ID,
    SIMULATION_SHELL_ID,
    ensure_provider_readiness_simulation_dry_run_layer_schema,
    get_gp141_provider_readiness_simulation_shell,
    get_gp141_status,
    get_gp142_provider_dry_run_scenario_registry,
    get_gp142_status,
    get_gp143_provider_connection_dry_run_plan,
    get_gp143_status,
    get_gp144_provider_metadata_dry_run_plan,
    get_gp144_status,
    get_gp145_provider_restore_dry_run_plan,
    get_gp145_status,
    get_gp146_provider_export_dry_run_plan,
    get_gp146_status,
    get_gp147_dry_run_receipt_draft_ledger,
    get_gp147_status,
    get_gp148_dry_run_result_review_queue,
    get_gp148_status,
    get_gp149_provider_readiness_simulation_blocker_board,
    get_gp149_status,
    get_gp150_provider_readiness_simulation_checkpoint,
    get_gp150_status,
    get_provider_readiness_simulation_dry_run_layer_home,
    initialize_provider_readiness_simulation_dry_run_layer,
    render_provider_readiness_simulation_dry_run_layer_page,
    validate_provider_readiness_simulation_dry_run_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp141_150_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp141_150.sqlite")

def test_gp141_150_schema_and_initialize(gp141_150_db):
    schema = ensure_provider_readiness_simulation_dry_run_layer_schema(gp141_150_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_provider_simulation_components" in schema["tables"]
    assert "vault_provider_dry_run_scenarios" in schema["tables"]
    assert "vault_provider_dry_run_plans" in schema["tables"]
    assert "vault_provider_dry_run_receipt_drafts" in schema["tables"]
    assert "vault_provider_dry_run_review_queue" in schema["tables"]
    assert "vault_provider_simulation_blockers" in schema["tables"]
    assert "vault_provider_simulation_readiness" in schema["tables"]

    result = initialize_provider_readiness_simulation_dry_run_layer(gp141_150_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["scenario_count"] == len(SCENARIOS)
    assert result["plan_count"] == len(PLAN_GROUPS)
    assert result["receipt_draft_count"] == len(SCENARIOS)
    assert result["review_item_count"] == len(SCENARIOS)
    assert result["blocker_count"] == 12
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp141_simulation_shell(gp141_150_db):
    payload = get_gp141_provider_readiness_simulation_shell(gp141_150_db)
    shell = payload["simulation_shell"]

    assert payload["pack"]["id"] == "VAULT_GP141"
    assert shell["component_id"] == SIMULATION_SHELL_ID
    assert shell["gp_number"] == 141
    assert shell["section_range"] == "GP141-GP150"
    assert shell["source_gp140_readiness_score"] == 100
    assert len(shell["source_gp140_readiness_hash"]) == 64
    assert shell["component_ready"] is True
    assert shell["component_locked"] is True
    assert shell["simulation_only"] is True
    assert shell["dry_run_only"] is True

    for field in FALSE_FIELDS:
        assert shell[field] is False

def test_gp142_scenarios(gp141_150_db):
    payload = get_gp142_provider_dry_run_scenario_registry(gp141_150_db)
    scenarios = payload["scenarios"]

    assert payload["pack"]["id"] == "VAULT_GP142"
    assert payload["scenario_registry"]["component_id"] == SCENARIO_REGISTRY_ID
    assert payload["scenario_count"] == len(SCENARIOS)
    assert all(item["scenario_ready"] is True for item in scenarios)
    assert all(item["scenario_locked"] is True for item in scenarios)
    assert all(item["simulation_only"] is True for item in scenarios)
    assert all(item["dry_run_only"] is True for item in scenarios)
    assert all(item["dry_run_submitted_to_provider"] is False for item in scenarios)
    assert all(item["real_provider_connection_started"] is False for item in scenarios)
    assert all(item["provider_api_called"] is False for item in scenarios)

def test_gp143_connection_plan(gp141_150_db):
    payload = get_gp143_provider_connection_dry_run_plan(gp141_150_db)
    plans = payload["plans"]

    assert payload["pack"]["id"] == "VAULT_GP143"
    assert payload["connection_dry_run_plan"]["component_id"] == CONNECTION_PLAN_ID
    assert len(plans) == 1
    plan = plans[0]
    assert plan["plan_category"] == "connection"
    assert plan["step_count"] == 5
    assert plan["plan_ready"] is True
    assert plan["plan_locked"] is True
    assert plan["simulation_only"] is True
    assert plan["dry_run_only"] is True
    assert plan["real_provider_connection_started"] is False
    assert plan["provider_api_called"] is False
    assert plan["provider_token_created"] is False
    assert plan["provider_session_created"] is False

def test_gp144_metadata_plan(gp141_150_db):
    payload = get_gp144_provider_metadata_dry_run_plan(gp141_150_db)
    plans = payload["plans"]

    assert payload["pack"]["id"] == "VAULT_GP144"
    assert payload["metadata_dry_run_plan"]["component_id"] == METADATA_PLAN_ID
    assert len(plans) == 1
    plan = plans[0]
    assert plan["plan_category"] == "metadata"
    assert plan["provider_metadata_imported"] is False
    assert plan["provider_metadata_read"] is False
    assert plan["provider_objects_listed"] is False
    assert plan["object_body_read"] is False

def test_gp145_restore_plan(gp141_150_db):
    payload = get_gp145_provider_restore_dry_run_plan(gp141_150_db)
    plans = payload["plans"]

    assert payload["pack"]["id"] == "VAULT_GP145"
    assert payload["restore_dry_run_plan"]["component_id"] == RESTORE_PLAN_ID
    assert len(plans) == 1
    plan = plans[0]
    assert plan["plan_category"] == "restore"
    assert plan["restore_requested"] is False
    assert plan["restore_request_created"] is False
    assert plan["restore_job_created"] is False
    assert plan["provider_restore_api_called"] is False

def test_gp146_export_plan(gp141_150_db):
    payload = get_gp146_provider_export_dry_run_plan(gp141_150_db)
    plans = payload["plans"]

    assert payload["pack"]["id"] == "VAULT_GP146"
    assert payload["export_dry_run_plan"]["component_id"] == EXPORT_PLAN_ID
    assert len(plans) == 1
    plan = plans[0]
    assert plan["plan_category"] == "export"
    assert plan["export_requested"] is False
    assert plan["export_enabled"] is False
    assert plan["export_package_created"] is False
    assert plan["export_manifest_created"] is False
    assert plan["export_download_enabled"] is False

def test_gp147_receipt_drafts(gp141_150_db):
    payload = get_gp147_dry_run_receipt_draft_ledger(gp141_150_db)
    receipts = payload["receipt_drafts"]

    assert payload["pack"]["id"] == "VAULT_GP147"
    assert payload["receipt_draft_ledger"]["component_id"] == RECEIPT_DRAFT_LEDGER_ID
    assert payload["receipt_draft_count"] == len(SCENARIOS)
    assert all(item["receipt_draft_locked"] is True for item in receipts)
    assert all(item["final_receipt_created"] is False for item in receipts)
    assert all(item["simulation_only"] is True for item in receipts)
    assert all(item["dry_run_only"] is True for item in receipts)
    assert all(item["dry_run_completed_by_provider"] is False for item in receipts)

def test_gp148_review_queue(gp141_150_db):
    payload = get_gp148_dry_run_result_review_queue(gp141_150_db)
    reviews = payload["review_items"]

    assert payload["pack"]["id"] == "VAULT_GP148"
    assert payload["result_review_queue"]["component_id"] == RESULT_REVIEW_QUEUE_ID
    assert payload["review_item_count"] == len(SCENARIOS)
    assert all(item["review_locked"] is True for item in reviews)
    assert all(item["owner_review_required"] is True for item in reviews)
    assert all(item["tower_review_required"] is True for item in reviews)
    assert all(item["owner_approval_recorded"] is False for item in reviews)
    assert all(item["owner_execute_action_approved"] is False for item in reviews)

def test_gp149_blockers(gp141_150_db):
    payload = get_gp149_provider_readiness_simulation_blocker_board(gp141_150_db)
    blockers = payload["blockers"]

    assert payload["pack"]["id"] == "VAULT_GP149"
    assert payload["simulation_blocker_board"]["component_id"] == SIMULATION_BLOCKER_BOARD_ID
    assert payload["blocker_count"] == 12
    assert all(item["blocker_active"] is True for item in blockers)
    assert all(item["blocks_real_provider_connection"] is True for item in blockers)
    assert all(item["blocks_provider_api"] is True for item in blockers)
    assert all(item["blocks_provider_token"] is True for item in blockers)
    assert all(item["blocks_provider_session"] is True for item in blockers)
    assert all(item["blocks_provider_job"] is True for item in blockers)
    assert all(item["blocks_provider_status_poll"] is True for item in blockers)
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

def test_gp150_readiness_home_status_and_validation(gp141_150_db):
    payload = get_gp150_provider_readiness_simulation_checkpoint(gp141_150_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP150"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["scenario_count"] == len(SCENARIOS)
    assert readiness["plan_count"] == len(PLAN_GROUPS)
    assert readiness["receipt_draft_count"] == len(SCENARIOS)
    assert readiness["review_item_count"] == len(SCENARIOS)
    assert readiness["blocker_count"] == 12
    assert readiness["safe_to_continue_to_gp151"] is True
    assert readiness["section_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp151"] is True
    assert validation["vault_done"] is False

    status = get_gp150_status(gp141_150_db)["gp150_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp151"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_REAL_PROVIDER_CONNECTION_READINESS_LAYER"
    assert status["next_section_range"] == "GP151-GP160"
    assert status["next_pack"] == "VAULT_GP151_160_REAL_PROVIDER_CONNECTION_READINESS_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp150"

    home = get_provider_readiness_simulation_dry_run_layer_home(gp141_150_db)
    assert home["pack"]["id"] == "VAULT_GP141_150"
    assert home["truth"]["provider_readiness_simulation_dry_run_layer_ready"] is True
    assert home["truth"]["safe_to_continue_to_gp151"] is True
    assert home["truth"]["simulation_only"] is True
    assert home["truth"]["dry_run_only"] is True
    assert home["truth"]["simulation_promoted_to_real"] is False
    assert home["truth"]["dry_run_submitted_to_provider"] is False
    assert home["truth"]["real_provider_connection_started"] is False
    assert home["truth"]["provider_api_called"] is False
    assert home["truth"]["provider_token_created"] is False
    assert home["truth"]["provider_session_created"] is False
    assert home["truth"]["provider_job_reference_created"] is False
    assert home["truth"]["provider_status_poll_started"] is False
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

def test_gp141_150_all_status_endpoints(gp141_150_db):
    funcs = [
        (141, get_gp141_status, "gp141_status"),
        (142, get_gp142_status, "gp142_status"),
        (143, get_gp143_status, "gp143_status"),
        (144, get_gp144_status, "gp144_status"),
        (145, get_gp145_status, "gp145_status"),
        (146, get_gp146_status, "gp146_status"),
        (147, get_gp147_status, "gp147_status"),
        (148, get_gp148_status, "gp148_status"),
        (149, get_gp149_status, "gp149_status"),
        (150, get_gp150_status, "gp150_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp141_150_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp151"] is True
        assert status["source_gp140_readiness_score"] == 100
        assert len(status["source_gp140_readiness_hash"]) == 64
        assert status["scenario_count"] == len(SCENARIOS)
        assert status["plan_count"] == len(PLAN_GROUPS)
        assert status["receipt_draft_count"] == len(SCENARIOS)
        assert status["blocker_count"] == 12
        assert status["simulation_only"] is True
        assert status["dry_run_only"] is True
        assert status["simulation_promoted_to_real"] is False
        assert status["dry_run_submitted_to_provider"] is False
        assert status["dry_run_completed_by_provider"] is False
        assert status["real_provider_connection_requested"] is False
        assert status["real_provider_connection_started"] is False
        assert status["real_provider_connection_completed"] is False
        assert status["provider_api_called"] is False
        assert status["provider_token_created"] is False
        assert status["provider_session_created"] is False
        assert status["provider_job_reference_created"] is False
        assert status["provider_status_poll_started"] is False
        assert status["provider_status_poll_completed"] is False
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

def test_gp141_150_html_is_dark_and_routes_registered(gp141_150_db):
    html = render_provider_readiness_simulation_dry_run_layer_page()
    lowered = html.lower()
    assert "Vault GP141-GP150 Provider Readiness Simulation Dry-Run Layer" in html
    assert "GP141-GP150 built" in html
    assert "Simulation ready" in html
    assert "Dry-run only" in html
    assert "Safe to GP151" in html
    assert "No provider connection" in html
    assert "No provider API" in html
    assert "No token/session/job" in html
    assert "No object body" in html
    assert "No export/restore" in html
    assert "No execution" in html
    assert "VAULT_GP151_160_REAL_PROVIDER_CONNECTION_READINESS_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/provider-readiness-simulation-dry-run-layer",
        "/vault/provider-readiness-simulation-dry-run-layer.json",
        "/vault/provider-readiness-simulation-shell.json",
        "/vault/provider-dry-run-scenario-registry.json",
        "/vault/provider-connection-dry-run-plan.json",
        "/vault/provider-metadata-dry-run-plan.json",
        "/vault/provider-restore-dry-run-plan.json",
        "/vault/provider-export-dry-run-plan.json",
        "/vault/provider-dry-run-receipt-draft-ledger.json",
        "/vault/provider-dry-run-result-review-queue.json",
        "/vault/provider-readiness-simulation-blocker-board.json",
        "/vault/provider-readiness-simulation-checkpoint.json",
        "/vault/gp141-status.json",
        "/vault/gp142-status.json",
        "/vault/gp143-status.json",
        "/vault/gp144-status.json",
        "/vault/gp145-status.json",
        "/vault/gp146-status.json",
        "/vault/gp147-status.json",
        "/vault/gp148-status.json",
        "/vault/gp149-status.json",
        "/vault/gp150-status.json",
    ]
    for route in required_routes:
        assert route in text
