
from __future__ import annotations
import importlib
from pathlib import Path

def test_pack_178_payload_ready():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation")
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload(force_refresh=True)

    assert payload["pack_number"] == 178
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-filter-navigation.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-detail-compare-view.json"

    for key in [
        "simulated_only",
        "navigation_preview_only",
        "filter_navigation_preview_only",
        "version_detail_preview_only",
        "compare_view_preview_only",
        "saved_navigation_preview_only",
        "saved_filter_preset_preview_only",
        "cached_non_recursive",
    ]:
        assert payload[key] is True

    for key in [
        "real_navigation_state_persisted",
        "real_filter_preference_saved",
        "real_drawer_selection_saved",
        "real_history_written",
        "real_version_written",
        "real_version_saved",
        "real_rollback_executed",
        "real_restore_executed",
        "real_saved_view_written",
        "real_user_preference_written",
    ]:
        assert payload[key] is False

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["navigation_item_count"] == 6
    assert summary["version_detail_drawer_count"] == 6
    assert summary["filter_lane_count"] >= 9
    assert summary["quick_filter_chip_count"] == 6
    assert summary["group_count"] >= 1
    assert summary["comparison_row_count"] == 30
    assert summary["default_filter_lane_id"] == "all_compare_drawers"
    assert summary["default_selected_drawer_id"]
    assert summary["default_selected_saved_view_preset_id"]

    checks = payload["readiness_checks"]
    for key in [
        "pack_177_ready",
        "has_drawers",
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
        "all_expected_filter_lanes_present",
        "all_quick_filters_present",
        "has_previous_next_pointers",
    ]:
        assert checks[key] is True, key

def test_pack_178_navigation_filters_indexes():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation")
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload(force_refresh=True)

    nav = payload["navigation_preview"]
    items = nav["navigation_items"]
    assert nav["navigation_status"] == "saved_view_preset_version_compare_drawer_navigation_preview_ready"
    assert len(items) == 6
    assert items[0]["has_previous"] is False
    assert items[0]["has_next"] is True
    assert items[-1]["has_next"] is False
    assert items[-1]["has_previous"] is True

    for item in items:
        assert item["navigation_item_id"].startswith("saved_view_preset_version_compare_nav_item_")
        assert item["version_detail_drawer_id"].startswith("saved_view_preset_version_detail_compare_drawer_")
        assert item["comparison_row_count"] == 5
        assert item["version_card_count"] == 3
        assert item["field_change_event_count"] == 5
        assert item["navigation_status"] == "saved_view_preset_version_compare_navigation_item_preview_ready"
        assert item["real_navigation_state_persisted"] is False
        assert item["real_filter_preference_saved"] is False
        assert item["real_drawer_selection_saved"] is False

    selected = nav["selected_drawer_preview"]
    assert selected["selection_status"] == "saved_view_preset_version_compare_selected_drawer_preview_ready"
    assert selected["selected_version_detail_drawer_id"]

    lanes = payload["filter_lanes_preview"]
    chips = payload["quick_filter_chips_preview"]
    grouped = payload["grouped_navigation_preview"]
    indexes = payload["navigation_indexes"]

    expected_lanes = {
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
    assert lanes["filter_status"] == "saved_view_preset_version_compare_filter_lanes_preview_ready"
    assert expected_lanes.issubset(set(lanes["filter_lane_index"].keys()))
    assert lanes["filter_lane_index"]["all_compare_drawers"]["matched_drawer_count"] == 6
    assert lanes["filter_lane_index"]["safe_preview_only"]["matched_drawer_count"] == 6

    assert chips["quick_filter_status"] == "saved_view_preset_version_compare_quick_filter_chips_preview_ready"
    assert chips["quick_filter_chip_count"] == 6

    assert grouped["grouped_navigation_status"] == "saved_view_preset_version_compare_grouped_navigation_preview_ready"
    assert grouped["group_count"] >= 1

    assert indexes["by_navigation_item_id"]
    assert indexes["by_version_detail_drawer_id"]
    assert indexes["by_saved_view_preset_id"]
    assert "all_compare_drawers" in indexes["by_filter_lane_id"]
    assert "default" in indexes["by_default_state"]
    assert "not_default" in indexes["by_default_state"]

def test_pack_178_integrations_and_no_secrets():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation")
    bridge = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_status_bridge(force_refresh=True)
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["navigation_item_count"] == 6

    action = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation"
    assert action["status"] == "ready"

    section = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation"
    assert section["status"] == "ready"

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_178_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_status_bridge")
    assert status.build_pack_178_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_status_bridge()["status"] == "ready"

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    actions = qa.append_pack_178_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_quick_action([])
    assert any(x.get("id") == "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation" for x in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    sections = unified.append_pack_178_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_section([])
    assert any(x.get("section_id") == "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation" for x in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-filter-navigation.json" in app_text
    assert "_pack_178_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_route_guard" in app_text
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-filter-navigation.json" in route_text

    payload_text = str(mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload(force_refresh=True)).lower()
    for frag in ["sk_live_","sk_test_","github_pat_","ghp_","xoxb-","aws_secret_access_key","private_key-----","broker_token_value","api_secret_value"]:
        assert frag not in payload_text
