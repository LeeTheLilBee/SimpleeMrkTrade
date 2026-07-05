
from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — OWNER-OWNED FILE STORAGE FOUNDATION LAYER / GP261-GP270"
LAYER_ID = "vault_gp261_270_owner_owned_file_storage_foundation_layer"
READINESS_LABEL = "Owner-owned file storage foundation ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
STORAGE_ROOT = DATA_DIR / "vault_owned_storage"
OBJECTS_DIR = STORAGE_ROOT / "objects"
MANIFESTS_DIR = STORAGE_ROOT / "manifests"
RECEIPTS_DIR = STORAGE_ROOT / "receipt_drafts"
QUARANTINE_DIR = STORAGE_ROOT / "quarantine_locked"
VERSIONS_DIR = STORAGE_ROOT / "versions_locked"
TRASH_DIR = STORAGE_ROOT / "trash_locked"
DB_PATH = DATA_DIR / "vault_owner_owned_file_storage_foundation.sqlite"

HASH_ALGORITHM = "sha256"

MISSION_LANES = [
    "personal",
    "trust",
    "simplee_world",
    "atm",
    "property",
    "ob",
    "tower",
    "vault",
    "proof_demo",
]

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

LOCKS = {
    "owner_only_storage_foundation": True,
    "external_provider_required": False,
    "provider_storage_unlocked": False,
    "public_upload_unlocked": False,
    "beta_upload_unlocked": False,
    "file_preview_unlocked": False,
    "file_download_unlocked": False,
    "file_share_unlocked": False,
    "file_delete_unlocked": False,
    "file_restore_unlocked": False,
    "external_sync_unlocked": False,
    "provider_api_call_allowed": False,
    "object_body_read_allowed": False,
    "object_body_plaintext_allowed": False,
    "billing_required": False,
    "tower_unlock_required_for_storage_foundation": False,
}

PACKS = [
    {"gp": 261, "title": "Owner-Owned File Storage Shell", "status": "ready", "route": "/vault/owner-owned-file-storage-shell.json"},
    {"gp": 262, "title": "Vault Storage Root Contract", "status": "ready", "route": "/vault/vault-storage-root-contract.json"},
    {"gp": 263, "title": "Physical Object Folder Registry", "status": "ready", "route": "/vault/physical-object-folder-registry.json"},
    {"gp": 264, "title": "File Object Metadata Registry", "status": "ready", "route": "/vault/file-object-metadata-registry.json"},
    {"gp": 265, "title": "File Hash and Integrity Contract", "status": "ready", "route": "/vault/file-hash-integrity-contract.json"},
    {"gp": 266, "title": "Original Filename and Safe Stored Name Contract", "status": "ready", "route": "/vault/original-filename-safe-stored-name-contract.json"},
    {"gp": 267, "title": "Mission Lane Folder Map", "status": "ready", "route": "/vault/mission-lane-folder-map.json"},
    {"gp": 268, "title": "Upload Receipt Draft Lock", "status": "ready", "route": "/vault/upload-receipt-draft-lock.json"},
    {"gp": 269, "title": "File Storage Safety Blocker Board", "status": "ready", "route": "/vault/file-storage-safety-blocker-board.json"},
    {"gp": 270, "title": "Owner-Owned File Storage Readiness Checkpoint", "status": "ready", "route": "/vault/owner-owned-file-storage-readiness-checkpoint.json"},
]

BLOCKERS = [
    {
        "blocker_id": "no_public_upload",
        "label": "Public uploads remain locked",
        "blocked_action": "public_upload",
        "allowed": False,
        "reason": "Owner-owned storage foundation is not a public file intake layer.",
    },
    {
        "blocker_id": "no_beta_upload",
        "label": "Beta uploads remain locked",
        "blocked_action": "beta_upload",
        "allowed": False,
        "reason": "Beta access and onboarding remain locked until future owner approval.",
    },
    {
        "blocker_id": "no_provider_dependency",
        "label": "External provider dependency prohibited",
        "blocked_action": "provider_required_storage",
        "allowed": False,
        "reason": "Vault-owned storage is the authority; providers are optional warehouses later.",
    },
    {
        "blocker_id": "no_preview",
        "label": "Preview remains locked",
        "blocked_action": "file_preview",
        "allowed": False,
        "reason": "This layer records storage foundation metadata only; no object body display.",
    },
    {
        "blocker_id": "no_download",
        "label": "Download remains locked",
        "blocked_action": "file_download",
        "allowed": False,
        "reason": "Download requires future Tower permission and owner approval rules.",
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
        "reason": "Delete must become trash/recovery locked before any destructive action exists.",
    },
    {
        "blocker_id": "no_restore",
        "label": "Restore remains locked",
        "blocked_action": "file_restore",
        "allowed": False,
        "reason": "Restore belongs to a later trash/recovery and restore approval layer.",
    },
    {
        "blocker_id": "no_external_sync",
        "label": "External sync remains locked",
        "blocked_action": "external_sync",
        "allowed": False,
        "reason": "External sync is not needed for owner-owned storage foundation.",
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


def ensure_storage_directories() -> Dict[str, str]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for path in [
        STORAGE_ROOT,
        OBJECTS_DIR,
        MANIFESTS_DIR,
        RECEIPTS_DIR,
        QUARANTINE_DIR,
        VERSIONS_DIR,
        TRASH_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)

    for folder in FOLDER_MAP:
        (OBJECTS_DIR / folder["relative_path"]).mkdir(parents=True, exist_ok=True)

    return {
        "storage_root": str(STORAGE_ROOT.relative_to(PROJECT_ROOT)),
        "objects_dir": str(OBJECTS_DIR.relative_to(PROJECT_ROOT)),
        "manifests_dir": str(MANIFESTS_DIR.relative_to(PROJECT_ROOT)),
        "receipt_drafts_dir": str(RECEIPTS_DIR.relative_to(PROJECT_ROOT)),
        "quarantine_dir": str(QUARANTINE_DIR.relative_to(PROJECT_ROOT)),
        "versions_dir": str(VERSIONS_DIR.relative_to(PROJECT_ROOT)),
        "trash_dir": str(TRASH_DIR.relative_to(PROJECT_ROOT)),
    }


def initialize_owner_owned_file_storage_foundation() -> Dict[str, Any]:
    directories = ensure_storage_directories()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS storage_roots (
                root_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                relative_path TEXT NOT NULL,
                storage_mode TEXT NOT NULL,
                owner_scope TEXT NOT NULL,
                external_provider_required INTEGER NOT NULL,
                provider_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS physical_object_folders (
                folder_key TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                mission_lane TEXT NOT NULL,
                relative_path TEXT NOT NULL,
                absolute_path TEXT NOT NULL,
                folder_state TEXT NOT NULL,
                preview_locked INTEGER NOT NULL,
                download_locked INTEGER NOT NULL,
                delete_locked INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_object_metadata_registry (
                file_object_id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                safe_stored_name TEXT NOT NULL,
                mission_lane TEXT NOT NULL,
                owner_lane TEXT NOT NULL,
                folder_key TEXT NOT NULL,
                relative_object_path TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                sha256_hash TEXT NOT NULL,
                storage_state TEXT NOT NULL,
                preview_locked INTEGER NOT NULL,
                download_locked INTEGER NOT NULL,
                share_locked INTEGER NOT NULL,
                delete_locked INTEGER NOT NULL,
                restore_locked INTEGER NOT NULL,
                version_locked INTEGER NOT NULL,
                external_provider_required INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS upload_receipt_draft_locks (
                receipt_lock_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                finalization_allowed INTEGER NOT NULL,
                upload_allowed INTEGER NOT NULL,
                hash_required INTEGER NOT NULL,
                owner_receipt_required INTEGER NOT NULL,
                tower_permission_required INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS storage_safety_blockers (
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

        conn.execute(
            """
            INSERT OR REPLACE INTO storage_roots (
                root_id, label, relative_path, storage_mode, owner_scope,
                external_provider_required, provider_name, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "vault_owned_storage_root",
                "Vault-owned storage root",
                directories["storage_root"],
                "owner_owned_local_foundation",
                "owner_only",
                0,
                "none_required",
                now,
                now,
            ),
        )

        for folder in FOLDER_MAP:
            absolute = OBJECTS_DIR / folder["relative_path"]
            conn.execute(
                """
                INSERT OR REPLACE INTO physical_object_folders (
                    folder_key, display_name, mission_lane, relative_path, absolute_path,
                    folder_state, preview_locked, download_locked, delete_locked,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    folder["folder_key"],
                    folder["display_name"],
                    folder["mission_lane"],
                    folder["relative_path"],
                    str(absolute),
                    "empty_ready_locked",
                    1,
                    1,
                    1,
                    now,
                    now,
                ),
            )

        conn.execute(
            """
            INSERT OR REPLACE INTO upload_receipt_draft_locks (
                receipt_lock_id, label, finalization_allowed, upload_allowed,
                hash_required, owner_receipt_required, tower_permission_required,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "owner_upload_receipt_draft_lock",
                "Upload receipt draft lock",
                0,
                0,
                1,
                1,
                0,
                now,
                now,
            ),
        )

        for blocker in BLOCKERS:
            conn.execute(
                """
                INSERT OR REPLACE INTO storage_safety_blockers (
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

        conn.commit()

    return {
        "initialized": True,
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "directories": directories,
    }


def sanitize_original_filename(original_filename: str) -> str:
    cleaned = original_filename.strip().replace("\\", "_").replace("/", "_")
    cleaned = re.sub(r"[^A-Za-z0-9._ -]+", "_", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or "unnamed_file"


def build_safe_stored_name(original_filename: str, sha256_hash: str) -> str:
    cleaned = sanitize_original_filename(original_filename)
    suffix = Path(cleaned).suffix.lower()
    stem = Path(cleaned).stem[:80] or "file"
    digest = sha256_hash[:16]
    return f"{stem}__vault_{digest}{suffix}"


def calculate_sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def infer_mime_type(filename: str) -> str:
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or "application/octet-stream"


def get_owner_owned_file_storage_shell() -> Dict[str, Any]:
    init = initialize_owner_owned_file_storage_foundation()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 261,
        "title": "Owner-Owned File Storage Shell",
        "ready": True,
        "owner_owned_storage": True,
        "dropbox_like_direction": True,
        "external_provider_required": False,
        "storage_foundation_mode": "owner_only_local_foundation",
        "initialized": init,
        "locks": LOCKS,
        "still_locked": [
            "public_upload",
            "beta_upload",
            "file_preview",
            "file_download",
            "file_share",
            "file_delete",
            "file_restore",
            "external_sync",
            "provider_api_call",
            "object_body_read",
        ],
    }


def get_vault_storage_root_contract() -> Dict[str, Any]:
    initialize_owner_owned_file_storage_foundation()
    with _connect() as conn:
        roots = _rows(conn, "SELECT * FROM storage_roots ORDER BY root_id")

    return {
        "section": SECTION,
        "gp": 262,
        "title": "Vault Storage Root Contract",
        "ready": True,
        "storage_roots": roots,
        "contract": {
            "vault_owns_file_record": True,
            "vault_owns_receipt": True,
            "vault_owns_hash": True,
            "vault_owns_permission_policy": True,
            "external_provider_is_optional_warehouse": True,
            "external_provider_is_authority": False,
        },
    }


def get_physical_object_folder_registry() -> Dict[str, Any]:
    initialize_owner_owned_file_storage_foundation()
    with _connect() as conn:
        folders = _rows(conn, "SELECT * FROM physical_object_folders ORDER BY folder_key")

    return {
        "section": SECTION,
        "gp": 263,
        "title": "Physical Object Folder Registry",
        "ready": True,
        "folder_count": len(folders),
        "folders": folders,
        "physical_storage_created": True,
        "object_body_operations_allowed": False,
    }


def get_file_object_metadata_registry() -> Dict[str, Any]:
    initialize_owner_owned_file_storage_foundation()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM file_object_metadata_registry ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 264,
        "title": "File Object Metadata Registry",
        "ready": True,
        "file_object_count": len(rows),
        "file_objects": rows,
        "schema_contract": {
            "file_object_id": "required",
            "original_filename": "required",
            "safe_stored_name": "required",
            "mission_lane": "required",
            "folder_key": "required",
            "relative_object_path": "required",
            "mime_type": "required",
            "size_bytes": "required",
            "sha256_hash": "required",
            "storage_state": "required",
            "preview_locked": True,
            "download_locked": True,
            "share_locked": True,
            "delete_locked": True,
            "restore_locked": True,
            "version_locked": True,
        },
        "note": "Registry is ready; real upload intake remains locked for a later layer.",
    }


def get_file_hash_integrity_contract() -> Dict[str, Any]:
    sample_payload = b"vault-owner-owned-storage-foundation-sample"
    sample_hash = calculate_sha256_bytes(sample_payload)

    return {
        "section": SECTION,
        "gp": 265,
        "title": "File Hash and Integrity Contract",
        "ready": True,
        "hash_algorithm": HASH_ALGORITHM,
        "hash_required_before_storage_receipt": True,
        "hash_required_before_download_unlock": True,
        "sample_hash": sample_hash,
        "integrity_rules": [
            "Every stored file object must have a sha256 hash.",
            "Every upload receipt draft must include the sha256 hash.",
            "Every version must have its own sha256 hash.",
            "A hash mismatch blocks preview, download, restore, and sharing.",
        ],
    }


def get_original_filename_safe_stored_name_contract() -> Dict[str, Any]:
    examples = []
    for filename in [
        "Operating Agreement.pdf",
        "Trust Document Final Signed.pdf",
        "../bad/path/private-tax-record.xlsx",
        "Simplee Property Closing Packet 001.docx",
    ]:
        fake_hash = calculate_sha256_bytes(filename.encode("utf-8"))
        examples.append(
            {
                "original_filename": filename,
                "sanitized_original_filename": sanitize_original_filename(filename),
                "safe_stored_name": build_safe_stored_name(filename, fake_hash),
                "mime_type": infer_mime_type(filename),
            }
        )

    return {
        "section": SECTION,
        "gp": 266,
        "title": "Original Filename and Safe Stored Name Contract",
        "ready": True,
        "rules": {
            "preserve_original_filename_in_metadata": True,
            "store_using_safe_generated_name": True,
            "remove_path_traversal": True,
            "include_hash_prefix_in_stored_name": True,
        },
        "examples": examples,
    }


def get_mission_lane_folder_map() -> Dict[str, Any]:
    initialize_owner_owned_file_storage_foundation()
    return {
        "section": SECTION,
        "gp": 267,
        "title": "Mission Lane Folder Map",
        "ready": True,
        "mission_lanes": MISSION_LANES,
        "folder_map": FOLDER_MAP,
        "rules": {
            "every_file_requires_mission_lane": True,
            "every_file_requires_folder_key": True,
            "unmapped_lane_blocks_storage_receipt": True,
        },
    }


def get_upload_receipt_draft_lock() -> Dict[str, Any]:
    initialize_owner_owned_file_storage_foundation()
    with _connect() as conn:
        locks = _rows(conn, "SELECT * FROM upload_receipt_draft_locks ORDER BY receipt_lock_id")

    return {
        "section": SECTION,
        "gp": 268,
        "title": "Upload Receipt Draft Lock",
        "ready": True,
        "receipt_locks": locks,
        "upload_allowed": False,
        "receipt_finalization_allowed": False,
        "receipt_draft_contract": {
            "requires_original_filename": True,
            "requires_safe_stored_name": True,
            "requires_sha256_hash": True,
            "requires_size_bytes": True,
            "requires_mime_type": True,
            "requires_mission_lane": True,
            "requires_folder_key": True,
            "requires_owner_lane": True,
        },
    }


def get_file_storage_safety_blocker_board() -> Dict[str, Any]:
    initialize_owner_owned_file_storage_foundation()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM storage_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 269,
        "title": "File Storage Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if item["allowed"]),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_owner_owned_file_storage_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_owner_owned_file_storage_foundation()

    shell = get_owner_owned_file_storage_shell()
    root = get_vault_storage_root_contract()
    folders = get_physical_object_folder_registry()
    metadata = get_file_object_metadata_registry()
    hash_contract = get_file_hash_integrity_contract()
    name_contract = get_original_filename_safe_stored_name_contract()
    lane_map = get_mission_lane_folder_map()
    receipt_lock = get_upload_receipt_draft_lock()
    blocker_board = get_file_storage_safety_blocker_board()

    checks = {
        "storage_root_ready": bool(root["storage_roots"]),
        "physical_object_folders_ready": folders["folder_count"] >= len(FOLDER_MAP),
        "metadata_registry_ready": metadata["ready"],
        "hash_contract_ready": hash_contract["hash_algorithm"] == HASH_ALGORITHM,
        "safe_name_contract_ready": bool(name_contract["examples"]),
        "mission_lane_folder_map_ready": len(lane_map["folder_map"]) >= len(FOLDER_MAP),
        "upload_receipt_draft_locked": receipt_lock["upload_allowed"] is False,
        "dangerous_actions_blocked": blocker_board["all_dangerous_actions_blocked"] is True,
        "external_provider_not_required": shell["external_provider_required"] is False,
        "owner_owned_storage_foundation": shell["owner_owned_storage"] is True,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 270,
        "title": "Owner-Owned File Storage Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Owner-owned file storage foundation blocked",
        "ready": ready,
        "checks": checks,
        "initialized": init,
        "next_recommended_layer": "ARCHIVE VAULT — OWNER UPLOAD INTAKE LOCK LAYER / GP271-GP280",
        "still_locked": [
            "no public upload",
            "no beta upload",
            "no file preview",
            "no file download",
            "no file sharing",
            "no file delete",
            "no file restore",
            "no external sync",
            "no external provider dependency",
            "no provider API call",
            "no object body read endpoint",
        ],
    }


def get_owner_owned_file_storage_home() -> Dict[str, Any]:
    checkpoint = get_owner_owned_file_storage_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_owner_owned_file_storage_foundation() -> Dict[str, Any]:
    checkpoint = get_owner_owned_file_storage_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["storage_root_ready"] is True
    assert checkpoint["checks"]["physical_object_folders_ready"] is True
    assert checkpoint["checks"]["metadata_registry_ready"] is True
    assert checkpoint["checks"]["hash_contract_ready"] is True
    assert checkpoint["checks"]["safe_name_contract_ready"] is True
    assert checkpoint["checks"]["mission_lane_folder_map_ready"] is True
    assert checkpoint["checks"]["upload_receipt_draft_locked"] is True
    assert checkpoint["checks"]["dangerous_actions_blocked"] is True
    assert checkpoint["checks"]["external_provider_not_required"] is True

    assert LOCKS["external_provider_required"] is False
    assert LOCKS["provider_storage_unlocked"] is False
    assert LOCKS["public_upload_unlocked"] is False
    assert LOCKS["beta_upload_unlocked"] is False
    assert LOCKS["file_preview_unlocked"] is False
    assert LOCKS["file_download_unlocked"] is False
    assert LOCKS["file_share_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
    assert LOCKS["external_sync_unlocked"] is False
    assert LOCKS["provider_api_call_allowed"] is False
    assert LOCKS["object_body_read_allowed"] is False

    return {
        "ok": True,
        "section": SECTION,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(item for item in PACKS if item["gp"] == gp)
    checkpoint = get_owner_owned_file_storage_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "locks_preserved": True,
        "external_provider_required": False,
    }


def get_gp261_status() -> Dict[str, Any]:
    return _gp_status(261)


def get_gp262_status() -> Dict[str, Any]:
    return _gp_status(262)


def get_gp263_status() -> Dict[str, Any]:
    return _gp_status(263)


def get_gp264_status() -> Dict[str, Any]:
    return _gp_status(264)


def get_gp265_status() -> Dict[str, Any]:
    return _gp_status(265)


def get_gp266_status() -> Dict[str, Any]:
    return _gp_status(266)


def get_gp267_status() -> Dict[str, Any]:
    return _gp_status(267)


def get_gp268_status() -> Dict[str, Any]:
    return _gp_status(268)


def get_gp269_status() -> Dict[str, Any]:
    return _gp_status(269)


def get_gp270_status() -> Dict[str, Any]:
    return _gp_status(270)
