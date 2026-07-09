
from pathlib import Path

from vault.controlled_recovery_commit_execution_dry_run_layer_service import (
    DOCTRINE,
    LOCKS,
    get_commit_outcome_diff_integrity_preview_board,
    get_controlled_commit_dry_run_safety_blocker_board,
    get_controlled_recovery_commit_dry_run_readiness_checkpoint,
    get_controlled_recovery_commit_execution_dry_run_home,
    get_isolated_commit_execution_sandbox_board,
    get_recovery_commit_closeout_intake_board,
    get_recovery_commit_command_simulation_queue,
    get_recovery_commit_preconditions_verification_board,
    get_recovery_write_barrier_rollback_simulation_board,
    get_tower_recovery_commit_dry_run_receipt_draft_ledger,
    validate_controlled_recovery_commit_execution_dry_run_layer,
)


def test_gp571_580_validation_passes():
    result = (
        validate_controlled_recovery_commit_execution_dry_run_layer()
    )

    assert result["ok"] is True
    assert result["ready"] is True


def test_gp571_doctrine_is_dry_run_only():
    home = (
        get_controlled_recovery_commit_execution_dry_run_home()
    )

    assert home["ready"] is True
    assert DOCTRINE["tower"] == "face_protocol_authority"
    assert DOCTRINE["teller"] == "workflow_request_source"
    assert DOCTRINE["vault"] == "sealed_memory"
    assert DOCTRINE["correct_flow"] == (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    )
    assert DOCTRINE[
        "tower_is_only_recovery_commit_authority"
    ] is True
    assert DOCTRINE[
        "commit_execution_dry_run_only"
    ] is True
    assert DOCTRINE["hash_only_simulation"] is True
    assert DOCTRINE["isolated_sandbox_required"] is True
    assert DOCTRINE["write_barriers_required"] is True
    assert DOCTRINE[
        "rollback_simulation_required"
    ] is True
    assert DOCTRINE["commit_point_closed"] is True
    assert DOCTRINE[
        "live_authorization_granted"
    ] is False
    assert DOCTRINE[
        "authorization_token_issued"
    ] is False
    assert DOCTRINE[
        "scope_freeze_activated"
    ] is False
    assert DOCTRINE[
        "commit_window_activated"
    ] is False
    assert DOCTRINE["execution_window_open"] is False
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


def test_gp572_closeout_intakes_are_verified():
    board = get_recovery_commit_closeout_intake_board()

    assert board["ready"] is True
    assert board["intake_count"] >= 1
    assert board[
        "all_closeout_evidence_verified"
    ] is True
    assert board[
        "all_tower_authority_verified"
    ] is True
    assert board[
        "all_approval_requirements_verified"
    ] is True
    assert board[
        "all_scope_freezes_verified"
    ] is True
    assert board[
        "all_commit_windows_verified"
    ] is True
    assert board[
        "all_closeout_drafts_verified"
    ] is True
    assert board[
        "all_closeout_receipts_verified"
    ] is True
    assert board[
        "all_eligible_for_commit_dry_run"
    ] is True
    assert board[
        "no_live_authorization_granted"
    ] is True
    assert board[
        "all_commit_points_closed"
    ] is True


def test_gp573_preconditions_are_verified_but_pending():
    board = (
        get_recovery_commit_preconditions_verification_board()
    )

    assert board["ready"] is True
    assert board["precondition_count"] >= 1
    assert board[
        "all_evidence_closeouts_complete"
    ] is True
    assert board[
        "all_tower_authority_reconfirmed"
    ] is True
    assert board[
        "all_approval_requirements_present"
    ] is True
    assert board[
        "all_approval_decisions_pending"
    ] is True
    assert board["all_exact_scopes_bound"] is True
    assert board[
        "all_one_time_windows_required"
    ] is True
    assert board[
        "all_scope_freezes_inactive"
    ] is True
    assert board[
        "all_commit_windows_inactive"
    ] is True
    assert board[
        "all_commit_points_closed"
    ] is True
    assert board[
        "all_precondition_hashes_present"
    ] is True


def test_gp574_sandboxes_are_isolated_hash_only():
    board = (
        get_isolated_commit_execution_sandbox_board()
    )

    assert board["ready"] is True
    assert board["sandbox_count"] >= 1
    assert board["all_isolated"] is True
    assert board["all_ephemeral"] is True
    assert board["all_hash_only"] is True
    assert board["no_production_mount"] is True
    assert board["no_writable_mount"] is True
    assert board["no_network_egress"] is True
    assert board[
        "no_external_provider_connection"
    ] is True
    assert board[
        "no_raw_bytes_materialized"
    ] is True
    assert board["no_raw_paths_exposed"] is True
    assert board[
        "all_sandbox_hashes_present"
    ] is True


def test_gp575_commit_commands_are_simulated_only():
    board = (
        get_recovery_commit_command_simulation_queue()
    )

    assert board["ready"] is True
    assert board["simulation_count"] >= 1
    assert board["all_sequences_complete"] is True
    assert board[
        "all_commit_commands_simulated"
    ] is True
    assert board["no_real_commit_commands"] is True
    assert board["no_actual_restores"] is True
    assert board["no_production_writes"] is True
    assert board["no_final_index_writes"] is True
    assert board["no_pack_overwrites"] is True
    assert board["no_sealed_bytes_writes"] is True
    assert board["no_package_materialization"] is True
    assert board[
        "all_command_hashes_present"
    ] is True


def test_gp576_write_barriers_and_rollback_are_simulated():
    board = (
        get_recovery_write_barrier_rollback_simulation_board()
    )

    assert board["ready"] is True
    assert board["simulation_count"] >= 1
    assert board[
        "all_write_barriers_engaged"
    ] is True
    assert board["all_abort_on_mismatch"] is True
    assert board[
        "all_rollback_on_mutation"
    ] is True
    assert board[
        "all_abort_simulations_present"
    ] is True
    assert board[
        "all_rollback_simulations_present"
    ] is True
    assert board["no_actual_aborts"] is True
    assert board["no_actual_rollbacks"] is True
    assert board[
        "all_barrier_hashes_present"
    ] is True


def test_gp577_outcomes_are_hash_only_and_clean():
    board = (
        get_commit_outcome_diff_integrity_preview_board()
    )

    assert board["ready"] is True
    assert board["preview_count"] >= 1
    assert board["all_hashes_present"] is True
    assert board[
        "all_expected_integrity_matches"
    ] is True
    assert board["no_actual_mutations"] is True
    assert board["no_production_diffs"] is True
    assert board["no_raw_bytes"] is True
    assert board["no_raw_paths"] is True
    assert board["no_raw_tokens"] is True
    assert board["no_public_links"] is True


def test_gp578_receipts_are_tower_controlled_drafts():
    ledger = (
        get_tower_recovery_commit_dry_run_receipt_draft_ledger()
    )

    assert ledger["ready"] is True
    assert ledger["receipt_count"] >= 1
    assert ledger["all_tower_controlled"] is True
    assert ledger[
        "all_dry_run_components_recorded"
    ] is True
    assert ledger[
        "no_live_authorization_or_token_recorded"
    ] is True
    assert ledger[
        "no_real_commit_restore_or_write_recorded"
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


def test_gp579_all_dangerous_actions_are_blocked():
    board = (
        get_controlled_commit_dry_run_safety_blocker_board()
    )

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board[
        "all_dangerous_actions_blocked"
    ] is True


def test_gp580_readiness_passes():
    checkpoint = (
        get_controlled_recovery_commit_dry_run_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True
    assert all(
        checkpoint["checks"].values()
    )
    assert checkpoint["dry_run_status"] == (
        "commit_execution_sequence_simulated_"
        "all_write_barriers_engaged_"
        "real_commit_closed"
    )
    assert (
        "RECOVERY COMMIT FINAL GO-NO-GO REVIEW"
        in checkpoint["next_recommended_layer"]
    )


def test_gp571_580_global_locks_remain_closed():
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
        "scope_freeze_activated"
    ] is False
    assert LOCKS[
        "commit_window_activated"
    ] is False
    assert LOCKS[
        "execution_window_open"
    ] is False
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
    assert LOCKS["network_egress_allowed"] is False
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
        "direct_vault_user_portal_allowed"
    ] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS[
        "quarantine_release_allowed"
    ] is False
    assert LOCKS[
        "physical_object_move_allowed"
    ] is False


def test_gp571_580_routes_are_json_only():
    app_text = Path("web/app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_routes = [
        "/vault/controlled-recovery-commit-execution-dry-run-layer.json",
        "/vault/controlled-recovery-commit-execution-dry-run-shell.json",
        "/vault/recovery-commit-closeout-intake-board.json",
        "/vault/recovery-commit-preconditions-verification-board.json",
        "/vault/isolated-commit-execution-sandbox-board.json",
        "/vault/recovery-commit-command-simulation-queue.json",
        "/vault/recovery-write-barrier-rollback-simulation-board.json",
        "/vault/commit-outcome-diff-integrity-preview-board.json",
        "/vault/tower-recovery-commit-dry-run-receipt-draft-ledger.json",
        "/vault/controlled-commit-dry-run-safety-blocker-board.json",
        "/vault/controlled-recovery-commit-dry-run-readiness.json",
        "/vault/gp571-status.json",
        "/vault/gp580-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert (
        '@app.route("/vault/controlled-recovery-'
        'commit-execution-dry-run-layer")'
        not in app_text
    )
