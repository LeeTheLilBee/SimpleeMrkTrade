
from pathlib import Path

from vault.headless_tower_status_bridge_layer_service import (
    DOCTRINE,
    LOCKS,
    get_headless_bridge_safety_blocker_board,
    get_headless_tower_status_bridge_home,
    get_headless_tower_status_bridge_readiness_checkpoint,
    get_sealed_rebuild_status_output_builder,
    get_teller_workflow_proof_status_bridge,
    get_tower_owner_clearance_status_bridge,
    get_tower_security_receipt_summary_board,
    get_tower_teller_bridge_redaction_contract,
    get_tower_vault_health_card_contract,
    get_vault_memory_integrity_signal_builder,
    validate_headless_tower_status_bridge_layer,
)


def test_gp441_450_readiness_checkpoint_passes():
    result = validate_headless_tower_status_bridge_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Headless Tower status bridge layer" in result["readiness_label"]


def test_gp441_450_doctrine_is_headless_tower_status_bridge_only():
    home = get_headless_tower_status_bridge_home()

    assert home["ready"] is True
    assert home["doctrine"]["tower"] == "face"
    assert home["doctrine"]["teller"] == "workflow"
    assert home["doctrine"]["vault"] == "sealed_memory"
    assert home["doctrine"]["bridge_behavior"] == "headless_internal_status_bridge_only"
    assert home["doctrine"]["people_enter_vault_directly"] is False
    assert home["doctrine"]["vault_is_public_dashboard"] is False
    assert home["doctrine"]["vault_is_direct_user_portal"] is False
    assert home["doctrine"]["bridge_outputs_are_redacted"] is True


def test_gp441_450_tower_health_cards_are_redacted_no_portal_dashboard_raw():
    board = get_tower_vault_health_card_contract()

    assert board["ready"] is True
    assert board["health_card_count"] >= 2
    assert board["all_vault_ready"] is True
    assert board["all_sealed_memory_ready"] is True
    assert board["all_rebuild_preview_ready"] is True
    assert board["all_tower_face_required"] is True
    assert board["all_teller_workflow_required"] is True
    assert board["no_direct_vault_portal"] is True
    assert board["no_public_dashboard"] is True
    assert board["no_raw_file_bytes_json"] is True

    for item in board["health_cards"]:
        assert item["health_state"] == "tower_vault_health_card_ready_redacted"
        assert item["vault_ready"] == 1
        assert item["sealed_memory_ready"] == 1
        assert item["rebuild_preview_ready"] == 1
        assert item["tower_face_required"] == 1
        assert item["teller_workflow_required"] == 1
        assert item["direct_vault_portal_allowed"] == 0
        assert item["public_dashboard_allowed"] == 0
        assert item["raw_file_bytes_json_allowed"] == 0
        assert len(item["health_hash"]) == 64


def test_gp441_450_tower_security_receipts_are_hash_only():
    board = get_tower_security_receipt_summary_board()

    assert board["ready"] is True
    assert board["receipt_summary_count"] >= 2
    assert board["all_hash_only"] is True
    assert board["no_raw_receipt_body"] is True
    assert board["no_raw_paths"] is True
    assert board["no_raw_urls"] is True
    assert board["no_raw_tokens"] is True

    for item in board["receipt_summaries"]:
        assert item["receipt_summary_state"] == "tower_security_receipt_summary_ready_hash_only"
        assert len(item["redacted_receipt_hash"]) == 64
        assert item["raw_receipt_body_included"] == 0
        assert item["raw_path_included"] == 0
        assert item["raw_url_included"] == 0
        assert item["raw_token_included"] == 0


def test_gp441_450_tower_clearance_requires_owner_step_up_and_no_vault_direct_approval():
    board = get_tower_owner_clearance_status_bridge()

    assert board["ready"] is True
    assert board["clearance_status_count"] >= 2
    assert board["all_owner_admin_required"] is True
    assert board["all_step_up_required"] is True
    assert board["all_tower_permission_required"] is True
    assert board["no_vault_direct_approval"] is True
    assert board["no_direct_user_portal"] is True

    for item in board["clearance_status_rows"]:
        assert item["clearance_state"] == "tower_owner_clearance_required_for_sensitive_vault_actions"
        assert item["owner_admin_required"] == 1
        assert item["step_up_required"] == 1
        assert item["tower_permission_required"] == 1
        assert item["vault_direct_approval_allowed"] == 0
        assert item["direct_user_portal_allowed"] == 0


def test_gp441_450_teller_workflow_proof_status_has_hashes_no_browse_raw_or_links():
    board = get_teller_workflow_proof_status_bridge()

    assert board["ready"] is True
    assert board["proof_status_count"] >= 2
    assert board["all_teller_workflow_required"] is True
    assert board["all_document_request_status_allowed"] is True
    assert board["all_proof_hash_allowed"] is True
    assert board["no_direct_vault_browse"] is True
    assert board["no_raw_file_bytes"] is True
    assert board["no_public_links"] is True

    for item in board["proof_status_rows"]:
        assert item["workflow_state"] == "teller_workflow_proof_status_ready_hash_only"
        assert item["teller_workflow_required"] == 1
        assert item["document_request_status_allowed"] == 1
        assert item["proof_hash_allowed"] == 1
        assert item["direct_vault_browse_allowed"] == 0
        assert item["raw_file_bytes_allowed"] == 0
        assert item["public_link_allowed"] == 0


def test_gp441_450_memory_integrity_signals_are_verified_no_raw_or_provider():
    board = get_vault_memory_integrity_signal_builder()

    assert board["ready"] is True
    assert board["integrity_signal_count"] >= 2
    assert board["all_merkle_verified"] is True
    assert board["no_raw_bytes_needed"] is True
    assert board["provider_not_needed"] is True

    for item in board["integrity_signals"]:
        assert item["integrity_state"] == "vault_memory_integrity_signal_ready"
        assert item["merkle_verified"] == 1
        assert item["raw_bytes_needed"] == 0
        assert item["provider_needed"] == 0
        assert len(item["integrity_signal_hash"]) == 64


def test_gp441_450_sealed_rebuild_outputs_are_redacted_preview_only():
    board = get_sealed_rebuild_status_output_builder()

    assert board["ready"] is True
    assert board["rebuild_output_count"] >= 2
    assert board["all_outputs_redacted"] is True
    assert board["all_preview_only"] is True
    assert board["all_final_index_writes_locked"] is True
    assert board["all_final_pack_overwrites_locked"] is True
    assert board["no_public_index"] is True
    assert board["no_external_browse"] is True
    assert board["no_raw_bytes_exposed"] is True

    for item in board["rebuild_outputs"]:
        assert item["output_state"] == "sealed_rebuild_status_output_ready_redacted"
        assert item["allowed_callers"] == "Tower|Teller"
        assert item["preview_only"] == 1
        assert item["final_index_write_allowed"] == 0
        assert item["final_pack_overwrite_allowed"] == 0
        assert item["public_index_allowed"] == 0
        assert item["external_browse_allowed"] == 0
        assert item["raw_bytes_exposed"] == 0
        assert "raw_file_bytes" in item["blocked_outputs"]
        assert "public_link" in item["blocked_outputs"]


def test_gp441_450_redaction_contract_blocks_raw_path_url_token_public_direct():
    board = get_tower_teller_bridge_redaction_contract()

    assert board["ready"] is True
    assert board["redaction_contract_count"] >= 2
    assert board["all_raw_file_bytes_redacted"] is True
    assert board["all_raw_paths_redacted"] is True
    assert board["all_raw_file_urls_redacted"] is True
    assert board["all_raw_tokens_redacted"] is True
    assert board["all_public_links_redacted"] is True
    assert board["all_direct_browse_redacted"] is True

    for item in board["redaction_contracts"]:
        assert item["redaction_state"] == "tower_teller_bridge_redaction_contract_ready"
        assert item["raw_file_bytes_redacted"] == 1
        assert item["raw_path_redacted"] == 1
        assert item["raw_file_url_redacted"] == 1
        assert item["raw_token_redacted"] == 1
        assert item["public_link_redacted"] == 1
        assert item["direct_browse_redacted"] == 1
        assert "health_state" in item["allowed_fields"]
        assert "raw_file_bytes" in item["redacted_fields"]


def test_gp441_450_safety_blockers_keep_danger_actions_locked():
    board = get_headless_bridge_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "public_vault_dashboard" in blocked_actions
    assert "direct_vault_user_portal" in blocked_actions
    assert "standalone_external_vault_dashboard" in blocked_actions
    assert "employee_vendor_customer_vault_browsing" in blocked_actions
    assert "external_collaborator_browsing" in blocked_actions
    assert "public_links_or_raw_urls" in blocked_actions
    assert "raw_file_bytes_json" in blocked_actions
    assert "raw_path_exposure" in blocked_actions
    assert "raw_token_exposure" in blocked_actions
    assert "final_rebuilt_index_write" in blocked_actions
    assert "provider_dependency" in blocked_actions
    assert "delete_restore_physical_move" in blocked_actions


def test_gp441_450_readiness_declares_next_teller_workflow_request_bridge():
    checkpoint = get_headless_tower_status_bridge_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_vault_pack_rebuild_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["headless_internal_status_bridge_only"] is True
    assert checkpoint["checks"]["bridge_outputs_redacted"] is True
    assert checkpoint["checks"]["health_cards_no_portal_dashboard_raw"] is True
    assert checkpoint["checks"]["receipt_summaries_no_raw_body_path_url_token"] is True
    assert checkpoint["checks"]["clearance_no_vault_direct_approval_or_portal"] is True
    assert checkpoint["checks"]["teller_no_vault_browse_raw_public"] is True
    assert checkpoint["checks"]["memory_integrity_verified_no_raw_provider"] is True
    assert checkpoint["checks"]["sealed_rebuild_no_final_write_public_browse_raw"] is True
    assert checkpoint["checks"]["redaction_blocks_raw_path_url_token_public_direct"] is True
    assert "HEADLESS TELLER WORKFLOW REQUEST BRIDGE" in checkpoint["next_recommended_layer"]


def test_gp441_450_global_locks_preserve_headless_no_dashboard_no_portal_behavior():
    assert LOCKS["tower_vault_health_cards_allowed"] is True
    assert LOCKS["tower_security_receipt_summaries_allowed"] is True
    assert LOCKS["tower_owner_clearance_status_allowed"] is True
    assert LOCKS["teller_workflow_proof_status_allowed"] is True
    assert LOCKS["vault_memory_integrity_signals_allowed"] is True
    assert LOCKS["sealed_rebuild_status_outputs_allowed"] is True
    assert LOCKS["tower_teller_bridge_redaction_allowed"] is True

    assert LOCKS["public_vault_dashboard_allowed"] is False
    assert LOCKS["standalone_external_vault_dashboard_allowed"] is False
    assert LOCKS["direct_vault_user_portal_allowed"] is False
    assert LOCKS["employee_vault_browsing_allowed"] is False
    assert LOCKS["vendor_vault_browsing_allowed"] is False
    assert LOCKS["customer_vault_browsing_allowed"] is False
    assert LOCKS["external_collaborator_browsing_allowed"] is False
    assert LOCKS["public_download_unlocked"] is False
    assert LOCKS["public_url_created"] is False
    assert LOCKS["share_link_created"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["raw_share_token_exposed"] is False
    assert LOCKS["final_rebuilt_index_write_allowed"] is False
    assert LOCKS["final_pack_overwrite_allowed"] is False
    assert LOCKS["sealed_pack_bytes_write_allowed"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False
    assert LOCKS["external_sync_unlocked"] is False


def test_gp441_450_routes_are_json_only_no_public_page_route():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/headless-tower-status-bridge-layer.json",
        "/vault/headless-tower-status-bridge-shell.json",
        "/vault/tower-vault-health-card-contract.json",
        "/vault/tower-security-receipt-summary-board.json",
        "/vault/tower-owner-clearance-status-bridge.json",
        "/vault/teller-workflow-proof-status-bridge.json",
        "/vault/vault-memory-integrity-signal-builder.json",
        "/vault/sealed-rebuild-status-output-builder.json",
        "/vault/tower-teller-bridge-redaction-contract.json",
        "/vault/headless-bridge-safety-blocker-board.json",
        "/vault/headless-tower-status-bridge-readiness-checkpoint.json",
        "/vault/gp441-status.json",
        "/vault/gp450-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert '@app.route("/vault/headless-tower-status-bridge-layer")' not in app_text
