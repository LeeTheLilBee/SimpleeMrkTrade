"""Vault Giant Pack 010 verification."""

from __future__ import annotations

import json
from pathlib import Path

from vault.vault_final_readiness_service import (
    get_clouds_handoff_contract_payload,
    get_vault_final_readiness_payload,
    get_vault_gp010_status_payload,
    get_vault_owner_final_queue_payload,
    get_vault_pack_gate_payload,
)


def test_gp010_pack_gate_verifies_gp001_through_gp009():
    payload = get_vault_pack_gate_payload()
    json.dumps(payload)

    assert payload["app_id"] == "archive_vault"
    assert payload["payload_type"] == "vault_pack_gate"
    assert payload["status"] == "ready"
    assert payload["public_access"] is False
    assert payload["tower_guard"]["tower_required"] is True
    assert payload["gate_count"] == 9
    assert payload["ready_gate_count"] == 9
    assert payload["blocked_gate_count"] == 0
    assert payload["all_previous_gates_ready"] is True

    pack_ids = {gate["pack_id"] for gate in payload["gates"]}
    assert pack_ids == {"gp001", "gp002", "gp003", "gp004", "gp005", "gp006", "gp007", "gp008", "gp009"}

    for gate in payload["gates"]:
        assert gate["ready"] is True
        assert gate["status"] == "ready"
        assert gate["missing_keys"] == []


def test_gp010_clouds_handoff_contract_is_summary_only_and_safe():
    payload = get_clouds_handoff_contract_payload()

    assert payload["payload_type"] == "clouds_handoff_contract"
    assert payload["status"] == "ready"
    assert payload["safe_for_clouds"] is True
    assert payload["clouds_view"] == "summary_only_redacted"
    assert len(payload["source_routes"]) >= 6
    assert len(payload["handoff_cards"]) >= 6
    assert "readiness_score" in payload["allowed_fields"]
    assert "owner_focus" in payload["allowed_fields"]
    assert "broker_credentials" in payload["hidden_fields"]
    assert "bank_account_numbers" in payload["hidden_fields"]
    assert "nda_body" in payload["hidden_fields"]
    assert "display_unredacted_document_body" in payload["clouds_must_not_do"]
    assert "show_vault_readiness" in payload["clouds_may_do"]


def test_gp010_owner_final_queue_has_locked_and_ready_actions():
    payload = get_vault_owner_final_queue_payload()

    assert payload["payload_type"] == "vault_owner_final_queue"
    assert payload["status"] == "ready"
    assert payload["action_count"] >= 6
    assert payload["critical_count"] >= 3
    assert payload["high_count"] >= 3
    assert payload["ready_action_count"] >= 3

    action_ids = {action["action_id"] for action in payload["actions"]}
    assert "vault_final_keep_upload_locked" in action_ids
    assert "vault_final_start_clouds_gp001" in action_ids
    assert "vault_final_keep_exports_locked" in action_ids
    assert "vault_final_preserve_redaction_boundaries" in action_ids


def test_gp010_final_readiness_marks_vault_foundation_complete_and_clouds_ready():
    payload = get_vault_final_readiness_payload()

    assert payload["payload_type"] == "vault_final_readiness"
    assert payload["status"] == "ready"
    assert payload["pack"] == "Vault Giant Pack 010"
    assert payload["final_score"] == 100
    assert payload["readiness_label"] == "vault_foundation_complete"
    assert payload["safe_to_start_clouds"] is True
    assert payload["safe_to_continue_to_vault_gp011"] is True

    assert payload["final_gate_summary"]["gate_count"] == 9
    assert payload["final_gate_summary"]["ready_gate_count"] == 9
    assert payload["final_gate_summary"]["blocked_gate_count"] == 0
    assert payload["final_gate_summary"]["all_previous_gates_ready"] is True

    foundation = payload["foundation_summary"]
    assert foundation["lane_count"] == 6
    assert foundation["route_count"] >= 16
    assert foundation["search_record_count"] >= 45
    assert foundation["requirement_count"] >= 40
    assert foundation["receipt_count"] >= 13
    assert foundation["locked_export_count"] >= 7

    clouds = payload["clouds_handoff_summary"]
    assert clouds["safe_for_clouds"] is True
    assert clouds["clouds_view"] == "summary_only_redacted"
    assert clouds["source_route_count"] >= 6
    assert clouds["handoff_card_count"] >= 6
    assert clouds["legacy_clouds_source_ready"] is True


def test_gp010_final_boundaries_stay_locked():
    payload = get_vault_final_readiness_payload()
    boundary = payload["boundary_final"]

    assert boundary["tower_guard_required"] is True
    assert boundary["vault_owns_permissions"] is False
    assert boundary["direct_upload_allowed"] is False
    assert boundary["exports_locked_by_default"] is True
    assert boundary["external_access_default_deny"] is True
    assert boundary["unredacted_export_allowed"] is False
    assert boundary["clouds_view"] == "summary_only_redacted"
    assert boundary["broker_secrets_allowed"] is False
    assert boundary["auto_execution_allowed"] is False
    assert boundary["public_proof_allowed"] is False
    assert boundary["public_beta_routes_allowed"] is False
    assert boundary["ai_generated_character_art_allowed"] is False

    assert "direct_upload_locked" in payload["intentional_locks"]
    assert "exports_locked_by_default" in payload["intentional_locks"]
    assert "unredacted_export_blocked" in payload["intentional_locks"]


def test_gp010_status_marks_safe_to_start_clouds():
    status = get_vault_gp010_status_payload()

    assert status["status"] == "ready"
    assert status["pack"] == "Vault Giant Pack 010"
    assert status["final_score"] == 100
    assert status["gate_count"] == 9
    assert status["ready_gate_count"] == 9
    assert status["safe_to_start_clouds"] is True
    assert status["clouds_source_route_count"] >= 6
    assert status["clouds_handoff_card_count"] >= 6
    assert status["direct_upload_allowed"] is False
    assert status["vault_owns_permissions"] is False
    assert status["exports_locked_by_default"] is True
    assert status["clouds_view"] == "summary_only_redacted"
    assert status["safe_to_continue_to_vault_gp011"] is True


def test_gp010_routes_template_and_css_exist():
    routes = Path("vault/vault_routes.py").read_text(encoding="utf-8")
    template = Path("templates/vault_final_readiness.html").read_text(encoding="utf-8")
    css = Path("static/vault/vault_final_readiness.css").read_text(encoding="utf-8")

    assert "/vault/final-readiness" in routes
    assert "/vault/final-readiness.json" in routes
    assert "/vault/pack-gate.json" in routes
    assert "/vault/clouds-handoff-contract.json" in routes
    assert "/vault/owner-final-queue.json" in routes
    assert "/vault/gp010-status.json" in routes

    assert "Vault foundation complete. Clouds can start." in template
    assert "Foundation Summary" in template
    assert "Clouds Handoff" in template
    assert "Final Boundary Wall" in template
    assert "Clouds Start Sources" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()
