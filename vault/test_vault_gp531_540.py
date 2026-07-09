
from pathlib import Path

from vault.cold_copy_restore_drill_layer_service import (
    DOCTRINE,
    LOCKS,
    get_cold_copy_manifest_verification_board,
    get_cold_copy_restore_drill_home,
    get_cold_copy_restore_drill_readiness_checkpoint,
    get_cold_copy_restore_drill_safety_blocker_board,
    get_restore_drill_eligibility_board,
    get_restore_integrity_comparison_board,
    get_restore_reconstruction_dry_run_board,
    get_restore_rollback_abort_guard_board,
    get_restore_target_sandbox_draft_board,
    get_tower_restore_drill_receipt_draft_ledger,
    validate_cold_copy_restore_drill_layer,
)


def test_gp531_540_readiness_checkpoint_passes():
    result = validate_cold_copy_restore_drill_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Cold copy restore drill layer" in result[
        "readiness_label"
    ]


def test_gp531_540_doctrine_is_restore_drill_only():
    home = get_cold_copy_restore_drill_home()

    assert home["ready"] is True
    assert home["doctrine"]["tower"] == "face_protocol_authority"
    assert home["doctrine"]["teller"] == "workflow_request_source"
    assert home["doctrine"]["vault"] == "sealed_memory"
    assert home["doctrine"]["correct_flow"] == (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    )
    assert home["doctrine"]["cold_copy_restore_drill_only"] is True
    assert home["doctrine"]["sandbox_reconstruction_only"] is True
    assert home["doctrine"]["integrity_comparison_only"] is True
    assert home["doctrine"][
        "tower_restore_drill_control_required"
    ] is True
    assert home["doctrine"]["actual_restore_execution_allowed"] is False
    assert home["doctrine"]["production_recovery_write_allowed"] is False
    assert home["doctrine"]["final_rebuilt_index_write_allowed"] is False
    assert home["doctrine"]["final_pack_overwrite_allowed"] is False
    assert home["doctrine"]["sealed_pack_bytes_write_allowed"] is False
    assert home["doctrine"][
        "backup_package_materialization_allowed"
    ] is False
    assert home["doctrine"]["teller_can_call_vault_directly"] is False


def test_gp531_540_restore_drill_eligibility_is_not_actual_restore():
    board = get_restore_drill_eligibility_board()

    assert board["ready"] is True
    assert board["eligibility_count"] >= 2
    assert board["all_manifests_verified"] is True
    assert board["all_package_hashes_verified"] is True
    assert board["all_custody_receipts_verified"] is True
    assert board["all_mutation_locks_verified"] is True
    assert board["all_eligible_for_restore_drill"] is True
    assert board["none_eligible_for_actual_restore"] is True
    assert board["all_tower_control_required"] is True
    assert board["no_raw_file_bytes_present"] is True
    assert board["no_public_links_present"] is True

    for row in board["eligibility_rows"]:
        assert row["eligibility_state"] == (
            "eligible_for_cold_copy_restore_drill_only"
        )
        assert row["cold_copy_manifest_verified"] == 1
        assert row["cold_copy_package_hash_verified"] == 1
        assert row["custody_receipt_verified"] == 1
        assert row["mutation_locks_verified"] == 1
        assert row["eligible_for_restore_drill"] == 1
        assert row["eligible_for_actual_restore"] == 0
        assert row["tower_control_required"] == 1
        assert row["raw_file_bytes_present"] == 0
        assert row["public_links_present"] == 0


def test_gp531_540_manifest_verification_uses_hashes_only():
    board = get_cold_copy_manifest_verification_board()

    assert board["ready"] is True
    assert board["verification_count"] >= 2
    assert board["all_manifest_hashes_verified"] is True
    assert board["all_package_hashes_verified"] is True
    assert board["all_custody_hashes_verified"] is True
    assert board["all_source_hashes_consistent"] is True
    assert board["no_raw_file_bytes_inspected"] is True
    assert board["no_raw_paths_exposed"] is True
    assert board["no_public_links_exposed"] is True
    assert board[
        "all_verification_bundle_hashes_present"
    ] is True

    for row in board["verifications"]:
        assert row["verification_state"] == (
            "cold_copy_manifest_package_custody_hashes_verified"
        )
        assert len(row["backup_manifest_hash"]) == 64
        assert len(row["offline_package_hash"]) == 64
        assert len(row["chain_of_custody_receipt_hash"]) == 64
        assert len(row["cold_copy_verification_hash"]) == 64
        assert row["manifest_hash_verified"] == 1
        assert row["package_hash_verified"] == 1
        assert row["custody_hash_verified"] == 1
        assert row["source_hashes_consistent"] == 1
        assert row["raw_file_bytes_inspected"] == 0
        assert row["raw_paths_exposed"] == 0
        assert row["public_links_exposed"] == 0
        assert len(row["verification_bundle_hash"]) == 64


def test_gp531_540_restore_sandbox_is_isolated_and_no_write():
    board = get_restore_target_sandbox_draft_board()

    assert board["ready"] is True
    assert board["sandbox_count"] >= 2
    assert board["all_isolated_sandbox_required"] is True
    assert board["no_production_target_allowed"] is True
    assert board["no_raw_target_path_visible"] is True
    assert board["no_external_provider_target"] is True
    assert board["no_physical_media_write"] is True
    assert board["no_physical_object_move"] is True
    assert board["no_sandbox_write_executed"] is True
    assert board["all_sandbox_identifier_hashes_present"] is True

    for row in board["sandbox_drafts"]:
        assert row["sandbox_state"] == (
            "restore_target_sandbox_draft_ready_hash_only"
        )
        assert row["isolated_sandbox_required"] == 1
        assert row["production_target_allowed"] == 0
        assert row["raw_target_path_visible"] == 0
        assert row["external_provider_target_allowed"] == 0
        assert row["physical_media_write_allowed"] == 0
        assert row["physical_object_move_allowed"] == 0
        assert row["sandbox_write_executed"] == 0
        assert len(row["sandbox_identifier_hash"]) == 64


def test_gp531_540_reconstruction_dry_run_has_no_mutation():
    board = get_restore_reconstruction_dry_run_board()

    assert board["ready"] is True
    assert board["reconstruction_count"] >= 2
    assert board[
        "all_hash_graph_reconstruction_simulated"
    ] is True
    assert board[
        "all_receipt_chain_reconstruction_simulated"
    ] is True
    assert board[
        "all_metadata_capsule_reconstruction_simulated"
    ] is True
    assert board["no_actual_restore_executed"] is True
    assert board["no_production_write_executed"] is True
    assert board["no_final_index_write_executed"] is True
    assert board["no_pack_overwrite_executed"] is True
    assert board[
        "no_sealed_pack_bytes_write_executed"
    ] is True
    assert board["no_package_materialized"] is True
    assert board["all_simulation_hashes_present"] is True

    for row in board["reconstructions"]:
        assert row["reconstruction_state"] == (
            "restore_reconstruction_dry_run_passed_no_mutation"
        )
        assert row["hash_graph_reconstruction_simulated"] == 1
        assert row["receipt_chain_reconstruction_simulated"] == 1
        assert row["metadata_capsule_reconstruction_simulated"] == 1
        assert row["actual_restore_executed"] == 0
        assert row["production_write_executed"] == 0
        assert row["final_index_write_executed"] == 0
        assert row["pack_overwrite_executed"] == 0
        assert row["sealed_pack_bytes_write_executed"] == 0
        assert row["package_materialized"] == 0
        assert len(row["reconstruction_simulation_hash"]) == 64


def test_gp531_540_integrity_comparison_matches_all_expected_hashes():
    board = get_restore_integrity_comparison_board()

    assert board["ready"] is True
    assert board["comparison_count"] >= 2
    assert board["all_manifest_hashes_match"] is True
    assert board["all_package_hashes_match"] is True
    assert board["all_custody_hashes_match"] is True
    assert board[
        "all_receipt_chain_integrity_matches"
    ] is True
    assert board["all_proof_integrity_matches"] is True
    assert board["all_overall_integrity_matches"] is True
    assert board["all_comparison_hashes_present"] is True

    for row in board["comparisons"]:
        assert row["comparison_state"] == (
            "restore_integrity_comparison_passed_hashes_match"
        )
        assert row["expected_manifest_hash"] == (
            row["simulated_manifest_hash"]
        )
        assert row["expected_package_hash"] == (
            row["simulated_package_hash"]
        )
        assert row["expected_custody_hash"] == (
            row["simulated_custody_hash"]
        )
        assert row["manifest_hash_match"] == 1
        assert row["package_hash_match"] == 1
        assert row["custody_hash_match"] == 1
        assert row["receipt_chain_integrity_match"] == 1
        assert row["proof_integrity_match"] == 1
        assert row["overall_integrity_match"] == 1
        assert len(row["integrity_comparison_hash"]) == 64


def test_gp531_540_rollback_and_abort_guards_are_engaged():
    board = get_restore_rollback_abort_guard_board()

    assert board["ready"] is True
    assert board["guard_count"] >= 2
    assert board["all_abort_on_hash_mismatch"] is True
    assert board["all_abort_on_receipt_mismatch"] is True
    assert board["all_abort_on_proof_mismatch"] is True
    assert board["all_rollback_on_any_mutation"] is True
    assert board["all_actual_restore_locked"] is True
    assert board["all_production_write_locked"] is True
    assert board["all_final_index_write_locked"] is True
    assert board["all_pack_overwrite_locked"] is True
    assert board[
        "all_sealed_pack_bytes_write_locked"
    ] is True
    assert board["all_delete_purge_locked"] is True
    assert board["all_quarantine_release_locked"] is True
    assert board["all_physical_object_move_locked"] is True
    assert board["all_guard_hashes_present"] is True

    for row in board["guards"]:
        assert row["guard_state"] == (
            "restore_rollback_abort_guards_engaged"
        )
        assert row["abort_on_hash_mismatch"] == 1
        assert row["abort_on_receipt_mismatch"] == 1
        assert row["abort_on_proof_mismatch"] == 1
        assert row["rollback_required_on_any_mutation"] == 1
        assert row["actual_restore_locked"] == 1
        assert row["production_write_locked"] == 1
        assert row["final_index_write_locked"] == 1
        assert row["pack_overwrite_locked"] == 1
        assert row["sealed_pack_bytes_write_locked"] == 1
        assert row["delete_purge_locked"] == 1
        assert row["quarantine_release_locked"] == 1
        assert row["physical_object_move_locked"] == 1
        assert len(row["guard_hash"]) == 64


def test_gp531_540_restore_drill_receipts_are_tower_controlled_drafts():
    ledger = get_tower_restore_drill_receipt_draft_ledger()

    assert ledger["ready"] is True
    assert ledger["receipt_count"] >= 2
    assert ledger["all_tower_controlled"] is True
    assert ledger["all_owner_admin_review_required"] is True
    assert ledger[
        "all_step_up_required_for_future_restore"
    ] is True
    assert ledger["no_actual_restore_executed"] is True
    assert ledger["no_production_write_executed"] is True
    assert ledger["no_package_materialized"] is True
    assert ledger["no_raw_file_bytes_receipted"] is True
    assert ledger["no_raw_paths_receipted"] is True
    assert ledger["no_raw_tokens_receipted"] is True
    assert ledger["no_public_links_receipted"] is True
    assert ledger["all_receipts_draft"] is True
    assert ledger["all_append_only"] is True
    assert ledger["all_immutable"] is True
    assert ledger["all_receipt_hashes_present"] is True

    for row in ledger["receipt_drafts"]:
        assert row["receipt_state"] == (
            "tower_restore_drill_receipt_draft_ready"
        )
        assert row["tower_controlled"] == 1
        assert row["owner_admin_review_required"] == 1
        assert row["step_up_required_for_future_restore"] == 1
        assert row["actual_restore_executed"] == 0
        assert row["production_write_executed"] == 0
        assert row["package_materialized"] == 0
        assert row["raw_file_bytes_receipted"] == 0
        assert row["raw_paths_receipted"] == 0
        assert row["raw_tokens_receipted"] == 0
        assert row["public_links_receipted"] == 0
        assert row["receipt_finalized"] == 0
        assert row["append_only"] == 1
        assert row["mutable"] == 0
        assert len(row["restore_drill_receipt_hash"]) == 64


def test_gp531_540_safety_blockers_prevent_real_restore_and_access():
    board = get_cold_copy_restore_drill_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked = {
        row["blocked_action"]
        for row in board["blockers"]
    }

    assert "actual_restore_execution" in blocked
    assert "production_recovery_write" in blocked
    assert "final_rebuilt_index_write" in blocked
    assert "final_pack_overwrite" in blocked
    assert "sealed_pack_bytes_write" in blocked
    assert "backup_package_materialization" in blocked
    assert "raw_file_bytes_returned_by_json" in blocked
    assert "raw_path_or_file_url_exposure" in blocked
    assert "raw_token_exposure" in blocked
    assert "public_view_download_or_proof_link" in blocked
    assert "external_provider_restore" in blocked
    assert "teller_direct_restore_or_vault_call" in blocked
    assert "direct_vault_user_portal" in blocked
    assert "public_vault_dashboard" in blocked
    assert "delete_purge_quarantine_release" in blocked
    assert "physical_object_move" in blocked


def test_gp531_540_readiness_declares_next_recovery_authorization_gate():
    checkpoint = get_cold_copy_restore_drill_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_cold_copy_lock_ready"] is True
    assert checkpoint["checks"]["drill_sandbox_integrity_only"] is True
    assert checkpoint["checks"]["tower_control_required"] is True
    assert checkpoint["checks"][
        "no_actual_restore_or_production_write"
    ] is True
    assert checkpoint["checks"][
        "no_final_index_pack_or_bytes_write"
    ] is True
    assert checkpoint["checks"][
        "manifest_package_custody_hashes_verified"
    ] is True
    assert checkpoint["checks"][
        "reconstruction_no_restore_or_writes"
    ] is True
    assert checkpoint["checks"][
        "all_integrity_comparisons_match"
    ] is True
    assert checkpoint["checks"][
        "all_restore_mutation_locks_engaged"
    ] is True
    assert checkpoint["restore_drill_status"] == (
        "cold_copy_hash_reconstruction_drill_passed_no_mutation"
    )
    assert "RECOVERY EXECUTION AUTHORIZATION GATE" in (
        checkpoint["next_recommended_layer"]
    )


def test_gp531_540_global_locks_preserve_no_real_restore_or_exposure():
    assert LOCKS["cold_copy_restore_drill_layer"] is True
    assert LOCKS["restore_reconstruction_dry_runs_allowed"] is True
    assert LOCKS["restore_integrity_comparisons_allowed"] is True
    assert LOCKS["rollback_abort_guards_allowed"] is True

    assert LOCKS["actual_restore_execution_allowed"] is False
    assert LOCKS["production_recovery_write_allowed"] is False
    assert LOCKS["final_rebuilt_index_write_allowed"] is False
    assert LOCKS["final_pack_overwrite_allowed"] is False
    assert LOCKS["sealed_pack_bytes_write_allowed"] is False
    assert LOCKS["backup_package_materialization_allowed"] is False
    assert LOCKS["offline_package_write_allowed"] is False
    assert LOCKS["external_provider_export_allowed"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["index_mutation_allowed"] is False
    assert LOCKS["pack_mutation_allowed"] is False
    assert LOCKS["metadata_mutation_allowed"] is False
    assert LOCKS["production_target_access_allowed"] is False
    assert LOCKS["physical_media_write_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False

    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["public_url_created"] is False
    assert LOCKS["share_link_created"] is False

    assert LOCKS["teller_direct_restore_allowed"] is False
    assert LOCKS["teller_to_vault_direct_call_allowed"] is False
    assert LOCKS["direct_vault_user_portal_allowed"] is False
    assert LOCKS["public_vault_dashboard_allowed"] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS["quarantine_release_allowed"] is False


def test_gp531_540_routes_are_json_only():
    app_text = Path("web/app.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_routes = [
        "/vault/cold-copy-restore-drill-layer.json",
        "/vault/cold-copy-restore-drill-shell.json",
        "/vault/restore-drill-eligibility-board.json",
        "/vault/cold-copy-manifest-verification-board.json",
        "/vault/restore-target-sandbox-draft-board.json",
        "/vault/restore-reconstruction-dry-run-board.json",
        "/vault/restore-integrity-comparison-board.json",
        "/vault/restore-rollback-abort-guard-board.json",
        "/vault/tower-restore-drill-receipt-draft-ledger.json",
        "/vault/cold-copy-restore-drill-safety-blocker-board.json",
        "/vault/cold-copy-restore-drill-readiness-checkpoint.json",
        "/vault/gp531-status.json",
        "/vault/gp540-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert (
        '@app.route("/vault/cold-copy-restore-drill-layer")'
        not in app_text
    )
