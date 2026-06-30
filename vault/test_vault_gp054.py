"""
Tests for VAULT GIANT PACK 054 — Storage Provider Comparison Board
"""

from pathlib import Path

import pytest

from vault.storage_provider_comparison_board_service import (
    get_gp054_status,
    get_storage_provider_comparison_board_home,
    get_storage_provider_comparison_next_step,
    get_storage_provider_comparison_rows,
    get_storage_provider_comparison_tower_review_gates,
    get_storage_provider_criteria_comparison_rollups,
    get_storage_provider_ranking_placeholders,
    get_storage_provider_recommendation_blockers,
    get_storage_provider_risk_comparison_rollups,
    render_storage_provider_comparison_board_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp054_status_ready_safe_continue_not_done():
    status = get_gp054_status()
    gp054 = status["gp054_status"]

    assert status["pack"]["id"] == "VAULT_GP054"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert status["pack"]["section_range"] == "GP051-GP060"

    assert gp054["ready"] is True
    assert gp054["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp054["section_title"] == "Archive Vault — Storage Provider Prep Layer"
    assert gp054["section_range"] == "GP051-GP060"
    assert gp054["storage_provider_comparison_board_ready"] is True
    assert gp054["safe_to_continue_to_gp055"] is True
    assert gp054["vault_done"] is False
    assert gp054["foundation_status"] == "safe_to_continue_not_done"
    assert gp054["metadata_only_comparison_board"] is True
    assert gp054["private_comparison_board_only"] is True
    assert gp054["comparison_rows_ready"] is True
    assert gp054["criteria_comparison_rollups_ready"] is True
    assert gp054["risk_comparison_rollups_ready"] is True
    assert gp054["ranking_placeholders_ready"] is True
    assert gp054["provider_ranking_finalized"] is False
    assert gp054["provider_score_finalized"] is False
    assert gp054["provider_recommended"] is False
    assert gp054["provider_selected"] is False
    assert gp054["provider_configured"] is False
    assert gp054["provider_write_enabled"] is False
    assert gp054["provider_read_enabled"] is False
    assert gp054["provider_object_read_claimed"] is False
    assert gp054["provider_connection_tested"] is False
    assert gp054["risk_accepted"] is False
    assert gp054["risk_waived"] is False
    assert gp054["mitigation_approved"] is False
    assert gp054["object_body_view_enabled"] is False
    assert gp054["raw_file_body_storage_still_locked"] is True
    assert gp054["file_body_persisted_count"] == 0
    assert gp054["object_body_available_count"] == 0
    assert gp054["direct_upload_still_locked"] is True
    assert gp054["checksum_verification_not_claimed"] is True
    assert gp054["hash_verification_not_claimed"] is True
    assert gp054["official_receipt_count"] == 0
    assert gp054["finalized_receipt_count"] == 0
    assert gp054["closed_receipt_count"] == 0
    assert gp054["official_audit_log_written_count"] == 0
    assert gp054["immutable_audit_write_count"] == 0
    assert gp054["access_request_granted_count"] == 0
    assert gp054["decision_granted_count"] == 0
    assert gp054["action_approved_count"] == 0
    assert gp054["action_executed_count"] == 0
    assert gp054["external_delivery_still_locked"] is True
    assert gp054["packet_export_still_locked"] is True
    assert gp054["approval_disabled"] is True
    assert gp054["execution_engine_disabled"] is True
    assert gp054["clouds_status"] == "parked_do_not_continue_from_vault_gp054"
    assert gp054["next_pack"] == "VAULT_GP055_STORAGE_PROVIDER_DECISION_DRAFT"


def test_gp054_comparison_truth_counts_and_locked_state():
    status = get_gp054_status()
    truth = status["comparison_truth"]

    assert truth["storage_provider_comparison_board_ready"] is True
    assert truth["comparison_rows_visible"] is True
    assert truth["criteria_comparison_rollups_visible"] is True
    assert truth["risk_comparison_rollups_visible"] is True
    assert truth["ranking_placeholders_visible"] is True
    assert truth["tower_comparison_review_gates_visible"] is True
    assert truth["recommendation_blockers_visible"] is True
    assert truth["metadata_only"] is True
    assert truth["private_comparison_board_only"] is True

    assert truth["provider_candidate_count"] == 5
    assert truth["comparison_row_count"] == 5
    assert truth["comparison_factor_count"] == 6
    assert truth["criteria_comparison_rollup_count"] == 8
    assert truth["risk_comparison_rollup_count"] == 8
    assert truth["ranking_placeholder_count"] == 5
    assert truth["tower_comparison_review_gate_count"] == 35
    assert truth["recommendation_blocker_count"] == 45

    assert truth["comparison_score_present_count"] == 0
    assert truth["comparison_score_finalized_count"] == 0
    assert truth["rank_present_count"] == 0
    assert truth["rank_finalized_count"] == 0
    assert truth["provider_recommended_count"] == 0
    assert truth["provider_selected_count"] == 0
    assert truth["provider_configured_count"] == 0
    assert truth["provider_read_enabled_count"] == 0
    assert truth["provider_write_enabled_count"] == 0
    assert truth["provider_object_read_claimed_count"] == 0
    assert truth["provider_connection_tested_count"] == 0
    assert truth["risk_accepted_count"] == 0
    assert truth["risk_waived_count"] == 0
    assert truth["mitigation_approved_count"] == 0
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
    assert truth["safe_to_continue_to_gp055"] is True


def test_gp054_connected_to_gp053():
    home = get_storage_provider_comparison_board_home()
    gp053 = home["gp053_connection"]

    assert gp053["gp053_pack_id"] == "VAULT_GP053"
    assert gp053["gp053_ready"] is True
    assert gp053["gp053_section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp053["gp053_section_range"] == "GP051-GP060"
    assert gp053["gp053_safe_to_continue"] is True
    assert gp053["gp053_vault_done"] is False
    assert gp053["gp053_provider_candidate_count"] == 5
    assert gp053["gp053_risk_card_count"] == 40
    assert gp053["gp053_risk_rollup_count"] == 8
    assert gp053["gp053_severity_placeholder_count"] == 40
    assert gp053["gp053_mitigation_placeholder_count"] == 160
    assert gp053["gp053_risk_selection_blocker_count"] == 45
    assert gp053["gp053_provider_selected_count"] == 0
    assert gp053["gp053_provider_recommended_count"] == 0


def test_gp054_comparison_rows_visible_unranked_unrecommended():
    rows = get_storage_provider_comparison_rows()["comparison_rows"]

    assert rows["comparison_row_count"] == 5
    assert rows["provider_candidate_count"] == 5
    assert rows["comparison_factor_count"] == 6
    assert rows["comparison_visible_count"] == 5
    assert rows["criteria_card_count"] == 40
    assert rows["risk_card_count"] == 40
    assert rows["comparison_score_present_count"] == 0
    assert rows["comparison_score_finalized_count"] == 0
    assert rows["rank_present_count"] == 0
    assert rows["rank_finalized_count"] == 0
    assert rows["provider_recommended_count"] == 0
    assert rows["provider_selected_count"] == 0
    assert rows["provider_configured_count"] == 0
    assert rows["provider_read_enabled_count"] == 0
    assert rows["provider_write_enabled_count"] == 0
    assert rows["provider_object_read_claimed_count"] == 0
    assert rows["provider_connection_tested_count"] == 0
    assert rows["risk_accepted_count"] == 0
    assert rows["risk_waived_count"] == 0
    assert rows["mitigation_approved_count"] == 0
    assert rows["tower_comparison_review_required_count"] == 5
    assert rows["tower_comparison_review_granted_count"] == 0
    assert rows["object_body_view_enabled_count"] == 0
    assert rows["file_body_persisted_count"] == 0
    assert rows["checksum_verified_count"] == 0
    assert rows["hash_verified_count"] == 0
    assert rows["official_audit_log_written_count"] == 0
    assert rows["action_executed_count"] == 0
    assert rows["export_allowed_count"] == 0
    assert rows["execution_allowed_count"] == 0
    assert rows["safe_to_continue_comparison_rows"] is True

    for item in rows["comparison_row_items"]:
        assert item["comparison_row_id"].startswith("VSPCMP-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["comparison_status"] == "COMPARISON_PLACEHOLDER_ONLY_NOT_RANKED_NOT_RECOMMENDED"
        assert item["metadata_only"] is True
        assert item["private_comparison_board_only"] is True
        assert item["comparison_visible"] is True
        assert item["criteria_card_count"] == 8
        assert item["risk_card_count"] == 8
        assert item["comparison_factor_count"] == 6
        assert item["comparison_score_present"] is False
        assert item["comparison_score_value"] is None
        assert item["rank_present"] is False
        assert item["rank_value"] is None
        assert item["rank_finalized"] is False
        assert item["provider_recommended"] is False
        assert item["provider_selected"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["execution_allowed"] is False


def test_gp054_criteria_comparison_rollups_unverified_unranked():
    rollups = get_storage_provider_criteria_comparison_rollups()["criteria_rollups"]

    assert rollups["criteria_comparison_rollup_count"] == 8
    assert rollups["provider_candidate_count"] == 5
    assert rollups["criteria_present_count"] == 8
    assert rollups["criteria_satisfied_count"] == 0
    assert rollups["criteria_verified_count"] == 0
    assert rollups["comparison_score_present_count"] == 0
    assert rollups["comparison_score_finalized_count"] == 0
    assert rollups["rank_present_count"] == 0
    assert rollups["rank_finalized_count"] == 0
    assert rollups["provider_recommended_count"] == 0
    assert rollups["provider_selected_count"] == 0
    assert rollups["safe_to_continue_criteria_comparison_rollups"] is True

    criteria = {item["criterion"] for item in rollups["criteria_comparison_rollup_items"]}
    assert "tower_authority_required" in criteria
    assert "encryption_support_required" in criteria
    assert "audit_trace_support_required" in criteria
    assert "object_body_locked_until_authorized" in criteria

    for item in rollups["criteria_comparison_rollup_items"]:
        assert item["criteria_comparison_rollup_id"].startswith("VSPCCR-")
        assert item["candidate_count"] == 5
        assert item["criteria_status"] == "REQUIRED_NOT_SATISFIED_NOT_VERIFIED_NOT_RANKED"
        assert item["metadata_only"] is True
        assert item["criteria_present"] is True
        assert item["criteria_satisfied_count"] == 0
        assert item["criteria_verified_count"] == 0
        assert item["rank_finalized_count"] == 0
        assert item["provider_selected_count"] == 0


def test_gp054_risk_comparison_rollups_unaccepted_unwaived():
    rollups = get_storage_provider_risk_comparison_rollups()["risk_rollups"]

    assert rollups["risk_comparison_rollup_count"] == 8
    assert rollups["provider_candidate_count"] == 5
    assert rollups["risk_present_count"] == 8
    assert rollups["severity_present_count"] == 0
    assert rollups["severity_finalized_count"] == 0
    assert rollups["risk_score_present_count"] == 0
    assert rollups["risk_score_finalized_count"] == 0
    assert rollups["risk_accepted_count"] == 0
    assert rollups["risk_waived_count"] == 0
    assert rollups["mitigation_approved_count"] == 0
    assert rollups["comparison_score_present_count"] == 0
    assert rollups["comparison_score_finalized_count"] == 0
    assert rollups["rank_present_count"] == 0
    assert rollups["rank_finalized_count"] == 0
    assert rollups["provider_recommended_count"] == 0
    assert rollups["provider_selected_count"] == 0
    assert rollups["safe_to_continue_risk_comparison_rollups"] is True

    categories = {item["risk_category"] for item in rollups["risk_comparison_rollup_items"]}
    assert "tower_authority_risk" in categories
    assert "privacy_boundary_risk" in categories
    assert "encryption_risk" in categories
    assert "export_control_risk" in categories

    for item in rollups["risk_comparison_rollup_items"]:
        assert item["risk_comparison_rollup_id"].startswith("VSPRCR-")
        assert item["candidate_count"] == 5
        assert item["risk_status"] == "RISK_PLACEHOLDER_NOT_ACCEPTED_NOT_WAIVED_NOT_RANKED"
        assert item["metadata_only"] is True
        assert item["risk_present"] is True
        assert item["risk_accepted_count"] == 0
        assert item["risk_waived_count"] == 0
        assert item["rank_finalized_count"] == 0
        assert item["provider_selected_count"] == 0


def test_gp054_ranking_placeholders_empty_not_finalized():
    placeholders = get_storage_provider_ranking_placeholders()["ranking_placeholders"]

    assert placeholders["ranking_placeholder_count"] == 5
    assert placeholders["rank_required_count"] == 5
    assert placeholders["rank_present_count"] == 0
    assert placeholders["rank_finalized_count"] == 0
    assert placeholders["comparison_score_present_count"] == 0
    assert placeholders["comparison_score_finalized_count"] == 0
    assert placeholders["provider_recommended_count"] == 0
    assert placeholders["provider_selected_count"] == 0
    assert placeholders["provider_configured_count"] == 0
    assert placeholders["tower_comparison_review_required_count"] == 5
    assert placeholders["tower_comparison_review_granted_count"] == 0
    assert placeholders["reviewer_bound_count"] == 0
    assert placeholders["reviewer_confirmed_count"] == 0
    assert placeholders["safe_to_continue_ranking_placeholders"] is True

    for item in placeholders["ranking_placeholder_items"]:
        assert item["ranking_placeholder_id"].startswith("VSPRANK-")
        assert item["comparison_row_id"].startswith("VSPCMP-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["ranking_status"] == "EMPTY_NOT_RANKED_NOT_FINALIZED"
        assert item["metadata_only"] is True
        assert item["rank_required"] is True
        assert item["rank_present"] is False
        assert item["rank_value"] is None
        assert item["rank_finalized"] is False
        assert item["comparison_score_present"] is False
        assert item["comparison_score_finalized"] is False
        assert item["provider_recommended"] is False
        assert item["provider_selected"] is False
        assert item["tower_comparison_review_required"] is True
        assert item["tower_comparison_review_granted"] is False


def test_gp054_tower_comparison_review_gates_required_not_granted():
    gates = get_storage_provider_comparison_tower_review_gates()["tower_review_gates"]

    assert gates["tower_comparison_review_gate_count"] == 35
    assert gates["required_count"] == 35
    assert gates["granted_count"] == 0
    assert gates["vault_override_allowed_count"] == 0
    assert gates["rank_finalized_count"] == 0
    assert gates["comparison_score_finalized_count"] == 0
    assert gates["provider_recommended_count"] == 0
    assert gates["provider_selected_count"] == 0
    assert gates["provider_configured_count"] == 0
    assert gates["provider_read_enabled_count"] == 0
    assert gates["provider_write_enabled_count"] == 0
    assert gates["risk_accepted_count"] == 0
    assert gates["risk_waived_count"] == 0
    assert gates["mitigation_approved_count"] == 0
    assert gates["object_body_view_enabled_count"] == 0
    assert gates["official_audit_log_written_count"] == 0
    assert gates["access_granted_count"] == 0
    assert gates["export_allowed_count"] == 0
    assert gates["execution_allowed_count"] == 0
    assert gates["safe_to_continue_tower_comparison_review_gates"] is True

    for item in gates["tower_comparison_review_gate_items"]:
        assert item["tower_comparison_review_gate_id"].startswith("VSPTCG-")
        assert item["tower_risk_review_gate_id"].startswith("VSPTRR-")
        assert item["gate_status"] == "TOWER_COMPARISON_REVIEW_REQUIRED_NOT_GRANTED"
        assert item["metadata_only"] is True
        assert item["required"] is True
        assert item["granted"] is False
        assert item["vault_can_override"] is False
        assert item["rank_finalized"] is False
        assert item["provider_recommended"] is False
        assert item["provider_selected"] is False
        assert item["execution_allowed"] is False


def test_gp054_recommendation_blockers_active():
    blockers = get_storage_provider_recommendation_blockers()["recommendation_blockers"]

    assert blockers["recommendation_blocker_count"] == 45
    assert blockers["active_blocker_count"] == 45
    assert blockers["blocks_rank_finalize_count"] == 45
    assert blockers["blocks_comparison_score_finalize_count"] == 45
    assert blockers["blocks_provider_recommendation_count"] == 45
    assert blockers["blocks_provider_selection_count"] == 45
    assert blockers["blocks_provider_configuration_count"] == 45
    assert blockers["blocks_provider_read_count"] == 45
    assert blockers["blocks_provider_write_count"] == 45
    assert blockers["blocks_risk_acceptance_count"] == 45
    assert blockers["blocks_risk_waiver_count"] == 45
    assert blockers["blocks_mitigation_approval_count"] == 45
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
    assert blockers["safe_to_continue_recommendation_blockers"] is True

    for item in blockers["recommendation_blocker_items"]:
        assert item["recommendation_blocker_id"].startswith("VSPREC-")
        assert item["risk_selection_blocker_id"].startswith("VSPRSB-")
        assert item["blocker_status"] == "ACTIVE_COMPARISON_RECOMMENDATION_BLOCKER"
        assert item["metadata_only"] is True
        assert item["active"] is True
        assert item["blocks_rank_finalize"] is True
        assert item["blocks_provider_recommendation"] is True
        assert item["blocks_provider_selection"] is True
        assert item["blocks_provider_read"] is True
        assert item["blocks_risk_acceptance"] is True
        assert item["blocks_mitigation_approval"] is True
        assert item["blocks_execution"] is True
        assert item["blocks_vault_done"] is True
        assert item["owner_resolvable_now"] is False
        assert item["tower_authority_required"] is True


def test_gp054_next_step_carries_forward_to_gp055_not_clouds():
    next_step = get_storage_provider_comparison_next_step()["next_step"]

    assert next_step["next_step_count"] == 3
    assert next_step["ready_for_gp055_count"] == 3
    assert next_step["comparison_row_count"] == 5
    assert next_step["criteria_comparison_rollup_count"] == 8
    assert next_step["risk_comparison_rollup_count"] == 8
    assert next_step["ranking_placeholder_count"] == 5
    assert next_step["tower_comparison_review_gate_count"] == 35
    assert next_step["recommendation_blocker_count"] == 45
    assert next_step["safe_to_continue_to_gp055"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False
    assert next_step["recommended_next_pack"] == "VAULT_GP055_STORAGE_PROVIDER_DECISION_DRAFT"
    assert next_step["recommended_next_pack_title"] == "Storage Provider Decision Draft"

    note = next_step["owner_notebook_note"].lower()
    assert "archive vault — storage provider prep layer" in note
    assert "gp051-gp060" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "provider comparison board metadata-only" in rules
    assert "do not finalize provider rankings" in rules
    assert "do not recommend a provider" in rules
    assert "do not select a provider" in rules
    assert "not vault done" in rules

    for item in next_step["next_step_items"]:
        assert item["next_step_id"].startswith("VSPCBNX-")
        assert item["target_pack"] == "VAULT_GP055_STORAGE_PROVIDER_DECISION_DRAFT"
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False


def test_gp054_routes_counts_and_boundaries_declared():
    home = get_storage_provider_comparison_board_home()
    routes = home["comparison_routes"]
    counts = home["comparison_counts"]
    tower = home["tower_authority"]
    boundary = home["vault_boundary"]

    assert routes["section_header"] == "Archive Vault — Storage Provider Prep Layer"
    assert routes["section_range"] == "GP051-GP060"
    assert routes["route"] == "/vault/storage-provider-comparison-board"
    assert routes["json_route"] == "/vault/storage-provider-comparison-board.json"
    assert routes["comparison_rows_route"] == "/vault/storage-provider-comparison-rows.json"
    assert routes["criteria_comparison_rollups_route"] == "/vault/storage-provider-criteria-comparison-rollups.json"
    assert routes["risk_comparison_rollups_route"] == "/vault/storage-provider-risk-comparison-rollups.json"
    assert routes["ranking_placeholders_route"] == "/vault/storage-provider-ranking-placeholders.json"
    assert routes["tower_review_gates_route"] == "/vault/storage-provider-comparison-tower-review-gates.json"
    assert routes["recommendation_blockers_route"] == "/vault/storage-provider-recommendation-blockers.json"
    assert routes["next_step_route"] == "/vault/storage-provider-comparison-next-step.json"
    assert routes["gp054_status_route"] == "/vault/gp054-status.json"

    assert counts["provider_candidate_count"] == 5
    assert counts["comparison_row_count"] == 5
    assert counts["comparison_factor_count"] == 6
    assert counts["criteria_comparison_rollup_count"] == 8
    assert counts["risk_comparison_rollup_count"] == 8
    assert counts["ranking_placeholder_count"] == 5
    assert counts["tower_comparison_review_gate_count"] == 35
    assert counts["recommendation_blocker_count"] == 45
    assert counts["comparison_score_present_count"] == 0
    assert counts["comparison_score_finalized_count"] == 0
    assert counts["rank_present_count"] == 0
    assert counts["rank_finalized_count"] == 0
    assert counts["provider_recommended_count"] == 0
    assert counts["provider_selected_count"] == 0
    assert counts["provider_configured_count"] == 0
    assert counts["provider_read_enabled_count"] == 0
    assert counts["provider_write_enabled_count"] == 0
    assert counts["risk_accepted_count"] == 0
    assert counts["risk_waived_count"] == 0
    assert counts["mitigation_approved_count"] == 0
    assert counts["object_body_view_enabled_count"] == 0
    assert counts["official_receipt_count"] == 0
    assert counts["official_audit_log_written_count"] == 0
    assert counts["action_executed_count"] == 0
    assert counts["packet_export_allowed_count"] == 0
    assert counts["execution_allowed_count"] == 0
    assert counts["vault_done_count"] == 0

    assert tower["tower_owns_provider_comparison_review"] is True
    assert tower["tower_owns_provider_recommendation_authority"] is True
    assert tower["vault_can_finalize_provider_ranking"] is False
    assert tower["vault_can_recommend_provider"] is False
    assert tower["vault_can_select_provider_without_tower"] is False
    assert tower["vault_can_mark_vault_done"] is False

    assert boundary["provider_selection_default"] == "comparison_board_only_no_provider_selected"
    assert boundary["provider_ranking_default"] == "placeholder_only_not_finalized"
    assert boundary["provider_recommendation_default"] == "blocked_no_recommendation"
    assert boundary["provider_read_allowed"] is False
    assert boundary["provider_write_allowed"] is False
    assert boundary["object_body_view_allowed"] is False
    assert boundary["public_packet_proof_allowed"] is False


def test_gp054_html_is_dark_and_mentions_comparison_board():
    html = render_storage_provider_comparison_board_page()
    lowered = html.lower()

    assert "Vault Storage Provider Comparison Board" in html
    assert "Storage Provider Prep Layer" in html
    assert "Archive Vault" in html
    assert "GP054" in html
    assert "/vault/storage-provider-comparison-board.json" in html
    assert "/vault/gp054-status.json" in html
    assert "Clouds parked" in html
    assert "No ranking finalized" in html
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


def test_gp054_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-provider-comparison-board",
        "/vault/storage-provider-comparison-board.json",
        "/vault/storage-provider-comparison-rows.json",
        "/vault/storage-provider-criteria-comparison-rollups.json",
        "/vault/storage-provider-risk-comparison-rollups.json",
        "/vault/storage-provider-ranking-placeholders.json",
        "/vault/storage-provider-comparison-tower-review-gates.json",
        "/vault/storage-provider-recommendation-blockers.json",
        "/vault/storage-provider-comparison-next-step.json",
        "/vault/gp054-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp054_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-provider-comparison-board",
        "/vault/storage-provider-comparison-board.json",
        "/vault/storage-provider-comparison-rows.json",
        "/vault/storage-provider-criteria-comparison-rollups.json",
        "/vault/storage-provider-risk-comparison-rollups.json",
        "/vault/storage-provider-ranking-placeholders.json",
        "/vault/storage-provider-comparison-tower-review-gates.json",
        "/vault/storage-provider-recommendation-blockers.json",
        "/vault/storage-provider-comparison-next-step.json",
        "/vault/gp054-status.json",
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
                assert b"Vault Storage Provider Comparison Board" in response.data
