"""
Tests for VAULT GIANT PACK 045 — Storage Access Receipt Preview
"""

from pathlib import Path

import pytest

from vault.storage_access_receipt_preview_service import (
    get_gp045_status,
    get_storage_access_denial_receipt_summaries,
    get_storage_access_no_grant_receipt_labels,
    get_storage_access_owner_review_receipts,
    get_storage_access_receipt_cards,
    get_storage_access_receipt_next_step,
    get_storage_access_receipt_preview_home,
    get_storage_access_tower_requirement_receipts,
    render_storage_access_receipt_preview_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp045_status_ready_safe_continue_not_done():
    status = get_gp045_status()
    gp045 = status["gp045_status"]

    assert status["pack"]["id"] == "VAULT_GP045"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert status["pack"]["section_range"] == "GP041-GP050"

    assert gp045["ready"] is True
    assert gp045["section_id"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert gp045["section_title"] == "Archive Vault — Next Product Depth Layer"
    assert gp045["section_range"] == "GP041-GP050"
    assert gp045["storage_access_receipt_preview_ready"] is True
    assert gp045["safe_to_continue_to_gp046"] is True
    assert gp045["vault_done"] is False
    assert gp045["foundation_status"] == "safe_to_continue_not_done"
    assert gp045["metadata_only_receipt_preview"] is True
    assert gp045["private_preview_only"] is True
    assert gp045["receipt_cards_ready"] is True
    assert gp045["official_receipt_created_count"] == 0
    assert gp045["official_receipt_claimed_count"] == 0
    assert gp045["finalized_receipt_count"] == 0
    assert gp045["closed_receipt_count"] == 0
    assert gp045["receipt_finalized"] is False
    assert gp045["receipt_closed"] is False
    assert gp045["access_request_submitted_count"] == 0
    assert gp045["access_request_approved_count"] == 0
    assert gp045["access_request_granted_count"] == 0
    assert gp045["decision_approved_count"] == 0
    assert gp045["decision_granted_count"] == 0
    assert gp045["access_denied_by_default"] is True
    assert gp045["no_grant_receipt_enforced"] is True
    assert gp045["provider_selected"] is False
    assert gp045["provider_configured"] is False
    assert gp045["provider_write_enabled"] is False
    assert gp045["provider_read_enabled"] is False
    assert gp045["provider_object_read_claimed"] is False
    assert gp045["object_body_view_enabled"] is False
    assert gp045["raw_file_body_storage_still_locked"] is True
    assert gp045["file_body_persisted_count"] == 0
    assert gp045["object_body_available_count"] == 0
    assert gp045["direct_upload_still_locked"] is True
    assert gp045["checksum_verification_not_claimed"] is True
    assert gp045["hash_verification_not_claimed"] is True
    assert gp045["external_delivery_still_locked"] is True
    assert gp045["packet_export_still_locked"] is True
    assert gp045["approval_disabled"] is True
    assert gp045["execution_engine_disabled"] is True
    assert gp045["clouds_status"] == "parked_do_not_continue_from_vault_gp045"
    assert gp045["next_pack"] == "VAULT_GP046_STORAGE_AUDIT_TRAIL_PREVIEW"


def test_gp045_receipt_truth_preview_only_no_official_final_or_close():
    status = get_gp045_status()
    truth = status["receipt_truth"]

    assert truth["storage_access_receipt_preview_ready"] is True
    assert truth["receipt_preview_cards_visible"] is True
    assert truth["no_grant_receipt_labels_visible"] is True
    assert truth["tower_requirement_receipt_snapshots_visible"] is True
    assert truth["owner_review_receipt_placeholders_visible"] is True
    assert truth["denial_receipt_summaries_visible"] is True
    assert truth["metadata_only"] is True
    assert truth["private_preview_only"] is True

    assert truth["receipt_preview_created_count"] == 7
    assert truth["official_receipt_created_count"] == 0
    assert truth["official_receipt_claimed_count"] == 0
    assert truth["finalized_receipt_count"] == 0
    assert truth["closed_receipt_count"] == 0
    assert truth["receipt_finalized"] is False
    assert truth["receipt_closed"] is False
    assert truth["access_request_submitted_count"] == 0
    assert truth["access_request_approved_count"] == 0
    assert truth["access_request_granted_count"] == 0
    assert truth["decision_approved_count"] == 0
    assert truth["decision_granted_count"] == 0
    assert truth["access_denied_by_default_count"] == 7
    assert truth["no_grant_receipt_count"] == 7

    assert truth["provider_selected"] is False
    assert truth["provider_configured"] is False
    assert truth["provider_write_enabled"] is False
    assert truth["provider_read_enabled"] is False
    assert truth["provider_object_read_claimed"] is False
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["file_body_persisted_count"] == 0
    assert truth["object_body_available_count"] == 0
    assert truth["object_body_view_enabled"] is False
    assert truth["direct_upload_unlocked"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["checksum_verified_count"] == 0
    assert truth["hash_verified_count"] == 0

    assert truth["external_packet_delivery_enabled"] is False
    assert truth["external_access_enabled"] is False
    assert truth["packet_export_enabled"] is False
    assert truth["unredacted_export_enabled"] is False
    assert truth["raw_export_enabled"] is False
    assert truth["public_packet_proof_enabled"] is False
    assert truth["public_proof_enabled"] is False
    assert truth["portal_access_enabled"] is False
    assert truth["approval_enabled"] is False
    assert truth["execution_engine_enabled"] is False
    assert truth["auto_action_execution_enabled"] is False
    assert truth["financing_decision_enabled"] is False
    assert truth["legal_advice_enabled"] is False
    assert truth["raw_document_verification_claimed"] is False
    assert truth["vault_done"] is False
    assert truth["clouds_should_continue"] is False
    assert truth["safe_to_continue_to_gp046"] is True


def test_gp045_connected_to_gp044():
    home = get_storage_access_receipt_preview_home()

    assert home["gp044_connection"]["gp044_ready"] is True
    assert home["gp044_connection"]["gp044_safe_to_continue"] is True
    assert home["gp044_connection"]["gp044_vault_done"] is False
    assert home["gp044_connection"]["gp044_section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert home["gp044_connection"]["gp044_decision_card_count"] == 7
    assert home["gp044_connection"]["gp044_tower_requirement_count"] == 56
    assert home["gp044_connection"]["gp044_owner_review_placeholder_count"] == 28
    assert home["gp044_connection"]["gp044_denial_reason_label_count"] == 49
    assert home["gp044_connection"]["gp044_no_grant_enforcement_count"] == 7


def test_gp045_tower_authority_and_vault_boundaries():
    status = get_gp045_status()
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
    assert tower["tower_owns_storage_provider_authorization"] is True
    assert tower["tower_owns_object_visibility"] is True
    assert tower["tower_owns_storage_access_authorization"] is True
    assert tower["tower_owns_access_decision_approval"] is True
    assert tower["tower_owns_receipt_authority"] is True
    assert tower["vault_owns_tower_permissions"] is False
    assert tower["vault_can_override_tower_storage_authority"] is False
    assert tower["vault_can_override_tower_visibility"] is False
    assert tower["vault_can_grant_storage_access"] is False
    assert tower["vault_can_approve_storage_access_decision"] is False
    assert tower["vault_can_finalize_storage_access_receipt"] is False

    assert vault["no_public_vault"] is True
    assert vault["direct_raw_upload_unlocked"] is False
    assert vault["permanent_file_body_storage_enabled"] is False
    assert vault["external_access_default"] == "denied"
    assert vault["storage_access_default"] == "denied_by_default"
    assert vault["decision_default"] == "blocked_denied_by_default"
    assert vault["receipt_default"] == "preview_only_not_official_not_final"
    assert vault["external_packet_delivery_allowed"] is False
    assert vault["packet_export_allowed"] is False
    assert vault["unredacted_export_allowed"] is False
    assert vault["raw_export_allowed"] is False
    assert vault["redacted_owner_preview_allowed"] is True
    assert vault["object_body_preview_allowed"] is False
    assert vault["object_body_view_allowed"] is False
    assert vault["provider_read_allowed"] is False
    assert vault["provider_write_allowed"] is False
    assert vault["sensitive_body_display_in_summary_views"] is False
    assert vault["beneficiary_details_in_summary_views"] is False
    assert vault["broker_secret_storage_allowed"] is False
    assert vault["public_ob_proof_allowed"] is False
    assert vault["public_packet_proof_allowed"] is False
    assert vault["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp045_receipt_cards_preview_only():
    cards = get_storage_access_receipt_cards()["receipt_cards"]

    assert cards["receipt_card_count"] == 7
    assert cards["receipt_preview_type_count"] == 4
    assert cards["receipt_preview_created_count"] == 7
    assert cards["official_receipt_created_count"] == 0
    assert cards["official_receipt_claimed_count"] == 0
    assert cards["receipt_finalized_count"] == 0
    assert cards["receipt_closed_count"] == 0
    assert cards["receipt_export_allowed_count"] == 0
    assert cards["receipt_external_delivery_allowed_count"] == 0
    assert cards["receipt_public_proof_allowed_count"] == 0
    assert cards["access_request_submitted_count"] == 0
    assert cards["access_request_approved_count"] == 0
    assert cards["access_granted_count"] == 0
    assert cards["decision_approved_count"] == 0
    assert cards["decision_granted_count"] == 0
    assert cards["no_grant_receipt_count"] == 7
    assert cards["tower_requirements_missing_count"] == 7
    assert cards["owner_review_missing_count"] == 7
    assert cards["provider_read_enabled_count"] == 0
    assert cards["provider_write_enabled_count"] == 0
    assert cards["object_body_view_enabled_count"] == 0
    assert cards["object_body_available_count"] == 0
    assert cards["file_body_persisted_count"] == 0
    assert cards["raw_file_body_storage_enabled_count"] == 0
    assert cards["direct_upload_enabled_count"] == 0
    assert cards["checksum_verified_count"] == 0
    assert cards["hash_verified_count"] == 0
    assert cards["export_allowed_count"] == 0
    assert cards["external_delivery_allowed_count"] == 0
    assert cards["portal_access_allowed_count"] == 0
    assert cards["approval_allowed_count"] == 0
    assert cards["execution_allowed_count"] == 0
    assert cards["safe_to_continue_receipt_cards"] is True

    scopes = {item["scope"] for item in cards["receipt_card_items"]}
    assert scopes == {
        "document_intake",
        "attachment_registry",
        "requirement_match",
        "evidence_binder",
        "packet_workspace",
        "controlled_packet_assembly",
        "receipt_chain",
    }

    for item in cards["receipt_card_items"]:
        assert item["receipt_card_id"].startswith("VSARP-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["object_key_contract_id"].startswith("VSOK-")
        assert item["checksum_placeholder_id"].startswith("VSCHK-")
        assert item["receipt_preview_status"] == "PREVIEW_ONLY_NOT_OFFICIAL_NOT_FINAL"
        assert item["receipt_owner_label"] == "Receipt preview only — no access granted"
        assert item["metadata_only"] is True
        assert item["private_preview_only"] is True
        assert item["receipt_preview_created"] is True
        assert item["official_receipt_created"] is False
        assert item["official_receipt_claimed"] is False
        assert item["receipt_finalized"] is False
        assert item["receipt_closed"] is False
        assert item["receipt_export_allowed"] is False
        assert item["receipt_external_delivery_allowed"] is False
        assert item["receipt_public_proof_allowed"] is False
        assert item["access_request_submitted"] is False
        assert item["access_request_approved"] is False
        assert item["access_granted"] is False
        assert item["decision_approved"] is False
        assert item["decision_granted"] is False
        assert item["no_grant_receipt"] is True
        assert item["tower_requirements_missing"] is True
        assert item["owner_review_missing"] is True
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["file_body_persisted"] is False
        assert item["raw_file_body_storage_enabled"] is False
        assert item["direct_upload_enabled"] is False
        assert item["checksum_verified"] is False
        assert item["hash_verified"] is False
        assert item["export_allowed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["approval_allowed"] is False
        assert item["execution_allowed"] is False


def test_gp045_no_grant_receipt_labels_enforce_no_grant():
    labels = get_storage_access_no_grant_receipt_labels()["no_grant_receipt_labels"]

    assert labels["no_grant_receipt_label_count"] == 7
    assert labels["no_grant_receipt_count"] == 7
    assert labels["access_granted_count"] == 0
    assert labels["decision_granted_count"] == 0
    assert labels["official_receipt_claimed_count"] == 0
    assert labels["receipt_finalized_count"] == 0
    assert labels["receipt_closed_count"] == 0
    assert labels["provider_read_enabled_count"] == 0
    assert labels["object_body_view_enabled_count"] == 0
    assert labels["external_delivery_allowed_count"] == 0
    assert labels["export_allowed_count"] == 0
    assert labels["portal_access_allowed_count"] == 0
    assert labels["public_proof_allowed_count"] == 0
    assert labels["execution_allowed_count"] == 0
    assert labels["safe_to_continue_no_grant_receipt_labels"] is True

    for item in labels["no_grant_receipt_label_items"]:
        assert item["no_grant_receipt_label_id"].startswith("VSANGRL-")
        assert item["receipt_card_id"].startswith("VSARP-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["no_grant_label"] == "NO_GRANT_RECEIPT_PREVIEW_ONLY"
        assert item["owner_label"] == "No access granted — receipt preview only"
        assert item["metadata_only"] is True
        assert item["no_grant_receipt"] is True
        assert item["access_granted"] is False
        assert item["decision_granted"] is False
        assert item["official_receipt_claimed"] is False
        assert item["receipt_finalized"] is False
        assert item["receipt_closed"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["external_delivery_allowed"] is False
        assert item["export_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["public_proof_allowed"] is False
        assert item["execution_allowed"] is False


def test_gp045_tower_requirement_receipts_required_not_granted():
    receipts = get_storage_access_tower_requirement_receipts()["tower_requirement_receipts"]

    assert receipts["tower_requirement_receipt_count"] == 56
    assert receipts["receipt_snapshot_created_count"] == 56
    assert receipts["required_count"] == 56
    assert receipts["granted_count"] == 0
    assert receipts["official_receipt_claimed_count"] == 0
    assert receipts["receipt_finalized_count"] == 0
    assert receipts["receipt_closed_count"] == 0
    assert receipts["vault_override_allowed_count"] == 0
    assert receipts["decision_approved_count"] == 0
    assert receipts["decision_granted_count"] == 0
    assert receipts["access_granted_count"] == 0
    assert receipts["provider_read_enabled_count"] == 0
    assert receipts["object_body_view_enabled_count"] == 0
    assert receipts["export_allowed_count"] == 0
    assert receipts["external_delivery_allowed_count"] == 0
    assert receipts["safe_to_continue_tower_requirement_receipts"] is True

    for item in receipts["tower_requirement_receipt_items"]:
        assert item["tower_requirement_receipt_id"].startswith("VSATRS-")
        assert item["tower_requirement_id"].startswith("VSATR-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["receipt_snapshot_status"] == "REQUIRED_NOT_GRANTED_SNAPSHOT"
        assert item["metadata_only"] is True
        assert item["required"] is True
        assert item["granted"] is False
        assert item["receipt_snapshot_created"] is True
        assert item["official_receipt_claimed"] is False
        assert item["receipt_finalized"] is False
        assert item["receipt_closed"] is False
        assert item["vault_can_override"] is False
        assert item["decision_approved"] is False
        assert item["decision_granted"] is False
        assert item["access_granted"] is False


def test_gp045_owner_review_receipts_empty_not_confirmed():
    receipts = get_storage_access_owner_review_receipts()["owner_review_receipts"]

    assert receipts["owner_review_receipt_placeholder_count"] == 28
    assert receipts["receipt_snapshot_created_count"] == 28
    assert receipts["owner_review_required_count"] == 28
    assert receipts["owner_reviewed_count"] == 0
    assert receipts["owner_confirmed_count"] == 0
    assert receipts["field_value_present_count"] == 0
    assert receipts["official_receipt_claimed_count"] == 0
    assert receipts["receipt_finalized_count"] == 0
    assert receipts["receipt_closed_count"] == 0
    assert receipts["decision_approved_count"] == 0
    assert receipts["decision_granted_count"] == 0
    assert receipts["access_granted_count"] == 0
    assert receipts["provider_read_enabled_count"] == 0
    assert receipts["object_body_view_enabled_count"] == 0
    assert receipts["external_delivery_allowed_count"] == 0
    assert receipts["export_allowed_count"] == 0
    assert receipts["safe_to_continue_owner_review_receipts"] is True

    for item in receipts["owner_review_receipt_placeholder_items"]:
        assert item["owner_review_receipt_placeholder_id"].startswith("VSAORR-")
        assert item["owner_review_placeholder_id"].startswith("VSAOR-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["receipt_placeholder_status"] == "EMPTY_NOT_REVIEWED_NOT_CONFIRMED"
        assert item["metadata_only"] is True
        assert item["owner_review_required"] is True
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["field_value_present"] is False
        assert item["receipt_snapshot_created"] is True
        assert item["official_receipt_claimed"] is False
        assert item["receipt_finalized"] is False
        assert item["receipt_closed"] is False
        assert item["decision_approved"] is False
        assert item["decision_granted"] is False
        assert item["access_granted"] is False


def test_gp045_denial_receipt_summaries_block_receipt_and_access():
    summaries = get_storage_access_denial_receipt_summaries()["denial_receipt_summaries"]

    assert summaries["denial_receipt_summary_count"] == 49
    assert summaries["denied_by_default_count"] == 49
    assert summaries["blocks_official_receipt_count"] == 49
    assert summaries["blocks_final_receipt_count"] == 49
    assert summaries["blocks_receipt_close_count"] == 49
    assert summaries["blocks_access_grant_count"] == 49
    assert summaries["blocks_provider_read_count"] == 49
    assert summaries["blocks_object_body_view_count"] == 49
    assert summaries["blocks_export_count"] == 49
    assert summaries["blocks_external_delivery_count"] == 49
    assert summaries["blocks_portal_access_count"] == 49
    assert summaries["blocks_execution_count"] == 49
    assert summaries["official_receipt_claimed_count"] == 0
    assert summaries["receipt_finalized_count"] == 0
    assert summaries["receipt_closed_count"] == 0
    assert summaries["safe_to_continue_denial_receipt_summaries"] is True

    reasons = {item["denial_reason"] for item in summaries["denial_receipt_summary_items"]}
    assert reasons == {
        "request_not_submitted",
        "tower_clearance_missing",
        "tower_step_up_missing",
        "storage_access_authorization_missing",
        "provider_read_locked",
        "object_body_view_locked",
        "export_locked",
    }

    for item in summaries["denial_receipt_summary_items"]:
        assert item["denial_receipt_summary_id"].startswith("VSADRS-")
        assert item["denial_reason_label_id"].startswith("VSADRL-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["denial_receipt_status"] == "ACTIVE_DENIAL_RECEIPT_SUMMARY"
        assert item["metadata_only"] is True
        assert item["denied_by_default"] is True
        assert item["blocks_official_receipt"] is True
        assert item["blocks_final_receipt"] is True
        assert item["blocks_receipt_close"] is True
        assert item["blocks_access_grant"] is True
        assert item["blocks_provider_read"] is True
        assert item["blocks_object_body_view"] is True
        assert item["blocks_export"] is True
        assert item["blocks_external_delivery"] is True
        assert item["blocks_portal_access"] is True
        assert item["blocks_execution"] is True
        assert item["official_receipt_claimed"] is False
        assert item["receipt_finalized"] is False
        assert item["receipt_closed"] is False


def test_gp045_next_step_carries_forward_to_gp046_not_clouds():
    next_step = get_storage_access_receipt_next_step()["next_step"]

    assert next_step["next_step_count"] == 3
    assert next_step["ready_for_gp046_count"] == 3
    assert next_step["receipt_card_count"] == 7
    assert next_step["no_grant_receipt_label_count"] == 7
    assert next_step["tower_requirement_receipt_count"] == 56
    assert next_step["owner_review_receipt_placeholder_count"] == 28
    assert next_step["denial_receipt_summary_count"] == 49
    assert next_step["safe_to_continue_to_gp046"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False
    assert next_step["recommended_next_pack"] == "VAULT_GP046"
    assert next_step["recommended_next_pack_title"] == "Storage Audit Trail Preview"

    note = next_step["owner_notebook_note"].lower()
    assert "archive vault — next product depth layer" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "receipt previews metadata-only" in rules
    assert "preview-only, not official" in rules
    assert "no finalized receipt claim" in rules
    assert "no receipt close claim" in rules
    assert "no-grant receipt labels active" in rules
    assert "safe to continue, not vault done" in rules

    for item in next_step["next_step_items"]:
        assert item["next_step_id"].startswith("VSARPNX-")
        assert item["target_pack"] == "VAULT_GP046"
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False


def test_gp045_routes_and_counts_declared():
    home = get_storage_access_receipt_preview_home()
    routes = home["receipt_routes"]
    counts = home["receipt_counts"]

    assert routes["section_header"] == "Archive Vault — Next Product Depth Layer"
    assert routes["section_range"] == "GP041-GP050"
    assert routes["route"] == "/vault/storage-access-receipt-preview"
    assert routes["json_route"] == "/vault/storage-access-receipt-preview.json"
    assert routes["receipt_cards_route"] == "/vault/storage-access-receipt-cards.json"
    assert routes["no_grant_receipt_labels_route"] == "/vault/storage-access-no-grant-receipt-labels.json"
    assert routes["tower_requirement_receipts_route"] == "/vault/storage-access-tower-requirement-receipts.json"
    assert routes["owner_review_receipts_route"] == "/vault/storage-access-owner-review-receipts.json"
    assert routes["denial_receipt_summaries_route"] == "/vault/storage-access-denial-receipt-summaries.json"
    assert routes["next_step_route"] == "/vault/storage-access-receipt-next-step.json"
    assert routes["gp045_status_route"] == "/vault/gp045-status.json"

    assert counts["receipt_card_count"] == 7
    assert counts["receipt_preview_type_count"] == 4
    assert counts["no_grant_receipt_label_count"] == 7
    assert counts["tower_requirement_receipt_count"] == 56
    assert counts["owner_review_receipt_placeholder_count"] == 28
    assert counts["denial_receipt_summary_count"] == 49
    assert counts["official_receipt_created_count"] == 0
    assert counts["official_receipt_claimed_count"] == 0
    assert counts["finalized_receipt_count"] == 0
    assert counts["closed_receipt_count"] == 0
    assert counts["access_request_submitted_count"] == 0
    assert counts["access_request_approved_count"] == 0
    assert counts["access_request_granted_count"] == 0
    assert counts["decision_approved_count"] == 0
    assert counts["decision_granted_count"] == 0
    assert counts["provider_read_enabled_count"] == 0
    assert counts["provider_write_enabled_count"] == 0
    assert counts["object_body_view_enabled_count"] == 0
    assert counts["file_body_persisted_count"] == 0
    assert counts["object_body_available_count"] == 0
    assert counts["checksum_verified_count"] == 0
    assert counts["hash_verified_count"] == 0
    assert counts["raw_file_body_storage_enabled_count"] == 0
    assert counts["direct_upload_unlocked_count"] == 0
    assert counts["external_delivery_allowed_count"] == 0
    assert counts["packet_export_allowed_count"] == 0
    assert counts["execution_allowed_count"] == 0
    assert counts["metadata_only"] is True


def test_gp045_html_is_dark_and_has_no_white_background_tokens():
    html = render_storage_access_receipt_preview_page()
    lowered = html.lower()

    assert "Vault Storage Access Receipt Preview" in html
    assert "Archive Vault" in html
    assert "/vault/storage-access-receipt-preview.json" in html
    assert "/vault/gp045-status.json" in html
    assert "Clouds parked" in html
    assert "No official receipt" in html
    assert "No final receipt" in html
    assert "No access grant" in html

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


def test_gp045_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-access-receipt-preview",
        "/vault/storage-access-receipt-preview.json",
        "/vault/storage-access-receipt-cards.json",
        "/vault/storage-access-no-grant-receipt-labels.json",
        "/vault/storage-access-tower-requirement-receipts.json",
        "/vault/storage-access-owner-review-receipts.json",
        "/vault/storage-access-denial-receipt-summaries.json",
        "/vault/storage-access-receipt-next-step.json",
        "/vault/gp045-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp045_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-access-receipt-preview",
        "/vault/storage-access-receipt-preview.json",
        "/vault/storage-access-receipt-cards.json",
        "/vault/storage-access-no-grant-receipt-labels.json",
        "/vault/storage-access-tower-requirement-receipts.json",
        "/vault/storage-access-owner-review-receipts.json",
        "/vault/storage-access-denial-receipt-summaries.json",
        "/vault/storage-access-receipt-next-step.json",
        "/vault/gp045-status.json",
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
                assert b"Vault Storage Access Receipt Preview" in response.data
