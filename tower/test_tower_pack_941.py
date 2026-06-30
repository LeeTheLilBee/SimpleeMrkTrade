"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_892_941_PACK_941_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_941_ready():
    mod = importlib.import_module("tower.tower_tower_beta_release_candidate_closeout_batch_close_readiness_v941")
    payload = mod.build_tower_beta_release_candidate_closeout_batch_close_readiness_preview()

    assert payload["pack"] == "941"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/beta-release-candidate-giant-closeout-v941.json"
    assert payload["source_pack"] == "940"
    assert payload["current_packs"] == "892-941"
    assert payload["save_block"] == "891-941"
    assert payload["next_pack"] == "942"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_942"] is True


def test_pack_941_summary_safety():
    mod = importlib.import_module("tower.tower_tower_beta_release_candidate_closeout_batch_close_readiness_v941")
    payload = mod.build_tower_beta_release_candidate_closeout_batch_close_readiness_preview()
    summary = payload["tower_beta_release_candidate_closeout_batch_close_readiness_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 48
    assert summary["check_count"] >= 15
    assert summary["release_candidate_field_count"] >= 13
    assert summary["release_candidate_item_count"] >= 13
    assert summary["blocked_real_action_count"] >= 22
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_real_actions_disabled"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_beta_release_candidate_closeout_batch_close_readiness_ready"] is True
    assert summary["real_release_candidate_approval_enabled"] is False
    assert summary["real_beta_go_decision_enabled"] is False
    assert summary["real_beta_unlock_enabled"] is False
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_941_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_beta_release_candidate_closeout_batch_close_readiness_v941")
    bridge = mod.build_pack_941_status_bridge()
    prep = mod.prepare_pack_942_tower_beta_release_candidate_save_readiness_index()

    assert bridge["pack"] == "941"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_release_candidate_closeout_batch_close_readiness_ready"] is True
    assert bridge["safe_to_continue_to_pack_942"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "942"
    assert prep["source_pack"] == "941"

    first = mod.build_tower_beta_release_candidate_closeout_batch_close_readiness_preview()
    second = mod.build_tower_beta_release_candidate_closeout_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_beta_release_candidate_closeout_batch_close_readiness_preview()
    assert third["status"] == "ready"
