"""
VAULT GP074 — Real Storage Provider Redacted Access View Lock Contract

Current section:
Archive Vault — Real Provider Receipt and Redacted Access Layer / GP071-GP080

This pack creates a real SQLite-backed redacted access view lock contract
sourced from GP073. It prepares durable view rules for future redacted access
review while keeping live provider views, provider metadata views, object
identifier display, object body display, direct upload, export, and execution
locked.

It does not call a provider, list objects, import metadata, render provider
data, display object identifiers, display object bodies, download, upload,
export, or execute.
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

from vault.real_storage_provider_receipt_lineage_lock_contract_service import (
    DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,
    get_gp073_status,
    get_storage_provider_receipt_lineage_blockers,
    get_storage_provider_receipt_lineage_lock_contract_record,
    get_storage_provider_receipt_lineage_policies,
    get_storage_provider_receipt_lineage_requirements,
)

PACK_ID = "VAULT_GP074"
PACK_NAME = "Real Storage Provider Redacted Access View Lock Contract"
SCHEMA_VERSION = "vault.real_storage_provider_redacted_access_view_lock_contract.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Receipt and Redacted Access Layer"
SECTION_RANGE = "GP071-GP080"

NEXT_PACK = "VAULT_GP075_REAL_STORAGE_PROVIDER_OWNER_REVIEW_PACKET_LOCK_CONTRACT"
NEXT_PACK_TITLE = "Real Storage Provider Owner Review Packet Lock Contract"

DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID = "VSPRAVLC-GP074-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_redacted_access_view_lock_contract.sqlite"

VIEW_REQUIREMENT_SPECS = [
    ("redacted_access_view_lock_record_required", "Redacted access view lock record required", "view_lock"),
    ("source_lineage_contract_link_required", "Source lineage contract link required", "source_lineage"),
    ("view_template_only_required", "View template-only state required", "template_only"),
    ("view_field_redaction_required", "View field redaction required", "field_redaction"),
    ("owner_access_review_required", "Owner access review required", "owner_review"),
    ("tower_view_unlock_required", "Tower view unlock required", "tower_gate"),
    ("object_body_display_boundary_required", "Object body display boundary required", "object_body_boundary"),
]

VIEW_POLICIES = [
    ("no_live_provider_access_view", "No live provider access view", "live_view_lock"),
    ("no_provider_object_view", "No provider object view", "object_view_lock"),
    ("no_provider_metadata_view", "No provider metadata view", "metadata_view_lock"),
    ("no_provider_receipt_lineage_view", "No provider receipt lineage view", "lineage_view_lock"),
    ("no_object_identifier_display", "No object identifier display", "identifier_display_lock"),
    ("no_object_key_display", "No object key display", "object_key_display_lock"),
    ("no_etag_size_timestamp_display", "No ETag, size, or timestamp display", "metadata_display_lock"),
    ("no_object_body_display", "No object body display", "object_body_display_lock"),
    ("no_plaintext_or_download_from_view", "No plaintext or download from view", "download_lock"),
    ("no_export_or_execution_from_view", "No export or execution from view", "egress_execution_lock"),
]

FALSE_FIELDS = [
    "redacted_access_view_configured",
    "redacted_access_view_attempted",
    "redacted_access_view_enabled",
    "redacted_access_view_rendered",
    "redacted_access_view_published",
    "live_provider_access_view_created",
    "provider_object_view_created",
    "provider_metadata_view_created",
    "provider_receipt_lineage_view_created",
    "object_identifier_displayed",
    "object_key_displayed",
    "object_etag_displayed",
    "object_size_displayed",
    "object_timestamp_displayed",
    "object_body_displayed",
    "plaintext_view_enabled",
    "view_download_enabled",
    "receipt_lineage_created",
    "receipt_lineage_finalized",
    "lineage_hash_computed",
    "lineage_hash_chained",
    "provider_derived_lineage_created",
    "provider_metadata_lineage_created",
    "object_identifier_lineage_created",
    "object_body_lineage_content_created",
    "redacted_metadata_receipt_created",
    "redacted_metadata_receipt_finalized",
    "provider_metadata_imported",
    "provider_metadata_read_attempted",
    "provider_metadata_read",
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
    "read_path_enabled",
    "provider_read_enabled",
    "provider_write_enabled",
    "direct_upload_enabled",
    "export_enabled",
    "execution_enabled",
    "vault_done",
]

TRUE_CONTRACT_FIELDS = [
    "redacted_access_view_lock_contract_ready",
    "redacted_access_view_requirements_ready",
    "redacted_access_view_policies_ready",
    "redacted_access_view_blockers_ready",
    "redacted_access_view_validation_ready",
    "redacted_access_view_locked",
    "view_template_only",
    "view_redaction_required",
    "source_receipt_lineage_lock_contract_attached",
    "safe_to_continue_to_gp075",
]

TRUE_REQUIREMENT_FIELDS = [
    "requirement_required",
    "view_locked",
    "template_only",
    "view_redaction_required",
    "tower_review_required",
]

TRUE_BLOCKER_FIELDS = [
    "blocker_active",
    "blocks_redacted_access_view",
    "blocks_live_provider_view",
    "blocks_provider_metadata_view",
    "blocks_object_identifier_display",
    "blocks_object_body_display",
    "blocks_plaintext_view",
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

def ensure_storage_provider_redacted_access_view_lock_contract_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)
        true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_CONTRACT_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_redacted_access_view_lock_contracts (
                redacted_access_view_lock_contract_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_receipt_lineage_lock_contract_id TEXT NOT NULL,
                source_receipt_lineage_pack_id TEXT NOT NULL,
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
            "redacted_access_view_configured",
            "redacted_access_view_attempted",
            "redacted_access_view_enabled",
            "redacted_access_view_rendered",
            "redacted_access_view_published",
            "live_provider_access_view_created",
            "provider_object_view_created",
            "provider_metadata_view_created",
            "provider_receipt_lineage_view_created",
            "object_identifier_displayed",
            "object_key_displayed",
            "object_etag_displayed",
            "object_size_displayed",
            "object_timestamp_displayed",
            "object_body_displayed",
            "plaintext_view_enabled",
            "view_download_enabled",
            "provider_metadata_imported",
            "provider_metadata_read",
            "provider_objects_listed",
            "object_id_collected",
            "object_key_collected",
            "object_body_read",
            "object_body_view_enabled",
            "object_body_content_exposed",
            "direct_upload_enabled",
            "export_enabled",
            "execution_enabled",
            "tower_review_granted",
        ]
        req_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_REQUIREMENT_FIELDS)
        req_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in req_false)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_redacted_access_view_requirements (
                redacted_access_view_requirement_id TEXT PRIMARY KEY,
                redacted_access_view_lock_contract_id TEXT NOT NULL,
                source_requirement_id TEXT NOT NULL,
                source_pack_id TEXT NOT NULL,
                source_requirement_code TEXT NOT NULL,
                requirement_code TEXT NOT NULL,
                requirement_name TEXT NOT NULL,
                requirement_category TEXT NOT NULL,
                requirement_message TEXT NOT NULL,
                requirement_status TEXT NOT NULL,
                {req_true_sql},
                {req_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(redacted_access_view_lock_contract_id)
                    REFERENCES vault_storage_provider_redacted_access_view_lock_contracts(redacted_access_view_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(redacted_access_view_lock_contract_id, source_requirement_id, requirement_code)
            )
            """
        )

        policy_false = [
            "policy_verified",
            "redacted_access_view_configured",
            "redacted_access_view_attempted",
            "redacted_access_view_enabled",
            "redacted_access_view_rendered",
            "redacted_access_view_published",
            "live_provider_access_view_created",
            "provider_object_view_created",
            "provider_metadata_view_created",
            "provider_receipt_lineage_view_created",
            "object_identifier_displayed",
            "object_key_displayed",
            "object_etag_displayed",
            "object_size_displayed",
            "object_timestamp_displayed",
            "object_body_displayed",
            "plaintext_view_enabled",
            "view_download_enabled",
            "provider_metadata_imported",
            "provider_metadata_read",
            "provider_objects_listed",
            "object_id_collected",
            "object_key_collected",
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_redacted_access_view_policies (
                redacted_access_view_policy_id TEXT PRIMARY KEY,
                redacted_access_view_lock_contract_id TEXT NOT NULL,
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
                FOREIGN KEY(redacted_access_view_lock_contract_id)
                    REFERENCES vault_storage_provider_redacted_access_view_lock_contracts(redacted_access_view_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(redacted_access_view_lock_contract_id, policy_code)
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_redacted_access_view_blockers (
                redacted_access_view_blocker_id TEXT PRIMARY KEY,
                redacted_access_view_lock_contract_id TEXT NOT NULL,
                source_receipt_lineage_blocker_id TEXT NOT NULL,
                source_blocker_code TEXT NOT NULL,
                source_blocker_category TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                {blocker_true_sql},
                {blocker_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(redacted_access_view_lock_contract_id)
                    REFERENCES vault_storage_provider_redacted_access_view_lock_contracts(redacted_access_view_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(redacted_access_view_lock_contract_id, source_receipt_lineage_blocker_id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_redacted_access_view_events (
                event_id TEXT PRIMARY KEY,
                redacted_access_view_lock_contract_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(redacted_access_view_lock_contract_id)
                    REFERENCES vault_storage_provider_redacted_access_view_lock_contracts(redacted_access_view_lock_contract_id)
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
            "vault_storage_provider_redacted_access_view_lock_contracts",
            "vault_storage_provider_redacted_access_view_requirements",
            "vault_storage_provider_redacted_access_view_policies",
            "vault_storage_provider_redacted_access_view_blockers",
            "vault_storage_provider_redacted_access_view_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, contract_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VSPRAVLCEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_storage_provider_redacted_access_view_events",
        {
            "event_id": event_id,
            "redacted_access_view_lock_contract_id": contract_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "contract_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_redacted_access_view_lock_contracts").fetchone()["c"]),
            "requirement_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_redacted_access_view_requirements").fetchone()["c"]),
            "policy_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_redacted_access_view_policies").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_redacted_access_view_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_redacted_access_view_events").fetchone()["c"]),
        }

def initialize_real_storage_provider_redacted_access_view_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_redacted_access_view_lock_contract_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            """
            SELECT redacted_access_view_lock_contract_id
            FROM vault_storage_provider_redacted_access_view_lock_contracts
            WHERE redacted_access_view_lock_contract_id = ?
            """,
            (DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,),
        ).fetchone()

        if exists is None:
            source_status_payload = get_gp073_status()
            source_status = source_status_payload["gp073_status"]
            source_contract = get_storage_provider_receipt_lineage_lock_contract_record()["receipt_lineage_lock_contract"]
            source_requirements = get_storage_provider_receipt_lineage_requirements()["requirements"]
            source_policies = get_storage_provider_receipt_lineage_policies()["policies"]
            source_blockers = get_storage_provider_receipt_lineage_blockers()["blockers"]
            now = _now_iso()

            requirement_seed = source_requirements[:63]

            contract_data = {
                "schema_version": SCHEMA_VERSION,
                "contract_type": "REAL_STORAGE_PROVIDER_REDACTED_ACCESS_VIEW_LOCK_CONTRACT",
                "source_pack": "VAULT_GP073",
                "source_receipt_lineage_lock_contract_id": source_contract["receipt_lineage_lock_contract_id"],
                "source_receipt_lineage_validation_passed": source_status["validation_passed"],
                "source_safe_to_continue_to_gp074": source_status["safe_to_continue_to_gp074"],
                "section": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "view_requirement_seed_count": len(requirement_seed),
                "view_requirement_code_count": len(VIEW_REQUIREMENT_SPECS),
                "view_requirement_count": len(requirement_seed) * len(VIEW_REQUIREMENT_SPECS),
                "view_policy_count": len(VIEW_POLICIES),
                "carried_receipt_lineage_blocker_count": len(source_blockers),
                "source_receipt_lineage_policy_count": len(source_policies),
                "redacted_access_view_locked": True,
                "view_template_only": True,
                "view_redaction_required": True,
                "redacted_access_view_rendered": False,
                "live_provider_access_view_created": False,
                "provider_object_view_created": False,
                "provider_metadata_view_created": False,
                "provider_receipt_lineage_view_created": False,
                "object_identifier_displayed": False,
                "object_key_displayed": False,
                "object_body_displayed": False,
                "plaintext_view_enabled": False,
                "view_download_enabled": False,
                "direct_upload_enabled": False,
                "export_enabled": False,
                "execution_enabled": False,
                "vault_done": False,
                "next_pack": NEXT_PACK,
                "next_pack_title": NEXT_PACK_TITLE,
                "safe_to_continue_to_gp075": True,
            }

            contract_payload = {
                "redacted_access_view_lock_contract_id": DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,
                "pack_id": PACK_ID,
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "source_receipt_lineage_lock_contract_id": source_contract["receipt_lineage_lock_contract_id"],
                "source_receipt_lineage_pack_id": source_contract["pack_id"],
                "contract_status": "REAL_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_OPEN_TEMPLATE_ONLY_TOWER_LOCKED",
                "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED_FOR_REDACTED_ACCESS_VIEW",
                "contract_data_json": _json_dumps(contract_data),
                "created_at": now,
                "updated_at": now,
            }
            for field in TRUE_CONTRACT_FIELDS:
                contract_payload[field] = 1
            for field in FALSE_FIELDS:
                contract_payload[field] = 0
            _insert_dict(conn, "vault_storage_provider_redacted_access_view_lock_contracts", contract_payload)

            for source_requirement in requirement_seed:
                for code, name, category in VIEW_REQUIREMENT_SPECS:
                    payload = {
                        "redacted_access_view_requirement_id": f"VSPRAVR-{source_requirement['receipt_lineage_requirement_id'].replace('VSPRLLR-', '')}-{code.upper().replace('_', '-')}",
                        "redacted_access_view_lock_contract_id": DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,
                        "source_requirement_id": source_requirement["receipt_lineage_requirement_id"],
                        "source_pack_id": source_requirement["source_pack_id"],
                        "source_requirement_code": source_requirement["requirement_code"],
                        "requirement_code": code,
                        "requirement_name": name,
                        "requirement_category": category,
                        "requirement_message": f"{name} remains required before a provider-backed redacted access view can be considered.",
                        "requirement_status": "REAL_REDACTED_ACCESS_VIEW_REQUIREMENT_RECORDED_TEMPLATE_ONLY_TOWER_LOCKED",
                        "created_at": now,
                        "updated_at": now,
                    }
                    for field in TRUE_REQUIREMENT_FIELDS:
                        payload[field] = 1
                    for field in [
                        "requirement_verified",
                        "redacted_access_view_configured",
                        "redacted_access_view_attempted",
                        "redacted_access_view_enabled",
                        "redacted_access_view_rendered",
                        "redacted_access_view_published",
                        "live_provider_access_view_created",
                        "provider_object_view_created",
                        "provider_metadata_view_created",
                        "provider_receipt_lineage_view_created",
                        "object_identifier_displayed",
                        "object_key_displayed",
                        "object_etag_displayed",
                        "object_size_displayed",
                        "object_timestamp_displayed",
                        "object_body_displayed",
                        "plaintext_view_enabled",
                        "view_download_enabled",
                        "provider_metadata_imported",
                        "provider_metadata_read",
                        "provider_objects_listed",
                        "object_id_collected",
                        "object_key_collected",
                        "object_body_read",
                        "object_body_view_enabled",
                        "object_body_content_exposed",
                        "direct_upload_enabled",
                        "export_enabled",
                        "execution_enabled",
                        "tower_review_granted",
                    ]:
                        payload[field] = 0
                    _insert_dict(conn, "vault_storage_provider_redacted_access_view_requirements", payload)

            for code, name, category in VIEW_POLICIES:
                payload = {
                    "redacted_access_view_policy_id": f"VSPRAVP-{code.upper().replace('_', '-')}",
                    "redacted_access_view_lock_contract_id": DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,
                    "policy_code": code,
                    "policy_name": name,
                    "policy_category": category,
                    "policy_message": f"{name}; GP074 cannot render provider data, display identifiers, expose bodies, download, export, or execute.",
                    "policy_status": "REAL_REDACTED_ACCESS_VIEW_POLICY_RECORDED_TEMPLATE_ONLY_TOWER_LOCKED",
                    "policy_required": 1,
                    "tower_review_required": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in [
                    "policy_verified",
                    "redacted_access_view_configured",
                    "redacted_access_view_attempted",
                    "redacted_access_view_enabled",
                    "redacted_access_view_rendered",
                    "redacted_access_view_published",
                    "live_provider_access_view_created",
                    "provider_object_view_created",
                    "provider_metadata_view_created",
                    "provider_receipt_lineage_view_created",
                    "object_identifier_displayed",
                    "object_key_displayed",
                    "object_etag_displayed",
                    "object_size_displayed",
                    "object_timestamp_displayed",
                    "object_body_displayed",
                    "plaintext_view_enabled",
                    "view_download_enabled",
                    "provider_metadata_imported",
                    "provider_metadata_read",
                    "provider_objects_listed",
                    "object_id_collected",
                    "object_key_collected",
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
                _insert_dict(conn, "vault_storage_provider_redacted_access_view_policies", payload)

            for blocker in source_blockers:
                payload = {
                    "redacted_access_view_blocker_id": f"VSPRAVB-{blocker['receipt_lineage_blocker_id'].replace('VSPRLLB-', '')}",
                    "redacted_access_view_lock_contract_id": DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,
                    "source_receipt_lineage_blocker_id": blocker["receipt_lineage_blocker_id"],
                    "source_blocker_code": blocker["source_blocker_code"],
                    "source_blocker_category": blocker["source_blocker_category"],
                    "blocker_name": blocker["blocker_name"],
                    "severity": blocker["severity"],
                    "blocker_status": "REAL_REDACTED_ACCESS_VIEW_BLOCKER_ACTIVE_CARRIED_FROM_GP073",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_BLOCKER_FIELDS:
                    payload[field] = 1
                for field in ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]:
                    payload[field] = 0
                _insert_dict(conn, "vault_storage_provider_redacted_access_view_blockers", payload)

            for event_type, event_payload in [
                ("REAL_STORAGE_PROVIDER_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_CREATED", contract_data),
                ("SOURCE_GP073_RECEIPT_LINEAGE_LOCK_CONTRACT_ATTACHED", {
                    "source_receipt_lineage_lock_contract_id": source_contract["receipt_lineage_lock_contract_id"],
                    "source_receipt_lineage_pack_id": source_contract["pack_id"],
                    "source_validation_passed": source_status["validation_passed"],
                    "source_safe_to_continue_to_gp074": source_status["safe_to_continue_to_gp074"],
                }),
                ("REAL_REDACTED_ACCESS_VIEW_REQUIREMENTS_CREATED_TEMPLATE_ONLY", {
                    "requirement_count": len(requirement_seed) * len(VIEW_REQUIREMENT_SPECS),
                    "requirement_seed_count": len(requirement_seed),
                }),
                ("REAL_REDACTED_ACCESS_VIEW_POLICIES_CREATED_TEMPLATE_ONLY", {
                    "policy_count": len(VIEW_POLICIES),
                }),
                ("REAL_REDACTED_ACCESS_VIEW_BLOCKERS_CARRIED_FORWARD", {
                    "blocker_count": len(source_blockers),
                }),
                ("REDACTED_ACCESS_VIEW_LOCKS_CONFIRMED", {
                    "redacted_access_view_rendered": False,
                    "live_provider_access_view_created": False,
                    "provider_object_view_created": False,
                    "provider_metadata_view_created": False,
                    "provider_receipt_lineage_view_created": False,
                    "object_identifier_displayed": False,
                    "object_key_displayed": False,
                    "object_body_displayed": False,
                    "plaintext_view_enabled": False,
                    "view_download_enabled": False,
                    "direct_upload_enabled": False,
                    "export_enabled": False,
                    "execution_enabled": False,
                    "vault_done": False,
                }),
            ]:
                _insert_event(conn, DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID, event_type, event_payload)

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

def get_storage_provider_redacted_access_view_lock_contract_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_redacted_access_view_lock_contract(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_redacted_access_view_lock_contracts
            WHERE redacted_access_view_lock_contract_id = ?
            """,
            (DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,),
        ).fetchone()
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "redacted_access_view_lock_contract": _boolify(row, {"contract_data_json": "contract_data"})}

def get_storage_provider_redacted_access_view_requirements(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_redacted_access_view_lock_contract(db_path)
    fields = [
        "requirement_required",
        "requirement_verified",
        "view_locked",
        "template_only",
        "view_redaction_required",
        "tower_review_required",
        "tower_review_granted",
        "redacted_access_view_configured",
        "redacted_access_view_attempted",
        "redacted_access_view_enabled",
        "redacted_access_view_rendered",
        "redacted_access_view_published",
        "live_provider_access_view_created",
        "provider_object_view_created",
        "provider_metadata_view_created",
        "provider_receipt_lineage_view_created",
        "object_identifier_displayed",
        "object_key_displayed",
        "object_etag_displayed",
        "object_size_displayed",
        "object_timestamp_displayed",
        "object_body_displayed",
        "plaintext_view_enabled",
        "view_download_enabled",
        "provider_metadata_imported",
        "provider_metadata_read",
        "provider_objects_listed",
        "object_id_collected",
        "object_key_collected",
        "object_body_read",
        "object_body_view_enabled",
        "object_body_content_exposed",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
    ]
    counts = _sum_counts(
        "vault_storage_provider_redacted_access_view_requirements",
        "redacted_access_view_lock_contract_id",
        DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_redacted_access_view_requirements
            WHERE redacted_access_view_lock_contract_id = ?
            ORDER BY source_requirement_id, requirement_category, requirement_code
            """,
            (DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,),
        ).fetchall()
        source_requirement_count = conn.execute(
            """
            SELECT COUNT(DISTINCT source_requirement_id) AS c
            FROM vault_storage_provider_redacted_access_view_requirements
            WHERE redacted_access_view_lock_contract_id = ?
            """,
            (DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]
        requirement_code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT requirement_code) AS c
            FROM vault_storage_provider_redacted_access_view_requirements
            WHERE redacted_access_view_lock_contract_id = ?
            """,
            (DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]

    counts["requirement_count"] = counts.pop("total_count")
    counts["source_requirement_count"] = int(source_requirement_count)
    counts["requirement_code_count"] = int(requirement_code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "requirements": [_boolify(row) for row in rows]}

def get_storage_provider_redacted_access_view_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_redacted_access_view_lock_contract(db_path)
    fields = [
        "policy_required",
        "policy_verified",
        "tower_review_required",
        "tower_review_granted",
        "redacted_access_view_configured",
        "redacted_access_view_attempted",
        "redacted_access_view_enabled",
        "redacted_access_view_rendered",
        "redacted_access_view_published",
        "live_provider_access_view_created",
        "provider_object_view_created",
        "provider_metadata_view_created",
        "provider_receipt_lineage_view_created",
        "object_identifier_displayed",
        "object_key_displayed",
        "object_etag_displayed",
        "object_size_displayed",
        "object_timestamp_displayed",
        "object_body_displayed",
        "plaintext_view_enabled",
        "view_download_enabled",
        "provider_metadata_imported",
        "provider_metadata_read",
        "provider_objects_listed",
        "object_id_collected",
        "object_key_collected",
        "object_body_read",
        "object_body_view_enabled",
        "object_body_content_exposed",
        "object_body_plaintext_visible",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
    ]
    counts = _sum_counts(
        "vault_storage_provider_redacted_access_view_policies",
        "redacted_access_view_lock_contract_id",
        DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_redacted_access_view_policies
            WHERE redacted_access_view_lock_contract_id = ?
            ORDER BY policy_category, policy_code
            """,
            (DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,),
        ).fetchall()
        policy_code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT policy_code) AS c
            FROM vault_storage_provider_redacted_access_view_policies
            WHERE redacted_access_view_lock_contract_id = ?
            """,
            (DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]

    counts["policy_count"] = counts.pop("total_count")
    counts["policy_code_count"] = int(policy_code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "policies": [_boolify(row) for row in rows]}

def get_storage_provider_redacted_access_view_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_redacted_access_view_lock_contract(db_path)
    fields = [
        "blocker_active",
        "blocks_redacted_access_view",
        "blocks_live_provider_view",
        "blocks_provider_metadata_view",
        "blocks_object_identifier_display",
        "blocks_object_body_display",
        "blocks_plaintext_view",
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
        "vault_storage_provider_redacted_access_view_blockers",
        "redacted_access_view_lock_contract_id",
        DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_redacted_access_view_blockers
            WHERE redacted_access_view_lock_contract_id = ?
            ORDER BY source_blocker_category, source_blocker_code
            """,
            (DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,),
        ).fetchall()

    counts["blocker_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "blockers": [_boolify(row) for row in rows]}

def get_storage_provider_redacted_access_view_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_redacted_access_view_lock_contract(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_redacted_access_view_events
            WHERE redacted_access_view_lock_contract_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,),
        ).fetchall()
    events = [
        {
            "event_id": row["event_id"],
            "redacted_access_view_lock_contract_id": row["redacted_access_view_lock_contract_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def record_storage_provider_redacted_access_view_event(event_type: str, event_payload: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_redacted_access_view_lock_contract(db_path)
    payload = dict(event_payload or {})
    payload.update({
        "write_type": "REAL_STORAGE_PROVIDER_REDACTED_ACCESS_VIEW_LOCK_EVENT",
        "redacted_access_view_lock_contract_ready": True,
        "redacted_access_view_locked": True,
        "view_template_only": True,
        "view_redaction_required": True,
        "redacted_access_view_rendered": False,
        "redacted_access_view_published": False,
        "live_provider_access_view_created": False,
        "provider_object_view_created": False,
        "provider_metadata_view_created": False,
        "provider_receipt_lineage_view_created": False,
        "object_identifier_displayed": False,
        "object_key_displayed": False,
        "object_body_displayed": False,
        "plaintext_view_enabled": False,
        "view_download_enabled": False,
        "provider_metadata_imported": False,
        "provider_metadata_read": False,
        "provider_objects_listed": False,
        "object_id_collected": False,
        "object_key_collected": False,
        "object_body_read": False,
        "object_body_view_enabled": False,
        "direct_upload_enabled": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    })
    with _connect(db_path) as conn:
        event_id = _insert_event(conn, DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID, event_type, payload)
        conn.commit()
    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "redacted_access_view_lock_contract_id": DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID,
        "real_sqlite_backed": True,
        **payload,
    }

def validate_storage_provider_redacted_access_view_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    contract = get_storage_provider_redacted_access_view_lock_contract_record(db_path)["redacted_access_view_lock_contract"]
    requirements = get_storage_provider_redacted_access_view_requirements(db_path)
    policies = get_storage_provider_redacted_access_view_policies(db_path)
    blockers = get_storage_provider_redacted_access_view_blockers(db_path)
    events = get_storage_provider_redacted_access_view_events(db_path)

    expected_requirements = 63 * len(VIEW_REQUIREMENT_SPECS)
    expected_policies = len(VIEW_POLICIES)
    expected_blockers = 14

    false_checks = [(f"NO_CONTRACT_{field.upper()}", contract[field] is False) for field in FALSE_FIELDS]

    checks = [
        ("REAL_SQLITE_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_EXISTS", contract["redacted_access_view_lock_contract_id"] == DEFAULT_REDACTED_ACCESS_VIEW_LOCK_CONTRACT_ID),
        ("SOURCE_GP073_RECEIPT_LINEAGE_LOCK_CONTRACT_ATTACHED", contract["source_receipt_lineage_lock_contract_id"] == DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID),
        ("REDACTED_ACCESS_VIEW_LOCK_CONTRACT_READY", contract["redacted_access_view_lock_contract_ready"] is True),
        ("REDACTED_ACCESS_VIEW_REQUIREMENTS_READY", contract["redacted_access_view_requirements_ready"] is True),
        ("REDACTED_ACCESS_VIEW_POLICIES_READY", contract["redacted_access_view_policies_ready"] is True),
        ("REDACTED_ACCESS_VIEW_BLOCKERS_READY", contract["redacted_access_view_blockers_ready"] is True),
        ("REDACTED_ACCESS_VIEW_VALIDATION_READY", contract["redacted_access_view_validation_ready"] is True),
        ("REDACTED_ACCESS_VIEW_LOCKED", contract["redacted_access_view_locked"] is True),
        ("VIEW_TEMPLATE_ONLY", contract["view_template_only"] is True),
        ("VIEW_REDACTION_REQUIRED", contract["view_redaction_required"] is True),
        ("SAFE_TO_CONTINUE_TO_GP075", contract["safe_to_continue_to_gp075"] is True),
        ("REAL_REDACTED_ACCESS_VIEW_REQUIREMENTS_EXIST", requirements["requirement_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_REQUIRED", requirements["requirement_required_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_VIEW_LOCKED", requirements["view_locked_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_TEMPLATE_ONLY", requirements["template_only_count"] == expected_requirements),
        ("NO_REQUIREMENT_VIEW_RENDERED", requirements["redacted_access_view_rendered_count"] == 0),
        ("NO_REQUIREMENT_VIEW_PUBLISHED", requirements["redacted_access_view_published_count"] == 0),
        ("NO_REQUIREMENT_LIVE_PROVIDER_VIEW", requirements["live_provider_access_view_created_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_OBJECT_VIEW", requirements["provider_object_view_created_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_METADATA_VIEW", requirements["provider_metadata_view_created_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_LINEAGE_VIEW", requirements["provider_receipt_lineage_view_created_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_IDENTIFIER_DISPLAY", requirements["object_identifier_displayed_count"] == 0 and requirements["object_key_displayed_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_METADATA_DISPLAY", requirements["object_etag_displayed_count"] == 0 and requirements["object_size_displayed_count"] == 0 and requirements["object_timestamp_displayed_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY_DISPLAY", requirements["object_body_displayed_count"] == 0),
        ("NO_REQUIREMENT_PLAINTEXT_OR_DOWNLOAD", requirements["plaintext_view_enabled_count"] == 0 and requirements["view_download_enabled_count"] == 0),
        ("NO_REQUIREMENT_DIRECT_UPLOAD", requirements["direct_upload_enabled_count"] == 0),
        ("NO_REQUIREMENT_EXPORT", requirements["export_enabled_count"] == 0),
        ("NO_REQUIREMENT_EXECUTION", requirements["execution_enabled_count"] == 0),
        ("REAL_REDACTED_ACCESS_VIEW_POLICIES_EXIST", policies["policy_count"] == expected_policies),
        ("NO_POLICY_VIEW_RENDERED", policies["redacted_access_view_rendered_count"] == 0),
        ("NO_POLICY_LIVE_PROVIDER_VIEW", policies["live_provider_access_view_created_count"] == 0),
        ("NO_POLICY_PROVIDER_METADATA_VIEW", policies["provider_metadata_view_created_count"] == 0),
        ("NO_POLICY_OBJECT_IDENTIFIER_DISPLAY", policies["object_identifier_displayed_count"] == 0 and policies["object_key_displayed_count"] == 0),
        ("NO_POLICY_OBJECT_BODY_DISPLAY", policies["object_body_displayed_count"] == 0),
        ("NO_POLICY_OBJECT_BODY_CONTENT_EXPOSED", policies["object_body_content_exposed_count"] == 0),
        ("NO_POLICY_PLAINTEXT_OR_DOWNLOAD", policies["plaintext_view_enabled_count"] == 0 and policies["view_download_enabled_count"] == 0),
        ("NO_POLICY_DIRECT_UPLOAD", policies["direct_upload_enabled_count"] == 0),
        ("NO_POLICY_EXPORT", policies["export_enabled_count"] == 0),
        ("NO_POLICY_EXECUTION", policies["execution_enabled_count"] == 0),
        ("REAL_REDACTED_ACCESS_VIEW_BLOCKERS_CARRIED_FORWARD", blockers["blocker_count"] == expected_blockers),
        ("ALL_BLOCKERS_ACTIVE", blockers["blocker_active_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_REDACTED_ACCESS_VIEW", blockers["blocks_redacted_access_view_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_LIVE_PROVIDER_VIEW", blockers["blocks_live_provider_view_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_METADATA_VIEW", blockers["blocks_provider_metadata_view_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_OBJECT_IDENTIFIER_DISPLAY", blockers["blocks_object_identifier_display_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY_DISPLAY", blockers["blocks_object_body_display_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PLAINTEXT_VIEW", blockers["blocks_plaintext_view_count"] == expected_blockers),
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
        "safe_to_continue_to_gp075": len(failed) == 0,
        "vault_done": False,
    }

def get_storage_provider_redacted_access_view_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp075": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP074 adds the real redacted access view lock contract in template-only mode. Continue to GP075 with the owner review packet lock contract while keeping live provider views, metadata views, object identifiers, object bodies, direct upload, export, and execution locked.",
            "carry_forward_rules": [
                "Keep the real SQLite redacted access view lock contract.",
                "Keep real redacted access view requirement rows.",
                "Keep real redacted access view policy rows.",
                "Keep real blocker rows carried from GP073.",
                "Do not create a live provider access view.",
                "Do not create provider object views.",
                "Do not create provider metadata views.",
                "Do not render receipt lineage from provider data.",
                "Do not display object IDs, keys, ETags, sizes, or timestamps.",
                "Do not display object bodies.",
                "Do not enable plaintext view.",
                "Do not enable view download.",
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
        "depends_on": ["VAULT_GP073"],
        "foundation_status": "redacted_access_view_lock_contract_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_redacted_access_view_lock_contract",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-storage-provider-redacted-access-view-lock-contract",
        "json_route": "/vault/real-storage-provider-redacted-access-view-lock-contract.json",
        "record_route": "/vault/storage-provider-redacted-access-view-lock-contract-record.json",
        "requirements_route": "/vault/storage-provider-redacted-access-view-requirements.json",
        "policies_route": "/vault/storage-provider-redacted-access-view-policies.json",
        "blockers_route": "/vault/storage-provider-redacted-access-view-blockers.json",
        "events_route": "/vault/storage-provider-redacted-access-view-events.json",
        "validation_route": "/vault/storage-provider-redacted-access-view-validation.json",
        "next_step_route": "/vault/storage-provider-redacted-access-view-next-step.json",
        "gp074_status_route": "/vault/gp074-status.json",
    }

def get_real_storage_provider_redacted_access_view_lock_contract_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_redacted_access_view_lock_contract(db_path)
    contract = get_storage_provider_redacted_access_view_lock_contract_record(db_path)["redacted_access_view_lock_contract"]
    requirements = get_storage_provider_redacted_access_view_requirements(db_path)
    policies = get_storage_provider_redacted_access_view_policies(db_path)
    blockers = get_storage_provider_redacted_access_view_blockers(db_path)
    events = get_storage_provider_redacted_access_view_events(db_path)
    validation = validate_storage_provider_redacted_access_view_lock_contract(db_path)

    truth = {
        "real_storage_provider_redacted_access_view_lock_contract_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "source_gp073_receipt_lineage_lock_contract_attached": contract["source_receipt_lineage_lock_contract_id"] == DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,
        "validation_passed": validation["valid"],
        "redacted_access_view_lock_contract_ready": contract["redacted_access_view_lock_contract_ready"],
        "redacted_access_view_locked": contract["redacted_access_view_locked"],
        "view_template_only": contract["view_template_only"],
        "view_redaction_required": contract["view_redaction_required"],
        "requirement_count": requirements["requirement_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "event_count": events["event_count"],
        "redacted_access_view_rendered": contract["redacted_access_view_rendered"],
        "live_provider_access_view_created": contract["live_provider_access_view_created"],
        "provider_object_view_created": contract["provider_object_view_created"],
        "provider_metadata_view_created": contract["provider_metadata_view_created"],
        "provider_receipt_lineage_view_created": contract["provider_receipt_lineage_view_created"],
        "object_identifier_displayed": contract["object_identifier_displayed"],
        "object_key_displayed": contract["object_key_displayed"],
        "object_body_displayed": contract["object_body_displayed"],
        "plaintext_view_enabled": contract["plaintext_view_enabled"],
        "view_download_enabled": contract["view_download_enabled"],
        "object_body_read": contract["object_body_read"],
        "object_body_view_enabled": contract["object_body_view_enabled"],
        "direct_upload_enabled": contract["direct_upload_enabled"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "safe_to_continue_to_gp075": validation["safe_to_continue_to_gp075"],
        "vault_done": contract["vault_done"],
    }

    return {
        "pack": _pack_payload(),
        "redacted_access_view_truth": truth,
        "store": init,
        "redacted_access_view_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_redacted_access_view_next_step()["next_step"],
    }

def get_gp074_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_redacted_access_view_lock_contract_home(db_path)
    contract = home["redacted_access_view_lock_contract"]
    requirements = home["requirements"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp074_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_redacted_access_view_lock_contract_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_contract_count": home["store"]["contract_count"],
            "real_requirement_count": home["store"]["requirement_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp073_receipt_lineage_lock_contract_attached": True,
            "redacted_access_view_lock_contract_ready": contract["redacted_access_view_lock_contract_ready"],
            "redacted_access_view_requirements_ready": contract["redacted_access_view_requirements_ready"],
            "redacted_access_view_policies_ready": contract["redacted_access_view_policies_ready"],
            "redacted_access_view_blockers_ready": contract["redacted_access_view_blockers_ready"],
            "redacted_access_view_validation_ready": contract["redacted_access_view_validation_ready"],
            "redacted_access_view_locked": contract["redacted_access_view_locked"],
            "view_template_only": contract["view_template_only"],
            "view_redaction_required": contract["view_redaction_required"],
            "source_requirement_count": requirements["source_requirement_count"],
            "requirement_code_count": requirements["requirement_code_count"],
            "policy_code_count": policies["policy_code_count"],
            "blocker_count": blockers["blocker_count"],
            "redacted_access_view_rendered_count": requirements["redacted_access_view_rendered_count"] + policies["redacted_access_view_rendered_count"],
            "redacted_access_view_published_count": requirements["redacted_access_view_published_count"] + policies["redacted_access_view_published_count"],
            "live_provider_access_view_created_count": requirements["live_provider_access_view_created_count"] + policies["live_provider_access_view_created_count"],
            "provider_object_view_created_count": requirements["provider_object_view_created_count"] + policies["provider_object_view_created_count"],
            "provider_metadata_view_created_count": requirements["provider_metadata_view_created_count"] + policies["provider_metadata_view_created_count"],
            "provider_receipt_lineage_view_created_count": requirements["provider_receipt_lineage_view_created_count"] + policies["provider_receipt_lineage_view_created_count"],
            "object_identifier_displayed_count": requirements["object_identifier_displayed_count"] + policies["object_identifier_displayed_count"],
            "object_key_displayed_count": requirements["object_key_displayed_count"] + policies["object_key_displayed_count"],
            "object_etag_displayed_count": requirements["object_etag_displayed_count"] + policies["object_etag_displayed_count"],
            "object_size_displayed_count": requirements["object_size_displayed_count"] + policies["object_size_displayed_count"],
            "object_timestamp_displayed_count": requirements["object_timestamp_displayed_count"] + policies["object_timestamp_displayed_count"],
            "object_body_displayed_count": requirements["object_body_displayed_count"] + policies["object_body_displayed_count"],
            "plaintext_view_enabled_count": requirements["plaintext_view_enabled_count"] + policies["plaintext_view_enabled_count"],
            "view_download_enabled_count": requirements["view_download_enabled_count"] + policies["view_download_enabled_count"],
            "direct_upload_enabled_count": requirements["direct_upload_enabled_count"] + policies["direct_upload_enabled_count"],
            "export_enabled_count": requirements["export_enabled_count"] + policies["export_enabled_count"],
            "execution_enabled_count": requirements["execution_enabled_count"] + policies["execution_enabled_count"],
            "blocks_redacted_access_view_count": blockers["blocks_redacted_access_view_count"],
            "blocks_live_provider_view_count": blockers["blocks_live_provider_view_count"],
            "blocks_provider_metadata_view_count": blockers["blocks_provider_metadata_view_count"],
            "blocks_object_identifier_display_count": blockers["blocks_object_identifier_display_count"],
            "blocks_object_body_display_count": blockers["blocks_object_body_display_count"],
            "blocks_plaintext_view_count": blockers["blocks_plaintext_view_count"],
            "blocks_direct_upload_count": blockers["blocks_direct_upload_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "tower_review_granted_count": blockers["tower_review_granted_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp075": validation["safe_to_continue_to_gp075"],
            "foundation_status": "redacted_access_view_lock_contract_ready_safe_to_continue_not_done",
            "redacted_access_view_configured": contract["redacted_access_view_configured"],
            "redacted_access_view_attempted": contract["redacted_access_view_attempted"],
            "redacted_access_view_enabled": contract["redacted_access_view_enabled"],
            "redacted_access_view_rendered": contract["redacted_access_view_rendered"],
            "redacted_access_view_published": contract["redacted_access_view_published"],
            "live_provider_access_view_created": contract["live_provider_access_view_created"],
            "provider_object_view_created": contract["provider_object_view_created"],
            "provider_metadata_view_created": contract["provider_metadata_view_created"],
            "provider_receipt_lineage_view_created": contract["provider_receipt_lineage_view_created"],
            "object_identifier_displayed": contract["object_identifier_displayed"],
            "object_key_displayed": contract["object_key_displayed"],
            "object_etag_displayed": contract["object_etag_displayed"],
            "object_size_displayed": contract["object_size_displayed"],
            "object_timestamp_displayed": contract["object_timestamp_displayed"],
            "object_body_displayed": contract["object_body_displayed"],
            "plaintext_view_enabled": contract["plaintext_view_enabled"],
            "view_download_enabled": contract["view_download_enabled"],
            "provider_metadata_imported": contract["provider_metadata_imported"],
            "provider_metadata_read": contract["provider_metadata_read"],
            "provider_objects_listed": contract["provider_objects_listed"],
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
            "clouds_status": "parked_do_not_continue_from_vault_gp074",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "redacted_access_view_truth": home["redacted_access_view_truth"],
        "routes": home["routes"],
        "redacted_access_view_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }

def render_real_storage_provider_redacted_access_view_lock_contract_page() -> str:
    home = get_real_storage_provider_redacted_access_view_lock_contract_home()
    truth = home["redacted_access_view_truth"]
    routes = home["routes"]
    next_step = home["next_step"]

    requirement_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['source_requirement_code'])}</strong>
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
<title>Vault Real Storage Provider Redacted Access View Lock Contract · GP074</title>
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
    <div class="eyebrow">Archive Vault · Giant Pack 074</div>
    <div class="eyebrow">Real Provider Receipt and Redacted Access Layer · GP071-GP080</div>
    <h1>Real Storage Provider Redacted Access View Lock Contract</h1>
    <p>GP074 creates a real redacted access view lock contract in template-only mode. It does not render provider data, display identifiers, expose bodies, export, or execute.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['requirement_count']}</strong><span>view requirements</span></div>
      <div class="metric"><strong>{truth['policy_count']}</strong><span>view policies</span></div>
      <div class="metric"><strong>{truth['redacted_access_view_rendered']}</strong><span>view rendered</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">View contract ready</span>
      <span class="pill ok">Template-only</span>
      <span class="pill ok">Real SQLite-backed</span>
      <span class="pill danger">No live provider view</span>
      <span class="pill danger">No identifiers displayed</span>
      <span class="pill danger">No body display</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Redacted Access View Requirements Preview</h2>
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
    <h2>GP074 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['requirements_route'])}</code>
      <code>{escape(routes['policies_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_step_route'])}</code>
      <code>{escape(routes['gp074_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
