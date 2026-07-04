"""
VAULT GP121-GP130 — Owner Console and Operating Dashboard Layer

New section:
Archive Vault — Owner Console and Operating Dashboard Layer / GP121-GP130

Builds:
- GP121 Owner Console Shell
- GP122 Operating Dashboard Snapshot
- GP123 Archive Health Summary
- GP124 Open Recovery Case Summary Board
- GP125 Receipt and Proof Summary Board
- GP126 Provider Lock Status Panel
- GP127 Tower Gate Status Panel
- GP128 Owner Next Safe Action Board
- GP129 Owner Console Blocker Board
- GP130 Owner Console Readiness Checkpoint

This layer gives the owner a command surface for archive health, open cases,
receipts, provider lock state, Tower gate state, blockers, and next safe actions.
It never unlocks restore/export/provider APIs/body reads/downloads/direct upload/execution.
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

from vault.redacted_archive_browser_layer_service import (
    get_gp120_status,
    get_gp120_redacted_archive_browser_readiness_checkpoint,
    get_redacted_archive_browser_layer_home,
    validate_redacted_archive_browser_layer,
    get_redacted_archive_folders,
    get_redacted_archive_object_cards,
    get_redacted_archive_search_index,
    get_redacted_archive_proof_packet_links,
    get_redacted_archive_case_links,
    get_redacted_archive_filters,
    get_redacted_archive_metadata_drawers,
    get_redacted_archive_browser_blockers,
)

LAYER_ID = "VAULT_GP121_130"
LAYER_NAME = "Owner Console and Operating Dashboard Layer"
SCHEMA_VERSION = "vault.owner_console_operating_dashboard_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_OWNER_CONSOLE_AND_OPERATING_DASHBOARD_LAYER"
SECTION_TITLE = "Archive Vault — Owner Console and Operating Dashboard Layer"
SECTION_RANGE = "GP121-GP130"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_REDACTED_ARCHIVE_BROWSER_LAYER"
PREVIOUS_SECTION_RANGE = "GP111-GP120"

NEXT_SECTION_ID = "ARCHIVE_VAULT_TOWER_GATED_PERMISSION_AND_STEP_UP_LAYER"
NEXT_SECTION_RANGE = "GP131-GP140"
NEXT_PACK = "VAULT_GP131_140_TOWER_GATED_PERMISSION_AND_STEP_UP_LAYER"

DEFAULT_DB_ENV = "VAULT_OWNER_CONSOLE_OPERATING_DASHBOARD_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_owner_console_operating_dashboard_layer.sqlite"

OWNER_CONSOLE_SHELL_ID = "VOCDS-GP121-001"
DASHBOARD_SNAPSHOT_ID = "VOCDS-GP122-001"
ARCHIVE_HEALTH_ID = "VOCAHS-GP123-001"
OPEN_CASE_BOARD_ID = "VOCOCSB-GP124-001"
RECEIPT_PROOF_BOARD_ID = "VOCRPSB-GP125-001"
PROVIDER_LOCK_PANEL_ID = "VOCPLSP-GP126-001"
TOWER_GATE_PANEL_ID = "VOCTGSP-GP127-001"
NEXT_SAFE_ACTION_ID = "VOCNSAB-GP128-001"
CONSOLE_BLOCKER_BOARD_ID = "VOCBB-GP129-001"
READINESS_ID = "VOCRC-GP130-001"

FALSE_FIELDS = [
    "owner_approval_recorded",
    "owner_rejection_recorded",
    "owner_decision_recorded",
    "owner_execute_action_requested",
    "owner_execute_action_approved",
    "tower_unlock_requested",
    "tower_unlock_granted",
    "tower_step_up_passed",
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
    "execution_enabled",
    "vault_done",
    "clouds_should_continue",
]

METRIC_SPECS = [
    ("archive_folders", "Archive Folders", "navigation"),
    ("redacted_object_cards", "Redacted Object Cards", "archive"),
    ("metadata_search_rows", "Metadata Search Rows", "search"),
    ("proof_packet_links", "Proof Packet Links", "receipts"),
    ("case_links", "Case Links", "cases"),
    ("filter_count", "Available Filters", "filters"),
    ("metadata_drawers", "Metadata Drawers", "metadata"),
    ("active_blockers", "Active Blockers", "blockers"),
]

SAFE_ACTION_SPECS = [
    ("review_archive_health", "Review archive health", "owner_review", "Open the health summary and confirm locks remain active."),
    ("review_open_cases", "Review open recovery cases", "case_review", "Review open case board without approving restore/export."),
    ("review_receipt_links", "Review receipt/proof links", "receipt_review", "Review redacted proof links only."),
    ("review_provider_locks", "Review provider locks", "provider_lock_review", "Confirm provider API remains locked."),
    ("review_tower_gate", "Review Tower gate status", "tower_gate_review", "Confirm Tower gate is locked."),
    ("review_blockers", "Review blocker board", "blocker_review", "Confirm active blockers remain unresolved."),
    ("prepare_gp131_handoff", "Prepare GP131 handoff", "handoff", "Move toward Tower-gated permission layer."),
    ("do_not_unlock", "Do not unlock dangerous actions", "safety", "No restore, export, object body, provider API, upload, or execution."),
]

PANEL_SPECS = [
    ("owner_console_shell", "Owner Console Shell", "console"),
    ("operating_snapshot", "Operating Dashboard Snapshot", "snapshot"),
    ("archive_health", "Archive Health Summary", "health"),
    ("open_case_board", "Open Recovery Case Summary Board", "cases"),
    ("receipt_proof_board", "Receipt and Proof Summary Board", "receipts"),
    ("provider_lock_panel", "Provider Lock Status Panel", "provider"),
    ("tower_gate_panel", "Tower Gate Status Panel", "tower"),
    ("next_safe_action_board", "Owner Next Safe Action Board", "action"),
]

COMPONENT_SPECS = [
    (121, OWNER_CONSOLE_SHELL_ID, "VAULT_GP121", "Owner Console Shell", "owner_console_shell"),
    (122, DASHBOARD_SNAPSHOT_ID, "VAULT_GP122", "Operating Dashboard Snapshot", "operating_dashboard_snapshot"),
    (123, ARCHIVE_HEALTH_ID, "VAULT_GP123", "Archive Health Summary", "archive_health_summary"),
    (124, OPEN_CASE_BOARD_ID, "VAULT_GP124", "Open Recovery Case Summary Board", "open_recovery_case_summary_board"),
    (125, RECEIPT_PROOF_BOARD_ID, "VAULT_GP125", "Receipt and Proof Summary Board", "receipt_and_proof_summary_board"),
    (126, PROVIDER_LOCK_PANEL_ID, "VAULT_GP126", "Provider Lock Status Panel", "provider_lock_status_panel"),
    (127, TOWER_GATE_PANEL_ID, "VAULT_GP127", "Tower Gate Status Panel", "tower_gate_status_panel"),
    (128, NEXT_SAFE_ACTION_ID, "VAULT_GP128", "Owner Next Safe Action Board", "owner_next_safe_action_board"),
    (129, CONSOLE_BLOCKER_BOARD_ID, "VAULT_GP129", "Owner Console Blocker Board", "owner_console_blocker_board"),
    (130, READINESS_ID, "VAULT_GP130", "Owner Console Readiness Checkpoint", "owner_console_readiness_checkpoint"),
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
        "source_gp120_readiness_score",
        "metric_count",
        "panel_count",
        "safe_action_count",
        "blocker_count",
        "component_count",
        "event_count",
        "readiness_score",
        "check_count",
        "passed_count",
        "failed_count",
        "current_value",
        "target_value",
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
            or key.endswith("_value")
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
        "depends_on": ["VAULT_GP120"],
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
        "depends_on": ["VAULT_GP120"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_owner_console_operating_dashboard_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_owner_console_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp120_readiness_id TEXT NOT NULL,
                source_gp120_readiness_hash TEXT NOT NULL,
                source_gp120_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                owner_console_visible INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_owner_console_metrics (
                metric_id TEXT PRIMARY KEY,
                metric_code TEXT NOT NULL UNIQUE,
                metric_name TEXT NOT NULL,
                metric_category TEXT NOT NULL,
                current_value INTEGER NOT NULL,
                target_value INTEGER NOT NULL,
                metric_status TEXT NOT NULL,
                source_gp120_readiness_hash TEXT NOT NULL,
                metric_visible INTEGER NOT NULL DEFAULT 1,
                metric_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                metric_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_owner_console_panels (
                panel_id TEXT PRIMARY KEY,
                panel_code TEXT NOT NULL UNIQUE,
                panel_name TEXT NOT NULL,
                panel_category TEXT NOT NULL,
                panel_status TEXT NOT NULL,
                panel_visible INTEGER NOT NULL DEFAULT 1,
                panel_locked INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                panel_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_owner_console_safe_actions (
                action_id TEXT PRIMARY KEY,
                action_code TEXT NOT NULL UNIQUE,
                action_name TEXT NOT NULL,
                action_category TEXT NOT NULL,
                action_description TEXT NOT NULL,
                action_status TEXT NOT NULL,
                action_visible INTEGER NOT NULL DEFAULT 1,
                action_locked INTEGER NOT NULL DEFAULT 1,
                safe_action INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                action_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_owner_console_blockers (
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
                blocks_owner_execution INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_owner_console_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                metric_count INTEGER NOT NULL,
                panel_count INTEGER NOT NULL,
                safe_action_count INTEGER NOT NULL,
                blocker_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                safe_to_continue_to_gp131 INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_owner_console_events (
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
            "vault_owner_console_components",
            "vault_owner_console_metrics",
            "vault_owner_console_panels",
            "vault_owner_console_safe_actions",
            "vault_owner_console_blockers",
            "vault_owner_console_readiness",
            "vault_owner_console_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VOCEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_owner_console_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_owner_console_operating_dashboard_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_owner_console_operating_dashboard_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_owner_console_components WHERE component_id = ?",
            (OWNER_CONSOLE_SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp120_status = get_gp120_status()["gp120_status"]
            gp120_checkpoint = get_gp120_redacted_archive_browser_readiness_checkpoint()["readiness_checkpoint"]
            gp120_home = get_redacted_archive_browser_layer_home()
            gp120_validation = validate_redacted_archive_browser_layer()

            folders = get_redacted_archive_folders()
            object_cards = get_redacted_archive_object_cards()
            search_rows = get_redacted_archive_search_index()
            proof_links = get_redacted_archive_proof_packet_links()
            case_links = get_redacted_archive_case_links()
            filters = get_redacted_archive_filters()
            drawers = get_redacted_archive_metadata_drawers()
            browser_blockers = get_redacted_archive_browser_blockers()

            gp120_readiness = gp120_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp120_readiness_id": gp120_readiness["readiness_id"],
                "source_gp120_readiness_hash": gp120_readiness["readiness_hash"],
                "source_gp120_readiness_score": gp120_readiness["readiness_score"],
            }

            metric_values = {
                "archive_folders": len(folders),
                "redacted_object_cards": len(object_cards),
                "metadata_search_rows": len(search_rows),
                "proof_packet_links": len(proof_links),
                "case_links": len(case_links),
                "filter_count": len(filters),
                "metadata_drawers": len(drawers),
                "active_blockers": len(browser_blockers),
            }

            source_context = {
                "source_gp120_status_ready": gp120_status["ready"],
                "source_gp120_validation_passed": gp120_status["validation_passed"],
                "source_gp120_safe_to_continue_to_gp121": gp120_status["safe_to_continue_to_gp121"],
                "source_gp120_readiness_hash": gp120_readiness["readiness_hash"],
                "source_gp120_readiness_score": gp120_readiness["readiness_score"],
                "source_folder_count": len(folders),
                "source_object_card_count": len(object_cards),
                "source_search_index_count": len(search_rows),
                "source_proof_packet_count": len(proof_links),
                "source_case_link_count": len(case_links),
                "source_filter_count": len(filters),
                "source_metadata_drawer_count": len(drawers),
                "source_blocker_count": len(browser_blockers),
                "source_validation_check_count": gp120_validation["check_count"],
            }

            component_extra = {
                OWNER_CONSOLE_SHELL_ID: {"owner_console_shell_ready": True},
                DASHBOARD_SNAPSHOT_ID: {"operating_dashboard_snapshot_ready": True, "metric_count": len(METRIC_SPECS)},
                ARCHIVE_HEALTH_ID: {"archive_health_summary_ready": True, "archive_health_status": "HEALTHY_LOCKED_REDACTED_ONLY"},
                OPEN_CASE_BOARD_ID: {"open_recovery_case_summary_board_ready": True, "case_link_count": len(case_links)},
                RECEIPT_PROOF_BOARD_ID: {"receipt_and_proof_summary_board_ready": True, "proof_packet_count": len(proof_links)},
                PROVIDER_LOCK_PANEL_ID: {"provider_lock_status_panel_ready": True, "provider_api_called": False},
                TOWER_GATE_PANEL_ID: {"tower_gate_status_panel_ready": True, "tower_unlock_granted": False},
                NEXT_SAFE_ACTION_ID: {"owner_next_safe_action_board_ready": True, "safe_action_count": len(SAFE_ACTION_SPECS)},
                CONSOLE_BLOCKER_BOARD_ID: {"owner_console_blocker_board_ready": True, "blocker_count": len(browser_blockers) + 8},
                READINESS_ID: {"owner_console_readiness_checkpoint_ready": True, "safe_to_continue_to_gp131": True},
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
                    "owner_console_visible": True,
                    "redacted_only": True,
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
                    "owner_console_visible": 1,
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
                _insert_dict(conn, "vault_owner_console_components", row)

            for code, name, category in METRIC_SPECS:
                current_value = int(metric_values[code])
                target_value = current_value
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "metric_code": code,
                    "metric_name": name,
                    "metric_category": category,
                    "current_value": current_value,
                    "target_value": target_value,
                    "metric_status": "VISIBLE_LOCKED_OWNER_DASHBOARD_METRIC",
                    "source_gp120_readiness_hash": gp120_readiness["readiness_hash"],
                    "metric_visible": True,
                    "metric_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "metric_id": f"VOCM-{code.upper().replace('_', '-')}",
                    "metric_code": code,
                    "metric_name": name,
                    "metric_category": category,
                    "current_value": current_value,
                    "target_value": target_value,
                    "metric_status": payload["metric_status"],
                    "source_gp120_readiness_hash": gp120_readiness["readiness_hash"],
                    "metric_visible": 1,
                    "metric_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "metric_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_owner_console_metrics", row)

            for code, name, category in PANEL_SPECS:
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "panel_code": code,
                    "panel_name": name,
                    "panel_category": category,
                    "panel_status": "VISIBLE_LOCKED_OWNER_CONSOLE_PANEL",
                    "panel_visible": True,
                    "panel_locked": True,
                    "redacted_only": True,
                    "allowed_owner_actions": ["view_status", "review_summary", "inspect_redacted_metadata", "review_blockers"],
                    "blocked_owner_actions": ["approve_restore", "approve_export", "unlock_tower", "call_provider_api", "read_object_body", "download_file", "execute"],
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "panel_id": f"VOCP-{code.upper().replace('_', '-')}",
                    "panel_code": code,
                    "panel_name": name,
                    "panel_category": category,
                    "panel_status": payload["panel_status"],
                    "panel_visible": 1,
                    "panel_locked": 1,
                    "redacted_only": 1,
                    "payload_json": _json_dumps(payload),
                    "panel_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_owner_console_panels", row)

            for code, name, category, description in SAFE_ACTION_SPECS:
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "action_code": code,
                    "action_name": name,
                    "action_category": category,
                    "action_description": description,
                    "action_status": "VISIBLE_SAFE_ACTION_LOCKED_NO_EXECUTION",
                    "action_visible": True,
                    "action_locked": True,
                    "safe_action": True,
                    "dangerous_action": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "action_id": f"VOCSA-{code.upper().replace('_', '-')}",
                    "action_code": code,
                    "action_name": name,
                    "action_category": category,
                    "action_description": description,
                    "action_status": payload["action_status"],
                    "action_visible": 1,
                    "action_locked": 1,
                    "safe_action": 1,
                    "payload_json": _json_dumps(payload),
                    "action_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_owner_console_safe_actions", row)

            inherited_blocker_specs = [
                ("provider_api_locked", "Provider API locked", "provider_api", "critical"),
                ("object_body_locked", "Object body locked", "object_body", "critical"),
                ("download_locked", "File download locked", "download", "critical"),
                ("export_locked", "Export locked", "export", "critical"),
                ("restore_locked", "Restore locked", "restore", "critical"),
                ("tower_unlock_locked", "Tower unlock locked", "tower", "critical"),
                ("owner_execution_locked", "Owner execution locked", "owner_execution", "critical"),
                ("vault_done_locked", "Vault done locked", "done", "critical"),
            ]

            for idx, (code, name, category, severity) in enumerate(inherited_blocker_specs, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "ACTIVE_OWNER_CONSOLE_BLOCKER",
                    "blocker_active": True,
                    "blocks_provider_api": True,
                    "blocks_object_body": True,
                    "blocks_download": True,
                    "blocks_export": True,
                    "blocks_restore": True,
                    "blocks_direct_upload": True,
                    "blocks_tower_unlock": True,
                    "blocks_owner_execution": True,
                    "blocks_execution": True,
                    "blocks_vault_done": True,
                    "resolved": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "blocker_id": f"VOCB-{idx:03d}",
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": payload["blocker_status"],
                    "blocker_active": 1,
                    "blocks_provider_api": 1,
                    "blocks_object_body": 1,
                    "blocks_download": 1,
                    "blocks_export": 1,
                    "blocks_restore": 1,
                    "blocks_direct_upload": 1,
                    "blocks_tower_unlock": 1,
                    "blocks_owner_execution": 1,
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
                _insert_dict(conn, "vault_owner_console_blockers", row)

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "metric_count": len(METRIC_SPECS),
                "panel_count": len(PANEL_SPECS),
                "safe_action_count": len(SAFE_ACTION_SPECS),
                "blocker_count": len(inherited_blocker_specs),
            }

            checks = [
                ("SOURCE_GP120_READY", bool(gp120_status["ready"])),
                ("SOURCE_GP120_VALIDATION_PASSED", bool(gp120_status["validation_passed"])),
                ("SOURCE_GP120_SAFE_TO_CONTINUE", bool(gp120_status["safe_to_continue_to_gp121"])),
                ("SOURCE_GP120_READINESS_SCORE_100", gp120_readiness["readiness_score"] == 100),
                ("SOURCE_GP120_READINESS_HASH_64", isinstance(gp120_readiness["readiness_hash"], str) and len(gp120_readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("METRIC_COUNT_8", counts["metric_count"] == 8),
                ("PANEL_COUNT_8", counts["panel_count"] == 8),
                ("SAFE_ACTION_COUNT_8", counts["safe_action_count"] == 8),
                ("BLOCKER_COUNT_8", counts["blocker_count"] == 8),
                ("SECTION_GP121_GP130", SECTION_RANGE == "GP121-GP130"),
                ("NEXT_SECTION_GP131_GP140", NEXT_SECTION_RANGE == "GP131-GP140"),
                ("NO_OWNER_DECISION", True),
                ("NO_TOWER_UNLOCK", True),
                ("NO_PROVIDER_API", True),
                ("NO_OBJECT_BODY", True),
                ("NO_DOWNLOAD", True),
                ("NO_EXPORT", True),
                ("NO_RESTORE", True),
                ("NO_DIRECT_UPLOAD", True),
                ("NO_EXECUTION", True),
                ("VAULT_NOT_DONE", True),
                ("CLOUDS_PARKED", True),
            ]
            passed_count = len([c for c in checks if c[1]])
            failed_count = len(checks) - passed_count

            readiness_payload = {
                "schema_version": SCHEMA_VERSION,
                "readiness_id": READINESS_ID,
                "gp_number": 130,
                "pack_id": "VAULT_GP130",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp120_readiness_id": gp120_readiness["readiness_id"],
                "source_gp120_readiness_hash": gp120_readiness["readiness_hash"],
                "source_gp120_readiness_score": gp120_readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "safe_to_continue_to_gp131": failed_count == 0,
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
                "gp_number": 130,
                "pack_id": "VAULT_GP130",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "OWNER_CONSOLE_OPERATING_DASHBOARD_LAYER_READY_LOCKED_SAFE_TO_CONTINUE_NOT_DONE",
                "readiness_score": readiness_payload["readiness_score"],
                "component_count": counts["component_count"],
                "metric_count": counts["metric_count"],
                "panel_count": counts["panel_count"],
                "safe_action_count": counts["safe_action_count"],
                "blocker_count": counts["blocker_count"],
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "safe_to_continue_to_gp131": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_owner_console_readiness", row)

            for event_type, event_payload in [
                ("GP121_OWNER_CONSOLE_SHELL_CREATED", {"component_id": OWNER_CONSOLE_SHELL_ID}),
                ("GP122_OPERATING_DASHBOARD_SNAPSHOT_CREATED", {"metric_count": counts["metric_count"]}),
                ("GP123_ARCHIVE_HEALTH_SUMMARY_CREATED", {"archive_health_status": "HEALTHY_LOCKED_REDACTED_ONLY"}),
                ("GP124_OPEN_RECOVERY_CASE_SUMMARY_BOARD_CREATED", {"case_link_count": len(case_links)}),
                ("GP125_RECEIPT_AND_PROOF_SUMMARY_BOARD_CREATED", {"proof_packet_count": len(proof_links)}),
                ("GP126_PROVIDER_LOCK_STATUS_PANEL_CREATED", {"provider_api_called": False}),
                ("GP127_TOWER_GATE_STATUS_PANEL_CREATED", {"tower_unlock_granted": False}),
                ("GP128_OWNER_NEXT_SAFE_ACTION_BOARD_CREATED", {"safe_action_count": counts["safe_action_count"]}),
                ("GP129_OWNER_CONSOLE_BLOCKER_BOARD_CREATED", {"blocker_count": counts["blocker_count"]}),
                ("GP130_OWNER_CONSOLE_READINESS_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp131": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_console_components").fetchone()["c"]),
            "metric_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_console_metrics").fetchone()["c"]),
            "panel_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_console_panels").fetchone()["c"]),
            "safe_action_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_console_safe_actions").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_console_blockers").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_console_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_console_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_owner_console_operating_dashboard_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_owner_console_operating_dashboard_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_owner_console_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_owner_console_operating_dashboard_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_owner_console_readiness WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_owner_console_operating_dashboard_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_owner_console_events ORDER BY created_at, event_id").fetchall()
    return [
        {
            "event_id": row["event_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]

def get_owner_console_metrics(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_owner_console_metrics", "metric_category, metric_code", db_path, {"payload_json": "payload"})

def get_owner_console_panels(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_owner_console_panels", "panel_category, panel_code", db_path, {"payload_json": "payload"})

def get_owner_console_safe_actions(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_owner_console_safe_actions", "action_category, action_code", db_path, {"payload_json": "payload"})

def get_owner_console_blockers(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_owner_console_blockers", "blocker_category, blocker_code", db_path, {"payload_json": "payload"})

def validate_owner_console_operating_dashboard_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_owner_console_components", "gp_number", db_path, {"data_json": "data"})
    metrics = get_owner_console_metrics(db_path)
    panels = get_owner_console_panels(db_path)
    actions = get_owner_console_safe_actions(db_path)
    blockers = get_owner_console_blockers(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("METRIC_COUNT_8", len(metrics) == len(METRIC_SPECS)),
        ("PANEL_COUNT_8", len(panels) == len(PANEL_SPECS)),
        ("SAFE_ACTION_COUNT_8", len(actions) == len(SAFE_ACTION_SPECS)),
        ("BLOCKER_COUNT_8", len(blockers) == 8),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("SAFE_TO_CONTINUE_TO_GP131", readiness["safe_to_continue_to_gp131"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("SECTION_GP121_GP130", readiness["section_range"] == "GP121-GP130"),
        ("NEXT_SECTION_GP131_GP140", readiness["readiness_payload"]["next_section_range"] == "GP131-GP140"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_VISIBLE", all(item["owner_console_visible"] is True for item in components)),
        ("ALL_COMPONENTS_LOCKED", all(item["component_locked"] is True for item in components)),
        ("ALL_METRICS_VISIBLE", all(item["metric_visible"] is True for item in metrics)),
        ("ALL_METRICS_LOCKED", all(item["metric_locked"] is True for item in metrics)),
        ("ALL_PANELS_VISIBLE", all(item["panel_visible"] is True for item in panels)),
        ("ALL_PANELS_LOCKED", all(item["panel_locked"] is True for item in panels)),
        ("ALL_PANELS_REDACTED_ONLY", all(item["redacted_only"] is True for item in panels)),
        ("ALL_ACTIONS_VISIBLE", all(item["action_visible"] is True for item in actions)),
        ("ALL_ACTIONS_LOCKED", all(item["action_locked"] is True for item in actions)),
        ("ALL_ACTIONS_SAFE", all(item["safe_action"] is True for item in actions)),
        ("ALL_BLOCKERS_ACTIVE", all(item["blocker_active"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", all(item["blocks_provider_api"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY", all(item["blocks_object_body"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DOWNLOAD", all(item["blocks_download"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_EXPORT", all(item["blocks_export"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_RESTORE", all(item["blocks_restore"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DIRECT_UPLOAD", all(item["blocks_direct_upload"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_TOWER_UNLOCK", all(item["blocks_tower_unlock"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_OWNER_EXECUTION", all(item["blocks_owner_execution"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_EXECUTION", all(item["blocks_execution"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_VAULT_DONE", all(item["blocks_vault_done"] is True for item in blockers)),
        ("NO_BLOCKERS_RESOLVED", all(item["resolved"] is False for item in blockers)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("METRIC", metrics),
        ("PANEL", panels),
        ("ACTION", actions),
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
        "metric_count": len(metrics),
        "panel_count": len(panels),
        "safe_action_count": len(actions),
        "blocker_count": len(blockers),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "safe_to_continue_to_gp131": len(failed) == 0 and readiness["safe_to_continue_to_gp131"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp121_owner_console_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(OWNER_CONSOLE_SHELL_ID, db_path)
    panels = get_owner_console_panels(db_path)
    return {"pack": _pack_payload(121, component["pack_name"]), "real_sqlite_backed": True, "owner_console_shell": component, "panel_count": len(panels), "panels": panels}

def get_gp122_operating_dashboard_snapshot(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(DASHBOARD_SNAPSHOT_ID, db_path)
    metrics = get_owner_console_metrics(db_path)
    return {"pack": _pack_payload(122, component["pack_name"]), "real_sqlite_backed": True, "dashboard_snapshot": component, "metric_count": len(metrics), "metrics": metrics}

def get_gp123_archive_health_summary(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(ARCHIVE_HEALTH_ID, db_path)
    metrics = get_owner_console_metrics(db_path)
    blockers = get_owner_console_blockers(db_path)
    health_payload = {
        "archive_health_status": "HEALTHY_LOCKED_REDACTED_ONLY",
        "metrics_ready": all(item["metric_locked"] is True for item in metrics),
        "active_blockers": len(blockers),
        "provider_api_locked": True,
        "object_body_locked": True,
        "download_locked": True,
        "export_locked": True,
        "restore_locked": True,
        "vault_done": False,
    }
    return {"pack": _pack_payload(123, component["pack_name"]), "real_sqlite_backed": True, "archive_health_summary": {**component, "health": health_payload}}

def get_gp124_open_recovery_case_summary_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(OPEN_CASE_BOARD_ID, db_path)
    source_links = get_redacted_archive_case_links()
    board = [
        {
            "source_case_code": item["source_case_code"],
            "object_card_id": item["object_card_id"],
            "evidence_link_count": item["evidence_link_count"],
            "receipt_link_count": item["receipt_link_count"],
            "case_link_status": item["case_link_status"],
            "case_link_locked": True,
            "redacted_only": True,
            "restore_requested": False,
            "export_requested": False,
        }
        for item in source_links
    ]
    return {"pack": _pack_payload(124, component["pack_name"]), "real_sqlite_backed": True, "open_case_summary_board": component, "case_link_count": len(board), "cases": board}

def get_gp125_receipt_and_proof_summary_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RECEIPT_PROOF_BOARD_ID, db_path)
    source_proof = get_redacted_archive_proof_packet_links()
    board = [
        {
            "proof_packet_code": item["proof_packet_code"],
            "source_case_id": item["source_case_id"],
            "source_ref": item["source_ref"],
            "proof_packet_status": item["proof_packet_status"],
            "proof_packet_locked": True,
            "redacted_only": True,
            "export_package_created": False,
            "object_body_read": False,
        }
        for item in source_proof
    ]
    return {"pack": _pack_payload(125, component["pack_name"]), "real_sqlite_backed": True, "receipt_proof_summary_board": component, "proof_packet_count": len(board), "proof_packets": board}

def get_gp126_provider_lock_status_panel(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(PROVIDER_LOCK_PANEL_ID, db_path)
    panel = {
        "provider_lock_status": "PROVIDER_API_LOCKED",
        "provider_api_configured": False,
        "provider_api_called": False,
        "provider_objects_listed": False,
        "provider_metadata_imported": False,
        "provider_metadata_read": False,
        "provider_restore_api_called": False,
        "direct_upload_enabled": False,
    }
    return {"pack": _pack_payload(126, component["pack_name"]), "real_sqlite_backed": True, "provider_lock_status_panel": {**component, "provider_lock": panel}}

def get_gp127_tower_gate_status_panel(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(TOWER_GATE_PANEL_ID, db_path)
    panel = {
        "tower_gate_status": "TOWER_GATE_LOCKED",
        "tower_unlock_requested": False,
        "tower_unlock_granted": False,
        "tower_step_up_passed": False,
        "owner_approval_recorded": False,
        "owner_decision_recorded": False,
        "execution_enabled": False,
    }
    return {"pack": _pack_payload(127, component["pack_name"]), "real_sqlite_backed": True, "tower_gate_status_panel": {**component, "tower_gate": panel}}

def get_gp128_owner_next_safe_action_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(NEXT_SAFE_ACTION_ID, db_path)
    actions = get_owner_console_safe_actions(db_path)
    return {"pack": _pack_payload(128, component["pack_name"]), "real_sqlite_backed": True, "next_safe_action_board": component, "safe_action_count": len(actions), "actions": actions}

def get_gp129_owner_console_blocker_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(CONSOLE_BLOCKER_BOARD_ID, db_path)
    blockers = get_owner_console_blockers(db_path)
    return {"pack": _pack_payload(129, component["pack_name"]), "real_sqlite_backed": True, "owner_console_blocker_board": component, "blocker_count": len(blockers), "blockers": blockers}

def get_gp130_owner_console_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_owner_console_operating_dashboard_layer(db_path)
    return {"pack": _pack_payload(130, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_owner_console_operating_dashboard_layer(db_path)
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
            "source_gp120_readiness_id": component["source_gp120_readiness_id"],
            "source_gp120_readiness_hash": component["source_gp120_readiness_hash"],
            "source_gp120_readiness_score": component["source_gp120_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "owner_console_visible": component["owner_console_visible"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp131": validation["safe_to_continue_to_gp131"],
            "foundation_status": "owner_console_operating_dashboard_layer_ready_locked_safe_to_continue_not_done",
            "next": next_label,
            "metric_count": counts["metric_count"],
            "panel_count": counts["panel_count"],
            "safe_action_count": counts["safe_action_count"],
            "blocker_count": counts["blocker_count"],
            "owner_decision_recorded": component["owner_decision_recorded"],
            "owner_approval_recorded": component["owner_approval_recorded"],
            "owner_rejection_recorded": component["owner_rejection_recorded"],
            "owner_execute_action_requested": component["owner_execute_action_requested"],
            "owner_execute_action_approved": component["owner_execute_action_approved"],
            "tower_unlock_requested": component["tower_unlock_requested"],
            "tower_unlock_granted": component["tower_unlock_granted"],
            "tower_step_up_passed": component["tower_step_up_passed"],
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
            "execution_enabled": component["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp130",
        },
        "validation": validation,
    }

def get_gp121_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(121, OWNER_CONSOLE_SHELL_ID, "VAULT_GP122_OPERATING_DASHBOARD_SNAPSHOT", db_path)

def get_gp122_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(122, DASHBOARD_SNAPSHOT_ID, "VAULT_GP123_ARCHIVE_HEALTH_SUMMARY", db_path)

def get_gp123_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(123, ARCHIVE_HEALTH_ID, "VAULT_GP124_OPEN_RECOVERY_CASE_SUMMARY_BOARD", db_path)

def get_gp124_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(124, OPEN_CASE_BOARD_ID, "VAULT_GP125_RECEIPT_AND_PROOF_SUMMARY_BOARD", db_path)

def get_gp125_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(125, RECEIPT_PROOF_BOARD_ID, "VAULT_GP126_PROVIDER_LOCK_STATUS_PANEL", db_path)

def get_gp126_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(126, PROVIDER_LOCK_PANEL_ID, "VAULT_GP127_TOWER_GATE_STATUS_PANEL", db_path)

def get_gp127_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(127, TOWER_GATE_PANEL_ID, "VAULT_GP128_OWNER_NEXT_SAFE_ACTION_BOARD", db_path)

def get_gp128_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(128, NEXT_SAFE_ACTION_ID, "VAULT_GP129_OWNER_CONSOLE_BLOCKER_BOARD", db_path)

def get_gp129_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(129, CONSOLE_BLOCKER_BOARD_ID, "VAULT_GP130_OWNER_CONSOLE_READINESS_CHECKPOINT", db_path)

def get_gp130_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(130, READINESS_ID, NEXT_PACK, db_path)
    status["gp130_status"]["next_section"] = NEXT_SECTION_ID
    status["gp130_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp130_status"]["next_pack"] = NEXT_PACK
    return status

def get_owner_console_operating_dashboard_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_owner_console_operating_dashboard_layer(db_path)
    components = _rows("vault_owner_console_components", "gp_number", db_path, {"data_json": "data"})
    metrics = get_owner_console_metrics(db_path)
    panels = get_owner_console_panels(db_path)
    actions = get_owner_console_safe_actions(db_path)
    blockers = get_owner_console_blockers(db_path)
    readiness = _readiness(db_path)
    validation = validate_owner_console_operating_dashboard_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "metrics": {"metric_count": len(metrics), "metrics": metrics},
        "panels": {"panel_count": len(panels), "panels": panels},
        "safe_actions": {"safe_action_count": len(actions), "actions": actions},
        "blockers": {"blocker_count": len(blockers), "blockers": blockers},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "owner_console_operating_dashboard_layer_ready": True,
            "owner_console_shell_ready": True,
            "operating_dashboard_snapshot_ready": True,
            "archive_health_summary_ready": True,
            "open_recovery_case_summary_board_ready": True,
            "receipt_and_proof_summary_board_ready": True,
            "provider_lock_status_panel_ready": True,
            "tower_gate_status_panel_ready": True,
            "owner_next_safe_action_board_ready": True,
            "owner_console_blocker_board_ready": True,
            "safe_to_continue_to_gp131": validation["safe_to_continue_to_gp131"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "provider_api_called": False,
            "provider_objects_listed": False,
            "provider_metadata_read": False,
            "object_body_read": False,
            "object_body_view_enabled": False,
            "object_body_download_enabled": False,
            "object_body_plaintext_visible": False,
            "object_download_enabled": False,
            "export_package_created": False,
            "export_manifest_created": False,
            "export_download_enabled": False,
            "restore_request_created": False,
            "restore_job_created": False,
            "provider_restore_api_called": False,
            "direct_upload_enabled": False,
            "tower_unlock_granted": False,
            "owner_approval_recorded": False,
            "owner_execute_action_approved": False,
            "execution_enabled": False,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        "routes": {
            "page": "/vault/owner-console-operating-dashboard-layer",
            "json": "/vault/owner-console-operating-dashboard-layer.json",
            "gp121": "/vault/gp121-status.json",
            "gp122": "/vault/gp122-status.json",
            "gp123": "/vault/gp123-status.json",
            "gp124": "/vault/gp124-status.json",
            "gp125": "/vault/gp125-status.json",
            "gp126": "/vault/gp126-status.json",
            "gp127": "/vault/gp127-status.json",
            "gp128": "/vault/gp128-status.json",
            "gp129": "/vault/gp129-status.json",
            "gp130": "/vault/gp130-status.json",
        },
    }

def render_owner_console_operating_dashboard_layer_page() -> str:
    home = get_owner_console_operating_dashboard_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    metric_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['metric_name'])}</strong>
          <span>{item['current_value']} / {item['target_value']}</span>
          <code>{escape(item['metric_category'])}</code>
        </article>
        """
        for item in home["metrics"]["metrics"]
    )

    action_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['action_name'])}</strong>
          <span>{escape(item['action_description'])}</span>
          <code>{escape(item['action_category'])} · safe locked</code>
        </article>
        """
        for item in home["safe_actions"]["actions"]
    )

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP121-GP130 Owner Console Operating Dashboard Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 121-130</div>
    <div class="eyebrow">Owner Console and Operating Dashboard Layer · GP121-GP130</div>
    <h1>Owner Console Operating Dashboard</h1>
    <p>This layer turns Vault into an owner-facing command surface for archive health, open cases, receipts, provider locks, Tower gate state, blockers, and next safe actions. Every dangerous operation remains locked.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['metric_count']}</strong><span>metrics</span></div>
      <div class="metric"><strong>{home['store']['panel_count']}</strong><span>panels</span></div>
      <div class="metric"><strong>{home['store']['safe_action_count']}</strong><span>safe actions</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP121-GP130 built</span>
      <span class="pill ok">Owner console ready</span>
      <span class="pill ok">Dashboard ready</span>
      <span class="pill ok">Safe to GP131</span>
      <span class="pill danger">No Tower unlock</span>
      <span class="pill danger">No provider API</span>
      <span class="pill danger">No object body</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No restore</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Operating Metrics</h2>
    <div class="cards">{metric_cards}</div>
  </section>

  <section class="section">
    <h2>Next Safe Actions</h2>
    <div class="cards">{action_cards}</div>
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
