"""
Tests for VAULT GP096-GP100 — Post-Closeout Handoff Governance Closeout Layer
"""

from pathlib import Path
import pytest

from vault.real_provider_post_closeout_handoff_owner_review_closeout_layer_service import (
    CLOSEOUT_RECEIPTS,
    FALSE_FIELDS,
    GP096_CLOSEOUT_LOCK_CONTRACT_ID,
    GP097_CLOSEOUT_RECEIPT_LEDGER_ID,
    GP098_OWNER_SUMMARY_ID,
    GP099_SECTION_CLOSEOUT_PACKET_ID,
    GP100_GOVERNANCE_READINESS_ID,
    ensure_post_closeout_handoff_governance_closeout_layer_schema,
    get_gp096_closeout_lock_contract,
    get_gp096_status,
    get_gp097_closeout_receipt_ledger,
    get_gp097_status,
    get_gp098_owner_summary,
    get_gp098_status,
    get_gp099_section_closeout_packet,
    get_gp099_status,
    get_gp100_governance_readiness_checkpoint,
    get_gp100_status,
    get_post_closeout_handoff_governance_closeout_layer_home,
    initialize_post_closeout_handoff_governance_closeout_layer,
    render_post_closeout_handoff_governance_closeout_layer_page,
    validate_post_closeout_handoff_governance_closeout_layer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp096_100_db(tmp_path, monkeypatch):
    envs = {
        "VAULT_STORAGE_PROVIDER_DECISION_DB": "decision.sqlite",
        "VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB": "selection_registry.sqlite",
        "VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB": "capability_contract.sqlite",
        "VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB": "risk_criteria_validation.sqlite",
        "VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB": "selection_review_receipt.sqlite",
        "VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB": "prep_readiness.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB": "config_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB": "credential_boundary.sqlite",
        "VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB": "secret_reference_ledger.sqlite",
        "VAULT_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT_DB": "endpoint_namespace_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT_DB": "encryption_policy_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT_DB": "connection_test_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT_DB": "write_path_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT_DB": "read_path_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT_DB": "object_body_view_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT_DB": "configuration_readiness_checkpoint.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT_DB": "object_catalog_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_METADATA_RECEIPT_CONTRACT_DB": "redacted_metadata_receipt_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_CONTRACT_DB": "receipt_lineage_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_DB": "redacted_access_view_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_PACKET_LOCK_CONTRACT_DB": "owner_review_packet_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_QUEUE_LOCK_CONTRACT_DB": "owner_review_queue_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_LOCK_CONTRACT_DB": "owner_review_decision_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_DB": "owner_review_decision_receipt_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_CLOSEOUT_LOCK_CONTRACT_DB": "owner_review_closeout_lock_contract.sqlite",
        "VAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_DB": "provider_receipt_redacted_access_readiness.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT_DB": "restore_request_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_ELIGIBILITY_LOCK_CONTRACT_DB": "restore_eligibility_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_AUTHORITY_LOCK_CONTRACT_DB": "restore_authority_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_SCOPE_LOCK_CONTRACT_DB": "restore_scope_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_TARGET_LOCK_CONTRACT_DB": "restore_target_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_OBJECT_LOCK_CONTRACT_DB": "restore_object_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_JOB_LOCK_CONTRACT_DB": "restore_job_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_API_LOCK_CONTRACT_DB": "restore_api_lock_contract.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_EXPORT_LOCK_CONTRACT_DB": "restore_export_lock_contract.sqlite",
        "VAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_DB": "restore_export_governance_readiness.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_DB": "post_closeout_handoff_lock_contract.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_DB": "post_closeout_handoff_receipt_ledger.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_DB": "post_closeout_handoff_owner_review_queue.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_DB": "post_closeout_handoff_owner_review_decision_lock_contract.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_DB": "post_closeout_handoff_owner_review_decision_receipt_lock_contract.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_GOVERNANCE_CLOSEOUT_LAYER_DB": "post_closeout_handoff_governance_closeout_layer.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "post_closeout_handoff_governance_closeout_layer.sqlite")

def test_gp096_100_schema_and_initialize(gp096_100_db):
    schema = ensure_post_closeout_handoff_governance_closeout_layer_schema(gp096_100_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_post_closeout_handoff_governance_components" in schema["tables"]
    assert "vault_post_closeout_handoff_governance_closeout_receipts" in schema["tables"]
    assert "vault_post_closeout_handoff_governance_readiness" in schema["tables"]
    assert "vault_post_closeout_handoff_governance_closeout_events" in schema["tables"]

    result = initialize_post_closeout_handoff_governance_closeout_layer(gp096_100_db)
    assert result["initialized"] is True
    assert result["component_count"] == 5
    assert result["receipt_count"] == len(CLOSEOUT_RECEIPTS)
    assert result["readiness_count"] == 1
    assert result["event_count"] >= 6

def test_gp096_closeout_lock_contract(gp096_100_db):
    payload = get_gp096_closeout_lock_contract(gp096_100_db)
    contract = payload["closeout_lock_contract"]

    assert payload["pack"]["id"] == "VAULT_GP096"
    assert contract["component_id"] == GP096_CLOSEOUT_LOCK_CONTRACT_ID
    assert contract["gp_number"] == 96
    assert contract["pack_id"] == "VAULT_GP096"
    assert contract["section_range"] == "GP091-GP100"
    assert contract["source_gp095_contract_id"] == "VPPCHORDRLC-GP095-001"
    assert contract["source_gp095_validation_passed"] is True
    assert contract["source_gp090_readiness_score"] == 100
    assert len(contract["source_gp090_readiness_hash"]) == 64
    assert len(contract["source_ledger_hash"]) == 64
    assert contract["component_ready"] is True
    assert contract["component_locked"] is True
    assert contract["safe_to_continue"] is True

    for field in FALSE_FIELDS:
        assert contract[field] is False

    status = get_gp096_status(gp096_100_db)["gp096_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["safe_to_continue_to_gp101"] is True
    assert status["vault_done"] is False

def test_gp097_receipt_ledger(gp096_100_db):
    payload = get_gp097_closeout_receipt_ledger(gp096_100_db)
    ledger = payload["receipt_ledger"]
    receipts = payload["receipts"]

    assert payload["pack"]["id"] == "VAULT_GP097"
    assert ledger["component_id"] == GP097_CLOSEOUT_RECEIPT_LEDGER_ID
    assert ledger["gp_number"] == 97
    assert ledger["receipt_count"] == len(CLOSEOUT_RECEIPTS)
    assert len(ledger["receipt_ledger_hash"]) == 64
    assert len(receipts) == len(CLOSEOUT_RECEIPTS)
    assert {item["receipt_code"] for item in receipts} == {item[0] for item in CLOSEOUT_RECEIPTS}
    assert all(len(item["receipt_hash"]) == 64 for item in receipts)
    assert all(item["receipt_locked"] is True for item in receipts)

    for receipt in receipts:
        for field in FALSE_FIELDS:
            assert receipt[field] is False

    status = get_gp097_status(gp096_100_db)["gp097_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["vault_done"] is False

def test_gp098_owner_summary(gp096_100_db):
    payload = get_gp098_owner_summary(gp096_100_db)
    summary = payload["owner_summary"]

    assert payload["pack"]["id"] == "VAULT_GP098"
    assert summary["component_id"] == GP098_OWNER_SUMMARY_ID
    assert summary["gp_number"] == 98
    assert summary["summary_status"] == "OWNER_SUMMARY_READY_LOCKED"
    assert summary["section_closed_by_gp100"] is True
    assert summary["safe_to_continue_to_gp101"] is True
    assert summary["vault_done"] is False
    assert summary["clouds_should_continue"] is False
    assert "summary_points" in summary["data"]

    for field in FALSE_FIELDS:
        assert summary[field] is False

    status = get_gp098_status(gp096_100_db)["gp098_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True

def test_gp099_section_closeout_packet(gp096_100_db):
    payload = get_gp099_section_closeout_packet(gp096_100_db)
    packet = payload["section_closeout_packet"]

    assert payload["pack"]["id"] == "VAULT_GP099"
    assert packet["component_id"] == GP099_SECTION_CLOSEOUT_PACKET_ID
    assert packet["gp_number"] == 99
    assert len(packet["packet_hash"]) == 64
    assert packet["section_closed"] is True
    assert packet["safe_to_continue_to_gp101"] is True
    assert packet["packet_payload"]["section_range"] == "GP091-GP100"
    assert packet["packet_payload"]["next_section_range"] == "GP101-GP110"
    assert packet["vault_done"] is False
    assert packet["clouds_should_continue"] is False

    for field in FALSE_FIELDS:
        assert packet[field] is False

    status = get_gp099_status(gp096_100_db)["gp099_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True

def test_gp100_readiness_checkpoint(gp096_100_db):
    payload = get_gp100_governance_readiness_checkpoint(gp096_100_db)
    checkpoint = payload["governance_readiness_checkpoint"]
    readiness = checkpoint["readiness"]
    validation = checkpoint["validation"]

    assert payload["pack"]["id"] == "VAULT_GP100"
    assert checkpoint["component_id"] == GP100_GOVERNANCE_READINESS_ID
    assert checkpoint["gp_number"] == 100
    assert readiness["readiness_id"] == GP100_GOVERNANCE_READINESS_ID
    assert readiness["readiness_score"] == 100
    assert len(readiness["readiness_hash"]) == 64
    assert readiness["component_count"] == 5
    assert readiness["receipt_count"] == len(CLOSEOUT_RECEIPTS)
    assert readiness["failed_count"] == 0
    assert readiness["section_closed"] is True
    assert readiness["safe_to_continue_to_gp101"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp101"] is True
    assert checkpoint["vault_done"] is False
    assert checkpoint["clouds_should_continue"] is False

    for field in FALSE_FIELDS:
        assert readiness[field] is False
        assert checkpoint[field] is False

    status = get_gp100_status(gp096_100_db)["gp100_status"]
    assert status["ready"] is True
    assert status["validation_passed"] is True
    assert status["section_closed"] is True
    assert status["safe_to_continue_to_gp101"] is True
    assert status["next_section"] == "ARCHIVE_VAULT_REAL_PROVIDER_RECOVERY_CASE_WORKSPACE_LAYER"
    assert status["next_section_range"] == "GP101-GP110"
    assert status["next_pack"] == "VAULT_GP101_110_REAL_PROVIDER_RECOVERY_CASE_WORKSPACE_LAYER"
    assert status["vault_done"] is False
    assert status["clouds_status"] == "parked_do_not_continue_from_vault_gp100"

def test_gp096_100_home_validation_and_dark_page(gp096_100_db):
    home = get_post_closeout_handoff_governance_closeout_layer_home(gp096_100_db)
    assert home["pack"]["id"] == "VAULT_GP096_100"
    assert home["store"]["component_count"] == 5
    assert home["store"]["receipt_count"] == len(CLOSEOUT_RECEIPTS)
    assert home["readiness"]["readiness_score"] == 100
    assert home["validation"]["valid"] is True
    assert home["validation"]["failed_count"] == 0
    assert home["truth"]["gp096_to_gp100_layer_ready"] is True
    assert home["truth"]["section_closed"] is True
    assert home["truth"]["safe_to_continue_to_gp101"] is True
    assert home["truth"]["vault_done"] is False
    assert home["truth"]["clouds_should_continue"] is False

    html = render_post_closeout_handoff_governance_closeout_layer_page()
    lowered = html.lower()
    assert "Vault GP096-GP100 Closeout Layer" in html
    assert "GP096-GP100 built" in html
    assert "Safe to GP101" in html
    assert "No restore" in html
    assert "No export" in html
    assert "No provider API" in html
    assert "No object body" in html
    assert "No execution" in html
    assert "VAULT_GP101_110_REAL_PROVIDER_RECOVERY_CASE_WORKSPACE_LAYER" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp096_100_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/post-closeout-handoff-governance-closeout-layer",
        "/vault/post-closeout-handoff-governance-closeout-layer.json",
        "/vault/post-closeout-handoff-owner-review-closeout-lock-contract.json",
        "/vault/post-closeout-handoff-owner-review-closeout-receipt-ledger.json",
        "/vault/post-closeout-handoff-owner-summary.json",
        "/vault/post-closeout-handoff-section-closeout-packet.json",
        "/vault/post-closeout-handoff-governance-readiness-checkpoint.json",
        "/vault/gp096-status.json",
        "/vault/gp097-status.json",
        "/vault/gp098-status.json",
        "/vault/gp099-status.json",
        "/vault/gp100-status.json",
    ]
    for route in required_routes:
        assert route in text
