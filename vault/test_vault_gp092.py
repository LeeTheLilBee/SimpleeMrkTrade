"""
Tests for VAULT GP092 — Real Provider Post-Closeout Handoff Receipt Ledger
"""

from pathlib import Path
import pytest

from vault.real_provider_post_closeout_handoff_receipt_ledger_service import (
    DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID,
    RECEIPT_POLICIES,
    RECEIPT_SPECS,
    ensure_post_closeout_handoff_receipt_ledger_schema,
    get_gp092_status,
    get_post_closeout_handoff_receipt_blockers,
    get_post_closeout_handoff_receipt_events,
    get_post_closeout_handoff_receipt_ledger_record,
    get_post_closeout_handoff_receipt_next_step,
    get_post_closeout_handoff_receipt_policies,
    get_post_closeout_handoff_receipts,
    get_real_provider_post_closeout_handoff_receipt_ledger_home,
    initialize_real_provider_post_closeout_handoff_receipt_ledger,
    record_post_closeout_handoff_receipt_event,
    render_real_provider_post_closeout_handoff_receipt_ledger_page,
    validate_post_closeout_handoff_receipt_ledger,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp092_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "post_closeout_handoff_receipt_ledger.sqlite")

def test_gp092_schema_and_initialize_are_real_sqlite_backed(gp092_db):
    schema = ensure_post_closeout_handoff_receipt_ledger_schema(gp092_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_post_closeout_handoff_receipt_ledgers" in schema["tables"]
    assert "vault_post_closeout_handoff_receipts" in schema["tables"]
    assert "vault_post_closeout_handoff_receipt_policies" in schema["tables"]
    assert "vault_post_closeout_handoff_receipt_blockers" in schema["tables"]
    assert "vault_post_closeout_handoff_receipt_events" in schema["tables"]

    result = initialize_real_provider_post_closeout_handoff_receipt_ledger(gp092_db)
    assert result["initialized"] is True
    assert result["ledger_count"] == 1
    assert result["receipt_count"] == len(RECEIPT_SPECS)
    assert result["policy_count"] == len(RECEIPT_POLICIES)
    assert result["blocker_count"] == 8
    assert result["event_count"] >= 6

def test_gp092_ledger_sources_gp091_and_carries_gp090_hash(gp092_db):
    ledger = get_post_closeout_handoff_receipt_ledger_record(gp092_db)["receipt_ledger"]

    assert ledger["receipt_ledger_id"] == DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID
    assert ledger["pack_id"] == "VAULT_GP092"
    assert ledger["section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_GOVERNANCE_LAYER"
    assert ledger["section_range"] == "GP091-GP100"
    assert ledger["source_handoff_lock_contract_id"] == "VPPCHLC-GP091-001"
    assert isinstance(ledger["source_gp090_readiness_hash"], str)
    assert len(ledger["source_gp090_readiness_hash"]) == 64
    assert ledger["source_gp090_readiness_score"] == 100
    assert isinstance(ledger["ledger_hash"], str)
    assert len(ledger["ledger_hash"]) == 64

    assert ledger["post_closeout_handoff_receipt_ledger_ready"] is True
    assert ledger["source_gp091_handoff_contract_attached"] is True
    assert ledger["source_gp090_readiness_hash_attached"] is True
    assert ledger["receipt_rows_ready"] is True
    assert ledger["receipt_hashes_ready"] is True
    assert ledger["ledger_hash_ready"] is True
    assert ledger["receipt_policies_ready"] is True
    assert ledger["receipt_blockers_ready"] is True
    assert ledger["receipt_validation_ready"] is True
    assert ledger["receipt_ledger_locked"] is True
    assert ledger["receipt_ledger_template_only"] is True
    assert ledger["safe_to_continue_to_gp093"] is True

    locked_false_fields = [
        "receipt_unlock_enabled",
        "restore_request_submitted",
        "restore_object_selected",
        "restore_job_created",
        "provider_restore_api_called",
        "object_body_read",
        "object_body_view_enabled",
        "object_body_download_enabled",
        "restore_export_package_created",
        "export_package_created",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
        "tower_unlock_granted",
        "vault_done",
        "clouds_should_continue",
    ]
    for field in locked_false_fields:
        assert ledger[field] is False

def test_gp092_receipts_policies_blockers_are_locked(gp092_db):
    receipts = get_post_closeout_handoff_receipts(gp092_db)
    assert receipts["receipt_count"] == len(RECEIPT_SPECS)
    assert receipts["receipt_recorded_count"] == len(RECEIPT_SPECS)
    assert receipts["receipt_hash_recorded_count"] == len(RECEIPT_SPECS)
    assert receipts["receipt_locked_count"] == len(RECEIPT_SPECS)
    assert receipts["receipt_unlock_enabled_count"] == 0
    assert receipts["provider_restore_api_called_count"] == 0
    assert receipts["object_body_read_count"] == 0
    assert receipts["export_enabled_count"] == 0
    assert receipts["direct_upload_enabled_count"] == 0
    assert receipts["execution_enabled_count"] == 0
    assert receipts["vault_done_count"] == 0
    assert receipts["clouds_should_continue_count"] == 0

    for item in receipts["receipts"]:
        assert item["receipt_hash"]
        assert len(item["receipt_hash"]) == 64
        assert item["receipt_payload"]
        assert item["receipt_unlock_enabled"] is False
        assert item["provider_restore_api_called"] is False
        assert item["object_body_read"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False
        assert item["vault_done"] is False

    policies = get_post_closeout_handoff_receipt_policies(gp092_db)
    assert policies["policy_count"] == len(RECEIPT_POLICIES)
    assert policies["policy_required_count"] == len(RECEIPT_POLICIES)
    assert policies["receipt_unlock_enabled_count"] == 0
    assert policies["provider_restore_api_called_count"] == 0
    assert policies["object_body_read_count"] == 0
    assert policies["export_enabled_count"] == 0
    assert policies["direct_upload_enabled_count"] == 0
    assert policies["execution_enabled_count"] == 0
    assert policies["vault_done_count"] == 0
    assert policies["clouds_should_continue_count"] == 0

    blockers = get_post_closeout_handoff_receipt_blockers(gp092_db)
    assert blockers["blocker_count"] == 8
    assert blockers["blocker_active_count"] == 8
    assert blockers["blocks_receipt_unlock_count"] == 8
    assert blockers["blocks_restore_unlock_count"] == 8
    assert blockers["blocks_provider_restore_api_count"] == 8
    assert blockers["blocks_object_body_access_count"] == 8
    assert blockers["blocks_export_count"] == 8
    assert blockers["blocks_direct_upload_count"] == 8
    assert blockers["blocks_execution_count"] == 8
    assert blockers["blocks_vault_done_count"] == 8
    assert blockers["resolved_count"] == 0

def test_gp092_event_log_and_manual_event_do_not_unlock(gp092_db):
    events = get_post_closeout_handoff_receipt_events(gp092_db)
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_CREATED" in event_types
    assert "SOURCE_GP091_HANDOFF_CONTRACT_ATTACHED" in event_types
    assert "SOURCE_GP090_READINESS_HASH_CARRIED_FORWARD" in event_types
    assert "POST_CLOSEOUT_HANDOFF_RECEIPTS_RECORDED" in event_types
    assert "POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_HASH_RECORDED" in event_types
    assert "POST_CLOSEOUT_HANDOFF_RECEIPT_LOCKS_CONFIRMED" in event_types

    before = events["event_count"]
    written = record_post_closeout_handoff_receipt_event(
        "OWNER_GP092_RECEIPT_LEDGER_REVIEWED",
        {"reviewer": "owner"},
        gp092_db,
    )
    after = get_post_closeout_handoff_receipt_events(gp092_db)

    assert after["event_count"] == before + 1
    assert written["event_written"] is True
    assert written["receipt_ledger_locked"] is True
    assert written["receipt_unlock_enabled"] is False
    assert written["provider_restore_api_called"] is False
    assert written["object_body_read"] is False
    assert written["export_package_created"] is False
    assert written["direct_upload_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False
    assert written["clouds_should_continue"] is False

def test_gp092_validation_home_status_and_next_step(gp092_db):
    validation = validate_post_closeout_handoff_receipt_ledger(gp092_db)
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert len(validation["ledger_hash"]) == 64
    assert validation["safe_to_continue_to_gp093"] is True
    assert validation["vault_done"] is False
    assert validation["clouds_should_continue"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_EXISTS" in codes
    assert "SOURCE_GP091_HANDOFF_CONTRACT_ATTACHED" in codes
    assert "SOURCE_GP090_READINESS_HASH_ATTACHED" in codes
    assert "SOURCE_GP090_READINESS_SCORE_100" in codes
    assert "LEDGER_HASH_MATCHES" in codes
    assert "ALL_RECEIPT_HASHES_MATCH" in codes
    assert "NO_LEDGER_PROVIDER_RESTORE_API_CALLED" in codes
    assert "NO_LEDGER_OBJECT_BODY_READ" in codes
    assert "NO_LEDGER_EXPORT_ENABLED" in codes
    assert "NO_LEDGER_DIRECT_UPLOAD_ENABLED" in codes
    assert "NO_LEDGER_EXECUTION_ENABLED" in codes
    assert "NO_LEDGER_VAULT_DONE" in codes

    home = get_real_provider_post_closeout_handoff_receipt_ledger_home(gp092_db)
    truth = home["receipt_ledger_truth"]
    assert truth["real_provider_post_closeout_handoff_receipt_ledger_ready"] is True
    assert truth["source_gp091_handoff_contract_attached"] is True
    assert len(truth["source_gp090_readiness_hash"]) == 64
    assert truth["source_gp090_readiness_score"] == 100
    assert truth["receipt_count"] == len(RECEIPT_SPECS)
    assert truth["policy_count"] == len(RECEIPT_POLICIES)
    assert truth["blocker_count"] == 8
    assert len(truth["ledger_hash"]) == 64
    assert truth["receipt_ledger_locked"] is True
    assert truth["receipt_unlock_enabled"] is False
    assert truth["provider_restore_api_called"] is False
    assert truth["object_body_read"] is False
    assert truth["export_package_created"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["execution_enabled"] is False
    assert truth["vault_done"] is False
    assert truth["clouds_should_continue"] is False

    status = get_gp092_status(gp092_db)
    gp092 = status["gp092_status"]
    assert gp092["ready"] is True
    assert gp092["section_range"] == "GP091-GP100"
    assert gp092["source_gp091_handoff_contract_attached"] is True
    assert gp092["source_gp090_readiness_score"] == 100
    assert len(gp092["source_gp090_readiness_hash"]) == 64
    assert gp092["validation_passed"] is True
    assert gp092["safe_to_continue_to_gp093"] is True
    assert gp092["receipt_count"] == len(RECEIPT_SPECS)
    assert gp092["receipt_unlock_enabled_count"] == 0
    assert gp092["provider_restore_api_called_count"] == 0
    assert gp092["object_body_read_count"] == 0
    assert gp092["export_enabled_count"] == 0
    assert gp092["direct_upload_enabled_count"] == 0
    assert gp092["execution_enabled_count"] == 0
    assert gp092["vault_done_count"] == 0
    assert gp092["vault_done"] is False
    assert gp092["clouds_status"] == "parked_do_not_continue_from_vault_gp092"
    assert gp092["next_pack"] == "VAULT_GP093_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE"

    next_step = get_post_closeout_handoff_receipt_next_step()["next_step"]
    assert next_step["current_section_range"] == "GP091-GP100"
    assert next_step["next_pack"] == "VAULT_GP093_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE"
    assert next_step["safe_to_continue_to_gp093"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp092_html_is_dark_and_mentions_receipt_ledger(monkeypatch, tmp_path):
    envs = {
        "VAULT_STORAGE_PROVIDER_DECISION_DB": "html_decision.sqlite",
        "VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB": "html_selection.sqlite",
        "VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB": "html_capability.sqlite",
        "VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB": "html_validation.sqlite",
        "VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB": "html_receipt.sqlite",
        "VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB": "html_readiness.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB": "html_config.sqlite",
        "VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB": "html_credential.sqlite",
        "VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB": "html_ledger.sqlite",
        "VAULT_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT_DB": "html_endpoint.sqlite",
        "VAULT_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT_DB": "html_encryption.sqlite",
        "VAULT_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT_DB": "html_connection.sqlite",
        "VAULT_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT_DB": "html_write.sqlite",
        "VAULT_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT_DB": "html_read.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT_DB": "html_obv.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT_DB": "html_gp070.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT_DB": "html_gp071.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_METADATA_RECEIPT_CONTRACT_DB": "html_gp072.sqlite",
        "VAULT_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_CONTRACT_DB": "html_gp073.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_DB": "html_gp074.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_PACKET_LOCK_CONTRACT_DB": "html_gp075.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_QUEUE_LOCK_CONTRACT_DB": "html_gp076.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_LOCK_CONTRACT_DB": "html_gp077.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_DB": "html_gp078.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_CLOSEOUT_LOCK_CONTRACT_DB": "html_gp079.sqlite",
        "VAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_DB": "html_gp080.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT_DB": "html_gp081.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_ELIGIBILITY_LOCK_CONTRACT_DB": "html_gp082.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_AUTHORITY_LOCK_CONTRACT_DB": "html_gp083.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_SCOPE_LOCK_CONTRACT_DB": "html_gp084.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_TARGET_LOCK_CONTRACT_DB": "html_gp085.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_OBJECT_LOCK_CONTRACT_DB": "html_gp086.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_JOB_LOCK_CONTRACT_DB": "html_gp087.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_API_LOCK_CONTRACT_DB": "html_gp088.sqlite",
        "VAULT_STORAGE_PROVIDER_RESTORE_EXPORT_LOCK_CONTRACT_DB": "html_gp089.sqlite",
        "VAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_DB": "html_gp090.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_DB": "html_gp091.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_DB": "html_gp092.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_provider_post_closeout_handoff_receipt_ledger_page()
    lowered = html.lower()

    assert "Vault Post-Closeout Handoff Receipt Ledger" in html
    assert "GP092" in html
    assert "Post-Closeout Handoff Governance Layer" in html
    assert "Ledger hash recorded" in html
    assert "Receipt hashes recorded" in html
    assert "GP090 hash carried" in html
    assert "No provider API" in html
    assert "No body read" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-provider-post-closeout-handoff-receipt-ledger.json" in html
    assert "/vault/gp092-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp092_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-provider-post-closeout-handoff-receipt-ledger",
        "/vault/real-provider-post-closeout-handoff-receipt-ledger.json",
        "/vault/post-closeout-handoff-receipt-ledger-record.json",
        "/vault/post-closeout-handoff-receipts.json",
        "/vault/post-closeout-handoff-receipt-policies.json",
        "/vault/post-closeout-handoff-receipt-blockers.json",
        "/vault/post-closeout-handoff-receipt-events.json",
        "/vault/post-closeout-handoff-receipt-validation.json",
        "/vault/post-closeout-handoff-receipt-next-step.json",
        "/vault/gp092-status.json",
    ]
    for route in required_routes:
        assert route in text
