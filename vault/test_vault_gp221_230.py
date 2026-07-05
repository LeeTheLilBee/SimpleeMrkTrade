"""
Tests for VAULT GP221-GP230 — Beta Onboarding Locked Experience Layer
"""

from pathlib import Path
import pytest

from vault.beta_onboarding_locked_experience_layer_service import (
    FALSE_FIELDS,
    POLICY_ACK_ID,
    POLICY_ACK_LOCKS,
    PROFILE_SETUP_ID,
    PROFILE_SETUP_PREVIEWS,
    QA_CHECKLIST_ID,
    QA_CHECKS,
    READINESS_ID,
    RECEIPT_PACKET_ID,
    SAFETY_COMPLIANCE_ID,
    SAFETY_LOCKS,
    SHELL_ID,
    SUPPORT_CHANNEL_ID,
    SUPPORT_CHANNEL_PREVIEWS,
    WELCOME_ORIENTATION_DRAFTS,
    WELCOME_ORIENTATION_ID,
    WORKSPACE_ACCESS_ID,
    WORKSPACE_PREVIEWS,
    ensure_beta_onboarding_locked_experience_layer_schema,
    get_gp221_beta_onboarding_locked_experience_shell,
    get_gp221_status,
    get_gp222_locked_welcome_orientation_draft_board,
    get_gp222_status,
    get_gp223_beta_profile_setup_preview_lock,
    get_gp223_status,
    get_gp224_nda_policy_acknowledgment_preview_lock,
    get_gp224_status,
    get_gp225_beta_workspace_access_preview_lock,
    get_gp225_status,
    get_gp226_beta_support_channel_preview_board,
    get_gp226_status,
    get_gp227_beta_onboarding_qa_checklist,
    get_gp227_status,
    get_gp228_onboarding_safety_compliance_lock_board,
    get_gp228_status,
    get_gp229_beta_onboarding_receipt_draft_packet,
    get_gp229_status,
    get_gp230_beta_onboarding_locked_experience_readiness_checkpoint,
    get_gp230_status,
    get_beta_onboarding_locked_experience_layer_home,
    initialize_beta_onboarding_locked_experience_layer,
    render_beta_onboarding_locked_experience_layer_page,
    validate_beta_onboarding_locked_experience_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp221_230_db(tmp_path, monkeypatch):
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
        "VAULT_BETA_ACCESS_INVITE_LOCK_LAYER_DB": "gp211_220.sqlite",
        "VAULT_BETA_ONBOARDING_LOCKED_EXPERIENCE_LAYER_DB": "gp221_230.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp221_230.sqlite")

def test_gp221_230_schema_and_initialize(gp221_230_db):
    schema = ensure_beta_onboarding_locked_experience_layer_schema(gp221_230_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_beta_onboarding_components" in schema["tables"]
    assert "vault_locked_welcome_orientation_drafts" in schema["tables"]
    assert "vault_beta_onboarding_readiness" in schema["tables"]

    result = initialize_beta_onboarding_locked_experience_layer(gp221_230_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["welcome_orientation_count"] == len(WELCOME_ORIENTATION_DRAFTS)
    assert result["profile_preview_count"] == len(PROFILE_SETUP_PREVIEWS)
    assert result["policy_ack_lock_count"] == len(POLICY_ACK_LOCKS)
    assert result["workspace_preview_count"] == len(WORKSPACE_PREVIEWS)
    assert result["support_channel_count"] == len(SUPPORT_CHANNEL_PREVIEWS)
    assert result["qa_check_count"] == len(QA_CHECKS)
    assert result["safety_lock_count"] == len(SAFETY_LOCKS)
    assert result["receipt_packet_count"] == 1
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp221_shell(gp221_230_db):
    payload = get_gp221_beta_onboarding_locked_experience_shell(gp221_230_db)
    shell = payload["shell"]

    assert payload["pack"]["id"] == "VAULT_GP221"
    assert shell["component_id"] == SHELL_ID
    assert shell["gp_number"] == 221
    assert shell["source_gp220_readiness_score"] == 100
    assert len(shell["source_gp220_readiness_hash"]) == 64
    assert shell["component_ready"] is True
    assert shell["component_locked"] is True
    assert shell["onboarding_experience_ready"] is True
    assert shell["onboarding_preview_locked"] is True
    assert shell["profile_preview_locked"] is True
    assert shell["policy_ack_locked"] is True
    assert shell["workspace_preview_locked"] is True
    assert shell["support_preview_locked"] is True
    assert shell["vault_not_done"] is True

    for field in FALSE_FIELDS:
        assert shell[field] is False

def test_gp222_welcome_orientation(gp221_230_db):
    payload = get_gp222_locked_welcome_orientation_draft_board(gp221_230_db)
    rows = payload["drafts"]

    assert payload["pack"]["id"] == "VAULT_GP222"
    assert payload["welcome_orientation_board"]["component_id"] == WELCOME_ORIENTATION_ID
    assert payload["welcome_orientation_count"] == len(WELCOME_ORIENTATION_DRAFTS)
    assert all(item["draft_ready"] is True for item in rows)
    assert all(item["draft_locked"] is True for item in rows)
    assert all(item["welcome_acknowledged"] is False for item in rows)
    assert all(item["orientation_started"] is False for item in rows)
    assert all(item["orientation_completed"] is False for item in rows)

def test_gp223_profile_setup(gp221_230_db):
    payload = get_gp223_beta_profile_setup_preview_lock(gp221_230_db)
    rows = payload["previews"]

    assert payload["pack"]["id"] == "VAULT_GP223"
    assert payload["profile_setup_preview_lock"]["component_id"] == PROFILE_SETUP_ID
    assert payload["profile_preview_count"] == len(PROFILE_SETUP_PREVIEWS)
    assert all(item["preview_ready"] is True for item in rows)
    assert all(item["preview_locked"] is True for item in rows)
    assert all(item["submit_locked"] is True for item in rows)
    assert all(item["profile_created"] is False for item in rows)
    assert all(item["profile_submitted"] is False for item in rows)
    assert all(item["profile_approved"] is False for item in rows)

def test_gp224_policy_ack(gp221_230_db):
    payload = get_gp224_nda_policy_acknowledgment_preview_lock(gp221_230_db)
    rows = payload["policies"]

    assert payload["pack"]["id"] == "VAULT_GP224"
    assert payload["policy_acknowledgment_preview_lock"]["component_id"] == POLICY_ACK_ID
    assert payload["policy_ack_lock_count"] == len(POLICY_ACK_LOCKS)
    assert all(item["preview_ready"] is True for item in rows)
    assert all(item["acknowledgment_locked"] is True for item in rows)
    assert all(item["acceptance_record_locked"] is True for item in rows)
    assert all(item["nda_signed"] is False for item in rows)
    assert all(item["policy_acknowledged"] is False for item in rows)
    assert all(item["policy_acceptance_recorded"] is False for item in rows)

def test_gp225_workspace_access(gp221_230_db):
    payload = get_gp225_beta_workspace_access_preview_lock(gp221_230_db)
    rows = payload["workspaces"]

    assert payload["pack"]["id"] == "VAULT_GP225"
    assert payload["workspace_access_preview_lock"]["component_id"] == WORKSPACE_ACCESS_ID
    assert payload["workspace_preview_count"] == len(WORKSPACE_PREVIEWS)
    assert all(item["workspace_preview_ready"] is True for item in rows)
    assert all(item["workspace_open_locked"] is True for item in rows)
    assert all(item["workspace_session_locked"] is True for item in rows)
    assert all(item["workspace_opened"] is False for item in rows)
    assert all(item["workspace_access_granted"] is False for item in rows)
    assert all(item["workspace_session_created"] is False for item in rows)

def test_gp226_support_channels(gp221_230_db):
    payload = get_gp226_beta_support_channel_preview_board(gp221_230_db)
    rows = payload["channels"]

    assert payload["pack"]["id"] == "VAULT_GP226"
    assert payload["support_channel_preview_board"]["component_id"] == SUPPORT_CHANNEL_ID
    assert payload["support_channel_count"] == len(SUPPORT_CHANNEL_PREVIEWS)
    assert all(item["channel_preview_ready"] is True for item in rows)
    assert all(item["channel_open_locked"] is True for item in rows)
    assert all(item["message_send_locked"] is True for item in rows)
    assert all(item["support_channel_opened"] is False for item in rows)
    assert all(item["support_message_sent"] is False for item in rows)

def test_gp227_qa_checklist(gp221_230_db):
    payload = get_gp227_beta_onboarding_qa_checklist(gp221_230_db)
    rows = payload["checks"]

    assert payload["pack"]["id"] == "VAULT_GP227"
    assert payload["qa_checklist"]["component_id"] == QA_CHECKLIST_ID
    assert payload["qa_check_count"] == len(QA_CHECKS)
    assert all(item["qa_ready"] is True for item in rows)
    assert all(item["qa_locked"] is True for item in rows)
    assert all(item["onboarding_started"] is False for item in rows)
    assert all(item["execution_enabled"] is False for item in rows)

def test_gp228_safety_compliance_locks(gp221_230_db):
    payload = get_gp228_onboarding_safety_compliance_lock_board(gp221_230_db)
    rows = payload["locks"]

    assert payload["pack"]["id"] == "VAULT_GP228"
    assert payload["safety_compliance_lock_board"]["component_id"] == SAFETY_COMPLIANCE_ID
    assert payload["safety_lock_count"] == len(SAFETY_LOCKS)
    assert all(item["lock_active"] is True for item in rows)
    assert all(item["blocks_onboarding_start"] is True for item in rows)
    assert all(item["blocks_profile_submit"] is True for item in rows)
    assert all(item["blocks_policy_accept"] is True for item in rows)
    assert all(item["blocks_workspace_open"] is True for item in rows)
    assert all(item["blocks_support_send"] is True for item in rows)
    assert all(item["blocks_feedback_issue_submit"] is True for item in rows)
    assert all(item["blocks_tower_gate"] is True for item in rows)
    assert all(item["blocks_billing_subscription"] is True for item in rows)
    assert all(item["blocks_provider_unlock"] is True for item in rows)
    assert all(item["blocks_provider_api"] is True for item in rows)
    assert all(item["blocks_object_body"] is True for item in rows)
    assert all(item["blocks_download"] is True for item in rows)
    assert all(item["blocks_restore"] is True for item in rows)
    assert all(item["blocks_export"] is True for item in rows)
    assert all(item["blocks_direct_upload"] is True for item in rows)
    assert all(item["blocks_delete"] is True for item in rows)
    assert all(item["blocks_execution"] is True for item in rows)
    assert all(item["blocks_vault_done"] is True for item in rows)
    assert all(item["resolved"] is False for item in rows)

def test_gp229_receipt_packet(gp221_230_db):
    payload = get_gp229_beta_onboarding_receipt_draft_packet(gp221_230_db)
    packets = payload["packets"]

    assert payload["pack"]["id"] == "VAULT_GP229"
    assert payload["receipt_packet_component"]["component_id"] == RECEIPT_PACKET_ID
    assert payload["receipt_packet_count"] == 1
    assert packets[0]["packet_ready"] is True
    assert packets[0]["packet_locked"] is True
    assert packets[0]["final_onboarding_receipt"] is False
    assert packets[0]["onboarding_started"] is False
    assert packets[0]["vault_done"] is False
    assert len(packets[0]["packet_hash"]) == 64

def test_gp230_readiness_home_status_validation(gp221_230_db):
    payload = get_gp230_beta_onboarding_locked_experience_readiness_checkpoint(gp221_230_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP230"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["welcome_orientation_count"] == len(WELCOME_ORIENTATION_DRAFTS)
    assert readiness["profile_preview_count"] == len(PROFILE_SETUP_PREVIEWS)
    assert readiness["policy_ack_lock_count"] == len(POLICY_ACK_LOCKS)
    assert readiness["workspace_preview_count"] == len(WORKSPACE_PREVIEWS)
    assert readiness["support_channel_count"] == len(SUPPORT_CHANNEL_PREVIEWS)
    assert readiness["qa_check_count"] == len(QA_CHECKS)
    assert readiness["safety_lock_count"] == len(SAFETY_LOCKS)
    assert readiness["receipt_packet_count"] == 1
    assert readiness["onboarding_experience_ready"] is True
    assert readiness["onboarding_preview_locked"] is True
    assert readiness["profile_preview_locked"] is True
    assert readiness["policy_ack_locked"] is True
    assert readiness["workspace_preview_locked"] is True
    assert readiness["support_preview_locked"] is True
    assert readiness["safe_to_continue_to_gp231"] is True
    assert readiness["section_ready"] is True
    assert readiness["vault_done"] is False
    assert readiness["clouds_should_continue"] is False
    assert validation["valid"] is True
    assert validation["failed_count"] == 0

    status = get_gp230_status(gp221_230_db)["gp230_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp231"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_BETA_FEEDBACK_AND_ISSUE_INTAKE_LOCK_LAYER"
    assert status["next_section_range"] == "GP231-GP240"
    assert status["next_pack"] == "VAULT_GP231_240_BETA_FEEDBACK_AND_ISSUE_INTAKE_LOCK_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp230"

    home = get_beta_onboarding_locked_experience_layer_home(gp221_230_db)
    assert home["pack"]["id"] == "VAULT_GP221_230"
    assert home["truth"]["beta_onboarding_locked_experience_layer_ready"] is True
    assert home["truth"]["safe_to_continue_to_gp231"] is True
    assert home["truth"]["onboarding_preview_locked"] is True
    assert home["truth"]["profile_preview_locked"] is True
    assert home["truth"]["policy_ack_locked"] is True
    assert home["truth"]["workspace_preview_locked"] is True
    assert home["truth"]["support_preview_locked"] is True
    assert home["truth"]["onboarding_started"] is False
    assert home["truth"]["onboarding_completed"] is False
    assert home["truth"]["profile_created"] is False
    assert home["truth"]["profile_submitted"] is False
    assert home["truth"]["nda_signed"] is False
    assert home["truth"]["policy_acknowledged"] is False
    assert home["truth"]["workspace_opened"] is False
    assert home["truth"]["support_channel_opened"] is False
    assert home["truth"]["support_message_sent"] is False
    assert home["truth"]["feedback_submitted"] is False
    assert home["truth"]["issue_submitted"] is False
    assert home["truth"]["tower_gate_opened"] is False
    assert home["truth"]["tower_unlock_granted"] is False
    assert home["truth"]["billing_flow_created"] is False
    assert home["truth"]["provider_api_called"] is False
    assert home["truth"]["provider_metadata_read"] is False
    assert home["truth"]["object_body_read"] is False
    assert home["truth"]["object_download_enabled"] is False
    assert home["truth"]["export_package_created"] is False
    assert home["truth"]["restore_job_created"] is False
    assert home["truth"]["execution_enabled"] is False
    assert home["truth"]["vault_done"] is False

def test_gp221_230_all_status_endpoints(gp221_230_db):
    funcs = [
        (221, get_gp221_status, "gp221_status"),
        (222, get_gp222_status, "gp222_status"),
        (223, get_gp223_status, "gp223_status"),
        (224, get_gp224_status, "gp224_status"),
        (225, get_gp225_status, "gp225_status"),
        (226, get_gp226_status, "gp226_status"),
        (227, get_gp227_status, "gp227_status"),
        (228, get_gp228_status, "gp228_status"),
        (229, get_gp229_status, "gp229_status"),
        (230, get_gp230_status, "gp230_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp221_230_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp231"] is True
        assert status["source_gp220_readiness_score"] == 100
        assert len(status["source_gp220_readiness_hash"]) == 64
        assert status["component_count"] == 10
        assert status["welcome_orientation_count"] == len(WELCOME_ORIENTATION_DRAFTS)
        assert status["safety_lock_count"] == len(SAFETY_LOCKS)
        assert status["onboarding_experience_ready"] is True
        assert status["onboarding_preview_locked"] is True
        assert status["profile_preview_locked"] is True
        assert status["policy_ack_locked"] is True
        assert status["workspace_preview_locked"] is True
        assert status["support_preview_locked"] is True
        assert status["beta_launch_approved"] is False
        assert status["beta_invite_sent"] is False
        assert status["beta_tester_added"] is False
        assert status["beta_tester_access_granted"] is False
        assert status["beta_access_token_created"] is False
        assert status["onboarding_started"] is False
        assert status["onboarding_completed"] is False
        assert status["profile_created"] is False
        assert status["profile_submitted"] is False
        assert status["nda_signed"] is False
        assert status["policy_acknowledged"] is False
        assert status["workspace_opened"] is False
        assert status["support_channel_opened"] is False
        assert status["feedback_submitted"] is False
        assert status["issue_submitted"] is False
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

def test_gp221_230_html_is_dark_and_routes_registered(gp221_230_db):
    html = render_beta_onboarding_locked_experience_layer_page()
    lowered = html.lower()
    assert "Vault GP221-GP230 Beta Onboarding Locked Experience Layer" in html
    assert "GP221-GP230 built" in html
    assert "Safe to GP231" in html
    assert "No onboarding started" in html
    assert "No profile submit" in html
    assert "No policy accepted" in html
    assert "No workspace opened" in html
    assert "No support send" in html
    assert "No Tower gate" in html
    assert "No execution" in html
    assert "Vault not done" in html
    assert "VAULT_GP231_240_BETA_FEEDBACK_AND_ISSUE_INTAKE_LOCK_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/beta-onboarding-locked-experience-layer",
        "/vault/beta-onboarding-locked-experience-layer.json",
        "/vault/beta-onboarding-locked-experience-shell.json",
        "/vault/locked-welcome-orientation-draft-board.json",
        "/vault/beta-profile-setup-preview-lock.json",
        "/vault/nda-policy-acknowledgment-preview-lock.json",
        "/vault/beta-workspace-access-preview-lock.json",
        "/vault/beta-support-channel-preview-board.json",
        "/vault/beta-onboarding-qa-checklist.json",
        "/vault/onboarding-safety-compliance-lock-board.json",
        "/vault/beta-onboarding-receipt-draft-packet.json",
        "/vault/beta-onboarding-locked-experience-readiness-checkpoint.json",
        "/vault/gp221-status.json",
        "/vault/gp222-status.json",
        "/vault/gp223-status.json",
        "/vault/gp224-status.json",
        "/vault/gp225-status.json",
        "/vault/gp226-status.json",
        "/vault/gp227-status.json",
        "/vault/gp228-status.json",
        "/vault/gp229-status.json",
        "/vault/gp230-status.json",
    ]
    for route in required_routes:
        assert route in text
