
from pathlib import Path

from vault.recovery_commit_owner_decision_preparation_layer_service import (
    CURRENT_RECOMMENDATION,
    DOCTRINE,
    LOCKS,
    get_final_go_no_go_review_intake_board,
    get_owner_admin_control_decision_packet_board,
    get_owner_decision_criteria_matrix,
    get_owner_decision_preparation_readiness_checkpoint,
    get_owner_decision_preparation_safety_blocker_board,
    get_recovery_commit_owner_decision_preparation_home,
    get_recovery_decision_alternatives_rationale_board,
    get_scope_freeze_commit_window_activation_plan_draft_board,
    get_tower_owner_decision_receipt_draft_ledger,
    get_tower_owner_decision_record_draft_board,
    validate_recovery_commit_owner_decision_preparation_layer,
)


def test_gp591_600_validation_passes():
    result = (
        validate_recovery_commit_owner_decision_preparation_layer()
    )

    assert result["ok"] is True
    assert result["ready"] is True
    assert result["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )


def test_gp591_doctrine_is_preparation_only():
    home = (
        get_recovery_commit_owner_decision_preparation_home()
    )

    assert home["ready"] is True
    assert DOCTRINE["tower"] == "face_protocol_authority"
    assert DOCTRINE["teller"] == "workflow_request_source"
    assert DOCTRINE["vault"] == "sealed_memory"
    assert DOCTRINE["correct_flow"] == (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    )
    assert DOCTRINE[
        "owner_decision_preparation_only"
    ] is True
    assert DOCTRINE[
        "technical_readiness_is_not_authorization"
    ] is True
    assert DOCTRINE[
        "owner_decision_recorded"
    ] is False
    assert DOCTRINE["go_decision_granted"] is False
    assert DOCTRINE[
        "live_authorization_granted"
    ] is False
    assert DOCTRINE[
        "teller_can_call_vault_directly"
    ] is False


def test_gp592_final_review_intake_is_verified():
    board = get_final_go_no_go_review_intake_board()

    assert board["ready"] is True
    assert board["intake_count"] >= 1
    assert board[
        "all_final_reviews_verified"
    ] is True
    assert board[
        "all_technical_dry_runs_verified"
    ] is True
    assert board[
        "all_technical_evidence_complete"
    ] is True
    assert board[
        "all_approval_gates_pending"
    ] is True
    assert board[
        "all_activation_gates_pending"
    ] is True
    assert board[
        "all_no_go_holds_verified"
    ] is True
    assert board[
        "all_eligible_for_preparation"
    ] is True
    assert board[
        "no_owner_decisions_recorded"
    ] is True
    assert board[
        "no_live_authorization_granted"
    ] is True


def test_gp593_criteria_separates_technical_and_go_readiness():
    board = get_owner_decision_criteria_matrix()

    assert board["ready"] is True
    assert board["criteria_count"] >= 1
    assert board[
        "all_technical_readiness_passed"
    ] is True
    assert board[
        "all_evidence_integrity_passed"
    ] is True
    assert board[
        "all_barrier_readiness_passed"
    ] is True
    assert board[
        "no_approval_gates_complete"
    ] is True
    assert board[
        "no_activation_gates_complete"
    ] is True
    assert board["no_go_eligibility"] is True
    assert board[
        "all_no_go_holds_required"
    ] is True
    assert board[
        "no_remediation_required"
    ] is True
    assert board[
        "all_criteria_hashes_present"
    ] is True


def test_gp594_owner_controls_remain_pending():
    board = (
        get_owner_admin_control_decision_packet_board()
    )

    assert board["ready"] is True
    assert board["packet_count"] >= 1
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
        "all_tower_only_presented"
    ] is True
    assert board[
        "no_vault_decision_authority"
    ] is True
    assert board[
        "no_teller_decision_authority"
    ] is True


def test_gp595_activation_plan_is_draft_only():
    board = (
        get_scope_freeze_commit_window_activation_plan_draft_board()
    )

    assert board["ready"] is True
    assert board["plan_count"] >= 1
    assert board["all_exact_scopes_bound"] is True
    assert board[
        "all_one_time_windows_required"
    ] is True
    assert board[
        "all_activation_steps_required"
    ] is True
    assert board["nothing_activated"] is True
    assert board[
        "no_production_targets_allowed"
    ] is True
    assert board[
        "no_external_providers_allowed"
    ] is True
    assert board[
        "all_activation_hashes_present"
    ] is True


def test_gp596_alternatives_keep_go_unavailable():
    board = (
        get_recovery_decision_alternatives_rationale_board()
    )

    assert board["ready"] is True
    assert board["review_count"] >= 1
    assert board[
        "all_have_three_available_options"
    ] is True
    assert board["no_go_option_available"] is True
    assert board[
        "all_no_go_holds_available"
    ] is True
    assert board[
        "all_remediation_available"
    ] is True
    assert board["all_defer_available"] is True
    assert board[
        "all_recommendations_are_no_go_hold"
    ] is True
    assert board[
        "all_rationale_hashes_present"
    ] is True


def test_gp597_owner_decision_record_is_pending():
    board = (
        get_tower_owner_decision_record_draft_board()
    )

    assert board["ready"] is True
    assert board["record_count"] >= 1
    assert board[
        "all_packet_components_complete"
    ] is True
    assert board[
        "all_owner_decisions_pending"
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
        "all_record_hashes_present"
    ] is True


def test_gp598_receipts_are_append_only_drafts():
    ledger = (
        get_tower_owner_decision_receipt_draft_ledger()
    )

    assert ledger["ready"] is True
    assert ledger["receipt_count"] >= 1
    assert ledger["all_tower_controlled"] is True
    assert ledger[
        "all_preparation_components_recorded"
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


def test_gp599_all_dangerous_actions_are_blocked():
    board = (
        get_owner_decision_preparation_safety_blocker_board()
    )

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board[
        "all_dangerous_actions_blocked"
    ] is True


def test_gp600_readiness_passes_and_corridor_continues():
    checkpoint = (
        get_owner_decision_preparation_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True
    assert all(
        checkpoint["checks"].values()
    )
    assert checkpoint["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )
    assert checkpoint["preparation_status"] == (
        "owner_decision_packet_complete_"
        "owner_decision_pending_"
        "all_execution_locks_closed"
    )
    assert checkpoint["corridor_continues"] is True
    assert checkpoint[
        "operational_readiness_gate_reached"
    ] is False
    assert (
        "RECOVERY COMMIT OWNER DECISION REVIEW"
        in checkpoint["next_recommended_layer"]
    )


def test_gp591_600_global_locks_remain_closed():
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


def test_gp591_600_routes_are_json_only():
    app_text = Path("web/app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_routes = [
        "/vault/recovery-commit-owner-decision-preparation-layer.json",
        "/vault/recovery-commit-owner-decision-preparation-shell.json",
        "/vault/final-go-no-go-review-intake-board.json",
        "/vault/owner-decision-criteria-matrix.json",
        "/vault/owner-admin-control-decision-packet-board.json",
        "/vault/scope-freeze-commit-window-activation-plan-draft-board.json",
        "/vault/recovery-decision-alternatives-rationale-board.json",
        "/vault/tower-owner-decision-record-draft-board.json",
        "/vault/tower-owner-decision-receipt-draft-ledger.json",
        "/vault/owner-decision-preparation-safety-blocker-board.json",
        "/vault/owner-decision-preparation-readiness.json",
        "/vault/gp591-status.json",
        "/vault/gp600-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert (
        '@app.route("/vault/recovery-commit-owner-'
        'decision-preparation-layer")'
        not in app_text
    )
