
"""
PACK 173 fast test - Owner Note Draft Version Compare Filter / Drawer Navigation Preview.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_173_payload_ready_and_navigation_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload(force_refresh=True)

    assert payload["pack_number"] == 173
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-version-compare-filter-navigation.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json"

    assert payload["simulated_only"] is True
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

    assert payload["real_navigation_state_persisted"] is False
    assert payload["real_filter_preference_saved"] is False
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
    assert payload["real_saved_view_written"] is False
    assert payload["real_user_preference_written"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["navigation_item_count"] >= 8
    assert summary["version_detail_drawer_count"] >= 8
    assert summary["filter_lane_count"] >= 8
    assert summary["quick_filter_chip_count"] == 6
    assert summary["group_count"] >= 1
    assert summary["default_filter_lane_id"] == "all_compare_drawers"
    assert summary["default_selected_drawer_id"]

    checks = payload["readiness_checks"]
    required_true_checks = [
        "pack_172_ready",
        "has_drawers",
        "has_navigation_items",
        "navigation_count_matches_drawers",
        "has_filter_lanes",
        "has_quick_filter_chips",
        "has_grouped_navigation",
        "all_simulated_only",
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
        "no_real_navigation_state_persisted",
        "no_real_filter_preference_saved",
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
        "no_real_saved_view_written",
        "no_real_user_preference_written",
        "all_navigation_persistence_blocked",
        "all_filter_preference_save_blocked",
        "all_drawer_selection_save_blocked",
        "all_restore_actions_blocked",
        "all_rollback_actions_blocked",
        "all_save_actions_blocked",
        "all_submit_actions_blocked",
        "all_raw_evidence_reveal_blocked",
        "all_raw_evidence_lookup_blocked",
        "all_navigation_item_ids_present",
        "all_drawer_ids_present",
        "all_owner_note_draft_ids_present",
        "all_saved_view_ids_present",
        "all_navigation_items_ready",
        "navigation_preview_ready",
        "selected_drawer_preview_ready",
        "filter_lanes_ready",
        "quick_filter_chips_ready",
        "grouped_navigation_ready",
        "all_expected_filter_lanes_present",
        "all_quick_filters_present",
        "all_compare_drawers_filter_present",
        "owner_review_required_filter_present",
        "critical_priority_filter_present",
        "high_priority_filter_present",
        "monitor_priority_filter_present",
        "safe_preview_only_filter_present",
        "has_previous_next_pointers",
        "cached_non_recursive",
    ]

    for key in required_true_checks:
        assert checks[key] is True, key


def test_pack_173_navigation_items_filters_and_indexes():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload(force_refresh=True)

    nav = payload["navigation_preview"]
    items = nav["navigation_items"]

    assert nav["navigation_status"] == "drawer_navigation_preview_ready"
    assert nav["navigation_item_count"] == len(items)
    assert nav["default_selected_navigation_item_id"]
    assert nav["default_selected_drawer_id"]
    assert nav["real_navigation_state_persisted"] is False

    selected = nav["selected_drawer_preview"]
    assert selected["selection_status"] == "selected_drawer_preview_ready"
    assert selected["selection_result_type"] == "owner_note_version_compare_selected_drawer_preview"
    assert selected["real_navigation_state_persisted"] is False
    assert selected["real_filter_preference_saved"] is False
    assert selected["real_drawer_selection_saved"] is False

    assert items[0]["has_previous"] is False
    assert items[0]["has_next"] is True
    assert items[-1]["has_next"] is False
    assert items[-1]["has_previous"] is True

    for item in items:
        assert item["navigation_item_id"].startswith("version_compare_drawer_nav_item_")
        assert item["version_detail_drawer_id"].startswith("owner_note_draft_version_detail_compare_drawer_")
        assert item["owner_note_draft_id"].startswith("evidence_drawer_owner_note_draft_")
        assert item["saved_view_id"]
        assert item["draft_priority"] in {"critical", "high", "medium", "standard", "monitor"}
        assert item["navigation_status"] == "drawer_navigation_item_preview_ready"
        assert item["comparison_row_count"] == 5
        assert item["changed_field_count"] == 5
        assert item["unchanged_field_count"] == 0
        assert item["navigation_persistence_allowed_now"] is False
        assert item["filter_preference_save_allowed_now"] is False
        assert item["drawer_selection_save_allowed_now"] is False
        assert item["real_navigation_state_persisted"] is False
        assert item["real_filter_preference_saved"] is False
        assert item["real_drawer_selection_saved"] is False
        assert item["raw_evidence_reveal_allowed"] is False

    lanes_payload = payload["filter_lanes_preview"]
    chips_payload = payload["quick_filter_chips_preview"]
    grouped = payload["grouped_navigation_preview"]
    indexes = payload["navigation_indexes"]

    expected_lanes = {
        "all_compare_drawers",
        "owner_review_required",
        "owner_review_not_required",
        "critical_priority",
        "high_priority",
        "medium_priority",
        "monitor_priority",
        "safe_preview_only",
    }

    expected_quick = {
        "all_compare_drawers",
        "owner_review_required",
        "critical_priority",
        "high_priority",
        "monitor_priority",
        "safe_preview_only",
    }

    assert lanes_payload["filter_status"] == "filter_lanes_preview_ready"
    assert lanes_payload["filter_lane_count"] >= 8
    assert lanes_payload["default_filter_lane_id"] == "all_compare_drawers"
    assert expected_lanes.issubset(set(lanes_payload["filter_lane_index"].keys()))
    assert lanes_payload["filter_lane_index"]["all_compare_drawers"]["matched_drawer_count"] == payload["summary"]["version_detail_drawer_count"]
    assert lanes_payload["filter_lane_index"]["safe_preview_only"]["matched_drawer_count"] >= 1
    assert lanes_payload["real_filter_preference_saved"] is False

    for lane in lanes_payload["filter_lanes"]:
        assert lane["filter_lane_preview_id"].startswith("version_compare_filter_lane_")
        assert lane["lane_status"] == "filter_lane_preview_ready"
        assert lane["filter_preference_save_allowed_now"] is False
        assert lane["real_filter_preference_saved"] is False

    assert chips_payload["quick_filter_status"] == "quick_filter_chips_preview_ready"
    assert chips_payload["quick_filter_chip_count"] == 6
    assert expected_quick.issubset(set(chips_payload["quick_filter_ids"]))
    assert chips_payload["real_filter_preference_saved"] is False

    for chip in chips_payload["quick_filter_chips"]:
        assert chip["quick_filter_chip_id"].startswith("version_compare_quick_filter_chip_")
        assert chip["chip_status"] == "quick_filter_chip_preview_ready"
        assert chip["filter_preference_save_allowed_now"] is False

    assert grouped["grouped_navigation_status"] == "grouped_navigation_preview_ready"
    assert grouped["group_count"] >= 1
    assert grouped["real_navigation_state_persisted"] is False

    assert indexes["by_navigation_item_id"]
    assert indexes["by_version_detail_drawer_id"]
    assert indexes["by_owner_note_draft_id"]
    assert indexes["by_saved_view_id"]
    assert indexes["by_draft_type"]
    assert indexes["by_draft_priority"]
    assert indexes["by_requires_owner_review"]
    assert indexes["by_filter_lane_id"]
    assert "all_compare_drawers" in indexes["by_filter_lane_id"]
    assert "owner_review_required" in indexes["by_filter_lane_id"]
    assert "safe_preview_only" in indexes["by_filter_lane_id"]


def test_pack_173_bridge_quick_action_unified_route_and_no_secrets():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation")

    bridge = mod.build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 173
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-version-compare-filter-navigation.json"
    assert bridge["navigation_item_count"] >= 8
    assert bridge["filter_lane_count"] >= 8
    assert bridge["quick_filter_chip_count"] == 6
    assert bridge["real_navigation_state_persisted"] is False
    assert bridge["real_filter_preference_saved"] is False
    assert bridge["real_drawer_selection_saved"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-version-compare-filter-navigation.json"
    assert action["status"] == "ready"

    section = mod.build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-version-compare-filter-navigation.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_status_bridge")
    tower_bridge = status.build_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_quick_action")
    assert hasattr(qa, "append_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_quick_action")
    actions = qa.append_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_quick_action([])
    assert any(item.get("id") == "policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_unified_section")
    assert hasattr(unified, "append_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_section")
    sections = unified.append_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_section([])
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-draft-version-compare-filter-navigation.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_json" in app_text
    assert "_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-draft-version-compare-filter-navigation.json" in route_text
    assert "_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_route_guard" in route_text

    payload_text = str(mod.build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload(force_refresh=True)).lower()
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
