
from pathlib import Path

from vault.trash_restore_recovery_prep_layer_service import (
    LOCKS,
    get_owner_trash_approval_lock_board,
    get_recovery_receipt_draft_ledger,
    get_restore_eligibility_lock_board,
    get_restore_scope_contract,
    get_soft_delete_scope_contract,
    get_trash_eligibility_policy_board,
    get_trash_restore_recovery_prep_home,
    get_trash_restore_recovery_prep_readiness_checkpoint,
    get_trash_restore_route_payload_draft_builder,
    get_trash_restore_safety_blocker_board,
    validate_trash_restore_recovery_prep_layer,
)


def test_gp391_400_readiness_checkpoint_passes():
    result = validate_trash_restore_recovery_prep_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Trash restore and recovery prep layer" in result["readiness_label"]


def test_gp391_400_trash_candidates_are_owner_only_and_all_lifecycle_actions_locked():
    board = get_trash_eligibility_policy_board()

    assert board["ready"] is True
    assert board["candidate_count"] >= 2
    assert board["all_candidates_owner_only"] is True
    assert board["all_owner_approval_required"] is True
    assert board["no_soft_delete_execution_allowed"] is True
    assert board["no_hard_delete_allowed"] is True
    assert board["no_purge_allowed"] is True
    assert board["no_restore_execution_allowed"] is True
    assert board["no_physical_object_move_allowed"] is True

    for item in board["candidates"]:
        assert item["eligibility_state"] == "trash_restore_policy_candidate_owner_approval_required_locked"
        assert item["owner_only"] == 1
        assert item["owner_approval_required"] == 1
        assert item["soft_delete_execution_allowed"] == 0
        assert item["hard_delete_allowed"] == 0
        assert item["purge_allowed"] == 0
        assert item["restore_execution_allowed"] == 0
        assert item["physical_object_move_allowed"] == 0
        assert len(item["share_packet_hash"]) == 64


def test_gp391_400_soft_delete_scope_contract_is_prep_only():
    contract = get_soft_delete_scope_contract()

    assert contract["ready"] is True
    assert contract["scope"]["owner_only_trash_prep"] is True
    assert contract["scope"]["owner_approval_required"] is True
    assert contract["scope"]["soft_delete_execution_allowed"] is False
    assert contract["scope"]["trash_state_write_allowed"] is False
    assert contract["scope"]["hard_delete_allowed"] is False
    assert contract["scope"]["purge_allowed"] is False
    assert contract["scope"]["physical_object_move_allowed"] is False
    assert contract["scope"]["public_trash_allowed"] is False
    assert contract["scope"]["beta_trash_allowed"] is False
    assert contract["scope"]["file_body_return_allowed"] is False
    assert contract["scope"]["soft_delete_retention_days"] == 30


def test_gp391_400_restore_scope_contract_is_prep_only():
    contract = get_restore_scope_contract()

    assert contract["ready"] is True
    assert contract["scope"]["owner_only_restore_prep"] is True
    assert contract["scope"]["restore_review_required"] is True
    assert contract["scope"]["restore_execution_allowed"] is False
    assert contract["scope"]["restore_state_write_allowed"] is False
    assert contract["scope"]["physical_object_move_allowed"] is False
    assert contract["scope"]["public_restore_allowed"] is False
    assert contract["scope"]["beta_restore_allowed"] is False
    assert contract["scope"]["file_body_return_allowed"] is False
    assert contract["scope"]["restore_review_window_days"] == 7


def test_gp391_400_owner_trash_approval_locks_are_closed():
    board = get_owner_trash_approval_lock_board()

    assert board["ready"] is True
    assert board["approval_lock_count"] >= 2
    assert board["all_owner_approval_required"] is True
    assert board["all_approval_recording_locked"] is True
    assert board["all_soft_delete_execution_locked"] is True
    assert board["all_hard_delete_locked"] is True
    assert board["all_purge_locked"] is True

    for item in board["approval_locks"]:
        assert item["approval_state"] == "owner_trash_approval_required_locked"
        assert item["owner_approval_required"] == 1
        assert item["approval_recording_allowed"] == 0
        assert item["soft_delete_execution_allowed"] == 0
        assert item["hard_delete_allowed"] == 0
        assert item["purge_allowed"] == 0


def test_gp391_400_restore_eligibility_locks_are_closed():
    board = get_restore_eligibility_lock_board()

    assert board["ready"] is True
    assert board["restore_lock_count"] >= 2
    assert board["all_restore_review_required"] is True
    assert board["all_restore_execution_locked"] is True
    assert board["all_restore_state_write_locked"] is True
    assert board["all_physical_object_move_locked"] is True

    for item in board["restore_locks"]:
        assert item["restore_state"] == "restore_eligibility_waiting_for_future_trash_state_locked"
        assert item["restore_review_required"] == 1
        assert item["restore_execution_allowed"] == 0
        assert item["restore_state_write_allowed"] == 0
        assert item["physical_object_move_allowed"] == 0
        assert item["restore_review_window_days"] == 7


def test_gp391_400_recovery_receipts_are_draft_locked():
    ledger = get_recovery_receipt_draft_ledger()

    assert ledger["ready"] is True
    assert ledger["receipt_draft_count"] >= 2
    assert ledger["all_receipts_draft_locked"] is True
    assert ledger["all_soft_delete_execution_locked"] is True
    assert ledger["all_restore_execution_locked"] is True

    for item in ledger["receipt_drafts"]:
        assert item["receipt_state"] == "recovery_receipt_draft_locked"
        assert item["finalized"] == 0
        assert item["finalization_allowed"] == 0
        assert item["soft_delete_execution_allowed"] == 0
        assert item["restore_execution_allowed"] == 0
        assert len(item["receipt_hash"]) == 64


def test_gp391_400_route_payload_drafts_exclude_actions_body_and_path():
    builder = get_trash_restore_route_payload_draft_builder()

    assert builder["ready"] is True
    assert builder["payload_draft_count"] >= 2
    assert builder["metadata_only"] is True
    assert builder["trash_action_included"] is False
    assert builder["restore_action_included"] is False
    assert builder["purge_action_included"] is False
    assert builder["file_body_included"] is False
    assert builder["physical_path_included"] is False

    for payload in builder["payload_drafts"]:
        assert payload["metadata_only"] is True
        assert payload["display"]["trash_action"] == "LOCKED"
        assert payload["display"]["restore_action"] == "LOCKED"
        assert payload["display"]["purge_action"] == "LOCKED"
        assert payload["display"]["file_body"] == "LOCKED"
        assert payload["display"]["physical_path"] == "LOCKED"
        assert payload["locks"]["trash_action_included"] is False
        assert payload["locks"]["restore_action_included"] is False
        assert payload["locks"]["purge_action_included"] is False
        assert payload["locks"]["file_body_included"] is False
        assert payload["locks"]["physical_path_included"] is False
        assert len(payload["payload_hash"]) == 64


def test_gp391_400_safety_blockers_keep_destructive_actions_locked():
    board = get_trash_restore_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "soft_delete_execution" in blocked_actions
    assert "hard_delete" in blocked_actions
    assert "purge" in blocked_actions
    assert "restore_execution" in blocked_actions
    assert "physical_object_move" in blocked_actions
    assert "trash_state_write" in blocked_actions
    assert "restore_state_write" in blocked_actions
    assert "file_body_return" in blocked_actions
    assert "public_trash_restore" in blocked_actions
    assert "beta_trash_restore" in blocked_actions
    assert "quarantine_release" in blocked_actions
    assert "provider_upload" in blocked_actions
    assert "external_sync" in blocked_actions


def test_gp391_400_home_exposes_packs_and_locks():
    home = get_trash_restore_recovery_prep_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["trash_eligibility_metadata_allowed"] is True
    assert home["locks"]["soft_delete_scope_policy_allowed"] is True
    assert home["locks"]["restore_scope_policy_allowed"] is True
    assert home["locks"]["soft_delete_execution_allowed"] is False
    assert home["locks"]["hard_delete_allowed"] is False
    assert home["locks"]["purge_allowed"] is False
    assert home["locks"]["restore_execution_allowed"] is False
    assert home["locks"]["physical_object_move_allowed"] is False


def test_gp391_400_readiness_declares_next_layer():
    checkpoint = get_trash_restore_recovery_prep_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_controlled_share_grant_ready"] is True
    assert checkpoint["checks"]["trash_eligibility_ready"] is True
    assert checkpoint["checks"]["soft_delete_locked_on_candidates"] is True
    assert checkpoint["checks"]["hard_delete_and_purge_locked_on_candidates"] is True
    assert checkpoint["checks"]["restore_locked_on_candidates"] is True
    assert checkpoint["checks"]["physical_object_move_locked_on_candidates"] is True
    assert checkpoint["checks"]["recovery_receipts_draft_locked"] is True
    assert checkpoint["checks"]["trash_restore_payload_actions_locked"] is True
    assert checkpoint["checks"]["trash_restore_payload_body_path_locked"] is True
    assert checkpoint["checks"]["state_writes_still_locked"] is True
    assert "CONTROLLED SOFT DELETE EXECUTION" in checkpoint["next_recommended_layer"]


def test_gp391_400_allowed_features_are_recovery_prep_only():
    assert LOCKS["trash_eligibility_metadata_allowed"] is True
    assert LOCKS["soft_delete_scope_policy_allowed"] is True
    assert LOCKS["restore_scope_policy_allowed"] is True
    assert LOCKS["owner_trash_approval_lock_allowed"] is True
    assert LOCKS["restore_eligibility_lock_allowed"] is True
    assert LOCKS["recovery_receipt_draft_allowed"] is True
    assert LOCKS["trash_restore_route_payload_draft_allowed"] is True

    assert LOCKS["soft_delete_execution_allowed"] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False
    assert LOCKS["trash_state_write_allowed"] is False
    assert LOCKS["restore_state_write_allowed"] is False
    assert LOCKS["file_body_return_allowed"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["public_trash_unlocked"] is False
    assert LOCKS["beta_trash_unlocked"] is False
    assert LOCKS["public_restore_unlocked"] is False
    assert LOCKS["beta_restore_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["quarantine_object_move_allowed"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["external_sync_unlocked"] is False


def test_gp391_400_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/trash-restore-recovery-prep-layer",
        "/vault/trash-restore-recovery-prep-layer.json",
        "/vault/trash-restore-recovery-prep-shell.json",
        "/vault/trash-eligibility-policy-board.json",
        "/vault/soft-delete-scope-contract.json",
        "/vault/restore-scope-contract.json",
        "/vault/owner-trash-approval-lock-board.json",
        "/vault/restore-eligibility-lock-board.json",
        "/vault/recovery-receipt-draft-ledger.json",
        "/vault/trash-restore-route-payload-draft-builder.json",
        "/vault/trash-restore-safety-blocker-board.json",
        "/vault/trash-restore-recovery-prep-readiness-checkpoint.json",
        "/vault/gp391-status.json",
        "/vault/gp400-status.json",
    ]

    for route in required_routes:
        assert route in app_text
