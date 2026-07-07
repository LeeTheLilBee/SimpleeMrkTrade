
from pathlib import Path

from vault.controlled_soft_delete_execution_layer_service import (
    LOCKS,
    get_controlled_soft_delete_execution_home,
    get_controlled_soft_delete_execution_readiness_checkpoint,
    get_owner_soft_delete_approval_execution_board,
    get_post_delete_access_lock_board,
    get_restore_handoff_preview_board,
    get_soft_delete_execution_scope_contract,
    get_soft_delete_receipt_finalization_board,
    get_soft_delete_safety_blocker_board,
    get_soft_delete_state_writer,
    get_trash_lifecycle_ledger,
    validate_controlled_soft_delete_execution_layer,
)


def test_gp401_410_readiness_checkpoint_passes():
    result = validate_controlled_soft_delete_execution_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Controlled soft delete execution layer" in result["readiness_label"]


def test_gp401_410_scope_contract_allows_metadata_soft_delete_only():
    contract = get_soft_delete_execution_scope_contract()

    assert contract["ready"] is True
    assert contract["scope"]["controlled_metadata_soft_delete_execution_allowed"] is True
    assert contract["scope"]["owner_only"] is True
    assert contract["scope"]["metadata_state_write_allowed"] is True
    assert contract["scope"]["trash_lifecycle_ledger_allowed"] is True
    assert contract["scope"]["soft_delete_receipt_finalization_allowed"] is True
    assert contract["scope"]["retention_days"] == 30
    assert contract["scope"]["hard_delete_allowed"] is False
    assert contract["scope"]["purge_allowed"] is False
    assert contract["scope"]["restore_execution_allowed"] is False
    assert contract["scope"]["physical_object_move_allowed"] is False
    assert contract["scope"]["physical_object_delete_allowed"] is False
    assert contract["scope"]["file_body_return_allowed"] is False
    assert contract["scope"]["raw_file_bytes_returned_by_json"] is False


def test_gp401_410_owner_approval_execution_records_soft_delete_only():
    board = get_owner_soft_delete_approval_execution_board()

    assert board["ready"] is True
    assert board["approval_execution_count"] >= 2
    assert board["all_owner_only"] is True
    assert board["all_approvals_executed"] is True
    assert board["controlled_soft_delete_count"] >= 2
    assert board["no_hard_delete_allowed"] is True
    assert board["no_purge_allowed"] is True

    for item in board["approval_executions"]:
        assert item["approval_state"] == "owner_soft_delete_approval_executed_for_metadata_soft_delete"
        assert item["owner_only"] == 1
        assert item["approval_executed"] == 1
        assert item["controlled_soft_delete_allowed"] == 1
        assert item["hard_delete_allowed"] == 0
        assert item["purge_allowed"] == 0


def test_gp401_410_soft_delete_state_writer_marks_metadata_soft_deleted():
    writer = get_soft_delete_state_writer()

    assert writer["ready"] is True
    assert writer["state_record_count"] >= 2
    assert writer["all_records_soft_deleted"] is True
    assert writer["all_hard_delete_locked"] is True
    assert writer["all_purge_locked"] is True
    assert writer["all_restore_execution_locked"] is True
    assert writer["all_physical_object_move_locked"] is True
    assert writer["all_file_body_return_locked"] is True

    for item in writer["state_records"]:
        assert item["lifecycle_state"] == "soft_deleted_metadata_only"
        assert item["soft_deleted"] == 1
        assert item["retention_days"] == 30
        assert item["hard_delete_allowed"] == 0
        assert item["purge_allowed"] == 0
        assert item["restore_execution_allowed"] == 0
        assert item["physical_object_move_allowed"] == 0
        assert item["file_body_return_allowed"] == 0
        assert len(item["state_hash"]) == 64


def test_gp401_410_trash_lifecycle_ledger_is_metadata_only_no_destructive_action():
    ledger = get_trash_lifecycle_ledger()

    assert ledger["ready"] is True
    assert ledger["lifecycle_event_count"] >= 2
    assert ledger["all_metadata_only"] is True
    assert ledger["no_physical_objects_moved"] is True
    assert ledger["no_hard_deletes"] is True
    assert ledger["no_purges"] is True

    for item in ledger["lifecycle_events"]:
        assert item["event_type"] == "metadata_soft_delete"
        assert item["event_state"] == "recorded_metadata_soft_delete_no_physical_move"
        assert item["metadata_only"] == 1
        assert item["physical_object_moved"] == 0
        assert item["hard_deleted"] == 0
        assert item["purged"] == 0
        assert len(item["lifecycle_hash"]) == 64


def test_gp401_410_soft_delete_receipts_finalized():
    board = get_soft_delete_receipt_finalization_board()

    assert board["ready"] is True
    assert board["final_receipt_count"] >= 2
    assert board["all_receipts_finalized"] is True

    for item in board["final_receipts"]:
        assert item["finalized"] == 1
        assert item["receipt_scope"] == "controlled_metadata_soft_delete_execution"
        assert len(item["final_receipt_hash"]) == 64


def test_gp401_410_post_delete_access_locks_preview_download_share_and_raw_bytes():
    board = get_post_delete_access_lock_board()

    assert board["ready"] is True
    assert board["access_lock_count"] >= 2
    assert board["all_preview_locked"] is True
    assert board["all_download_locked"] is True
    assert board["all_share_locked"] is True
    assert board["all_restore_preview_allowed"] is True
    assert board["all_public_beta_locked"] is True
    assert board["all_raw_file_bytes_json_locked"] is True

    for item in board["access_locks"]:
        assert item["access_state"] == "post_soft_delete_access_locked_restore_preview_only"
        assert item["preview_allowed"] == 0
        assert item["download_allowed"] == 0
        assert item["share_allowed"] == 0
        assert item["restore_preview_allowed"] == 1
        assert item["public_access_allowed"] == 0
        assert item["beta_access_allowed"] == 0
        assert item["raw_file_bytes_json_allowed"] == 0


def test_gp401_410_restore_handoff_preview_is_ready_but_execution_locked():
    board = get_restore_handoff_preview_board()

    assert board["ready"] is True
    assert board["restore_handoff_count"] >= 2
    assert board["all_restore_review_required"] is True
    assert board["all_restore_execution_locked"] is True
    assert board["all_restore_state_write_locked"] is True
    assert board["all_physical_object_move_locked"] is True

    for item in board["restore_handoffs"]:
        assert item["restore_state"] == "restore_handoff_preview_ready_execution_locked"
        assert item["restore_review_required"] == 1
        assert item["restore_execution_allowed"] == 0
        assert item["restore_state_write_allowed"] == 0
        assert item["physical_object_move_allowed"] == 0
        assert item["restore_review_window_days"] == 7


def test_gp401_410_safety_blockers_keep_destructive_actions_locked():
    board = get_soft_delete_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "hard_delete" in blocked_actions
    assert "purge" in blocked_actions
    assert "restore_execution" in blocked_actions
    assert "physical_object_move" in blocked_actions
    assert "physical_object_delete" in blocked_actions
    assert "file_body_return" in blocked_actions
    assert "public_delete_restore" in blocked_actions
    assert "beta_delete_restore" in blocked_actions
    assert "quarantine_release" in blocked_actions
    assert "provider_upload" in blocked_actions
    assert "external_sync" in blocked_actions


def test_gp401_410_home_exposes_packs_and_locks():
    home = get_controlled_soft_delete_execution_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["controlled_metadata_soft_delete_execution_allowed"] is True
    assert home["locks"]["soft_delete_state_write_allowed"] is True
    assert home["locks"]["trash_lifecycle_ledger_allowed"] is True
    assert home["locks"]["hard_delete_allowed"] is False
    assert home["locks"]["purge_allowed"] is False
    assert home["locks"]["restore_execution_allowed"] is False
    assert home["locks"]["physical_object_move_allowed"] is False
    assert home["locks"]["raw_file_bytes_returned_by_json"] is False


def test_gp401_410_readiness_declares_next_layer():
    checkpoint = get_controlled_soft_delete_execution_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_trash_restore_recovery_prep_ready"] is True
    assert checkpoint["checks"]["controlled_soft_delete_records_written"] is True
    assert checkpoint["checks"]["all_state_records_soft_deleted"] is True
    assert checkpoint["checks"]["lifecycle_metadata_only"] is True
    assert checkpoint["checks"]["lifecycle_no_physical_delete_or_move"] is True
    assert checkpoint["checks"]["soft_delete_receipts_finalized"] is True
    assert checkpoint["checks"]["post_delete_preview_download_share_locked"] is True
    assert checkpoint["checks"]["post_delete_restore_preview_allowed"] is True
    assert checkpoint["checks"]["restore_execution_still_locked"] is True
    assert checkpoint["checks"]["hard_delete_purge_still_locked"] is True
    assert checkpoint["checks"]["physical_object_move_still_locked"] is True
    assert "CONTROLLED RESTORE EXECUTION" in checkpoint["next_recommended_layer"]


def test_gp401_410_allowed_features_are_soft_delete_only():
    assert LOCKS["controlled_metadata_soft_delete_execution_allowed"] is True
    assert LOCKS["soft_delete_state_write_allowed"] is True
    assert LOCKS["trash_lifecycle_ledger_allowed"] is True
    assert LOCKS["soft_delete_receipt_finalization_allowed"] is True
    assert LOCKS["post_delete_access_lock_allowed"] is True
    assert LOCKS["restore_handoff_preview_allowed"] is True

    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["restore_state_write_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False
    assert LOCKS["physical_object_delete_allowed"] is False
    assert LOCKS["file_body_return_allowed"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["public_delete_unlocked"] is False
    assert LOCKS["beta_delete_unlocked"] is False
    assert LOCKS["public_restore_unlocked"] is False
    assert LOCKS["beta_restore_unlocked"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["quarantine_object_move_allowed"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["external_sync_unlocked"] is False


def test_gp401_410_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/controlled-soft-delete-execution-layer",
        "/vault/controlled-soft-delete-execution-layer.json",
        "/vault/controlled-soft-delete-execution-shell.json",
        "/vault/soft-delete-execution-scope-contract.json",
        "/vault/owner-soft-delete-approval-execution-board.json",
        "/vault/soft-delete-state-writer.json",
        "/vault/trash-lifecycle-ledger.json",
        "/vault/soft-delete-receipt-finalization-board.json",
        "/vault/post-delete-access-lock-board.json",
        "/vault/restore-handoff-preview-board.json",
        "/vault/soft-delete-safety-blocker-board.json",
        "/vault/controlled-soft-delete-execution-readiness-checkpoint.json",
        "/vault/gp401-status.json",
        "/vault/gp410-status.json",
    ]

    for route in required_routes:
        assert route in app_text
