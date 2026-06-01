
"""
PACK 183 fast test - Owner Note Saved View Preset Detail Edit History Version Compare Filter / Drawer Navigation Preview.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_183_payload_ready_and_preview_only():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload(force_refresh=True)

    assert payload["pack_number"] == 183
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-filter-navigation.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-detail-compare-view.json"

    required_true = [
        "simulated_only",
        "navigation_preview_only",
        "filter_navigation_preview_only",
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
    assert summary["navigation_item_count"] >= 15
    assert summary["version_detail_drawer_count"] >= 15
    assert summary["filter_lane_count"] == 9
    assert summary["quick_filter_chip_count"] == 6
    assert summary["group_count"] >= 2
    assert summary["comparison_row_count"] >= 75
    assert summary["changed_compare_row_count"] >= 1
    assert summary["unchanged_compare_row_count"] >= 1
    assert summary["default_filter_lane_id"] == "all_compare_drawers"
    assert summary["default_selected_version_detail_drawer_id"]

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_182_ready",
        "has_version_detail_drawers",
        "has_navigation_items",
        "navigation_count_matches_drawers",
        "has_filter_lanes",
        "has_quick_filter_chips",
        "has_grouped_navigation",
        "has_selected_drawer_preview",
        "all_navigation_items_ready",
        "filter_lanes_ready",
        "quick_filter_chips_ready",
        "grouped_navigation_ready",
        "selected_drawer_preview_ready",
        "all_expected_filter_lanes_present",
        "all_quick_filters_present",
        "has_previous_next_pointers",
        "navigation_indexes_present",
        "filter_lane_indexes_present",
        "all_simulated_only",
        "all_navigation_preview_only",
        "all_filter_navigation_preview_only",
        "all_version_detail_preview_only",
        "all_compare_view_preview_only",
        "no_real_navigation_state_persisted",
        "no_real_filter_preference_saved",
        "no_real_drawer_selection_saved",
        "no_real_history_written",
        "no_real_version_written",
        "no_real_version_saved",
        "no_real_rollback_executed",
        "no_real_restore_executed",
        "no_real_edit_persisted",
        "all_navigation_persistence_blocked",
        "all_filter_preference_saves_blocked",
        "all_drawer_selection_saves_blocked",
        "all_saves_blocked",
        "all_persists_blocked",
        "all_raw_evidence_reveal_blocked",
        "all_raw_evidence_lookup_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_183_navigation_filters_groups_and_selected_drawer():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload(force_refresh=True)

    navigation_preview = payload["navigation_preview"]
    nav_items = navigation_preview["navigation_items"]
    filter_lanes_preview = payload["filter_lanes_preview"]
    lanes = filter_lanes_preview["filter_lanes"]
    quick_filter_payload = payload["quick_filter_chips_preview"]
    chips = quick_filter_payload["quick_filter_chips"]
    grouped = payload["grouped_navigation_preview"]
    selected = navigation_preview["selected_drawer_preview"]

    assert navigation_preview["navigation_status"] == "saved_view_preset_version_compare_drawer_navigation_preview_ready"
    assert navigation_preview["navigation_item_count"] == len(nav_items)
    assert len(nav_items) >= 15
    assert navigation_preview["default_selected_version_detail_drawer_id"] == selected["selected_version_detail_drawer_id"]

    for idx, item in enumerate(nav_items, start=1):
        assert item["navigation_item_id"].startswith("saved_view_preset_version_compare_nav_item_")
        assert item["position"] == idx
        assert item["total_count"] == len(nav_items)
        assert item["version_detail_drawer_id"]
        assert item["edit_history_timeline_id"]
        assert item["detail_edit_drawer_id"]
        assert item["source_kind"] in {"saved_view_preset", "filter_preset"}
        assert item["source_id"]
        assert item["label"]
        assert item["comparison_row_count"] == 5
        assert item["changed_compare_row_count"] >= 0
        assert item["unchanged_compare_row_count"] >= 0
        assert item["version_card_count"] == 3
        assert item["changed_compare_row_count"] + item["unchanged_compare_row_count"] == 5
        assert item["navigation_status"] == "saved_view_preset_version_compare_navigation_item_preview_ready"
        assert item["navigation_result_type"] == "owner_note_saved_view_preset_version_compare_navigation_item_preview"
        assert item["open_allowed_in_preview"] is True
        assert item["selection_allowed_in_preview"] is True

        if idx == 1:
            assert item["has_previous"] is False
            assert item["previous_version_detail_drawer_id"] is None
            assert item["has_next"] is True
            assert item["next_version_detail_drawer_id"]
        elif idx == len(nav_items):
            assert item["has_previous"] is True
            assert item["previous_version_detail_drawer_id"]
            assert item["has_next"] is False
            assert item["next_version_detail_drawer_id"] is None
        else:
            assert item["has_previous"] is True
            assert item["previous_version_detail_drawer_id"]
            assert item["has_next"] is True
            assert item["next_version_detail_drawer_id"]

        assert item["simulated_only"] is True
        assert item["navigation_preview_only"] is True
        assert item["filter_navigation_preview_only"] is True
        assert item["version_detail_preview_only"] is True
        assert item["compare_view_preview_only"] is True
        assert item["real_navigation_state_persisted"] is False
        assert item["real_filter_preference_saved"] is False
        assert item["real_drawer_selection_saved"] is False
        assert item["real_history_written"] is False
        assert item["real_version_written"] is False
        assert item["real_version_saved"] is False
        assert item["real_rollback_executed"] is False
        assert item["real_restore_executed"] is False
        assert item["real_edit_persisted"] is False

    expected_lane_ids = {
        "all_compare_drawers",
        "saved_view_preset_drawers",
        "filter_preset_drawers",
        "changed_fields_present",
        "unchanged_fields_present",
        "rollback_blocked",
        "restore_blocked",
        "save_blocked",
        "safe_preview_only",
    }

    assert filter_lanes_preview["filter_status"] == "saved_view_preset_version_compare_filter_lanes_preview_ready"
    assert filter_lanes_preview["filter_lane_count"] == 9
    assert set(filter_lanes_preview["filter_lane_ids"]) == expected_lane_ids
    assert filter_lanes_preview["default_filter_lane_id"] == "all_compare_drawers"

    for lane in lanes:
        assert lane["filter_lane_preview_id"].startswith("saved_view_preset_version_compare_filter_lane_")
        assert lane["filter_lane_id"] in expected_lane_ids
        assert lane["label"]
        assert lane["filter_type"] in {"all", "source_kind", "change_state", "blocked_action", "safety"}
        assert lane["matched_drawer_count"] >= 0
        assert isinstance(lane["matched_version_detail_drawer_ids"], list)
        assert isinstance(lane["matched_source_ids"], list)
        assert lane["lane_status"] == "saved_view_preset_version_compare_filter_lane_preview_ready"
        assert lane["lane_result_type"] == "owner_note_saved_view_preset_version_compare_filter_lane_preview"
        assert lane["filter_allowed_in_preview"] is True
        assert lane["selection_allowed_in_preview"] is True
        assert lane["simulated_only"] is True
        assert lane["real_filter_preference_saved"] is False
        assert lane["real_navigation_state_persisted"] is False
        assert lane["real_drawer_selection_saved"] is False

    lane_index = filter_lanes_preview["filter_lane_index"]
    assert lane_index["all_compare_drawers"]["matched_drawer_count"] == len(nav_items)
    assert lane_index["saved_view_preset_drawers"]["matched_drawer_count"] == 6
    assert lane_index["filter_preset_drawers"]["matched_drawer_count"] >= 9
    assert lane_index["rollback_blocked"]["matched_drawer_count"] == len(nav_items)
    assert lane_index["restore_blocked"]["matched_drawer_count"] == len(nav_items)
    assert lane_index["save_blocked"]["matched_drawer_count"] == len(nav_items)
    assert lane_index["safe_preview_only"]["matched_drawer_count"] == len(nav_items)

    assert quick_filter_payload["quick_filter_status"] == "saved_view_preset_version_compare_quick_filter_chips_preview_ready"
    assert quick_filter_payload["quick_filter_chip_count"] == 6
    assert quick_filter_payload["quick_filter_ids"] == [
        "all_compare_drawers",
        "saved_view_preset_drawers",
        "filter_preset_drawers",
        "changed_fields_present",
        "rollback_blocked",
        "safe_preview_only",
    ]

    for chip in chips:
        assert chip["quick_filter_chip_id"].startswith("saved_view_preset_version_compare_quick_filter_chip_")
        assert chip["filter_lane_id"] in quick_filter_payload["quick_filter_ids"]
        assert chip["label"]
        assert chip["matched_drawer_count"] >= 0
        assert chip["chip_status"] == "saved_view_preset_version_compare_quick_filter_chip_preview_ready"
        assert chip["chip_result_type"] == "owner_note_saved_view_preset_version_compare_quick_filter_chip_preview"
        assert chip["simulated_only"] is True

    assert grouped["grouped_navigation_status"] == "saved_view_preset_version_compare_grouped_navigation_preview_ready"
    assert grouped["group_count"] >= 2
    assert "saved_view_preset" in grouped["groups"]
    assert "filter_preset" in grouped["groups"]
    assert grouped["groups"]["saved_view_preset"]["navigation_item_count"] == 6
    assert grouped["groups"]["filter_preset"]["navigation_item_count"] >= 9

    assert selected["selection_status"] == "saved_view_preset_version_compare_selected_drawer_preview_ready"
    assert selected["selected_navigation_item_id"]
    assert selected["selected_version_detail_drawer_id"]
    assert selected["selected_edit_history_timeline_id"]
    assert selected["selected_source_kind"] in {"saved_view_preset", "filter_preset"}
    assert selected["selected_source_id"]
    assert selected["selected_comparison_row_count"] == 5
    assert selected["selected_drawer_status"] == "saved_view_preset_version_detail_compare_drawer_preview_ready"
    assert selected["real_navigation_state_persisted"] is False
    assert selected["real_drawer_selection_saved"] is False
    assert selected["real_filter_preference_saved"] is False


def test_pack_183_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload(force_refresh=True)

    indexes = payload["navigation_indexes"]

    assert indexes["navigation_items_by_id"]
    assert indexes["navigation_items_by_version_detail_drawer_id"]
    assert indexes["navigation_items_by_timeline_id"]
    assert indexes["navigation_items_by_detail_edit_drawer_id"]
    assert indexes["navigation_items_by_source_kind"]
    assert indexes["navigation_items_by_source_id"]
    assert indexes["filter_lanes_by_id"]
    assert indexes["navigation_items_by_filter_lane_id"]

    assert "saved_view_preset" in indexes["navigation_items_by_source_kind"]
    assert "filter_preset" in indexes["navigation_items_by_source_kind"]
    assert "all_compare_drawers" in indexes["filter_lanes_by_id"]
    assert "safe_preview_only" in indexes["filter_lanes_by_id"]
    assert len(indexes["navigation_items_by_filter_lane_id"]["all_compare_drawers"]) >= 15

    bridge = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 183
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-filter-navigation.json"
    assert bridge["navigation_item_count"] >= 15
    assert bridge["version_detail_drawer_count"] >= 15
    assert bridge["filter_lane_count"] == 9
    assert bridge["quick_filter_chip_count"] == 6
    assert bridge["group_count"] >= 2
    assert bridge["comparison_row_count"] >= 75
    assert bridge["changed_compare_row_count"] >= 1
    assert bridge["default_filter_lane_id"] == "all_compare_drawers"
    assert bridge["default_selected_version_detail_drawer_id"]

    action = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-filter-navigation.json"
    assert action["status"] == "ready"

    section = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-filter-navigation.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_183_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_status_bridge")
    tower_bridge = status.build_pack_183_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_183_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_quick_action")
    assert hasattr(qa, "append_pack_183_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_quick_action")
    actions = qa.append_pack_183_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_quick_action([])
    assert any(item.get("id") == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_183_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_unified_section")
    assert hasattr(unified, "append_pack_183_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_section")
    sections = unified.append_pack_183_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_section([])
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-filter-navigation.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_json" in app_text
    assert "_pack_183_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-filter-navigation.json" in route_text
    assert "_pack_183_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_route_guard" in route_text

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
