
"""
PACK 197 fast test - Owner Note Version Compare Navigation Action Receipt
Filter / Search Facets Preview.

Uses short safe module:
    tower.owner_note_vc_nav_action_receipt_filter_v197
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_197_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.owner_note_vc_nav_action_receipt_filter_v197")
    payload = mod.build_owner_note_vc_nav_action_receipt_filter_v197_payload(force_refresh=True)

    assert payload["pack_number"] == 197
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/owner-note-vc-nav-action-receipt-filter-v197.json"
    assert payload["source_endpoint"] == "/tower/owner-note-vc-nav-focus-action-receipts-v196.json"

    required_true = [
        "simulated_only",
        "action_receipt_filter_preview_only",
        "search_facet_preview_only",
        "filter_preview_only",
        "filter_navigation_preview_only",
        "action_receipt_preview_only",
        "blocked_action_receipt_preview_only",
        "preview_action_receipt_preview_only",
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
    assert summary["action_receipt_filter_lane_count"] == 8
    assert summary["action_receipt_search_facet_count"] == 5
    assert summary["action_receipt_quick_filter_chip_count"] == 8
    assert summary["source_action_receipt_count"] == 5
    assert summary["selected_action_receipt_filter_lane_id"] == "all_action_receipts"
    assert summary["selected_action_receipt_count"] == 5

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_196_ready",
        "has_action_receipts",
        "has_filter_lanes",
        "has_search_facets",
        "has_quick_filter_chips",
        "default_all_action_receipts_lane_present",
        "all_filter_lanes_ready",
        "all_search_facets_ready",
        "all_quick_chips_ready",
        "selected_filter_preview_ready",
        "filter_indexes_present",
        "facet_indexes_present",
        "chip_indexes_present",
        "selected_filter_index_present",
        "selected_receipts_match_total",
        "all_simulated_only",
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


def test_pack_197_filter_lanes_facets_and_chips():
    mod = importlib.import_module("tower.owner_note_vc_nav_action_receipt_filter_v197")
    payload = mod.build_owner_note_vc_nav_action_receipt_filter_v197_payload(force_refresh=True)

    lanes = payload["action_receipt_filter_lanes"]
    facets = payload["action_receipt_search_facets"]
    chips = payload["action_receipt_quick_filter_chips"]

    assert len(lanes) == 8
    assert len(facets) == 5
    assert len(chips) == 8

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

    lane_ids = {lane["action_receipt_filter_lane_id"] for lane in lanes}
    assert lane_ids == expected_lanes

    for lane in lanes:
        assert lane["action_receipt_filter_lane_preview_id"].startswith("version_compare_navigation_action_receipt_filter_lane_")
        assert lane["action_receipt_filter_lane_id"] in expected_lanes
        assert lane["label"]
        assert lane["description"]
        assert lane["filter_type"] in {"all", "receipt_kind", "allowed_state", "blocked_state", "safety"}
        assert lane["sequence"] >= 1
        assert lane["matched_action_receipt_count"] >= 0
        assert isinstance(lane["matched_action_receipt_ids"], list)
        assert lane["matched_action_receipt_count"] == len(lane["matched_action_receipt_ids"])
        assert lane["filter_lane_status"] == "version_compare_navigation_action_receipt_filter_lane_preview_ready"
        assert lane["filter_lane_result_type"] == "owner_note_version_compare_navigation_action_receipt_filter_lane_preview"
        assert lane["filter_allowed_in_preview"] is True
        assert lane["selection_allowed_in_preview"] is True
        assert lane["safe_preview_only"] is True

        assert lane["simulated_only"] is True
        assert lane["action_receipt_filter_preview_only"] is True
        assert lane["action_receipt_preview_only"] is True
        assert lane["real_action_executed"] is False
        assert lane["real_filter_preference_saved"] is False
        assert lane["real_navigation_state_persisted"] is False
        assert lane["real_drawer_selection_saved"] is False
        assert lane["real_raw_evidence_revealed"] is False
        assert lane["action_execution_allowed_now"] is False
        assert lane["filter_preference_save_allowed_now"] is False
        assert lane["navigation_persistence_allowed_now"] is False
        assert lane["drawer_selection_save_allowed_now"] is False
        assert lane["raw_evidence_reveal_allowed"] is False
        assert lane["raw_evidence_lookup_allowed"] is False

    by_lane = {lane["action_receipt_filter_lane_id"]: lane for lane in lanes}
    assert by_lane["all_action_receipts"]["matched_action_receipt_count"] == 5
    assert by_lane["preview_action_receipts"]["matched_action_receipt_count"] == 3
    assert by_lane["blocked_action_receipts"]["matched_action_receipt_count"] == 2
    assert by_lane["allowed_in_preview"]["matched_action_receipt_count"] == 3
    assert by_lane["blocked_in_preview"]["matched_action_receipt_count"] == 2
    assert by_lane["no_real_execution"]["matched_action_receipt_count"] == 5
    assert by_lane["raw_reveal_blocked"]["matched_action_receipt_count"] == 5
    assert by_lane["persistence_blocked"]["matched_action_receipt_count"] == 5

    expected_facets = {"action_id", "receipt_kind", "outcome", "blocked_state", "safety_state"}
    facet_ids = {facet["action_receipt_search_facet_id"] for facet in facets}
    assert facet_ids == expected_facets

    for facet in facets:
        assert facet["action_receipt_search_facet_preview_id"].startswith("version_compare_navigation_action_receipt_search_facet_")
        assert facet["action_receipt_search_facet_id"] in expected_facets
        assert facet["label"]
        assert facet["facet_type"] in {"action_id", "receipt_kind", "outcome", "blocked_state", "safety"}
        assert facet["sequence"] >= 1
        assert isinstance(facet["values"], list)
        assert facet["value_count"] == len(facet["values"])
        assert facet["value_count"] >= 1
        assert facet["search_facet_status"] == "version_compare_navigation_action_receipt_search_facet_preview_ready"
        assert facet["search_facet_result_type"] == "owner_note_version_compare_navigation_action_receipt_search_facet_preview"
        assert facet["search_allowed_in_preview"] is True
        assert facet["safe_preview_only"] is True

        assert facet["simulated_only"] is True
        assert facet["action_receipt_filter_preview_only"] is True
        assert facet["search_facet_preview_only"] is True
        assert facet["real_action_executed"] is False
        assert facet["real_filter_preference_saved"] is False
        assert facet["real_raw_evidence_revealed"] is False

        for value in facet["values"]:
            assert value["value_id"]
            assert value["label"]
            assert value["count"] >= 1
            assert isinstance(value["matched_action_receipt_ids"], list)

    chip_lane_ids = {chip["action_receipt_filter_lane_id"] for chip in chips}
    assert chip_lane_ids == expected_lanes

    for chip in chips:
        assert chip["action_receipt_quick_filter_chip_id"].startswith("version_compare_navigation_action_receipt_quick_chip_")
        assert chip["action_receipt_filter_lane_id"] in expected_lanes
        assert chip["label"]
        assert chip["sequence"] >= 1
        assert chip["matched_action_receipt_count"] >= 0
        assert chip["chip_status"] == "version_compare_navigation_action_receipt_quick_chip_preview_ready"
        assert chip["chip_result_type"] == "owner_note_version_compare_navigation_action_receipt_quick_chip_preview"
        assert chip["selection_allowed_in_preview"] is True
        assert chip["safe_preview_only"] is True
        assert chip["simulated_only"] is True
        assert chip["action_receipt_filter_preview_only"] is True
        assert chip["real_action_executed"] is False
        assert chip["real_filter_preference_saved"] is False
        assert chip["real_raw_evidence_revealed"] is False


def test_pack_197_selected_preview_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.owner_note_vc_nav_action_receipt_filter_v197")
    payload = mod.build_owner_note_vc_nav_action_receipt_filter_v197_payload(force_refresh=True)

    selected = payload["selected_action_receipt_filter_preview"]
    assert selected["selected_action_receipt_filter_preview_id"].startswith("version_compare_navigation_selected_action_receipt_filter_")
    assert selected["selected_action_receipt_filter_lane_id"] == "all_action_receipts"
    assert selected["selected_action_receipt_filter_lane_preview_id"]
    assert selected["selected_search_query"] == ""
    assert isinstance(selected["selected_action_receipt_search_facet_ids"], list)
    assert len(selected["selected_action_receipt_search_facet_ids"]) == 5
    assert selected["selected_action_receipt_count"] == 5
    assert isinstance(selected["selected_action_receipt_ids"], list)
    assert len(selected["selected_action_receipt_ids"]) == 5
    assert selected["selection_status"] == "version_compare_navigation_selected_action_receipt_filter_preview_ready"
    assert selected["selection_result_type"] == "owner_note_version_compare_navigation_selected_action_receipt_filter_preview"
    assert selected["filter_allowed_in_preview"] is True
    assert selected["search_allowed_in_preview"] is True
    assert selected["selection_allowed_in_preview"] is True
    assert selected["safe_preview_only"] is True
    assert selected["real_action_executed"] is False
    assert selected["real_filter_preference_saved"] is False
    assert selected["real_navigation_state_persisted"] is False
    assert selected["real_drawer_selection_saved"] is False
    assert selected["real_raw_evidence_revealed"] is False

    indexes = payload["action_receipt_filter_indexes"]

    assert indexes["action_receipt_filter_lanes_by_id"]
    assert indexes["action_receipt_filter_lanes_by_type"]
    assert indexes["action_receipt_search_facets_by_id"]
    assert indexes["action_receipt_search_facets_by_type"]
    assert indexes["action_receipt_quick_chips_by_id"]
    assert indexes["action_receipt_quick_chips_by_lane_id"]
    assert indexes["action_receipt_ids_by_filter_lane_id"]
    assert indexes["selected_action_receipt_filter_preview_by_id"]

    assert "all_action_receipts" in indexes["action_receipt_filter_lanes_by_id"]
    assert "preview_action_receipts" in indexes["action_receipt_filter_lanes_by_id"]
    assert "blocked_action_receipts" in indexes["action_receipt_filter_lanes_by_id"]
    assert "no_real_execution" in indexes["action_receipt_filter_lanes_by_id"]

    assert len(indexes["action_receipt_ids_by_filter_lane_id"]["all_action_receipts"]) == 5
    assert len(indexes["action_receipt_ids_by_filter_lane_id"]["preview_action_receipts"]) == 3
    assert len(indexes["action_receipt_ids_by_filter_lane_id"]["blocked_action_receipts"]) == 2

    assert selected["selected_action_receipt_filter_preview_id"] in indexes["selected_action_receipt_filter_preview_by_id"]

    bridge = mod.build_owner_note_vc_nav_action_receipt_filter_v197_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 197
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/owner-note-vc-nav-action-receipt-filter-v197.json"
    assert bridge["action_receipt_filter_lane_count"] == 8
    assert bridge["action_receipt_search_facet_count"] == 5
    assert bridge["action_receipt_quick_filter_chip_count"] == 8
    assert bridge["source_action_receipt_count"] == 5
    assert bridge["selected_action_receipt_filter_lane_id"] == "all_action_receipts"
    assert bridge["selected_action_receipt_count"] == 5

    action = mod.build_owner_note_vc_nav_action_receipt_filter_v197_quick_action()
    assert action["id"] == "owner_note_vc_nav_action_receipt_filter_v197"
    assert action["href"] == "/tower/owner-note-vc-nav-action-receipt-filter-v197.json"
    assert action["status"] == "ready"

    section = mod.build_owner_note_vc_nav_action_receipt_filter_v197_unified_owner_section()
    assert section["section_id"] == "owner_note_vc_nav_action_receipt_filter_v197"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/owner-note-vc-nav-action-receipt-filter-v197.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_197_owner_note_vc_nav_action_receipt_filter_v197_status_bridge")
    tower_bridge = status.build_pack_197_owner_note_vc_nav_action_receipt_filter_v197_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_197_owner_note_vc_nav_action_receipt_filter_v197_quick_action")
    assert hasattr(qa, "append_pack_197_owner_note_vc_nav_action_receipt_filter_v197_quick_action")
    actions = qa.append_pack_197_owner_note_vc_nav_action_receipt_filter_v197_quick_action([])
    assert any(item.get("id") == "owner_note_vc_nav_action_receipt_filter_v197" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_197_owner_note_vc_nav_action_receipt_filter_v197_unified_section")
    assert hasattr(unified, "append_pack_197_owner_note_vc_nav_action_receipt_filter_v197_section")
    sections = unified.append_pack_197_owner_note_vc_nav_action_receipt_filter_v197_section([])
    assert any(item.get("section_id") == "owner_note_vc_nav_action_receipt_filter_v197" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-action-receipt-filter-v197.json" in app_text
    assert "tower_owner_note_vc_nav_action_receipt_filter_v197_json" in app_text
    assert "_pack_197_owner_note_vc_nav_action_receipt_filter_v197_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-action-receipt-filter-v197.json" in route_text
    assert "_pack_197_owner_note_vc_nav_action_receipt_filter_v197_route_guard" in route_text

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
