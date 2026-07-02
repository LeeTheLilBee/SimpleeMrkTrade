"""
Tests for VAULT GIANT PACK 059 — Real Provider Selection Review Receipt
"""

from pathlib import Path

import pytest

from vault.real_provider_selection_review_receipt_service import (
    DEFAULT_REVIEW_RECEIPT_ID,
    ensure_provider_selection_review_receipt_schema,
    get_gp059_status,
    get_provider_selection_review_receipt_events,
    get_provider_selection_review_receipt_lines,
    get_provider_selection_review_receipt_next_step,
    get_provider_selection_review_receipt_record,
    get_real_provider_selection_review_receipt_home,
    initialize_real_provider_selection_review_receipt,
    record_provider_selection_review_receipt_event,
    render_real_provider_selection_review_receipt_page,
    validate_provider_selection_review_receipt,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TOTAL_LINES = 140
EXPECTED_CAPABILITY_LINES = 60
EXPECTED_CRITERIA_LINES = 40
EXPECTED_RISK_LINES = 40


@pytest.fixture()
def receipt_db(tmp_path, monkeypatch):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "selection_registry.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "capability_contract.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "risk_criteria_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "selection_review_receipt.sqlite"))
    return str(tmp_path / "selection_review_receipt.sqlite")


def test_gp059_schema_is_real_sqlite_backed(receipt_db):
    result = ensure_provider_selection_review_receipt_schema(receipt_db)
    db_path = Path(result["db_path"])

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert db_path.exists()
    assert "vault_provider_selection_review_receipts" in result["tables"]
    assert "vault_provider_selection_review_receipt_lines" in result["tables"]
    assert "vault_provider_selection_review_receipt_events" in result["tables"]


def test_gp059_initialize_creates_real_receipt_lines_and_event_log(receipt_db):
    result = initialize_real_provider_selection_review_receipt(receipt_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["receipt_id"] == DEFAULT_REVIEW_RECEIPT_ID
    assert result["receipt_count"] == 1
    assert result["receipt_line_count"] == EXPECTED_TOTAL_LINES
    assert result["event_count"] >= 4

    second = initialize_real_provider_selection_review_receipt(receipt_db)
    assert second["receipt_count"] == 1
    assert second["receipt_line_count"] == EXPECTED_TOTAL_LINES
    assert second["event_count"] >= 4


def test_gp059_receipt_record_is_real_and_sourced_from_gp058(receipt_db):
    receipt = get_provider_selection_review_receipt_record(receipt_db)["receipt"]

    assert receipt["receipt_id"] == DEFAULT_REVIEW_RECEIPT_ID
    assert receipt["pack_id"] == "VAULT_GP059"
    assert receipt["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert receipt["section_range"] == "GP051-GP060"
    assert receipt["source_validation_run_id"] == "VSPRCV-GP058-001"
    assert receipt["source_validation_pack_id"] == "VAULT_GP058"
    assert receipt["receipt_status"] == "REAL_PROVIDER_SELECTION_REVIEW_RECEIPT_OPEN_TOWER_LOCKED"
    assert receipt["tower_authority_status"] == "TOWER_REVIEW_REQUIRED_NOT_GRANTED"

    data = receipt["receipt_data"]
    assert data["receipt_type"] == "REAL_PROVIDER_SELECTION_REVIEW_RECEIPT"
    assert data["real_durable_receipt"] is True
    assert data["internal_review_receipt"] is True
    assert data["official_receipt"] is False
    assert data["finalized_receipt"] is False
    assert data["closed_receipt"] is False
    assert data["metadata_source"] == "VAULT_GP058_REAL_PROVIDER_RISK_CRITERIA_VALIDATION_ENGINE"
    assert data["source_validation_run_id"] == "VSPRCV-GP058-001"
    assert data["source_validation_pack_id"] == "VAULT_GP058"
    assert data["provider_candidate_count"] == 5
    assert data["receipt_line_count"] == EXPECTED_TOTAL_LINES
    assert data["capability_line_count"] == EXPECTED_CAPABILITY_LINES
    assert data["criteria_line_count"] == EXPECTED_CRITERIA_LINES
    assert data["risk_line_count"] == EXPECTED_RISK_LINES
    assert data["safe_to_continue_to_gp060"] is True


def test_gp059_receipt_keeps_all_unsafe_operations_locked(receipt_db):
    receipt = get_provider_selection_review_receipt_record(receipt_db)["receipt"]

    assert receipt["internal_review_receipt"] is True
    assert receipt["official_receipt"] is False
    assert receipt["finalized_receipt"] is False
    assert receipt["closed_receipt"] is False
    assert receipt["provider_approved"] is False
    assert receipt["provider_activated"] is False
    assert receipt["provider_recommended"] is False
    assert receipt["provider_selected"] is False
    assert receipt["provider_configured"] is False
    assert receipt["provider_read_enabled"] is False
    assert receipt["provider_write_enabled"] is False
    assert receipt["provider_object_read_claimed"] is False
    assert receipt["provider_connection_tested"] is False
    assert receipt["risk_accepted"] is False
    assert receipt["risk_waived"] is False
    assert receipt["mitigation_approved"] is False
    assert receipt["object_body_view_enabled"] is False
    assert receipt["direct_upload_enabled"] is False
    assert receipt["export_enabled"] is False
    assert receipt["execution_enabled"] is False
    assert receipt["vault_done"] is False


def test_gp059_receipt_lines_are_real_and_blocking(receipt_db):
    payload = get_provider_selection_review_receipt_lines(receipt_db)

    assert payload["pack"]["id"] == "VAULT_GP059"
    assert payload["real_sqlite_backed"] is True
    assert payload["receipt_line_count"] == EXPECTED_TOTAL_LINES
    assert payload["capability_line_count"] == EXPECTED_CAPABILITY_LINES
    assert payload["criteria_line_count"] == EXPECTED_CRITERIA_LINES
    assert payload["risk_line_count"] == EXPECTED_RISK_LINES

    assert payload["blocks_provider_approval_count"] == EXPECTED_TOTAL_LINES
    assert payload["blocks_provider_activation_count"] == EXPECTED_TOTAL_LINES
    assert payload["blocks_provider_selection_count"] == EXPECTED_TOTAL_LINES
    assert payload["blocks_provider_configuration_count"] == EXPECTED_TOTAL_LINES
    assert payload["blocks_provider_read_write_count"] == EXPECTED_TOTAL_LINES
    assert payload["blocks_object_body_view_count"] == EXPECTED_TOTAL_LINES
    assert payload["blocks_export_count"] == EXPECTED_TOTAL_LINES
    assert payload["blocks_execution_count"] == EXPECTED_TOTAL_LINES
    assert payload["tower_review_required_count"] == EXPECTED_TOTAL_LINES
    assert payload["tower_review_granted_count"] == 0
    assert payload["risk_accepted_count"] == 0
    assert payload["risk_waived_count"] == 0
    assert payload["mitigation_approved_count"] == 0
    assert payload["resolved_count"] == 0
    assert payload["official_receipt_line_count"] == 0
    assert payload["finalized_receipt_line_count"] == 0
    assert payload["closed_receipt_line_count"] == 0

    categories = {item["line_category"] for item in payload["lines"]}
    assert categories == {"capability_contract", "criteria_validation", "risk_validation"}

    for item in payload["lines"]:
        assert item["receipt_line_id"].startswith("VSPRL-")
        assert item["receipt_id"] == DEFAULT_REVIEW_RECEIPT_ID
        assert item["source_finding_id"].startswith("VSPRCF-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["severity"] in {"critical", "high"}
        assert item["line_status"] == "REAL_REVIEW_RECEIPT_LINE_RECORDED_BLOCKER_ACTIVE"
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
        assert item["official_receipt_line"] is False
        assert item["finalized_receipt_line"] is False
        assert item["closed_receipt_line"] is False


def test_gp059_event_log_is_real_and_seeded(receipt_db):
    events = get_provider_selection_review_receipt_events(receipt_db)

    assert events["pack"]["id"] == "VAULT_GP059"
    assert events["real_sqlite_backed"] is True
    assert events["event_count"] >= 4

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_PROVIDER_SELECTION_REVIEW_RECEIPT_CREATED" in event_types
    assert "SOURCE_GP058_VALIDATION_RUN_ATTACHED" in event_types
    assert "REAL_REVIEW_RECEIPT_LINES_CREATED" in event_types
    assert "TOWER_REVIEW_RECEIPT_LOCKS_CONFIRMED" in event_types

    for event in events["events"]:
        assert event["event_id"].startswith("VSPRE-")
        assert event["receipt_id"] == DEFAULT_REVIEW_RECEIPT_ID
        assert isinstance(event["event_payload"], dict)
        assert event["created_at"]


def test_gp059_can_write_real_review_event_without_closing_or_approving(receipt_db):
    before = get_provider_selection_review_receipt_events(receipt_db)["event_count"]

    written = record_provider_selection_review_receipt_event(
        "OWNER_PROVIDER_SELECTION_REVIEW_RECEIPT_OBSERVED",
        {"reviewer": "owner", "note": "reviewed real selection review receipt"},
        receipt_db,
    )

    after = get_provider_selection_review_receipt_events(receipt_db)
    receipt = get_provider_selection_review_receipt_record(receipt_db)["receipt"]
    lines = get_provider_selection_review_receipt_lines(receipt_db)

    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPRE-")
    assert written["receipt_id"] == DEFAULT_REVIEW_RECEIPT_ID
    assert written["real_sqlite_backed"] is True
    assert written["internal_review_receipt"] is True
    assert written["official_receipt"] is False
    assert written["finalized_receipt"] is False
    assert written["closed_receipt"] is False
    assert written["provider_approved"] is False
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
    assert "OWNER_PROVIDER_SELECTION_REVIEW_RECEIPT_OBSERVED" in {event["event_type"] for event in after["events"]}

    assert receipt["official_receipt"] is False
    assert receipt["finalized_receipt"] is False
    assert receipt["closed_receipt"] is False
    assert receipt["provider_approved"] is False
    assert receipt["provider_selected"] is False
    assert receipt["provider_configured"] is False
    assert receipt["vault_done"] is False

    assert lines["resolved_count"] == 0
    assert lines["blocks_execution_count"] == EXPECTED_TOTAL_LINES


def test_gp059_validation_passes_locked_real_review_receipt(receipt_db):
    validation = validate_provider_selection_review_receipt(receipt_db)

    assert validation["pack"]["id"] == "VAULT_GP059"
    assert validation["validation_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["passed_count"] == validation["check_count"]
    assert validation["real_sqlite_backed"] is True
    assert validation["safe_to_continue_to_gp060"] is True

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_REVIEW_RECEIPT_EXISTS" in codes
    assert "SOURCE_GP058_VALIDATION_RUN_ATTACHED" in codes
    assert "REAL_REVIEW_RECEIPT_LINES_EXIST" in codes
    assert "ALL_RECEIPT_LINES_BLOCK_PROVIDER_APPROVAL" in codes
    assert "ALL_RECEIPT_LINES_BLOCK_PROVIDER_ACTIVATION" in codes
    assert "ALL_RECEIPT_LINES_BLOCK_EXPORT" in codes
    assert "ALL_RECEIPT_LINES_BLOCK_EXECUTION" in codes
    assert "INTERNAL_REVIEW_RECEIPT_ONLY" in codes
    assert "NO_OFFICIAL_RECEIPT" in codes
    assert "NO_FINALIZED_RECEIPT" in codes
    assert "NO_CLOSED_RECEIPT" in codes
    assert "NO_PROVIDER_APPROVED" in codes
    assert "NO_PROVIDER_ACTIVATED" in codes
    assert "NO_PROVIDER_SELECTED" in codes
    assert "NO_EXPORT" in codes
    assert "NO_EXECUTION" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "EVENT_LOG_EXISTS" in codes


def test_gp059_home_payload_has_truth_routes_and_next_step(receipt_db):
    home = get_real_provider_selection_review_receipt_home(receipt_db)

    assert home["pack"]["id"] == "VAULT_GP059"
    assert home["receipt_truth"]["real_provider_selection_review_receipt_ready"] is True
    assert home["receipt_truth"]["real_sqlite_backed"] is True
    assert home["receipt_truth"]["real_schema_ready"] is True
    assert home["receipt_truth"]["real_review_receipt_exists"] is True
    assert home["receipt_truth"]["real_receipt_lines_exist"] is True
    assert home["receipt_truth"]["real_event_log_exists"] is True
    assert home["receipt_truth"]["source_gp058_validation_run_attached"] is True
    assert home["receipt_truth"]["validation_passed"] is True
    assert home["receipt_truth"]["receipt_line_count"] == EXPECTED_TOTAL_LINES
    assert home["receipt_truth"]["capability_line_count"] == EXPECTED_CAPABILITY_LINES
    assert home["receipt_truth"]["criteria_line_count"] == EXPECTED_CRITERIA_LINES
    assert home["receipt_truth"]["risk_line_count"] == EXPECTED_RISK_LINES
    assert home["receipt_truth"]["internal_review_receipt"] is True
    assert home["receipt_truth"]["official_receipt"] is False
    assert home["receipt_truth"]["finalized_receipt"] is False
    assert home["receipt_truth"]["closed_receipt"] is False
    assert home["receipt_truth"]["provider_approved"] is False
    assert home["receipt_truth"]["provider_activated"] is False
    assert home["receipt_truth"]["provider_selected"] is False
    assert home["receipt_truth"]["provider_configured"] is False
    assert home["receipt_truth"]["provider_read_enabled"] is False
    assert home["receipt_truth"]["provider_write_enabled"] is False
    assert home["receipt_truth"]["export_enabled"] is False
    assert home["receipt_truth"]["execution_enabled"] is False
    assert home["receipt_truth"]["vault_done"] is False

    routes = home["routes"]
    assert routes["route"] == "/vault/real-provider-selection-review-receipt"
    assert routes["json_route"] == "/vault/real-provider-selection-review-receipt.json"
    assert routes["receipt_route"] == "/vault/provider-selection-review-receipt-record.json"
    assert routes["lines_route"] == "/vault/provider-selection-review-receipt-lines.json"
    assert routes["events_route"] == "/vault/provider-selection-review-receipt-events.json"
    assert routes["validation_route"] == "/vault/provider-selection-review-receipt-validation.json"
    assert routes["next_step_route"] == "/vault/provider-selection-review-receipt-next-step.json"
    assert routes["gp059_status_route"] == "/vault/gp059-status.json"

    assert home["next_step"]["next_pack"] == "VAULT_GP060_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT"
    assert home["next_step"]["safe_to_continue_to_gp060"] is True
    assert home["next_step"]["vault_done"] is False
    assert home["next_step"]["clouds_should_continue"] is False


def test_gp059_status_ready_real_and_locked(receipt_db):
    status = get_gp059_status(receipt_db)
    gp059 = status["gp059_status"]

    assert status["pack"]["id"] == "VAULT_GP059"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert status["pack"]["section_range"] == "GP051-GP060"

    assert gp059["ready"] is True
    assert gp059["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp059["section_title"] == "Archive Vault — Storage Provider Prep Layer"
    assert gp059["section_range"] == "GP051-GP060"
    assert gp059["real_provider_selection_review_receipt_ready"] is True
    assert gp059["real_sqlite_backed"] is True
    assert gp059["real_schema_ready"] is True
    assert gp059["real_receipt_count"] == 1
    assert gp059["real_receipt_line_count"] == EXPECTED_TOTAL_LINES
    assert gp059["real_event_count"] >= 4
    assert gp059["source_gp058_validation_run_attached"] is True
    assert gp059["capability_line_count"] == EXPECTED_CAPABILITY_LINES
    assert gp059["criteria_line_count"] == EXPECTED_CRITERIA_LINES
    assert gp059["risk_line_count"] == EXPECTED_RISK_LINES
    assert gp059["blocks_provider_approval_count"] == EXPECTED_TOTAL_LINES
    assert gp059["blocks_provider_activation_count"] == EXPECTED_TOTAL_LINES
    assert gp059["blocks_export_count"] == EXPECTED_TOTAL_LINES
    assert gp059["blocks_execution_count"] == EXPECTED_TOTAL_LINES
    assert gp059["tower_review_granted_count"] == 0
    assert gp059["resolved_count"] == 0
    assert gp059["validation_ready"] is True
    assert gp059["validation_passed"] is True
    assert gp059["safe_to_continue_to_gp060"] is True
    assert gp059["vault_done"] is False
    assert gp059["foundation_status"] == "safe_to_continue_not_done"
    assert gp059["internal_review_receipt"] is True
    assert gp059["official_receipt"] is False
    assert gp059["finalized_receipt"] is False
    assert gp059["closed_receipt"] is False
    assert gp059["provider_approved"] is False
    assert gp059["provider_activated"] is False
    assert gp059["provider_recommended"] is False
    assert gp059["provider_selected"] is False
    assert gp059["provider_configured"] is False
    assert gp059["provider_write_enabled"] is False
    assert gp059["provider_read_enabled"] is False
    assert gp059["provider_object_read_claimed"] is False
    assert gp059["provider_connection_tested"] is False
    assert gp059["risk_accepted"] is False
    assert gp059["risk_waived"] is False
    assert gp059["mitigation_approved"] is False
    assert gp059["object_body_view_enabled"] is False
    assert gp059["direct_upload_enabled"] is False
    assert gp059["export_enabled"] is False
    assert gp059["execution_enabled"] is False
    assert gp059["clouds_status"] == "parked_do_not_continue_from_vault_gp059"
    assert gp059["next_pack"] == "VAULT_GP060_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT"


def test_gp059_next_step_says_gp060_section_checkpoint_not_clouds():
    next_step = get_provider_selection_review_receipt_next_step()["next_step"]

    assert next_step["next_pack"] == "VAULT_GP060_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT"
    assert next_step["next_pack_title"] == "Storage Provider Prep Readiness Checkpoint"
    assert next_step["safe_to_continue_to_gp060"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

    note = next_step["owner_notebook_note"].lower()
    assert "gp060 should close this section" in note
    assert "real readiness checkpoint" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "real sqlite provider selection review receipt" in rules
    assert "real receipt lines sourced from gp058 findings" in rules
    assert "real storage provider prep readiness checkpoint" in rules
    assert "do not make the receipt official yet" in rules
    assert "do not approve a provider yet" in rules
    assert "do not activate a provider yet" in rules
    assert "not vault done" in rules


def test_gp059_html_is_dark_and_mentions_real_review_receipt(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "html_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "html_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "html_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "html_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "html_receipt.sqlite"))

    html = render_real_provider_selection_review_receipt_page()
    lowered = html.lower()

    assert "Vault Real Provider Selection Review Receipt" in html
    assert "Storage Provider Prep Layer" in html
    assert "Archive Vault" in html
    assert "GP059" in html
    assert "Real SQLite-backed" in html
    assert "Real receipt lines" in html
    assert "Internal review receipt" in html
    assert "No official receipt" in html
    assert "No provider approved" in html
    assert "No execution" in html
    assert "/vault/real-provider-selection-review-receipt.json" in html
    assert "/vault/gp059-status.json" in html

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


def test_gp059_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/real-provider-selection-review-receipt",
        "/vault/real-provider-selection-review-receipt.json",
        "/vault/provider-selection-review-receipt-record.json",
        "/vault/provider-selection-review-receipt-lines.json",
        "/vault/provider-selection-review-receipt-events.json",
        "/vault/provider-selection-review-receipt-validation.json",
        "/vault/provider-selection-review-receipt-next-step.json",
        "/vault/gp059-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp059_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "routes_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "routes_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "routes_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "routes_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "routes_receipt.sqlite"))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/real-provider-selection-review-receipt",
        "/vault/real-provider-selection-review-receipt.json",
        "/vault/provider-selection-review-receipt-record.json",
        "/vault/provider-selection-review-receipt-lines.json",
        "/vault/provider-selection-review-receipt-events.json",
        "/vault/provider-selection-review-receipt-validation.json",
        "/vault/provider-selection-review-receipt-next-step.json",
        "/vault/gp059-status.json",
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
                assert b"Vault Real Provider Selection Review Receipt" in response.data
