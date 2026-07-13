
from pathlib import Path

from vault.recovery_commit_final_go_no_go_review_layer_service import (
    CURRENT_DECISION,
    DOCTRINE,
    LOCKS,
    get_commit_dry_run_evidence_review_intake_board,
    get_final_commit_preconditions_revalidation_board,
    get_final_go_no_go_review_readiness_checkpoint,
    get_final_go_no_go_safety_blocker_board,
    get_owner_admin_approval_decision_review_board,
    get_recovery_commit_final_go_no_go_review_home,
    get_scope_freeze_commit_window_review_board,
    get_tower_final_go_no_go_decision_draft_board,
    get_tower_final_go_no_go_review_receipt_draft_ledger,
    get_write_barrier_rollback_readiness_review_board,
    validate_recovery_commit_final_go_no_go_review_layer,
)


def test_gp581_590_validation_passes():
    result = (
        validate_recovery_commit_final_go_no_go_review_layer()
    )

    assert result["ok"] is True
    assert result["ready"] is True
    assert result["current_decision"] == (
        "NO_GO_HOLD_PENDING_APPROVALS_AND_ACTIVATION"
    )


def test_gp581_doctrine_is_final_review_only():
    home = (
        get_recovery_commit_final_go_no_go_review_home()
    )

    assert home["ready"] is True
    assert DOCTRINE["tower"] == "face_protocol_authority"
    assert DOCTRINE["teller"] == "workflow_request_source"
    assert DOCTRINE["vault"] == "sealed_memory"
    assert DOCTRINE["correct_flow"] == (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    )
    assert DOCTRINE[
        "tower_is_only_final_decision_authority"
    ] is True
    assert DOCTRINE["final_review_layer_only"] is True
    assert DOCTRINE["decision_draft_only"] is True
    assert DOCTRINE["current_decision"] == (
        CURRENT_DECISION
    )
    assert DOCTRINE["go_decision_granted"] is False
    assert DOCTRINE["no_go_hold_required"] is True
    assert DOCTRINE[
        "live_authorization_granted"
    ] is False
    assert DOCTRINE[
        "authorization_token_issued"
    ] is False
    assert DOCTRINE["commit_command_issued"] is False
    assert DOCTRINE[
        "actual_restore_execution_allowed"
    ] is False
    assert DOCTRINE[
        "production_recovery_write_allowed"
    ] is False
    assert DOCTRINE[
        "teller_can_call_vault_directly"
    ] is False


def test_gp582_dry_run_evidence_is_verified():
    board = (
        get_commit_dry_run_evidence_review_intake_board()
    )

    assert board["ready"] is True
    assert board["intake_count"] >= 1
    assert board[
        "all_dry_run_intakes_verified"
    ] is True
    assert board["all_preconditions_verified"] is True
    assert board["all_sandboxes_verified"] is True
    assert board[
        "all_command_simulations_verified"
    ] is True
    assert board[
        "all_barrier_simulations_verified"
    ] is True
    assert board[
        "all_outcome_previews_verified"
    ] is True
    assert board[
        "all_dry_run_receipts_verified"
    ] is True
    assert board[
        "all_eligible_for_final_review"
    ] is True
    assert board[
        "no_live_authorization_granted"
    ] is True
    assert board[
        "all_commit_points_closed"
    ] is True


def test_gp583_preconditions_are_revalidated_but_go_is_not_met():
    board = (
        get_final_commit_preconditions_revalidation_board()
    )

    assert board["ready"] is True
    assert board["revalidation_count"] >= 1
    assert board["all_evidence_complete"] is True
    assert board[
        "all_tower_authority_reconfirmed"
    ] is True
    assert board["all_exact_scopes_bound"] is True
    assert board[
        "all_one_time_windows_required"
    ] is True
    assert board[
        "all_approval_requirements_present"
    ] is True
    assert board[
        "all_approval_decisions_pending"
    ] is True
    assert board[
        "all_scope_freezes_inactive"
    ] is True
    assert board[
        "all_commit_windows_inactive"
    ] is True
    assert board[
        "all_execution_windows_closed"
    ] is True
    assert board["all_commit_points_closed"] is True
    assert board[
        "no_go_criteria_currently_met"
    ] is True
    assert board[
        "all_revalidation_hashes_present"
    ] is True


def test_gp584_approval_gate_requires_no_go_hold():
    board = (
        get_owner_admin_approval_decision_review_board()
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
        "all_second_authority_review_required"
    ] is True
    assert board[
        "no_owner_admin_approval_granted"
    ] is True
    assert board["no_step_up_satisfied"] is True
    assert board[
        "no_dual_receipt_satisfied"
    ] is True
    assert board[
        "no_second_authority_granted"
    ] is True
    assert board[
        "no_approval_gates_complete"
    ] is True
    assert board[
        "all_no_go_holds_required"
    ] is True
    assert board[
        "all_review_hashes_present"
    ] is True


def test_gp585_scope_and_window_are_valid_but_inactive():
    board = (
        get_scope_freeze_commit_window_review_board()
    )

    assert board["ready"] is True
    assert board["review_count"] >= 1
    assert board["all_exact_scopes_bound"] is True
    assert board[
        "all_one_time_windows_required"
    ] is True
    assert board[
        "all_scope_freeze_activation_required"
    ] is True
    assert board[
        "all_commit_window_activation_required"
    ] is True
    assert board[
        "no_scope_freezes_activated"
    ] is True
    assert board[
        "no_commit_windows_activated"
    ] is True
    assert board["no_execution_windows_open"] is True
    assert board["no_commit_points_open"] is True
    assert board[
        "no_production_targets_allowed"
    ] is True
    assert board[
        "no_external_providers_allowed"
    ] is True
    assert board[
        "all_ready_for_activation_review"
    ] is True
    assert board[
        "all_review_hashes_present"
    ] is True


def test_gp586_barriers_and_rollback_are_ready():
    board = (
        get_write_barrier_rollback_readiness_review_board()
    )

    assert board["ready"] is True
    assert board["review_count"] >= 1
    assert board[
        "all_command_sequences_simulated"
    ] is True
    assert board["no_real_commit_commands"] is True
    assert board["no_actual_restores"] is True
    assert board["no_production_writes"] is True
    assert board["no_final_index_writes"] is True
    assert board["no_pack_overwrites"] is True
    assert board["no_sealed_bytes_writes"] is True
    assert board["no_package_materialization"] is True
    assert board[
        "all_write_barriers_engaged"
    ] is True
    assert board["all_abort_on_mismatch"] is True
    assert board[
        "all_rollback_on_mutation"
    ] is True
    assert board[
        "all_expected_integrity_matches"
    ] is True
    assert board["no_actual_mutations"] is True
    assert board[
        "all_readiness_hashes_present"
    ] is True


def test_gp587_decision_is_no_go_hold():
    board = (
        get_tower_final_go_no_go_decision_draft_board()
    )

    assert board["ready"] is True
    assert board["decision_count"] >= 1
    assert board["current_decision"] == (
        "NO_GO_HOLD_PENDING_APPROVALS_AND_ACTIVATION"
    )
    assert board[
        "all_evidence_reviews_complete"
    ] is True
    assert board[
        "all_precondition_reviews_complete"
    ] is True
    assert board[
        "all_barrier_reviews_complete"
    ] is True
    assert board[
        "all_eligible_for_owner_decision_review"
    ] is True
    assert board[
        "all_technical_dry_runs_passed"
    ] is True
    assert board[
        "no_approval_gates_complete"
    ] is True
    assert board[
        "no_activation_gates_complete"
    ] is True
    assert board[
        "all_decisions_are_no_go_hold"
    ] is True
    assert board[
        "no_live_authorization_granted"
    ] is True
    assert board["no_tokens_issued"] is True
    assert board[
        "no_commit_commands_issued"
    ] is True
    assert board[
        "no_restore_or_write_allowed"
    ] is True
    assert board[
        "all_decision_hashes_present"
    ] is True


def test_gp588_receipts_record_no_go_hold_only():
    ledger = (
        get_tower_final_go_no_go_review_receipt_draft_ledger()
    )

    assert ledger["ready"] is True
    assert ledger["receipt_count"] >= 1
    assert ledger["all_tower_controlled"] is True
    assert ledger[
        "all_review_components_recorded"
    ] is True
    assert ledger[
        "all_no_go_holds_recorded"
    ] is True
    assert ledger[
        "no_go_decisions_recorded"
    ] is True
    assert ledger[
        "no_authorization_or_token_recorded"
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


def test_gp589_all_dangerous_actions_are_blocked():
    board = get_final_go_no_go_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board[
        "all_dangerous_actions_blocked"
    ] is True


def test_gp590_readiness_passes_and_corridor_continues():
    checkpoint = (
        get_final_go_no_go_review_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True
    assert all(
        checkpoint["checks"].values()
    )
    assert checkpoint["current_decision"] == (
        "NO_GO_HOLD_PENDING_APPROVALS_AND_ACTIVATION"
    )
    assert checkpoint["decision_status"] == (
        "technical_dry_run_passed_"
        "final_no_go_hold_correctly_applied"
    )
    assert checkpoint["corridor_continues"] is True
    assert checkpoint[
        "operational_readiness_gate_reached"
    ] is False
    assert (
        "RECOVERY COMMIT OWNER DECISION PREPARATION"
        in checkpoint["next_recommended_layer"]
    )


def test_gp581_590_global_locks_remain_closed():
    assert LOCKS["go_decision_granted"] is False
    assert LOCKS[
        "live_recovery_authorization_granted"
    ] is False
    assert LOCKS[
        "authorization_token_issued"
    ] is False
    assert LOCKS[
        "recovery_capability_token_issued"
    ] is False
    assert LOCKS[
        "recovery_bypass_token_issued"
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
    assert LOCKS["real_commit_attempted"] is False
    assert LOCKS[
        "actual_restore_execution_allowed"
    ] is False
    assert LOCKS[
        "production_recovery_write_allowed"
    ] is False
    assert LOCKS[
        "final_rebuilt_index_write_allowed"
    ] is False
    assert LOCKS[
        "final_pack_overwrite_allowed"
    ] is False
    assert LOCKS[
        "sealed_pack_bytes_write_allowed"
    ] is False
    assert LOCKS[
        "backup_package_materialization_allowed"
    ] is False
    assert LOCKS["production_mount_allowed"] is False
    assert LOCKS["writable_mount_allowed"] is False
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


def test_gp581_590_routes_are_json_only():
    app_text = Path("web/app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_routes = [
        "/vault/recovery-commit-final-go-no-go-review-layer.json",
        "/vault/recovery-commit-final-go-no-go-review-shell.json",
        "/vault/commit-dry-run-evidence-review-intake-board.json",
        "/vault/final-commit-preconditions-revalidation-board.json",
        "/vault/owner-admin-approval-decision-review-board.json",
        "/vault/scope-freeze-commit-window-review-board.json",
        "/vault/write-barrier-rollback-readiness-review-board.json",
        "/vault/tower-final-go-no-go-decision-draft-board.json",
        "/vault/tower-final-go-no-go-review-receipt-draft-ledger.json",
        "/vault/final-go-no-go-safety-blocker-board.json",
        "/vault/final-go-no-go-review-readiness.json",
        "/vault/gp581-status.json",
        "/vault/gp590-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert (
        '@app.route("/vault/recovery-commit-'
        'final-go-no-go-review-layer")'
        not in app_text
    )
