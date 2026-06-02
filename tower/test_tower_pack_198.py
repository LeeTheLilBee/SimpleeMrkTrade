
"""
PACK 198 fast test - Owner Note Version Compare Navigation Action Receipt
Filter Navigation / Receipt Selection Preview.

Uses short safe module:
    tower.owner_note_vc_nav_action_receipt_filter_nav_v198
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_198_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.owner_note_vc_nav_action_receipt_filter_nav_v198")
    payload = mod.build_owner_note_vc_nav_action_receipt_filter_nav_v198_payload(force_refresh=True)

    assert payload["pack_number"] == 198
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/owner-note-vc-nav-action-receipt-filter-nav-v198.json"
    assert payload["source_endpoint"] == "/tower/owner-note-vc-nav-action-receipt-filter-v197.json"

    required_true = [
        "simulated_only",
        "action_receipt_navigation_preview_only",
        "receipt_selection_preview_only",
        "action_receipt_filter_preview_only",
        "search_facet_preview_only",
        "filter_preview_only",
        "filter_navigation_preview_only",
        "action_receipt_preview_only",
        "cached_non_recursive",
    ]

    for key in required_true:
        assert payload[key] is True, key

    required_false = [
        "real_action_executed",
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
    assert summary["action_receipt_navigation_item_count"] == 8
    assert summary["action_receipt_selection_preview_count"] == 8
    assert summary["action_receipt_navigation_group_count"] == 8
    assert summary["search_navigation_facet_count"] == 5
    assert summary["search_navigation_chip_count"] == 8
    assert summary["total_navigation_receipt_reference_count"] >= 5
    assert summary["default_action_receipt_filter_lane_id"] == "all_action_receipts"
    assert summary["selected_action_receipt_navigation_item_id"]
    assert summary["selected_action_receipt_selection_preview_id"]
    assert summary["selected_action_receipt_id"]
    assert summary["selected_action_receipt_count"] == 5

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_197_ready",
        "has_filter_lanes",
        "has_navigation_items",
        "has_receipt_selection_previews",
        "has_navigation_groups",
        "has_search_navigation_summary",
        "default_selected_navigation_ready",
        "default_all_action_receipts_navigation_present",
        "all_navigation_items_ready",
        "all_receipt_selections_ready",
        "all_navigation_groups_ready",
        "navigation_indexes_present",
        "selection_indexes_present",
        "group_indexes_present",
        "has_receipt_references",
        "selected_receipt_present",
        "selected_receipts_match_total",
        "all_simulated_only",
        "all_action_receipt_navigation_preview_only",
        "all_receipt_selection_preview_only",
        "all_action_receipt_filter_preview_only",
        "all_action_receipt_preview_only",
        "no_real_action_executed",
        "no_real_filter_preference_saved",
        "no_real_navigation_state_persisted",
        "no_real_drawer_selection_saved",
        "no_real_raw_evidence_revealed",
        "all_action_execution_blocked",
        "all_filter_preference_saves_blocked",
        "all_navigation_persistence_blocked",
        "all_drawer_selection_saves_blocked",
        "all_raw_evidence_reveal_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_198_navigation_items_selections_and_groups():
    mod = importlib.import_module("tower.owner_note_vc_nav_action_receipt_filter_nav_v198")
    payload = mod.build_owner_note_vc_nav_action_receipt_filter_nav_v198_payload(force_refresh=True)

    nav_items = payload["action_receipt_navigation_items"]
    selections = payload["action_receipt_selection_previews"]
    groups = payload["action_receipt_navigation_groups"]

    assert len(nav_items) == 8
    assert len(selections) == 8
    assert len(groups) == 8

    expected_lanes = {
        "all_action_receipts",
        "preview_action_receipts",
        "blocked_action_receipts",
        "allowed_in_preview",
        "blocked_in_preview",
        "no_real_execution",
        "raw_reveal_blocked",
        "persistence_blocked",
    }

    assert {item["action_receipt_filter_lane_id"] for item in nav_items} == expected_lanes
    assert {item["action_receipt_filter_lane_id"] for item in selections} == expected_lanes
    assert {item["action_receipt_filter_lane_id"] for item in groups} == expected_lanes

    for item in nav_items:
        assert item["action_receipt_navigation_item_id"].startswith("version_compare_navigation_action_receipt_nav_item_")
        assert item["action_receipt_filter_lane_id"] in expected_lanes
        assert item["action_receipt_filter_lane_preview_id"]
        assert item["label"]
        assert item["description"]
        assert item["filter_type"] in {"all", "receipt_kind", "allowed_state", "blocked_state", "safety"}
        assert item["sequence"] >= 1
        assert item["matched_action_receipt_count"] >= 0
        assert isinstance(item["matched_action_receipt_ids"], list)
        assert item["matched_action_receipt_count"] == len(item["matched_action_receipt_ids"])
        assert item["navigation_status"] == "version_compare_navigation_action_receipt_navigation_item_preview_ready"
        assert item["navigation_result_type"] == "owner_note_version_compare_navigation_action_receipt_navigation_item_preview"
        assert item["open_allowed_in_preview"] is True
        assert item["selection_allowed_in_preview"] is True
        assert item["safe_preview_only"] is True

        assert item["simulated_only"] is True
        assert item["action_receipt_navigation_preview_only"] is True
        assert item["receipt_selection_preview_only"] is True
        assert item["action_receipt_filter_preview_only"] is True
        assert item["action_receipt_preview_only"] is True
        assert item["real_action_executed"] is False
        assert item["real_filter_preference_saved"] is False
        assert item["real_navigation_state_persisted"] is False
        assert item["real_drawer_selection_saved"] is False
        assert item["real_raw_evidence_revealed"] is False
        assert item["action_execution_allowed_now"] is False
        assert item["filter_preference_save_allowed_now"] is False
        assert item["navigation_persistence_allowed_now"] is False
        assert item["drawer_selection_save_allowed_now"] is False
        assert item["raw_evidence_reveal_allowed"] is False

    nav_by_lane = {item["action_receipt_filter_lane_id"]: item for item in nav_items}

    assert nav_by_lane["all_action_receipts"]["matched_action_receipt_count"] == 5
    assert nav_by_lane["preview_action_receipts"]["matched_action_receipt_count"] == 3
    assert nav_by_lane["blocked_action_receipts"]["matched_action_receipt_count"] == 2
    assert nav_by_lane["allowed_in_preview"]["matched_action_receipt_count"] == 3
    assert nav_by_lane["blocked_in_preview"]["matched_action_receipt_count"] == 2
    assert nav_by_lane["no_real_execution"]["matched_action_receipt_count"] == 5
    assert nav_by_lane["raw_reveal_blocked"]["matched_action_receipt_count"] == 5
    assert nav_by_lane["persistence_blocked"]["matched_action_receipt_count"] == 5
    assert nav_by_lane["all_action_receipts"]["default_action_receipt_id"]

    selection_by_lane = {item["action_receipt_filter_lane_id"]: item for item in selections}
    group_by_lane = {item["action_receipt_filter_lane_id"]: item for item in groups}

    for lane_id in expected_lanes:
        nav = nav_by_lane[lane_id]
        selection = selection_by_lane[lane_id]
        group = group_by_lane[lane_id]

        assert selection["action_receipt_selection_preview_id"].startswith("version_compare_navigation_action_receipt_selection_")
        assert selection["action_receipt_navigation_item_id"] == nav["action_receipt_navigation_item_id"]
        assert selection["action_receipt_filter_lane_id"] == lane_id
        assert selection["selected_action_receipt_id"] == nav["default_action_receipt_id"]
        assert selection["available_action_receipt_count"] == nav["matched_action_receipt_count"]
        assert selection["available_action_receipt_count"] == len(selection["available_action_receipt_ids"])
        assert selection["selection_status"] == "version_compare_navigation_action_receipt_selection_preview_ready"
        assert selection["selection_result_type"] == "owner_note_version_compare_navigation_action_receipt_selection_preview"
        assert selection["open_allowed_in_preview"] is True
        assert selection["selection_allowed_in_preview"] is True
        assert selection["safe_preview_only"] is True
        assert selection["real_action_executed"] is False
        assert selection["real_filter_preference_saved"] is False
        assert selection["real_navigation_state_persisted"] is False
        assert selection["real_drawer_selection_saved"] is False
        assert selection["real_raw_evidence_revealed"] is False

        assert group["action_receipt_navigation_group_id"].startswith("version_compare_navigation_action_receipt_navigation_group_")
        assert group["action_receipt_navigation_item_id"] == nav["action_receipt_navigation_item_id"]
        assert group["action_receipt_selection_preview_id"] == selection["action_receipt_selection_preview_id"]
        assert group["action_receipt_filter_lane_id"] == lane_id
        assert group["label"] == nav["label"]
        assert group["action_receipt_count"] == nav["matched_action_receipt_count"]
        assert group["selected_action_receipt_id"] == selection["selected_action_receipt_id"]
        assert group["group_status"] == "version_compare_navigation_action_receipt_navigation_group_preview_ready"
        assert group["group_result_type"] == "owner_note_version_compare_navigation_action_receipt_navigation_group_preview"
        assert group["safe_preview_only"] is True
        assert group["real_action_executed"] is False
        assert group["real_filter_preference_saved"] is False
        assert group["real_navigation_state_persisted"] is False
        assert group["real_drawer_selection_saved"] is False

    assert selection_by_lane["all_action_receipts"]["selected_action_receipt_id"]
    assert selection_by_lane["all_action_receipts"]["available_action_receipt_count"] == 5


def test_pack_198_search_summary_selected_preview_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.owner_note_vc_nav_action_receipt_filter_nav_v198")
    payload = mod.build_owner_note_vc_nav_action_receipt_filter_nav_v198_payload(force_refresh=True)

    search_summary = payload["action_receipt_search_navigation_summary"]
    assert search_summary["action_receipt_search_navigation_summary_id"].startswith("version_compare_navigation_action_receipt_search_summary_")
    assert search_summary["action_receipt_search_facet_count"] == 5
    assert isinstance(search_summary["action_receipt_search_facet_ids"], list)
    assert len(search_summary["action_receipt_search_facet_ids"]) == 5
    assert search_summary["action_receipt_search_facet_value_count"] >= 1
    assert search_summary["action_receipt_quick_filter_chip_count"] == 8
    assert isinstance(search_summary["action_receipt_quick_filter_chip_ids"], list)
    assert len(search_summary["action_receipt_quick_filter_chip_ids"]) == 8
    assert search_summary["search_query_preview"] == ""
    assert search_summary["summary_status"] == "version_compare_navigation_action_receipt_search_summary_preview_ready"
    assert search_summary["summary_result_type"] == "owner_note_version_compare_navigation_action_receipt_search_summary_preview"
    assert search_summary["search_allowed_in_preview"] is True
    assert search_summary["safe_preview_only"] is True
    assert search_summary["real_action_executed"] is False
    assert search_summary["real_filter_preference_saved"] is False
    assert search_summary["real_navigation_state_persisted"] is False
    assert search_summary["real_raw_evidence_revealed"] is False

    selected = payload["selected_action_receipt_navigation_preview"]
    assert selected["selected_action_receipt_navigation_preview_id"].startswith("version_compare_navigation_selected_action_receipt_nav_")
    assert selected["default_action_receipt_filter_lane_id"] == "all_action_receipts"
    assert selected["selected_action_receipt_navigation_item_id"]
    assert selected["selected_action_receipt_selection_preview_id"]
    assert selected["selected_action_receipt_id"]
    assert selected["selected_action_receipt_count"] == 5
    assert isinstance(selected["selected_action_receipt_ids"], list)
    assert len(selected["selected_action_receipt_ids"]) == 5
    assert selected["selection_status"] == "version_compare_navigation_selected_action_receipt_navigation_preview_ready"
    assert selected["selection_result_type"] == "owner_note_version_compare_navigation_selected_action_receipt_navigation_preview"
    assert selected["open_allowed_in_preview"] is True
    assert selected["selection_allowed_in_preview"] is True
    assert selected["safe_preview_only"] is True
    assert selected["real_action_executed"] is False
    assert selected["real_filter_preference_saved"] is False
    assert selected["real_navigation_state_persisted"] is False
    assert selected["real_drawer_selection_saved"] is False
    assert selected["real_raw_evidence_revealed"] is False

    indexes = payload["action_receipt_filter_navigation_indexes"]

    assert indexes["action_receipt_navigation_items_by_id"]
    assert indexes["action_receipt_navigation_items_by_filter_lane_id"]
    assert indexes["action_receipt_navigation_items_by_filter_type"]
    assert indexes["action_receipt_selections_by_id"]
    assert indexes["action_receipt_selections_by_filter_lane_id"]
    assert indexes["action_receipt_navigation_groups_by_id"]
    assert indexes["action_receipt_navigation_groups_by_filter_lane_id"]
    assert indexes["action_receipt_ids_by_filter_lane_id"]

    assert "all_action_receipts" in indexes["action_receipt_navigation_items_by_filter_lane_id"]
    assert "preview_action_receipts" in indexes["action_receipt_navigation_items_by_filter_lane_id"]
    assert "blocked_action_receipts" in indexes["action_receipt_navigation_items_by_filter_lane_id"]
    assert "no_real_execution" in indexes["action_receipt_navigation_items_by_filter_lane_id"]

    assert len(indexes["action_receipt_ids_by_filter_lane_id"]["all_action_receipts"]) == 5
    assert len(indexes["action_receipt_ids_by_filter_lane_id"]["preview_action_receipts"]) == 3
    assert len(indexes["action_receipt_ids_by_filter_lane_id"]["blocked_action_receipts"]) == 2

    bridge = mod.build_owner_note_vc_nav_action_receipt_filter_nav_v198_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 198
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/owner-note-vc-nav-action-receipt-filter-nav-v198.json"
    assert bridge["action_receipt_navigation_item_count"] == 8
    assert bridge["action_receipt_selection_preview_count"] == 8
    assert bridge["action_receipt_navigation_group_count"] == 8
    assert bridge["search_navigation_facet_count"] == 5
    assert bridge["search_navigation_chip_count"] == 8
    assert bridge["total_navigation_receipt_reference_count"] >= 5
    assert bridge["default_action_receipt_filter_lane_id"] == "all_action_receipts"
    assert bridge["selected_action_receipt_navigation_item_id"]
    assert bridge["selected_action_receipt_selection_preview_id"]
    assert bridge["selected_action_receipt_id"]
    assert bridge["selected_action_receipt_count"] == 5

    action = mod.build_owner_note_vc_nav_action_receipt_filter_nav_v198_quick_action()
    assert action["id"] == "owner_note_vc_nav_action_receipt_filter_nav_v198"
    assert action["href"] == "/tower/owner-note-vc-nav-action-receipt-filter-nav-v198.json"
    assert action["status"] == "ready"

    section = mod.build_owner_note_vc_nav_action_receipt_filter_nav_v198_unified_owner_section()
    assert section["section_id"] == "owner_note_vc_nav_action_receipt_filter_nav_v198"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/owner-note-vc-nav-action-receipt-filter-nav-v198.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_198_owner_note_vc_nav_action_receipt_filter_nav_v198_status_bridge")
    tower_bridge = status.build_pack_198_owner_note_vc_nav_action_receipt_filter_nav_v198_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_198_owner_note_vc_nav_action_receipt_filter_nav_v198_quick_action")
    assert hasattr(qa, "append_pack_198_owner_note_vc_nav_action_receipt_filter_nav_v198_quick_action")
    actions = qa.append_pack_198_owner_note_vc_nav_action_receipt_filter_nav_v198_quick_action([])
    assert any(item.get("id") == "owner_note_vc_nav_action_receipt_filter_nav_v198" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_198_owner_note_vc_nav_action_receipt_filter_nav_v198_unified_section")
    assert hasattr(unified, "append_pack_198_owner_note_vc_nav_action_receipt_filter_nav_v198_section")
    sections = unified.append_pack_198_owner_note_vc_nav_action_receipt_filter_nav_v198_section([])
    assert any(item.get("section_id") == "owner_note_vc_nav_action_receipt_filter_nav_v198" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-action-receipt-filter-nav-v198.json" in app_text
    assert "tower_owner_note_vc_nav_action_receipt_filter_nav_v198_json" in app_text
    assert "_pack_198_owner_note_vc_nav_action_receipt_filter_nav_v198_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-action-receipt-filter-nav-v198.json" in route_text
    assert "_pack_198_owner_note_vc_nav_action_receipt_filter_nav_v198_route_guard" in route_text

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
