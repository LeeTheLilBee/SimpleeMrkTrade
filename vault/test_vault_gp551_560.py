
from pathlib import Path

from vault.controlled_recovery_execution_staging_layer_service import (
    DOCTRINE,
    LOCKS,
    get_authorized_recovery_staging_intake_board,
    get_controlled_recovery_execution_staging_home,
    get_controlled_recovery_execution_staging_readiness_checkpoint,
    get_controlled_recovery_staging_safety_blocker_board,
    get_isolated_recovery_staging_environment_board,
    get_recovery_action_plan_draft_board,
    get_recovery_commit_point_lock_board,
    get_recovery_mutation_diff_preview_board,
    get_recovery_write_simulation_queue,
    get_tower_recovery_staging_receipt_draft_ledger,
    validate_controlled_recovery_execution_staging_layer,
)


def test_gp551_560_validation_passes():
    result = (
        validate_controlled_recovery_execution_staging_layer()
    )

    assert result["ok"] is True
    assert result["ready"] is True


def test_gp551_doctrine_is_staging_only():
    home = (
        get_controlled_recovery_execution_staging_home()
    )

    assert home["ready"] is True
    assert DOCTRINE["tower"] == "face_protocol_authority"
    assert DOCTRINE["teller"] == "workflow_request_source"
    assert DOCTRINE["vault"] == "sealed_memory"
    assert DOCTRINE["correct_flow"] == (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    )
    assert DOCTRINE[
        "tower_is_only_recovery_authority"
    ] is True
    assert DOCTRINE["staging_design_only"] is True
    assert DOCTRINE["staging_simulation_only"] is True
    assert DOCTRINE["commit_point_closed"] is True
    assert DOCTRINE[
        "live_authorization_granted"
    ] is False
    assert DOCTRINE["authorization_token_issued"] is False
    assert DOCTRINE[
        "actual_restore_execution_allowed"
    ] is False
    assert DOCTRINE[
        "production_recovery_write_allowed"
    ] is False
    assert DOCTRINE[
        "teller_can_call_vault_directly"
    ] is False


def test_gp552_staging_intakes_are_review_only():
    board = (
        get_authorized_recovery_staging_intake_board()
    )

    assert board["ready"] is True
    assert board["intake_count"] >= 1
    assert board[
        "all_authorization_reviews_eligible"
    ] is True
    assert board[
        "all_tower_authority_verified"
    ] is True
    assert board["all_evidence_verified"] is True
    assert board["all_safe_scopes_verified"] is True
    assert board[
        "all_authorizations_still_pending"
    ] is True
    assert board[
        "all_staging_design_allowed"
    ] is True
    assert board["no_live_execution_allowed"] is True
    assert board["no_production_write_allowed"] is True


def test_gp553_environments_are_isolated_hash_only():
    board = (
        get_isolated_recovery_staging_environment_board()
    )

    assert board["ready"] is True
    assert board["environment_count"] >= 1
    assert board["all_isolated"] is True
    assert board["all_hash_only"] is True
    assert board["all_ephemeral"] is True
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
        "all_environment_hashes_present"
    ] is True


def test_gp554_action_plans_are_simulation_only():
    board = get_recovery_action_plan_draft_board()

    assert board["ready"] is True
    assert board["action_plan_count"] >= 1
    assert board["all_action_counts_complete"] is True
    assert board["all_simulation_only"] is True
    assert board["all_abort_on_mismatch"] is True
    assert board[
        "all_rollback_guard_required"
    ] is True
    assert board["no_live_execution_allowed"] is True
    assert board[
        "all_action_plan_hashes_present"
    ] is True


def test_gp555_write_queue_executes_no_writes():
    board = get_recovery_write_simulation_queue()

    assert board["ready"] is True
    assert board["simulation_count"] >= 1
    assert board[
        "all_expected_simulations_present"
    ] is True
    assert board["no_actual_writes"] is True
    assert board["no_production_writes"] is True
    assert board["no_sealed_bytes_writes"] is True
    assert board["no_package_materialization"] is True
    assert board[
        "all_simulation_hashes_present"
    ] is True


def test_gp556_diff_previews_are_hash_only():
    board = (
        get_recovery_mutation_diff_preview_board()
    )

    assert board["ready"] is True
    assert board["diff_preview_count"] >= 1
    assert board[
        "all_expected_hashes_present"
    ] is True
    assert board["no_actual_hashes_recorded"] is True
    assert board["no_actual_mutations"] is True
    assert board[
        "no_production_diff_generated"
    ] is True
    assert board["no_raw_bytes"] is True
    assert board["no_raw_paths"] is True
    assert board["all_diff_hashes_present"] is True


def test_gp557_commit_points_remain_closed():
    board = get_recovery_commit_point_lock_board()

    assert board["ready"] is True
    assert board["commit_lock_count"] >= 1
    assert board[
        "all_commit_points_required"
    ] is True
    assert board["all_commit_points_closed"] is True
    assert board[
        "no_commit_commands_issued"
    ] is True
    assert board[
        "all_authorizations_pending"
    ] is True
    assert board["all_approvals_pending"] is True
    assert board[
        "all_dangerous_writes_locked"
    ] is True
    assert board["all_lock_hashes_present"] is True


def test_gp558_receipts_are_drafts_only():
    ledger = (
        get_tower_recovery_staging_receipt_draft_ledger()
    )

    assert ledger["ready"] is True
    assert ledger["receipt_count"] >= 1
    assert ledger["all_tower_controlled"] is True
    assert ledger[
        "all_staging_and_simulation_recorded"
    ] is True
    assert ledger[
        "no_live_authorization_or_token_recorded"
    ] is True
    assert ledger[
        "no_restore_or_write_recorded"
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


def test_gp559_all_dangerous_actions_are_blocked():
    board = (
        get_controlled_recovery_staging_safety_blocker_board()
    )

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board[
        "all_dangerous_actions_blocked"
    ] is True


def test_gp560_readiness_passes():
    checkpoint = (
        get_controlled_recovery_execution_staging_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True
    assert all(
        checkpoint["checks"].values()
    )
    assert checkpoint["staging_status"] == (
        "isolated_hash_only_staging_ready_"
        "commit_point_closed"
    )
    assert (
        "RECOVERY COMMIT AUTHORIZATION CLOSEOUT"
        in checkpoint["next_recommended_layer"]
    )


def test_gp551_560_global_locks_remain_closed():
    assert LOCKS[
        "live_recovery_authorization_granted"
    ] is False
    assert LOCKS["authorization_token_issued"] is False
    assert LOCKS[
        "recovery_capability_token_issued"
    ] is False
    assert LOCKS[
        "recovery_bypass_token_issued"
    ] is False
    assert LOCKS["commit_point_open"] is False
    assert LOCKS["commit_command_issued"] is False
    assert LOCKS["execution_window_open"] is False
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


def test_gp551_560_routes_are_json_only():
    app_text = Path("web/app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_routes = [
        (
            "/vault/controlled-recovery-execution-"
            "staging-layer.json"
        ),
        (
            "/vault/controlled-recovery-execution-"
            "staging-shell.json"
        ),
        (
            "/vault/authorized-recovery-"
            "staging-intake-board.json"
        ),
        (
            "/vault/isolated-recovery-"
            "staging-environment-board.json"
        ),
        (
            "/vault/recovery-action-plan-"
            "draft-board.json"
        ),
        (
            "/vault/recovery-write-"
            "simulation-queue.json"
        ),
        (
            "/vault/recovery-mutation-"
            "diff-preview-board.json"
        ),
        (
            "/vault/recovery-commit-"
            "point-lock-board.json"
        ),
        (
            "/vault/tower-recovery-staging-"
            "receipt-draft-ledger.json"
        ),
        (
            "/vault/controlled-recovery-staging-"
            "safety-blocker-board.json"
        ),
        (
            "/vault/controlled-recovery-execution-"
            "staging-readiness.json"
        ),
        "/vault/gp551-status.json",
        "/vault/gp560-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert (
        '@app.route("/vault/controlled-recovery-'
        'execution-staging-layer")'
        not in app_text
    )
