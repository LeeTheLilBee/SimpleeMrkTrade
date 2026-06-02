
"""
PACK 194 fast test - Owner Note Version Compare Navigation Compare
Filter Navigation / Drawer Selection Preview.

Uses short safe module:
    tower.owner_note_vc_nav_filter_nav_v194
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_194_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.owner_note_vc_nav_filter_nav_v194")
    payload = mod.build_owner_note_vc_nav_filter_nav_v194_payload(force_refresh=True)

    assert payload["pack_number"] == 194
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/owner-note-vc-nav-filter-nav-v194.json"
    assert payload["source_endpoint"] == "/tower/owner-note-vc-nav-compare-filter-v193.json"

    required_true = [
        "simulated_only",
        "navigation_preview_only",
        "filter_navigation_preview_only",
        "drawer_selection_preview_only",
        "filter_preview_only",
        "search_facet_preview_only",
        "version_detail_preview_only",
        "compare_view_preview_only",
        "cached_non_recursive",
    ]

    for key in required_true:
        assert payload[key] is True, key

    required_false = [
        "real_filter_preference_saved",
        "real_navigation_state_persisted",
        "real_drawer_selection_saved",
        "real_saved_view_written",
        "real_user_preference_written",
        "real_history_written",
        "real_version_written",
        "real_version_saved",
        "real_rollback_executed",
        "real_restore_executed",
        "real_edit_persisted",
        "real_raw_evidence_revealed",
    ]

    for key in required_false:
        assert payload[key] is False, key

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["navigation_item_count"] == 9
    assert summary["drawer_selection_preview_count"] == 9
    assert summary["navigation_group_count"] == 9
    assert summary["search_navigation_facet_count"] == 5
    assert summary["search_navigation_chip_count"] == 9
    assert summary["total_navigation_drawer_reference_count"] >= 15
    assert summary["total_navigation_compare_row_reference_count"] >= 75
    assert summary["default_filter_lane_id"] == "all_compare_drawers"
    assert summary["selected_navigation_item_id"]
    assert summary["selected_version_detail_drawer_id"]
    assert summary["selected_compare_row_count"] >= 75

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_193_ready",
        "has_filter_lanes",
        "has_navigation_items",
        "has_drawer_selection_previews",
        "has_navigation_groups",
        "has_search_navigation_summary",
        "default_selected_navigation_ready",
        "default_all_compare_navigation_present",
        "all_navigation_items_ready",
        "all_drawer_selections_ready",
        "all_navigation_groups_ready",
        "navigation_indexes_present",
        "drawer_selection_indexes_present",
        "navigation_group_indexes_present",
        "has_drawer_references",
        "has_compare_row_references",
        "selected_drawer_present",
        "selected_rows_present",
        "all_simulated_only",
        "all_navigation_preview_only",
        "all_filter_navigation_preview_only",
        "all_drawer_selection_preview_only",
        "all_filter_preview_only",
        "all_search_facet_preview_only",
        "no_real_filter_preference_saved",
        "no_real_navigation_state_persisted",
        "no_real_drawer_selection_saved",
        "no_real_raw_evidence_revealed",
        "all_filter_preference_saves_blocked",
        "all_navigation_persistence_blocked",
        "all_drawer_selection_saves_blocked",
        "all_raw_evidence_reveal_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_194_navigation_items_drawer_selections_and_groups():
    mod = importlib.import_module("tower.owner_note_vc_nav_filter_nav_v194")
    payload = mod.build_owner_note_vc_nav_filter_nav_v194_payload(force_refresh=True)

    nav_items = payload["navigation_items"]
    selections = payload["drawer_selection_previews"]
    groups = payload["navigation_groups"]

    assert len(nav_items) == 9
    assert len(selections) == 9
    assert len(groups) == 9

    expected_lane_ids = {
        "all_compare_drawers",
        "saved_view_preset_drawers",
        "filter_preset_drawers",
        "changed_compare_rows",
        "unchanged_compare_rows",
        "raw_reveal_blocked",
        "rollback_blocked",
        "restore_blocked",
        "safe_preview_only",
    }

    nav_lane_ids = {item["filter_lane_id"] for item in nav_items}
    selection_lane_ids = {item["filter_lane_id"] for item in selections}
    group_lane_ids = {item["filter_lane_id"] for item in groups}

    assert nav_lane_ids == expected_lane_ids
    assert selection_lane_ids == expected_lane_ids
    assert group_lane_ids == expected_lane_ids

    for item in nav_items:
        assert item["navigation_item_id"].startswith("version_compare_navigation_filter_nav_item_")
        assert item["filter_lane_id"] in expected_lane_ids
        assert item["filter_lane_preview_id"]
        assert item["label"]
        assert item["description"]
        assert item["filter_type"] in {"all", "source_kind", "change_state", "safety", "blocked_action"}
        assert item["sequence"] >= 1
        assert item["matched_version_detail_drawer_count"] >= 0
        assert isinstance(item["matched_version_detail_drawer_ids"], list)
        assert item["matched_compare_row_count"] >= 0
        assert isinstance(item["matched_compare_row_ids"], list)
        assert item["navigation_status"] == "version_compare_navigation_filter_navigation_item_preview_ready"
        assert item["navigation_result_type"] == "owner_note_version_compare_navigation_filter_navigation_item_preview"
        assert item["open_allowed_in_preview"] is True
        assert item["selection_allowed_in_preview"] is True
        assert item["safe_preview_only"] is True

        assert item["simulated_only"] is True
        assert item["navigation_preview_only"] is True
        assert item["filter_navigation_preview_only"] is True
        assert item["drawer_selection_preview_only"] is True
        assert item["filter_preview_only"] is True
        assert item["search_facet_preview_only"] is True
        assert item["real_filter_preference_saved"] is False
        assert item["real_navigation_state_persisted"] is False
        assert item["real_drawer_selection_saved"] is False
        assert item["real_raw_evidence_revealed"] is False
        assert item["filter_preference_save_allowed_now"] is False
        assert item["navigation_persistence_allowed_now"] is False
        assert item["drawer_selection_save_allowed_now"] is False
        assert item["raw_evidence_reveal_allowed"] is False
        assert item["raw_evidence_lookup_allowed"] is False

    all_item = next(item for item in nav_items if item["filter_lane_id"] == "all_compare_drawers")
    saved_view_item = next(item for item in nav_items if item["filter_lane_id"] == "saved_view_preset_drawers")
    filter_preset_item = next(item for item in nav_items if item["filter_lane_id"] == "filter_preset_drawers")
    safe_item = next(item for item in nav_items if item["filter_lane_id"] == "safe_preview_only")

    assert all_item["matched_version_detail_drawer_count"] >= 15
    assert all_item["matched_compare_row_count"] >= 75
    assert all_item["default_version_detail_drawer_id"]
    assert saved_view_item["matched_version_detail_drawer_count"] == 6
    assert filter_preset_item["matched_version_detail_drawer_count"] >= 9
    assert safe_item["matched_version_detail_drawer_count"] >= 15

    selection_by_lane = {item["filter_lane_id"]: item for item in selections}
    group_by_lane = {item["filter_lane_id"]: item for item in groups}
    nav_by_lane = {item["filter_lane_id"]: item for item in nav_items}

    for lane_id in expected_lane_ids:
        selection = selection_by_lane[lane_id]
        nav = nav_by_lane[lane_id]
        group = group_by_lane[lane_id]

        assert selection["drawer_selection_preview_id"].startswith("version_compare_navigation_drawer_selection_")
        assert selection["navigation_item_id"] == nav["navigation_item_id"]
        assert selection["filter_lane_id"] == lane_id
        assert selection["available_version_detail_drawer_count"] == len(selection["available_version_detail_drawer_ids"])
        assert selection["visible_compare_row_count"] == len(selection["visible_compare_row_ids"])
        assert selection["selection_status"] == "version_compare_navigation_drawer_selection_preview_ready"
        assert selection["selection_result_type"] == "owner_note_version_compare_navigation_drawer_selection_preview"
        assert selection["open_allowed_in_preview"] is True
        assert selection["selection_allowed_in_preview"] is True
        assert selection["safe_preview_only"] is True
        assert selection["real_filter_preference_saved"] is False
        assert selection["real_navigation_state_persisted"] is False
        assert selection["real_drawer_selection_saved"] is False
        assert selection["real_raw_evidence_revealed"] is False

        assert group["navigation_group_id"].startswith("version_compare_navigation_filter_group_")
        assert group["navigation_item_id"] == nav["navigation_item_id"]
        assert group["drawer_selection_preview_id"] == selection["drawer_selection_preview_id"]
        assert group["filter_lane_id"] == lane_id
        assert group["label"] == nav["label"]
        assert group["drawer_count"] == nav["matched_version_detail_drawer_count"]
        assert group["row_count"] == nav["matched_compare_row_count"]
        assert group["selected_version_detail_drawer_id"] == selection["selected_version_detail_drawer_id"]
        assert group["group_status"] == "version_compare_navigation_filter_group_preview_ready"
        assert group["group_result_type"] == "owner_note_version_compare_navigation_filter_group_preview"
        assert group["safe_preview_only"] is True
        assert group["real_filter_preference_saved"] is False
        assert group["real_navigation_state_persisted"] is False
        assert group["real_drawer_selection_saved"] is False

    assert selection_by_lane["all_compare_drawers"]["selected_version_detail_drawer_id"]
    assert selection_by_lane["all_compare_drawers"]["available_version_detail_drawer_count"] >= 15
    assert selection_by_lane["all_compare_drawers"]["visible_compare_row_count"] >= 75


def test_pack_194_search_summary_selected_preview_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.owner_note_vc_nav_filter_nav_v194")
    payload = mod.build_owner_note_vc_nav_filter_nav_v194_payload(force_refresh=True)

    search_summary = payload["search_navigation_summary"]
    assert search_summary["search_navigation_summary_id"].startswith("version_compare_navigation_search_summary_")
    assert search_summary["search_facet_count"] == 5
    assert isinstance(search_summary["search_facet_ids"], list)
    assert len(search_summary["search_facet_ids"]) == 5
    assert search_summary["search_facet_value_count"] >= 1
    assert search_summary["quick_filter_chip_count"] == 9
    assert isinstance(search_summary["quick_filter_chip_ids"], list)
    assert len(search_summary["quick_filter_chip_ids"]) == 9
    assert search_summary["search_query_preview"] == ""
    assert search_summary["summary_status"] == "version_compare_navigation_search_summary_preview_ready"
    assert search_summary["summary_result_type"] == "owner_note_version_compare_navigation_search_summary_preview"
    assert search_summary["search_allowed_in_preview"] is True
    assert search_summary["safe_preview_only"] is True
    assert search_summary["real_filter_preference_saved"] is False
    assert search_summary["real_navigation_state_persisted"] is False
    assert search_summary["real_drawer_selection_saved"] is False
    assert search_summary["real_raw_evidence_revealed"] is False

    selected = payload["selected_navigation_preview"]
    assert selected["selected_navigation_preview_id"].startswith("version_compare_navigation_selected_nav_")
    assert selected["default_filter_lane_id"] == "all_compare_drawers"
    assert selected["selected_navigation_item_id"]
    assert selected["selected_drawer_selection_preview_id"]
    assert selected["selected_version_detail_drawer_id"]
    assert selected["selected_version_detail_drawer_count"] >= 15
    assert selected["selected_compare_row_count"] >= 75
    assert isinstance(selected["selected_compare_row_ids"], list)
    assert len(selected["selected_compare_row_ids"]) >= 75
    assert selected["selection_status"] == "version_compare_navigation_selected_navigation_preview_ready"
    assert selected["selection_result_type"] == "owner_note_version_compare_navigation_selected_navigation_preview"
    assert selected["open_allowed_in_preview"] is True
    assert selected["selection_allowed_in_preview"] is True
    assert selected["safe_preview_only"] is True
    assert selected["real_filter_preference_saved"] is False
    assert selected["real_navigation_state_persisted"] is False
    assert selected["real_drawer_selection_saved"] is False
    assert selected["real_raw_evidence_revealed"] is False

    indexes = payload["filter_navigation_indexes"]

    assert indexes["navigation_items_by_id"]
    assert indexes["navigation_items_by_filter_lane_id"]
    assert indexes["navigation_items_by_filter_type"]
    assert indexes["drawer_selections_by_id"]
    assert indexes["drawer_selections_by_filter_lane_id"]
    assert indexes["navigation_groups_by_id"]
    assert indexes["navigation_groups_by_filter_lane_id"]
    assert indexes["version_detail_drawer_ids_by_filter_lane_id"]
    assert indexes["compare_row_ids_by_filter_lane_id"]

    assert "all_compare_drawers" in indexes["navigation_items_by_filter_lane_id"]
    assert "saved_view_preset_drawers" in indexes["navigation_items_by_filter_lane_id"]
    assert "filter_preset_drawers" in indexes["navigation_items_by_filter_lane_id"]
    assert "safe_preview_only" in indexes["navigation_items_by_filter_lane_id"]

    assert "all" in indexes["navigation_items_by_filter_type"]
    assert "source_kind" in indexes["navigation_items_by_filter_type"]
    assert "change_state" in indexes["navigation_items_by_filter_type"]
    assert "safety" in indexes["navigation_items_by_filter_type"]
    assert "blocked_action" in indexes["navigation_items_by_filter_type"]

    assert indexes["version_detail_drawer_ids_by_filter_lane_id"]["all_compare_drawers"]
    assert indexes["compare_row_ids_by_filter_lane_id"]["all_compare_drawers"]
    assert len(indexes["compare_row_ids_by_filter_lane_id"]["all_compare_drawers"]) >= 75

    bridge = mod.build_owner_note_vc_nav_filter_nav_v194_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 194
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/owner-note-vc-nav-filter-nav-v194.json"
    assert bridge["navigation_item_count"] == 9
    assert bridge["drawer_selection_preview_count"] == 9
    assert bridge["navigation_group_count"] == 9
    assert bridge["search_navigation_facet_count"] == 5
    assert bridge["search_navigation_chip_count"] == 9
    assert bridge["total_navigation_drawer_reference_count"] >= 15
    assert bridge["total_navigation_compare_row_reference_count"] >= 75
    assert bridge["default_filter_lane_id"] == "all_compare_drawers"
    assert bridge["selected_navigation_item_id"]
    assert bridge["selected_version_detail_drawer_id"]
    assert bridge["selected_compare_row_count"] >= 75

    action = mod.build_owner_note_vc_nav_filter_nav_v194_quick_action()
    assert action["id"] == "owner_note_vc_nav_filter_nav_v194"
    assert action["href"] == "/tower/owner-note-vc-nav-filter-nav-v194.json"
    assert action["status"] == "ready"

    section = mod.build_owner_note_vc_nav_filter_nav_v194_unified_owner_section()
    assert section["section_id"] == "owner_note_vc_nav_filter_nav_v194"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/owner-note-vc-nav-filter-nav-v194.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_194_owner_note_vc_nav_filter_nav_v194_status_bridge")
    tower_bridge = status.build_pack_194_owner_note_vc_nav_filter_nav_v194_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_194_owner_note_vc_nav_filter_nav_v194_quick_action")
    assert hasattr(qa, "append_pack_194_owner_note_vc_nav_filter_nav_v194_quick_action")
    actions = qa.append_pack_194_owner_note_vc_nav_filter_nav_v194_quick_action([])
    assert any(item.get("id") == "owner_note_vc_nav_filter_nav_v194" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_194_owner_note_vc_nav_filter_nav_v194_unified_section")
    assert hasattr(unified, "append_pack_194_owner_note_vc_nav_filter_nav_v194_section")
    sections = unified.append_pack_194_owner_note_vc_nav_filter_nav_v194_section([])
    assert any(item.get("section_id") == "owner_note_vc_nav_filter_nav_v194" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-filter-nav-v194.json" in app_text
    assert "tower_owner_note_vc_nav_filter_nav_v194_json" in app_text
    assert "_pack_194_owner_note_vc_nav_filter_nav_v194_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-filter-nav-v194.json" in route_text
    assert "_pack_194_owner_note_vc_nav_filter_nav_v194_route_guard" in route_text

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
