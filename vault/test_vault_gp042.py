"""
Tests for VAULT GIANT PACK 042 — Storage Object Inventory Preview
"""

from pathlib import Path

import pytest

from vault.storage_object_inventory_preview_service import (
    get_gp042_status,
    get_storage_object_checksum_status,
    get_storage_object_inventory_home,
    get_storage_object_inventory_rows,
    get_storage_object_missing_warnings,
    get_storage_object_next_step,
    get_storage_object_provider_links,
    get_storage_object_status_labels,
    get_storage_object_tower_visibility_gates,
    render_storage_object_inventory_preview_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp042_status_ready_safe_continue_not_done():
    status = get_gp042_status()
    gp042 = status["gp042_status"]

    assert status["pack"]["id"] == "VAULT_GP042"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert status["pack"]["section_range"] == "GP041-GP050"

    assert gp042["ready"] is True
    assert gp042["section_id"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert gp042["section_title"] == "Archive Vault — Next Product Depth Layer"
    assert gp042["section_range"] == "GP041-GP050"
    assert gp042["storage_object_inventory_preview_ready"] is True
    assert gp042["safe_to_continue_to_gp043"] is True
    assert gp042["vault_done"] is False
    assert gp042["foundation_status"] == "safe_to_continue_not_done"
    assert gp042["metadata_only_inventory"] is True
    assert gp042["private_preview_only"] is True
    assert gp042["provider_selected"] is False
    assert gp042["provider_configured"] is False
    assert gp042["provider_write_enabled"] is False
    assert gp042["provider_read_enabled"] is False
    assert gp042["raw_file_body_storage_still_locked"] is True
    assert gp042["file_body_persisted_count"] == 0
    assert gp042["object_body_available_count"] == 0
    assert gp042["direct_upload_still_locked"] is True
    assert gp042["checksum_verification_not_claimed"] is True
    assert gp042["hash_verification_not_claimed"] is True
    assert gp042["external_delivery_still_locked"] is True
    assert gp042["packet_export_still_locked"] is True
    assert gp042["approval_disabled"] is True
    assert gp042["execution_engine_disabled"] is True
    assert gp042["clouds_status"] == "parked_do_not_continue_from_vault_gp042"
    assert gp042["next_pack"] == "VAULT_GP043_STORAGE_ACCESS_REQUEST_PREVIEW"


def test_gp042_inventory_truth_keeps_storage_locked():
    status = get_gp042_status()
    truth = status["inventory_truth"]

    assert truth["storage_object_inventory_preview_ready"] is True
    assert truth["inventory_rows_visible"] is True
    assert truth["storage_status_labels_visible"] is True
    assert truth["provider_placeholder_links_visible"] is True
    assert truth["checksum_pending_labels_visible"] is True
    assert truth["missing_object_warnings_visible"] is True
    assert truth["tower_visibility_gates_visible"] is True
    assert truth["metadata_only"] is True
    assert truth["private_preview_only"] is True

    assert truth["provider_selected"] is False
    assert truth["provider_configured"] is False
    assert truth["provider_write_enabled"] is False
    assert truth["provider_read_enabled"] is False
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["file_body_persisted_count"] == 0
    assert truth["direct_upload_unlocked"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["checksum_verified_count"] == 0
    assert truth["hash_verified_count"] == 0
    assert truth["object_body_available_count"] == 0
    assert truth["object_body_preview_allowed"] is False

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
    assert truth["safe_to_continue_to_gp043"] is True


def test_gp042_connected_to_gp041():
    home = get_storage_object_inventory_home()

    assert home["gp041_connection"]["gp041_ready"] is True
    assert home["gp041_connection"]["gp041_safe_to_continue"] is True
    assert home["gp041_connection"]["gp041_vault_done"] is False
    assert home["gp041_connection"]["gp041_section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert home["gp041_connection"]["gp041_provider_option_count"] == 4
    assert home["gp041_connection"]["gp041_object_key_placeholder_count"] == 7
    assert home["gp041_connection"]["gp041_checksum_placeholder_count"] == 7
    assert home["gp041_connection"]["gp041_boundary_violation_count"] == 0


def test_gp042_tower_authority_and_vault_boundaries():
    status = get_gp042_status()
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
    assert tower["vault_owns_tower_permissions"] is False
    assert tower["vault_can_override_tower_storage_authority"] is False
    assert tower["vault_can_override_tower_visibility"] is False

    assert vault["no_public_vault"] is True
    assert vault["direct_raw_upload_unlocked"] is False
    assert vault["permanent_file_body_storage_enabled"] is False
    assert vault["external_access_default"] == "denied"
    assert vault["external_packet_delivery_allowed"] is False
    assert vault["packet_export_allowed"] is False
    assert vault["unredacted_export_allowed"] is False
    assert vault["raw_export_allowed"] is False
    assert vault["redacted_owner_preview_allowed"] is True
    assert vault["object_body_preview_allowed"] is False
    assert vault["sensitive_body_display_in_summary_views"] is False
    assert vault["beneficiary_details_in_summary_views"] is False
    assert vault["broker_secret_storage_allowed"] is False
    assert vault["public_ob_proof_allowed"] is False
    assert vault["public_packet_proof_allowed"] is False
    assert vault["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp042_inventory_rows_metadata_only():
    rows = get_storage_object_inventory_rows()["inventory_rows"]

    assert rows["inventory_row_count"] == 7
    assert rows["metadata_only_row_count"] == 7
    assert rows["provider_placeholder_linked_count"] == 7
    assert rows["provider_selected_count"] == 0
    assert rows["provider_configured_count"] == 0
    assert rows["provider_write_enabled_count"] == 0
    assert rows["provider_read_enabled_count"] == 0
    assert rows["object_key_bound_to_provider_count"] == 0
    assert rows["file_body_persisted_count"] == 0
    assert rows["object_body_available_count"] == 0
    assert rows["object_body_preview_allowed_count"] == 0
    assert rows["raw_file_body_storage_enabled_count"] == 0
    assert rows["direct_upload_enabled_count"] == 0
    assert rows["checksum_present_count"] == 0
    assert rows["checksum_verified_count"] == 0
    assert rows["hash_verified_count"] == 0
    assert rows["external_delivery_allowed_count"] == 0
    assert rows["packet_export_allowed_count"] == 0
    assert rows["raw_export_allowed_count"] == 0
    assert rows["unredacted_export_allowed_count"] == 0
    assert rows["public_packet_proof_allowed_count"] == 0
    assert rows["portal_access_allowed_count"] == 0
    assert rows["tower_visibility_required_count"] == 7
    assert rows["tower_visibility_granted_count"] == 0
    assert rows["safe_to_continue_inventory_rows"] is True

    scopes = {item["scope"] for item in rows["inventory_row_items"]}
    assert scopes == {
        "document_intake",
        "attachment_registry",
        "requirement_match",
        "evidence_binder",
        "packet_workspace",
        "controlled_packet_assembly",
        "receipt_chain",
    }

    for item in rows["inventory_row_items"]:
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["object_key_contract_id"].startswith("VSOK-")
        assert item["checksum_placeholder_id"].startswith("VSCHK-")
        assert item["object_inventory_status"] == "EXPECTED_METADATA_ONLY_OBJECT_NOT_STORED"
        assert item["storage_status_label"] == "MISSING_OBJECT_BODY_PROVIDER_NOT_CONFIGURED"
        assert item["metadata_only"] is True
        assert item["private_preview_only"] is True
        assert item["provider_placeholder_linked"] is True
        assert item["provider_selected"] is False
        assert item["provider_configured"] is False
        assert item["provider_write_enabled"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_key_bound_to_provider"] is False
        assert item["file_body_persisted"] is False
        assert item["object_body_available"] is False
        assert item["object_body_preview_allowed"] is False
        assert item["raw_file_body_storage_enabled"] is False
        assert item["direct_upload_enabled"] is False
        assert item["checksum_present"] is False
        assert item["checksum_verified"] is False
        assert item["hash_verified"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["tower_visibility_required"] is True
        assert item["tower_visibility_granted"] is False
        assert item["safe_to_continue_to_gp043"] is True


def test_gp042_storage_status_labels_are_not_ready_for_raw_export_or_execution():
    labels = get_storage_object_status_labels()["status_labels"]

    assert labels["status_label_count"] == 7
    assert labels["ready_for_owner_preview_count"] == 7
    assert labels["ready_for_raw_view_count"] == 0
    assert labels["ready_for_provider_write_count"] == 0
    assert labels["ready_for_export_count"] == 0
    assert labels["ready_for_external_delivery_count"] == 0
    assert labels["ready_for_public_proof_count"] == 0
    assert labels["ready_for_execution_count"] == 0
    assert labels["safe_to_continue_status_labels"] is True

    for item in labels["status_label_items"]:
        assert item["status_label_id"].startswith("VSOSL-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["storage_status_label"] == "MISSING_OBJECT_BODY_PROVIDER_NOT_CONFIGURED"
        assert item["owner_label"] == "Missing object body — provider not configured"
        assert item["metadata_only"] is True
        assert item["ready_for_owner_preview"] is True
        assert item["ready_for_raw_view"] is False
        assert item["ready_for_provider_write"] is False
        assert item["ready_for_export"] is False
        assert item["ready_for_external_delivery"] is False
        assert item["ready_for_public_proof"] is False
        assert item["ready_for_execution"] is False


def test_gp042_provider_links_placeholder_only():
    links = get_storage_object_provider_links()["provider_links"]

    assert links["provider_link_count"] == 28
    assert links["inventory_row_count"] == 7
    assert links["provider_option_count"] == 4
    assert links["provider_selected_count"] == 0
    assert links["provider_configured_count"] == 0
    assert links["provider_write_enabled_count"] == 0
    assert links["provider_read_enabled_count"] == 0
    assert links["object_key_bound_to_provider_count"] == 0
    assert links["file_body_persisted_count"] == 0
    assert links["external_delivery_enabled_count"] == 0
    assert links["packet_export_enabled_count"] == 0
    assert links["tower_authorization_required_count"] == 28
    assert links["tower_authorized_count"] == 0
    assert links["safe_to_continue_provider_links"] is True

    for item in links["provider_link_items"]:
        assert item["provider_link_id"].startswith("VSPL-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["provider_option_id"].startswith("VSP-")
        assert item["provider_link_status"] == "PLACEHOLDER_LINK_NOT_SELECTED_NOT_CONFIGURED"
        assert item["metadata_only"] is True
        assert item["provider_selected"] is False
        assert item["provider_configured"] is False
        assert item["provider_write_enabled"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_key_bound_to_provider"] is False
        assert item["file_body_persisted"] is False
        assert item["external_delivery_enabled"] is False
        assert item["packet_export_enabled"] is False
        assert item["tower_authorization_required"] is True
        assert item["tower_authorized"] is False
        assert item["safe_to_continue_to_gp043"] is True


def test_gp042_checksum_status_pending_not_verified():
    status = get_storage_object_checksum_status()["checksum_status"]

    assert status["checksum_status_count"] == 7
    assert status["checksum_present_count"] == 0
    assert status["checksum_verified_count"] == 0
    assert status["hash_verified_count"] == 0
    assert status["file_body_persisted_count"] == 0
    assert status["raw_body_available_count"] == 0
    assert status["direct_upload_enabled_count"] == 0
    assert status["provider_configured_count"] == 0
    assert status["verification_claimed_count"] == 0
    assert status["safe_to_continue_checksum_status"] is True

    for item in status["checksum_status_items"]:
        assert item["checksum_status_id"].startswith("VSCS-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["checksum_placeholder_id"].startswith("VSCHK-")
        assert item["checksum_status_label"] == "CHECKSUM_PENDING_NOT_PRESENT_NOT_VERIFIED"
        assert item["hash_status_label"] == "HASH_PENDING_NOT_VERIFIED"
        assert item["hash_algorithm_placeholder"] == "sha256_placeholder_not_verified"
        assert item["metadata_only"] is True
        assert item["checksum_present"] is False
        assert item["checksum_verified"] is False
        assert item["hash_verified"] is False
        assert item["file_body_persisted"] is False
        assert item["raw_body_available"] is False
        assert item["direct_upload_enabled"] is False
        assert item["provider_configured"] is False
        assert item["verification_claimed"] is False
        assert item["safe_to_continue_to_gp043"] is True


def test_gp042_missing_warnings_block_restricted_paths():
    warnings = get_storage_object_missing_warnings()["missing_warnings"]

    assert warnings["missing_warning_count"] == 35
    assert warnings["warning_type_count"] == 5
    assert warnings["inventory_row_count"] == 7
    assert warnings["blocks_raw_view_count"] == 35
    assert warnings["blocks_provider_write_count"] == 35
    assert warnings["blocks_export_count"] == 35
    assert warnings["blocks_external_delivery_count"] == 35
    assert warnings["blocks_public_proof_count"] == 35
    assert warnings["blocks_execution_count"] == 35
    assert warnings["owner_resolvable_now_count"] == 0
    assert warnings["tower_authorization_required_count"] == 35
    assert warnings["safe_to_continue_missing_warnings"] is True

    types = {item["warning_type"] for item in warnings["missing_warning_items"]}
    assert types == {
        "provider_not_selected",
        "provider_not_configured",
        "file_body_not_persisted",
        "checksum_not_verified",
        "direct_upload_locked",
    }

    for item in warnings["missing_warning_items"]:
        assert item["missing_warning_id"].startswith("VSOW-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["warning_status"] == "ACTIVE_METADATA_ONLY_WARNING"
        assert item["metadata_only"] is True
        assert item["blocks_raw_view"] is True
        assert item["blocks_provider_write"] is True
        assert item["blocks_export"] is True
        assert item["blocks_external_delivery"] is True
        assert item["blocks_public_proof"] is True
        assert item["blocks_execution"] is True
        assert item["owner_resolvable_now"] is False
        assert item["tower_authorization_required"] is True


def test_gp042_tower_visibility_gates_required_not_granted():
    gates = get_storage_object_tower_visibility_gates()["tower_visibility_gates"]

    assert gates["tower_visibility_gate_count"] == 49
    assert gates["visibility_gate_type_count"] == 7
    assert gates["inventory_row_count"] == 7
    assert gates["required_gate_count"] == 49
    assert gates["granted_gate_count"] == 0
    assert gates["vault_override_allowed_count"] == 0
    assert gates["owner_redacted_preview_allowed_count"] == 7
    assert gates["raw_view_allowed_count"] == 0
    assert gates["sensitive_visibility_allowed_count"] == 0
    assert gates["export_allowed_count"] == 0
    assert gates["external_access_allowed_count"] == 0
    assert gates["portal_access_allowed_count"] == 0
    assert gates["tower_visibility_preserved"] is True
    assert gates["safe_to_continue_tower_visibility_gates"] is True

    gate_names = {item["gate_name"] for item in gates["tower_visibility_gate_items"]}
    assert "owner_redacted_preview" in gate_names
    assert "tower_sensitive_visibility" in gate_names
    assert "export_lock" in gate_names
    assert "external_access_lock" in gate_names
    assert "portal_access_lock" in gate_names

    for item in gates["tower_visibility_gate_items"]:
        assert item["visibility_gate_id"].startswith("VSOVG-")
        assert item["inventory_row_id"].startswith("VSOI-")
        assert item["gate_status"] == "TOWER_VISIBILITY_REQUIRED_NOT_GRANTED"
        assert item["metadata_only"] is True
        assert item["required"] is True
        assert item["granted"] is False
        assert item["vault_can_override"] is False
        assert item["raw_view_allowed"] is False
        assert item["sensitive_visibility_allowed"] is False
        assert item["export_allowed"] is False
        assert item["external_access_allowed"] is False
        assert item["portal_access_allowed"] is False


def test_gp042_next_step_carries_forward_to_gp043_not_clouds():
    next_step = get_storage_object_next_step()["next_step"]

    assert next_step["next_step_count"] == 3
    assert next_step["ready_for_gp043_count"] == 3
    assert next_step["inventory_row_count"] == 7
    assert next_step["provider_link_count"] == 28
    assert next_step["checksum_status_count"] == 7
    assert next_step["missing_warning_count"] == 35
    assert next_step["tower_visibility_gate_count"] == 49
    assert next_step["safe_to_continue_to_gp043"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False
    assert next_step["recommended_next_pack"] == "VAULT_GP043"
    assert next_step["recommended_next_pack_title"] == "Storage Access Request Preview"

    note = next_step["owner_notebook_note"].lower()
    assert "archive vault — next product depth layer" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "metadata-only" in rules
    assert "provider write/read locked" in rules
    assert "raw file body storage locked" in rules
    assert "direct upload locked" in rules
    assert "checksum/hash verification unclaimed" in rules
    assert "safe to continue, not vault done" in rules

    for item in next_step["next_step_items"]:
        assert item["next_step_id"].startswith("VSONX-")
        assert item["target_pack"] == "VAULT_GP043"
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False


def test_gp042_routes_and_counts_declared():
    home = get_storage_object_inventory_home()
    routes = home["inventory_routes"]
    counts = home["inventory_counts"]

    assert routes["section_header"] == "Archive Vault — Next Product Depth Layer"
    assert routes["section_range"] == "GP041-GP050"
    assert routes["route"] == "/vault/storage-object-inventory"
    assert routes["json_route"] == "/vault/storage-object-inventory.json"
    assert routes["inventory_rows_route"] == "/vault/storage-object-inventory-rows.json"
    assert routes["status_labels_route"] == "/vault/storage-object-status-labels.json"
    assert routes["provider_links_route"] == "/vault/storage-object-provider-links.json"
    assert routes["checksum_status_route"] == "/vault/storage-object-checksum-status.json"
    assert routes["missing_warnings_route"] == "/vault/storage-object-missing-warnings.json"
    assert routes["tower_visibility_gates_route"] == "/vault/storage-object-tower-visibility-gates.json"
    assert routes["next_step_route"] == "/vault/storage-object-next-step.json"
    assert routes["gp042_status_route"] == "/vault/gp042-status.json"

    assert counts["inventory_row_count"] == 7
    assert counts["status_label_count"] == 7
    assert counts["provider_link_count"] == 28
    assert counts["checksum_status_count"] == 7
    assert counts["missing_warning_count"] == 35
    assert counts["tower_visibility_gate_count"] == 49
    assert counts["file_body_persisted_count"] == 0
    assert counts["object_body_available_count"] == 0
    assert counts["provider_selected_count"] == 0
    assert counts["provider_configured_count"] == 0
    assert counts["provider_write_enabled_count"] == 0
    assert counts["provider_read_enabled_count"] == 0
    assert counts["checksum_verified_count"] == 0
    assert counts["hash_verified_count"] == 0
    assert counts["raw_file_body_storage_enabled_count"] == 0
    assert counts["direct_upload_unlocked_count"] == 0
    assert counts["external_delivery_allowed_count"] == 0
    assert counts["packet_export_allowed_count"] == 0
    assert counts["execution_allowed_count"] == 0
    assert counts["metadata_only"] is True


def test_gp042_html_is_dark_and_has_no_white_background_tokens():
    html = render_storage_object_inventory_preview_page()
    lowered = html.lower()

    assert "Vault Storage Object Inventory Preview" in html
    assert "Archive Vault" in html
    assert "/vault/storage-object-inventory.json" in html
    assert "/vault/gp042-status.json" in html
    assert "Clouds parked" in html
    assert "No object bodies" in html
    assert "No provider write/read" in html

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


def test_gp042_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-object-inventory",
        "/vault/storage-object-inventory.json",
        "/vault/storage-object-inventory-rows.json",
        "/vault/storage-object-status-labels.json",
        "/vault/storage-object-provider-links.json",
        "/vault/storage-object-checksum-status.json",
        "/vault/storage-object-missing-warnings.json",
        "/vault/storage-object-tower-visibility-gates.json",
        "/vault/storage-object-next-step.json",
        "/vault/gp042-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp042_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-object-inventory",
        "/vault/storage-object-inventory.json",
        "/vault/storage-object-inventory-rows.json",
        "/vault/storage-object-status-labels.json",
        "/vault/storage-object-provider-links.json",
        "/vault/storage-object-checksum-status.json",
        "/vault/storage-object-missing-warnings.json",
        "/vault/storage-object-tower-visibility-gates.json",
        "/vault/storage-object-next-step.json",
        "/vault/gp042-status.json",
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
                assert b"Vault Storage Object Inventory Preview" in response.data
