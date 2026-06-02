
"""
PACK 199 fast test - Owner Note Version Compare Navigation Selected Action
Receipt Detail Focus Preview.

Uses short safe module:
    tower.owner_note_vc_nav_receipt_detail_focus_v199
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_199_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.owner_note_vc_nav_receipt_detail_focus_v199")
    payload = mod.build_owner_note_vc_nav_receipt_detail_focus_v199_payload(force_refresh=True)

    assert payload["pack_number"] == 199
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/owner-note-vc-nav-receipt-detail-focus-v199.json"
    assert payload["source_endpoint"] == "/tower/owner-note-vc-nav-action-receipt-filter-nav-v198.json"

    required_true = [
        "simulated_only",
        "receipt_detail_focus_preview_only",
        "receipt_safety_detail_preview_only",
        "receipt_action_panel_preview_only",
        "receipt_breadcrumb_preview_only",
        "action_receipt_navigation_preview_only",
        "receipt_selection_preview_only",
        "action_receipt_filter_preview_only",
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
    assert summary["selected_receipt_detail_focus_count"] == 1
    assert summary["breadcrumb_count"] == 4
    assert summary["receipt_safety_detail_card_count"] == 6
    assert summary["blocked_safety_detail_card_count"] == 5
    assert summary["preview_scope_detail_card_count"] == 1
    assert summary["receipt_detail_focus_group_count"] == 3
    assert summary["receipt_action_count"] == 6
    assert summary["selected_action_receipt_id"]
    assert summary["selected_action_receipt_count"] == 5

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_198_ready",
        "has_selected_action_receipt_navigation_preview",
        "selected_receipt_present",
        "breadcrumb_trail_ready",
        "has_safety_detail_cards",
        "has_blocked_safety_cards",
        "has_preview_scope_cards",
        "all_safety_cards_ready",
        "has_focus_groups",
        "all_focus_groups_ready",
        "receipt_action_panel_ready",
        "selected_receipt_focus_ready",
        "focus_indexes_present",
        "focus_group_indexes_present",
        "selected_focus_indexes_present",
        "all_simulated_only",
        "all_receipt_detail_focus_preview_only",
        "all_receipt_safety_detail_preview_only",
        "all_action_receipt_navigation_preview_only",
        "all_receipt_selection_preview_only",
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


def test_pack_199_breadcrumb_cards_groups_and_action_panel():
    mod = importlib.import_module("tower.owner_note_vc_nav_receipt_detail_focus_v199")
    payload = mod.build_owner_note_vc_nav_receipt_detail_focus_v199_payload(force_refresh=True)

    breadcrumb = payload["receipt_breadcrumb_trail"]
    cards = payload["receipt_safety_detail_cards"]
    groups = payload["receipt_detail_focus_groups"]
    panel = payload["receipt_action_detail_panel"]
    focus = payload["selected_receipt_detail_focus"]

    assert breadcrumb["receipt_breadcrumb_trail_id"].startswith("version_compare_navigation_receipt_detail_breadcrumb_")
    assert breadcrumb["breadcrumb_count"] == 4
    assert len(breadcrumb["breadcrumbs"]) == 4
    assert breadcrumb["trail_status"] == "version_compare_navigation_receipt_detail_breadcrumb_preview_ready"
    assert breadcrumb["trail_result_type"] == "owner_note_version_compare_navigation_receipt_detail_breadcrumb_preview"
    assert breadcrumb["safe_preview_only"] is True

    labels = [crumb["label"] for crumb in breadcrumb["breadcrumbs"]]
    assert labels == ["Receipt filter", "Receipt navigation", "Receipt selection", "Selected receipt"]

    for crumb in breadcrumb["breadcrumbs"]:
        assert crumb["breadcrumb_id"]
        assert crumb["label"]
        assert crumb["value"]
        assert crumb["sequence"] in {1, 2, 3, 4}

    assert len(cards) == 6

    blocked_cards = [card for card in cards if card["state"] == "Blocked"]
    preview_cards = [card for card in cards if card["state"] == "Preview only"]

    assert len(blocked_cards) == 5
    assert len(preview_cards) == 1

    expected_keys = {
        "execution_block",
        "raw_evidence_block",
        "preference_write_block",
        "navigation_write_block",
        "drawer_selection_write_block",
        "receipt_preview_scope",
    }

    assert {card["safety_key"] for card in cards} == expected_keys

    selected_receipt_id = focus["selected_action_receipt_id"]

    for card in cards:
        assert card["receipt_safety_detail_card_id"].startswith("version_compare_navigation_receipt_safety_card_")
        assert card["safety_key"] in expected_keys
        assert card["title"]
        assert card["state"] in {"Blocked", "Preview only"}
        assert card["description"]
        assert card["sequence"] >= 1
        assert card["selected_action_receipt_id"] == selected_receipt_id
        assert card["card_status"] == "version_compare_navigation_receipt_safety_detail_card_preview_ready"
        assert card["card_result_type"] == "owner_note_version_compare_navigation_receipt_safety_detail_card_preview"
        assert card["safe_preview_only"] is True

        assert card["simulated_only"] is True
        assert card["receipt_detail_focus_preview_only"] is True
        assert card["receipt_safety_detail_preview_only"] is True
        assert card["action_receipt_navigation_preview_only"] is True
        assert card["receipt_selection_preview_only"] is True
        assert card["action_receipt_preview_only"] is True
        assert card["real_action_executed"] is False
        assert card["real_filter_preference_saved"] is False
        assert card["real_navigation_state_persisted"] is False
        assert card["real_drawer_selection_saved"] is False
        assert card["real_raw_evidence_revealed"] is False
        assert card["action_execution_allowed_now"] is False
        assert card["filter_preference_save_allowed_now"] is False
        assert card["navigation_persistence_allowed_now"] is False
        assert card["drawer_selection_save_allowed_now"] is False
        assert card["raw_evidence_reveal_allowed"] is False
        assert card["raw_evidence_lookup_allowed"] is False

    assert len(groups) == 3
    group_keys = {group["receipt_detail_focus_group_key"] for group in groups}
    assert group_keys == {"blocked_safety_details", "preview_scope_details", "all_receipt_detail_cards"}

    group_by_key = {group["receipt_detail_focus_group_key"]: group for group in groups}

    assert group_by_key["blocked_safety_details"]["receipt_safety_detail_card_count"] == 5
    assert group_by_key["preview_scope_details"]["receipt_safety_detail_card_count"] == 1
    assert group_by_key["all_receipt_detail_cards"]["receipt_safety_detail_card_count"] == 6

    for group in groups:
        assert group["receipt_detail_focus_group_id"].startswith("version_compare_navigation_receipt_detail_group_")
        assert group["label"] in {"Blocked safety details", "Preview scope details", "All receipt detail cards"}
        assert group["sequence"] in {1, 2, 3}
        assert isinstance(group["receipt_safety_detail_card_ids"], list)
        assert group["receipt_safety_detail_card_count"] == len(group["receipt_safety_detail_card_ids"])
        assert group["group_status"] == "version_compare_navigation_receipt_detail_focus_group_preview_ready"
        assert group["group_result_type"] == "owner_note_version_compare_navigation_receipt_detail_focus_group_preview"
        assert group["safe_preview_only"] is True
        assert group["real_action_executed"] is False
        assert group["real_filter_preference_saved"] is False
        assert group["real_navigation_state_persisted"] is False
        assert group["real_drawer_selection_saved"] is False
        assert group["real_raw_evidence_revealed"] is False

    assert panel["receipt_action_detail_panel_id"].startswith("version_compare_navigation_receipt_action_panel_")
    assert panel["selected_action_receipt_id"] == selected_receipt_id
    assert panel["action_count"] == 6
    assert len(panel["actions"]) == 6
    assert panel["visible_safety_detail_card_count"] == 6
    assert panel["panel_status"] == "version_compare_navigation_receipt_action_detail_panel_preview_ready"
    assert panel["panel_result_type"] == "owner_note_version_compare_navigation_receipt_action_detail_panel_preview"
    assert panel["safe_preview_only"] is True
    assert panel["real_action_executed"] is False
    assert panel["real_filter_preference_saved"] is False
    assert panel["real_navigation_state_persisted"] is False
    assert panel["real_drawer_selection_saved"] is False
    assert panel["real_raw_evidence_revealed"] is False

    action_ids = {action["action_id"] for action in panel["actions"]}
    assert action_ids == {
        "preview_open_receipt_detail",
        "preview_show_safety_cards",
        "preview_show_breadcrumbs",
        "blocked_save_receipt_selection",
        "blocked_reveal_receipt_raw_evidence",
        "blocked_execute_receipt_action",
    }

    blocked_actions = [action for action in panel["actions"] if action["action_id"].startswith("blocked_")]
    preview_actions = [action for action in panel["actions"] if action["action_id"].startswith("preview_")]

    assert len(blocked_actions) == 3
    assert len(preview_actions) == 3

    for action in blocked_actions:
        assert action["allowed_in_preview"] is False
        assert action["executes_real_action"] is False

    for action in preview_actions:
        assert action["allowed_in_preview"] is True
        assert action["executes_real_action"] is False


def test_pack_199_selected_focus_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.owner_note_vc_nav_receipt_detail_focus_v199")
    payload = mod.build_owner_note_vc_nav_receipt_detail_focus_v199_payload(force_refresh=True)

    focus = payload["selected_receipt_detail_focus"]
    cards = payload["receipt_safety_detail_cards"]
    groups = payload["receipt_detail_focus_groups"]
    panel = payload["receipt_action_detail_panel"]

    assert focus["selected_receipt_detail_focus_id"].startswith("version_compare_navigation_selected_receipt_focus_")
    assert focus["default_action_receipt_filter_lane_id"] == "all_action_receipts"
    assert focus["selected_action_receipt_navigation_item_id"]
    assert focus["selected_action_receipt_selection_preview_id"]
    assert focus["selected_action_receipt_id"]
    assert focus["selected_action_receipt_count"] == 5
    assert focus["receipt_breadcrumb_trail_id"] == payload["receipt_breadcrumb_trail"]["receipt_breadcrumb_trail_id"]
    assert focus["receipt_safety_detail_card_count"] == len(cards)
    assert len(focus["receipt_safety_detail_card_ids"]) == len(cards)
    assert focus["receipt_detail_focus_group_count"] == len(groups)
    assert len(focus["receipt_detail_focus_group_ids"]) == len(groups)
    assert focus["receipt_action_detail_panel_id"] == panel["receipt_action_detail_panel_id"]
    assert focus["focus_status"] == "version_compare_navigation_selected_receipt_detail_focus_preview_ready"
    assert focus["focus_result_type"] == "owner_note_version_compare_navigation_selected_receipt_detail_focus_preview"
    assert focus["open_allowed_in_preview"] is True
    assert focus["selection_allowed_in_preview"] is True
    assert focus["safe_preview_only"] is True
    assert focus["real_action_executed"] is False
    assert focus["real_filter_preference_saved"] is False
    assert focus["real_navigation_state_persisted"] is False
    assert focus["real_drawer_selection_saved"] is False
    assert focus["real_raw_evidence_revealed"] is False

    indexes = payload["receipt_detail_focus_indexes"]

    assert indexes["receipt_safety_detail_cards_by_id"]
    assert indexes["receipt_safety_detail_cards_by_key"]
    assert indexes["receipt_safety_detail_cards_by_state"]
    assert indexes["receipt_detail_focus_groups_by_id"]
    assert indexes["receipt_detail_focus_groups_by_key"]
    assert indexes["selected_receipt_detail_focus_by_id"]
    assert indexes["selected_receipt_detail_focus_by_receipt_id"]

    assert "Blocked" in indexes["receipt_safety_detail_cards_by_state"]
    assert "Preview only" in indexes["receipt_safety_detail_cards_by_state"]
    assert len(indexes["receipt_safety_detail_cards_by_state"]["Blocked"]) == 5
    assert len(indexes["receipt_safety_detail_cards_by_state"]["Preview only"]) == 1
    assert "blocked_safety_details" in indexes["receipt_detail_focus_groups_by_key"]
    assert "preview_scope_details" in indexes["receipt_detail_focus_groups_by_key"]
    assert "all_receipt_detail_cards" in indexes["receipt_detail_focus_groups_by_key"]
    assert focus["selected_receipt_detail_focus_id"] in indexes["selected_receipt_detail_focus_by_id"]
    assert focus["selected_action_receipt_id"] in indexes["selected_receipt_detail_focus_by_receipt_id"]

    bridge = mod.build_owner_note_vc_nav_receipt_detail_focus_v199_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 199
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/owner-note-vc-nav-receipt-detail-focus-v199.json"
    assert bridge["selected_receipt_detail_focus_count"] == 1
    assert bridge["breadcrumb_count"] == 4
    assert bridge["receipt_safety_detail_card_count"] == 6
    assert bridge["blocked_safety_detail_card_count"] == 5
    assert bridge["preview_scope_detail_card_count"] == 1
    assert bridge["receipt_detail_focus_group_count"] == 3
    assert bridge["receipt_action_count"] == 6
    assert bridge["selected_action_receipt_id"]
    assert bridge["selected_action_receipt_count"] == 5

    action = mod.build_owner_note_vc_nav_receipt_detail_focus_v199_quick_action()
    assert action["id"] == "owner_note_vc_nav_receipt_detail_focus_v199"
    assert action["href"] == "/tower/owner-note-vc-nav-receipt-detail-focus-v199.json"
    assert action["status"] == "ready"

    section = mod.build_owner_note_vc_nav_receipt_detail_focus_v199_unified_owner_section()
    assert section["section_id"] == "owner_note_vc_nav_receipt_detail_focus_v199"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/owner-note-vc-nav-receipt-detail-focus-v199.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_199_owner_note_vc_nav_receipt_detail_focus_v199_status_bridge")
    tower_bridge = status.build_pack_199_owner_note_vc_nav_receipt_detail_focus_v199_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_199_owner_note_vc_nav_receipt_detail_focus_v199_quick_action")
    assert hasattr(qa, "append_pack_199_owner_note_vc_nav_receipt_detail_focus_v199_quick_action")
    actions = qa.append_pack_199_owner_note_vc_nav_receipt_detail_focus_v199_quick_action([])
    assert any(item.get("id") == "owner_note_vc_nav_receipt_detail_focus_v199" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_199_owner_note_vc_nav_receipt_detail_focus_v199_unified_section")
    assert hasattr(unified, "append_pack_199_owner_note_vc_nav_receipt_detail_focus_v199_section")
    sections = unified.append_pack_199_owner_note_vc_nav_receipt_detail_focus_v199_section([])
    assert any(item.get("section_id") == "owner_note_vc_nav_receipt_detail_focus_v199" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-receipt-detail-focus-v199.json" in app_text
    assert "tower_owner_note_vc_nav_receipt_detail_focus_v199_json" in app_text
    assert "_pack_199_owner_note_vc_nav_receipt_detail_focus_v199_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-receipt-detail-focus-v199.json" in route_text
    assert "_pack_199_owner_note_vc_nav_receipt_detail_focus_v199_route_guard" in route_text

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
