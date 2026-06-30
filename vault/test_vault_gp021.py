"""
Tests for VAULT GIANT PACK 021 — Deepened Owner Packet Review
"""

from pathlib import Path

import pytest

from vault.owner_packet_review_depth_service import (
    get_gp021_status,
    get_owner_packet_review_blockers,
    get_owner_packet_review_board,
    get_owner_packet_review_decision_desk,
    get_owner_packet_review_detail,
    get_owner_packet_review_home,
    get_owner_packet_review_owner_queue,
    render_owner_packet_review_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp021_status_ready_safe_to_continue_and_not_done():
    status = get_gp021_status()

    assert status["pack"]["id"] == "VAULT_GP021"
    assert status["gp021_status"]["ready"] is True
    assert status["gp021_status"]["gp020_checkpoint_connected"] is True
    assert status["gp021_status"]["owner_packet_review_depth_ready"] is True
    assert status["gp021_status"]["safe_to_continue_to_gp022"] is True
    assert status["gp021_status"]["vault_done"] is False
    assert status["gp021_status"]["metadata_only_review"] is True
    assert status["gp021_status"]["direct_upload_still_locked"] is True
    assert status["gp021_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp021_status"]["external_access_still_locked"] is True
    assert status["gp021_status"]["unredacted_export_still_locked"] is True
    assert status["gp021_status"]["raw_export_still_locked"] is True
    assert status["gp021_status"]["public_proof_still_locked"] is True
    assert status["gp021_status"]["portal_access_still_locked"] is True
    assert status["gp021_status"]["financing_decision_not_claimed"] is True
    assert status["gp021_status"]["legal_advice_not_claimed"] is True
    assert status["gp021_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp021"


def test_gp021_review_truth_keeps_all_restricted_paths_locked():
    status = get_gp021_status()
    truth = status["review_truth"]

    assert truth["owner_packet_review_enabled"] is True
    assert truth["metadata_only"] is True
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


def test_gp021_tower_authority_and_vault_boundaries():
    status = get_gp021_status()
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


def test_gp021_board_has_all_owner_packet_lanes():
    board = get_owner_packet_review_board()["review_board"]

    assert board["review_packet_count"] >= 6
    assert board["high_priority_count"] >= 3
    assert board["ready_for_owner_review_count"] == board["review_packet_count"]
    assert board["clouds_status"] == "parked_do_not_continue_from_vault_gp021"

    packet_ids = {packet["packet_id"] for packet in board["review_packets"]}
    assert "owner_review_atm_route_acquisition" in packet_ids
    assert "owner_review_apartment_lender" in packet_ids
    assert "owner_review_trust_entity_authority" in packet_ids
    assert "owner_review_ob_manual_live_private_proof" in packet_ids
    assert "owner_review_soulaana_artist_ip" in packet_ids
    assert "owner_review_private_beta_onboarding" in packet_ids

    for packet in board["review_packets"]:
        assert packet["review_status"] == "READY_FOR_OWNER_REVIEW"
        assert packet["section_count"] >= 4
        assert packet["preview_state"]["redacted_owner_preview_available"] is True
        assert packet["preview_state"]["raw_body_available"] is False
        assert packet["preview_state"]["raw_export_allowed"] is False
        assert packet["preview_state"]["unredacted_export_allowed"] is False
        assert packet["preview_state"]["external_share_allowed"] is False
        assert packet["preview_state"]["public_proof_allowed"] is False
        assert packet["tower_boundary"]["tower_guard_required"] is True
        assert packet["tower_boundary"]["vault_permission_owner"] is False
        assert packet["checkpoint_connection"]["gp020_safe_to_continue"] is True
        assert packet["checkpoint_connection"]["vault_done"] is False


def test_gp021_packet_sections_are_metadata_only():
    board = get_owner_packet_review_board()["review_board"]

    for packet in board["review_packets"]:
        for section in packet["sections"]:
            assert section["status"] == "ready_for_metadata_review"
            assert section["summary_safe"] is True
            assert section["raw_body_available"] is False
            assert section["unredacted_preview_allowed"] is False
            assert section["owner_confirmed"] is False


def test_gp021_detail_records_are_safe_to_carry_to_gp022():
    detail = get_owner_packet_review_detail()

    assert detail["detail_record_count"] >= 6

    for record in detail["review_detail_records"]:
        assert record["detail_id"].startswith("OPRD-")
        assert record["packet_id"].startswith("owner_review_")
        assert record["metadata_detail_ready"] is True
        assert record["raw_body_detail_ready"] is False
        assert record["external_detail_ready"] is False
        assert record["safe_to_carry_to_gp022"] is True
        assert record["sections_ready_count"] >= 4
        assert record["blocked_code_count"] >= 1


def test_gp021_decision_desk_never_auto_applies():
    desk = get_owner_packet_review_decision_desk()["decision_desk"]

    assert desk["decision_count"] >= 6
    assert desk["owner_confirmation_required"] is True
    assert desk["auto_apply_allowed"] is False
    assert desk["financing_decision_allowed"] is False
    assert desk["legal_decision_allowed"] is False
    assert desk["external_share_decision_allowed"] is False

    for decision in desk["decisions"]:
        assert decision["decision_id"].startswith("OPR-DECISION-")
        assert decision["recommended_decision"] == "CONTINUE_METADATA_REVIEW"
        assert decision["owner_must_confirm"] is True
        assert decision["auto_apply_allowed"] is False
        assert decision["reason_auto_apply_blocked"]


def test_gp021_blocker_matrix_keeps_restricted_paths_locked():
    blockers = get_owner_packet_review_blockers()["blocker_matrix"]

    assert blockers["blocker_count"] >= 10
    assert blockers["all_blockers_safe"] is True
    assert blockers["all_restricted_paths_locked"] is True

    codes = {item["code"] for item in blockers["blockers"]}
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "PERMANENT_STORAGE_NOT_CONFIGURED" in codes
    assert "EXTERNAL_ACCESS_DENIED" in codes
    assert "UNREDACTED_EXPORT_LOCKED" in codes
    assert "RAW_EXPORT_LOCKED" in codes
    assert "PUBLIC_PROOF_LOCKED" in codes
    assert "PORTAL_ACCESS_LOCKED" in codes
    assert "NO_FINANCING_DECISION" in codes
    assert "NO_LEGAL_ADVICE" in codes
    assert "NO_RAW_VERIFICATION_CLAIM" in codes
    assert "NO_AUTO_PACKET_APPROVAL" in codes
    assert "CLOUDS_PARKED" in codes

    for blocker in blockers["blockers"]:
        assert blocker["safe_to_override_inside_vault"] is False
        assert blocker["vault_response"]


def test_gp021_owner_queue_says_continue_vault_not_clouds():
    queue = get_owner_packet_review_owner_queue()["owner_review_state"]

    assert queue["review_room"] == "Vault Owner Packet Review"
    assert queue["action_count"] >= 5
    assert queue["review_packet_count"] >= 6
    assert queue["decision_count"] >= 6
    assert queue["blocker_count"] >= 10
    assert queue["owner_review_needed_count"] >= 1
    assert queue["tower_owned_action_count"] >= 1
    assert queue["auto_complete_allowed"] is False

    joined = " ".join(queue["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp022" in joined


def test_gp021_home_routes_declared():
    home = get_owner_packet_review_home()
    summary = home["review_summary"]

    assert summary["route"] == "/vault/owner-packet-review"
    assert summary["json_route"] == "/vault/owner-packet-review.json"
    assert summary["board_route"] == "/vault/owner-packet-review-board.json"
    assert summary["detail_route"] == "/vault/owner-packet-review-detail.json"
    assert summary["decision_desk_route"] == "/vault/owner-packet-review-decision-desk.json"
    assert summary["blockers_route"] == "/vault/owner-packet-review-blockers.json"
    assert summary["owner_queue_route"] == "/vault/owner-packet-review-owner-queue.json"
    assert summary["gp021_status_route"] == "/vault/gp021-status.json"
    assert summary["metadata_only"] is True

    assert home["gp020_checkpoint_connection"]["gp020_ready"] is True
    assert home["gp020_checkpoint_connection"]["gp020_safe_to_continue"] is True
    assert home["gp020_checkpoint_connection"]["gp020_vault_done"] is False


def test_gp021_html_is_dark_and_has_no_white_background_tokens():
    html = render_owner_packet_review_page()
    lowered = html.lower()

    assert "Vault Owner Packet Review" in html
    assert "Archive Vault" in html
    assert "/vault/owner-packet-review.json" in html
    assert "/vault/gp021-status.json" in html
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


def test_gp021_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-packet-review",
        "/vault/owner-packet-review.json",
        "/vault/owner-packet-review-board.json",
        "/vault/owner-packet-review-detail.json",
        "/vault/owner-packet-review-decision-desk.json",
        "/vault/owner-packet-review-blockers.json",
        "/vault/owner-packet-review-owner-queue.json",
        "/vault/gp021-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp021_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/owner-packet-review",
        "/vault/owner-packet-review.json",
        "/vault/owner-packet-review-board.json",
        "/vault/owner-packet-review-detail.json",
        "/vault/owner-packet-review-decision-desk.json",
        "/vault/owner-packet-review-blockers.json",
        "/vault/owner-packet-review-owner-queue.json",
        "/vault/gp021-status.json",
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
                assert b"Vault Owner Packet Review" in response.data
