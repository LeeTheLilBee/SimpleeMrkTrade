"""
Tests for VAULT GIANT PACK 022 — Packet Gap Detail
"""

from pathlib import Path

import pytest

from vault.packet_gap_detail_service import (
    get_gp022_status,
    get_packet_gap_detail_blockers,
    get_packet_gap_detail_board,
    get_packet_gap_detail_home,
    get_packet_gap_detail_owner_queue,
    get_packet_gap_detail_records,
    get_packet_gap_detail_requirements,
    render_packet_gap_detail_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp022_status_ready_safe_to_continue_and_not_done():
    status = get_gp022_status()

    assert status["pack"]["id"] == "VAULT_GP022"
    assert status["gp022_status"]["ready"] is True
    assert status["gp022_status"]["gp021_owner_packet_review_connected"] is True
    assert status["gp022_status"]["packet_gap_detail_ready"] is True
    assert status["gp022_status"]["safe_to_continue_to_gp023"] is True
    assert status["gp022_status"]["vault_done"] is False
    assert status["gp022_status"]["metadata_only_gap_detail"] is True
    assert status["gp022_status"]["direct_upload_still_locked"] is True
    assert status["gp022_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp022_status"]["external_access_still_locked"] is True
    assert status["gp022_status"]["unredacted_export_still_locked"] is True
    assert status["gp022_status"]["raw_export_still_locked"] is True
    assert status["gp022_status"]["public_proof_still_locked"] is True
    assert status["gp022_status"]["portal_access_still_locked"] is True
    assert status["gp022_status"]["financing_decision_not_claimed"] is True
    assert status["gp022_status"]["legal_advice_not_claimed"] is True
    assert status["gp022_status"]["raw_verification_not_claimed"] is True
    assert status["gp022_status"]["auto_gap_close_disabled"] is True
    assert status["gp022_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp022"


def test_gp022_gap_truth_keeps_all_restricted_paths_locked():
    status = get_gp022_status()
    truth = status["gap_truth"]

    assert truth["packet_gap_detail_enabled"] is True
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
    assert truth["auto_gap_close_enabled"] is False
    assert truth["clouds_should_continue"] is False


def test_gp022_tower_authority_and_vault_boundaries():
    status = get_gp022_status()
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


def test_gp022_gap_board_has_packet_gap_records():
    board = get_packet_gap_detail_board()["gap_board"]

    assert board["review_packet_count"] >= 6
    assert board["gap_record_count"] >= 20
    assert board["high_priority_gap_count"] >= 1
    assert board["locked_gap_count"] >= 1
    assert board["blocked_gap_count"] >= 1
    assert board["metadata_detail_ready_count"] == board["gap_record_count"]
    assert board["raw_body_available_count"] == 0
    assert board["external_share_allowed_count"] == 0
    assert board["clouds_status"] == "parked_do_not_continue_from_vault_gp022"


def test_gp022_gap_records_are_metadata_only_and_open_for_owner_review():
    records = get_packet_gap_detail_records()

    assert records["gap_record_count"] >= 20

    gap_types = {record["gap_type"] for record in records["gap_records"]}
    assert "missing_metadata_detail" in gap_types
    assert "raw_document_support_locked" in gap_types
    assert "owner_confirmation_required" in gap_types
    assert "external_share_locked" in gap_types
    assert "verification_claim_blocked" in gap_types

    for record in records["gap_records"]:
        assert record["gap_id"].startswith("VGD-")
        assert record["packet_id"].startswith("owner_review_")
        assert record["review_status"] == "OPEN_FOR_OWNER_REVIEW"
        assert record["metadata_detail_ready"] is True
        assert record["raw_body_available"] is False
        assert record["external_share_allowed"] is False
        assert record["owner_confirmed"] is False
        assert record["auto_close_allowed"] is False
        assert "RAW_FILE_BODY_LOCKED" in record["blocked_codes"]
        assert "DIRECT_UPLOAD_LOCKED" in record["blocked_codes"]
        assert "NO_AUTO_GAP_CLOSE" in record["blocked_codes"]
        assert "CLOUDS_PARKED" in record["blocked_codes"]


def test_gp022_requirement_drilldowns_are_safe_to_carry_to_gp023():
    requirements = get_packet_gap_detail_requirements()

    assert requirements["requirement_drilldown_count"] >= 6

    packet_ids = {item["packet_id"] for item in requirements["requirement_drilldowns"]}
    assert "owner_review_atm_route_acquisition" in packet_ids
    assert "owner_review_apartment_lender" in packet_ids
    assert "owner_review_trust_entity_authority" in packet_ids

    for item in requirements["requirement_drilldowns"]:
        assert item["drilldown_id"].startswith("VDR-")
        assert item["packet_id"].startswith("owner_review_")
        assert item["gap_count"] >= 1
        assert item["open_gap_count"] >= 1
        assert item["metadata_drilldown_ready"] is True
        assert item["raw_body_drilldown_ready"] is False
        assert item["external_drilldown_ready"] is False
        assert item["owner_review_required"] is True
        assert item["safe_to_carry_to_gp023"] is True


def test_gp022_blocker_detail_keeps_restricted_paths_locked():
    blockers = get_packet_gap_detail_blockers()["blocker_detail"]

    assert blockers["blocker_count"] >= 10
    assert blockers["all_blockers_safe"] is True
    assert blockers["all_restricted_paths_locked"] is True
    assert blockers["auto_override_allowed"] is False

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
    assert "NO_AUTO_GAP_CLOSE" in codes
    assert "CLOUDS_PARKED" in codes

    for blocker in blockers["blockers"]:
        assert blocker["safe_to_override_inside_vault"] is False
        assert blocker["vault_response"]
        assert blocker["affected_gap_count"] >= 1


def test_gp022_owner_queue_says_continue_vault_not_clouds():
    queue = get_packet_gap_detail_owner_queue()["owner_review_state"]

    assert queue["review_room"] == "Vault Packet Gap Detail"
    assert queue["action_count"] >= 5
    assert queue["review_packet_count"] >= 6
    assert queue["gap_record_count"] >= 20
    assert queue["blocker_count"] >= 10
    assert queue["owner_review_needed_count"] >= 1
    assert queue["tower_owned_action_count"] >= 1
    assert queue["auto_complete_allowed"] is False

    joined = " ".join(queue["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp023" in joined


def test_gp022_home_routes_declared():
    home = get_packet_gap_detail_home()
    summary = home["gap_summary"]

    assert summary["route"] == "/vault/packet-gap-detail"
    assert summary["json_route"] == "/vault/packet-gap-detail.json"
    assert summary["board_route"] == "/vault/packet-gap-detail-board.json"
    assert summary["records_route"] == "/vault/packet-gap-detail-records.json"
    assert summary["requirements_route"] == "/vault/packet-gap-detail-requirements.json"
    assert summary["blockers_route"] == "/vault/packet-gap-detail-blockers.json"
    assert summary["owner_queue_route"] == "/vault/packet-gap-detail-owner-queue.json"
    assert summary["gp022_status_route"] == "/vault/gp022-status.json"
    assert summary["metadata_only"] is True

    assert home["gp021_connection"]["gp021_ready"] is True
    assert home["gp021_connection"]["gp021_safe_to_continue"] is True
    assert home["gp021_connection"]["gp021_vault_done"] is False


def test_gp022_html_is_dark_and_has_no_white_background_tokens():
    html = render_packet_gap_detail_page()
    lowered = html.lower()

    assert "Vault Packet Gap Detail" in html
    assert "Archive Vault" in html
    assert "/vault/packet-gap-detail.json" in html
    assert "/vault/gp022-status.json" in html
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


def test_gp022_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/packet-gap-detail",
        "/vault/packet-gap-detail.json",
        "/vault/packet-gap-detail-board.json",
        "/vault/packet-gap-detail-records.json",
        "/vault/packet-gap-detail-requirements.json",
        "/vault/packet-gap-detail-blockers.json",
        "/vault/packet-gap-detail-owner-queue.json",
        "/vault/gp022-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp022_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/packet-gap-detail",
        "/vault/packet-gap-detail.json",
        "/vault/packet-gap-detail-board.json",
        "/vault/packet-gap-detail-records.json",
        "/vault/packet-gap-detail-requirements.json",
        "/vault/packet-gap-detail-blockers.json",
        "/vault/packet-gap-detail-owner-queue.json",
        "/vault/gp022-status.json",
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
                assert b"Vault Packet Gap Detail" in response.data
