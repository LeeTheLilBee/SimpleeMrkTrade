"""
Tests for VAULT GIANT PACK 046 — Storage Audit Trail Preview
"""

from pathlib import Path

import pytest

from vault.storage_audit_trail_preview_service import (
    get_gp046_status,
    get_storage_audit_event_cards,
    get_storage_audit_trail_next_step,
    get_storage_audit_trail_preview_home,
    get_storage_denied_access_audit_rows,
    get_storage_immutable_log_placeholders,
    get_storage_receipt_preview_audit_links,
    get_storage_tower_gate_audit_snapshots,
    render_storage_audit_trail_preview_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp046_status_ready_safe_continue_not_done():
    status = get_gp046_status()
    gp046 = status["gp046_status"]

    assert status["pack"]["id"] == "VAULT_GP046"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert status["pack"]["section_range"] == "GP041-GP050"

    assert gp046["ready"] is True
    assert gp046["section_id"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert gp046["section_title"] == "Archive Vault — Next Product Depth Layer"
    assert gp046["section_range"] == "GP041-GP050"
    assert gp046["storage_audit_trail_preview_ready"] is True
    assert gp046["safe_to_continue_to_gp047"] is True
    assert gp046["vault_done"] is False
    assert gp046["foundation_status"] == "safe_to_continue_not_done"
    assert gp046["metadata_only_audit_preview"] is True
    assert gp046["private_preview_only"] is True
    assert gp046["audit_event_cards_ready"] is True
    assert gp046["official_audit_log_created_count"] == 0
    assert gp046["official_audit_log_written_count"] == 0
    assert gp046["immutable_audit_write_count"] == 0
    assert gp046["immutable_hash_chain_written_count"] == 0
    assert gp046["tower_attestation_written_count"] == 0
    assert gp046["official_receipt_claimed_count"] == 0
    assert gp046["finalized_receipt_count"] == 0
    assert gp046["closed_receipt_count"] == 0
    assert gp046["receipt_finalized"] is False
    assert gp046["receipt_closed"] is False
    assert gp046["access_request_granted_count"] == 0
    assert gp046["decision_granted_count"] == 0
    assert gp046["access_denied_by_default"] is True
    assert gp046["provider_read_enabled"] is False
    assert gp046["provider_write_enabled"] is False
    assert gp046["object_body_view_enabled"] is False
    assert gp046["raw_file_body_storage_still_locked"] is True
    assert gp046["file_body_persisted_count"] == 0
    assert gp046["object_body_available_count"] == 0
    assert gp046["direct_upload_still_locked"] is True
    assert gp046["checksum_verification_not_claimed"] is True
    assert gp046["hash_verification_not_claimed"] is True
    assert gp046["external_delivery_still_locked"] is True
    assert gp046["packet_export_still_locked"] is True
    assert gp046["approval_disabled"] is True
    assert gp046["execution_engine_disabled"] is True
    assert gp046["clouds_status"] == "parked_do_not_continue_from_vault_gp046"
    assert gp046["next_pack"] == "VAULT_GP047_STORAGE_AUDIT_REVIEW_BOARD"


def test_gp046_audit_truth_preview_only_no_official_or_immutable_log():
    status = get_gp046_status()
    truth = status["audit_truth"]

    assert truth["storage_audit_trail_preview_ready"] is True
    assert truth["audit_event_cards_visible"] is True
    assert truth["denied_access_audit_rows_visible"] is True
    assert truth["tower_gate_audit_snapshots_visible"] is True
    assert truth["receipt_preview_audit_links_visible"] is True
    assert truth["immutable_log_placeholders_visible"] is True
    assert truth["metadata_only"] is True
    assert truth["private_preview_only"] is True

    assert truth["audit_event_preview_created_count"] == 7
    assert truth["official_audit_log_created_count"] == 0
    assert truth["official_audit_log_written_count"] == 0
    assert truth["immutable_audit_write_count"] == 0
    assert truth["immutable_hash_chain_written_count"] == 0
    assert truth["tower_attestation_written_count"] == 0
    assert truth["official_receipt_claimed_count"] == 0
    assert truth["finalized_receipt_count"] == 0
    assert truth["closed_receipt_count"] == 0
    assert truth["receipt_finalized"] is False
    assert truth["receipt_closed"] is False
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
    assert truth["safe_to_continue_to_gp047"] is True


def test_gp046_connected_to_gp045():
    home = get_storage_audit_trail_preview_home()

    assert home["gp045_connection"]["gp045_ready"] is True
    assert home["gp045_connection"]["gp045_safe_to_continue"] is True
    assert home["gp045_connection"]["gp045_vault_done"] is False
    assert home["gp045_connection"]["gp045_section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert home["gp045_connection"]["gp045_receipt_card_count"] == 7
    assert home["gp045_connection"]["gp045_tower_requirement_receipt_count"] == 56
    assert home["gp045_connection"]["gp045_owner_review_receipt_placeholder_count"] == 28
    assert home["gp045_connection"]["gp045_denial_receipt_summary_count"] == 49
    assert home["gp045_connection"]["gp045_official_receipt_claimed_count"] == 0


def test_gp046_tower_authority_and_vault_boundaries():
    status = get_gp046_status()
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
    assert tower["vault_owns_tower_permissions"] is False
    assert tower["vault_can_write_official_audit_log"] is False

    assert vault["no_public_vault"] is True
    assert vault["direct_raw_upload_unlocked"] is False
    assert vault["permanent_file_body_storage_enabled"] is False
    assert vault["audit_default"] == "preview_only_not_official_not_immutable"
    assert vault["external_packet_delivery_allowed"] is False
    assert vault["packet_export_allowed"] is False
    assert vault["unredacted_export_allowed"] is False
    assert vault["raw_export_allowed"] is False
    assert vault["object_body_view_allowed"] is False
    assert vault["provider_read_allowed"] is False
    assert vault["provider_write_allowed"] is False
    assert vault["official_audit_log_write_allowed"] is False
    assert vault["immutable_log_write_allowed"] is False
    assert vault["public_ob_proof_allowed"] is False
    assert vault["public_packet_proof_allowed"] is False
    assert vault["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp046_audit_event_cards_preview_only():
    cards = get_storage_audit_event_cards()["audit_event_cards"]

    assert cards["audit_event_card_count"] == 7
    assert cards["audit_event_type_count"] == 5
    assert cards["audit_preview_created_count"] == 7
    assert cards["official_audit_log_created_count"] == 0
    assert cards["official_audit_log_written_count"] == 0
    assert cards["immutable_audit_written_count"] == 0
    assert cards["immutable_hash_chain_written_count"] == 0
    assert cards["tower_attestation_written_count"] == 0
    assert cards["receipt_preview_linked_count"] == 7
    assert cards["official_receipt_claimed_count"] == 0
    assert cards["receipt_finalized_count"] == 0
    assert cards["receipt_closed_count"] == 0
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
    assert cards["safe_to_continue_audit_event_cards"] is True

    scopes = {item["scope"] for item in cards["audit_event_card_items"]}
    assert scopes == {
        "document_intake",
        "attachment_registry",
        "requirement_match",
        "evidence_binder",
        "packet_workspace",
        "controlled_packet_assembly",
        "receipt_chain",
    }

    for item in cards["audit_event_card_items"]:
        assert item["audit_event_card_id"].startswith("VSAE-")
        assert item["receipt_card_id"].startswith("VSARP-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["access_request_card_id"].startswith("VSAR-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["audit_event_status"] == "PREVIEW_ONLY_NOT_OFFICIAL_NOT_IMMUTABLE"
        assert item["metadata_only"] is True
        assert item["private_preview_only"] is True
        assert item["audit_preview_created"] is True
        assert item["official_audit_log_created"] is False
        assert item["official_audit_log_written"] is False
        assert item["immutable_audit_written"] is False
        assert item["immutable_hash_chain_written"] is False
        assert item["tower_attestation_written"] is False
        assert item["receipt_preview_linked"] is True
        assert item["access_granted"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["execution_allowed"] is False


def test_gp046_denied_access_audit_rows_block_access():
    rows = get_storage_denied_access_audit_rows()["denied_access_audit_rows"]

    assert rows["denied_access_audit_row_count"] == 49
    assert rows["denied_by_default_count"] == 49
    assert rows["access_granted_count"] == 0
    assert rows["official_audit_log_written_count"] == 0
    assert rows["immutable_audit_written_count"] == 0
    assert rows["official_receipt_claimed_count"] == 0
    assert rows["receipt_finalized_count"] == 0
    assert rows["receipt_closed_count"] == 0
    assert rows["provider_read_enabled_count"] == 0
    assert rows["object_body_view_enabled_count"] == 0
    assert rows["export_allowed_count"] == 0
    assert rows["external_delivery_allowed_count"] == 0
    assert rows["portal_access_allowed_count"] == 0
    assert rows["execution_allowed_count"] == 0
    assert rows["safe_to_continue_denied_access_audit_rows"] is True

    for item in rows["denied_access_audit_row_items"]:
        assert item["denied_access_audit_row_id"].startswith("VSADAR-")
        assert item["denial_receipt_summary_id"].startswith("VSADRS-")
        assert item["denial_reason_label_id"].startswith("VSADRL-")
        assert item["audit_row_status"] == "DENIED_ACCESS_AUDIT_PREVIEW_ONLY"
        assert item["metadata_only"] is True
        assert item["denied_by_default"] is True
        assert item["access_granted"] is False
        assert item["official_audit_log_written"] is False
        assert item["immutable_audit_written"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["execution_allowed"] is False


def test_gp046_tower_gate_audit_snapshots_required_not_granted():
    snapshots = get_storage_tower_gate_audit_snapshots()["tower_gate_audit_snapshots"]

    assert snapshots["tower_gate_audit_snapshot_count"] == 56
    assert snapshots["audit_snapshot_created_count"] == 56
    assert snapshots["required_count"] == 56
    assert snapshots["granted_count"] == 0
    assert snapshots["official_audit_log_written_count"] == 0
    assert snapshots["immutable_audit_written_count"] == 0
    assert snapshots["tower_attestation_written_count"] == 0
    assert snapshots["vault_override_allowed_count"] == 0
    assert snapshots["decision_approved_count"] == 0
    assert snapshots["access_granted_count"] == 0
    assert snapshots["provider_read_enabled_count"] == 0
    assert snapshots["object_body_view_enabled_count"] == 0
    assert snapshots["export_allowed_count"] == 0
    assert snapshots["external_delivery_allowed_count"] == 0
    assert snapshots["safe_to_continue_tower_gate_audit_snapshots"] is True

    for item in snapshots["tower_gate_audit_snapshot_items"]:
        assert item["tower_gate_audit_snapshot_id"].startswith("VSATGAS-")
        assert item["tower_requirement_receipt_id"].startswith("VSATRS-")
        assert item["tower_requirement_id"].startswith("VSATR-")
        assert item["audit_snapshot_status"] == "TOWER_REQUIREMENT_REQUIRED_NOT_GRANTED_AUDIT_PREVIEW"
        assert item["metadata_only"] is True
        assert item["required"] is True
        assert item["granted"] is False
        assert item["audit_snapshot_created"] is True
        assert item["official_audit_log_written"] is False
        assert item["immutable_audit_written"] is False
        assert item["tower_attestation_written"] is False
        assert item["vault_can_override"] is False


def test_gp046_receipt_preview_audit_links_preview_only():
    links = get_storage_receipt_preview_audit_links()["receipt_preview_audit_links"]

    assert links["receipt_preview_audit_link_count"] == 7
    assert links["receipt_preview_linked_count"] == 7
    assert links["official_receipt_claimed_count"] == 0
    assert links["receipt_finalized_count"] == 0
    assert links["receipt_closed_count"] == 0
    assert links["official_audit_log_written_count"] == 0
    assert links["immutable_audit_written_count"] == 0
    assert links["access_granted_count"] == 0
    assert links["provider_read_enabled_count"] == 0
    assert links["object_body_view_enabled_count"] == 0
    assert links["export_allowed_count"] == 0
    assert links["external_delivery_allowed_count"] == 0
    assert links["safe_to_continue_receipt_preview_audit_links"] is True

    for item in links["receipt_preview_audit_link_items"]:
        assert item["receipt_preview_audit_link_id"].startswith("VSARPAL-")
        assert item["receipt_card_id"].startswith("VSARP-")
        assert item["decision_card_id"].startswith("VSADQ-")
        assert item["audit_link_status"] == "LINKED_TO_PREVIEW_ONLY_RECEIPT"
        assert item["metadata_only"] is True
        assert item["receipt_preview_linked"] is True
        assert item["official_receipt_claimed"] is False
        assert item["receipt_finalized"] is False
        assert item["receipt_closed"] is False
        assert item["official_audit_log_written"] is False
        assert item["immutable_audit_written"] is False
        assert item["access_granted"] is False


def test_gp046_immutable_log_placeholders_not_written():
    placeholders = get_storage_immutable_log_placeholders()["immutable_log_placeholders"]

    assert placeholders["immutable_log_placeholder_count"] == 28
    assert placeholders["placeholder_type_count"] == 4
    assert placeholders["audit_event_card_count"] == 7
    assert placeholders["immutable_log_placeholder_created_count"] == 28
    assert placeholders["official_audit_log_written_count"] == 0
    assert placeholders["immutable_audit_written_count"] == 0
    assert placeholders["immutable_hash_chain_written_count"] == 0
    assert placeholders["timestamp_anchor_written_count"] == 0
    assert placeholders["tower_attestation_written_count"] == 0
    assert placeholders["official_receipt_claimed_count"] == 0
    assert placeholders["receipt_finalized_count"] == 0
    assert placeholders["receipt_closed_count"] == 0
    assert placeholders["access_granted_count"] == 0
    assert placeholders["provider_read_enabled_count"] == 0
    assert placeholders["object_body_view_enabled_count"] == 0
    assert placeholders["export_allowed_count"] == 0
    assert placeholders["external_delivery_allowed_count"] == 0
    assert placeholders["execution_allowed_count"] == 0
    assert placeholders["safe_to_continue_immutable_log_placeholders"] is True

    types = {item["placeholder_type"] for item in placeholders["immutable_log_placeholder_items"]}
    assert types == {
        "audit_chain_placeholder",
        "hash_chain_placeholder",
        "timestamp_anchor_placeholder",
        "tower_attestation_placeholder",
    }

    for item in placeholders["immutable_log_placeholder_items"]:
        assert item["immutable_log_placeholder_id"].startswith("VSAILP-")
        assert item["audit_event_card_id"].startswith("VSAE-")
        assert item["placeholder_status"] == "PLACEHOLDER_ONLY_NOT_WRITTEN"
        assert item["metadata_only"] is True
        assert item["immutable_log_placeholder_created"] is True
        assert item["official_audit_log_written"] is False
        assert item["immutable_audit_written"] is False
        assert item["immutable_hash_chain_written"] is False
        assert item["timestamp_anchor_written"] is False
        assert item["tower_attestation_written"] is False
        assert item["execution_allowed"] is False


def test_gp046_next_step_carries_forward_to_gp047_not_clouds():
    next_step = get_storage_audit_trail_next_step()["next_step"]

    assert next_step["next_step_count"] == 3
    assert next_step["ready_for_gp047_count"] == 3
    assert next_step["audit_event_card_count"] == 7
    assert next_step["denied_access_audit_row_count"] == 49
    assert next_step["tower_gate_audit_snapshot_count"] == 56
    assert next_step["receipt_preview_audit_link_count"] == 7
    assert next_step["immutable_log_placeholder_count"] == 28
    assert next_step["safe_to_continue_to_gp047"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False
    assert next_step["recommended_next_pack"] == "VAULT_GP047"
    assert next_step["recommended_next_pack_title"] == "Storage Audit Review Board"

    note = next_step["owner_notebook_note"].lower()
    assert "archive vault — next product depth layer" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "audit trail previews metadata-only" in rules
    assert "preview-only, not official" in rules
    assert "no immutable audit write claim" in rules
    assert "no official audit log claim" in rules
    assert "object body view locked" in rules
    assert "safe to continue, not vault done" in rules

    for item in next_step["next_step_items"]:
        assert item["next_step_id"].startswith("VSATPNX-")
        assert item["target_pack"] == "VAULT_GP047"
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False


def test_gp046_routes_and_counts_declared():
    home = get_storage_audit_trail_preview_home()
    routes = home["audit_routes"]
    counts = home["audit_counts"]

    assert routes["section_header"] == "Archive Vault — Next Product Depth Layer"
    assert routes["section_range"] == "GP041-GP050"
    assert routes["route"] == "/vault/storage-audit-trail-preview"
    assert routes["json_route"] == "/vault/storage-audit-trail-preview.json"
    assert routes["audit_event_cards_route"] == "/vault/storage-audit-event-cards.json"
    assert routes["denied_access_audit_rows_route"] == "/vault/storage-denied-access-audit-rows.json"
    assert routes["tower_gate_audit_snapshots_route"] == "/vault/storage-tower-gate-audit-snapshots.json"
    assert routes["receipt_preview_audit_links_route"] == "/vault/storage-receipt-preview-audit-links.json"
    assert routes["immutable_log_placeholders_route"] == "/vault/storage-immutable-log-placeholders.json"
    assert routes["next_step_route"] == "/vault/storage-audit-trail-next-step.json"
    assert routes["gp046_status_route"] == "/vault/gp046-status.json"

    assert counts["audit_event_card_count"] == 7
    assert counts["audit_event_type_count"] == 5
    assert counts["denied_access_audit_row_count"] == 49
    assert counts["tower_gate_audit_snapshot_count"] == 56
    assert counts["receipt_preview_audit_link_count"] == 7
    assert counts["immutable_log_placeholder_count"] == 28
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


def test_gp046_html_is_dark_and_has_no_white_background_tokens():
    html = render_storage_audit_trail_preview_page()
    lowered = html.lower()

    assert "Vault Storage Audit Trail Preview" in html
    assert "Archive Vault" in html
    assert "/vault/storage-audit-trail-preview.json" in html
    assert "/vault/gp046-status.json" in html
    assert "Clouds parked" in html
    assert "No official audit log" in html
    assert "No immutable audit write" in html
    assert "No object access" in html

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


def test_gp046_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-audit-trail-preview",
        "/vault/storage-audit-trail-preview.json",
        "/vault/storage-audit-event-cards.json",
        "/vault/storage-denied-access-audit-rows.json",
        "/vault/storage-tower-gate-audit-snapshots.json",
        "/vault/storage-receipt-preview-audit-links.json",
        "/vault/storage-immutable-log-placeholders.json",
        "/vault/storage-audit-trail-next-step.json",
        "/vault/gp046-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp046_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-audit-trail-preview",
        "/vault/storage-audit-trail-preview.json",
        "/vault/storage-audit-event-cards.json",
        "/vault/storage-denied-access-audit-rows.json",
        "/vault/storage-tower-gate-audit-snapshots.json",
        "/vault/storage-receipt-preview-audit-links.json",
        "/vault/storage-immutable-log-placeholders.json",
        "/vault/storage-audit-trail-next-step.json",
        "/vault/gp046-status.json",
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
                assert b"Vault Storage Audit Trail Preview" in response.data
