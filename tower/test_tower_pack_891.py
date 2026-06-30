"""
SEARCHABLE LABEL: TOWER_PACK_891_BETA_OWNER_GO_NO_GO_SAVE_READINESS_TESTS
"""

from __future__ import annotations

from tower.tower_beta_owner_go_no_go_save_readiness_index_v891 import (
    build_tower_beta_owner_go_no_go_save_readiness_index_preview,
    build_pack_891_status_bridge,
    prepare_pack_892_tower_beta_release_candidate_index,
)


def test_pack_891_beta_owner_go_no_go_save_readiness_ready():
    payload = build_tower_beta_owner_go_no_go_save_readiness_index_preview()

    assert payload["pack"] == "891"
    assert payload["pack_number"] == 891
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/beta-owner-go-no-go-save-readiness-index-v891.json"
    assert payload["source_block"] == "840-890"
    assert payload["source_pack"] == "890"
    assert payload["next_pack"] == "892"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["go_no_go_save_readiness_preview_only"] is True
    assert payload["safe_to_continue_to_pack_892"] is True


def test_pack_891_summary_safety():
    payload = build_tower_beta_owner_go_no_go_save_readiness_index_preview()
    summary = payload["tower_pack_891_summary"]

    assert summary["source_block"] == "840-890"
    assert summary["source_pack"] == "890"
    assert summary["row_count"] >= 33
    assert summary["check_count"] >= 13
    assert summary["post_go_no_go_save_check_count"] >= 8
    assert summary["next_corridor_hint_count"] >= 5
    assert summary["blocked_real_action_count"] >= 20
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_pack_891_ready"] is True
    assert summary["real_release_candidate_approval_enabled"] is False
    assert summary["real_beta_go_decision_enabled"] is False
    assert summary["real_beta_unlock_enabled"] is False
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["real_save_push_execution_enabled"] is False


def test_pack_891_bridge_prep_and_copy():
    bridge = build_pack_891_status_bridge()
    prep = prepare_pack_892_tower_beta_release_candidate_index()

    assert bridge["pack"] == "891"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_pack_891_ready"] is True
    assert bridge["safe_to_continue_to_pack_892"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "892"
    assert prep["source_pack"] == "891"

    first = build_tower_beta_owner_go_no_go_save_readiness_index_preview()
    second = build_tower_beta_owner_go_no_go_save_readiness_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = build_tower_beta_owner_go_no_go_save_readiness_index_preview()
    assert third["status"] == "ready"
