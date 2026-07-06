
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — OWNER FILE REGISTRY PROMOTION EXECUTION LAYER / GP301-GP310"
LAYER_ID = "vault_gp301_310_owner_file_registry_promotion_execution_layer"
READINESS_LABEL = "Owner file registry promotion execution layer ready"

# GP301 repair: prevent pytest/readiness getters from repeatedly rebuilding the whole dependency chain.
_GP301_INIT_CACHE = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_owner_file_registry_promotion_execution_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.owner_file_registry_promotion_lock_layer_service import (
        get_active_file_registry_preview,
        get_promotion_receipt_draft_ledger,
        get_promotion_hash_continuity_board,
        get_quarantine_release_prohibition_board,
        validate_owner_file_registry_promotion_lock_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP301-GP310 requires GP291-GP300 owner file registry promotion lock layer first."
    ) from exc


LOCKS = {
    "owner_file_registry_promotion_execution_layer": True,
    "metadata_only_active_registry_write_allowed": True,
    "registry_promotion_execution_allowed": True,
    "promotion_receipt_finalization_allowed": True,
    "object_body_read_allowed": False,
    "object_body_preview_allowed": False,
    "file_preview_unlocked": False,
    "file_download_unlocked": False,
    "file_share_unlocked": False,
    "file_delete_unlocked": False,
    "file_restore_unlocked": False,
    "quarantine_release_allowed": False,
    "quarantine_object_move_allowed": False,
    "public_upload_unlocked": False,
    "beta_upload_unlocked": False,
    "provider_upload_unlocked": False,
    "provider_storage_required": False,
    "external_sync_unlocked": False,
    "raw_user_upload_endpoint_allowed": False,
}

PACKS = [
    {"gp": 301, "title": "Owner File Registry Promotion Execution Shell", "status": "ready", "route": "/vault/owner-file-registry-promotion-execution-shell.json"},
    {"gp": 302, "title": "Owner Approval Execution Contract", "status": "ready", "route": "/vault/owner-approval-execution-contract.json"},
    {"gp": 303, "title": "Active File Registry Writer", "status": "ready", "route": "/vault/active-file-registry-writer.json"},
    {"gp": 304, "title": "Registry Promotion Execution Ledger", "status": "ready", "route": "/vault/registry-promotion-execution-ledger.json"},
    {"gp": 305, "title": "Promotion Receipt Finalization Board", "status": "ready", "route": "/vault/promotion-receipt-finalization-board.json"},
    {"gp": 306, "title": "Active Registry Hash Continuity Board", "status": "ready", "route": "/vault/active-registry-hash-continuity-board.json"},
    {"gp": 307, "title": "Quarantine Hold After Promotion Contract", "status": "ready", "route": "/vault/quarantine-hold-after-promotion-contract.json"},
    {"gp": 308, "title": "Promotion Execution Rollback Preview", "status": "ready", "route": "/vault/promotion-execution-rollback-preview.json"},
    {"gp": 309, "title": "Promotion Execution Safety Blocker Board", "status": "ready", "route": "/vault/promotion-execution-safety-blocker-board.json"},
    {"gp": 310, "title": "Owner File Registry Promotion Execution Readiness Checkpoint", "status": "ready", "route": "/vault/owner-file-registry-promotion-execution-readiness-checkpoint.json"},
]

BLOCKERS = [
    {
        "blocker_id": "no_object_body_read",
        "label": "Object body read remains locked",
        "blocked_action": "object_body_read",
        "allowed": False,
        "reason": "Active registry promotion writes metadata only and never reads plaintext object bodies.",
    },
    {
        "blocker_id": "no_preview",
        "label": "Preview remains locked",
        "blocked_action": "file_preview",
        "allowed": False,
        "reason": "Safe preview belongs to a later file detail and preview layer.",
    },
    {
        "blocker_id": "no_download",
        "label": "Download remains locked",
        "blocked_action": "file_download",
        "allowed": False,
        "reason": "Download requires later Tower permission and owner approval rules.",
    },
    {
        "blocker_id": "no_share",
        "label": "Sharing remains locked",
        "blocked_action": "file_share",
        "allowed": False,
        "reason": "Sharing belongs to a later share/access layer.",
    },
    {
        "blocker_id": "no_delete",
        "label": "Delete remains locked",
        "blocked_action": "file_delete",
        "allowed": False,
        "reason": "Delete must remain trash/recovery locked.",
    },
    {
        "blocker_id": "no_restore",
        "label": "Restore remains locked",
        "blocked_action": "file_restore",
        "allowed": False,
        "reason": "Restore belongs to a later recovery approval layer.",
    },
    {
        "blocker_id": "no_quarantine_release",
        "label": "Quarantine release remains locked",
        "blocked_action": "quarantine_release",
        "allowed": False,
        "reason": "This layer registers metadata but does not move/release physical objects from quarantine.",
    },
    {
        "blocker_id": "no_quarantine_move",
        "label": "Quarantine object move remains locked",
        "blocked_action": "quarantine_object_move",
        "allowed": False,
        "reason": "Physical object movement belongs to a later controlled release layer.",
    },
    {
        "blocker_id": "no_public_upload",
        "label": "Public upload remains locked",
        "blocked_action": "public_upload",
        "allowed": False,
        "reason": "Registry promotion does not expose public upload.",
    },
    {
        "blocker_id": "no_beta_upload",
        "label": "Beta upload remains locked",
        "blocked_action": "beta_upload",
        "allowed": False,
        "reason": "Beta file upload remains Tower-controlled and locked.",
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
        "reason": "Registry execution does not sync files externally.",
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


def _execution_id(active_file_id: str) -> str:
    return "promotion_exec_" + calculate_sha256_bytes(("exec|" + active_file_id).encode("utf-8"))[:24]


def _final_receipt_id(active_file_id: str) -> str:
    return "promotion_receipt_final_" + calculate_sha256_bytes(("final_receipt|" + active_file_id).encode("utf-8"))[:24]


def _rollback_preview_id(active_file_id: str) -> str:
    return "promotion_rollback_preview_" + calculate_sha256_bytes(("rollback|" + active_file_id).encode("utf-8"))[:24]


def initialize_owner_file_registry_promotion_execution_layer() -> Dict[str, Any]:
    global _GP301_INIT_CACHE
    if _GP301_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP301_INIT_CACHE)

    previous = validate_owner_file_registry_promotion_lock_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS active_file_registry (
                active_file_id TEXT PRIMARY KEY,
                source_candidate_id TEXT NOT NULL,
                source_object_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                safe_stored_name TEXT NOT NULL,
                mission_lane TEXT NOT NULL,
                folder_key TEXT NOT NULL,
                owner_lane TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                sha256_hash TEXT NOT NULL,
                registry_state TEXT NOT NULL,
                metadata_only INTEGER NOT NULL,
                quarantine_held INTEGER NOT NULL,
                object_body_read_locked INTEGER NOT NULL,
                preview_locked INTEGER NOT NULL,
                download_locked INTEGER NOT NULL,
                share_locked INTEGER NOT NULL,
                delete_locked INTEGER NOT NULL,
                restore_locked INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS registry_promotion_execution_ledger (
                execution_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                source_candidate_id TEXT NOT NULL,
                source_object_id TEXT NOT NULL,
                execution_state TEXT NOT NULL,
                metadata_write_executed INTEGER NOT NULL,
                object_body_read_executed INTEGER NOT NULL,
                quarantine_release_executed INTEGER NOT NULL,
                receipt_finalized INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS promotion_receipt_finalization_board (
                final_receipt_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                source_object_id TEXT NOT NULL,
                final_receipt_hash TEXT NOT NULL,
                finalized INTEGER NOT NULL,
                finalization_state TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS active_registry_hash_continuity (
                continuity_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                source_object_id TEXT NOT NULL,
                registry_hash TEXT NOT NULL,
                source_hash TEXT NOT NULL,
                verified INTEGER NOT NULL,
                verified_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quarantine_hold_after_promotion (
                hold_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                source_object_id TEXT NOT NULL,
                quarantine_held INTEGER NOT NULL,
                release_allowed INTEGER NOT NULL,
                object_move_allowed INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS promotion_execution_rollback_previews (
                rollback_preview_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                source_object_id TEXT NOT NULL,
                rollback_available INTEGER NOT NULL,
                rollback_executed INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS promotion_execution_safety_blockers (
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
                INSERT OR REPLACE INTO promotion_execution_safety_blockers (
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

        previews = get_active_file_registry_preview().get("previews", [])

        for item in previews:
            active_file_id = item["active_file_id"]
            source_candidate_id = item["candidate_id"]
            source_object_id = item["object_id"]
            sha256_hash = item["sha256_hash"]

            conn.execute(
                """
                INSERT OR REPLACE INTO active_file_registry (
                    active_file_id, source_candidate_id, source_object_id,
                    original_filename, safe_stored_name, mission_lane, folder_key,
                    owner_lane, size_bytes, mime_type, sha256_hash, registry_state,
                    metadata_only, quarantine_held, object_body_read_locked,
                    preview_locked, download_locked, share_locked, delete_locked,
                    restore_locked, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    active_file_id,
                    source_candidate_id,
                    source_object_id,
                    item["original_filename"],
                    item["safe_stored_name"],
                    item["mission_lane"],
                    item["folder_key"],
                    item["owner_lane"],
                    item["size_bytes"],
                    item["mime_type"],
                    sha256_hash,
                    "active_registered_metadata_only_quarantine_held",
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO registry_promotion_execution_ledger (
                    execution_id, active_file_id, source_candidate_id,
                    source_object_id, execution_state, metadata_write_executed,
                    object_body_read_executed, quarantine_release_executed,
                    receipt_finalized, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _execution_id(active_file_id),
                    active_file_id,
                    source_candidate_id,
                    source_object_id,
                    "metadata_registry_promotion_executed_quarantine_held",
                    1,
                    0,
                    0,
                    1,
                    now,
                    now,
                ),
            )

            final_receipt_material = {
                "active_file_id": active_file_id,
                "source_candidate_id": source_candidate_id,
                "source_object_id": source_object_id,
                "sha256_hash": sha256_hash,
                "registry_state": "active_registered_metadata_only_quarantine_held",
                "metadata_only": True,
                "quarantine_held": True,
                "object_body_read_executed": False,
                "quarantine_release_executed": False,
            }
            final_receipt_hash = calculate_sha256_bytes(
                repr(sorted(final_receipt_material.items())).encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO promotion_receipt_finalization_board (
                    final_receipt_id, active_file_id, source_object_id,
                    final_receipt_hash, finalized, finalization_state, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _final_receipt_id(active_file_id),
                    active_file_id,
                    source_object_id,
                    final_receipt_hash,
                    1,
                    "finalized_metadata_only_promotion_receipt",
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO active_registry_hash_continuity (
                    continuity_id, active_file_id, source_object_id,
                    registry_hash, source_hash, verified, verified_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "active_continuity_" + active_file_id,
                    active_file_id,
                    source_object_id,
                    sha256_hash,
                    sha256_hash,
                    1,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO quarantine_hold_after_promotion (
                    hold_id, active_file_id, source_object_id,
                    quarantine_held, release_allowed, object_move_allowed,
                    reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "quarantine_hold_" + active_file_id,
                    active_file_id,
                    source_object_id,
                    1,
                    0,
                    0,
                    "Metadata promotion completed, but physical object remains quarantine-held.",
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO promotion_execution_rollback_previews (
                    rollback_preview_id, active_file_id, source_object_id,
                    rollback_available, rollback_executed, reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _rollback_preview_id(active_file_id),
                    active_file_id,
                    source_object_id,
                    1,
                    0,
                    "Rollback preview exists for metadata registry entry only; no destructive rollback executed.",
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_promotion_lock_layer_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP301_INIT_CACHE = dict(result)
    return result


def get_owner_file_registry_promotion_execution_shell() -> Dict[str, Any]:
    init = initialize_owner_file_registry_promotion_execution_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 301,
        "title": "Owner File Registry Promotion Execution Shell",
        "ready": True,
        "initialized": init,
        "metadata_only_active_registry_write_allowed": True,
        "object_body_read_allowed": False,
        "quarantine_release_allowed": False,
        "locks": LOCKS,
    }


def get_owner_approval_execution_contract() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_execution_layer()
    return {
        "section": SECTION,
        "gp": 302,
        "title": "Owner Approval Execution Contract",
        "ready": True,
        "contract": {
            "owner_execution_scope": "metadata_registry_promotion_only",
            "approval_mode": "system_locked_owner_foundation_execution",
            "writes_active_metadata_registry": True,
            "finalizes_metadata_promotion_receipt": True,
            "reads_object_body": False,
            "moves_physical_object": False,
            "releases_quarantine": False,
            "unlocks_preview": False,
            "unlocks_download": False,
            "unlocks_share": False,
            "unlocks_delete": False,
        },
    }


def get_active_file_registry_writer() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM active_file_registry ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 303,
        "title": "Active File Registry Writer",
        "ready": True,
        "active_file_count": len(rows),
        "active_files": rows,
        "metadata_only": True,
        "object_body_read_allowed": False,
        "quarantine_held": True,
    }


def get_registry_promotion_execution_ledger() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM registry_promotion_execution_ledger ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 304,
        "title": "Registry Promotion Execution Ledger",
        "ready": True,
        "execution_count": len(rows),
        "executions": rows,
        "all_metadata_writes_executed": all(bool(item["metadata_write_executed"]) for item in rows),
        "no_object_body_reads_executed": all(not bool(item["object_body_read_executed"]) for item in rows),
        "no_quarantine_releases_executed": all(not bool(item["quarantine_release_executed"]) for item in rows),
    }


def get_promotion_receipt_finalization_board() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM promotion_receipt_finalization_board ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 305,
        "title": "Promotion Receipt Finalization Board",
        "ready": True,
        "final_receipt_count": len(rows),
        "final_receipts": rows,
        "all_receipts_finalized": all(bool(item["finalized"]) for item in rows),
        "receipt_scope": "metadata_only_registry_promotion",
    }


def get_active_registry_hash_continuity_board() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM active_registry_hash_continuity ORDER BY verified_at DESC")

    return {
        "section": SECTION,
        "gp": 306,
        "title": "Active Registry Hash Continuity Board",
        "ready": True,
        "continuity_count": len(rows),
        "continuity_rows": rows,
        "all_hash_continuity_verified": all(bool(item["verified"]) for item in rows),
    }


def get_quarantine_hold_after_promotion_contract() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM quarantine_hold_after_promotion ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 307,
        "title": "Quarantine Hold After Promotion Contract",
        "ready": True,
        "hold_count": len(rows),
        "holds": rows,
        "all_objects_quarantine_held": all(bool(item["quarantine_held"]) for item in rows),
        "release_allowed": False,
        "object_move_allowed": False,
    }


def get_promotion_execution_rollback_preview() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM promotion_execution_rollback_previews ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 308,
        "title": "Promotion Execution Rollback Preview",
        "ready": True,
        "rollback_preview_count": len(rows),
        "rollback_previews": rows,
        "rollback_available": True,
        "rollback_executed": False,
        "all_rollbacks_preview_only": all(not bool(item["rollback_executed"]) for item in rows),
    }


def get_promotion_execution_safety_blocker_board() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_execution_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM promotion_execution_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 309,
        "title": "Promotion Execution Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_owner_file_registry_promotion_execution_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_owner_file_registry_promotion_execution_layer()

    shell = get_owner_file_registry_promotion_execution_shell()
    contract = get_owner_approval_execution_contract()
    writer = get_active_file_registry_writer()
    ledger = get_registry_promotion_execution_ledger()
    receipts = get_promotion_receipt_finalization_board()
    continuity = get_active_registry_hash_continuity_board()
    quarantine_hold = get_quarantine_hold_after_promotion_contract()
    rollback = get_promotion_execution_rollback_preview()
    blockers = get_promotion_execution_safety_blocker_board()

    checks = {
        "previous_promotion_lock_layer_ready": init["previous_promotion_lock_layer_ready"] is True,
        "execution_shell_ready": shell["ready"] is True,
        "owner_execution_contract_ready": contract["ready"] is True and contract["contract"]["writes_active_metadata_registry"] is True,
        "active_registry_writer_ready": writer["ready"] is True and writer["active_file_count"] >= 2 and writer["metadata_only"] is True,
        "execution_ledger_ready": ledger["ready"] is True and ledger["all_metadata_writes_executed"] is True,
        "no_object_body_reads_executed": ledger["no_object_body_reads_executed"] is True,
        "no_quarantine_releases_executed": ledger["no_quarantine_releases_executed"] is True,
        "promotion_receipts_finalized": receipts["ready"] is True and receipts["all_receipts_finalized"] is True,
        "active_registry_hash_continuity_ready": continuity["ready"] is True and continuity["all_hash_continuity_verified"] is True,
        "quarantine_hold_ready": quarantine_hold["ready"] is True and quarantine_hold["all_objects_quarantine_held"] is True,
        "rollback_preview_ready": rollback["ready"] is True and rollback["all_rollbacks_preview_only"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "object_body_read_still_locked": LOCKS["object_body_read_allowed"] is False,
        "download_still_locked": LOCKS["file_download_unlocked"] is False,
        "quarantine_release_still_locked": LOCKS["quarantine_release_allowed"] is False,
        "provider_not_required": LOCKS["provider_storage_required"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 310,
        "title": "Owner File Registry Promotion Execution Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Owner file registry promotion execution layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — OWNER FILE DETAIL METADATA VIEW LAYER / GP311-GP320",
        "still_locked": [
            "no object body read",
            "no preview",
            "no download",
            "no sharing",
            "no delete",
            "no restore",
            "no quarantine release",
            "no physical object move",
            "no public upload",
            "no beta upload",
            "no provider upload",
            "no external sync",
        ],
    }


def get_owner_file_registry_promotion_execution_home() -> Dict[str, Any]:
    checkpoint = get_owner_file_registry_promotion_execution_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_owner_file_registry_promotion_execution_layer() -> Dict[str, Any]:
    checkpoint = get_owner_file_registry_promotion_execution_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_promotion_lock_layer_ready"] is True
    assert checkpoint["checks"]["active_registry_writer_ready"] is True
    assert checkpoint["checks"]["execution_ledger_ready"] is True
    assert checkpoint["checks"]["no_object_body_reads_executed"] is True
    assert checkpoint["checks"]["no_quarantine_releases_executed"] is True
    assert checkpoint["checks"]["promotion_receipts_finalized"] is True
    assert checkpoint["checks"]["active_registry_hash_continuity_ready"] is True
    assert checkpoint["checks"]["quarantine_hold_ready"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["metadata_only_active_registry_write_allowed"] is True
    assert LOCKS["registry_promotion_execution_allowed"] is True
    assert LOCKS["promotion_receipt_finalization_allowed"] is True
    assert LOCKS["object_body_read_allowed"] is False
    assert LOCKS["object_body_preview_allowed"] is False
    assert LOCKS["file_preview_unlocked"] is False
    assert LOCKS["file_download_unlocked"] is False
    assert LOCKS["file_share_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["quarantine_object_move_allowed"] is False
    assert LOCKS["public_upload_unlocked"] is False
    assert LOCKS["beta_upload_unlocked"] is False
    assert LOCKS["provider_upload_unlocked"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["external_sync_unlocked"] is False
    assert LOCKS["raw_user_upload_endpoint_allowed"] is False

    return {
        "ok": True,
        "section": SECTION,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(item for item in PACKS if item["gp"] == gp)
    checkpoint = get_owner_file_registry_promotion_execution_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "locks_preserved": True,
        "metadata_registry_write_allowed": True,
        "object_body_read_allowed": False,
        "download_allowed": False,
        "quarantine_release_allowed": False,
    }


def get_gp301_status() -> Dict[str, Any]:
    return _gp_status(301)


def get_gp302_status() -> Dict[str, Any]:
    return _gp_status(302)


def get_gp303_status() -> Dict[str, Any]:
    return _gp_status(303)


def get_gp304_status() -> Dict[str, Any]:
    return _gp_status(304)


def get_gp305_status() -> Dict[str, Any]:
    return _gp_status(305)


def get_gp306_status() -> Dict[str, Any]:
    return _gp_status(306)


def get_gp307_status() -> Dict[str, Any]:
    return _gp_status(307)


def get_gp308_status() -> Dict[str, Any]:
    return _gp_status(308)


def get_gp309_status() -> Dict[str, Any]:
    return _gp_status(309)


def get_gp310_status() -> Dict[str, Any]:
    return _gp_status(310)
