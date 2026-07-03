"""
Tests for VAULT GP075 — Real Storage Provider Owner Review Packet Lock Contract
"""

from pathlib import Path
import pytest

from vault.real_storage_provider_owner_review_packet_lock_contract_service import (
    DEFAULT_OWNER_REVIEW_PACKET_LOCK_CONTRACT_ID,
    PACKET_POLICIES,
    PACKET_REQUIREMENT_SPECS,
    ensure_storage_provider_owner_review_packet_lock_contract_schema,
    get_gp075_status,
    get_real_storage_provider_owner_review_packet_lock_contract_home,
    get_storage_provider_owner_review_packet_blockers,
    get_storage_provider_owner_review_packet_events,
    get_storage_provider_owner_review_packet_lock_contract_record,
    get_storage_provider_owner_review_packet_next_step,
    get_storage_provider_owner_review_packet_policies,
    get_storage_provider_owner_review_packet_requirements,
    initialize_real_storage_provider_owner_review_packet_lock_contract,
    record_storage_provider_owner_review_packet_event,
    render_real_storage_provider_owner_review_packet_lock_contract_page,
    validate_storage_provider_owner_review_packet_lock_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_REQUIREMENTS = 63
EXPECTED_REQUIREMENTS = EXPECTED_SOURCE_REQUIREMENTS * len(PACKET_REQUIREMENT_SPECS)
EXPECTED_POLICIES = len(PACKET_POLICIES)
EXPECTED_BLOCKERS = 14

@pytest.fixture()
def gp075_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "owner_review_packet_lock_contract.sqlite")

def test_gp075_schema_is_real_sqlite_backed(gp075_db):
    result = ensure_storage_provider_owner_review_packet_lock_contract_schema(gp075_db)

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert Path(result["db_path"]).exists()
    assert "vault_storage_provider_owner_review_packet_lock_contracts" in result["tables"]
    assert "vault_storage_provider_owner_review_packet_requirements" in result["tables"]
    assert "vault_storage_provider_owner_review_packet_policies" in result["tables"]
    assert "vault_storage_provider_owner_review_packet_blockers" in result["tables"]
    assert "vault_storage_provider_owner_review_packet_events" in result["tables"]

def test_gp075_initialize_creates_real_contract_requirements_policies_blockers_events(gp075_db):
    result = initialize_real_storage_provider_owner_review_packet_lock_contract(gp075_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["contract_count"] == 1
    assert result["requirement_count"] == EXPECTED_REQUIREMENTS
    assert result["policy_count"] == EXPECTED_POLICIES
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_owner_review_packet_lock_contract(gp075_db)
    assert second["contract_count"] == 1
    assert second["requirement_count"] == EXPECTED_REQUIREMENTS
    assert second["policy_count"] == EXPECTED_POLICIES
    assert second["blocker_count"] == EXPECTED_BLOCKERS

def test_gp075_contract_sourced_from_gp074_and_locked(gp075_db):
    contract = get_storage_provider_owner_review_packet_lock_contract_record(gp075_db)["owner_review_packet_lock_contract"]

    assert contract["owner_review_packet_lock_contract_id"] == DEFAULT_OWNER_REVIEW_PACKET_LOCK_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP075"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
    assert contract["section_range"] == "GP071-GP080"
    assert contract["source_redacted_access_view_lock_contract_id"] == "VSPRAVLC-GP074-001"
    assert contract["source_redacted_access_view_pack_id"] == "VAULT_GP074"
    assert contract["contract_status"] == "REAL_OWNER_REVIEW_PACKET_LOCK_CONTRACT_OPEN_TEMPLATE_ONLY_TOWER_LOCKED"

    assert contract["owner_review_packet_lock_contract_ready"] is True
    assert contract["owner_review_packet_requirements_ready"] is True
    assert contract["owner_review_packet_policies_ready"] is True
    assert contract["owner_review_packet_blockers_ready"] is True
    assert contract["owner_review_packet_validation_ready"] is True
    assert contract["owner_review_packet_locked"] is True
    assert contract["packet_template_only"] is True
    assert contract["packet_redaction_required"] is True
    assert contract["source_redacted_access_view_lock_contract_attached"] is True
    assert contract["safe_to_continue_to_gp076"] is True

    locked_false_fields = [
        "owner_review_packet_created",
        "owner_review_packet_assembled",
        "owner_review_packet_published",
        "owner_review_packet_finalized",
        "provider_backed_packet_created",
        "provider_backed_packet_assembled",
        "owner_review_started",
        "owner_review_completed",
        "owner_approval_requested",
        "owner_approval_granted",
        "tower_unlock_requested",
        "tower_unlock_granted",
        "provider_access_view_attached",
        "provider_metadata_view_attached",
        "object_identifier_attached",
        "object_body_attached",
        "plaintext_packet_enabled",
        "packet_download_enabled",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
        "vault_done",
    ]
    for field in locked_false_fields:
        assert contract[field] is False

    assert contract["contract_data"]["safe_to_continue_to_gp076"] is True
    assert contract["contract_data"]["next_pack"] == "VAULT_GP076_REAL_STORAGE_PROVIDER_OWNER_REVIEW_QUEUE_LOCK_CONTRACT"

def test_gp075_requirements_are_real_template_only_and_locked(gp075_db):
    payload = get_storage_provider_owner_review_packet_requirements(gp075_db)

    assert payload["requirement_count"] == EXPECTED_REQUIREMENTS
    assert payload["source_requirement_count"] == EXPECTED_SOURCE_REQUIREMENTS
    assert payload["requirement_code_count"] == len(PACKET_REQUIREMENT_SPECS)
    assert payload["requirement_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["requirement_verified_count"] == 0
    assert payload["packet_locked_count"] == EXPECTED_REQUIREMENTS
    assert payload["template_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["packet_redaction_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["tower_review_granted_count"] == 0

    assert payload["owner_review_packet_created_count"] == 0
    assert payload["owner_review_packet_assembled_count"] == 0
    assert payload["owner_review_packet_published_count"] == 0
    assert payload["owner_review_packet_finalized_count"] == 0
    assert payload["provider_backed_packet_created_count"] == 0
    assert payload["provider_backed_packet_assembled_count"] == 0
    assert payload["owner_review_started_count"] == 0
    assert payload["owner_review_completed_count"] == 0
    assert payload["owner_approval_requested_count"] == 0
    assert payload["owner_approval_granted_count"] == 0
    assert payload["tower_unlock_requested_count"] == 0
    assert payload["tower_unlock_granted_count"] == 0
    assert payload["provider_access_view_attached_count"] == 0
    assert payload["provider_metadata_view_attached_count"] == 0
    assert payload["object_identifier_attached_count"] == 0
    assert payload["object_body_attached_count"] == 0
    assert payload["plaintext_packet_enabled_count"] == 0
    assert payload["packet_download_enabled_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    for item in payload["requirements"]:
        assert item["owner_review_packet_requirement_id"].startswith("VSPORPR-")
        assert item["owner_review_packet_lock_contract_id"] == DEFAULT_OWNER_REVIEW_PACKET_LOCK_CONTRACT_ID
        assert item["source_requirement_id"].startswith("VSPRAVR-")
        assert item["packet_locked"] is True
        assert item["template_only"] is True
        assert item["packet_redaction_required"] is True
        assert item["owner_review_packet_created"] is False
        assert item["provider_backed_packet_created"] is False
        assert item["owner_approval_granted"] is False
        assert item["tower_unlock_granted"] is False
        assert item["object_body_attached"] is False
        assert item["direct_upload_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp075_policies_are_real_template_only_and_locked(gp075_db):
    payload = get_storage_provider_owner_review_packet_policies(gp075_db)

    assert payload["policy_count"] == EXPECTED_POLICIES
    assert payload["policy_code_count"] == EXPECTED_POLICIES
    assert payload["policy_required_count"] == EXPECTED_POLICIES
    assert payload["policy_verified_count"] == 0
    assert payload["tower_review_granted_count"] == 0

    assert payload["owner_review_packet_created_count"] == 0
    assert payload["owner_review_packet_assembled_count"] == 0
    assert payload["owner_review_packet_published_count"] == 0
    assert payload["owner_review_packet_finalized_count"] == 0
    assert payload["provider_backed_packet_created_count"] == 0
    assert payload["provider_backed_packet_assembled_count"] == 0
    assert payload["owner_approval_requested_count"] == 0
    assert payload["owner_approval_granted_count"] == 0
    assert payload["tower_unlock_requested_count"] == 0
    assert payload["tower_unlock_granted_count"] == 0
    assert payload["provider_access_view_attached_count"] == 0
    assert payload["provider_metadata_view_attached_count"] == 0
    assert payload["object_identifier_attached_count"] == 0
    assert payload["object_key_attached_count"] == 0
    assert payload["object_body_attached_count"] == 0
    assert payload["plaintext_packet_enabled_count"] == 0
    assert payload["packet_download_enabled_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    for item in payload["policies"]:
        assert item["owner_review_packet_policy_id"].startswith("VSPORPP-")
        assert item["owner_review_packet_lock_contract_id"] == DEFAULT_OWNER_REVIEW_PACKET_LOCK_CONTRACT_ID
        assert item["owner_review_packet_created"] is False
        assert item["provider_backed_packet_created"] is False
        assert item["owner_approval_granted"] is False
        assert item["tower_unlock_granted"] is False
        assert item["object_body_attached"] is False
        assert item["packet_download_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp075_blockers_are_real_and_carried_from_gp074(gp075_db):
    payload = get_storage_provider_owner_review_packet_blockers(gp075_db)

    assert payload["blocker_count"] == EXPECTED_BLOCKERS
    assert payload["blocker_active_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_owner_review_packet_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_backed_packet_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_owner_approval_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_tower_unlock_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_view_attachment_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_identifier_attachment_count"] == EXPECTED_BLOCKERS
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
        assert item["owner_review_packet_blocker_id"].startswith("VSPORPB-")
        assert item["owner_review_packet_lock_contract_id"] == DEFAULT_OWNER_REVIEW_PACKET_LOCK_CONTRACT_ID
        assert item["source_redacted_access_view_blocker_id"].startswith("VSPRAVB-")
        assert item["blocker_active"] is True
        assert item["blocks_owner_review_packet"] is True
        assert item["blocks_provider_backed_packet"] is True
        assert item["blocks_owner_approval"] is True
        assert item["blocks_tower_unlock"] is True
        assert item["blocks_object_body_attachment"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["resolved"] is False

def test_gp075_event_log_and_manual_event_write_do_not_unlock(gp075_db):
    events = get_storage_provider_owner_review_packet_events(gp075_db)
    assert events["event_count"] >= 6

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_OWNER_REVIEW_PACKET_LOCK_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP074_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ATTACHED" in event_types
    assert "REAL_OWNER_REVIEW_PACKET_REQUIREMENTS_CREATED_TEMPLATE_ONLY" in event_types
    assert "REAL_OWNER_REVIEW_PACKET_POLICIES_CREATED_TEMPLATE_ONLY" in event_types
    assert "REAL_OWNER_REVIEW_PACKET_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "OWNER_REVIEW_PACKET_LOCKS_CONFIRMED" in event_types

    before = events["event_count"]
    written = record_storage_provider_owner_review_packet_event(
        "OWNER_GP075_PACKET_REVIEWED",
        {"reviewer": "owner"},
        gp075_db,
    )
    after = get_storage_provider_owner_review_packet_events(gp075_db)

    assert after["event_count"] == before + 1
    assert written["event_written"] is True
    assert written["owner_review_packet_locked"] is True
    assert written["packet_template_only"] is True
    assert written["owner_review_packet_created"] is False
    assert written["owner_review_packet_assembled"] is False
    assert written["provider_backed_packet_created"] is False
    assert written["owner_approval_granted"] is False
    assert written["tower_unlock_granted"] is False
    assert written["object_body_attached"] is False
    assert written["packet_download_enabled"] is False
    assert written["direct_upload_enabled"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

def test_gp075_validation_home_status_and_next_step(gp075_db):
    validation = validate_storage_provider_owner_review_packet_lock_contract(gp075_db)

    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp076"] is True
    assert validation["vault_done"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_OWNER_REVIEW_PACKET_LOCK_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP074_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ATTACHED" in codes
    assert "OWNER_REVIEW_PACKET_LOCK_CONTRACT_READY" in codes
    assert "OWNER_REVIEW_PACKET_LOCKED" in codes
    assert "PACKET_TEMPLATE_ONLY" in codes
    assert "REAL_OWNER_REVIEW_PACKET_REQUIREMENTS_EXIST" in codes
    assert "REAL_OWNER_REVIEW_PACKET_POLICIES_EXIST" in codes
    assert "REAL_OWNER_REVIEW_PACKET_BLOCKERS_CARRIED_FORWARD" in codes
    assert "NO_CONTRACT_OWNER_REVIEW_PACKET_CREATED" in codes
    assert "NO_CONTRACT_PROVIDER_BACKED_PACKET_CREATED" in codes
    assert "NO_CONTRACT_OWNER_APPROVAL_GRANTED" in codes
    assert "NO_CONTRACT_TOWER_UNLOCK_GRANTED" in codes
    assert "NO_CONTRACT_PROVIDER_ACCESS_VIEW_ATTACHED" in codes
    assert "NO_CONTRACT_OBJECT_BODY_ATTACHED" in codes
    assert "NO_CONTRACT_DIRECT_UPLOAD_ENABLED" in codes
    assert "NO_CONTRACT_EXPORT_ENABLED" in codes
    assert "NO_CONTRACT_EXECUTION_ENABLED" in codes
    assert "NO_CONTRACT_VAULT_DONE" in codes

    home = get_real_storage_provider_owner_review_packet_lock_contract_home(gp075_db)
    truth = home["owner_review_packet_truth"]
    assert truth["real_storage_provider_owner_review_packet_lock_contract_ready"] is True
    assert truth["validation_passed"] is True
    assert truth["owner_review_packet_locked"] is True
    assert truth["packet_template_only"] is True
    assert truth["requirement_count"] == EXPECTED_REQUIREMENTS
    assert truth["policy_count"] == EXPECTED_POLICIES
    assert truth["blocker_count"] == EXPECTED_BLOCKERS
    assert truth["owner_review_packet_created"] is False
    assert truth["owner_review_packet_assembled"] is False
    assert truth["provider_backed_packet_created"] is False
    assert truth["owner_approval_granted"] is False
    assert truth["tower_unlock_granted"] is False
    assert truth["provider_access_view_attached"] is False
    assert truth["object_identifier_attached"] is False
    assert truth["object_body_attached"] is False
    assert truth["packet_download_enabled"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["export_enabled"] is False
    assert truth["execution_enabled"] is False
    assert truth["vault_done"] is False

    status = get_gp075_status(gp075_db)
    gp075 = status["gp075_status"]
    assert gp075["ready"] is True
    assert gp075["validation_passed"] is True
    assert gp075["safe_to_continue_to_gp076"] is True
    assert gp075["source_requirement_count"] == EXPECTED_SOURCE_REQUIREMENTS
    assert gp075["requirement_code_count"] == len(PACKET_REQUIREMENT_SPECS)
    assert gp075["policy_code_count"] == EXPECTED_POLICIES
    assert gp075["blocker_count"] == EXPECTED_BLOCKERS
    assert gp075["owner_review_packet_created_count"] == 0
    assert gp075["owner_review_packet_assembled_count"] == 0
    assert gp075["provider_backed_packet_created_count"] == 0
    assert gp075["owner_approval_granted_count"] == 0
    assert gp075["tower_unlock_granted_count"] == 0
    assert gp075["provider_access_view_attached_count"] == 0
    assert gp075["provider_metadata_view_attached_count"] == 0
    assert gp075["object_identifier_attached_count"] == 0
    assert gp075["object_body_attached_count"] == 0
    assert gp075["packet_download_enabled_count"] == 0
    assert gp075["direct_upload_enabled_count"] == 0
    assert gp075["export_enabled_count"] == 0
    assert gp075["execution_enabled_count"] == 0
    assert gp075["vault_done"] is False
    assert gp075["clouds_status"] == "parked_do_not_continue_from_vault_gp075"
    assert gp075["next_pack"] == "VAULT_GP076_REAL_STORAGE_PROVIDER_OWNER_REVIEW_QUEUE_LOCK_CONTRACT"

    next_step = get_storage_provider_owner_review_packet_next_step()["next_step"]
    assert next_step["current_section_range"] == "GP071-GP080"
    assert next_step["next_pack"] == "VAULT_GP076_REAL_STORAGE_PROVIDER_OWNER_REVIEW_QUEUE_LOCK_CONTRACT"
    assert next_step["safe_to_continue_to_gp076"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp075_html_is_dark_and_mentions_owner_review_packet(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_storage_provider_owner_review_packet_lock_contract_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Owner Review Packet Lock Contract" in html
    assert "Real Provider Receipt and Redacted Access Layer" in html
    assert "GP075" in html
    assert "Owner packet contract ready" in html
    assert "Template-only" in html
    assert "No provider packet" in html
    assert "No owner approval" in html
    assert "No Tower unlock" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-owner-review-packet-lock-contract.json" in html
    assert "/vault/gp075-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp075_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-storage-provider-owner-review-packet-lock-contract",
        "/vault/real-storage-provider-owner-review-packet-lock-contract.json",
        "/vault/storage-provider-owner-review-packet-lock-contract-record.json",
        "/vault/storage-provider-owner-review-packet-requirements.json",
        "/vault/storage-provider-owner-review-packet-policies.json",
        "/vault/storage-provider-owner-review-packet-blockers.json",
        "/vault/storage-provider-owner-review-packet-events.json",
        "/vault/storage-provider-owner-review-packet-validation.json",
        "/vault/storage-provider-owner-review-packet-next-step.json",
        "/vault/gp075-status.json",
    ]
    for route in required_routes:
        assert route in text

def test_gp075_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()
    routes = [
        "/vault/real-storage-provider-owner-review-packet-lock-contract",
        "/vault/real-storage-provider-owner-review-packet-lock-contract.json",
        "/vault/storage-provider-owner-review-packet-lock-contract-record.json",
        "/vault/storage-provider-owner-review-packet-requirements.json",
        "/vault/storage-provider-owner-review-packet-policies.json",
        "/vault/storage-provider-owner-review-packet-blockers.json",
        "/vault/storage-provider-owner-review-packet-events.json",
        "/vault/storage-provider-owner-review-packet-validation.json",
        "/vault/storage-provider-owner-review-packet-next-step.json",
        "/vault/gp075-status.json",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Real Storage Provider Owner Review Packet Lock Contract" in response.data
