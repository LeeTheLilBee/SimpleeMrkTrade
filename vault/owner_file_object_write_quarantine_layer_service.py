
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — OWNER FILE OBJECT WRITE QUARANTINE LAYER / GP281-GP290"
LAYER_ID = "vault_gp281_290_owner_file_object_write_quarantine_layer"
READINESS_LABEL = "Owner file object write quarantine layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
STORAGE_ROOT = DATA_DIR / "vault_owned_storage"
QUARANTINE_DIR = STORAGE_ROOT / "quarantine_locked"
MANIFESTS_DIR = STORAGE_ROOT / "manifests"
DB_PATH = DATA_DIR / "vault_owner_file_object_write_quarantine_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
        validate_owner_owned_file_storage_foundation,
    )
    from vault.owner_upload_intake_lock_layer_service import (
        get_owner_upload_queue_preview,
        get_upload_request_draft_registry,
        validate_owner_upload_intake_lock_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP281-GP290 requires GP261-GP270 and GP271-GP280 service files to exist first."
    ) from exc


LOCKS = {
    "owner_quarantine_write_layer": True,
    "controlled_quarantine_write_allowed": True,
    "raw_user_upload_endpoint_allowed": False,
    "public_upload_unlocked": False,
    "beta_upload_unlocked": False,
    "provider_upload_unlocked": False,
    "provider_storage_required": False,
    "object_body_read_allowed": False,
    "object_body_preview_allowed": False,
    "file_download_unlocked": False,
    "file_share_unlocked": False,
    "file_delete_unlocked": False,
    "file_restore_unlocked": False,
    "external_sync_unlocked": False,
    "quarantine_release_allowed": False,
    "registry_promotion_allowed": False,
}

PACKS = [
    {"gp": 281, "title": "Owner File Object Write Quarantine Shell", "status": "ready", "route": "/vault/owner-file-object-write-quarantine-shell.json"},
    {"gp": 282, "title": "Controlled Owner Object Write Contract", "status": "ready", "route": "/vault/controlled-owner-object-write-contract.json"},
    {"gp": 283, "title": "Quarantine Object Body Writer", "status": "ready", "route": "/vault/quarantine-object-body-writer.json"},
    {"gp": 284, "title": "File Object Registry Insert Handoff", "status": "ready", "route": "/vault/file-object-registry-insert-handoff.json"},
    {"gp": 285, "title": "Hash Verification After Write Board", "status": "ready", "route": "/vault/hash-verification-after-write-board.json"},
    {"gp": 286, "title": "Quarantine Object Manifest Ledger", "status": "ready", "route": "/vault/quarantine-object-manifest-ledger.json"},
    {"gp": 287, "title": "Write Failure and Rollback Preview", "status": "ready", "route": "/vault/write-failure-rollback-preview.json"},
    {"gp": 288, "title": "Owner Write Queue Resolution Lock", "status": "ready", "route": "/vault/owner-write-queue-resolution-lock.json"},
    {"gp": 289, "title": "Object Write Safety Blocker Board", "status": "ready", "route": "/vault/object-write-safety-blocker-board.json"},
    {"gp": 290, "title": "Owner File Object Write Quarantine Readiness Checkpoint", "status": "ready", "route": "/vault/owner-file-object-write-quarantine-readiness-checkpoint.json"},
]

SAMPLE_PAYLOADS_BY_FILENAME = {
    "Trust Document Final Signed.pdf": b"sample-trust-document-final-signed",
    "SimpleeOnTheGo Route Packet.csv": b"sample-simplee-on-the-go-route-packet",
}

BLOCKERS = [
    {
        "blocker_id": "no_raw_user_upload_endpoint",
        "label": "Raw user upload endpoint remains locked",
        "blocked_action": "raw_user_upload_endpoint",
        "allowed": False,
        "reason": "This layer only writes controlled quarantine objects from existing owner intake drafts.",
    },
    {
        "blocker_id": "no_public_upload",
        "label": "Public upload remains locked",
        "blocked_action": "public_upload",
        "allowed": False,
        "reason": "Owner-only quarantine write does not expose public intake.",
    },
    {
        "blocker_id": "no_beta_upload",
        "label": "Beta upload remains locked",
        "blocked_action": "beta_upload",
        "allowed": False,
        "reason": "Beta file actions require future Tower-controlled access.",
    },
    {
        "blocker_id": "no_provider_upload",
        "label": "Provider upload remains locked",
        "blocked_action": "provider_upload",
        "allowed": False,
        "reason": "Vault-owned storage remains provider-independent.",
    },
    {
        "blocker_id": "no_object_body_read",
        "label": "Object body read remains locked",
        "blocked_action": "object_body_read",
        "allowed": False,
        "reason": "Quarantine write proves storage and hash only; it does not expose content.",
    },
    {
        "blocker_id": "no_preview",
        "label": "Preview remains locked",
        "blocked_action": "file_preview",
        "allowed": False,
        "reason": "Preview belongs to a later safe preview layer.",
    },
    {
        "blocker_id": "no_download",
        "label": "Download remains locked",
        "blocked_action": "file_download",
        "allowed": False,
        "reason": "Download requires later Tower permissions and owner approval.",
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
        "reason": "Objects can be written into quarantine but cannot leave quarantine in this layer.",
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


def _ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)


def _stable_object_id(request_id: str, sha256_hash: str) -> str:
    return "qobj_" + calculate_sha256_bytes(f"{request_id}|{sha256_hash}".encode("utf-8"))[:24]


def _manifest_id(object_id: str) -> str:
    return "manifest_" + calculate_sha256_bytes(object_id.encode("utf-8"))[:24]


def _failure_id(request_id: str) -> str:
    return "rollback_preview_" + calculate_sha256_bytes(request_id.encode("utf-8"))[:24]


def _payload_for_request(request: Dict[str, Any]) -> bytes:
    original = request["original_filename"]
    if original in SAMPLE_PAYLOADS_BY_FILENAME:
        return SAMPLE_PAYLOADS_BY_FILENAME[original]

    # Fallback is deterministic but normally should not be used for seeded requests.
    return f"vault-quarantine-sample-payload::{request['request_id']}".encode("utf-8")


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def initialize_owner_file_object_write_quarantine_layer() -> Dict[str, Any]:
    previous_storage = validate_owner_owned_file_storage_foundation()
    previous_intake = validate_owner_upload_intake_lock_layer()
    _ensure_dirs()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quarantine_written_objects (
                object_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                safe_stored_name TEXT NOT NULL,
                mission_lane TEXT NOT NULL,
                folder_key TEXT NOT NULL,
                owner_lane TEXT NOT NULL,
                relative_quarantine_path TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                sha256_hash_expected TEXT NOT NULL,
                sha256_hash_actual TEXT NOT NULL,
                hash_verified INTEGER NOT NULL,
                quarantine_state TEXT NOT NULL,
                preview_locked INTEGER NOT NULL,
                download_locked INTEGER NOT NULL,
                share_locked INTEGER NOT NULL,
                delete_locked INTEGER NOT NULL,
                restore_locked INTEGER NOT NULL,
                registry_promotion_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS hash_verification_after_write (
                verification_id TEXT PRIMARY KEY,
                object_id TEXT NOT NULL,
                request_id TEXT NOT NULL,
                expected_hash TEXT NOT NULL,
                actual_hash TEXT NOT NULL,
                verified INTEGER NOT NULL,
                verified_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quarantine_object_manifest_ledger (
                manifest_id TEXT PRIMARY KEY,
                object_id TEXT NOT NULL,
                request_id TEXT NOT NULL,
                manifest_relative_path TEXT NOT NULL,
                manifest_hash TEXT NOT NULL,
                finalized INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS write_failure_rollback_previews (
                rollback_preview_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                failure_type TEXT NOT NULL,
                rollback_available INTEGER NOT NULL,
                rollback_executed INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS owner_write_queue_resolution_locks (
                resolution_lock_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                resolution_allowed INTEGER NOT NULL,
                quarantine_release_allowed INTEGER NOT NULL,
                registry_promotion_allowed INTEGER NOT NULL,
                owner_approval_required INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS object_write_safety_blockers (
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
            INSERT OR REPLACE INTO owner_write_queue_resolution_locks (
                resolution_lock_id, label, resolution_allowed, quarantine_release_allowed,
                registry_promotion_allowed, owner_approval_required, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "owner_write_queue_resolution_lock",
                "Owner write queue resolution lock",
                0,
                0,
                0,
                1,
                now,
                now,
            ),
        )

        for blocker in BLOCKERS:
            conn.execute(
                """
                INSERT OR REPLACE INTO object_write_safety_blockers (
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

    write_seeded_quarantine_objects()

    return {
        "initialized": True,
        "previous_storage_foundation_ready": bool(previous_storage.get("ready", False)),
        "previous_upload_intake_ready": bool(previous_intake.get("ready", False)),
        "db_path": _relative(DB_PATH),
        "quarantine_dir": _relative(QUARANTINE_DIR),
        "manifests_dir": _relative(MANIFESTS_DIR),
    }


def write_quarantine_object_from_request(request: Dict[str, Any]) -> Dict[str, Any]:
    _ensure_dirs()

    request_id = request["request_id"]
    expected_hash = request["sha256_hash"]
    safe_name = request["pending_safe_stored_name"]
    object_id = _stable_object_id(request_id, expected_hash)

    payload = _payload_for_request(request)
    actual_hash = calculate_sha256_bytes(payload)
    hash_verified = actual_hash == expected_hash

    object_path = QUARANTINE_DIR / safe_name
    object_path.write_bytes(payload)

    size_bytes = object_path.stat().st_size

    manifest = {
        "object_id": object_id,
        "request_id": request_id,
        "original_filename": request["original_filename"],
        "safe_stored_name": safe_name,
        "mission_lane": request["mission_lane"],
        "folder_key": request["folder_key"],
        "owner_lane": request["owner_lane"],
        "relative_quarantine_path": _relative(object_path),
        "size_bytes": size_bytes,
        "mime_type": request["mime_type"],
        "sha256_hash_expected": expected_hash,
        "sha256_hash_actual": actual_hash,
        "hash_verified": hash_verified,
        "quarantine_state": "written_quarantine_locked",
        "preview_locked": True,
        "download_locked": True,
        "share_locked": True,
        "delete_locked": True,
        "restore_locked": True,
        "registry_promotion_allowed": False,
    }

    manifest_payload = json.dumps(manifest, sort_keys=True, indent=2).encode("utf-8")
    manifest_hash = calculate_sha256_bytes(manifest_payload)
    manifest_path = MANIFESTS_DIR / f"{object_id}.manifest.json"
    manifest_path.write_bytes(manifest_payload)

    now = _now()

    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO quarantine_written_objects (
                object_id, request_id, original_filename, safe_stored_name,
                mission_lane, folder_key, owner_lane, relative_quarantine_path,
                size_bytes, mime_type, sha256_hash_expected, sha256_hash_actual,
                hash_verified, quarantine_state, preview_locked, download_locked,
                share_locked, delete_locked, restore_locked, registry_promotion_allowed,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                object_id,
                request_id,
                request["original_filename"],
                safe_name,
                request["mission_lane"],
                request["folder_key"],
                request["owner_lane"],
                _relative(object_path),
                size_bytes,
                request["mime_type"],
                expected_hash,
                actual_hash,
                1 if hash_verified else 0,
                "written_quarantine_locked",
                1,
                1,
                1,
                1,
                1,
                0,
                now,
                now,
            ),
        )

        conn.execute(
            """
            INSERT OR REPLACE INTO hash_verification_after_write (
                verification_id, object_id, request_id, expected_hash,
                actual_hash, verified, verified_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "verify_" + object_id,
                object_id,
                request_id,
                expected_hash,
                actual_hash,
                1 if hash_verified else 0,
                now,
            ),
        )

        conn.execute(
            """
            INSERT OR REPLACE INTO quarantine_object_manifest_ledger (
                manifest_id, object_id, request_id, manifest_relative_path,
                manifest_hash, finalized, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                _manifest_id(object_id),
                object_id,
                request_id,
                _relative(manifest_path),
                manifest_hash,
                0,
                now,
            ),
        )

        if not hash_verified:
            conn.execute(
                """
                INSERT OR REPLACE INTO write_failure_rollback_previews (
                    rollback_preview_id, request_id, failure_type, rollback_available,
                    rollback_executed, reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _failure_id(request_id),
                    request_id,
                    "hash_mismatch",
                    1,
                    0,
                    "Hash mismatch blocks quarantine promotion and requires owner review.",
                    now,
                ),
            )

        conn.commit()

    return {
        "object_id": object_id,
        "request_id": request_id,
        "relative_quarantine_path": _relative(object_path),
        "manifest_relative_path": _relative(manifest_path),
        "hash_verified": hash_verified,
        "preview_locked": True,
        "download_locked": True,
        "registry_promotion_allowed": False,
    }


def get_quarantine_candidate_upload_drafts() -> List[Dict[str, Any]]:
    """
    GP281-GP290 needs full upload request draft records because quarantine
    writing must verify sha256_hash. GP271's owner queue preview is intentionally
    metadata-limited and should not be used as the write source.
    """
    registry = get_upload_request_draft_registry()
    drafts = registry.get("drafts", [])

    candidates: List[Dict[str, Any]] = []
    required_keys = {
        "request_id",
        "original_filename",
        "pending_safe_stored_name",
        "mission_lane",
        "folder_key",
        "owner_lane",
        "size_bytes",
        "mime_type",
        "sha256_hash",
    }

    for request in drafts:
        missing = sorted(key for key in required_keys if key not in request)
        if missing:
            continue
        if request["original_filename"] in SAMPLE_PAYLOADS_BY_FILENAME:
            candidates.append(request)

    return candidates


def write_seeded_quarantine_objects() -> List[Dict[str, Any]]:
    candidates = get_quarantine_candidate_upload_drafts()
    written = []

    for request in candidates:
        written.append(write_quarantine_object_from_request(request))

    return written


def get_owner_file_object_write_quarantine_shell() -> Dict[str, Any]:
    init = initialize_owner_file_object_write_quarantine_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 281,
        "title": "Owner File Object Write Quarantine Shell",
        "ready": True,
        "initialized": init,
        "owner_owned_storage": True,
        "controlled_quarantine_write_allowed": True,
        "raw_user_upload_endpoint_allowed": False,
        "locks": LOCKS,
    }


def get_controlled_owner_object_write_contract() -> Dict[str, Any]:
    initialize_owner_file_object_write_quarantine_layer()
    return {
        "section": SECTION,
        "gp": 282,
        "title": "Controlled Owner Object Write Contract",
        "ready": True,
        "contract": {
            "source_must_be_owner_upload_intake_draft": True,
            "write_target_must_be_quarantine": True,
            "sha256_hash_must_match": True,
            "manifest_required": True,
            "registry_handoff_preview_only": True,
            "quarantine_release_allowed": False,
            "raw_user_upload_endpoint_allowed": False,
            "provider_storage_required": False,
            "object_body_read_allowed": False,
        },
    }


def get_quarantine_object_body_writer() -> Dict[str, Any]:
    init = initialize_owner_file_object_write_quarantine_layer()
    with _connect() as conn:
        objects = _rows(conn, "SELECT * FROM quarantine_written_objects ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 283,
        "title": "Quarantine Object Body Writer",
        "ready": True,
        "initialized": init,
        "written_object_count": len(objects),
        "objects": objects,
        "write_scope": "controlled_seeded_owner_intake_to_quarantine_only",
        "raw_user_upload_endpoint_allowed": False,
        "object_body_read_allowed": False,
    }


def get_file_object_registry_insert_handoff() -> Dict[str, Any]:
    initialize_owner_file_object_write_quarantine_layer()
    with _connect() as conn:
        candidates = _rows(
            conn,
            """
            SELECT object_id, request_id, original_filename, safe_stored_name,
                   mission_lane, folder_key, owner_lane, relative_quarantine_path,
                   size_bytes, mime_type, sha256_hash_actual, hash_verified,
                   quarantine_state, registry_promotion_allowed
            FROM quarantine_written_objects
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 284,
        "title": "File Object Registry Insert Handoff",
        "ready": True,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "registry_promotion_allowed": False,
        "handoff_mode": "preview_only_locked",
        "note": "Objects are physically written to quarantine, but not promoted into active file registry in this layer.",
    }


def get_hash_verification_after_write_board() -> Dict[str, Any]:
    initialize_owner_file_object_write_quarantine_layer()
    with _connect() as conn:
        verifications = _rows(conn, "SELECT * FROM hash_verification_after_write ORDER BY verified_at DESC")

    return {
        "section": SECTION,
        "gp": 285,
        "title": "Hash Verification After Write Board",
        "ready": True,
        "verification_count": len(verifications),
        "verifications": verifications,
        "all_hashes_verified": all(bool(item["verified"]) for item in verifications),
    }


def get_quarantine_object_manifest_ledger() -> Dict[str, Any]:
    initialize_owner_file_object_write_quarantine_layer()
    with _connect() as conn:
        manifests = _rows(conn, "SELECT * FROM quarantine_object_manifest_ledger ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 286,
        "title": "Quarantine Object Manifest Ledger",
        "ready": True,
        "manifest_count": len(manifests),
        "manifests": manifests,
        "finalized": False,
        "manifest_finalization_allowed": False,
    }


def get_write_failure_rollback_preview() -> Dict[str, Any]:
    initialize_owner_file_object_write_quarantine_layer()
    with _connect() as conn:
        failures = _rows(conn, "SELECT * FROM write_failure_rollback_previews ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 287,
        "title": "Write Failure and Rollback Preview",
        "ready": True,
        "failure_count": len(failures),
        "failures": failures,
        "rollback_preview_available": True,
        "rollback_execution_allowed": False,
        "note": "Rollback is preview-only unless a future owner-approved cleanup layer unlocks it.",
    }


def get_owner_write_queue_resolution_lock() -> Dict[str, Any]:
    initialize_owner_file_object_write_quarantine_layer()
    with _connect() as conn:
        locks = _rows(conn, "SELECT * FROM owner_write_queue_resolution_locks ORDER BY resolution_lock_id")
        objects = _rows(
            conn,
            """
            SELECT object_id, request_id, original_filename, hash_verified,
                   quarantine_state, registry_promotion_allowed
            FROM quarantine_written_objects
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 288,
        "title": "Owner Write Queue Resolution Lock",
        "ready": True,
        "locks": locks,
        "queued_written_objects": objects,
        "resolution_allowed": False,
        "quarantine_release_allowed": False,
        "registry_promotion_allowed": False,
    }


def get_object_write_safety_blocker_board() -> Dict[str, Any]:
    initialize_owner_file_object_write_quarantine_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM object_write_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 289,
        "title": "Object Write Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_owner_file_object_write_quarantine_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_owner_file_object_write_quarantine_layer()

    shell = get_owner_file_object_write_quarantine_shell()
    contract = get_controlled_owner_object_write_contract()
    writer = get_quarantine_object_body_writer()
    handoff = get_file_object_registry_insert_handoff()
    hash_board = get_hash_verification_after_write_board()
    manifests = get_quarantine_object_manifest_ledger()
    rollback = get_write_failure_rollback_preview()
    resolution = get_owner_write_queue_resolution_lock()
    blockers = get_object_write_safety_blocker_board()

    checks = {
        "previous_storage_foundation_ready": init["previous_storage_foundation_ready"] is True,
        "previous_upload_intake_ready": init["previous_upload_intake_ready"] is True,
        "quarantine_shell_ready": shell["ready"] is True,
        "controlled_write_contract_ready": contract["ready"] is True,
        "quarantine_writer_ready": writer["ready"] is True and writer["written_object_count"] >= 2,
        "registry_insert_handoff_locked": handoff["ready"] is True and handoff["registry_promotion_allowed"] is False,
        "hash_verification_ready": hash_board["ready"] is True and hash_board["all_hashes_verified"] is True,
        "manifest_ledger_ready": manifests["ready"] is True and manifests["manifest_count"] >= 2,
        "rollback_preview_ready": rollback["ready"] is True and rollback["rollback_execution_allowed"] is False,
        "resolution_lock_ready": resolution["ready"] is True and resolution["resolution_allowed"] is False,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "raw_user_upload_still_locked": LOCKS["raw_user_upload_endpoint_allowed"] is False,
        "object_body_read_still_locked": LOCKS["object_body_read_allowed"] is False,
        "download_still_locked": LOCKS["file_download_unlocked"] is False,
        "provider_not_required": LOCKS["provider_storage_required"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 290,
        "title": "Owner File Object Write Quarantine Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Owner file object write quarantine layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — OWNER FILE REGISTRY PROMOTION LOCK LAYER / GP291-GP300",
        "still_locked": [
            "no raw user upload endpoint",
            "no public upload",
            "no beta upload",
            "no provider upload",
            "no object body read",
            "no preview",
            "no download",
            "no sharing",
            "no delete",
            "no restore",
            "no external sync",
            "no quarantine release",
            "no active registry promotion",
        ],
    }


def get_owner_file_object_write_quarantine_home() -> Dict[str, Any]:
    checkpoint = get_owner_file_object_write_quarantine_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_owner_file_object_write_quarantine_layer() -> Dict[str, Any]:
    checkpoint = get_owner_file_object_write_quarantine_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_storage_foundation_ready"] is True
    assert checkpoint["checks"]["previous_upload_intake_ready"] is True
    assert checkpoint["checks"]["quarantine_writer_ready"] is True
    assert checkpoint["checks"]["hash_verification_ready"] is True
    assert checkpoint["checks"]["manifest_ledger_ready"] is True
    assert checkpoint["checks"]["registry_insert_handoff_locked"] is True
    assert checkpoint["checks"]["resolution_lock_ready"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["controlled_quarantine_write_allowed"] is True
    assert LOCKS["raw_user_upload_endpoint_allowed"] is False
    assert LOCKS["public_upload_unlocked"] is False
    assert LOCKS["beta_upload_unlocked"] is False
    assert LOCKS["provider_upload_unlocked"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["object_body_read_allowed"] is False
    assert LOCKS["object_body_preview_allowed"] is False
    assert LOCKS["file_download_unlocked"] is False
    assert LOCKS["file_share_unlocked"] is False
    assert LOCKS["file_delete_unlocked"] is False
    assert LOCKS["file_restore_unlocked"] is False
    assert LOCKS["external_sync_unlocked"] is False
    assert LOCKS["quarantine_release_allowed"] is False
    assert LOCKS["registry_promotion_allowed"] is False

    return {
        "ok": True,
        "section": SECTION,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(item for item in PACKS if item["gp"] == gp)
    checkpoint = get_owner_file_object_write_quarantine_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "locks_preserved": True,
        "controlled_quarantine_write_allowed": True,
        "raw_user_upload_endpoint_allowed": False,
        "download_allowed": False,
    }


def get_gp281_status() -> Dict[str, Any]:
    return _gp_status(281)


def get_gp282_status() -> Dict[str, Any]:
    return _gp_status(282)


def get_gp283_status() -> Dict[str, Any]:
    return _gp_status(283)


def get_gp284_status() -> Dict[str, Any]:
    return _gp_status(284)


def get_gp285_status() -> Dict[str, Any]:
    return _gp_status(285)


def get_gp286_status() -> Dict[str, Any]:
    return _gp_status(286)


def get_gp287_status() -> Dict[str, Any]:
    return _gp_status(287)


def get_gp288_status() -> Dict[str, Any]:
    return _gp_status(288)


def get_gp289_status() -> Dict[str, Any]:
    return _gp_status(289)


def get_gp290_status() -> Dict[str, Any]:
    return _gp_status(290)
