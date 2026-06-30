"""
Tests for VAULT GIANT PACK 041 — Storage Provider Contract Starter
"""

from pathlib import Path

import pytest

from vault.storage_provider_contract_starter_service import (
    get_gp041_status,
    get_storage_object_key_contract,
    get_storage_provider_boundary_check,
    get_storage_provider_contract_home,
    get_storage_provider_next_step,
    get_storage_provider_options,
    get_storage_provider_tower_gates,
    get_storage_retention_redaction_gates,
    render_storage_provider_contract_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp041_status_ready_new_section_safe_to_continue_not_done():
    status = get_gp041_status()
    gp041 = status["gp041_status"]

    assert status["pack"]["id"] == "VAULT_GP041"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert status["pack"]["section_range"] == "GP041-GP050"
    assert status["pack"]["new_section_start"] is True

    assert gp041["ready"] is True
    assert gp041["section_id"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert gp041["section_title"] == "Archive Vault — Next Product Depth Layer"
    assert gp041["section_range"] == "GP041-GP050"
    assert gp041["new_section_started"] is True
    assert gp041["started_after_gp040"] is True
    assert gp041["storage_provider_contract_starter_ready"] is True
    assert gp041["safe_to_continue_to_gp042"] is True
    assert gp041["vault_done"] is False
    assert gp041["foundation_status"] == "safe_to_continue_not_done"
    assert gp041["metadata_only_contract"] is True
    assert gp041["private_contract_only"] is True
    assert gp041["provider_selected"] is False
    assert gp041["provider_configured"] is False
    assert gp041["provider_write_enabled"] is False
    assert gp041["provider_read_enabled"] is False
    assert gp041["raw_file_body_storage_still_locked"] is True
    assert gp041["direct_upload_still_locked"] is True
    assert gp041["checksum_verification_not_claimed"] is True
    assert gp041["hash_verification_not_claimed"] is True
    assert gp041["external_delivery_still_locked"] is True
    assert gp041["packet_export_still_locked"] is True
    assert gp041["approval_disabled"] is True
    assert gp041["execution_engine_disabled"] is True
    assert gp041["clouds_status"] == "parked_do_not_continue_from_vault_gp041"
    assert gp041["next_pack"] == "VAULT_GP042_STORAGE_OBJECT_INVENTORY_PREVIEW"


def test_gp041_contract_truth_keeps_storage_locked():
    status = get_gp041_status()
    truth = status["contract_truth"]

    assert truth["storage_provider_contract_started"] is True
    assert truth["storage_provider_contract_ready"] is True
    assert truth["provider_options_visible"] is True
    assert truth["object_key_contract_visible"] is True
    assert truth["checksum_placeholder_contract_visible"] is True
    assert truth["retention_redaction_gates_visible"] is True
    assert truth["tower_storage_gates_visible"] is True
    assert truth["boundary_check_visible"] is True
    assert truth["metadata_only"] is True
    assert truth["private_contract_only"] is True

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
    assert truth["safe_to_continue_to_gp042"] is True


def test_gp041_section_context_connected_to_gp040():
    home = get_storage_provider_contract_home()

    assert home["section_context"]["current_section_id"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert home["section_context"]["current_section_range"] == "GP041-GP050"
    assert home["section_context"]["previous_section_id"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert home["section_context"]["previous_section_range"] == "GP031-GP040"
    assert home["section_context"]["started_after_gp040"] is True
    assert home["section_context"]["gp040_checkpoint_required"] is True
    assert home["section_context"]["gp040_checkpoint_connected"] is True
    assert home["section_context"]["clouds_parked"] is True
    assert home["section_context"]["vault_done"] is False

    assert home["gp040_connection"]["gp040_ready"] is True
    assert home["gp040_connection"]["gp040_safe_to_continue"] is True
    assert home["gp040_connection"]["gp040_vault_done"] is False
    assert home["gp040_connection"]["gp040_section_checkpoint_complete"] is True
    assert home["gp040_connection"]["gp040_new_section_starts_after_this_pack"] is True


def test_gp041_tower_authority_and_vault_boundaries():
    status = get_gp041_status()
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
    assert tower["vault_owns_tower_permissions"] is False
    assert tower["vault_can_override_tower_storage_authority"] is False

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


def test_gp041_provider_options_are_placeholders_only():
    providers = get_storage_provider_options()["provider_options"]

    assert providers["provider_option_count"] == 4
    assert providers["provider_selected_count"] == 0
    assert providers["provider_configured_count"] == 0
    assert providers["provider_write_enabled_count"] == 0
    assert providers["provider_read_enabled_count"] == 0
    assert providers["raw_file_body_storage_enabled_count"] == 0
    assert providers["direct_upload_enabled_count"] == 0
    assert providers["external_delivery_enabled_count"] == 0
    assert providers["packet_export_enabled_count"] == 0
    assert providers["public_proof_enabled_count"] == 0
    assert providers["portal_access_enabled_count"] == 0
    assert providers["tower_authorization_required_count"] == 4
    assert providers["tower_authorized_count"] == 0
    assert providers["owner_confirmed_count"] == 0
    assert providers["safe_to_select_now_count"] == 0
    assert providers["safe_to_configure_now_count"] == 0
    assert providers["safe_to_write_now_count"] == 0
    assert providers["safe_to_continue_provider_options"] is True

    ids = {item["provider_id"] for item in providers["provider_option_items"]}
    assert "VAULT_PROVIDER_LOCAL_ENCRYPTED_PLACEHOLDER" in ids
    assert "VAULT_PROVIDER_OBJECT_STORAGE_PLACEHOLDER" in ids
    assert "VAULT_PROVIDER_DRIVE_ARCHIVE_PLACEHOLDER" in ids
    assert "VAULT_PROVIDER_TOWER_MANAGED_PLACEHOLDER" in ids

    for item in providers["provider_option_items"]:
        assert item["provider_option_id"].startswith("VSP-")
        assert item["contract_status"] == "PLACEHOLDER_NOT_SELECTED_NOT_CONFIGURED"
        assert item["metadata_only"] is True
        assert item["provider_selected"] is False
        assert item["provider_configured"] is False
        assert item["provider_write_enabled"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_delete_enabled"] is False
        assert item["raw_file_body_storage_enabled"] is False
        assert item["direct_upload_enabled"] is False
        assert item["external_delivery_enabled"] is False
        assert item["packet_export_enabled"] is False
        assert item["public_proof_enabled"] is False
        assert item["portal_access_enabled"] is False
        assert item["tower_authorization_required"] is True
        assert item["tower_authorized"] is False
        assert item["safe_to_select_now"] is False
        assert item["safe_to_configure_now"] is False
        assert item["safe_to_write_now"] is False
        assert item["safe_to_continue_to_gp042"] is True


def test_gp041_object_key_contract_metadata_only():
    contract = get_storage_object_key_contract()["object_key_contract"]

    assert contract["object_key_scope_count"] == 7
    assert contract["object_key_placeholder_count"] == 7
    assert contract["checksum_placeholder_count"] == 7
    assert contract["object_key_bound_to_provider_count"] == 0
    assert contract["provider_selected_count"] == 0
    assert contract["provider_configured_count"] == 0
    assert contract["file_body_persisted_count"] == 0
    assert contract["raw_body_available_count"] == 0
    assert contract["checksum_present_count"] == 0
    assert contract["checksum_verified_count"] == 0
    assert contract["hash_verified_count"] == 0
    assert contract["direct_upload_enabled_count"] == 0
    assert contract["external_delivery_enabled_count"] == 0
    assert contract["packet_export_enabled_count"] == 0
    assert contract["safe_to_continue_object_key_contract"] is True

    scopes = {item["scope"] for item in contract["object_key_contract_items"]}
    assert scopes == {
        "document_intake",
        "attachment_registry",
        "requirement_match",
        "evidence_binder",
        "packet_workspace",
        "controlled_packet_assembly",
        "receipt_chain",
    }

    for item in contract["object_key_contract_items"]:
        assert item["object_key_contract_id"].startswith("VSOK-")
        assert item["checksum_placeholder_id"].startswith("VSCHK-")
        assert item["hash_algorithm_placeholder"] == "sha256_placeholder_not_verified"
        assert item["metadata_only"] is True
        assert item["object_key_placeholder_only"] is True
        assert item["object_key_bound_to_provider"] is False
        assert item["provider_selected"] is False
        assert item["provider_configured"] is False
        assert item["file_body_persisted"] is False
        assert item["raw_body_available"] is False
        assert item["checksum_present"] is False
        assert item["checksum_verified"] is False
        assert item["hash_verified"] is False
        assert item["direct_upload_enabled"] is False
        assert item["external_delivery_enabled"] is False
        assert item["packet_export_enabled"] is False
        assert item["tower_authorization_required"] is True
        assert item["safe_to_continue_to_gp042"] is True


def test_gp041_retention_redaction_gates_are_locked():
    gates = get_storage_retention_redaction_gates()["retention_redaction_gates"]

    assert gates["retention_gate_count"] == 3
    assert gates["redaction_gate_count"] == 3
    assert gates["active_retention_policy_count"] == 0
    assert gates["raw_view_allowed_count"] == 0
    assert gates["unredacted_export_allowed_count"] == 0
    assert gates["packet_export_allowed_count"] == 0
    assert gates["redacted_preview_allowed_count"] == 3
    assert gates["tower_authorization_required_count"] == 6
    assert gates["safe_to_continue_retention_redaction_gates"] is True

    for item in gates["retention_gate_items"]:
        assert item["retention_gate_id"].startswith("VSRG-")
        assert item["metadata_only"] is True
        assert item["policy_active"] is False
        assert item["owner_review_required"] is True
        assert item["tower_authorization_required"] is True

    for item in gates["redaction_gate_items"]:
        assert item["redaction_gate_id"].startswith("VSRD-")
        assert item["metadata_only"] is True
        assert item["redacted_preview_allowed"] is True
        assert item["raw_view_allowed"] is False
        assert item["unredacted_export_allowed"] is False
        assert item["tower_authorization_required"] is True


def test_gp041_tower_storage_gates_required_not_granted():
    gates = get_storage_provider_tower_gates()["tower_gates"]

    assert gates["tower_gate_count"] == 10
    assert gates["required_gate_count"] == 10
    assert gates["granted_gate_count"] == 0
    assert gates["vault_override_allowed_count"] == 0
    assert gates["provider_selected_count"] == 0
    assert gates["provider_configured_count"] == 0
    assert gates["write_enabled_count"] == 0
    assert gates["external_delivery_enabled_count"] == 0
    assert gates["export_enabled_count"] == 0
    assert gates["tower_authority_preserved"] is True
    assert gates["safe_to_continue_tower_gates"] is True

    names = {item["gate_name"] for item in gates["tower_gate_items"]}
    assert "storage_provider_authorization_required" in names
    assert "export_lock_required" in names
    assert "external_access_lock_required" in names

    for item in gates["tower_gate_items"]:
        assert item["tower_gate_id"].startswith("VSTG-")
        assert item["gate_status"] == "TOWER_REQUIRED_NOT_GRANTED"
        assert item["metadata_only"] is True
        assert item["required"] is True
        assert item["granted"] is False
        assert item["vault_can_override"] is False
        assert item["provider_selected"] is False
        assert item["provider_configured"] is False
        assert item["write_enabled"] is False
        assert item["external_delivery_enabled"] is False
        assert item["export_enabled"] is False


def test_gp041_boundary_check_all_locked():
    boundary = get_storage_provider_boundary_check()["boundary_check"]

    assert boundary["boundary_lock_count"] >= 25
    assert boundary["boundary_violation_count"] == 0
    assert boundary["all_boundaries_locked"] is True
    assert boundary["all_restricted_paths_locked"] is True
    assert boundary["gp040_boundary_violation_count"] == 0
    assert boundary["gp040_safe_to_continue"] is True

    assert boundary["raw_file_body_storage_locked"] is True
    assert boundary["direct_upload_locked"] is True
    assert boundary["provider_selected_locked"] is True
    assert boundary["provider_configured_locked"] is True
    assert boundary["provider_write_enabled_locked"] is True
    assert boundary["checksum_verified_not_claimed"] is True
    assert boundary["file_body_persisted_count"] == 0
    assert boundary["external_packet_delivery_locked"] is True
    assert boundary["external_access_locked"] is True
    assert boundary["packet_export_locked"] is True
    assert boundary["unredacted_export_locked"] is True
    assert boundary["raw_export_locked"] is True
    assert boundary["public_proof_locked"] is True
    assert boundary["public_packet_proof_locked"] is True
    assert boundary["portal_access_locked"] is True
    assert boundary["approval_locked"] is True
    assert boundary["execution_engine_locked"] is True
    assert boundary["auto_action_execution_locked"] is True
    assert boundary["receipt_close_locked"] is True
    assert boundary["receipt_finalization_locked"] is True
    assert boundary["vault_done_false"] is True
    assert boundary["clouds_parked"] is True
    assert boundary["safe_to_continue_boundary_check"] is True

    for item in boundary["boundary_check_items"]:
        assert item["boundary_check_id"].startswith("VSPBC-")
        assert item["expected_state"] == "locked_or_false"
        assert item["actual_state"] == "locked_or_false"
        assert item["locked"] is True
        assert item["violation"] is False
        assert item["metadata_only"] is True
        assert item["tower_owned_when_applicable"] is True
        assert item["vault_override_allowed"] is False


def test_gp041_next_step_carries_forward_to_gp042_not_clouds():
    next_step = get_storage_provider_next_step()["next_step"]

    assert next_step["next_step_count"] == 3
    assert next_step["ready_for_gp042_count"] == 3
    assert next_step["provider_option_count"] == 4
    assert next_step["object_key_placeholder_count"] == 7
    assert next_step["boundary_violation_count"] == 0
    assert next_step["safe_to_continue_to_gp042"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False
    assert next_step["recommended_next_pack"] == "VAULT_GP042"
    assert next_step["recommended_next_pack_title"] == "Storage Object Inventory Preview"

    note = next_step["owner_notebook_note"].lower()
    assert "archive vault — next product depth layer" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "tower authority" in rules
    assert "raw file body storage locked" in rules
    assert "direct upload locked" in rules
    assert "checksum/hash verification unclaimed" in rules
    assert "safe to continue, not vault done" in rules

    for item in next_step["next_step_items"]:
        assert item["next_step_id"].startswith("VSPNX-")
        assert item["target_pack"] == "VAULT_GP042"
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False


def test_gp041_routes_and_counts_declared():
    home = get_storage_provider_contract_home()
    routes = home["contract_routes"]
    counts = home["contract_counts"]

    assert routes["section_header"] == "Archive Vault — Next Product Depth Layer"
    assert routes["section_range"] == "GP041-GP050"
    assert routes["route"] == "/vault/storage-provider-contract"
    assert routes["json_route"] == "/vault/storage-provider-contract.json"
    assert routes["provider_options_route"] == "/vault/storage-provider-options.json"
    assert routes["object_key_contract_route"] == "/vault/storage-object-key-contract.json"
    assert routes["retention_redaction_gates_route"] == "/vault/storage-retention-redaction-gates.json"
    assert routes["tower_gates_route"] == "/vault/storage-provider-tower-gates.json"
    assert routes["boundary_check_route"] == "/vault/storage-provider-boundary-check.json"
    assert routes["next_step_route"] == "/vault/storage-provider-next-step.json"
    assert routes["gp041_status_route"] == "/vault/gp041-status.json"

    assert counts["provider_option_count"] == 4
    assert counts["provider_selected_count"] == 0
    assert counts["provider_configured_count"] == 0
    assert counts["object_key_scope_count"] == 7
    assert counts["object_key_placeholder_count"] == 7
    assert counts["checksum_placeholder_count"] == 7
    assert counts["retention_gate_count"] == 3
    assert counts["redaction_gate_count"] == 3
    assert counts["tower_gate_count"] == 10
    assert counts["boundary_violation_count"] == 0
    assert counts["file_body_persisted_count"] == 0
    assert counts["checksum_verified_count"] == 0
    assert counts["raw_file_body_storage_enabled_count"] == 0
    assert counts["direct_upload_unlocked_count"] == 0
    assert counts["external_delivery_allowed_count"] == 0
    assert counts["packet_export_allowed_count"] == 0
    assert counts["execution_allowed_count"] == 0
    assert counts["metadata_only"] is True


def test_gp041_html_is_dark_and_has_no_white_background_tokens():
    html = render_storage_provider_contract_page()
    lowered = html.lower()

    assert "Vault Storage Provider Contract Starter" in html
    assert "Archive Vault" in html
    assert "/vault/storage-provider-contract.json" in html
    assert "/vault/gp041-status.json" in html
    assert "Clouds parked" in html
    assert "No raw storage" in html
    assert "No direct upload" in html

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


def test_gp041_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-provider-contract",
        "/vault/storage-provider-contract.json",
        "/vault/storage-provider-options.json",
        "/vault/storage-object-key-contract.json",
        "/vault/storage-retention-redaction-gates.json",
        "/vault/storage-provider-tower-gates.json",
        "/vault/storage-provider-boundary-check.json",
        "/vault/storage-provider-next-step.json",
        "/vault/gp041-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp041_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-provider-contract",
        "/vault/storage-provider-contract.json",
        "/vault/storage-provider-options.json",
        "/vault/storage-object-key-contract.json",
        "/vault/storage-retention-redaction-gates.json",
        "/vault/storage-provider-tower-gates.json",
        "/vault/storage-provider-boundary-check.json",
        "/vault/storage-provider-next-step.json",
        "/vault/gp041-status.json",
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
                assert b"Vault Storage Provider Contract Starter" in response.data
