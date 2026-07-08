
from pathlib import Path

from vault.recovery_safe_rebuild_execution_prep_layer_service import (
    DOCTRINE,
    LOCKS,
    get_dry_run_rebuild_simulation_board,
    get_rebuild_eligibility_from_receipt_closeout_board,
    get_rebuild_execution_plan_draft_board,
    get_rebuild_execution_receipt_draft_ledger,
    get_rebuild_mutation_lock_board,
    get_rebuild_source_proof_verification_board,
    get_recovery_safe_rebuild_execution_prep_home,
    get_recovery_safe_rebuild_execution_prep_readiness_checkpoint,
    get_recovery_safe_rebuild_safety_blocker_board,
    get_tower_recovery_approval_requirement_board,
    validate_recovery_safe_rebuild_execution_prep_layer,
)


def test_gp511_520_readiness_checkpoint_passes():
    result = validate_recovery_safe_rebuild_execution_prep_layer()

    assert result["ok"] is True
    assert result["ready"] is True
    assert "Recovery safe rebuild execution prep layer" in result["readiness_label"]


def test_gp511_520_doctrine_is_prep_and_dry_run_only():
    home = get_recovery_safe_rebuild_execution_prep_home()

    assert home["ready"] is True
    assert home["doctrine"]["tower"] == "face_protocol_authority"
    assert home["doctrine"]["teller"] == "workflow_request_source"
    assert home["doctrine"]["vault"] == "sealed_memory"
    assert home["doctrine"]["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller"
    assert home["doctrine"]["rebuild_execution_prep_only"] is True
    assert home["doctrine"]["dry_run_only"] is True
    assert home["doctrine"]["tower_recovery_approval_required"] is True
    assert home["doctrine"]["actual_rebuild_execution_allowed"] is False
    assert home["doctrine"]["restore_execution_allowed"] is False
    assert home["doctrine"]["final_rebuilt_index_write_allowed"] is False
    assert home["doctrine"]["final_pack_overwrite_allowed"] is False
    assert home["doctrine"]["teller_can_call_vault_directly"] is False


def test_gp511_520_eligibility_is_dry_run_only_and_requires_tower_approval():
    board = get_rebuild_eligibility_from_receipt_closeout_board()

    assert board["ready"] is True
    assert board["eligibility_count"] >= 2
    assert board["all_eligible_for_dry_run"] is True
    assert board["none_eligible_for_actual_rebuild_yet"] is True
    assert board["all_tower_recovery_approval_required"] is True
    assert board["no_raw_file_bytes_present"] is True
    assert board["no_public_links_present"] is True

    for item in board["eligibility_rows"]:
        assert item["eligibility_state"] == "eligible_for_rebuild_dry_run_only_from_closed_receipts"
        assert len(item["final_protocol_receipt_hash"]) == 64
        assert len(item["receipt_chain_integrity_hash"]) == 64
        assert len(item["proof_integrity_hash"]) == 64
        assert item["eligible_for_dry_run"] == 1
        assert item["eligible_for_actual_rebuild"] == 0
        assert item["tower_recovery_approval_required"] == 1
        assert item["raw_file_bytes_present"] == 0
        assert item["public_links_present"] == 0


def test_gp511_520_source_proofs_are_verified_hash_only():
    board = get_rebuild_source_proof_verification_board()

    assert board["ready"] is True
    assert board["source_verification_count"] >= 2
    assert board["all_service_receipts_verified"] is True
    assert board["all_proof_integrity_verified"] is True
    assert board["all_vault_answered_tower_only"] is True
    assert board["all_raw_file_bytes_absent"] is True
    assert board["all_public_links_absent"] is True
    assert board["all_hashes_present"] is True

    for item in board["source_verifications"]:
        assert item["source_state"] == "rebuild_source_proof_verified_hash_only"
        assert item["service_receipts_verified"] == 1
        assert item["proof_integrity_verified"] == 1
        assert item["vault_answered_tower_only"] == 1
        assert item["raw_file_bytes_verified_absent"] == 1
        assert item["public_links_verified_absent"] == 1


def test_gp511_520_plan_drafts_never_allow_actual_execution_or_final_writes():
    board = get_rebuild_execution_plan_draft_board()

    assert board["ready"] is True
    assert board["plan_count"] >= 2
    assert board["all_dry_run_only"] is True
    assert board["no_actual_execution_allowed"] is True
    assert board["no_final_rebuilt_index_write"] is True
    assert board["no_final_pack_overwrite"] is True
    assert board["no_sealed_pack_bytes_write"] is True
    assert board["all_plan_hashes_present"] is True

    for item in board["plan_drafts"]:
        assert item["plan_state"] == "rebuild_execution_plan_draft_ready_dry_run_only"
        assert item["plan_kind"] == "receipt_chain_rebuild_dry_run_plan"
        assert item["dry_run_only"] == 1
        assert item["actual_execution_allowed"] == 0
        assert item["final_rebuilt_index_write_allowed"] == 0
        assert item["final_pack_overwrite_allowed"] == 0
        assert item["sealed_pack_bytes_write_allowed"] == 0
        assert len(item["plan_hash"]) == 64


def test_gp511_520_dry_run_simulations_pass_without_mutation():
    board = get_dry_run_rebuild_simulation_board()

    assert board["ready"] is True
    assert board["simulation_count"] >= 2
    assert board["all_dry_runs_passed"] is True
    assert board["no_actual_rebuild_executed"] is True
    assert board["no_restore_executed"] is True
    assert board["no_index_mutation"] is True
    assert board["no_pack_mutation"] is True
    assert board["no_metadata_mutation"] is True
    assert board["all_simulation_hashes_present"] is True

    for item in board["simulations"]:
        assert item["simulation_state"] == "dry_run_rebuild_simulation_passed_no_mutation"
        assert item["dry_run_passed"] == 1
        assert item["actual_rebuild_executed"] == 0
        assert item["restore_executed"] == 0
        assert item["index_mutated"] == 0
        assert item["pack_mutated"] == 0
        assert item["metadata_mutated"] == 0
        assert len(item["simulation_hash"]) == 64


def test_gp511_520_mutation_locks_are_all_engaged():
    board = get_rebuild_mutation_lock_board()

    assert board["ready"] is True
    assert board["mutation_lock_count"] >= 2
    assert board["all_actual_rebuild_locked"] is True
    assert board["all_restore_locked"] is True
    assert board["all_final_index_write_locked"] is True
    assert board["all_pack_overwrite_locked"] is True
    assert board["all_sealed_pack_bytes_write_locked"] is True
    assert board["all_delete_purge_locked"] is True
    assert board["all_quarantine_release_locked"] is True
    assert board["all_physical_object_move_locked"] is True

    for item in board["mutation_locks"]:
        assert item["lock_state"] == "rebuild_mutation_locks_engaged"
        assert item["actual_rebuild_execution_locked"] == 1
        assert item["restore_execution_locked"] == 1
        assert item["final_rebuilt_index_write_locked"] == 1
        assert item["final_pack_overwrite_locked"] == 1
        assert item["sealed_pack_bytes_write_locked"] == 1
        assert item["delete_purge_locked"] == 1
        assert item["quarantine_release_locked"] == 1
        assert item["physical_object_move_locked"] == 1


def test_gp511_520_tower_recovery_approval_required_before_execution():
    board = get_tower_recovery_approval_requirement_board()

    assert board["ready"] is True
    assert board["approval_requirement_count"] >= 2
    assert board["all_tower_recovery_approval_required"] is True
    assert board["all_owner_admin_approval_required"] is True
    assert board["all_step_up_required"] is True
    assert board["all_dual_receipt_required"] is True
    assert board["all_dry_run_result_required"] is True
    assert board["no_actual_execution_before_approval"] is True

    for item in board["approval_requirements"]:
        assert item["approval_state"] == "tower_recovery_approval_required_before_execution"
        assert item["tower_recovery_approval_required"] == 1
        assert item["owner_admin_approval_required"] == 1
        assert item["step_up_required"] == 1
        assert item["dual_receipt_required"] == 1
        assert item["dry_run_result_required"] == 1
        assert item["actual_execution_allowed_before_approval"] == 0


def test_gp511_520_rebuild_receipts_are_draft_append_only_and_not_executed():
    ledger = get_rebuild_execution_receipt_draft_ledger()

    assert ledger["ready"] is True
    assert ledger["receipt_draft_count"] >= 2
    assert ledger["all_receipts_draft"] is True
    assert ledger["all_append_only"] is True
    assert ledger["all_immutable"] is True
    assert ledger["no_actual_rebuild_executed"] is True
    assert ledger["no_restore_executed"] is True
    assert ledger["no_raw_file_bytes_receipted"] is True
    assert ledger["no_public_links_receipted"] is True
    assert ledger["all_rebuild_receipt_hashes_present"] is True

    for item in ledger["receipt_drafts"]:
        assert item["receipt_state"] == "rebuild_execution_receipt_draft_ready_not_executed"
        assert item["receipt_finalized"] == 0
        assert item["append_only"] == 1
        assert item["mutable"] == 0
        assert item["actual_rebuild_executed"] == 0
        assert item["restore_executed"] == 0
        assert item["raw_file_bytes_receipted"] == 0
        assert item["public_link_receipted"] == 0
        assert len(item["rebuild_receipt_hash"]) == 64


def test_gp511_520_safety_blockers_prevent_actual_rebuild_restore_mutation_raw_public():
    board = get_recovery_safe_rebuild_safety_blocker_board()

    assert board["ready"] is True
    assert board["unsafe_action_count"] == 0
    assert board["all_dangerous_actions_blocked"] is True

    blocked_actions = {item["blocked_action"] for item in board["blockers"]}
    assert "actual_rebuild_execution" in blocked_actions
    assert "restore_execution" in blocked_actions
    assert "final_rebuilt_index_write" in blocked_actions
    assert "final_pack_overwrite" in blocked_actions
    assert "sealed_pack_bytes_write" in blocked_actions
    assert "index_or_metadata_mutation" in blocked_actions
    assert "teller_to_vault_direct_call" in blocked_actions
    assert "public_view_download_or_proof_link" in blocked_actions
    assert "raw_file_bytes_returned_by_json" in blocked_actions
    assert "raw_path_or_file_url_exposure" in blocked_actions
    assert "delete_purge_quarantine_release" in blocked_actions
    assert "physical_object_move" in blocked_actions


def test_gp511_520_readiness_declares_next_backup_export_cold_copy_lock_layer():
    checkpoint = get_recovery_safe_rebuild_execution_prep_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_tower_protocol_receipt_closeout_ready"] is True
    assert checkpoint["checks"]["prep_and_dry_run_only"] is True
    assert checkpoint["checks"]["tower_recovery_approval_required"] is True
    assert checkpoint["checks"]["no_actual_restore_or_final_write"] is True
    assert checkpoint["checks"]["eligibility_dry_run_only"] is True
    assert checkpoint["checks"]["plans_dry_run_only_no_final_write"] is True
    assert checkpoint["checks"]["simulations_passed_no_mutation"] is True
    assert checkpoint["checks"]["mutation_locks_engaged"] is True
    assert checkpoint["checks"]["approvals_required_before_execution"] is True
    assert checkpoint["recovery_safe_status"] == "prep_and_dry_run_ready_no_mutation"
    assert "BACKUP EXPORT COLD COPY LOCK" in checkpoint["next_recommended_layer"]


def test_gp511_520_global_locks_preserve_no_execution_or_mutation():
    assert LOCKS["recovery_safe_rebuild_execution_prep_layer"] is True
    assert LOCKS["dry_run_rebuild_simulations_allowed"] is True
    assert LOCKS["tower_recovery_approval_requirements_allowed"] is True

    assert LOCKS["actual_rebuild_execution_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["final_rebuilt_index_write_allowed"] is False
    assert LOCKS["final_pack_overwrite_allowed"] is False
    assert LOCKS["sealed_pack_bytes_write_allowed"] is False
    assert LOCKS["index_mutation_allowed"] is False
    assert LOCKS["pack_mutation_allowed"] is False
    assert LOCKS["metadata_mutation_allowed"] is False
    assert LOCKS["teller_to_vault_direct_call_allowed"] is False
    assert LOCKS["direct_vault_user_portal_allowed"] is False
    assert LOCKS["public_vault_dashboard_allowed"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False


def test_gp511_520_routes_are_json_only_no_public_page_route():
    app_text = Path("web/app.py").read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/recovery-safe-rebuild-execution-prep-layer.json",
        "/vault/recovery-safe-rebuild-execution-prep-shell.json",
        "/vault/rebuild-eligibility-from-receipt-closeout-board.json",
        "/vault/rebuild-source-proof-verification-board.json",
        "/vault/rebuild-execution-plan-draft-board.json",
        "/vault/dry-run-rebuild-simulation-board.json",
        "/vault/rebuild-mutation-lock-board.json",
        "/vault/tower-recovery-approval-requirement-board.json",
        "/vault/rebuild-execution-receipt-draft-ledger.json",
        "/vault/recovery-safe-rebuild-safety-blocker-board.json",
        "/vault/recovery-safe-rebuild-execution-prep-readiness-checkpoint.json",
        "/vault/gp511-status.json",
        "/vault/gp520-status.json",
    ]

    for route in required_routes:
        assert route in app_text

    assert '@app.route("/vault/recovery-safe-rebuild-execution-prep-layer")' not in app_text
