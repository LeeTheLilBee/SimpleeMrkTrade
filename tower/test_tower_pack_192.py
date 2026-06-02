
"""
PACK 192 fast test - Owner Note Version Compare Navigation Saved View /
Filter Preset Detail Edit History Version Detail / Compare View Preview.

Uses short safe module:
    tower.owner_note_vc_nav_version_compare_v192
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_192_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.owner_note_vc_nav_version_compare_v192")
    payload = mod.build_owner_note_vc_nav_version_compare_v192_payload(force_refresh=True)

    assert payload["pack_number"] == 192
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/owner-note-vc-nav-version-compare-v192.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-history-version-preview.json"

    required_true = [
        "simulated_only",
        "version_detail_preview_only",
        "compare_view_preview_only",
        "version_preview_only",
        "edit_history_preview_only",
        "rollback_preview_only",
        "restore_preview_only",
        "compare_preview_only",
        "detail_edit_preview_only",
        "saved_view_preview_only",
        "filter_preset_preview_only",
        "navigation_preview_only",
        "filter_navigation_preview_only",
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
        "real_raw_evidence_revealed",
    ]

    for key in required_false:
        assert payload[key] is False, key

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["version_detail_drawer_count"] >= 15
    assert summary["saved_view_version_detail_drawer_count"] == 6
    assert summary["filter_preset_version_detail_drawer_count"] >= 9
    assert summary["comparison_row_count"] >= 75
    assert summary["changed_compare_row_count"] >= 1
    assert summary["unchanged_compare_row_count"] >= 1
    assert summary["selected_version_detail_drawer_id"]

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_191_ready",
        "has_timelines",
        "has_version_detail_drawers",
        "has_saved_view_version_detail_drawers",
        "has_filter_preset_version_detail_drawers",
        "version_detail_drawer_count_matches_timelines",
        "all_version_detail_drawers_ready",
        "all_version_detail_drawers_have_compare_rows",
        "has_compare_rows",
        "has_changed_compare_rows",
        "has_unchanged_compare_rows",
        "selected_version_detail_preview_ready",
        "version_detail_indexes_present",
        "compare_row_indexes_present",
        "changed_compare_row_indexes_present",
        "all_simulated_only",
        "all_version_detail_preview_only",
        "all_compare_view_preview_only",
        "all_version_preview_only",
        "all_edit_history_preview_only",
        "all_detail_edit_preview_only",
        "no_real_history_written",
        "no_real_version_written",
        "no_real_version_saved",
        "no_real_rollback_executed",
        "no_real_restore_executed",
        "no_real_edit_persisted",
        "no_real_raw_evidence_revealed",
        "all_raw_evidence_reveal_blocked",
        "all_raw_evidence_lookup_blocked",
        "all_version_writes_blocked",
        "all_version_saves_blocked",
        "all_rollback_actions_blocked",
        "all_restore_actions_blocked",
        "all_saves_blocked",
        "all_persists_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_192_version_detail_drawers_and_compare_rows():
    mod = importlib.import_module("tower.owner_note_vc_nav_version_compare_v192")
    payload = mod.build_owner_note_vc_nav_version_compare_v192_payload(force_refresh=True)

    drawers = payload["version_detail_drawers"]

    assert len(drawers) >= 15

    saved_view_drawers = [item for item in drawers if item["source_kind"] == "saved_view_preset"]
    filter_preset_drawers = [item for item in drawers if item["source_kind"] == "filter_preset"]

    assert len(saved_view_drawers) == 6
    assert len(filter_preset_drawers) >= 9

    for drawer in drawers:
        assert drawer["version_detail_drawer_id"].startswith("version_compare_navigation_version_detail_drawer_")
        assert drawer["edit_history_timeline_id"]
        assert drawer["detail_edit_drawer_id"]
        assert drawer["source_kind"] in {"saved_view_preset", "filter_preset"}
        assert drawer["source_id"]
        assert drawer["sequence"] >= 1
        assert drawer["original_version_card_id"]
        assert drawer["draft_preview_version_card_id"]
        assert drawer["compare_preview_version_card_id"]
        assert drawer["active_version_card_id"]
        assert isinstance(drawer["original_snapshot"], dict)
        assert isinstance(drawer["draft_preview_snapshot"], dict)
        assert isinstance(drawer["compare_rows"], list)
        assert drawer["comparison_row_count"] >= 1
        assert len(drawer["compare_rows"]) == drawer["comparison_row_count"]
        assert drawer["changed_compare_row_count"] >= 0
        assert drawer["unchanged_compare_row_count"] >= 0
        assert drawer["changed_compare_row_count"] + drawer["unchanged_compare_row_count"] == drawer["comparison_row_count"]
        assert isinstance(drawer["rollback_preview"], dict)
        assert isinstance(drawer["restore_preview"], dict)
        assert isinstance(drawer["compare_preview"], dict)
        assert drawer["drawer_status"] == "version_compare_navigation_version_detail_drawer_preview_ready"
        assert drawer["drawer_result_type"] == "owner_note_version_compare_navigation_version_detail_drawer_preview"
        assert drawer["open_allowed_in_preview"] is True
        assert drawer["selection_allowed_in_preview"] is True
        assert drawer["safe_preview_only"] is True

        assert drawer["simulated_only"] is True
        assert drawer["version_detail_preview_only"] is True
        assert drawer["compare_view_preview_only"] is True
        assert drawer["version_preview_only"] is True
        assert drawer["edit_history_preview_only"] is True
        assert drawer["detail_edit_preview_only"] is True
        assert drawer["real_history_written"] is False
        assert drawer["real_version_written"] is False
        assert drawer["real_version_saved"] is False
        assert drawer["real_rollback_executed"] is False
        assert drawer["real_restore_executed"] is False
        assert drawer["real_edit_persisted"] is False
        assert drawer["real_raw_evidence_revealed"] is False
        assert drawer["raw_evidence_reveal_allowed"] is False
        assert drawer["raw_evidence_lookup_allowed"] is False
        assert drawer["version_write_allowed_now"] is False
        assert drawer["version_save_allowed_now"] is False
        assert drawer["rollback_allowed_now"] is False
        assert drawer["restore_allowed_now"] is False
        assert drawer["save_allowed_now"] is False
        assert drawer["persist_allowed_now"] is False

        for row in drawer["compare_rows"]:
            assert row["compare_row_id"].startswith("version_compare_navigation_detail_compare_row_")
            assert row["edit_history_timeline_id"] == drawer["edit_history_timeline_id"]
            assert row["detail_edit_drawer_id"] == drawer["detail_edit_drawer_id"]
            assert row["source_kind"] == drawer["source_kind"]
            assert row["source_id"] == drawer["source_id"]
            assert row["field_id"]
            assert row["field_label"]
            assert row["sequence"] >= 1
            assert "original_value" in row
            assert "draft_preview_value" in row
            assert "original_display_value" in row
            assert "draft_preview_display_value" in row
            assert isinstance(row["changed"], bool)
            assert row["change_status"] in {"changed_preview", "unchanged_preview"}
            assert row["row_status"] == "version_compare_navigation_version_detail_compare_row_preview_ready"
            assert row["row_result_type"] == "owner_note_version_compare_navigation_version_detail_compare_row_preview"
            assert row["safe_preview_only"] is True

            assert row["simulated_only"] is True
            assert row["version_detail_preview_only"] is True
            assert row["compare_view_preview_only"] is True
            assert row["version_preview_only"] is True
            assert row["edit_history_preview_only"] is True
            assert row["real_history_written"] is False
            assert row["real_version_written"] is False
            assert row["real_version_saved"] is False
            assert row["real_rollback_executed"] is False
            assert row["real_restore_executed"] is False
            assert row["real_edit_persisted"] is False
            assert row["real_raw_evidence_revealed"] is False
            assert row["raw_evidence_reveal_allowed"] is False
            assert row["raw_evidence_lookup_allowed"] is False
            assert row["version_write_allowed_now"] is False
            assert row["version_save_allowed_now"] is False
            assert row["rollback_allowed_now"] is False
            assert row["restore_allowed_now"] is False
            assert row["save_allowed_now"] is False
            assert row["persist_allowed_now"] is False


def test_pack_192_selected_preview_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.owner_note_vc_nav_version_compare_v192")
    payload = mod.build_owner_note_vc_nav_version_compare_v192_payload(force_refresh=True)

    selected = payload["selected_version_detail_preview"]
    assert selected["selected_version_detail_preview_id"].startswith("version_compare_navigation_selected_version_detail_")
    assert selected["selected_version_detail_drawer_id"]
    assert selected["selected_edit_history_timeline_id"]
    assert selected["selected_detail_edit_drawer_id"]
    assert selected["selected_source_kind"] in {"saved_view_preset", "filter_preset"}
    assert selected["selected_source_id"]
    assert selected["selected_comparison_row_count"] >= 1
    assert selected["selection_status"] == "version_compare_navigation_selected_version_detail_preview_ready"
    assert selected["selection_result_type"] == "owner_note_version_compare_navigation_selected_version_detail_preview"
    assert selected["open_allowed_in_preview"] is True
    assert selected["selection_allowed_in_preview"] is True
    assert selected["safe_preview_only"] is True
    assert selected["raw_evidence_reveal_allowed"] is False
    assert selected["raw_evidence_lookup_allowed"] is False
    assert selected["real_raw_evidence_revealed"] is False

    indexes = payload["version_detail_compare_indexes"]

    assert indexes["version_detail_drawers_by_id"]
    assert indexes["version_detail_drawers_by_timeline_id"]
    assert indexes["version_detail_drawers_by_detail_edit_drawer_id"]
    assert indexes["version_detail_drawers_by_source_kind"]
    assert indexes["version_detail_drawers_by_source_id"]
    assert indexes["compare_rows_by_id"]
    assert indexes["compare_rows_by_version_detail_drawer_id"]
    assert indexes["compare_rows_by_timeline_id"]
    assert indexes["compare_rows_by_source_kind"]
    assert indexes["compare_rows_by_field_id"]
    assert indexes["changed_compare_rows_by_drawer_id"]
    assert indexes["unchanged_compare_rows_by_drawer_id"]

    assert "saved_view_preset" in indexes["version_detail_drawers_by_source_kind"]
    assert "filter_preset" in indexes["version_detail_drawers_by_source_kind"]
    assert "saved_view_preset" in indexes["compare_rows_by_source_kind"]
    assert "filter_preset" in indexes["compare_rows_by_source_kind"]

    bridge = mod.build_owner_note_vc_nav_version_compare_v192_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 192
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/owner-note-vc-nav-version-compare-v192.json"
    assert bridge["version_detail_drawer_count"] >= 15
    assert bridge["saved_view_version_detail_drawer_count"] == 6
    assert bridge["filter_preset_version_detail_drawer_count"] >= 9
    assert bridge["comparison_row_count"] >= 75
    assert bridge["changed_compare_row_count"] >= 1
    assert bridge["unchanged_compare_row_count"] >= 1
    assert bridge["selected_version_detail_drawer_id"]

    action = mod.build_owner_note_vc_nav_version_compare_v192_quick_action()
    assert action["id"] == "owner_note_vc_nav_version_compare_v192"
    assert action["href"] == "/tower/owner-note-vc-nav-version-compare-v192.json"
    assert action["status"] == "ready"

    section = mod.build_owner_note_vc_nav_version_compare_v192_unified_owner_section()
    assert section["section_id"] == "owner_note_vc_nav_version_compare_v192"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/owner-note-vc-nav-version-compare-v192.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_192_owner_note_vc_nav_version_compare_v192_status_bridge")
    tower_bridge = status.build_pack_192_owner_note_vc_nav_version_compare_v192_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_192_owner_note_vc_nav_version_compare_v192_quick_action")
    assert hasattr(qa, "append_pack_192_owner_note_vc_nav_version_compare_v192_quick_action")
    actions = qa.append_pack_192_owner_note_vc_nav_version_compare_v192_quick_action([])
    assert any(item.get("id") == "owner_note_vc_nav_version_compare_v192" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_192_owner_note_vc_nav_version_compare_v192_unified_section")
    assert hasattr(unified, "append_pack_192_owner_note_vc_nav_version_compare_v192_section")
    sections = unified.append_pack_192_owner_note_vc_nav_version_compare_v192_section([])
    assert any(item.get("section_id") == "owner_note_vc_nav_version_compare_v192" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-version-compare-v192.json" in app_text
    assert "tower_owner_note_vc_nav_version_compare_v192_json" in app_text
    assert "_pack_192_owner_note_vc_nav_version_compare_v192_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-version-compare-v192.json" in route_text
    assert "_pack_192_owner_note_vc_nav_version_compare_v192_route_guard" in route_text

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
