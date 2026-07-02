"""
Tests for VAULT GIANT PACK 060 — Storage Provider Prep Readiness Checkpoint
"""

from pathlib import Path

import pytest

from vault.storage_provider_prep_readiness_checkpoint_service import (
    COMPONENT_SPECS,
    DEFAULT_READINESS_CHECKPOINT_ID,
    ensure_storage_provider_prep_readiness_schema,
    get_gp060_status,
    get_storage_provider_prep_readiness_blockers,
    get_storage_provider_prep_readiness_checkpoint_home,
    get_storage_provider_prep_readiness_checkpoint_record,
    get_storage_provider_prep_readiness_components,
    get_storage_provider_prep_readiness_events,
    get_storage_provider_prep_readiness_next_step,
    initialize_storage_provider_prep_readiness_checkpoint,
    record_storage_provider_prep_readiness_event,
    render_storage_provider_prep_readiness_checkpoint_page,
    validate_storage_provider_prep_readiness_checkpoint,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BLOCKERS = 140
EXPECTED_COMPONENTS = len(COMPONENT_SPECS)


@pytest.fixture()
def readiness_db(tmp_path, monkeypatch):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "selection_registry.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "capability_contract.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "risk_criteria_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "selection_review_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "prep_readiness.sqlite"))
    return str(tmp_path / "prep_readiness.sqlite")


def test_gp060_schema_is_real_sqlite_backed(readiness_db):
    result = ensure_storage_provider_prep_readiness_schema(readiness_db)
    db_path = Path(result["db_path"])

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert db_path.exists()
    assert "vault_storage_provider_prep_readiness_checkpoints" in result["tables"]
    assert "vault_storage_provider_prep_readiness_components" in result["tables"]
    assert "vault_storage_provider_prep_readiness_blockers" in result["tables"]
    assert "vault_storage_provider_prep_readiness_events" in result["tables"]


def test_gp060_initialize_creates_real_checkpoint_components_blockers_events(readiness_db):
    result = initialize_storage_provider_prep_readiness_checkpoint(readiness_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["checkpoint_id"] == DEFAULT_READINESS_CHECKPOINT_ID
    assert result["checkpoint_count"] == 1
    assert result["component_count"] == EXPECTED_COMPONENTS
    assert result["blocker_count"] == EXPECTED_BLOCKERS
    assert result["event_count"] >= 5

    second = initialize_storage_provider_prep_readiness_checkpoint(readiness_db)
    assert second["checkpoint_count"] == 1
    assert second["component_count"] == EXPECTED_COMPONENTS
    assert second["blocker_count"] == EXPECTED_BLOCKERS
    assert second["event_count"] >= 5


def test_gp060_checkpoint_record_is_real_and_sourced_from_gp059(readiness_db):
    checkpoint = get_storage_provider_prep_readiness_checkpoint_record(readiness_db)["checkpoint"]

    assert checkpoint["checkpoint_id"] == DEFAULT_READINESS_CHECKPOINT_ID
    assert checkpoint["pack_id"] == "VAULT_GP060"
    assert checkpoint["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert checkpoint["section_range"] == "GP051-GP060"
    assert checkpoint["source_review_receipt_id"] == "VSPRR-GP059-001"
    assert checkpoint["source_review_receipt_pack_id"] == "VAULT_GP059"
    assert checkpoint["checkpoint_status"] == "REAL_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_COMPLETE_LOCKED"
    assert checkpoint["tower_authority_status"] == "TOWER_REVIEW_REQUIRED_NOT_GRANTED"

    data = checkpoint["readiness_data"]
    assert data["checkpoint_type"] == "REAL_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT"
    assert data["real_durable_checkpoint"] is True
    assert data["metadata_source"] == "VAULT_GP059_REAL_PROVIDER_SELECTION_REVIEW_RECEIPT"
    assert data["source_review_receipt_id"] == "VSPRR-GP059-001"
    assert data["source_review_receipt_pack_id"] == "VAULT_GP059"
    assert data["section_closed"] is True
    assert data["prep_layer_complete"] is True
    assert data["readiness_score"] == 100
    assert data["component_count"] == EXPECTED_COMPONENTS
    assert data["blocker_count"] == EXPECTED_BLOCKERS
    assert data["safe_to_continue_to_gp061"] is True


def test_gp060_checkpoint_closes_prep_but_keeps_provider_operations_locked(readiness_db):
    checkpoint = get_storage_provider_prep_readiness_checkpoint_record(readiness_db)["checkpoint"]

    assert checkpoint["prep_layer_complete"] is True
    assert checkpoint["readiness_score"] == 100
    assert checkpoint["safe_to_continue_to_gp061"] is True

    assert checkpoint["provider_approval_ready"] is False
    assert checkpoint["provider_activation_ready"] is False
    assert checkpoint["provider_configuration_ready"] is False
    assert checkpoint["provider_read_write_ready"] is False
    assert checkpoint["provider_approved"] is False
    assert checkpoint["provider_activated"] is False
    assert checkpoint["provider_recommended"] is False
    assert checkpoint["provider_selected"] is False
    assert checkpoint["provider_configured"] is False
    assert checkpoint["provider_read_enabled"] is False
    assert checkpoint["provider_write_enabled"] is False
    assert checkpoint["provider_object_read_claimed"] is False
    assert checkpoint["provider_connection_tested"] is False
    assert checkpoint["risk_accepted"] is False
    assert checkpoint["risk_waived"] is False
    assert checkpoint["mitigation_approved"] is False
    assert checkpoint["official_storage_receipt"] is False
    assert checkpoint["finalized_storage_receipt"] is False
    assert checkpoint["closed_storage_receipt"] is False
    assert checkpoint["object_body_view_enabled"] is False
    assert checkpoint["direct_upload_enabled"] is False
    assert checkpoint["export_enabled"] is False
    assert checkpoint["execution_enabled"] is False
    assert checkpoint["vault_done"] is False


def test_gp060_components_are_real_ready_and_locked(readiness_db):
    payload = get_storage_provider_prep_readiness_components(readiness_db)

    assert payload["pack"]["id"] == "VAULT_GP060"
    assert payload["real_sqlite_backed"] is True
    assert payload["component_count"] == EXPECTED_COMPONENTS
    assert payload["real_sqlite_backed_count"] == EXPECTED_COMPONENTS
    assert payload["component_ready_count"] == EXPECTED_COMPONENTS
    assert payload["tower_locked_count"] == EXPECTED_COMPONENTS
    assert payload["provider_approval_unlocked_count"] == 0
    assert payload["provider_activation_unlocked_count"] == 0
    assert payload["export_unlocked_count"] == 0
    assert payload["execution_unlocked_count"] == 0

    component_codes = {item["component_code"] for item in payload["components"]}
    expected_codes = {item["component_code"] for item in COMPONENT_SPECS}
    assert component_codes == expected_codes

    for item in payload["components"]:
        assert item["component_id"].startswith("VSPPC-")
        assert item["checkpoint_id"] == DEFAULT_READINESS_CHECKPOINT_ID
        assert item["component_status"] == "REAL_COMPONENT_READY_FOR_PREP_SECTION_CLOSE_TOWER_LOCKED"
        assert item["real_sqlite_backed"] is True
        assert item["component_ready"] is True
        assert item["tower_locked"] is True
        assert item["provider_approval_unlocked"] is False
        assert item["provider_activation_unlocked"] is False
        assert item["export_unlocked"] is False
        assert item["execution_unlocked"] is False


def test_gp060_blockers_are_real_and_preserved(readiness_db):
    payload = get_storage_provider_prep_readiness_blockers(readiness_db)

    assert payload["pack"]["id"] == "VAULT_GP060"
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
        assert item["blocker_id"].startswith("VSPPB-")
        assert item["checkpoint_id"] == DEFAULT_READINESS_CHECKPOINT_ID
        assert item["source_receipt_line_id"].startswith("VSPRL-")
        assert item["source_finding_id"].startswith("VSPRCF-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["blocker_status"] == "REAL_PREP_READINESS_BLOCKER_ACTIVE_CARRIED_FROM_GP059"
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


def test_gp060_event_log_is_real_and_seeded(readiness_db):
    events = get_storage_provider_prep_readiness_events(readiness_db)

    assert events["pack"]["id"] == "VAULT_GP060"
    assert events["real_sqlite_backed"] is True
    assert events["event_count"] >= 5

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_CREATED" in event_types
    assert "SOURCE_GP059_REVIEW_RECEIPT_ATTACHED" in event_types
    assert "REAL_READINESS_COMPONENTS_CREATED" in event_types
    assert "REAL_READINESS_BLOCKERS_CARRIED_FORWARD" in event_types
    assert "SECTION_GP051_GP060_CLOSED_FOR_PREP_ONLY" in event_types

    for event in events["events"]:
        assert event["event_id"].startswith("VSPPE-")
        assert event["checkpoint_id"] == DEFAULT_READINESS_CHECKPOINT_ID
        assert isinstance(event["event_payload"], dict)
        assert event["created_at"]


def test_gp060_can_write_real_event_without_unlocking_provider(readiness_db):
    before = get_storage_provider_prep_readiness_events(readiness_db)["event_count"]

    written = record_storage_provider_prep_readiness_event(
        "OWNER_GP060_SECTION_CLOSE_OBSERVED",
        {"reviewer": "owner", "note": "reviewed real GP060 section checkpoint"},
        readiness_db,
    )

    after = get_storage_provider_prep_readiness_events(readiness_db)
    checkpoint = get_storage_provider_prep_readiness_checkpoint_record(readiness_db)["checkpoint"]
    blockers = get_storage_provider_prep_readiness_blockers(readiness_db)

    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPPE-")
    assert written["checkpoint_id"] == DEFAULT_READINESS_CHECKPOINT_ID
    assert written["real_sqlite_backed"] is True
    assert written["prep_layer_complete"] is True
    assert written["safe_to_continue_to_gp061"] is True
    assert written["provider_approval_ready"] is False
    assert written["provider_activation_ready"] is False
    assert written["provider_selected"] is False
    assert written["provider_configured"] is False
    assert written["provider_read_enabled"] is False
    assert written["provider_write_enabled"] is False
    assert written["export_enabled"] is False
    assert written["execution_enabled"] is False
    assert written["vault_done"] is False

    assert after["event_count"] == before + 1
    assert "OWNER_GP060_SECTION_CLOSE_OBSERVED" in {event["event_type"] for event in after["events"]}

    assert checkpoint["prep_layer_complete"] is True
    assert checkpoint["provider_approved"] is False
    assert checkpoint["provider_activated"] is False
    assert checkpoint["provider_selected"] is False
    assert checkpoint["provider_configured"] is False
    assert checkpoint["vault_done"] is False

    assert blockers["resolved_count"] == 0
    assert blockers["blocks_execution_count"] == EXPECTED_BLOCKERS


def test_gp060_validation_passes_real_section_checkpoint(readiness_db):
    validation = validate_storage_provider_prep_readiness_checkpoint(readiness_db)

    assert validation["pack"]["id"] == "VAULT_GP060"
    assert validation["validation_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["passed_count"] == validation["check_count"]
    assert validation["real_sqlite_backed"] is True
    assert validation["section_closed"] is True
    assert validation["safe_to_continue_to_gp061"] is True

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_READINESS_CHECKPOINT_EXISTS" in codes
    assert "SOURCE_GP059_REVIEW_RECEIPT_ATTACHED" in codes
    assert "PREP_LAYER_COMPLETE" in codes
    assert "READINESS_SCORE_100_FOR_PREP_LAYER_ONLY" in codes
    assert "SAFE_TO_CONTINUE_TO_GP061" in codes
    assert "REAL_COMPONENT_ROWS_EXIST" in codes
    assert "REAL_BLOCKER_ROWS_CARRIED_FORWARD" in codes
    assert "ALL_BLOCKERS_BLOCK_PROVIDER_APPROVAL" in codes
    assert "ALL_BLOCKERS_BLOCK_PROVIDER_ACTIVATION" in codes
    assert "ALL_BLOCKERS_BLOCK_EXPORT" in codes
    assert "ALL_BLOCKERS_BLOCK_EXECUTION" in codes
    assert "NO_PROVIDER_APPROVAL_READY" in codes
    assert "NO_PROVIDER_ACTIVATION_READY" in codes
    assert "NO_PROVIDER_APPROVED" in codes
    assert "NO_PROVIDER_SELECTED" in codes
    assert "NO_OFFICIAL_STORAGE_RECEIPT" in codes
    assert "NO_EXPORT" in codes
    assert "NO_EXECUTION" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "EVENT_LOG_EXISTS" in codes


def test_gp060_home_payload_has_truth_routes_and_next_step(readiness_db):
    home = get_storage_provider_prep_readiness_checkpoint_home(readiness_db)

    assert home["pack"]["id"] == "VAULT_GP060"
    assert home["readiness_truth"]["storage_provider_prep_readiness_checkpoint_ready"] is True
    assert home["readiness_truth"]["real_sqlite_backed"] is True
    assert home["readiness_truth"]["real_schema_ready"] is True
    assert home["readiness_truth"]["real_checkpoint_exists"] is True
    assert home["readiness_truth"]["real_component_rows_exist"] is True
    assert home["readiness_truth"]["real_blocker_rows_exist"] is True
    assert home["readiness_truth"]["real_event_log_exists"] is True
    assert home["readiness_truth"]["source_gp059_review_receipt_attached"] is True
    assert home["readiness_truth"]["section_closed"] is True
    assert home["readiness_truth"]["prep_layer_complete"] is True
    assert home["readiness_truth"]["readiness_score"] == 100
    assert home["readiness_truth"]["safe_to_continue_to_gp061"] is True
    assert home["readiness_truth"]["provider_approval_ready"] is False
    assert home["readiness_truth"]["provider_activation_ready"] is False
    assert home["readiness_truth"]["provider_selected"] is False
    assert home["readiness_truth"]["provider_configured"] is False
    assert home["readiness_truth"]["export_enabled"] is False
    assert home["readiness_truth"]["execution_enabled"] is False
    assert home["readiness_truth"]["vault_done"] is False

    routes = home["routes"]
    assert routes["route"] == "/vault/storage-provider-prep-readiness-checkpoint"
    assert routes["json_route"] == "/vault/storage-provider-prep-readiness-checkpoint.json"
    assert routes["record_route"] == "/vault/storage-provider-prep-readiness-record.json"
    assert routes["components_route"] == "/vault/storage-provider-prep-readiness-components.json"
    assert routes["blockers_route"] == "/vault/storage-provider-prep-readiness-blockers.json"
    assert routes["events_route"] == "/vault/storage-provider-prep-readiness-events.json"
    assert routes["validation_route"] == "/vault/storage-provider-prep-readiness-validation.json"
    assert routes["next_step_route"] == "/vault/storage-provider-prep-readiness-next-step.json"
    assert routes["gp060_status_route"] == "/vault/gp060-status.json"

    assert home["next_step"]["current_section_closed"] is True
    assert home["next_step"]["next_pack"] == "VAULT_GP061_REAL_STORAGE_PROVIDER_CONFIG_CONTRACT"
    assert home["next_step"]["safe_to_continue_to_gp061"] is True
    assert home["next_step"]["vault_done"] is False
    assert home["next_step"]["clouds_should_continue"] is False


def test_gp060_status_ready_real_section_closed_and_locked(readiness_db):
    status = get_gp060_status(readiness_db)
    gp060 = status["gp060_status"]

    assert status["pack"]["id"] == "VAULT_GP060"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert status["pack"]["section_range"] == "GP051-GP060"

    assert gp060["ready"] is True
    assert gp060["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp060["section_title"] == "Archive Vault — Storage Provider Prep Layer"
    assert gp060["section_range"] == "GP051-GP060"
    assert gp060["storage_provider_prep_readiness_checkpoint_ready"] is True
    assert gp060["section_closed"] is True
    assert gp060["real_sqlite_backed"] is True
    assert gp060["real_schema_ready"] is True
    assert gp060["real_checkpoint_count"] == 1
    assert gp060["real_component_count"] == EXPECTED_COMPONENTS
    assert gp060["real_blocker_count"] == EXPECTED_BLOCKERS
    assert gp060["real_event_count"] >= 5
    assert gp060["source_gp059_review_receipt_attached"] is True
    assert gp060["prep_layer_complete"] is True
    assert gp060["readiness_score"] == 100
    assert gp060["component_ready_count"] == EXPECTED_COMPONENTS
    assert gp060["tower_locked_component_count"] == EXPECTED_COMPONENTS
    assert gp060["capability_blocker_count"] == 60
    assert gp060["criteria_blocker_count"] == 40
    assert gp060["risk_blocker_count"] == 40
    assert gp060["blocks_provider_approval_count"] == EXPECTED_BLOCKERS
    assert gp060["blocks_provider_activation_count"] == EXPECTED_BLOCKERS
    assert gp060["blocks_export_count"] == EXPECTED_BLOCKERS
    assert gp060["blocks_execution_count"] == EXPECTED_BLOCKERS
    assert gp060["tower_review_granted_count"] == 0
    assert gp060["resolved_count"] == 0
    assert gp060["validation_ready"] is True
    assert gp060["validation_passed"] is True
    assert gp060["safe_to_continue_to_gp061"] is True
    assert gp060["vault_done"] is False
    assert gp060["foundation_status"] == "section_closed_safe_to_continue_not_done"
    assert gp060["next_section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert gp060["next_section_range"] == "GP061-GP070"

    assert gp060["provider_approval_ready"] is False
    assert gp060["provider_activation_ready"] is False
    assert gp060["provider_configuration_ready"] is False
    assert gp060["provider_read_write_ready"] is False
    assert gp060["provider_approved"] is False
    assert gp060["provider_activated"] is False
    assert gp060["provider_recommended"] is False
    assert gp060["provider_selected"] is False
    assert gp060["provider_configured"] is False
    assert gp060["provider_write_enabled"] is False
    assert gp060["provider_read_enabled"] is False
    assert gp060["provider_object_read_claimed"] is False
    assert gp060["provider_connection_tested"] is False
    assert gp060["risk_accepted"] is False
    assert gp060["risk_waived"] is False
    assert gp060["mitigation_approved"] is False
    assert gp060["official_storage_receipt"] is False
    assert gp060["finalized_storage_receipt"] is False
    assert gp060["closed_storage_receipt"] is False
    assert gp060["object_body_view_enabled"] is False
    assert gp060["direct_upload_enabled"] is False
    assert gp060["export_enabled"] is False
    assert gp060["execution_enabled"] is False
    assert gp060["clouds_status"] == "parked_do_not_continue_from_vault_gp060"
    assert gp060["next_pack"] == "VAULT_GP061_REAL_STORAGE_PROVIDER_CONFIG_CONTRACT"


def test_gp060_next_step_closes_section_and_points_to_gp061():
    next_step = get_storage_provider_prep_readiness_next_step()["next_step"]

    assert next_step["current_section_closed"] is True
    assert next_step["closed_section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert next_step["closed_section_range"] == "GP051-GP060"
    assert next_step["next_section"] == "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
    assert next_step["next_section_range"] == "GP061-GP070"
    assert next_step["next_pack"] == "VAULT_GP061_REAL_STORAGE_PROVIDER_CONFIG_CONTRACT"
    assert next_step["next_pack_title"] == "Real Storage Provider Config Contract"
    assert next_step["safe_to_continue_to_gp061"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

    note = next_step["owner_notebook_note"].lower()
    assert "gp051-gp060 is closed" in note
    assert "continue to gp061" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "storage provider prep layer is complete" in rules
    assert "real sqlite prep readiness checkpoint" in rules
    assert "real blocker rows" in rules
    assert "provider approval blocked" in rules
    assert "provider activation blocked" in rules
    assert "build gp061 real storage provider config contract next" in rules
    assert "do not treat vault as done" in rules


def test_gp060_html_is_dark_and_mentions_section_close(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "html_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "html_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "html_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "html_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "html_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "html_readiness.sqlite"))

    html = render_storage_provider_prep_readiness_checkpoint_page()
    lowered = html.lower()

    assert "Vault Storage Provider Prep Readiness Checkpoint" in html
    assert "Storage Provider Prep Layer" in html
    assert "Archive Vault" in html
    assert "GP060" in html
    assert "Section closed" in html
    assert "Safe to GP061" in html
    assert "Real SQLite-backed" in html
    assert "No provider approved" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/storage-provider-prep-readiness-checkpoint.json" in html
    assert "/vault/gp060-status.json" in html

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


def test_gp060_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-provider-prep-readiness-checkpoint",
        "/vault/storage-provider-prep-readiness-checkpoint.json",
        "/vault/storage-provider-prep-readiness-record.json",
        "/vault/storage-provider-prep-readiness-components.json",
        "/vault/storage-provider-prep-readiness-blockers.json",
        "/vault/storage-provider-prep-readiness-events.json",
        "/vault/storage-provider-prep-readiness-validation.json",
        "/vault/storage-provider-prep-readiness-next-step.json",
        "/vault/gp060-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp060_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "routes_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "routes_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "routes_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "routes_validation.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB", str(tmp_path / "routes_receipt.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB", str(tmp_path / "routes_readiness.sqlite"))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-provider-prep-readiness-checkpoint",
        "/vault/storage-provider-prep-readiness-checkpoint.json",
        "/vault/storage-provider-prep-readiness-record.json",
        "/vault/storage-provider-prep-readiness-components.json",
        "/vault/storage-provider-prep-readiness-blockers.json",
        "/vault/storage-provider-prep-readiness-events.json",
        "/vault/storage-provider-prep-readiness-validation.json",
        "/vault/storage-provider-prep-readiness-next-step.json",
        "/vault/gp060-status.json",
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
                assert b"Vault Storage Provider Prep Readiness Checkpoint" in response.data
