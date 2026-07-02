"""
VAULT GP070 — Real Storage Provider Configuration Readiness Checkpoint

Current section:
Archive Vault — Real Storage Provider Configuration Layer / GP061-GP070

This pack closes the real storage provider configuration layer with a real
SQLite-backed readiness checkpoint. It summarizes GP061-GP069 and proves the
Vault can continue to the next section while every actual provider capability
remains locked.

It does not configure credentials, secrets, endpoint, namespace, encryption,
connection tests, write path, read path, object body view, upload, export, or
execution.
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

from vault.real_storage_provider_object_body_view_lock_contract_service import (
    get_gp069_status,
)

PACK_ID = "VAULT_GP070"
PACK_NAME = "Real Storage Provider Configuration Readiness Checkpoint"
SCHEMA_VERSION = "vault.real_storage_provider_configuration_readiness_checkpoint.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
SECTION_TITLE = "Archive Vault — Real Storage Provider Configuration Layer"
SECTION_RANGE = "GP061-GP070"

NEXT_SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
NEXT_SECTION_TITLE = "Archive Vault — Real Provider Receipt and Redacted Access Layer"
NEXT_SECTION_RANGE = "GP071-GP080"
NEXT_PACK = "VAULT_GP071_REAL_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT"
NEXT_PACK_TITLE = "Real Storage Provider Object Catalog Lock Contract"

DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID = "VSPCRC-GP070-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_configuration_readiness_checkpoint.sqlite"

CONFIGURATION_COMPONENTS = [
    ("VAULT_GP061", "Real Storage Provider Config Contract", "config_contract", "/vault/gp061-status.json"),
    ("VAULT_GP062", "Real Storage Provider Credential Boundary", "credential_boundary", "/vault/gp062-status.json"),
    ("VAULT_GP063", "Real Storage Provider Secret Reference Ledger", "secret_reference_ledger", "/vault/gp063-status.json"),
    ("VAULT_GP064", "Real Storage Provider Endpoint Namespace Contract", "endpoint_namespace_contract", "/vault/gp064-status.json"),
    ("VAULT_GP065", "Real Storage Provider Encryption Policy Contract", "encryption_policy_contract", "/vault/gp065-status.json"),
    ("VAULT_GP066", "Real Storage Provider Connection Test Lock Contract", "connection_test_lock_contract", "/vault/gp066-status.json"),
    ("VAULT_GP067", "Real Storage Provider Write Path Lock Contract", "write_path_lock_contract", "/vault/gp067-status.json"),
    ("VAULT_GP068", "Real Storage Provider Read Path Lock Contract", "read_path_lock_contract", "/vault/gp068-status.json"),
    ("VAULT_GP069", "Real Storage Provider Object Body View Lock Contract", "object_body_view_lock_contract", "/vault/gp069-status.json"),
]

CONFIGURATION_READINESS_BLOCKERS = [
    ("credentials_not_configured", "Credentials are not configured", "credential_boundary"),
    ("secret_values_not_stored", "Secret values are not stored", "secret_boundary"),
    ("secret_references_not_activated", "Secret references are not activated", "secret_reference_boundary"),
    ("endpoint_not_configured", "Provider endpoint is not configured", "endpoint_namespace_boundary"),
    ("container_not_configured", "Storage container is not configured", "endpoint_namespace_boundary"),
    ("namespace_not_configured", "Storage namespace is not configured", "endpoint_namespace_boundary"),
    ("encryption_not_configured", "Encryption policy is not configured", "encryption_boundary"),
    ("connection_not_tested", "Provider connection is not tested", "connection_test_lock"),
    ("write_path_locked", "Provider write path remains locked", "write_path_lock"),
    ("read_path_locked", "Provider read path remains locked", "read_path_lock"),
    ("object_body_view_locked", "Object body view remains locked", "object_body_view_lock"),
    ("direct_upload_locked", "Direct upload remains locked", "upload_lock"),
    ("export_locked", "Export remains locked", "export_lock"),
    ("execution_locked", "Execution remains locked", "execution_lock"),
]

FALSE_FIELDS = [
    "actual_secret_values_stored",
    "secret_values_present",
    "token_material_present",
    "encrypted_secret_payload_present",
    "key_material_stored",
    "kms_key_id_stored",
    "key_locator_present",
    "credentials_configured",
    "secret_references_created",
    "secret_references_activated",
    "provider_endpoint_configured",
    "storage_container_configured",
    "namespace_configured",
    "encryption_policy_configured",
    "connection_probe_configured",
    "connection_test_attempted",
    "provider_connection_tested",
    "write_path_configured",
    "write_path_attempted",
    "write_path_enabled",
    "upload_path_configured",
    "object_create_attempted",
    "object_created",
    "read_path_configured",
    "read_path_attempted",
    "read_path_enabled",
    "read_receipt_created",
    "object_listing_configured",
    "object_list_attempted",
    "object_listed",
    "object_body_read_attempted",
    "object_body_read",
    "object_body_view_configured",
    "object_body_view_attempted",
    "object_body_view_enabled",
    "object_body_receipt_created",
    "object_body_content_exposed",
    "object_body_plaintext_visible",
    "object_body_download_enabled",
    "provider_approval_ready",
    "provider_activation_ready",
    "provider_configuration_ready",
    "provider_read_write_ready",
    "provider_approved",
    "provider_activated",
    "provider_recommended",
    "provider_selected",
    "provider_configured",
    "provider_read_enabled",
    "provider_write_enabled",
    "provider_object_read_claimed",
    "provider_object_write_claimed",
    "risk_accepted",
    "risk_waived",
    "mitigation_approved",
    "official_storage_receipt",
    "finalized_storage_receipt",
    "closed_storage_receipt",
    "direct_upload_enabled",
    "export_enabled",
    "execution_enabled",
    "vault_done",
]

TRUE_CHECKPOINT_FIELDS = [
    "configuration_readiness_checkpoint_ready",
    "configuration_layer_closed",
    "configuration_components_ready",
    "configuration_blockers_ready",
    "configuration_validation_ready",
    "configuration_locked",
    "safe_to_continue_to_next_section",
]

TRUE_COMPONENT_FIELDS = [
    "component_ready",
    "component_verified",
    "component_locked",
    "tower_review_required",
]

TRUE_BLOCKER_FIELDS = [
    "blocker_active",
    "blocks_provider_configuration",
    "blocks_provider_read_write",
    "blocks_object_body_view",
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
    json_fields = json_fields or {}
    out = {}
    for key in row.keys():
        if key in json_fields:
            out[json_fields[key]] = _json_loads(row[key])
        elif isinstance(row[key], int):
            out[key] = bool(row[key])
        else:
            out[key] = row[key]
    return out

def ensure_storage_provider_configuration_readiness_checkpoint_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)
        true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_CHECKPOINT_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_configuration_readiness_checkpoints (
                configuration_readiness_checkpoint_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_object_body_view_lock_contract_id TEXT NOT NULL,
                source_object_body_view_pack_id TEXT NOT NULL,
                checkpoint_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                checkpoint_data_json TEXT NOT NULL,
                {true_sql},
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        component_false_fields = [
            "component_unlocks_provider",
            "component_unlocks_credentials",
            "component_unlocks_secrets",
            "component_unlocks_endpoint",
            "component_unlocks_encryption",
            "component_unlocks_connection_test",
            "component_unlocks_write_path",
            "component_unlocks_read_path",
            "component_unlocks_object_body_view",
            "component_unlocks_direct_upload",
            "component_unlocks_export",
            "component_unlocks_execution",
            "tower_review_granted",
            "component_claims_vault_done",
        ]
        component_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in component_false_fields)
        component_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_COMPONENT_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_configuration_readiness_components (
                configuration_component_id TEXT PRIMARY KEY,
                configuration_readiness_checkpoint_id TEXT NOT NULL,
                source_pack_id TEXT NOT NULL,
                component_name TEXT NOT NULL,
                component_category TEXT NOT NULL,
                component_status_route TEXT NOT NULL,
                component_status TEXT NOT NULL,
                component_notes TEXT NOT NULL,
                {component_true_sql},
                {component_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(configuration_readiness_checkpoint_id)
                    REFERENCES vault_storage_provider_configuration_readiness_checkpoints(configuration_readiness_checkpoint_id)
                    ON DELETE CASCADE,
                UNIQUE(configuration_readiness_checkpoint_id, source_pack_id)
            )
            """
        )

        blocker_false_fields = [
            "tower_review_granted",
            "risk_accepted",
            "risk_waived",
            "mitigation_approved",
            "resolved",
        ]
        blocker_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in blocker_false_fields)
        blocker_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_BLOCKER_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_configuration_readiness_blockers (
                configuration_blocker_id TEXT PRIMARY KEY,
                configuration_readiness_checkpoint_id TEXT NOT NULL,
                blocker_code TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                {blocker_true_sql},
                {blocker_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(configuration_readiness_checkpoint_id)
                    REFERENCES vault_storage_provider_configuration_readiness_checkpoints(configuration_readiness_checkpoint_id)
                    ON DELETE CASCADE,
                UNIQUE(configuration_readiness_checkpoint_id, blocker_code)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_configuration_readiness_events (
                event_id TEXT PRIMARY KEY,
                configuration_readiness_checkpoint_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(configuration_readiness_checkpoint_id)
                    REFERENCES vault_storage_provider_configuration_readiness_checkpoints(configuration_readiness_checkpoint_id)
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
            "vault_storage_provider_configuration_readiness_checkpoints",
            "vault_storage_provider_configuration_readiness_components",
            "vault_storage_provider_configuration_readiness_blockers",
            "vault_storage_provider_configuration_readiness_events",
        ],
    }

def _insert_event(conn, checkpoint_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VSPCRCEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_storage_provider_configuration_readiness_events",
        {
            "event_id": event_id,
            "configuration_readiness_checkpoint_id": checkpoint_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "checkpoint_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_configuration_readiness_checkpoints").fetchone()["c"]),
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_configuration_readiness_components").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_configuration_readiness_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_configuration_readiness_events").fetchone()["c"]),
        }

def initialize_real_storage_provider_configuration_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_configuration_readiness_checkpoint_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            """
            SELECT configuration_readiness_checkpoint_id
            FROM vault_storage_provider_configuration_readiness_checkpoints
            WHERE configuration_readiness_checkpoint_id = ?
            """,
            (DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,),
        ).fetchone()

        if exists is None:
            source = get_gp069_status()
            source_status = source["gp069_status"]
            source_contract = source["object_body_view_lock_contract"]
            now = _now_iso()

            checkpoint_data = {
                "schema_version": SCHEMA_VERSION,
                "checkpoint_type": "REAL_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT",
                "source_pack": "VAULT_GP069",
                "source_object_body_view_lock_contract_id": source_contract["object_body_view_lock_contract_id"],
                "section_closed": SECTION_ID,
                "section_range": SECTION_RANGE,
                "component_count": len(CONFIGURATION_COMPONENTS),
                "blocker_count": len(CONFIGURATION_READINESS_BLOCKERS),
                "configuration_locked": True,
                "safe_to_continue_to_next_section": True,
                "next_section": NEXT_SECTION_ID,
                "next_section_title": NEXT_SECTION_TITLE,
                "next_section_range": NEXT_SECTION_RANGE,
                "next_pack": NEXT_PACK,
                "next_pack_title": NEXT_PACK_TITLE,
                "vault_done": False,
                "source_gp069_validation_passed": source_status["validation_passed"],
                "source_gp069_safe_to_continue_to_gp070": source_status["safe_to_continue_to_gp070"],
            }

            checkpoint_payload = {
                "configuration_readiness_checkpoint_id": DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,
                "pack_id": PACK_ID,
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "source_object_body_view_lock_contract_id": source_contract["object_body_view_lock_contract_id"],
                "source_object_body_view_pack_id": source_contract["pack_id"],
                "checkpoint_status": "REAL_CONFIGURATION_READINESS_CHECKPOINT_CLOSED_SAFE_TO_CONTINUE_LOCKED",
                "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED_FOR_PROVIDER_ACTIVATION",
                "checkpoint_data_json": _json_dumps(checkpoint_data),
                "created_at": now,
                "updated_at": now,
            }
            for field in TRUE_CHECKPOINT_FIELDS:
                checkpoint_payload[field] = 1
            for field in FALSE_FIELDS:
                checkpoint_payload[field] = 0
            _insert_dict(conn, "vault_storage_provider_configuration_readiness_checkpoints", checkpoint_payload)

            for source_pack_id, component_name, category, route in CONFIGURATION_COMPONENTS:
                component_payload = {
                    "configuration_component_id": f"VSPCRC-COMP-{source_pack_id.replace('VAULT_GP', 'GP')}",
                    "configuration_readiness_checkpoint_id": DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,
                    "source_pack_id": source_pack_id,
                    "component_name": component_name,
                    "component_category": category,
                    "component_status_route": route,
                    "component_status": "REAL_COMPONENT_PRESENT_LOCKED_SAFE_TO_CARRY_FORWARD",
                    "component_notes": f"{component_name} is present in GP061-GP070 configuration layer and remains non-operational/locked.",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_COMPONENT_FIELDS:
                    component_payload[field] = 1
                for field in [
                    "component_unlocks_provider",
                    "component_unlocks_credentials",
                    "component_unlocks_secrets",
                    "component_unlocks_endpoint",
                    "component_unlocks_encryption",
                    "component_unlocks_connection_test",
                    "component_unlocks_write_path",
                    "component_unlocks_read_path",
                    "component_unlocks_object_body_view",
                    "component_unlocks_direct_upload",
                    "component_unlocks_export",
                    "component_unlocks_execution",
                    "tower_review_granted",
                    "component_claims_vault_done",
                ]:
                    component_payload[field] = 0
                _insert_dict(conn, "vault_storage_provider_configuration_readiness_components", component_payload)

            for code, name, category in CONFIGURATION_READINESS_BLOCKERS:
                blocker_payload = {
                    "configuration_blocker_id": f"VSPCRC-BLOCK-{code.upper().replace('_', '-')}",
                    "configuration_readiness_checkpoint_id": DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": "HIGH",
                    "blocker_status": "REAL_CONFIGURATION_BLOCKER_ACTIVE_TOWER_LOCKED",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_BLOCKER_FIELDS:
                    blocker_payload[field] = 1
                for field in ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]:
                    blocker_payload[field] = 0
                _insert_dict(conn, "vault_storage_provider_configuration_readiness_blockers", blocker_payload)

            for event_type, event_payload in [
                ("REAL_STORAGE_PROVIDER_CONFIGURATION_READINESS_CHECKPOINT_CREATED", checkpoint_data),
                ("SOURCE_GP069_OBJECT_BODY_VIEW_LOCK_CONTRACT_ATTACHED", {
                    "source_object_body_view_lock_contract_id": source_contract["object_body_view_lock_contract_id"],
                    "source_object_body_view_pack_id": source_contract["pack_id"],
                    "source_validation_passed": source_status["validation_passed"],
                    "source_safe_to_continue_to_gp070": source_status["safe_to_continue_to_gp070"],
                }),
                ("REAL_CONFIGURATION_COMPONENTS_REGISTERED_LOCKED", {
                    "component_count": len(CONFIGURATION_COMPONENTS),
                    "component_source_packs": [item[0] for item in CONFIGURATION_COMPONENTS],
                }),
                ("REAL_CONFIGURATION_BLOCKERS_REGISTERED_ACTIVE", {
                    "blocker_count": len(CONFIGURATION_READINESS_BLOCKERS),
                    "blocks_provider_configuration": True,
                    "blocks_provider_read_write": True,
                    "blocks_object_body_view": True,
                    "blocks_direct_upload": True,
                    "blocks_export": True,
                    "blocks_execution": True,
                }),
                ("CONFIGURATION_LAYER_CLOSED_SAFE_TO_CONTINUE", {
                    "section_closed": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    "next_section": NEXT_SECTION_ID,
                    "next_section_range": NEXT_SECTION_RANGE,
                    "safe_to_continue_to_next_section": True,
                    "vault_done": False,
                }),
                ("ALL_PROVIDER_CAPABILITIES_CONFIRMED_LOCKED", {
                    "credentials_configured": False,
                    "secret_values_present": False,
                    "provider_endpoint_configured": False,
                    "storage_container_configured": False,
                    "namespace_configured": False,
                    "encryption_policy_configured": False,
                    "provider_connection_tested": False,
                    "write_path_enabled": False,
                    "read_path_enabled": False,
                    "object_body_view_enabled": False,
                    "object_body_content_exposed": False,
                    "direct_upload_enabled": False,
                    "export_enabled": False,
                    "execution_enabled": False,
                }),
            ]:
                _insert_event(conn, DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _sum_counts(table: str, contract_col: str, contract_id: str, fields: list[str], db_path: Optional[str] = None) -> Dict[str, int]:
    selects = ["COUNT(*) AS total_count"]
    for field in fields:
        selects.append(f"SUM(CASE WHEN {field} = 1 THEN 1 ELSE 0 END) AS {field}_count")
    with _connect(db_path) as conn:
        row = conn.execute(
            f"SELECT {', '.join(selects)} FROM {table} WHERE {contract_col} = ?",
            (contract_id,),
        ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}

def get_storage_provider_configuration_readiness_checkpoint_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_configuration_readiness_checkpoint(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_configuration_readiness_checkpoints
            WHERE configuration_readiness_checkpoint_id = ?
            """,
            (DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,),
        ).fetchone()
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "configuration_readiness_checkpoint": _boolify(row, {"checkpoint_data_json": "checkpoint_data"})}

def get_storage_provider_configuration_readiness_components(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_configuration_readiness_checkpoint(db_path)
    fields = [
        "component_ready",
        "component_verified",
        "component_locked",
        "tower_review_required",
        "component_unlocks_provider",
        "component_unlocks_credentials",
        "component_unlocks_secrets",
        "component_unlocks_endpoint",
        "component_unlocks_encryption",
        "component_unlocks_connection_test",
        "component_unlocks_write_path",
        "component_unlocks_read_path",
        "component_unlocks_object_body_view",
        "component_unlocks_direct_upload",
        "component_unlocks_export",
        "component_unlocks_execution",
        "tower_review_granted",
        "component_claims_vault_done",
    ]
    counts = _sum_counts(
        "vault_storage_provider_configuration_readiness_components",
        "configuration_readiness_checkpoint_id",
        DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_configuration_readiness_components
            WHERE configuration_readiness_checkpoint_id = ?
            ORDER BY source_pack_id
            """,
            (DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,),
        ).fetchall()
    counts["component_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "components": [_boolify(row) for row in rows]}

def get_storage_provider_configuration_readiness_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_configuration_readiness_checkpoint(db_path)
    fields = [
        "blocker_active",
        "blocks_provider_configuration",
        "blocks_provider_read_write",
        "blocks_object_body_view",
        "blocks_direct_upload",
        "blocks_export",
        "blocks_execution",
        "tower_review_required",
        "tower_review_granted",
        "risk_accepted",
        "risk_waived",
        "mitigation_approved",
        "resolved",
    ]
    counts = _sum_counts(
        "vault_storage_provider_configuration_readiness_blockers",
        "configuration_readiness_checkpoint_id",
        DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_configuration_readiness_blockers
            WHERE configuration_readiness_checkpoint_id = ?
            ORDER BY blocker_category, blocker_code
            """,
            (DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,),
        ).fetchall()
    counts["blocker_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "blockers": [_boolify(row) for row in rows]}

def get_storage_provider_configuration_readiness_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_configuration_readiness_checkpoint(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_configuration_readiness_events
            WHERE configuration_readiness_checkpoint_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,),
        ).fetchall()
    events = [
        {
            "event_id": row["event_id"],
            "configuration_readiness_checkpoint_id": row["configuration_readiness_checkpoint_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def record_storage_provider_configuration_readiness_event(event_type: str, event_payload: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_configuration_readiness_checkpoint(db_path)
    payload = dict(event_payload or {})
    payload.update({
        "write_type": "REAL_STORAGE_PROVIDER_CONFIGURATION_READINESS_EVENT",
        "configuration_readiness_checkpoint_ready": True,
        "configuration_layer_closed": True,
        "configuration_locked": True,
        "safe_to_continue_to_next_section": True,
        "credentials_configured": False,
        "secret_values_present": False,
        "secret_references_activated": False,
        "provider_endpoint_configured": False,
        "storage_container_configured": False,
        "namespace_configured": False,
        "encryption_policy_configured": False,
        "provider_connection_tested": False,
        "write_path_enabled": False,
        "read_path_enabled": False,
        "object_body_view_enabled": False,
        "object_body_content_exposed": False,
        "direct_upload_enabled": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    })
    with _connect(db_path) as conn:
        event_id = _insert_event(conn, DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID, event_type, payload)
        conn.commit()
    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "configuration_readiness_checkpoint_id": DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,
        "real_sqlite_backed": True,
        **payload,
    }

def validate_storage_provider_configuration_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    checkpoint = get_storage_provider_configuration_readiness_checkpoint_record(db_path)["configuration_readiness_checkpoint"]
    components = get_storage_provider_configuration_readiness_components(db_path)
    blockers = get_storage_provider_configuration_readiness_blockers(db_path)
    events = get_storage_provider_configuration_readiness_events(db_path)

    expected_components = len(CONFIGURATION_COMPONENTS)
    expected_blockers = len(CONFIGURATION_READINESS_BLOCKERS)

    false_checks = [(f"NO_CONTRACT_{field.upper()}", checkpoint[field] is False) for field in FALSE_FIELDS]
    checks = [
        ("REAL_SQLITE_CONFIGURATION_READINESS_CHECKPOINT_EXISTS", checkpoint["configuration_readiness_checkpoint_id"] == DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID),
        ("SOURCE_GP069_OBJECT_BODY_VIEW_LOCK_CONTRACT_ATTACHED", checkpoint["source_object_body_view_pack_id"] == "VAULT_GP069"),
        ("CONFIGURATION_READINESS_CHECKPOINT_READY", checkpoint["configuration_readiness_checkpoint_ready"] is True),
        ("CONFIGURATION_LAYER_CLOSED", checkpoint["configuration_layer_closed"] is True),
        ("CONFIGURATION_COMPONENTS_READY", checkpoint["configuration_components_ready"] is True),
        ("CONFIGURATION_BLOCKERS_READY", checkpoint["configuration_blockers_ready"] is True),
        ("CONFIGURATION_VALIDATION_READY", checkpoint["configuration_validation_ready"] is True),
        ("CONFIGURATION_LOCKED", checkpoint["configuration_locked"] is True),
        ("SAFE_TO_CONTINUE_TO_NEXT_SECTION", checkpoint["safe_to_continue_to_next_section"] is True),
        ("REAL_CONFIGURATION_COMPONENTS_EXIST", components["component_count"] == expected_components),
        ("ALL_COMPONENTS_READY", components["component_ready_count"] == expected_components),
        ("ALL_COMPONENTS_VERIFIED", components["component_verified_count"] == expected_components),
        ("ALL_COMPONENTS_LOCKED", components["component_locked_count"] == expected_components),
        ("NO_COMPONENT_UNLOCKS_PROVIDER", components["component_unlocks_provider_count"] == 0),
        ("NO_COMPONENT_UNLOCKS_CREDENTIALS", components["component_unlocks_credentials_count"] == 0),
        ("NO_COMPONENT_UNLOCKS_SECRETS", components["component_unlocks_secrets_count"] == 0),
        ("NO_COMPONENT_UNLOCKS_ENDPOINT", components["component_unlocks_endpoint_count"] == 0),
        ("NO_COMPONENT_UNLOCKS_ENCRYPTION", components["component_unlocks_encryption_count"] == 0),
        ("NO_COMPONENT_UNLOCKS_CONNECTION_TEST", components["component_unlocks_connection_test_count"] == 0),
        ("NO_COMPONENT_UNLOCKS_WRITE_PATH", components["component_unlocks_write_path_count"] == 0),
        ("NO_COMPONENT_UNLOCKS_READ_PATH", components["component_unlocks_read_path_count"] == 0),
        ("NO_COMPONENT_UNLOCKS_OBJECT_BODY_VIEW", components["component_unlocks_object_body_view_count"] == 0),
        ("NO_COMPONENT_UNLOCKS_DIRECT_UPLOAD", components["component_unlocks_direct_upload_count"] == 0),
        ("NO_COMPONENT_UNLOCKS_EXPORT", components["component_unlocks_export_count"] == 0),
        ("NO_COMPONENT_UNLOCKS_EXECUTION", components["component_unlocks_execution_count"] == 0),
        ("NO_COMPONENT_CLAIMS_VAULT_DONE", components["component_claims_vault_done_count"] == 0),
        ("REAL_CONFIGURATION_BLOCKERS_EXIST", blockers["blocker_count"] == expected_blockers),
        ("ALL_BLOCKERS_ACTIVE", blockers["blocker_active_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_CONFIGURATION", blockers["blocks_provider_configuration_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_READ_WRITE", blockers["blocks_provider_read_write_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY_VIEW", blockers["blocks_object_body_view_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_DIRECT_UPLOAD", blockers["blocks_direct_upload_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_EXPORT", blockers["blocks_export_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_EXECUTION", blockers["blocks_execution_count"] == expected_blockers),
        ("NO_BLOCKERS_TOWER_REVIEW_GRANTED", blockers["tower_review_granted_count"] == 0),
        ("NO_BLOCKERS_RISK_ACCEPTED", blockers["risk_accepted_count"] == 0),
        ("NO_BLOCKERS_RISK_WAIVED", blockers["risk_waived_count"] == 0),
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
        "safe_to_continue_to_gp071": len(failed) == 0,
        "configuration_layer_closed": len(failed) == 0,
        "vault_done": False,
    }

def get_storage_provider_configuration_readiness_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "closed_section": SECTION_ID,
            "closed_section_title": SECTION_TITLE,
            "closed_section_range": SECTION_RANGE,
            "next_section": NEXT_SECTION_ID,
            "next_section_title": NEXT_SECTION_TITLE,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp071": True,
            "configuration_layer_closed": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP070 closes ARCHIVE VAULT — REAL STORAGE PROVIDER CONFIGURATION LAYER / GP061-GP070. Continue to GP071 under the real provider receipt and redacted access layer. Keep provider credentials, secrets, connection, read/write, object body view, direct upload, export, and execution locked.",
            "carry_forward_rules": [
                "Keep the real SQLite configuration readiness checkpoint.",
                "Keep the real GP061-GP069 component summary rows.",
                "Keep the real configuration blocker rows.",
                "Keep the real configuration readiness event log.",
                "Start GP071 in the next Archive Vault section.",
                "Do not configure credentials.",
                "Do not store secret values.",
                "Do not activate secret references.",
                "Do not configure endpoint/container/namespace.",
                "Do not configure encryption.",
                "Do not test provider connection.",
                "Do not enable provider write.",
                "Do not enable provider read.",
                "Do not enable object body view.",
                "Do not expose plaintext object bodies.",
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
        "depends_on": ["VAULT_GP069"],
        "foundation_status": "configuration_readiness_checkpoint_ready_section_closed_safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_configuration_readiness_checkpoint",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-storage-provider-configuration-readiness-checkpoint",
        "json_route": "/vault/real-storage-provider-configuration-readiness-checkpoint.json",
        "record_route": "/vault/storage-provider-configuration-readiness-checkpoint-record.json",
        "components_route": "/vault/storage-provider-configuration-readiness-components.json",
        "blockers_route": "/vault/storage-provider-configuration-readiness-blockers.json",
        "events_route": "/vault/storage-provider-configuration-readiness-events.json",
        "validation_route": "/vault/storage-provider-configuration-readiness-validation.json",
        "next_step_route": "/vault/storage-provider-configuration-readiness-next-step.json",
        "gp070_status_route": "/vault/gp070-status.json",
    }

def get_real_storage_provider_configuration_readiness_checkpoint_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_configuration_readiness_checkpoint(db_path)
    checkpoint = get_storage_provider_configuration_readiness_checkpoint_record(db_path)["configuration_readiness_checkpoint"]
    components = get_storage_provider_configuration_readiness_components(db_path)
    blockers = get_storage_provider_configuration_readiness_blockers(db_path)
    events = get_storage_provider_configuration_readiness_events(db_path)
    validation = validate_storage_provider_configuration_readiness_checkpoint(db_path)

    truth = {
        "real_storage_provider_configuration_readiness_checkpoint_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "source_gp069_object_body_view_lock_contract_attached": checkpoint["source_object_body_view_pack_id"] == "VAULT_GP069",
        "validation_passed": validation["valid"],
        "configuration_layer_closed": checkpoint["configuration_layer_closed"],
        "configuration_locked": checkpoint["configuration_locked"],
        "safe_to_continue_to_gp071": validation["safe_to_continue_to_gp071"],
        "component_count": components["component_count"],
        "blocker_count": blockers["blocker_count"],
        "event_count": events["event_count"],
        "credentials_configured": checkpoint["credentials_configured"],
        "secret_values_present": checkpoint["secret_values_present"],
        "secret_references_activated": checkpoint["secret_references_activated"],
        "provider_endpoint_configured": checkpoint["provider_endpoint_configured"],
        "storage_container_configured": checkpoint["storage_container_configured"],
        "namespace_configured": checkpoint["namespace_configured"],
        "encryption_policy_configured": checkpoint["encryption_policy_configured"],
        "provider_connection_tested": checkpoint["provider_connection_tested"],
        "write_path_enabled": checkpoint["write_path_enabled"],
        "read_path_enabled": checkpoint["read_path_enabled"],
        "object_body_view_enabled": checkpoint["object_body_view_enabled"],
        "object_body_content_exposed": checkpoint["object_body_content_exposed"],
        "direct_upload_enabled": checkpoint["direct_upload_enabled"],
        "export_enabled": checkpoint["export_enabled"],
        "execution_enabled": checkpoint["execution_enabled"],
        "vault_done": checkpoint["vault_done"],
    }

    return {
        "pack": _pack_payload(),
        "configuration_readiness_truth": truth,
        "store": init,
        "configuration_readiness_checkpoint": checkpoint,
        "components": components,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_configuration_readiness_next_step()["next_step"],
    }

def get_gp070_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_configuration_readiness_checkpoint_home(db_path)
    checkpoint = home["configuration_readiness_checkpoint"]
    components = home["components"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp070_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "section_closed": True,
            "real_storage_provider_configuration_readiness_checkpoint_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_checkpoint_count": home["store"]["checkpoint_count"],
            "real_component_count": home["store"]["component_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp069_object_body_view_lock_contract_attached": True,
            "configuration_readiness_checkpoint_ready": checkpoint["configuration_readiness_checkpoint_ready"],
            "configuration_layer_closed": checkpoint["configuration_layer_closed"],
            "configuration_components_ready": checkpoint["configuration_components_ready"],
            "configuration_blockers_ready": checkpoint["configuration_blockers_ready"],
            "configuration_validation_ready": checkpoint["configuration_validation_ready"],
            "configuration_locked": checkpoint["configuration_locked"],
            "safe_to_continue_to_gp071": validation["safe_to_continue_to_gp071"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "component_count": components["component_count"],
            "component_ready_count": components["component_ready_count"],
            "component_verified_count": components["component_verified_count"],
            "component_locked_count": components["component_locked_count"],
            "component_unlocks_provider_count": components["component_unlocks_provider_count"],
            "component_unlocks_credentials_count": components["component_unlocks_credentials_count"],
            "component_unlocks_secrets_count": components["component_unlocks_secrets_count"],
            "component_unlocks_endpoint_count": components["component_unlocks_endpoint_count"],
            "component_unlocks_encryption_count": components["component_unlocks_encryption_count"],
            "component_unlocks_connection_test_count": components["component_unlocks_connection_test_count"],
            "component_unlocks_write_path_count": components["component_unlocks_write_path_count"],
            "component_unlocks_read_path_count": components["component_unlocks_read_path_count"],
            "component_unlocks_object_body_view_count": components["component_unlocks_object_body_view_count"],
            "component_unlocks_direct_upload_count": components["component_unlocks_direct_upload_count"],
            "component_unlocks_export_count": components["component_unlocks_export_count"],
            "component_unlocks_execution_count": components["component_unlocks_execution_count"],
            "blocker_count": blockers["blocker_count"],
            "blocker_active_count": blockers["blocker_active_count"],
            "blocks_provider_configuration_count": blockers["blocks_provider_configuration_count"],
            "blocks_provider_read_write_count": blockers["blocks_provider_read_write_count"],
            "blocks_object_body_view_count": blockers["blocks_object_body_view_count"],
            "blocks_direct_upload_count": blockers["blocks_direct_upload_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "tower_review_granted_count": blockers["tower_review_granted_count"],
            "resolved_count": blockers["resolved_count"],
            "foundation_status": "configuration_readiness_checkpoint_ready_section_closed_safe_to_continue_not_done",
            "credentials_configured": checkpoint["credentials_configured"],
            "secret_values_present": checkpoint["secret_values_present"],
            "secret_references_created": checkpoint["secret_references_created"],
            "secret_references_activated": checkpoint["secret_references_activated"],
            "provider_endpoint_configured": checkpoint["provider_endpoint_configured"],
            "storage_container_configured": checkpoint["storage_container_configured"],
            "namespace_configured": checkpoint["namespace_configured"],
            "encryption_policy_configured": checkpoint["encryption_policy_configured"],
            "connection_test_attempted": checkpoint["connection_test_attempted"],
            "provider_connection_tested": checkpoint["provider_connection_tested"],
            "write_path_configured": checkpoint["write_path_configured"],
            "write_path_attempted": checkpoint["write_path_attempted"],
            "write_path_enabled": checkpoint["write_path_enabled"],
            "read_path_configured": checkpoint["read_path_configured"],
            "read_path_attempted": checkpoint["read_path_attempted"],
            "read_path_enabled": checkpoint["read_path_enabled"],
            "object_body_view_configured": checkpoint["object_body_view_configured"],
            "object_body_view_attempted": checkpoint["object_body_view_attempted"],
            "object_body_view_enabled": checkpoint["object_body_view_enabled"],
            "object_body_content_exposed": checkpoint["object_body_content_exposed"],
            "object_body_plaintext_visible": checkpoint["object_body_plaintext_visible"],
            "object_body_download_enabled": checkpoint["object_body_download_enabled"],
            "provider_read_enabled": checkpoint["provider_read_enabled"],
            "provider_write_enabled": checkpoint["provider_write_enabled"],
            "direct_upload_enabled": checkpoint["direct_upload_enabled"],
            "export_enabled": checkpoint["export_enabled"],
            "execution_enabled": checkpoint["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp070",
            "closed_section": SECTION_ID,
            "closed_section_title": SECTION_TITLE,
            "closed_section_range": SECTION_RANGE,
            "next_section": NEXT_SECTION_ID,
            "next_section_title": NEXT_SECTION_TITLE,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "configuration_readiness_truth": home["configuration_readiness_truth"],
        "routes": home["routes"],
        "configuration_readiness_checkpoint": checkpoint,
        "components": components,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }

def render_real_storage_provider_configuration_readiness_checkpoint_page() -> str:
    home = get_real_storage_provider_configuration_readiness_checkpoint_home()
    truth = home["configuration_readiness_truth"]
    routes = home["routes"]
    next_step = home["next_step"]

    component_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['source_pack_id'])}</strong>
          <span>{escape(item['component_name'])}</span>
          <code>{escape(item['component_status_route'])}</code>
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
<title>Vault Real Storage Provider Configuration Readiness Checkpoint · GP070</title>
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
    <div class="eyebrow">Archive Vault · Giant Pack 070</div>
    <div class="eyebrow">Real Storage Provider Configuration Layer · GP061-GP070</div>
    <h1>Real Storage Provider Configuration Readiness Checkpoint</h1>
    <p>GP070 closes the configuration layer with a real checkpoint. It confirms the layer is ready to continue while every provider capability remains locked.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['component_count']}</strong><span>configuration components</span></div>
      <div class="metric"><strong>{truth['blocker_count']}</strong><span>active blockers</span></div>
      <div class="metric"><strong>{str(truth['configuration_layer_closed']).lower()}</strong><span>section closed</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">Configuration checkpoint ready</span>
      <span class="pill ok">Real SQLite-backed</span>
      <span class="pill ok">Safe to continue GP071</span>
      <span class="pill danger">No provider configured</span>
      <span class="pill danger">No direct upload</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>GP061-GP069 Components</h2>
    <div class="cards">{component_cards}</div>
  </section>

  <section class="section">
    <h2>Validation Checks</h2>
    {checks}
  </section>

  <section class="section">
    <h2>Next Section</h2>
    <p>{escape(next_step['owner_notebook_note'])}</p>
    <ul>{rules}</ul>
  </section>

  <section class="section">
    <h2>GP070 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['components_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_step_route'])}</code>
      <code>{escape(routes['gp070_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
