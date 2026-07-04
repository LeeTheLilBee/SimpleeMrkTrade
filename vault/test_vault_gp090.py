"""
Tests for VAULT GP090 — Real Provider Restore and Export Governance Readiness Checkpoint
"""

from pathlib import Path
import pytest

from vault.real_provider_restore_and_export_governance_readiness_checkpoint_service import (
    DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID,
    READINESS_CRITERIA,
    ensure_restore_export_governance_readiness_schema,
    get_gp090_status,
    get_real_provider_restore_export_governance_readiness_home,
    get_restore_export_governance_blockers,
    get_restore_export_governance_components,
    get_restore_export_governance_criteria,
    get_restore_export_governance_events,
    get_restore_export_governance_next_section,
    get_restore_export_governance_readiness_checkpoint_record,
    initialize_real_provider_restore_export_governance_readiness_checkpoint,
    render_real_provider_restore_export_governance_readiness_checkpoint_page,
    validate_restore_export_governance_readiness_checkpoint,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture()
def gp090_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "restore_export_governance_readiness.sqlite")

def test_gp090_schema_and_initialize_are_real_sqlite_backed(gp090_db):
    schema = ensure_restore_export_governance_readiness_schema(gp090_db)
    assert schema["schema_ready"] is True
    assert schema["real_sqlite_backed"] is True
    assert Path(schema["db_path"]).exists()
    assert "vault_restore_export_governance_readiness_checkpoints" in schema["tables"]
    assert "vault_restore_export_governance_components" in schema["tables"]
    assert "vault_restore_export_governance_criteria" in schema["tables"]
    assert "vault_restore_export_governance_blockers" in schema["tables"]
    assert "vault_restore_export_governance_events" in schema["tables"]

    result = initialize_real_provider_restore_export_governance_readiness_checkpoint(gp090_db)
    assert result["initialized"] is True
    assert result["checkpoint_count"] == 1
    assert result["component_count"] == 9
    assert result["criteria_count"] == len(READINESS_CRITERIA)
    assert result["blocker_count"] == 0
    assert result["event_count"] >= 6

def test_gp090_checkpoint_closes_section_but_not_vault(gp090_db):
    checkpoint = get_restore_export_governance_readiness_checkpoint_record(gp090_db)["checkpoint"]

    assert checkpoint["checkpoint_id"] == DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID
    assert checkpoint["pack_id"] == "VAULT_GP090"
    assert checkpoint["section_id"] == "ARCHIVE_VAULT_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_LAYER"
    assert checkpoint["section_range"] == "GP081-GP090"
    assert checkpoint["checkpoint_status"] == "RESTORE_EXPORT_GOVERNANCE_SECTION_CLOSED_READY_FOR_NEXT_SECTION"
    assert checkpoint["readiness_score"] == 100
    assert len(checkpoint["readiness_hash"]) == 64
    assert checkpoint["component_count"] == 9
    assert checkpoint["criteria_count"] == len(READINESS_CRITERIA)
    assert checkpoint["failed_criteria_count"] == 0
    assert checkpoint["active_blocker_count"] == 0

    assert checkpoint["real_sqlite_backed"] is True
    assert checkpoint["section_closeout_ready"] is True
    assert checkpoint["section_closed"] is True
    assert checkpoint["restore_export_governance_ready"] is True
    assert checkpoint["safe_to_continue_to_gp091"] is True
    assert checkpoint["restore_execution_locked"] is True
    assert checkpoint["restore_export_locked"] is True
    assert checkpoint["provider_restore_api_locked"] is True
    assert checkpoint["object_body_access_locked"] is True
    assert checkpoint["direct_upload_locked"] is True
    assert checkpoint["export_locked"] is True
    assert checkpoint["execution_locked"] is True
    assert checkpoint["vault_done"] is False
    assert checkpoint["clouds_should_continue"] is False

    assert checkpoint["next_pack"] == "VAULT_GP091_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT"

def test_gp090_components_criteria_blockers_events(gp090_db):
    components = get_restore_export_governance_components(gp090_db)
    assert components["component_count"] == 9
    assert components["components_ready_count"] == 9
    assert components["components_safe_to_continue_count"] == 9
    assert components["components_locked_count"] == 9
    assert [item["component_id"] for item in components["components"]] == [
        "VAULT_GP081",
        "VAULT_GP082",
        "VAULT_GP083",
        "VAULT_GP084",
        "VAULT_GP085",
        "VAULT_GP086",
        "VAULT_GP087",
        "VAULT_GP088",
        "VAULT_GP089",
    ]

    criteria = get_restore_export_governance_criteria(gp090_db)
    assert criteria["criteria_count"] == len(READINESS_CRITERIA)
    assert criteria["failed_criteria_count"] == 0
    assert criteria["passed_criteria_count"] == len(READINESS_CRITERIA)
    assert all(item["passed"] for item in criteria["criteria"])

    blockers = get_restore_export_governance_blockers(gp090_db)
    assert blockers["blocker_count"] == 0
    assert blockers["active_blocker_count"] == 0

    events = get_restore_export_governance_events(gp090_db)
    assert events["event_count"] >= 6
    event_types = {event["event_type"] for event in events["events"]}
    assert "RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_CREATED" in event_types
    assert "RESTORE_EXPORT_GOVERNANCE_COMPONENTS_SNAPSHOTTED" in event_types
    assert "RESTORE_EXPORT_GOVERNANCE_CRITERIA_EVALUATED" in event_types
    assert "RESTORE_EXPORT_GOVERNANCE_LOCKS_CONFIRMED" in event_types
    assert "RESTORE_EXPORT_GOVERNANCE_READINESS_HASH_RECORDED" in event_types
    assert "RESTORE_EXPORT_GOVERNANCE_NEXT_SECTION_HANDOFF_READY" in event_types

def test_gp090_validation_home_status_next_section(gp090_db):
    validation = validate_restore_export_governance_readiness_checkpoint(gp090_db)
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["readiness_score"] == 100
    assert len(validation["readiness_hash"]) == 64
    assert validation["safe_to_continue_to_gp091"] is True
    assert validation["vault_done"] is False

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_READINESS_CHECKPOINT_EXISTS" in codes
    assert "SECTION_GP081_GP090" in codes
    assert "READINESS_SCORE_100" in codes
    assert "READINESS_HASH_MATCHES" in codes
    assert "COMPONENT_COUNT_9" in codes
    assert "ALL_COMPONENTS_SAFE_TO_CONTINUE" in codes
    assert "NO_ACTIVE_BLOCKERS" in codes
    assert "SECTION_CLOSED" in codes
    assert "PROVIDER_RESTORE_API_LOCKED" in codes
    assert "OBJECT_BODY_ACCESS_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "EXPORT_LOCKED" in codes
    assert "EXECUTION_LOCKED" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "SAFE_TO_CONTINUE_TO_GP091" in codes

    home = get_real_provider_restore_export_governance_readiness_home(gp090_db)
    truth = home["readiness_truth"]
    assert truth["real_provider_restore_export_governance_readiness_checkpoint_ready"] is True
    assert truth["readiness_score"] == 100
    assert truth["section_closed"] is True
    assert truth["active_blocker_count"] == 0
    assert truth["restore_execution_locked"] is True
    assert truth["restore_export_locked"] is True
    assert truth["provider_restore_api_locked"] is True
    assert truth["object_body_access_locked"] is True
    assert truth["direct_upload_locked"] is True
    assert truth["export_locked"] is True
    assert truth["execution_locked"] is True
    assert truth["safe_to_continue_to_gp091"] is True
    assert truth["vault_done"] is False
    assert truth["clouds_should_continue"] is False

    status = get_gp090_status(gp090_db)
    gp090 = status["gp090_status"]
    assert gp090["ready"] is True
    assert gp090["section_closed"] is True
    assert gp090["readiness_score"] == 100
    assert gp090["validation_passed"] is True
    assert gp090["safe_to_continue_to_gp091"] is True
    assert gp090["vault_done"] is False
    assert gp090["clouds_status"] == "parked_do_not_continue_from_vault_gp090"
    assert gp090["next_pack"] == "VAULT_GP091_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT"

    next_section = get_restore_export_governance_next_section()["next_section"]
    assert next_section["section_closed"] is True
    assert next_section["next_section_range"] == "GP091-GP100"
    assert next_section["next_pack"] == "VAULT_GP091_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT"
    assert next_section["safe_to_continue_to_gp091"] is True
    assert next_section["vault_done"] is False
    assert next_section["clouds_should_continue"] is False

def test_gp090_html_is_dark_and_mentions_closeout(monkeypatch, tmp_path):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_provider_restore_export_governance_readiness_checkpoint_page()
    lowered = html.lower()

    assert "Vault Restore/Export Governance Readiness Checkpoint" in html
    assert "GP090" in html
    assert "Section closed" in html
    assert "Readiness hash recorded" in html
    assert "Vault not done" in html
    assert "No provider API" in html
    assert "No body read" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-provider-restore-export-governance-readiness-checkpoint.json" in html
    assert "/vault/gp090-status.json" in html

    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp090_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-provider-restore-export-governance-readiness-checkpoint",
        "/vault/real-provider-restore-export-governance-readiness-checkpoint.json",
        "/vault/restore-export-governance-readiness-checkpoint-record.json",
        "/vault/restore-export-governance-components.json",
        "/vault/restore-export-governance-criteria.json",
        "/vault/restore-export-governance-blockers.json",
        "/vault/restore-export-governance-events.json",
        "/vault/restore-export-governance-validation.json",
        "/vault/restore-export-governance-next-section.json",
        "/vault/gp090-status.json",
    ]
    for route in required_routes:
        assert route in text
