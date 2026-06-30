"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_790_839_PACK_834_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_834_ready():
    mod = importlib.import_module("tower.tower_tower_beta_readiness_scoreboard_closeout_owner_summary_v834")
    payload = mod.build_tower_beta_readiness_scoreboard_closeout_owner_summary_preview()

    assert payload["pack"] == "834"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-readiness-scoreboard-closeout-owner-summary-v834.json"
    assert payload["source_pack"] == "833"
    assert payload["current_packs"] == "790-839"
    assert payload["save_block"] == "790-839"
    assert payload["next_pack"] == "835"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_835"] is True


def test_pack_834_summary_safety():
    mod = importlib.import_module("tower.tower_tower_beta_readiness_scoreboard_closeout_owner_summary_v834")
    payload = mod.build_tower_beta_readiness_scoreboard_closeout_owner_summary_preview()
    summary = payload["tower_beta_readiness_scoreboard_closeout_owner_summary_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 43
    assert summary["check_count"] >= 14
    assert summary["readiness_field_count"] >= 12
    assert summary["beta_score_item_count"] >= 10
    assert summary["blocked_real_action_count"] >= 21
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_score_preview_100"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_beta_readiness_scoreboard_closeout_owner_summary_ready"] is True
    assert summary["real_beta_unlock_enabled"] is False
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["real_focus_queue_publish_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_834_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_beta_readiness_scoreboard_closeout_owner_summary_v834")
    bridge = mod.build_pack_834_status_bridge()
    prep = mod.prepare_pack_835_tower_beta_readiness_scoreboard_closeout_note_draft()

    assert bridge["pack"] == "834"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_readiness_scoreboard_closeout_owner_summary_ready"] is True
    assert bridge["safe_to_continue_to_pack_835"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "835"
    assert prep["source_pack"] == "834"

    first = mod.build_tower_beta_readiness_scoreboard_closeout_owner_summary_preview()
    second = mod.build_tower_beta_readiness_scoreboard_closeout_owner_summary_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_beta_readiness_scoreboard_closeout_owner_summary_preview()
    assert third["status"] == "ready"
