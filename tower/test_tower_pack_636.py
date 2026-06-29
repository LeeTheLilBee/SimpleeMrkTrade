"""
SEARCHABLE LABEL: TOWER_PACK_636_POST_STACK_SECURITY_BOUNDARY_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_636_ready():
    mod = importlib.import_module("tower.tower_tower_post_stack_security_boundary_owner_summary_v636")
    payload = mod.build_tower_post_stack_security_boundary_owner_summary_preview()

    assert payload["pack"] == "636"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-post-stack-security-boundary-owner-summary-v636.json"
    assert payload["source_pack"] == "635"
    assert payload["current_packs"] == "633-637"
    assert payload["save_block"] == "632-637"
    assert payload["next_pack"] == "637"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_637"] is True


def test_pack_636_summary_safety():
    mod = importlib.import_module("tower.tower_tower_post_stack_security_boundary_owner_summary_v636")
    payload = mod.build_tower_post_stack_security_boundary_owner_summary_preview()
    summary = payload["tower_post_stack_security_boundary_owner_summary_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 40
    assert summary["check_count"] >= 12
    assert summary["security_boundary_count"] >= 12
    assert summary["boundary_check_count"] >= 12
    assert summary["blocked_real_action_count"] >= 17
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_post_stack_security_boundary_owner_summary_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_manual_live_unlock_enabled"] is False
    assert summary["real_hybrid_unlock_enabled"] is False
    assert summary["real_automated_unlock_enabled"] is False
    assert summary["real_route_mutation_enabled"] is False
    assert summary["real_security_mutation_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_636_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_post_stack_security_boundary_owner_summary_v636")
    bridge = mod.build_pack_636_status_bridge()
    prep = mod.prepare_pack_637_tower_post_stack_security_boundary_batch_close_readiness()

    assert bridge["pack"] == "636"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_post_stack_security_boundary_owner_summary_ready"] is True
    assert bridge["safe_to_continue_to_pack_637"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "637"
    assert prep["source_pack"] == "636"

    first = mod.build_tower_post_stack_security_boundary_owner_summary_preview()
    second = mod.build_tower_post_stack_security_boundary_owner_summary_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_post_stack_security_boundary_owner_summary_preview()
    assert third["status"] == "ready"
