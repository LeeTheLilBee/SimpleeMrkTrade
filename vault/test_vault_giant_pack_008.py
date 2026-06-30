"""Vault Giant Pack 008 verification."""

from __future__ import annotations

import json
from pathlib import Path

from vault.vault_receipt_control_service import (
    get_approval_chain_console_payload,
    get_blocked_decision_review_payload,
    get_freeze_revoke_undo_wall_payload,
    get_receipt_chain_console_payload,
    get_receipt_control_center_payload,
    get_vault_gp008_status_payload,
)


def test_gp008_receipt_chain_console_is_ready():
    payload = get_receipt_chain_console_payload()
    json.dumps(payload)

    assert payload["app_id"] == "archive_vault"
    assert payload["payload_type"] == "receipt_chain_console"
    assert payload["status"] == "ready"
    assert payload["public_access"] is False
    assert payload["tower_guard"]["tower_required"] is True
    assert payload["receipt_count"] >= 13
    assert payload["active_count"] >= 13
    assert "build" in payload["receipt_types"]
    assert "security_boundary" in payload["receipt_types"]
    assert "privacy_boundary" in payload["receipt_types"]
    assert payload["boundary"]["direct_upload_allowed"] is False
    assert payload["boundary"]["clouds_view"] == "summary_only_redacted"


def test_gp008_approval_chain_console_is_ready_and_export_locked():
    payload = get_approval_chain_console_payload()

    assert payload["payload_type"] == "approval_chain_console"
    assert payload["status"] == "ready"
    assert payload["chain_count"] >= 6
    assert payload["role_count"] >= 5
    assert payload["export_locked_count"] == payload["chain_count"]
    assert payload["step_up_required_count"] == payload["chain_count"]
    assert payload["boundary"]["tower_enforces_roles"] is True
    assert payload["boundary"]["vault_owns_permissions"] is False
    assert payload["boundary"]["exports_locked_by_default"] is True


def test_gp008_freeze_revoke_undo_wall_has_controls():
    payload = get_freeze_revoke_undo_wall_payload()

    assert payload["payload_type"] == "freeze_revoke_undo_wall"
    assert payload["status"] == "ready"
    assert payload["rule_count"] >= 9
    assert payload["active_rule_count"] >= 5
    assert payload["template_rule_count"] >= 3
    assert payload["undo_allowed_count"] >= 3
    assert payload["tower_required_count"] >= 7

    control_types = set(payload["control_types"])
    assert {"freeze", "revoke", "undo"}.issubset(control_types)

    rule_ids = {rule["rule_id"] for rule in payload["rules"]}
    assert "freeze_direct_upload_unlock" in rule_ids
    assert "freeze_ob_auto_execution_path" in rule_ids
    assert "freeze_ai_character_art_preview" in rule_ids
    assert "revoke_beta_access" in rule_ids


def test_gp008_blocked_decision_review_defaults_to_keep_blocked():
    payload = get_blocked_decision_review_payload()

    assert payload["payload_type"] == "blocked_decision_review"
    assert payload["status"] == "ready"
    assert payload["blocked_decision_count"] >= 50
    assert payload["boundary"]["default_action"] == "keep_blocked"
    assert payload["boundary"]["owner_can_review"] is True
    assert payload["boundary"]["tower_required_for_unlock"] is True
    assert payload["boundary"]["dangerous_unlocks_blocked"] is True


def test_gp008_receipt_control_center_is_clouds_safe():
    payload = get_receipt_control_center_payload()

    assert payload["payload_type"] == "receipt_control_center"
    assert payload["status"] == "ready"
    assert payload["boundary"]["tower_guard_required"] is True
    assert payload["boundary"]["vault_owns_permissions"] is False
    assert payload["boundary"]["direct_upload_allowed"] is False
    assert payload["boundary"]["redacted_view_default"] is True
    assert payload["boundary"]["clouds_view"] == "summary_only_redacted"
    assert payload["boundary"]["dangerous_unlocks_default_blocked"] is True

    clouds = payload["clouds_safe_source"]
    assert clouds["safe_for_clouds"] is True
    assert clouds["view"] == "summary_only_redacted"
    assert clouds["receipt_count"] >= 13
    assert clouds["approval_chain_count"] >= 6
    assert clouds["control_rule_count"] >= 9
    assert clouds["blocked_decision_count"] >= 50


def test_gp008_status_marks_safe_to_continue():
    status = get_vault_gp008_status_payload()

    assert status["status"] == "ready"
    assert status["pack"] == "Vault Giant Pack 008"
    assert status["receipt_count"] >= 13
    assert status["approval_chain_count"] >= 6
    assert status["control_rule_count"] >= 9
    assert status["blocked_decision_count"] >= 50
    assert status["direct_upload_allowed"] is False
    assert status["vault_owns_permissions"] is False
    assert status["clouds_safe"] is True
    assert status["safe_to_continue_to_gp009"] is True


def test_gp008_routes_template_and_css_exist():
    routes = Path("vault/vault_routes.py").read_text(encoding="utf-8")
    template = Path("templates/vault_receipt_control.html").read_text(encoding="utf-8")
    css = Path("static/vault/vault_receipt_control.css").read_text(encoding="utf-8")

    assert "/vault/receipt-control" in routes
    assert "/vault/receipt-control-center.json" in routes
    assert "/vault/receipt-chain-console.json" in routes
    assert "/vault/approval-chain-console.json" in routes
    assert "/vault/freeze-revoke-undo-wall.json" in routes
    assert "/vault/blocked-decision-review.json" in routes
    assert "/vault/gp008-status.json" in routes

    assert "Proof chains, approvals, freezes, revokes, and undo paths." in template
    assert "Receipt Chain Console" in template
    assert "Approval Chain Console" in template
    assert "Freeze / Revoke / Undo Wall" in template
    assert "Blocked Decision Review" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()
