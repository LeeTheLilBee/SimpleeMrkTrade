
from pathlib import Path

from vault.owner_file_object_write_quarantine_layer_service import (
    LOCKS,
    get_controlled_owner_object_write_contract,
    get_file_object_registry_insert_handoff,
    get_hash_verification_after_write_board,
    get_object_write_safety_blocker_board,
    get_owner_file_object_write_quarantine_home,
    get_owner_file_object_write_quarantine_readiness_checkpoint,
    get_owner_write_queue_resolution_lock,
    get_quarantine_object_body_writer,
    get_quarantine_object_manifest_ledger,
    get_write_failure_rollback_preview,
    validate_owner_file_object_write_quarantine_layer,
)


def test_gp281_290_readiness_checkpoint_passes():
    result = validate_owner_file_object_write_quarantine_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Owner file object write quarantine layer" in result["readiness_label"]


def test_gp281_290_controlled_write_contract_allows_only_quarantine():
    contract = get_controlled_owner_object_write_contract()

    assert contract["ready"] is True
    assert contract["contract"]["source_must_be_owner_upload_intake_draft"] is True
    assert contract["contract"]["write_target_must_be_quarantine"] is True
    assert contract["contract"]["sha256_hash_must_match"] is True
    assert contract["contract"]["manifest_required"] is True
    assert contract["contract"]["registry_handoff_preview_only"] is True
    assert contract["contract"]["quarantine_release_allowed"] is False
    assert contract["contract"]["raw_user_upload_endpoint_allowed"] is False
    assert contract["contract"]["provider_storage_required"] is False
    assert contract["contract"]["object_body_read_allowed"] is False


def test_gp281_290_quarantine_writer_physically_writes_locked_objects():
    writer = get_quarantine_object_body_writer()

    assert writer["ready"] is True
    assert writer["written_object_count"] >= 2
    assert writer["raw_user_upload_endpoint_allowed"] is False
    assert writer["object_body_read_allowed"] is False

    for item in writer["objects"]:
        path = Path(item["relative_quarantine_path"])
        assert path.exists()
        assert item["hash_verified"] == 1
        assert item["quarantine_state"] == "written_quarantine_locked"
        assert item["preview_locked"] == 1
        assert item["download_locked"] == 1
        assert item["share_locked"] == 1
        assert item["delete_locked"] == 1
        assert item["restore_locked"] == 1
        assert item["registry_promotion_allowed"] == 0


def test_gp281_290_registry_insert_handoff_is_preview_only_locked():
    handoff = get_file_object_registry_insert_handoff()

    assert handoff["ready"] is True
    assert handoff["candidate_count"] >= 2
    assert handoff["registry_promotion_allowed"] is False
    assert handoff["handoff_mode"] == "preview_only_locked"

    for item in handoff["candidates"]:
        assert item["hash_verified"] == 1
        assert item["registry_promotion_allowed"] == 0


def test_gp281_290_hash_verification_after_write_passes():
    board = get_hash_verification_after_write_board()

    assert board["ready"] is True
    assert board["verification_count"] >= 2
    assert board["all_hashes_verified"] is True

    for item in board["verifications"]:
        assert item["expected_hash"] == item["actual_hash"]
        assert item["verified"] == 1


def test_gp281_290_manifest_ledger_exists_but_not_finalized():
    ledger = get_quarantine_object_manifest_ledger()

    assert ledger["ready"] is True
    assert ledger["manifest_count"] >= 2
    assert ledger["finalized"] is False
    assert ledger["manifest_finalization_allowed"] is False

    for item in ledger["manifests"]:
        manifest_path = Path(item["manifest_relative_path"])
        assert manifest_path.exists()
        assert item["finalized"] == 0
        assert len(item["manifest_hash"]) == 64


def test_gp281_290_rollback_preview_does_not_execute():
    rollback = get_write_failure_rollback_preview()

    assert rollback["ready"] is True
    assert rollback["rollback_preview_available"] is True
    assert rollback["rollback_execution_allowed"] is False
    assert rollback["failure_count"] == 0


def test_gp281_290_owner_write_queue_resolution_is_locked():
    lock = get_owner_write_queue_resolution_lock()

    assert lock["ready"] is True
    assert lock["resolution_allowed"] is False
    assert lock["quarantine_release_allowed"] is False
    assert lock["registry_promotion_allowed"] is False
    assert len(lock["queued_written_objects"]) >= 2

    for item in lock["queued_written_objects"]:
        assert item["quarantine_state"] == "written_quarantine_locked"
        assert item["registry_promotion_allowed"] == 0


def test_gp281_290_safety_blockers_preserve_danger_locks():
    board = get_object_write_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "raw_user_upload_endpoint" in blocked_actions
    assert "public_upload" in blocked_actions
    assert "beta_upload" in blocked_actions
    assert "provider_upload" in blocked_actions
    assert "object_body_read" in blocked_actions
    assert "file_preview" in blocked_actions
    assert "file_download" in blocked_actions
    assert "quarantine_release" in blocked_actions


def test_gp281_290_home_exposes_packs_and_locks():
    home = get_owner_file_object_write_quarantine_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["controlled_quarantine_write_allowed"] is True
    assert home["locks"]["raw_user_upload_endpoint_allowed"] is False
    assert home["locks"]["object_body_read_allowed"] is False
    assert home["locks"]["file_download_unlocked"] is False


def test_gp281_290_readiness_checkpoint_declares_next_layer():
    checkpoint = get_owner_file_object_write_quarantine_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_storage_foundation_ready"] is True
    assert checkpoint["checks"]["previous_upload_intake_ready"] is True
    assert checkpoint["checks"]["quarantine_writer_ready"] is True
    assert checkpoint["checks"]["hash_verification_ready"] is True
    assert checkpoint["checks"]["manifest_ledger_ready"] is True
    assert checkpoint["checks"]["raw_user_upload_still_locked"] is True
    assert "OWNER FILE REGISTRY PROMOTION" in checkpoint["next_recommended_layer"]


def test_gp281_290_all_dangerous_locks_remain_false():
    assert LOCKS["controlled_quarantine_write_allowed"] is True
    assert LOCKS["raw_user_upload_endpoint_allowed"] is False
    assert LOCKS["public_upload_unlocked"] is False
    assert LOCKS["beta_upload_unlocked"] is False
    assert LOCKS["provider_upload_unlocked"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["object_body_read_allowed"] is False
    assert LOCKS["object_body_preview_allowed"] is False
    assert LOCKS["file_download_unlocked"] is False
    assert LOCKS["file_share_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
    assert LOCKS["external_sync_unlocked"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["registry_promotion_allowed"] is False


def test_gp281_290_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-file-object-write-quarantine-layer",
        "/vault/owner-file-object-write-quarantine-layer.json",
        "/vault/owner-file-object-write-quarantine-shell.json",
        "/vault/controlled-owner-object-write-contract.json",
        "/vault/quarantine-object-body-writer.json",
        "/vault/file-object-registry-insert-handoff.json",
        "/vault/hash-verification-after-write-board.json",
        "/vault/quarantine-object-manifest-ledger.json",
        "/vault/write-failure-rollback-preview.json",
        "/vault/owner-write-queue-resolution-lock.json",
        "/vault/object-write-safety-blocker-board.json",
        "/vault/owner-file-object-write-quarantine-readiness-checkpoint.json",
        "/vault/gp281-status.json",
        "/vault/gp290-status.json",
    ]

    for route in required_routes:
        assert route in app_text
