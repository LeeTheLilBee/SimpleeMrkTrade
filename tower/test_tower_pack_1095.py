"""
SEARCHABLE LABEL: TOWER_PACK_1095_BETA_LAUNCH_AUTHORIZATION_REVIEW_SAVE_READINESS_TESTS
"""

from __future__ import annotations

from tower.tower_beta_launch_authorization_review_save_readiness_index_v1095 import (
    build_tower_beta_launch_authorization_review_save_readiness_index_preview,
    build_pack_1095_status_bridge,
    prepare_pack_1096_tower_beta_launch_readiness_receipt_index,
)


def test_pack_1095_beta_launch_authorization_review_save_readiness_ready():
    payload = build_tower_beta_launch_authorization_review_save_readiness_index_preview()

    assert payload["pack"] == "1095"
    assert payload["pack_number"] == 1095
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/beta-launch-authorization-review-save-readiness-index-v1095.json"
    assert payload["source_block"] == "1044-1094"
    assert payload["source_pack"] == "1094"
    assert payload["next_pack"] == "1096"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["launch_authorization_review_save_readiness_preview_only"] is True
    assert payload["safe_to_continue_to_pack_1096"] is True


def test_pack_1095_summary_safety():
    payload = build_tower_beta_launch_authorization_review_save_readiness_index_preview()
    summary = payload["tower_pack_1095_summary"]

    assert summary["source_block"] == "1044-1094"
    assert summary["source_pack"] == "1094"
    assert summary["row_count"] >= 37
    assert summary["check_count"] >= 17
    assert summary["post_launch_authorization_review_save_check_count"] >= 8
    assert summary["next_corridor_hint_count"] >= 5
    assert summary["blocked_real_action_count"] >= 24
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_pack_1095_ready"] is True
    assert summary["real_beta_launch_readiness_receipt_issue_enabled"] is False
    assert summary["real_beta_launch_authorization_enabled"] is False
    assert summary["real_beta_launch_lock_release_enabled"] is False
    assert summary["real_final_owner_review_approval_enabled"] is False
    assert summary["real_release_candidate_approval_enabled"] is False
    assert summary["real_beta_go_decision_enabled"] is False
    assert summary["real_beta_unlock_enabled"] is False
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["real_save_push_execution_enabled"] is False


def test_pack_1095_bridge_prep_and_copy():
    bridge = build_pack_1095_status_bridge()
    prep = prepare_pack_1096_tower_beta_launch_readiness_receipt_index()

    assert bridge["pack"] == "1095"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_pack_1095_ready"] is True
    assert bridge["safe_to_continue_to_pack_1096"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1096"
    assert prep["source_pack"] == "1095"

    first = build_tower_beta_launch_authorization_review_save_readiness_index_preview()
    second = build_tower_beta_launch_authorization_review_save_readiness_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = build_tower_beta_launch_authorization_review_save_readiness_index_preview()
    assert third["status"] == "ready"
