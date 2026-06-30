"""The Clouds Giant Pack 006 verification."""

from __future__ import annotations

import json
from pathlib import Path

from clouds.clouds_mission_lane_service import (
    get_clouds_future_lane_slots_payload,
    get_clouds_gp006_status_payload,
    get_clouds_mission_lane_dashboard_payload,
    get_clouds_mission_lane_focus_payload,
    get_clouds_mission_lane_registry_payload,
    get_clouds_mission_lane_status_payload,
)


def test_clouds_gp006_mission_lane_registry_is_ready():
    payload = get_clouds_mission_lane_registry_payload()
    json.dumps(payload)

    assert payload["app_id"] == "clouds"
    assert payload["payload_type"] == "clouds_mission_lane_registry"
    assert payload["status"] == "ready"
    assert payload["mission_lane_count"] >= 9
    assert payload["vault_backed_lane_count"] >= 6
    assert payload["placeholder_lane_count"] >= 2
    assert payload["future_lane_count"] >= 1

    lane_ids = {lane["mission_lane_id"] for lane in payload["mission_lanes"]}
    assert "trust" in lane_ids
    assert "atm" in lane_ids
    assert "property" in lane_ids
    assert "observatory" in lane_ids
    assert "soulaana" in lane_ids
    assert "beta" in lane_ids
    assert "tower" in lane_ids
    assert "teller" in lane_ids
    assert "future_apps" in lane_ids

    assert payload["boundary"]["clouds_is_mission_dashboard"] is True
    assert payload["boundary"]["clouds_is_not_mission_owner"] is True
    assert payload["boundary"]["owning_apps_keep_authority"] is True
    assert payload["boundary"]["summary_only_redacted"] is True
    assert payload["boundary"]["future_slots_are_not_live_sources"] is True


def test_clouds_gp006_mission_lane_status_cards_are_ready():
    payload = get_clouds_mission_lane_status_payload()

    assert payload["payload_type"] == "clouds_mission_lane_status"
    assert payload["status"] == "ready"
    assert payload["mission_card_count"] >= 9
    assert payload["vault_backed_count"] >= 6
    assert payload["placeholder_count"] >= 2
    assert payload["future_count"] >= 1

    cards = {card["mission_lane_id"]: card for card in payload["mission_cards"]}
    assert cards["trust"]["setup_score"] == 100
    assert cards["atm"]["setup_score"] == 100
    assert cards["property"]["setup_score"] == 100
    assert cards["observatory"]["setup_score"] == 100
    assert cards["soulaana"]["setup_score"] == 100
    assert cards["beta"]["setup_score"] == 100
    assert cards["tower"]["status"] == "placeholder"
    assert cards["teller"]["status"] == "placeholder"
    assert cards["future_apps"]["status"] == "future"

    assert payload["supporting_summary"]["receipt_count"] >= 13
    assert payload["supporting_summary"]["locked_export_count"] >= 7
    assert payload["supporting_summary"]["today_focus_count"] >= 16

    assert payload["boundary"]["mission_status_is_summary_only"] is True
    assert payload["boundary"]["clouds_routes_to_owning_app"] is True
    assert payload["boundary"]["clouds_does_not_complete_lane_actions"] is True


def test_clouds_gp006_mission_lane_focus_is_ready():
    payload = get_clouds_mission_lane_focus_payload()

    assert payload["payload_type"] == "clouds_mission_lane_focus"
    assert payload["status"] == "ready"
    assert payload["lane_focus_count"] >= 9
    assert payload["placeholder_or_future_count"] >= 3
    assert payload["boundary"]["focus_is_visibility_only"] is True
    assert payload["boundary"]["clouds_routes_only"] is True
    assert payload["boundary"]["owning_apps_act"] is True

    lane_ids = {lane["mission_lane_id"] for lane in payload["lane_focus"]}
    assert "atm" in lane_ids
    assert "property" in lane_ids
    assert "soulaana" in lane_ids
    assert "beta" in lane_ids


def test_clouds_gp006_future_slots_are_reserved_not_live():
    payload = get_clouds_future_lane_slots_payload()

    assert payload["payload_type"] == "clouds_future_lane_slots"
    assert payload["status"] == "ready"
    assert payload["future_slot_count"] >= 5

    slot_ids = {slot["future_slot_id"] for slot in payload["future_slots"]}
    assert "luxe_laundromat" in slot_ids
    assert "simplee_farming" in slot_ids
    assert "simplee_grocery" in slot_ids
    assert "simplee_land" in slot_ids
    assert "simplee_skincare" in slot_ids

    assert payload["boundary"]["future_slots_are_not_live_apps"] is True
    assert payload["boundary"]["clouds_does_not_invent_operating_data"] is True
    assert payload["boundary"]["source_contract_required_before_live_status"] is True


def test_clouds_gp006_dashboard_rolls_up_mission_lanes():
    payload = get_clouds_mission_lane_dashboard_payload()

    assert payload["payload_type"] == "clouds_mission_lane_dashboard"
    assert payload["status"] == "ready"
    assert payload["mission_registry"]["mission_lane_count"] >= 9
    assert payload["mission_registry"]["vault_backed_lane_count"] >= 6
    assert payload["mission_status"]["mission_card_count"] >= 9
    assert payload["future_slots"]["future_slot_count"] >= 5
    assert payload["vault_summary"]["final_score"] == 100
    assert payload["vault_summary"]["safe_to_start_clouds"] is True
    assert payload["today_summary"]["focus_count"] >= 16
    assert payload["prior_pack_status"]["gp001"] == "ready"
    assert payload["prior_pack_status"]["gp002"] == "ready"
    assert payload["prior_pack_status"]["gp003"] == "ready"
    assert payload["prior_pack_status"]["gp004"] == "ready"
    assert payload["prior_pack_status"]["gp005"] == "ready"

    assert payload["boundary"]["clouds_is_mission_visibility_layer"] is True
    assert payload["boundary"]["clouds_is_not_operating_app"] is True
    assert payload["boundary"]["summary_only_redacted"] is True
    assert payload["boundary"]["owning_apps_keep_authority"] is True
    assert payload["boundary"]["future_slots_not_live"] is True


def test_clouds_gp006_status_is_ready_and_safe_to_continue():
    payload = get_clouds_gp006_status_payload()

    assert payload["payload_type"] == "clouds_gp006_status"
    assert payload["status"] == "ready"
    assert payload["pack"] == "The Clouds Giant Pack 006"
    assert payload["mission_lane_count"] >= 9
    assert payload["vault_backed_lane_count"] >= 6
    assert payload["placeholder_lane_count"] >= 2
    assert payload["future_lane_count"] >= 1
    assert payload["mission_card_count"] >= 9
    assert payload["future_slot_count"] >= 5
    assert payload["vault_final_score"] == 100
    assert payload["prior_gp001_status"] == "ready"
    assert payload["prior_gp002_status"] == "ready"
    assert payload["prior_gp003_status"] == "ready"
    assert payload["prior_gp004_status"] == "ready"
    assert payload["prior_gp005_status"] == "ready"
    assert payload["clouds_is_mission_visibility_layer"] is True
    assert payload["clouds_is_not_operating_app"] is True
    assert payload["summary_only_redacted"] is True
    assert payload["safe_to_continue_to_clouds_gp007"] is True


def test_clouds_gp006_routes_template_and_css_exist():
    routes = Path("clouds/clouds_routes.py").read_text(encoding="utf-8")
    template = Path("templates/clouds_mission_lanes.html").read_text(encoding="utf-8")
    css = Path("static/clouds/clouds_mission_lanes.css").read_text(encoding="utf-8")

    assert "/clouds/mission-lanes" in routes
    assert "/clouds/mission-lane-registry.json" in routes
    assert "/clouds/mission-lane-status.json" in routes
    assert "/clouds/mission-lane-focus.json" in routes
    assert "/clouds/future-lane-slots.json" in routes
    assert "/clouds/mission-lane-dashboard.json" in routes
    assert "/clouds/gp006-status.json" in routes

    assert "Every mission in its lane." in template
    assert "Mission Lane Status" in template
    assert "Mission Focus" in template
    assert "Future Lane Slots" in template
    assert "Open-App Handoff" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()
