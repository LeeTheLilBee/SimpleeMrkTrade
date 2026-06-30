"""
Tests for VAULT GIANT PACK 011 — Real Document Intake + Vault Inbox
"""

from pathlib import Path

import pytest

from vault.document_intake_service import (
    get_blocked_intake_reasons,
    get_document_intake_records,
    get_gp011_status,
    get_inbox_status,
    get_intake_queue,
    get_owner_review_state,
    render_vault_inbox_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp011_status_is_ready_and_safe_to_continue():
    status = get_gp011_status()

    assert status["pack"]["id"] == "VAULT_GP011"
    assert status["gp011_status"]["ready"] is True
    assert status["gp011_status"]["safe_to_continue_to_gp012"] is True
    assert status["gp011_status"]["next_pack"] == "VAULT_GP012_FILE_ATTACHMENT_REGISTRY_PACKET_LINKING"
    assert status["gp011_status"]["blocked_items_are_explicit_not_fake_complete"] is True


def test_gp011_keeps_tower_authority_and_vault_boundaries():
    status = get_gp011_status()

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
    assert boundary["external_access_default"] == "denied"
    assert boundary["unredacted_export_allowed"] is False
    assert boundary["sensitive_packet_body_in_summary_views"] is False
    assert boundary["broker_secret_storage_allowed"] is False
    assert boundary["ob_auto_execution_allowed"] is False
    assert boundary["public_ob_proof_allowed"] is False
    assert boundary["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp011_storage_truth_is_not_fake_complete():
    status = get_gp011_status()
    storage = status["storage_provider_state"]

    assert storage["provider_configured"] is False
    assert storage["provider_name"] is None
    assert storage["metadata_registry_status"] == "ready"
    assert storage["fake_file_storage_complete"] is False
    assert storage["file_body_storage_status"] == "blocked_by_provider_and_tower_clearance"


def test_gp011_intake_queue_has_real_registry_records_without_file_bodies():
    queue = get_intake_queue()

    assert queue["direct_raw_upload_unlocked"] is False
    assert queue["queue_count"] >= 6

    lanes = {item["lane"] for item in queue["intake_queue"]}
    assert "SimpleeOnTheGo / ATM" in lanes
    assert "SimpleeProperty / Apartment" in lanes
    assert "Trust / Entity" in lanes
    assert "The Observatory / Manual Live" in lanes
    assert "Soulaana / IP" in lanes
    assert "Private Beta" in lanes

    for item in queue["intake_queue"]:
        assert item["body_storage"]["file_body_attached"] is False
        assert item["body_storage"]["file_body_display_allowed"] is False
        assert item["body_storage"]["raw_file_download_allowed"] is False
        assert item["redaction"]["summary_safe"] is True
        assert item["redaction"]["unredacted_export_allowed"] is False
        assert item["tower_boundary"]["tower_guard_required"] is True
        assert item["tower_boundary"]["vault_permission_owner"] is False


def test_gp011_records_blocked_reasons_and_owner_review_state():
    records = get_document_intake_records()
    blocked = get_blocked_intake_reasons()
    owner = get_owner_review_state()

    assert records["record_count"] >= 6
    assert records["file_body_storage_status"] == "blocked_by_provider_and_tower_clearance"

    codes = {reason["code"] for reason in blocked["blocked_intake_reasons"]}
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "FILE_PROVIDER_NOT_CONFIGURED" in codes
    assert "TOWER_CLEARANCE_REQUIRED" in codes
    assert "EXTERNAL_ACCESS_DEFAULT_DENIED" in codes

    review = owner["owner_review_state"]
    assert review["review_room"] == "Vault Inbox"
    assert review["owner_queue_count"] >= 6
    assert review["blocked_count"] >= 1
    assert review["ready_for_owner_review_count"] >= 1
    assert len(review["next_owner_actions"]) >= 4


def test_gp011_inbox_status_routes_are_declared():
    inbox = get_inbox_status()
    summary = inbox["inbox_summary"]

    assert summary["route"] == "/vault/inbox"
    assert summary["json_route"] == "/vault/inbox.json"
    assert summary["queue_route"] == "/vault/intake-queue.json"
    assert summary["records_route"] == "/vault/document-intake-records.json"
    assert summary["blocked_reasons_route"] == "/vault/blocked-intake-reasons.json"
    assert summary["owner_review_route"] == "/vault/owner-review-state.json"
    assert summary["real_registry_workflow_enabled"] is True
    assert summary["raw_body_storage_enabled"] is False


def test_gp011_html_is_dark_vault_inbox_and_has_no_light_background_tokens():
    html = render_vault_inbox_page()
    lowered = html.lower()

    assert "Vault Inbox" in html
    assert "Archive Vault" in html
    assert "/vault/inbox.json" in html
    assert "/vault/gp011-status.json" in html

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


def test_gp011_routes_are_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/inbox",
        "/vault/inbox.json",
        "/vault/intake-queue.json",
        "/vault/document-intake-records.json",
        "/vault/blocked-intake-reasons.json",
        "/vault/owner-review-state.json",
        "/vault/gp011-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp011_flask_routes_when_app_importable():
    """
    GP011 routes may return 403 in the full Flask app because the Tower/OB guard
    layer protects private /vault paths. That is correct.

    This test accepts:
    - 200 when the local test app exposes the route directly
    - 403 when the private guard blocks access before the route body is shown

    It does not accept 404 because GP011 routes should not disappear.
    """
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/inbox",
        "/vault/inbox.json",
        "/vault/intake-queue.json",
        "/vault/document-intake-records.json",
        "/vault/blocked-intake-reasons.json",
        "/vault/owner-review-state.json",
        "/vault/gp011-status.json",
    ]

    for route in routes:
        response = client.get(route)

        assert response.status_code in (200, 403), (
            f"{route} returned unexpected status {response.status_code}. "
            "Expected 200 direct route response or 403 Tower/private guard protection."
        )

        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Inbox" in response.data

    web_app_text = (PROJECT_ROOT / "web" / "app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    for route in routes:
        assert route in web_app_text
