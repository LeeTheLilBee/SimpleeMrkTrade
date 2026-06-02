
"""
PACK 196 fast test - Owner Note Version Compare Navigation Focus Action
Result / Blocked Action Receipt Preview.

Uses short safe module:
    tower.owner_note_vc_nav_focus_action_receipts_v196
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_196_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.owner_note_vc_nav_focus_action_receipts_v196")
    payload = mod.build_owner_note_vc_nav_focus_action_receipts_v196_payload(force_refresh=True)

    assert payload["pack_number"] == 196
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/owner-note-vc-nav-focus-action-receipts-v196.json"
    assert payload["source_endpoint"] == "/tower/owner-note-vc-nav-drawer-focus-v195.json"

    required_true = [
        "simulated_only",
        "action_receipt_preview_only",
        "blocked_action_receipt_preview_only",
        "preview_action_receipt_preview_only",
        "drawer_action_preview_only",
        "selected_drawer_preview_only",
        "compare_row_focus_preview_only",
        "navigation_preview_only",
        "filter_navigation_preview_only",
        "drawer_selection_preview_only",
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
    assert summary["action_receipt_count"] == 5
    assert summary["preview_action_receipt_count"] == 3
    assert summary["blocked_action_receipt_count"] == 2
    assert summary["action_receipt_group_count"] == 3
    assert summary["selected_action_receipt_preview_count"] == 1
    assert summary["real_action_executed_count"] == 0
    assert summary["raw_evidence_revealed_count"] == 0
    assert summary["persistence_write_count"] == 0
    assert summary["selected_action_receipt_id"]
    assert summary["selected_version_detail_drawer_id"]

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_195_ready",
        "has_selected_drawer_focus",
        "has_drawer_action_panel",
        "has_action_receipts",
        "has_preview_action_receipts",
        "has_blocked_action_receipts",
        "all_action_receipts_ready",
        "blocked_receipts_are_blocked",
        "preview_receipts_do_not_execute_real_actions",
        "safety_summary_ready",
        "has_receipt_groups",
        "all_receipt_groups_ready",
        "selected_action_receipt_preview_ready",
        "receipt_indexes_present",
        "receipt_group_indexes_present",
        "selected_receipt_index_present",
        "all_simulated_only",
        "all_action_receipt_preview_only",
        "all_drawer_action_preview_only",
        "all_selected_drawer_preview_only",
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


def test_pack_196_action_receipts_safety_summary_and_groups():
    mod = importlib.import_module("tower.owner_note_vc_nav_focus_action_receipts_v196")
    payload = mod.build_owner_note_vc_nav_focus_action_receipts_v196_payload(force_refresh=True)

    receipts = payload["action_receipts"]
    groups = payload["action_receipt_groups"]
    safety = payload["action_safety_summary"]

    assert len(receipts) == 5

    action_ids = {receipt["action_id"] for receipt in receipts}
    assert action_ids == {
        "preview_open_drawer",
        "preview_filter_changed_rows",
        "preview_filter_unchanged_rows",
        "blocked_save_selection",
        "blocked_reveal_raw_evidence",
    }

    preview_receipts = [receipt for receipt in receipts if receipt["blocked_in_preview"] is False]
    blocked_receipts = [receipt for receipt in receipts if receipt["blocked_in_preview"] is True]

    assert len(preview_receipts) == 3
    assert len(blocked_receipts) == 2

    for receipt in receipts:
        assert receipt["action_receipt_id"].startswith("version_compare_navigation_focus_action_receipt_")
        assert receipt["action_id"]
        assert receipt["action_label"]
        assert receipt["receipt_kind"] in {"preview_action_receipt", "blocked_action_receipt"}
        assert receipt["sequence"] >= 1
        assert receipt["selected_version_detail_drawer_id"]
        assert receipt["selected_navigation_item_id"]
        assert receipt["selected_drawer_selection_preview_id"]
        assert receipt["selected_compare_row_count"] >= 75
        assert isinstance(receipt["allowed_in_preview"], bool)
        assert isinstance(receipt["blocked_in_preview"], bool)
        assert receipt["executes_real_action"] is False
        assert receipt["outcome"] in {"preview_ready_no_real_execution", "blocked_preview_only"}
        assert receipt["reason"]
        assert receipt["receipt_status"] == "version_compare_navigation_focus_action_receipt_preview_ready"
        assert receipt["receipt_result_type"] == "owner_note_version_compare_navigation_focus_action_receipt_preview"
        assert receipt["safe_preview_only"] is True

        assert receipt["simulated_only"] is True
        assert receipt["action_receipt_preview_only"] is True
        assert receipt["drawer_action_preview_only"] is True
        assert receipt["selected_drawer_preview_only"] is True
        assert receipt["compare_row_focus_preview_only"] is True
        assert receipt["real_action_executed"] is False
        assert receipt["real_filter_preference_saved"] is False
        assert receipt["real_navigation_state_persisted"] is False
        assert receipt["real_drawer_selection_saved"] is False
        assert receipt["real_raw_evidence_revealed"] is False
        assert receipt["action_execution_allowed_now"] is False
        assert receipt["filter_preference_save_allowed_now"] is False
        assert receipt["navigation_persistence_allowed_now"] is False
        assert receipt["drawer_selection_save_allowed_now"] is False
        assert receipt["raw_evidence_reveal_allowed"] is False
        assert receipt["raw_evidence_lookup_allowed"] is False

    for receipt in preview_receipts:
        assert receipt["receipt_kind"] == "preview_action_receipt"
        assert receipt["allowed_in_preview"] is True
        assert receipt["blocked_in_preview"] is False
        assert receipt["blocked_action_receipt_preview_only"] is False
        assert receipt["preview_action_receipt_preview_only"] is True
        assert receipt["outcome"] == "preview_ready_no_real_execution"

    for receipt in blocked_receipts:
        assert receipt["receipt_kind"] == "blocked_action_receipt"
        assert receipt["allowed_in_preview"] is False
        assert receipt["blocked_in_preview"] is True
        assert receipt["blocked_action_receipt_preview_only"] is True
        assert receipt["preview_action_receipt_preview_only"] is False
        assert receipt["outcome"] == "blocked_preview_only"
        assert receipt["reason"] == "Blocked by Tower preview safety policy."

    assert safety["action_safety_summary_id"].startswith("version_compare_navigation_focus_action_safety_summary_")
    assert safety["action_receipt_count"] == 5
    assert safety["preview_action_receipt_count"] == 3
    assert safety["blocked_action_receipt_count"] == 2
    assert safety["real_action_executed_count"] == 0
    assert safety["raw_evidence_revealed_count"] == 0
    assert safety["persistence_write_count"] == 0
    assert safety["all_actions_preview_only"] is True
    assert safety["all_blocked_actions_blocked"] is True
    assert safety["all_real_execution_blocked"] is True
    assert safety["summary_status"] == "version_compare_navigation_focus_action_safety_summary_preview_ready"
    assert safety["summary_result_type"] == "owner_note_version_compare_navigation_focus_action_safety_summary_preview"
    assert safety["safe_preview_only"] is True
    assert safety["real_action_executed"] is False
    assert safety["real_raw_evidence_revealed"] is False

    assert len(groups) == 3
    group_keys = {group["action_receipt_group_key"] for group in groups}
    assert group_keys == {"preview_actions", "blocked_actions", "all_action_receipts"}

    group_by_key = {group["action_receipt_group_key"]: group for group in groups}

    assert group_by_key["preview_actions"]["action_receipt_count"] == 3
    assert group_by_key["blocked_actions"]["action_receipt_count"] == 2
    assert group_by_key["all_action_receipts"]["action_receipt_count"] == 5

    for group in groups:
        assert group["action_receipt_group_id"].startswith("version_compare_navigation_focus_action_receipt_group_")
        assert group["label"] in {"Preview actions", "Blocked actions", "All action receipts"}
        assert group["sequence"] in {1, 2, 3}
        assert isinstance(group["action_receipt_ids"], list)
        assert group["action_receipt_count"] == len(group["action_receipt_ids"])
        assert group["group_status"] == "version_compare_navigation_focus_action_receipt_group_preview_ready"
        assert group["group_result_type"] == "owner_note_version_compare_navigation_focus_action_receipt_group_preview"
        assert group["safe_preview_only"] is True
        assert group["simulated_only"] is True
        assert group["action_receipt_preview_only"] is True
        assert group["real_action_executed"] is False
        assert group["real_filter_preference_saved"] is False
        assert group["real_navigation_state_persisted"] is False
        assert group["real_drawer_selection_saved"] is False
        assert group["real_raw_evidence_revealed"] is False


def test_pack_196_selected_preview_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.owner_note_vc_nav_focus_action_receipts_v196")
    payload = mod.build_owner_note_vc_nav_focus_action_receipts_v196_payload(force_refresh=True)

    selected = payload["selected_action_receipt_preview"]
    assert selected["selected_action_receipt_preview_id"].startswith("version_compare_navigation_selected_action_receipt_")
    assert selected["selected_action_receipt_id"]
    assert selected["selected_action_id"]
    assert selected["selected_receipt_kind"] in {"preview_action_receipt", "blocked_action_receipt"}
    assert selected["selected_version_detail_drawer_id"]
    assert selected["selected_compare_row_count"] >= 75
    assert selected["selection_status"] == "version_compare_navigation_selected_action_receipt_preview_ready"
    assert selected["selection_result_type"] == "owner_note_version_compare_navigation_selected_action_receipt_preview"
    assert selected["safe_preview_only"] is True
    assert selected["real_action_executed"] is False
    assert selected["real_filter_preference_saved"] is False
    assert selected["real_navigation_state_persisted"] is False
    assert selected["real_drawer_selection_saved"] is False
    assert selected["real_raw_evidence_revealed"] is False

    indexes = payload["action_receipt_indexes"]

    assert indexes["action_receipts_by_id"]
    assert indexes["action_receipts_by_action_id"]
    assert indexes["action_receipts_by_kind"]
    assert indexes["action_receipts_by_blocked_state"]
    assert indexes["action_receipt_groups_by_id"]
    assert indexes["action_receipt_groups_by_key"]
    assert indexes["selected_action_receipt_preview_by_id"]

    assert "preview_action_receipt" in indexes["action_receipts_by_kind"]
    assert "blocked_action_receipt" in indexes["action_receipts_by_kind"]
    assert len(indexes["action_receipts_by_blocked_state"]["preview"]) == 3
    assert len(indexes["action_receipts_by_blocked_state"]["blocked"]) == 2
    assert "preview_actions" in indexes["action_receipt_groups_by_key"]
    assert "blocked_actions" in indexes["action_receipt_groups_by_key"]
    assert "all_action_receipts" in indexes["action_receipt_groups_by_key"]
    assert selected["selected_action_receipt_preview_id"] in indexes["selected_action_receipt_preview_by_id"]

    bridge = mod.build_owner_note_vc_nav_focus_action_receipts_v196_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 196
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/owner-note-vc-nav-focus-action-receipts-v196.json"
    assert bridge["action_receipt_count"] == 5
    assert bridge["preview_action_receipt_count"] == 3
    assert bridge["blocked_action_receipt_count"] == 2
    assert bridge["action_receipt_group_count"] == 3
    assert bridge["selected_action_receipt_preview_count"] == 1
    assert bridge["real_action_executed_count"] == 0
    assert bridge["raw_evidence_revealed_count"] == 0
    assert bridge["persistence_write_count"] == 0
    assert bridge["selected_action_receipt_id"]
    assert bridge["selected_version_detail_drawer_id"]

    action = mod.build_owner_note_vc_nav_focus_action_receipts_v196_quick_action()
    assert action["id"] == "owner_note_vc_nav_focus_action_receipts_v196"
    assert action["href"] == "/tower/owner-note-vc-nav-focus-action-receipts-v196.json"
    assert action["status"] == "ready"

    section = mod.build_owner_note_vc_nav_focus_action_receipts_v196_unified_owner_section()
    assert section["section_id"] == "owner_note_vc_nav_focus_action_receipts_v196"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/owner-note-vc-nav-focus-action-receipts-v196.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_196_owner_note_vc_nav_focus_action_receipts_v196_status_bridge")
    tower_bridge = status.build_pack_196_owner_note_vc_nav_focus_action_receipts_v196_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_196_owner_note_vc_nav_focus_action_receipts_v196_quick_action")
    assert hasattr(qa, "append_pack_196_owner_note_vc_nav_focus_action_receipts_v196_quick_action")
    actions = qa.append_pack_196_owner_note_vc_nav_focus_action_receipts_v196_quick_action([])
    assert any(item.get("id") == "owner_note_vc_nav_focus_action_receipts_v196" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_196_owner_note_vc_nav_focus_action_receipts_v196_unified_section")
    assert hasattr(unified, "append_pack_196_owner_note_vc_nav_focus_action_receipts_v196_section")
    sections = unified.append_pack_196_owner_note_vc_nav_focus_action_receipts_v196_section([])
    assert any(item.get("section_id") == "owner_note_vc_nav_focus_action_receipts_v196" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-focus-action-receipts-v196.json" in app_text
    assert "tower_owner_note_vc_nav_focus_action_receipts_v196_json" in app_text
    assert "_pack_196_owner_note_vc_nav_focus_action_receipts_v196_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-focus-action-receipts-v196.json" in route_text
    assert "_pack_196_owner_note_vc_nav_focus_action_receipts_v196_route_guard" in route_text

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
