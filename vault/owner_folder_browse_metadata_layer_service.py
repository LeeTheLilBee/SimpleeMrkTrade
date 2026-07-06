
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — OWNER FOLDER BROWSE METADATA LAYER / GP321-GP330"
LAYER_ID = "vault_gp321_330_owner_folder_browse_metadata_layer"
READINESS_LABEL = "Owner folder browse metadata layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_owner_folder_browse_metadata_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes, FOLDER_MAP, MISSION_LANES
    from vault.owner_file_detail_metadata_view_layer_service import (
        get_file_detail_route_payload_builder,
        get_file_identity_summary_board,
        get_file_lock_status_board,
        validate_owner_file_detail_metadata_view_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP321-GP330 requires GP311-GP320 owner file detail metadata view layer first."
    ) from exc


LOCKS = {
    "owner_folder_browse_metadata_layer": True,
    "folder_browse_metadata_allowed": True,
    "mission_lane_grouping_allowed": True,
    "folder_card_payload_allowed": True,
    "breadcrumb_metadata_allowed": True,
    "folder_file_rows_allowed": True,
    "sort_filter_metadata_allowed": True,
    "folder_browse_audit_allowed": True,
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
    {"gp": 321, "title": "Owner Folder Browse Metadata Shell", "status": "ready", "route": "/vault/owner-folder-browse-metadata-shell.json"},
    {"gp": 322, "title": "Folder Browse Index Builder", "status": "ready", "route": "/vault/folder-browse-index-builder.json"},
    {"gp": 323, "title": "Mission Lane Folder Group Board", "status": "ready", "route": "/vault/mission-lane-folder-group-board.json"},
    {"gp": 324, "title": "Folder Breadcrumb Metadata Contract", "status": "ready", "route": "/vault/folder-breadcrumb-metadata-contract.json"},
    {"gp": 325, "title": "Folder File Row Payload Builder", "status": "ready", "route": "/vault/folder-file-row-payload-builder.json"},
    {"gp": 326, "title": "Empty Folder Placeholder Board", "status": "ready", "route": "/vault/empty-folder-placeholder-board.json"},
    {"gp": 327, "title": "Folder Browse Sort and Filter Contract", "status": "ready", "route": "/vault/folder-browse-sort-filter-contract.json"},
    {"gp": 328, "title": "Folder Browse Audit Snapshot Ledger", "status": "ready", "route": "/vault/folder-browse-audit-snapshot-ledger.json"},
    {"gp": 329, "title": "Folder Browse Safety Blocker Board", "status": "ready", "route": "/vault/folder-browse-safety-blocker-board.json"},
    {"gp": 330, "title": "Owner Folder Browse Metadata Readiness Checkpoint", "status": "ready", "route": "/vault/owner-folder-browse-metadata-readiness-checkpoint.json"},
]

SORT_FILTER_OPTIONS = {
    "sort_fields": ["original_filename", "created_at", "size_bytes", "mime_type", "mission_lane", "folder_key"],
    "default_sort": "original_filename",
    "sort_direction": ["asc", "desc"],
    "filter_fields": ["mission_lane", "folder_key", "mime_type", "lock_status", "quarantine_held"],
    "search_fields": ["original_filename", "safe_stored_name", "sha256_hash"],
    "metadata_only": True,
}

BLOCKERS = [
    {
        "blocker_id": "no_object_body_read",
        "label": "Object body read remains locked",
        "blocked_action": "object_body_read",
        "allowed": False,
        "reason": "Folder browse uses metadata rows only.",
    },
    {
        "blocker_id": "no_plaintext_content",
        "label": "Plaintext content remains locked",
        "blocked_action": "plaintext_content",
        "allowed": False,
        "reason": "Folder browse does not extract or display file contents.",
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
        "reason": "Folder browsing does not release or move physical objects.",
    },
    {
        "blocker_id": "no_public_upload",
        "label": "Public upload remains locked",
        "blocked_action": "public_upload",
        "allowed": False,
        "reason": "Folder browse does not expose public upload.",
    },
    {
        "blocker_id": "no_beta_upload",
        "label": "Beta upload remains locked",
        "blocked_action": "beta_upload",
        "allowed": False,
        "reason": "Folder browse does not expose beta upload.",
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
        "reason": "Folder browse does not sync externally.",
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


def _folder_card_id(folder_key: str) -> str:
    return "folder_card_" + calculate_sha256_bytes(("folder|" + folder_key).encode("utf-8"))[:24]


def _folder_file_row_id(active_file_id: str) -> str:
    return "folder_file_row_" + calculate_sha256_bytes(("row|" + active_file_id).encode("utf-8"))[:24]


def _breadcrumb_id(folder_key: str) -> str:
    return "breadcrumb_" + calculate_sha256_bytes(("breadcrumb|" + folder_key).encode("utf-8"))[:24]


def _audit_snapshot_id(folder_key: str) -> str:
    return "folder_browse_audit_" + calculate_sha256_bytes(("audit|" + folder_key).encode("utf-8"))[:24]


def _known_folder(folder_key: str) -> Dict[str, Any]:
    for item in FOLDER_MAP:
        if item["folder_key"] == folder_key:
            return item
    return {
        "folder_key": folder_key,
        "display_name": folder_key.replace("_", " ").title(),
        "mission_lane": "vault",
        "relative_path": folder_key.replace("_", " ").title(),
    }


def _folder_path_parts(folder_key: str) -> List[str]:
    folder = _known_folder(folder_key)
    lane = folder.get("mission_lane", "vault")
    display_name = folder.get("display_name", folder_key)
    return ["Vault", "Owner Files", lane, display_name]


def initialize_owner_folder_browse_metadata_layer() -> Dict[str, Any]:
    previous = validate_owner_file_detail_metadata_view_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS folder_browse_index (
                folder_card_id TEXT PRIMARY KEY,
                folder_key TEXT NOT NULL,
                display_name TEXT NOT NULL,
                mission_lane TEXT NOT NULL,
                relative_path TEXT NOT NULL,
                file_count INTEGER NOT NULL,
                total_size_bytes INTEGER NOT NULL,
                metadata_only INTEGER NOT NULL,
                object_body_read_locked INTEGER NOT NULL,
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
            CREATE TABLE IF NOT EXISTS folder_file_rows (
                folder_file_row_id TEXT PRIMARY KEY,
                folder_key TEXT NOT NULL,
                active_file_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                safe_stored_name TEXT NOT NULL,
                mission_lane TEXT NOT NULL,
                owner_lane TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                sha256_hash TEXT NOT NULL,
                registry_state TEXT NOT NULL,
                object_body_read_locked INTEGER NOT NULL,
                preview_locked INTEGER NOT NULL,
                download_locked INTEGER NOT NULL,
                share_locked INTEGER NOT NULL,
                delete_locked INTEGER NOT NULL,
                restore_locked INTEGER NOT NULL,
                metadata_only INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS folder_breadcrumb_metadata (
                breadcrumb_id TEXT PRIMARY KEY,
                folder_key TEXT NOT NULL,
                mission_lane TEXT NOT NULL,
                breadcrumb_json TEXT NOT NULL,
                active_depth INTEGER NOT NULL,
                object_body_read_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS empty_folder_placeholders (
                placeholder_id TEXT PRIMARY KEY,
                folder_key TEXT NOT NULL,
                display_name TEXT NOT NULL,
                mission_lane TEXT NOT NULL,
                relative_path TEXT NOT NULL,
                file_count INTEGER NOT NULL,
                placeholder_visible INTEGER NOT NULL,
                upload_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS folder_browse_audit_snapshot_ledger (
                audit_snapshot_id TEXT PRIMARY KEY,
                folder_key TEXT NOT NULL,
                file_count INTEGER NOT NULL,
                total_size_bytes INTEGER NOT NULL,
                metadata_only INTEGER NOT NULL,
                object_body_read_executed INTEGER NOT NULL,
                preview_executed INTEGER NOT NULL,
                download_executed INTEGER NOT NULL,
                snapshot_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS folder_browse_safety_blockers (
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
                INSERT OR REPLACE INTO folder_browse_safety_blockers (
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

        payloads = get_file_detail_route_payload_builder().get("payloads", [])
        by_folder: Dict[str, List[Dict[str, Any]]] = {}

        for payload in payloads:
            identity = payload["identity"]
            folder_key = identity["folder_key"]
            by_folder.setdefault(folder_key, []).append(payload)

            locks = payload["locks"]
            conn.execute(
                """
                INSERT OR REPLACE INTO folder_file_rows (
                    folder_file_row_id, folder_key, active_file_id,
                    original_filename, safe_stored_name, mission_lane, owner_lane,
                    size_bytes, mime_type, sha256_hash, registry_state,
                    object_body_read_locked, preview_locked, download_locked,
                    share_locked, delete_locked, restore_locked, metadata_only,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _folder_file_row_id(payload["active_file_id"]),
                    folder_key,
                    payload["active_file_id"],
                    identity["original_filename"],
                    identity["safe_stored_name"],
                    identity["mission_lane"],
                    identity["owner_lane"],
                    identity["size_bytes"],
                    identity["mime_type"],
                    identity["sha256_hash"],
                    identity["registry_state"],
                    1 if locks["object_body_read_locked"] else 0,
                    1 if locks["preview_locked"] else 0,
                    1 if locks["download_locked"] else 0,
                    1 if locks["share_locked"] else 0,
                    1 if locks["delete_locked"] else 0,
                    1 if locks["restore_locked"] else 0,
                    1,
                    now,
                    now,
                ),
            )

        known_folder_keys = [item["folder_key"] for item in FOLDER_MAP]

        for folder_key in sorted(set(known_folder_keys) | set(by_folder.keys())):
            folder = _known_folder(folder_key)
            files = by_folder.get(folder_key, [])
            total_size = sum(int(item["identity"]["size_bytes"]) for item in files)
            file_count = len(files)

            conn.execute(
                """
                INSERT OR REPLACE INTO folder_browse_index (
                    folder_card_id, folder_key, display_name, mission_lane,
                    relative_path, file_count, total_size_bytes, metadata_only,
                    object_body_read_locked, preview_locked, download_locked,
                    share_locked, delete_locked, restore_locked, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _folder_card_id(folder_key),
                    folder_key,
                    folder["display_name"],
                    folder["mission_lane"],
                    folder["relative_path"],
                    file_count,
                    total_size,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    now,
                    now,
                ),
            )

            breadcrumb_parts = _folder_path_parts(folder_key)
            conn.execute(
                """
                INSERT OR REPLACE INTO folder_breadcrumb_metadata (
                    breadcrumb_id, folder_key, mission_lane, breadcrumb_json,
                    active_depth, object_body_read_allowed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _breadcrumb_id(folder_key),
                    folder_key,
                    folder["mission_lane"],
                    json.dumps(breadcrumb_parts),
                    len(breadcrumb_parts),
                    0,
                    now,
                    now,
                ),
            )

            if file_count == 0:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO empty_folder_placeholders (
                        placeholder_id, folder_key, display_name, mission_lane,
                        relative_path, file_count, placeholder_visible,
                        upload_allowed, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "empty_" + _folder_card_id(folder_key),
                        folder_key,
                        folder["display_name"],
                        folder["mission_lane"],
                        folder["relative_path"],
                        0,
                        1,
                        0,
                        now,
                        now,
                    ),
                )

            snapshot_material = {
                "folder_key": folder_key,
                "file_count": file_count,
                "total_size_bytes": total_size,
                "metadata_only": True,
                "object_body_read_executed": False,
                "preview_executed": False,
                "download_executed": False,
            }
            snapshot_hash = calculate_sha256_bytes(repr(sorted(snapshot_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO folder_browse_audit_snapshot_ledger (
                    audit_snapshot_id, folder_key, file_count, total_size_bytes,
                    metadata_only, object_body_read_executed, preview_executed,
                    download_executed, snapshot_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _audit_snapshot_id(folder_key),
                    folder_key,
                    file_count,
                    total_size,
                    1,
                    0,
                    0,
                    0,
                    snapshot_hash,
                    now,
                ),
            )

        conn.commit()

    return {
        "initialized": True,
        "previous_file_detail_metadata_view_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
    }


def get_owner_folder_browse_metadata_shell() -> Dict[str, Any]:
    init = initialize_owner_folder_browse_metadata_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 321,
        "title": "Owner Folder Browse Metadata Shell",
        "ready": True,
        "initialized": init,
        "folder_browse_metadata_allowed": True,
        "object_body_read_allowed": False,
        "file_preview_unlocked": False,
        "file_download_unlocked": False,
        "locks": LOCKS,
    }


def get_folder_browse_index_builder() -> Dict[str, Any]:
    initialize_owner_folder_browse_metadata_layer()
    with _connect() as conn:
        folders = _rows(conn, "SELECT * FROM folder_browse_index ORDER BY mission_lane, display_name")

    return {
        "section": SECTION,
        "gp": 322,
        "title": "Folder Browse Index Builder",
        "ready": True,
        "folder_count": len(folders),
        "folders": folders,
        "metadata_only": True,
        "object_body_read_allowed": False,
        "download_allowed": False,
    }


def get_mission_lane_folder_group_board() -> Dict[str, Any]:
    initialize_owner_folder_browse_metadata_layer()
    with _connect() as conn:
        folders = _rows(conn, "SELECT * FROM folder_browse_index ORDER BY mission_lane, display_name")

    groups: Dict[str, Dict[str, Any]] = {}
    for folder in folders:
        lane = folder["mission_lane"]
        groups.setdefault(
            lane,
            {
                "mission_lane": lane,
                "folder_count": 0,
                "file_count": 0,
                "total_size_bytes": 0,
                "folders": [],
            },
        )
        groups[lane]["folder_count"] += 1
        groups[lane]["file_count"] += int(folder["file_count"])
        groups[lane]["total_size_bytes"] += int(folder["total_size_bytes"])
        groups[lane]["folders"].append(folder)

    return {
        "section": SECTION,
        "gp": 323,
        "title": "Mission Lane Folder Group Board",
        "ready": True,
        "mission_lane_count": len(groups),
        "mission_lanes": list(groups.values()),
        "known_mission_lanes": MISSION_LANES,
        "metadata_only": True,
    }


def get_folder_breadcrumb_metadata_contract() -> Dict[str, Any]:
    initialize_owner_folder_browse_metadata_layer()
    with _connect() as conn:
        breadcrumbs = _rows(conn, "SELECT * FROM folder_breadcrumb_metadata ORDER BY mission_lane, folder_key")

    decoded = []
    for item in breadcrumbs:
        clone = dict(item)
        clone["breadcrumb_parts"] = json.loads(item["breadcrumb_json"])
        decoded.append(clone)

    return {
        "section": SECTION,
        "gp": 324,
        "title": "Folder Breadcrumb Metadata Contract",
        "ready": True,
        "breadcrumb_count": len(decoded),
        "breadcrumbs": decoded,
        "object_body_read_allowed": False,
        "breadcrumb_rules": {
            "root_label": "Vault",
            "owner_scope_label": "Owner Files",
            "mission_lane_required": True,
            "folder_key_required": True,
            "metadata_only": True,
        },
    }


def get_folder_file_row_payload_builder() -> Dict[str, Any]:
    initialize_owner_folder_browse_metadata_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM folder_file_rows ORDER BY folder_key, original_filename")

    payloads = []
    for item in rows:
        payloads.append(
            {
                "folder_file_row_id": item["folder_file_row_id"],
                "folder_key": item["folder_key"],
                "active_file_id": item["active_file_id"],
                "identity": {
                    "original_filename": item["original_filename"],
                    "safe_stored_name": item["safe_stored_name"],
                    "mission_lane": item["mission_lane"],
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
                },
                "metadata_only": bool(item["metadata_only"]),
            }
        )

    return {
        "section": SECTION,
        "gp": 325,
        "title": "Folder File Row Payload Builder",
        "ready": True,
        "row_count": len(payloads),
        "rows": payloads,
        "metadata_only": True,
        "object_body_included": False,
        "download_url_included": False,
    }


def get_empty_folder_placeholder_board() -> Dict[str, Any]:
    initialize_owner_folder_browse_metadata_layer()
    with _connect() as conn:
        placeholders = _rows(conn, "SELECT * FROM empty_folder_placeholders ORDER BY mission_lane, display_name")

    return {
        "section": SECTION,
        "gp": 326,
        "title": "Empty Folder Placeholder Board",
        "ready": True,
        "placeholder_count": len(placeholders),
        "placeholders": placeholders,
        "upload_allowed": False,
        "all_placeholders_upload_locked": all(not bool(item["upload_allowed"]) for item in placeholders),
    }


def get_folder_browse_sort_filter_contract() -> Dict[str, Any]:
    initialize_owner_folder_browse_metadata_layer()
    return {
        "section": SECTION,
        "gp": 327,
        "title": "Folder Browse Sort and Filter Contract",
        "ready": True,
        "sort_filter_options": SORT_FILTER_OPTIONS,
        "metadata_only": True,
        "body_search_allowed": False,
        "plaintext_search_allowed": False,
        "download_required": False,
    }


def get_folder_browse_audit_snapshot_ledger() -> Dict[str, Any]:
    initialize_owner_folder_browse_metadata_layer()
    with _connect() as conn:
        audits = _rows(conn, "SELECT * FROM folder_browse_audit_snapshot_ledger ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 328,
        "title": "Folder Browse Audit Snapshot Ledger",
        "ready": True,
        "audit_snapshot_count": len(audits),
        "audit_snapshots": audits,
        "no_object_body_reads_executed": all(not bool(item["object_body_read_executed"]) for item in audits),
        "no_previews_executed": all(not bool(item["preview_executed"]) for item in audits),
        "no_downloads_executed": all(not bool(item["download_executed"]) for item in audits),
    }


def get_folder_browse_safety_blocker_board() -> Dict[str, Any]:
    initialize_owner_folder_browse_metadata_layer()
    with _connect() as conn:
        blockers = _rows(conn, "SELECT * FROM folder_browse_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 329,
        "title": "Folder Browse Safety Blocker Board",
        "ready": True,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "unsafe_action_count": sum(1 for item in blockers if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in blockers),
    }


def get_owner_folder_browse_metadata_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_owner_folder_browse_metadata_layer()

    shell = get_owner_folder_browse_metadata_shell()
    index = get_folder_browse_index_builder()
    lanes = get_mission_lane_folder_group_board()
    breadcrumbs = get_folder_breadcrumb_metadata_contract()
    rows = get_folder_file_row_payload_builder()
    empty = get_empty_folder_placeholder_board()
    sort_filter = get_folder_browse_sort_filter_contract()
    audits = get_folder_browse_audit_snapshot_ledger()
    blockers = get_folder_browse_safety_blocker_board()

    checks = {
        "previous_file_detail_metadata_view_ready": init["previous_file_detail_metadata_view_ready"] is True,
        "folder_shell_ready": shell["ready"] is True,
        "folder_index_ready": index["ready"] is True and index["folder_count"] >= len(FOLDER_MAP),
        "mission_lane_groups_ready": lanes["ready"] is True and lanes["mission_lane_count"] >= 1,
        "breadcrumb_metadata_ready": breadcrumbs["ready"] is True and breadcrumbs["breadcrumb_count"] >= len(FOLDER_MAP),
        "folder_file_rows_ready": rows["ready"] is True and rows["row_count"] >= 2,
        "empty_folder_placeholders_ready": empty["ready"] is True and empty["all_placeholders_upload_locked"] is True,
        "sort_filter_contract_ready": sort_filter["ready"] is True and sort_filter["metadata_only"] is True,
        "audit_snapshot_ready": audits["ready"] is True and audits["no_object_body_reads_executed"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "object_body_read_still_locked": LOCKS["object_body_read_allowed"] is False,
        "preview_still_locked": LOCKS["file_preview_unlocked"] is False,
        "download_still_locked": LOCKS["file_download_unlocked"] is False,
        "share_still_locked": LOCKS["file_share_unlocked"] is False,
        "quarantine_release_still_locked": LOCKS["quarantine_release_allowed"] is False,
        "provider_not_required": LOCKS["provider_storage_required"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 330,
        "title": "Owner Folder Browse Metadata Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Owner folder browse metadata layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — OWNER SAFE PREVIEW LOCK PREP LAYER / GP331-GP340",
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


def get_owner_folder_browse_metadata_home() -> Dict[str, Any]:
    checkpoint = get_owner_folder_browse_metadata_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_owner_folder_browse_metadata_layer() -> Dict[str, Any]:
    checkpoint = get_owner_folder_browse_metadata_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_file_detail_metadata_view_ready"] is True
    assert checkpoint["checks"]["folder_index_ready"] is True
    assert checkpoint["checks"]["mission_lane_groups_ready"] is True
    assert checkpoint["checks"]["breadcrumb_metadata_ready"] is True
    assert checkpoint["checks"]["folder_file_rows_ready"] is True
    assert checkpoint["checks"]["empty_folder_placeholders_ready"] is True
    assert checkpoint["checks"]["sort_filter_contract_ready"] is True
    assert checkpoint["checks"]["audit_snapshot_ready"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["folder_browse_metadata_allowed"] is True
    assert LOCKS["mission_lane_grouping_allowed"] is True
    assert LOCKS["folder_card_payload_allowed"] is True
    assert LOCKS["breadcrumb_metadata_allowed"] is True
    assert LOCKS["folder_file_rows_allowed"] is True
    assert LOCKS["sort_filter_metadata_allowed"] is True
    assert LOCKS["folder_browse_audit_allowed"] is True

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
    checkpoint = get_owner_folder_browse_metadata_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "locks_preserved": True,
        "folder_browse_metadata_allowed": True,
        "object_body_read_allowed": False,
        "preview_allowed": False,
        "download_allowed": False,
    }


def get_gp321_status() -> Dict[str, Any]:
    return _gp_status(321)


def get_gp322_status() -> Dict[str, Any]:
    return _gp_status(322)


def get_gp323_status() -> Dict[str, Any]:
    return _gp_status(323)


def get_gp324_status() -> Dict[str, Any]:
    return _gp_status(324)


def get_gp325_status() -> Dict[str, Any]:
    return _gp_status(325)


def get_gp326_status() -> Dict[str, Any]:
    return _gp_status(326)


def get_gp327_status() -> Dict[str, Any]:
    return _gp_status(327)


def get_gp328_status() -> Dict[str, Any]:
    return _gp_status(328)


def get_gp329_status() -> Dict[str, Any]:
    return _gp_status(329)


def get_gp330_status() -> Dict[str, Any]:
    return _gp_status(330)
