"""
SEARCHABLE LABEL: TOWER_PACK_626_POST_STACK_SAVE_VERIFICATION_TESTS
"""

from __future__ import annotations

from tower.tower_post_stack_save_verification_index_v626 import (
    build_tower_post_stack_save_verification_index_preview,
    build_pack_626_status_bridge,
    prepare_pack_627_tower_post_stack_route_manifest_index,
)


def test_pack_626_post_save_verification_ready():
    payload = build_tower_post_stack_save_verification_index_preview()

    assert payload["pack"] == "626"
    assert payload["pack_number"] == 626
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/post-stack-save-verification-index-v626.json"
    assert payload["source_stack"] == "501-625"
    assert payload["source_pack"] == "625"
    assert payload["next_pack"] == "627"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["post_save_verification_preview_only"] is True
    assert payload["safe_to_continue_to_pack_627"] is True


def test_pack_626_summary_safety():
    payload = build_tower_post_stack_save_verification_index_preview()
    summary = payload["tower_pack_626_summary"]

    assert summary["source_stack"] == "501-625"
    assert summary["source_pack"] == "625"
    assert summary["row_count"] >= 20
    assert summary["check_count"] >= 9
    assert summary["post_save_check_count"] >= 8
    assert summary["blocked_real_action_count"] >= 15
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_pack_626_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_manual_live_unlock_enabled"] is False
    assert summary["real_save_push_execution_enabled"] is False


def test_pack_626_bridge_prep_and_copy():
    payload = build_tower_post_stack_save_verification_index_preview()
    bridge = build_pack_626_status_bridge()
    prep = prepare_pack_627_tower_post_stack_route_manifest_index()

    assert bridge["pack"] == "626"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_pack_626_ready"] is True
    assert bridge["safe_to_continue_to_pack_627"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "627"
    assert prep["source_pack"] == "626"

    first = build_tower_post_stack_save_verification_index_preview()
    second = build_tower_post_stack_save_verification_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = build_tower_post_stack_save_verification_index_preview()
    assert third["status"] == "ready"
