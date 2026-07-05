
from pathlib import Path

from vault.owner_upload_intake_lock_layer_service import (
    ALLOWED_EXTENSIONS,
    BLOCKED_EXTENSIONS,
    LOCKS,
    MAX_FILE_SIZE_BYTES,
    get_allowed_file_type_size_contract,
    get_duplicate_hash_detection_preview_board,
    get_owner_upload_intake_home,
    get_owner_upload_intake_lock_readiness_checkpoint,
    get_owner_upload_queue_preview,
    get_quarantine_intake_status_lock,
    get_upload_intake_safety_blocker_board,
    get_upload_receipt_draft_builder_lock,
    get_upload_request_draft_registry,
    get_upload_validation_policy_board,
    preview_duplicate_hash,
    validate_owner_upload_intake_lock_layer,
    validate_upload_metadata,
)


def test_gp271_280_readiness_checkpoint_passes():
    result = validate_owner_upload_intake_lock_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Owner upload intake lock layer" in result["readiness_label"]


def test_gp271_280_upload_request_registry_is_metadata_only_and_locked():
    registry = get_upload_request_draft_registry()

    assert registry["ready"] is True
    assert registry["draft_count"] >= 2
    assert registry["registry_contract"]["metadata_only"] is True
    assert registry["registry_contract"]["object_body_not_stored"] is True
    assert registry["registry_contract"]["upload_allowed"] is False
    assert registry["registry_contract"]["receipt_finalization_allowed"] is False

    for draft in registry["drafts"]:
        assert draft["upload_allowed"] == 0
        assert draft["object_body_written"] == 0
        assert draft["receipt_finalization_allowed"] == 0
        assert draft["quarantine_state"] == "quarantine_locked"


def test_gp271_280_validation_policy_board_blocks_upload():
    board = get_upload_validation_policy_board()

    assert board["ready"] is True
    assert board["policy_count"] >= 8
    assert board["all_policies_block_upload"] is True


def test_gp271_280_allowed_file_type_and_size_contract_blocks_executables():
    contract = get_allowed_file_type_size_contract()

    assert contract["ready"] is True
    assert ".pdf" in contract["allowed_extensions"]
    assert ".csv" in contract["allowed_extensions"]
    assert ".exe" in contract["blocked_extensions"]
    assert ".sh" in contract["blocked_extensions"]
    assert contract["max_file_size_bytes"] == MAX_FILE_SIZE_BYTES
    assert contract["real_upload_allowed"] is False
    assert set(BLOCKED_EXTENSIONS).isdisjoint(set(ALLOWED_EXTENSIONS))


def test_gp271_280_validate_upload_metadata_accepts_safe_metadata_but_upload_stays_locked():
    safe = validate_upload_metadata(
        original_filename="Operating Agreement.pdf",
        mission_lane="trust",
        folder_key="trust",
        size_bytes=1000,
        sha256_hash="a" * 64,
    )

    assert safe["valid"] is True
    assert safe["extension"] == ".pdf"
    assert safe["mime_type"] == "application/pdf"

    bad = validate_upload_metadata(
        original_filename="../bad/script.sh",
        mission_lane="trust",
        folder_key="trust",
        size_bytes=1000,
        sha256_hash="not-a-hash",
    )

    assert bad["valid"] is False
    assert "extension_not_allowed" in bad["errors"]
    assert "blocked_extension" in bad["errors"]
    assert "invalid_sha256_hash" in bad["errors"]
    assert "filename_will_be_sanitized" in bad["warnings"]


def test_gp271_280_duplicate_hash_detection_is_preview_only():
    board = get_duplicate_hash_detection_preview_board()

    assert board["ready"] is True
    assert board["preview_only"] is True
    assert board["duplicate_resolution_allowed"] is False
    assert board["object_body_scan_allowed"] is False

    invalid = preview_duplicate_hash("bad")
    assert invalid["valid_hash"] is False
    assert invalid["preview_only"] is True
    assert invalid["duplicate_resolution_allowed"] is False


def test_gp271_280_quarantine_status_lock_keeps_everything_locked():
    lock = get_quarantine_intake_status_lock()

    assert lock["ready"] is True
    assert lock["all_queued_items_quarantine_locked"] is True
    assert lock["release_allowed"] is False

    for item in lock["queued_items"]:
        assert item["quarantine_state"] == "quarantine_locked"
        assert item["upload_allowed"] == 0
        assert item["object_body_written"] == 0


def test_gp271_280_owner_upload_queue_preview_is_not_real_upload():
    queue = get_owner_upload_queue_preview()

    assert queue["ready"] is True
    assert queue["queue_count"] >= 2
    assert queue["queue_mode"] == "metadata_only_preview"
    assert queue["real_upload_allowed"] is False

    for item in queue["queue"]:
        assert item["object_body_written"] == 0
        assert item["upload_allowed"] == 0


def test_gp271_280_upload_receipt_draft_builder_is_locked():
    builder = get_upload_receipt_draft_builder_lock()

    assert builder["ready"] is True
    assert builder["receipt_draft_count"] >= 2
    assert builder["finalization_allowed"] is False
    assert builder["upload_allowed"] is False

    for draft in builder["receipt_drafts"]:
        assert draft["finalized"] is False
        assert draft["material"]["upload_allowed"] is False
        assert draft["material"]["object_body_written"] is False
        assert draft["material"]["receipt_finalization_allowed"] is False


def test_gp271_280_safety_blockers_preserve_all_locks():
    board = get_upload_intake_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "real_upload" in blocked_actions
    assert "object_body_write" in blocked_actions
    assert "object_body_read" in blocked_actions
    assert "public_upload" in blocked_actions
    assert "beta_upload" in blocked_actions
    assert "provider_upload" in blocked_actions
    assert "file_download" in blocked_actions


def test_gp271_280_home_exposes_packs_and_lock_state():
    home = get_owner_upload_intake_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["owner_upload_intake_foundation"] is True
    assert home["locks"]["real_upload_unlocked"] is False
    assert home["locks"]["object_body_write_allowed"] is False
    assert home["locks"]["file_download_unlocked"] is False


def test_gp271_280_readiness_checkpoint_declares_next_layer():
    checkpoint = get_owner_upload_intake_lock_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_storage_foundation_ready"] is True
    assert checkpoint["checks"]["real_upload_still_locked"] is True
    assert checkpoint["checks"]["object_body_write_still_locked"] is True
    assert "OWNER FILE OBJECT WRITE QUARANTINE" in checkpoint["next_recommended_layer"]


def test_gp271_280_all_dangerous_locks_false():
    assert LOCKS["real_upload_unlocked"] is False
    assert LOCKS["object_body_write_allowed"] is False
    assert LOCKS["object_body_read_allowed"] is False
    assert LOCKS["public_upload_unlocked"] is False
    assert LOCKS["beta_upload_unlocked"] is False
    assert LOCKS["provider_upload_unlocked"] is False
    assert LOCKS["file_preview_unlocked"] is False
    assert LOCKS["file_download_unlocked"] is False
    assert LOCKS["file_share_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
    assert LOCKS["external_sync_unlocked"] is False
    assert LOCKS["upload_receipt_finalization_allowed"] is False


def test_gp271_280_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-upload-intake-lock-layer",
        "/vault/owner-upload-intake-lock-layer.json",
        "/vault/owner-upload-intake-lock-shell.json",
        "/vault/upload-request-draft-registry.json",
        "/vault/upload-validation-policy-board.json",
        "/vault/allowed-file-type-size-contract.json",
        "/vault/duplicate-hash-detection-preview-board.json",
        "/vault/quarantine-intake-status-lock.json",
        "/vault/owner-upload-queue-preview.json",
        "/vault/upload-receipt-draft-builder-lock.json",
        "/vault/upload-intake-safety-blocker-board.json",
        "/vault/owner-upload-intake-lock-readiness-checkpoint.json",
        "/vault/gp271-status.json",
        "/vault/gp280-status.json",
    ]

    for route in required_routes:
        assert route in app_text
