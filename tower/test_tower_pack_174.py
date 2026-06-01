
"""
PACK 174 fast test - Owner Note Compare Navigation Saved View / Filter Preset Preview.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_174_payload_ready_and_saved_view_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset")
    payload = mod.build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload(force_refresh=True)

    assert payload["pack_number"] == 174
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-compare-navigation-saved-view-filter-preset.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-version-compare-filter-navigation.json"

    assert payload["simulated_only"] is True
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
    assert summary["saved_view_preset_count"] == 6
    assert summary["preset_chip_count"] == 6
    assert summary["preset_detail_count"] == 6
    assert summary["default_saved_view_preset_id"] == "default_all_compare_drawers"
    assert summary["default_filter_lane_id"] == "all_compare_drawers"

    checks = payload["readiness_checks"]
    required_true_checks = [
        "pack_173_ready",
        "has_saved_view_presets",
        "has_preset_chips",
        "has_default_saved_view_selection",
        "has_preset_detail_previews",
        "all_expected_presets_present",
        "all_presets_ready",
        "all_preset_chips_ready",
        "all_preset_details_ready",
        "default_selection_ready",
        "all_simulated_only",
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
        "all_saved_view_writes_blocked",
        "all_user_preference_writes_blocked",
        "all_filter_preference_saves_blocked",
        "all_navigation_persistence_blocked",
        "all_drawer_selection_saves_blocked",
        "all_raw_evidence_reveal_blocked",
        "all_raw_evidence_lookup_blocked",
        "default_all_compare_drawers_present",
        "owner_review_focus_present",
        "critical_priority_focus_present",
        "high_priority_focus_present",
        "monitor_only_focus_present",
        "safe_preview_focus_present",
        "exactly_one_default_preset",
        "cached_non_recursive",
    ]

    for key in required_true_checks:
        assert checks[key] is True, key


def test_pack_174_presets_chips_details_and_indexes():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset")
    payload = mod.build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload(force_refresh=True)

    presets = payload["saved_view_presets"]
    chips_payload = payload["preset_chips_preview"]
    details_payload = payload["preset_detail_previews"]
    default_selection = payload["default_saved_view_selection"]
    indexes = payload["saved_view_indexes"]

    expected_presets = {
        "default_all_compare_drawers",
        "owner_review_focus",
        "critical_priority_focus",
        "high_priority_focus",
        "monitor_only_focus",
        "safe_preview_focus",
    }

    assert len(presets) == 6
    assert expected_presets.issubset({preset["saved_view_preset_id"] for preset in presets})

    default_presets = [preset for preset in presets if preset["is_default"] is True]
    assert len(default_presets) == 1
    assert default_presets[0]["saved_view_preset_id"] == "default_all_compare_drawers"
    assert default_presets[0]["filter_lane_id"] == "all_compare_drawers"

    for preset in presets:
        assert preset["saved_view_preset_preview_id"].startswith("owner_note_compare_saved_view_preset_")
        assert preset["label"]
        assert preset["description"]
        assert preset["filter_lane_id"]
        assert preset["view_priority"] in {"critical", "high", "medium", "standard", "monitor"}
        assert preset["matched_drawer_count"] >= 0
        assert isinstance(preset["matched_version_detail_drawer_ids"], list)
        assert preset["preset_status"] == "saved_view_filter_preset_preview_ready"
        assert preset["preset_result_type"] == "owner_note_compare_navigation_saved_view_filter_preset_preview"
        assert preset["filter_allowed_in_preview"] is True
        assert preset["selection_allowed_in_preview"] is True
        assert preset["preset_detail_allowed_in_preview"] is True
        assert preset["saved_view_write_allowed_now"] is False
        assert preset["filter_preference_save_allowed_now"] is False
        assert preset["navigation_persistence_allowed_now"] is False
        assert preset["drawer_selection_save_allowed_now"] is False
        assert preset["user_preference_write_allowed_now"] is False
        assert preset["real_saved_view_written"] is False
        assert preset["real_user_preference_written"] is False
        assert preset["real_filter_preference_saved"] is False
        assert preset["real_navigation_state_persisted"] is False
        assert preset["real_drawer_selection_saved"] is False
        assert preset["raw_evidence_reveal_allowed"] is False
        assert preset["raw_evidence_lookup_allowed"] is False
        assert preset["simulated_only"] is True
        assert preset["saved_navigation_preview_only"] is True
        assert preset["saved_filter_preset_preview_only"] is True

    assert chips_payload["chips_status"] == "saved_view_preset_chips_preview_ready"
    assert chips_payload["chips_result_type"] == "owner_note_compare_saved_view_preset_chips_preview"
    assert chips_payload["preset_chip_count"] == 6
    assert expected_presets.issubset(set(chips_payload["preset_ids"]))
    assert chips_payload["default_preset_chip_id"]
    assert chips_payload["real_saved_view_written"] is False
    assert chips_payload["real_filter_preference_saved"] is False
    assert chips_payload["real_user_preference_written"] is False

    for chip in chips_payload["preset_chips"]:
        assert chip["preset_chip_id"].startswith("owner_note_compare_preset_chip_")
        assert chip["saved_view_preset_id"] in expected_presets
        assert chip["label"]
        assert chip["order"] >= 1
        assert chip["chip_status"] == "saved_view_preset_chip_preview_ready"
        assert chip["chip_result_type"] == "owner_note_compare_saved_view_preset_chip_preview"
        assert chip["saved_view_write_allowed_now"] is False
        assert chip["filter_preference_save_allowed_now"] is False
        assert chip["user_preference_write_allowed_now"] is False
        assert chip["real_saved_view_written"] is False
        assert chip["real_filter_preference_saved"] is False
        assert chip["real_user_preference_written"] is False

    assert default_selection["default_saved_view_selection_id"].startswith("owner_note_compare_default_saved_view_selection_")
    assert default_selection["default_saved_view_preset_id"] == "default_all_compare_drawers"
    assert default_selection["default_filter_lane_id"] == "all_compare_drawers"
    assert default_selection["selection_status"] == "default_saved_view_selection_preview_ready"
    assert default_selection["selection_result_type"] == "owner_note_compare_default_saved_view_selection_preview"
    assert default_selection["saved_view_write_allowed_now"] is False
    assert default_selection["filter_preference_save_allowed_now"] is False
    assert default_selection["navigation_persistence_allowed_now"] is False
    assert default_selection["drawer_selection_save_allowed_now"] is False
    assert default_selection["user_preference_write_allowed_now"] is False
    assert default_selection["real_saved_view_written"] is False
    assert default_selection["real_user_preference_written"] is False
    assert default_selection["real_filter_preference_saved"] is False
    assert default_selection["real_navigation_state_persisted"] is False
    assert default_selection["real_drawer_selection_saved"] is False

    assert details_payload["details_status"] == "saved_view_preset_detail_previews_ready"
    assert details_payload["preset_detail_count"] == 6
    assert expected_presets.issubset(set(details_payload["preset_detail_index"].keys()))
    assert details_payload["real_saved_view_written"] is False
    assert details_payload["real_user_preference_written"] is False

    for detail in details_payload["preset_detail_previews"]:
        assert detail["preset_detail_preview_id"].startswith("owner_note_compare_preset_detail_preview_")
        assert detail["saved_view_preset_id"] in expected_presets
        assert detail["detail_status"] == "saved_view_preset_detail_preview_ready"
        assert detail["detail_result_type"] == "owner_note_compare_saved_view_preset_detail_preview"
        assert detail["detail_section_count"] == 4
        assert detail["preset_detail_allowed_in_preview"] is True
        assert detail["saved_view_write_allowed_now"] is False
        assert detail["filter_preference_save_allowed_now"] is False
        assert detail["navigation_persistence_allowed_now"] is False
        assert detail["drawer_selection_save_allowed_now"] is False
        assert detail["user_preference_write_allowed_now"] is False
        assert detail["real_saved_view_written"] is False
        assert detail["real_user_preference_written"] is False
        assert detail["real_filter_preference_saved"] is False
        assert detail["real_navigation_state_persisted"] is False
        assert detail["real_drawer_selection_saved"] is False

    assert indexes["by_saved_view_preset_id"]
    assert indexes["by_filter_lane_id"]
    assert indexes["by_view_priority"]
    assert indexes["by_default_state"]
    assert indexes["by_preset_detail_id"]
    assert "default_all_compare_drawers" in indexes["by_saved_view_preset_id"]
    assert "owner_review_focus" in indexes["by_saved_view_preset_id"]
    assert "all_compare_drawers" in indexes["by_filter_lane_id"]
    assert "default" in indexes["by_default_state"]
    assert "not_default" in indexes["by_default_state"]


def test_pack_174_bridge_quick_action_unified_route_and_no_secrets():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset")

    bridge = mod.build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 174
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-compare-navigation-saved-view-filter-preset.json"
    assert bridge["saved_view_preset_count"] == 6
    assert bridge["preset_chip_count"] == 6
    assert bridge["preset_detail_count"] == 6
    assert bridge["default_saved_view_preset_id"] == "default_all_compare_drawers"
    assert bridge["default_filter_lane_id"] == "all_compare_drawers"
    assert bridge["simulated_only"] is True
    assert bridge["saved_navigation_preview_only"] is True
    assert bridge["saved_filter_preset_preview_only"] is True
    assert bridge["real_saved_view_written"] is False
    assert bridge["real_user_preference_written"] is False
    assert bridge["real_filter_preference_saved"] is False
    assert bridge["real_navigation_state_persisted"] is False
    assert bridge["real_drawer_selection_saved"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-compare-navigation-saved-view-filter-preset.json"
    assert action["status"] == "ready"

    section = mod.build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-compare-navigation-saved-view-filter-preset.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_status_bridge")
    tower_bridge = status.build_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_quick_action")
    assert hasattr(qa, "append_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_quick_action")
    actions = qa.append_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_quick_action([])
    assert any(item.get("id") == "policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_unified_section")
    assert hasattr(unified, "append_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_section")
    sections = unified.append_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_section([])
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-compare-navigation-saved-view-filter-preset.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_json" in app_text
    assert "_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-compare-navigation-saved-view-filter-preset.json" in route_text
    assert "_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_route_guard" in route_text

    payload_text = str(mod.build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload(force_refresh=True)).lower()
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
