"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_790_839_PACK_795_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_795_ready():
    mod = importlib.import_module("tower.tower_tower_post_stack_beta_preflight_save_readiness_note_draft_v795")
    payload = mod.build_tower_post_stack_beta_preflight_save_readiness_note_draft_preview()

    assert payload["pack"] == "795"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-post-stack-beta-preflight-save-readiness-note-draft-v795.json"
    assert payload["source_pack"] == "794"
    assert payload["current_packs"] == "790-839"
    assert payload["save_block"] == "790-839"
    assert payload["next_pack"] == "796"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_796"] is True


def test_pack_795_summary_safety():
    mod = importlib.import_module("tower.tower_tower_post_stack_beta_preflight_save_readiness_note_draft_v795")
    payload = mod.build_tower_post_stack_beta_preflight_save_readiness_note_draft_preview()
    summary = payload["tower_post_stack_beta_preflight_save_readiness_note_draft_summary"]

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
    assert summary["tower_post_stack_beta_preflight_save_readiness_note_draft_ready"] is True
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


def test_pack_795_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_post_stack_beta_preflight_save_readiness_note_draft_v795")
    bridge = mod.build_pack_795_status_bridge()
    prep = mod.prepare_pack_796_tower_post_stack_beta_preflight_save_readiness_note_version()

    assert bridge["pack"] == "795"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_post_stack_beta_preflight_save_readiness_note_draft_ready"] is True
    assert bridge["safe_to_continue_to_pack_796"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "796"
    assert prep["source_pack"] == "795"

    first = mod.build_tower_post_stack_beta_preflight_save_readiness_note_draft_preview()
    second = mod.build_tower_post_stack_beta_preflight_save_readiness_note_draft_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_post_stack_beta_preflight_save_readiness_note_draft_preview()
    assert third["status"] == "ready"
