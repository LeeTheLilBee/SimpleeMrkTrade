"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_943_992_PACK_987_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_987_ready():
    mod = importlib.import_module("tower.tower_tower_beta_final_owner_review_closeout_owner_summary_v987")
    payload = mod.build_tower_beta_final_owner_review_closeout_owner_summary_preview()

    assert payload["pack"] == "987"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-final-owner-review-closeout-owner-summary-v987.json"
    assert payload["source_pack"] == "986"
    assert payload["current_packs"] == "943-992"
    assert payload["save_block"] == "942-992"
    assert payload["next_pack"] == "988"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_988"] is True


def test_pack_987_summary_safety():
    mod = importlib.import_module("tower.tower_tower_beta_final_owner_review_closeout_owner_summary_v987")
    payload = mod.build_tower_beta_final_owner_review_closeout_owner_summary_preview()
    summary = payload["tower_beta_final_owner_review_closeout_owner_summary_summary"]

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
    assert summary["tower_beta_final_owner_review_closeout_owner_summary_ready"] is True
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


def test_pack_987_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_beta_final_owner_review_closeout_owner_summary_v987")
    bridge = mod.build_pack_987_status_bridge()
    prep = mod.prepare_pack_988_tower_beta_final_owner_review_closeout_note_draft()

    assert bridge["pack"] == "987"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_final_owner_review_closeout_owner_summary_ready"] is True
    assert bridge["safe_to_continue_to_pack_988"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "988"
    assert prep["source_pack"] == "987"

    first = mod.build_tower_beta_final_owner_review_closeout_owner_summary_preview()
    second = mod.build_tower_beta_final_owner_review_closeout_owner_summary_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_beta_final_owner_review_closeout_owner_summary_preview()
    assert third["status"] == "ready"
