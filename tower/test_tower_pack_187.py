
"""
PACK 187 fast test - Owner Note Saved View Preset Detail Edit History Version Compare
Saved View / Filter Preset Detail Edit History Version Detail / Compare View.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_187_payload_ready_and_preview_only():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_payload(force_refresh=True)

    assert payload["pack_number"] == 187
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-detail-compare-view.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-preview.json"

    required_true = [
        "simulated_only",
        "version_detail_preview_only",
        "compare_view_preview_only",
        "edit_history_preview_only",
        "version_preview_only",
        "rollback_preview_only",
        "restore_preview_only",
        "compare_preview_only",
        "detail_edit_preview_only",
        "saved_view_preview_only",
        "filter_preset_preview_only",
        "navigation_preview_only",
        "filter_navigation_preview_only",
        "saved_view_preset_detail_preview_only",
        "saved_view_preset_edit_preview_only",
        "saved_navigation_preview_only",
        "saved_filter_preset_preview_only",
        "cached_non_recursive",
    ]

    for key in required_true:
        assert payload[key] is True, key

    required_false = [
        "real_saved_view_written",
        "real_user_preference_written",
        "real_filter_preference_saved",
        "real_navigation_state_persisted",
        "real_drawer_selection_saved",
        "real_history_written",
        "real_version_written",
        "real_version_saved",
        "real_rollback_executed",
        "real_restore_executed",
        "real_edit_persisted",
    ]

    for key in required_false:
        assert payload[key] is False, key

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["version_detail_drawer_count"] >= 15
    assert summary["saved_view_version_detail_drawer_count"] == 6
    assert summary["filter_preset_version_detail_drawer_count"] >= 9
    assert summary["version_card_count"] >= 45
    assert summary["comparison_row_count"] >= 75
    assert summary["changed_compare_row_count"] >= 1
    assert summary["unchanged_compare_row_count"] >= 1
    assert summary["rollback_action_preview_count"] >= 15
    assert summary["restore_action_preview_count"] >= 15
    assert summary["save_action_preview_count"] >= 15

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_186_ready",
        "has_timelines",
        "has_version_detail_drawers",
        "version_detail_drawer_count_matches_timelines",
        "saved_view_drawer_count_is_six",
        "filter_preset_drawer_count_is_nine",
        "all_version_detail_drawers_ready",
        "all_drawers_have_three_version_cards",
        "all_drawers_have_five_compare_rows",
        "has_compare_rows",
        "has_changed_compare_rows",
        "has_unchanged_compare_rows",
        "has_version_cards",
        "all_compare_rows_ready",
        "all_rollback_actions_blocked",
        "all_restore_actions_blocked",
        "all_save_actions_blocked",
        "version_detail_indexes_present",
        "compare_row_indexes_present",
        "changed_compare_row_indexes_present",
        "unchanged_compare_row_indexes_present",
        "version_card_indexes_present",
        "all_simulated_only",
        "all_version_detail_preview_only",
        "all_compare_view_preview_only",
        "all_edit_history_preview_only",
        "all_version_preview_only",
        "all_rollback_preview_only",
        "all_restore_preview_only",
        "no_real_history_written",
        "no_real_version_written",
        "no_real_version_saved",
        "no_real_rollback_executed",
        "no_real_restore_executed",
        "no_real_edit_persisted",
        "no_real_saved_view_written",
        "no_real_user_preference_written",
        "all_history_writes_blocked",
        "all_version_writes_blocked",
        "all_version_saves_blocked",
        "all_saves_blocked",
        "all_persists_blocked",
        "all_raw_evidence_reveal_blocked",
        "all_raw_evidence_lookup_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_187_version_detail_drawers_compare_rows_and_blocked_actions():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_payload(force_refresh=True)

    drawers = payload["version_detail_drawers"]

    assert len(drawers) >= 15

    for drawer in drawers:
        assert drawer["version_detail_drawer_id"].startswith("version_compare_saved_view_filter_detail_edit_version_detail_compare_drawer_")
        assert drawer["edit_history_timeline_id"]
        assert drawer["detail_edit_drawer_id"]
        assert drawer["source_kind"] in {"saved_view_preset", "filter_preset"}
        assert drawer["source_id"]
        assert drawer["drawer_status"] == "version_compare_saved_view_filter_detail_edit_version_detail_compare_drawer_preview_ready"
        assert drawer["drawer_result_type"] == "owner_note_version_compare_saved_view_filter_detail_edit_version_detail_compare_drawer_preview"
        assert drawer["version_card_count"] == 3
        assert drawer["comparison_row_count"] == 5
        assert len(drawer["compare_rows"]) == 5
        assert len(drawer["comparison_rows"]) == 5
        assert isinstance(drawer["changed_compare_rows"], list)
        assert isinstance(drawer["unchanged_compare_rows"], list)
        assert drawer["changed_field_count"] + drawer["unchanged_field_count"] == 5

        grouping = drawer["compare_grouping"]
        assert "changed_fields" in grouping
        assert "unchanged_fields" in grouping
        assert grouping["changed_fields"]["row_count"] == drawer["changed_field_count"]
        assert grouping["unchanged_fields"]["row_count"] == drawer["unchanged_field_count"]

        rollback = drawer["rollback_action_preview"]
        restore = drawer["restore_action_preview"]
        save = drawer["save_action_preview"]

        assert rollback["allowed_in_preview"] is True
        assert rollback["allowed_now"] is False
        assert rollback["real_rollback_executed"] is False
        assert restore["allowed_in_preview"] is True
        assert restore["allowed_now"] is False
        assert restore["real_restore_executed"] is False
        assert save["allowed_in_preview"] is True
        assert save["allowed_now"] is False
        assert save["real_version_saved"] is False
        assert save["real_edit_persisted"] is False

        assert drawer["simulated_only"] is True
        assert drawer["version_detail_preview_only"] is True
        assert drawer["compare_view_preview_only"] is True
        assert drawer["edit_history_preview_only"] is True
        assert drawer["version_preview_only"] is True
        assert drawer["rollback_preview_only"] is True
        assert drawer["restore_preview_only"] is True
        assert drawer["detail_edit_preview_only"] is True
        assert drawer["saved_view_preview_only"] is True
        assert drawer["filter_preset_preview_only"] is True
        assert drawer["real_history_written"] is False
        assert drawer["real_version_written"] is False
        assert drawer["real_version_saved"] is False
        assert drawer["real_rollback_executed"] is False
        assert drawer["real_restore_executed"] is False
        assert drawer["real_edit_persisted"] is False
        assert drawer["real_saved_view_written"] is False
        assert drawer["real_user_preference_written"] is False
        assert drawer["history_write_allowed_now"] is False
        assert drawer["version_write_allowed_now"] is False
        assert drawer["version_save_allowed_now"] is False
        assert drawer["rollback_allowed_now"] is False
        assert drawer["restore_allowed_now"] is False
        assert drawer["save_allowed_now"] is False
        assert drawer["persist_allowed_now"] is False

        for row in drawer["compare_rows"]:
            assert row["version_compare_row_id"].startswith("version_compare_saved_view_filter_detail_edit_compare_row_")
            assert row["edit_history_timeline_id"] == drawer["edit_history_timeline_id"]
            assert row["detail_edit_drawer_id"] == drawer["detail_edit_drawer_id"]
            assert row["source_kind"] == drawer["source_kind"]
            assert row["source_id"] == drawer["source_id"]
            assert row["field_change_event_id"]
            assert row["field_id"]
            assert row["field_label"]
            assert row["field_type"]
            assert isinstance(row["changed"], bool)
            assert row["change_group"] in {"changed_fields", "unchanged_fields"}
            assert row["left_version_label"] == "Original Detail Edit Snapshot"
            assert row["right_version_label"] == "Draft Detail Edit Snapshot"
            assert row["row_status"] == "version_compare_saved_view_filter_detail_edit_compare_row_preview_ready"
            assert row["row_result_type"] == "owner_note_version_compare_saved_view_filter_detail_edit_compare_row_preview"
            assert row["safe_preview_only"] is True

            assert row["simulated_only"] is True
            assert row["version_detail_preview_only"] is True
            assert row["compare_view_preview_only"] is True
            assert row["edit_history_preview_only"] is True
            assert row["version_preview_only"] is True
            assert row["real_history_written"] is False
            assert row["real_version_written"] is False
            assert row["real_version_saved"] is False
            assert row["real_rollback_executed"] is False
            assert row["real_restore_executed"] is False
            assert row["real_edit_persisted"] is False
            assert row["real_saved_view_written"] is False
            assert row["real_user_preference_written"] is False


def test_pack_187_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_payload(force_refresh=True)

    indexes = payload["version_detail_compare_indexes"]

    assert indexes["version_detail_drawers_by_id"]
    assert indexes["version_detail_drawers_by_timeline_id"]
    assert indexes["version_detail_drawers_by_detail_edit_drawer_id"]
    assert indexes["version_detail_drawers_by_source_kind"]
    assert indexes["version_detail_drawers_by_source_id"]
    assert indexes["compare_rows_by_id"]
    assert indexes["compare_rows_by_drawer_id"]
    assert indexes["compare_rows_by_source_kind"]
    assert indexes["changed_compare_rows_by_drawer_id"]
    assert indexes["unchanged_compare_rows_by_drawer_id"]
    assert indexes["version_cards_by_id"]

    assert "saved_view_preset" in indexes["version_detail_drawers_by_source_kind"]
    assert "filter_preset" in indexes["version_detail_drawers_by_source_kind"]
    assert "saved_view_preset" in indexes["compare_rows_by_source_kind"]
    assert "filter_preset" in indexes["compare_rows_by_source_kind"]

    bridge = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 187
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-detail-compare-view.json"
    assert bridge["version_detail_drawer_count"] >= 15
    assert bridge["saved_view_version_detail_drawer_count"] == 6
    assert bridge["filter_preset_version_detail_drawer_count"] >= 9
    assert bridge["version_card_count"] >= 45
    assert bridge["comparison_row_count"] >= 75
    assert bridge["changed_compare_row_count"] >= 1
    assert bridge["rollback_action_preview_count"] >= 15
    assert bridge["restore_action_preview_count"] >= 15
    assert bridge["save_action_preview_count"] >= 15

    action = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-detail-compare-view.json"
    assert action["status"] == "ready"

    section = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-detail-compare-view.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_187_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_status_bridge")
    tower_bridge = status.build_pack_187_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_187_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_quick_action")
    assert hasattr(qa, "append_pack_187_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_quick_action")
    actions = qa.append_pack_187_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_quick_action([])
    assert any(item.get("id") == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_187_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_unified_section")
    assert hasattr(unified, "append_pack_187_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_section")
    sections = unified.append_pack_187_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_section([])
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-detail-compare-view.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_json" in app_text
    assert "_pack_187_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-detail-compare-view.json" in route_text
    assert "_pack_187_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_route_guard" in route_text

    payload_text = str(payload).lower()
    forbidden_fragments = [
        "sk_live_",
        "sk_test_",
        "github_pat_",
        "ghp_",
        "xoxb-",
        "aws_secret_access_key",
        "private_key-----",
        "broker_token_value",
        "api_secret_value",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in payload_text
