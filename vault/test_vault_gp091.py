"""
Tests for VAULT GP091 — Real Provider Post-Closeout Handoff Lock Contract
"""

from pathlib import Path
import pytest

from vault.real_provider_post_closeout_handoff_lock_contract_service import (
    DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID,
    HANDOFF_POLICIES,
    HANDOFF_REQUIREMENT_SPECS,
    ensure_post_closeout_handoff_lock_contract_schema,
    get_gp091_status,
    get_post_closeout_handoff_blockers,
    get_post_closeout_handoff_events,
    get_post_closeout_handoff_lock_contract_record,
    get_post_closeout_handoff_next_step,
    get_post_closeout_handoff_policies,
    get_post_closeout_handoff_requirements,
    get_real_provider_post_closeout_handoff_lock_contract_home,
    initialize_real_provider_post_closeout_handoff_lock_contract,
    record_post_closeout_handoff_event,
    render_real_provider_post_closeout_handoff_lock_contract_page,
    validate_post_closeout_handoff_lock_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp091_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "post_closeout_handoff_lock_contract.sqlite")

def test_gp091_schema_and_initialize_are_real_sqlite_backed(gp091_db):
    schema = ensure_post_closeout_handoff_lock_contract_schema(gp091_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_post_closeout_handoff_lock_contracts" in schema["tables"]
    assert "vault_post_closeout_handoff_requirements" in schema["tables"]
    assert "vault_post_closeout_handoff_policies" in schema["tables"]
    assert "vault_post_closeout_handoff_blockers" in schema["tables"]
    assert "vault_post_closeout_handoff_events" in schema["tables"]

    result = initialize_real_provider_post_closeout_handoff_lock_contract(gp091_db)
    assert result["initialized"] is True
    assert result["contract_count"] == 1
    assert result["requirement_count"] == len(HANDOFF_REQUIREMENT_SPECS)
    assert result["policy_count"] == len(HANDOFF_POLICIES)
    assert result["blocker_count"] == 7
    assert result["event_count"] >= 6

def test_gp091_contract_sources_gp090_and_starts_new_section(gp091_db):
    contract = get_post_closeout_handoff_lock_contract_record(gp091_db)["handoff_lock_contract"]

    assert contract["handoff_lock_contract_id"] == DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP091"
    assert contract["previous_section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_LAYER"
    assert contract["previous_section_range"] == "GP081-GP090"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_GOVERNANCE_LAYER"
    assert contract["section_range"] == "GP091-GP100"

    assert contract["source_gp090_checkpoint_id"] == "VRERGRC-GP090-001"
    assert isinstance(contract["source_gp090_readiness_hash"], str)
    assert len(contract["source_gp090_readiness_hash"]) == 64
    assert contract["source_gp090_readiness_score"] == 100
    assert contract["source_gp090_next_pack"] == "VAULT_GP091_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT"

    assert contract["post_closeout_handoff_lock_contract_ready"] is True
    assert contract["post_closeout_handoff_requirements_ready"] is True
    assert contract["post_closeout_handoff_policies_ready"] is True
    assert contract["post_closeout_handoff_blockers_ready"] is True
    assert contract["post_closeout_handoff_validation_ready"] is True
    assert contract["source_gp090_checkpoint_attached"] is True
    assert contract["source_gp090_readiness_hash_attached"] is True
    assert contract["source_gp090_section_closed"] is True
    assert contract["post_closeout_handoff_locked"] is True
    assert contract["post_closeout_template_only"] is True
    assert contract["safe_to_continue_to_gp092"] is True

    locked_false_fields = [
        "handoff_unlock_enabled",
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
        assert contract[field] is False

def test_gp091_requirements_policies_blockers_are_locked(gp091_db):
    requirements = get_post_closeout_handoff_requirements(gp091_db)
    assert requirements["requirement_count"] == len(HANDOFF_REQUIREMENT_SPECS)
    assert requirements["requirement_required_count"] == len(HANDOFF_REQUIREMENT_SPECS)
    assert requirements["handoff_locked_count"] == len(HANDOFF_REQUIREMENT_SPECS)
    assert requirements["template_only_count"] == len(HANDOFF_REQUIREMENT_SPECS)
    assert requirements["handoff_unlock_enabled_count"] == 0
    assert requirements["provider_restore_api_called_count"] == 0
    assert requirements["object_body_read_count"] == 0
    assert requirements["export_enabled_count"] == 0
    assert requirements["execution_enabled_count"] == 0
    assert requirements["vault_done_count"] == 0
    assert requirements["clouds_should_continue_count"] == 0

    policies = get_post_closeout_handoff_policies(gp091_db)
    assert policies["policy_count"] == len(HANDOFF_POLICIES)
    assert policies["policy_required_count"] == len(HANDOFF_POLICIES)
    assert policies["handoff_unlock_enabled_count"] == 0
    assert policies["provider_restore_api_called_count"] == 0
    assert policies["object_body_read_count"] == 0
    assert policies["export_enabled_count"] == 0
    assert policies["execution_enabled_count"] == 0
    assert policies["vault_done_count"] == 0
    assert policies["clouds_should_continue_count"] == 0

    blockers = get_post_closeout_handoff_blockers(gp091_db)
    assert blockers["blocker_count"] == 7
    assert blockers["blocker_active_count"] == 7
    assert blockers["blocks_restore_unlock_count"] == 7
    assert blockers["blocks_provider_restore_api_count"] == 7
    assert blockers["blocks_object_body_access_count"] == 7
    assert blockers["blocks_export_count"] == 7
    assert blockers["blocks_direct_upload_count"] == 7
    assert blockers["blocks_execution_count"] == 7
    assert blockers["blocks_vault_done_count"] == 7
    assert blockers["resolved_count"] == 0

def test_gp091_event_log_and_manual_event_do_not_unlock(gp091_db):
    events = get_post_closeout_handoff_events(gp091_db)
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP090_READINESS_CHECKPOINT_ATTACHED" in event_types
    assert "GP091_NEW_SECTION_OPENED_LOCK_ONLY" in event_types
    assert "POST_CLOSEOUT_HANDOFF_REQUIREMENTS_CREATED" in event_types
    assert "POST_CLOSEOUT_HANDOFF_POLICIES_CREATED" in event_types
    assert "POST_CLOSEOUT_HANDOFF_LOCKS_CONFIRMED" in event_types

    before = events["event_count"]
    written = record_post_closeout_handoff_event(
        "OWNER_GP091_HANDOFF_REVIEWED",
        {"reviewer": "owner"},
        gp091_db,
    )
    after = get_post_closeout_handoff_events(gp091_db)

    assert after["event_count"] == before + 1
    assert written["event_written"] is True
    assert written["post_closeout_handoff_locked"] is True
    assert written["handoff_unlock_enabled"] is False
    assert written["provider_restore_api_called"] is False
    assert written["object_body_read"] is False
    assert written["export_package_created"] is False
    assert written["direct_upload_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False
    assert written["clouds_should_continue"] is False

def test_gp091_validation_home_status_and_next_step(gp091_db):
    validation = validate_post_closeout_handoff_lock_contract(gp091_db)
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp092"] is True
    assert validation["vault_done"] is False
    assert validation["clouds_should_continue"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_POST_CLOSEOUT_HANDOFF_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP090_CHECKPOINT_ATTACHED" in codes
    assert "SOURCE_GP090_READINESS_SCORE_100" in codes
    assert "SOURCE_GP090_HASH_ATTACHED" in codes
    assert "NEW_SECTION_GP091_GP100" in codes
    assert "HANDOFF_LOCKED" in codes
    assert "NO_CONTRACT_PROVIDER_RESTORE_API_CALLED" in codes
    assert "NO_CONTRACT_OBJECT_BODY_READ" in codes
    assert "NO_CONTRACT_EXPORT_ENABLED" in codes
    assert "NO_CONTRACT_EXECUTION_ENABLED" in codes
    assert "NO_CONTRACT_VAULT_DONE" in codes

    home = get_real_provider_post_closeout_handoff_lock_contract_home(gp091_db)
    truth = home["handoff_truth"]
    assert truth["real_provider_post_closeout_handoff_lock_contract_ready"] is True
    assert truth["source_gp090_checkpoint_attached"] is True
    assert len(truth["source_gp090_readiness_hash"]) == 64
    assert truth["source_gp090_readiness_score"] == 100
    assert truth["source_gp090_section_closed"] is True
    assert truth["post_closeout_handoff_locked"] is True
    assert truth["post_closeout_template_only"] is True
    assert truth["handoff_unlock_enabled"] is False
    assert truth["provider_restore_api_called"] is False
    assert truth["object_body_read"] is False
    assert truth["export_package_created"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["execution_enabled"] is False
    assert truth["vault_done"] is False
    assert truth["clouds_should_continue"] is False

    status = get_gp091_status(gp091_db)
    gp091 = status["gp091_status"]
    assert gp091["ready"] is True
    assert gp091["section_range"] == "GP091-GP100"
    assert gp091["source_gp090_readiness_score"] == 100
    assert len(gp091["source_gp090_readiness_hash"]) == 64
    assert gp091["validation_passed"] is True
    assert gp091["safe_to_continue_to_gp092"] is True
    assert gp091["vault_done"] is False
    assert gp091["clouds_status"] == "parked_do_not_continue_from_vault_gp091"
    assert gp091["next_pack"] == "VAULT_GP092_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER"

    next_step = get_post_closeout_handoff_next_step()["next_step"]
    assert next_step["current_section_range"] == "GP091-GP100"
    assert next_step["previous_section_range"] == "GP081-GP090"
    assert next_step["next_pack"] == "VAULT_GP092_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER"
    assert next_step["safe_to_continue_to_gp092"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp091_html_is_dark_and_mentions_new_section(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_provider_post_closeout_handoff_lock_contract_page()
    lowered = html.lower()

    assert "Vault Post-Closeout Handoff Lock Contract" in html
    assert "GP091" in html
    assert "Post-Closeout Handoff Governance Layer" in html
    assert "GP090 hash attached" in html
    assert "New section opened" in html
    assert "Handoff locked" in html
    assert "No provider API" in html
    assert "No body read" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-provider-post-closeout-handoff-lock-contract.json" in html
    assert "/vault/gp091-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp091_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-provider-post-closeout-handoff-lock-contract",
        "/vault/real-provider-post-closeout-handoff-lock-contract.json",
        "/vault/post-closeout-handoff-lock-contract-record.json",
        "/vault/post-closeout-handoff-requirements.json",
        "/vault/post-closeout-handoff-policies.json",
        "/vault/post-closeout-handoff-blockers.json",
        "/vault/post-closeout-handoff-events.json",
        "/vault/post-closeout-handoff-validation.json",
        "/vault/post-closeout-handoff-next-step.json",
        "/vault/gp091-status.json",
    ]
    for route in required_routes:
        assert route in text
