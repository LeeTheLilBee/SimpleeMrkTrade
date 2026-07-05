"""
Tests for VAULT GP231-GP240 — Beta Feedback and Issue Intake Lock Layer
"""

from pathlib import Path
import pytest

from vault.beta_feedback_issue_intake_lock_layer_service import (
    FALSE_FIELDS,
    FEEDBACK_FORM_ID,
    FEEDBACK_FORMS,
    FEEDBACK_SUBMIT_LOCK_ID,
    FEEDBACK_SUBMIT_LOCKS,
    ISSUE_REPORT_ID,
    ISSUE_REPORTS,
    ISSUE_SUBMIT_LOCK_ID,
    ISSUE_SUBMIT_LOCKS,
    READINESS_ID,
    RECEIPT_PACKET_ID,
    ROUTING_PREVIEW_ID,
    ROUTING_PREVIEWS,
    SAFETY_COMPLIANCE_ID,
    SAFETY_LOCKS,
    SHELL_ID,
    SUPPORT_MESSAGE_LOCK_ID,
    SUPPORT_MESSAGE_LOCKS,
    ensure_beta_feedback_issue_intake_lock_layer_schema,
    get_gp231_beta_feedback_issue_intake_lock_shell,
    get_gp231_status,
    get_gp232_feedback_form_draft_registry,
    get_gp232_status,
    get_gp233_issue_report_draft_registry,
    get_gp233_status,
    get_gp234_feedback_submit_lock_contract,
    get_gp234_status,
    get_gp235_issue_submit_lock_contract,
    get_gp235_status,
    get_gp236_support_message_lock_contract,
    get_gp236_status,
    get_gp237_intake_routing_preview_board,
    get_gp237_status,
    get_gp238_intake_safety_compliance_lock_board,
    get_gp238_status,
    get_gp239_feedback_issue_intake_receipt_draft_packet,
    get_gp239_status,
    get_gp240_feedback_issue_intake_lock_readiness_checkpoint,
    get_gp240_status,
    get_beta_feedback_issue_intake_lock_layer_home,
    initialize_beta_feedback_issue_intake_lock_layer,
    render_beta_feedback_issue_intake_lock_layer_page,
    validate_beta_feedback_issue_intake_lock_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp231_240_db(tmp_path, monkeypatch):
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
        "VAULT_BETA_FEEDBACK_ISSUE_INTAKE_LOCK_LAYER_DB": "gp231_240.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp231_240.sqlite")

def test_gp231_240_schema_and_initialize(gp231_240_db):
    schema = ensure_beta_feedback_issue_intake_lock_layer_schema(gp231_240_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_beta_feedback_issue_intake_components" in schema["tables"]
    assert "vault_feedback_form_draft_registry" in schema["tables"]
    assert "vault_feedback_issue_intake_readiness" in schema["tables"]

    result = initialize_beta_feedback_issue_intake_lock_layer(gp231_240_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["feedback_form_count"] == len(FEEDBACK_FORMS)
    assert result["issue_report_count"] == len(ISSUE_REPORTS)
    assert result["feedback_submit_lock_count"] == len(FEEDBACK_SUBMIT_LOCKS)
    assert result["issue_submit_lock_count"] == len(ISSUE_SUBMIT_LOCKS)
    assert result["support_message_lock_count"] == len(SUPPORT_MESSAGE_LOCKS)
    assert result["routing_preview_count"] == len(ROUTING_PREVIEWS)
    assert result["safety_lock_count"] == len(SAFETY_LOCKS)
    assert result["receipt_packet_count"] == 1
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp231_shell(gp231_240_db):
    payload = get_gp231_beta_feedback_issue_intake_lock_shell(gp231_240_db)
    shell = payload["shell"]

    assert payload["pack"]["id"] == "VAULT_GP231"
    assert shell["component_id"] == SHELL_ID
    assert shell["gp_number"] == 231
    assert shell["source_gp230_readiness_score"] == 100
    assert len(shell["source_gp230_readiness_hash"]) == 64
    assert shell["component_ready"] is True
    assert shell["component_locked"] is True
    assert shell["feedback_intake_ready"] is True
    assert shell["issue_intake_ready"] is True
    assert shell["submit_locks_active"] is True
    assert shell["routing_preview_only"] is True
    assert shell["support_message_locked"] is True
    assert shell["vault_not_done"] is True

    for field in FALSE_FIELDS:
        assert shell[field] is False

def test_gp232_feedback_forms(gp231_240_db):
    payload = get_gp232_feedback_form_draft_registry(gp231_240_db)
    rows = payload["forms"]

    assert payload["pack"]["id"] == "VAULT_GP232"
    assert payload["feedback_form_registry"]["component_id"] == FEEDBACK_FORM_ID
    assert payload["feedback_form_count"] == len(FEEDBACK_FORMS)
    assert all(item["form_ready"] is True for item in rows)
    assert all(item["form_locked"] is True for item in rows)
    assert all(item["submit_locked"] is True for item in rows)
    assert all(item["feedback_form_opened"] is False for item in rows)
    assert all(item["feedback_submitted"] is False for item in rows)

def test_gp233_issue_reports(gp231_240_db):
    payload = get_gp233_issue_report_draft_registry(gp231_240_db)
    rows = payload["reports"]

    assert payload["pack"]["id"] == "VAULT_GP233"
    assert payload["issue_report_registry"]["component_id"] == ISSUE_REPORT_ID
    assert payload["issue_report_count"] == len(ISSUE_REPORTS)
    assert all(item["report_ready"] is True for item in rows)
    assert all(item["report_locked"] is True for item in rows)
    assert all(item["submit_locked"] is True for item in rows)
    assert all(item["issue_report_opened"] is False for item in rows)
    assert all(item["issue_created"] is False for item in rows)
    assert all(item["issue_submitted"] is False for item in rows)

def test_gp234_feedback_submit_locks(gp231_240_db):
    payload = get_gp234_feedback_submit_lock_contract(gp231_240_db)
    rows = payload["locks"]

    assert payload["pack"]["id"] == "VAULT_GP234"
    assert payload["feedback_submit_lock_contract"]["component_id"] == FEEDBACK_SUBMIT_LOCK_ID
    assert payload["feedback_submit_lock_count"] == len(FEEDBACK_SUBMIT_LOCKS)
    assert all(item["feedback_submit_locked"] is True for item in rows)
    assert all(item["feedback_receipt_locked"] is True for item in rows)
    assert all(item["feedback_submitted"] is False for item in rows)
    assert all(item["feedback_received"] is False for item in rows)
    assert all(item["feedback_receipt_finalized"] is False for item in rows)

def test_gp235_issue_submit_locks(gp231_240_db):
    payload = get_gp235_issue_submit_lock_contract(gp231_240_db)
    rows = payload["locks"]

    assert payload["pack"]["id"] == "VAULT_GP235"
    assert payload["issue_submit_lock_contract"]["component_id"] == ISSUE_SUBMIT_LOCK_ID
    assert payload["issue_submit_lock_count"] == len(ISSUE_SUBMIT_LOCKS)
    assert all(item["issue_submit_locked"] is True for item in rows)
    assert all(item["issue_receipt_locked"] is True for item in rows)
    assert all(item["issue_created"] is False for item in rows)
    assert all(item["issue_submitted"] is False for item in rows)
    assert all(item["issue_receipt_finalized"] is False for item in rows)

def test_gp236_support_message_locks(gp231_240_db):
    payload = get_gp236_support_message_lock_contract(gp231_240_db)
    rows = payload["locks"]

    assert payload["pack"]["id"] == "VAULT_GP236"
    assert payload["support_message_lock_contract"]["component_id"] == SUPPORT_MESSAGE_LOCK_ID
    assert payload["support_message_lock_count"] == len(SUPPORT_MESSAGE_LOCKS)
    assert all(item["support_message_locked"] is True for item in rows)
    assert all(item["support_ticket_locked"] is True for item in rows)
    assert all(item["support_message_created"] is False for item in rows)
    assert all(item["support_message_sent"] is False for item in rows)
    assert all(item["support_ticket_created"] is False for item in rows)

def test_gp237_routing_previews(gp231_240_db):
    payload = get_gp237_intake_routing_preview_board(gp231_240_db)
    rows = payload["routes"]

    assert payload["pack"]["id"] == "VAULT_GP237"
    assert payload["routing_preview_board"]["component_id"] == ROUTING_PREVIEW_ID
    assert payload["routing_preview_count"] == len(ROUTING_PREVIEWS)
    assert all(item["preview_ready"] is True for item in rows)
    assert all(item["routing_locked"] is True for item in rows)
    assert all(item["triage_locked"] is True for item in rows)
    assert all(item["escalation_locked"] is True for item in rows)
    assert all(item["intake_routing_executed"] is False for item in rows)
    assert all(item["intake_triage_started"] is False for item in rows)
    assert all(item["intake_escalation_sent"] is False for item in rows)

def test_gp238_safety_compliance_locks(gp231_240_db):
    payload = get_gp238_intake_safety_compliance_lock_board(gp231_240_db)
    rows = payload["locks"]

    assert payload["pack"]["id"] == "VAULT_GP238"
    assert payload["safety_compliance_lock_board"]["component_id"] == SAFETY_COMPLIANCE_ID
    assert payload["safety_lock_count"] == len(SAFETY_LOCKS)
    assert all(item["lock_active"] is True for item in rows)
    assert all(item["blocks_feedback_submit"] is True for item in rows)
    assert all(item["blocks_issue_submit"] is True for item in rows)
    assert all(item["blocks_support_send"] is True for item in rows)
    assert all(item["blocks_routing"] is True for item in rows)
    assert all(item["blocks_triage"] is True for item in rows)
    assert all(item["blocks_escalation"] is True for item in rows)
    assert all(item["blocks_ticket_creation"] is True for item in rows)
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

def test_gp239_receipt_packet(gp231_240_db):
    payload = get_gp239_feedback_issue_intake_receipt_draft_packet(gp231_240_db)
    packets = payload["packets"]

    assert payload["pack"]["id"] == "VAULT_GP239"
    assert payload["receipt_packet_component"]["component_id"] == RECEIPT_PACKET_ID
    assert payload["receipt_packet_count"] == 1
    assert packets[0]["packet_ready"] is True
    assert packets[0]["packet_locked"] is True
    assert packets[0]["final_feedback_receipt"] is False
    assert packets[0]["final_issue_receipt"] is False
    assert packets[0]["feedback_submitted"] is False
    assert packets[0]["issue_submitted"] is False
    assert packets[0]["vault_done"] is False
    assert len(packets[0]["packet_hash"]) == 64

def test_gp240_readiness_home_status_validation(gp231_240_db):
    payload = get_gp240_feedback_issue_intake_lock_readiness_checkpoint(gp231_240_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP240"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["feedback_form_count"] == len(FEEDBACK_FORMS)
    assert readiness["issue_report_count"] == len(ISSUE_REPORTS)
    assert readiness["feedback_submit_lock_count"] == len(FEEDBACK_SUBMIT_LOCKS)
    assert readiness["issue_submit_lock_count"] == len(ISSUE_SUBMIT_LOCKS)
    assert readiness["support_message_lock_count"] == len(SUPPORT_MESSAGE_LOCKS)
    assert readiness["routing_preview_count"] == len(ROUTING_PREVIEWS)
    assert readiness["safety_lock_count"] == len(SAFETY_LOCKS)
    assert readiness["receipt_packet_count"] == 1
    assert readiness["feedback_intake_ready"] is True
    assert readiness["issue_intake_ready"] is True
    assert readiness["submit_locks_active"] is True
    assert readiness["routing_preview_only"] is True
    assert readiness["support_message_locked"] is True
    assert readiness["safe_to_continue_to_gp241"] is True
    assert readiness["section_ready"] is True
    assert readiness["vault_done"] is False
    assert readiness["clouds_should_continue"] is False
    assert validation["valid"] is True
    assert validation["failed_count"] == 0

    status = get_gp240_status(gp231_240_db)["gp240_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp241"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_BETA_FEEDBACK_REVIEW_AND_TRIAGE_LOCK_LAYER"
    assert status["next_section_range"] == "GP241-GP250"
    assert status["next_pack"] == "VAULT_GP241_250_BETA_FEEDBACK_REVIEW_AND_TRIAGE_LOCK_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp240"

    home = get_beta_feedback_issue_intake_lock_layer_home(gp231_240_db)
    assert home["pack"]["id"] == "VAULT_GP231_240"
    assert home["truth"]["beta_feedback_issue_intake_lock_layer_ready"] is True
    assert home["truth"]["safe_to_continue_to_gp241"] is True
    assert home["truth"]["feedback_submitted"] is False
    assert home["truth"]["issue_created"] is False
    assert home["truth"]["issue_submitted"] is False
    assert home["truth"]["support_message_sent"] is False
    assert home["truth"]["intake_routing_executed"] is False
    assert home["truth"]["intake_triage_started"] is False
    assert home["truth"]["intake_escalation_sent"] is False
    assert home["truth"]["support_ticket_created"] is False
    assert home["truth"]["bug_ticket_created"] is False
    assert home["truth"]["feedback_review_started"] is False
    assert home["truth"]["issue_review_started"] is False
    assert home["truth"]["tower_gate_opened"] is False
    assert home["truth"]["billing_flow_created"] is False
    assert home["truth"]["provider_api_called"] is False
    assert home["truth"]["provider_metadata_read"] is False
    assert home["truth"]["object_body_read"] is False
    assert home["truth"]["object_download_enabled"] is False
    assert home["truth"]["export_package_created"] is False
    assert home["truth"]["restore_job_created"] is False
    assert home["truth"]["execution_enabled"] is False
    assert home["truth"]["vault_done"] is False

def test_gp231_240_all_status_endpoints(gp231_240_db):
    funcs = [
        (231, get_gp231_status, "gp231_status"),
        (232, get_gp232_status, "gp232_status"),
        (233, get_gp233_status, "gp233_status"),
        (234, get_gp234_status, "gp234_status"),
        (235, get_gp235_status, "gp235_status"),
        (236, get_gp236_status, "gp236_status"),
        (237, get_gp237_status, "gp237_status"),
        (238, get_gp238_status, "gp238_status"),
        (239, get_gp239_status, "gp239_status"),
        (240, get_gp240_status, "gp240_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp231_240_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp241"] is True
        assert status["source_gp230_readiness_score"] == 100
        assert len(status["source_gp230_readiness_hash"]) == 64
        assert status["component_count"] == 10
        assert status["feedback_form_count"] == len(FEEDBACK_FORMS)
        assert status["issue_report_count"] == len(ISSUE_REPORTS)
        assert status["safety_lock_count"] == len(SAFETY_LOCKS)
        assert status["feedback_intake_ready"] is True
        assert status["issue_intake_ready"] is True
        assert status["submit_locks_active"] is True
        assert status["routing_preview_only"] is True
        assert status["support_message_locked"] is True
        assert status["feedback_submitted"] is False
        assert status["issue_created"] is False
        assert status["issue_submitted"] is False
        assert status["support_message_sent"] is False
        assert status["intake_routing_executed"] is False
        assert status["intake_triage_started"] is False
        assert status["intake_escalation_sent"] is False
        assert status["support_ticket_created"] is False
        assert status["bug_ticket_created"] is False
        assert status["feedback_review_started"] is False
        assert status["issue_review_started"] is False
        assert status["onboarding_started"] is False
        assert status["profile_submitted"] is False
        assert status["policy_acknowledged"] is False
        assert status["workspace_opened"] is False
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

def test_gp231_240_html_is_dark_and_routes_registered(gp231_240_db):
    html = render_beta_feedback_issue_intake_lock_layer_page()
    lowered = html.lower()
    assert "Vault GP231-GP240 Beta Feedback Issue Intake Lock Layer" in html
    assert "GP231-GP240 built" in html
    assert "Safe to GP241" in html
    assert "No feedback submit" in html
    assert "No issue submit" in html
    assert "No support message" in html
    assert "No routing" in html
    assert "No triage" in html
    assert "No escalation" in html
    assert "No execution" in html
    assert "Vault not done" in html
    assert "VAULT_GP241_250_BETA_FEEDBACK_REVIEW_AND_TRIAGE_LOCK_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/beta-feedback-issue-intake-lock-layer",
        "/vault/beta-feedback-issue-intake-lock-layer.json",
        "/vault/beta-feedback-issue-intake-lock-shell.json",
        "/vault/feedback-form-draft-registry.json",
        "/vault/issue-report-draft-registry.json",
        "/vault/feedback-submit-lock-contract.json",
        "/vault/issue-submit-lock-contract.json",
        "/vault/support-message-lock-contract.json",
        "/vault/intake-routing-preview-board.json",
        "/vault/intake-safety-compliance-lock-board.json",
        "/vault/feedback-issue-intake-receipt-draft-packet.json",
        "/vault/feedback-issue-intake-lock-readiness-checkpoint.json",
        "/vault/gp231-status.json",
        "/vault/gp232-status.json",
        "/vault/gp233-status.json",
        "/vault/gp234-status.json",
        "/vault/gp235-status.json",
        "/vault/gp236-status.json",
        "/vault/gp237-status.json",
        "/vault/gp238-status.json",
        "/vault/gp239-status.json",
        "/vault/gp240-status.json",
    ]
    for route in required_routes:
        assert route in text
