"""
SEARCHABLE LABEL:
TOWER_PACK_1758_BETA_OPERATIONS_COMMAND_READINESS_INDEX_TESTS
"""

from tower.tower_beta_operations_command_readiness_index_v1758 import (
    build_tower_beta_operations_command_readiness_index_preview,
    build_pack_1758_status_bridge,
    prepare_pack_1759_tower_beta_operations_command_readiness_registry_contract,
)


def test_pack_1758_ready():
    payload = build_tower_beta_operations_command_readiness_index_preview()

    assert payload["pack"] == "1758"
    assert payload["pack_number"] == 1758
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["source_block"] == "1707-1757"
    assert payload["source_pack"] == "1757"
    assert payload["next_pack"] == "1759"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["safe_to_continue_to_pack_1759"] is True


def test_pack_1758_protocol_authority_and_locks():
    payload = build_tower_beta_operations_command_readiness_index_preview()
    summary = payload["tower_pack_1758_summary"]

    assert summary["row_count"] >= 130
    assert summary["check_count"] >= 40
    assert summary["command_category_count"] >= 30
    assert summary["command_item_count"] >= 40
    assert summary["blocked_real_action_count"] >= 60
    assert summary["tower_pack_1758_ready"] is True

    assert summary["tower_is_face"] is True
    assert summary["teller_is_workflow"] is True
    assert summary["vault_is_sealed_memory"] is True

    assert summary["tower_is_only_vault_protocol_authority"] is True
    assert summary["teller_to_vault_direct_calls_allowed"] is False
    assert summary["user_to_vault_direct_calls_allowed"] is False
    assert summary["vault_answers_tower_only"] is True

    assert summary["tower_controls_identity"] is True
    assert summary["tower_controls_permissions"] is True
    assert summary["tower_controls_clearance"] is True
    assert summary["tower_controls_step_up"] is True
    assert summary["tower_controls_owner_admin_approval"] is True
    assert summary["tower_controls_policy"] is True
    assert summary["tower_controls_protocol_selection"] is True
    assert summary["tower_controls_redaction"] is True
    assert summary["tower_controls_output_type"] is True
    assert summary["tower_controls_request_receipts"] is True
    assert summary["tower_controls_security_receipts"] is True
    assert summary["tower_controls_denial_receipts"] is True

    assert summary["real_operations_command_enabled"] is False
    assert summary["real_beta_operations_activation_enabled"] is False
    assert summary["real_vault_request_enabled"] is False
    assert summary["real_vault_status_request_enabled"] is False
    assert summary["real_vault_proof_request_enabled"] is False
    assert summary["real_vault_view_request_enabled"] is False
    assert summary["real_vault_preview_request_enabled"] is False
    assert summary["real_vault_download_request_enabled"] is False
    assert summary["real_vault_receipt_lookup_enabled"] is False
    assert summary["real_vault_rebuild_status_request_enabled"] is False

    assert summary["raw_file_bytes_json_enabled"] is False
    assert summary["raw_file_url_enabled"] is False
    assert summary["raw_download_token_enabled"] is False
    assert summary["public_vault_link_enabled"] is False
    assert summary["shared_folder_browsing_enabled"] is False
    assert summary["external_collaborator_browsing_enabled"] is False

    assert summary["pivot_to_initial_setup"] is False
    assert summary["pivot_to_access_home"] is False
    assert summary["pivot_to_waitlist"] is False
    assert summary["pivot_to_admin_dashboard"] is False
    assert summary["save_push_performed"] is False


def test_pack_1758_bridge_prep_and_copy():
    bridge = build_pack_1758_status_bridge()
    prep = prepare_pack_1759_tower_beta_operations_command_readiness_registry_contract()

    assert bridge["pack"] == "1758"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_pack_1758_ready"] is True
    assert bridge["safe_to_continue_to_pack_1759"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1759"
    assert prep["source_pack"] == "1758"

    first = build_tower_beta_operations_command_readiness_index_preview()
    second = build_tower_beta_operations_command_readiness_index_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated"

    third = build_tower_beta_operations_command_readiness_index_preview()
    assert third["status"] == "ready"
