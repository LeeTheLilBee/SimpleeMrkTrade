"""The Clouds Giant Pack 003 verification."""

from __future__ import annotations

import json
from pathlib import Path

from clouds.clouds_owner_focus_service import (
    get_clouds_blocked_watch_payload,
    get_clouds_focus_lanes_payload,
    get_clouds_gp003_status_payload,
    get_clouds_owner_focus_dashboard_payload,
    get_clouds_owner_focus_queue_payload,
)


def test_clouds_gp003_owner_focus_queue_is_ready_and_routing_only():
    payload = get_clouds_owner_focus_queue_payload()
    json.dumps(payload)

    assert payload["app_id"] == "clouds"
    assert payload["payload_type"] == "clouds_owner_focus_queue"
    assert payload["status"] == "ready"
    assert payload["focus_count"] >= 16
    assert payload["critical_count"] >= 4
    assert payload["high_count"] >= 7
    assert payload["ready_count"] >= 5
    assert payload["blocked_count"] >= 7

    assert payload["boundary"]["clouds_can_complete_actions"] is False
    assert payload["boundary"]["clouds_can_route_to_owning_app"] is True
    assert payload["boundary"]["owning_app_keeps_authority"] is True
    assert payload["boundary"]["summary_only_redacted"] is True
    assert payload["boundary"]["placeholder_sources_are_not_connected"] is True

    source_apps = {item["source_app"] for item in payload["focus_items"]}
    assert "archive_vault" in source_apps
    assert "tower" in source_apps
    assert "observatory" in source_apps
    assert "teller" in source_apps
    assert "simplee_on_the_go" in source_apps
    assert "simplee_property" in source_apps


def test_clouds_gp003_focus_lanes_group_attention():
    payload = get_clouds_focus_lanes_payload()

    assert payload["payload_type"] == "clouds_focus_lanes"
    assert payload["status"] == "ready"
    assert payload["lane_count"] >= 8
    assert payload["boundary"]["lanes_are_dashboard_groupings"] is True
    assert payload["boundary"]["owning_apps_keep_authority"] is True
    assert payload["boundary"]["clouds_routes_only"] is True

    lane_ids = {lane["lane_id"] for lane in payload["lanes"]}
    assert "vault" in lane_ids
    assert "clouds" in lane_ids
    assert "tower" in lane_ids
    assert "observatory" in lane_ids
    assert "teller" in lane_ids
    assert "atm" in lane_ids
    assert "property" in lane_ids


def test_clouds_gp003_blocked_watch_defaults_to_keep_blocked():
    payload = get_clouds_blocked_watch_payload()

    assert payload["payload_type"] == "clouds_blocked_watch"
    assert payload["status"] == "ready"
    assert payload["blocked_item_count"] >= 7
    assert payload["blocked_reason_count"] >= 7

    reasons = set(payload["blocked_reasons"])
    assert "direct_upload_locked" in reasons
    assert "export_locked" in reasons
    assert "source_contract_not_connected" in reasons

    assert payload["boundary"]["default_action"] == "keep_blocked"
    assert payload["boundary"]["clouds_can_unlock"] is False
    assert payload["boundary"]["tower_or_owning_app_required"] is True
    assert payload["boundary"]["blocked_watch_is_visibility_only"] is True


def test_clouds_gp003_dashboard_rolls_up_focus_queue():
    payload = get_clouds_owner_focus_dashboard_payload()

    assert payload["payload_type"] == "clouds_owner_focus_dashboard"
    assert payload["status"] == "ready"
    assert payload["focus_summary"]["focus_count"] >= 16
    assert payload["focus_summary"]["critical_count"] >= 4
    assert payload["focus_summary"]["high_count"] >= 7
    assert payload["lane_summary"]["lane_count"] >= 8
    assert payload["blocked_watch"]["blocked_reason_count"] >= 7
    assert payload["registry_summary"]["registered_app_count"] >= 8
    assert payload["registry_summary"]["placeholder_count"] >= 3
    assert payload["gp001_summary"]["dashboard_status"] == "ready"
    assert payload["gp001_summary"]["vault_final_score"] == 100
    assert len(payload["open_app_targets"]) >= 6


def test_clouds_gp003_status_is_ready_and_safe_to_continue():
    payload = get_clouds_gp003_status_payload()

    assert payload["payload_type"] == "clouds_gp003_status"
    assert payload["status"] == "ready"
    assert payload["pack"] == "The Clouds Giant Pack 003"
    assert payload["focus_count"] >= 16
    assert payload["critical_count"] >= 4
    assert payload["high_count"] >= 7
    assert payload["ready_count"] >= 5
    assert payload["blocked_count"] >= 7
    assert payload["lane_count"] >= 8
    assert payload["blocked_reason_count"] >= 7
    assert payload["clouds_can_complete_actions"] is False
    assert payload["clouds_can_route_to_owning_app"] is True
    assert payload["summary_only_redacted"] is True
    assert payload["safe_to_continue_to_clouds_gp004"] is True


def test_clouds_gp003_routes_template_and_css_exist():
    routes = Path("clouds/clouds_routes.py").read_text(encoding="utf-8")
    template = Path("templates/clouds_owner_focus.html").read_text(encoding="utf-8")
    css = Path("static/clouds/clouds_owner_focus.css").read_text(encoding="utf-8")

    assert "/clouds/owner-focus" in routes
    assert "/clouds/owner-focus-queue.json" in routes
    assert "/clouds/focus-lanes.json" in routes
    assert "/clouds/blocked-watch.json" in routes
    assert "/clouds/owner-focus-dashboard.json" in routes
    assert "/clouds/gp003-status.json" in routes

    assert "One queue for what matters next." in template
    assert "Focus Queue" in template
    assert "Focus Lanes" in template
    assert "Blocked Watch" in template
    assert "Open-App Targets" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()
