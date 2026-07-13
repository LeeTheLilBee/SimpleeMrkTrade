
from pathlib import Path

from vault.recovery_commit_owner_decision_recording_closeout_layer_service import (
    ALLOWED_DECISION_VALUES,
    CURRENT_RECOMMENDATION,
    DOCTRINE,
    LOCKS,
    RECORDING_CONTRACT_FIELDS,
    get_approval_dual_receipt_gate_closeout_board,
    get_identity_step_up_prerequisite_closeout_board,
    get_owner_decision_recording_closeout_readiness_checkpoint,
    get_owner_decision_recording_closeout_safety_blocker_board,
    get_owner_decision_recording_closeout_shell,
    get_owner_decision_recording_contract_freeze_board,
    get_recording_gate_evidence_closeout_intake_board,
    get_recovery_commit_owner_decision_recording_closeout_home,
    get_scope_freeze_commit_window_boundary_closeout_board,
    get_tower_owner_decision_recording_closeout_record_draft_board,
    get_tower_recording_closeout_receipt_draft_ledger,
    validate_recovery_commit_owner_decision_recording_closeout_layer,
)


def test_gp621_630_validation_passes():
    result = (
        validate_recovery_commit_owner_decision_recording_closeout_layer()
    )

    assert result["ok"] is True
    assert result["ready"] is True
    assert result["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )


def test_gp621_closeout_doctrine_is_locked():
    home = (
        get_recovery_commit_owner_decision_recording_closeout_home()
    )

    shell = (
        get_owner_decision_recording_closeout_shell()
    )

    assert home["ready"] is True
    assert shell["ready"] is True
    assert DOCTRINE["tower"] == "face_protocol_authority"
    assert DOCTRINE["teller"] == "workflow_request_source"
    assert DOCTRINE["vault"] == "sealed_memory"
    assert DOCTRINE["correct_flow"] == (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    )
    assert DOCTRINE["recording_closeout_only"] is True
    assert DOCTRINE[
        "recording_contract_may_be_frozen"
    ] is True
    assert DOCTRINE[
        "recording_gate_may_be_opened"
    ] is False
    assert DOCTRINE[
        "owner_decision_may_be_recorded"
    ] is False
    assert DOCTRINE[
        "teller_can_call_vault_directly"
    ] is False


def test_gp622_recording_gate_evidence_is_verified():
    board = (
        get_recording_gate_evidence_closeout_intake_board()
    )

    assert board["ready"] is True
    assert board["intake_count"] >= 1
    assert board[
        "all_recording_intakes_verified"
    ] is True
    assert board[
        "all_identity_prerequisites_verified"
    ] is True
    assert board[
        "all_approval_gates_verified"
    ] is True
    assert board[
        "all_recording_contracts_verified"
    ] is True
    assert board[
        "all_boundaries_verified"
    ] is True
    assert board[
        "all_record_drafts_verified"
    ] is True
    assert board[
        "all_receipt_drafts_verified"
    ] is True
    assert board[
        "all_eligible_for_closeout"
    ] is True
    assert board[
        "no_recording_gates_open"
    ] is True
    assert board[
        "no_owner_decisions_recorded"
    ] is True


def test_gp623_identity_requirements_are_sealed_not_satisfied():
    board = (
        get_identity_step_up_prerequisite_closeout_board()
    )

    assert board["ready"] is True
    assert board["closeout_count"] >= 1
    assert board[
        "all_requirements_sealed"
    ] is True
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
        "no_prerequisites_complete"
    ] is True
    assert board[
        "all_source_hashes_present"
    ] is True
    assert board[
        "all_closeout_hashes_present"
    ] is True


def test_gp624_approval_requirements_are_sealed_not_satisfied():
    board = (
        get_approval_dual_receipt_gate_closeout_board()
    )

    assert board["ready"] is True
    assert board["closeout_count"] >= 1
    assert board[
        "all_requirements_sealed"
    ] is True
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
        "all_source_hashes_present"
    ] is True
    assert board[
        "all_closeout_hashes_present"
    ] is True


def test_gp625_recording_contract_is_frozen():
    board = (
        get_owner_decision_recording_contract_freeze_board()
    )

    assert board["ready"] is True
    assert board["freeze_count"] >= 1
    assert len(ALLOWED_DECISION_VALUES) == 4
    assert "GRANT_GO" in ALLOWED_DECISION_VALUES
    assert "request_id" in RECORDING_CONTRACT_FIELDS
    assert "idempotency_key" in RECORDING_CONTRACT_FIELDS
    assert board["all_contracts_frozen"] is True
    assert board[
        "all_decision_enums_complete"
    ] is True
    assert board[
        "all_required_fields_complete"
    ] is True
    assert board[
        "no_owner_selections_present"
    ] is True
    assert board[
        "all_append_only_required"
    ] is True
    assert board["no_mutation_allowed"] is True
    assert board[
        "no_raw_material_allowed"
    ] is True
    assert board[
        "all_source_hashes_present"
    ] is True
    assert board[
        "all_freeze_hashes_present"
    ] is True


def test_gp626_boundaries_are_sealed_and_inactive():
    board = (
        get_scope_freeze_commit_window_boundary_closeout_board()
    )

    assert board["ready"] is True
    assert board["closeout_count"] >= 1
    assert board[
        "all_boundaries_sealed"
    ] is True
    assert board["all_exact_scopes_bound"] is True
    assert board[
        "all_one_time_windows_required"
    ] is True
    assert board[
        "all_scope_window_hashes_required"
    ] is True
    assert board["nothing_activated"] is True
    assert board[
        "recording_cannot_activate_boundaries"
    ] is True
    assert board[
        "no_production_targets_allowed"
    ] is True
    assert board[
        "no_external_providers_allowed"
    ] is True
    assert board[
        "all_source_hashes_present"
    ] is True
    assert board[
        "all_closeout_hashes_present"
    ] is True


def test_gp627_closeout_record_is_append_only_and_closed():
    board = (
        get_tower_owner_decision_recording_closeout_record_draft_board()
    )

    assert board["ready"] is True
    assert board["record_count"] >= 1
    assert board[
        "all_source_hashes_present"
    ] is True
    assert board[
        "all_closeout_packages_complete"
    ] is True
    assert board[
        "all_future_tower_handoffs_eligible"
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
        "all_records_unfinalized"
    ] is True
    assert board["all_append_only"] is True
    assert board["all_immutable"] is True
    assert board[
        "all_closeout_hashes_present"
    ] is True


def test_gp628_receipts_are_append_only_closeout_drafts():
    ledger = (
        get_tower_recording_closeout_receipt_draft_ledger()
    )

    assert ledger["ready"] is True
    assert ledger["receipt_count"] >= 1
    assert ledger["all_tower_controlled"] is True
    assert ledger[
        "all_closeout_components_recorded"
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


def test_gp629_all_dangerous_actions_are_blocked():
    board = (
        get_owner_decision_recording_closeout_safety_blocker_board()
    )

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board[
        "all_dangerous_actions_blocked"
    ] is True


def test_gp630_readiness_passes_and_corridor_continues():
    checkpoint = (
        get_owner_decision_recording_closeout_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True
    assert all(
        checkpoint["checks"].values()
    )
    assert checkpoint["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )
    assert checkpoint["closeout_status"] == (
        "recording_gate_contracts_sealed_"
        "prerequisites_unsatisfied_"
        "recording_gate_closed_"
        "owner_decision_absent"
    )
    assert checkpoint["corridor_continues"] is True
    assert checkpoint[
        "operational_readiness_gate_reached"
    ] is False
    assert (
        "OWNER DECISION TOWER HANDOFF"
        in checkpoint["next_recommended_layer"]
    )


def test_gp621_630_global_locks_remain_closed():
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


def test_gp621_630_routes_are_json_only():
    app_text = Path("web/app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_routes = [
        "/vault/recovery-commit-owner-decision-recording-closeout-layer.json",
        "/vault/owner-decision-recording-closeout-shell.json",
        "/vault/recording-gate-evidence-closeout-intake-board.json",
        "/vault/identity-step-up-prerequisite-closeout-board.json",
        "/vault/approval-dual-receipt-gate-closeout-board.json",
        "/vault/owner-decision-recording-contract-freeze-board.json",
        "/vault/scope-freeze-commit-window-boundary-closeout-board.json",
        "/vault/tower-owner-decision-recording-closeout-record-draft-board.json",
        "/vault/tower-recording-closeout-receipt-draft-ledger.json",
        "/vault/owner-decision-recording-closeout-safety-blocker-board.json",
        "/vault/owner-decision-recording-closeout-readiness.json",
        "/vault/gp621-status.json",
        "/vault/gp630-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert (
        '@app.route("/vault/recovery-commit-owner-'
        'decision-recording-closeout-layer")'
        not in app_text
    )
