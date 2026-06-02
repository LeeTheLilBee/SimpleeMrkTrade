
"""
PACK 190 fast test - Owner Note Saved View Preset Detail Edit History Version Compare
Saved View / Filter Preset Detail Edit History Version Compare Navigation
Saved View / Filter Preset Detail Edit Preview.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_190_payload_ready_and_preview_only():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload(force_refresh=True)

    assert payload["pack_number"] == 190
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-preview.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset.json"

    required_true = [
        "simulated_only",
        "detail_edit_preview_only",
        "saved_view_preview_only",
        "filter_preset_preview_only",
        "navigation_preview_only",
        "filter_navigation_preview_only",
        "version_detail_preview_only",
        "compare_view_preview_only",
        "edit_history_preview_only",
        "version_preview_only",
        "rollback_preview_only",
        "restore_preview_only",
        "compare_preview_only",
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
    assert summary["saved_view_detail_drawer_count"] == 6
    assert summary["filter_preset_detail_drawer_count"] >= 9
    assert summary["total_detail_drawer_count"] >= 15
    assert summary["saved_view_editable_row_count"] == 30
    assert summary["filter_preset_editable_row_count"] >= 45
    assert summary["total_editable_row_count"] >= 75
    assert summary["changed_field_count"] >= 1
    assert summary["unchanged_field_count"] >= 1
    assert summary["saved_view_changed_field_count"] >= 1
    assert summary["filter_preset_changed_field_count"] >= 1

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_189_ready",
        "has_saved_view_presets",
        "has_filter_presets",
        "saved_view_drawer_count_is_six",
        "filter_preset_drawer_count_is_nine",
        "has_detail_edit_drawers",
        "all_saved_view_drawers_ready",
        "all_filter_preset_drawers_ready",
        "all_saved_view_drawers_have_five_rows",
        "all_filter_preset_drawers_have_five_rows",
        "has_editable_rows",
        "has_changed_rows",
        "has_unchanged_rows",
        "saved_view_indexes_present",
        "filter_preset_indexes_present",
        "editable_row_indexes_present",
        "changed_row_indexes_present",
        "all_simulated_only",
        "all_detail_edit_preview_only",
        "all_saved_view_preview_only",
        "all_filter_preset_preview_only",
        "all_navigation_preview_only",
        "all_filter_navigation_preview_only",
        "no_real_saved_view_written",
        "no_real_user_preference_written",
        "no_real_filter_preference_saved",
        "no_real_navigation_state_persisted",
        "no_real_drawer_selection_saved",
        "no_real_edit_persisted",
        "all_saved_view_writes_blocked",
        "all_user_preference_writes_blocked",
        "all_filter_preference_saves_blocked",
        "all_navigation_persistence_blocked",
        "all_drawer_selection_saves_blocked",
        "all_saves_blocked",
        "all_persists_blocked",
        "all_raw_evidence_reveal_blocked",
        "all_raw_evidence_lookup_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_190_saved_view_detail_drawers_and_editable_rows():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload(force_refresh=True)

    drawers = payload["saved_view_detail_edit_drawers"]

    assert len(drawers) == 6

    expected_fields = {"label", "description", "filter_lane_id", "view_priority", "is_default"}

    for drawer in drawers:
        assert drawer["detail_edit_drawer_id"].startswith("version_compare_navigation_saved_view_preset_detail_edit_drawer_")
        assert drawer["source_kind"] == "saved_view_preset"
        assert drawer["source_id"]
        assert drawer["saved_view_preset_id"] == drawer["source_id"]
        assert drawer["saved_view_preset_preview_id"]
        assert drawer["filter_lane_id"]
        assert drawer["linked_filter_preset_id"]
        assert drawer["label"]
        assert drawer["view_priority"] in {"critical", "high", "medium", "monitor"}
        assert isinstance(drawer["is_default"], bool)
        assert drawer["editable_field_row_count"] == 5
        assert drawer["changed_field_count"] >= 0
        assert drawer["unchanged_field_count"] >= 0
        assert drawer["changed_field_count"] + drawer["unchanged_field_count"] == 5
        assert drawer["drawer_status"] == "version_compare_navigation_saved_view_preset_detail_edit_drawer_preview_ready"
        assert drawer["drawer_result_type"] == "owner_note_version_compare_navigation_saved_view_preset_detail_edit_drawer_preview"
        assert drawer["safe_preview_only"] is True

        assert set(drawer["original_snapshot"].keys()) == expected_fields
        assert set(drawer["preview_edit_snapshot"].keys()) == expected_fields

        assert drawer["simulated_only"] is True
        assert drawer["detail_edit_preview_only"] is True
        assert drawer["saved_view_preview_only"] is True
        assert drawer["filter_preset_preview_only"] is True
        assert drawer["navigation_preview_only"] is True
        assert drawer["filter_navigation_preview_only"] is True
        assert drawer["real_saved_view_written"] is False
        assert drawer["real_user_preference_written"] is False
        assert drawer["real_filter_preference_saved"] is False
        assert drawer["real_navigation_state_persisted"] is False
        assert drawer["real_drawer_selection_saved"] is False
        assert drawer["real_edit_persisted"] is False
        assert drawer["saved_view_write_allowed_now"] is False
        assert drawer["user_preference_write_allowed_now"] is False
        assert drawer["filter_preference_save_allowed_now"] is False
        assert drawer["navigation_persistence_allowed_now"] is False
        assert drawer["drawer_selection_save_allowed_now"] is False
        assert drawer["save_allowed_now"] is False
        assert drawer["persist_allowed_now"] is False

        row_fields = {row["field_id"] for row in drawer["editable_field_rows"]}
        assert row_fields == expected_fields

        for row in drawer["editable_field_rows"]:
            assert row["editable_field_row_id"].startswith("version_compare_navigation_saved_view_filter_detail_edit_row_")
            assert row["source_kind"] == "saved_view_preset"
            assert row["source_id"] == drawer["source_id"]
            assert row["drawer_id"] == drawer["detail_edit_drawer_id"]
            assert row["field_id"] in expected_fields
            assert row["field_label"]
            assert row["field_type"] in {"text", "textarea", "select", "boolean"}
            assert row["sequence"] >= 1
            assert isinstance(row["current_value"], dict)
            assert isinstance(row["preview_value"], dict)
            assert "value" in row["current_value"]
            assert "display_value" in row["current_value"]
            assert "value" in row["preview_value"]
            assert "display_value" in row["preview_value"]
            assert isinstance(row["changed"], bool)
            assert row["row_status"] == "version_compare_navigation_saved_view_filter_detail_edit_row_preview_ready"
            assert row["row_result_type"] == "owner_note_version_compare_navigation_saved_view_filter_detail_edit_row_preview"
            assert row["safe_preview_only"] is True

            assert row["simulated_only"] is True
            assert row["detail_edit_preview_only"] is True
            assert row["saved_view_preview_only"] is True
            assert row["filter_preset_preview_only"] is True
            assert row["real_saved_view_written"] is False
            assert row["real_user_preference_written"] is False
            assert row["real_filter_preference_saved"] is False
            assert row["real_navigation_state_persisted"] is False
            assert row["real_drawer_selection_saved"] is False
            assert row["real_edit_persisted"] is False
            assert row["saved_view_write_allowed_now"] is False
            assert row["user_preference_write_allowed_now"] is False
            assert row["filter_preference_save_allowed_now"] is False
            assert row["navigation_persistence_allowed_now"] is False
            assert row["drawer_selection_save_allowed_now"] is False
            assert row["save_allowed_now"] is False
            assert row["persist_allowed_now"] is False


def test_pack_190_filter_preset_detail_drawers_and_editable_rows():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload(force_refresh=True)

    drawers = payload["filter_preset_detail_edit_drawers"]

    assert len(drawers) >= 9

    expected_fields = {"label", "filter_lane_id", "filter_type", "matched_navigation_item_count", "default_selected_version_detail_drawer_id"}

    for drawer in drawers:
        assert drawer["detail_edit_drawer_id"].startswith("version_compare_navigation_filter_preset_detail_edit_drawer_")
        assert drawer["source_kind"] == "filter_preset"
        assert drawer["source_id"]
        assert drawer["filter_preset_id"] == drawer["source_id"]
        assert drawer["filter_lane_id"]
        assert drawer["label"]
        assert drawer["filter_type"] in {"all", "source_kind", "change_state", "blocked_action", "safety"}
        assert drawer["editable_field_row_count"] == 5
        assert drawer["changed_field_count"] >= 0
        assert drawer["unchanged_field_count"] >= 0
        assert drawer["changed_field_count"] + drawer["unchanged_field_count"] == 5
        assert drawer["drawer_status"] == "version_compare_navigation_filter_preset_detail_edit_drawer_preview_ready"
        assert drawer["drawer_result_type"] == "owner_note_version_compare_navigation_filter_preset_detail_edit_drawer_preview"
        assert drawer["safe_preview_only"] is True

        assert set(drawer["original_snapshot"].keys()) == expected_fields
        assert set(drawer["preview_edit_snapshot"].keys()) == expected_fields

        assert drawer["simulated_only"] is True
        assert drawer["detail_edit_preview_only"] is True
        assert drawer["saved_view_preview_only"] is True
        assert drawer["filter_preset_preview_only"] is True
        assert drawer["navigation_preview_only"] is True
        assert drawer["filter_navigation_preview_only"] is True
        assert drawer["real_saved_view_written"] is False
        assert drawer["real_user_preference_written"] is False
        assert drawer["real_filter_preference_saved"] is False
        assert drawer["real_navigation_state_persisted"] is False
        assert drawer["real_drawer_selection_saved"] is False
        assert drawer["real_edit_persisted"] is False
        assert drawer["saved_view_write_allowed_now"] is False
        assert drawer["user_preference_write_allowed_now"] is False
        assert drawer["filter_preference_save_allowed_now"] is False
        assert drawer["navigation_persistence_allowed_now"] is False
        assert drawer["drawer_selection_save_allowed_now"] is False
        assert drawer["save_allowed_now"] is False
        assert drawer["persist_allowed_now"] is False

        row_fields = {row["field_id"] for row in drawer["editable_field_rows"]}
        assert row_fields == expected_fields

        for row in drawer["editable_field_rows"]:
            assert row["editable_field_row_id"].startswith("version_compare_navigation_saved_view_filter_detail_edit_row_")
            assert row["source_kind"] == "filter_preset"
            assert row["source_id"] == drawer["source_id"]
            assert row["drawer_id"] == drawer["detail_edit_drawer_id"]
            assert row["field_id"] in expected_fields
            assert row["field_label"]
            assert row["field_type"] in {"text", "readonly_text", "readonly_number"}
            assert row["sequence"] >= 1
            assert isinstance(row["current_value"], dict)
            assert isinstance(row["preview_value"], dict)
            assert "value" in row["current_value"]
            assert "display_value" in row["current_value"]
            assert "value" in row["preview_value"]
            assert "display_value" in row["preview_value"]
            assert isinstance(row["changed"], bool)
            assert row["row_status"] == "version_compare_navigation_saved_view_filter_detail_edit_row_preview_ready"
            assert row["row_result_type"] == "owner_note_version_compare_navigation_saved_view_filter_detail_edit_row_preview"
            assert row["safe_preview_only"] is True


def test_pack_190_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module(
        "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview"
    )
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload(force_refresh=True)

    indexes = payload["detail_edit_indexes"]

    assert indexes["drawers_by_id"]
    assert indexes["drawers_by_source_kind"]
    assert indexes["drawers_by_source_id"]
    assert indexes["saved_view_drawers_by_preset_id"]
    assert indexes["saved_view_drawers_by_filter_lane_id"]
    assert indexes["saved_view_drawers_by_priority"]
    assert indexes["filter_preset_drawers_by_preset_id"]
    assert indexes["filter_preset_drawers_by_filter_lane_id"]
    assert indexes["editable_rows_by_id"]
    assert indexes["editable_rows_by_drawer_id"]
    assert indexes["editable_rows_by_source_kind"]
    assert indexes["editable_rows_by_field_id"]
    assert indexes["changed_rows_by_drawer_id"]

    assert "saved_view_preset" in indexes["drawers_by_source_kind"]
    assert "filter_preset" in indexes["drawers_by_source_kind"]
    assert "saved_view_preset" in indexes["editable_rows_by_source_kind"]
    assert "filter_preset" in indexes["editable_rows_by_source_kind"]
    assert "label" in indexes["editable_rows_by_field_id"]
    assert "filter_lane_id" in indexes["editable_rows_by_field_id"]

    bridge = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 190
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-preview.json"
    assert bridge["saved_view_detail_drawer_count"] == 6
    assert bridge["filter_preset_detail_drawer_count"] >= 9
    assert bridge["total_detail_drawer_count"] >= 15
    assert bridge["saved_view_editable_row_count"] == 30
    assert bridge["filter_preset_editable_row_count"] >= 45
    assert bridge["total_editable_row_count"] >= 75
    assert bridge["changed_field_count"] >= 1
    assert bridge["unchanged_field_count"] >= 1
    assert bridge["saved_view_changed_field_count"] >= 1
    assert bridge["filter_preset_changed_field_count"] >= 1

    action = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-preview.json"
    assert action["status"] == "ready"

    section = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-preview.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_190_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_status_bridge")
    tower_bridge = status.build_pack_190_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_190_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_quick_action")
    assert hasattr(qa, "append_pack_190_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_quick_action")
    actions = qa.append_pack_190_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_quick_action([])
    assert any(item.get("id") == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_190_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_unified_section")
    assert hasattr(unified, "append_pack_190_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_section")
    sections = unified.append_pack_190_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_section([])
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-preview.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_json" in app_text
    assert "_pack_190_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-preview.json" in route_text
    assert "_pack_190_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_route_guard" in route_text

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
