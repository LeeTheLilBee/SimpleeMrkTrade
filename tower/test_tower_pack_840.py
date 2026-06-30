"""
SEARCHABLE LABEL: TOWER_PACK_840_BETA_READINESS_SCOREBOARD_SAVE_READINESS_TESTS
"""

from __future__ import annotations

from tower.tower_beta_readiness_scoreboard_save_readiness_index_v840 import (
    build_tower_beta_readiness_scoreboard_save_readiness_index_preview,
    build_pack_840_status_bridge,
    prepare_pack_841_tower_beta_owner_go_no_go_index,
)


def test_pack_840_beta_readiness_scoreboard_save_readiness_ready():
    payload = build_tower_beta_readiness_scoreboard_save_readiness_index_preview()

    assert payload["pack"] == "840"
    assert payload["pack_number"] == 840
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/beta-readiness-scoreboard-save-readiness-index-v840.json"
    assert payload["source_block"] == "790-839"
    assert payload["source_pack"] == "839"
    assert payload["next_pack"] == "841"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["scoreboard_save_readiness_preview_only"] is True
    assert payload["safe_to_continue_to_pack_841"] is True


def test_pack_840_summary_safety():
    payload = build_tower_beta_readiness_scoreboard_save_readiness_index_preview()
    summary = payload["tower_pack_840_summary"]

    assert summary["source_block"] == "790-839"
    assert summary["source_pack"] == "839"
    assert summary["row_count"] >= 32
    assert summary["check_count"] >= 12
    assert summary["post_scoreboard_save_check_count"] >= 8
    assert summary["next_corridor_hint_count"] >= 5
    assert summary["blocked_real_action_count"] >= 19
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_pack_840_ready"] is True
    assert summary["real_beta_unlock_enabled"] is False
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_go_no_go_decision_apply_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["real_save_push_execution_enabled"] is False


def test_pack_840_bridge_prep_and_copy():
    payload = build_tower_beta_readiness_scoreboard_save_readiness_index_preview()
    bridge = build_pack_840_status_bridge()
    prep = prepare_pack_841_tower_beta_owner_go_no_go_index()

    assert bridge["pack"] == "840"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_pack_840_ready"] is True
    assert bridge["safe_to_continue_to_pack_841"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "841"
    assert prep["source_pack"] == "840"

    first = build_tower_beta_readiness_scoreboard_save_readiness_index_preview()
    second = build_tower_beta_readiness_scoreboard_save_readiness_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = build_tower_beta_readiness_scoreboard_save_readiness_index_preview()
    assert third["status"] == "ready"
