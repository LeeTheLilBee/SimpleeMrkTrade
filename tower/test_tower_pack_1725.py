"""
SEARCHABLE LABEL:
TOWER_PACK_1725_BETA_OPERATIONS_READINESS_TESTS
"""

import importlib


def test_pack_1725_ready():
    mod = importlib.import_module("tower.tower_tower_beta_operations_readiness_route_review_handoff_contract_v1725")
    payload = mod.build_tower_beta_operations_readiness_route_review_handoff_contract_preview()

    assert payload["pack"] == "1725"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-operations-readiness-route-review-handoff-contract-v1725.json"
    assert payload["source_pack"] == "1724"
    assert payload["current_packs"] == "1708-1757"
    assert payload["save_block"] == "1707-1757"
    assert payload["next_pack"] == "1726"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_1726"] is True


def test_pack_1725_protocol_authority_and_locks():
    mod = importlib.import_module("tower.tower_tower_beta_operations_readiness_route_review_handoff_contract_v1725")
    payload = mod.build_tower_beta_operations_readiness_route_review_handoff_contract_preview()
    summary = payload["tower_beta_operations_readiness_route_review_handoff_contract_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 130
    assert summary["check_count"] >= 35
    assert summary["operations_category_count"] >= 30
    assert summary["operations_item_count"] >= 40
    assert summary["blocked_real_action_count"] >= 60
    assert summary["tower_beta_operations_readiness_route_review_handoff_contract_ready"] is True

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
    assert summary["tower_controls_output_type"] is True
    assert summary["tower_controls_redaction"] is True
    assert summary["tower_controls_request_receipts"] is True

    assert summary["real_beta_operations_activation_enabled"] is False
    assert summary["real_vault_request_enabled"] is False
    assert summary["real_view_execution_enabled"] is False
    assert summary["real_download_execution_enabled"] is False
    assert summary["real_proof_execution_enabled"] is False
    assert summary["real_rebuild_status_execution_enabled"] is False

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


def test_pack_1725_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_beta_operations_readiness_route_review_handoff_contract_v1725")

    bridge = mod.build_pack_1725_status_bridge()
    prep = mod.prepare_pack_1726_tower_beta_operations_readiness_route_review_readiness_bridge()

    assert bridge["pack"] == "1725"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_operations_readiness_route_review_handoff_contract_ready"] is True
    assert bridge["safe_to_continue_to_pack_1726"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1726"
    assert prep["source_pack"] == "1725"

    first = mod.build_tower_beta_operations_readiness_route_review_handoff_contract_preview()
    second = mod.build_tower_beta_operations_readiness_route_review_handoff_contract_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated"

    third = mod.build_tower_beta_operations_readiness_route_review_handoff_contract_preview()
    assert third["status"] == "ready"
