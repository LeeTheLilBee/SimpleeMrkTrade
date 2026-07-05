
from pathlib import Path

from vault.owner_file_registry_promotion_lock_layer_service import (
    LOCKS,
    get_active_file_registry_preview,
    get_owner_file_registry_promotion_home,
    get_owner_file_registry_promotion_lock_readiness_checkpoint,
    get_promotion_approval_lock_board,
    get_promotion_eligibility_contract,
    get_promotion_hash_continuity_board,
    get_promotion_receipt_draft_ledger,
    get_quarantine_promotion_candidate_board,
    get_quarantine_release_prohibition_board,
    get_registry_promotion_safety_blocker_board,
    validate_owner_file_registry_promotion_lock_layer,
)


def test_gp291_300_readiness_checkpoint_passes():
    result = validate_owner_file_registry_promotion_lock_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Owner file registry promotion lock layer" in result["readiness_label"]


def test_gp291_300_candidate_board_finds_quarantine_written_objects_but_locks_promotion():
    board = get_quarantine_promotion_candidate_board()

    assert board["ready"] is True
    assert board["candidate_count"] >= 2
    assert board["promotion_allowed"] is False
    assert board["quarantine_release_allowed"] is False

    for item in board["candidates"]:
        assert item["hash_verified"] == 1
        assert item["eligibility_state"] == "eligible_preview_locked"
        assert item["promotion_state"] == "promotion_locked"
        assert item["active_registry_final_write_allowed"] == 0
        assert item["quarantine_release_allowed"] == 0


def test_gp291_300_promotion_eligibility_contract_is_preview_only():
    contract = get_promotion_eligibility_contract()

    assert contract["ready"] is True
    assert contract["promotion_execution_allowed"] is False
    assert contract["eligibility_rules"]["must_come_from_quarantine_writer"] is True
    assert contract["eligibility_rules"]["must_have_verified_hash"] is True
    assert contract["eligibility_rules"]["must_remain_quarantine_locked"] is True
    assert contract["eligibility_rules"]["final_promotion_requires_future_owner_approval"] is True


def test_gp291_300_active_file_registry_preview_does_not_final_write():
    preview = get_active_file_registry_preview()

    assert preview["ready"] is True
    assert preview["preview_count"] >= 2
    assert preview["preview_only"] is True
    assert preview["final_write_allowed"] is False
    assert preview["active_registry_created"] is False

    for item in preview["previews"]:
        assert item["registry_state"] == "active_registry_preview_only_locked"
        assert item["preview_only"] == 1
        assert item["final_write_allowed"] == 0
        assert item["preview_locked"] == 1
        assert item["download_locked"] == 1
        assert item["share_locked"] == 1
        assert item["delete_locked"] == 1
        assert item["restore_locked"] == 1


def test_gp291_300_promotion_approval_lock_board_blocks_approval_recording():
    board = get_promotion_approval_lock_board()

    assert board["ready"] is True
    assert board["approval_lock_count"] >= 2
    assert board["approval_recording_allowed"] is False
    assert board["all_approval_locks_closed"] is True

    for item in board["approval_locks"]:
        assert item["approval_state"] == "owner_approval_required_locked"
        assert item["approval_recording_allowed"] == 0
        assert item["owner_approval_required"] == 1


def test_gp291_300_promotion_receipts_are_draft_locked():
    ledger = get_promotion_receipt_draft_ledger()

    assert ledger["ready"] is True
    assert ledger["receipt_draft_count"] >= 2
    assert ledger["finalization_allowed"] is False
    assert ledger["all_receipts_draft_locked"] is True

    for item in ledger["receipt_drafts"]:
        assert len(item["receipt_hash"]) == 64
        assert item["receipt_state"] == "draft_locked"
        assert item["finalized"] == 0
        assert item["finalization_allowed"] == 0


def test_gp291_300_hash_continuity_is_preserved_from_quarantine_to_preview():
    board = get_promotion_hash_continuity_board()

    assert board["ready"] is True
    assert board["continuity_count"] >= 2
    assert board["all_hash_continuity_verified"] is True

    for item in board["continuity_rows"]:
        assert item["quarantine_hash"] == item["registry_preview_hash"]
        assert item["hash_continuity_verified"] == 1


def test_gp291_300_quarantine_release_is_prohibited():
    board = get_quarantine_release_prohibition_board()

    assert board["ready"] is True
    assert board["prohibition_count"] >= 2
    assert board["release_allowed"] is False
    assert board["all_release_prohibited"] is True

    for item in board["prohibitions"]:
        assert item["release_allowed"] == 0


def test_gp291_300_safety_blockers_preserve_danger_locks():
    board = get_registry_promotion_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "active_registry_final_write" in blocked_actions
    assert "registry_promotion" in blocked_actions
    assert "quarantine_release" in blocked_actions
    assert "promotion_approval_record" in blocked_actions
    assert "promotion_receipt_finalize" in blocked_actions
    assert "object_body_read" in blocked_actions
    assert "file_preview" in blocked_actions
    assert "file_download" in blocked_actions
    assert "file_share" in blocked_actions


def test_gp291_300_home_exposes_packs_and_locks():
    home = get_owner_file_registry_promotion_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["promotion_candidate_detection_allowed"] is True
    assert home["locks"]["active_registry_preview_allowed"] is True
    assert home["locks"]["active_registry_final_write_allowed"] is False
    assert home["locks"]["registry_promotion_allowed"] is False
    assert home["locks"]["file_download_unlocked"] is False


def test_gp291_300_readiness_checkpoint_declares_next_layer():
    checkpoint = get_owner_file_registry_promotion_lock_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_quarantine_layer_ready"] is True
    assert checkpoint["checks"]["candidate_board_ready"] is True
    assert checkpoint["checks"]["active_registry_preview_ready"] is True
    assert checkpoint["checks"]["quarantine_release_prohibited"] is True
    assert checkpoint["checks"]["final_registry_write_still_locked"] is True
    assert "OWNER FILE REGISTRY PROMOTION EXECUTION" in checkpoint["next_recommended_layer"]


def test_gp291_300_all_dangerous_locks_remain_false():
    assert LOCKS["promotion_candidate_detection_allowed"] is True
    assert LOCKS["active_registry_preview_allowed"] is True
    assert LOCKS["active_registry_final_write_allowed"] is False
    assert LOCKS["registry_promotion_allowed"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["promotion_approval_recording_allowed"] is False
    assert LOCKS["promotion_receipt_finalization_allowed"] is False
    assert LOCKS["object_body_read_allowed"] is False
    assert LOCKS["file_preview_unlocked"] is False
    assert LOCKS["file_download_unlocked"] is False
    assert LOCKS["file_share_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
    assert LOCKS["public_upload_unlocked"] is False
    assert LOCKS["beta_upload_unlocked"] is False
    assert LOCKS["provider_upload_unlocked"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["external_sync_unlocked"] is False


def test_gp291_300_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-file-registry-promotion-lock-layer",
        "/vault/owner-file-registry-promotion-lock-layer.json",
        "/vault/owner-file-registry-promotion-lock-shell.json",
        "/vault/quarantine-promotion-candidate-board.json",
        "/vault/promotion-eligibility-contract.json",
        "/vault/active-file-registry-preview.json",
        "/vault/promotion-approval-lock-board.json",
        "/vault/promotion-receipt-draft-ledger.json",
        "/vault/promotion-hash-continuity-board.json",
        "/vault/quarantine-release-prohibition-board.json",
        "/vault/registry-promotion-safety-blocker-board.json",
        "/vault/owner-file-registry-promotion-lock-readiness-checkpoint.json",
        "/vault/gp291-status.json",
        "/vault/gp300-status.json",
    ]

    for route in required_routes:
        assert route in app_text
