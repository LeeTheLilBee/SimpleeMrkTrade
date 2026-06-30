"""Flask routes for Archive Vault.

Registered from web/app.py by Vault Giant Pack 001. The routes are JSON-first so
The Clouds and The Tower can read them without scraping UI.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from .vault_service import (
    get_clouds_source_payload,
    get_document_registry_payload,
    get_no_direct_upload_payload,
    get_open_app_handoff_payload,
    get_owner_console_payload,
    get_packet_templates_payload,
    get_readiness_payload,
    get_receipt_chain_payload,
    get_redacted_view_policy_payload,
    get_vault_status,
)


vault_bp = Blueprint("vault", __name__)


@vault_bp.route("/vault")
@vault_bp.route("/archive-vault")
def vault_home():
    return render_template("vault_home.html", status=get_vault_status(), owner_console=get_owner_console_payload())


@vault_bp.route("/vault/status.json")
@vault_bp.route("/archive-vault/status.json")
def vault_status_json():
    return jsonify(get_vault_status())


@vault_bp.route("/vault/document-registry.json")
def vault_document_registry_json():
    return jsonify(get_document_registry_payload())


@vault_bp.route("/vault/packet-templates.json")
def vault_packet_templates_json():
    return jsonify(get_packet_templates_payload())


@vault_bp.route("/vault/owner-console.json")
def vault_owner_console_json():
    return jsonify(get_owner_console_payload())


@vault_bp.route("/vault/readiness.json")
def vault_readiness_json():
    return jsonify(get_readiness_payload())


@vault_bp.route("/vault/no-direct-upload.json")
def vault_no_direct_upload_json():
    return jsonify(get_no_direct_upload_payload())


@vault_bp.route("/vault/redacted-view-policy.json")
def vault_redacted_view_policy_json():
    return jsonify(get_redacted_view_policy_payload())


@vault_bp.route("/vault/open-app-handoff.json")
def vault_open_app_handoff_json():
    return jsonify(get_open_app_handoff_payload())


@vault_bp.route("/vault/receipt-chain.json")
def vault_receipt_chain_json():
    return jsonify(get_receipt_chain_payload())


@vault_bp.route("/vault/clouds-source.json")
def vault_clouds_source_json():
    return jsonify(get_clouds_source_payload())
