"""
Tests for VAULT GP069 — Real Storage Provider Object Body View Lock Contract
"""

from pathlib import Path
import pytest

from vault.real_storage_provider_object_body_view_lock_contract_service import (
    DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID,
    OBJECT_BODY_VIEW_POLICIES,
    OBJECT_BODY_VIEW_REQUIREMENT_SPECS,
    ensure_storage_provider_object_body_view_lock_contract_schema,
    get_gp069_status,
    get_real_storage_provider_object_body_view_lock_contract_home,
    get_storage_provider_object_body_view_blockers,
    get_storage_provider_object_body_view_events,
    get_storage_provider_object_body_view_lock_contract_record,
    get_storage_provider_object_body_view_next_step,
    get_storage_provider_object_body_view_policies,
    get_storage_provider_object_body_view_requirements,
    initialize_real_storage_provider_object_body_view_lock_contract,
    record_storage_provider_object_body_view_event,
    render_real_storage_provider_object_body_view_lock_contract_page,
    validate_storage_provider_object_body_view_lock_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROVIDER_CANDIDATES = 5
EXPECTED_REQUIREMENTS = EXPECTED_PROVIDER_CANDIDATES * len(OBJECT_BODY_VIEW_REQUIREMENT_SPECS)
EXPECTED_POLICIES = len(OBJECT_BODY_VIEW_POLICIES)
EXPECTED_BLOCKERS = 140

@pytest.fixture()
def obv_db(tmp_path, monkeypatch):
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
    }
    for key, name in envs.items():
        monkeypatch.setenv(key, str(tmp_path / name))
    return str(tmp_path / "object_body_view_lock_contract.sqlite")

def test_gp069_schema_is_real_sqlite_backed(obv_db):
    result = ensure_storage_provider_object_body_view_lock_contract_schema(obv_db)
    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert Path(result["db_path"]).exists()
    assert "vault_storage_provider_object_body_view_lock_contracts" in result["tables"]
    assert "vault_storage_provider_object_body_view_requirements" in result["tables"]
    assert "vault_storage_provider_object_body_view_policies" in result["tables"]
    assert "vault_storage_provider_object_body_view_blockers" in result["tables"]
    assert "vault_storage_provider_object_body_view_events" in result["tables"]

def test_gp069_initialize_creates_real_rows(obv_db):
    result = initialize_real_storage_provider_object_body_view_lock_contract(obv_db)
    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["contract_count"] == 1
    assert result["requirement_count"] == EXPECTED_REQUIREMENTS
    assert result["policy_count"] == EXPECTED_POLICIES
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 6

    second = initialize_real_storage_provider_object_body_view_lock_contract(obv_db)
    assert second["contract_count"] == 1
    assert second["requirement_count"] == EXPECTED_REQUIREMENTS
    assert second["policy_count"] == EXPECTED_POLICIES
    assert second["blocker_count"] == EXPECTED_BLOCKERS

def test_gp069_contract_is_sourced_from_gp068_and_locked(obv_db):
    contract = get_storage_provider_object_body_view_lock_contract_record(obv_db)["object_body_view_lock_contract"]
    assert contract["object_body_view_lock_contract_id"] == DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP069"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert contract["section_range"] == "GP061-GP070"
    assert contract["source_read_path_lock_contract_id"] == "VSPRPLC-GP068-001"
    assert contract["source_read_path_pack_id"] == "VAULT_GP068"
    assert contract["contract_status"] == "REAL_OBJECT_BODY_VIEW_LOCK_CONTRACT_OPEN_TOWER_LOCKED"
    assert contract["object_body_view_lock_contract_ready"] is True
    assert contract["object_body_view_requirements_ready"] is True
    assert contract["object_body_view_policy_ready"] is True
    assert contract["object_body_view_locked"] is True
    assert contract["object_body_metadata_only"] is True
    assert contract["object_body_redacted_view_only"] is True
    assert contract["object_body_view_configured"] is False
    assert contract["object_body_view_attempted"] is False
    assert contract["object_body_view_enabled"] is False
    assert contract["object_body_receipt_created"] is False
    assert contract["object_body_content_exposed"] is False
    assert contract["object_body_plaintext_visible"] is False
    assert contract["object_body_download_enabled"] is False
    assert contract["read_path_enabled"] is False
    assert contract["provider_read_enabled"] is False
    assert contract["provider_write_enabled"] is False
    assert contract["direct_upload_enabled"] is False
    assert contract["export_enabled"] is False
    assert contract["execution_enabled"] is False
    assert contract["vault_done"] is False
    assert contract["contract_data"]["safe_to_continue_to_gp070"] is True

def test_gp069_requirements_are_real_and_locked(obv_db):
    payload = get_storage_provider_object_body_view_requirements(obv_db)
    assert payload["requirement_count"] == EXPECTED_REQUIREMENTS
    assert payload["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert payload["requirement_code_count"] == len(OBJECT_BODY_VIEW_REQUIREMENT_SPECS)
    assert payload["requirement_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["requirement_verified_count"] == 0
    assert payload["object_body_view_locked_count"] == EXPECTED_REQUIREMENTS
    assert payload["object_body_metadata_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["object_body_redacted_view_only_count"] == EXPECTED_REQUIREMENTS
    assert payload["object_body_view_configured_count"] == 0
    assert payload["object_body_view_attempted_count"] == 0
    assert payload["object_body_view_enabled_count"] == 0
    assert payload["object_body_content_exposed_count"] == 0
    assert payload["object_body_plaintext_visible_count"] == 0
    assert payload["object_body_download_enabled_count"] == 0
    assert payload["provider_read_enabled_count"] == 0
    assert payload["provider_write_enabled_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0
    assert payload["tower_review_granted_count"] == 0
    for item in payload["requirements"]:
        assert item["object_body_view_requirement_id"].startswith("VSPOBVR-")
        assert item["object_body_view_lock_contract_id"] == DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["object_body_view_locked"] is True
        assert item["object_body_view_configured"] is False
        assert item["object_body_content_exposed"] is False
        assert item["object_body_plaintext_visible"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp069_policies_are_real_and_locked(obv_db):
    payload = get_storage_provider_object_body_view_policies(obv_db)
    assert payload["policy_count"] == EXPECTED_POLICIES
    assert payload["policy_code_count"] == EXPECTED_POLICIES
    assert payload["policy_required_count"] == EXPECTED_POLICIES
    assert payload["policy_verified_count"] == 0
    assert payload["object_body_view_configured_count"] == 0
    assert payload["object_body_view_attempted_count"] == 0
    assert payload["object_body_view_enabled_count"] == 0
    assert payload["object_body_content_exposed_count"] == 0
    assert payload["object_body_plaintext_visible_count"] == 0
    assert payload["object_body_download_enabled_count"] == 0
    assert payload["provider_read_enabled_count"] == 0
    assert payload["provider_write_enabled_count"] == 0
    assert payload["direct_upload_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0
    assert payload["tower_review_granted_count"] == 0
    for item in payload["policies"]:
        assert item["object_body_view_policy_id"].startswith("VSPOBVP-")
        assert item["object_body_view_lock_contract_id"] == DEFAULT_OBJECT_BODY_VIEW_LOCK_CONTRACT_ID
        assert item["object_body_view_configured"] is False
        assert item["object_body_content_exposed"] is False
        assert item["object_body_plaintext_visible"] is False
        assert item["object_body_download_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False

def test_gp069_blockers_are_real_and_carried_from_gp068(obv_db):
    payload = get_storage_provider_object_body_view_blockers(obv_db)
    assert payload["blocker_count"] == EXPECTED_BLOCKERS
    assert payload["capability_blocker_count"] == 60
    assert payload["criteria_blocker_count"] == 40
    assert payload["risk_blocker_count"] == 40
    assert payload["blocks_provider_configuration_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_read_write_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_body_view_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_export_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_granted_count"] == 0
    assert payload["resolved_count"] == 0
    for item in payload["blockers"]:
        assert item["object_body_view_blocker_id"].startswith("VSPOBVB-")
        assert item["source_read_path_blocker_id"].startswith("VSPRPB-")
        assert item["blocks_object_body_view"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["resolved"] is False

def test_gp069_event_log_and_manual_event_write_do_not_unlock_content(obv_db):
    before = get_storage_provider_object_body_view_events(obv_db)["event_count"]
    written = record_storage_provider_object_body_view_event(
        "OWNER_GP069_OBJECT_BODY_VIEW_LOCK_CONTRACT_OBSERVED",
        {"reviewer": "owner"},
        obv_db,
    )
    after = get_storage_provider_object_body_view_events(obv_db)
    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPOBVEVT-")
    assert after["event_count"] == before + 1
    assert written["object_body_view_configured"] is False
    assert written["object_body_view_attempted"] is False
    assert written["object_body_content_exposed"] is False
    assert written["object_body_plaintext_visible"] is False
    assert written["object_body_download_enabled"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

def test_gp069_validation_status_home_and_next_step(obv_db):
    validation = validate_storage_provider_object_body_view_lock_contract(obv_db)
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["safe_to_continue_to_gp070"] is True

    home = get_real_storage_provider_object_body_view_lock_contract_home(obv_db)
    assert home["pack"]["id"] == "VAULT_GP069"
    assert home["object_body_view_truth"]["real_storage_provider_object_body_view_lock_contract_ready"] is True
    assert home["object_body_view_truth"]["object_body_view_configured_count"] == 0
    assert home["object_body_view_truth"]["object_body_content_exposed_count"] == 0
    assert home["object_body_view_truth"]["object_body_plaintext_visible_count"] == 0
    assert home["object_body_view_truth"]["export_enabled"] is False
    assert home["object_body_view_truth"]["execution_enabled"] is False
    assert home["next_step"]["next_pack"] == "VAULT_GP070_REAL_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT"

    status = get_gp069_status(obv_db)
    gp069 = status["gp069_status"]
    assert gp069["ready"] is True
    assert gp069["validation_passed"] is True
    assert gp069["safe_to_continue_to_gp070"] is True
    assert gp069["vault_done"] is False
    assert gp069["clouds_status"] == "parked_do_not_continue_from_vault_gp069"

    next_step = get_storage_provider_object_body_view_next_step()["next_step"]
    assert next_step["next_pack"] == "VAULT_GP070_REAL_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT"
    assert next_step["safe_to_continue_to_gp070"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

def test_gp069_html_is_dark_and_mentions_object_body_view_lock_contract(monkeypatch, tmp_path):
    for key, name in {
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
    }.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    html = render_real_storage_provider_object_body_view_lock_contract_page()
    lowered = html.lower()
    assert "Vault Real Storage Provider Object Body View Lock Contract" in html
    assert "Real Storage Provider Configuration Layer" in html
    assert "GP069" in html
    assert "Object body view lock ready" in html
    assert "No object body view" in html
    assert "No plaintext" in html
    assert "No download" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-object-body-view-lock-contract.json" in html
    assert "/vault/gp069-status.json" in html
    for token in ["background: #fff", "background:#fff", "background-color: #fff", "background-color:#fff", "background: white", "background:white"]:
        assert token not in lowered

def test_gp069_routes_registered_in_web_app_text():
    text = (PROJECT_ROOT / "web" / "app.py").read_text(encoding="utf-8", errors="ignore")
    required_routes = [
        "/vault/real-storage-provider-object-body-view-lock-contract",
        "/vault/real-storage-provider-object-body-view-lock-contract.json",
        "/vault/storage-provider-object-body-view-lock-contract-record.json",
        "/vault/storage-provider-object-body-view-requirements.json",
        "/vault/storage-provider-object-body-view-policies.json",
        "/vault/storage-provider-object-body-view-blockers.json",
        "/vault/storage-provider-object-body-view-events.json",
        "/vault/storage-provider-object-body-view-validation.json",
        "/vault/storage-provider-object-body-view-next-step.json",
        "/vault/gp069-status.json",
    ]
    for route in required_routes:
        assert route in text

def test_gp069_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
    for key, name in {
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
    }.items():
        monkeypatch.setenv(key, str(tmp_path / name))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()
    routes = [
        "/vault/real-storage-provider-object-body-view-lock-contract",
        "/vault/real-storage-provider-object-body-view-lock-contract.json",
        "/vault/storage-provider-object-body-view-lock-contract-record.json",
        "/vault/storage-provider-object-body-view-requirements.json",
        "/vault/storage-provider-object-body-view-policies.json",
        "/vault/storage-provider-object-body-view-blockers.json",
        "/vault/storage-provider-object-body-view-events.json",
        "/vault/storage-provider-object-body-view-validation.json",
        "/vault/storage-provider-object-body-view-next-step.json",
        "/vault/gp069-status.json",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Real Storage Provider Object Body View Lock Contract" in response.data
