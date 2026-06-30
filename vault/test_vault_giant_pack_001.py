"""Vault Giant Pack 001 verification."""

from __future__ import annotations

import json
from pathlib import Path

from vault.vault_readiness import get_readiness_score
from vault.vault_registry import PACKET_TEMPLATES, SAMPLE_DOCUMENT_RECORDS, get_registry_snapshot
from vault.vault_security import NO_DIRECT_UPLOAD_POLICY, REDACTION_POLICY, TOWER_GUARD_CONTRACT
from vault.vault_service import (
    get_clouds_source_payload,
    get_document_registry_payload,
    get_no_direct_upload_payload,
    get_owner_console_payload,
    get_packet_templates_payload,
    get_readiness_payload,
    get_vault_status,
)


def test_vault_registry_has_aggressive_packet_templates():
    template_ids = {template.packet_id for template in PACKET_TEMPLATES}
    assert "packet_atm_route_acquisition" in template_ids
    assert "packet_apartment_lender_due_diligence" in template_ids
    assert "packet_trust_entity" in template_ids
    assert "packet_ob_manual_live_proof" in template_ids
    assert "packet_soulaana_artist_package" in template_ids
    assert "packet_beta_onboarding" in template_ids
    assert len(PACKET_TEMPLATES) >= 6


def test_vault_document_records_are_private_and_upload_locked():
    assert SAMPLE_DOCUMENT_RECORDS
    for record in SAMPLE_DOCUMENT_RECORDS:
        assert record.redaction_required is True
        assert record.direct_upload_allowed is False
        assert record.sensitivity in {"high", "restricted", "medium"}
        assert record.universal_id.app_id == "archive_vault"


def test_tower_owns_security_not_vault():
    assert TOWER_GUARD_CONTRACT["tower_required"] is True
    assert TOWER_GUARD_CONTRACT["vault_owns_permissions"] is False
    assert TOWER_GUARD_CONTRACT["public_routes_allowed"] is False
    assert NO_DIRECT_UPLOAD_POLICY["enabled"] is True
    assert NO_DIRECT_UPLOAD_POLICY["direct_upload_allowed"] is False
    assert REDACTION_POLICY["enabled"] is True
    assert REDACTION_POLICY["clouds_default"] == "summary_only"


def test_service_payloads_are_json_serializable_and_ready():
    payloads = [
        get_vault_status(),
        get_document_registry_payload(),
        get_packet_templates_payload(),
        get_owner_console_payload(),
        get_readiness_payload(),
        get_no_direct_upload_payload(),
        get_clouds_source_payload(),
    ]

    for payload in payloads:
        json.dumps(payload)
        assert payload["app_id"] == "archive_vault"
        assert payload["public_access"] is False
        assert payload["tower_guard"]["tower_required"] is True


def test_readiness_is_full_for_gp001_foundation():
    readiness = get_readiness_score()
    assert readiness["score"] == 100
    assert readiness["label"] == "ready"
    assert readiness["passed"] == readiness["total"]


def test_clouds_source_is_ready_and_redacted():
    clouds = get_clouds_source_payload()
    assert clouds["safe_for_clouds"] is True
    assert clouds["clouds_view"] == "summary_only_redacted"
    assert clouds["readiness_score"] == 100
    assert "bank_account_details" in clouds["clouds_should_not_display"]


def test_registry_snapshot_has_search_and_handoff_contracts():
    snapshot = get_registry_snapshot()
    assert "summary" in snapshot["global_search_scope"]
    assert any(handoff["target_app"] == "clouds" for handoff in snapshot["open_app_handoffs"])
    assert any(handoff["target_app"] == "tower" for handoff in snapshot["open_app_handoffs"])


def test_vault_ui_does_not_introduce_bright_page_background():
    template = Path("templates/vault_home.html").read_text(encoding="utf-8")
    css = Path("static/vault/vault.css").read_text(encoding="utf-8")
    combined = (template + css).lower()
    banned = ["background: white", "background:#fff", "background-color: white", "background-color:#fff"]
    assert not any(token in combined for token in banned)


def test_web_app_registration_marker_exists_when_app_file_is_present():
    app_file = Path("web/app.py")
    if app_file.exists():
        text = app_file.read_text(encoding="utf-8")
        assert "VAULT GIANT PACK 001 ROUTES START" in text
        assert "vault_bp" in text
