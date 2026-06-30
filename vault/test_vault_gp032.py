"""
Tests for VAULT GIANT PACK 032 — Packet Component Detail
"""

from pathlib import Path

import pytest

from vault.packet_component_detail_service import (
    get_gp032_status,
    get_packet_component_detail_blockers,
    get_packet_component_detail_carry_forward,
    get_packet_component_detail_home,
    get_packet_component_detail_owner_queue,
    get_packet_component_detail_records,
    get_packet_component_detail_redacted_preview,
    get_packet_component_detail_requirements,
    get_packet_component_detail_tower_gates,
    render_packet_component_detail_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp032_status_ready_and_safe_to_continue():
    status = get_gp032_status()

    assert status["pack"]["id"] == "VAULT_GP032"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["pack"]["section_range"] == "GP031-GP040"
    assert status["gp032_status"]["ready"] is True
    assert status["gp032_status"]["section_id"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["gp032_status"]["gp031_assembly_connected"] is True
    assert status["gp032_status"]["packet_component_detail_ready"] is True
    assert status["gp032_status"]["safe_to_continue_to_gp033"] is True
    assert status["gp032_status"]["vault_done"] is False
    assert status["gp032_status"]["metadata_only_detail"] is True
    assert status["gp032_status"]["private_detail_only"] is True
    assert status["gp032_status"]["owner_review_required"] is True
    assert status["gp032_status"]["owner_confirmation_required"] is True
    assert status["gp032_status"]["owner_confirmed_count"] == 0
    assert status["gp032_status"]["completed_count"] == 0
    assert status["gp032_status"]["auto_completion_disabled"] is True
    assert status["gp032_status"]["auto_confirmation_disabled"] is True
    assert status["gp032_status"]["execution_engine_disabled"] is True
    assert status["gp032_status"]["auto_action_execution_disabled"] is True
    assert status["gp032_status"]["direct_upload_still_locked"] is True
    assert status["gp032_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp032_status"]["external_delivery_still_locked"] is True
    assert status["gp032_status"]["external_access_still_locked"] is True
    assert status["gp032_status"]["packet_export_still_locked"] is True
    assert status["gp032_status"]["unredacted_export_still_locked"] is True
    assert status["gp032_status"]["raw_export_still_locked"] is True
    assert status["gp032_status"]["public_proof_still_locked"] is True
    assert status["gp032_status"]["public_packet_proof_disabled"] is True
    assert status["gp032_status"]["portal_access_still_locked"] is True
    assert status["gp032_status"]["financing_decision_not_claimed"] is True
    assert status["gp032_status"]["legal_advice_not_claimed"] is True
    assert status["gp032_status"]["raw_verification_not_claimed"] is True
    assert status["gp032_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp032"


def test_gp032_truth_keeps_restricted_paths_locked():
    status = get_gp032_status()
    truth = status["detail_truth"]

    assert truth["packet_component_detail_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["private_detail_only"] is True
    assert truth["detail_means_owner_review_not_delivery"] is True
    assert truth["requirement_meaning_enabled"] is True
    assert truth["linked_reference_enabled"] is True
    assert truth["redacted_preview_status_enabled"] is True
    assert truth["tower_gate_state_enabled"] is True
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


def test_gp032_tower_authority_and_vault_boundaries():
    status = get_gp032_status()
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


def test_gp032_detail_records_cover_all_packet_components():
    records = get_packet_component_detail_records()

    assert records["detail_record_count"] == 49

    component_types = {record["component_type"] for record in records["detail_records"]}
    assert "requirement_summary" in component_types
    assert "redacted_preview_slot" in component_types
    assert "receipt_chain_reference" in component_types
    assert "owner_action_reference" in component_types
    assert "tower_gate_status" in component_types
    assert "blocked_path_summary" in component_types
    assert "carry_forward_marker" in component_types

    packet_ids = {record["packet_id"] for record in records["detail_records"]}
    assert "ATM_ROUTE_ACQUISITION_PACKET" in packet_ids
    assert "APARTMENT_LENDER_DUE_DILIGENCE_PACKET" in packet_ids
    assert "TRUST_ENTITY_AUTHORITY_PACKET" in packet_ids
    assert "OB_MANUAL_LIVE_PROOF_PACKET" in packet_ids
    assert "SOULAANA_ARTIST_IP_PACKET" in packet_ids
    assert "PRIVATE_BETA_ONBOARDING_PACKET" in packet_ids
    assert "OWNER_ACTION_RECEIPT_PACKET" in packet_ids

    for record in records["detail_records"]:
        assert record["detail_id"].startswith("VPD-")
        assert record["component_id"].startswith("VPC-")
        assert record["assembly_id"].startswith("VPA-")
        assert record["linked_reference_id"].startswith("VREF-")
        assert record["detail_status"] == "OPEN_FOR_OWNER_REVIEW"
        assert record["metadata_only"] is True
        assert record["private_detail_only"] is True
        assert record["owner_review_required"] is True
        assert record["owner_reviewed"] is False
        assert record["owner_confirmation_required"] is True
        assert record["owner_confirmed"] is False
        assert record["completed"] is False
        assert record["auto_complete_allowed"] is False
        assert record["auto_confirm_allowed"] is False
        assert record["can_execute_from_vault"] is False
        assert record["execution_engine_enabled"] is False
        assert record["raw_body_available"] is False
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
        assert record["tower_can_unlock_later"] is True
        assert record["vault_can_override_tower"] is False
        assert record["ready_for_owner_review"] is True
        assert record["ready_for_external_delivery"] is False
        assert record["ready_for_export"] is False
        assert record["safe_to_carry_to_gp033"] is True
        assert "PACKET_COMPONENT_DETAIL_PRIVATE_ONLY" in record["blocked_codes"]
        assert "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY" in record["blocked_codes"]
        assert "NO_EXTERNAL_PACKET_DELIVERY" in record["blocked_codes"]
        assert "NO_PACKET_EXPORT" in record["blocked_codes"]
        assert "CLOUDS_PARKED" in record["blocked_codes"]


def test_gp032_requirement_meanings_are_metadata_only_no_raw_verification_claim():
    requirements = get_packet_component_detail_requirements()["requirement_meanings"]

    assert requirements["requirement_meaning_count"] == 49
    assert requirements["raw_verification_claimed_count"] == 0
    assert requirements["metadata_only_count"] == 49
    assert requirements["owner_review_required_count"] == 49
    assert requirements["safe_to_continue_requirement_meanings"] is True

    for item in requirements["requirement_meanings"]:
        assert item["requirement_meaning_id"].startswith("VRM-")
        assert item["detail_id"].startswith("VPD-")
        assert item["component_id"].startswith("VPC-")
        assert item["assembly_id"].startswith("VPA-")
        assert item["requirement_purpose"]
        assert item["requirement_meaning"]
        assert item["reference_type"].endswith("_reference")
        assert item["metadata_only"] is True
        assert item["raw_verification_claimed"] is False
        assert item["owner_review_required"] is True
        assert item["safe_to_carry_to_gp033"] is True


def test_gp032_redacted_preview_state_locks_raw_body_and_exports():
    redacted = get_packet_component_detail_redacted_preview()["redacted_preview_state"]

    assert redacted["redacted_preview_count"] == 49
    assert redacted["redacted_preview_slot_count"] == 7
    assert redacted["raw_body_available_count"] == 0
    assert redacted["raw_body_stored_count"] == 0
    assert redacted["direct_upload_unlocked_count"] == 0
    assert redacted["unredacted_export_allowed_count"] == 0
    assert redacted["raw_export_allowed_count"] == 0
    assert redacted["public_packet_proof_allowed_count"] == 0
    assert redacted["safe_to_continue_redacted_preview"] is True

    slot_items = [item for item in redacted["redacted_preview_items"] if item["redacted_preview_only"]]
    assert len(slot_items) == 7

    for item in redacted["redacted_preview_items"]:
        assert item["redacted_preview_id"].startswith("VRP-")
        assert item["detail_id"].startswith("VPD-")
        assert item["component_id"].startswith("VPC-")
        assert item["assembly_id"].startswith("VPA-")
        assert item["raw_body_available"] is False
        assert item["raw_body_stored"] is False
        assert item["direct_upload_unlocked"] is False
        assert item["unredacted_export_allowed"] is False
        assert item["raw_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["metadata_only"] is True


def test_gp032_tower_gate_state_preserves_tower_control():
    tower = get_packet_component_detail_tower_gates()["tower_gate_state"]

    assert tower["tower_gate_count"] == 49
    assert tower["tower_clearance_required_count"] == 49
    assert tower["tower_step_up_required_count"] == 49
    assert tower["vault_override_allowed_count"] == 0
    assert tower["external_delivery_allowed_count"] == 0
    assert tower["packet_export_allowed_count"] == 0
    assert tower["portal_access_allowed_count"] == 0
    assert tower["all_tower_gates_preserved"] is True

    for item in tower["tower_gate_items"]:
        assert item["tower_gate_id"].startswith("VTG-")
        assert item["detail_id"].startswith("VPD-")
        assert item["component_id"].startswith("VPC-")
        assert item["assembly_id"].startswith("VPA-")
        assert item["tower_gate_observed"] is True
        assert item["tower_clearance_required"] is True
        assert item["tower_step_up_required"] is True
        assert item["tower_owns_external_access"] is True
        assert item["tower_owns_export_locks"] is True
        assert item["tower_owns_portal_unlocks"] is True
        assert item["tower_owns_sensitive_visibility"] is True
        assert item["vault_can_override_tower"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["portal_access_allowed"] is False


def test_gp032_blocker_wall_keeps_all_restricted_paths_locked():
    blockers = get_packet_component_detail_blockers()["blocker_wall"]

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
    assert "PACKET_COMPONENT_DETAIL_PRIVATE_ONLY" in codes
    assert "CLOUDS_PARKED" in codes

    for blocker in blockers["blockers"]:
        assert blocker["safe_to_override_inside_vault"] is False
        assert blocker["vault_response"]


def test_gp032_owner_queue_says_continue_vault_not_clouds():
    queue = get_packet_component_detail_owner_queue()["owner_review_state"]

    assert queue["owner_review_item_count"] == 49
    assert queue["ready_for_owner_review_count"] == 49
    assert queue["owner_reviewed_count"] == 0
    assert queue["owner_confirmed_count"] == 0
    assert queue["completed_count"] == 0
    assert queue["auto_completed_count"] == 0
    assert queue["external_delivery_allowed_count"] == 0
    assert queue["packet_export_allowed_count"] == 0
    assert queue["public_packet_proof_allowed_count"] == 0
    assert queue["safe_to_continue_owner_review"] is True

    joined = " ".join(queue["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp033" in joined


def test_gp032_carry_forward_prepares_gp033_not_clouds():
    carry = get_packet_component_detail_carry_forward()["carry_forward"]

    assert carry["carry_forward_count"] == 49
    assert carry["ready_for_gp033_count"] == 49
    assert carry["owner_reviewed_count"] == 0
    assert carry["owner_confirmed_count"] == 0
    assert carry["completed_count"] == 0
    assert carry["external_delivery_allowed_count"] == 0
    assert carry["packet_export_allowed_count"] == 0
    assert carry["public_packet_proof_allowed_count"] == 0
    assert carry["safe_to_carry_to_gp033"] is True
    assert carry["owner_review_item_count"] == 49

    for item in carry["carry_forward_items"]:
        assert item["carry_forward_id"].startswith("VPD-CF-")
        assert item["detail_id"].startswith("VPD-")
        assert item["component_id"].startswith("VPC-")
        assert item["assembly_id"].startswith("VPA-")
        assert item["carry_forward_status"] == "READY_FOR_GP033_PACKET_REVIEW_GROUPING"
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["completed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["safe_to_carry_to_gp033"] is True


def test_gp032_home_routes_declared():
    home = get_packet_component_detail_home()
    summary = home["detail_summary"]

    assert summary["section_header"] == "Archive Vault — Controlled Packet Assembly Layer"
    assert summary["section_range"] == "GP031-GP040"
    assert summary["route"] == "/vault/packet-component-detail"
    assert summary["json_route"] == "/vault/packet-component-detail.json"
    assert summary["records_route"] == "/vault/packet-component-detail-records.json"
    assert summary["requirements_route"] == "/vault/packet-component-detail-requirements.json"
    assert summary["redacted_preview_route"] == "/vault/packet-component-detail-redacted-preview.json"
    assert summary["tower_gates_route"] == "/vault/packet-component-detail-tower-gates.json"
    assert summary["blockers_route"] == "/vault/packet-component-detail-blockers.json"
    assert summary["owner_queue_route"] == "/vault/packet-component-detail-owner-queue.json"
    assert summary["carry_forward_route"] == "/vault/packet-component-detail-carry-forward.json"
    assert summary["gp032_status_route"] == "/vault/gp032-status.json"
    assert summary["detail_record_count"] == 49
    assert summary["requirement_meaning_count"] == 49
    assert summary["metadata_only"] is True

    assert home["gp031_connection"]["gp031_ready"] is True
    assert home["gp031_connection"]["gp031_safe_to_continue"] is True
    assert home["gp031_connection"]["gp031_vault_done"] is False
    assert home["gp031_connection"]["gp031_assembly_record_count"] == 7
    assert home["gp031_connection"]["gp031_component_row_count"] == 49


def test_gp032_html_is_dark_and_has_no_white_background_tokens():
    html = render_packet_component_detail_page()
    lowered = html.lower()

    assert "Vault Packet Component Detail" in html
    assert "Archive Vault" in html
    assert "/vault/packet-component-detail.json" in html
    assert "/vault/gp032-status.json" in html
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


def test_gp032_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/packet-component-detail",
        "/vault/packet-component-detail.json",
        "/vault/packet-component-detail-records.json",
        "/vault/packet-component-detail-requirements.json",
        "/vault/packet-component-detail-redacted-preview.json",
        "/vault/packet-component-detail-tower-gates.json",
        "/vault/packet-component-detail-blockers.json",
        "/vault/packet-component-detail-owner-queue.json",
        "/vault/packet-component-detail-carry-forward.json",
        "/vault/gp032-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp032_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/packet-component-detail",
        "/vault/packet-component-detail.json",
        "/vault/packet-component-detail-records.json",
        "/vault/packet-component-detail-requirements.json",
        "/vault/packet-component-detail-redacted-preview.json",
        "/vault/packet-component-detail-tower-gates.json",
        "/vault/packet-component-detail-blockers.json",
        "/vault/packet-component-detail-owner-queue.json",
        "/vault/packet-component-detail-carry-forward.json",
        "/vault/gp032-status.json",
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
                assert b"Vault Packet Component Detail" in response.data
