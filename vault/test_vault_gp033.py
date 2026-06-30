"""
Tests for VAULT GIANT PACK 033 — Packet Review Grouping
"""

from pathlib import Path

import pytest

from vault.packet_review_grouping_service import (
    get_gp033_status,
    get_packet_review_grouping_blockers,
    get_packet_review_grouping_carry_forward,
    get_packet_review_grouping_groups,
    get_packet_review_grouping_home,
    get_packet_review_grouping_lanes,
    get_packet_review_grouping_owner_queue,
    get_packet_review_grouping_redacted_preview,
    get_packet_review_grouping_tower_gates,
    render_packet_review_grouping_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp033_status_ready_and_safe_to_continue():
    status = get_gp033_status()

    assert status["pack"]["id"] == "VAULT_GP033"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["pack"]["section_range"] == "GP031-GP040"
    assert status["gp033_status"]["ready"] is True
    assert status["gp033_status"]["section_id"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["gp033_status"]["gp032_component_detail_connected"] is True
    assert status["gp033_status"]["packet_review_grouping_ready"] is True
    assert status["gp033_status"]["safe_to_continue_to_gp034"] is True
    assert status["gp033_status"]["vault_done"] is False
    assert status["gp033_status"]["metadata_only_grouping"] is True
    assert status["gp033_status"]["private_grouping_only"] is True
    assert status["gp033_status"]["owner_review_required"] is True
    assert status["gp033_status"]["owner_confirmation_required"] is True
    assert status["gp033_status"]["owner_confirmed_count"] == 0
    assert status["gp033_status"]["completed_count"] == 0
    assert status["gp033_status"]["auto_completion_disabled"] is True
    assert status["gp033_status"]["auto_confirmation_disabled"] is True
    assert status["gp033_status"]["execution_engine_disabled"] is True
    assert status["gp033_status"]["auto_action_execution_disabled"] is True
    assert status["gp033_status"]["direct_upload_still_locked"] is True
    assert status["gp033_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp033_status"]["external_delivery_still_locked"] is True
    assert status["gp033_status"]["external_access_still_locked"] is True
    assert status["gp033_status"]["packet_export_still_locked"] is True
    assert status["gp033_status"]["unredacted_export_still_locked"] is True
    assert status["gp033_status"]["raw_export_still_locked"] is True
    assert status["gp033_status"]["public_proof_still_locked"] is True
    assert status["gp033_status"]["public_packet_proof_disabled"] is True
    assert status["gp033_status"]["portal_access_still_locked"] is True
    assert status["gp033_status"]["financing_decision_not_claimed"] is True
    assert status["gp033_status"]["legal_advice_not_claimed"] is True
    assert status["gp033_status"]["raw_verification_not_claimed"] is True
    assert status["gp033_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp033"


def test_gp033_truth_keeps_restricted_paths_locked():
    status = get_gp033_status()
    truth = status["grouping_truth"]

    assert truth["packet_review_grouping_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["private_grouping_only"] is True
    assert truth["grouping_means_owner_review_not_delivery"] is True
    assert truth["review_lanes_enabled"] is True
    assert truth["redacted_preview_grouping_enabled"] is True
    assert truth["tower_gate_grouping_enabled"] is True
    assert truth["blocker_grouping_enabled"] is True
    assert truth["owner_review_state_enabled"] is True
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["direct_upload_unlocked"] is False
    assert truth["provider_configured"] is False
    assert truth["external_packet_delivery_enabled"] is False
    assert truth["external_access_enabled"] is False
    assert truth["packet_export_enabled"] is False
    assert truth["unredacted_export_enabled"] is False
    assert truth["raw_export_enabled"] is False
    assert truth["public_packet_proof_enabled"] is False
    assert truth["public_proof_enabled"] is False
    assert truth["portal_access_enabled"] is False
    assert truth["owner_confirmed_count"] == 0
    assert truth["completed_count"] == 0
    assert truth["auto_completion_enabled"] is False
    assert truth["auto_confirmation_enabled"] is False
    assert truth["execution_engine_enabled"] is False
    assert truth["auto_action_execution_enabled"] is False
    assert truth["financing_decision_enabled"] is False
    assert truth["legal_advice_enabled"] is False
    assert truth["raw_document_verification_claimed"] is False
    assert truth["auto_packet_approval_enabled"] is False
    assert truth["clouds_should_continue"] is False


def test_gp033_tower_authority_and_vault_boundaries():
    status = get_gp033_status()
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
    assert vault["external_packet_delivery_allowed"] is False
    assert vault["packet_export_allowed"] is False
    assert vault["unredacted_export_allowed"] is False
    assert vault["raw_export_allowed"] is False
    assert vault["redacted_owner_preview_allowed"] is True
    assert vault["sensitive_body_display_in_summary_views"] is False
    assert vault["beneficiary_details_in_summary_views"] is False
    assert vault["broker_secret_storage_allowed"] is False
    assert vault["public_ob_proof_allowed"] is False
    assert vault["public_packet_proof_allowed"] is False
    assert vault["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp033_review_groups_cover_all_packets_and_details():
    groups = get_packet_review_grouping_groups()

    assert groups["review_group_count"] == 7

    packet_ids = {group["packet_id"] for group in groups["review_groups"]}
    assert "ATM_ROUTE_ACQUISITION_PACKET" in packet_ids
    assert "APARTMENT_LENDER_DUE_DILIGENCE_PACKET" in packet_ids
    assert "TRUST_ENTITY_AUTHORITY_PACKET" in packet_ids
    assert "OB_MANUAL_LIVE_PROOF_PACKET" in packet_ids
    assert "SOULAANA_ARTIST_IP_PACKET" in packet_ids
    assert "PRIVATE_BETA_ONBOARDING_PACKET" in packet_ids
    assert "OWNER_ACTION_RECEIPT_PACKET" in packet_ids

    assert sum(group["detail_count"] for group in groups["review_groups"]) == 49
    assert sum(group["redacted_preview_slot_count"] for group in groups["review_groups"]) == 7

    for group in groups["review_groups"]:
        assert group["review_group_id"].startswith("VPG-")
        assert group["assembly_id"].startswith("VPA-")
        assert group["review_group_status"] == "OPEN_FOR_OWNER_REVIEW_DELIVERY_BLOCKED"
        assert group["metadata_only"] is True
        assert group["private_grouping_only"] is True
        assert group["owner_review_required"] is True
        assert group["owner_reviewed"] is False
        assert group["owner_confirmation_required"] is True
        assert group["owner_confirmed"] is False
        assert group["completed"] is False
        assert group["auto_complete_allowed"] is False
        assert group["auto_confirm_allowed"] is False
        assert group["can_execute_from_vault"] is False
        assert group["execution_engine_enabled"] is False
        assert group["detail_count"] == 7
        assert len(group["detail_ids"]) == 7
        assert len(group["component_ids"]) == 7
        assert group["redacted_preview_slot_count"] == 1
        assert group["tower_gate_count"] == 7
        assert group["raw_body_available_count"] == 0
        assert group["raw_file_body_storage_enabled"] is False
        assert group["direct_upload_unlocked"] is False
        assert group["external_delivery_allowed"] is False
        assert group["external_access_allowed"] is False
        assert group["packet_export_allowed"] is False
        assert group["raw_export_allowed"] is False
        assert group["unredacted_export_allowed"] is False
        assert group["public_packet_proof_allowed"] is False
        assert group["portal_access_allowed"] is False
        assert group["ready_for_owner_review"] is True
        assert group["ready_for_external_delivery"] is False
        assert group["ready_for_export"] is False
        assert group["safe_to_carry_to_gp034"] is True
        assert "PACKET_REVIEW_GROUPING_PRIVATE_ONLY" in group["blocked_codes"]
        assert "NO_EXTERNAL_PACKET_DELIVERY" in group["blocked_codes"]
        assert "NO_PACKET_EXPORT" in group["blocked_codes"]
        assert "CLOUDS_PARKED" in group["blocked_codes"]


def test_gp033_review_lanes_are_private_owner_review_only():
    lanes = get_packet_review_grouping_lanes()["review_lanes"]

    assert lanes["review_lane_count"] == 42
    assert lanes["lane_type_count"] == 6
    assert lanes["packet_group_count"] == 7
    assert lanes["tower_owned_lane_count"] == 7
    assert lanes["owner_review_required_count"] == 42
    assert lanes["completed_lane_count"] == 0
    assert lanes["external_delivery_allowed_count"] == 0
    assert lanes["packet_export_allowed_count"] == 0
    assert lanes["public_packet_proof_allowed_count"] == 0
    assert lanes["all_lanes_metadata_only"] is True
    assert lanes["safe_to_continue_review_lanes"] is True

    lane_types = {lane["lane_type"] for lane in lanes["review_lanes"]}
    assert lane_types == {
        "requirements",
        "redacted_preview",
        "receipt_references",
        "tower_gates",
        "blocked_paths",
        "carry_forward",
    }

    for lane in lanes["review_lanes"]:
        assert lane["review_lane_id"].startswith("VPL-")
        assert lane["review_group_id"].startswith("VPG-")
        assert lane["assembly_id"].startswith("VPA-")
        assert lane["lane_status"] == "OPEN_FOR_OWNER_REVIEW"
        assert lane["metadata_only"] is True
        assert lane["owner_review_required"] is True
        assert lane["owner_reviewed"] is False
        assert lane["completed"] is False
        assert lane["auto_complete_allowed"] is False
        assert lane["external_delivery_allowed"] is False
        assert lane["packet_export_allowed"] is False
        assert lane["public_packet_proof_allowed"] is False
        assert lane["safe_to_carry_to_gp034"] is True


def test_gp033_redacted_preview_grouping_locks_raw_body_and_exports():
    redacted = get_packet_review_grouping_redacted_preview()["redacted_preview_grouping"]

    assert redacted["redacted_preview_group_count"] == 7
    assert redacted["total_redacted_preview_slot_count"] == 7
    assert redacted["raw_body_available_count"] == 0
    assert redacted["raw_body_stored_count"] == 0
    assert redacted["direct_upload_unlocked_count"] == 0
    assert redacted["unredacted_export_allowed_count"] == 0
    assert redacted["raw_export_allowed_count"] == 0
    assert redacted["public_packet_proof_allowed_count"] == 0
    assert redacted["safe_to_continue_redacted_preview_grouping"] is True

    for group in redacted["redacted_preview_groups"]:
        assert group["redacted_preview_group_id"].startswith("VRPG-")
        assert group["review_group_id"].startswith("VPG-")
        assert group["assembly_id"].startswith("VPA-")
        assert group["redacted_preview_slot_count"] == 1
        assert group["redacted_preview_state"] == "REDACTED_PREVIEW_GROUP_RESERVED_NO_RAW_BODY"
        assert group["metadata_only"] is True
        assert group["raw_body_available"] is False
        assert group["raw_body_stored"] is False
        assert group["direct_upload_unlocked"] is False
        assert group["unredacted_export_allowed"] is False
        assert group["raw_export_allowed"] is False
        assert group["public_packet_proof_allowed"] is False
        assert group["owner_review_required"] is True
        assert group["safe_to_carry_to_gp034"] is True


def test_gp033_tower_gate_grouping_preserves_tower_control():
    tower = get_packet_review_grouping_tower_gates()["tower_gate_grouping"]

    assert tower["tower_gate_group_count"] == 7
    assert tower["tower_clearance_required_count"] == 7
    assert tower["tower_step_up_required_count"] == 7
    assert tower["vault_override_allowed_count"] == 0
    assert tower["external_delivery_allowed_count"] == 0
    assert tower["packet_export_allowed_count"] == 0
    assert tower["portal_access_allowed_count"] == 0
    assert tower["all_tower_gate_groups_preserved"] is True

    for group in tower["tower_gate_groups"]:
        assert group["tower_gate_group_id"].startswith("VTGG-")
        assert group["review_group_id"].startswith("VPG-")
        assert group["assembly_id"].startswith("VPA-")
        assert group["tower_gate_count"] == 7
        assert group["tower_clearance_required"] is True
        assert group["tower_step_up_required"] is True
        assert group["tower_owns_external_access"] is True
        assert group["tower_owns_export_locks"] is True
        assert group["tower_owns_portal_unlocks"] is True
        assert group["tower_owns_sensitive_visibility"] is True
        assert group["vault_can_override_tower"] is False
        assert group["external_delivery_allowed"] is False
        assert group["packet_export_allowed"] is False
        assert group["portal_access_allowed"] is False
        assert group["safe_to_carry_to_gp034"] is True


def test_gp033_blocker_grouping_keeps_all_restricted_paths_locked():
    blockers = get_packet_review_grouping_blockers()["blocker_grouping"]

    assert blockers["blocker_group_count"] == 7
    assert blockers["active_block_code_count"] >= 20
    assert blockers["all_blocker_groups_safe"] is True
    assert blockers["auto_override_allowed"] is False
    assert blockers["all_restricted_paths_locked"] is True
    assert blockers["raw_storage_allowed"] is False
    assert blockers["direct_upload_allowed"] is False
    assert blockers["external_delivery_allowed"] is False
    assert blockers["packet_export_allowed"] is False
    assert blockers["public_packet_proof_allowed"] is False
    assert blockers["portal_access_allowed"] is False

    codes = set(blockers["active_block_codes"])
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "EXTERNAL_ACCESS_DENIED" in codes
    assert "UNREDACTED_EXPORT_LOCKED" in codes
    assert "RAW_EXPORT_LOCKED" in codes
    assert "PUBLIC_PACKET_PROOF_LOCKED" in codes
    assert "PORTAL_ACCESS_LOCKED" in codes
    assert "TOWER_CLEARANCE_REQUIRED" in codes
    assert "TOWER_STEP_UP_REQUIRED" in codes
    assert "NO_EXTERNAL_PACKET_DELIVERY" in codes
    assert "NO_PACKET_EXPORT" in codes
    assert "NO_FINANCING_DECISION" in codes
    assert "NO_LEGAL_ADVICE" in codes
    assert "NO_RAW_VERIFICATION_CLAIM" in codes
    assert "PACKET_REVIEW_GROUPING_PRIVATE_ONLY" in codes
    assert "CLOUDS_PARKED" in codes

    for group in blockers["blocker_groups"]:
        assert group["blocker_group_id"].startswith("VBG-")
        assert group["review_group_id"].startswith("VPG-")
        assert group["assembly_id"].startswith("VPA-")
        assert group["blocked_code_count"] >= 20
        assert group["all_restricted_paths_locked"] is True
        assert group["safe_to_override_inside_vault"] is False
        assert group["raw_storage_allowed"] is False
        assert group["direct_upload_allowed"] is False
        assert group["external_delivery_allowed"] is False
        assert group["packet_export_allowed"] is False
        assert group["public_packet_proof_allowed"] is False
        assert group["portal_access_allowed"] is False
        assert group["safe_to_carry_to_gp034"] is True


def test_gp033_owner_queue_says_continue_vault_not_clouds():
    queue = get_packet_review_grouping_owner_queue()["owner_review_state"]

    assert queue["owner_review_item_count"] == 7
    assert queue["ready_for_owner_review_count"] == 7
    assert queue["owner_reviewed_count"] == 0
    assert queue["owner_confirmed_count"] == 0
    assert queue["completed_count"] == 0
    assert queue["auto_completed_count"] == 0
    assert queue["review_lane_count"] == 42
    assert queue["blocker_group_count"] == 7
    assert queue["external_delivery_allowed_count"] == 0
    assert queue["packet_export_allowed_count"] == 0
    assert queue["public_packet_proof_allowed_count"] == 0
    assert queue["safe_to_continue_owner_review"] is True

    joined = " ".join(queue["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp034" in joined


def test_gp033_carry_forward_prepares_gp034_not_clouds():
    carry = get_packet_review_grouping_carry_forward()["carry_forward"]

    assert carry["carry_forward_count"] == 7
    assert carry["ready_for_gp034_count"] == 7
    assert carry["owner_reviewed_count"] == 0
    assert carry["owner_confirmed_count"] == 0
    assert carry["completed_count"] == 0
    assert carry["external_delivery_allowed_count"] == 0
    assert carry["packet_export_allowed_count"] == 0
    assert carry["public_packet_proof_allowed_count"] == 0
    assert carry["safe_to_carry_to_gp034"] is True
    assert carry["owner_review_item_count"] == 7

    for item in carry["carry_forward_items"]:
        assert item["carry_forward_id"].startswith("VPG-CF-")
        assert item["review_group_id"].startswith("VPG-")
        assert item["assembly_id"].startswith("VPA-")
        assert item["carry_forward_status"] == "READY_FOR_GP034_PACKET_REVIEW_PRIORITY"
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["completed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["safe_to_carry_to_gp034"] is True


def test_gp033_home_routes_declared():
    home = get_packet_review_grouping_home()
    summary = home["grouping_summary"]

    assert summary["section_header"] == "Archive Vault — Controlled Packet Assembly Layer"
    assert summary["section_range"] == "GP031-GP040"
    assert summary["route"] == "/vault/packet-review-grouping"
    assert summary["json_route"] == "/vault/packet-review-grouping.json"
    assert summary["groups_route"] == "/vault/packet-review-grouping-groups.json"
    assert summary["lanes_route"] == "/vault/packet-review-grouping-lanes.json"
    assert summary["redacted_preview_route"] == "/vault/packet-review-grouping-redacted-preview.json"
    assert summary["tower_gates_route"] == "/vault/packet-review-grouping-tower-gates.json"
    assert summary["blockers_route"] == "/vault/packet-review-grouping-blockers.json"
    assert summary["owner_queue_route"] == "/vault/packet-review-grouping-owner-queue.json"
    assert summary["carry_forward_route"] == "/vault/packet-review-grouping-carry-forward.json"
    assert summary["gp033_status_route"] == "/vault/gp033-status.json"
    assert summary["review_group_count"] == 7
    assert summary["detail_record_count"] == 49
    assert summary["review_lane_count"] == 42
    assert summary["metadata_only"] is True

    assert home["gp032_connection"]["gp032_ready"] is True
    assert home["gp032_connection"]["gp032_safe_to_continue"] is True
    assert home["gp032_connection"]["gp032_vault_done"] is False
    assert home["gp032_connection"]["gp032_detail_record_count"] == 49
    assert home["gp032_connection"]["gp032_redacted_preview_slot_count"] == 7


def test_gp033_html_is_dark_and_has_no_white_background_tokens():
    html = render_packet_review_grouping_page()
    lowered = html.lower()

    assert "Vault Packet Review Grouping" in html
    assert "Archive Vault" in html
    assert "/vault/packet-review-grouping.json" in html
    assert "/vault/gp033-status.json" in html
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


def test_gp033_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/packet-review-grouping",
        "/vault/packet-review-grouping.json",
        "/vault/packet-review-grouping-groups.json",
        "/vault/packet-review-grouping-lanes.json",
        "/vault/packet-review-grouping-redacted-preview.json",
        "/vault/packet-review-grouping-tower-gates.json",
        "/vault/packet-review-grouping-blockers.json",
        "/vault/packet-review-grouping-owner-queue.json",
        "/vault/packet-review-grouping-carry-forward.json",
        "/vault/gp033-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp033_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/packet-review-grouping",
        "/vault/packet-review-grouping.json",
        "/vault/packet-review-grouping-groups.json",
        "/vault/packet-review-grouping-lanes.json",
        "/vault/packet-review-grouping-redacted-preview.json",
        "/vault/packet-review-grouping-tower-gates.json",
        "/vault/packet-review-grouping-blockers.json",
        "/vault/packet-review-grouping-owner-queue.json",
        "/vault/packet-review-grouping-carry-forward.json",
        "/vault/gp033-status.json",
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
                assert b"Vault Packet Review Grouping" in response.data
