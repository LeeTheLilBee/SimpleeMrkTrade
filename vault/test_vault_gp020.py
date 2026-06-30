"""
Tests for VAULT GIANT PACK 020 — Vault Operational Readiness Checkpoint
"""

from pathlib import Path

import pytest

from vault.operational_readiness_checkpoint_service import (
    EXPECTED_PACKS,
    EXPECTED_ROUTES,
    GP020_ROUTES,
    get_gp020_status,
    get_operational_readiness_boundaries,
    get_operational_readiness_checkpoint,
    get_operational_readiness_home,
    get_operational_readiness_owner_queue,
    get_operational_readiness_routes,
    render_operational_readiness_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp020_status_ready_safe_to_continue_not_done():
    status = get_gp020_status()

    assert status["pack"]["id"] == "VAULT_GP020"
    assert status["gp020_status"]["ready"] is True
    assert status["gp020_status"]["operational_readiness_checkpoint_complete"] is True
    assert status["gp020_status"]["gp011_to_gp019_verified"] is True
    assert status["gp020_status"]["safe_to_continue_to_gp021"] is True
    assert status["gp020_status"]["vault_done"] is False
    assert status["gp020_status"]["foundation_checkpoint_means_safe_to_continue"] is True
    assert status["gp020_status"]["do_not_jump_apps_after_checkpoint"] is True
    assert status["gp020_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp020"


def test_gp020_checkpoint_truth_keeps_clouds_parked_and_rejects_fake_completion():
    status = get_gp020_status()
    truth = status["checkpoint_truth"]

    assert truth["gp020_is_final_readiness_for_gp011_to_gp019_body"] is True
    assert truth["vault_done"] is False
    assert truth["safe_to_continue_past_checkpoint"] is True
    assert truth["clouds_should_continue"] is False
    assert truth["clouds_status"] == "parked_do_not_continue_from_vault_gp020"
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["direct_upload_unlocked"] is False
    assert truth["provider_configured"] is False
    assert truth["public_proof_enabled"] is False
    assert truth["external_access_enabled"] is False
    assert truth["unredacted_export_enabled"] is False
    assert truth["raw_export_enabled"] is False
    assert truth["seller_or_trustee_portals_enabled"] is False
    assert truth["financing_decisions_enabled"] is False
    assert truth["legal_advice_enabled"] is False
    assert truth["fake_completion_claimed"] is False


def test_gp020_pack_matrix_verifies_gp011_to_gp019():
    checkpoint = get_operational_readiness_checkpoint()
    matrix = checkpoint["pack_matrix"]

    assert matrix["expected_pack_count"] == 9
    assert matrix["verified_pack_count"] == 9
    assert matrix["all_expected_packs_present"] is True
    assert matrix["all_expected_packs_ready"] is True
    assert matrix["safe_to_continue_stack"] is True

    seen = {item["pack_id"] for item in matrix["pack_items"]}
    assert set(EXPECTED_PACKS) == seen

    for item in matrix["pack_items"]:
        assert item["present"] is True
        assert item["ready"] is True
        assert item["safe_to_continue"] is True
        assert item["foundation_status"] == "safe_to_continue_not_done"
        assert item["product_depth_layer"] != "unknown"


def test_gp020_product_depth_matrix_is_real_depth_not_foundation_only():
    checkpoint = get_operational_readiness_checkpoint()
    depth = checkpoint["product_depth_matrix"]

    assert depth["product_depth_layer_count"] == 9
    assert depth["all_product_depth_layers_ready"] is True
    assert depth["foundation_only"] is False
    assert depth["real_product_depth_started"] is True

    layers = {item["layer"] for item in depth["product_depth_items"]}
    assert "real_document_intake_inbox" in layers
    assert "file_attachment_registry_packet_linking" in layers
    assert "metadata_document_classifier_requirement_match" in layers
    assert "manual_upload_review_queue" in layers
    assert "version_history_replace_supersede_flow" in layers
    assert "evidence_binder_builder" in layers
    assert "atm_route_packet_workspace_v2" in layers
    assert "apartment_lender_packet_workspace_v2" in layers
    assert "trust_entity_binder_workspace_v2" in layers


def test_gp020_boundary_matrix_all_boundaries_locked():
    boundaries = get_operational_readiness_boundaries()
    matrix = boundaries["boundary_matrix"]

    assert matrix["all_boundaries_locked"] is True
    assert matrix["tower_authority_preserved"] is True
    assert matrix["vault_permission_ownership_rejected"] is True
    assert matrix["locked_boundary_count"] >= 17

    boundary_names = {item["boundary"] for item in matrix["boundary_items"]}
    assert "raw_file_body_storage" in boundary_names
    assert "direct_upload" in boundary_names
    assert "permanent_storage_provider" in boundary_names
    assert "external_access" in boundary_names
    assert "public_proof" in boundary_names
    assert "raw_export" in boundary_names
    assert "unredacted_export" in boundary_names
    assert "seller_portal" in boundary_names
    assert "trustee_portal" in boundary_names
    assert "financing_decision" in boundary_names
    assert "legal_advice" in boundary_names
    assert "legal_sufficiency_claim" in boundary_names
    assert "raw_document_verification_claims" in boundary_names
    assert "beneficiary_summary_exposure" in boundary_names
    assert "vault_owned_tower_permissions" in boundary_names

    for item in matrix["boundary_items"]:
        assert item["locked"] is True


def test_gp020_tower_authority_and_vault_boundaries_are_preserved():
    boundaries = get_operational_readiness_boundaries()
    tower = boundaries["tower_authority"]
    vault = boundaries["vault_boundary"]

    assert tower["tower_owns_identity"] is True
    assert tower["tower_owns_permissions"] is True
    assert tower["tower_owns_clearance"] is True
    assert tower["tower_owns_step_up"] is True
    assert tower["tower_owns_export_locks"] is True
    assert tower["tower_owns_freeze_revoke"] is True
    assert tower["tower_owns_external_access"] is True
    assert tower["tower_owns_portal_unlocks"] is True
    assert tower["tower_owns_sensitive_visibility"] is True
    assert tower["vault_owns_tower_permissions"] is False

    assert vault["no_public_vault"] is True
    assert vault["direct_raw_upload_unlocked"] is False
    assert vault["permanent_file_body_storage_enabled"] is False
    assert vault["external_access_default"] == "denied"
    assert vault["unredacted_export_allowed"] is False
    assert vault["raw_export_allowed"] is False
    assert vault["redacted_owner_preview_allowed"] is True
    assert vault["sensitive_body_display_in_summary_views"] is False
    assert vault["beneficiary_details_in_summary_views"] is False
    assert vault["broker_secret_storage_allowed"] is False
    assert vault["public_ob_proof_allowed"] is False
    assert vault["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp020_route_matrix_declares_all_expected_routes():
    routes = get_operational_readiness_routes()
    matrix = routes["route_matrix"]

    assert matrix["expected_prior_route_count"] == len(EXPECTED_ROUTES)
    assert matrix["gp020_route_count"] == len(GP020_ROUTES)
    assert matrix["route_expectations_ready"] is True
    assert matrix["tower_guard_403_is_acceptable"] is True
    assert matrix["route_404_is_not_acceptable"] is True

    prior_routes = {item["route"] for item in matrix["expected_prior_routes"]}
    gp020_routes = {item["route"] for item in matrix["gp020_routes"]}

    for route in EXPECTED_ROUTES:
        assert route in prior_routes

    for route in GP020_ROUTES:
        assert route in gp020_routes


def test_gp020_owner_queue_says_continue_vault_not_clouds():
    owner = get_operational_readiness_owner_queue()["owner_review_state"]

    assert owner["review_room"] == "Vault Operational Readiness Checkpoint"
    assert owner["action_count"] >= 6
    assert owner["owner_review_needed_count"] >= 1
    assert owner["tower_owned_action_count"] >= 1
    assert owner["auto_complete_allowed"] is False

    joined = " ".join(owner["next_owner_actions"]).lower()
    assert "do not treat gp020 as vault done" in joined
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined


def test_gp020_readiness_score_is_100_and_safe_to_continue():
    home = get_operational_readiness_home()
    score = home["readiness_score"]
    summary = home["readiness_summary"]

    assert score["score"] == 100
    assert score["label"] == "Vault operational readiness checkpoint passed"
    assert score["safe_to_continue_to_gp021"] is True
    assert score["vault_done"] is False

    assert summary["verified_pack_count"] == 9
    assert summary["expected_pack_count"] == 9
    assert summary["product_depth_layer_count"] == 9
    assert summary["readiness_score"] == 100


def test_gp020_html_is_dark_and_has_no_white_background_tokens():
    html = render_operational_readiness_page()
    lowered = html.lower()

    assert "Vault Operational Readiness" in html
    assert "Archive Vault" in html
    assert "/vault/operational-readiness.json" in html
    assert "/vault/gp020-status.json" in html
    assert "Clouds parked" in html

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


def test_gp020_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/operational-readiness",
        "/vault/operational-readiness.json",
        "/vault/operational-readiness-checkpoint.json",
        "/vault/operational-readiness-routes.json",
        "/vault/operational-readiness-boundaries.json",
        "/vault/operational-readiness-owner-queue.json",
        "/vault/gp020-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp020_flask_routes_when_app_importable_accepts_tower_guard():
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
        "/vault/operational-readiness",
        "/vault/operational-readiness.json",
        "/vault/operational-readiness-checkpoint.json",
        "/vault/operational-readiness-routes.json",
        "/vault/operational-readiness-boundaries.json",
        "/vault/operational-readiness-owner-queue.json",
        "/vault/gp020-status.json",
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
                assert b"Vault Operational Readiness" in response.data
