"""
Tests for VAULT GIANT PACK 058 — Real Provider Risk / Criteria Validation Engine
"""

from pathlib import Path

import pytest

from vault.real_provider_risk_criteria_validation_engine_service import (
    CRITERIA_RULES,
    DEFAULT_VALIDATION_RUN_ID,
    RISK_RULES,
    ensure_risk_criteria_validation_schema,
    get_gp058_status,
    get_provider_risk_criteria_validation_events,
    get_provider_risk_criteria_validation_findings,
    get_provider_risk_criteria_validation_next_step,
    get_provider_risk_criteria_validation_run,
    get_real_provider_risk_criteria_validation_engine_home,
    initialize_real_provider_risk_criteria_validation_engine,
    record_provider_risk_criteria_validation_review_event,
    render_real_provider_risk_criteria_validation_engine_page,
    validate_provider_risk_criteria_validation_engine,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CAPABILITY_FINDINGS = 60
EXPECTED_CRITERIA_FINDINGS = 40
EXPECTED_RISK_FINDINGS = 40
EXPECTED_TOTAL_FINDINGS = 140


@pytest.fixture()
def validation_db(tmp_path, monkeypatch):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "selection_registry.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "capability_contract.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "risk_criteria_validation.sqlite"))
    return str(tmp_path / "risk_criteria_validation.sqlite")


def test_gp058_schema_is_real_sqlite_backed(validation_db):
    result = ensure_risk_criteria_validation_schema(validation_db)
    db_path = Path(result["db_path"])

    assert result["schema_ready"] is True
    assert result["real_sqlite_backed"] is True
    assert db_path.exists()
    assert "vault_provider_risk_criteria_validation_runs" in result["tables"]
    assert "vault_provider_risk_criteria_validation_findings" in result["tables"]
    assert "vault_provider_risk_criteria_validation_events" in result["tables"]


def test_gp058_initialize_creates_real_run_findings_and_event_log(validation_db):
    result = initialize_real_provider_risk_criteria_validation_engine(validation_db)

    assert result["initialized"] is True
    assert result["real_sqlite_backed"] is True
    assert result["validation_run_id"] == DEFAULT_VALIDATION_RUN_ID
    assert result["run_count"] == 1
    assert result["finding_count"] == EXPECTED_TOTAL_FINDINGS
    assert result["event_count"] >= 4

    second = initialize_real_provider_risk_criteria_validation_engine(validation_db)
    assert second["run_count"] == 1
    assert second["finding_count"] == EXPECTED_TOTAL_FINDINGS
    assert second["event_count"] >= 4


def test_gp058_validation_run_is_real_and_sourced_from_gp057(validation_db):
    run = get_provider_risk_criteria_validation_run(validation_db)["validation_run"]

    assert run["validation_run_id"] == DEFAULT_VALIDATION_RUN_ID
    assert run["pack_id"] == "VAULT_GP058"
    assert run["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert run["section_range"] == "GP051-GP060"
    assert run["source_capability_contract_id"] == "VSPCC-GP057-001"
    assert run["source_capability_pack_id"] == "VAULT_GP057"
    assert run["run_status"] == "REAL_VALIDATION_RUN_COMPLETE_BLOCKERS_ACTIVE_TOWER_LOCKED"
    assert run["tower_authority_status"] == "TOWER_REVIEW_REQUIRED_NOT_GRANTED"

    data = run["engine_data"]
    assert data["engine_type"] == "REAL_PROVIDER_RISK_CRITERIA_VALIDATION_ENGINE"
    assert data["real_durable_validation_engine"] is True
    assert data["metadata_source"] == "VAULT_GP057_REAL_STORAGE_PROVIDER_CAPABILITY_CONTRACT"
    assert data["source_capability_contract_id"] == "VSPCC-GP057-001"
    assert data["source_capability_pack_id"] == "VAULT_GP057"
    assert data["provider_candidate_count"] == 5
    assert data["criteria_rule_count"] == len(CRITERIA_RULES)
    assert data["risk_rule_count"] == len(RISK_RULES)
    assert data["capability_finding_count"] == EXPECTED_CAPABILITY_FINDINGS
    assert data["criteria_finding_count"] == EXPECTED_CRITERIA_FINDINGS
    assert data["risk_finding_count"] == EXPECTED_RISK_FINDINGS
    assert data["total_finding_count"] == EXPECTED_TOTAL_FINDINGS
    assert data["safe_to_continue_to_gp059"] is True


def test_gp058_run_keeps_all_unsafe_operations_locked(validation_db):
    run = get_provider_risk_criteria_validation_run(validation_db)["validation_run"]

    assert run["provider_approved"] is False
    assert run["provider_activated"] is False
    assert run["provider_recommended"] is False
    assert run["provider_selected"] is False
    assert run["provider_configured"] is False
    assert run["provider_read_enabled"] is False
    assert run["provider_write_enabled"] is False
    assert run["provider_object_read_claimed"] is False
    assert run["provider_connection_tested"] is False
    assert run["risk_accepted"] is False
    assert run["risk_waived"] is False
    assert run["mitigation_approved"] is False
    assert run["object_body_view_enabled"] is False
    assert run["direct_upload_enabled"] is False
    assert run["export_enabled"] is False
    assert run["execution_enabled"] is False
    assert run["vault_done"] is False


def test_gp058_findings_are_real_and_blocking(validation_db):
    payload = get_provider_risk_criteria_validation_findings(validation_db)

    assert payload["pack"]["id"] == "VAULT_GP058"
    assert payload["real_sqlite_backed"] is True
    assert payload["finding_count"] == EXPECTED_TOTAL_FINDINGS
    assert payload["capability_finding_count"] == EXPECTED_CAPABILITY_FINDINGS
    assert payload["criteria_finding_count"] == EXPECTED_CRITERIA_FINDINGS
    assert payload["risk_finding_count"] == EXPECTED_RISK_FINDINGS

    assert payload["blocks_provider_approval_count"] == EXPECTED_TOTAL_FINDINGS
    assert payload["blocks_provider_activation_count"] == EXPECTED_TOTAL_FINDINGS
    assert payload["blocks_provider_selection_count"] == EXPECTED_TOTAL_FINDINGS
    assert payload["blocks_provider_configuration_count"] == EXPECTED_TOTAL_FINDINGS
    assert payload["blocks_provider_read_write_count"] == EXPECTED_TOTAL_FINDINGS
    assert payload["blocks_object_body_view_count"] == EXPECTED_TOTAL_FINDINGS
    assert payload["blocks_export_count"] == EXPECTED_TOTAL_FINDINGS
    assert payload["blocks_execution_count"] == EXPECTED_TOTAL_FINDINGS
    assert payload["tower_review_required_count"] == EXPECTED_TOTAL_FINDINGS
    assert payload["tower_review_granted_count"] == 0
    assert payload["risk_accepted_count"] == 0
    assert payload["risk_waived_count"] == 0
    assert payload["mitigation_approved_count"] == 0
    assert payload["resolved_count"] == 0

    categories = {item["finding_category"] for item in payload["findings"]}
    assert categories == {"capability_contract", "criteria_validation", "risk_validation"}

    for item in payload["findings"]:
        assert item["finding_id"].startswith("VSPRCF-")
        assert item["validation_run_id"] == DEFAULT_VALIDATION_RUN_ID
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["severity"] in {"critical", "high"}
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


def test_gp058_event_log_is_real_and_seeded(validation_db):
    events = get_provider_risk_criteria_validation_events(validation_db)

    assert events["pack"]["id"] == "VAULT_GP058"
    assert events["real_sqlite_backed"] is True
    assert events["event_count"] >= 4

    event_types = {event["event_type"] for event in events["events"]}
    assert "REAL_PROVIDER_RISK_CRITERIA_VALIDATION_RUN_CREATED" in event_types
    assert "SOURCE_GP057_CAPABILITY_CONTRACT_ATTACHED" in event_types
    assert "REAL_VALIDATION_FINDINGS_CREATED" in event_types
    assert "TOWER_VALIDATION_LOCKS_CONFIRMED" in event_types

    for event in events["events"]:
        assert event["event_id"].startswith("VSPVE-")
        assert event["validation_run_id"] == DEFAULT_VALIDATION_RUN_ID
        assert isinstance(event["event_payload"], dict)
        assert event["created_at"]


def test_gp058_can_write_real_review_event_without_unlocking_provider(validation_db):
    before = get_provider_risk_criteria_validation_events(validation_db)["event_count"]

    written = record_provider_risk_criteria_validation_review_event(
        "OWNER_VALIDATION_REVIEW_OBSERVED",
        {"reviewer": "owner", "note": "reviewed real validation engine"},
        validation_db,
    )

    after = get_provider_risk_criteria_validation_events(validation_db)
    run = get_provider_risk_criteria_validation_run(validation_db)["validation_run"]
    findings = get_provider_risk_criteria_validation_findings(validation_db)

    assert written["event_written"] is True
    assert written["event_id"].startswith("VSPVE-")
    assert written["validation_run_id"] == DEFAULT_VALIDATION_RUN_ID
    assert written["real_sqlite_backed"] is True
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
    assert "OWNER_VALIDATION_REVIEW_OBSERVED" in {event["event_type"] for event in after["events"]}

    assert run["provider_approved"] is False
    assert run["provider_activated"] is False
    assert run["provider_selected"] is False
    assert run["provider_configured"] is False
    assert run["provider_read_enabled"] is False
    assert run["provider_write_enabled"] is False
    assert run["vault_done"] is False

    assert findings["resolved_count"] == 0
    assert findings["blocks_execution_count"] == EXPECTED_TOTAL_FINDINGS


def test_gp058_validation_passes_locked_real_validation_engine(validation_db):
    validation = validate_provider_risk_criteria_validation_engine(validation_db)

    assert validation["pack"]["id"] == "VAULT_GP058"
    assert validation["validation_ready"] is True
    assert validation["valid"] is True
    assert validation["failed_count"] == 0
    assert validation["passed_count"] == validation["check_count"]
    assert validation["real_sqlite_backed"] is True
    assert validation["safe_to_continue_to_gp059"] is True

    codes = {item["code"] for item in validation["checks"]}
    assert "REAL_SQLITE_VALIDATION_RUN_EXISTS" in codes
    assert "SOURCE_GP057_CAPABILITY_CONTRACT_ATTACHED" in codes
    assert "REAL_CAPABILITY_FINDINGS_EXIST" in codes
    assert "REAL_CRITERIA_FINDINGS_EXIST" in codes
    assert "REAL_RISK_FINDINGS_EXIST" in codes
    assert "ALL_FINDINGS_BLOCK_PROVIDER_APPROVAL" in codes
    assert "ALL_FINDINGS_BLOCK_PROVIDER_ACTIVATION" in codes
    assert "ALL_FINDINGS_BLOCK_EXPORT" in codes
    assert "ALL_FINDINGS_BLOCK_EXECUTION" in codes
    assert "NO_PROVIDER_APPROVED" in codes
    assert "NO_PROVIDER_ACTIVATED" in codes
    assert "NO_PROVIDER_SELECTED" in codes
    assert "NO_EXPORT" in codes
    assert "NO_EXECUTION" in codes
    assert "VAULT_NOT_DONE" in codes
    assert "EVENT_LOG_EXISTS" in codes


def test_gp058_home_payload_has_truth_routes_and_next_step(validation_db):
    home = get_real_provider_risk_criteria_validation_engine_home(validation_db)

    assert home["pack"]["id"] == "VAULT_GP058"
    assert home["engine_truth"]["real_provider_risk_criteria_validation_engine_ready"] is True
    assert home["engine_truth"]["real_sqlite_backed"] is True
    assert home["engine_truth"]["real_schema_ready"] is True
    assert home["engine_truth"]["real_validation_run_exists"] is True
    assert home["engine_truth"]["real_findings_exist"] is True
    assert home["engine_truth"]["real_event_log_exists"] is True
    assert home["engine_truth"]["source_gp057_capability_contract_attached"] is True
    assert home["engine_truth"]["validation_passed"] is True
    assert home["engine_truth"]["provider_candidate_count"] == 5
    assert home["engine_truth"]["capability_finding_count"] == EXPECTED_CAPABILITY_FINDINGS
    assert home["engine_truth"]["criteria_finding_count"] == EXPECTED_CRITERIA_FINDINGS
    assert home["engine_truth"]["risk_finding_count"] == EXPECTED_RISK_FINDINGS
    assert home["engine_truth"]["finding_count"] == EXPECTED_TOTAL_FINDINGS
    assert home["engine_truth"]["provider_approved"] is False
    assert home["engine_truth"]["provider_activated"] is False
    assert home["engine_truth"]["provider_selected"] is False
    assert home["engine_truth"]["provider_configured"] is False
    assert home["engine_truth"]["provider_read_enabled"] is False
    assert home["engine_truth"]["provider_write_enabled"] is False
    assert home["engine_truth"]["export_enabled"] is False
    assert home["engine_truth"]["execution_enabled"] is False
    assert home["engine_truth"]["vault_done"] is False

    routes = home["routes"]
    assert routes["route"] == "/vault/real-provider-risk-criteria-validation-engine"
    assert routes["json_route"] == "/vault/real-provider-risk-criteria-validation-engine.json"
    assert routes["run_route"] == "/vault/provider-risk-criteria-validation-run.json"
    assert routes["findings_route"] == "/vault/provider-risk-criteria-validation-findings.json"
    assert routes["events_route"] == "/vault/provider-risk-criteria-validation-events.json"
    assert routes["validation_route"] == "/vault/provider-risk-criteria-validation-summary.json"
    assert routes["next_step_route"] == "/vault/provider-risk-criteria-validation-next-step.json"
    assert routes["gp058_status_route"] == "/vault/gp058-status.json"

    assert home["next_step"]["next_pack"] == "VAULT_GP059_REAL_PROVIDER_SELECTION_REVIEW_RECEIPT"
    assert home["next_step"]["safe_to_continue_to_gp059"] is True
    assert home["next_step"]["vault_done"] is False
    assert home["next_step"]["clouds_should_continue"] is False


def test_gp058_status_ready_real_and_locked(validation_db):
    status = get_gp058_status(validation_db)
    gp058 = status["gp058_status"]

    assert status["pack"]["id"] == "VAULT_GP058"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert status["pack"]["section_range"] == "GP051-GP060"

    assert gp058["ready"] is True
    assert gp058["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp058["section_title"] == "Archive Vault — Storage Provider Prep Layer"
    assert gp058["section_range"] == "GP051-GP060"
    assert gp058["real_provider_risk_criteria_validation_engine_ready"] is True
    assert gp058["real_sqlite_backed"] is True
    assert gp058["real_schema_ready"] is True
    assert gp058["real_validation_run_count"] == 1
    assert gp058["real_finding_count"] == EXPECTED_TOTAL_FINDINGS
    assert gp058["real_event_count"] >= 4
    assert gp058["source_gp057_capability_contract_attached"] is True
    assert gp058["capability_finding_count"] == EXPECTED_CAPABILITY_FINDINGS
    assert gp058["criteria_finding_count"] == EXPECTED_CRITERIA_FINDINGS
    assert gp058["risk_finding_count"] == EXPECTED_RISK_FINDINGS
    assert gp058["blocks_provider_approval_count"] == EXPECTED_TOTAL_FINDINGS
    assert gp058["blocks_provider_activation_count"] == EXPECTED_TOTAL_FINDINGS
    assert gp058["blocks_export_count"] == EXPECTED_TOTAL_FINDINGS
    assert gp058["blocks_execution_count"] == EXPECTED_TOTAL_FINDINGS
    assert gp058["tower_review_granted_count"] == 0
    assert gp058["resolved_count"] == 0
    assert gp058["validation_ready"] is True
    assert gp058["validation_passed"] is True
    assert gp058["safe_to_continue_to_gp059"] is True
    assert gp058["vault_done"] is False
    assert gp058["foundation_status"] == "safe_to_continue_not_done"
    assert gp058["provider_approved"] is False
    assert gp058["provider_activated"] is False
    assert gp058["provider_recommended"] is False
    assert gp058["provider_selected"] is False
    assert gp058["provider_configured"] is False
    assert gp058["provider_write_enabled"] is False
    assert gp058["provider_read_enabled"] is False
    assert gp058["provider_object_read_claimed"] is False
    assert gp058["provider_connection_tested"] is False
    assert gp058["risk_accepted"] is False
    assert gp058["risk_waived"] is False
    assert gp058["mitigation_approved"] is False
    assert gp058["object_body_view_enabled"] is False
    assert gp058["direct_upload_enabled"] is False
    assert gp058["export_enabled"] is False
    assert gp058["execution_enabled"] is False
    assert gp058["clouds_status"] == "parked_do_not_continue_from_vault_gp058"
    assert gp058["next_pack"] == "VAULT_GP059_REAL_PROVIDER_SELECTION_REVIEW_RECEIPT"


def test_gp058_next_step_says_continue_real_vault_not_clouds():
    next_step = get_provider_risk_criteria_validation_next_step()["next_step"]

    assert next_step["next_pack"] == "VAULT_GP059_REAL_PROVIDER_SELECTION_REVIEW_RECEIPT"
    assert next_step["next_pack_title"] == "Real Provider Selection Review Receipt"
    assert next_step["safe_to_continue_to_gp059"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False

    note = next_step["owner_notebook_note"].lower()
    assert "keep vault real and durable" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "real sqlite risk/criteria validation engine" in rules
    assert "real validation run records" in rules
    assert "real capability validation findings" in rules
    assert "real criteria validation findings" in rules
    assert "real risk validation findings" in rules
    assert "real provider selection review receipt" in rules
    assert "do not approve a provider yet" in rules
    assert "do not activate a provider yet" in rules
    assert "not vault done" in rules


def test_gp058_html_is_dark_and_mentions_real_validation_engine(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "html_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "html_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "html_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "html_validation.sqlite"))

    html = render_real_provider_risk_criteria_validation_engine_page()
    lowered = html.lower()

    assert "Vault Real Provider Risk / Criteria Validation Engine" in html
    assert "Storage Provider Prep Layer" in html
    assert "Archive Vault" in html
    assert "GP058" in html
    assert "Real SQLite-backed" in html
    assert "Real validation findings" in html
    assert "Real blocker rollups" in html
    assert "No provider approved" in html
    assert "No export" in html
    assert "No execution" in html
    assert "/vault/real-provider-risk-criteria-validation-engine.json" in html
    assert "/vault/gp058-status.json" in html

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


def test_gp058_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/real-provider-risk-criteria-validation-engine",
        "/vault/real-provider-risk-criteria-validation-engine.json",
        "/vault/provider-risk-criteria-validation-run.json",
        "/vault/provider-risk-criteria-validation-findings.json",
        "/vault/provider-risk-criteria-validation-events.json",
        "/vault/provider-risk-criteria-validation-summary.json",
        "/vault/provider-risk-criteria-validation-next-step.json",
        "/vault/gp058-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp058_flask_routes_when_app_importable_accepts_tower_guard(monkeypatch, tmp_path):
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_DECISION_DB", str(tmp_path / "routes_decision.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB", str(tmp_path / "routes_selection.sqlite"))
    monkeypatch.setenv("VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB", str(tmp_path / "routes_capability.sqlite"))
    monkeypatch.setenv("VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB", str(tmp_path / "routes_validation.sqlite"))

    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/real-provider-risk-criteria-validation-engine",
        "/vault/real-provider-risk-criteria-validation-engine.json",
        "/vault/provider-risk-criteria-validation-run.json",
        "/vault/provider-risk-criteria-validation-findings.json",
        "/vault/provider-risk-criteria-validation-events.json",
        "/vault/provider-risk-criteria-validation-summary.json",
        "/vault/provider-risk-criteria-validation-next-step.json",
        "/vault/gp058-status.json",
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
                assert b"Vault Real Provider Risk / Criteria Validation Engine" in response.data
