"""Vault Giant Pack 004 verification."""

from __future__ import annotations

import json
from pathlib import Path

from vault.vault_trust_ob_service import (
    get_ob_manual_live_proof_vault_payload,
    get_trust_entity_vault_payload,
    get_trust_ob_owner_queue_payload,
    get_trust_ob_vault_payload,
    get_vault_gp004_status_payload,
)


def test_gp004_trust_entity_vault_is_ready_and_redacted():
    payload = get_trust_entity_vault_payload()
    json.dumps(payload)

    assert payload["tower_guard"]["tower_required"] is True
    assert payload["vault_id"] == "vault_trust_entity_packet"
    assert payload["business_lane"] == "trust"
    assert payload["status"] == "ready"
    assert payload["readiness"]["setup_score"] == 100
    assert len(payload["documents"]) >= 7
    assert len(payload["authority_matrix"]) >= 5
    assert payload["privacy_boundary"]["bank_account_details_hidden"] is True
    assert payload["privacy_boundary"]["beneficiary_details_hidden"] is True
    assert payload["privacy_boundary"]["direct_upload_allowed"] is False


def test_gp004_ob_manual_live_proof_vault_locks_execution_boundaries():
    payload = get_ob_manual_live_proof_vault_payload()
    json.dumps(payload)

    assert payload["tower_guard"]["tower_required"] is True
    assert payload["vault_id"] == "vault_ob_manual_live_proof"
    assert payload["business_lane"] == "observatory"
    assert payload["status"] == "ready"
    assert payload["readiness"]["setup_score"] == 100
    assert len(payload["proof_documents"]) >= 6

    boundary_ids = {boundary["boundary_id"] for boundary in payload["mode_boundaries"]}
    assert "no_broker_api_read" in boundary_ids
    assert "no_broker_order_submit" in boundary_ids
    assert "no_auto_execution" in boundary_ids
    assert "no_public_proof" in boundary_ids
    assert "hybrid_locked" in boundary_ids
    assert "automated_locked" in boundary_ids
    assert "live_auto_locked" in boundary_ids

    assert payload["privacy_boundary"]["proof_is_public"] is False
    assert payload["privacy_boundary"]["broker_secrets_allowed"] is False
    assert payload["privacy_boundary"]["auto_execution_allowed"] is False


def test_gp004_owner_queue_has_trust_ob_and_clouds_actions():
    queue = get_trust_ob_owner_queue_payload()

    assert queue["action_count"] >= 6
    assert queue["critical_count"] >= 2
    assert queue["high_count"] >= 3

    action_ids = {action["action_id"] for action in queue["actions"]}
    assert "trust_packet_keep_index_ready" in action_ids
    assert "trust_bank_summary_redaction_check" in action_ids
    assert "ob_manual_live_proof_chain_ready" in action_ids
    assert "ob_execution_boundary_lock" in action_ids
    assert "clouds_trust_ob_summary_ready" in action_ids


def test_gp004_combined_trust_ob_clouds_source_is_safe():
    payload = get_trust_ob_vault_payload()

    assert payload["status"] == "ready"
    assert payload["boundary"]["tower_permission_required"] is True
    assert payload["boundary"]["direct_upload_allowed"] is False
    assert payload["boundary"]["public_proof_allowed"] is False
    assert payload["boundary"]["broker_secrets_allowed"] is False
    assert payload["boundary"]["bank_account_details_hidden"] is True
    assert payload["boundary"]["beneficiary_details_hidden"] is True

    clouds = payload["clouds_safe_source"]
    assert clouds["safe_for_clouds"] is True
    assert clouds["view"] == "summary_only_redacted"
    assert len(clouds["summaries"]) == 2
    assert "broker_credentials" in clouds["hidden_sensitive_fields"]
    assert "bank_account_numbers" in clouds["hidden_sensitive_fields"]
    assert "public_proof_blocked" in clouds["blocked_reasons"]
    assert "auto_execution_blocked" in clouds["blocked_reasons"]


def test_gp004_status_marks_safe_to_continue():
    status = get_vault_gp004_status_payload()

    assert status["status"] == "ready"
    assert status["pack"] == "Vault Giant Pack 004"
    assert status["trust_document_count"] >= 7
    assert status["trust_authority_role_count"] >= 5
    assert status["ob_proof_document_count"] >= 6
    assert status["ob_boundary_count"] >= 7
    assert status["trust_setup_score"] == 100
    assert status["ob_setup_score"] == 100
    assert status["direct_upload_allowed"] is False
    assert status["public_proof_allowed"] is False
    assert status["broker_secrets_allowed"] is False
    assert status["safe_to_continue_to_gp005"] is True


def test_gp004_routes_template_and_css_exist():
    routes = Path("vault/vault_routes.py").read_text(encoding="utf-8")
    template = Path("templates/vault_trust_ob.html").read_text(encoding="utf-8")
    css = Path("static/vault/vault_trust_ob.css").read_text(encoding="utf-8")

    assert "/vault/trust-ob" in routes
    assert "/vault/trust-ob-vault.json" in routes
    assert "/vault/trust-entity-vault.json" in routes
    assert "/vault/ob-manual-live-proof-vault.json" in routes
    assert "/vault/gp004-status.json" in routes

    assert "Ownership protected" in template
    assert "Proof private" in template
    assert "Broker Secrets" in template
    assert "Clouds Safe Trust + OB Source" in template

    assert "background: white" not in css.lower()
    assert "background-color: white" not in css.lower()
