
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — CONTROLLED SOFT DELETE EXECUTION LAYER / GP401-GP410"
LAYER_ID = "vault_gp401_410_controlled_soft_delete_execution_layer"
READINESS_LABEL = "Controlled soft delete execution layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_controlled_soft_delete_execution_layer.sqlite"

SOFT_DELETE_RETENTION_DAYS = 30
RESTORE_REVIEW_WINDOW_DAYS = 7

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.trash_restore_recovery_prep_layer_service import (
        get_trash_eligibility_policy_board,
        get_owner_trash_approval_lock_board,
        get_restore_eligibility_lock_board,
        get_recovery_receipt_draft_ledger,
        validate_trash_restore_recovery_prep_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP401-GP410 requires GP391-GP400 trash restore recovery prep layer first."
    ) from exc


_GP401_INIT_CACHE = None

LOCKS = {
    "controlled_soft_delete_execution_layer": True,
    "controlled_metadata_soft_delete_execution_allowed": True,
    "soft_delete_state_write_allowed": True,
    "trash_lifecycle_ledger_allowed": True,
    "soft_delete_receipt_finalization_allowed": True,
    "post_delete_access_lock_allowed": True,
    "restore_handoff_preview_allowed": True,
    "hard_delete_allowed": False,
    "purge_allowed": False,
    "restore_execution_allowed": False,
    "restore_state_write_allowed": False,
    "physical_object_move_allowed": False,
    "physical_object_delete_allowed": False,
    "file_body_return_allowed": False,
    "raw_file_bytes_returned_by_json": False,
    "public_delete_unlocked": False,
    "beta_delete_unlocked": False,
    "public_restore_unlocked": False,
    "beta_restore_unlocked": False,
    "public_trash_unlocked": False,
    "beta_trash_unlocked": False,
    "quarantine_release_allowed": False,
    "quarantine_object_move_allowed": False,
    "public_upload_unlocked": False,
    "beta_upload_unlocked": False,
    "provider_upload_unlocked": False,
    "provider_storage_required": False,
    "external_sync_unlocked": False,
}

PACKS = [
    {"gp": 401, "title": "Controlled Soft Delete Execution Shell", "status": "ready", "route": "/vault/controlled-soft-delete-execution-shell.json"},
    {"gp": 402, "title": "Soft Delete Execution Scope Contract", "status": "ready", "route": "/vault/soft-delete-execution-scope-contract.json"},
    {"gp": 403, "title": "Owner Soft Delete Approval Execution Board", "status": "ready", "route": "/vault/owner-soft-delete-approval-execution-board.json"},
    {"gp": 404, "title": "Soft Delete State Writer", "status": "ready", "route": "/vault/soft-delete-state-writer.json"},
    {"gp": 405, "title": "Trash Lifecycle Ledger", "status": "ready", "route": "/vault/trash-lifecycle-ledger.json"},
    {"gp": 406, "title": "Soft Delete Receipt Finalization Board", "status": "ready", "route": "/vault/soft-delete-receipt-finalization-board.json"},
    {"gp": 407, "title": "Post-Delete Access Lock Board", "status": "ready", "route": "/vault/post-delete-access-lock-board.json"},
    {"gp": 408, "title": "Restore Handoff Preview Board", "status": "ready", "route": "/vault/restore-handoff-preview-board.json"},
    {"gp": 409, "title": "Soft Delete Safety Blocker Board", "status": "ready", "route": "/vault/soft-delete-safety-blocker-board.json"},
    {"gp": 410, "title": "Controlled Soft Delete Execution Readiness Checkpoint", "status": "ready", "route": "/vault/controlled-soft-delete-execution-readiness-checkpoint.json"},
]

BLOCKERS = [
    {
        "blocker_id": "no_hard_delete",
        "label": "Hard delete remains locked",
        "blocked_action": "hard_delete",
        "allowed": False,
        "reason": "Soft delete is metadata-only and reversible.",
    },
    {
        "blocker_id": "no_purge",
        "label": "Purge remains locked",
        "blocked_action": "purge",
        "allowed": False,
        "reason": "Purge is destructive and not allowed in this layer.",
    },
    {
        "blocker_id": "no_restore_execution",
        "label": "Restore execution remains locked",
        "blocked_action": "restore_execution",
        "allowed": False,
        "reason": "Restore belongs to a later controlled restore execution layer.",
    },
    {
        "blocker_id": "no_physical_object_move",
        "label": "Physical object move remains locked",
        "blocked_action": "physical_object_move",
        "allowed": False,
        "reason": "Soft delete only changes metadata state.",
    },
    {
        "blocker_id": "no_physical_object_delete",
        "label": "Physical object delete remains locked",
        "blocked_action": "physical_object_delete",
        "allowed": False,
        "reason": "No stored bytes are removed.",
    },
    {
        "blocker_id": "no_file_body_return",
        "label": "File body return remains locked",
        "blocked_action": "file_body_return",
        "allowed": False,
        "reason": "Soft delete execution routes are metadata-only.",
    },
    {
        "blocker_id": "no_public_delete_restore",
        "label": "Public delete/restore remains locked",
        "blocked_action": "public_delete_restore",
        "allowed": False,
        "reason": "No public lifecycle control exists.",
    },
    {
        "blocker_id": "no_beta_delete_restore",
        "label": "Beta delete/restore remains locked",
        "blocked_action": "beta_delete_restore",
        "allowed": False,
        "reason": "No tester lifecycle control exists.",
    },
    {
        "blocker_id": "no_quarantine_release",
        "label": "Quarantine release remains locked",
        "blocked_action": "quarantine_release",
        "allowed": False,
        "reason": "Soft delete does not release or move quarantine-held objects.",
    },
    {
        "blocker_id": "no_provider_upload",
        "label": "Provider upload remains locked",
        "blocked_action": "provider_upload",
        "allowed": False,
        "reason": "Owner-owned storage remains provider-independent.",
    },
    {
        "blocker_id": "no_external_sync",
        "label": "External sync remains locked",
        "blocked_action": "external_sync",
        "allowed": False,
        "reason": "Soft delete execution does not sync externally.",
    },
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


def _soft_delete_execution_id(active_file_id: str) -> str:
    return "soft_delete_execution_" + calculate_sha256_bytes(("soft_delete_execution|" + active_file_id).encode("utf-8"))[:24]


def _soft_delete_state_id(active_file_id: str) -> str:
    return "soft_delete_state_" + calculate_sha256_bytes(("soft_delete_state|" + active_file_id).encode("utf-8"))[:24]


def _trash_lifecycle_event_id(active_file_id: str) -> str:
    return "trash_lifecycle_event_" + calculate_sha256_bytes(("trash_lifecycle|" + active_file_id).encode("utf-8"))[:24]


def _soft_delete_receipt_id(active_file_id: str) -> str:
    return "soft_delete_receipt_final_" + calculate_sha256_bytes(("soft_delete_receipt|" + active_file_id).encode("utf-8"))[:24]


def _post_delete_access_lock_id(active_file_id: str) -> str:
    return "post_delete_access_lock_" + calculate_sha256_bytes(("post_delete_access|" + active_file_id).encode("utf-8"))[:24]


def _restore_handoff_preview_id(active_file_id: str) -> str:
    return "restore_handoff_preview_" + calculate_sha256_bytes(("restore_handoff|" + active_file_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    candidates = get_trash_eligibility_policy_board().get("candidates", [])
    approval_rows = get_owner_trash_approval_lock_board().get("approval_locks", [])
    restore_rows = get_restore_eligibility_lock_board().get("restore_locks", [])
    receipt_rows = get_recovery_receipt_draft_ledger().get("receipt_drafts", [])

    approval_by_file = {row["active_file_id"]: row for row in approval_rows}
    restore_by_file = {row["active_file_id"]: row for row in restore_rows}
    receipt_by_file = {row["active_file_id"]: row for row in receipt_rows}

    rows = []
    for item in candidates:
        active_file_id = item["active_file_id"]
        approval = approval_by_file.get(active_file_id, {})
        restore = restore_by_file.get(active_file_id, {})
        receipt = receipt_by_file.get(active_file_id, {})
        rows.append(
            {
                "active_file_id": active_file_id,
                "trash_candidate_id": item["trash_candidate_id"],
                "share_candidate_id": item["share_candidate_id"],
                "share_packet_id": item["share_packet_id"],
                "original_filename": item["original_filename"],
                "mime_type": item["mime_type"],
                "source_hash": item["source_hash"],
                "verified_hash": item["verified_hash"],
                "share_packet_hash": item["share_packet_hash"],
                "approval_state": approval.get("approval_state", "owner_trash_approval_required_locked"),
                "restore_state": restore.get("restore_state", "restore_eligibility_waiting_for_future_trash_state_locked"),
                "restore_review_window_days": int(restore.get("restore_review_window_days", RESTORE_REVIEW_WINDOW_DAYS)),
                "recovery_receipt_hash": receipt.get("receipt_hash", "recovery_receipt_draft_missing"),
            }
        )
    return rows


def initialize_controlled_soft_delete_execution_layer() -> Dict[str, Any]:
    global _GP401_INIT_CACHE
    if _GP401_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP401_INIT_CACHE)

    previous = validate_trash_restore_recovery_prep_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS owner_soft_delete_approval_execution (
                soft_delete_execution_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                trash_candidate_id TEXT NOT NULL,
                approval_state TEXT NOT NULL,
                owner_only INTEGER NOT NULL,
                approval_executed INTEGER NOT NULL,
                controlled_soft_delete_allowed INTEGER NOT NULL,
                hard_delete_allowed INTEGER NOT NULL,
                purge_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS soft_delete_state_records (
                soft_delete_state_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                trash_candidate_id TEXT NOT NULL,
                lifecycle_state TEXT NOT NULL,
                soft_deleted INTEGER NOT NULL,
                soft_deleted_at TEXT NOT NULL,
                retention_days INTEGER NOT NULL,
                hard_delete_allowed INTEGER NOT NULL,
                purge_allowed INTEGER NOT NULL,
                restore_execution_allowed INTEGER NOT NULL,
                physical_object_move_allowed INTEGER NOT NULL,
                file_body_return_allowed INTEGER NOT NULL,
                state_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trash_lifecycle_ledger (
                lifecycle_event_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                trash_candidate_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_state TEXT NOT NULL,
                metadata_only INTEGER NOT NULL,
                physical_object_moved INTEGER NOT NULL,
                hard_deleted INTEGER NOT NULL,
                purged INTEGER NOT NULL,
                lifecycle_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS soft_delete_receipt_finalization_board (
                final_receipt_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                trash_candidate_id TEXT NOT NULL,
                soft_delete_state_id TEXT NOT NULL,
                lifecycle_event_id TEXT NOT NULL,
                final_receipt_hash TEXT NOT NULL,
                finalized INTEGER NOT NULL,
                receipt_scope TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS post_delete_access_locks (
                post_delete_access_lock_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                trash_candidate_id TEXT NOT NULL,
                access_state TEXT NOT NULL,
                preview_allowed INTEGER NOT NULL,
                download_allowed INTEGER NOT NULL,
                share_allowed INTEGER NOT NULL,
                restore_preview_allowed INTEGER NOT NULL,
                public_access_allowed INTEGER NOT NULL,
                beta_access_allowed INTEGER NOT NULL,
                raw_file_bytes_json_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS restore_handoff_previews (
                restore_handoff_preview_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                trash_candidate_id TEXT NOT NULL,
                restore_state TEXT NOT NULL,
                restore_review_required INTEGER NOT NULL,
                restore_execution_allowed INTEGER NOT NULL,
                restore_state_write_allowed INTEGER NOT NULL,
                physical_object_move_allowed INTEGER NOT NULL,
                restore_review_window_days INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS soft_delete_safety_blockers (
                blocker_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
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
                INSERT OR REPLACE INTO soft_delete_safety_blockers (
                    blocker_id, label, blocked_action, allowed, reason, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    blocker["blocker_id"],
                    blocker["label"],
                    blocker["blocked_action"],
                    1 if blocker["allowed"] else 0,
                    blocker["reason"],
                    now,
                    now,
                ),
            )

        for row in _candidate_source_rows():
            active_file_id = row["active_file_id"]
            trash_candidate_id = row["trash_candidate_id"]
            execution_id = _soft_delete_execution_id(active_file_id)
            state_id = _soft_delete_state_id(active_file_id)
            lifecycle_event_id = _trash_lifecycle_event_id(active_file_id)

            conn.execute(
                """
                INSERT OR REPLACE INTO owner_soft_delete_approval_execution (
                    soft_delete_execution_id, active_file_id, trash_candidate_id,
                    approval_state, owner_only, approval_executed,
                    controlled_soft_delete_allowed, hard_delete_allowed,
                    purge_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    execution_id,
                    active_file_id,
                    trash_candidate_id,
                    "owner_soft_delete_approval_executed_for_metadata_soft_delete",
                    1,
                    1,
                    1,
                    0,
                    0,
                    now,
                ),
            )

            state_material = {
                "active_file_id": active_file_id,
                "trash_candidate_id": trash_candidate_id,
                "source_hash": row["source_hash"],
                "share_packet_hash": row["share_packet_hash"],
                "soft_deleted": True,
                "hard_delete_allowed": False,
                "purge_allowed": False,
                "restore_execution_allowed": False,
                "physical_object_move_allowed": False,
                "file_body_return_allowed": False,
            }
            state_hash = calculate_sha256_bytes(repr(sorted(state_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO soft_delete_state_records (
                    soft_delete_state_id, active_file_id, trash_candidate_id,
                    lifecycle_state, soft_deleted, soft_deleted_at,
                    retention_days, hard_delete_allowed, purge_allowed,
                    restore_execution_allowed, physical_object_move_allowed,
                    file_body_return_allowed, state_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state_id,
                    active_file_id,
                    trash_candidate_id,
                    "soft_deleted_metadata_only",
                    1,
                    now,
                    SOFT_DELETE_RETENTION_DAYS,
                    0,
                    0,
                    0,
                    0,
                    0,
                    state_hash,
                    now,
                ),
            )

            lifecycle_material = {
                "active_file_id": active_file_id,
                "trash_candidate_id": trash_candidate_id,
                "state_hash": state_hash,
                "event_type": "metadata_soft_delete",
                "metadata_only": True,
                "physical_object_moved": False,
                "hard_deleted": False,
                "purged": False,
            }
            lifecycle_hash = calculate_sha256_bytes(repr(sorted(lifecycle_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO trash_lifecycle_ledger (
                    lifecycle_event_id, active_file_id, trash_candidate_id,
                    event_type, event_state, metadata_only,
                    physical_object_moved, hard_deleted, purged,
                    lifecycle_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lifecycle_event_id,
                    active_file_id,
                    trash_candidate_id,
                    "metadata_soft_delete",
                    "recorded_metadata_soft_delete_no_physical_move",
                    1,
                    0,
                    0,
                    0,
                    lifecycle_hash,
                    now,
                ),
            )

            receipt_material = {
                "active_file_id": active_file_id,
                "trash_candidate_id": trash_candidate_id,
                "soft_delete_state_id": state_id,
                "lifecycle_event_id": lifecycle_event_id,
                "state_hash": state_hash,
                "lifecycle_hash": lifecycle_hash,
                "metadata_only": True,
                "hard_deleted": False,
                "purged": False,
                "physical_object_moved": False,
            }
            receipt_hash = calculate_sha256_bytes(repr(sorted(receipt_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO soft_delete_receipt_finalization_board (
                    final_receipt_id, active_file_id, trash_candidate_id,
                    soft_delete_state_id, lifecycle_event_id,
                    final_receipt_hash, finalized, receipt_scope, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _soft_delete_receipt_id(active_file_id),
                    active_file_id,
                    trash_candidate_id,
                    state_id,
                    lifecycle_event_id,
                    receipt_hash,
                    1,
                    "controlled_metadata_soft_delete_execution",
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO post_delete_access_locks (
                    post_delete_access_lock_id, active_file_id,
                    trash_candidate_id, access_state, preview_allowed,
                    download_allowed, share_allowed, restore_preview_allowed,
                    public_access_allowed, beta_access_allowed,
                    raw_file_bytes_json_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _post_delete_access_lock_id(active_file_id),
                    active_file_id,
                    trash_candidate_id,
                    "post_soft_delete_access_locked_restore_preview_only",
                    0,
                    0,
                    0,
                    1,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO restore_handoff_previews (
                    restore_handoff_preview_id, active_file_id,
                    trash_candidate_id, restore_state,
                    restore_review_required, restore_execution_allowed,
                    restore_state_write_allowed, physical_object_move_allowed,
                    restore_review_window_days, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _restore_handoff_preview_id(active_file_id),
                    active_file_id,
                    trash_candidate_id,
                    "restore_handoff_preview_ready_execution_locked",
                    1,
                    0,
                    0,
                    0,
                    row["restore_review_window_days"],
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_trash_restore_recovery_prep_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP401_INIT_CACHE = dict(result)
    return result


def get_controlled_soft_delete_execution_shell() -> Dict[str, Any]:
    init = initialize_controlled_soft_delete_execution_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 401,
        "title": "Controlled Soft Delete Execution Shell",
        "ready": True,
        "initialized": init,
        "controlled_metadata_soft_delete_execution_allowed": True,
        "hard_delete_allowed": False,
        "purge_allowed": False,
        "restore_execution_allowed": False,
        "physical_object_move_allowed": False,
        "locks": LOCKS,
    }


def get_soft_delete_execution_scope_contract() -> Dict[str, Any]:
    initialize_controlled_soft_delete_execution_layer()
    return {
        "section": SECTION,
        "gp": 402,
        "title": "Soft Delete Execution Scope Contract",
        "ready": True,
        "scope": {
            "controlled_metadata_soft_delete_execution_allowed": True,
            "owner_only": True,
            "metadata_state_write_allowed": True,
            "trash_lifecycle_ledger_allowed": True,
            "soft_delete_receipt_finalization_allowed": True,
            "retention_days": SOFT_DELETE_RETENTION_DAYS,
            "hard_delete_allowed": False,
            "purge_allowed": False,
            "restore_execution_allowed": False,
            "restore_state_write_allowed": False,
            "physical_object_move_allowed": False,
            "physical_object_delete_allowed": False,
            "file_body_return_allowed": False,
            "raw_file_bytes_returned_by_json": False,
            "public_delete_allowed": False,
            "beta_delete_allowed": False,
            "public_restore_allowed": False,
            "beta_restore_allowed": False,
        },
    }


def get_owner_soft_delete_approval_execution_board() -> Dict[str, Any]:
    initialize_controlled_soft_delete_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM owner_soft_delete_approval_execution ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 403,
        "title": "Owner Soft Delete Approval Execution Board",
        "ready": True,
        "approval_execution_count": len(rows),
        "approval_executions": rows,
        "all_owner_only": all(bool(item["owner_only"]) for item in rows),
        "all_approvals_executed": all(bool(item["approval_executed"]) for item in rows),
        "controlled_soft_delete_count": sum(1 for item in rows if bool(item["controlled_soft_delete_allowed"])),
        "no_hard_delete_allowed": all(not bool(item["hard_delete_allowed"]) for item in rows),
        "no_purge_allowed": all(not bool(item["purge_allowed"]) for item in rows),
    }


def get_soft_delete_state_writer() -> Dict[str, Any]:
    initialize_controlled_soft_delete_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM soft_delete_state_records ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 404,
        "title": "Soft Delete State Writer",
        "ready": True,
        "state_record_count": len(rows),
        "state_records": rows,
        "all_records_soft_deleted": all(bool(item["soft_deleted"]) for item in rows),
        "all_hard_delete_locked": all(not bool(item["hard_delete_allowed"]) for item in rows),
        "all_purge_locked": all(not bool(item["purge_allowed"]) for item in rows),
        "all_restore_execution_locked": all(not bool(item["restore_execution_allowed"]) for item in rows),
        "all_physical_object_move_locked": all(not bool(item["physical_object_move_allowed"]) for item in rows),
        "all_file_body_return_locked": all(not bool(item["file_body_return_allowed"]) for item in rows),
    }


def get_trash_lifecycle_ledger() -> Dict[str, Any]:
    initialize_controlled_soft_delete_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM trash_lifecycle_ledger ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 405,
        "title": "Trash Lifecycle Ledger",
        "ready": True,
        "lifecycle_event_count": len(rows),
        "lifecycle_events": rows,
        "all_metadata_only": all(bool(item["metadata_only"]) for item in rows),
        "no_physical_objects_moved": all(not bool(item["physical_object_moved"]) for item in rows),
        "no_hard_deletes": all(not bool(item["hard_deleted"]) for item in rows),
        "no_purges": all(not bool(item["purged"]) for item in rows),
    }


def get_soft_delete_receipt_finalization_board() -> Dict[str, Any]:
    initialize_controlled_soft_delete_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM soft_delete_receipt_finalization_board ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 406,
        "title": "Soft Delete Receipt Finalization Board",
        "ready": True,
        "final_receipt_count": len(rows),
        "final_receipts": rows,
        "all_receipts_finalized": all(bool(item["finalized"]) for item in rows),
    }


def get_post_delete_access_lock_board() -> Dict[str, Any]:
    initialize_controlled_soft_delete_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM post_delete_access_locks ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 407,
        "title": "Post-Delete Access Lock Board",
        "ready": True,
        "access_lock_count": len(rows),
        "access_locks": rows,
        "all_preview_locked": all(not bool(item["preview_allowed"]) for item in rows),
        "all_download_locked": all(not bool(item["download_allowed"]) for item in rows),
        "all_share_locked": all(not bool(item["share_allowed"]) for item in rows),
        "all_restore_preview_allowed": all(bool(item["restore_preview_allowed"]) for item in rows),
        "all_public_beta_locked": all(not bool(item["public_access_allowed"]) and not bool(item["beta_access_allowed"]) for item in rows),
        "all_raw_file_bytes_json_locked": all(not bool(item["raw_file_bytes_json_allowed"]) for item in rows),
    }


def get_restore_handoff_preview_board() -> Dict[str, Any]:
    initialize_controlled_soft_delete_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM restore_handoff_previews ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 408,
        "title": "Restore Handoff Preview Board",
        "ready": True,
        "restore_handoff_count": len(rows),
        "restore_handoffs": rows,
        "all_restore_review_required": all(bool(item["restore_review_required"]) for item in rows),
        "all_restore_execution_locked": all(not bool(item["restore_execution_allowed"]) for item in rows),
        "all_restore_state_write_locked": all(not bool(item["restore_state_write_allowed"]) for item in rows),
        "all_physical_object_move_locked": all(not bool(item["physical_object_move_allowed"]) for item in rows),
    }


def get_soft_delete_safety_blocker_board() -> Dict[str, Any]:
    initialize_controlled_soft_delete_execution_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM soft_delete_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 409,
        "title": "Soft Delete Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_controlled_soft_delete_execution_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_controlled_soft_delete_execution_layer()

    shell = get_controlled_soft_delete_execution_shell()
    scope = get_soft_delete_execution_scope_contract()
    approvals = get_owner_soft_delete_approval_execution_board()
    states = get_soft_delete_state_writer()
    ledger = get_trash_lifecycle_ledger()
    receipts = get_soft_delete_receipt_finalization_board()
    access = get_post_delete_access_lock_board()
    restore = get_restore_handoff_preview_board()
    blockers = get_soft_delete_safety_blocker_board()

    checks = {
        "previous_trash_restore_recovery_prep_ready": init["previous_trash_restore_recovery_prep_ready"] is True,
        "soft_delete_shell_ready": shell["ready"] is True,
        "soft_delete_scope_ready": scope["ready"] is True and scope["scope"]["controlled_metadata_soft_delete_execution_allowed"] is True,
        "scope_hard_delete_purge_locked": scope["scope"]["hard_delete_allowed"] is False and scope["scope"]["purge_allowed"] is False,
        "scope_restore_physical_move_locked": scope["scope"]["restore_execution_allowed"] is False and scope["scope"]["physical_object_move_allowed"] is False,
        "scope_file_body_locked": scope["scope"]["file_body_return_allowed"] is False and scope["scope"]["raw_file_bytes_returned_by_json"] is False,
        "owner_approval_execution_ready": approvals["ready"] is True and approvals["approval_execution_count"] >= 2,
        "controlled_soft_delete_records_written": approvals["controlled_soft_delete_count"] >= 2,
        "approval_hard_delete_purge_locked": approvals["no_hard_delete_allowed"] is True and approvals["no_purge_allowed"] is True,
        "soft_delete_states_ready": states["ready"] is True and states["state_record_count"] >= 2,
        "all_state_records_soft_deleted": states["all_records_soft_deleted"] is True,
        "state_hard_delete_purge_locked": states["all_hard_delete_locked"] is True and states["all_purge_locked"] is True,
        "state_restore_physical_move_locked": states["all_restore_execution_locked"] is True and states["all_physical_object_move_locked"] is True,
        "state_file_body_locked": states["all_file_body_return_locked"] is True,
        "trash_lifecycle_ledger_ready": ledger["ready"] is True and ledger["lifecycle_event_count"] >= 2,
        "lifecycle_metadata_only": ledger["all_metadata_only"] is True,
        "lifecycle_no_physical_delete_or_move": ledger["no_physical_objects_moved"] is True and ledger["no_hard_deletes"] is True and ledger["no_purges"] is True,
        "soft_delete_receipts_finalized": receipts["ready"] is True and receipts["all_receipts_finalized"] is True,
        "post_delete_access_locks_ready": access["ready"] is True and access["access_lock_count"] >= 2,
        "post_delete_preview_download_share_locked": access["all_preview_locked"] is True and access["all_download_locked"] is True and access["all_share_locked"] is True,
        "post_delete_restore_preview_allowed": access["all_restore_preview_allowed"] is True,
        "post_delete_public_beta_raw_locked": access["all_public_beta_locked"] is True and access["all_raw_file_bytes_json_locked"] is True,
        "restore_handoff_preview_ready": restore["ready"] is True and restore["restore_handoff_count"] >= 2,
        "restore_execution_still_locked": restore["all_restore_execution_locked"] is True,
        "restore_state_and_physical_move_locked": restore["all_restore_state_write_locked"] is True and restore["all_physical_object_move_locked"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "hard_delete_purge_still_locked": LOCKS["hard_delete_allowed"] is False and LOCKS["purge_allowed"] is False,
        "restore_execution_still_globally_locked": LOCKS["restore_execution_allowed"] is False,
        "physical_object_move_still_locked": LOCKS["physical_object_move_allowed"] is False,
        "raw_file_bytes_json_still_locked": LOCKS["raw_file_bytes_returned_by_json"] is False,
        "public_beta_lifecycle_still_locked": LOCKS["public_delete_unlocked"] is False and LOCKS["beta_delete_unlocked"] is False and LOCKS["public_restore_unlocked"] is False and LOCKS["beta_restore_unlocked"] is False,
        "provider_not_required": LOCKS["provider_storage_required"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 410,
        "title": "Controlled Soft Delete Execution Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Controlled soft delete execution layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — CONTROLLED RESTORE EXECUTION LAYER / GP411-GP420",
        "still_locked": [
            "no hard delete",
            "no purge",
            "no restore execution",
            "no restore state write",
            "no physical object move",
            "no physical object delete",
            "no file body return",
            "no raw file bytes returned by JSON",
            "no public/beta delete or restore",
            "no quarantine release",
            "no public/beta/provider upload",
            "no external sync",
        ],
    }


def get_controlled_soft_delete_execution_home() -> Dict[str, Any]:
    checkpoint = get_controlled_soft_delete_execution_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_controlled_soft_delete_execution_layer() -> Dict[str, Any]:
    checkpoint = get_controlled_soft_delete_execution_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_trash_restore_recovery_prep_ready"] is True
    assert checkpoint["checks"]["soft_delete_shell_ready"] is True
    assert checkpoint["checks"]["soft_delete_scope_ready"] is True
    assert checkpoint["checks"]["scope_hard_delete_purge_locked"] is True
    assert checkpoint["checks"]["scope_restore_physical_move_locked"] is True
    assert checkpoint["checks"]["scope_file_body_locked"] is True
    assert checkpoint["checks"]["owner_approval_execution_ready"] is True
    assert checkpoint["checks"]["controlled_soft_delete_records_written"] is True
    assert checkpoint["checks"]["approval_hard_delete_purge_locked"] is True
    assert checkpoint["checks"]["soft_delete_states_ready"] is True
    assert checkpoint["checks"]["all_state_records_soft_deleted"] is True
    assert checkpoint["checks"]["state_hard_delete_purge_locked"] is True
    assert checkpoint["checks"]["state_restore_physical_move_locked"] is True
    assert checkpoint["checks"]["state_file_body_locked"] is True
    assert checkpoint["checks"]["trash_lifecycle_ledger_ready"] is True
    assert checkpoint["checks"]["lifecycle_metadata_only"] is True
    assert checkpoint["checks"]["lifecycle_no_physical_delete_or_move"] is True
    assert checkpoint["checks"]["soft_delete_receipts_finalized"] is True
    assert checkpoint["checks"]["post_delete_access_locks_ready"] is True
    assert checkpoint["checks"]["post_delete_preview_download_share_locked"] is True
    assert checkpoint["checks"]["post_delete_restore_preview_allowed"] is True
    assert checkpoint["checks"]["post_delete_public_beta_raw_locked"] is True
    assert checkpoint["checks"]["restore_handoff_preview_ready"] is True
    assert checkpoint["checks"]["restore_execution_still_locked"] is True
    assert checkpoint["checks"]["restore_state_and_physical_move_locked"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["controlled_metadata_soft_delete_execution_allowed"] is True
    assert LOCKS["soft_delete_state_write_allowed"] is True
    assert LOCKS["trash_lifecycle_ledger_allowed"] is True
    assert LOCKS["soft_delete_receipt_finalization_allowed"] is True
    assert LOCKS["post_delete_access_lock_allowed"] is True
    assert LOCKS["restore_handoff_preview_allowed"] is True

    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["restore_state_write_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False
    assert LOCKS["physical_object_delete_allowed"] is False
    assert LOCKS["file_body_return_allowed"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["public_delete_unlocked"] is False
    assert LOCKS["beta_delete_unlocked"] is False
    assert LOCKS["public_restore_unlocked"] is False
    assert LOCKS["beta_restore_unlocked"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["quarantine_object_move_allowed"] is False
    assert LOCKS["public_upload_unlocked"] is False
    assert LOCKS["beta_upload_unlocked"] is False
    assert LOCKS["provider_upload_unlocked"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["external_sync_unlocked"] is False

    return {
        "ok": True,
        "section": SECTION,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(item for item in PACKS if item["gp"] == gp)
    checkpoint = get_controlled_soft_delete_execution_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "controlled_soft_delete_allowed": True,
        "hard_delete_allowed": False,
        "purge_allowed": False,
        "restore_execution_allowed": False,
        "physical_object_move_allowed": False,
        "locks_preserved": True,
    }


def get_gp401_status() -> Dict[str, Any]:
    return _gp_status(401)


def get_gp402_status() -> Dict[str, Any]:
    return _gp_status(402)


def get_gp403_status() -> Dict[str, Any]:
    return _gp_status(403)


def get_gp404_status() -> Dict[str, Any]:
    return _gp_status(404)


def get_gp405_status() -> Dict[str, Any]:
    return _gp_status(405)


def get_gp406_status() -> Dict[str, Any]:
    return _gp_status(406)


def get_gp407_status() -> Dict[str, Any]:
    return _gp_status(407)


def get_gp408_status() -> Dict[str, Any]:
    return _gp_status(408)


def get_gp409_status() -> Dict[str, Any]:
    return _gp_status(409)


def get_gp410_status() -> Dict[str, Any]:
    return _gp_status(410)
