"""
Tests for VAULT GIANT PACK 038 — Receipt Review Close Staging
"""

from pathlib import Path

import pytest

from vault.receipt_review_close_staging_service import (
    get_gp038_status,
    get_receipt_review_blocker_close_gates,
    get_receipt_review_close_cards,
    get_receipt_review_close_carry_forward,
    get_receipt_review_close_readiness,
    get_receipt_review_close_staging_home,
    get_receipt_review_draft_final_warnings,
    get_receipt_review_missing_ack_checks,
    get_receipt_review_next_close_staging,
    get_receipt_review_no_execution_close_proof,
    get_receipt_review_tower_close_gates,
    render_receipt_review_close_staging_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp038_status_ready_and_safe_to_continue():
    status = get_gp038_status()

    assert status["pack"]["id"] == "VAULT_GP038"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["pack"]["section_range"] == "GP031-GP040"
    assert status["gp038_status"]["ready"] is True
    assert status["gp038_status"]["section_id"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["gp038_status"]["gp037_receipt_staging_connected"] is True
    assert status["gp038_status"]["receipt_review_close_staging_ready"] is True
    assert status["gp038_status"]["safe_to_continue_to_gp039"] is True
    assert status["gp038_status"]["vault_done"] is False
    assert status["gp038_status"]["metadata_only_close_staging"] is True
    assert status["gp038_status"]["private_close_staging_only"] is True
    assert status["gp038_status"]["close_cards_only"] is True
    assert status["gp038_status"]["receipt_close_disabled"] is True
    assert status["gp038_status"]["receipt_finalization_disabled"] is True
    assert status["gp038_status"]["official_receipt_claim_disabled"] is True
    assert status["gp038_status"]["owner_review_claim_disabled"] is True
    assert status["gp038_status"]["tower_ack_claim_disabled"] is True
    assert status["gp038_status"]["blocker_ack_claim_disabled"] is True
    assert status["gp038_status"]["no_execution_confirmation_claim_disabled"] is True
    assert status["gp038_status"]["owner_review_required"] is True
    assert status["gp038_status"]["owner_confirmation_required"] is True
    assert status["gp038_status"]["owner_reviewed_count"] == 0
    assert status["gp038_status"]["owner_confirmed_count"] == 0
    assert status["gp038_status"]["decision_selected_count"] == 0
    assert status["gp038_status"]["closed_receipt_count"] == 0
    assert status["gp038_status"]["finalized_receipt_count"] == 0
    assert status["gp038_status"]["completed_count"] == 0
    assert status["gp038_status"]["auto_completion_disabled"] is True
    assert status["gp038_status"]["auto_confirmation_disabled"] is True
    assert status["gp038_status"]["approval_disabled"] is True
    assert status["gp038_status"]["execution_engine_disabled"] is True
    assert status["gp038_status"]["auto_action_execution_disabled"] is True
    assert status["gp038_status"]["direct_upload_still_locked"] is True
    assert status["gp038_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp038_status"]["external_delivery_still_locked"] is True
    assert status["gp038_status"]["external_access_still_locked"] is True
    assert status["gp038_status"]["packet_export_still_locked"] is True
    assert status["gp038_status"]["unredacted_export_still_locked"] is True
    assert status["gp038_status"]["raw_export_still_locked"] is True
    assert status["gp038_status"]["public_proof_still_locked"] is True
    assert status["gp038_status"]["public_packet_proof_disabled"] is True
    assert status["gp038_status"]["portal_access_still_locked"] is True
    assert status["gp038_status"]["financing_decision_not_claimed"] is True
    assert status["gp038_status"]["legal_advice_not_claimed"] is True
    assert status["gp038_status"]["raw_verification_not_claimed"] is True
    assert status["gp038_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp038"


def test_gp038_truth_keeps_close_and_finalization_disabled():
    status = get_gp038_status()
    truth = status["close_truth"]

    assert truth["receipt_review_close_staging_enabled"] is True
    assert truth["close_cards_enabled"] is True
    assert truth["close_readiness_labels_enabled"] is True
    assert truth["missing_ack_checks_enabled"] is True
    assert truth["draft_vs_final_warnings_enabled"] is True
    assert truth["tower_close_gates_enabled"] is True
    assert truth["blocker_close_gates_enabled"] is True
    assert truth["no_execution_close_proof_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["private_close_staging_only"] is True
    assert truth["close_staging_means_not_closed"] is True
    assert truth["receipt_close_enabled"] is False
    assert truth["receipt_finalization_enabled"] is False
    assert truth["finalized_receipt_count"] == 0
    assert truth["closed_receipt_count"] == 0
    assert truth["official_receipt_claimed_count"] == 0
    assert truth["owner_review_claimed_count"] == 0
    assert truth["tower_ack_claimed_count"] == 0
    assert truth["blocker_ack_claimed_count"] == 0
    assert truth["no_execution_confirmation_claimed_count"] == 0
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


def test_gp038_tower_authority_and_vault_boundaries():
    status = get_gp038_status()
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


def test_gp038_close_cards_cover_receipt_drafts():
    cards = get_receipt_review_close_cards()

    assert cards["close_card_count"] == 7

    ordered_packet_ids = [card["packet_id"] for card in cards["close_cards"]]
    assert ordered_packet_ids == [
        "ATM_ROUTE_ACQUISITION_PACKET",
        "APARTMENT_LENDER_DUE_DILIGENCE_PACKET",
        "TRUST_ENTITY_AUTHORITY_PACKET",
        "OB_MANUAL_LIVE_PROOF_PACKET",
        "SOULAANA_ARTIST_IP_PACKET",
        "PRIVATE_BETA_ONBOARDING_PACKET",
        "OWNER_ACTION_RECEIPT_PACKET",
    ]

    for card in cards["close_cards"]:
        assert card["close_card_id"].startswith("VRCC-")
        assert card["close_stage_id"].startswith("VRCS-")
        assert card["receipt_draft_id"].startswith("VRDR-")
        assert card["receipt_stage_id"].startswith("VRST-")
        assert card["review_card_id"].startswith("VODR-")
        assert card["decision_prep_id"].startswith("VDR-")
        assert card["priority_id"].startswith("VPR-")
        assert card["review_group_id"].startswith("VPG-")
        assert card["assembly_id"].startswith("VPA-")
        assert card["close_readiness_label"] == "NOT_READY_TO_CLOSE_MISSING_ACKS_DRAFT_ONLY"
        assert card["close_stage_status"] == "CLOSE_STAGING_READY_DRAFT_NOT_FINAL"
        assert card["metadata_only"] is True
        assert card["private_close_staging_only"] is True
        assert card["receipt_type"] == "reviewed_decision_receipt_close_staging"
        assert card["receipt_finalized"] is False
        assert card["receipt_closed"] is False
        assert card["official_receipt_claimed"] is False
        assert card["owner_review_claimed"] is False
        assert card["tower_ack_claimed"] is False
        assert card["blocker_ack_claimed"] is False
        assert card["no_execution_confirmation_claimed"] is False
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
        assert card["missing_ack_count"] == 4
        assert set(card["missing_ack_types"]) == {
            "owner_review",
            "tower_gate_ack",
            "blocker_ack",
            "no_execution_confirmation",
        }
        assert card["draft_final_warning_count"] == 4
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
        assert card["safe_to_review_close_privately"] is True
        assert card["safe_to_close_receipt"] is False
        assert card["safe_to_finalize_receipt"] is False
        assert card["safe_to_deliver_externally"] is False
        assert card["safe_to_export"] is False
        assert card["safe_to_carry_to_gp039"] is True
        assert "RECEIPT_REVIEW_CLOSE_STAGING_PRIVATE_ONLY" in card["blocked_codes"]
        assert "RECEIPT_CLOSE_NOT_ALLOWED" in card["blocked_codes"]
        assert "NO_EXTERNAL_PACKET_DELIVERY" in card["blocked_codes"]
        assert "NO_PACKET_EXPORT" in card["blocked_codes"]
        assert "CLOUDS_PARKED" in card["blocked_codes"]


def test_gp038_close_readiness_not_ready_to_close():
    readiness = get_receipt_review_close_readiness()["close_readiness"]

    assert readiness["close_readiness_count"] == 7
    assert readiness["not_ready_to_close_count"] == 7
    assert readiness["ready_to_close_count"] == 0
    assert readiness["safe_to_close_receipt_count"] == 0
    assert readiness["safe_to_finalize_receipt_count"] == 0
    assert readiness["receipt_closed_count"] == 0
    assert readiness["receipt_finalized_count"] == 0
    assert readiness["official_receipt_claimed_count"] == 0
    assert readiness["owner_confirmed_count"] == 0
    assert readiness["completed_count"] == 0
    assert readiness["external_delivery_allowed_count"] == 0
    assert readiness["packet_export_allowed_count"] == 0
    assert readiness["safe_to_continue_close_readiness"] is True

    for item in readiness["close_readiness_items"]:
        assert item["close_readiness_id"].startswith("VRCR-")
        assert item["close_card_id"].startswith("VRCC-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["close_readiness_label"] == "NOT_READY_TO_CLOSE_MISSING_ACKS_DRAFT_ONLY"
        assert item["missing_ack_count"] == 4
        assert item["draft_final_warning_count"] == 4
        assert item["metadata_only"] is True
        assert item["safe_to_close_receipt"] is False
        assert item["safe_to_finalize_receipt"] is False
        assert item["receipt_closed"] is False
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["owner_review_required"] is True
        assert item["owner_confirmed"] is False
        assert item["completed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["safe_to_carry_to_gp039"] is True


def test_gp038_missing_ack_checks_require_four_acks_per_packet():
    checks = get_receipt_review_missing_ack_checks()["missing_ack_checks"]

    assert checks["missing_ack_check_count"] == 28
    assert checks["missing_ack_type_count"] == 4
    assert checks["close_card_count"] == 7
    assert checks["ack_present_count"] == 0
    assert checks["ack_claimed_count"] == 0
    assert checks["acknowledged_count"] == 0
    assert checks["receipt_closed_count"] == 0
    assert checks["receipt_finalized_count"] == 0
    assert checks["official_receipt_claimed_count"] == 0
    assert checks["external_delivery_allowed_count"] == 0
    assert checks["packet_export_allowed_count"] == 0
    assert checks["executes_action_count"] == 0
    assert checks["safe_to_continue_missing_ack_checks"] is True

    ack_types = {item["ack_type"] for item in checks["missing_ack_check_items"]}
    assert ack_types == {
        "owner_review",
        "tower_gate_ack",
        "blocker_ack",
        "no_execution_confirmation",
    }

    for item in checks["missing_ack_check_items"]:
        assert item["missing_ack_check_id"].startswith("VRMA-")
        assert item["close_card_id"].startswith("VRCC-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["ack_required"] is True
        assert item["ack_present"] is False
        assert item["ack_claimed"] is False
        assert item["acknowledged"] is False
        assert item["check_status"] == "MISSING_ACK_REQUIRED_FOR_FUTURE_CLOSE"
        assert item["metadata_only"] is True
        assert item["receipt_closed"] is False
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["owner_review_required"] is True
        assert item["owner_confirmed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["executes_action"] is False
        assert item["safe_to_carry_to_gp039"] is True


def test_gp038_draft_final_warnings_are_active():
    warnings = get_receipt_review_draft_final_warnings()["draft_final_warnings"]

    assert warnings["draft_final_warning_count"] == 28
    assert warnings["warning_type_count"] == 4
    assert warnings["close_card_count"] == 7
    assert warnings["receipt_draft_only_count"] == 28
    assert warnings["receipt_closed_count"] == 0
    assert warnings["receipt_finalized_count"] == 0
    assert warnings["official_receipt_claimed_count"] == 0
    assert warnings["owner_review_claimed_count"] == 0
    assert warnings["no_execution_confirmation_claimed_count"] == 0
    assert warnings["external_delivery_allowed_count"] == 0
    assert warnings["packet_export_allowed_count"] == 0
    assert warnings["executes_action_count"] == 0
    assert warnings["safe_to_continue_draft_final_warnings"] is True

    warning_types = {item["warning_type"] for item in warnings["draft_final_warning_items"]}
    assert warning_types == {
        "receipt_draft_not_finalized",
        "official_receipt_not_claimed",
        "owner_review_not_claimed",
        "no_execution_not_confirmed",
    }

    for item in warnings["draft_final_warning_items"]:
        assert item["draft_final_warning_id"].startswith("VRDFW-")
        assert item["close_card_id"].startswith("VRCC-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["warning_status"] == "DRAFT_NOT_FINAL_WARNING_ACTIVE"
        assert item["metadata_only"] is True
        assert item["receipt_draft_only"] is True
        assert item["receipt_closed"] is False
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["owner_review_claimed"] is False
        assert item["no_execution_confirmation_claimed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["executes_action"] is False
        assert item["safe_to_carry_to_gp039"] is True


def test_gp038_tower_close_gates_preserve_tower_control():
    gates = get_receipt_review_tower_close_gates()["tower_close_gates"]

    assert gates["tower_close_gate_count"] == 7
    assert gates["tower_ack_required_count"] == 7
    assert gates["tower_acknowledged_count"] == 0
    assert gates["tower_ack_claimed_count"] == 0
    assert gates["tower_clearance_required_count"] == 7
    assert gates["tower_step_up_required_count"] == 7
    assert gates["tower_export_lock_required_count"] == 7
    assert gates["vault_override_allowed_count"] == 0
    assert gates["receipt_closed_count"] == 0
    assert gates["receipt_finalized_count"] == 0
    assert gates["official_receipt_claimed_count"] == 0
    assert gates["external_delivery_allowed_count"] == 0
    assert gates["packet_export_allowed_count"] == 0
    assert gates["portal_access_allowed_count"] == 0
    assert gates["all_tower_close_gates_preserve_authority"] is True

    for item in gates["tower_close_gate_items"]:
        assert item["tower_close_gate_id"].startswith("VRTCG-")
        assert item["close_card_id"].startswith("VRCC-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["tower_close_gate_status"] == "TOWER_CLOSE_GATES_REQUIRED_NOT_ACKNOWLEDGED"
        assert item["tower_ack_required"] is True
        assert item["tower_acknowledged"] is False
        assert item["tower_ack_claimed"] is False
        assert item["tower_clearance_required"] is True
        assert item["tower_step_up_required"] is True
        assert item["tower_export_lock_required"] is True
        assert item["tower_external_access_required"] is True
        assert item["tower_portal_unlock_required"] is True
        assert item["tower_sensitive_visibility_required"] is True
        assert item["vault_can_override_tower"] is False
        assert item["metadata_only"] is True
        assert item["receipt_closed"] is False
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["safe_to_carry_to_gp039"] is True


def test_gp038_blocker_close_gates_keep_restricted_paths_locked():
    gates = get_receipt_review_blocker_close_gates()["blocker_close_gates"]

    assert gates["blocker_close_gate_count"] == 7
    assert gates["active_block_code_count"] >= 20
    assert gates["blocker_ack_required_count"] == 7
    assert gates["blocker_acknowledged_count"] == 0
    assert gates["blocker_ack_claimed_count"] == 0
    assert gates["all_restricted_paths_locked"] is True
    assert gates["safe_to_override_inside_vault_count"] == 0
    assert gates["receipt_closed_count"] == 0
    assert gates["receipt_finalized_count"] == 0
    assert gates["official_receipt_claimed_count"] == 0
    assert gates["external_delivery_allowed_count"] == 0
    assert gates["packet_export_allowed_count"] == 0
    assert gates["public_packet_proof_allowed_count"] == 0
    assert gates["execution_allowed_count"] == 0
    assert gates["safe_to_continue_blocker_close_gates"] is True

    codes = set(gates["active_block_codes"])
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "NO_EXTERNAL_PACKET_DELIVERY" in codes
    assert "NO_PACKET_EXPORT" in codes
    assert "RECEIPT_REVIEW_CLOSE_STAGING_PRIVATE_ONLY" in codes
    assert "RECEIPT_CLOSE_NOT_ALLOWED" in codes
    assert "CLOUDS_PARKED" in codes

    for item in gates["blocker_close_gate_items"]:
        assert item["blocker_close_gate_id"].startswith("VRBCG-")
        assert item["close_card_id"].startswith("VRCC-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["blocker_close_gate_status"] == "BLOCKER_CLOSE_GATES_ACTIVE_NOT_ACKNOWLEDGED"
        assert item["blocker_ack_required"] is True
        assert item["blocker_acknowledged"] is False
        assert item["blocker_ack_claimed"] is False
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
        assert item["receipt_closed"] is False
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["safe_to_carry_to_gp039"] is True


def test_gp038_no_execution_close_proof_is_not_confirmed_or_executed():
    proof = get_receipt_review_no_execution_close_proof()["no_execution_close_proof"]

    assert proof["no_execution_close_proof_count"] == 7
    assert proof["no_execution_confirmation_required_count"] == 7
    assert proof["no_execution_confirmed_count"] == 0
    assert proof["no_execution_confirmation_claimed_count"] == 0
    assert proof["receipt_closed_count"] == 0
    assert proof["receipt_finalized_count"] == 0
    assert proof["official_receipt_claimed_count"] == 0
    assert proof["auto_action_execution_enabled_count"] == 0
    assert proof["execution_engine_enabled_count"] == 0
    assert proof["approval_allowed_count"] == 0
    assert proof["financing_decision_enabled_count"] == 0
    assert proof["legal_advice_enabled_count"] == 0
    assert proof["raw_document_verification_claimed_count"] == 0
    assert proof["auto_packet_approval_enabled_count"] == 0
    assert proof["external_delivery_allowed_count"] == 0
    assert proof["packet_export_allowed_count"] == 0
    assert proof["safe_to_continue_no_execution_close_proof"] is True

    for item in proof["no_execution_close_proof_items"]:
        assert item["no_execution_close_proof_id"].startswith("VRNEC-")
        assert item["close_card_id"].startswith("VRCC-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["no_execution_close_status"] == "NO_EXECUTION_CLOSE_PROOF_STAGED_NOT_CONFIRMED"
        assert item["no_execution_confirmation_required"] is True
        assert item["no_execution_confirmed"] is False
        assert item["no_execution_confirmation_claimed"] is False
        assert item["receipt_closed"] is False
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["auto_action_execution_enabled"] is False
        assert item["execution_engine_enabled"] is False
        assert item["approval_allowed"] is False
        assert item["financing_decision_enabled"] is False
        assert item["legal_advice_enabled"] is False
        assert item["raw_document_verification_claimed"] is False
        assert item["auto_packet_approval_enabled"] is False
        assert item["metadata_only"] is True
        assert item["private_close_staging_only"] is True
        assert item["owner_confirmed"] is False
        assert item["completed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["safe_to_carry_to_gp039"] is True


def test_gp038_next_close_staging_sorted_and_continue_vault_not_clouds():
    next_close = get_receipt_review_next_close_staging()["next_close_staging"]

    assert next_close["next_close_staging_count"] == 9
    assert next_close["packet_close_count"] == 7
    assert next_close["boundary_close_count"] == 1
    assert next_close["next_build_close_count"] == 1
    assert next_close["missing_ack_check_count"] == 28
    assert next_close["draft_final_warning_count"] == 28
    assert next_close["no_execution_close_proof_count"] == 7
    assert next_close["receipt_closed_count"] == 0
    assert next_close["receipt_finalized_count"] == 0
    assert next_close["official_receipt_claimed_count"] == 0
    assert next_close["owner_review_claimed_count"] == 0
    assert next_close["tower_ack_claimed_count"] == 0
    assert next_close["blocker_ack_claimed_count"] == 0
    assert next_close["no_execution_confirmation_claimed_count"] == 0
    assert next_close["owner_review_required_count"] == 9
    assert next_close["decision_selected_count"] == 0
    assert next_close["owner_confirmed_count"] == 0
    assert next_close["completed_count"] == 0
    assert next_close["external_delivery_allowed_count"] == 0
    assert next_close["packet_export_allowed_count"] == 0
    assert next_close["public_packet_proof_allowed_count"] == 0
    assert next_close["safe_to_continue_next_close_staging"] is True

    ranks = [item["priority_rank"] for item in next_close["next_close_staging_items"]]
    assert ranks == sorted(ranks)

    assert next_close["next_close_staging_items"][0]["packet_id"] == "ATM_ROUTE_ACQUISITION_PACKET"
    assert next_close["next_close_staging_items"][1]["packet_id"] == "APARTMENT_LENDER_DUE_DILIGENCE_PACKET"
    assert next_close["next_close_staging_items"][-1]["packet_id"] == "NEXT_VAULT_PACK"

    joined = " ".join(next_close["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp039" in joined

    for item in next_close["next_close_staging_items"]:
        assert item["next_close_staging_id"].startswith("VRCNX-")
        assert item["metadata_only"] is True
        assert item["private_close_staging_only"] is True
        assert item["receipt_closed"] is False
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["owner_review_claimed"] is False
        assert item["tower_ack_claimed"] is False
        assert item["blocker_ack_claimed"] is False
        assert item["no_execution_confirmation_claimed"] is False
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
        assert item["safe_to_carry_to_gp039"] is True


def test_gp038_carry_forward_prepares_gp039():
    carry = get_receipt_review_close_carry_forward()["carry_forward"]

    assert carry["carry_forward_count"] == 7
    assert carry["ready_for_gp039_count"] == 7
    assert carry["receipt_closed_count"] == 0
    assert carry["receipt_finalized_count"] == 0
    assert carry["official_receipt_claimed_count"] == 0
    assert carry["owner_review_claimed_count"] == 0
    assert carry["tower_ack_claimed_count"] == 0
    assert carry["blocker_ack_claimed_count"] == 0
    assert carry["no_execution_confirmation_claimed_count"] == 0
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
    assert carry["safe_to_carry_to_gp039"] is True
    assert carry["next_close_staging_count"] == 9

    for item in carry["carry_forward_items"]:
        assert item["carry_forward_id"].startswith("VRCC-CF-")
        assert item["close_card_id"].startswith("VRCC-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["priority_id"].startswith("VPR-")
        assert item["review_group_id"].startswith("VPG-")
        assert item["carry_forward_status"] == "READY_FOR_GP039_RECEIPT_CLOSE_SUMMARY"
        assert item["receipt_closed"] is False
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["owner_review_claimed"] is False
        assert item["tower_ack_claimed"] is False
        assert item["blocker_ack_claimed"] is False
        assert item["no_execution_confirmation_claimed"] is False
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
        assert item["safe_to_carry_to_gp039"] is True


def test_gp038_home_routes_declared():
    home = get_receipt_review_close_staging_home()
    summary = home["close_summary"]

    assert summary["section_header"] == "Archive Vault — Controlled Packet Assembly Layer"
    assert summary["section_range"] == "GP031-GP040"
    assert summary["route"] == "/vault/receipt-review-close-staging"
    assert summary["json_route"] == "/vault/receipt-review-close-staging.json"
    assert summary["cards_route"] == "/vault/receipt-review-close-cards.json"
    assert summary["readiness_route"] == "/vault/receipt-review-close-readiness.json"
    assert summary["missing_ack_checks_route"] == "/vault/receipt-review-missing-ack-checks.json"
    assert summary["draft_final_warnings_route"] == "/vault/receipt-review-draft-final-warnings.json"
    assert summary["tower_close_gates_route"] == "/vault/receipt-review-tower-close-gates.json"
    assert summary["blocker_close_gates_route"] == "/vault/receipt-review-blocker-close-gates.json"
    assert summary["no_execution_close_proof_route"] == "/vault/receipt-review-no-execution-close-proof.json"
    assert summary["next_close_staging_route"] == "/vault/receipt-review-next-close-staging.json"
    assert summary["carry_forward_route"] == "/vault/receipt-review-close-carry-forward.json"
    assert summary["gp038_status_route"] == "/vault/gp038-status.json"
    assert summary["close_card_count"] == 7
    assert summary["missing_ack_check_count"] == 28
    assert summary["draft_final_warning_count"] == 28
    assert summary["next_close_staging_count"] == 9
    assert summary["closed_receipt_count"] == 0
    assert summary["finalized_receipt_count"] == 0
    assert summary["official_receipt_claimed_count"] == 0
    assert summary["metadata_only"] is True

    assert home["gp037_connection"]["gp037_ready"] is True
    assert home["gp037_connection"]["gp037_safe_to_continue"] is True
    assert home["gp037_connection"]["gp037_vault_done"] is False
    assert home["gp037_connection"]["gp037_receipt_draft_count"] == 7
    assert home["gp037_connection"]["gp037_ack_receipt_preview_count"] == 21
    assert home["gp037_connection"]["gp037_no_execution_receipt_count"] == 7
    assert home["gp037_connection"]["gp037_next_receipt_count"] == 9


def test_gp038_html_is_dark_and_has_no_white_background_tokens():
    html = render_receipt_review_close_staging_page()
    lowered = html.lower()

    assert "Vault Receipt Review Close Staging" in html
    assert "Archive Vault" in html
    assert "/vault/receipt-review-close-staging.json" in html
    assert "/vault/gp038-status.json" in html
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


def test_gp038_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/receipt-review-close-staging",
        "/vault/receipt-review-close-staging.json",
        "/vault/receipt-review-close-cards.json",
        "/vault/receipt-review-close-readiness.json",
        "/vault/receipt-review-missing-ack-checks.json",
        "/vault/receipt-review-draft-final-warnings.json",
        "/vault/receipt-review-tower-close-gates.json",
        "/vault/receipt-review-blocker-close-gates.json",
        "/vault/receipt-review-no-execution-close-proof.json",
        "/vault/receipt-review-next-close-staging.json",
        "/vault/receipt-review-close-carry-forward.json",
        "/vault/gp038-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp038_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/receipt-review-close-staging",
        "/vault/receipt-review-close-staging.json",
        "/vault/receipt-review-close-cards.json",
        "/vault/receipt-review-close-readiness.json",
        "/vault/receipt-review-missing-ack-checks.json",
        "/vault/receipt-review-draft-final-warnings.json",
        "/vault/receipt-review-tower-close-gates.json",
        "/vault/receipt-review-blocker-close-gates.json",
        "/vault/receipt-review-no-execution-close-proof.json",
        "/vault/receipt-review-next-close-staging.json",
        "/vault/receipt-review-close-carry-forward.json",
        "/vault/gp038-status.json",
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
                assert b"Vault Receipt Review Close Staging" in response.data
