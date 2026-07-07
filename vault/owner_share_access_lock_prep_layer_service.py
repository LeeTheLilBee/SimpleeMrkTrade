
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — OWNER SHARE ACCESS LOCK PREP LAYER / GP371-GP380"
LAYER_ID = "vault_gp371_380_owner_share_access_lock_prep_layer"
READINESS_LABEL = "Owner share access lock prep layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_owner_share_access_lock_prep_layer.sqlite"

DEFAULT_SHARE_TTL_SECONDS = 3600
MAX_SHARE_TTL_SECONDS = 86400

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.controlled_owner_download_execution_layer_service import (
        get_controlled_download_packet_builder,
        get_download_access_ledger,
        get_download_receipt_finalization_board,
        validate_controlled_owner_download_execution_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP371-GP380 requires GP361-GP370 controlled owner download execution layer first."
    ) from exc


_GP371_INIT_CACHE = None

LOCKS = {
    "owner_share_access_lock_prep_layer": True,
    "share_eligibility_metadata_allowed": True,
    "share_scope_policy_allowed": True,
    "share_recipient_policy_allowed": True,
    "owner_share_approval_lock_allowed": True,
    "share_expiration_policy_allowed": True,
    "share_route_payload_draft_allowed": True,
    "share_receipt_draft_allowed": True,
    "share_execution_allowed": False,
    "share_link_creation_allowed": False,
    "share_token_creation_allowed": False,
    "external_recipient_grant_allowed": False,
    "public_access_unlocked": False,
    "beta_access_unlocked": False,
    "download_link_sharing_allowed": False,
    "raw_file_bytes_returned_by_json": False,
    "raw_share_token_exposed": False,
    "public_url_created": False,
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
    {"gp": 371, "title": "Owner Share Access Lock Prep Shell", "status": "ready", "route": "/vault/owner-share-access-lock-prep-shell.json"},
    {"gp": 372, "title": "Share Eligibility Policy Board", "status": "ready", "route": "/vault/share-eligibility-policy-board.json"},
    {"gp": 373, "title": "Share Scope Contract", "status": "ready", "route": "/vault/share-scope-contract.json"},
    {"gp": 374, "title": "Share Recipient Policy Board", "status": "ready", "route": "/vault/share-recipient-policy-board.json"},
    {"gp": 375, "title": "Owner Share Approval Lock Board", "status": "ready", "route": "/vault/owner-share-approval-lock-board.json"},
    {"gp": 376, "title": "Share Expiration Policy Board", "status": "ready", "route": "/vault/share-expiration-policy-board.json"},
    {"gp": 377, "title": "Share Route Payload Draft Builder", "status": "ready", "route": "/vault/share-route-payload-draft-builder.json"},
    {"gp": 378, "title": "Share Receipt Draft Ledger", "status": "ready", "route": "/vault/share-receipt-draft-ledger.json"},
    {"gp": 379, "title": "Share Safety Blocker Board", "status": "ready", "route": "/vault/share-safety-blocker-board.json"},
    {"gp": 380, "title": "Owner Share Access Lock Prep Readiness Checkpoint", "status": "ready", "route": "/vault/owner-share-access-lock-prep-readiness-checkpoint.json"},
]

BLOCKERS = [
    {
        "blocker_id": "no_share_execution",
        "label": "Share execution remains locked",
        "blocked_action": "share_execution",
        "allowed": False,
        "reason": "This layer only prepares share access policy.",
    },
    {
        "blocker_id": "no_share_link_creation",
        "label": "Share link creation remains locked",
        "blocked_action": "share_link_creation",
        "allowed": False,
        "reason": "No share URL or link is created in this layer.",
    },
    {
        "blocker_id": "no_share_token_creation",
        "label": "Share token creation remains locked",
        "blocked_action": "share_token_creation",
        "allowed": False,
        "reason": "Share tokens belong to controlled share execution later.",
    },
    {
        "blocker_id": "no_external_recipient_grant",
        "label": "External recipient grant remains locked",
        "blocked_action": "external_recipient_grant",
        "allowed": False,
        "reason": "Recipient access is policy-only in this layer.",
    },
    {
        "blocker_id": "no_public_access",
        "label": "Public access remains locked",
        "blocked_action": "public_access",
        "allowed": False,
        "reason": "Public file access is not allowed.",
    },
    {
        "blocker_id": "no_beta_access",
        "label": "Beta access remains locked",
        "blocked_action": "beta_access",
        "allowed": False,
        "reason": "Tester/beta share access is not unlocked.",
    },
    {
        "blocker_id": "no_download_link_sharing",
        "label": "Download link sharing remains locked",
        "blocked_action": "download_link_sharing",
        "allowed": False,
        "reason": "Owner download and file sharing stay separated.",
    },
    {
        "blocker_id": "no_raw_file_bytes_json",
        "label": "Raw file bytes are not returned by JSON routes",
        "blocked_action": "raw_file_bytes_json",
        "allowed": False,
        "reason": "Share prep routes are metadata-only.",
    },
    {
        "blocker_id": "no_raw_share_token_exposure",
        "label": "Raw share token exposure remains locked",
        "blocked_action": "raw_share_token_exposure",
        "allowed": False,
        "reason": "No share token exists yet.",
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
        "reason": "Share prep does not move or release objects.",
    },
    {
        "blocker_id": "no_external_sync",
        "label": "External sync remains locked",
        "blocked_action": "external_sync",
        "allowed": False,
        "reason": "Share prep does not sync externally.",
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


def _share_candidate_id(active_file_id: str) -> str:
    return "share_candidate_" + calculate_sha256_bytes(("share_candidate|" + active_file_id).encode("utf-8"))[:24]


def _recipient_policy_id(active_file_id: str) -> str:
    return "share_recipient_policy_" + calculate_sha256_bytes(("share_recipient|" + active_file_id).encode("utf-8"))[:24]


def _share_approval_lock_id(active_file_id: str) -> str:
    return "share_approval_lock_" + calculate_sha256_bytes(("share_approval|" + active_file_id).encode("utf-8"))[:24]


def _share_expiration_policy_id(active_file_id: str) -> str:
    return "share_expiration_" + calculate_sha256_bytes(("share_expiration|" + active_file_id).encode("utf-8"))[:24]


def _share_payload_draft_id(active_file_id: str) -> str:
    return "share_payload_draft_" + calculate_sha256_bytes(("share_payload|" + active_file_id).encode("utf-8"))[:24]


def _share_receipt_draft_id(active_file_id: str) -> str:
    return "share_receipt_draft_" + calculate_sha256_bytes(("share_receipt|" + active_file_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    packets = get_controlled_download_packet_builder().get("packets", [])
    access_rows = get_download_access_ledger().get("access_rows", [])
    receipts = get_download_receipt_finalization_board().get("final_receipts", [])

    access_by_file = {row["active_file_id"]: row for row in access_rows}
    receipt_by_file = {row["active_file_id"]: row for row in receipts}

    rows = []
    for packet in packets:
        active_file_id = packet["active_file_id"]
        rows.append(
            {
                "active_file_id": active_file_id,
                "download_candidate_id": packet["download_candidate_id"],
                "packet_id": packet["packet_id"],
                "original_filename": packet["original_filename"],
                "mime_type": packet["mime_type"],
                "source_hash": packet["source_hash"],
                "verified_hash": packet["verified_hash"],
                "packet_hash": packet["packet_hash"],
                "bytes_verified": packet["bytes_verified"],
                "download_access_scope": access_by_file.get(active_file_id, {}).get("access_scope", "owner_only_controlled_download"),
                "download_receipt_hash": receipt_by_file.get(active_file_id, {}).get("final_receipt_hash", "download_receipt_not_required_for_share_prep"),
            }
        )
    return rows


def initialize_owner_share_access_lock_prep_layer() -> Dict[str, Any]:
    global _GP371_INIT_CACHE
    if _GP371_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP371_INIT_CACHE)

    previous = validate_controlled_owner_download_execution_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS share_eligibility_candidates (
                share_candidate_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                download_candidate_id TEXT NOT NULL,
                packet_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                source_hash TEXT NOT NULL,
                verified_hash TEXT NOT NULL,
                packet_hash TEXT NOT NULL,
                bytes_verified INTEGER NOT NULL,
                eligibility_state TEXT NOT NULL,
                owner_only INTEGER NOT NULL,
                owner_approval_required INTEGER NOT NULL,
                share_execution_allowed INTEGER NOT NULL,
                share_link_created INTEGER NOT NULL,
                external_recipient_granted INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS share_recipient_policies (
                recipient_policy_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                share_candidate_id TEXT NOT NULL,
                recipient_policy_state TEXT NOT NULL,
                allowed_recipient_type TEXT NOT NULL,
                external_email_allowed INTEGER NOT NULL,
                tower_identity_required INTEGER NOT NULL,
                recipient_grant_allowed INTEGER NOT NULL,
                public_access_allowed INTEGER NOT NULL,
                beta_access_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS owner_share_approval_locks (
                approval_lock_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                share_candidate_id TEXT NOT NULL,
                approval_state TEXT NOT NULL,
                owner_approval_required INTEGER NOT NULL,
                approval_recording_allowed INTEGER NOT NULL,
                share_execution_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS share_expiration_policies (
                policy_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                share_candidate_id TEXT NOT NULL,
                ttl_seconds INTEGER NOT NULL,
                max_ttl_seconds INTEGER NOT NULL,
                one_time_access_required INTEGER NOT NULL,
                expiration_enforced INTEGER NOT NULL,
                share_token_creation_allowed INTEGER NOT NULL,
                share_execution_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS share_route_payload_drafts (
                payload_draft_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                share_candidate_id TEXT NOT NULL,
                route_state TEXT NOT NULL,
                metadata_only INTEGER NOT NULL,
                share_link_included INTEGER NOT NULL,
                share_token_included INTEGER NOT NULL,
                recipient_access_included INTEGER NOT NULL,
                public_url_included INTEGER NOT NULL,
                file_body_included INTEGER NOT NULL,
                payload_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS share_receipt_draft_ledger (
                receipt_draft_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                share_candidate_id TEXT NOT NULL,
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
            CREATE TABLE IF NOT EXISTS share_safety_blockers (
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
                INSERT OR REPLACE INTO share_safety_blockers (
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
            share_candidate_id = _share_candidate_id(active_file_id)

            conn.execute(
                """
                INSERT OR REPLACE INTO share_eligibility_candidates (
                    share_candidate_id, active_file_id, download_candidate_id,
                    packet_id, original_filename, mime_type, source_hash,
                    verified_hash, packet_hash, bytes_verified,
                    eligibility_state, owner_only, owner_approval_required,
                    share_execution_allowed, share_link_created,
                    external_recipient_granted, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    share_candidate_id,
                    active_file_id,
                    row["download_candidate_id"],
                    row["packet_id"],
                    row["original_filename"],
                    row["mime_type"],
                    row["source_hash"],
                    row["verified_hash"],
                    row["packet_hash"],
                    row["bytes_verified"],
                    "share_policy_candidate_owner_approval_required_locked",
                    1,
                    1,
                    0,
                    0,
                    0,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO share_recipient_policies (
                    recipient_policy_id, active_file_id, share_candidate_id,
                    recipient_policy_state, allowed_recipient_type,
                    external_email_allowed, tower_identity_required,
                    recipient_grant_allowed, public_access_allowed,
                    beta_access_allowed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _recipient_policy_id(active_file_id),
                    active_file_id,
                    share_candidate_id,
                    "recipient_policy_draft_locked_tower_identity_required",
                    "future_tower_identity_subject_only",
                    0,
                    1,
                    0,
                    0,
                    0,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO owner_share_approval_locks (
                    approval_lock_id, active_file_id, share_candidate_id,
                    approval_state, owner_approval_required,
                    approval_recording_allowed, share_execution_allowed,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _share_approval_lock_id(active_file_id),
                    active_file_id,
                    share_candidate_id,
                    "owner_share_approval_required_locked",
                    1,
                    0,
                    0,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO share_expiration_policies (
                    policy_id, active_file_id, share_candidate_id,
                    ttl_seconds, max_ttl_seconds, one_time_access_required,
                    expiration_enforced, share_token_creation_allowed,
                    share_execution_allowed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _share_expiration_policy_id(active_file_id),
                    active_file_id,
                    share_candidate_id,
                    DEFAULT_SHARE_TTL_SECONDS,
                    MAX_SHARE_TTL_SECONDS,
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
                "share_candidate_id": share_candidate_id,
                "packet_hash": row["packet_hash"],
                "share_execution_allowed": False,
                "share_link_included": False,
                "share_token_included": False,
                "recipient_access_included": False,
                "public_url_included": False,
                "file_body_included": False,
            }
            payload_hash = calculate_sha256_bytes(repr(sorted(payload_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO share_route_payload_drafts (
                    payload_draft_id, active_file_id, share_candidate_id,
                    route_state, metadata_only, share_link_included,
                    share_token_included, recipient_access_included,
                    public_url_included, file_body_included,
                    payload_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _share_payload_draft_id(active_file_id),
                    active_file_id,
                    share_candidate_id,
                    "share_route_payload_draft_locked_metadata_only",
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

            receipt_material = {
                "active_file_id": active_file_id,
                "share_candidate_id": share_candidate_id,
                "packet_hash": row["packet_hash"],
                "scope": "owner_share_access_lock_prep",
                "share_execution_allowed": False,
                "share_link_created": False,
                "recipient_granted": False,
            }
            receipt_hash = calculate_sha256_bytes(repr(sorted(receipt_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO share_receipt_draft_ledger (
                    receipt_draft_id, active_file_id, share_candidate_id,
                    receipt_state, finalized, finalization_allowed,
                    receipt_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _share_receipt_draft_id(active_file_id),
                    active_file_id,
                    share_candidate_id,
                    "share_receipt_draft_locked",
                    0,
                    0,
                    receipt_hash,
                    now,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_controlled_owner_download_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP371_INIT_CACHE = dict(result)
    return result


def get_owner_share_access_lock_prep_shell() -> Dict[str, Any]:
    init = initialize_owner_share_access_lock_prep_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 371,
        "title": "Owner Share Access Lock Prep Shell",
        "ready": True,
        "initialized": init,
        "share_policy_prep_allowed": True,
        "share_execution_allowed": False,
        "share_link_creation_allowed": False,
        "external_recipient_grant_allowed": False,
        "locks": LOCKS,
    }


def get_share_eligibility_policy_board() -> Dict[str, Any]:
    initialize_owner_share_access_lock_prep_layer()
    with _connect() as conn:
        candidates = _rows(conn, "SELECT * FROM share_eligibility_candidates ORDER BY original_filename")

    return {
        "section": SECTION,
        "gp": 372,
        "title": "Share Eligibility Policy Board",
        "ready": True,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "all_candidates_owner_only": all(bool(item["owner_only"]) for item in candidates),
        "all_owner_approval_required": all(bool(item["owner_approval_required"]) for item in candidates),
        "no_share_execution_allowed": all(not bool(item["share_execution_allowed"]) for item in candidates),
        "no_share_links_created": all(not bool(item["share_link_created"]) for item in candidates),
        "no_external_recipients_granted": all(not bool(item["external_recipient_granted"]) for item in candidates),
    }


def get_share_scope_contract() -> Dict[str, Any]:
    initialize_owner_share_access_lock_prep_layer()
    return {
        "section": SECTION,
        "gp": 373,
        "title": "Share Scope Contract",
        "ready": True,
        "scope": {
            "owner_only_share_prep": True,
            "owner_approval_required": True,
            "tower_identity_required_for_future_recipient": True,
            "share_execution_allowed": False,
            "share_link_creation_allowed": False,
            "share_token_creation_allowed": False,
            "external_recipient_grant_allowed": False,
            "public_access_allowed": False,
            "beta_access_allowed": False,
            "download_link_sharing_allowed": False,
            "raw_file_bytes_returned_by_json": False,
            "default_ttl_seconds": DEFAULT_SHARE_TTL_SECONDS,
            "max_ttl_seconds": MAX_SHARE_TTL_SECONDS,
            "one_time_access_required": True,
            "delete_allowed": False,
            "restore_allowed": False,
        },
    }


def get_share_recipient_policy_board() -> Dict[str, Any]:
    initialize_owner_share_access_lock_prep_layer()
    with _connect() as conn:
        policies = _rows(conn, "SELECT * FROM share_recipient_policies ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 374,
        "title": "Share Recipient Policy Board",
        "ready": True,
        "recipient_policy_count": len(policies),
        "recipient_policies": policies,
        "all_tower_identity_required": all(bool(item["tower_identity_required"]) for item in policies),
        "all_external_email_locked": all(not bool(item["external_email_allowed"]) for item in policies),
        "all_recipient_grants_locked": all(not bool(item["recipient_grant_allowed"]) for item in policies),
        "all_public_access_locked": all(not bool(item["public_access_allowed"]) for item in policies),
        "all_beta_access_locked": all(not bool(item["beta_access_allowed"]) for item in policies),
    }


def get_owner_share_approval_lock_board() -> Dict[str, Any]:
    initialize_owner_share_access_lock_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM owner_share_approval_locks ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 375,
        "title": "Owner Share Approval Lock Board",
        "ready": True,
        "approval_lock_count": len(rows),
        "approval_locks": rows,
        "all_owner_approval_required": all(bool(item["owner_approval_required"]) for item in rows),
        "all_approval_recording_locked": all(not bool(item["approval_recording_allowed"]) for item in rows),
        "all_share_execution_locked": all(not bool(item["share_execution_allowed"]) for item in rows),
    }


def get_share_expiration_policy_board() -> Dict[str, Any]:
    initialize_owner_share_access_lock_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM share_expiration_policies ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 376,
        "title": "Share Expiration Policy Board",
        "ready": True,
        "expiration_policy_count": len(rows),
        "expiration_policies": rows,
        "all_one_time_access_required": all(bool(item["one_time_access_required"]) for item in rows),
        "all_expiration_enforced": all(bool(item["expiration_enforced"]) for item in rows),
        "all_share_token_creation_locked": all(not bool(item["share_token_creation_allowed"]) for item in rows),
        "all_share_execution_locked": all(not bool(item["share_execution_allowed"]) for item in rows),
    }


def get_share_route_payload_draft_builder() -> Dict[str, Any]:
    initialize_owner_share_access_lock_prep_layer()
    with _connect() as conn:
        drafts = _rows(conn, "SELECT * FROM share_route_payload_drafts ORDER BY created_at DESC")

    payloads = []
    for item in drafts:
        payloads.append(
            {
                "payload_draft_id": item["payload_draft_id"],
                "active_file_id": item["active_file_id"],
                "share_candidate_id": item["share_candidate_id"],
                "route_state": item["route_state"],
                "metadata_only": bool(item["metadata_only"]),
                "display": {
                    "share_link": "LOCKED",
                    "share_token": "LOCKED",
                    "recipient_access": "LOCKED",
                    "public_url": "LOCKED",
                    "file_body": "LOCKED",
                },
                "locks": {
                    "share_link_included": bool(item["share_link_included"]),
                    "share_token_included": bool(item["share_token_included"]),
                    "recipient_access_included": bool(item["recipient_access_included"]),
                    "public_url_included": bool(item["public_url_included"]),
                    "file_body_included": bool(item["file_body_included"]),
                },
                "payload_hash": item["payload_hash"],
            }
        )

    return {
        "section": SECTION,
        "gp": 377,
        "title": "Share Route Payload Draft Builder",
        "ready": True,
        "payload_draft_count": len(payloads),
        "payload_drafts": payloads,
        "metadata_only": True,
        "share_link_included": False,
        "share_token_included": False,
        "recipient_access_included": False,
        "public_url_included": False,
        "file_body_included": False,
    }


def get_share_receipt_draft_ledger() -> Dict[str, Any]:
    initialize_owner_share_access_lock_prep_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM share_receipt_draft_ledger ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 378,
        "title": "Share Receipt Draft Ledger",
        "ready": True,
        "receipt_draft_count": len(rows),
        "receipt_drafts": rows,
        "all_receipts_draft_locked": all(not bool(item["finalized"]) and not bool(item["finalization_allowed"]) for item in rows),
        "receipt_finalization_allowed": False,
    }


def get_share_safety_blocker_board() -> Dict[str, Any]:
    initialize_owner_share_access_lock_prep_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM share_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 379,
        "title": "Share Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_owner_share_access_lock_prep_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_owner_share_access_lock_prep_layer()

    shell = get_owner_share_access_lock_prep_shell()
    eligibility = get_share_eligibility_policy_board()
    scope = get_share_scope_contract()
    recipients = get_share_recipient_policy_board()
    approvals = get_owner_share_approval_lock_board()
    expirations = get_share_expiration_policy_board()
    payloads = get_share_route_payload_draft_builder()
    receipts = get_share_receipt_draft_ledger()
    blockers = get_share_safety_blocker_board()

    checks = {
        "previous_controlled_owner_download_ready": init["previous_controlled_owner_download_ready"] is True,
        "share_shell_ready": shell["ready"] is True,
        "share_eligibility_ready": eligibility["ready"] is True and eligibility["candidate_count"] >= 2,
        "share_candidates_owner_only": eligibility["all_candidates_owner_only"] is True,
        "share_candidates_approval_required": eligibility["all_owner_approval_required"] is True,
        "share_execution_locked_on_candidates": eligibility["no_share_execution_allowed"] is True,
        "share_links_not_created": eligibility["no_share_links_created"] is True,
        "external_recipients_not_granted": eligibility["no_external_recipients_granted"] is True,
        "share_scope_contract_ready": scope["ready"] is True and scope["scope"]["owner_only_share_prep"] is True,
        "share_scope_execution_locked": scope["scope"]["share_execution_allowed"] is False,
        "share_scope_link_creation_locked": scope["scope"]["share_link_creation_allowed"] is False,
        "recipient_policy_ready": recipients["ready"] is True and recipients["all_tower_identity_required"] is True,
        "recipient_grants_locked": recipients["all_recipient_grants_locked"] is True,
        "public_beta_access_locked": recipients["all_public_access_locked"] is True and recipients["all_beta_access_locked"] is True,
        "owner_share_approval_locks_ready": approvals["ready"] is True and approvals["all_share_execution_locked"] is True,
        "share_expiration_policy_ready": expirations["ready"] is True and expirations["all_expiration_enforced"] is True,
        "share_token_creation_locked": expirations["all_share_token_creation_locked"] is True,
        "share_payload_drafts_ready": payloads["ready"] is True and payloads["payload_draft_count"] >= 2,
        "share_payloads_metadata_only": payloads["metadata_only"] is True and payloads["share_link_included"] is False,
        "share_payloads_no_recipient_or_public_access": payloads["recipient_access_included"] is False and payloads["public_url_included"] is False,
        "share_receipt_drafts_locked": receipts["ready"] is True and receipts["all_receipts_draft_locked"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "share_execution_still_locked": LOCKS["share_execution_allowed"] is False,
        "share_link_creation_still_locked": LOCKS["share_link_creation_allowed"] is False,
        "share_token_creation_still_locked": LOCKS["share_token_creation_allowed"] is False,
        "external_recipient_grant_still_locked": LOCKS["external_recipient_grant_allowed"] is False,
        "download_link_sharing_still_locked": LOCKS["download_link_sharing_allowed"] is False,
        "raw_file_bytes_json_still_locked": LOCKS["raw_file_bytes_returned_by_json"] is False,
        "delete_restore_still_locked": LOCKS["file_delete_unlocked"] is False and LOCKS["file_restore_unlocked"] is False,
        "quarantine_release_still_locked": LOCKS["quarantine_release_allowed"] is False,
        "provider_not_required": LOCKS["provider_storage_required"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 380,
        "title": "Owner Share Access Lock Prep Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Owner share access lock prep layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — CONTROLLED SHARE GRANT EXECUTION LAYER / GP381-GP390",
        "still_locked": [
            "no share execution",
            "no share link",
            "no share token",
            "no external recipient grant",
            "no public access",
            "no beta access",
            "no download link sharing",
            "no raw file bytes returned by JSON",
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


def get_owner_share_access_lock_prep_home() -> Dict[str, Any]:
    checkpoint = get_owner_share_access_lock_prep_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_owner_share_access_lock_prep_layer() -> Dict[str, Any]:
    checkpoint = get_owner_share_access_lock_prep_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_controlled_owner_download_ready"] is True
    assert checkpoint["checks"]["share_eligibility_ready"] is True
    assert checkpoint["checks"]["share_candidates_owner_only"] is True
    assert checkpoint["checks"]["share_candidates_approval_required"] is True
    assert checkpoint["checks"]["share_execution_locked_on_candidates"] is True
    assert checkpoint["checks"]["share_links_not_created"] is True
    assert checkpoint["checks"]["external_recipients_not_granted"] is True
    assert checkpoint["checks"]["share_scope_contract_ready"] is True
    assert checkpoint["checks"]["share_scope_execution_locked"] is True
    assert checkpoint["checks"]["share_scope_link_creation_locked"] is True
    assert checkpoint["checks"]["recipient_policy_ready"] is True
    assert checkpoint["checks"]["recipient_grants_locked"] is True
    assert checkpoint["checks"]["public_beta_access_locked"] is True
    assert checkpoint["checks"]["owner_share_approval_locks_ready"] is True
    assert checkpoint["checks"]["share_expiration_policy_ready"] is True
    assert checkpoint["checks"]["share_token_creation_locked"] is True
    assert checkpoint["checks"]["share_payload_drafts_ready"] is True
    assert checkpoint["checks"]["share_payloads_metadata_only"] is True
    assert checkpoint["checks"]["share_payloads_no_recipient_or_public_access"] is True
    assert checkpoint["checks"]["share_receipt_drafts_locked"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["share_eligibility_metadata_allowed"] is True
    assert LOCKS["share_scope_policy_allowed"] is True
    assert LOCKS["share_recipient_policy_allowed"] is True
    assert LOCKS["owner_share_approval_lock_allowed"] is True
    assert LOCKS["share_expiration_policy_allowed"] is True
    assert LOCKS["share_route_payload_draft_allowed"] is True
    assert LOCKS["share_receipt_draft_allowed"] is True

    assert LOCKS["share_execution_allowed"] is False
    assert LOCKS["share_link_creation_allowed"] is False
    assert LOCKS["share_token_creation_allowed"] is False
    assert LOCKS["external_recipient_grant_allowed"] is False
    assert LOCKS["public_access_unlocked"] is False
    assert LOCKS["beta_access_unlocked"] is False
    assert LOCKS["download_link_sharing_allowed"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_share_token_exposed"] is False
    assert LOCKS["public_url_created"] is False
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
    checkpoint = get_owner_share_access_lock_prep_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "share_prep_allowed": True,
        "share_execution_allowed": False,
        "share_link_created": False,
        "external_recipient_granted": False,
        "locks_preserved": True,
    }


def get_gp371_status() -> Dict[str, Any]:
    return _gp_status(371)


def get_gp372_status() -> Dict[str, Any]:
    return _gp_status(372)


def get_gp373_status() -> Dict[str, Any]:
    return _gp_status(373)


def get_gp374_status() -> Dict[str, Any]:
    return _gp_status(374)


def get_gp375_status() -> Dict[str, Any]:
    return _gp_status(375)


def get_gp376_status() -> Dict[str, Any]:
    return _gp_status(376)


def get_gp377_status() -> Dict[str, Any]:
    return _gp_status(377)


def get_gp378_status() -> Dict[str, Any]:
    return _gp_status(378)


def get_gp379_status() -> Dict[str, Any]:
    return _gp_status(379)


def get_gp380_status() -> Dict[str, Any]:
    return _gp_status(380)
