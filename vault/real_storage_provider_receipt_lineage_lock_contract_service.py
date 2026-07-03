"""
VAULT GP073 — Real Storage Provider Receipt Lineage Lock Contract

Current section:
Archive Vault — Real Provider Receipt and Redacted Access Layer / GP071-GP080

This pack creates a real SQLite-backed receipt lineage lock contract sourced
from GP072. It prepares durable lineage rules for future receipt chaining while
keeping provider-derived lineage, receipt finalization, provider metadata,
object identifiers, object body access, direct upload, export, and execution
locked.

It does not call a provider, list objects, import metadata, collect object
identifiers, create lineage from provider data, hash provider-derived receipt
chains, finalize receipts, read object bodies, upload, export, or execute.
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

from vault.real_storage_provider_redacted_metadata_receipt_contract_service import (
    DEFAULT_REDACTED_METADATA_RECEIPT_CONTRACT_ID,
    get_gp072_status,
    get_storage_provider_redacted_metadata_receipt_blockers,
    get_storage_provider_redacted_metadata_receipt_contract_record,
    get_storage_provider_redacted_metadata_receipt_policies,
    get_storage_provider_redacted_metadata_receipt_requirements,
)

PACK_ID = "VAULT_GP073"
PACK_NAME = "Real Storage Provider Receipt Lineage Lock Contract"
SCHEMA_VERSION = "vault.real_storage_provider_receipt_lineage_lock_contract.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Receipt and Redacted Access Layer"
SECTION_RANGE = "GP071-GP080"

NEXT_PACK = "VAULT_GP074_REAL_STORAGE_PROVIDER_REDACTED_ACCESS_VIEW_LOCK_CONTRACT"
NEXT_PACK_TITLE = "Real Storage Provider Redacted Access View Lock Contract"

DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID = "VSPRLLC-GP073-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_CONTRACT_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_receipt_lineage_lock_contract.sqlite"

LINEAGE_REQUIREMENT_SPECS = [
    ("receipt_lineage_lock_record_required", "Receipt lineage lock record required", "lineage_lock"),
    ("source_receipt_contract_link_required", "Source receipt contract link required", "source_contract"),
    ("lineage_hash_plan_required", "Lineage hash plan required", "lineage_hash"),
    ("parent_child_receipt_rules_required", "Parent/child receipt rules required", "parent_child_rules"),
    ("lineage_redaction_boundary_required", "Lineage redaction boundary required", "redaction_boundary"),
    ("tower_lineage_unlock_required", "Tower lineage unlock required", "tower_gate"),
    ("owner_lineage_review_required", "Owner lineage review required", "owner_review"),
]

LINEAGE_POLICIES = [
    ("no_provider_derived_lineage_creation", "No provider-derived lineage creation", "provider_lineage_lock"),
    ("no_receipt_lineage_finalization", "No receipt lineage finalization", "lineage_finalization_lock"),
    ("no_receipt_hash_chain_from_provider", "No receipt hash chain from provider", "lineage_hash_lock"),
    ("no_parent_receipt_attachment", "No parent receipt attachment", "parent_child_lock"),
    ("no_child_receipt_attachment", "No child receipt attachment", "parent_child_lock"),
    ("no_provider_metadata_lineage", "No provider metadata lineage", "metadata_lineage_lock"),
    ("no_object_identifier_lineage", "No object identifier lineage", "identifier_lineage_lock"),
    ("no_object_body_lineage_content", "No object body lineage content", "object_body_lock"),
    ("no_export_from_lineage_contract", "No export from lineage contract", "export_lock"),
    ("no_execution_from_lineage_contract", "No execution from lineage contract", "execution_lock"),
]

FALSE_FIELDS = [
    "receipt_lineage_configured",
    "receipt_lineage_attempted",
    "receipt_lineage_enabled",
    "receipt_lineage_created",
    "receipt_lineage_finalized",
    "lineage_hash_plan_approved",
    "lineage_hash_computed",
    "lineage_hash_chained",
    "parent_receipt_attached",
    "child_receipt_attached",
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
    "receipt_lineage_lock_contract_ready",
    "receipt_lineage_requirements_ready",
    "receipt_lineage_policies_ready",
    "receipt_lineage_blockers_ready",
    "receipt_lineage_validation_ready",
    "receipt_lineage_locked",
    "lineage_template_only",
    "lineage_redaction_required",
    "source_redacted_metadata_receipt_contract_attached",
    "safe_to_continue_to_gp074",
]

TRUE_REQUIREMENT_FIELDS = [
    "requirement_required",
    "lineage_locked",
    "template_only",
    "lineage_redaction_required",
    "tower_review_required",
]

TRUE_BLOCKER_FIELDS = [
    "blocker_active",
    "blocks_receipt_lineage",
    "blocks_provider_derived_lineage",
    "blocks_receipt_finalization",
    "blocks_lineage_hash_chain",
    "blocks_object_identifier_lineage",
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
    payload = {}
    for key in row.keys():
        if key in json_fields:
            payload[json_fields[key]] = _json_loads(row[key])
        elif isinstance(row[key], int):
            payload[key] = bool(row[key])
        else:
            payload[key] = row[key]
    return payload

def ensure_storage_provider_receipt_lineage_lock_contract_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)
        true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_CONTRACT_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_receipt_lineage_lock_contracts (
                receipt_lineage_lock_contract_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_redacted_metadata_receipt_contract_id TEXT NOT NULL,
                source_redacted_metadata_pack_id TEXT NOT NULL,
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
            "receipt_lineage_configured",
            "receipt_lineage_attempted",
            "receipt_lineage_enabled",
            "receipt_lineage_created",
            "receipt_lineage_finalized",
            "lineage_hash_plan_approved",
            "lineage_hash_computed",
            "lineage_hash_chained",
            "parent_receipt_attached",
            "child_receipt_attached",
            "provider_derived_lineage_created",
            "provider_metadata_lineage_created",
            "object_identifier_lineage_created",
            "object_body_lineage_content_created",
            "redacted_metadata_receipt_created",
            "provider_metadata_imported",
            "provider_metadata_read",
            "provider_objects_listed",
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_receipt_lineage_requirements (
                receipt_lineage_requirement_id TEXT PRIMARY KEY,
                receipt_lineage_lock_contract_id TEXT NOT NULL,
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
                FOREIGN KEY(receipt_lineage_lock_contract_id)
                    REFERENCES vault_storage_provider_receipt_lineage_lock_contracts(receipt_lineage_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(receipt_lineage_lock_contract_id, source_requirement_id, requirement_code)
            )
            """
        )

        policy_false = [
            "policy_verified",
            "receipt_lineage_configured",
            "receipt_lineage_attempted",
            "receipt_lineage_enabled",
            "receipt_lineage_created",
            "receipt_lineage_finalized",
            "lineage_hash_plan_approved",
            "lineage_hash_computed",
            "lineage_hash_chained",
            "parent_receipt_attached",
            "child_receipt_attached",
            "provider_derived_lineage_created",
            "provider_metadata_lineage_created",
            "object_identifier_lineage_created",
            "object_body_lineage_content_created",
            "redacted_metadata_receipt_created",
            "provider_metadata_imported",
            "provider_metadata_read",
            "provider_objects_listed",
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_receipt_lineage_policies (
                receipt_lineage_policy_id TEXT PRIMARY KEY,
                receipt_lineage_lock_contract_id TEXT NOT NULL,
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
                FOREIGN KEY(receipt_lineage_lock_contract_id)
                    REFERENCES vault_storage_provider_receipt_lineage_lock_contracts(receipt_lineage_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(receipt_lineage_lock_contract_id, policy_code)
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_receipt_lineage_blockers (
                receipt_lineage_blocker_id TEXT PRIMARY KEY,
                receipt_lineage_lock_contract_id TEXT NOT NULL,
                source_redacted_metadata_blocker_id TEXT NOT NULL,
                source_blocker_code TEXT NOT NULL,
                source_blocker_category TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                {blocker_true_sql},
                {blocker_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(receipt_lineage_lock_contract_id)
                    REFERENCES vault_storage_provider_receipt_lineage_lock_contracts(receipt_lineage_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(receipt_lineage_lock_contract_id, source_redacted_metadata_blocker_id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_receipt_lineage_events (
                event_id TEXT PRIMARY KEY,
                receipt_lineage_lock_contract_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(receipt_lineage_lock_contract_id)
                    REFERENCES vault_storage_provider_receipt_lineage_lock_contracts(receipt_lineage_lock_contract_id)
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
            "vault_storage_provider_receipt_lineage_lock_contracts",
            "vault_storage_provider_receipt_lineage_requirements",
            "vault_storage_provider_receipt_lineage_policies",
            "vault_storage_provider_receipt_lineage_blockers",
            "vault_storage_provider_receipt_lineage_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, contract_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VSPRLLCEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_storage_provider_receipt_lineage_events",
        {
            "event_id": event_id,
            "receipt_lineage_lock_contract_id": contract_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "contract_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_receipt_lineage_lock_contracts").fetchone()["c"]),
            "requirement_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_receipt_lineage_requirements").fetchone()["c"]),
            "policy_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_receipt_lineage_policies").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_receipt_lineage_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_receipt_lineage_events").fetchone()["c"]),
        }

def initialize_real_storage_provider_receipt_lineage_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_receipt_lineage_lock_contract_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            """
            SELECT receipt_lineage_lock_contract_id
            FROM vault_storage_provider_receipt_lineage_lock_contracts
            WHERE receipt_lineage_lock_contract_id = ?
            """,
            (DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,),
        ).fetchone()

        if exists is None:
            source_status_payload = get_gp072_status()
            source_status = source_status_payload["gp072_status"]
            source_contract = get_storage_provider_redacted_metadata_receipt_contract_record()["redacted_metadata_receipt_contract"]
            source_requirements = get_storage_provider_redacted_metadata_receipt_requirements()["requirements"]
            source_policies = get_storage_provider_redacted_metadata_receipt_policies()["policies"]
            source_blockers = get_storage_provider_redacted_metadata_receipt_blockers()["blockers"]
            now = _now_iso()

            requirement_seed = source_requirements

            contract_data = {
                "schema_version": SCHEMA_VERSION,
                "contract_type": "REAL_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_CONTRACT",
                "source_pack": "VAULT_GP072",
                "source_redacted_metadata_receipt_contract_id": source_contract["redacted_metadata_receipt_contract_id"],
                "source_redacted_metadata_validation_passed": source_status["validation_passed"],
                "source_safe_to_continue_to_gp073": source_status["safe_to_continue_to_gp073"],
                "section": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "lineage_requirement_seed_count": len(requirement_seed),
                "lineage_requirement_code_count": len(LINEAGE_REQUIREMENT_SPECS),
                "lineage_requirement_count": len(requirement_seed) * len(LINEAGE_REQUIREMENT_SPECS),
                "lineage_policy_count": len(LINEAGE_POLICIES),
                "carried_redacted_metadata_blocker_count": len(source_blockers),
                "source_redacted_metadata_policy_count": len(source_policies),
                "receipt_lineage_locked": True,
                "lineage_template_only": True,
                "lineage_redaction_required": True,
                "receipt_lineage_created": False,
                "receipt_lineage_finalized": False,
                "lineage_hash_computed": False,
                "lineage_hash_chained": False,
                "provider_derived_lineage_created": False,
                "provider_metadata_lineage_created": False,
                "object_identifier_lineage_created": False,
                "object_body_lineage_content_created": False,
                "provider_metadata_imported": False,
                "object_id_collected": False,
                "object_key_collected": False,
                "object_body_read": False,
                "object_body_view_enabled": False,
                "direct_upload_enabled": False,
                "export_enabled": False,
                "execution_enabled": False,
                "vault_done": False,
                "next_pack": NEXT_PACK,
                "next_pack_title": NEXT_PACK_TITLE,
                "safe_to_continue_to_gp074": True,
            }

            contract_payload = {
                "receipt_lineage_lock_contract_id": DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,
                "pack_id": PACK_ID,
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "source_redacted_metadata_receipt_contract_id": source_contract["redacted_metadata_receipt_contract_id"],
                "source_redacted_metadata_pack_id": source_contract["pack_id"],
                "contract_status": "REAL_RECEIPT_LINEAGE_LOCK_CONTRACT_OPEN_TEMPLATE_ONLY_TOWER_LOCKED",
                "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED_FOR_RECEIPT_LINEAGE",
                "contract_data_json": _json_dumps(contract_data),
                "created_at": now,
                "updated_at": now,
            }
            for field in TRUE_CONTRACT_FIELDS:
                contract_payload[field] = 1
            for field in FALSE_FIELDS:
                contract_payload[field] = 0
            _insert_dict(conn, "vault_storage_provider_receipt_lineage_lock_contracts", contract_payload)

            for source_requirement in requirement_seed:
                for code, name, category in LINEAGE_REQUIREMENT_SPECS:
                    payload = {
                        "receipt_lineage_requirement_id": f"VSPRLLR-{source_requirement['redacted_metadata_requirement_id'].replace('VSPRMRR-', '')}-{code.upper().replace('_', '-')}",
                        "receipt_lineage_lock_contract_id": DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,
                        "source_requirement_id": source_requirement["redacted_metadata_requirement_id"],
                        "source_pack_id": source_requirement["source_pack_id"],
                        "source_requirement_code": source_requirement["requirement_code"],
                        "requirement_code": code,
                        "requirement_name": name,
                        "requirement_category": category,
                        "requirement_message": f"{name} remains required before provider-derived receipt lineage can be considered.",
                        "requirement_status": "REAL_RECEIPT_LINEAGE_REQUIREMENT_RECORDED_TEMPLATE_ONLY_TOWER_LOCKED",
                        "created_at": now,
                        "updated_at": now,
                    }
                    for field in TRUE_REQUIREMENT_FIELDS:
                        payload[field] = 1
                    for field in [
                        "requirement_verified",
                        "receipt_lineage_configured",
                        "receipt_lineage_attempted",
                        "receipt_lineage_enabled",
                        "receipt_lineage_created",
                        "receipt_lineage_finalized",
                        "lineage_hash_plan_approved",
                        "lineage_hash_computed",
                        "lineage_hash_chained",
                        "parent_receipt_attached",
                        "child_receipt_attached",
                        "provider_derived_lineage_created",
                        "provider_metadata_lineage_created",
                        "object_identifier_lineage_created",
                        "object_body_lineage_content_created",
                        "redacted_metadata_receipt_created",
                        "provider_metadata_imported",
                        "provider_metadata_read",
                        "provider_objects_listed",
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
                    _insert_dict(conn, "vault_storage_provider_receipt_lineage_requirements", payload)

            for code, name, category in LINEAGE_POLICIES:
                payload = {
                    "receipt_lineage_policy_id": f"VSPRLLP-{code.upper().replace('_', '-')}",
                    "receipt_lineage_lock_contract_id": DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,
                    "policy_code": code,
                    "policy_name": name,
                    "policy_category": category,
                    "policy_message": f"{name}; GP073 cannot create lineage, finalize receipts, attach parent/child provider receipts, export, or execute.",
                    "policy_status": "REAL_RECEIPT_LINEAGE_POLICY_RECORDED_TEMPLATE_ONLY_TOWER_LOCKED",
                    "policy_required": 1,
                    "tower_review_required": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in [
                    "policy_verified",
                    "receipt_lineage_configured",
                    "receipt_lineage_attempted",
                    "receipt_lineage_enabled",
                    "receipt_lineage_created",
                    "receipt_lineage_finalized",
                    "lineage_hash_plan_approved",
                    "lineage_hash_computed",
                    "lineage_hash_chained",
                    "parent_receipt_attached",
                    "child_receipt_attached",
                    "provider_derived_lineage_created",
                    "provider_metadata_lineage_created",
                    "object_identifier_lineage_created",
                    "object_body_lineage_content_created",
                    "redacted_metadata_receipt_created",
                    "provider_metadata_imported",
                    "provider_metadata_read",
                    "provider_objects_listed",
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
                _insert_dict(conn, "vault_storage_provider_receipt_lineage_policies", payload)

            for blocker in source_blockers:
                payload = {
                    "receipt_lineage_blocker_id": f"VSPRLLB-{blocker['redacted_metadata_blocker_id'].replace('VSPRM-BLOCK-', '')}",
                    "receipt_lineage_lock_contract_id": DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,
                    "source_redacted_metadata_blocker_id": blocker["redacted_metadata_blocker_id"],
                    "source_blocker_code": blocker["source_blocker_code"],
                    "source_blocker_category": blocker["source_blocker_category"],
                    "blocker_name": blocker["blocker_name"],
                    "severity": blocker["severity"],
                    "blocker_status": "REAL_RECEIPT_LINEAGE_BLOCKER_ACTIVE_CARRIED_FROM_GP072",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_BLOCKER_FIELDS:
                    payload[field] = 1
                for field in ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]:
                    payload[field] = 0
                _insert_dict(conn, "vault_storage_provider_receipt_lineage_blockers", payload)

            for event_type, event_payload in [
                ("REAL_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_CONTRACT_CREATED", contract_data),
                ("SOURCE_GP072_REDACTED_METADATA_RECEIPT_CONTRACT_ATTACHED", {
                    "source_redacted_metadata_receipt_contract_id": source_contract["redacted_metadata_receipt_contract_id"],
                    "source_redacted_metadata_pack_id": source_contract["pack_id"],
                    "source_validation_passed": source_status["validation_passed"],
                    "source_safe_to_continue_to_gp073": source_status["safe_to_continue_to_gp073"],
                }),
                ("REAL_RECEIPT_LINEAGE_REQUIREMENTS_CREATED_TEMPLATE_ONLY", {
                    "requirement_count": len(requirement_seed) * len(LINEAGE_REQUIREMENT_SPECS),
                    "requirement_seed_count": len(requirement_seed),
                }),
                ("REAL_RECEIPT_LINEAGE_POLICIES_CREATED_TEMPLATE_ONLY", {
                    "policy_count": len(LINEAGE_POLICIES),
                }),
                ("REAL_RECEIPT_LINEAGE_BLOCKERS_CARRIED_FORWARD", {
                    "blocker_count": len(source_blockers),
                }),
                ("RECEIPT_LINEAGE_LOCKS_CONFIRMED", {
                    "receipt_lineage_created": False,
                    "receipt_lineage_finalized": False,
                    "lineage_hash_computed": False,
                    "lineage_hash_chained": False,
                    "parent_receipt_attached": False,
                    "child_receipt_attached": False,
                    "provider_derived_lineage_created": False,
                    "provider_metadata_lineage_created": False,
                    "object_identifier_lineage_created": False,
                    "object_body_lineage_content_created": False,
                    "direct_upload_enabled": False,
                    "export_enabled": False,
                    "execution_enabled": False,
                    "vault_done": False,
                }),
            ]:
                _insert_event(conn, DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID, event_type, event_payload)

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

def get_storage_provider_receipt_lineage_lock_contract_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_receipt_lineage_lock_contract(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_receipt_lineage_lock_contracts
            WHERE receipt_lineage_lock_contract_id = ?
            """,
            (DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,),
        ).fetchone()
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "receipt_lineage_lock_contract": _boolify(row, {"contract_data_json": "contract_data"})}

def get_storage_provider_receipt_lineage_requirements(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_receipt_lineage_lock_contract(db_path)
    fields = [
        "requirement_required",
        "requirement_verified",
        "lineage_locked",
        "template_only",
        "lineage_redaction_required",
        "tower_review_required",
        "tower_review_granted",
        "receipt_lineage_configured",
        "receipt_lineage_attempted",
        "receipt_lineage_enabled",
        "receipt_lineage_created",
        "receipt_lineage_finalized",
        "lineage_hash_plan_approved",
        "lineage_hash_computed",
        "lineage_hash_chained",
        "parent_receipt_attached",
        "child_receipt_attached",
        "provider_derived_lineage_created",
        "provider_metadata_lineage_created",
        "object_identifier_lineage_created",
        "object_body_lineage_content_created",
        "redacted_metadata_receipt_created",
        "provider_metadata_imported",
        "provider_metadata_read",
        "provider_objects_listed",
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
        "vault_storage_provider_receipt_lineage_requirements",
        "receipt_lineage_lock_contract_id",
        DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_receipt_lineage_requirements
            WHERE receipt_lineage_lock_contract_id = ?
            ORDER BY source_requirement_id, requirement_category, requirement_code
            """,
            (DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,),
        ).fetchall()
        source_requirement_count = conn.execute(
            """
            SELECT COUNT(DISTINCT source_requirement_id) AS c
            FROM vault_storage_provider_receipt_lineage_requirements
            WHERE receipt_lineage_lock_contract_id = ?
            """,
            (DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]
        requirement_code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT requirement_code) AS c
            FROM vault_storage_provider_receipt_lineage_requirements
            WHERE receipt_lineage_lock_contract_id = ?
            """,
            (DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]

    counts["requirement_count"] = counts.pop("total_count")
    counts["source_requirement_count"] = int(source_requirement_count)
    counts["requirement_code_count"] = int(requirement_code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "requirements": [_boolify(row) for row in rows]}

def get_storage_provider_receipt_lineage_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_receipt_lineage_lock_contract(db_path)
    fields = [
        "policy_required",
        "policy_verified",
        "tower_review_required",
        "tower_review_granted",
        "receipt_lineage_configured",
        "receipt_lineage_attempted",
        "receipt_lineage_enabled",
        "receipt_lineage_created",
        "receipt_lineage_finalized",
        "lineage_hash_plan_approved",
        "lineage_hash_computed",
        "lineage_hash_chained",
        "parent_receipt_attached",
        "child_receipt_attached",
        "provider_derived_lineage_created",
        "provider_metadata_lineage_created",
        "object_identifier_lineage_created",
        "object_body_lineage_content_created",
        "redacted_metadata_receipt_created",
        "provider_metadata_imported",
        "provider_metadata_read",
        "provider_objects_listed",
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
        "vault_storage_provider_receipt_lineage_policies",
        "receipt_lineage_lock_contract_id",
        DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_receipt_lineage_policies
            WHERE receipt_lineage_lock_contract_id = ?
            ORDER BY policy_category, policy_code
            """,
            (DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,),
        ).fetchall()
        policy_code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT policy_code) AS c
            FROM vault_storage_provider_receipt_lineage_policies
            WHERE receipt_lineage_lock_contract_id = ?
            """,
            (DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]

    counts["policy_count"] = counts.pop("total_count")
    counts["policy_code_count"] = int(policy_code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "policies": [_boolify(row) for row in rows]}

def get_storage_provider_receipt_lineage_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_receipt_lineage_lock_contract(db_path)
    fields = [
        "blocker_active",
        "blocks_receipt_lineage",
        "blocks_provider_derived_lineage",
        "blocks_receipt_finalization",
        "blocks_lineage_hash_chain",
        "blocks_object_identifier_lineage",
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
        "vault_storage_provider_receipt_lineage_blockers",
        "receipt_lineage_lock_contract_id",
        DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_receipt_lineage_blockers
            WHERE receipt_lineage_lock_contract_id = ?
            ORDER BY source_blocker_category, source_blocker_code
            """,
            (DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,),
        ).fetchall()

    counts["blocker_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "blockers": [_boolify(row) for row in rows]}

def get_storage_provider_receipt_lineage_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_receipt_lineage_lock_contract(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_receipt_lineage_events
            WHERE receipt_lineage_lock_contract_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,),
        ).fetchall()
    events = [
        {
            "event_id": row["event_id"],
            "receipt_lineage_lock_contract_id": row["receipt_lineage_lock_contract_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def record_storage_provider_receipt_lineage_event(event_type: str, event_payload: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_receipt_lineage_lock_contract(db_path)
    payload = dict(event_payload or {})
    payload.update({
        "write_type": "REAL_STORAGE_PROVIDER_RECEIPT_LINEAGE_LOCK_EVENT",
        "receipt_lineage_lock_contract_ready": True,
        "receipt_lineage_locked": True,
        "lineage_template_only": True,
        "lineage_redaction_required": True,
        "receipt_lineage_configured": False,
        "receipt_lineage_attempted": False,
        "receipt_lineage_enabled": False,
        "receipt_lineage_created": False,
        "receipt_lineage_finalized": False,
        "lineage_hash_computed": False,
        "lineage_hash_chained": False,
        "parent_receipt_attached": False,
        "child_receipt_attached": False,
        "provider_derived_lineage_created": False,
        "provider_metadata_lineage_created": False,
        "object_identifier_lineage_created": False,
        "object_body_lineage_content_created": False,
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
        event_id = _insert_event(conn, DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID, event_type, payload)
        conn.commit()
    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "receipt_lineage_lock_contract_id": DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID,
        "real_sqlite_backed": True,
        **payload,
    }

def validate_storage_provider_receipt_lineage_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    contract = get_storage_provider_receipt_lineage_lock_contract_record(db_path)["receipt_lineage_lock_contract"]
    requirements = get_storage_provider_receipt_lineage_requirements(db_path)
    policies = get_storage_provider_receipt_lineage_policies(db_path)
    blockers = get_storage_provider_receipt_lineage_blockers(db_path)
    events = get_storage_provider_receipt_lineage_events(db_path)

    expected_requirements = 63 * len(LINEAGE_REQUIREMENT_SPECS)
    expected_policies = len(LINEAGE_POLICIES)
    expected_blockers = 14

    false_checks = [(f"NO_CONTRACT_{field.upper()}", contract[field] is False) for field in FALSE_FIELDS]

    checks = [
        ("REAL_SQLITE_RECEIPT_LINEAGE_LOCK_CONTRACT_EXISTS", contract["receipt_lineage_lock_contract_id"] == DEFAULT_RECEIPT_LINEAGE_LOCK_CONTRACT_ID),
        ("SOURCE_GP072_REDACTED_METADATA_RECEIPT_CONTRACT_ATTACHED", contract["source_redacted_metadata_receipt_contract_id"] == DEFAULT_REDACTED_METADATA_RECEIPT_CONTRACT_ID),
        ("RECEIPT_LINEAGE_LOCK_CONTRACT_READY", contract["receipt_lineage_lock_contract_ready"] is True),
        ("RECEIPT_LINEAGE_REQUIREMENTS_READY", contract["receipt_lineage_requirements_ready"] is True),
        ("RECEIPT_LINEAGE_POLICIES_READY", contract["receipt_lineage_policies_ready"] is True),
        ("RECEIPT_LINEAGE_BLOCKERS_READY", contract["receipt_lineage_blockers_ready"] is True),
        ("RECEIPT_LINEAGE_VALIDATION_READY", contract["receipt_lineage_validation_ready"] is True),
        ("RECEIPT_LINEAGE_LOCKED", contract["receipt_lineage_locked"] is True),
        ("LINEAGE_TEMPLATE_ONLY", contract["lineage_template_only"] is True),
        ("LINEAGE_REDACTION_REQUIRED", contract["lineage_redaction_required"] is True),
        ("SAFE_TO_CONTINUE_TO_GP074", contract["safe_to_continue_to_gp074"] is True),
        ("REAL_RECEIPT_LINEAGE_REQUIREMENTS_EXIST", requirements["requirement_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_REQUIRED", requirements["requirement_required_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_LINEAGE_LOCKED", requirements["lineage_locked_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_TEMPLATE_ONLY", requirements["template_only_count"] == expected_requirements),
        ("NO_REQUIREMENT_LINEAGE_CREATED", requirements["receipt_lineage_created_count"] == 0),
        ("NO_REQUIREMENT_LINEAGE_FINALIZED", requirements["receipt_lineage_finalized_count"] == 0),
        ("NO_REQUIREMENT_HASH_CHAINED", requirements["lineage_hash_chained_count"] == 0),
        ("NO_REQUIREMENT_PARENT_CHILD_ATTACHMENT", requirements["parent_receipt_attached_count"] == 0 and requirements["child_receipt_attached_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_DERIVED_LINEAGE", requirements["provider_derived_lineage_created_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_METADATA_LINEAGE", requirements["provider_metadata_lineage_created_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_IDENTIFIER_LINEAGE", requirements["object_identifier_lineage_created_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY_LINEAGE", requirements["object_body_lineage_content_created_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_IDENTIFIERS_COLLECTED", requirements["object_id_collected_count"] == 0 and requirements["object_key_collected_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY_READ", requirements["object_body_read_count"] == 0),
        ("NO_REQUIREMENT_DIRECT_UPLOAD", requirements["direct_upload_enabled_count"] == 0),
        ("NO_REQUIREMENT_EXPORT", requirements["export_enabled_count"] == 0),
        ("NO_REQUIREMENT_EXECUTION", requirements["execution_enabled_count"] == 0),
        ("REAL_RECEIPT_LINEAGE_POLICIES_EXIST", policies["policy_count"] == expected_policies),
        ("NO_POLICY_LINEAGE_CREATED", policies["receipt_lineage_created_count"] == 0),
        ("NO_POLICY_LINEAGE_FINALIZED", policies["receipt_lineage_finalized_count"] == 0),
        ("NO_POLICY_HASH_CHAINED", policies["lineage_hash_chained_count"] == 0),
        ("NO_POLICY_PARENT_CHILD_ATTACHMENT", policies["parent_receipt_attached_count"] == 0 and policies["child_receipt_attached_count"] == 0),
        ("NO_POLICY_PROVIDER_DERIVED_LINEAGE", policies["provider_derived_lineage_created_count"] == 0),
        ("NO_POLICY_OBJECT_IDENTIFIER_LINEAGE", policies["object_identifier_lineage_created_count"] == 0),
        ("NO_POLICY_OBJECT_BODY_LINEAGE", policies["object_body_lineage_content_created_count"] == 0),
        ("NO_POLICY_OBJECT_BODY_CONTENT_EXPOSED", policies["object_body_content_exposed_count"] == 0),
        ("NO_POLICY_DIRECT_UPLOAD", policies["direct_upload_enabled_count"] == 0),
        ("NO_POLICY_EXPORT", policies["export_enabled_count"] == 0),
        ("NO_POLICY_EXECUTION", policies["execution_enabled_count"] == 0),
        ("REAL_RECEIPT_LINEAGE_BLOCKERS_CARRIED_FORWARD", blockers["blocker_count"] == expected_blockers),
        ("ALL_BLOCKERS_ACTIVE", blockers["blocker_active_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_RECEIPT_LINEAGE", blockers["blocks_receipt_lineage_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_DERIVED_LINEAGE", blockers["blocks_provider_derived_lineage_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_RECEIPT_FINALIZATION", blockers["blocks_receipt_finalization_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_LINEAGE_HASH_CHAIN", blockers["blocks_lineage_hash_chain_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_OBJECT_IDENTIFIER_LINEAGE", blockers["blocks_object_identifier_lineage_count"] == expected_blockers),
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
        "safe_to_continue_to_gp074": len(failed) == 0,
        "vault_done": False,
    }

def get_storage_provider_receipt_lineage_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp074": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP073 adds the real receipt lineage lock contract in template-only mode. Continue to GP074 with the redacted access view lock contract while keeping provider-derived lineage, receipt finalization, object identifiers, object body access, direct upload, export, and execution locked.",
            "carry_forward_rules": [
                "Keep the real SQLite receipt lineage lock contract.",
                "Keep real receipt lineage requirement rows.",
                "Keep real receipt lineage policy rows.",
                "Keep real blocker rows carried from GP072.",
                "Do not create provider-derived receipt lineage.",
                "Do not finalize receipt lineage.",
                "Do not compute lineage hashes from provider data.",
                "Do not attach parent or child provider receipts.",
                "Do not create provider metadata lineage.",
                "Do not create object identifier lineage.",
                "Do not create object body lineage content.",
                "Do not collect object IDs, keys, ETags, sizes, or timestamps.",
                "Do not list provider objects.",
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
        "depends_on": ["VAULT_GP072"],
        "foundation_status": "receipt_lineage_lock_contract_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_receipt_lineage_lock_contract",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-storage-provider-receipt-lineage-lock-contract",
        "json_route": "/vault/real-storage-provider-receipt-lineage-lock-contract.json",
        "record_route": "/vault/storage-provider-receipt-lineage-lock-contract-record.json",
        "requirements_route": "/vault/storage-provider-receipt-lineage-requirements.json",
        "policies_route": "/vault/storage-provider-receipt-lineage-policies.json",
        "blockers_route": "/vault/storage-provider-receipt-lineage-blockers.json",
        "events_route": "/vault/storage-provider-receipt-lineage-events.json",
        "validation_route": "/vault/storage-provider-receipt-lineage-validation.json",
        "next_step_route": "/vault/storage-provider-receipt-lineage-next-step.json",
        "gp073_status_route": "/vault/gp073-status.json",
    }

def get_real_storage_provider_receipt_lineage_lock_contract_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_receipt_lineage_lock_contract(db_path)
    contract = get_storage_provider_receipt_lineage_lock_contract_record(db_path)["receipt_lineage_lock_contract"]
    requirements = get_storage_provider_receipt_lineage_requirements(db_path)
    policies = get_storage_provider_receipt_lineage_policies(db_path)
    blockers = get_storage_provider_receipt_lineage_blockers(db_path)
    events = get_storage_provider_receipt_lineage_events(db_path)
    validation = validate_storage_provider_receipt_lineage_lock_contract(db_path)

    truth = {
        "real_storage_provider_receipt_lineage_lock_contract_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "source_gp072_redacted_metadata_receipt_contract_attached": contract["source_redacted_metadata_receipt_contract_id"] == DEFAULT_REDACTED_METADATA_RECEIPT_CONTRACT_ID,
        "validation_passed": validation["valid"],
        "receipt_lineage_lock_contract_ready": contract["receipt_lineage_lock_contract_ready"],
        "receipt_lineage_locked": contract["receipt_lineage_locked"],
        "lineage_template_only": contract["lineage_template_only"],
        "lineage_redaction_required": contract["lineage_redaction_required"],
        "requirement_count": requirements["requirement_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "event_count": events["event_count"],
        "receipt_lineage_created": contract["receipt_lineage_created"],
        "receipt_lineage_finalized": contract["receipt_lineage_finalized"],
        "lineage_hash_computed": contract["lineage_hash_computed"],
        "lineage_hash_chained": contract["lineage_hash_chained"],
        "provider_derived_lineage_created": contract["provider_derived_lineage_created"],
        "provider_metadata_lineage_created": contract["provider_metadata_lineage_created"],
        "object_identifier_lineage_created": contract["object_identifier_lineage_created"],
        "object_body_lineage_content_created": contract["object_body_lineage_content_created"],
        "object_id_collected": contract["object_id_collected"],
        "object_key_collected": contract["object_key_collected"],
        "object_body_read": contract["object_body_read"],
        "object_body_view_enabled": contract["object_body_view_enabled"],
        "direct_upload_enabled": contract["direct_upload_enabled"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "safe_to_continue_to_gp074": validation["safe_to_continue_to_gp074"],
        "vault_done": contract["vault_done"],
    }

    return {
        "pack": _pack_payload(),
        "receipt_lineage_truth": truth,
        "store": init,
        "receipt_lineage_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_receipt_lineage_next_step()["next_step"],
    }

def get_gp073_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_receipt_lineage_lock_contract_home(db_path)
    contract = home["receipt_lineage_lock_contract"]
    requirements = home["requirements"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp073_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_receipt_lineage_lock_contract_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_contract_count": home["store"]["contract_count"],
            "real_requirement_count": home["store"]["requirement_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp072_redacted_metadata_receipt_contract_attached": True,
            "receipt_lineage_lock_contract_ready": contract["receipt_lineage_lock_contract_ready"],
            "receipt_lineage_requirements_ready": contract["receipt_lineage_requirements_ready"],
            "receipt_lineage_policies_ready": contract["receipt_lineage_policies_ready"],
            "receipt_lineage_blockers_ready": contract["receipt_lineage_blockers_ready"],
            "receipt_lineage_validation_ready": contract["receipt_lineage_validation_ready"],
            "receipt_lineage_locked": contract["receipt_lineage_locked"],
            "lineage_template_only": contract["lineage_template_only"],
            "lineage_redaction_required": contract["lineage_redaction_required"],
            "source_requirement_count": requirements["source_requirement_count"],
            "requirement_code_count": requirements["requirement_code_count"],
            "policy_code_count": policies["policy_code_count"],
            "blocker_count": blockers["blocker_count"],
            "receipt_lineage_created_count": requirements["receipt_lineage_created_count"] + policies["receipt_lineage_created_count"],
            "receipt_lineage_finalized_count": requirements["receipt_lineage_finalized_count"] + policies["receipt_lineage_finalized_count"],
            "lineage_hash_computed_count": requirements["lineage_hash_computed_count"] + policies["lineage_hash_computed_count"],
            "lineage_hash_chained_count": requirements["lineage_hash_chained_count"] + policies["lineage_hash_chained_count"],
            "parent_receipt_attached_count": requirements["parent_receipt_attached_count"] + policies["parent_receipt_attached_count"],
            "child_receipt_attached_count": requirements["child_receipt_attached_count"] + policies["child_receipt_attached_count"],
            "provider_derived_lineage_created_count": requirements["provider_derived_lineage_created_count"] + policies["provider_derived_lineage_created_count"],
            "provider_metadata_lineage_created_count": requirements["provider_metadata_lineage_created_count"] + policies["provider_metadata_lineage_created_count"],
            "object_identifier_lineage_created_count": requirements["object_identifier_lineage_created_count"] + policies["object_identifier_lineage_created_count"],
            "object_body_lineage_content_created_count": requirements["object_body_lineage_content_created_count"] + policies["object_body_lineage_content_created_count"],
            "object_id_collected_count": requirements["object_id_collected_count"] + policies["object_id_collected_count"],
            "object_key_collected_count": requirements["object_key_collected_count"] + policies["object_key_collected_count"],
            "object_body_read_count": requirements["object_body_read_count"] + policies["object_body_read_count"],
            "object_body_view_enabled_count": requirements["object_body_view_enabled_count"] + policies["object_body_view_enabled_count"],
            "direct_upload_enabled_count": requirements["direct_upload_enabled_count"] + policies["direct_upload_enabled_count"],
            "export_enabled_count": requirements["export_enabled_count"] + policies["export_enabled_count"],
            "execution_enabled_count": requirements["execution_enabled_count"] + policies["execution_enabled_count"],
            "blocks_receipt_lineage_count": blockers["blocks_receipt_lineage_count"],
            "blocks_provider_derived_lineage_count": blockers["blocks_provider_derived_lineage_count"],
            "blocks_receipt_finalization_count": blockers["blocks_receipt_finalization_count"],
            "blocks_lineage_hash_chain_count": blockers["blocks_lineage_hash_chain_count"],
            "blocks_object_identifier_lineage_count": blockers["blocks_object_identifier_lineage_count"],
            "blocks_object_body_view_count": blockers["blocks_object_body_view_count"],
            "blocks_direct_upload_count": blockers["blocks_direct_upload_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "tower_review_granted_count": blockers["tower_review_granted_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp074": validation["safe_to_continue_to_gp074"],
            "foundation_status": "receipt_lineage_lock_contract_ready_safe_to_continue_not_done",
            "receipt_lineage_configured": contract["receipt_lineage_configured"],
            "receipt_lineage_attempted": contract["receipt_lineage_attempted"],
            "receipt_lineage_enabled": contract["receipt_lineage_enabled"],
            "receipt_lineage_created": contract["receipt_lineage_created"],
            "receipt_lineage_finalized": contract["receipt_lineage_finalized"],
            "lineage_hash_plan_approved": contract["lineage_hash_plan_approved"],
            "lineage_hash_computed": contract["lineage_hash_computed"],
            "lineage_hash_chained": contract["lineage_hash_chained"],
            "parent_receipt_attached": contract["parent_receipt_attached"],
            "child_receipt_attached": contract["child_receipt_attached"],
            "provider_derived_lineage_created": contract["provider_derived_lineage_created"],
            "provider_metadata_lineage_created": contract["provider_metadata_lineage_created"],
            "object_identifier_lineage_created": contract["object_identifier_lineage_created"],
            "object_body_lineage_content_created": contract["object_body_lineage_content_created"],
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
            "clouds_status": "parked_do_not_continue_from_vault_gp073",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "receipt_lineage_truth": home["receipt_lineage_truth"],
        "routes": home["routes"],
        "receipt_lineage_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }

def render_real_storage_provider_receipt_lineage_lock_contract_page() -> str:
    home = get_real_storage_provider_receipt_lineage_lock_contract_home()
    truth = home["receipt_lineage_truth"]
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
<title>Vault Real Storage Provider Receipt Lineage Lock Contract · GP073</title>
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
    <div class="eyebrow">Archive Vault · Giant Pack 073</div>
    <div class="eyebrow">Real Provider Receipt and Redacted Access Layer · GP071-GP080</div>
    <h1>Real Storage Provider Receipt Lineage Lock Contract</h1>
    <p>GP073 creates a real receipt lineage lock contract in template-only mode. It does not create provider-derived lineage, finalize receipts, collect identifiers, export, or execute.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['requirement_count']}</strong><span>lineage requirements</span></div>
      <div class="metric"><strong>{truth['policy_count']}</strong><span>lineage policies</span></div>
      <div class="metric"><strong>{truth['receipt_lineage_created']}</strong><span>lineage created</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">Lineage contract ready</span>
      <span class="pill ok">Template-only</span>
      <span class="pill ok">Real SQLite-backed</span>
      <span class="pill danger">No provider lineage</span>
      <span class="pill danger">No finalization</span>
      <span class="pill danger">No body lineage</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Lineage Requirements Preview</h2>
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
    <h2>GP073 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['requirements_route'])}</code>
      <code>{escape(routes['policies_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_step_route'])}</code>
      <code>{escape(routes['gp073_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
