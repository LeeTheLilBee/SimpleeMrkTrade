"""
Tests for VAULT GIANT PACK 019 — Trust/Entity Binder Workspace v2
"""

from pathlib import Path

import pytest

from vault.trust_entity_binder_workspace_v2_service import (
    get_gp019_status,
    get_trust_entity_authority_map,
    get_trust_entity_binder,
    get_trust_entity_blocked_reasons,
    get_trust_entity_owner_actions,
    get_trust_entity_review,
    get_trust_entity_workspace_home,
    render_trust_entity_workspace_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp019_status_ready_and_safe_to_continue():
    status = get_gp019_status()

    assert status["pack"]["id"] == "VAULT_GP019"
    assert status["gp019_status"]["ready"] is True
    assert status["gp019_status"]["safe_to_continue_to_gp020"] is True
    assert status["gp019_status"]["next_pack"] == "VAULT_GP020_OPERATIONAL_READINESS_CHECKPOINT"
    assert status["gp019_status"]["gp016_trust_entity_binder_connected"] is True
    assert status["gp019_status"]["trust_entity_workspace_ready"] is True
    assert status["gp019_status"]["metadata_only_workspace"] is True
    assert status["gp019_status"]["direct_upload_still_locked"] is True
    assert status["gp019_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp019_status"]["trustee_portal_still_locked"] is True
    assert status["gp019_status"]["external_bank_lender_share_still_locked"] is True
    assert status["gp019_status"]["legal_advice_not_claimed"] is True
    assert status["gp019_status"]["legal_sufficiency_not_claimed"] is True
    assert status["gp019_status"]["trust_document_verification_not_claimed"] is True
    assert status["gp019_status"]["entity_verification_not_claimed"] is True
    assert status["gp019_status"]["beneficiary_summary_exposure_blocked"] is True


def test_gp019_workspace_truth_keeps_sensitive_paths_locked():
    status = get_gp019_status()
    truth = status["workspace_truth"]

    assert truth["workspace_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["direct_upload_unlocked"] is False
    assert truth["provider_configured"] is False
    assert truth["trustee_portal_enabled"] is False
    assert truth["external_bank_lender_share_enabled"] is False
    assert truth["raw_export_enabled"] is False
    assert truth["unredacted_preview_enabled"] is False
    assert truth["redacted_owner_preview_enabled"] is True
    assert truth["auto_authority_approval_enabled"] is False
    assert truth["legal_advice_enabled"] is False
    assert truth["legal_sufficiency_claimed"] is False
    assert truth["trust_document_verified_from_raw_document"] is False
    assert truth["entity_documents_verified_from_raw_documents"] is False
    assert truth["trustee_authority_verified_from_raw_documents"] is False
    assert truth["beneficiary_details_exposed_in_summary"] is False
    assert truth["fake_trust_entity_packet_complete"] is False


def test_gp019_keeps_tower_authority_and_vault_boundaries():
    status = get_gp019_status()
    tower = status["tower_authority"]
    boundary = status["vault_boundary"]

    assert tower["tower_owns_identity"] is True
    assert tower["tower_owns_permissions"] is True
    assert tower["tower_owns_clearance"] is True
    assert tower["tower_owns_step_up"] is True
    assert tower["tower_owns_export_locks"] is True
    assert tower["tower_owns_freeze_revoke"] is True
    assert tower["tower_owns_external_access"] is True
    assert tower["tower_owns_trustee_portal_unlock"] is True
    assert tower["tower_owns_bank_lender_share_unlock"] is True
    assert tower["tower_owns_sensitive_authority_visibility"] is True
    assert tower["vault_owns_tower_permissions"] is False

    assert boundary["no_public_vault"] is True
    assert boundary["direct_raw_upload_unlocked"] is False
    assert boundary["permanent_file_body_storage_enabled"] is False
    assert boundary["external_access_default"] == "denied"
    assert boundary["unredacted_export_allowed"] is False
    assert boundary["raw_export_allowed"] is False
    assert boundary["redacted_owner_preview_allowed"] is True
    assert boundary["trustee_portal_allowed"] is False
    assert boundary["external_bank_lender_share_allowed"] is False
    assert boundary["sensitive_body_display_in_summary_views"] is False
    assert boundary["beneficiary_details_in_summary_views"] is False
    assert boundary["broker_secret_storage_allowed"] is False
    assert boundary["public_ob_proof_allowed"] is False
    assert boundary["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp019_trust_entity_binder_requirements_are_metadata_only():
    binder = get_trust_entity_binder()["trust_entity_binder"]

    assert binder["packet_id"] == "trust_entity_binder_workspace_v2"
    assert binder["source_binder_id"] == "VEB-TRUST-ENTITY-001"
    assert binder["lane"] == "Trust / Entity"
    assert binder["requirements_total"] >= 7
    assert binder["requirements_raw_body_available"] == 0
    assert binder["trust_entity_truth"]["trust_document_received_as_raw_body"] is False
    assert binder["trust_entity_truth"]["trust_document_verified_from_raw_document"] is False
    assert binder["trust_entity_truth"]["entity_documents_verified_from_raw_documents"] is False
    assert binder["trust_entity_truth"]["trustee_authority_verified_from_raw_documents"] is False
    assert binder["trust_entity_truth"]["beneficiary_details_exposed_in_summary"] is False
    assert binder["trust_entity_truth"]["trustee_portal_enabled"] is False
    assert binder["trust_entity_truth"]["external_bank_lender_access_enabled"] is False
    assert binder["trust_entity_truth"]["fake_trust_entity_packet_complete"] is False
    assert binder["redacted_owner_preview"]["available"] is True
    assert binder["redacted_owner_preview"]["restricted_fields_hidden"] is True
    assert binder["redacted_owner_preview"]["raw_values_hidden"] is True
    assert binder["redacted_owner_preview"]["unredacted_preview_allowed"] is False

    requirement_ids = {item["requirement_id"] for item in binder["requirements"]}
    assert "trust_instrument_metadata" in requirement_ids
    assert "trustee_authority_metadata" in requirement_ids
    assert "entity_llc_ein_metadata" in requirement_ids
    assert "bank_lender_authority_packet" in requirement_ids
    assert "acquisition_authority_map" in requirement_ids
    assert "beneficiary_privacy_boundary" in requirement_ids
    assert "operating_agreement_placeholder" in requirement_ids

    for item in binder["requirements"]:
        assert item["required"] is True
        assert item["raw_body_available"] is False
        assert item["owner_confirmed"] is False
        assert item["tower_clearance_required"] is True
        if item["requirement_id"] == "beneficiary_privacy_boundary":
            assert item["summary_safe"] is False


def test_gp019_authority_lanes_are_ready_but_not_auto_approved():
    authority = get_trust_entity_authority_map()["trust_entity_authority_map"]

    assert authority["workspace"] == "Trust/Entity Authority Map"
    assert authority["source_binder_id"] == "VEB-TRUST-ENTITY-001"
    assert authority["lane_count"] >= 7
    assert authority["metadata_review_ready_count"] == authority["lane_count"]
    assert authority["raw_body_available_count"] == 0
    assert authority["tower_clearance_required_count"] >= 1
    assert authority["owner_confirmation_required"] is True
    assert authority["auto_authority_pass_allowed"] is False

    lane_ids = {lane["lane_id"] for lane in authority["lanes"]}
    assert "trust_authority_settlor_trustee" in lane_ids
    assert "trust_authority_successor_trustee" in lane_ids
    assert "trust_authority_entity_ownership" in lane_ids
    assert "trust_authority_bank_lender" in lane_ids
    assert "trust_authority_atm_acquisition" in lane_ids
    assert "trust_authority_property_acquisition" in lane_ids
    assert "trust_privacy_beneficiaries" in lane_ids

    for lane in authority["lanes"]:
        assert lane["status"] == "metadata_review_ready"
        assert lane["raw_body_available"] is False
        assert lane["owner_confirmed"] is False
        assert "RAW_FILE_BODY_LOCKED" in lane["blocked_codes"]
        assert "DIRECT_UPLOAD_LOCKED" in lane["blocked_codes"]
        assert "NO_LEGAL_ADVICE" in lane["blocked_codes"]
        assert "NO_LEGAL_SUFFICIENCY_CLAIM" in lane["blocked_codes"]


def test_gp019_entity_review_does_not_claim_legal_or_raw_verification():
    review = get_trust_entity_review()["trust_entity_review"]

    assert review["review_id"] == "TRUST-ENTITY-REVIEW-GP019"
    assert review["entity_review_mode"] == "metadata_placeholders_only"
    assert review["legal_advice_enabled"] is False
    assert review["legal_sufficiency_claimed"] is False
    assert review["bank_submission_enabled"] is False
    assert review["external_bank_lender_share_enabled"] is False
    assert review["trust_document_verified_from_raw_document"] is False
    assert review["entity_documents_verified_from_raw_documents"] is False
    assert review["trustee_authority_verified_from_raw_documents"] is False
    assert review["beneficiary_details_exposed_in_summary"] is False
    assert review["authority_tracking"]["enabled"] is True
    assert review["authority_tracking"]["final_authority_known"] is False
    assert review["authority_tracking"]["raw_document_support_available"] is False

    field_ids = {field["field_id"] for field in review["review_fields"]}
    assert "trust_name_metadata" in field_ids
    assert "trustee_role_metadata" in field_ids
    assert "entity_llc_metadata" in field_ids
    assert "ein_banking_metadata" in field_ids
    assert "beneficiary_privacy_metadata" in field_ids
    assert "acquisition_authority_metadata" in field_ids

    for field in review["review_fields"]:
        assert field["raw_support_available"] is False
        assert field["owner_confirmed"] is False

    restricted = [field for field in review["review_fields"] if field["field_id"] == "beneficiary_privacy_metadata"][0]
    assert restricted["summary_safe"] is False

    assert "NO_LEGAL_ADVICE" in review["blocked_codes"]
    assert "NO_LEGAL_SUFFICIENCY_CLAIM" in review["blocked_codes"]
    assert "NO_TRUST_DOCUMENT_VERIFICATION_CLAIM" in review["blocked_codes"]
    assert "NO_ENTITY_VERIFICATION_CLAIM" in review["blocked_codes"]
    assert "NO_TRUSTEE_AUTHORITY_VERIFICATION_CLAIM" in review["blocked_codes"]
    assert "NO_BENEFICIARY_DISCLOSURE_IN_SUMMARY" in review["blocked_codes"]


def test_gp019_owner_actions_and_blocked_reasons_exist():
    actions = get_trust_entity_owner_actions()["trust_entity_owner_actions"]
    blocked = get_trust_entity_blocked_reasons()

    assert actions["review_room"] == "Vault Trust/Entity Binder Workspace"
    assert actions["source_binder_id"] == "VEB-TRUST-ENTITY-001"
    assert actions["action_count"] >= 6
    assert actions["owner_review_needed_count"] >= 1
    assert actions["tower_owned_action_count"] >= 1
    assert actions["auto_complete_allowed"] is False

    codes = {reason["code"] for reason in blocked["trust_entity_blocked_reasons"]}
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "TRUSTEE_PORTAL_LOCKED" in codes
    assert "EXTERNAL_BANK_LENDER_SHARE_LOCKED" in codes
    assert "RAW_EXPORT_LOCKED" in codes
    assert "NO_LEGAL_ADVICE" in codes
    assert "NO_LEGAL_SUFFICIENCY_CLAIM" in codes
    assert "NO_TRUST_DOCUMENT_VERIFICATION_CLAIM" in codes
    assert "NO_ENTITY_VERIFICATION_CLAIM" in codes
    assert "NO_TRUSTEE_AUTHORITY_VERIFICATION_CLAIM" in codes
    assert "NO_BENEFICIARY_DISCLOSURE_IN_SUMMARY" in codes


def test_gp019_home_routes_declared():
    home = get_trust_entity_workspace_home()
    summary = home["workspace_summary"]

    assert summary["route"] == "/vault/trust-entity-workspace"
    assert summary["json_route"] == "/vault/trust-entity-workspace.json"
    assert summary["binder_route"] == "/vault/trust-entity-binder.json"
    assert summary["authority_map_route"] == "/vault/trust-entity-authority-map.json"
    assert summary["entity_review_route"] == "/vault/trust-entity-review.json"
    assert summary["owner_actions_route"] == "/vault/trust-entity-owner-actions.json"
    assert summary["blocked_reasons_route"] == "/vault/trust-entity-blocked-reasons.json"
    assert summary["gp019_status_route"] == "/vault/gp019-status.json"
    assert summary["metadata_only"] is True


def test_gp019_html_is_dark_and_has_no_white_background_tokens():
    html = render_trust_entity_workspace_page()
    lowered = html.lower()

    assert "Vault Trust/Entity Binder Workspace" in html
    assert "Archive Vault" in html
    assert "/vault/trust-entity-workspace.json" in html
    assert "/vault/gp019-status.json" in html

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


def test_gp019_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/trust-entity-workspace",
        "/vault/trust-entity-workspace.json",
        "/vault/trust-entity-binder.json",
        "/vault/trust-entity-authority-map.json",
        "/vault/trust-entity-review.json",
        "/vault/trust-entity-owner-actions.json",
        "/vault/trust-entity-blocked-reasons.json",
        "/vault/gp019-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp019_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/trust-entity-workspace",
        "/vault/trust-entity-workspace.json",
        "/vault/trust-entity-binder.json",
        "/vault/trust-entity-authority-map.json",
        "/vault/trust-entity-review.json",
        "/vault/trust-entity-owner-actions.json",
        "/vault/trust-entity-blocked-reasons.json",
        "/vault/gp019-status.json",
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
                assert b"Vault Trust/Entity Binder Workspace" in response.data
