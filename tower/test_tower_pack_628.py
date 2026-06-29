"""
SEARCHABLE LABEL: TOWER_PACK_628_POST_STACK_ROUTE_MANIFEST_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_628_ready():
    mod = importlib.import_module("tower.tower_tower_post_stack_route_manifest_route_inventory_v628")
    payload = mod.build_tower_post_stack_route_manifest_route_inventory_preview()

    assert payload["pack"] == "628"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-post-stack-route-manifest-route-inventory-v628.json"
    assert payload["source_pack"] == "627"
    assert payload["current_packs"] == "627-631"
    assert payload["save_block"] == "626-631"
    assert payload["next_pack"] == "629"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_629"] is True


def test_pack_628_summary_safety():
    mod = importlib.import_module("tower.tower_tower_post_stack_route_manifest_route_inventory_v628")
    payload = mod.build_tower_post_stack_route_manifest_route_inventory_preview()
    summary = payload["tower_post_stack_route_manifest_route_inventory_summary"]

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
    assert summary["tower_post_stack_route_manifest_route_inventory_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_route_mutation_enabled"] is False
    assert summary["real_security_mutation_enabled"] is False
    assert summary["real_public_route_publish_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["save_push_performed"] is False


def test_pack_628_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_post_stack_route_manifest_route_inventory_v628")
    bridge = mod.build_pack_628_status_bridge()
    prep = mod.prepare_pack_629_tower_post_stack_route_manifest_guard_matrix()

    assert bridge["pack"] == "628"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_post_stack_route_manifest_route_inventory_ready"] is True
    assert bridge["safe_to_continue_to_pack_629"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "629"
    assert prep["source_pack"] == "628"

    first = mod.build_tower_post_stack_route_manifest_route_inventory_preview()
    second = mod.build_tower_post_stack_route_manifest_route_inventory_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_post_stack_route_manifest_route_inventory_preview()
    assert third["status"] == "ready"
