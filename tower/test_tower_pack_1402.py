"""
SEARCHABLE LABEL: TOWER_ONE_CELL_PACK_1401_1451_PACK_1402_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_1402_ready():
    mod = importlib.import_module("tower.tower_tower_final_archive_receipt_save_readiness_index_v1402")
    payload = mod.build_tower_final_archive_receipt_save_readiness_index_preview()

    assert payload["pack"] == "1402"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-final-archive-receipt-save-readiness-index-v1402.json"
    assert payload["source_pack"] == "1401"
    assert payload["current_packs"] == "1402-1451"
    assert payload["save_block"] == "1401-1451"
    assert payload["next_pack"] == "1403"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_1403"] is True


def test_pack_1402_summary_safety_no_pivot():
    mod = importlib.import_module("tower.tower_tower_final_archive_receipt_save_readiness_index_v1402")
    payload = mod.build_tower_final_archive_receipt_save_readiness_index_preview()
    summary = payload["tower_final_archive_receipt_save_readiness_index_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 70
    assert summary["check_count"] >= 23
    assert summary["final_field_count"] >= 15
    assert summary["final_item_count"] >= 23
    assert summary["blocked_real_action_count"] >= 33
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_real_actions_disabled"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_final_archive_receipt_save_readiness_index_ready"] is True
    assert summary["pivot_to_access_home"] is False
    assert summary["pivot_to_admin_dashboard"] is False
    assert summary["real_beta_launch_archive_receipt_issue_enabled"] is False
    assert summary["real_beta_unlock_enabled"] is False
    assert summary["real_live_money_permission_enabled"] is False
    assert summary["real_broker_api_enabled"] is False
    assert summary["real_order_submit_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_1402_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_final_archive_receipt_save_readiness_index_v1402")
    bridge = mod.build_pack_1402_status_bridge()
    prep = mod.prepare_pack_1403_tower_final_archive_receipt_save_readiness_registry_contract()

    assert bridge["pack"] == "1402"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_final_archive_receipt_save_readiness_index_ready"] is True
    assert bridge["safe_to_continue_to_pack_1403"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1403"
    assert prep["source_pack"] == "1402"

    first = mod.build_tower_final_archive_receipt_save_readiness_index_preview()
    second = mod.build_tower_final_archive_receipt_save_readiness_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_final_archive_receipt_save_readiness_index_preview()
    assert third["status"] == "ready"
