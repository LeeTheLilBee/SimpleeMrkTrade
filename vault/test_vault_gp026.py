"""
Tests for VAULT GIANT PACK 026 — Owner Confirmation Ledger
"""

from pathlib import Path

import pytest

from vault.owner_confirmation_ledger_service import (
    get_gp026_status,
    get_owner_confirmation_ledger_blockers,
    get_owner_confirmation_ledger_carry_forward,
    get_owner_confirmation_ledger_entries,
    get_owner_confirmation_ledger_home,
    get_owner_confirmation_ledger_owner_queue,
    get_owner_confirmation_ledger_receipt_links,
    get_owner_confirmation_ledger_review_state,
    render_owner_confirmation_ledger_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp026_status_ready_safe_to_continue_and_not_done():
    status = get_gp026_status()

    assert status["pack"]["id"] == "VAULT_GP026"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER"
    assert status["gp026_status"]["ready"] is True
    assert status["gp026_status"]["gp025_receipts_connected"] is True
    assert status["gp026_status"]["owner_confirmation_ledger_ready"] is True
    assert status["gp026_status"]["safe_to_continue_to_gp027"] is True
    assert status["gp026_status"]["vault_done"] is False
    assert status["gp026_status"]["metadata_only_ledger"] is True
    assert status["gp026_status"]["private_ledger_only"] is True
    assert status["gp026_status"]["owner_review_required"] is True
    assert status["gp026_status"]["owner_confirmation_required"] is True
    assert status["gp026_status"]["owner_confirmed_count"] == 0
    assert status["gp026_status"]["auto_confirmation_disabled"] is True
    assert status["gp026_status"]["execution_after_confirmation_disabled"] is True
    assert status["gp026_status"]["execution_engine_disabled"] is True
    assert status["gp026_status"]["direct_upload_still_locked"] is True
    assert status["gp026_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp026_status"]["external_access_still_locked"] is True
    assert status["gp026_status"]["unredacted_export_still_locked"] is True
    assert status["gp026_status"]["raw_export_still_locked"] is True
    assert status["gp026_status"]["public_proof_still_locked"] is True
    assert status["gp026_status"]["public_ledger_proof_disabled"] is True
    assert status["gp026_status"]["portal_access_still_locked"] is True
    assert status["gp026_status"]["financing_decision_not_claimed"] is True
    assert status["gp026_status"]["legal_advice_not_claimed"] is True
    assert status["gp026_status"]["raw_verification_not_claimed"] is True
    assert status["gp026_status"]["auto_action_execution_disabled"] is True
    assert status["gp026_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp026"


def test_gp026_confirmation_truth_keeps_restricted_paths_locked():
    status = get_gp026_status()
    truth = status["confirmation_truth"]

    assert truth["owner_confirmation_ledger_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["owner_review_required"] is True
    assert truth["owner_confirmation_required"] is True
    assert truth["owner_confirmed_count"] == 0
    assert truth["auto_confirmation_enabled"] is False
    assert truth["execution_after_confirmation_enabled"] is False
    assert truth["execution_engine_enabled"] is False
    assert truth["auto_action_execution_enabled"] is False
    assert truth["private_ledger_only"] is True
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


def test_gp026_tower_authority_and_vault_boundaries():
    status = get_gp026_status()
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


def test_gp026_ledger_entries_wait_for_owner_and_never_execute():
    entries = get_owner_confirmation_ledger_entries()

    assert entries["ledger_entry_count"] >= 40

    for entry in entries["ledger_entries"]:
        assert entry["ledger_id"].startswith("VOL-")
        assert entry["seed_ledger_entry_id"].startswith("VCL-")
        assert entry["receipt_id"].startswith("VAR-")
        assert entry["prep_id"].startswith("VEP-")
        assert entry["source_step_id"].startswith("VAS-")
        assert entry["ledger_status"] == "WAITING_OWNER_REVIEW"
        assert entry["metadata_only"] is True
        assert entry["private_ledger_only"] is True
        assert entry["owner_review_required"] is True
        assert entry["owner_reviewed"] is False
        assert entry["owner_confirmation_required"] is True
        assert entry["owner_confirmed"] is False
        assert entry["auto_confirm_allowed"] is False
        assert entry["can_execute_after_confirmation"] is False
        assert entry["can_execute_from_vault"] is False
        assert entry["execution_engine_enabled"] is False
        assert entry["public_proof_allowed"] is False
        assert entry["public_ledger_proof_allowed"] is False
        assert entry["raw_body_available"] is False
        assert entry["external_share_allowed"] is False
        assert entry["raw_export_allowed"] is False
        assert entry["unredacted_export_allowed"] is False
        assert entry["review_state_row_count"] >= 5
        assert "OWNER_REVIEW_REQUIRED" in entry["blocked_codes"]
        assert "OWNER_CONFIRMATION_REQUIRED" in entry["blocked_codes"]
        assert "NO_AUTO_CONFIRMATION" in entry["blocked_codes"]
        assert "NO_EXECUTION_AFTER_CONFIRMATION" in entry["blocked_codes"]
        assert "NO_ACTION_EXECUTION_FROM_VAULT" in entry["blocked_codes"]
        assert "NO_PUBLIC_RECEIPT_PROOF" in entry["blocked_codes"]
        assert "CLOUDS_PARKED" in entry["blocked_codes"]


def test_gp026_review_state_rows_are_open_and_not_auto_completed():
    review_state = get_owner_confirmation_ledger_review_state()

    assert review_state["review_state_row_count"] >= 200

    state_types = {row["state_type"] for row in review_state["review_state_rows"]}
    assert "owner_review" in state_types
    assert "owner_confirmation" in state_types
    assert "tower_gate_observation" in state_types
    assert "execution_block" in state_types
    assert "carry_forward" in state_types

    for row in review_state["review_state_rows"]:
        assert row["review_state_id"].startswith("VRS-")
        assert row["ledger_id"].startswith("VOL-")
        assert row["receipt_id"].startswith("VAR-")
        assert row["prep_id"].startswith("VEP-")
        assert row["required"] is True
        assert row["status"] == "OPEN"
        assert row["completed"] is False
        assert row["owner_review_required"] is True
        assert row["owner_confirmed"] is False
        assert row["auto_complete_allowed"] is False
        assert row["auto_confirm_allowed"] is False
        assert row["can_execute_from_vault"] is False
        assert row["metadata_only"] is True
        assert "OWNER_REVIEW_REQUIRED" in row["blocked_codes"]
        assert "OWNER_CONFIRMATION_REQUIRED" in row["blocked_codes"]
        assert "NO_AUTO_CONFIRMATION" in row["blocked_codes"]
        assert "NO_EXECUTION_AFTER_CONFIRMATION" in row["blocked_codes"]
        assert "NO_ACTION_EXECUTION_FROM_VAULT" in row["blocked_codes"]
        assert "CLOUDS_PARKED" in row["blocked_codes"]


def test_gp026_receipt_links_connect_every_ledger_to_private_receipt():
    links = get_owner_confirmation_ledger_receipt_links()["receipt_links"]

    assert links["receipt_link_count"] >= 40
    assert links["all_ledger_entries_linked"] is True
    assert links["receipt_created_count"] == 0
    assert links["public_proof_allowed_count"] == 0
    assert links["external_share_allowed_count"] == 0
    assert links["safe_to_carry_to_gp027"] is True

    for item in links["links"]:
        assert item["link_id"].startswith("VLR-")
        assert item["ledger_id"].startswith("VOL-")
        assert item["receipt_id"].startswith("VAR-")
        assert item["prep_id"].startswith("VEP-")
        assert item["source_step_id"].startswith("VAS-")
        assert item["plan_packet_id"].startswith("owner_review_")
        assert item["link_status"] == "LEDGER_LINKED_TO_PRIVATE_RECEIPT"
        assert item["receipt_exists"] is True
        assert item["receipt_created"] is False
        assert item["public_proof_allowed"] is False
        assert item["external_share_allowed"] is False
        assert item["safe_to_carry_to_gp027"] is True


def test_gp026_blockers_keep_restricted_paths_locked():
    blockers = get_owner_confirmation_ledger_blockers()["confirmation_blockers"]

    assert blockers["blocker_count"] >= 10
    assert blockers["all_blockers_safe"] is True
    assert blockers["auto_override_allowed"] is False
    assert blockers["all_restricted_paths_locked"] is True
    assert blockers["auto_confirmation_allowed"] is False
    assert blockers["execution_after_confirmation_allowed"] is False
    assert blockers["public_ledger_proof_allowed"] is False

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
    assert "CLOUDS_PARKED" in codes

    for blocker in blockers["blockers"]:
        assert blocker["safe_to_override_inside_vault"] is False
        assert blocker["affected_ledger_count"] >= 1
        assert blocker["vault_response"]


def test_gp026_carry_forward_trail_prepares_gp027_without_execution():
    carry = get_owner_confirmation_ledger_carry_forward()["carry_forward_trail"]

    assert carry["carry_forward_count"] >= 40
    assert carry["ready_for_gp027_count"] == carry["carry_forward_count"]
    assert carry["owner_confirmed_count"] == 0
    assert carry["execution_allowed_count"] == 0
    assert carry["public_proof_allowed_count"] == 0
    assert carry["safe_to_carry_to_gp027"] is True

    for item in carry["carry_forward_items"]:
        assert item["carry_forward_id"].startswith("VCF-")
        assert item["ledger_id"].startswith("VOL-")
        assert item["receipt_id"].startswith("VAR-")
        assert item["prep_id"].startswith("VEP-")
        assert item["carry_forward_status"] == "READY_FOR_GP027_DETAIL_DRAWER"
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["auto_confirm_allowed"] is False
        assert item["execution_allowed"] is False
        assert item["public_proof_allowed"] is False
        assert item["safe_to_carry_to_gp027"] is True


def test_gp026_owner_queue_says_continue_vault_not_clouds():
    queue = get_owner_confirmation_ledger_owner_queue()["owner_review_state"]

    assert queue["review_room"] == "Vault Owner Confirmation Ledger"
    assert queue["section_header"] == "Archive Vault — Owner Action Receipt / Checklist Layer"
    assert queue["action_count"] >= 5
    assert queue["ledger_entry_count"] >= 40
    assert queue["review_state_row_count"] >= 200
    assert queue["blocker_count"] >= 10
    assert queue["carry_forward_count"] >= 40
    assert queue["owner_review_needed_count"] >= 1
    assert queue["tower_owned_action_count"] >= 1
    assert queue["auto_complete_allowed"] is False

    joined = " ".join(queue["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp027" in joined


def test_gp026_home_routes_declared():
    home = get_owner_confirmation_ledger_home()
    summary = home["confirmation_summary"]

    assert summary["section_header"] == "Archive Vault — Owner Action Receipt / Checklist Layer"
    assert summary["route"] == "/vault/owner-confirmation-ledger"
    assert summary["json_route"] == "/vault/owner-confirmation-ledger.json"
    assert summary["entries_route"] == "/vault/owner-confirmation-ledger-entries.json"
    assert summary["review_state_route"] == "/vault/owner-confirmation-ledger-review-state.json"
    assert summary["receipt_links_route"] == "/vault/owner-confirmation-ledger-receipt-links.json"
    assert summary["blockers_route"] == "/vault/owner-confirmation-ledger-blockers.json"
    assert summary["carry_forward_route"] == "/vault/owner-confirmation-ledger-carry-forward.json"
    assert summary["owner_queue_route"] == "/vault/owner-confirmation-ledger-owner-queue.json"
    assert summary["gp026_status_route"] == "/vault/gp026-status.json"
    assert summary["metadata_only"] is True

    assert home["gp025_connection"]["gp025_ready"] is True
    assert home["gp025_connection"]["gp025_safe_to_continue"] is True
    assert home["gp025_connection"]["gp025_vault_done"] is False


def test_gp026_html_is_dark_and_has_no_white_background_tokens():
    html = render_owner_confirmation_ledger_page()
    lowered = html.lower()

    assert "Vault Owner Confirmation Ledger" in html
    assert "Archive Vault" in html
    assert "/vault/owner-confirmation-ledger.json" in html
    assert "/vault/gp026-status.json" in html
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


def test_gp026_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-confirmation-ledger",
        "/vault/owner-confirmation-ledger.json",
        "/vault/owner-confirmation-ledger-entries.json",
        "/vault/owner-confirmation-ledger-review-state.json",
        "/vault/owner-confirmation-ledger-receipt-links.json",
        "/vault/owner-confirmation-ledger-blockers.json",
        "/vault/owner-confirmation-ledger-carry-forward.json",
        "/vault/owner-confirmation-ledger-owner-queue.json",
        "/vault/gp026-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp026_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/owner-confirmation-ledger",
        "/vault/owner-confirmation-ledger.json",
        "/vault/owner-confirmation-ledger-entries.json",
        "/vault/owner-confirmation-ledger-review-state.json",
        "/vault/owner-confirmation-ledger-receipt-links.json",
        "/vault/owner-confirmation-ledger-blockers.json",
        "/vault/owner-confirmation-ledger-carry-forward.json",
        "/vault/owner-confirmation-ledger-owner-queue.json",
        "/vault/gp026-status.json",
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
                assert b"Vault Owner Confirmation Ledger" in response.data
