"""
Tests for VAULT GIANT PACK 040 — Controlled Packet Assembly Readiness Checkpoint
"""

from pathlib import Path

import pytest

from vault.controlled_packet_assembly_readiness_checkpoint_service import (
    get_controlled_packet_assembly_readiness_checkpoint_home,
    get_controlled_packet_boundary_verification,
    get_controlled_packet_next_section_handoff,
    get_controlled_packet_owner_final_queue,
    get_controlled_packet_readiness_summary,
    get_controlled_packet_safe_continue,
    get_controlled_packet_section_matrix,
    get_gp040_status,
    render_controlled_packet_assembly_readiness_checkpoint_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp040_status_ready_safe_to_continue_not_done():
    status = get_gp040_status()

    assert status["pack"]["id"] == "VAULT_GP040"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["pack"]["section_range"] == "GP031-GP040"
    assert status["pack"]["checkpoint_pack"] is True

    gp040 = status["gp040_status"]
    assert gp040["ready"] is True
    assert gp040["controlled_packet_assembly_readiness_checkpoint_ready"] is True
    assert gp040["controlled_packet_assembly_section_checkpoint_complete"] is True
    assert gp040["gp031_to_gp039_verified"] is True
    assert gp040["all_expected_packs_present"] is True
    assert gp040["all_expected_packs_ready"] is True
    assert gp040["all_expected_packs_safe_to_continue"] is True
    assert gp040["safe_to_continue_to_gp041"] is True
    assert gp040["vault_done"] is False
    assert gp040["checkpoint_means_safe_to_continue_not_done"] is True
    assert gp040["metadata_only_checkpoint"] is True
    assert gp040["private_checkpoint_only"] is True
    assert gp040["section_id"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert gp040["section_title"] == "Archive Vault — Controlled Packet Assembly Layer"
    assert gp040["section_range"] == "GP031-GP040"
    assert gp040["new_section_starts_after_this_pack"] is True
    assert gp040["clouds_status"] == "parked_do_not_continue_from_vault_gp040"


def test_gp040_truth_keeps_every_restricted_path_locked():
    status = get_gp040_status()
    truth = status["checkpoint_truth"]

    assert truth["controlled_packet_assembly_readiness_checkpoint_enabled"] is True
    assert truth["section_checkpoint_complete"] is True
    assert truth["section_safe_to_continue"] is True
    assert truth["vault_done"] is False
    assert truth["foundation_status"] == "safe_to_continue_not_done"
    assert truth["checkpoint_means_safe_to_continue_not_done"] is True
    assert truth["metadata_only"] is True
    assert truth["private_checkpoint_only"] is True
    assert truth["no_public_vault"] is True

    assert truth["receipt_close_enabled"] is False
    assert truth["receipt_finalization_enabled"] is False
    assert truth["finalized_receipt_count"] == 0
    assert truth["closed_receipt_count"] == 0
    assert truth["official_receipt_claimed_count"] == 0
    assert truth["owner_review_claimed_count"] == 0
    assert truth["tower_ack_claimed_count"] == 0
    assert truth["blocker_ack_claimed_count"] == 0
    assert truth["no_execution_confirmation_claimed_count"] == 0

    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["direct_upload_unlocked"] is False
    assert truth["provider_configured"] is False
    assert truth["external_packet_delivery_enabled"] is False
    assert truth["external_access_enabled"] is False
    assert truth["packet_export_enabled"] is False
    assert truth["unredacted_export_enabled"] is False
    assert truth["raw_export_enabled"] is False
    assert truth["public_packet_proof_enabled"] is False
    assert truth["public_proof_enabled"] is False
    assert truth["portal_access_enabled"] is False

    assert truth["owner_review_required"] is True
    assert truth["owner_confirmation_required"] is True
    assert truth["owner_reviewed_count"] == 0
    assert truth["owner_confirmed_count"] == 0
    assert truth["decision_selected_count"] == 0
    assert truth["completed_count"] == 0

    assert truth["auto_completion_enabled"] is False
    assert truth["auto_confirmation_enabled"] is False
    assert truth["approval_enabled"] is False
    assert truth["execution_engine_enabled"] is False
    assert truth["auto_action_execution_enabled"] is False
    assert truth["financing_decision_enabled"] is False
    assert truth["legal_advice_enabled"] is False
    assert truth["raw_document_verification_claimed"] is False
    assert truth["auto_packet_approval_enabled"] is False
    assert truth["clouds_should_continue"] is False


def test_gp040_tower_authority_and_vault_boundaries():
    status = get_gp040_status()
    tower = status["tower_authority"]
    vault = status["vault_boundary"]

    assert tower["tower_owns_identity"] is True
    assert tower["tower_owns_permissions"] is True
    assert tower["tower_owns_clearance"] is True
    assert tower["tower_owns_step_up"] is True
    assert tower["tower_owns_export_locks"] is True
    assert tower["tower_owns_freeze_revoke"] is True
    assert tower["tower_owns_external_access"] is True
    assert tower["tower_owns_portal_unlocks"] is True
    assert tower["tower_owns_sensitive_visibility"] is True
    assert tower["tower_owns_action_authority_gates"] is True
    assert tower["vault_owns_tower_permissions"] is False

    assert vault["no_public_vault"] is True
    assert vault["direct_raw_upload_unlocked"] is False
    assert vault["permanent_file_body_storage_enabled"] is False
    assert vault["external_access_default"] == "denied"
    assert vault["external_packet_delivery_allowed"] is False
    assert vault["packet_export_allowed"] is False
    assert vault["unredacted_export_allowed"] is False
    assert vault["raw_export_allowed"] is False
    assert vault["redacted_owner_preview_allowed"] is True
    assert vault["sensitive_body_display_in_summary_views"] is False
    assert vault["beneficiary_details_in_summary_views"] is False
    assert vault["broker_secret_storage_allowed"] is False
    assert vault["public_ob_proof_allowed"] is False
    assert vault["public_packet_proof_allowed"] is False
    assert vault["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp040_section_matrix_verifies_gp031_to_gp039():
    matrix = get_controlled_packet_section_matrix()["section_matrix"]

    assert matrix["expected_pack_count"] == 9
    assert matrix["verified_pack_count"] == 9
    assert matrix["ready_pack_count"] == 9
    assert matrix["safe_to_continue_pack_count"] == 9
    assert matrix["all_expected_packs_present"] is True
    assert matrix["all_expected_packs_ready"] is True
    assert matrix["all_expected_packs_safe_to_continue"] is True
    assert matrix["gp039_rollup_pack_count"] == 8
    assert matrix["gp039_rollup_ready_for_gp040"] is True
    assert matrix["section_checkpoint_complete"] is True
    assert matrix["safe_to_continue_to_next_section"] is True
    assert matrix["vault_done"] is False
    assert matrix["clouds_should_continue"] is False

    seen = [item["pack_id"] for item in matrix["section_matrix_items"]]
    assert seen == [
        "VAULT_GP031",
        "VAULT_GP032",
        "VAULT_GP033",
        "VAULT_GP034",
        "VAULT_GP035",
        "VAULT_GP036",
        "VAULT_GP037",
        "VAULT_GP038",
        "VAULT_GP039",
    ]

    for item in matrix["section_matrix_items"]:
        assert item["matrix_id"].startswith("VCPAC-")
        assert item["section"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
        assert item["section_title"] == "Archive Vault — Controlled Packet Assembly Layer"
        assert item["section_range"] == "GP031-GP040"
        assert item["present"] is True
        assert item["ready"] is True
        assert item["safe_to_continue"] is True
        assert item["foundation_status"] == "safe_to_continue_not_done"
        assert item["vault_done"] is False
        assert item["metadata_only_private_layer"] is True
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["execution_allowed"] is False


def test_gp040_boundary_verification_all_locked():
    boundary = get_controlled_packet_boundary_verification()["boundary_verification"]

    assert boundary["boundary_lock_count"] >= 20
    assert boundary["boundary_violation_count"] == 0
    assert boundary["all_boundaries_locked"] is True
    assert boundary["all_restricted_paths_locked"] is True

    assert boundary["raw_file_body_storage_locked"] is True
    assert boundary["direct_upload_locked"] is True
    assert boundary["external_packet_delivery_locked"] is True
    assert boundary["external_access_locked"] is True
    assert boundary["packet_export_locked"] is True
    assert boundary["unredacted_export_locked"] is True
    assert boundary["raw_export_locked"] is True
    assert boundary["public_proof_locked"] is True
    assert boundary["public_packet_proof_locked"] is True
    assert boundary["portal_access_locked"] is True
    assert boundary["receipt_close_locked"] is True
    assert boundary["receipt_finalization_locked"] is True
    assert boundary["approval_locked"] is True
    assert boundary["execution_engine_locked"] is True
    assert boundary["auto_action_execution_locked"] is True
    assert boundary["financing_decision_not_claimed"] is True
    assert boundary["legal_advice_not_claimed"] is True
    assert boundary["raw_verification_not_claimed"] is True
    assert boundary["clouds_parked"] is True
    assert boundary["vault_boundary_no_public_vault"] is True
    assert boundary["vault_boundary_redacted_owner_preview_allowed"] is True
    assert boundary["safe_to_continue_boundary_verification"] is True

    for item in boundary["boundary_lock_items"]:
        assert item["boundary_id"].startswith("VCPBL-")
        assert item["expected_state"] == "locked_or_false"
        assert item["actual_state"] == "locked_or_false"
        assert item["locked"] is True
        assert item["violation"] is False
        assert item["tower_owned_when_applicable"] is True
        assert item["vault_override_allowed"] is False


def test_gp040_readiness_summary_safe_continue_not_done():
    summary = get_controlled_packet_readiness_summary()["readiness_summary"]

    assert summary["readiness_label"] == "CONTROLLED_PACKET_ASSEMBLY_SECTION_SAFE_TO_CONTINUE"
    assert summary["owner_label"] == "Safe to continue Vault. Vault is not done."
    assert summary["section_checkpoint_complete"] is True
    assert summary["safe_to_continue_to_gp041"] is True
    assert summary["vault_done"] is False
    assert summary["clouds_should_continue"] is False
    assert summary["foundation_status"] == "safe_to_continue_not_done"
    assert summary["expected_pack_count"] == 9
    assert summary["verified_pack_count"] == 9
    assert summary["ready_pack_count"] == 9
    assert summary["safe_to_continue_pack_count"] == 9
    assert summary["boundary_violation_count"] == 0
    assert summary["gp039_summary_board_count"] == 7
    assert summary["gp039_controlled_rollup_pack_count"] == 8
    assert summary["closed_receipt_count"] == 0
    assert summary["finalized_receipt_count"] == 0
    assert summary["official_receipt_claimed_count"] == 0
    assert summary["owner_reviewed_count"] == 0
    assert summary["owner_confirmed_count"] == 0
    assert summary["decision_selected_count"] == 0
    assert summary["completed_count"] == 0
    assert summary["metadata_only"] is True
    assert summary["private_checkpoint_only"] is True

    notes = " ".join(summary["readiness_notes"]).lower()
    assert "safe to continue" in notes
    assert "does not mean vault is done" in notes
    assert "clouds remains parked" in notes
    assert "gp041" in notes


def test_gp040_safe_continue_gates_pass():
    safe = get_controlled_packet_safe_continue()["safe_continue"]

    assert safe["safe_continue_gate_count"] == 5
    assert safe["passed_gate_count"] == 5
    assert safe["failed_gate_count"] == 0
    assert safe["safe_to_continue"] is True
    assert safe["safe_to_continue_to_gp041"] is True
    assert safe["vault_done"] is False
    assert safe["clouds_should_continue"] is False
    assert safe["do_not_switch_apps"] is True
    assert safe["continue_vault_aggressively"] is True

    gate_names = {gate["gate_name"] for gate in safe["safe_continue_gates"]}
    assert "GP031-GP039 verified" in gate_names
    assert "All expected packs ready" in gate_names
    assert "Boundary violations zero" in gate_names
    assert "Vault not done" in gate_names
    assert "Clouds parked" in gate_names

    for gate in safe["safe_continue_gates"]:
        assert gate["passed"] is True
        assert gate["required"] is True


def test_gp040_next_section_handoff_ready_but_not_clouds():
    handoff = get_controlled_packet_next_section_handoff()["next_section_handoff"]

    assert handoff["next_section_id"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert handoff["next_section_title"] == "Archive Vault — Next Product Depth Layer"
    assert handoff["next_section_start_pack"] == "VAULT_GP041"
    assert handoff["new_section_starts_after_gp040"] is True
    assert handoff["current_section_closed_as_checkpoint"] is True
    assert handoff["current_section_safe_to_continue"] is True
    assert handoff["vault_done"] is False
    assert handoff["clouds_should_continue"] is False
    assert handoff["safe_to_continue_to_gp041"] is True
    assert handoff["recommended_next_pack"] == "VAULT_GP041"
    assert handoff["handoff_status"] == "READY_TO_START_NEXT_VAULT_SECTION_AFTER_GP040"

    note = handoff["owner_notebook_note"].lower()
    assert "after gp040 passes and pushes" in note
    assert "new notebook section" in note
    assert "do not continue clouds" in note

    rules = " ".join(handoff["next_section_rules"]).lower()
    assert "tower authority" in rules
    assert "vault private" in rules
    assert "raw storage locked" in rules
    assert "safe to continue, not done" in rules


def test_gp040_owner_final_queue():
    queue = get_controlled_packet_owner_final_queue()["owner_final_queue"]

    assert queue["owner_final_queue_count"] == 4
    assert queue["owner_action_required_count"] == 0
    assert queue["safe_to_continue_item_count"] == 4
    assert queue["section_matrix_verified_pack_count"] == 9
    assert queue["boundary_violation_count"] == 0
    assert queue["gp039_summary_board_count"] == 7
    assert queue["vault_done"] is False
    assert queue["clouds_should_continue"] is False
    assert queue["safe_to_continue_owner_final_queue"] is True

    titles = {item["title"] for item in queue["owner_final_queue_items"]}
    assert "Controlled packet assembly section checkpointed" in titles
    assert "Review next Vault section label before GP041" in titles
    assert "Keep Clouds parked" in titles
    assert "Do not treat Vault as done" in titles

    for item in queue["owner_final_queue_items"]:
        assert item["owner_queue_id"].startswith("VCPFOQ-")
        assert item["owner_action_required"] is False
        assert item["safe_to_continue"] is True


def test_gp040_home_routes_and_counts_declared():
    home = get_controlled_packet_assembly_readiness_checkpoint_home()
    routes = home["checkpoint_routes"]
    counts = home["checkpoint_counts"]

    assert routes["section_header"] == "Archive Vault — Controlled Packet Assembly Layer"
    assert routes["section_range"] == "GP031-GP040"
    assert routes["route"] == "/vault/controlled-packet-assembly-readiness-checkpoint"
    assert routes["json_route"] == "/vault/controlled-packet-assembly-readiness-checkpoint.json"
    assert routes["section_matrix_route"] == "/vault/controlled-packet-section-matrix.json"
    assert routes["boundary_verification_route"] == "/vault/controlled-packet-boundary-verification.json"
    assert routes["readiness_summary_route"] == "/vault/controlled-packet-readiness-summary.json"
    assert routes["safe_continue_route"] == "/vault/controlled-packet-safe-continue.json"
    assert routes["next_section_handoff_route"] == "/vault/controlled-packet-next-section-handoff.json"
    assert routes["owner_final_queue_route"] == "/vault/controlled-packet-owner-final-queue.json"
    assert routes["gp040_status_route"] == "/vault/gp040-status.json"

    assert counts["expected_pack_count"] == 9
    assert counts["verified_pack_count"] == 9
    assert counts["ready_pack_count"] == 9
    assert counts["safe_to_continue_pack_count"] == 9
    assert counts["boundary_violation_count"] == 0
    assert counts["owner_final_queue_count"] == 4
    assert counts["closed_receipt_count"] == 0
    assert counts["finalized_receipt_count"] == 0
    assert counts["official_receipt_claimed_count"] == 0
    assert counts["metadata_only"] is True

    assert home["gp039_connection"]["gp039_ready"] is True
    assert home["gp039_connection"]["gp039_safe_to_continue"] is True
    assert home["gp039_connection"]["gp039_vault_done"] is False
    assert home["gp039_connection"]["gp039_summary_board_count"] == 7
    assert home["gp039_connection"]["gp039_controlled_rollup_pack_count"] == 8


def test_gp040_html_is_dark_and_has_no_white_background_tokens():
    html = render_controlled_packet_assembly_readiness_checkpoint_page()
    lowered = html.lower()

    assert "Vault Controlled Packet Assembly Readiness Checkpoint" in html
    assert "Archive Vault" in html
    assert "/vault/controlled-packet-assembly-readiness-checkpoint.json" in html
    assert "/vault/gp040-status.json" in html
    assert "Clouds parked" in html
    assert "Vault not done" in html

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


def test_gp040_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/controlled-packet-assembly-readiness-checkpoint",
        "/vault/controlled-packet-assembly-readiness-checkpoint.json",
        "/vault/controlled-packet-section-matrix.json",
        "/vault/controlled-packet-boundary-verification.json",
        "/vault/controlled-packet-readiness-summary.json",
        "/vault/controlled-packet-safe-continue.json",
        "/vault/controlled-packet-next-section-handoff.json",
        "/vault/controlled-packet-owner-final-queue.json",
        "/vault/gp040-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp040_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/controlled-packet-assembly-readiness-checkpoint",
        "/vault/controlled-packet-assembly-readiness-checkpoint.json",
        "/vault/controlled-packet-section-matrix.json",
        "/vault/controlled-packet-boundary-verification.json",
        "/vault/controlled-packet-readiness-summary.json",
        "/vault/controlled-packet-safe-continue.json",
        "/vault/controlled-packet-next-section-handoff.json",
        "/vault/controlled-packet-owner-final-queue.json",
        "/vault/gp040-status.json",
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
                assert b"Vault Controlled Packet Assembly Readiness Checkpoint" in response.data
