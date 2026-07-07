
from pathlib import Path

from vault.tower_vault_request_protocol_gate_layer_service import (
    DOCTRINE,
    LOCKS,
    get_clearance_step_up_approval_gate_board,
    get_protocol_type_decision_board,
    get_redaction_scope_enforcement_board,
    get_tower_authorized_vault_request_draft_builder,
    get_tower_identity_permission_gate_board,
    get_tower_protocol_gate_safety_blocker_board,
    get_tower_protocol_receipt_draft_ledger,
    get_tower_vault_request_protocol_gate_home,
    get_tower_vault_request_protocol_gate_readiness_checkpoint,
    get_vault_call_pending_queue_preview_board,
    validate_tower_vault_request_protocol_gate_layer,
)


def test_gp461_470_readiness_checkpoint_passes():
    result = validate_tower_vault_request_protocol_gate_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Tower Vault request protocol gate layer" in result["readiness_label"]


def test_gp461_470_doctrine_locks_tower_as_protocol_gate():
    home = get_tower_vault_request_protocol_gate_home()

    assert home["ready"] is True
    assert home["doctrine"]["tower"] == "face_protocol_authority"
    assert home["doctrine"]["teller"] == "workflow_request_source"
    assert home["doctrine"]["vault"] == "sealed_memory"
    assert home["doctrine"]["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller"
    assert home["doctrine"]["tower_owns_protocol_gate"] is True
    assert home["doctrine"]["teller_can_call_vault_directly"] is False
    assert home["doctrine"]["vault_answers_tower_only"] is True
    assert home["doctrine"]["protocol_gate_executes_vault_call"] is False


def test_gp461_470_identity_permission_gates_require_tower_checks():
    board = get_tower_identity_permission_gate_board()

    assert board["ready"] is True
    assert board["identity_gate_count"] >= 2
    assert board["all_tower_identity_check_required"] is True
    assert board["all_tower_permission_check_required"] is True
    assert board["no_teller_self_approval"] is True
    assert board["no_vault_direct_approval"] is True

    for item in board["identity_permission_gates"]:
        assert item["gate_state"] == "tower_identity_permission_gate_required"
        assert item["tower_identity_check_required"] == 1
        assert item["tower_permission_check_required"] == 1
        assert item["teller_self_approval_allowed"] == 0
        assert item["vault_direct_approval_allowed"] == 0
        assert len(item["gate_hash"]) == 64


def test_gp461_470_clearance_step_up_gates_require_tower_approval_no_vault_direct():
    board = get_clearance_step_up_approval_gate_board()

    assert board["ready"] is True
    assert board["clearance_gate_count"] >= 2
    assert board["all_clearance_required"] is True
    assert board["all_tower_approval_required"] is True
    assert board["no_vault_direct_approval"] is True

    for item in board["clearance_gates"]:
        assert item["gate_state"] == "clearance_step_up_owner_approval_gate_required"
        assert item["clearance_required"] == 1
        assert item["tower_approval_required"] == 1
        assert item["vault_direct_approval_allowed"] == 0


def test_gp461_470_protocol_decisions_are_tower_gate_and_no_execution_yet():
    board = get_protocol_type_decision_board()

    assert board["ready"] is True
    assert board["protocol_decision_count"] >= 2
    assert board["all_tower_protocol_gate_required"] is True
    assert board["no_protocol_execution_yet"] is True
    assert board["no_teller_direct_protocol"] is True
    assert board["vault_answers_tower_only"] is True

    allowed_protocols = {
        "status_protocol",
        "proof_protocol",
        "receipt_protocol",
        "view_protocol",
        "download_protocol",
    }

    for item in board["protocol_decisions"]:
        assert item["decision_state"] == "protocol_type_selected_pending_tower_authorization"
        assert item["selected_protocol"] in allowed_protocols
        assert item["tower_protocol_gate_required"] == 1
        assert item["protocol_execution_allowed"] == 0
        assert item["teller_direct_protocol_allowed"] == 0
        assert item["vault_answers_tower_only"] == 1


def test_gp461_470_redaction_scope_blocks_raw_path_url_token_public_direct():
    board = get_redaction_scope_enforcement_board()

    assert board["ready"] is True
    assert board["redaction_scope_count"] >= 2
    assert board["all_redaction_required"] is True
    assert board["all_raw_file_bytes_redacted"] is True
    assert board["all_raw_paths_redacted"] is True
    assert board["all_raw_file_urls_redacted"] is True
    assert board["all_raw_tokens_redacted"] is True
    assert board["all_public_links_redacted"] is True
    assert board["all_direct_browse_redacted"] is True

    for item in board["redaction_scopes"]:
        assert item["redaction_state"] == "redaction_scope_enforced_for_tower_protocol"
        assert item["redaction_required"] == 1
        assert item["raw_file_bytes_redacted"] == 1
        assert item["raw_path_redacted"] == 1
        assert item["raw_file_url_redacted"] == 1
        assert item["raw_token_redacted"] == 1
        assert item["public_link_redacted"] == 1
        assert item["direct_browse_redacted"] == 1


def test_gp461_470_tower_authorized_vault_request_drafts_are_from_tower_only_not_sent():
    board = get_tower_authorized_vault_request_draft_builder()

    assert board["ready"] is True
    assert board["vault_request_draft_count"] >= 2
    assert board["all_addressed_to_vault"] is True
    assert board["all_originating_from_tower"] is True
    assert board["all_tower_is_requester"] is True
    assert board["no_teller_is_requester"] is True
    assert board["all_vault_calls_not_ready_yet"] is True
    assert board["no_vault_calls_sent"] is True
    assert board["no_protocol_execution_yet"] is True
    assert board["no_raw_file_bytes_requested"] is True
    assert board["no_raw_paths_requested"] is True
    assert board["no_public_links_requested"] is True

    for item in board["vault_request_drafts"]:
        assert item["draft_state"] == "tower_authorized_vault_request_draft_pending_protocol_execution"
        assert item["addressed_to"] == "Vault"
        assert item["originating_service"] == "Tower"
        assert item["tower_is_requester"] == 1
        assert item["teller_is_requester"] == 0
        assert item["vault_call_ready"] == 0
        assert item["vault_call_sent"] == 0
        assert item["protocol_execution_allowed"] == 0
        assert item["raw_file_bytes_requested"] == 0
        assert item["raw_path_requested"] == 0
        assert item["public_link_requested"] == 0
        assert len(item["request_draft_hash"]) == 64


def test_gp461_470_protocol_receipts_are_draft_append_only_and_require_vault_receipts():
    ledger = get_tower_protocol_receipt_draft_ledger()

    assert ledger["ready"] is True
    assert ledger["protocol_receipt_draft_count"] >= 2
    assert ledger["all_vault_service_receipts_required"] is True
    assert ledger["all_receipts_draft"] is True
    assert ledger["all_append_only"] is True
    assert ledger["all_immutable"] is True

    for item in ledger["protocol_receipt_drafts"]:
        assert item["receipt_state"] == "tower_protocol_receipt_draft_ready_pending_vault_call"
        assert item["vault_service_receipt_required"] == 1
        assert item["receipt_finalized"] == 0
        assert item["append_only"] == 1
        assert item["mutable"] == 0
        assert len(item["tower_protocol_receipt_hash"]) == 64


def test_gp461_470_pending_queue_is_preview_only_not_sent_or_received():
    board = get_vault_call_pending_queue_preview_board()

    assert board["ready"] is True
    assert board["pending_queue_count"] >= 2
    assert board["all_tower_protocol_pending"] is True
    assert board["all_vault_call_pending"] is True
    assert board["no_vault_calls_sent"] is True
    assert board["no_vault_response_received"] is True
    assert board["all_preview_only"] is True
    assert board["no_raw_file_bytes"] is True
    assert board["no_raw_paths"] is True
    assert board["no_public_links"] is True

    for item in board["pending_queue_previews"]:
        assert item["queue_state"] == "vault_call_pending_queue_preview_ready_not_sent"
        assert item["tower_protocol_pending"] == 1
        assert item["vault_call_pending"] == 1
        assert item["vault_call_sent"] == 0
        assert item["vault_response_received"] == 0
        assert item["preview_only"] == 1
        assert item["raw_file_bytes_included"] == 0
        assert item["raw_path_included"] == 0
        assert item["public_link_included"] == 0
        assert len(item["pending_queue_hash"]) == 64


def test_gp461_470_safety_blockers_prevent_protocol_execution_and_teller_direct_vault():
    board = get_tower_protocol_gate_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "actual_vault_call_execution" in blocked_actions
    assert "teller_to_vault_direct_call" in blocked_actions
    assert "teller_direct_download_from_vault" in blocked_actions
    assert "teller_direct_view_from_vault" in blocked_actions
    assert "teller_direct_proof_call_to_vault" in blocked_actions
    assert "view_download_proof_protocol_execution" in blocked_actions
    assert "public_vault_dashboard" in blocked_actions
    assert "direct_vault_user_portal" in blocked_actions
    assert "employee_vendor_customer_vault_browsing" in blocked_actions
    assert "public_links_or_raw_urls" in blocked_actions
    assert "raw_file_bytes_json" in blocked_actions


def test_gp461_470_readiness_declares_next_tower_authorized_view_protocol():
    checkpoint = get_tower_vault_request_protocol_gate_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_teller_to_tower_handoff_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"]["tower_owns_protocol_gate"] is True
    assert checkpoint["checks"]["teller_cannot_call_vault_directly"] is True
    assert checkpoint["checks"]["vault_answers_tower_only"] is True
    assert checkpoint["checks"]["protocol_gate_does_not_execute_vault_call"] is True
    assert checkpoint["checks"]["drafts_addressed_to_vault_from_tower_only"] is True
    assert checkpoint["checks"]["drafts_no_vault_call_or_protocol_execution_yet"] is True
    assert checkpoint["checks"]["pending_queue_not_sent_or_received"] is True
    assert "TOWER AUTHORIZED VIEW PROTOCOL" in checkpoint["next_recommended_layer"]


def test_gp461_470_global_locks_preserve_no_execution_no_teller_to_vault():
    assert LOCKS["tower_identity_permission_gate_allowed"] is True
    assert LOCKS["clearance_step_up_approval_gate_allowed"] is True
    assert LOCKS["protocol_type_decision_allowed"] is True
    assert LOCKS["redaction_scope_enforcement_allowed"] is True
    assert LOCKS["tower_authorized_vault_request_drafts_allowed"] is True
    assert LOCKS["tower_protocol_receipt_drafts_allowed"] is True
    assert LOCKS["vault_call_pending_queue_preview_allowed"] is True

    assert LOCKS["actual_vault_call_execution_allowed"] is False
    assert LOCKS["vault_call_sent"] is False
    assert LOCKS["teller_to_vault_direct_call_allowed"] is False
    assert LOCKS["vault_direct_request_from_teller_allowed"] is False
    assert LOCKS["vault_direct_approval_from_teller_allowed"] is False
    assert LOCKS["view_protocol_execution_allowed"] is False
    assert LOCKS["download_protocol_execution_allowed"] is False
    assert LOCKS["proof_protocol_execution_allowed"] is False
    assert LOCKS["public_vault_dashboard_allowed"] is False
    assert LOCKS["direct_vault_user_portal_allowed"] is False
    assert LOCKS["employee_vault_browsing_allowed"] is False
    assert LOCKS["external_collaborator_browsing_allowed"] is False
    assert LOCKS["public_url_created"] is False
    assert LOCKS["share_link_created"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False


def test_gp461_470_routes_are_json_only_no_public_page_route():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/tower-vault-request-protocol-gate-layer.json",
        "/vault/tower-vault-request-protocol-gate-shell.json",
        "/vault/tower-identity-permission-gate-board.json",
        "/vault/clearance-step-up-approval-gate-board.json",
        "/vault/protocol-type-decision-board.json",
        "/vault/redaction-scope-enforcement-board.json",
        "/vault/tower-authorized-vault-request-draft-builder.json",
        "/vault/tower-protocol-receipt-draft-ledger.json",
        "/vault/vault-call-pending-queue-preview-board.json",
        "/vault/tower-protocol-gate-safety-blocker-board.json",
        "/vault/tower-vault-request-protocol-gate-readiness-checkpoint.json",
        "/vault/gp461-status.json",
        "/vault/gp470-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert '@app.route("/vault/tower-vault-request-protocol-gate-layer")' not in app_text
