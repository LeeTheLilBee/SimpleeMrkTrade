
"""
PACK 195 fast test - Owner Note Version Compare Navigation Selected Drawer
Detail / Compare Row Focus Preview.

Uses short safe module:
    tower.owner_note_vc_nav_drawer_focus_v195
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_195_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.owner_note_vc_nav_drawer_focus_v195")
    payload = mod.build_owner_note_vc_nav_drawer_focus_v195_payload(force_refresh=True)

    assert payload["pack_number"] == 195
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/owner-note-vc-nav-drawer-focus-v195.json"
    assert payload["source_endpoint"] == "/tower/owner-note-vc-nav-filter-nav-v194.json"

    required_true = [
        "simulated_only",
        "selected_drawer_preview_only",
        "compare_row_focus_preview_only",
        "drawer_action_preview_only",
        "breadcrumb_preview_only",
        "navigation_preview_only",
        "filter_navigation_preview_only",
        "drawer_selection_preview_only",
        "filter_preview_only",
        "search_facet_preview_only",
        "version_detail_preview_only",
        "compare_view_preview_only",
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
    assert summary["selected_drawer_focus_count"] == 1
    assert summary["breadcrumb_count"] == 3
    assert summary["compare_row_focus_card_count"] >= 75
    assert summary["changed_focus_card_count"] >= 1
    assert summary["unchanged_focus_card_count"] >= 1
    assert summary["focus_group_count"] == 3
    assert summary["drawer_action_count"] == 5
    assert summary["selected_version_detail_drawer_id"]
    assert summary["selected_compare_row_count"] >= 75

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_194_ready",
        "has_selected_navigation_preview",
        "selected_drawer_present",
        "has_selected_compare_rows",
        "breadcrumb_trail_ready",
        "has_compare_row_focus_cards",
        "has_changed_focus_cards",
        "has_unchanged_focus_cards",
        "all_focus_cards_ready",
        "has_focus_groups",
        "all_focus_groups_ready",
        "drawer_action_panel_ready",
        "selected_drawer_focus_ready",
        "focus_indexes_present",
        "focus_group_indexes_present",
        "selected_focus_indexes_present",
        "all_simulated_only",
        "all_selected_drawer_preview_only",
        "all_compare_row_focus_preview_only",
        "all_navigation_preview_only",
        "all_drawer_selection_preview_only",
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


def test_pack_195_breadcrumb_focus_cards_groups_and_action_panel():
    mod = importlib.import_module("tower.owner_note_vc_nav_drawer_focus_v195")
    payload = mod.build_owner_note_vc_nav_drawer_focus_v195_payload(force_refresh=True)

    breadcrumb = payload["breadcrumb_trail"]
    cards = payload["compare_row_focus_cards"]
    groups = payload["focus_groups"]
    panel = payload["drawer_action_panel"]
    focus = payload["selected_drawer_focus"]

    assert breadcrumb["breadcrumb_trail_id"].startswith("version_compare_navigation_drawer_focus_breadcrumb_")
    assert breadcrumb["breadcrumb_count"] == 3
    assert len(breadcrumb["breadcrumbs"]) == 3
    assert breadcrumb["trail_status"] == "version_compare_navigation_drawer_focus_breadcrumb_preview_ready"
    assert breadcrumb["trail_result_type"] == "owner_note_version_compare_navigation_drawer_focus_breadcrumb_preview"
    assert breadcrumb["safe_preview_only"] is True

    labels = [crumb["label"] for crumb in breadcrumb["breadcrumbs"]]
    assert labels == ["Compare filter", "Navigation item", "Selected drawer"]

    for crumb in breadcrumb["breadcrumbs"]:
        assert crumb["breadcrumb_id"]
        assert crumb["label"]
        assert crumb["value"]
        assert crumb["sequence"] in {1, 2, 3}

    assert len(cards) >= 75

    changed_cards = [card for card in cards if card["changed"] is True]
    unchanged_cards = [card for card in cards if card["changed"] is False]

    assert len(changed_cards) >= 1
    assert len(unchanged_cards) >= 1

    selected_drawer_id = focus["selected_version_detail_drawer_id"]

    for card in cards:
        assert card["compare_row_focus_card_id"].startswith("version_compare_navigation_compare_row_focus_")
        assert card["selected_version_detail_drawer_id"] == selected_drawer_id
        assert card["compare_row_id"]
        assert card["sequence"] >= 1
        assert card["focus_state"] in {"changed_focus_preview", "unchanged_focus_preview"}
        assert isinstance(card["changed"], bool)
        assert card["row_summary_label"] in {"Changed compare row preview", "Unchanged compare row preview"}
        assert card["raw_content_redacted"] is True
        assert card["raw_evidence_available_in_preview"] is False
        assert card["focus_card_status"] == "version_compare_navigation_compare_row_focus_card_preview_ready"
        assert card["focus_card_result_type"] == "owner_note_version_compare_navigation_compare_row_focus_card_preview"
        assert card["open_allowed_in_preview"] is True
        assert card["safe_preview_only"] is True

        assert card["simulated_only"] is True
        assert card["selected_drawer_preview_only"] is True
        assert card["compare_row_focus_preview_only"] is True
        assert card["navigation_preview_only"] is True
        assert card["drawer_selection_preview_only"] is True
        assert card["real_filter_preference_saved"] is False
        assert card["real_navigation_state_persisted"] is False
        assert card["real_drawer_selection_saved"] is False
        assert card["real_raw_evidence_revealed"] is False
        assert card["raw_evidence_reveal_allowed"] is False
        assert card["raw_evidence_lookup_allowed"] is False
        assert card["filter_preference_save_allowed_now"] is False
        assert card["navigation_persistence_allowed_now"] is False
        assert card["drawer_selection_save_allowed_now"] is False

    assert len(groups) == 3
    group_keys = {group["focus_group_key"] for group in groups}
    assert group_keys == {"changed_rows_focus", "unchanged_rows_focus", "all_rows_focus"}

    group_by_key = {group["focus_group_key"]: group for group in groups}

    assert group_by_key["changed_rows_focus"]["focus_card_count"] == len(changed_cards)
    assert group_by_key["unchanged_rows_focus"]["focus_card_count"] == len(unchanged_cards)
    assert group_by_key["all_rows_focus"]["focus_card_count"] == len(cards)

    for group in groups:
        assert group["focus_group_id"].startswith("version_compare_navigation_focus_group_")
        assert group["label"] in {"Changed compare rows", "Unchanged compare rows", "All compare rows"}
        assert group["sequence"] in {1, 2, 3}
        assert isinstance(group["focus_card_ids"], list)
        assert group["focus_card_count"] == len(group["focus_card_ids"])
        assert group["focus_group_status"] == "version_compare_navigation_compare_row_focus_group_preview_ready"
        assert group["focus_group_result_type"] == "owner_note_version_compare_navigation_compare_row_focus_group_preview"
        assert group["safe_preview_only"] is True
        assert group["real_filter_preference_saved"] is False
        assert group["real_navigation_state_persisted"] is False
        assert group["real_drawer_selection_saved"] is False
        assert group["real_raw_evidence_revealed"] is False

    assert panel["drawer_action_panel_id"].startswith("version_compare_navigation_drawer_action_panel_")
    assert panel["selected_version_detail_drawer_id"] == selected_drawer_id
    assert panel["action_count"] == 5
    assert len(panel["actions"]) == 5
    assert panel["visible_focus_card_count"] == len(cards)
    assert panel["panel_status"] == "version_compare_navigation_drawer_action_panel_preview_ready"
    assert panel["panel_result_type"] == "owner_note_version_compare_navigation_drawer_action_panel_preview"
    assert panel["safe_preview_only"] is True
    assert panel["real_filter_preference_saved"] is False
    assert panel["real_navigation_state_persisted"] is False
    assert panel["real_drawer_selection_saved"] is False
    assert panel["real_raw_evidence_revealed"] is False

    action_ids = {action["action_id"] for action in panel["actions"]}
    assert action_ids == {
        "preview_open_drawer",
        "preview_filter_changed_rows",
        "preview_filter_unchanged_rows",
        "blocked_save_selection",
        "blocked_reveal_raw_evidence",
    }

    blocked = [action for action in panel["actions"] if action["action_id"].startswith("blocked_")]
    preview = [action for action in panel["actions"] if action["action_id"].startswith("preview_")]

    assert len(blocked) == 2
    assert len(preview) == 3

    for action in blocked:
        assert action["allowed_in_preview"] is False
        assert action["executes_real_action"] is False

    for action in preview:
        assert action["allowed_in_preview"] is True
        assert action["executes_real_action"] is False


def test_pack_195_selected_focus_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.owner_note_vc_nav_drawer_focus_v195")
    payload = mod.build_owner_note_vc_nav_drawer_focus_v195_payload(force_refresh=True)

    focus = payload["selected_drawer_focus"]
    cards = payload["compare_row_focus_cards"]

    assert focus["selected_drawer_focus_id"].startswith("version_compare_navigation_selected_drawer_focus_")
    assert focus["default_filter_lane_id"] == "all_compare_drawers"
    assert focus["selected_navigation_item_id"]
    assert focus["selected_drawer_selection_preview_id"]
    assert focus["selected_version_detail_drawer_id"]
    assert focus["selected_compare_row_count"] >= 75
    assert isinstance(focus["selected_compare_row_ids"], list)
    assert len(focus["selected_compare_row_ids"]) >= 75
    assert focus["breadcrumb_trail_id"] == payload["breadcrumb_trail"]["breadcrumb_trail_id"]
    assert focus["compare_row_focus_card_count"] == len(cards)
    assert len(focus["compare_row_focus_card_ids"]) == len(cards)
    assert focus["focus_group_count"] == 3
    assert len(focus["focus_group_ids"]) == 3
    assert focus["drawer_action_panel_id"] == payload["drawer_action_panel"]["drawer_action_panel_id"]
    assert focus["focus_status"] == "version_compare_navigation_selected_drawer_focus_preview_ready"
    assert focus["focus_result_type"] == "owner_note_version_compare_navigation_selected_drawer_focus_preview"
    assert focus["open_allowed_in_preview"] is True
    assert focus["selection_allowed_in_preview"] is True
    assert focus["safe_preview_only"] is True
    assert focus["real_filter_preference_saved"] is False
    assert focus["real_navigation_state_persisted"] is False
    assert focus["real_drawer_selection_saved"] is False
    assert focus["real_raw_evidence_revealed"] is False

    indexes = payload["drawer_focus_indexes"]

    assert indexes["compare_row_focus_cards_by_id"]
    assert indexes["compare_row_focus_cards_by_row_id"]
    assert indexes["compare_row_focus_cards_by_changed_state"]
    assert indexes["focus_groups_by_id"]
    assert indexes["focus_groups_by_key"]
    assert indexes["selected_drawer_focus_by_id"]
    assert indexes["selected_drawer_focus_by_drawer_id"]

    assert indexes["compare_row_focus_cards_by_changed_state"]["changed"]
    assert indexes["compare_row_focus_cards_by_changed_state"]["unchanged"]
    assert "changed_rows_focus" in indexes["focus_groups_by_key"]
    assert "unchanged_rows_focus" in indexes["focus_groups_by_key"]
    assert "all_rows_focus" in indexes["focus_groups_by_key"]
    assert focus["selected_drawer_focus_id"] in indexes["selected_drawer_focus_by_id"]
    assert focus["selected_version_detail_drawer_id"] in indexes["selected_drawer_focus_by_drawer_id"]

    bridge = mod.build_owner_note_vc_nav_drawer_focus_v195_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 195
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/owner-note-vc-nav-drawer-focus-v195.json"
    assert bridge["selected_drawer_focus_count"] == 1
    assert bridge["breadcrumb_count"] == 3
    assert bridge["compare_row_focus_card_count"] >= 75
    assert bridge["changed_focus_card_count"] >= 1
    assert bridge["unchanged_focus_card_count"] >= 1
    assert bridge["focus_group_count"] == 3
    assert bridge["drawer_action_count"] == 5
    assert bridge["selected_version_detail_drawer_id"]
    assert bridge["selected_compare_row_count"] >= 75

    action = mod.build_owner_note_vc_nav_drawer_focus_v195_quick_action()
    assert action["id"] == "owner_note_vc_nav_drawer_focus_v195"
    assert action["href"] == "/tower/owner-note-vc-nav-drawer-focus-v195.json"
    assert action["status"] == "ready"

    section = mod.build_owner_note_vc_nav_drawer_focus_v195_unified_owner_section()
    assert section["section_id"] == "owner_note_vc_nav_drawer_focus_v195"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/owner-note-vc-nav-drawer-focus-v195.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_195_owner_note_vc_nav_drawer_focus_v195_status_bridge")
    tower_bridge = status.build_pack_195_owner_note_vc_nav_drawer_focus_v195_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_195_owner_note_vc_nav_drawer_focus_v195_quick_action")
    assert hasattr(qa, "append_pack_195_owner_note_vc_nav_drawer_focus_v195_quick_action")
    actions = qa.append_pack_195_owner_note_vc_nav_drawer_focus_v195_quick_action([])
    assert any(item.get("id") == "owner_note_vc_nav_drawer_focus_v195" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_195_owner_note_vc_nav_drawer_focus_v195_unified_section")
    assert hasattr(unified, "append_pack_195_owner_note_vc_nav_drawer_focus_v195_section")
    sections = unified.append_pack_195_owner_note_vc_nav_drawer_focus_v195_section([])
    assert any(item.get("section_id") == "owner_note_vc_nav_drawer_focus_v195" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-drawer-focus-v195.json" in app_text
    assert "tower_owner_note_vc_nav_drawer_focus_v195_json" in app_text
    assert "_pack_195_owner_note_vc_nav_drawer_focus_v195_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/owner-note-vc-nav-drawer-focus-v195.json" in route_text
    assert "_pack_195_owner_note_vc_nav_drawer_focus_v195_route_guard" in route_text

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
