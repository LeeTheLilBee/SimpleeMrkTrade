"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_638_687_PACK_648_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_648_ready():
    mod = importlib.import_module("tower.tower_tower_post_stack_capital_safety_snapshot_index_v648")
    payload = mod.build_tower_post_stack_capital_safety_snapshot_index_preview()

    assert payload["pack"] == "648"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-post-stack-capital-safety-snapshot-index-v648.json"
    assert payload["source_pack"] == "647"
    assert payload["current_packs"] == "638-687"
    assert payload["save_block"] == "638-687"
    assert payload["next_pack"] == "649"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_649"] is True


def test_pack_648_summary_safety():
    mod = importlib.import_module("tower.tower_tower_post_stack_capital_safety_snapshot_index_v648")
    payload = mod.build_tower_post_stack_capital_safety_snapshot_index_preview()
    summary = payload["tower_post_stack_capital_safety_snapshot_index_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 50
    assert summary["check_count"] >= 13
    assert summary["owner_console_field_count"] >= 10
    assert summary["clouds_snapshot_field_count"] >= 12
    assert summary["security_boundary_field_count"] >= 13
    assert summary["blocked_real_action_count"] >= 20
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["no_clouds_write"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_post_stack_capital_safety_snapshot_index_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_648_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_post_stack_capital_safety_snapshot_index_v648")
    bridge = mod.build_pack_648_status_bridge()
    prep = mod.prepare_pack_649_tower_post_stack_capital_safety_snapshot_registry_contract()

    assert bridge["pack"] == "648"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_post_stack_capital_safety_snapshot_index_ready"] is True
    assert bridge["safe_to_continue_to_pack_649"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "649"
    assert prep["source_pack"] == "648"

    first = mod.build_tower_post_stack_capital_safety_snapshot_index_preview()
    second = mod.build_tower_post_stack_capital_safety_snapshot_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_post_stack_capital_safety_snapshot_index_preview()
    assert third["status"] == "ready"
