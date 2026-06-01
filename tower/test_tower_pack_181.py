
"""
PACK 181 fast test - Owner Note Saved View Preset Detail Edit History / Version Preview.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_181_payload_ready_and_preview_only():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_payload(force_refresh=True)

    assert payload["pack_number"] == 181
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-preview.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-saved-view-filter-preset-detail-edit-preview.json"

    required_true = [
        "simulated_only",
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
        "version_detail_preview_only",
        "compare_view_preview_only",
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
    assert summary["edit_history_timeline_count"] >= 15
    assert summary["saved_view_timeline_count"] == 6
    assert summary["filter_preset_timeline_count"] >= 9
    assert summary["version_card_count"] >= 45
    assert summary["field_change_event_count"] >= 75
    assert summary["changed_field_event_count"] >= 1
    assert summary["unchanged_field_event_count"] >= 1
    assert summary["rollback_preview_count"] >= 15
    assert summary["restore_preview_count"] >= 15
    assert summary["compare_preview_count"] >= 15

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_180_ready",
        "has_detail_edit_drawers",
        "has_saved_view_timelines",
        "has_filter_preset_timelines",
        "timeline_count_matches_drawers",
        "all_timelines_ready",
        "all_timelines_have_three_versions",
        "all_timelines_have_five_events",
        "has_version_cards",
        "has_field_change_events",
        "has_changed_events",
        "has_unchanged_events",
        "all_version_cards_ready",
        "all_field_change_events_ready",
        "timeline_indexes_present",
        "version_card_indexes_present",
        "field_change_event_indexes_present",
        "changed_event_indexes_present",
        "all_simulated_only",
        "all_edit_history_preview_only",
        "all_version_preview_only",
        "all_rollback_preview_only",
        "all_restore_preview_only",
        "all_detail_edit_preview_only",
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
        "all_rollback_actions_blocked",
        "all_restore_actions_blocked",
        "all_saves_blocked",
        "all_persists_blocked",
        "all_raw_evidence_reveal_blocked",
        "all_raw_evidence_lookup_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_181_timelines_version_cards_and_events():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_payload(force_refresh=True)

    timelines = payload["edit_history_timelines"]

    assert len(timelines) >= 15

    for timeline in timelines:
        assert timeline["edit_history_timeline_id"].startswith("saved_view_preset_detail_edit_history_timeline_")
        assert timeline["detail_edit_drawer_id"]
        assert timeline["source_kind"] in {"saved_view_preset", "filter_preset"}
        assert timeline["source_id"]
        assert timeline["timeline_status"] == "saved_view_preset_detail_edit_history_timeline_preview_ready"
        assert timeline["timeline_result_type"] == "owner_note_saved_view_preset_detail_edit_history_timeline_preview"
        assert timeline["version_card_count"] == 3
        assert timeline["field_change_event_count"] == 5
        assert timeline["active_version_card_id"]
        assert timeline["original_version_card_id"]
        assert timeline["compare_version_card_id"]
        assert isinstance(timeline["rollback_preview"], dict)
        assert isinstance(timeline["restore_preview"], dict)
        assert isinstance(timeline["compare_preview"], dict)

        assert timeline["rollback_preview"]["rollback_allowed_now"] is False
        assert timeline["rollback_preview"]["real_rollback_executed"] is False
        assert timeline["restore_preview"]["restore_allowed_now"] is False
        assert timeline["restore_preview"]["real_restore_executed"] is False
        assert timeline["compare_preview"]["compare_allowed_in_preview"] is True

        assert timeline["simulated_only"] is True
        assert timeline["edit_history_preview_only"] is True
        assert timeline["version_preview_only"] is True
        assert timeline["rollback_preview_only"] is True
        assert timeline["restore_preview_only"] is True
        assert timeline["detail_edit_preview_only"] is True
        assert timeline["real_history_written"] is False
        assert timeline["real_version_written"] is False
        assert timeline["real_version_saved"] is False
        assert timeline["real_rollback_executed"] is False
        assert timeline["real_restore_executed"] is False
        assert timeline["real_edit_persisted"] is False
        assert timeline["history_write_allowed_now"] is False
        assert timeline["version_write_allowed_now"] is False
        assert timeline["version_save_allowed_now"] is False
        assert timeline["rollback_allowed_now"] is False
        assert timeline["restore_allowed_now"] is False
        assert timeline["save_allowed_now"] is False
        assert timeline["persist_allowed_now"] is False

        version_roles = {card["version_role"] for card in timeline["version_cards"]}
        assert {"original", "draft_preview", "compare_preview"}.issubset(version_roles)

        for card in timeline["version_cards"]:
            assert card["version_card_id"].startswith("saved_view_preset_detail_edit_version_card_")
            assert card["detail_edit_drawer_id"] == timeline["detail_edit_drawer_id"]
            assert card["source_kind"] == timeline["source_kind"]
            assert card["source_id"] == timeline["source_id"]
            assert card["version_number"] in {1, 2, 3}
            assert card["version_role"] in {"original", "draft_preview", "compare_preview"}
            assert card["version_status"] == "saved_view_preset_detail_edit_version_card_preview_ready"
            assert card["version_result_type"] == "owner_note_saved_view_preset_detail_edit_version_card_preview"
            assert card["compare_allowed_in_preview"] is True
            assert card["rollback_allowed_in_preview"] is True
            assert card["restore_allowed_in_preview"] is True
            assert card["safe_preview_only"] is True

            assert card["simulated_only"] is True
            assert card["edit_history_preview_only"] is True
            assert card["version_preview_only"] is True
            assert card["real_history_written"] is False
            assert card["real_version_written"] is False
            assert card["real_version_saved"] is False
            assert card["real_rollback_executed"] is False
            assert card["real_restore_executed"] is False
            assert card["real_edit_persisted"] is False

        for event in timeline["field_change_events"]:
            assert event["field_change_event_id"].startswith("saved_view_preset_detail_edit_field_change_event_")
            assert event["detail_edit_drawer_id"] == timeline["detail_edit_drawer_id"]
            assert event["source_kind"] == timeline["source_kind"]
            assert event["source_id"] == timeline["source_id"]
            assert event["editable_field_row_id"]
            assert event["field_id"]
            assert event["field_label"]
            assert isinstance(event["changed"], bool)
            assert event["change_status"] in {"changed_preview", "unchanged_preview"}
            assert event["event_status"] == "saved_view_preset_detail_edit_field_change_event_preview_ready"
            assert event["event_result_type"] == "owner_note_saved_view_preset_detail_edit_field_change_event_preview"
            assert event["safe_preview_only"] is True

            assert event["simulated_only"] is True
            assert event["edit_history_preview_only"] is True
            assert event["version_preview_only"] is True
            assert event["real_history_written"] is False
            assert event["real_version_written"] is False
            assert event["real_version_saved"] is False
            assert event["real_rollback_executed"] is False
            assert event["real_restore_executed"] is False
            assert event["real_edit_persisted"] is False


def test_pack_181_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_payload(force_refresh=True)

    indexes = payload["edit_history_version_indexes"]

    assert indexes["timelines_by_id"]
    assert indexes["timelines_by_drawer_id"]
    assert indexes["timelines_by_source_kind"]
    assert indexes["timelines_by_source_id"]
    assert indexes["version_cards_by_id"]
    assert indexes["version_cards_by_drawer_id"]
    assert indexes["field_change_events_by_id"]
    assert indexes["field_change_events_by_drawer_id"]
    assert indexes["field_change_events_by_source_kind"]
    assert indexes["changed_events_by_drawer_id"]

    assert "saved_view_preset" in indexes["timelines_by_source_kind"]
    assert "filter_preset" in indexes["timelines_by_source_kind"]
    assert "saved_view_preset" in indexes["field_change_events_by_source_kind"]
    assert "filter_preset" in indexes["field_change_events_by_source_kind"]

    bridge = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 181
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-preview.json"
    assert bridge["edit_history_timeline_count"] >= 15
    assert bridge["saved_view_timeline_count"] == 6
    assert bridge["filter_preset_timeline_count"] >= 9
    assert bridge["version_card_count"] >= 45
    assert bridge["field_change_event_count"] >= 75
    assert bridge["changed_field_event_count"] >= 1
    assert bridge["rollback_preview_count"] >= 15
    assert bridge["restore_preview_count"] >= 15
    assert bridge["compare_preview_count"] >= 15

    action = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-preview.json"
    assert action["status"] == "ready"

    section = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-preview.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_181_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_status_bridge")
    tower_bridge = status.build_pack_181_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_181_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_quick_action")
    assert hasattr(qa, "append_pack_181_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_quick_action")
    actions = qa.append_pack_181_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_quick_action([])
    assert any(item.get("id") == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_181_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_unified_section")
    assert hasattr(unified, "append_pack_181_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_section")
    sections = unified.append_pack_181_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_section([])
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-preview.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_json" in app_text
    assert "_pack_181_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-preview.json" in route_text
    assert "_pack_181_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_route_guard" in route_text

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
