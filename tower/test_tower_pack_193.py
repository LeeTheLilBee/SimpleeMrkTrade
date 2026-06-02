
"""
PACK 193 fast test - Owner Note Version Compare Navigation Compare
Filter / Search Facets Preview.

Uses short safe module:
    tower.owner_note_vc_nav_compare_filter_v193
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_193_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.owner_note_vc_nav_compare_filter_v193")
    payload = mod.build_owner_note_vc_nav_compare_filter_v193_payload(force_refresh=True)

    assert payload["pack_number"] == 193
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/owner-note-vc-nav-compare-filter-v193.json"
    assert payload["source_endpoint"] == "/tower/owner-note-vc-nav-version-compare-v192.json"

    required_true = [
        "simulated_only",
        "filter_preview_only",
        "search_facet_preview_only",
        "filter_navigation_preview_only",
        "version_detail_preview_only",
        "compare_view_preview_only",
        "version_preview_only",
        "edit_history_preview_only",
        "navigation_preview_only",
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
    assert summary["filter_lane_count"] == 9
    assert summary["search_facet_count"] == 5
    assert summary["quick_filter_chip_count"] == 9
    assert summary["source_version_detail_drawer_count"] >= 15
    assert summary["total_lane_drawer_match_count"] >= summary["source_version_detail_drawer_count"]
    assert summary["total_lane_compare_row_match_count"] >= 75
    assert summary["default_filter_lane_id"] == "all_compare_drawers"
    assert summary["selected_version_detail_drawer_count"] >= 15
    assert summary["selected_compare_row_count"] >= 75

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_192_ready",
        "has_version_detail_drawers",
        "has_filter_lanes",
        "has_search_facets",
        "has_quick_filter_chips",
        "default_all_compare_lane_present",
        "saved_view_lane_present",
        "filter_preset_lane_present",
        "changed_lane_present",
        "safe_preview_lane_present",
        "all_filter_lanes_ready",
        "all_search_facets_ready",
        "all_quick_chips_ready",
        "selected_filter_preview_ready",
        "filter_lane_indexes_present",
        "search_facet_indexes_present",
        "quick_chip_indexes_present",
        "drawer_search_text_index_present",
        "has_lane_drawer_matches",
        "has_lane_row_matches",
        "all_simulated_only",
        "all_filter_preview_only",
        "all_search_facet_preview_only",
        "all_version_detail_preview_only",
        "all_compare_view_preview_only",
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


def test_pack_193_filter_lanes_facets_and_quick_chips():
    mod = importlib.import_module("tower.owner_note_vc_nav_compare_filter_v193")
    payload = mod.build_owner_note_vc_nav_compare_filter_v193_payload(force_refresh=True)

    lanes = payload["filter_lanes"]
    facets = payload["search_facets"]
    chips = payload["quick_filter_chips"]

    assert len(lanes) == 9
    assert len(facets) == 5
    assert len(chips) == 9

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

    lane_ids = {lane["filter_lane_id"] for lane in lanes}
    assert lane_ids == expected_lane_ids

    for lane in lanes:
        assert lane["filter_lane_preview_id"].startswith("version_compare_navigation_filter_lane_")
        assert lane["filter_lane_id"] in expected_lane_ids
        assert lane["label"]
        assert lane["description"]
        assert lane["filter_type"] in {"all", "source_kind", "change_state", "safety", "blocked_action"}
        assert lane["sequence"] >= 1
        assert lane["matched_version_detail_drawer_count"] >= 0
        assert isinstance(lane["matched_version_detail_drawer_ids"], list)
        assert lane["matched_compare_row_count"] >= 0
        assert isinstance(lane["matched_compare_row_ids"], list)
        assert lane["filter_lane_status"] == "version_compare_navigation_compare_filter_lane_preview_ready"
        assert lane["filter_lane_result_type"] == "owner_note_version_compare_navigation_compare_filter_lane_preview"
        assert lane["filter_allowed_in_preview"] is True
        assert lane["selection_allowed_in_preview"] is True
        assert lane["safe_preview_only"] is True

        assert lane["simulated_only"] is True
        assert lane["filter_preview_only"] is True
        assert lane["search_facet_preview_only"] is True
        assert lane["filter_navigation_preview_only"] is True
        assert lane["version_detail_preview_only"] is True
        assert lane["compare_view_preview_only"] is True
        assert lane["real_filter_preference_saved"] is False
        assert lane["real_navigation_state_persisted"] is False
        assert lane["real_drawer_selection_saved"] is False
        assert lane["real_raw_evidence_revealed"] is False
        assert lane["filter_preference_save_allowed_now"] is False
        assert lane["navigation_persistence_allowed_now"] is False
        assert lane["drawer_selection_save_allowed_now"] is False
        assert lane["raw_evidence_reveal_allowed"] is False
        assert lane["raw_evidence_lookup_allowed"] is False

    all_lane = next(lane for lane in lanes if lane["filter_lane_id"] == "all_compare_drawers")
    saved_view_lane = next(lane for lane in lanes if lane["filter_lane_id"] == "saved_view_preset_drawers")
    filter_preset_lane = next(lane for lane in lanes if lane["filter_lane_id"] == "filter_preset_drawers")
    changed_lane = next(lane for lane in lanes if lane["filter_lane_id"] == "changed_compare_rows")
    safe_lane = next(lane for lane in lanes if lane["filter_lane_id"] == "safe_preview_only")

    assert all_lane["matched_version_detail_drawer_count"] >= 15
    assert all_lane["matched_compare_row_count"] >= 75
    assert saved_view_lane["matched_version_detail_drawer_count"] == 6
    assert filter_preset_lane["matched_version_detail_drawer_count"] >= 9
    assert changed_lane["matched_version_detail_drawer_count"] >= 1
    assert safe_lane["matched_version_detail_drawer_count"] >= 15

    expected_facets = {"source_kind", "drawer_status", "field_id", "change_state", "safety_state"}
    facet_ids = {facet["search_facet_id"] for facet in facets}
    assert facet_ids == expected_facets

    for facet in facets:
        assert facet["search_facet_preview_id"].startswith("version_compare_navigation_search_facet_")
        assert facet["search_facet_id"] in expected_facets
        assert facet["label"]
        assert facet["facet_type"] in {"source_kind", "status", "field", "change_state", "safety"}
        assert facet["sequence"] >= 1
        assert isinstance(facet["values"], list)
        assert facet["value_count"] == len(facet["values"])
        assert facet["value_count"] >= 1
        assert facet["search_facet_status"] == "version_compare_navigation_compare_search_facet_preview_ready"
        assert facet["search_facet_result_type"] == "owner_note_version_compare_navigation_compare_search_facet_preview"
        assert facet["search_allowed_in_preview"] is True
        assert facet["safe_preview_only"] is True

        assert facet["simulated_only"] is True
        assert facet["filter_preview_only"] is True
        assert facet["search_facet_preview_only"] is True
        assert facet["real_filter_preference_saved"] is False
        assert facet["real_navigation_state_persisted"] is False
        assert facet["real_drawer_selection_saved"] is False

        for value in facet["values"]:
            assert value["value_id"]
            assert value["label"]
            assert value["count"] >= 1
            assert isinstance(value["matched_version_detail_drawer_ids"], list)

    chip_lane_ids = {chip["filter_lane_id"] for chip in chips}
    assert chip_lane_ids == expected_lane_ids

    for chip in chips:
        assert chip["quick_filter_chip_id"].startswith("version_compare_navigation_quick_filter_chip_")
        assert chip["filter_lane_id"] in expected_lane_ids
        assert chip["label"]
        assert chip["sequence"] >= 1
        assert chip["matched_version_detail_drawer_count"] >= 0
        assert chip["matched_compare_row_count"] >= 0
        assert chip["chip_status"] == "version_compare_navigation_quick_filter_chip_preview_ready"
        assert chip["chip_result_type"] == "owner_note_version_compare_navigation_quick_filter_chip_preview"
        assert chip["selection_allowed_in_preview"] is True
        assert chip["safe_preview_only"] is True
        assert chip["simulated_only"] is True
        assert chip["filter_preview_only"] is True
        assert chip["real_filter_preference_saved"] is False
        assert chip["real_navigation_state_persisted"] is False
        assert chip["real_drawer_selection_saved"] is False


def test_pack_193_selected_preview_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.owner_note_vc_nav_compare_filter_v193")
    payload = mod.build_owner_note_vc_nav_compare_filter_v193_payload(force_refresh=True)

    selected = payload["selected_filter_preview"]
    assert selected["selected_filter_preview_id"].startswith("version_compare_navigation_selected_filter_")
    assert selected["selected_filter_lane_id"] == "all_compare_drawers"
    assert selected["selected_filter_lane_preview_id"]
    assert selected["selected_search_query"] == ""
    assert isinstance(selected["selected_search_facet_ids"], list)
    assert len(selected["selected_search_facet_ids"]) == 5
    assert selected["selected_version_detail_drawer_count"] >= 15
    assert selected["selected_compare_row_count"] >= 75
    assert isinstance(selected["selected_version_detail_drawer_ids"], list)
    assert selected["selection_status"] == "version_compare_navigation_selected_compare_filter_preview_ready"
    assert selected["selection_result_type"] == "owner_note_version_compare_navigation_selected_compare_filter_preview"
    assert selected["filter_allowed_in_preview"] is True
    assert selected["search_allowed_in_preview"] is True
    assert selected["selection_allowed_in_preview"] is True
    assert selected["safe_preview_only"] is True
    assert selected["real_filter_preference_saved"] is False
    assert selected["real_navigation_state_persisted"] is False
    assert selected["real_drawer_selection_saved"] is False
    assert selected["real_raw_evidence_revealed"] is False

    indexes = payload["compare_filter_indexes"]

    assert indexes["filter_lanes_by_id"]
    assert indexes["filter_lanes_by_type"]
    assert indexes["search_facets_by_id"]
    assert indexes["search_facets_by_type"]
    assert indexes["quick_filter_chips_by_id"]
    assert indexes["quick_filter_chips_by_lane_id"]
    assert indexes["version_detail_drawers_by_filter_lane_id"]
    assert indexes["compare_rows_by_filter_lane_id"]
    assert indexes["drawer_search_text_by_id"]

    assert "all_compare_drawers" in indexes["filter_lanes_by_id"]
    assert "saved_view_preset_drawers" in indexes["filter_lanes_by_id"]
    assert "filter_preset_drawers" in indexes["filter_lanes_by_id"]
    assert "changed_compare_rows" in indexes["filter_lanes_by_id"]
    assert "safe_preview_only" in indexes["filter_lanes_by_id"]

    assert "source_kind" in indexes["search_facets_by_id"]
    assert "drawer_status" in indexes["search_facets_by_id"]
    assert "field_id" in indexes["search_facets_by_id"]
    assert "change_state" in indexes["search_facets_by_id"]
    assert "safety_state" in indexes["search_facets_by_id"]

    assert "all" in indexes["filter_lanes_by_type"]
    assert "source_kind" in indexes["filter_lanes_by_type"]
    assert "change_state" in indexes["filter_lanes_by_type"]
    assert "safety" in indexes["filter_lanes_by_type"]
    assert "blocked_action" in indexes["filter_lanes_by_type"]

    assert indexes["version_detail_drawers_by_filter_lane_id"]["all_compare_drawers"]
    assert indexes["compare_rows_by_filter_lane_id"]["all_compare_drawers"]
    assert indexes["drawer_search_text_by_id"]

    bridge = mod.build_owner_note_vc_nav_compare_filter_v193_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 193
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/owner-note-vc-nav-compare-filter-v193.json"
    assert bridge["filter_lane_count"] == 9
    assert bridge["search_facet_count"] == 5
    assert bridge["quick_filter_chip_count"] == 9
    assert bridge["source_version_detail_drawer_count"] >= 15
    assert bridge["total_lane_drawer_match_count"] >= 15
    assert bridge["total_lane_compare_row_match_count"] >= 75
    assert bridge["default_filter_lane_id"] == "all_compare_drawers"
    assert bridge["selected_version_detail_drawer_count"] >= 15
    assert bridge["selected_compare_row_count"] >= 75

    action = mod.build_owner_note_vc_nav_compare_filter_v193_quick_action()
    assert action["id"] == "owner_note_vc_nav_compare_filter_v193"
    assert action["href"] == "/tower/owner-note-vc-nav-compare-filter-v193.json"
    assert action["status"] == "ready"

    section = mod.build_owner_note_vc_nav_compare_filter_v193_unified_owner_section()
    assert section["section_id"] == "owner_note_vc_nav_compare_filter_v193"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/owner-note-vc-nav-compare-filter-v193.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_193_owner_note_vc_nav_compare_filter_v193_status_bridge")
    tower_bridge = status.build_pack_193_owner_note_vc_nav_compare_filter_v193_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_193_owner_note_vc_nav_compare_filter_v193_quick_action")
    assert hasattr(qa, "append_pack_193_owner_note_vc_nav_compare_filter_v193_quick_action")
    actions = qa.append_pack_193_owner_note_vc_nav_compare_filter_v193_quick_action([])
    assert any(item.get("id") == "owner_note_vc_nav_compare_filter_v193" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_193_owner_note_vc_nav_compare_filter_v193_unified_section")
    assert hasattr(unified, "append_pack_193_owner_note_vc_nav_compare_filter_v193_section")
    sections = unified.append_pack_193_owner_note_vc_nav_compare_filter_v193_section([])
    assert any(item.get("section_id") == "owner_note_vc_nav_compare_filter_v193" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-compare-filter-v193.json" in app_text
    assert "tower_owner_note_vc_nav_compare_filter_v193_json" in app_text
    assert "_pack_193_owner_note_vc_nav_compare_filter_v193_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-compare-filter-v193.json" in route_text
    assert "_pack_193_owner_note_vc_nav_compare_filter_v193_route_guard" in route_text

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
