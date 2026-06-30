"""
Tests for VAULT GIANT PACK 048 — Storage Audit Action Preview
"""

from pathlib import Path

import pytest

from vault.storage_audit_action_preview_service import (
    get_gp048_status,
    get_storage_audit_action_next_step,
    get_storage_audit_action_preview_home,
    get_storage_audit_action_suggestions,
    get_storage_audit_blocked_action_labels,
    get_storage_audit_no_execution_enforcement,
    get_storage_audit_reviewer_followup_placeholders,
    get_storage_tower_action_authority_gates,
    render_storage_audit_action_preview_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp048_status_ready_safe_continue_not_done():
    status = get_gp048_status()
    gp048 = status["gp048_status"]

    assert status["pack"]["id"] == "VAULT_GP048"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert status["pack"]["section_range"] == "GP041-GP050"

    assert gp048["ready"] is True
    assert gp048["section_id"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert gp048["section_title"] == "Archive Vault — Next Product Depth Layer"
    assert gp048["section_range"] == "GP041-GP050"
    assert gp048["storage_audit_action_preview_ready"] is True
    assert gp048["safe_to_continue_to_gp049"] is True
    assert gp048["vault_done"] is False
    assert gp048["foundation_status"] == "safe_to_continue_not_done"
    assert gp048["metadata_only_action_preview"] is True
    assert gp048["private_action_preview_only"] is True
    assert gp048["action_suggestions_ready"] is True
    assert gp048["action_approved_count"] == 0
    assert gp048["action_executed_count"] == 0
    assert gp048["action_completed_count"] == 0
    assert gp048["action_closed_count"] == 0
    assert gp048["audit_review_approved_count"] == 0
    assert gp048["official_audit_log_written_count"] == 0
    assert gp048["immutable_audit_write_count"] == 0
    assert gp048["tower_attestation_written_count"] == 0
    assert gp048["official_receipt_claimed_count"] == 0
    assert gp048["finalized_receipt_count"] == 0
    assert gp048["closed_receipt_count"] == 0
    assert gp048["access_request_granted_count"] == 0
    assert gp048["decision_granted_count"] == 0
    assert gp048["no_execution_enforced"] is True
    assert gp048["provider_read_enabled"] is False
    assert gp048["provider_write_enabled"] is False
    assert gp048["object_body_view_enabled"] is False
    assert gp048["raw_file_body_storage_still_locked"] is True
    assert gp048["file_body_persisted_count"] == 0
    assert gp048["object_body_available_count"] == 0
    assert gp048["direct_upload_still_locked"] is True
    assert gp048["checksum_verification_not_claimed"] is True
    assert gp048["hash_verification_not_claimed"] is True
    assert gp048["external_delivery_still_locked"] is True
    assert gp048["packet_export_still_locked"] is True
    assert gp048["approval_disabled"] is True
    assert gp048["execution_engine_disabled"] is True
    assert gp048["clouds_status"] == "parked_do_not_continue_from_vault_gp048"
    assert gp048["next_pack"] == "VAULT_GP049_STORAGE_AUDIT_ACTION_RECEIPT_PREVIEW"


def test_gp048_action_truth_metadata_only_no_approval_or_execution():
    status = get_gp048_status()
    truth = status["action_truth"]

    assert truth["storage_audit_action_preview_ready"] is True
    assert truth["action_suggestion_cards_visible"] is True
    assert truth["blocked_action_labels_visible"] is True
    assert truth["tower_action_authority_gates_visible"] is True
    assert truth["reviewer_followup_placeholders_visible"] is True
    assert truth["no_execution_enforcement_visible"] is True
    assert truth["metadata_only"] is True
    assert truth["private_action_preview_only"] is True

    assert truth["action_suggestion_count"] == 35
    assert truth["action_approved_count"] == 0
    assert truth["action_executed_count"] == 0
    assert truth["action_completed_count"] == 0
    assert truth["action_closed_count"] == 0
    assert truth["audit_review_approved_count"] == 0
    assert truth["official_audit_log_created_count"] == 0
    assert truth["official_audit_log_written_count"] == 0
    assert truth["immutable_audit_write_count"] == 0
    assert truth["immutable_hash_chain_written_count"] == 0
    assert truth["tower_attestation_written_count"] == 0
    assert truth["official_receipt_claimed_count"] == 0
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
    assert truth["safe_to_continue_to_gp049"] is True


def test_gp048_connected_to_gp047():
    home = get_storage_audit_action_preview_home()

    assert home["gp047_connection"]["gp047_ready"] is True
    assert home["gp047_connection"]["gp047_safe_to_continue"] is True
    assert home["gp047_connection"]["gp047_vault_done"] is False
    assert home["gp047_connection"]["gp047_section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert home["gp047_connection"]["gp047_review_card_count"] == 7
    assert home["gp047_connection"]["gp047_focus_lane_count"] == 35
    assert home["gp047_connection"]["gp047_unresolved_issue_label_count"] == 56
    assert home["gp047_connection"]["gp047_tower_authority_check_count"] == 56
    assert home["gp047_connection"]["gp047_reviewer_note_placeholder_count"] == 28
    assert home["gp047_connection"]["gp047_audit_review_approved_count"] == 0


def test_gp048_tower_authority_and_vault_boundaries():
    status = get_gp048_status()
    tower = status["tower_authority"]
    vault = status["vault_boundary"]

    assert tower["tower_owns_identity"] is True
    assert tower["tower_owns_permissions"] is True
    assert tower["tower_owns_action_authority_gates"] is True
    assert tower["tower_owns_execution_gates"] is True
    assert tower["tower_owns_audit_action_authority"] is True
    assert tower["tower_owns_audit_review_authority"] is True
    assert tower["vault_can_write_official_audit_log"] is False
    assert tower["vault_can_approve_audit_review"] is False
    assert tower["vault_can_approve_audit_action"] is False
    assert tower["vault_can_execute_audit_action"] is False

    assert vault["no_public_vault"] is True
    assert vault["action_default"] == "suggestion_only_blocked_no_execution"
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
    assert vault["public_packet_proof_allowed"] is False


def test_gp048_action_suggestions_are_blocked_preview_only():
    actions = get_storage_audit_action_suggestions()["action_suggestions"]

    assert actions["source_review_card_count"] == 7
    assert actions["action_suggestion_count"] == 35
    assert actions["action_suggestion_type_count"] == 5
    assert actions["action_suggestion_created_count"] == 35
    assert actions["action_approved_count"] == 0
    assert actions["action_executed_count"] == 0
    assert actions["action_completed_count"] == 0
    assert actions["action_closed_count"] == 0
    assert actions["blocked_action_count"] == 35
    assert actions["tower_action_authority_required_count"] == 35
    assert actions["tower_action_authority_granted_count"] == 0
    assert actions["reviewer_followup_required_count"] == 35
    assert actions["reviewer_followup_present_count"] == 0
    assert actions["no_execution_enforced_count"] == 35
    assert actions["audit_review_approved_count"] == 0
    assert actions["official_audit_log_written_count"] == 0
    assert actions["immutable_audit_written_count"] == 0
    assert actions["tower_attestation_written_count"] == 0
    assert actions["access_granted_count"] == 0
    assert actions["provider_read_enabled_count"] == 0
    assert actions["provider_write_enabled_count"] == 0
    assert actions["object_body_view_enabled_count"] == 0
    assert actions["file_body_persisted_count"] == 0
    assert actions["checksum_verified_count"] == 0
    assert actions["hash_verified_count"] == 0
    assert actions["export_allowed_count"] == 0
    assert actions["external_delivery_allowed_count"] == 0
    assert actions["approval_allowed_count"] == 0
    assert actions["execution_allowed_count"] == 0
    assert actions["safe_to_continue_action_suggestions"] is True

    action_types = {item["action_type"] for item in actions["action_suggestion_items"]}
    assert action_types == {
        "create_reviewer_followup",
        "request_tower_authority_review",
        "keep_provider_lock",
        "prepare_owner_summary",
        "carry_forward_to_action_receipt_preview",
    }

    for item in actions["action_suggestion_items"]:
        assert item["action_suggestion_id"].startswith("VSASP-")
        assert item["review_card_id"].startswith("VSARB-")
        assert item["audit_event_card_id"].startswith("VSAE-")
        assert item["receipt_card_id"].startswith("VSARP-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["action_status"] == "SUGGESTION_ONLY_BLOCKED_NO_EXECUTION"
        assert item["metadata_only"] is True
        assert item["private_action_preview_only"] is True
        assert item["action_suggestion_created"] is True
        assert item["action_approved"] is False
        assert item["action_executed"] is False
        assert item["blocked_action"] is True
        assert item["tower_action_authority_required"] is True
        assert item["tower_action_authority_granted"] is False
        assert item["no_execution_enforced"] is True
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["execution_allowed"] is False


def test_gp048_blocked_action_labels_block_everything_sensitive():
    labels = get_storage_audit_blocked_action_labels()["blocked_action_labels"]

    assert labels["blocked_action_label_count"] == 35
    assert labels["blocked_action_count"] == 35
    assert labels["blocks_action_approval_count"] == 35
    assert labels["blocks_action_execution_count"] == 35
    assert labels["blocks_provider_read_count"] == 35
    assert labels["blocks_object_body_view_count"] == 35
    assert labels["blocks_export_count"] == 35
    assert labels["blocks_external_delivery_count"] == 35
    assert labels["blocks_portal_access_count"] == 35
    assert labels["blocks_public_proof_count"] == 35
    assert labels["blocks_financing_decision_count"] == 35
    assert labels["blocks_legal_advice_count"] == 35
    assert labels["tower_authority_required_count"] == 35
    assert labels["action_approved_count"] == 0
    assert labels["action_executed_count"] == 0
    assert labels["safe_to_continue_blocked_action_labels"] is True

    for item in labels["blocked_action_label_items"]:
        assert item["blocked_action_label_id"].startswith("VSABAL-")
        assert item["action_suggestion_id"].startswith("VSASP-")
        assert item["blocked_action_label"] == "BLOCKED_ACTION_PREVIEW_ONLY_NO_EXECUTION"
        assert item["metadata_only"] is True
        assert item["blocked_action"] is True
        assert item["blocks_action_approval"] is True
        assert item["blocks_action_execution"] is True
        assert item["blocks_provider_read"] is True
        assert item["blocks_object_body_view"] is True
        assert item["blocks_execution"] is True
        assert item["action_approved"] is False
        assert item["action_executed"] is False


def test_gp048_tower_action_authority_gates_required_not_granted():
    gates = get_storage_tower_action_authority_gates()["tower_action_authority_gates"]

    assert gates["tower_action_authority_gate_count"] == 210
    assert gates["gate_type_count"] == 6
    assert gates["action_suggestion_count"] == 35
    assert gates["required_count"] == 210
    assert gates["granted_count"] == 0
    assert gates["vault_override_allowed_count"] == 0
    assert gates["action_approved_count"] == 0
    assert gates["action_executed_count"] == 0
    assert gates["audit_review_approved_count"] == 0
    assert gates["official_audit_log_written_count"] == 0
    assert gates["immutable_audit_written_count"] == 0
    assert gates["access_granted_count"] == 0
    assert gates["provider_read_enabled_count"] == 0
    assert gates["object_body_view_enabled_count"] == 0
    assert gates["execution_allowed_count"] == 0
    assert gates["safe_to_continue_tower_action_authority_gates"] is True

    gate_names = {item["gate_name"] for item in gates["tower_action_authority_gate_items"]}
    assert gate_names == {
        "identity_required",
        "tower_action_authority_required",
        "tower_audit_review_authority_required",
        "owner_review_required",
        "export_lock_required",
        "execution_lock_required",
    }

    for item in gates["tower_action_authority_gate_items"]:
        assert item["tower_action_gate_id"].startswith("VSATAG-")
        assert item["action_suggestion_id"].startswith("VSASP-")
        assert item["gate_status"] == "TOWER_ACTION_AUTHORITY_REQUIRED_NOT_GRANTED"
        assert item["metadata_only"] is True
        assert item["required"] is True
        assert item["granted"] is False
        assert item["vault_can_override"] is False
        assert item["action_approved"] is False
        assert item["action_executed"] is False
        assert item["execution_allowed"] is False


def test_gp048_reviewer_followup_placeholders_empty_unconfirmed():
    followups = get_storage_audit_reviewer_followup_placeholders()["reviewer_followup_placeholders"]

    assert followups["reviewer_followup_placeholder_count"] == 140
    assert followups["followup_field_type_count"] == 4
    assert followups["action_suggestion_count"] == 35
    assert followups["followup_required_count"] == 140
    assert followups["followup_present_count"] == 0
    assert followups["reviewer_bound_count"] == 0
    assert followups["reviewer_confirmed_count"] == 0
    assert followups["action_approved_count"] == 0
    assert followups["action_executed_count"] == 0
    assert followups["action_closed_count"] == 0
    assert followups["official_audit_log_written_count"] == 0
    assert followups["immutable_audit_written_count"] == 0
    assert followups["access_granted_count"] == 0
    assert followups["provider_read_enabled_count"] == 0
    assert followups["object_body_view_enabled_count"] == 0
    assert followups["execution_allowed_count"] == 0
    assert followups["safe_to_continue_reviewer_followup_placeholders"] is True

    fields = {item["followup_field"] for item in followups["reviewer_followup_placeholder_items"]}
    assert fields == {
        "followup_note",
        "risk_context",
        "tower_question",
        "owner_summary",
    }

    for item in followups["reviewer_followup_placeholder_items"]:
        assert item["reviewer_followup_placeholder_id"].startswith("VSARFP-")
        assert item["action_suggestion_id"].startswith("VSASP-")
        assert item["placeholder_status"] == "EMPTY_NOT_REVIEWED_NOT_CONFIRMED"
        assert item["metadata_only"] is True
        assert item["followup_required"] is True
        assert item["followup_present"] is False
        assert item["reviewer_confirmed"] is False
        assert item["action_approved"] is False
        assert item["action_executed"] is False
        assert item["execution_allowed"] is False


def test_gp048_no_execution_enforcement_records_lock_execution():
    enforcement = get_storage_audit_no_execution_enforcement()["no_execution_enforcement"]

    assert enforcement["no_execution_enforcement_count"] == 35
    assert enforcement["no_execution_enforced_count"] == 35
    assert enforcement["action_approved_count"] == 0
    assert enforcement["action_executed_count"] == 0
    assert enforcement["action_completed_count"] == 0
    assert enforcement["action_closed_count"] == 0
    assert enforcement["audit_review_approved_count"] == 0
    assert enforcement["official_audit_log_written_count"] == 0
    assert enforcement["immutable_audit_written_count"] == 0
    assert enforcement["official_receipt_claimed_count"] == 0
    assert enforcement["access_granted_count"] == 0
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
    assert enforcement["financing_decision_allowed_count"] == 0
    assert enforcement["legal_advice_allowed_count"] == 0
    assert enforcement["execution_allowed_count"] == 0
    assert enforcement["vault_override_allowed_count"] == 0
    assert enforcement["tower_authority_required_count"] == 35
    assert enforcement["safe_to_continue_no_execution_enforcement"] is True

    for item in enforcement["no_execution_enforcement_items"]:
        assert item["no_execution_enforcement_id"].startswith("VSANEE-")
        assert item["action_suggestion_id"].startswith("VSASP-")
        assert item["enforcement_status"] == "NO_EXECUTION_ENFORCED"
        assert item["metadata_only"] is True
        assert item["no_execution_enforced"] is True
        assert item["action_approved"] is False
        assert item["action_executed"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["execution_allowed"] is False
        assert item["vault_can_override"] is False
        assert item["tower_authority_required"] is True


def test_gp048_next_step_carries_forward_to_gp049_not_clouds():
    next_step = get_storage_audit_action_next_step()["next_step"]

    assert next_step["next_step_count"] == 3
    assert next_step["ready_for_gp049_count"] == 3
    assert next_step["action_suggestion_count"] == 35
    assert next_step["blocked_action_label_count"] == 35
    assert next_step["tower_action_authority_gate_count"] == 210
    assert next_step["reviewer_followup_placeholder_count"] == 140
    assert next_step["no_execution_enforcement_count"] == 35
    assert next_step["safe_to_continue_to_gp049"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False
    assert next_step["recommended_next_pack"] == "VAULT_GP049"
    assert next_step["recommended_next_pack_title"] == "Storage Audit Action Receipt Preview"

    note = next_step["owner_notebook_note"].lower()
    assert "archive vault — next product depth layer" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "audit action previews metadata-only" in rules
    assert "suggestion-only and blocked" in rules
    assert "no action approval claim" in rules
    assert "no action execution claim" in rules
    assert "no-execution enforcement active" in rules
    assert "safe to continue, not vault done" in rules

    for item in next_step["next_step_items"]:
        assert item["next_step_id"].startswith("VSAAPNX-")
        assert item["target_pack"] == "VAULT_GP049"
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False


def test_gp048_routes_and_counts_declared():
    home = get_storage_audit_action_preview_home()
    routes = home["action_routes"]
    counts = home["action_counts"]

    assert routes["section_header"] == "Archive Vault — Next Product Depth Layer"
    assert routes["section_range"] == "GP041-GP050"
    assert routes["route"] == "/vault/storage-audit-action-preview"
    assert routes["json_route"] == "/vault/storage-audit-action-preview.json"
    assert routes["action_suggestions_route"] == "/vault/storage-audit-action-suggestions.json"
    assert routes["blocked_action_labels_route"] == "/vault/storage-audit-blocked-action-labels.json"
    assert routes["tower_action_authority_gates_route"] == "/vault/storage-tower-action-authority-gates.json"
    assert routes["reviewer_followup_placeholders_route"] == "/vault/storage-audit-reviewer-followup-placeholders.json"
    assert routes["no_execution_enforcement_route"] == "/vault/storage-audit-no-execution-enforcement.json"
    assert routes["next_step_route"] == "/vault/storage-audit-action-next-step.json"
    assert routes["gp048_status_route"] == "/vault/gp048-status.json"

    assert counts["source_review_card_count"] == 7
    assert counts["action_suggestion_count"] == 35
    assert counts["action_suggestion_type_count"] == 5
    assert counts["blocked_action_label_count"] == 35
    assert counts["tower_action_authority_gate_count"] == 210
    assert counts["reviewer_followup_placeholder_count"] == 140
    assert counts["no_execution_enforcement_count"] == 35
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


def test_gp048_html_is_dark_and_has_no_white_background_tokens():
    html = render_storage_audit_action_preview_page()
    lowered = html.lower()

    assert "Vault Storage Audit Action Preview" in html
    assert "Archive Vault" in html
    assert "/vault/storage-audit-action-preview.json" in html
    assert "/vault/gp048-status.json" in html
    assert "Clouds parked" in html
    assert "No action approval" in html
    assert "No execution" in html
    assert "No provider access" in html

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


def test_gp048_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-audit-action-preview",
        "/vault/storage-audit-action-preview.json",
        "/vault/storage-audit-action-suggestions.json",
        "/vault/storage-audit-blocked-action-labels.json",
        "/vault/storage-tower-action-authority-gates.json",
        "/vault/storage-audit-reviewer-followup-placeholders.json",
        "/vault/storage-audit-no-execution-enforcement.json",
        "/vault/storage-audit-action-next-step.json",
        "/vault/gp048-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp048_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-audit-action-preview",
        "/vault/storage-audit-action-preview.json",
        "/vault/storage-audit-action-suggestions.json",
        "/vault/storage-audit-blocked-action-labels.json",
        "/vault/storage-tower-action-authority-gates.json",
        "/vault/storage-audit-reviewer-followup-placeholders.json",
        "/vault/storage-audit-no-execution-enforcement.json",
        "/vault/storage-audit-action-next-step.json",
        "/vault/gp048-status.json",
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
                assert b"Vault Storage Audit Action Preview" in response.data
