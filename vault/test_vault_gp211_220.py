"""
Tests for VAULT GP211-GP220 — Beta Access and Invite Lock Layer
"""

from pathlib import Path
import pytest

from vault.beta_access_invite_lock_layer_service import (
    ACCESS_GRANT_LOCKS,
    ACCESS_GRANT_LOCK_ID,
    BILLING_HANDOFF_ID,
    BILLING_HANDOFF_PREVIEWS,
    FALSE_FIELDS,
    INVITE_DRAFTS,
    INVITE_DRAFT_REGISTRY_ID,
    INVITE_SEND_LOCKS,
    INVITE_SEND_LOCK_ID,
    READINESS_ID,
    RISK_BLOCKER_ID,
    RISK_BLOCKERS,
    ROLE_PERMISSION_MATRIX_ID,
    ROLE_PERMISSION_PREVIEWS,
    SHELL_ID,
    TESTER_CANDIDATES,
    TESTER_INTAKE_LOCK_ID,
    TOWER_GATE_HANDOFF_ID,
    TOWER_HANDOFF_PREVIEWS,
    ensure_beta_access_invite_lock_layer_schema,
    get_gp211_beta_access_invite_lock_shell,
    get_gp211_status,
    get_gp212_beta_invite_draft_registry,
    get_gp212_status,
    get_gp213_tester_candidate_intake_lock_board,
    get_gp213_status,
    get_gp214_invite_send_lock_contract,
    get_gp214_status,
    get_gp215_access_grant_lock_contract,
    get_gp215_status,
    get_gp216_beta_role_permission_preview_matrix,
    get_gp216_status,
    get_gp217_tower_beta_gate_handoff_preview,
    get_gp217_status,
    get_gp218_billing_subscription_lock_handoff_preview,
    get_gp218_status,
    get_gp219_beta_access_risk_blocker_board,
    get_gp219_status,
    get_gp220_beta_access_invite_lock_readiness_checkpoint,
    get_gp220_status,
    get_beta_access_invite_lock_layer_home,
    initialize_beta_access_invite_lock_layer,
    render_beta_access_invite_lock_layer_page,
    validate_beta_access_invite_lock_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp211_220_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp211_220.sqlite")

def test_gp211_220_schema_and_initialize(gp211_220_db):
    schema = ensure_beta_access_invite_lock_layer_schema(gp211_220_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_beta_access_invite_components" in schema["tables"]
    assert "vault_beta_invite_draft_registry" in schema["tables"]
    assert "vault_beta_access_invite_readiness" in schema["tables"]

    result = initialize_beta_access_invite_lock_layer(gp211_220_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["invite_draft_count"] == len(INVITE_DRAFTS)
    assert result["tester_candidate_count"] == len(TESTER_CANDIDATES)
    assert result["invite_send_lock_count"] == len(INVITE_SEND_LOCKS)
    assert result["access_grant_lock_count"] == len(ACCESS_GRANT_LOCKS)
    assert result["role_permission_preview_count"] == len(ROLE_PERMISSION_PREVIEWS)
    assert result["tower_handoff_preview_count"] == len(TOWER_HANDOFF_PREVIEWS)
    assert result["billing_handoff_preview_count"] == len(BILLING_HANDOFF_PREVIEWS)
    assert result["risk_blocker_count"] == len(RISK_BLOCKERS)
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp211_shell(gp211_220_db):
    payload = get_gp211_beta_access_invite_lock_shell(gp211_220_db)
    shell = payload["shell"]

    assert payload["pack"]["id"] == "VAULT_GP211"
    assert shell["component_id"] == SHELL_ID
    assert shell["gp_number"] == 211
    assert shell["source_gp210_readiness_score"] == 100
    assert len(shell["source_gp210_readiness_hash"]) == 64
    assert shell["component_ready"] is True
    assert shell["component_locked"] is True
    assert shell["beta_access_layer_ready"] is True
    assert shell["invite_lock_active"] is True
    assert shell["access_grant_lock_active"] is True
    assert shell["tower_gate_preview_only"] is True
    assert shell["billing_preview_only"] is True
    assert shell["vault_not_done"] is True

    for field in FALSE_FIELDS:
        assert shell[field] is False

def test_gp212_invite_drafts(gp211_220_db):
    payload = get_gp212_beta_invite_draft_registry(gp211_220_db)
    rows = payload["invites"]

    assert payload["pack"]["id"] == "VAULT_GP212"
    assert payload["invite_draft_registry"]["component_id"] == INVITE_DRAFT_REGISTRY_ID
    assert payload["invite_draft_count"] == len(INVITE_DRAFTS)
    assert all(item["draft_ready"] is True for item in rows)
    assert all(item["draft_locked"] is True for item in rows)
    assert all(item["send_locked"] is True for item in rows)
    assert all(item["beta_invite_created"] is False for item in rows)
    assert all(item["beta_invite_sent"] is False for item in rows)

def test_gp213_tester_candidates(gp211_220_db):
    payload = get_gp213_tester_candidate_intake_lock_board(gp211_220_db)
    rows = payload["candidates"]

    assert payload["pack"]["id"] == "VAULT_GP213"
    assert payload["tester_candidate_intake_lock_board"]["component_id"] == TESTER_INTAKE_LOCK_ID
    assert payload["tester_candidate_count"] == len(TESTER_CANDIDATES)
    assert all(item["intake_locked"] is True for item in rows)
    assert all(item["approval_locked"] is True for item in rows)
    assert all(item["add_locked"] is True for item in rows)
    assert all(item["tester_candidate_submitted"] is False for item in rows)
    assert all(item["tester_candidate_approved"] is False for item in rows)
    assert all(item["beta_tester_added"] is False for item in rows)

def test_gp214_invite_send_locks(gp211_220_db):
    payload = get_gp214_invite_send_lock_contract(gp211_220_db)
    rows = payload["locks"]

    assert payload["pack"]["id"] == "VAULT_GP214"
    assert payload["invite_send_lock_contract"]["component_id"] == INVITE_SEND_LOCK_ID
    assert payload["invite_send_lock_count"] == len(INVITE_SEND_LOCKS)
    assert all(item["invite_send_locked"] is True for item in rows)
    assert all(item["invite_delivery_locked"] is True for item in rows)
    assert all(item["beta_invite_sent"] is False for item in rows)
    assert all(item["beta_invite_delivered"] is False for item in rows)

def test_gp215_access_grant_locks(gp211_220_db):
    payload = get_gp215_access_grant_lock_contract(gp211_220_db)
    rows = payload["locks"]

    assert payload["pack"]["id"] == "VAULT_GP215"
    assert payload["access_grant_lock_contract"]["component_id"] == ACCESS_GRANT_LOCK_ID
    assert payload["access_grant_lock_count"] == len(ACCESS_GRANT_LOCKS)
    assert all(item["access_grant_locked"] is True for item in rows)
    assert all(item["token_session_locked"] is True for item in rows)
    assert all(item["beta_tester_access_granted"] is False for item in rows)
    assert all(item["beta_access_token_created"] is False for item in rows)
    assert all(item["beta_access_session_created"] is False for item in rows)

def test_gp216_role_permission_preview(gp211_220_db):
    payload = get_gp216_beta_role_permission_preview_matrix(gp211_220_db)
    rows = payload["roles"]

    assert payload["pack"]["id"] == "VAULT_GP216"
    assert payload["role_permission_matrix"]["component_id"] == ROLE_PERMISSION_MATRIX_ID
    assert payload["role_permission_preview_count"] == len(ROLE_PERMISSION_PREVIEWS)
    assert all(item["preview_only"] is True for item in rows)
    assert all(item["role_assignment_locked"] is True for item in rows)
    assert all(item["permission_grant_locked"] is True for item in rows)
    assert all(item["beta_role_assigned"] is False for item in rows)
    assert all(item["beta_permission_granted"] is False for item in rows)

def test_gp217_tower_handoff(gp211_220_db):
    payload = get_gp217_tower_beta_gate_handoff_preview(gp211_220_db)
    rows = payload["handoffs"]

    assert payload["pack"]["id"] == "VAULT_GP217"
    assert payload["tower_handoff_preview"]["component_id"] == TOWER_GATE_HANDOFF_ID
    assert payload["tower_handoff_preview_count"] == len(TOWER_HANDOFF_PREVIEWS)
    assert all(item["preview_only"] is True for item in rows)
    assert all(item["tower_gate_locked"] is True for item in rows)
    assert all(item["tower_unlock_locked"] is True for item in rows)
    assert all(item["tower_gate_opened"] is False for item in rows)
    assert all(item["tower_gate_passed"] is False for item in rows)
    assert all(item["tower_unlock_granted"] is False for item in rows)

def test_gp218_billing_handoff(gp211_220_db):
    payload = get_gp218_billing_subscription_lock_handoff_preview(gp211_220_db)
    rows = payload["handoffs"]

    assert payload["pack"]["id"] == "VAULT_GP218"
    assert payload["billing_handoff_preview"]["component_id"] == BILLING_HANDOFF_ID
    assert payload["billing_handoff_preview_count"] == len(BILLING_HANDOFF_PREVIEWS)
    assert all(item["preview_only"] is True for item in rows)
    assert all(item["billing_locked"] is True for item in rows)
    assert all(item["subscription_locked"] is True for item in rows)
    assert all(item["billing_flow_created"] is False for item in rows)
    assert all(item["subscription_flow_created"] is False for item in rows)
    assert all(item["payment_processor_called"] is False for item in rows)

def test_gp219_risk_blockers(gp211_220_db):
    payload = get_gp219_beta_access_risk_blocker_board(gp211_220_db)
    rows = payload["blockers"]

    assert payload["pack"]["id"] == "VAULT_GP219"
    assert payload["risk_blocker_board"]["component_id"] == RISK_BLOCKER_ID
    assert payload["risk_blocker_count"] == len(RISK_BLOCKERS)
    assert all(item["blocker_active"] is True for item in rows)
    assert all(item["blocks_beta_launch"] is True for item in rows)
    assert all(item["blocks_invite_send"] is True for item in rows)
    assert all(item["blocks_tester_add"] is True for item in rows)
    assert all(item["blocks_access_grant"] is True for item in rows)
    assert all(item["blocks_token_session"] is True for item in rows)
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

def test_gp220_readiness_home_status_validation(gp211_220_db):
    payload = get_gp220_beta_access_invite_lock_readiness_checkpoint(gp211_220_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP220"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["invite_draft_count"] == len(INVITE_DRAFTS)
    assert readiness["tester_candidate_count"] == len(TESTER_CANDIDATES)
    assert readiness["invite_send_lock_count"] == len(INVITE_SEND_LOCKS)
    assert readiness["access_grant_lock_count"] == len(ACCESS_GRANT_LOCKS)
    assert readiness["role_permission_preview_count"] == len(ROLE_PERMISSION_PREVIEWS)
    assert readiness["tower_handoff_preview_count"] == len(TOWER_HANDOFF_PREVIEWS)
    assert readiness["billing_handoff_preview_count"] == len(BILLING_HANDOFF_PREVIEWS)
    assert readiness["risk_blocker_count"] == len(RISK_BLOCKERS)
    assert readiness["beta_access_layer_ready"] is True
    assert readiness["invite_lock_active"] is True
    assert readiness["access_grant_lock_active"] is True
    assert readiness["safe_to_continue_to_gp221"] is True
    assert readiness["section_ready"] is True
    assert readiness["vault_done"] is False
    assert readiness["clouds_should_continue"] is False
    assert validation["valid"] is True
    assert validation["failed_count"] == 0

    status = get_gp220_status(gp211_220_db)["gp220_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp221"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_BETA_ONBOARDING_LOCKED_EXPERIENCE_LAYER"
    assert status["next_section_range"] == "GP221-GP230"
    assert status["next_pack"] == "VAULT_GP221_230_BETA_ONBOARDING_LOCKED_EXPERIENCE_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp220"

    home = get_beta_access_invite_lock_layer_home(gp211_220_db)
    assert home["pack"]["id"] == "VAULT_GP211_220"
    assert home["truth"]["beta_access_invite_lock_layer_ready"] is True
    assert home["truth"]["safe_to_continue_to_gp221"] is True
    assert home["truth"]["beta_invite_created"] is False
    assert home["truth"]["beta_invite_sent"] is False
    assert home["truth"]["tester_candidate_submitted"] is False
    assert home["truth"]["beta_tester_added"] is False
    assert home["truth"]["beta_tester_access_granted"] is False
    assert home["truth"]["beta_access_token_created"] is False
    assert home["truth"]["beta_access_session_created"] is False
    assert home["truth"]["billing_flow_created"] is False
    assert home["truth"]["subscription_flow_created"] is False
    assert home["truth"]["payment_processor_called"] is False
    assert home["truth"]["tower_gate_opened"] is False
    assert home["truth"]["tower_unlock_granted"] is False
    assert home["truth"]["provider_api_called"] is False
    assert home["truth"]["provider_metadata_read"] is False
    assert home["truth"]["object_body_read"] is False
    assert home["truth"]["object_download_enabled"] is False
    assert home["truth"]["export_package_created"] is False
    assert home["truth"]["restore_job_created"] is False
    assert home["truth"]["execution_enabled"] is False
    assert home["truth"]["vault_done"] is False

def test_gp211_220_all_status_endpoints(gp211_220_db):
    funcs = [
        (211, get_gp211_status, "gp211_status"),
        (212, get_gp212_status, "gp212_status"),
        (213, get_gp213_status, "gp213_status"),
        (214, get_gp214_status, "gp214_status"),
        (215, get_gp215_status, "gp215_status"),
        (216, get_gp216_status, "gp216_status"),
        (217, get_gp217_status, "gp217_status"),
        (218, get_gp218_status, "gp218_status"),
        (219, get_gp219_status, "gp219_status"),
        (220, get_gp220_status, "gp220_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp211_220_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp221"] is True
        assert status["source_gp210_readiness_score"] == 100
        assert len(status["source_gp210_readiness_hash"]) == 64
        assert status["component_count"] == 10
        assert status["invite_draft_count"] == len(INVITE_DRAFTS)
        assert status["risk_blocker_count"] == len(RISK_BLOCKERS)
        assert status["beta_access_layer_ready"] is True
        assert status["invite_lock_active"] is True
        assert status["access_grant_lock_active"] is True
        assert status["beta_launch_approved"] is False
        assert status["beta_invite_created"] is False
        assert status["beta_invite_sent"] is False
        assert status["beta_tester_added"] is False
        assert status["beta_tester_access_granted"] is False
        assert status["beta_access_token_created"] is False
        assert status["beta_access_session_created"] is False
        assert status["billing_flow_created"] is False
        assert status["subscription_flow_created"] is False
        assert status["payment_processor_called"] is False
        assert status["provider_unlock_requested"] is False
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

def test_gp211_220_html_is_dark_and_routes_registered(gp211_220_db):
    html = render_beta_access_invite_lock_layer_page()
    lowered = html.lower()
    assert "Vault GP211-GP220 Beta Access Invite Lock Layer" in html
    assert "GP211-GP220 built" in html
    assert "Safe to GP221" in html
    assert "No invite sent" in html
    assert "No tester added" in html
    assert "No access granted" in html
    assert "No token/session" in html
    assert "No Tower gate" in html
    assert "No billing flow" in html
    assert "No execution" in html
    assert "Vault not done" in html
    assert "VAULT_GP221_230_BETA_ONBOARDING_LOCKED_EXPERIENCE_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/beta-access-invite-lock-layer",
        "/vault/beta-access-invite-lock-layer.json",
        "/vault/beta-access-invite-lock-shell.json",
        "/vault/beta-invite-draft-registry.json",
        "/vault/tester-candidate-intake-lock-board.json",
        "/vault/invite-send-lock-contract.json",
        "/vault/access-grant-lock-contract.json",
        "/vault/beta-role-permission-preview-matrix.json",
        "/vault/tower-beta-gate-handoff-preview.json",
        "/vault/billing-subscription-lock-handoff-preview.json",
        "/vault/beta-access-risk-blocker-board.json",
        "/vault/beta-access-invite-lock-readiness-checkpoint.json",
        "/vault/gp211-status.json",
        "/vault/gp212-status.json",
        "/vault/gp213-status.json",
        "/vault/gp214-status.json",
        "/vault/gp215-status.json",
        "/vault/gp216-status.json",
        "/vault/gp217-status.json",
        "/vault/gp218-status.json",
        "/vault/gp219-status.json",
        "/vault/gp220-status.json",
    ]
    for route in required_routes:
        assert route in text
