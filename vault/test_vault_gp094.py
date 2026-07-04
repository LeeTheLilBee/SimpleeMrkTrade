"""
Tests for VAULT GP094 — Real Provider Post-Closeout Handoff Owner Review Decision Lock Contract
"""

from pathlib import Path
import pytest

from vault.real_provider_post_closeout_handoff_owner_review_decision_lock_contract_service import (
    DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,
    DECISION_POLICIES,
    DECISION_REQUIREMENT_SPECS,
    ensure_post_closeout_handoff_owner_review_decision_lock_contract_schema,
    get_gp094_status,
    get_post_closeout_handoff_owner_review_decision_blockers,
    get_post_closeout_handoff_owner_review_decision_events,
    get_post_closeout_handoff_owner_review_decision_lock_contract_record,
    get_post_closeout_handoff_owner_review_decision_next_step,
    get_post_closeout_handoff_owner_review_decision_policies,
    get_post_closeout_handoff_owner_review_decision_requirements,
    get_real_provider_post_closeout_handoff_owner_review_decision_lock_contract_home,
    initialize_real_provider_post_closeout_handoff_owner_review_decision_lock_contract,
    record_post_closeout_handoff_owner_review_decision_event,
    render_real_provider_post_closeout_handoff_owner_review_decision_lock_contract_page,
    validate_post_closeout_handoff_owner_review_decision_lock_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp094_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "post_closeout_handoff_owner_review_decision_lock_contract.sqlite")

def test_gp094_schema_and_initialize_are_real_sqlite_backed(gp094_db):
    schema = ensure_post_closeout_handoff_owner_review_decision_lock_contract_schema(gp094_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_post_closeout_handoff_owner_review_decision_lock_contracts" in schema["tables"]
    assert "vault_post_closeout_handoff_owner_review_decision_requirements" in schema["tables"]
    assert "vault_post_closeout_handoff_owner_review_decision_policies" in schema["tables"]
    assert "vault_post_closeout_handoff_owner_review_decision_blockers" in schema["tables"]
    assert "vault_post_closeout_handoff_owner_review_decision_events" in schema["tables"]

    result = initialize_real_provider_post_closeout_handoff_owner_review_decision_lock_contract(gp094_db)
    assert result["initialized"] is True
    assert result["contract_count"] == 1
    assert result["requirement_count"] == len(DECISION_REQUIREMENT_SPECS)
    assert result["policy_count"] == len(DECISION_POLICIES)
    assert result["blocker_count"] == 10
    assert result["event_count"] >= 6

def test_gp094_contract_sources_gp093_and_locks_decision(gp094_db):
    contract = get_post_closeout_handoff_owner_review_decision_lock_contract_record(gp094_db)["decision_lock_contract"]

    assert contract["decision_lock_contract_id"] == DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP094"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_GOVERNANCE_LAYER"
    assert contract["section_range"] == "GP091-GP100"
    assert contract["source_owner_review_queue_id"] == "VPPCHORQ-GP093-001"
    assert contract["source_receipt_ledger_id"] == "VPPCHRL-GP092-001"
    assert isinstance(contract["source_ledger_hash"], str)
    assert len(contract["source_ledger_hash"]) == 64
    assert isinstance(contract["source_gp090_readiness_hash"], str)
    assert len(contract["source_gp090_readiness_hash"]) == 64
    assert contract["source_gp090_readiness_score"] == 100
    assert contract["source_review_item_count"] == 8

    assert contract["owner_review_decision_lock_contract_ready"] is True
    assert contract["source_gp093_owner_review_queue_attached"] is True
    assert contract["source_gp092_receipt_ledger_attached"] is True
    assert contract["source_gp091_handoff_contract_attached"] is True
    assert contract["source_gp090_readiness_hash_attached"] is True
    assert contract["decision_requirements_ready"] is True
    assert contract["decision_policies_ready"] is True
    assert contract["decision_blockers_ready"] is True
    assert contract["decision_events_ready"] is True
    assert contract["decision_validation_ready"] is True
    assert contract["owner_review_decision_locked"] is True
    assert contract["owner_review_decision_template_only"] is True
    assert contract["safe_to_continue_to_gp095"] is True

    locked_false_fields = [
        "owner_review_decision_recorded",
        "owner_review_approval_recorded",
        "owner_review_rejection_recorded",
        "decision_receipt_created",
        "tower_unlock_granted",
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
        "vault_done",
        "clouds_should_continue",
    ]
    for field in locked_false_fields:
        assert contract[field] is False

def test_gp094_requirements_policies_blockers_are_locked(gp094_db):
    requirements = get_post_closeout_handoff_owner_review_decision_requirements(gp094_db)
    assert requirements["requirement_count"] == len(DECISION_REQUIREMENT_SPECS)
    assert requirements["requirement_required_count"] == len(DECISION_REQUIREMENT_SPECS)
    assert requirements["decision_locked_count"] == len(DECISION_REQUIREMENT_SPECS)
    assert requirements["owner_review_decision_recorded_count"] == 0
    assert requirements["owner_review_approval_recorded_count"] == 0
    assert requirements["owner_review_rejection_recorded_count"] == 0
    assert requirements["decision_receipt_created_count"] == 0
    assert requirements["tower_unlock_granted_count"] == 0
    assert requirements["provider_restore_api_called_count"] == 0
    assert requirements["object_body_read_count"] == 0
    assert requirements["export_enabled_count"] == 0
    assert requirements["direct_upload_enabled_count"] == 0
    assert requirements["execution_enabled_count"] == 0
    assert requirements["vault_done_count"] == 0

    policies = get_post_closeout_handoff_owner_review_decision_policies(gp094_db)
    assert policies["policy_count"] == len(DECISION_POLICIES)
    assert policies["policy_required_count"] == len(DECISION_POLICIES)
    assert policies["owner_review_decision_recorded_count"] == 0
    assert policies["owner_review_approval_recorded_count"] == 0
    assert policies["owner_review_rejection_recorded_count"] == 0
    assert policies["decision_receipt_created_count"] == 0
    assert policies["tower_unlock_granted_count"] == 0
    assert policies["provider_restore_api_called_count"] == 0
    assert policies["object_body_read_count"] == 0
    assert policies["export_enabled_count"] == 0
    assert policies["direct_upload_enabled_count"] == 0
    assert policies["execution_enabled_count"] == 0
    assert policies["vault_done_count"] == 0

    blockers = get_post_closeout_handoff_owner_review_decision_blockers(gp094_db)
    assert blockers["blocker_count"] == 10
    assert blockers["blocker_active_count"] == 10
    assert blockers["blocks_owner_decision_count"] == 10
    assert blockers["blocks_owner_approval_count"] == 10
    assert blockers["blocks_owner_rejection_count"] == 10
    assert blockers["blocks_decision_receipt_count"] == 10
    assert blockers["blocks_tower_unlock_count"] == 10
    assert blockers["blocks_provider_restore_api_count"] == 10
    assert blockers["blocks_object_body_access_count"] == 10
    assert blockers["blocks_export_count"] == 10
    assert blockers["blocks_direct_upload_count"] == 10
    assert blockers["blocks_execution_count"] == 10
    assert blockers["blocks_vault_done_count"] == 10
    assert blockers["resolved_count"] == 0

def test_gp094_event_log_and_manual_event_do_not_unlock(gp094_db):
    events = get_post_closeout_handoff_owner_review_decision_events(gp094_db)
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP093_OWNER_REVIEW_QUEUE_ATTACHED" in event_types
    assert "SOURCE_GP092_LEDGER_AND_GP090_HASH_CARRIED_FORWARD" in event_types
    assert "OWNER_REVIEW_DECISION_REQUIREMENTS_CREATED" in event_types
    assert "OWNER_REVIEW_DECISION_POLICIES_AND_BLOCKERS_RECORDED" in event_types
    assert "OWNER_REVIEW_DECISION_LOCKS_CONFIRMED" in event_types

    before = events["event_count"]
    written = record_post_closeout_handoff_owner_review_decision_event(
        "OWNER_GP094_DECISION_LOCK_REVIEWED",
        {"reviewer": "owner"},
        gp094_db,
    )
    after = get_post_closeout_handoff_owner_review_decision_events(gp094_db)

    assert after["event_count"] == before + 1
    assert written["event_written"] is True
    assert written["owner_review_decision_locked"] is True
    assert written["owner_review_decision_recorded"] is False
    assert written["owner_review_approval_recorded"] is False
    assert written["owner_review_rejection_recorded"] is False
    assert written["decision_receipt_created"] is False
    assert written["tower_unlock_granted"] is False
    assert written["provider_restore_api_called"] is False
    assert written["object_body_read"] is False
    assert written["export_package_created"] is False
    assert written["direct_upload_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False
    assert written["clouds_should_continue"] is False

def test_gp094_validation_home_status_and_next_step(gp094_db):
    validation = validate_post_closeout_handoff_owner_review_decision_lock_contract(gp094_db)
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp095"] is True
    assert validation["vault_done"] is False
    assert validation["clouds_should_continue"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_OWNER_REVIEW_DECISION_LOCK_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP093_OWNER_REVIEW_QUEUE_ATTACHED" in codes
    assert "SOURCE_GP092_LEDGER_ATTACHED" in codes
    assert "SOURCE_GP090_READINESS_HASH_ATTACHED" in codes
    assert "SOURCE_GP090_READINESS_SCORE_100" in codes
    assert "DECISION_LOCKED" in codes
    assert "NO_CONTRACT_OWNER_REVIEW_DECISION_RECORDED" in codes
    assert "NO_CONTRACT_OWNER_REVIEW_APPROVAL_RECORDED" in codes
    assert "NO_CONTRACT_OWNER_REVIEW_REJECTION_RECORDED" in codes
    assert "NO_CONTRACT_DECISION_RECEIPT_CREATED" in codes
    assert "NO_CONTRACT_TOWER_UNLOCK_GRANTED" in codes
    assert "NO_CONTRACT_PROVIDER_RESTORE_API_CALLED" in codes
    assert "NO_CONTRACT_OBJECT_BODY_READ" in codes
    assert "NO_CONTRACT_EXPORT_ENABLED" in codes
    assert "NO_CONTRACT_DIRECT_UPLOAD_ENABLED" in codes
    assert "NO_CONTRACT_EXECUTION_ENABLED" in codes
    assert "NO_CONTRACT_VAULT_DONE" in codes

    home = get_real_provider_post_closeout_handoff_owner_review_decision_lock_contract_home(gp094_db)
    truth = home["decision_lock_truth"]
    assert truth["real_provider_post_closeout_handoff_owner_review_decision_lock_contract_ready"] is True
    assert truth["source_gp093_owner_review_queue_attached"] is True
    assert len(truth["source_ledger_hash"]) == 64
    assert len(truth["source_gp090_readiness_hash"]) == 64
    assert truth["source_gp090_readiness_score"] == 100
    assert truth["requirement_count"] == len(DECISION_REQUIREMENT_SPECS)
    assert truth["policy_count"] == len(DECISION_POLICIES)
    assert truth["blocker_count"] == 10
    assert truth["owner_review_decision_locked"] is True
    assert truth["owner_review_decision_template_only"] is True
    assert truth["owner_review_decision_recorded"] is False
    assert truth["owner_review_approval_recorded"] is False
    assert truth["owner_review_rejection_recorded"] is False
    assert truth["decision_receipt_created"] is False
    assert truth["tower_unlock_granted"] is False
    assert truth["provider_restore_api_called"] is False
    assert truth["object_body_read"] is False
    assert truth["export_package_created"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["execution_enabled"] is False
    assert truth["vault_done"] is False
    assert truth["clouds_should_continue"] is False

    status = get_gp094_status(gp094_db)
    gp094 = status["gp094_status"]
    assert gp094["ready"] is True
    assert gp094["section_range"] == "GP091-GP100"
    assert gp094["source_gp093_owner_review_queue_attached"] is True
    assert gp094["source_gp090_readiness_score"] == 100
    assert len(gp094["source_gp090_readiness_hash"]) == 64
    assert gp094["validation_passed"] is True
    assert gp094["safe_to_continue_to_gp095"] is True
    assert gp094["requirement_count"] == len(DECISION_REQUIREMENT_SPECS)
    assert gp094["owner_review_decision_recorded_count"] == 0
    assert gp094["owner_review_approval_recorded_count"] == 0
    assert gp094["owner_review_rejection_recorded_count"] == 0
    assert gp094["decision_receipt_created_count"] == 0
    assert gp094["tower_unlock_granted_count"] == 0
    assert gp094["provider_restore_api_called_count"] == 0
    assert gp094["object_body_read_count"] == 0
    assert gp094["export_enabled_count"] == 0
    assert gp094["direct_upload_enabled_count"] == 0
    assert gp094["execution_enabled_count"] == 0
    assert gp094["vault_done_count"] == 0
    assert gp094["vault_done"] is False
    assert gp094["clouds_status"] == "parked_do_not_continue_from_vault_gp094"
    assert gp094["next_pack"] == "VAULT_GP095_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT"

    next_step = get_post_closeout_handoff_owner_review_decision_next_step()["next_step"]
    assert next_step["current_section_range"] == "GP091-GP100"
    assert next_step["next_pack"] == "VAULT_GP095_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT"
    assert next_step["safe_to_continue_to_gp095"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp094_html_is_dark_and_mentions_decision_lock(monkeypatch, tmp_path):
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
        "VAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_DB": "html_gp093.sqlite",
        "VAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_DB": "html_gp094.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_provider_post_closeout_handoff_owner_review_decision_lock_contract_page()
    lowered = html.lower()

    assert "Vault Owner Review Decision Lock Contract" in html
    assert "GP094" in html
    assert "Post-Closeout Handoff Governance Layer" in html
    assert "Decision lock built" in html
    assert "GP093 queue attached" in html
    assert "GP090 hash carried" in html
    assert "No decision" in html
    assert "No approval" in html
    assert "No Tower unlock" in html
    assert "No execution" in html
    assert "/vault/real-provider-post-closeout-handoff-owner-review-decision-lock-contract.json" in html
    assert "/vault/gp094-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp094_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-provider-post-closeout-handoff-owner-review-decision-lock-contract",
        "/vault/real-provider-post-closeout-handoff-owner-review-decision-lock-contract.json",
        "/vault/post-closeout-handoff-owner-review-decision-lock-contract-record.json",
        "/vault/post-closeout-handoff-owner-review-decision-requirements.json",
        "/vault/post-closeout-handoff-owner-review-decision-policies.json",
        "/vault/post-closeout-handoff-owner-review-decision-blockers.json",
        "/vault/post-closeout-handoff-owner-review-decision-events.json",
        "/vault/post-closeout-handoff-owner-review-decision-validation.json",
        "/vault/post-closeout-handoff-owner-review-decision-next-step.json",
        "/vault/gp094-status.json",
    ]
    for route in required_routes:
        assert route in text
