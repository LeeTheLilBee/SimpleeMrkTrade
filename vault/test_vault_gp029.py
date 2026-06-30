"""
Tests for VAULT GIANT PACK 029 — Receipt Chain Review Board
"""

from pathlib import Path

import pytest

from vault.receipt_chain_review_board_service import (
    get_gp029_status,
    get_receipt_chain_review_board_blockers,
    get_receipt_chain_review_board_carry_forward,
    get_receipt_chain_review_board_completion_summary,
    get_receipt_chain_review_board_home,
    get_receipt_chain_review_board_lanes,
    get_receipt_chain_review_board_owner_queue,
    get_receipt_chain_review_board_priority,
    get_receipt_chain_review_board_records,
    get_receipt_chain_review_board_rows,
    render_receipt_chain_review_board_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp029_status_ready_safe_to_continue_and_not_done():
    status = get_gp029_status()

    assert status["pack"]["id"] == "VAULT_GP029"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER"
    assert status["gp029_status"]["ready"] is True
    assert status["gp029_status"]["gp028_completion_state_connected"] is True
    assert status["gp029_status"]["receipt_chain_review_board_ready"] is True
    assert status["gp029_status"]["safe_to_continue_to_gp030"] is True
    assert status["gp029_status"]["vault_done"] is False
    assert status["gp029_status"]["metadata_only_board"] is True
    assert status["gp029_status"]["private_board_only"] is True
    assert status["gp029_status"]["owner_review_required"] is True
    assert status["gp029_status"]["owner_confirmation_required"] is True
    assert status["gp029_status"]["owner_confirmed_count"] == 0
    assert status["gp029_status"]["completed_count"] == 0
    assert status["gp029_status"]["auto_completion_disabled"] is True
    assert status["gp029_status"]["auto_confirmation_disabled"] is True
    assert status["gp029_status"]["execution_after_completion_disabled"] is True
    assert status["gp029_status"]["execution_after_confirmation_disabled"] is True
    assert status["gp029_status"]["execution_engine_disabled"] is True
    assert status["gp029_status"]["board_public_proof_disabled"] is True
    assert status["gp029_status"]["direct_upload_still_locked"] is True
    assert status["gp029_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp029_status"]["external_access_still_locked"] is True
    assert status["gp029_status"]["unredacted_export_still_locked"] is True
    assert status["gp029_status"]["raw_export_still_locked"] is True
    assert status["gp029_status"]["public_proof_still_locked"] is True
    assert status["gp029_status"]["portal_access_still_locked"] is True
    assert status["gp029_status"]["financing_decision_not_claimed"] is True
    assert status["gp029_status"]["legal_advice_not_claimed"] is True
    assert status["gp029_status"]["raw_verification_not_claimed"] is True
    assert status["gp029_status"]["auto_action_execution_disabled"] is True
    assert status["gp029_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp029"


def test_gp029_board_truth_keeps_restricted_paths_locked():
    status = get_gp029_status()
    truth = status["board_truth"]

    assert truth["receipt_chain_review_board_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["private_board_only"] is True
    assert truth["receipt_chain_review_means_grouped_review_not_done"] is True
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
    assert truth["public_board_proof_enabled"] is False
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


def test_gp029_tower_authority_and_vault_boundaries():
    status = get_gp029_status()
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


def test_gp029_board_records_group_receipt_chains_without_completion():
    records = get_receipt_chain_review_board_records()

    assert records["board_record_count"] >= 40

    for record in records["board_records"]:
        assert record["board_record_id"].startswith("VRB-")
        assert record["completion_record_id"].startswith("VCS-")
        assert record["drawer_id"].startswith("VDD-")
        assert record["ledger_id"].startswith("VOL-")
        assert record["receipt_id"].startswith("VAR-")
        assert record["prep_id"].startswith("VEP-")
        assert record["source_step_id"].startswith("VAS-")
        assert record["board_status"] == "OPEN_FOR_CHAIN_REVIEW"
        assert record["metadata_only"] is True
        assert record["private_board_only"] is True
        assert record["owner_review_required"] is True
        assert record["owner_reviewed"] is False
        assert record["owner_confirmation_required"] is True
        assert record["owner_confirmed"] is False
        assert record["auto_complete_allowed"] is False
        assert record["auto_confirm_allowed"] is False
        assert record["can_execute_after_review"] is False
        assert record["can_execute_after_completion"] is False
        assert record["can_execute_after_confirmation"] is False
        assert record["can_execute_from_vault"] is False
        assert record["execution_engine_enabled"] is False
        assert record["public_proof_allowed"] is False
        assert record["raw_body_available"] is False
        assert record["external_share_allowed"] is False
        assert record["raw_export_allowed"] is False
        assert record["unredacted_export_allowed"] is False
        assert record["chain_row_count"] >= 5
        assert record["open_row_count"] >= 5
        assert record["blocked_row_count"] >= 1
        assert record["completed_row_count"] == 0
        assert record["auto_completed_row_count"] == 0
        assert record["ready_for_owner_review"] is True
        assert record["ready_to_execute"] is False
        assert record["safe_to_carry_to_gp030"] is True
        assert "RECEIPT_CHAIN_REVIEW_PRIVATE_ONLY" in record["blocked_codes"]
        assert "OWNER_REVIEW_REQUIRED" in record["blocked_codes"]
        assert "OWNER_CONFIRMATION_REQUIRED" in record["blocked_codes"]
        assert "NO_AUTO_COMPLETION" in record["blocked_codes"]
        assert "NO_AUTO_CONFIRMATION" in record["blocked_codes"]
        assert "NO_EXECUTION_AFTER_COMPLETION" in record["blocked_codes"]
        assert "NO_ACTION_EXECUTION_FROM_VAULT" in record["blocked_codes"]
        assert "CLOUDS_PARKED" in record["blocked_codes"]


def test_gp029_chain_rows_remain_open_blocked_and_not_completed():
    rows = get_receipt_chain_review_board_rows()

    assert rows["chain_row_count"] >= 200

    for row in rows["chain_rows"]:
        assert row["chain_row_id"].startswith("VBR-")
        assert row["board_record_id"].startswith("VRB-")
        assert row["completion_record_id"].startswith("VCS-")
        assert row["completion_row_id"].startswith("VCR-")
        assert row["drawer_id"].startswith("VDD-")
        assert row["ledger_id"].startswith("VOL-")
        assert row["receipt_id"].startswith("VAR-")
        assert row["prep_id"].startswith("VEP-")
        assert row["status"] == "OPEN"
        assert row["board_state"] == "OPEN_FOR_CHAIN_REVIEW"
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
        assert "RECEIPT_CHAIN_REVIEW_PRIVATE_ONLY" in row["blocked_codes"]
        assert "OWNER_REVIEW_REQUIRED" in row["blocked_codes"]
        assert "OWNER_CONFIRMATION_REQUIRED" in row["blocked_codes"]
        assert "NO_AUTO_COMPLETION" in row["blocked_codes"]
        assert "NO_AUTO_CONFIRMATION" in row["blocked_codes"]
        assert "NO_EXECUTION_AFTER_COMPLETION" in row["blocked_codes"]
        assert "NO_ACTION_EXECUTION_FROM_VAULT" in row["blocked_codes"]
        assert "CLOUDS_PARKED" in row["blocked_codes"]


def test_gp029_review_lanes_are_private_and_execution_blocked():
    lanes = get_receipt_chain_review_board_lanes()["review_lanes"]

    assert lanes["lane_count"] >= 5
    assert lanes["blocked_lane_count"] >= 1
    assert lanes["tower_owned_lane_count"] >= 1
    assert lanes["execution_allowed_count"] == 0
    assert lanes["all_review_lanes_private"] is True

    lane_ids = {lane["lane_id"] for lane in lanes["lanes"]}
    assert "receipt_chain_owner_review" in lane_ids
    assert "receipt_chain_tower_gate" in lane_ids
    assert "receipt_chain_completion_state" in lane_ids
    assert "receipt_chain_blockers" in lane_ids
    assert "receipt_chain_carry_forward" in lane_ids

    for lane in lanes["lanes"]:
        assert lane["affected_record_count"] >= 0
        assert lane["auto_complete_allowed"] is False
        assert lane["auto_confirm_allowed"] is False
        assert lane["execution_allowed"] is False
        assert lane["external_share_allowed"] is False


def test_gp029_priority_queue_orders_owner_review_without_execution():
    priority = get_receipt_chain_review_board_priority()["priority_queue"]

    assert priority["priority_item_count"] >= 40
    assert priority["owner_review_required"] is True
    assert priority["auto_complete_allowed"] is False
    assert priority["execution_allowed_count"] == 0
    assert priority["safe_to_carry_to_gp030"] is True

    ranks = [item["priority_rank"] for item in priority["priority_items"]]
    assert ranks == sorted(ranks)

    for item in priority["priority_items"]:
        assert item["priority_id"].startswith("RCB-P")
        assert item["board_record_id"].startswith("VRB-")
        assert item["completion_record_id"].startswith("VCS-")
        assert item["drawer_id"].startswith("VDD-")
        assert item["ledger_id"].startswith("VOL-")
        assert item["receipt_id"].startswith("VAR-")
        assert item["prep_id"].startswith("VEP-")
        assert item["owner_review_required"] is True
        assert item["owner_confirmed"] is False
        assert item["auto_complete_allowed"] is False
        assert item["can_execute_from_vault"] is False
        assert item["safe_to_carry_to_gp030"] is True


def test_gp029_completion_summary_says_review_not_done():
    summary = get_receipt_chain_review_board_completion_summary()["board_completion_summary"]

    assert summary["board_record_count"] >= 40
    assert summary["chain_row_count"] >= 200
    assert summary["open_row_count"] >= 200
    assert summary["blocked_row_count"] >= 1
    assert summary["completed_row_count"] == 0
    assert summary["auto_completed_row_count"] == 0
    assert summary["owner_review_required_count"] >= 40
    assert summary["owner_confirmed_count"] == 0
    assert summary["ready_for_owner_review_count"] >= 40
    assert summary["ready_to_execute_count"] == 0
    assert summary["execution_allowed_count"] == 0
    assert summary["public_proof_allowed_count"] == 0
    assert "does not mark anything complete" in summary["completion_truth"]


def test_gp029_blockers_keep_restricted_paths_locked():
    blockers = get_receipt_chain_review_board_blockers()["board_blockers"]

    assert blockers["blocker_count"] >= 10
    assert blockers["all_blockers_safe"] is True
    assert blockers["auto_override_allowed"] is False
    assert blockers["all_restricted_paths_locked"] is True
    assert blockers["auto_completion_allowed"] is False
    assert blockers["auto_confirmation_allowed"] is False
    assert blockers["execution_after_review_allowed"] is False
    assert blockers["execution_after_completion_allowed"] is False
    assert blockers["execution_after_confirmation_allowed"] is False
    assert blockers["public_board_proof_allowed"] is False

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
    assert "RECEIPT_CHAIN_REVIEW_PRIVATE_ONLY" in codes
    assert "CLOUDS_PARKED" in codes

    for blocker in blockers["blockers"]:
        assert blocker["safe_to_override_inside_vault"] is False
        assert blocker["affected_board_record_count"] >= 0
        assert blocker["affected_chain_row_count"] >= 0
        assert blocker["vault_response"]


def test_gp029_carry_forward_prepares_gp030_without_completion_or_execution():
    carry = get_receipt_chain_review_board_carry_forward()["board_carry_forward"]

    assert carry["carry_forward_count"] >= 40
    assert carry["ready_for_gp030_count"] == carry["carry_forward_count"]
    assert carry["owner_confirmed_count"] == 0
    assert carry["completed_count"] == 0
    assert carry["auto_completed_count"] == 0
    assert carry["execution_allowed_count"] == 0
    assert carry["public_proof_allowed_count"] == 0
    assert carry["safe_to_carry_to_gp030"] is True

    for item in carry["carry_forward_items"]:
        assert item["board_carry_forward_id"].startswith("RCB-CF-")
        assert item["board_record_id"].startswith("VRB-")
        assert item["completion_record_id"].startswith("VCS-")
        assert item["drawer_id"].startswith("VDD-")
        assert item["ledger_id"].startswith("VOL-")
        assert item["receipt_id"].startswith("VAR-")
        assert item["prep_id"].startswith("VEP-")
        assert item["carry_forward_status"] == "READY_FOR_GP030_OWNER_ACTION_RECEIPT_READINESS_CHECKPOINT"
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["completed_count"] == 0
        assert item["auto_complete_allowed"] is False
        assert item["auto_confirm_allowed"] is False
        assert item["execution_allowed"] is False
        assert item["public_proof_allowed"] is False
        assert item["safe_to_carry_to_gp030"] is True


def test_gp029_owner_queue_says_continue_vault_not_clouds():
    queue = get_receipt_chain_review_board_owner_queue()["owner_review_state"]

    assert queue["review_room"] == "Vault Receipt Chain Review Board"
    assert queue["section_header"] == "Archive Vault — Owner Action Receipt / Checklist Layer"
    assert queue["action_count"] >= 5
    assert queue["board_record_count"] >= 40
    assert queue["chain_row_count"] >= 200
    assert queue["review_lane_count"] >= 5
    assert queue["blocker_count"] >= 10
    assert queue["carry_forward_count"] >= 40
    assert queue["owner_review_needed_count"] >= 1
    assert queue["tower_owned_action_count"] >= 1
    assert queue["auto_complete_allowed"] is False

    joined = " ".join(queue["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp030" in joined


def test_gp029_home_routes_declared():
    home = get_receipt_chain_review_board_home()
    summary = home["board_summary"]

    assert summary["section_header"] == "Archive Vault — Owner Action Receipt / Checklist Layer"
    assert summary["route"] == "/vault/receipt-chain-review-board"
    assert summary["json_route"] == "/vault/receipt-chain-review-board.json"
    assert summary["records_route"] == "/vault/receipt-chain-review-board-records.json"
    assert summary["rows_route"] == "/vault/receipt-chain-review-board-rows.json"
    assert summary["lanes_route"] == "/vault/receipt-chain-review-board-lanes.json"
    assert summary["priority_route"] == "/vault/receipt-chain-review-board-priority.json"
    assert summary["completion_summary_route"] == "/vault/receipt-chain-review-board-completion-summary.json"
    assert summary["blockers_route"] == "/vault/receipt-chain-review-board-blockers.json"
    assert summary["carry_forward_route"] == "/vault/receipt-chain-review-board-carry-forward.json"
    assert summary["owner_queue_route"] == "/vault/receipt-chain-review-board-owner-queue.json"
    assert summary["gp029_status_route"] == "/vault/gp029-status.json"
    assert summary["metadata_only"] is True

    assert home["gp028_connection"]["gp028_ready"] is True
    assert home["gp028_connection"]["gp028_safe_to_continue"] is True
    assert home["gp028_connection"]["gp028_vault_done"] is False


def test_gp029_html_is_dark_and_has_no_white_background_tokens():
    html = render_receipt_chain_review_board_page()
    lowered = html.lower()

    assert "Vault Receipt Chain Review Board" in html
    assert "Archive Vault" in html
    assert "/vault/receipt-chain-review-board.json" in html
    assert "/vault/gp029-status.json" in html
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


def test_gp029_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/receipt-chain-review-board",
        "/vault/receipt-chain-review-board.json",
        "/vault/receipt-chain-review-board-records.json",
        "/vault/receipt-chain-review-board-rows.json",
        "/vault/receipt-chain-review-board-lanes.json",
        "/vault/receipt-chain-review-board-priority.json",
        "/vault/receipt-chain-review-board-completion-summary.json",
        "/vault/receipt-chain-review-board-blockers.json",
        "/vault/receipt-chain-review-board-carry-forward.json",
        "/vault/receipt-chain-review-board-owner-queue.json",
        "/vault/gp029-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp029_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/receipt-chain-review-board",
        "/vault/receipt-chain-review-board.json",
        "/vault/receipt-chain-review-board-records.json",
        "/vault/receipt-chain-review-board-rows.json",
        "/vault/receipt-chain-review-board-lanes.json",
        "/vault/receipt-chain-review-board-priority.json",
        "/vault/receipt-chain-review-board-completion-summary.json",
        "/vault/receipt-chain-review-board-blockers.json",
        "/vault/receipt-chain-review-board-carry-forward.json",
        "/vault/receipt-chain-review-board-owner-queue.json",
        "/vault/gp029-status.json",
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
                assert b"Vault Receipt Chain Review Board" in response.data
