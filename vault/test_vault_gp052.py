"""
Tests for VAULT GIANT PACK 052 — Storage Provider Criteria Board
"""

from pathlib import Path

import pytest

from vault.storage_provider_criteria_board_service import (
    get_gp052_status,
    get_storage_provider_criteria_board_home,
    get_storage_provider_criteria_cards,
    get_storage_provider_criteria_next_step,
    get_storage_provider_criteria_rollups,
    get_storage_provider_criteria_selection_blockers,
    get_storage_provider_criteria_tower_review_gates,
    get_storage_provider_scoring_placeholders,
    render_storage_provider_criteria_board_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp052_status_ready_safe_continue_not_done():
    status = get_gp052_status()
    gp052 = status["gp052_status"]

    assert status["pack"]["id"] == "VAULT_GP052"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert status["pack"]["section_range"] == "GP051-GP060"

    assert gp052["ready"] is True
    assert gp052["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp052["section_title"] == "Archive Vault — Storage Provider Prep Layer"
    assert gp052["section_range"] == "GP051-GP060"
    assert gp052["storage_provider_criteria_board_ready"] is True
    assert gp052["safe_to_continue_to_gp053"] is True
    assert gp052["vault_done"] is False
    assert gp052["foundation_status"] == "safe_to_continue_not_done"
    assert gp052["metadata_only_criteria_board"] is True
    assert gp052["private_criteria_board_only"] is True
    assert gp052["criteria_cards_ready"] is True
    assert gp052["criteria_rollups_ready"] is True
    assert gp052["scoring_placeholders_ready"] is True
    assert gp052["provider_score_finalized"] is False
    assert gp052["provider_recommended"] is False
    assert gp052["provider_selected"] is False
    assert gp052["provider_configured"] is False
    assert gp052["provider_write_enabled"] is False
    assert gp052["provider_read_enabled"] is False
    assert gp052["provider_object_read_claimed"] is False
    assert gp052["provider_connection_tested"] is False
    assert gp052["object_body_view_enabled"] is False
    assert gp052["raw_file_body_storage_still_locked"] is True
    assert gp052["file_body_persisted_count"] == 0
    assert gp052["object_body_available_count"] == 0
    assert gp052["direct_upload_still_locked"] is True
    assert gp052["checksum_verification_not_claimed"] is True
    assert gp052["hash_verification_not_claimed"] is True
    assert gp052["official_receipt_count"] == 0
    assert gp052["finalized_receipt_count"] == 0
    assert gp052["closed_receipt_count"] == 0
    assert gp052["official_audit_log_written_count"] == 0
    assert gp052["immutable_audit_write_count"] == 0
    assert gp052["access_request_granted_count"] == 0
    assert gp052["decision_granted_count"] == 0
    assert gp052["action_approved_count"] == 0
    assert gp052["action_executed_count"] == 0
    assert gp052["external_delivery_still_locked"] is True
    assert gp052["packet_export_still_locked"] is True
    assert gp052["approval_disabled"] is True
    assert gp052["execution_engine_disabled"] is True
    assert gp052["clouds_status"] == "parked_do_not_continue_from_vault_gp052"
    assert gp052["next_pack"] == "VAULT_GP053_STORAGE_PROVIDER_RISK_MATRIX"


def test_gp052_criteria_truth_counts_and_locked_state():
    status = get_gp052_status()
    truth = status["criteria_truth"]

    assert truth["storage_provider_criteria_board_ready"] is True
    assert truth["criteria_cards_visible"] is True
    assert truth["criteria_rollups_visible"] is True
    assert truth["scoring_placeholders_visible"] is True
    assert truth["tower_review_gates_visible"] is True
    assert truth["selection_blockers_visible"] is True
    assert truth["metadata_only"] is True
    assert truth["private_criteria_board_only"] is True

    assert truth["provider_candidate_count"] == 5
    assert truth["criteria_card_count"] == 40
    assert truth["criteria_rollup_count"] == 8
    assert truth["scoring_placeholder_count"] == 40
    assert truth["tower_review_gate_count"] == 35
    assert truth["selection_blocker_count"] == 45
    assert truth["criteria_satisfied_count"] == 0
    assert truth["criteria_verified_count"] == 0
    assert truth["score_present_count"] == 0
    assert truth["score_finalized_count"] == 0
    assert truth["provider_recommended_count"] == 0
    assert truth["provider_selected_count"] == 0
    assert truth["provider_configured_count"] == 0
    assert truth["provider_read_enabled_count"] == 0
    assert truth["provider_write_enabled_count"] == 0
    assert truth["provider_object_read_claimed_count"] == 0
    assert truth["provider_connection_tested_count"] == 0
    assert truth["object_body_view_enabled"] is False
    assert truth["file_body_persisted_count"] == 0
    assert truth["object_body_available_count"] == 0
    assert truth["checksum_verified_count"] == 0
    assert truth["hash_verified_count"] == 0
    assert truth["official_storage_receipt_claimed_count"] == 0
    assert truth["finalized_storage_receipt_count"] == 0
    assert truth["closed_storage_receipt_count"] == 0
    assert truth["official_audit_log_written_count"] == 0
    assert truth["immutable_audit_write_count"] == 0
    assert truth["access_request_granted_count"] == 0
    assert truth["action_executed_count"] == 0
    assert truth["external_packet_delivery_enabled"] is False
    assert truth["packet_export_enabled"] is False
    assert truth["portal_access_enabled"] is False
    assert truth["execution_engine_enabled"] is False
    assert truth["vault_done"] is False
    assert truth["clouds_should_continue"] is False
    assert truth["safe_to_continue_to_gp053"] is True


def test_gp052_connected_to_gp051():
    home = get_storage_provider_criteria_board_home()
    gp051 = home["gp051_connection"]

    assert gp051["gp051_pack_id"] == "VAULT_GP051"
    assert gp051["gp051_ready"] is True
    assert gp051["gp051_section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp051["gp051_section_range"] == "GP051-GP060"
    assert gp051["gp051_safe_to_continue"] is True
    assert gp051["gp051_vault_done"] is False
    assert gp051["gp051_provider_candidate_count"] == 5
    assert gp051["gp051_selection_criteria_count"] == 40
    assert gp051["gp051_selection_lock_count"] == 45
    assert gp051["gp051_tower_provider_gate_count"] == 35
    assert gp051["gp051_prep_note_placeholder_count"] == 20
    assert gp051["gp051_provider_selected_count"] == 0


def test_gp052_criteria_cards_required_unsatisfied_unverified_unscored():
    cards = get_storage_provider_criteria_cards()["criteria_board"]

    assert cards["criteria_card_count"] == 40
    assert cards["provider_candidate_count"] == 5
    assert cards["criteria_type_count"] == 8
    assert cards["criteria_required_count"] == 40
    assert cards["criteria_satisfied_count"] == 0
    assert cards["criteria_verified_count"] == 0
    assert cards["score_present_count"] == 0
    assert cards["score_finalized_count"] == 0
    assert cards["provider_recommended_count"] == 0
    assert cards["provider_selected_count"] == 0
    assert cards["provider_configured_count"] == 0
    assert cards["provider_read_enabled_count"] == 0
    assert cards["provider_write_enabled_count"] == 0
    assert cards["tower_review_required_count"] == 40
    assert cards["tower_review_granted_count"] == 0
    assert cards["object_body_view_enabled_count"] == 0
    assert cards["file_body_persisted_count"] == 0
    assert cards["checksum_verified_count"] == 0
    assert cards["hash_verified_count"] == 0
    assert cards["official_audit_log_written_count"] == 0
    assert cards["action_executed_count"] == 0
    assert cards["export_allowed_count"] == 0
    assert cards["execution_allowed_count"] == 0
    assert cards["safe_to_continue_criteria_board"] is True

    for item in cards["criteria_card_items"]:
        assert item["criteria_card_id"].startswith("VSPCB-")
        assert item["selection_criteria_id"].startswith("VSPCR-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["criteria_card_status"] == "REQUIRED_NOT_SATISFIED_NOT_VERIFIED_NOT_SCORED"
        assert item["metadata_only"] is True
        assert item["private_criteria_board_only"] is True
        assert item["required"] is True
        assert item["satisfied"] is False
        assert item["verified"] is False
        assert item["score_present"] is False
        assert item["score_finalized"] is False
        assert item["provider_recommended"] is False
        assert item["provider_selected"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["execution_allowed"] is False


def test_gp052_criteria_rollups_by_criterion():
    rollups = get_storage_provider_criteria_rollups()["criteria_rollups"]

    assert rollups["criteria_rollup_count"] == 8
    assert rollups["criteria_card_count"] == 40
    assert rollups["provider_candidate_count"] == 5
    assert rollups["required_count"] == 40
    assert rollups["satisfied_count"] == 0
    assert rollups["verified_count"] == 0
    assert rollups["score_present_count"] == 0
    assert rollups["score_finalized_count"] == 0
    assert rollups["provider_recommended_count"] == 0
    assert rollups["provider_selected_count"] == 0
    assert rollups["provider_configured_count"] == 0
    assert rollups["provider_read_enabled_count"] == 0
    assert rollups["provider_write_enabled_count"] == 0
    assert rollups["object_body_view_enabled_count"] == 0
    assert rollups["export_allowed_count"] == 0
    assert rollups["execution_allowed_count"] == 0
    assert rollups["safe_to_continue_criteria_rollups"] is True

    criteria = {item["criterion"] for item in rollups["criteria_rollup_items"]}
    assert criteria == {
        "audit_trace_support_required",
        "encryption_support_required",
        "export_lock_compatibility_required",
        "metadata_first_support_required",
        "no_public_access_default_required",
        "object_body_locked_until_authorized",
        "private_vault_boundary_required",
        "tower_authority_required",
    }

    for item in rollups["criteria_rollup_items"]:
        assert item["criteria_rollup_id"].startswith("VSPCRU-")
        assert item["candidate_count"] == 5
        assert item["criteria_card_count"] == 5
        assert item["rollup_status"] == "REQUIRED_NOT_SATISFIED_NOT_VERIFIED_NOT_SCORED"
        assert item["required_count"] == 5
        assert item["satisfied_count"] == 0
        assert item["verified_count"] == 0
        assert item["score_present_count"] == 0
        assert item["score_finalized_count"] == 0
        assert item["provider_selected_count"] == 0
        assert item["execution_allowed_count"] == 0


def test_gp052_scoring_placeholders_empty_not_finalized():
    placeholders = get_storage_provider_scoring_placeholders()["scoring_placeholders"]

    assert placeholders["scoring_placeholder_count"] == 40
    assert placeholders["score_required_count"] == 40
    assert placeholders["score_present_count"] == 0
    assert placeholders["score_finalized_count"] == 0
    assert placeholders["provider_recommended_count"] == 0
    assert placeholders["provider_selected_count"] == 0
    assert placeholders["provider_configured_count"] == 0
    assert placeholders["tower_review_required_count"] == 40
    assert placeholders["tower_review_granted_count"] == 0
    assert placeholders["reviewer_bound_count"] == 0
    assert placeholders["reviewer_confirmed_count"] == 0
    assert placeholders["safe_to_continue_scoring_placeholders"] is True

    for item in placeholders["scoring_placeholder_items"]:
        assert item["scoring_placeholder_id"].startswith("VSPSP-")
        assert item["criteria_card_id"].startswith("VSPCB-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["scoring_status"] == "EMPTY_NOT_SCORED_NOT_FINALIZED"
        assert item["metadata_only"] is True
        assert item["score_required"] is True
        assert item["score_present"] is False
        assert item["score_value"] is None
        assert item["score_finalized"] is False
        assert item["provider_recommended"] is False
        assert item["provider_selected"] is False
        assert item["tower_review_required"] is True
        assert item["tower_review_granted"] is False
        assert item["reviewer_confirmed"] is False


def test_gp052_tower_review_gates_required_not_granted():
    gates = get_storage_provider_criteria_tower_review_gates()["tower_review_gates"]

    assert gates["tower_review_gate_count"] == 35
    assert gates["required_count"] == 35
    assert gates["granted_count"] == 0
    assert gates["vault_override_allowed_count"] == 0
    assert gates["provider_score_finalized_count"] == 0
    assert gates["provider_recommended_count"] == 0
    assert gates["provider_selected_count"] == 0
    assert gates["provider_configured_count"] == 0
    assert gates["provider_read_enabled_count"] == 0
    assert gates["provider_write_enabled_count"] == 0
    assert gates["object_body_view_enabled_count"] == 0
    assert gates["official_audit_log_written_count"] == 0
    assert gates["access_granted_count"] == 0
    assert gates["export_allowed_count"] == 0
    assert gates["execution_allowed_count"] == 0
    assert gates["safe_to_continue_tower_review_gates"] is True

    for item in gates["tower_review_gate_items"]:
        assert item["tower_review_gate_id"].startswith("VSPTRG-")
        assert item["tower_provider_gate_id"].startswith("VSPTG-")
        assert item["gate_status"] == "TOWER_CRITERIA_REVIEW_REQUIRED_NOT_GRANTED"
        assert item["metadata_only"] is True
        assert item["required"] is True
        assert item["granted"] is False
        assert item["vault_can_override"] is False
        assert item["provider_score_finalized"] is False
        assert item["provider_recommended"] is False
        assert item["provider_selected"] is False
        assert item["execution_allowed"] is False


def test_gp052_selection_blockers_active():
    blockers = get_storage_provider_criteria_selection_blockers()["selection_blockers"]

    assert blockers["selection_blocker_count"] == 45
    assert blockers["active_blocker_count"] == 45
    assert blockers["blocks_score_finalize_count"] == 45
    assert blockers["blocks_provider_recommendation_count"] == 45
    assert blockers["blocks_provider_selection_count"] == 45
    assert blockers["blocks_provider_configuration_count"] == 45
    assert blockers["blocks_provider_read_count"] == 45
    assert blockers["blocks_provider_write_count"] == 45
    assert blockers["blocks_object_body_view_count"] == 45
    assert blockers["blocks_raw_file_body_storage_count"] == 45
    assert blockers["blocks_direct_upload_count"] == 45
    assert blockers["blocks_checksum_hash_verification_claim_count"] == 45
    assert blockers["blocks_export_count"] == 45
    assert blockers["blocks_external_delivery_count"] == 45
    assert blockers["blocks_execution_count"] == 45
    assert blockers["blocks_vault_done_count"] == 45
    assert blockers["owner_resolvable_now_count"] == 0
    assert blockers["tower_authority_required_count"] == 45
    assert blockers["safe_to_continue_selection_blockers"] is True

    for item in blockers["selection_blocker_items"]:
        assert item["selection_blocker_id"].startswith("VSPCBL-")
        assert item["selection_lock_id"].startswith("VSPL-")
        assert item["blocker_status"] == "ACTIVE_CRITERIA_BOARD_BLOCKER"
        assert item["metadata_only"] is True
        assert item["active"] is True
        assert item["blocks_score_finalize"] is True
        assert item["blocks_provider_recommendation"] is True
        assert item["blocks_provider_selection"] is True
        assert item["blocks_provider_read"] is True
        assert item["blocks_execution"] is True
        assert item["blocks_vault_done"] is True
        assert item["owner_resolvable_now"] is False
        assert item["tower_authority_required"] is True


def test_gp052_next_step_carries_forward_to_gp053_not_clouds():
    next_step = get_storage_provider_criteria_next_step()["next_step"]

    assert next_step["next_step_count"] == 3
    assert next_step["ready_for_gp053_count"] == 3
    assert next_step["criteria_card_count"] == 40
    assert next_step["criteria_rollup_count"] == 8
    assert next_step["scoring_placeholder_count"] == 40
    assert next_step["tower_review_gate_count"] == 35
    assert next_step["selection_blocker_count"] == 45
    assert next_step["safe_to_continue_to_gp053"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False
    assert next_step["recommended_next_pack"] == "VAULT_GP053_STORAGE_PROVIDER_RISK_MATRIX"
    assert next_step["recommended_next_pack_title"] == "Storage Provider Risk Matrix"

    note = next_step["owner_notebook_note"].lower()
    assert "archive vault — storage provider prep layer" in note
    assert "gp051-gp060" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "provider criteria metadata-only" in rules
    assert "do not finalize provider scores" in rules
    assert "do not recommend a provider" in rules
    assert "do not select a provider" in rules
    assert "not vault done" in rules

    for item in next_step["next_step_items"]:
        assert item["next_step_id"].startswith("VSPCBNX-")
        assert item["target_pack"] == "VAULT_GP053_STORAGE_PROVIDER_RISK_MATRIX"
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False


def test_gp052_routes_counts_and_boundaries_declared():
    home = get_storage_provider_criteria_board_home()
    routes = home["criteria_routes"]
    counts = home["criteria_counts"]
    tower = home["tower_authority"]
    boundary = home["vault_boundary"]

    assert routes["section_header"] == "Archive Vault — Storage Provider Prep Layer"
    assert routes["section_range"] == "GP051-GP060"
    assert routes["route"] == "/vault/storage-provider-criteria-board"
    assert routes["json_route"] == "/vault/storage-provider-criteria-board.json"
    assert routes["criteria_cards_route"] == "/vault/storage-provider-criteria-cards.json"
    assert routes["criteria_rollups_route"] == "/vault/storage-provider-criteria-rollups.json"
    assert routes["scoring_placeholders_route"] == "/vault/storage-provider-scoring-placeholders.json"
    assert routes["tower_review_gates_route"] == "/vault/storage-provider-criteria-tower-review-gates.json"
    assert routes["selection_blockers_route"] == "/vault/storage-provider-criteria-selection-blockers.json"
    assert routes["next_step_route"] == "/vault/storage-provider-criteria-next-step.json"
    assert routes["gp052_status_route"] == "/vault/gp052-status.json"

    assert counts["provider_candidate_count"] == 5
    assert counts["criteria_card_count"] == 40
    assert counts["criteria_rollup_count"] == 8
    assert counts["scoring_placeholder_count"] == 40
    assert counts["tower_review_gate_count"] == 35
    assert counts["selection_blocker_count"] == 45
    assert counts["criteria_required_count"] == 40
    assert counts["criteria_satisfied_count"] == 0
    assert counts["criteria_verified_count"] == 0
    assert counts["score_present_count"] == 0
    assert counts["score_finalized_count"] == 0
    assert counts["provider_recommended_count"] == 0
    assert counts["provider_selected_count"] == 0
    assert counts["provider_configured_count"] == 0
    assert counts["provider_read_enabled_count"] == 0
    assert counts["provider_write_enabled_count"] == 0
    assert counts["object_body_view_enabled_count"] == 0
    assert counts["official_receipt_count"] == 0
    assert counts["official_audit_log_written_count"] == 0
    assert counts["action_executed_count"] == 0
    assert counts["packet_export_allowed_count"] == 0
    assert counts["execution_allowed_count"] == 0
    assert counts["vault_done_count"] == 0

    assert tower["tower_owns_provider_criteria_review"] is True
    assert tower["vault_can_finalize_provider_score"] is False
    assert tower["vault_can_recommend_provider"] is False
    assert tower["vault_can_select_provider_without_tower"] is False
    assert tower["vault_can_enable_provider_read"] is False
    assert tower["vault_can_mark_vault_done"] is False

    assert boundary["provider_selection_default"] == "criteria_board_only_no_provider_selected"
    assert boundary["provider_score_default"] == "placeholder_only_not_finalized"
    assert boundary["provider_recommendation_default"] == "blocked_no_recommendation"
    assert boundary["provider_read_allowed"] is False
    assert boundary["provider_write_allowed"] is False
    assert boundary["object_body_view_allowed"] is False
    assert boundary["public_packet_proof_allowed"] is False


def test_gp052_html_is_dark_and_mentions_criteria_board():
    html = render_storage_provider_criteria_board_page()
    lowered = html.lower()

    assert "Vault Storage Provider Criteria Board" in html
    assert "Archive Vault" in html
    assert "GP052" in html
    assert "Storage Provider Prep Layer" in html
    assert "/vault/storage-provider-criteria-board.json" in html
    assert "/vault/gp052-status.json" in html
    assert "Clouds parked" in html
    assert "No scores finalized" in html
    assert "No provider recommended" in html
    assert "No provider selected" in html

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


def test_gp052_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-provider-criteria-board",
        "/vault/storage-provider-criteria-board.json",
        "/vault/storage-provider-criteria-cards.json",
        "/vault/storage-provider-criteria-rollups.json",
        "/vault/storage-provider-scoring-placeholders.json",
        "/vault/storage-provider-criteria-tower-review-gates.json",
        "/vault/storage-provider-criteria-selection-blockers.json",
        "/vault/storage-provider-criteria-next-step.json",
        "/vault/gp052-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp052_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-provider-criteria-board",
        "/vault/storage-provider-criteria-board.json",
        "/vault/storage-provider-criteria-cards.json",
        "/vault/storage-provider-criteria-rollups.json",
        "/vault/storage-provider-scoring-placeholders.json",
        "/vault/storage-provider-criteria-tower-review-gates.json",
        "/vault/storage-provider-criteria-selection-blockers.json",
        "/vault/storage-provider-criteria-next-step.json",
        "/vault/gp052-status.json",
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
                assert b"Vault Storage Provider Criteria Board" in response.data
