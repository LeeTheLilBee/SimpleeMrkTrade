"""Vault Giant Pack 009 verification."""

from __future__ import annotations

import json
from pathlib import Path

from vault.vault_export_service import (
    get_export_lock_console_payload,
    get_export_preview_center_payload,
    get_external_access_review_payload,
    get_packet_export_request_queue_payload,
    get_redacted_packet_preview_payload,
    get_vault_gp009_status_payload,
)


def test_gp009_export_lock_console_is_ready_and_locked_by_default():
    payload = get_export_lock_console_payload()
    json.dumps(payload)

    assert payload["app_id"] == "archive_vault"
    assert payload["payload_type"] == "export_lock_console"
    assert payload["status"] == "ready"
    assert payload["public_access"] is False
    assert payload["tower_guard"]["tower_required"] is True
    assert payload["export_record_count"] >= 8
    assert payload["locked_export_count"] >= 7
    assert payload["summary_allowed_count"] >= 1
    assert payload["step_up_required_count"] >= 7
    assert payload["tower_clearance_required_count"] == payload["export_record_count"]
    assert payload["owner_approval_required_count"] >= 7
    assert payload["boundary"]["exports_locked_by_default"] is True
    assert payload["boundary"]["direct_upload_allowed"] is False
    assert payload["boundary"]["unredacted_export_allowed"] is False
    assert payload["boundary"]["clouds_summary_allowed"] is True


def test_gp009_redacted_packet_preview_has_all_six_lanes_and_hidden_fields():
    payload = get_redacted_packet_preview_payload()

    assert payload["payload_type"] == "redacted_packet_preview"
    assert payload["status"] == "ready"
    assert payload["preview_count"] == 6

    lanes = set(payload["preview_lanes"])
    assert lanes == {"atm", "property", "trust", "observatory", "soulaana", "beta"}

    assert payload["hidden_field_count"] >= 25
    assert "broker_credentials" in payload["hidden_fields"]
    assert "bank_account_numbers" in payload["hidden_fields"]
    assert "nda_body" in payload["hidden_fields"]
    assert "artist_payment_details" in payload["hidden_fields"]

    assert payload["boundary"]["redacted_preview_available"] is True
    assert payload["boundary"]["unredacted_preview_allowed"] is False
    assert payload["boundary"]["export_allowed_from_preview"] is False
    assert payload["boundary"]["watermark_required"] is True
    assert payload["boundary"]["sensitive_body_hidden"] is True


def test_gp009_export_request_queue_does_not_equal_approval():
    payload = get_packet_export_request_queue_payload()

    assert payload["payload_type"] == "packet_export_request_queue"
    assert payload["status"] == "ready"
    assert payload["request_count"] >= 8
    assert payload["not_requested_count"] >= 7
    assert payload["summary_handoff_allowed_count"] >= 1
    assert payload["boundary"]["request_does_not_equal_approval"] is True
    assert payload["boundary"]["tower_clearance_required"] is True
    assert payload["boundary"]["approval_chain_required"] is True
    assert payload["boundary"]["direct_upload_allowed"] is False


def test_gp009_external_access_review_is_default_deny():
    payload = get_external_access_review_payload()

    assert payload["payload_type"] == "external_access_review"
    assert payload["status"] == "ready"
    assert payload["review_item_count"] >= 5
    assert payload["policy_count"] >= 5
    assert payload["locked_export_count"] >= 7
    assert payload["boundary"]["external_access_default_deny"] is True
    assert payload["boundary"]["tower_clearance_required"] is True
    assert payload["boundary"]["expiration_required"] is True
    assert payload["boundary"]["revocation_supported"] is True
    assert payload["boundary"]["redacted_only_by_default"] is True


def test_gp009_export_preview_center_is_clouds_safe():
    payload = get_export_preview_center_payload()

    assert payload["payload_type"] == "export_preview_center"
    assert payload["status"] == "ready"
    assert payload["boundary"]["exports_locked_by_default"] is True
    assert payload["boundary"]["direct_upload_allowed"] is False
    assert payload["boundary"]["unredacted_export_allowed"] is False
    assert payload["boundary"]["external_access_default_deny"] is True
    assert payload["boundary"]["tower_guard_required"] is True
    assert payload["boundary"]["redacted_preview_only"] is True
    assert payload["boundary"]["clouds_view"] == "summary_only_redacted"

    clouds = payload["clouds_safe_source"]
    assert clouds["safe_for_clouds"] is True
    assert clouds["view"] == "summary_only_redacted"
    assert clouds["export_record_count"] >= 8
    assert clouds["locked_export_count"] >= 7
    assert clouds["preview_count"] == 6
    assert clouds["request_count"] >= 8
    assert clouds["external_review_item_count"] >= 5
    assert "export_locked" in clouds["blocked_reasons"]
    assert "unredacted_export_blocked" in clouds["blocked_reasons"]


def test_gp009_status_marks_safe_to_continue():
    status = get_vault_gp009_status_payload()

    assert status["status"] == "ready"
    assert status["pack"] == "Vault Giant Pack 009"
    assert status["export_record_count"] >= 8
    assert status["locked_export_count"] >= 7
    assert status["redacted_preview_count"] == 6
    assert status["export_request_count"] >= 8
    assert status["external_review_item_count"] >= 5
    assert status["direct_upload_allowed"] is False
    assert status["unredacted_export_allowed"] is False
    assert status["external_access_default_deny"] is True
    assert status["clouds_safe"] is True
    assert status["safe_to_continue_to_gp010"] is True


def test_gp009_routes_template_and_css_exist():
    routes = Path("vault/vault_routes.py").read_text(encoding="utf-8")
    template = Path("templates/vault_export_preview.html").read_text(encoding="utf-8")
    css = Path("static/vault/vault_export_preview.css").read_text(encoding="utf-8")

    assert "/vault/export-preview" in routes
    assert "/vault/export-preview-center.json" in routes
    assert "/vault/export-lock-console.json" in routes
    assert "/vault/redacted-packet-preview.json" in routes
    assert "/vault/packet-export-request-queue.json" in routes
    assert "/vault/external-access-review.json" in routes
    assert "/vault/gp009-status.json" in routes

    assert "Preview safely. Export only after approval." in template
    assert "Export Lock Console" in template
    assert "Redacted Packet Preview" in template
    assert "External Access Review" in template
    assert "Clouds Safe Export Source" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()
