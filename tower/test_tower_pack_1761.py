"""
SEARCHABLE LABEL:
TOWER_PACK_1761_OPERATIONS_COMMAND_READINESS_TESTS
"""

import importlib


def test_pack_1761_ready():
    mod = importlib.import_module(
        "tower.tower_tower_beta_operations_command_readiness_command_matrix_v1761"
    )

    payload = mod.build_tower_beta_operations_command_readiness_command_matrix_preview()

    assert payload["pack"] == "1761"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-operations-command-readiness-command-matrix-v1761.json"
    assert payload["source_pack"] == "1760"
    assert payload["current_packs"] == "1759-1808"
    assert payload["save_block"] == "1759-1808"
    assert payload["next_pack"] == "1762"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True

    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_1762"] is True


def test_pack_1761_protocol_authority_and_locks():
    mod = importlib.import_module(
        "tower.tower_tower_beta_operations_command_readiness_command_matrix_v1761"
    )

    payload = mod.build_tower_beta_operations_command_readiness_command_matrix_preview()
    summary = payload["tower_beta_operations_command_readiness_command_matrix_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 155
    assert summary["check_count"] >= 45
    assert summary["command_category_count"] >= 34
    assert summary["command_item_count"] >= 58
    assert summary["blocked_real_action_count"] >= 65
    assert summary["tower_beta_operations_command_readiness_command_matrix_ready"] is True

    assert summary["tower_is_face"] is True
    assert summary["teller_is_workflow"] is True
    assert summary["vault_is_sealed_memory"] is True

    assert summary[
        "tower_is_only_vault_protocol_authority"
    ] is True

    assert summary[
        "teller_to_vault_direct_calls_allowed"
    ] is False

    assert summary[
        "user_to_vault_direct_calls_allowed"
    ] is False

    assert summary["vault_answers_tower_only"] is True

    assert summary["tower_controls_identity"] is True
    assert summary["tower_controls_roles"] is True
    assert summary["tower_controls_permissions"] is True
    assert summary["tower_controls_clearance"] is True
    assert summary["tower_controls_policy"] is True
    assert summary["tower_controls_step_up"] is True
    assert summary[
        "tower_controls_owner_admin_approval"
    ] is True
    assert summary["tower_controls_sessions"] is True
    assert summary["tower_controls_routes"] is True
    assert summary["tower_controls_objects"] is True
    assert summary["tower_controls_access"] is True
    assert summary["tower_controls_lockback"] is True
    assert summary[
        "tower_controls_protocol_selection"
    ] is True
    assert summary["tower_controls_redaction"] is True
    assert summary[
        "tower_controls_output_routing"
    ] is True

    assert summary[
        "real_operations_command_enabled"
    ] is False
    assert summary[
        "real_beta_operations_activation_enabled"
    ] is False
    assert summary["real_vault_request_enabled"] is False
    assert summary[
        "real_vault_status_request_enabled"
    ] is False
    assert summary[
        "real_vault_proof_request_enabled"
    ] is False
    assert summary[
        "real_vault_view_request_enabled"
    ] is False
    assert summary[
        "real_vault_preview_request_enabled"
    ] is False
    assert summary[
        "real_vault_download_request_enabled"
    ] is False
    assert summary[
        "real_vault_receipt_lookup_enabled"
    ] is False
    assert summary[
        "real_vault_rebuild_status_request_enabled"
    ] is False

    assert summary[
        "real_account_mutation_enabled"
    ] is False
    assert summary[
        "real_user_mutation_enabled"
    ] is False
    assert summary[
        "real_access_mutation_enabled"
    ] is False

    assert summary["raw_file_bytes_json_enabled"] is False
    assert summary["raw_file_url_enabled"] is False
    assert summary["raw_download_token_enabled"] is False
    assert summary["public_vault_link_enabled"] is False
    assert summary["shared_folder_browsing_enabled"] is False
    assert summary[
        "external_collaborator_browsing_enabled"
    ] is False

    assert summary["pivot_to_initial_setup"] is False
    assert summary["pivot_to_access_home"] is False
    assert summary["pivot_to_waitlist"] is False
    assert summary["pivot_to_admin_dashboard"] is False
    assert summary["save_push_performed"] is False


def test_pack_1761_bridge_prep_and_copy():
    mod = importlib.import_module(
        "tower.tower_tower_beta_operations_command_readiness_command_matrix_v1761"
    )

    bridge = mod.build_pack_1761_status_bridge()
    prep = mod.prepare_pack_1762_tower_beta_operations_command_readiness_detail_drawer()

    assert bridge["pack"] == "1761"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_operations_command_readiness_command_matrix_ready"] is True
    assert bridge["safe_to_continue_to_pack_1762"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1762"
    assert prep["source_pack"] == "1761"

    first = mod.build_tower_beta_operations_command_readiness_command_matrix_preview()
    second = mod.build_tower_beta_operations_command_readiness_command_matrix_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated"

    third = mod.build_tower_beta_operations_command_readiness_command_matrix_preview()
    assert third["status"] == "ready"
