"""
SEARCHABLE LABEL: TOWER_ONE_CELL_PACK_1248_1298_PACK_1291_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_1291_ready():
    mod = importlib.import_module("tower.tower_tower_beta_launch_receipt_close_review_closeout_close_matrix_v1291")
    payload = mod.build_tower_beta_launch_receipt_close_review_closeout_close_matrix_preview()

    assert payload["pack"] == "1291"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-launch-receipt-close-review-closeout-close-matrix-v1291.json"
    assert payload["source_pack"] == "1290"
    assert payload["current_packs"] == "1249-1298"
    assert payload["save_block"] == "1248-1298"
    assert payload["next_pack"] == "1292"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_1292"] is True


def test_pack_1291_summary_safety():
    mod = importlib.import_module("tower.tower_tower_beta_launch_receipt_close_review_closeout_close_matrix_v1291")
    payload = mod.build_tower_beta_launch_receipt_close_review_closeout_close_matrix_preview()
    summary = payload["tower_beta_launch_receipt_close_review_closeout_close_matrix_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 59
    assert summary["check_count"] >= 18
    assert summary["close_field_count"] >= 13
    assert summary["close_item_count"] >= 18
    assert summary["blocked_real_action_count"] >= 28
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_real_actions_disabled"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_beta_launch_receipt_close_review_closeout_close_matrix_ready"] is True
    assert summary["real_beta_launch_receipt_close_enabled"] is False
    assert summary["real_beta_launch_command_receipt_issue_enabled"] is False
    assert summary["real_beta_launch_command_enabled"] is False
    assert summary["real_beta_launch_authorization_enabled"] is False
    assert summary["real_beta_unlock_enabled"] is False
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_1291_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_beta_launch_receipt_close_review_closeout_close_matrix_v1291")
    bridge = mod.build_pack_1291_status_bridge()
    prep = mod.prepare_pack_1292_tower_beta_launch_receipt_close_review_closeout_detail_drawer()

    assert bridge["pack"] == "1291"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_launch_receipt_close_review_closeout_close_matrix_ready"] is True
    assert bridge["safe_to_continue_to_pack_1292"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1292"
    assert prep["source_pack"] == "1291"

    first = mod.build_tower_beta_launch_receipt_close_review_closeout_close_matrix_preview()
    second = mod.build_tower_beta_launch_receipt_close_review_closeout_close_matrix_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_beta_launch_receipt_close_review_closeout_close_matrix_preview()
    assert third["status"] == "ready"
