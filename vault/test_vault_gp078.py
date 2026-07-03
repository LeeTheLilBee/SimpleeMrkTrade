"""
Tests for VAULT GP078 — Real Storage Provider Owner Review Decision Receipt Lock Contract
"""

from pathlib import Path
import pytest

from vault.real_storage_provider_owner_review_decision_receipt_lock_contract_service import (
    DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,
    RECEIPT_POLICIES,
    RECEIPT_REQUIREMENT_SPECS,
    ensure_storage_provider_owner_review_decision_receipt_lock_contract_schema,
    get_gp078_status,
    get_real_storage_provider_owner_review_decision_receipt_lock_contract_home,
    get_storage_provider_owner_review_decision_receipt_blockers,
    get_storage_provider_owner_review_decision_receipt_events,
    get_storage_provider_owner_review_decision_receipt_lock_contract_record,
    get_storage_provider_owner_review_decision_receipt_next_step,
    get_storage_provider_owner_review_decision_receipt_policies,
    get_storage_provider_owner_review_decision_receipt_requirements,
    initialize_real_storage_provider_owner_review_decision_receipt_lock_contract,
    record_storage_provider_owner_review_decision_receipt_event,
    render_real_storage_provider_owner_review_decision_receipt_lock_contract_page,
    validate_storage_provider_owner_review_decision_receipt_lock_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_REQUIREMENTS = 63
EXPECTED_REQUIREMENTS = EXPECTED_SOURCE_REQUIREMENTS * len(RECEIPT_REQUIREMENT_SPECS)
EXPECTED_POLICIES = len(RECEIPT_POLICIES)
EXPECTED_BLOCKERS = 14

@pytest.fixture()
def gp078_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "owner_review_decision_receipt_lock_contract.sqlite")

def test_gp078_schema_is_real_sqlite_backed(gp078_db):
    result = ensure_storage_provider_owner_review_decision_receipt_lock_contract_schema(gp078_db)

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert Path(result["db_path"]).exists()
    assert "vault_storage_provider_owner_review_decision_receipt_lock_contracts" in result["tables"]
    assert "vault_storage_provider_owner_review_decision_receipt_requirements" in result["tables"]
    assert "vault_storage_provider_owner_review_decision_receipt_policies" in result["tables"]
    assert "vault_storage_provider_owner_review_decision_receipt_blockers" in result["tables"]
    assert "vault_storage_provider_owner_review_decision_receipt_events" in result["tables"]

def test_gp078_initialize_creates_real_contract_requirements_policies_blockers_events(gp078_db):
    result = initialize_real_storage_provider_owner_review_decision_receipt_lock_contract(gp078_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["contract_count"] == 1
    assert result["requirement_count"] == EXPECTED_REQUIREMENTS
    assert result["policy_count"] == EXPECTED_POLICIES
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_owner_review_decision_receipt_lock_contract(gp078_db)
    assert second["contract_count"] == 1
    assert second["requirement_count"] == EXPECTED_REQUIREMENTS
    assert second["policy_count"] == EXPECTED_POLICIES
    assert second["blocker_count"] == EXPECTED_BLOCKERS

def test_gp078_contract_sourced_from_gp077_and_locked(gp078_db):
    contract = get_storage_provider_owner_review_decision_receipt_lock_contract_record(gp078_db)["owner_review_decision_receipt_lock_contract"]

    assert contract["owner_review_decision_receipt_lock_contract_id"] == DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP078"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
    assert contract["section_range"] == "GP071-GP080"
    assert contract["source_owner_review_decision_lock_contract_id"] == "VSPORDLC-GP077-001"
    assert contract["source_owner_review_decision_pack_id"] == "VAULT_GP077"
    assert contract["contract_status"] == "REAL_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_OPEN_TEMPLATE_ONLY_TOWER_LOCKED"

    assert contract["owner_review_decision_receipt_lock_contract_ready"] is True
    assert contract["owner_review_decision_receipt_requirements_ready"] is True
    assert contract["owner_review_decision_receipt_policies_ready"] is True
    assert contract["owner_review_decision_receipt_blockers_ready"] is True
    assert contract["owner_review_decision_receipt_validation_ready"] is True
    assert contract["owner_review_decision_receipt_locked"] is True
    assert contract["receipt_template_only"] is True
    assert contract["receipt_redaction_required"] is True
    assert contract["source_owner_review_decision_lock_contract_attached"] is True
    assert contract["safe_to_continue_to_gp079"] is True

    locked_false_fields = [
        "owner_review_decision_receipt_created",
        "owner_review_decision_receipt_finalized",
        "provider_backed_decision_receipt_created",
        "decision_receipt_identity_hash_computed",
        "decision_receipt_reason_recorded",
        "decision_receipt_packet_created",
        "owner_decision_recorded",
        "owner_decision_approved",
        "owner_decision_denied",
        "owner_approval_granted",
        "owner_denial_recorded",
        "tower_unlock_granted",
        "provider_packet_attached",
        "object_identifier_attached",
        "object_body_attached",
        "decision_receipt_download_enabled",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
        "vault_done",
    ]
    for field in locked_false_fields:
        assert contract[field] is False

    assert contract["contract_data"]["safe_to_continue_to_gp079"] is True
    assert contract["contract_data"]["next_pack"] == "VAULT_GP079_REAL_STORAGE_PROVIDER_OWNER_REVIEW_CLOSEOUT_LOCK_CONTRACT"

def test_gp078_requirements_are_real_template_only_and_locked(gp078_db):
    payload = get_storage_provider_owner_review_decision_receipt_requirements(gp078_db)

    assert payload["requirement_count"] == EXPECTED_REQUIREMENTS
    assert payload["source_requirement_count"] == EXPECTED_SOURCE_REQUIREMENTS
    assert payload["requirement_code_count"] == len(RECEIPT_REQUIREMENT_SPECS)
    assert payload["requirement_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["requirement_verified_count"] == 0
    assert payload["receipt_locked_count"] == EXPECTED_REQUIREMENTS
    assert payload["template_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["receipt_redaction_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["tower_review_granted_count"] == 0

    assert payload["owner_review_decision_receipt_created_count"] == 0
    assert payload["owner_review_decision_receipt_finalized_count"] == 0
    assert payload["provider_backed_decision_receipt_created_count"] == 0
    assert payload["decision_receipt_identity_hash_computed_count"] == 0
    assert payload["decision_receipt_identity_hash_chained_count"] == 0
    assert payload["decision_receipt_reason_recorded_count"] == 0
    assert payload["decision_receipt_packet_created_count"] == 0
    assert payload["decision_receipt_packet_finalized_count"] == 0
    assert payload["owner_decision_recorded_count"] == 0
    assert payload["owner_decision_approved_count"] == 0
    assert payload["owner_decision_denied_count"] == 0
    assert payload["owner_approval_granted_count"] == 0
    assert payload["owner_denial_recorded_count"] == 0
    assert payload["tower_unlock_granted_count"] == 0
    assert payload["provider_packet_attached_count"] == 0
    assert payload["object_identifier_attached_count"] == 0
    assert payload["object_body_attached_count"] == 0
    assert payload["decision_receipt_download_enabled_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    for item in payload["requirements"]:
        assert item["owner_review_decision_receipt_requirement_id"].startswith("VSPORDRR-")
        assert item["owner_review_decision_receipt_lock_contract_id"] == DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID
        assert item["source_requirement_id"].startswith("VSPORDR-")
        assert item["receipt_locked"] is True
        assert item["template_only"] is True
        assert item["receipt_redaction_required"] is True
        assert item["owner_review_decision_receipt_created"] is False
        assert item["owner_review_decision_receipt_finalized"] is False
        assert item["decision_receipt_identity_hash_computed"] is False
        assert item["owner_decision_recorded"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp078_policies_are_real_template_only_and_locked(gp078_db):
    payload = get_storage_provider_owner_review_decision_receipt_policies(gp078_db)

    assert payload["policy_count"] == EXPECTED_POLICIES
    assert payload["policy_code_count"] == EXPECTED_POLICIES
    assert payload["policy_required_count"] == EXPECTED_POLICIES
    assert payload["policy_verified_count"] == 0
    assert payload["tower_review_granted_count"] == 0

    assert payload["owner_review_decision_receipt_created_count"] == 0
    assert payload["owner_review_decision_receipt_finalized_count"] == 0
    assert payload["provider_backed_decision_receipt_created_count"] == 0
    assert payload["decision_receipt_identity_hash_computed_count"] == 0
    assert payload["decision_receipt_reason_recorded_count"] == 0
    assert payload["decision_receipt_packet_created_count"] == 0
    assert payload["owner_decision_recorded_count"] == 0
    assert payload["owner_decision_approved_count"] == 0
    assert payload["owner_decision_denied_count"] == 0
    assert payload["owner_approval_granted_count"] == 0
    assert payload["tower_unlock_granted_count"] == 0
    assert payload["provider_packet_attached_count"] == 0
    assert payload["object_identifier_attached_count"] == 0
    assert payload["object_body_attached_count"] == 0
    assert payload["decision_receipt_download_enabled_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    for item in payload["policies"]:
        assert item["owner_review_decision_receipt_policy_id"].startswith("VSPORDRP-")
        assert item["owner_review_decision_receipt_lock_contract_id"] == DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID
        assert item["owner_review_decision_receipt_created"] is False
        assert item["owner_review_decision_receipt_finalized"] is False
        assert item["owner_decision_recorded"] is False
        assert item["tower_unlock_granted"] is False
        assert item["provider_packet_attached"] is False
        assert item["object_body_attached"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp078_blockers_are_real_and_carried_from_gp077(gp078_db):
    payload = get_storage_provider_owner_review_decision_receipt_blockers(gp078_db)

    assert payload["blocker_count"] == EXPECTED_BLOCKERS
    assert payload["blocker_active_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_owner_review_decision_receipt_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_backed_receipt_record_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_receipt_finalization_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_receipt_identity_hash_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_decision_receipt_reason_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_tower_unlock_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_packet_attachment_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_body_attachment_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_direct_upload_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_export_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_required_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_granted_count"] == 0
    assert payload["risk_accepted_count"] == 0
    assert payload["risk_waived_count"] == 0
    assert payload["mitigation_approved_count"] == 0
    assert payload["resolved_count"] == 0

    for item in payload["blockers"]:
        assert item["owner_review_decision_receipt_blocker_id"].startswith("VSPORDRB-")
        assert item["owner_review_decision_receipt_lock_contract_id"] == DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID
        assert item["source_owner_review_decision_blocker_id"].startswith("VSPORDB-")
        assert item["blocker_active"] is True
        assert item["blocks_owner_review_decision_receipt"] is True
        assert item["blocks_provider_backed_receipt_record"] is True
        assert item["blocks_receipt_finalization"] is True
        assert item["blocks_receipt_identity_hash"] is True
        assert item["blocks_tower_unlock"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["resolved"] is False

def test_gp078_event_log_and_manual_event_write_do_not_unlock(gp078_db):
    events = get_storage_provider_owner_review_decision_receipt_events(gp078_db)
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP077_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ATTACHED" in event_types
    assert "REAL_OWNER_REVIEW_DECISION_RECEIPT_REQUIREMENTS_CREATED_TEMPLATE_ONLY" in event_types
    assert "REAL_OWNER_REVIEW_DECISION_RECEIPT_POLICIES_CREATED_TEMPLATE_ONLY" in event_types
    assert "REAL_OWNER_REVIEW_DECISION_RECEIPT_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "OWNER_REVIEW_DECISION_RECEIPT_LOCKS_CONFIRMED" in event_types

    before = events["event_count"]
    written = record_storage_provider_owner_review_decision_receipt_event(
        "OWNER_GP078_DECISION_RECEIPT_REVIEWED",
        {"reviewer": "owner"},
        gp078_db,
    )
    after = get_storage_provider_owner_review_decision_receipt_events(gp078_db)

    assert after["event_count"] == before + 1
    assert written["event_written"] is True
    assert written["owner_review_decision_receipt_locked"] is True
    assert written["receipt_template_only"] is True
    assert written["owner_review_decision_receipt_created"] is False
    assert written["owner_review_decision_receipt_finalized"] is False
    assert written["provider_backed_decision_receipt_created"] is False
    assert written["decision_receipt_identity_hash_computed"] is False
    assert written["owner_decision_recorded"] is False
    assert written["owner_approval_granted"] is False
    assert written["tower_unlock_granted"] is False
    assert written["provider_packet_attached"] is False
    assert written["object_body_attached"] is False
    assert written["decision_receipt_download_enabled"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

def test_gp078_validation_home_status_and_next_step(gp078_db):
    validation = validate_storage_provider_owner_review_decision_receipt_lock_contract(gp078_db)

    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp079"] is True
    assert validation["vault_done"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP077_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ATTACHED" in codes
    assert "OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_READY" in codes
    assert "OWNER_REVIEW_DECISION_RECEIPT_LOCKED" in codes
    assert "RECEIPT_TEMPLATE_ONLY" in codes
    assert "REAL_OWNER_REVIEW_DECISION_RECEIPT_REQUIREMENTS_EXIST" in codes
    assert "REAL_OWNER_REVIEW_DECISION_RECEIPT_POLICIES_EXIST" in codes
    assert "REAL_OWNER_REVIEW_DECISION_RECEIPT_BLOCKERS_CARRIED_FORWARD" in codes
    assert "NO_CONTRACT_OWNER_REVIEW_DECISION_RECEIPT_CREATED" in codes
    assert "NO_CONTRACT_OWNER_REVIEW_DECISION_RECEIPT_FINALIZED" in codes
    assert "NO_CONTRACT_DECISION_RECEIPT_IDENTITY_HASH_COMPUTED" in codes
    assert "NO_CONTRACT_OWNER_DECISION_RECORDED" in codes
    assert "NO_CONTRACT_OWNER_APPROVAL_GRANTED" in codes
    assert "NO_CONTRACT_TOWER_UNLOCK_GRANTED" in codes
    assert "NO_CONTRACT_PROVIDER_PACKET_ATTACHED" in codes
    assert "NO_CONTRACT_OBJECT_BODY_ATTACHED" in codes
    assert "NO_CONTRACT_EXPORT_ENABLED" in codes
    assert "NO_CONTRACT_EXECUTION_ENABLED" in codes
    assert "NO_CONTRACT_VAULT_DONE" in codes

    home = get_real_storage_provider_owner_review_decision_receipt_lock_contract_home(gp078_db)
    truth = home["owner_review_decision_receipt_truth"]
    assert truth["real_storage_provider_owner_review_decision_receipt_lock_contract_ready"] is True
    assert truth["validation_passed"] is True
    assert truth["owner_review_decision_receipt_locked"] is True
    assert truth["receipt_template_only"] is True
    assert truth["requirement_count"] == EXPECTED_REQUIREMENTS
    assert truth["policy_count"] == EXPECTED_POLICIES
    assert truth["blocker_count"] == EXPECTED_BLOCKERS
    assert truth["owner_review_decision_receipt_created"] is False
    assert truth["owner_review_decision_receipt_finalized"] is False
    assert truth["provider_backed_decision_receipt_created"] is False
    assert truth["decision_receipt_identity_hash_computed"] is False
    assert truth["decision_receipt_reason_recorded"] is False
    assert truth["decision_receipt_packet_created"] is False
    assert truth["owner_decision_recorded"] is False
    assert truth["owner_decision_approved"] is False
    assert truth["owner_decision_denied"] is False
    assert truth["owner_approval_granted"] is False
    assert truth["tower_unlock_granted"] is False
    assert truth["provider_packet_attached"] is False
    assert truth["object_identifier_attached"] is False
    assert truth["object_body_attached"] is False
    assert truth["decision_receipt_download_enabled"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["export_enabled"] is False
    assert truth["execution_enabled"] is False
    assert truth["vault_done"] is False

    status = get_gp078_status(gp078_db)
    gp078 = status["gp078_status"]
    assert gp078["ready"] is True
    assert gp078["validation_passed"] is True
    assert gp078["safe_to_continue_to_gp079"] is True
    assert gp078["source_requirement_count"] == EXPECTED_SOURCE_REQUIREMENTS
    assert gp078["requirement_code_count"] == len(RECEIPT_REQUIREMENT_SPECS)
    assert gp078["policy_code_count"] == EXPECTED_POLICIES
    assert gp078["blocker_count"] == EXPECTED_BLOCKERS
    assert gp078["owner_review_decision_receipt_created_count"] == 0
    assert gp078["owner_review_decision_receipt_finalized_count"] == 0
    assert gp078["provider_backed_decision_receipt_created_count"] == 0
    assert gp078["decision_receipt_identity_hash_computed_count"] == 0
    assert gp078["decision_receipt_reason_recorded_count"] == 0
    assert gp078["owner_decision_recorded_count"] == 0
    assert gp078["owner_decision_approved_count"] == 0
    assert gp078["owner_decision_denied_count"] == 0
    assert gp078["tower_unlock_granted_count"] == 0
    assert gp078["provider_packet_attached_count"] == 0
    assert gp078["object_identifier_attached_count"] == 0
    assert gp078["object_body_attached_count"] == 0
    assert gp078["decision_receipt_download_enabled_count"] == 0
    assert gp078["direct_upload_enabled_count"] == 0
    assert gp078["export_enabled_count"] == 0
    assert gp078["execution_enabled_count"] == 0
    assert gp078["vault_done"] is False
    assert gp078["clouds_status"] == "parked_do_not_continue_from_vault_gp078"
    assert gp078["next_pack"] == "VAULT_GP079_REAL_STORAGE_PROVIDER_OWNER_REVIEW_CLOSEOUT_LOCK_CONTRACT"

    next_step = get_storage_provider_owner_review_decision_receipt_next_step()["next_step"]
    assert next_step["current_section_range"] == "GP071-GP080"
    assert next_step["next_pack"] == "VAULT_GP079_REAL_STORAGE_PROVIDER_OWNER_REVIEW_CLOSEOUT_LOCK_CONTRACT"
    assert next_step["safe_to_continue_to_gp079"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp078_html_is_dark_and_mentions_decision_receipt(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_storage_provider_owner_review_decision_receipt_lock_contract_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Owner Review Decision Receipt Lock Contract" in html
    assert "Real Provider Receipt and Redacted Access Layer" in html
    assert "GP078" in html
    assert "Decision receipt contract ready" in html
    assert "Template-only" in html
    assert "No receipt" in html
    assert "No finalization" in html
    assert "No receipt hash" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-owner-review-decision-receipt-lock-contract.json" in html
    assert "/vault/gp078-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp078_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-storage-provider-owner-review-decision-receipt-lock-contract",
        "/vault/real-storage-provider-owner-review-decision-receipt-lock-contract.json",
        "/vault/storage-provider-owner-review-decision-receipt-lock-contract-record.json",
        "/vault/storage-provider-owner-review-decision-receipt-requirements.json",
        "/vault/storage-provider-owner-review-decision-receipt-policies.json",
        "/vault/storage-provider-owner-review-decision-receipt-blockers.json",
        "/vault/storage-provider-owner-review-decision-receipt-events.json",
        "/vault/storage-provider-owner-review-decision-receipt-validation.json",
        "/vault/storage-provider-owner-review-decision-receipt-next-step.json",
        "/vault/gp078-status.json",
    ]
    for route in required_routes:
        assert route in text

def test_gp078_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
    envs = {
        "VAULT_STORAGE_PROVIDER_DECISION_DB": "routes_decision.sqlite",
        "VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB": "routes_selection.sqlite",
        "VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB": "routes_capability.sqlite",
        "VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB": "routes_validation.sqlite",
        "VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB": "routes_receipt.sqlite",
        "VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB": "routes_readiness.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB": "routes_config.sqlite",
        "VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB": "routes_credential.sqlite",
        "VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB": "routes_ledger.sqlite",
        "VAULT_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT_DB": "routes_endpoint.sqlite",
        "VAULT_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT_DB": "routes_encryption.sqlite",
        "VAULT_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT_DB": "routes_connection.sqlite",
        "VAULT_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT_DB": "routes_write.sqlite",
        "VAULT_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT_DB": "routes_read.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT_DB": "routes_obv.sqlite",
        "VAULT_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT_DB": "routes_gp070.sqlite",
        "VAULT_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT_DB": "routes_gp071.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_METADATA_RECEIPT_CONTRACT_DB": "routes_gp072.sqlite",
        "VAULT_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_CONTRACT_DB": "routes_gp073.sqlite",
        "VAULT_STORAGE_PROVIDER_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_DB": "routes_gp074.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_PACKET_LOCK_CONTRACT_DB": "routes_gp075.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_QUEUE_LOCK_CONTRACT_DB": "routes_gp076.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_LOCK_CONTRACT_DB": "routes_gp077.sqlite",
        "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_DB": "routes_gp078.sqlite",
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()
    routes = [
        "/vault/real-storage-provider-owner-review-decision-receipt-lock-contract",
        "/vault/real-storage-provider-owner-review-decision-receipt-lock-contract.json",
        "/vault/storage-provider-owner-review-decision-receipt-lock-contract-record.json",
        "/vault/storage-provider-owner-review-decision-receipt-requirements.json",
        "/vault/storage-provider-owner-review-decision-receipt-policies.json",
        "/vault/storage-provider-owner-review-decision-receipt-blockers.json",
        "/vault/storage-provider-owner-review-decision-receipt-events.json",
        "/vault/storage-provider-owner-review-decision-receipt-validation.json",
        "/vault/storage-provider-owner-review-decision-receipt-next-step.json",
        "/vault/gp078-status.json",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Real Storage Provider Owner Review Decision Receipt Lock Contract" in response.data
