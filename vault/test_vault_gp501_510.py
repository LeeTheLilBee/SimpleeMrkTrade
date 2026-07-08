
from pathlib import Path

from vault.tower_protocol_receipt_closeout_layer_service import (
    DOCTRINE,
    LOCKS,
    get_protocol_denial_redaction_closeout_board,
    get_receipt_chain_integrity_hash_board,
    get_request_to_protocol_receipt_chain_board,
    get_teller_workflow_safe_return_receipt_board,
    get_tower_final_protocol_receipt_builder,
    get_tower_protocol_receipt_closeout_home,
    get_tower_protocol_receipt_closeout_readiness_checkpoint,
    get_tower_protocol_receipt_closeout_safety_blocker_board,
    get_vault_service_receipt_verification_board,
    get_view_download_proof_receipt_linker,
    validate_tower_protocol_receipt_closeout_layer,
)


def test_gp501_510_readiness_checkpoint_passes():
    result = validate_tower_protocol_receipt_closeout_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Tower protocol receipt closeout layer" in result["readiness_label"]


def test_gp501_510_doctrine_closes_receipts_without_new_access():
    home = get_tower_protocol_receipt_closeout_home()

    assert home["ready"] is True
    assert home["doctrine"]["tower"] == "face_protocol_authority"
    assert home["doctrine"]["teller"] == "workflow_request_source"
    assert home["doctrine"]["vault"] == "sealed_memory"
    assert home["doctrine"]["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller"
    assert home["doctrine"]["tower_closes_protocol_receipts"] is True
    assert home["doctrine"]["teller_receives_workflow_safe_return_only"] is True
    assert home["doctrine"]["vault_answers_tower_only"] is True
    assert home["doctrine"]["teller_can_call_vault_directly"] is False
    assert home["doctrine"]["receipt_closeout_creates_new_access"] is False
    assert home["doctrine"]["receipt_closeout_returns_raw_files"] is False
    assert home["doctrine"]["receipt_closeout_creates_public_links"] is False


def test_gp501_510_request_to_protocol_receipt_chains_are_closed_append_only():
    board = get_request_to_protocol_receipt_chain_board()

    assert board["ready"] is True
    assert board["chain_count"] >= 2
    assert board["all_chains_closed"] is True
    assert board["all_have_chain_hash"] is True
    assert board["all_append_only"] is True
    assert board["all_immutable"] is True

    for item in board["receipt_chains"]:
        assert item["chain_state"] == "request_to_protocol_receipt_chain_closed"
        assert len(item["teller_receipt_hash"]) == 64
        assert len(item["tower_protocol_receipt_hash"]) == 64
        assert len(item["view_redaction_receipt_hash"]) == 64
        assert len(item["download_receipt_hash"]) == 64
        assert len(item["proof_receipt_hash"]) == 64
        assert len(item["chain_hash"]) == 64
        assert item["append_only"] == 1
        assert item["mutable"] == 0


def test_gp501_510_view_download_proof_linker_has_no_raw_path_token_public():
    board = get_view_download_proof_receipt_linker()

    assert board["ready"] is True
    assert board["linker_count"] >= 2
    assert board["all_protocol_receipts_present"] is True
    assert board["no_raw_file_bytes_linked"] is True
    assert board["no_raw_paths_linked"] is True
    assert board["no_raw_tokens_linked"] is True
    assert board["no_public_links_linked"] is True

    for item in board["receipt_linkers"]:
        assert item["linker_state"] == "view_download_proof_receipts_linked_hash_only"
        assert item["all_protocol_receipts_present"] == 1
        assert len(item["view_redaction_receipt_hash"]) == 64
        assert len(item["download_receipt_hash"]) == 64
        assert len(item["proof_receipt_hash"]) == 64
        assert len(item["proof_packet_hash"]) == 64
        assert item["raw_file_bytes_linked"] == 0
        assert item["raw_path_linked"] == 0
        assert item["raw_token_linked"] == 0
        assert item["public_link_linked"] == 0


def test_gp501_510_final_protocol_receipts_are_finalized_hash_only():
    board = get_tower_final_protocol_receipt_builder()

    assert board["ready"] is True
    assert board["final_receipt_count"] >= 2
    assert board["all_finalized"] is True
    assert board["all_append_only"] is True
    assert board["all_immutable"] is True
    assert board["all_have_final_receipt_hash"] is True
    assert board["no_raw_file_bytes"] is True
    assert board["no_raw_paths"] is True
    assert board["no_raw_tokens"] is True
    assert board["no_public_links"] is True

    for item in board["final_protocol_receipts"]:
        assert item["final_receipt_state"] == "tower_final_protocol_receipt_closed_hash_only"
        assert item["finalized"] == 1
        assert item["append_only"] == 1
        assert item["mutable"] == 0
        assert len(item["final_protocol_receipt_hash"]) == 64
        assert len(item["chain_hash"]) == 64
        assert len(item["proof_packet_hash"]) == 64
        assert len(item["proof_integrity_hash"]) == 64
        assert item["raw_file_bytes_included"] == 0
        assert item["raw_path_included"] == 0
        assert item["raw_token_included"] == 0
        assert item["public_link_included"] == 0


def test_gp501_510_vault_service_receipts_are_verified_tower_only():
    board = get_vault_service_receipt_verification_board()

    assert board["ready"] is True
    assert board["verification_count"] >= 2
    assert board["all_vault_answered_tower_only"] is True
    assert board["all_service_receipts_verified"] is True
    assert board["all_proof_integrity_verified"] is True
    assert board["all_raw_file_bytes_absent"] is True
    assert board["all_public_links_absent"] is True

    for item in board["service_receipt_verifications"]:
        assert item["verification_state"] == "vault_service_receipts_verified_tower_only"
        assert len(item["proof_response_hash"]) == 64
        assert len(item["proof_integrity_hash"]) == 64
        assert len(item["sealed_download_artifact_hash"]) == 64
        assert len(item["handle_guard_hash"]) == 64
        assert item["vault_answered_tower_only"] == 1
        assert item["service_receipts_verified"] == 1
        assert item["proof_integrity_verified"] == 1
        assert item["raw_file_bytes_verified_absent"] == 1
        assert item["public_links_verified_absent"] == 1


def test_gp501_510_teller_workflow_safe_returns_include_no_direct_vault_raw_token_public():
    board = get_teller_workflow_safe_return_receipt_board()

    assert board["ready"] is True
    assert board["return_receipt_count"] >= 2
    assert board["all_returned_to_teller"] is True
    assert board["all_workflow_safe_output_ready"] is True
    assert board["all_teller_delivery_allowed_after_tower"] is True
    assert board["no_direct_vault_access"] is True
    assert board["no_raw_file_bytes"] is True
    assert board["no_raw_paths"] is True
    assert board["no_raw_tokens"] is True
    assert board["no_public_links"] is True

    for item in board["return_receipts"]:
        assert item["return_state"] == "teller_workflow_safe_return_receipt_ready_from_tower"
        assert item["returned_to"] == "Teller"
        assert item["workflow_safe_output_ready"] == 1
        assert item["teller_delivery_allowed_after_tower"] == 1
        assert item["direct_vault_access_included"] == 0
        assert item["raw_file_bytes_included"] == 0
        assert item["raw_path_included"] == 0
        assert item["raw_token_included"] == 0
        assert item["public_link_included"] == 0
        assert len(item["return_receipt_hash"]) == 64


def test_gp501_510_denial_redaction_closeouts_block_direct_raw_public():
    board = get_protocol_denial_redaction_closeout_board()

    assert board["ready"] is True
    assert board["denial_closeout_count"] >= 2
    assert board["all_closeouts_complete"] is True
    assert board["all_direct_teller_vault_access_denied"] is True
    assert board["all_public_links_denied"] is True
    assert board["all_raw_file_bytes_denied"] is True
    assert board["all_raw_paths_denied"] is True
    assert board["all_raw_tokens_denied"] is True
    assert board["all_direct_vault_portal_denied"] is True

    for item in board["denial_redaction_closeouts"]:
        assert item["closeout_state"] == "protocol_denial_redaction_closeout_complete"
        assert item["denied_direct_teller_vault_access"] == 1
        assert item["denied_public_links"] == 1
        assert item["denied_raw_file_bytes"] == 1
        assert item["denied_raw_paths"] == 1
        assert item["denied_raw_tokens"] == 1
        assert item["denied_direct_vault_portal"] == 1
        assert len(item["redaction_closeout_hash"]) == 64


def test_gp501_510_integrity_hashes_are_closed_append_only():
    board = get_receipt_chain_integrity_hash_board()

    assert board["ready"] is True
    assert board["integrity_hash_count"] >= 2
    assert board["all_integrity_closed"] is True
    assert board["all_have_integrity_hash"] is True
    assert board["all_append_only"] is True
    assert board["all_immutable"] is True

    for item in board["integrity_hashes"]:
        assert item["integrity_state"] == "receipt_chain_integrity_hash_closed"
        assert len(item["chain_hash"]) == 64
        assert len(item["final_protocol_receipt_hash"]) == 64
        assert len(item["return_receipt_hash"]) == 64
        assert len(item["redaction_closeout_hash"]) == 64
        assert len(item["receipt_chain_integrity_hash"]) == 64
        assert item["append_only"] == 1
        assert item["mutable"] == 0


def test_gp501_510_safety_blockers_prevent_new_access_raw_public_token_and_teller_direct():
    board = get_tower_protocol_receipt_closeout_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "new_access_surface_creation" in blocked_actions
    assert "teller_to_vault_direct_call" in blocked_actions
    assert "teller_direct_download_or_proof" in blocked_actions
    assert "raw_file_bytes_returned_by_json" in blocked_actions
    assert "raw_download_token_exposure" in blocked_actions
    assert "public_view_download_or_proof_link" in blocked_actions
    assert "raw_path_or_file_url_exposure" in blocked_actions
    assert "public_vault_dashboard" in blocked_actions
    assert "direct_vault_user_portal" in blocked_actions
    assert "employee_vendor_customer_vault_browsing" in blocked_actions


def test_gp501_510_readiness_declares_next_recovery_safe_rebuild_prep():
    checkpoint = get_tower_protocol_receipt_closeout_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_tower_authorized_proof_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"]["tower_closes_receipts"] is True
    assert checkpoint["checks"]["teller_receives_safe_return_only"] is True
    assert checkpoint["checks"]["vault_answers_tower_only"] is True
    assert checkpoint["checks"]["closeout_creates_no_access_raw_public"] is True
    assert checkpoint["checks"]["receipt_chains_closed_append_only"] is True
    assert checkpoint["checks"]["workflow_safe_returns_to_teller_only"] is True
    assert checkpoint["checks"]["denial_redaction_blocks_direct_raw_public"] is True
    assert "RECOVERY SAFE REBUILD EXECUTION PREP" in checkpoint["next_recommended_layer"]
    assert "GP451-GP510" in checkpoint["closed_corridor"]


def test_gp501_510_global_locks_preserve_receipt_only_no_new_access():
    assert LOCKS["tower_protocol_receipt_closeout_layer"] is True
    assert LOCKS["request_to_protocol_receipt_chain_allowed"] is True
    assert LOCKS["tower_final_protocol_receipt_allowed"] is True
    assert LOCKS["receipt_chain_integrity_hash_allowed"] is True

    assert LOCKS["new_access_surface_created"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_file_bytes_exposed"] is False
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["raw_share_token_exposed"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS["public_proof_link_created"] is False
    assert LOCKS["teller_direct_proof_allowed"] is False
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


def test_gp501_510_routes_are_json_only_no_public_page_route():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/tower-protocol-receipt-closeout-layer.json",
        "/vault/tower-protocol-receipt-closeout-shell.json",
        "/vault/request-to-protocol-receipt-chain-board.json",
        "/vault/view-download-proof-receipt-linker.json",
        "/vault/tower-final-protocol-receipt-builder.json",
        "/vault/vault-service-receipt-verification-board.json",
        "/vault/teller-workflow-safe-return-receipt-board.json",
        "/vault/protocol-denial-redaction-closeout-board.json",
        "/vault/receipt-chain-integrity-hash-board.json",
        "/vault/tower-protocol-receipt-closeout-safety-blocker-board.json",
        "/vault/tower-protocol-receipt-closeout-readiness-checkpoint.json",
        "/vault/gp501-status.json",
        "/vault/gp510-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert '@app.route("/vault/tower-protocol-receipt-closeout-layer")' not in app_text
