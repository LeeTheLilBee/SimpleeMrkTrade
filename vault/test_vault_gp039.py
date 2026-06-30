"""
Tests for VAULT GIANT PACK 039 — Receipt Close Summary
"""

from pathlib import Path

import pytest

from vault.receipt_close_summary_service import (
    get_controlled_packet_assembly_rollup,
    get_gp039_status,
    get_receipt_close_carry_forward,
    get_receipt_close_next_summary,
    get_receipt_close_no_execution_summary_proof,
    get_receipt_close_not_final_warnings,
    get_receipt_close_summary_board,
    get_receipt_close_summary_home,
    get_receipt_close_tower_owner_readiness,
    get_receipt_close_unresolved_blockers,
    render_receipt_close_summary_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp039_status_ready_and_safe_to_continue():
    status = get_gp039_status()

    assert status["pack"]["id"] == "VAULT_GP039"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["pack"]["section_range"] == "GP031-GP040"
    assert status["gp039_status"]["ready"] is True
    assert status["gp039_status"]["section_id"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["gp039_status"]["gp038_close_staging_connected"] is True
    assert status["gp039_status"]["receipt_close_summary_ready"] is True
    assert status["gp039_status"]["safe_to_continue_to_gp040"] is True
    assert status["gp039_status"]["vault_done"] is False
    assert status["gp039_status"]["metadata_only_summary"] is True
    assert status["gp039_status"]["private_summary_only"] is True
    assert status["gp039_status"]["summary_board_only"] is True
    assert status["gp039_status"]["receipt_close_disabled"] is True
    assert status["gp039_status"]["receipt_finalization_disabled"] is True
    assert status["gp039_status"]["official_receipt_claim_disabled"] is True
    assert status["gp039_status"]["owner_review_claim_disabled"] is True
    assert status["gp039_status"]["tower_ack_claim_disabled"] is True
    assert status["gp039_status"]["blocker_ack_claim_disabled"] is True
    assert status["gp039_status"]["no_execution_confirmation_claim_disabled"] is True
    assert status["gp039_status"]["section_checkpoint_not_yet_built"] is True
    assert status["gp039_status"]["owner_review_required"] is True
    assert status["gp039_status"]["owner_confirmation_required"] is True
    assert status["gp039_status"]["owner_reviewed_count"] == 0
    assert status["gp039_status"]["owner_confirmed_count"] == 0
    assert status["gp039_status"]["decision_selected_count"] == 0
    assert status["gp039_status"]["closed_receipt_count"] == 0
    assert status["gp039_status"]["finalized_receipt_count"] == 0
    assert status["gp039_status"]["completed_count"] == 0
    assert status["gp039_status"]["auto_completion_disabled"] is True
    assert status["gp039_status"]["auto_confirmation_disabled"] is True
    assert status["gp039_status"]["approval_disabled"] is True
    assert status["gp039_status"]["execution_engine_disabled"] is True
    assert status["gp039_status"]["auto_action_execution_disabled"] is True
    assert status["gp039_status"]["direct_upload_still_locked"] is True
    assert status["gp039_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp039_status"]["external_delivery_still_locked"] is True
    assert status["gp039_status"]["external_access_still_locked"] is True
    assert status["gp039_status"]["packet_export_still_locked"] is True
    assert status["gp039_status"]["unredacted_export_still_locked"] is True
    assert status["gp039_status"]["raw_export_still_locked"] is True
    assert status["gp039_status"]["public_proof_still_locked"] is True
    assert status["gp039_status"]["public_packet_proof_disabled"] is True
    assert status["gp039_status"]["portal_access_still_locked"] is True
    assert status["gp039_status"]["financing_decision_not_claimed"] is True
    assert status["gp039_status"]["legal_advice_not_claimed"] is True
    assert status["gp039_status"]["raw_verification_not_claimed"] is True
    assert status["gp039_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp039"


def test_gp039_truth_keeps_summary_not_closed_not_checkpoint():
    status = get_gp039_status()
    truth = status["summary_truth"]

    assert truth["receipt_close_summary_enabled"] is True
    assert truth["summary_board_enabled"] is True
    assert truth["unresolved_close_blockers_enabled"] is True
    assert truth["receipt_not_final_warnings_enabled"] is True
    assert truth["tower_owner_close_readiness_enabled"] is True
    assert truth["no_execution_summary_proof_enabled"] is True
    assert truth["controlled_packet_assembly_rollup_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["private_summary_only"] is True
    assert truth["summary_means_not_checkpoint"] is True
    assert truth["summary_means_not_closed"] is True
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


def test_gp039_tower_authority_and_vault_boundaries():
    status = get_gp039_status()
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


def test_gp039_summary_board_covers_close_cards():
    board = get_receipt_close_summary_board()["summary_board"]

    assert board["summary_board_count"] == 7
    assert board["receipt_closed_count"] == 0
    assert board["receipt_finalized_count"] == 0
    assert board["official_receipt_claimed_count"] == 0
    assert board["owner_review_claimed_count"] == 0
    assert board["tower_ack_claimed_count"] == 0
    assert board["blocker_ack_claimed_count"] == 0
    assert board["no_execution_confirmation_claimed_count"] == 0
    assert board["owner_review_required_count"] == 7
    assert board["missing_ack_total"] == 28
    assert board["draft_final_warning_total"] == 28
    assert board["external_delivery_allowed_count"] == 0
    assert board["packet_export_allowed_count"] == 0
    assert board["safe_to_continue_summary_board"] is True

    ordered_packet_ids = [item["packet_id"] for item in board["summary_board_items"]]
    assert ordered_packet_ids == [
        "ATM_ROUTE_ACQUISITION_PACKET",
        "APARTMENT_LENDER_DUE_DILIGENCE_PACKET",
        "TRUST_ENTITY_AUTHORITY_PACKET",
        "OB_MANUAL_LIVE_PROOF_PACKET",
        "SOULAANA_ARTIST_IP_PACKET",
        "PRIVATE_BETA_ONBOARDING_PACKET",
        "OWNER_ACTION_RECEIPT_PACKET",
    ]

    for item in board["summary_board_items"]:
        assert item["summary_item_id"].startswith("VRCSB-")
        assert item["close_card_id"].startswith("VRCC-")
        assert item["close_stage_id"].startswith("VRCS-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["priority_id"].startswith("VPR-")
        assert item["review_group_id"].startswith("VPG-")
        assert item["assembly_id"].startswith("VPA-")
        assert item["summary_status"] == "SUMMARY_READY_NOT_CLOSED_NOT_FINAL"
        assert item["metadata_only"] is True
        assert item["private_summary_only"] is True
        assert item["receipt_closed"] is False
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["owner_review_claimed"] is False
        assert item["tower_ack_claimed"] is False
        assert item["blocker_ack_claimed"] is False
        assert item["no_execution_confirmation_claimed"] is False
        assert item["owner_review_required"] is True
        assert item["owner_reviewed"] is False
        assert item["owner_confirmation_required"] is True
        assert item["owner_confirmed"] is False
        assert item["decision_selected"] is False
        assert item["completed"] is False
        assert item["auto_complete_allowed"] is False
        assert item["auto_confirm_allowed"] is False
        assert item["approval_allowed"] is False
        assert item["can_execute_from_vault"] is False
        assert item["execution_engine_enabled"] is False
        assert item["missing_ack_count"] == 4
        assert item["draft_final_warning_count"] == 4
        assert item["raw_file_body_storage_enabled"] is False
        assert item["direct_upload_unlocked"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["tower_clearance_required"] is True
        assert item["tower_step_up_required"] is True
        assert item["vault_can_override_tower"] is False
        assert item["safe_to_close_receipt"] is False
        assert item["safe_to_finalize_receipt"] is False
        assert item["safe_to_export"] is False
        assert item["safe_to_carry_to_gp040"] is True
        assert "RECEIPT_CLOSE_SUMMARY_PRIVATE_ONLY" in item["blocked_codes"]
        assert "RECEIPT_CLOSE_SUMMARY_NOT_SECTION_CHECKPOINT" in item["blocked_codes"]
        assert "NO_EXTERNAL_PACKET_DELIVERY" in item["blocked_codes"]
        assert "NO_PACKET_EXPORT" in item["blocked_codes"]
        assert "CLOUDS_PARKED" in item["blocked_codes"]


def test_gp039_unresolved_blockers_remain_locked():
    blockers = get_receipt_close_unresolved_blockers()["unresolved_blockers"]

    assert blockers["unresolved_blocker_count"] == 7
    assert blockers["active_block_code_count"] >= 20
    assert blockers["all_restricted_paths_locked"] is True
    assert blockers["safe_to_override_inside_vault_count"] == 0
    assert blockers["receipt_closed_count"] == 0
    assert blockers["receipt_finalized_count"] == 0
    assert blockers["official_receipt_claimed_count"] == 0
    assert blockers["external_delivery_allowed_count"] == 0
    assert blockers["packet_export_allowed_count"] == 0
    assert blockers["public_packet_proof_allowed_count"] == 0
    assert blockers["execution_allowed_count"] == 0
    assert blockers["safe_to_continue_unresolved_blockers"] is True

    codes = set(blockers["active_block_codes"])
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "NO_EXTERNAL_PACKET_DELIVERY" in codes
    assert "NO_PACKET_EXPORT" in codes
    assert "RECEIPT_CLOSE_SUMMARY_PRIVATE_ONLY" in codes
    assert "RECEIPT_CLOSE_SUMMARY_NOT_SECTION_CHECKPOINT" in codes
    assert "CLOUDS_PARKED" in codes

    for item in blockers["unresolved_blocker_items"]:
        assert item["unresolved_blocker_id"].startswith("VRCUB-")
        assert item["close_card_id"].startswith("VRCC-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["blocker_status"] == "UNRESOLVED_CLOSE_BLOCKERS_ACTIVE"
        assert item["metadata_only"] is True
        assert item["all_restricted_paths_locked"] is True
        assert item["safe_to_override_inside_vault"] is False
        assert item["raw_storage_allowed"] is False
        assert item["direct_upload_allowed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["execution_allowed"] is False
        assert item["receipt_closed"] is False
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["safe_to_carry_to_gp040"] is True


def test_gp039_receipt_not_final_warnings_active():
    warnings = get_receipt_close_not_final_warnings()["not_final_warnings"]

    assert warnings["not_final_warning_count"] == 28
    assert warnings["warning_type_count"] == 4
    assert warnings["receipt_draft_only_count"] == 28
    assert warnings["receipt_closed_count"] == 0
    assert warnings["receipt_finalized_count"] == 0
    assert warnings["official_receipt_claimed_count"] == 0
    assert warnings["owner_review_claimed_count"] == 0
    assert warnings["no_execution_confirmation_claimed_count"] == 0
    assert warnings["external_delivery_allowed_count"] == 0
    assert warnings["packet_export_allowed_count"] == 0
    assert warnings["executes_action_count"] == 0
    assert warnings["safe_to_continue_not_final_warnings"] is True

    warning_types = {item["warning_type"] for item in warnings["not_final_warning_items"]}
    assert warning_types == {
        "receipt_draft_not_finalized",
        "official_receipt_not_claimed",
        "owner_review_not_claimed",
        "no_execution_not_confirmed",
    }

    for item in warnings["not_final_warning_items"]:
        assert item["not_final_warning_id"].startswith("VRCNFW-")
        assert item["close_card_id"].startswith("VRCC-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["warning_status"] == "RECEIPT_NOT_FINAL_WARNING_ACTIVE"
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
        assert item["safe_to_carry_to_gp040"] is True


def test_gp039_tower_owner_readiness_not_ready_to_close():
    readiness = get_receipt_close_tower_owner_readiness()["tower_owner_readiness"]

    assert readiness["tower_owner_readiness_count"] == 7
    assert readiness["owner_review_required_count"] == 7
    assert readiness["owner_reviewed_count"] == 0
    assert readiness["owner_confirmed_count"] == 0
    assert readiness["tower_ack_required_count"] == 7
    assert readiness["tower_acknowledged_count"] == 0
    assert readiness["tower_ack_claimed_count"] == 0
    assert readiness["tower_clearance_required_count"] == 7
    assert readiness["tower_step_up_required_count"] == 7
    assert readiness["vault_override_allowed_count"] == 0
    assert readiness["receipt_closed_count"] == 0
    assert readiness["receipt_finalized_count"] == 0
    assert readiness["official_receipt_claimed_count"] == 0
    assert readiness["external_delivery_allowed_count"] == 0
    assert readiness["packet_export_allowed_count"] == 0
    assert readiness["portal_access_allowed_count"] == 0
    assert readiness["all_tower_owner_readiness_preserved"] is True

    for item in readiness["tower_owner_readiness_items"]:
        assert item["tower_owner_readiness_id"].startswith("VRCTOR-")
        assert item["close_card_id"].startswith("VRCC-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["readiness_status"] == "OWNER_AND_TOWER_NOT_READY_TO_CLOSE"
        assert item["owner_review_required"] is True
        assert item["owner_reviewed"] is False
        assert item["owner_confirmation_required"] is True
        assert item["owner_confirmed"] is False
        assert item["tower_ack_required"] is True
        assert item["tower_acknowledged"] is False
        assert item["tower_ack_claimed"] is False
        assert item["tower_clearance_required"] is True
        assert item["tower_step_up_required"] is True
        assert item["tower_export_lock_required"] is True
        assert item["vault_can_override_tower"] is False
        assert item["metadata_only"] is True
        assert item["receipt_closed"] is False
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["safe_to_carry_to_gp040"] is True


def test_gp039_no_execution_summary_proof_not_confirmed_or_executed():
    proof = get_receipt_close_no_execution_summary_proof()["no_execution_summary"]

    assert proof["no_execution_summary_count"] == 7
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
    assert proof["safe_to_continue_no_execution_summary"] is True

    for item in proof["no_execution_summary_items"]:
        assert item["no_execution_summary_id"].startswith("VRCNES-")
        assert item["close_card_id"].startswith("VRCC-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["no_execution_summary_status"] == "NO_EXECUTION_SUMMARY_PROOF_VISIBLE_NOT_CONFIRMED"
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
        assert item["private_summary_only"] is True
        assert item["owner_confirmed"] is False
        assert item["completed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["safe_to_carry_to_gp040"] is True


def test_gp039_controlled_packet_assembly_rollup_ready_for_gp040():
    rollup = get_controlled_packet_assembly_rollup()["controlled_rollup"]

    assert rollup["controlled_rollup_pack_count"] == 8
    assert rollup["expected_pack_count"] == 8
    assert rollup["present_pack_count"] == 8
    assert rollup["ready_pack_count"] == 8
    assert rollup["safe_to_continue_pack_count"] == 8
    assert rollup["all_expected_packs_present"] is True
    assert rollup["all_expected_packs_ready"] is True
    assert rollup["all_expected_packs_safe_to_continue"] is True
    assert rollup["vault_done"] is False
    assert rollup["gp038_connection_ready"] is True
    assert rollup["gp038_connection_safe_to_continue"] is True
    assert rollup["ready_for_gp040_section_checkpoint"] is True
    assert rollup["clouds_should_continue"] is False

    seen = {item["pack_id"] for item in rollup["controlled_rollup_items"]}
    assert seen == {
        "VAULT_GP031",
        "VAULT_GP032",
        "VAULT_GP033",
        "VAULT_GP034",
        "VAULT_GP035",
        "VAULT_GP036",
        "VAULT_GP037",
        "VAULT_GP038",
    }

    for item in rollup["controlled_rollup_items"]:
        assert item["rollup_id"].startswith("VCPR-")
        assert item["section"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
        assert item["section_range"] == "GP031-GP040"
        assert item["present"] is True
        assert item["ready"] is True
        assert item["safe_to_continue"] is True
        assert item["foundation_status"] == "safe_to_continue_not_done"
        assert item["vault_done"] is False
        assert item["metadata_only_private_layer"] is True
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["execution_allowed"] is False


def test_gp039_next_summary_sorted_and_continue_vault_not_clouds():
    next_summary = get_receipt_close_next_summary()["next_summary"]

    assert next_summary["next_summary_count"] == 9
    assert next_summary["packet_summary_count"] == 7
    assert next_summary["boundary_summary_count"] == 1
    assert next_summary["next_build_summary_count"] == 1
    assert next_summary["unresolved_blocker_count"] == 7
    assert next_summary["not_final_warning_count"] == 28
    assert next_summary["tower_owner_readiness_count"] == 7
    assert next_summary["no_execution_summary_count"] == 7
    assert next_summary["controlled_rollup_pack_count"] == 8
    assert next_summary["receipt_closed_count"] == 0
    assert next_summary["receipt_finalized_count"] == 0
    assert next_summary["official_receipt_claimed_count"] == 0
    assert next_summary["owner_review_claimed_count"] == 0
    assert next_summary["tower_ack_claimed_count"] == 0
    assert next_summary["blocker_ack_claimed_count"] == 0
    assert next_summary["no_execution_confirmation_claimed_count"] == 0
    assert next_summary["owner_review_required_count"] == 9
    assert next_summary["decision_selected_count"] == 0
    assert next_summary["owner_confirmed_count"] == 0
    assert next_summary["completed_count"] == 0
    assert next_summary["external_delivery_allowed_count"] == 0
    assert next_summary["packet_export_allowed_count"] == 0
    assert next_summary["public_packet_proof_allowed_count"] == 0
    assert next_summary["safe_to_continue_next_summary"] is True

    ranks = [item["priority_rank"] for item in next_summary["next_summary_items"]]
    assert ranks == sorted(ranks)

    assert next_summary["next_summary_items"][0]["packet_id"] == "ATM_ROUTE_ACQUISITION_PACKET"
    assert next_summary["next_summary_items"][1]["packet_id"] == "APARTMENT_LENDER_DUE_DILIGENCE_PACKET"
    assert next_summary["next_summary_items"][-1]["packet_id"] == "NEXT_VAULT_PACK"

    joined = " ".join(next_summary["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp040" in joined

    for item in next_summary["next_summary_items"]:
        assert item["next_summary_id"].startswith("VRCSNX-")
        assert item["metadata_only"] is True
        assert item["private_summary_only"] is True
        assert item["receipt_closed"] is False
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["owner_review_claimed"] is False
        assert item["tower_ack_claimed"] is False
        assert item["blocker_ack_claimed"] is False
        assert item["no_execution_confirmation_claimed"] is False
        assert item["owner_review_required"] is True
        assert item["owner_reviewed"] is False
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
        assert item["safe_to_carry_to_gp040"] is True


def test_gp039_carry_forward_prepares_gp040():
    carry = get_receipt_close_carry_forward()["carry_forward"]

    assert carry["carry_forward_count"] == 7
    assert carry["ready_for_gp040_count"] == 7
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
    assert carry["safe_to_carry_to_gp040"] is True
    assert carry["next_summary_count"] == 9

    for item in carry["carry_forward_items"]:
        assert item["carry_forward_id"].startswith("VRCS-CF-")
        assert item["summary_item_id"].startswith("VRCSB-")
        assert item["close_card_id"].startswith("VRCC-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["priority_id"].startswith("VPR-")
        assert item["review_group_id"].startswith("VPG-")
        assert item["carry_forward_status"] == "READY_FOR_GP040_CONTROLLED_PACKET_ASSEMBLY_READINESS_CHECKPOINT"
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
        assert item["safe_to_carry_to_gp040"] is True


def test_gp039_home_routes_declared():
    home = get_receipt_close_summary_home()
    routes = home["summary_routes"]
    counts = home["summary_counts"]

    assert routes["section_header"] == "Archive Vault — Controlled Packet Assembly Layer"
    assert routes["section_range"] == "GP031-GP040"
    assert routes["route"] == "/vault/receipt-close-summary"
    assert routes["json_route"] == "/vault/receipt-close-summary.json"
    assert routes["board_route"] == "/vault/receipt-close-summary-board.json"
    assert routes["unresolved_blockers_route"] == "/vault/receipt-close-unresolved-blockers.json"
    assert routes["not_final_warnings_route"] == "/vault/receipt-close-not-final-warnings.json"
    assert routes["tower_owner_readiness_route"] == "/vault/receipt-close-tower-owner-readiness.json"
    assert routes["no_execution_summary_proof_route"] == "/vault/receipt-close-no-execution-summary-proof.json"
    assert routes["controlled_rollup_route"] == "/vault/controlled-packet-assembly-rollup.json"
    assert routes["next_summary_route"] == "/vault/receipt-close-next-summary.json"
    assert routes["carry_forward_route"] == "/vault/receipt-close-carry-forward.json"
    assert routes["gp039_status_route"] == "/vault/gp039-status.json"

    assert counts["summary_board_count"] == 7
    assert counts["unresolved_blocker_count"] == 7
    assert counts["not_final_warning_count"] == 28
    assert counts["controlled_rollup_pack_count"] == 8
    assert counts["next_summary_count"] == 9
    assert counts["closed_receipt_count"] == 0
    assert counts["finalized_receipt_count"] == 0
    assert counts["official_receipt_claimed_count"] == 0
    assert counts["metadata_only"] is True

    assert home["gp038_connection"]["gp038_ready"] is True
    assert home["gp038_connection"]["gp038_safe_to_continue"] is True
    assert home["gp038_connection"]["gp038_vault_done"] is False
    assert home["gp038_connection"]["gp038_close_card_count"] == 7
    assert home["gp038_connection"]["gp038_missing_ack_check_count"] == 28
    assert home["gp038_connection"]["gp038_draft_final_warning_count"] == 28
    assert home["gp038_connection"]["gp038_next_close_staging_count"] == 9


def test_gp039_html_is_dark_and_has_no_white_background_tokens():
    html = render_receipt_close_summary_page()
    lowered = html.lower()

    assert "Vault Receipt Close Summary" in html
    assert "Archive Vault" in html
    assert "/vault/receipt-close-summary.json" in html
    assert "/vault/gp039-status.json" in html
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


def test_gp039_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/receipt-close-summary",
        "/vault/receipt-close-summary.json",
        "/vault/receipt-close-summary-board.json",
        "/vault/receipt-close-unresolved-blockers.json",
        "/vault/receipt-close-not-final-warnings.json",
        "/vault/receipt-close-tower-owner-readiness.json",
        "/vault/receipt-close-no-execution-summary-proof.json",
        "/vault/controlled-packet-assembly-rollup.json",
        "/vault/receipt-close-next-summary.json",
        "/vault/receipt-close-carry-forward.json",
        "/vault/gp039-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp039_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/receipt-close-summary",
        "/vault/receipt-close-summary.json",
        "/vault/receipt-close-summary-board.json",
        "/vault/receipt-close-unresolved-blockers.json",
        "/vault/receipt-close-not-final-warnings.json",
        "/vault/receipt-close-tower-owner-readiness.json",
        "/vault/receipt-close-no-execution-summary-proof.json",
        "/vault/controlled-packet-assembly-rollup.json",
        "/vault/receipt-close-next-summary.json",
        "/vault/receipt-close-carry-forward.json",
        "/vault/gp039-status.json",
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
                assert b"Vault Receipt Close Summary" in response.data
