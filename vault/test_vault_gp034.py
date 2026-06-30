"""
Tests for VAULT GIANT PACK 034 — Packet Review Priority
"""

from pathlib import Path

import pytest

from vault.packet_review_priority_service import (
    get_gp034_status,
    get_packet_review_priority_blocker_severity,
    get_packet_review_priority_carry_forward,
    get_packet_review_priority_home,
    get_packet_review_priority_next_actions,
    get_packet_review_priority_owner_focus,
    get_packet_review_priority_reasons,
    get_packet_review_priority_records,
    get_packet_review_priority_tower_urgency,
    render_packet_review_priority_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp034_status_ready_and_safe_to_continue():
    status = get_gp034_status()

    assert status["pack"]["id"] == "VAULT_GP034"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["pack"]["section_range"] == "GP031-GP040"
    assert status["gp034_status"]["ready"] is True
    assert status["gp034_status"]["section_id"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["gp034_status"]["gp033_review_grouping_connected"] is True
    assert status["gp034_status"]["packet_review_priority_ready"] is True
    assert status["gp034_status"]["safe_to_continue_to_gp035"] is True
    assert status["gp034_status"]["vault_done"] is False
    assert status["gp034_status"]["metadata_only_priority"] is True
    assert status["gp034_status"]["private_priority_only"] is True
    assert status["gp034_status"]["owner_review_required"] is True
    assert status["gp034_status"]["owner_confirmation_required"] is True
    assert status["gp034_status"]["owner_confirmed_count"] == 0
    assert status["gp034_status"]["completed_count"] == 0
    assert status["gp034_status"]["auto_completion_disabled"] is True
    assert status["gp034_status"]["auto_confirmation_disabled"] is True
    assert status["gp034_status"]["execution_engine_disabled"] is True
    assert status["gp034_status"]["auto_action_execution_disabled"] is True
    assert status["gp034_status"]["direct_upload_still_locked"] is True
    assert status["gp034_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp034_status"]["external_delivery_still_locked"] is True
    assert status["gp034_status"]["external_access_still_locked"] is True
    assert status["gp034_status"]["packet_export_still_locked"] is True
    assert status["gp034_status"]["unredacted_export_still_locked"] is True
    assert status["gp034_status"]["raw_export_still_locked"] is True
    assert status["gp034_status"]["public_proof_still_locked"] is True
    assert status["gp034_status"]["public_packet_proof_disabled"] is True
    assert status["gp034_status"]["portal_access_still_locked"] is True
    assert status["gp034_status"]["financing_decision_not_claimed"] is True
    assert status["gp034_status"]["legal_advice_not_claimed"] is True
    assert status["gp034_status"]["raw_verification_not_claimed"] is True
    assert status["gp034_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp034"


def test_gp034_truth_keeps_restricted_paths_locked():
    status = get_gp034_status()
    truth = status["priority_truth"]

    assert truth["packet_review_priority_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["private_priority_only"] is True
    assert truth["priority_means_owner_focus_not_delivery"] is True
    assert truth["priority_ranking_enabled"] is True
    assert truth["reason_codes_enabled"] is True
    assert truth["owner_focus_order_enabled"] is True
    assert truth["blocker_severity_enabled"] is True
    assert truth["tower_gate_urgency_enabled"] is True
    assert truth["next_action_sorting_enabled"] is True
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


def test_gp034_tower_authority_and_vault_boundaries():
    status = get_gp034_status()
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


def test_gp034_priority_records_rank_owner_focus_order():
    records = get_packet_review_priority_records()

    assert records["priority_record_count"] == 7

    ordered_packet_ids = [record["packet_id"] for record in records["priority_records"]]
    assert ordered_packet_ids == [
        "ATM_ROUTE_ACQUISITION_PACKET",
        "APARTMENT_LENDER_DUE_DILIGENCE_PACKET",
        "TRUST_ENTITY_AUTHORITY_PACKET",
        "OB_MANUAL_LIVE_PROOF_PACKET",
        "SOULAANA_ARTIST_IP_PACKET",
        "PRIVATE_BETA_ONBOARDING_PACKET",
        "OWNER_ACTION_RECEIPT_PACKET",
    ]

    ranks = [record["priority_rank"] for record in records["priority_records"]]
    assert ranks == [1, 2, 3, 4, 5, 6, 7]

    for record in records["priority_records"]:
        assert record["priority_id"].startswith("VPR-")
        assert record["review_group_id"].startswith("VPG-")
        assert record["assembly_id"].startswith("VPA-")
        assert record["priority_status"] == "READY_FOR_OWNER_FOCUS_EXTERNAL_DELIVERY_BLOCKED"
        assert record["metadata_only"] is True
        assert record["private_priority_only"] is True
        assert record["owner_review_required"] is True
        assert record["owner_reviewed"] is False
        assert record["owner_confirmation_required"] is True
        assert record["owner_confirmed"] is False
        assert record["completed"] is False
        assert record["auto_complete_allowed"] is False
        assert record["auto_confirm_allowed"] is False
        assert record["can_execute_from_vault"] is False
        assert record["execution_engine_enabled"] is False
        assert record["detail_count"] == 7
        assert record["review_lane_count"] == 6
        assert record["redacted_preview_slot_count"] == 1
        assert record["tower_gate_count"] == 7
        assert record["raw_body_available_count"] == 0
        assert record["raw_file_body_storage_enabled"] is False
        assert record["direct_upload_unlocked"] is False
        assert record["external_delivery_allowed"] is False
        assert record["external_access_allowed"] is False
        assert record["packet_export_allowed"] is False
        assert record["raw_export_allowed"] is False
        assert record["unredacted_export_allowed"] is False
        assert record["public_packet_proof_allowed"] is False
        assert record["portal_access_allowed"] is False
        assert record["ready_for_owner_focus"] is True
        assert record["ready_for_external_delivery"] is False
        assert record["ready_for_export"] is False
        assert record["safe_to_carry_to_gp035"] is True
        assert "PACKET_REVIEW_PRIORITY_PRIVATE_ONLY" in record["blocked_codes"]
        assert "NO_EXTERNAL_PACKET_DELIVERY" in record["blocked_codes"]
        assert "NO_PACKET_EXPORT" in record["blocked_codes"]
        assert "CLOUDS_PARKED" in record["blocked_codes"]


def test_gp034_priority_reasons_exist_for_each_packet():
    reasons = get_packet_review_priority_reasons()["priority_reasons"]

    assert reasons["priority_reason_count"] == 28
    assert reasons["packet_count"] == 7
    assert reasons["metadata_only_count"] == 28
    assert reasons["external_delivery_allowed_count"] == 0
    assert reasons["packet_export_allowed_count"] == 0
    assert reasons["safe_to_continue_priority_reasons"] is True

    codes = {item["reason_code"] for item in reasons["priority_reason_items"]}
    assert "ATM_ROUTE_ACQUISITION_FIRST" in codes
    assert "APARTMENT_LENDER_PACKET_SECOND" in codes
    assert "TRUST_ENTITY_AUTHORITY_PACKET_THIRD" in codes
    assert "OB_MANUAL_LIVE_PRIVATE_PROOF" in codes
    assert "SOULAANA_ARTIST_IP_BOUNDARY" in codes
    assert "PRIVATE_BETA_ONBOARDING" in codes
    assert "OWNER_ACTION_RECEIPT_CONTEXT" in codes

    for item in reasons["priority_reason_items"]:
        assert item["reason_id"].startswith("VPRR-")
        assert item["priority_id"].startswith("VPR-")
        assert item["review_group_id"].startswith("VPG-")
        assert item["priority_rank"] >= 1
        assert item["metadata_only"] is True
        assert item["owner_review_required"] is True
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["safe_to_carry_to_gp035"] is True


def test_gp034_owner_focus_order_is_private_and_not_delivery():
    focus = get_packet_review_priority_owner_focus()["owner_focus_order"]

    assert focus["owner_focus_item_count"] == 7
    assert focus["first_focus_packet_id"] == "ATM_ROUTE_ACQUISITION_PACKET"
    assert focus["last_focus_packet_id"] == "OWNER_ACTION_RECEIPT_PACKET"
    assert focus["owner_reviewed_count"] == 0
    assert focus["owner_confirmed_count"] == 0
    assert focus["completed_count"] == 0
    assert focus["external_delivery_allowed_count"] == 0
    assert focus["packet_export_allowed_count"] == 0
    assert focus["safe_to_continue_owner_focus"] is True

    for item in focus["owner_focus_items"]:
        assert item["owner_focus_id"].startswith("VPFO-")
        assert item["priority_id"].startswith("VPR-")
        assert item["review_group_id"].startswith("VPG-")
        assert item["focus_status"] == "READY_FOR_OWNER_FOCUS_ONLY"
        assert item["metadata_only"] is True
        assert item["owner_review_required"] is True
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["completed"] is False
        assert item["auto_complete_allowed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["safe_to_carry_to_gp035"] is True


def test_gp034_blocker_severity_keeps_restricted_paths_locked():
    severity = get_packet_review_priority_blocker_severity()["blocker_severity"]

    assert severity["blocker_severity_item_count"] == 7
    assert severity["critical_count"] == 2
    assert severity["high_count"] == 3
    assert severity["medium_count"] == 2
    assert severity["all_restricted_paths_locked"] is True
    assert severity["safe_to_override_inside_vault_count"] == 0
    assert severity["external_delivery_allowed_count"] == 0
    assert severity["packet_export_allowed_count"] == 0
    assert severity["public_packet_proof_allowed_count"] == 0
    assert severity["safe_to_continue_blocker_severity"] is True

    for item in severity["blocker_severity_items"]:
        assert item["blocker_severity_id"].startswith("VBS-")
        assert item["priority_id"].startswith("VPR-")
        assert item["review_group_id"].startswith("VPG-")
        assert item["blocker_severity"] in {"critical", "high", "medium"}
        assert item["blocked_code_count"] >= 20
        assert item["all_restricted_paths_locked"] is True
        assert item["safe_to_override_inside_vault"] is False
        assert item["raw_storage_allowed"] is False
        assert item["direct_upload_allowed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["safe_to_carry_to_gp035"] is True


def test_gp034_tower_urgency_preserves_tower_control():
    tower = get_packet_review_priority_tower_urgency()["tower_urgency"]

    assert tower["tower_urgency_item_count"] == 7
    assert tower["high_urgency_count"] == 3
    assert tower["medium_urgency_count"] == 4
    assert tower["tower_clearance_required_count"] == 7
    assert tower["tower_step_up_required_count"] == 7
    assert tower["vault_override_allowed_count"] == 0
    assert tower["external_delivery_allowed_count"] == 0
    assert tower["packet_export_allowed_count"] == 0
    assert tower["portal_access_allowed_count"] == 0
    assert tower["all_tower_urgency_preserved"] is True

    for item in tower["tower_urgency_items"]:
        assert item["tower_urgency_id"].startswith("VTU-")
        assert item["priority_id"].startswith("VPR-")
        assert item["review_group_id"].startswith("VPG-")
        assert item["tower_gate_urgency"] in {"high", "medium"}
        assert item["tower_gate_count"] == 7
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
        assert item["safe_to_carry_to_gp035"] is True


def test_gp034_next_actions_sorted_and_continue_vault_not_clouds():
    actions = get_packet_review_priority_next_actions()["next_actions"]

    assert actions["next_action_count"] == 9
    assert actions["packet_action_count"] == 7
    assert actions["boundary_action_count"] == 1
    assert actions["next_build_action_count"] == 1
    assert actions["owner_review_required_count"] == 9
    assert actions["completed_count"] == 0
    assert actions["owner_confirmed_count"] == 0
    assert actions["external_delivery_allowed_count"] == 0
    assert actions["packet_export_allowed_count"] == 0
    assert actions["public_packet_proof_allowed_count"] == 0
    assert actions["safe_to_continue_next_actions"] is True

    ranks = [item["priority_rank"] for item in actions["next_actions"]]
    assert ranks == sorted(ranks)

    assert actions["next_actions"][0]["packet_id"] == "ATM_ROUTE_ACQUISITION_PACKET"
    assert actions["next_actions"][1]["packet_id"] == "APARTMENT_LENDER_DUE_DILIGENCE_PACKET"
    assert actions["next_actions"][-1]["packet_id"] == "NEXT_VAULT_PACK"

    joined = " ".join(actions["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp035" in joined

    for item in actions["next_actions"]:
        assert item["next_action_id"].startswith("VPNX-")
        assert item["metadata_only"] is True
        assert item["owner_review_required"] is True
        assert item["owner_confirmed"] is False
        assert item["completed"] is False
        assert item["auto_complete_allowed"] is False
        assert item["auto_confirm_allowed"] is False
        assert item["can_execute_from_vault"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["safe_to_carry_to_gp035"] is True


def test_gp034_carry_forward_prepares_gp035():
    carry = get_packet_review_priority_carry_forward()["carry_forward"]

    assert carry["carry_forward_count"] == 7
    assert carry["ready_for_gp035_count"] == 7
    assert carry["owner_reviewed_count"] == 0
    assert carry["owner_confirmed_count"] == 0
    assert carry["completed_count"] == 0
    assert carry["external_delivery_allowed_count"] == 0
    assert carry["packet_export_allowed_count"] == 0
    assert carry["public_packet_proof_allowed_count"] == 0
    assert carry["safe_to_carry_to_gp035"] is True
    assert carry["next_action_count"] == 9

    for item in carry["carry_forward_items"]:
        assert item["carry_forward_id"].startswith("VPR-CF-")
        assert item["priority_id"].startswith("VPR-")
        assert item["review_group_id"].startswith("VPG-")
        assert item["carry_forward_status"] == "READY_FOR_GP035_PACKET_REVIEW_DECISION_PREP"
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["completed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["safe_to_carry_to_gp035"] is True


def test_gp034_home_routes_declared():
    home = get_packet_review_priority_home()
    summary = home["priority_summary"]

    assert summary["section_header"] == "Archive Vault — Controlled Packet Assembly Layer"
    assert summary["section_range"] == "GP031-GP040"
    assert summary["route"] == "/vault/packet-review-priority"
    assert summary["json_route"] == "/vault/packet-review-priority.json"
    assert summary["records_route"] == "/vault/packet-review-priority-records.json"
    assert summary["reasons_route"] == "/vault/packet-review-priority-reasons.json"
    assert summary["owner_focus_route"] == "/vault/packet-review-priority-owner-focus.json"
    assert summary["blocker_severity_route"] == "/vault/packet-review-priority-blocker-severity.json"
    assert summary["tower_urgency_route"] == "/vault/packet-review-priority-tower-urgency.json"
    assert summary["next_actions_route"] == "/vault/packet-review-priority-next-actions.json"
    assert summary["carry_forward_route"] == "/vault/packet-review-priority-carry-forward.json"
    assert summary["gp034_status_route"] == "/vault/gp034-status.json"
    assert summary["priority_record_count"] == 7
    assert summary["next_action_count"] == 9
    assert summary["metadata_only"] is True

    assert home["gp033_connection"]["gp033_ready"] is True
    assert home["gp033_connection"]["gp033_safe_to_continue"] is True
    assert home["gp033_connection"]["gp033_vault_done"] is False
    assert home["gp033_connection"]["gp033_review_group_count"] == 7
    assert home["gp033_connection"]["gp033_review_lane_count"] == 42
    assert home["gp033_connection"]["gp033_detail_record_count"] == 49


def test_gp034_html_is_dark_and_has_no_white_background_tokens():
    html = render_packet_review_priority_page()
    lowered = html.lower()

    assert "Vault Packet Review Priority" in html
    assert "Archive Vault" in html
    assert "/vault/packet-review-priority.json" in html
    assert "/vault/gp034-status.json" in html
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


def test_gp034_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/packet-review-priority",
        "/vault/packet-review-priority.json",
        "/vault/packet-review-priority-records.json",
        "/vault/packet-review-priority-reasons.json",
        "/vault/packet-review-priority-owner-focus.json",
        "/vault/packet-review-priority-blocker-severity.json",
        "/vault/packet-review-priority-tower-urgency.json",
        "/vault/packet-review-priority-next-actions.json",
        "/vault/packet-review-priority-carry-forward.json",
        "/vault/gp034-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp034_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/packet-review-priority",
        "/vault/packet-review-priority.json",
        "/vault/packet-review-priority-records.json",
        "/vault/packet-review-priority-reasons.json",
        "/vault/packet-review-priority-owner-focus.json",
        "/vault/packet-review-priority-blocker-severity.json",
        "/vault/packet-review-priority-tower-urgency.json",
        "/vault/packet-review-priority-next-actions.json",
        "/vault/packet-review-priority-carry-forward.json",
        "/vault/gp034-status.json",
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
                assert b"Vault Packet Review Priority" in response.data
