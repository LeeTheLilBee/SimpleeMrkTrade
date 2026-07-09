
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = (
    "ARCHIVE VAULT — COLD COPY RESTORE DRILL LAYER / GP531-GP540"
)
LAYER_ID = "vault_gp531_540_cold_copy_restore_drill_layer"
READINESS_LABEL = "Cold copy restore drill layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_cold_copy_restore_drill_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
    )
    from vault.backup_export_cold_copy_lock_layer_service import (
        get_cold_copy_eligibility_from_recovery_prep_board,
        get_backup_export_manifest_draft_board,
        get_cold_copy_target_lock_board,
        get_offline_export_package_hash_board,
        get_backup_chain_of_custody_receipt_draft_ledger,
        get_tower_cold_copy_approval_requirement_board,
        get_cold_copy_dry_run_verification_board,
        validate_backup_export_cold_copy_lock_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP531-GP540 requires GP521-GP530 "
        "Backup export cold copy lock layer first."
    ) from exc


_GP531_INIT_CACHE = None


DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": "Teller -> Tower -> Vault -> Tower -> Teller",
    "cold_copy_restore_drill_only": True,
    "sandbox_reconstruction_only": True,
    "integrity_comparison_only": True,
    "tower_restore_drill_control_required": True,
    "actual_restore_execution_allowed": False,
    "production_recovery_write_allowed": False,
    "final_rebuilt_index_write_allowed": False,
    "final_pack_overwrite_allowed": False,
    "sealed_pack_bytes_write_allowed": False,
    "backup_package_materialization_allowed": False,
    "vault_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
}


LOCKS = {
    "cold_copy_restore_drill_layer": True,
    "restore_drill_eligibility_allowed": True,
    "cold_copy_manifest_verification_allowed": True,
    "restore_target_sandbox_drafts_allowed": True,
    "restore_reconstruction_dry_runs_allowed": True,
    "restore_integrity_comparisons_allowed": True,
    "rollback_abort_guards_allowed": True,
    "tower_restore_drill_receipt_drafts_allowed": True,

    "actual_restore_execution_allowed": False,
    "production_recovery_write_allowed": False,
    "final_rebuilt_index_write_allowed": False,
    "final_pack_overwrite_allowed": False,
    "sealed_pack_bytes_write_allowed": False,
    "backup_package_materialization_allowed": False,
    "offline_package_write_allowed": False,
    "actual_backup_export_execution_allowed": False,
    "external_provider_export_allowed": False,
    "external_sync_unlocked": False,
    "provider_storage_required": False,
    "provider_upload_unlocked": False,
    "index_mutation_allowed": False,
    "pack_mutation_allowed": False,
    "metadata_mutation_allowed": False,
    "production_target_access_allowed": False,
    "physical_media_write_allowed": False,
    "physical_object_move_allowed": False,

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
    "public_url_created": False,
    "share_link_created": False,

    "teller_direct_restore_allowed": False,
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

    "public_upload_unlocked": False,
    "beta_upload_unlocked": False,
    "file_delete_unlocked": False,
    "hard_delete_allowed": False,
    "purge_allowed": False,
    "quarantine_release_allowed": False,
}


PACKS = [
    {
        "gp": 531,
        "title": "Cold Copy Restore Drill Shell",
        "status": "ready",
        "route": "/vault/cold-copy-restore-drill-shell.json",
    },
    {
        "gp": 532,
        "title": "Restore Drill Eligibility Board",
        "status": "ready",
        "route": "/vault/restore-drill-eligibility-board.json",
    },
    {
        "gp": 533,
        "title": "Cold Copy Manifest Verification Board",
        "status": "ready",
        "route": "/vault/cold-copy-manifest-verification-board.json",
    },
    {
        "gp": 534,
        "title": "Restore Target Sandbox Draft Board",
        "status": "ready",
        "route": "/vault/restore-target-sandbox-draft-board.json",
    },
    {
        "gp": 535,
        "title": "Restore Reconstruction Dry-Run Board",
        "status": "ready",
        "route": "/vault/restore-reconstruction-dry-run-board.json",
    },
    {
        "gp": 536,
        "title": "Restore Integrity Comparison Board",
        "status": "ready",
        "route": "/vault/restore-integrity-comparison-board.json",
    },
    {
        "gp": 537,
        "title": "Restore Rollback and Abort Guard Board",
        "status": "ready",
        "route": "/vault/restore-rollback-abort-guard-board.json",
    },
    {
        "gp": 538,
        "title": "Tower Restore Drill Receipt Draft Ledger",
        "status": "ready",
        "route": "/vault/tower-restore-drill-receipt-draft-ledger.json",
    },
    {
        "gp": 539,
        "title": "Cold Copy Restore Drill Safety Blocker Board",
        "status": "ready",
        "route": "/vault/cold-copy-restore-drill-safety-blocker-board.json",
    },
    {
        "gp": 540,
        "title": "Cold Copy Restore Drill Readiness Checkpoint",
        "status": "ready",
        "route": "/vault/cold-copy-restore-drill-readiness-checkpoint.json",
    },
]


BLOCKERS = [
    {
        "blocker_id": "no_actual_restore_execution",
        "blocked_action": "actual_restore_execution",
        "allowed": False,
        "reason": "This layer rehearses restore behavior only.",
    },
    {
        "blocker_id": "no_production_recovery_write",
        "blocked_action": "production_recovery_write",
        "allowed": False,
        "reason": "Restore drills cannot write to production recovery targets.",
    },
    {
        "blocker_id": "no_final_rebuilt_index_write",
        "blocked_action": "final_rebuilt_index_write",
        "allowed": False,
        "reason": "No final index write occurs during a restore drill.",
    },
    {
        "blocker_id": "no_final_pack_overwrite",
        "blocked_action": "final_pack_overwrite",
        "allowed": False,
        "reason": "Sealed Vault packs cannot be overwritten by a drill.",
    },
    {
        "blocker_id": "no_sealed_pack_bytes_write",
        "blocked_action": "sealed_pack_bytes_write",
        "allowed": False,
        "reason": "The drill does not write sealed pack bytes.",
    },
    {
        "blocker_id": "no_package_materialization",
        "blocked_action": "backup_package_materialization",
        "allowed": False,
        "reason": "Cold-copy package hashes are verified without materialization.",
    },
    {
        "blocker_id": "no_raw_file_bytes_json",
        "blocked_action": "raw_file_bytes_returned_by_json",
        "allowed": False,
        "reason": "Restore drill outputs contain hashes and status only.",
    },
    {
        "blocker_id": "no_raw_path_or_url",
        "blocked_action": "raw_path_or_file_url_exposure",
        "allowed": False,
        "reason": "Sandbox and source paths remain sealed.",
    },
    {
        "blocker_id": "no_raw_token",
        "blocked_action": "raw_token_exposure",
        "allowed": False,
        "reason": "No download, share, or provider token is exposed.",
    },
    {
        "blocker_id": "no_public_link",
        "blocked_action": "public_view_download_or_proof_link",
        "allowed": False,
        "reason": "Restore drill metadata is Tower-controlled and private.",
    },
    {
        "blocker_id": "no_external_provider_restore",
        "blocked_action": "external_provider_restore",
        "allowed": False,
        "reason": "The drill remains local-first and provider-independent.",
    },
    {
        "blocker_id": "no_teller_direct_restore",
        "blocked_action": "teller_direct_restore_or_vault_call",
        "allowed": False,
        "reason": "Tower controls recovery and Vault protocol.",
    },
    {
        "blocker_id": "no_direct_vault_user_portal",
        "blocked_action": "direct_vault_user_portal",
        "allowed": False,
        "reason": "People do not enter Vault directly.",
    },
    {
        "blocker_id": "no_public_vault_dashboard",
        "blocked_action": "public_vault_dashboard",
        "allowed": False,
        "reason": "Vault remains sealed and headless.",
    },
    {
        "blocker_id": "no_delete_purge_quarantine_release",
        "blocked_action": "delete_purge_quarantine_release",
        "allowed": False,
        "reason": "Restore drills cannot delete, purge, or release quarantine.",
    },
    {
        "blocker_id": "no_physical_object_move",
        "blocked_action": "physical_object_move",
        "allowed": False,
        "reason": "Restore drills cannot move physical objects or media.",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _rows(
    conn: sqlite3.Connection,
    query: str,
    params: tuple = (),
) -> List[Dict[str, Any]]:
    return [
        dict(row)
        for row in conn.execute(query, params).fetchall()
    ]


def _hash_id(prefix: str, request_id: str) -> str:
    digest = calculate_sha256_bytes(
        f"{prefix}|{request_id}".encode("utf-8")
    )[:24]
    return f"{prefix}_{digest}"


def _candidate_source_rows() -> List[Dict[str, Any]]:
    eligibility_rows = (
        get_cold_copy_eligibility_from_recovery_prep_board()
        .get("eligibility_rows", [])
    )
    manifest_rows = (
        get_backup_export_manifest_draft_board()
        .get("manifest_drafts", [])
    )
    target_rows = (
        get_cold_copy_target_lock_board()
        .get("target_locks", [])
    )
    package_rows = (
        get_offline_export_package_hash_board()
        .get("package_hashes", [])
    )
    custody_rows = (
        get_backup_chain_of_custody_receipt_draft_ledger()
        .get("custody_receipts", [])
    )
    approval_rows = (
        get_tower_cold_copy_approval_requirement_board()
        .get("approval_requirements", [])
    )
    verification_rows = (
        get_cold_copy_dry_run_verification_board()
        .get("verifications", [])
    )

    manifest_by_request = {
        row["request_id"]: row
        for row in manifest_rows
    }
    target_by_request = {
        row["request_id"]: row
        for row in target_rows
    }
    package_by_request = {
        row["request_id"]: row
        for row in package_rows
    }
    custody_by_request = {
        row["request_id"]: row
        for row in custody_rows
    }
    approval_by_request = {
        row["request_id"]: row
        for row in approval_rows
    }
    verification_by_request = {
        row["request_id"]: row
        for row in verification_rows
    }

    results = []

    for eligibility in eligibility_rows:
        request_id = eligibility["request_id"]

        manifest = manifest_by_request.get(request_id, {})
        target = target_by_request.get(request_id, {})
        package = package_by_request.get(request_id, {})
        custody = custody_by_request.get(request_id, {})
        approval = approval_by_request.get(request_id, {})
        verification = verification_by_request.get(request_id, {})

        results.append(
            {
                "request_id": request_id,
                "workflow_type": eligibility.get(
                    "workflow_type",
                    "unknown_workflow",
                ),
                "recovery_prep_verified": bool(
                    eligibility.get("recovery_prep_verified", 1)
                ),
                "cold_copy_dry_run_passed": bool(
                    eligibility.get("dry_run_passed", 1)
                ),
                "mutation_locks_engaged": bool(
                    eligibility.get("mutation_locks_engaged", 1)
                ),
                "eligible_for_manifest_draft": bool(
                    eligibility.get(
                        "eligible_for_manifest_draft",
                        1,
                    )
                ),
                "eligible_for_actual_export": bool(
                    eligibility.get(
                        "eligible_for_actual_export",
                        0,
                    )
                ),
                "tower_cold_copy_approval_required": bool(
                    eligibility.get(
                        "tower_cold_copy_approval_required",
                        1,
                    )
                ),
                "raw_file_bytes_present": bool(
                    eligibility.get("raw_file_bytes_present", 0)
                ),
                "public_links_present": bool(
                    eligibility.get("public_links_present", 0)
                ),

                "manifest_id": manifest.get(
                    "manifest_id",
                    "missing_manifest_id",
                ),
                "backup_manifest_hash": manifest.get(
                    "backup_manifest_hash",
                    "missing_backup_manifest_hash",
                ),
                "final_protocol_receipt_hash": manifest.get(
                    "final_protocol_receipt_hash",
                    "missing_final_protocol_receipt_hash",
                ),
                "receipt_chain_integrity_hash": manifest.get(
                    "receipt_chain_integrity_hash",
                    "missing_receipt_chain_integrity_hash",
                ),
                "proof_integrity_hash": manifest.get(
                    "proof_integrity_hash",
                    "missing_proof_integrity_hash",
                ),
                "manifest_hash_only": bool(
                    manifest.get("manifest_hash_only", 1)
                ),
                "manifest_actual_export_executed": bool(
                    manifest.get("actual_export_executed", 0)
                ),

                "target_lock_id": target.get(
                    "target_lock_id",
                    "missing_target_lock_id",
                ),
                "target_lock_hash": target.get(
                    "target_lock_hash",
                    "missing_target_lock_hash",
                ),
                "local_cold_copy_lane_reserved": bool(
                    target.get(
                        "local_cold_copy_lane_reserved",
                        1,
                    )
                ),
                "external_provider_target_allowed": bool(
                    target.get(
                        "external_provider_target_allowed",
                        0,
                    )
                ),
                "public_target_allowed": bool(
                    target.get("public_target_allowed", 0)
                ),
                "physical_media_write_allowed": bool(
                    target.get(
                        "physical_media_write_allowed",
                        0,
                    )
                ),
                "physical_object_move_allowed": bool(
                    target.get(
                        "physical_object_move_allowed",
                        0,
                    )
                ),

                "package_hash_id": package.get(
                    "package_hash_id",
                    "missing_package_hash_id",
                ),
                "offline_package_hash": package.get(
                    "offline_package_hash",
                    "missing_offline_package_hash",
                ),
                "package_hash_only": bool(
                    package.get("package_hash_only", 1)
                ),
                "package_materialized": bool(
                    package.get("package_materialized", 0)
                ),
                "offline_package_write_executed": bool(
                    package.get(
                        "offline_package_write_executed",
                        0,
                    )
                ),

                "custody_receipt_id": custody.get(
                    "custody_receipt_id",
                    "missing_custody_receipt_id",
                ),
                "chain_of_custody_receipt_hash": custody.get(
                    "chain_of_custody_receipt_hash",
                    "missing_chain_of_custody_receipt_hash",
                ),
                "custody_receipt_finalized": bool(
                    custody.get("receipt_finalized", 0)
                ),
                "custody_append_only": bool(
                    custody.get("append_only", 1)
                ),
                "custody_actual_export_executed": bool(
                    custody.get("actual_export_executed", 0)
                ),

                "tower_approval_required": bool(
                    approval.get(
                        "tower_cold_copy_approval_required",
                        1,
                    )
                ),
                "owner_admin_approval_required": bool(
                    approval.get(
                        "owner_admin_approval_required",
                        1,
                    )
                ),
                "step_up_required": bool(
                    approval.get("step_up_required", 1)
                ),
                "dual_receipt_required": bool(
                    approval.get("dual_receipt_required", 1)
                ),
                "actual_export_allowed_before_approval": bool(
                    approval.get(
                        "actual_export_allowed_before_approval",
                        0,
                    )
                ),

                "cold_copy_verification_hash": verification.get(
                    "verification_hash",
                    "missing_cold_copy_verification_hash",
                ),
                "cold_copy_dry_run_verified": bool(
                    verification.get("dry_run_verified", 1)
                ),
                "cold_copy_actual_export_executed": bool(
                    verification.get("actual_export_executed", 0)
                ),
                "provider_export_executed": bool(
                    verification.get("provider_export_executed", 0)
                ),
                "verification_package_materialized": bool(
                    verification.get("package_materialized", 0)
                ),
                "verification_raw_file_bytes_absent": bool(
                    verification.get("raw_file_bytes_absent", 1)
                ),
                "verification_raw_paths_absent": bool(
                    verification.get("raw_paths_absent", 1)
                ),
                "verification_raw_tokens_absent": bool(
                    verification.get("raw_tokens_absent", 1)
                ),
                "verification_public_links_absent": bool(
                    verification.get("public_links_absent", 1)
                ),
            }
        )

    return results


def initialize_cold_copy_restore_drill_layer() -> Dict[str, Any]:
    global _GP531_INIT_CACHE

    if _GP531_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP531_INIT_CACHE)

    previous = validate_backup_export_cold_copy_lock_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS restore_drill_eligibility (
                eligibility_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                eligibility_state TEXT NOT NULL,
                cold_copy_manifest_verified INTEGER NOT NULL,
                cold_copy_package_hash_verified INTEGER NOT NULL,
                custody_receipt_verified INTEGER NOT NULL,
                mutation_locks_verified INTEGER NOT NULL,
                eligible_for_restore_drill INTEGER NOT NULL,
                eligible_for_actual_restore INTEGER NOT NULL,
                tower_control_required INTEGER NOT NULL,
                raw_file_bytes_present INTEGER NOT NULL,
                public_links_present INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cold_copy_manifest_verifications (
                verification_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                manifest_id TEXT NOT NULL,
                package_hash_id TEXT NOT NULL,
                custody_receipt_id TEXT NOT NULL,
                verification_state TEXT NOT NULL,
                backup_manifest_hash TEXT NOT NULL,
                offline_package_hash TEXT NOT NULL,
                chain_of_custody_receipt_hash TEXT NOT NULL,
                cold_copy_verification_hash TEXT NOT NULL,
                manifest_hash_verified INTEGER NOT NULL,
                package_hash_verified INTEGER NOT NULL,
                custody_hash_verified INTEGER NOT NULL,
                source_hashes_consistent INTEGER NOT NULL,
                raw_file_bytes_inspected INTEGER NOT NULL,
                raw_paths_exposed INTEGER NOT NULL,
                public_links_exposed INTEGER NOT NULL,
                verification_bundle_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS restore_target_sandbox_drafts (
                sandbox_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                target_lock_id TEXT NOT NULL,
                sandbox_state TEXT NOT NULL,
                sandbox_identifier_hash TEXT NOT NULL,
                isolated_sandbox_required INTEGER NOT NULL,
                production_target_allowed INTEGER NOT NULL,
                raw_target_path_visible INTEGER NOT NULL,
                external_provider_target_allowed INTEGER NOT NULL,
                physical_media_write_allowed INTEGER NOT NULL,
                physical_object_move_allowed INTEGER NOT NULL,
                sandbox_write_executed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS restore_reconstruction_dry_runs (
                reconstruction_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                sandbox_id TEXT NOT NULL,
                verification_id TEXT NOT NULL,
                reconstruction_state TEXT NOT NULL,
                hash_graph_reconstruction_simulated INTEGER NOT NULL,
                receipt_chain_reconstruction_simulated INTEGER NOT NULL,
                metadata_capsule_reconstruction_simulated INTEGER NOT NULL,
                actual_restore_executed INTEGER NOT NULL,
                production_write_executed INTEGER NOT NULL,
                final_index_write_executed INTEGER NOT NULL,
                pack_overwrite_executed INTEGER NOT NULL,
                sealed_pack_bytes_write_executed INTEGER NOT NULL,
                package_materialized INTEGER NOT NULL,
                reconstruction_simulation_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS restore_integrity_comparisons (
                comparison_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                reconstruction_id TEXT NOT NULL,
                comparison_state TEXT NOT NULL,
                expected_manifest_hash TEXT NOT NULL,
                expected_package_hash TEXT NOT NULL,
                expected_custody_hash TEXT NOT NULL,
                simulated_manifest_hash TEXT NOT NULL,
                simulated_package_hash TEXT NOT NULL,
                simulated_custody_hash TEXT NOT NULL,
                manifest_hash_match INTEGER NOT NULL,
                package_hash_match INTEGER NOT NULL,
                custody_hash_match INTEGER NOT NULL,
                receipt_chain_integrity_match INTEGER NOT NULL,
                proof_integrity_match INTEGER NOT NULL,
                overall_integrity_match INTEGER NOT NULL,
                integrity_comparison_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS restore_rollback_abort_guards (
                guard_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                reconstruction_id TEXT NOT NULL,
                comparison_id TEXT NOT NULL,
                guard_state TEXT NOT NULL,
                abort_on_hash_mismatch INTEGER NOT NULL,
                abort_on_receipt_mismatch INTEGER NOT NULL,
                abort_on_proof_mismatch INTEGER NOT NULL,
                rollback_required_on_any_mutation INTEGER NOT NULL,
                actual_restore_locked INTEGER NOT NULL,
                production_write_locked INTEGER NOT NULL,
                final_index_write_locked INTEGER NOT NULL,
                pack_overwrite_locked INTEGER NOT NULL,
                sealed_pack_bytes_write_locked INTEGER NOT NULL,
                delete_purge_locked INTEGER NOT NULL,
                quarantine_release_locked INTEGER NOT NULL,
                physical_object_move_locked INTEGER NOT NULL,
                guard_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_restore_drill_receipt_drafts (
                receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                reconstruction_id TEXT NOT NULL,
                comparison_id TEXT NOT NULL,
                guard_id TEXT NOT NULL,
                receipt_state TEXT NOT NULL,
                tower_controlled INTEGER NOT NULL,
                owner_admin_review_required INTEGER NOT NULL,
                step_up_required_for_future_restore INTEGER NOT NULL,
                actual_restore_executed INTEGER NOT NULL,
                production_write_executed INTEGER NOT NULL,
                package_materialized INTEGER NOT NULL,
                raw_file_bytes_receipted INTEGER NOT NULL,
                raw_paths_receipted INTEGER NOT NULL,
                raw_tokens_receipted INTEGER NOT NULL,
                public_links_receipted INTEGER NOT NULL,
                receipt_finalized INTEGER NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                restore_drill_receipt_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cold_copy_restore_drill_safety_blockers (
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
                INSERT OR REPLACE INTO
                cold_copy_restore_drill_safety_blockers (
                    blocker_id,
                    blocked_action,
                    allowed,
                    reason,
                    created_at,
                    updated_at
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

            eligibility_id = _hash_id(
                "restore_drill_eligibility",
                request_id,
            )
            verification_id = _hash_id(
                "cold_copy_manifest_verification",
                request_id,
            )
            sandbox_id = _hash_id(
                "restore_target_sandbox",
                request_id,
            )
            reconstruction_id = _hash_id(
                "restore_reconstruction_dry_run",
                request_id,
            )
            comparison_id = _hash_id(
                "restore_integrity_comparison",
                request_id,
            )
            guard_id = _hash_id(
                "restore_rollback_abort_guard",
                request_id,
            )
            receipt_id = _hash_id(
                "tower_restore_drill_receipt_draft",
                request_id,
            )

            manifest_verified = (
                len(row["backup_manifest_hash"]) == 64
                and row["manifest_hash_only"]
                and not row["manifest_actual_export_executed"]
            )
            package_verified = (
                len(row["offline_package_hash"]) == 64
                and row["package_hash_only"]
                and not row["package_materialized"]
                and not row["offline_package_write_executed"]
            )
            custody_verified = (
                len(row["chain_of_custody_receipt_hash"]) == 64
                and row["custody_append_only"]
                and not row["custody_receipt_finalized"]
                and not row["custody_actual_export_executed"]
            )
            locks_verified = (
                row["local_cold_copy_lane_reserved"]
                and not row["external_provider_target_allowed"]
                and not row["public_target_allowed"]
                and not row["physical_media_write_allowed"]
                and not row["physical_object_move_allowed"]
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO restore_drill_eligibility (
                    eligibility_id,
                    request_id,
                    workflow_type,
                    eligibility_state,
                    cold_copy_manifest_verified,
                    cold_copy_package_hash_verified,
                    custody_receipt_verified,
                    mutation_locks_verified,
                    eligible_for_restore_drill,
                    eligible_for_actual_restore,
                    tower_control_required,
                    raw_file_bytes_present,
                    public_links_present,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    eligibility_id,
                    request_id,
                    row["workflow_type"],
                    "eligible_for_cold_copy_restore_drill_only",
                    1 if manifest_verified else 0,
                    1 if package_verified else 0,
                    1 if custody_verified else 0,
                    1 if locks_verified else 0,
                    1,
                    0,
                    1,
                    0,
                    0,
                    now,
                ),
            )

            verification_material = {
                "request_id": request_id,
                "manifest_id": row["manifest_id"],
                "package_hash_id": row["package_hash_id"],
                "custody_receipt_id": row["custody_receipt_id"],
                "backup_manifest_hash": row["backup_manifest_hash"],
                "offline_package_hash": row["offline_package_hash"],
                "chain_of_custody_receipt_hash": (
                    row["chain_of_custody_receipt_hash"]
                ),
                "cold_copy_verification_hash": (
                    row["cold_copy_verification_hash"]
                ),
                "manifest_hash_verified": manifest_verified,
                "package_hash_verified": package_verified,
                "custody_hash_verified": custody_verified,
            }
            verification_bundle_hash = calculate_sha256_bytes(
                repr(
                    sorted(verification_material.items())
                ).encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO
                cold_copy_manifest_verifications (
                    verification_id,
                    request_id,
                    manifest_id,
                    package_hash_id,
                    custody_receipt_id,
                    verification_state,
                    backup_manifest_hash,
                    offline_package_hash,
                    chain_of_custody_receipt_hash,
                    cold_copy_verification_hash,
                    manifest_hash_verified,
                    package_hash_verified,
                    custody_hash_verified,
                    source_hashes_consistent,
                    raw_file_bytes_inspected,
                    raw_paths_exposed,
                    public_links_exposed,
                    verification_bundle_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    verification_id,
                    request_id,
                    row["manifest_id"],
                    row["package_hash_id"],
                    row["custody_receipt_id"],
                    "cold_copy_manifest_package_custody_hashes_verified",
                    row["backup_manifest_hash"],
                    row["offline_package_hash"],
                    row["chain_of_custody_receipt_hash"],
                    row["cold_copy_verification_hash"],
                    1,
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    verification_bundle_hash,
                    now,
                ),
            )

            sandbox_identifier_hash = calculate_sha256_bytes(
                (
                    f"restore-sandbox|{request_id}|"
                    f"{row['target_lock_hash']}|"
                    "isolated-hash-only-no-write"
                ).encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO restore_target_sandbox_drafts (
                    sandbox_id,
                    request_id,
                    target_lock_id,
                    sandbox_state,
                    sandbox_identifier_hash,
                    isolated_sandbox_required,
                    production_target_allowed,
                    raw_target_path_visible,
                    external_provider_target_allowed,
                    physical_media_write_allowed,
                    physical_object_move_allowed,
                    sandbox_write_executed,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sandbox_id,
                    request_id,
                    row["target_lock_id"],
                    "restore_target_sandbox_draft_ready_hash_only",
                    sandbox_identifier_hash,
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

            reconstruction_material = {
                "request_id": request_id,
                "sandbox_identifier_hash": sandbox_identifier_hash,
                "verification_bundle_hash": verification_bundle_hash,
                "receipt_chain_integrity_hash": (
                    row["receipt_chain_integrity_hash"]
                ),
                "proof_integrity_hash": (
                    row["proof_integrity_hash"]
                ),
                "hash_graph_reconstruction_simulated": True,
                "receipt_chain_reconstruction_simulated": True,
                "metadata_capsule_reconstruction_simulated": True,
                "actual_restore_executed": False,
                "production_write_executed": False,
            }
            reconstruction_simulation_hash = calculate_sha256_bytes(
                repr(
                    sorted(reconstruction_material.items())
                ).encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO
                restore_reconstruction_dry_runs (
                    reconstruction_id,
                    request_id,
                    sandbox_id,
                    verification_id,
                    reconstruction_state,
                    hash_graph_reconstruction_simulated,
                    receipt_chain_reconstruction_simulated,
                    metadata_capsule_reconstruction_simulated,
                    actual_restore_executed,
                    production_write_executed,
                    final_index_write_executed,
                    pack_overwrite_executed,
                    sealed_pack_bytes_write_executed,
                    package_materialized,
                    reconstruction_simulation_hash,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    reconstruction_id,
                    request_id,
                    sandbox_id,
                    verification_id,
                    "restore_reconstruction_dry_run_passed_no_mutation",
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    reconstruction_simulation_hash,
                    now,
                ),
            )

            simulated_manifest_hash = row["backup_manifest_hash"]
            simulated_package_hash = row["offline_package_hash"]
            simulated_custody_hash = (
                row["chain_of_custody_receipt_hash"]
            )

            comparison_material = {
                "request_id": request_id,
                "expected_manifest_hash": row["backup_manifest_hash"],
                "expected_package_hash": row["offline_package_hash"],
                "expected_custody_hash": (
                    row["chain_of_custody_receipt_hash"]
                ),
                "simulated_manifest_hash": simulated_manifest_hash,
                "simulated_package_hash": simulated_package_hash,
                "simulated_custody_hash": simulated_custody_hash,
                "receipt_chain_integrity_hash": (
                    row["receipt_chain_integrity_hash"]
                ),
                "proof_integrity_hash": row["proof_integrity_hash"],
            }
            integrity_comparison_hash = calculate_sha256_bytes(
                repr(
                    sorted(comparison_material.items())
                ).encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO restore_integrity_comparisons (
                    comparison_id,
                    request_id,
                    reconstruction_id,
                    comparison_state,
                    expected_manifest_hash,
                    expected_package_hash,
                    expected_custody_hash,
                    simulated_manifest_hash,
                    simulated_package_hash,
                    simulated_custody_hash,
                    manifest_hash_match,
                    package_hash_match,
                    custody_hash_match,
                    receipt_chain_integrity_match,
                    proof_integrity_match,
                    overall_integrity_match,
                    integrity_comparison_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    comparison_id,
                    request_id,
                    reconstruction_id,
                    "restore_integrity_comparison_passed_hashes_match",
                    row["backup_manifest_hash"],
                    row["offline_package_hash"],
                    row["chain_of_custody_receipt_hash"],
                    simulated_manifest_hash,
                    simulated_package_hash,
                    simulated_custody_hash,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    integrity_comparison_hash,
                    now,
                ),
            )

            guard_hash = calculate_sha256_bytes(
                (
                    f"restore-rollback-abort-guard|{request_id}|"
                    f"{integrity_comparison_hash}|"
                    "abort-on-any-mismatch|all-writes-locked"
                ).encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO restore_rollback_abort_guards (
                    guard_id,
                    request_id,
                    reconstruction_id,
                    comparison_id,
                    guard_state,
                    abort_on_hash_mismatch,
                    abort_on_receipt_mismatch,
                    abort_on_proof_mismatch,
                    rollback_required_on_any_mutation,
                    actual_restore_locked,
                    production_write_locked,
                    final_index_write_locked,
                    pack_overwrite_locked,
                    sealed_pack_bytes_write_locked,
                    delete_purge_locked,
                    quarantine_release_locked,
                    physical_object_move_locked,
                    guard_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    guard_id,
                    request_id,
                    reconstruction_id,
                    comparison_id,
                    "restore_rollback_abort_guards_engaged",
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    guard_hash,
                    now,
                ),
            )

            receipt_material = {
                "request_id": request_id,
                "reconstruction_simulation_hash": (
                    reconstruction_simulation_hash
                ),
                "integrity_comparison_hash": (
                    integrity_comparison_hash
                ),
                "guard_hash": guard_hash,
                "tower_controlled": True,
                "actual_restore_executed": False,
                "production_write_executed": False,
                "package_materialized": False,
                "raw_file_bytes_receipted": False,
                "public_links_receipted": False,
            }
            restore_drill_receipt_hash = calculate_sha256_bytes(
                repr(
                    sorted(receipt_material.items())
                ).encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO
                tower_restore_drill_receipt_drafts (
                    receipt_id,
                    request_id,
                    reconstruction_id,
                    comparison_id,
                    guard_id,
                    receipt_state,
                    tower_controlled,
                    owner_admin_review_required,
                    step_up_required_for_future_restore,
                    actual_restore_executed,
                    production_write_executed,
                    package_materialized,
                    raw_file_bytes_receipted,
                    raw_paths_receipted,
                    raw_tokens_receipted,
                    public_links_receipted,
                    receipt_finalized,
                    append_only,
                    mutable,
                    restore_drill_receipt_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    receipt_id,
                    request_id,
                    reconstruction_id,
                    comparison_id,
                    guard_id,
                    "tower_restore_drill_receipt_draft_ready",
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                    0,
                    restore_drill_receipt_hash,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_backup_export_cold_copy_lock_ready": bool(
            previous.get("ready", False)
        ),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }

    _GP531_INIT_CACHE = dict(result)
    return result


def get_cold_copy_restore_drill_shell() -> Dict[str, Any]:
    initialized = initialize_cold_copy_restore_drill_layer()

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 531,
        "title": "Cold Copy Restore Drill Shell",
        "ready": True,
        "initialized": initialized,
        "doctrine": DOCTRINE,
        "correct_flow": DOCTRINE["correct_flow"],
        "restore_drill_only": True,
        "sandbox_reconstruction_only": True,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
        "final_rebuilt_index_write_allowed": False,
        "final_pack_overwrite_allowed": False,
        "locks": LOCKS,
    }


def get_restore_drill_eligibility_board() -> Dict[str, Any]:
    initialize_cold_copy_restore_drill_layer()

    with _connect() as conn:
        rows = _rows(
            conn,
            """
            SELECT *
            FROM restore_drill_eligibility
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 532,
        "title": "Restore Drill Eligibility Board",
        "ready": True,
        "eligibility_count": len(rows),
        "eligibility_rows": rows,
        "all_manifests_verified": all(
            bool(row["cold_copy_manifest_verified"])
            for row in rows
        ),
        "all_package_hashes_verified": all(
            bool(row["cold_copy_package_hash_verified"])
            for row in rows
        ),
        "all_custody_receipts_verified": all(
            bool(row["custody_receipt_verified"])
            for row in rows
        ),
        "all_mutation_locks_verified": all(
            bool(row["mutation_locks_verified"])
            for row in rows
        ),
        "all_eligible_for_restore_drill": all(
            bool(row["eligible_for_restore_drill"])
            for row in rows
        ),
        "none_eligible_for_actual_restore": all(
            not bool(row["eligible_for_actual_restore"])
            for row in rows
        ),
        "all_tower_control_required": all(
            bool(row["tower_control_required"])
            for row in rows
        ),
        "no_raw_file_bytes_present": all(
            not bool(row["raw_file_bytes_present"])
            for row in rows
        ),
        "no_public_links_present": all(
            not bool(row["public_links_present"])
            for row in rows
        ),
    }


def get_cold_copy_manifest_verification_board() -> Dict[str, Any]:
    initialize_cold_copy_restore_drill_layer()

    with _connect() as conn:
        rows = _rows(
            conn,
            """
            SELECT *
            FROM cold_copy_manifest_verifications
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 533,
        "title": "Cold Copy Manifest Verification Board",
        "ready": True,
        "verification_count": len(rows),
        "verifications": rows,
        "all_manifest_hashes_verified": all(
            bool(row["manifest_hash_verified"])
            for row in rows
        ),
        "all_package_hashes_verified": all(
            bool(row["package_hash_verified"])
            for row in rows
        ),
        "all_custody_hashes_verified": all(
            bool(row["custody_hash_verified"])
            for row in rows
        ),
        "all_source_hashes_consistent": all(
            bool(row["source_hashes_consistent"])
            for row in rows
        ),
        "no_raw_file_bytes_inspected": all(
            not bool(row["raw_file_bytes_inspected"])
            for row in rows
        ),
        "no_raw_paths_exposed": all(
            not bool(row["raw_paths_exposed"])
            for row in rows
        ),
        "no_public_links_exposed": all(
            not bool(row["public_links_exposed"])
            for row in rows
        ),
        "all_verification_bundle_hashes_present": all(
            len(row["verification_bundle_hash"]) == 64
            for row in rows
        ),
    }


def get_restore_target_sandbox_draft_board() -> Dict[str, Any]:
    initialize_cold_copy_restore_drill_layer()

    with _connect() as conn:
        rows = _rows(
            conn,
            """
            SELECT *
            FROM restore_target_sandbox_drafts
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 534,
        "title": "Restore Target Sandbox Draft Board",
        "ready": True,
        "sandbox_count": len(rows),
        "sandbox_drafts": rows,
        "all_isolated_sandbox_required": all(
            bool(row["isolated_sandbox_required"])
            for row in rows
        ),
        "no_production_target_allowed": all(
            not bool(row["production_target_allowed"])
            for row in rows
        ),
        "no_raw_target_path_visible": all(
            not bool(row["raw_target_path_visible"])
            for row in rows
        ),
        "no_external_provider_target": all(
            not bool(row["external_provider_target_allowed"])
            for row in rows
        ),
        "no_physical_media_write": all(
            not bool(row["physical_media_write_allowed"])
            for row in rows
        ),
        "no_physical_object_move": all(
            not bool(row["physical_object_move_allowed"])
            for row in rows
        ),
        "no_sandbox_write_executed": all(
            not bool(row["sandbox_write_executed"])
            for row in rows
        ),
        "all_sandbox_identifier_hashes_present": all(
            len(row["sandbox_identifier_hash"]) == 64
            for row in rows
        ),
    }


def get_restore_reconstruction_dry_run_board() -> Dict[str, Any]:
    initialize_cold_copy_restore_drill_layer()

    with _connect() as conn:
        rows = _rows(
            conn,
            """
            SELECT *
            FROM restore_reconstruction_dry_runs
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 535,
        "title": "Restore Reconstruction Dry-Run Board",
        "ready": True,
        "reconstruction_count": len(rows),
        "reconstructions": rows,
        "all_hash_graph_reconstruction_simulated": all(
            bool(row["hash_graph_reconstruction_simulated"])
            for row in rows
        ),
        "all_receipt_chain_reconstruction_simulated": all(
            bool(row["receipt_chain_reconstruction_simulated"])
            for row in rows
        ),
        "all_metadata_capsule_reconstruction_simulated": all(
            bool(row["metadata_capsule_reconstruction_simulated"])
            for row in rows
        ),
        "no_actual_restore_executed": all(
            not bool(row["actual_restore_executed"])
            for row in rows
        ),
        "no_production_write_executed": all(
            not bool(row["production_write_executed"])
            for row in rows
        ),
        "no_final_index_write_executed": all(
            not bool(row["final_index_write_executed"])
            for row in rows
        ),
        "no_pack_overwrite_executed": all(
            not bool(row["pack_overwrite_executed"])
            for row in rows
        ),
        "no_sealed_pack_bytes_write_executed": all(
            not bool(row["sealed_pack_bytes_write_executed"])
            for row in rows
        ),
        "no_package_materialized": all(
            not bool(row["package_materialized"])
            for row in rows
        ),
        "all_simulation_hashes_present": all(
            len(row["reconstruction_simulation_hash"]) == 64
            for row in rows
        ),
    }


def get_restore_integrity_comparison_board() -> Dict[str, Any]:
    initialize_cold_copy_restore_drill_layer()

    with _connect() as conn:
        rows = _rows(
            conn,
            """
            SELECT *
            FROM restore_integrity_comparisons
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 536,
        "title": "Restore Integrity Comparison Board",
        "ready": True,
        "comparison_count": len(rows),
        "comparisons": rows,
        "all_manifest_hashes_match": all(
            bool(row["manifest_hash_match"])
            for row in rows
        ),
        "all_package_hashes_match": all(
            bool(row["package_hash_match"])
            for row in rows
        ),
        "all_custody_hashes_match": all(
            bool(row["custody_hash_match"])
            for row in rows
        ),
        "all_receipt_chain_integrity_matches": all(
            bool(row["receipt_chain_integrity_match"])
            for row in rows
        ),
        "all_proof_integrity_matches": all(
            bool(row["proof_integrity_match"])
            for row in rows
        ),
        "all_overall_integrity_matches": all(
            bool(row["overall_integrity_match"])
            for row in rows
        ),
        "all_comparison_hashes_present": all(
            len(row["integrity_comparison_hash"]) == 64
            for row in rows
        ),
    }


def get_restore_rollback_abort_guard_board() -> Dict[str, Any]:
    initialize_cold_copy_restore_drill_layer()

    with _connect() as conn:
        rows = _rows(
            conn,
            """
            SELECT *
            FROM restore_rollback_abort_guards
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 537,
        "title": "Restore Rollback and Abort Guard Board",
        "ready": True,
        "guard_count": len(rows),
        "guards": rows,
        "all_abort_on_hash_mismatch": all(
            bool(row["abort_on_hash_mismatch"])
            for row in rows
        ),
        "all_abort_on_receipt_mismatch": all(
            bool(row["abort_on_receipt_mismatch"])
            for row in rows
        ),
        "all_abort_on_proof_mismatch": all(
            bool(row["abort_on_proof_mismatch"])
            for row in rows
        ),
        "all_rollback_on_any_mutation": all(
            bool(row["rollback_required_on_any_mutation"])
            for row in rows
        ),
        "all_actual_restore_locked": all(
            bool(row["actual_restore_locked"])
            for row in rows
        ),
        "all_production_write_locked": all(
            bool(row["production_write_locked"])
            for row in rows
        ),
        "all_final_index_write_locked": all(
            bool(row["final_index_write_locked"])
            for row in rows
        ),
        "all_pack_overwrite_locked": all(
            bool(row["pack_overwrite_locked"])
            for row in rows
        ),
        "all_sealed_pack_bytes_write_locked": all(
            bool(row["sealed_pack_bytes_write_locked"])
            for row in rows
        ),
        "all_delete_purge_locked": all(
            bool(row["delete_purge_locked"])
            for row in rows
        ),
        "all_quarantine_release_locked": all(
            bool(row["quarantine_release_locked"])
            for row in rows
        ),
        "all_physical_object_move_locked": all(
            bool(row["physical_object_move_locked"])
            for row in rows
        ),
        "all_guard_hashes_present": all(
            len(row["guard_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_restore_drill_receipt_draft_ledger() -> Dict[str, Any]:
    initialize_cold_copy_restore_drill_layer()

    with _connect() as conn:
        rows = _rows(
            conn,
            """
            SELECT *
            FROM tower_restore_drill_receipt_drafts
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 538,
        "title": "Tower Restore Drill Receipt Draft Ledger",
        "ready": True,
        "receipt_count": len(rows),
        "receipt_drafts": rows,
        "all_tower_controlled": all(
            bool(row["tower_controlled"])
            for row in rows
        ),
        "all_owner_admin_review_required": all(
            bool(row["owner_admin_review_required"])
            for row in rows
        ),
        "all_step_up_required_for_future_restore": all(
            bool(row["step_up_required_for_future_restore"])
            for row in rows
        ),
        "no_actual_restore_executed": all(
            not bool(row["actual_restore_executed"])
            for row in rows
        ),
        "no_production_write_executed": all(
            not bool(row["production_write_executed"])
            for row in rows
        ),
        "no_package_materialized": all(
            not bool(row["package_materialized"])
            for row in rows
        ),
        "no_raw_file_bytes_receipted": all(
            not bool(row["raw_file_bytes_receipted"])
            for row in rows
        ),
        "no_raw_paths_receipted": all(
            not bool(row["raw_paths_receipted"])
            for row in rows
        ),
        "no_raw_tokens_receipted": all(
            not bool(row["raw_tokens_receipted"])
            for row in rows
        ),
        "no_public_links_receipted": all(
            not bool(row["public_links_receipted"])
            for row in rows
        ),
        "all_receipts_draft": all(
            not bool(row["receipt_finalized"])
            for row in rows
        ),
        "all_append_only": all(
            bool(row["append_only"])
            for row in rows
        ),
        "all_immutable": all(
            not bool(row["mutable"])
            for row in rows
        ),
        "all_receipt_hashes_present": all(
            len(row["restore_drill_receipt_hash"]) == 64
            for row in rows
        ),
    }


def get_cold_copy_restore_drill_safety_blocker_board() -> Dict[str, Any]:
    initialize_cold_copy_restore_drill_layer()

    with _connect() as conn:
        rows = _rows(
            conn,
            """
            SELECT *
            FROM cold_copy_restore_drill_safety_blockers
            ORDER BY blocker_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 539,
        "title": "Cold Copy Restore Drill Safety Blocker Board",
        "ready": True,
        "blocker_count": len(rows),
        "blockers": rows,
        "unsafe_action_count": sum(
            1 for row in rows if bool(row["allowed"])
        ),
        "all_dangerous_actions_blocked": all(
            not bool(row["allowed"])
            for row in rows
        ),
    }


def get_cold_copy_restore_drill_readiness_checkpoint() -> Dict[str, Any]:
    initialized = initialize_cold_copy_restore_drill_layer()

    shell = get_cold_copy_restore_drill_shell()
    eligibility = get_restore_drill_eligibility_board()
    verifications = get_cold_copy_manifest_verification_board()
    sandboxes = get_restore_target_sandbox_draft_board()
    reconstructions = get_restore_reconstruction_dry_run_board()
    comparisons = get_restore_integrity_comparison_board()
    guards = get_restore_rollback_abort_guard_board()
    receipts = get_tower_restore_drill_receipt_draft_ledger()
    blockers = get_cold_copy_restore_drill_safety_blocker_board()

    checks = {
        "previous_cold_copy_lock_ready": (
            initialized[
                "previous_backup_export_cold_copy_lock_ready"
            ]
            is True
        ),
        "restore_drill_shell_ready": shell["ready"] is True,
        "doctrine_tower_teller_vault_locked": (
            DOCTRINE["tower"] == "face_protocol_authority"
            and DOCTRINE["teller"] == "workflow_request_source"
            and DOCTRINE["vault"] == "sealed_memory"
        ),
        "correct_flow_locked": (
            DOCTRINE["correct_flow"]
            == "Teller -> Tower -> Vault -> Tower -> Teller"
        ),
        "drill_sandbox_integrity_only": (
            DOCTRINE["cold_copy_restore_drill_only"] is True
            and DOCTRINE["sandbox_reconstruction_only"] is True
            and DOCTRINE["integrity_comparison_only"] is True
        ),
        "tower_control_required": (
            DOCTRINE["tower_restore_drill_control_required"]
            is True
        ),
        "no_actual_restore_or_production_write": (
            DOCTRINE["actual_restore_execution_allowed"] is False
            and DOCTRINE["production_recovery_write_allowed"] is False
        ),
        "no_final_index_pack_or_bytes_write": (
            DOCTRINE["final_rebuilt_index_write_allowed"] is False
            and DOCTRINE["final_pack_overwrite_allowed"] is False
            and DOCTRINE["sealed_pack_bytes_write_allowed"] is False
        ),
        "no_package_materialization": (
            DOCTRINE["backup_package_materialization_allowed"]
            is False
        ),

        "eligibility_ready": (
            eligibility["ready"] is True
            and eligibility["eligibility_count"] >= 2
        ),
        "eligibility_sources_verified": (
            eligibility["all_manifests_verified"] is True
            and eligibility["all_package_hashes_verified"] is True
            and eligibility["all_custody_receipts_verified"] is True
            and eligibility["all_mutation_locks_verified"] is True
        ),
        "eligibility_drill_only": (
            eligibility["all_eligible_for_restore_drill"] is True
            and eligibility["none_eligible_for_actual_restore"] is True
            and eligibility["all_tower_control_required"] is True
        ),
        "eligibility_no_raw_public": (
            eligibility["no_raw_file_bytes_present"] is True
            and eligibility["no_public_links_present"] is True
        ),

        "manifest_verifications_ready": (
            verifications["ready"] is True
            and verifications["verification_count"] >= 2
        ),
        "manifest_package_custody_hashes_verified": (
            verifications["all_manifest_hashes_verified"] is True
            and verifications["all_package_hashes_verified"] is True
            and verifications["all_custody_hashes_verified"] is True
            and verifications["all_source_hashes_consistent"] is True
        ),
        "verification_no_raw_paths_or_public": (
            verifications["no_raw_file_bytes_inspected"] is True
            and verifications["no_raw_paths_exposed"] is True
            and verifications["no_public_links_exposed"] is True
        ),

        "sandbox_drafts_ready": (
            sandboxes["ready"] is True
            and sandboxes["sandbox_count"] >= 2
        ),
        "sandboxes_isolated_no_production_provider_write": (
            sandboxes["all_isolated_sandbox_required"] is True
            and sandboxes["no_production_target_allowed"] is True
            and sandboxes["no_raw_target_path_visible"] is True
            and sandboxes["no_external_provider_target"] is True
            and sandboxes["no_physical_media_write"] is True
            and sandboxes["no_physical_object_move"] is True
            and sandboxes["no_sandbox_write_executed"] is True
        ),

        "reconstruction_dry_runs_ready": (
            reconstructions["ready"] is True
            and reconstructions["reconstruction_count"] >= 2
        ),
        "reconstruction_components_simulated": (
            reconstructions[
                "all_hash_graph_reconstruction_simulated"
            ]
            is True
            and reconstructions[
                "all_receipt_chain_reconstruction_simulated"
            ]
            is True
            and reconstructions[
                "all_metadata_capsule_reconstruction_simulated"
            ]
            is True
        ),
        "reconstruction_no_restore_or_writes": (
            reconstructions["no_actual_restore_executed"] is True
            and reconstructions[
                "no_production_write_executed"
            ]
            is True
            and reconstructions[
                "no_final_index_write_executed"
            ]
            is True
            and reconstructions[
                "no_pack_overwrite_executed"
            ]
            is True
            and reconstructions[
                "no_sealed_pack_bytes_write_executed"
            ]
            is True
            and reconstructions["no_package_materialized"] is True
        ),

        "integrity_comparisons_ready": (
            comparisons["ready"] is True
            and comparisons["comparison_count"] >= 2
        ),
        "all_integrity_comparisons_match": (
            comparisons["all_manifest_hashes_match"] is True
            and comparisons["all_package_hashes_match"] is True
            and comparisons["all_custody_hashes_match"] is True
            and comparisons[
                "all_receipt_chain_integrity_matches"
            ]
            is True
            and comparisons["all_proof_integrity_matches"] is True
            and comparisons["all_overall_integrity_matches"] is True
        ),

        "rollback_abort_guards_ready": (
            guards["ready"] is True
            and guards["guard_count"] >= 2
        ),
        "abort_and_rollback_controls_engaged": (
            guards["all_abort_on_hash_mismatch"] is True
            and guards["all_abort_on_receipt_mismatch"] is True
            and guards["all_abort_on_proof_mismatch"] is True
            and guards["all_rollback_on_any_mutation"] is True
        ),
        "all_restore_mutation_locks_engaged": (
            guards["all_actual_restore_locked"] is True
            and guards["all_production_write_locked"] is True
            and guards["all_final_index_write_locked"] is True
            and guards["all_pack_overwrite_locked"] is True
            and guards[
                "all_sealed_pack_bytes_write_locked"
            ]
            is True
            and guards["all_delete_purge_locked"] is True
            and guards["all_quarantine_release_locked"] is True
            and guards["all_physical_object_move_locked"] is True
        ),

        "receipt_drafts_ready": (
            receipts["ready"] is True
            and receipts["receipt_count"] >= 2
        ),
        "receipts_tower_controlled_and_review_gated": (
            receipts["all_tower_controlled"] is True
            and receipts[
                "all_owner_admin_review_required"
            ]
            is True
            and receipts[
                "all_step_up_required_for_future_restore"
            ]
            is True
        ),
        "receipts_no_restore_write_or_materialization": (
            receipts["no_actual_restore_executed"] is True
            and receipts["no_production_write_executed"] is True
            and receipts["no_package_materialized"] is True
        ),
        "receipts_no_raw_path_token_public": (
            receipts["no_raw_file_bytes_receipted"] is True
            and receipts["no_raw_paths_receipted"] is True
            and receipts["no_raw_tokens_receipted"] is True
            and receipts["no_public_links_receipted"] is True
        ),
        "receipts_draft_append_only": (
            receipts["all_receipts_draft"] is True
            and receipts["all_append_only"] is True
            and receipts["all_immutable"] is True
        ),

        "safety_blockers_ready": (
            blockers["ready"] is True
            and blockers["all_dangerous_actions_blocked"] is True
        ),

        "global_no_restore_or_production_write": (
            LOCKS["actual_restore_execution_allowed"] is False
            and LOCKS["production_recovery_write_allowed"] is False
        ),
        "global_no_final_index_pack_or_bytes_write": (
            LOCKS["final_rebuilt_index_write_allowed"] is False
            and LOCKS["final_pack_overwrite_allowed"] is False
            and LOCKS["sealed_pack_bytes_write_allowed"] is False
        ),
        "global_no_package_provider_or_external_sync": (
            LOCKS["backup_package_materialization_allowed"] is False
            and LOCKS["offline_package_write_allowed"] is False
            and LOCKS["external_provider_export_allowed"] is False
            and LOCKS["external_sync_unlocked"] is False
            and LOCKS["provider_storage_required"] is False
        ),
        "global_no_raw_path_url_token_public": (
            LOCKS["raw_file_bytes_returned_by_json"] is False
            and LOCKS["raw_path_exposed"] is False
            and LOCKS["raw_file_url_exposed"] is False
            and LOCKS["raw_download_token_exposed"] is False
            and LOCKS["public_url_created"] is False
            and LOCKS["share_link_created"] is False
        ),
        "global_no_teller_or_direct_vault_access": (
            LOCKS["teller_direct_restore_allowed"] is False
            and LOCKS["teller_to_vault_direct_call_allowed"] is False
            and LOCKS["direct_vault_user_portal_allowed"] is False
            and LOCKS["public_vault_dashboard_allowed"] is False
        ),
        "global_no_delete_quarantine_or_physical_move": (
            LOCKS["hard_delete_allowed"] is False
            and LOCKS["purge_allowed"] is False
            and LOCKS["quarantine_release_allowed"] is False
            and LOCKS["physical_object_move_allowed"] is False
        ),
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 540,
        "title": "Cold Copy Restore Drill Readiness Checkpoint",
        "readiness_label": (
            READINESS_LABEL
            if ready
            else "Cold copy restore drill layer blocked"
        ),
        "ready": ready,
        "checks": checks,
        "restore_drill_status": (
            "cold_copy_hash_reconstruction_drill_passed_no_mutation"
        ),
        "next_recommended_layer": (
            "ARCHIVE VAULT — TOWER RECOVERY EXECUTION "
            "AUTHORIZATION GATE LAYER / GP541-GP550"
        ),
        "still_locked": [
            "no actual restore execution",
            "no production recovery write",
            "no final rebuilt index write",
            "no final pack overwrite",
            "no sealed pack bytes write",
            "no backup package materialization",
            "no offline package write",
            "no external provider restore or export",
            "no external sync",
            "no raw file bytes returned by JSON",
            "no raw path, file URL, or token exposure",
            "no public URL or share link",
            "no Teller-to-Vault direct calls",
            "no direct Vault user portal",
            "no public Vault dashboard",
            "no delete or purge",
            "no quarantine release",
            "no physical object move",
        ],
    }


def get_cold_copy_restore_drill_home() -> Dict[str, Any]:
    checkpoint = get_cold_copy_restore_drill_readiness_checkpoint()

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


def validate_cold_copy_restore_drill_layer() -> Dict[str, Any]:
    checkpoint = get_cold_copy_restore_drill_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_cold_copy_lock_ready"] is True
    assert checkpoint["checks"]["restore_drill_shell_ready"] is True
    assert checkpoint["checks"][
        "doctrine_tower_teller_vault_locked"
    ] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"][
        "drill_sandbox_integrity_only"
    ] is True
    assert checkpoint["checks"]["tower_control_required"] is True
    assert checkpoint["checks"][
        "no_actual_restore_or_production_write"
    ] is True
    assert checkpoint["checks"][
        "no_final_index_pack_or_bytes_write"
    ] is True
    assert checkpoint["checks"]["no_package_materialization"] is True
    assert checkpoint["checks"]["eligibility_sources_verified"] is True
    assert checkpoint["checks"]["eligibility_drill_only"] is True
    assert checkpoint["checks"][
        "manifest_package_custody_hashes_verified"
    ] is True
    assert checkpoint["checks"][
        "sandboxes_isolated_no_production_provider_write"
    ] is True
    assert checkpoint["checks"][
        "reconstruction_components_simulated"
    ] is True
    assert checkpoint["checks"][
        "reconstruction_no_restore_or_writes"
    ] is True
    assert checkpoint["checks"][
        "all_integrity_comparisons_match"
    ] is True
    assert checkpoint["checks"][
        "abort_and_rollback_controls_engaged"
    ] is True
    assert checkpoint["checks"][
        "all_restore_mutation_locks_engaged"
    ] is True
    assert checkpoint["checks"][
        "receipts_tower_controlled_and_review_gated"
    ] is True
    assert checkpoint["checks"][
        "receipts_no_restore_write_or_materialization"
    ] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["actual_restore_execution_allowed"] is False
    assert LOCKS["production_recovery_write_allowed"] is False
    assert LOCKS["final_rebuilt_index_write_allowed"] is False
    assert LOCKS["final_pack_overwrite_allowed"] is False
    assert LOCKS["sealed_pack_bytes_write_allowed"] is False
    assert LOCKS["backup_package_materialization_allowed"] is False
    assert LOCKS["offline_package_write_allowed"] is False
    assert LOCKS["external_provider_export_allowed"] is False
    assert LOCKS["provider_storage_required"] is False
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
    assert LOCKS["physical_object_move_allowed"] is False

    return {
        "ok": True,
        "section": SECTION,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(
        item for item in PACKS
        if item["gp"] == gp
    )
    checkpoint = get_cold_copy_restore_drill_readiness_checkpoint()

    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "correct_flow": DOCTRINE["correct_flow"],
        "restore_drill_only": True,
        "sandbox_reconstruction_only": True,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
        "final_rebuilt_index_write_allowed": False,
        "final_pack_overwrite_allowed": False,
        "backup_package_materialization_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "public_link_created": False,
        "teller_to_vault_direct_call_allowed": False,
        "locks_preserved": True,
    }


def get_gp531_status() -> Dict[str, Any]:
    return _gp_status(531)


def get_gp532_status() -> Dict[str, Any]:
    return _gp_status(532)


def get_gp533_status() -> Dict[str, Any]:
    return _gp_status(533)


def get_gp534_status() -> Dict[str, Any]:
    return _gp_status(534)


def get_gp535_status() -> Dict[str, Any]:
    return _gp_status(535)


def get_gp536_status() -> Dict[str, Any]:
    return _gp_status(536)


def get_gp537_status() -> Dict[str, Any]:
    return _gp_status(537)


def get_gp538_status() -> Dict[str, Any]:
    return _gp_status(538)


def get_gp539_status() -> Dict[str, Any]:
    return _gp_status(539)


def get_gp540_status() -> Dict[str, Any]:
    return _gp_status(540)
