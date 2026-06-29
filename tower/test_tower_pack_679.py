"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_638_687_PACK_679_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_679_ready():
    mod = importlib.import_module("tower.tower_tower_post_stack_owner_console_clouds_snapshot_closeout_registry_contract_v679")
    payload = mod.build_tower_post_stack_owner_console_clouds_snapshot_closeout_registry_contract_preview()

    assert payload["pack"] == "679"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-post-stack-owner-console-clouds-snapshot-closeout-registry-contract-v679.json"
    assert payload["source_pack"] == "678"
    assert payload["current_packs"] == "638-687"
    assert payload["save_block"] == "638-687"
    assert payload["next_pack"] == "680"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_680"] is True


def test_pack_679_summary_safety():
    mod = importlib.import_module("tower.tower_tower_post_stack_owner_console_clouds_snapshot_closeout_registry_contract_v679")
    payload = mod.build_tower_post_stack_owner_console_clouds_snapshot_closeout_registry_contract_preview()
    summary = payload["tower_post_stack_owner_console_clouds_snapshot_closeout_registry_contract_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 50
    assert summary["check_count"] >= 13
    assert summary["owner_console_field_count"] >= 10
    assert summary["clouds_snapshot_field_count"] >= 12
    assert summary["security_boundary_field_count"] >= 13
    assert summary["blocked_real_action_count"] >= 20
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["no_clouds_write"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_post_stack_owner_console_clouds_snapshot_closeout_registry_contract_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_679_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_post_stack_owner_console_clouds_snapshot_closeout_registry_contract_v679")
    bridge = mod.build_pack_679_status_bridge()
    prep = mod.prepare_pack_680_tower_post_stack_owner_console_clouds_snapshot_closeout_snapshot_matrix()

    assert bridge["pack"] == "679"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_post_stack_owner_console_clouds_snapshot_closeout_registry_contract_ready"] is True
    assert bridge["safe_to_continue_to_pack_680"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "680"
    assert prep["source_pack"] == "679"

    first = mod.build_tower_post_stack_owner_console_clouds_snapshot_closeout_registry_contract_preview()
    second = mod.build_tower_post_stack_owner_console_clouds_snapshot_closeout_registry_contract_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_post_stack_owner_console_clouds_snapshot_closeout_registry_contract_preview()
    assert third["status"] == "ready"
