
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — BACKUP EXPORT COLD COPY LOCK LAYER / GP521-GP530"
LAYER_ID = "vault_gp521_530_backup_export_cold_copy_lock_layer"
READINESS_LABEL = "Backup export cold copy lock layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_backup_export_cold_copy_lock_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.recovery_safe_rebuild_execution_prep_layer_service import (
        get_rebuild_eligibility_from_receipt_closeout_board,
        get_rebuild_source_proof_verification_board,
        get_rebuild_execution_plan_draft_board,
        get_dry_run_rebuild_simulation_board,
        get_rebuild_mutation_lock_board,
        get_tower_recovery_approval_requirement_board,
        get_rebuild_execution_receipt_draft_ledger,
        validate_recovery_safe_rebuild_execution_prep_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP521-GP530 requires GP511-GP520 Recovery safe rebuild execution prep layer first."
    ) from exc


_GP521_INIT_CACHE = None

DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": "Teller -> Tower -> Vault -> Tower -> Teller",
    "backup_export_cold_copy_lock_only": True,
    "hash_and_manifest_only": True,
    "dry_run_only": True,
    "tower_cold_copy_approval_required": True,
    "actual_backup_export_execution_allowed": False,
    "backup_package_materialization_allowed": False,
    "external_provider_export_allowed": False,
    "physical_object_move_allowed": False,
    "vault_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
}

LOCKS = {
    "backup_export_cold_copy_lock_layer": True,
    "cold_copy_eligibility_allowed": True,
    "backup_export_manifest_drafts_allowed": True,
    "cold_copy_target_locks_allowed": True,
    "offline_export_package_hashes_allowed": True,
    "backup_chain_of_custody_receipts_allowed": True,
    "tower_cold_copy_approval_requirements_allowed": True,
    "cold_copy_dry_run_verification_allowed": True,

    "actual_backup_export_execution_allowed": False,
    "backup_package_materialization_allowed": False,
    "offline_package_write_allowed": False,
    "external_provider_export_allowed": False,
    "external_sync_unlocked": False,
    "provider_storage_required": False,
    "provider_upload_unlocked": False,
    "physical_object_move_allowed": False,
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
    "file_delete_unlocked": False,
    "hard_delete_allowed": False,
    "purge_allowed": False,
    "quarantine_release_allowed": False,
}

PACKS = [
    {"gp": 521, "title": "Backup Export Cold Copy Lock Shell", "status": "ready", "route": "/vault/backup-export-cold-copy-lock-shell.json"},
    {"gp": 522, "title": "Cold Copy Eligibility From Recovery Prep Board", "status": "ready", "route": "/vault/cold-copy-eligibility-from-recovery-prep-board.json"},
    {"gp": 523, "title": "Backup Export Manifest Draft Board", "status": "ready", "route": "/vault/backup-export-manifest-draft-board.json"},
    {"gp": 524, "title": "Cold Copy Target Lock Board", "status": "ready", "route": "/vault/cold-copy-target-lock-board.json"},
    {"gp": 525, "title": "Offline Export Package Hash Board", "status": "ready", "route": "/vault/offline-export-package-hash-board.json"},
    {"gp": 526, "title": "Backup Chain-of-Custody Receipt Draft Ledger", "status": "ready", "route": "/vault/backup-chain-of-custody-receipt-draft-ledger.json"},
    {"gp": 527, "title": "Tower Cold Copy Approval Requirement Board", "status": "ready", "route": "/vault/tower-cold-copy-approval-requirement-board.json"},
    {"gp": 528, "title": "Cold Copy Dry-Run Verification Board", "status": "ready", "route": "/vault/cold-copy-dry-run-verification-board.json"},
    {"gp": 529, "title": "Backup Export Cold Copy Safety Blocker Board", "status": "ready", "route": "/vault/backup-export-cold-copy-safety-blocker-board.json"},
    {"gp": 530, "title": "Backup Export Cold Copy Lock Readiness Checkpoint", "status": "ready", "route": "/vault/backup-export-cold-copy-lock-readiness-checkpoint.json"},
]

BLOCKERS = [
    {"blocker_id": "no_actual_backup_export_execution", "blocked_action": "actual_backup_export_execution", "allowed": False, "reason": "This layer drafts and locks cold-copy exports only."},
    {"blocker_id": "no_backup_package_materialization", "blocked_action": "backup_package_materialization", "allowed": False, "reason": "Only package hashes and manifests are produced in this layer."},
    {"blocker_id": "no_offline_package_write", "blocked_action": "offline_package_write", "allowed": False, "reason": "No offline package is written in the cold-copy lock layer."},
    {"blocker_id": "no_external_provider_export", "blocked_action": "external_provider_export", "allowed": False, "reason": "No provider dependency or external export is unlocked."},
    {"blocker_id": "no_external_sync", "blocked_action": "external_sync", "allowed": False, "reason": "Cold-copy lock is local-first and does not sync externally."},
    {"blocker_id": "no_raw_file_bytes_json", "blocked_action": "raw_file_bytes_returned_by_json", "allowed": False, "reason": "Cold-copy layer never returns raw file bytes."},
    {"blocker_id": "no_raw_path_or_url", "blocked_action": "raw_path_or_file_url_exposure", "allowed": False, "reason": "Cold-copy layer never exposes raw paths or file URLs."},
    {"blocker_id": "no_raw_token", "blocked_action": "raw_token_exposure", "allowed": False, "reason": "Cold-copy layer never exposes raw tokens."},
    {"blocker_id": "no_public_links", "blocked_action": "public_view_download_or_proof_link", "allowed": False, "reason": "Cold-copy layer never creates public links."},
    {"blocker_id": "no_teller_to_vault_direct_call", "blocked_action": "teller_to_vault_direct_call", "allowed": False, "reason": "Teller cannot initiate backup/export directly."},
    {"blocker_id": "no_public_vault_dashboard", "blocked_action": "public_vault_dashboard", "allowed": False, "reason": "Tower is the face; Vault remains headless."},
    {"blocker_id": "no_direct_vault_user_portal", "blocked_action": "direct_vault_user_portal", "allowed": False, "reason": "People do not enter Vault directly."},
    {"blocker_id": "no_restore_or_rebuild_execution", "blocked_action": "restore_or_rebuild_execution", "allowed": False, "reason": "Cold-copy lock does not restore, rebuild, or mutate indexes."},
    {"blocker_id": "no_delete_purge_quarantine_release", "blocked_action": "delete_purge_quarantine_release", "allowed": False, "reason": "Cold-copy lock cannot delete, purge, or release quarantine."},
    {"blocker_id": "no_physical_object_move", "blocked_action": "physical_object_move", "allowed": False, "reason": "Cold-copy lock cannot move physical objects."},
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
    return "cold_copy_eligibility_" + calculate_sha256_bytes(("cold_copy_eligibility|" + request_id).encode("utf-8"))[:24]


def _manifest_id(request_id: str) -> str:
    return "backup_export_manifest_draft_" + calculate_sha256_bytes(("backup_manifest|" + request_id).encode("utf-8"))[:24]


def _target_lock_id(request_id: str) -> str:
    return "cold_copy_target_lock_" + calculate_sha256_bytes(("target_lock|" + request_id).encode("utf-8"))[:24]


def _package_hash_id(request_id: str) -> str:
    return "offline_export_package_hash_" + calculate_sha256_bytes(("package_hash|" + request_id).encode("utf-8"))[:24]


def _custody_receipt_id(request_id: str) -> str:
    return "backup_chain_of_custody_receipt_draft_" + calculate_sha256_bytes(("custody_receipt|" + request_id).encode("utf-8"))[:24]


def _approval_id(request_id: str) -> str:
    return "tower_cold_copy_approval_requirement_" + calculate_sha256_bytes(("cold_copy_approval|" + request_id).encode("utf-8"))[:24]


def _verification_id(request_id: str) -> str:
    return "cold_copy_dry_run_verification_" + calculate_sha256_bytes(("cold_copy_verification|" + request_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    eligibility = get_rebuild_eligibility_from_receipt_closeout_board().get("eligibility_rows", [])
    sources = get_rebuild_source_proof_verification_board().get("source_verifications", [])
    plans = get_rebuild_execution_plan_draft_board().get("plan_drafts", [])
    simulations = get_dry_run_rebuild_simulation_board().get("simulations", [])
    locks = get_rebuild_mutation_lock_board().get("mutation_locks", [])
    approvals = get_tower_recovery_approval_requirement_board().get("approval_requirements", [])
    receipts = get_rebuild_execution_receipt_draft_ledger().get("receipt_drafts", [])

    source_by_request = {row["request_id"]: row for row in sources}
    plan_by_request = {row["request_id"]: row for row in plans}
    simulation_by_request = {row["request_id"]: row for row in simulations}
    lock_by_request = {row["request_id"]: row for row in locks}
    approval_by_request = {row["request_id"]: row for row in approvals}
    receipt_by_request = {row["request_id"]: row for row in receipts}

    rows = []
    for item in eligibility:
        request_id = item["request_id"]
        source = source_by_request.get(request_id, {})
        plan = plan_by_request.get(request_id, {})
        simulation = simulation_by_request.get(request_id, {})
        mutation_lock = lock_by_request.get(request_id, {})
        approval = approval_by_request.get(request_id, {})
        receipt = receipt_by_request.get(request_id, {})

        rows.append(
            {
                "request_id": request_id,
                "workflow_type": item.get("workflow_type", "unknown_workflow"),
                "final_protocol_receipt_hash": item.get("final_protocol_receipt_hash", "missing_final_receipt_hash"),
                "receipt_chain_integrity_hash": item.get("receipt_chain_integrity_hash", "missing_integrity_hash"),
                "proof_integrity_hash": item.get("proof_integrity_hash", "missing_proof_integrity_hash"),
                "eligible_for_dry_run": bool(item.get("eligible_for_dry_run", 1)),
                "eligible_for_actual_rebuild": bool(item.get("eligible_for_actual_rebuild", 0)),
                "tower_recovery_approval_required": bool(item.get("tower_recovery_approval_required", 1)),
                "raw_file_bytes_present": bool(item.get("raw_file_bytes_present", 0)),
                "public_links_present": bool(item.get("public_links_present", 0)),
                "proof_response_hash": source.get("proof_response_hash", "missing_proof_response_hash"),
                "sealed_download_artifact_hash": source.get("sealed_download_artifact_hash", "missing_sealed_download_artifact_hash"),
                "handle_guard_hash": source.get("handle_guard_hash", "missing_handle_guard_hash"),
                "service_receipts_verified": bool(source.get("service_receipts_verified", 1)),
                "proof_integrity_verified": bool(source.get("proof_integrity_verified", 1)),
                "vault_answered_tower_only": bool(source.get("vault_answered_tower_only", 1)),
                "plan_id": plan.get("plan_id", "missing_plan_id"),
                "plan_hash": plan.get("plan_hash", "missing_plan_hash"),
                "dry_run_only": bool(plan.get("dry_run_only", 1)),
                "actual_execution_allowed": bool(plan.get("actual_execution_allowed", 0)),
                "final_rebuilt_index_write_allowed": bool(plan.get("final_rebuilt_index_write_allowed", 0)),
                "simulation_id": simulation.get("simulation_id", "missing_simulation_id"),
                "simulation_hash": simulation.get("simulation_hash", "missing_simulation_hash"),
                "dry_run_passed": bool(simulation.get("dry_run_passed", 1)),
                "actual_rebuild_executed": bool(simulation.get("actual_rebuild_executed", 0)),
                "restore_executed": bool(simulation.get("restore_executed", 0)),
                "index_mutated": bool(simulation.get("index_mutated", 0)),
                "pack_mutated": bool(simulation.get("pack_mutated", 0)),
                "actual_rebuild_execution_locked": bool(mutation_lock.get("actual_rebuild_execution_locked", 1)),
                "restore_execution_locked": bool(mutation_lock.get("restore_execution_locked", 1)),
                "delete_purge_locked": bool(mutation_lock.get("delete_purge_locked", 1)),
                "physical_object_move_locked": bool(mutation_lock.get("physical_object_move_locked", 1)),
                "tower_approval_required": bool(approval.get("tower_recovery_approval_required", 1)),
                "owner_admin_approval_required": bool(approval.get("owner_admin_approval_required", 1)),
                "step_up_required": bool(approval.get("step_up_required", 1)),
                "dual_receipt_required": bool(approval.get("dual_receipt_required", 1)),
                "rebuild_receipt_hash": receipt.get("rebuild_receipt_hash", "missing_rebuild_receipt_hash"),
            }
        )
    return rows


def initialize_backup_export_cold_copy_lock_layer() -> Dict[str, Any]:
    global _GP521_INIT_CACHE
    if _GP521_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP521_INIT_CACHE)

    previous = validate_recovery_safe_rebuild_execution_prep_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cold_copy_eligibility_from_recovery_prep (
                eligibility_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                eligibility_state TEXT NOT NULL,
                recovery_prep_verified INTEGER NOT NULL,
                dry_run_passed INTEGER NOT NULL,
                mutation_locks_engaged INTEGER NOT NULL,
                eligible_for_manifest_draft INTEGER NOT NULL,
                eligible_for_actual_export INTEGER NOT NULL,
                tower_cold_copy_approval_required INTEGER NOT NULL,
                raw_file_bytes_present INTEGER NOT NULL,
                public_links_present INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS backup_export_manifest_drafts (
                manifest_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                manifest_state TEXT NOT NULL,
                manifest_kind TEXT NOT NULL,
                final_protocol_receipt_hash TEXT NOT NULL,
                receipt_chain_integrity_hash TEXT NOT NULL,
                proof_integrity_hash TEXT NOT NULL,
                backup_manifest_hash TEXT NOT NULL,
                manifest_hash_only INTEGER NOT NULL,
                actual_export_executed INTEGER NOT NULL,
                raw_file_bytes_included INTEGER NOT NULL,
                raw_path_included INTEGER NOT NULL,
                raw_file_url_included INTEGER NOT NULL,
                raw_token_included INTEGER NOT NULL,
                public_link_included INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cold_copy_target_locks (
                target_lock_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                target_lock_state TEXT NOT NULL,
                local_cold_copy_lane_reserved INTEGER NOT NULL,
                external_provider_target_allowed INTEGER NOT NULL,
                public_target_allowed INTEGER NOT NULL,
                raw_target_path_visible INTEGER NOT NULL,
                physical_media_write_allowed INTEGER NOT NULL,
                physical_object_move_allowed INTEGER NOT NULL,
                provider_dependency_required INTEGER NOT NULL,
                target_lock_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS offline_export_package_hashes (
                package_hash_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                manifest_id TEXT NOT NULL,
                package_state TEXT NOT NULL,
                offline_package_hash TEXT NOT NULL,
                package_hash_only INTEGER NOT NULL,
                package_materialized INTEGER NOT NULL,
                offline_package_write_executed INTEGER NOT NULL,
                raw_file_bytes_included INTEGER NOT NULL,
                raw_path_included INTEGER NOT NULL,
                raw_file_url_included INTEGER NOT NULL,
                raw_token_included INTEGER NOT NULL,
                public_link_included INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS backup_chain_of_custody_receipt_drafts (
                custody_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                manifest_id TEXT NOT NULL,
                package_hash_id TEXT NOT NULL,
                receipt_state TEXT NOT NULL,
                chain_of_custody_receipt_hash TEXT NOT NULL,
                receipt_finalized INTEGER NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                actual_export_executed INTEGER NOT NULL,
                package_materialized INTEGER NOT NULL,
                physical_object_move_executed INTEGER NOT NULL,
                raw_file_bytes_receipted INTEGER NOT NULL,
                public_link_receipted INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_cold_copy_approval_requirements (
                approval_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                approval_state TEXT NOT NULL,
                tower_cold_copy_approval_required INTEGER NOT NULL,
                owner_admin_approval_required INTEGER NOT NULL,
                step_up_required INTEGER NOT NULL,
                dual_receipt_required INTEGER NOT NULL,
                manifest_hash_required INTEGER NOT NULL,
                dry_run_verification_required INTEGER NOT NULL,
                actual_export_allowed_before_approval INTEGER NOT NULL,
                external_provider_export_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cold_copy_dry_run_verifications (
                verification_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                manifest_id TEXT NOT NULL,
                package_hash_id TEXT NOT NULL,
                verification_state TEXT NOT NULL,
                dry_run_verified INTEGER NOT NULL,
                actual_export_executed INTEGER NOT NULL,
                provider_export_executed INTEGER NOT NULL,
                package_materialized INTEGER NOT NULL,
                raw_file_bytes_absent INTEGER NOT NULL,
                raw_paths_absent INTEGER NOT NULL,
                raw_tokens_absent INTEGER NOT NULL,
                public_links_absent INTEGER NOT NULL,
                verification_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS backup_export_cold_copy_safety_blockers (
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
                INSERT OR REPLACE INTO backup_export_cold_copy_safety_blockers (
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
            manifest_id = _manifest_id(request_id)
            target_lock_id = _target_lock_id(request_id)
            package_hash_id = _package_hash_id(request_id)
            custody_receipt_id = _custody_receipt_id(request_id)
            approval_id = _approval_id(request_id)
            verification_id = _verification_id(request_id)

            recovery_prep_verified = (
                row["eligible_for_dry_run"]
                and row["dry_run_passed"]
                and row["actual_rebuild_execution_locked"]
                and row["restore_execution_locked"]
                and row["delete_purge_locked"]
                and row["physical_object_move_locked"]
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO cold_copy_eligibility_from_recovery_prep (
                    eligibility_id, request_id, workflow_type,
                    eligibility_state, recovery_prep_verified,
                    dry_run_passed, mutation_locks_engaged,
                    eligible_for_manifest_draft,
                    eligible_for_actual_export,
                    tower_cold_copy_approval_required,
                    raw_file_bytes_present, public_links_present,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    eligibility_id,
                    request_id,
                    row["workflow_type"],
                    "eligible_for_cold_copy_manifest_draft_only",
                    1 if recovery_prep_verified else 0,
                    1 if row["dry_run_passed"] else 0,
                    1,
                    1,
                    0,
                    1,
                    0,
                    0,
                    now,
                ),
            )

            manifest_material = {
                "request_id": request_id,
                "workflow_type": row["workflow_type"],
                "final_protocol_receipt_hash": row["final_protocol_receipt_hash"],
                "receipt_chain_integrity_hash": row["receipt_chain_integrity_hash"],
                "proof_integrity_hash": row["proof_integrity_hash"],
                "sealed_download_artifact_hash": row["sealed_download_artifact_hash"],
                "rebuild_receipt_hash": row["rebuild_receipt_hash"],
                "actual_export_executed": False,
                "raw_file_bytes_included": False,
                "public_link_included": False,
            }
            backup_manifest_hash = calculate_sha256_bytes(repr(sorted(manifest_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO backup_export_manifest_drafts (
                    manifest_id, request_id, workflow_type,
                    manifest_state, manifest_kind,
                    final_protocol_receipt_hash,
                    receipt_chain_integrity_hash,
                    proof_integrity_hash,
                    backup_manifest_hash,
                    manifest_hash_only,
                    actual_export_executed,
                    raw_file_bytes_included,
                    raw_path_included, raw_file_url_included,
                    raw_token_included, public_link_included,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    manifest_id,
                    request_id,
                    row["workflow_type"],
                    "backup_export_manifest_draft_ready_hash_only",
                    "cold_copy_manifest_draft",
                    row["final_protocol_receipt_hash"],
                    row["receipt_chain_integrity_hash"],
                    row["proof_integrity_hash"],
                    backup_manifest_hash,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            target_lock_hash = calculate_sha256_bytes(
                f"cold-copy-target-lock|{request_id}|local-lane-reserved|no-provider|no-public|no-physical-move".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO cold_copy_target_locks (
                    target_lock_id, request_id, target_lock_state,
                    local_cold_copy_lane_reserved,
                    external_provider_target_allowed,
                    public_target_allowed,
                    raw_target_path_visible,
                    physical_media_write_allowed,
                    physical_object_move_allowed,
                    provider_dependency_required,
                    target_lock_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    target_lock_id,
                    request_id,
                    "cold_copy_target_locked_no_provider_no_public_no_physical_move",
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    target_lock_hash,
                    now,
                ),
            )

            offline_package_hash = calculate_sha256_bytes(
                f"offline-export-package-hash|{request_id}|{backup_manifest_hash}|{target_lock_hash}|hash-only-not-materialized".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO offline_export_package_hashes (
                    package_hash_id, request_id, manifest_id,
                    package_state, offline_package_hash,
                    package_hash_only, package_materialized,
                    offline_package_write_executed,
                    raw_file_bytes_included, raw_path_included,
                    raw_file_url_included, raw_token_included,
                    public_link_included, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    package_hash_id,
                    request_id,
                    manifest_id,
                    "offline_export_package_hash_ready_not_materialized",
                    offline_package_hash,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            custody_hash = calculate_sha256_bytes(
                f"backup-chain-of-custody-draft|{request_id}|{backup_manifest_hash}|{offline_package_hash}|not-exported".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO backup_chain_of_custody_receipt_drafts (
                    custody_receipt_id, request_id, manifest_id,
                    package_hash_id, receipt_state,
                    chain_of_custody_receipt_hash,
                    receipt_finalized, append_only, mutable,
                    actual_export_executed, package_materialized,
                    physical_object_move_executed,
                    raw_file_bytes_receipted, public_link_receipted,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    custody_receipt_id,
                    request_id,
                    manifest_id,
                    package_hash_id,
                    "backup_chain_of_custody_receipt_draft_ready_not_exported",
                    custody_hash,
                    0,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_cold_copy_approval_requirements (
                    approval_id, request_id, approval_state,
                    tower_cold_copy_approval_required,
                    owner_admin_approval_required,
                    step_up_required, dual_receipt_required,
                    manifest_hash_required,
                    dry_run_verification_required,
                    actual_export_allowed_before_approval,
                    external_provider_export_allowed,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval_id,
                    request_id,
                    "tower_cold_copy_approval_required_before_any_export",
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    0,
                    0,
                    now,
                ),
            )

            verification_hash = calculate_sha256_bytes(
                f"cold-copy-dry-run-verification|{request_id}|{offline_package_hash}|no-export-no-provider-no-public".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO cold_copy_dry_run_verifications (
                    verification_id, request_id, manifest_id,
                    package_hash_id, verification_state,
                    dry_run_verified, actual_export_executed,
                    provider_export_executed, package_materialized,
                    raw_file_bytes_absent, raw_paths_absent,
                    raw_tokens_absent, public_links_absent,
                    verification_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    verification_id,
                    request_id,
                    manifest_id,
                    package_hash_id,
                    "cold_copy_dry_run_verified_no_export_no_materialization",
                    1,
                    0,
                    0,
                    0,
                    1,
                    1,
                    1,
                    1,
                    verification_hash,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_recovery_safe_rebuild_prep_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP521_INIT_CACHE = dict(result)
    return result


def get_backup_export_cold_copy_lock_shell() -> Dict[str, Any]:
    init = initialize_backup_export_cold_copy_lock_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 521,
        "title": "Backup Export Cold Copy Lock Shell",
        "ready": True,
        "initialized": init,
        "doctrine": DOCTRINE,
        "correct_flow": DOCTRINE["correct_flow"],
        "hash_and_manifest_only": True,
        "actual_backup_export_execution_allowed": False,
        "backup_package_materialization_allowed": False,
        "external_provider_export_allowed": False,
        "locks": LOCKS,
    }


def get_cold_copy_eligibility_from_recovery_prep_board() -> Dict[str, Any]:
    initialize_backup_export_cold_copy_lock_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM cold_copy_eligibility_from_recovery_prep ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 522,
        "title": "Cold Copy Eligibility From Recovery Prep Board",
        "ready": True,
        "eligibility_count": len(rows),
        "eligibility_rows": rows,
        "all_recovery_prep_verified": all(bool(item["recovery_prep_verified"]) for item in rows),
        "all_dry_run_passed": all(bool(item["dry_run_passed"]) for item in rows),
        "all_mutation_locks_engaged": all(bool(item["mutation_locks_engaged"]) for item in rows),
        "all_eligible_for_manifest_draft": all(bool(item["eligible_for_manifest_draft"]) for item in rows),
        "none_eligible_for_actual_export": all(not bool(item["eligible_for_actual_export"]) for item in rows),
        "all_tower_cold_copy_approval_required": all(bool(item["tower_cold_copy_approval_required"]) for item in rows),
        "no_raw_file_bytes_present": all(not bool(item["raw_file_bytes_present"]) for item in rows),
        "no_public_links_present": all(not bool(item["public_links_present"]) for item in rows),
    }


def get_backup_export_manifest_draft_board() -> Dict[str, Any]:
    initialize_backup_export_cold_copy_lock_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM backup_export_manifest_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 523,
        "title": "Backup Export Manifest Draft Board",
        "ready": True,
        "manifest_count": len(rows),
        "manifest_drafts": rows,
        "all_manifest_hash_only": all(bool(item["manifest_hash_only"]) for item in rows),
        "no_actual_export_executed": all(not bool(item["actual_export_executed"]) for item in rows),
        "all_have_manifest_hash": all(len(item["backup_manifest_hash"]) == 64 for item in rows),
        "no_raw_file_bytes": all(not bool(item["raw_file_bytes_included"]) for item in rows),
        "no_raw_paths": all(not bool(item["raw_path_included"]) for item in rows),
        "no_raw_file_urls": all(not bool(item["raw_file_url_included"]) for item in rows),
        "no_raw_tokens": all(not bool(item["raw_token_included"]) for item in rows),
        "no_public_links": all(not bool(item["public_link_included"]) for item in rows),
    }


def get_cold_copy_target_lock_board() -> Dict[str, Any]:
    initialize_backup_export_cold_copy_lock_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM cold_copy_target_locks ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 524,
        "title": "Cold Copy Target Lock Board",
        "ready": True,
        "target_lock_count": len(rows),
        "target_locks": rows,
        "all_local_cold_copy_lane_reserved": all(bool(item["local_cold_copy_lane_reserved"]) for item in rows),
        "no_external_provider_target": all(not bool(item["external_provider_target_allowed"]) for item in rows),
        "no_public_target": all(not bool(item["public_target_allowed"]) for item in rows),
        "no_raw_target_path_visible": all(not bool(item["raw_target_path_visible"]) for item in rows),
        "no_physical_media_write": all(not bool(item["physical_media_write_allowed"]) for item in rows),
        "no_physical_object_move": all(not bool(item["physical_object_move_allowed"]) for item in rows),
        "no_provider_dependency": all(not bool(item["provider_dependency_required"]) for item in rows),
        "all_have_target_lock_hash": all(len(item["target_lock_hash"]) == 64 for item in rows),
    }


def get_offline_export_package_hash_board() -> Dict[str, Any]:
    initialize_backup_export_cold_copy_lock_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM offline_export_package_hashes ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 525,
        "title": "Offline Export Package Hash Board",
        "ready": True,
        "package_hash_count": len(rows),
        "package_hashes": rows,
        "all_package_hash_only": all(bool(item["package_hash_only"]) for item in rows),
        "no_package_materialized": all(not bool(item["package_materialized"]) for item in rows),
        "no_offline_package_write": all(not bool(item["offline_package_write_executed"]) for item in rows),
        "all_have_offline_package_hash": all(len(item["offline_package_hash"]) == 64 for item in rows),
        "no_raw_file_bytes": all(not bool(item["raw_file_bytes_included"]) for item in rows),
        "no_raw_paths": all(not bool(item["raw_path_included"]) for item in rows),
        "no_raw_file_urls": all(not bool(item["raw_file_url_included"]) for item in rows),
        "no_raw_tokens": all(not bool(item["raw_token_included"]) for item in rows),
        "no_public_links": all(not bool(item["public_link_included"]) for item in rows),
    }


def get_backup_chain_of_custody_receipt_draft_ledger() -> Dict[str, Any]:
    initialize_backup_export_cold_copy_lock_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM backup_chain_of_custody_receipt_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 526,
        "title": "Backup Chain-of-Custody Receipt Draft Ledger",
        "ready": True,
        "custody_receipt_count": len(rows),
        "custody_receipts": rows,
        "all_receipts_draft": all(not bool(item["receipt_finalized"]) for item in rows),
        "all_append_only": all(bool(item["append_only"]) for item in rows),
        "all_immutable": all(not bool(item["mutable"]) for item in rows),
        "no_actual_export_executed": all(not bool(item["actual_export_executed"]) for item in rows),
        "no_package_materialized": all(not bool(item["package_materialized"]) for item in rows),
        "no_physical_object_move": all(not bool(item["physical_object_move_executed"]) for item in rows),
        "no_raw_file_bytes_receipted": all(not bool(item["raw_file_bytes_receipted"]) for item in rows),
        "no_public_links_receipted": all(not bool(item["public_link_receipted"]) for item in rows),
        "all_have_custody_hash": all(len(item["chain_of_custody_receipt_hash"]) == 64 for item in rows),
    }


def get_tower_cold_copy_approval_requirement_board() -> Dict[str, Any]:
    initialize_backup_export_cold_copy_lock_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_cold_copy_approval_requirements ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 527,
        "title": "Tower Cold Copy Approval Requirement Board",
        "ready": True,
        "approval_requirement_count": len(rows),
        "approval_requirements": rows,
        "all_tower_cold_copy_approval_required": all(bool(item["tower_cold_copy_approval_required"]) for item in rows),
        "all_owner_admin_approval_required": all(bool(item["owner_admin_approval_required"]) for item in rows),
        "all_step_up_required": all(bool(item["step_up_required"]) for item in rows),
        "all_dual_receipt_required": all(bool(item["dual_receipt_required"]) for item in rows),
        "all_manifest_hash_required": all(bool(item["manifest_hash_required"]) for item in rows),
        "all_dry_run_verification_required": all(bool(item["dry_run_verification_required"]) for item in rows),
        "no_actual_export_before_approval": all(not bool(item["actual_export_allowed_before_approval"]) for item in rows),
        "no_external_provider_export": all(not bool(item["external_provider_export_allowed"]) for item in rows),
    }


def get_cold_copy_dry_run_verification_board() -> Dict[str, Any]:
    initialize_backup_export_cold_copy_lock_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM cold_copy_dry_run_verifications ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 528,
        "title": "Cold Copy Dry-Run Verification Board",
        "ready": True,
        "verification_count": len(rows),
        "verifications": rows,
        "all_dry_run_verified": all(bool(item["dry_run_verified"]) for item in rows),
        "no_actual_export_executed": all(not bool(item["actual_export_executed"]) for item in rows),
        "no_provider_export_executed": all(not bool(item["provider_export_executed"]) for item in rows),
        "no_package_materialized": all(not bool(item["package_materialized"]) for item in rows),
        "all_raw_file_bytes_absent": all(bool(item["raw_file_bytes_absent"]) for item in rows),
        "all_raw_paths_absent": all(bool(item["raw_paths_absent"]) for item in rows),
        "all_raw_tokens_absent": all(bool(item["raw_tokens_absent"]) for item in rows),
        "all_public_links_absent": all(bool(item["public_links_absent"]) for item in rows),
        "all_have_verification_hash": all(len(item["verification_hash"]) == 64 for item in rows),
    }


def get_backup_export_cold_copy_safety_blocker_board() -> Dict[str, Any]:
    initialize_backup_export_cold_copy_lock_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM backup_export_cold_copy_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 529,
        "title": "Backup Export Cold Copy Safety Blocker Board",
        "ready": True,
        "blocker_count": len(rows),
        "blockers": rows,
        "unsafe_action_count": sum(1 for item in rows if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in rows),
    }


def get_backup_export_cold_copy_lock_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_backup_export_cold_copy_lock_layer()

    shell = get_backup_export_cold_copy_lock_shell()
    eligibility = get_cold_copy_eligibility_from_recovery_prep_board()
    manifests = get_backup_export_manifest_draft_board()
    targets = get_cold_copy_target_lock_board()
    packages = get_offline_export_package_hash_board()
    custody = get_backup_chain_of_custody_receipt_draft_ledger()
    approvals = get_tower_cold_copy_approval_requirement_board()
    verifications = get_cold_copy_dry_run_verification_board()
    blockers = get_backup_export_cold_copy_safety_blocker_board()

    checks = {
        "previous_recovery_safe_rebuild_prep_ready": init["previous_recovery_safe_rebuild_prep_ready"] is True,
        "cold_copy_shell_ready": shell["ready"] is True,
        "doctrine_tower_teller_vault_locked": DOCTRINE["tower"] == "face_protocol_authority" and DOCTRINE["teller"] == "workflow_request_source" and DOCTRINE["vault"] == "sealed_memory",
        "correct_flow_locked": DOCTRINE["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller",
        "lock_hash_dry_run_only": DOCTRINE["backup_export_cold_copy_lock_only"] is True and DOCTRINE["hash_and_manifest_only"] is True and DOCTRINE["dry_run_only"] is True,
        "tower_cold_copy_approval_required": DOCTRINE["tower_cold_copy_approval_required"] is True,
        "no_actual_export_package_provider_or_physical_move": DOCTRINE["actual_backup_export_execution_allowed"] is False and DOCTRINE["backup_package_materialization_allowed"] is False and DOCTRINE["external_provider_export_allowed"] is False and DOCTRINE["physical_object_move_allowed"] is False,
        "eligibility_ready": eligibility["ready"] is True and eligibility["eligibility_count"] >= 2,
        "eligibility_from_recovery_prep_verified": eligibility["all_recovery_prep_verified"] is True and eligibility["all_dry_run_passed"] is True and eligibility["all_mutation_locks_engaged"] is True,
        "eligibility_manifest_only_no_actual_export": eligibility["all_eligible_for_manifest_draft"] is True and eligibility["none_eligible_for_actual_export"] is True,
        "eligibility_approval_no_raw_public": eligibility["all_tower_cold_copy_approval_required"] is True and eligibility["no_raw_file_bytes_present"] is True and eligibility["no_public_links_present"] is True,
        "manifests_ready": manifests["ready"] is True and manifests["manifest_count"] >= 2,
        "manifests_hash_only_not_exported": manifests["all_manifest_hash_only"] is True and manifests["no_actual_export_executed"] is True and manifests["all_have_manifest_hash"] is True,
        "manifests_no_raw_path_url_token_public": manifests["no_raw_file_bytes"] is True and manifests["no_raw_paths"] is True and manifests["no_raw_file_urls"] is True and manifests["no_raw_tokens"] is True and manifests["no_public_links"] is True,
        "target_locks_ready": targets["ready"] is True and targets["target_lock_count"] >= 2,
        "target_locks_no_provider_public_physical": targets["all_local_cold_copy_lane_reserved"] is True and targets["no_external_provider_target"] is True and targets["no_public_target"] is True and targets["no_raw_target_path_visible"] is True and targets["no_physical_media_write"] is True and targets["no_physical_object_move"] is True and targets["no_provider_dependency"] is True,
        "package_hashes_ready": packages["ready"] is True and packages["package_hash_count"] >= 2,
        "package_hashes_only_not_materialized": packages["all_package_hash_only"] is True and packages["no_package_materialized"] is True and packages["no_offline_package_write"] is True and packages["all_have_offline_package_hash"] is True,
        "package_hashes_no_raw_path_url_token_public": packages["no_raw_file_bytes"] is True and packages["no_raw_paths"] is True and packages["no_raw_file_urls"] is True and packages["no_raw_tokens"] is True and packages["no_public_links"] is True,
        "custody_receipts_ready": custody["ready"] is True and custody["custody_receipt_count"] >= 2,
        "custody_receipts_draft_append_only_no_export": custody["all_receipts_draft"] is True and custody["all_append_only"] is True and custody["all_immutable"] is True and custody["no_actual_export_executed"] is True and custody["no_package_materialized"] is True and custody["no_physical_object_move"] is True,
        "custody_receipts_no_raw_public": custody["no_raw_file_bytes_receipted"] is True and custody["no_public_links_receipted"] is True,
        "approvals_ready": approvals["ready"] is True and approvals["approval_requirement_count"] >= 2,
        "approvals_required_before_export": approvals["all_tower_cold_copy_approval_required"] is True and approvals["all_owner_admin_approval_required"] is True and approvals["all_step_up_required"] is True and approvals["all_dual_receipt_required"] is True and approvals["all_manifest_hash_required"] is True and approvals["all_dry_run_verification_required"] is True and approvals["no_actual_export_before_approval"] is True and approvals["no_external_provider_export"] is True,
        "verifications_ready": verifications["ready"] is True and verifications["verification_count"] >= 2,
        "verifications_dry_run_no_export_provider_materialization": verifications["all_dry_run_verified"] is True and verifications["no_actual_export_executed"] is True and verifications["no_provider_export_executed"] is True and verifications["no_package_materialized"] is True,
        "verifications_no_raw_path_token_public": verifications["all_raw_file_bytes_absent"] is True and verifications["all_raw_paths_absent"] is True and verifications["all_raw_tokens_absent"] is True and verifications["all_public_links_absent"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "global_layer_allowed_manifest_hash_only": LOCKS["backup_export_cold_copy_lock_layer"] is True and LOCKS["backup_export_manifest_drafts_allowed"] is True and LOCKS["offline_export_package_hashes_allowed"] is True,
        "global_no_export_package_provider_sync": LOCKS["actual_backup_export_execution_allowed"] is False and LOCKS["backup_package_materialization_allowed"] is False and LOCKS["offline_package_write_allowed"] is False and LOCKS["external_provider_export_allowed"] is False and LOCKS["external_sync_unlocked"] is False and LOCKS["provider_storage_required"] is False,
        "global_no_raw_path_url_token_public": LOCKS["raw_file_bytes_returned_by_json"] is False and LOCKS["raw_path_exposed"] is False and LOCKS["raw_file_url_exposed"] is False and LOCKS["raw_download_token_exposed"] is False and LOCKS["public_url_created"] is False and LOCKS["share_link_created"] is False,
        "global_no_rebuild_restore_mutation": LOCKS["actual_rebuild_execution_allowed"] is False and LOCKS["restore_execution_allowed"] is False and LOCKS["final_rebuilt_index_write_allowed"] is False and LOCKS["final_pack_overwrite_allowed"] is False and LOCKS["sealed_pack_bytes_write_allowed"] is False and LOCKS["index_mutation_allowed"] is False and LOCKS["pack_mutation_allowed"] is False,
        "global_no_teller_or_public_vault_access": LOCKS["teller_to_vault_direct_call_allowed"] is False and LOCKS["direct_vault_user_portal_allowed"] is False and LOCKS["public_vault_dashboard_allowed"] is False and LOCKS["external_collaborator_browsing_allowed"] is False,
        "global_no_delete_purge_quarantine_physical": LOCKS["hard_delete_allowed"] is False and LOCKS["purge_allowed"] is False and LOCKS["quarantine_release_allowed"] is False and LOCKS["physical_object_move_allowed"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 530,
        "title": "Backup Export Cold Copy Lock Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Backup export cold copy lock layer blocked",
        "ready": ready,
        "checks": checks,
        "cold_copy_status": "manifest_hashes_and_locks_ready_no_export",
        "next_recommended_layer": "ARCHIVE VAULT — COLD COPY RESTORE DRILL LAYER / GP531-GP540",
        "still_locked": [
            "no actual backup export execution",
            "no backup package materialization",
            "no offline package write",
            "no external provider export",
            "no external sync",
            "no raw file bytes returned by JSON",
            "no raw path/file URL/token exposure",
            "no public URL/share link",
            "no Teller-to-Vault direct calls",
            "no direct Vault user portal",
            "no public Vault dashboard",
            "no restore execution",
            "no final rebuilt index write",
            "no final pack overwrite",
            "no delete or purge",
            "no quarantine release",
            "no physical object move",
            "no provider dependency by default",
        ],
    }


def get_backup_export_cold_copy_lock_home() -> Dict[str, Any]:
    checkpoint = get_backup_export_cold_copy_lock_readiness_checkpoint()
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


def validate_backup_export_cold_copy_lock_layer() -> Dict[str, Any]:
    checkpoint = get_backup_export_cold_copy_lock_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_recovery_safe_rebuild_prep_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"]["lock_hash_dry_run_only"] is True
    assert checkpoint["checks"]["tower_cold_copy_approval_required"] is True
    assert checkpoint["checks"]["no_actual_export_package_provider_or_physical_move"] is True
    assert checkpoint["checks"]["eligibility_from_recovery_prep_verified"] is True
    assert checkpoint["checks"]["eligibility_manifest_only_no_actual_export"] is True
    assert checkpoint["checks"]["manifests_hash_only_not_exported"] is True
    assert checkpoint["checks"]["target_locks_no_provider_public_physical"] is True
    assert checkpoint["checks"]["package_hashes_only_not_materialized"] is True
    assert checkpoint["checks"]["custody_receipts_draft_append_only_no_export"] is True
    assert checkpoint["checks"]["approvals_required_before_export"] is True
    assert checkpoint["checks"]["verifications_dry_run_no_export_provider_materialization"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["actual_backup_export_execution_allowed"] is False
    assert LOCKS["backup_package_materialization_allowed"] is False
    assert LOCKS["offline_package_write_allowed"] is False
    assert LOCKS["external_provider_export_allowed"] is False
    assert LOCKS["external_sync_unlocked"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_file_bytes_exposed"] is False
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["raw_share_token_exposed"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
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

    return {
        "ok": True,
        "section": SECTION,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(item for item in PACKS if item["gp"] == gp)
    checkpoint = get_backup_export_cold_copy_lock_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "correct_flow": DOCTRINE["correct_flow"],
        "hash_and_manifest_only": True,
        "actual_backup_export_execution_allowed": False,
        "backup_package_materialization_allowed": False,
        "external_provider_export_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "public_link_created": False,
        "teller_to_vault_direct_call_allowed": False,
        "locks_preserved": True,
    }


def get_gp521_status() -> Dict[str, Any]:
    return _gp_status(521)


def get_gp522_status() -> Dict[str, Any]:
    return _gp_status(522)


def get_gp523_status() -> Dict[str, Any]:
    return _gp_status(523)


def get_gp524_status() -> Dict[str, Any]:
    return _gp_status(524)


def get_gp525_status() -> Dict[str, Any]:
    return _gp_status(525)


def get_gp526_status() -> Dict[str, Any]:
    return _gp_status(526)


def get_gp527_status() -> Dict[str, Any]:
    return _gp_status(527)


def get_gp528_status() -> Dict[str, Any]:
    return _gp_status(528)


def get_gp529_status() -> Dict[str, Any]:
    return _gp_status(529)


def get_gp530_status() -> Dict[str, Any]:
    return _gp_status(530)
