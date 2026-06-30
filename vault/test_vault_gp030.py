"""
Tests for VAULT GIANT PACK 030 — Owner Action Receipt Readiness Checkpoint
"""

from pathlib import Path

import pytest

from vault.owner_action_receipt_readiness_checkpoint_service import (
    get_gp030_status,
    get_owner_action_receipt_readiness_boundaries,
    get_owner_action_receipt_readiness_carry_forward,
    get_owner_action_receipt_readiness_home,
    get_owner_action_receipt_readiness_owner_queue,
    get_owner_action_receipt_readiness_pack_matrix,
    get_owner_action_receipt_readiness_routes,
    get_owner_action_receipt_readiness_summary,
    render_owner_action_receipt_readiness_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp030_status_ready_section_closed_safe_to_continue_not_done():
    status = get_gp030_status()

    assert status["pack"]["id"] == "VAULT_GP030"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER"
    assert status["pack"]["section_range"] == "GP025-GP030"
    assert status["gp030_status"]["ready"] is True
    assert status["gp030_status"]["gp025_to_gp029_verified"] is True
    assert status["gp030_status"]["owner_action_receipt_layer_ready"] is True
    assert status["gp030_status"]["section_closed_as_checkpoint"] is True
    assert status["gp030_status"]["section_safe_to_continue"] is True
    assert status["gp030_status"]["safe_to_continue_to_gp031"] is True
    assert status["gp030_status"]["vault_done"] is False
    assert status["gp030_status"]["metadata_only_checkpoint"] is True
    assert status["gp030_status"]["private_checkpoint_only"] is True
    assert status["gp030_status"]["owner_review_required"] is True
    assert status["gp030_status"]["owner_confirmation_required"] is True
    assert status["gp030_status"]["owner_confirmed_count"] == 0
    assert status["gp030_status"]["completed_count"] == 0
    assert status["gp030_status"]["auto_completion_disabled"] is True
    assert status["gp030_status"]["auto_confirmation_disabled"] is True
    assert status["gp030_status"]["execution_after_review_disabled"] is True
    assert status["gp030_status"]["execution_after_completion_disabled"] is True
    assert status["gp030_status"]["execution_after_confirmation_disabled"] is True
    assert status["gp030_status"]["execution_engine_disabled"] is True
    assert status["gp030_status"]["checkpoint_public_proof_disabled"] is True
    assert status["gp030_status"]["direct_upload_still_locked"] is True
    assert status["gp030_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp030_status"]["external_access_still_locked"] is True
    assert status["gp030_status"]["unredacted_export_still_locked"] is True
    assert status["gp030_status"]["raw_export_still_locked"] is True
    assert status["gp030_status"]["public_proof_still_locked"] is True
    assert status["gp030_status"]["portal_access_still_locked"] is True
    assert status["gp030_status"]["financing_decision_not_claimed"] is True
    assert status["gp030_status"]["legal_advice_not_claimed"] is True
    assert status["gp030_status"]["raw_verification_not_claimed"] is True
    assert status["gp030_status"]["auto_action_execution_disabled"] is True
    assert status["gp030_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp030"


def test_gp030_checkpoint_truth_keeps_every_restricted_path_locked():
    status = get_gp030_status()
    truth = status["checkpoint_truth"]

    assert truth["section_readiness_checkpoint_enabled"] is True
    assert truth["section_closed_as_checkpoint"] is True
    assert truth["section_safe_to_continue"] is True
    assert truth["vault_done"] is False
    assert truth["safe_to_continue_not_done"] is True
    assert truth["metadata_only"] is True
    assert truth["private_checkpoint_only"] is True
    assert truth["owner_review_required"] is True
    assert truth["owner_confirmation_required"] is True
    assert truth["owner_confirmed_count"] == 0
    assert truth["completed_count"] == 0
    assert truth["auto_completion_enabled"] is False
    assert truth["auto_confirmation_enabled"] is False
    assert truth["execution_after_review_enabled"] is False
    assert truth["execution_after_completion_enabled"] is False
    assert truth["execution_after_confirmation_enabled"] is False
    assert truth["execution_engine_enabled"] is False
    assert truth["auto_action_execution_enabled"] is False
    assert truth["public_checkpoint_proof_enabled"] is False
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


def test_gp030_tower_authority_and_vault_boundaries():
    status = get_gp030_status()
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


def test_gp030_pack_matrix_verifies_gp025_to_gp029():
    matrix = get_owner_action_receipt_readiness_pack_matrix()["pack_matrix"]

    assert matrix["expected_pack_count"] == 5
    assert matrix["verified_pack_count"] == 5
    assert matrix["safe_to_continue_count"] == 5
    assert matrix["vault_done_count"] == 0
    assert matrix["all_expected_packs_present"] is True
    assert matrix["all_expected_packs_ready"] is True
    assert matrix["all_safe_to_continue"] is True
    assert matrix["all_not_done"] is True
    assert matrix["section_consistent"] is True
    assert matrix["foundation_status_consistent"] is True
    assert matrix["safe_to_close_section_checkpoint"] is True
    assert matrix["safe_to_continue_stack"] is True

    seen = {item["pack_id"] for item in matrix["pack_items"]}
    assert seen == {"VAULT_GP025", "VAULT_GP026", "VAULT_GP027", "VAULT_GP028", "VAULT_GP029"}

    for item in matrix["pack_items"]:
        assert item["present"] is True
        assert item["ready"] is True
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["section"] == "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER"
        assert item["foundation_status"] == "safe_to_continue_not_done"
        assert item["product_depth_layer"] != "unknown"


def test_gp030_boundary_review_all_locked():
    boundaries = get_owner_action_receipt_readiness_boundaries()["boundary_review"]

    assert boundaries["boundary_count"] >= 15
    assert boundaries["passed_boundary_count"] == boundaries["boundary_count"]
    assert boundaries["all_boundaries_locked"] is True
    assert boundaries["restricted_path_unlock_count"] == 0
    assert boundaries["tower_authority_preserved"] is True
    assert boundaries["safe_to_close_section_checkpoint"] is True

    codes = {item["code"] for item in boundaries["boundary_checks"]}
    assert "NO_VAULT_DONE" in codes
    assert "SAFE_TO_CONTINUE_NOT_DONE" in codes
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "EXTERNAL_ACCESS_DENIED" in codes
    assert "UNREDACTED_EXPORT_LOCKED" in codes
    assert "RAW_EXPORT_LOCKED" in codes
    assert "PUBLIC_PROOF_LOCKED" in codes
    assert "PORTAL_ACCESS_LOCKED" in codes
    assert "NO_AUTO_COMPLETION" in codes
    assert "NO_AUTO_CONFIRMATION" in codes
    assert "NO_AUTO_ACTION_EXECUTION" in codes
    assert "NO_ACTION_EXECUTION_FROM_VAULT" in codes
    assert "NO_FINANCING_DECISION" in codes
    assert "NO_LEGAL_ADVICE" in codes
    assert "NO_RAW_VERIFICATION_CLAIM" in codes
    assert "CLOUDS_PARKED" in codes

    for item in boundaries["boundary_checks"]:
        assert item["passed"] is True
        assert item["safe_to_override_inside_vault"] is False
        assert item["label"]


def test_gp030_route_review_is_private_or_guarded():
    routes = get_owner_action_receipt_readiness_routes()["route_review"]

    assert routes["required_route_count"] >= 40
    assert routes["checkpoint_route_count"] >= 8
    assert routes["total_route_count"] == routes["required_route_count"] + routes["checkpoint_route_count"]
    assert routes["all_routes_private_or_guarded"] is True
    assert routes["public_route_count"] == 0
    assert routes["safe_to_continue_route_review"] is True

    for item in routes["required_routes"] + routes["checkpoint_routes"]:
        assert item["route"].startswith("/vault/")
        assert item["required"] is True
        assert item["private_or_guarded"] is True
        assert item["public"] is False


def test_gp030_readiness_summary_counts_and_truth():
    summary = get_owner_action_receipt_readiness_summary()["readiness_summary"]

    assert summary["summary_id"] == "VAULT_GP030_OWNER_ACTION_RECEIPT_LAYER_READINESS"
    assert summary["section"] == "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER"
    assert summary["section_range"] == "GP025-GP030"
    assert summary["receipt_record_count"] >= 40
    assert summary["ledger_entry_count"] >= 40
    assert summary["drawer_record_count"] >= 40
    assert summary["completion_record_count"] >= 40
    assert summary["board_record_count"] >= 40
    assert summary["total_review_row_count"] >= 1000
    assert summary["completed_count"] == 0
    assert summary["owner_confirmed_count"] == 0
    assert summary["auto_completed_count"] == 0
    assert summary["auto_confirmed_count"] == 0
    assert summary["execution_allowed_count"] == 0
    assert summary["public_proof_allowed_count"] == 0
    assert summary["raw_export_allowed_count"] == 0
    assert summary["external_share_allowed_count"] == 0
    assert summary["pack_matrix_ready"] is True
    assert summary["boundaries_locked"] is True
    assert summary["section_ready"] is True
    assert summary["section_closed_as_checkpoint"] is True
    assert summary["section_safe_to_continue"] is True
    assert summary["vault_done"] is False
    assert "safe to continue, not Vault done" in summary["readiness_truth"]


def test_gp030_carry_forward_prepares_gp031_not_clouds():
    carry = get_owner_action_receipt_readiness_carry_forward()["carry_forward"]

    assert carry["carry_forward_count"] >= 3
    assert carry["ready_for_next_vault_section"] is True
    assert carry["safe_to_continue_to_gp031"] is True
    assert carry["clouds_should_continue"] is False
    assert carry["clouds_status"] == "parked_do_not_continue_from_vault_gp030"
    assert carry["vault_done"] is False
    assert carry["pack_matrix_ready"] is True
    assert carry["boundaries_locked"] is True

    joined = " ".join(item["label"] for item in carry["carry_forward_items"]).lower()
    assert "next vault" in joined
    assert "clouds" in joined


def test_gp030_owner_queue_says_continue_vault_not_clouds():
    queue = get_owner_action_receipt_readiness_owner_queue()["owner_review_state"]

    assert queue["review_room"] == "Vault Owner Action Receipt Readiness Checkpoint"
    assert queue["section_header"] == "Archive Vault — Owner Action Receipt / Checklist Layer"
    assert queue["section_range"] == "GP025-GP030"
    assert queue["action_count"] >= 5
    assert queue["ready_action_count"] >= 1
    assert queue["tower_owned_action_count"] >= 1
    assert queue["auto_complete_allowed"] is False
    assert queue["section_ready"] is True
    assert queue["section_safe_to_continue"] is True
    assert queue["boundaries_locked"] is True
    assert queue["carry_forward_count"] >= 3
    assert queue["vault_done"] is False

    joined = " ".join(queue["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp031" in joined


def test_gp030_home_routes_declared():
    home = get_owner_action_receipt_readiness_home()
    summary = home["checkpoint_summary"]

    assert summary["section_header"] == "Archive Vault — Owner Action Receipt / Checklist Layer"
    assert summary["section_range"] == "GP025-GP030"
    assert summary["route"] == "/vault/owner-action-receipt-readiness"
    assert summary["json_route"] == "/vault/owner-action-receipt-readiness.json"
    assert summary["pack_matrix_route"] == "/vault/owner-action-receipt-readiness-pack-matrix.json"
    assert summary["boundaries_route"] == "/vault/owner-action-receipt-readiness-boundaries.json"
    assert summary["routes_route"] == "/vault/owner-action-receipt-readiness-routes.json"
    assert summary["summary_route"] == "/vault/owner-action-receipt-readiness-summary.json"
    assert summary["owner_queue_route"] == "/vault/owner-action-receipt-readiness-owner-queue.json"
    assert summary["carry_forward_route"] == "/vault/owner-action-receipt-readiness-carry-forward.json"
    assert summary["gp030_status_route"] == "/vault/gp030-status.json"
    assert summary["section_ready"] is True
    assert summary["section_safe_to_continue"] is True
    assert summary["vault_done"] is False
    assert summary["metadata_only"] is True

    assert home["gp029_connection"]["gp029_ready"] is True
    assert home["gp029_connection"]["gp029_safe_to_continue"] is True
    assert home["gp029_connection"]["gp029_vault_done"] is False


def test_gp030_html_is_dark_and_has_no_white_background_tokens():
    html = render_owner_action_receipt_readiness_page()
    lowered = html.lower()

    assert "Vault Owner Action Receipt Readiness Checkpoint" in html
    assert "Archive Vault" in html
    assert "Section Close" in html
    assert "/vault/owner-action-receipt-readiness.json" in html
    assert "/vault/gp030-status.json" in html
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


def test_gp030_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-action-receipt-readiness",
        "/vault/owner-action-receipt-readiness.json",
        "/vault/owner-action-receipt-readiness-pack-matrix.json",
        "/vault/owner-action-receipt-readiness-boundaries.json",
        "/vault/owner-action-receipt-readiness-routes.json",
        "/vault/owner-action-receipt-readiness-summary.json",
        "/vault/owner-action-receipt-readiness-owner-queue.json",
        "/vault/owner-action-receipt-readiness-carry-forward.json",
        "/vault/gp030-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp030_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/owner-action-receipt-readiness",
        "/vault/owner-action-receipt-readiness.json",
        "/vault/owner-action-receipt-readiness-pack-matrix.json",
        "/vault/owner-action-receipt-readiness-boundaries.json",
        "/vault/owner-action-receipt-readiness-routes.json",
        "/vault/owner-action-receipt-readiness-summary.json",
        "/vault/owner-action-receipt-readiness-owner-queue.json",
        "/vault/owner-action-receipt-readiness-carry-forward.json",
        "/vault/gp030-status.json",
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
                assert b"Vault Owner Action Receipt Readiness Checkpoint" in response.data
