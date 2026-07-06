
from pathlib import Path

from vault.owner_folder_browse_metadata_layer_service import (
    FOLDER_MAP,
    LOCKS,
    get_empty_folder_placeholder_board,
    get_folder_breadcrumb_metadata_contract,
    get_folder_browse_audit_snapshot_ledger,
    get_folder_browse_index_builder,
    get_folder_browse_safety_blocker_board,
    get_folder_browse_sort_filter_contract,
    get_folder_file_row_payload_builder,
    get_mission_lane_folder_group_board,
    get_owner_folder_browse_metadata_home,
    get_owner_folder_browse_metadata_readiness_checkpoint,
    validate_owner_folder_browse_metadata_layer,
)


def test_gp321_330_readiness_checkpoint_passes():
    result = validate_owner_folder_browse_metadata_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Owner folder browse metadata layer" in result["readiness_label"]


def test_gp321_330_folder_browse_index_has_folder_cards_metadata_only():
    index = get_folder_browse_index_builder()

    assert index["ready"] is True
    assert index["folder_count"] >= len(FOLDER_MAP)
    assert index["metadata_only"] is True
    assert index["object_body_read_allowed"] is False
    assert index["download_allowed"] is False

    for folder in index["folders"]:
        assert folder["metadata_only"] == 1
        assert folder["object_body_read_locked"] == 1
        assert folder["preview_locked"] == 1
        assert folder["download_locked"] == 1
        assert folder["share_locked"] == 1
        assert folder["delete_locked"] == 1
        assert folder["restore_locked"] == 1


def test_gp321_330_mission_lane_folder_groups_are_built():
    board = get_mission_lane_folder_group_board()

    assert board["ready"] is True
    assert board["mission_lane_count"] >= 1
    assert "trust" in board["known_mission_lanes"]
    assert "atm" in board["known_mission_lanes"]

    total_files = sum(item["file_count"] for item in board["mission_lanes"])
    assert total_files >= 2


def test_gp321_330_breadcrumb_contract_is_metadata_only():
    board = get_folder_breadcrumb_metadata_contract()

    assert board["ready"] is True
    assert board["breadcrumb_count"] >= len(FOLDER_MAP)
    assert board["object_body_read_allowed"] is False
    assert board["breadcrumb_rules"]["metadata_only"] is True
    assert board["breadcrumb_rules"]["mission_lane_required"] is True

    for item in board["breadcrumbs"]:
        assert item["breadcrumb_parts"][0] == "Vault"
        assert item["breadcrumb_parts"][1] == "Owner Files"
        assert item["object_body_read_allowed"] == 0


def test_gp321_330_folder_file_rows_are_metadata_only_and_locked():
    rows = get_folder_file_row_payload_builder()

    assert rows["ready"] is True
    assert rows["row_count"] >= 2
    assert rows["metadata_only"] is True
    assert rows["object_body_included"] is False
    assert rows["download_url_included"] is False

    for row in rows["rows"]:
        assert row["metadata_only"] is True
        assert row["identity"]["original_filename"]
        assert len(row["identity"]["sha256_hash"]) == 64
        assert row["locks"]["object_body_read_locked"] is True
        assert row["locks"]["preview_locked"] is True
        assert row["locks"]["download_locked"] is True
        assert row["locks"]["share_locked"] is True
        assert row["locks"]["delete_locked"] is True
        assert row["locks"]["restore_locked"] is True


def test_gp321_330_empty_folder_placeholders_exist_and_upload_locked():
    board = get_empty_folder_placeholder_board()

    assert board["ready"] is True
    assert board["placeholder_count"] >= 1
    assert board["upload_allowed"] is False
    assert board["all_placeholders_upload_locked"] is True

    for item in board["placeholders"]:
        assert item["file_count"] == 0
        assert item["placeholder_visible"] == 1
        assert item["upload_allowed"] == 0


def test_gp321_330_sort_filter_contract_is_metadata_only():
    contract = get_folder_browse_sort_filter_contract()

    assert contract["ready"] is True
    assert contract["metadata_only"] is True
    assert contract["body_search_allowed"] is False
    assert contract["plaintext_search_allowed"] is False
    assert contract["download_required"] is False
    assert "original_filename" in contract["sort_filter_options"]["sort_fields"]
    assert "folder_key" in contract["sort_filter_options"]["filter_fields"]
    assert "sha256_hash" in contract["sort_filter_options"]["search_fields"]


def test_gp321_330_audit_snapshot_ledger_did_no_body_preview_download():
    ledger = get_folder_browse_audit_snapshot_ledger()

    assert ledger["ready"] is True
    assert ledger["audit_snapshot_count"] >= len(FOLDER_MAP)
    assert ledger["no_object_body_reads_executed"] is True
    assert ledger["no_previews_executed"] is True
    assert ledger["no_downloads_executed"] is True

    for item in ledger["audit_snapshots"]:
        assert item["metadata_only"] == 1
        assert item["object_body_read_executed"] == 0
        assert item["preview_executed"] == 0
        assert item["download_executed"] == 0
        assert len(item["snapshot_hash"]) == 64


def test_gp321_330_safety_blockers_keep_danger_actions_locked():
    board = get_folder_browse_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "object_body_read" in blocked_actions
    assert "plaintext_content" in blocked_actions
    assert "file_preview" in blocked_actions
    assert "file_download" in blocked_actions
    assert "file_share" in blocked_actions
    assert "file_delete" in blocked_actions
    assert "file_restore" in blocked_actions
    assert "quarantine_release" in blocked_actions
    assert "external_sync" in blocked_actions


def test_gp321_330_home_exposes_packs_and_locks():
    home = get_owner_folder_browse_metadata_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["folder_browse_metadata_allowed"] is True
    assert home["locks"]["mission_lane_grouping_allowed"] is True
    assert home["locks"]["object_body_read_allowed"] is False
    assert home["locks"]["file_preview_unlocked"] is False
    assert home["locks"]["file_download_unlocked"] is False


def test_gp321_330_readiness_checkpoint_declares_next_layer():
    checkpoint = get_owner_folder_browse_metadata_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_file_detail_metadata_view_ready"] is True
    assert checkpoint["checks"]["folder_index_ready"] is True
    assert checkpoint["checks"]["mission_lane_groups_ready"] is True
    assert checkpoint["checks"]["breadcrumb_metadata_ready"] is True
    assert checkpoint["checks"]["folder_file_rows_ready"] is True
    assert checkpoint["checks"]["object_body_read_still_locked"] is True
    assert checkpoint["checks"]["download_still_locked"] is True
    assert "OWNER SAFE PREVIEW LOCK PREP" in checkpoint["next_recommended_layer"]


def test_gp321_330_allowed_features_are_metadata_only():
    assert LOCKS["folder_browse_metadata_allowed"] is True
    assert LOCKS["mission_lane_grouping_allowed"] is True
    assert LOCKS["folder_card_payload_allowed"] is True
    assert LOCKS["breadcrumb_metadata_allowed"] is True
    assert LOCKS["folder_file_rows_allowed"] is True
    assert LOCKS["sort_filter_metadata_allowed"] is True
    assert LOCKS["folder_browse_audit_allowed"] is True

    assert LOCKS["object_body_read_allowed"] is False
    assert LOCKS["plaintext_content_allowed"] is False
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


def test_gp321_330_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-folder-browse-metadata-layer",
        "/vault/owner-folder-browse-metadata-layer.json",
        "/vault/owner-folder-browse-metadata-shell.json",
        "/vault/folder-browse-index-builder.json",
        "/vault/mission-lane-folder-group-board.json",
        "/vault/folder-breadcrumb-metadata-contract.json",
        "/vault/folder-file-row-payload-builder.json",
        "/vault/empty-folder-placeholder-board.json",
        "/vault/folder-browse-sort-filter-contract.json",
        "/vault/folder-browse-audit-snapshot-ledger.json",
        "/vault/folder-browse-safety-blocker-board.json",
        "/vault/owner-folder-browse-metadata-readiness-checkpoint.json",
        "/vault/gp321-status.json",
        "/vault/gp330-status.json",
    ]

    for route in required_routes:
        assert route in app_text
