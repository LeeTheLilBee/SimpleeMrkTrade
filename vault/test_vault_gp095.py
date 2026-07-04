"""
Tests for VAULT GP095 — Real Provider Post-Closeout Handoff Owner Review Decision Receipt Lock Contract
"""

from pathlib import Path
import pytest

from vault.real_provider_post_closeout_handoff_owner_review_decision_receipt_lock_contract_service import (
    DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,
    DECISION_RECEIPT_POLICIES,
    DECISION_RECEIPT_REQUIREMENT_SPECS,
    ensure_post_closeout_handoff_owner_review_decision_receipt_lock_contract_schema,
    get_gp095_status,
    get_post_closeout_handoff_owner_review_decision_receipt_blockers,
    get_post_closeout_handoff_owner_review_decision_receipt_events,
    get_post_closeout_handoff_owner_review_decision_receipt_lock_contract_record,
    get_post_closeout_handoff_owner_review_decision_receipt_next_step,
    get_post_closeout_handoff_owner_review_decision_receipt_policies,
    get_post_closeout_handoff_owner_review_decision_receipt_requirements,
    get_real_provider_post_closeout_handoff_owner_review_decision_receipt_lock_contract_home,
    initialize_real_provider_post_closeout_handoff_owner_review_decision_receipt_lock_contract,
    record_post_closeout_handoff_owner_review_decision_receipt_event,
    render_real_provider_post_closeout_handoff_owner_review_decision_receipt_lock_contract_page,
    validate_post_closeout_handoff_owner_review_decision_receipt_lock_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp095_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "post_closeout_handoff_owner_review_decision_receipt_lock_contract.sqlite")

def test_gp095_schema_and_initialize_are_real_sqlite_backed(gp095_db):
    schema = ensure_post_closeout_handoff_owner_review_decision_receipt_lock_contract_schema(gp095_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_post_closeout_handoff_owner_review_decision_receipt_lock_contracts" in schema["tables"]
    assert "vault_post_closeout_handoff_owner_review_decision_receipt_requirements" in schema["tables"]
    assert "vault_post_closeout_handoff_owner_review_decision_receipt_policies" in schema["tables"]
    assert "vault_post_closeout_handoff_owner_review_decision_receipt_blockers" in schema["tables"]
    assert "vault_post_closeout_handoff_owner_review_decision_receipt_events" in schema["tables"]

    result = initialize_real_provider_post_closeout_handoff_owner_review_decision_receipt_lock_contract(gp095_db)
    assert result["initialized"] is True
    assert result["contract_count"] == 1
    assert result["requirement_count"] == len(DECISION_RECEIPT_REQUIREMENT_SPECS)
    assert result["policy_count"] == len(DECISION_RECEIPT_POLICIES)
    assert result["blocker_count"] == 10
    assert result["event_count"] >= 6

def test_gp095_contract_sources_gp094_and_locks_decision_receipt(gp095_db):
    contract = get_post_closeout_handoff_owner_review_decision_receipt_lock_contract_record(gp095_db)["decision_receipt_lock_contract"]

    assert contract["decision_receipt_lock_contract_id"] == DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP095"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_GOVERNANCE_LAYER"
    assert contract["section_range"] == "GP091-GP100"
    assert contract["source_decision_lock_contract_id"] == "VPPCHORDLC-GP094-001"
    assert contract["source_owner_review_queue_id"] == "VPPCHORQ-GP093-001"
    assert contract["source_receipt_ledger_id"] == "VPPCHRL-GP092-001"
    assert isinstance(contract["source_ledger_hash"], str)
    assert len(contract["source_ledger_hash"]) == 64
    assert isinstance(contract["source_gp090_readiness_hash"], str)
    assert len(contract["source_gp090_readiness_hash"]) == 64
    assert contract["source_gp090_readiness_score"] == 100
    assert contract["source_review_item_count"] == 8

    assert contract["owner_review_decision_receipt_lock_contract_ready"] is True
    assert contract["source_gp094_decision_lock_contract_attached"] is True
    assert contract["source_gp093_owner_review_queue_attached"] is True
    assert contract["source_gp092_receipt_ledger_attached"] is True
    assert contract["source_gp091_handoff_contract_attached"] is True
    assert contract["source_gp090_readiness_hash_attached"] is True
    assert contract["decision_receipt_requirements_ready"] is True
    assert contract["decision_receipt_policies_ready"] is True
    assert contract["decision_receipt_blockers_ready"] is True
    assert contract["decision_receipt_events_ready"] is True
    assert contract["decision_receipt_validation_ready"] is True
    assert contract["owner_review_decision_receipt_locked"] is True
    assert contract["owner_review_decision_receipt_template_only"] is True
    assert contract["safe_to_continue_to_gp096"] is True

    locked_false_fields = [
        "decision_receipt_created",
        "decision_receipt_hash_created",
        "decision_receipt_packet_created",
        "decision_receipt_persisted",
        "owner_review_decision_recorded",
        "owner_review_approval_recorded",
        "owner_review_rejection_recorded",
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

def test_gp095_requirements_policies_blockers_are_locked(gp095_db):
    requirements = get_post_closeout_handoff_owner_review_decision_receipt_requirements(gp095_db)
    assert requirements["requirement_count"] == len(DECISION_RECEIPT_REQUIREMENT_SPECS)
    assert requirements["requirement_required_count"] == len(DECISION_RECEIPT_REQUIREMENT_SPECS)
    assert requirements["decision_receipt_locked_count"] == len(DECISION_RECEIPT_REQUIREMENT_SPECS)
    assert requirements["decision_receipt_created_count"] == 0
    assert requirements["decision_receipt_hash_created_count"] == 0
    assert requirements["decision_receipt_packet_created_count"] == 0
    assert requirements["decision_receipt_persisted_count"] == 0
    assert requirements["owner_review_decision_recorded_count"] == 0
    assert requirements["owner_review_approval_recorded_count"] == 0
    assert requirements["owner_review_rejection_recorded_count"] == 0
    assert requirements["tower_unlock_granted_count"] == 0
    assert requirements["provider_restore_api_called_count"] == 0
    assert requirements["object_body_read_count"] == 0
    assert requirements["export_enabled_count"] == 0
    assert requirements["direct_upload_enabled_count"] == 0
    assert requirements["execution_enabled_count"] == 0
    assert requirements["vault_done_count"] == 0

    policies = get_post_closeout_handoff_owner_review_decision_receipt_policies(gp095_db)
    assert policies["policy_count"] == len(DECISION_RECEIPT_POLICIES)
    assert policies["policy_required_count"] == len(DECISION_RECEIPT_POLICIES)
    assert policies["decision_receipt_created_count"] == 0
    assert policies["decision_receipt_hash_created_count"] == 0
    assert policies["decision_receipt_packet_created_count"] == 0
    assert policies["decision_receipt_persisted_count"] == 0
    assert policies["owner_review_decision_recorded_count"] == 0
    assert policies["owner_review_approval_recorded_count"] == 0
    assert policies["owner_review_rejection_recorded_count"] == 0
    assert policies["tower_unlock_granted_count"] == 0
    assert policies["provider_restore_api_called_count"] == 0
    assert policies["object_body_read_count"] == 0
    assert policies["export_enabled_count"] == 0
    assert policies["direct_upload_enabled_count"] == 0
    assert policies["execution_enabled_count"] == 0
    assert policies["vault_done_count"] == 0

    blockers = get_post_closeout_handoff_owner_review_decision_receipt_blockers(gp095_db)
    assert blockers["blocker_count"] == 10
    assert blockers["blocker_active_count"] == 10
    assert blockers["blocks_decision_receipt_count"] == 10
    assert blockers["blocks_owner_decision_count"] == 10
    assert blockers["blocks_owner_approval_count"] == 10
    assert blockers["blocks_owner_rejection_count"] == 10
    assert blockers["blocks_tower_unlock_count"] == 10
    assert blockers["blocks_provider_restore_api_count"] == 10
    assert blockers["blocks_object_body_access_count"] == 10
    assert blockers["blocks_export_count"] == 10
    assert blockers["blocks_direct_upload_count"] == 10
    assert blockers["blocks_execution_count"] == 10
    assert blockers["blocks_vault_done_count"] == 10
    assert blockers["resolved_count"] == 0

def test_gp095_event_log_and_manual_event_do_not_unlock(gp095_db):
    events = get_post_closeout_handoff_owner_review_decision_receipt_events(gp095_db)
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP094_DECISION_LOCK_CONTRACT_ATTACHED" in event_types
    assert "SOURCE_GP092_LEDGER_AND_GP090_HASH_CARRIED_FORWARD" in event_types
    assert "OWNER_REVIEW_DECISION_RECEIPT_REQUIREMENTS_CREATED" in event_types
    assert "OWNER_REVIEW_DECISION_RECEIPT_POLICIES_AND_BLOCKERS_RECORDED" in event_types
    assert "OWNER_REVIEW_DECISION_RECEIPT_LOCKS_CONFIRMED" in event_types

    before = events["event_count"]
    written = record_post_closeout_handoff_owner_review_decision_receipt_event(
        "OWNER_GP095_DECISION_RECEIPT_LOCK_REVIEWED",
        {"reviewer": "owner"},
        gp095_db,
    )
    after = get_post_closeout_handoff_owner_review_decision_receipt_events(gp095_db)

    assert after["event_count"] == before + 1
    assert written["event_written"] is True
    assert written["owner_review_decision_receipt_locked"] is True
    assert written["decision_receipt_created"] is False
    assert written["decision_receipt_hash_created"] is False
    assert written["decision_receipt_packet_created"] is False
    assert written["decision_receipt_persisted"] is False
    assert written["owner_review_decision_recorded"] is False
    assert written["owner_review_approval_recorded"] is False
    assert written["owner_review_rejection_recorded"] is False
    assert written["tower_unlock_granted"] is False
    assert written["provider_restore_api_called"] is False
    assert written["object_body_read"] is False
    assert written["export_package_created"] is False
    assert written["direct_upload_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False
    assert written["clouds_should_continue"] is False

def test_gp095_validation_home_status_and_next_step(gp095_db):
    validation = validate_post_closeout_handoff_owner_review_decision_receipt_lock_contract(gp095_db)
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp096"] is True
    assert validation["vault_done"] is False
    assert validation["clouds_should_continue"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP094_DECISION_LOCK_CONTRACT_ATTACHED" in codes
    assert "SOURCE_GP093_QUEUE_ATTACHED" in codes
    assert "SOURCE_GP092_LEDGER_ATTACHED" in codes
    assert "SOURCE_GP090_READINESS_HASH_ATTACHED" in codes
    assert "SOURCE_GP090_READINESS_SCORE_100" in codes
    assert "DECISION_RECEIPT_LOCKED" in codes
    assert "NO_CONTRACT_DECISION_RECEIPT_CREATED" in codes
    assert "NO_CONTRACT_DECISION_RECEIPT_HASH_CREATED" in codes
    assert "NO_CONTRACT_DECISION_RECEIPT_PACKET_CREATED" in codes
    assert "NO_CONTRACT_OWNER_REVIEW_DECISION_RECORDED" in codes
    assert "NO_CONTRACT_OWNER_REVIEW_APPROVAL_RECORDED" in codes
    assert "NO_CONTRACT_OWNER_REVIEW_REJECTION_RECORDED" in codes
    assert "NO_CONTRACT_TOWER_UNLOCK_GRANTED" in codes
    assert "NO_CONTRACT_PROVIDER_RESTORE_API_CALLED" in codes
    assert "NO_CONTRACT_OBJECT_BODY_READ" in codes
    assert "NO_CONTRACT_EXPORT_ENABLED" in codes
    assert "NO_CONTRACT_DIRECT_UPLOAD_ENABLED" in codes
    assert "NO_CONTRACT_EXECUTION_ENABLED" in codes
    assert "NO_CONTRACT_VAULT_DONE" in codes

    home = get_real_provider_post_closeout_handoff_owner_review_decision_receipt_lock_contract_home(gp095_db)
    truth = home["decision_receipt_lock_truth"]
    assert truth["real_provider_post_closeout_handoff_owner_review_decision_receipt_lock_contract_ready"] is True
    assert truth["source_gp094_decision_lock_contract_attached"] is True
    assert len(truth["source_ledger_hash"]) == 64
    assert len(truth["source_gp090_readiness_hash"]) == 64
    assert truth["source_gp090_readiness_score"] == 100
    assert truth["requirement_count"] == len(DECISION_RECEIPT_REQUIREMENT_SPECS)
    assert truth["policy_count"] == len(DECISION_RECEIPT_POLICIES)
    assert truth["blocker_count"] == 10
    assert truth["owner_review_decision_receipt_locked"] is True
    assert truth["owner_review_decision_receipt_template_only"] is True
    assert truth["decision_receipt_created"] is False
    assert truth["decision_receipt_hash_created"] is False
    assert truth["decision_receipt_packet_created"] is False
    assert truth["decision_receipt_persisted"] is False
    assert truth["owner_review_decision_recorded"] is False
    assert truth["owner_review_approval_recorded"] is False
    assert truth["owner_review_rejection_recorded"] is False
    assert truth["tower_unlock_granted"] is False
    assert truth["provider_restore_api_called"] is False
    assert truth["object_body_read"] is False
    assert truth["export_package_created"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["execution_enabled"] is False
    assert truth["vault_done"] is False
    assert truth["clouds_should_continue"] is False

    status = get_gp095_status(gp095_db)
    gp095 = status["gp095_status"]
    assert gp095["ready"] is True
    assert gp095["section_range"] == "GP091-GP100"
    assert gp095["source_gp094_decision_lock_contract_attached"] is True
    assert gp095["source_gp090_readiness_score"] == 100
    assert len(gp095["source_gp090_readiness_hash"]) == 64
    assert gp095["validation_passed"] is True
    assert gp095["safe_to_continue_to_gp096"] is True
    assert gp095["requirement_count"] == len(DECISION_RECEIPT_REQUIREMENT_SPECS)
    assert gp095["decision_receipt_created_count"] == 0
    assert gp095["decision_receipt_hash_created_count"] == 0
    assert gp095["decision_receipt_packet_created_count"] == 0
    assert gp095["decision_receipt_persisted_count"] == 0
    assert gp095["owner_review_decision_recorded_count"] == 0
    assert gp095["owner_review_approval_recorded_count"] == 0
    assert gp095["owner_review_rejection_recorded_count"] == 0
    assert gp095["tower_unlock_granted_count"] == 0
    assert gp095["provider_restore_api_called_count"] == 0
    assert gp095["object_body_read_count"] == 0
    assert gp095["export_enabled_count"] == 0
    assert gp095["direct_upload_enabled_count"] == 0
    assert gp095["execution_enabled_count"] == 0
    assert gp095["vault_done_count"] == 0
    assert gp095["vault_done"] is False
    assert gp095["clouds_status"] == "parked_do_not_continue_from_vault_gp095"
    assert gp095["next_pack"] == "VAULT_GP096_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_CLOSEOUT_LOCK_CONTRACT"

    next_step = get_post_closeout_handoff_owner_review_decision_receipt_next_step()["next_step"]
    assert next_step["current_section_range"] == "GP091-GP100"
    assert next_step["next_pack"] == "VAULT_GP096_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_CLOSEOUT_LOCK_CONTRACT"
    assert next_step["safe_to_continue_to_gp096"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp095_html_is_dark_and_mentions_decision_receipt_lock(monkeypatch, tmp_path):
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
        "VAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_DB": "html_gp095.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_provider_post_closeout_handoff_owner_review_decision_receipt_lock_contract_page()
    lowered = html.lower()

    assert "Vault Owner Review Decision Receipt Lock Contract" in html
    assert "GP095" in html
    assert "Post-Closeout Handoff Governance Layer" in html
    assert "Decision receipt lock built" in html
    assert "GP094 contract attached" in html
    assert "GP090 hash carried" in html
    assert "No receipt created" in html
    assert "No decision" in html
    assert "No Tower unlock" in html
    assert "No execution" in html
    assert "/vault/real-provider-post-closeout-handoff-owner-review-decision-receipt-lock-contract.json" in html
    assert "/vault/gp095-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp095_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-provider-post-closeout-handoff-owner-review-decision-receipt-lock-contract",
        "/vault/real-provider-post-closeout-handoff-owner-review-decision-receipt-lock-contract.json",
        "/vault/post-closeout-handoff-owner-review-decision-receipt-lock-contract-record.json",
        "/vault/post-closeout-handoff-owner-review-decision-receipt-requirements.json",
        "/vault/post-closeout-handoff-owner-review-decision-receipt-policies.json",
        "/vault/post-closeout-handoff-owner-review-decision-receipt-blockers.json",
        "/vault/post-closeout-handoff-owner-review-decision-receipt-events.json",
        "/vault/post-closeout-handoff-owner-review-decision-receipt-validation.json",
        "/vault/post-closeout-handoff-owner-review-decision-receipt-next-step.json",
        "/vault/gp095-status.json",
    ]
    for route in required_routes:
        assert route in text
