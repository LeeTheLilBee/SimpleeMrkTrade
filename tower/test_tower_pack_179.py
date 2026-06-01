
"""
PACK 179 fast test - Owner Note Saved View Preset Version Compare Navigation Saved View / Filter Preset Preview.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_179_payload_ready_and_preview_only():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload(force_refresh=True)

    assert payload["pack_number"] == 179
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-navigation-saved-view-filter-preset.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-filter-navigation.json"

    required_true = [
        "simulated_only",
        "saved_view_preview_only",
        "filter_preset_preview_only",
        "navigation_preview_only",
        "filter_navigation_preview_only",
        "version_detail_preview_only",
        "compare_view_preview_only",
        "edit_history_preview_only",
        "version_preview_only",
        "rollback_preview_only",
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
    assert summary["saved_view_preset_count"] == 6
    assert summary["filter_preset_count"] >= 9
    assert summary["source_navigation_item_count"] == 6
    assert summary["source_filter_lane_count"] >= 9
    assert summary["comparison_row_count"] >= 30
    assert summary["default_saved_view_preset_id"] == "default_all_compare_navigation"
    assert summary["default_selected_version_detail_drawer_id"]

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_178_ready",
        "has_navigation_items",
        "has_filter_lanes",
        "has_saved_view_presets",
        "has_filter_presets",
        "saved_view_preset_count_is_six",
        "filter_preset_count_is_nine",
        "selected_saved_view_preview_ready",
        "default_saved_view_present",
        "all_expected_saved_view_presets_present",
        "all_expected_filter_presets_present",
        "all_saved_view_presets_ready",
        "all_filter_presets_ready",
        "all_saved_view_presets_simulated_only",
        "all_filter_presets_simulated_only",
        "all_saved_view_preview_only",
        "all_filter_preset_preview_only",
        "all_navigation_preview_only",
        "all_filter_navigation_preview_only",
        "all_version_detail_preview_only",
        "all_compare_view_preview_only",
        "no_real_saved_view_written",
        "no_real_user_preference_written",
        "no_real_filter_preference_saved",
        "no_real_navigation_state_persisted",
        "no_real_drawer_selection_saved",
        "no_real_history_written",
        "no_real_version_written",
        "no_real_version_saved",
        "no_real_rollback_executed",
        "no_real_restore_executed",
        "no_real_edit_persisted",
        "all_saved_view_writes_blocked",
        "all_user_preference_writes_blocked",
        "all_filter_preference_saves_blocked",
        "all_navigation_persistence_blocked",
        "all_drawer_selection_saves_blocked",
        "all_restore_actions_blocked",
        "all_rollback_actions_blocked",
        "all_raw_evidence_reveal_blocked",
        "all_raw_evidence_lookup_blocked",
        "saved_view_indexes_present",
        "filter_preset_indexes_present",
        "default_all_compare_navigation_indexed",
        "all_compare_drawers_filter_preset_indexed",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_179_saved_view_presets_filter_presets_and_selected_preview():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload(force_refresh=True)

    saved_views = payload["saved_view_presets"]
    filter_presets = payload["filter_presets"]
    selected = payload["selected_saved_view_preview"]

    expected_saved_view_ids = {
        "default_all_compare_navigation",
        "default_saved_view_focus",
        "critical_priority_focus",
        "high_priority_focus",
        "changed_fields_focus",
        "safe_preview_focus",
    }

    expected_filter_lane_ids = {
        "all_compare_drawers",
        "default_saved_view",
        "not_default_saved_views",
        "critical_priority",
        "high_priority",
        "standard_priority",
        "monitor_priority",
        "changed_fields_present",
        "safe_preview_only",
    }

    assert len(saved_views) == 6
    assert expected_saved_view_ids.issubset({item["saved_view_preset_id"] for item in saved_views})

    for preset in saved_views:
        assert preset["saved_view_preset_preview_id"].startswith("saved_view_preset_version_compare_saved_view_preset_")
        assert preset["saved_view_preset_id"] in expected_saved_view_ids
        assert preset["filter_lane_id"]
        assert preset["linked_filter_preset_id"]
        assert preset["view_priority"] in {"critical", "high", "medium", "standard", "monitor"}
        assert isinstance(preset["is_default"], bool)
        assert preset["matched_navigation_item_count"] >= 0
        assert isinstance(preset["matched_navigation_item_ids"], list)
        assert isinstance(preset["matched_version_detail_drawer_ids"], list)
        assert preset["default_selected_navigation_item_id"]
        assert preset["default_selected_version_detail_drawer_id"]
        assert preset["saved_view_preset_status"] == "saved_view_preset_version_compare_saved_view_preset_preview_ready"
        assert preset["saved_view_preset_result_type"] == "owner_note_saved_view_preset_version_compare_saved_view_preset_preview"

        assert preset["simulated_only"] is True
        assert preset["saved_view_preview_only"] is True
        assert preset["filter_preset_preview_only"] is True
        assert preset["navigation_preview_only"] is True
        assert preset["filter_navigation_preview_only"] is True
        assert preset["real_saved_view_written"] is False
        assert preset["real_user_preference_written"] is False
        assert preset["real_filter_preference_saved"] is False
        assert preset["real_navigation_state_persisted"] is False
        assert preset["real_drawer_selection_saved"] is False
        assert preset["saved_view_write_allowed_now"] is False
        assert preset["user_preference_write_allowed_now"] is False
        assert preset["filter_preference_save_allowed_now"] is False
        assert preset["navigation_persistence_allowed_now"] is False

    assert len(filter_presets) >= 9
    assert expected_filter_lane_ids.issubset({item["filter_lane_id"] for item in filter_presets})

    for preset in filter_presets:
        assert preset["filter_preset_id"].startswith("saved_view_preset_version_compare_filter_preset_")
        assert preset["filter_lane_id"] in expected_filter_lane_ids
        assert preset["label"]
        assert preset["filter_type"] in {"all", "default_state", "priority", "change_state", "safety"}
        assert preset["filter_preset_status"] == "saved_view_preset_version_compare_filter_preset_preview_ready"
        assert preset["filter_preset_result_type"] == "owner_note_saved_view_preset_version_compare_filter_preset_preview"
        assert preset["matched_drawer_count"] >= 0
        assert isinstance(preset["matched_version_detail_drawer_ids"], list)
        assert isinstance(preset["matched_saved_view_preset_ids"], list)

        assert preset["simulated_only"] is True
        assert preset["filter_preset_preview_only"] is True
        assert preset["navigation_preview_only"] is True
        assert preset["filter_navigation_preview_only"] is True
        assert preset["real_saved_view_written"] is False
        assert preset["real_user_preference_written"] is False
        assert preset["real_filter_preference_saved"] is False
        assert preset["real_navigation_state_persisted"] is False
        assert preset["real_drawer_selection_saved"] is False
        assert preset["saved_view_write_allowed_now"] is False
        assert preset["user_preference_write_allowed_now"] is False
        assert preset["filter_preference_save_allowed_now"] is False
        assert preset["navigation_persistence_allowed_now"] is False

    assert selected["selection_status"] == "saved_view_preset_version_compare_selected_saved_view_preview_ready"
    assert selected["selection_result_type"] == "owner_note_saved_view_preset_version_compare_selected_saved_view_preview"
    assert selected["selected_saved_view_preset_id"] == "default_all_compare_navigation"
    assert selected["selected_saved_view_preset_preview_id"]
    assert selected["selected_linked_filter_preset_id"]
    assert selected["selected_default_navigation_item_id"]
    assert selected["selected_default_version_detail_drawer_id"]

    assert selected["simulated_only"] is True
    assert selected["saved_view_preview_only"] is True
    assert selected["filter_preset_preview_only"] is True
    assert selected["real_saved_view_written"] is False
    assert selected["real_user_preference_written"] is False
    assert selected["real_filter_preference_saved"] is False
    assert selected["real_navigation_state_persisted"] is False
    assert selected["real_drawer_selection_saved"] is False


def test_pack_179_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload(force_refresh=True)

    indexes = payload["saved_view_filter_preset_indexes"]

    assert indexes["saved_views_by_preview_id"]
    assert indexes["saved_views_by_id"]
    assert indexes["saved_views_by_filter_lane_id"]
    assert indexes["saved_views_by_priority"]
    assert indexes["saved_views_by_default_state"]
    assert indexes["filter_presets_by_id"]
    assert indexes["filter_presets_by_lane_id"]
    assert indexes["filter_presets_by_filter_type"]

    assert "default_all_compare_navigation" in indexes["saved_views_by_id"]
    assert "safe_preview_focus" in indexes["saved_views_by_id"]
    assert "all_compare_drawers" in indexes["filter_presets_by_lane_id"]
    assert "safe_preview_only" in indexes["filter_presets_by_lane_id"]
    assert "default" in indexes["saved_views_by_default_state"]
    assert "not_default" in indexes["saved_views_by_default_state"]

    bridge = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 179
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-navigation-saved-view-filter-preset.json"
    assert bridge["saved_view_preset_count"] == 6
    assert bridge["filter_preset_count"] >= 9
    assert bridge["source_navigation_item_count"] == 6
    assert bridge["source_filter_lane_count"] >= 9
    assert bridge["comparison_row_count"] >= 30

    action = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-navigation-saved-view-filter-preset.json"
    assert action["status"] == "ready"

    section = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-navigation-saved-view-filter-preset.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_179_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_status_bridge")
    tower_bridge = status.build_pack_179_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_179_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_quick_action")
    assert hasattr(qa, "append_pack_179_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_quick_action")
    actions = qa.append_pack_179_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_quick_action([])
    assert any(item.get("id") == "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_179_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_unified_section")
    assert hasattr(unified, "append_pack_179_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_section")
    sections = unified.append_pack_179_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_section([])
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-navigation-saved-view-filter-preset.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_json" in app_text
    assert "_pack_179_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-navigation-saved-view-filter-preset.json" in route_text
    assert "_pack_179_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_route_guard" in route_text

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
