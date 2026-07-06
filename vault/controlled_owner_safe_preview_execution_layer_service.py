
from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — CONTROLLED OWNER SAFE PREVIEW EXECUTION LAYER / GP341-GP350"
LAYER_ID = "vault_gp341_350_controlled_owner_safe_preview_execution_layer"
READINESS_LABEL = "Controlled owner safe preview execution layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_controlled_owner_safe_preview_execution_layer.sqlite"

MAX_PREVIEW_BYTES = 4096
MAX_PREVIEW_CHARS = 800

BODY_READ_MIME_TYPES = {
    "text/csv",
    "text/plain",
    "application/json",
}

RENDERER_PENDING_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.owner_file_object_write_quarantine_layer_service import get_quarantine_object_body_writer
    from vault.owner_safe_preview_lock_prep_layer_service import (
        get_preview_eligibility_policy_board,
        get_preview_route_payload_draft_builder,
        get_preview_receipt_draft_ledger,
        validate_owner_safe_preview_lock_prep_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP341-GP350 requires GP331-GP340 owner safe preview lock prep layer first."
    ) from exc


_GP341_INIT_CACHE = None

LOCKS = {
    "controlled_owner_safe_preview_execution_layer": True,
    "controlled_owner_preview_execution_allowed": True,
    "scoped_object_body_read_allowed": True,
    "scoped_plaintext_extraction_allowed": True,
    "safe_preview_artifact_write_allowed": True,
    "preview_cache_index_allowed": True,
    "preview_access_ledger_allowed": True,
    "preview_receipt_finalization_allowed": True,
    "owner_only_preview_allowed": True,
    "general_object_body_read_allowed": False,
    "public_preview_unlocked": False,
    "beta_preview_unlocked": False,
    "preview_download_allowed": False,
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
    {"gp": 341, "title": "Controlled Owner Safe Preview Execution Shell", "status": "ready", "route": "/vault/controlled-owner-safe-preview-execution-shell.json"},
    {"gp": 342, "title": "Preview Execution Scope Contract", "status": "ready", "route": "/vault/preview-execution-scope-contract.json"},
    {"gp": 343, "title": "Controlled Preview Body Reader", "status": "ready", "route": "/vault/controlled-preview-body-reader.json"},
    {"gp": 344, "title": "Safe Preview Artifact Builder", "status": "ready", "route": "/vault/safe-preview-artifact-builder.json"},
    {"gp": 345, "title": "Preview Cache Index", "status": "ready", "route": "/vault/preview-cache-index.json"},
    {"gp": 346, "title": "Preview Access Ledger", "status": "ready", "route": "/vault/preview-access-ledger.json"},
    {"gp": 347, "title": "Preview Receipt Finalization Board", "status": "ready", "route": "/vault/preview-receipt-finalization-board.json"},
    {"gp": 348, "title": "Preview Redaction Result Board", "status": "ready", "route": "/vault/preview-redaction-result-board.json"},
    {"gp": 349, "title": "Preview Execution Safety Blocker Board", "status": "ready", "route": "/vault/preview-execution-safety-blocker-board.json"},
    {"gp": 350, "title": "Controlled Owner Safe Preview Execution Readiness Checkpoint", "status": "ready", "route": "/vault/controlled-owner-safe-preview-execution-readiness-checkpoint.json"},
]

BLOCKERS = [
    {
        "blocker_id": "no_public_preview",
        "label": "Public preview remains locked",
        "blocked_action": "public_preview",
        "allowed": False,
        "reason": "Preview execution is owner-only.",
    },
    {
        "blocker_id": "no_beta_preview",
        "label": "Beta preview remains locked",
        "blocked_action": "beta_preview",
        "allowed": False,
        "reason": "No tester preview access exists in this layer.",
    },
    {
        "blocker_id": "no_preview_download",
        "label": "Preview download remains locked",
        "blocked_action": "preview_download",
        "allowed": False,
        "reason": "Preview artifacts are view-only metadata/text snippets, not downloadable files.",
    },
    {
        "blocker_id": "no_file_download",
        "label": "File download remains locked",
        "blocked_action": "file_download",
        "allowed": False,
        "reason": "Download belongs to a later controlled owner download layer.",
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
        "reason": "Preview does not release or move physical objects.",
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
        "reason": "Preview execution does not sync externally.",
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


def _preview_artifact_id(active_file_id: str) -> str:
    return "preview_artifact_" + calculate_sha256_bytes(("artifact|" + active_file_id).encode("utf-8"))[:24]


def _preview_access_id(active_file_id: str) -> str:
    return "preview_access_" + calculate_sha256_bytes(("access|" + active_file_id).encode("utf-8"))[:24]


def _preview_receipt_final_id(active_file_id: str) -> str:
    return "preview_receipt_final_" + calculate_sha256_bytes(("final|" + active_file_id).encode("utf-8"))[:24]


def _redaction_result_id(active_file_id: str) -> str:
    return "preview_redaction_" + calculate_sha256_bytes(("redaction|" + active_file_id).encode("utf-8"))[:24]


def _decode_preview(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_PREVIEW_CHARS]


def _preview_hash(preview_text: str, active_file_id: str, sha256_hash: str) -> str:
    material = {
        "active_file_id": active_file_id,
        "source_hash": sha256_hash,
        "preview_text": preview_text,
        "scope": "controlled_owner_safe_preview",
    }
    return calculate_sha256_bytes(repr(sorted(material.items())).encode("utf-8"))



def _source_by_hash() -> Dict[str, Dict[str, Any]]:
    """
    Robust source lookup for preview execution.

    Upstream quarantine/write layers have evolved across packs, so this accepts
    multiple hash/path key names and falls back to scanning the Vault-owned
    storage folder by SHA256. This keeps preview execution real: it still reads
    only actual quarantine-written bytes, never invented content.
    """
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


def initialize_controlled_owner_safe_preview_execution_layer() -> Dict[str, Any]:
    global _GP341_INIT_CACHE
    if _GP341_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP341_INIT_CACHE)

    previous = validate_owner_safe_preview_lock_prep_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS controlled_preview_body_reads (
                read_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                eligibility_id TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                source_hash TEXT NOT NULL,
                source_relative_path TEXT NOT NULL,
                read_state TEXT NOT NULL,
                body_read_executed INTEGER NOT NULL,
                bytes_read INTEGER NOT NULL,
                owner_only INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS safe_preview_artifacts (
                preview_artifact_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                eligibility_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                preview_family TEXT NOT NULL,
                artifact_state TEXT NOT NULL,
                preview_text TEXT NOT NULL,
                preview_hash TEXT NOT NULL,
                rendered_preview_included INTEGER NOT NULL,
                download_url_included INTEGER NOT NULL,
                owner_only INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preview_cache_index (
                preview_artifact_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                cache_state TEXT NOT NULL,
                metadata_only_index INTEGER NOT NULL,
                cache_read_allowed INTEGER NOT NULL,
                cache_write_executed INTEGER NOT NULL,
                preview_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preview_access_ledger (
                access_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                preview_artifact_id TEXT NOT NULL,
                access_scope TEXT NOT NULL,
                owner_only INTEGER NOT NULL,
                public_access_allowed INTEGER NOT NULL,
                beta_access_allowed INTEGER NOT NULL,
                download_allowed INTEGER NOT NULL,
                share_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preview_receipt_finalization_board (
                final_receipt_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                preview_artifact_id TEXT NOT NULL,
                final_receipt_hash TEXT NOT NULL,
                finalized INTEGER NOT NULL,
                receipt_scope TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preview_redaction_results (
                redaction_result_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                preview_artifact_id TEXT NOT NULL,
                redaction_state TEXT NOT NULL,
                object_body_excluded INTEGER NOT NULL,
                plaintext_limited INTEGER NOT NULL,
                physical_path_excluded INTEGER NOT NULL,
                download_url_excluded INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preview_execution_safety_blockers (
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
                INSERT OR REPLACE INTO preview_execution_safety_blockers (
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
        candidates = get_preview_eligibility_policy_board().get("candidates", [])

        for item in candidates:
            active_file_id = item["active_file_id"]
            eligibility_id = item["eligibility_id"]
            mime_type = item["mime_type"]
            source_hash = item["sha256_hash"]
            source = sources.get(source_hash)
            preview_artifact_id = _preview_artifact_id(active_file_id)

            body_read_executed = False
            bytes_read = 0
            preview_text = "PREVIEW_RENDERER_PENDING_LOCKED"
            artifact_state = "renderer_pending_locked"
            source_relative_path = "not_read_renderer_pending"

            if bool(item["policy_eligible"]) and mime_type in BODY_READ_MIME_TYPES and source:
                path = _resolve_source_path(source, source_hash)
                if path is not None:
                    try:
                        source_relative_path = str(path.relative_to(PROJECT_ROOT))
                    except Exception:
                        source_relative_path = str(path)
                    raw = path.read_bytes()[:MAX_PREVIEW_BYTES]
                    body_read_executed = True
                    bytes_read = len(raw)
                    preview_text = _decode_preview(raw)
                    artifact_state = "controlled_owner_safe_preview_rendered_text_snippet"
                else:
                    source_relative_path = "source_hash_not_found_for_safe_text_preview"
                    artifact_state = "safe_text_source_lookup_failed_locked"
                    preview_text = "SAFE_TEXT_SOURCE_LOOKUP_FAILED_LOCKED"

            elif mime_type in RENDERER_PENDING_MIME_TYPES:
                artifact_state = "policy_eligible_renderer_pending_locked"
                preview_text = "SAFE_PREVIEW_RENDERER_PENDING"

            else:
                artifact_state = "preview_not_eligible_or_review_required_locked"
                preview_text = "PREVIEW_NOT_ELIGIBLE_OR_REVIEW_REQUIRED"

            preview_hash = _preview_hash(preview_text, active_file_id, source_hash)

            conn.execute(
                """
                INSERT OR REPLACE INTO controlled_preview_body_reads (
                    read_id, active_file_id, eligibility_id, mime_type,
                    source_hash, source_relative_path, read_state,
                    body_read_executed, bytes_read, owner_only, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "body_read_" + preview_artifact_id,
                    active_file_id,
                    eligibility_id,
                    mime_type,
                    source_hash,
                    source_relative_path,
                    "scoped_safe_text_body_read_executed" if body_read_executed else "body_read_not_executed_renderer_or_review_locked",
                    1 if body_read_executed else 0,
                    bytes_read,
                    1,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO safe_preview_artifacts (
                    preview_artifact_id, active_file_id, eligibility_id,
                    original_filename, mime_type, preview_family,
                    artifact_state, preview_text, preview_hash,
                    rendered_preview_included, download_url_included,
                    owner_only, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    preview_artifact_id,
                    active_file_id,
                    eligibility_id,
                    item["original_filename"],
                    mime_type,
                    item["preview_family"],
                    artifact_state,
                    preview_text,
                    preview_hash,
                    1 if body_read_executed else 0,
                    0,
                    1,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO preview_cache_index (
                    preview_artifact_id, active_file_id, cache_state,
                    metadata_only_index, cache_read_allowed, cache_write_executed,
                    preview_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    preview_artifact_id,
                    active_file_id,
                    "preview_cache_indexed_owner_only",
                    1,
                    1,
                    1,
                    preview_hash,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO preview_access_ledger (
                    access_id, active_file_id, preview_artifact_id,
                    access_scope, owner_only, public_access_allowed,
                    beta_access_allowed, download_allowed, share_allowed,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _preview_access_id(active_file_id),
                    active_file_id,
                    preview_artifact_id,
                    "owner_only_controlled_safe_preview",
                    1,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            receipt_material = {
                "active_file_id": active_file_id,
                "preview_artifact_id": preview_artifact_id,
                "preview_hash": preview_hash,
                "owner_only": True,
                "download_allowed": False,
                "share_allowed": False,
            }
            final_receipt_hash = calculate_sha256_bytes(repr(sorted(receipt_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO preview_receipt_finalization_board (
                    final_receipt_id, active_file_id, preview_artifact_id,
                    final_receipt_hash, finalized, receipt_scope, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _preview_receipt_final_id(active_file_id),
                    active_file_id,
                    preview_artifact_id,
                    final_receipt_hash,
                    1,
                    "controlled_owner_safe_preview_execution",
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO preview_redaction_results (
                    redaction_result_id, active_file_id, preview_artifact_id,
                    redaction_state, object_body_excluded, plaintext_limited,
                    physical_path_excluded, download_url_excluded, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _redaction_result_id(active_file_id),
                    active_file_id,
                    preview_artifact_id,
                    "redacted_safe_preview_result_ready",
                    1,
                    1,
                    1,
                    1,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_safe_preview_lock_prep_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP341_INIT_CACHE = dict(result)
    return result


def get_controlled_owner_safe_preview_execution_shell() -> Dict[str, Any]:
    init = initialize_controlled_owner_safe_preview_execution_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 341,
        "title": "Controlled Owner Safe Preview Execution Shell",
        "ready": True,
        "initialized": init,
        "controlled_owner_preview_execution_allowed": True,
        "owner_only_preview_allowed": True,
        "download_allowed": False,
        "share_allowed": False,
        "locks": LOCKS,
    }


def get_preview_execution_scope_contract() -> Dict[str, Any]:
    initialize_controlled_owner_safe_preview_execution_layer()
    return {
        "section": SECTION,
        "gp": 342,
        "title": "Preview Execution Scope Contract",
        "ready": True,
        "scope": {
            "owner_only": True,
            "safe_text_like_mime_body_read_allowed": True,
            "allowed_body_read_mime_types": sorted(BODY_READ_MIME_TYPES),
            "renderer_pending_mime_types": sorted(RENDERER_PENDING_MIME_TYPES),
            "max_preview_bytes": MAX_PREVIEW_BYTES,
            "max_preview_chars": MAX_PREVIEW_CHARS,
            "download_allowed": False,
            "share_allowed": False,
            "delete_allowed": False,
            "restore_allowed": False,
            "public_access_allowed": False,
            "beta_access_allowed": False,
        },
    }


def get_controlled_preview_body_reader() -> Dict[str, Any]:
    initialize_controlled_owner_safe_preview_execution_layer()
    with _connect() as conn:
        reads = _rows(conn, "SELECT * FROM controlled_preview_body_reads ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 343,
        "title": "Controlled Preview Body Reader",
        "ready": True,
        "read_count": len(reads),
        "body_reads": reads,
        "executed_read_count": sum(1 for item in reads if bool(item["body_read_executed"])),
        "all_reads_owner_only": all(bool(item["owner_only"]) for item in reads),
        "no_download_allowed": True,
    }


def get_safe_preview_artifact_builder() -> Dict[str, Any]:
    initialize_controlled_owner_safe_preview_execution_layer()
    with _connect() as conn:
        artifacts = _rows(conn, "SELECT * FROM safe_preview_artifacts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 344,
        "title": "Safe Preview Artifact Builder",
        "ready": True,
        "artifact_count": len(artifacts),
        "rendered_text_preview_count": sum(1 for item in artifacts if bool(item["rendered_preview_included"])),
        "artifacts": artifacts,
        "all_artifacts_owner_only": all(bool(item["owner_only"]) for item in artifacts),
        "all_download_urls_excluded": all(not bool(item["download_url_included"]) for item in artifacts),
    }


def get_preview_cache_index() -> Dict[str, Any]:
    initialize_controlled_owner_safe_preview_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM preview_cache_index ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 345,
        "title": "Preview Cache Index",
        "ready": True,
        "cache_entry_count": len(rows),
        "cache_entries": rows,
        "metadata_only_index": True,
        "all_cache_entries_indexed": all(bool(item["cache_write_executed"]) for item in rows),
    }


def get_preview_access_ledger() -> Dict[str, Any]:
    initialize_controlled_owner_safe_preview_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM preview_access_ledger ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 346,
        "title": "Preview Access Ledger",
        "ready": True,
        "access_count": len(rows),
        "access_rows": rows,
        "all_owner_only": all(bool(item["owner_only"]) for item in rows),
        "no_public_access": all(not bool(item["public_access_allowed"]) for item in rows),
        "no_beta_access": all(not bool(item["beta_access_allowed"]) for item in rows),
        "no_download_access": all(not bool(item["download_allowed"]) for item in rows),
        "no_share_access": all(not bool(item["share_allowed"]) for item in rows),
    }


def get_preview_receipt_finalization_board() -> Dict[str, Any]:
    initialize_controlled_owner_safe_preview_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM preview_receipt_finalization_board ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 347,
        "title": "Preview Receipt Finalization Board",
        "ready": True,
        "final_receipt_count": len(rows),
        "final_receipts": rows,
        "all_receipts_finalized": all(bool(item["finalized"]) for item in rows),
    }


def get_preview_redaction_result_board() -> Dict[str, Any]:
    initialize_controlled_owner_safe_preview_execution_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM preview_redaction_results ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 348,
        "title": "Preview Redaction Result Board",
        "ready": True,
        "redaction_result_count": len(rows),
        "redaction_results": rows,
        "all_object_bodies_excluded": all(bool(item["object_body_excluded"]) for item in rows),
        "all_plaintext_limited": all(bool(item["plaintext_limited"]) for item in rows),
        "all_physical_paths_excluded": all(bool(item["physical_path_excluded"]) for item in rows),
        "all_download_urls_excluded": all(bool(item["download_url_excluded"]) for item in rows),
    }


def get_preview_execution_safety_blocker_board() -> Dict[str, Any]:
    initialize_controlled_owner_safe_preview_execution_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM preview_execution_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 349,
        "title": "Preview Execution Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_controlled_owner_safe_preview_execution_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_controlled_owner_safe_preview_execution_layer()

    shell = get_controlled_owner_safe_preview_execution_shell()
    scope = get_preview_execution_scope_contract()
    reader = get_controlled_preview_body_reader()
    artifacts = get_safe_preview_artifact_builder()
    cache = get_preview_cache_index()
    access = get_preview_access_ledger()
    receipts = get_preview_receipt_finalization_board()
    redaction = get_preview_redaction_result_board()
    blockers = get_preview_execution_safety_blocker_board()

    checks = {
        "previous_safe_preview_lock_prep_ready": init["previous_safe_preview_lock_prep_ready"] is True,
        "execution_shell_ready": shell["ready"] is True,
        "scope_contract_ready": scope["ready"] is True and scope["scope"]["owner_only"] is True,
        "body_reader_ready": reader["ready"] is True and reader["read_count"] >= 2,
        "at_least_one_safe_text_preview_body_read": reader["executed_read_count"] >= 1,
        "preview_artifacts_ready": artifacts["ready"] is True and artifacts["artifact_count"] >= 2,
        "at_least_one_text_preview_rendered": artifacts["rendered_text_preview_count"] >= 1,
        "all_artifacts_owner_only": artifacts["all_artifacts_owner_only"] is True,
        "download_urls_excluded": artifacts["all_download_urls_excluded"] is True,
        "cache_index_ready": cache["ready"] is True and cache["all_cache_entries_indexed"] is True,
        "access_ledger_owner_only": access["ready"] is True and access["all_owner_only"] is True,
        "no_public_or_beta_access": access["no_public_access"] is True and access["no_beta_access"] is True,
        "no_download_or_share_access": access["no_download_access"] is True and access["no_share_access"] is True,
        "receipts_finalized": receipts["ready"] is True and receipts["all_receipts_finalized"] is True,
        "redaction_ready": redaction["ready"] is True and redaction["all_object_bodies_excluded"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "download_still_locked": LOCKS["file_download_unlocked"] is False,
        "share_still_locked": LOCKS["file_share_unlocked"] is False,
        "quarantine_release_still_locked": LOCKS["quarantine_release_allowed"] is False,
        "provider_not_required": LOCKS["provider_storage_required"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 350,
        "title": "Controlled Owner Safe Preview Execution Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Controlled owner safe preview execution layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — OWNER DOWNLOAD LOCK PREP LAYER / GP351-GP360",
        "still_locked": [
            "no download",
            "no sharing",
            "no delete",
            "no restore",
            "no public preview",
            "no beta preview",
            "no public upload",
            "no beta upload",
            "no provider upload",
            "no quarantine release",
            "no physical object move",
            "no external sync",
        ],
    }


def get_controlled_owner_safe_preview_execution_home() -> Dict[str, Any]:
    checkpoint = get_controlled_owner_safe_preview_execution_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_controlled_owner_safe_preview_execution_layer() -> Dict[str, Any]:
    checkpoint = get_controlled_owner_safe_preview_execution_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_safe_preview_lock_prep_ready"] is True
    assert checkpoint["checks"]["at_least_one_safe_text_preview_body_read"] is True
    assert checkpoint["checks"]["at_least_one_text_preview_rendered"] is True
    assert checkpoint["checks"]["all_artifacts_owner_only"] is True
    assert checkpoint["checks"]["download_urls_excluded"] is True
    assert checkpoint["checks"]["access_ledger_owner_only"] is True
    assert checkpoint["checks"]["no_public_or_beta_access"] is True
    assert checkpoint["checks"]["no_download_or_share_access"] is True
    assert checkpoint["checks"]["receipts_finalized"] is True
    assert checkpoint["checks"]["redaction_ready"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["controlled_owner_preview_execution_allowed"] is True
    assert LOCKS["scoped_object_body_read_allowed"] is True
    assert LOCKS["safe_preview_artifact_write_allowed"] is True
    assert LOCKS["owner_only_preview_allowed"] is True

    assert LOCKS["general_object_body_read_allowed"] is False
    assert LOCKS["public_preview_unlocked"] is False
    assert LOCKS["beta_preview_unlocked"] is False
    assert LOCKS["preview_download_allowed"] is False
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
    checkpoint = get_controlled_owner_safe_preview_execution_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "owner_only_preview_allowed": True,
        "download_allowed": False,
        "share_allowed": False,
        "locks_preserved": True,
    }


def get_gp341_status() -> Dict[str, Any]:
    return _gp_status(341)


def get_gp342_status() -> Dict[str, Any]:
    return _gp_status(342)


def get_gp343_status() -> Dict[str, Any]:
    return _gp_status(343)


def get_gp344_status() -> Dict[str, Any]:
    return _gp_status(344)


def get_gp345_status() -> Dict[str, Any]:
    return _gp_status(345)


def get_gp346_status() -> Dict[str, Any]:
    return _gp_status(346)


def get_gp347_status() -> Dict[str, Any]:
    return _gp_status(347)


def get_gp348_status() -> Dict[str, Any]:
    return _gp_status(348)


def get_gp349_status() -> Dict[str, Any]:
    return _gp_status(349)


def get_gp350_status() -> Dict[str, Any]:
    return _gp_status(350)
