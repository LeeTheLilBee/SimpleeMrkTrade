
from pathlib import Path

from vault.headless_sealed_memory_service_layer_service import (
    DOCTRINE,
    LOCKS,
    get_append_only_receipt_chain_service,
    get_blackseed_metadata_capsule_builder,
    get_headless_sealed_memory_service_home,
    get_headless_sealed_memory_service_readiness_checkpoint,
    get_internal_service_call_boundary_contract,
    get_merkle_repair_manifest_builder,
    get_rebuildable_index_snapshot_board,
    get_sealed_memory_node_registry,
    get_tower_teller_service_output_contract,
    get_vault_pack_manifest_index,
    validate_headless_sealed_memory_service_layer,
)


def test_gp411_420_readiness_checkpoint_passes():
    result = validate_headless_sealed_memory_service_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Headless sealed memory service layer" in result["readiness_label"]


def test_gp411_420_doctrine_is_locked():
    home = get_headless_sealed_memory_service_home()

    assert home["ready"] is True
    assert home["doctrine"]["tower"] == "face"
    assert home["doctrine"]["teller"] == "workflow"
    assert home["doctrine"]["vault"] == "sealed_memory"
    assert home["doctrine"]["people_enter_vault_directly"] is False
    assert home["doctrine"]["vault_is_public_drive_app"] is False
    assert home["doctrine"]["vault_is_standalone_external_dashboard"] is False
    assert home["doctrine"]["vault_service_behavior"] == "headless_authorized_internal_service_calls_only"


def test_gp411_420_internal_service_boundaries_keep_tower_teller_vault_split():
    contract = get_internal_service_call_boundary_contract()

    assert contract["ready"] is True
    assert contract["boundary_count"] == 3
    assert contract["tower_is_face"] is True
    assert contract["teller_is_workflow"] is True
    assert contract["vault_is_sealed_memory"] is True
    assert contract["all_direct_people_access_locked"] is True
    assert contract["all_public_dashboards_locked"] is True
    assert contract["all_raw_urls_locked"] is True


def test_gp411_420_sealed_memory_nodes_are_local_first_and_headless():
    registry = get_sealed_memory_node_registry()

    assert registry["ready"] is True
    assert registry["node_count"] >= 2
    assert registry["all_local_first"] is True
    assert registry["all_serverless_style"] is True
    assert registry["provider_dependency_not_required"] is True
    assert registry["no_public_browsing"] is True
    assert registry["no_raw_bytes_exposed"] is True

    for node in registry["memory_nodes"]:
        assert node["node_kind"] == "sealed_local_first_memory_node"
        assert node["sealed_state"] == "sealed_memory_node_registered"
        assert node["local_first"] == 1
        assert node["serverless_style"] == 1
        assert node["provider_dependency_required"] == 0
        assert node["public_browsing_allowed"] == 0
        assert node["raw_bytes_exposed"] == 0
        assert len(node["node_hash"]) == 64


def test_gp411_420_blackseed_capsules_are_opaque_metadata_only():
    builder = get_blackseed_metadata_capsule_builder()

    assert builder["ready"] is True
    assert builder["capsule_count"] >= 2
    assert builder["all_opaque_metadata_only"] is True
    assert builder["all_compact_metadata_only"] is True
    assert builder["no_raw_filenames_exposed"] is True
    assert builder["no_raw_paths_exposed"] is True
    assert builder["no_raw_file_bytes_exposed"] is True

    for capsule in builder["capsules"]:
        assert capsule["capsule_kind"] == "blackseed_opaque_metadata_capsule"
        assert capsule["opaque_metadata_only"] == 1
        assert capsule["compact_metadata_only"] == 1
        assert capsule["raw_filename_exposed"] == 0
        assert capsule["raw_path_exposed"] == 0
        assert capsule["raw_file_bytes_exposed"] == 0
        assert len(capsule["capsule_hash"]) == 64


def test_gp411_420_vault_pack_manifests_are_sealed_no_provider_or_urls():
    index = get_vault_pack_manifest_index()

    assert index["ready"] is True
    assert index["pack_manifest_count"] >= 2
    assert index["all_sealed_pack_manifests"] is True
    assert index["provider_storage_not_required"] is True
    assert index["no_raw_file_urls"] is True

    for manifest in index["pack_manifests"]:
        assert manifest["pack_state"] == "sealed_pack_manifest_indexed"
        assert manifest["pack_kind"] == "sealed_vault_pack_manifest"
        assert manifest["provider_storage_required"] == 0
        assert manifest["raw_file_url_allowed"] == 0
        assert len(manifest["sealed_pack_hash"]) == 64


def test_gp411_420_append_only_receipt_chain_is_immutable():
    chain = get_append_only_receipt_chain_service()

    assert chain["ready"] is True
    assert chain["receipt_chain_count"] >= 2
    assert chain["all_append_only"] is True
    assert chain["all_immutable"] is True

    for item in chain["receipt_chains"]:
        assert item["append_only"] == 1
        assert item["mutable"] == 0
        assert len(item["chain_hash"]) == 64


def test_gp411_420_merkle_repair_manifests_repair_indexes_not_raw_bytes():
    builder = get_merkle_repair_manifest_builder()

    assert builder["ready"] is True
    assert builder["merkle_manifest_count"] >= 2
    assert builder["all_can_rebuild_index"] is True
    assert builder["none_can_expose_raw_bytes"] is True

    for manifest in builder["merkle_manifests"]:
        assert manifest["repair_manifest_state"] == "merkle_repair_manifest_ready_for_index_repair"
        assert manifest["repair_can_rebuild_index"] == 1
        assert manifest["repair_can_expose_raw_bytes"] == 0
        assert len(manifest["merkle_root"]) == 64


def test_gp411_420_rebuildable_index_snapshots_are_not_public_or_browsable():
    board = get_rebuildable_index_snapshot_board()

    assert board["ready"] is True
    assert board["snapshot_count"] >= 2
    assert board["all_rebuild_from_pack_allowed"] is True
    assert board["all_rebuild_from_receipts_allowed"] is True
    assert board["no_public_index"] is True
    assert board["no_external_browse"] is True

    for snapshot in board["index_snapshots"]:
        assert snapshot["snapshot_state"] == "rebuildable_headless_index_snapshot_ready"
        assert snapshot["rebuild_from_pack_allowed"] == 1
        assert snapshot["rebuild_from_receipts_allowed"] == 1
        assert snapshot["public_index_allowed"] == 0
        assert snapshot["external_browse_allowed"] == 0
        assert len(snapshot["snapshot_hash"]) == 64


def test_gp411_420_tower_teller_outputs_are_controlled_proofs_only():
    contract = get_tower_teller_service_output_contract()

    assert contract["ready"] is True
    assert contract["output_contract_count"] >= 2
    assert contract["all_tower_face_required"] is True
    assert contract["all_teller_workflow_required"] is True
    assert contract["no_direct_vault_portal"] is True
    assert contract["no_public_dashboard"] is True
    assert contract["no_raw_file_bytes_json"] is True

    for item in contract["output_contracts"]:
        assert item["tower_face_required"] == 1
        assert item["teller_workflow_required"] == 1
        assert item["direct_vault_portal_allowed"] == 0
        assert item["public_dashboard_allowed"] == 0
        assert item["raw_file_bytes_json_allowed"] == 0
        assert "status_card" in item["allowed_outputs"]
        assert "receipt_hash" in item["allowed_outputs"]
        assert "raw_file_bytes" in item["blocked_outputs"]
        assert "public_link" in item["blocked_outputs"]


def test_gp411_420_readiness_declares_next_capsule_index_repair_layer():
    checkpoint = get_headless_sealed_memory_service_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_controlled_soft_delete_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["direct_people_access_locked"] is True
    assert checkpoint["checks"]["vault_not_public_drive"] is True
    assert checkpoint["checks"]["nodes_local_first_serverless"] is True
    assert checkpoint["checks"]["nodes_provider_not_required"] is True
    assert checkpoint["checks"]["capsules_opaque_compact"] is True
    assert checkpoint["checks"]["packs_sealed_no_provider_or_urls"] is True
    assert checkpoint["checks"]["receipt_chain_append_only_immutable"] is True
    assert checkpoint["checks"]["merkle_can_repair_index_not_raw_bytes"] is True
    assert checkpoint["checks"]["index_rebuildable_not_public"] is True
    assert checkpoint["checks"]["outputs_tower_teller_required"] is True
    assert checkpoint["checks"]["outputs_no_direct_portal_dashboard_raw_bytes"] is True
    assert "BLACKSEED CAPSULE INDEX REPAIR" in checkpoint["next_recommended_layer"]


def test_gp411_420_global_locks_preserve_headless_no_drive_behavior():
    assert LOCKS["headless_internal_service_metadata_allowed"] is True
    assert LOCKS["sealed_memory_nodes_allowed"] is True
    assert LOCKS["blackseed_metadata_capsules_allowed"] is True
    assert LOCKS["vault_pack_manifest_index_allowed"] is True
    assert LOCKS["append_only_receipt_chain_allowed"] is True
    assert LOCKS["merkle_repair_manifest_allowed"] is True
    assert LOCKS["rebuildable_index_snapshot_allowed"] is True
    assert LOCKS["tower_teller_service_output_allowed"] is True

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
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["raw_share_token_exposed"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False
    assert LOCKS["external_sync_unlocked"] is False


def test_gp411_420_routes_are_registered_but_no_public_page_route():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/headless-sealed-memory-service-layer.json",
        "/vault/headless-sealed-memory-service-shell.json",
        "/vault/internal-service-call-boundary-contract.json",
        "/vault/sealed-memory-node-registry.json",
        "/vault/blackseed-metadata-capsule-builder.json",
        "/vault/vault-pack-manifest-index.json",
        "/vault/append-only-receipt-chain-service.json",
        "/vault/merkle-repair-manifest-builder.json",
        "/vault/rebuildable-index-snapshot-board.json",
        "/vault/tower-teller-service-output-contract.json",
        "/vault/headless-sealed-memory-service-readiness-checkpoint.json",
        "/vault/gp411-status.json",
        "/vault/gp420-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert '@app.route("/vault/headless-sealed-memory-service-layer")' not in app_text
    assert '@app.route("/vault")' not in app_text
