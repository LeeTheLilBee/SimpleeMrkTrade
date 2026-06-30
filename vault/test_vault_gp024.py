"""
Tests for VAULT GIANT PACK 024 — Owner Action Execution Prep
"""

from pathlib import Path

import pytest

from vault.owner_action_execution_prep_service import (
    get_gp024_status,
    get_owner_action_execution_prep_blocked,
    get_owner_action_execution_prep_confirmations,
    get_owner_action_execution_prep_home,
    get_owner_action_execution_prep_owner_queue,
    get_owner_action_execution_prep_readiness,
    get_owner_action_execution_prep_receipts,
    get_owner_action_execution_prep_records,
    get_owner_action_execution_prep_tower_gates,
    render_owner_action_execution_prep_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp024_status_ready_safe_to_continue_and_not_done():
    status = get_gp024_status()

    assert status["pack"]["id"] == "VAULT_GP024"
    assert status["gp024_status"]["ready"] is True
    assert status["gp024_status"]["gp023_packet_action_plan_connected"] is True
    assert status["gp024_status"]["owner_action_execution_prep_ready"] is True
    assert status["gp024_status"]["safe_to_continue_to_gp025"] is True
    assert status["gp024_status"]["vault_done"] is False
    assert status["gp024_status"]["metadata_only_execution_prep"] is True
    assert status["gp024_status"]["execution_engine_disabled"] is True
    assert status["gp024_status"]["direct_upload_still_locked"] is True
    assert status["gp024_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp024_status"]["external_access_still_locked"] is True
    assert status["gp024_status"]["unredacted_export_still_locked"] is True
    assert status["gp024_status"]["raw_export_still_locked"] is True
    assert status["gp024_status"]["public_proof_still_locked"] is True
    assert status["gp024_status"]["portal_access_still_locked"] is True
    assert status["gp024_status"]["financing_decision_not_claimed"] is True
    assert status["gp024_status"]["legal_advice_not_claimed"] is True
    assert status["gp024_status"]["raw_verification_not_claimed"] is True
    assert status["gp024_status"]["auto_action_execution_disabled"] is True
    assert status["gp024_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp024"


def test_gp024_execution_prep_truth_keeps_all_restricted_paths_locked():
    status = get_gp024_status()
    truth = status["execution_prep_truth"]

    assert truth["owner_action_execution_prep_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["execution_engine_enabled"] is False
    assert truth["auto_action_execution_enabled"] is False
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["direct_upload_unlocked"] is False
    assert truth["provider_configured"] is False
    assert truth["external_access_enabled"] is False
    assert truth["unredacted_export_enabled"] is False
    assert truth["raw_export_enabled"] is False
    assert truth["public_proof_enabled"] is False
    assert truth["portal_access_enabled"] is False
    assert truth["financing_decision_enabled"] is False
    assert truth["legal_advice_enabled"] is False
    assert truth["raw_document_verification_claimed"] is False
    assert truth["auto_packet_approval_enabled"] is False
    assert truth["clouds_should_continue"] is False


def test_gp024_tower_authority_and_vault_boundaries():
    status = get_gp024_status()
    tower = status["tower_authority"]
    vault = status["vault_boundary"]

    assert tower["tower_owns_identity"] is True
    assert tower["tower_owns_permissions"] is True
    assert tower["tower_owns_clearance"] is True
    assert tower["tower_owns_step_up"] is True
    assert tower["tower_owns_export_locks"] is True
    assert tower["tower_owns_freeze_revoke"] is True
    assert tower["tower_owns_external_access"] is True
    assert tower["tower_owns_portal_unlocks"] is True
    assert tower["tower_owns_sensitive_visibility"] is True
    assert tower["tower_owns_action_authority_gates"] is True
    assert tower["vault_owns_tower_permissions"] is False

    assert vault["no_public_vault"] is True
    assert vault["direct_raw_upload_unlocked"] is False
    assert vault["permanent_file_body_storage_enabled"] is False
    assert vault["external_access_default"] == "denied"
    assert vault["unredacted_export_allowed"] is False
    assert vault["raw_export_allowed"] is False
    assert vault["redacted_owner_preview_allowed"] is True
    assert vault["sensitive_body_display_in_summary_views"] is False
    assert vault["beneficiary_details_in_summary_views"] is False
    assert vault["broker_secret_storage_allowed"] is False
    assert vault["public_ob_proof_allowed"] is False
    assert vault["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp024_prep_records_are_metadata_only_and_cannot_execute():
    records = get_owner_action_execution_prep_records()

    assert records["prep_record_count"] >= 40

    for record in records["execution_prep_records"]:
        assert record["prep_id"].startswith("VEP-")
        assert record["source_step_id"].startswith("VAS-")
        assert record["plan_packet_id"].startswith("owner_review_")
        assert record["prep_status"] == "READY_FOR_OWNER_PREP_REVIEW"
        assert record["metadata_only"] is True
        assert record["owner_required"] is True
        assert record["owner_confirmed"] is False
        assert record["can_execute_from_vault"] is False
        assert record["auto_execute_allowed"] is False
        assert record["raw_body_available"] is False
        assert record["external_share_allowed"] is False
        assert record["receipt_placeholder_required"] is True
        assert record["receipt_created"] is False
        assert record["phase_count"] >= 4
        assert "OWNER_CONFIRMATION_REQUIRED" in record["blocked_codes"]
        assert "NO_AUTO_ACTION_EXECUTION" in record["blocked_codes"]
        assert "NO_ACTION_EXECUTION_FROM_VAULT" in record["blocked_codes"]
        assert "CLOUDS_PARKED" in record["blocked_codes"]


def test_gp024_phase_records_are_prep_only_not_executed():
    records = get_owner_action_execution_prep_records()["execution_prep_records"]

    for record in records:
        phase_ids = {phase["phase_id"] for phase in record["phase_records"]}
        assert "owner_confirmation" in phase_ids
        assert "tower_gate_check" in phase_ids
        assert "blocked_reason_review" in phase_ids
        assert "receipt_placeholder" in phase_ids

        for phase in record["phase_records"]:
            assert phase["phase_status"] == "PREP_ONLY_NOT_EXECUTED"
            assert phase["owner_confirmed"] is False
            assert phase["auto_run_allowed"] is False
            assert phase["can_execute_from_vault"] is False
            assert "NO_AUTO_ACTION_EXECUTION" in phase["blocked_codes"]
            assert "NO_ACTION_EXECUTION_FROM_VAULT" in phase["blocked_codes"]


def test_gp024_confirmation_queue_waits_for_owner_and_never_executes():
    confirmations = get_owner_action_execution_prep_confirmations()["confirmation_queue"]

    assert confirmations["confirmation_count"] >= 40
    assert confirmations["waiting_owner_confirmation_count"] == confirmations["confirmation_count"]
    assert confirmations["owner_confirmed_count"] == 0
    assert confirmations["auto_confirm_allowed"] is False
    assert confirmations["execution_after_confirmation_allowed"] is False

    for item in confirmations["confirmations"]:
        assert item["confirmation_id"].startswith("VOC-")
        assert item["prep_id"].startswith("VEP-")
        assert item["confirmation_status"] == "WAITING_OWNER_CONFIRMATION"
        assert item["owner_confirmed"] is False
        assert item["auto_confirm_allowed"] is False
        assert item["can_execute_after_confirmation"] is False
        assert "does not execute" in item["reason_execution_blocked"]


def test_gp024_tower_gate_matrix_preserves_tower_control():
    gates = get_owner_action_execution_prep_tower_gates()["tower_gate_matrix"]

    assert gates["gate_count"] >= 40
    assert gates["tower_owned_gate_count"] == gates["gate_count"]
    assert gates["clearance_required_count"] >= 1
    assert gates["step_up_required_count"] >= 1
    assert gates["vault_override_allowed_count"] == 0
    assert gates["all_tower_gates_preserved"] is True

    for gate in gates["gates"]:
        assert gate["gate_id"].startswith("VTG-")
        assert gate["prep_id"].startswith("VEP-")
        assert gate["tower_owned"] is True
        assert gate["gate_status"] == "LOCKED_OR_OBSERVED"
        assert gate["vault_can_override"] is False
        assert gate["external_access_allowed"] is False
        assert gate["export_allowed"] is False
        assert gate["portal_access_allowed"] is False


def test_gp024_receipt_placeholders_do_not_create_public_proof_or_exports():
    receipts = get_owner_action_execution_prep_receipts()["receipt_placeholders"]

    assert receipts["receipt_placeholder_count"] >= 40
    assert receipts["receipt_created_count"] == 0
    assert receipts["raw_export_allowed_count"] == 0
    assert receipts["unredacted_export_allowed_count"] == 0
    assert receipts["public_proof_allowed_count"] == 0
    assert receipts["owner_review_required"] is True

    for item in receipts["receipt_placeholders"]:
        assert item["receipt_placeholder_id"].startswith("VRP-")
        assert item["prep_id"].startswith("VEP-")
        assert item["receipt_type"] == "owner_action_execution_prep_receipt"
        assert item["receipt_status"] == "PLACEHOLDER_ONLY"
        assert item["receipt_created"] is False
        assert item["raw_export_allowed"] is False
        assert item["unredacted_export_allowed"] is False
        assert item["public_proof_allowed"] is False


def test_gp024_blocked_prep_keeps_restricted_paths_locked():
    blocked = get_owner_action_execution_prep_blocked()["blocked_prep"]

    assert blocked["blocked_prep_count"] >= 10
    assert blocked["all_blocked_prep_safe"] is True
    assert blocked["auto_override_allowed"] is False
    assert blocked["all_restricted_paths_locked"] is True
    assert blocked["execution_from_vault_allowed"] is False

    codes = {item["code"] for item in blocked["blocked_prep"]}
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "EXTERNAL_ACCESS_DENIED" in codes
    assert "UNREDACTED_EXPORT_LOCKED" in codes
    assert "RAW_EXPORT_LOCKED" in codes
    assert "TOWER_CLEARANCE_REQUIRED" in codes
    assert "TOWER_STEP_UP_REQUIRED" in codes
    assert "OWNER_CONFIRMATION_REQUIRED" in codes
    assert "NO_AUTO_ACTION_EXECUTION" in codes
    assert "NO_ACTION_EXECUTION_FROM_VAULT" in codes
    assert "CLOUDS_PARKED" in codes

    for blocker in blocked["blocked_prep"]:
        assert blocker["safe_to_override_inside_vault"] is False
        assert blocker["affected_prep_count"] >= 1
        assert blocker["vault_response"]


def test_gp024_readiness_queue_is_prep_ready_but_execution_blocked():
    readiness = get_owner_action_execution_prep_readiness()["readiness_queue"]

    assert readiness["readiness_item_count"] >= 40
    assert readiness["prep_ready_count"] == readiness["readiness_item_count"]
    assert readiness["execution_allowed_count"] == 0
    assert readiness["owner_confirmation_ready_count"] >= 40
    assert readiness["tower_gate_observed_count"] >= 40
    assert readiness["safe_to_carry_to_gp025"] is True

    for item in readiness["readiness_items"]:
        assert item["readiness_id"].startswith("VER-")
        assert item["prep_id"].startswith("VEP-")
        assert item["readiness_status"] == "PREP_READY_EXECUTION_BLOCKED"
        assert item["owner_confirmation_ready"] is True
        assert item["owner_confirmed"] is False
        assert item["tower_gate_observed"] is True
        assert item["can_execute_from_vault"] is False
        assert item["safe_to_carry_to_gp025"] is True


def test_gp024_owner_queue_says_continue_vault_not_clouds():
    queue = get_owner_action_execution_prep_owner_queue()["owner_review_state"]

    assert queue["review_room"] == "Vault Owner Action Execution Prep"
    assert queue["action_count"] >= 5
    assert queue["prep_record_count"] >= 40
    assert queue["readiness_item_count"] >= 40
    assert queue["blocked_prep_count"] >= 10
    assert queue["owner_review_needed_count"] >= 1
    assert queue["tower_owned_action_count"] >= 1
    assert queue["auto_complete_allowed"] is False

    joined = " ".join(queue["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp025" in joined


def test_gp024_home_routes_declared():
    home = get_owner_action_execution_prep_home()
    summary = home["execution_prep_summary"]

    assert summary["route"] == "/vault/owner-action-execution-prep"
    assert summary["json_route"] == "/vault/owner-action-execution-prep.json"
    assert summary["records_route"] == "/vault/owner-action-execution-prep-records.json"
    assert summary["confirmation_route"] == "/vault/owner-action-execution-prep-confirmations.json"
    assert summary["tower_gates_route"] == "/vault/owner-action-execution-prep-tower-gates.json"
    assert summary["receipts_route"] == "/vault/owner-action-execution-prep-receipts.json"
    assert summary["blocked_route"] == "/vault/owner-action-execution-prep-blocked.json"
    assert summary["readiness_route"] == "/vault/owner-action-execution-prep-readiness.json"
    assert summary["owner_queue_route"] == "/vault/owner-action-execution-prep-owner-queue.json"
    assert summary["gp024_status_route"] == "/vault/gp024-status.json"
    assert summary["metadata_only"] is True

    assert home["gp023_connection"]["gp023_ready"] is True
    assert home["gp023_connection"]["gp023_safe_to_continue"] is True
    assert home["gp023_connection"]["gp023_vault_done"] is False


def test_gp024_html_is_dark_and_has_no_white_background_tokens():
    html = render_owner_action_execution_prep_page()
    lowered = html.lower()

    assert "Vault Owner Action Execution Prep" in html
    assert "Archive Vault" in html
    assert "/vault/owner-action-execution-prep.json" in html
    assert "/vault/gp024-status.json" in html
    assert "Clouds parked" in html

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


def test_gp024_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-action-execution-prep",
        "/vault/owner-action-execution-prep.json",
        "/vault/owner-action-execution-prep-records.json",
        "/vault/owner-action-execution-prep-confirmations.json",
        "/vault/owner-action-execution-prep-tower-gates.json",
        "/vault/owner-action-execution-prep-receipts.json",
        "/vault/owner-action-execution-prep-blocked.json",
        "/vault/owner-action-execution-prep-readiness.json",
        "/vault/owner-action-execution-prep-owner-queue.json",
        "/vault/gp024-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp024_flask_routes_when_app_importable_accepts_tower_guard():
    """
    In the full app, private Vault paths may return 403 because Tower/guard layers
    protect /vault routes. That is correct.

    Accept:
    - 200 direct local route response
    - 403 protected private route response

    Do not accept 404.
    """
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/owner-action-execution-prep",
        "/vault/owner-action-execution-prep.json",
        "/vault/owner-action-execution-prep-records.json",
        "/vault/owner-action-execution-prep-confirmations.json",
        "/vault/owner-action-execution-prep-tower-gates.json",
        "/vault/owner-action-execution-prep-receipts.json",
        "/vault/owner-action-execution-prep-blocked.json",
        "/vault/owner-action-execution-prep-readiness.json",
        "/vault/owner-action-execution-prep-owner-queue.json",
        "/vault/gp024-status.json",
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
                assert b"Vault Owner Action Execution Prep" in response.data
