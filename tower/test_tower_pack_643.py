"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_638_687_PACK_643_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_643_ready():
    mod = importlib.import_module("tower.tower_tower_post_stack_owner_console_snapshot_note_draft_v643")
    payload = mod.build_tower_post_stack_owner_console_snapshot_note_draft_preview()

    assert payload["pack"] == "643"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-post-stack-owner-console-snapshot-note-draft-v643.json"
    assert payload["source_pack"] == "642"
    assert payload["current_packs"] == "638-687"
    assert payload["save_block"] == "638-687"
    assert payload["next_pack"] == "644"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_644"] is True


def test_pack_643_summary_safety():
    mod = importlib.import_module("tower.tower_tower_post_stack_owner_console_snapshot_note_draft_v643")
    payload = mod.build_tower_post_stack_owner_console_snapshot_note_draft_preview()
    summary = payload["tower_post_stack_owner_console_snapshot_note_draft_summary"]

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
    assert summary["tower_post_stack_owner_console_snapshot_note_draft_ready"] is True
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_643_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_post_stack_owner_console_snapshot_note_draft_v643")
    bridge = mod.build_pack_643_status_bridge()
    prep = mod.prepare_pack_644_tower_post_stack_owner_console_snapshot_note_version()

    assert bridge["pack"] == "643"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_post_stack_owner_console_snapshot_note_draft_ready"] is True
    assert bridge["safe_to_continue_to_pack_644"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "644"
    assert prep["source_pack"] == "643"

    first = mod.build_tower_post_stack_owner_console_snapshot_note_draft_preview()
    second = mod.build_tower_post_stack_owner_console_snapshot_note_draft_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_post_stack_owner_console_snapshot_note_draft_preview()
    assert third["status"] == "ready"
