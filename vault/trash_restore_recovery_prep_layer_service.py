
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — TRASH RESTORE AND RECOVERY PREP LAYER / GP391-GP400"
LAYER_ID = "vault_gp391_400_trash_restore_recovery_prep_layer"
READINESS_LABEL = "Trash restore and recovery prep layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_trash_restore_recovery_prep_layer.sqlite"

SOFT_DELETE_RETENTION_DAYS = 30
RESTORE_REVIEW_WINDOW_DAYS = 7

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.controlled_share_grant_execution_layer_service import (
        get_controlled_share_grant_packet_builder,
        get_share_access_ledger,
        get_share_receipt_finalization_board,
        validate_controlled_share_grant_execution_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP391-GP400 requires GP381-GP390 controlled share grant execution layer first."
    ) from exc


_GP391_INIT_CACHE = None

LOCKS = {
    "trash_restore_recovery_prep_layer": True,
    "trash_eligibility_metadata_allowed": True,
    "soft_delete_scope_policy_allowed": True,
    "restore_scope_policy_allowed": True,
    "owner_trash_approval_lock_allowed": True,
    "restore_eligibility_lock_allowed": True,
    "recovery_receipt_draft_allowed": True,
    "trash_restore_route_payload_draft_allowed": True,
    "soft_delete_execution_allowed": False,
    "hard_delete_allowed": False,
    "purge_allowed": False,
    "restore_execution_allowed": False,
    "physical_object_move_allowed": False,
    "trash_state_write_allowed": False,
    "restore_state_write_allowed": False,
    "file_body_return_allowed": False,
    "raw_file_bytes_returned_by_json": False,
    "public_trash_unlocked": False,
    "beta_trash_unlocked": False,
    "public_restore_unlocked": False,
    "beta_restore_unlocked": False,
    "public_delete_unlocked": False,
    "file_delete_unlocked": False,
    "file_restore_unlocked": False,
    "quarantine_release_allowed": False,
    "quarantine_object_move_allowed": False,
    "public_upload_unlocked": False,
    "beta_upload_unlocked": False,
    "provider_upload_unlocked": False,
    "provider_storage_required": False,
    "external_sync_unlocked": False,
}

PACKS = [
    {"gp": 391, "title": "Trash Restore Recovery Prep Shell", "status": "ready", "route": "/vault/trash-restore-recovery-prep-shell.json"},
    {"gp": 392, "title": "Trash Eligibility Policy Board", "status": "ready", "route": "/vault/trash-eligibility-policy-board.json"},
    {"gp": 393, "title": "Soft Delete Scope Contract", "status": "ready", "route": "/vault/soft-delete-scope-contract.json"},
    {"gp": 394, "title": "Restore Scope Contract", "status": "ready", "route": "/vault/restore-scope-contract.json"},
    {"gp": 395, "title": "Owner Trash Approval Lock Board", "status": "ready", "route": "/vault/owner-trash-approval-lock-board.json"},
    {"gp": 396, "title": "Restore Eligibility Lock Board", "status": "ready", "route": "/vault/restore-eligibility-lock-board.json"},
    {"gp": 397, "title": "Recovery Receipt Draft Ledger", "status": "ready", "route": "/vault/recovery-receipt-draft-ledger.json"},
    {"gp": 398, "title": "Trash Restore Route Payload Draft Builder", "status": "ready", "route": "/vault/trash-restore-route-payload-draft-builder.json"},
    {"gp": 399, "title": "Trash Restore Safety Blocker Board", "status": "ready", "route": "/vault/trash-restore-safety-blocker-board.json"},
    {"gp": 400, "title": "Trash Restore Recovery Prep Readiness Checkpoint", "status": "ready", "route": "/vault/trash-restore-recovery-prep-readiness-checkpoint.json"},
]

BLOCKERS = [
    {
        "blocker_id": "no_soft_delete_execution",
        "label": "Soft delete execution remains locked",
        "blocked_action": "soft_delete_execution",
        "allowed": False,
        "reason": "This layer only prepares trash policy.",
    },
    {
        "blocker_id": "no_hard_delete",
        "label": "Hard delete remains locked",
        "blocked_action": "hard_delete",
        "allowed": False,
        "reason": "Hard delete and purge are not allowed.",
    },
    {
        "blocker_id": "no_purge",
        "label": "Purge remains locked",
        "blocked_action": "purge",
        "allowed": False,
        "reason": "Purge belongs to a much later owner-approved destructive action layer, if ever.",
    },
    {
        "blocker_id": "no_restore_execution",
        "label": "Restore execution remains locked",
        "blocked_action": "restore_execution",
        "allowed": False,
        "reason": "This layer only prepares restore policy.",
    },
    {
        "blocker_id": "no_physical_object_move",
        "label": "Physical object move remains locked",
        "blocked_action": "physical_object_move",
        "allowed": False,
        "reason": "Prep layer does not move stored objects.",
    },
    {
        "blocker_id": "no_trash_state_write",
        "label": "Trash state write remains locked",
        "blocked_action": "trash_state_write",
        "allowed": False,
        "reason": "Trash state mutation belongs to controlled soft delete execution.",
    },
    {
        "blocker_id": "no_restore_state_write",
        "label": "Restore state write remains locked",
        "blocked_action": "restore_state_write",
        "allowed": False,
        "reason": "Restore state mutation belongs to controlled restore execution.",
    },
    {
        "blocker_id": "no_file_body_return",
        "label": "File body return remains locked",
        "blocked_action": "file_body_return",
        "allowed": False,
        "reason": "Trash/restore prep routes are metadata-only.",
    },
    {
        "blocker_id": "no_public_trash_or_restore",
        "label": "Public trash/restore remains locked",
        "blocked_action": "public_trash_restore",
        "allowed": False,
        "reason": "No public lifecycle control exists.",
    },
    {
        "blocker_id": "no_beta_trash_or_restore",
        "label": "Beta trash/restore remains locked",
        "blocked_action": "beta_trash_restore",
        "allowed": False,
        "reason": "No tester lifecycle control exists.",
    },
    {
        "blocker_id": "no_quarantine_release",
        "label": "Quarantine release remains locked",
        "blocked_action": "quarantine_release",
        "allowed": False,
        "reason": "Recovery prep does not release or move quarantine-held objects.",
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
        "reason": "Recovery prep does not sync externally.",
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


def _trash_candidate_id(active_file_id: str) -> str:
    return "trash_candidate_" + calculate_sha256_bytes(("trash_candidate|" + active_file_id).encode("utf-8"))[:24]


def _trash_approval_lock_id(active_file_id: str) -> str:
    return "trash_approval_lock_" + calculate_sha256_bytes(("trash_approval|" + active_file_id).encode("utf-8"))[:24]


def _restore_eligibility_lock_id(active_file_id: str) -> str:
    return "restore_eligibility_lock_" + calculate_sha256_bytes(("restore_eligibility|" + active_file_id).encode("utf-8"))[:24]


def _recovery_receipt_draft_id(active_file_id: str) -> str:
    return "recovery_receipt_draft_" + calculate_sha256_bytes(("recovery_receipt|" + active_file_id).encode("utf-8"))[:24]


def _trash_restore_payload_draft_id(active_file_id: str) -> str:
    return "trash_restore_payload_draft_" + calculate_sha256_bytes(("trash_restore_payload|" + active_file_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    packets = get_controlled_share_grant_packet_builder().get("share_packets", [])
    access_rows = get_share_access_ledger().get("share_access_rows", [])
    receipts = get_share_receipt_finalization_board().get("final_receipts", [])

    access_by_file = {row["active_file_id"]: row for row in access_rows}
    receipt_by_file = {row["active_file_id"]: row for row in receipts}

    rows = []
    for packet in packets:
        active_file_id = packet["active_file_id"]
        access = access_by_file.get(active_file_id, {})
        receipt = receipt_by_file.get(active_file_id, {})
        rows.append(
            {
                "active_file_id": active_file_id,
                "share_candidate_id": packet["share_candidate_id"],
                "share_packet_id": packet["share_packet_id"],
                "original_filename": packet["original_filename"],
                "mime_type": packet["mime_type"],
                "source_hash": packet["source_hash"],
                "verified_hash": packet["verified_hash"],
                "share_packet_hash": packet["share_packet_hash"],
                "share_access_scope": access.get("access_scope", "controlled_future_tower_identity_share_grant"),
                "share_receipt_hash": receipt.get("final_receipt_hash", "share_receipt_not_required_for_recovery_prep"),
                "delete_allowed_upstream": bool(access.get("delete_allowed", 0)),
                "restore_allowed_upstream": bool(access.get("restore_allowed", 0)),
            }
        )
    return rows


def initialize_trash_restore_recovery_prep_layer() -> Dict[str, Any]:
    global _GP391_INIT_CACHE
    if _GP391_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP391_INIT_CACHE)

    previous = validate_controlled_share_grant_execution_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trash_eligibility_candidates (
                trash_candidate_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                share_candidate_id TEXT NOT NULL,
                share_packet_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                source_hash TEXT NOT NULL,
                verified_hash TEXT NOT NULL,
                share_packet_hash TEXT NOT NULL,
                eligibility_state TEXT NOT NULL,
                owner_only INTEGER NOT NULL,
                owner_approval_required INTEGER NOT NULL,
                soft_delete_execution_allowed INTEGER NOT NULL,
                hard_delete_allowed INTEGER NOT NULL,
                purge_allowed INTEGER NOT NULL,
                restore_execution_allowed INTEGER NOT NULL,
                physical_object_move_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS owner_trash_approval_locks (
                approval_lock_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                trash_candidate_id TEXT NOT NULL,
                approval_state TEXT NOT NULL,
                owner_approval_required INTEGER NOT NULL,
                approval_recording_allowed INTEGER NOT NULL,
                soft_delete_execution_allowed INTEGER NOT NULL,
                hard_delete_allowed INTEGER NOT NULL,
                purge_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS restore_eligibility_locks (
                restore_eligibility_lock_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                trash_candidate_id TEXT NOT NULL,
                restore_state TEXT NOT NULL,
                restore_review_required INTEGER NOT NULL,
                restore_execution_allowed INTEGER NOT NULL,
                restore_state_write_allowed INTEGER NOT NULL,
                physical_object_move_allowed INTEGER NOT NULL,
                restore_review_window_days INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recovery_receipt_draft_ledger (
                recovery_receipt_draft_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                trash_candidate_id TEXT NOT NULL,
                receipt_state TEXT NOT NULL,
                finalized INTEGER NOT NULL,
                finalization_allowed INTEGER NOT NULL,
                soft_delete_execution_allowed INTEGER NOT NULL,
                restore_execution_allowed INTEGER NOT NULL,
                receipt_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trash_restore_route_payload_drafts (
                payload_draft_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                trash_candidate_id TEXT NOT NULL,
                route_state TEXT NOT NULL,
                metadata_only INTEGER NOT NULL,
                trash_action_included INTEGER NOT NULL,
                restore_action_included INTEGER NOT NULL,
                purge_action_included INTEGER NOT NULL,
                file_body_included INTEGER NOT NULL,
                physical_path_included INTEGER NOT NULL,
                payload_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trash_restore_safety_blockers (
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
                INSERT OR REPLACE INTO trash_restore_safety_blockers (
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
            trash_candidate_id = _trash_candidate_id(active_file_id)

            conn.execute(
                """
                INSERT OR REPLACE INTO trash_eligibility_candidates (
                    trash_candidate_id, active_file_id, share_candidate_id,
                    share_packet_id, original_filename, mime_type,
                    source_hash, verified_hash, share_packet_hash,
                    eligibility_state, owner_only, owner_approval_required,
                    soft_delete_execution_allowed, hard_delete_allowed,
                    purge_allowed, restore_execution_allowed,
                    physical_object_move_allowed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trash_candidate_id,
                    active_file_id,
                    row["share_candidate_id"],
                    row["share_packet_id"],
                    row["original_filename"],
                    row["mime_type"],
                    row["source_hash"],
                    row["verified_hash"],
                    row["share_packet_hash"],
                    "trash_restore_policy_candidate_owner_approval_required_locked",
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO owner_trash_approval_locks (
                    approval_lock_id, active_file_id, trash_candidate_id,
                    approval_state, owner_approval_required,
                    approval_recording_allowed, soft_delete_execution_allowed,
                    hard_delete_allowed, purge_allowed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _trash_approval_lock_id(active_file_id),
                    active_file_id,
                    trash_candidate_id,
                    "owner_trash_approval_required_locked",
                    1,
                    0,
                    0,
                    0,
                    0,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO restore_eligibility_locks (
                    restore_eligibility_lock_id, active_file_id,
                    trash_candidate_id, restore_state,
                    restore_review_required, restore_execution_allowed,
                    restore_state_write_allowed, physical_object_move_allowed,
                    restore_review_window_days, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _restore_eligibility_lock_id(active_file_id),
                    active_file_id,
                    trash_candidate_id,
                    "restore_eligibility_waiting_for_future_trash_state_locked",
                    1,
                    0,
                    0,
                    0,
                    RESTORE_REVIEW_WINDOW_DAYS,
                    now,
                    now,
                ),
            )

            receipt_material = {
                "active_file_id": active_file_id,
                "trash_candidate_id": trash_candidate_id,
                "share_packet_hash": row["share_packet_hash"],
                "scope": "trash_restore_recovery_prep",
                "soft_delete_execution_allowed": False,
                "hard_delete_allowed": False,
                "purge_allowed": False,
                "restore_execution_allowed": False,
                "physical_object_move_allowed": False,
            }
            receipt_hash = calculate_sha256_bytes(repr(sorted(receipt_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO recovery_receipt_draft_ledger (
                    recovery_receipt_draft_id, active_file_id,
                    trash_candidate_id, receipt_state, finalized,
                    finalization_allowed, soft_delete_execution_allowed,
                    restore_execution_allowed, receipt_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _recovery_receipt_draft_id(active_file_id),
                    active_file_id,
                    trash_candidate_id,
                    "recovery_receipt_draft_locked",
                    0,
                    0,
                    0,
                    0,
                    receipt_hash,
                    now,
                    now,
                ),
            )

            payload_material = {
                "active_file_id": active_file_id,
                "trash_candidate_id": trash_candidate_id,
                "share_packet_hash": row["share_packet_hash"],
                "trash_action_included": False,
                "restore_action_included": False,
                "purge_action_included": False,
                "file_body_included": False,
                "physical_path_included": False,
            }
            payload_hash = calculate_sha256_bytes(repr(sorted(payload_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO trash_restore_route_payload_drafts (
                    payload_draft_id, active_file_id, trash_candidate_id,
                    route_state, metadata_only, trash_action_included,
                    restore_action_included, purge_action_included,
                    file_body_included, physical_path_included,
                    payload_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _trash_restore_payload_draft_id(active_file_id),
                    active_file_id,
                    trash_candidate_id,
                    "trash_restore_route_payload_draft_locked_metadata_only",
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    payload_hash,
                    now,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_controlled_share_grant_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP391_INIT_CACHE = dict(result)
    return result


def get_trash_restore_recovery_prep_shell() -> Dict[str, Any]:
    init = initialize_trash_restore_recovery_prep_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 391,
        "title": "Trash Restore Recovery Prep Shell",
        "ready": True,
        "initialized": init,
        "trash_restore_policy_prep_allowed": True,
        "soft_delete_execution_allowed": False,
        "restore_execution_allowed": False,
        "hard_delete_allowed": False,
        "purge_allowed": False,
        "locks": LOCKS,
    }


def get_trash_eligibility_policy_board() -> Dict[str, Any]:
    initialize_trash_restore_recovery_prep_layer()
    with _connect() as conn:
        candidates = _rows(conn, "SELECT * FROM trash_eligibility_candidates ORDER BY original_filename")

    return {
        "section": SECTION,
        "gp": 392,
        "title": "Trash Eligibility Policy Board",
        "ready": True,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "all_candidates_owner_only": all(bool(item["owner_only"]) for item in candidates),
        "all_owner_approval_required": all(bool(item["owner_approval_required"]) for item in candidates),
        "no_soft_delete_execution_allowed": all(not bool(item["soft_delete_execution_allowed"]) for item in candidates),
        "no_hard_delete_allowed": all(not bool(item["hard_delete_allowed"]) for item in candidates),
        "no_purge_allowed": all(not bool(item["purge_allowed"]) for item in candidates),
        "no_restore_execution_allowed": all(not bool(item["restore_execution_allowed"]) for item in candidates),
        "no_physical_object_move_allowed": all(not bool(item["physical_object_move_allowed"]) for item in candidates),
    }


def get_soft_delete_scope_contract() -> Dict[str, Any]:
    initialize_trash_restore_recovery_prep_layer()
    return {
        "section": SECTION,
        "gp": 393,
        "title": "Soft Delete Scope Contract",
        "ready": True,
        "scope": {
            "owner_only_trash_prep": True,
            "owner_approval_required": True,
            "soft_delete_execution_allowed": False,
            "trash_state_write_allowed": False,
            "hard_delete_allowed": False,
            "purge_allowed": False,
            "physical_object_move_allowed": False,
            "public_trash_allowed": False,
            "beta_trash_allowed": False,
            "file_body_return_allowed": False,
            "soft_delete_retention_days": SOFT_DELETE_RETENTION_DAYS,
        },
    }


def get_restore_scope_contract() -> Dict[str, Any]:
    initialize_trash_restore_recovery_prep_layer()
    return {
        "section": SECTION,
        "gp": 394,
        "title": "Restore Scope Contract",
        "ready": True,
        "scope": {
            "owner_only_restore_prep": True,
            "restore_review_required": True,
            "restore_execution_allowed": False,
            "restore_state_write_allowed": False,
            "physical_object_move_allowed": False,
            "public_restore_allowed": False,
            "beta_restore_allowed": False,
            "file_body_return_allowed": False,
            "restore_review_window_days": RESTORE_REVIEW_WINDOW_DAYS,
        },
    }


def get_owner_trash_approval_lock_board() -> Dict[str, Any]:
    initialize_trash_restore_recovery_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM owner_trash_approval_locks ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 395,
        "title": "Owner Trash Approval Lock Board",
        "ready": True,
        "approval_lock_count": len(rows),
        "approval_locks": rows,
        "all_owner_approval_required": all(bool(item["owner_approval_required"]) for item in rows),
        "all_approval_recording_locked": all(not bool(item["approval_recording_allowed"]) for item in rows),
        "all_soft_delete_execution_locked": all(not bool(item["soft_delete_execution_allowed"]) for item in rows),
        "all_hard_delete_locked": all(not bool(item["hard_delete_allowed"]) for item in rows),
        "all_purge_locked": all(not bool(item["purge_allowed"]) for item in rows),
    }


def get_restore_eligibility_lock_board() -> Dict[str, Any]:
    initialize_trash_restore_recovery_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM restore_eligibility_locks ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 396,
        "title": "Restore Eligibility Lock Board",
        "ready": True,
        "restore_lock_count": len(rows),
        "restore_locks": rows,
        "all_restore_review_required": all(bool(item["restore_review_required"]) for item in rows),
        "all_restore_execution_locked": all(not bool(item["restore_execution_allowed"]) for item in rows),
        "all_restore_state_write_locked": all(not bool(item["restore_state_write_allowed"]) for item in rows),
        "all_physical_object_move_locked": all(not bool(item["physical_object_move_allowed"]) for item in rows),
    }


def get_recovery_receipt_draft_ledger() -> Dict[str, Any]:
    initialize_trash_restore_recovery_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM recovery_receipt_draft_ledger ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 397,
        "title": "Recovery Receipt Draft Ledger",
        "ready": True,
        "receipt_draft_count": len(rows),
        "receipt_drafts": rows,
        "all_receipts_draft_locked": all(not bool(item["finalized"]) and not bool(item["finalization_allowed"]) for item in rows),
        "all_soft_delete_execution_locked": all(not bool(item["soft_delete_execution_allowed"]) for item in rows),
        "all_restore_execution_locked": all(not bool(item["restore_execution_allowed"]) for item in rows),
    }


def get_trash_restore_route_payload_draft_builder() -> Dict[str, Any]:
    initialize_trash_restore_recovery_prep_layer()
    with _connect() as conn:
        drafts = _rows(conn, "SELECT * FROM trash_restore_route_payload_drafts ORDER BY created_at DESC")

    payloads = []
    for item in drafts:
        payloads.append(
            {
                "payload_draft_id": item["payload_draft_id"],
                "active_file_id": item["active_file_id"],
                "trash_candidate_id": item["trash_candidate_id"],
                "route_state": item["route_state"],
                "metadata_only": bool(item["metadata_only"]),
                "display": {
                    "trash_action": "LOCKED",
                    "restore_action": "LOCKED",
                    "purge_action": "LOCKED",
                    "file_body": "LOCKED",
                    "physical_path": "LOCKED",
                },
                "locks": {
                    "trash_action_included": bool(item["trash_action_included"]),
                    "restore_action_included": bool(item["restore_action_included"]),
                    "purge_action_included": bool(item["purge_action_included"]),
                    "file_body_included": bool(item["file_body_included"]),
                    "physical_path_included": bool(item["physical_path_included"]),
                },
                "payload_hash": item["payload_hash"],
            }
        )

    return {
        "section": SECTION,
        "gp": 398,
        "title": "Trash Restore Route Payload Draft Builder",
        "ready": True,
        "payload_draft_count": len(payloads),
        "payload_drafts": payloads,
        "metadata_only": True,
        "trash_action_included": False,
        "restore_action_included": False,
        "purge_action_included": False,
        "file_body_included": False,
        "physical_path_included": False,
    }


def get_trash_restore_safety_blocker_board() -> Dict[str, Any]:
    initialize_trash_restore_recovery_prep_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM trash_restore_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 399,
        "title": "Trash Restore Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_trash_restore_recovery_prep_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_trash_restore_recovery_prep_layer()

    shell = get_trash_restore_recovery_prep_shell()
    eligibility = get_trash_eligibility_policy_board()
    soft_delete = get_soft_delete_scope_contract()
    restore = get_restore_scope_contract()
    approvals = get_owner_trash_approval_lock_board()
    restore_locks = get_restore_eligibility_lock_board()
    receipts = get_recovery_receipt_draft_ledger()
    payloads = get_trash_restore_route_payload_draft_builder()
    blockers = get_trash_restore_safety_blocker_board()

    checks = {
        "previous_controlled_share_grant_ready": init["previous_controlled_share_grant_ready"] is True,
        "trash_restore_shell_ready": shell["ready"] is True,
        "trash_eligibility_ready": eligibility["ready"] is True and eligibility["candidate_count"] >= 2,
        "trash_candidates_owner_only": eligibility["all_candidates_owner_only"] is True,
        "trash_candidates_approval_required": eligibility["all_owner_approval_required"] is True,
        "soft_delete_locked_on_candidates": eligibility["no_soft_delete_execution_allowed"] is True,
        "hard_delete_and_purge_locked_on_candidates": eligibility["no_hard_delete_allowed"] is True and eligibility["no_purge_allowed"] is True,
        "restore_locked_on_candidates": eligibility["no_restore_execution_allowed"] is True,
        "physical_object_move_locked_on_candidates": eligibility["no_physical_object_move_allowed"] is True,
        "soft_delete_scope_ready": soft_delete["ready"] is True and soft_delete["scope"]["soft_delete_execution_allowed"] is False,
        "soft_delete_scope_hard_delete_purge_locked": soft_delete["scope"]["hard_delete_allowed"] is False and soft_delete["scope"]["purge_allowed"] is False,
        "restore_scope_ready": restore["ready"] is True and restore["scope"]["restore_execution_allowed"] is False,
        "restore_scope_physical_move_locked": restore["scope"]["physical_object_move_allowed"] is False,
        "owner_trash_approval_locks_ready": approvals["ready"] is True and approvals["all_soft_delete_execution_locked"] is True,
        "owner_trash_hard_delete_purge_locked": approvals["all_hard_delete_locked"] is True and approvals["all_purge_locked"] is True,
        "restore_eligibility_locks_ready": restore_locks["ready"] is True and restore_locks["all_restore_execution_locked"] is True,
        "restore_state_and_physical_move_locked": restore_locks["all_restore_state_write_locked"] is True and restore_locks["all_physical_object_move_locked"] is True,
        "recovery_receipt_drafts_ready": receipts["ready"] is True and receipts["receipt_draft_count"] >= 2,
        "recovery_receipts_draft_locked": receipts["all_receipts_draft_locked"] is True,
        "trash_restore_payload_drafts_ready": payloads["ready"] is True and payloads["payload_draft_count"] >= 2,
        "trash_restore_payloads_metadata_only": payloads["metadata_only"] is True,
        "trash_restore_payload_actions_locked": payloads["trash_action_included"] is False and payloads["restore_action_included"] is False and payloads["purge_action_included"] is False,
        "trash_restore_payload_body_path_locked": payloads["file_body_included"] is False and payloads["physical_path_included"] is False,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "soft_delete_execution_still_locked": LOCKS["soft_delete_execution_allowed"] is False,
        "hard_delete_purge_still_locked": LOCKS["hard_delete_allowed"] is False and LOCKS["purge_allowed"] is False,
        "restore_execution_still_locked": LOCKS["restore_execution_allowed"] is False,
        "physical_object_move_still_locked": LOCKS["physical_object_move_allowed"] is False,
        "state_writes_still_locked": LOCKS["trash_state_write_allowed"] is False and LOCKS["restore_state_write_allowed"] is False,
        "raw_file_bytes_json_still_locked": LOCKS["raw_file_bytes_returned_by_json"] is False,
        "public_beta_lifecycle_still_locked": LOCKS["public_trash_unlocked"] is False and LOCKS["beta_trash_unlocked"] is False and LOCKS["public_restore_unlocked"] is False and LOCKS["beta_restore_unlocked"] is False,
        "quarantine_release_still_locked": LOCKS["quarantine_release_allowed"] is False,
        "provider_not_required": LOCKS["provider_storage_required"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 400,
        "title": "Trash Restore Recovery Prep Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Trash restore and recovery prep layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — CONTROLLED SOFT DELETE EXECUTION LAYER / GP401-GP410",
        "still_locked": [
            "no soft delete execution",
            "no hard delete",
            "no purge",
            "no restore execution",
            "no physical object move",
            "no trash state write",
            "no restore state write",
            "no file body return",
            "no raw file bytes returned by JSON",
            "no public/beta trash or restore",
            "no quarantine release",
            "no public/beta/provider upload",
            "no external sync",
        ],
    }


def get_trash_restore_recovery_prep_home() -> Dict[str, Any]:
    checkpoint = get_trash_restore_recovery_prep_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_trash_restore_recovery_prep_layer() -> Dict[str, Any]:
    checkpoint = get_trash_restore_recovery_prep_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_controlled_share_grant_ready"] is True
    assert checkpoint["checks"]["trash_restore_shell_ready"] is True
    assert checkpoint["checks"]["trash_eligibility_ready"] is True
    assert checkpoint["checks"]["trash_candidates_owner_only"] is True
    assert checkpoint["checks"]["trash_candidates_approval_required"] is True
    assert checkpoint["checks"]["soft_delete_locked_on_candidates"] is True
    assert checkpoint["checks"]["hard_delete_and_purge_locked_on_candidates"] is True
    assert checkpoint["checks"]["restore_locked_on_candidates"] is True
    assert checkpoint["checks"]["physical_object_move_locked_on_candidates"] is True
    assert checkpoint["checks"]["soft_delete_scope_ready"] is True
    assert checkpoint["checks"]["soft_delete_scope_hard_delete_purge_locked"] is True
    assert checkpoint["checks"]["restore_scope_ready"] is True
    assert checkpoint["checks"]["restore_scope_physical_move_locked"] is True
    assert checkpoint["checks"]["owner_trash_approval_locks_ready"] is True
    assert checkpoint["checks"]["owner_trash_hard_delete_purge_locked"] is True
    assert checkpoint["checks"]["restore_eligibility_locks_ready"] is True
    assert checkpoint["checks"]["restore_state_and_physical_move_locked"] is True
    assert checkpoint["checks"]["recovery_receipt_drafts_ready"] is True
    assert checkpoint["checks"]["recovery_receipts_draft_locked"] is True
    assert checkpoint["checks"]["trash_restore_payload_drafts_ready"] is True
    assert checkpoint["checks"]["trash_restore_payloads_metadata_only"] is True
    assert checkpoint["checks"]["trash_restore_payload_actions_locked"] is True
    assert checkpoint["checks"]["trash_restore_payload_body_path_locked"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["trash_eligibility_metadata_allowed"] is True
    assert LOCKS["soft_delete_scope_policy_allowed"] is True
    assert LOCKS["restore_scope_policy_allowed"] is True
    assert LOCKS["owner_trash_approval_lock_allowed"] is True
    assert LOCKS["restore_eligibility_lock_allowed"] is True
    assert LOCKS["recovery_receipt_draft_allowed"] is True
    assert LOCKS["trash_restore_route_payload_draft_allowed"] is True

    assert LOCKS["soft_delete_execution_allowed"] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False
    assert LOCKS["trash_state_write_allowed"] is False
    assert LOCKS["restore_state_write_allowed"] is False
    assert LOCKS["file_body_return_allowed"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["public_trash_unlocked"] is False
    assert LOCKS["beta_trash_unlocked"] is False
    assert LOCKS["public_restore_unlocked"] is False
    assert LOCKS["beta_restore_unlocked"] is False
    assert LOCKS["public_delete_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
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
    checkpoint = get_trash_restore_recovery_prep_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "recovery_prep_allowed": True,
        "soft_delete_execution_allowed": False,
        "restore_execution_allowed": False,
        "hard_delete_allowed": False,
        "purge_allowed": False,
        "locks_preserved": True,
    }


def get_gp391_status() -> Dict[str, Any]:
    return _gp_status(391)


def get_gp392_status() -> Dict[str, Any]:
    return _gp_status(392)


def get_gp393_status() -> Dict[str, Any]:
    return _gp_status(393)


def get_gp394_status() -> Dict[str, Any]:
    return _gp_status(394)


def get_gp395_status() -> Dict[str, Any]:
    return _gp_status(395)


def get_gp396_status() -> Dict[str, Any]:
    return _gp_status(396)


def get_gp397_status() -> Dict[str, Any]:
    return _gp_status(397)


def get_gp398_status() -> Dict[str, Any]:
    return _gp_status(398)


def get_gp399_status() -> Dict[str, Any]:
    return _gp_status(399)


def get_gp400_status() -> Dict[str, Any]:
    return _gp_status(400)
