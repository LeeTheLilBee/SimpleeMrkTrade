
from pathlib import Path

from vault.tower_authorized_view_protocol_layer_service import (
    DOCTRINE,
    LOCKS,
    get_redacted_view_projection_builder,
    get_tower_authorized_view_protocol_home,
    get_tower_authorized_view_protocol_readiness_checkpoint,
    get_tower_authorized_view_safety_blocker_board,
    get_tower_internal_vault_view_request_ledger,
    get_tower_view_result_delivery_preview_board,
    get_tower_view_session_draft_board,
    get_vault_view_response_envelope_board,
    get_view_eligibility_gate_board,
    get_view_redaction_receipt_draft_ledger,
    validate_tower_authorized_view_protocol_layer,
)


def test_gp471_480_readiness_checkpoint_passes():
    result = validate_tower_authorized_view_protocol_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Tower authorized view protocol layer" in result["readiness_label"]


def test_gp471_480_doctrine_locks_controlled_view_only():
    home = get_tower_authorized_view_protocol_home()

    assert home["ready"] is True
    assert home["doctrine"]["tower"] == "face_protocol_authority"
    assert home["doctrine"]["teller"] == "workflow_request_source"
    assert home["doctrine"]["vault"] == "sealed_memory"
    assert home["doctrine"]["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller"
    assert home["doctrine"]["tower_executes_controlled_view_protocol"] is True
    assert home["doctrine"]["view_protocol_answers_tower_only"] is True
    assert home["doctrine"]["teller_can_call_vault_directly"] is False
    assert home["doctrine"]["vault_answers_tower_only"] is True
    assert home["doctrine"]["raw_file_bytes_exposed_by_view"] is False
    assert home["doctrine"]["public_link_created_by_view"] is False


def test_gp471_480_view_eligibility_is_tower_only_and_view_only():
    board = get_view_eligibility_gate_board()

    assert board["ready"] is True
    assert board["view_eligibility_count"] >= 2
    assert board["all_tower_is_requester"] is True
    assert board["no_teller_is_requester"] is True
    assert board["all_tower_identity_permission_passed"] is True
    assert board["all_tower_approval_recorded"] is True
    assert board["all_view_protocol_allowed"] is True
    assert board["no_download_protocol_allowed"] is True
    assert board["no_proof_protocol_allowed"] is True
    assert board["no_raw_file_view"] is True
    assert board["no_public_view_link"] is True

    for item in board["view_eligibility_gates"]:
        assert item["gate_state"] == "view_eligibility_gate_passed_for_tower_only"
        assert item["tower_is_requester"] == 1
        assert item["teller_is_requester"] == 0
        assert item["view_protocol_allowed"] == 1
        assert item["download_protocol_allowed"] == 0
        assert item["proof_protocol_allowed"] == 0
        assert item["raw_file_view_allowed"] == 0
        assert item["public_view_link_allowed"] == 0


def test_gp471_480_redacted_view_projection_has_no_raw_path_url_token_public_direct():
    board = get_redacted_view_projection_builder()

    assert board["ready"] is True
    assert board["projection_count"] >= 2
    assert board["all_redacted_for_tower"] is True
    assert board["no_raw_file_bytes"] is True
    assert board["no_raw_paths"] is True
    assert board["no_raw_file_urls"] is True
    assert board["no_raw_tokens"] is True
    assert board["no_public_links"] is True
    assert board["no_direct_browse"] is True

    for item in board["view_projections"]:
        assert item["projection_state"] == "redacted_view_projection_ready_for_tower"
        assert item["projection_type"] == "redacted_tower_view_projection"
        assert item["raw_file_bytes_included"] == 0
        assert item["raw_path_included"] == 0
        assert item["raw_file_url_included"] == 0
        assert item["raw_token_included"] == 0
        assert item["public_link_included"] == 0
        assert item["direct_browse_included"] == 0
        assert len(item["projection_hash"]) == 64


def test_gp471_480_tower_view_sessions_are_internal_only():
    board = get_tower_view_session_draft_board()

    assert board["ready"] is True
    assert board["view_session_count"] >= 2
    assert board["all_session_owner_tower"] is True
    assert board["all_tower_session_required"] is True
    assert board["no_teller_session"] is True
    assert board["no_direct_vault_session"] is True
    assert board["no_public_session"] is True
    assert board["all_expire_without_public_link"] is True

    for item in board["view_sessions"]:
        assert item["session_state"] == "tower_view_session_draft_ready_internal_only"
        assert item["session_owner"] == "Tower"
        assert item["tower_session_required"] == 1
        assert item["teller_session_allowed"] == 0
        assert item["direct_vault_session_allowed"] == 0
        assert item["public_session_allowed"] == 0
        assert item["expires_without_public_link"] == 1


def test_gp471_480_internal_view_requests_are_tower_to_vault_only_no_raw_public():
    ledger = get_tower_internal_vault_view_request_ledger()

    assert ledger["ready"] is True
    assert ledger["internal_view_request_count"] >= 2
    assert ledger["all_from_tower_to_vault"] is True
    assert ledger["all_vault_answer_target_tower"] is True
    assert ledger["all_internal_view_calls_sent"] is True
    assert ledger["no_teller_calls_sent"] is True
    assert ledger["no_raw_file_bytes_requested"] is True
    assert ledger["no_raw_paths_requested"] is True
    assert ledger["no_public_links_requested"] is True

    for item in ledger["internal_view_requests"]:
        assert item["request_state"] == "tower_internal_vault_view_request_sent_controlled"
        assert item["from_service"] == "Tower"
        assert item["to_service"] == "Vault"
        assert item["vault_answer_target"] == "Tower"
        assert item["internal_vault_view_call_sent"] == 1
        assert item["teller_call_sent"] == 0
        assert item["raw_file_bytes_requested"] == 0
        assert item["raw_path_requested"] == 0
        assert item["public_link_requested"] == 0
        assert len(item["internal_request_hash"]) == 64


def test_gp471_480_vault_view_response_answers_tower_only_with_redacted_envelope():
    board = get_vault_view_response_envelope_board()

    assert board["ready"] is True
    assert board["view_response_count"] >= 2
    assert board["all_answered_to_tower"] is True
    assert board["all_vault_answered_tower_only"] is True
    assert board["all_redacted_view_payload_ready"] is True
    assert board["no_raw_file_bytes_returned"] is True
    assert board["no_raw_paths_returned"] is True
    assert board["no_raw_file_urls_returned"] is True
    assert board["no_raw_tokens_returned"] is True
    assert board["no_public_links_returned"] is True

    for item in board["view_response_envelopes"]:
        assert item["response_state"] == "vault_view_response_envelope_ready_for_tower"
        assert item["answered_to"] == "Tower"
        assert item["vault_answered_tower_only"] == 1
        assert item["redacted_view_payload_ready"] == 1
        assert item["raw_file_bytes_returned"] == 0
        assert item["raw_path_returned"] == 0
        assert item["raw_file_url_returned"] == 0
        assert item["raw_token_returned"] == 0
        assert item["public_link_returned"] == 0
        assert len(item["response_envelope_hash"]) == 64


def test_gp471_480_view_redaction_receipts_are_draft_append_only_no_raw_public():
    ledger = get_view_redaction_receipt_draft_ledger()

    assert ledger["ready"] is True
    assert ledger["view_receipt_count"] >= 2
    assert ledger["all_receipts_draft"] is True
    assert ledger["all_append_only"] is True
    assert ledger["all_immutable"] is True
    assert ledger["no_raw_file_bytes_receipted"] is True
    assert ledger["no_public_links_receipted"] is True

    for item in ledger["view_receipts"]:
        assert item["receipt_state"] == "view_redaction_receipt_draft_ready_append_only"
        assert item["receipt_finalized"] == 0
        assert item["append_only"] == 1
        assert item["mutable"] == 0
        assert item["raw_file_bytes_receipted"] == 0
        assert item["public_link_receipted"] == 0
        assert len(item["redaction_receipt_hash"]) == 64


def test_gp471_480_delivery_preview_returns_tower_workflow_safe_result_only():
    board = get_tower_view_result_delivery_preview_board()

    assert board["ready"] is True
    assert board["delivery_preview_count"] >= 2
    assert board["all_delivered_to_tower"] is True
    assert board["all_teller_delivery_allowed_after_tower"] is True
    assert board["no_direct_person_delivery"] is True
    assert board["no_direct_vault_link"] is True
    assert board["no_raw_file_bytes"] is True
    assert board["no_public_links"] is True
    assert board["all_workflow_safe_status_ready"] is True

    for item in board["delivery_previews"]:
        assert item["delivery_state"] == "tower_view_result_delivery_preview_ready_workflow_safe"
        assert item["delivered_to"] == "Tower"
        assert item["teller_delivery_allowed"] == 1
        assert item["direct_person_delivery_allowed"] == 0
        assert item["direct_vault_link_included"] == 0
        assert item["raw_file_bytes_included"] == 0
        assert item["public_link_included"] == 0
        assert item["workflow_safe_status_ready"] == 1
        assert len(item["delivery_preview_hash"]) == 64


def test_gp471_480_safety_blockers_prevent_download_proof_public_raw_and_teller_direct():
    board = get_tower_authorized_view_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "download_protocol_execution" in blocked_actions
    assert "proof_protocol_execution" in blocked_actions
    assert "teller_to_vault_direct_call" in blocked_actions
    assert "teller_direct_view_from_vault" in blocked_actions
    assert "public_vault_dashboard" in blocked_actions
    assert "direct_vault_user_portal" in blocked_actions
    assert "employee_vendor_customer_vault_browsing" in blocked_actions
    assert "public_links_or_raw_urls" in blocked_actions
    assert "raw_file_bytes_json" in blocked_actions
    assert "raw_path_or_token_exposure" in blocked_actions


def test_gp471_480_readiness_declares_next_download_protocol():
    checkpoint = get_tower_authorized_view_protocol_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_tower_protocol_gate_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"]["tower_executes_controlled_view_protocol"] is True
    assert checkpoint["checks"]["view_answers_tower_only"] is True
    assert checkpoint["checks"]["view_exposes_no_raw_or_public_link"] is True
    assert checkpoint["checks"]["eligibility_tower_only"] is True
    assert checkpoint["checks"]["internal_requests_tower_to_vault_only"] is True
    assert checkpoint["checks"]["responses_tower_only_redacted"] is True
    assert checkpoint["checks"]["delivery_to_tower_then_workflow_safe"] is True
    assert "TOWER AUTHORIZED DOWNLOAD PROTOCOL" in checkpoint["next_recommended_layer"]


def test_gp471_480_global_locks_allow_only_controlled_view_protocol():
    assert LOCKS["controlled_view_protocol_execution_allowed"] is True
    assert LOCKS["tower_internal_vault_view_requests_allowed"] is True
    assert LOCKS["vault_view_response_envelopes_allowed"] is True

    assert LOCKS["download_protocol_execution_allowed"] is False
    assert LOCKS["proof_protocol_execution_allowed"] is False
    assert LOCKS["public_view_link_allowed"] is False
    assert LOCKS["raw_file_view_allowed"] is False
    assert LOCKS["teller_to_vault_direct_call_allowed"] is False
    assert LOCKS["direct_vault_user_portal_allowed"] is False
    assert LOCKS["public_vault_dashboard_allowed"] is False
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


def test_gp471_480_routes_are_json_only_no_public_page_route():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/tower-authorized-view-protocol-layer.json",
        "/vault/tower-authorized-view-protocol-shell.json",
        "/vault/view-eligibility-gate-board.json",
        "/vault/redacted-view-projection-builder.json",
        "/vault/tower-view-session-draft-board.json",
        "/vault/tower-internal-vault-view-request-ledger.json",
        "/vault/vault-view-response-envelope-board.json",
        "/vault/view-redaction-receipt-draft-ledger.json",
        "/vault/tower-view-result-delivery-preview-board.json",
        "/vault/tower-authorized-view-safety-blocker-board.json",
        "/vault/tower-authorized-view-protocol-readiness-checkpoint.json",
        "/vault/gp471-status.json",
        "/vault/gp480-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert '@app.route("/vault/tower-authorized-view-protocol-layer")' not in app_text
