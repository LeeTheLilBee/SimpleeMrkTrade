"""
Tests for VAULT GIANT PACK 031 — Controlled Packet Assembly Board
"""

from pathlib import Path

import pytest

from vault.controlled_packet_assembly_board_service import (
    get_gp031_status,
    get_controlled_packet_assembly_blockers,
    get_controlled_packet_assembly_carry_forward,
    get_controlled_packet_assembly_components,
    get_controlled_packet_assembly_home,
    get_controlled_packet_assembly_lanes,
    get_controlled_packet_assembly_owner_queue,
    get_controlled_packet_assembly_readiness,
    get_controlled_packet_assembly_records,
    render_controlled_packet_assembly_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp031_status_ready_new_section_and_safe_to_continue():
    status = get_gp031_status()

    assert status["pack"]["id"] == "VAULT_GP031"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["pack"]["section_range"] == "GP031-GP040"
    assert status["gp031_status"]["ready"] is True
    assert status["gp031_status"]["new_section_started"] is True
    assert status["gp031_status"]["section_id"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["gp031_status"]["gp030_readiness_connected"] is True
    assert status["gp031_status"]["controlled_packet_assembly_board_ready"] is True
    assert status["gp031_status"]["safe_to_continue_to_gp032"] is True
    assert status["gp031_status"]["vault_done"] is False
    assert status["gp031_status"]["metadata_only_assembly"] is True
    assert status["gp031_status"]["private_assembly_only"] is True
    assert status["gp031_status"]["owner_review_required"] is True
    assert status["gp031_status"]["owner_confirmation_required"] is True
    assert status["gp031_status"]["owner_confirmed_count"] == 0
    assert status["gp031_status"]["completed_count"] == 0
    assert status["gp031_status"]["auto_completion_disabled"] is True
    assert status["gp031_status"]["auto_confirmation_disabled"] is True
    assert status["gp031_status"]["execution_engine_disabled"] is True
    assert status["gp031_status"]["auto_action_execution_disabled"] is True
    assert status["gp031_status"]["direct_upload_still_locked"] is True
    assert status["gp031_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp031_status"]["external_delivery_still_locked"] is True
    assert status["gp031_status"]["external_access_still_locked"] is True
    assert status["gp031_status"]["packet_export_still_locked"] is True
    assert status["gp031_status"]["unredacted_export_still_locked"] is True
    assert status["gp031_status"]["raw_export_still_locked"] is True
    assert status["gp031_status"]["public_proof_still_locked"] is True
    assert status["gp031_status"]["public_packet_proof_disabled"] is True
    assert status["gp031_status"]["portal_access_still_locked"] is True
    assert status["gp031_status"]["financing_decision_not_claimed"] is True
    assert status["gp031_status"]["legal_advice_not_claimed"] is True
    assert status["gp031_status"]["raw_verification_not_claimed"] is True
    assert status["gp031_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp031"


def test_gp031_truth_keeps_restricted_paths_locked():
    status = get_gp031_status()
    truth = status["assembly_truth"]

    assert truth["controlled_packet_assembly_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["private_assembly_only"] is True
    assert truth["assembly_means_owner_review_not_delivery"] is True
    assert truth["redacted_preview_slots_allowed"] is True
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


def test_gp031_tower_authority_and_vault_boundaries():
    status = get_gp031_status()
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


def test_gp031_assembly_records_are_metadata_only_private_review():
    records = get_controlled_packet_assembly_records()

    assert records["assembly_record_count"] == 7

    packet_ids = {record["packet_id"] for record in records["assembly_records"]}
    assert "ATM_ROUTE_ACQUISITION_PACKET" in packet_ids
    assert "APARTMENT_LENDER_DUE_DILIGENCE_PACKET" in packet_ids
    assert "TRUST_ENTITY_AUTHORITY_PACKET" in packet_ids
    assert "OB_MANUAL_LIVE_PROOF_PACKET" in packet_ids
    assert "SOULAANA_ARTIST_IP_PACKET" in packet_ids
    assert "PRIVATE_BETA_ONBOARDING_PACKET" in packet_ids
    assert "OWNER_ACTION_RECEIPT_PACKET" in packet_ids

    for record in records["assembly_records"]:
        assert record["assembly_id"].startswith("VPA-")
        assert record["source_checkpoint_id"] == "VAULT_GP030"
        assert record["assembly_status"] == "ASSEMBLY_BOARD_OPEN_OWNER_REVIEW"
        assert record["metadata_only"] is True
        assert record["private_assembly_only"] is True
        assert record["owner_review_required"] is True
        assert record["owner_confirmation_required"] is True
        assert record["owner_reviewed"] is False
        assert record["owner_confirmed"] is False
        assert record["completed"] is False
        assert record["auto_complete_allowed"] is False
        assert record["auto_confirm_allowed"] is False
        assert record["can_execute_from_vault"] is False
        assert record["execution_engine_enabled"] is False
        assert record["redacted_preview_slot_ready"] is True
        assert record["raw_body_included"] is False
        assert record["raw_file_body_storage_enabled"] is False
        assert record["direct_upload_unlocked"] is False
        assert record["external_delivery_allowed"] is False
        assert record["external_access_allowed"] is False
        assert record["packet_export_allowed"] is False
        assert record["raw_export_allowed"] is False
        assert record["unredacted_export_allowed"] is False
        assert record["public_packet_proof_allowed"] is False
        assert record["portal_access_allowed"] is False
        assert record["tower_gate_observed"] is True
        assert record["tower_clearance_required"] is True
        assert record["tower_step_up_required"] is True
        assert record["component_row_count"] == 7
        assert record["open_component_count"] == 7
        assert record["completed_component_count"] == 0
        assert record["blocked_component_count"] == 7
        assert record["ready_for_owner_review"] is True
        assert record["ready_for_external_delivery"] is False
        assert record["ready_for_export"] is False
        assert record["safe_to_carry_to_gp032"] is True
        assert "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY" in record["blocked_codes"]
        assert "NO_EXTERNAL_PACKET_DELIVERY" in record["blocked_codes"]
        assert "NO_PACKET_EXPORT" in record["blocked_codes"]
        assert "CLOUDS_PARKED" in record["blocked_codes"]


def test_gp031_component_rows_are_open_blocked_and_not_complete():
    components = get_controlled_packet_assembly_components()

    assert components["component_row_count"] == 49

    component_types = {row["component_type"] for row in components["component_rows"]}
    assert "requirement_summary" in component_types
    assert "redacted_preview_slot" in component_types
    assert "receipt_chain_reference" in component_types
    assert "owner_action_reference" in component_types
    assert "tower_gate_status" in component_types
    assert "blocked_path_summary" in component_types
    assert "carry_forward_marker" in component_types

    for row in components["component_rows"]:
        assert row["component_id"].startswith("VPC-")
        assert row["assembly_id"].startswith("VPA-")
        assert row["required"] is True
        assert row["status"] == "OPEN"
        assert row["blocked"] is True
        assert row["completed"] is False
        assert row["auto_completed"] is False
        assert row["metadata_only"] is True
        assert row["raw_body_available"] is False
        assert row["external_delivery_allowed"] is False
        assert row["packet_export_allowed"] is False
        assert row["public_packet_proof_allowed"] is False
        assert row["owner_review_required"] is True
        assert row["owner_confirmed"] is False
        assert row["can_execute_from_vault"] is False
        assert "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY" in row["blocked_codes"]
        assert "NO_EXTERNAL_PACKET_DELIVERY" in row["blocked_codes"]
        assert "NO_PACKET_EXPORT" in row["blocked_codes"]
        assert "CLOUDS_PARKED" in row["blocked_codes"]


def test_gp031_lane_board_groups_all_packet_lanes():
    lanes = get_controlled_packet_assembly_lanes()["lane_board"]

    assert lanes["lane_count"] == 7
    assert lanes["open_lane_count"] == 7
    assert lanes["completed_lane_count"] == 0
    assert lanes["blocked_lane_count"] == 7
    assert lanes["external_delivery_allowed_count"] == 0
    assert lanes["packet_export_allowed_count"] == 0
    assert lanes["public_packet_proof_allowed_count"] == 0
    assert lanes["all_lanes_metadata_only"] is True
    assert lanes["safe_to_continue_lane_board"] is True

    lane_names = {lane["lane"] for lane in lanes["lanes"]}
    assert "atm_route" in lane_names
    assert "apartment_lender" in lane_names
    assert "trust_entity" in lane_names
    assert "ob_manual_live" in lane_names
    assert "soulaana_ip" in lane_names
    assert "private_beta" in lane_names
    assert "owner_action_receipts" in lane_names

    for lane in lanes["lanes"]:
        assert lane["lane_id"].startswith("assembly_lane_")
        assert lane["component_count"] == 7
        assert lane["open_component_count"] == 7
        assert lane["completed_component_count"] == 0
        assert lane["blocked_component_count"] == 7
        assert lane["metadata_only"] is True
        assert lane["external_delivery_allowed"] is False
        assert lane["packet_export_allowed"] is False
        assert lane["public_packet_proof_allowed"] is False
        assert lane["tower_clearance_required"] is True
        assert lane["safe_to_carry_to_gp032"] is True


def test_gp031_blocker_wall_keeps_all_restricted_paths_locked():
    blockers = get_controlled_packet_assembly_blockers()["blocker_wall"]

    assert blockers["blocker_count"] >= 20
    assert blockers["all_blockers_safe"] is True
    assert blockers["auto_override_allowed"] is False
    assert blockers["all_restricted_paths_locked"] is True
    assert blockers["raw_storage_allowed"] is False
    assert blockers["direct_upload_allowed"] is False
    assert blockers["external_delivery_allowed"] is False
    assert blockers["packet_export_allowed"] is False
    assert blockers["public_packet_proof_allowed"] is False
    assert blockers["portal_access_allowed"] is False

    codes = {item["code"] for item in blockers["blockers"]}
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
    assert "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY" in codes
    assert "CLOUDS_PARKED" in codes

    for blocker in blockers["blockers"]:
        assert blocker["safe_to_override_inside_vault"] is False
        assert blocker["vault_response"]


def test_gp031_readiness_is_owner_review_only_not_delivery():
    readiness = get_controlled_packet_assembly_readiness()["assembly_readiness"]

    assert readiness["readiness_item_count"] == 7
    assert readiness["ready_for_owner_review_count"] == 7
    assert readiness["completed_count"] == 0
    assert readiness["owner_confirmed_count"] == 0
    assert readiness["external_delivery_allowed_count"] == 0
    assert readiness["packet_export_allowed_count"] == 0
    assert readiness["public_packet_proof_allowed_count"] == 0
    assert readiness["blocked_component_count"] == 49
    assert readiness["safe_to_continue_to_gp032"] is True

    for item in readiness["readiness_items"]:
        assert item["readiness_id"].startswith("VPAR-")
        assert item["assembly_id"].startswith("VPA-")
        assert item["readiness_status"] == "READY_FOR_OWNER_REVIEW_EXTERNAL_DELIVERY_BLOCKED"
        assert item["component_count"] == 7
        assert item["open_component_count"] == 7
        assert item["completed_component_count"] == 0
        assert item["blocked_component_count"] == 7
        assert item["owner_review_required"] is True
        assert item["owner_confirmed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["safe_to_carry_to_gp032"] is True


def test_gp031_carry_forward_prepares_gp032_not_clouds():
    carry = get_controlled_packet_assembly_carry_forward()["carry_forward"]

    assert carry["carry_forward_count"] == 7
    assert carry["ready_for_gp032_count"] == 7
    assert carry["owner_confirmed_count"] == 0
    assert carry["completed_count"] == 0
    assert carry["external_delivery_allowed_count"] == 0
    assert carry["packet_export_allowed_count"] == 0
    assert carry["public_packet_proof_allowed_count"] == 0
    assert carry["safe_to_carry_to_gp032"] is True

    for item in carry["carry_forward_items"]:
        assert item["carry_forward_id"].startswith("VPA-CF-")
        assert item["assembly_id"].startswith("VPA-")
        assert item["carry_forward_status"] == "READY_FOR_GP032_PACKET_COMPONENT_DETAIL"
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["completed_count"] == 0
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["safe_to_carry_to_gp032"] is True


def test_gp031_owner_queue_says_continue_vault_not_clouds():
    queue = get_controlled_packet_assembly_owner_queue()["owner_review_state"]

    assert queue["review_room"] == "Vault Controlled Packet Assembly Board"
    assert queue["section_header"] == "Archive Vault — Controlled Packet Assembly Layer"
    assert queue["section_range"] == "GP031-GP040"
    assert queue["action_count"] >= 5
    assert queue["assembly_record_count"] == 7
    assert queue["lane_count"] == 7
    assert queue["blocker_count"] >= 20
    assert queue["carry_forward_count"] == 7
    assert queue["ready_action_count"] >= 1
    assert queue["tower_owned_action_count"] >= 1
    assert queue["auto_complete_allowed"] is False
    assert queue["external_delivery_allowed"] is False
    assert queue["packet_export_allowed"] is False
    assert queue["public_packet_proof_allowed"] is False

    joined = " ".join(queue["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp032" in joined


def test_gp031_home_routes_declared():
    home = get_controlled_packet_assembly_home()
    summary = home["assembly_summary"]

    assert summary["section_header"] == "Archive Vault — Controlled Packet Assembly Layer"
    assert summary["section_range"] == "GP031-GP040"
    assert summary["route"] == "/vault/controlled-packet-assembly"
    assert summary["json_route"] == "/vault/controlled-packet-assembly.json"
    assert summary["records_route"] == "/vault/controlled-packet-assembly-records.json"
    assert summary["components_route"] == "/vault/controlled-packet-assembly-components.json"
    assert summary["lanes_route"] == "/vault/controlled-packet-assembly-lanes.json"
    assert summary["blockers_route"] == "/vault/controlled-packet-assembly-blockers.json"
    assert summary["readiness_route"] == "/vault/controlled-packet-assembly-readiness.json"
    assert summary["owner_queue_route"] == "/vault/controlled-packet-assembly-owner-queue.json"
    assert summary["carry_forward_route"] == "/vault/controlled-packet-assembly-carry-forward.json"
    assert summary["gp031_status_route"] == "/vault/gp031-status.json"
    assert summary["assembly_record_count"] == 7
    assert summary["component_row_count"] == 49
    assert summary["metadata_only"] is True

    assert home["gp030_connection"]["gp030_ready"] is True
    assert home["gp030_connection"]["gp030_safe_to_continue"] is True
    assert home["gp030_connection"]["gp030_vault_done"] is False
    assert home["gp030_connection"]["gp030_section_closed"] is True


def test_gp031_html_is_dark_and_has_no_white_background_tokens():
    html = render_controlled_packet_assembly_page()
    lowered = html.lower()

    assert "Vault Controlled Packet Assembly Board" in html
    assert "Archive Vault" in html
    assert "New Section" in html
    assert "/vault/controlled-packet-assembly.json" in html
    assert "/vault/gp031-status.json" in html
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


def test_gp031_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/controlled-packet-assembly",
        "/vault/controlled-packet-assembly.json",
        "/vault/controlled-packet-assembly-records.json",
        "/vault/controlled-packet-assembly-components.json",
        "/vault/controlled-packet-assembly-lanes.json",
        "/vault/controlled-packet-assembly-blockers.json",
        "/vault/controlled-packet-assembly-readiness.json",
        "/vault/controlled-packet-assembly-owner-queue.json",
        "/vault/controlled-packet-assembly-carry-forward.json",
        "/vault/gp031-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp031_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/controlled-packet-assembly",
        "/vault/controlled-packet-assembly.json",
        "/vault/controlled-packet-assembly-records.json",
        "/vault/controlled-packet-assembly-components.json",
        "/vault/controlled-packet-assembly-lanes.json",
        "/vault/controlled-packet-assembly-blockers.json",
        "/vault/controlled-packet-assembly-readiness.json",
        "/vault/controlled-packet-assembly-owner-queue.json",
        "/vault/controlled-packet-assembly-carry-forward.json",
        "/vault/gp031-status.json",
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
                assert b"Vault Controlled Packet Assembly Board" in response.data
