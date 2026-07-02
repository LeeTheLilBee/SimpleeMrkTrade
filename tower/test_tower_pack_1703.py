"""
SEARCHABLE LABEL: TOWER_ONE_CELL_PACK_1656_1706_PACK_1703_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_1703_ready():
    mod = importlib.import_module("tower.tower_tower_beta_access_monitoring_first_user_safety_closeout_note_version_v1703")
    payload = mod.build_tower_beta_access_monitoring_first_user_safety_closeout_note_version_preview()

    assert payload["pack"] == "1703"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-access-monitoring-first-user-safety-closeout-note-version-v1703.json"
    assert payload["source_pack"] == "1702"
    assert payload["current_packs"] == "1657-1706"
    assert payload["save_block"] == "1656-1706"
    assert payload["next_pack"] == "1704"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_1704"] is True


def test_pack_1703_summary_safety_no_pivot():
    mod = importlib.import_module("tower.tower_tower_beta_access_monitoring_first_user_safety_closeout_note_version_v1703")
    payload = mod.build_tower_beta_access_monitoring_first_user_safety_closeout_note_version_preview()
    summary = payload["tower_beta_access_monitoring_first_user_safety_closeout_note_version_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 82
    assert summary["check_count"] >= 30
    assert summary["monitoring_category_count"] >= 15
    assert summary["monitoring_item_count"] >= 28
    assert summary["blocked_real_action_count"] >= 39
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_real_actions_disabled"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_beta_access_monitoring_first_user_safety_closeout_note_version_ready"] is True
    assert summary["access_monitoring_first_user_safety_active"] is True
    assert summary["real_access_monitoring_activation_enabled"] is False
    assert summary["real_first_user_access_grant_enabled"] is False
    assert summary["real_first_user_access_revoke_enabled"] is False
    assert summary["real_account_mutation_enabled"] is False
    assert summary["real_user_mutation_enabled"] is False
    assert summary["real_session_revoke_enabled"] is False
    assert summary["real_route_lock_mutation_enabled"] is False
    assert summary["real_controlled_unlock_apply_enabled"] is False
    assert summary["real_emergency_lockback_apply_enabled"] is False
    assert summary["real_beta_unlock_enabled"] is False
    assert summary["pivot_to_access_home"] is False
    assert summary["pivot_to_admin_dashboard"] is False
    assert summary["pivot_to_waitlist"] is False
    assert summary["pivot_to_initial_setup"] is False
    assert summary["real_mfa_enrollment_enabled"] is False
    assert summary["real_setup_email_send_enabled"] is False
    assert summary["real_password_store_enabled"] is False
    assert summary["real_clouds_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["external_share_enabled"] is False
    assert summary["save_push_performed"] is False


def test_pack_1703_bridge_prep_copy():
    mod = importlib.import_module("tower.tower_tower_beta_access_monitoring_first_user_safety_closeout_note_version_v1703")
    bridge = mod.build_pack_1703_status_bridge()
    prep = mod.prepare_pack_1704_tower_beta_access_monitoring_first_user_safety_closeout_handoff_contract()

    assert bridge["pack"] == "1703"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_access_monitoring_first_user_safety_closeout_note_version_ready"] is True
    assert bridge["safe_to_continue_to_pack_1704"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1704"
    assert prep["source_pack"] == "1703"

    first = mod.build_tower_beta_access_monitoring_first_user_safety_closeout_note_version_preview()
    second = mod.build_tower_beta_access_monitoring_first_user_safety_closeout_note_version_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_tower_beta_access_monitoring_first_user_safety_closeout_note_version_preview()
    assert third["status"] == "ready"
