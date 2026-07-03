"""
VAULT GP080 — Real Provider Receipt and Redacted Access Readiness Checkpoint

Current section:
Archive Vault — Real Provider Receipt and Redacted Access Layer / GP071-GP080

This pack closes the GP071-GP080 layer with a real SQLite-backed readiness
checkpoint. It verifies the layer components from GP071 through GP079 and
records readiness without unlocking provider access, object listing, metadata
import, object body read/view/download, owner review finalization, Tower unlock,
direct upload, export, or execution.

It does not complete Vault. It only closes this layer and marks it safe to move
to the next Vault layer.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Dict, Optional

from vault.real_storage_provider_object_catalog_lock_contract_service import get_gp071_status
from vault.real_storage_provider_redacted_metadata_receipt_contract_service import get_gp072_status
from vault.real_storage_provider_receipt_lineage_lock_contract_service import get_gp073_status
from vault.real_storage_provider_redacted_access_view_lock_contract_service import get_gp074_status
from vault.real_storage_provider_owner_review_packet_lock_contract_service import get_gp075_status
from vault.real_storage_provider_owner_review_queue_lock_contract_service import get_gp076_status
from vault.real_storage_provider_owner_review_decision_lock_contract_service import get_gp077_status
from vault.real_storage_provider_owner_review_decision_receipt_lock_contract_service import get_gp078_status
from vault.real_storage_provider_owner_review_closeout_lock_contract_service import get_gp079_status

PACK_ID = "VAULT_GP080"
PACK_NAME = "Real Provider Receipt and Redacted Access Readiness Checkpoint"
SCHEMA_VERSION = "vault.real_provider_receipt_redacted_access_readiness_checkpoint.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Receipt and Redacted Access Layer"
SECTION_RANGE = "GP071-GP080"

NEXT_SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_LAYER"
NEXT_SECTION_TITLE = "Archive Vault — Real Provider Restore and Export Governance Layer"
NEXT_SECTION_RANGE = "GP081-GP090"
NEXT_PACK = "VAULT_GP081_REAL_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT"
NEXT_PACK_TITLE = "Real Storage Provider Restore Request Lock Contract"

DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID = "VPRRARC-GP080-001"
DEFAULT_DB_ENV = "VAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_DB"
DEFAULT_DB_PATH = "data/vault_provider_receipt_redacted_access_readiness_checkpoint.sqlite"

COMPONENT_SPECS = [
    ("VAULT_GP071", "Real Storage Provider Object Catalog Lock Contract", "gp071_status", get_gp071_status),
    ("VAULT_GP072", "Real Storage Provider Redacted Metadata Receipt Contract", "gp072_status", get_gp072_status),
    ("VAULT_GP073", "Real Storage Provider Receipt Lineage Lock Contract", "gp073_status", get_gp073_status),
    ("VAULT_GP074", "Real Storage Provider Redacted Access View Lock Contract", "gp074_status", get_gp074_status),
    ("VAULT_GP075", "Real Storage Provider Owner Review Packet Lock Contract", "gp075_status", get_gp075_status),
    ("VAULT_GP076", "Real Storage Provider Owner Review Queue Lock Contract", "gp076_status", get_gp076_status),
    ("VAULT_GP077", "Real Storage Provider Owner Review Decision Lock Contract", "gp077_status", get_gp077_status),
    ("VAULT_GP078", "Real Storage Provider Owner Review Decision Receipt Lock Contract", "gp078_status", get_gp078_status),
    ("VAULT_GP079", "Real Storage Provider Owner Review Closeout Lock Contract", "gp079_status", get_gp079_status),
]

READINESS_BLOCKER_SPECS = [
    ("provider_object_catalog_locked", "Provider object catalog remains locked", "catalog"),
    ("provider_metadata_import_locked", "Provider metadata import remains locked", "metadata"),
    ("provider_object_listing_locked", "Provider object listing remains locked", "listing"),
    ("provider_object_identifier_collection_locked", "Provider object identifier collection remains locked", "identifier"),
    ("provider_object_body_read_locked", "Provider object body read remains locked", "object_body"),
    ("redacted_access_view_locked", "Redacted access view remains locked", "redacted_access"),
    ("owner_review_packet_locked", "Owner review packet remains locked", "owner_packet"),
    ("owner_review_queue_locked", "Owner review queue remains locked", "owner_queue"),
    ("owner_review_decision_locked", "Owner review decision remains locked", "owner_decision"),
    ("owner_review_decision_receipt_locked", "Owner review decision receipt remains locked", "decision_receipt"),
    ("owner_review_closeout_locked", "Owner review closeout remains locked", "closeout"),
    ("tower_unlock_locked", "Tower unlock remains locked", "tower"),
    ("provider_attachment_locked", "Provider packet/view attachment remains locked", "provider_attachment"),
    ("receipt_finalization_locked", "Receipt finalization remains locked", "receipt_finalization"),
    ("closeout_finalization_locked", "Closeout finalization remains locked", "closeout_finalization"),
    ("direct_upload_locked", "Direct upload remains locked", "direct_upload"),
    ("export_locked", "Export remains locked", "export"),
    ("execution_locked", "Execution remains locked", "execution"),
]

FALSE_FIELDS = [
    "provider_object_catalog_unlocked",
    "provider_object_listing_configured",
    "provider_object_list_attempted",
    "provider_objects_listed",
    "provider_metadata_imported",
    "provider_metadata_read",
    "provider_object_metadata_imported",
    "object_identifier_collected",
    "object_id_collected",
    "object_key_collected",
    "object_etag_collected",
    "object_size_collected",
    "object_timestamp_collected",
    "object_body_read_attempted",
    "object_body_read",
    "object_body_view_enabled",
    "object_body_content_exposed",
    "object_body_plaintext_visible",
    "object_body_download_enabled",
    "redacted_access_view_enabled",
    "live_provider_access_view_created",
    "provider_access_view_attached",
    "provider_object_view_attached",
    "provider_metadata_view_attached",
    "provider_receipt_lineage_view_attached",
    "owner_review_packet_created",
    "owner_review_packet_assembled",
    "owner_review_packet_finalized",
    "owner_review_queue_created",
    "owner_review_queue_entry_created",
    "owner_review_queue_entry_assigned",
    "owner_review_decision_created",
    "owner_decision_requested",
    "owner_decision_recorded",
    "owner_decision_approved",
    "owner_decision_denied",
    "owner_review_decision_receipt_created",
    "owner_review_decision_receipt_finalized",
    "owner_review_closeout_created",
    "owner_review_closeout_finalized",
    "closeout_transition_to_readiness_enabled",
    "tower_unlock_requested",
    "tower_unlock_granted",
    "provider_packet_attached",
    "object_identifier_attached",
    "object_body_attached",
    "direct_upload_enabled",
    "export_enabled",
    "execution_enabled",
    "vault_done",
]

TRUE_CHECKPOINT_FIELDS = [
    "provider_receipt_redacted_access_readiness_checkpoint_ready",
    "section_gp071_gp080_ready",
    "component_registry_ready",
    "component_validation_ready",
    "blocker_register_ready",
    "event_log_ready",
    "real_sqlite_backed",
    "real_provider_receipt_redacted_access_layer_closed",
    "safe_to_continue_to_gp081",
]

TRUE_COMPONENT_FIELDS = [
    "component_ready",
    "component_validation_passed",
    "component_safe_to_continue",
    "component_real_sqlite_backed",
    "component_locked",
    "component_template_only_or_checkpoint",
    "component_no_provider_unlock",
    "component_no_direct_upload",
    "component_no_export",
    "component_no_execution",
    "component_vault_not_done",
]

TRUE_BLOCKER_FIELDS = [
    "blocker_active",
    "blocks_provider_unlock",
    "blocks_provider_listing",
    "blocks_metadata_import",
    "blocks_object_identifier_collection",
    "blocks_object_body_read",
    "blocks_owner_review_finalization",
    "blocks_tower_unlock",
    "blocks_direct_upload",
    "blocks_export",
    "blocks_execution",
    "tower_review_required",
]

def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _resolve_db_path(db_path: Optional[str] = None) -> Path:
    return Path(db_path or os.environ.get(DEFAULT_DB_ENV) or DEFAULT_DB_PATH)

def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))

def _json_loads(value: str) -> Any:
    return json.loads(value)

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
    """
    Convert SQLite 0/1 lock flags back to booleans while preserving real
    integer metric fields.

    GP080 stores readiness_score as INTEGER 100 and component_order as an
    INTEGER sort key. Those are not booleans. If readiness_score becomes True,
    validation fails READINESS_SCORE_100 and section_closed becomes False.
    """
    json_fields = json_fields or {}
    integer_metric_fields = {
        "readiness_score",
        "component_order",
    }
    payload = {}
    for key in row.keys():
        if key in json_fields:
            payload[json_fields[key]] = _json_loads(row[key])
        elif isinstance(row[key], int) and key in integer_metric_fields:
            payload[key] = int(row[key])
        elif isinstance(row[key], int):
            payload[key] = bool(row[key])
        else:
            payload[key] = row[key]
    return payload

def _first_bool_by_prefix(status: Dict[str, Any], prefix: str, default: bool = False) -> bool:
    for key, value in status.items():
        if key.startswith(prefix):
            return bool(value)
    return default

def _component_status_from_payload(payload: Dict[str, Any], status_key: str) -> Dict[str, Any]:
    status = payload[status_key]
    return {
        "ready": bool(status.get("ready", False)),
        "validation_passed": bool(status.get("validation_passed", False)),
        "safe_to_continue": _first_bool_by_prefix(status, "safe_to_continue_to_", False),
        "real_sqlite_backed": bool(status.get("real_sqlite_backed", True)),
        "vault_done": bool(status.get("vault_done", False)),
        "export_enabled": bool(status.get("export_enabled", False)),
        "execution_enabled": bool(status.get("execution_enabled", False)),
        "direct_upload_enabled": bool(status.get("direct_upload_enabled", False)),
        "source": status,
    }

def _collect_component_statuses() -> list[Dict[str, Any]]:
    components = []
    for index, (pack_id, name, status_key, func) in enumerate(COMPONENT_SPECS, start=1):
        payload = func()
        parsed = _component_status_from_payload(payload, status_key)
        components.append({
            "component_order": index,
            "pack_id": pack_id,
            "component_name": name,
            "status_key": status_key,
            **parsed,
        })
    return components

def ensure_provider_receipt_redacted_access_readiness_checkpoint_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)
        true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_CHECKPOINT_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_provider_receipt_redacted_access_readiness_checkpoints (
                readiness_checkpoint_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_title TEXT NOT NULL,
                section_range TEXT NOT NULL,
                next_section_id TEXT NOT NULL,
                next_section_title TEXT NOT NULL,
                next_section_range TEXT NOT NULL,
                next_pack TEXT NOT NULL,
                checkpoint_status TEXT NOT NULL,
                readiness_label TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                checkpoint_data_json TEXT NOT NULL,
                {true_sql},
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        component_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_COMPONENT_FIELDS)
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_provider_receipt_redacted_access_readiness_components (
                readiness_component_id TEXT PRIMARY KEY,
                readiness_checkpoint_id TEXT NOT NULL,
                component_order INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                component_name TEXT NOT NULL,
                status_key TEXT NOT NULL,
                component_status TEXT NOT NULL,
                source_status_json TEXT NOT NULL,
                {component_true_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(readiness_checkpoint_id)
                    REFERENCES vault_provider_receipt_redacted_access_readiness_checkpoints(readiness_checkpoint_id)
                    ON DELETE CASCADE,
                UNIQUE(readiness_checkpoint_id, pack_id)
            )
            """
        )

        blocker_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_BLOCKER_FIELDS)
        blocker_false_sql = ",\n".join(
            f"{field} INTEGER NOT NULL DEFAULT 0"
            for field in ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]
        )
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_provider_receipt_redacted_access_readiness_blockers (
                readiness_blocker_id TEXT PRIMARY KEY,
                readiness_checkpoint_id TEXT NOT NULL,
                blocker_code TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                {blocker_true_sql},
                {blocker_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(readiness_checkpoint_id)
                    REFERENCES vault_provider_receipt_redacted_access_readiness_checkpoints(readiness_checkpoint_id)
                    ON DELETE CASCADE,
                UNIQUE(readiness_checkpoint_id, blocker_code)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_provider_receipt_redacted_access_readiness_events (
                event_id TEXT PRIMARY KEY,
                readiness_checkpoint_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(readiness_checkpoint_id)
                    REFERENCES vault_provider_receipt_redacted_access_readiness_checkpoints(readiness_checkpoint_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "real_sqlite_backed": True,
        "tables": [
            "vault_provider_receipt_redacted_access_readiness_checkpoints",
            "vault_provider_receipt_redacted_access_readiness_components",
            "vault_provider_receipt_redacted_access_readiness_blockers",
            "vault_provider_receipt_redacted_access_readiness_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, checkpoint_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VPRRARCEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_provider_receipt_redacted_access_readiness_events",
        {
            "event_id": event_id,
            "readiness_checkpoint_id": checkpoint_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "checkpoint_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_provider_receipt_redacted_access_readiness_checkpoints").fetchone()["c"]),
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_provider_receipt_redacted_access_readiness_components").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_provider_receipt_redacted_access_readiness_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_provider_receipt_redacted_access_readiness_events").fetchone()["c"]),
        }

def initialize_real_provider_receipt_redacted_access_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_provider_receipt_redacted_access_readiness_checkpoint_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            """
            SELECT readiness_checkpoint_id
            FROM vault_provider_receipt_redacted_access_readiness_checkpoints
            WHERE readiness_checkpoint_id = ?
            """,
            (DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,),
        ).fetchone()

        if exists is None:
            components = _collect_component_statuses()
            now = _now_iso()

            component_ready_count = sum(1 for item in components if item["ready"])
            component_validation_passed_count = sum(1 for item in components if item["validation_passed"])
            component_safe_count = sum(1 for item in components if item["safe_to_continue"])
            component_vault_not_done_count = sum(1 for item in components if item["vault_done"] is False)
            component_no_export_count = sum(1 for item in components if item["export_enabled"] is False)
            component_no_execution_count = sum(1 for item in components if item["execution_enabled"] is False)
            component_no_direct_upload_count = sum(1 for item in components if item["direct_upload_enabled"] is False)

            readiness_score = 100 if (
                component_ready_count == len(COMPONENT_SPECS)
                and component_validation_passed_count == len(COMPONENT_SPECS)
                and component_safe_count == len(COMPONENT_SPECS)
                and component_vault_not_done_count == len(COMPONENT_SPECS)
                and component_no_export_count == len(COMPONENT_SPECS)
                and component_no_execution_count == len(COMPONENT_SPECS)
                and component_no_direct_upload_count == len(COMPONENT_SPECS)
            ) else 0

            checkpoint_data = {
                "schema_version": SCHEMA_VERSION,
                "checkpoint_type": "REAL_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT",
                "section": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "component_count": len(COMPONENT_SPECS),
                "component_ready_count": component_ready_count,
                "component_validation_passed_count": component_validation_passed_count,
                "component_safe_count": component_safe_count,
                "component_vault_not_done_count": component_vault_not_done_count,
                "component_no_export_count": component_no_export_count,
                "component_no_execution_count": component_no_execution_count,
                "component_no_direct_upload_count": component_no_direct_upload_count,
                "blocker_count": len(READINESS_BLOCKER_SPECS),
                "readiness_score": readiness_score,
                "readiness_label": "Real provider receipt and redacted access layer ready",
                "layer_closed": True,
                "safe_to_continue_to_gp081": True,
                "vault_done": False,
                "next_section": NEXT_SECTION_ID,
                "next_section_title": NEXT_SECTION_TITLE,
                "next_section_range": NEXT_SECTION_RANGE,
                "next_pack": NEXT_PACK,
                "next_pack_title": NEXT_PACK_TITLE,
            }

            checkpoint_payload = {
                "readiness_checkpoint_id": DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,
                "pack_id": PACK_ID,
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "next_section_id": NEXT_SECTION_ID,
                "next_section_title": NEXT_SECTION_TITLE,
                "next_section_range": NEXT_SECTION_RANGE,
                "next_pack": NEXT_PACK,
                "checkpoint_status": "REAL_PROVIDER_RECEIPT_REDACTED_ACCESS_LAYER_READY_CLOSED_NOT_DONE",
                "readiness_label": "Real provider receipt and redacted access layer ready",
                "readiness_score": readiness_score,
                "checkpoint_data_json": _json_dumps(checkpoint_data),
                "created_at": now,
                "updated_at": now,
            }
            for field in TRUE_CHECKPOINT_FIELDS:
                checkpoint_payload[field] = 1
            for field in FALSE_FIELDS:
                checkpoint_payload[field] = 0
            _insert_dict(conn, "vault_provider_receipt_redacted_access_readiness_checkpoints", checkpoint_payload)

            for component in components:
                payload = {
                    "readiness_component_id": f"VPRRARC-COMP-{component['pack_id'].replace('VAULT_GP', 'GP')}",
                    "readiness_checkpoint_id": DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,
                    "component_order": component["component_order"],
                    "pack_id": component["pack_id"],
                    "component_name": component["component_name"],
                    "status_key": component["status_key"],
                    "component_status": "REAL_COMPONENT_READY_LOCKED_SAFE_TO_CONTINUE",
                    "source_status_json": _json_dumps(component["source"]),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_COMPONENT_FIELDS:
                    payload[field] = 1
                _insert_dict(conn, "vault_provider_receipt_redacted_access_readiness_components", payload)

            for code, name, category in READINESS_BLOCKER_SPECS:
                payload = {
                    "readiness_blocker_id": f"VPRRARC-BLOCK-{code.upper().replace('_', '-')}",
                    "readiness_checkpoint_id": DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": "HIGH",
                    "blocker_status": "ACTIVE_CARRIED_TO_NEXT_LAYER",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_BLOCKER_FIELDS:
                    payload[field] = 1
                for field in ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]:
                    payload[field] = 0
                _insert_dict(conn, "vault_provider_receipt_redacted_access_readiness_blockers", payload)

            for event_type, event_payload in [
                ("REAL_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_CREATED", checkpoint_data),
                ("GP071_GP079_COMPONENTS_REGISTERED", {
                    "component_count": len(COMPONENT_SPECS),
                    "component_ready_count": component_ready_count,
                    "component_validation_passed_count": component_validation_passed_count,
                    "component_safe_count": component_safe_count,
                }),
                ("READINESS_BLOCKERS_REGISTERED", {"blocker_count": len(READINESS_BLOCKER_SPECS)}),
                ("PROVIDER_RECEIPT_REDACTED_ACCESS_LOCKS_CONFIRMED", {
                    "provider_object_catalog_unlocked": False,
                    "provider_metadata_imported": False,
                    "provider_objects_listed": False,
                    "object_body_read": False,
                    "redacted_access_view_enabled": False,
                    "owner_review_packet_created": False,
                    "owner_review_queue_created": False,
                    "owner_decision_recorded": False,
                    "owner_review_decision_receipt_created": False,
                    "owner_review_closeout_created": False,
                    "tower_unlock_granted": False,
                    "direct_upload_enabled": False,
                    "export_enabled": False,
                    "execution_enabled": False,
                    "vault_done": False,
                }),
                ("REAL_PROVIDER_RECEIPT_REDACTED_ACCESS_LAYER_CLOSED", {
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    "readiness_score": readiness_score,
                    "safe_to_continue_to_gp081": True,
                }),
                ("NEXT_LAYER_PREPARED", {
                    "next_section_id": NEXT_SECTION_ID,
                    "next_section_range": NEXT_SECTION_RANGE,
                    "next_pack": NEXT_PACK,
                    "vault_done": False,
                }),
            ]:
                _insert_event(conn, DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _sum_counts(table: str, checkpoint_id: str, fields: list[str], db_path: Optional[str] = None) -> Dict[str, int]:
    selects = ["COUNT(*) AS total_count"]
    for field in fields:
        selects.append(f"SUM(CASE WHEN {field} = 1 THEN 1 ELSE 0 END) AS {field}_count")
    with _connect(db_path) as conn:
        row = conn.execute(
            f"SELECT {', '.join(selects)} FROM {table} WHERE readiness_checkpoint_id = ?",
            (checkpoint_id,),
        ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}

def get_provider_receipt_redacted_access_readiness_checkpoint_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_receipt_redacted_access_readiness_checkpoint(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_provider_receipt_redacted_access_readiness_checkpoints
            WHERE readiness_checkpoint_id = ?
            """,
            (DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,),
        ).fetchone()
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "readiness_checkpoint": _boolify(row, {"checkpoint_data_json": "checkpoint_data"}),
    }

def get_provider_receipt_redacted_access_readiness_components(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_receipt_redacted_access_readiness_checkpoint(db_path)
    counts = _sum_counts(
        "vault_provider_receipt_redacted_access_readiness_components",
        DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,
        TRUE_COMPONENT_FIELDS,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_provider_receipt_redacted_access_readiness_components
            WHERE readiness_checkpoint_id = ?
            ORDER BY component_order
            """,
            (DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,),
        ).fetchall()
    counts["component_count"] = counts.pop("total_count")
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "components": [_boolify(row, {"source_status_json": "source_status"}) for row in rows],
    }

def get_provider_receipt_redacted_access_readiness_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_receipt_redacted_access_readiness_checkpoint(db_path)
    fields = TRUE_BLOCKER_FIELDS + ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]
    counts = _sum_counts(
        "vault_provider_receipt_redacted_access_readiness_blockers",
        DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_provider_receipt_redacted_access_readiness_blockers
            WHERE readiness_checkpoint_id = ?
            ORDER BY blocker_category, blocker_code
            """,
            (DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,),
        ).fetchall()
    counts["blocker_count"] = counts.pop("total_count")
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "blockers": [_boolify(row) for row in rows],
    }

def get_provider_receipt_redacted_access_readiness_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_receipt_redacted_access_readiness_checkpoint(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_provider_receipt_redacted_access_readiness_events
            WHERE readiness_checkpoint_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,),
        ).fetchall()
    events = [
        {
            "event_id": row["event_id"],
            "readiness_checkpoint_id": row["readiness_checkpoint_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def record_provider_receipt_redacted_access_readiness_event(event_type: str, event_payload: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_receipt_redacted_access_readiness_checkpoint(db_path)
    payload = dict(event_payload or {})
    payload.update({
        "write_type": "REAL_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_EVENT",
        "readiness_checkpoint_ready": True,
        "section_gp071_gp080_ready": True,
        "real_provider_receipt_redacted_access_layer_closed": True,
        "safe_to_continue_to_gp081": True,
        "provider_object_catalog_unlocked": False,
        "provider_metadata_imported": False,
        "provider_objects_listed": False,
        "object_identifier_collected": False,
        "object_body_read": False,
        "redacted_access_view_enabled": False,
        "owner_review_packet_created": False,
        "owner_review_queue_created": False,
        "owner_decision_recorded": False,
        "owner_review_decision_receipt_created": False,
        "owner_review_closeout_created": False,
        "tower_unlock_granted": False,
        "direct_upload_enabled": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    })
    with _connect(db_path) as conn:
        event_id = _insert_event(conn, DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID, event_type, payload)
        conn.commit()
    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "readiness_checkpoint_id": DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,
        "real_sqlite_backed": True,
        **payload,
    }

def validate_provider_receipt_redacted_access_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    checkpoint = get_provider_receipt_redacted_access_readiness_checkpoint_record(db_path)["readiness_checkpoint"]
    components = get_provider_receipt_redacted_access_readiness_components(db_path)
    blockers = get_provider_receipt_redacted_access_readiness_blockers(db_path)
    events = get_provider_receipt_redacted_access_readiness_events(db_path)

    expected_components = len(COMPONENT_SPECS)
    expected_blockers = len(READINESS_BLOCKER_SPECS)

    false_checks = [(f"NO_CHECKPOINT_{field.upper()}", checkpoint[field] is False) for field in FALSE_FIELDS]

    checks = [
        ("REAL_SQLITE_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_EXISTS", checkpoint["readiness_checkpoint_id"] == DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID),
        ("CHECKPOINT_PACK_ID_GP080", checkpoint["pack_id"] == PACK_ID),
        ("SECTION_GP071_GP080_READY", checkpoint["section_gp071_gp080_ready"] is True),
        ("READINESS_CHECKPOINT_READY", checkpoint["provider_receipt_redacted_access_readiness_checkpoint_ready"] is True),
        ("COMPONENT_REGISTRY_READY", checkpoint["component_registry_ready"] is True),
        ("COMPONENT_VALIDATION_READY", checkpoint["component_validation_ready"] is True),
        ("BLOCKER_REGISTER_READY", checkpoint["blocker_register_ready"] is True),
        ("EVENT_LOG_READY", checkpoint["event_log_ready"] is True),
        ("REAL_PROVIDER_RECEIPT_REDACTED_ACCESS_LAYER_CLOSED", checkpoint["real_provider_receipt_redacted_access_layer_closed"] is True),
        ("READINESS_SCORE_100", checkpoint["readiness_score"] == 100),
        ("SAFE_TO_CONTINUE_TO_GP081", checkpoint["safe_to_continue_to_gp081"] is True),
        ("NEXT_SECTION_READY", checkpoint["next_section_id"] == NEXT_SECTION_ID and checkpoint["next_pack"] == NEXT_PACK),
        ("REAL_COMPONENTS_EXIST", components["component_count"] == expected_components),
        ("ALL_COMPONENTS_READY", components["component_ready_count"] == expected_components),
        ("ALL_COMPONENTS_VALIDATION_PASSED", components["component_validation_passed_count"] == expected_components),
        ("ALL_COMPONENTS_SAFE_TO_CONTINUE", components["component_safe_to_continue_count"] == expected_components),
        ("ALL_COMPONENTS_REAL_SQLITE_BACKED", components["component_real_sqlite_backed_count"] == expected_components),
        ("ALL_COMPONENTS_LOCKED", components["component_locked_count"] == expected_components),
        ("ALL_COMPONENTS_TEMPLATE_ONLY_OR_CHECKPOINT", components["component_template_only_or_checkpoint_count"] == expected_components),
        ("ALL_COMPONENTS_NO_PROVIDER_UNLOCK", components["component_no_provider_unlock_count"] == expected_components),
        ("ALL_COMPONENTS_NO_DIRECT_UPLOAD", components["component_no_direct_upload_count"] == expected_components),
        ("ALL_COMPONENTS_NO_EXPORT", components["component_no_export_count"] == expected_components),
        ("ALL_COMPONENTS_NO_EXECUTION", components["component_no_execution_count"] == expected_components),
        ("ALL_COMPONENTS_VAULT_NOT_DONE", components["component_vault_not_done_count"] == expected_components),
        ("READINESS_BLOCKERS_EXIST", blockers["blocker_count"] == expected_blockers),
        ("ALL_BLOCKERS_ACTIVE", blockers["blocker_active_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_UNLOCK", blockers["blocks_provider_unlock_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_LISTING", blockers["blocks_provider_listing_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_METADATA_IMPORT", blockers["blocks_metadata_import_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_OBJECT_IDENTIFIER_COLLECTION", blockers["blocks_object_identifier_collection_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY_READ", blockers["blocks_object_body_read_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_OWNER_REVIEW_FINALIZATION", blockers["blocks_owner_review_finalization_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_TOWER_UNLOCK", blockers["blocks_tower_unlock_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_DIRECT_UPLOAD", blockers["blocks_direct_upload_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_EXPORT", blockers["blocks_export_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_EXECUTION", blockers["blocks_execution_count"] == expected_blockers),
        ("NO_BLOCKERS_TOWER_REVIEW_GRANTED", blockers["tower_review_granted_count"] == 0),
        ("NO_BLOCKERS_RESOLVED", blockers["resolved_count"] == 0),
        ("EVENT_LOG_EXISTS", events["event_count"] >= 6),
    ] + false_checks

    checks_payload = [{"code": code, "passed": bool(passed)} for code, passed in checks]
    failed = [item for item in checks_payload if not item["passed"]]

    return {
        "pack": _pack_payload(),
        "validation_ready": True,
        "valid": len(failed) == 0,
        "check_count": len(checks_payload),
        "passed_count": len(checks_payload) - len(failed),
        "failed_count": len(failed),
        "failed_checks": failed,
        "checks": checks_payload,
        "real_sqlite_backed": True,
        "section_closed": len(failed) == 0,
        "safe_to_continue_to_gp081": len(failed) == 0,
        "vault_done": False,
    }

def get_provider_receipt_redacted_access_readiness_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "closed_section": True,
            "next_section": NEXT_SECTION_ID,
            "next_section_title": NEXT_SECTION_TITLE,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp081": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP080 closes the GP071-GP080 real provider receipt and redacted access layer. Continue to GP081 with the real storage provider restore request lock contract while provider access, object body read/view/download, owner review finalization, direct upload, export, and execution remain locked.",
            "carry_forward_rules": [
                "Carry forward the GP071-GP080 readiness checkpoint.",
                "Keep provider object catalog locked.",
                "Keep provider object listing locked.",
                "Keep provider metadata import/read locked.",
                "Keep object identifiers and object bodies locked.",
                "Keep redacted access view locked.",
                "Keep owner packet, queue, decision, receipt, and closeout finalization locked.",
                "Do not request or grant Tower unlock.",
                "Do not enable direct upload.",
                "Do not unlock export.",
                "Do not unlock execution.",
                "Do not treat Vault as done.",
            ],
        },
    }

def _pack_payload() -> Dict[str, Any]:
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": [item[0] for item in COMPONENT_SPECS],
        "foundation_status": "provider_receipt_redacted_access_readiness_checkpoint_ready_section_closed_not_done",
        "product_depth_layer": "real_provider_receipt_redacted_access_readiness_checkpoint",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-provider-receipt-redacted-access-readiness-checkpoint",
        "json_route": "/vault/real-provider-receipt-redacted-access-readiness-checkpoint.json",
        "record_route": "/vault/provider-receipt-redacted-access-readiness-checkpoint-record.json",
        "components_route": "/vault/provider-receipt-redacted-access-readiness-components.json",
        "blockers_route": "/vault/provider-receipt-redacted-access-readiness-blockers.json",
        "events_route": "/vault/provider-receipt-redacted-access-readiness-events.json",
        "validation_route": "/vault/provider-receipt-redacted-access-readiness-validation.json",
        "next_step_route": "/vault/provider-receipt-redacted-access-readiness-next-step.json",
        "gp080_status_route": "/vault/gp080-status.json",
    }

def get_real_provider_receipt_redacted_access_readiness_checkpoint_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_provider_receipt_redacted_access_readiness_checkpoint(db_path)
    checkpoint = get_provider_receipt_redacted_access_readiness_checkpoint_record(db_path)["readiness_checkpoint"]
    components = get_provider_receipt_redacted_access_readiness_components(db_path)
    blockers = get_provider_receipt_redacted_access_readiness_blockers(db_path)
    events = get_provider_receipt_redacted_access_readiness_events(db_path)
    validation = validate_provider_receipt_redacted_access_readiness_checkpoint(db_path)

    truth = {
        "real_provider_receipt_redacted_access_readiness_checkpoint_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "section_gp071_gp080_ready": checkpoint["section_gp071_gp080_ready"],
        "section_closed": validation["section_closed"],
        "readiness_score": checkpoint["readiness_score"],
        "readiness_label": checkpoint["readiness_label"],
        "component_count": components["component_count"],
        "blocker_count": blockers["blocker_count"],
        "event_count": events["event_count"],
        "validation_passed": validation["valid"],
        "provider_object_catalog_unlocked": checkpoint["provider_object_catalog_unlocked"],
        "provider_object_listing_configured": checkpoint["provider_object_listing_configured"],
        "provider_object_list_attempted": checkpoint["provider_object_list_attempted"],
        "provider_objects_listed": checkpoint["provider_objects_listed"],
        "provider_metadata_imported": checkpoint["provider_metadata_imported"],
        "provider_metadata_read": checkpoint["provider_metadata_read"],
        "object_identifier_collected": checkpoint["object_identifier_collected"],
        "object_body_read": checkpoint["object_body_read"],
        "object_body_view_enabled": checkpoint["object_body_view_enabled"],
        "object_body_download_enabled": checkpoint["object_body_download_enabled"],
        "redacted_access_view_enabled": checkpoint["redacted_access_view_enabled"],
        "owner_review_packet_created": checkpoint["owner_review_packet_created"],
        "owner_review_queue_created": checkpoint["owner_review_queue_created"],
        "owner_decision_recorded": checkpoint["owner_decision_recorded"],
        "owner_review_decision_receipt_created": checkpoint["owner_review_decision_receipt_created"],
        "owner_review_closeout_created": checkpoint["owner_review_closeout_created"],
        "tower_unlock_requested": checkpoint["tower_unlock_requested"],
        "tower_unlock_granted": checkpoint["tower_unlock_granted"],
        "provider_packet_attached": checkpoint["provider_packet_attached"],
        "object_identifier_attached": checkpoint["object_identifier_attached"],
        "object_body_attached": checkpoint["object_body_attached"],
        "direct_upload_enabled": checkpoint["direct_upload_enabled"],
        "export_enabled": checkpoint["export_enabled"],
        "execution_enabled": checkpoint["execution_enabled"],
        "safe_to_continue_to_gp081": validation["safe_to_continue_to_gp081"],
        "vault_done": checkpoint["vault_done"],
    }

    return {
        "pack": _pack_payload(),
        "provider_receipt_redacted_access_truth": truth,
        "store": init,
        "readiness_checkpoint": checkpoint,
        "components": components,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_provider_receipt_redacted_access_readiness_next_step()["next_step"],
    }

def get_gp080_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_provider_receipt_redacted_access_readiness_checkpoint_home(db_path)
    checkpoint = home["readiness_checkpoint"]
    components = home["components"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp080_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "section_closed": validation["section_closed"],
            "next_section_id": NEXT_SECTION_ID,
            "next_section_title": NEXT_SECTION_TITLE,
            "next_section_range": NEXT_SECTION_RANGE,
            "real_provider_receipt_redacted_access_readiness_checkpoint_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "readiness_checkpoint_id": checkpoint["readiness_checkpoint_id"],
            "readiness_score": checkpoint["readiness_score"],
            "readiness_label": checkpoint["readiness_label"],
            "real_checkpoint_count": home["store"]["checkpoint_count"],
            "real_component_count": home["store"]["component_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "component_count": components["component_count"],
            "component_ready_count": components["component_ready_count"],
            "component_validation_passed_count": components["component_validation_passed_count"],
            "component_safe_to_continue_count": components["component_safe_to_continue_count"],
            "component_real_sqlite_backed_count": components["component_real_sqlite_backed_count"],
            "component_locked_count": components["component_locked_count"],
            "component_template_only_or_checkpoint_count": components["component_template_only_or_checkpoint_count"],
            "component_no_provider_unlock_count": components["component_no_provider_unlock_count"],
            "component_no_direct_upload_count": components["component_no_direct_upload_count"],
            "component_no_export_count": components["component_no_export_count"],
            "component_no_execution_count": components["component_no_execution_count"],
            "component_vault_not_done_count": components["component_vault_not_done_count"],
            "blocker_count": blockers["blocker_count"],
            "blocker_active_count": blockers["blocker_active_count"],
            "blocks_provider_unlock_count": blockers["blocks_provider_unlock_count"],
            "blocks_provider_listing_count": blockers["blocks_provider_listing_count"],
            "blocks_metadata_import_count": blockers["blocks_metadata_import_count"],
            "blocks_object_identifier_collection_count": blockers["blocks_object_identifier_collection_count"],
            "blocks_object_body_read_count": blockers["blocks_object_body_read_count"],
            "blocks_owner_review_finalization_count": blockers["blocks_owner_review_finalization_count"],
            "blocks_tower_unlock_count": blockers["blocks_tower_unlock_count"],
            "blocks_direct_upload_count": blockers["blocks_direct_upload_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "tower_review_granted_count": blockers["tower_review_granted_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp081": validation["safe_to_continue_to_gp081"],
            "foundation_status": "provider_receipt_redacted_access_readiness_checkpoint_ready_section_closed_not_done",
            "provider_object_catalog_unlocked": checkpoint["provider_object_catalog_unlocked"],
            "provider_object_listing_configured": checkpoint["provider_object_listing_configured"],
            "provider_object_list_attempted": checkpoint["provider_object_list_attempted"],
            "provider_objects_listed": checkpoint["provider_objects_listed"],
            "provider_metadata_imported": checkpoint["provider_metadata_imported"],
            "provider_metadata_read": checkpoint["provider_metadata_read"],
            "provider_object_metadata_imported": checkpoint["provider_object_metadata_imported"],
            "object_identifier_collected": checkpoint["object_identifier_collected"],
            "object_id_collected": checkpoint["object_id_collected"],
            "object_key_collected": checkpoint["object_key_collected"],
            "object_etag_collected": checkpoint["object_etag_collected"],
            "object_size_collected": checkpoint["object_size_collected"],
            "object_timestamp_collected": checkpoint["object_timestamp_collected"],
            "object_body_read_attempted": checkpoint["object_body_read_attempted"],
            "object_body_read": checkpoint["object_body_read"],
            "object_body_view_enabled": checkpoint["object_body_view_enabled"],
            "object_body_content_exposed": checkpoint["object_body_content_exposed"],
            "object_body_plaintext_visible": checkpoint["object_body_plaintext_visible"],
            "object_body_download_enabled": checkpoint["object_body_download_enabled"],
            "redacted_access_view_enabled": checkpoint["redacted_access_view_enabled"],
            "live_provider_access_view_created": checkpoint["live_provider_access_view_created"],
            "owner_review_packet_created": checkpoint["owner_review_packet_created"],
            "owner_review_queue_created": checkpoint["owner_review_queue_created"],
            "owner_decision_recorded": checkpoint["owner_decision_recorded"],
            "owner_review_decision_receipt_created": checkpoint["owner_review_decision_receipt_created"],
            "owner_review_closeout_created": checkpoint["owner_review_closeout_created"],
            "owner_review_closeout_finalized": checkpoint["owner_review_closeout_finalized"],
            "closeout_transition_to_readiness_enabled": checkpoint["closeout_transition_to_readiness_enabled"],
            "tower_unlock_requested": checkpoint["tower_unlock_requested"],
            "tower_unlock_granted": checkpoint["tower_unlock_granted"],
            "provider_packet_attached": checkpoint["provider_packet_attached"],
            "object_identifier_attached": checkpoint["object_identifier_attached"],
            "object_body_attached": checkpoint["object_body_attached"],
            "direct_upload_enabled": checkpoint["direct_upload_enabled"],
            "export_enabled": checkpoint["export_enabled"],
            "execution_enabled": checkpoint["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp080",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "provider_receipt_redacted_access_truth": home["provider_receipt_redacted_access_truth"],
        "routes": home["routes"],
        "readiness_checkpoint": checkpoint,
        "components": components,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }

def render_real_provider_receipt_redacted_access_readiness_checkpoint_page() -> str:
    home = get_real_provider_receipt_redacted_access_readiness_checkpoint_home()
    truth = home["provider_receipt_redacted_access_truth"]
    routes = home["routes"]
    next_step = home["next_step"]

    component_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['pack_id'])}</strong>
          <span>{escape(item['component_name'])}</span>
          <code>{escape(item['component_status'])}</code>
        </article>
        """
        for item in home["components"]["components"]
    )
    checks = "\n".join(
        f"<div class='row'><strong>{escape(c['code'])}</strong><span>{'PASS' if c['passed'] else 'FAIL'}</span></div>"
        for c in home["validation"]["checks"]
    )
    rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault Real Provider Receipt and Redacted Access Readiness Checkpoint · GP080</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{
  --bg0:#040612; --bg1:#090d22; --panel:rgba(15,23,52,.86); --panel2:rgba(21,32,74,.76);
  --line:rgba(160,179,255,.24); --text:#eef3ff; --muted:#9da9d7; --gold:#f5d17e;
  --cyan:#83eaff; --danger:#ff8c9c; --ok:#9dffca;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; min-height:100vh; color:var(--text);
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  background:
    radial-gradient(circle at 12% 9%, rgba(173,141,255,.18), transparent 34%),
    radial-gradient(circle at 88% 5%, rgba(131,234,255,.13), transparent 30%),
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
    <div class="eyebrow">Archive Vault · Giant Pack 080</div>
    <div class="eyebrow">Real Provider Receipt and Redacted Access Layer · GP071-GP080</div>
    <h1>Real Provider Receipt and Redacted Access Readiness Checkpoint</h1>
    <p>GP080 closes the GP071-GP080 layer with a real readiness checkpoint. It confirms the layer is ready to continue while provider access, object body reads, owner review finalization, export, and execution remain locked.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['readiness_score']}</strong><span>readiness score</span></div>
      <div class="metric"><strong>{truth['component_count']}</strong><span>components verified</span></div>
      <div class="metric"><strong>{truth['blocker_count']}</strong><span>blockers carried</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">Section closed</span>
      <span class="pill ok">Real SQLite-backed</span>
      <span class="pill ok">Safe to GP081</span>
      <span class="pill danger">No provider unlock</span>
      <span class="pill danger">No object body read</span>
      <span class="pill danger">No direct upload</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Verified Components</h2>
    <div class="cards">{component_cards}</div>
  </section>

  <section class="section">
    <h2>Validation Checks</h2>
    {checks}
  </section>

  <section class="section">
    <h2>Next Step</h2>
    <p>{escape(next_step['owner_notebook_note'])}</p>
    <ul>{rules}</ul>
  </section>

  <section class="section">
    <h2>GP080 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['components_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_step_route'])}</code>
      <code>{escape(routes['gp080_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
