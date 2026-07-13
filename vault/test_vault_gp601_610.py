
from pathlib import Path

from vault.recovery_commit_owner_decision_review_layer_service import (
    CURRENT_RECOMMENDATION,
    DOCTRINE,
    LOCKS,
    get_owner_admin_control_satisfaction_review_board,
    get_owner_decision_preparation_intake_board,
    get_owner_decision_review_readiness_checkpoint,
    get_owner_decision_review_safety_blocker_board,
    get_recovery_commit_owner_decision_review_home,
    get_recovery_decision_option_evaluation_board,
    get_scope_freeze_commit_window_decision_review_board,
    get_tower_owner_decision_review_draft_board,
    get_tower_owner_decision_review_receipt_draft_ledger,
    get_tower_owner_decision_review_session_board,
    validate_recovery_commit_owner_decision_review_layer,
)


def test_gp601_610_validation_passes():
    result = (
        validate_recovery_commit_owner_decision_review_layer()
    )

    assert result["ok"] is True
    assert result["ready"] is True
    assert result["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )


def test_gp601_doctrine_is_review_only():
    home = (
        get_recovery_commit_owner_decision_review_home()
    )

    assert home["ready"] is True
    assert DOCTRINE["tower"] == "face_protocol_authority"
    assert DOCTRINE["teller"] == "workflow_request_source"
    assert DOCTRINE["vault"] == "sealed_memory"
    assert DOCTRINE["correct_flow"] == (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    )
    assert DOCTRINE[
        "owner_decision_review_only"
    ] is True
    assert DOCTRINE[
        "owner_decision_recording_allowed"
    ] is False
    assert DOCTRINE[
        "technical_readiness_is_not_authorization"
    ] is True
    assert DOCTRINE["review_session_started"] is False
    assert DOCTRINE["owner_authenticated"] is False
    assert DOCTRINE[
        "owner_decision_recorded"
    ] is False
    assert DOCTRINE["go_decision_granted"] is False
    assert DOCTRINE[
        "teller_can_call_vault_directly"
    ] is False


def test_gp602_preparation_packet_is_verified():
    board = (
        get_owner_decision_preparation_intake_board()
    )

    assert board["ready"] is True
    assert board["intake_count"] >= 1
    assert board[
        "all_preparation_packets_verified"
    ] is True
    assert board["all_criteria_verified"] is True
    assert board["all_controls_verified"] is True
    assert board[
        "all_activation_plans_verified"
    ] is True
    assert board[
        "all_alternatives_verified"
    ] is True
    assert board[
        "all_decision_records_verified"
    ] is True
    assert board["all_receipts_verified"] is True
    assert board[
        "all_eligible_for_owner_review"
    ] is True
    assert board[
        "no_owner_decisions_recorded"
    ] is True
    assert board[
        "no_live_authorization_granted"
    ] is True


def test_gp603_tower_review_session_is_ready_not_started():
    board = (
        get_tower_owner_decision_review_session_board()
    )

    assert board["ready"] is True
    assert board["session_count"] >= 1
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
        "all_step_up_challenges_required"
    ] is True
    assert board[
        "all_dual_receipt_reviews_required"
    ] is True
    assert board[
        "all_second_authority_reviews_required"
    ] is True
    assert board["no_sessions_started"] is True
    assert board[
        "no_owners_authenticated"
    ] is True
    assert board[
        "no_owner_decisions_recorded"
    ] is True
    assert board[
        "all_session_hashes_present"
    ] is True


def test_gp604_owner_controls_remain_pending():
    board = (
        get_owner_admin_control_satisfaction_review_board()
    )

    assert board["ready"] is True
    assert board["review_count"] >= 1
    assert board[
        "all_owner_admin_approval_required"
    ] is True
    assert board["all_step_up_required"] is True
    assert board[
        "all_dual_receipts_required"
    ] is True
    assert board[
        "all_second_authority_reviews_required"
    ] is True
    assert board[
        "no_owner_admin_approval_granted"
    ] is True
    assert board["no_step_up_satisfied"] is True
    assert board[
        "no_dual_receipts_satisfied"
    ] is True
    assert board[
        "no_second_authority_granted"
    ] is True
    assert board[
        "no_control_gates_complete"
    ] is True
    assert board[
        "all_no_go_holds_required"
    ] is True
    assert board[
        "all_control_hashes_present"
    ] is True


def test_gp605_activation_review_changes_nothing():
    board = (
        get_scope_freeze_commit_window_decision_review_board()
    )

    assert board["ready"] is True
    assert board["review_count"] >= 1
    assert board["all_exact_scopes_bound"] is True
    assert board[
        "all_one_time_windows_required"
    ] is True
    assert board[
        "all_activation_steps_required"
    ] is True
    assert board["nothing_activated"] is True
    assert board[
        "no_activation_decisions_recorded"
    ] is True
    assert board[
        "no_activation_gates_complete"
    ] is True
    assert board[
        "no_production_targets_allowed"
    ] is True
    assert board[
        "no_external_providers_allowed"
    ] is True
    assert board[
        "all_activation_hashes_present"
    ] is True


def test_gp606_go_option_remains_unavailable():
    board = (
        get_recovery_decision_option_evaluation_board()
    )

    assert board["ready"] is True
    assert board["evaluation_count"] >= 1
    assert board[
        "all_have_three_available_options"
    ] is True
    assert board[
        "all_hold_options_available"
    ] is True
    assert board[
        "all_remediation_options_available"
    ] is True
    assert board[
        "all_defer_options_available"
    ] is True
    assert board[
        "no_go_options_available"
    ] is True
    assert board[
        "all_owner_selections_pending"
    ] is True
    assert board[
        "all_recommendations_are_no_go_hold"
    ] is True
    assert board[
        "all_option_hashes_present"
    ] is True


def test_gp607_review_draft_is_ready_but_pending():
    board = (
        get_tower_owner_decision_review_draft_board()
    )

    assert board["ready"] is True
    assert board["draft_count"] >= 1
    assert board[
        "all_preparation_packets_complete"
    ] is True
    assert board[
        "all_review_sessions_ready"
    ] is True
    assert board["all_controls_pending"] is True
    assert board[
        "all_activations_pending"
    ] is True
    assert board[
        "all_owner_selections_pending"
    ] is True
    assert board[
        "all_recommendations_are_no_go_hold"
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
        "all_review_hashes_present"
    ] is True


def test_gp608_receipts_are_append_only_drafts():
    ledger = (
        get_tower_owner_decision_review_receipt_draft_ledger()
    )

    assert ledger["ready"] is True
    assert ledger["receipt_count"] >= 1
    assert ledger["all_tower_controlled"] is True
    assert ledger[
        "all_review_components_recorded"
    ] is True
    assert ledger[
        "no_final_owner_decisions_recorded"
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


def test_gp609_all_dangerous_actions_are_blocked():
    board = (
        get_owner_decision_review_safety_blocker_board()
    )

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board[
        "all_dangerous_actions_blocked"
    ] is True


def test_gp610_readiness_passes_and_corridor_continues():
    checkpoint = (
        get_owner_decision_review_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True
    assert all(
        checkpoint["checks"].values()
    )
    assert checkpoint["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )
    assert checkpoint["review_status"] == (
        "owner_review_packet_ready_"
        "review_session_not_started_"
        "owner_decision_not_recorded_"
        "all_execution_locks_closed"
    )
    assert checkpoint["corridor_continues"] is True
    assert checkpoint[
        "operational_readiness_gate_reached"
    ] is False
    assert (
        "OWNER DECISION RECORDING GATE"
        in checkpoint["next_recommended_layer"]
    )


def test_gp601_610_global_locks_remain_closed():
    assert LOCKS["review_session_started"] is False
    assert LOCKS["owner_authenticated"] is False
    assert LOCKS[
        "owner_decision_recorded"
    ] is False
    assert LOCKS["go_decision_granted"] is False
    assert LOCKS[
        "live_recovery_authorization_granted"
    ] is False
    assert LOCKS[
        "authorization_token_issued"
    ] is False
    assert LOCKS[
        "owner_admin_approval_granted"
    ] is False
    assert LOCKS["step_up_satisfied"] is False
    assert LOCKS["dual_receipt_satisfied"] is False
    assert LOCKS[
        "second_authority_review_granted"
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


def test_gp601_610_routes_are_json_only():
    app_text = Path("web/app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_routes = [
        "/vault/recovery-commit-owner-decision-review-layer.json",
        "/vault/recovery-commit-owner-decision-review-shell.json",
        "/vault/owner-decision-preparation-intake-board.json",
        "/vault/tower-owner-decision-review-session-board.json",
        "/vault/owner-admin-control-satisfaction-review-board.json",
        "/vault/scope-freeze-commit-window-decision-review-board.json",
        "/vault/recovery-decision-option-evaluation-board.json",
        "/vault/tower-owner-decision-review-draft-board.json",
        "/vault/tower-owner-decision-review-receipt-draft-ledger.json",
        "/vault/owner-decision-review-safety-blocker-board.json",
        "/vault/owner-decision-review-readiness.json",
        "/vault/gp601-status.json",
        "/vault/gp610-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert (
        '@app.route("/vault/recovery-commit-owner-'
        'decision-review-layer")'
        not in app_text
    )
