"""Vault Giant Pack 005 verification."""

from __future__ import annotations

import json
from pathlib import Path

from vault.vault_soulaana_beta_service import (
    get_private_beta_onboarding_vault_payload,
    get_soulaana_artist_ip_vault_payload,
    get_soulaana_beta_owner_queue_payload,
    get_soulaana_beta_vault_payload,
    get_vault_gp005_status_payload,
)


def test_gp005_soulaana_artist_ip_vault_is_ready_and_blocks_ai_character_art():
    payload = get_soulaana_artist_ip_vault_payload()
    json.dumps(payload)

    assert payload["tower_guard"]["tower_required"] is True
    assert payload["vault_id"] == "vault_soulaana_artist_ip_package"
    assert payload["business_lane"] == "soulaana"
    assert payload["status"] == "ready"
    assert payload["readiness"]["setup_score"] == 100
    assert len(payload["reserved_art_slots"]) >= 4
    assert len(payload["package_records"]) >= 6
    assert len(payload["ip_receipt_chain"]) >= 6

    boundary = payload["creative_boundary"]
    assert boundary["human_artist_only"] is True
    assert boundary["ai_generated_black_women_or_soulaana_character_art_allowed"] is False
    assert "reserved_art_slot" in boundary["allowed_preview_assets"]
    assert "ai_generated_black_woman_depiction" in boundary["blocked_preview_assets"]
    assert boundary["direct_upload_allowed"] is False


def test_gp005_private_beta_vault_is_tower_controlled():
    payload = get_private_beta_onboarding_vault_payload()
    json.dumps(payload)

    assert payload["tower_guard"]["tower_required"] is True
    assert payload["vault_id"] == "vault_private_beta_onboarding"
    assert payload["business_lane"] == "beta"
    assert payload["status"] == "ready"
    assert payload["readiness"]["setup_score"] == 100
    assert len(payload["onboarding_records"]) >= 6
    assert len(payload["access_boundaries"]) >= 7
    assert len(payload["onboarding_flow"]) >= 6

    boundary = payload["access_boundary"]
    assert boundary["invite_only"] is True
    assert boundary["nda_required"] is True
    assert boundary["tower_clearance_required"] is True
    assert boundary["vault_owns_permissions"] is False
    assert boundary["tower_owns_permissions"] is True
    assert boundary["public_beta_routes_allowed"] is False


def test_gp005_owner_queue_has_soulaana_beta_and_clouds_actions():
    queue = get_soulaana_beta_owner_queue_payload()

    assert queue["action_count"] >= 6
    assert queue["critical_count"] >= 2
    assert queue["high_count"] >= 3

    action_ids = {action["action_id"] for action in queue["actions"]}
    assert "soulaana_artist_scope_ready" in action_ids
    assert "soulaana_no_ai_character_art_boundary" in action_ids
    assert "soulaana_ip_receipt_chain_ready" in action_ids
    assert "beta_invite_packet_ready" in action_ids
    assert "beta_tower_clearance_required" in action_ids
    assert "clouds_soulaana_beta_summary_ready" in action_ids


def test_gp005_combined_clouds_source_is_summary_only_and_safe():
    payload = get_soulaana_beta_vault_payload()

    assert payload["status"] == "ready"
    assert payload["boundary"]["tower_permission_required"] is True
    assert payload["boundary"]["direct_upload_allowed"] is False
    assert payload["boundary"]["public_beta_routes_allowed"] is False
    assert payload["boundary"]["vault_owns_beta_permissions"] is False
    assert payload["boundary"]["tower_owns_beta_permissions"] is True
    assert payload["boundary"]["ai_generated_character_art_allowed"] is False
    assert payload["boundary"]["reserved_art_slots_only_until_artist_delivery"] is True

    clouds = payload["clouds_safe_source"]
    assert clouds["safe_for_clouds"] is True
    assert clouds["view"] == "summary_only_redacted"
    assert len(clouds["summaries"]) == 2
    assert "artist_payment_details" in clouds["hidden_sensitive_fields"]
    assert "nda_body" in clouds["hidden_sensitive_fields"]
    assert "ai_generated_character_art_blocked" in clouds["blocked_reasons"]
    assert "public_beta_routes_blocked" in clouds["blocked_reasons"]
    assert "vault_permission_authority_blocked" in clouds["blocked_reasons"]


def test_gp005_status_marks_safe_to_continue():
    status = get_vault_gp005_status_payload()

    assert status["status"] == "ready"
    assert status["pack"] == "Vault Giant Pack 005"
    assert status["soulaana_package_record_count"] >= 6
    assert status["soulaana_reserved_art_slot_count"] >= 4
    assert status["soulaana_receipt_count"] >= 6
    assert status["beta_onboarding_record_count"] >= 6
    assert status["beta_access_boundary_count"] >= 7
    assert status["soulaana_setup_score"] == 100
    assert status["beta_setup_score"] == 100
    assert status["direct_upload_allowed"] is False
    assert status["ai_generated_character_art_allowed"] is False
    assert status["vault_owns_beta_permissions"] is False
    assert status["safe_to_continue_to_gp006"] is True


def test_gp005_routes_template_and_css_exist():
    routes = Path("vault/vault_routes.py").read_text(encoding="utf-8")
    template = Path("templates/vault_soulaana_beta.html").read_text(encoding="utf-8")
    css = Path("static/vault/vault_soulaana_beta.css").read_text(encoding="utf-8")

    assert "/vault/soulaana-beta" in routes
    assert "/vault/soulaana-beta-vault.json" in routes
    assert "/vault/soulaana-artist-ip-vault.json" in routes
    assert "/vault/private-beta-onboarding-vault.json" in routes
    assert "/vault/gp005-status.json" in routes

    assert "Art slots reserved" in template
    assert "AI Character Art" in template
    assert "Beta Access" in template
    assert "Clouds Safe Soulaana + Beta Source" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()
