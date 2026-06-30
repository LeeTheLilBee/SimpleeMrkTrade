"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_841_890_PACK_872_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_872_ready():
    mod = importlib.import_module("tower.tower_tower_beta_owner_go_no_go_owner_summary_registry_contract_v872")
    payload = mod.build_tower_beta_owner_go_no_go_owner_summary_registry_contract_preview()

    assert payload["pack"] == "872"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-owner-go-no-go-owner-summary-registry-contract-v872.json"
    assert payload["source_pack"] == "871"
    assert payload["current_packs"] == "841-890"
    assert payload["save_block"] == "840-890"
    assert payload["next_pack"] == "873"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_873"] is True


def test_pack_872_summary_safety():
    mod = importlib.import_module("tower.tower_tower_beta_owner_go_no_go_owner_summary_registry_contract_v872")
    payload = mod.build_tower_beta_owner_go_no_go_owner_summary_registry_contract_preview()
    summary = payload["tower_beta_owner_go_no_go_owner_summary_registry_contract_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 45
    assert summary["check_count"] >= 14
    assert summary["go_no_go_field_count"] >= 12
    assert summary["go_no_go_item_count"] >= 12
    assert summary["blocked_real_action_count"] >= 21
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_real_actions_disabled"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_beta_owner_go_no_go_owner_summary_registry_contract_ready"] is True
    assert summary["real_go_decision_enabled"] is False
    assert summary["real_beta_unlock_enabled"] is False
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_872_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_beta_owner_go_no_go_owner_summary_registry_contract_v872")
    bridge = mod.build_pack_872_status_bridge()
    prep = mod.prepare_pack_873_tower_beta_owner_go_no_go_owner_summary_go_no_go_matrix()

    assert bridge["pack"] == "872"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_owner_go_no_go_owner_summary_registry_contract_ready"] is True
    assert bridge["safe_to_continue_to_pack_873"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "873"
    assert prep["source_pack"] == "872"

    first = mod.build_tower_beta_owner_go_no_go_owner_summary_registry_contract_preview()
    second = mod.build_tower_beta_owner_go_no_go_owner_summary_registry_contract_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_beta_owner_go_no_go_owner_summary_registry_contract_preview()
    assert third["status"] == "ready"
