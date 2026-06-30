"""
Tests for VAULT GIANT PACK 037 — Reviewed Decision Receipt Staging
"""

from pathlib import Path

import pytest

from vault.reviewed_decision_receipt_staging_service import (
    get_gp037_status,
    get_reviewed_decision_ack_receipt_previews,
    get_reviewed_decision_blocker_receipt_refs,
    get_reviewed_decision_next_receipts,
    get_reviewed_decision_no_execution_proof,
    get_reviewed_decision_receipt_carry_forward,
    get_reviewed_decision_receipt_drafts,
    get_reviewed_decision_receipt_staging_home,
    get_reviewed_decision_tower_receipt_refs,
    render_reviewed_decision_receipt_staging_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp037_status_ready_and_safe_to_continue():
    status = get_gp037_status()

    assert status["pack"]["id"] == "VAULT_GP037"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["pack"]["section_range"] == "GP031-GP040"
    assert status["gp037_status"]["ready"] is True
    assert status["gp037_status"]["section_id"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["gp037_status"]["gp036_owner_decision_review_connected"] is True
    assert status["gp037_status"]["reviewed_decision_receipt_staging_ready"] is True
    assert status["gp037_status"]["safe_to_continue_to_gp038"] is True
    assert status["gp037_status"]["vault_done"] is False
    assert status["gp037_status"]["metadata_only_receipt_staging"] is True
    assert status["gp037_status"]["private_receipt_staging_only"] is True
    assert status["gp037_status"]["receipt_drafts_only"] is True
    assert status["gp037_status"]["receipt_finalization_disabled"] is True
    assert status["gp037_status"]["official_receipt_claim_disabled"] is True
    assert status["gp037_status"]["owner_review_claim_disabled"] is True
    assert status["gp037_status"]["tower_ack_claim_disabled"] is True
    assert status["gp037_status"]["blocker_ack_claim_disabled"] is True
    assert status["gp037_status"]["no_execution_confirmation_claim_disabled"] is True
    assert status["gp037_status"]["owner_review_required"] is True
    assert status["gp037_status"]["owner_confirmation_required"] is True
    assert status["gp037_status"]["owner_reviewed_count"] == 0
    assert status["gp037_status"]["owner_confirmed_count"] == 0
    assert status["gp037_status"]["decision_selected_count"] == 0
    assert status["gp037_status"]["completed_count"] == 0
    assert status["gp037_status"]["auto_completion_disabled"] is True
    assert status["gp037_status"]["auto_confirmation_disabled"] is True
    assert status["gp037_status"]["approval_disabled"] is True
    assert status["gp037_status"]["execution_engine_disabled"] is True
    assert status["gp037_status"]["auto_action_execution_disabled"] is True
    assert status["gp037_status"]["direct_upload_still_locked"] is True
    assert status["gp037_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp037_status"]["external_delivery_still_locked"] is True
    assert status["gp037_status"]["external_access_still_locked"] is True
    assert status["gp037_status"]["packet_export_still_locked"] is True
    assert status["gp037_status"]["unredacted_export_still_locked"] is True
    assert status["gp037_status"]["raw_export_still_locked"] is True
    assert status["gp037_status"]["public_proof_still_locked"] is True
    assert status["gp037_status"]["public_packet_proof_disabled"] is True
    assert status["gp037_status"]["portal_access_still_locked"] is True
    assert status["gp037_status"]["financing_decision_not_claimed"] is True
    assert status["gp037_status"]["legal_advice_not_claimed"] is True
    assert status["gp037_status"]["raw_verification_not_claimed"] is True
    assert status["gp037_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp037"


def test_gp037_truth_keeps_receipts_draft_only_and_restricted_paths_locked():
    status = get_gp037_status()
    truth = status["receipt_truth"]

    assert truth["reviewed_decision_receipt_staging_enabled"] is True
    assert truth["receipt_drafts_enabled"] is True
    assert truth["ack_receipt_previews_enabled"] is True
    assert truth["no_execution_receipt_proof_enabled"] is True
    assert truth["tower_gate_receipt_refs_enabled"] is True
    assert truth["blocker_receipt_refs_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["private_receipt_staging_only"] is True
    assert truth["receipt_staging_means_draft_not_final"] is True
    assert truth["receipt_finalization_enabled"] is False
    assert truth["finalized_receipt_count"] == 0
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


def test_gp037_tower_authority_and_vault_boundaries():
    status = get_gp037_status()
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


def test_gp037_receipt_drafts_cover_owner_review_cards():
    drafts = get_reviewed_decision_receipt_drafts()

    assert drafts["receipt_draft_count"] == 7

    ordered_packet_ids = [draft["packet_id"] for draft in drafts["receipt_drafts"]]
    assert ordered_packet_ids == [
        "ATM_ROUTE_ACQUISITION_PACKET",
        "APARTMENT_LENDER_DUE_DILIGENCE_PACKET",
        "TRUST_ENTITY_AUTHORITY_PACKET",
        "OB_MANUAL_LIVE_PROOF_PACKET",
        "SOULAANA_ARTIST_IP_PACKET",
        "PRIVATE_BETA_ONBOARDING_PACKET",
        "OWNER_ACTION_RECEIPT_PACKET",
    ]

    for draft in drafts["receipt_drafts"]:
        assert draft["receipt_draft_id"].startswith("VRDR-")
        assert draft["receipt_stage_id"].startswith("VRST-")
        assert draft["review_card_id"].startswith("VODR-")
        assert draft["decision_prep_id"].startswith("VDR-")
        assert draft["priority_id"].startswith("VPR-")
        assert draft["review_group_id"].startswith("VPG-")
        assert draft["assembly_id"].startswith("VPA-")
        assert draft["receipt_draft_status"] == "RECEIPT_DRAFT_STAGED_NOT_FINALIZED"
        assert draft["receipt_type"] == "reviewed_decision_receipt_draft"
        assert draft["metadata_only"] is True
        assert draft["private_receipt_staging_only"] is True
        assert draft["receipt_finalized"] is False
        assert draft["official_receipt_claimed"] is False
        assert draft["owner_review_claimed"] is False
        assert draft["tower_ack_claimed"] is False
        assert draft["blocker_ack_claimed"] is False
        assert draft["no_execution_confirmation_claimed"] is False
        assert draft["owner_review_required"] is True
        assert draft["owner_reviewed"] is False
        assert draft["owner_confirmation_required"] is True
        assert draft["owner_confirmed"] is False
        assert draft["decision_selected"] is False
        assert draft["selected_decision_code"] is None
        assert draft["completed"] is False
        assert draft["auto_complete_allowed"] is False
        assert draft["auto_confirm_allowed"] is False
        assert draft["approval_allowed"] is False
        assert draft["can_execute_from_vault"] is False
        assert draft["execution_engine_enabled"] is False
        assert draft["tower_ack_required"] is True
        assert draft["tower_acknowledged"] is False
        assert draft["blocker_ack_required"] is True
        assert draft["blocker_acknowledged"] is False
        assert draft["no_execution_confirmation_required"] is True
        assert draft["no_execution_confirmed"] is False
        assert draft["raw_body_available_count"] == 0
        assert draft["raw_file_body_storage_enabled"] is False
        assert draft["direct_upload_unlocked"] is False
        assert draft["external_delivery_allowed"] is False
        assert draft["external_access_allowed"] is False
        assert draft["packet_export_allowed"] is False
        assert draft["raw_export_allowed"] is False
        assert draft["unredacted_export_allowed"] is False
        assert draft["public_packet_proof_allowed"] is False
        assert draft["portal_access_allowed"] is False
        assert draft["tower_clearance_required"] is True
        assert draft["tower_step_up_required"] is True
        assert draft["vault_can_override_tower"] is False
        assert draft["safe_to_review_privately"] is True
        assert draft["safe_to_finalize_receipt"] is False
        assert draft["safe_to_deliver_externally"] is False
        assert draft["safe_to_export"] is False
        assert draft["safe_to_carry_to_gp038"] is True
        assert "REVIEWED_DECISION_RECEIPT_STAGING_PRIVATE_ONLY" in draft["blocked_codes"]
        assert "RECEIPT_DRAFT_NOT_FINALIZED" in draft["blocked_codes"]
        assert "NO_EXTERNAL_PACKET_DELIVERY" in draft["blocked_codes"]
        assert "NO_PACKET_EXPORT" in draft["blocked_codes"]
        assert "CLOUDS_PARKED" in draft["blocked_codes"]


def test_gp037_ack_receipt_previews_are_previews_only():
    previews = get_reviewed_decision_ack_receipt_previews()["ack_receipt_previews"]

    assert previews["ack_receipt_preview_count"] == 21
    assert previews["ack_type_count"] == 3
    assert previews["receipt_draft_count"] == 7
    assert previews["ack_claimed_count"] == 0
    assert previews["acknowledged_count"] == 0
    assert previews["receipt_finalized_count"] == 0
    assert previews["official_receipt_claimed_count"] == 0
    assert previews["external_delivery_allowed_count"] == 0
    assert previews["packet_export_allowed_count"] == 0
    assert previews["executes_action_count"] == 0
    assert previews["safe_to_continue_ack_receipt_previews"] is True

    ack_types = {item["ack_type"] for item in previews["ack_receipt_preview_items"]}
    assert ack_types == {"tower_gate_ack", "blocker_ack", "no_execution_ack"}

    for item in previews["ack_receipt_preview_items"]:
        assert item["ack_receipt_preview_id"].startswith("VRAP-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["ack_required"] is True
        assert item["ack_claimed"] is False
        assert item["acknowledged"] is False
        assert item["preview_status"] == "ACK_RECEIPT_PREVIEW_ONLY_NOT_ACKNOWLEDGED"
        assert item["metadata_only"] is True
        assert item["private_receipt_staging_only"] is True
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["owner_review_required"] is True
        assert item["owner_confirmed"] is False
        assert item["completed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["executes_action"] is False
        assert item["safe_to_carry_to_gp038"] is True


def test_gp037_no_execution_proof_is_not_confirmed_or_executed():
    proof = get_reviewed_decision_no_execution_proof()["no_execution_proof"]

    assert proof["no_execution_receipt_count"] == 7
    assert proof["no_execution_confirmation_required_count"] == 7
    assert proof["no_execution_confirmed_count"] == 0
    assert proof["no_execution_confirmation_claimed_count"] == 0
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
    assert proof["safe_to_continue_no_execution_proof"] is True

    for item in proof["no_execution_receipt_items"]:
        assert item["no_execution_receipt_id"].startswith("VRNE-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["no_execution_receipt_status"] == "NO_EXECUTION_PROOF_STAGED_NOT_CONFIRMED"
        assert item["no_execution_confirmation_required"] is True
        assert item["no_execution_confirmed"] is False
        assert item["no_execution_confirmation_claimed"] is False
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
        assert item["private_receipt_staging_only"] is True
        assert item["owner_confirmed"] is False
        assert item["completed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["safe_to_carry_to_gp038"] is True


def test_gp037_tower_receipt_refs_preserve_tower_control():
    refs = get_reviewed_decision_tower_receipt_refs()["tower_receipt_refs"]

    assert refs["tower_receipt_ref_count"] == 7
    assert refs["tower_ack_required_count"] == 7
    assert refs["tower_acknowledged_count"] == 0
    assert refs["tower_ack_claimed_count"] == 0
    assert refs["tower_clearance_required_count"] == 7
    assert refs["tower_step_up_required_count"] == 7
    assert refs["tower_export_lock_required_count"] == 7
    assert refs["vault_override_allowed_count"] == 0
    assert refs["receipt_finalized_count"] == 0
    assert refs["official_receipt_claimed_count"] == 0
    assert refs["external_delivery_allowed_count"] == 0
    assert refs["packet_export_allowed_count"] == 0
    assert refs["portal_access_allowed_count"] == 0
    assert refs["all_tower_receipt_refs_preserve_authority"] is True

    for item in refs["tower_receipt_ref_items"]:
        assert item["tower_receipt_ref_id"].startswith("VRTR-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["tower_receipt_ref_status"] == "TOWER_GATE_RECEIPT_REFERENCE_STAGED_NOT_ACKNOWLEDGED"
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
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["safe_to_carry_to_gp038"] is True


def test_gp037_blocker_receipt_refs_keep_restricted_paths_locked():
    refs = get_reviewed_decision_blocker_receipt_refs()["blocker_receipt_refs"]

    assert refs["blocker_receipt_ref_count"] == 7
    assert refs["active_block_code_count"] >= 20
    assert refs["blocker_ack_required_count"] == 7
    assert refs["blocker_acknowledged_count"] == 0
    assert refs["blocker_ack_claimed_count"] == 0
    assert refs["all_restricted_paths_locked"] is True
    assert refs["safe_to_override_inside_vault_count"] == 0
    assert refs["receipt_finalized_count"] == 0
    assert refs["official_receipt_claimed_count"] == 0
    assert refs["external_delivery_allowed_count"] == 0
    assert refs["packet_export_allowed_count"] == 0
    assert refs["public_packet_proof_allowed_count"] == 0
    assert refs["execution_allowed_count"] == 0
    assert refs["safe_to_continue_blocker_receipt_refs"] is True

    codes = set(refs["active_block_codes"])
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "NO_EXTERNAL_PACKET_DELIVERY" in codes
    assert "NO_PACKET_EXPORT" in codes
    assert "REVIEWED_DECISION_RECEIPT_STAGING_PRIVATE_ONLY" in codes
    assert "RECEIPT_DRAFT_NOT_FINALIZED" in codes
    assert "CLOUDS_PARKED" in codes

    for item in refs["blocker_receipt_ref_items"]:
        assert item["blocker_receipt_ref_id"].startswith("VRBR-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["blocker_receipt_ref_status"] == "BLOCKER_RECEIPT_REFERENCE_STAGED_NOT_ACKNOWLEDGED"
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
        assert item["receipt_finalized"] is False
        assert item["official_receipt_claimed"] is False
        assert item["safe_to_carry_to_gp038"] is True


def test_gp037_next_receipts_sorted_and_continue_vault_not_clouds():
    next_receipts = get_reviewed_decision_next_receipts()["next_receipts"]

    assert next_receipts["next_receipt_count"] == 9
    assert next_receipts["packet_receipt_count"] == 7
    assert next_receipts["boundary_receipt_count"] == 1
    assert next_receipts["next_build_receipt_count"] == 1
    assert next_receipts["ack_receipt_preview_count"] == 21
    assert next_receipts["no_execution_receipt_count"] == 7
    assert next_receipts["receipt_finalized_count"] == 0
    assert next_receipts["official_receipt_claimed_count"] == 0
    assert next_receipts["owner_review_claimed_count"] == 0
    assert next_receipts["tower_ack_claimed_count"] == 0
    assert next_receipts["blocker_ack_claimed_count"] == 0
    assert next_receipts["no_execution_confirmation_claimed_count"] == 0
    assert next_receipts["owner_review_required_count"] == 9
    assert next_receipts["decision_selected_count"] == 0
    assert next_receipts["owner_confirmed_count"] == 0
    assert next_receipts["completed_count"] == 0
    assert next_receipts["external_delivery_allowed_count"] == 0
    assert next_receipts["packet_export_allowed_count"] == 0
    assert next_receipts["public_packet_proof_allowed_count"] == 0
    assert next_receipts["safe_to_continue_next_receipts"] is True

    ranks = [item["priority_rank"] for item in next_receipts["next_receipt_items"]]
    assert ranks == sorted(ranks)

    assert next_receipts["next_receipt_items"][0]["packet_id"] == "ATM_ROUTE_ACQUISITION_PACKET"
    assert next_receipts["next_receipt_items"][1]["packet_id"] == "APARTMENT_LENDER_DUE_DILIGENCE_PACKET"
    assert next_receipts["next_receipt_items"][-1]["packet_id"] == "NEXT_VAULT_PACK"

    joined = " ".join(next_receipts["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp038" in joined

    for item in next_receipts["next_receipt_items"]:
        assert item["next_receipt_id"].startswith("VRNX-")
        assert item["metadata_only"] is True
        assert item["private_receipt_staging_only"] is True
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
        assert item["safe_to_carry_to_gp038"] is True


def test_gp037_carry_forward_prepares_gp038():
    carry = get_reviewed_decision_receipt_carry_forward()["carry_forward"]

    assert carry["carry_forward_count"] == 7
    assert carry["ready_for_gp038_count"] == 7
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
    assert carry["safe_to_carry_to_gp038"] is True
    assert carry["next_receipt_count"] == 9

    for item in carry["carry_forward_items"]:
        assert item["carry_forward_id"].startswith("VRDR-CF-")
        assert item["receipt_draft_id"].startswith("VRDR-")
        assert item["review_card_id"].startswith("VODR-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["priority_id"].startswith("VPR-")
        assert item["review_group_id"].startswith("VPG-")
        assert item["carry_forward_status"] == "READY_FOR_GP038_RECEIPT_REVIEW_CLOSE_STAGING"
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
        assert item["safe_to_carry_to_gp038"] is True


def test_gp037_home_routes_declared():
    home = get_reviewed_decision_receipt_staging_home()
    summary = home["receipt_summary"]

    assert summary["section_header"] == "Archive Vault — Controlled Packet Assembly Layer"
    assert summary["section_range"] == "GP031-GP040"
    assert summary["route"] == "/vault/reviewed-decision-receipt-staging"
    assert summary["json_route"] == "/vault/reviewed-decision-receipt-staging.json"
    assert summary["drafts_route"] == "/vault/reviewed-decision-receipt-drafts.json"
    assert summary["ack_previews_route"] == "/vault/reviewed-decision-ack-receipt-previews.json"
    assert summary["no_execution_proof_route"] == "/vault/reviewed-decision-no-execution-proof.json"
    assert summary["tower_refs_route"] == "/vault/reviewed-decision-tower-receipt-refs.json"
    assert summary["blocker_refs_route"] == "/vault/reviewed-decision-blocker-receipt-refs.json"
    assert summary["next_receipts_route"] == "/vault/reviewed-decision-next-receipts.json"
    assert summary["carry_forward_route"] == "/vault/reviewed-decision-receipt-carry-forward.json"
    assert summary["gp037_status_route"] == "/vault/gp037-status.json"
    assert summary["receipt_draft_count"] == 7
    assert summary["ack_receipt_preview_count"] == 21
    assert summary["no_execution_receipt_count"] == 7
    assert summary["next_receipt_count"] == 9
    assert summary["finalized_receipt_count"] == 0
    assert summary["official_receipt_claimed_count"] == 0
    assert summary["metadata_only"] is True

    assert home["gp036_connection"]["gp036_ready"] is True
    assert home["gp036_connection"]["gp036_safe_to_continue"] is True
    assert home["gp036_connection"]["gp036_vault_done"] is False
    assert home["gp036_connection"]["gp036_review_card_count"] == 7
    assert home["gp036_connection"]["gp036_selection_preview_count"] == 7
    assert home["gp036_connection"]["gp036_no_execution_confirmation_count"] == 7
    assert home["gp036_connection"]["gp036_next_review_count"] == 9


def test_gp037_html_is_dark_and_has_no_white_background_tokens():
    html = render_reviewed_decision_receipt_staging_page()
    lowered = html.lower()

    assert "Vault Reviewed Decision Receipt Staging" in html
    assert "Archive Vault" in html
    assert "/vault/reviewed-decision-receipt-staging.json" in html
    assert "/vault/gp037-status.json" in html
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


def test_gp037_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/reviewed-decision-receipt-staging",
        "/vault/reviewed-decision-receipt-staging.json",
        "/vault/reviewed-decision-receipt-drafts.json",
        "/vault/reviewed-decision-ack-receipt-previews.json",
        "/vault/reviewed-decision-no-execution-proof.json",
        "/vault/reviewed-decision-tower-receipt-refs.json",
        "/vault/reviewed-decision-blocker-receipt-refs.json",
        "/vault/reviewed-decision-next-receipts.json",
        "/vault/reviewed-decision-receipt-carry-forward.json",
        "/vault/gp037-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp037_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/reviewed-decision-receipt-staging",
        "/vault/reviewed-decision-receipt-staging.json",
        "/vault/reviewed-decision-receipt-drafts.json",
        "/vault/reviewed-decision-ack-receipt-previews.json",
        "/vault/reviewed-decision-no-execution-proof.json",
        "/vault/reviewed-decision-tower-receipt-refs.json",
        "/vault/reviewed-decision-blocker-receipt-refs.json",
        "/vault/reviewed-decision-next-receipts.json",
        "/vault/reviewed-decision-receipt-carry-forward.json",
        "/vault/gp037-status.json",
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
                assert b"Vault Reviewed Decision Receipt Staging" in response.data
