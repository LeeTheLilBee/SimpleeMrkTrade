"""
Tests for VAULT GIANT PACK 027 — Action Receipt Detail Drawer
"""

from pathlib import Path

import pytest

from vault.action_receipt_detail_drawer_service import (
    get_gp027_status,
    get_action_receipt_detail_drawer_blockers,
    get_action_receipt_detail_drawer_carry_forward,
    get_action_receipt_detail_drawer_checklist,
    get_action_receipt_detail_drawer_home,
    get_action_receipt_detail_drawer_owner_queue,
    get_action_receipt_detail_drawer_panels,
    get_action_receipt_detail_drawer_records,
    get_action_receipt_detail_drawer_tower_gates,
    render_action_receipt_detail_drawer_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp027_status_ready_safe_to_continue_and_not_done():
    status = get_gp027_status()

    assert status["pack"]["id"] == "VAULT_GP027"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER"
    assert status["gp027_status"]["ready"] is True
    assert status["gp027_status"]["gp026_confirmation_ledger_connected"] is True
    assert status["gp027_status"]["action_receipt_detail_drawer_ready"] is True
    assert status["gp027_status"]["safe_to_continue_to_gp028"] is True
    assert status["gp027_status"]["vault_done"] is False
    assert status["gp027_status"]["metadata_only_drawer"] is True
    assert status["gp027_status"]["private_drawer_only"] is True
    assert status["gp027_status"]["owner_review_required"] is True
    assert status["gp027_status"]["owner_confirmation_required"] is True
    assert status["gp027_status"]["owner_confirmed_count"] == 0
    assert status["gp027_status"]["auto_confirmation_disabled"] is True
    assert status["gp027_status"]["execution_after_confirmation_disabled"] is True
    assert status["gp027_status"]["execution_engine_disabled"] is True
    assert status["gp027_status"]["drawer_execution_disabled"] is True
    assert status["gp027_status"]["drawer_public_proof_disabled"] is True
    assert status["gp027_status"]["direct_upload_still_locked"] is True
    assert status["gp027_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp027_status"]["external_access_still_locked"] is True
    assert status["gp027_status"]["unredacted_export_still_locked"] is True
    assert status["gp027_status"]["raw_export_still_locked"] is True
    assert status["gp027_status"]["public_proof_still_locked"] is True
    assert status["gp027_status"]["public_ledger_proof_disabled"] is True
    assert status["gp027_status"]["portal_access_still_locked"] is True
    assert status["gp027_status"]["financing_decision_not_claimed"] is True
    assert status["gp027_status"]["legal_advice_not_claimed"] is True
    assert status["gp027_status"]["raw_verification_not_claimed"] is True
    assert status["gp027_status"]["auto_action_execution_disabled"] is True
    assert status["gp027_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp027"


def test_gp027_drawer_truth_keeps_restricted_paths_locked():
    status = get_gp027_status()
    truth = status["drawer_truth"]

    assert truth["action_receipt_detail_drawer_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["private_drawer_only"] is True
    assert truth["drawer_can_show_sensitive_body"] is False
    assert truth["drawer_can_execute_action"] is False
    assert truth["drawer_can_auto_confirm"] is False
    assert truth["drawer_can_create_public_proof"] is False
    assert truth["owner_review_required"] is True
    assert truth["owner_confirmation_required"] is True
    assert truth["owner_confirmed_count"] == 0
    assert truth["auto_confirmation_enabled"] is False
    assert truth["execution_after_confirmation_enabled"] is False
    assert truth["execution_engine_enabled"] is False
    assert truth["auto_action_execution_enabled"] is False
    assert truth["public_ledger_proof_enabled"] is False
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


def test_gp027_tower_authority_and_vault_boundaries():
    status = get_gp027_status()
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


def test_gp027_drawer_records_are_private_metadata_only():
    records = get_action_receipt_detail_drawer_records()

    assert records["drawer_record_count"] >= 40

    for record in records["drawer_records"]:
        assert record["drawer_id"].startswith("VDD-")
        assert record["ledger_id"].startswith("VOL-")
        assert record["receipt_id"].startswith("VAR-")
        assert record["prep_id"].startswith("VEP-")
        assert record["source_step_id"].startswith("VAS-")
        assert record["drawer_status"] == "OPEN_FOR_OWNER_REVIEW"
        assert record["metadata_only"] is True
        assert record["private_drawer_only"] is True
        assert record["owner_review_required"] is True
        assert record["owner_reviewed"] is False
        assert record["owner_confirmation_required"] is True
        assert record["owner_confirmed"] is False
        assert record["auto_confirm_allowed"] is False
        assert record["can_execute_after_confirmation"] is False
        assert record["can_execute_from_vault"] is False
        assert record["execution_engine_enabled"] is False
        assert record["public_proof_allowed"] is False
        assert record["public_ledger_proof_allowed"] is False
        assert record["raw_body_available"] is False
        assert record["external_share_allowed"] is False
        assert record["raw_export_allowed"] is False
        assert record["unredacted_export_allowed"] is False
        assert record["tower_gate_observed"] is True
        assert record["drawer_panel_count"] >= 7
        assert record["detail_checklist_row_count"] >= 5
        assert record["safe_to_carry_to_gp028"] is True
        assert "DETAIL_DRAWER_PRIVATE_ONLY" in record["blocked_codes"]
        assert "OWNER_REVIEW_REQUIRED" in record["blocked_codes"]
        assert "OWNER_CONFIRMATION_REQUIRED" in record["blocked_codes"]
        assert "NO_AUTO_CONFIRMATION" in record["blocked_codes"]
        assert "NO_EXECUTION_AFTER_CONFIRMATION" in record["blocked_codes"]
        assert "NO_ACTION_EXECUTION_FROM_VAULT" in record["blocked_codes"]
        assert "NO_PUBLIC_RECEIPT_PROOF" in record["blocked_codes"]
        assert "CLOUDS_PARKED" in record["blocked_codes"]


def test_gp027_drawer_panels_are_metadata_only_and_private():
    panels = get_action_receipt_detail_drawer_panels()

    assert panels["drawer_panel_count"] >= 280

    panel_types = {panel["panel_type"] for panel in panels["drawer_panels"]}
    assert "receipt_context" in panel_types
    assert "ledger_context" in panel_types
    assert "review_state" in panel_types
    assert "tower_gate" in panel_types
    assert "blockers" in panel_types
    assert "carry_forward" in panel_types
    assert "owner_next_action" in panel_types

    for panel in panels["drawer_panels"]:
        assert panel["panel_id"].startswith("VDP-")
        assert panel["drawer_id"].startswith("VDD-")
        assert panel["ledger_id"].startswith("VOL-")
        assert panel["receipt_id"].startswith("VAR-")
        assert panel["prep_id"].startswith("VEP-")
        assert panel["required"] is True
        assert panel["panel_status"] == "OPEN_METADATA_ONLY"
        assert panel["metadata_only"] is True
        assert panel["can_show_raw_body"] is False
        assert panel["can_execute_from_vault"] is False
        assert panel["can_auto_confirm"] is False
        assert panel["public_proof_allowed"] is False
        assert panel["receipt_linked"] is True
        assert "DETAIL_DRAWER_PRIVATE_ONLY" in panel["blocked_codes"]
        assert "OWNER_REVIEW_REQUIRED" in panel["blocked_codes"]
        assert "OWNER_CONFIRMATION_REQUIRED" in panel["blocked_codes"]
        assert "NO_AUTO_CONFIRMATION" in panel["blocked_codes"]
        assert "NO_EXECUTION_AFTER_CONFIRMATION" in panel["blocked_codes"]
        assert "NO_ACTION_EXECUTION_FROM_VAULT" in panel["blocked_codes"]
        assert "CLOUDS_PARKED" in panel["blocked_codes"]


def test_gp027_detail_checklist_rows_remain_open():
    checklist = get_action_receipt_detail_drawer_checklist()

    assert checklist["detail_checklist_row_count"] >= 200

    state_types = {row["state_type"] for row in checklist["detail_checklist_rows"]}
    assert "owner_review" in state_types
    assert "owner_confirmation" in state_types
    assert "tower_gate_observation" in state_types
    assert "execution_block" in state_types
    assert "carry_forward" in state_types

    for row in checklist["detail_checklist_rows"]:
        assert row["detail_checklist_id"].startswith("VDC-")
        assert row["drawer_id"].startswith("VDD-")
        assert row["ledger_id"].startswith("VOL-")
        assert row["receipt_id"].startswith("VAR-")
        assert row["prep_id"].startswith("VEP-")
        assert row["review_state_id"].startswith("VRS-")
        assert row["required"] is True
        assert row["status"] == "OPEN"
        assert row["completed"] is False
        assert row["owner_review_required"] is True
        assert row["owner_confirmed"] is False
        assert row["auto_complete_allowed"] is False
        assert row["auto_confirm_allowed"] is False
        assert row["can_execute_from_vault"] is False
        assert row["metadata_only"] is True
        assert "DETAIL_DRAWER_PRIVATE_ONLY" in row["blocked_codes"]
        assert "OWNER_REVIEW_REQUIRED" in row["blocked_codes"]
        assert "OWNER_CONFIRMATION_REQUIRED" in row["blocked_codes"]
        assert "NO_AUTO_CONFIRMATION" in row["blocked_codes"]
        assert "NO_EXECUTION_AFTER_CONFIRMATION" in row["blocked_codes"]
        assert "NO_ACTION_EXECUTION_FROM_VAULT" in row["blocked_codes"]
        assert "CLOUDS_PARKED" in row["blocked_codes"]


def test_gp027_tower_gate_detail_preserves_tower_control():
    gates = get_action_receipt_detail_drawer_tower_gates()["tower_gate_detail"]

    assert gates["tower_gate_detail_count"] >= 40
    assert gates["tower_owned_gate_count"] == gates["tower_gate_detail_count"]
    assert gates["vault_override_allowed_count"] == 0
    assert gates["all_tower_gates_preserved"] is True

    for row in gates["tower_gate_details"]:
        assert row["tower_gate_detail_id"].startswith("VDG-")
        assert row["drawer_id"].startswith("VDD-")
        assert row["ledger_id"].startswith("VOL-")
        assert row["receipt_id"].startswith("VAR-")
        assert row["prep_id"].startswith("VEP-")
        assert row["tower_gate_observed"] is True
        assert row["tower_owned"] is True
        assert row["vault_can_override"] is False
        assert row["external_access_allowed"] is False
        assert row["portal_access_allowed"] is False
        assert row["export_allowed"] is False


def test_gp027_blockers_keep_restricted_paths_locked():
    blockers = get_action_receipt_detail_drawer_blockers()["drawer_blocker_detail"]

    assert blockers["blocker_count"] >= 10
    assert blockers["all_blockers_safe"] is True
    assert blockers["auto_override_allowed"] is False
    assert blockers["all_restricted_paths_locked"] is True
    assert blockers["auto_confirmation_allowed"] is False
    assert blockers["execution_after_confirmation_allowed"] is False
    assert blockers["public_drawer_proof_allowed"] is False

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
    assert "NO_AUTO_CONFIRMATION" in codes
    assert "NO_EXECUTION_AFTER_CONFIRMATION" in codes
    assert "NO_AUTO_ACTION_EXECUTION" in codes
    assert "NO_ACTION_EXECUTION_FROM_VAULT" in codes
    assert "NO_PUBLIC_RECEIPT_PROOF" in codes
    assert "DETAIL_DRAWER_PRIVATE_ONLY" in codes
    assert "CLOUDS_PARKED" in codes

    for blocker in blockers["blockers"]:
        assert blocker["safe_to_override_inside_vault"] is False
        assert blocker["affected_drawer_count"] >= 1
        assert blocker["vault_response"]


def test_gp027_carry_forward_prepares_gp028_without_execution():
    carry = get_action_receipt_detail_drawer_carry_forward()["drawer_carry_forward"]

    assert carry["carry_forward_count"] >= 40
    assert carry["ready_for_gp028_count"] == carry["carry_forward_count"]
    assert carry["owner_confirmed_count"] == 0
    assert carry["execution_allowed_count"] == 0
    assert carry["public_proof_allowed_count"] == 0
    assert carry["safe_to_carry_to_gp028"] is True

    for item in carry["carry_forward_items"]:
        assert item["drawer_carry_forward_id"].startswith("VDF-")
        assert item["drawer_id"].startswith("VDD-")
        assert item["ledger_id"].startswith("VOL-")
        assert item["receipt_id"].startswith("VAR-")
        assert item["prep_id"].startswith("VEP-")
        assert item["carry_forward_status"] == "READY_FOR_GP028_CHECKLIST_COMPLETION_STATE"
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["auto_confirm_allowed"] is False
        assert item["execution_allowed"] is False
        assert item["public_proof_allowed"] is False
        assert item["safe_to_carry_to_gp028"] is True


def test_gp027_owner_queue_says_continue_vault_not_clouds():
    queue = get_action_receipt_detail_drawer_owner_queue()["owner_review_state"]

    assert queue["review_room"] == "Vault Action Receipt Detail Drawer"
    assert queue["section_header"] == "Archive Vault — Owner Action Receipt / Checklist Layer"
    assert queue["action_count"] >= 5
    assert queue["drawer_record_count"] >= 40
    assert queue["drawer_panel_count"] >= 280
    assert queue["blocker_count"] >= 10
    assert queue["carry_forward_count"] >= 40
    assert queue["owner_review_needed_count"] >= 1
    assert queue["tower_owned_action_count"] >= 1
    assert queue["auto_complete_allowed"] is False

    joined = " ".join(queue["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp028" in joined


def test_gp027_home_routes_declared():
    home = get_action_receipt_detail_drawer_home()
    summary = home["drawer_summary"]

    assert summary["section_header"] == "Archive Vault — Owner Action Receipt / Checklist Layer"
    assert summary["route"] == "/vault/action-receipt-detail-drawer"
    assert summary["json_route"] == "/vault/action-receipt-detail-drawer.json"
    assert summary["records_route"] == "/vault/action-receipt-detail-drawer-records.json"
    assert summary["panels_route"] == "/vault/action-receipt-detail-drawer-panels.json"
    assert summary["checklist_route"] == "/vault/action-receipt-detail-drawer-checklist.json"
    assert summary["tower_gates_route"] == "/vault/action-receipt-detail-drawer-tower-gates.json"
    assert summary["blockers_route"] == "/vault/action-receipt-detail-drawer-blockers.json"
    assert summary["carry_forward_route"] == "/vault/action-receipt-detail-drawer-carry-forward.json"
    assert summary["owner_queue_route"] == "/vault/action-receipt-detail-drawer-owner-queue.json"
    assert summary["gp027_status_route"] == "/vault/gp027-status.json"
    assert summary["metadata_only"] is True

    assert home["gp026_connection"]["gp026_ready"] is True
    assert home["gp026_connection"]["gp026_safe_to_continue"] is True
    assert home["gp026_connection"]["gp026_vault_done"] is False


def test_gp027_html_is_dark_and_has_no_white_background_tokens():
    html = render_action_receipt_detail_drawer_page()
    lowered = html.lower()

    assert "Vault Action Receipt Detail Drawer" in html
    assert "Archive Vault" in html
    assert "/vault/action-receipt-detail-drawer.json" in html
    assert "/vault/gp027-status.json" in html
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


def test_gp027_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/action-receipt-detail-drawer",
        "/vault/action-receipt-detail-drawer.json",
        "/vault/action-receipt-detail-drawer-records.json",
        "/vault/action-receipt-detail-drawer-panels.json",
        "/vault/action-receipt-detail-drawer-checklist.json",
        "/vault/action-receipt-detail-drawer-tower-gates.json",
        "/vault/action-receipt-detail-drawer-blockers.json",
        "/vault/action-receipt-detail-drawer-carry-forward.json",
        "/vault/action-receipt-detail-drawer-owner-queue.json",
        "/vault/gp027-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp027_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/action-receipt-detail-drawer",
        "/vault/action-receipt-detail-drawer.json",
        "/vault/action-receipt-detail-drawer-records.json",
        "/vault/action-receipt-detail-drawer-panels.json",
        "/vault/action-receipt-detail-drawer-checklist.json",
        "/vault/action-receipt-detail-drawer-tower-gates.json",
        "/vault/action-receipt-detail-drawer-blockers.json",
        "/vault/action-receipt-detail-drawer-carry-forward.json",
        "/vault/action-receipt-detail-drawer-owner-queue.json",
        "/vault/gp027-status.json",
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
                assert b"Vault Action Receipt Detail Drawer" in response.data
