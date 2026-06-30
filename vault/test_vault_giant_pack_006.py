"""Vault Giant Pack 006 verification."""

from __future__ import annotations

import json
from pathlib import Path

from vault.vault_command_center_service import (
    get_unified_vault_command_center_payload,
    get_vault_gp006_status_payload,
)


def test_gp006_command_center_is_ready_and_json_serializable():
    payload = get_unified_vault_command_center_payload()
    json.dumps(payload)

    assert payload["app_id"] == "archive_vault"
    assert payload["payload_type"] == "unified_vault_command_center"
    assert payload["command_center_status"] == "ready"
    assert payload["command_level"] == "six_lane_foundation_ready"
    assert payload["public_access"] is False
    assert payload["private_invite_only"] is True
    assert payload["tower_guard"]["tower_required"] is True
    assert payload["tower_guard"]["vault_owns_permissions"] is False


def test_gp006_has_all_six_lane_cards():
    payload = get_unified_vault_command_center_payload()
    lanes = {card["lane_id"] for card in payload["lane_cards"]}

    assert payload["lane_count"] == 6
    assert lanes == {"atm", "property", "trust", "observatory", "soulaana", "beta"}

    for card in payload["lane_cards"]:
        assert card["setup_score"] == 100
        assert card["record_count"] >= 1
        assert card["tower_guard_required"] is True
        assert card["direct_upload_allowed"] is False
        assert card["redacted_view_default"] is True
        assert card["clouds_view"] == "summary_only_redacted"


def test_gp006_boundary_wall_keeps_dangerous_doors_locked():
    payload = get_unified_vault_command_center_payload()
    boundary = payload["boundary_wall"]

    assert boundary["tower_permission_required"] is True
    assert boundary["vault_owns_permissions"] is False
    assert boundary["direct_upload_allowed"] is False
    assert boundary["redacted_view_default"] is True
    assert boundary["clouds_view"] == "summary_only_redacted"
    assert boundary["broker_secrets_allowed"] is False
    assert boundary["auto_execution_allowed"] is False
    assert boundary["public_proof_allowed"] is False
    assert boundary["public_beta_routes_allowed"] is False
    assert boundary["ai_generated_character_art_allowed"] is False
    assert boundary["bank_account_details_hidden"] is True
    assert boundary["beneficiary_details_hidden"] is True

    assert "direct_upload_locked" in boundary["blocked_reasons"]
    assert "public_proof_blocked" in boundary["blocked_reasons"]
    assert "ai_generated_character_art_blocked" in boundary["blocked_reasons"]
    assert "public_beta_routes_blocked" in boundary["blocked_reasons"]


def test_gp006_owner_focus_queue_is_consolidated():
    payload = get_unified_vault_command_center_payload()

    assert payload["owner_action_count"] >= 20
    assert payload["critical_owner_action_count"] >= 6
    assert payload["high_owner_action_count"] >= 10

    sources = {action["source"] for action in payload["owner_focus_queue"]}
    assert {"vault_room", "acquisition", "trust_ob", "soulaana_beta"}.issubset(sources)


def test_gp006_route_index_covers_all_vault_rooms_and_json_sources():
    payload = get_unified_vault_command_center_payload()
    routes = {route["route"] for route in payload["route_index"]}

    assert payload["route_count"] >= 16
    assert "/vault" in routes
    assert "/vault/command-center" in routes
    assert "/vault/acquisition-builders" in routes
    assert "/vault/trust-ob" in routes
    assert "/vault/soulaana-beta" in routes
    assert "/vault/command-center.json" in routes
    assert "/vault/atm-route-builder.json" in routes
    assert "/vault/apartment-lender-builder.json" in routes
    assert "/vault/trust-entity-vault.json" in routes
    assert "/vault/ob-manual-live-proof-vault.json" in routes
    assert "/vault/soulaana-artist-ip-vault.json" in routes
    assert "/vault/private-beta-onboarding-vault.json" in routes


def test_gp006_clouds_source_map_is_summary_only_and_redacted():
    payload = get_unified_vault_command_center_payload()
    clouds = payload["clouds_safe_source_map"]

    assert clouds["safe_for_clouds"] is True
    assert clouds["view"] == "summary_only_redacted"
    assert len(clouds["lane_summaries"]) == 6
    assert "/vault/command-center.json" in clouds["source_routes"]
    assert "bank_account_numbers" in clouds["hidden_sensitive_fields"]
    assert "broker_credentials" in clouds["hidden_sensitive_fields"]
    assert "artist_payment_details" in clouds["hidden_sensitive_fields"]
    assert "nda_body" in clouds["hidden_sensitive_fields"]


def test_gp006_status_marks_safe_to_continue():
    status = get_vault_gp006_status_payload()

    assert status["status"] == "ready"
    assert status["pack"] == "Vault Giant Pack 006"
    assert status["lane_count"] == 6
    assert status["route_count"] >= 16
    assert status["owner_action_count"] >= 20
    assert status["readiness_score"] == 100
    assert status["command_level"] == "six_lane_foundation_ready"
    assert status["direct_upload_allowed"] is False
    assert status["vault_owns_permissions"] is False
    assert status["clouds_safe"] is True
    assert status["safe_to_continue_to_gp007"] is True


def test_gp006_routes_template_and_css_exist():
    routes = Path("vault/vault_routes.py").read_text(encoding="utf-8")
    template = Path("templates/vault_command_center.html").read_text(encoding="utf-8")
    css = Path("static/vault/vault_command_center.css").read_text(encoding="utf-8")

    assert "/vault/command-center" in routes
    assert "/vault/command-center.json" in routes
    assert "/vault/gp006-status.json" in routes

    assert "Six lanes. One Vault command wall." in template
    assert "Six-Lane Readiness Wall" in template
    assert "Boundary Wall" in template
    assert "Owner Focus Queue" in template
    assert "Clouds Safe Source Map" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()
