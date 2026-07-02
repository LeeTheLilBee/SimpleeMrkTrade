"""
SEARCHABLE LABEL: TOWER_ONE_CELL_PACK_1554_1604_PACK_1600_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_1600_ready():
    mod = importlib.import_module("tower.tower_tower_beta_owner_go_no_go_decision_closeout_note_draft_v1600")
    payload = mod.build_tower_beta_owner_go_no_go_decision_closeout_note_draft_preview()

    assert payload["pack"] == "1600"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-owner-go-no-go-decision-closeout-note-draft-v1600.json"
    assert payload["source_pack"] == "1599"
    assert payload["current_packs"] == "1555-1604"
    assert payload["save_block"] == "1554-1604"
    assert payload["next_pack"] == "1601"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_1601"] is True


def test_pack_1600_summary_safety_no_pivot():
    mod = importlib.import_module("tower.tower_tower_beta_owner_go_no_go_decision_closeout_note_draft_v1600")
    payload = mod.build_tower_beta_owner_go_no_go_decision_closeout_note_draft_preview()
    summary = payload["tower_beta_owner_go_no_go_decision_closeout_note_draft_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 70
    assert summary["check_count"] >= 30
    assert summary["decision_category_count"] >= 15
    assert summary["decision_item_count"] >= 24
    assert summary["blocked_real_action_count"] >= 31
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_real_actions_disabled"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_beta_owner_go_no_go_decision_closeout_note_draft_ready"] is True
    assert summary["owner_go_no_go_decision_active"] is True
    assert summary["real_go_decision_apply_enabled"] is False
    assert summary["real_no_go_decision_apply_enabled"] is False
    assert summary["real_owner_approval_apply_enabled"] is False
    assert summary["real_controlled_unlock_apply_enabled"] is False
    assert summary["real_emergency_lockback_apply_enabled"] is False
    assert summary["pivot_to_access_home"] is False
    assert summary["pivot_to_admin_dashboard"] is False
    assert summary["pivot_to_waitlist"] is False
    assert summary["pivot_to_initial_setup"] is False
    assert summary["real_beta_unlock_enabled"] is False
    assert summary["real_beta_launch_command_enabled"] is False
    assert summary["real_account_mutation_enabled"] is False
    assert summary["real_access_grant_mutation_enabled"] is False
    assert summary["real_access_revoke_mutation_enabled"] is False
    assert summary["real_mfa_enrollment_enabled"] is False
    assert summary["real_setup_email_send_enabled"] is False
    assert summary["real_password_store_enabled"] is False
    assert summary["real_owner_console_mutation_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_1600_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_beta_owner_go_no_go_decision_closeout_note_draft_v1600")
    bridge = mod.build_pack_1600_status_bridge()
    prep = mod.prepare_pack_1601_tower_beta_owner_go_no_go_decision_closeout_note_version()

    assert bridge["pack"] == "1600"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_owner_go_no_go_decision_closeout_note_draft_ready"] is True
    assert bridge["safe_to_continue_to_pack_1601"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1601"
    assert prep["source_pack"] == "1600"

    first = mod.build_tower_beta_owner_go_no_go_decision_closeout_note_draft_preview()
    second = mod.build_tower_beta_owner_go_no_go_decision_closeout_note_draft_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_beta_owner_go_no_go_decision_closeout_note_draft_preview()
    assert third["status"] == "ready"
