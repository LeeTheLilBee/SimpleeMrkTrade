
from pathlib import Path

from vault.recovery_commit_owner_decision_tower_handoff_acceptance_gate_service import (
    ACCEPTANCE_CONTRACT_FIELDS,
    ACCEPTANCE_DECISIONS,
    CURRENT_RECOMMENDATION,
    DOCTRINE,
    LOCKS,
    get_recovery_commit_owner_decision_tower_handoff_acceptance_home,
    get_tower_acceptance_session_prerequisite_board,
    get_tower_handoff_acceptance_authority_contract_board,
    get_tower_handoff_acceptance_decision_contract_board,
    get_tower_handoff_acceptance_evidence_reference_gate,
    get_tower_handoff_acceptance_gate_readiness_checkpoint,
    get_tower_handoff_acceptance_gate_shell,
    get_tower_handoff_acceptance_receipt_draft_ledger,
    get_tower_handoff_acceptance_record_draft_board,
    get_tower_handoff_acceptance_safety_blocker_board,
    get_tower_handoff_packet_intake_verification_board,
    validate_recovery_commit_owner_decision_tower_handoff_acceptance_gate,
)


def test_gp641_650_validation_passes():
    result = (
        validate_recovery_commit_owner_decision_tower_handoff_acceptance_gate()
    )

    assert result["ok"] is True
    assert result["ready"] is True
    assert result["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )


def test_gp641_acceptance_doctrine_is_definition_only():
    home = (
        get_recovery_commit_owner_decision_tower_handoff_acceptance_home()
    )

    shell = (
        get_tower_handoff_acceptance_gate_shell()
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
        "acceptance_gate_definition_only"
    ] is True
    assert DOCTRINE[
        "acceptance_execution_allowed"
    ] is False
    assert DOCTRINE[
        "tower_is_only_handoff_acceptance_authority"
    ] is True
    assert DOCTRINE[
        "vault_cannot_accept_its_own_handoff"
    ] is True
    assert DOCTRINE[
        "teller_cannot_accept_vault_handoff"
    ] is True


def test_gp642_handoff_packet_is_verified():
    board = (
        get_tower_handoff_packet_intake_verification_board()
    )

    assert board["ready"] is True
    assert board["intake_count"] >= 1
    assert board[
        "all_handoff_intakes_verified"
    ] is True
    assert board["all_envelopes_verified"] is True
    assert board[
        "all_session_contracts_verified"
    ] is True
    assert board[
        "all_owner_input_contracts_verified"
    ] is True
    assert board[
        "all_approval_reference_contracts_verified"
    ] is True
    assert board["all_packets_verified"] is True
    assert board["all_receipts_verified"] is True
    assert board[
        "all_eligible_for_acceptance_review"
    ] is True
    assert board["no_handoffs_delivered"] is True
    assert board["no_handoffs_accepted"] is True


def test_gp643_only_tower_can_accept():
    board = (
        get_tower_handoff_acceptance_authority_contract_board()
    )

    assert board["ready"] is True
    assert board["contract_count"] >= 1
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
        "all_authority_hashes_present"
    ] is True


def test_gp644_acceptance_session_is_not_created():
    board = (
        get_tower_acceptance_session_prerequisite_board()
    )

    assert board["ready"] is True
    assert board["session_count"] >= 1
    assert board["all_requirements_present"] is True
    assert board["no_sessions_created"] is True
    assert board["no_sessions_started"] is True
    assert board[
        "no_prerequisites_complete"
    ] is True
    assert board[
        "all_prerequisite_hashes_present"
    ] is True


def test_gp645_evidence_references_are_required_not_supplied():
    board = (
        get_tower_handoff_acceptance_evidence_reference_gate()
    )

    assert board["ready"] is True
    assert board["gate_count"] >= 1
    assert board[
        "all_evidence_requirements_present"
    ] is True
    assert board["no_references_supplied"] is True
    assert board[
        "no_evidence_gates_complete"
    ] is True
    assert board[
        "all_evidence_hashes_present"
    ] is True


def test_gp646_acceptance_contract_is_complete_but_unselected():
    board = (
        get_tower_handoff_acceptance_decision_contract_board()
    )

    assert board["ready"] is True
    assert board["contract_count"] >= 1
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
        "all_contract_hashes_present"
    ] is True


def test_gp647_acceptance_record_is_draft_only():
    board = (
        get_tower_handoff_acceptance_record_draft_board()
    )

    assert board["ready"] is True
    assert board["record_count"] >= 1
    assert board[
        "all_source_hashes_present"
    ] is True
    assert board[
        "all_acceptance_contracts_complete"
    ] is True
    assert board["no_handoffs_delivered"] is True
    assert board["no_handoffs_accepted"] is True
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


def test_gp648_receipts_are_append_only_drafts():
    ledger = (
        get_tower_handoff_acceptance_receipt_draft_ledger()
    )

    assert ledger["ready"] is True
    assert ledger["receipt_count"] >= 1
    assert ledger["all_tower_controlled"] is True
    assert ledger[
        "all_contract_components_recorded"
    ] is True
    assert ledger[
        "no_delivery_or_acceptance_recorded"
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


def test_gp649_all_dangerous_actions_are_blocked():
    board = (
        get_tower_handoff_acceptance_safety_blocker_board()
    )

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board[
        "all_dangerous_actions_blocked"
    ] is True


def test_gp650_readiness_passes_and_corridor_continues():
    checkpoint = (
        get_tower_handoff_acceptance_gate_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True
    assert all(
        checkpoint["checks"].values()
    )
    assert checkpoint["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )
    assert checkpoint["acceptance_gate_status"] == (
        "handoff_packet_verified_"
        "tower_acceptance_contract_ready_"
        "acceptance_evidence_unsupplied_"
        "handoff_not_delivered_or_accepted"
    )
    assert checkpoint["corridor_continues"] is True
    assert checkpoint[
        "operational_readiness_gate_reached"
    ] is False
    assert (
        "ACCEPTANCE CLOSEOUT"
        in checkpoint["next_recommended_layer"]
    )


def test_gp641_650_global_locks_remain_closed():
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


def test_gp641_650_routes_are_json_only():
    app_text = Path("web/app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_routes = [
        "/vault/recovery-commit-owner-decision-tower-handoff-acceptance-gate.json",
        "/vault/tower-handoff-acceptance-gate-shell.json",
        "/vault/tower-handoff-packet-intake-verification-board.json",
        "/vault/tower-handoff-acceptance-authority-contract-board.json",
        "/vault/tower-acceptance-session-prerequisite-board.json",
        "/vault/tower-handoff-acceptance-evidence-reference-gate.json",
        "/vault/tower-handoff-acceptance-decision-contract-board.json",
        "/vault/tower-handoff-acceptance-record-draft-board.json",
        "/vault/tower-handoff-acceptance-receipt-draft-ledger.json",
        "/vault/tower-handoff-acceptance-safety-blocker-board.json",
        "/vault/tower-handoff-acceptance-gate-readiness.json",
        "/vault/gp641-status.json",
        "/vault/gp650-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert (
        '@app.route("/vault/recovery-commit-owner-'
        'decision-tower-handoff-acceptance-gate")'
        not in app_text
    )
