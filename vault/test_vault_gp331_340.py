
from pathlib import Path

from vault.owner_safe_preview_lock_prep_layer_service import (
    LOCKS,
    get_owner_preview_approval_lock_board,
    get_owner_safe_preview_lock_prep_home,
    get_owner_safe_preview_lock_prep_readiness_checkpoint,
    get_preview_eligibility_policy_board,
    get_preview_mime_type_contract,
    get_preview_receipt_draft_ledger,
    get_preview_redaction_policy_board,
    get_preview_route_payload_draft_builder,
    get_preview_safety_blocker_board,
    get_preview_safety_review_queue,
    validate_owner_safe_preview_lock_prep_layer,
)


def test_gp331_340_readiness_checkpoint_passes():
    result = validate_owner_safe_preview_lock_prep_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Owner safe preview lock prep layer" in result["readiness_label"]


def test_gp331_340_preview_eligibility_board_is_metadata_only_and_locked():
    board = get_preview_eligibility_policy_board()

    assert board["ready"] is True
    assert board["candidate_count"] >= 2
    assert board["metadata_only"] is True
    assert board["preview_execution_allowed"] is False
    assert board["object_body_read_allowed"] is False

    for item in board["candidates"]:
        assert item["owner_approval_required"] == 1
        assert item["object_body_read_allowed"] == 0
        assert item["preview_rendering_allowed"] == 0
        assert item["eligibility_state"].endswith("preview_locked")


def test_gp331_340_mime_type_contract_preps_policy_but_locks_extraction_and_rendering():
    contract = get_preview_mime_type_contract()

    assert contract["ready"] is True
    assert contract["mime_type_count"] >= 6
    assert contract["future_preview_policy_count"] >= 1
    assert contract["all_content_extraction_locked"] is True
    assert contract["all_rendering_locked"] is True

    mime_types = {item["mime_type"] for item in contract["mime_types"]}
    assert "application/pdf" in mime_types
    assert "image/png" in mime_types
    assert "image/jpeg" in mime_types


def test_gp331_340_preview_redaction_policy_blocks_body_plaintext_and_physical_path():
    board = get_preview_redaction_policy_board()

    assert board["ready"] is True
    assert board["policy_count"] >= 5
    assert board["object_body_blocked"] is True
    assert board["plaintext_content_blocked"] is True
    assert board["physical_path_hidden"] is True


def test_gp331_340_owner_preview_approval_locks_are_closed():
    board = get_owner_preview_approval_lock_board()

    assert board["ready"] is True
    assert board["approval_lock_count"] >= 2
    assert board["all_owner_approval_required"] is True
    assert board["all_approval_recording_locked"] is True
    assert board["all_preview_execution_locked"] is True

    for item in board["approval_locks"]:
        assert item["approval_state"] == "owner_preview_approval_required_locked"
        assert item["owner_approval_required"] == 1
        assert item["approval_recording_allowed"] == 0
        assert item["preview_execution_allowed"] == 0


def test_gp331_340_preview_route_payload_drafts_exclude_content_preview_and_download():
    builder = get_preview_route_payload_draft_builder()

    assert builder["ready"] is True
    assert builder["payload_draft_count"] >= 2
    assert builder["metadata_only"] is True
    assert builder["object_body_included"] is False
    assert builder["plaintext_content_included"] is False
    assert builder["rendered_preview_included"] is False
    assert builder["download_url_included"] is False

    for payload in builder["payload_drafts"]:
        assert payload["metadata_only"] is True
        assert payload["display"]["object_body"] == "LOCKED"
        assert payload["display"]["plaintext_content"] == "LOCKED"
        assert payload["display"]["rendered_preview"] == "LOCKED"
        assert payload["display"]["download_url"] == "LOCKED"
        assert payload["locks"]["object_body_included"] is False
        assert payload["locks"]["rendered_preview_included"] is False
        assert len(payload["payload_hash"]) == 64


def test_gp331_340_preview_receipts_are_draft_locked():
    ledger = get_preview_receipt_draft_ledger()

    assert ledger["ready"] is True
    assert ledger["receipt_draft_count"] >= 2
    assert ledger["all_receipts_draft_locked"] is True
    assert ledger["receipt_finalization_allowed"] is False

    for item in ledger["receipt_drafts"]:
        assert item["receipt_state"] == "draft_locked"
        assert item["finalized"] == 0
        assert item["finalization_allowed"] == 0
        assert len(item["receipt_hash"]) == 64


def test_gp331_340_preview_safety_review_queue_is_locked():
    queue = get_preview_safety_review_queue()

    assert queue["ready"] is True
    assert queue["review_queue_count"] >= 2
    assert queue["all_reviewer_actions_locked"] is True
    assert queue["all_preview_execution_locked"] is True

    for item in queue["review_queue"]:
        assert item["review_state"] == "queued_for_future_preview_safety_review_locked"
        assert item["reviewer_action_allowed"] == 0
        assert item["preview_execution_allowed"] == 0


def test_gp331_340_preview_safety_blockers_keep_danger_actions_locked():
    board = get_preview_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "object_body_read" in blocked_actions
    assert "plaintext_extraction" in blocked_actions
    assert "preview_rendering" in blocked_actions
    assert "preview_endpoint_execution" in blocked_actions
    assert "preview_cache_write" in blocked_actions
    assert "preview_cache_read" in blocked_actions
    assert "file_download" in blocked_actions
    assert "file_share" in blocked_actions
    assert "file_delete" in blocked_actions
    assert "file_restore" in blocked_actions
    assert "quarantine_release" in blocked_actions
    assert "external_sync" in blocked_actions


def test_gp331_340_home_exposes_packs_and_locks():
    home = get_owner_safe_preview_lock_prep_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["preview_eligibility_metadata_allowed"] is True
    assert home["locks"]["preview_mime_policy_allowed"] is True
    assert home["locks"]["owner_preview_approval_lock_allowed"] is True
    assert home["locks"]["object_body_read_allowed"] is False
    assert home["locks"]["preview_rendering_allowed"] is False
    assert home["locks"]["file_preview_unlocked"] is False


def test_gp331_340_readiness_checkpoint_declares_next_layer():
    checkpoint = get_owner_safe_preview_lock_prep_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_folder_browse_metadata_ready"] is True
    assert checkpoint["checks"]["preview_eligibility_ready"] is True
    assert checkpoint["checks"]["mime_contract_ready"] is True
    assert checkpoint["checks"]["mime_content_extraction_locked"] is True
    assert checkpoint["checks"]["mime_rendering_locked"] is True
    assert checkpoint["checks"]["preview_payloads_metadata_only"] is True
    assert checkpoint["checks"]["object_body_read_still_locked"] is True
    assert checkpoint["checks"]["preview_rendering_still_locked"] is True
    assert "CONTROLLED OWNER SAFE PREVIEW EXECUTION" in checkpoint["next_recommended_layer"]


def test_gp331_340_allowed_features_are_preview_prep_only():
    assert LOCKS["preview_eligibility_metadata_allowed"] is True
    assert LOCKS["preview_mime_policy_allowed"] is True
    assert LOCKS["preview_redaction_policy_allowed"] is True
    assert LOCKS["owner_preview_approval_lock_allowed"] is True
    assert LOCKS["preview_route_payload_draft_allowed"] is True
    assert LOCKS["preview_receipt_draft_allowed"] is True
    assert LOCKS["preview_safety_review_queue_allowed"] is True

    assert LOCKS["object_body_read_allowed"] is False
    assert LOCKS["plaintext_content_extraction_allowed"] is False
    assert LOCKS["preview_rendering_allowed"] is False
    assert LOCKS["preview_endpoint_execution_allowed"] is False
    assert LOCKS["preview_cache_write_allowed"] is False
    assert LOCKS["preview_cache_read_allowed"] is False
    assert LOCKS["file_preview_unlocked"] is False
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


def test_gp331_340_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-safe-preview-lock-prep-layer",
        "/vault/owner-safe-preview-lock-prep-layer.json",
        "/vault/owner-safe-preview-lock-prep-shell.json",
        "/vault/preview-eligibility-policy-board.json",
        "/vault/preview-mime-type-contract.json",
        "/vault/preview-redaction-policy-board.json",
        "/vault/owner-preview-approval-lock-board.json",
        "/vault/preview-route-payload-draft-builder.json",
        "/vault/preview-receipt-draft-ledger.json",
        "/vault/preview-safety-review-queue.json",
        "/vault/preview-safety-blocker-board.json",
        "/vault/owner-safe-preview-lock-prep-readiness-checkpoint.json",
        "/vault/gp331-status.json",
        "/vault/gp340-status.json",
    ]

    for route in required_routes:
        assert route in app_text
