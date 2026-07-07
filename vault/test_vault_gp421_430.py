
from pathlib import Path

from vault.blackseed_capsule_index_repair_layer_service import (
    DOCTRINE,
    LOCKS,
    get_blackseed_capsule_index_repair_home,
    get_blackseed_capsule_index_repair_readiness_checkpoint,
    get_capsule_hash_continuity_board,
    get_capsule_index_integrity_scanner,
    get_capsule_repair_safety_blocker_board,
    get_capsule_to_pack_repair_map,
    get_missing_capsule_repair_plan_builder,
    get_opaque_metadata_rebuild_contract,
    get_repair_receipt_chain_draft_ledger,
    get_repaired_index_snapshot_preview_board,
    validate_blackseed_capsule_index_repair_layer,
)


def test_gp421_430_readiness_checkpoint_passes():
    result = validate_blackseed_capsule_index_repair_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Blackseed capsule index repair layer" in result["readiness_label"]


def test_gp421_430_doctrine_is_headless_repair_only():
    home = get_blackseed_capsule_index_repair_home()

    assert home["ready"] is True
    assert home["doctrine"]["tower"] == "face"
    assert home["doctrine"]["teller"] == "workflow"
    assert home["doctrine"]["vault"] == "sealed_memory"
    assert home["doctrine"]["repair_behavior"] == "headless_capsule_index_repair_only"
    assert home["doctrine"]["people_enter_vault_directly"] is False
    assert home["doctrine"]["vault_is_public_drive_app"] is False
    assert home["doctrine"]["repair_exposes_raw_bytes"] is False


def test_gp421_430_capsule_index_integrity_scanner_sees_all_sources_no_public_raw_provider():
    scanner = get_capsule_index_integrity_scanner()

    assert scanner["ready"] is True
    assert scanner["scan_count"] >= 2
    assert scanner["all_capsules_present"] is True
    assert scanner["all_pack_manifests_present"] is True
    assert scanner["all_receipt_chains_present"] is True
    assert scanner["all_merkle_manifests_present"] is True
    assert scanner["all_index_snapshots_present"] is True
    assert scanner["all_opaque_metadata_only"] is True
    assert scanner["no_raw_bytes_exposed"] is True
    assert scanner["no_public_browse_allowed"] is True
    assert scanner["provider_dependency_not_required"] is True

    for item in scanner["scans"]:
        assert item["scan_state"] == "capsule_index_integrity_ok"
        assert item["capsule_present"] == 1
        assert item["pack_manifest_present"] == 1
        assert item["receipt_chain_present"] == 1
        assert item["merkle_manifest_present"] == 1
        assert item["index_snapshot_present"] == 1
        assert item["opaque_metadata_only"] == 1
        assert item["raw_bytes_exposed"] == 0
        assert item["public_browse_allowed"] == 0
        assert item["provider_dependency_required"] == 0


def test_gp421_430_capsule_hash_continuity_requires_no_raw_bytes():
    board = get_capsule_hash_continuity_board()

    assert board["ready"] is True
    assert board["continuity_count"] >= 2
    assert board["all_hash_chains_complete"] is True
    assert board["no_raw_bytes_needed"] is True

    for item in board["continuity_rows"]:
        assert item["continuity_state"] == "capsule_hash_continuity_verified"
        assert item["hash_chain_complete"] == 1
        assert item["raw_bytes_needed"] == 0
        assert len(item["capsule_hash"]) == 64
        assert len(item["sealed_pack_hash"]) == 64
        assert len(item["chain_hash"]) == 64
        assert len(item["merkle_root"]) == 64
        assert len(item["snapshot_hash"]) == 64
        assert len(item["continuity_hash"]) == 64


def test_gp421_430_capsule_to_pack_repair_map_uses_sealed_sources_only():
    board = get_capsule_to_pack_repair_map()

    assert board["ready"] is True
    assert board["repair_map_count"] >= 2
    assert board["all_can_repair_from_pack"] is True
    assert board["all_can_repair_from_receipts"] is True
    assert board["all_can_repair_from_merkle"] is True
    assert board["none_can_expose_raw_bytes"] is True
    assert board["provider_not_required"] is True

    for item in board["repair_maps"]:
        assert "sealed_pack_manifest" in item["repair_path"]
        assert "append_only_receipt_chain" in item["repair_path"]
        assert "merkle_repair_manifest" in item["repair_path"]
        assert item["can_repair_from_pack"] == 1
        assert item["can_repair_from_receipts"] == 1
        assert item["can_repair_from_merkle"] == 1
        assert item["can_expose_raw_bytes"] == 0
        assert item["provider_required"] == 0


def test_gp421_430_missing_capsule_repair_plans_are_owner_review_no_raw_no_direct_user():
    builder = get_missing_capsule_repair_plan_builder()

    assert builder["ready"] is True
    assert builder["repair_plan_count"] >= 2
    assert builder["all_owner_review_required"] is True
    assert builder["no_raw_bytes_required"] is True
    assert builder["no_direct_user_action_allowed"] is True

    for item in builder["repair_plans"]:
        assert item["owner_review_required"] == 1
        assert item["raw_bytes_required"] == 0
        assert item["direct_user_action_allowed"] == 0
        assert item["rebuild_source"] == "sealed_pack_manifest_and_append_only_receipt_chain"


def test_gp421_430_opaque_metadata_rebuild_contract_exposes_no_raw_or_public_data():
    contract = get_opaque_metadata_rebuild_contract()

    assert contract["ready"] is True
    assert contract["contract_count"] >= 2
    assert contract["all_opaque_metadata_only"] is True
    assert contract["all_compact_metadata_only"] is True
    assert contract["no_raw_filename"] is True
    assert contract["no_raw_path"] is True
    assert contract["no_raw_file_bytes"] is True
    assert contract["no_public_index"] is True
    assert contract["no_external_browse"] is True
    assert contract["provider_not_required"] is True

    for item in contract["contracts"]:
        assert item["contract_state"] == "opaque_metadata_rebuild_contract_ready"
        assert item["opaque_metadata_only"] == 1
        assert item["compact_metadata_only"] == 1
        assert item["raw_filename_allowed"] == 0
        assert item["raw_path_allowed"] == 0
        assert item["raw_file_bytes_allowed"] == 0
        assert item["public_index_allowed"] == 0
        assert item["external_browse_allowed"] == 0
        assert item["provider_dependency_required"] == 0


def test_gp421_430_repair_receipt_chain_drafts_are_append_only_immutable_and_locked():
    ledger = get_repair_receipt_chain_draft_ledger()

    assert ledger["ready"] is True
    assert ledger["repair_receipt_draft_count"] >= 2
    assert ledger["all_receipts_draft_locked"] is True
    assert ledger["all_append_only"] is True
    assert ledger["all_immutable"] is True

    for item in ledger["repair_receipt_drafts"]:
        assert item["receipt_state"] == "repair_receipt_chain_draft_locked"
        assert item["finalized"] == 0
        assert item["finalization_allowed"] == 0
        assert item["append_only"] == 1
        assert item["mutable"] == 0
        assert len(item["repair_receipt_hash"]) == 64


def test_gp421_430_repaired_snapshot_previews_do_not_write_or_expose():
    board = get_repaired_index_snapshot_preview_board()

    assert board["ready"] is True
    assert board["snapshot_preview_count"] >= 2
    assert board["all_preview_only"] is True
    assert board["all_index_writes_locked"] is True
    assert board["no_public_index"] is True
    assert board["no_external_browse"] is True
    assert board["no_raw_bytes_exposed"] is True

    for item in board["snapshot_previews"]:
        assert item["repaired_snapshot_state"] == "repaired_index_snapshot_preview_ready_write_locked"
        assert item["preview_only"] == 1
        assert item["index_write_allowed"] == 0
        assert item["public_index_allowed"] == 0
        assert item["external_browse_allowed"] == 0
        assert item["raw_bytes_exposed"] == 0
        assert len(item["repaired_snapshot_hash"]) == 64


def test_gp421_430_capsule_repair_safety_blockers_keep_danger_actions_locked():
    board = get_capsule_repair_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "public_vault_dashboard" in blocked_actions
    assert "direct_vault_user_portal" in blocked_actions
    assert "standalone_external_vault_dashboard" in blocked_actions
    assert "external_collaborator_browsing" in blocked_actions
    assert "employee_vendor_customer_vault_browsing" in blocked_actions
    assert "public_links_or_raw_urls" in blocked_actions
    assert "raw_file_bytes_json" in blocked_actions
    assert "raw_path_exposure" in blocked_actions
    assert "provider_dependency" in blocked_actions
    assert "delete_restore_physical_move" in blocked_actions


def test_gp421_430_readiness_declares_next_vault_pack_rebuild_layer():
    checkpoint = get_blackseed_capsule_index_repair_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_headless_sealed_memory_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["headless_repair_only"] is True
    assert checkpoint["checks"]["repair_exposes_no_raw_bytes"] is True
    assert checkpoint["checks"]["scanner_all_sources_present"] is True
    assert checkpoint["checks"]["hash_chains_complete_no_raw_bytes"] is True
    assert checkpoint["checks"]["repair_map_uses_pack_receipts_merkle"] is True
    assert checkpoint["checks"]["repair_map_no_raw_or_provider"] is True
    assert checkpoint["checks"]["repair_plans_owner_review_no_raw_no_direct_user"] is True
    assert checkpoint["checks"]["rebuild_no_raw_public_external_provider"] is True
    assert checkpoint["checks"]["snapshot_previews_write_locked_no_public_raw"] is True
    assert "VAULT PACK REBUILD SERVICE" in checkpoint["next_recommended_layer"]


def test_gp421_430_global_locks_preserve_headless_no_drive_behavior():
    assert LOCKS["capsule_index_integrity_scanning_allowed"] is True
    assert LOCKS["capsule_hash_continuity_verification_allowed"] is True
    assert LOCKS["capsule_to_pack_repair_mapping_allowed"] is True
    assert LOCKS["missing_capsule_repair_planning_allowed"] is True
    assert LOCKS["opaque_metadata_rebuild_contract_allowed"] is True
    assert LOCKS["repair_receipt_chain_draft_allowed"] is True
    assert LOCKS["repaired_index_snapshot_preview_allowed"] is True

    assert LOCKS["public_vault_dashboard_allowed"] is False
    assert LOCKS["standalone_external_vault_dashboard_allowed"] is False
    assert LOCKS["direct_vault_user_portal_allowed"] is False
    assert LOCKS["employee_vault_browsing_allowed"] is False
    assert LOCKS["vendor_vault_browsing_allowed"] is False
    assert LOCKS["customer_vault_browsing_allowed"] is False
    assert LOCKS["external_collaborator_browsing_allowed"] is False
    assert LOCKS["public_download_unlocked"] is False
    assert LOCKS["public_url_created"] is False
    assert LOCKS["share_link_created"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False
    assert LOCKS["external_sync_unlocked"] is False


def test_gp421_430_routes_are_json_only_no_public_page_route():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/blackseed-capsule-index-repair-layer.json",
        "/vault/blackseed-capsule-index-repair-shell.json",
        "/vault/capsule-index-integrity-scanner.json",
        "/vault/capsule-hash-continuity-board.json",
        "/vault/capsule-to-pack-repair-map.json",
        "/vault/missing-capsule-repair-plan-builder.json",
        "/vault/opaque-metadata-rebuild-contract.json",
        "/vault/repair-receipt-chain-draft-ledger.json",
        "/vault/repaired-index-snapshot-preview-board.json",
        "/vault/capsule-repair-safety-blocker-board.json",
        "/vault/blackseed-capsule-index-repair-readiness-checkpoint.json",
        "/vault/gp421-status.json",
        "/vault/gp430-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert '@app.route("/vault/blackseed-capsule-index-repair-layer")' not in app_text
