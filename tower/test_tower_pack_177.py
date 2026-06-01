
"""
PACK 177 fast test - Owner Note Saved View Preset Version Detail / Compare View.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_177_payload_ready_and_version_detail_compare_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view")
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload(force_refresh=True)

    assert payload["pack_number"] == 177
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-detail-compare-view.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-edit-history-version-preview.json"

    assert payload["simulated_only"] is True
    assert payload["version_detail_preview_only"] is True
    assert payload["compare_view_preview_only"] is True
    assert payload["edit_history_preview_only"] is True
    assert payload["version_preview_only"] is True
    assert payload["rollback_preview_only"] is True
    assert payload["saved_view_preset_detail_preview_only"] is True
    assert payload["saved_view_preset_edit_preview_only"] is True
    assert payload["saved_navigation_preview_only"] is True
    assert payload["saved_filter_preset_preview_only"] is True
    assert payload["navigation_preview_only"] is True
    assert payload["filter_navigation_preview_only"] is True
    assert payload["saved_view_preview_only"] is True
    assert payload["filter_preset_preview_only"] is True

    assert payload["real_history_written"] is False
    assert payload["real_version_written"] is False
    assert payload["real_version_saved"] is False
    assert payload["real_rollback_executed"] is False
    assert payload["real_restore_executed"] is False
    assert payload["real_edit_persisted"] is False
    assert payload["real_saved_view_written"] is False
    assert payload["real_user_preference_written"] is False
    assert payload["real_filter_preference_saved"] is False
    assert payload["real_navigation_state_persisted"] is False
    assert payload["real_drawer_selection_saved"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["version_detail_drawer_count"] == 6
    assert summary["source_edit_history_timeline_count"] == 6
    assert summary["comparison_row_count"] == 30
    assert summary["drawer_section_count"] >= 42
    assert summary["version_card_count"] == 18
    assert summary["field_change_event_count"] == 30
    assert summary["compare_field_count"] == 5

    checks = payload["readiness_checks"]
    required_true_checks = [
        "pack_176_ready",
        "has_version_detail_drawers",
        "drawer_count_matches_timelines",
        "all_drawers_ready",
        "all_have_five_compare_rows",
        "all_have_three_version_cards",
        "all_have_five_field_change_events",
        "all_have_seven_drawer_sections",
        "all_have_comparison_groups",
        "all_have_original_snapshot",
        "all_have_preview_edit_snapshot",
        "all_simulated_only",
        "all_version_detail_preview_only",
        "all_compare_view_preview_only",
        "all_edit_history_preview_only",
        "all_version_preview_only",
        "all_rollback_preview_only",
        "all_saved_view_preset_detail_preview_only",
        "all_saved_view_preset_edit_preview_only",
        "all_saved_navigation_preview_only",
        "all_saved_filter_preset_preview_only",
        "all_navigation_preview_only",
        "all_filter_navigation_preview_only",
        "all_saved_view_preview_only",
        "all_filter_preset_preview_only",
        "no_real_history_written",
        "no_real_version_written",
        "no_real_version_saved",
        "no_real_rollback_executed",
        "no_real_restore_executed",
        "no_real_edit_persisted",
        "no_real_saved_view_written",
        "no_real_user_preference_written",
        "no_real_filter_preference_saved",
        "no_real_navigation_state_persisted",
        "no_real_drawer_selection_saved",
        "all_restore_actions_blocked",
        "all_rollback_actions_blocked",
        "all_save_actions_blocked",
        "all_persist_actions_blocked",
        "all_history_writes_blocked",
        "all_version_writes_blocked",
        "all_saved_view_writes_blocked",
        "all_user_preference_writes_blocked",
        "all_raw_evidence_reveal_blocked",
        "all_raw_evidence_lookup_blocked",
        "default_all_compare_drawers_drawer_present",
        "owner_review_focus_drawer_present",
        "critical_priority_focus_drawer_present",
        "high_priority_focus_drawer_present",
        "monitor_only_focus_drawer_present",
        "safe_preview_focus_drawer_present",
        "cached_non_recursive",
    ]

    for key in required_true_checks:
        assert checks[key] is True, key


def test_pack_177_version_detail_drawers_compare_rows_and_groups_are_ready():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view")
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload(force_refresh=True)

    drawers = payload["version_detail_drawers"]
    expected_presets = {
        "default_all_compare_drawers",
        "owner_review_focus",
        "critical_priority_focus",
        "high_priority_focus",
        "monitor_only_focus",
        "safe_preview_focus",
    }
    expected_fields = {
        "label",
        "description",
        "filter_lane_id",
        "view_priority",
        "is_default",
    }
    expected_sections = {
        "version_identity",
        "original_snapshot",
        "preview_edit_snapshot",
        "compare_rows",
        "blocked_restore_rollback",
        "blocked_history_version_writes",
        "safety_flags",
    }

    assert len(drawers) == 6
    assert expected_presets.issubset({drawer["saved_view_preset_id"] for drawer in drawers})

    for drawer in drawers:
        assert drawer["version_detail_drawer_id"].startswith("saved_view_preset_version_detail_compare_drawer_")
        assert drawer["saved_view_preset_id"] in expected_presets
        assert drawer["edit_history_timeline_id"].startswith("saved_view_preset_edit_history_timeline_")
        assert drawer["detail_edit_drawer_id"].startswith("saved_view_preset_detail_edit_drawer_")
        assert drawer["label"]
        assert drawer["filter_lane_id"]
        assert drawer["view_priority"] in {"critical", "high", "medium", "standard", "monitor"}
        assert isinstance(drawer["is_default"], bool)

        assert drawer["drawer_status"] == "saved_view_preset_version_detail_compare_view_preview_ready"
        assert drawer["drawer_result_type"] == "owner_note_saved_view_preset_version_detail_compare_drawer_preview"
        assert isinstance(drawer["original_snapshot"], dict)
        assert isinstance(drawer["preview_edit_snapshot"], dict)
        assert drawer["original_snapshot"]
        assert drawer["preview_edit_snapshot"]

        assert drawer["version_card_count"] == 3
        assert drawer["field_change_event_count"] == 5
        assert drawer["comparison_row_count"] == 5
        assert drawer["drawer_section_count"] >= 7

        compare_field_ids = {row["field_id"] for row in drawer["compare_rows"]}
        assert expected_fields.issubset(compare_field_ids)

        for row in drawer["compare_rows"]:
            assert row["compare_row_id"].startswith("saved_view_preset_version_compare_row_")
            assert row["saved_view_preset_id"] == drawer["saved_view_preset_id"]
            assert row["edit_history_timeline_id"] == drawer["edit_history_timeline_id"]
            assert row["detail_edit_drawer_id"] == drawer["detail_edit_drawer_id"]
            assert row["field_id"] in expected_fields
            assert row["field_label"]
            assert isinstance(row["original_value"], dict)
            assert isinstance(row["preview_value"], dict)
            assert isinstance(row["changed"], bool)
            assert row["comparison_status"] == "saved_view_preset_version_compare_row_preview_ready"
            assert row["comparison_result_type"] == "owner_note_saved_view_preset_version_compare_row_preview"
            assert row["safe_preview_only"] is True
            assert row["restore_allowed_now"] is False
            assert row["rollback_allowed_now"] is False
            assert row["save_allowed_now"] is False
            assert row["persist_allowed_now"] is False
            assert row["history_write_allowed_now"] is False
            assert row["version_write_allowed_now"] is False
            assert row["saved_view_write_allowed_now"] is False
            assert row["user_preference_write_allowed_now"] is False
            assert row["raw_evidence_reveal_allowed"] is False
            assert row["raw_evidence_lookup_allowed"] is False
            assert row["real_history_written"] is False
            assert row["real_version_written"] is False
            assert row["real_version_saved"] is False
            assert row["real_rollback_executed"] is False
            assert row["real_restore_executed"] is False
            assert row["real_edit_persisted"] is False
            assert row["real_saved_view_written"] is False
            assert row["real_user_preference_written"] is False
            assert row["simulated_only"] is True
            assert row["version_detail_preview_only"] is True
            assert row["compare_view_preview_only"] is True

        groups = drawer["comparison_groups"]
        assert groups["group_status"] == "saved_view_preset_version_compare_groups_preview_ready"
        assert groups["group_result_type"] == "owner_note_saved_view_preset_version_compare_groups_preview"
        assert groups["safe_preview_only"] is True
        assert groups["cached_non_recursive"] is True
        assert groups["changed_fields"]["count"] + groups["unchanged_fields"]["count"] == 5
        assert isinstance(groups["changed_fields"]["rows"], list)
        assert isinstance(groups["unchanged_fields"]["rows"], list)

        section_ids = {section["section_id"] for section in drawer["drawer_sections"]}
        assert expected_sections.issubset(section_ids)

        assert drawer["restore_allowed_now"] is False
        assert drawer["rollback_allowed_now"] is False
        assert drawer["save_allowed_now"] is False
        assert drawer["persist_allowed_now"] is False
        assert drawer["history_write_allowed_now"] is False
        assert drawer["version_write_allowed_now"] is False
        assert drawer["saved_view_write_allowed_now"] is False
        assert drawer["user_preference_write_allowed_now"] is False
        assert drawer["raw_evidence_reveal_allowed"] is False
        assert drawer["raw_evidence_lookup_allowed"] is False
        assert drawer["real_history_written"] is False
        assert drawer["real_version_written"] is False
        assert drawer["real_version_saved"] is False
        assert drawer["real_rollback_executed"] is False
        assert drawer["real_restore_executed"] is False
        assert drawer["real_edit_persisted"] is False


def test_pack_177_indexes_bridge_quick_action_unified_route_and_no_secrets():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view")
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload(force_refresh=True)

    indexes = payload["version_detail_indexes"]
    assert indexes["by_version_detail_drawer_id"]
    assert indexes["by_edit_history_timeline_id"]
    assert indexes["by_detail_edit_drawer_id"]
    assert indexes["by_saved_view_preset_id"]
    assert indexes["by_filter_lane_id"]
    assert indexes["by_view_priority"]
    assert indexes["by_default_state"]
    assert indexes["by_drawer_status"]
    assert indexes["compare_rows_by_id"]

    assert "default_all_compare_drawers" in indexes["by_saved_view_preset_id"]
    assert "owner_review_focus" in indexes["by_saved_view_preset_id"]
    assert "critical_priority_focus" in indexes["by_saved_view_preset_id"]
    assert "high_priority_focus" in indexes["by_saved_view_preset_id"]
    assert "monitor_only_focus" in indexes["by_saved_view_preset_id"]
    assert "safe_preview_focus" in indexes["by_saved_view_preset_id"]
    assert "default" in indexes["by_default_state"]
    assert "not_default" in indexes["by_default_state"]
    assert "saved_view_preset_version_detail_compare_view_preview_ready" in indexes["by_drawer_status"]

    bridge = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 177
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-detail-compare-view.json"
    assert bridge["version_detail_drawer_count"] == 6
    assert bridge["source_edit_history_timeline_count"] == 6
    assert bridge["comparison_row_count"] == 30
    assert bridge["drawer_section_count"] >= 42
    assert bridge["version_card_count"] == 18
    assert bridge["field_change_event_count"] == 30
    assert bridge["compare_field_count"] == 5
    assert bridge["simulated_only"] is True
    assert bridge["version_detail_preview_only"] is True
    assert bridge["compare_view_preview_only"] is True
    assert bridge["edit_history_preview_only"] is True
    assert bridge["version_preview_only"] is True
    assert bridge["rollback_preview_only"] is True
    assert bridge["real_history_written"] is False
    assert bridge["real_version_written"] is False
    assert bridge["real_version_saved"] is False
    assert bridge["real_rollback_executed"] is False
    assert bridge["real_restore_executed"] is False
    assert bridge["real_edit_persisted"] is False
    assert bridge["real_saved_view_written"] is False
    assert bridge["real_user_preference_written"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-detail-compare-view.json"
    assert action["status"] == "ready"

    section = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-detail-compare-view.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_status_bridge")
    tower_bridge = status.build_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_quick_action")
    assert hasattr(qa, "append_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_quick_action")
    actions = qa.append_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_quick_action([])
    assert any(item.get("id") == "policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_unified_section")
    assert hasattr(unified, "append_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_section")
    sections = unified.append_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_section([])
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-detail-compare-view.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_json" in app_text
    assert "_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-detail-compare-view.json" in route_text
    assert "_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_route_guard" in route_text

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
