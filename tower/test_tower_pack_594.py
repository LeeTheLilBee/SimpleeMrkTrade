"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_5_PACK_594_TOWER_CLOUDS_STATUS_SNAPSHOT_BRIDGE_READINESS_BRIDGE_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_594_contract_ready():
    mod = importlib.import_module("tower.tower_tower_clouds_status_snapshot_bridge_readiness_bridge_v594")
    payload = mod.build_tower_clouds_status_snapshot_bridge_readiness_bridge_preview()

    assert payload["pack"] == "594"
    assert payload["pack_number"] == 594
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-clouds-status-snapshot-bridge-readiness-bridge-v594.json"
    assert payload["tower_layer"] == "Local Stack After Beta Backbone"
    assert payload["source_pack"] == "593"
    assert payload["local_source_stack"] == "501-575"
    assert payload["current_giant_pack"] == "576-600"
    assert payload["planned_local_stack"] == "501-625"
    assert payload["next_pack"] == "595"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["beta_control_surface_preview_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_595"] is True


def test_pack_594_summary_safety_ready():
    mod = importlib.import_module("tower.tower_tower_clouds_status_snapshot_bridge_readiness_bridge_v594")
    payload = mod.build_tower_clouds_status_snapshot_bridge_readiness_bridge_preview()
    summary = payload["tower_clouds_status_snapshot_bridge_readiness_bridge_summary"]

    assert summary["source_ready"] is True
    assert summary["source_mode"] == "local_recursion_safe_snapshot"
    assert summary["row_count"] >= 38
    assert summary["check_count"] >= 16
    assert summary["action_count"] >= 5
    assert summary["control_surface_domain_count"] >= 10
    assert summary["owner_console_bridge_count"] >= 8
    assert summary["quick_action_count"] >= 10
    assert summary["clouds_snapshot_field_count"] >= 10
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_quick_actions_safe"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_actions_no_writes"] is True
    assert summary["tower_clouds_status_snapshot_bridge_readiness_bridge_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_manual_live_unlock_enabled"] is False
    assert summary["real_hybrid_unlock_enabled"] is False
    assert summary["real_automated_unlock_enabled"] is False
    assert summary["real_capital_deployment_enabled"] is False
    assert summary["real_owner_override_apply_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_quick_action_execution_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_594_copy_and_bridge():
    mod = importlib.import_module("tower.tower_tower_clouds_status_snapshot_bridge_readiness_bridge_v594")
    payload = mod.build_tower_clouds_status_snapshot_bridge_readiness_bridge_preview()

    bridge = mod.build_pack_594_status_bridge()
    assert bridge["pack"] == "594"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_clouds_status_snapshot_bridge_readiness_bridge_ready"] is True
    assert bridge["safe_to_continue_to_pack_595"] is True

    prep = mod.prepare_pack_595_tower_clouds_status_snapshot_bridge_batch_close_readiness()
    assert prep["ready"] is True
    assert prep["next_pack"] == "595"
    assert prep["source_pack"] == "594"

    first = mod.build_tower_clouds_status_snapshot_bridge_readiness_bridge_preview()
    second = mod.build_tower_clouds_status_snapshot_bridge_readiness_bridge_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_clouds_status_snapshot_bridge_readiness_bridge_preview()
    assert third["status"] == "ready"
