"""
SEARCHABLE LABEL: TOWER_PACK_632_POST_STACK_SAVE_PUSH_READINESS_TESTS
"""

from __future__ import annotations

from tower.tower_post_stack_save_push_readiness_index_v632 import (
    build_tower_post_stack_save_push_readiness_index_preview,
    build_pack_632_status_bridge,
    prepare_pack_633_tower_post_stack_security_boundary_index,
)


def test_pack_632_post_save_push_readiness_ready():
    payload = build_tower_post_stack_save_push_readiness_index_preview()

    assert payload["pack"] == "632"
    assert payload["pack_number"] == 632
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/post-stack-save-push-readiness-index-v632.json"
    assert payload["source_block"] == "626-631"
    assert payload["source_pack"] == "631"
    assert payload["next_pack"] == "633"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["post_save_push_readiness_preview_only"] is True
    assert payload["safe_to_continue_to_pack_633"] is True


def test_pack_632_summary_safety():
    payload = build_tower_post_stack_save_push_readiness_index_preview()
    summary = payload["tower_pack_632_summary"]

    assert summary["source_block"] == "626-631"
    assert summary["source_pack"] == "631"
    assert summary["row_count"] >= 20
    assert summary["check_count"] >= 9
    assert summary["post_save_push_check_count"] >= 8
    assert summary["next_corridor_hint_count"] >= 4
    assert summary["blocked_real_action_count"] >= 14
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_pack_632_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_manual_live_unlock_enabled"] is False
    assert summary["real_save_push_execution_enabled"] is False


def test_pack_632_bridge_prep_and_copy():
    payload = build_tower_post_stack_save_push_readiness_index_preview()
    bridge = build_pack_632_status_bridge()
    prep = prepare_pack_633_tower_post_stack_security_boundary_index()

    assert bridge["pack"] == "632"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_pack_632_ready"] is True
    assert bridge["safe_to_continue_to_pack_633"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "633"
    assert prep["source_pack"] == "632"

    first = build_tower_post_stack_save_push_readiness_index_preview()
    second = build_tower_post_stack_save_push_readiness_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = build_tower_post_stack_save_push_readiness_index_preview()
    assert third["status"] == "ready"
