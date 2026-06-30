"""
Tests for VAULT GIANT PACK 044 — Storage Access Decision Queue
"""

from pathlib import Path

import pytest

from vault.storage_access_decision_queue_service import (
    get_gp044_status,
    get_storage_access_decision_cards,
    get_storage_access_decision_next_step,
    get_storage_access_decision_queue_home,
    get_storage_access_denial_reason_labels,
    get_storage_access_no_grant_enforcement,
    get_storage_access_owner_review_placeholders,
    get_storage_access_tower_approval_requirements,
    render_storage_access_decision_queue_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp044_status_ready_safe_continue_not_done():
    status = get_gp044_status()
    gp044 = status["gp044_status"]

    assert status["pack"]["id"] == "VAULT_GP044"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert status["pack"]["section_range"] == "GP041-GP050"

    assert gp044["ready"] is True
    assert gp044["section_id"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert gp044["section_title"] == "Archive Vault — Next Product Depth Layer"
    assert gp044["section_range"] == "GP041-GP050"
    assert gp044["storage_access_decision_queue_ready"] is True
    assert gp044["safe_to_continue_to_gp045"] is True
    assert gp044["vault_done"] is False
    assert gp044["foundation_status"] == "safe_to_continue_not_done"
    assert gp044["metadata_only_decision_queue"] is True
    assert gp044["private_queue_only"] is True
    assert gp044["decision_cards_ready"] is True
    assert gp044["access_request_submitted_count"] == 0
    assert gp044["access_request_approved_count"] == 0
    assert gp044["access_request_granted_count"] == 0
    assert gp044["decision_approved_count"] == 0
    assert gp044["decision_granted_count"] == 0
    assert gp044["access_denied_by_default"] is True
    assert gp044["no_grant_enforced"] is True
    assert gp044["provider_selected"] is False
    assert gp044["provider_configured"] is False
    assert gp044["provider_write_enabled"] is False
    assert gp044["provider_read_enabled"] is False
    assert gp044["provider_object_read_claimed"] is False
    assert gp044["object_body_view_enabled"] is False
    assert gp044["raw_file_body_storage_still_locked"] is True
    assert gp044["file_body_persisted_count"] == 0
    assert gp044["object_body_available_count"] == 0
    assert gp044["direct_upload_still_locked"] is True
    assert gp044["checksum_verification_not_claimed"] is True
    assert gp044["hash_verification_not_claimed"] is True
    assert gp044["external_delivery_still_locked"] is True
    assert gp044["packet_export_still_locked"] is True
    assert gp044["approval_disabled"] is True
    assert gp044["execution_engine_disabled"] is True
    assert gp044["clouds_status"] == "parked_do_not_continue_from_vault_gp044"
    assert gp044["next_pack"] == "VAULT_GP045_STORAGE_ACCESS_RECEIPT_PREVIEW"


def test_gp044_decision_truth_keeps_decisions_blocked_and_locked():
    status = get_gp044_status()
    truth = status["decision_truth"]

    assert truth["storage_access_decision_queue_ready"] is True
    assert truth["decision_cards_visible"] is True
    assert truth["tower_approval_requirements_visible"] is True
    assert truth["owner_review_placeholders_visible"] is True
    assert truth["denial_reason_labels_visible"] is True
    assert truth["no_grant_enforcement_visible"] is True
    assert truth["metadata_only"] is True
    assert truth["private_queue_only"] is True

    assert truth["decision_card_created_count"] == 7
    assert truth["decision_status_pending_count"] == 7
    assert truth["decision_status_blocked_count"] == 7
    assert truth["decision_status_denied_count"] == 7
    assert truth["access_request_submitted_count"] == 0
    assert truth["access_request_approved_count"] == 0
    assert truth["access_request_granted_count"] == 0
    assert truth["decision_approved_count"] == 0
    assert truth["decision_granted_count"] == 0
    assert truth["decision_released_count"] == 0
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
    assert truth["receipt_close_enabled"] is False
    assert truth["receipt_finalization_enabled"] is False
    assert truth["vault_done"] is False
    assert truth["clouds_should_continue"] is False
    assert truth["safe_to_continue_to_gp045"] is True


def test_gp044_connected_to_gp043():
    home = get_storage_access_decision_queue_home()

    assert home["gp043_connection"]["gp043_ready"] is True
    assert home["gp043_connection"]["gp043_safe_to_continue"] is True
    assert home["gp043_connection"]["gp043_vault_done"] is False
    assert home["gp043_connection"]["gp043_section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert home["gp043_connection"]["gp043_request_card_count"] == 7
    assert home["gp043_connection"]["gp043_tower_gate_count"] == 63
    assert home["gp043_connection"]["gp043_denied_label_count"] == 7
    assert home["gp043_connection"]["gp043_reason_field_count"] == 49


def test_gp044_tower_authority_and_vault_boundaries():
    status = get_gp044_status()
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
    assert tower["vault_owns_tower_permissions"] is False
    assert tower["vault_can_override_tower_storage_authority"] is False
    assert tower["vault_can_override_tower_visibility"] is False
    assert tower["vault_can_grant_storage_access"] is False
    assert tower["vault_can_approve_storage_access_decision"] is False

    assert vault["no_public_vault"] is True
    assert vault["direct_raw_upload_unlocked"] is False
    assert vault["permanent_file_body_storage_enabled"] is False
    assert vault["external_access_default"] == "denied"
    assert vault["storage_access_default"] == "denied_by_default"
    assert vault["decision_default"] == "blocked_denied_by_default"
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


def test_gp044_decision_cards_pending_blocked_denied():
    cards = get_storage_access_decision_cards()["decision_cards"]

    assert cards["decision_card_count"] == 7
    assert cards["pending_decision_count"] == 7
    assert cards["blocked_decision_count"] == 7
    assert cards["denied_decision_count"] == 7
    assert cards["decision_submitted_count"] == 0
    assert cards["decision_approved_count"] == 0
    assert cards["decision_granted_count"] == 0
    assert cards["access_request_submitted_count"] == 0
    assert cards["access_request_approved_count"] == 0
    assert cards["access_granted_count"] == 0
    assert cards["no_grant_enforced_count"] == 7
    assert cards["tower_approval_required_count"] == 7
    assert cards["tower_approval_granted_count"] == 0
    assert cards["owner_review_required_count"] == 7
    assert cards["owner_reviewed_count"] == 0
    assert cards["owner_confirmed_count"] == 0
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
    assert cards["safe_to_continue_decision_cards"] is True

    scopes = {item["scope"] for item in cards["decision_card_items"]}
    assert scopes == {
        "document_intake",
        "attachment_registry",
        "requirement_match",
        "evidence_binder",
        "packet_workspace",
        "controlled_packet_assembly",
        "receipt_chain",
    }

    for item in cards["decision_card_items"]:
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["object_key_contract_id"].startswith("VSOK-")
        assert item["checksum_placeholder_id"].startswith("VSCHK-")
        assert item["decision_status"] == "BLOCKED_DENIED_BY_DEFAULT_TOWER_REVIEW_REQUIRED"
        assert item["queue_label"] == "Pending decision — blocked and denied by default"
        assert item["metadata_only"] is True
        assert item["private_queue_only"] is True
        assert item["pending_decision"] is True
        assert item["blocked_decision"] is True
        assert item["denied_decision"] is True
        assert item["decision_submitted"] is False
        assert item["decision_approved"] is False
        assert item["decision_granted"] is False
        assert item["access_request_submitted"] is False
        assert item["access_request_approved"] is False
        assert item["access_granted"] is False
        assert item["no_grant_enforced"] is True
        assert item["tower_approval_required"] is True
        assert item["tower_approval_granted"] is False
        assert item["owner_review_required"] is True
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["object_body_available"] is False
        assert item["file_body_persisted"] is False
        assert item["raw_file_body_storage_enabled"] is False
        assert item["direct_upload_enabled"] is False
        assert item["checksum_verified"] is False
        assert item["hash_verified"] is False
        assert item["export_allowed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["approval_allowed"] is False
        assert item["execution_allowed"] is False


def test_gp044_tower_approval_requirements_required_not_granted():
    req = get_storage_access_tower_approval_requirements()["tower_requirements"]

    assert req["tower_requirement_count"] == 56
    assert req["tower_requirement_type_count"] == 8
    assert req["decision_card_count"] == 7
    assert req["required_count"] == 56
    assert req["granted_count"] == 0
    assert req["vault_override_allowed_count"] == 0
    assert req["decision_approved_count"] == 0
    assert req["decision_granted_count"] == 0
    assert req["access_granted_count"] == 0
    assert req["provider_read_enabled_count"] == 0
    assert req["object_body_view_enabled_count"] == 0
    assert req["export_allowed_count"] == 0
    assert req["external_delivery_allowed_count"] == 0
    assert req["tower_authority_preserved"] is True
    assert req["safe_to_continue_tower_requirements"] is True

    names = {item["requirement_name"] for item in req["tower_requirement_items"]}
    assert "identity_verified" in names
    assert "permission_granted" in names
    assert "clearance_granted" in names
    assert "step_up_completed" in names
    assert "storage_access_authorized" in names
    assert "audit_receipt_ready" in names

    for item in req["tower_requirement_items"]:
        assert item["tower_requirement_id"].startswith("VSATR-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["requirement_status"] == "REQUIRED_NOT_GRANTED"
        assert item["metadata_only"] is True
        assert item["required"] is True
        assert item["granted"] is False
        assert item["vault_can_override"] is False
        assert item["decision_approved"] is False
        assert item["decision_granted"] is False
        assert item["access_granted"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["export_allowed"] is False
        assert item["external_delivery_allowed"] is False


def test_gp044_owner_review_placeholders_empty_not_reviewed():
    placeholders = get_storage_access_owner_review_placeholders()["owner_review_placeholders"]

    assert placeholders["owner_review_placeholder_count"] == 28
    assert placeholders["owner_review_field_type_count"] == 4
    assert placeholders["decision_card_count"] == 7
    assert placeholders["owner_review_required_count"] == 28
    assert placeholders["owner_reviewed_count"] == 0
    assert placeholders["owner_confirmed_count"] == 0
    assert placeholders["field_value_present_count"] == 0
    assert placeholders["decision_approved_count"] == 0
    assert placeholders["decision_granted_count"] == 0
    assert placeholders["access_granted_count"] == 0
    assert placeholders["provider_read_enabled_count"] == 0
    assert placeholders["object_body_view_enabled_count"] == 0
    assert placeholders["external_delivery_allowed_count"] == 0
    assert placeholders["export_allowed_count"] == 0
    assert placeholders["safe_to_continue_owner_review_placeholders"] is True

    fields = {item["owner_review_field"] for item in placeholders["owner_review_placeholder_items"]}
    assert fields == {
        "owner_review_note",
        "owner_business_reason",
        "owner_visibility_scope",
        "owner_risk_acknowledgment",
    }

    for item in placeholders["owner_review_placeholder_items"]:
        assert item["owner_review_placeholder_id"].startswith("VSAOR-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["placeholder_status"] == "EMPTY_NOT_REVIEWED_NOT_CONFIRMED"
        assert item["metadata_only"] is True
        assert item["owner_review_required"] is True
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["field_value_present"] is False
        assert item["decision_approved"] is False
        assert item["decision_granted"] is False
        assert item["access_granted"] is False


def test_gp044_denial_reason_labels_block_everything():
    labels = get_storage_access_denial_reason_labels()["denial_reason_labels"]

    assert labels["denial_reason_label_count"] == 49
    assert labels["denial_reason_type_count"] == 7
    assert labels["decision_card_count"] == 7
    assert labels["denied_by_default_count"] == 49
    assert labels["blocks_approval_count"] == 49
    assert labels["blocks_access_grant_count"] == 49
    assert labels["blocks_provider_read_count"] == 49
    assert labels["blocks_object_body_view_count"] == 49
    assert labels["blocks_export_count"] == 49
    assert labels["blocks_external_delivery_count"] == 49
    assert labels["blocks_portal_access_count"] == 49
    assert labels["blocks_execution_count"] == 49
    assert labels["owner_resolvable_now_count"] == 0
    assert labels["tower_authorization_required_count"] == 49
    assert labels["safe_to_continue_denial_reason_labels"] is True

    reasons = {item["denial_reason"] for item in labels["denial_reason_label_items"]}
    assert reasons == {
        "request_not_submitted",
        "tower_clearance_missing",
        "tower_step_up_missing",
        "storage_access_authorization_missing",
        "provider_read_locked",
        "object_body_view_locked",
        "export_locked",
    }

    for item in labels["denial_reason_label_items"]:
        assert item["denial_reason_label_id"].startswith("VSADRL-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["denial_status"] == "ACTIVE_DENIAL_REASON"
        assert item["metadata_only"] is True
        assert item["denied_by_default"] is True
        assert item["blocks_approval"] is True
        assert item["blocks_access_grant"] is True
        assert item["blocks_provider_read"] is True
        assert item["blocks_object_body_view"] is True
        assert item["blocks_export"] is True
        assert item["blocks_external_delivery"] is True
        assert item["blocks_portal_access"] is True
        assert item["blocks_execution"] is True
        assert item["owner_resolvable_now"] is False
        assert item["tower_authorization_required"] is True


def test_gp044_no_grant_enforcement_records_lock_access():
    enforcement = get_storage_access_no_grant_enforcement()["no_grant_enforcement"]

    assert enforcement["no_grant_enforcement_count"] == 7
    assert enforcement["no_grant_enforced_count"] == 7
    assert enforcement["access_granted_count"] == 0
    assert enforcement["decision_granted_count"] == 0
    assert enforcement["provider_read_enabled_count"] == 0
    assert enforcement["provider_write_enabled_count"] == 0
    assert enforcement["object_body_view_enabled_count"] == 0
    assert enforcement["object_body_available_count"] == 0
    assert enforcement["file_body_persisted_count"] == 0
    assert enforcement["direct_upload_enabled_count"] == 0
    assert enforcement["external_delivery_allowed_count"] == 0
    assert enforcement["export_allowed_count"] == 0
    assert enforcement["portal_access_allowed_count"] == 0
    assert enforcement["public_proof_allowed_count"] == 0
    assert enforcement["execution_allowed_count"] == 0
    assert enforcement["vault_override_allowed_count"] == 0
    assert enforcement["tower_authorization_required_count"] == 7
    assert enforcement["safe_to_continue_no_grant_enforcement"] is True

    for item in enforcement["no_grant_enforcement_items"]:
        assert item["no_grant_enforcement_id"].startswith("VSANGE-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["enforcement_status"] == "NO_GRANT_ENFORCED"
        assert item["metadata_only"] is True
        assert item["no_grant_enforced"] is True
        assert item["access_granted"] is False
        assert item["decision_granted"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["object_body_available"] is False
        assert item["file_body_persisted"] is False
        assert item["direct_upload_enabled"] is False
        assert item["external_delivery_allowed"] is False
        assert item["export_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["public_proof_allowed"] is False
        assert item["execution_allowed"] is False
        assert item["vault_can_override"] is False
        assert item["tower_authorization_required"] is True


def test_gp044_next_step_carries_forward_to_gp045_not_clouds():
    next_step = get_storage_access_decision_next_step()["next_step"]

    assert next_step["next_step_count"] == 3
    assert next_step["ready_for_gp045_count"] == 3
    assert next_step["decision_card_count"] == 7
    assert next_step["tower_requirement_count"] == 56
    assert next_step["owner_review_placeholder_count"] == 28
    assert next_step["denial_reason_label_count"] == 49
    assert next_step["no_grant_enforcement_count"] == 7
    assert next_step["safe_to_continue_to_gp045"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False
    assert next_step["recommended_next_pack"] == "VAULT_GP045"
    assert next_step["recommended_next_pack_title"] == "Storage Access Receipt Preview"

    note = next_step["owner_notebook_note"].lower()
    assert "archive vault — next product depth layer" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "decision queue metadata-only" in rules
    assert "no-grant enforcement active" in rules
    assert "tower approval requirements required and ungranted" in rules
    assert "object body view locked" in rules
    assert "provider read/write locked" in rules
    assert "safe to continue, not vault done" in rules

    for item in next_step["next_step_items"]:
        assert item["next_step_id"].startswith("VSADQNX-")
        assert item["target_pack"] == "VAULT_GP045"
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False


def test_gp044_routes_and_counts_declared():
    home = get_storage_access_decision_queue_home()
    routes = home["decision_routes"]
    counts = home["decision_counts"]

    assert routes["section_header"] == "Archive Vault — Next Product Depth Layer"
    assert routes["section_range"] == "GP041-GP050"
    assert routes["route"] == "/vault/storage-access-decision-queue"
    assert routes["json_route"] == "/vault/storage-access-decision-queue.json"
    assert routes["decision_cards_route"] == "/vault/storage-access-decision-cards.json"
    assert routes["tower_requirements_route"] == "/vault/storage-access-tower-approval-requirements.json"
    assert routes["owner_review_placeholders_route"] == "/vault/storage-access-owner-review-placeholders.json"
    assert routes["denial_reason_labels_route"] == "/vault/storage-access-denial-reason-labels.json"
    assert routes["no_grant_enforcement_route"] == "/vault/storage-access-no-grant-enforcement.json"
    assert routes["next_step_route"] == "/vault/storage-access-decision-next-step.json"
    assert routes["gp044_status_route"] == "/vault/gp044-status.json"

    assert counts["decision_card_count"] == 7
    assert counts["pending_decision_count"] == 7
    assert counts["blocked_decision_count"] == 7
    assert counts["denied_decision_count"] == 7
    assert counts["tower_requirement_count"] == 56
    assert counts["owner_review_placeholder_count"] == 28
    assert counts["denial_reason_label_count"] == 49
    assert counts["no_grant_enforcement_count"] == 7
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


def test_gp044_html_is_dark_and_has_no_white_background_tokens():
    html = render_storage_access_decision_queue_page()
    lowered = html.lower()

    assert "Vault Storage Access Decision Queue" in html
    assert "Archive Vault" in html
    assert "/vault/storage-access-decision-queue.json" in html
    assert "/vault/gp044-status.json" in html
    assert "Clouds parked" in html
    assert "No grant enforced" in html
    assert "No access approval" in html
    assert "No provider read/write" in html

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


def test_gp044_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-access-decision-queue",
        "/vault/storage-access-decision-queue.json",
        "/vault/storage-access-decision-cards.json",
        "/vault/storage-access-tower-approval-requirements.json",
        "/vault/storage-access-owner-review-placeholders.json",
        "/vault/storage-access-denial-reason-labels.json",
        "/vault/storage-access-no-grant-enforcement.json",
        "/vault/storage-access-decision-next-step.json",
        "/vault/gp044-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp044_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-access-decision-queue",
        "/vault/storage-access-decision-queue.json",
        "/vault/storage-access-decision-cards.json",
        "/vault/storage-access-tower-approval-requirements.json",
        "/vault/storage-access-owner-review-placeholders.json",
        "/vault/storage-access-denial-reason-labels.json",
        "/vault/storage-access-no-grant-enforcement.json",
        "/vault/storage-access-decision-next-step.json",
        "/vault/gp044-status.json",
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
                assert b"Vault Storage Access Decision Queue" in response.data
