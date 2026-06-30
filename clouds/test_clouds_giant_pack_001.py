"""The Clouds Giant Pack 001 verification."""

from __future__ import annotations

import json
from pathlib import Path

from clouds.clouds_service import (
    get_clouds_command_dashboard_payload,
    get_clouds_gp001_status_payload,
    get_clouds_source_map_payload,
    get_clouds_status_payload,
    get_clouds_vault_summary_payload,
)


def test_clouds_gp001_source_map_uses_vault_handoff_safely():
    payload = get_clouds_source_map_payload()
    json.dumps(payload)

    assert payload["app_id"] == "clouds"
    assert payload["status"] == "ready"
    assert payload["source_count"] >= 6
    assert payload["first_source_app"] == "archive_vault"
    assert payload["vault_handoff_status"] == "ready"
    assert payload["vault_handoff_view"] == "summary_only_redacted"
    assert payload["boundary"]["summary_only"] is True
    assert payload["boundary"]["redacted"] is True
    assert payload["boundary"]["tower_guard_required"] is True
    assert payload["boundary"]["clouds_owns_permissions"] is False
    assert payload["boundary"]["clouds_owns_documents"] is False
    assert payload["boundary"]["clouds_owns_exports"] is False
    assert payload["boundary"]["clouds_owns_execution"] is False
    assert "display_unredacted_document_body" in payload["clouds_must_not_do"]
    assert "show_vault_readiness" in payload["clouds_may_do"]


def test_clouds_gp001_vault_summary_reads_final_vault_state():
    payload = get_clouds_vault_summary_payload()

    assert payload["payload_type"] == "clouds_vault_summary"
    assert payload["status"] == "ready"
    assert payload["summary_only"] is True
    assert payload["redacted"] is True
    assert payload["vault"]["final_score"] == 100
    assert payload["vault"]["safe_to_start_clouds"] is True
    assert payload["vault"]["clouds_view"] == "summary_only_redacted"
    assert payload["vault"]["lane_count"] == 6
    assert payload["vault"]["search_record_count"] >= 45
    assert payload["vault"]["requirement_count"] >= 40
    assert payload["vault"]["receipt_count"] >= 13
    assert payload["vault"]["locked_export_count"] >= 7
    assert len(payload["open_app_targets"]) >= 5


def test_clouds_gp001_dashboard_has_cards_boundaries_and_owner_focus():
    payload = get_clouds_command_dashboard_payload()

    assert payload["payload_type"] == "clouds_command_dashboard"
    assert payload["status"] == "ready"
    assert payload["mode"] == "owner_command_foundation"
    assert payload["source_count"] >= 6
    assert payload["card_count"] >= 8
    assert payload["boundary_count"] >= 6
    assert payload["vault_summary"]["final_score"] == 100
    assert len(payload["owner_focus"]) >= 6
    assert len(payload["open_app_targets"]) >= 5
    assert "vault" in payload["foundation_lanes"]
    assert "tower" in payload["foundation_lanes"]
    assert "observatory" in payload["foundation_lanes"]
    assert "teller" in payload["foundation_lanes"]

    boundary_ids = {boundary["boundary_id"] for boundary in payload["boundaries"]}
    assert "clouds_not_tower" in boundary_ids
    assert "clouds_not_vault" in boundary_ids
    assert "clouds_not_ob" in boundary_ids
    assert "clouds_not_teller" in boundary_ids
    assert "summary_only_redacted" in boundary_ids


def test_clouds_gp001_status_is_ready_and_safe_to_continue():
    payload = get_clouds_status_payload()

    assert payload["payload_type"] == "clouds_status"
    assert payload["status"] == "ready"
    assert payload["pack"] == "The Clouds Giant Pack 001"
    assert payload["dashboard_status"] == "ready"
    assert payload["source_count"] >= 6
    assert payload["card_count"] >= 8
    assert payload["boundary_count"] >= 6
    assert payload["vault_final_score"] == 100
    assert payload["vault_safe_to_start_clouds"] is True
    assert payload["clouds_view"] == "summary_only_redacted"
    assert payload["clouds_owns_permissions"] is False
    assert payload["clouds_owns_documents"] is False
    assert payload["clouds_owns_execution"] is False
    assert payload["clouds_owns_exports"] is False
    assert payload["safe_to_continue_to_clouds_gp002"] is True


def test_clouds_gp001_status_alias_matches_status():
    alias_payload = get_clouds_gp001_status_payload()
    status_payload = get_clouds_status_payload()

    alias_payload.pop("generated_at", None)
    status_payload.pop("generated_at", None)

    assert alias_payload == status_payload


def test_clouds_gp001_routes_template_and_css_exist():
    routes = Path("clouds/clouds_routes.py").read_text(encoding="utf-8")
    template = Path("templates/clouds_home.html").read_text(encoding="utf-8")
    css = Path("static/clouds/clouds.css").read_text(encoding="utf-8")

    assert "/clouds" in routes
    assert "/the-clouds" in routes
    assert "/clouds/status.json" in routes
    assert "/clouds/source-map.json" in routes
    assert "/clouds/vault-summary.json" in routes
    assert "/clouds/dashboard.json" in routes
    assert "/clouds/gp001-status.json" in routes

    assert "Owner command dashboard." in template
    assert "Vault Source" in template
    assert "Clouds Boundaries" in template
    assert "Open-App Handoff" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()


def test_web_app_registration_marker_exists_when_app_file_is_present():
    app_file = Path("web/app.py")
    if app_file.exists():
        text = app_file.read_text(encoding="utf-8")
        assert "CLOUDS GIANT PACK 001 ROUTES START" in text
        assert "clouds_bp" in text
