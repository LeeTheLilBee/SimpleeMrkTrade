"""
Tests for VAULT GIANT PACK 053 — Storage Provider Risk Matrix
"""

from pathlib import Path

import pytest

from vault.storage_provider_risk_matrix_service import (
    get_gp053_status,
    get_storage_provider_risk_cards,
    get_storage_provider_risk_matrix_home,
    get_storage_provider_risk_mitigation_placeholders,
    get_storage_provider_risk_next_step,
    get_storage_provider_risk_rollups,
    get_storage_provider_risk_selection_blockers,
    get_storage_provider_risk_severity_placeholders,
    get_storage_provider_risk_tower_review_gates,
    render_storage_provider_risk_matrix_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp053_status_ready_safe_continue_not_done():
    status = get_gp053_status()
    gp053 = status["gp053_status"]

    assert status["pack"]["id"] == "VAULT_GP053"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert status["pack"]["section_range"] == "GP051-GP060"

    assert gp053["ready"] is True
    assert gp053["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp053["section_title"] == "Archive Vault — Storage Provider Prep Layer"
    assert gp053["section_range"] == "GP051-GP060"
    assert gp053["storage_provider_risk_matrix_ready"] is True
    assert gp053["safe_to_continue_to_gp054"] is True
    assert gp053["vault_done"] is False
    assert gp053["foundation_status"] == "safe_to_continue_not_done"
    assert gp053["metadata_only_risk_matrix"] is True
    assert gp053["private_risk_matrix_only"] is True
    assert gp053["risk_cards_ready"] is True
    assert gp053["risk_rollups_ready"] is True
    assert gp053["severity_placeholders_ready"] is True
    assert gp053["mitigation_placeholders_ready"] is True
    assert gp053["risk_accepted"] is False
    assert gp053["risk_waived"] is False
    assert gp053["mitigation_approved"] is False
    assert gp053["provider_score_finalized"] is False
    assert gp053["provider_recommended"] is False
    assert gp053["provider_selected"] is False
    assert gp053["provider_configured"] is False
    assert gp053["provider_write_enabled"] is False
    assert gp053["provider_read_enabled"] is False
    assert gp053["provider_object_read_claimed"] is False
    assert gp053["provider_connection_tested"] is False
    assert gp053["object_body_view_enabled"] is False
    assert gp053["raw_file_body_storage_still_locked"] is True
    assert gp053["file_body_persisted_count"] == 0
    assert gp053["object_body_available_count"] == 0
    assert gp053["direct_upload_still_locked"] is True
    assert gp053["checksum_verification_not_claimed"] is True
    assert gp053["hash_verification_not_claimed"] is True
    assert gp053["official_receipt_count"] == 0
    assert gp053["finalized_receipt_count"] == 0
    assert gp053["closed_receipt_count"] == 0
    assert gp053["official_audit_log_written_count"] == 0
    assert gp053["immutable_audit_write_count"] == 0
    assert gp053["access_request_granted_count"] == 0
    assert gp053["decision_granted_count"] == 0
    assert gp053["action_approved_count"] == 0
    assert gp053["action_executed_count"] == 0
    assert gp053["external_delivery_still_locked"] is True
    assert gp053["packet_export_still_locked"] is True
    assert gp053["approval_disabled"] is True
    assert gp053["execution_engine_disabled"] is True
    assert gp053["clouds_status"] == "parked_do_not_continue_from_vault_gp053"
    assert gp053["next_pack"] == "VAULT_GP054_STORAGE_PROVIDER_COMPARISON_BOARD"


def test_gp053_risk_truth_counts_and_locked_state():
    status = get_gp053_status()
    truth = status["risk_truth"]

    assert truth["storage_provider_risk_matrix_ready"] is True
    assert truth["risk_cards_visible"] is True
    assert truth["risk_rollups_visible"] is True
    assert truth["severity_placeholders_visible"] is True
    assert truth["mitigation_placeholders_visible"] is True
    assert truth["tower_risk_review_gates_visible"] is True
    assert truth["risk_selection_blockers_visible"] is True
    assert truth["metadata_only"] is True
    assert truth["private_risk_matrix_only"] is True

    assert truth["provider_candidate_count"] == 5
    assert truth["risk_category_count"] == 8
    assert truth["risk_card_count"] == 40
    assert truth["risk_rollup_count"] == 8
    assert truth["severity_placeholder_count"] == 40
    assert truth["mitigation_placeholder_count"] == 160
    assert truth["tower_risk_review_gate_count"] == 35
    assert truth["risk_selection_blocker_count"] == 45

    assert truth["severity_present_count"] == 0
    assert truth["severity_finalized_count"] == 0
    assert truth["risk_score_present_count"] == 0
    assert truth["risk_score_finalized_count"] == 0
    assert truth["risk_accepted_count"] == 0
    assert truth["risk_waived_count"] == 0
    assert truth["mitigation_present_count"] == 0
    assert truth["mitigation_approved_count"] == 0
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
    assert truth["safe_to_continue_to_gp054"] is True


def test_gp053_connected_to_gp052():
    home = get_storage_provider_risk_matrix_home()
    gp052 = home["gp052_connection"]

    assert gp052["gp052_pack_id"] == "VAULT_GP052"
    assert gp052["gp052_ready"] is True
    assert gp052["gp052_section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp052["gp052_section_range"] == "GP051-GP060"
    assert gp052["gp052_safe_to_continue"] is True
    assert gp052["gp052_vault_done"] is False
    assert gp052["gp052_provider_candidate_count"] == 5
    assert gp052["gp052_criteria_card_count"] == 40
    assert gp052["gp052_scoring_placeholder_count"] == 40
    assert gp052["gp052_selection_blocker_count"] == 45
    assert gp052["gp052_provider_selected_count"] == 0
    assert gp052["gp052_provider_recommended_count"] == 0


def test_gp053_risk_cards_required_unscored_unaccepted_unwaived():
    cards = get_storage_provider_risk_cards()["risk_cards"]

    assert cards["risk_card_count"] == 40
    assert cards["provider_candidate_count"] == 5
    assert cards["risk_category_count"] == 8
    assert cards["risk_visible_count"] == 40
    assert cards["risk_required_count"] == 40
    assert cards["severity_present_count"] == 0
    assert cards["severity_finalized_count"] == 0
    assert cards["risk_score_present_count"] == 0
    assert cards["risk_score_finalized_count"] == 0
    assert cards["risk_accepted_count"] == 0
    assert cards["risk_waived_count"] == 0
    assert cards["mitigation_required_count"] == 40
    assert cards["mitigation_present_count"] == 0
    assert cards["mitigation_approved_count"] == 0
    assert cards["tower_risk_review_required_count"] == 40
    assert cards["tower_risk_review_granted_count"] == 0
    assert cards["provider_recommended_count"] == 0
    assert cards["provider_selected_count"] == 0
    assert cards["provider_configured_count"] == 0
    assert cards["provider_read_enabled_count"] == 0
    assert cards["provider_write_enabled_count"] == 0
    assert cards["object_body_view_enabled_count"] == 0
    assert cards["file_body_persisted_count"] == 0
    assert cards["checksum_verified_count"] == 0
    assert cards["hash_verified_count"] == 0
    assert cards["official_audit_log_written_count"] == 0
    assert cards["action_executed_count"] == 0
    assert cards["export_allowed_count"] == 0
    assert cards["execution_allowed_count"] == 0
    assert cards["safe_to_continue_risk_cards"] is True

    categories = {item["risk_category"] for item in cards["risk_card_items"]}
    assert categories == {
        "tower_authority_risk",
        "privacy_boundary_risk",
        "encryption_risk",
        "audit_trace_risk",
        "object_visibility_risk",
        "export_control_risk",
        "integration_risk",
        "continuity_risk",
    }

    for item in cards["risk_card_items"]:
        assert item["risk_card_id"].startswith("VSPRM-")
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["risk_card_status"] == "RISK_PLACEHOLDER_ONLY_NOT_SCORED_NOT_ACCEPTED_NOT_WAIVED"
        assert item["metadata_only"] is True
        assert item["private_risk_matrix_only"] is True
        assert item["risk_visible"] is True
        assert item["risk_required"] is True
        assert item["severity_present"] is False
        assert item["severity_level"] is None
        assert item["risk_score_present"] is False
        assert item["risk_score_value"] is None
        assert item["risk_accepted"] is False
        assert item["risk_waived"] is False
        assert item["mitigation_required"] is True
        assert item["mitigation_present"] is False
        assert item["mitigation_approved"] is False
        assert item["provider_selected"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["execution_allowed"] is False


def test_gp053_risk_rollups_by_category():
    rollups = get_storage_provider_risk_rollups()["risk_rollups"]

    assert rollups["risk_rollup_count"] == 8
    assert rollups["risk_card_count"] == 40
    assert rollups["provider_candidate_count"] == 5
    assert rollups["risk_required_count"] == 40
    assert rollups["severity_present_count"] == 0
    assert rollups["severity_finalized_count"] == 0
    assert rollups["risk_score_present_count"] == 0
    assert rollups["risk_score_finalized_count"] == 0
    assert rollups["risk_accepted_count"] == 0
    assert rollups["risk_waived_count"] == 0
    assert rollups["mitigation_present_count"] == 0
    assert rollups["mitigation_approved_count"] == 0
    assert rollups["provider_recommended_count"] == 0
    assert rollups["provider_selected_count"] == 0
    assert rollups["provider_configured_count"] == 0
    assert rollups["provider_read_enabled_count"] == 0
    assert rollups["provider_write_enabled_count"] == 0
    assert rollups["object_body_view_enabled_count"] == 0
    assert rollups["export_allowed_count"] == 0
    assert rollups["execution_allowed_count"] == 0
    assert rollups["safe_to_continue_risk_rollups"] is True

    for item in rollups["risk_rollup_items"]:
        assert item["risk_rollup_id"].startswith("VSPRR-")
        assert item["candidate_count"] == 5
        assert item["risk_card_count"] == 5
        assert item["rollup_status"] == "RISK_PLACEHOLDER_ONLY_NOT_SCORED_NOT_ACCEPTED_NOT_WAIVED"
        assert item["risk_required_count"] == 5
        assert item["severity_present_count"] == 0
        assert item["risk_accepted_count"] == 0
        assert item["risk_waived_count"] == 0
        assert item["mitigation_approved_count"] == 0
        assert item["provider_selected_count"] == 0
        assert item["execution_allowed_count"] == 0


def test_gp053_severity_placeholders_empty_not_finalized():
    placeholders = get_storage_provider_risk_severity_placeholders()["severity_placeholders"]

    assert placeholders["severity_placeholder_count"] == 40
    assert placeholders["severity_required_count"] == 40
    assert placeholders["severity_present_count"] == 0
    assert placeholders["severity_finalized_count"] == 0
    assert placeholders["risk_score_present_count"] == 0
    assert placeholders["risk_score_finalized_count"] == 0
    assert placeholders["risk_accepted_count"] == 0
    assert placeholders["risk_waived_count"] == 0
    assert placeholders["provider_recommended_count"] == 0
    assert placeholders["provider_selected_count"] == 0
    assert placeholders["tower_risk_review_required_count"] == 40
    assert placeholders["tower_risk_review_granted_count"] == 0
    assert placeholders["reviewer_bound_count"] == 0
    assert placeholders["reviewer_confirmed_count"] == 0
    assert placeholders["safe_to_continue_severity_placeholders"] is True

    for item in placeholders["severity_placeholder_items"]:
        assert item["severity_placeholder_id"].startswith("VSPSV-")
        assert item["risk_card_id"].startswith("VSPRM-")
        assert item["severity_status"] == "EMPTY_NOT_ASSIGNED_NOT_FINALIZED"
        assert item["metadata_only"] is True
        assert item["severity_required"] is True
        assert item["severity_present"] is False
        assert item["severity_level"] is None
        assert item["severity_finalized"] is False
        assert item["risk_accepted"] is False
        assert item["risk_waived"] is False
        assert item["provider_selected"] is False
        assert item["tower_risk_review_required"] is True
        assert item["tower_risk_review_granted"] is False


def test_gp053_mitigation_placeholders_empty_not_approved():
    placeholders = get_storage_provider_risk_mitigation_placeholders()["mitigation_placeholders"]

    assert placeholders["mitigation_placeholder_count"] == 160
    assert placeholders["mitigation_field_type_count"] == 4
    assert placeholders["risk_card_count"] == 40
    assert placeholders["mitigation_required_count"] == 160
    assert placeholders["mitigation_present_count"] == 0
    assert placeholders["mitigation_approved_count"] == 0
    assert placeholders["risk_accepted_count"] == 0
    assert placeholders["risk_waived_count"] == 0
    assert placeholders["provider_recommended_count"] == 0
    assert placeholders["provider_selected_count"] == 0
    assert placeholders["provider_configured_count"] == 0
    assert placeholders["tower_risk_review_required_count"] == 160
    assert placeholders["tower_risk_review_granted_count"] == 0
    assert placeholders["reviewer_bound_count"] == 0
    assert placeholders["reviewer_confirmed_count"] == 0
    assert placeholders["safe_to_continue_mitigation_placeholders"] is True

    fields = {item["mitigation_field"] for item in placeholders["mitigation_placeholder_items"]}
    assert fields == {
        "owner_mitigation_note",
        "tower_mitigation_question",
        "technical_mitigation_note",
        "operational_mitigation_note",
    }

    for item in placeholders["mitigation_placeholder_items"]:
        assert item["mitigation_placeholder_id"].startswith("VSPMP-")
        assert item["risk_card_id"].startswith("VSPRM-")
        assert item["mitigation_status"] == "EMPTY_NOT_REVIEWED_NOT_APPROVED"
        assert item["metadata_only"] is True
        assert item["mitigation_required"] is True
        assert item["mitigation_present"] is False
        assert item["mitigation_approved"] is False
        assert item["risk_accepted"] is False
        assert item["risk_waived"] is False
        assert item["provider_selected"] is False
        assert item["tower_risk_review_required"] is True


def test_gp053_tower_risk_review_gates_required_not_granted():
    gates = get_storage_provider_risk_tower_review_gates()["tower_review_gates"]

    assert gates["tower_risk_review_gate_count"] == 35
    assert gates["required_count"] == 35
    assert gates["granted_count"] == 0
    assert gates["vault_override_allowed_count"] == 0
    assert gates["risk_score_finalized_count"] == 0
    assert gates["risk_accepted_count"] == 0
    assert gates["risk_waived_count"] == 0
    assert gates["mitigation_approved_count"] == 0
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
    assert gates["safe_to_continue_tower_risk_review_gates"] is True

    for item in gates["tower_risk_review_gate_items"]:
        assert item["tower_risk_review_gate_id"].startswith("VSPTRR-")
        assert item["tower_review_gate_id"].startswith("VSPTRG-")
        assert item["gate_status"] == "TOWER_RISK_REVIEW_REQUIRED_NOT_GRANTED"
        assert item["metadata_only"] is True
        assert item["required"] is True
        assert item["granted"] is False
        assert item["vault_can_override"] is False
        assert item["risk_accepted"] is False
        assert item["risk_waived"] is False
        assert item["mitigation_approved"] is False
        assert item["provider_selected"] is False
        assert item["execution_allowed"] is False


def test_gp053_risk_selection_blockers_active():
    blockers = get_storage_provider_risk_selection_blockers()["selection_blockers"]

    assert blockers["risk_selection_blocker_count"] == 45
    assert blockers["active_blocker_count"] == 45
    assert blockers["blocks_severity_finalize_count"] == 45
    assert blockers["blocks_risk_score_finalize_count"] == 45
    assert blockers["blocks_risk_acceptance_count"] == 45
    assert blockers["blocks_risk_waiver_count"] == 45
    assert blockers["blocks_mitigation_approval_count"] == 45
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
    assert blockers["safe_to_continue_risk_selection_blockers"] is True

    for item in blockers["risk_selection_blocker_items"]:
        assert item["risk_selection_blocker_id"].startswith("VSPRSB-")
        assert item["selection_blocker_id"].startswith("VSPCBL-")
        assert item["blocker_status"] == "ACTIVE_RISK_MATRIX_BLOCKER"
        assert item["metadata_only"] is True
        assert item["active"] is True
        assert item["blocks_risk_acceptance"] is True
        assert item["blocks_risk_waiver"] is True
        assert item["blocks_mitigation_approval"] is True
        assert item["blocks_provider_recommendation"] is True
        assert item["blocks_provider_selection"] is True
        assert item["blocks_provider_read"] is True
        assert item["blocks_execution"] is True
        assert item["blocks_vault_done"] is True
        assert item["owner_resolvable_now"] is False
        assert item["tower_authority_required"] is True


def test_gp053_next_step_carries_forward_to_gp054_not_clouds():
    next_step = get_storage_provider_risk_next_step()["next_step"]

    assert next_step["next_step_count"] == 3
    assert next_step["ready_for_gp054_count"] == 3
    assert next_step["risk_card_count"] == 40
    assert next_step["risk_rollup_count"] == 8
    assert next_step["severity_placeholder_count"] == 40
    assert next_step["mitigation_placeholder_count"] == 160
    assert next_step["tower_risk_review_gate_count"] == 35
    assert next_step["risk_selection_blocker_count"] == 45
    assert next_step["safe_to_continue_to_gp054"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False
    assert next_step["recommended_next_pack"] == "VAULT_GP054_STORAGE_PROVIDER_COMPARISON_BOARD"
    assert next_step["recommended_next_pack_title"] == "Storage Provider Comparison Board"

    note = next_step["owner_notebook_note"].lower()
    assert "archive vault — storage provider prep layer" in note
    assert "gp051-gp060" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "provider risk matrix metadata-only" in rules
    assert "do not accept risk" in rules
    assert "do not waive risk" in rules
    assert "do not approve mitigation" in rules
    assert "do not recommend a provider" in rules
    assert "do not select a provider" in rules
    assert "not vault done" in rules

    for item in next_step["next_step_items"]:
        assert item["next_step_id"].startswith("VSPRMNX-")
        assert item["target_pack"] == "VAULT_GP054_STORAGE_PROVIDER_COMPARISON_BOARD"
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False


def test_gp053_routes_counts_and_boundaries_declared():
    home = get_storage_provider_risk_matrix_home()
    routes = home["risk_routes"]
    counts = home["risk_counts"]
    tower = home["tower_authority"]
    boundary = home["vault_boundary"]

    assert routes["section_header"] == "Archive Vault — Storage Provider Prep Layer"
    assert routes["section_range"] == "GP051-GP060"
    assert routes["route"] == "/vault/storage-provider-risk-matrix"
    assert routes["json_route"] == "/vault/storage-provider-risk-matrix.json"
    assert routes["risk_cards_route"] == "/vault/storage-provider-risk-cards.json"
    assert routes["risk_rollups_route"] == "/vault/storage-provider-risk-rollups.json"
    assert routes["severity_placeholders_route"] == "/vault/storage-provider-risk-severity-placeholders.json"
    assert routes["mitigation_placeholders_route"] == "/vault/storage-provider-risk-mitigation-placeholders.json"
    assert routes["tower_review_gates_route"] == "/vault/storage-provider-risk-tower-review-gates.json"
    assert routes["selection_blockers_route"] == "/vault/storage-provider-risk-selection-blockers.json"
    assert routes["next_step_route"] == "/vault/storage-provider-risk-next-step.json"
    assert routes["gp053_status_route"] == "/vault/gp053-status.json"

    assert counts["provider_candidate_count"] == 5
    assert counts["risk_category_count"] == 8
    assert counts["risk_card_count"] == 40
    assert counts["risk_rollup_count"] == 8
    assert counts["severity_placeholder_count"] == 40
    assert counts["mitigation_placeholder_count"] == 160
    assert counts["tower_risk_review_gate_count"] == 35
    assert counts["risk_selection_blocker_count"] == 45
    assert counts["severity_present_count"] == 0
    assert counts["risk_score_finalized_count"] == 0
    assert counts["risk_accepted_count"] == 0
    assert counts["risk_waived_count"] == 0
    assert counts["mitigation_approved_count"] == 0
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

    assert tower["tower_owns_provider_risk_review"] is True
    assert tower["tower_owns_risk_acceptance_authority"] is True
    assert tower["vault_can_accept_or_waive_risk"] is False
    assert tower["vault_can_approve_mitigation"] is False
    assert tower["vault_can_recommend_provider"] is False
    assert tower["vault_can_select_provider_without_tower"] is False
    assert tower["vault_can_mark_vault_done"] is False

    assert boundary["provider_selection_default"] == "risk_matrix_only_no_provider_selected"
    assert boundary["risk_default"] == "placeholder_only_not_accepted_not_waived"
    assert boundary["mitigation_default"] == "placeholder_only_not_approved"
    assert boundary["provider_read_allowed"] is False
    assert boundary["provider_write_allowed"] is False
    assert boundary["object_body_view_allowed"] is False
    assert boundary["public_packet_proof_allowed"] is False


def test_gp053_html_is_dark_and_mentions_risk_matrix():
    html = render_storage_provider_risk_matrix_page()
    lowered = html.lower()

    assert "Vault Storage Provider Risk Matrix" in html
    assert "Storage Provider Prep Layer" in html
    assert "Archive Vault" in html
    assert "GP053" in html
    assert "/vault/storage-provider-risk-matrix.json" in html
    assert "/vault/gp053-status.json" in html
    assert "Clouds parked" in html
    assert "No risk accepted" in html
    assert "No mitigation approved" in html
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


def test_gp053_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-provider-risk-matrix",
        "/vault/storage-provider-risk-matrix.json",
        "/vault/storage-provider-risk-cards.json",
        "/vault/storage-provider-risk-rollups.json",
        "/vault/storage-provider-risk-severity-placeholders.json",
        "/vault/storage-provider-risk-mitigation-placeholders.json",
        "/vault/storage-provider-risk-tower-review-gates.json",
        "/vault/storage-provider-risk-selection-blockers.json",
        "/vault/storage-provider-risk-next-step.json",
        "/vault/gp053-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp053_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-provider-risk-matrix",
        "/vault/storage-provider-risk-matrix.json",
        "/vault/storage-provider-risk-cards.json",
        "/vault/storage-provider-risk-rollups.json",
        "/vault/storage-provider-risk-severity-placeholders.json",
        "/vault/storage-provider-risk-mitigation-placeholders.json",
        "/vault/storage-provider-risk-tower-review-gates.json",
        "/vault/storage-provider-risk-selection-blockers.json",
        "/vault/storage-provider-risk-next-step.json",
        "/vault/gp053-status.json",
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
                assert b"Vault Storage Provider Risk Matrix" in response.data
