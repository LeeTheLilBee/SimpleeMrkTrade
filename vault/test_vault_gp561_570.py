
from pathlib import Path

from vault.recovery_commit_authorization_closeout_layer_service import (
    DOCTRINE,
    LOCKS,
    get_one_time_commit_authorization_closeout_draft_board,
    get_owner_admin_step_up_dual_receipt_closeout_board,
    get_recovery_commit_authorization_closeout_home,
    get_recovery_commit_authorization_closeout_readiness_checkpoint,
    get_recovery_commit_authorization_closeout_safety_blocker_board,
    get_recovery_commit_scope_freeze_board,
    get_recovery_commit_window_draft_board,
    get_recovery_staging_evidence_closeout_intake_board,
    get_tower_recovery_commit_authority_reconfirmation_board,
    get_tower_recovery_commit_authorization_receipt_draft_ledger,
    validate_recovery_commit_authorization_closeout_layer,
)


def test_gp561_570_validation_passes():
    result = (
        validate_recovery_commit_authorization_closeout_layer()
    )

    assert result["ok"] is True
    assert result["ready"] is True


def test_gp561_doctrine_is_closeout_draft_only():
    home = (
        get_recovery_commit_authorization_closeout_home()
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
        "authorization_closeout_drafts_only"
    ] is True
    assert DOCTRINE[
        "scope_freeze_drafts_only"
    ] is True
    assert DOCTRINE[
        "commit_window_drafts_only"
    ] is True
    assert DOCTRINE["commit_point_closed"] is True
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


def test_gp562_staging_evidence_is_closed():
    board = (
        get_recovery_staging_evidence_closeout_intake_board()
    )

    assert board["ready"] is True
    assert board["intake_count"] >= 1
    assert board[
        "all_staging_intakes_verified"
    ] is True
    assert board[
        "all_environments_verified"
    ] is True
    assert board[
        "all_action_plans_verified"
    ] is True
    assert board[
        "all_simulations_verified"
    ] is True
    assert board[
        "all_diff_previews_verified"
    ] is True
    assert board[
        "all_commit_locks_verified"
    ] is True
    assert board[
        "all_staging_receipts_verified"
    ] is True
    assert board[
        "all_eligible_for_closeout_draft"
    ] is True
    assert board[
        "no_live_authorization_granted"
    ] is True
    assert board[
        "all_commit_points_closed"
    ] is True


def test_gp563_tower_authority_is_reconfirmed():
    board = (
        get_tower_recovery_commit_authority_reconfirmation_board()
    )

    assert board["ready"] is True
    assert board["reconfirmation_count"] >= 1
    assert board["all_requesters_are_tower"] is True
    assert board[
        "all_identity_reconfirmed"
    ] is True
    assert board[
        "all_permissions_reconfirmed"
    ] is True
    assert board[
        "all_clearances_reconfirmed"
    ] is True
    assert board[
        "all_least_privilege_reconfirmed"
    ] is True
    assert board[
        "all_vault_answers_target_tower"
    ] is True
    assert board["no_teller_authority"] is True
    assert board[
        "no_direct_vault_user_access"
    ] is True
    assert board[
        "all_reconfirmation_hashes_present"
    ] is True


def test_gp564_approval_requirements_are_packaged_but_pending():
    board = (
        get_owner_admin_step_up_dual_receipt_closeout_board()
    )

    assert board["ready"] is True
    assert board["closeout_count"] >= 1
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
        "all_requirements_packaged"
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
        "no_live_authorization_allowed"
    ] is True
    assert board[
        "all_approval_hashes_present"
    ] is True


def test_gp565_scope_freezes_are_exact_and_inactive():
    board = get_recovery_commit_scope_freeze_board()

    assert board["ready"] is True
    assert board["scope_freeze_count"] >= 1
    assert board[
        "all_source_hashes_present"
    ] is True
    assert board["all_request_bound"] is True
    assert board["all_environment_bound"] is True
    assert board["all_action_plan_bound"] is True
    assert board["all_mutation_diff_bound"] is True
    assert board["no_scope_expansion"] is True
    assert board["no_production_target"] is True
    assert board["no_external_provider"] is True
    assert board[
        "no_scope_freeze_activated"
    ] is True


def test_gp566_commit_windows_are_drafts_only():
    board = get_recovery_commit_window_draft_board()

    assert board["ready"] is True
    assert board["window_count"] >= 1
    assert board[
        "all_one_time_windows_required"
    ] is True
    assert board["all_request_bound"] is True
    assert board["all_scope_bound"] is True
    assert board["all_authority_bound"] is True
    assert board["all_expiry_required"] is True
    assert board[
        "all_activation_requirements_present"
    ] is True
    assert board["no_windows_activated"] is True
    assert board[
        "no_execution_windows_open"
    ] is True
    assert board["no_commit_points_open"] is True
    assert board[
        "all_window_hashes_present"
    ] is True


def test_gp567_closeout_drafts_are_complete_but_not_granted():
    board = (
        get_one_time_commit_authorization_closeout_draft_board()
    )

    assert board["ready"] is True
    assert board["draft_count"] >= 1
    assert board[
        "all_evidence_closeouts_complete"
    ] is True
    assert board[
        "all_authority_reconfirmations_complete"
    ] is True
    assert board[
        "all_approval_requirements_packaged"
    ] is True
    assert board[
        "all_scope_freeze_drafts_complete"
    ] is True
    assert board[
        "all_commit_window_drafts_complete"
    ] is True
    assert board[
        "all_one_time_authorization_required"
    ] is True
    assert board["no_authorization_granted"] is True
    assert board[
        "no_authorization_tokens_issued"
    ] is True
    assert board[
        "no_commit_commands_issued"
    ] is True
    assert board[
        "no_restore_or_write_allowed"
    ] is True
    assert board[
        "all_closeout_hashes_present"
    ] is True


def test_gp568_receipts_are_append_only_drafts():
    ledger = (
        get_tower_recovery_commit_authorization_receipt_draft_ledger()
    )

    assert ledger["ready"] is True
    assert ledger["receipt_count"] >= 1
    assert ledger["all_tower_controlled"] is True
    assert ledger[
        "all_closeout_components_recorded"
    ] is True
    assert ledger[
        "no_live_authorization_or_token_recorded"
    ] is True
    assert ledger[
        "no_commit_or_execution_recorded"
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


def test_gp569_all_dangerous_actions_are_blocked():
    board = (
        get_recovery_commit_authorization_closeout_safety_blocker_board()
    )

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board[
        "all_dangerous_actions_blocked"
    ] is True


def test_gp570_readiness_passes():
    checkpoint = (
        get_recovery_commit_authorization_closeout_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True
    assert all(
        checkpoint["checks"].values()
    )
    assert checkpoint["closeout_status"] == (
        "commit_authorization_closeout_drafts_ready_"
        "commit_point_closed"
    )
    assert (
        "CONTROLLED RECOVERY COMMIT EXECUTION DRY-RUN"
        in checkpoint["next_recommended_layer"]
    )


def test_gp561_570_global_locks_remain_closed():
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
    assert LOCKS[
        "owner_admin_approval_granted"
    ] is False
    assert LOCKS["step_up_satisfied"] is False
    assert LOCKS["dual_receipt_satisfied"] is False
    assert LOCKS[
        "second_authority_review_granted"
    ] is False
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


def test_gp561_570_routes_are_json_only():
    app_text = Path("web/app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_routes = [
        "/vault/recovery-commit-authorization-closeout-layer.json",
        "/vault/recovery-commit-authorization-closeout-shell.json",
        "/vault/recovery-staging-evidence-closeout-intake-board.json",
        "/vault/tower-recovery-commit-authority-reconfirmation-board.json",
        "/vault/owner-admin-step-up-dual-receipt-closeout-board.json",
        "/vault/recovery-commit-scope-freeze-board.json",
        "/vault/recovery-commit-window-draft-board.json",
        "/vault/one-time-commit-authorization-closeout-draft-board.json",
        (
            "/vault/tower-recovery-commit-authorization-"
            "receipt-draft-ledger.json"
        ),
        (
            "/vault/recovery-commit-authorization-closeout-"
            "safety-blocker-board.json"
        ),
        "/vault/recovery-commit-authorization-closeout-readiness.json",
        "/vault/gp561-status.json",
        "/vault/gp570-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert (
        '@app.route("/vault/recovery-commit-'
        'authorization-closeout-layer")'
        not in app_text
    )
