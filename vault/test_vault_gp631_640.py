
from pathlib import Path

from vault.recovery_commit_owner_decision_tower_handoff_layer_service import (
    ALLOWED_DECISION_VALUES,
    CURRENT_RECOMMENDATION,
    DOCTRINE,
    HANDOFF_ENVELOPE_FIELDS,
    LOCKS,
    RECORDING_CONTRACT_FIELDS,
    get_approval_receipt_reference_handoff_board,
    get_owner_decision_input_handoff_contract_board,
    get_owner_decision_tower_handoff_shell,
    get_recording_closeout_package_intake_board,
    get_recovery_commit_owner_decision_tower_handoff_home,
    get_tower_handoff_envelope_contract_board,
    get_tower_handoff_readiness_checkpoint,
    get_tower_handoff_safety_blocker_board,
    get_tower_owner_decision_handoff_packet_draft_board,
    get_tower_owner_decision_handoff_receipt_draft_ledger,
    get_tower_owner_review_session_launch_prerequisite_board,
    validate_recovery_commit_owner_decision_tower_handoff_layer,
)


def test_gp631_640_validation_passes():
    result = (
        validate_recovery_commit_owner_decision_tower_handoff_layer()
    )

    assert result["ok"] is True
    assert result["ready"] is True
    assert result["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )


def test_gp631_handoff_doctrine_is_packaging_only():
    home = (
        get_recovery_commit_owner_decision_tower_handoff_home()
    )

    shell = get_owner_decision_tower_handoff_shell()

    assert home["ready"] is True
    assert shell["ready"] is True
    assert DOCTRINE["tower"] == "face_protocol_authority"
    assert DOCTRINE["teller"] == "workflow_request_source"
    assert DOCTRINE["vault"] == "sealed_memory"
    assert DOCTRINE["correct_flow"] == (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    )
    assert DOCTRINE[
        "tower_handoff_packaging_only"
    ] is True
    assert DOCTRINE[
        "tower_handoff_delivery_allowed"
    ] is False
    assert DOCTRINE[
        "tower_handoff_acceptance_allowed"
    ] is False
    assert DOCTRINE[
        "vault_may_not_collect_owner_input"
    ] is True
    assert DOCTRINE[
        "teller_can_call_vault_directly"
    ] is False


def test_gp632_closeout_package_is_verified():
    board = (
        get_recording_closeout_package_intake_board()
    )

    assert board["ready"] is True
    assert board["intake_count"] >= 1
    assert board[
        "all_closeout_intakes_verified"
    ] is True
    assert board[
        "all_identity_closeouts_verified"
    ] is True
    assert board[
        "all_approval_closeouts_verified"
    ] is True
    assert board[
        "all_contract_freezes_verified"
    ] is True
    assert board[
        "all_boundaries_verified"
    ] is True
    assert board[
        "all_closeout_records_verified"
    ] is True
    assert board[
        "all_closeout_receipts_verified"
    ] is True
    assert board[
        "all_eligible_for_handoff_packaging"
    ] is True
    assert board[
        "no_handoffs_delivered"
    ] is True
    assert board[
        "no_handoffs_accepted"
    ] is True


def test_gp633_handoff_envelope_is_tower_only():
    board = (
        get_tower_handoff_envelope_contract_board()
    )

    assert board["ready"] is True
    assert board["envelope_count"] >= 1
    assert "handoff_id" in HANDOFF_ENVELOPE_FIELDS
    assert (
        "required_step_up_receipt_reference"
        in HANDOFF_ENVELOPE_FIELDS
    )
    assert board["all_target_tower"] is True
    assert board["all_workflows_bound"] is True
    assert board[
        "all_required_fields_complete"
    ] is True
    assert board[
        "all_source_hashes_present"
    ] is True
    assert board["all_tower_only"] is True
    assert board["all_references_only"] is True
    assert board[
        "no_raw_material_allowed"
    ] is True
    assert board["no_delivery_allowed"] is True
    assert board["no_acceptance_allowed"] is True
    assert board[
        "all_envelope_hashes_present"
    ] is True


def test_gp634_session_prerequisites_are_unsatisfied():
    board = (
        get_tower_owner_review_session_launch_prerequisite_board()
    )

    assert board["ready"] is True
    assert board["prerequisite_count"] >= 1
    assert board[
        "all_session_requirements_present"
    ] is True
    assert board["no_sessions_created"] is True
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
        "all_prerequisite_hashes_present"
    ] is True


def test_gp635_owner_input_contract_is_tower_ui_only():
    board = (
        get_owner_decision_input_handoff_contract_board()
    )

    assert board["ready"] is True
    assert board["contract_count"] >= 1
    assert len(ALLOWED_DECISION_VALUES) == 4
    assert "GRANT_GO" in ALLOWED_DECISION_VALUES
    assert "request_id" in RECORDING_CONTRACT_FIELDS
    assert board[
        "all_decision_enums_complete"
    ] is True
    assert board[
        "all_recording_fields_complete"
    ] is True
    assert board["all_tower_ui_only"] is True
    assert board["no_vault_direct_input"] is True
    assert board["no_teller_direct_input"] is True
    assert board[
        "no_owner_selections_present"
    ] is True
    assert board[
        "no_owner_decisions_recorded"
    ] is True
    assert board[
        "all_integrity_requirements_present"
    ] is True
    assert board[
        "all_contract_hashes_present"
    ] is True


def test_gp636_approval_references_are_required_not_supplied():
    board = (
        get_approval_receipt_reference_handoff_board()
    )

    assert board["ready"] is True
    assert board["handoff_count"] >= 1
    assert board[
        "all_required_references_present"
    ] is True
    assert board["no_references_supplied"] is True
    assert board[
        "no_reference_gates_complete"
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
        "all_reference_hashes_present"
    ] is True


def test_gp637_handoff_packet_is_complete_not_delivered():
    board = (
        get_tower_owner_decision_handoff_packet_draft_board()
    )

    assert board["ready"] is True
    assert board["packet_count"] >= 1
    assert board[
        "all_source_hashes_present"
    ] is True
    assert board["all_packages_complete"] is True
    assert board[
        "all_future_acceptance_eligible"
    ] is True
    assert board[
        "no_handoffs_delivered"
    ] is True
    assert board[
        "no_handoffs_accepted"
    ] is True
    assert board[
        "no_tower_sessions_created"
    ] is True
    assert board[
        "no_owner_selections_present"
    ] is True
    assert board[
        "no_owner_decisions_recorded"
    ] is True
    assert board[
        "no_recording_gates_open"
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
        "all_packets_unfinalized"
    ] is True
    assert board["all_append_only"] is True
    assert board["all_immutable"] is True
    assert board[
        "all_packet_hashes_present"
    ] is True


def test_gp638_receipts_are_append_only_drafts():
    ledger = (
        get_tower_owner_decision_handoff_receipt_draft_ledger()
    )

    assert ledger["ready"] is True
    assert ledger["receipt_count"] >= 1
    assert ledger["all_tower_controlled"] is True
    assert ledger[
        "all_package_components_recorded"
    ] is True
    assert ledger[
        "no_delivery_acceptance_or_session_recorded"
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


def test_gp639_all_dangerous_actions_are_blocked():
    board = get_tower_handoff_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board[
        "all_dangerous_actions_blocked"
    ] is True


def test_gp640_readiness_passes_and_corridor_continues():
    checkpoint = get_tower_handoff_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert all(
        checkpoint["checks"].values()
    )
    assert checkpoint["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )
    assert checkpoint["handoff_status"] == (
        "sealed_closeout_package_verified_"
        "tower_handoff_packet_ready_"
        "handoff_not_delivered_or_accepted_"
        "owner_decision_absent"
    )
    assert checkpoint["corridor_continues"] is True
    assert checkpoint[
        "operational_readiness_gate_reached"
    ] is False
    assert (
        "TOWER HANDOFF ACCEPTANCE GATE"
        in checkpoint["next_recommended_layer"]
    )


def test_gp631_640_global_locks_remain_closed():
    assert LOCKS["handoff_delivered"] is False
    assert LOCKS["handoff_accepted"] is False
    assert LOCKS["tower_session_created"] is False
    assert LOCKS["review_session_started"] is False
    assert LOCKS["owner_authenticated"] is False
    assert LOCKS["step_up_satisfied"] is False
    assert LOCKS[
        "owner_admin_approval_granted"
    ] is False
    assert LOCKS["dual_receipt_satisfied"] is False
    assert LOCKS[
        "second_authority_review_granted"
    ] is False
    assert LOCKS["owner_selection_present"] is False
    assert LOCKS["owner_decision_recorded"] is False
    assert LOCKS["recording_gate_open"] is False
    assert LOCKS["go_decision_granted"] is False
    assert LOCKS[
        "live_recovery_authorization_granted"
    ] is False
    assert LOCKS["authorization_token_issued"] is False
    assert LOCKS["scope_freeze_activated"] is False
    assert LOCKS["commit_window_activated"] is False
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


def test_gp631_640_routes_are_json_only():
    app_text = Path("web/app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_routes = [
        "/vault/recovery-commit-owner-decision-tower-handoff-layer.json",
        "/vault/owner-decision-tower-handoff-shell.json",
        "/vault/recording-closeout-package-intake-board.json",
        "/vault/tower-handoff-envelope-contract-board.json",
        "/vault/tower-owner-review-session-launch-prerequisite-board.json",
        "/vault/owner-decision-input-handoff-contract-board.json",
        "/vault/approval-receipt-reference-handoff-board.json",
        "/vault/tower-owner-decision-handoff-packet-draft-board.json",
        "/vault/tower-owner-decision-handoff-receipt-draft-ledger.json",
        "/vault/tower-handoff-safety-blocker-board.json",
        "/vault/tower-handoff-readiness.json",
        "/vault/gp631-status.json",
        "/vault/gp640-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert (
        '@app.route("/vault/recovery-commit-owner-'
        'decision-tower-handoff-layer")'
        not in app_text
    )
