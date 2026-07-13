
from pathlib import Path

from vault.recovery_commit_owner_decision_recording_gate_service import (
    ALLOWED_DECISION_VALUES,
    CURRENT_RECOMMENDATION,
    DOCTRINE,
    LOCKS,
    RECORDING_CONTRACT_FIELDS,
    get_owner_admin_approval_dual_receipt_recording_gate,
    get_owner_decision_recording_gate_readiness_checkpoint,
    get_owner_decision_recording_safety_blocker_board,
    get_owner_decision_selection_recording_contract_board,
    get_owner_identity_step_up_recording_prerequisite_board,
    get_recovery_commit_owner_decision_recording_gate_home,
    get_scope_freeze_commit_window_recording_boundary_board,
    get_tower_owner_decision_append_only_record_draft_board,
    get_tower_owner_decision_recording_receipt_draft_ledger,
    get_tower_owner_review_intake_verification_board,
    validate_recovery_commit_owner_decision_recording_gate,
)


def test_gp611_620_validation_passes():
    result = (
        validate_recovery_commit_owner_decision_recording_gate()
    )

    assert result["ok"] is True
    assert result["ready"] is True
    assert result["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )


def test_gp611_doctrine_is_recording_definition_only():
    home = (
        get_recovery_commit_owner_decision_recording_gate_home()
    )

    assert home["ready"] is True
    assert DOCTRINE["tower"] == "face_protocol_authority"
    assert DOCTRINE["teller"] == "workflow_request_source"
    assert DOCTRINE["vault"] == "sealed_memory"
    assert DOCTRINE["correct_flow"] == (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    )
    assert DOCTRINE[
        "tower_is_only_recording_boundary"
    ] is True
    assert DOCTRINE[
        "recording_gate_definition_only"
    ] is True
    assert DOCTRINE[
        "recording_execution_allowed"
    ] is False
    assert DOCTRINE["owner_authenticated"] is False
    assert DOCTRINE[
        "owner_selection_present"
    ] is False
    assert DOCTRINE[
        "owner_decision_recorded"
    ] is False
    assert DOCTRINE["go_decision_granted"] is False
    assert DOCTRINE[
        "teller_can_call_vault_directly"
    ] is False


def test_gp612_owner_review_packet_is_verified():
    board = (
        get_tower_owner_review_intake_verification_board()
    )

    assert board["ready"] is True
    assert board["intake_count"] >= 1
    assert board[
        "all_review_packets_verified"
    ] is True
    assert board[
        "all_session_requirements_verified"
    ] is True
    assert board[
        "all_control_requirements_verified"
    ] is True
    assert board[
        "all_activation_boundaries_verified"
    ] is True
    assert board[
        "all_decision_options_verified"
    ] is True
    assert board[
        "all_review_drafts_verified"
    ] is True
    assert board[
        "all_review_receipts_verified"
    ] is True
    assert board[
        "all_eligible_for_gate_review"
    ] is True
    assert board[
        "no_recording_gates_open"
    ] is True
    assert board[
        "no_owner_decisions_recorded"
    ] is True


def test_gp613_identity_and_step_up_are_required_not_satisfied():
    board = (
        get_owner_identity_step_up_recording_prerequisite_board()
    )

    assert board["ready"] is True
    assert board["prerequisite_count"] >= 1
    assert board[
        "all_tower_sessions_required"
    ] is True
    assert board[
        "all_owner_presence_required"
    ] is True
    assert board[
        "all_identity_verification_required"
    ] is True
    assert board[
        "all_step_up_required"
    ] is True
    assert board[
        "all_reference_requirements_present"
    ] is True
    assert board["no_sessions_started"] is True
    assert board[
        "no_owners_authenticated"
    ] is True
    assert board[
        "no_step_up_satisfied"
    ] is True
    assert board[
        "no_identity_prerequisites_complete"
    ] is True
    assert board[
        "all_prerequisite_hashes_present"
    ] is True


def test_gp614_approval_and_dual_receipt_gate_is_closed():
    board = (
        get_owner_admin_approval_dual_receipt_recording_gate()
    )

    assert board["ready"] is True
    assert board["gate_count"] >= 1
    assert board[
        "all_owner_admin_approval_required"
    ] is True
    assert board[
        "all_dual_receipts_required"
    ] is True
    assert board[
        "all_second_authority_reviews_required"
    ] is True
    assert board[
        "all_receipt_references_required"
    ] is True
    assert board[
        "no_owner_admin_approval_granted"
    ] is True
    assert board[
        "no_dual_receipts_satisfied"
    ] is True
    assert board[
        "no_second_authority_granted"
    ] is True
    assert board[
        "no_approval_gates_complete"
    ] is True
    assert board[
        "all_gate_hashes_present"
    ] is True


def test_gp615_recording_contract_is_complete_but_unselected():
    board = (
        get_owner_decision_selection_recording_contract_board()
    )

    assert board["ready"] is True
    assert board["contract_count"] >= 1
    assert len(ALLOWED_DECISION_VALUES) == 4
    assert "GRANT_GO" in ALLOWED_DECISION_VALUES
    assert "request_id" in RECORDING_CONTRACT_FIELDS
    assert (
        "owner_identity_verification_receipt_reference"
        in RECORDING_CONTRACT_FIELDS
    )
    assert (
        "idempotency_key"
        in RECORDING_CONTRACT_FIELDS
    )
    assert board[
        "all_decision_enums_complete"
    ] is True
    assert board[
        "no_selected_decisions_present"
    ] is True
    assert board[
        "all_integrity_requirements_present"
    ] is True
    assert board[
        "no_mutation_allowed"
    ] is True
    assert board[
        "no_raw_material_allowed"
    ] is True
    assert board[
        "all_contract_hashes_present"
    ] is True


def test_gp616_scope_window_boundary_changes_nothing():
    board = (
        get_scope_freeze_commit_window_recording_boundary_board()
    )

    assert board["ready"] is True
    assert board["boundary_count"] >= 1
    assert board["all_exact_scopes_bound"] is True
    assert board[
        "all_one_time_windows_required"
    ] is True
    assert board[
        "all_scope_window_hashes_required"
    ] is True
    assert board["nothing_activated"] is True
    assert board[
        "recording_cannot_activate_scope_or_window"
    ] is True
    assert board[
        "no_production_targets_allowed"
    ] is True
    assert board[
        "no_external_providers_allowed"
    ] is True
    assert board[
        "all_boundary_hashes_present"
    ] is True


def test_gp617_record_draft_is_append_only_and_closed():
    board = (
        get_tower_owner_decision_append_only_record_draft_board()
    )

    assert board["ready"] is True
    assert board["draft_count"] >= 1
    assert board[
        "all_source_hashes_present"
    ] is True
    assert board[
        "all_ready_for_future_tower_input"
    ] is True
    assert board[
        "no_recording_gates_open"
    ] is True
    assert board[
        "no_owner_selections_present"
    ] is True
    assert board[
        "no_owner_decisions_recorded"
    ] is True
    assert board[
        "no_go_decisions_granted"
    ] is True
    assert board[
        "no_authorization_or_tokens"
    ] is True
    assert board[
        "no_commit_restore_or_write"
    ] is True
    assert board[
        "all_drafts_unfinalized"
    ] is True
    assert board["all_append_only"] is True
    assert board["all_immutable"] is True
    assert board[
        "all_record_hashes_present"
    ] is True


def test_gp618_receipts_are_append_only_gate_drafts():
    ledger = (
        get_tower_owner_decision_recording_receipt_draft_ledger()
    )

    assert ledger["ready"] is True
    assert ledger["receipt_count"] >= 1
    assert ledger["all_tower_controlled"] is True
    assert ledger[
        "all_gate_definition_components_recorded"
    ] is True
    assert ledger[
        "no_owner_selection_or_decision_recorded"
    ] is True
    assert ledger[
        "no_authorization_or_tokens_recorded"
    ] is True
    assert ledger[
        "no_commit_restore_or_write_recorded"
    ] is True
    assert ledger[
        "no_raw_or_public_recorded"
    ] is True
    assert ledger["all_receipts_draft"] is True
    assert ledger["all_append_only"] is True
    assert ledger["all_immutable"] is True
    assert ledger[
        "all_receipt_hashes_present"
    ] is True


def test_gp619_all_dangerous_actions_are_blocked():
    board = (
        get_owner_decision_recording_safety_blocker_board()
    )

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board[
        "all_dangerous_actions_blocked"
    ] is True


def test_gp620_readiness_passes_and_corridor_continues():
    checkpoint = (
        get_owner_decision_recording_gate_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True
    assert all(
        checkpoint["checks"].values()
    )
    assert checkpoint["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )
    assert checkpoint["recording_gate_status"] == (
        "recording_contract_ready_"
        "identity_and_approval_prerequisites_pending_"
        "recording_gate_closed_"
        "no_owner_decision_recorded"
    )
    assert checkpoint["corridor_continues"] is True
    assert checkpoint[
        "operational_readiness_gate_reached"
    ] is False
    assert (
        "OWNER DECISION RECORDING CLOSEOUT"
        in checkpoint["next_recommended_layer"]
    )


def test_gp611_620_global_locks_remain_closed():
    assert LOCKS["recording_gate_open"] is False
    assert LOCKS[
        "recording_execution_allowed"
    ] is False
    assert LOCKS["review_session_started"] is False
    assert LOCKS["owner_authenticated"] is False
    assert LOCKS[
        "owner_selection_present"
    ] is False
    assert LOCKS[
        "owner_decision_recorded"
    ] is False
    assert LOCKS["go_decision_granted"] is False
    assert LOCKS[
        "owner_admin_approval_granted"
    ] is False
    assert LOCKS["step_up_satisfied"] is False
    assert LOCKS["dual_receipt_satisfied"] is False
    assert LOCKS[
        "second_authority_review_granted"
    ] is False
    assert LOCKS[
        "live_recovery_authorization_granted"
    ] is False
    assert LOCKS[
        "authorization_token_issued"
    ] is False
    assert LOCKS[
        "scope_freeze_activated"
    ] is False
    assert LOCKS[
        "commit_window_activated"
    ] is False
    assert LOCKS["execution_window_open"] is False
    assert LOCKS["commit_point_open"] is False
    assert LOCKS["commit_command_issued"] is False
    assert LOCKS[
        "actual_restore_execution_allowed"
    ] is False
    assert LOCKS[
        "production_recovery_write_allowed"
    ] is False
    assert LOCKS[
        "external_provider_connection_allowed"
    ] is False
    assert LOCKS[
        "raw_file_bytes_returned_by_json"
    ] is False
    assert LOCKS[
        "raw_file_bytes_materialized"
    ] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS[
        "raw_recovery_token_exposed"
    ] is False
    assert LOCKS["public_url_created"] is False
    assert LOCKS["share_link_created"] is False
    assert LOCKS[
        "teller_to_vault_direct_call_allowed"
    ] is False
    assert LOCKS[
        "resident_vault_access_allowed"
    ] is False
    assert LOCKS[
        "vendor_vault_access_allowed"
    ] is False
    assert LOCKS[
        "public_vault_access_allowed"
    ] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS[
        "quarantine_release_allowed"
    ] is False
    assert LOCKS[
        "physical_object_move_allowed"
    ] is False


def test_gp611_620_routes_are_json_only():
    app_text = Path("web/app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_routes = [
        "/vault/recovery-commit-owner-decision-recording-gate.json",
        "/vault/recovery-commit-owner-decision-recording-gate-shell.json",
        "/vault/tower-owner-review-intake-verification-board.json",
        "/vault/owner-identity-step-up-recording-prerequisite-board.json",
        "/vault/owner-admin-approval-dual-receipt-recording-gate.json",
        "/vault/owner-decision-selection-recording-contract-board.json",
        "/vault/scope-freeze-commit-window-recording-boundary-board.json",
        "/vault/tower-owner-decision-append-only-record-draft-board.json",
        "/vault/tower-owner-decision-recording-receipt-draft-ledger.json",
        "/vault/owner-decision-recording-safety-blocker-board.json",
        "/vault/owner-decision-recording-gate-readiness.json",
        "/vault/gp611-status.json",
        "/vault/gp620-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert (
        '@app.route("/vault/recovery-commit-owner-'
        'decision-recording-gate")'
        not in app_text
    )
