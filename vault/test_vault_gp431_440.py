
from pathlib import Path

from vault.vault_pack_rebuild_service_layer_service import (
    DOCTRINE,
    LOCKS,
    get_merkle_root_rebuild_verifier,
    get_pack_chunk_reconstruction_plan_builder,
    get_rebuild_source_contract,
    get_rebuilt_pack_index_preview_board,
    get_receipt_chain_rebuild_guard,
    get_sealed_pack_rebuild_candidate_board,
    get_tower_teller_rebuild_output_contract,
    get_vault_pack_rebuild_safety_blocker_board,
    get_vault_pack_rebuild_service_home,
    get_vault_pack_rebuild_service_readiness_checkpoint,
    validate_vault_pack_rebuild_service_layer,
)


def test_gp431_440_readiness_checkpoint_passes():
    result = validate_vault_pack_rebuild_service_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Vault Pack rebuild service layer" in result["readiness_label"]


def test_gp431_440_doctrine_is_headless_rebuild_only():
    home = get_vault_pack_rebuild_service_home()

    assert home["ready"] is True
    assert home["doctrine"]["tower"] == "face"
    assert home["doctrine"]["teller"] == "workflow"
    assert home["doctrine"]["vault"] == "sealed_memory"
    assert home["doctrine"]["service_behavior"] == "headless_vault_pack_rebuild_service_only"
    assert home["doctrine"]["people_enter_vault_directly"] is False
    assert home["doctrine"]["vault_is_public_drive_app"] is False
    assert home["doctrine"]["rebuild_exposes_raw_bytes"] is False
    assert home["doctrine"]["final_index_write_allowed"] is False


def test_gp431_440_rebuild_source_contract_uses_local_headless_sources_only():
    contract = get_rebuild_source_contract()

    assert contract["ready"] is True
    assert contract["contract_count"] >= 1
    assert contract["all_local_first"] is True
    assert contract["all_serverless_style"] is True
    assert contract["provider_dependency_not_required"] is True
    assert contract["no_raw_bytes_required"] is True
    assert contract["no_public_index"] is True
    assert contract["no_direct_user_action"] is True

    for item in contract["contracts"]:
        assert item["source_scope"] == "headless_sealed_pack_rebuild_sources"
        assert "blackseed_capsule_repair_map" in item["allowed_sources"]
        assert "append_only_repair_receipt_chain" in item["allowed_sources"]
        assert "raw_file_bytes" in item["blocked_sources"]
        assert "public_link" in item["blocked_sources"]
        assert item["provider_dependency_required"] == 0
        assert item["raw_bytes_required"] == 0
        assert item["direct_user_action_allowed"] == 0


def test_gp431_440_rebuild_candidates_use_pack_receipts_merkle_no_raw_or_final_write():
    board = get_sealed_pack_rebuild_candidate_board()

    assert board["ready"] is True
    assert board["candidate_count"] >= 2
    assert board["all_can_rebuild_from_pack"] is True
    assert board["all_can_rebuild_from_receipts"] is True
    assert board["all_can_rebuild_from_merkle"] is True
    assert board["no_raw_bytes_required"] is True
    assert board["no_raw_paths_required"] is True
    assert board["provider_not_required"] is True
    assert board["all_final_index_writes_locked"] is True
    assert board["all_final_pack_overwrites_locked"] is True

    for item in board["candidates"]:
        assert item["candidate_state"] == "sealed_pack_rebuild_candidate_ready_preview_only"
        assert item["can_rebuild_from_pack"] == 1
        assert item["can_rebuild_from_receipts"] == 1
        assert item["can_rebuild_from_merkle"] == 1
        assert item["raw_bytes_required"] == 0
        assert item["raw_path_required"] == 0
        assert item["provider_required"] == 0
        assert item["final_index_write_allowed"] == 0
        assert item["final_pack_overwrite_allowed"] == 0
        assert len(item["candidate_hash"]) == 64


def test_gp431_440_chunk_reconstruction_plans_are_opaque_no_raw_move():
    builder = get_pack_chunk_reconstruction_plan_builder()

    assert builder["ready"] is True
    assert builder["chunk_plan_count"] >= 2
    assert builder["all_opaque_metadata_only"] is True
    assert builder["no_raw_filename"] is True
    assert builder["no_raw_path"] is True
    assert builder["no_raw_file_bytes"] is True
    assert builder["no_physical_object_move"] is True

    for item in builder["chunk_plans"]:
        assert item["plan_state"] == "pack_chunk_reconstruction_plan_ready_write_locked"
        assert item["chunk_strategy"] == "sealed_manifest_hash_reconstruction_plan"
        assert item["sealed_chunk_count"] == 3
        assert item["opaque_metadata_only"] == 1
        assert item["raw_filename_allowed"] == 0
        assert item["raw_path_allowed"] == 0
        assert item["raw_file_bytes_allowed"] == 0
        assert item["physical_object_move_allowed"] == 0
        assert len(item["plan_hash"]) == 64


def test_gp431_440_receipt_chain_guards_are_append_only_and_no_rewrite():
    guard = get_receipt_chain_rebuild_guard()

    assert guard["ready"] is True
    assert guard["receipt_guard_count"] >= 2
    assert guard["all_append_only"] is True
    assert guard["all_immutable"] is True
    assert guard["all_finalization_locked"] is True
    assert guard["all_chain_rewrite_locked"] is True

    for item in guard["receipt_guards"]:
        assert item["guard_state"] == "receipt_chain_rebuild_guard_ready_append_only"
        assert item["append_only"] == 1
        assert item["mutable"] == 0
        assert item["finalization_allowed"] == 0
        assert item["chain_rewrite_allowed"] == 0
        assert len(item["guard_hash"]) == 64


def test_gp431_440_merkle_rebuild_verifier_needs_no_raw_or_provider():
    verifier = get_merkle_root_rebuild_verifier()

    assert verifier["ready"] is True
    assert verifier["merkle_verifier_count"] >= 2
    assert verifier["all_merkle_rebuild_verified"] is True
    assert verifier["no_raw_bytes_needed"] is True
    assert verifier["provider_not_needed"] is True

    for item in verifier["merkle_verifiers"]:
        assert item["verifier_state"] == "merkle_rebuild_verified_for_preview"
        assert item["merkle_rebuild_verified"] == 1
        assert item["raw_bytes_needed"] == 0
        assert item["provider_needed"] == 0
        assert len(item["verifier_hash"]) == 64


def test_gp431_440_rebuilt_pack_index_previews_are_preview_only_no_write_public_raw():
    board = get_rebuilt_pack_index_preview_board()

    assert board["ready"] is True
    assert board["preview_count"] >= 2
    assert board["all_preview_only"] is True
    assert board["all_final_index_writes_locked"] is True
    assert board["all_final_pack_overwrites_locked"] is True
    assert board["no_public_index"] is True
    assert board["no_external_browse"] is True
    assert board["no_raw_bytes_exposed"] is True

    for item in board["previews"]:
        assert item["preview_state"] == "rebuilt_pack_index_preview_ready_write_locked"
        assert item["preview_only"] == 1
        assert item["final_index_write_allowed"] == 0
        assert item["final_pack_overwrite_allowed"] == 0
        assert item["public_index_allowed"] == 0
        assert item["external_browse_allowed"] == 0
        assert item["raw_bytes_exposed"] == 0
        assert len(item["rebuilt_index_preview_hash"]) == 64


def test_gp431_440_tower_teller_outputs_no_portal_dashboard_raw_or_write():
    contract = get_tower_teller_rebuild_output_contract()

    assert contract["ready"] is True
    assert contract["output_contract_count"] >= 2
    assert contract["all_tower_face_required"] is True
    assert contract["all_teller_workflow_required"] is True
    assert contract["no_direct_vault_portal"] is True
    assert contract["no_public_dashboard"] is True
    assert contract["no_raw_file_bytes_json"] is True
    assert contract["all_final_index_writes_locked"] is True

    for item in contract["output_contracts"]:
        assert item["tower_face_required"] == 1
        assert item["teller_workflow_required"] == 1
        assert item["direct_vault_portal_allowed"] == 0
        assert item["public_dashboard_allowed"] == 0
        assert item["raw_file_bytes_json_allowed"] == 0
        assert item["final_index_write_allowed"] == 0
        assert "rebuild_status_card" in item["allowed_outputs"]
        assert "merkle_verification_result" in item["allowed_outputs"]
        assert "raw_file_bytes" in item["blocked_outputs"]
        assert "final_index_write" in item["blocked_outputs"]


def test_gp431_440_safety_blockers_keep_danger_actions_locked():
    board = get_vault_pack_rebuild_safety_blocker_board()

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
    assert "final_rebuilt_index_write" in blocked_actions
    assert "final_pack_overwrite" in blocked_actions
    assert "provider_dependency" in blocked_actions
    assert "delete_restore_physical_move" in blocked_actions


def test_gp431_440_readiness_declares_next_tower_status_bridge_layer():
    checkpoint = get_vault_pack_rebuild_service_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_blackseed_capsule_index_repair_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["headless_rebuild_only"] is True
    assert checkpoint["checks"]["rebuild_exposes_no_raw_bytes"] is True
    assert checkpoint["checks"]["final_index_write_locked_by_doctrine"] is True
    assert checkpoint["checks"]["source_no_provider_raw_public_direct"] is True
    assert checkpoint["checks"]["candidates_use_pack_receipts_merkle"] is True
    assert checkpoint["checks"]["candidates_no_raw_path_provider"] is True
    assert checkpoint["checks"]["candidates_no_final_write_or_overwrite"] is True
    assert checkpoint["checks"]["chunk_plans_opaque_no_raw_move"] is True
    assert checkpoint["checks"]["receipt_guards_append_only_no_rewrite"] is True
    assert checkpoint["checks"]["merkle_verified_no_raw_provider"] is True
    assert checkpoint["checks"]["previews_only_no_write_public_raw"] is True
    assert checkpoint["checks"]["outputs_tower_teller_no_portal_dashboard_raw_write"] is True
    assert "HEADLESS TOWER STATUS BRIDGE" in checkpoint["next_recommended_layer"]


def test_gp431_440_global_locks_preserve_headless_no_drive_behavior():
    assert LOCKS["rebuild_source_contract_allowed"] is True
    assert LOCKS["sealed_pack_rebuild_candidates_allowed"] is True
    assert LOCKS["pack_chunk_reconstruction_planning_allowed"] is True
    assert LOCKS["receipt_chain_rebuild_guard_allowed"] is True
    assert LOCKS["merkle_root_rebuild_verification_allowed"] is True
    assert LOCKS["rebuilt_pack_index_preview_allowed"] is True
    assert LOCKS["tower_teller_rebuild_output_allowed"] is True

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
    assert LOCKS["final_rebuilt_index_write_allowed"] is False
    assert LOCKS["final_pack_overwrite_allowed"] is False
    assert LOCKS["sealed_pack_bytes_write_allowed"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False
    assert LOCKS["external_sync_unlocked"] is False


def test_gp431_440_routes_are_json_only_no_public_page_route():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/vault-pack-rebuild-service-layer.json",
        "/vault/vault-pack-rebuild-service-shell.json",
        "/vault/rebuild-source-contract.json",
        "/vault/sealed-pack-rebuild-candidate-board.json",
        "/vault/pack-chunk-reconstruction-plan-builder.json",
        "/vault/receipt-chain-rebuild-guard.json",
        "/vault/merkle-root-rebuild-verifier.json",
        "/vault/rebuilt-pack-index-preview-board.json",
        "/vault/tower-teller-rebuild-output-contract.json",
        "/vault/vault-pack-rebuild-safety-blocker-board.json",
        "/vault/vault-pack-rebuild-service-readiness-checkpoint.json",
        "/vault/gp431-status.json",
        "/vault/gp440-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert '@app.route("/vault/vault-pack-rebuild-service-layer")' not in app_text
