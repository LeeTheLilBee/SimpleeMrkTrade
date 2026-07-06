
from pathlib import Path

from vault.owner_download_lock_prep_layer_service import (
    LOCKS,
    get_download_eligibility_policy_board,
    get_download_expiration_policy_board,
    get_download_receipt_draft_ledger,
    get_download_route_payload_draft_builder,
    get_download_safety_blocker_board,
    get_download_safety_review_queue,
    get_download_scope_contract,
    get_owner_download_approval_lock_board,
    get_owner_download_lock_prep_home,
    get_owner_download_lock_prep_readiness_checkpoint,
    validate_owner_download_lock_prep_layer,
)


def test_gp351_360_readiness_checkpoint_passes():
    result = validate_owner_download_lock_prep_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Owner download lock prep layer" in result["readiness_label"]


def test_gp351_360_download_eligibility_candidates_are_owner_only_and_locked():
    board = get_download_eligibility_policy_board()

    assert board["ready"] is True
    assert board["candidate_count"] >= 2
    assert board["all_candidates_owner_only"] is True
    assert board["all_owner_approval_required"] is True
    assert board["no_download_execution_allowed"] is True
    assert board["no_download_urls_created"] is True

    for item in board["candidates"]:
        assert item["owner_only"] == 1
        assert item["owner_approval_required"] == 1
        assert item["download_execution_allowed"] == 0
        assert item["download_url_created"] == 0
        assert item["eligibility_state"] == "download_policy_candidate_owner_approval_required_locked"
        assert len(item["sha256_hash"]) == 64


def test_gp351_360_download_scope_contract_keeps_execution_locked():
    contract = get_download_scope_contract()

    assert contract["ready"] is True
    assert contract["scope"]["owner_only"] is True
    assert contract["scope"]["owner_approval_required"] is True
    assert contract["scope"]["download_execution_allowed"] is False
    assert contract["scope"]["download_url_creation_allowed"] is False
    assert contract["scope"]["download_token_creation_allowed"] is False
    assert contract["scope"]["download_streaming_allowed"] is False
    assert contract["scope"]["download_file_body_return_allowed"] is False
    assert contract["scope"]["one_time_download_required"] is True
    assert contract["scope"]["public_download_allowed"] is False
    assert contract["scope"]["beta_download_allowed"] is False


def test_gp351_360_owner_download_approval_locks_are_closed():
    board = get_owner_download_approval_lock_board()

    assert board["ready"] is True
    assert board["approval_lock_count"] >= 2
    assert board["all_owner_approval_required"] is True
    assert board["all_approval_recording_locked"] is True
    assert board["all_download_execution_locked"] is True

    for item in board["approval_locks"]:
        assert item["approval_state"] == "owner_download_approval_required_locked"
        assert item["owner_approval_required"] == 1
        assert item["approval_recording_allowed"] == 0
        assert item["download_execution_allowed"] == 0


def test_gp351_360_download_expiration_policy_is_prepared_but_token_locked():
    board = get_download_expiration_policy_board()

    assert board["ready"] is True
    assert board["expiration_policy_count"] >= 2
    assert board["all_one_time_download_required"] is True
    assert board["all_expiration_enforced"] is True
    assert board["all_token_creation_locked"] is True
    assert board["all_download_execution_locked"] is True

    for item in board["expiration_policies"]:
        assert item["ttl_seconds"] == 900
        assert item["max_ttl_seconds"] == 1800
        assert item["one_time_download_required"] == 1
        assert item["expiration_enforced"] == 1
        assert item["token_creation_allowed"] == 0
        assert item["download_execution_allowed"] == 0


def test_gp351_360_download_payload_drafts_exclude_url_token_and_file_body():
    builder = get_download_route_payload_draft_builder()

    assert builder["ready"] is True
    assert builder["payload_draft_count"] >= 2
    assert builder["metadata_only"] is True
    assert builder["download_url_included"] is False
    assert builder["download_token_included"] is False
    assert builder["file_body_included"] is False

    for payload in builder["payload_drafts"]:
        assert payload["metadata_only"] is True
        assert payload["display"]["download_url"] == "LOCKED"
        assert payload["display"]["download_token"] == "LOCKED"
        assert payload["display"]["file_body"] == "LOCKED"
        assert payload["locks"]["download_url_included"] is False
        assert payload["locks"]["download_token_included"] is False
        assert payload["locks"]["file_body_included"] is False
        assert len(payload["payload_hash"]) == 64


def test_gp351_360_download_receipts_are_draft_locked():
    ledger = get_download_receipt_draft_ledger()

    assert ledger["ready"] is True
    assert ledger["receipt_draft_count"] >= 2
    assert ledger["all_receipts_draft_locked"] is True
    assert ledger["receipt_finalization_allowed"] is False

    for item in ledger["receipt_drafts"]:
        assert item["receipt_state"] == "download_receipt_draft_locked"
        assert item["finalized"] == 0
        assert item["finalization_allowed"] == 0
        assert len(item["receipt_hash"]) == 64


def test_gp351_360_download_safety_review_queue_is_locked():
    queue = get_download_safety_review_queue()

    assert queue["ready"] is True
    assert queue["review_queue_count"] >= 2
    assert queue["all_reviewer_actions_locked"] is True
    assert queue["all_download_execution_locked"] is True

    for item in queue["review_queue"]:
        assert item["review_state"] == "queued_for_future_owner_download_safety_review_locked"
        assert item["reviewer_action_allowed"] == 0
        assert item["download_execution_allowed"] == 0


def test_gp351_360_download_safety_blockers_keep_danger_actions_locked():
    board = get_download_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "download_execution" in blocked_actions
    assert "download_url_creation" in blocked_actions
    assert "download_token_creation" in blocked_actions
    assert "download_streaming" in blocked_actions
    assert "file_body_return" in blocked_actions
    assert "public_download" in blocked_actions
    assert "beta_download" in blocked_actions
    assert "file_share" in blocked_actions
    assert "file_delete" in blocked_actions
    assert "file_restore" in blocked_actions
    assert "quarantine_release" in blocked_actions
    assert "external_sync" in blocked_actions


def test_gp351_360_home_exposes_packs_and_locks():
    home = get_owner_download_lock_prep_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["download_eligibility_metadata_allowed"] is True
    assert home["locks"]["download_scope_policy_allowed"] is True
    assert home["locks"]["owner_download_approval_lock_allowed"] is True
    assert home["locks"]["download_execution_allowed"] is False
    assert home["locks"]["download_url_creation_allowed"] is False
    assert home["locks"]["file_download_unlocked"] is False


def test_gp351_360_readiness_declares_next_layer():
    checkpoint = get_owner_download_lock_prep_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_controlled_owner_safe_preview_ready"] is True
    assert checkpoint["checks"]["download_eligibility_ready"] is True
    assert checkpoint["checks"]["download_execution_locked_on_candidates"] is True
    assert checkpoint["checks"]["download_urls_not_created"] is True
    assert checkpoint["checks"]["download_payloads_metadata_only"] is True
    assert checkpoint["checks"]["download_receipt_drafts_locked"] is True
    assert checkpoint["checks"]["download_execution_still_locked"] is True
    assert checkpoint["checks"]["download_url_creation_still_locked"] is True
    assert checkpoint["checks"]["file_body_return_still_locked"] is True
    assert "CONTROLLED OWNER DOWNLOAD EXECUTION" in checkpoint["next_recommended_layer"]


def test_gp351_360_allowed_features_are_download_prep_only():
    assert LOCKS["download_eligibility_metadata_allowed"] is True
    assert LOCKS["download_scope_policy_allowed"] is True
    assert LOCKS["owner_download_approval_lock_allowed"] is True
    assert LOCKS["download_expiration_policy_allowed"] is True
    assert LOCKS["download_route_payload_draft_allowed"] is True
    assert LOCKS["download_receipt_draft_allowed"] is True
    assert LOCKS["download_safety_review_queue_allowed"] is True

    assert LOCKS["download_execution_allowed"] is False
    assert LOCKS["download_url_creation_allowed"] is False
    assert LOCKS["download_token_creation_allowed"] is False
    assert LOCKS["download_streaming_allowed"] is False
    assert LOCKS["download_file_body_return_allowed"] is False
    assert LOCKS["public_download_unlocked"] is False
    assert LOCKS["beta_download_unlocked"] is False
    assert LOCKS["file_download_unlocked"] is False
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


def test_gp351_360_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-download-lock-prep-layer",
        "/vault/owner-download-lock-prep-layer.json",
        "/vault/owner-download-lock-prep-shell.json",
        "/vault/download-eligibility-policy-board.json",
        "/vault/download-scope-contract.json",
        "/vault/owner-download-approval-lock-board.json",
        "/vault/download-expiration-policy-board.json",
        "/vault/download-route-payload-draft-builder.json",
        "/vault/download-receipt-draft-ledger.json",
        "/vault/download-safety-review-queue.json",
        "/vault/download-safety-blocker-board.json",
        "/vault/owner-download-lock-prep-readiness-checkpoint.json",
        "/vault/gp351-status.json",
        "/vault/gp360-status.json",
    ]

    for route in required_routes:
        assert route in app_text
