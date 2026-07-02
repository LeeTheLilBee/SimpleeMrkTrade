"""
SEARCHABLE LABEL: TOWER_PACK_1605_CONTROLLED_UNLOCK_LOCKBACK_INDEX_TESTS
"""

from __future__ import annotations

from tower.tower_beta_controlled_unlock_emergency_lockback_index_v1605 import (
    build_tower_beta_controlled_unlock_emergency_lockback_index_preview,
    build_pack_1605_status_bridge,
    prepare_pack_1606_tower_beta_controlled_unlock_emergency_lockback_index,
)


def test_pack_1605_ready():
    payload = build_tower_beta_controlled_unlock_emergency_lockback_index_preview()

    assert payload["pack"] == "1605"
    assert payload["pack_number"] == 1605
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/beta-controlled-unlock-emergency-lockback-index-v1605.json"
    assert payload["source_block"] == "1554-1604"
    assert payload["source_pack"] == "1604"
    assert payload["next_pack"] == "1606"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["safe_to_continue_to_pack_1606"] is True


def test_pack_1605_summary_safety_no_pivot():
    payload = build_tower_beta_controlled_unlock_emergency_lockback_index_preview()
    summary = payload["tower_pack_1605_summary"]

    assert summary["source_block"] == "1554-1604"
    assert summary["source_pack"] == "1604"
    assert summary["row_count"] >= 78
    assert summary["check_count"] >= 18
    assert summary["unlock_category_count"] >= 15
    assert summary["unlock_item_count"] >= 28
    assert summary["blocked_real_action_count"] >= 35
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_real_actions_disabled"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_pack_1605_ready"] is True
    assert summary["controlled_unlock_lockback_started"] is True
    assert summary["access_monitoring_first_user_safety_next"] is True
    assert summary["real_controlled_unlock_apply_enabled"] is False
    assert summary["real_emergency_lockback_apply_enabled"] is False
    assert summary["real_beta_unlock_enabled"] is False
    assert summary["real_go_decision_apply_enabled"] is False
    assert summary["real_owner_approval_apply_enabled"] is False
    assert summary["pivot_to_access_home"] is False
    assert summary["pivot_to_admin_dashboard"] is False
    assert summary["pivot_to_waitlist"] is False
    assert summary["pivot_to_initial_setup"] is False
    assert summary["real_account_mutation_enabled"] is False
    assert summary["real_access_grant_mutation_enabled"] is False
    assert summary["real_access_revoke_mutation_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["real_save_push_execution_enabled"] is False


def test_pack_1605_bridge_prep_copy():
    bridge = build_pack_1605_status_bridge()
    prep = prepare_pack_1606_tower_beta_controlled_unlock_emergency_lockback_index()

    assert bridge["pack"] == "1605"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_pack_1605_ready"] is True
    assert bridge["safe_to_continue_to_pack_1606"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1606"
    assert prep["source_pack"] == "1605"

    first = build_tower_beta_controlled_unlock_emergency_lockback_index_preview()
    second = build_tower_beta_controlled_unlock_emergency_lockback_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = build_tower_beta_controlled_unlock_emergency_lockback_index_preview()
    assert third["status"] == "ready"
