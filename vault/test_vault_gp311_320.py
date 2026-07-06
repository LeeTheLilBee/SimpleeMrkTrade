
from pathlib import Path

from vault.owner_file_detail_metadata_view_layer_service import (
    LOCKS,
    get_active_file_metadata_detail_contract,
    get_file_detail_audit_snapshot_ledger,
    get_file_detail_route_payload_builder,
    get_file_detail_safety_blocker_board,
    get_file_identity_summary_board,
    get_file_lock_status_board,
    get_file_provenance_receipt_reference_board,
    get_metadata_redaction_display_policy_board,
    get_owner_file_detail_metadata_view_home,
    get_owner_file_detail_metadata_view_readiness_checkpoint,
    validate_owner_file_detail_metadata_view_layer,
)


def test_gp311_320_readiness_checkpoint_passes():
    result = validate_owner_file_detail_metadata_view_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Owner file detail metadata view layer" in result["readiness_label"]


def test_gp311_320_metadata_detail_contract_blocks_body_and_download_fields():
    contract = get_active_file_metadata_detail_contract()

    assert contract["ready"] is True
    assert contract["contract"]["metadata_only"] is True
    assert "object_body" in contract["contract"]["blocked_fields"]
    assert "plaintext_content" in contract["contract"]["blocked_fields"]
    assert "download_url" in contract["contract"]["blocked_fields"]
    assert contract["contract"]["object_body_read_allowed"] is False
    assert contract["contract"]["preview_allowed"] is False
    assert contract["contract"]["download_allowed"] is False


def test_gp311_320_file_identity_summary_is_metadata_only():
    board = get_file_identity_summary_board()

    assert board["ready"] is True
    assert board["file_count"] >= 2
    assert board["metadata_only"] is True

    for item in board["files"]:
        assert len(item["sha256_hash"]) == 64
        assert item["original_filename"]
        assert item["safe_stored_name"]
        assert item["mission_lane"]
        assert item["folder_key"]


def test_gp311_320_provenance_and_receipt_references_are_ready():
    board = get_file_provenance_receipt_reference_board()

    assert board["ready"] is True
    assert board["snapshot_count"] >= 2
    assert board["execution_reference_count"] >= 2
    assert board["receipt_reference_count"] >= 2
    assert board["hash_continuity_reference_count"] >= 2
    assert board["quarantine_hold_reference_count"] >= 2
    assert board["provenance_ready"] is True

    for item in board["snapshots"]:
        assert len(item["detail_payload_hash"]) == 64


def test_gp311_320_file_lock_status_board_keeps_all_actions_locked():
    board = get_file_lock_status_board()

    assert board["ready"] is True
    assert board["file_count"] >= 2
    assert board["all_object_body_reads_locked"] is True
    assert board["all_previews_locked"] is True
    assert board["all_downloads_locked"] is True
    assert board["all_shares_locked"] is True
    assert board["all_deletes_locked"] is True
    assert board["all_restores_locked"] is True

    for item in board["lock_rows"]:
        assert item["object_body_read_locked"] == 1
        assert item["preview_locked"] == 1
        assert item["download_locked"] == 1
        assert item["share_locked"] == 1
        assert item["delete_locked"] == 1
        assert item["restore_locked"] == 1


def test_gp311_320_metadata_redaction_display_policy_blocks_sensitive_fields():
    board = get_metadata_redaction_display_policy_board()

    assert board["ready"] is True
    assert board["policy_count"] >= 7
    assert board["object_body_blocked"] is True
    assert board["plaintext_content_blocked"] is True
    assert board["physical_path_hidden"] is True


def test_gp311_320_file_detail_route_payload_builder_excludes_body_and_download_url():
    builder = get_file_detail_route_payload_builder()

    assert builder["ready"] is True
    assert builder["payload_count"] >= 2
    assert builder["metadata_only"] is True
    assert builder["object_body_included"] is False
    assert builder["download_url_included"] is False

    for payload in builder["payloads"]:
        assert payload["display"]["metadata_only"] is True
        assert payload["display"]["object_body"] == "LOCKED"
        assert payload["display"]["plaintext_content"] == "LOCKED"
        assert payload["display"]["preview"] == "LOCKED"
        assert payload["display"]["download"] == "LOCKED"
        assert payload["locks"]["object_body_read_locked"] is True
        assert payload["locks"]["preview_locked"] is True
        assert payload["locks"]["download_locked"] is True


def test_gp311_320_file_detail_audit_snapshot_has_no_body_preview_or_download():
    ledger = get_file_detail_audit_snapshot_ledger()

    assert ledger["ready"] is True
    assert ledger["audit_snapshot_count"] >= 2
    assert ledger["no_object_body_reads_executed"] is True
    assert ledger["no_previews_executed"] is True
    assert ledger["no_downloads_executed"] is True

    for item in ledger["audit_snapshots"]:
        assert item["object_body_read_executed"] == 0
        assert item["preview_executed"] == 0
        assert item["download_executed"] == 0
        assert len(item["detail_payload_hash"]) == 64


def test_gp311_320_safety_blockers_keep_danger_actions_locked():
    board = get_file_detail_safety_blocker_board()

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


def test_gp311_320_home_exposes_packs_and_locks():
    home = get_owner_file_detail_metadata_view_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["metadata_detail_view_allowed"] is True
    assert home["locks"]["identity_summary_allowed"] is True
    assert home["locks"]["object_body_read_allowed"] is False
    assert home["locks"]["file_preview_unlocked"] is False
    assert home["locks"]["file_download_unlocked"] is False


def test_gp311_320_readiness_checkpoint_declares_next_layer():
    checkpoint = get_owner_file_detail_metadata_view_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_registry_promotion_execution_ready"] is True
    assert checkpoint["checks"]["metadata_detail_contract_ready"] is True
    assert checkpoint["checks"]["identity_summary_ready"] is True
    assert checkpoint["checks"]["provenance_reference_ready"] is True
    assert checkpoint["checks"]["lock_status_ready"] is True
    assert checkpoint["checks"]["object_body_read_still_locked"] is True
    assert checkpoint["checks"]["download_still_locked"] is True
    assert "OWNER FOLDER BROWSE METADATA" in checkpoint["next_recommended_layer"]


def test_gp311_320_allowed_features_are_metadata_only():
    assert LOCKS["metadata_detail_view_allowed"] is True
    assert LOCKS["identity_summary_allowed"] is True
    assert LOCKS["provenance_reference_allowed"] is True
    assert LOCKS["receipt_reference_allowed"] is True
    assert LOCKS["lock_status_display_allowed"] is True
    assert LOCKS["metadata_redaction_policy_allowed"] is True
    assert LOCKS["file_detail_payload_allowed"] is True
    assert LOCKS["audit_snapshot_allowed"] is True

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


def test_gp311_320_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/owner-file-detail-metadata-view-layer",
        "/vault/owner-file-detail-metadata-view-layer.json",
        "/vault/owner-file-detail-metadata-view-shell.json",
        "/vault/active-file-metadata-detail-contract.json",
        "/vault/file-identity-summary-board.json",
        "/vault/file-provenance-receipt-reference-board.json",
        "/vault/file-lock-status-board.json",
        "/vault/metadata-redaction-display-policy-board.json",
        "/vault/file-detail-route-payload-builder.json",
        "/vault/file-detail-audit-snapshot-ledger.json",
        "/vault/file-detail-safety-blocker-board.json",
        "/vault/owner-file-detail-metadata-view-readiness-checkpoint.json",
        "/vault/gp311-status.json",
        "/vault/gp320-status.json",
    ]

    for route in required_routes:
        assert route in app_text
