
from pathlib import Path

from vault.owner_owned_file_storage_foundation_layer_service import (
    BLOCKERS,
    FOLDER_MAP,
    LOCKS,
    calculate_sha256_bytes,
    get_file_hash_integrity_contract,
    get_file_object_metadata_registry,
    get_file_storage_safety_blocker_board,
    get_mission_lane_folder_map,
    get_original_filename_safe_stored_name_contract,
    get_owner_owned_file_storage_home,
    get_owner_owned_file_storage_readiness_checkpoint,
    get_physical_object_folder_registry,
    get_upload_receipt_draft_lock,
    get_vault_storage_root_contract,
    infer_mime_type,
    sanitize_original_filename,
    validate_owner_owned_file_storage_foundation,
)


def test_gp261_270_readiness_checkpoint_passes():
    result = validate_owner_owned_file_storage_foundation()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Owner-owned file storage foundation" in result["readiness_label"]


def test_gp261_270_storage_root_is_owner_owned_not_provider_required():
    root = get_vault_storage_root_contract()

    assert root["ready"] is True
    assert root["contract"]["vault_owns_file_record"] is True
    assert root["contract"]["vault_owns_receipt"] is True
    assert root["contract"]["vault_owns_hash"] is True
    assert root["contract"]["external_provider_is_authority"] is False
    assert root["storage_roots"][0]["external_provider_required"] == 0
    assert root["storage_roots"][0]["provider_name"] == "none_required"


def test_gp261_270_physical_folder_registry_created_and_locked():
    folders = get_physical_object_folder_registry()

    assert folders["ready"] is True
    assert folders["folder_count"] >= len(FOLDER_MAP)
    assert folders["physical_storage_created"] is True
    assert folders["object_body_operations_allowed"] is False

    for folder in folders["folders"]:
        assert folder["preview_locked"] == 1
        assert folder["download_locked"] == 1
        assert folder["delete_locked"] == 1


def test_gp261_270_metadata_registry_schema_is_locked_before_upload():
    registry = get_file_object_metadata_registry()

    assert registry["ready"] is True
    assert registry["schema_contract"]["file_object_id"] == "required"
    assert registry["schema_contract"]["sha256_hash"] == "required"
    assert registry["schema_contract"]["preview_locked"] is True
    assert registry["schema_contract"]["download_locked"] is True
    assert registry["schema_contract"]["share_locked"] is True
    assert registry["schema_contract"]["delete_locked"] is True
    assert registry["schema_contract"]["restore_locked"] is True


def test_gp261_270_hash_integrity_contract_uses_sha256():
    contract = get_file_hash_integrity_contract()

    assert contract["ready"] is True
    assert contract["hash_algorithm"] == "sha256"
    assert contract["hash_required_before_storage_receipt"] is True
    assert contract["hash_required_before_download_unlock"] is True
    assert calculate_sha256_bytes(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_gp261_270_safe_stored_name_contract_blocks_bad_paths():
    contract = get_original_filename_safe_stored_name_contract()

    assert contract["ready"] is True
    assert contract["rules"]["preserve_original_filename_in_metadata"] is True
    assert contract["rules"]["store_using_safe_generated_name"] is True
    assert contract["rules"]["remove_path_traversal"] is True

    cleaned = sanitize_original_filename("../bad/path/private-tax-record.xlsx")
    assert "/" not in cleaned
    assert "\\" not in cleaned
    assert infer_mime_type("file.pdf") == "application/pdf"


def test_gp261_270_mission_lane_folder_map_requires_lanes():
    lane_map = get_mission_lane_folder_map()

    assert lane_map["ready"] is True
    assert "trust" in lane_map["mission_lanes"]
    assert "atm" in lane_map["mission_lanes"]
    assert "property" in lane_map["mission_lanes"]
    assert lane_map["rules"]["every_file_requires_mission_lane"] is True
    assert lane_map["rules"]["unmapped_lane_blocks_storage_receipt"] is True


def test_gp261_270_upload_receipt_draft_lock_stays_locked():
    lock = get_upload_receipt_draft_lock()

    assert lock["ready"] is True
    assert lock["upload_allowed"] is False
    assert lock["receipt_finalization_allowed"] is False

    receipt = lock["receipt_draft_contract"]
    assert receipt["requires_original_filename"] is True
    assert receipt["requires_safe_stored_name"] is True
    assert receipt["requires_sha256_hash"] is True
    assert receipt["requires_mission_lane"] is True


def test_gp261_270_safety_blockers_block_every_dangerous_action():
    board = get_file_storage_safety_blocker_board()

    assert board["ready"] is True
    assert board["blocker_count"] >= len(BLOCKERS)
    assert board["all_dangerous_actions_blocked"] is True
    assert board["unsafe_action_count"] == 0

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "public_upload" in blocked_actions
    assert "file_download" in blocked_actions
    assert "file_share" in blocked_actions
    assert "file_delete" in blocked_actions
    assert "external_sync" in blocked_actions


def test_gp261_270_home_exposes_packs_and_preserved_locks():
    home = get_owner_owned_file_storage_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["owner_only_storage_foundation"] is True
    assert home["locks"]["external_provider_required"] is False
    assert home["locks"]["file_download_unlocked"] is False


def test_gp261_270_all_dangerous_locks_false():
    assert LOCKS["provider_storage_unlocked"] is False
    assert LOCKS["public_upload_unlocked"] is False
    assert LOCKS["beta_upload_unlocked"] is False
    assert LOCKS["file_preview_unlocked"] is False
    assert LOCKS["file_download_unlocked"] is False
    assert LOCKS["file_share_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
    assert LOCKS["external_sync_unlocked"] is False
    assert LOCKS["provider_api_call_allowed"] is False
    assert LOCKS["object_body_read_allowed"] is False


def test_gp261_270_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-owned-file-storage-foundation-layer",
        "/vault/owner-owned-file-storage-foundation-layer.json",
        "/vault/owner-owned-file-storage-shell.json",
        "/vault/vault-storage-root-contract.json",
        "/vault/physical-object-folder-registry.json",
        "/vault/file-object-metadata-registry.json",
        "/vault/file-hash-integrity-contract.json",
        "/vault/original-filename-safe-stored-name-contract.json",
        "/vault/mission-lane-folder-map.json",
        "/vault/upload-receipt-draft-lock.json",
        "/vault/file-storage-safety-blocker-board.json",
        "/vault/owner-owned-file-storage-readiness-checkpoint.json",
        "/vault/gp261-status.json",
        "/vault/gp270-status.json",
    ]

    for route in required_routes:
        assert route in app_text
