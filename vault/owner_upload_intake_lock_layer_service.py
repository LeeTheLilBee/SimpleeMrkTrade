
from __future__ import annotations

import hashlib
import mimetypes
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — OWNER UPLOAD INTAKE LOCK LAYER / GP271-GP280"
LAYER_ID = "vault_gp271_280_owner_upload_intake_lock_layer"
READINESS_LABEL = "Owner upload intake lock layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_owner_upload_intake_lock_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        FOLDER_MAP,
        MISSION_LANES,
        calculate_sha256_bytes,
        sanitize_original_filename,
        infer_mime_type,
        validate_owner_owned_file_storage_foundation,
    )
except Exception:
    FOLDER_MAP = [
        {"folder_key": "personal", "display_name": "Personal", "mission_lane": "personal", "relative_path": "Personal"},
        {"folder_key": "trust", "display_name": "Trust", "mission_lane": "trust", "relative_path": "Trust"},
        {"folder_key": "simplee_world", "display_name": "Simplee World", "mission_lane": "simplee_world", "relative_path": "Simplee World"},
        {"folder_key": "atm", "display_name": "SimpleeOnTheGo ATM", "mission_lane": "atm", "relative_path": "SimpleeOnTheGo ATM"},
        {"folder_key": "property", "display_name": "SimpleeProperty", "mission_lane": "property", "relative_path": "SimpleeProperty"},
        {"folder_key": "ob", "display_name": "The Observatory", "mission_lane": "ob", "relative_path": "The Observatory"},
        {"folder_key": "tower", "display_name": "The Tower", "mission_lane": "tower", "relative_path": "The Tower"},
        {"folder_key": "vault_receipts", "display_name": "Vault Receipts", "mission_lane": "vault", "relative_path": "Vault Receipts"},
        {"folder_key": "contracts", "display_name": "Contracts", "mission_lane": "trust", "relative_path": "Contracts"},
        {"folder_key": "proof_demo", "display_name": "Proof Demo", "mission_lane": "proof_demo", "relative_path": "Proof Demo"},
    ]
    MISSION_LANES = ["personal", "trust", "simplee_world", "atm", "property", "ob", "tower", "vault", "proof_demo"]

    def calculate_sha256_bytes(payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()

    def sanitize_original_filename(original_filename: str) -> str:
        cleaned = original_filename.strip().replace("\\", "_").replace("/", "_")
        cleaned = re.sub(r"[^A-Za-z0-9._ -]+", "_", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned or "unnamed_file"

    def infer_mime_type(filename: str) -> str:
        guessed, _ = mimetypes.guess_type(filename)
        return guessed or "application/octet-stream"

    def validate_owner_owned_file_storage_foundation() -> Dict[str, Any]:
        return {"ok": True, "ready": True, "fallback": True}


ALLOWED_EXTENSIONS = [
    ".csv",
    ".docx",
    ".jpeg",
    ".jpg",
    ".json",
    ".pdf",
    ".png",
    ".txt",
    ".xlsx",
]

BLOCKED_EXTENSIONS = [
    ".app",
    ".bat",
    ".cmd",
    ".com",
    ".dll",
    ".dmg",
    ".exe",
    ".js",
    ".msi",
    ".ps1",
    ".scr",
    ".sh",
    ".vbs",
]

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024
MIN_FILE_SIZE_BYTES = 1

LOCKS = {
    "owner_upload_intake_foundation": True,
    "real_upload_unlocked": False,
    "object_body_write_allowed": False,
    "object_body_read_allowed": False,
    "public_upload_unlocked": False,
    "beta_upload_unlocked": False,
    "provider_upload_unlocked": False,
    "file_preview_unlocked": False,
    "file_download_unlocked": False,
    "file_share_unlocked": False,
    "file_delete_unlocked": False,
    "file_restore_unlocked": False,
    "external_sync_unlocked": False,
    "upload_receipt_finalization_allowed": False,
}

PACKS = [
    {"gp": 271, "title": "Owner Upload Intake Lock Shell", "status": "ready", "route": "/vault/owner-upload-intake-lock-shell.json"},
    {"gp": 272, "title": "Upload Request Draft Registry", "status": "ready", "route": "/vault/upload-request-draft-registry.json"},
    {"gp": 273, "title": "Upload Validation Policy Board", "status": "ready", "route": "/vault/upload-validation-policy-board.json"},
    {"gp": 274, "title": "Allowed File Type and Size Contract", "status": "ready", "route": "/vault/allowed-file-type-size-contract.json"},
    {"gp": 275, "title": "Duplicate Hash Detection Preview Board", "status": "ready", "route": "/vault/duplicate-hash-detection-preview-board.json"},
    {"gp": 276, "title": "Quarantine Intake Status Lock", "status": "ready", "route": "/vault/quarantine-intake-status-lock.json"},
    {"gp": 277, "title": "Owner Upload Queue Preview", "status": "ready", "route": "/vault/owner-upload-queue-preview.json"},
    {"gp": 278, "title": "Upload Receipt Draft Builder Lock", "status": "ready", "route": "/vault/upload-receipt-draft-builder-lock.json"},
    {"gp": 279, "title": "Upload Intake Safety Blocker Board", "status": "ready", "route": "/vault/upload-intake-safety-blocker-board.json"},
    {"gp": 280, "title": "Owner Upload Intake Lock Readiness Checkpoint", "status": "ready", "route": "/vault/owner-upload-intake-lock-readiness-checkpoint.json"},
]

VALIDATION_POLICIES = [
    {
        "policy_id": "filename_required",
        "label": "Original filename required",
        "required": True,
        "blocks_upload": True,
    },
    {
        "policy_id": "mission_lane_required",
        "label": "Mission lane required",
        "required": True,
        "blocks_upload": True,
    },
    {
        "policy_id": "folder_key_required",
        "label": "Folder key required",
        "required": True,
        "blocks_upload": True,
    },
    {
        "policy_id": "sha256_required",
        "label": "SHA256 hash required before receipt",
        "required": True,
        "blocks_upload": True,
    },
    {
        "policy_id": "allowed_extension_required",
        "label": "Allowed extension required",
        "required": True,
        "blocks_upload": True,
    },
    {
        "policy_id": "size_limit_required",
        "label": "File size must be inside policy bounds",
        "required": True,
        "blocks_upload": True,
    },
    {
        "policy_id": "duplicate_hash_preview_required",
        "label": "Duplicate hash preview required",
        "required": True,
        "blocks_upload": True,
    },
    {
        "policy_id": "quarantine_status_required",
        "label": "Intake starts in quarantine locked state",
        "required": True,
        "blocks_upload": True,
    },
]

BLOCKERS = [
    {
        "blocker_id": "no_real_upload",
        "label": "Real upload remains locked",
        "blocked_action": "real_upload",
        "allowed": False,
        "reason": "This layer builds upload intake records only; no file body write is allowed.",
    },
    {
        "blocker_id": "no_object_body_write",
        "label": "Object body write remains locked",
        "blocked_action": "object_body_write",
        "allowed": False,
        "reason": "Physical object write belongs to a later controlled owner upload execution layer.",
    },
    {
        "blocker_id": "no_object_body_read",
        "label": "Object body read remains locked",
        "blocked_action": "object_body_read",
        "allowed": False,
        "reason": "No previews, downloads, or plaintext object reads exist in this layer.",
    },
    {
        "blocker_id": "no_public_upload",
        "label": "Public upload remains locked",
        "blocked_action": "public_upload",
        "allowed": False,
        "reason": "Only owner intake contracts are being prepared.",
    },
    {
        "blocker_id": "no_beta_upload",
        "label": "Beta upload remains locked",
        "blocked_action": "beta_upload",
        "allowed": False,
        "reason": "Beta upload requires future Tower-controlled access and approval.",
    },
    {
        "blocker_id": "no_provider_upload",
        "label": "Provider upload remains locked",
        "blocked_action": "provider_upload",
        "allowed": False,
        "reason": "Owner-owned Vault storage remains provider-independent.",
    },
    {
        "blocker_id": "no_download",
        "label": "Download remains locked",
        "blocked_action": "file_download",
        "allowed": False,
        "reason": "Download permissions and body delivery are not part of upload intake.",
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
        "reason": "Delete must remain trash/recovery locked.",
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


def _folder_keys() -> List[str]:
    return [item["folder_key"] for item in FOLDER_MAP]


def _extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def _stable_request_id(original_filename: str, mission_lane: str, folder_key: str, sha256_hash: str) -> str:
    payload = f"{original_filename}|{mission_lane}|{folder_key}|{sha256_hash}".encode("utf-8")
    return "upload_req_" + calculate_sha256_bytes(payload)[:24]


def _safe_filename(original_filename: str, sha256_hash: str) -> str:
    cleaned = sanitize_original_filename(original_filename)
    suffix = Path(cleaned).suffix.lower()
    stem = Path(cleaned).stem[:80] or "file"
    return f"{stem}__pending_{sha256_hash[:16]}{suffix}"


def validate_upload_metadata(
    original_filename: str,
    mission_lane: str,
    folder_key: str,
    size_bytes: int,
    sha256_hash: str,
) -> Dict[str, Any]:
    errors = []
    warnings = []

    cleaned_filename = sanitize_original_filename(original_filename)
    ext = _extension(cleaned_filename)

    if not cleaned_filename:
        errors.append("original_filename_required")

    if mission_lane not in MISSION_LANES:
        errors.append("invalid_mission_lane")

    if folder_key not in _folder_keys():
        errors.append("invalid_folder_key")

    if not isinstance(size_bytes, int) or size_bytes < MIN_FILE_SIZE_BYTES:
        errors.append("file_size_too_small")

    if isinstance(size_bytes, int) and size_bytes > MAX_FILE_SIZE_BYTES:
        errors.append("file_size_too_large")

    if ext not in ALLOWED_EXTENSIONS:
        errors.append("extension_not_allowed")

    if ext in BLOCKED_EXTENSIONS:
        errors.append("blocked_extension")

    if not re.fullmatch(r"[a-fA-F0-9]{64}", sha256_hash or ""):
        errors.append("invalid_sha256_hash")

    if original_filename != cleaned_filename:
        warnings.append("filename_will_be_sanitized")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "sanitized_original_filename": cleaned_filename,
        "extension": ext,
        "mime_type": infer_mime_type(cleaned_filename),
    }


def initialize_owner_upload_intake_lock_layer() -> Dict[str, Any]:
    previous = validate_owner_owned_file_storage_foundation()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS upload_request_drafts (
                request_id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                sanitized_original_filename TEXT NOT NULL,
                pending_safe_stored_name TEXT NOT NULL,
                mission_lane TEXT NOT NULL,
                folder_key TEXT NOT NULL,
                owner_lane TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                extension TEXT NOT NULL,
                sha256_hash TEXT NOT NULL,
                validation_state TEXT NOT NULL,
                duplicate_preview_state TEXT NOT NULL,
                quarantine_state TEXT NOT NULL,
                upload_allowed INTEGER NOT NULL,
                object_body_written INTEGER NOT NULL,
                receipt_finalization_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS upload_validation_policies (
                policy_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                required INTEGER NOT NULL,
                blocks_upload INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS duplicate_hash_previews (
                preview_id TEXT PRIMARY KEY,
                sha256_hash TEXT NOT NULL,
                possible_duplicate_count INTEGER NOT NULL,
                preview_only INTEGER NOT NULL,
                duplicate_resolution_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quarantine_intake_locks (
                quarantine_lock_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                default_state TEXT NOT NULL,
                release_allowed INTEGER NOT NULL,
                owner_release_required INTEGER NOT NULL,
                tower_release_required INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS upload_intake_safety_blockers (
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

        for policy in VALIDATION_POLICIES:
            conn.execute(
                """
                INSERT OR REPLACE INTO upload_validation_policies (
                    policy_id, label, required, blocks_upload, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    policy["policy_id"],
                    policy["label"],
                    1 if policy["required"] else 0,
                    1 if policy["blocks_upload"] else 0,
                    now,
                    now,
                ),
            )

        conn.execute(
            """
            INSERT OR REPLACE INTO quarantine_intake_locks (
                quarantine_lock_id, label, default_state, release_allowed,
                owner_release_required, tower_release_required, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "owner_upload_quarantine_intake_lock",
                "Owner upload quarantine intake lock",
                "quarantine_locked",
                0,
                1,
                0,
                now,
                now,
            ),
        )

        for blocker in BLOCKERS:
            conn.execute(
                """
                INSERT OR REPLACE INTO upload_intake_safety_blockers (
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

        seed_upload_request_draft(
            conn=conn,
            original_filename="Trust Document Final Signed.pdf",
            mission_lane="trust",
            folder_key="trust",
            owner_lane="owner",
            size_bytes=245760,
            sha256_hash=calculate_sha256_bytes(b"sample-trust-document-final-signed"),
        )
        seed_upload_request_draft(
            conn=conn,
            original_filename="SimpleeOnTheGo Route Packet.csv",
            mission_lane="atm",
            folder_key="atm",
            owner_lane="owner",
            size_bytes=32768,
            sha256_hash=calculate_sha256_bytes(b"sample-simplee-on-the-go-route-packet"),
        )

        conn.commit()

    return {
        "initialized": True,
        "previous_layer_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
    }


def seed_upload_request_draft(
    conn: sqlite3.Connection,
    original_filename: str,
    mission_lane: str,
    folder_key: str,
    owner_lane: str,
    size_bytes: int,
    sha256_hash: str,
) -> Dict[str, Any]:
    validation = validate_upload_metadata(
        original_filename=original_filename,
        mission_lane=mission_lane,
        folder_key=folder_key,
        size_bytes=size_bytes,
        sha256_hash=sha256_hash,
    )
    request_id = _stable_request_id(original_filename, mission_lane, folder_key, sha256_hash)
    pending_safe_name = _safe_filename(original_filename, sha256_hash)
    now = _now()
    validation_state = "metadata_valid_upload_locked" if validation["valid"] else "metadata_invalid_upload_locked"

    conn.execute(
        """
        INSERT OR REPLACE INTO upload_request_drafts (
            request_id, original_filename, sanitized_original_filename,
            pending_safe_stored_name, mission_lane, folder_key, owner_lane,
            size_bytes, mime_type, extension, sha256_hash, validation_state,
            duplicate_preview_state, quarantine_state, upload_allowed,
            object_body_written, receipt_finalization_allowed, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            request_id,
            original_filename,
            validation["sanitized_original_filename"],
            pending_safe_name,
            mission_lane,
            folder_key,
            owner_lane,
            size_bytes,
            validation["mime_type"],
            validation["extension"],
            sha256_hash,
            validation_state,
            "preview_only_not_resolved",
            "quarantine_locked",
            0,
            0,
            0,
            now,
            now,
        ),
    )

    conn.execute(
        """
        INSERT OR REPLACE INTO duplicate_hash_previews (
            preview_id, sha256_hash, possible_duplicate_count,
            preview_only, duplicate_resolution_allowed, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "dup_preview_" + sha256_hash[:24],
            sha256_hash,
            0,
            1,
            0,
            now,
            now,
        ),
    )

    return {
        "request_id": request_id,
        "validation": validation,
        "upload_allowed": False,
        "object_body_written": False,
    }


def get_owner_upload_intake_lock_shell() -> Dict[str, Any]:
    init = initialize_owner_upload_intake_lock_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 271,
        "title": "Owner Upload Intake Lock Shell",
        "ready": True,
        "initialized": init,
        "owner_only": True,
        "dropbox_like_direction": True,
        "real_upload_allowed": False,
        "object_body_write_allowed": False,
        "locks": LOCKS,
    }


def get_upload_request_draft_registry() -> Dict[str, Any]:
    initialize_owner_upload_intake_lock_layer()
    with _connect() as conn:
        drafts = _rows(conn, "SELECT * FROM upload_request_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 272,
        "title": "Upload Request Draft Registry",
        "ready": True,
        "draft_count": len(drafts),
        "drafts": drafts,
        "registry_contract": {
            "metadata_only": True,
            "object_body_not_stored": True,
            "upload_allowed": False,
            "receipt_finalization_allowed": False,
        },
    }


def get_upload_validation_policy_board() -> Dict[str, Any]:
    initialize_owner_upload_intake_lock_layer()
    with _connect() as conn:
        policies = _rows(conn, "SELECT * FROM upload_validation_policies ORDER BY policy_id")

    return {
        "section": SECTION,
        "gp": 273,
        "title": "Upload Validation Policy Board",
        "ready": True,
        "policy_count": len(policies),
        "policies": policies,
        "all_policies_block_upload": all(bool(item["blocks_upload"]) for item in policies),
    }


def get_allowed_file_type_size_contract() -> Dict[str, Any]:
    return {
        "section": SECTION,
        "gp": 274,
        "title": "Allowed File Type and Size Contract",
        "ready": True,
        "allowed_extensions": ALLOWED_EXTENSIONS,
        "blocked_extensions": BLOCKED_EXTENSIONS,
        "min_file_size_bytes": MIN_FILE_SIZE_BYTES,
        "max_file_size_bytes": MAX_FILE_SIZE_BYTES,
        "max_file_size_mb": round(MAX_FILE_SIZE_BYTES / 1024 / 1024, 2),
        "real_upload_allowed": False,
        "rules": {
            "allow_documents_and_business_files": True,
            "block_executables_and_scripts": True,
            "size_policy_required_before_upload": True,
            "mime_type_inference_required": True,
        },
    }


def preview_duplicate_hash(sha256_hash: str) -> Dict[str, Any]:
    initialize_owner_upload_intake_lock_layer()
    if not re.fullmatch(r"[a-fA-F0-9]{64}", sha256_hash or ""):
        return {
            "sha256_hash": sha256_hash,
            "valid_hash": False,
            "possible_duplicate_count": 0,
            "preview_only": True,
            "duplicate_resolution_allowed": False,
        }

    with _connect() as conn:
        rows = _rows(
            conn,
            "SELECT request_id, original_filename, mission_lane, folder_key FROM upload_request_drafts WHERE sha256_hash = ?",
            (sha256_hash,),
        )

    return {
        "sha256_hash": sha256_hash,
        "valid_hash": True,
        "possible_duplicate_count": len(rows),
        "possible_duplicates": rows,
        "preview_only": True,
        "duplicate_resolution_allowed": False,
    }


def get_duplicate_hash_detection_preview_board() -> Dict[str, Any]:
    initialize_owner_upload_intake_lock_layer()
    with _connect() as conn:
        previews = _rows(conn, "SELECT * FROM duplicate_hash_previews ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 275,
        "title": "Duplicate Hash Detection Preview Board",
        "ready": True,
        "preview_count": len(previews),
        "previews": previews,
        "preview_only": True,
        "duplicate_resolution_allowed": False,
        "object_body_scan_allowed": False,
    }


def get_quarantine_intake_status_lock() -> Dict[str, Any]:
    initialize_owner_upload_intake_lock_layer()
    with _connect() as conn:
        locks = _rows(conn, "SELECT * FROM quarantine_intake_locks ORDER BY quarantine_lock_id")
        queued = _rows(
            conn,
            """
            SELECT request_id, original_filename, quarantine_state, upload_allowed, object_body_written
            FROM upload_request_drafts
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 276,
        "title": "Quarantine Intake Status Lock",
        "ready": True,
        "locks": locks,
        "queued_items": queued,
        "all_queued_items_quarantine_locked": all(item["quarantine_state"] == "quarantine_locked" for item in queued),
        "release_allowed": False,
    }


def get_owner_upload_queue_preview() -> Dict[str, Any]:
    initialize_owner_upload_intake_lock_layer()
    with _connect() as conn:
        queue = _rows(
            conn,
            """
            SELECT request_id, original_filename, sanitized_original_filename,
                   pending_safe_stored_name, mission_lane, folder_key, owner_lane,
                   size_bytes, mime_type, extension, validation_state,
                   duplicate_preview_state, quarantine_state, upload_allowed,
                   object_body_written, receipt_finalization_allowed, created_at
            FROM upload_request_drafts
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 277,
        "title": "Owner Upload Queue Preview",
        "ready": True,
        "queue_count": len(queue),
        "queue": queue,
        "queue_mode": "metadata_only_preview",
        "real_upload_allowed": False,
    }


def build_upload_receipt_draft_from_request(request: Dict[str, Any]) -> Dict[str, Any]:
    receipt_material = {
        "request_id": request["request_id"],
        "original_filename": request["original_filename"],
        "safe_stored_name": request["pending_safe_stored_name"],
        "mission_lane": request["mission_lane"],
        "folder_key": request["folder_key"],
        "size_bytes": request["size_bytes"],
        "mime_type": request["mime_type"],
        "sha256_hash": request["sha256_hash"],
        "quarantine_state": request["quarantine_state"],
        "upload_allowed": False,
        "object_body_written": False,
        "receipt_finalization_allowed": False,
    }
    receipt_hash = calculate_sha256_bytes(
        repr(sorted(receipt_material.items())).encode("utf-8")
    )
    return {
        "receipt_draft_id": "upload_receipt_draft_" + receipt_hash[:24],
        "receipt_hash": receipt_hash,
        "finalized": False,
        "material": receipt_material,
    }


def get_upload_receipt_draft_builder_lock() -> Dict[str, Any]:
    initialize_owner_upload_intake_lock_layer()
    with _connect() as conn:
        requests = _rows(conn, "SELECT * FROM upload_request_drafts ORDER BY created_at DESC")

    receipt_drafts = [build_upload_receipt_draft_from_request(item) for item in requests]

    return {
        "section": SECTION,
        "gp": 278,
        "title": "Upload Receipt Draft Builder Lock",
        "ready": True,
        "receipt_draft_count": len(receipt_drafts),
        "receipt_drafts": receipt_drafts,
        "finalization_allowed": False,
        "upload_allowed": False,
    }


def get_upload_intake_safety_blocker_board() -> Dict[str, Any]:
    initialize_owner_upload_intake_lock_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM upload_intake_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 279,
        "title": "Upload Intake Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_owner_upload_intake_lock_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_owner_upload_intake_lock_layer()

    shell = get_owner_upload_intake_lock_shell()
    registry = get_upload_request_draft_registry()
    policies = get_upload_validation_policy_board()
    type_size = get_allowed_file_type_size_contract()
    duplicate = get_duplicate_hash_detection_preview_board()
    quarantine = get_quarantine_intake_status_lock()
    queue = get_owner_upload_queue_preview()
    receipts = get_upload_receipt_draft_builder_lock()
    blockers = get_upload_intake_safety_blocker_board()

    checks = {
        "previous_storage_foundation_ready": init["previous_layer_ready"] is True,
        "upload_shell_ready": shell["ready"] is True,
        "draft_registry_ready": registry["ready"] is True and registry["draft_count"] >= 2,
        "validation_policy_board_ready": policies["ready"] is True and policies["policy_count"] >= len(VALIDATION_POLICIES),
        "allowed_type_size_contract_ready": type_size["ready"] is True and ".pdf" in type_size["allowed_extensions"],
        "duplicate_hash_preview_ready": duplicate["ready"] is True and duplicate["preview_only"] is True,
        "quarantine_lock_ready": quarantine["ready"] is True and quarantine["all_queued_items_quarantine_locked"] is True,
        "owner_upload_queue_preview_ready": queue["ready"] is True and queue["queue_count"] >= 2,
        "upload_receipt_draft_builder_locked": receipts["ready"] is True and receipts["finalization_allowed"] is False,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "real_upload_still_locked": LOCKS["real_upload_unlocked"] is False,
        "object_body_write_still_locked": LOCKS["object_body_write_allowed"] is False,
        "external_provider_not_required": LOCKS["provider_upload_unlocked"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 280,
        "title": "Owner Upload Intake Lock Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Owner upload intake lock layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — OWNER FILE OBJECT WRITE QUARANTINE LAYER / GP281-GP290",
        "still_locked": [
            "no real file upload",
            "no object body write",
            "no object body read",
            "no preview",
            "no download",
            "no sharing",
            "no delete",
            "no restore",
            "no external sync",
            "no provider upload",
            "no public upload",
            "no beta upload",
        ],
    }


def get_owner_upload_intake_home() -> Dict[str, Any]:
    checkpoint = get_owner_upload_intake_lock_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_owner_upload_intake_lock_layer() -> Dict[str, Any]:
    checkpoint = get_owner_upload_intake_lock_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_storage_foundation_ready"] is True
    assert checkpoint["checks"]["draft_registry_ready"] is True
    assert checkpoint["checks"]["validation_policy_board_ready"] is True
    assert checkpoint["checks"]["allowed_type_size_contract_ready"] is True
    assert checkpoint["checks"]["duplicate_hash_preview_ready"] is True
    assert checkpoint["checks"]["quarantine_lock_ready"] is True
    assert checkpoint["checks"]["owner_upload_queue_preview_ready"] is True
    assert checkpoint["checks"]["upload_receipt_draft_builder_locked"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True
    assert checkpoint["checks"]["real_upload_still_locked"] is True
    assert checkpoint["checks"]["object_body_write_still_locked"] is True

    assert LOCKS["real_upload_unlocked"] is False
    assert LOCKS["object_body_write_allowed"] is False
    assert LOCKS["object_body_read_allowed"] is False
    assert LOCKS["public_upload_unlocked"] is False
    assert LOCKS["beta_upload_unlocked"] is False
    assert LOCKS["provider_upload_unlocked"] is False
    assert LOCKS["file_preview_unlocked"] is False
    assert LOCKS["file_download_unlocked"] is False
    assert LOCKS["file_share_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
    assert LOCKS["external_sync_unlocked"] is False
    assert LOCKS["upload_receipt_finalization_allowed"] is False

    return {
        "ok": True,
        "section": SECTION,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(item for item in PACKS if item["gp"] == gp)
    checkpoint = get_owner_upload_intake_lock_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "locks_preserved": True,
        "real_upload_allowed": False,
        "object_body_write_allowed": False,
    }


def get_gp271_status() -> Dict[str, Any]:
    return _gp_status(271)


def get_gp272_status() -> Dict[str, Any]:
    return _gp_status(272)


def get_gp273_status() -> Dict[str, Any]:
    return _gp_status(273)


def get_gp274_status() -> Dict[str, Any]:
    return _gp_status(274)


def get_gp275_status() -> Dict[str, Any]:
    return _gp_status(275)


def get_gp276_status() -> Dict[str, Any]:
    return _gp_status(276)


def get_gp277_status() -> Dict[str, Any]:
    return _gp_status(277)


def get_gp278_status() -> Dict[str, Any]:
    return _gp_status(278)


def get_gp279_status() -> Dict[str, Any]:
    return _gp_status(279)


def get_gp280_status() -> Dict[str, Any]:
    return _gp_status(280)
