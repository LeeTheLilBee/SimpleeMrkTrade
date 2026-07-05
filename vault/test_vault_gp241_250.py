"""
Tests for VAULT GP241-GP250 — Beta Feedback Review and Triage Lock Layer
"""

from pathlib import Path
import pytest

from vault.beta_feedback_review_triage_lock_layer_service import (
    ASSIGNMENT_LOCK_ID,
    ASSIGNMENT_LOCKS,
    ESCALATION_LOCK_ID,
    ESCALATION_LOCKS,
    FALSE_FIELDS,
    FEEDBACK_REVIEW_DRAFTS,
    FEEDBACK_REVIEW_ID,
    FIX_ROOM_HANDOFF_ID,
    FIX_ROOM_HANDOFFS,
    ISSUE_REVIEW_DRAFTS,
    ISSUE_REVIEW_ID,
    READINESS_ID,
    RECEIPT_PACKET_ID,
    REVIEWER_DECISION_ID,
    REVIEWER_DECISION_LOCKS,
    SHELL_ID,
    TRIAGE_CLASSIFICATIONS,
    TRIAGE_MATRIX_ID,
    ensure_beta_feedback_review_triage_lock_layer_schema,
    get_gp241_beta_feedback_review_triage_lock_shell,
    get_gp241_status,
    get_gp242_feedback_review_draft_queue,
    get_gp242_status,
    get_gp243_issue_review_draft_queue,
    get_gp243_status,
    get_gp244_triage_classification_preview_matrix,
    get_gp244_status,
    get_gp245_assignment_lock_contract,
    get_gp245_status,
    get_gp246_escalation_lock_contract,
    get_gp246_status,
    get_gp247_fix_room_handoff_preview,
    get_gp247_status,
    get_gp248_reviewer_decision_lock_board,
    get_gp248_status,
    get_gp249_review_triage_receipt_draft_packet,
    get_gp249_status,
    get_gp250_review_triage_lock_readiness_checkpoint,
    get_gp250_status,
    get_beta_feedback_review_triage_lock_layer_home,
    initialize_beta_feedback_review_triage_lock_layer,
    render_beta_feedback_review_triage_lock_layer_page,
    validate_beta_feedback_review_triage_lock_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp241_250_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp241_250.sqlite")

def test_gp241_250_schema_and_initialize(gp241_250_db):
    schema = ensure_beta_feedback_review_triage_lock_layer_schema(gp241_250_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_beta_feedback_review_triage_components" in schema["tables"]
    assert "vault_feedback_review_draft_queue" in schema["tables"]
    assert "vault_review_triage_readiness" in schema["tables"]

    result = initialize_beta_feedback_review_triage_lock_layer(gp241_250_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["feedback_review_count"] == len(FEEDBACK_REVIEW_DRAFTS)
    assert result["issue_review_count"] == len(ISSUE_REVIEW_DRAFTS)
    assert result["triage_classification_count"] == len(TRIAGE_CLASSIFICATIONS)
    assert result["assignment_lock_count"] == len(ASSIGNMENT_LOCKS)
    assert result["escalation_lock_count"] == len(ESCALATION_LOCKS)
    assert result["fix_room_handoff_count"] == len(FIX_ROOM_HANDOFFS)
    assert result["reviewer_decision_lock_count"] == len(REVIEWER_DECISION_LOCKS)
    assert result["receipt_packet_count"] == 1
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp241_shell(gp241_250_db):
    payload = get_gp241_beta_feedback_review_triage_lock_shell(gp241_250_db)
    shell = payload["shell"]

    assert payload["pack"]["id"] == "VAULT_GP241"
    assert shell["component_id"] == SHELL_ID
    assert shell["gp_number"] == 241
    assert shell["source_gp240_readiness_score"] == 100
    assert len(shell["source_gp240_readiness_hash"]) == 64
    assert shell["component_ready"] is True
    assert shell["component_locked"] is True
    assert shell["review_triage_ready"] is True
    assert shell["review_lock_active"] is True
    assert shell["triage_lock_active"] is True
    assert shell["assignment_lock_active"] is True
    assert shell["escalation_lock_active"] is True
    assert shell["fix_room_preview_only"] is True
    assert shell["reviewer_decision_locked"] is True
    assert shell["vault_not_done"] is True

    for field in FALSE_FIELDS:
        assert shell[field] is False

def test_gp242_feedback_review_queue(gp241_250_db):
    payload = get_gp242_feedback_review_draft_queue(gp241_250_db)
    rows = payload["reviews"]

    assert payload["pack"]["id"] == "VAULT_GP242"
    assert payload["feedback_review_queue"]["component_id"] == FEEDBACK_REVIEW_ID
    assert payload["feedback_review_count"] == len(FEEDBACK_REVIEW_DRAFTS)
    assert all(item["review_ready"] is True for item in rows)
    assert all(item["review_locked"] is True for item in rows)
    assert all(item["decision_locked"] is True for item in rows)
    assert all(item["feedback_review_started"] is False for item in rows)
    assert all(item["feedback_review_completed"] is False for item in rows)
    assert all(item["feedback_review_decision_recorded"] is False for item in rows)

def test_gp243_issue_review_queue(gp241_250_db):
    payload = get_gp243_issue_review_draft_queue(gp241_250_db)
    rows = payload["reviews"]

    assert payload["pack"]["id"] == "VAULT_GP243"
    assert payload["issue_review_queue"]["component_id"] == ISSUE_REVIEW_ID
    assert payload["issue_review_count"] == len(ISSUE_REVIEW_DRAFTS)
    assert all(item["review_ready"] is True for item in rows)
    assert all(item["review_locked"] is True for item in rows)
    assert all(item["decision_locked"] is True for item in rows)
    assert all(item["issue_review_started"] is False for item in rows)
    assert all(item["issue_review_completed"] is False for item in rows)
    assert all(item["issue_review_decision_recorded"] is False for item in rows)

def test_gp244_triage_matrix(gp241_250_db):
    payload = get_gp244_triage_classification_preview_matrix(gp241_250_db)
    rows = payload["classifications"]

    assert payload["pack"]["id"] == "VAULT_GP244"
    assert payload["triage_classification_matrix"]["component_id"] == TRIAGE_MATRIX_ID
    assert payload["triage_classification_count"] == len(TRIAGE_CLASSIFICATIONS)
    assert all(item["preview_ready"] is True for item in rows)
    assert all(item["classification_locked"] is True for item in rows)
    assert all(item["priority_locked"] is True for item in rows)
    assert all(item["severity_locked"] is True for item in rows)
    assert all(item["triage_classification_applied"] is False for item in rows)
    assert all(item["triage_priority_applied"] is False for item in rows)
    assert all(item["triage_severity_applied"] is False for item in rows)

def test_gp245_assignment_locks(gp241_250_db):
    payload = get_gp245_assignment_lock_contract(gp241_250_db)
    rows = payload["locks"]

    assert payload["pack"]["id"] == "VAULT_GP245"
    assert payload["assignment_lock_contract"]["component_id"] == ASSIGNMENT_LOCK_ID
    assert payload["assignment_lock_count"] == len(ASSIGNMENT_LOCKS)
    assert all(item["assignment_locked"] is True for item in rows)
    assert all(item["notification_locked"] is True for item in rows)
    assert all(item["acceptance_locked"] is True for item in rows)
    assert all(item["assignment_created"] is False for item in rows)
    assert all(item["assignment_sent"] is False for item in rows)
    assert all(item["assignee_notified"] is False for item in rows)

def test_gp246_escalation_locks(gp241_250_db):
    payload = get_gp246_escalation_lock_contract(gp241_250_db)
    rows = payload["locks"]

    assert payload["pack"]["id"] == "VAULT_GP246"
    assert payload["escalation_lock_contract"]["component_id"] == ESCALATION_LOCK_ID
    assert payload["escalation_lock_count"] == len(ESCALATION_LOCKS)
    assert all(item["escalation_locked"] is True for item in rows)
    assert all(item["escalation_send_locked"] is True for item in rows)
    assert all(item["acknowledgment_locked"] is True for item in rows)
    assert all(item["intake_escalation_created"] is False for item in rows)
    assert all(item["intake_escalation_sent"] is False for item in rows)
    assert all(item["escalation_acknowledged"] is False for item in rows)

def test_gp247_fix_room_handoff(gp241_250_db):
    payload = get_gp247_fix_room_handoff_preview(gp241_250_db)
    rows = payload["handoffs"]

    assert payload["pack"]["id"] == "VAULT_GP247"
    assert payload["fix_room_handoff_preview"]["component_id"] == FIX_ROOM_HANDOFF_ID
    assert payload["fix_room_handoff_count"] == len(FIX_ROOM_HANDOFFS)
    assert all(item["preview_ready"] is True for item in rows)
    assert all(item["fix_room_open_locked"] is True for item in rows)
    assert all(item["handoff_locked"] is True for item in rows)
    assert all(item["fix_task_locked"] is True for item in rows)
    assert all(item["fix_room_opened"] is False for item in rows)
    assert all(item["fix_room_handoff_sent"] is False for item in rows)
    assert all(item["fix_task_created"] is False for item in rows)

def test_gp248_reviewer_decisions(gp241_250_db):
    payload = get_gp248_reviewer_decision_lock_board(gp241_250_db)
    rows = payload["decisions"]

    assert payload["pack"]["id"] == "VAULT_GP248"
    assert payload["reviewer_decision_lock_board"]["component_id"] == REVIEWER_DECISION_ID
    assert payload["reviewer_decision_lock_count"] == len(REVIEWER_DECISION_LOCKS)
    assert all(item["decision_locked"] is True for item in rows)
    assert all(item["approval_locked"] is True for item in rows)
    assert all(item["rejection_locked"] is True for item in rows)
    assert all(item["closeout_locked"] is True for item in rows)
    assert all(item["reviewer_decision_recorded"] is False for item in rows)
    assert all(item["reviewer_approval_recorded"] is False for item in rows)
    assert all(item["reviewer_closeout_recorded"] is False for item in rows)

def test_gp249_receipt_packet(gp241_250_db):
    payload = get_gp249_review_triage_receipt_draft_packet(gp241_250_db)
    packets = payload["packets"]

    assert payload["pack"]["id"] == "VAULT_GP249"
    assert payload["receipt_packet_component"]["component_id"] == RECEIPT_PACKET_ID
    assert payload["receipt_packet_count"] == 1
    assert packets[0]["packet_ready"] is True
    assert packets[0]["packet_locked"] is True
    assert packets[0]["final_review_receipt"] is False
    assert packets[0]["final_triage_receipt"] is False
    assert packets[0]["feedback_review_started"] is False
    assert packets[0]["intake_triage_started"] is False
    assert packets[0]["vault_done"] is False
    assert len(packets[0]["packet_hash"]) == 64

def test_gp250_readiness_home_status_validation(gp241_250_db):
    payload = get_gp250_review_triage_lock_readiness_checkpoint(gp241_250_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP250"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["feedback_review_count"] == len(FEEDBACK_REVIEW_DRAFTS)
    assert readiness["issue_review_count"] == len(ISSUE_REVIEW_DRAFTS)
    assert readiness["triage_classification_count"] == len(TRIAGE_CLASSIFICATIONS)
    assert readiness["assignment_lock_count"] == len(ASSIGNMENT_LOCKS)
    assert readiness["escalation_lock_count"] == len(ESCALATION_LOCKS)
    assert readiness["fix_room_handoff_count"] == len(FIX_ROOM_HANDOFFS)
    assert readiness["reviewer_decision_lock_count"] == len(REVIEWER_DECISION_LOCKS)
    assert readiness["receipt_packet_count"] == 1
    assert readiness["review_triage_ready"] is True
    assert readiness["review_lock_active"] is True
    assert readiness["triage_lock_active"] is True
    assert readiness["assignment_lock_active"] is True
    assert readiness["escalation_lock_active"] is True
    assert readiness["fix_room_preview_only"] is True
    assert readiness["reviewer_decision_locked"] is True
    assert readiness["safe_to_continue_to_gp251"] is True
    assert readiness["section_ready"] is True
    assert readiness["vault_done"] is False
    assert readiness["clouds_should_continue"] is False
    assert validation["valid"] is True
    assert validation["failed_count"] == 0

    status = get_gp250_status(gp241_250_db)["gp250_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp251"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_BETA_FIX_AND_RESPONSE_LOCK_LAYER"
    assert status["next_section_range"] == "GP251-GP260"
    assert status["next_pack"] == "VAULT_GP251_260_BETA_FIX_AND_RESPONSE_LOCK_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp250"

    home = get_beta_feedback_review_triage_lock_layer_home(gp241_250_db)
    assert home["pack"]["id"] == "VAULT_GP241_250"
    assert home["truth"]["beta_feedback_review_triage_lock_layer_ready"] is True
    assert home["truth"]["safe_to_continue_to_gp251"] is True
    assert home["truth"]["feedback_review_started"] is False
    assert home["truth"]["issue_review_started"] is False
    assert home["truth"]["intake_triage_started"] is False
    assert home["truth"]["triage_classification_applied"] is False
    assert home["truth"]["assignment_created"] is False
    assert home["truth"]["assignment_sent"] is False
    assert home["truth"]["intake_escalation_created"] is False
    assert home["truth"]["intake_escalation_sent"] is False
    assert home["truth"]["fix_room_opened"] is False
    assert home["truth"]["fix_task_created"] is False
    assert home["truth"]["reviewer_decision_recorded"] is False
    assert home["truth"]["billing_flow_created"] is False
    assert home["truth"]["provider_api_called"] is False
    assert home["truth"]["provider_metadata_read"] is False
    assert home["truth"]["object_body_read"] is False
    assert home["truth"]["object_download_enabled"] is False
    assert home["truth"]["export_package_created"] is False
    assert home["truth"]["restore_job_created"] is False
    assert home["truth"]["execution_enabled"] is False
    assert home["truth"]["vault_done"] is False

def test_gp241_250_all_status_endpoints(gp241_250_db):
    funcs = [
        (241, get_gp241_status, "gp241_status"),
        (242, get_gp242_status, "gp242_status"),
        (243, get_gp243_status, "gp243_status"),
        (244, get_gp244_status, "gp244_status"),
        (245, get_gp245_status, "gp245_status"),
        (246, get_gp246_status, "gp246_status"),
        (247, get_gp247_status, "gp247_status"),
        (248, get_gp248_status, "gp248_status"),
        (249, get_gp249_status, "gp249_status"),
        (250, get_gp250_status, "gp250_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp241_250_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp251"] is True
        assert status["source_gp240_readiness_score"] == 100
        assert len(status["source_gp240_readiness_hash"]) == 64
        assert status["component_count"] == 10
        assert status["feedback_review_count"] == len(FEEDBACK_REVIEW_DRAFTS)
        assert status["issue_review_count"] == len(ISSUE_REVIEW_DRAFTS)
        assert status["triage_classification_count"] == len(TRIAGE_CLASSIFICATIONS)
        assert status["review_triage_ready"] is True
        assert status["review_lock_active"] is True
        assert status["triage_lock_active"] is True
        assert status["assignment_lock_active"] is True
        assert status["escalation_lock_active"] is True
        assert status["fix_room_preview_only"] is True
        assert status["reviewer_decision_locked"] is True
        assert status["feedback_review_started"] is False
        assert status["issue_review_started"] is False
        assert status["intake_triage_started"] is False
        assert status["triage_classification_applied"] is False
        assert status["assignment_created"] is False
        assert status["intake_escalation_created"] is False
        assert status["fix_room_opened"] is False
        assert status["fix_task_created"] is False
        assert status["reviewer_decision_recorded"] is False
        assert status["feedback_submitted"] is False
        assert status["issue_submitted"] is False
        assert status["support_message_sent"] is False
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

def test_gp241_250_html_is_dark_and_routes_registered(gp241_250_db):
    html = render_beta_feedback_review_triage_lock_layer_page()
    lowered = html.lower()
    assert "Vault GP241-GP250 Beta Feedback Review Triage Lock Layer" in html
    assert "GP241-GP250 built" in html
    assert "Safe to GP251" in html
    assert "No review started" in html
    assert "No triage" in html
    assert "No classification" in html
    assert "No assignment" in html
    assert "No escalation" in html
    assert "No fix room" in html
    assert "No decision" in html
    assert "Vault not done" in html
    assert "VAULT_GP251_260_BETA_FIX_AND_RESPONSE_LOCK_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/beta-feedback-review-triage-lock-layer",
        "/vault/beta-feedback-review-triage-lock-layer.json",
        "/vault/beta-feedback-review-triage-lock-shell.json",
        "/vault/feedback-review-draft-queue.json",
        "/vault/issue-review-draft-queue.json",
        "/vault/triage-classification-preview-matrix.json",
        "/vault/assignment-lock-contract.json",
        "/vault/escalation-lock-contract.json",
        "/vault/fix-room-handoff-preview.json",
        "/vault/reviewer-decision-lock-board.json",
        "/vault/review-triage-receipt-draft-packet.json",
        "/vault/review-triage-lock-readiness-checkpoint.json",
        "/vault/gp241-status.json",
        "/vault/gp242-status.json",
        "/vault/gp243-status.json",
        "/vault/gp244-status.json",
        "/vault/gp245-status.json",
        "/vault/gp246-status.json",
        "/vault/gp247-status.json",
        "/vault/gp248-status.json",
        "/vault/gp249-status.json",
        "/vault/gp250-status.json",
    ]
    for route in required_routes:
        assert route in text
