
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — OWNER FILE DETAIL METADATA VIEW LAYER / GP311-GP320"
LAYER_ID = "vault_gp311_320_owner_file_detail_metadata_view_layer"
READINESS_LABEL = "Owner file detail metadata view layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_owner_file_detail_metadata_view_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.owner_file_registry_promotion_execution_layer_service import (
        get_active_file_registry_writer,
        get_registry_promotion_execution_ledger,
        get_promotion_receipt_finalization_board,
        get_active_registry_hash_continuity_board,
        get_quarantine_hold_after_promotion_contract,
        validate_owner_file_registry_promotion_execution_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP311-GP320 requires GP301-GP310 owner file registry promotion execution layer first."
    ) from exc


LOCKS = {
    "owner_file_detail_metadata_view_layer": True,
    "metadata_detail_view_allowed": True,
    "identity_summary_allowed": True,
    "provenance_reference_allowed": True,
    "receipt_reference_allowed": True,
    "lock_status_display_allowed": True,
    "metadata_redaction_policy_allowed": True,
    "file_detail_payload_allowed": True,
    "audit_snapshot_allowed": True,
    "object_body_read_allowed": False,
    "plaintext_content_allowed": False,
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
}

PACKS = [
    {"gp": 311, "title": "Owner File Detail Metadata View Shell", "status": "ready", "route": "/vault/owner-file-detail-metadata-view-shell.json"},
    {"gp": 312, "title": "Active File Metadata Detail Contract", "status": "ready", "route": "/vault/active-file-metadata-detail-contract.json"},
    {"gp": 313, "title": "File Identity Summary Board", "status": "ready", "route": "/vault/file-identity-summary-board.json"},
    {"gp": 314, "title": "File Provenance and Receipt Reference Board", "status": "ready", "route": "/vault/file-provenance-receipt-reference-board.json"},
    {"gp": 315, "title": "File Lock Status Board", "status": "ready", "route": "/vault/file-lock-status-board.json"},
    {"gp": 316, "title": "Metadata Redaction Display Policy Board", "status": "ready", "route": "/vault/metadata-redaction-display-policy-board.json"},
    {"gp": 317, "title": "File Detail Route Payload Builder", "status": "ready", "route": "/vault/file-detail-route-payload-builder.json"},
    {"gp": 318, "title": "File Detail Audit Snapshot Ledger", "status": "ready", "route": "/vault/file-detail-audit-snapshot-ledger.json"},
    {"gp": 319, "title": "File Detail Safety Blocker Board", "status": "ready", "route": "/vault/file-detail-safety-blocker-board.json"},
    {"gp": 320, "title": "Owner File Detail Metadata View Readiness Checkpoint", "status": "ready", "route": "/vault/owner-file-detail-metadata-view-readiness-checkpoint.json"},
]

DISPLAY_POLICIES = [
    {
        "policy_id": "show_original_filename",
        "label": "Show original filename",
        "field_name": "original_filename",
        "display_state": "visible",
        "redacted": False,
    },
    {
        "policy_id": "show_safe_stored_name",
        "label": "Show safe stored name",
        "field_name": "safe_stored_name",
        "display_state": "visible",
        "redacted": False,
    },
    {
        "policy_id": "show_hash",
        "label": "Show SHA256 hash",
        "field_name": "sha256_hash",
        "display_state": "visible",
        "redacted": False,
    },
    {
        "policy_id": "show_lanes",
        "label": "Show mission/folder/owner lanes",
        "field_name": "lanes",
        "display_state": "visible",
        "redacted": False,
    },
    {
        "policy_id": "hide_quarantine_path",
        "label": "Hide physical quarantine path from owner detail view",
        "field_name": "relative_quarantine_path",
        "display_state": "hidden",
        "redacted": True,
    },
    {
        "policy_id": "hide_object_body",
        "label": "Never display object body",
        "field_name": "object_body",
        "display_state": "blocked",
        "redacted": True,
    },
    {
        "policy_id": "hide_plaintext_content",
        "label": "Never display plaintext content",
        "field_name": "plaintext_content",
        "display_state": "blocked",
        "redacted": True,
    },
]

BLOCKERS = [
    {
        "blocker_id": "no_object_body_read",
        "label": "Object body read remains locked",
        "blocked_action": "object_body_read",
        "allowed": False,
        "reason": "File detail view is metadata-only.",
    },
    {
        "blocker_id": "no_plaintext_content",
        "label": "Plaintext content remains locked",
        "blocked_action": "plaintext_content",
        "allowed": False,
        "reason": "No file text/body extraction exists in this layer.",
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
        "reason": "Download requires later Tower permission and owner approval rules.",
    },
    {
        "blocker_id": "no_share",
        "label": "Sharing remains locked",
        "blocked_action": "file_share",
        "allowed": False,
        "reason": "Sharing belongs to a later access/share lock layer.",
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
        "reason": "Metadata view does not release or move physical objects.",
    },
    {
        "blocker_id": "no_public_upload",
        "label": "Public upload remains locked",
        "blocked_action": "public_upload",
        "allowed": False,
        "reason": "Metadata view does not expose public upload.",
    },
    {
        "blocker_id": "no_beta_upload",
        "label": "Beta upload remains locked",
        "blocked_action": "beta_upload",
        "allowed": False,
        "reason": "Metadata view does not expose beta upload.",
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
        "reason": "File metadata detail does not sync externally.",
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


def _detail_snapshot_id(active_file_id: str) -> str:
    return "file_detail_snapshot_" + calculate_sha256_bytes(("detail|" + active_file_id).encode("utf-8"))[:24]


def _audit_snapshot_id(active_file_id: str) -> str:
    return "file_detail_audit_" + calculate_sha256_bytes(("audit|" + active_file_id).encode("utf-8"))[:24]


def _display_hash(payload: Dict[str, Any]) -> str:
    return calculate_sha256_bytes(repr(sorted(payload.items())).encode("utf-8"))


def initialize_owner_file_detail_metadata_view_layer() -> Dict[str, Any]:
    previous = validate_owner_file_registry_promotion_execution_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_detail_metadata_snapshots (
                detail_snapshot_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
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
                detail_payload_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata_display_policies (
                policy_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                field_name TEXT NOT NULL,
                display_state TEXT NOT NULL,
                redacted INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_detail_audit_snapshot_ledger (
                audit_snapshot_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                detail_snapshot_id TEXT NOT NULL,
                audit_state TEXT NOT NULL,
                object_body_read_executed INTEGER NOT NULL,
                preview_executed INTEGER NOT NULL,
                download_executed INTEGER NOT NULL,
                detail_payload_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_detail_safety_blockers (
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

        for policy in DISPLAY_POLICIES:
            conn.execute(
                """
                INSERT OR REPLACE INTO metadata_display_policies (
                    policy_id, label, field_name, display_state, redacted, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    policy["policy_id"],
                    policy["label"],
                    policy["field_name"],
                    policy["display_state"],
                    1 if policy["redacted"] else 0,
                    now,
                    now,
                ),
            )

        for blocker in BLOCKERS:
            conn.execute(
                """
                INSERT OR REPLACE INTO file_detail_safety_blockers (
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

        active_files = get_active_file_registry_writer().get("active_files", [])

        for item in active_files:
            active_file_id = item["active_file_id"]
            detail_snapshot_id = _detail_snapshot_id(active_file_id)

            detail_material = {
                "active_file_id": active_file_id,
                "source_object_id": item["source_object_id"],
                "original_filename": item["original_filename"],
                "safe_stored_name": item["safe_stored_name"],
                "mission_lane": item["mission_lane"],
                "folder_key": item["folder_key"],
                "owner_lane": item["owner_lane"],
                "size_bytes": item["size_bytes"],
                "mime_type": item["mime_type"],
                "sha256_hash": item["sha256_hash"],
                "registry_state": item["registry_state"],
                "metadata_only": True,
                "quarantine_held": bool(item["quarantine_held"]),
                "object_body_read_locked": True,
                "preview_locked": True,
                "download_locked": True,
            }
            detail_payload_hash = _display_hash(detail_material)

            conn.execute(
                """
                INSERT OR REPLACE INTO file_detail_metadata_snapshots (
                    detail_snapshot_id, active_file_id, source_object_id,
                    original_filename, safe_stored_name, mission_lane, folder_key,
                    owner_lane, size_bytes, mime_type, sha256_hash, registry_state,
                    metadata_only, quarantine_held, object_body_read_locked,
                    preview_locked, download_locked, share_locked, delete_locked,
                    restore_locked, detail_payload_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    detail_snapshot_id,
                    active_file_id,
                    item["source_object_id"],
                    item["original_filename"],
                    item["safe_stored_name"],
                    item["mission_lane"],
                    item["folder_key"],
                    item["owner_lane"],
                    item["size_bytes"],
                    item["mime_type"],
                    item["sha256_hash"],
                    item["registry_state"],
                    1,
                    1 if item["quarantine_held"] else 0,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    detail_payload_hash,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO file_detail_audit_snapshot_ledger (
                    audit_snapshot_id, active_file_id, detail_snapshot_id,
                    audit_state, object_body_read_executed, preview_executed,
                    download_executed, detail_payload_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _audit_snapshot_id(active_file_id),
                    active_file_id,
                    detail_snapshot_id,
                    "metadata_detail_snapshot_recorded",
                    0,
                    0,
                    0,
                    detail_payload_hash,
                    now,
                ),
            )

        conn.commit()

    return {
        "initialized": True,
        "previous_registry_promotion_execution_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
    }


def get_owner_file_detail_metadata_view_shell() -> Dict[str, Any]:
    init = initialize_owner_file_detail_metadata_view_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 311,
        "title": "Owner File Detail Metadata View Shell",
        "ready": True,
        "initialized": init,
        "metadata_detail_view_allowed": True,
        "object_body_read_allowed": False,
        "file_preview_unlocked": False,
        "file_download_unlocked": False,
        "locks": LOCKS,
    }


def get_active_file_metadata_detail_contract() -> Dict[str, Any]:
    initialize_owner_file_detail_metadata_view_layer()
    return {
        "section": SECTION,
        "gp": 312,
        "title": "Active File Metadata Detail Contract",
        "ready": True,
        "contract": {
            "metadata_only": True,
            "allowed_fields": [
                "active_file_id",
                "original_filename",
                "safe_stored_name",
                "mission_lane",
                "folder_key",
                "owner_lane",
                "size_bytes",
                "mime_type",
                "sha256_hash",
                "registry_state",
                "lock_status",
                "receipt_reference",
                "provenance_reference",
            ],
            "blocked_fields": [
                "object_body",
                "plaintext_content",
                "preview_content",
                "download_url",
                "external_share_url",
                "physical_quarantine_path",
            ],
            "object_body_read_allowed": False,
            "preview_allowed": False,
            "download_allowed": False,
        },
    }


def get_file_identity_summary_board() -> Dict[str, Any]:
    initialize_owner_file_detail_metadata_view_layer()
    with _connect() as conn:
        rows = _rows(
            conn,
            """
            SELECT active_file_id, original_filename, safe_stored_name,
                   mission_lane, folder_key, owner_lane, size_bytes,
                   mime_type, sha256_hash, registry_state
            FROM file_detail_metadata_snapshots
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 313,
        "title": "File Identity Summary Board",
        "ready": True,
        "file_count": len(rows),
        "files": rows,
        "metadata_only": True,
    }


def get_file_provenance_receipt_reference_board() -> Dict[str, Any]:
    initialize_owner_file_detail_metadata_view_layer()

    execution_ledger = get_registry_promotion_execution_ledger()
    receipts = get_promotion_receipt_finalization_board()
    continuity = get_active_registry_hash_continuity_board()
    quarantine_hold = get_quarantine_hold_after_promotion_contract()

    with _connect() as conn:
        snapshots = _rows(
            conn,
            """
            SELECT active_file_id, source_object_id, detail_snapshot_id,
                   detail_payload_hash, created_at
            FROM file_detail_metadata_snapshots
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 314,
        "title": "File Provenance and Receipt Reference Board",
        "ready": True,
        "snapshot_count": len(snapshots),
        "snapshots": snapshots,
        "execution_reference_count": execution_ledger["execution_count"],
        "receipt_reference_count": receipts["final_receipt_count"],
        "hash_continuity_reference_count": continuity["continuity_count"],
        "quarantine_hold_reference_count": quarantine_hold["hold_count"],
        "provenance_ready": (
            execution_ledger["execution_count"] >= 2
            and receipts["final_receipt_count"] >= 2
            and continuity["continuity_count"] >= 2
            and quarantine_hold["hold_count"] >= 2
        ),
    }


def get_file_lock_status_board() -> Dict[str, Any]:
    initialize_owner_file_detail_metadata_view_layer()
    with _connect() as conn:
        rows = _rows(
            conn,
            """
            SELECT active_file_id, original_filename, object_body_read_locked,
                   preview_locked, download_locked, share_locked, delete_locked,
                   restore_locked, quarantine_held
            FROM file_detail_metadata_snapshots
            ORDER BY created_at DESC
            """,
        )

    return {
        "section": SECTION,
        "gp": 315,
        "title": "File Lock Status Board",
        "ready": True,
        "file_count": len(rows),
        "lock_rows": rows,
        "all_object_body_reads_locked": all(bool(item["object_body_read_locked"]) for item in rows),
        "all_previews_locked": all(bool(item["preview_locked"]) for item in rows),
        "all_downloads_locked": all(bool(item["download_locked"]) for item in rows),
        "all_shares_locked": all(bool(item["share_locked"]) for item in rows),
        "all_deletes_locked": all(bool(item["delete_locked"]) for item in rows),
        "all_restores_locked": all(bool(item["restore_locked"]) for item in rows),
    }


def get_metadata_redaction_display_policy_board() -> Dict[str, Any]:
    initialize_owner_file_detail_metadata_view_layer()
    with _connect() as conn:
        policies = _rows(conn, "SELECT * FROM metadata_display_policies ORDER BY policy_id")

    return {
        "section": SECTION,
        "gp": 316,
        "title": "Metadata Redaction Display Policy Board",
        "ready": True,
        "policy_count": len(policies),
        "policies": policies,
        "object_body_blocked": any(item["field_name"] == "object_body" and bool(item["redacted"]) for item in policies),
        "plaintext_content_blocked": any(item["field_name"] == "plaintext_content" and bool(item["redacted"]) for item in policies),
        "physical_path_hidden": any(item["field_name"] == "relative_quarantine_path" and bool(item["redacted"]) for item in policies),
    }


def get_file_detail_route_payload_builder() -> Dict[str, Any]:
    initialize_owner_file_detail_metadata_view_layer()
    with _connect() as conn:
        snapshots = _rows(conn, "SELECT * FROM file_detail_metadata_snapshots ORDER BY created_at DESC")

    payloads = []
    for item in snapshots:
        payloads.append(
            {
                "active_file_id": item["active_file_id"],
                "detail_snapshot_id": item["detail_snapshot_id"],
                "identity": {
                    "original_filename": item["original_filename"],
                    "safe_stored_name": item["safe_stored_name"],
                    "mission_lane": item["mission_lane"],
                    "folder_key": item["folder_key"],
                    "owner_lane": item["owner_lane"],
                    "size_bytes": item["size_bytes"],
                    "mime_type": item["mime_type"],
                    "sha256_hash": item["sha256_hash"],
                    "registry_state": item["registry_state"],
                },
                "locks": {
                    "object_body_read_locked": bool(item["object_body_read_locked"]),
                    "preview_locked": bool(item["preview_locked"]),
                    "download_locked": bool(item["download_locked"]),
                    "share_locked": bool(item["share_locked"]),
                    "delete_locked": bool(item["delete_locked"]),
                    "restore_locked": bool(item["restore_locked"]),
                    "quarantine_held": bool(item["quarantine_held"]),
                },
                "display": {
                    "metadata_only": True,
                    "object_body": "LOCKED",
                    "plaintext_content": "LOCKED",
                    "preview": "LOCKED",
                    "download": "LOCKED",
                },
                "detail_payload_hash": item["detail_payload_hash"],
            }
        )

    return {
        "section": SECTION,
        "gp": 317,
        "title": "File Detail Route Payload Builder",
        "ready": True,
        "payload_count": len(payloads),
        "payloads": payloads,
        "metadata_only": True,
        "object_body_included": False,
        "download_url_included": False,
    }


def get_file_detail_audit_snapshot_ledger() -> Dict[str, Any]:
    initialize_owner_file_detail_metadata_view_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM file_detail_audit_snapshot_ledger ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 318,
        "title": "File Detail Audit Snapshot Ledger",
        "ready": True,
        "audit_snapshot_count": len(rows),
        "audit_snapshots": rows,
        "no_object_body_reads_executed": all(not bool(item["object_body_read_executed"]) for item in rows),
        "no_previews_executed": all(not bool(item["preview_executed"]) for item in rows),
        "no_downloads_executed": all(not bool(item["download_executed"]) for item in rows),
    }


def get_file_detail_safety_blocker_board() -> Dict[str, Any]:
    initialize_owner_file_detail_metadata_view_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM file_detail_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 319,
        "title": "File Detail Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_owner_file_detail_metadata_view_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_owner_file_detail_metadata_view_layer()

    shell = get_owner_file_detail_metadata_view_shell()
    contract = get_active_file_metadata_detail_contract()
    identity = get_file_identity_summary_board()
    provenance = get_file_provenance_receipt_reference_board()
    locks = get_file_lock_status_board()
    policies = get_metadata_redaction_display_policy_board()
    payloads = get_file_detail_route_payload_builder()
    audits = get_file_detail_audit_snapshot_ledger()
    blockers = get_file_detail_safety_blocker_board()

    checks = {
        "previous_registry_promotion_execution_ready": init["previous_registry_promotion_execution_ready"] is True,
        "detail_shell_ready": shell["ready"] is True,
        "metadata_detail_contract_ready": contract["ready"] is True and contract["contract"]["metadata_only"] is True,
        "identity_summary_ready": identity["ready"] is True and identity["file_count"] >= 2,
        "provenance_reference_ready": provenance["ready"] is True and provenance["provenance_ready"] is True,
        "lock_status_ready": locks["ready"] is True and locks["all_downloads_locked"] is True and locks["all_previews_locked"] is True,
        "metadata_redaction_policy_ready": policies["ready"] is True and policies["object_body_blocked"] is True,
        "file_detail_payload_ready": payloads["ready"] is True and payloads["payload_count"] >= 2 and payloads["object_body_included"] is False,
        "audit_snapshot_ready": audits["ready"] is True and audits["no_object_body_reads_executed"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "object_body_read_still_locked": LOCKS["object_body_read_allowed"] is False,
        "preview_still_locked": LOCKS["file_preview_unlocked"] is False,
        "download_still_locked": LOCKS["file_download_unlocked"] is False,
        "quarantine_release_still_locked": LOCKS["quarantine_release_allowed"] is False,
        "provider_not_required": LOCKS["provider_storage_required"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 320,
        "title": "Owner File Detail Metadata View Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Owner file detail metadata view layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — OWNER FOLDER BROWSE METADATA LAYER / GP321-GP330",
        "still_locked": [
            "no object body read",
            "no plaintext content",
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


def get_owner_file_detail_metadata_view_home() -> Dict[str, Any]:
    checkpoint = get_owner_file_detail_metadata_view_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_owner_file_detail_metadata_view_layer() -> Dict[str, Any]:
    checkpoint = get_owner_file_detail_metadata_view_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_registry_promotion_execution_ready"] is True
    assert checkpoint["checks"]["metadata_detail_contract_ready"] is True
    assert checkpoint["checks"]["identity_summary_ready"] is True
    assert checkpoint["checks"]["provenance_reference_ready"] is True
    assert checkpoint["checks"]["lock_status_ready"] is True
    assert checkpoint["checks"]["metadata_redaction_policy_ready"] is True
    assert checkpoint["checks"]["file_detail_payload_ready"] is True
    assert checkpoint["checks"]["audit_snapshot_ready"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["metadata_detail_view_allowed"] is True
    assert LOCKS["identity_summary_allowed"] is True
    assert LOCKS["provenance_reference_allowed"] is True
    assert LOCKS["receipt_reference_allowed"] is True
    assert LOCKS["lock_status_display_allowed"] is True
    assert LOCKS["metadata_redaction_policy_allowed"] is True
    assert LOCKS["file_detail_payload_allowed"] is True
    assert LOCKS["audit_snapshot_allowed"] is True

    assert LOCKS["object_body_read_allowed"] is False
    assert LOCKS["plaintext_content_allowed"] is False
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

    return {
        "ok": True,
        "section": SECTION,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(item for item in PACKS if item["gp"] == gp)
    checkpoint = get_owner_file_detail_metadata_view_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "locks_preserved": True,
        "metadata_detail_view_allowed": True,
        "object_body_read_allowed": False,
        "preview_allowed": False,
        "download_allowed": False,
    }


def get_gp311_status() -> Dict[str, Any]:
    return _gp_status(311)


def get_gp312_status() -> Dict[str, Any]:
    return _gp_status(312)


def get_gp313_status() -> Dict[str, Any]:
    return _gp_status(313)


def get_gp314_status() -> Dict[str, Any]:
    return _gp_status(314)


def get_gp315_status() -> Dict[str, Any]:
    return _gp_status(315)


def get_gp316_status() -> Dict[str, Any]:
    return _gp_status(316)


def get_gp317_status() -> Dict[str, Any]:
    return _gp_status(317)


def get_gp318_status() -> Dict[str, Any]:
    return _gp_status(318)


def get_gp319_status() -> Dict[str, Any]:
    return _gp_status(319)


def get_gp320_status() -> Dict[str, Any]:
    return _gp_status(320)
