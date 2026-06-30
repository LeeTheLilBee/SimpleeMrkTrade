"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_943_992_PACK_992_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_992_ready():
    mod = importlib.import_module("tower.tower_tower_beta_final_owner_review_closeout_batch_close_readiness_v992")
    payload = mod.build_tower_beta_final_owner_review_closeout_batch_close_readiness_preview()

    assert payload["pack"] == "992"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/beta-final-owner-review-giant-closeout-v992.json"
    assert payload["source_pack"] == "991"
    assert payload["current_packs"] == "943-992"
    assert payload["save_block"] == "942-992"
    assert payload["next_pack"] == "993"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_993"] is True


def test_pack_992_summary_safety():
    mod = importlib.import_module("tower.tower_tower_beta_final_owner_review_closeout_batch_close_readiness_v992")
    payload = mod.build_tower_beta_final_owner_review_closeout_batch_close_readiness_preview()
    summary = payload["tower_beta_final_owner_review_closeout_batch_close_readiness_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 50
    assert summary["check_count"] >= 16
    assert summary["final_owner_review_field_count"] >= 13
    assert summary["final_owner_review_item_count"] >= 14
    assert summary["blocked_real_action_count"] >= 23
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_real_actions_disabled"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_beta_final_owner_review_closeout_batch_close_readiness_ready"] is True
    assert summary["real_final_owner_review_approval_enabled"] is False
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


def test_pack_992_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_beta_final_owner_review_closeout_batch_close_readiness_v992")
    bridge = mod.build_pack_992_status_bridge()
    prep = mod.prepare_pack_993_tower_beta_final_owner_review_save_readiness_index()

    assert bridge["pack"] == "992"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_final_owner_review_closeout_batch_close_readiness_ready"] is True
    assert bridge["safe_to_continue_to_pack_993"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "993"
    assert prep["source_pack"] == "992"

    first = mod.build_tower_beta_final_owner_review_closeout_batch_close_readiness_preview()
    second = mod.build_tower_beta_final_owner_review_closeout_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_beta_final_owner_review_closeout_batch_close_readiness_preview()
    assert third["status"] == "ready"
