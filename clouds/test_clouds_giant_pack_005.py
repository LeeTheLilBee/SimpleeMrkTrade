"""The Clouds Giant Pack 005 verification."""

from __future__ import annotations

import json
from pathlib import Path

from clouds.clouds_today_service import (
    get_clouds_gp005_status_payload,
    get_clouds_open_targets_payload,
    get_clouds_owner_snapshot_header_payload,
    get_clouds_today_dashboard_payload,
    get_clouds_today_focus_payload,
    get_clouds_today_watch_payload,
)


def test_clouds_gp005_owner_snapshot_header_is_ready():
    payload = get_clouds_owner_snapshot_header_payload()
    json.dumps(payload)

    assert payload["app_id"] == "clouds"
    assert payload["payload_type"] == "clouds_owner_snapshot_header"
    assert payload["status"] == "ready"
    assert payload["snapshot_status"] == "ready"
    assert payload["snapshot_card_count"] >= 8
    assert payload["vault_final_score"] == 100
    assert payload["vault_safe_to_start_clouds"] is True
    assert payload["clouds_view"] == "summary_only_redacted"

    assert payload["clouds_pack_status"]["gp001"] == "ready"
    assert payload["clouds_pack_status"]["gp002"] == "ready"
    assert payload["clouds_pack_status"]["gp003"] == "ready"
    assert payload["clouds_pack_status"]["gp004"] == "ready"

    assert payload["boundary"]["snapshot_is_visibility_only"] is True
    assert payload["boundary"]["clouds_can_complete_actions"] is False
    assert payload["boundary"]["clouds_can_route_to_owning_app"] is True
    assert payload["boundary"]["summary_only_redacted"] is True


def test_clouds_gp005_today_focus_sections_are_ready():
    payload = get_clouds_today_focus_payload()

    assert payload["payload_type"] == "clouds_today_focus"
    assert payload["status"] == "ready"
    assert payload["focus_count"] >= 16
    assert payload["critical_count"] >= 4
    assert payload["high_count"] >= 7
    assert payload["ready_count"] >= 5
    assert payload["blocked_count"] >= 7
    assert payload["blocked_reason_count"] >= 7
    assert payload["today_top_item_count"] >= 8
    assert len(payload["today_sections"]) == 4

    section_ids = {section["section_id"] for section in payload["today_sections"]}
    assert section_ids == {"today_critical", "today_high", "today_ready", "today_blocked"}

    assert payload["boundary"]["today_view_is_command_visibility"] is True
    assert payload["boundary"]["clouds_can_route"] is True
    assert payload["boundary"]["clouds_can_complete"] is False
    assert payload["boundary"]["blocked_items_default_to_locked"] is True


def test_clouds_gp005_today_watch_keeps_locked_items_visible():
    payload = get_clouds_today_watch_payload()

    assert payload["payload_type"] == "clouds_today_watch"
    assert payload["status"] == "ready"
    assert payload["watch_card_count"] >= 5
    assert payload["blocked_watch"]["blocked_reason_count"] >= 7
    assert payload["placeholder_health"]["placeholder_count"] >= 3

    watch_ids = {card["watch_id"] for card in payload["watch_cards"]}
    assert "watch_blocked_reasons" in watch_ids
    assert "watch_placeholder_apps" in watch_ids
    assert "watch_locked_apps" in watch_ids
    assert "watch_vault_locked" in watch_ids

    assert payload["boundary"]["watch_items_do_not_unlock"] is True
    assert payload["boundary"]["clouds_can_route_only"] is True
    assert payload["boundary"]["owning_app_or_tower_required"] is True


def test_clouds_gp005_open_targets_are_routes_not_authority():
    payload = get_clouds_open_targets_payload()

    assert payload["payload_type"] == "clouds_open_targets"
    assert payload["status"] == "ready"
    assert payload["target_count"] >= 10

    routes = {target["route"] for target in payload["targets"]}
    assert "/vault/final-readiness" in routes
    assert "/clouds/owner-focus" in routes
    assert "/clouds/app-lane-status" in routes

    assert payload["boundary"]["targets_are_links_not_authority"] is True
    assert payload["boundary"]["clouds_routes_to_owning_app"] is True
    assert payload["boundary"]["owning_app_completes_action"] is True


def test_clouds_gp005_today_dashboard_rolls_up_snapshot_focus_watch_targets():
    payload = get_clouds_today_dashboard_payload()

    assert payload["payload_type"] == "clouds_today_dashboard"
    assert payload["status"] == "ready"
    assert payload["snapshot"]["snapshot_card_count"] >= 8
    assert payload["snapshot"]["vault_final_score"] == 100
    assert payload["snapshot"]["clouds_view"] == "summary_only_redacted"
    assert payload["today_focus"]["focus_count"] >= 16
    assert payload["today_focus"]["critical_count"] >= 4
    assert payload["today_focus"]["high_count"] >= 7
    assert payload["today_watch"]["watch_card_count"] >= 5
    assert payload["open_targets"]["target_count"] >= 10
    assert payload["prior_pack_status"]["gp001"] == "ready"
    assert payload["prior_pack_status"]["gp002"] == "ready"
    assert payload["prior_pack_status"]["gp003"] == "ready"
    assert payload["prior_pack_status"]["gp004"] == "ready"

    assert payload["boundary"]["today_view_is_owner_visibility"] is True
    assert payload["boundary"]["clouds_can_complete_actions"] is False
    assert payload["boundary"]["clouds_routes_only"] is True
    assert payload["boundary"]["summary_only_redacted"] is True


def test_clouds_gp005_status_is_ready_and_safe_to_continue():
    payload = get_clouds_gp005_status_payload()

    assert payload["payload_type"] == "clouds_gp005_status"
    assert payload["status"] == "ready"
    assert payload["pack"] == "The Clouds Giant Pack 005"
    assert payload["snapshot_card_count"] >= 8
    assert payload["focus_count"] >= 16
    assert payload["critical_count"] >= 4
    assert payload["high_count"] >= 7
    assert payload["ready_count"] >= 5
    assert payload["blocked_count"] >= 7
    assert payload["watch_card_count"] >= 5
    assert payload["open_target_count"] >= 10
    assert payload["vault_final_score"] == 100
    assert payload["prior_gp001_status"] == "ready"
    assert payload["prior_gp002_status"] == "ready"
    assert payload["prior_gp003_status"] == "ready"
    assert payload["prior_gp004_status"] == "ready"
    assert payload["clouds_can_complete_actions"] is False
    assert payload["clouds_routes_only"] is True
    assert payload["summary_only_redacted"] is True
    assert payload["safe_to_continue_to_clouds_gp006"] is True


def test_clouds_gp005_routes_template_and_css_exist():
    routes = Path("clouds/clouds_routes.py").read_text(encoding="utf-8")
    template = Path("templates/clouds_today.html").read_text(encoding="utf-8")
    css = Path("static/clouds/clouds_today.css").read_text(encoding="utf-8")

    assert "/clouds/today" in routes
    assert "/clouds/owner-snapshot.json" in routes
    assert "/clouds/today-focus.json" in routes
    assert "/clouds/today-watch.json" in routes
    assert "/clouds/open-targets.json" in routes
    assert "/clouds/today-dashboard.json" in routes
    assert "/clouds/gp005-status.json" in routes

    assert "Today’s command view." in template
    assert "Owner Snapshot Header" in template
    assert "Today Focus" in template
    assert "Today Watch" in template
    assert "Open-App Targets" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()
