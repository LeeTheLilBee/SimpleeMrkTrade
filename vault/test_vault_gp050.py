"""
Tests for VAULT GIANT PACK 050 — Next Product Depth Readiness Checkpoint
"""

from pathlib import Path

import pytest

from vault.next_product_depth_readiness_checkpoint_service import (
    get_gp050_next_section_preview,
    get_gp050_readiness_board,
    get_gp050_section_rollup,
    get_gp050_status,
    get_gp050_tower_closeout_checks,
    get_gp050_unresolved_locks,
    get_next_product_depth_readiness_checkpoint_home,
    render_next_product_depth_readiness_checkpoint_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp050_status_ready_closes_section_not_vault_done():
    status = get_gp050_status()
    gp050 = status["gp050_status"]

    assert status["pack"]["id"] == "VAULT_GP050"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert status["pack"]["section_range"] == "GP041-GP050"
    assert status["pack"]["next_section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert status["pack"]["next_section_range"] == "GP051-GP060"

    assert gp050["ready"] is True
    assert gp050["next_product_depth_readiness_checkpoint_ready"] is True
    assert gp050["section_close_checkpoint_ready"] is True
    assert gp050["section_closed_by_gp050"] is True
    assert gp050["gp041_to_gp050_closed"] is True
    assert gp050["safe_to_continue_to_gp051"] is True
    assert gp050["start_new_section_after_gp050_push"] is True
    assert gp050["next_section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp050["next_section_title"] == "Archive Vault — Storage Provider Prep Layer"
    assert gp050["next_section_range"] == "GP051-GP060"
    assert gp050["next_pack"] == "VAULT_GP051_STORAGE_PROVIDER_SELECTION_PREP"
    assert gp050["next_pack_title"] == "Storage Provider Selection Prep"

    assert gp050["vault_done"] is False
    assert gp050["foundation_status"] == "section_closed_safe_to_continue_not_done"
    assert gp050["metadata_only_checkpoint"] is True
    assert gp050["private_checkpoint_only"] is True
    assert gp050["clouds_status"] == "parked_do_not_continue_from_vault_gp050"


def test_gp050_checkpoint_truth_keeps_all_sensitive_unlocks_zero_or_false():
    status = get_gp050_status()
    truth = status["checkpoint_truth"]

    assert truth["gp050_ready"] is True
    assert truth["section_close_checkpoint_ready"] is True
    assert truth["section_closed_by_gp050"] is True
    assert truth["gp041_to_gp050_closed"] is True
    assert truth["next_product_depth_layer_complete"] is True
    assert truth["safe_to_continue_to_gp051"] is True
    assert truth["start_new_section_after_gp050_push"] is True
    assert truth["metadata_only"] is True
    assert truth["private_checkpoint_only"] is True
    assert truth["vault_done"] is False
    assert truth["clouds_should_continue"] is False

    assert truth["provider_selected"] is False
    assert truth["provider_configured"] is False
    assert truth["provider_write_enabled"] is False
    assert truth["provider_read_enabled"] is False
    assert truth["provider_object_read_claimed"] is False
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["file_body_persisted_count"] == 0
    assert truth["object_body_available_count"] == 0
    assert truth["object_body_view_enabled"] is False
    assert truth["direct_upload_unlocked"] is False
    assert truth["direct_upload_enabled"] is False
    assert truth["checksum_verified_count"] == 0
    assert truth["hash_verified_count"] == 0

    assert truth["official_storage_receipt_claimed_count"] == 0
    assert truth["finalized_storage_receipt_count"] == 0
    assert truth["closed_storage_receipt_count"] == 0
    assert truth["official_action_receipt_claimed_count"] == 0
    assert truth["finalized_action_receipt_count"] == 0
    assert truth["closed_action_receipt_count"] == 0
    assert truth["official_audit_log_written_count"] == 0
    assert truth["immutable_audit_write_count"] == 0
    assert truth["access_request_granted_count"] == 0
    assert truth["decision_granted_count"] == 0
    assert truth["action_approved_count"] == 0
    assert truth["action_executed_count"] == 0

    assert truth["external_packet_delivery_enabled"] is False
    assert truth["packet_export_enabled"] is False
    assert truth["public_proof_enabled"] is False
    assert truth["portal_access_enabled"] is False
    assert truth["approval_enabled"] is False
    assert truth["execution_engine_enabled"] is False


def test_gp050_connected_to_gp049():
    home = get_next_product_depth_readiness_checkpoint_home()
    gp049 = home["gp049_connection"]

    assert gp049["gp049_pack_id"] == "VAULT_GP049"
    assert gp049["gp049_ready"] is True
    assert gp049["gp049_safe_to_continue"] is True
    assert gp049["gp049_vault_done"] is False
    assert gp049["gp049_section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert gp049["gp049_action_receipt_card_count"] == 35
    assert gp049["gp049_blocked_action_receipt_label_count"] == 35
    assert gp049["gp049_tower_action_gate_receipt_count"] == 210
    assert gp049["gp049_followup_receipt_placeholder_count"] == 140
    assert gp049["gp049_no_execution_receipt_count"] == 35
    assert gp049["gp049_action_executed_count"] == 0


def test_gp050_section_rollup_closes_gp041_to_gp050():
    rollup = get_gp050_section_rollup()["section_rollup"]

    assert rollup["section_id"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert rollup["section_title"] == "Archive Vault — Next Product Depth Layer"
    assert rollup["section_range"] == "GP041-GP050"
    assert rollup["section_pack_count"] == 10
    assert rollup["section_ready_pack_count"] == 10
    assert rollup["section_close_checkpoint_count"] == 1
    assert rollup["section_closed_by_gp050"] is True
    assert rollup["gp041_to_gp050_closed"] is True
    assert rollup["next_product_depth_layer_complete"] is True
    assert rollup["safe_to_continue_to_gp051"] is True
    assert rollup["vault_done"] is False
    assert rollup["clouds_should_continue"] is False
    assert rollup["readiness_score"] == 100
    assert rollup["readiness_label"] == "next_product_depth_ready_to_continue"
    assert rollup["gp049_action_receipt_card_count"] == 35
    assert rollup["gp049_no_execution_receipt_count"] == 35
    assert rollup["gp049_action_executed_count"] == 0
    assert rollup["provider_selected_count"] == 0
    assert rollup["object_body_view_enabled_count"] == 0
    assert rollup["official_receipt_claimed_count"] == 0
    assert rollup["action_executed_count"] == 0
    assert rollup["export_allowed_count"] == 0
    assert rollup["execution_allowed_count"] == 0

    pack_ids = [item["pack_id"] for item in rollup["section_rollup_items"]]
    assert pack_ids == [
        "VAULT_GP041",
        "VAULT_GP042",
        "VAULT_GP043",
        "VAULT_GP044",
        "VAULT_GP045",
        "VAULT_GP046",
        "VAULT_GP047",
        "VAULT_GP048",
        "VAULT_GP049",
        "VAULT_GP050",
    ]

    closeout_cards = [item for item in rollup["section_rollup_items"] if item["section_close_checkpoint"]]
    assert len(closeout_cards) == 1
    assert closeout_cards[0]["pack_id"] == "VAULT_GP050"

    for item in rollup["section_rollup_items"]:
        assert item["ready"] is True
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["official_audit_log_written"] is False
        assert item["action_executed"] is False
        assert item["execution_allowed"] is False


def test_gp050_readiness_board_is_100_and_safe_to_continue():
    board = get_gp050_readiness_board()["readiness_board"]

    assert board["readiness_card_count"] == 10
    assert board["ready_card_count"] == 10
    assert board["blocked_or_failed_card_count"] == 0
    assert board["safe_to_continue_to_gp051"] is True
    assert board["section_closed_by_gp050"] is True
    assert board["vault_done"] is False
    assert board["clouds_should_continue"] is False
    assert board["readiness_score"] == 100
    assert board["readiness_label"] == "next_product_depth_ready_to_continue"
    assert board["gp049_ready"] is True
    assert board["gp049_safe_to_continue"] is True
    assert board["gp049_vault_done"] is False

    kinds = {item["readiness_kind"] for item in board["readiness_card_items"]}
    assert kinds == {
        "section_close",
        "gp049_link",
        "metadata_only",
        "tower_authority",
        "provider_locked",
        "object_body_locked",
        "receipt_locked",
        "audit_locked",
        "execution_locked",
        "next_section_ready",
    }

    for item in board["readiness_card_items"]:
        assert item["ready"] is True
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["action_executed"] is False
        assert item["execution_allowed"] is False


def test_gp050_unresolved_locks_carried_forward():
    locks = get_gp050_unresolved_locks()["unresolved_locks"]

    assert locks["unresolved_lock_count"] == 22
    assert locks["active_lock_count"] == 22
    assert locks["blocks_vault_done_count"] == 22
    assert locks["owner_resolvable_now_count"] == 0
    assert locks["tower_authority_required_count"] == 22
    assert locks["provider_selected_count"] == 0
    assert locks["provider_configured_count"] == 0
    assert locks["provider_read_enabled_count"] == 0
    assert locks["provider_write_enabled_count"] == 0
    assert locks["object_body_view_enabled_count"] == 0
    assert locks["official_receipt_claimed_count"] == 0
    assert locks["receipt_finalized_count"] == 0
    assert locks["receipt_closed_count"] == 0
    assert locks["action_approved_count"] == 0
    assert locks["action_executed_count"] == 0
    assert locks["export_allowed_count"] == 0
    assert locks["external_delivery_allowed_count"] == 0
    assert locks["portal_access_allowed_count"] == 0
    assert locks["execution_allowed_count"] == 0
    assert locks["safe_to_continue_unresolved_locks"] is True
    assert locks["safe_to_continue_to_gp051"] is True
    assert locks["gp049_no_execution_receipt_count"] == 35

    lock_names = {item["lock_name"] for item in locks["unresolved_lock_items"]}
    assert "provider_selection_locked" in lock_names
    assert "object_body_view_locked" in lock_names
    assert "action_execution_locked" in lock_names
    assert "packet_export_locked" in lock_names
    assert "public_proof_locked" in lock_names

    for item in locks["unresolved_lock_items"]:
        assert item["active"] is True
        assert item["blocks_vault_done"] is True
        assert item["owner_resolvable_now"] is False
        assert item["tower_authority_required"] is True
        assert item["safe_to_continue_to_gp051"] is True


def test_gp050_tower_closeout_checks_preserve_authority_without_granting():
    checks = get_gp050_tower_closeout_checks()["tower_closeout_checks"]

    assert checks["tower_closeout_check_count"] == 12
    assert checks["tower_authority_required_count"] == 12
    assert checks["tower_authority_preserved_count"] == 12
    assert checks["tower_authority_granted_count"] == 0
    assert checks["vault_override_allowed_count"] == 0
    assert checks["provider_access_unlocked_count"] == 0
    assert checks["object_visibility_unlocked_count"] == 0
    assert checks["receipt_authority_unlocked_count"] == 0
    assert checks["audit_authority_unlocked_count"] == 0
    assert checks["action_authority_unlocked_count"] == 0
    assert checks["execution_unlocked_count"] == 0
    assert checks["export_unlocked_count"] == 0
    assert checks["safe_to_continue_tower_closeout_checks"] is True
    assert checks["safe_to_continue_to_gp051"] is True

    names = {item["check_name"] for item in checks["tower_closeout_check_items"]}
    assert names == {
        "identity_authority",
        "permission_authority",
        "clearance_authority",
        "step_up_authority",
        "storage_provider_authority",
        "storage_access_authority",
        "object_visibility_authority",
        "receipt_authority",
        "audit_authority",
        "action_authority",
        "export_authority",
        "execution_authority",
    }

    for item in checks["tower_closeout_check_items"]:
        assert item["tower_authority_required"] is True
        assert item["tower_authority_preserved"] is True
        assert item["tower_authority_granted_to_vault"] is False
        assert item["vault_can_override"] is False
        assert item["provider_access_unlocked"] is False
        assert item["execution_unlocked"] is False
        assert item["export_unlocked"] is False


def test_gp050_next_section_preview_starts_new_section_after_push():
    preview = get_gp050_next_section_preview()["next_section_preview"]

    assert preview["next_section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert preview["next_section_title"] == "Archive Vault — Storage Provider Prep Layer"
    assert preview["next_section_range"] == "GP051-GP060"
    assert preview["recommended_next_pack"] == "VAULT_GP051_STORAGE_PROVIDER_SELECTION_PREP"
    assert preview["recommended_next_pack_title"] == "Storage Provider Selection Prep"
    assert preview["new_section_should_start_after_gp050_push"] is True
    assert preview["current_section_closed"] is True
    assert preview["current_section_id"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert preview["current_section_range"] == "GP041-GP050"
    assert preview["readiness_score"] == 100
    assert preview["unresolved_lock_count"] == 22
    assert preview["safe_to_continue_to_gp051"] is True
    assert preview["vault_done"] is False
    assert preview["clouds_should_continue"] is False
    assert preview["provider_selected"] is False
    assert preview["provider_configured"] is False
    assert preview["provider_read_enabled"] is False
    assert preview["object_body_view_enabled"] is False
    assert preview["action_executed"] is False
    assert preview["export_allowed"] is False
    assert preview["execution_allowed"] is False

    note = preview["owner_notebook_note"].lower()
    assert "start a new notebook section" in note
    assert "archive vault — storage provider prep layer" in note
    assert "gp051-gp060" in note

    rules = " ".join(preview["carry_forward_rules"]).lower()
    assert "gp041-gp050 is closed" in rules
    assert "start a new notebook section" in rules
    assert "do not switch to clouds" in rules
    assert "not vault done" in rules


def test_gp050_routes_counts_and_boundaries_declared():
    home = get_next_product_depth_readiness_checkpoint_home()
    routes = home["checkpoint_routes"]
    counts = home["checkpoint_counts"]
    tower = home["tower_authority"]
    boundary = home["vault_boundary"]

    assert routes["section_header"] == "Archive Vault — Next Product Depth Layer"
    assert routes["section_range"] == "GP041-GP050"
    assert routes["route"] == "/vault/next-product-depth-readiness-checkpoint"
    assert routes["json_route"] == "/vault/next-product-depth-readiness-checkpoint.json"
    assert routes["section_rollup_route"] == "/vault/gp050-section-rollup.json"
    assert routes["readiness_board_route"] == "/vault/gp050-readiness-board.json"
    assert routes["unresolved_locks_route"] == "/vault/gp050-unresolved-locks.json"
    assert routes["tower_closeout_checks_route"] == "/vault/gp050-tower-closeout-checks.json"
    assert routes["next_section_preview_route"] == "/vault/gp050-next-section-preview.json"
    assert routes["gp050_status_route"] == "/vault/gp050-status.json"

    assert counts["section_pack_count"] == 10
    assert counts["section_ready_pack_count"] == 10
    assert counts["section_closed_count"] == 1
    assert counts["readiness_card_count"] == 10
    assert counts["ready_card_count"] == 10
    assert counts["unresolved_lock_count"] == 22
    assert counts["active_lock_count"] == 22
    assert counts["tower_closeout_check_count"] == 12
    assert counts["tower_authority_required_count"] == 12
    assert counts["tower_authority_granted_count"] == 0
    assert counts["provider_selected_count"] == 0
    assert counts["provider_configured_count"] == 0
    assert counts["provider_read_enabled_count"] == 0
    assert counts["object_body_view_enabled_count"] == 0
    assert counts["official_receipt_count"] == 0
    assert counts["finalized_receipt_count"] == 0
    assert counts["closed_receipt_count"] == 0
    assert counts["official_audit_log_written_count"] == 0
    assert counts["immutable_audit_write_count"] == 0
    assert counts["action_executed_count"] == 0
    assert counts["packet_export_allowed_count"] == 0
    assert counts["execution_allowed_count"] == 0
    assert counts["vault_done_count"] == 0

    assert tower["tower_owns_identity"] is True
    assert tower["tower_owns_action_receipt_authority"] is True
    assert tower["vault_can_mark_vault_done"] is False
    assert tower["vault_can_execute_audit_action"] is False

    assert boundary["provider_prep_default"] == "selection_prep_only_no_provider_selected"
    assert boundary["provider_read_allowed"] is False
    assert boundary["provider_write_allowed"] is False
    assert boundary["object_body_view_allowed"] is False
    assert boundary["audit_action_execution_allowed"] is False
    assert boundary["action_receipt_finalize_allowed"] is False
    assert boundary["public_packet_proof_allowed"] is False


def test_gp050_html_is_dark_and_mentions_new_section():
    html = render_next_product_depth_readiness_checkpoint_page()
    lowered = html.lower()

    assert "Vault Next Product Depth Readiness Checkpoint" in html
    assert "Archive Vault" in html
    assert "GP041–GP050" in html
    assert "Archive Vault — Storage Provider Prep Layer" in html
    assert "GP051-GP060" in html
    assert "/vault/next-product-depth-readiness-checkpoint.json" in html
    assert "/vault/gp050-status.json" in html
    assert "Clouds parked" in html
    assert "Vault not done" in html
    assert "No provider access" in html

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


def test_gp050_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/next-product-depth-readiness-checkpoint",
        "/vault/next-product-depth-readiness-checkpoint.json",
        "/vault/gp050-section-rollup.json",
        "/vault/gp050-readiness-board.json",
        "/vault/gp050-unresolved-locks.json",
        "/vault/gp050-tower-closeout-checks.json",
        "/vault/gp050-next-section-preview.json",
        "/vault/gp050-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp050_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/next-product-depth-readiness-checkpoint",
        "/vault/next-product-depth-readiness-checkpoint.json",
        "/vault/gp050-section-rollup.json",
        "/vault/gp050-readiness-board.json",
        "/vault/gp050-unresolved-locks.json",
        "/vault/gp050-tower-closeout-checks.json",
        "/vault/gp050-next-section-preview.json",
        "/vault/gp050-status.json",
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
                assert b"Vault Next Product Depth Readiness Checkpoint" in response.data
