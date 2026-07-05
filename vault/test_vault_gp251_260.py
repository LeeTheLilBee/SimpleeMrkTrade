"""
Tests for VAULT GP251-GP260 — Beta Fix and Response Lock Layer
"""

from pathlib import Path
import pytest

from vault.beta_fix_response_lock_layer_service import (
    FALSE_FIELDS,
    FIX_DRAFT_ID,
    FIX_DRAFTS,
    FIX_EXECUTION_LOCK_ID,
    FIX_EXECUTION_LOCKS,
    FIX_VERIFICATION_ID,
    FIX_VERIFICATION_PREVIEWS,
    OWNER_RESPONSE_APPROVAL_ID,
    OWNER_RESPONSE_APPROVAL_LOCKS,
    READINESS_ID,
    RECEIPT_PACKET_ID,
    RELEASE_CLOSEOUT_ID,
    RELEASE_CLOSEOUT_LOCKS,
    RESPONSE_DRAFT_ID,
    RESPONSE_DRAFTS,
    RESPONSE_SEND_LOCK_ID,
    RESPONSE_SEND_LOCKS,
    SHELL_ID,
    ensure_beta_fix_response_lock_layer_schema,
    get_gp251_beta_fix_response_lock_shell,
    get_gp251_status,
    get_gp252_fix_draft_queue,
    get_gp252_status,
    get_gp253_response_draft_queue,
    get_gp253_status,
    get_gp254_fix_execution_lock_contract,
    get_gp254_status,
    get_gp255_response_send_lock_contract,
    get_gp255_status,
    get_gp256_fix_verification_preview_board,
    get_gp256_status,
    get_gp257_release_closeout_lock_contract,
    get_gp257_status,
    get_gp258_owner_response_approval_lock_board,
    get_gp258_status,
    get_gp259_fix_response_receipt_draft_packet,
    get_gp259_status,
    get_gp260_fix_response_lock_readiness_checkpoint,
    get_gp260_status,
    get_beta_fix_response_lock_layer_home,
    initialize_beta_fix_response_lock_layer,
    render_beta_fix_response_lock_layer_page,
    validate_beta_fix_response_lock_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp251_260_db(tmp_path, monkeypatch):
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
        "VAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_DB": "gp080.sqlite",
        "VAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_DB": "gp090.sqlite",
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
        "VAULT_BETA_ACCESS_INVITE_LOCK_LAYER_DB": "gp211_220.sqlite",
        "VAULT_BETA_ONBOARDING_LOCKED_EXPERIENCE_LAYER_DB": "gp221_230.sqlite",
        "VAULT_BETA_FEEDBACK_ISSUE_INTAKE_LOCK_LAYER_DB": "gp231_240.sqlite",
        "VAULT_BETA_FEEDBACK_REVIEW_TRIAGE_LOCK_LAYER_DB": "gp241_250.sqlite",
        "VAULT_BETA_FIX_RESPONSE_LOCK_LAYER_DB": "gp251_260.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp251_260.sqlite")

def test_gp251_260_schema_and_initialize(gp251_260_db):
    schema = ensure_beta_fix_response_lock_layer_schema(gp251_260_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_beta_fix_response_components" in schema["tables"]
    assert "vault_fix_draft_queue" in schema["tables"]
    assert "vault_fix_response_readiness" in schema["tables"]

    result = initialize_beta_fix_response_lock_layer(gp251_260_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["fix_draft_count"] == len(FIX_DRAFTS)
    assert result["response_draft_count"] == len(RESPONSE_DRAFTS)
    assert result["fix_execution_lock_count"] == len(FIX_EXECUTION_LOCKS)
    assert result["response_send_lock_count"] == len(RESPONSE_SEND_LOCKS)
    assert result["fix_verification_count"] == len(FIX_VERIFICATION_PREVIEWS)
    assert result["release_closeout_lock_count"] == len(RELEASE_CLOSEOUT_LOCKS)
    assert result["owner_response_approval_lock_count"] == len(OWNER_RESPONSE_APPROVAL_LOCKS)
    assert result["receipt_packet_count"] == 1
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp251_shell(gp251_260_db):
    payload = get_gp251_beta_fix_response_lock_shell(gp251_260_db)
    shell = payload["shell"]

    assert payload["pack"]["id"] == "VAULT_GP251"
    assert shell["component_id"] == SHELL_ID
    assert shell["gp_number"] == 251
    assert shell["source_gp250_readiness_score"] == 100
    assert len(shell["source_gp250_readiness_hash"]) == 64
    assert shell["component_ready"] is True
    assert shell["component_locked"] is True
    assert shell["fix_response_ready"] is True
    assert shell["fix_execution_locked"] is True
    assert shell["response_send_locked"] is True
    assert shell["verification_preview_only"] is True
    assert shell["release_closeout_locked"] is True
    assert shell["owner_response_approval_locked"] is True
    assert shell["vault_not_done"] is True

    for field in FALSE_FIELDS:
        assert shell[field] is False

def test_gp252_fix_drafts(gp251_260_db):
    payload = get_gp252_fix_draft_queue(gp251_260_db)
    rows = payload["drafts"]

    assert payload["pack"]["id"] == "VAULT_GP252"
    assert payload["fix_draft_queue"]["component_id"] == FIX_DRAFT_ID
    assert payload["fix_draft_count"] == len(FIX_DRAFTS)
    assert all(item["draft_ready"] is True for item in rows)
    assert all(item["draft_locked"] is True for item in rows)
    assert all(item["execution_locked"] is True for item in rows)
    assert all(item["fix_draft_created"] is False for item in rows)
    assert all(item["fix_task_created"] is False for item in rows)
    assert all(item["fix_started"] is False for item in rows)

def test_gp253_response_drafts(gp251_260_db):
    payload = get_gp253_response_draft_queue(gp251_260_db)
    rows = payload["drafts"]

    assert payload["pack"]["id"] == "VAULT_GP253"
    assert payload["response_draft_queue"]["component_id"] == RESPONSE_DRAFT_ID
    assert payload["response_draft_count"] == len(RESPONSE_DRAFTS)
    assert all(item["draft_ready"] is True for item in rows)
    assert all(item["draft_locked"] is True for item in rows)
    assert all(item["send_locked"] is True for item in rows)
    assert all(item["response_draft_created"] is False for item in rows)
    assert all(item["response_sent"] is False for item in rows)
    assert all(item["tester_notified"] is False for item in rows)

def test_gp254_fix_execution_locks(gp251_260_db):
    payload = get_gp254_fix_execution_lock_contract(gp251_260_db)
    rows = payload["locks"]

    assert payload["pack"]["id"] == "VAULT_GP254"
    assert payload["fix_execution_lock_contract"]["component_id"] == FIX_EXECUTION_LOCK_ID
    assert payload["fix_execution_lock_count"] == len(FIX_EXECUTION_LOCKS)
    assert all(item["fix_execution_locked"] is True for item in rows)
    assert all(item["code_patch_locked"] is True for item in rows)
    assert all(item["test_run_locked"] is True for item in rows)
    assert all(item["fix_started"] is False for item in rows)
    assert all(item["code_patch_written"] is False for item in rows)
    assert all(item["test_run_started"] is False for item in rows)

def test_gp255_response_send_locks(gp251_260_db):
    payload = get_gp255_response_send_lock_contract(gp251_260_db)
    rows = payload["locks"]

    assert payload["pack"]["id"] == "VAULT_GP255"
    assert payload["response_send_lock_contract"]["component_id"] == RESPONSE_SEND_LOCK_ID
    assert payload["response_send_lock_count"] == len(RESPONSE_SEND_LOCKS)
    assert all(item["response_send_locked"] is True for item in rows)
    assert all(item["tester_notify_locked"] is True for item in rows)
    assert all(item["support_response_locked"] is True for item in rows)
    assert all(item["response_sent"] is False for item in rows)
    assert all(item["tester_notified"] is False for item in rows)
    assert all(item["support_response_sent"] is False for item in rows)

def test_gp256_fix_verification(gp251_260_db):
    payload = get_gp256_fix_verification_preview_board(gp251_260_db)
    rows = payload["verifications"]

    assert payload["pack"]["id"] == "VAULT_GP256"
    assert payload["fix_verification_preview_board"]["component_id"] == FIX_VERIFICATION_ID
    assert payload["fix_verification_count"] == len(FIX_VERIFICATION_PREVIEWS)
    assert all(item["preview_ready"] is True for item in rows)
    assert all(item["verification_locked"] is True for item in rows)
    assert all(item["final_result_locked"] is True for item in rows)
    assert all(item["fix_verification_started"] is False for item in rows)
    assert all(item["fix_verification_completed"] is False for item in rows)
    assert all(item["fix_verified"] is False for item in rows)

def test_gp257_release_closeout(gp251_260_db):
    payload = get_gp257_release_closeout_lock_contract(gp251_260_db)
    rows = payload["locks"]

    assert payload["pack"]["id"] == "VAULT_GP257"
    assert payload["release_closeout_lock_contract"]["component_id"] == RELEASE_CLOSEOUT_ID
    assert payload["release_closeout_lock_count"] == len(RELEASE_CLOSEOUT_LOCKS)
    assert all(item["release_locked"] is True for item in rows)
    assert all(item["closeout_locked"] is True for item in rows)
    assert all(item["publish_locked"] is True for item in rows)
    assert all(item["release_created"] is False for item in rows)
    assert all(item["release_published"] is False for item in rows)
    assert all(item["closeout_recorded"] is False for item in rows)

def test_gp258_owner_response_approval(gp251_260_db):
    payload = get_gp258_owner_response_approval_lock_board(gp251_260_db)
    rows = payload["locks"]

    assert payload["pack"]["id"] == "VAULT_GP258"
    assert payload["owner_response_approval_lock_board"]["component_id"] == OWNER_RESPONSE_APPROVAL_ID
    assert payload["owner_response_approval_lock_count"] == len(OWNER_RESPONSE_APPROVAL_LOCKS)
    assert all(item["owner_approval_locked"] is True for item in rows)
    assert all(item["owner_rejection_locked"] is True for item in rows)
    assert all(item["owner_closeout_locked"] is True for item in rows)
    assert all(item["owner_response_approval_recorded"] is False for item in rows)
    assert all(item["owner_response_rejection_recorded"] is False for item in rows)
    assert all(item["owner_approval_recorded"] is False for item in rows)

def test_gp259_receipt_packet(gp251_260_db):
    payload = get_gp259_fix_response_receipt_draft_packet(gp251_260_db)
    packets = payload["packets"]

    assert payload["pack"]["id"] == "VAULT_GP259"
    assert payload["receipt_packet_component"]["component_id"] == RECEIPT_PACKET_ID
    assert payload["receipt_packet_count"] == 1
    assert packets[0]["packet_ready"] is True
    assert packets[0]["packet_locked"] is True
    assert packets[0]["final_fix_receipt"] is False
    assert packets[0]["final_response_receipt"] is False
    assert packets[0]["fix_started"] is False
    assert packets[0]["response_sent"] is False
    assert packets[0]["vault_done"] is False
    assert len(packets[0]["packet_hash"]) == 64

def test_gp260_readiness_home_status_validation(gp251_260_db):
    payload = get_gp260_fix_response_lock_readiness_checkpoint(gp251_260_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP260"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["fix_draft_count"] == len(FIX_DRAFTS)
    assert readiness["response_draft_count"] == len(RESPONSE_DRAFTS)
    assert readiness["fix_execution_lock_count"] == len(FIX_EXECUTION_LOCKS)
    assert readiness["response_send_lock_count"] == len(RESPONSE_SEND_LOCKS)
    assert readiness["fix_verification_count"] == len(FIX_VERIFICATION_PREVIEWS)
    assert readiness["release_closeout_lock_count"] == len(RELEASE_CLOSEOUT_LOCKS)
    assert readiness["owner_response_approval_lock_count"] == len(OWNER_RESPONSE_APPROVAL_LOCKS)
    assert readiness["receipt_packet_count"] == 1
    assert readiness["fix_response_ready"] is True
    assert readiness["fix_execution_locked"] is True
    assert readiness["response_send_locked"] is True
    assert readiness["verification_preview_only"] is True
    assert readiness["release_closeout_locked"] is True
    assert readiness["owner_response_approval_locked"] is True
    assert readiness["safe_to_continue_to_gp261"] is True
    assert readiness["section_ready"] is True
    assert readiness["vault_done"] is False
    assert readiness["clouds_should_continue"] is False
    assert validation["valid"] is True
    assert validation["failed_count"] == 0

    status = get_gp260_status(gp251_260_db)["gp260_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp261"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_BETA_CLOSEOUT_AND_GO_NO_GO_LOCK_LAYER"
    assert status["next_section_range"] == "GP261-GP270"
    assert status["next_pack"] == "VAULT_GP261_270_BETA_CLOSEOUT_AND_GO_NO_GO_LOCK_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp260"

    home = get_beta_fix_response_lock_layer_home(gp251_260_db)
    assert home["pack"]["id"] == "VAULT_GP251_260"
    assert home["truth"]["beta_fix_response_lock_layer_ready"] is True
    assert home["truth"]["safe_to_continue_to_gp261"] is True
    assert home["truth"]["fix_draft_created"] is False
    assert home["truth"]["fix_task_created"] is False
    assert home["truth"]["fix_started"] is False
    assert home["truth"]["code_patch_written"] is False
    assert home["truth"]["test_run_started"] is False
    assert home["truth"]["response_draft_created"] is False
    assert home["truth"]["response_sent"] is False
    assert home["truth"]["tester_notified"] is False
    assert home["truth"]["fix_verification_started"] is False
    assert home["truth"]["fix_verified"] is False
    assert home["truth"]["release_created"] is False
    assert home["truth"]["release_published"] is False
    assert home["truth"]["closeout_recorded"] is False
    assert home["truth"]["owner_response_approval_recorded"] is False
    assert home["truth"]["billing_flow_created"] is False
    assert home["truth"]["provider_api_called"] is False
    assert home["truth"]["provider_metadata_read"] is False
    assert home["truth"]["object_body_read"] is False
    assert home["truth"]["object_download_enabled"] is False
    assert home["truth"]["export_package_created"] is False
    assert home["truth"]["restore_job_created"] is False
    assert home["truth"]["execution_enabled"] is False
    assert home["truth"]["vault_done"] is False

def test_gp251_260_all_status_endpoints(gp251_260_db):
    funcs = [
        (251, get_gp251_status, "gp251_status"),
        (252, get_gp252_status, "gp252_status"),
        (253, get_gp253_status, "gp253_status"),
        (254, get_gp254_status, "gp254_status"),
        (255, get_gp255_status, "gp255_status"),
        (256, get_gp256_status, "gp256_status"),
        (257, get_gp257_status, "gp257_status"),
        (258, get_gp258_status, "gp258_status"),
        (259, get_gp259_status, "gp259_status"),
        (260, get_gp260_status, "gp260_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp251_260_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp261"] is True
        assert status["source_gp250_readiness_score"] == 100
        assert len(status["source_gp250_readiness_hash"]) == 64
        assert status["component_count"] == 10
        assert status["fix_draft_count"] == len(FIX_DRAFTS)
        assert status["response_draft_count"] == len(RESPONSE_DRAFTS)
        assert status["fix_execution_lock_count"] == len(FIX_EXECUTION_LOCKS)
        assert status["fix_response_ready"] is True
        assert status["fix_execution_locked"] is True
        assert status["response_send_locked"] is True
        assert status["verification_preview_only"] is True
        assert status["release_closeout_locked"] is True
        assert status["owner_response_approval_locked"] is True
        assert status["fix_draft_created"] is False
        assert status["fix_task_created"] is False
        assert status["fix_started"] is False
        assert status["fix_completed"] is False
        assert status["code_patch_written"] is False
        assert status["test_run_started"] is False
        assert status["response_draft_created"] is False
        assert status["response_sent"] is False
        assert status["fix_verification_started"] is False
        assert status["fix_verified"] is False
        assert status["release_created"] is False
        assert status["release_published"] is False
        assert status["closeout_recorded"] is False
        assert status["owner_response_approval_recorded"] is False
        assert status["assignment_created"] is False
        assert status["intake_escalation_created"] is False
        assert status["billing_flow_created"] is False
        assert status["provider_api_called"] is False
        assert status["provider_metadata_read"] is False
        assert status["object_body_read"] is False
        assert status["object_download_enabled"] is False
        assert status["export_package_created"] is False
        assert status["restore_job_created"] is False
        assert status["tower_gate_opened"] is False
        assert status["tower_unlock_granted"] is False
        assert status["execution_enabled"] is False
        assert status["vault_done"] is False

def test_gp251_260_html_is_dark_and_routes_registered(gp251_260_db):
    html = render_beta_fix_response_lock_layer_page()
    lowered = html.lower()
    assert "Vault GP251-GP260 Beta Fix Response Lock Layer" in html
    assert "GP251-GP260 built" in html
    assert "Safe to GP261" in html
    assert "No fix created" in html
    assert "No code patch" in html
    assert "No response sent" in html
    assert "No verification" in html
    assert "No release" in html
    assert "No closeout" in html
    assert "No owner approval" in html
    assert "Vault not done" in html
    assert "VAULT_GP261_270_BETA_CLOSEOUT_AND_GO_NO_GO_LOCK_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/beta-fix-response-lock-layer",
        "/vault/beta-fix-response-lock-layer.json",
        "/vault/beta-fix-response-lock-shell.json",
        "/vault/fix-draft-queue.json",
        "/vault/response-draft-queue.json",
        "/vault/fix-execution-lock-contract.json",
        "/vault/response-send-lock-contract.json",
        "/vault/fix-verification-preview-board.json",
        "/vault/release-closeout-lock-contract.json",
        "/vault/owner-response-approval-lock-board.json",
        "/vault/fix-response-receipt-draft-packet.json",
        "/vault/fix-response-lock-readiness-checkpoint.json",
        "/vault/gp251-status.json",
        "/vault/gp252-status.json",
        "/vault/gp253-status.json",
        "/vault/gp254-status.json",
        "/vault/gp255-status.json",
        "/vault/gp256-status.json",
        "/vault/gp257-status.json",
        "/vault/gp258-status.json",
        "/vault/gp259-status.json",
        "/vault/gp260-status.json",
    ]
    for route in required_routes:
        assert route in text
