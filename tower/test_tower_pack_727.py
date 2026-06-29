"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_689_738_PACK_727_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_727_ready():
    mod = importlib.import_module("tower.tower_tower_security_boundary_next_action_bridge_readiness_bridge_v727")
    payload = mod.build_tower_security_boundary_next_action_bridge_readiness_bridge_preview()

    assert payload["pack"] == "727"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-security-boundary-next-action-bridge-readiness-bridge-v727.json"
    assert payload["source_pack"] == "726"
    assert payload["current_packs"] == "689-738"
    assert payload["save_block"] == "688-738"
    assert payload["next_pack"] == "728"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_728"] is True


def test_pack_727_summary_safety():
    mod = importlib.import_module("tower.tower_tower_security_boundary_next_action_bridge_readiness_bridge_v727")
    payload = mod.build_tower_security_boundary_next_action_bridge_readiness_bridge_preview()
    summary = payload["tower_security_boundary_next_action_bridge_readiness_bridge_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 40
    assert summary["check_count"] >= 13
    assert summary["action_field_count"] >= 12
    assert summary["focus_queue_item_count"] >= 8
    assert summary["blocked_real_action_count"] >= 20
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["no_focus_publish"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_security_boundary_next_action_bridge_readiness_bridge_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["real_focus_queue_publish_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_727_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_security_boundary_next_action_bridge_readiness_bridge_v727")
    bridge = mod.build_pack_727_status_bridge()
    prep = mod.prepare_pack_728_tower_security_boundary_next_action_bridge_batch_close_readiness()

    assert bridge["pack"] == "727"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_security_boundary_next_action_bridge_readiness_bridge_ready"] is True
    assert bridge["safe_to_continue_to_pack_728"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "728"
    assert prep["source_pack"] == "727"

    first = mod.build_tower_security_boundary_next_action_bridge_readiness_bridge_preview()
    second = mod.build_tower_security_boundary_next_action_bridge_readiness_bridge_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_security_boundary_next_action_bridge_readiness_bridge_preview()
    assert third["status"] == "ready"
