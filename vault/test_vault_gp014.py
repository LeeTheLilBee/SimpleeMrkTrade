"""
Tests for VAULT GIANT PACK 014 — Manual Upload Review Queue
"""

from pathlib import Path

import pytest

from vault.manual_upload_review_queue_service import (
    get_gp014_status,
    get_manual_upload_review_home,
    get_manual_upload_review_queue,
    get_upload_review_blocked_reasons,
    get_upload_review_checklist,
    get_upload_review_decisions,
    render_manual_upload_review_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp014_status_ready_and_safe_to_continue():
    status = get_gp014_status()

    assert status["pack"]["id"] == "VAULT_GP014"
    assert status["gp014_status"]["ready"] is True
    assert status["gp014_status"]["safe_to_continue_to_gp015"] is True
    assert status["gp014_status"]["next_pack"] == "VAULT_GP015_VERSION_HISTORY_REPLACE_SUPERSEDE_FLOW"
    assert status["gp014_status"]["gp013_classifier_records_connected"] is True
    assert status["gp014_status"]["manual_review_queue_ready"] is True
    assert status["gp014_status"]["direct_upload_still_locked"] is True
    assert status["gp014_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp014_status"]["fake_upload_completion_not_claimed"] is True


def test_gp014_manual_upload_truth_does_not_fake_upload_storage():
    status = get_gp014_status()
    truth = status["manual_upload_truth"]

    assert truth["manual_review_enabled"] is True
    assert truth["direct_upload_unlocked"] is False
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["provider_configured"] is False
    assert truth["upload_body_write_enabled"] is False
    assert truth["download_enabled"] is False
    assert truth["unredacted_preview_enabled"] is False
    assert truth["external_access_enabled"] is False
    assert truth["auto_file_completion_enabled"] is False
    assert truth["fake_upload_complete"] is False


def test_gp014_keeps_tower_authority_and_vault_boundaries():
    status = get_gp014_status()
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


def test_gp014_review_queue_connects_to_gp013_classifier_records():
    queue = get_manual_upload_review_queue()["manual_upload_review_queue"]

    assert queue["review_room"] == "Vault Manual Upload Review"
    assert queue["review_count"] >= 6
    assert queue["needs_owner_review_count"] >= 1

    required_attachment_ids = {
        "VAT-ATM-SELLER-PACKET-001",
        "VAT-APT-LENDER-DD-001",
        "VAT-TRUST-PROOF-001",
        "VAT-OB-MANUAL-LIVE-001",
        "VAT-SOULAANA-IP-001",
        "VAT-BETA-NDA-001",
    }

    seen_attachment_ids = {item["attachment_id"] for item in queue["review_items"]}
    assert required_attachment_ids.issubset(seen_attachment_ids)

    for item in queue["review_items"]:
        assert item["review_id"].startswith("VUR-")
        assert item["classification_id"].startswith("VCL-")
        assert item["attachment_id"].startswith("VAT-")
        assert item["intake_id"].startswith("VIN-")
        assert item["predicted_document_type"]
        assert item["recommended_decision"]
        assert item["needs_owner_review"] is True
        assert item["upload_body_state"]["body_present"] is False
        assert item["upload_body_state"]["body_write_allowed"] is False
        assert item["upload_body_state"]["body_read_allowed"] is False
        assert item["upload_body_state"]["direct_upload_allowed"] is False
        assert item["upload_body_state"]["provider_configured"] is False
        assert item["tower_boundary"]["tower_guard_required"] is True
        assert item["tower_boundary"]["vault_permission_owner"] is False
        assert item["redaction_boundary"]["summary_safe"] is True
        assert item["redaction_boundary"]["unredacted_preview_allowed"] is False
        assert item["redaction_boundary"]["external_preview_allowed"] is False


def test_gp014_decisions_never_auto_apply():
    decisions = get_upload_review_decisions()["upload_review_decisions"]

    assert decisions["decision_count"] >= 6
    assert decisions["auto_apply_allowed"] is False
    assert decisions["owner_confirmation_required"] is True

    for item in decisions["decision_items"]:
        assert item["decision_id"].startswith("VUD-")
        assert item["review_id"].startswith("VUR-")
        assert item["attachment_id"].startswith("VAT-")
        assert item["owner_must_confirm"] is True
        assert item["auto_apply_allowed"] is False
        assert item["reason_auto_apply_blocked"]


def test_gp014_checklist_and_blocked_reasons_exist():
    checklist = get_upload_review_checklist()["upload_review_checklist"]
    blocked = get_upload_review_blocked_reasons()

    assert checklist["total_review_checks"] >= 6
    assert checklist["tower_owned_check_count"] >= 1
    assert checklist["all_checks_auto_complete"] is False
    assert checklist["owner_confirmation_required"] is True
    assert checklist["tower_clearance_required_for_sensitive_steps"] is True

    codes = {reason["code"] for reason in blocked["upload_review_blocked_reasons"]}
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "EXTERNAL_ACCESS_DENIED" in codes
    assert "UNREDACTED_PREVIEW_LOCKED" in codes
    assert "NO_AUTO_FILE_COMPLETION" in codes
    assert "OWNER_CONFIRMATION_REQUIRED" in codes


def test_gp014_home_routes_declared():
    home = get_manual_upload_review_home()
    summary = home["review_summary"]

    assert summary["route"] == "/vault/manual-upload-review"
    assert summary["json_route"] == "/vault/manual-upload-review.json"
    assert summary["queue_route"] == "/vault/manual-upload-review-queue.json"
    assert summary["decisions_route"] == "/vault/upload-review-decisions.json"
    assert summary["checklist_route"] == "/vault/upload-review-checklist.json"
    assert summary["blocked_reasons_route"] == "/vault/upload-review-blocked-reasons.json"
    assert summary["gp014_status_route"] == "/vault/gp014-status.json"
    assert summary["raw_body_storage_enabled"] is False
    assert summary["direct_upload_unlocked"] is False


def test_gp014_html_is_dark_and_has_no_white_background_tokens():
    html = render_manual_upload_review_page()
    lowered = html.lower()

    assert "Vault Manual Upload Review" in html
    assert "Archive Vault" in html
    assert "/vault/manual-upload-review.json" in html
    assert "/vault/gp014-status.json" in html

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


def test_gp014_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/manual-upload-review",
        "/vault/manual-upload-review.json",
        "/vault/manual-upload-review-queue.json",
        "/vault/upload-review-decisions.json",
        "/vault/upload-review-checklist.json",
        "/vault/upload-review-blocked-reasons.json",
        "/vault/gp014-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp014_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/manual-upload-review",
        "/vault/manual-upload-review.json",
        "/vault/manual-upload-review-queue.json",
        "/vault/upload-review-decisions.json",
        "/vault/upload-review-checklist.json",
        "/vault/upload-review-blocked-reasons.json",
        "/vault/gp014-status.json",
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
                assert b"Vault Manual Upload Review" in response.data
