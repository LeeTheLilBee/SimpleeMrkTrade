"""
SEARCHABLE LABEL: TOWER_PACK_1656_ACCESS_MONITORING_FIRST_USER_SAFETY_RECEIPTS_INDEX_TESTS
"""

from __future__ import annotations

from tower.tower_beta_access_monitoring_first_user_safety_receipts_index_v1656 import (
    build_tower_beta_access_monitoring_first_user_safety_receipts_index_preview,
    build_pack_1656_status_bridge,
    prepare_pack_1657_tower_beta_access_monitoring_first_user_safety_receipts_index,
)


def test_pack_1656_ready():
    payload = build_tower_beta_access_monitoring_first_user_safety_receipts_index_preview()

    assert payload["pack"] == "1656"
    assert payload["pack_number"] == 1656
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/beta-access-monitoring-first-user-safety-receipts-index-v1656.json"
    assert payload["source_block"] == "1605-1655"
    assert payload["source_pack"] == "1655"
    assert payload["next_pack"] == "1657"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["safe_to_continue_to_pack_1657"] is True


def test_pack_1656_summary_safety_no_pivot():
    payload = build_tower_beta_access_monitoring_first_user_safety_receipts_index_preview()
    summary = payload["tower_pack_1656_summary"]

    assert summary["source_block"] == "1605-1655"
    assert summary["source_pack"] == "1655"
    assert summary["row_count"] >= 82
    assert summary["check_count"] >= 22
    assert summary["monitoring_category_count"] >= 15
    assert summary["monitoring_item_count"] >= 28
    assert summary["blocked_real_action_count"] >= 39
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_real_actions_disabled"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_pack_1656_ready"] is True
    assert summary["access_monitoring_first_user_safety_started"] is True
    assert summary["beta_operations_next"] is True
    assert summary["real_access_monitoring_activation_enabled"] is False
    assert summary["real_first_user_access_grant_enabled"] is False
    assert summary["real_first_user_access_revoke_enabled"] is False
    assert summary["real_account_mutation_enabled"] is False
    assert summary["real_session_revoke_enabled"] is False
    assert summary["real_route_lock_mutation_enabled"] is False
    assert summary["real_controlled_unlock_apply_enabled"] is False
    assert summary["real_emergency_lockback_apply_enabled"] is False
    assert summary["real_beta_unlock_enabled"] is False
    assert summary["pivot_to_access_home"] is False
    assert summary["pivot_to_admin_dashboard"] is False
    assert summary["pivot_to_waitlist"] is False
    assert summary["pivot_to_initial_setup"] is False
    assert summary["real_mfa_enrollment_enabled"] is False
    assert summary["real_setup_email_send_enabled"] is False
    assert summary["real_password_store_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["real_save_push_execution_enabled"] is False


def test_pack_1656_bridge_prep_copy():
    bridge = build_pack_1656_status_bridge()
    prep = prepare_pack_1657_tower_beta_access_monitoring_first_user_safety_receipts_index()

    assert bridge["pack"] == "1656"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_pack_1656_ready"] is True
    assert bridge["safe_to_continue_to_pack_1657"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1657"
    assert prep["source_pack"] == "1656"

    first = build_tower_beta_access_monitoring_first_user_safety_receipts_index_preview()
    second = build_tower_beta_access_monitoring_first_user_safety_receipts_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = build_tower_beta_access_monitoring_first_user_safety_receipts_index_preview()
    assert third["status"] == "ready"
