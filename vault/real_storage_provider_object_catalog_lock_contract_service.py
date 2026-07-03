"""
VAULT GP071 — Real Storage Provider Object Catalog Lock Contract

Current section:
Archive Vault — Real Provider Receipt and Redacted Access Layer / GP071-GP080

This pack starts the next Vault section by creating a real SQLite-backed object
catalog lock contract. It prepares the durable contract that will govern future
catalog/metadata work while explicitly preventing provider object listing,
object metadata import, object body access, direct upload, export, and execution.

It does not call a provider, list objects, read objects, download object bodies,
or create a provider object catalog.
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

from vault.real_storage_provider_configuration_readiness_checkpoint_service import (
    DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,
    get_gp070_status,
    get_storage_provider_configuration_readiness_blockers,
    get_storage_provider_configuration_readiness_checkpoint_record,
    get_storage_provider_configuration_readiness_components,
)

PACK_ID = "VAULT_GP071"
PACK_NAME = "Real Storage Provider Object Catalog Lock Contract"
SCHEMA_VERSION = "vault.real_storage_provider_object_catalog_lock_contract.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Receipt and Redacted Access Layer"
SECTION_RANGE = "GP071-GP080"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
PREVIOUS_SECTION_TITLE = "Archive Vault — Real Storage Provider Configuration Layer"
PREVIOUS_SECTION_RANGE = "GP061-GP070"

NEXT_PACK = "VAULT_GP072_REAL_STORAGE_PROVIDER_REDACTED_METADATA_RECEIPT_CONTRACT"
NEXT_PACK_TITLE = "Real Storage Provider Redacted Metadata Receipt Contract"

DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID = "VSPOCLC-GP071-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_object_catalog_lock_contract.sqlite"

CATALOG_REQUIREMENT_SPECS = [
    ("catalog_lock_record_required", "Catalog lock record required", "catalog_lock"),
    ("tower_catalog_unlock_required", "Tower catalog unlock required", "tower_gate"),
    ("owner_catalog_review_required", "Owner catalog review required", "owner_review"),
    ("metadata_only_catalog_required", "Metadata-only catalog required", "redacted_metadata"),
    ("provider_listing_lock_required", "Provider listing lock required", "provider_listing_lock"),
    ("object_body_boundary_required", "Object body boundary required", "object_body_boundary"),
]

CATALOG_POLICIES = [
    ("no_provider_object_listing_configuration", "No provider object listing configuration", "provider_listing_lock"),
    ("no_provider_object_list_attempt", "No provider object list attempt", "provider_listing_lock"),
    ("no_provider_objects_listed", "No provider objects listed", "provider_listing_lock"),
    ("no_catalog_entries_from_provider", "No catalog entries from provider", "catalog_entry_lock"),
    ("no_provider_object_metadata_import", "No provider object metadata import", "metadata_lock"),
    ("no_object_identifier_collection", "No object identifier collection", "object_identifier_lock"),
    ("no_object_key_collection", "No object key collection", "object_key_lock"),
    ("no_object_etag_size_timestamp_collection", "No object ETag, size, or timestamp collection", "object_metadata_lock"),
    ("no_object_body_read_or_view", "No object body read or view", "object_body_lock"),
    ("no_upload_export_execution_from_catalog", "No upload, export, or execution from catalog", "egress_execution_lock"),
]

FALSE_FIELDS = [
    "object_catalog_configured",
    "object_catalog_attempted",
    "object_catalog_enabled",
    "provider_object_listing_configured",
    "provider_object_list_attempted",
    "provider_objects_listed",
    "catalog_entries_created",
    "provider_object_metadata_imported",
    "object_id_collected",
    "object_key_collected",
    "object_etag_collected",
    "object_size_collected",
    "object_last_modified_collected",
    "object_body_read_attempted",
    "object_body_read",
    "object_body_view_configured",
    "object_body_view_attempted",
    "object_body_view_enabled",
    "object_body_content_exposed",
    "object_body_plaintext_visible",
    "object_body_download_enabled",
    "credentials_configured",
    "secret_values_present",
    "secret_references_activated",
    "provider_endpoint_configured",
    "storage_container_configured",
    "namespace_configured",
    "encryption_policy_configured",
    "provider_connection_tested",
    "write_path_enabled",
    "read_path_enabled",
    "provider_read_enabled",
    "provider_write_enabled",
    "direct_upload_enabled",
    "export_enabled",
    "execution_enabled",
    "vault_done",
]

TRUE_CONTRACT_FIELDS = [
    "object_catalog_lock_contract_ready",
    "object_catalog_requirements_ready",
    "object_catalog_policies_ready",
    "object_catalog_blockers_ready",
    "object_catalog_validation_ready",
    "object_catalog_locked",
    "catalog_metadata_only",
    "catalog_redacted_access_only",
    "source_configuration_checkpoint_attached",
    "safe_to_continue_to_gp072",
]

TRUE_REQUIREMENT_FIELDS = [
    "requirement_required",
    "catalog_locked",
    "metadata_only",
    "redacted_access_only",
    "tower_review_required",
]

TRUE_BLOCKER_FIELDS = [
    "blocker_active",
    "blocks_object_catalog",
    "blocks_provider_listing",
    "blocks_metadata_import",
    "blocks_object_body_view",
    "blocks_provider_read_write",
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
    payload = {}
    for key in row.keys():
        if key in json_fields:
            payload[json_fields[key]] = _json_loads(row[key])
        elif isinstance(row[key], int):
            payload[key] = bool(row[key])
        else:
            payload[key] = row[key]
    return payload

def ensure_storage_provider_object_catalog_lock_contract_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)
        true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_CONTRACT_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_object_catalog_lock_contracts (
                object_catalog_lock_contract_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                previous_section_id TEXT NOT NULL,
                previous_section_range TEXT NOT NULL,
                source_configuration_readiness_checkpoint_id TEXT NOT NULL,
                source_configuration_pack_id TEXT NOT NULL,
                contract_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                contract_data_json TEXT NOT NULL,
                {true_sql},
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        req_false = [
            "requirement_verified",
            "object_catalog_configured",
            "object_catalog_attempted",
            "object_catalog_enabled",
            "provider_object_listing_configured",
            "provider_object_list_attempted",
            "provider_objects_listed",
            "catalog_entries_created",
            "provider_object_metadata_imported",
            "object_id_collected",
            "object_key_collected",
            "object_etag_collected",
            "object_size_collected",
            "object_last_modified_collected",
            "object_body_read",
            "object_body_view_enabled",
            "direct_upload_enabled",
            "export_enabled",
            "execution_enabled",
            "tower_review_granted",
        ]
        req_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_REQUIREMENT_FIELDS)
        req_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in req_false)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_object_catalog_requirements (
                object_catalog_requirement_id TEXT PRIMARY KEY,
                object_catalog_lock_contract_id TEXT NOT NULL,
                source_pack_id TEXT NOT NULL,
                source_component_category TEXT NOT NULL,
                requirement_code TEXT NOT NULL,
                requirement_name TEXT NOT NULL,
                requirement_category TEXT NOT NULL,
                requirement_message TEXT NOT NULL,
                requirement_status TEXT NOT NULL,
                {req_true_sql},
                {req_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(object_catalog_lock_contract_id)
                    REFERENCES vault_storage_provider_object_catalog_lock_contracts(object_catalog_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(object_catalog_lock_contract_id, source_pack_id, requirement_code)
            )
            """
        )

        policy_false = [
            "policy_verified",
            "object_catalog_configured",
            "object_catalog_attempted",
            "object_catalog_enabled",
            "provider_object_listing_configured",
            "provider_object_list_attempted",
            "provider_objects_listed",
            "catalog_entries_created",
            "provider_object_metadata_imported",
            "object_id_collected",
            "object_key_collected",
            "object_etag_collected",
            "object_size_collected",
            "object_last_modified_collected",
            "object_body_read",
            "object_body_view_enabled",
            "object_body_content_exposed",
            "object_body_plaintext_visible",
            "direct_upload_enabled",
            "export_enabled",
            "execution_enabled",
            "tower_review_granted",
        ]
        policy_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in policy_false)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_object_catalog_policies (
                object_catalog_policy_id TEXT PRIMARY KEY,
                object_catalog_lock_contract_id TEXT NOT NULL,
                policy_code TEXT NOT NULL,
                policy_name TEXT NOT NULL,
                policy_category TEXT NOT NULL,
                policy_message TEXT NOT NULL,
                policy_status TEXT NOT NULL,
                policy_required INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                {policy_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(object_catalog_lock_contract_id)
                    REFERENCES vault_storage_provider_object_catalog_lock_contracts(object_catalog_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(object_catalog_lock_contract_id, policy_code)
            )
            """
        )

        blocker_false = [
            "tower_review_granted",
            "risk_accepted",
            "risk_waived",
            "mitigation_approved",
            "resolved",
        ]
        blocker_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_BLOCKER_FIELDS)
        blocker_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in blocker_false)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_object_catalog_blockers (
                object_catalog_blocker_id TEXT PRIMARY KEY,
                object_catalog_lock_contract_id TEXT NOT NULL,
                source_configuration_blocker_id TEXT NOT NULL,
                source_blocker_code TEXT NOT NULL,
                source_blocker_category TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                {blocker_true_sql},
                {blocker_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(object_catalog_lock_contract_id)
                    REFERENCES vault_storage_provider_object_catalog_lock_contracts(object_catalog_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(object_catalog_lock_contract_id, source_configuration_blocker_id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_object_catalog_events (
                event_id TEXT PRIMARY KEY,
                object_catalog_lock_contract_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(object_catalog_lock_contract_id)
                    REFERENCES vault_storage_provider_object_catalog_lock_contracts(object_catalog_lock_contract_id)
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
            "vault_storage_provider_object_catalog_lock_contracts",
            "vault_storage_provider_object_catalog_requirements",
            "vault_storage_provider_object_catalog_policies",
            "vault_storage_provider_object_catalog_blockers",
            "vault_storage_provider_object_catalog_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, contract_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VSPOCLCEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_storage_provider_object_catalog_events",
        {
            "event_id": event_id,
            "object_catalog_lock_contract_id": contract_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "contract_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_object_catalog_lock_contracts").fetchone()["c"]),
            "requirement_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_object_catalog_requirements").fetchone()["c"]),
            "policy_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_object_catalog_policies").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_object_catalog_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_object_catalog_events").fetchone()["c"]),
        }

def initialize_real_storage_provider_object_catalog_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_object_catalog_lock_contract_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            """
            SELECT object_catalog_lock_contract_id
            FROM vault_storage_provider_object_catalog_lock_contracts
            WHERE object_catalog_lock_contract_id = ?
            """,
            (DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,),
        ).fetchone()

        if exists is None:
            source_status_payload = get_gp070_status()
            source_status = source_status_payload["gp070_status"]
            source_checkpoint = get_storage_provider_configuration_readiness_checkpoint_record()["configuration_readiness_checkpoint"]
            source_components = get_storage_provider_configuration_readiness_components()["components"]
            source_blockers = get_storage_provider_configuration_readiness_blockers()["blockers"]
            now = _now_iso()

            contract_data = {
                "schema_version": SCHEMA_VERSION,
                "contract_type": "REAL_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT",
                "source_pack": "VAULT_GP070",
                "source_configuration_readiness_checkpoint_id": source_checkpoint["configuration_readiness_checkpoint_id"],
                "source_configuration_layer_closed": source_status["configuration_layer_closed"],
                "source_safe_to_continue_to_gp071": source_status["safe_to_continue_to_gp071"],
                "section": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "previous_section": PREVIOUS_SECTION_ID,
                "previous_section_range": PREVIOUS_SECTION_RANGE,
                "component_count": len(source_components),
                "catalog_requirement_code_count": len(CATALOG_REQUIREMENT_SPECS),
                "catalog_requirement_count": len(source_components) * len(CATALOG_REQUIREMENT_SPECS),
                "catalog_policy_count": len(CATALOG_POLICIES),
                "carried_configuration_blocker_count": len(source_blockers),
                "object_catalog_locked": True,
                "catalog_metadata_only": True,
                "catalog_redacted_access_only": True,
                "provider_object_listing_configured": False,
                "provider_object_list_attempted": False,
                "provider_objects_listed": False,
                "catalog_entries_created": False,
                "provider_object_metadata_imported": False,
                "object_body_read": False,
                "object_body_view_enabled": False,
                "direct_upload_enabled": False,
                "export_enabled": False,
                "execution_enabled": False,
                "vault_done": False,
                "next_pack": NEXT_PACK,
                "next_pack_title": NEXT_PACK_TITLE,
                "safe_to_continue_to_gp072": True,
            }

            contract_payload = {
                "object_catalog_lock_contract_id": DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,
                "pack_id": PACK_ID,
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "previous_section_id": PREVIOUS_SECTION_ID,
                "previous_section_range": PREVIOUS_SECTION_RANGE,
                "source_configuration_readiness_checkpoint_id": source_checkpoint["configuration_readiness_checkpoint_id"],
                "source_configuration_pack_id": source_checkpoint["pack_id"],
                "contract_status": "REAL_OBJECT_CATALOG_LOCK_CONTRACT_OPEN_TOWER_LOCKED",
                "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED_FOR_OBJECT_CATALOG",
                "contract_data_json": _json_dumps(contract_data),
                "created_at": now,
                "updated_at": now,
            }
            for field in TRUE_CONTRACT_FIELDS:
                contract_payload[field] = 1
            for field in FALSE_FIELDS:
                contract_payload[field] = 0
            _insert_dict(conn, "vault_storage_provider_object_catalog_lock_contracts", contract_payload)

            for component in source_components:
                for code, name, category in CATALOG_REQUIREMENT_SPECS:
                    payload = {
                        "object_catalog_requirement_id": f"VSPOCLR-{component['source_pack_id'].replace('VAULT_', '')}-{code.upper().replace('_', '-')}",
                        "object_catalog_lock_contract_id": DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,
                        "source_pack_id": component["source_pack_id"],
                        "source_component_category": component["component_category"],
                        "requirement_code": code,
                        "requirement_name": name,
                        "requirement_category": category,
                        "requirement_message": f"{name} remains required before provider object catalog access can be considered.",
                        "requirement_status": "REAL_OBJECT_CATALOG_REQUIREMENT_RECORDED_LOCKED_TOWER_LOCKED",
                        "created_at": now,
                        "updated_at": now,
                    }
                    for field in TRUE_REQUIREMENT_FIELDS:
                        payload[field] = 1
                    for field in [
                        "requirement_verified",
                        "object_catalog_configured",
                        "object_catalog_attempted",
                        "object_catalog_enabled",
                        "provider_object_listing_configured",
                        "provider_object_list_attempted",
                        "provider_objects_listed",
                        "catalog_entries_created",
                        "provider_object_metadata_imported",
                        "object_id_collected",
                        "object_key_collected",
                        "object_etag_collected",
                        "object_size_collected",
                        "object_last_modified_collected",
                        "object_body_read",
                        "object_body_view_enabled",
                        "direct_upload_enabled",
                        "export_enabled",
                        "execution_enabled",
                        "tower_review_granted",
                    ]:
                        payload[field] = 0
                    _insert_dict(conn, "vault_storage_provider_object_catalog_requirements", payload)

            for code, name, category in CATALOG_POLICIES:
                payload = {
                    "object_catalog_policy_id": f"VSPOCLP-{code.upper().replace('_', '-')}",
                    "object_catalog_lock_contract_id": DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,
                    "policy_code": code,
                    "policy_name": name,
                    "policy_category": category,
                    "policy_message": f"{name}; GP071 cannot list provider objects, import metadata, expose bodies, export, or execute.",
                    "policy_status": "REAL_OBJECT_CATALOG_POLICY_RECORDED_TOWER_LOCKED",
                    "policy_required": 1,
                    "tower_review_required": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in [
                    "policy_verified",
                    "object_catalog_configured",
                    "object_catalog_attempted",
                    "object_catalog_enabled",
                    "provider_object_listing_configured",
                    "provider_object_list_attempted",
                    "provider_objects_listed",
                    "catalog_entries_created",
                    "provider_object_metadata_imported",
                    "object_id_collected",
                    "object_key_collected",
                    "object_etag_collected",
                    "object_size_collected",
                    "object_last_modified_collected",
                    "object_body_read",
                    "object_body_view_enabled",
                    "object_body_content_exposed",
                    "object_body_plaintext_visible",
                    "direct_upload_enabled",
                    "export_enabled",
                    "execution_enabled",
                    "tower_review_granted",
                ]:
                    payload[field] = 0
                _insert_dict(conn, "vault_storage_provider_object_catalog_policies", payload)

            for blocker in source_blockers:
                payload = {
                    "object_catalog_blocker_id": f"VSPOCLB-{blocker['configuration_blocker_id'].replace('VSPCRC-BLOCK-', '')}",
                    "object_catalog_lock_contract_id": DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,
                    "source_configuration_blocker_id": blocker["configuration_blocker_id"],
                    "source_blocker_code": blocker["blocker_code"],
                    "source_blocker_category": blocker["blocker_category"],
                    "blocker_name": blocker["blocker_name"],
                    "severity": blocker["severity"],
                    "blocker_status": "REAL_OBJECT_CATALOG_BLOCKER_ACTIVE_CARRIED_FROM_GP070",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_BLOCKER_FIELDS:
                    payload[field] = 1
                for field in ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]:
                    payload[field] = 0
                _insert_dict(conn, "vault_storage_provider_object_catalog_blockers", payload)

            for event_type, event_payload in [
                ("REAL_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_CONTRACT_CREATED", contract_data),
                ("SOURCE_GP070_CONFIGURATION_READINESS_CHECKPOINT_ATTACHED", {
                    "source_configuration_readiness_checkpoint_id": source_checkpoint["configuration_readiness_checkpoint_id"],
                    "source_configuration_pack_id": source_checkpoint["pack_id"],
                    "source_section_closed": source_status["section_closed"],
                    "source_safe_to_continue_to_gp071": source_status["safe_to_continue_to_gp071"],
                }),
                ("REAL_OBJECT_CATALOG_REQUIREMENTS_CREATED_LOCKED", {
                    "requirement_count": len(source_components) * len(CATALOG_REQUIREMENT_SPECS),
                    "component_count": len(source_components),
                }),
                ("REAL_OBJECT_CATALOG_POLICIES_CREATED_LOCKED", {
                    "policy_count": len(CATALOG_POLICIES),
                }),
                ("REAL_OBJECT_CATALOG_BLOCKERS_CARRIED_FORWARD", {
                    "blocker_count": len(source_blockers),
                }),
                ("OBJECT_CATALOG_LOCKS_CONFIRMED", {
                    "object_catalog_configured": False,
                    "provider_object_listing_configured": False,
                    "provider_object_list_attempted": False,
                    "provider_objects_listed": False,
                    "catalog_entries_created": False,
                    "provider_object_metadata_imported": False,
                    "object_body_read": False,
                    "object_body_view_enabled": False,
                    "direct_upload_enabled": False,
                    "export_enabled": False,
                    "execution_enabled": False,
                    "vault_done": False,
                }),
            ]:
                _insert_event(conn, DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID, event_type, event_payload)

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

def get_storage_provider_object_catalog_lock_contract_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_object_catalog_lock_contract(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_object_catalog_lock_contracts
            WHERE object_catalog_lock_contract_id = ?
            """,
            (DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,),
        ).fetchone()
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "object_catalog_lock_contract": _boolify(row, {"contract_data_json": "contract_data"})}

def get_storage_provider_object_catalog_requirements(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_object_catalog_lock_contract(db_path)
    fields = [
        "requirement_required",
        "requirement_verified",
        "catalog_locked",
        "metadata_only",
        "redacted_access_only",
        "tower_review_required",
        "tower_review_granted",
        "object_catalog_configured",
        "object_catalog_attempted",
        "object_catalog_enabled",
        "provider_object_listing_configured",
        "provider_object_list_attempted",
        "provider_objects_listed",
        "catalog_entries_created",
        "provider_object_metadata_imported",
        "object_id_collected",
        "object_key_collected",
        "object_etag_collected",
        "object_size_collected",
        "object_last_modified_collected",
        "object_body_read",
        "object_body_view_enabled",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
    ]
    counts = _sum_counts(
        "vault_storage_provider_object_catalog_requirements",
        "object_catalog_lock_contract_id",
        DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_object_catalog_requirements
            WHERE object_catalog_lock_contract_id = ?
            ORDER BY source_pack_id, requirement_category, requirement_code
            """,
            (DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,),
        ).fetchall()
        source_pack_count = conn.execute(
            """
            SELECT COUNT(DISTINCT source_pack_id) AS c
            FROM vault_storage_provider_object_catalog_requirements
            WHERE object_catalog_lock_contract_id = ?
            """,
            (DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]
        requirement_code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT requirement_code) AS c
            FROM vault_storage_provider_object_catalog_requirements
            WHERE object_catalog_lock_contract_id = ?
            """,
            (DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]

    counts["requirement_count"] = counts.pop("total_count")
    counts["source_pack_count"] = int(source_pack_count)
    counts["requirement_code_count"] = int(requirement_code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "requirements": [_boolify(row) for row in rows]}

def get_storage_provider_object_catalog_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_object_catalog_lock_contract(db_path)
    fields = [
        "policy_required",
        "policy_verified",
        "tower_review_required",
        "tower_review_granted",
        "object_catalog_configured",
        "object_catalog_attempted",
        "object_catalog_enabled",
        "provider_object_listing_configured",
        "provider_object_list_attempted",
        "provider_objects_listed",
        "catalog_entries_created",
        "provider_object_metadata_imported",
        "object_id_collected",
        "object_key_collected",
        "object_etag_collected",
        "object_size_collected",
        "object_last_modified_collected",
        "object_body_read",
        "object_body_view_enabled",
        "object_body_content_exposed",
        "object_body_plaintext_visible",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
    ]
    counts = _sum_counts(
        "vault_storage_provider_object_catalog_policies",
        "object_catalog_lock_contract_id",
        DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_object_catalog_policies
            WHERE object_catalog_lock_contract_id = ?
            ORDER BY policy_category, policy_code
            """,
            (DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,),
        ).fetchall()
        policy_code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT policy_code) AS c
            FROM vault_storage_provider_object_catalog_policies
            WHERE object_catalog_lock_contract_id = ?
            """,
            (DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]

    counts["policy_count"] = counts.pop("total_count")
    counts["policy_code_count"] = int(policy_code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "policies": [_boolify(row) for row in rows]}

def get_storage_provider_object_catalog_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_object_catalog_lock_contract(db_path)
    fields = [
        "blocker_active",
        "blocks_object_catalog",
        "blocks_provider_listing",
        "blocks_metadata_import",
        "blocks_object_body_view",
        "blocks_provider_read_write",
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
        "vault_storage_provider_object_catalog_blockers",
        "object_catalog_lock_contract_id",
        DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_object_catalog_blockers
            WHERE object_catalog_lock_contract_id = ?
            ORDER BY source_blocker_category, source_blocker_code
            """,
            (DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,),
        ).fetchall()

    counts["blocker_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "blockers": [_boolify(row) for row in rows]}

def get_storage_provider_object_catalog_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_object_catalog_lock_contract(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_object_catalog_events
            WHERE object_catalog_lock_contract_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,),
        ).fetchall()
    events = [
        {
            "event_id": row["event_id"],
            "object_catalog_lock_contract_id": row["object_catalog_lock_contract_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def record_storage_provider_object_catalog_event(event_type: str, event_payload: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_object_catalog_lock_contract(db_path)
    payload = dict(event_payload or {})
    payload.update({
        "write_type": "REAL_STORAGE_PROVIDER_OBJECT_CATALOG_LOCK_EVENT",
        "object_catalog_lock_contract_ready": True,
        "object_catalog_locked": True,
        "catalog_metadata_only": True,
        "catalog_redacted_access_only": True,
        "object_catalog_configured": False,
        "object_catalog_attempted": False,
        "object_catalog_enabled": False,
        "provider_object_listing_configured": False,
        "provider_object_list_attempted": False,
        "provider_objects_listed": False,
        "catalog_entries_created": False,
        "provider_object_metadata_imported": False,
        "object_body_read": False,
        "object_body_view_enabled": False,
        "direct_upload_enabled": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    })
    with _connect(db_path) as conn:
        event_id = _insert_event(conn, DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID, event_type, payload)
        conn.commit()
    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "object_catalog_lock_contract_id": DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID,
        "real_sqlite_backed": True,
        **payload,
    }

def validate_storage_provider_object_catalog_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    contract = get_storage_provider_object_catalog_lock_contract_record(db_path)["object_catalog_lock_contract"]
    requirements = get_storage_provider_object_catalog_requirements(db_path)
    policies = get_storage_provider_object_catalog_policies(db_path)
    blockers = get_storage_provider_object_catalog_blockers(db_path)
    events = get_storage_provider_object_catalog_events(db_path)

    expected_requirements = 9 * len(CATALOG_REQUIREMENT_SPECS)
    expected_policies = len(CATALOG_POLICIES)
    expected_blockers = 14

    false_checks = [(f"NO_CONTRACT_{field.upper()}", contract[field] is False) for field in FALSE_FIELDS]

    checks = [
        ("REAL_SQLITE_OBJECT_CATALOG_LOCK_CONTRACT_EXISTS", contract["object_catalog_lock_contract_id"] == DEFAULT_OBJECT_CATALOG_LOCK_CONTRACT_ID),
        ("SOURCE_GP070_CONFIGURATION_READINESS_CHECKPOINT_ATTACHED", contract["source_configuration_readiness_checkpoint_id"] == DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID),
        ("OBJECT_CATALOG_LOCK_CONTRACT_READY", contract["object_catalog_lock_contract_ready"] is True),
        ("OBJECT_CATALOG_REQUIREMENTS_READY", contract["object_catalog_requirements_ready"] is True),
        ("OBJECT_CATALOG_POLICIES_READY", contract["object_catalog_policies_ready"] is True),
        ("OBJECT_CATALOG_BLOCKERS_READY", contract["object_catalog_blockers_ready"] is True),
        ("OBJECT_CATALOG_VALIDATION_READY", contract["object_catalog_validation_ready"] is True),
        ("OBJECT_CATALOG_LOCKED", contract["object_catalog_locked"] is True),
        ("CATALOG_METADATA_ONLY", contract["catalog_metadata_only"] is True),
        ("CATALOG_REDACTED_ACCESS_ONLY", contract["catalog_redacted_access_only"] is True),
        ("SAFE_TO_CONTINUE_TO_GP072", contract["safe_to_continue_to_gp072"] is True),
        ("REAL_OBJECT_CATALOG_REQUIREMENTS_EXIST", requirements["requirement_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_REQUIRED", requirements["requirement_required_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_CATALOG_LOCKED", requirements["catalog_locked_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_METADATA_ONLY", requirements["metadata_only_count"] == expected_requirements),
        ("NO_REQUIREMENT_PROVIDER_LISTING_CONFIGURED", requirements["provider_object_listing_configured_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_LIST_ATTEMPTED", requirements["provider_object_list_attempted_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_OBJECTS_LISTED", requirements["provider_objects_listed_count"] == 0),
        ("NO_REQUIREMENT_CATALOG_ENTRIES_CREATED", requirements["catalog_entries_created_count"] == 0),
        ("NO_REQUIREMENT_METADATA_IMPORTED", requirements["provider_object_metadata_imported_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_IDENTIFIERS_COLLECTED", requirements["object_id_collected_count"] == 0 and requirements["object_key_collected_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY_READ", requirements["object_body_read_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY_VIEW", requirements["object_body_view_enabled_count"] == 0),
        ("NO_REQUIREMENT_DIRECT_UPLOAD", requirements["direct_upload_enabled_count"] == 0),
        ("NO_REQUIREMENT_EXPORT", requirements["export_enabled_count"] == 0),
        ("NO_REQUIREMENT_EXECUTION", requirements["execution_enabled_count"] == 0),
        ("REAL_OBJECT_CATALOG_POLICIES_EXIST", policies["policy_count"] == expected_policies),
        ("NO_POLICY_PROVIDER_LISTING_CONFIGURED", policies["provider_object_listing_configured_count"] == 0),
        ("NO_POLICY_PROVIDER_LIST_ATTEMPTED", policies["provider_object_list_attempted_count"] == 0),
        ("NO_POLICY_PROVIDER_OBJECTS_LISTED", policies["provider_objects_listed_count"] == 0),
        ("NO_POLICY_CATALOG_ENTRIES_CREATED", policies["catalog_entries_created_count"] == 0),
        ("NO_POLICY_METADATA_IMPORTED", policies["provider_object_metadata_imported_count"] == 0),
        ("NO_POLICY_OBJECT_BODY_READ", policies["object_body_read_count"] == 0),
        ("NO_POLICY_OBJECT_BODY_CONTENT_EXPOSED", policies["object_body_content_exposed_count"] == 0),
        ("NO_POLICY_DIRECT_UPLOAD", policies["direct_upload_enabled_count"] == 0),
        ("NO_POLICY_EXPORT", policies["export_enabled_count"] == 0),
        ("NO_POLICY_EXECUTION", policies["execution_enabled_count"] == 0),
        ("REAL_OBJECT_CATALOG_BLOCKERS_CARRIED_FORWARD", blockers["blocker_count"] == expected_blockers),
        ("ALL_BLOCKERS_ACTIVE", blockers["blocker_active_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_OBJECT_CATALOG", blockers["blocks_object_catalog_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_LISTING", blockers["blocks_provider_listing_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_METADATA_IMPORT", blockers["blocks_metadata_import_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY_VIEW", blockers["blocks_object_body_view_count"] == expected_blockers),
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
        "safe_to_continue_to_gp072": len(failed) == 0,
        "vault_done": False,
    }

def get_storage_provider_object_catalog_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp072": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP071 begins ARCHIVE VAULT — REAL PROVIDER RECEIPT AND REDACTED ACCESS LAYER / GP071-GP080. Continue to GP072 with a real redacted metadata receipt contract while keeping provider listing, object catalog creation, object body access, direct upload, export, and execution locked.",
            "carry_forward_rules": [
                "Keep the real SQLite object catalog lock contract.",
                "Keep the real object catalog requirement rows.",
                "Keep the real object catalog policy rows.",
                "Keep the real object catalog blocker rows carried from GP070.",
                "Do not configure provider object listing.",
                "Do not attempt provider object listing.",
                "Do not list provider objects.",
                "Do not create provider-backed catalog entries.",
                "Do not import provider object metadata.",
                "Do not collect object IDs, keys, ETags, sizes, or timestamps.",
                "Do not read object bodies.",
                "Do not enable object body view.",
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
        "depends_on": ["VAULT_GP070"],
        "foundation_status": "object_catalog_lock_contract_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_object_catalog_lock_contract",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-storage-provider-object-catalog-lock-contract",
        "json_route": "/vault/real-storage-provider-object-catalog-lock-contract.json",
        "record_route": "/vault/storage-provider-object-catalog-lock-contract-record.json",
        "requirements_route": "/vault/storage-provider-object-catalog-requirements.json",
        "policies_route": "/vault/storage-provider-object-catalog-policies.json",
        "blockers_route": "/vault/storage-provider-object-catalog-blockers.json",
        "events_route": "/vault/storage-provider-object-catalog-events.json",
        "validation_route": "/vault/storage-provider-object-catalog-validation.json",
        "next_step_route": "/vault/storage-provider-object-catalog-next-step.json",
        "gp071_status_route": "/vault/gp071-status.json",
    }

def get_real_storage_provider_object_catalog_lock_contract_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_object_catalog_lock_contract(db_path)
    contract = get_storage_provider_object_catalog_lock_contract_record(db_path)["object_catalog_lock_contract"]
    requirements = get_storage_provider_object_catalog_requirements(db_path)
    policies = get_storage_provider_object_catalog_policies(db_path)
    blockers = get_storage_provider_object_catalog_blockers(db_path)
    events = get_storage_provider_object_catalog_events(db_path)
    validation = validate_storage_provider_object_catalog_lock_contract(db_path)

    truth = {
        "real_storage_provider_object_catalog_lock_contract_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "source_gp070_configuration_readiness_checkpoint_attached": contract["source_configuration_readiness_checkpoint_id"] == DEFAULT_CONFIGURATION_READINESS_CHECKPOINT_ID,
        "validation_passed": validation["valid"],
        "object_catalog_lock_contract_ready": contract["object_catalog_lock_contract_ready"],
        "object_catalog_locked": contract["object_catalog_locked"],
        "catalog_metadata_only": contract["catalog_metadata_only"],
        "catalog_redacted_access_only": contract["catalog_redacted_access_only"],
        "requirement_count": requirements["requirement_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "event_count": events["event_count"],
        "object_catalog_configured": contract["object_catalog_configured"],
        "object_catalog_attempted": contract["object_catalog_attempted"],
        "object_catalog_enabled": contract["object_catalog_enabled"],
        "provider_object_listing_configured": contract["provider_object_listing_configured"],
        "provider_object_list_attempted": contract["provider_object_list_attempted"],
        "provider_objects_listed": contract["provider_objects_listed"],
        "catalog_entries_created": contract["catalog_entries_created"],
        "provider_object_metadata_imported": contract["provider_object_metadata_imported"],
        "object_body_read": contract["object_body_read"],
        "object_body_view_enabled": contract["object_body_view_enabled"],
        "direct_upload_enabled": contract["direct_upload_enabled"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "safe_to_continue_to_gp072": validation["safe_to_continue_to_gp072"],
        "vault_done": contract["vault_done"],
    }

    return {
        "pack": _pack_payload(),
        "object_catalog_truth": truth,
        "store": init,
        "object_catalog_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_object_catalog_next_step()["next_step"],
    }

def get_gp071_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_object_catalog_lock_contract_home(db_path)
    contract = home["object_catalog_lock_contract"]
    requirements = home["requirements"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp071_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_object_catalog_lock_contract_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_contract_count": home["store"]["contract_count"],
            "real_requirement_count": home["store"]["requirement_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp070_configuration_readiness_checkpoint_attached": True,
            "object_catalog_lock_contract_ready": contract["object_catalog_lock_contract_ready"],
            "object_catalog_requirements_ready": contract["object_catalog_requirements_ready"],
            "object_catalog_policies_ready": contract["object_catalog_policies_ready"],
            "object_catalog_blockers_ready": contract["object_catalog_blockers_ready"],
            "object_catalog_validation_ready": contract["object_catalog_validation_ready"],
            "object_catalog_locked": contract["object_catalog_locked"],
            "catalog_metadata_only": contract["catalog_metadata_only"],
            "catalog_redacted_access_only": contract["catalog_redacted_access_only"],
            "source_pack_count": requirements["source_pack_count"],
            "requirement_code_count": requirements["requirement_code_count"],
            "policy_code_count": policies["policy_code_count"],
            "blocker_count": blockers["blocker_count"],
            "provider_object_listing_configured_count": requirements["provider_object_listing_configured_count"] + policies["provider_object_listing_configured_count"],
            "provider_object_list_attempted_count": requirements["provider_object_list_attempted_count"] + policies["provider_object_list_attempted_count"],
            "provider_objects_listed_count": requirements["provider_objects_listed_count"] + policies["provider_objects_listed_count"],
            "catalog_entries_created_count": requirements["catalog_entries_created_count"] + policies["catalog_entries_created_count"],
            "provider_object_metadata_imported_count": requirements["provider_object_metadata_imported_count"] + policies["provider_object_metadata_imported_count"],
            "object_body_read_count": requirements["object_body_read_count"] + policies["object_body_read_count"],
            "object_body_view_enabled_count": requirements["object_body_view_enabled_count"] + policies["object_body_view_enabled_count"],
            "direct_upload_enabled_count": requirements["direct_upload_enabled_count"] + policies["direct_upload_enabled_count"],
            "export_enabled_count": requirements["export_enabled_count"] + policies["export_enabled_count"],
            "execution_enabled_count": requirements["execution_enabled_count"] + policies["execution_enabled_count"],
            "blocks_object_catalog_count": blockers["blocks_object_catalog_count"],
            "blocks_provider_listing_count": blockers["blocks_provider_listing_count"],
            "blocks_metadata_import_count": blockers["blocks_metadata_import_count"],
            "blocks_object_body_view_count": blockers["blocks_object_body_view_count"],
            "blocks_provider_read_write_count": blockers["blocks_provider_read_write_count"],
            "blocks_direct_upload_count": blockers["blocks_direct_upload_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "tower_review_granted_count": blockers["tower_review_granted_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp072": validation["safe_to_continue_to_gp072"],
            "foundation_status": "object_catalog_lock_contract_ready_safe_to_continue_not_done",
            "object_catalog_configured": contract["object_catalog_configured"],
            "object_catalog_attempted": contract["object_catalog_attempted"],
            "object_catalog_enabled": contract["object_catalog_enabled"],
            "provider_object_listing_configured": contract["provider_object_listing_configured"],
            "provider_object_list_attempted": contract["provider_object_list_attempted"],
            "provider_objects_listed": contract["provider_objects_listed"],
            "catalog_entries_created": contract["catalog_entries_created"],
            "provider_object_metadata_imported": contract["provider_object_metadata_imported"],
            "object_id_collected": contract["object_id_collected"],
            "object_key_collected": contract["object_key_collected"],
            "object_etag_collected": contract["object_etag_collected"],
            "object_size_collected": contract["object_size_collected"],
            "object_last_modified_collected": contract["object_last_modified_collected"],
            "object_body_read": contract["object_body_read"],
            "object_body_view_enabled": contract["object_body_view_enabled"],
            "object_body_content_exposed": contract["object_body_content_exposed"],
            "object_body_plaintext_visible": contract["object_body_plaintext_visible"],
            "object_body_download_enabled": contract["object_body_download_enabled"],
            "read_path_enabled": contract["read_path_enabled"],
            "provider_read_enabled": contract["provider_read_enabled"],
            "provider_write_enabled": contract["provider_write_enabled"],
            "direct_upload_enabled": contract["direct_upload_enabled"],
            "export_enabled": contract["export_enabled"],
            "execution_enabled": contract["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp071",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "object_catalog_truth": home["object_catalog_truth"],
        "routes": home["routes"],
        "object_catalog_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }

def render_real_storage_provider_object_catalog_lock_contract_page() -> str:
    home = get_real_storage_provider_object_catalog_lock_contract_home()
    truth = home["object_catalog_truth"]
    routes = home["routes"]
    next_step = home["next_step"]

    requirement_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['source_pack_id'])}</strong>
          <span>{escape(item['requirement_name'])}</span>
          <code>{escape(item['requirement_code'])}</code>
        </article>
        """
        for item in home["requirements"]["requirements"][:12]
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
<title>Vault Real Storage Provider Object Catalog Lock Contract · GP071</title>
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
    <div class="eyebrow">Archive Vault · Giant Pack 071</div>
    <div class="eyebrow">Real Provider Receipt and Redacted Access Layer · GP071-GP080</div>
    <h1>Real Storage Provider Object Catalog Lock Contract</h1>
    <p>GP071 creates a real object catalog lock contract. It does not list provider objects, import provider metadata, read object bodies, export, or execute.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['requirement_count']}</strong><span>catalog requirements</span></div>
      <div class="metric"><strong>{truth['policy_count']}</strong><span>catalog policies</span></div>
      <div class="metric"><strong>{truth['provider_objects_listed']}</strong><span>objects listed</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">Object catalog lock ready</span>
      <span class="pill ok">Real SQLite-backed</span>
      <span class="pill danger">No provider listing</span>
      <span class="pill danger">No metadata import</span>
      <span class="pill danger">No body read</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Catalog Requirements Preview</h2>
    <div class="cards">{requirement_cards}</div>
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
    <h2>GP071 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['requirements_route'])}</code>
      <code>{escape(routes['policies_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_step_route'])}</code>
      <code>{escape(routes['gp071_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
