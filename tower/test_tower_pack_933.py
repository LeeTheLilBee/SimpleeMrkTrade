"""
SEARCHABLE LABEL: TOWER_GIANT_PACK_892_941_PACK_933_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_933_ready():
    mod = importlib.import_module("tower.tower_tower_beta_release_candidate_closeout_registry_contract_v933")
    payload = mod.build_tower_beta_release_candidate_closeout_registry_contract_preview()

    assert payload["pack"] == "933"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-release-candidate-closeout-registry-contract-v933.json"
    assert payload["source_pack"] == "932"
    assert payload["current_packs"] == "892-941"
    assert payload["save_block"] == "891-941"
    assert payload["next_pack"] == "934"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_934"] is True


def test_pack_933_summary_safety():
    mod = importlib.import_module("tower.tower_tower_beta_release_candidate_closeout_registry_contract_v933")
    payload = mod.build_tower_beta_release_candidate_closeout_registry_contract_preview()
    summary = payload["tower_beta_release_candidate_closeout_registry_contract_summary"]

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
    assert summary["tower_beta_release_candidate_closeout_registry_contract_ready"] is True
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


def test_pack_933_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_beta_release_candidate_closeout_registry_contract_v933")
    bridge = mod.build_pack_933_status_bridge()
    prep = mod.prepare_pack_934_tower_beta_release_candidate_closeout_candidate_matrix()

    assert bridge["pack"] == "933"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_release_candidate_closeout_registry_contract_ready"] is True
    assert bridge["safe_to_continue_to_pack_934"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "934"
    assert prep["source_pack"] == "933"

    first = mod.build_tower_beta_release_candidate_closeout_registry_contract_preview()
    second = mod.build_tower_beta_release_candidate_closeout_registry_contract_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_beta_release_candidate_closeout_registry_contract_preview()
    assert third["status"] == "ready"
