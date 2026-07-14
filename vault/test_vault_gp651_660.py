
from pathlib import Path

from vault.recovery_commit_owner_decision_tower_handoff_acceptance_closeout_layer_service import (
    ACCEPTANCE_CONTRACT_FIELDS,
    ACCEPTANCE_DECISIONS,
    CURRENT_RECOMMENDATION,
    DOCTRINE,
    LOCKS,
    get_acceptance_evidence_reference_requirement_freeze_board,
    get_acceptance_gate_evidence_closeout_intake_board,
    get_recovery_commit_owner_decision_tower_handoff_acceptance_closeout_home,
    get_tower_acceptance_authority_requirement_closeout_board,
    get_tower_acceptance_closeout_readiness_checkpoint,
    get_tower_acceptance_closeout_receipt_draft_ledger,
    get_tower_acceptance_closeout_record_draft_board,
    get_tower_acceptance_closeout_safety_blocker_board,
    get_tower_acceptance_decision_contract_freeze_board,
    get_tower_acceptance_session_requirement_closeout_board,
    get_tower_handoff_acceptance_closeout_shell,
    validate_recovery_commit_owner_decision_tower_handoff_acceptance_closeout_layer,
)


def test_gp651_660_validation_passes():
    result = (
        validate_recovery_commit_owner_decision_tower_handoff_acceptance_closeout_layer()
    )

    assert result["ok"] is True
    assert result["ready"] is True
    assert result["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )


def test_gp651_closeout_doctrine_is_locked():
    home = (
        get_recovery_commit_owner_decision_tower_handoff_acceptance_closeout_home()
    )

    shell = (
        get_tower_handoff_acceptance_closeout_shell()
    )

    assert home["ready"] is True
    assert shell["ready"] is True
    assert DOCTRINE["tower"] == "face_protocol_authority"
    assert DOCTRINE["teller"] == "workflow_request_source"
    assert DOCTRINE["vault"] == "sealed_memory"
    assert DOCTRINE["correct_flow"] == (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    )
    assert DOCTRINE[
        "acceptance_closeout_only"
    ] is True
    assert DOCTRINE[
        "acceptance_requirements_may_be_sealed"
    ] is True
    assert DOCTRINE[
        "acceptance_execution_allowed"
    ] is False
    assert DOCTRINE[
        "vault_cannot_accept_its_own_handoff"
    ] is True
    assert DOCTRINE[
        "teller_cannot_accept_vault_handoff"
    ] is True


def test_gp652_acceptance_gate_evidence_is_verified():
    board = (
        get_acceptance_gate_evidence_closeout_intake_board()
    )

    assert board["ready"] is True
    assert board["intake_count"] >= 1
    assert board[
        "all_acceptance_intakes_verified"
    ] is True
    assert board[
        "all_authority_contracts_verified"
    ] is True
    assert board[
        "all_session_contracts_verified"
    ] is True
    assert board[
        "all_evidence_gates_verified"
    ] is True
    assert board[
        "all_decision_contracts_verified"
    ] is True
    assert board[
        "all_acceptance_records_verified"
    ] is True
    assert board[
        "all_acceptance_receipts_verified"
    ] is True
    assert board[
        "all_eligible_for_closeout"
    ] is True
    assert board[
        "no_handoffs_delivered"
    ] is True
    assert board[
        "no_handoffs_accepted"
    ] is True
    assert board[
        "no_acceptance_decisions_recorded"
    ] is True


def test_gp653_acceptance_authority_requirements_are_sealed():
    board = (
        get_tower_acceptance_authority_requirement_closeout_board()
    )

    assert board["ready"] is True
    assert board["closeout_count"] >= 1
    assert board[
        "all_requirements_sealed"
    ] is True
    assert board["all_target_tower"] is True
    assert board[
        "all_tower_controls_required"
    ] is True
    assert board[
        "no_vault_acceptance_authority"
    ] is True
    assert board[
        "no_teller_acceptance_authority"
    ] is True
    assert board[
        "no_acceptance_authority_granted"
    ] is True
    assert board[
        "all_source_hashes_present"
    ] is True
    assert board[
        "all_closeout_hashes_present"
    ] is True


def test_gp654_acceptance_session_requirements_are_sealed():
    board = (
        get_tower_acceptance_session_requirement_closeout_board()
    )

    assert board["ready"] is True
    assert board["closeout_count"] >= 1
    assert board[
        "all_requirements_sealed"
    ] is True
    assert board[
        "all_session_requirements_present"
    ] is True
    assert board[
        "no_sessions_created"
    ] is True
    assert board[
        "no_sessions_started"
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


def test_gp655_evidence_requirements_are_frozen_unsupplied():
    board = (
        get_acceptance_evidence_reference_requirement_freeze_board()
    )

    assert board["ready"] is True
    assert board["freeze_count"] >= 1
    assert board[
        "all_requirements_frozen"
    ] is True
    assert board[
        "all_reference_requirements_present"
    ] is True
    assert board[
        "no_references_supplied"
    ] is True
    assert board[
        "no_evidence_gates_complete"
    ] is True
    assert board[
        "all_source_hashes_present"
    ] is True
    assert board[
        "all_freeze_hashes_present"
    ] is True


def test_gp656_acceptance_decision_contract_is_frozen():
    board = (
        get_tower_acceptance_decision_contract_freeze_board()
    )

    assert board["ready"] is True
    assert board["freeze_count"] >= 1
    assert len(ACCEPTANCE_DECISIONS) == 4
    assert "ACCEPT_HANDOFF" in ACCEPTANCE_DECISIONS
    assert "REJECT_HANDOFF" in ACCEPTANCE_DECISIONS
    assert "handoff_packet_id" in (
        ACCEPTANCE_CONTRACT_FIELDS
    )
    assert "idempotency_key" in (
        ACCEPTANCE_CONTRACT_FIELDS
    )
    assert board[
        "all_contracts_frozen"
    ] is True
    assert board[
        "all_decision_enums_complete"
    ] is True
    assert board[
        "all_required_fields_complete"
    ] is True
    assert board["all_tower_only"] is True
    assert board[
        "no_acceptance_selections_present"
    ] is True
    assert board[
        "no_acceptance_decisions_recorded"
    ] is True
    assert board[
        "no_owner_decisions_recorded"
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


def test_gp657_closeout_record_is_append_only():
    board = (
        get_tower_acceptance_closeout_record_draft_board()
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
        "all_future_delivery_preparation_eligible"
    ] is True
    assert board[
        "no_handoffs_delivered"
    ] is True
    assert board[
        "no_handoffs_accepted"
    ] is True
    assert board[
        "no_acceptance_decisions_recorded"
    ] is True
    assert board[
        "no_tower_sessions_created"
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
        "all_records_unfinalized"
    ] is True
    assert board["all_append_only"] is True
    assert board["all_immutable"] is True
    assert board[
        "all_record_hashes_present"
    ] is True


def test_gp658_closeout_receipts_are_safe_drafts():
    ledger = (
        get_tower_acceptance_closeout_receipt_draft_ledger()
    )

    assert ledger["ready"] is True
    assert ledger["receipt_count"] >= 1
    assert ledger["all_tower_controlled"] is True
    assert ledger[
        "all_closeout_components_recorded"
    ] is True
    assert ledger[
        "no_delivery_acceptance_or_session_recorded"
    ] is True
    assert ledger[
        "no_owner_or_recovery_actions_recorded"
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


def test_gp659_all_dangerous_actions_are_blocked():
    board = (
        get_tower_acceptance_closeout_safety_blocker_board()
    )

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board[
        "all_dangerous_actions_blocked"
    ] is True


def test_gp660_readiness_passes_and_corridor_continues():
    checkpoint = (
        get_tower_acceptance_closeout_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True
    assert all(
        checkpoint["checks"].values()
    )
    assert checkpoint["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )
    assert checkpoint["closeout_status"] == (
        "acceptance_gate_evidence_verified_"
        "acceptance_requirements_sealed_"
        "acceptance_evidence_unsupplied_"
        "handoff_not_delivered_or_accepted"
    )
    assert checkpoint["corridor_continues"] is True
    assert checkpoint[
        "operational_readiness_gate_reached"
    ] is False
    assert (
        "DELIVERY PREPARATION"
        in checkpoint["next_recommended_layer"]
    )


def test_gp651_660_global_locks_remain_closed():
    assert LOCKS["handoff_delivered"] is False
    assert LOCKS["handoff_accepted"] is False
    assert LOCKS[
        "acceptance_decision_recorded"
    ] is False
    assert LOCKS["acceptance_gate_open"] is False
    assert LOCKS[
        "acceptance_execution_allowed"
    ] is False
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
        "employee_vault_access_allowed"
    ] is False
    assert LOCKS[
        "customer_vault_access_allowed"
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


def test_gp651_660_routes_are_json_only():
    app_text = Path("web/app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_routes = [
        "/vault/recovery-commit-owner-decision-tower-handoff-acceptance-closeout-layer.json",
        "/vault/tower-handoff-acceptance-closeout-shell.json",
        "/vault/acceptance-gate-evidence-closeout-intake-board.json",
        "/vault/tower-acceptance-authority-requirement-closeout-board.json",
        "/vault/tower-acceptance-session-requirement-closeout-board.json",
        "/vault/acceptance-evidence-reference-requirement-freeze-board.json",
        "/vault/tower-acceptance-decision-contract-freeze-board.json",
        "/vault/tower-acceptance-closeout-record-draft-board.json",
        "/vault/tower-acceptance-closeout-receipt-draft-ledger.json",
        "/vault/tower-acceptance-closeout-safety-blocker-board.json",
        "/vault/tower-acceptance-closeout-readiness.json",
        "/vault/gp651-status.json",
        "/vault/gp660-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert (
        '@app.route("/vault/recovery-commit-owner-'
        'decision-tower-handoff-acceptance-closeout-layer")'
        not in app_text
    )
