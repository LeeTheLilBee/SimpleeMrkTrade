
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — CONTROLLED OWNER DOWNLOAD EXECUTION LAYER / GP361-GP370"
LAYER_ID = "vault_gp361_370_controlled_owner_download_execution_layer"
READINESS_LABEL = "Controlled owner download execution layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_controlled_owner_download_execution_layer.sqlite"

DEFAULT_DOWNLOAD_TTL_SECONDS = 900
MAX_DOWNLOAD_TTL_SECONDS = 1800

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.owner_file_object_write_quarantine_layer_service import get_quarantine_object_body_writer
    from vault.owner_download_lock_prep_layer_service import (
        get_download_eligibility_policy_board,
        get_download_expiration_policy_board,
        get_download_receipt_draft_ledger,
        validate_owner_download_lock_prep_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP361-GP370 requires GP351-GP360 owner download lock prep layer first."
    ) from exc


_GP361_INIT_CACHE = None

LOCKS = {
    "controlled_owner_download_execution_layer": True,
    "controlled_owner_download_execution_allowed": True,
    "owner_only_download_allowed": True,
    "scoped_internal_file_byte_verification_allowed": True,
    "controlled_download_token_fingerprint_allowed": True,
    "controlled_download_packet_metadata_allowed": True,
    "download_hash_verification_allowed": True,
    "download_access_ledger_allowed": True,
    "download_receipt_finalization_allowed": True,
    "raw_download_token_exposed": False,
    "raw_file_bytes_returned_by_json": False,
    "public_download_unlocked": False,
    "beta_download_unlocked": False,
    "public_download_url_unlocked": False,
    "share_link_unlocked": False,
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
    {"gp": 361, "title": "Controlled Owner Download Execution Shell", "status": "ready", "route": "/vault/controlled-owner-download-execution-shell.json"},
    {"gp": 362, "title": "Download Execution Scope Contract", "status": "ready", "route": "/vault/download-execution-scope-contract.json"},
    {"gp": 363, "title": "Owner Download Approval Execution Board", "status": "ready", "route": "/vault/owner-download-approval-execution-board.json"},
    {"gp": 364, "title": "Controlled Download Token Builder", "status": "ready", "route": "/vault/controlled-download-token-builder.json"},
    {"gp": 365, "title": "Controlled Download Packet Builder", "status": "ready", "route": "/vault/controlled-download-packet-builder.json"},
    {"gp": 366, "title": "Download Hash Verification Board", "status": "ready", "route": "/vault/download-hash-verification-board.json"},
    {"gp": 367, "title": "Download Access Ledger", "status": "ready", "route": "/vault/download-access-ledger.json"},
    {"gp": 368, "title": "Download Receipt Finalization Board", "status": "ready", "route": "/vault/download-receipt-finalization-board.json"},
    {"gp": 369, "title": "Download Execution Safety Blocker Board", "status": "ready", "route": "/vault/download-execution-safety-blocker-board.json"},
    {"gp": 370, "title": "Controlled Owner Download Execution Readiness Checkpoint", "status": "ready", "route": "/vault/controlled-owner-download-execution-readiness-checkpoint.json"},
]

BLOCKERS = [
    {
        "blocker_id": "no_raw_file_bytes_json",
        "label": "Raw file bytes are not returned by JSON routes",
        "blocked_action": "raw_file_bytes_json",
        "allowed": False,
        "reason": "Routes expose metadata-only download packet state, not file bytes.",
    },
    {
        "blocker_id": "no_raw_token_exposure",
        "label": "Raw download token is not exposed",
        "blocked_action": "raw_download_token_exposure",
        "allowed": False,
        "reason": "Only token fingerprints are exposed.",
    },
    {
        "blocker_id": "no_public_download",
        "label": "Public download remains locked",
        "blocked_action": "public_download",
        "allowed": False,
        "reason": "Download execution is owner-only.",
    },
    {
        "blocker_id": "no_beta_download",
        "label": "Beta download remains locked",
        "blocked_action": "beta_download",
        "allowed": False,
        "reason": "Tester/beta download is not unlocked in this layer.",
    },
    {
        "blocker_id": "no_public_url",
        "label": "Public URL remains locked",
        "blocked_action": "public_download_url",
        "allowed": False,
        "reason": "No public or shareable link is created.",
    },
    {
        "blocker_id": "no_share_link",
        "label": "Share link remains locked",
        "blocked_action": "share_link",
        "allowed": False,
        "reason": "Share links belong to a later Tower-gated share layer.",
    },
    {
        "blocker_id": "no_file_share",
        "label": "File sharing remains locked",
        "blocked_action": "file_share",
        "allowed": False,
        "reason": "Sharing is separate from owner-only download.",
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
        "reason": "Owner download does not release or move quarantine-held objects.",
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
        "reason": "Download execution does not sync externally.",
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
    return "download_execution_" + calculate_sha256_bytes(("download_execution|" + active_file_id).encode("utf-8"))[:24]


def _token_id(active_file_id: str) -> str:
    return "controlled_download_token_" + calculate_sha256_bytes(("download_token|" + active_file_id).encode("utf-8"))[:24]


def _packet_id(active_file_id: str) -> str:
    return "controlled_download_packet_" + calculate_sha256_bytes(("download_packet|" + active_file_id).encode("utf-8"))[:24]


def _verification_id(active_file_id: str) -> str:
    return "download_hash_verification_" + calculate_sha256_bytes(("download_hash|" + active_file_id).encode("utf-8"))[:24]


def _access_id(active_file_id: str) -> str:
    return "download_access_" + calculate_sha256_bytes(("download_access|" + active_file_id).encode("utf-8"))[:24]


def _receipt_id(active_file_id: str) -> str:
    return "download_receipt_final_" + calculate_sha256_bytes(("download_receipt_final|" + active_file_id).encode("utf-8"))[:24]


def _token_fingerprint(active_file_id: str, sha256_hash: str) -> str:
    material = f"owner-only-download-token|{active_file_id}|{sha256_hash}|{DEFAULT_DOWNLOAD_TTL_SECONDS}"
    return calculate_sha256_bytes(material.encode("utf-8"))


def _source_by_hash() -> Dict[str, Dict[str, Any]]:
    writer = get_quarantine_object_body_writer()
    sources: Dict[str, Dict[str, Any]] = {}

    possible_lists = []
    for key in [
        "written_objects",
        "objects",
        "body_writes",
        "writes",
        "quarantine_objects",
        "file_objects",
    ]:
        value = writer.get(key)
        if isinstance(value, list):
            possible_lists.extend(value)

    hash_keys = [
        "sha256_hash_actual",
        "sha256_hash",
        "actual_sha256_hash",
        "source_sha256_hash",
        "expected_sha256_hash",
        "file_sha256_hash",
    ]
    path_keys = [
        "relative_quarantine_path",
        "quarantine_relative_path",
        "relative_object_path",
        "object_relative_path",
        "stored_relative_path",
        "storage_relative_path",
        "path_relative_to_project",
        "relative_path",
        "file_relative_path",
        "stored_path",
        "file_path",
    ]

    for item in possible_lists:
        if not isinstance(item, dict):
            continue

        actual_hash = next((item.get(k) for k in hash_keys if item.get(k)), None)
        relative_path = next((item.get(k) for k in path_keys if item.get(k)), None)

        if actual_hash:
            normalized = dict(item)
            if relative_path:
                relative_path = str(relative_path)
                if relative_path.startswith(str(PROJECT_ROOT)):
                    try:
                        relative_path = str(Path(relative_path).relative_to(PROJECT_ROOT))
                    except Exception:
                        pass
                normalized["relative_quarantine_path"] = relative_path
            sources[str(actual_hash)] = normalized

    storage_root = PROJECT_ROOT / "data" / "vault_owned_storage"
    if storage_root.exists():
        for path in storage_root.rglob("*"):
            if not path.is_file():
                continue
            try:
                digest = calculate_sha256_bytes(path.read_bytes())
            except Exception:
                continue

            sources.setdefault(
                digest,
                {
                    "sha256_hash_actual": digest,
                    "relative_quarantine_path": str(path.relative_to(PROJECT_ROOT)),
                    "source": "vault_owned_storage_hash_scan",
                },
            )

    return sources


def _resolve_source_path(source: Dict[str, Any], source_hash: str) -> Path | None:
    if not source:
        return None

    for key in [
        "relative_quarantine_path",
        "quarantine_relative_path",
        "relative_object_path",
        "object_relative_path",
        "stored_relative_path",
        "storage_relative_path",
        "path_relative_to_project",
        "relative_path",
        "file_relative_path",
        "stored_path",
        "file_path",
    ]:
        value = source.get(key)
        if not value:
            continue

        candidate = Path(str(value))
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate

        if candidate.exists() and candidate.is_file():
            return candidate

    storage_root = PROJECT_ROOT / "data" / "vault_owned_storage"
    if storage_root.exists():
        for path in storage_root.rglob("*"):
            if not path.is_file():
                continue
            try:
                if calculate_sha256_bytes(path.read_bytes()) == source_hash:
                    return path
            except Exception:
                continue

    return None


def _candidate_source_rows() -> List[Dict[str, Any]]:
    candidates = get_download_eligibility_policy_board().get("candidates", [])
    expiration_rows = get_download_expiration_policy_board().get("expiration_policies", [])
    receipt_drafts = get_download_receipt_draft_ledger().get("receipt_drafts", [])

    expiration_by_file = {row["active_file_id"]: row for row in expiration_rows}
    receipt_by_file = {row["active_file_id"]: row for row in receipt_drafts}

    rows = []
    for row in candidates:
        active_file_id = row["active_file_id"]
        expiration = expiration_by_file.get(active_file_id, {})
        receipt = receipt_by_file.get(active_file_id, {})
        rows.append(
            {
                "active_file_id": active_file_id,
                "download_candidate_id": row["download_candidate_id"],
                "eligibility_id": row["eligibility_id"],
                "original_filename": row["original_filename"],
                "safe_stored_name": row["safe_stored_name"],
                "folder_key": row["folder_key"],
                "mission_lane": row["mission_lane"],
                "owner_lane": row["owner_lane"],
                "size_bytes": row["size_bytes"],
                "mime_type": row["mime_type"],
                "sha256_hash": row["sha256_hash"],
                "ttl_seconds": expiration.get("ttl_seconds", DEFAULT_DOWNLOAD_TTL_SECONDS),
                "max_ttl_seconds": expiration.get("max_ttl_seconds", MAX_DOWNLOAD_TTL_SECONDS),
                "one_time_download_required": bool(expiration.get("one_time_download_required", 1)),
                "draft_receipt_hash": receipt.get("receipt_hash", "download_draft_receipt_missing"),
            }
        )

    return rows


def initialize_controlled_owner_download_execution_layer() -> Dict[str, Any]:
    global _GP361_INIT_CACHE
    if _GP361_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP361_INIT_CACHE)

    previous = validate_owner_download_lock_prep_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS owner_download_approval_execution (
                execution_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                download_candidate_id TEXT NOT NULL,
                approval_state TEXT NOT NULL,
                owner_only INTEGER NOT NULL,
                approval_executed INTEGER NOT NULL,
                download_execution_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS controlled_download_tokens (
                token_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                download_candidate_id TEXT NOT NULL,
                token_state TEXT NOT NULL,
                token_fingerprint TEXT NOT NULL,
                raw_token_exposed INTEGER NOT NULL,
                ttl_seconds INTEGER NOT NULL,
                max_ttl_seconds INTEGER NOT NULL,
                one_time_download_required INTEGER NOT NULL,
                owner_only INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS controlled_download_packets (
                packet_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                download_candidate_id TEXT NOT NULL,
                token_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                source_hash TEXT NOT NULL,
                verified_hash TEXT NOT NULL,
                source_relative_path TEXT NOT NULL,
                packet_state TEXT NOT NULL,
                packet_hash TEXT NOT NULL,
                bytes_verified INTEGER NOT NULL,
                raw_file_bytes_returned_by_json INTEGER NOT NULL,
                public_url_created INTEGER NOT NULL,
                owner_only INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_hash_verification (
                verification_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                packet_id TEXT NOT NULL,
                expected_hash TEXT NOT NULL,
                actual_hash TEXT NOT NULL,
                hash_match INTEGER NOT NULL,
                bytes_verified INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_access_ledger (
                access_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                packet_id TEXT NOT NULL,
                access_scope TEXT NOT NULL,
                owner_only INTEGER NOT NULL,
                public_access_allowed INTEGER NOT NULL,
                beta_access_allowed INTEGER NOT NULL,
                share_allowed INTEGER NOT NULL,
                delete_allowed INTEGER NOT NULL,
                restore_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_receipt_finalization_board (
                final_receipt_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                packet_id TEXT NOT NULL,
                final_receipt_hash TEXT NOT NULL,
                finalized INTEGER NOT NULL,
                receipt_scope TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_execution_safety_blockers (
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
                INSERT OR REPLACE INTO download_execution_safety_blockers (
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

        sources = _source_by_hash()

        for row in _candidate_source_rows():
            active_file_id = row["active_file_id"]
            source_hash = row["sha256_hash"]
            source = sources.get(source_hash)
            path = _resolve_source_path(source, source_hash)

            if path is None:
                source_relative_path = "source_hash_not_found_download_blocked"
                raw = b""
                actual_hash = "missing"
                hash_match = False
                packet_state = "download_source_lookup_failed_locked"
            else:
                try:
                    source_relative_path = str(path.relative_to(PROJECT_ROOT))
                except Exception:
                    source_relative_path = str(path)
                raw = path.read_bytes()
                actual_hash = calculate_sha256_bytes(raw)
                hash_match = actual_hash == source_hash
                packet_state = "controlled_owner_download_packet_ready" if hash_match else "download_hash_mismatch_blocked"

            execution_id = _execution_id(active_file_id)
            token_id = _token_id(active_file_id)
            packet_id = _packet_id(active_file_id)
            token_fingerprint = _token_fingerprint(active_file_id, source_hash)

            conn.execute(
                """
                INSERT OR REPLACE INTO owner_download_approval_execution (
                    execution_id, active_file_id, download_candidate_id,
                    approval_state, owner_only, approval_executed,
                    download_execution_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    execution_id,
                    active_file_id,
                    row["download_candidate_id"],
                    "owner_download_approval_executed_for_controlled_owner_only_download",
                    1,
                    1,
                    1 if hash_match else 0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO controlled_download_tokens (
                    token_id, active_file_id, download_candidate_id,
                    token_state, token_fingerprint, raw_token_exposed,
                    ttl_seconds, max_ttl_seconds, one_time_download_required,
                    owner_only, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    token_id,
                    active_file_id,
                    row["download_candidate_id"],
                    "controlled_owner_download_token_fingerprint_created" if hash_match else "token_blocked_until_hash_match",
                    token_fingerprint,
                    0,
                    row["ttl_seconds"],
                    row["max_ttl_seconds"],
                    1 if row["one_time_download_required"] else 0,
                    1,
                    now,
                ),
            )

            packet_material = {
                "active_file_id": active_file_id,
                "download_candidate_id": row["download_candidate_id"],
                "token_fingerprint": token_fingerprint,
                "source_hash": source_hash,
                "actual_hash": actual_hash,
                "hash_match": hash_match,
                "owner_only": True,
                "raw_file_bytes_returned_by_json": False,
                "public_url_created": False,
            }
            packet_hash = calculate_sha256_bytes(repr(sorted(packet_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO controlled_download_packets (
                    packet_id, active_file_id, download_candidate_id, token_id,
                    original_filename, mime_type, source_hash, verified_hash,
                    source_relative_path, packet_state, packet_hash,
                    bytes_verified, raw_file_bytes_returned_by_json,
                    public_url_created, owner_only, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    packet_id,
                    active_file_id,
                    row["download_candidate_id"],
                    token_id,
                    row["original_filename"],
                    row["mime_type"],
                    source_hash,
                    actual_hash,
                    source_relative_path,
                    packet_state,
                    packet_hash,
                    len(raw),
                    0,
                    0,
                    1,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO download_hash_verification (
                    verification_id, active_file_id, packet_id,
                    expected_hash, actual_hash, hash_match, bytes_verified, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _verification_id(active_file_id),
                    active_file_id,
                    packet_id,
                    source_hash,
                    actual_hash,
                    1 if hash_match else 0,
                    len(raw),
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO download_access_ledger (
                    access_id, active_file_id, packet_id, access_scope,
                    owner_only, public_access_allowed, beta_access_allowed,
                    share_allowed, delete_allowed, restore_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _access_id(active_file_id),
                    active_file_id,
                    packet_id,
                    "owner_only_controlled_download",
                    1,
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
                "packet_id": packet_id,
                "packet_hash": packet_hash,
                "token_fingerprint": token_fingerprint,
                "hash_match": hash_match,
                "owner_only": True,
                "public_access_allowed": False,
                "share_allowed": False,
                "raw_file_bytes_returned_by_json": False,
            }
            final_receipt_hash = calculate_sha256_bytes(repr(sorted(receipt_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO download_receipt_finalization_board (
                    final_receipt_id, active_file_id, packet_id,
                    final_receipt_hash, finalized, receipt_scope, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _receipt_id(active_file_id),
                    active_file_id,
                    packet_id,
                    final_receipt_hash,
                    1 if hash_match else 0,
                    "controlled_owner_download_execution",
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_owner_download_lock_prep_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP361_INIT_CACHE = dict(result)
    return result


def get_controlled_owner_download_execution_shell() -> Dict[str, Any]:
    init = initialize_controlled_owner_download_execution_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 361,
        "title": "Controlled Owner Download Execution Shell",
        "ready": True,
        "initialized": init,
        "controlled_owner_download_execution_allowed": True,
        "owner_only_download_allowed": True,
        "raw_file_bytes_returned_by_json": False,
        "public_download_unlocked": False,
        "locks": LOCKS,
    }


def get_download_execution_scope_contract() -> Dict[str, Any]:
    initialize_controlled_owner_download_execution_layer()
    return {
        "section": SECTION,
        "gp": 362,
        "title": "Download Execution Scope Contract",
        "ready": True,
        "scope": {
            "owner_only": True,
            "controlled_download_execution_allowed": True,
            "internal_file_byte_verification_allowed": True,
            "token_fingerprint_allowed": True,
            "raw_token_exposed": False,
            "raw_file_bytes_returned_by_json": False,
            "public_download_allowed": False,
            "beta_download_allowed": False,
            "public_download_url_allowed": False,
            "share_allowed": False,
            "delete_allowed": False,
            "restore_allowed": False,
            "ttl_seconds": DEFAULT_DOWNLOAD_TTL_SECONDS,
            "max_ttl_seconds": MAX_DOWNLOAD_TTL_SECONDS,
            "one_time_download_required": True,
        },
    }


def get_owner_download_approval_execution_board() -> Dict[str, Any]:
    initialize_controlled_owner_download_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM owner_download_approval_execution ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 363,
        "title": "Owner Download Approval Execution Board",
        "ready": True,
        "approval_execution_count": len(rows),
        "approval_executions": rows,
        "all_owner_only": all(bool(item["owner_only"]) for item in rows),
        "all_approvals_executed": all(bool(item["approval_executed"]) for item in rows),
        "successful_download_execution_count": sum(1 for item in rows if bool(item["download_execution_allowed"])),
    }


def get_controlled_download_token_builder() -> Dict[str, Any]:
    initialize_controlled_owner_download_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM controlled_download_tokens ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 364,
        "title": "Controlled Download Token Builder",
        "ready": True,
        "token_count": len(rows),
        "tokens": rows,
        "all_owner_only": all(bool(item["owner_only"]) for item in rows),
        "no_raw_tokens_exposed": all(not bool(item["raw_token_exposed"]) for item in rows),
        "all_one_time_download_required": all(bool(item["one_time_download_required"]) for item in rows),
    }


def get_controlled_download_packet_builder() -> Dict[str, Any]:
    initialize_controlled_owner_download_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM controlled_download_packets ORDER BY created_at DESC")

    packets = []
    for item in rows:
        packets.append(
            {
                "packet_id": item["packet_id"],
                "active_file_id": item["active_file_id"],
                "download_candidate_id": item["download_candidate_id"],
                "token_id": item["token_id"],
                "original_filename": item["original_filename"],
                "mime_type": item["mime_type"],
                "source_hash": item["source_hash"],
                "verified_hash": item["verified_hash"],
                "packet_state": item["packet_state"],
                "packet_hash": item["packet_hash"],
                "bytes_verified": item["bytes_verified"],
                "owner_only": bool(item["owner_only"]),
                "display": {
                    "raw_file_bytes": "LOCKED_FROM_JSON",
                    "raw_download_token": "LOCKED_FINGERPRINT_ONLY",
                    "public_url": "LOCKED",
                    "share_link": "LOCKED",
                },
                "locks": {
                    "raw_file_bytes_returned_by_json": bool(item["raw_file_bytes_returned_by_json"]),
                    "public_url_created": bool(item["public_url_created"]),
                },
            }
        )

    return {
        "section": SECTION,
        "gp": 365,
        "title": "Controlled Download Packet Builder",
        "ready": True,
        "packet_count": len(packets),
        "packets": packets,
        "successful_packet_count": sum(1 for item in packets if item["packet_state"] == "controlled_owner_download_packet_ready"),
        "all_owner_only": all(item["owner_only"] for item in packets),
        "no_raw_file_bytes_returned_by_json": all(not item["locks"]["raw_file_bytes_returned_by_json"] for item in packets),
        "no_public_urls_created": all(not item["locks"]["public_url_created"] for item in packets),
    }


def get_download_hash_verification_board() -> Dict[str, Any]:
    initialize_controlled_owner_download_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM download_hash_verification ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 366,
        "title": "Download Hash Verification Board",
        "ready": True,
        "verification_count": len(rows),
        "verifications": rows,
        "all_hashes_match": all(bool(item["hash_match"]) for item in rows),
        "all_bytes_verified": all(int(item["bytes_verified"]) > 0 for item in rows),
    }


def get_download_access_ledger() -> Dict[str, Any]:
    initialize_controlled_owner_download_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM download_access_ledger ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 367,
        "title": "Download Access Ledger",
        "ready": True,
        "access_count": len(rows),
        "access_rows": rows,
        "all_owner_only": all(bool(item["owner_only"]) for item in rows),
        "no_public_access": all(not bool(item["public_access_allowed"]) for item in rows),
        "no_beta_access": all(not bool(item["beta_access_allowed"]) for item in rows),
        "no_share_access": all(not bool(item["share_allowed"]) for item in rows),
        "no_delete_access": all(not bool(item["delete_allowed"]) for item in rows),
        "no_restore_access": all(not bool(item["restore_allowed"]) for item in rows),
    }


def get_download_receipt_finalization_board() -> Dict[str, Any]:
    initialize_controlled_owner_download_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM download_receipt_finalization_board ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 368,
        "title": "Download Receipt Finalization Board",
        "ready": True,
        "final_receipt_count": len(rows),
        "final_receipts": rows,
        "all_receipts_finalized": all(bool(item["finalized"]) for item in rows),
    }


def get_download_execution_safety_blocker_board() -> Dict[str, Any]:
    initialize_controlled_owner_download_execution_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM download_execution_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 369,
        "title": "Download Execution Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_controlled_owner_download_execution_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_controlled_owner_download_execution_layer()

    shell = get_controlled_owner_download_execution_shell()
    scope = get_download_execution_scope_contract()
    approvals = get_owner_download_approval_execution_board()
    tokens = get_controlled_download_token_builder()
    packets = get_controlled_download_packet_builder()
    hashes = get_download_hash_verification_board()
    access = get_download_access_ledger()
    receipts = get_download_receipt_finalization_board()
    blockers = get_download_execution_safety_blocker_board()

    checks = {
        "previous_owner_download_lock_prep_ready": init["previous_owner_download_lock_prep_ready"] is True,
        "download_execution_shell_ready": shell["ready"] is True,
        "download_scope_contract_ready": scope["ready"] is True and scope["scope"]["owner_only"] is True,
        "scope_raw_file_bytes_not_returned_by_json": scope["scope"]["raw_file_bytes_returned_by_json"] is False,
        "scope_raw_token_not_exposed": scope["scope"]["raw_token_exposed"] is False,
        "owner_approval_execution_ready": approvals["ready"] is True and approvals["approval_execution_count"] >= 2,
        "download_execution_records_successful": approvals["successful_download_execution_count"] >= 2,
        "controlled_tokens_ready": tokens["ready"] is True and tokens["token_count"] >= 2,
        "no_raw_tokens_exposed": tokens["no_raw_tokens_exposed"] is True,
        "controlled_packets_ready": packets["ready"] is True and packets["packet_count"] >= 2,
        "controlled_packets_successful": packets["successful_packet_count"] >= 2,
        "packets_owner_only": packets["all_owner_only"] is True,
        "packets_no_raw_bytes_json": packets["no_raw_file_bytes_returned_by_json"] is True,
        "packets_no_public_urls": packets["no_public_urls_created"] is True,
        "hash_verification_ready": hashes["ready"] is True and hashes["all_hashes_match"] is True,
        "download_access_owner_only": access["ready"] is True and access["all_owner_only"] is True,
        "no_public_or_beta_access": access["no_public_access"] is True and access["no_beta_access"] is True,
        "no_share_delete_restore_access": access["no_share_access"] is True and access["no_delete_access"] is True and access["no_restore_access"] is True,
        "download_receipts_finalized": receipts["ready"] is True and receipts["all_receipts_finalized"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "public_download_still_locked": LOCKS["public_download_unlocked"] is False,
        "beta_download_still_locked": LOCKS["beta_download_unlocked"] is False,
        "raw_file_bytes_json_still_locked": LOCKS["raw_file_bytes_returned_by_json"] is False,
        "share_still_locked": LOCKS["file_share_unlocked"] is False,
        "quarantine_release_still_locked": LOCKS["quarantine_release_allowed"] is False,
        "provider_not_required": LOCKS["provider_storage_required"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 370,
        "title": "Controlled Owner Download Execution Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Controlled owner download execution layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — OWNER SHARE ACCESS LOCK PREP LAYER / GP371-GP380",
        "still_locked": [
            "no public download",
            "no beta download",
            "no public URL",
            "no raw file bytes returned by JSON",
            "no raw download token exposure",
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


def get_controlled_owner_download_execution_home() -> Dict[str, Any]:
    checkpoint = get_controlled_owner_download_execution_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_controlled_owner_download_execution_layer() -> Dict[str, Any]:
    checkpoint = get_controlled_owner_download_execution_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_owner_download_lock_prep_ready"] is True
    assert checkpoint["checks"]["download_execution_shell_ready"] is True
    assert checkpoint["checks"]["download_scope_contract_ready"] is True
    assert checkpoint["checks"]["scope_raw_file_bytes_not_returned_by_json"] is True
    assert checkpoint["checks"]["scope_raw_token_not_exposed"] is True
    assert checkpoint["checks"]["owner_approval_execution_ready"] is True
    assert checkpoint["checks"]["download_execution_records_successful"] is True
    assert checkpoint["checks"]["controlled_tokens_ready"] is True
    assert checkpoint["checks"]["no_raw_tokens_exposed"] is True
    assert checkpoint["checks"]["controlled_packets_ready"] is True
    assert checkpoint["checks"]["controlled_packets_successful"] is True
    assert checkpoint["checks"]["packets_no_raw_bytes_json"] is True
    assert checkpoint["checks"]["packets_no_public_urls"] is True
    assert checkpoint["checks"]["hash_verification_ready"] is True
    assert checkpoint["checks"]["download_access_owner_only"] is True
    assert checkpoint["checks"]["no_public_or_beta_access"] is True
    assert checkpoint["checks"]["no_share_delete_restore_access"] is True
    assert checkpoint["checks"]["download_receipts_finalized"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["controlled_owner_download_execution_allowed"] is True
    assert LOCKS["owner_only_download_allowed"] is True
    assert LOCKS["scoped_internal_file_byte_verification_allowed"] is True
    assert LOCKS["controlled_download_token_fingerprint_allowed"] is True
    assert LOCKS["controlled_download_packet_metadata_allowed"] is True
    assert LOCKS["download_hash_verification_allowed"] is True
    assert LOCKS["download_access_ledger_allowed"] is True
    assert LOCKS["download_receipt_finalization_allowed"] is True

    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["public_download_unlocked"] is False
    assert LOCKS["beta_download_unlocked"] is False
    assert LOCKS["public_download_url_unlocked"] is False
    assert LOCKS["share_link_unlocked"] is False
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
    checkpoint = get_controlled_owner_download_execution_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "owner_only_download_allowed": True,
        "public_download_allowed": False,
        "share_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "locks_preserved": True,
    }


def get_gp361_status() -> Dict[str, Any]:
    return _gp_status(361)


def get_gp362_status() -> Dict[str, Any]:
    return _gp_status(362)


def get_gp363_status() -> Dict[str, Any]:
    return _gp_status(363)


def get_gp364_status() -> Dict[str, Any]:
    return _gp_status(364)


def get_gp365_status() -> Dict[str, Any]:
    return _gp_status(365)


def get_gp366_status() -> Dict[str, Any]:
    return _gp_status(366)


def get_gp367_status() -> Dict[str, Any]:
    return _gp_status(367)


def get_gp368_status() -> Dict[str, Any]:
    return _gp_status(368)


def get_gp369_status() -> Dict[str, Any]:
    return _gp_status(369)


def get_gp370_status() -> Dict[str, Any]:
    return _gp_status(370)
