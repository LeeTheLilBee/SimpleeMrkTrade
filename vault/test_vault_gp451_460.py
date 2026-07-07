
from pathlib import Path

from vault.teller_to_tower_request_handoff_layer_service import (
    DOCTRINE,
    LOCKS,
    get_document_proof_type_scope_board,
    get_requester_role_context_board,
    get_sensitivity_redaction_need_classifier,
    get_teller_to_tower_handoff_safety_blocker_board,
    get_teller_to_tower_request_handoff_home,
    get_teller_to_tower_request_handoff_readiness_checkpoint,
    get_teller_workflow_receipt_draft_ledger,
    get_tower_approval_required_flag_builder,
    get_tower_intake_payload_preview_board,
    get_workflow_request_packet_contract,
    validate_teller_to_tower_request_handoff_layer,
)


def test_gp451_460_readiness_checkpoint_passes():
    result = validate_teller_to_tower_request_handoff_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Teller-to-Tower request handoff layer" in result["readiness_label"]


def test_gp451_460_doctrine_locks_teller_tower_vault_flow():
    home = get_teller_to_tower_request_handoff_home()

    assert home["ready"] is True
    assert home["doctrine"]["tower"] == "face_protocol_authority"
    assert home["doctrine"]["teller"] == "workflow_request_source"
    assert home["doctrine"]["vault"] == "sealed_memory"
    assert home["doctrine"]["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller"
    assert home["doctrine"]["teller_can_create_requests"] is True
    assert home["doctrine"]["teller_can_call_vault_directly"] is False
    assert home["doctrine"]["tower_must_authorize_protocol"] is True
    assert home["doctrine"]["vault_answers_tower_only"] is True


def test_gp451_460_workflow_request_packets_are_addressed_to_tower_only():
    board = get_workflow_request_packet_contract()

    assert board["ready"] is True
    assert board["packet_count"] >= 2
    assert board["all_addressed_to_tower"] is True
    assert board["no_vault_direct_request"] is True
    assert board["all_tower_approval_required"] is True

    allowed_workflows = {
        "employee_document_request",
        "vendor_document_request",
        "payroll_proof_request",
        "onboarding_packet_request",
        "agreement_proof_request",
        "payment_receipt_request",
    }

    for item in board["request_packets"]:
        assert item["workflow_type"] in allowed_workflows
        assert item["addressed_to"] == "Tower"
        assert item["vault_direct_request_allowed"] == 0
        assert item["tower_approval_required"] == 1
        assert len(item["packet_hash"]) == 64


def test_gp451_460_requester_role_context_requires_tower_checks():
    board = get_requester_role_context_board()

    assert board["ready"] is True
    assert board["role_context_count"] >= 2
    assert board["all_tower_identity_check_required"] is True
    assert board["all_tower_permission_check_required"] is True
    assert board["no_teller_self_approval"] is True
    assert board["no_vault_direct_approval"] is True

    for item in board["role_contexts"]:
        assert item["role_context_state"] == "requester_role_context_ready_for_tower_review"
        assert item["tower_identity_check_required"] == 1
        assert item["tower_permission_check_required"] == 1
        assert item["teller_can_self_approve"] == 0
        assert item["vault_direct_approval_allowed"] == 0


def test_gp451_460_document_scope_requires_tower_protocol_no_vault_direct_raw_public():
    board = get_document_proof_type_scope_board()

    assert board["ready"] is True
    assert board["scope_count"] >= 2
    assert board["all_tower_protocol_required"] is True
    assert board["no_vault_direct_access"] is True
    assert board["no_raw_file_bytes_allowed"] is True
    assert board["no_public_links_allowed"] is True

    allowed_protocols = {
        "status_protocol",
        "proof_protocol",
        "receipt_protocol",
        "view_protocol",
        "download_protocol",
    }

    for item in board["scopes"]:
        assert item["scope_state"] == "document_proof_scope_ready_for_tower_protocol_gate"
        assert item["tower_protocol_required"] in allowed_protocols
        assert item["vault_direct_access_allowed"] == 0
        assert item["raw_file_bytes_allowed"] == 0
        assert item["public_link_allowed"] == 0


def test_gp451_460_sensitivity_classifier_redacts_raw_path_url_token_public_direct():
    board = get_sensitivity_redaction_need_classifier()

    assert board["ready"] is True
    assert board["classifier_count"] >= 2
    assert board["all_redaction_required"] is True
    assert board["all_raw_file_bytes_redacted"] is True
    assert board["all_raw_paths_redacted"] is True
    assert board["all_raw_file_urls_redacted"] is True
    assert board["all_raw_tokens_redacted"] is True
    assert board["all_public_links_redacted"] is True
    assert board["all_direct_browse_redacted"] is True

    for item in board["classifiers"]:
        assert item["classifier_state"] == "sensitivity_redaction_classified_for_tower"
        assert item["redaction_required"] == 1
        assert item["raw_file_bytes_redacted"] == 1
        assert item["raw_path_redacted"] == 1
        assert item["raw_file_url_redacted"] == 1
        assert item["raw_token_redacted"] == 1
        assert item["public_link_redacted"] == 1
        assert item["direct_browse_redacted"] == 1


def test_gp451_460_tower_approval_flags_are_required_before_vault_protocol():
    board = get_tower_approval_required_flag_builder()

    assert board["ready"] is True
    assert board["approval_flag_count"] >= 2
    assert board["all_tower_approval_required"] is True
    assert board["all_tower_permission_required"] is True
    assert board["all_tower_protocol_gate_required"] is True
    assert board["no_teller_to_vault_direct_call"] is True

    for item in board["approval_flags"]:
        assert item["approval_state"] == "tower_approval_required_before_vault_protocol"
        assert item["tower_approval_required"] == 1
        assert item["tower_permission_required"] == 1
        assert item["tower_protocol_gate_required"] == 1
        assert item["teller_to_vault_direct_call_allowed"] == 0


def test_gp451_460_teller_workflow_receipts_are_draft_append_only_and_require_tower_and_vault_receipts():
    ledger = get_teller_workflow_receipt_draft_ledger()

    assert ledger["ready"] is True
    assert ledger["receipt_draft_count"] >= 2
    assert ledger["all_receipts_draft"] is True
    assert ledger["all_tower_receipts_required"] is True
    assert ledger["all_vault_service_receipts_required"] is True
    assert ledger["all_append_only"] is True
    assert ledger["all_immutable"] is True

    for item in ledger["receipt_drafts"]:
        assert item["receipt_state"] == "teller_workflow_receipt_draft_ready_for_tower_intake"
        assert item["receipt_finalized"] == 0
        assert item["tower_receipt_required"] == 1
        assert item["vault_service_receipt_required"] == 1
        assert item["append_only"] == 1
        assert item["mutable"] == 0
        assert len(item["receipt_hash"]) == 64


def test_gp451_460_tower_intake_preview_is_tower_only_and_not_vault_ready_yet():
    board = get_tower_intake_payload_preview_board()

    assert board["ready"] is True
    assert board["intake_preview_count"] >= 2
    assert board["all_addressed_to_tower"] is True
    assert board["all_tower_intake_ready"] is True
    assert board["all_vault_request_not_ready_yet"] is True
    assert board["all_tower_protocol_pending"] is True
    assert board["all_preview_only"] is True
    assert board["no_raw_file_bytes"] is True
    assert board["no_raw_paths"] is True
    assert board["no_public_links"] is True

    for item in board["intake_previews"]:
        assert item["preview_state"] == "tower_intake_payload_preview_ready_no_vault_call"
        assert item["addressed_to"] == "Tower"
        assert item["tower_intake_ready"] == 1
        assert item["vault_request_ready"] == 0
        assert item["tower_protocol_pending"] == 1
        assert item["payload_preview_only"] == 1
        assert item["raw_file_bytes_included"] == 0
        assert item["raw_path_included"] == 0
        assert item["public_link_included"] == 0
        assert len(item["intake_payload_hash"]) == 64


def test_gp451_460_safety_blockers_prevent_teller_direct_vault_and_public_behavior():
    board = get_teller_to_tower_handoff_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "teller_to_vault_direct_call" in blocked_actions
    assert "teller_direct_download_from_vault" in blocked_actions
    assert "teller_direct_view_from_vault" in blocked_actions
    assert "teller_direct_proof_call_to_vault" in blocked_actions
    assert "public_vault_dashboard" in blocked_actions
    assert "direct_vault_user_portal" in blocked_actions
    assert "employee_vendor_customer_vault_browsing" in blocked_actions
    assert "public_links_or_raw_urls" in blocked_actions
    assert "raw_file_bytes_json" in blocked_actions
    assert "view_download_proof_protocol_execution" in blocked_actions


def test_gp451_460_readiness_declares_next_tower_protocol_gate():
    checkpoint = get_teller_to_tower_request_handoff_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_headless_tower_status_bridge_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"]["teller_cannot_call_vault_directly"] is True
    assert checkpoint["checks"]["tower_must_authorize_protocol"] is True
    assert checkpoint["checks"]["vault_answers_tower_only"] is True
    assert checkpoint["checks"]["packets_addressed_to_tower_only"] is True
    assert checkpoint["checks"]["scope_requires_tower_protocol"] is True
    assert checkpoint["checks"]["approval_no_teller_to_vault_direct_call"] is True
    assert checkpoint["checks"]["intake_addressed_to_tower_and_protocol_pending"] is True
    assert "TOWER VAULT REQUEST PROTOCOL GATE" in checkpoint["next_recommended_layer"]


def test_gp451_460_global_locks_preserve_no_teller_to_vault():
    assert LOCKS["workflow_request_packet_creation_allowed"] is True
    assert LOCKS["tower_addressed_handoff_allowed"] is True

    assert LOCKS["teller_to_vault_direct_call_allowed"] is False
    assert LOCKS["vault_direct_request_from_teller_allowed"] is False
    assert LOCKS["vault_direct_approval_from_teller_allowed"] is False
    assert LOCKS["view_protocol_execution_allowed"] is False
    assert LOCKS["download_protocol_execution_allowed"] is False
    assert LOCKS["proof_protocol_execution_allowed"] is False
    assert LOCKS["public_vault_dashboard_allowed"] is False
    assert LOCKS["direct_vault_user_portal_allowed"] is False
    assert LOCKS["employee_vault_browsing_allowed"] is False
    assert LOCKS["vendor_vault_browsing_allowed"] is False
    assert LOCKS["customer_vault_browsing_allowed"] is False
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


def test_gp451_460_routes_are_json_only_no_public_page_route():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/teller-to-tower-request-handoff-layer.json",
        "/vault/teller-to-tower-request-handoff-shell.json",
        "/vault/workflow-request-packet-contract.json",
        "/vault/requester-role-context-board.json",
        "/vault/document-proof-type-scope-board.json",
        "/vault/sensitivity-redaction-need-classifier.json",
        "/vault/tower-approval-required-flag-builder.json",
        "/vault/teller-workflow-receipt-draft-ledger.json",
        "/vault/tower-intake-payload-preview-board.json",
        "/vault/teller-to-tower-handoff-safety-blocker-board.json",
        "/vault/teller-to-tower-request-handoff-readiness-checkpoint.json",
        "/vault/gp451-status.json",
        "/vault/gp460-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert '@app.route("/vault/teller-to-tower-request-handoff-layer")' not in app_text
