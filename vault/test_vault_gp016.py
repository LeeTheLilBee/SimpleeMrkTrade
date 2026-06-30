"""
Tests for VAULT GIANT PACK 016 — Evidence Binder Builder
"""

from pathlib import Path

import pytest

from vault.evidence_binder_builder_service import (
    get_evidence_binder_blocked_reasons,
    get_evidence_binder_builder,
    get_evidence_binder_export_preview,
    get_evidence_binder_home,
    get_evidence_binder_packets,
    get_evidence_binder_requirements,
    get_gp016_status,
    render_evidence_binder_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp016_status_ready_and_safe_to_continue():
    status = get_gp016_status()

    assert status["pack"]["id"] == "VAULT_GP016"
    assert status["gp016_status"]["ready"] is True
    assert status["gp016_status"]["safe_to_continue_to_gp017"] is True
    assert status["gp016_status"]["next_pack"] == "VAULT_GP017_ATM_ROUTE_PACKET_WORKSPACE_V2"
    assert status["gp016_status"]["gp015_version_lineage_connected"] is True
    assert status["gp016_status"]["evidence_binder_metadata_ready"] is True
    assert status["gp016_status"]["redacted_export_preview_only"] is True
    assert status["gp016_status"]["direct_upload_still_locked"] is True
    assert status["gp016_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp016_status"]["raw_binder_export_still_locked"] is True
    assert status["gp016_status"]["public_proof_still_locked"] is True
    assert status["gp016_status"]["fake_binder_body_completion_not_claimed"] is True


def test_gp016_binder_truth_does_not_fake_storage_or_exports():
    status = get_gp016_status()
    truth = status["binder_truth"]

    assert truth["binder_metadata_enabled"] is True
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["direct_upload_unlocked"] is False
    assert truth["provider_configured"] is False
    assert truth["raw_binder_export_enabled"] is False
    assert truth["redacted_export_preview_enabled"] is True
    assert truth["unredacted_export_enabled"] is False
    assert truth["public_proof_enabled"] is False
    assert truth["external_access_enabled"] is False
    assert truth["auto_binder_completion_enabled"] is False
    assert truth["fake_binder_body_complete"] is False


def test_gp016_keeps_tower_authority_and_vault_boundaries():
    status = get_gp016_status()
    tower = status["tower_authority"]
    boundary = status["vault_boundary"]

    assert tower["tower_owns_identity"] is True
    assert tower["tower_owns_permissions"] is True
    assert tower["tower_owns_clearance"] is True
    assert tower["tower_owns_step_up"] is True
    assert tower["tower_owns_export_locks"] is True
    assert tower["tower_owns_freeze_revoke"] is True
    assert tower["tower_owns_external_access"] is True
    assert tower["vault_owns_tower_permissions"] is False

    assert boundary["no_public_vault"] is True
    assert boundary["direct_raw_upload_unlocked"] is False
    assert boundary["permanent_file_body_storage_enabled"] is False
    assert boundary["external_access_default"] == "denied"
    assert boundary["unredacted_export_allowed"] is False
    assert boundary["raw_binder_export_allowed"] is False
    assert boundary["redacted_export_preview_allowed"] is True
    assert boundary["sensitive_body_display_in_summary_views"] is False
    assert boundary["broker_secret_storage_allowed"] is False
    assert boundary["public_ob_proof_allowed"] is False
    assert boundary["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp016_builds_expected_evidence_binders():
    builder = get_evidence_binder_builder()

    assert builder["binder_count"] >= 6

    binder_ids = {binder["binder_id"] for binder in builder["evidence_binders"]}
    assert "VEB-ATM-ROUTE-001" in binder_ids
    assert "VEB-APT-LENDER-001" in binder_ids
    assert "VEB-TRUST-ENTITY-001" in binder_ids
    assert "VEB-OB-MANUAL-LIVE-001" in binder_ids
    assert "VEB-SOULAANA-IP-001" in binder_ids
    assert "VEB-BETA-ONBOARD-001" in binder_ids

    for binder in builder["evidence_binders"]:
        assert binder["binder_id"].startswith("VEB-")
        assert binder["binder_type"]
        assert binder["binder_type_label"]
        assert binder["lane"]
        assert binder["packet_id"]
        assert binder["section_count"] >= 1
        assert binder["binder_controls"]["owner_confirmation_required"] is True
        assert binder["binder_controls"]["tower_clearance_required_for_sensitive_steps"] is True
        assert binder["binder_controls"]["raw_body_storage_enabled"] is False
        assert binder["binder_controls"]["direct_upload_allowed"] is False
        assert binder["binder_controls"]["raw_download_allowed"] is False
        assert binder["binder_controls"]["unredacted_preview_allowed"] is False
        assert binder["binder_controls"]["redacted_export_preview_allowed"] is True
        assert binder["binder_controls"]["external_access_allowed"] is False
        assert binder["binder_controls"]["public_proof_allowed"] is False
        assert binder["binder_controls"]["auto_complete_allowed"] is False
        assert binder["tower_boundary"]["tower_guard_required"] is True
        assert binder["tower_boundary"]["vault_permission_owner"] is False
        assert binder["redaction_boundary"]["summary_safe"] is True
        assert binder["redaction_boundary"]["redacted_preview_available"] is True
        assert binder["redaction_boundary"]["unredacted_preview_allowed"] is False
        assert binder["redaction_boundary"]["external_preview_allowed"] is False


def test_gp016_binder_sections_are_metadata_only():
    builder = get_evidence_binder_builder()

    for binder in builder["evidence_binders"]:
        for section in binder["sections"]:
            assert section["summary_safe"] is True
            assert section["body_available"] is False
            assert section["raw_preview_allowed"] is False
            assert section["external_preview_allowed"] is False
            if section["section_status"] == "metadata_version_linked":
                assert section["version_id"].startswith("VVER-")
                assert section["document_key"].startswith("VDOC-")
                assert section["attachment_id"].startswith("VAT-")
                assert section["intake_id"].startswith("VIN-")
                assert section["redacted_preview_allowed"] is True


def test_gp016_packets_and_requirements_are_owner_review_safe():
    packets = get_evidence_binder_packets()["evidence_binder_packets"]
    requirements = get_evidence_binder_requirements()["evidence_binder_requirements"]

    assert packets["packet_count"] >= 6
    assert packets["ready_for_external_packet_share_count"] == 0
    assert requirements["coverage_count"] >= 6
    assert requirements["auto_complete_allowed"] is False

    for item in packets["packet_items"]:
        assert item["packet_binder_id"].startswith("VBP-")
        assert item["binder_id"].startswith("VEB-")
        assert item["ready_for_owner_packet_review"] is True
        assert item["ready_for_external_packet_share"] is False
        assert item["reason_external_share_blocked"]

    for item in requirements["coverage_items"]:
        assert item["coverage_id"].startswith("VBC-")
        assert item["binder_id"].startswith("VEB-")
        assert item["covered_requirement_count"] >= 1
        assert item["owner_confirmation_required"] is True
        assert item["auto_complete_allowed"] is False


def test_gp016_export_preview_is_redacted_only():
    preview = get_evidence_binder_export_preview()["evidence_binder_export_preview"]

    assert preview["preview_count"] >= 6
    assert preview["redacted_preview_count"] >= 6
    assert preview["raw_export_count"] == 0
    assert preview["unredacted_export_count"] == 0
    assert preview["external_preview_count"] == 0
    assert preview["public_proof_count"] == 0

    for item in preview["preview_items"]:
        assert item["preview_id"].startswith("VEP-")
        assert item["binder_id"].startswith("VEB-")
        assert item["redacted_preview_available"] is True
        assert item["raw_export_available"] is False
        assert item["unredacted_export_available"] is False
        assert item["external_preview_available"] is False
        assert item["public_proof_available"] is False
        assert "NO_RAW_BINDER_EXPORT" in item["blocked_codes"]
        assert "PUBLIC_PROOF_LOCKED" in item["blocked_codes"]


def test_gp016_blocked_reasons_exist():
    blocked = get_evidence_binder_blocked_reasons()

    codes = {reason["code"] for reason in blocked["evidence_binder_blocked_reasons"]}

    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "EXTERNAL_ACCESS_DENIED" in codes
    assert "UNREDACTED_PREVIEW_LOCKED" in codes
    assert "OWNER_CONFIRMATION_REQUIRED" in codes
    assert "PUBLIC_PROOF_LOCKED" in codes
    assert "NO_RAW_BINDER_EXPORT" in codes
    assert "NO_AUTO_BINDER_COMPLETE" in codes


def test_gp016_home_routes_declared():
    home = get_evidence_binder_home()
    summary = home["binder_summary"]

    assert summary["route"] == "/vault/evidence-binder"
    assert summary["json_route"] == "/vault/evidence-binder.json"
    assert summary["builder_route"] == "/vault/evidence-binder-builder.json"
    assert summary["packets_route"] == "/vault/evidence-binder-packets.json"
    assert summary["requirements_route"] == "/vault/evidence-binder-requirements.json"
    assert summary["export_preview_route"] == "/vault/evidence-binder-export-preview.json"
    assert summary["blocked_reasons_route"] == "/vault/evidence-binder-blocked-reasons.json"
    assert summary["gp016_status_route"] == "/vault/gp016-status.json"
    assert summary["raw_body_storage_enabled"] is False
    assert summary["direct_upload_unlocked"] is False


def test_gp016_html_is_dark_and_has_no_white_background_tokens():
    html = render_evidence_binder_page()
    lowered = html.lower()

    assert "Vault Evidence Binder Builder" in html
    assert "Archive Vault" in html
    assert "/vault/evidence-binder.json" in html
    assert "/vault/gp016-status.json" in html

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


def test_gp016_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/evidence-binder",
        "/vault/evidence-binder.json",
        "/vault/evidence-binder-builder.json",
        "/vault/evidence-binder-packets.json",
        "/vault/evidence-binder-requirements.json",
        "/vault/evidence-binder-export-preview.json",
        "/vault/evidence-binder-blocked-reasons.json",
        "/vault/gp016-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp016_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/evidence-binder",
        "/vault/evidence-binder.json",
        "/vault/evidence-binder-builder.json",
        "/vault/evidence-binder-packets.json",
        "/vault/evidence-binder-requirements.json",
        "/vault/evidence-binder-export-preview.json",
        "/vault/evidence-binder-blocked-reasons.json",
        "/vault/gp016-status.json",
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
                assert b"Vault Evidence Binder Builder" in response.data
