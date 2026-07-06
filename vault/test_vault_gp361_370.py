
from pathlib import Path

from vault.controlled_owner_download_execution_layer_service import (
    LOCKS,
    get_controlled_download_packet_builder,
    get_controlled_download_token_builder,
    get_controlled_owner_download_execution_home,
    get_controlled_owner_download_execution_readiness_checkpoint,
    get_download_access_ledger,
    get_download_execution_safety_blocker_board,
    get_download_execution_scope_contract,
    get_download_hash_verification_board,
    get_download_receipt_finalization_board,
    get_owner_download_approval_execution_board,
    validate_controlled_owner_download_execution_layer,
)


def test_gp361_370_readiness_checkpoint_passes():
    result = validate_controlled_owner_download_execution_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Controlled owner download execution layer" in result["readiness_label"]


def test_gp361_370_scope_contract_owner_only_no_public_or_raw_json_bytes():
    contract = get_download_execution_scope_contract()

    assert contract["ready"] is True
    assert contract["scope"]["owner_only"] is True
    assert contract["scope"]["controlled_download_execution_allowed"] is True
    assert contract["scope"]["internal_file_byte_verification_allowed"] is True
    assert contract["scope"]["token_fingerprint_allowed"] is True
    assert contract["scope"]["raw_token_exposed"] is False
    assert contract["scope"]["raw_file_bytes_returned_by_json"] is False
    assert contract["scope"]["public_download_allowed"] is False
    assert contract["scope"]["beta_download_allowed"] is False
    assert contract["scope"]["share_allowed"] is False


def test_gp361_370_owner_download_approval_execution_board():
    board = get_owner_download_approval_execution_board()

    assert board["ready"] is True
    assert board["approval_execution_count"] >= 2
    assert board["all_owner_only"] is True
    assert board["all_approvals_executed"] is True
    assert board["successful_download_execution_count"] >= 2

    for item in board["approval_executions"]:
        assert item["approval_state"] == "owner_download_approval_executed_for_controlled_owner_only_download"
        assert item["owner_only"] == 1
        assert item["approval_executed"] == 1
        assert item["download_execution_allowed"] == 1


def test_gp361_370_controlled_download_tokens_are_fingerprints_only():
    builder = get_controlled_download_token_builder()

    assert builder["ready"] is True
    assert builder["token_count"] >= 2
    assert builder["all_owner_only"] is True
    assert builder["no_raw_tokens_exposed"] is True
    assert builder["all_one_time_download_required"] is True

    for item in builder["tokens"]:
        assert item["token_state"] == "controlled_owner_download_token_fingerprint_created"
        assert len(item["token_fingerprint"]) == 64
        assert item["raw_token_exposed"] == 0
        assert item["owner_only"] == 1
        assert item["ttl_seconds"] == 900
        assert item["max_ttl_seconds"] == 1800


def test_gp361_370_controlled_download_packets_are_metadata_only_to_json():
    builder = get_controlled_download_packet_builder()

    assert builder["ready"] is True
    assert builder["packet_count"] >= 2
    assert builder["successful_packet_count"] >= 2
    assert builder["all_owner_only"] is True
    assert builder["no_raw_file_bytes_returned_by_json"] is True
    assert builder["no_public_urls_created"] is True

    for packet in builder["packets"]:
        assert packet["packet_state"] == "controlled_owner_download_packet_ready"
        assert packet["owner_only"] is True
        assert packet["bytes_verified"] > 0
        assert len(packet["packet_hash"]) == 64
        assert packet["display"]["raw_file_bytes"] == "LOCKED_FROM_JSON"
        assert packet["display"]["raw_download_token"] == "LOCKED_FINGERPRINT_ONLY"
        assert packet["display"]["public_url"] == "LOCKED"
        assert packet["display"]["share_link"] == "LOCKED"
        assert packet["locks"]["raw_file_bytes_returned_by_json"] is False
        assert packet["locks"]["public_url_created"] is False


def test_gp361_370_download_hash_verification_passes():
    board = get_download_hash_verification_board()

    assert board["ready"] is True
    assert board["verification_count"] >= 2
    assert board["all_hashes_match"] is True
    assert board["all_bytes_verified"] is True

    for item in board["verifications"]:
        assert item["expected_hash"] == item["actual_hash"]
        assert item["hash_match"] == 1
        assert item["bytes_verified"] > 0


def test_gp361_370_download_access_ledger_owner_only():
    ledger = get_download_access_ledger()

    assert ledger["ready"] is True
    assert ledger["access_count"] >= 2
    assert ledger["all_owner_only"] is True
    assert ledger["no_public_access"] is True
    assert ledger["no_beta_access"] is True
    assert ledger["no_share_access"] is True
    assert ledger["no_delete_access"] is True
    assert ledger["no_restore_access"] is True

    for item in ledger["access_rows"]:
        assert item["access_scope"] == "owner_only_controlled_download"
        assert item["owner_only"] == 1
        assert item["public_access_allowed"] == 0
        assert item["beta_access_allowed"] == 0
        assert item["share_allowed"] == 0
        assert item["delete_allowed"] == 0
        assert item["restore_allowed"] == 0


def test_gp361_370_download_receipts_finalized():
    board = get_download_receipt_finalization_board()

    assert board["ready"] is True
    assert board["final_receipt_count"] >= 2
    assert board["all_receipts_finalized"] is True

    for item in board["final_receipts"]:
        assert item["finalized"] == 1
        assert item["receipt_scope"] == "controlled_owner_download_execution"
        assert len(item["final_receipt_hash"]) == 64


def test_gp361_370_safety_blockers_keep_danger_actions_locked():
    board = get_download_execution_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "raw_file_bytes_json" in blocked_actions
    assert "raw_download_token_exposure" in blocked_actions
    assert "public_download" in blocked_actions
    assert "beta_download" in blocked_actions
    assert "public_download_url" in blocked_actions
    assert "share_link" in blocked_actions
    assert "file_share" in blocked_actions
    assert "file_delete" in blocked_actions
    assert "file_restore" in blocked_actions
    assert "quarantine_release" in blocked_actions
    assert "external_sync" in blocked_actions


def test_gp361_370_home_exposes_packs_and_locks():
    home = get_controlled_owner_download_execution_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["controlled_owner_download_execution_allowed"] is True
    assert home["locks"]["owner_only_download_allowed"] is True
    assert home["locks"]["raw_download_token_exposed"] is False
    assert home["locks"]["raw_file_bytes_returned_by_json"] is False
    assert home["locks"]["public_download_unlocked"] is False
    assert home["locks"]["file_share_unlocked"] is False


def test_gp361_370_readiness_declares_next_layer():
    checkpoint = get_controlled_owner_download_execution_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_owner_download_lock_prep_ready"] is True
    assert checkpoint["checks"]["download_execution_records_successful"] is True
    assert checkpoint["checks"]["controlled_tokens_ready"] is True
    assert checkpoint["checks"]["no_raw_tokens_exposed"] is True
    assert checkpoint["checks"]["controlled_packets_successful"] is True
    assert checkpoint["checks"]["packets_no_raw_bytes_json"] is True
    assert checkpoint["checks"]["hash_verification_ready"] is True
    assert checkpoint["checks"]["no_public_or_beta_access"] is True
    assert checkpoint["checks"]["no_share_delete_restore_access"] is True
    assert "OWNER SHARE ACCESS LOCK PREP" in checkpoint["next_recommended_layer"]


def test_gp361_370_allowed_features_are_owner_download_only():
    assert LOCKS["controlled_owner_download_execution_allowed"] is True
    assert LOCKS["owner_only_download_allowed"] is True
    assert LOCKS["scoped_internal_file_byte_verification_allowed"] is True
    assert LOCKS["controlled_download_token_fingerprint_allowed"] is True
    assert LOCKS["controlled_download_packet_metadata_allowed"] is True
    assert LOCKS["download_hash_verification_allowed"] is True
    assert LOCKS["download_access_ledger_allowed"] is True
    assert LOCKS["download_receipt_finalization_allowed"] is True

    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["public_download_unlocked"] is False
    assert LOCKS["beta_download_unlocked"] is False
    assert LOCKS["public_download_url_unlocked"] is False
    assert LOCKS["share_link_unlocked"] is False
    assert LOCKS["file_share_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["quarantine_object_move_allowed"] is False
    assert LOCKS["public_upload_unlocked"] is False
    assert LOCKS["beta_upload_unlocked"] is False
    assert LOCKS["provider_upload_unlocked"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["external_sync_unlocked"] is False


def test_gp361_370_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/controlled-owner-download-execution-layer",
        "/vault/controlled-owner-download-execution-layer.json",
        "/vault/controlled-owner-download-execution-shell.json",
        "/vault/download-execution-scope-contract.json",
        "/vault/owner-download-approval-execution-board.json",
        "/vault/controlled-download-token-builder.json",
        "/vault/controlled-download-packet-builder.json",
        "/vault/download-hash-verification-board.json",
        "/vault/download-access-ledger.json",
        "/vault/download-receipt-finalization-board.json",
        "/vault/download-execution-safety-blocker-board.json",
        "/vault/controlled-owner-download-execution-readiness-checkpoint.json",
        "/vault/gp361-status.json",
        "/vault/gp370-status.json",
    ]

    for route in required_routes:
        assert route in app_text
