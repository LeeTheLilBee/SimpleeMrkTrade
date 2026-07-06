
from pathlib import Path

from vault.owner_file_registry_promotion_execution_layer_service import (
    LOCKS,
    get_active_file_registry_writer,
    get_active_registry_hash_continuity_board,
    get_owner_approval_execution_contract,
    get_owner_file_registry_promotion_execution_home,
    get_owner_file_registry_promotion_execution_readiness_checkpoint,
    get_promotion_execution_rollback_preview,
    get_promotion_execution_safety_blocker_board,
    get_promotion_receipt_finalization_board,
    get_quarantine_hold_after_promotion_contract,
    get_registry_promotion_execution_ledger,
    validate_owner_file_registry_promotion_execution_layer,
)


def test_gp301_310_readiness_checkpoint_passes():
    result = validate_owner_file_registry_promotion_execution_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Owner file registry promotion execution layer" in result["readiness_label"]


def test_gp301_310_owner_approval_execution_contract_is_metadata_only():
    contract = get_owner_approval_execution_contract()

    assert contract["ready"] is True
    assert contract["contract"]["writes_active_metadata_registry"] is True
    assert contract["contract"]["finalizes_metadata_promotion_receipt"] is True
    assert contract["contract"]["reads_object_body"] is False
    assert contract["contract"]["moves_physical_object"] is False
    assert contract["contract"]["releases_quarantine"] is False
    assert contract["contract"]["unlocks_download"] is False


def test_gp301_310_active_file_registry_writer_creates_metadata_only_records():
    writer = get_active_file_registry_writer()

    assert writer["ready"] is True
    assert writer["active_file_count"] >= 2
    assert writer["metadata_only"] is True
    assert writer["object_body_read_allowed"] is False
    assert writer["quarantine_held"] is True

    for item in writer["active_files"]:
        assert item["registry_state"] == "active_registered_metadata_only_quarantine_held"
        assert item["metadata_only"] == 1
        assert item["quarantine_held"] == 1
        assert item["object_body_read_locked"] == 1
        assert item["preview_locked"] == 1
        assert item["download_locked"] == 1
        assert item["share_locked"] == 1
        assert item["delete_locked"] == 1
        assert item["restore_locked"] == 1
        assert len(item["sha256_hash"]) == 64


def test_gp301_310_execution_ledger_records_no_body_read_or_release():
    ledger = get_registry_promotion_execution_ledger()

    assert ledger["ready"] is True
    assert ledger["execution_count"] >= 2
    assert ledger["all_metadata_writes_executed"] is True
    assert ledger["no_object_body_reads_executed"] is True
    assert ledger["no_quarantine_releases_executed"] is True

    for item in ledger["executions"]:
        assert item["execution_state"] == "metadata_registry_promotion_executed_quarantine_held"
        assert item["metadata_write_executed"] == 1
        assert item["object_body_read_executed"] == 0
        assert item["quarantine_release_executed"] == 0
        assert item["receipt_finalized"] == 1


def test_gp301_310_promotion_receipts_are_finalized_for_metadata_promotion():
    board = get_promotion_receipt_finalization_board()

    assert board["ready"] is True
    assert board["final_receipt_count"] >= 2
    assert board["all_receipts_finalized"] is True
    assert board["receipt_scope"] == "metadata_only_registry_promotion"

    for item in board["final_receipts"]:
        assert item["finalized"] == 1
        assert item["finalization_state"] == "finalized_metadata_only_promotion_receipt"
        assert len(item["final_receipt_hash"]) == 64


def test_gp301_310_active_registry_hash_continuity_is_verified():
    board = get_active_registry_hash_continuity_board()

    assert board["ready"] is True
    assert board["continuity_count"] >= 2
    assert board["all_hash_continuity_verified"] is True

    for item in board["continuity_rows"]:
        assert item["registry_hash"] == item["source_hash"]
        assert item["verified"] == 1


def test_gp301_310_quarantine_hold_after_promotion_remains_locked():
    hold = get_quarantine_hold_after_promotion_contract()

    assert hold["ready"] is True
    assert hold["hold_count"] >= 2
    assert hold["all_objects_quarantine_held"] is True
    assert hold["release_allowed"] is False
    assert hold["object_move_allowed"] is False

    for item in hold["holds"]:
        assert item["quarantine_held"] == 1
        assert item["release_allowed"] == 0
        assert item["object_move_allowed"] == 0


def test_gp301_310_rollback_preview_exists_but_does_not_execute():
    rollback = get_promotion_execution_rollback_preview()

    assert rollback["ready"] is True
    assert rollback["rollback_preview_count"] >= 2
    assert rollback["rollback_available"] is True
    assert rollback["rollback_executed"] is False
    assert rollback["all_rollbacks_preview_only"] is True

    for item in rollback["rollback_previews"]:
        assert item["rollback_available"] == 1
        assert item["rollback_executed"] == 0


def test_gp301_310_safety_blockers_keep_danger_actions_locked():
    board = get_promotion_execution_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "object_body_read" in blocked_actions
    assert "file_preview" in blocked_actions
    assert "file_download" in blocked_actions
    assert "file_share" in blocked_actions
    assert "file_delete" in blocked_actions
    assert "file_restore" in blocked_actions
    assert "quarantine_release" in blocked_actions
    assert "quarantine_object_move" in blocked_actions
    assert "external_sync" in blocked_actions


def test_gp301_310_home_exposes_packs_and_locks():
    home = get_owner_file_registry_promotion_execution_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["metadata_only_active_registry_write_allowed"] is True
    assert home["locks"]["registry_promotion_execution_allowed"] is True
    assert home["locks"]["object_body_read_allowed"] is False
    assert home["locks"]["file_download_unlocked"] is False
    assert home["locks"]["quarantine_release_allowed"] is False


def test_gp301_310_readiness_checkpoint_declares_next_layer():
    checkpoint = get_owner_file_registry_promotion_execution_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_promotion_lock_layer_ready"] is True
    assert checkpoint["checks"]["active_registry_writer_ready"] is True
    assert checkpoint["checks"]["execution_ledger_ready"] is True
    assert checkpoint["checks"]["no_object_body_reads_executed"] is True
    assert checkpoint["checks"]["no_quarantine_releases_executed"] is True
    assert checkpoint["checks"]["promotion_receipts_finalized"] is True
    assert checkpoint["checks"]["quarantine_hold_ready"] is True
    assert "OWNER FILE DETAIL METADATA VIEW" in checkpoint["next_recommended_layer"]


def test_gp301_310_allowed_execution_is_only_metadata_registry_and_receipts():
    assert LOCKS["metadata_only_active_registry_write_allowed"] is True
    assert LOCKS["registry_promotion_execution_allowed"] is True
    assert LOCKS["promotion_receipt_finalization_allowed"] is True

    assert LOCKS["object_body_read_allowed"] is False
    assert LOCKS["object_body_preview_allowed"] is False
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
    assert LOCKS["raw_user_upload_endpoint_allowed"] is False


def test_gp301_310_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-file-registry-promotion-execution-layer",
        "/vault/owner-file-registry-promotion-execution-layer.json",
        "/vault/owner-file-registry-promotion-execution-shell.json",
        "/vault/owner-approval-execution-contract.json",
        "/vault/active-file-registry-writer.json",
        "/vault/registry-promotion-execution-ledger.json",
        "/vault/promotion-receipt-finalization-board.json",
        "/vault/active-registry-hash-continuity-board.json",
        "/vault/quarantine-hold-after-promotion-contract.json",
        "/vault/promotion-execution-rollback-preview.json",
        "/vault/promotion-execution-safety-blocker-board.json",
        "/vault/owner-file-registry-promotion-execution-readiness-checkpoint.json",
        "/vault/gp301-status.json",
        "/vault/gp310-status.json",
    ]

    for route in required_routes:
        assert route in app_text
