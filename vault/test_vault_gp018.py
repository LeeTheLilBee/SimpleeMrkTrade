"""
Tests for VAULT GIANT PACK 018 — Apartment Lender Packet Workspace v2
"""

from pathlib import Path

import pytest

from vault.apartment_lender_packet_workspace_v2_service import (
    get_apartment_blocked_reasons,
    get_apartment_due_diligence,
    get_apartment_financial_review,
    get_apartment_lender_packet,
    get_apartment_lender_workspace_home,
    get_apartment_owner_actions,
    get_gp018_status,
    render_apartment_lender_workspace_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp018_status_ready_and_safe_to_continue():
    status = get_gp018_status()

    assert status["pack"]["id"] == "VAULT_GP018"
    assert status["gp018_status"]["ready"] is True
    assert status["gp018_status"]["safe_to_continue_to_gp019"] is True
    assert status["gp018_status"]["next_pack"] == "VAULT_GP019_TRUST_ENTITY_BINDER_WORKSPACE_V2"
    assert status["gp018_status"]["gp016_apartment_binder_connected"] is True
    assert status["gp018_status"]["apartment_lender_workspace_ready"] is True
    assert status["gp018_status"]["metadata_only_workspace"] is True
    assert status["gp018_status"]["direct_upload_still_locked"] is True
    assert status["gp018_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp018_status"]["seller_broker_portal_still_locked"] is True
    assert status["gp018_status"]["external_lender_share_still_locked"] is True
    assert status["gp018_status"]["financing_decision_not_claimed"] is True
    assert status["gp018_status"]["rent_roll_verification_not_claimed"] is True
    assert status["gp018_status"]["t12_verification_not_claimed"] is True
    assert status["gp018_status"]["noi_dscr_verification_not_claimed"] is True


def test_gp018_workspace_truth_keeps_sensitive_paths_locked():
    status = get_gp018_status()
    truth = status["workspace_truth"]

    assert truth["workspace_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["direct_upload_unlocked"] is False
    assert truth["provider_configured"] is False
    assert truth["seller_broker_portal_enabled"] is False
    assert truth["external_lender_share_enabled"] is False
    assert truth["raw_export_enabled"] is False
    assert truth["unredacted_preview_enabled"] is False
    assert truth["redacted_owner_preview_enabled"] is True
    assert truth["auto_acquisition_approval_enabled"] is False
    assert truth["financing_decision_enabled"] is False
    assert truth["rent_roll_verified_from_raw_documents"] is False
    assert truth["t12_verified_from_raw_documents"] is False
    assert truth["noi_dscr_final_or_verified"] is False
    assert truth["appraisal_inspection_title_verified"] is False
    assert truth["fake_lender_packet_complete"] is False


def test_gp018_keeps_tower_authority_and_vault_boundaries():
    status = get_gp018_status()
    tower = status["tower_authority"]
    boundary = status["vault_boundary"]

    assert tower["tower_owns_identity"] is True
    assert tower["tower_owns_permissions"] is True
    assert tower["tower_owns_clearance"] is True
    assert tower["tower_owns_step_up"] is True
    assert tower["tower_owns_export_locks"] is True
    assert tower["tower_owns_freeze_revoke"] is True
    assert tower["tower_owns_external_access"] is True
    assert tower["tower_owns_seller_broker_portal_unlock"] is True
    assert tower["tower_owns_lender_share_unlock"] is True
    assert tower["vault_owns_tower_permissions"] is False

    assert boundary["no_public_vault"] is True
    assert boundary["direct_raw_upload_unlocked"] is False
    assert boundary["permanent_file_body_storage_enabled"] is False
    assert boundary["external_access_default"] == "denied"
    assert boundary["unredacted_export_allowed"] is False
    assert boundary["raw_export_allowed"] is False
    assert boundary["redacted_owner_preview_allowed"] is True
    assert boundary["seller_broker_portal_allowed"] is False
    assert boundary["external_lender_share_allowed"] is False
    assert boundary["sensitive_body_display_in_summary_views"] is False
    assert boundary["broker_secret_storage_allowed"] is False
    assert boundary["public_ob_proof_allowed"] is False
    assert boundary["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp018_apartment_packet_requirements_are_metadata_only():
    packet = get_apartment_lender_packet()["apartment_lender_packet"]

    assert packet["packet_id"] == "apartment_lender_packet_v2"
    assert packet["source_binder_id"] == "VEB-APT-LENDER-001"
    assert packet["lane"] == "SimpleeProperty / Apartment"
    assert packet["requirements_total"] >= 7
    assert packet["requirements_raw_body_available"] == 0
    assert packet["seller_packet_truth"]["seller_packet_received_as_raw_body"] is False
    assert packet["seller_packet_truth"]["rent_roll_verified_from_raw_document"] is False
    assert packet["seller_packet_truth"]["t12_verified_from_raw_document"] is False
    assert packet["seller_packet_truth"]["seller_broker_portal_enabled"] is False
    assert packet["seller_packet_truth"]["external_lender_access_enabled"] is False
    assert packet["seller_packet_truth"]["fake_lender_packet_complete"] is False
    assert packet["redacted_owner_preview"]["available"] is True
    assert packet["redacted_owner_preview"]["raw_values_hidden"] is True
    assert packet["redacted_owner_preview"]["unredacted_preview_allowed"] is False

    requirement_ids = {item["requirement_id"] for item in packet["requirements"]}
    assert "apt_rent_roll" in requirement_ids
    assert "apt_t12_operating_statement" in requirement_ids
    assert "apt_noi_dscr_snapshot" in requirement_ids
    assert "apt_property_tax_insurance" in requirement_ids
    assert "apt_title_survey" in requirement_ids
    assert "apt_inspection_capex" in requirement_ids
    assert "apt_lender_packet_requirements" in requirement_ids

    for item in packet["requirements"]:
        assert item["required"] is True
        assert item["raw_body_available"] is False
        assert item["owner_confirmed"] is False


def test_gp018_due_diligence_lanes_are_ready_but_not_auto_passed():
    due_diligence = get_apartment_due_diligence()["apartment_due_diligence"]

    assert due_diligence["workspace"] == "Apartment Due Diligence"
    assert due_diligence["source_binder_id"] == "VEB-APT-LENDER-001"
    assert due_diligence["lane_count"] >= 7
    assert due_diligence["metadata_review_ready_count"] == due_diligence["lane_count"]
    assert due_diligence["raw_body_available_count"] == 0
    assert due_diligence["tower_clearance_required_count"] >= 1
    assert due_diligence["owner_confirmation_required"] is True
    assert due_diligence["auto_due_diligence_pass_allowed"] is False

    lane_ids = {lane["lane_id"] for lane in due_diligence["lanes"]}
    assert "apt_dd_property_identity" in lane_ids
    assert "apt_dd_seller_broker" in lane_ids
    assert "apt_dd_rent_roll" in lane_ids
    assert "apt_dd_t12_noi" in lane_ids
    assert "apt_dd_lender_packet" in lane_ids
    assert "apt_dd_inspection_capex" in lane_ids
    assert "apt_dd_title_survey" in lane_ids

    for lane in due_diligence["lanes"]:
        assert lane["status"] == "metadata_review_ready"
        assert lane["raw_body_available"] is False
        assert lane["owner_confirmed"] is False
        assert "RAW_FILE_BODY_LOCKED" in lane["blocked_codes"]
        assert "DIRECT_UPLOAD_LOCKED" in lane["blocked_codes"]


def test_gp018_financial_review_is_placeholder_not_financing_decision():
    review = get_apartment_financial_review()["apartment_financial_review"]

    assert review["review_id"] == "APT-FIN-REVIEW-GP018"
    assert review["financial_review_mode"] == "metadata_placeholders_only"
    assert review["financing_decision_enabled"] is False
    assert review["bank_submission_enabled"] is False
    assert review["external_lender_share_enabled"] is False
    assert review["rent_roll_verified_from_raw_documents"] is False
    assert review["t12_verified_from_raw_documents"] is False
    assert review["noi_dscr_final_or_verified"] is False
    assert review["appraisal_inspection_title_verified"] is False
    assert review["loan_packet_tracking"]["enabled"] is True
    assert review["loan_packet_tracking"]["final_loan_amount_known"] is False
    assert review["loan_packet_tracking"]["raw_statement_support_available"] is False

    field_ids = {field["field_id"] for field in review["review_fields"]}
    assert "asking_price" in field_ids
    assert "unit_count" in field_ids
    assert "rent_roll_income" in field_ids
    assert "t12_expenses" in field_ids
    assert "noi" in field_ids
    assert "dscr" in field_ids
    assert "lender_packet_readiness" in field_ids

    for field in review["review_fields"]:
        assert field["raw_support_available"] is False
        assert field["owner_confirmed"] is False

    assert "NO_FINANCING_DECISION" in review["blocked_codes"]
    assert "NO_RENT_ROLL_VERIFICATION_CLAIM" in review["blocked_codes"]
    assert "NO_T12_VERIFICATION_CLAIM" in review["blocked_codes"]
    assert "NO_NOI_DSCR_CLAIM" in review["blocked_codes"]


def test_gp018_owner_actions_and_blocked_reasons_exist():
    actions = get_apartment_owner_actions()["apartment_owner_actions"]
    blocked = get_apartment_blocked_reasons()

    assert actions["review_room"] == "Vault Apartment Lender Packet Workspace"
    assert actions["source_binder_id"] == "VEB-APT-LENDER-001"
    assert actions["action_count"] >= 6
    assert actions["owner_review_needed_count"] >= 1
    assert actions["tower_owned_action_count"] >= 1
    assert actions["auto_complete_allowed"] is False

    codes = {reason["code"] for reason in blocked["apartment_blocked_reasons"]}
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "SELLER_BROKER_PORTAL_LOCKED" in codes
    assert "EXTERNAL_LENDER_SHARE_LOCKED" in codes
    assert "RAW_EXPORT_LOCKED" in codes
    assert "NO_AUTO_ACQUISITION_APPROVAL" in codes
    assert "NO_FINANCING_DECISION" in codes
    assert "NO_RENT_ROLL_VERIFICATION_CLAIM" in codes
    assert "NO_T12_VERIFICATION_CLAIM" in codes
    assert "NO_NOI_DSCR_CLAIM" in codes
    assert "NO_APPRAISAL_INSPECTION_TITLE_CLAIM" in codes


def test_gp018_home_routes_declared():
    home = get_apartment_lender_workspace_home()
    summary = home["workspace_summary"]

    assert summary["route"] == "/vault/apartment-lender-workspace"
    assert summary["json_route"] == "/vault/apartment-lender-workspace.json"
    assert summary["packet_route"] == "/vault/apartment-lender-packet.json"
    assert summary["due_diligence_route"] == "/vault/apartment-due-diligence.json"
    assert summary["financial_review_route"] == "/vault/apartment-financial-review.json"
    assert summary["owner_actions_route"] == "/vault/apartment-owner-actions.json"
    assert summary["blocked_reasons_route"] == "/vault/apartment-blocked-reasons.json"
    assert summary["gp018_status_route"] == "/vault/gp018-status.json"
    assert summary["metadata_only"] is True


def test_gp018_html_is_dark_and_has_no_white_background_tokens():
    html = render_apartment_lender_workspace_page()
    lowered = html.lower()

    assert "Vault Apartment Lender Packet Workspace" in html
    assert "Archive Vault" in html
    assert "/vault/apartment-lender-workspace.json" in html
    assert "/vault/gp018-status.json" in html

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


def test_gp018_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/apartment-lender-workspace",
        "/vault/apartment-lender-workspace.json",
        "/vault/apartment-lender-packet.json",
        "/vault/apartment-due-diligence.json",
        "/vault/apartment-financial-review.json",
        "/vault/apartment-owner-actions.json",
        "/vault/apartment-blocked-reasons.json",
        "/vault/gp018-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp018_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/apartment-lender-workspace",
        "/vault/apartment-lender-workspace.json",
        "/vault/apartment-lender-packet.json",
        "/vault/apartment-due-diligence.json",
        "/vault/apartment-financial-review.json",
        "/vault/apartment-owner-actions.json",
        "/vault/apartment-blocked-reasons.json",
        "/vault/gp018-status.json",
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
                assert b"Vault Apartment Lender Packet Workspace" in response.data
