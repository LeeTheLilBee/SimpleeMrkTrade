"""
Tests for VAULT GIANT PACK 012 — File Attachment Registry + Packet Linking
"""

from pathlib import Path

import pytest

from vault.file_attachment_registry_service import (
    get_attachment_orphan_state,
    get_attachment_requirement_links,
    get_attachments_home,
    get_file_attachment_registry,
    get_gp012_status,
    get_packet_links,
    render_attachment_registry_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp012_status_ready_and_safe_to_continue():
    status = get_gp012_status()

    assert status["pack"]["id"] == "VAULT_GP012"
    assert status["gp012_status"]["ready"] is True
    assert status["gp012_status"]["safe_to_continue_to_gp013"] is True
    assert status["gp012_status"]["next_pack"] == "VAULT_GP013_DOCUMENT_TYPE_CLASSIFIER_REQUIREMENT_MATCH"
    assert status["gp012_status"]["gp011_intake_records_connected"] is True
    assert status["gp012_status"]["attachment_registry_metadata_only"] is True
    assert status["gp012_status"]["raw_file_body_storage_still_locked"] is True


def test_gp012_keeps_tower_authority_and_vault_boundaries():
    status = get_gp012_status()
    tower = status["tower_authority"]
    boundary = status["vault_boundary"]

    assert tower["tower_owns_identity"] is True
    assert tower["tower_owns_permissions"] is True
    assert tower["tower_owns_clearance"] is True
    assert tower["tower_owns_step_up"] is True
    assert tower["tower_owns_export_locks"] is True
    assert tower["tower_owns_freeze_revoke"] is True
    assert tower["vault_owns_tower_permissions"] is False

    assert boundary["no_public_vault"] is True
    assert boundary["direct_raw_upload_unlocked"] is False
    assert boundary["controlled_metadata_attachment_slots_enabled"] is True
    assert boundary["permanent_file_body_storage_enabled"] is False
    assert boundary["external_access_default"] == "denied"
    assert boundary["unredacted_export_allowed"] is False
    assert boundary["sensitive_body_display_in_summary_views"] is False
    assert boundary["broker_secret_storage_allowed"] is False
    assert boundary["public_ob_proof_allowed"] is False
    assert boundary["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp012_storage_truth_not_fake_complete():
    status = get_gp012_status()
    storage = status["storage_truth"]

    assert storage["provider_configured"] is False
    assert storage["provider_name"] is None
    assert storage["file_body_storage_status"] == "blocked_by_provider_and_tower_clearance"
    assert storage["attachment_metadata_registry_status"] == "ready"
    assert storage["fake_storage_complete"] is False


def test_gp012_attachment_slots_link_to_gp011_intake_and_packets():
    registry = get_file_attachment_registry()

    assert registry["attachment_slot_count"] >= 6

    required_intake_ids = {
        "VIN-ATM-ROUTE-001",
        "VIN-APT-LENDER-001",
        "VIN-TRUST-ENTITY-001",
        "VIN-OB-PROOF-001",
        "VIN-SOULAANA-IP-001",
        "VIN-BETA-ONBOARD-001",
    }

    seen_intake_ids = {slot["intake_id"] for slot in registry["attachment_slots"]}
    assert required_intake_ids.issubset(seen_intake_ids)

    for slot in registry["attachment_slots"]:
        assert slot["attachment_id"].startswith("VAT-")
        assert slot["attachment_metadata"]["body_present"] is False
        assert slot["attachment_metadata"]["metadata_only"] is True
        assert slot["storage_state"]["raw_body_storage_enabled"] is False
        assert slot["storage_state"]["provider_configured"] is False
        assert slot["storage_state"]["download_allowed"] is False
        assert slot["storage_state"]["preview_allowed"] is False
        assert slot["storage_state"]["upload_allowed_from_vault"] is False
        assert slot["redaction_state"]["summary_safe"] is True
        assert slot["redaction_state"]["unredacted_preview_allowed"] is False
        assert slot["redaction_state"]["external_preview_allowed"] is False
        assert slot["tower_boundary"]["tower_guard_required"] is True
        assert slot["tower_boundary"]["vault_permission_owner"] is False


def test_gp012_packet_links_and_requirement_links_exist():
    packets = get_packet_links()
    requirements = get_attachment_requirement_links()

    assert packets["packet_link_count"] >= 6
    assert requirements["requirement_link_count"] >= 6

    packet_ids = {packet["packet_id"] for packet in packets["packet_links"]}
    assert "atm_route_acquisition_packet" in packet_ids
    assert "apartment_lender_due_diligence_packet" in packet_ids
    assert "trust_entity_binder" in packet_ids
    assert "ob_manual_live_private_proof_packet" in packet_ids
    assert "soulaana_artist_ip_vault" in packet_ids
    assert "private_beta_onboarding_vault" in packet_ids

    for link in requirements["requirement_links"]:
        assert link["attachment_id"].startswith("VAT-")
        assert link["packet_id"]
        assert link["requirement_id"]
        assert link["ready_for_gp013_classifier"] is True


def test_gp012_orphan_state_is_safe():
    orphan = get_attachment_orphan_state()["orphan_state"]

    assert orphan["orphan_attachment_count"] == 0
    assert orphan["orphan_safe_to_continue"] is True
    assert isinstance(orphan["intake_without_attachment_slot"], list)
    assert isinstance(orphan["attachment_without_intake"], list)


def test_gp012_home_routes_declared():
    home = get_attachments_home()
    summary = home["registry_summary"]

    assert summary["route"] == "/vault/attachments"
    assert summary["json_route"] == "/vault/attachments.json"
    assert summary["registry_route"] == "/vault/file-attachment-registry.json"
    assert summary["packet_links_route"] == "/vault/packet-links.json"
    assert summary["requirement_links_route"] == "/vault/attachment-requirement-links.json"
    assert summary["orphan_state_route"] == "/vault/attachment-orphan-state.json"
    assert summary["gp012_status_route"] == "/vault/gp012-status.json"
    assert summary["raw_body_storage_enabled"] is False


def test_gp012_html_is_dark_and_has_no_white_background_tokens():
    html = render_attachment_registry_page()
    lowered = html.lower()

    assert "Vault Attachment Registry" in html
    assert "Archive Vault" in html
    assert "/vault/attachments.json" in html
    assert "/vault/gp012-status.json" in html

    forbidden = [
        "background: #fff",
        "background:#fff",
        "background-color: #fff",
        "background-color:#fff",
        "background: white",
        "background:white",
    ]

    for token in forbidden:
        assert token not in lowered


def test_gp012_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/attachments",
        "/vault/attachments.json",
        "/vault/file-attachment-registry.json",
        "/vault/packet-links.json",
        "/vault/attachment-requirement-links.json",
        "/vault/attachment-orphan-state.json",
        "/vault/gp012-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp012_flask_routes_when_app_importable_accepts_tower_guard():
    """
    In the full app, private Vault paths may return 403 because Tower/guard layers
    protect /vault routes. That is correct.

    Accept:
    - 200 direct local route response
    - 403 protected private route response

    Do not accept 404.
    """
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/attachments",
        "/vault/attachments.json",
        "/vault/file-attachment-registry.json",
        "/vault/packet-links.json",
        "/vault/attachment-requirement-links.json",
        "/vault/attachment-orphan-state.json",
        "/vault/gp012-status.json",
    ]

    for route in routes:
        response = client.get(route)
        assert response.status_code in (200, 403), (
            f"{route} returned unexpected status {response.status_code}. "
            "Expected 200 direct route or 403 Tower/private guard."
        )

        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Attachment Registry" in response.data
