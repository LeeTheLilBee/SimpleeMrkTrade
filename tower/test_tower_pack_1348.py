"""
SEARCHABLE LABEL: TOWER_ONE_CELL_PACK_1299_1349_PACK_1348_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_1348_ready():
    mod = importlib.import_module("tower.tower_tower_beta_launch_receipt_archive_review_closeout_readiness_bridge_v1348")
    payload = mod.build_tower_beta_launch_receipt_archive_review_closeout_readiness_bridge_preview()

    assert payload["pack"] == "1348"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-launch-receipt-archive-review-closeout-readiness-bridge-v1348.json"
    assert payload["source_pack"] == "1347"
    assert payload["current_packs"] == "1300-1349"
    assert payload["save_block"] == "1299-1349"
    assert payload["next_pack"] == "1349"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_1349"] is True


def test_pack_1348_summary_safety():
    mod = importlib.import_module("tower.tower_tower_beta_launch_receipt_archive_review_closeout_readiness_bridge_v1348")
    payload = mod.build_tower_beta_launch_receipt_archive_review_closeout_readiness_bridge_preview()
    summary = payload["tower_beta_launch_receipt_archive_review_closeout_readiness_bridge_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 61
    assert summary["check_count"] >= 19
    assert summary["archive_field_count"] >= 13
    assert summary["archive_item_count"] >= 19
    assert summary["blocked_real_action_count"] >= 29
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_real_actions_disabled"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_beta_launch_receipt_archive_review_closeout_readiness_bridge_ready"] is True
    assert summary["real_beta_launch_receipt_archive_enabled"] is False
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


def test_pack_1348_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_beta_launch_receipt_archive_review_closeout_readiness_bridge_v1348")
    bridge = mod.build_pack_1348_status_bridge()
    prep = mod.prepare_pack_1349_tower_beta_launch_receipt_archive_review_closeout_batch_close_readiness()

    assert bridge["pack"] == "1348"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_launch_receipt_archive_review_closeout_readiness_bridge_ready"] is True
    assert bridge["safe_to_continue_to_pack_1349"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1349"
    assert prep["source_pack"] == "1348"

    first = mod.build_tower_beta_launch_receipt_archive_review_closeout_readiness_bridge_preview()
    second = mod.build_tower_beta_launch_receipt_archive_review_closeout_readiness_bridge_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_beta_launch_receipt_archive_review_closeout_readiness_bridge_preview()
    assert third["status"] == "ready"
