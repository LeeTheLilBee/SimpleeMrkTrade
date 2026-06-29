"""
SEARCHABLE LABEL: TOWER_GIANT_PUSH_2_PACK_482_TOWER_SAFETY_NOTIFICATION_SNAPSHOT_REGISTRY_CONTRACT_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_482_contract_ready():
    mod = importlib.import_module("tower.tower_tower_safety_notification_snapshot_registry_contract_v482")
    payload = mod.build_tower_safety_notification_snapshot_registry_contract_preview()

    assert payload["pack"] == "482"
    assert payload["pack_number"] == 482
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-safety-notification-snapshot-registry-contract-v482.json"
    assert payload["tower_layer"] == "Giant Push 2"
    assert payload["tower_sublayer"] == "Safety Notification and Status Snapshot layer"
    assert payload["source_pack"] == "481"
    assert payload["source_closed_batch"] == "396-450"
    assert payload["giant_push"] == "451-500"
    assert payload["next_batch"] == "501-550"
    assert payload["next_pack"] == "483"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["tower_safety_notification_snapshot_preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["capital_safety_preview_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_483"] is True
    assert payload["prepare_pack_483_tower_safety_notification_snapshot_policy_matrix"]["pack"] == "483"


def test_pack_482_summary_safety_ready():
    mod = importlib.import_module("tower.tower_tower_safety_notification_snapshot_registry_contract_v482")
    payload = mod.build_tower_safety_notification_snapshot_registry_contract_preview()
    summary = payload["tower_safety_notification_snapshot_registry_contract_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 30
    assert summary["check_count"] >= 21
    assert summary["action_count"] >= 7
    assert summary["mission_account_count"] >= 6
    assert summary["mode_count"] >= 10
    assert summary["kill_switch_count"] >= 15
    assert summary["notification_level_count"] >= 6
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["no_real_live_permission"] is True
    assert summary["no_real_permission_granted"] is True
    assert summary["no_real_kill_switch_activation"] is True
    assert summary["no_real_kill_switch_release"] is True
    assert summary["proof_demo_live_blocked"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_actions_no_writes"] is True
    assert summary["tower_safety_notification_snapshot_registry_contract_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_manual_live_unlock_enabled"] is False
    assert summary["real_hybrid_unlock_enabled"] is False
    assert summary["real_automated_unlock_enabled"] is False
    assert summary["real_kill_switch_mutation_enabled"] is False
    assert summary["real_emergency_halt_mutation_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_482_payload_shapes_endpoint_bridge_and_copy():
    mod = importlib.import_module("tower.tower_tower_safety_notification_snapshot_registry_contract_v482")
    payload = mod.build_tower_safety_notification_snapshot_registry_contract_preview()

    rows = payload["tower_safety_notification_snapshot_registry_contract_rows"]
    checks = payload["tower_safety_notification_snapshot_registry_contract_checks"]
    actions = payload["tower_safety_notification_snapshot_registry_contract_actions"]

    assert rows
    assert checks
    assert actions

    assert any(row.get("account_id") == "acct_proof_demo_ob" for row in rows)
    proof_demo = next(row for row in rows if row.get("account_id") == "acct_proof_demo_ob")
    assert "manual_live_preview" in proof_demo["blocked_modes"]
    assert "automated_expanded" in proof_demo["blocked_modes"]

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

    bridge = mod.build_pack_482_status_bridge()
    assert bridge["pack"] == "482"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["mission_account_count"] >= 6
    assert bridge["mode_count"] >= 10
    assert bridge["kill_switch_count"] >= 15
    assert bridge["tower_safety_notification_snapshot_registry_contract_ready"] is True
    assert bridge["safe_to_continue_to_pack_483"] is True

    prep = mod.prepare_pack_483_tower_safety_notification_snapshot_policy_matrix()
    assert prep["ready"] is True
    assert prep["next_pack"] == "483"
    assert prep["source_pack"] == "482"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/tower-safety-notification-snapshot-registry-contract-v482.json" in rules

    response = app.test_client().get("/tower/tower-safety-notification-snapshot-registry-contract-v482.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "482"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["safe_to_continue_to_pack_483"] is True

    first = mod.build_tower_safety_notification_snapshot_registry_contract_preview()
    second = mod.build_tower_safety_notification_snapshot_registry_contract_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_safety_notification_snapshot_registry_contract_preview()
    assert third["status"] == "ready"
