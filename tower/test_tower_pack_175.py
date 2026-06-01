
"""
PACK 175 fast test - Owner Note Saved View Preset Detail Drawer / Edit Preview.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_175_payload_ready_and_detail_edit_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_payload(force_refresh=True)

    assert payload["pack_number"] == 175
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-preview.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-compare-navigation-saved-view-filter-preset.json"

    assert payload["simulated_only"] is True
    assert payload["saved_view_preset_detail_preview_only"] is True
    assert payload["saved_view_preset_edit_preview_only"] is True
    assert payload["saved_navigation_preview_only"] is True
    assert payload["saved_filter_preset_preview_only"] is True
    assert payload["navigation_preview_only"] is True
    assert payload["filter_navigation_preview_only"] is True
    assert payload["version_detail_preview_only"] is True
    assert payload["compare_view_preview_only"] is True
    assert payload["version_preview_only"] is True
    assert payload["edit_history_preview_only"] is True
    assert payload["rollback_preview_only"] is True
    assert payload["compare_preview_only"] is True
    assert payload["edit_preview_only"] is True
    assert payload["detail_drawer_preview_only"] is True
    assert payload["owner_note_preview_only"] is True
    assert payload["review_draft_preview_only"] is True
    assert payload["saved_view_preview_only"] is True
    assert payload["filter_preset_preview_only"] is True
    assert payload["filter_preview_only"] is True
    assert payload["search_facet_preview_only"] is True
    assert payload["lookup_preview_only"] is True
    assert payload["detail_preview_only"] is True
    assert payload["evidence_drawer_preview_only"] is True
    assert payload["owner_review_preview_only"] is True
    assert payload["queue_preview_only"] is True
    assert payload["renewal_preview_only"] is True
    assert payload["recheck_preview_only"] is True
    assert payload["expiration_preview_only"] is True
    assert payload["vault_preview_only"] is True
    assert payload["index_preview_only"] is True
    assert payload["receipt_preview_only"] is True
    assert payload["approval_preview_only"] is True
    assert payload["evidence_preview_only"] is True

    assert payload["real_saved_view_written"] is False
    assert payload["real_user_preference_written"] is False
    assert payload["real_filter_preference_saved"] is False
    assert payload["real_navigation_state_persisted"] is False
    assert payload["real_drawer_selection_saved"] is False
    assert payload["real_history_written"] is False
    assert payload["real_version_written"] is False
    assert payload["real_version_saved"] is False
    assert payload["real_rollback_executed"] is False
    assert payload["real_restore_executed"] is False
    assert payload["real_edit_persisted"] is False
    assert payload["real_note_written"] is False
    assert payload["real_draft_saved"] is False
    assert payload["real_approval_executed"] is False
    assert payload["real_policy_change_executed"] is False
    assert payload["real_permission_change_executed"] is False
    assert payload["real_access_granted"] is False
    assert payload["real_enforcement_executed"] is False
    assert payload["real_audit_written"] is False
    assert payload["real_receipt_written"] is False
    assert payload["real_archive_written"] is False
    assert payload["real_vault_written"] is False
    assert payload["real_expiration_enforced"] is False
    assert payload["real_recheck_executed"] is False
    assert payload["real_renewal_executed"] is False
    assert payload["real_queue_action_executed"] is False
    assert payload["real_owner_review_completed"] is False
    assert payload["real_owner_approval_executed"] is False
    assert payload["real_owner_rejection_executed"] is False
    assert payload["real_owner_acknowledgement_executed"] is False
    assert payload["real_evidence_revealed"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["detail_edit_drawer_count"] == 6
    assert summary["source_saved_view_preset_count"] == 6
    assert summary["editable_field_row_count"] == 30
    assert summary["drawer_section_count"] >= 36
    assert summary["editable_field_count"] == 5

    checks = payload["readiness_checks"]
    required_true_checks = [
        "pack_174_ready",
        "has_detail_edit_drawers",
        "drawer_count_matches_presets",
        "all_drawers_ready",
        "all_have_five_editable_fields",
        "all_have_six_drawer_sections",
        "all_have_proposed_update_preview",
        "all_expected_editable_fields_present",
        "all_simulated_only",
        "all_saved_view_preset_detail_preview_only",
        "all_saved_view_preset_edit_preview_only",
        "all_saved_navigation_preview_only",
        "all_saved_filter_preset_preview_only",
        "all_navigation_preview_only",
        "all_filter_navigation_preview_only",
        "all_version_detail_preview_only",
        "all_compare_view_preview_only",
        "all_version_preview_only",
        "all_edit_history_preview_only",
        "all_rollback_preview_only",
        "all_compare_preview_only",
        "all_edit_preview_only",
        "all_detail_drawer_preview_only",
        "all_owner_note_preview_only",
        "all_review_draft_preview_only",
        "all_saved_view_preview_only",
        "all_filter_preset_preview_only",
        "all_filter_preview_only",
        "all_search_facet_preview_only",
        "all_lookup_preview_only",
        "all_detail_preview_only",
        "all_evidence_drawer_preview_only",
        "all_owner_review_preview_only",
        "all_queue_preview_only",
        "all_renewal_preview_only",
        "all_recheck_preview_only",
        "all_expiration_preview_only",
        "all_vault_preview_only",
        "all_index_preview_only",
        "all_receipt_preview_only",
        "all_approval_preview_only",
        "all_evidence_preview_only",
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
        "no_real_note_written",
        "no_real_draft_saved",
        "no_real_approval_executed",
        "no_real_policy_change",
        "no_real_permission_change",
        "no_real_access_granted",
        "no_real_enforcement",
        "no_real_audit_written",
        "no_real_receipt_written",
        "no_real_archive_written",
        "no_real_vault_written",
        "no_real_expiration_enforced",
        "no_real_recheck_executed",
        "no_real_renewal_executed",
        "no_real_queue_action_executed",
        "no_real_owner_review_completed",
        "no_real_owner_approval_executed",
        "no_real_owner_rejection_executed",
        "no_real_owner_acknowledgement_executed",
        "no_real_evidence_revealed",
        "all_save_actions_blocked",
        "all_apply_actions_blocked",
        "all_persist_actions_blocked",
        "all_saved_view_writes_blocked",
        "all_user_preference_writes_blocked",
        "all_filter_preference_saves_blocked",
        "all_navigation_persistence_blocked",
        "all_drawer_selection_saves_blocked",
        "all_raw_evidence_reveal_blocked",
        "all_raw_evidence_lookup_blocked",
        "default_all_compare_drawers_drawer_present",
        "owner_review_focus_drawer_present",
        "critical_priority_focus_drawer_present",
        "high_priority_focus_drawer_present",
        "monitor_only_focus_drawer_present",
        "safe_preview_focus_drawer_present",
        "cached_non_recursive",
    ]

    for key in required_true_checks:
        assert checks[key] is True, key


def test_pack_175_detail_edit_drawers_and_field_rows_are_ready():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_payload(force_refresh=True)

    drawers = payload["detail_edit_drawers"]
    expected_presets = {
        "default_all_compare_drawers",
        "owner_review_focus",
        "critical_priority_focus",
        "high_priority_focus",
        "monitor_only_focus",
        "safe_preview_focus",
    }
    expected_fields = {
        "label",
        "description",
        "filter_lane_id",
        "view_priority",
        "is_default",
    }
    expected_sections = {
        "preset_identity",
        "matched_drawers",
        "editable_fields",
        "proposed_update",
        "blocked_persistence",
        "safety_flags",
    }

    assert len(drawers) == 6
    assert expected_presets.issubset({drawer["saved_view_preset_id"] for drawer in drawers})

    for drawer in drawers:
        assert drawer["saved_view_preset_detail_edit_drawer_id"].startswith("saved_view_preset_detail_edit_drawer_")
        assert drawer["saved_view_preset_id"] in expected_presets
        assert drawer["saved_view_preset_preview_id"].startswith("owner_note_compare_saved_view_preset_")
        assert drawer["label"]
        assert drawer["description"]
        assert drawer["filter_lane_id"]
        assert drawer["view_priority"] in {"critical", "high", "medium", "standard", "monitor"}
        assert isinstance(drawer["is_default"], bool)
        assert drawer["drawer_status"] == "saved_view_preset_detail_edit_preview_ready"
        assert drawer["drawer_result_type"] == "owner_note_saved_view_preset_detail_edit_drawer_preview"

        assert drawer["editable_field_count"] == 5
        field_ids = {row["field_id"] for row in drawer["editable_field_rows"]}
        assert expected_fields.issubset(field_ids)

        for row in drawer["editable_field_rows"]:
            assert row["editable_field_row_id"].startswith("saved_view_preset_editable_field_row_")
            assert row["saved_view_preset_id"] == drawer["saved_view_preset_id"]
            assert row["field_id"] in expected_fields
            assert row["field_label"]
            assert row["field_type"] in {"text", "textarea", "select", "boolean"}
            assert isinstance(row["current_value"], dict)
            assert isinstance(row["proposed_value"], dict)
            assert isinstance(row["changed"], bool)
            assert row["validation"]["valid"] is True
            assert row["row_status"] == "saved_view_preset_editable_field_preview_ready"
            assert row["row_result_type"] == "owner_note_saved_view_preset_editable_field_preview"
            assert row["edit_allowed_in_preview"] is True
            assert row["save_allowed_now"] is False
            assert row["apply_allowed_now"] is False
            assert row["persist_allowed_now"] is False
            assert row["saved_view_write_allowed_now"] is False
            assert row["user_preference_write_allowed_now"] is False
            assert row["real_saved_view_written"] is False
            assert row["real_user_preference_written"] is False
            assert row["real_filter_preference_saved"] is False
            assert row["real_navigation_state_persisted"] is False
            assert row["real_drawer_selection_saved"] is False
            assert row["real_history_written"] is False
            assert row["real_version_written"] is False
            assert row["simulated_only"] is True
            assert row["saved_view_preset_detail_preview_only"] is True
            assert row["saved_view_preset_edit_preview_only"] is True

        update = drawer["proposed_update_preview"]
        assert update["proposed_update_preview_id"].startswith("saved_view_preset_proposed_update_preview_")
        assert update["saved_view_preset_id"] == drawer["saved_view_preset_id"]
        assert update["update_status"] == "saved_view_preset_proposed_update_preview_ready"
        assert update["update_result_type"] == "owner_note_saved_view_preset_proposed_update_preview"
        assert update["validation"]["valid"] is True
        assert update["save_allowed_now"] is False
        assert update["apply_allowed_now"] is False
        assert update["persist_allowed_now"] is False
        assert update["saved_view_write_allowed_now"] is False
        assert update["user_preference_write_allowed_now"] is False
        assert update["filter_preference_save_allowed_now"] is False
        assert update["navigation_persistence_allowed_now"] is False
        assert update["drawer_selection_save_allowed_now"] is False
        assert update["real_saved_view_written"] is False
        assert update["real_user_preference_written"] is False
        assert update["real_filter_preference_saved"] is False
        assert update["real_navigation_state_persisted"] is False
        assert update["real_drawer_selection_saved"] is False

        section_ids = {section["section_id"] for section in drawer["drawer_sections"]}
        assert expected_sections.issubset(section_ids)
        assert drawer["drawer_section_count"] >= 6

        assert drawer["edit_allowed_in_preview"] is True
        assert drawer["preset_detail_allowed_in_preview"] is True
        assert drawer["save_allowed_now"] is False
        assert drawer["apply_allowed_now"] is False
        assert drawer["persist_allowed_now"] is False
        assert drawer["saved_view_write_allowed_now"] is False
        assert drawer["user_preference_write_allowed_now"] is False
        assert drawer["filter_preference_save_allowed_now"] is False
        assert drawer["navigation_persistence_allowed_now"] is False
        assert drawer["drawer_selection_save_allowed_now"] is False
        assert drawer["raw_evidence_reveal_allowed"] is False
        assert drawer["raw_evidence_lookup_allowed"] is False
        assert drawer["real_saved_view_written"] is False
        assert drawer["real_user_preference_written"] is False
        assert drawer["real_history_written"] is False
        assert drawer["real_version_written"] is False


def test_pack_175_indexes_bridge_quick_action_unified_route_and_no_secrets():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_payload(force_refresh=True)

    indexes = payload["detail_edit_indexes"]
    assert indexes["by_detail_edit_drawer_id"]
    assert indexes["by_saved_view_preset_id"]
    assert indexes["by_filter_lane_id"]
    assert indexes["by_view_priority"]
    assert indexes["by_default_state"]
    assert indexes["by_drawer_status"]

    assert "default_all_compare_drawers" in indexes["by_saved_view_preset_id"]
    assert "owner_review_focus" in indexes["by_saved_view_preset_id"]
    assert "critical_priority_focus" in indexes["by_saved_view_preset_id"]
    assert "high_priority_focus" in indexes["by_saved_view_preset_id"]
    assert "monitor_only_focus" in indexes["by_saved_view_preset_id"]
    assert "safe_preview_focus" in indexes["by_saved_view_preset_id"]
    assert "default" in indexes["by_default_state"]
    assert "not_default" in indexes["by_default_state"]
    assert "saved_view_preset_detail_edit_preview_ready" in indexes["by_drawer_status"]

    bridge = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 175
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-preview.json"
    assert bridge["detail_edit_drawer_count"] == 6
    assert bridge["source_saved_view_preset_count"] == 6
    assert bridge["editable_field_row_count"] == 30
    assert bridge["editable_field_count"] == 5
    assert bridge["simulated_only"] is True
    assert bridge["saved_view_preset_detail_preview_only"] is True
    assert bridge["saved_view_preset_edit_preview_only"] is True
    assert bridge["real_saved_view_written"] is False
    assert bridge["real_user_preference_written"] is False
    assert bridge["real_filter_preference_saved"] is False
    assert bridge["real_navigation_state_persisted"] is False
    assert bridge["real_drawer_selection_saved"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-preview.json"
    assert action["status"] == "ready"

    section = mod.build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-preview.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_status_bridge")
    tower_bridge = status.build_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_quick_action")
    assert hasattr(qa, "append_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_quick_action")
    actions = qa.append_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_quick_action([])
    assert any(item.get("id") == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_unified_section")
    assert hasattr(unified, "append_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_section")
    sections = unified.append_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_section([])
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-preview.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_json" in app_text
    assert "_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-preview.json" in route_text
    assert "_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_route_guard" in route_text

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
