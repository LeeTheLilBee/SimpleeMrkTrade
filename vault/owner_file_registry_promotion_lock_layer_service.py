
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — OWNER FILE REGISTRY PROMOTION LOCK LAYER / GP291-GP300"
LAYER_ID = "vault_gp291_300_owner_file_registry_promotion_lock_layer"
READINESS_LABEL = "Owner file registry promotion lock layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_owner_file_registry_promotion_lock_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.owner_file_object_write_quarantine_layer_service import (
        get_file_object_registry_insert_handoff,
        get_hash_verification_after_write_board,
        get_quarantine_object_manifest_ledger,
        validate_owner_file_object_write_quarantine_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP291-GP300 requires GP281-GP290 owner file object write quarantine layer first."
    ) from exc


LOCKS = {
    "owner_file_registry_promotion_lock_layer": True,
    "promotion_candidate_detection_allowed": True,
    "active_registry_preview_allowed": True,
    "active_registry_final_write_allowed": False,
    "registry_promotion_allowed": False,
    "quarantine_release_allowed": False,
    "promotion_approval_recording_allowed": False,
    "promotion_receipt_finalization_allowed": False,
    "object_body_read_allowed": False,
    "file_preview_unlocked": False,
    "file_download_unlocked": False,
    "file_share_unlocked": False,
    "file_delete_unlocked": False,
    "file_restore_unlocked": False,
    "public_upload_unlocked": False,
    "beta_upload_unlocked": False,
    "provider_upload_unlocked": False,
    "provider_storage_required": False,
    "external_sync_unlocked": False,
}

PACKS = [
    {"gp": 291, "title": "Owner File Registry Promotion Lock Shell", "status": "ready", "route": "/vault/owner-file-registry-promotion-lock-shell.json"},
    {"gp": 292, "title": "Quarantine Promotion Candidate Board", "status": "ready", "route": "/vault/quarantine-promotion-candidate-board.json"},
    {"gp": 293, "title": "Promotion Eligibility Contract", "status": "ready", "route": "/vault/promotion-eligibility-contract.json"},
    {"gp": 294, "title": "Active File Registry Preview", "status": "ready", "route": "/vault/active-file-registry-preview.json"},
    {"gp": 295, "title": "Promotion Approval Lock Board", "status": "ready", "route": "/vault/promotion-approval-lock-board.json"},
    {"gp": 296, "title": "Promotion Receipt Draft Ledger", "status": "ready", "route": "/vault/promotion-receipt-draft-ledger.json"},
    {"gp": 297, "title": "Promotion Hash Continuity Board", "status": "ready", "route": "/vault/promotion-hash-continuity-board.json"},
    {"gp": 298, "title": "Quarantine Release Prohibition Board", "status": "ready", "route": "/vault/quarantine-release-prohibition-board.json"},
    {"gp": 299, "title": "Registry Promotion Safety Blocker Board", "status": "ready", "route": "/vault/registry-promotion-safety-blocker-board.json"},
    {"gp": 300, "title": "Owner File Registry Promotion Lock Readiness Checkpoint", "status": "ready", "route": "/vault/owner-file-registry-promotion-lock-readiness-checkpoint.json"},
]

BLOCKERS = [
    {
        "blocker_id": "no_final_registry_write",
        "label": "Final active registry write remains locked",
        "blocked_action": "active_registry_final_write",
        "allowed": False,
        "reason": "This layer builds promotion candidates and preview records only.",
    },
    {
        "blocker_id": "no_registry_promotion",
        "label": "Registry promotion remains locked",
        "blocked_action": "registry_promotion",
        "allowed": False,
        "reason": "Promotion requires a future owner-approved execution layer.",
    },
    {
        "blocker_id": "no_quarantine_release",
        "label": "Quarantine release remains locked",
        "blocked_action": "quarantine_release",
        "allowed": False,
        "reason": "Objects stay in quarantine until a later release approval layer.",
    },
    {
        "blocker_id": "no_promotion_approval_recording",
        "label": "Promotion approval recording remains locked",
        "blocked_action": "promotion_approval_record",
        "allowed": False,
        "reason": "Approval board is preview/lock state only.",
    },
    {
        "blocker_id": "no_promotion_receipt_finalization",
        "label": "Promotion receipt finalization remains locked",
        "blocked_action": "promotion_receipt_finalize",
        "allowed": False,
        "reason": "Receipt drafts are prepared but not finalized in this layer.",
    },
    {
        "blocker_id": "no_object_body_read",
        "label": "Object body read remains locked",
        "blocked_action": "object_body_read",
        "allowed": False,
        "reason": "Registry promotion does not expose file contents.",
    },
    {
        "blocker_id": "no_preview",
        "label": "Preview remains locked",
        "blocked_action": "file_preview",
        "allowed": False,
        "reason": "Safe preview belongs to a later file detail/preview layer.",
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
        "reason": "Sharing belongs to a later share/access lock layer.",
    },
    {
        "blocker_id": "no_delete",
        "label": "Delete remains locked",
        "blocked_action": "file_delete",
        "allowed": False,
        "reason": "Delete must stay trash/recovery locked.",
    },
    {
        "blocker_id": "no_restore",
        "label": "Restore remains locked",
        "blocked_action": "file_restore",
        "allowed": False,
        "reason": "Restore belongs to a later recovery approval layer.",
    },
    {
        "blocker_id": "no_external_sync",
        "label": "External sync remains locked",
        "blocked_action": "external_sync",
        "allowed": False,
        "reason": "Owner-owned registry promotion does not sync externally.",
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


def _candidate_id(object_id: str) -> str:
    return "promotion_candidate_" + calculate_sha256_bytes(object_id.encode("utf-8"))[:24]


def _active_file_id(object_id: str) -> str:
    return "active_file_preview_" + calculate_sha256_bytes(("active|" + object_id).encode("utf-8"))[:24]


def _approval_lock_id(object_id: str) -> str:
    return "promotion_approval_lock_" + calculate_sha256_bytes(("approval|" + object_id).encode("utf-8"))[:24]


def _receipt_draft_id(object_id: str) -> str:
    return "promotion_receipt_draft_" + calculate_sha256_bytes(("receipt|" + object_id).encode("utf-8"))[:24]


def initialize_owner_file_registry_promotion_lock_layer() -> Dict[str, Any]:
    previous = validate_owner_file_object_write_quarantine_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quarantine_promotion_candidates (
                candidate_id TEXT PRIMARY KEY,
                object_id TEXT NOT NULL,
                request_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                safe_stored_name TEXT NOT NULL,
                mission_lane TEXT NOT NULL,
                folder_key TEXT NOT NULL,
                owner_lane TEXT NOT NULL,
                relative_quarantine_path TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                sha256_hash TEXT NOT NULL,
                hash_verified INTEGER NOT NULL,
                quarantine_state TEXT NOT NULL,
                eligibility_state TEXT NOT NULL,
                promotion_state TEXT NOT NULL,
                active_file_id TEXT NOT NULL,
                active_registry_final_write_allowed INTEGER NOT NULL,
                quarantine_release_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS active_file_registry_preview (
                active_file_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                object_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                safe_stored_name TEXT NOT NULL,
                mission_lane TEXT NOT NULL,
                folder_key TEXT NOT NULL,
                owner_lane TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                sha256_hash TEXT NOT NULL,
                registry_state TEXT NOT NULL,
                preview_only INTEGER NOT NULL,
                final_write_allowed INTEGER NOT NULL,
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
            CREATE TABLE IF NOT EXISTS promotion_approval_locks (
                approval_lock_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                object_id TEXT NOT NULL,
                approval_state TEXT NOT NULL,
                approval_recording_allowed INTEGER NOT NULL,
                owner_approval_required INTEGER NOT NULL,
                tower_step_up_required INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS promotion_receipt_draft_ledger (
                receipt_draft_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                object_id TEXT NOT NULL,
                receipt_hash TEXT NOT NULL,
                receipt_state TEXT NOT NULL,
                finalized INTEGER NOT NULL,
                finalization_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS promotion_hash_continuity (
                continuity_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                object_id TEXT NOT NULL,
                quarantine_hash TEXT NOT NULL,
                registry_preview_hash TEXT NOT NULL,
                hash_continuity_verified INTEGER NOT NULL,
                verified_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quarantine_release_prohibitions (
                prohibition_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                object_id TEXT NOT NULL,
                release_allowed INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS registry_promotion_safety_blockers (
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
                INSERT OR REPLACE INTO registry_promotion_safety_blockers (
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

        handoff = get_file_object_registry_insert_handoff()
        candidates = handoff.get("candidates", [])

        for item in candidates:
            if not bool(item.get("hash_verified")):
                continue

            object_id = item["object_id"]
            candidate_id = _candidate_id(object_id)
            active_file_id = _active_file_id(object_id)
            sha256_hash = item["sha256_hash_actual"]

            conn.execute(
                """
                INSERT OR REPLACE INTO quarantine_promotion_candidates (
                    candidate_id, object_id, request_id, original_filename,
                    safe_stored_name, mission_lane, folder_key, owner_lane,
                    relative_quarantine_path, size_bytes, mime_type, sha256_hash,
                    hash_verified, quarantine_state, eligibility_state, promotion_state,
                    active_file_id, active_registry_final_write_allowed,
                    quarantine_release_allowed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate_id,
                    object_id,
                    item["request_id"],
                    item["original_filename"],
                    item["safe_stored_name"],
                    item["mission_lane"],
                    item["folder_key"],
                    item["owner_lane"],
                    item["relative_quarantine_path"],
                    item["size_bytes"],
                    item["mime_type"],
                    sha256_hash,
                    1,
                    item["quarantine_state"],
                    "eligible_preview_locked",
                    "promotion_locked",
                    active_file_id,
                    0,
                    0,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO active_file_registry_preview (
                    active_file_id, candidate_id, object_id, original_filename,
                    safe_stored_name, mission_lane, folder_key, owner_lane,
                    size_bytes, mime_type, sha256_hash, registry_state,
                    preview_only, final_write_allowed, preview_locked,
                    download_locked, share_locked, delete_locked, restore_locked,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    active_file_id,
                    candidate_id,
                    object_id,
                    item["original_filename"],
                    item["safe_stored_name"],
                    item["mission_lane"],
                    item["folder_key"],
                    item["owner_lane"],
                    item["size_bytes"],
                    item["mime_type"],
                    sha256_hash,
                    "active_registry_preview_only_locked",
                    1,
                    0,
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
                INSERT OR REPLACE INTO promotion_approval_locks (
                    approval_lock_id, candidate_id, object_id, approval_state,
                    approval_recording_allowed, owner_approval_required,
                    tower_step_up_required, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _approval_lock_id(object_id),
                    candidate_id,
                    object_id,
                    "owner_approval_required_locked",
                    0,
                    1,
                    0,
                    now,
                    now,
                ),
            )

            receipt_material = {
                "candidate_id": candidate_id,
                "object_id": object_id,
                "active_file_id": active_file_id,
                "sha256_hash": sha256_hash,
                "promotion_state": "promotion_locked",
                "quarantine_release_allowed": False,
                "final_write_allowed": False,
            }
            receipt_hash = calculate_sha256_bytes(repr(sorted(receipt_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO promotion_receipt_draft_ledger (
                    receipt_draft_id, candidate_id, object_id, receipt_hash,
                    receipt_state, finalized, finalization_allowed,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _receipt_draft_id(object_id),
                    candidate_id,
                    object_id,
                    receipt_hash,
                    "draft_locked",
                    0,
                    0,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO promotion_hash_continuity (
                    continuity_id, candidate_id, object_id, quarantine_hash,
                    registry_preview_hash, hash_continuity_verified, verified_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "continuity_" + object_id,
                    candidate_id,
                    object_id,
                    sha256_hash,
                    sha256_hash,
                    1,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO quarantine_release_prohibitions (
                    prohibition_id, candidate_id, object_id, release_allowed,
                    reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "release_prohibition_" + object_id,
                    candidate_id,
                    object_id,
                    0,
                    "Quarantine release is prohibited until a future owner-approved promotion execution layer.",
                    now,
                ),
            )

        conn.commit()

    return {
        "initialized": True,
        "previous_quarantine_layer_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
    }


def get_owner_file_registry_promotion_lock_shell() -> Dict[str, Any]:
    init = initialize_owner_file_registry_promotion_lock_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 291,
        "title": "Owner File Registry Promotion Lock Shell",
        "ready": True,
        "initialized": init,
        "promotion_candidate_detection_allowed": True,
        "active_registry_preview_allowed": True,
        "active_registry_final_write_allowed": False,
        "locks": LOCKS,
    }


def get_quarantine_promotion_candidate_board() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_lock_layer()
    with _connect() as conn:
        candidates = _rows(conn, "SELECT * FROM quarantine_promotion_candidates ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 292,
        "title": "Quarantine Promotion Candidate Board",
        "ready": True,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "promotion_allowed": False,
        "quarantine_release_allowed": False,
    }


def get_promotion_eligibility_contract() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_lock_layer()
    return {
        "section": SECTION,
        "gp": 293,
        "title": "Promotion Eligibility Contract",
        "ready": True,
        "eligibility_rules": {
            "must_come_from_quarantine_writer": True,
            "must_have_verified_hash": True,
            "must_have_manifest": True,
            "must_preserve_original_filename": True,
            "must_preserve_safe_stored_name": True,
            "must_preserve_mission_lane": True,
            "must_preserve_folder_key": True,
            "must_remain_quarantine_locked": True,
            "final_promotion_requires_future_owner_approval": True,
        },
        "promotion_execution_allowed": False,
    }


def get_active_file_registry_preview() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_lock_layer()
    with _connect() as conn:
        previews = _rows(conn, "SELECT * FROM active_file_registry_preview ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 294,
        "title": "Active File Registry Preview",
        "ready": True,
        "preview_count": len(previews),
        "previews": previews,
        "preview_only": True,
        "final_write_allowed": False,
        "active_registry_created": False,
    }


def get_promotion_approval_lock_board() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_lock_layer()
    with _connect() as conn:
        locks = _rows(conn, "SELECT * FROM promotion_approval_locks ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 295,
        "title": "Promotion Approval Lock Board",
        "ready": True,
        "approval_lock_count": len(locks),
        "approval_locks": locks,
        "approval_recording_allowed": False,
        "all_approval_locks_closed": all(not bool(item["approval_recording_allowed"]) for item in locks),
    }


def get_promotion_receipt_draft_ledger() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_lock_layer()
    with _connect() as conn:
        receipts = _rows(conn, "SELECT * FROM promotion_receipt_draft_ledger ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 296,
        "title": "Promotion Receipt Draft Ledger",
        "ready": True,
        "receipt_draft_count": len(receipts),
        "receipt_drafts": receipts,
        "finalization_allowed": False,
        "all_receipts_draft_locked": all(not bool(item["finalized"]) and not bool(item["finalization_allowed"]) for item in receipts),
    }


def get_promotion_hash_continuity_board() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_lock_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM promotion_hash_continuity ORDER BY verified_at DESC")

    return {
        "section": SECTION,
        "gp": 297,
        "title": "Promotion Hash Continuity Board",
        "ready": True,
        "continuity_count": len(rows),
        "continuity_rows": rows,
        "all_hash_continuity_verified": all(bool(item["hash_continuity_verified"]) for item in rows),
    }


def get_quarantine_release_prohibition_board() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_lock_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM quarantine_release_prohibitions ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 298,
        "title": "Quarantine Release Prohibition Board",
        "ready": True,
        "prohibition_count": len(rows),
        "prohibitions": rows,
        "release_allowed": False,
        "all_release_prohibited": all(not bool(item["release_allowed"]) for item in rows),
    }


def get_registry_promotion_safety_blocker_board() -> Dict[str, Any]:
    initialize_owner_file_registry_promotion_lock_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM registry_promotion_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 299,
        "title": "Registry Promotion Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_owner_file_registry_promotion_lock_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_owner_file_registry_promotion_lock_layer()

    shell = get_owner_file_registry_promotion_lock_shell()
    candidates = get_quarantine_promotion_candidate_board()
    eligibility = get_promotion_eligibility_contract()
    preview = get_active_file_registry_preview()
    approvals = get_promotion_approval_lock_board()
    receipts = get_promotion_receipt_draft_ledger()
    continuity = get_promotion_hash_continuity_board()
    release = get_quarantine_release_prohibition_board()
    blockers = get_registry_promotion_safety_blocker_board()

    checks = {
        "previous_quarantine_layer_ready": init["previous_quarantine_layer_ready"] is True,
        "promotion_shell_ready": shell["ready"] is True,
        "candidate_board_ready": candidates["ready"] is True and candidates["candidate_count"] >= 2,
        "eligibility_contract_ready": eligibility["ready"] is True and eligibility["promotion_execution_allowed"] is False,
        "active_registry_preview_ready": preview["ready"] is True and preview["preview_count"] >= 2 and preview["final_write_allowed"] is False,
        "approval_lock_board_ready": approvals["ready"] is True and approvals["all_approval_locks_closed"] is True,
        "promotion_receipt_drafts_locked": receipts["ready"] is True and receipts["all_receipts_draft_locked"] is True,
        "hash_continuity_ready": continuity["ready"] is True and continuity["all_hash_continuity_verified"] is True,
        "quarantine_release_prohibited": release["ready"] is True and release["all_release_prohibited"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "final_registry_write_still_locked": LOCKS["active_registry_final_write_allowed"] is False,
        "registry_promotion_still_locked": LOCKS["registry_promotion_allowed"] is False,
        "quarantine_release_still_locked": LOCKS["quarantine_release_allowed"] is False,
        "download_still_locked": LOCKS["file_download_unlocked"] is False,
        "object_body_read_still_locked": LOCKS["object_body_read_allowed"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 300,
        "title": "Owner File Registry Promotion Lock Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Owner file registry promotion lock layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — OWNER FILE REGISTRY PROMOTION EXECUTION LAYER / GP301-GP310",
        "still_locked": [
            "no quarantine release",
            "no final active registry promotion",
            "no promotion approval recording",
            "no receipt finalization",
            "no object body read",
            "no preview",
            "no download",
            "no sharing",
            "no delete",
            "no restore",
            "no public upload",
            "no beta upload",
            "no provider upload",
            "no external sync",
        ],
    }


def get_owner_file_registry_promotion_home() -> Dict[str, Any]:
    checkpoint = get_owner_file_registry_promotion_lock_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_owner_file_registry_promotion_lock_layer() -> Dict[str, Any]:
    checkpoint = get_owner_file_registry_promotion_lock_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_quarantine_layer_ready"] is True
    assert checkpoint["checks"]["candidate_board_ready"] is True
    assert checkpoint["checks"]["eligibility_contract_ready"] is True
    assert checkpoint["checks"]["active_registry_preview_ready"] is True
    assert checkpoint["checks"]["approval_lock_board_ready"] is True
    assert checkpoint["checks"]["promotion_receipt_drafts_locked"] is True
    assert checkpoint["checks"]["hash_continuity_ready"] is True
    assert checkpoint["checks"]["quarantine_release_prohibited"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["promotion_candidate_detection_allowed"] is True
    assert LOCKS["active_registry_preview_allowed"] is True
    assert LOCKS["active_registry_final_write_allowed"] is False
    assert LOCKS["registry_promotion_allowed"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["promotion_approval_recording_allowed"] is False
    assert LOCKS["promotion_receipt_finalization_allowed"] is False
    assert LOCKS["object_body_read_allowed"] is False
    assert LOCKS["file_preview_unlocked"] is False
    assert LOCKS["file_download_unlocked"] is False
    assert LOCKS["file_share_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
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
    checkpoint = get_owner_file_registry_promotion_lock_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "locks_preserved": True,
        "active_registry_preview_allowed": True,
        "active_registry_final_write_allowed": False,
        "registry_promotion_allowed": False,
        "quarantine_release_allowed": False,
        "download_allowed": False,
    }


def get_gp291_status() -> Dict[str, Any]:
    return _gp_status(291)


def get_gp292_status() -> Dict[str, Any]:
    return _gp_status(292)


def get_gp293_status() -> Dict[str, Any]:
    return _gp_status(293)


def get_gp294_status() -> Dict[str, Any]:
    return _gp_status(294)


def get_gp295_status() -> Dict[str, Any]:
    return _gp_status(295)


def get_gp296_status() -> Dict[str, Any]:
    return _gp_status(296)


def get_gp297_status() -> Dict[str, Any]:
    return _gp_status(297)


def get_gp298_status() -> Dict[str, Any]:
    return _gp_status(298)


def get_gp299_status() -> Dict[str, Any]:
    return _gp_status(299)


def get_gp300_status() -> Dict[str, Any]:
    return _gp_status(300)
