
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — OWNER DOWNLOAD LOCK PREP LAYER / GP351-GP360"
LAYER_ID = "vault_gp351_360_owner_download_lock_prep_layer"
READINESS_LABEL = "Owner download lock prep layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_owner_download_lock_prep_layer.sqlite"

DEFAULT_DOWNLOAD_TTL_SECONDS = 900
MAX_DOWNLOAD_TTL_SECONDS = 1800

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.owner_safe_preview_lock_prep_layer_service import get_preview_eligibility_policy_board
    from vault.controlled_owner_safe_preview_execution_layer_service import (
        get_safe_preview_artifact_builder,
        get_preview_access_ledger,
        get_preview_receipt_finalization_board,
        validate_controlled_owner_safe_preview_execution_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP351-GP360 requires GP341-GP350 controlled owner safe preview execution layer first."
    ) from exc


_GP351_INIT_CACHE = None

LOCKS = {
    "owner_download_lock_prep_layer": True,
    "download_eligibility_metadata_allowed": True,
    "download_scope_policy_allowed": True,
    "owner_download_approval_lock_allowed": True,
    "download_expiration_policy_allowed": True,
    "download_route_payload_draft_allowed": True,
    "download_receipt_draft_allowed": True,
    "download_safety_review_queue_allowed": True,
    "download_execution_allowed": False,
    "download_url_creation_allowed": False,
    "download_token_creation_allowed": False,
    "download_streaming_allowed": False,
    "download_file_body_return_allowed": False,
    "public_download_unlocked": False,
    "beta_download_unlocked": False,
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
}

PACKS = [
    {"gp": 351, "title": "Owner Download Lock Prep Shell", "status": "ready", "route": "/vault/owner-download-lock-prep-shell.json"},
    {"gp": 352, "title": "Download Eligibility Policy Board", "status": "ready", "route": "/vault/download-eligibility-policy-board.json"},
    {"gp": 353, "title": "Download Scope Contract", "status": "ready", "route": "/vault/download-scope-contract.json"},
    {"gp": 354, "title": "Owner Download Approval Lock Board", "status": "ready", "route": "/vault/owner-download-approval-lock-board.json"},
    {"gp": 355, "title": "Download Expiration Policy Board", "status": "ready", "route": "/vault/download-expiration-policy-board.json"},
    {"gp": 356, "title": "Download Route Payload Draft Builder", "status": "ready", "route": "/vault/download-route-payload-draft-builder.json"},
    {"gp": 357, "title": "Download Receipt Draft Ledger", "status": "ready", "route": "/vault/download-receipt-draft-ledger.json"},
    {"gp": 358, "title": "Download Safety Review Queue", "status": "ready", "route": "/vault/download-safety-review-queue.json"},
    {"gp": 359, "title": "Download Safety Blocker Board", "status": "ready", "route": "/vault/download-safety-blocker-board.json"},
    {"gp": 360, "title": "Owner Download Lock Prep Readiness Checkpoint", "status": "ready", "route": "/vault/owner-download-lock-prep-readiness-checkpoint.json"},
]

BLOCKERS = [
    {
        "blocker_id": "no_download_execution",
        "label": "Download execution remains locked",
        "blocked_action": "download_execution",
        "allowed": False,
        "reason": "This layer only prepares owner download policy.",
    },
    {
        "blocker_id": "no_download_url_creation",
        "label": "Download URL creation remains locked",
        "blocked_action": "download_url_creation",
        "allowed": False,
        "reason": "No signed URL or route URL is created in this layer.",
    },
    {
        "blocker_id": "no_download_token_creation",
        "label": "Download token creation remains locked",
        "blocked_action": "download_token_creation",
        "allowed": False,
        "reason": "Download tokens belong to controlled execution later.",
    },
    {
        "blocker_id": "no_download_streaming",
        "label": "Download streaming remains locked",
        "blocked_action": "download_streaming",
        "allowed": False,
        "reason": "No file body is streamed or returned.",
    },
    {
        "blocker_id": "no_file_body_return",
        "label": "File body return remains locked",
        "blocked_action": "file_body_return",
        "allowed": False,
        "reason": "Download prep never returns raw file bytes.",
    },
    {
        "blocker_id": "no_public_download",
        "label": "Public download remains locked",
        "blocked_action": "public_download",
        "allowed": False,
        "reason": "Downloads must be owner-only first.",
    },
    {
        "blocker_id": "no_beta_download",
        "label": "Beta download remains locked",
        "blocked_action": "beta_download",
        "allowed": False,
        "reason": "Beta/tester download is not unlocked in this layer.",
    },
    {
        "blocker_id": "no_share",
        "label": "Sharing remains locked",
        "blocked_action": "file_share",
        "allowed": False,
        "reason": "Sharing belongs to a later Tower-gated share layer.",
    },
    {
        "blocker_id": "no_delete",
        "label": "Delete remains locked",
        "blocked_action": "file_delete",
        "allowed": False,
        "reason": "Delete remains trash/recovery locked.",
    },
    {
        "blocker_id": "no_restore",
        "label": "Restore remains locked",
        "blocked_action": "file_restore",
        "allowed": False,
        "reason": "Restore belongs to a later recovery layer.",
    },
    {
        "blocker_id": "no_quarantine_release",
        "label": "Quarantine release remains locked",
        "blocked_action": "quarantine_release",
        "allowed": False,
        "reason": "Download prep does not move or release physical objects.",
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
        "reason": "Download prep does not sync externally.",
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


def _download_candidate_id(active_file_id: str) -> str:
    return "download_candidate_" + calculate_sha256_bytes(("download_candidate|" + active_file_id).encode("utf-8"))[:24]


def _download_approval_lock_id(active_file_id: str) -> str:
    return "download_approval_lock_" + calculate_sha256_bytes(("download_approval|" + active_file_id).encode("utf-8"))[:24]


def _download_payload_draft_id(active_file_id: str) -> str:
    return "download_payload_draft_" + calculate_sha256_bytes(("download_payload|" + active_file_id).encode("utf-8"))[:24]


def _download_receipt_draft_id(active_file_id: str) -> str:
    return "download_receipt_draft_" + calculate_sha256_bytes(("download_receipt|" + active_file_id).encode("utf-8"))[:24]


def _download_review_id(active_file_id: str) -> str:
    return "download_review_" + calculate_sha256_bytes(("download_review|" + active_file_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    eligibility_rows = get_preview_eligibility_policy_board().get("candidates", [])
    artifacts = get_safe_preview_artifact_builder().get("artifacts", [])
    access_rows = get_preview_access_ledger().get("access_rows", [])
    receipts = get_preview_receipt_finalization_board().get("final_receipts", [])

    artifact_by_file = {row["active_file_id"]: row for row in artifacts}
    access_by_file = {row["active_file_id"]: row for row in access_rows}
    receipt_by_file = {row["active_file_id"]: row for row in receipts}

    merged = []
    for row in eligibility_rows:
        active_file_id = row["active_file_id"]
        merged.append(
            {
                "active_file_id": active_file_id,
                "eligibility_id": row["eligibility_id"],
                "original_filename": row["original_filename"],
                "safe_stored_name": row["safe_stored_name"],
                "folder_key": row["folder_key"],
                "mission_lane": row["mission_lane"],
                "owner_lane": row["owner_lane"],
                "size_bytes": row["size_bytes"],
                "mime_type": row["mime_type"],
                "sha256_hash": row["sha256_hash"],
                "preview_artifact_id": artifact_by_file.get(active_file_id, {}).get("preview_artifact_id", "preview_not_required_for_download_prep"),
                "preview_access_scope": access_by_file.get(active_file_id, {}).get("access_scope", "owner_only_controlled_safe_preview"),
                "preview_receipt_hash": receipt_by_file.get(active_file_id, {}).get("final_receipt_hash", "preview_receipt_not_required_for_download_prep"),
            }
        )
    return merged


def initialize_owner_download_lock_prep_layer() -> Dict[str, Any]:
    global _GP351_INIT_CACHE
    if _GP351_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP351_INIT_CACHE)

    previous = validate_controlled_owner_safe_preview_execution_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_eligibility_candidates (
                download_candidate_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                eligibility_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                safe_stored_name TEXT NOT NULL,
                folder_key TEXT NOT NULL,
                mission_lane TEXT NOT NULL,
                owner_lane TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                sha256_hash TEXT NOT NULL,
                preview_artifact_id TEXT NOT NULL,
                eligibility_state TEXT NOT NULL,
                owner_only INTEGER NOT NULL,
                owner_approval_required INTEGER NOT NULL,
                download_execution_allowed INTEGER NOT NULL,
                download_url_created INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS owner_download_approval_locks (
                approval_lock_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                download_candidate_id TEXT NOT NULL,
                approval_state TEXT NOT NULL,
                owner_approval_required INTEGER NOT NULL,
                approval_recording_allowed INTEGER NOT NULL,
                download_execution_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_expiration_policies (
                policy_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                download_candidate_id TEXT NOT NULL,
                ttl_seconds INTEGER NOT NULL,
                max_ttl_seconds INTEGER NOT NULL,
                one_time_download_required INTEGER NOT NULL,
                expiration_enforced INTEGER NOT NULL,
                token_creation_allowed INTEGER NOT NULL,
                download_execution_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_route_payload_drafts (
                payload_draft_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                download_candidate_id TEXT NOT NULL,
                route_state TEXT NOT NULL,
                metadata_only INTEGER NOT NULL,
                download_url_included INTEGER NOT NULL,
                download_token_included INTEGER NOT NULL,
                file_body_included INTEGER NOT NULL,
                payload_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_receipt_draft_ledger (
                receipt_draft_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                download_candidate_id TEXT NOT NULL,
                receipt_state TEXT NOT NULL,
                finalized INTEGER NOT NULL,
                finalization_allowed INTEGER NOT NULL,
                receipt_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_safety_review_queue (
                review_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                download_candidate_id TEXT NOT NULL,
                review_state TEXT NOT NULL,
                reviewer_action_allowed INTEGER NOT NULL,
                download_execution_allowed INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_safety_blockers (
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
                INSERT OR REPLACE INTO download_safety_blockers (
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
            download_candidate_id = _download_candidate_id(active_file_id)

            conn.execute(
                """
                INSERT OR REPLACE INTO download_eligibility_candidates (
                    download_candidate_id, active_file_id, eligibility_id,
                    original_filename, safe_stored_name, folder_key,
                    mission_lane, owner_lane, size_bytes, mime_type,
                    sha256_hash, preview_artifact_id, eligibility_state,
                    owner_only, owner_approval_required, download_execution_allowed,
                    download_url_created, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    download_candidate_id,
                    active_file_id,
                    row["eligibility_id"],
                    row["original_filename"],
                    row["safe_stored_name"],
                    row["folder_key"],
                    row["mission_lane"],
                    row["owner_lane"],
                    row["size_bytes"],
                    row["mime_type"],
                    row["sha256_hash"],
                    row["preview_artifact_id"],
                    "download_policy_candidate_owner_approval_required_locked",
                    1,
                    1,
                    0,
                    0,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO owner_download_approval_locks (
                    approval_lock_id, active_file_id, download_candidate_id,
                    approval_state, owner_approval_required,
                    approval_recording_allowed, download_execution_allowed,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _download_approval_lock_id(active_file_id),
                    active_file_id,
                    download_candidate_id,
                    "owner_download_approval_required_locked",
                    1,
                    0,
                    0,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO download_expiration_policies (
                    policy_id, active_file_id, download_candidate_id,
                    ttl_seconds, max_ttl_seconds, one_time_download_required,
                    expiration_enforced, token_creation_allowed,
                    download_execution_allowed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "download_expiration_" + download_candidate_id,
                    active_file_id,
                    download_candidate_id,
                    DEFAULT_DOWNLOAD_TTL_SECONDS,
                    MAX_DOWNLOAD_TTL_SECONDS,
                    1,
                    1,
                    0,
                    0,
                    now,
                    now,
                ),
            )

            payload_material = {
                "active_file_id": active_file_id,
                "download_candidate_id": download_candidate_id,
                "original_filename": row["original_filename"],
                "sha256_hash": row["sha256_hash"],
                "download_execution_allowed": False,
                "download_url_included": False,
                "download_token_included": False,
                "file_body_included": False,
            }
            payload_hash = calculate_sha256_bytes(repr(sorted(payload_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO download_route_payload_drafts (
                    payload_draft_id, active_file_id, download_candidate_id,
                    route_state, metadata_only, download_url_included,
                    download_token_included, file_body_included,
                    payload_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _download_payload_draft_id(active_file_id),
                    active_file_id,
                    download_candidate_id,
                    "download_route_payload_draft_locked_metadata_only",
                    1,
                    0,
                    0,
                    0,
                    payload_hash,
                    now,
                    now,
                ),
            )

            receipt_material = {
                "active_file_id": active_file_id,
                "download_candidate_id": download_candidate_id,
                "sha256_hash": row["sha256_hash"],
                "scope": "owner_download_lock_prep",
                "download_execution_allowed": False,
                "download_url_created": False,
            }
            receipt_hash = calculate_sha256_bytes(repr(sorted(receipt_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO download_receipt_draft_ledger (
                    receipt_draft_id, active_file_id, download_candidate_id,
                    receipt_state, finalized, finalization_allowed,
                    receipt_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _download_receipt_draft_id(active_file_id),
                    active_file_id,
                    download_candidate_id,
                    "download_receipt_draft_locked",
                    0,
                    0,
                    receipt_hash,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO download_safety_review_queue (
                    review_id, active_file_id, download_candidate_id,
                    review_state, reviewer_action_allowed,
                    download_execution_allowed, reason, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _download_review_id(active_file_id),
                    active_file_id,
                    download_candidate_id,
                    "queued_for_future_owner_download_safety_review_locked",
                    0,
                    0,
                    "Download safety review exists as a queue record only; no reviewer action or download execution allowed.",
                    now,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_controlled_owner_safe_preview_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP351_INIT_CACHE = dict(result)
    return result


def get_owner_download_lock_prep_shell() -> Dict[str, Any]:
    init = initialize_owner_download_lock_prep_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 351,
        "title": "Owner Download Lock Prep Shell",
        "ready": True,
        "initialized": init,
        "download_policy_prep_allowed": True,
        "download_execution_allowed": False,
        "download_url_creation_allowed": False,
        "locks": LOCKS,
    }


def get_download_eligibility_policy_board() -> Dict[str, Any]:
    initialize_owner_download_lock_prep_layer()
    with _connect() as conn:
        candidates = _rows(conn, "SELECT * FROM download_eligibility_candidates ORDER BY folder_key, original_filename")

    return {
        "section": SECTION,
        "gp": 352,
        "title": "Download Eligibility Policy Board",
        "ready": True,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "all_candidates_owner_only": all(bool(item["owner_only"]) for item in candidates),
        "all_owner_approval_required": all(bool(item["owner_approval_required"]) for item in candidates),
        "no_download_execution_allowed": all(not bool(item["download_execution_allowed"]) for item in candidates),
        "no_download_urls_created": all(not bool(item["download_url_created"]) for item in candidates),
    }


def get_download_scope_contract() -> Dict[str, Any]:
    initialize_owner_download_lock_prep_layer()
    return {
        "section": SECTION,
        "gp": 353,
        "title": "Download Scope Contract",
        "ready": True,
        "scope": {
            "owner_only": True,
            "owner_approval_required": True,
            "download_execution_allowed": False,
            "download_url_creation_allowed": False,
            "download_token_creation_allowed": False,
            "download_streaming_allowed": False,
            "download_file_body_return_allowed": False,
            "default_ttl_seconds": DEFAULT_DOWNLOAD_TTL_SECONDS,
            "max_ttl_seconds": MAX_DOWNLOAD_TTL_SECONDS,
            "one_time_download_required": True,
            "public_download_allowed": False,
            "beta_download_allowed": False,
            "share_allowed": False,
            "delete_allowed": False,
            "restore_allowed": False,
        },
    }


def get_owner_download_approval_lock_board() -> Dict[str, Any]:
    initialize_owner_download_lock_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM owner_download_approval_locks ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 354,
        "title": "Owner Download Approval Lock Board",
        "ready": True,
        "approval_lock_count": len(rows),
        "approval_locks": rows,
        "all_owner_approval_required": all(bool(item["owner_approval_required"]) for item in rows),
        "all_approval_recording_locked": all(not bool(item["approval_recording_allowed"]) for item in rows),
        "all_download_execution_locked": all(not bool(item["download_execution_allowed"]) for item in rows),
    }


def get_download_expiration_policy_board() -> Dict[str, Any]:
    initialize_owner_download_lock_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM download_expiration_policies ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 355,
        "title": "Download Expiration Policy Board",
        "ready": True,
        "expiration_policy_count": len(rows),
        "expiration_policies": rows,
        "all_one_time_download_required": all(bool(item["one_time_download_required"]) for item in rows),
        "all_expiration_enforced": all(bool(item["expiration_enforced"]) for item in rows),
        "all_token_creation_locked": all(not bool(item["token_creation_allowed"]) for item in rows),
        "all_download_execution_locked": all(not bool(item["download_execution_allowed"]) for item in rows),
    }


def get_download_route_payload_draft_builder() -> Dict[str, Any]:
    initialize_owner_download_lock_prep_layer()
    with _connect() as conn:
        drafts = _rows(conn, "SELECT * FROM download_route_payload_drafts ORDER BY created_at DESC")

    payloads = []
    for item in drafts:
        payloads.append(
            {
                "payload_draft_id": item["payload_draft_id"],
                "active_file_id": item["active_file_id"],
                "download_candidate_id": item["download_candidate_id"],
                "route_state": item["route_state"],
                "metadata_only": bool(item["metadata_only"]),
                "display": {
                    "download_url": "LOCKED",
                    "download_token": "LOCKED",
                    "file_body": "LOCKED",
                },
                "locks": {
                    "download_url_included": bool(item["download_url_included"]),
                    "download_token_included": bool(item["download_token_included"]),
                    "file_body_included": bool(item["file_body_included"]),
                },
                "payload_hash": item["payload_hash"],
            }
        )

    return {
        "section": SECTION,
        "gp": 356,
        "title": "Download Route Payload Draft Builder",
        "ready": True,
        "payload_draft_count": len(payloads),
        "payload_drafts": payloads,
        "metadata_only": True,
        "download_url_included": False,
        "download_token_included": False,
        "file_body_included": False,
    }


def get_download_receipt_draft_ledger() -> Dict[str, Any]:
    initialize_owner_download_lock_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM download_receipt_draft_ledger ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 357,
        "title": "Download Receipt Draft Ledger",
        "ready": True,
        "receipt_draft_count": len(rows),
        "receipt_drafts": rows,
        "all_receipts_draft_locked": all(not bool(item["finalized"]) and not bool(item["finalization_allowed"]) for item in rows),
        "receipt_finalization_allowed": False,
    }


def get_download_safety_review_queue() -> Dict[str, Any]:
    initialize_owner_download_lock_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM download_safety_review_queue ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 358,
        "title": "Download Safety Review Queue",
        "ready": True,
        "review_queue_count": len(rows),
        "review_queue": rows,
        "all_reviewer_actions_locked": all(not bool(item["reviewer_action_allowed"]) for item in rows),
        "all_download_execution_locked": all(not bool(item["download_execution_allowed"]) for item in rows),
    }


def get_download_safety_blocker_board() -> Dict[str, Any]:
    initialize_owner_download_lock_prep_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM download_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 359,
        "title": "Download Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_owner_download_lock_prep_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_owner_download_lock_prep_layer()

    shell = get_owner_download_lock_prep_shell()
    eligibility = get_download_eligibility_policy_board()
    scope = get_download_scope_contract()
    approvals = get_owner_download_approval_lock_board()
    expirations = get_download_expiration_policy_board()
    payloads = get_download_route_payload_draft_builder()
    receipts = get_download_receipt_draft_ledger()
    review_queue = get_download_safety_review_queue()
    blockers = get_download_safety_blocker_board()

    checks = {
        "previous_controlled_owner_safe_preview_ready": init["previous_controlled_owner_safe_preview_ready"] is True,
        "download_shell_ready": shell["ready"] is True,
        "download_eligibility_ready": eligibility["ready"] is True and eligibility["candidate_count"] >= 2,
        "download_candidates_owner_only": eligibility["all_candidates_owner_only"] is True,
        "download_candidates_approval_required": eligibility["all_owner_approval_required"] is True,
        "download_execution_locked_on_candidates": eligibility["no_download_execution_allowed"] is True,
        "download_urls_not_created": eligibility["no_download_urls_created"] is True,
        "download_scope_contract_ready": scope["ready"] is True and scope["scope"]["owner_only"] is True,
        "download_scope_execution_locked": scope["scope"]["download_execution_allowed"] is False,
        "owner_download_approval_locks_ready": approvals["ready"] is True and approvals["all_download_execution_locked"] is True,
        "download_expiration_policy_ready": expirations["ready"] is True and expirations["all_expiration_enforced"] is True,
        "download_token_creation_locked": expirations["all_token_creation_locked"] is True,
        "download_payload_drafts_ready": payloads["ready"] is True and payloads["payload_draft_count"] >= 2,
        "download_payloads_metadata_only": payloads["metadata_only"] is True and payloads["download_url_included"] is False,
        "download_receipt_drafts_locked": receipts["ready"] is True and receipts["all_receipts_draft_locked"] is True,
        "download_safety_review_queue_ready": review_queue["ready"] is True and review_queue["all_download_execution_locked"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "download_execution_still_locked": LOCKS["download_execution_allowed"] is False,
        "download_url_creation_still_locked": LOCKS["download_url_creation_allowed"] is False,
        "download_token_creation_still_locked": LOCKS["download_token_creation_allowed"] is False,
        "download_streaming_still_locked": LOCKS["download_streaming_allowed"] is False,
        "file_body_return_still_locked": LOCKS["download_file_body_return_allowed"] is False,
        "share_still_locked": LOCKS["file_share_unlocked"] is False,
        "quarantine_release_still_locked": LOCKS["quarantine_release_allowed"] is False,
        "provider_not_required": LOCKS["provider_storage_required"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 360,
        "title": "Owner Download Lock Prep Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Owner download lock prep layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — CONTROLLED OWNER DOWNLOAD EXECUTION LAYER / GP361-GP370",
        "still_locked": [
            "no download execution",
            "no download URL",
            "no download token",
            "no file body return",
            "no public download",
            "no beta download",
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


def get_owner_download_lock_prep_home() -> Dict[str, Any]:
    checkpoint = get_owner_download_lock_prep_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_owner_download_lock_prep_layer() -> Dict[str, Any]:
    checkpoint = get_owner_download_lock_prep_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_controlled_owner_safe_preview_ready"] is True
    assert checkpoint["checks"]["download_eligibility_ready"] is True
    assert checkpoint["checks"]["download_candidates_owner_only"] is True
    assert checkpoint["checks"]["download_candidates_approval_required"] is True
    assert checkpoint["checks"]["download_execution_locked_on_candidates"] is True
    assert checkpoint["checks"]["download_urls_not_created"] is True
    assert checkpoint["checks"]["download_scope_contract_ready"] is True
    assert checkpoint["checks"]["download_scope_execution_locked"] is True
    assert checkpoint["checks"]["owner_download_approval_locks_ready"] is True
    assert checkpoint["checks"]["download_expiration_policy_ready"] is True
    assert checkpoint["checks"]["download_token_creation_locked"] is True
    assert checkpoint["checks"]["download_payload_drafts_ready"] is True
    assert checkpoint["checks"]["download_payloads_metadata_only"] is True
    assert checkpoint["checks"]["download_receipt_drafts_locked"] is True
    assert checkpoint["checks"]["download_safety_review_queue_ready"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["download_eligibility_metadata_allowed"] is True
    assert LOCKS["download_scope_policy_allowed"] is True
    assert LOCKS["owner_download_approval_lock_allowed"] is True
    assert LOCKS["download_expiration_policy_allowed"] is True
    assert LOCKS["download_route_payload_draft_allowed"] is True
    assert LOCKS["download_receipt_draft_allowed"] is True
    assert LOCKS["download_safety_review_queue_allowed"] is True

    assert LOCKS["download_execution_allowed"] is False
    assert LOCKS["download_url_creation_allowed"] is False
    assert LOCKS["download_token_creation_allowed"] is False
    assert LOCKS["download_streaming_allowed"] is False
    assert LOCKS["download_file_body_return_allowed"] is False
    assert LOCKS["public_download_unlocked"] is False
    assert LOCKS["beta_download_unlocked"] is False
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

    return {
        "ok": True,
        "section": SECTION,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(item for item in PACKS if item["gp"] == gp)
    checkpoint = get_owner_download_lock_prep_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "download_prep_allowed": True,
        "download_execution_allowed": False,
        "download_url_created": False,
        "locks_preserved": True,
    }


def get_gp351_status() -> Dict[str, Any]:
    return _gp_status(351)


def get_gp352_status() -> Dict[str, Any]:
    return _gp_status(352)


def get_gp353_status() -> Dict[str, Any]:
    return _gp_status(353)


def get_gp354_status() -> Dict[str, Any]:
    return _gp_status(354)


def get_gp355_status() -> Dict[str, Any]:
    return _gp_status(355)


def get_gp356_status() -> Dict[str, Any]:
    return _gp_status(356)


def get_gp357_status() -> Dict[str, Any]:
    return _gp_status(357)


def get_gp358_status() -> Dict[str, Any]:
    return _gp_status(358)


def get_gp359_status() -> Dict[str, Any]:
    return _gp_status(359)


def get_gp360_status() -> Dict[str, Any]:
    return _gp_status(360)
