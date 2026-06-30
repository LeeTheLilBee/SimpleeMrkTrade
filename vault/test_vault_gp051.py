"""
Tests for VAULT GIANT PACK 051 — Storage Provider Selection Prep
"""

from pathlib import Path

import pytest

from vault.storage_provider_selection_prep_service import (
    get_gp051_status,
    get_storage_provider_candidates,
    get_storage_provider_prep_notes,
    get_storage_provider_selection_criteria,
    get_storage_provider_selection_locks,
    get_storage_provider_selection_next_step,
    get_storage_provider_selection_prep_home,
    get_storage_provider_tower_authority_gates,
    render_storage_provider_selection_prep_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp051_status_ready_new_section_safe_continue_not_done():
    status = get_gp051_status()
    gp051 = status["gp051_status"]

    assert status["pack"]["id"] == "VAULT_GP051"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert status["pack"]["section_range"] == "GP051-GP060"
    assert status["pack"]["previous_section"] == "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
    assert status["pack"]["previous_section_range"] == "GP041-GP050"
    assert status["pack"]["starts_new_section"] is True

    assert gp051["ready"] is True
    assert gp051["section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp051["section_title"] == "Archive Vault — Storage Provider Prep Layer"
    assert gp051["section_range"] == "GP051-GP060"
    assert gp051["storage_provider_selection_prep_ready"] is True
    assert gp051["new_section_started"] is True
    assert gp051["safe_to_continue_to_gp052"] is True
    assert gp051["vault_done"] is False
    assert gp051["foundation_status"] == "safe_to_continue_not_done"
    assert gp051["metadata_only_provider_prep"] is True
    assert gp051["private_provider_prep_only"] is True
    assert gp051["provider_candidates_ready"] is True
    assert gp051["provider_selected"] is False
    assert gp051["provider_configured"] is False
    assert gp051["provider_write_enabled"] is False
    assert gp051["provider_read_enabled"] is False
    assert gp051["provider_object_read_claimed"] is False
    assert gp051["provider_connection_tested"] is False
    assert gp051["object_body_view_enabled"] is False
    assert gp051["raw_file_body_storage_still_locked"] is True
    assert gp051["file_body_persisted_count"] == 0
    assert gp051["object_body_available_count"] == 0
    assert gp051["direct_upload_still_locked"] is True
    assert gp051["checksum_verification_not_claimed"] is True
    assert gp051["hash_verification_not_claimed"] is True
    assert gp051["official_receipt_count"] == 0
    assert gp051["finalized_receipt_count"] == 0
    assert gp051["closed_receipt_count"] == 0
    assert gp051["official_audit_log_written_count"] == 0
    assert gp051["immutable_audit_write_count"] == 0
    assert gp051["access_request_granted_count"] == 0
    assert gp051["decision_granted_count"] == 0
    assert gp051["action_approved_count"] == 0
    assert gp051["action_executed_count"] == 0
    assert gp051["external_delivery_still_locked"] is True
    assert gp051["packet_export_still_locked"] is True
    assert gp051["approval_disabled"] is True
    assert gp051["execution_engine_disabled"] is True
    assert gp051["clouds_status"] == "parked_do_not_continue_from_vault_gp051"
    assert gp051["next_pack"] == "VAULT_GP052_STORAGE_PROVIDER_CRITERIA_BOARD"


def test_gp051_selection_truth_keeps_provider_unselected_unconfigured():
    status = get_gp051_status()
    truth = status["selection_truth"]

    assert truth["storage_provider_selection_prep_ready"] is True
    assert truth["new_section_started"] is True
    assert truth["provider_candidate_previews_visible"] is True
    assert truth["selection_criteria_visible"] is True
    assert truth["selection_locks_visible"] is True
    assert truth["tower_provider_authority_gates_visible"] is True
    assert truth["provider_prep_notes_visible"] is True
    assert truth["metadata_only"] is True
    assert truth["private_prep_only"] is True
    assert truth["provider_candidate_count"] == 5
    assert truth["selection_criteria_count"] == 40
    assert truth["selection_lock_count"] == 45
    assert truth["tower_provider_gate_count"] == 35
    assert truth["prep_note_placeholder_count"] == 20

    assert truth["provider_selected_count"] == 0
    assert truth["provider_configured_count"] == 0
    assert truth["provider_write_enabled_count"] == 0
    assert truth["provider_read_enabled_count"] == 0
    assert truth["provider_object_read_claimed_count"] == 0
    assert truth["provider_connection_tested_count"] == 0
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["file_body_persisted_count"] == 0
    assert truth["object_body_available_count"] == 0
    assert truth["object_body_view_enabled"] is False
    assert truth["direct_upload_unlocked"] is False
    assert truth["checksum_verified_count"] == 0
    assert truth["hash_verified_count"] == 0
    assert truth["official_storage_receipt_claimed_count"] == 0
    assert truth["finalized_storage_receipt_count"] == 0
    assert truth["closed_storage_receipt_count"] == 0
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
    assert truth["vault_done"] is False
    assert truth["clouds_should_continue"] is False
    assert truth["safe_to_continue_to_gp052"] is True


def test_gp051_connected_to_gp050_new_section():
    home = get_storage_provider_selection_prep_home()
    gp050 = home["gp050_connection"]

    assert gp050["gp050_pack_id"] == "VAULT_GP050"
    assert gp050["gp050_ready"] is True
    assert gp050["gp050_section_closed"] is True
    assert gp050["gp050_safe_to_continue"] is True
    assert gp050["gp050_vault_done"] is False
    assert gp050["gp050_next_section_id"] == "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
    assert gp050["gp050_next_section_title"] == "Archive Vault — Storage Provider Prep Layer"
    assert gp050["gp050_next_section_range"] == "GP051-GP060"
    assert gp050["gp050_next_pack"] == "VAULT_GP051_STORAGE_PROVIDER_SELECTION_PREP"


def test_gp051_provider_candidates_are_preview_only():
    candidates = get_storage_provider_candidates()["provider_candidates"]

    assert candidates["provider_candidate_count"] == 5
    assert candidates["candidate_visible_count"] == 5
    assert candidates["provider_selected_count"] == 0
    assert candidates["provider_configured_count"] == 0
    assert candidates["provider_read_enabled_count"] == 0
    assert candidates["provider_write_enabled_count"] == 0
    assert candidates["provider_object_read_claimed_count"] == 0
    assert candidates["provider_connection_tested_count"] == 0
    assert candidates["tower_provider_authority_required_count"] == 5
    assert candidates["tower_provider_authority_granted_count"] == 0
    assert candidates["object_body_view_enabled_count"] == 0
    assert candidates["raw_file_body_storage_enabled_count"] == 0
    assert candidates["file_body_persisted_count"] == 0
    assert candidates["object_body_available_count"] == 0
    assert candidates["direct_upload_enabled_count"] == 0
    assert candidates["checksum_verified_count"] == 0
    assert candidates["hash_verified_count"] == 0
    assert candidates["official_receipt_claimed_count"] == 0
    assert candidates["receipt_finalized_count"] == 0
    assert candidates["receipt_closed_count"] == 0
    assert candidates["official_audit_log_written_count"] == 0
    assert candidates["immutable_audit_written_count"] == 0
    assert candidates["access_granted_count"] == 0
    assert candidates["action_approved_count"] == 0
    assert candidates["action_executed_count"] == 0
    assert candidates["export_allowed_count"] == 0
    assert candidates["external_delivery_allowed_count"] == 0
    assert candidates["portal_access_allowed_count"] == 0
    assert candidates["execution_allowed_count"] == 0
    assert candidates["safe_to_continue_provider_candidates"] is True

    candidate_types = {item["candidate_type"] for item in candidates["provider_candidate_items"]}
    assert candidate_types == {
        "encrypted_object_storage_candidate",
        "private_archive_bucket_candidate",
        "evidence_packet_store_candidate",
        "receipt_metadata_store_candidate",
        "immutable_audit_log_store_candidate",
    }

    for item in candidates["provider_candidate_items"]:
        assert item["provider_candidate_id"].startswith("VSPC-")
        assert item["candidate_status"] == "CANDIDATE_PREVIEW_ONLY_NOT_SELECTED"
        assert item["metadata_only"] is True
        assert item["private_prep_only"] is True
        assert item["candidate_visible"] is True
        assert item["provider_selected"] is False
        assert item["provider_configured"] is False
        assert item["provider_read_enabled"] is False
        assert item["provider_write_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["execution_allowed"] is False


def test_gp051_selection_criteria_required_not_satisfied_not_verified():
    criteria = get_storage_provider_selection_criteria()["selection_criteria"]

    assert criteria["selection_criteria_count"] == 40
    assert criteria["criteria_type_count"] == 8
    assert criteria["provider_candidate_count"] == 5
    assert criteria["required_count"] == 40
    assert criteria["satisfied_count"] == 0
    assert criteria["verified_count"] == 0
    assert criteria["tower_authority_required_count"] == 40
    assert criteria["tower_authority_granted_count"] == 0
    assert criteria["provider_selected_count"] == 0
    assert criteria["provider_configured_count"] == 0
    assert criteria["provider_read_enabled_count"] == 0
    assert criteria["provider_write_enabled_count"] == 0
    assert criteria["object_body_view_enabled_count"] == 0
    assert criteria["export_allowed_count"] == 0
    assert criteria["execution_allowed_count"] == 0
    assert criteria["safe_to_continue_selection_criteria"] is True

    criterion_names = {item["criterion"] for item in criteria["selection_criteria_items"]}
    assert criterion_names == {
        "tower_authority_required",
        "private_vault_boundary_required",
        "metadata_first_support_required",
        "encryption_support_required",
        "audit_trace_support_required",
        "no_public_access_default_required",
        "object_body_locked_until_authorized",
        "export_lock_compatibility_required",
    }

    for item in criteria["selection_criteria_items"]:
        assert item["selection_criteria_id"].startswith("VSPCR-")
        assert item["criterion_status"] == "REQUIRED_NOT_SATISFIED_NOT_VERIFIED"
        assert item["metadata_only"] is True
        assert item["required"] is True
        assert item["satisfied"] is False
        assert item["verified"] is False
        assert item["tower_authority_required"] is True
        assert item["tower_authority_granted"] is False
        assert item["provider_selected"] is False
        assert item["execution_allowed"] is False


def test_gp051_selection_locks_active_and_blocking():
    locks = get_storage_provider_selection_locks()["selection_locks"]

    assert locks["selection_lock_count"] == 45
    assert locks["lock_type_count"] == 9
    assert locks["provider_candidate_count"] == 5
    assert locks["active_lock_count"] == 45
    assert locks["blocks_provider_selection_count"] == 45
    assert locks["blocks_provider_configuration_count"] == 45
    assert locks["blocks_provider_read_count"] == 45
    assert locks["blocks_provider_write_count"] == 45
    assert locks["blocks_object_body_view_count"] == 45
    assert locks["blocks_raw_file_body_storage_count"] == 45
    assert locks["blocks_direct_upload_count"] == 45
    assert locks["blocks_checksum_hash_verification_claim_count"] == 45
    assert locks["blocks_export_count"] == 45
    assert locks["blocks_external_delivery_count"] == 45
    assert locks["blocks_execution_count"] == 45
    assert locks["blocks_vault_done_count"] == 45
    assert locks["owner_resolvable_now_count"] == 0
    assert locks["tower_authority_required_count"] == 45
    assert locks["safe_to_continue_selection_locks"] is True

    lock_names = {item["lock_name"] for item in locks["selection_lock_items"]}
    assert "provider_selection_blocked" in lock_names
    assert "provider_read_blocked" in lock_names
    assert "object_body_view_blocked" in lock_names
    assert "direct_upload_blocked" in lock_names
    assert "external_export_blocked" in lock_names

    for item in locks["selection_lock_items"]:
        assert item["selection_lock_id"].startswith("VSPL-")
        assert item["lock_status"] == "ACTIVE_SELECTION_PREP_LOCK"
        assert item["metadata_only"] is True
        assert item["active"] is True
        assert item["blocks_provider_selection"] is True
        assert item["blocks_provider_configuration"] is True
        assert item["blocks_provider_read"] is True
        assert item["blocks_provider_write"] is True
        assert item["blocks_object_body_view"] is True
        assert item["blocks_execution"] is True
        assert item["blocks_vault_done"] is True
        assert item["owner_resolvable_now"] is False
        assert item["tower_authority_required"] is True


def test_gp051_tower_provider_authority_gates_required_not_granted():
    gates = get_storage_provider_tower_authority_gates()["tower_authority_gates"]

    assert gates["tower_provider_gate_count"] == 35
    assert gates["gate_type_count"] == 7
    assert gates["provider_candidate_count"] == 5
    assert gates["required_count"] == 35
    assert gates["granted_count"] == 0
    assert gates["vault_override_allowed_count"] == 0
    assert gates["provider_selected_count"] == 0
    assert gates["provider_configured_count"] == 0
    assert gates["provider_read_enabled_count"] == 0
    assert gates["provider_write_enabled_count"] == 0
    assert gates["object_body_view_enabled_count"] == 0
    assert gates["official_receipt_claimed_count"] == 0
    assert gates["official_audit_log_written_count"] == 0
    assert gates["access_granted_count"] == 0
    assert gates["export_allowed_count"] == 0
    assert gates["execution_allowed_count"] == 0
    assert gates["safe_to_continue_tower_authority_gates"] is True

    gate_names = {item["gate_name"] for item in gates["tower_provider_gate_items"]}
    assert gate_names == {
        "tower_identity_gate",
        "tower_clearance_gate",
        "tower_storage_provider_authority_gate",
        "tower_storage_access_authority_gate",
        "tower_object_visibility_gate",
        "tower_export_lock_gate",
        "tower_execution_lock_gate",
    }

    for item in gates["tower_provider_gate_items"]:
        assert item["tower_provider_gate_id"].startswith("VSPTG-")
        assert item["gate_status"] == "TOWER_PROVIDER_AUTHORITY_REQUIRED_NOT_GRANTED"
        assert item["metadata_only"] is True
        assert item["required"] is True
        assert item["granted"] is False
        assert item["vault_can_override"] is False
        assert item["provider_selected"] is False
        assert item["provider_read_enabled"] is False
        assert item["object_body_view_enabled"] is False
        assert item["execution_allowed"] is False


def test_gp051_prep_notes_empty_unconfirmed():
    notes = get_storage_provider_prep_notes()["prep_notes"]

    assert notes["prep_note_placeholder_count"] == 20
    assert notes["prep_note_field_type_count"] == 4
    assert notes["provider_candidate_count"] == 5
    assert notes["note_required_count"] == 20
    assert notes["note_present_count"] == 0
    assert notes["reviewer_bound_count"] == 0
    assert notes["reviewer_confirmed_count"] == 0
    assert notes["provider_selected_count"] == 0
    assert notes["provider_configured_count"] == 0
    assert notes["provider_read_enabled_count"] == 0
    assert notes["provider_write_enabled_count"] == 0
    assert notes["object_body_view_enabled_count"] == 0
    assert notes["export_allowed_count"] == 0
    assert notes["execution_allowed_count"] == 0
    assert notes["safe_to_continue_prep_notes"] is True

    fields = {item["note_field"] for item in notes["prep_note_placeholder_items"]}
    assert fields == {
        "owner_selection_note",
        "tower_question",
        "risk_note",
        "integration_note",
    }

    for item in notes["prep_note_placeholder_items"]:
        assert item["prep_note_placeholder_id"].startswith("VSPNP-")
        assert item["note_status"] == "EMPTY_NOT_REVIEWED_NOT_CONFIRMED"
        assert item["metadata_only"] is True
        assert item["note_required"] is True
        assert item["note_present"] is False
        assert item["reviewer_confirmed"] is False
        assert item["provider_selected"] is False
        assert item["provider_read_enabled"] is False
        assert item["execution_allowed"] is False


def test_gp051_next_step_carries_forward_to_gp052_not_clouds():
    next_step = get_storage_provider_selection_next_step()["next_step"]

    assert next_step["next_step_count"] == 3
    assert next_step["ready_for_gp052_count"] == 3
    assert next_step["provider_candidate_count"] == 5
    assert next_step["selection_criteria_count"] == 40
    assert next_step["selection_lock_count"] == 45
    assert next_step["tower_provider_gate_count"] == 35
    assert next_step["prep_note_placeholder_count"] == 20
    assert next_step["safe_to_continue_to_gp052"] is True
    assert next_step["vault_done"] is False
    assert next_step["clouds_should_continue"] is False
    assert next_step["recommended_next_pack"] == "VAULT_GP052_STORAGE_PROVIDER_CRITERIA_BOARD"
    assert next_step["recommended_next_pack_title"] == "Storage Provider Criteria Board"

    note = next_step["owner_notebook_note"].lower()
    assert "archive vault — storage provider prep layer" in note
    assert "gp051-gp060" in note
    assert "do not switch to clouds" in note

    rules = " ".join(next_step["carry_forward_rules"]).lower()
    assert "provider candidates preview-only" in rules
    assert "do not select a provider" in rules
    assert "do not configure a provider" in rules
    assert "do not enable provider read" in rules
    assert "not vault done" in rules

    for item in next_step["next_step_items"]:
        assert item["next_step_id"].startswith("VSPSPNX-")
        assert item["target_pack"] == "VAULT_GP052_STORAGE_PROVIDER_CRITERIA_BOARD"
        assert item["safe_to_continue"] is True
        assert item["vault_done"] is False
        assert item["clouds_should_continue"] is False


def test_gp051_routes_counts_and_boundaries_declared():
    home = get_storage_provider_selection_prep_home()
    routes = home["selection_routes"]
    counts = home["selection_counts"]
    tower = home["tower_authority"]
    boundary = home["vault_boundary"]

    assert routes["section_header"] == "Archive Vault — Storage Provider Prep Layer"
    assert routes["section_range"] == "GP051-GP060"
    assert routes["route"] == "/vault/storage-provider-selection-prep"
    assert routes["json_route"] == "/vault/storage-provider-selection-prep.json"
    assert routes["provider_candidates_route"] == "/vault/storage-provider-candidates.json"
    assert routes["selection_criteria_route"] == "/vault/storage-provider-selection-criteria.json"
    assert routes["selection_locks_route"] == "/vault/storage-provider-selection-locks.json"
    assert routes["tower_authority_gates_route"] == "/vault/storage-provider-tower-authority-gates.json"
    assert routes["prep_notes_route"] == "/vault/storage-provider-prep-notes.json"
    assert routes["next_step_route"] == "/vault/storage-provider-selection-next-step.json"
    assert routes["gp051_status_route"] == "/vault/gp051-status.json"

    assert counts["provider_candidate_count"] == 5
    assert counts["selection_criteria_count"] == 40
    assert counts["selection_lock_count"] == 45
    assert counts["tower_provider_gate_count"] == 35
    assert counts["prep_note_placeholder_count"] == 20
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

    assert tower["tower_owns_storage_provider_authorization"] is True
    assert tower["tower_owns_storage_access_authorization"] is True
    assert tower["tower_owns_object_visibility"] is True
    assert tower["vault_can_select_provider_without_tower"] is False
    assert tower["vault_can_configure_provider_without_tower"] is False
    assert tower["vault_can_enable_provider_read"] is False
    assert tower["vault_can_enable_provider_write"] is False
    assert tower["vault_can_view_object_body"] is False
    assert tower["vault_can_mark_vault_done"] is False

    assert boundary["provider_selection_default"] == "candidate_preview_only_no_provider_selected"
    assert boundary["provider_configuration_default"] == "locked_not_configured"
    assert boundary["provider_read_default"] == "locked_not_enabled"
    assert boundary["provider_write_default"] == "locked_not_enabled"
    assert boundary["object_body_default"] == "locked_not_visible"
    assert boundary["provider_read_allowed"] is False
    assert boundary["provider_write_allowed"] is False
    assert boundary["object_body_view_allowed"] is False
    assert boundary["public_packet_proof_allowed"] is False


def test_gp051_html_is_dark_and_mentions_new_section():
    html = render_storage_provider_selection_prep_page()
    lowered = html.lower()

    assert "Vault Storage Provider Selection Prep" in html
    assert "Archive Vault" in html
    assert "GP051" in html
    assert "Storage Provider Prep Layer" in html
    assert "/vault/storage-provider-selection-prep.json" in html
    assert "/vault/gp051-status.json" in html
    assert "Clouds parked" in html
    assert "No provider selected" in html
    assert "No provider access" in html
    assert "No object body view" in html

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


def test_gp051_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/storage-provider-selection-prep",
        "/vault/storage-provider-selection-prep.json",
        "/vault/storage-provider-candidates.json",
        "/vault/storage-provider-selection-criteria.json",
        "/vault/storage-provider-selection-locks.json",
        "/vault/storage-provider-tower-authority-gates.json",
        "/vault/storage-provider-prep-notes.json",
        "/vault/storage-provider-selection-next-step.json",
        "/vault/gp051-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp051_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/storage-provider-selection-prep",
        "/vault/storage-provider-selection-prep.json",
        "/vault/storage-provider-candidates.json",
        "/vault/storage-provider-selection-criteria.json",
        "/vault/storage-provider-selection-locks.json",
        "/vault/storage-provider-tower-authority-gates.json",
        "/vault/storage-provider-prep-notes.json",
        "/vault/storage-provider-selection-next-step.json",
        "/vault/gp051-status.json",
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
                assert b"Vault Storage Provider Selection Prep" in response.data
