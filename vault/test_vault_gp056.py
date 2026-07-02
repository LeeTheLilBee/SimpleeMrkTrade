"""
Tests for VAULT GIANT PACK 056 — Real Storage Provider Selection Registry
"""

from pathlib import Path

import pytest

from vault.real_storage_provider_selection_registry_service import (
    DEFAULT_SELECTION_REGISTRY_ID,
    ensure_selection_registry_schema,
    get_gp056_status,
    get_real_storage_provider_selection_registry_home,
    get_storage_provider_selection_candidates,
    get_storage_provider_selection_events,
    get_storage_provider_selection_next_step,
    get_storage_provider_selection_registry_record,
    initialize_real_storage_provider_selection_registry,
    record_storage_provider_selection_review_event,
    render_real_storage_provider_selection_registry_page,
    validate_storage_provider_selection_registry,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def registry_db(tmp_path, monkeypatch):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "selection_registry.sqlite"))
    return str(tmp_path / "selection_registry.sqlite")


def test_gp056_schema_is_real_sqlite_backed(registry_db):
    result = ensure_selection_registry_schema(registry_db)
    db_path = Path(result["db_path"])

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert db_path.exists()
    assert "vault_storage_provider_selection_registries" in result["tables"]
    assert "vault_storage_provider_selection_candidates" in result["tables"]
    assert "vault_storage_provider_selection_events" in result["tables"]


def test_gp056_initialize_creates_real_registry_candidates_and_event_log(registry_db):
    result = initialize_real_storage_provider_selection_registry(registry_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["registry_id"] == DEFAULT_SELECTION_REGISTRY_ID
    assert result["registry_count"] == 1
    assert result["candidate_count"] == 5
    assert result["event_count"] >= 4

    second = initialize_real_storage_provider_selection_registry(registry_db)
    assert second["registry_count"] == 1
    assert second["candidate_count"] == 5
    assert second["event_count"] >= 4


def test_gp056_registry_record_is_real_and_sourced_from_gp055(registry_db):
    registry = get_storage_provider_selection_registry_record(registry_db)["registry"]

    assert registry["registry_id"] == DEFAULT_SELECTION_REGISTRY_ID
    assert registry["pack_id"] == "VAULT_GP056"
    assert registry["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert registry["section_range"] == "GP051-GP060"
    assert registry["source_decision_record_id"] == "VSPDR-GP055-001"
    assert registry["source_decision_pack_id"] == "VAULT_GP055"
    assert registry["registry_status"] == "REAL_SELECTION_REGISTRY_OPEN_TOWER_LOCKED"
    assert registry["tower_authority_status"] == "TOWER_REVIEW_REQUIRED_NOT_GRANTED"

    data = registry["registry_data"]
    assert data["registry_type"] == "REAL_STORAGE_PROVIDER_SELECTION_REGISTRY"
    assert data["real_durable_registry"] is True
    assert data["metadata_source"] == "VAULT_GP055_REAL_STORAGE_PROVIDER_DECISION_RECORD"
    assert data["source_decision_record_id"] == "VSPDR-GP055-001"
    assert data["source_decision_pack_id"] == "VAULT_GP055"
    assert data["provider_candidate_count"] == 5
    assert len(data["candidate_entries"]) == 5
    assert data["safe_to_continue_to_gp057"] is True


def test_gp056_registry_keeps_all_unsafe_operations_locked(registry_db):
    registry = get_storage_provider_selection_registry_record(registry_db)["registry"]

    assert registry["recommended_provider_id"] is None
    assert registry["selected_provider_id"] is None
    assert registry["provider_configured"] is False
    assert registry["provider_read_enabled"] is False
    assert registry["provider_write_enabled"] is False
    assert registry["provider_object_read_claimed"] is False
    assert registry["provider_connection_tested"] is False
    assert registry["risk_accepted"] is False
    assert registry["risk_waived"] is False
    assert registry["mitigation_approved"] is False
    assert registry["object_body_view_enabled"] is False
    assert registry["direct_upload_enabled"] is False
    assert registry["export_enabled"] is False
    assert registry["execution_enabled"] is False
    assert registry["vault_done"] is False


def test_gp056_candidate_rows_are_real_and_locked(registry_db):
    candidates = get_storage_provider_selection_candidates(registry_db)

    assert candidates["pack"]["id"] == "VAULT_GP056"
    assert candidates["real_sqlite_backed"] is True
    assert candidates["candidate_count"] == 5
    assert candidates["provider_recommended_count"] == 0
    assert candidates["provider_selected_count"] == 0
    assert candidates["provider_configured_count"] == 0
    assert candidates["provider_read_enabled_count"] == 0
    assert candidates["provider_write_enabled_count"] == 0
    assert candidates["risk_accepted_count"] == 0
    assert candidates["risk_waived_count"] == 0
    assert candidates["mitigation_approved_count"] == 0
    assert candidates["tower_review_required_count"] == 5
    assert candidates["tower_review_granted_count"] == 0

    for item in candidates["candidates"]:
        assert item["candidate_entry_id"].startswith("VSPSC-")
        assert item["registry_id"] == DEFAULT_SELECTION_REGISTRY_ID
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["decision_state"] == "REAL_SELECTION_CANDIDATE_REGISTERED_NOT_RECOMMENDED_NOT_SELECTED"
        assert item["criteria_card_count"] == 8
        assert item["risk_card_count"] == 8
        assert item["comparison_factor_count"] == 6
        assert item["rank_present"] is False
        assert item["rank_finalized"] is False
        assert item["comparison_score_present"] is False
        assert item["comparison_score_finalized"] is False
        assert item["provider_recommended"] is False
        assert item["provider_selected"] is False
        assert item["provider_configured"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["risk_accepted"] is False
        assert item["risk_waived"] is False
        assert item["mitigation_approved"] is False
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False


def test_gp056_event_log_is_real_and_seeded(registry_db):
    events = get_storage_provider_selection_events(registry_db)

    assert events["pack"]["id"] == "VAULT_GP056"
    assert events["real_sqlite_backed"] is True
    assert events["event_count"] >= 4

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_SELECTION_REGISTRY_CREATED" in event_types
    assert "SOURCE_GP055_DECISION_RECORD_ATTACHED" in event_types
    assert "REAL_CANDIDATE_REGISTRY_ENTRIES_CREATED" in event_types
    assert "TOWER_SELECTION_LOCKS_CONFIRMED" in event_types

    for event in events["events"]:
        assert event["event_id"].startswith("VSPSE-")
        assert event["registry_id"] == DEFAULT_SELECTION_REGISTRY_ID
        assert isinstance(event["event_payload"], dict)
        assert event["created_at"]


def test_gp056_can_write_real_review_event_without_unlocking_selection(registry_db):
    before = get_storage_provider_selection_events(registry_db)["event_count"]

    written = record_storage_provider_selection_review_event(
        "OWNER_SELECTION_REVIEW_OBSERVED",
        {"reviewer": "owner", "note": "reviewed real selection registry"},
        registry_db,
    )

    after = get_storage_provider_selection_events(registry_db)
    registry = get_storage_provider_selection_registry_record(registry_db)["registry"]
    candidates = get_storage_provider_selection_candidates(registry_db)

    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPSE-")
    assert written["registry_id"] == DEFAULT_SELECTION_REGISTRY_ID
    assert written["real_sqlite_backed"] is True
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
    assert "OWNER_SELECTION_REVIEW_OBSERVED" in {event["event_type"] for event in after["events"]}

    assert registry["selected_provider_id"] is None
    assert registry["recommended_provider_id"] is None
    assert registry["provider_configured"] is False
    assert registry["provider_read_enabled"] is False
    assert registry["provider_write_enabled"] is False
    assert registry["vault_done"] is False

    assert candidates["provider_selected_count"] == 0
    assert candidates["provider_recommended_count"] == 0


def test_gp056_validation_passes_locked_real_selection_registry(registry_db):
    validation = validate_storage_provider_selection_registry(registry_db)

    assert validation["pack"]["id"] == "VAULT_GP056"
    assert validation["validation_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["passed_count"] == validation["check_count"]
    assert validation["real_sqlite_backed"] is True
    assert validation["safe_to_continue_to_gp057"] is True

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_SELECTION_REGISTRY_EXISTS" in codes
    assert "SOURCE_GP055_DECISION_RECORD_ATTACHED" in codes
    assert "REAL_CANDIDATE_REGISTRY_ROWS_EXIST" in codes
    assert "NO_PROVIDER_RECOMMENDED" in codes
    assert "NO_PROVIDER_SELECTED" in codes
    assert "NO_PROVIDER_CONFIGURED" in codes
    assert "NO_PROVIDER_READ_ENABLED" in codes
    assert "NO_PROVIDER_WRITE_ENABLED" in codes
    assert "NO_EXPORT" in codes
    assert "NO_EXECUTION" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "EVENT_LOG_EXISTS" in codes


def test_gp056_home_payload_has_truth_routes_and_next_step(registry_db):
    home = get_real_storage_provider_selection_registry_home(registry_db)

    assert home["pack"]["id"] == "VAULT_GP056"
    assert home["selection_truth"]["real_storage_provider_selection_registry_ready"] is True
    assert home["selection_truth"]["real_sqlite_backed"] is True
    assert home["selection_truth"]["real_schema_ready"] is True
    assert home["selection_truth"]["real_selection_registry_exists"] is True
    assert home["selection_truth"]["real_candidate_registry_rows_exist"] is True
    assert home["selection_truth"]["real_event_log_exists"] is True
    assert home["selection_truth"]["source_gp055_decision_record_attached"] is True
    assert home["selection_truth"]["validation_passed"] is True
    assert home["selection_truth"]["provider_candidate_count"] == 5
    assert home["selection_truth"]["provider_recommended"] is False
    assert home["selection_truth"]["provider_selected"] is False
    assert home["selection_truth"]["provider_configured"] is False
    assert home["selection_truth"]["provider_read_enabled"] is False
    assert home["selection_truth"]["provider_write_enabled"] is False
    assert home["selection_truth"]["candidate_provider_recommended_count"] == 0
    assert home["selection_truth"]["candidate_provider_selected_count"] == 0
    assert home["selection_truth"]["export_enabled"] is False
    assert home["selection_truth"]["execution_enabled"] is False
    assert home["selection_truth"]["vault_done"] is False

    routes = home["routes"]
    assert routes["route"] == "/vault/real-storage-provider-selection-registry"
    assert routes["json_route"] == "/vault/real-storage-provider-selection-registry.json"
    assert routes["registry_route"] == "/vault/storage-provider-selection-registry-record.json"
    assert routes["candidates_route"] == "/vault/storage-provider-selection-candidates.json"
    assert routes["events_route"] == "/vault/storage-provider-selection-events.json"
    assert routes["validation_route"] == "/vault/storage-provider-selection-validation.json"
    assert routes["next_step_route"] == "/vault/storage-provider-selection-next-step.json"
    assert routes["gp056_status_route"] == "/vault/gp056-status.json"

    assert home["next_step"]["next_pack"] == "VAULT_GP057_REAL_STORAGE_PROVIDER_CAPABILITY_CONTRACT"
    assert home["next_step"]["safe_to_continue_to_gp057"] is True
    assert home["next_step"]["vault_done"] is False
    assert home["next_step"]["clouds_should_continue"] is False


def test_gp056_status_ready_real_and_locked(registry_db):
    status = get_gp056_status(registry_db)
    gp056 = status["gp056_status"]

    assert status["pack"]["id"] == "VAULT_GP056"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert status["pack"]["section_range"] == "GP051-GP060"

    assert gp056["ready"] is True
    assert gp056["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp056["section_title"] == "Archive Vault — Storage Provider Prep Layer"
    assert gp056["section_range"] == "GP051-GP060"
    assert gp056["real_storage_provider_selection_registry_ready"] is True
    assert gp056["real_sqlite_backed"] is True
    assert gp056["real_schema_ready"] is True
    assert gp056["real_registry_count"] == 1
    assert gp056["real_candidate_count"] == 5
    assert gp056["real_event_count"] >= 4
    assert gp056["source_gp055_decision_record_attached"] is True
    assert gp056["validation_ready"] is True
    assert gp056["validation_passed"] is True
    assert gp056["safe_to_continue_to_gp057"] is True
    assert gp056["vault_done"] is False
    assert gp056["foundation_status"] == "safe_to_continue_not_done"
    assert gp056["provider_recommended"] is False
    assert gp056["provider_selected"] is False
    assert gp056["provider_configured"] is False
    assert gp056["provider_write_enabled"] is False
    assert gp056["provider_read_enabled"] is False
    assert gp056["provider_object_read_claimed"] is False
    assert gp056["provider_connection_tested"] is False
    assert gp056["candidate_provider_recommended_count"] == 0
    assert gp056["candidate_provider_selected_count"] == 0
    assert gp056["risk_accepted"] is False
    assert gp056["risk_waived"] is False
    assert gp056["mitigation_approved"] is False
    assert gp056["object_body_view_enabled"] is False
    assert gp056["direct_upload_enabled"] is False
    assert gp056["export_enabled"] is False
    assert gp056["execution_enabled"] is False
    assert gp056["clouds_status"] == "parked_do_not_continue_from_vault_gp056"
    assert gp056["next_pack"] == "VAULT_GP057_REAL_STORAGE_PROVIDER_CAPABILITY_CONTRACT"


def test_gp056_next_step_says_continue_real_vault_not_clouds():
    next_step = get_storage_provider_selection_next_step()["next_step"]

    assert next_step["next_pack"] == "VAULT_GP057_REAL_STORAGE_PROVIDER_CAPABILITY_CONTRACT"
    assert next_step["next_pack_title"] == "Real Storage Provider Capability Contract"
    assert next_step["safe_to_continue_to_gp057"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

    note = next_step["owner_notebook_note"].lower()
    assert "keep vault real and durable" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "real sqlite selection registry" in rules
    assert "real candidate registry rows" in rules
    assert "real selection registry events" in rules
    assert "real storage provider capability contract" in rules
    assert "do not recommend a provider yet" in rules
    assert "do not select a provider yet" in rules
    assert "not vault done" in rules


def test_gp056_html_is_dark_and_mentions_real_selection_registry(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "html_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "html_selection.sqlite"))

    html = render_real_storage_provider_selection_registry_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Selection Registry" in html
    assert "Storage Provider Prep Layer" in html
    assert "Archive Vault" in html
    assert "GP056" in html
    assert "Real SQLite-backed" in html
    assert "Real candidate rows" in html
    assert "Real event log" in html
    assert "No provider selected" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-selection-registry.json" in html
    assert "/vault/gp056-status.json" in html

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


def test_gp056_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/real-storage-provider-selection-registry",
        "/vault/real-storage-provider-selection-registry.json",
        "/vault/storage-provider-selection-registry-record.json",
        "/vault/storage-provider-selection-candidates.json",
        "/vault/storage-provider-selection-events.json",
        "/vault/storage-provider-selection-validation.json",
        "/vault/storage-provider-selection-next-step.json",
        "/vault/gp056-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp056_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "routes_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "routes_selection.sqlite"))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/real-storage-provider-selection-registry",
        "/vault/real-storage-provider-selection-registry.json",
        "/vault/storage-provider-selection-registry-record.json",
        "/vault/storage-provider-selection-candidates.json",
        "/vault/storage-provider-selection-events.json",
        "/vault/storage-provider-selection-validation.json",
        "/vault/storage-provider-selection-next-step.json",
        "/vault/gp056-status.json",
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
                assert b"Vault Real Storage Provider Selection Registry" in response.data
