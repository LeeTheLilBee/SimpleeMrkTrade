"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_6_PACK_615_TOWER_BETA_STACK_ROUTE_GUARD_FINAL_REVIEW_BATCH_CLOSE_READINESS_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_615_contract_ready():
    mod = importlib.import_module("tower.tower_tower_beta_stack_route_guard_final_review_batch_close_readiness_v615")
    payload = mod.build_tower_beta_stack_route_guard_final_review_batch_close_readiness_preview()

    assert payload["pack"] == "615"
    assert payload["pack_number"] == 615
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-stack-route-guard-final-review-batch-close-readiness-v615.json"
    assert payload["tower_layer"] == "Local Stack After Beta Backbone"
    assert payload["source_pack"] == "614"
    assert payload["local_source_stack"] == "501-600"
    assert payload["current_giant_pack"] == "601-625"
    assert payload["planned_local_stack"] == "501-625"
    assert payload["next_pack"] == "616"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["beta_stack_final_closeout_preview_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_616"] is True


def test_pack_615_summary_safety_ready():
    mod = importlib.import_module("tower.tower_tower_beta_stack_route_guard_final_review_batch_close_readiness_v615")
    payload = mod.build_tower_beta_stack_route_guard_final_review_batch_close_readiness_preview()
    summary = payload["tower_beta_stack_route_guard_final_review_batch_close_readiness_summary"]

    assert summary["source_ready"] is True
    assert summary["source_mode"] == "local_recursion_safe_snapshot"
    assert summary["row_count"] >= 24
    assert summary["check_count"] >= 19
    assert summary["action_count"] >= 5
    assert summary["stack_segment_count"] >= 4
    assert summary["final_review_domain_count"] >= 12
    assert summary["pre_save_gate_count"] >= 8
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["no_actual_save_push"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_actions_no_writes"] is True
    assert summary["tower_beta_stack_route_guard_final_review_batch_close_readiness_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_manual_live_unlock_enabled"] is False
    assert summary["real_hybrid_unlock_enabled"] is False
    assert summary["real_automated_unlock_enabled"] is False
    assert summary["real_capital_deployment_enabled"] is False
    assert summary["real_owner_override_apply_enabled"] is False
    assert summary["real_save_push_execution_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_615_copy_and_bridge():
    mod = importlib.import_module("tower.tower_tower_beta_stack_route_guard_final_review_batch_close_readiness_v615")
    payload = mod.build_tower_beta_stack_route_guard_final_review_batch_close_readiness_preview()

    bridge = mod.build_pack_615_status_bridge()
    assert bridge["pack"] == "615"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_stack_route_guard_final_review_batch_close_readiness_ready"] is True
    assert bridge["safe_to_continue_to_pack_616"] is True

    prep = mod.prepare_pack_616_tower_beta_stack_pre_save_verification_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "616"
    assert prep["source_pack"] == "615"

    first = mod.build_tower_beta_stack_route_guard_final_review_batch_close_readiness_preview()
    second = mod.build_tower_beta_stack_route_guard_final_review_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_beta_stack_route_guard_final_review_batch_close_readiness_preview()
    assert third["status"] == "ready"
