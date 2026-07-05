"""
Tests for VAULT GP131-GP140 — Tower-Gated Permission and Step-Up Layer
"""

from pathlib import Path
import pytest

from vault.tower_gated_permission_step_up_layer_service import (
    DENIAL_BLOCK_REASON_ID,
    DENIAL_REASONS,
    FALSE_FIELDS,
    HANDOFF_SHELL_ID,
    OWNER_AUTHORITY_BOUNDARY_ID,
    PERMISSION_BLOCKER_BOARD_ID,
    PERMISSION_DRAFT_REGISTRY_ID,
    PERMISSION_RECEIPT_LEDGER_ID,
    PERMISSION_SURFACES,
    READINESS_ID,
    STEP_UP_LOCK_ID,
    TOWER_EVIDENCE_MAP_ID,
    TOWER_REVIEW_QUEUE_ID,
    ensure_tower_gated_permission_step_up_layer_schema,
    get_gp131_tower_permission_handoff_shell,
    get_gp131_status,
    get_gp132_permission_request_draft_registry,
    get_gp132_status,
    get_gp133_step_up_challenge_lock_contract,
    get_gp133_status,
    get_gp134_tower_gate_review_queue,
    get_gp134_status,
    get_gp135_owner_authority_boundary_view,
    get_gp135_status,
    get_gp136_permission_receipt_draft_ledger,
    get_gp136_status,
    get_gp137_denial_and_block_reason_board,
    get_gp137_status,
    get_gp138_tower_handoff_evidence_map,
    get_gp138_status,
    get_gp139_tower_gated_permission_blocker_board,
    get_gp139_status,
    get_gp140_tower_gated_permission_readiness_checkpoint,
    get_gp140_status,
    get_tower_gated_permission_step_up_layer_home,
    initialize_tower_gated_permission_step_up_layer,
    render_tower_gated_permission_step_up_layer_page,
    validate_tower_gated_permission_step_up_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp131_140_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "gp131_140.sqlite")

def test_gp131_140_schema_and_initialize(gp131_140_db):
    schema = ensure_tower_gated_permission_step_up_layer_schema(gp131_140_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_tower_permission_components" in schema["tables"]
    assert "vault_permission_request_drafts" in schema["tables"]
    assert "vault_step_up_challenge_locks" in schema["tables"]
    assert "vault_tower_gate_review_queue" in schema["tables"]
    assert "vault_owner_authority_boundaries" in schema["tables"]
    assert "vault_permission_receipt_drafts" in schema["tables"]
    assert "vault_permission_denial_reasons" in schema["tables"]
    assert "vault_tower_handoff_evidence_links" in schema["tables"]
    assert "vault_tower_permission_blockers" in schema["tables"]
    assert "vault_tower_permission_readiness" in schema["tables"]

    result = initialize_tower_gated_permission_step_up_layer(gp131_140_db)
    assert result["initialized"] is True
    assert result["component_count"] == 10
    assert result["permission_draft_count"] == len(PERMISSION_SURFACES)
    assert result["step_up_challenge_count"] == len(PERMISSION_SURFACES)
    assert result["tower_review_item_count"] == len(PERMISSION_SURFACES)
    assert result["authority_boundary_count"] == len(PERMISSION_SURFACES)
    assert result["permission_receipt_draft_count"] == len(PERMISSION_SURFACES)
    assert result["denial_reason_count"] == len(DENIAL_REASONS)
    assert result["evidence_link_count"] == 8
    assert result["blocker_count"] == 10
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 10

def test_gp131_handoff_shell(gp131_140_db):
    payload = get_gp131_tower_permission_handoff_shell(gp131_140_db)
    shell = payload["handoff_shell"]

    assert payload["pack"]["id"] == "VAULT_GP131"
    assert shell["component_id"] == HANDOFF_SHELL_ID
    assert shell["gp_number"] == 131
    assert shell["section_range"] == "GP131-GP140"
    assert shell["source_gp130_readiness_score"] == 100
    assert len(shell["source_gp130_readiness_hash"]) == 64
    assert shell["component_ready"] is True
    assert shell["component_locked"] is True
    assert shell["tower_gated"] is True

    for field in FALSE_FIELDS:
        assert shell[field] is False

def test_gp132_permission_request_drafts(gp131_140_db):
    payload = get_gp132_permission_request_draft_registry(gp131_140_db)
    drafts = payload["drafts"]

    assert payload["pack"]["id"] == "VAULT_GP132"
    assert payload["permission_request_draft_registry"]["component_id"] == PERMISSION_DRAFT_REGISTRY_ID
    assert payload["permission_draft_count"] == len(PERMISSION_SURFACES)
    assert all(item["draft_ready"] is True for item in drafts)
    assert all(item["draft_locked"] is True for item in drafts)
    assert all(item["tower_gated"] is True for item in drafts)
    assert all(item["permission_request_submitted"] is False for item in drafts)
    assert all(item["permission_request_approved"] is False for item in drafts)
    assert all(item["permission_request_granted"] is False for item in drafts)

def test_gp133_step_up_challenge_locks(gp131_140_db):
    payload = get_gp133_step_up_challenge_lock_contract(gp131_140_db)
    challenges = payload["challenges"]

    assert payload["pack"]["id"] == "VAULT_GP133"
    assert payload["step_up_challenge_lock_contract"]["component_id"] == STEP_UP_LOCK_ID
    assert payload["step_up_challenge_count"] == len(PERMISSION_SURFACES)
    assert all(item["challenge_locked"] is True for item in challenges)
    assert all(item["tower_gated"] is True for item in challenges)
    assert all(item["step_up_challenge_started"] is False for item in challenges)
    assert all(item["step_up_challenge_passed"] is False for item in challenges)
    assert all(item["step_up_token_created"] is False for item in challenges)
    assert all(item["step_up_session_created"] is False for item in challenges)

def test_gp134_tower_gate_review_queue(gp131_140_db):
    payload = get_gp134_tower_gate_review_queue(gp131_140_db)
    queue = payload["queue"]

    assert payload["pack"]["id"] == "VAULT_GP134"
    assert payload["tower_gate_review_queue"]["component_id"] == TOWER_REVIEW_QUEUE_ID
    assert payload["tower_review_item_count"] == len(PERMISSION_SURFACES)
    assert all(item["review_locked"] is True for item in queue)
    assert all(item["tower_review_required"] is True for item in queue)
    assert all(item["owner_review_required"] is True for item in queue)
    assert all(item["tower_unlock_granted"] is False for item in queue)
    assert all(item["tower_gate_passed"] is False for item in queue)

def test_gp135_owner_authority_boundaries(gp131_140_db):
    payload = get_gp135_owner_authority_boundary_view(gp131_140_db)
    boundaries = payload["boundaries"]

    assert payload["pack"]["id"] == "VAULT_GP135"
    assert payload["owner_authority_boundary_view"]["component_id"] == OWNER_AUTHORITY_BOUNDARY_ID
    assert payload["authority_boundary_count"] == len(PERMISSION_SURFACES)
    assert all(item["boundary_locked"] is True for item in boundaries)
    assert all(item["owner_visible"] is True for item in boundaries)
    assert all(item["tower_gated"] is True for item in boundaries)
    assert all(item["owner_decision_recorded"] is False for item in boundaries)
    assert all(item["owner_execute_action_approved"] is False for item in boundaries)

def test_gp136_permission_receipt_drafts(gp131_140_db):
    payload = get_gp136_permission_receipt_draft_ledger(gp131_140_db)
    receipts = payload["receipt_drafts"]

    assert payload["pack"]["id"] == "VAULT_GP136"
    assert payload["permission_receipt_draft_ledger"]["component_id"] == PERMISSION_RECEIPT_LEDGER_ID
    assert payload["permission_receipt_draft_count"] == len(PERMISSION_SURFACES)
    assert all(item["receipt_draft_locked"] is True for item in receipts)
    assert all(item["final_receipt_created"] is False for item in receipts)
    assert all(item["permission_receipt_finalized"] is False for item in receipts)
    assert all(item["permission_receipt_persisted"] is False for item in receipts)

def test_gp137_denial_reasons(gp131_140_db):
    payload = get_gp137_denial_and_block_reason_board(gp131_140_db)
    reasons = payload["denial_reasons"]

    assert payload["pack"]["id"] == "VAULT_GP137"
    assert payload["denial_and_block_reason_board"]["component_id"] == DENIAL_BLOCK_REASON_ID
    assert payload["denial_reason_count"] == len(DENIAL_REASONS)
    assert all(item["denial_active"] is True for item in reasons)
    assert all(item["permission_request_denied_final"] is False for item in reasons)

def test_gp138_evidence_map(gp131_140_db):
    payload = get_gp138_tower_handoff_evidence_map(gp131_140_db)
    evidence = payload["evidence_links"]

    assert payload["pack"]["id"] == "VAULT_GP138"
    assert payload["tower_handoff_evidence_map"]["component_id"] == TOWER_EVIDENCE_MAP_ID
    assert payload["evidence_link_count"] == 8
    assert all(item["evidence_locked"] is True for item in evidence)
    assert all(item["tower_gated"] is True for item in evidence)
    assert all(len(item["evidence_hash"]) == 64 for item in evidence)

def test_gp139_blocker_board(gp131_140_db):
    payload = get_gp139_tower_gated_permission_blocker_board(gp131_140_db)
    blockers = payload["blockers"]

    assert payload["pack"]["id"] == "VAULT_GP139"
    assert payload["tower_gated_permission_blocker_board"]["component_id"] == PERMISSION_BLOCKER_BOARD_ID
    assert payload["blocker_count"] == 10
    assert all(item["blocker_active"] is True for item in blockers)
    assert all(item["blocks_permission_submit"] is True for item in blockers)
    assert all(item["blocks_step_up_pass"] is True for item in blockers)
    assert all(item["blocks_tower_unlock"] is True for item in blockers)
    assert all(item["blocks_owner_execution"] is True for item in blockers)
    assert all(item["blocks_provider_api"] is True for item in blockers)
    assert all(item["blocks_object_body"] is True for item in blockers)
    assert all(item["blocks_download"] is True for item in blockers)
    assert all(item["blocks_export"] is True for item in blockers)
    assert all(item["blocks_restore"] is True for item in blockers)
    assert all(item["blocks_direct_upload"] is True for item in blockers)
    assert all(item["blocks_execution"] is True for item in blockers)
    assert all(item["blocks_vault_done"] is True for item in blockers)
    assert all(item["resolved"] is False for item in blockers)

def test_gp140_readiness_status_home_and_validation(gp131_140_db):
    payload = get_gp140_tower_gated_permission_readiness_checkpoint(gp131_140_db)
    checkpoint = payload["readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP140"
    assert checkpoint["component_id"] == READINESS_ID
    assert readiness["readiness_id"] == READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 10
    assert readiness["permission_draft_count"] == len(PERMISSION_SURFACES)
    assert readiness["step_up_challenge_count"] == len(PERMISSION_SURFACES)
    assert readiness["tower_review_item_count"] == len(PERMISSION_SURFACES)
    assert readiness["authority_boundary_count"] == len(PERMISSION_SURFACES)
    assert readiness["permission_receipt_draft_count"] == len(PERMISSION_SURFACES)
    assert readiness["denial_reason_count"] == len(DENIAL_REASONS)
    assert readiness["evidence_link_count"] == 8
    assert readiness["blocker_count"] == 10
    assert readiness["safe_to_continue_to_gp141"] is True
    assert readiness["section_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp141"] is True
    assert validation["vault_done"] is False

    status = get_gp140_status(gp131_140_db)["gp140_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp141"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_PROVIDER_READINESS_SIMULATION_AND_DRY_RUN_LAYER"
    assert status["next_section_range"] == "GP141-GP150"
    assert status["next_pack"] == "VAULT_GP141_150_PROVIDER_READINESS_SIMULATION_AND_DRY_RUN_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp140"

    home = get_tower_gated_permission_step_up_layer_home(gp131_140_db)
    assert home["pack"]["id"] == "VAULT_GP131_140"
    assert home["truth"]["tower_gated_permission_step_up_layer_ready"] is True
    assert home["truth"]["safe_to_continue_to_gp141"] is True
    assert home["truth"]["permission_request_submitted"] is False
    assert home["truth"]["permission_request_approved"] is False
    assert home["truth"]["step_up_challenge_passed"] is False
    assert home["truth"]["step_up_token_created"] is False
    assert home["truth"]["tower_unlock_granted"] is False
    assert home["truth"]["tower_clearance_granted"] is False
    assert home["truth"]["owner_approval_recorded"] is False
    assert home["truth"]["provider_api_called"] is False
    assert home["truth"]["provider_objects_listed"] is False
    assert home["truth"]["provider_metadata_read"] is False
    assert home["truth"]["object_body_read"] is False
    assert home["truth"]["object_body_view_enabled"] is False
    assert home["truth"]["object_body_download_enabled"] is False
    assert home["truth"]["object_body_plaintext_visible"] is False
    assert home["truth"]["export_package_created"] is False
    assert home["truth"]["restore_job_created"] is False
    assert home["truth"]["direct_upload_enabled"] is False
    assert home["truth"]["execution_enabled"] is False
    assert home["truth"]["vault_done"] is False
    assert home["truth"]["clouds_should_continue"] is False

def test_gp131_140_all_status_endpoints(gp131_140_db):
    funcs = [
        (131, get_gp131_status, "gp131_status"),
        (132, get_gp132_status, "gp132_status"),
        (133, get_gp133_status, "gp133_status"),
        (134, get_gp134_status, "gp134_status"),
        (135, get_gp135_status, "gp135_status"),
        (136, get_gp136_status, "gp136_status"),
        (137, get_gp137_status, "gp137_status"),
        (138, get_gp138_status, "gp138_status"),
        (139, get_gp139_status, "gp139_status"),
        (140, get_gp140_status, "gp140_status"),
    ]

    for gp_number, fn, key in funcs:
        status = fn(gp131_140_db)[key]
        assert status["pack_id"] == f"VAULT_GP{gp_number:03d}"
        assert status["ready"] is True
        assert status["validation_passed"] is True
        assert status["safe_to_continue_to_gp141"] is True
        assert status["source_gp130_readiness_score"] == 100
        assert len(status["source_gp130_readiness_hash"]) == 64
        assert status["permission_draft_count"] == len(PERMISSION_SURFACES)
        assert status["step_up_challenge_count"] == len(PERMISSION_SURFACES)
        assert status["blocker_count"] == 10
        assert status["permission_request_submitted"] is False
        assert status["permission_request_approved"] is False
        assert status["permission_request_granted"] is False
        assert status["step_up_challenge_started"] is False
        assert status["step_up_challenge_passed"] is False
        assert status["step_up_token_created"] is False
        assert status["step_up_session_created"] is False
        assert status["tower_gate_opened"] is False
        assert status["tower_gate_passed"] is False
        assert status["tower_unlock_requested"] is False
        assert status["tower_unlock_granted"] is False
        assert status["tower_clearance_granted"] is False
        assert status["owner_decision_recorded"] is False
        assert status["owner_approval_recorded"] is False
        assert status["owner_execute_action_approved"] is False
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
        assert status["export_enabled"] is False
        assert status["restore_request_created"] is False
        assert status["restore_job_created"] is False
        assert status["provider_restore_api_called"] is False
        assert status["direct_upload_enabled"] is False
        assert status["execution_enabled"] is False
        assert status["vault_done"] is False

def test_gp131_140_html_is_dark_and_routes_registered(gp131_140_db):
    html = render_tower_gated_permission_step_up_layer_page()
    lowered = html.lower()
    assert "Vault GP131-GP140 Tower-Gated Permission Step-Up Layer" in html
    assert "GP131-GP140 built" in html
    assert "Tower handoff ready" in html
    assert "Safe to GP141" in html
    assert "No permission submit" in html
    assert "No step-up pass" in html
    assert "No Tower unlock" in html
    assert "No provider API" in html
    assert "No object body" in html
    assert "No execution" in html
    assert "VAULT_GP141_150_PROVIDER_READINESS_SIMULATION_AND_DRY_RUN_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/tower-gated-permission-step-up-layer",
        "/vault/tower-gated-permission-step-up-layer.json",
        "/vault/tower-permission-handoff-shell.json",
        "/vault/permission-request-draft-registry.json",
        "/vault/step-up-challenge-lock-contract.json",
        "/vault/tower-gate-review-queue.json",
        "/vault/owner-authority-boundary-view.json",
        "/vault/permission-receipt-draft-ledger.json",
        "/vault/permission-denial-block-reason-board.json",
        "/vault/tower-handoff-evidence-map.json",
        "/vault/tower-gated-permission-blocker-board.json",
        "/vault/tower-gated-permission-readiness-checkpoint.json",
        "/vault/gp131-status.json",
        "/vault/gp132-status.json",
        "/vault/gp133-status.json",
        "/vault/gp134-status.json",
        "/vault/gp135-status.json",
        "/vault/gp136-status.json",
        "/vault/gp137-status.json",
        "/vault/gp138-status.json",
        "/vault/gp139-status.json",
        "/vault/gp140-status.json",
    ]
    for route in required_routes:
        assert route in text
