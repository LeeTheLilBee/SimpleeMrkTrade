
from pathlib import Path

from vault.tower_authorized_download_protocol_layer_service import (
    DOCTRINE,
    LOCKS,
    get_download_eligibility_gate_board,
    get_download_handle_hash_guard_board,
    get_download_receipt_draft_ledger,
    get_download_scope_redaction_gate_board,
    get_tower_authorized_download_protocol_home,
    get_tower_authorized_download_protocol_readiness_checkpoint,
    get_tower_authorized_download_safety_blocker_board,
    get_tower_download_result_delivery_preview_board,
    get_tower_download_session_draft_board,
    get_tower_internal_vault_download_request_ledger,
    get_vault_download_response_envelope_board,
    validate_tower_authorized_download_protocol_layer,
)


def test_gp481_490_readiness_checkpoint_passes():
    result = validate_tower_authorized_download_protocol_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Tower authorized download protocol layer" in result["readiness_label"]


def test_gp481_490_doctrine_locks_controlled_download_only():
    home = get_tower_authorized_download_protocol_home()

    assert home["ready"] is True
    assert home["doctrine"]["tower"] == "face_protocol_authority"
    assert home["doctrine"]["teller"] == "workflow_request_source"
    assert home["doctrine"]["vault"] == "sealed_memory"
    assert home["doctrine"]["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller"
    assert home["doctrine"]["tower_executes_controlled_download_protocol"] is True
    assert home["doctrine"]["download_protocol_answers_tower_only"] is True
    assert home["doctrine"]["teller_can_call_vault_directly"] is False
    assert home["doctrine"]["teller_can_download_from_vault_directly"] is False
    assert home["doctrine"]["vault_answers_tower_only"] is True
    assert home["doctrine"]["raw_file_bytes_exposed_by_json"] is False
    assert home["doctrine"]["raw_download_token_exposed"] is False
    assert home["doctrine"]["public_link_created_by_download"] is False


def test_gp481_490_download_eligibility_is_tower_only_no_raw_token_or_public():
    board = get_download_eligibility_gate_board()

    assert board["ready"] is True
    assert board["download_eligibility_count"] >= 2
    assert board["all_tower_is_requester"] is True
    assert board["no_teller_is_requester"] is True
    assert board["all_tower_identity_permission_passed"] is True
    assert board["all_tower_approval_recorded"] is True
    assert board["all_download_protocol_allowed"] is True
    assert board["no_proof_protocol_allowed"] is True
    assert board["no_teller_direct_download"] is True
    assert board["no_raw_file_bytes_json"] is True
    assert board["no_public_download_links"] is True
    assert board["no_raw_download_tokens"] is True

    for item in board["download_eligibility_gates"]:
        assert item["gate_state"] == "download_eligibility_gate_passed_for_tower_only"
        assert item["tower_is_requester"] == 1
        assert item["teller_is_requester"] == 0
        assert item["download_protocol_allowed"] == 1
        assert item["proof_protocol_allowed"] == 0
        assert item["teller_direct_download_allowed"] == 0
        assert item["raw_file_bytes_json_allowed"] == 0
        assert item["public_download_link_allowed"] == 0
        assert item["raw_download_token_allowed"] == 0


def test_gp481_490_download_redaction_is_sealed_handle_only():
    board = get_download_scope_redaction_gate_board()

    assert board["ready"] is True
    assert board["download_redaction_count"] >= 2
    assert board["all_sealed_handle_only"] is True
    assert board["all_raw_file_bytes_redacted"] is True
    assert board["all_raw_paths_redacted"] is True
    assert board["all_raw_file_urls_redacted"] is True
    assert board["all_raw_download_tokens_redacted"] is True
    assert board["all_public_links_redacted"] is True
    assert board["all_direct_browse_redacted"] is True

    for item in board["download_redaction_gates"]:
        assert item["redaction_state"] == "download_scope_redaction_gate_ready_handle_hash_only"
        assert item["sealed_handle_only"] == 1
        assert item["raw_file_bytes_redacted"] == 1
        assert item["raw_path_redacted"] == 1
        assert item["raw_file_url_redacted"] == 1
        assert item["raw_download_token_redacted"] == 1
        assert item["public_link_redacted"] == 1
        assert item["direct_browse_redacted"] == 1


def test_gp481_490_tower_download_sessions_are_internal_only():
    board = get_tower_download_session_draft_board()

    assert board["ready"] is True
    assert board["download_session_count"] >= 2
    assert board["all_session_owner_tower"] is True
    assert board["all_tower_session_required"] is True
    assert board["no_teller_session"] is True
    assert board["no_direct_vault_session"] is True
    assert board["no_public_session"] is True

    for item in board["download_sessions"]:
        assert item["session_state"] == "tower_download_session_draft_ready_internal_only"
        assert item["session_owner"] == "Tower"
        assert item["tower_session_required"] == 1
        assert item["teller_session_allowed"] == 0
        assert item["direct_vault_session_allowed"] == 0
        assert item["public_session_allowed"] == 0
        assert len(item["download_session_hash"]) == 64


def test_gp481_490_internal_download_requests_are_tower_to_vault_only_no_raw_url_token_public():
    ledger = get_tower_internal_vault_download_request_ledger()

    assert ledger["ready"] is True
    assert ledger["internal_download_request_count"] >= 2
    assert ledger["all_from_tower_to_vault"] is True
    assert ledger["all_vault_answer_target_tower"] is True
    assert ledger["all_internal_download_calls_sent"] is True
    assert ledger["no_teller_calls_sent"] is True
    assert ledger["no_raw_file_bytes_requested"] is True
    assert ledger["no_raw_paths_requested"] is True
    assert ledger["no_raw_file_urls_requested"] is True
    assert ledger["no_raw_tokens_requested"] is True
    assert ledger["no_public_links_requested"] is True

    for item in ledger["internal_download_requests"]:
        assert item["request_state"] == "tower_internal_vault_download_request_sent_controlled"
        assert item["from_service"] == "Tower"
        assert item["to_service"] == "Vault"
        assert item["vault_answer_target"] == "Tower"
        assert item["internal_vault_download_call_sent"] == 1
        assert item["teller_call_sent"] == 0
        assert item["raw_file_bytes_requested"] == 0
        assert item["raw_path_requested"] == 0
        assert item["raw_file_url_requested"] == 0
        assert item["raw_token_requested"] == 0
        assert item["public_link_requested"] == 0
        assert len(item["internal_request_hash"]) == 64


def test_gp481_490_vault_download_response_is_tower_only_hash_envelope_no_raw_public():
    board = get_vault_download_response_envelope_board()

    assert board["ready"] is True
    assert board["download_response_count"] >= 2
    assert board["all_answered_to_tower"] is True
    assert board["all_vault_answered_tower_only"] is True
    assert board["all_have_sealed_handle_hash"] is True
    assert board["all_have_sealed_artifact_hash"] is True
    assert board["no_raw_file_bytes_json"] is True
    assert board["no_raw_paths_returned"] is True
    assert board["no_raw_file_urls_returned"] is True
    assert board["no_raw_download_tokens_returned"] is True
    assert board["no_public_links_returned"] is True

    for item in board["download_response_envelopes"]:
        assert item["response_state"] == "vault_download_response_envelope_ready_for_tower_hash_only"
        assert item["answered_to"] == "Tower"
        assert item["vault_answered_tower_only"] == 1
        assert len(item["sealed_download_handle_hash"]) == 64
        assert len(item["sealed_download_artifact_hash"]) == 64
        assert item["raw_file_bytes_returned_by_json"] == 0
        assert item["raw_path_returned"] == 0
        assert item["raw_file_url_returned"] == 0
        assert item["raw_download_token_returned"] == 0
        assert item["public_link_returned"] == 0


def test_gp481_490_download_handle_guard_is_hash_only_no_raw_token_public():
    board = get_download_handle_hash_guard_board()

    assert board["ready"] is True
    assert board["handle_guard_count"] >= 2
    assert board["all_handle_hash_only"] is True
    assert board["no_raw_handle_visible"] is True
    assert board["no_raw_download_token_visible"] is True
    assert board["no_public_link_visible"] is True
    assert board["no_raw_file_bytes_visible"] is True
    assert board["all_expire_under_tower_control"] is True

    for item in board["handle_guards"]:
        assert item["guard_state"] == "download_handle_hash_guard_ready_no_raw_token"
        assert item["handle_hash_only"] == 1
        assert item["raw_handle_visible"] == 0
        assert item["raw_download_token_visible"] == 0
        assert item["public_link_visible"] == 0
        assert item["raw_file_bytes_visible"] == 0
        assert item["expires_under_tower_control"] == 1
        assert len(item["handle_guard_hash"]) == 64


def test_gp481_490_download_receipts_are_draft_append_only_no_raw_token_public():
    ledger = get_download_receipt_draft_ledger()

    assert ledger["ready"] is True
    assert ledger["download_receipt_count"] >= 2
    assert ledger["all_receipts_draft"] is True
    assert ledger["all_append_only"] is True
    assert ledger["all_immutable"] is True
    assert ledger["no_raw_file_bytes_receipted"] is True
    assert ledger["no_raw_download_tokens_receipted"] is True
    assert ledger["no_public_links_receipted"] is True

    for item in ledger["download_receipts"]:
        assert item["receipt_state"] == "download_receipt_draft_ready_append_only"
        assert item["receipt_finalized"] == 0
        assert item["append_only"] == 1
        assert item["mutable"] == 0
        assert item["raw_file_bytes_receipted"] == 0
        assert item["raw_download_token_receipted"] == 0
        assert item["public_link_receipted"] == 0
        assert len(item["download_receipt_hash"]) == 64


def test_gp481_490_delivery_preview_returns_tower_workflow_safe_result_only():
    board = get_tower_download_result_delivery_preview_board()

    assert board["ready"] is True
    assert board["download_delivery_preview_count"] >= 2
    assert board["all_delivered_to_tower"] is True
    assert board["all_teller_delivery_allowed_after_tower"] is True
    assert board["no_direct_person_delivery"] is True
    assert board["no_direct_vault_link"] is True
    assert board["no_raw_file_bytes"] is True
    assert board["no_raw_download_tokens"] is True
    assert board["no_public_links"] is True
    assert board["all_workflow_safe_status_ready"] is True

    for item in board["download_delivery_previews"]:
        assert item["delivery_state"] == "tower_download_result_delivery_preview_ready_workflow_safe_hash_only"
        assert item["delivered_to"] == "Tower"
        assert item["teller_delivery_allowed_after_tower"] == 1
        assert item["direct_person_delivery_allowed"] == 0
        assert item["direct_vault_link_included"] == 0
        assert item["raw_file_bytes_included"] == 0
        assert item["raw_download_token_included"] == 0
        assert item["public_link_included"] == 0
        assert item["workflow_safe_status_ready"] == 1
        assert len(item["delivery_preview_hash"]) == 64


def test_gp481_490_safety_blockers_prevent_raw_public_token_and_teller_direct():
    board = get_tower_authorized_download_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "raw_file_bytes_returned_by_json" in blocked_actions
    assert "raw_download_token_exposure" in blocked_actions
    assert "public_download_link" in blocked_actions
    assert "raw_path_or_file_url_exposure" in blocked_actions
    assert "teller_direct_download_from_vault" in blocked_actions
    assert "teller_to_vault_direct_call" in blocked_actions
    assert "proof_protocol_execution" in blocked_actions
    assert "public_vault_dashboard" in blocked_actions
    assert "direct_vault_user_portal" in blocked_actions
    assert "employee_vendor_customer_vault_browsing" in blocked_actions


def test_gp481_490_readiness_declares_next_proof_protocol():
    checkpoint = get_tower_authorized_download_protocol_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_tower_authorized_view_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"]["tower_executes_controlled_download_protocol"] is True
    assert checkpoint["checks"]["download_answers_tower_only"] is True
    assert checkpoint["checks"]["download_exposes_no_raw_token_or_public_link"] is True
    assert checkpoint["checks"]["eligibility_tower_only"] is True
    assert checkpoint["checks"]["internal_requests_tower_to_vault_only"] is True
    assert checkpoint["checks"]["responses_tower_only_hash_envelope"] is True
    assert checkpoint["checks"]["handle_guards_hash_only_no_raw_token_public"] is True
    assert checkpoint["checks"]["delivery_to_tower_then_workflow_safe"] is True
    assert "TOWER AUTHORIZED PROOF PROTOCOL" in checkpoint["next_recommended_layer"]


def test_gp481_490_global_locks_preserve_no_raw_download_exposure():
    assert LOCKS["controlled_download_protocol_metadata_allowed"] is True
    assert LOCKS["tower_internal_vault_download_requests_allowed"] is True
    assert LOCKS["vault_download_response_envelopes_allowed"] is True
    assert LOCKS["download_handle_hash_guards_allowed"] is True

    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_file_bytes_exposed"] is False
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["raw_share_token_exposed"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS["public_download_link_created"] is False
    assert LOCKS["proof_protocol_execution_allowed"] is False
    assert LOCKS["teller_direct_download_allowed"] is False
    assert LOCKS["teller_to_vault_direct_call_allowed"] is False
    assert LOCKS["direct_vault_user_portal_allowed"] is False
    assert LOCKS["public_vault_dashboard_allowed"] is False
    assert LOCKS["employee_vault_browsing_allowed"] is False
    assert LOCKS["external_collaborator_browsing_allowed"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False


def test_gp481_490_routes_are_json_only_no_public_page_route():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/tower-authorized-download-protocol-layer.json",
        "/vault/tower-authorized-download-protocol-shell.json",
        "/vault/download-eligibility-gate-board.json",
        "/vault/download-scope-redaction-gate-board.json",
        "/vault/tower-download-session-draft-board.json",
        "/vault/tower-internal-vault-download-request-ledger.json",
        "/vault/vault-download-response-envelope-board.json",
        "/vault/download-handle-hash-guard-board.json",
        "/vault/download-receipt-draft-ledger.json",
        "/vault/tower-download-result-delivery-preview-board.json",
        "/vault/tower-authorized-download-safety-blocker-board.json",
        "/vault/tower-authorized-download-protocol-readiness-checkpoint.json",
        "/vault/gp481-status.json",
        "/vault/gp490-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert '@app.route("/vault/tower-authorized-download-protocol-layer")' not in app_text
