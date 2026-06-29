"""
SEARCHABLE LABEL: TOWER_GIANT_PUSH_3_PACK_511_TOWER_MANUAL_LIVE_CLEARANCE_GATE_INDEX_TESTS_RECURSION_SAFE
"""

from __future__ import annotations

import importlib


def test_pack_511_contract_ready():
    mod = importlib.import_module("tower.tower_tower_manual_live_clearance_gate_index_v511")
    payload = mod.build_tower_manual_live_clearance_gate_index_preview()

    assert payload["pack"] == "511"
    assert payload["pack_number"] == 511
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-manual-live-clearance-gate-index-v511.json"
    assert payload["tower_layer"] == "Giant Push 3"
    assert payload["tower_sublayer"] == "Manual Live Clearance Gate layer"
    assert payload["source_pack"] == "510"
    assert payload["source_closed_batch"] == "451-500"
    assert payload["giant_push"] == "501-550"
    assert payload["next_batch"] == "551-575"
    assert payload["next_pack"] == "512"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["tower_manual_live_clearance_gate_preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["capital_safety_preview_only"] is True
    assert payload["beta_backbone_preview_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_512"] is True
    assert payload["prepare_pack_512_tower_manual_live_clearance_gate_registry_contract"]["pack"] == "512"


def test_pack_511_summary_safety_ready():
    mod = importlib.import_module("tower.tower_tower_manual_live_clearance_gate_index_v511")
    payload = mod.build_tower_manual_live_clearance_gate_index_preview()
    summary = payload["tower_manual_live_clearance_gate_index_summary"]

    assert summary["source_ready"] is True
    assert summary["source_mode"] == "recursion_safe_snapshot"
    assert summary["row_count"] >= 40
    assert summary["check_count"] >= 25
    assert summary["action_count"] >= 7
    assert summary["broker_safeguard_count"] >= 13
    assert summary["manual_live_gate_count"] >= 9
    assert summary["capital_deployment_gate_count"] >= 9
    assert summary["hard_block_count"] >= 8
    assert summary["decision_trigger_count"] >= 8
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["no_real_broker_api"] is True
    assert summary["no_real_clearance"] is True
    assert summary["no_real_manual_live_unlock"] is True
    assert summary["no_real_capital_movement"] is True
    assert summary["no_real_deployment_mark"] is True
    assert summary["no_real_trigger_execution"] is True
    assert summary["hard_blocks_preserved"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_actions_no_writes"] is True
    assert summary["tower_manual_live_clearance_gate_index_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_manual_live_unlock_enabled"] is False
    assert summary["real_hybrid_unlock_enabled"] is False
    assert summary["real_automated_unlock_enabled"] is False
    assert summary["real_capital_deployment_enabled"] is False
    assert summary["real_owner_override_apply_enabled"] is False
    assert summary["real_trigger_fire_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_511_payload_shapes_endpoint_bridge_and_copy():
    mod = importlib.import_module("tower.tower_tower_manual_live_clearance_gate_index_v511")
    payload = mod.build_tower_manual_live_clearance_gate_index_preview()

    rows = payload["tower_manual_live_clearance_gate_index_rows"]
    checks = payload["tower_manual_live_clearance_gate_index_checks"]
    actions = payload["tower_manual_live_clearance_gate_index_actions"]

    assert rows
    assert checks
    assert actions

    assert any(row.get("row_type") == "broker_safeguard" for row in rows)
    assert any(row.get("row_type") == "manual_live_gate" for row in rows)
    assert any(row.get("row_type") == "capital_deployment_gate" for row in rows)
    assert any(row.get("row_type") == "hard_block" for row in rows)
    assert any(row.get("row_type") == "decision_trigger" for row in rows)

    hard_blocks = [row for row in rows if row.get("row_type") == "hard_block"]
    assert hard_blocks
    assert all(row["hard_block_preserved"] is True for row in hard_blocks)

    assert all(row["preview_only"] is True for row in rows)
    assert all(row["contract_only"] is True for row in rows)
    assert all(row["writes_state"] is False for row in rows)

    assert all(check["passed"] is True for check in checks)
    assert all(check["writes_state"] is False for check in checks)

    preview_actions = [row for row in actions if row["result"] == "preview_allowed"]
    blocked_actions = [row for row in actions if row["result"] == "blocked_preview_only"]
    assert preview_actions
    assert blocked_actions
    assert all(row["enabled"] is True for row in preview_actions)
    assert all(row["enabled"] is False for row in blocked_actions)
    assert all(row["writes_state"] is False for row in actions)

    bridge = mod.build_pack_511_status_bridge()
    assert bridge["pack"] == "511"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["broker_safeguard_count"] >= 13
    assert bridge["manual_live_gate_count"] >= 9
    assert bridge["capital_deployment_gate_count"] >= 9
    assert bridge["hard_block_count"] >= 8
    assert bridge["decision_trigger_count"] >= 8
    assert bridge["tower_manual_live_clearance_gate_index_ready"] is True
    assert bridge["safe_to_continue_to_pack_512"] is True

    prep = mod.prepare_pack_512_tower_manual_live_clearance_gate_registry_contract()
    assert prep["ready"] is True
    assert prep["next_pack"] == "512"
    assert prep["source_pack"] == "511"

    first = mod.build_tower_manual_live_clearance_gate_index_preview()
    second = mod.build_tower_manual_live_clearance_gate_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_manual_live_clearance_gate_index_preview()
    assert third["status"] == "ready"
