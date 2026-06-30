"""
Tests for VAULT GIANT PACK 015 — Version History + Replace/Supersede Flow
"""

from pathlib import Path

import pytest

from vault.version_history_replace_supersede_flow_service import (
    get_gp015_status,
    get_replace_supersede_flow,
    get_version_blocked_reasons,
    get_version_history_home,
    get_version_lineage,
    get_version_records,
    render_version_history_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp015_status_ready_and_safe_to_continue():
    status = get_gp015_status()

    assert status["pack"]["id"] == "VAULT_GP015"
    assert status["gp015_status"]["ready"] is True
    assert status["gp015_status"]["safe_to_continue_to_gp016"] is True
    assert status["gp015_status"]["next_pack"] == "VAULT_GP016_EVIDENCE_BINDER_BUILDER"
    assert status["gp015_status"]["gp014_manual_review_records_connected"] is True
    assert status["gp015_status"]["version_metadata_ready"] is True
    assert status["gp015_status"]["replace_supersede_metadata_flow_ready"] is True
    assert status["gp015_status"]["direct_upload_still_locked"] is True
    assert status["gp015_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp015_status"]["fake_version_body_completion_not_claimed"] is True


def test_gp015_version_truth_does_not_fake_file_storage():
    status = get_gp015_status()
    truth = status["version_truth"]

    assert truth["version_metadata_enabled"] is True
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["direct_upload_unlocked"] is False
    assert truth["provider_configured"] is False
    assert truth["replace_flow_enabled_metadata_only"] is True
    assert truth["supersede_flow_enabled_metadata_only"] is True
    assert truth["destructive_delete_enabled"] is False
    assert truth["auto_replace_enabled"] is False
    assert truth["auto_supersede_enabled"] is False
    assert truth["download_enabled"] is False
    assert truth["unredacted_preview_enabled"] is False
    assert truth["external_access_enabled"] is False
    assert truth["fake_version_body_complete"] is False


def test_gp015_keeps_tower_authority_and_vault_boundaries():
    status = get_gp015_status()
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
    assert boundary["sensitive_body_display_in_summary_views"] is False
    assert boundary["broker_secret_storage_allowed"] is False
    assert boundary["public_ob_proof_allowed"] is False
    assert boundary["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp015_version_records_connect_to_gp014_review_records():
    records = get_version_records()

    assert records["version_record_count"] >= 6

    required_attachment_ids = {
        "VAT-ATM-SELLER-PACKET-001",
        "VAT-APT-LENDER-DD-001",
        "VAT-TRUST-PROOF-001",
        "VAT-OB-MANUAL-LIVE-001",
        "VAT-SOULAANA-IP-001",
        "VAT-BETA-NDA-001",
    }

    seen_attachment_ids = {record["attachment_id"] for record in records["version_records"]}
    assert required_attachment_ids.issubset(seen_attachment_ids)

    for record in records["version_records"]:
        assert record["version_id"].startswith("VVER-")
        assert record["document_key"].startswith("VDOC-")
        assert record["review_id"].startswith("VUR-")
        assert record["classification_id"].startswith("VCL-")
        assert record["attachment_id"].startswith("VAT-")
        assert record["intake_id"].startswith("VIN-")
        assert record["version_number"] == 1
        assert record["body_state"]["body_present"] is False
        assert record["body_state"]["body_hash"] is None
        assert record["body_state"]["body_storage_uri"] is None
        assert record["body_state"]["body_write_allowed"] is False
        assert record["body_state"]["body_read_allowed"] is False
        assert record["body_state"]["direct_upload_allowed"] is False
        assert record["body_state"]["provider_configured"] is False
        assert record["replace_supersede_state"]["auto_replace_allowed"] is False
        assert record["replace_supersede_state"]["auto_supersede_allowed"] is False
        assert record["replace_supersede_state"]["destructive_delete_allowed"] is False
        assert record["replace_supersede_state"]["requires_owner_confirmation"] is True
        assert record["tower_boundary"]["tower_guard_required"] is True
        assert record["tower_boundary"]["vault_permission_owner"] is False
        assert record["redaction_boundary"]["summary_safe"] is True
        assert record["redaction_boundary"]["unredacted_preview_allowed"] is False
        assert record["redaction_boundary"]["external_preview_allowed"] is False


def test_gp015_replace_supersede_flow_never_auto_applies_or_deletes():
    flow = get_replace_supersede_flow()["replace_supersede_flow"]

    assert flow["flow_count"] >= 6
    assert flow["auto_apply_allowed"] is False
    assert flow["destructive_delete_allowed"] is False
    assert flow["owner_confirmation_required"] is True

    for item in flow["flow_items"]:
        assert item["flow_id"].startswith("VRS-")
        assert item["version_id"].startswith("VVER-")
        assert item["document_key"].startswith("VDOC-")
        assert item["attachment_id"].startswith("VAT-")
        assert item["owner_must_confirm"] is True
        assert item["tower_must_clear_sensitive_steps"] is True
        assert item["auto_apply_allowed"] is False
        assert item["destructive_delete_allowed"] is False
        assert item["body_copy_allowed"] is False
        assert item["reason_body_copy_blocked"]


def test_gp015_lineage_is_metadata_safe_for_gp016():
    lineage = get_version_lineage()["version_lineage"]

    assert lineage["lineage_count"] >= 6
    assert lineage["safe_to_continue_to_gp016"] is True

    for item in lineage["lineage_items"]:
        assert item["lineage_id"].startswith("VLN-")
        assert item["document_key"].startswith("VDOC-")
        assert item["active_version_id"].startswith("VVER-")
        assert item["known_version_ids"]
        assert item["has_body_storage"] is False
        assert item["has_external_access"] is False
        assert item["safe_for_evidence_binder_metadata"] is True
        assert item["requires_owner_review_before_export"] is True


def test_gp015_blocked_reasons_exist():
    blocked = get_version_blocked_reasons()

    codes = {reason["code"] for reason in blocked["version_blocked_reasons"]}

    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "EXTERNAL_ACCESS_DENIED" in codes
    assert "UNREDACTED_PREVIEW_LOCKED" in codes
    assert "OWNER_CONFIRMATION_REQUIRED" in codes
    assert "NO_AUTO_REPLACE" in codes
    assert "NO_AUTO_SUPERSEDE" in codes
    assert "NO_DESTRUCTIVE_DELETE" in codes


def test_gp015_home_routes_declared():
    home = get_version_history_home()
    summary = home["version_summary"]

    assert summary["route"] == "/vault/version-history"
    assert summary["json_route"] == "/vault/version-history.json"
    assert summary["version_records_route"] == "/vault/version-records.json"
    assert summary["replace_supersede_route"] == "/vault/replace-supersede-flow.json"
    assert summary["lineage_route"] == "/vault/version-lineage.json"
    assert summary["blocked_reasons_route"] == "/vault/version-blocked-reasons.json"
    assert summary["gp015_status_route"] == "/vault/gp015-status.json"
    assert summary["raw_body_storage_enabled"] is False
    assert summary["direct_upload_unlocked"] is False


def test_gp015_html_is_dark_and_has_no_white_background_tokens():
    html = render_version_history_page()
    lowered = html.lower()

    assert "Vault Version History" in html
    assert "Archive Vault" in html
    assert "/vault/version-history.json" in html
    assert "/vault/gp015-status.json" in html

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


def test_gp015_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/version-history",
        "/vault/version-history.json",
        "/vault/version-records.json",
        "/vault/replace-supersede-flow.json",
        "/vault/version-lineage.json",
        "/vault/version-blocked-reasons.json",
        "/vault/gp015-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp015_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/version-history",
        "/vault/version-history.json",
        "/vault/version-records.json",
        "/vault/replace-supersede-flow.json",
        "/vault/version-lineage.json",
        "/vault/version-blocked-reasons.json",
        "/vault/gp015-status.json",
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
                assert b"Vault Version History" in response.data
