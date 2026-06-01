
"""
PACK 176 fast test - Owner Note Saved View Preset Edit History / Version Preview.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_176_payload_ready_and_history_version_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_payload(force_refresh=True)

    assert payload["pack_number"] == 176
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-edit-history-version-preview.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-preview.json"

    assert payload["simulated_only"] is True
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
    assert summary["edit_history_timeline_count"] == 6
    assert summary["source_detail_edit_drawer_count"] == 6
    assert summary["version_card_count"] == 18
    assert summary["field_change_event_count"] == 30
    assert summary["timeline_section_count"] >= 36
    assert summary["changed_field_count"] >= 0
    assert summary["unchanged_field_count"] >= 0

    checks = payload["readiness_checks"]
    required_true_checks = [
        "pack_175_ready",
        "has_edit_history_timelines",
        "timeline_count_matches_detail_edit_drawers",
        "all_timelines_ready",
        "all_have_three_version_cards",
        "all_have_five_field_change_events",
        "all_have_six_timeline_sections",
        "all_have_original_snapshot",
        "all_have_preview_edit_snapshot",
        "all_simulated_only",
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
        "default_all_compare_drawers_timeline_present",
        "owner_review_focus_timeline_present",
        "critical_priority_focus_timeline_present",
        "high_priority_focus_timeline_present",
        "monitor_only_focus_timeline_present",
        "safe_preview_focus_timeline_present",
        "cached_non_recursive",
    ]

    for key in required_true_checks:
        assert checks[key] is True, key


def test_pack_176_timelines_version_cards_and_events_are_ready():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_payload(force_refresh=True)

    timelines = payload["edit_history_timelines"]
    expected_presets = {
        "default_all_compare_drawers",
        "owner_review_focus",
        "critical_priority_focus",
        "high_priority_focus",
        "monitor_only_focus",
        "safe_preview_focus",
    }
    expected_stages = {
        "original_saved_view_preset",
        "preview_edit",
        "blocked_save_attempt",
    }
    expected_sections = {
        "timeline_identity",
        "version_cards",
        "field_change_events",
        "blocked_rollback_restore",
        "blocked_history_writes",
        "safety_flags",
    }

    assert len(timelines) == 6
    assert expected_presets.issubset({timeline["saved_view_preset_id"] for timeline in timelines})

    for timeline in timelines:
        assert timeline["edit_history_timeline_id"].startswith("saved_view_preset_edit_history_timeline_")
        assert timeline["saved_view_preset_id"] in expected_presets
        assert timeline["detail_edit_drawer_id"].startswith("saved_view_preset_detail_edit_drawer_")
        assert timeline["label"]
        assert timeline["filter_lane_id"]
        assert timeline["view_priority"] in {"critical", "high", "medium", "standard", "monitor"}
        assert isinstance(timeline["is_default"], bool)

        assert timeline["timeline_status"] == "saved_view_preset_edit_history_version_preview_ready"
        assert timeline["timeline_result_type"] == "owner_note_saved_view_preset_edit_history_timeline_preview"
        assert timeline["version_card_count"] == 3
        assert timeline["field_change_event_count"] == 5
        assert timeline["timeline_section_count"] >= 6
        assert isinstance(timeline["preview_edit_snapshot"], dict)
        assert isinstance(timeline["original_snapshot"], dict)
        assert timeline["preview_edit_snapshot"]
        assert timeline["original_snapshot"]

        stage_ids = {card["version_stage"] for card in timeline["version_cards"]}
        assert expected_stages.issubset(stage_ids)

        for card in timeline["version_cards"]:
            assert card["version_card_id"].startswith("saved_view_preset_version_card_")
            assert card["saved_view_preset_id"] == timeline["saved_view_preset_id"]
            assert card["detail_edit_drawer_id"] == timeline["detail_edit_drawer_id"]
            assert card["version_stage"] in expected_stages
            assert card["version_stage_label"]
            assert card["snapshot_field_count"] >= 1
            assert card["version_status"] == "saved_view_preset_version_preview_ready"
            assert card["version_result_type"] == "owner_note_saved_view_preset_version_card_preview"
            assert card["restore_allowed_now"] is False
            assert card["rollback_allowed_now"] is False
            assert card["save_allowed_now"] is False
            assert card["persist_allowed_now"] is False
            assert card["history_write_allowed_now"] is False
            assert card["version_write_allowed_now"] is False
            assert card["saved_view_write_allowed_now"] is False
            assert card["user_preference_write_allowed_now"] is False
            assert card["real_history_written"] is False
            assert card["real_version_written"] is False
            assert card["real_version_saved"] is False
            assert card["real_rollback_executed"] is False
            assert card["real_restore_executed"] is False
            assert card["real_edit_persisted"] is False
            assert card["real_saved_view_written"] is False
            assert card["real_user_preference_written"] is False
            assert card["simulated_only"] is True
            assert card["edit_history_preview_only"] is True
            assert card["version_preview_only"] is True
            assert card["rollback_preview_only"] is True

        for event in timeline["field_change_events"]:
            assert event["field_change_event_id"].startswith("saved_view_preset_field_change_event_")
            assert event["saved_view_preset_id"] == timeline["saved_view_preset_id"]
            assert event["detail_edit_drawer_id"] == timeline["detail_edit_drawer_id"]
            assert event["editable_field_row_id"].startswith("saved_view_preset_editable_field_row_")
            assert event["field_id"] in {"label", "description", "filter_lane_id", "view_priority", "is_default"}
            assert event["field_label"]
            assert event["field_type"] in {"text", "textarea", "select", "boolean"}
            assert isinstance(event["current_value"], dict)
            assert isinstance(event["proposed_value"], dict)
            assert isinstance(event["changed"], bool)
            assert event["event_status"] == "saved_view_preset_field_change_event_preview_ready"
            assert event["event_result_type"] == "owner_note_saved_view_preset_field_change_event_preview"
            assert event["safe_preview_only"] is True
            assert event["restore_allowed_now"] is False
            assert event["rollback_allowed_now"] is False
            assert event["save_allowed_now"] is False
            assert event["persist_allowed_now"] is False
            assert event["history_write_allowed_now"] is False
            assert event["version_write_allowed_now"] is False
            assert event["saved_view_write_allowed_now"] is False
            assert event["user_preference_write_allowed_now"] is False
            assert event["real_history_written"] is False
            assert event["real_version_written"] is False
            assert event["real_version_saved"] is False
            assert event["real_rollback_executed"] is False
            assert event["real_restore_executed"] is False
            assert event["real_edit_persisted"] is False
            assert event["real_saved_view_written"] is False
            assert event["real_user_preference_written"] is False
            assert event["simulated_only"] is True
            assert event["edit_history_preview_only"] is True
            assert event["version_preview_only"] is True
            assert event["rollback_preview_only"] is True

        section_ids = {section["section_id"] for section in timeline["timeline_sections"]}
        assert expected_sections.issubset(section_ids)

        assert timeline["restore_allowed_now"] is False
        assert timeline["rollback_allowed_now"] is False
        assert timeline["save_allowed_now"] is False
        assert timeline["persist_allowed_now"] is False
        assert timeline["history_write_allowed_now"] is False
        assert timeline["version_write_allowed_now"] is False
        assert timeline["saved_view_write_allowed_now"] is False
        assert timeline["user_preference_write_allowed_now"] is False
        assert timeline["raw_evidence_reveal_allowed"] is False
        assert timeline["raw_evidence_lookup_allowed"] is False
        assert timeline["real_history_written"] is False
        assert timeline["real_version_written"] is False
        assert timeline["real_version_saved"] is False
        assert timeline["real_rollback_executed"] is False
        assert timeline["real_restore_executed"] is False
        assert timeline["real_edit_persisted"] is False


def test_pack_176_indexes_bridge_quick_action_unified_route_and_no_secrets():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_payload(force_refresh=True)

    indexes = payload["edit_history_indexes"]
    assert indexes["by_edit_history_timeline_id"]
    assert indexes["by_detail_edit_drawer_id"]
    assert indexes["by_saved_view_preset_id"]
    assert indexes["by_filter_lane_id"]
    assert indexes["by_view_priority"]
    assert indexes["by_default_state"]
    assert indexes["by_timeline_status"]
    assert indexes["version_cards_by_id"]
    assert indexes["field_change_events_by_id"]

    assert "default_all_compare_drawers" in indexes["by_saved_view_preset_id"]
    assert "owner_review_focus" in indexes["by_saved_view_preset_id"]
    assert "critical_priority_focus" in indexes["by_saved_view_preset_id"]
    assert "high_priority_focus" in indexes["by_saved_view_preset_id"]
    assert "monitor_only_focus" in indexes["by_saved_view_preset_id"]
    assert "safe_preview_focus" in indexes["by_saved_view_preset_id"]
    assert "default" in indexes["by_default_state"]
    assert "not_default" in indexes["by_default_state"]
    assert "saved_view_preset_edit_history_version_preview_ready" in indexes["by_timeline_status"]

    bridge = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 176
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-edit-history-version-preview.json"
    assert bridge["edit_history_timeline_count"] == 6
    assert bridge["source_detail_edit_drawer_count"] == 6
    assert bridge["version_card_count"] == 18
    assert bridge["field_change_event_count"] == 30
    assert bridge["timeline_section_count"] >= 36
    assert bridge["simulated_only"] is True
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

    action = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-edit-history-version-preview.json"
    assert action["status"] == "ready"

    section = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-edit-history-version-preview.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_status_bridge")
    tower_bridge = status.build_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_quick_action")
    assert hasattr(qa, "append_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_quick_action")
    actions = qa.append_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_quick_action([])
    assert any(item.get("id") == "policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_unified_section")
    assert hasattr(unified, "append_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_section")
    sections = unified.append_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_section([])
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-edit-history-version-preview.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_json" in app_text
    assert "_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-edit-history-version-preview.json" in route_text
    assert "_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_route_guard" in route_text

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
