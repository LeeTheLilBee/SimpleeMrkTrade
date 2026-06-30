"""
Tests for VAULT GIANT PACK 013 — Document Type Classifier + Requirement Match
"""

from pathlib import Path

import pytest

from vault.document_type_classifier_service import (
    get_classification_blocked_reasons,
    get_classifier_review_queue,
    get_document_classifier_home,
    get_document_type_classifier,
    get_gp013_status,
    get_requirement_match,
    render_document_classifier_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp013_status_ready_and_safe_to_continue():
    status = get_gp013_status()

    assert status["pack"]["id"] == "VAULT_GP013"
    assert status["gp013_status"]["ready"] is True
    assert status["gp013_status"]["safe_to_continue_to_gp014"] is True
    assert status["gp013_status"]["next_pack"] == "VAULT_GP014_MANUAL_UPLOAD_REVIEW_QUEUE"
    assert status["gp013_status"]["gp012_attachment_slots_connected"] is True
    assert status["gp013_status"]["metadata_rule_classifier_ready"] is True
    assert status["gp013_status"]["requirement_matcher_ready"] is True
    assert status["gp013_status"]["ocr_or_body_parse_not_claimed"] is True
    assert status["gp013_status"]["raw_file_body_storage_still_locked"] is True


def test_gp013_classifier_truth_does_not_fake_ocr_or_body_analysis():
    status = get_gp013_status()
    truth = status["classifier_truth"]

    assert truth["classification_mode"] == "metadata_rules_only"
    assert truth["ocr_enabled"] is False
    assert truth["file_body_parse_enabled"] is False
    assert truth["content_extraction_enabled"] is False
    assert truth["raw_body_required_for_gp013"] is False
    assert truth["fake_content_analysis_complete"] is False


def test_gp013_keeps_tower_authority_and_vault_boundaries():
    status = get_gp013_status()
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
    assert boundary["permanent_file_body_storage_enabled"] is False
    assert boundary["external_access_default"] == "denied"
    assert boundary["unredacted_export_allowed"] is False
    assert boundary["sensitive_body_display_in_summary_views"] is False
    assert boundary["broker_secret_storage_allowed"] is False
    assert boundary["public_ob_proof_allowed"] is False
    assert boundary["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp013_classification_records_cover_gp012_attachment_slots():
    classifier = get_document_type_classifier()

    assert classifier["classification_record_count"] >= 6

    required_attachment_ids = {
        "VAT-ATM-SELLER-PACKET-001",
        "VAT-APT-LENDER-DD-001",
        "VAT-TRUST-PROOF-001",
        "VAT-OB-MANUAL-LIVE-001",
        "VAT-SOULAANA-IP-001",
        "VAT-BETA-NDA-001",
    }

    seen_attachment_ids = {record["attachment_id"] for record in classifier["classification_records"]}
    assert required_attachment_ids.issubset(seen_attachment_ids)

    for record in classifier["classification_records"]:
        assert record["classification_id"].startswith("VCL-")
        assert record["predicted_document_type"]
        assert record["predicted_document_label"]
        assert record["confidence"] > 0
        assert record["classification_basis"]["mode"] == "metadata_rules_only"
        assert record["classification_basis"]["file_body_used"] is False
        assert record["classification_basis"]["ocr_used"] is False
        assert record["classification_basis"]["content_parse_used"] is False
        assert record["classification_basis"]["body_storage_required"] is False
        assert record["requirement_match"]["match_id"].startswith("VRM-")
        assert record["tower_boundary"]["tower_guard_required"] is True
        assert record["tower_boundary"]["vault_permission_owner"] is False
        assert record["redaction_boundary"]["summary_safe"] is True
        assert record["redaction_boundary"]["unredacted_preview_allowed"] is False
        assert record["redaction_boundary"]["external_preview_allowed"] is False


def test_gp013_requirement_matches_are_linked_to_packets_and_requirements():
    matches = get_requirement_match()

    assert matches["requirement_match_count"] >= 6

    packet_ids = {match["packet_id"] for match in matches["requirement_matches"]}
    assert "atm_route_acquisition_packet" in packet_ids
    assert "apartment_lender_due_diligence_packet" in packet_ids
    assert "trust_entity_binder" in packet_ids
    assert "ob_manual_live_private_proof_packet" in packet_ids
    assert "soulaana_artist_ip_vault" in packet_ids
    assert "private_beta_onboarding_vault" in packet_ids

    for match in matches["requirement_matches"]:
        assert match["attachment_id"].startswith("VAT-")
        assert match["match_id"].startswith("VRM-")
        assert match["requirement_id"]
        assert match["predicted_document_type"]
        assert match["match_basis"]["metadata_rule"] is True
        assert match["match_basis"]["packet_link_used"] is True
        assert match["match_basis"]["requirement_link_used"] is True
        assert match["match_basis"]["ocr_used"] is False
        assert match["match_basis"]["body_content_used"] is False
        assert match["ready_for_auto_filing"] is False


def test_gp013_review_queue_and_blocked_reasons_exist():
    queue = get_classifier_review_queue()["classifier_review_queue"]
    blocked = get_classification_blocked_reasons()

    assert queue["review_room"] == "Vault Document Classifier"
    assert queue["review_count"] >= 6
    assert queue["needs_owner_review_count"] >= 1
    assert len(queue["next_owner_actions"]) >= 4

    codes = {reason["code"] for reason in blocked["classification_blocked_reasons"]}
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "NO_OCR_OR_CONTENT_PARSE_YET" in codes
    assert "EXTERNAL_ACCESS_DENIED" in codes
    assert "OWNER_CONFIRMATION_REQUIRED" in codes


def test_gp013_home_routes_declared():
    home = get_document_classifier_home()
    summary = home["classifier_summary"]

    assert summary["route"] == "/vault/document-classifier"
    assert summary["json_route"] == "/vault/document-classifier.json"
    assert summary["classifier_route"] == "/vault/document-type-classifier.json"
    assert summary["requirement_match_route"] == "/vault/requirement-match.json"
    assert summary["review_queue_route"] == "/vault/classifier-review-queue.json"
    assert summary["blocked_reasons_route"] == "/vault/classification-blocked-reasons.json"
    assert summary["gp013_status_route"] == "/vault/gp013-status.json"
    assert summary["raw_body_storage_enabled"] is False
    assert summary["ocr_enabled"] is False


def test_gp013_html_is_dark_and_has_no_white_background_tokens():
    html = render_document_classifier_page()
    lowered = html.lower()

    assert "Vault Document Classifier" in html
    assert "Archive Vault" in html
    assert "/vault/document-classifier.json" in html
    assert "/vault/gp013-status.json" in html

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


def test_gp013_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/document-classifier",
        "/vault/document-classifier.json",
        "/vault/document-type-classifier.json",
        "/vault/requirement-match.json",
        "/vault/classifier-review-queue.json",
        "/vault/classification-blocked-reasons.json",
        "/vault/gp013-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp013_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/document-classifier",
        "/vault/document-classifier.json",
        "/vault/document-type-classifier.json",
        "/vault/requirement-match.json",
        "/vault/classifier-review-queue.json",
        "/vault/classification-blocked-reasons.json",
        "/vault/gp013-status.json",
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
                assert b"Vault Document Classifier" in response.data
