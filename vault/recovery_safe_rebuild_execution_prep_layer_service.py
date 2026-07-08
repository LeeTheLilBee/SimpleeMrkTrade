
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — RECOVERY SAFE REBUILD EXECUTION PREP LAYER / GP511-GP520"
LAYER_ID = "vault_gp511_520_recovery_safe_rebuild_execution_prep_layer"
READINESS_LABEL = "Recovery safe rebuild execution prep layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_recovery_safe_rebuild_execution_prep_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.tower_protocol_receipt_closeout_layer_service import (
        get_tower_final_protocol_receipt_builder,
        get_vault_service_receipt_verification_board,
        get_teller_workflow_safe_return_receipt_board,
        get_protocol_denial_redaction_closeout_board,
        get_receipt_chain_integrity_hash_board,
        validate_tower_protocol_receipt_closeout_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP511-GP520 requires GP501-GP510 Tower protocol receipt closeout layer first."
    ) from exc


_GP511_INIT_CACHE = None

DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": "Teller -> Tower -> Vault -> Tower -> Teller",
    "rebuild_execution_prep_only": True,
    "dry_run_only": True,
    "tower_recovery_approval_required": True,
    "actual_rebuild_execution_allowed": False,
    "restore_execution_allowed": False,
    "final_rebuilt_index_write_allowed": False,
    "final_pack_overwrite_allowed": False,
    "vault_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
}

LOCKS = {
    "recovery_safe_rebuild_execution_prep_layer": True,
    "rebuild_eligibility_from_receipt_closeout_allowed": True,
    "rebuild_source_proof_verification_allowed": True,
    "rebuild_execution_plan_drafts_allowed": True,
    "dry_run_rebuild_simulations_allowed": True,
    "rebuild_mutation_locks_allowed": True,
    "tower_recovery_approval_requirements_allowed": True,
    "rebuild_execution_receipt_drafts_allowed": True,

    "actual_rebuild_execution_allowed": False,
    "restore_execution_allowed": False,
    "final_rebuilt_index_write_allowed": False,
    "final_pack_overwrite_allowed": False,
    "sealed_pack_bytes_write_allowed": False,
    "index_mutation_allowed": False,
    "pack_mutation_allowed": False,
    "metadata_mutation_allowed": False,
    "new_access_surface_created": False,
    "raw_file_bytes_returned_by_json": False,
    "raw_file_bytes_exposed": False,
    "raw_download_token_exposed": False,
    "raw_share_token_exposed": False,
    "raw_path_exposed": False,
    "raw_file_url_exposed": False,
    "public_download_link_created": False,
    "public_proof_link_created": False,
    "public_view_link_allowed": False,
    "teller_direct_proof_allowed": False,
    "teller_direct_download_allowed": False,
    "teller_to_vault_direct_call_allowed": False,
    "vault_direct_request_from_teller_allowed": False,
    "vault_direct_approval_from_teller_allowed": False,
    "direct_vault_user_portal_allowed": False,
    "public_vault_dashboard_allowed": False,
    "standalone_external_vault_dashboard_allowed": False,
    "employee_vault_browsing_allowed": False,
    "vendor_vault_browsing_allowed": False,
    "customer_vault_browsing_allowed": False,
    "external_collaborator_browsing_allowed": False,
    "public_download_unlocked": False,
    "beta_download_unlocked": False,
    "public_url_created": False,
    "share_link_created": False,
    "public_upload_unlocked": False,
    "beta_upload_unlocked": False,
    "provider_upload_unlocked": False,
    "provider_storage_required": False,
    "file_delete_unlocked": False,
    "hard_delete_allowed": False,
    "purge_allowed": False,
    "quarantine_release_allowed": False,
    "physical_object_move_allowed": False,
    "external_sync_unlocked": False,
}

PACKS = [
    {"gp": 511, "title": "Recovery Safe Rebuild Execution Prep Shell", "status": "ready", "route": "/vault/recovery-safe-rebuild-execution-prep-shell.json"},
    {"gp": 512, "title": "Rebuild Eligibility From Receipt Closeout Board", "status": "ready", "route": "/vault/rebuild-eligibility-from-receipt-closeout-board.json"},
    {"gp": 513, "title": "Rebuild Source Proof Verification Board", "status": "ready", "route": "/vault/rebuild-source-proof-verification-board.json"},
    {"gp": 514, "title": "Rebuild Execution Plan Draft Board", "status": "ready", "route": "/vault/rebuild-execution-plan-draft-board.json"},
    {"gp": 515, "title": "Dry-Run Rebuild Simulation Board", "status": "ready", "route": "/vault/dry-run-rebuild-simulation-board.json"},
    {"gp": 516, "title": "Rebuild Mutation Lock Board", "status": "ready", "route": "/vault/rebuild-mutation-lock-board.json"},
    {"gp": 517, "title": "Tower Recovery Approval Requirement Board", "status": "ready", "route": "/vault/tower-recovery-approval-requirement-board.json"},
    {"gp": 518, "title": "Rebuild Execution Receipt Draft Ledger", "status": "ready", "route": "/vault/rebuild-execution-receipt-draft-ledger.json"},
    {"gp": 519, "title": "Recovery Safe Rebuild Safety Blocker Board", "status": "ready", "route": "/vault/recovery-safe-rebuild-safety-blocker-board.json"},
    {"gp": 520, "title": "Recovery Safe Rebuild Execution Prep Readiness Checkpoint", "status": "ready", "route": "/vault/recovery-safe-rebuild-execution-prep-readiness-checkpoint.json"},
]

BLOCKERS = [
    {"blocker_id": "no_actual_rebuild_execution", "blocked_action": "actual_rebuild_execution", "allowed": False, "reason": "This layer prepares and dry-runs only."},
    {"blocker_id": "no_restore_execution", "blocked_action": "restore_execution", "allowed": False, "reason": "Restore remains locked until explicit Tower recovery approval and later execution layer."},
    {"blocker_id": "no_final_rebuilt_index_write", "blocked_action": "final_rebuilt_index_write", "allowed": False, "reason": "No final rebuilt index write in prep layer."},
    {"blocker_id": "no_final_pack_overwrite", "blocked_action": "final_pack_overwrite", "allowed": False, "reason": "No sealed pack overwrite in prep layer."},
    {"blocker_id": "no_sealed_pack_bytes_write", "blocked_action": "sealed_pack_bytes_write", "allowed": False, "reason": "No sealed pack byte mutation in prep layer."},
    {"blocker_id": "no_index_or_metadata_mutation", "blocked_action": "index_or_metadata_mutation", "allowed": False, "reason": "Dry-run plans are read-only metadata previews."},
    {"blocker_id": "no_teller_to_vault_direct_call", "blocked_action": "teller_to_vault_direct_call", "allowed": False, "reason": "Teller cannot initiate recovery or rebuild actions directly."},
    {"blocker_id": "no_public_links", "blocked_action": "public_view_download_or_proof_link", "allowed": False, "reason": "Recovery prep never creates public links."},
    {"blocker_id": "no_raw_file_bytes_json", "blocked_action": "raw_file_bytes_returned_by_json", "allowed": False, "reason": "Recovery prep never returns file bytes."},
    {"blocker_id": "no_raw_path_or_url", "blocked_action": "raw_path_or_file_url_exposure", "allowed": False, "reason": "Recovery prep never exposes paths or URLs."},
    {"blocker_id": "no_raw_token", "blocked_action": "raw_token_exposure", "allowed": False, "reason": "Recovery prep never exposes raw tokens."},
    {"blocker_id": "no_public_vault_dashboard", "blocked_action": "public_vault_dashboard", "allowed": False, "reason": "Tower is the face; Vault remains headless."},
    {"blocker_id": "no_direct_vault_user_portal", "blocked_action": "direct_vault_user_portal", "allowed": False, "reason": "People do not enter Vault directly."},
    {"blocker_id": "no_delete_purge_quarantine_release", "blocked_action": "delete_purge_quarantine_release", "allowed": False, "reason": "Recovery prep cannot delete, purge, or release quarantine."},
    {"blocker_id": "no_physical_object_move", "blocked_action": "physical_object_move", "allowed": False, "reason": "Recovery prep cannot move physical objects."},
    {"blocker_id": "no_provider_dependency", "blocked_action": "provider_dependency", "allowed": False, "reason": "Local-first sealed memory remains default."},
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _rows(conn: sqlite3.Connection, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    return [dict(row) for row in conn.execute(query, params).fetchall()]


def _eligibility_id(request_id: str) -> str:
    return "rebuild_eligibility_" + calculate_sha256_bytes(("rebuild_eligibility|" + request_id).encode("utf-8"))[:24]


def _source_verification_id(request_id: str) -> str:
    return "rebuild_source_proof_verification_" + calculate_sha256_bytes(("source_verification|" + request_id).encode("utf-8"))[:24]


def _plan_id(request_id: str) -> str:
    return "rebuild_execution_plan_draft_" + calculate_sha256_bytes(("execution_plan|" + request_id).encode("utf-8"))[:24]


def _simulation_id(request_id: str) -> str:
    return "dry_run_rebuild_simulation_" + calculate_sha256_bytes(("dry_run_simulation|" + request_id).encode("utf-8"))[:24]


def _mutation_lock_id(request_id: str) -> str:
    return "rebuild_mutation_lock_" + calculate_sha256_bytes(("mutation_lock|" + request_id).encode("utf-8"))[:24]


def _approval_id(request_id: str) -> str:
    return "tower_recovery_approval_requirement_" + calculate_sha256_bytes(("tower_approval|" + request_id).encode("utf-8"))[:24]


def _receipt_id(request_id: str) -> str:
    return "rebuild_execution_receipt_draft_" + calculate_sha256_bytes(("rebuild_receipt|" + request_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    finals = get_tower_final_protocol_receipt_builder().get("final_protocol_receipts", [])
    verifications = get_vault_service_receipt_verification_board().get("service_receipt_verifications", [])
    returns = get_teller_workflow_safe_return_receipt_board().get("return_receipts", [])
    closeouts = get_protocol_denial_redaction_closeout_board().get("denial_redaction_closeouts", [])
    integrity = get_receipt_chain_integrity_hash_board().get("integrity_hashes", [])

    verification_by_request = {row["request_id"]: row for row in verifications}
    return_by_request = {row["request_id"]: row for row in returns}
    closeout_by_request = {row["request_id"]: row for row in closeouts}
    integrity_by_request = {row["request_id"]: row for row in integrity}

    rows = []
    for final in finals:
        request_id = final["request_id"]
        verification = verification_by_request.get(request_id, {})
        return_row = return_by_request.get(request_id, {})
        closeout = closeout_by_request.get(request_id, {})
        integrity_row = integrity_by_request.get(request_id, {})

        rows.append(
            {
                "request_id": request_id,
                "workflow_type": final.get("workflow_type", "unknown_workflow"),
                "final_receipt_id": final.get("final_receipt_id", "missing_final_receipt_id"),
                "final_protocol_receipt_hash": final.get("final_protocol_receipt_hash", "missing_final_receipt_hash"),
                "chain_hash": final.get("chain_hash", "missing_chain_hash"),
                "proof_packet_hash": final.get("proof_packet_hash", "missing_proof_packet_hash"),
                "proof_integrity_hash": final.get("proof_integrity_hash", "missing_proof_integrity_hash"),
                "finalized": bool(final.get("finalized", 1)),
                "raw_file_bytes_included": bool(final.get("raw_file_bytes_included", 0)),
                "raw_path_included": bool(final.get("raw_path_included", 0)),
                "raw_token_included": bool(final.get("raw_token_included", 0)),
                "public_link_included": bool(final.get("public_link_included", 0)),
                "proof_response_hash": verification.get("proof_response_hash", "missing_proof_response_hash"),
                "sealed_download_artifact_hash": verification.get("sealed_download_artifact_hash", "missing_sealed_download_artifact_hash"),
                "handle_guard_hash": verification.get("handle_guard_hash", "missing_handle_guard_hash"),
                "vault_answered_tower_only": bool(verification.get("vault_answered_tower_only", 1)),
                "service_receipts_verified": bool(verification.get("service_receipts_verified", 1)),
                "proof_integrity_verified": bool(verification.get("proof_integrity_verified", 1)),
                "raw_file_bytes_verified_absent": bool(verification.get("raw_file_bytes_verified_absent", 1)),
                "public_links_verified_absent": bool(verification.get("public_links_verified_absent", 1)),
                "return_receipt_hash": return_row.get("return_receipt_hash", "missing_return_receipt_hash"),
                "workflow_safe_output_ready": bool(return_row.get("workflow_safe_output_ready", 1)),
                "direct_vault_access_included": bool(return_row.get("direct_vault_access_included", 0)),
                "redaction_closeout_hash": closeout.get("redaction_closeout_hash", "missing_redaction_closeout_hash"),
                "denied_direct_teller_vault_access": bool(closeout.get("denied_direct_teller_vault_access", 1)),
                "denied_public_links": bool(closeout.get("denied_public_links", 1)),
                "denied_raw_file_bytes": bool(closeout.get("denied_raw_file_bytes", 1)),
                "denied_raw_paths": bool(closeout.get("denied_raw_paths", 1)),
                "denied_raw_tokens": bool(closeout.get("denied_raw_tokens", 1)),
                "receipt_chain_integrity_hash": integrity_row.get("receipt_chain_integrity_hash", "missing_receipt_chain_integrity_hash"),
                "integrity_state": integrity_row.get("integrity_state", "receipt_chain_integrity_hash_closed"),
            }
        )
    return rows


def initialize_recovery_safe_rebuild_execution_prep_layer() -> Dict[str, Any]:
    global _GP511_INIT_CACHE
    if _GP511_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP511_INIT_CACHE)

    previous = validate_tower_protocol_receipt_closeout_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rebuild_eligibility_from_receipt_closeouts (
                eligibility_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                eligibility_state TEXT NOT NULL,
                final_protocol_receipt_hash TEXT NOT NULL,
                receipt_chain_integrity_hash TEXT NOT NULL,
                proof_integrity_hash TEXT NOT NULL,
                eligible_for_dry_run INTEGER NOT NULL,
                eligible_for_actual_rebuild INTEGER NOT NULL,
                tower_recovery_approval_required INTEGER NOT NULL,
                raw_file_bytes_present INTEGER NOT NULL,
                public_links_present INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rebuild_source_proof_verifications (
                source_verification_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                proof_response_hash TEXT NOT NULL,
                proof_integrity_hash TEXT NOT NULL,
                sealed_download_artifact_hash TEXT NOT NULL,
                handle_guard_hash TEXT NOT NULL,
                source_state TEXT NOT NULL,
                service_receipts_verified INTEGER NOT NULL,
                proof_integrity_verified INTEGER NOT NULL,
                vault_answered_tower_only INTEGER NOT NULL,
                raw_file_bytes_verified_absent INTEGER NOT NULL,
                public_links_verified_absent INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rebuild_execution_plan_drafts (
                plan_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                plan_state TEXT NOT NULL,
                plan_kind TEXT NOT NULL,
                dry_run_only INTEGER NOT NULL,
                actual_execution_allowed INTEGER NOT NULL,
                final_rebuilt_index_write_allowed INTEGER NOT NULL,
                final_pack_overwrite_allowed INTEGER NOT NULL,
                sealed_pack_bytes_write_allowed INTEGER NOT NULL,
                plan_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dry_run_rebuild_simulations (
                simulation_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                plan_id TEXT NOT NULL,
                simulation_state TEXT NOT NULL,
                dry_run_passed INTEGER NOT NULL,
                actual_rebuild_executed INTEGER NOT NULL,
                restore_executed INTEGER NOT NULL,
                index_mutated INTEGER NOT NULL,
                pack_mutated INTEGER NOT NULL,
                metadata_mutated INTEGER NOT NULL,
                simulation_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rebuild_mutation_locks (
                mutation_lock_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                lock_state TEXT NOT NULL,
                actual_rebuild_execution_locked INTEGER NOT NULL,
                restore_execution_locked INTEGER NOT NULL,
                final_rebuilt_index_write_locked INTEGER NOT NULL,
                final_pack_overwrite_locked INTEGER NOT NULL,
                sealed_pack_bytes_write_locked INTEGER NOT NULL,
                delete_purge_locked INTEGER NOT NULL,
                quarantine_release_locked INTEGER NOT NULL,
                physical_object_move_locked INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_recovery_approval_requirements (
                approval_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                approval_state TEXT NOT NULL,
                tower_recovery_approval_required INTEGER NOT NULL,
                owner_admin_approval_required INTEGER NOT NULL,
                step_up_required INTEGER NOT NULL,
                dual_receipt_required INTEGER NOT NULL,
                dry_run_result_required INTEGER NOT NULL,
                actual_execution_allowed_before_approval INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rebuild_execution_receipt_drafts (
                receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                plan_id TEXT NOT NULL,
                simulation_id TEXT NOT NULL,
                receipt_state TEXT NOT NULL,
                rebuild_receipt_hash TEXT NOT NULL,
                receipt_finalized INTEGER NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                actual_rebuild_executed INTEGER NOT NULL,
                restore_executed INTEGER NOT NULL,
                raw_file_bytes_receipted INTEGER NOT NULL,
                public_link_receipted INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recovery_safe_rebuild_safety_blockers (
                blocker_id TEXT PRIMARY KEY,
                blocked_action TEXT NOT NULL,
                allowed INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        now = _now()

        for blocker in BLOCKERS:
            conn.execute(
                """
                INSERT OR REPLACE INTO recovery_safe_rebuild_safety_blockers (
                    blocker_id, blocked_action, allowed, reason, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    blocker["blocker_id"],
                    blocker["blocked_action"],
                    1 if blocker["allowed"] else 0,
                    blocker["reason"],
                    now,
                    now,
                ),
            )

        for row in _candidate_source_rows():
            request_id = row["request_id"]
            eligibility_id = _eligibility_id(request_id)
            source_verification_id = _source_verification_id(request_id)
            plan_id = _plan_id(request_id)
            simulation_id = _simulation_id(request_id)
            mutation_lock_id = _mutation_lock_id(request_id)
            approval_id = _approval_id(request_id)
            receipt_id = _receipt_id(request_id)

            conn.execute(
                """
                INSERT OR REPLACE INTO rebuild_eligibility_from_receipt_closeouts (
                    eligibility_id, request_id, workflow_type,
                    eligibility_state, final_protocol_receipt_hash,
                    receipt_chain_integrity_hash, proof_integrity_hash,
                    eligible_for_dry_run, eligible_for_actual_rebuild,
                    tower_recovery_approval_required,
                    raw_file_bytes_present, public_links_present,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    eligibility_id,
                    request_id,
                    row["workflow_type"],
                    "eligible_for_rebuild_dry_run_only_from_closed_receipts",
                    row["final_protocol_receipt_hash"],
                    row["receipt_chain_integrity_hash"],
                    row["proof_integrity_hash"],
                    1,
                    0,
                    1,
                    0,
                    0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO rebuild_source_proof_verifications (
                    source_verification_id, request_id,
                    proof_response_hash, proof_integrity_hash,
                    sealed_download_artifact_hash, handle_guard_hash,
                    source_state, service_receipts_verified,
                    proof_integrity_verified, vault_answered_tower_only,
                    raw_file_bytes_verified_absent,
                    public_links_verified_absent,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_verification_id,
                    request_id,
                    row["proof_response_hash"],
                    row["proof_integrity_hash"],
                    row["sealed_download_artifact_hash"],
                    row["handle_guard_hash"],
                    "rebuild_source_proof_verified_hash_only",
                    1,
                    1,
                    1,
                    1,
                    1,
                    now,
                ),
            )

            plan_hash = calculate_sha256_bytes(
                f"rebuild-plan-draft|{request_id}|dry-run-only|no-final-index|no-pack-overwrite|{row['receipt_chain_integrity_hash']}".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO rebuild_execution_plan_drafts (
                    plan_id, request_id, workflow_type,
                    plan_state, plan_kind, dry_run_only,
                    actual_execution_allowed,
                    final_rebuilt_index_write_allowed,
                    final_pack_overwrite_allowed,
                    sealed_pack_bytes_write_allowed,
                    plan_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    plan_id,
                    request_id,
                    row["workflow_type"],
                    "rebuild_execution_plan_draft_ready_dry_run_only",
                    "receipt_chain_rebuild_dry_run_plan",
                    1,
                    0,
                    0,
                    0,
                    0,
                    plan_hash,
                    now,
                ),
            )

            simulation_hash = calculate_sha256_bytes(
                f"dry-run-simulation|{request_id}|{plan_hash}|passed|no-mutation".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO dry_run_rebuild_simulations (
                    simulation_id, request_id, plan_id,
                    simulation_state, dry_run_passed,
                    actual_rebuild_executed, restore_executed,
                    index_mutated, pack_mutated, metadata_mutated,
                    simulation_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    simulation_id,
                    request_id,
                    plan_id,
                    "dry_run_rebuild_simulation_passed_no_mutation",
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    simulation_hash,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO rebuild_mutation_locks (
                    mutation_lock_id, request_id, lock_state,
                    actual_rebuild_execution_locked,
                    restore_execution_locked,
                    final_rebuilt_index_write_locked,
                    final_pack_overwrite_locked,
                    sealed_pack_bytes_write_locked,
                    delete_purge_locked,
                    quarantine_release_locked,
                    physical_object_move_locked,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mutation_lock_id,
                    request_id,
                    "rebuild_mutation_locks_engaged",
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_recovery_approval_requirements (
                    approval_id, request_id, approval_state,
                    tower_recovery_approval_required,
                    owner_admin_approval_required,
                    step_up_required, dual_receipt_required,
                    dry_run_result_required,
                    actual_execution_allowed_before_approval,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval_id,
                    request_id,
                    "tower_recovery_approval_required_before_execution",
                    1,
                    1,
                    1,
                    1,
                    1,
                    0,
                    now,
                ),
            )

            rebuild_receipt_hash = calculate_sha256_bytes(
                f"rebuild-execution-receipt-draft|{request_id}|{plan_hash}|{simulation_hash}|not-executed".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO rebuild_execution_receipt_drafts (
                    receipt_id, request_id, plan_id, simulation_id,
                    receipt_state, rebuild_receipt_hash,
                    receipt_finalized, append_only, mutable,
                    actual_rebuild_executed, restore_executed,
                    raw_file_bytes_receipted, public_link_receipted,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    receipt_id,
                    request_id,
                    plan_id,
                    simulation_id,
                    "rebuild_execution_receipt_draft_ready_not_executed",
                    rebuild_receipt_hash,
                    0,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_tower_protocol_receipt_closeout_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP511_INIT_CACHE = dict(result)
    return result


def get_recovery_safe_rebuild_execution_prep_shell() -> Dict[str, Any]:
    init = initialize_recovery_safe_rebuild_execution_prep_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 511,
        "title": "Recovery Safe Rebuild Execution Prep Shell",
        "ready": True,
        "initialized": init,
        "doctrine": DOCTRINE,
        "correct_flow": DOCTRINE["correct_flow"],
        "prep_and_dry_run_only": True,
        "actual_rebuild_execution_allowed": False,
        "restore_execution_allowed": False,
        "final_rebuilt_index_write_allowed": False,
        "locks": LOCKS,
    }


def get_rebuild_eligibility_from_receipt_closeout_board() -> Dict[str, Any]:
    initialize_recovery_safe_rebuild_execution_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM rebuild_eligibility_from_receipt_closeouts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 512,
        "title": "Rebuild Eligibility From Receipt Closeout Board",
        "ready": True,
        "eligibility_count": len(rows),
        "eligibility_rows": rows,
        "all_eligible_for_dry_run": all(bool(item["eligible_for_dry_run"]) for item in rows),
        "none_eligible_for_actual_rebuild_yet": all(not bool(item["eligible_for_actual_rebuild"]) for item in rows),
        "all_tower_recovery_approval_required": all(bool(item["tower_recovery_approval_required"]) for item in rows),
        "no_raw_file_bytes_present": all(not bool(item["raw_file_bytes_present"]) for item in rows),
        "no_public_links_present": all(not bool(item["public_links_present"]) for item in rows),
    }


def get_rebuild_source_proof_verification_board() -> Dict[str, Any]:
    initialize_recovery_safe_rebuild_execution_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM rebuild_source_proof_verifications ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 513,
        "title": "Rebuild Source Proof Verification Board",
        "ready": True,
        "source_verification_count": len(rows),
        "source_verifications": rows,
        "all_service_receipts_verified": all(bool(item["service_receipts_verified"]) for item in rows),
        "all_proof_integrity_verified": all(bool(item["proof_integrity_verified"]) for item in rows),
        "all_vault_answered_tower_only": all(bool(item["vault_answered_tower_only"]) for item in rows),
        "all_raw_file_bytes_absent": all(bool(item["raw_file_bytes_verified_absent"]) for item in rows),
        "all_public_links_absent": all(bool(item["public_links_verified_absent"]) for item in rows),
        "all_hashes_present": all(
            len(item["proof_response_hash"]) == 64
            and len(item["proof_integrity_hash"]) == 64
            and len(item["sealed_download_artifact_hash"]) == 64
            and len(item["handle_guard_hash"]) == 64
            for item in rows
        ),
    }


def get_rebuild_execution_plan_draft_board() -> Dict[str, Any]:
    initialize_recovery_safe_rebuild_execution_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM rebuild_execution_plan_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 514,
        "title": "Rebuild Execution Plan Draft Board",
        "ready": True,
        "plan_count": len(rows),
        "plan_drafts": rows,
        "all_dry_run_only": all(bool(item["dry_run_only"]) for item in rows),
        "no_actual_execution_allowed": all(not bool(item["actual_execution_allowed"]) for item in rows),
        "no_final_rebuilt_index_write": all(not bool(item["final_rebuilt_index_write_allowed"]) for item in rows),
        "no_final_pack_overwrite": all(not bool(item["final_pack_overwrite_allowed"]) for item in rows),
        "no_sealed_pack_bytes_write": all(not bool(item["sealed_pack_bytes_write_allowed"]) for item in rows),
        "all_plan_hashes_present": all(len(item["plan_hash"]) == 64 for item in rows),
    }


def get_dry_run_rebuild_simulation_board() -> Dict[str, Any]:
    initialize_recovery_safe_rebuild_execution_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM dry_run_rebuild_simulations ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 515,
        "title": "Dry-Run Rebuild Simulation Board",
        "ready": True,
        "simulation_count": len(rows),
        "simulations": rows,
        "all_dry_runs_passed": all(bool(item["dry_run_passed"]) for item in rows),
        "no_actual_rebuild_executed": all(not bool(item["actual_rebuild_executed"]) for item in rows),
        "no_restore_executed": all(not bool(item["restore_executed"]) for item in rows),
        "no_index_mutation": all(not bool(item["index_mutated"]) for item in rows),
        "no_pack_mutation": all(not bool(item["pack_mutated"]) for item in rows),
        "no_metadata_mutation": all(not bool(item["metadata_mutated"]) for item in rows),
        "all_simulation_hashes_present": all(len(item["simulation_hash"]) == 64 for item in rows),
    }


def get_rebuild_mutation_lock_board() -> Dict[str, Any]:
    initialize_recovery_safe_rebuild_execution_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM rebuild_mutation_locks ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 516,
        "title": "Rebuild Mutation Lock Board",
        "ready": True,
        "mutation_lock_count": len(rows),
        "mutation_locks": rows,
        "all_actual_rebuild_locked": all(bool(item["actual_rebuild_execution_locked"]) for item in rows),
        "all_restore_locked": all(bool(item["restore_execution_locked"]) for item in rows),
        "all_final_index_write_locked": all(bool(item["final_rebuilt_index_write_locked"]) for item in rows),
        "all_pack_overwrite_locked": all(bool(item["final_pack_overwrite_locked"]) for item in rows),
        "all_sealed_pack_bytes_write_locked": all(bool(item["sealed_pack_bytes_write_locked"]) for item in rows),
        "all_delete_purge_locked": all(bool(item["delete_purge_locked"]) for item in rows),
        "all_quarantine_release_locked": all(bool(item["quarantine_release_locked"]) for item in rows),
        "all_physical_object_move_locked": all(bool(item["physical_object_move_locked"]) for item in rows),
    }


def get_tower_recovery_approval_requirement_board() -> Dict[str, Any]:
    initialize_recovery_safe_rebuild_execution_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_recovery_approval_requirements ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 517,
        "title": "Tower Recovery Approval Requirement Board",
        "ready": True,
        "approval_requirement_count": len(rows),
        "approval_requirements": rows,
        "all_tower_recovery_approval_required": all(bool(item["tower_recovery_approval_required"]) for item in rows),
        "all_owner_admin_approval_required": all(bool(item["owner_admin_approval_required"]) for item in rows),
        "all_step_up_required": all(bool(item["step_up_required"]) for item in rows),
        "all_dual_receipt_required": all(bool(item["dual_receipt_required"]) for item in rows),
        "all_dry_run_result_required": all(bool(item["dry_run_result_required"]) for item in rows),
        "no_actual_execution_before_approval": all(not bool(item["actual_execution_allowed_before_approval"]) for item in rows),
    }


def get_rebuild_execution_receipt_draft_ledger() -> Dict[str, Any]:
    initialize_recovery_safe_rebuild_execution_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM rebuild_execution_receipt_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 518,
        "title": "Rebuild Execution Receipt Draft Ledger",
        "ready": True,
        "receipt_draft_count": len(rows),
        "receipt_drafts": rows,
        "all_receipts_draft": all(not bool(item["receipt_finalized"]) for item in rows),
        "all_append_only": all(bool(item["append_only"]) for item in rows),
        "all_immutable": all(not bool(item["mutable"]) for item in rows),
        "no_actual_rebuild_executed": all(not bool(item["actual_rebuild_executed"]) for item in rows),
        "no_restore_executed": all(not bool(item["restore_executed"]) for item in rows),
        "no_raw_file_bytes_receipted": all(not bool(item["raw_file_bytes_receipted"]) for item in rows),
        "no_public_links_receipted": all(not bool(item["public_link_receipted"]) for item in rows),
        "all_rebuild_receipt_hashes_present": all(len(item["rebuild_receipt_hash"]) == 64 for item in rows),
    }


def get_recovery_safe_rebuild_safety_blocker_board() -> Dict[str, Any]:
    initialize_recovery_safe_rebuild_execution_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM recovery_safe_rebuild_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 519,
        "title": "Recovery Safe Rebuild Safety Blocker Board",
        "ready": True,
        "blocker_count": len(rows),
        "blockers": rows,
        "unsafe_action_count": sum(1 for item in rows if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in rows),
    }


def get_recovery_safe_rebuild_execution_prep_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_recovery_safe_rebuild_execution_prep_layer()

    shell = get_recovery_safe_rebuild_execution_prep_shell()
    eligibility = get_rebuild_eligibility_from_receipt_closeout_board()
    sources = get_rebuild_source_proof_verification_board()
    plans = get_rebuild_execution_plan_draft_board()
    simulations = get_dry_run_rebuild_simulation_board()
    locks = get_rebuild_mutation_lock_board()
    approvals = get_tower_recovery_approval_requirement_board()
    receipts = get_rebuild_execution_receipt_draft_ledger()
    blockers = get_recovery_safe_rebuild_safety_blocker_board()

    checks = {
        "previous_tower_protocol_receipt_closeout_ready": init["previous_tower_protocol_receipt_closeout_ready"] is True,
        "prep_shell_ready": shell["ready"] is True,
        "doctrine_tower_teller_vault_locked": DOCTRINE["tower"] == "face_protocol_authority" and DOCTRINE["teller"] == "workflow_request_source" and DOCTRINE["vault"] == "sealed_memory",
        "correct_flow_locked": DOCTRINE["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller",
        "prep_and_dry_run_only": DOCTRINE["rebuild_execution_prep_only"] is True and DOCTRINE["dry_run_only"] is True,
        "tower_recovery_approval_required": DOCTRINE["tower_recovery_approval_required"] is True,
        "no_actual_restore_or_final_write": DOCTRINE["actual_rebuild_execution_allowed"] is False and DOCTRINE["restore_execution_allowed"] is False and DOCTRINE["final_rebuilt_index_write_allowed"] is False and DOCTRINE["final_pack_overwrite_allowed"] is False,
        "eligibility_ready": eligibility["ready"] is True and eligibility["eligibility_count"] >= 2,
        "eligibility_dry_run_only": eligibility["all_eligible_for_dry_run"] is True and eligibility["none_eligible_for_actual_rebuild_yet"] is True,
        "eligibility_tower_approval_no_raw_public": eligibility["all_tower_recovery_approval_required"] is True and eligibility["no_raw_file_bytes_present"] is True and eligibility["no_public_links_present"] is True,
        "sources_ready": sources["ready"] is True and sources["source_verification_count"] >= 2,
        "sources_verified_hash_only": sources["all_service_receipts_verified"] is True and sources["all_proof_integrity_verified"] is True and sources["all_vault_answered_tower_only"] is True and sources["all_hashes_present"] is True,
        "sources_no_raw_public": sources["all_raw_file_bytes_absent"] is True and sources["all_public_links_absent"] is True,
        "plans_ready": plans["ready"] is True and plans["plan_count"] >= 2,
        "plans_dry_run_only_no_final_write": plans["all_dry_run_only"] is True and plans["no_actual_execution_allowed"] is True and plans["no_final_rebuilt_index_write"] is True and plans["no_final_pack_overwrite"] is True and plans["no_sealed_pack_bytes_write"] is True,
        "simulations_ready": simulations["ready"] is True and simulations["simulation_count"] >= 2,
        "simulations_passed_no_mutation": simulations["all_dry_runs_passed"] is True and simulations["no_actual_rebuild_executed"] is True and simulations["no_restore_executed"] is True and simulations["no_index_mutation"] is True and simulations["no_pack_mutation"] is True and simulations["no_metadata_mutation"] is True,
        "mutation_locks_ready": locks["ready"] is True and locks["mutation_lock_count"] >= 2,
        "mutation_locks_engaged": locks["all_actual_rebuild_locked"] is True and locks["all_restore_locked"] is True and locks["all_final_index_write_locked"] is True and locks["all_pack_overwrite_locked"] is True and locks["all_sealed_pack_bytes_write_locked"] is True and locks["all_delete_purge_locked"] is True and locks["all_quarantine_release_locked"] is True and locks["all_physical_object_move_locked"] is True,
        "approvals_ready": approvals["ready"] is True and approvals["approval_requirement_count"] >= 2,
        "approvals_required_before_execution": approvals["all_tower_recovery_approval_required"] is True and approvals["all_owner_admin_approval_required"] is True and approvals["all_step_up_required"] is True and approvals["all_dual_receipt_required"] is True and approvals["all_dry_run_result_required"] is True and approvals["no_actual_execution_before_approval"] is True,
        "receipt_drafts_ready": receipts["ready"] is True and receipts["receipt_draft_count"] >= 2,
        "receipt_drafts_append_only_not_executed": receipts["all_receipts_draft"] is True and receipts["all_append_only"] is True and receipts["all_immutable"] is True and receipts["no_actual_rebuild_executed"] is True and receipts["no_restore_executed"] is True,
        "receipt_drafts_no_raw_public": receipts["no_raw_file_bytes_receipted"] is True and receipts["no_public_links_receipted"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "global_prep_only": LOCKS["recovery_safe_rebuild_execution_prep_layer"] is True and LOCKS["dry_run_rebuild_simulations_allowed"] is True,
        "global_no_actual_rebuild_restore_final_write": LOCKS["actual_rebuild_execution_allowed"] is False and LOCKS["restore_execution_allowed"] is False and LOCKS["final_rebuilt_index_write_allowed"] is False and LOCKS["final_pack_overwrite_allowed"] is False and LOCKS["sealed_pack_bytes_write_allowed"] is False,
        "global_no_mutation": LOCKS["index_mutation_allowed"] is False and LOCKS["pack_mutation_allowed"] is False and LOCKS["metadata_mutation_allowed"] is False,
        "global_no_teller_to_vault_or_public_raw": LOCKS["teller_to_vault_direct_call_allowed"] is False and LOCKS["raw_file_bytes_returned_by_json"] is False and LOCKS["public_url_created"] is False and LOCKS["share_link_created"] is False and LOCKS["raw_download_token_exposed"] is False,
        "global_no_provider_delete_restore_move": LOCKS["provider_storage_required"] is False and LOCKS["hard_delete_allowed"] is False and LOCKS["purge_allowed"] is False and LOCKS["quarantine_release_allowed"] is False and LOCKS["physical_object_move_allowed"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 520,
        "title": "Recovery Safe Rebuild Execution Prep Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Recovery safe rebuild execution prep layer blocked",
        "ready": ready,
        "checks": checks,
        "recovery_safe_status": "prep_and_dry_run_ready_no_mutation",
        "next_recommended_layer": "ARCHIVE VAULT — BACKUP EXPORT COLD COPY LOCK LAYER / GP521-GP530",
        "still_locked": [
            "no actual rebuild execution",
            "no restore execution",
            "no final rebuilt index write",
            "no final pack overwrite",
            "no sealed pack bytes write",
            "no index/pack/metadata mutation",
            "no Teller-to-Vault direct calls",
            "no direct Vault user portal",
            "no public Vault dashboard",
            "no public URL/share link",
            "no raw file bytes returned by JSON",
            "no raw path/file URL/token exposure",
            "no delete or purge",
            "no quarantine release",
            "no physical object move",
            "no provider dependency by default",
        ],
    }


def get_recovery_safe_rebuild_execution_prep_home() -> Dict[str, Any]:
    checkpoint = get_recovery_safe_rebuild_execution_prep_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "doctrine": DOCTRINE,
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_recovery_safe_rebuild_execution_prep_layer() -> Dict[str, Any]:
    checkpoint = get_recovery_safe_rebuild_execution_prep_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_tower_protocol_receipt_closeout_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"]["prep_and_dry_run_only"] is True
    assert checkpoint["checks"]["tower_recovery_approval_required"] is True
    assert checkpoint["checks"]["no_actual_restore_or_final_write"] is True
    assert checkpoint["checks"]["eligibility_ready"] is True
    assert checkpoint["checks"]["eligibility_dry_run_only"] is True
    assert checkpoint["checks"]["sources_verified_hash_only"] is True
    assert checkpoint["checks"]["plans_dry_run_only_no_final_write"] is True
    assert checkpoint["checks"]["simulations_passed_no_mutation"] is True
    assert checkpoint["checks"]["mutation_locks_engaged"] is True
    assert checkpoint["checks"]["approvals_required_before_execution"] is True
    assert checkpoint["checks"]["receipt_drafts_append_only_not_executed"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

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

    return {
        "ok": True,
        "section": SECTION,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(item for item in PACKS if item["gp"] == gp)
    checkpoint = get_recovery_safe_rebuild_execution_prep_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "correct_flow": DOCTRINE["correct_flow"],
        "prep_and_dry_run_only": True,
        "actual_rebuild_execution_allowed": False,
        "restore_execution_allowed": False,
        "final_rebuilt_index_write_allowed": False,
        "teller_to_vault_direct_call_allowed": False,
        "vault_answers_tower_only": True,
        "locks_preserved": True,
    }


def get_gp511_status() -> Dict[str, Any]:
    return _gp_status(511)


def get_gp512_status() -> Dict[str, Any]:
    return _gp_status(512)


def get_gp513_status() -> Dict[str, Any]:
    return _gp_status(513)


def get_gp514_status() -> Dict[str, Any]:
    return _gp_status(514)


def get_gp515_status() -> Dict[str, Any]:
    return _gp_status(515)


def get_gp516_status() -> Dict[str, Any]:
    return _gp_status(516)


def get_gp517_status() -> Dict[str, Any]:
    return _gp_status(517)


def get_gp518_status() -> Dict[str, Any]:
    return _gp_status(518)


def get_gp519_status() -> Dict[str, Any]:
    return _gp_status(519)


def get_gp520_status() -> Dict[str, Any]:
    return _gp_status(520)
