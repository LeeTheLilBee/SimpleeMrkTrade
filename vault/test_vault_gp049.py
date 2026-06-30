"""
Tests for VAULT GIANT PACK 049 — Storage Audit Action Receipt Preview
"""

from pathlib import Path

import pytest

from vault.storage_audit_action_receipt_preview_service import (
    get_gp049_status,
    get_storage_audit_action_receipt_cards,
    get_storage_audit_action_receipt_next_step,
    get_storage_audit_action_receipt_preview_home,
    get_storage_audit_blocked_action_receipt_labels,
    get_storage_audit_followup_receipt_placeholders,
    get_storage_audit_no_execution_receipts,
    get_storage_tower_action_gate_receipts,
    render_storage_audit_action_receipt_preview_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp049_status_ready_safe_continue_not_done():
    status = get_gp049_status()
    gp049 = status["gp049_status"]

    assert status["pack"]["id"] == "VAULT_GP049"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert status["pack"]["section_range"] == "GP041-GP050"

    assert gp049["ready"] is True
    assert gp049["section_id"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert gp049["section_title"] == "Archive Vault — Next Product Depth Layer"
    assert gp049["section_range"] == "GP041-GP050"
    assert gp049["storage_audit_action_receipt_preview_ready"] is True
    assert gp049["safe_to_continue_to_gp050"] is True
    assert gp049["vault_done"] is False
    assert gp049["foundation_status"] == "safe_to_continue_not_done"
    assert gp049["metadata_only_action_receipt_preview"] is True
    assert gp049["private_action_receipt_preview_only"] is True
    assert gp049["action_receipt_cards_ready"] is True

    assert gp049["official_action_receipt_created_count"] == 0
    assert gp049["official_action_receipt_claimed_count"] == 0
    assert gp049["finalized_action_receipt_count"] == 0
    assert gp049["closed_action_receipt_count"] == 0
    assert gp049["action_receipt_finalized"] is False
    assert gp049["action_receipt_closed"] is False
    assert gp049["action_approved_count"] == 0
    assert gp049["action_executed_count"] == 0
    assert gp049["action_completed_count"] == 0
    assert gp049["action_closed_count"] == 0
    assert gp049["audit_review_approved_count"] == 0
    assert gp049["official_audit_log_written_count"] == 0
    assert gp049["immutable_audit_write_count"] == 0
    assert gp049["tower_attestation_written_count"] == 0
    assert gp049["official_storage_receipt_claimed_count"] == 0
    assert gp049["finalized_storage_receipt_count"] == 0
    assert gp049["closed_storage_receipt_count"] == 0
    assert gp049["access_request_granted_count"] == 0
    assert gp049["decision_granted_count"] == 0
    assert gp049["blocked_action_receipts_active"] is True
    assert gp049["no_execution_receipts_active"] is True

    assert gp049["provider_read_enabled"] is False
    assert gp049["provider_write_enabled"] is False
    assert gp049["object_body_view_enabled"] is False
    assert gp049["raw_file_body_storage_still_locked"] is True
    assert gp049["file_body_persisted_count"] == 0
    assert gp049["object_body_available_count"] == 0
    assert gp049["direct_upload_still_locked"] is True
    assert gp049["checksum_verification_not_claimed"] is True
    assert gp049["hash_verification_not_claimed"] is True
    assert gp049["external_delivery_still_locked"] is True
    assert gp049["packet_export_still_locked"] is True
    assert gp049["approval_disabled"] is True
    assert gp049["execution_engine_disabled"] is True
    assert gp049["clouds_status"] == "parked_do_not_continue_from_vault_gp049"
    assert gp049["next_pack"] == "VAULT_GP050_NEXT_PRODUCT_DEPTH_READINESS_CHECKPOINT"


def test_gp049_action_receipt_truth_metadata_only_no_official_final_close_or_execution():
    status = get_gp049_status()
    truth = status["action_receipt_truth"]

    assert truth["storage_audit_action_receipt_preview_ready"] is True
    assert truth["action_receipt_preview_cards_visible"] is True
    assert truth["blocked_action_receipt_labels_visible"] is True
    assert truth["tower_action_gate_receipt_snapshots_visible"] is True
    assert truth["reviewer_followup_receipt_placeholders_visible"] is True
    assert truth["no_execution_receipt_enforcement_visible"] is True
    assert truth["metadata_only"] is True
    assert truth["private_action_receipt_preview_only"] is True

    assert truth["action_receipt_preview_count"] == 35
    assert truth["official_action_receipt_created_count"] == 0
    assert truth["official_action_receipt_claimed_count"] == 0
    assert truth["finalized_action_receipt_count"] == 0
    assert truth["closed_action_receipt_count"] == 0
    assert truth["action_receipt_finalized"] is False
    assert truth["action_receipt_closed"] is False
    assert truth["action_approved_count"] == 0
    assert truth["action_executed_count"] == 0
    assert truth["action_completed_count"] == 0
    assert truth["action_closed_count"] == 0
    assert truth["audit_review_approved_count"] == 0
    assert truth["official_audit_log_created_count"] == 0
    assert truth["official_audit_log_written_count"] == 0
    assert truth["immutable_audit_write_count"] == 0
    assert truth["tower_attestation_written_count"] == 0
    assert truth["official_storage_receipt_claimed_count"] == 0
    assert truth["finalized_storage_receipt_count"] == 0
    assert truth["closed_storage_receipt_count"] == 0
    assert truth["access_request_granted_count"] == 0
    assert truth["decision_granted_count"] == 0
    assert truth["access_denied_by_default_count"] == 7

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
    assert truth["checksum_verified_count"] == 0
    assert truth["hash_verified_count"] == 0

    assert truth["external_packet_delivery_enabled"] is False
    assert truth["external_access_enabled"] is False
    assert truth["packet_export_enabled"] is False
    assert truth["public_proof_enabled"] is False
    assert truth["portal_access_enabled"] is False
    assert truth["approval_enabled"] is False
    assert truth["execution_engine_enabled"] is False
    assert truth["vault_done"] is False
    assert truth["clouds_should_continue"] is False
    assert truth["safe_to_continue_to_gp050"] is True


def test_gp049_connected_to_gp048():
    home = get_storage_audit_action_receipt_preview_home()

    assert home["gp048_connection"]["gp048_ready"] is True
    assert home["gp048_connection"]["gp048_safe_to_continue"] is True
    assert home["gp048_connection"]["gp048_vault_done"] is False
    assert home["gp048_connection"]["gp048_section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert home["gp048_connection"]["gp048_action_suggestion_count"] == 35
    assert home["gp048_connection"]["gp048_blocked_action_label_count"] == 35
    assert home["gp048_connection"]["gp048_tower_action_authority_gate_count"] == 210
    assert home["gp048_connection"]["gp048_reviewer_followup_placeholder_count"] == 140
    assert home["gp048_connection"]["gp048_no_execution_enforcement_count"] == 35
    assert home["gp048_connection"]["gp048_action_executed_count"] == 0


def test_gp049_tower_authority_and_vault_boundaries():
    status = get_gp049_status()
    tower = status["tower_authority"]
    vault = status["vault_boundary"]

    assert tower["tower_owns_identity"] is True
    assert tower["tower_owns_permissions"] is True
    assert tower["tower_owns_action_authority_gates"] is True
    assert tower["tower_owns_execution_gates"] is True
    assert tower["tower_owns_audit_action_authority"] is True
    assert tower["tower_owns_action_receipt_authority"] is True
    assert tower["vault_can_write_official_audit_log"] is False
    assert tower["vault_can_approve_audit_review"] is False
    assert tower["vault_can_approve_audit_action"] is False
    assert tower["vault_can_execute_audit_action"] is False
    assert tower["vault_can_finalize_action_receipt"] is False

    assert vault["no_public_vault"] is True
    assert vault["action_default"] == "suggestion_only_blocked_no_execution"
    assert vault["action_receipt_default"] == "preview_only_not_official_not_final_not_closed"
    assert vault["review_default"] == "metadata_only_unapproved_unclosed"
    assert vault["audit_default"] == "preview_only_not_official_not_immutable"
    assert vault["external_packet_delivery_allowed"] is False
    assert vault["packet_export_allowed"] is False
    assert vault["object_body_view_allowed"] is False
    assert vault["provider_read_allowed"] is False
    assert vault["provider_write_allowed"] is False
    assert vault["official_audit_log_write_allowed"] is False
    assert vault["immutable_log_write_allowed"] is False
    assert vault["audit_review_approval_allowed"] is False
    assert vault["audit_action_approval_allowed"] is False
    assert vault["audit_action_execution_allowed"] is False
    assert vault["action_receipt_finalize_allowed"] is False
    assert vault["public_packet_proof_allowed"] is False


def test_gp049_action_receipt_cards_preview_only():
    cards = get_storage_audit_action_receipt_cards()["action_receipt_cards"]

    assert cards["source_action_suggestion_count"] == 35
    assert cards["action_receipt_card_count"] == 35
    assert cards["action_receipt_preview_type_count"] == 5
    assert cards["action_receipt_preview_created_count"] == 35
    assert cards["official_action_receipt_created_count"] == 0
    assert cards["official_action_receipt_claimed_count"] == 0
    assert cards["action_receipt_finalized_count"] == 0
    assert cards["action_receipt_closed_count"] == 0
    assert cards["action_approved_count"] == 0
    assert cards["action_executed_count"] == 0
    assert cards["blocked_action_receipt_count"] == 35
    assert cards["no_execution_receipt_count"] == 35
    assert cards["tower_action_authority_required_count"] == 35
    assert cards["tower_action_authority_granted_count"] == 0
    assert cards["reviewer_followup_required_count"] == 35
    assert cards["reviewer_followup_present_count"] == 0
    assert cards["official_audit_log_written_count"] == 0
    assert cards["immutable_audit_written_count"] == 0
    assert cards["tower_attestation_written_count"] == 0
    assert cards["access_granted_count"] == 0
    assert cards["provider_read_enabled_count"] == 0
    assert cards["provider_write_enabled_count"] == 0
    assert cards["object_body_view_enabled_count"] == 0
    assert cards["file_body_persisted_count"] == 0
    assert cards["checksum_verified_count"] == 0
    assert cards["hash_verified_count"] == 0
    assert cards["export_allowed_count"] == 0
    assert cards["external_delivery_allowed_count"] == 0
    assert cards["approval_allowed_count"] == 0
    assert cards["execution_allowed_count"] == 0
    assert cards["safe_to_continue_action_receipt_cards"] is True

    for item in cards["action_receipt_card_items"]:
        assert item["action_receipt_card_id"].startswith("VSAAR-")
        assert item["action_suggestion_id"].startswith("VSASP-")
        assert item["review_card_id"].startswith("VSARB-")
        assert item["audit_event_card_id"].startswith("VSAE-")
        assert item["receipt_card_id"].startswith("VSARP-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["action_receipt_status"] == "PREVIEW_ONLY_NOT_OFFICIAL_NOT_FINAL_NOT_CLOSED"
        assert item["metadata_only"] is True
        assert item["private_action_receipt_preview_only"] is True
        assert item["action_receipt_preview_created"] is True
        assert item["official_action_receipt_claimed"] is False
        assert item["action_receipt_finalized"] is False
        assert item["action_receipt_closed"] is False
        assert item["action_approved"] is False
        assert item["action_executed"] is False
        assert item["blocked_action_receipt"] is True
        assert item["no_execution_receipt"] is True
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["execution_allowed"] is False


def test_gp049_blocked_action_receipt_labels_block_sensitive_paths():
    labels = get_storage_audit_blocked_action_receipt_labels()["blocked_action_receipt_labels"]

    assert labels["blocked_action_receipt_label_count"] == 35
    assert labels["blocked_action_receipt_count"] == 35
    assert labels["blocks_official_action_receipt_count"] == 35
    assert labels["blocks_action_receipt_finalize_count"] == 35
    assert labels["blocks_action_receipt_close_count"] == 35
    assert labels["blocks_action_approval_count"] == 35
    assert labels["blocks_action_execution_count"] == 35
    assert labels["blocks_execution_count"] == 35
    assert labels["blocks_provider_read_count"] == 35
    assert labels["blocks_object_body_view_count"] == 35
    assert labels["blocks_export_count"] == 35
    assert labels["blocks_external_delivery_count"] == 35
    assert labels["blocks_portal_access_count"] == 35
    assert labels["blocks_public_proof_count"] == 35
    assert labels["blocks_financing_decision_count"] == 35
    assert labels["blocks_legal_advice_count"] == 35
    assert labels["tower_authority_required_count"] == 35
    assert labels["official_action_receipt_claimed_count"] == 0
    assert labels["action_receipt_finalized_count"] == 0
    assert labels["action_receipt_closed_count"] == 0
    assert labels["action_approved_count"] == 0
    assert labels["action_executed_count"] == 0
    assert labels["safe_to_continue_blocked_action_receipt_labels"] is True

    for item in labels["blocked_action_receipt_label_items"]:
        assert item["blocked_action_receipt_label_id"].startswith("VSABARL-")
        assert item["action_receipt_card_id"].startswith("VSAAR-")
        assert item["action_suggestion_id"].startswith("VSASP-")
        assert item["blocked_receipt_label"] == "BLOCKED_ACTION_RECEIPT_PREVIEW_ONLY"
        assert item["metadata_only"] is True
        assert item["blocked_action_receipt"] is True
        assert item["blocks_official_action_receipt"] is True
        assert item["blocks_action_receipt_finalize"] is True
        assert item["blocks_action_receipt_close"] is True
        assert item["blocks_action_approval"] is True
        assert item["blocks_action_execution"] is True
        assert item["blocks_execution"] is True
        assert item["blocks_provider_read"] is True
        assert item["blocks_object_body_view"] is True
        assert item["action_approved"] is False
        assert item["action_executed"] is False


def test_gp049_tower_action_gate_receipts_required_not_granted():
    receipts = get_storage_tower_action_gate_receipts()["tower_action_gate_receipts"]

    assert receipts["tower_action_gate_receipt_count"] == 210
    assert receipts["receipt_snapshot_created_count"] == 210
    assert receipts["required_count"] == 210
    assert receipts["granted_count"] == 0
    assert receipts["vault_override_allowed_count"] == 0
    assert receipts["official_action_receipt_claimed_count"] == 0
    assert receipts["action_receipt_finalized_count"] == 0
    assert receipts["action_receipt_closed_count"] == 0
    assert receipts["action_approved_count"] == 0
    assert receipts["action_executed_count"] == 0
    assert receipts["audit_review_approved_count"] == 0
    assert receipts["official_audit_log_written_count"] == 0
    assert receipts["immutable_audit_written_count"] == 0
    assert receipts["access_granted_count"] == 0
    assert receipts["provider_read_enabled_count"] == 0
    assert receipts["object_body_view_enabled_count"] == 0
    assert receipts["export_allowed_count"] == 0
    assert receipts["external_delivery_allowed_count"] == 0
    assert receipts["execution_allowed_count"] == 0
    assert receipts["safe_to_continue_tower_action_gate_receipts"] is True

    for item in receipts["tower_action_gate_receipt_items"]:
        assert item["tower_action_gate_receipt_id"].startswith("VSATAGR-")
        assert item["tower_action_gate_id"].startswith("VSATAG-")
        assert item["action_suggestion_id"].startswith("VSASP-")
        assert item["gate_receipt_status"] == "REQUIRED_NOT_GRANTED_RECEIPT_PREVIEW"
        assert item["metadata_only"] is True
        assert item["required"] is True
        assert item["granted"] is False
        assert item["vault_can_override"] is False
        assert item["action_approved"] is False
        assert item["action_executed"] is False
        assert item["execution_allowed"] is False


def test_gp049_followup_receipt_placeholders_empty_unconfirmed():
    placeholders = get_storage_audit_followup_receipt_placeholders()["followup_receipt_placeholders"]

    assert placeholders["followup_receipt_placeholder_count"] == 140
    assert placeholders["receipt_snapshot_created_count"] == 140
    assert placeholders["followup_required_count"] == 140
    assert placeholders["followup_present_count"] == 0
    assert placeholders["reviewer_bound_count"] == 0
    assert placeholders["reviewer_confirmed_count"] == 0
    assert placeholders["official_action_receipt_claimed_count"] == 0
    assert placeholders["action_receipt_finalized_count"] == 0
    assert placeholders["action_receipt_closed_count"] == 0
    assert placeholders["action_approved_count"] == 0
    assert placeholders["action_executed_count"] == 0
    assert placeholders["official_audit_log_written_count"] == 0
    assert placeholders["immutable_audit_written_count"] == 0
    assert placeholders["access_granted_count"] == 0
    assert placeholders["provider_read_enabled_count"] == 0
    assert placeholders["object_body_view_enabled_count"] == 0
    assert placeholders["execution_allowed_count"] == 0
    assert placeholders["safe_to_continue_followup_receipt_placeholders"] is True

    for item in placeholders["followup_receipt_placeholder_items"]:
        assert item["followup_receipt_placeholder_id"].startswith("VSARFR-")
        assert item["reviewer_followup_placeholder_id"].startswith("VSARFP-")
        assert item["action_suggestion_id"].startswith("VSASP-")
        assert item["receipt_placeholder_status"] == "EMPTY_NOT_REVIEWED_NOT_CONFIRMED"
        assert item["metadata_only"] is True
        assert item["followup_required"] is True
        assert item["followup_present"] is False
        assert item["reviewer_confirmed"] is False
        assert item["action_approved"] is False
        assert item["action_executed"] is False
        assert item["execution_allowed"] is False


def test_gp049_no_execution_receipts_active():
    receipts = get_storage_audit_no_execution_receipts()["no_execution_receipts"]

    assert receipts["no_execution_receipt_count"] == 35
    assert receipts["no_execution_enforced_count"] == 35
    assert receipts["official_action_receipt_claimed_count"] == 0
    assert receipts["action_receipt_finalized_count"] == 0
    assert receipts["action_receipt_closed_count"] == 0
    assert receipts["action_approved_count"] == 0
    assert receipts["action_executed_count"] == 0
    assert receipts["action_completed_count"] == 0
    assert receipts["action_closed_count"] == 0
    assert receipts["audit_review_approved_count"] == 0
    assert receipts["official_audit_log_written_count"] == 0
    assert receipts["immutable_audit_written_count"] == 0
    assert receipts["official_storage_receipt_claimed_count"] == 0
    assert receipts["storage_receipt_finalized_count"] == 0
    assert receipts["storage_receipt_closed_count"] == 0
    assert receipts["access_granted_count"] == 0
    assert receipts["decision_granted_count"] == 0
    assert receipts["provider_read_enabled_count"] == 0
    assert receipts["provider_write_enabled_count"] == 0
    assert receipts["object_body_view_enabled_count"] == 0
    assert receipts["object_body_available_count"] == 0
    assert receipts["file_body_persisted_count"] == 0
    assert receipts["direct_upload_enabled_count"] == 0
    assert receipts["external_delivery_allowed_count"] == 0
    assert receipts["export_allowed_count"] == 0
    assert receipts["portal_access_allowed_count"] == 0
    assert receipts["public_proof_allowed_count"] == 0
    assert receipts["financing_decision_allowed_count"] == 0
    assert receipts["legal_advice_allowed_count"] == 0
    assert receipts["execution_allowed_count"] == 0
    assert receipts["vault_override_allowed_count"] == 0
    assert receipts["tower_authority_required_count"] == 35
    assert receipts["safe_to_continue_no_execution_receipts"] is True

    for item in receipts["no_execution_receipt_items"]:
        assert item["no_execution_receipt_id"].startswith("VSANER-")
        assert item["no_execution_enforcement_id"].startswith("VSANEE-")
        assert item["action_suggestion_id"].startswith("VSASP-")
        assert item["no_execution_receipt_status"] == "NO_EXECUTION_RECEIPT_PREVIEW_ACTIVE"
        assert item["metadata_only"] is True
        assert item["no_execution_receipt"] is True
        assert item["no_execution_enforced"] is True
        assert item["action_approved"] is False
        assert item["action_executed"] is False
        assert item["execution_allowed"] is False
        assert item["vault_can_override"] is False


def test_gp049_next_step_carries_forward_to_gp050_not_clouds():
    next_step = get_storage_audit_action_receipt_next_step()["next_step"]

    assert next_step["next_step_count"] == 3
    assert next_step["ready_for_gp050_count"] == 3
    assert next_step["action_receipt_card_count"] == 35
    assert next_step["blocked_action_receipt_label_count"] == 35
    assert next_step["tower_action_gate_receipt_count"] == 210
    assert next_step["followup_receipt_placeholder_count"] == 140
    assert next_step["no_execution_receipt_count"] == 35
    assert next_step["safe_to_continue_to_gp050"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False
    assert next_step["recommended_next_pack"] == "VAULT_GP050"
    assert next_step["recommended_next_pack_title"] == "Next Product Depth Readiness Checkpoint"

    note = next_step["owner_notebook_note"].lower()
    assert "archive vault — next product depth layer" in note
    assert "gp050 should close gp041-gp050" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "action receipt previews metadata-only" in rules
    assert "not official" in rules
    assert "no official action receipt claim" in rules
    assert "no finalized action receipt claim" in rules
    assert "no action execution claim" in rules
    assert "safe to continue, not vault done" in rules

    for item in next_step["next_step_items"]:
        assert item["next_step_id"].startswith("VSAARNX-")
        assert item["target_pack"] == "VAULT_GP050"
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False


def test_gp049_routes_and_counts_declared():
    home = get_storage_audit_action_receipt_preview_home()
    routes = home["action_receipt_routes"]
    counts = home["action_receipt_counts"]

    assert routes["section_header"] == "Archive Vault — Next Product Depth Layer"
    assert routes["section_range"] == "GP041-GP050"
    assert routes["route"] == "/vault/storage-audit-action-receipt-preview"
    assert routes["json_route"] == "/vault/storage-audit-action-receipt-preview.json"
    assert routes["action_receipt_cards_route"] == "/vault/storage-audit-action-receipt-cards.json"
    assert routes["blocked_action_receipt_labels_route"] == "/vault/storage-audit-blocked-action-receipt-labels.json"
    assert routes["tower_action_gate_receipts_route"] == "/vault/storage-tower-action-gate-receipts.json"
    assert routes["followup_receipt_placeholders_route"] == "/vault/storage-audit-followup-receipt-placeholders.json"
    assert routes["no_execution_receipts_route"] == "/vault/storage-audit-no-execution-receipts.json"
    assert routes["next_step_route"] == "/vault/storage-audit-action-receipt-next-step.json"
    assert routes["gp049_status_route"] == "/vault/gp049-status.json"

    assert counts["source_action_suggestion_count"] == 35
    assert counts["action_receipt_card_count"] == 35
    assert counts["action_receipt_preview_type_count"] == 5
    assert counts["blocked_action_receipt_label_count"] == 35
    assert counts["tower_action_gate_receipt_count"] == 210
    assert counts["followup_receipt_placeholder_count"] == 140
    assert counts["no_execution_receipt_count"] == 35
    assert counts["official_action_receipt_created_count"] == 0
    assert counts["official_action_receipt_claimed_count"] == 0
    assert counts["finalized_action_receipt_count"] == 0
    assert counts["closed_action_receipt_count"] == 0
    assert counts["action_approved_count"] == 0
    assert counts["action_executed_count"] == 0
    assert counts["official_audit_log_written_count"] == 0
    assert counts["immutable_audit_write_count"] == 0
    assert counts["access_request_granted_count"] == 0
    assert counts["decision_granted_count"] == 0
    assert counts["provider_read_enabled_count"] == 0
    assert counts["object_body_view_enabled_count"] == 0
    assert counts["external_delivery_allowed_count"] == 0
    assert counts["packet_export_allowed_count"] == 0
    assert counts["execution_allowed_count"] == 0
    assert counts["metadata_only"] is True


def test_gp049_html_is_dark_and_has_no_white_background_tokens():
    html = render_storage_audit_action_receipt_preview_page()
    lowered = html.lower()

    assert "Vault Storage Audit Action Receipt Preview" in html
    assert "Archive Vault" in html
    assert "/vault/storage-audit-action-receipt-preview.json" in html
    assert "/vault/gp049-status.json" in html
    assert "Clouds parked" in html
    assert "No official receipt" in html
    assert "No receipt close" in html
    assert "No execution" in html

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


def test_gp049_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-audit-action-receipt-preview",
        "/vault/storage-audit-action-receipt-preview.json",
        "/vault/storage-audit-action-receipt-cards.json",
        "/vault/storage-audit-blocked-action-receipt-labels.json",
        "/vault/storage-tower-action-gate-receipts.json",
        "/vault/storage-audit-followup-receipt-placeholders.json",
        "/vault/storage-audit-no-execution-receipts.json",
        "/vault/storage-audit-action-receipt-next-step.json",
        "/vault/gp049-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp049_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-audit-action-receipt-preview",
        "/vault/storage-audit-action-receipt-preview.json",
        "/vault/storage-audit-action-receipt-cards.json",
        "/vault/storage-audit-blocked-action-receipt-labels.json",
        "/vault/storage-tower-action-gate-receipts.json",
        "/vault/storage-audit-followup-receipt-placeholders.json",
        "/vault/storage-audit-no-execution-receipts.json",
        "/vault/storage-audit-action-receipt-next-step.json",
        "/vault/gp049-status.json",
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
                assert b"Vault Storage Audit Action Receipt Preview" in response.data
