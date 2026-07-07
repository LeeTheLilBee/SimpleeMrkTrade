
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — CONTROLLED SHARE GRANT EXECUTION LAYER / GP381-GP390"
LAYER_ID = "vault_gp381_390_controlled_share_grant_execution_layer"
READINESS_LABEL = "Controlled share grant execution layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_controlled_share_grant_execution_layer.sqlite"

DEFAULT_SHARE_TTL_SECONDS = 3600
MAX_SHARE_TTL_SECONDS = 86400
FUTURE_TOWER_SUBJECT_KIND = "future_tower_identity_subject"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.owner_share_access_lock_prep_layer_service import (
        get_share_eligibility_policy_board,
        get_share_recipient_policy_board,
        get_share_expiration_policy_board,
        get_share_receipt_draft_ledger,
        validate_owner_share_access_lock_prep_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP381-GP390 requires GP371-GP380 owner share access lock prep layer first."
    ) from exc


_GP381_INIT_CACHE = None

LOCKS = {
    "controlled_share_grant_execution_layer": True,
    "controlled_owner_share_grant_execution_allowed": True,
    "future_tower_identity_recipient_grant_allowed": True,
    "controlled_share_token_fingerprint_allowed": True,
    "controlled_share_grant_packet_metadata_allowed": True,
    "share_access_ledger_allowed": True,
    "share_receipt_finalization_allowed": True,
    "public_share_unlocked": False,
    "beta_share_unlocked": False,
    "public_url_created": False,
    "share_link_created": False,
    "external_email_grant_allowed": False,
    "external_recipient_grant_allowed": False,
    "download_link_sharing_allowed": False,
    "raw_share_token_exposed": False,
    "raw_file_bytes_returned_by_json": False,
    "raw_file_download_for_recipient_allowed": False,
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
    {"gp": 381, "title": "Controlled Share Grant Execution Shell", "status": "ready", "route": "/vault/controlled-share-grant-execution-shell.json"},
    {"gp": 382, "title": "Share Grant Scope Contract", "status": "ready", "route": "/vault/share-grant-scope-contract.json"},
    {"gp": 383, "title": "Owner Share Approval Execution Board", "status": "ready", "route": "/vault/owner-share-approval-execution-board.json"},
    {"gp": 384, "title": "Controlled Share Token Builder", "status": "ready", "route": "/vault/controlled-share-token-builder.json"},
    {"gp": 385, "title": "Controlled Share Grant Packet Builder", "status": "ready", "route": "/vault/controlled-share-grant-packet-builder.json"},
    {"gp": 386, "title": "Tower Identity Recipient Grant Board", "status": "ready", "route": "/vault/tower-identity-recipient-grant-board.json"},
    {"gp": 387, "title": "Share Access Ledger", "status": "ready", "route": "/vault/share-access-ledger.json"},
    {"gp": 388, "title": "Share Receipt Finalization Board", "status": "ready", "route": "/vault/share-receipt-finalization-board.json"},
    {"gp": 389, "title": "Share Grant Safety Blocker Board", "status": "ready", "route": "/vault/share-grant-safety-blocker-board.json"},
    {"gp": 390, "title": "Controlled Share Grant Execution Readiness Checkpoint", "status": "ready", "route": "/vault/controlled-share-grant-execution-readiness-checkpoint.json"},
]

BLOCKERS = [
    {
        "blocker_id": "no_public_share",
        "label": "Public share remains locked",
        "blocked_action": "public_share",
        "allowed": False,
        "reason": "Controlled grant is not public sharing.",
    },
    {
        "blocker_id": "no_beta_share",
        "label": "Beta share remains locked",
        "blocked_action": "beta_share",
        "allowed": False,
        "reason": "Beta/tester share access is not unlocked.",
    },
    {
        "blocker_id": "no_public_url",
        "label": "Public URL remains locked",
        "blocked_action": "public_url",
        "allowed": False,
        "reason": "No public or web share URL is created.",
    },
    {
        "blocker_id": "no_share_link",
        "label": "Share link remains locked",
        "blocked_action": "share_link",
        "allowed": False,
        "reason": "Only internal controlled share grant metadata is created.",
    },
    {
        "blocker_id": "no_external_email_grant",
        "label": "External email grant remains locked",
        "blocked_action": "external_email_grant",
        "allowed": False,
        "reason": "Recipients must be future Tower identity subjects, not raw email addresses.",
    },
    {
        "blocker_id": "no_external_recipient_grant",
        "label": "External recipient grant remains locked",
        "blocked_action": "external_recipient_grant",
        "allowed": False,
        "reason": "Only internal future Tower identity subject metadata is allowed.",
    },
    {
        "blocker_id": "no_download_link_sharing",
        "label": "Download link sharing remains locked",
        "blocked_action": "download_link_sharing",
        "allowed": False,
        "reason": "Owner download and sharing stay separated.",
    },
    {
        "blocker_id": "no_raw_share_token_exposure",
        "label": "Raw share token exposure remains locked",
        "blocked_action": "raw_share_token_exposure",
        "allowed": False,
        "reason": "Only token fingerprints are exposed.",
    },
    {
        "blocker_id": "no_raw_file_bytes_json",
        "label": "Raw file bytes are not returned by JSON routes",
        "blocked_action": "raw_file_bytes_json",
        "allowed": False,
        "reason": "Share grant routes are metadata-only.",
    },
    {
        "blocker_id": "no_recipient_raw_download",
        "label": "Recipient raw download remains locked",
        "blocked_action": "recipient_raw_download",
        "allowed": False,
        "reason": "Recipient download access belongs to later Tower-gated file serving.",
    },
    {
        "blocker_id": "no_delete",
        "label": "Delete remains locked",
        "blocked_action": "file_delete",
        "allowed": False,
        "reason": "Delete belongs to trash/recovery layers.",
    },
    {
        "blocker_id": "no_restore",
        "label": "Restore remains locked",
        "blocked_action": "file_restore",
        "allowed": False,
        "reason": "Restore belongs to recovery layers.",
    },
    {
        "blocker_id": "no_quarantine_release",
        "label": "Quarantine release remains locked",
        "blocked_action": "quarantine_release",
        "allowed": False,
        "reason": "Sharing does not move or release stored objects.",
    },
    {
        "blocker_id": "no_external_sync",
        "label": "External sync remains locked",
        "blocked_action": "external_sync",
        "allowed": False,
        "reason": "Share grants do not sync externally.",
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


def _approval_execution_id(active_file_id: str) -> str:
    return "share_approval_execution_" + calculate_sha256_bytes(("share_approval_execution|" + active_file_id).encode("utf-8"))[:24]


def _share_token_id(active_file_id: str) -> str:
    return "controlled_share_token_" + calculate_sha256_bytes(("share_token|" + active_file_id).encode("utf-8"))[:24]


def _share_packet_id(active_file_id: str) -> str:
    return "controlled_share_packet_" + calculate_sha256_bytes(("share_packet|" + active_file_id).encode("utf-8"))[:24]


def _recipient_grant_id(active_file_id: str) -> str:
    return "tower_identity_recipient_grant_" + calculate_sha256_bytes(("tower_recipient|" + active_file_id).encode("utf-8"))[:24]


def _share_access_id(active_file_id: str) -> str:
    return "share_access_" + calculate_sha256_bytes(("share_access|" + active_file_id).encode("utf-8"))[:24]


def _share_receipt_final_id(active_file_id: str) -> str:
    return "share_receipt_final_" + calculate_sha256_bytes(("share_receipt_final|" + active_file_id).encode("utf-8"))[:24]


def _future_tower_subject_id(active_file_id: str) -> str:
    return "future_tower_subject_" + calculate_sha256_bytes(("future_subject|" + active_file_id).encode("utf-8"))[:16]


def _share_token_fingerprint(active_file_id: str, packet_hash: str) -> str:
    material = f"controlled-share-token|{active_file_id}|{packet_hash}|{DEFAULT_SHARE_TTL_SECONDS}"
    return calculate_sha256_bytes(material.encode("utf-8"))


def _candidate_source_rows() -> List[Dict[str, Any]]:
    candidates = get_share_eligibility_policy_board().get("candidates", [])
    recipient_policies = get_share_recipient_policy_board().get("recipient_policies", [])
    expiration_rows = get_share_expiration_policy_board().get("expiration_policies", [])
    receipt_drafts = get_share_receipt_draft_ledger().get("receipt_drafts", [])

    recipient_by_file = {row["active_file_id"]: row for row in recipient_policies}
    expiration_by_file = {row["active_file_id"]: row for row in expiration_rows}
    receipt_by_file = {row["active_file_id"]: row for row in receipt_drafts}

    rows = []
    for item in candidates:
        active_file_id = item["active_file_id"]
        recipient = recipient_by_file.get(active_file_id, {})
        expiration = expiration_by_file.get(active_file_id, {})
        receipt = receipt_by_file.get(active_file_id, {})
        rows.append(
            {
                "active_file_id": active_file_id,
                "share_candidate_id": item["share_candidate_id"],
                "download_candidate_id": item["download_candidate_id"],
                "packet_id": item["packet_id"],
                "original_filename": item["original_filename"],
                "mime_type": item["mime_type"],
                "source_hash": item["source_hash"],
                "verified_hash": item["verified_hash"],
                "packet_hash": item["packet_hash"],
                "bytes_verified": item["bytes_verified"],
                "allowed_recipient_type": recipient.get("allowed_recipient_type", "future_tower_identity_subject_only"),
                "tower_identity_required": bool(recipient.get("tower_identity_required", 1)),
                "ttl_seconds": expiration.get("ttl_seconds", DEFAULT_SHARE_TTL_SECONDS),
                "max_ttl_seconds": expiration.get("max_ttl_seconds", MAX_SHARE_TTL_SECONDS),
                "one_time_access_required": bool(expiration.get("one_time_access_required", 1)),
                "draft_receipt_hash": receipt.get("receipt_hash", "share_draft_receipt_missing"),
            }
        )
    return rows


def initialize_controlled_share_grant_execution_layer() -> Dict[str, Any]:
    global _GP381_INIT_CACHE
    if _GP381_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP381_INIT_CACHE)

    previous = validate_owner_share_access_lock_prep_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS owner_share_approval_execution (
                approval_execution_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                share_candidate_id TEXT NOT NULL,
                approval_state TEXT NOT NULL,
                owner_only INTEGER NOT NULL,
                approval_executed INTEGER NOT NULL,
                controlled_share_grant_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS controlled_share_tokens (
                share_token_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                share_candidate_id TEXT NOT NULL,
                token_state TEXT NOT NULL,
                token_fingerprint TEXT NOT NULL,
                raw_token_exposed INTEGER NOT NULL,
                ttl_seconds INTEGER NOT NULL,
                max_ttl_seconds INTEGER NOT NULL,
                one_time_access_required INTEGER NOT NULL,
                owner_only INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS controlled_share_grant_packets (
                share_packet_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                share_candidate_id TEXT NOT NULL,
                share_token_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                source_hash TEXT NOT NULL,
                verified_hash TEXT NOT NULL,
                source_packet_hash TEXT NOT NULL,
                share_packet_state TEXT NOT NULL,
                share_packet_hash TEXT NOT NULL,
                raw_file_bytes_returned_by_json INTEGER NOT NULL,
                public_url_created INTEGER NOT NULL,
                share_link_created INTEGER NOT NULL,
                external_email_grant_created INTEGER NOT NULL,
                owner_only INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_identity_recipient_grants (
                recipient_grant_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                share_candidate_id TEXT NOT NULL,
                share_packet_id TEXT NOT NULL,
                future_tower_subject_id TEXT NOT NULL,
                recipient_subject_kind TEXT NOT NULL,
                grant_state TEXT NOT NULL,
                tower_identity_required INTEGER NOT NULL,
                external_email_allowed INTEGER NOT NULL,
                external_email_grant_created INTEGER NOT NULL,
                public_access_allowed INTEGER NOT NULL,
                beta_access_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS share_access_ledger (
                share_access_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                share_packet_id TEXT NOT NULL,
                recipient_grant_id TEXT NOT NULL,
                access_scope TEXT NOT NULL,
                owner_only INTEGER NOT NULL,
                future_tower_identity_recipient_allowed INTEGER NOT NULL,
                public_access_allowed INTEGER NOT NULL,
                beta_access_allowed INTEGER NOT NULL,
                external_email_access_allowed INTEGER NOT NULL,
                download_link_sharing_allowed INTEGER NOT NULL,
                raw_file_bytes_json_allowed INTEGER NOT NULL,
                delete_allowed INTEGER NOT NULL,
                restore_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS share_receipt_finalization_board (
                final_receipt_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                share_packet_id TEXT NOT NULL,
                recipient_grant_id TEXT NOT NULL,
                final_receipt_hash TEXT NOT NULL,
                finalized INTEGER NOT NULL,
                receipt_scope TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS share_grant_safety_blockers (
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
                INSERT OR REPLACE INTO share_grant_safety_blockers (
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
            share_candidate_id = row["share_candidate_id"]
            approval_execution_id = _approval_execution_id(active_file_id)
            share_token_id = _share_token_id(active_file_id)
            share_packet_id = _share_packet_id(active_file_id)
            recipient_grant_id = _recipient_grant_id(active_file_id)
            future_subject_id = _future_tower_subject_id(active_file_id)
            token_fingerprint = _share_token_fingerprint(active_file_id, row["packet_hash"])

            conn.execute(
                """
                INSERT OR REPLACE INTO owner_share_approval_execution (
                    approval_execution_id, active_file_id, share_candidate_id,
                    approval_state, owner_only, approval_executed,
                    controlled_share_grant_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval_execution_id,
                    active_file_id,
                    share_candidate_id,
                    "owner_share_approval_executed_for_controlled_tower_identity_grant",
                    1,
                    1,
                    1,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO controlled_share_tokens (
                    share_token_id, active_file_id, share_candidate_id,
                    token_state, token_fingerprint, raw_token_exposed,
                    ttl_seconds, max_ttl_seconds, one_time_access_required,
                    owner_only, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    share_token_id,
                    active_file_id,
                    share_candidate_id,
                    "controlled_share_token_fingerprint_created",
                    token_fingerprint,
                    0,
                    row["ttl_seconds"],
                    row["max_ttl_seconds"],
                    1 if row["one_time_access_required"] else 0,
                    1,
                    now,
                ),
            )

            packet_material = {
                "active_file_id": active_file_id,
                "share_candidate_id": share_candidate_id,
                "source_packet_hash": row["packet_hash"],
                "token_fingerprint": token_fingerprint,
                "future_tower_subject_id": future_subject_id,
                "owner_only": True,
                "public_url_created": False,
                "share_link_created": False,
                "external_email_grant_created": False,
                "raw_file_bytes_returned_by_json": False,
            }
            share_packet_hash = calculate_sha256_bytes(repr(sorted(packet_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO controlled_share_grant_packets (
                    share_packet_id, active_file_id, share_candidate_id,
                    share_token_id, original_filename, mime_type,
                    source_hash, verified_hash, source_packet_hash,
                    share_packet_state, share_packet_hash,
                    raw_file_bytes_returned_by_json, public_url_created,
                    share_link_created, external_email_grant_created,
                    owner_only, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    share_packet_id,
                    active_file_id,
                    share_candidate_id,
                    share_token_id,
                    row["original_filename"],
                    row["mime_type"],
                    row["source_hash"],
                    row["verified_hash"],
                    row["packet_hash"],
                    "controlled_tower_identity_share_grant_packet_ready",
                    share_packet_hash,
                    0,
                    0,
                    0,
                    0,
                    1,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_identity_recipient_grants (
                    recipient_grant_id, active_file_id, share_candidate_id,
                    share_packet_id, future_tower_subject_id,
                    recipient_subject_kind, grant_state,
                    tower_identity_required, external_email_allowed,
                    external_email_grant_created, public_access_allowed,
                    beta_access_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    recipient_grant_id,
                    active_file_id,
                    share_candidate_id,
                    share_packet_id,
                    future_subject_id,
                    FUTURE_TOWER_SUBJECT_KIND,
                    "controlled_future_tower_identity_recipient_grant_recorded",
                    1,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO share_access_ledger (
                    share_access_id, active_file_id, share_packet_id,
                    recipient_grant_id, access_scope, owner_only,
                    future_tower_identity_recipient_allowed,
                    public_access_allowed, beta_access_allowed,
                    external_email_access_allowed, download_link_sharing_allowed,
                    raw_file_bytes_json_allowed, delete_allowed,
                    restore_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _share_access_id(active_file_id),
                    active_file_id,
                    share_packet_id,
                    recipient_grant_id,
                    "controlled_future_tower_identity_share_grant",
                    1,
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

            receipt_material = {
                "active_file_id": active_file_id,
                "share_packet_id": share_packet_id,
                "recipient_grant_id": recipient_grant_id,
                "share_packet_hash": share_packet_hash,
                "token_fingerprint": token_fingerprint,
                "future_tower_subject_id": future_subject_id,
                "public_access_allowed": False,
                "external_email_access_allowed": False,
                "download_link_sharing_allowed": False,
                "raw_file_bytes_json_allowed": False,
            }
            final_receipt_hash = calculate_sha256_bytes(repr(sorted(receipt_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO share_receipt_finalization_board (
                    final_receipt_id, active_file_id, share_packet_id,
                    recipient_grant_id, final_receipt_hash,
                    finalized, receipt_scope, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _share_receipt_final_id(active_file_id),
                    active_file_id,
                    share_packet_id,
                    recipient_grant_id,
                    final_receipt_hash,
                    1,
                    "controlled_share_grant_execution",
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_owner_share_access_lock_prep_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP381_INIT_CACHE = dict(result)
    return result


def get_controlled_share_grant_execution_shell() -> Dict[str, Any]:
    init = initialize_controlled_share_grant_execution_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 381,
        "title": "Controlled Share Grant Execution Shell",
        "ready": True,
        "initialized": init,
        "controlled_owner_share_grant_execution_allowed": True,
        "future_tower_identity_recipient_grant_allowed": True,
        "public_share_unlocked": False,
        "external_email_grant_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "locks": LOCKS,
    }


def get_share_grant_scope_contract() -> Dict[str, Any]:
    initialize_controlled_share_grant_execution_layer()
    return {
        "section": SECTION,
        "gp": 382,
        "title": "Share Grant Scope Contract",
        "ready": True,
        "scope": {
            "controlled_owner_share_grant_execution_allowed": True,
            "future_tower_identity_recipient_grant_allowed": True,
            "tower_identity_required": True,
            "recipient_subject_kind": FUTURE_TOWER_SUBJECT_KIND,
            "controlled_share_token_fingerprint_allowed": True,
            "raw_share_token_exposed": False,
            "raw_file_bytes_returned_by_json": False,
            "public_share_allowed": False,
            "beta_share_allowed": False,
            "public_url_allowed": False,
            "share_link_allowed": False,
            "external_email_grant_allowed": False,
            "download_link_sharing_allowed": False,
            "delete_allowed": False,
            "restore_allowed": False,
            "ttl_seconds": DEFAULT_SHARE_TTL_SECONDS,
            "max_ttl_seconds": MAX_SHARE_TTL_SECONDS,
            "one_time_access_required": True,
        },
    }


def get_owner_share_approval_execution_board() -> Dict[str, Any]:
    initialize_controlled_share_grant_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM owner_share_approval_execution ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 383,
        "title": "Owner Share Approval Execution Board",
        "ready": True,
        "approval_execution_count": len(rows),
        "approval_executions": rows,
        "all_owner_only": all(bool(item["owner_only"]) for item in rows),
        "all_approvals_executed": all(bool(item["approval_executed"]) for item in rows),
        "controlled_share_grant_count": sum(1 for item in rows if bool(item["controlled_share_grant_allowed"])),
    }


def get_controlled_share_token_builder() -> Dict[str, Any]:
    initialize_controlled_share_grant_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM controlled_share_tokens ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 384,
        "title": "Controlled Share Token Builder",
        "ready": True,
        "share_token_count": len(rows),
        "share_tokens": rows,
        "all_owner_only": all(bool(item["owner_only"]) for item in rows),
        "no_raw_tokens_exposed": all(not bool(item["raw_token_exposed"]) for item in rows),
        "all_one_time_access_required": all(bool(item["one_time_access_required"]) for item in rows),
    }


def get_controlled_share_grant_packet_builder() -> Dict[str, Any]:
    initialize_controlled_share_grant_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM controlled_share_grant_packets ORDER BY created_at DESC")

    packets = []
    for item in rows:
        packets.append(
            {
                "share_packet_id": item["share_packet_id"],
                "active_file_id": item["active_file_id"],
                "share_candidate_id": item["share_candidate_id"],
                "share_token_id": item["share_token_id"],
                "original_filename": item["original_filename"],
                "mime_type": item["mime_type"],
                "source_hash": item["source_hash"],
                "verified_hash": item["verified_hash"],
                "source_packet_hash": item["source_packet_hash"],
                "share_packet_state": item["share_packet_state"],
                "share_packet_hash": item["share_packet_hash"],
                "owner_only": bool(item["owner_only"]),
                "display": {
                    "raw_file_bytes": "LOCKED_FROM_JSON",
                    "raw_share_token": "LOCKED_FINGERPRINT_ONLY",
                    "public_url": "LOCKED",
                    "share_link": "LOCKED",
                    "external_email_grant": "LOCKED",
                },
                "locks": {
                    "raw_file_bytes_returned_by_json": bool(item["raw_file_bytes_returned_by_json"]),
                    "public_url_created": bool(item["public_url_created"]),
                    "share_link_created": bool(item["share_link_created"]),
                    "external_email_grant_created": bool(item["external_email_grant_created"]),
                },
            }
        )

    return {
        "section": SECTION,
        "gp": 385,
        "title": "Controlled Share Grant Packet Builder",
        "ready": True,
        "share_packet_count": len(packets),
        "share_packets": packets,
        "successful_share_packet_count": sum(1 for item in packets if item["share_packet_state"] == "controlled_tower_identity_share_grant_packet_ready"),
        "all_owner_only": all(item["owner_only"] for item in packets),
        "no_raw_file_bytes_returned_by_json": all(not item["locks"]["raw_file_bytes_returned_by_json"] for item in packets),
        "no_public_urls_created": all(not item["locks"]["public_url_created"] for item in packets),
        "no_share_links_created": all(not item["locks"]["share_link_created"] for item in packets),
        "no_external_email_grants_created": all(not item["locks"]["external_email_grant_created"] for item in packets),
    }


def get_tower_identity_recipient_grant_board() -> Dict[str, Any]:
    initialize_controlled_share_grant_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_identity_recipient_grants ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 386,
        "title": "Tower Identity Recipient Grant Board",
        "ready": True,
        "recipient_grant_count": len(rows),
        "recipient_grants": rows,
        "all_tower_identity_required": all(bool(item["tower_identity_required"]) for item in rows),
        "all_future_tower_subjects": all(item["recipient_subject_kind"] == FUTURE_TOWER_SUBJECT_KIND for item in rows),
        "no_external_email_allowed": all(not bool(item["external_email_allowed"]) for item in rows),
        "no_external_email_grants_created": all(not bool(item["external_email_grant_created"]) for item in rows),
        "no_public_access": all(not bool(item["public_access_allowed"]) for item in rows),
        "no_beta_access": all(not bool(item["beta_access_allowed"]) for item in rows),
    }


def get_share_access_ledger() -> Dict[str, Any]:
    initialize_controlled_share_grant_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM share_access_ledger ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 387,
        "title": "Share Access Ledger",
        "ready": True,
        "share_access_count": len(rows),
        "share_access_rows": rows,
        "all_owner_only": all(bool(item["owner_only"]) for item in rows),
        "all_future_tower_identity_recipient_allowed": all(bool(item["future_tower_identity_recipient_allowed"]) for item in rows),
        "no_public_access": all(not bool(item["public_access_allowed"]) for item in rows),
        "no_beta_access": all(not bool(item["beta_access_allowed"]) for item in rows),
        "no_external_email_access": all(not bool(item["external_email_access_allowed"]) for item in rows),
        "no_download_link_sharing": all(not bool(item["download_link_sharing_allowed"]) for item in rows),
        "no_raw_file_bytes_json": all(not bool(item["raw_file_bytes_json_allowed"]) for item in rows),
        "no_delete_access": all(not bool(item["delete_allowed"]) for item in rows),
        "no_restore_access": all(not bool(item["restore_allowed"]) for item in rows),
    }


def get_share_receipt_finalization_board() -> Dict[str, Any]:
    initialize_controlled_share_grant_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM share_receipt_finalization_board ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 388,
        "title": "Share Receipt Finalization Board",
        "ready": True,
        "final_receipt_count": len(rows),
        "final_receipts": rows,
        "all_receipts_finalized": all(bool(item["finalized"]) for item in rows),
    }


def get_share_grant_safety_blocker_board() -> Dict[str, Any]:
    initialize_controlled_share_grant_execution_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM share_grant_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 389,
        "title": "Share Grant Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_controlled_share_grant_execution_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_controlled_share_grant_execution_layer()

    shell = get_controlled_share_grant_execution_shell()
    scope = get_share_grant_scope_contract()
    approvals = get_owner_share_approval_execution_board()
    tokens = get_controlled_share_token_builder()
    packets = get_controlled_share_grant_packet_builder()
    recipients = get_tower_identity_recipient_grant_board()
    access = get_share_access_ledger()
    receipts = get_share_receipt_finalization_board()
    blockers = get_share_grant_safety_blocker_board()

    checks = {
        "previous_owner_share_access_lock_prep_ready": init["previous_owner_share_access_lock_prep_ready"] is True,
        "share_grant_shell_ready": shell["ready"] is True,
        "share_grant_scope_ready": scope["ready"] is True and scope["scope"]["controlled_owner_share_grant_execution_allowed"] is True,
        "scope_tower_identity_required": scope["scope"]["future_tower_identity_recipient_grant_allowed"] is True,
        "scope_raw_share_token_not_exposed": scope["scope"]["raw_share_token_exposed"] is False,
        "scope_raw_file_bytes_not_returned": scope["scope"]["raw_file_bytes_returned_by_json"] is False,
        "scope_public_beta_locked": scope["scope"]["public_share_allowed"] is False and scope["scope"]["beta_share_allowed"] is False,
        "owner_share_approval_execution_ready": approvals["ready"] is True and approvals["approval_execution_count"] >= 2,
        "controlled_share_grants_recorded": approvals["controlled_share_grant_count"] >= 2,
        "controlled_share_tokens_ready": tokens["ready"] is True and tokens["share_token_count"] >= 2,
        "no_raw_tokens_exposed": tokens["no_raw_tokens_exposed"] is True,
        "controlled_share_packets_ready": packets["ready"] is True and packets["share_packet_count"] >= 2,
        "controlled_share_packets_successful": packets["successful_share_packet_count"] >= 2,
        "share_packets_owner_only": packets["all_owner_only"] is True,
        "share_packets_no_raw_bytes_json": packets["no_raw_file_bytes_returned_by_json"] is True,
        "share_packets_no_public_urls": packets["no_public_urls_created"] is True,
        "share_packets_no_links": packets["no_share_links_created"] is True,
        "share_packets_no_external_email_grants": packets["no_external_email_grants_created"] is True,
        "tower_identity_recipient_grants_ready": recipients["ready"] is True and recipients["recipient_grant_count"] >= 2,
        "recipient_grants_tower_identity_only": recipients["all_tower_identity_required"] is True and recipients["all_future_tower_subjects"] is True,
        "recipient_grants_no_external_email": recipients["no_external_email_allowed"] is True and recipients["no_external_email_grants_created"] is True,
        "recipient_grants_no_public_beta": recipients["no_public_access"] is True and recipients["no_beta_access"] is True,
        "share_access_ledger_ready": access["ready"] is True and access["share_access_count"] >= 2,
        "share_access_future_tower_identity_only": access["all_future_tower_identity_recipient_allowed"] is True,
        "share_access_no_public_beta_external": access["no_public_access"] is True and access["no_beta_access"] is True and access["no_external_email_access"] is True,
        "share_access_no_download_raw_delete_restore": access["no_download_link_sharing"] is True and access["no_raw_file_bytes_json"] is True and access["no_delete_access"] is True and access["no_restore_access"] is True,
        "share_receipts_finalized": receipts["ready"] is True and receipts["all_receipts_finalized"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "public_share_still_locked": LOCKS["public_share_unlocked"] is False,
        "beta_share_still_locked": LOCKS["beta_share_unlocked"] is False,
        "public_url_still_locked": LOCKS["public_url_created"] is False,
        "share_link_still_locked": LOCKS["share_link_created"] is False,
        "external_email_grant_still_locked": LOCKS["external_email_grant_allowed"] is False,
        "raw_file_bytes_json_still_locked": LOCKS["raw_file_bytes_returned_by_json"] is False,
        "delete_restore_still_locked": LOCKS["file_delete_unlocked"] is False and LOCKS["file_restore_unlocked"] is False,
        "quarantine_release_still_locked": LOCKS["quarantine_release_allowed"] is False,
        "provider_not_required": LOCKS["provider_storage_required"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 390,
        "title": "Controlled Share Grant Execution Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Controlled share grant execution layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — TRASH RESTORE AND RECOVERY PREP LAYER / GP391-GP400",
        "still_locked": [
            "no public share",
            "no beta share",
            "no public URL",
            "no share link",
            "no external email grant",
            "no external recipient grant",
            "no download link sharing",
            "no raw share token exposure",
            "no raw file bytes returned by JSON",
            "no recipient raw download",
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


def get_controlled_share_grant_execution_home() -> Dict[str, Any]:
    checkpoint = get_controlled_share_grant_execution_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_controlled_share_grant_execution_layer() -> Dict[str, Any]:
    checkpoint = get_controlled_share_grant_execution_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_owner_share_access_lock_prep_ready"] is True
    assert checkpoint["checks"]["share_grant_shell_ready"] is True
    assert checkpoint["checks"]["share_grant_scope_ready"] is True
    assert checkpoint["checks"]["scope_tower_identity_required"] is True
    assert checkpoint["checks"]["scope_raw_share_token_not_exposed"] is True
    assert checkpoint["checks"]["scope_raw_file_bytes_not_returned"] is True
    assert checkpoint["checks"]["scope_public_beta_locked"] is True
    assert checkpoint["checks"]["owner_share_approval_execution_ready"] is True
    assert checkpoint["checks"]["controlled_share_grants_recorded"] is True
    assert checkpoint["checks"]["controlled_share_tokens_ready"] is True
    assert checkpoint["checks"]["no_raw_tokens_exposed"] is True
    assert checkpoint["checks"]["controlled_share_packets_ready"] is True
    assert checkpoint["checks"]["controlled_share_packets_successful"] is True
    assert checkpoint["checks"]["share_packets_no_raw_bytes_json"] is True
    assert checkpoint["checks"]["share_packets_no_public_urls"] is True
    assert checkpoint["checks"]["share_packets_no_links"] is True
    assert checkpoint["checks"]["share_packets_no_external_email_grants"] is True
    assert checkpoint["checks"]["tower_identity_recipient_grants_ready"] is True
    assert checkpoint["checks"]["recipient_grants_tower_identity_only"] is True
    assert checkpoint["checks"]["recipient_grants_no_external_email"] is True
    assert checkpoint["checks"]["recipient_grants_no_public_beta"] is True
    assert checkpoint["checks"]["share_access_ledger_ready"] is True
    assert checkpoint["checks"]["share_access_future_tower_identity_only"] is True
    assert checkpoint["checks"]["share_access_no_public_beta_external"] is True
    assert checkpoint["checks"]["share_access_no_download_raw_delete_restore"] is True
    assert checkpoint["checks"]["share_receipts_finalized"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["controlled_owner_share_grant_execution_allowed"] is True
    assert LOCKS["future_tower_identity_recipient_grant_allowed"] is True
    assert LOCKS["controlled_share_token_fingerprint_allowed"] is True
    assert LOCKS["controlled_share_grant_packet_metadata_allowed"] is True
    assert LOCKS["share_access_ledger_allowed"] is True
    assert LOCKS["share_receipt_finalization_allowed"] is True

    assert LOCKS["public_share_unlocked"] is False
    assert LOCKS["beta_share_unlocked"] is False
    assert LOCKS["public_url_created"] is False
    assert LOCKS["share_link_created"] is False
    assert LOCKS["external_email_grant_allowed"] is False
    assert LOCKS["external_recipient_grant_allowed"] is False
    assert LOCKS["download_link_sharing_allowed"] is False
    assert LOCKS["raw_share_token_exposed"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_file_download_for_recipient_allowed"] is False
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
    checkpoint = get_controlled_share_grant_execution_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "controlled_share_grant_allowed": True,
        "future_tower_identity_recipient_grant_allowed": True,
        "public_share_allowed": False,
        "external_email_grant_allowed": False,
        "share_link_created": False,
        "raw_file_bytes_returned_by_json": False,
        "locks_preserved": True,
    }


def get_gp381_status() -> Dict[str, Any]:
    return _gp_status(381)


def get_gp382_status() -> Dict[str, Any]:
    return _gp_status(382)


def get_gp383_status() -> Dict[str, Any]:
    return _gp_status(383)


def get_gp384_status() -> Dict[str, Any]:
    return _gp_status(384)


def get_gp385_status() -> Dict[str, Any]:
    return _gp_status(385)


def get_gp386_status() -> Dict[str, Any]:
    return _gp_status(386)


def get_gp387_status() -> Dict[str, Any]:
    return _gp_status(387)


def get_gp388_status() -> Dict[str, Any]:
    return _gp_status(388)


def get_gp389_status() -> Dict[str, Any]:
    return _gp_status(389)


def get_gp390_status() -> Dict[str, Any]:
    return _gp_status(390)
