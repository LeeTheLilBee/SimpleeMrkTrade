"""The Clouds Giant Pack 002 verification."""

from __future__ import annotations

import json
from pathlib import Path

from clouds.clouds_app_registry_service import (
    get_clouds_app_registry_dashboard_payload,
    get_clouds_app_registry_payload,
    get_clouds_authority_map_payload,
    get_clouds_gp002_status_payload,
    get_clouds_placeholder_sources_payload,
)


def test_clouds_gp002_app_registry_is_ready_and_contains_core_apps():
    payload = get_clouds_app_registry_payload()
    json.dumps(payload)

    assert payload["app_id"] == "clouds"
    assert payload["payload_type"] == "clouds_app_registry"
    assert payload["status"] == "ready"
    assert payload["public_access"] is False
    assert payload["registered_app_count"] >= 8
    assert payload["ready_app_count"] >= 5
    assert payload["locked_placeholder_count"] >= 3

    app_ids = {app["registered_app_id"] for app in payload["apps"]}
    assert "archive_vault" in app_ids
    assert "tower" in app_ids
    assert "observatory" in app_ids
    assert "teller" in app_ids
    assert "simplee_on_the_go" in app_ids
    assert "simplee_property" in app_ids
    assert "soulaana" in app_ids
    assert "private_beta" in app_ids

    assert payload["registry_boundary"]["clouds_is_registry_not_authority"] is True
    assert payload["registry_boundary"]["owning_app_keeps_authority"] is True
    assert payload["registry_boundary"]["tower_keeps_permissions"] is True
    assert payload["registry_boundary"]["summary_only_redacted"] is True


def test_clouds_gp002_placeholders_are_visible_but_not_connected():
    payload = get_clouds_placeholder_sources_payload()

    assert payload["payload_type"] == "clouds_placeholder_sources"
    assert payload["status"] == "ready"
    assert payload["placeholder_count"] >= 3

    placeholders = set(payload["placeholder_apps"])
    assert "tower" in placeholders
    assert "observatory" in placeholders
    assert "teller" in placeholders

    assert payload["boundary"]["placeholder_does_not_mean_connected"] is True
    assert payload["boundary"]["placeholder_does_not_grant_authority"] is True
    assert payload["boundary"]["clouds_must_wait_for_source_contract"] is True
    assert payload["boundary"]["owner_can_see_future_slot"] is True


def test_clouds_gp002_authority_map_keeps_clouds_in_its_lane():
    payload = get_clouds_authority_map_payload()

    assert payload["payload_type"] == "clouds_authority_map"
    assert payload["status"] == "ready"
    assert payload["authority_row_count"] >= 5
    assert payload["boundary"]["clouds_is_command_layer"] is True
    assert payload["boundary"]["clouds_is_not_system_of_record"] is True
    assert payload["boundary"]["clouds_routes_to_owning_app"] is True

    authority_ids = {row["authority_id"] for row in payload["authority_rows"]}
    assert "tower_authority" in authority_ids
    assert "vault_authority" in authority_ids
    assert "ob_authority" in authority_ids
    assert "teller_authority" in authority_ids
    assert "clouds_authority" in authority_ids


def test_clouds_gp002_dashboard_rolls_up_registry():
    payload = get_clouds_app_registry_dashboard_payload()

    assert payload["payload_type"] == "clouds_app_registry_dashboard"
    assert payload["status"] == "ready"
    assert payload["registered_app_count"] >= 8
    assert payload["ready_app_count"] >= 5
    assert payload["locked_placeholder_count"] >= 3
    assert payload["placeholder_count"] >= 3
    assert payload["authority_row_count"] >= 5
    assert payload["app_card_count"] >= 8
    assert payload["gp001_status"]["status"] == "ready"
    assert payload["gp001_status"]["vault_final_score"] == 100
    assert payload["gp001_dashboard_card_count"] >= 8

    card_ids = {card["card_id"] for card in payload["app_cards"]}
    assert "clouds_app_archive_vault" in card_ids
    assert "clouds_app_tower" in card_ids
    assert "clouds_app_observatory" in card_ids
    assert "clouds_app_teller" in card_ids


def test_clouds_gp002_status_is_ready_and_safe_to_continue():
    payload = get_clouds_gp002_status_payload()

    assert payload["payload_type"] == "clouds_gp002_status"
    assert payload["status"] == "ready"
    assert payload["pack"] == "The Clouds Giant Pack 002"
    assert payload["registered_app_count"] >= 8
    assert payload["ready_app_count"] >= 5
    assert payload["locked_placeholder_count"] >= 3
    assert payload["placeholder_count"] >= 3
    assert payload["authority_row_count"] >= 5
    assert payload["app_card_count"] >= 8
    assert payload["clouds_owns_permissions"] is False
    assert payload["clouds_is_system_of_record"] is False
    assert payload["summary_only_redacted"] is True
    assert payload["safe_to_continue_to_clouds_gp003"] is True


def test_clouds_gp002_routes_template_and_css_exist():
    routes = Path("clouds/clouds_routes.py").read_text(encoding="utf-8")
    template = Path("templates/clouds_app_registry.html").read_text(encoding="utf-8")
    css = Path("static/clouds/clouds_app_registry.css").read_text(encoding="utf-8")

    assert "/clouds/app-registry" in routes
    assert "/clouds/app-registry.json" in routes
    assert "/clouds/placeholder-sources.json" in routes
    assert "/clouds/authority-map.json" in routes
    assert "/clouds/app-registry-dashboard.json" in routes
    assert "/clouds/gp002-status.json" in routes

    assert "Every app gets a place. Authority stays where it belongs." in template
    assert "Authority Map" in template
    assert "Placeholder Sources" in template
    assert "Open-App Handoff" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()
