"""
SEARCHABLE LABEL: TOWER_PACK_631_POST_STACK_ROUTE_MANIFEST_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_631_ready():
    mod = importlib.import_module("tower.tower_tower_post_stack_route_manifest_batch_close_readiness_v631")
    payload = mod.build_tower_post_stack_route_manifest_batch_close_readiness_preview()

    assert payload["pack"] == "631"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/post-stack-route-manifest-batch-close-readiness-v631.json"
    assert payload["source_pack"] == "630"
    assert payload["current_packs"] == "627-631"
    assert payload["save_block"] == "626-631"
    assert payload["next_pack"] == "632"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_632"] is True


def test_pack_631_summary_safety():
    mod = importlib.import_module("tower.tower_tower_post_stack_route_manifest_batch_close_readiness_v631")
    payload = mod.build_tower_post_stack_route_manifest_batch_close_readiness_preview()
    summary = payload["tower_post_stack_route_manifest_batch_close_readiness_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 30
    assert summary["check_count"] >= 10
    assert summary["route_manifest_domain_count"] >= 10
    assert summary["guard_review_item_count"] >= 8
    assert summary["blocked_real_action_count"] >= 15
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_post_stack_route_manifest_batch_close_readiness_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_route_mutation_enabled"] is False
    assert summary["real_security_mutation_enabled"] is False
    assert summary["real_public_route_publish_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["save_push_performed"] is False


def test_pack_631_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_post_stack_route_manifest_batch_close_readiness_v631")
    bridge = mod.build_pack_631_status_bridge()
    prep = mod.prepare_pack_632_tower_post_stack_save_push_readiness_index()

    assert bridge["pack"] == "631"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_post_stack_route_manifest_batch_close_readiness_ready"] is True
    assert bridge["safe_to_continue_to_pack_632"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "632"
    assert prep["source_pack"] == "631"

    first = mod.build_tower_post_stack_route_manifest_batch_close_readiness_preview()
    second = mod.build_tower_post_stack_route_manifest_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_post_stack_route_manifest_batch_close_readiness_preview()
    assert third["status"] == "ready"
