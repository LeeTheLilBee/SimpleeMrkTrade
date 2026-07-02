"""
Tests for VAULT GIANT PACK 057 — Real Storage Provider Capability Contract
"""

from pathlib import Path

import pytest

from vault.real_storage_provider_capability_contract_service import (
    CAPABILITY_REQUIREMENTS,
    DEFAULT_CAPABILITY_CONTRACT_ID,
    ensure_capability_contract_schema,
    get_gp057_status,
    get_real_storage_provider_capability_contract_home,
    get_storage_provider_capability_contract_record,
    get_storage_provider_capability_events,
    get_storage_provider_capability_next_step,
    get_storage_provider_capability_requirements,
    initialize_real_storage_provider_capability_contract,
    record_storage_provider_capability_review_event,
    render_real_storage_provider_capability_contract_page,
    validate_storage_provider_capability_contract,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def capability_db(tmp_path, monkeypatch):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "selection_registry.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "capability_contract.sqlite"))
    return str(tmp_path / "capability_contract.sqlite")


def test_gp057_schema_is_real_sqlite_backed(capability_db):
    result = ensure_capability_contract_schema(capability_db)
    db_path = Path(result["db_path"])

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert db_path.exists()
    assert "vault_storage_provider_capability_contracts" in result["tables"]
    assert "vault_storage_provider_capability_requirements" in result["tables"]
    assert "vault_storage_provider_capability_events" in result["tables"]


def test_gp057_initialize_creates_real_contract_requirements_and_event_log(capability_db):
    result = initialize_real_storage_provider_capability_contract(capability_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["contract_id"] == DEFAULT_CAPABILITY_CONTRACT_ID
    assert result["contract_count"] == 1
    assert result["capability_requirement_count"] == 5 * len(CAPABILITY_REQUIREMENTS)
    assert result["event_count"] >= 4

    second = initialize_real_storage_provider_capability_contract(capability_db)
    assert second["contract_count"] == 1
    assert second["capability_requirement_count"] == 5 * len(CAPABILITY_REQUIREMENTS)
    assert second["event_count"] >= 4


def test_gp057_contract_record_is_real_and_sourced_from_gp056(capability_db):
    contract = get_storage_provider_capability_contract_record(capability_db)["contract"]

    assert contract["contract_id"] == DEFAULT_CAPABILITY_CONTRACT_ID
    assert contract["pack_id"] == "VAULT_GP057"
    assert contract["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert contract["section_range"] == "GP051-GP060"
    assert contract["source_selection_registry_id"] == "VSPSR-GP056-001"
    assert contract["source_selection_pack_id"] == "VAULT_GP056"
    assert contract["contract_status"] == "REAL_CAPABILITY_CONTRACT_OPEN_TOWER_LOCKED"
    assert contract["tower_authority_status"] == "TOWER_REVIEW_REQUIRED_NOT_GRANTED"

    data = contract["contract_data"]
    assert data["contract_type"] == "REAL_STORAGE_PROVIDER_CAPABILITY_CONTRACT"
    assert data["real_durable_contract"] is True
    assert data["metadata_source"] == "VAULT_GP056_REAL_STORAGE_PROVIDER_SELECTION_REGISTRY"
    assert data["source_selection_registry_id"] == "VSPSR-GP056-001"
    assert data["source_selection_pack_id"] == "VAULT_GP056"
    assert data["provider_candidate_count"] == 5
    assert data["capability_code_count"] == len(CAPABILITY_REQUIREMENTS)
    assert data["capability_requirement_count"] == 5 * len(CAPABILITY_REQUIREMENTS)
    assert len(data["candidate_contract_summaries"]) == 5
    assert data["safe_to_continue_to_gp058"] is True


def test_gp057_contract_keeps_all_unsafe_operations_locked(capability_db):
    contract = get_storage_provider_capability_contract_record(capability_db)["contract"]

    assert contract["provider_activated"] is False
    assert contract["provider_recommended"] is False
    assert contract["provider_selected"] is False
    assert contract["provider_configured"] is False
    assert contract["provider_read_enabled"] is False
    assert contract["provider_write_enabled"] is False
    assert contract["provider_object_read_claimed"] is False
    assert contract["provider_connection_tested"] is False
    assert contract["risk_accepted"] is False
    assert contract["risk_waived"] is False
    assert contract["mitigation_approved"] is False
    assert contract["object_body_view_enabled"] is False
    assert contract["direct_upload_enabled"] is False
    assert contract["export_enabled"] is False
    assert contract["execution_enabled"] is False
    assert contract["vault_done"] is False


def test_gp057_capability_requirement_rows_are_real_and_locked(capability_db):
    payload = get_storage_provider_capability_requirements(capability_db)

    expected_count = 5 * len(CAPABILITY_REQUIREMENTS)

    assert payload["pack"]["id"] == "VAULT_GP057"
    assert payload["real_sqlite_backed"] is True
    assert payload["capability_requirement_count"] == expected_count
    assert payload["provider_candidate_count"] == 5
    assert payload["capability_code_count"] == len(CAPABILITY_REQUIREMENTS)
    assert payload["required_for_beta_count"] == expected_count
    assert payload["candidate_claimed_supported_count"] == 0
    assert payload["contract_verified_count"] == 0
    assert payload["tower_review_required_count"] == expected_count
    assert payload["tower_review_granted_count"] == 0
    assert payload["provider_activated_count"] == 0
    assert payload["provider_recommended_count"] == 0
    assert payload["provider_selected_count"] == 0
    assert payload["provider_configured_count"] == 0
    assert payload["provider_read_enabled_count"] == 0
    assert payload["provider_write_enabled_count"] == 0
    assert payload["object_body_view_enabled_count"] == 0
    assert payload["export_enabled_count"] == 0
    assert payload["execution_enabled_count"] == 0

    codes = {item["capability_code"] for item in payload["requirements"]}
    expected_codes = {item["capability_code"] for item in CAPABILITY_REQUIREMENTS}
    assert codes == expected_codes

    for item in payload["requirements"]:
        assert item["capability_requirement_id"].startswith("VSPCR-")
        assert item["contract_id"] == DEFAULT_CAPABILITY_CONTRACT_ID
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["requirement_status"] == "REQUIRED_CONTRACT_ROW_NOT_CLAIMED_NOT_VERIFIED_TOWER_LOCKED"
        assert item["required_for_beta"] is True
        assert item["candidate_claimed_supported"] is False
        assert item["contract_verified"] is False
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False
        assert item["provider_activated"] is False
        assert item["provider_recommended"] is False
        assert item["provider_selected"] is False
        assert item["provider_configured"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["export_enabled"] is False
        assert item["execution_enabled"] is False


def test_gp057_event_log_is_real_and_seeded(capability_db):
    events = get_storage_provider_capability_events(capability_db)

    assert events["pack"]["id"] == "VAULT_GP057"
    assert events["real_sqlite_backed"] is True
    assert events["event_count"] >= 4

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_CAPABILITY_CONTRACT_CREATED" in event_types
    assert "SOURCE_GP056_SELECTION_REGISTRY_ATTACHED" in event_types
    assert "REAL_CAPABILITY_REQUIREMENTS_CREATED" in event_types
    assert "TOWER_CAPABILITY_LOCKS_CONFIRMED" in event_types

    for event in events["events"]:
        assert event["event_id"].startswith("VSPCE-")
        assert event["contract_id"] == DEFAULT_CAPABILITY_CONTRACT_ID
        assert isinstance(event["event_payload"], dict)
        assert event["created_at"]


def test_gp057_can_write_real_review_event_without_unlocking_provider(capability_db):
    before = get_storage_provider_capability_events(capability_db)["event_count"]

    written = record_storage_provider_capability_review_event(
        "OWNER_CAPABILITY_REVIEW_OBSERVED",
        {"reviewer": "owner", "note": "reviewed real capability contract"},
        capability_db,
    )

    after = get_storage_provider_capability_events(capability_db)
    contract = get_storage_provider_capability_contract_record(capability_db)["contract"]
    requirements = get_storage_provider_capability_requirements(capability_db)

    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPCE-")
    assert written["contract_id"] == DEFAULT_CAPABILITY_CONTRACT_ID
    assert written["real_sqlite_backed"] is True
    assert written["provider_activated"] is False
    assert written["provider_selected"] is False
    assert written["provider_recommended"] is False
    assert written["provider_configured"] is False
    assert written["provider_read_enabled"] is False
    assert written["provider_write_enabled"] is False
    assert written["risk_accepted"] is False
    assert written["risk_waived"] is False
    assert written["mitigation_approved"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

    assert after["event_count"] == before + 1
    assert "OWNER_CAPABILITY_REVIEW_OBSERVED" in {event["event_type"] for event in after["events"]}

    assert contract["provider_activated"] is False
    assert contract["provider_selected"] is False
    assert contract["provider_configured"] is False
    assert contract["provider_read_enabled"] is False
    assert contract["provider_write_enabled"] is False
    assert contract["vault_done"] is False

    assert requirements["provider_activated_count"] == 0
    assert requirements["contract_verified_count"] == 0


def test_gp057_validation_passes_locked_real_capability_contract(capability_db):
    validation = validate_storage_provider_capability_contract(capability_db)

    assert validation["pack"]["id"] == "VAULT_GP057"
    assert validation["validation_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["passed_count"] == validation["check_count"]
    assert validation["real_sqlite_backed"] is True
    assert validation["safe_to_continue_to_gp058"] is True

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_CAPABILITY_CONTRACT_EXISTS" in codes
    assert "SOURCE_GP056_SELECTION_REGISTRY_ATTACHED" in codes
    assert "REAL_CAPABILITY_REQUIREMENT_ROWS_EXIST" in codes
    assert "ALL_REQUIRED_CAPABILITIES_RECORDED" in codes
    assert "NO_CAPABILITY_SUPPORT_CLAIMED_YET" in codes
    assert "NO_CAPABILITY_CONTRACT_VERIFIED_YET" in codes
    assert "NO_PROVIDER_ACTIVATED" in codes
    assert "NO_PROVIDER_RECOMMENDED" in codes
    assert "NO_PROVIDER_SELECTED" in codes
    assert "NO_PROVIDER_CONFIGURED" in codes
    assert "NO_PROVIDER_READ_ENABLED" in codes
    assert "NO_PROVIDER_WRITE_ENABLED" in codes
    assert "NO_EXPORT" in codes
    assert "NO_EXECUTION" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "EVENT_LOG_EXISTS" in codes


def test_gp057_home_payload_has_truth_routes_and_next_step(capability_db):
    home = get_real_storage_provider_capability_contract_home(capability_db)

    assert home["pack"]["id"] == "VAULT_GP057"
    assert home["capability_truth"]["real_storage_provider_capability_contract_ready"] is True
    assert home["capability_truth"]["real_sqlite_backed"] is True
    assert home["capability_truth"]["real_schema_ready"] is True
    assert home["capability_truth"]["real_capability_contract_exists"] is True
    assert home["capability_truth"]["real_capability_requirement_rows_exist"] is True
    assert home["capability_truth"]["real_event_log_exists"] is True
    assert home["capability_truth"]["source_gp056_selection_registry_attached"] is True
    assert home["capability_truth"]["validation_passed"] is True
    assert home["capability_truth"]["provider_candidate_count"] == 5
    assert home["capability_truth"]["capability_code_count"] == len(CAPABILITY_REQUIREMENTS)
    assert home["capability_truth"]["capability_requirement_count"] == 5 * len(CAPABILITY_REQUIREMENTS)
    assert home["capability_truth"]["provider_activated"] is False
    assert home["capability_truth"]["provider_recommended"] is False
    assert home["capability_truth"]["provider_selected"] is False
    assert home["capability_truth"]["provider_configured"] is False
    assert home["capability_truth"]["provider_read_enabled"] is False
    assert home["capability_truth"]["provider_write_enabled"] is False
    assert home["capability_truth"]["candidate_claimed_supported_count"] == 0
    assert home["capability_truth"]["contract_verified_count"] == 0
    assert home["capability_truth"]["export_enabled"] is False
    assert home["capability_truth"]["execution_enabled"] is False
    assert home["capability_truth"]["vault_done"] is False

    routes = home["routes"]
    assert routes["route"] == "/vault/real-storage-provider-capability-contract"
    assert routes["json_route"] == "/vault/real-storage-provider-capability-contract.json"
    assert routes["contract_route"] == "/vault/storage-provider-capability-contract-record.json"
    assert routes["requirements_route"] == "/vault/storage-provider-capability-requirements.json"
    assert routes["events_route"] == "/vault/storage-provider-capability-events.json"
    assert routes["validation_route"] == "/vault/storage-provider-capability-validation.json"
    assert routes["next_step_route"] == "/vault/storage-provider-capability-next-step.json"
    assert routes["gp057_status_route"] == "/vault/gp057-status.json"

    assert home["next_step"]["next_pack"] == "VAULT_GP058_REAL_PROVIDER_RISK_CRITERIA_VALIDATION_ENGINE"
    assert home["next_step"]["safe_to_continue_to_gp058"] is True
    assert home["next_step"]["vault_done"] is False
    assert home["next_step"]["clouds_should_continue"] is False


def test_gp057_status_ready_real_and_locked(capability_db):
    status = get_gp057_status(capability_db)
    gp057 = status["gp057_status"]

    assert status["pack"]["id"] == "VAULT_GP057"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert status["pack"]["section_range"] == "GP051-GP060"

    assert gp057["ready"] is True
    assert gp057["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp057["section_title"] == "Archive Vault — Storage Provider Prep Layer"
    assert gp057["section_range"] == "GP051-GP060"
    assert gp057["real_storage_provider_capability_contract_ready"] is True
    assert gp057["real_sqlite_backed"] is True
    assert gp057["real_schema_ready"] is True
    assert gp057["real_contract_count"] == 1
    assert gp057["real_capability_requirement_count"] == 5 * len(CAPABILITY_REQUIREMENTS)
    assert gp057["real_event_count"] >= 4
    assert gp057["source_gp056_selection_registry_attached"] is True
    assert gp057["validation_ready"] is True
    assert gp057["validation_passed"] is True
    assert gp057["safe_to_continue_to_gp058"] is True
    assert gp057["vault_done"] is False
    assert gp057["foundation_status"] == "safe_to_continue_not_done"
    assert gp057["provider_activated"] is False
    assert gp057["provider_recommended"] is False
    assert gp057["provider_selected"] is False
    assert gp057["provider_configured"] is False
    assert gp057["provider_write_enabled"] is False
    assert gp057["provider_read_enabled"] is False
    assert gp057["provider_object_read_claimed"] is False
    assert gp057["provider_connection_tested"] is False
    assert gp057["capability_candidate_claimed_supported_count"] == 0
    assert gp057["capability_contract_verified_count"] == 0
    assert gp057["risk_accepted"] is False
    assert gp057["risk_waived"] is False
    assert gp057["mitigation_approved"] is False
    assert gp057["object_body_view_enabled"] is False
    assert gp057["direct_upload_enabled"] is False
    assert gp057["export_enabled"] is False
    assert gp057["execution_enabled"] is False
    assert gp057["clouds_status"] == "parked_do_not_continue_from_vault_gp057"
    assert gp057["next_pack"] == "VAULT_GP058_REAL_PROVIDER_RISK_CRITERIA_VALIDATION_ENGINE"


def test_gp057_next_step_says_continue_real_vault_not_clouds():
    next_step = get_storage_provider_capability_next_step()["next_step"]

    assert next_step["next_pack"] == "VAULT_GP058_REAL_PROVIDER_RISK_CRITERIA_VALIDATION_ENGINE"
    assert next_step["next_pack_title"] == "Real Provider Risk / Criteria Validation Engine"
    assert next_step["safe_to_continue_to_gp058"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

    note = next_step["owner_notebook_note"].lower()
    assert "keep vault real and durable" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "real sqlite capability contract" in rules
    assert "real capability requirement rows" in rules
    assert "real capability event log" in rules
    assert "real provider risk/criteria validation engine" in rules
    assert "do not activate a provider yet" in rules
    assert "do not select a provider yet" in rules
    assert "not vault done" in rules


def test_gp057_html_is_dark_and_mentions_real_capability_contract(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "html_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "html_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "html_capability.sqlite"))

    html = render_real_storage_provider_capability_contract_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Capability Contract" in html
    assert "Storage Provider Prep Layer" in html
    assert "Archive Vault" in html
    assert "GP057" in html
    assert "Real SQLite-backed" in html
    assert "Real capability contract" in html
    assert "Real requirement rows" in html
    assert "No provider activated" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-capability-contract.json" in html
    assert "/vault/gp057-status.json" in html

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


def test_gp057_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/real-storage-provider-capability-contract",
        "/vault/real-storage-provider-capability-contract.json",
        "/vault/storage-provider-capability-contract-record.json",
        "/vault/storage-provider-capability-requirements.json",
        "/vault/storage-provider-capability-events.json",
        "/vault/storage-provider-capability-validation.json",
        "/vault/storage-provider-capability-next-step.json",
        "/vault/gp057-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp057_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "routes_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "routes_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "routes_capability.sqlite"))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/real-storage-provider-capability-contract",
        "/vault/real-storage-provider-capability-contract.json",
        "/vault/storage-provider-capability-contract-record.json",
        "/vault/storage-provider-capability-requirements.json",
        "/vault/storage-provider-capability-events.json",
        "/vault/storage-provider-capability-validation.json",
        "/vault/storage-provider-capability-next-step.json",
        "/vault/gp057-status.json",
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
                assert b"Vault Real Storage Provider Capability Contract" in response.data
