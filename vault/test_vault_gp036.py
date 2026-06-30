"""
Tests for VAULT GIANT PACK 036 — Owner Decision Review
"""

from pathlib import Path

import pytest

from vault.owner_decision_review_service import (
    get_gp036_status,
    get_owner_decision_review_blocker_ack,
    get_owner_decision_review_cards,
    get_owner_decision_review_carry_forward,
    get_owner_decision_review_home,
    get_owner_decision_review_next_reviews,
    get_owner_decision_review_no_execution,
    get_owner_decision_review_selection_preview,
    get_owner_decision_review_status,
    get_owner_decision_review_tower_ack,
    render_owner_decision_review_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp036_status_ready_and_safe_to_continue():
    status = get_gp036_status()

    assert status["pack"]["id"] == "VAULT_GP036"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["pack"]["section_range"] == "GP031-GP040"
    assert status["gp036_status"]["ready"] is True
    assert status["gp036_status"]["section_id"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["gp036_status"]["gp035_decision_prep_connected"] is True
    assert status["gp036_status"]["owner_decision_review_ready"] is True
    assert status["gp036_status"]["safe_to_continue_to_gp037"] is True
    assert status["gp036_status"]["vault_done"] is False
    assert status["gp036_status"]["metadata_only_review"] is True
    assert status["gp036_status"]["private_owner_review_only"] is True
    assert status["gp036_status"]["owner_review_required"] is True
    assert status["gp036_status"]["owner_confirmation_required"] is True
    assert status["gp036_status"]["owner_reviewed_count"] == 0
    assert status["gp036_status"]["owner_confirmed_count"] == 0
    assert status["gp036_status"]["decision_selected_count"] == 0
    assert status["gp036_status"]["completed_count"] == 0
    assert status["gp036_status"]["auto_completion_disabled"] is True
    assert status["gp036_status"]["auto_confirmation_disabled"] is True
    assert status["gp036_status"]["approval_disabled"] is True
    assert status["gp036_status"]["execution_engine_disabled"] is True
    assert status["gp036_status"]["auto_action_execution_disabled"] is True
    assert status["gp036_status"]["direct_upload_still_locked"] is True
    assert status["gp036_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp036_status"]["external_delivery_still_locked"] is True
    assert status["gp036_status"]["external_access_still_locked"] is True
    assert status["gp036_status"]["packet_export_still_locked"] is True
    assert status["gp036_status"]["unredacted_export_still_locked"] is True
    assert status["gp036_status"]["raw_export_still_locked"] is True
    assert status["gp036_status"]["public_proof_still_locked"] is True
    assert status["gp036_status"]["public_packet_proof_disabled"] is True
    assert status["gp036_status"]["portal_access_still_locked"] is True
    assert status["gp036_status"]["financing_decision_not_claimed"] is True
    assert status["gp036_status"]["legal_advice_not_claimed"] is True
    assert status["gp036_status"]["raw_verification_not_claimed"] is True
    assert status["gp036_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp036"


def test_gp036_truth_keeps_restricted_paths_locked():
    status = get_gp036_status()
    truth = status["review_truth"]

    assert truth["owner_decision_review_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["private_owner_review_only"] is True
    assert truth["review_means_owner_visibility_not_approval"] is True
    assert truth["review_cards_enabled"] is True
    assert truth["safe_selection_preview_enabled"] is True
    assert truth["tower_gate_ack_enabled"] is True
    assert truth["blocker_ack_enabled"] is True
    assert truth["no_execution_confirmation_enabled"] is True
    assert truth["next_review_sorting_enabled"] is True
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
    assert truth["owner_reviewed_count"] == 0
    assert truth["owner_confirmed_count"] == 0
    assert truth["decision_selected_count"] == 0
    assert truth["completed_count"] == 0
    assert truth["auto_completion_enabled"] is False
    assert truth["auto_confirmation_enabled"] is False
    assert truth["approval_enabled"] is False
    assert truth["execution_engine_enabled"] is False
    assert truth["auto_action_execution_enabled"] is False
    assert truth["financing_decision_enabled"] is False
    assert truth["legal_advice_enabled"] is False
    assert truth["raw_document_verification_claimed"] is False
    assert truth["auto_packet_approval_enabled"] is False
    assert truth["clouds_should_continue"] is False


def test_gp036_tower_authority_and_vault_boundaries():
    status = get_gp036_status()
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


def test_gp036_review_cards_cover_decision_prep_packets():
    cards = get_owner_decision_review_cards()

    assert cards["review_card_count"] == 7

    ordered_packet_ids = [card["packet_id"] for card in cards["review_cards"]]
    assert ordered_packet_ids == [
        "ATM_ROUTE_ACQUISITION_PACKET",
        "APARTMENT_LENDER_DUE_DILIGENCE_PACKET",
        "TRUST_ENTITY_AUTHORITY_PACKET",
        "OB_MANUAL_LIVE_PROOF_PACKET",
        "SOULAANA_ARTIST_IP_PACKET",
        "PRIVATE_BETA_ONBOARDING_PACKET",
        "OWNER_ACTION_RECEIPT_PACKET",
    ]

    for card in cards["review_cards"]:
        assert card["review_card_id"].startswith("VODR-")
        assert card["decision_prep_id"].startswith("VDR-")
        assert card["priority_id"].startswith("VPR-")
        assert card["review_group_id"].startswith("VPG-")
        assert card["assembly_id"].startswith("VPA-")
        assert card["review_card_status"] == "READY_FOR_OWNER_REVIEW_NO_DECISION_SELECTED"
        assert len(card["review_steps"]) == 6
        assert "confirm_no_execution" in card["review_steps"]
        assert card["metadata_only"] is True
        assert card["private_owner_review_only"] is True
        assert card["owner_review_required"] is True
        assert card["owner_reviewed"] is False
        assert card["owner_confirmation_required"] is True
        assert card["owner_confirmed"] is False
        assert card["decision_selected"] is False
        assert card["selected_decision_code"] is None
        assert card["completed"] is False
        assert card["auto_complete_allowed"] is False
        assert card["auto_confirm_allowed"] is False
        assert card["approval_allowed"] is False
        assert card["can_execute_from_vault"] is False
        assert card["execution_engine_enabled"] is False
        assert card["tower_ack_required"] is True
        assert card["tower_acknowledged"] is False
        assert card["blocker_ack_required"] is True
        assert card["blocker_acknowledged"] is False
        assert card["no_execution_confirmation_required"] is True
        assert card["no_execution_confirmed"] is False
        assert card["raw_body_available_count"] == 0
        assert card["raw_file_body_storage_enabled"] is False
        assert card["direct_upload_unlocked"] is False
        assert card["external_delivery_allowed"] is False
        assert card["external_access_allowed"] is False
        assert card["packet_export_allowed"] is False
        assert card["raw_export_allowed"] is False
        assert card["unredacted_export_allowed"] is False
        assert card["public_packet_proof_allowed"] is False
        assert card["portal_access_allowed"] is False
        assert card["tower_clearance_required"] is True
        assert card["tower_step_up_required"] is True
        assert card["vault_can_override_tower"] is False
        assert card["safe_to_review_privately"] is True
        assert card["safe_to_deliver_externally"] is False
        assert card["safe_to_export"] is False
        assert card["safe_to_carry_to_gp037"] is True
        assert "OWNER_DECISION_REVIEW_PRIVATE_ONLY" in card["blocked_codes"]
        assert "NO_EXTERNAL_PACKET_DELIVERY" in card["blocked_codes"]
        assert "NO_PACKET_EXPORT" in card["blocked_codes"]
        assert "CLOUDS_PARKED" in card["blocked_codes"]


def test_gp036_review_status_never_auto_selects_or_confirms():
    status = get_owner_decision_review_status()["review_status"]

    assert status["review_status_count"] == 7
    assert status["owner_review_required_count"] == 7
    assert status["owner_reviewed_count"] == 0
    assert status["owner_confirmed_count"] == 0
    assert status["decision_selected_count"] == 0
    assert status["completed_count"] == 0
    assert status["external_delivery_allowed_count"] == 0
    assert status["packet_export_allowed_count"] == 0
    assert status["execution_allowed_count"] == 0
    assert status["safe_to_continue_review_status"] is True

    for item in status["review_status_items"]:
        assert item["review_status_id"].startswith("VODRS-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["review_card_status"] == "READY_FOR_OWNER_REVIEW_NO_DECISION_SELECTED"
        assert item["owner_review_required"] is True
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["decision_selected"] is False
        assert item["completed"] is False
        assert item["metadata_only"] is True
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["can_execute_from_vault"] is False
        assert item["safe_to_carry_to_gp037"] is True


def test_gp036_selection_preview_is_not_selection():
    preview = get_owner_decision_review_selection_preview()["selection_preview"]

    assert preview["selection_preview_count"] == 7
    assert preview["safe_selection_preview_count"] == 7
    assert preview["decision_selected_count"] == 0
    assert preview["owner_confirmed_count"] == 0
    assert preview["auto_confirm_allowed_count"] == 0
    assert preview["approval_allowed_count"] == 0
    assert preview["executes_action_count"] == 0
    assert preview["external_delivery_allowed_count"] == 0
    assert preview["packet_export_allowed_count"] == 0
    assert preview["safe_to_continue_selection_preview"] is True

    for item in preview["selection_preview_items"]:
        assert item["selection_preview_id"].startswith("VODSP-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["selection_preview_status"] == "SAFE_SELECTION_PREVIEW_ONLY_NOT_SELECTED"
        assert item["safe_selection_preview"] is True
        assert item["decision_selected"] is False
        assert item["selected_decision_code"] is None
        assert item["metadata_only"] is True
        assert item["owner_review_required"] is True
        assert item["owner_confirmed"] is False
        assert item["auto_confirm_allowed"] is False
        assert item["approval_allowed"] is False
        assert item["executes_action"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["safe_to_carry_to_gp037"] is True


def test_gp036_tower_ack_preserves_tower_control():
    tower = get_owner_decision_review_tower_ack()["tower_ack"]

    assert tower["tower_ack_count"] == 7
    assert tower["tower_ack_required_count"] == 7
    assert tower["tower_acknowledged_count"] == 0
    assert tower["tower_clearance_required_count"] == 7
    assert tower["tower_step_up_required_count"] == 7
    assert tower["tower_export_lock_required_count"] == 7
    assert tower["vault_override_allowed_count"] == 0
    assert tower["external_delivery_allowed_count"] == 0
    assert tower["packet_export_allowed_count"] == 0
    assert tower["portal_access_allowed_count"] == 0
    assert tower["all_tower_acks_preserve_authority"] is True

    for item in tower["tower_ack_items"]:
        assert item["tower_ack_id"].startswith("VODTA-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["tower_ack_status"] == "TOWER_GATES_VISIBLE_NOT_ACKNOWLEDGED"
        assert item["tower_ack_required"] is True
        assert item["tower_acknowledged"] is False
        assert item["tower_clearance_required"] is True
        assert item["tower_step_up_required"] is True
        assert item["tower_export_lock_required"] is True
        assert item["tower_external_access_required"] is True
        assert item["tower_portal_unlock_required"] is True
        assert item["tower_sensitive_visibility_required"] is True
        assert item["vault_can_override_tower"] is False
        assert item["metadata_only"] is True
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["safe_to_carry_to_gp037"] is True


def test_gp036_blocker_ack_keeps_all_restricted_paths_locked():
    blocker = get_owner_decision_review_blocker_ack()["blocker_ack"]

    assert blocker["blocker_ack_count"] == 7
    assert blocker["active_block_code_count"] >= 20
    assert blocker["blocker_ack_required_count"] == 7
    assert blocker["blocker_acknowledged_count"] == 0
    assert blocker["all_restricted_paths_locked"] is True
    assert blocker["safe_to_override_inside_vault_count"] == 0
    assert blocker["external_delivery_allowed_count"] == 0
    assert blocker["packet_export_allowed_count"] == 0
    assert blocker["public_packet_proof_allowed_count"] == 0
    assert blocker["execution_allowed_count"] == 0
    assert blocker["safe_to_continue_blocker_ack"] is True

    codes = set(blocker["active_block_codes"])
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "NO_EXTERNAL_PACKET_DELIVERY" in codes
    assert "NO_PACKET_EXPORT" in codes
    assert "NO_ACTION_EXECUTION_FROM_VAULT" in codes
    assert "OWNER_DECISION_REVIEW_PRIVATE_ONLY" in codes
    assert "CLOUDS_PARKED" in codes

    for item in blocker["blocker_ack_items"]:
        assert item["blocker_ack_id"].startswith("VODBA-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["blocker_ack_status"] == "BLOCKERS_VISIBLE_NOT_ACKNOWLEDGED"
        assert item["blocker_ack_required"] is True
        assert item["blocker_acknowledged"] is False
        assert item["all_restricted_paths_locked"] is True
        assert item["safe_to_override_inside_vault"] is False
        assert item["raw_storage_allowed"] is False
        assert item["direct_upload_allowed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["execution_allowed"] is False
        assert item["metadata_only"] is True
        assert item["safe_to_carry_to_gp037"] is True


def test_gp036_no_execution_confirmation_disables_execution_and_approval():
    no_execution = get_owner_decision_review_no_execution()["no_execution"]

    assert no_execution["no_execution_confirmation_count"] == 7
    assert no_execution["no_execution_confirmation_required_count"] == 7
    assert no_execution["no_execution_confirmed_count"] == 0
    assert no_execution["auto_action_execution_enabled_count"] == 0
    assert no_execution["execution_engine_enabled_count"] == 0
    assert no_execution["approval_allowed_count"] == 0
    assert no_execution["financing_decision_enabled_count"] == 0
    assert no_execution["legal_advice_enabled_count"] == 0
    assert no_execution["raw_document_verification_claimed_count"] == 0
    assert no_execution["auto_packet_approval_enabled_count"] == 0
    assert no_execution["external_delivery_allowed_count"] == 0
    assert no_execution["packet_export_allowed_count"] == 0
    assert no_execution["safe_to_continue_no_execution"] is True

    for item in no_execution["no_execution_items"]:
        assert item["no_execution_id"].startswith("VODNE-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["no_execution_status"] == "NO_EXECUTION_CONFIRMATION_REQUIRED_NOT_CONFIRMED"
        assert item["no_execution_confirmation_required"] is True
        assert item["no_execution_confirmed"] is False
        assert item["auto_action_execution_enabled"] is False
        assert item["execution_engine_enabled"] is False
        assert item["approval_allowed"] is False
        assert item["financing_decision_enabled"] is False
        assert item["legal_advice_enabled"] is False
        assert item["raw_document_verification_claimed"] is False
        assert item["auto_packet_approval_enabled"] is False
        assert item["metadata_only"] is True
        assert item["owner_confirmed"] is False
        assert item["completed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["safe_to_carry_to_gp037"] is True


def test_gp036_next_reviews_sorted_and_continue_vault_not_clouds():
    reviews = get_owner_decision_review_next_reviews()["next_reviews"]

    assert reviews["next_review_count"] == 9
    assert reviews["packet_review_count"] == 7
    assert reviews["boundary_review_count"] == 1
    assert reviews["next_build_review_count"] == 1
    assert reviews["owner_review_required_count"] == 9
    assert reviews["owner_reviewed_count"] == 0
    assert reviews["decision_selected_count"] == 0
    assert reviews["owner_confirmed_count"] == 0
    assert reviews["completed_count"] == 0
    assert reviews["external_delivery_allowed_count"] == 0
    assert reviews["packet_export_allowed_count"] == 0
    assert reviews["public_packet_proof_allowed_count"] == 0
    assert reviews["safe_to_continue_next_reviews"] is True

    ranks = [item["priority_rank"] for item in reviews["next_review_items"]]
    assert ranks == sorted(ranks)

    assert reviews["next_review_items"][0]["packet_id"] == "ATM_ROUTE_ACQUISITION_PACKET"
    assert reviews["next_review_items"][1]["packet_id"] == "APARTMENT_LENDER_DUE_DILIGENCE_PACKET"
    assert reviews["next_review_items"][-1]["packet_id"] == "NEXT_VAULT_PACK"

    joined = " ".join(reviews["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp037" in joined

    for item in reviews["next_review_items"]:
        assert item["next_review_id"].startswith("VODNR-")
        assert item["metadata_only"] is True
        assert item["owner_review_required"] is True
        assert item["owner_reviewed"] is False
        assert item["tower_ack_required"] is True
        assert item["tower_acknowledged"] is False
        assert item["blocker_ack_required"] is True
        assert item["blocker_acknowledged"] is False
        assert item["no_execution_confirmation_required"] is True
        assert item["no_execution_confirmed"] is False
        assert item["decision_selected"] is False
        assert item["owner_confirmed"] is False
        assert item["completed"] is False
        assert item["auto_complete_allowed"] is False
        assert item["auto_confirm_allowed"] is False
        assert item["approval_allowed"] is False
        assert item["can_execute_from_vault"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["safe_to_carry_to_gp037"] is True


def test_gp036_carry_forward_prepares_gp037():
    carry = get_owner_decision_review_carry_forward()["carry_forward"]

    assert carry["carry_forward_count"] == 7
    assert carry["ready_for_gp037_count"] == 7
    assert carry["owner_reviewed_count"] == 0
    assert carry["tower_acknowledged_count"] == 0
    assert carry["blocker_acknowledged_count"] == 0
    assert carry["no_execution_confirmed_count"] == 0
    assert carry["owner_confirmed_count"] == 0
    assert carry["decision_selected_count"] == 0
    assert carry["completed_count"] == 0
    assert carry["external_delivery_allowed_count"] == 0
    assert carry["packet_export_allowed_count"] == 0
    assert carry["public_packet_proof_allowed_count"] == 0
    assert carry["safe_to_carry_to_gp037"] is True
    assert carry["next_review_count"] == 9

    for item in carry["carry_forward_items"]:
        assert item["carry_forward_id"].startswith("VODR-CF-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["priority_id"].startswith("VPR-")
        assert item["review_group_id"].startswith("VPG-")
        assert item["carry_forward_status"] == "READY_FOR_GP037_REVIEWED_DECISION_RECEIPT_STAGING"
        assert item["owner_reviewed"] is False
        assert item["tower_acknowledged"] is False
        assert item["blocker_acknowledged"] is False
        assert item["no_execution_confirmed"] is False
        assert item["owner_confirmed"] is False
        assert item["decision_selected"] is False
        assert item["completed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["safe_to_carry_to_gp037"] is True


def test_gp036_home_routes_declared():
    home = get_owner_decision_review_home()
    summary = home["review_summary"]

    assert summary["section_header"] == "Archive Vault — Controlled Packet Assembly Layer"
    assert summary["section_range"] == "GP031-GP040"
    assert summary["route"] == "/vault/owner-decision-review"
    assert summary["json_route"] == "/vault/owner-decision-review.json"
    assert summary["cards_route"] == "/vault/owner-decision-review-cards.json"
    assert summary["status_route"] == "/vault/owner-decision-review-status.json"
    assert summary["selection_preview_route"] == "/vault/owner-decision-review-selection-preview.json"
    assert summary["tower_ack_route"] == "/vault/owner-decision-review-tower-ack.json"
    assert summary["blocker_ack_route"] == "/vault/owner-decision-review-blocker-ack.json"
    assert summary["no_execution_route"] == "/vault/owner-decision-review-no-execution.json"
    assert summary["next_reviews_route"] == "/vault/owner-decision-review-next-reviews.json"
    assert summary["carry_forward_route"] == "/vault/owner-decision-review-carry-forward.json"
    assert summary["gp036_status_route"] == "/vault/gp036-status.json"
    assert summary["review_card_count"] == 7
    assert summary["selection_preview_count"] == 7
    assert summary["no_execution_confirmation_count"] == 7
    assert summary["next_review_count"] == 9
    assert summary["metadata_only"] is True

    assert home["gp035_connection"]["gp035_ready"] is True
    assert home["gp035_connection"]["gp035_safe_to_continue"] is True
    assert home["gp035_connection"]["gp035_vault_done"] is False
    assert home["gp035_connection"]["gp035_decision_record_count"] == 7
    assert home["gp035_connection"]["gp035_safe_option_count"] == 28
    assert home["gp035_connection"]["gp035_unsafe_option_count"] == 112
    assert home["gp035_connection"]["gp035_next_decision_count"] == 9


def test_gp036_html_is_dark_and_has_no_white_background_tokens():
    html = render_owner_decision_review_page()
    lowered = html.lower()

    assert "Vault Owner Decision Review" in html
    assert "Archive Vault" in html
    assert "/vault/owner-decision-review.json" in html
    assert "/vault/gp036-status.json" in html
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


def test_gp036_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-decision-review",
        "/vault/owner-decision-review.json",
        "/vault/owner-decision-review-cards.json",
        "/vault/owner-decision-review-status.json",
        "/vault/owner-decision-review-selection-preview.json",
        "/vault/owner-decision-review-tower-ack.json",
        "/vault/owner-decision-review-blocker-ack.json",
        "/vault/owner-decision-review-no-execution.json",
        "/vault/owner-decision-review-next-reviews.json",
        "/vault/owner-decision-review-carry-forward.json",
        "/vault/gp036-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp036_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/owner-decision-review",
        "/vault/owner-decision-review.json",
        "/vault/owner-decision-review-cards.json",
        "/vault/owner-decision-review-status.json",
        "/vault/owner-decision-review-selection-preview.json",
        "/vault/owner-decision-review-tower-ack.json",
        "/vault/owner-decision-review-blocker-ack.json",
        "/vault/owner-decision-review-no-execution.json",
        "/vault/owner-decision-review-next-reviews.json",
        "/vault/owner-decision-review-carry-forward.json",
        "/vault/gp036-status.json",
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
                assert b"Vault Owner Decision Review" in response.data
