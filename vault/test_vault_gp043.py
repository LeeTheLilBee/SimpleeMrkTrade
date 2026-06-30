"""
Tests for VAULT GIANT PACK 043 — Storage Access Request Preview
"""

from pathlib import Path

import pytest

from vault.storage_access_request_preview_service import (
    get_gp043_status,
    get_storage_access_denied_labels,
    get_storage_access_next_step,
    get_storage_access_reason_fields,
    get_storage_access_request_cards,
    get_storage_access_request_home,
    get_storage_access_requester_placeholders,
    get_storage_access_tower_gates,
    get_storage_access_visibility_limits,
    render_storage_access_request_preview_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp043_status_ready_safe_continue_not_done():
    status = get_gp043_status()
    gp043 = status["gp043_status"]

    assert status["pack"]["id"] == "VAULT_GP043"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert status["pack"]["section_range"] == "GP041-GP050"

    assert gp043["ready"] is True
    assert gp043["section_id"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert gp043["section_title"] == "Archive Vault — Next Product Depth Layer"
    assert gp043["section_range"] == "GP041-GP050"
    assert gp043["storage_access_request_preview_ready"] is True
    assert gp043["safe_to_continue_to_gp044"] is True
    assert gp043["vault_done"] is False
    assert gp043["foundation_status"] == "safe_to_continue_not_done"
    assert gp043["metadata_only_access_preview"] is True
    assert gp043["private_preview_only"] is True
    assert gp043["access_request_submitted_count"] == 0
    assert gp043["access_request_approved_count"] == 0
    assert gp043["access_request_granted_count"] == 0
    assert gp043["access_denied_by_default"] is True
    assert gp043["provider_selected"] is False
    assert gp043["provider_configured"] is False
    assert gp043["provider_write_enabled"] is False
    assert gp043["provider_read_enabled"] is False
    assert gp043["provider_object_read_claimed"] is False
    assert gp043["object_body_view_enabled"] is False
    assert gp043["raw_file_body_storage_still_locked"] is True
    assert gp043["file_body_persisted_count"] == 0
    assert gp043["object_body_available_count"] == 0
    assert gp043["direct_upload_still_locked"] is True
    assert gp043["checksum_verification_not_claimed"] is True
    assert gp043["hash_verification_not_claimed"] is True
    assert gp043["external_delivery_still_locked"] is True
    assert gp043["packet_export_still_locked"] is True
    assert gp043["approval_disabled"] is True
    assert gp043["execution_engine_disabled"] is True
    assert gp043["clouds_status"] == "parked_do_not_continue_from_vault_gp043"
    assert gp043["next_pack"] == "VAULT_GP044_STORAGE_ACCESS_DECISION_QUEUE"


def test_gp043_access_truth_keeps_access_denied_and_locked():
    status = get_gp043_status()
    truth = status["access_truth"]

    assert truth["storage_access_request_preview_ready"] is True
    assert truth["request_cards_visible"] is True
    assert truth["requester_placeholders_visible"] is True
    assert truth["tower_clearance_step_up_gates_visible"] is True
    assert truth["object_visibility_limits_visible"] is True
    assert truth["denied_by_default_labels_visible"] is True
    assert truth["access_reason_fields_visible"] is True
    assert truth["metadata_only"] is True
    assert truth["private_preview_only"] is True

    assert truth["access_request_created_count"] == 7
    assert truth["access_request_submitted_count"] == 0
    assert truth["access_request_approved_count"] == 0
    assert truth["access_request_granted_count"] == 0
    assert truth["access_request_denied_by_default_count"] == 7

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
    assert truth["safe_to_continue_to_gp044"] is True


def test_gp043_connected_to_gp042():
    home = get_storage_access_request_home()

    assert home["gp042_connection"]["gp042_ready"] is True
    assert home["gp042_connection"]["gp042_safe_to_continue"] is True
    assert home["gp042_connection"]["gp042_vault_done"] is False
    assert home["gp042_connection"]["gp042_section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert home["gp042_connection"]["gp042_inventory_row_count"] == 7
    assert home["gp042_connection"]["gp042_provider_link_count"] == 28
    assert home["gp042_connection"]["gp042_missing_warning_count"] == 35
    assert home["gp042_connection"]["gp042_tower_visibility_gate_count"] == 49


def test_gp043_tower_authority_and_vault_boundaries():
    status = get_gp043_status()
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
    assert tower["vault_owns_tower_permissions"] is False
    assert tower["vault_can_override_tower_storage_authority"] is False
    assert tower["vault_can_override_tower_visibility"] is False
    assert tower["vault_can_grant_storage_access"] is False

    assert vault["no_public_vault"] is True
    assert vault["direct_raw_upload_unlocked"] is False
    assert vault["permanent_file_body_storage_enabled"] is False
    assert vault["external_access_default"] == "denied"
    assert vault["storage_access_default"] == "denied_by_default"
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


def test_gp043_request_cards_are_denied_by_default():
    cards = get_storage_access_request_cards()["request_cards"]

    assert cards["request_card_count"] == 7
    assert cards["request_created_count"] == 7
    assert cards["request_submitted_count"] == 0
    assert cards["request_approved_count"] == 0
    assert cards["access_granted_count"] == 0
    assert cards["access_denied_by_default_count"] == 7
    assert cards["requester_placeholder_required_count"] == 7
    assert cards["requester_bound_count"] == 0
    assert cards["tower_clearance_required_count"] == 7
    assert cards["tower_clearance_granted_count"] == 0
    assert cards["tower_step_up_required_count"] == 7
    assert cards["tower_step_up_granted_count"] == 0
    assert cards["tower_storage_access_authorization_required_count"] == 7
    assert cards["tower_storage_access_authorized_count"] == 0
    assert cards["owner_review_required_count"] == 7
    assert cards["owner_reviewed_count"] == 0
    assert cards["owner_confirmed_count"] == 0
    assert cards["provider_read_enabled_count"] == 0
    assert cards["provider_write_enabled_count"] == 0
    assert cards["provider_object_read_claimed_count"] == 0
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
    assert cards["safe_to_continue_request_cards"] is True

    scopes = {item["scope"] for item in cards["request_card_items"]}
    assert scopes == {
        "document_intake",
        "attachment_registry",
        "requirement_match",
        "evidence_binder",
        "packet_workspace",
        "controlled_packet_assembly",
        "receipt_chain",
    }

    for item in cards["request_card_items"]:
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["object_key_contract_id"].startswith("VSOK-")
        assert item["checksum_placeholder_id"].startswith("VSCHK-")
        assert item["request_status"] == "PREVIEW_ONLY_DENIED_BY_DEFAULT"
        assert item["access_status_label"] == "ACCESS_NOT_REQUESTED_DENIED_BY_DEFAULT"
        assert item["metadata_only"] is True
        assert item["private_preview_only"] is True
        assert item["request_created"] is True
        assert item["request_submitted"] is False
        assert item["request_approved"] is False
        assert item["access_granted"] is False
        assert item["access_denied_by_default"] is True
        assert item["tower_clearance_required"] is True
        assert item["tower_clearance_granted"] is False
        assert item["tower_step_up_required"] is True
        assert item["tower_step_up_granted"] is False
        assert item["tower_storage_access_authorization_required"] is True
        assert item["tower_storage_access_authorized"] is False
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
        assert item["safe_to_continue_to_gp044"] is True


def test_gp043_requester_placeholders_unbound_and_unauthorized():
    placeholders = get_storage_access_requester_placeholders()["requester_placeholders"]

    assert placeholders["requester_placeholder_count"] == 28
    assert placeholders["request_card_count"] == 7
    assert placeholders["requester_role_count"] == 4
    assert placeholders["requester_bound_count"] == 0
    assert placeholders["identity_verified_count"] == 0
    assert placeholders["permission_granted_count"] == 0
    assert placeholders["tower_clearance_granted_count"] == 0
    assert placeholders["tower_step_up_granted_count"] == 0
    assert placeholders["access_authorized_count"] == 0
    assert placeholders["external_party_placeholder_count"] == 7
    assert placeholders["external_access_allowed_count"] == 0
    assert placeholders["portal_access_allowed_count"] == 0
    assert placeholders["object_body_view_enabled_count"] == 0
    assert placeholders["provider_read_enabled_count"] == 0
    assert placeholders["safe_to_continue_requester_placeholders"] is True

    roles = {item["requester_role"] for item in placeholders["requester_placeholder_items"]}
    assert roles == {"owner", "tower_admin", "vault_reviewer", "external_party_placeholder"}

    for item in placeholders["requester_placeholder_items"]:
        assert item["requester_placeholder_id"].startswith("VSARP-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["requester_status"] == "PLACEHOLDER_NOT_BOUND_NOT_AUTHORIZED"
        assert item["metadata_only"] is True
        assert item["requester_bound"] is False
        assert item["identity_verified"] is False
        assert item["permission_granted"] is False
        assert item["tower_clearance_granted"] is False
        assert item["tower_step_up_granted"] is False
        assert item["access_authorized"] is False
        assert item["external_access_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["object_body_view_enabled"] is False
        assert item["provider_read_enabled"] is False
        assert item["safe_to_continue_to_gp044"] is True


def test_gp043_tower_gates_required_not_granted():
    gates = get_storage_access_tower_gates()["tower_gates"]

    assert gates["tower_gate_count"] == 63
    assert gates["tower_gate_type_count"] == 9
    assert gates["request_card_count"] == 7
    assert gates["required_gate_count"] == 63
    assert gates["granted_gate_count"] == 0
    assert gates["vault_override_allowed_count"] == 0
    assert gates["access_request_submitted_count"] == 0
    assert gates["access_request_approved_count"] == 0
    assert gates["access_granted_count"] == 0
    assert gates["provider_read_enabled_count"] == 0
    assert gates["object_body_view_enabled_count"] == 0
    assert gates["export_allowed_count"] == 0
    assert gates["external_access_allowed_count"] == 0
    assert gates["tower_authority_preserved"] is True
    assert gates["safe_to_continue_tower_gates"] is True

    gate_names = {item["gate_name"] for item in gates["tower_gate_items"]}
    assert "clearance_required" in gate_names
    assert "step_up_required" in gate_names
    assert "storage_access_authorization_required" in gate_names
    assert "export_lock_required" in gate_names
    assert "external_access_lock_required" in gate_names

    for item in gates["tower_gate_items"]:
        assert item["tower_access_gate_id"].startswith("VSATG-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["gate_status"] == "TOWER_REQUIRED_NOT_GRANTED"
        assert item["metadata_only"] is True
        assert item["required"] is True
        assert item["granted"] is False
        assert item["vault_can_override"] is False
        assert item["access_request_submitted"] is False
        assert item["access_request_approved"] is False
        assert item["access_granted"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["export_allowed"] is False
        assert item["external_access_allowed"] is False


def test_gp043_visibility_limits_keep_object_body_and_export_locked():
    limits = get_storage_access_visibility_limits()["visibility_limits"]

    assert limits["visibility_limit_count"] == 49
    assert limits["visibility_limit_type_count"] == 7
    assert limits["request_card_count"] == 7
    assert limits["active_limit_count"] == 49
    assert limits["owner_redacted_preview_allowed_count"] == 7
    assert limits["object_body_view_allowed_count"] == 0
    assert limits["raw_view_allowed_count"] == 0
    assert limits["sensitive_body_display_allowed_count"] == 0
    assert limits["export_allowed_count"] == 0
    assert limits["external_access_allowed_count"] == 0
    assert limits["portal_access_allowed_count"] == 0
    assert limits["vault_override_allowed_count"] == 0
    assert limits["safe_to_continue_visibility_limits"] is True

    names = {item["visibility_limit"] for item in limits["visibility_limit_items"]}
    assert names == {
        "metadata_only",
        "redacted_owner_preview_only",
        "no_object_body_view",
        "no_raw_view",
        "no_sensitive_body_display",
        "no_export_view",
        "no_external_access",
    }

    for item in limits["visibility_limit_items"]:
        assert item["visibility_limit_id"].startswith("VSAVL-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["limit_status"] == "ACTIVE_LIMIT"
        assert item["metadata_only"] is True
        assert item["limit_active"] is True
        assert item["object_body_view_allowed"] is False
        assert item["raw_view_allowed"] is False
        assert item["sensitive_body_display_allowed"] is False
        assert item["export_allowed"] is False
        assert item["external_access_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["vault_can_override"] is False


def test_gp043_denied_labels_denied_by_default():
    labels = get_storage_access_denied_labels()["denied_labels"]

    assert labels["denied_label_count"] == 7
    assert labels["denied_by_default_count"] == 7
    assert labels["access_request_submitted_count"] == 0
    assert labels["access_request_approved_count"] == 0
    assert labels["access_granted_count"] == 0
    assert labels["provider_read_enabled_count"] == 0
    assert labels["object_body_view_enabled_count"] == 0
    assert labels["external_access_allowed_count"] == 0
    assert labels["export_allowed_count"] == 0
    assert labels["portal_access_allowed_count"] == 0
    assert labels["execution_allowed_count"] == 0
    assert labels["safe_to_continue_denied_labels"] is True

    for item in labels["denied_label_items"]:
        assert item["denied_label_id"].startswith("VSADL-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["denied_label"] == "DENIED_BY_DEFAULT_TOWER_ACCESS_REQUIRED"
        assert item["owner_label"] == "Access denied by default — Tower clearance and step-up required"
        assert item["metadata_only"] is True
        assert item["denied_by_default"] is True
        assert item["access_request_submitted"] is False
        assert item["access_request_approved"] is False
        assert item["access_granted"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["external_access_allowed"] is False
        assert item["export_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["execution_allowed"] is False


def test_gp043_reason_fields_empty_not_submitted():
    fields = get_storage_access_reason_fields()["reason_fields"]

    assert fields["reason_field_count"] == 49
    assert fields["reason_field_type_count"] == 7
    assert fields["request_card_count"] == 7
    assert fields["field_required_before_submission_count"] == 49
    assert fields["field_value_present_count"] == 0
    assert fields["request_submitted_count"] == 0
    assert fields["request_approved_count"] == 0
    assert fields["access_granted_count"] == 0
    assert fields["tower_review_required_count"] == 49
    assert fields["owner_review_required_count"] == 49
    assert fields["external_delivery_allowed_count"] == 0
    assert fields["export_allowed_count"] == 0
    assert fields["execution_allowed_count"] == 0
    assert fields["safe_to_continue_reason_fields"] is True

    field_names = {item["field_name"] for item in fields["reason_field_items"]}
    assert field_names == {
        "request_reason",
        "business_lane",
        "linked_packet",
        "linked_requirement",
        "requested_visibility",
        "tower_clearance_reason",
        "owner_review_note",
    }

    for item in fields["reason_field_items"]:
        assert item["reason_field_id"].startswith("VSARF-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["field_status"] == "PLACEHOLDER_EMPTY_NOT_SUBMITTED"
        assert item["metadata_only"] is True
        assert item["field_required_before_submission"] is True
        assert item["field_value_present"] is False
        assert item["request_submitted"] is False
        assert item["request_approved"] is False
        assert item["access_granted"] is False
        assert item["tower_review_required"] is True
        assert item["owner_review_required"] is True
        assert item["external_delivery_allowed"] is False
        assert item["export_allowed"] is False
        assert item["execution_allowed"] is False


def test_gp043_next_step_carries_forward_to_gp044_not_clouds():
    next_step = get_storage_access_next_step()["next_step"]

    assert next_step["next_step_count"] == 3
    assert next_step["ready_for_gp044_count"] == 3
    assert next_step["request_card_count"] == 7
    assert next_step["requester_placeholder_count"] == 28
    assert next_step["tower_gate_count"] == 63
    assert next_step["visibility_limit_count"] == 49
    assert next_step["denied_label_count"] == 7
    assert next_step["reason_field_count"] == 49
    assert next_step["safe_to_continue_to_gp044"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False
    assert next_step["recommended_next_pack"] == "VAULT_GP044"
    assert next_step["recommended_next_pack_title"] == "Storage Access Decision Queue"

    note = next_step["owner_notebook_note"].lower()
    assert "archive vault — next product depth layer" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "access denied by default" in rules
    assert "tower clearance and step-up required" in rules
    assert "object body view locked" in rules
    assert "provider read/write locked" in rules
    assert "safe to continue, not vault done" in rules

    for item in next_step["next_step_items"]:
        assert item["next_step_id"].startswith("VSARNX-")
        assert item["target_pack"] == "VAULT_GP044"
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False


def test_gp043_routes_and_counts_declared():
    home = get_storage_access_request_home()
    routes = home["access_routes"]
    counts = home["access_counts"]

    assert routes["section_header"] == "Archive Vault — Next Product Depth Layer"
    assert routes["section_range"] == "GP041-GP050"
    assert routes["route"] == "/vault/storage-access-request"
    assert routes["json_route"] == "/vault/storage-access-request.json"
    assert routes["request_cards_route"] == "/vault/storage-access-request-cards.json"
    assert routes["requester_placeholders_route"] == "/vault/storage-access-requester-placeholders.json"
    assert routes["tower_gates_route"] == "/vault/storage-access-tower-gates.json"
    assert routes["visibility_limits_route"] == "/vault/storage-access-visibility-limits.json"
    assert routes["denied_labels_route"] == "/vault/storage-access-denied-labels.json"
    assert routes["reason_fields_route"] == "/vault/storage-access-reason-fields.json"
    assert routes["next_step_route"] == "/vault/storage-access-next-step.json"
    assert routes["gp043_status_route"] == "/vault/gp043-status.json"

    assert counts["request_card_count"] == 7
    assert counts["requester_placeholder_count"] == 28
    assert counts["tower_gate_count"] == 63
    assert counts["visibility_limit_count"] == 49
    assert counts["denied_label_count"] == 7
    assert counts["reason_field_count"] == 49
    assert counts["access_request_submitted_count"] == 0
    assert counts["access_request_approved_count"] == 0
    assert counts["access_request_granted_count"] == 0
    assert counts["access_request_denied_by_default_count"] == 7
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


def test_gp043_html_is_dark_and_has_no_white_background_tokens():
    html = render_storage_access_request_preview_page()
    lowered = html.lower()

    assert "Vault Storage Access Request Preview" in html
    assert "Archive Vault" in html
    assert "/vault/storage-access-request.json" in html
    assert "/vault/gp043-status.json" in html
    assert "Clouds parked" in html
    assert "No object body view" in html
    assert "No provider read/write" in html
    assert "Denied by default" in html

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


def test_gp043_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-access-request",
        "/vault/storage-access-request.json",
        "/vault/storage-access-request-cards.json",
        "/vault/storage-access-requester-placeholders.json",
        "/vault/storage-access-tower-gates.json",
        "/vault/storage-access-visibility-limits.json",
        "/vault/storage-access-denied-labels.json",
        "/vault/storage-access-reason-fields.json",
        "/vault/storage-access-next-step.json",
        "/vault/gp043-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp043_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-access-request",
        "/vault/storage-access-request.json",
        "/vault/storage-access-request-cards.json",
        "/vault/storage-access-requester-placeholders.json",
        "/vault/storage-access-tower-gates.json",
        "/vault/storage-access-visibility-limits.json",
        "/vault/storage-access-denied-labels.json",
        "/vault/storage-access-reason-fields.json",
        "/vault/storage-access-next-step.json",
        "/vault/gp043-status.json",
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
                assert b"Vault Storage Access Request Preview" in response.data
