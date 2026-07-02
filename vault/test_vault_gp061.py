"""
Tests for VAULT GIANT PACK 061 — Real Storage Provider Config Contract
"""

from pathlib import Path

import pytest

from vault.real_storage_provider_config_contract_service import (
    CONFIG_REQUIREMENTS,
    DEFAULT_CONFIG_CONTRACT_ID,
    ensure_storage_provider_config_contract_schema,
    get_gp061_status,
    get_real_storage_provider_config_contract_home,
    get_storage_provider_config_blockers,
    get_storage_provider_config_contract_record,
    get_storage_provider_config_events,
    get_storage_provider_config_next_step,
    get_storage_provider_config_requirements,
    initialize_real_storage_provider_config_contract,
    record_storage_provider_config_event,
    render_real_storage_provider_config_contract_page,
    validate_storage_provider_config_contract,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROVIDER_CANDIDATES = 5
EXPECTED_REQUIREMENTS = EXPECTED_PROVIDER_CANDIDATES * len(CONFIG_REQUIREMENTS)
EXPECTED_BLOCKERS = 140


@pytest.fixture()
def config_db(tmp_path, monkeypatch):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "selection_registry.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "capability_contract.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "risk_criteria_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "selection_review_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "prep_readiness.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB", str(tmp_path / "config_contract.sqlite"))
    return str(tmp_path / "config_contract.sqlite")


def test_gp061_schema_is_real_sqlite_backed(config_db):
    result = ensure_storage_provider_config_contract_schema(config_db)
    db_path = Path(result["db_path"])

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert db_path.exists()
    assert "vault_storage_provider_config_contracts" in result["tables"]
    assert "vault_storage_provider_config_requirements" in result["tables"]
    assert "vault_storage_provider_config_blockers" in result["tables"]
    assert "vault_storage_provider_config_events" in result["tables"]


def test_gp061_initialize_creates_real_contract_requirements_blockers_events(config_db):
    result = initialize_real_storage_provider_config_contract(config_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["config_contract_id"] == DEFAULT_CONFIG_CONTRACT_ID
    assert result["contract_count"] == 1
    assert result["requirement_count"] == EXPECTED_REQUIREMENTS
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 5

    second = initialize_real_storage_provider_config_contract(config_db)
    assert second["contract_count"] == 1
    assert second["requirement_count"] == EXPECTED_REQUIREMENTS
    assert second["blocker_count"] == EXPECTED_BLOCKERS
    assert second["event_count"] >= 5


def test_gp061_contract_record_is_real_and_sourced_from_gp060(config_db):
    contract = get_storage_provider_config_contract_record(config_db)["contract"]

    assert contract["config_contract_id"] == DEFAULT_CONFIG_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP061"
    assert contract["section_id"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert contract["section_range"] == "GP061-GP070"
    assert contract["source_readiness_checkpoint_id"] == "VSPPRC-GP060-001"
    assert contract["source_readiness_pack_id"] == "VAULT_GP060"
    assert contract["contract_status"] == "REAL_STORAGE_PROVIDER_CONFIG_CONTRACT_OPEN_TOWER_LOCKED"
    assert contract["tower_authority_status"] == "TOWER_REVIEW_REQUIRED_NOT_GRANTED"

    data = contract["contract_data"]
    assert data["contract_type"] == "REAL_STORAGE_PROVIDER_CONFIG_CONTRACT"
    assert data["real_durable_config_contract"] is True
    assert data["metadata_source"] == "VAULT_GP060_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT"
    assert data["source_readiness_checkpoint_id"] == "VSPPRC-GP060-001"
    assert data["source_readiness_pack_id"] == "VAULT_GP060"
    assert data["previous_section"]["section_range"] == "GP051-GP060"
    assert data["previous_section"]["closed"] is True
    assert data["current_section"]["section_range"] == "GP061-GP070"
    assert data["current_section"]["started"] is True
    assert data["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert data["config_requirement_code_count"] == len(CONFIG_REQUIREMENTS)
    assert data["config_requirement_count"] == EXPECTED_REQUIREMENTS
    assert data["carried_blocker_count"] == EXPECTED_BLOCKERS
    assert data["safe_to_continue_to_gp062"] is True


def test_gp061_contract_keeps_all_config_and_provider_operations_locked(config_db):
    contract = get_storage_provider_config_contract_record(config_db)["contract"]

    assert contract["config_contract_ready"] is True
    assert contract["provider_approval_ready"] is False
    assert contract["provider_activation_ready"] is False
    assert contract["provider_configuration_ready"] is False
    assert contract["provider_read_write_ready"] is False
    assert contract["provider_approved"] is False
    assert contract["provider_activated"] is False
    assert contract["provider_recommended"] is False
    assert contract["provider_selected"] is False
    assert contract["provider_configured"] is False
    assert contract["credentials_configured"] is False
    assert contract["provider_endpoint_configured"] is False
    assert contract["storage_container_configured"] is False
    assert contract["encryption_configured"] is False
    assert contract["provider_read_enabled"] is False
    assert contract["provider_write_enabled"] is False
    assert contract["provider_object_read_claimed"] is False
    assert contract["provider_connection_tested"] is False
    assert contract["risk_accepted"] is False
    assert contract["risk_waived"] is False
    assert contract["mitigation_approved"] is False
    assert contract["official_storage_receipt"] is False
    assert contract["finalized_storage_receipt"] is False
    assert contract["closed_storage_receipt"] is False
    assert contract["object_body_view_enabled"] is False
    assert contract["direct_upload_enabled"] is False
    assert contract["export_enabled"] is False
    assert contract["execution_enabled"] is False
    assert contract["vault_done"] is False


def test_gp061_config_requirements_are_real_and_locked(config_db):
    payload = get_storage_provider_config_requirements(config_db)

    assert payload["pack"]["id"] == "VAULT_GP061"
    assert payload["real_sqlite_backed"] is True
    assert payload["requirement_count"] == EXPECTED_REQUIREMENTS
    assert payload["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert payload["requirement_code_count"] == len(CONFIG_REQUIREMENTS)
    assert payload["required_for_configuration_count"] == EXPECTED_REQUIREMENTS
    assert payload["config_value_present_count"] == 0
    assert payload["secret_value_present_count"] == 0
    assert payload["config_verified_count"] == 0
    assert payload["tower_review_required_count"] == EXPECTED_REQUIREMENTS
    assert payload["tower_review_granted_count"] == 0
    assert payload["provider_configured_count"] == 0
    assert payload["provider_read_enabled_count"] == 0
    assert payload["provider_write_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    codes = {item["requirement_code"] for item in payload["requirements"]}
    expected_codes = {item["requirement_code"] for item in CONFIG_REQUIREMENTS}
    assert codes == expected_codes

    categories = {item["requirement_category"] for item in payload["requirements"]}
    assert "credentials" in categories
    assert "endpoint" in categories
    assert "namespace" in categories
    assert "encryption" in categories
    assert "tower_gate" in categories

    for item in payload["requirements"]:
        assert item["config_requirement_id"].startswith("VSPCFGREQ-")
        assert item["config_contract_id"] == DEFAULT_CONFIG_CONTRACT_ID
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["requirement_status"] == "REAL_CONFIG_REQUIREMENT_RECORDED_NOT_CONFIGURED_TOWER_LOCKED"
        assert item["required_for_configuration"] is True
        assert item["config_value_present"] is False
        assert item["secret_value_present"] is False
        assert item["config_verified"] is False
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False
        assert item["provider_configured"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False


def test_gp061_config_blockers_are_real_and_carried_from_gp060(config_db):
    payload = get_storage_provider_config_blockers(config_db)

    assert payload["pack"]["id"] == "VAULT_GP061"
    assert payload["real_sqlite_backed"] is True
    assert payload["blocker_count"] == EXPECTED_BLOCKERS
    assert payload["capability_blocker_count"] == 60
    assert payload["criteria_blocker_count"] == 40
    assert payload["risk_blocker_count"] == 40

    assert payload["blocks_provider_approval_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_activation_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_selection_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_configuration_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_provider_read_write_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_object_body_view_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_export_count"] == EXPECTED_BLOCKERS
    assert payload["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_required_count"] == EXPECTED_BLOCKERS
    assert payload["tower_review_granted_count"] == 0
    assert payload["risk_accepted_count"] == 0
    assert payload["risk_waived_count"] == 0
    assert payload["mitigation_approved_count"] == 0
    assert payload["resolved_count"] == 0

    categories = {item["blocker_category"] for item in payload["blockers"]}
    assert categories == {"capability_contract", "criteria_validation", "risk_validation"}

    for item in payload["blockers"]:
        assert item["config_blocker_id"].startswith("VSPCFGB-")
        assert item["config_contract_id"] == DEFAULT_CONFIG_CONTRACT_ID
        assert item["source_readiness_blocker_id"].startswith("VSPPB-")
        assert item["source_receipt_line_id"].startswith("VSPRL-")
        assert item["source_finding_id"].startswith("VSPRCF-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["blocker_status"] == "REAL_CONFIG_CONTRACT_BLOCKER_ACTIVE_CARRIED_FROM_GP060"
        assert item["blocks_provider_approval"] is True
        assert item["blocks_provider_activation"] is True
        assert item["blocks_provider_selection"] is True
        assert item["blocks_provider_configuration"] is True
        assert item["blocks_provider_read_write"] is True
        assert item["blocks_object_body_view"] is True
        assert item["blocks_export"] is True
        assert item["blocks_execution"] is True
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False
        assert item["risk_accepted"] is False
        assert item["risk_waived"] is False
        assert item["mitigation_approved"] is False
        assert item["resolved"] is False


def test_gp061_event_log_is_real_and_seeded(config_db):
    events = get_storage_provider_config_events(config_db)

    assert events["pack"]["id"] == "VAULT_GP061"
    assert events["real_sqlite_backed"] is True
    assert events["event_count"] >= 5

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_CONFIG_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP060_READINESS_CHECKPOINT_ATTACHED" in event_types
    assert "REAL_CONFIG_REQUIREMENTS_CREATED" in event_types
    assert "REAL_CONFIG_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "CONFIG_CONTRACT_LOCKS_CONFIRMED" in event_types

    for event in events["events"]:
        assert event["event_id"].startswith("VSPCFGE-")
        assert event["config_contract_id"] == DEFAULT_CONFIG_CONTRACT_ID
        assert isinstance(event["event_payload"], dict)
        assert event["created_at"]


def test_gp061_can_write_real_event_without_configuring_provider(config_db):
    before = get_storage_provider_config_events(config_db)["event_count"]

    written = record_storage_provider_config_event(
        "OWNER_GP061_CONFIG_CONTRACT_OBSERVED",
        {"reviewer": "owner", "note": "reviewed real GP061 config contract"},
        config_db,
    )

    after = get_storage_provider_config_events(config_db)
    contract = get_storage_provider_config_contract_record(config_db)["contract"]
    requirements = get_storage_provider_config_requirements(config_db)
    blockers = get_storage_provider_config_blockers(config_db)

    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPCFGE-")
    assert written["config_contract_id"] == DEFAULT_CONFIG_CONTRACT_ID
    assert written["real_sqlite_backed"] is True
    assert written["config_contract_ready"] is True
    assert written["provider_configuration_ready"] is False
    assert written["provider_configured"] is False
    assert written["credentials_configured"] is False
    assert written["provider_endpoint_configured"] is False
    assert written["storage_container_configured"] is False
    assert written["encryption_configured"] is False
    assert written["provider_read_enabled"] is False
    assert written["provider_write_enabled"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

    assert after["event_count"] == before + 1
    assert "OWNER_GP061_CONFIG_CONTRACT_OBSERVED" in {event["event_type"] for event in after["events"]}

    assert contract["provider_configured"] is False
    assert contract["credentials_configured"] is False
    assert contract["provider_endpoint_configured"] is False
    assert contract["provider_read_enabled"] is False
    assert contract["provider_write_enabled"] is False
    assert contract["vault_done"] is False

    assert requirements["config_value_present_count"] == 0
    assert requirements["secret_value_present_count"] == 0
    assert blockers["resolved_count"] == 0
    assert blockers["blocks_execution_count"] == EXPECTED_BLOCKERS


def test_gp061_validation_passes_real_locked_config_contract(config_db):
    validation = validate_storage_provider_config_contract(config_db)

    assert validation["pack"]["id"] == "VAULT_GP061"
    assert validation["validation_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["passed_count"] == validation["check_count"]
    assert validation["real_sqlite_backed"] is True
    assert validation["safe_to_continue_to_gp062"] is True

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_CONFIG_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP060_READINESS_CHECKPOINT_ATTACHED" in codes
    assert "CONFIG_CONTRACT_READY" in codes
    assert "NEW_CONFIG_SECTION_STARTED" in codes
    assert "REAL_CONFIG_REQUIREMENT_ROWS_EXIST" in codes
    assert "NO_CONFIG_VALUES_PRESENT" in codes
    assert "NO_SECRET_VALUES_PRESENT" in codes
    assert "NO_CONFIG_REQUIREMENTS_VERIFIED" in codes
    assert "REAL_CONFIG_BLOCKERS_CARRIED_FORWARD" in codes
    assert "ALL_BLOCKERS_BLOCK_PROVIDER_CONFIGURATION" in codes
    assert "ALL_BLOCKERS_BLOCK_EXPORT" in codes
    assert "ALL_BLOCKERS_BLOCK_EXECUTION" in codes
    assert "NO_PROVIDER_CONFIGURATION_READY" in codes
    assert "NO_PROVIDER_CONFIGURED" in codes
    assert "NO_CREDENTIALS_CONFIGURED" in codes
    assert "NO_ENDPOINT_CONFIGURED" in codes
    assert "NO_STORAGE_CONTAINER_CONFIGURED" in codes
    assert "NO_ENCRYPTION_CONFIGURED" in codes
    assert "NO_PROVIDER_READ_ENABLED" in codes
    assert "NO_PROVIDER_WRITE_ENABLED" in codes
    assert "NO_EXPORT" in codes
    assert "NO_EXECUTION" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "EVENT_LOG_EXISTS" in codes


def test_gp061_home_payload_has_truth_routes_and_next_step(config_db):
    home = get_real_storage_provider_config_contract_home(config_db)

    assert home["pack"]["id"] == "VAULT_GP061"
    assert home["config_truth"]["real_storage_provider_config_contract_ready"] is True
    assert home["config_truth"]["real_sqlite_backed"] is True
    assert home["config_truth"]["real_schema_ready"] is True
    assert home["config_truth"]["real_config_contract_exists"] is True
    assert home["config_truth"]["real_config_requirement_rows_exist"] is True
    assert home["config_truth"]["real_config_blocker_rows_exist"] is True
    assert home["config_truth"]["real_event_log_exists"] is True
    assert home["config_truth"]["source_gp060_readiness_checkpoint_attached"] is True
    assert home["config_truth"]["validation_passed"] is True
    assert home["config_truth"]["config_contract_ready"] is True
    assert home["config_truth"]["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert home["config_truth"]["requirement_count"] == EXPECTED_REQUIREMENTS
    assert home["config_truth"]["blocker_count"] == EXPECTED_BLOCKERS
    assert home["config_truth"]["config_value_present_count"] == 0
    assert home["config_truth"]["secret_value_present_count"] == 0
    assert home["config_truth"]["config_verified_count"] == 0
    assert home["config_truth"]["provider_configuration_ready"] is False
    assert home["config_truth"]["provider_configured"] is False
    assert home["config_truth"]["credentials_configured"] is False
    assert home["config_truth"]["provider_endpoint_configured"] is False
    assert home["config_truth"]["storage_container_configured"] is False
    assert home["config_truth"]["encryption_configured"] is False
    assert home["config_truth"]["export_enabled"] is False
    assert home["config_truth"]["execution_enabled"] is False
    assert home["config_truth"]["vault_done"] is False

    routes = home["routes"]
    assert routes["route"] == "/vault/real-storage-provider-config-contract"
    assert routes["json_route"] == "/vault/real-storage-provider-config-contract.json"
    assert routes["record_route"] == "/vault/storage-provider-config-contract-record.json"
    assert routes["requirements_route"] == "/vault/storage-provider-config-requirements.json"
    assert routes["blockers_route"] == "/vault/storage-provider-config-blockers.json"
    assert routes["events_route"] == "/vault/storage-provider-config-events.json"
    assert routes["validation_route"] == "/vault/storage-provider-config-validation.json"
    assert routes["next_step_route"] == "/vault/storage-provider-config-next-step.json"
    assert routes["gp061_status_route"] == "/vault/gp061-status.json"

    assert home["next_step"]["next_pack"] == "VAULT_GP062_REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY"
    assert home["next_step"]["safe_to_continue_to_gp062"] is True
    assert home["next_step"]["vault_done"] is False
    assert home["next_step"]["clouds_should_continue"] is False


def test_gp061_status_ready_real_new_section_and_locked(config_db):
    status = get_gp061_status(config_db)
    gp061 = status["gp061_status"]

    assert status["pack"]["id"] == "VAULT_GP061"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert status["pack"]["section_range"] == "GP061-GP070"

    assert gp061["ready"] is True
    assert gp061["section_id"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert gp061["section_title"] == "Archive Vault — Real Storage Provider Configuration Layer"
    assert gp061["section_range"] == "GP061-GP070"
    assert gp061["real_storage_provider_config_contract_ready"] is True
    assert gp061["real_sqlite_backed"] is True
    assert gp061["real_schema_ready"] is True
    assert gp061["real_contract_count"] == 1
    assert gp061["real_requirement_count"] == EXPECTED_REQUIREMENTS
    assert gp061["real_blocker_count"] == EXPECTED_BLOCKERS
    assert gp061["real_event_count"] >= 5
    assert gp061["source_gp060_readiness_checkpoint_attached"] is True
    assert gp061["config_contract_ready"] is True
    assert gp061["provider_candidate_count"] == EXPECTED_PROVIDER_CANDIDATES
    assert gp061["requirement_code_count"] == len(CONFIG_REQUIREMENTS)
    assert gp061["config_value_present_count"] == 0
    assert gp061["secret_value_present_count"] == 0
    assert gp061["config_verified_count"] == 0
    assert gp061["capability_blocker_count"] == 60
    assert gp061["criteria_blocker_count"] == 40
    assert gp061["risk_blocker_count"] == 40
    assert gp061["blocks_provider_configuration_count"] == EXPECTED_BLOCKERS
    assert gp061["blocks_provider_read_write_count"] == EXPECTED_BLOCKERS
    assert gp061["blocks_export_count"] == EXPECTED_BLOCKERS
    assert gp061["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert gp061["tower_review_granted_count"] == 0
    assert gp061["resolved_count"] == 0
    assert gp061["validation_ready"] is True
    assert gp061["validation_passed"] is True
    assert gp061["safe_to_continue_to_gp062"] is True
    assert gp061["vault_done"] is False
    assert gp061["foundation_status"] == "config_contract_ready_safe_to_continue_not_done"

    assert gp061["provider_approval_ready"] is False
    assert gp061["provider_activation_ready"] is False
    assert gp061["provider_configuration_ready"] is False
    assert gp061["provider_read_write_ready"] is False
    assert gp061["provider_approved"] is False
    assert gp061["provider_activated"] is False
    assert gp061["provider_recommended"] is False
    assert gp061["provider_selected"] is False
    assert gp061["provider_configured"] is False
    assert gp061["credentials_configured"] is False
    assert gp061["provider_endpoint_configured"] is False
    assert gp061["storage_container_configured"] is False
    assert gp061["encryption_configured"] is False
    assert gp061["provider_write_enabled"] is False
    assert gp061["provider_read_enabled"] is False
    assert gp061["provider_object_read_claimed"] is False
    assert gp061["provider_connection_tested"] is False
    assert gp061["risk_accepted"] is False
    assert gp061["risk_waived"] is False
    assert gp061["mitigation_approved"] is False
    assert gp061["official_storage_receipt"] is False
    assert gp061["finalized_storage_receipt"] is False
    assert gp061["closed_storage_receipt"] is False
    assert gp061["object_body_view_enabled"] is False
    assert gp061["direct_upload_enabled"] is False
    assert gp061["export_enabled"] is False
    assert gp061["execution_enabled"] is False
    assert gp061["clouds_status"] == "parked_do_not_continue_from_vault_gp061"
    assert gp061["next_pack"] == "VAULT_GP062_REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY"


def test_gp061_next_step_points_to_gp062_credential_boundary():
    next_step = get_storage_provider_config_next_step()["next_step"]

    assert next_step["current_section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert next_step["current_section_range"] == "GP061-GP070"
    assert next_step["next_pack"] == "VAULT_GP062_REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY"
    assert next_step["next_pack_title"] == "Real Storage Provider Credential Boundary"
    assert next_step["safe_to_continue_to_gp062"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

    note = next_step["owner_notebook_note"].lower()
    assert "real storage provider configuration layer" in note
    assert "gp062" in note
    assert "without storing secrets" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "real sqlite storage provider config contract" in rules
    assert "real config requirement rows" in rules
    assert "real blockers carried from gp060" in rules
    assert "real storage provider credential boundary" in rules
    assert "do not store provider secrets" in rules
    assert "do not configure credentials yet" in rules
    assert "do not configure provider endpoint yet" in rules
    assert "do not unlock export" in rules
    assert "do not unlock execution" in rules
    assert "do not treat vault as done" in rules


def test_gp061_html_is_dark_and_mentions_config_contract(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "html_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "html_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "html_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "html_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "html_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "html_readiness.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB", str(tmp_path / "html_config.sqlite"))

    html = render_real_storage_provider_config_contract_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Config Contract" in html
    assert "Real Storage Provider Configuration Layer" in html
    assert "Archive Vault" in html
    assert "GP061" in html
    assert "New section started" in html
    assert "Real SQLite-backed" in html
    assert "Config contract ready" in html
    assert "No credentials configured" in html
    assert "No provider configured" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-config-contract.json" in html
    assert "/vault/gp061-status.json" in html

    forbidden = [
        "background: #fff",
        "background:#fff",
        "background-color: #fff",
        "background-color:#fff",
        "background: white",
        "background:white",
    ]

    for token in forbidden:
        assert token not in lowered


def test_gp061_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/real-storage-provider-config-contract",
        "/vault/real-storage-provider-config-contract.json",
        "/vault/storage-provider-config-contract-record.json",
        "/vault/storage-provider-config-requirements.json",
        "/vault/storage-provider-config-blockers.json",
        "/vault/storage-provider-config-events.json",
        "/vault/storage-provider-config-validation.json",
        "/vault/storage-provider-config-next-step.json",
        "/vault/gp061-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp061_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "routes_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "routes_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "routes_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "routes_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "routes_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "routes_readiness.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB", str(tmp_path / "routes_config.sqlite"))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/real-storage-provider-config-contract",
        "/vault/real-storage-provider-config-contract.json",
        "/vault/storage-provider-config-contract-record.json",
        "/vault/storage-provider-config-requirements.json",
        "/vault/storage-provider-config-blockers.json",
        "/vault/storage-provider-config-events.json",
        "/vault/storage-provider-config-validation.json",
        "/vault/storage-provider-config-next-step.json",
        "/vault/gp061-status.json",
    ]

    for route in routes:
        response = client.get(route)
        assert response.status_code in (200, 403), (
            f"{route} returned unexpected status {response.status_code}. "
            "Expected 200 direct route or 403 Tower/private guard."
        )

        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Real Storage Provider Config Contract" in response.data
