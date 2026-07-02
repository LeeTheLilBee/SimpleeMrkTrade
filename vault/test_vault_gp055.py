"""
Tests for VAULT GIANT PACK 055 — Real Storage Provider Decision Record
"""

from pathlib import Path

import pytest

from vault.real_storage_provider_decision_record_service import (
    DEFAULT_DECISION_RECORD_ID,
    ensure_decision_store_schema,
    get_current_storage_provider_decision_record,
    get_gp055_status,
    get_real_storage_provider_decision_record_home,
    get_storage_provider_decision_events,
    get_storage_provider_decision_next_step,
    get_storage_provider_decision_records,
    initialize_real_storage_provider_decision_store,
    record_storage_provider_decision_review_event,
    render_real_storage_provider_decision_record_page,
    validate_storage_provider_decision_record,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def decision_db(tmp_path):
    return str(tmp_path / "vault_storage_provider_decisions.sqlite")


def test_gp055_schema_is_real_sqlite_backed(decision_db):
    result = ensure_decision_store_schema(decision_db)
    db_path = Path(result["db_path"])

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert db_path.exists()
    assert "vault_storage_provider_decision_records" in result["tables"]
    assert "vault_storage_provider_decision_events" in result["tables"]


def test_gp055_initialize_creates_real_record_and_event_log(decision_db):
    result = initialize_real_storage_provider_decision_store(decision_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["record_id"] == DEFAULT_DECISION_RECORD_ID
    assert result["record_count"] == 1
    assert result["event_count"] >= 3

    second = initialize_real_storage_provider_decision_store(decision_db)
    assert second["record_count"] == 1
    assert second["event_count"] >= 3


def test_gp055_current_decision_record_is_real_and_sourced_from_gp054(decision_db):
    current = get_current_storage_provider_decision_record(decision_db)["current_record"]

    assert current["record_id"] == DEFAULT_DECISION_RECORD_ID
    assert current["pack_id"] == "VAULT_GP055"
    assert current["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert current["section_range"] == "GP051-GP060"
    assert current["decision_status"] == "REAL_DECISION_RECORD_OPEN_TOWER_LOCKED"
    assert current["tower_authority_status"] == "TOWER_REVIEW_REQUIRED_NOT_GRANTED"
    assert current["source_pack_id"] == "VAULT_GP054"
    assert current["source_record"]["source_pack_id"] == "VAULT_GP054"
    assert current["source_record"]["safe_to_continue_to_gp055"] is True
    assert current["source_record"]["vault_done"] is False
    assert current["source_record"]["provider_candidate_count"] == 5
    assert current["source_record"]["comparison_row_count"] == 5

    data = current["decision_data"]
    assert data["record_type"] == "REAL_STORAGE_PROVIDER_DECISION_RECORD"
    assert data["real_durable_record"] is True
    assert data["metadata_source"] == "VAULT_GP054_COMPARISON_BOARD"
    assert data["provider_candidate_count"] == 5
    assert len(data["candidate_records"]) == 5
    assert data["safe_to_continue_to_gp056"] is True


def test_gp055_decision_record_keeps_all_unsafe_operations_locked(decision_db):
    current = get_current_storage_provider_decision_record(decision_db)["current_record"]

    assert current["recommended_provider_id"] is None
    assert current["selected_provider_id"] is None
    assert current["provider_configured"] is False
    assert current["provider_read_enabled"] is False
    assert current["provider_write_enabled"] is False
    assert current["provider_object_read_claimed"] is False
    assert current["provider_connection_tested"] is False
    assert current["risk_accepted"] is False
    assert current["risk_waived"] is False
    assert current["mitigation_approved"] is False
    assert current["object_body_view_enabled"] is False
    assert current["direct_upload_enabled"] is False
    assert current["export_enabled"] is False
    assert current["execution_enabled"] is False
    assert current["vault_done"] is False

    for candidate in current["decision_data"]["candidate_records"]:
        assert candidate["decision_state"] == "REAL_CANDIDATE_RECORDED_NOT_RECOMMENDED_NOT_SELECTED"
        assert candidate["rank_present"] is False
        assert candidate["rank_finalized"] is False
        assert candidate["comparison_score_present"] is False
        assert candidate["comparison_score_finalized"] is False
        assert candidate["provider_recommended"] is False
        assert candidate["provider_selected"] is False
        assert candidate["provider_configured"] is False
        assert candidate["provider_read_enabled"] is False
        assert candidate["provider_write_enabled"] is False
        assert candidate["risk_accepted"] is False
        assert candidate["risk_waived"] is False
        assert candidate["mitigation_approved"] is False
        assert candidate["tower_review_required"] is True
        assert candidate["tower_review_granted"] is False


def test_gp055_records_list_returns_real_records(decision_db):
    records = get_storage_provider_decision_records(decision_db)

    assert records["pack"]["id"] == "VAULT_GP055"
    assert records["real_sqlite_backed"] is True
    assert records["record_count"] == 1
    assert records["records"][0]["record_id"] == DEFAULT_DECISION_RECORD_ID
    assert records["records"][0]["source_pack_id"] == "VAULT_GP054"


def test_gp055_event_log_is_real_and_seeded(decision_db):
    events = get_storage_provider_decision_events(decision_db)

    assert events["pack"]["id"] == "VAULT_GP055"
    assert events["real_sqlite_backed"] is True
    assert events["event_count"] >= 3

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_DECISION_RECORD_CREATED" in event_types
    assert "SOURCE_GP054_COMPARISON_ATTACHED" in event_types
    assert "TOWER_LOCKS_CONFIRMED" in event_types

    for event in events["events"]:
        assert event["event_id"].startswith("VSPDE-")
        assert event["record_id"] == DEFAULT_DECISION_RECORD_ID
        assert isinstance(event["event_payload"], dict)
        assert event["created_at"]


def test_gp055_can_write_real_review_event_without_unlocking_selection(decision_db):
    before = get_storage_provider_decision_events(decision_db)["event_count"]

    written = record_storage_provider_decision_review_event(
        "OWNER_REVIEW_OBSERVED",
        {"reviewer": "owner", "note": "reviewed durable decision record"},
        decision_db,
    )

    after = get_storage_provider_decision_events(decision_db)
    current = get_current_storage_provider_decision_record(decision_db)["current_record"]

    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPDE-")
    assert written["record_id"] == DEFAULT_DECISION_RECORD_ID
    assert written["real_sqlite_backed"] is True
    assert written["provider_selected"] is False
    assert written["provider_recommended"] is False
    assert written["provider_configured"] is False
    assert written["provider_read_enabled"] is False
    assert written["provider_write_enabled"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

    assert after["event_count"] == before + 1
    event_types = [event["event_type"] for event in after["events"]]
    assert "OWNER_REVIEW_OBSERVED" in event_types

    assert current["selected_provider_id"] is None
    assert current["recommended_provider_id"] is None
    assert current["provider_configured"] is False
    assert current["provider_read_enabled"] is False
    assert current["provider_write_enabled"] is False
    assert current["vault_done"] is False


def test_gp055_validation_passes_locked_real_decision_record(decision_db):
    validation = validate_storage_provider_decision_record(decision_db)

    assert validation["pack"]["id"] == "VAULT_GP055"
    assert validation["validation_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["passed_count"] == validation["check_count"]
    assert validation["real_sqlite_backed"] is True
    assert validation["safe_to_continue_to_gp056"] is True

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_DECISION_RECORD_EXISTS" in codes
    assert "SOURCE_GP054_ATTACHED" in codes
    assert "NO_PROVIDER_RECOMMENDED" in codes
    assert "NO_PROVIDER_SELECTED" in codes
    assert "NO_PROVIDER_CONFIGURED" in codes
    assert "NO_PROVIDER_READ_ENABLED" in codes
    assert "NO_PROVIDER_WRITE_ENABLED" in codes
    assert "NO_EXPORT" in codes
    assert "NO_EXECUTION" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "EVENT_LOG_EXISTS" in codes


def test_gp055_home_payload_has_truth_routes_and_next_step(decision_db):
    home = get_real_storage_provider_decision_record_home(decision_db)

    assert home["pack"]["id"] == "VAULT_GP055"
    assert home["decision_truth"]["real_storage_provider_decision_record_ready"] is True
    assert home["decision_truth"]["real_sqlite_backed"] is True
    assert home["decision_truth"]["real_schema_ready"] is True
    assert home["decision_truth"]["real_decision_record_exists"] is True
    assert home["decision_truth"]["real_event_log_exists"] is True
    assert home["decision_truth"]["source_gp054_attached"] is True
    assert home["decision_truth"]["validation_passed"] is True
    assert home["decision_truth"]["provider_candidate_count"] == 5
    assert home["decision_truth"]["provider_recommended"] is False
    assert home["decision_truth"]["provider_selected"] is False
    assert home["decision_truth"]["provider_configured"] is False
    assert home["decision_truth"]["provider_read_enabled"] is False
    assert home["decision_truth"]["provider_write_enabled"] is False
    assert home["decision_truth"]["export_enabled"] is False
    assert home["decision_truth"]["execution_enabled"] is False
    assert home["decision_truth"]["vault_done"] is False

    routes = home["routes"]
    assert routes["route"] == "/vault/real-storage-provider-decision-record"
    assert routes["json_route"] == "/vault/real-storage-provider-decision-record.json"
    assert routes["records_route"] == "/vault/storage-provider-decision-records.json"
    assert routes["current_record_route"] == "/vault/storage-provider-current-decision-record.json"
    assert routes["events_route"] == "/vault/storage-provider-decision-events.json"
    assert routes["validation_route"] == "/vault/storage-provider-decision-validation.json"
    assert routes["next_step_route"] == "/vault/storage-provider-decision-next-step.json"
    assert routes["gp055_status_route"] == "/vault/gp055-status.json"

    assert home["next_step"]["next_pack"] == "VAULT_GP056_REAL_STORAGE_PROVIDER_SELECTION_REGISTRY"
    assert home["next_step"]["safe_to_continue_to_gp056"] is True
    assert home["next_step"]["vault_done"] is False
    assert home["next_step"]["clouds_should_continue"] is False


def test_gp055_status_ready_real_and_locked(decision_db):
    status = get_gp055_status(decision_db)
    gp055 = status["gp055_status"]

    assert status["pack"]["id"] == "VAULT_GP055"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert status["pack"]["section_range"] == "GP051-GP060"

    assert gp055["ready"] is True
    assert gp055["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp055["section_title"] == "Archive Vault — Storage Provider Prep Layer"
    assert gp055["section_range"] == "GP051-GP060"
    assert gp055["real_storage_provider_decision_record_ready"] is True
    assert gp055["real_sqlite_backed"] is True
    assert gp055["real_schema_ready"] is True
    assert gp055["real_record_count"] == 1
    assert gp055["real_event_count"] >= 3
    assert gp055["source_gp054_attached"] is True
    assert gp055["validation_ready"] is True
    assert gp055["validation_passed"] is True
    assert gp055["safe_to_continue_to_gp056"] is True
    assert gp055["vault_done"] is False
    assert gp055["foundation_status"] == "safe_to_continue_not_done"
    assert gp055["provider_recommended"] is False
    assert gp055["provider_selected"] is False
    assert gp055["provider_configured"] is False
    assert gp055["provider_write_enabled"] is False
    assert gp055["provider_read_enabled"] is False
    assert gp055["provider_object_read_claimed"] is False
    assert gp055["provider_connection_tested"] is False
    assert gp055["risk_accepted"] is False
    assert gp055["risk_waived"] is False
    assert gp055["mitigation_approved"] is False
    assert gp055["object_body_view_enabled"] is False
    assert gp055["direct_upload_enabled"] is False
    assert gp055["export_enabled"] is False
    assert gp055["execution_enabled"] is False
    assert gp055["clouds_status"] == "parked_do_not_continue_from_vault_gp055"
    assert gp055["next_pack"] == "VAULT_GP056_REAL_STORAGE_PROVIDER_SELECTION_REGISTRY"


def test_gp055_next_step_says_continue_real_vault_not_clouds():
    next_step = get_storage_provider_decision_next_step()["next_step"]

    assert next_step["next_pack"] == "VAULT_GP056_REAL_STORAGE_PROVIDER_SELECTION_REGISTRY"
    assert next_step["next_pack_title"] == "Real Storage Provider Selection Registry"
    assert next_step["safe_to_continue_to_gp056"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

    note = next_step["owner_notebook_note"].lower()
    assert "keep vault real and durable" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "real sqlite decision records" in rules
    assert "real decision events" in rules
    assert "real provider selection registry" in rules
    assert "do not recommend a provider yet" in rules
    assert "do not select a provider yet" in rules
    assert "not vault done" in rules


def test_gp055_html_is_dark_and_mentions_real_decision_record(monkeypatch, tmp_path):
    db_path = tmp_path / "html_decision.sqlite"
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(db_path))

    html = render_real_storage_provider_decision_record_page()
    lowered = html.lower()

    assert "Vault Real Storage Provider Decision Record" in html
    assert "Storage Provider Prep Layer" in html
    assert "Archive Vault" in html
    assert "GP055" in html
    assert "Real SQLite-backed" in html
    assert "Real decision record" in html
    assert "Real event log" in html
    assert "No provider selected" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-storage-provider-decision-record.json" in html
    assert "/vault/gp055-status.json" in html

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


def test_gp055_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/real-storage-provider-decision-record",
        "/vault/real-storage-provider-decision-record.json",
        "/vault/storage-provider-decision-records.json",
        "/vault/storage-provider-current-decision-record.json",
        "/vault/storage-provider-decision-events.json",
        "/vault/storage-provider-decision-validation.json",
        "/vault/storage-provider-decision-next-step.json",
        "/vault/gp055-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp055_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "routes_decision.sqlite"))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/real-storage-provider-decision-record",
        "/vault/real-storage-provider-decision-record.json",
        "/vault/storage-provider-decision-records.json",
        "/vault/storage-provider-current-decision-record.json",
        "/vault/storage-provider-decision-events.json",
        "/vault/storage-provider-decision-validation.json",
        "/vault/storage-provider-decision-next-step.json",
        "/vault/gp055-status.json",
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
                assert b"Vault Real Storage Provider Decision Record" in response.data
