"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_1045_1094_PACK_1066_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_1066_ready():
    mod = importlib.import_module("tower.tower_tower_beta_launch_authorization_review_blocker_review_registry_contract_v1066")
    payload = mod.build_tower_beta_launch_authorization_review_blocker_review_registry_contract_preview()

    assert payload["pack"] == "1066"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-launch-authorization-review-blocker-review-registry-contract-v1066.json"
    assert payload["source_pack"] == "1065"
    assert payload["current_packs"] == "1045-1094"
    assert payload["save_block"] == "1044-1094"
    assert payload["next_pack"] == "1067"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_1067"] is True


def test_pack_1066_summary_safety():
    mod = importlib.import_module("tower.tower_tower_beta_launch_authorization_review_blocker_review_registry_contract_v1066")
    payload = mod.build_tower_beta_launch_authorization_review_blocker_review_registry_contract_preview()
    summary = payload["tower_beta_launch_authorization_review_blocker_review_registry_contract_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 54
    assert summary["check_count"] >= 18
    assert summary["authorization_field_count"] >= 13
    assert summary["authorization_item_count"] >= 16
    assert summary["blocked_real_action_count"] >= 25
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_real_actions_disabled"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_beta_launch_authorization_review_blocker_review_registry_contract_ready"] is True
    assert summary["real_beta_launch_authorization_enabled"] is False
    assert summary["real_beta_launch_lock_release_enabled"] is False
    assert summary["real_final_owner_review_approval_enabled"] is False
    assert summary["real_release_candidate_approval_enabled"] is False
    assert summary["real_beta_go_decision_enabled"] is False
    assert summary["real_beta_unlock_enabled"] is False
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_1066_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_beta_launch_authorization_review_blocker_review_registry_contract_v1066")
    bridge = mod.build_pack_1066_status_bridge()
    prep = mod.prepare_pack_1067_tower_beta_launch_authorization_review_blocker_review_authorization_matrix()

    assert bridge["pack"] == "1066"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_launch_authorization_review_blocker_review_registry_contract_ready"] is True
    assert bridge["safe_to_continue_to_pack_1067"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1067"
    assert prep["source_pack"] == "1066"

    first = mod.build_tower_beta_launch_authorization_review_blocker_review_registry_contract_preview()
    second = mod.build_tower_beta_launch_authorization_review_blocker_review_registry_contract_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_beta_launch_authorization_review_blocker_review_registry_contract_preview()
    assert third["status"] == "ready"
