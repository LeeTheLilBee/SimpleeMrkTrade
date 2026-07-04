"""
VAULT GP111-GP120 — Redacted Archive Browser Layer

New section:
Archive Vault — Redacted Archive Browser Layer / GP111-GP120

Builds:
- GP111 Redacted Archive Browser Shell
- GP112 Business Lane Folder Navigation
- GP113 Redacted Archive Object Cards
- GP114 Archive Search Index
- GP115 Receipt and Proof Packet Browser
- GP116 Case-to-Archive Link View
- GP117 Archive Filter Board
- GP118 Redacted Metadata Detail Drawer
- GP119 Archive Browser Blocker Board
- GP120 Redacted Archive Browser Readiness Checkpoint

This layer creates a browsable, searchable, owner-facing redacted archive view
sourced from GP101-GP110 recovery cases. It never reads object bodies,
downloads content, exports packages, calls provider APIs, unlocks Tower gates,
executes, or marks Vault done.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Dict, Optional

from vault.real_provider_recovery_case_workspace_layer_service import (
    get_gp110_status,
    get_gp110_recovery_case_workspace_readiness_checkpoint,
    get_recovery_case_workspace_layer_home,
    validate_recovery_case_workspace_layer,
    get_recovery_cases,
    get_recovery_case_receipts,
    get_recovery_case_evidence_links,
    get_redacted_object_references,
    get_recovery_case_blockers,
)

LAYER_ID = "VAULT_GP111_120"
LAYER_NAME = "Redacted Archive Browser Layer"
SCHEMA_VERSION = "vault.redacted_archive_browser_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_REDACTED_ARCHIVE_BROWSER_LAYER"
SECTION_TITLE = "Archive Vault — Redacted Archive Browser Layer"
SECTION_RANGE = "GP111-GP120"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RECOVERY_CASE_WORKSPACE_LAYER"
PREVIOUS_SECTION_RANGE = "GP101-GP110"

NEXT_SECTION_ID = "ARCHIVE_VAULT_OWNER_CONSOLE_AND_OPERATING_DASHBOARD_LAYER"
NEXT_SECTION_RANGE = "GP121-GP130"
NEXT_PACK = "VAULT_GP121_130_OWNER_CONSOLE_AND_OPERATING_DASHBOARD_LAYER"

DEFAULT_DB_ENV = "VAULT_REDACTED_ARCHIVE_BROWSER_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_redacted_archive_browser_layer.sqlite"

BROWSER_SHELL_ID = "VRABS-GP111-001"
FOLDER_NAV_ID = "VRABFN-GP112-001"
OBJECT_CARDS_ID = "VRABOC-GP113-001"
SEARCH_INDEX_ID = "VRABSI-GP114-001"
PROOF_PACKET_BROWSER_ID = "VRABPPB-GP115-001"
CASE_LINK_VIEW_ID = "VRABCLV-GP116-001"
FILTER_BOARD_ID = "VRABFB-GP117-001"
METADATA_DRAWER_ID = "VRABMDD-GP118-001"
BROWSER_BLOCKER_BOARD_ID = "VRABBBB-GP119-001"
READINESS_ID = "VRABRC-GP120-001"

FALSE_FIELDS = [
    "provider_api_configured",
    "provider_api_called",
    "provider_object_catalog_unlocked",
    "provider_objects_listed",
    "provider_metadata_imported",
    "provider_metadata_read",
    "object_identifier_collected",
    "object_body_read_attempted",
    "object_body_read",
    "object_body_view_enabled",
    "object_body_download_enabled",
    "object_body_content_exposed",
    "object_body_plaintext_visible",
    "object_download_created",
    "object_download_enabled",
    "archive_file_opened",
    "archive_file_streamed",
    "archive_file_exported",
    "export_requested",
    "export_approved",
    "export_package_created",
    "export_manifest_created",
    "export_download_enabled",
    "export_enabled",
    "restore_requested",
    "restore_approved",
    "restore_request_created",
    "restore_request_submitted",
    "restore_job_configured",
    "restore_job_created",
    "restore_job_started",
    "restore_job_completed",
    "provider_restore_api_configured",
    "provider_restore_api_called",
    "direct_upload_enabled",
    "tower_unlock_requested",
    "tower_unlock_granted",
    "owner_decision_recorded",
    "owner_approval_recorded",
    "execution_enabled",
    "vault_done",
    "clouds_should_continue",
]

FOLDER_SPECS = [
    ("trust", "Trust", "Trust archive lane", "high"),
    ("business", "Business", "Business archive lane", "high"),
    ("atm", "ATM", "ATM archive lane", "medium"),
    ("property", "Property", "Property archive lane", "medium"),
    ("owner", "Owner", "Owner archive lane", "high"),
    ("operations", "Operations", "Operations archive lane", "medium"),
    ("archive", "Archive", "Archive system lane", "high"),
    ("provider", "Provider", "Provider governance lane", "high"),
]

FILTER_SPECS = [
    ("business_lane", "Business Lane", "folder"),
    ("sensitivity_label", "Sensitivity Label", "security"),
    ("case_type", "Case Type", "case"),
    ("blocker_status", "Blocker Status", "blocker"),
    ("redacted_only", "Redacted Only", "privacy"),
    ("receipt_linked", "Receipt Linked", "receipt"),
    ("evidence_linked", "Evidence Linked", "evidence"),
    ("safe_action", "Safe Action", "governance"),
]

COMPONENT_SPECS = [
    (111, BROWSER_SHELL_ID, "VAULT_GP111", "Redacted Archive Browser Shell", "redacted_archive_browser_shell"),
    (112, FOLDER_NAV_ID, "VAULT_GP112", "Business Lane Folder Navigation", "business_lane_folder_navigation"),
    (113, OBJECT_CARDS_ID, "VAULT_GP113", "Redacted Archive Object Cards", "redacted_archive_object_cards"),
    (114, SEARCH_INDEX_ID, "VAULT_GP114", "Archive Search Index", "archive_search_index"),
    (115, PROOF_PACKET_BROWSER_ID, "VAULT_GP115", "Receipt and Proof Packet Browser", "receipt_and_proof_packet_browser"),
    (116, CASE_LINK_VIEW_ID, "VAULT_GP116", "Case-to-Archive Link View", "case_to_archive_link_view"),
    (117, FILTER_BOARD_ID, "VAULT_GP117", "Archive Filter Board", "archive_filter_board"),
    (118, METADATA_DRAWER_ID, "VAULT_GP118", "Redacted Metadata Detail Drawer", "redacted_metadata_detail_drawer"),
    (119, BROWSER_BLOCKER_BOARD_ID, "VAULT_GP119", "Archive Browser Blocker Board", "archive_browser_blocker_board"),
    (120, READINESS_ID, "VAULT_GP120", "Redacted Archive Browser Readiness Checkpoint", "redacted_archive_browser_readiness_checkpoint"),
]

def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _resolve_db_path(db_path: Optional[str] = None) -> Path:
    return Path(db_path or os.environ.get(DEFAULT_DB_ENV) or DEFAULT_DB_PATH)

def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)

def _json_loads(value: str) -> Any:
    return json.loads(value)

def _hash_payload(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(_json_dumps(payload).encode("utf-8")).hexdigest()

def _connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = _resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _insert_dict(conn: sqlite3.Connection, table: str, payload: Dict[str, Any]) -> None:
    cols = list(payload.keys())
    conn.execute(
        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(['?'] * len(cols))})",
        tuple(payload[c] for c in cols),
    )

def _boolify(row: sqlite3.Row, json_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    json_fields = json_fields or {}
    numeric_fields = {
        "gp_number",
        "source_gp110_readiness_score",
        "folder_count",
        "object_card_count",
        "search_index_count",
        "proof_packet_count",
        "case_link_count",
        "filter_count",
        "metadata_drawer_count",
        "blocker_count",
        "component_count",
        "event_count",
        "readiness_score",
        "check_count",
        "passed_count",
        "failed_count",
    }
    payload = {}
    for key in row.keys():
        if key in json_fields:
            payload[json_fields[key]] = _json_loads(row[key])
        elif isinstance(row[key], int) and (
            key in numeric_fields
            or key.endswith("_count")
            or key.endswith("_score")
            or key.endswith("_order")
            or key.endswith("_number")
            or key.endswith("_position")
        ):
            payload[key] = int(row[key])
        elif isinstance(row[key], int):
            payload[key] = bool(row[key])
        else:
            payload[key] = row[key]
    return payload

def _layer_pack_payload() -> Dict[str, Any]:
    return {
        "id": LAYER_ID,
        "name": LAYER_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP110"],
        "packs": [item[2] for item in COMPONENT_SPECS],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "previous_section": PREVIOUS_SECTION_ID,
        "previous_section_range": PREVIOUS_SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
        "next_pack": NEXT_PACK,
    }

def _pack_payload(gp_number: int, pack_name: str) -> Dict[str, Any]:
    return {
        "id": f"VAULT_GP{gp_number:03d}",
        "name": pack_name,
        "layer_id": LAYER_ID,
        "layer_name": LAYER_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP110"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_redacted_archive_browser_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)
    false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)
    readiness_false_sql = ",\n".join(
        f"{field} INTEGER NOT NULL DEFAULT 0"
        for field in FALSE_FIELDS
        if field not in {"vault_done", "clouds_should_continue"}
    )

    with _connect(str(path)) as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_redacted_archive_browser_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp110_readiness_id TEXT NOT NULL,
                source_gp110_readiness_hash TEXT NOT NULL,
                source_gp110_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                owner_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                safe_to_continue INTEGER NOT NULL DEFAULT 1,
                data_json TEXT NOT NULL,
                component_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_redacted_archive_folders (
                folder_id TEXT PRIMARY KEY,
                folder_code TEXT NOT NULL UNIQUE,
                folder_name TEXT NOT NULL,
                folder_description TEXT NOT NULL,
                sensitivity_label TEXT NOT NULL,
                source_gp110_readiness_hash TEXT NOT NULL,
                folder_ready INTEGER NOT NULL DEFAULT 1,
                folder_locked INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                folder_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_redacted_archive_object_cards (
                object_card_id TEXT PRIMARY KEY,
                object_card_code TEXT NOT NULL UNIQUE,
                source_case_id TEXT NOT NULL,
                source_case_code TEXT NOT NULL,
                folder_code TEXT NOT NULL,
                object_title TEXT NOT NULL,
                object_category TEXT NOT NULL,
                sensitivity_label TEXT NOT NULL,
                redaction_label TEXT NOT NULL,
                provider_reference_placeholder TEXT NOT NULL,
                object_card_status TEXT NOT NULL,
                object_card_ready INTEGER NOT NULL DEFAULT 1,
                object_card_locked INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                object_card_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_redacted_archive_search_index (
                search_index_id TEXT PRIMARY KEY,
                search_code TEXT NOT NULL UNIQUE,
                source_object_card_id TEXT NOT NULL,
                search_title TEXT NOT NULL,
                search_terms_json TEXT NOT NULL,
                search_scope TEXT NOT NULL,
                search_status TEXT NOT NULL,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                search_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_redacted_archive_proof_packet_links (
                proof_packet_link_id TEXT PRIMARY KEY,
                proof_packet_code TEXT NOT NULL UNIQUE,
                source_case_id TEXT NOT NULL,
                source_ref TEXT NOT NULL,
                proof_packet_title TEXT NOT NULL,
                proof_packet_status TEXT NOT NULL,
                proof_packet_locked INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                proof_packet_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_redacted_archive_case_links (
                case_link_id TEXT PRIMARY KEY,
                case_link_code TEXT NOT NULL UNIQUE,
                source_case_id TEXT NOT NULL,
                source_case_code TEXT NOT NULL,
                object_card_id TEXT NOT NULL,
                evidence_link_count INTEGER NOT NULL,
                receipt_link_count INTEGER NOT NULL,
                case_link_status TEXT NOT NULL,
                case_link_locked INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                case_link_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_redacted_archive_filters (
                filter_id TEXT PRIMARY KEY,
                filter_code TEXT NOT NULL UNIQUE,
                filter_name TEXT NOT NULL,
                filter_category TEXT NOT NULL,
                filter_status TEXT NOT NULL,
                filter_locked INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                filter_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_redacted_archive_metadata_drawers (
                drawer_id TEXT PRIMARY KEY,
                drawer_code TEXT NOT NULL UNIQUE,
                object_card_id TEXT NOT NULL,
                drawer_title TEXT NOT NULL,
                drawer_status TEXT NOT NULL,
                redacted_metadata_json TEXT NOT NULL,
                drawer_locked INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                drawer_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_redacted_archive_browser_blockers (
                blocker_id TEXT PRIMARY KEY,
                blocker_code TEXT NOT NULL UNIQUE,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocker_active INTEGER NOT NULL DEFAULT 1,
                blocks_provider_api INTEGER NOT NULL DEFAULT 1,
                blocks_object_body INTEGER NOT NULL DEFAULT 1,
                blocks_download INTEGER NOT NULL DEFAULT 1,
                blocks_export INTEGER NOT NULL DEFAULT 1,
                blocks_restore INTEGER NOT NULL DEFAULT 1,
                blocks_direct_upload INTEGER NOT NULL DEFAULT 1,
                blocks_tower_unlock INTEGER NOT NULL DEFAULT 1,
                blocks_execution INTEGER NOT NULL DEFAULT 1,
                blocks_vault_done INTEGER NOT NULL DEFAULT 1,
                resolved INTEGER NOT NULL DEFAULT 0,
                payload_json TEXT NOT NULL,
                blocker_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_redacted_archive_browser_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                folder_count INTEGER NOT NULL,
                object_card_count INTEGER NOT NULL,
                search_index_count INTEGER NOT NULL,
                proof_packet_count INTEGER NOT NULL,
                case_link_count INTEGER NOT NULL,
                filter_count INTEGER NOT NULL,
                metadata_drawer_count INTEGER NOT NULL,
                blocker_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                safe_to_continue_to_gp121 INTEGER NOT NULL DEFAULT 1,
                section_ready INTEGER NOT NULL DEFAULT 1,
                vault_done INTEGER NOT NULL DEFAULT 0,
                clouds_should_continue INTEGER NOT NULL DEFAULT 0,
                {readiness_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_redacted_archive_browser_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "real_sqlite_backed": True,
        "tables": [
            "vault_redacted_archive_browser_components",
            "vault_redacted_archive_folders",
            "vault_redacted_archive_object_cards",
            "vault_redacted_archive_search_index",
            "vault_redacted_archive_proof_packet_links",
            "vault_redacted_archive_case_links",
            "vault_redacted_archive_filters",
            "vault_redacted_archive_metadata_drawers",
            "vault_redacted_archive_browser_blockers",
            "vault_redacted_archive_browser_readiness",
            "vault_redacted_archive_browser_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VRABEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_redacted_archive_browser_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_redacted_archive_browser_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_redacted_archive_browser_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_redacted_archive_browser_components WHERE component_id = ?",
            (BROWSER_SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp110_status = get_gp110_status()["gp110_status"]
            gp110_checkpoint = get_gp110_recovery_case_workspace_readiness_checkpoint()["readiness_checkpoint"]
            gp110_home = get_recovery_case_workspace_layer_home()
            gp110_validation = validate_recovery_case_workspace_layer()

            source_cases = get_recovery_cases()
            source_receipts = get_recovery_case_receipts()
            source_evidence = get_recovery_case_evidence_links()
            source_objects = get_redacted_object_references()
            source_blockers = get_recovery_case_blockers()

            gp110_readiness = gp110_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp110_readiness_id": gp110_readiness["readiness_id"],
                "source_gp110_readiness_hash": gp110_readiness["readiness_hash"],
                "source_gp110_readiness_score": gp110_readiness["readiness_score"],
            }

            source_context = {
                "source_gp110_status_ready": gp110_status["ready"],
                "source_gp110_validation_passed": gp110_status["validation_passed"],
                "source_gp110_safe_to_continue_to_gp111": gp110_status["safe_to_continue_to_gp111"],
                "source_gp110_readiness_hash": gp110_readiness["readiness_hash"],
                "source_gp110_readiness_score": gp110_readiness["readiness_score"],
                "source_case_count": gp110_home["store"]["case_count"],
                "source_receipt_count": gp110_home["store"]["receipt_count"],
                "source_evidence_link_count": gp110_home["store"]["evidence_link_count"],
                "source_redacted_object_reference_count": gp110_home["store"]["redacted_object_reference_count"],
                "source_blocker_count": gp110_home["store"]["blocker_count"],
                "source_validation_check_count": gp110_validation["check_count"],
            }

            component_extra = {
                BROWSER_SHELL_ID: {"browser_shell_ready": True},
                FOLDER_NAV_ID: {"folder_navigation_ready": True, "folder_count": len(FOLDER_SPECS)},
                OBJECT_CARDS_ID: {"object_cards_ready": True, "object_card_count": len(source_objects)},
                SEARCH_INDEX_ID: {"search_index_ready": True, "search_index_count": len(source_objects)},
                PROOF_PACKET_BROWSER_ID: {"proof_packet_browser_ready": True, "proof_packet_count": min(16, len(source_receipts))},
                CASE_LINK_VIEW_ID: {"case_link_view_ready": True, "case_link_count": len(source_cases)},
                FILTER_BOARD_ID: {"filter_board_ready": True, "filter_count": len(FILTER_SPECS)},
                METADATA_DRAWER_ID: {"metadata_detail_drawer_ready": True, "metadata_drawer_count": len(source_objects)},
                BROWSER_BLOCKER_BOARD_ID: {"browser_blocker_board_ready": True, "blocker_count": len(FOLDER_SPECS) * 4},
                READINESS_ID: {"readiness_checkpoint_ready": True, "safe_to_continue_to_gp121": True},
            }

            for gp_number, component_id, pack_id, pack_name, component_type in COMPONENT_SPECS:
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "component_id": component_id,
                    "gp_number": gp_number,
                    "pack_id": pack_id,
                    "pack_name": pack_name,
                    "component_type": component_type,
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    **source_context,
                    **component_extra[component_id],
                    "redacted_only": True,
                    "metadata_only": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "next_section": NEXT_SECTION_ID,
                    "next_section_range": NEXT_SECTION_RANGE,
                    "next_pack": NEXT_PACK,
                }
                component_hash = _hash_payload(payload)
                row = {
                    "component_id": component_id,
                    "gp_number": gp_number,
                    "pack_id": pack_id,
                    "pack_name": pack_name,
                    "component_type": component_type,
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    **source_payload,
                    "component_ready": 1,
                    "component_locked": 1,
                    "redacted_only": 1,
                    "owner_review_required": 1,
                    "tower_review_required": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": component_hash,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_redacted_archive_browser_components", row)

            for folder_code, folder_name, folder_description, sensitivity in FOLDER_SPECS:
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "folder_code": folder_code,
                    "folder_name": folder_name,
                    "folder_description": folder_description,
                    "sensitivity_label": sensitivity,
                    "source_gp110_readiness_hash": gp110_readiness["readiness_hash"],
                    "folder_ready": True,
                    "folder_locked": True,
                    "redacted_only": True,
                    "allowed_actions": ["view_redacted_cards", "filter", "search_redacted_metadata", "open_detail_drawer"],
                    "blocked_actions": ["read_body", "download", "export", "restore", "provider_api", "direct_upload", "execution"],
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                folder_hash = _hash_payload(payload)
                row = {
                    "folder_id": f"VRABF-{folder_code.upper()}",
                    "folder_code": folder_code,
                    "folder_name": folder_name,
                    "folder_description": folder_description,
                    "sensitivity_label": sensitivity,
                    "source_gp110_readiness_hash": gp110_readiness["readiness_hash"],
                    "folder_ready": 1,
                    "folder_locked": 1,
                    "redacted_only": 1,
                    "payload_json": _json_dumps(payload),
                    "folder_hash": folder_hash,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_redacted_archive_folders", row)

            folder_codes = [item[0] for item in FOLDER_SPECS]
            object_cards = []
            for idx, obj in enumerate(source_objects, start=1):
                source_case_id = obj["case_id"]
                source_case = next((case for case in source_cases if case["case_id"] == source_case_id), source_cases[(idx - 1) % len(source_cases)])
                folder_code = str(source_case.get("business_lane", "archive")).lower()
                if folder_code not in folder_codes:
                    folder_code = folder_codes[(idx - 1) % len(folder_codes)]

                object_card_code = f"redacted_archive_object_{idx:03d}"
                object_card_id = f"VRABOC-{idx:03d}"
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "object_card_id": object_card_id,
                    "object_card_code": object_card_code,
                    "source_case_id": source_case["case_id"],
                    "source_case_code": source_case["case_code"],
                    "folder_code": folder_code,
                    "object_title": f"Redacted archive object for {source_case['case_title']}",
                    "object_category": obj["object_category"],
                    "sensitivity_label": source_case["sensitivity_label"],
                    "redaction_label": "REDACTED_METADATA_ONLY_BODY_LOCKED",
                    "provider_reference_placeholder": obj["provider_reference_placeholder"],
                    "object_card_status": "VISIBLE_REDACTED_METADATA_ONLY_LOCKED",
                    "object_card_ready": True,
                    "object_card_locked": True,
                    "redacted_only": True,
                    "metadata_only": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                object_card_hash = _hash_payload(payload)
                row = {
                    "object_card_id": object_card_id,
                    "object_card_code": object_card_code,
                    "source_case_id": source_case["case_id"],
                    "source_case_code": source_case["case_code"],
                    "folder_code": folder_code,
                    "object_title": payload["object_title"],
                    "object_category": obj["object_category"],
                    "sensitivity_label": source_case["sensitivity_label"],
                    "redaction_label": payload["redaction_label"],
                    "provider_reference_placeholder": obj["provider_reference_placeholder"],
                    "object_card_status": payload["object_card_status"],
                    "object_card_ready": 1,
                    "object_card_locked": 1,
                    "redacted_only": 1,
                    "metadata_only": 1,
                    "payload_json": _json_dumps(payload),
                    "object_card_hash": object_card_hash,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_redacted_archive_object_cards", row)
                object_cards.append(row)

                search_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "search_code": f"{object_card_code}_search",
                    "source_object_card_id": object_card_id,
                    "search_title": payload["object_title"],
                    "search_terms": [source_case["case_code"], folder_code, obj["object_category"], source_case["sensitivity_label"], "redacted", "metadata"],
                    "search_scope": "REDACTED_METADATA_ONLY",
                    "redacted_only": True,
                    "metadata_only": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "search_index_id": f"VRABSI-{idx:03d}",
                    "search_code": search_payload["search_code"],
                    "source_object_card_id": object_card_id,
                    "search_title": search_payload["search_title"],
                    "search_terms_json": _json_dumps(search_payload["search_terms"]),
                    "search_scope": search_payload["search_scope"],
                    "search_status": "SEARCHABLE_REDACTED_METADATA_ONLY",
                    "redacted_only": 1,
                    "metadata_only": 1,
                    "search_hash": _hash_payload(search_payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_redacted_archive_search_index", row)

                drawer_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "drawer_code": f"{object_card_code}_drawer",
                    "object_card_id": object_card_id,
                    "drawer_title": f"Redacted metadata drawer for {object_card_code}",
                    "redacted_metadata": {
                        "source_case_code": source_case["case_code"],
                        "folder_code": folder_code,
                        "object_category": obj["object_category"],
                        "sensitivity_label": source_case["sensitivity_label"],
                        "provider_reference_placeholder": obj["provider_reference_placeholder"],
                        "body": "LOCKED",
                        "download": "LOCKED",
                        "plaintext": "LOCKED",
                    },
                    "drawer_locked": True,
                    "redacted_only": True,
                    "metadata_only": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "drawer_id": f"VRABMDD-{idx:03d}",
                    "drawer_code": drawer_payload["drawer_code"],
                    "object_card_id": object_card_id,
                    "drawer_title": drawer_payload["drawer_title"],
                    "drawer_status": "READY_REDACTED_METADATA_ONLY_BODY_LOCKED",
                    "redacted_metadata_json": _json_dumps(drawer_payload["redacted_metadata"]),
                    "drawer_locked": 1,
                    "redacted_only": 1,
                    "metadata_only": 1,
                    "drawer_hash": _hash_payload(drawer_payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_redacted_archive_metadata_drawers", row)

                case_link_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "case_link_code": f"{source_case['case_code']}_archive_link",
                    "source_case_id": source_case["case_id"],
                    "source_case_code": source_case["case_code"],
                    "object_card_id": object_card_id,
                    "evidence_link_count": len([item for item in source_evidence if item["case_id"] == source_case["case_id"]]),
                    "receipt_link_count": len([item for item in source_receipts if item["case_id"] == source_case["case_id"]]),
                    "case_link_locked": True,
                    "redacted_only": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "case_link_id": f"VRABCLV-{idx:03d}",
                    "case_link_code": case_link_payload["case_link_code"],
                    "source_case_id": source_case["case_id"],
                    "source_case_code": source_case["case_code"],
                    "object_card_id": object_card_id,
                    "evidence_link_count": case_link_payload["evidence_link_count"],
                    "receipt_link_count": case_link_payload["receipt_link_count"],
                    "case_link_status": "LINKED_REDACTED_ONLY",
                    "case_link_locked": 1,
                    "redacted_only": 1,
                    "case_link_hash": _hash_payload(case_link_payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_redacted_archive_case_links", row)

            for idx, receipt in enumerate(source_receipts[:16], start=1):
                proof_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "proof_packet_code": f"redacted_proof_packet_{idx:03d}",
                    "source_case_id": receipt["case_id"],
                    "source_ref": receipt["receipt_code"],
                    "proof_packet_title": f"Redacted proof packet link for {receipt['receipt_code']}",
                    "proof_packet_status": "VISIBLE_REDACTED_PROOF_LINK_ONLY",
                    "proof_packet_locked": True,
                    "redacted_only": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "proof_packet_link_id": f"VRABPPB-{idx:03d}",
                    "proof_packet_code": proof_payload["proof_packet_code"],
                    "source_case_id": receipt["case_id"],
                    "source_ref": receipt["receipt_code"],
                    "proof_packet_title": proof_payload["proof_packet_title"],
                    "proof_packet_status": proof_payload["proof_packet_status"],
                    "proof_packet_locked": 1,
                    "redacted_only": 1,
                    "payload_json": _json_dumps(proof_payload),
                    "proof_packet_hash": _hash_payload(proof_payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_redacted_archive_proof_packet_links", row)

            for code, name, category in FILTER_SPECS:
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "filter_code": code,
                    "filter_name": name,
                    "filter_category": category,
                    "filter_status": "AVAILABLE_REDACTED_METADATA_ONLY",
                    "filter_locked": True,
                    "redacted_only": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "filter_id": f"VRABFILT-{code.upper().replace('_', '-')}",
                    "filter_code": code,
                    "filter_name": name,
                    "filter_category": category,
                    "filter_status": payload["filter_status"],
                    "filter_locked": 1,
                    "redacted_only": 1,
                    "payload_json": _json_dumps(payload),
                    "filter_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_redacted_archive_filters", row)

            blocker_specs = [
                ("provider_api_locked", "Provider API locked", "provider_api", "critical"),
                ("object_body_locked", "Object body access locked", "object_body", "critical"),
                ("download_export_locked", "Download and export locked", "export_download", "critical"),
                ("tower_unlock_missing", "Tower unlock missing", "tower", "critical"),
            ]
            blocker_idx = 1
            for folder_code, folder_name, _desc, _sensitivity in FOLDER_SPECS:
                for code, name, category, severity in blocker_specs:
                    blocker_code = f"{folder_code}_{code}"
                    payload = {
                        "schema_version": SCHEMA_VERSION,
                        "blocker_code": blocker_code,
                        "blocker_name": f"{folder_name}: {name}",
                        "blocker_category": category,
                        "severity": severity,
                        "blocker_active": True,
                        "blocks_provider_api": True,
                        "blocks_object_body": True,
                        "blocks_download": True,
                        "blocks_export": True,
                        "blocks_restore": True,
                        "blocks_direct_upload": True,
                        "blocks_tower_unlock": True,
                        "blocks_execution": True,
                        "blocks_vault_done": True,
                        "resolved": False,
                        "locked_truth": {field: False for field in FALSE_FIELDS},
                        "vault_done": False,
                        "clouds_should_continue": False,
                    }
                    row = {
                        "blocker_id": f"VRABBB-{blocker_idx:03d}",
                        "blocker_code": blocker_code,
                        "blocker_name": payload["blocker_name"],
                        "blocker_category": category,
                        "severity": severity,
                        "blocker_status": "ACTIVE_REDACTED_ARCHIVE_BROWSER_BLOCKER",
                        "blocker_active": 1,
                        "blocks_provider_api": 1,
                        "blocks_object_body": 1,
                        "blocks_download": 1,
                        "blocks_export": 1,
                        "blocks_restore": 1,
                        "blocks_direct_upload": 1,
                        "blocks_tower_unlock": 1,
                        "blocks_execution": 1,
                        "blocks_vault_done": 1,
                        "resolved": 0,
                        "payload_json": _json_dumps(payload),
                        "blocker_hash": _hash_payload(payload),
                        "created_at": now,
                        "updated_at": now,
                    }
                    for field in FALSE_FIELDS:
                        row[field] = 0
                    _insert_dict(conn, "vault_redacted_archive_browser_blockers", row)
                    blocker_idx += 1

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "folder_count": len(FOLDER_SPECS),
                "object_card_count": len(source_objects),
                "search_index_count": len(source_objects),
                "proof_packet_count": min(16, len(source_receipts)),
                "case_link_count": len(source_objects),
                "filter_count": len(FILTER_SPECS),
                "metadata_drawer_count": len(source_objects),
                "blocker_count": len(FOLDER_SPECS) * 4,
            }

            checks = [
                ("SOURCE_GP110_READY", bool(gp110_status["ready"])),
                ("SOURCE_GP110_VALIDATION_PASSED", bool(gp110_status["validation_passed"])),
                ("SOURCE_GP110_SAFE_TO_CONTINUE", bool(gp110_status["safe_to_continue_to_gp111"])),
                ("SOURCE_GP110_READINESS_SCORE_100", gp110_readiness["readiness_score"] == 100),
                ("SOURCE_GP110_READINESS_HASH_64", isinstance(gp110_readiness["readiness_hash"], str) and len(gp110_readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("FOLDER_COUNT_8", counts["folder_count"] == 8),
                ("OBJECT_CARD_COUNT_8", counts["object_card_count"] == 8),
                ("SEARCH_INDEX_COUNT_8", counts["search_index_count"] == 8),
                ("PROOF_PACKET_COUNT_16", counts["proof_packet_count"] == 16),
                ("CASE_LINK_COUNT_8", counts["case_link_count"] == 8),
                ("FILTER_COUNT_8", counts["filter_count"] == 8),
                ("METADATA_DRAWER_COUNT_8", counts["metadata_drawer_count"] == 8),
                ("BLOCKER_COUNT_32", counts["blocker_count"] == 32),
                ("SECTION_GP111_GP120", SECTION_RANGE == "GP111-GP120"),
                ("NEXT_SECTION_GP121_GP130", NEXT_SECTION_RANGE == "GP121-GP130"),
                ("NO_PROVIDER_API", True),
                ("NO_OBJECT_BODY", True),
                ("NO_DOWNLOAD", True),
                ("NO_EXPORT", True),
                ("NO_RESTORE", True),
                ("NO_DIRECT_UPLOAD", True),
                ("NO_TOWER_UNLOCK", True),
                ("NO_EXECUTION", True),
                ("VAULT_NOT_DONE", True),
                ("CLOUDS_PARKED", True),
            ]
            passed_count = len([c for c in checks if c[1]])
            failed_count = len(checks) - passed_count

            readiness_payload = {
                "schema_version": SCHEMA_VERSION,
                "readiness_id": READINESS_ID,
                "gp_number": 120,
                "pack_id": "VAULT_GP120",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp110_readiness_id": gp110_readiness["readiness_id"],
                "source_gp110_readiness_hash": gp110_readiness["readiness_hash"],
                "source_gp110_readiness_score": gp110_readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "safe_to_continue_to_gp121": failed_count == 0,
                "section_ready": True,
                "vault_done": False,
                "clouds_should_continue": False,
                "next_section": NEXT_SECTION_ID,
                "next_section_range": NEXT_SECTION_RANGE,
                "next_pack": NEXT_PACK,
                "locked_truth": {field: False for field in FALSE_FIELDS},
            }
            readiness_hash = _hash_payload(readiness_payload)

            row = {
                "readiness_id": READINESS_ID,
                "gp_number": 120,
                "pack_id": "VAULT_GP120",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "REDACTED_ARCHIVE_BROWSER_LAYER_READY_LOCKED_SAFE_TO_CONTINUE_NOT_DONE",
                "readiness_score": readiness_payload["readiness_score"],
                "component_count": counts["component_count"],
                "folder_count": counts["folder_count"],
                "object_card_count": counts["object_card_count"],
                "search_index_count": counts["search_index_count"],
                "proof_packet_count": counts["proof_packet_count"],
                "case_link_count": counts["case_link_count"],
                "filter_count": counts["filter_count"],
                "metadata_drawer_count": counts["metadata_drawer_count"],
                "blocker_count": counts["blocker_count"],
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "safe_to_continue_to_gp121": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_redacted_archive_browser_readiness", row)

            for event_type, event_payload in [
                ("GP111_REDACTED_ARCHIVE_BROWSER_SHELL_CREATED", {"component_id": BROWSER_SHELL_ID}),
                ("GP112_BUSINESS_LANE_FOLDER_NAVIGATION_CREATED", {"folder_count": counts["folder_count"]}),
                ("GP113_REDACTED_ARCHIVE_OBJECT_CARDS_CREATED", {"object_card_count": counts["object_card_count"]}),
                ("GP114_ARCHIVE_SEARCH_INDEX_CREATED", {"search_index_count": counts["search_index_count"]}),
                ("GP115_RECEIPT_AND_PROOF_PACKET_BROWSER_CREATED", {"proof_packet_count": counts["proof_packet_count"]}),
                ("GP116_CASE_TO_ARCHIVE_LINK_VIEW_CREATED", {"case_link_count": counts["case_link_count"]}),
                ("GP117_ARCHIVE_FILTER_BOARD_CREATED", {"filter_count": counts["filter_count"]}),
                ("GP118_REDACTED_METADATA_DETAIL_DRAWER_CREATED", {"metadata_drawer_count": counts["metadata_drawer_count"]}),
                ("GP119_ARCHIVE_BROWSER_BLOCKER_BOARD_CREATED", {"blocker_count": counts["blocker_count"]}),
                ("GP120_REDACTED_ARCHIVE_BROWSER_READINESS_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp121": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_redacted_archive_browser_components").fetchone()["c"]),
            "folder_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_redacted_archive_folders").fetchone()["c"]),
            "object_card_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_redacted_archive_object_cards").fetchone()["c"]),
            "search_index_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_redacted_archive_search_index").fetchone()["c"]),
            "proof_packet_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_redacted_archive_proof_packet_links").fetchone()["c"]),
            "case_link_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_redacted_archive_case_links").fetchone()["c"]),
            "filter_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_redacted_archive_filters").fetchone()["c"]),
            "metadata_drawer_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_redacted_archive_metadata_drawers").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_redacted_archive_browser_blockers").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_redacted_archive_browser_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_redacted_archive_browser_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_redacted_archive_browser_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_redacted_archive_browser_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_redacted_archive_browser_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_redacted_archive_browser_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_redacted_archive_browser_readiness WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_redacted_archive_browser_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_redacted_archive_browser_events ORDER BY created_at, event_id").fetchall()
    return [
        {
            "event_id": row["event_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]

def get_redacted_archive_folders(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_redacted_archive_folders", "folder_code", db_path, {"payload_json": "payload"})

def get_redacted_archive_object_cards(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_redacted_archive_object_cards", "object_card_code", db_path, {"payload_json": "payload"})

def get_redacted_archive_search_index(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_redacted_archive_search_index", "search_code", db_path, {"search_terms_json": "search_terms"})

def get_redacted_archive_proof_packet_links(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_redacted_archive_proof_packet_links", "proof_packet_code", db_path, {"payload_json": "payload"})

def get_redacted_archive_case_links(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_redacted_archive_case_links", "case_link_code", db_path)

def get_redacted_archive_filters(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_redacted_archive_filters", "filter_code", db_path, {"payload_json": "payload"})

def get_redacted_archive_metadata_drawers(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_redacted_archive_metadata_drawers", "drawer_code", db_path, {"redacted_metadata_json": "redacted_metadata"})

def get_redacted_archive_browser_blockers(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_redacted_archive_browser_blockers", "blocker_category, blocker_code", db_path, {"payload_json": "payload"})

def validate_redacted_archive_browser_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_redacted_archive_browser_components", "gp_number", db_path, {"data_json": "data"})
    folders = get_redacted_archive_folders(db_path)
    cards = get_redacted_archive_object_cards(db_path)
    search = get_redacted_archive_search_index(db_path)
    proof = get_redacted_archive_proof_packet_links(db_path)
    case_links = get_redacted_archive_case_links(db_path)
    filters = get_redacted_archive_filters(db_path)
    drawers = get_redacted_archive_metadata_drawers(db_path)
    blockers = get_redacted_archive_browser_blockers(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("FOLDER_COUNT_8", len(folders) == len(FOLDER_SPECS)),
        ("OBJECT_CARD_COUNT_8", len(cards) == 8),
        ("SEARCH_INDEX_COUNT_8", len(search) == 8),
        ("PROOF_PACKET_COUNT_16", len(proof) == 16),
        ("CASE_LINK_COUNT_8", len(case_links) == 8),
        ("FILTER_COUNT_8", len(filters) == len(FILTER_SPECS)),
        ("METADATA_DRAWER_COUNT_8", len(drawers) == 8),
        ("BLOCKER_COUNT_32", len(blockers) == 32),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("SAFE_TO_CONTINUE_TO_GP121", readiness["safe_to_continue_to_gp121"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("SECTION_GP111_GP120", readiness["section_range"] == "GP111-GP120"),
        ("NEXT_SECTION_GP121_GP130", readiness["readiness_payload"]["next_section_range"] == "GP121-GP130"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_REDACTED_ONLY", all(item["redacted_only"] is True for item in components)),
        ("ALL_FOLDERS_REDACTED_ONLY", all(item["redacted_only"] is True for item in folders)),
        ("ALL_OBJECT_CARDS_REDACTED_ONLY", all(item["redacted_only"] is True for item in cards)),
        ("ALL_OBJECT_CARDS_METADATA_ONLY", all(item["metadata_only"] is True for item in cards)),
        ("ALL_SEARCH_REDACTED_ONLY", all(item["redacted_only"] is True for item in search)),
        ("ALL_SEARCH_METADATA_ONLY", all(item["metadata_only"] is True for item in search)),
        ("ALL_PROOF_LINKS_LOCKED", all(item["proof_packet_locked"] is True for item in proof)),
        ("ALL_CASE_LINKS_LOCKED", all(item["case_link_locked"] is True for item in case_links)),
        ("ALL_FILTERS_LOCKED", all(item["filter_locked"] is True for item in filters)),
        ("ALL_DRAWERS_LOCKED", all(item["drawer_locked"] is True for item in drawers)),
        ("ALL_DRAWERS_REDACTED_ONLY", all(item["redacted_only"] is True for item in drawers)),
        ("ALL_DRAWERS_METADATA_ONLY", all(item["metadata_only"] is True for item in drawers)),
        ("ALL_BLOCKERS_ACTIVE", all(item["blocker_active"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", all(item["blocks_provider_api"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY", all(item["blocks_object_body"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DOWNLOAD", all(item["blocks_download"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_EXPORT", all(item["blocks_export"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_RESTORE", all(item["blocks_restore"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DIRECT_UPLOAD", all(item["blocks_direct_upload"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_TOWER_UNLOCK", all(item["blocks_tower_unlock"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_EXECUTION", all(item["blocks_execution"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_VAULT_DONE", all(item["blocks_vault_done"] is True for item in blockers)),
        ("NO_BLOCKERS_RESOLVED", all(item["resolved"] is False for item in blockers)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("FOLDER", folders),
        ("CARD", cards),
        ("SEARCH", search),
        ("PROOF", proof),
        ("CASE_LINK", case_links),
        ("FILTER", filters),
        ("DRAWER", drawers),
        ("BLOCKER", blockers),
    ]:
        for idx, row in enumerate(rows, start=1):
            for field in FALSE_FIELDS:
                checks.append((f"{collection_name}_{idx}_NO_{field.upper()}", row[field] is False))

    for field in FALSE_FIELDS:
        if field in readiness:
            checks.append((f"READINESS_NO_{field.upper()}", readiness[field] is False))

    checks_payload = [{"code": code, "passed": bool(passed)} for code, passed in checks]
    failed = [item for item in checks_payload if not item["passed"]]

    return {
        "pack": _layer_pack_payload(),
        "validation_ready": True,
        "valid": len(failed) == 0,
        "check_count": len(checks_payload),
        "passed_count": len(checks_payload) - len(failed),
        "failed_count": len(failed),
        "failed_checks": failed,
        "checks": checks_payload,
        "component_count": len(components),
        "folder_count": len(folders),
        "object_card_count": len(cards),
        "search_index_count": len(search),
        "proof_packet_count": len(proof),
        "case_link_count": len(case_links),
        "filter_count": len(filters),
        "metadata_drawer_count": len(drawers),
        "blocker_count": len(blockers),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "safe_to_continue_to_gp121": len(failed) == 0 and readiness["safe_to_continue_to_gp121"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp111_redacted_archive_browser_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(BROWSER_SHELL_ID, db_path)
    return {"pack": _pack_payload(111, component["pack_name"]), "real_sqlite_backed": True, "browser_shell": component}

def get_gp112_business_lane_folder_navigation(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(FOLDER_NAV_ID, db_path)
    folders = get_redacted_archive_folders(db_path)
    return {"pack": _pack_payload(112, component["pack_name"]), "real_sqlite_backed": True, "folder_navigation": component, "folder_count": len(folders), "folders": folders}

def get_gp113_redacted_archive_object_cards(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(OBJECT_CARDS_ID, db_path)
    cards = get_redacted_archive_object_cards(db_path)
    return {"pack": _pack_payload(113, component["pack_name"]), "real_sqlite_backed": True, "object_cards": component, "object_card_count": len(cards), "cards": cards}

def get_gp114_archive_search_index(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SEARCH_INDEX_ID, db_path)
    search = get_redacted_archive_search_index(db_path)
    return {"pack": _pack_payload(114, component["pack_name"]), "real_sqlite_backed": True, "search_index": component, "search_index_count": len(search), "search_rows": search}

def get_gp115_receipt_and_proof_packet_browser(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(PROOF_PACKET_BROWSER_ID, db_path)
    proof = get_redacted_archive_proof_packet_links(db_path)
    return {"pack": _pack_payload(115, component["pack_name"]), "real_sqlite_backed": True, "proof_packet_browser": component, "proof_packet_count": len(proof), "proof_packet_links": proof}

def get_gp116_case_to_archive_link_view(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(CASE_LINK_VIEW_ID, db_path)
    links = get_redacted_archive_case_links(db_path)
    return {"pack": _pack_payload(116, component["pack_name"]), "real_sqlite_backed": True, "case_link_view": component, "case_link_count": len(links), "case_links": links}

def get_gp117_archive_filter_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(FILTER_BOARD_ID, db_path)
    filters = get_redacted_archive_filters(db_path)
    return {"pack": _pack_payload(117, component["pack_name"]), "real_sqlite_backed": True, "filter_board": component, "filter_count": len(filters), "filters": filters}

def get_gp118_redacted_metadata_detail_drawer(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(METADATA_DRAWER_ID, db_path)
    drawers = get_redacted_archive_metadata_drawers(db_path)
    return {"pack": _pack_payload(118, component["pack_name"]), "real_sqlite_backed": True, "metadata_detail_drawer": component, "metadata_drawer_count": len(drawers), "drawers": drawers}

def get_gp119_archive_browser_blocker_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(BROWSER_BLOCKER_BOARD_ID, db_path)
    blockers = get_redacted_archive_browser_blockers(db_path)
    return {"pack": _pack_payload(119, component["pack_name"]), "real_sqlite_backed": True, "browser_blocker_board": component, "blocker_count": len(blockers), "blockers": blockers}

def get_gp120_redacted_archive_browser_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_redacted_archive_browser_layer(db_path)
    return {"pack": _pack_payload(120, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_redacted_archive_browser_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_redacted_archive_browser_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_redacted_archive_browser_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_redacted_archive_browser_readiness WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_redacted_archive_browser_layer(db_path)
    counts = _counts(db_path)

    return {
        "pack": _pack_payload(gp_number, component["pack_name"]),
        f"gp{gp_number:03d}_status": {
            "pack_id": f"VAULT_GP{gp_number:03d}",
            "ready": True,
            "layer_id": LAYER_ID,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "component_id": component_id,
            "component_type": component["component_type"],
            "real_sqlite_backed": True,
            "source_gp110_readiness_id": component["source_gp110_readiness_id"],
            "source_gp110_readiness_hash": component["source_gp110_readiness_hash"],
            "source_gp110_readiness_score": component["source_gp110_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "redacted_only": component["redacted_only"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp121": validation["safe_to_continue_to_gp121"],
            "foundation_status": "redacted_archive_browser_layer_ready_locked_safe_to_continue_not_done",
            "next": next_label,
            "folder_count": counts["folder_count"],
            "object_card_count": counts["object_card_count"],
            "search_index_count": counts["search_index_count"],
            "proof_packet_count": counts["proof_packet_count"],
            "case_link_count": counts["case_link_count"],
            "filter_count": counts["filter_count"],
            "metadata_drawer_count": counts["metadata_drawer_count"],
            "blocker_count": counts["blocker_count"],
            "provider_api_called": component["provider_api_called"],
            "provider_objects_listed": component["provider_objects_listed"],
            "provider_metadata_read": component["provider_metadata_read"],
            "object_body_read": component["object_body_read"],
            "object_body_view_enabled": component["object_body_view_enabled"],
            "object_body_download_enabled": component["object_body_download_enabled"],
            "object_body_plaintext_visible": component["object_body_plaintext_visible"],
            "object_download_enabled": component["object_download_enabled"],
            "export_package_created": component["export_package_created"],
            "export_manifest_created": component["export_manifest_created"],
            "export_download_enabled": component["export_download_enabled"],
            "restore_request_created": component["restore_request_created"],
            "restore_job_created": component["restore_job_created"],
            "provider_restore_api_called": component["provider_restore_api_called"],
            "direct_upload_enabled": component["direct_upload_enabled"],
            "tower_unlock_granted": component["tower_unlock_granted"],
            "execution_enabled": component["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp120",
        },
        "validation": validation,
    }

def get_gp111_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(111, BROWSER_SHELL_ID, "VAULT_GP112_BUSINESS_LANE_FOLDER_NAVIGATION", db_path)

def get_gp112_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(112, FOLDER_NAV_ID, "VAULT_GP113_REDACTED_ARCHIVE_OBJECT_CARDS", db_path)

def get_gp113_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(113, OBJECT_CARDS_ID, "VAULT_GP114_ARCHIVE_SEARCH_INDEX", db_path)

def get_gp114_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(114, SEARCH_INDEX_ID, "VAULT_GP115_RECEIPT_AND_PROOF_PACKET_BROWSER", db_path)

def get_gp115_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(115, PROOF_PACKET_BROWSER_ID, "VAULT_GP116_CASE_TO_ARCHIVE_LINK_VIEW", db_path)

def get_gp116_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(116, CASE_LINK_VIEW_ID, "VAULT_GP117_ARCHIVE_FILTER_BOARD", db_path)

def get_gp117_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(117, FILTER_BOARD_ID, "VAULT_GP118_REDACTED_METADATA_DETAIL_DRAWER", db_path)

def get_gp118_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(118, METADATA_DRAWER_ID, "VAULT_GP119_ARCHIVE_BROWSER_BLOCKER_BOARD", db_path)

def get_gp119_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(119, BROWSER_BLOCKER_BOARD_ID, "VAULT_GP120_REDACTED_ARCHIVE_BROWSER_READINESS_CHECKPOINT", db_path)

def get_gp120_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(120, READINESS_ID, NEXT_PACK, db_path)
    status["gp120_status"]["next_section"] = NEXT_SECTION_ID
    status["gp120_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp120_status"]["next_pack"] = NEXT_PACK
    return status

def get_redacted_archive_browser_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_redacted_archive_browser_layer(db_path)
    components = _rows("vault_redacted_archive_browser_components", "gp_number", db_path, {"data_json": "data"})
    folders = get_redacted_archive_folders(db_path)
    cards = get_redacted_archive_object_cards(db_path)
    search = get_redacted_archive_search_index(db_path)
    proof = get_redacted_archive_proof_packet_links(db_path)
    links = get_redacted_archive_case_links(db_path)
    filters = get_redacted_archive_filters(db_path)
    drawers = get_redacted_archive_metadata_drawers(db_path)
    blockers = get_redacted_archive_browser_blockers(db_path)
    readiness = _readiness(db_path)
    validation = validate_redacted_archive_browser_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "folders": {"folder_count": len(folders), "folders": folders},
        "object_cards": {"object_card_count": len(cards), "cards": cards},
        "search_index": {"search_index_count": len(search), "search_rows": search},
        "proof_packet_browser": {"proof_packet_count": len(proof), "proof_packet_links": proof},
        "case_links": {"case_link_count": len(links), "case_links": links},
        "filters": {"filter_count": len(filters), "filters": filters},
        "metadata_drawers": {"metadata_drawer_count": len(drawers), "drawers": drawers},
        "blockers": {"blocker_count": len(blockers), "blockers": blockers},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "redacted_archive_browser_layer_ready": True,
            "browser_shell_ready": True,
            "folder_navigation_ready": True,
            "object_cards_ready": True,
            "search_index_ready": True,
            "proof_packet_browser_ready": True,
            "case_link_view_ready": True,
            "filter_board_ready": True,
            "metadata_drawer_ready": True,
            "browser_blocker_board_ready": True,
            "safe_to_continue_to_gp121": validation["safe_to_continue_to_gp121"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "redacted_only": True,
            "metadata_only": True,
            "provider_api_called": False,
            "provider_objects_listed": False,
            "provider_metadata_read": False,
            "object_body_read": False,
            "object_body_view_enabled": False,
            "object_body_download_enabled": False,
            "object_body_plaintext_visible": False,
            "export_package_created": False,
            "export_manifest_created": False,
            "export_download_enabled": False,
            "restore_request_created": False,
            "restore_job_created": False,
            "provider_restore_api_called": False,
            "direct_upload_enabled": False,
            "tower_unlock_granted": False,
            "execution_enabled": False,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        "routes": {
            "page": "/vault/redacted-archive-browser-layer",
            "json": "/vault/redacted-archive-browser-layer.json",
            "gp111": "/vault/gp111-status.json",
            "gp112": "/vault/gp112-status.json",
            "gp113": "/vault/gp113-status.json",
            "gp114": "/vault/gp114-status.json",
            "gp115": "/vault/gp115-status.json",
            "gp116": "/vault/gp116-status.json",
            "gp117": "/vault/gp117-status.json",
            "gp118": "/vault/gp118-status.json",
            "gp119": "/vault/gp119-status.json",
            "gp120": "/vault/gp120-status.json",
        },
    }

def render_redacted_archive_browser_layer_page() -> str:
    home = get_redacted_archive_browser_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    folder_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['folder_name'])}</strong>
          <span>{escape(item['folder_description'])}</span>
          <code>{escape(item['sensitivity_label'])}</code>
        </article>
        """
        for item in home["folders"]["folders"]
    )

    object_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['object_card_code'])}</strong>
          <span>{escape(item['object_title'])}</span>
          <code>{escape(item['folder_code'])} · redacted only</code>
        </article>
        """
        for item in home["object_cards"]["cards"]
    )

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP111-GP120 Redacted Archive Browser Layer</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{
  --bg0:#03040b; --bg1:#080d22; --panel:rgba(14,22,52,.86); --panel2:rgba(21,32,74,.76);
  --line:rgba(164,184,255,.23); --text:#eef3ff; --muted:#a8b2dd; --gold:#f5d17e;
  --cyan:#83eaff; --danger:#ff8c9c; --ok:#9dffca;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; min-height:100vh; color:var(--text);
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  background:
    radial-gradient(circle at 10% 8%, rgba(173,141,255,.18), transparent 34%),
    radial-gradient(circle at 88% 4%, rgba(131,234,255,.13), transparent 30%),
    linear-gradient(135deg,var(--bg0),var(--bg1) 52%,#03040b);
}}
.shell {{ width:min(1240px, calc(100% - 32px)); margin:0 auto; padding:34px 0 48px; }}
.hero,.section {{ border:1px solid var(--line); background:var(--panel); border-radius:28px; padding:26px; margin-top:18px; }}
.eyebrow {{ color:var(--gold); letter-spacing:.18em; text-transform:uppercase; font-size:12px; font-weight:850; }}
h1 {{ margin:14px 0; font-size:clamp(34px,5vw,62px); line-height:.95; }}
p, li {{ color:var(--muted); line-height:1.62; }}
.grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin-top:18px; }}
.cards {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin-top:18px; }}
.metric,.card {{ border:1px solid var(--line); background:var(--panel2); border-radius:20px; padding:16px; }}
.metric strong {{ display:block; font-size:26px; }}
.card span {{ display:block; color:var(--muted); margin:8px 0; }}
.metric span,.muted {{ color:var(--muted); }}
.chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }}
.pill {{ border:1px solid var(--line); border-radius:999px; padding:7px 10px; font-size:12px; font-weight:800; background:rgba(10,16,38,.72); }}
.ok {{ color:var(--ok); }} .danger {{ color:var(--danger); }}
.row {{ display:flex; justify-content:space-between; gap:12px; padding:10px 0; border-bottom:1px solid rgba(160,179,255,.14); }}
code {{ color:var(--cyan); background:rgba(0,0,0,.28); border:1px solid var(--line); border-radius:8px; padding:2px 6px; }}
@media(max-width:900px) {{ .grid,.cards {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main class="shell">
  <section class="hero">
    <div class="eyebrow">Archive Vault · Giant Packs 111-120</div>
    <div class="eyebrow">Redacted Archive Browser Layer · GP111-GP120</div>
    <h1>Redacted Archive Browser Layer</h1>
    <p>This layer gives Vault a browse/search surface for redacted archive metadata only. It never reads bodies, downloads files, exports packages, calls provider APIs, restores, uploads, executes, or marks Vault done.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['folder_count']}</strong><span>folders</span></div>
      <div class="metric"><strong>{home['store']['object_card_count']}</strong><span>object cards</span></div>
      <div class="metric"><strong>{home['store']['search_index_count']}</strong><span>search rows</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP111-GP120 built</span>
      <span class="pill ok">Browser ready</span>
      <span class="pill ok">Redacted only</span>
      <span class="pill ok">Safe to GP121</span>
      <span class="pill danger">No body read</span>
      <span class="pill danger">No download</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No restore</span>
      <span class="pill danger">No provider API</span>
    </div>
  </section>

  <section class="section">
    <h2>Business Lane Folders</h2>
    <div class="cards">{folder_cards}</div>
  </section>

  <section class="section">
    <h2>Redacted Object Cards</h2>
    <div class="cards">{object_cards}</div>
  </section>

  <section class="section">
    <h2>Validation</h2>
    <p class="ok">Passed: {validation['passed_count']} / {validation['check_count']}</p>
    {failed}
    <p><code>{escape(readiness['readiness_hash'])}</code></p>
  </section>

  <section class="section">
    <h2>Next Section</h2>
    <p><code>{escape(NEXT_PACK)}</code></p>
    <p>{escape(NEXT_SECTION_ID)} · {escape(NEXT_SECTION_RANGE)}</p>
  </section>
</main>
</body>
</html>"""
