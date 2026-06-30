"""The Clouds Giant Pack 004 verification."""

from __future__ import annotations

import json
from pathlib import Path

from clouds.clouds_app_lane_status_service import (
    get_clouds_app_lane_status_dashboard_payload,
    get_clouds_app_status_board_payload,
    get_clouds_gp004_status_payload,
    get_clouds_lane_status_board_payload,
    get_clouds_placeholder_health_payload,
    get_clouds_vault_live_status_payload,
)


def test_clouds_gp004_app_status_board_is_ready():
    payload = get_clouds_app_status_board_payload()
    json.dumps(payload)

    assert payload["app_id"] == "clouds"
    assert payload["payload_type"] == "clouds_app_status_board"
    assert payload["status"] == "ready"
    assert payload["app_count"] >= 8
    assert payload["live_source_count"] >= 1
    assert payload["vault_summary_source_count"] >= 4
    assert payload["placeholder_count"] >= 3
    assert payload["locked_placeholder_count"] >= 3

    app_ids = {card["app_id"] for card in payload["app_status_cards"]}
    assert "archive_vault" in app_ids
    assert "tower" in app_ids
    assert "observatory" in app_ids
    assert "teller" in app_ids

    assert payload["boundary"]["clouds_is_status_board"] is True
    assert payload["boundary"]["clouds_is_not_authority"] is True
    assert payload["boundary"]["owning_app_keeps_authority"] is True
    assert payload["boundary"]["placeholders_are_not_connected"] is True
    assert payload["boundary"]["summary_only_redacted"] is True


def test_clouds_gp004_lane_status_board_groups_lanes():
    payload = get_clouds_lane_status_board_payload()

    assert payload["payload_type"] == "clouds_lane_status_board"
    assert payload["status"] == "ready"
    assert payload["lane_count"] >= 8
    assert payload["watch_lane_count"] >= 1
    assert payload["vault_live_lane_count"] >= 6
    assert payload["vault_final_score"] == 100

    lane_ids = {lane["lane_id"] for lane in payload["lane_status_cards"]}
    assert "vault" in lane_ids
    assert "atm" in lane_ids
    assert "property" in lane_ids
    assert "trust" in lane_ids
    assert "observatory" in lane_ids
    assert "soulaana" in lane_ids
    assert "beta" in lane_ids

    assert payload["boundary"]["lanes_are_visibility_groupings"] is True
    assert payload["boundary"]["clouds_routes_to_owning_app"] is True
    assert payload["boundary"]["clouds_does_not_execute_lane_actions"] is True


def test_clouds_gp004_placeholder_health_is_not_connected():
    payload = get_clouds_placeholder_health_payload()

    assert payload["payload_type"] == "clouds_placeholder_health"
    assert payload["status"] == "ready"
    assert payload["placeholder_health_count"] >= 3

    apps = set(payload["placeholder_apps"])
    assert "tower" in apps
    assert "observatory" in apps
    assert "teller" in apps

    for card in payload["health_cards"]:
        assert card["health"] == "placeholder_not_connected"
        assert card["clouds_can_claim_live_source"] is False
        assert card["clouds_can_grant_authority"] is False
        assert "source_contract_not_connected" in card["blocked_by"]

    assert payload["boundary"]["placeholder_is_visible"] is True
    assert payload["boundary"]["placeholder_is_not_connected"] is True
    assert payload["boundary"]["clouds_cannot_claim_live_source"] is True


def test_clouds_gp004_vault_live_status_uses_vault_summary():
    payload = get_clouds_vault_live_status_payload()

    assert payload["payload_type"] == "clouds_vault_live_status"
    assert payload["status"] == "ready"
    assert payload["source_app"] == "archive_vault"
    assert payload["live_status_card_count"] >= 6
    assert payload["vault_ready"] is True
    assert payload["vault_final_score"] == 100
    assert payload["clouds_view"] == "summary_only_redacted"
    assert "direct_upload_locked" in payload["intentional_locks"]

    card_ids = {card["card_id"] for card in payload["status_cards"]}
    assert "vault_live_readiness" in card_ids
    assert "vault_live_requirements" in card_ids
    assert "vault_live_receipts" in card_ids
    assert "vault_live_exports" in card_ids

    assert payload["boundary"]["vault_is_live_summary_source"] is True
    assert payload["boundary"]["clouds_reads_summary_only"] is True
    assert payload["boundary"]["clouds_does_not_unlock_vault"] is True


def test_clouds_gp004_dashboard_rolls_everything_up():
    payload = get_clouds_app_lane_status_dashboard_payload()

    assert payload["payload_type"] == "clouds_app_lane_status_dashboard"
    assert payload["status"] == "ready"
    assert payload["app_board"]["app_count"] >= 8
    assert payload["lane_board"]["lane_count"] >= 8
    assert payload["placeholder_health"]["placeholder_health_count"] >= 3
    assert payload["vault_live_status"]["live_status_card_count"] >= 6
    assert payload["vault_live_status"]["vault_ready"] is True
    assert payload["vault_live_status"]["vault_final_score"] == 100
    assert payload["prior_pack_status"]["gp001"] == "ready"
    assert payload["prior_pack_status"]["gp002"] == "ready"
    assert payload["prior_pack_status"]["gp003"] == "ready"
    assert len(payload["open_app_targets"]) >= 6

    assert payload["boundary"]["clouds_is_status_layer"] is True
    assert payload["boundary"]["clouds_is_not_system_of_record"] is True
    assert payload["boundary"]["summary_only_redacted"] is True
    assert payload["boundary"]["owning_apps_keep_authority"] is True


def test_clouds_gp004_status_is_ready_and_safe_to_continue():
    payload = get_clouds_gp004_status_payload()

    assert payload["payload_type"] == "clouds_gp004_status"
    assert payload["status"] == "ready"
    assert payload["pack"] == "The Clouds Giant Pack 004"
    assert payload["app_count"] >= 8
    assert payload["lane_count"] >= 8
    assert payload["placeholder_count"] >= 3
    assert payload["vault_live_status_card_count"] >= 6
    assert payload["vault_final_score"] == 100
    assert payload["prior_gp001_status"] == "ready"
    assert payload["prior_gp002_status"] == "ready"
    assert payload["prior_gp003_status"] == "ready"
    assert payload["clouds_is_status_layer"] is True
    assert payload["clouds_is_not_system_of_record"] is True
    assert payload["summary_only_redacted"] is True
    assert payload["safe_to_continue_to_clouds_gp005"] is True


def test_clouds_gp004_routes_template_and_css_exist():
    routes = Path("clouds/clouds_routes.py").read_text(encoding="utf-8")
    template = Path("templates/clouds_app_lane_status.html").read_text(encoding="utf-8")
    css = Path("static/clouds/clouds_app_lane_status.css").read_text(encoding="utf-8")

    assert "/clouds/app-lane-status" in routes
    assert "/clouds/app-status-board.json" in routes
    assert "/clouds/lane-status-board.json" in routes
    assert "/clouds/placeholder-health.json" in routes
    assert "/clouds/vault-live-status.json" in routes
    assert "/clouds/app-lane-status-dashboard.json" in routes
    assert "/clouds/gp004-status.json" in routes

    assert "See the whole board without stealing the controls." in template
    assert "Vault Live Status" in template
    assert "App Status Board" in template
    assert "Lane Status Board" in template
    assert "Placeholder Health" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()
