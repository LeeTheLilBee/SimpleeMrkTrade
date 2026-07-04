"""
Tests for VAULT GP121-GP130 — Owner Console and Operating Dashboard Layer
"""

from pathlib import Path
import pytest

from vault.owner_console_operating_dashboard_layer_service import (
    ARCHIVE_HEALTH_ID,
    CONSOLE_BLOCKER_BOARD_ID,
    DASHBOARD_SNAPSHOT_ID,
    FALSE_FIELDS,
    METRIC_SPECS,
    NEXT_SAFE_ACTION_ID,
    OPEN_CASE_BOARD_ID,
    OWNER_CONSOLE_SHELL_ID,
    PANEL_SPECS,
    PROVIDER_LOCK_PANEL_ID,
    READINESS_ID,
    RECEIPT_PROOF_BOARD_ID,
    SAFE_ACTION_SPECS,
    TOWER_GATE_PANEL_ID,
    ensure_owner_console_operating_dashboard_layer_schema,
    get_gp121_owner_console_shell,
    get_gp121_status,
    get_gp122_operating_dashboard_snapshot,
    get_gp122_status,
    get_gp123_archive_health_summary,
    get_gp123_status,
    get_gp124_open_recovery_case_summary_board,
    get_gp124_status,
    get_gp125_receipt_and_proof_summary_board,
    get_gp125_status,
    get_gp126_provider_lock_status_panel,
    get_gp126_status,
    get_gp127_tower_gate_status_panel,
    get_gp127_status,
    get_gp128_owner_next_safe_action_board,
    get_gp128_status,
    get_gp129_owner_console_blocker_board,
    get_gp129_status,
    get_gp130_owner_console_readiness_checkpoint,
    get_gp130_status,
    get_owner_console_operating_dashboard_layer_home,
    initialize_owner_console_operating_dashboard_layer,
    render_owner_console_operating_dashboard_layer_page,
    validate_owner_console_operating_dashboard_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp121_130_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp121_130.sqlite")

def test_gp121_130_schema_and_initialize(gp121_130_db):
    schema = ensure_owner_console_operating_dashboard_layer_schema(gp121_130_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_owner_console_components" in schema["tables"]
    assert "vault_owner_console_metrics" in schema["tables"]
    assert "vault_owner_console_panels" in schema["tables"]
    assert "vault_owner_console_safe_actions" in schema["tables"]
    assert "vault_owner_console_blockers" in schema["tables"]
    assert "vault_owner_console_readiness" in schema["tables"]

    result = initialize_owner_console_operating_dashboard_layer(gp121_130_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["metric_count"] == len(METRIC_SPECS)
    assert result["panel_count"] == len(PANEL_SPECS)
    assert result["safe_action_count"] == len(SAFE_ACTION_SPECS)
    assert result["blocker_count"] == 8
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp121_owner_console_shell(gp121_130_db):
    payload = get_gp121_owner_console_shell(gp121_130_db)
    shell = payload["owner_console_shell"]
    panels = payload["panels"]

    assert payload["pack"]["id"] == "VAULT_GP121"
    assert shell["component_id"] == OWNER_CONSOLE_SHELL_ID
    assert shell["gp_number"] == 121
    assert shell["section_range"] == "GP121-GP130"
    assert shell["source_gp120_readiness_score"] == 100
    assert len(shell["source_gp120_readiness_hash"]) == 64
    assert shell["component_ready"] is True
    assert shell["component_locked"] is True
    assert shell["owner_console_visible"] is True
    assert payload["panel_count"] == len(PANEL_SPECS)
    assert all(item["panel_visible"] is True for item in panels)
    assert all(item["panel_locked"] is True for item in panels)
    assert all(item["redacted_only"] is True for item in panels)

    for field in FALSE_FIELDS:
        assert shell[field] is False

def test_gp122_operating_dashboard_snapshot(gp121_130_db):
    payload = get_gp122_operating_dashboard_snapshot(gp121_130_db)
    snapshot = payload["dashboard_snapshot"]
    metrics = payload["metrics"]

    assert payload["pack"]["id"] == "VAULT_GP122"
    assert snapshot["component_id"] == DASHBOARD_SNAPSHOT_ID
    assert payload["metric_count"] == len(METRIC_SPECS)
    assert {item["metric_code"] for item in metrics} == {item[0] for item in METRIC_SPECS}
    assert all(item["metric_visible"] is True for item in metrics)
    assert all(item["metric_locked"] is True for item in metrics)
    assert all(item["current_value"] == item["target_value"] for item in metrics)
    for item in metrics:
        for field in FALSE_FIELDS:
            assert item[field] is False

def test_gp123_archive_health_summary(gp121_130_db):
    payload = get_gp123_archive_health_summary(gp121_130_db)
    summary = payload["archive_health_summary"]
    health = summary["health"]

    assert payload["pack"]["id"] == "VAULT_GP123"
    assert summary["component_id"] == ARCHIVE_HEALTH_ID
    assert health["archive_health_status"] == "HEALTHY_LOCKED_REDACTED_ONLY"
    assert health["metrics_ready"] is True
    assert health["active_blockers"] == 8
    assert health["provider_api_locked"] is True
    assert health["object_body_locked"] is True
    assert health["download_locked"] is True
    assert health["export_locked"] is True
    assert health["restore_locked"] is True
    assert health["vault_done"] is False

def test_gp124_open_recovery_case_summary_board(gp121_130_db):
    payload = get_gp124_open_recovery_case_summary_board(gp121_130_db)
    board = payload["cases"]

    assert payload["pack"]["id"] == "VAULT_GP124"
    assert payload["open_case_summary_board"]["component_id"] == OPEN_CASE_BOARD_ID
    assert payload["case_link_count"] == 8
    assert all(item["case_link_locked"] is True for item in board)
    assert all(item["redacted_only"] is True for item in board)
    assert all(item["evidence_link_count"] == 3 for item in board)
    assert all(item["receipt_link_count"] == 2 for item in board)
    assert all(item["restore_requested"] is False for item in board)
    assert all(item["export_requested"] is False for item in board)

def test_gp125_receipt_and_proof_summary_board(gp121_130_db):
    payload = get_gp125_receipt_and_proof_summary_board(gp121_130_db)
    proof = payload["proof_packets"]

    assert payload["pack"]["id"] == "VAULT_GP125"
    assert payload["receipt_proof_summary_board"]["component_id"] == RECEIPT_PROOF_BOARD_ID
    assert payload["proof_packet_count"] == 16
    assert all(item["proof_packet_locked"] is True for item in proof)
    assert all(item["redacted_only"] is True for item in proof)
    assert all(item["export_package_created"] is False for item in proof)
    assert all(item["object_body_read"] is False for item in proof)

def test_gp126_provider_lock_status_panel(gp121_130_db):
    payload = get_gp126_provider_lock_status_panel(gp121_130_db)
    panel = payload["provider_lock_status_panel"]
    lock = panel["provider_lock"]

    assert payload["pack"]["id"] == "VAULT_GP126"
    assert panel["component_id"] == PROVIDER_LOCK_PANEL_ID
    assert lock["provider_lock_status"] == "PROVIDER_API_LOCKED"
    assert lock["provider_api_configured"] is False
    assert lock["provider_api_called"] is False
    assert lock["provider_objects_listed"] is False
    assert lock["provider_metadata_imported"] is False
    assert lock["provider_metadata_read"] is False
    assert lock["provider_restore_api_called"] is False
    assert lock["direct_upload_enabled"] is False

def test_gp127_tower_gate_status_panel(gp121_130_db):
    payload = get_gp127_tower_gate_status_panel(gp121_130_db)
    panel = payload["tower_gate_status_panel"]
    gate = panel["tower_gate"]

    assert payload["pack"]["id"] == "VAULT_GP127"
    assert panel["component_id"] == TOWER_GATE_PANEL_ID
    assert gate["tower_gate_status"] == "TOWER_GATE_LOCKED"
    assert gate["tower_unlock_requested"] is False
    assert gate["tower_unlock_granted"] is False
    assert gate["tower_step_up_passed"] is False
    assert gate["owner_approval_recorded"] is False
    assert gate["owner_decision_recorded"] is False
    assert gate["execution_enabled"] is False

def test_gp128_next_safe_action_board(gp121_130_db):
    payload = get_gp128_owner_next_safe_action_board(gp121_130_db)
    actions = payload["actions"]

    assert payload["pack"]["id"] == "VAULT_GP128"
    assert payload["next_safe_action_board"]["component_id"] == NEXT_SAFE_ACTION_ID
    assert payload["safe_action_count"] == len(SAFE_ACTION_SPECS)
    assert all(item["action_visible"] is True for item in actions)
    assert all(item["action_locked"] is True for item in actions)
    assert all(item["safe_action"] is True for item in actions)
    assert any(item["action_code"] == "prepare_gp131_handoff" for item in actions)
    assert any(item["action_code"] == "do_not_unlock" for item in actions)
    for item in actions:
        assert item["owner_execute_action_approved"] is False
        assert item["execution_enabled"] is False
        assert item["vault_done"] is False

def test_gp129_blocker_board(gp121_130_db):
    payload = get_gp129_owner_console_blocker_board(gp121_130_db)
    blockers = payload["blockers"]

    assert payload["pack"]["id"] == "VAULT_GP129"
    assert payload["owner_console_blocker_board"]["component_id"] == CONSOLE_BLOCKER_BOARD_ID
    assert payload["blocker_count"] == 8
    assert all(item["blocker_active"] is True for item in blockers)
    assert all(item["blocks_provider_api"] is True for item in blockers)
    assert all(item["blocks_object_body"] is True for item in blockers)
    assert all(item["blocks_download"] is True for item in blockers)
    assert all(item["blocks_export"] is True for item in blockers)
    assert all(item["blocks_restore"] is True for item in blockers)
    assert all(item["blocks_direct_upload"] is True for item in blockers)
    assert all(item["blocks_tower_unlock"] is True for item in blockers)
    assert all(item["blocks_owner_execution"] is True for item in blockers)
    assert all(item["blocks_execution"] is True for item in blockers)
    assert all(item["blocks_vault_done"] is True for item in blockers)
    assert all(item["resolved"] is False for item in blockers)

def test_gp130_readiness_status_home_and_validation(gp121_130_db):
    payload = get_gp130_owner_console_readiness_checkpoint(gp121_130_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP130"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["metric_count"] == len(METRIC_SPECS)
    assert readiness["panel_count"] == len(PANEL_SPECS)
    assert readiness["safe_action_count"] == len(SAFE_ACTION_SPECS)
    assert readiness["blocker_count"] == 8
    assert readiness["safe_to_continue_to_gp131"] is True
    assert readiness["section_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp131"] is True
    assert validation["vault_done"] is False

    status = get_gp130_status(gp121_130_db)["gp130_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp131"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_TOWER_GATED_PERMISSION_AND_STEP_UP_LAYER"
    assert status["next_section_range"] == "GP131-GP140"
    assert status["next_pack"] == "VAULT_GP131_140_TOWER_GATED_PERMISSION_AND_STEP_UP_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp130"

    home = get_owner_console_operating_dashboard_layer_home(gp121_130_db)
    assert home["pack"]["id"] == "VAULT_GP121_130"
    assert home["truth"]["owner_console_operating_dashboard_layer_ready"] is True
    assert home["truth"]["safe_to_continue_to_gp131"] is True
    assert home["truth"]["provider_api_called"] is False
    assert home["truth"]["provider_objects_listed"] is False
    assert home["truth"]["provider_metadata_read"] is False
    assert home["truth"]["object_body_read"] is False
    assert home["truth"]["object_body_view_enabled"] is False
    assert home["truth"]["object_body_download_enabled"] is False
    assert home["truth"]["object_body_plaintext_visible"] is False
    assert home["truth"]["object_download_enabled"] is False
    assert home["truth"]["export_package_created"] is False
    assert home["truth"]["restore_job_created"] is False
    assert home["truth"]["direct_upload_enabled"] is False
    assert home["truth"]["tower_unlock_granted"] is False
    assert home["truth"]["owner_approval_recorded"] is False
    assert home["truth"]["owner_execute_action_approved"] is False
    assert home["truth"]["execution_enabled"] is False
    assert home["truth"]["vault_done"] is False
    assert home["truth"]["clouds_should_continue"] is False

def test_gp121_130_all_status_endpoints(gp121_130_db):
    funcs = [
        (121, get_gp121_status, "gp121_status"),
        (122, get_gp122_status, "gp122_status"),
        (123, get_gp123_status, "gp123_status"),
        (124, get_gp124_status, "gp124_status"),
        (125, get_gp125_status, "gp125_status"),
        (126, get_gp126_status, "gp126_status"),
        (127, get_gp127_status, "gp127_status"),
        (128, get_gp128_status, "gp128_status"),
        (129, get_gp129_status, "gp129_status"),
        (130, get_gp130_status, "gp130_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp121_130_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp131"] is True
        assert status["source_gp120_readiness_score"] == 100
        assert len(status["source_gp120_readiness_hash"]) == 64
        assert status["metric_count"] == len(METRIC_SPECS)
        assert status["panel_count"] == len(PANEL_SPECS)
        assert status["safe_action_count"] == len(SAFE_ACTION_SPECS)
        assert status["blocker_count"] == 8
        assert status["owner_decision_recorded"] is False
        assert status["owner_approval_recorded"] is False
        assert status["owner_rejection_recorded"] is False
        assert status["owner_execute_action_requested"] is False
        assert status["owner_execute_action_approved"] is False
        assert status["tower_unlock_requested"] is False
        assert status["tower_unlock_granted"] is False
        assert status["tower_step_up_passed"] is False
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
        assert status["execution_enabled"] is False
        assert status["vault_done"] is False

def test_gp121_130_html_is_dark_and_routes_registered(gp121_130_db):
    html = render_owner_console_operating_dashboard_layer_page()
    lowered = html.lower()
    assert "Vault GP121-GP130 Owner Console Operating Dashboard Layer" in html
    assert "GP121-GP130 built" in html
    assert "Owner console ready" in html
    assert "Dashboard ready" in html
    assert "Safe to GP131" in html
    assert "No Tower unlock" in html
    assert "No provider API" in html
    assert "No object body" in html
    assert "No export" in html
    assert "No restore" in html
    assert "No execution" in html
    assert "VAULT_GP131_140_TOWER_GATED_PERMISSION_AND_STEP_UP_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/owner-console-operating-dashboard-layer",
        "/vault/owner-console-operating-dashboard-layer.json",
        "/vault/owner-console-shell.json",
        "/vault/owner-operating-dashboard-snapshot.json",
        "/vault/owner-archive-health-summary.json",
        "/vault/owner-open-recovery-case-summary-board.json",
        "/vault/owner-receipt-proof-summary-board.json",
        "/vault/owner-provider-lock-status-panel.json",
        "/vault/owner-tower-gate-status-panel.json",
        "/vault/owner-next-safe-action-board.json",
        "/vault/owner-console-blocker-board.json",
        "/vault/owner-console-readiness-checkpoint.json",
        "/vault/gp121-status.json",
        "/vault/gp122-status.json",
        "/vault/gp123-status.json",
        "/vault/gp124-status.json",
        "/vault/gp125-status.json",
        "/vault/gp126-status.json",
        "/vault/gp127-status.json",
        "/vault/gp128-status.json",
        "/vault/gp129-status.json",
        "/vault/gp130-status.json",
    ]
    for route in required_routes:
        assert route in text
