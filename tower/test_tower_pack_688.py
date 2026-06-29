"""
SEARCHABLE LABEL: TOWER_PACK_688_POST_STACK_GIANT_SAVE_READINESS_TESTS
"""

from __future__ import annotations

from tower.tower_post_stack_giant_save_readiness_index_v688 import (
    build_tower_post_stack_giant_save_readiness_index_preview,
    build_pack_688_status_bridge,
    prepare_pack_689_tower_post_stack_owner_console_action_summary_index,
)


def test_pack_688_post_giant_save_readiness_ready():
    payload = build_tower_post_stack_giant_save_readiness_index_preview()

    assert payload["pack"] == "688"
    assert payload["pack_number"] == 688
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/post-stack-giant-save-readiness-index-v688.json"
    assert payload["source_block"] == "638-687"
    assert payload["source_pack"] == "687"
    assert payload["next_pack"] == "689"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["post_giant_save_readiness_preview_only"] is True
    assert payload["safe_to_continue_to_pack_689"] is True


def test_pack_688_summary_safety():
    payload = build_tower_post_stack_giant_save_readiness_index_preview()
    summary = payload["tower_pack_688_summary"]

    assert summary["source_block"] == "638-687"
    assert summary["source_pack"] == "687"
    assert summary["row_count"] >= 25
    assert summary["check_count"] >= 10
    assert summary["post_giant_save_check_count"] >= 8
    assert summary["next_corridor_hint_count"] >= 5
    assert summary["blocked_real_action_count"] >= 16
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_pack_688_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["real_save_push_execution_enabled"] is False


def test_pack_688_bridge_prep_and_copy():
    payload = build_tower_post_stack_giant_save_readiness_index_preview()
    bridge = build_pack_688_status_bridge()
    prep = prepare_pack_689_tower_post_stack_owner_console_action_summary_index()

    assert bridge["pack"] == "688"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_pack_688_ready"] is True
    assert bridge["safe_to_continue_to_pack_689"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "689"
    assert prep["source_pack"] == "688"

    first = build_tower_post_stack_giant_save_readiness_index_preview()
    second = build_tower_post_stack_giant_save_readiness_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = build_tower_post_stack_giant_save_readiness_index_preview()
    assert third["status"] == "ready"
