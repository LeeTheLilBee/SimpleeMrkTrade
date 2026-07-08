
from pathlib import Path

from vault.backup_export_cold_copy_lock_layer_service import (
    DOCTRINE,
    LOCKS,
    get_backup_chain_of_custody_receipt_draft_ledger,
    get_backup_export_cold_copy_lock_home,
    get_backup_export_cold_copy_lock_readiness_checkpoint,
    get_backup_export_cold_copy_safety_blocker_board,
    get_backup_export_manifest_draft_board,
    get_cold_copy_dry_run_verification_board,
    get_cold_copy_eligibility_from_recovery_prep_board,
    get_cold_copy_target_lock_board,
    get_offline_export_package_hash_board,
    get_tower_cold_copy_approval_requirement_board,
    validate_backup_export_cold_copy_lock_layer,
)


def test_gp521_530_readiness_checkpoint_passes():
    result = validate_backup_export_cold_copy_lock_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Backup export cold copy lock layer" in result["readiness_label"]


def test_gp521_530_doctrine_is_hash_manifest_lock_only():
    home = get_backup_export_cold_copy_lock_home()

    assert home["ready"] is True
    assert home["doctrine"]["tower"] == "face_protocol_authority"
    assert home["doctrine"]["teller"] == "workflow_request_source"
    assert home["doctrine"]["vault"] == "sealed_memory"
    assert home["doctrine"]["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller"
    assert home["doctrine"]["backup_export_cold_copy_lock_only"] is True
    assert home["doctrine"]["hash_and_manifest_only"] is True
    assert home["doctrine"]["dry_run_only"] is True
    assert home["doctrine"]["tower_cold_copy_approval_required"] is True
    assert home["doctrine"]["actual_backup_export_execution_allowed"] is False
    assert home["doctrine"]["backup_package_materialization_allowed"] is False
    assert home["doctrine"]["external_provider_export_allowed"] is False
    assert home["doctrine"]["physical_object_move_allowed"] is False
    assert home["doctrine"]["teller_can_call_vault_directly"] is False


def test_gp521_530_cold_copy_eligibility_is_manifest_only_no_actual_export():
    board = get_cold_copy_eligibility_from_recovery_prep_board()

    assert board["ready"] is True
    assert board["eligibility_count"] >= 2
    assert board["all_recovery_prep_verified"] is True
    assert board["all_dry_run_passed"] is True
    assert board["all_mutation_locks_engaged"] is True
    assert board["all_eligible_for_manifest_draft"] is True
    assert board["none_eligible_for_actual_export"] is True
    assert board["all_tower_cold_copy_approval_required"] is True
    assert board["no_raw_file_bytes_present"] is True
    assert board["no_public_links_present"] is True

    for item in board["eligibility_rows"]:
        assert item["eligibility_state"] == "eligible_for_cold_copy_manifest_draft_only"
        assert item["recovery_prep_verified"] == 1
        assert item["dry_run_passed"] == 1
        assert item["mutation_locks_engaged"] == 1
        assert item["eligible_for_manifest_draft"] == 1
        assert item["eligible_for_actual_export"] == 0
        assert item["tower_cold_copy_approval_required"] == 1
        assert item["raw_file_bytes_present"] == 0
        assert item["public_links_present"] == 0


def test_gp521_530_backup_manifest_drafts_are_hash_only_and_not_exported():
    board = get_backup_export_manifest_draft_board()

    assert board["ready"] is True
    assert board["manifest_count"] >= 2
    assert board["all_manifest_hash_only"] is True
    assert board["no_actual_export_executed"] is True
    assert board["all_have_manifest_hash"] is True
    assert board["no_raw_file_bytes"] is True
    assert board["no_raw_paths"] is True
    assert board["no_raw_file_urls"] is True
    assert board["no_raw_tokens"] is True
    assert board["no_public_links"] is True

    for item in board["manifest_drafts"]:
        assert item["manifest_state"] == "backup_export_manifest_draft_ready_hash_only"
        assert item["manifest_kind"] == "cold_copy_manifest_draft"
        assert item["manifest_hash_only"] == 1
        assert item["actual_export_executed"] == 0
        assert len(item["backup_manifest_hash"]) == 64
        assert item["raw_file_bytes_included"] == 0
        assert item["raw_path_included"] == 0
        assert item["raw_file_url_included"] == 0
        assert item["raw_token_included"] == 0
        assert item["public_link_included"] == 0


def test_gp521_530_cold_copy_targets_lock_provider_public_path_and_physical_move():
    board = get_cold_copy_target_lock_board()

    assert board["ready"] is True
    assert board["target_lock_count"] >= 2
    assert board["all_local_cold_copy_lane_reserved"] is True
    assert board["no_external_provider_target"] is True
    assert board["no_public_target"] is True
    assert board["no_raw_target_path_visible"] is True
    assert board["no_physical_media_write"] is True
    assert board["no_physical_object_move"] is True
    assert board["no_provider_dependency"] is True
    assert board["all_have_target_lock_hash"] is True

    for item in board["target_locks"]:
        assert item["target_lock_state"] == "cold_copy_target_locked_no_provider_no_public_no_physical_move"
        assert item["local_cold_copy_lane_reserved"] == 1
        assert item["external_provider_target_allowed"] == 0
        assert item["public_target_allowed"] == 0
        assert item["raw_target_path_visible"] == 0
        assert item["physical_media_write_allowed"] == 0
        assert item["physical_object_move_allowed"] == 0
        assert item["provider_dependency_required"] == 0
        assert len(item["target_lock_hash"]) == 64


def test_gp521_530_offline_package_hashes_are_not_materialized_or_written():
    board = get_offline_export_package_hash_board()

    assert board["ready"] is True
    assert board["package_hash_count"] >= 2
    assert board["all_package_hash_only"] is True
    assert board["no_package_materialized"] is True
    assert board["no_offline_package_write"] is True
    assert board["all_have_offline_package_hash"] is True
    assert board["no_raw_file_bytes"] is True
    assert board["no_raw_paths"] is True
    assert board["no_raw_file_urls"] is True
    assert board["no_raw_tokens"] is True
    assert board["no_public_links"] is True

    for item in board["package_hashes"]:
        assert item["package_state"] == "offline_export_package_hash_ready_not_materialized"
        assert item["package_hash_only"] == 1
        assert item["package_materialized"] == 0
        assert item["offline_package_write_executed"] == 0
        assert len(item["offline_package_hash"]) == 64
        assert item["raw_file_bytes_included"] == 0
        assert item["raw_path_included"] == 0
        assert item["raw_file_url_included"] == 0
        assert item["raw_token_included"] == 0
        assert item["public_link_included"] == 0


def test_gp521_530_chain_of_custody_receipts_are_draft_no_export_no_raw_public():
    ledger = get_backup_chain_of_custody_receipt_draft_ledger()

    assert ledger["ready"] is True
    assert ledger["custody_receipt_count"] >= 2
    assert ledger["all_receipts_draft"] is True
    assert ledger["all_append_only"] is True
    assert ledger["all_immutable"] is True
    assert ledger["no_actual_export_executed"] is True
    assert ledger["no_package_materialized"] is True
    assert ledger["no_physical_object_move"] is True
    assert ledger["no_raw_file_bytes_receipted"] is True
    assert ledger["no_public_links_receipted"] is True
    assert ledger["all_have_custody_hash"] is True

    for item in ledger["custody_receipts"]:
        assert item["receipt_state"] == "backup_chain_of_custody_receipt_draft_ready_not_exported"
        assert item["receipt_finalized"] == 0
        assert item["append_only"] == 1
        assert item["mutable"] == 0
        assert item["actual_export_executed"] == 0
        assert item["package_materialized"] == 0
        assert item["physical_object_move_executed"] == 0
        assert item["raw_file_bytes_receipted"] == 0
        assert item["public_link_receipted"] == 0
        assert len(item["chain_of_custody_receipt_hash"]) == 64


def test_gp521_530_tower_cold_copy_approval_required_before_export():
    board = get_tower_cold_copy_approval_requirement_board()

    assert board["ready"] is True
    assert board["approval_requirement_count"] >= 2
    assert board["all_tower_cold_copy_approval_required"] is True
    assert board["all_owner_admin_approval_required"] is True
    assert board["all_step_up_required"] is True
    assert board["all_dual_receipt_required"] is True
    assert board["all_manifest_hash_required"] is True
    assert board["all_dry_run_verification_required"] is True
    assert board["no_actual_export_before_approval"] is True
    assert board["no_external_provider_export"] is True

    for item in board["approval_requirements"]:
        assert item["approval_state"] == "tower_cold_copy_approval_required_before_any_export"
        assert item["tower_cold_copy_approval_required"] == 1
        assert item["owner_admin_approval_required"] == 1
        assert item["step_up_required"] == 1
        assert item["dual_receipt_required"] == 1
        assert item["manifest_hash_required"] == 1
        assert item["dry_run_verification_required"] == 1
        assert item["actual_export_allowed_before_approval"] == 0
        assert item["external_provider_export_allowed"] == 0


def test_gp521_530_cold_copy_dry_run_verification_has_no_export_provider_materialization():
    board = get_cold_copy_dry_run_verification_board()

    assert board["ready"] is True
    assert board["verification_count"] >= 2
    assert board["all_dry_run_verified"] is True
    assert board["no_actual_export_executed"] is True
    assert board["no_provider_export_executed"] is True
    assert board["no_package_materialized"] is True
    assert board["all_raw_file_bytes_absent"] is True
    assert board["all_raw_paths_absent"] is True
    assert board["all_raw_tokens_absent"] is True
    assert board["all_public_links_absent"] is True
    assert board["all_have_verification_hash"] is True

    for item in board["verifications"]:
        assert item["verification_state"] == "cold_copy_dry_run_verified_no_export_no_materialization"
        assert item["dry_run_verified"] == 1
        assert item["actual_export_executed"] == 0
        assert item["provider_export_executed"] == 0
        assert item["package_materialized"] == 0
        assert item["raw_file_bytes_absent"] == 1
        assert item["raw_paths_absent"] == 1
        assert item["raw_tokens_absent"] == 1
        assert item["public_links_absent"] == 1
        assert len(item["verification_hash"]) == 64


def test_gp521_530_safety_blockers_prevent_export_materialization_provider_raw_public():
    board = get_backup_export_cold_copy_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "actual_backup_export_execution" in blocked_actions
    assert "backup_package_materialization" in blocked_actions
    assert "offline_package_write" in blocked_actions
    assert "external_provider_export" in blocked_actions
    assert "external_sync" in blocked_actions
    assert "raw_file_bytes_returned_by_json" in blocked_actions
    assert "raw_path_or_file_url_exposure" in blocked_actions
    assert "raw_token_exposure" in blocked_actions
    assert "public_view_download_or_proof_link" in blocked_actions
    assert "teller_to_vault_direct_call" in blocked_actions
    assert "restore_or_rebuild_execution" in blocked_actions
    assert "delete_purge_quarantine_release" in blocked_actions
    assert "physical_object_move" in blocked_actions


def test_gp521_530_readiness_declares_next_cold_copy_restore_drill_layer():
    checkpoint = get_backup_export_cold_copy_lock_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_recovery_safe_rebuild_prep_ready"] is True
    assert checkpoint["checks"]["lock_hash_dry_run_only"] is True
    assert checkpoint["checks"]["tower_cold_copy_approval_required"] is True
    assert checkpoint["checks"]["no_actual_export_package_provider_or_physical_move"] is True
    assert checkpoint["checks"]["eligibility_manifest_only_no_actual_export"] is True
    assert checkpoint["checks"]["manifests_hash_only_not_exported"] is True
    assert checkpoint["checks"]["target_locks_no_provider_public_physical"] is True
    assert checkpoint["checks"]["package_hashes_only_not_materialized"] is True
    assert checkpoint["checks"]["custody_receipts_draft_append_only_no_export"] is True
    assert checkpoint["checks"]["approvals_required_before_export"] is True
    assert checkpoint["checks"]["verifications_dry_run_no_export_provider_materialization"] is True
    assert checkpoint["cold_copy_status"] == "manifest_hashes_and_locks_ready_no_export"
    assert "COLD COPY RESTORE DRILL" in checkpoint["next_recommended_layer"]


def test_gp521_530_global_locks_preserve_no_export_or_provider_dependency():
    assert LOCKS["backup_export_cold_copy_lock_layer"] is True
    assert LOCKS["backup_export_manifest_drafts_allowed"] is True
    assert LOCKS["offline_export_package_hashes_allowed"] is True
    assert LOCKS["tower_cold_copy_approval_requirements_allowed"] is True

    assert LOCKS["actual_backup_export_execution_allowed"] is False
    assert LOCKS["backup_package_materialization_allowed"] is False
    assert LOCKS["offline_package_write_allowed"] is False
    assert LOCKS["external_provider_export_allowed"] is False
    assert LOCKS["external_sync_unlocked"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["public_url_created"] is False
    assert LOCKS["share_link_created"] is False
    assert LOCKS["teller_to_vault_direct_call_allowed"] is False
    assert LOCKS["direct_vault_user_portal_allowed"] is False
    assert LOCKS["public_vault_dashboard_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["final_rebuilt_index_write_allowed"] is False
    assert LOCKS["final_pack_overwrite_allowed"] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False


def test_gp521_530_routes_are_json_only_no_public_page_route():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/backup-export-cold-copy-lock-layer.json",
        "/vault/backup-export-cold-copy-lock-shell.json",
        "/vault/cold-copy-eligibility-from-recovery-prep-board.json",
        "/vault/backup-export-manifest-draft-board.json",
        "/vault/cold-copy-target-lock-board.json",
        "/vault/offline-export-package-hash-board.json",
        "/vault/backup-chain-of-custody-receipt-draft-ledger.json",
        "/vault/tower-cold-copy-approval-requirement-board.json",
        "/vault/cold-copy-dry-run-verification-board.json",
        "/vault/backup-export-cold-copy-safety-blocker-board.json",
        "/vault/backup-export-cold-copy-lock-readiness-checkpoint.json",
        "/vault/gp521-status.json",
        "/vault/gp530-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert '@app.route("/vault/backup-export-cold-copy-lock-layer")' not in app_text
