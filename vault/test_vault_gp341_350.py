
from pathlib import Path

from vault.controlled_owner_safe_preview_execution_layer_service import (
    LOCKS,
    get_controlled_owner_safe_preview_execution_home,
    get_controlled_owner_safe_preview_execution_readiness_checkpoint,
    get_controlled_preview_body_reader,
    get_preview_access_ledger,
    get_preview_cache_index,
    get_preview_execution_safety_blocker_board,
    get_preview_execution_scope_contract,
    get_preview_receipt_finalization_board,
    get_preview_redaction_result_board,
    get_safe_preview_artifact_builder,
    validate_controlled_owner_safe_preview_execution_layer,
)


def test_gp341_350_readiness_checkpoint_passes():
    result = validate_controlled_owner_safe_preview_execution_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Controlled owner safe preview execution layer" in result["readiness_label"]


def test_gp341_350_scope_contract_is_owner_only_and_no_download():
    contract = get_preview_execution_scope_contract()

    assert contract["ready"] is True
    assert contract["scope"]["owner_only"] is True
    assert contract["scope"]["safe_text_like_mime_body_read_allowed"] is True
    assert "text/csv" in contract["scope"]["allowed_body_read_mime_types"]
    assert contract["scope"]["download_allowed"] is False
    assert contract["scope"]["share_allowed"] is False
    assert contract["scope"]["public_access_allowed"] is False
    assert contract["scope"]["beta_access_allowed"] is False


def test_gp341_350_body_reader_executes_at_least_one_safe_text_read():
    reader = get_controlled_preview_body_reader()

    assert reader["ready"] is True
    assert reader["read_count"] >= 2
    assert reader["executed_read_count"] >= 1
    assert reader["all_reads_owner_only"] is True
    assert reader["no_download_allowed"] is True

    for item in reader["body_reads"]:
        assert item["owner_only"] == 1
        if item["body_read_executed"] == 1:
            assert item["mime_type"] in {"text/csv", "text/plain", "application/json"}
            assert item["bytes_read"] > 0


def test_gp341_350_safe_preview_artifacts_created_owner_only_no_download_url():
    builder = get_safe_preview_artifact_builder()

    assert builder["ready"] is True
    assert builder["artifact_count"] >= 2
    assert builder["rendered_text_preview_count"] >= 1
    assert builder["all_artifacts_owner_only"] is True
    assert builder["all_download_urls_excluded"] is True

    for item in builder["artifacts"]:
        assert item["owner_only"] == 1
        assert item["download_url_included"] == 0
        assert len(item["preview_hash"]) == 64
        assert item["preview_text"]


def test_gp341_350_preview_cache_index_is_metadata_indexed():
    cache = get_preview_cache_index()

    assert cache["ready"] is True
    assert cache["cache_entry_count"] >= 2
    assert cache["metadata_only_index"] is True
    assert cache["all_cache_entries_indexed"] is True

    for item in cache["cache_entries"]:
        assert item["metadata_only_index"] == 1
        assert item["cache_read_allowed"] == 1
        assert item["cache_write_executed"] == 1
        assert len(item["preview_hash"]) == 64


def test_gp341_350_preview_access_ledger_is_owner_only():
    ledger = get_preview_access_ledger()

    assert ledger["ready"] is True
    assert ledger["access_count"] >= 2
    assert ledger["all_owner_only"] is True
    assert ledger["no_public_access"] is True
    assert ledger["no_beta_access"] is True
    assert ledger["no_download_access"] is True
    assert ledger["no_share_access"] is True

    for item in ledger["access_rows"]:
        assert item["owner_only"] == 1
        assert item["public_access_allowed"] == 0
        assert item["beta_access_allowed"] == 0
        assert item["download_allowed"] == 0
        assert item["share_allowed"] == 0


def test_gp341_350_preview_receipts_are_finalized():
    board = get_preview_receipt_finalization_board()

    assert board["ready"] is True
    assert board["final_receipt_count"] >= 2
    assert board["all_receipts_finalized"] is True

    for item in board["final_receipts"]:
        assert item["finalized"] == 1
        assert len(item["final_receipt_hash"]) == 64
        assert item["receipt_scope"] == "controlled_owner_safe_preview_execution"


def test_gp341_350_redaction_results_exclude_body_path_and_download_url():
    board = get_preview_redaction_result_board()

    assert board["ready"] is True
    assert board["redaction_result_count"] >= 2
    assert board["all_object_bodies_excluded"] is True
    assert board["all_plaintext_limited"] is True
    assert board["all_physical_paths_excluded"] is True
    assert board["all_download_urls_excluded"] is True


def test_gp341_350_safety_blockers_keep_danger_actions_locked():
    board = get_preview_execution_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "public_preview" in blocked_actions
    assert "beta_preview" in blocked_actions
    assert "preview_download" in blocked_actions
    assert "file_download" in blocked_actions
    assert "file_share" in blocked_actions
    assert "file_delete" in blocked_actions
    assert "file_restore" in blocked_actions
    assert "quarantine_release" in blocked_actions
    assert "external_sync" in blocked_actions


def test_gp341_350_home_exposes_packs_and_locks():
    home = get_controlled_owner_safe_preview_execution_home()

    assert home["ready"] is True
    assert len(home["packs"]) == 10
    assert home["locks"]["controlled_owner_preview_execution_allowed"] is True
    assert home["locks"]["owner_only_preview_allowed"] is True
    assert home["locks"]["file_download_unlocked"] is False
    assert home["locks"]["file_share_unlocked"] is False


def test_gp341_350_readiness_declares_next_layer():
    checkpoint = get_controlled_owner_safe_preview_execution_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_safe_preview_lock_prep_ready"] is True
    assert checkpoint["checks"]["at_least_one_safe_text_preview_body_read"] is True
    assert checkpoint["checks"]["at_least_one_text_preview_rendered"] is True
    assert checkpoint["checks"]["no_public_or_beta_access"] is True
    assert checkpoint["checks"]["no_download_or_share_access"] is True
    assert "OWNER DOWNLOAD LOCK PREP" in checkpoint["next_recommended_layer"]


def test_gp341_350_allowed_features_are_preview_execution_only():
    assert LOCKS["controlled_owner_preview_execution_allowed"] is True
    assert LOCKS["scoped_object_body_read_allowed"] is True
    assert LOCKS["safe_preview_artifact_write_allowed"] is True
    assert LOCKS["owner_only_preview_allowed"] is True

    assert LOCKS["general_object_body_read_allowed"] is False
    assert LOCKS["public_preview_unlocked"] is False
    assert LOCKS["beta_preview_unlocked"] is False
    assert LOCKS["preview_download_allowed"] is False
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


def test_gp341_350_routes_are_registered_in_web_app_text():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/controlled-owner-safe-preview-execution-layer",
        "/vault/controlled-owner-safe-preview-execution-layer.json",
        "/vault/controlled-owner-safe-preview-execution-shell.json",
        "/vault/preview-execution-scope-contract.json",
        "/vault/controlled-preview-body-reader.json",
        "/vault/safe-preview-artifact-builder.json",
        "/vault/preview-cache-index.json",
        "/vault/preview-access-ledger.json",
        "/vault/preview-receipt-finalization-board.json",
        "/vault/preview-redaction-result-board.json",
        "/vault/preview-execution-safety-blocker-board.json",
        "/vault/controlled-owner-safe-preview-execution-readiness-checkpoint.json",
        "/vault/gp341-status.json",
        "/vault/gp350-status.json",
    ]

    for route in required_routes:
        assert route in app_text
