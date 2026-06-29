"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_689_738_PACK_709_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_709_ready():
    mod = importlib.import_module("tower.tower_tower_capital_safety_next_action_bridge_index_v709")
    payload = mod.build_tower_capital_safety_next_action_bridge_index_preview()

    assert payload["pack"] == "709"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-capital-safety-next-action-bridge-index-v709.json"
    assert payload["source_pack"] == "708"
    assert payload["current_packs"] == "689-738"
    assert payload["save_block"] == "688-738"
    assert payload["next_pack"] == "710"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_710"] is True


def test_pack_709_summary_safety():
    mod = importlib.import_module("tower.tower_tower_capital_safety_next_action_bridge_index_v709")
    payload = mod.build_tower_capital_safety_next_action_bridge_index_preview()
    summary = payload["tower_capital_safety_next_action_bridge_index_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 40
    assert summary["check_count"] >= 13
    assert summary["action_field_count"] >= 12
    assert summary["focus_queue_item_count"] >= 8
    assert summary["blocked_real_action_count"] >= 20
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["no_focus_publish"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_capital_safety_next_action_bridge_index_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["real_focus_queue_publish_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_709_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_capital_safety_next_action_bridge_index_v709")
    bridge = mod.build_pack_709_status_bridge()
    prep = mod.prepare_pack_710_tower_capital_safety_next_action_bridge_registry_contract()

    assert bridge["pack"] == "709"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_capital_safety_next_action_bridge_index_ready"] is True
    assert bridge["safe_to_continue_to_pack_710"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "710"
    assert prep["source_pack"] == "709"

    first = mod.build_tower_capital_safety_next_action_bridge_index_preview()
    second = mod.build_tower_capital_safety_next_action_bridge_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_capital_safety_next_action_bridge_index_preview()
    assert third["status"] == "ready"
