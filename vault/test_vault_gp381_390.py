
from pathlib import Path

from vault.controlled_share_grant_execution_layer_service import (
    LOCKS,
    get_controlled_share_grant_execution_home,
    get_controlled_share_grant_execution_readiness_checkpoint,
    get_controlled_share_grant_packet_builder,
    get_controlled_share_token_builder,
    get_owner_share_approval_execution_board,
    get_share_access_ledger,
    get_share_grant_safety_blocker_board,
    get_share_grant_scope_contract,
    get_share_receipt_finalization_board,
    get_tower_identity_recipient_grant_board,
    validate_controlled_share_grant_execution_layer,
)


def test_gp381_390_readiness_checkpoint_passes():
    result = validate_controlled_share_grant_execution_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Controlled share grant execution layer" in result["readiness_label"]


def test_gp381_390_scope_contract_is_tower_identity_only_no_public_link_or_raw_bytes():
    contract = get_share_grant_scope_contract()

    assert contract["ready"] is True
    assert contract["scope"]["controlled_owner_share_grant_execution_allowed"] is True
    assert contract["scope"]["future_tower_identity_recipient_grant_allowed"] is True
    assert contract["scope"]["tower_identity_required"] is True
    assert contract["scope"]["recipient_subject_kind"] == "future_tower_identity_subject"
    assert contract["scope"]["controlled_share_token_fingerprint_allowed"] is True
    assert contract["scope"]["raw_share_token_exposed"] is False
    assert contract["scope"]["raw_file_bytes_returned_by_json"] is False
    assert contract["scope"]["public_share_allowed"] is False
    assert contract["scope"]["beta_share_allowed"] is False
    assert contract["scope"]["public_url_allowed"] is False
    assert contract["scope"]["share_link_allowed"] is False
    assert contract["scope"]["external_email_grant_allowed"] is False
    assert contract["scope"]["download_link_sharing_allowed"] is False


def test_gp381_390_owner_share_approval_execution_board():
    board = get_owner_share_approval_execution_board()

    assert board["ready"] is True
    assert board["approval_execution_count"] >= 2
    assert board["all_owner_only"] is True
    assert board["all_approvals_executed"] is True
    assert board["controlled_share_grant_count"] >= 2

    for item in board["approval_executions"]:
        assert item["approval_state"] == "owner_share_approval_executed_for_controlled_tower_identity_grant"
        assert item["owner_only"] == 1
        assert item["approval_executed"] == 1
        assert item["controlled_share_grant_allowed"] == 1


def test_gp381_390_controlled_share_tokens_are_fingerprints_only():
    builder = get_controlled_share_token_builder()

    assert builder["ready"] is True
    assert builder["share_token_count"] >= 2
    assert builder["all_owner_only"] is True
    assert builder["no_raw_tokens_exposed"] is True
    assert builder["all_one_time_access_required"] is True

    for item in builder["share_tokens"]:
        assert item["token_state"] == "controlled_share_token_fingerprint_created"
        assert len(item["token_fingerprint"]) == 64
        assert item["raw_token_exposed"] == 0
        assert item["owner_only"] == 1
        assert item["ttl_seconds"] == 3600
        assert item["max_ttl_seconds"] == 86400


def test_gp381_390_controlled_share_packets_are_metadata_only_no_links():
    builder = get_controlled_share_grant_packet_builder()

    assert builder["ready"] is True
    assert builder["share_packet_count"] >= 2
    assert builder["successful_share_packet_count"] >= 2
    assert builder["all_owner_only"] is True
    assert builder["no_raw_file_bytes_returned_by_json"] is True
    assert builder["no_public_urls_created"] is True
    assert builder["no_share_links_created"] is True
    assert builder["no_external_email_grants_created"] is True

    for packet in builder["share_packets"]:
        assert packet["share_packet_state"] == "controlled_tower_identity_share_grant_packet_ready"
        assert packet["owner_only"] is True
        assert len(packet["share_packet_hash"]) == 64
        assert packet["display"]["raw_file_bytes"] == "LOCKED_FROM_JSON"
        assert packet["display"]["raw_share_token"] == "LOCKED_FINGERPRINT_ONLY"
        assert packet["display"]["public_url"] == "LOCKED"
        assert packet["display"]["share_link"] == "LOCKED"
        assert packet["display"]["external_email_grant"] == "LOCKED"
        assert packet["locks"]["raw_file_bytes_returned_by_json"] is False
        assert packet["locks"]["public_url_created"] is False
        assert packet["locks"]["share_link_created"] is False
        assert packet["locks"]["external_email_grant_created"] is False


def test_gp381_390_tower_identity_recipient_grants_are_internal_only():
    board = get_tower_identity_recipient_grant_board()

    assert board["ready"] is True
    assert board["recipient_grant_count"] >= 2
    assert board["all_tower_identity_required"] is True
    assert board["all_future_tower_subjects"] is True
    assert board["no_external_email_allowed"] is True
    assert board["no_external_email_grants_created"] is True
    assert board["no_public_access"] is True
    assert board["no_beta_access"] is True

    for item in board["recipient_grants"]:
        assert item["recipient_subject_kind"] == "future_tower_identity_subject"
        assert item["grant_state"] == "controlled_future_tower_identity_recipient_grant_recorded"
        assert item["tower_identity_required"] == 1
        assert item["external_email_allowed"] == 0
        assert item["external_email_grant_created"] == 0
        assert item["public_access_allowed"] == 0
        assert item["beta_access_allowed"] == 0


def test_gp381_390_share_access_ledger_locks_public_external_download_raw_delete_restore():
    ledger = get_share_access_ledger()

    assert ledger["ready"] is True
    assert ledger["share_access_count"] >= 2
    assert ledger["all_owner_only"] is True
    assert ledger["all_future_tower_identity_recipient_allowed"] is True
    assert ledger["no_public_access"] is True
    assert ledger["no_beta_access"] is True
    assert ledger["no_external_email_access"] is True
    assert ledger["no_download_link_sharing"] is True
    assert ledger["no_raw_file_bytes_json"] is True
    assert ledger["no_delete_access"] is True
    assert ledger["no_restore_access"] is True

    for item in ledger["share_access_rows"]:
        assert item["access_scope"] == "controlled_future_tower_identity_share_grant"
        assert item["owner_only"] == 1
        assert item["future_tower_identity_recipient_allowed"] == 1
        assert item["public_access_allowed"] == 0
        assert item["beta_access_allowed"] == 0
        assert item["external_email_access_allowed"] == 0
        assert item["download_link_sharing_allowed"] == 0
        assert item["raw_file_bytes_json_allowed"] == 0
        assert item["delete_allowed"] == 0
        assert item["restore_allowed"] == 0


def test_gp381_390_share_receipts_finalized():
    board = get_share_receipt_finalization_board()

    assert board["ready"] is True
    assert board["final_receipt_count"] >= 2
    assert board["all_receipts_finalized"] is True

    for item in board["final_receipts"]:
        assert item["finalized"] == 1
        assert item["receipt_scope"] == "controlled_share_grant_execution"
        assert len(item["final_receipt_hash"]) == 64


def test_gp381_390_safety_blockers_keep_danger_actions_locked():
    board = get_share_grant_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "public_share" in blocked_actions
    assert "beta_share" in blocked_actions
    assert "public_url" in blocked_actions
    assert "share_link" in blocked_actions
    assert "external_email_grant" in blocked_actions
    assert "external_recipient_grant" in blocked_actions
    assert "download_link_sharing" in blocked_actions
    assert "raw_share_token_exposure" in blocked_actions
    assert "raw_file_bytes_json" in blocked_actions
    assert "recipient_raw_download" in blocked_actions
    assert "file_delete" in blocked_actions
    assert "file_restore" in blocked_actions
    assert "quarantine_release" in blocked_actions
    assert "external_sync" in blocked_actions


def test_gp381_390_home_exposes_packs_and_locks():
    home = get_controlled_share_grant_execution_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["controlled_owner_share_grant_execution_allowed"] is True
    assert home["locks"]["future_tower_identity_recipient_grant_allowed"] is True
    assert home["locks"]["controlled_share_token_fingerprint_allowed"] is True
    assert home["locks"]["public_share_unlocked"] is False
    assert home["locks"]["beta_share_unlocked"] is False
    assert home["locks"]["public_url_created"] is False
    assert home["locks"]["share_link_created"] is False
    assert home["locks"]["external_email_grant_allowed"] is False
    assert home["locks"]["raw_share_token_exposed"] is False
    assert home["locks"]["raw_file_bytes_returned_by_json"] is False


def test_gp381_390_readiness_declares_next_layer():
    checkpoint = get_controlled_share_grant_execution_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_owner_share_access_lock_prep_ready"] is True
    assert checkpoint["checks"]["controlled_share_grants_recorded"] is True
    assert checkpoint["checks"]["controlled_share_tokens_ready"] is True
    assert checkpoint["checks"]["no_raw_tokens_exposed"] is True
    assert checkpoint["checks"]["controlled_share_packets_successful"] is True
    assert checkpoint["checks"]["share_packets_no_raw_bytes_json"] is True
    assert checkpoint["checks"]["share_packets_no_public_urls"] is True
    assert checkpoint["checks"]["share_packets_no_links"] is True
    assert checkpoint["checks"]["share_packets_no_external_email_grants"] is True
    assert checkpoint["checks"]["recipient_grants_tower_identity_only"] is True
    assert checkpoint["checks"]["recipient_grants_no_external_email"] is True
    assert checkpoint["checks"]["share_access_no_download_raw_delete_restore"] is True
    assert "TRASH RESTORE AND RECOVERY PREP" in checkpoint["next_recommended_layer"]


def test_gp381_390_allowed_features_are_controlled_share_grants_only():
    assert LOCKS["controlled_owner_share_grant_execution_allowed"] is True
    assert LOCKS["future_tower_identity_recipient_grant_allowed"] is True
    assert LOCKS["controlled_share_token_fingerprint_allowed"] is True
    assert LOCKS["controlled_share_grant_packet_metadata_allowed"] is True
    assert LOCKS["share_access_ledger_allowed"] is True
    assert LOCKS["share_receipt_finalization_allowed"] is True

    assert LOCKS["public_share_unlocked"] is False
    assert LOCKS["beta_share_unlocked"] is False
    assert LOCKS["public_url_created"] is False
    assert LOCKS["share_link_created"] is False
    assert LOCKS["external_email_grant_allowed"] is False
    assert LOCKS["external_recipient_grant_allowed"] is False
    assert LOCKS["download_link_sharing_allowed"] is False
    assert LOCKS["raw_share_token_exposed"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_file_download_for_recipient_allowed"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["quarantine_object_move_allowed"] is False
    assert LOCKS["public_upload_unlocked"] is False
    assert LOCKS["beta_upload_unlocked"] is False
    assert LOCKS["provider_upload_unlocked"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["external_sync_unlocked"] is False


def test_gp381_390_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/controlled-share-grant-execution-layer",
        "/vault/controlled-share-grant-execution-layer.json",
        "/vault/controlled-share-grant-execution-shell.json",
        "/vault/share-grant-scope-contract.json",
        "/vault/owner-share-approval-execution-board.json",
        "/vault/controlled-share-token-builder.json",
        "/vault/controlled-share-grant-packet-builder.json",
        "/vault/tower-identity-recipient-grant-board.json",
        "/vault/share-access-ledger.json",
        "/vault/share-receipt-finalization-board.json",
        "/vault/share-grant-safety-blocker-board.json",
        "/vault/controlled-share-grant-execution-readiness-checkpoint.json",
        "/vault/gp381-status.json",
        "/vault/gp390-status.json",
    ]

    for route in required_routes:
        assert route in app_text
