"""Vault Giant Pack 003 verification."""

from __future__ import annotations

import json
from pathlib import Path

from vault.vault_acquisition_service import (
    get_acquisition_builders_payload,
    get_acquisition_owner_queue_payload,
    get_apartment_lender_builder_payload,
    get_atm_route_builder_payload,
    get_vault_gp003_status_payload,
)


def test_gp003_atm_builder_is_ready_but_packet_empty():
    payload = get_atm_route_builder_payload()
    json.dumps(payload)

    builder = payload["builder"]
    assert payload["tower_guard"]["tower_required"] is True
    assert builder["builder_id"] == "builder_atm_route_acquisition"
    assert builder["business_lane"] == "atm"
    assert builder["readiness"]["builder_setup_score"] == 100
    assert builder["readiness"]["packet_completion_score"] == 0
    assert builder["readiness"]["required_document_count"] >= 8
    assert builder["direct_upload_allowed"] is False
    assert "starting_vault_cash_needed" in builder["vault_cash_plan_fields"]


def test_gp003_apartment_builder_is_ready_but_packet_empty():
    payload = get_apartment_lender_builder_payload()
    json.dumps(payload)

    builder = payload["builder"]
    assert payload["tower_guard"]["tower_required"] is True
    assert builder["builder_id"] == "builder_apartment_lender_due_diligence"
    assert builder["business_lane"] == "property"
    assert builder["readiness"]["builder_setup_score"] == 100
    assert builder["readiness"]["packet_completion_score"] == 0
    assert builder["readiness"]["required_document_count"] >= 8
    assert builder["direct_upload_allowed"] is False
    assert "rent_roll_summary" in builder["lender_packet_fields"]


def test_gp003_builders_payload_exposes_both_money_lanes_to_clouds_safely():
    payload = get_acquisition_builders_payload()
    summaries = payload["clouds_safe_source"]["builder_summaries"]

    assert payload["status"] == "ready"
    assert payload["builder_count"] == 2
    assert payload["boundary"]["direct_upload_allowed"] is False
    assert payload["boundary"]["tower_permission_required"] is True
    assert payload["clouds_safe_source"]["safe_for_clouds"] is True
    assert payload["clouds_safe_source"]["view"] == "summary_only_redacted"

    lanes = {summary["business_lane"] for summary in summaries}
    assert lanes == {"atm", "property"}
    assert "bank_account_details" in payload["clouds_safe_source"]["hidden_sensitive_fields"]
    assert "raw_direct_file_upload" in payload["clouds_safe_source"]["blocked_reasons"]


def test_gp003_owner_queue_has_atm_property_and_lock_actions():
    queue = get_acquisition_owner_queue_payload()

    assert queue["action_count"] >= 5
    assert queue["critical_count"] >= 2
    assert queue["high_count"] >= 3

    action_ids = {action["action_id"] for action in queue["actions"]}
    assert "acq_owner_choose_first_atm_targets" in action_ids
    assert "acq_owner_confirm_atm_vault_cash_path" in action_ids
    assert "acq_owner_start_apartment_target_watch" in action_ids
    assert "acq_owner_keep_upload_locked" in action_ids

    lock_action = next(action for action in queue["actions"] if action["action_id"] == "acq_owner_keep_upload_locked")
    assert "direct_upload_locked" in lock_action["blocked_by"]


def test_gp003_status_marks_safe_to_continue_to_gp004():
    status = get_vault_gp003_status_payload()

    assert status["status"] == "ready"
    assert status["pack"] == "Vault Giant Pack 003"
    assert status["builder_count"] == 2
    assert status["atm_builder_setup_score"] == 100
    assert status["apartment_builder_setup_score"] == 100
    assert status["direct_upload_allowed"] is False
    assert status["safe_to_continue_to_gp004"] is True


def test_gp003_routes_and_template_exist():
    routes = Path("vault/vault_routes.py").read_text(encoding="utf-8")
    template = Path("templates/vault_acquisition_builders.html").read_text(encoding="utf-8")
    css = Path("static/vault/vault_acquisition.css").read_text(encoding="utf-8")

    assert "/vault/acquisition-builders" in routes
    assert "/vault/acquisition-builders.json" in routes
    assert "/vault/atm-route-builder.json" in routes
    assert "/vault/apartment-lender-builder.json" in routes
    assert "/vault/gp003-status.json" in routes

    assert "ATM route builder" in template
    assert "Apartment lender builder" in template
    assert "Direct Upload" in template
    assert "Tower Guard" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()
