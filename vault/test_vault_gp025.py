"""
Tests for VAULT GIANT PACK 025 — Owner Action Receipts / Checklists
"""

from pathlib import Path

import pytest

from vault.owner_action_receipts_checklists_service import (
    get_gp025_status,
    get_owner_action_checklists,
    get_owner_action_confirmation_ledger_seed,
    get_owner_action_prep_receipt_map,
    get_owner_action_receipt_blocked,
    get_owner_action_receipt_chain,
    get_owner_action_receipt_owner_queue,
    get_owner_action_receipt_records,
    get_owner_action_receipts_home,
    render_owner_action_receipts_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp025_status_ready_safe_to_continue_and_not_done():
    status = get_gp025_status()

    assert status["pack"]["id"] == "VAULT_GP025"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER"
    assert status["gp025_status"]["ready"] is True
    assert status["gp025_status"]["gp024_execution_prep_connected"] is True
    assert status["gp025_status"]["owner_action_receipts_ready"] is True
    assert status["gp025_status"]["owner_action_checklists_ready"] is True
    assert status["gp025_status"]["safe_to_continue_to_gp026"] is True
    assert status["gp025_status"]["vault_done"] is False
    assert status["gp025_status"]["metadata_only_receipts"] is True
    assert status["gp025_status"]["execution_engine_disabled"] is True
    assert status["gp025_status"]["receipt_creation_placeholder_only"] is True
    assert status["gp025_status"]["private_receipts_only"] is True
    assert status["gp025_status"]["direct_upload_still_locked"] is True
    assert status["gp025_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp025_status"]["external_access_still_locked"] is True
    assert status["gp025_status"]["unredacted_export_still_locked"] is True
    assert status["gp025_status"]["raw_export_still_locked"] is True
    assert status["gp025_status"]["public_proof_still_locked"] is True
    assert status["gp025_status"]["portal_access_still_locked"] is True
    assert status["gp025_status"]["financing_decision_not_claimed"] is True
    assert status["gp025_status"]["legal_advice_not_claimed"] is True
    assert status["gp025_status"]["raw_verification_not_claimed"] is True
    assert status["gp025_status"]["auto_action_execution_disabled"] is True
    assert status["gp025_status"]["public_receipt_proof_disabled"] is True
    assert status["gp025_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp025"


def test_gp025_receipt_truth_keeps_all_restricted_paths_locked():
    status = get_gp025_status()
    truth = status["receipt_truth"]

    assert truth["owner_action_receipts_enabled"] is True
    assert truth["owner_action_checklists_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["execution_engine_enabled"] is False
    assert truth["auto_action_execution_enabled"] is False
    assert truth["receipt_creation_is_placeholder_only"] is True
    assert truth["private_receipt_only"] is True
    assert truth["public_receipt_proof_enabled"] is False
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


def test_gp025_tower_authority_and_vault_boundaries():
    status = get_gp025_status()
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


def test_gp025_receipt_records_are_private_placeholders_only():
    records = get_owner_action_receipt_records()

    assert records["receipt_record_count"] >= 40

    for record in records["receipt_records"]:
        assert record["receipt_id"].startswith("VAR-")
        assert record["prep_id"].startswith("VEP-")
        assert record["source_step_id"].startswith("VAS-")
        assert record["plan_packet_id"].startswith("owner_review_")
        assert record["receipt_status"] == "RECEIPT_PLACEHOLDER_READY"
        assert record["metadata_only"] is True
        assert record["private_receipt_only"] is True
        assert record["public_proof_allowed"] is False
        assert record["receipt_created"] is False
        assert record["receipt_placeholder_ready"] is True
        assert record["owner_review_required"] is True
        assert record["owner_reviewed"] is False
        assert record["owner_confirmed"] is False
        assert record["tower_gate_observed"] is True
        assert record["can_execute_from_vault"] is False
        assert record["auto_execute_allowed"] is False
        assert record["raw_body_available"] is False
        assert record["external_share_allowed"] is False
        assert record["raw_export_allowed"] is False
        assert record["unredacted_export_allowed"] is False
        assert record["checklist_row_count"] >= 5
        assert record["checklist_complete_count"] == 0
        assert "NO_PUBLIC_RECEIPT_PROOF" in record["blocked_codes"]
        assert "NO_ACTION_EXECUTION_FROM_VAULT" in record["blocked_codes"]
        assert "NO_AUTO_ACTION_EXECUTION" in record["blocked_codes"]
        assert "CLOUDS_PARKED" in record["blocked_codes"]


def test_gp025_checklist_rows_are_open_and_not_auto_completed():
    checklists = get_owner_action_checklists()

    assert checklists["checklist_row_count"] >= 200

    types = {row["checklist_type"] for row in checklists["checklist_rows"]}
    assert "owner_review" in types
    assert "tower_gate" in types
    assert "blocked_reason" in types
    assert "receipt_placeholder" in types
    assert "carry_forward" in types

    for row in checklists["checklist_rows"]:
        assert row["checklist_id"].startswith("VAC-")
        assert row["prep_id"].startswith("VEP-")
        assert row["receipt_id"].startswith("VAR-")
        assert row["plan_packet_id"].startswith("owner_review_")
        assert row["required"] is True
        assert row["status"] == "OPEN"
        assert row["completed"] is False
        assert row["owner_review_required"] is True
        assert row["owner_confirmed"] is False
        assert row["can_auto_complete"] is False
        assert row["can_execute_from_vault"] is False
        assert row["metadata_only"] is True
        assert "OWNER_CONFIRMATION_REQUIRED" in row["blocked_codes"]
        assert "NO_AUTO_ACTION_EXECUTION" in row["blocked_codes"]
        assert "NO_ACTION_EXECUTION_FROM_VAULT" in row["blocked_codes"]
        assert "CLOUDS_PARKED" in row["blocked_codes"]


def test_gp025_prep_receipt_map_links_every_prep_to_receipt():
    mapping = get_owner_action_prep_receipt_map()["prep_receipt_map"]

    assert mapping["mapping_count"] >= 40
    assert mapping["all_prep_records_mapped"] is True
    assert mapping["receipt_created_count"] == 0
    assert mapping["execution_allowed_count"] == 0
    assert mapping["safe_to_carry_to_gp026"] is True

    for item in mapping["mappings"]:
        assert item["mapping_id"].startswith("VPM-")
        assert item["prep_id"].startswith("VEP-")
        assert item["source_step_id"].startswith("VAS-")
        assert item["receipt_id"].startswith("VAR-")
        assert item["plan_packet_id"].startswith("owner_review_")
        assert item["mapping_status"] == "MAPPED_PLACEHOLDER_ONLY"
        assert item["receipt_created"] is False
        assert item["can_execute_from_vault"] is False
        assert item["safe_to_carry_to_gp026"] is True


def test_gp025_confirmation_ledger_seed_waits_for_owner_confirmation():
    ledger = get_owner_action_confirmation_ledger_seed()["confirmation_ledger_seed"]

    assert ledger["ledger_entry_count"] >= 40
    assert ledger["waiting_owner_confirmation_count"] == ledger["ledger_entry_count"]
    assert ledger["owner_confirmed_count"] == 0
    assert ledger["auto_confirm_allowed"] is False
    assert ledger["execution_after_confirmation_allowed"] is False
    assert ledger["safe_to_deepen_in_gp026"] is True

    for entry in ledger["ledger_entries"]:
        assert entry["ledger_entry_id"].startswith("VCL-")
        assert entry["receipt_id"].startswith("VAR-")
        assert entry["prep_id"].startswith("VEP-")
        assert entry["ledger_status"] == "SEEDED_WAITING_OWNER_CONFIRMATION"
        assert entry["owner_reviewed"] is False
        assert entry["owner_confirmed"] is False
        assert entry["auto_confirm_allowed"] is False
        assert entry["can_execute_after_confirmation"] is False
        assert entry["public_proof_allowed"] is False


def test_gp025_receipt_chain_is_placeholder_only():
    chain = get_owner_action_receipt_chain()["receipt_chain"]

    assert chain["chain_node_count"] >= 40
    assert chain["placeholder_chain_node_count"] == chain["chain_node_count"]
    assert chain["receipt_created_count"] == 0
    assert chain["raw_export_allowed_count"] == 0
    assert chain["public_proof_allowed_count"] == 0
    assert chain["external_share_allowed_count"] == 0

    for node in chain["chain_nodes"]:
        assert node["chain_node_id"].startswith("VRC-")
        assert node["receipt_id"].startswith("VAR-")
        assert node["prep_id"].startswith("VEP-")
        assert node["source_step_id"].startswith("VAS-")
        assert node["chain_status"] == "PLACEHOLDER_CHAIN_NODE"
        assert node["checklist_row_count"] >= 5
        assert node["receipt_created"] is False
        assert node["raw_export_allowed"] is False
        assert node["unredacted_export_allowed"] is False
        assert node["public_proof_allowed"] is False
        assert node["external_share_allowed"] is False


def test_gp025_blocked_receipts_keep_restricted_paths_locked():
    blocked = get_owner_action_receipt_blocked()["blocked_receipts"]

    assert blocked["blocked_receipt_count"] >= 10
    assert blocked["all_blocked_receipts_safe"] is True
    assert blocked["auto_override_allowed"] is False
    assert blocked["all_restricted_paths_locked"] is True
    assert blocked["execution_from_vault_allowed"] is False
    assert blocked["public_receipt_proof_allowed"] is False

    codes = {item["code"] for item in blocked["blocked_receipts"]}
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
    assert "NO_PUBLIC_RECEIPT_PROOF" in codes
    assert "CLOUDS_PARKED" in codes

    for blocker in blocked["blocked_receipts"]:
        assert blocker["safe_to_override_inside_vault"] is False
        assert blocker["affected_receipt_count"] >= 1
        assert blocker["vault_response"]


def test_gp025_owner_queue_says_continue_vault_not_clouds():
    queue = get_owner_action_receipt_owner_queue()["owner_review_state"]

    assert queue["review_room"] == "Vault Owner Action Receipts / Checklists"
    assert queue["section_header"] == "Archive Vault — Owner Action Receipt / Checklist Layer"
    assert queue["action_count"] >= 5
    assert queue["receipt_record_count"] >= 40
    assert queue["checklist_row_count"] >= 200
    assert queue["blocked_receipt_count"] >= 10
    assert queue["owner_review_needed_count"] >= 1
    assert queue["tower_owned_action_count"] >= 1
    assert queue["auto_complete_allowed"] is False

    joined = " ".join(queue["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp026" in joined


def test_gp025_home_routes_declared():
    home = get_owner_action_receipts_home()
    summary = home["receipt_summary"]

    assert summary["section_header"] == "Archive Vault — Owner Action Receipt / Checklist Layer"
    assert summary["route"] == "/vault/owner-action-receipts"
    assert summary["json_route"] == "/vault/owner-action-receipts.json"
    assert summary["records_route"] == "/vault/owner-action-receipt-records.json"
    assert summary["checklists_route"] == "/vault/owner-action-checklists.json"
    assert summary["map_route"] == "/vault/owner-action-prep-receipt-map.json"
    assert summary["confirmation_ledger_route"] == "/vault/owner-action-confirmation-ledger-seed.json"
    assert summary["chain_route"] == "/vault/owner-action-receipt-chain.json"
    assert summary["blocked_route"] == "/vault/owner-action-receipt-blocked.json"
    assert summary["owner_queue_route"] == "/vault/owner-action-receipt-owner-queue.json"
    assert summary["gp025_status_route"] == "/vault/gp025-status.json"
    assert summary["metadata_only"] is True

    assert home["gp024_connection"]["gp024_ready"] is True
    assert home["gp024_connection"]["gp024_safe_to_continue"] is True
    assert home["gp024_connection"]["gp024_vault_done"] is False


def test_gp025_html_is_dark_and_has_no_white_background_tokens():
    html = render_owner_action_receipts_page()
    lowered = html.lower()

    assert "Vault Owner Action Receipts / Checklists" in html
    assert "Archive Vault" in html
    assert "/vault/owner-action-receipts.json" in html
    assert "/vault/gp025-status.json" in html
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


def test_gp025_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-action-receipts",
        "/vault/owner-action-receipts.json",
        "/vault/owner-action-receipt-records.json",
        "/vault/owner-action-checklists.json",
        "/vault/owner-action-prep-receipt-map.json",
        "/vault/owner-action-confirmation-ledger-seed.json",
        "/vault/owner-action-receipt-chain.json",
        "/vault/owner-action-receipt-blocked.json",
        "/vault/owner-action-receipt-owner-queue.json",
        "/vault/gp025-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp025_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/owner-action-receipts",
        "/vault/owner-action-receipts.json",
        "/vault/owner-action-receipt-records.json",
        "/vault/owner-action-checklists.json",
        "/vault/owner-action-prep-receipt-map.json",
        "/vault/owner-action-confirmation-ledger-seed.json",
        "/vault/owner-action-receipt-chain.json",
        "/vault/owner-action-receipt-blocked.json",
        "/vault/owner-action-receipt-owner-queue.json",
        "/vault/gp025-status.json",
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
                assert b"Vault Owner Action Receipts / Checklists" in response.data
