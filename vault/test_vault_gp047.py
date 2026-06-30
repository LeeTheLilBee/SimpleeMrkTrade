"""
Tests for VAULT GIANT PACK 047 — Storage Audit Review Board
"""

from pathlib import Path

import pytest

from vault.storage_audit_review_board_service import (
    get_gp047_status,
    get_storage_audit_review_board_home,
    get_storage_audit_review_cards,
    get_storage_audit_review_focus_lanes,
    get_storage_audit_review_next_step,
    get_storage_audit_reviewer_note_placeholders,
    get_storage_audit_unresolved_issue_labels,
    get_storage_tower_audit_authority_checks,
    render_storage_audit_review_board_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp047_status_ready_safe_continue_not_done():
    status = get_gp047_status()
    gp047 = status["gp047_status"]

    assert status["pack"]["id"] == "VAULT_GP047"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert status["pack"]["section_range"] == "GP041-GP050"

    assert gp047["ready"] is True
    assert gp047["section_id"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert gp047["section_title"] == "Archive Vault — Next Product Depth Layer"
    assert gp047["section_range"] == "GP041-GP050"
    assert gp047["storage_audit_review_board_ready"] is True
    assert gp047["safe_to_continue_to_gp048"] is True
    assert gp047["vault_done"] is False
    assert gp047["foundation_status"] == "safe_to_continue_not_done"
    assert gp047["metadata_only_review_board"] is True
    assert gp047["private_review_only"] is True
    assert gp047["review_cards_ready"] is True
    assert gp047["audit_review_approved_count"] == 0
    assert gp047["audit_review_completed_count"] == 0
    assert gp047["audit_review_closed_count"] == 0
    assert gp047["official_audit_log_created_count"] == 0
    assert gp047["official_audit_log_written_count"] == 0
    assert gp047["immutable_audit_write_count"] == 0
    assert gp047["immutable_hash_chain_written_count"] == 0
    assert gp047["tower_attestation_written_count"] == 0
    assert gp047["official_receipt_claimed_count"] == 0
    assert gp047["finalized_receipt_count"] == 0
    assert gp047["closed_receipt_count"] == 0
    assert gp047["access_request_granted_count"] == 0
    assert gp047["decision_granted_count"] == 0
    assert gp047["provider_read_enabled"] is False
    assert gp047["provider_write_enabled"] is False
    assert gp047["object_body_view_enabled"] is False
    assert gp047["raw_file_body_storage_still_locked"] is True
    assert gp047["file_body_persisted_count"] == 0
    assert gp047["object_body_available_count"] == 0
    assert gp047["direct_upload_still_locked"] is True
    assert gp047["checksum_verification_not_claimed"] is True
    assert gp047["hash_verification_not_claimed"] is True
    assert gp047["external_delivery_still_locked"] is True
    assert gp047["packet_export_still_locked"] is True
    assert gp047["approval_disabled"] is True
    assert gp047["execution_engine_disabled"] is True
    assert gp047["clouds_status"] == "parked_do_not_continue_from_vault_gp047"
    assert gp047["next_pack"] == "VAULT_GP048_STORAGE_AUDIT_ACTION_PREVIEW"


def test_gp047_review_truth_metadata_only_no_approval_or_official_logs():
    status = get_gp047_status()
    truth = status["review_truth"]

    assert truth["storage_audit_review_board_ready"] is True
    assert truth["review_cards_visible"] is True
    assert truth["focus_lanes_visible"] is True
    assert truth["unresolved_issue_labels_visible"] is True
    assert truth["tower_audit_authority_checks_visible"] is True
    assert truth["reviewer_note_placeholders_visible"] is True
    assert truth["metadata_only"] is True
    assert truth["private_review_only"] is True

    assert truth["audit_review_card_count"] == 7
    assert truth["audit_review_approved_count"] == 0
    assert truth["audit_review_completed_count"] == 0
    assert truth["audit_review_closed_count"] == 0
    assert truth["official_audit_log_created_count"] == 0
    assert truth["official_audit_log_written_count"] == 0
    assert truth["immutable_audit_write_count"] == 0
    assert truth["immutable_hash_chain_written_count"] == 0
    assert truth["tower_attestation_written_count"] == 0
    assert truth["official_receipt_claimed_count"] == 0
    assert truth["finalized_receipt_count"] == 0
    assert truth["closed_receipt_count"] == 0
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
    assert truth["direct_upload_enabled"] is False
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
    assert truth["safe_to_continue_to_gp048"] is True


def test_gp047_connected_to_gp046():
    home = get_storage_audit_review_board_home()

    assert home["gp046_connection"]["gp046_ready"] is True
    assert home["gp046_connection"]["gp046_safe_to_continue"] is True
    assert home["gp046_connection"]["gp046_vault_done"] is False
    assert home["gp046_connection"]["gp046_section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert home["gp046_connection"]["gp046_audit_event_card_count"] == 7
    assert home["gp046_connection"]["gp046_denied_access_audit_row_count"] == 49
    assert home["gp046_connection"]["gp046_tower_gate_audit_snapshot_count"] == 56
    assert home["gp046_connection"]["gp046_receipt_preview_audit_link_count"] == 7
    assert home["gp046_connection"]["gp046_immutable_log_placeholder_count"] == 28
    assert home["gp046_connection"]["gp046_official_audit_log_written_count"] == 0


def test_gp047_tower_authority_and_vault_boundaries():
    status = get_gp047_status()
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
    assert tower["tower_owns_audit_authority"] is True
    assert tower["tower_owns_audit_review_authority"] is True
    assert tower["vault_can_write_official_audit_log"] is False
    assert tower["vault_can_approve_audit_review"] is False

    assert vault["no_public_vault"] is True
    assert vault["direct_raw_upload_unlocked"] is False
    assert vault["permanent_file_body_storage_enabled"] is False
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
    assert vault["public_packet_proof_allowed"] is False


def test_gp047_review_cards_metadata_only_unapproved_unclosed():
    cards = get_storage_audit_review_cards()["review_cards"]

    assert cards["review_card_count"] == 7
    assert cards["review_card_created_count"] == 7
    assert cards["review_approved_count"] == 0
    assert cards["review_completed_count"] == 0
    assert cards["review_closed_count"] == 0
    assert cards["reviewer_note_required_count"] == 7
    assert cards["reviewer_note_present_count"] == 0
    assert cards["unresolved_issues_active_count"] == 7
    assert cards["tower_audit_authority_required_count"] == 7
    assert cards["tower_audit_authority_granted_count"] == 0
    assert cards["official_audit_log_written_count"] == 0
    assert cards["immutable_audit_written_count"] == 0
    assert cards["tower_attestation_written_count"] == 0
    assert cards["access_granted_count"] == 0
    assert cards["decision_granted_count"] == 0
    assert cards["provider_read_enabled_count"] == 0
    assert cards["provider_write_enabled_count"] == 0
    assert cards["object_body_view_enabled_count"] == 0
    assert cards["file_body_persisted_count"] == 0
    assert cards["checksum_verified_count"] == 0
    assert cards["hash_verified_count"] == 0
    assert cards["export_allowed_count"] == 0
    assert cards["external_delivery_allowed_count"] == 0
    assert cards["portal_access_allowed_count"] == 0
    assert cards["approval_allowed_count"] == 0
    assert cards["execution_allowed_count"] == 0
    assert cards["safe_to_continue_review_cards"] is True

    scopes = {item["scope"] for item in cards["review_card_items"]}
    assert scopes == {
        "document_intake",
        "attachment_registry",
        "requirement_match",
        "evidence_binder",
        "packet_workspace",
        "controlled_packet_assembly",
        "receipt_chain",
    }

    for item in cards["review_card_items"]:
        assert item["review_card_id"].startswith("VSARB-")
        assert item["audit_event_card_id"].startswith("VSAE-")
        assert item["receipt_card_id"].startswith("VSARP-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["review_status"] == "REVIEW_BOARD_PREVIEW_ONLY_UNAPPROVED_UNCLOSED"
        assert item["metadata_only"] is True
        assert item["private_review_only"] is True
        assert item["review_card_created"] is True
        assert item["review_approved"] is False
        assert item["review_completed"] is False
        assert item["review_closed"] is False
        assert item["unresolved_issues_active"] is True
        assert item["tower_audit_authority_required"] is True
        assert item["tower_audit_authority_granted"] is False
        assert item["official_audit_log_written"] is False
        assert item["immutable_audit_written"] is False
        assert item["tower_attestation_written"] is False
        assert item["access_granted"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["execution_allowed"] is False


def test_gp047_focus_lanes_open_not_completed():
    lanes = get_storage_audit_review_focus_lanes()["focus_lanes"]

    assert lanes["focus_lane_count"] == 35
    assert lanes["focus_lane_type_count"] == 5
    assert lanes["review_card_count"] == 7
    assert lanes["focus_lane_open_count"] == 35
    assert lanes["focus_lane_completed_count"] == 0
    assert lanes["review_approved_count"] == 0
    assert lanes["official_audit_log_written_count"] == 0
    assert lanes["immutable_audit_written_count"] == 0
    assert lanes["tower_attestation_written_count"] == 0
    assert lanes["access_granted_count"] == 0
    assert lanes["provider_read_enabled_count"] == 0
    assert lanes["object_body_view_enabled_count"] == 0
    assert lanes["export_allowed_count"] == 0
    assert lanes["external_delivery_allowed_count"] == 0
    assert lanes["execution_allowed_count"] == 0
    assert lanes["safe_to_continue_focus_lanes"] is True

    lane_names = {item["focus_lane"] for item in lanes["focus_lane_items"]}
    assert lane_names == {
        "denied_access_review",
        "tower_gate_review",
        "receipt_preview_review",
        "immutable_placeholder_review",
        "provider_lock_review",
    }

    for item in lanes["focus_lane_items"]:
        assert item["focus_lane_id"].startswith("VSARFL-")
        assert item["review_card_id"].startswith("VSARB-")
        assert item["focus_status"] == "OPEN_REVIEW_FOCUS_METADATA_ONLY"
        assert item["metadata_only"] is True
        assert item["focus_lane_open"] is True
        assert item["focus_lane_completed"] is False
        assert item["review_approved"] is False
        assert item["official_audit_log_written"] is False
        assert item["immutable_audit_written"] is False
        assert item["access_granted"] is False


def test_gp047_unresolved_issue_labels_block_sensitive_paths():
    labels = get_storage_audit_unresolved_issue_labels()["unresolved_issue_labels"]

    assert labels["unresolved_issue_label_count"] == 56
    assert labels["unresolved_issue_type_count"] == 8
    assert labels["review_card_count"] == 7
    assert labels["unresolved_count"] == 56
    assert labels["blocks_review_approval_count"] == 56
    assert labels["blocks_review_close_count"] == 56
    assert labels["blocks_official_audit_log_count"] == 56
    assert labels["blocks_immutable_audit_write_count"] == 56
    assert labels["blocks_tower_attestation_count"] == 56
    assert labels["blocks_access_grant_count"] == 56
    assert labels["blocks_provider_read_count"] == 56
    assert labels["blocks_object_body_view_count"] == 56
    assert labels["blocks_export_count"] == 56
    assert labels["blocks_external_delivery_count"] == 56
    assert labels["blocks_execution_count"] == 56
    assert labels["owner_resolvable_now_count"] == 0
    assert labels["tower_authority_required_count"] == 56
    assert labels["safe_to_continue_unresolved_issue_labels"] is True

    issues = {item["issue_type"] for item in labels["unresolved_issue_label_items"]}
    assert issues == {
        "official_audit_log_not_written",
        "immutable_audit_not_written",
        "tower_attestation_not_written",
        "official_receipt_not_claimed",
        "receipt_not_finalized",
        "access_not_granted",
        "provider_read_locked",
        "object_body_view_locked",
    }

    for item in labels["unresolved_issue_label_items"]:
        assert item["unresolved_issue_label_id"].startswith("VSAUIL-")
        assert item["review_card_id"].startswith("VSARB-")
        assert item["issue_status"] == "ACTIVE_UNRESOLVED_REVIEW_ISSUE"
        assert item["metadata_only"] is True
        assert item["unresolved"] is True
        assert item["blocks_review_approval"] is True
        assert item["blocks_official_audit_log"] is True
        assert item["blocks_immutable_audit_write"] is True
        assert item["blocks_access_grant"] is True
        assert item["blocks_execution"] is True


def test_gp047_tower_authority_checks_required_not_granted():
    checks = get_storage_tower_audit_authority_checks()["tower_authority_checks"]

    assert checks["tower_authority_check_count"] == 56
    assert checks["tower_audit_authority_required_count"] == 56
    assert checks["tower_audit_authority_granted_count"] == 0
    assert checks["vault_override_allowed_count"] == 0
    assert checks["review_approved_count"] == 0
    assert checks["official_audit_log_written_count"] == 0
    assert checks["immutable_audit_written_count"] == 0
    assert checks["tower_attestation_written_count"] == 0
    assert checks["decision_approved_count"] == 0
    assert checks["access_granted_count"] == 0
    assert checks["provider_read_enabled_count"] == 0
    assert checks["object_body_view_enabled_count"] == 0
    assert checks["export_allowed_count"] == 0
    assert checks["external_delivery_allowed_count"] == 0
    assert checks["safe_to_continue_tower_authority_checks"] is True

    for item in checks["tower_authority_check_items"]:
        assert item["tower_authority_check_id"].startswith("VSATAC-")
        assert item["tower_gate_audit_snapshot_id"].startswith("VSATGAS-")
        assert item["authority_check_status"] == "TOWER_AUDIT_AUTHORITY_REQUIRED_NOT_GRANTED"
        assert item["metadata_only"] is True
        assert item["tower_audit_authority_required"] is True
        assert item["tower_audit_authority_granted"] is False
        assert item["vault_can_override"] is False
        assert item["review_approved"] is False
        assert item["official_audit_log_written"] is False
        assert item["immutable_audit_written"] is False
        assert item["tower_attestation_written"] is False


def test_gp047_reviewer_note_placeholders_empty_unconfirmed():
    notes = get_storage_audit_reviewer_note_placeholders()["reviewer_note_placeholders"]

    assert notes["reviewer_note_placeholder_count"] == 28
    assert notes["reviewer_note_field_type_count"] == 4
    assert notes["review_card_count"] == 7
    assert notes["note_required_count"] == 28
    assert notes["note_present_count"] == 0
    assert notes["reviewer_bound_count"] == 0
    assert notes["reviewer_confirmed_count"] == 0
    assert notes["review_approved_count"] == 0
    assert notes["review_completed_count"] == 0
    assert notes["review_closed_count"] == 0
    assert notes["official_audit_log_written_count"] == 0
    assert notes["immutable_audit_written_count"] == 0
    assert notes["tower_attestation_written_count"] == 0
    assert notes["access_granted_count"] == 0
    assert notes["provider_read_enabled_count"] == 0
    assert notes["object_body_view_enabled_count"] == 0
    assert notes["export_allowed_count"] == 0
    assert notes["external_delivery_allowed_count"] == 0
    assert notes["execution_allowed_count"] == 0
    assert notes["safe_to_continue_reviewer_note_placeholders"] is True

    fields = {item["note_field"] for item in notes["reviewer_note_placeholder_items"]}
    assert fields == {
        "reviewer_observation",
        "risk_note",
        "tower_followup_note",
        "owner_summary_note",
    }

    for item in notes["reviewer_note_placeholder_items"]:
        assert item["reviewer_note_placeholder_id"].startswith("VSARNP-")
        assert item["review_card_id"].startswith("VSARB-")
        assert item["placeholder_status"] == "EMPTY_NOT_REVIEWED_NOT_CONFIRMED"
        assert item["metadata_only"] is True
        assert item["note_required"] is True
        assert item["note_present"] is False
        assert item["reviewer_bound"] is False
        assert item["reviewer_confirmed"] is False
        assert item["review_approved"] is False
        assert item["review_closed"] is False
        assert item["official_audit_log_written"] is False
        assert item["execution_allowed"] is False


def test_gp047_next_step_carries_forward_to_gp048_not_clouds():
    next_step = get_storage_audit_review_next_step()["next_step"]

    assert next_step["next_step_count"] == 3
    assert next_step["ready_for_gp048_count"] == 3
    assert next_step["review_card_count"] == 7
    assert next_step["focus_lane_count"] == 35
    assert next_step["unresolved_issue_label_count"] == 56
    assert next_step["tower_authority_check_count"] == 56
    assert next_step["reviewer_note_placeholder_count"] == 28
    assert next_step["safe_to_continue_to_gp048"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False
    assert next_step["recommended_next_pack"] == "VAULT_GP048"
    assert next_step["recommended_next_pack_title"] == "Storage Audit Action Preview"

    note = next_step["owner_notebook_note"].lower()
    assert "archive vault — next product depth layer" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "audit review board metadata-only" in rules
    assert "unapproved, incomplete, and unclosed" in rules
    assert "unresolved review issues active" in rules
    assert "no official audit log claim" in rules
    assert "no immutable audit write claim" in rules
    assert "safe to continue, not vault done" in rules

    for item in next_step["next_step_items"]:
        assert item["next_step_id"].startswith("VSARBNX-")
        assert item["target_pack"] == "VAULT_GP048"
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False


def test_gp047_routes_and_counts_declared():
    home = get_storage_audit_review_board_home()
    routes = home["review_routes"]
    counts = home["review_counts"]

    assert routes["section_header"] == "Archive Vault — Next Product Depth Layer"
    assert routes["section_range"] == "GP041-GP050"
    assert routes["route"] == "/vault/storage-audit-review-board"
    assert routes["json_route"] == "/vault/storage-audit-review-board.json"
    assert routes["review_cards_route"] == "/vault/storage-audit-review-cards.json"
    assert routes["focus_lanes_route"] == "/vault/storage-audit-review-focus-lanes.json"
    assert routes["unresolved_issue_labels_route"] == "/vault/storage-audit-unresolved-issue-labels.json"
    assert routes["tower_authority_checks_route"] == "/vault/storage-tower-audit-authority-checks.json"
    assert routes["reviewer_note_placeholders_route"] == "/vault/storage-audit-reviewer-note-placeholders.json"
    assert routes["next_step_route"] == "/vault/storage-audit-review-next-step.json"
    assert routes["gp047_status_route"] == "/vault/gp047-status.json"

    assert counts["review_card_count"] == 7
    assert counts["focus_lane_count"] == 35
    assert counts["unresolved_issue_label_count"] == 56
    assert counts["tower_authority_check_count"] == 56
    assert counts["reviewer_note_placeholder_count"] == 28
    assert counts["audit_review_approved_count"] == 0
    assert counts["audit_review_completed_count"] == 0
    assert counts["audit_review_closed_count"] == 0
    assert counts["official_audit_log_created_count"] == 0
    assert counts["official_audit_log_written_count"] == 0
    assert counts["immutable_audit_write_count"] == 0
    assert counts["official_receipt_claimed_count"] == 0
    assert counts["finalized_receipt_count"] == 0
    assert counts["closed_receipt_count"] == 0
    assert counts["access_request_granted_count"] == 0
    assert counts["decision_granted_count"] == 0
    assert counts["provider_read_enabled_count"] == 0
    assert counts["object_body_view_enabled_count"] == 0
    assert counts["external_delivery_allowed_count"] == 0
    assert counts["packet_export_allowed_count"] == 0
    assert counts["execution_allowed_count"] == 0
    assert counts["metadata_only"] is True


def test_gp047_html_is_dark_and_has_no_white_background_tokens():
    html = render_storage_audit_review_board_page()
    lowered = html.lower()

    assert "Vault Storage Audit Review Board" in html
    assert "Archive Vault" in html
    assert "/vault/storage-audit-review-board.json" in html
    assert "/vault/gp047-status.json" in html
    assert "Clouds parked" in html
    assert "No review approval" in html
    assert "No official audit log" in html
    assert "No immutable write" in html

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


def test_gp047_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-audit-review-board",
        "/vault/storage-audit-review-board.json",
        "/vault/storage-audit-review-cards.json",
        "/vault/storage-audit-review-focus-lanes.json",
        "/vault/storage-audit-unresolved-issue-labels.json",
        "/vault/storage-tower-audit-authority-checks.json",
        "/vault/storage-audit-reviewer-note-placeholders.json",
        "/vault/storage-audit-review-next-step.json",
        "/vault/gp047-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp047_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-audit-review-board",
        "/vault/storage-audit-review-board.json",
        "/vault/storage-audit-review-cards.json",
        "/vault/storage-audit-review-focus-lanes.json",
        "/vault/storage-audit-unresolved-issue-labels.json",
        "/vault/storage-tower-audit-authority-checks.json",
        "/vault/storage-audit-reviewer-note-placeholders.json",
        "/vault/storage-audit-review-next-step.json",
        "/vault/gp047-status.json",
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
                assert b"Vault Storage Audit Review Board" in response.data
