
from pathlib import Path

from vault.tower_recovery_execution_authorization_gate_layer_service import (
    DOCTRINE,
    LOCKS,
    get_one_time_recovery_authorization_draft_board,
    get_owner_admin_step_up_dual_approval_gate,
    get_recovery_authorization_intake_board,
    get_recovery_authorization_safety_blocker_board,
    get_recovery_evidence_receipt_prerequisite_board,
    get_recovery_execution_authorization_gate_readiness_checkpoint,
    get_recovery_execution_scope_allowlist_board,
    get_tower_recovery_authority_gate,
    get_tower_recovery_authorization_receipt_draft_ledger,
    get_tower_recovery_execution_authorization_gate_home,
    validate_tower_recovery_execution_authorization_gate_layer,
)


def test_gp541_550_validation_passes():
    result = (
        validate_tower_recovery_execution_authorization_gate_layer()
    )

    assert result["ok"] is True
    assert result["ready"] is True


def test_gp541_550_doctrine_is_tower_only_and_draft_only():
    home = (
        get_tower_recovery_execution_authorization_gate_home()
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
    assert DOCTRINE["authorization_gate_only"] is True
    assert DOCTRINE["authorization_drafts_only"] is True
    assert DOCTRINE[
        "live_recovery_authorization_granted"
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


def test_gp542_intakes_are_review_only():
    board = get_recovery_authorization_intake_board()

    assert board["ready"] is True
    assert board["intake_count"] >= 1
    assert board["all_restore_drills_verified"] is True
    assert board["all_evidence_verified"] is True
    assert board["all_guards_verified"] is True
    assert board["all_receipts_verified"] is True
    assert board["all_eligible_for_review"] is True
    assert board["no_live_authorization_granted"] is True
    assert board["no_actual_restore_allowed"] is True


def test_gp543_authority_is_tower_only():
    board = get_tower_recovery_authority_gate()

    assert board["ready"] is True
    assert board["gate_count"] >= 1
    assert board["all_requesters_are_tower"] is True
    assert board[
        "all_identity_contracts_verified"
    ] is True
    assert board[
        "all_permission_contracts_verified"
    ] is True
    assert board[
        "all_clearance_contracts_verified"
    ] is True
    assert board[
        "all_least_privilege_contracts_verified"
    ] is True
    assert board[
        "all_vault_answers_target_tower"
    ] is True
    assert board["no_teller_authorization"] is True
    assert board[
        "no_direct_vault_user_access"
    ] is True


def test_gp544_approvals_remain_pending():
    board = (
        get_owner_admin_step_up_dual_approval_gate()
    )

    assert board["ready"] is True
    assert board["gate_count"] >= 1
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
        "no_owner_approval_granted"
    ] is True
    assert board["no_step_up_satisfied"] is True
    assert board[
        "no_second_authority_granted"
    ] is True
    assert board[
        "no_live_authorization_allowed"
    ] is True


def test_gp545_evidence_is_hash_only():
    board = (
        get_recovery_evidence_receipt_prerequisite_board()
    )

    assert board["ready"] is True
    assert board["prerequisite_count"] >= 1
    assert board["all_hashes_present"] is True
    assert board["all_evidence_verified"] is True
    assert board["no_raw_bytes"] is True
    assert board["no_raw_paths"] is True
    assert board["no_raw_tokens"] is True
    assert board["no_public_links"] is True


def test_gp546_scopes_exclude_production_mutation():
    board = (
        get_recovery_execution_scope_allowlist_board()
    )

    assert board["ready"] is True
    assert board["scope_count"] >= 1
    assert board["all_safe_scopes_allowed"] is True
    assert board["no_production_target"] is True
    assert board["no_final_index_write"] is True
    assert board["no_pack_overwrite"] is True
    assert board["no_sealed_bytes_write"] is True
    assert board["no_delete_purge"] is True
    assert board["no_quarantine_release"] is True
    assert board["no_physical_move"] is True
    assert board["no_external_provider"] is True
    assert board["all_scope_hashes_present"] is True


def test_gp547_authorizations_are_pending_drafts():
    board = (
        get_one_time_recovery_authorization_draft_board()
    )

    assert board["ready"] is True
    assert board["draft_count"] >= 1
    assert board["all_one_time_use_required"] is True
    assert board["all_request_bound"] is True
    assert board["all_scope_bound"] is True
    assert board["all_expiry_required"] is True
    assert board["all_approvals_pending"] is True
    assert board["no_authorization_granted"] is True
    assert board[
        "no_authorization_token_issued"
    ] is True
    assert board[
        "no_restore_or_writes_allowed"
    ] is True
    assert board[
        "all_draft_hashes_present"
    ] is True


def test_gp548_receipts_are_tower_controlled_drafts():
    ledger = (
        get_tower_recovery_authorization_receipt_draft_ledger()
    )

    assert ledger["ready"] is True
    assert ledger["receipt_count"] >= 1
    assert ledger["all_tower_controlled"] is True
    assert ledger["no_approvals_recorded"] is True
    assert ledger[
        "no_authorization_or_token_recorded"
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


def test_gp549_all_unsafe_actions_are_blocked():
    board = (
        get_recovery_authorization_safety_blocker_board()
    )

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board[
        "all_dangerous_actions_blocked"
    ] is True


def test_gp550_readiness_declares_staging_next():
    checkpoint = (
        get_recovery_execution_authorization_gate_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True
    assert all(
        checkpoint["checks"].values()
    )
    assert checkpoint["authorization_status"] == (
        "authorization_drafts_ready_"
        "live_authorization_not_granted"
    )
    assert (
        "CONTROLLED RECOVERY EXECUTION STAGING"
        in checkpoint["next_recommended_layer"]
    )


def test_gp541_550_global_locks_remain_closed():
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
    assert LOCKS[
        "external_provider_restore_allowed"
    ] is False
    assert LOCKS[
        "raw_file_bytes_returned_by_json"
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


def test_gp541_550_routes_are_json_only():
    app_text = Path("web/app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_routes = [
        (
            "/vault/tower-recovery-execution-"
            "authorization-gate-layer.json"
        ),
        (
            "/vault/tower-recovery-execution-"
            "authorization-gate-shell.json"
        ),
        (
            "/vault/recovery-authorization-"
            "intake-board.json"
        ),
        "/vault/tower-recovery-authority-gate.json",
        (
            "/vault/owner-admin-step-up-"
            "dual-approval-gate.json"
        ),
        (
            "/vault/recovery-evidence-receipt-"
            "prerequisite-board.json"
        ),
        (
            "/vault/recovery-execution-"
            "scope-allowlist-board.json"
        ),
        (
            "/vault/one-time-recovery-"
            "authorization-draft-board.json"
        ),
        (
            "/vault/tower-recovery-authorization-"
            "receipt-draft-ledger.json"
        ),
        (
            "/vault/recovery-authorization-"
            "safety-blocker-board.json"
        ),
        (
            "/vault/recovery-execution-authorization-"
            "gate-readiness-checkpoint.json"
        ),
        "/vault/gp541-status.json",
        "/vault/gp550-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert (
        '@app.route("/vault/tower-recovery-'
        'execution-authorization-gate-layer")'
        not in app_text
    )
