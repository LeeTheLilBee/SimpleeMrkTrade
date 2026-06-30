"""Vault Giant Pack 007 verification."""

from __future__ import annotations

import json
from pathlib import Path

from vault.vault_tracking_service import (
    get_data_freshness_wall_payload,
    get_expiration_renewal_wall_payload,
    get_requirement_tracker_payload,
    get_vault_gp007_status_payload,
    get_vault_search_index_payload,
    get_vault_search_tracker_payload,
)


def test_gp007_search_index_is_ready_and_covers_all_lanes():
    payload = get_vault_search_index_payload()
    json.dumps(payload)

    assert payload["app_id"] == "archive_vault"
    assert payload["payload_type"] == "vault_search_index"
    assert payload["status"] == "ready"
    assert payload["public_access"] is False
    assert payload["tower_guard"]["tower_required"] is True
    assert payload["boundary"]["direct_upload_allowed"] is False
    assert payload["record_count"] >= 45

    lanes = set(payload["filters"]["lanes"])
    assert {"atm", "property", "trust", "observatory", "soulaana", "beta"}.issubset(lanes)

    fields = set(payload["search_fields"])
    assert "record_id" in fields
    assert "title" in fields
    assert "blocked_reasons" in fields


def test_gp007_requirement_tracker_counts_requirements_and_blocked_items():
    payload = get_requirement_tracker_payload()

    assert payload["payload_type"] == "requirement_tracker"
    assert payload["status"] == "ready"
    assert payload["setup_score"] == 100
    assert payload["requirement_count"] >= 40
    assert payload["required_count"] >= 40
    assert payload["evidence_attached_count"] == 0
    assert payload["blocked_count"] >= 30
    assert payload["packet_completion_score"] == 0
    assert payload["boundary"]["raw_files_can_be_uploaded"] is False
    assert payload["boundary"]["tower_storage_clearance_required"] is True

    lane_summary = payload["lane_summary"]
    assert "atm" in lane_summary
    assert "property" in lane_summary
    assert "trust" in lane_summary
    assert "observatory" in lane_summary
    assert "soulaana" in lane_summary
    assert "beta" in lane_summary


def test_gp007_expiration_renewal_wall_is_ready():
    payload = get_expiration_renewal_wall_payload()

    assert payload["payload_type"] == "expiration_renewal_wall"
    assert payload["status"] == "ready"
    assert payload["renewal_item_count"] >= 40
    assert payload["expired_count"] == 0
    assert payload["expiring_soon_count"] == 0
    assert payload["expiration_not_set_count"] == payload["renewal_item_count"]
    assert payload["renewal_policy"]["ob_manual_live_proof_days"] == 7
    assert payload["renewal_policy"]["trust_entity_documents_days"] == 365


def test_gp007_data_freshness_wall_has_six_lanes():
    payload = get_data_freshness_wall_payload()

    assert payload["payload_type"] == "data_freshness_wall"
    assert payload["status"] == "ready"
    assert payload["lane_count"] == 6

    lanes = {lane["lane"] for lane in payload["freshness_lanes"]}
    assert lanes == {"atm", "property", "trust", "observatory", "soulaana", "beta"}

    assert payload["standard"]["freshness_required"] is True
    assert payload["standard"]["clouds_gets_staleness_summary_only"] is True


def test_gp007_combined_tracker_is_clouds_safe():
    payload = get_vault_search_tracker_payload()

    assert payload["payload_type"] == "vault_search_tracker"
    assert payload["status"] == "ready"
    assert payload["boundary"]["tower_guard_required"] is True
    assert payload["boundary"]["direct_upload_allowed"] is False
    assert payload["boundary"]["redacted_view_default"] is True
    assert payload["boundary"]["clouds_view"] == "summary_only_redacted"
    assert payload["boundary"]["search_reveals_sensitive_body"] is False

    clouds = payload["clouds_safe_source"]
    assert clouds["safe_for_clouds"] is True
    assert clouds["view"] == "summary_only_redacted"
    assert clouds["record_count"] >= 45
    assert clouds["requirement_count"] >= 40
    assert clouds["renewal_item_count"] >= 40
    assert clouds["freshness_lane_count"] == 6


def test_gp007_status_marks_safe_to_continue():
    status = get_vault_gp007_status_payload()

    assert status["status"] == "ready"
    assert status["pack"] == "Vault Giant Pack 007"
    assert status["search_record_count"] >= 45
    assert status["requirement_count"] >= 40
    assert status["blocked_requirement_count"] >= 30
    assert status["renewal_item_count"] >= 40
    assert status["freshness_lane_count"] == 6
    assert status["direct_upload_allowed"] is False
    assert status["clouds_safe"] is True
    assert status["safe_to_continue_to_gp008"] is True


def test_gp007_routes_template_and_css_exist():
    routes = Path("vault/vault_routes.py").read_text(encoding="utf-8")
    template = Path("templates/vault_search_tracker.html").read_text(encoding="utf-8")
    css = Path("static/vault/vault_search_tracker.css").read_text(encoding="utf-8")

    assert "/vault/search-tracker" in routes
    assert "/vault/search-tracker.json" in routes
    assert "/vault/search-index.json" in routes
    assert "/vault/requirement-tracker.json" in routes
    assert "/vault/expiration-renewal-wall.json" in routes
    assert "/vault/data-freshness-wall.json" in routes
    assert "/vault/gp007-status.json" in routes

    assert "Find it. Track it. Renew it before it goes stale." in template
    assert "Lane Requirement Wall" in template
    assert "Expiration + Renewal Wall" in template
    assert "Data Freshness Wall" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()
