"""
Tests for VAULT GIANT PACK 028 — Checklist Completion State
"""

from pathlib import Path

import pytest

from vault.checklist_completion_state_service import (
    get_gp028_status,
    get_checklist_completion_state_blockers,
    get_checklist_completion_state_carry_forward,
    get_checklist_completion_state_home,
    get_checklist_completion_state_owner_queue,
    get_checklist_completion_state_readiness,
    get_checklist_completion_state_records,
    get_checklist_completion_state_rows,
    render_checklist_completion_state_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp028_status_ready_safe_to_continue_and_not_done():
    status = get_gp028_status()

    assert status["pack"]["id"] == "VAULT_GP028"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER"
    assert status["gp028_status"]["ready"] is True
    assert status["gp028_status"]["gp027_detail_drawer_connected"] is True
    assert status["gp028_status"]["checklist_completion_state_ready"] is True
    assert status["gp028_status"]["safe_to_continue_to_gp029"] is True
    assert status["gp028_status"]["vault_done"] is False
    assert status["gp028_status"]["metadata_only_completion_state"] is True
    assert status["gp028_status"]["private_completion_state_only"] is True
    assert status["gp028_status"]["owner_review_required"] is True
    assert status["gp028_status"]["owner_confirmation_required"] is True
    assert status["gp028_status"]["owner_confirmed_count"] == 0
    assert status["gp028_status"]["completed_count"] == 0
    assert status["gp028_status"]["auto_completion_disabled"] is True
    assert status["gp028_status"]["auto_confirmation_disabled"] is True
    assert status["gp028_status"]["execution_after_completion_disabled"] is True
    assert status["gp028_status"]["execution_after_confirmation_disabled"] is True
    assert status["gp028_status"]["execution_engine_disabled"] is True
    assert status["gp028_status"]["completion_public_proof_disabled"] is True
    assert status["gp028_status"]["direct_upload_still_locked"] is True
    assert status["gp028_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp028_status"]["external_access_still_locked"] is True
    assert status["gp028_status"]["unredacted_export_still_locked"] is True
    assert status["gp028_status"]["raw_export_still_locked"] is True
    assert status["gp028_status"]["public_proof_still_locked"] is True
    assert status["gp028_status"]["portal_access_still_locked"] is True
    assert status["gp028_status"]["financing_decision_not_claimed"] is True
    assert status["gp028_status"]["legal_advice_not_claimed"] is True
    assert status["gp028_status"]["raw_verification_not_claimed"] is True
    assert status["gp028_status"]["auto_action_execution_disabled"] is True
    assert status["gp028_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp028"


def test_gp028_completion_truth_keeps_restricted_paths_locked():
    status = get_gp028_status()
    truth = status["completion_truth"]

    assert truth["checklist_completion_state_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["private_completion_state_only"] is True
    assert truth["completion_means_status_tracking_not_done"] is True
    assert truth["owner_review_required"] is True
    assert truth["owner_confirmation_required"] is True
    assert truth["owner_confirmed_count"] == 0
    assert truth["completed_count"] == 0
    assert truth["auto_completion_enabled"] is False
    assert truth["auto_confirmation_enabled"] is False
    assert truth["execution_after_completion_enabled"] is False
    assert truth["execution_after_confirmation_enabled"] is False
    assert truth["execution_engine_enabled"] is False
    assert truth["auto_action_execution_enabled"] is False
    assert truth["public_completion_proof_enabled"] is False
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


def test_gp028_tower_authority_and_vault_boundaries():
    status = get_gp028_status()
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


def test_gp028_completion_records_track_state_not_done():
    records = get_checklist_completion_state_records()

    assert records["completion_record_count"] >= 40

    for record in records["completion_records"]:
        assert record["completion_record_id"].startswith("VCS-")
        assert record["drawer_id"].startswith("VDD-")
        assert record["ledger_id"].startswith("VOL-")
        assert record["receipt_id"].startswith("VAR-")
        assert record["prep_id"].startswith("VEP-")
        assert record["source_step_id"].startswith("VAS-")
        assert record["completion_status"] == "OPEN_OWNER_REVIEW_REQUIRED"
        assert record["metadata_only"] is True
        assert record["private_completion_state_only"] is True
        assert record["owner_review_required"] is True
        assert record["owner_reviewed"] is False
        assert record["owner_confirmation_required"] is True
        assert record["owner_confirmed"] is False
        assert record["auto_complete_allowed"] is False
        assert record["auto_confirm_allowed"] is False
        assert record["can_execute_after_completion"] is False
        assert record["can_execute_after_confirmation"] is False
        assert record["can_execute_from_vault"] is False
        assert record["execution_engine_enabled"] is False
        assert record["public_proof_allowed"] is False
        assert record["raw_body_available"] is False
        assert record["external_share_allowed"] is False
        assert record["raw_export_allowed"] is False
        assert record["unredacted_export_allowed"] is False
        assert record["completion_row_count"] >= 5
        assert record["open_row_count"] >= 5
        assert record["blocked_row_count"] >= 1
        assert record["completed_row_count"] == 0
        assert record["auto_completed_row_count"] == 0
        assert record["ready_to_review"] is True
        assert record["ready_to_execute"] is False
        assert record["safe_to_carry_to_gp029"] is True
        assert "CHECKLIST_COMPLETION_PRIVATE_ONLY" in record["blocked_codes"]
        assert "OWNER_REVIEW_REQUIRED" in record["blocked_codes"]
        assert "OWNER_CONFIRMATION_REQUIRED" in record["blocked_codes"]
        assert "NO_AUTO_COMPLETION" in record["blocked_codes"]
        assert "NO_AUTO_CONFIRMATION" in record["blocked_codes"]
        assert "NO_EXECUTION_AFTER_COMPLETION" in record["blocked_codes"]
        assert "NO_ACTION_EXECUTION_FROM_VAULT" in record["blocked_codes"]
        assert "CLOUDS_PARKED" in record["blocked_codes"]


def test_gp028_completion_rows_remain_open_blocked_and_not_completed():
    rows = get_checklist_completion_state_rows()

    assert rows["completion_row_count"] >= 200

    states = {row["completion_state"] for row in rows["completion_rows"]}
    assert "BLOCKED_BY_TOWER_GATE" in states or "BLOCKED_BY_OWNER_CONFIRMATION" in states

    for row in rows["completion_rows"]:
        assert row["completion_row_id"].startswith("VCR-")
        assert row["completion_record_id"].startswith("VCS-")
        assert row["drawer_id"].startswith("VDD-")
        assert row["ledger_id"].startswith("VOL-")
        assert row["receipt_id"].startswith("VAR-")
        assert row["prep_id"].startswith("VEP-")
        assert row["detail_checklist_id"].startswith("VDC-")
        assert row["review_state_id"].startswith("VRS-")
        assert row["required"] is True
        assert row["status"] == "OPEN"
        assert row["blocked"] is True
        assert row["completed"] is False
        assert row["auto_completed"] is False
        assert row["owner_review_required"] is True
        assert row["owner_reviewed"] is False
        assert row["owner_confirmation_required"] is True
        assert row["owner_confirmed"] is False
        assert row["auto_complete_allowed"] is False
        assert row["auto_confirm_allowed"] is False
        assert row["can_execute_after_completion"] is False
        assert row["can_execute_after_confirmation"] is False
        assert row["can_execute_from_vault"] is False
        assert row["metadata_only"] is True
        assert row["public_proof_allowed"] is False
        assert row["external_share_allowed"] is False
        assert "CHECKLIST_COMPLETION_PRIVATE_ONLY" in row["blocked_codes"]
        assert "OWNER_REVIEW_REQUIRED" in row["blocked_codes"]
        assert "OWNER_CONFIRMATION_REQUIRED" in row["blocked_codes"]
        assert "NO_AUTO_COMPLETION" in row["blocked_codes"]
        assert "NO_AUTO_CONFIRMATION" in row["blocked_codes"]
        assert "NO_EXECUTION_AFTER_COMPLETION" in row["blocked_codes"]
        assert "NO_ACTION_EXECUTION_FROM_VAULT" in row["blocked_codes"]
        assert "CLOUDS_PARKED" in row["blocked_codes"]


def test_gp028_blockers_keep_restricted_paths_locked():
    blockers = get_checklist_completion_state_blockers()["completion_blockers"]

    assert blockers["blocker_count"] >= 10
    assert blockers["all_blockers_safe"] is True
    assert blockers["auto_override_allowed"] is False
    assert blockers["all_restricted_paths_locked"] is True
    assert blockers["auto_completion_allowed"] is False
    assert blockers["auto_confirmation_allowed"] is False
    assert blockers["execution_after_completion_allowed"] is False
    assert blockers["execution_after_confirmation_allowed"] is False
    assert blockers["public_completion_proof_allowed"] is False

    codes = {item["code"] for item in blockers["blockers"]}
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "EXTERNAL_ACCESS_DENIED" in codes
    assert "UNREDACTED_EXPORT_LOCKED" in codes
    assert "RAW_EXPORT_LOCKED" in codes
    assert "TOWER_CLEARANCE_REQUIRED" in codes
    assert "TOWER_STEP_UP_REQUIRED" in codes
    assert "OWNER_REVIEW_REQUIRED" in codes
    assert "OWNER_CONFIRMATION_REQUIRED" in codes
    assert "NO_AUTO_COMPLETION" in codes
    assert "NO_AUTO_CONFIRMATION" in codes
    assert "NO_EXECUTION_AFTER_COMPLETION" in codes
    assert "NO_EXECUTION_AFTER_CONFIRMATION" in codes
    assert "NO_AUTO_ACTION_EXECUTION" in codes
    assert "NO_ACTION_EXECUTION_FROM_VAULT" in codes
    assert "CHECKLIST_COMPLETION_PRIVATE_ONLY" in codes
    assert "CLOUDS_PARKED" in codes

    for blocker in blockers["blockers"]:
        assert blocker["safe_to_override_inside_vault"] is False
        assert blocker["affected_record_count"] >= 0
        assert blocker["affected_row_count"] >= 0
        assert blocker["vault_response"]


def test_gp028_readiness_is_review_ready_but_execution_blocked():
    readiness = get_checklist_completion_state_readiness()["completion_readiness"]

    assert readiness["readiness_item_count"] >= 40
    assert readiness["ready_to_review_count"] == readiness["readiness_item_count"]
    assert readiness["completion_allowed_count"] == 0
    assert readiness["execution_allowed_count"] == 0
    assert readiness["owner_confirmed_count"] == 0
    assert readiness["auto_completed_count"] == 0
    assert readiness["total_open_row_count"] >= 200
    assert readiness["total_completed_row_count"] == 0
    assert readiness["safe_to_carry_to_gp029"] is True

    for item in readiness["readiness_items"]:
        assert item["readiness_id"].startswith("VCSR-")
        assert item["completion_record_id"].startswith("VCS-")
        assert item["drawer_id"].startswith("VDD-")
        assert item["ledger_id"].startswith("VOL-")
        assert item["receipt_id"].startswith("VAR-")
        assert item["prep_id"].startswith("VEP-")
        assert item["readiness_status"] == "READY_TO_REVIEW_EXECUTION_BLOCKED"
        assert item["open_row_count"] >= 5
        assert item["blocked_row_count"] >= 1
        assert item["completed_row_count"] == 0
        assert item["owner_review_required"] is True
        assert item["owner_confirmed"] is False
        assert item["auto_complete_allowed"] is False
        assert item["can_execute_from_vault"] is False
        assert item["safe_to_carry_to_gp029"] is True


def test_gp028_carry_forward_prepares_gp029_without_completion_or_execution():
    carry = get_checklist_completion_state_carry_forward()["completion_carry_forward"]

    assert carry["carry_forward_count"] >= 40
    assert carry["ready_for_gp029_count"] == carry["carry_forward_count"]
    assert carry["owner_confirmed_count"] == 0
    assert carry["completed_count"] == 0
    assert carry["auto_completed_count"] == 0
    assert carry["execution_allowed_count"] == 0
    assert carry["public_proof_allowed_count"] == 0
    assert carry["safe_to_carry_to_gp029"] is True

    for item in carry["carry_forward_items"]:
        assert item["completion_carry_forward_id"].startswith("VCCF-")
        assert item["completion_record_id"].startswith("VCS-")
        assert item["drawer_id"].startswith("VDD-")
        assert item["ledger_id"].startswith("VOL-")
        assert item["receipt_id"].startswith("VAR-")
        assert item["prep_id"].startswith("VEP-")
        assert item["carry_forward_status"] == "READY_FOR_GP029_RECEIPT_CHAIN_REVIEW_BOARD"
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["completed_count"] == 0
        assert item["auto_complete_allowed"] is False
        assert item["auto_confirm_allowed"] is False
        assert item["execution_allowed"] is False
        assert item["public_proof_allowed"] is False
        assert item["safe_to_carry_to_gp029"] is True


def test_gp028_owner_queue_says_continue_vault_not_clouds():
    queue = get_checklist_completion_state_owner_queue()["owner_review_state"]

    assert queue["review_room"] == "Vault Checklist Completion State"
    assert queue["section_header"] == "Archive Vault — Owner Action Receipt / Checklist Layer"
    assert queue["action_count"] >= 5
    assert queue["completion_record_count"] >= 40
    assert queue["completion_row_count"] >= 200
    assert queue["blocker_count"] >= 10
    assert queue["readiness_item_count"] >= 40
    assert queue["carry_forward_count"] >= 40
    assert queue["owner_review_needed_count"] >= 1
    assert queue["tower_owned_action_count"] >= 1
    assert queue["auto_complete_allowed"] is False

    joined = " ".join(queue["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp029" in joined


def test_gp028_home_routes_declared():
    home = get_checklist_completion_state_home()
    summary = home["completion_summary"]

    assert summary["section_header"] == "Archive Vault — Owner Action Receipt / Checklist Layer"
    assert summary["route"] == "/vault/checklist-completion-state"
    assert summary["json_route"] == "/vault/checklist-completion-state.json"
    assert summary["records_route"] == "/vault/checklist-completion-state-records.json"
    assert summary["rows_route"] == "/vault/checklist-completion-state-rows.json"
    assert summary["blockers_route"] == "/vault/checklist-completion-state-blockers.json"
    assert summary["readiness_route"] == "/vault/checklist-completion-state-readiness.json"
    assert summary["carry_forward_route"] == "/vault/checklist-completion-state-carry-forward.json"
    assert summary["owner_queue_route"] == "/vault/checklist-completion-state-owner-queue.json"
    assert summary["gp028_status_route"] == "/vault/gp028-status.json"
    assert summary["metadata_only"] is True

    assert home["gp027_connection"]["gp027_ready"] is True
    assert home["gp027_connection"]["gp027_safe_to_continue"] is True
    assert home["gp027_connection"]["gp027_vault_done"] is False


def test_gp028_html_is_dark_and_has_no_white_background_tokens():
    html = render_checklist_completion_state_page()
    lowered = html.lower()

    assert "Vault Checklist Completion State" in html
    assert "Archive Vault" in html
    assert "/vault/checklist-completion-state.json" in html
    assert "/vault/gp028-status.json" in html
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


def test_gp028_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/checklist-completion-state",
        "/vault/checklist-completion-state.json",
        "/vault/checklist-completion-state-records.json",
        "/vault/checklist-completion-state-rows.json",
        "/vault/checklist-completion-state-blockers.json",
        "/vault/checklist-completion-state-readiness.json",
        "/vault/checklist-completion-state-carry-forward.json",
        "/vault/checklist-completion-state-owner-queue.json",
        "/vault/gp028-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp028_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/checklist-completion-state",
        "/vault/checklist-completion-state.json",
        "/vault/checklist-completion-state-records.json",
        "/vault/checklist-completion-state-rows.json",
        "/vault/checklist-completion-state-blockers.json",
        "/vault/checklist-completion-state-readiness.json",
        "/vault/checklist-completion-state-carry-forward.json",
        "/vault/checklist-completion-state-owner-queue.json",
        "/vault/gp028-status.json",
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
                assert b"Vault Checklist Completion State" in response.data
