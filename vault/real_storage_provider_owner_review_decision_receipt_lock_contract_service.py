"""
VAULT GP078 — Real Storage Provider Owner Review Decision Receipt Lock Contract

Current section:
Archive Vault — Real Provider Receipt and Redacted Access Layer / GP071-GP080

This pack creates a real SQLite-backed owner review decision receipt lock
contract sourced from GP077. It prepares durable decision receipt rules for
future provider review while keeping receipt creation, finalization, approval,
denial, Tower unlock, provider attachments, object identifiers, object bodies,
direct upload, export, and execution locked.

It does not create a decision receipt, finalize a receipt, approve, deny,
unlock, attach provider material, download, upload, export, or execute.
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

from vault.real_storage_provider_owner_review_decision_lock_contract_service import (
    DEFAULT_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,
    get_gp077_status,
    get_storage_provider_owner_review_decision_blockers,
    get_storage_provider_owner_review_decision_lock_contract_record,
    get_storage_provider_owner_review_decision_policies,
    get_storage_provider_owner_review_decision_requirements,
)

PACK_ID = "VAULT_GP078"
PACK_NAME = "Real Storage Provider Owner Review Decision Receipt Lock Contract"
SCHEMA_VERSION = "vault.real_storage_provider_owner_review_decision_receipt_lock_contract.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Receipt and Redacted Access Layer"
SECTION_RANGE = "GP071-GP080"

NEXT_PACK = "VAULT_GP079_REAL_STORAGE_PROVIDER_OWNER_REVIEW_CLOSEOUT_LOCK_CONTRACT"
NEXT_PACK_TITLE = "Real Storage Provider Owner Review Closeout Lock Contract"

DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID = "VSPORDRLC-GP078-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_owner_review_decision_receipt_lock_contract.sqlite"

RECEIPT_REQUIREMENT_SPECS = [
    ("owner_review_decision_receipt_lock_record_required", "Owner review decision receipt lock record required", "receipt_lock"),
    ("source_owner_decision_contract_link_required", "Source owner decision contract link required", "source_decision"),
    ("receipt_template_only_required", "Receipt template-only state required", "template_only"),
    ("decision_receipt_identity_boundary_required", "Decision receipt identity boundary required", "receipt_identity_boundary"),
    ("receipt_not_finalization_required", "Receipt-not-finalization boundary required", "receipt_boundary"),
    ("tower_receipt_unlock_required", "Tower receipt unlock required", "tower_gate"),
]

RECEIPT_POLICIES = [
    ("no_live_decision_receipt", "No live decision receipt", "receipt_lock"),
    ("no_provider_backed_receipt_record", "No provider-backed receipt record", "provider_receipt_lock"),
    ("no_receipt_finalization", "No receipt finalization", "finalization_lock"),
    ("no_receipt_identity_hash", "No receipt identity hash", "identity_hash_lock"),
    ("no_decision_receipt_reason", "No decision receipt reason", "reason_lock"),
    ("no_tower_unlock_from_receipt", "No Tower unlock from receipt", "tower_unlock_lock"),
    ("no_provider_packet_attachment_to_receipt", "No provider packet attachment to receipt", "packet_attachment_lock"),
    ("no_object_identifier_or_body_in_receipt", "No object identifier or body in receipt", "object_lock"),
    ("no_receipt_download_or_export", "No receipt download or export", "export_lock"),
    ("no_execution_from_receipt", "No execution from receipt", "execution_lock"),
]

FALSE_FIELDS = [
    "owner_review_decision_receipt_configured",
    "owner_review_decision_receipt_attempted",
    "owner_review_decision_receipt_enabled",
    "owner_review_decision_receipt_created",
    "owner_review_decision_receipt_published",
    "owner_review_decision_receipt_finalized",
    "provider_backed_decision_receipt_created",
    "provider_backed_decision_receipt_attached",
    "decision_receipt_identity_hash_computed",
    "decision_receipt_identity_hash_chained",
    "decision_receipt_reason_requested",
    "decision_receipt_reason_recorded",
    "decision_receipt_packet_created",
    "decision_receipt_packet_finalized",
    "owner_review_decision_created",
    "provider_backed_decision_record_created",
    "provider_backed_decision_record_attached",
    "owner_decision_requested",
    "owner_decision_recorded",
    "owner_decision_approved",
    "owner_decision_denied",
    "owner_decision_deferred",
    "owner_decision_status_set",
    "decision_reason_requested",
    "decision_reason_recorded",
    "decision_receipt_created",
    "decision_receipt_finalized",
    "owner_approval_requested",
    "owner_approval_granted",
    "owner_denial_requested",
    "owner_denial_recorded",
    "tower_unlock_requested",
    "tower_unlock_granted",
    "provider_packet_attached",
    "provider_access_view_attached",
    "provider_object_view_attached",
    "provider_metadata_view_attached",
    "provider_receipt_lineage_view_attached",
    "object_identifier_attached",
    "object_key_attached",
    "object_etag_attached",
    "object_size_attached",
    "object_timestamp_attached",
    "object_body_attached",
    "plaintext_receipt_enabled",
    "decision_receipt_download_enabled",
    "owner_review_queue_created",
    "owner_review_queue_entry_created",
    "provider_backed_queue_entry_created",
    "owner_review_packet_created",
    "owner_review_packet_assembled",
    "provider_backed_packet_created",
    "redacted_access_view_rendered",
    "provider_metadata_imported",
    "provider_metadata_read",
    "provider_objects_listed",
    "object_id_collected",
    "object_key_collected",
    "object_etag_collected",
    "object_size_collected",
    "object_last_modified_collected",
    "object_body_read_attempted",
    "object_body_read",
    "object_body_view_enabled",
    "object_body_content_exposed",
    "object_body_plaintext_visible",
    "object_body_download_enabled",
    "direct_upload_enabled",
    "export_enabled",
    "execution_enabled",
    "vault_done",
]

TRUE_CONTRACT_FIELDS = [
    "owner_review_decision_receipt_lock_contract_ready",
    "owner_review_decision_receipt_requirements_ready",
    "owner_review_decision_receipt_policies_ready",
    "owner_review_decision_receipt_blockers_ready",
    "owner_review_decision_receipt_validation_ready",
    "owner_review_decision_receipt_locked",
    "receipt_template_only",
    "receipt_redaction_required",
    "source_owner_review_decision_lock_contract_attached",
    "safe_to_continue_to_gp079",
]

TRUE_REQUIREMENT_FIELDS = [
    "requirement_required",
    "receipt_locked",
    "template_only",
    "receipt_redaction_required",
    "tower_review_required",
]

TRUE_BLOCKER_FIELDS = [
    "blocker_active",
    "blocks_owner_review_decision_receipt",
    "blocks_provider_backed_receipt_record",
    "blocks_receipt_finalization",
    "blocks_receipt_identity_hash",
    "blocks_decision_receipt_reason",
    "blocks_tower_unlock",
    "blocks_provider_packet_attachment",
    "blocks_object_body_attachment",
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

def ensure_storage_provider_owner_review_decision_receipt_lock_contract_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)
        true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_CONTRACT_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_owner_review_decision_receipt_lock_contracts (
                owner_review_decision_receipt_lock_contract_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_owner_review_decision_lock_contract_id TEXT NOT NULL,
                source_owner_review_decision_pack_id TEXT NOT NULL,
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
            "owner_review_decision_receipt_created",
            "owner_review_decision_receipt_finalized",
            "provider_backed_decision_receipt_created",
            "provider_backed_decision_receipt_attached",
            "decision_receipt_identity_hash_computed",
            "decision_receipt_identity_hash_chained",
            "decision_receipt_reason_requested",
            "decision_receipt_reason_recorded",
            "decision_receipt_packet_created",
            "decision_receipt_packet_finalized",
            "owner_decision_recorded",
            "owner_decision_approved",
            "owner_decision_denied",
            "owner_approval_granted",
            "owner_denial_recorded",
            "tower_unlock_requested",
            "tower_unlock_granted",
            "provider_packet_attached",
            "provider_access_view_attached",
            "provider_metadata_view_attached",
            "object_identifier_attached",
            "object_key_attached",
            "object_body_attached",
            "plaintext_receipt_enabled",
            "decision_receipt_download_enabled",
            "direct_upload_enabled",
            "export_enabled",
            "execution_enabled",
            "tower_review_granted",
        ]
        req_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_REQUIREMENT_FIELDS)
        req_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in req_false)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_owner_review_decision_receipt_requirements (
                owner_review_decision_receipt_requirement_id TEXT PRIMARY KEY,
                owner_review_decision_receipt_lock_contract_id TEXT NOT NULL,
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
                FOREIGN KEY(owner_review_decision_receipt_lock_contract_id)
                    REFERENCES vault_storage_provider_owner_review_decision_receipt_lock_contracts(owner_review_decision_receipt_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(owner_review_decision_receipt_lock_contract_id, source_requirement_id, requirement_code)
            )
            """
        )

        policy_false = [
            "policy_verified",
            "owner_review_decision_receipt_created",
            "owner_review_decision_receipt_finalized",
            "provider_backed_decision_receipt_created",
            "provider_backed_decision_receipt_attached",
            "decision_receipt_identity_hash_computed",
            "decision_receipt_identity_hash_chained",
            "decision_receipt_reason_requested",
            "decision_receipt_reason_recorded",
            "decision_receipt_packet_created",
            "decision_receipt_packet_finalized",
            "owner_decision_recorded",
            "owner_decision_approved",
            "owner_decision_denied",
            "owner_approval_granted",
            "owner_denial_recorded",
            "tower_unlock_requested",
            "tower_unlock_granted",
            "provider_packet_attached",
            "provider_access_view_attached",
            "provider_metadata_view_attached",
            "object_identifier_attached",
            "object_key_attached",
            "object_body_attached",
            "plaintext_receipt_enabled",
            "decision_receipt_download_enabled",
            "direct_upload_enabled",
            "export_enabled",
            "execution_enabled",
            "tower_review_granted",
        ]
        policy_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in policy_false)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_owner_review_decision_receipt_policies (
                owner_review_decision_receipt_policy_id TEXT PRIMARY KEY,
                owner_review_decision_receipt_lock_contract_id TEXT NOT NULL,
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
                FOREIGN KEY(owner_review_decision_receipt_lock_contract_id)
                    REFERENCES vault_storage_provider_owner_review_decision_receipt_lock_contracts(owner_review_decision_receipt_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(owner_review_decision_receipt_lock_contract_id, policy_code)
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_owner_review_decision_receipt_blockers (
                owner_review_decision_receipt_blocker_id TEXT PRIMARY KEY,
                owner_review_decision_receipt_lock_contract_id TEXT NOT NULL,
                source_owner_review_decision_blocker_id TEXT NOT NULL,
                source_blocker_code TEXT NOT NULL,
                source_blocker_category TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                {blocker_true_sql},
                {blocker_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(owner_review_decision_receipt_lock_contract_id)
                    REFERENCES vault_storage_provider_owner_review_decision_receipt_lock_contracts(owner_review_decision_receipt_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(owner_review_decision_receipt_lock_contract_id, source_owner_review_decision_blocker_id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_owner_review_decision_receipt_events (
                event_id TEXT PRIMARY KEY,
                owner_review_decision_receipt_lock_contract_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(owner_review_decision_receipt_lock_contract_id)
                    REFERENCES vault_storage_provider_owner_review_decision_receipt_lock_contracts(owner_review_decision_receipt_lock_contract_id)
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
            "vault_storage_provider_owner_review_decision_receipt_lock_contracts",
            "vault_storage_provider_owner_review_decision_receipt_requirements",
            "vault_storage_provider_owner_review_decision_receipt_policies",
            "vault_storage_provider_owner_review_decision_receipt_blockers",
            "vault_storage_provider_owner_review_decision_receipt_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, contract_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VSPORDRLCEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_storage_provider_owner_review_decision_receipt_events",
        {
            "event_id": event_id,
            "owner_review_decision_receipt_lock_contract_id": contract_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "contract_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_owner_review_decision_receipt_lock_contracts").fetchone()["c"]),
            "requirement_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_owner_review_decision_receipt_requirements").fetchone()["c"]),
            "policy_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_owner_review_decision_receipt_policies").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_owner_review_decision_receipt_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_owner_review_decision_receipt_events").fetchone()["c"]),
        }

def _select_requirement_seed(source_requirements: list[dict], limit: int = 63) -> list[dict]:
    selected = []
    seen = set()

    for item in source_requirements:
        source_requirement_id = item["owner_review_decision_requirement_id"]
        if source_requirement_id in seen:
            continue
        seen.add(source_requirement_id)
        selected.append(item)
        if len(selected) >= limit:
            break

    if len(selected) < limit:
        for item in source_requirements:
            if item in selected:
                continue
            selected.append(item)
            if len(selected) >= limit:
                break

    return selected[:limit]

def initialize_real_storage_provider_owner_review_decision_receipt_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_owner_review_decision_receipt_lock_contract_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            """
            SELECT owner_review_decision_receipt_lock_contract_id
            FROM vault_storage_provider_owner_review_decision_receipt_lock_contracts
            WHERE owner_review_decision_receipt_lock_contract_id = ?
            """,
            (DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,),
        ).fetchone()

        if exists is None:
            source_status_payload = get_gp077_status()
            source_status = source_status_payload["gp077_status"]
            source_contract = get_storage_provider_owner_review_decision_lock_contract_record()["owner_review_decision_lock_contract"]
            source_requirements = get_storage_provider_owner_review_decision_requirements()["requirements"]
            source_policies = get_storage_provider_owner_review_decision_policies()["policies"]
            source_blockers = get_storage_provider_owner_review_decision_blockers()["blockers"]
            now = _now_iso()

            requirement_seed = _select_requirement_seed(source_requirements, 63)

            contract_data = {
                "schema_version": SCHEMA_VERSION,
                "contract_type": "REAL_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT",
                "source_pack": "VAULT_GP077",
                "source_owner_review_decision_lock_contract_id": source_contract["owner_review_decision_lock_contract_id"],
                "source_owner_review_decision_validation_passed": source_status["validation_passed"],
                "source_safe_to_continue_to_gp078": source_status["safe_to_continue_to_gp078"],
                "section": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "receipt_requirement_seed_count": len(requirement_seed),
                "receipt_requirement_code_count": len(RECEIPT_REQUIREMENT_SPECS),
                "receipt_requirement_count": len(requirement_seed) * len(RECEIPT_REQUIREMENT_SPECS),
                "receipt_policy_count": len(RECEIPT_POLICIES),
                "carried_owner_review_decision_blocker_count": len(source_blockers),
                "source_owner_review_decision_policy_count": len(source_policies),
                "owner_review_decision_receipt_locked": True,
                "receipt_template_only": True,
                "receipt_redaction_required": True,
                "owner_review_decision_receipt_created": False,
                "owner_review_decision_receipt_finalized": False,
                "provider_backed_decision_receipt_created": False,
                "decision_receipt_identity_hash_computed": False,
                "decision_receipt_identity_hash_chained": False,
                "decision_receipt_reason_recorded": False,
                "decision_receipt_packet_created": False,
                "decision_receipt_packet_finalized": False,
                "owner_decision_recorded": False,
                "owner_decision_approved": False,
                "owner_decision_denied": False,
                "owner_approval_granted": False,
                "owner_denial_recorded": False,
                "tower_unlock_granted": False,
                "provider_packet_attached": False,
                "object_identifier_attached": False,
                "object_body_attached": False,
                "decision_receipt_download_enabled": False,
                "direct_upload_enabled": False,
                "export_enabled": False,
                "execution_enabled": False,
                "vault_done": False,
                "next_pack": NEXT_PACK,
                "next_pack_title": NEXT_PACK_TITLE,
                "safe_to_continue_to_gp079": True,
            }

            contract_payload = {
                "owner_review_decision_receipt_lock_contract_id": DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,
                "pack_id": PACK_ID,
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "source_owner_review_decision_lock_contract_id": source_contract["owner_review_decision_lock_contract_id"],
                "source_owner_review_decision_pack_id": source_contract["pack_id"],
                "contract_status": "REAL_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_OPEN_TEMPLATE_ONLY_TOWER_LOCKED",
                "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED_FOR_OWNER_REVIEW_DECISION_RECEIPT",
                "contract_data_json": _json_dumps(contract_data),
                "created_at": now,
                "updated_at": now,
            }
            for field in TRUE_CONTRACT_FIELDS:
                contract_payload[field] = 1
            for field in FALSE_FIELDS:
                contract_payload[field] = 0
            _insert_dict(conn, "vault_storage_provider_owner_review_decision_receipt_lock_contracts", contract_payload)

            for source_requirement in requirement_seed:
                for code, name, category in RECEIPT_REQUIREMENT_SPECS:
                    payload = {
                        "owner_review_decision_receipt_requirement_id": f"VSPORDRR-{source_requirement['owner_review_decision_requirement_id'].replace('VSPORDR-', '')}-{code.upper().replace('_', '-')}",
                        "owner_review_decision_receipt_lock_contract_id": DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,
                        "source_requirement_id": source_requirement["owner_review_decision_requirement_id"],
                        "source_pack_id": source_requirement["source_pack_id"],
                        "source_requirement_code": source_requirement["requirement_code"],
                        "requirement_code": code,
                        "requirement_name": name,
                        "requirement_category": category,
                        "requirement_message": f"{name} remains required before an owner review decision receipt can be created.",
                        "requirement_status": "REAL_OWNER_REVIEW_DECISION_RECEIPT_REQUIREMENT_RECORDED_TEMPLATE_ONLY_TOWER_LOCKED",
                        "created_at": now,
                        "updated_at": now,
                    }
                    for field in TRUE_REQUIREMENT_FIELDS:
                        payload[field] = 1
                    for field in [
                        "requirement_verified",
                        "owner_review_decision_receipt_created",
                        "owner_review_decision_receipt_finalized",
                        "provider_backed_decision_receipt_created",
                        "provider_backed_decision_receipt_attached",
                        "decision_receipt_identity_hash_computed",
                        "decision_receipt_identity_hash_chained",
                        "decision_receipt_reason_requested",
                        "decision_receipt_reason_recorded",
                        "decision_receipt_packet_created",
                        "decision_receipt_packet_finalized",
                        "owner_decision_recorded",
                        "owner_decision_approved",
                        "owner_decision_denied",
                        "owner_approval_granted",
                        "owner_denial_recorded",
                        "tower_unlock_requested",
                        "tower_unlock_granted",
                        "provider_packet_attached",
                        "provider_access_view_attached",
                        "provider_metadata_view_attached",
                        "object_identifier_attached",
                        "object_key_attached",
                        "object_body_attached",
                        "plaintext_receipt_enabled",
                        "decision_receipt_download_enabled",
                        "direct_upload_enabled",
                        "export_enabled",
                        "execution_enabled",
                        "tower_review_granted",
                    ]:
                        payload[field] = 0
                    _insert_dict(conn, "vault_storage_provider_owner_review_decision_receipt_requirements", payload)

            for code, name, category in RECEIPT_POLICIES:
                payload = {
                    "owner_review_decision_receipt_policy_id": f"VSPORDRP-{code.upper().replace('_', '-')}",
                    "owner_review_decision_receipt_lock_contract_id": DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,
                    "policy_code": code,
                    "policy_name": name,
                    "policy_category": category,
                    "policy_message": f"{name}; GP078 cannot create/finalize receipts, approve, deny, unlock, download, export, or execute.",
                    "policy_status": "REAL_OWNER_REVIEW_DECISION_RECEIPT_POLICY_RECORDED_TEMPLATE_ONLY_TOWER_LOCKED",
                    "policy_required": 1,
                    "tower_review_required": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in [
                    "policy_verified",
                    "owner_review_decision_receipt_created",
                    "owner_review_decision_receipt_finalized",
                    "provider_backed_decision_receipt_created",
                    "provider_backed_decision_receipt_attached",
                    "decision_receipt_identity_hash_computed",
                    "decision_receipt_identity_hash_chained",
                    "decision_receipt_reason_requested",
                    "decision_receipt_reason_recorded",
                    "decision_receipt_packet_created",
                    "decision_receipt_packet_finalized",
                    "owner_decision_recorded",
                    "owner_decision_approved",
                    "owner_decision_denied",
                    "owner_approval_granted",
                    "owner_denial_recorded",
                    "tower_unlock_requested",
                    "tower_unlock_granted",
                    "provider_packet_attached",
                    "provider_access_view_attached",
                    "provider_metadata_view_attached",
                    "object_identifier_attached",
                    "object_key_attached",
                    "object_body_attached",
                    "plaintext_receipt_enabled",
                    "decision_receipt_download_enabled",
                    "direct_upload_enabled",
                    "export_enabled",
                    "execution_enabled",
                    "tower_review_granted",
                ]:
                    payload[field] = 0
                _insert_dict(conn, "vault_storage_provider_owner_review_decision_receipt_policies", payload)

            for blocker in source_blockers:
                payload = {
                    "owner_review_decision_receipt_blocker_id": f"VSPORDRB-{blocker['owner_review_decision_blocker_id'].replace('VSPORDB-', '')}",
                    "owner_review_decision_receipt_lock_contract_id": DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,
                    "source_owner_review_decision_blocker_id": blocker["owner_review_decision_blocker_id"],
                    "source_blocker_code": blocker["source_blocker_code"],
                    "source_blocker_category": blocker["source_blocker_category"],
                    "blocker_name": blocker["blocker_name"],
                    "severity": blocker["severity"],
                    "blocker_status": "REAL_OWNER_REVIEW_DECISION_RECEIPT_BLOCKER_ACTIVE_CARRIED_FROM_GP077",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_BLOCKER_FIELDS:
                    payload[field] = 1
                for field in ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]:
                    payload[field] = 0
                _insert_dict(conn, "vault_storage_provider_owner_review_decision_receipt_blockers", payload)

            for event_type, event_payload in [
                ("REAL_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_CREATED", contract_data),
                ("SOURCE_GP077_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ATTACHED", {
                    "source_owner_review_decision_lock_contract_id": source_contract["owner_review_decision_lock_contract_id"],
                    "source_owner_review_decision_pack_id": source_contract["pack_id"],
                    "source_validation_passed": source_status["validation_passed"],
                    "source_safe_to_continue_to_gp078": source_status["safe_to_continue_to_gp078"],
                }),
                ("REAL_OWNER_REVIEW_DECISION_RECEIPT_REQUIREMENTS_CREATED_TEMPLATE_ONLY", {
                    "requirement_count": len(requirement_seed) * len(RECEIPT_REQUIREMENT_SPECS),
                    "requirement_seed_count": len(requirement_seed),
                }),
                ("REAL_OWNER_REVIEW_DECISION_RECEIPT_POLICIES_CREATED_TEMPLATE_ONLY", {
                    "policy_count": len(RECEIPT_POLICIES),
                }),
                ("REAL_OWNER_REVIEW_DECISION_RECEIPT_BLOCKERS_CARRIED_FORWARD", {
                    "blocker_count": len(source_blockers),
                }),
                ("OWNER_REVIEW_DECISION_RECEIPT_LOCKS_CONFIRMED", {
                    "owner_review_decision_receipt_created": False,
                    "owner_review_decision_receipt_finalized": False,
                    "provider_backed_decision_receipt_created": False,
                    "decision_receipt_identity_hash_computed": False,
                    "decision_receipt_reason_recorded": False,
                    "decision_receipt_packet_created": False,
                    "owner_decision_recorded": False,
                    "owner_decision_approved": False,
                    "owner_decision_denied": False,
                    "owner_approval_granted": False,
                    "tower_unlock_granted": False,
                    "provider_packet_attached": False,
                    "object_identifier_attached": False,
                    "object_body_attached": False,
                    "decision_receipt_download_enabled": False,
                    "direct_upload_enabled": False,
                    "export_enabled": False,
                    "execution_enabled": False,
                    "vault_done": False,
                }),
            ]:
                _insert_event(conn, DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID, event_type, event_payload)

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

def get_storage_provider_owner_review_decision_receipt_lock_contract_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_owner_review_decision_receipt_lock_contract(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_owner_review_decision_receipt_lock_contracts
            WHERE owner_review_decision_receipt_lock_contract_id = ?
            """,
            (DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,),
        ).fetchone()
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "owner_review_decision_receipt_lock_contract": _boolify(row, {"contract_data_json": "contract_data"})}

def get_storage_provider_owner_review_decision_receipt_requirements(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_owner_review_decision_receipt_lock_contract(db_path)
    fields = [
        "requirement_required",
        "requirement_verified",
        "receipt_locked",
        "template_only",
        "receipt_redaction_required",
        "tower_review_required",
        "tower_review_granted",
        "owner_review_decision_receipt_created",
        "owner_review_decision_receipt_finalized",
        "provider_backed_decision_receipt_created",
        "provider_backed_decision_receipt_attached",
        "decision_receipt_identity_hash_computed",
        "decision_receipt_identity_hash_chained",
        "decision_receipt_reason_requested",
        "decision_receipt_reason_recorded",
        "decision_receipt_packet_created",
        "decision_receipt_packet_finalized",
        "owner_decision_recorded",
        "owner_decision_approved",
        "owner_decision_denied",
        "owner_approval_granted",
        "owner_denial_recorded",
        "tower_unlock_requested",
        "tower_unlock_granted",
        "provider_packet_attached",
        "provider_access_view_attached",
        "provider_metadata_view_attached",
        "object_identifier_attached",
        "object_key_attached",
        "object_body_attached",
        "plaintext_receipt_enabled",
        "decision_receipt_download_enabled",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
    ]
    counts = _sum_counts(
        "vault_storage_provider_owner_review_decision_receipt_requirements",
        "owner_review_decision_receipt_lock_contract_id",
        DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_owner_review_decision_receipt_requirements
            WHERE owner_review_decision_receipt_lock_contract_id = ?
            ORDER BY source_requirement_id, requirement_category, requirement_code
            """,
            (DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,),
        ).fetchall()
        source_requirement_count = conn.execute(
            """
            SELECT COUNT(DISTINCT source_requirement_id) AS c
            FROM vault_storage_provider_owner_review_decision_receipt_requirements
            WHERE owner_review_decision_receipt_lock_contract_id = ?
            """,
            (DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]
        requirement_code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT requirement_code) AS c
            FROM vault_storage_provider_owner_review_decision_receipt_requirements
            WHERE owner_review_decision_receipt_lock_contract_id = ?
            """,
            (DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]

    counts["requirement_count"] = counts.pop("total_count")
    counts["source_requirement_count"] = int(source_requirement_count)
    counts["requirement_code_count"] = int(requirement_code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "requirements": [_boolify(row) for row in rows]}

def get_storage_provider_owner_review_decision_receipt_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_owner_review_decision_receipt_lock_contract(db_path)
    fields = [
        "policy_required",
        "policy_verified",
        "tower_review_required",
        "tower_review_granted",
        "owner_review_decision_receipt_created",
        "owner_review_decision_receipt_finalized",
        "provider_backed_decision_receipt_created",
        "provider_backed_decision_receipt_attached",
        "decision_receipt_identity_hash_computed",
        "decision_receipt_identity_hash_chained",
        "decision_receipt_reason_requested",
        "decision_receipt_reason_recorded",
        "decision_receipt_packet_created",
        "decision_receipt_packet_finalized",
        "owner_decision_recorded",
        "owner_decision_approved",
        "owner_decision_denied",
        "owner_approval_granted",
        "owner_denial_recorded",
        "tower_unlock_requested",
        "tower_unlock_granted",
        "provider_packet_attached",
        "provider_access_view_attached",
        "provider_metadata_view_attached",
        "object_identifier_attached",
        "object_key_attached",
        "object_body_attached",
        "plaintext_receipt_enabled",
        "decision_receipt_download_enabled",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
    ]
    counts = _sum_counts(
        "vault_storage_provider_owner_review_decision_receipt_policies",
        "owner_review_decision_receipt_lock_contract_id",
        DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_owner_review_decision_receipt_policies
            WHERE owner_review_decision_receipt_lock_contract_id = ?
            ORDER BY policy_category, policy_code
            """,
            (DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,),
        ).fetchall()
        policy_code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT policy_code) AS c
            FROM vault_storage_provider_owner_review_decision_receipt_policies
            WHERE owner_review_decision_receipt_lock_contract_id = ?
            """,
            (DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]

    counts["policy_count"] = counts.pop("total_count")
    counts["policy_code_count"] = int(policy_code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "policies": [_boolify(row) for row in rows]}

def get_storage_provider_owner_review_decision_receipt_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_owner_review_decision_receipt_lock_contract(db_path)
    fields = [
        "blocker_active",
        "blocks_owner_review_decision_receipt",
        "blocks_provider_backed_receipt_record",
        "blocks_receipt_finalization",
        "blocks_receipt_identity_hash",
        "blocks_decision_receipt_reason",
        "blocks_tower_unlock",
        "blocks_provider_packet_attachment",
        "blocks_object_body_attachment",
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
        "vault_storage_provider_owner_review_decision_receipt_blockers",
        "owner_review_decision_receipt_lock_contract_id",
        DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,
        fields,
        db_path,
    )
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_owner_review_decision_receipt_blockers
            WHERE owner_review_decision_receipt_lock_contract_id = ?
            ORDER BY source_blocker_category, source_blocker_code
            """,
            (DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,),
        ).fetchall()

    counts["blocker_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "blockers": [_boolify(row) for row in rows]}

def get_storage_provider_owner_review_decision_receipt_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_owner_review_decision_receipt_lock_contract(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_owner_review_decision_receipt_events
            WHERE owner_review_decision_receipt_lock_contract_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,),
        ).fetchall()
    events = [
        {
            "event_id": row["event_id"],
            "owner_review_decision_receipt_lock_contract_id": row["owner_review_decision_receipt_lock_contract_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def record_storage_provider_owner_review_decision_receipt_event(event_type: str, event_payload: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_owner_review_decision_receipt_lock_contract(db_path)
    payload = dict(event_payload or {})
    payload.update({
        "write_type": "REAL_STORAGE_PROVIDER_OWNER_REVIEW_DECISION_RECEIPT_LOCK_EVENT",
        "owner_review_decision_receipt_lock_contract_ready": True,
        "owner_review_decision_receipt_locked": True,
        "receipt_template_only": True,
        "receipt_redaction_required": True,
        "owner_review_decision_receipt_created": False,
        "owner_review_decision_receipt_finalized": False,
        "provider_backed_decision_receipt_created": False,
        "decision_receipt_identity_hash_computed": False,
        "decision_receipt_reason_recorded": False,
        "decision_receipt_packet_created": False,
        "owner_decision_recorded": False,
        "owner_decision_approved": False,
        "owner_decision_denied": False,
        "owner_approval_granted": False,
        "owner_denial_recorded": False,
        "tower_unlock_granted": False,
        "provider_packet_attached": False,
        "object_identifier_attached": False,
        "object_body_attached": False,
        "decision_receipt_download_enabled": False,
        "direct_upload_enabled": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    })
    with _connect(db_path) as conn:
        event_id = _insert_event(conn, DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID, event_type, payload)
        conn.commit()
    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "owner_review_decision_receipt_lock_contract_id": DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,
        "real_sqlite_backed": True,
        **payload,
    }

def validate_storage_provider_owner_review_decision_receipt_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    contract = get_storage_provider_owner_review_decision_receipt_lock_contract_record(db_path)["owner_review_decision_receipt_lock_contract"]
    requirements = get_storage_provider_owner_review_decision_receipt_requirements(db_path)
    policies = get_storage_provider_owner_review_decision_receipt_policies(db_path)
    blockers = get_storage_provider_owner_review_decision_receipt_blockers(db_path)
    events = get_storage_provider_owner_review_decision_receipt_events(db_path)

    expected_requirements = 63 * len(RECEIPT_REQUIREMENT_SPECS)
    expected_policies = len(RECEIPT_POLICIES)
    expected_blockers = 14

    false_checks = [(f"NO_CONTRACT_{field.upper()}", contract[field] is False) for field in FALSE_FIELDS]

    checks = [
        ("REAL_SQLITE_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_EXISTS", contract["owner_review_decision_receipt_lock_contract_id"] == DEFAULT_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID),
        ("SOURCE_GP077_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ATTACHED", contract["source_owner_review_decision_lock_contract_id"] == DEFAULT_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID),
        ("OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_READY", contract["owner_review_decision_receipt_lock_contract_ready"] is True),
        ("OWNER_REVIEW_DECISION_RECEIPT_REQUIREMENTS_READY", contract["owner_review_decision_receipt_requirements_ready"] is True),
        ("OWNER_REVIEW_DECISION_RECEIPT_POLICIES_READY", contract["owner_review_decision_receipt_policies_ready"] is True),
        ("OWNER_REVIEW_DECISION_RECEIPT_BLOCKERS_READY", contract["owner_review_decision_receipt_blockers_ready"] is True),
        ("OWNER_REVIEW_DECISION_RECEIPT_VALIDATION_READY", contract["owner_review_decision_receipt_validation_ready"] is True),
        ("OWNER_REVIEW_DECISION_RECEIPT_LOCKED", contract["owner_review_decision_receipt_locked"] is True),
        ("RECEIPT_TEMPLATE_ONLY", contract["receipt_template_only"] is True),
        ("RECEIPT_REDACTION_REQUIRED", contract["receipt_redaction_required"] is True),
        ("SAFE_TO_CONTINUE_TO_GP079", contract["safe_to_continue_to_gp079"] is True),
        ("REAL_OWNER_REVIEW_DECISION_RECEIPT_REQUIREMENTS_EXIST", requirements["requirement_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_REQUIRED", requirements["requirement_required_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_RECEIPT_LOCKED", requirements["receipt_locked_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_TEMPLATE_ONLY", requirements["template_only_count"] == expected_requirements),
        ("NO_REQUIREMENT_RECEIPT_CREATED", requirements["owner_review_decision_receipt_created_count"] == 0),
        ("NO_REQUIREMENT_RECEIPT_FINALIZED", requirements["owner_review_decision_receipt_finalized_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_BACKED_RECEIPT", requirements["provider_backed_decision_receipt_created_count"] == 0),
        ("NO_REQUIREMENT_RECEIPT_HASH", requirements["decision_receipt_identity_hash_computed_count"] == 0),
        ("NO_REQUIREMENT_RECEIPT_REASON", requirements["decision_receipt_reason_recorded_count"] == 0),
        ("NO_REQUIREMENT_DECISION_PACKET", requirements["decision_receipt_packet_created_count"] == 0),
        ("NO_REQUIREMENT_OWNER_DECISION", requirements["owner_decision_recorded_count"] == 0),
        ("NO_REQUIREMENT_APPROVAL_OR_DENIAL", requirements["owner_approval_granted_count"] == 0 and requirements["owner_denial_recorded_count"] == 0),
        ("NO_REQUIREMENT_TOWER_UNLOCK", requirements["tower_unlock_requested_count"] == 0 and requirements["tower_unlock_granted_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_PACKET_ATTACHMENT", requirements["provider_packet_attached_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_ATTACHMENT", requirements["object_identifier_attached_count"] == 0 and requirements["object_body_attached_count"] == 0),
        ("NO_REQUIREMENT_DOWNLOAD_OR_EXPORT", requirements["decision_receipt_download_enabled_count"] == 0 and requirements["export_enabled_count"] == 0),
        ("NO_REQUIREMENT_DIRECT_UPLOAD", requirements["direct_upload_enabled_count"] == 0),
        ("NO_REQUIREMENT_EXECUTION", requirements["execution_enabled_count"] == 0),
        ("REAL_OWNER_REVIEW_DECISION_RECEIPT_POLICIES_EXIST", policies["policy_count"] == expected_policies),
        ("NO_POLICY_RECEIPT_CREATED", policies["owner_review_decision_receipt_created_count"] == 0),
        ("NO_POLICY_RECEIPT_FINALIZED", policies["owner_review_decision_receipt_finalized_count"] == 0),
        ("NO_POLICY_PROVIDER_BACKED_RECEIPT", policies["provider_backed_decision_receipt_created_count"] == 0),
        ("NO_POLICY_RECEIPT_HASH", policies["decision_receipt_identity_hash_computed_count"] == 0),
        ("NO_POLICY_RECEIPT_REASON", policies["decision_receipt_reason_recorded_count"] == 0),
        ("NO_POLICY_DECISION_PACKET", policies["decision_receipt_packet_created_count"] == 0),
        ("NO_POLICY_OWNER_DECISION", policies["owner_decision_recorded_count"] == 0),
        ("NO_POLICY_APPROVAL_OR_DENIAL", policies["owner_approval_granted_count"] == 0 and policies["owner_denial_recorded_count"] == 0),
        ("NO_POLICY_TOWER_UNLOCK", policies["tower_unlock_requested_count"] == 0 and policies["tower_unlock_granted_count"] == 0),
        ("NO_POLICY_PROVIDER_PACKET_ATTACHMENT", policies["provider_packet_attached_count"] == 0),
        ("NO_POLICY_OBJECT_ATTACHMENT", policies["object_identifier_attached_count"] == 0 and policies["object_body_attached_count"] == 0),
        ("NO_POLICY_DOWNLOAD_OR_EXPORT", policies["decision_receipt_download_enabled_count"] == 0 and policies["export_enabled_count"] == 0),
        ("NO_POLICY_DIRECT_UPLOAD", policies["direct_upload_enabled_count"] == 0),
        ("NO_POLICY_EXECUTION", policies["execution_enabled_count"] == 0),
        ("REAL_OWNER_REVIEW_DECISION_RECEIPT_BLOCKERS_CARRIED_FORWARD", blockers["blocker_count"] == expected_blockers),
        ("ALL_BLOCKERS_ACTIVE", blockers["blocker_active_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_OWNER_REVIEW_DECISION_RECEIPT", blockers["blocks_owner_review_decision_receipt_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_BACKED_RECEIPT_RECORD", blockers["blocks_provider_backed_receipt_record_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_RECEIPT_FINALIZATION", blockers["blocks_receipt_finalization_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_RECEIPT_IDENTITY_HASH", blockers["blocks_receipt_identity_hash_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_DECISION_RECEIPT_REASON", blockers["blocks_decision_receipt_reason_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_TOWER_UNLOCK", blockers["blocks_tower_unlock_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_PACKET_ATTACHMENT", blockers["blocks_provider_packet_attachment_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY_ATTACHMENT", blockers["blocks_object_body_attachment_count"] == expected_blockers),
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
        "safe_to_continue_to_gp079": len(failed) == 0,
        "vault_done": False,
    }

def get_storage_provider_owner_review_decision_receipt_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp079": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP078 adds the real owner review decision receipt lock contract in template-only mode. Continue to GP079 with the owner review closeout lock contract while keeping receipt creation/finalization, owner decisions, approvals, denials, Tower unlocks, provider attachments, direct upload, export, and execution locked.",
            "carry_forward_rules": [
                "Keep the real SQLite owner review decision receipt lock contract.",
                "Keep real owner review decision receipt requirement rows.",
                "Keep real owner review decision receipt policy rows.",
                "Keep real blocker rows carried from GP077.",
                "Do not create live decision receipts.",
                "Do not create provider-backed receipt records.",
                "Do not finalize decision receipts.",
                "Do not compute receipt identity hashes.",
                "Do not record decision receipt reasons.",
                "Do not record owner decisions.",
                "Do not approve or deny provider access.",
                "Do not request or grant Tower unlock.",
                "Do not attach provider packets.",
                "Do not attach provider views.",
                "Do not attach object identifiers.",
                "Do not attach object bodies.",
                "Do not enable receipt download.",
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
        "depends_on": ["VAULT_GP077"],
        "foundation_status": "owner_review_decision_receipt_lock_contract_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_owner_review_decision_receipt_lock_contract",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-storage-provider-owner-review-decision-receipt-lock-contract",
        "json_route": "/vault/real-storage-provider-owner-review-decision-receipt-lock-contract.json",
        "record_route": "/vault/storage-provider-owner-review-decision-receipt-lock-contract-record.json",
        "requirements_route": "/vault/storage-provider-owner-review-decision-receipt-requirements.json",
        "policies_route": "/vault/storage-provider-owner-review-decision-receipt-policies.json",
        "blockers_route": "/vault/storage-provider-owner-review-decision-receipt-blockers.json",
        "events_route": "/vault/storage-provider-owner-review-decision-receipt-events.json",
        "validation_route": "/vault/storage-provider-owner-review-decision-receipt-validation.json",
        "next_step_route": "/vault/storage-provider-owner-review-decision-receipt-next-step.json",
        "gp078_status_route": "/vault/gp078-status.json",
    }

def get_real_storage_provider_owner_review_decision_receipt_lock_contract_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_owner_review_decision_receipt_lock_contract(db_path)
    contract = get_storage_provider_owner_review_decision_receipt_lock_contract_record(db_path)["owner_review_decision_receipt_lock_contract"]
    requirements = get_storage_provider_owner_review_decision_receipt_requirements(db_path)
    policies = get_storage_provider_owner_review_decision_receipt_policies(db_path)
    blockers = get_storage_provider_owner_review_decision_receipt_blockers(db_path)
    events = get_storage_provider_owner_review_decision_receipt_events(db_path)
    validation = validate_storage_provider_owner_review_decision_receipt_lock_contract(db_path)

    truth = {
        "real_storage_provider_owner_review_decision_receipt_lock_contract_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "source_gp077_owner_review_decision_lock_contract_attached": contract["source_owner_review_decision_lock_contract_id"] == DEFAULT_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,
        "validation_passed": validation["valid"],
        "owner_review_decision_receipt_lock_contract_ready": contract["owner_review_decision_receipt_lock_contract_ready"],
        "owner_review_decision_receipt_locked": contract["owner_review_decision_receipt_locked"],
        "receipt_template_only": contract["receipt_template_only"],
        "receipt_redaction_required": contract["receipt_redaction_required"],
        "requirement_count": requirements["requirement_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "event_count": events["event_count"],
        "owner_review_decision_receipt_created": contract["owner_review_decision_receipt_created"],
        "owner_review_decision_receipt_finalized": contract["owner_review_decision_receipt_finalized"],
        "provider_backed_decision_receipt_created": contract["provider_backed_decision_receipt_created"],
        "decision_receipt_identity_hash_computed": contract["decision_receipt_identity_hash_computed"],
        "decision_receipt_reason_recorded": contract["decision_receipt_reason_recorded"],
        "decision_receipt_packet_created": contract["decision_receipt_packet_created"],
        "owner_decision_recorded": contract["owner_decision_recorded"],
        "owner_decision_approved": contract["owner_decision_approved"],
        "owner_decision_denied": contract["owner_decision_denied"],
        "owner_approval_granted": contract["owner_approval_granted"],
        "tower_unlock_granted": contract["tower_unlock_granted"],
        "provider_packet_attached": contract["provider_packet_attached"],
        "object_identifier_attached": contract["object_identifier_attached"],
        "object_body_attached": contract["object_body_attached"],
        "decision_receipt_download_enabled": contract["decision_receipt_download_enabled"],
        "direct_upload_enabled": contract["direct_upload_enabled"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "safe_to_continue_to_gp079": validation["safe_to_continue_to_gp079"],
        "vault_done": contract["vault_done"],
    }

    return {
        "pack": _pack_payload(),
        "owner_review_decision_receipt_truth": truth,
        "store": init,
        "owner_review_decision_receipt_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_owner_review_decision_receipt_next_step()["next_step"],
    }

def get_gp078_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_owner_review_decision_receipt_lock_contract_home(db_path)
    contract = home["owner_review_decision_receipt_lock_contract"]
    requirements = home["requirements"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp078_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_owner_review_decision_receipt_lock_contract_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_contract_count": home["store"]["contract_count"],
            "real_requirement_count": home["store"]["requirement_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp077_owner_review_decision_lock_contract_attached": True,
            "owner_review_decision_receipt_lock_contract_ready": contract["owner_review_decision_receipt_lock_contract_ready"],
            "owner_review_decision_receipt_requirements_ready": contract["owner_review_decision_receipt_requirements_ready"],
            "owner_review_decision_receipt_policies_ready": contract["owner_review_decision_receipt_policies_ready"],
            "owner_review_decision_receipt_blockers_ready": contract["owner_review_decision_receipt_blockers_ready"],
            "owner_review_decision_receipt_validation_ready": contract["owner_review_decision_receipt_validation_ready"],
            "owner_review_decision_receipt_locked": contract["owner_review_decision_receipt_locked"],
            "receipt_template_only": contract["receipt_template_only"],
            "receipt_redaction_required": contract["receipt_redaction_required"],
            "source_requirement_count": requirements["source_requirement_count"],
            "requirement_code_count": requirements["requirement_code_count"],
            "policy_code_count": policies["policy_code_count"],
            "blocker_count": blockers["blocker_count"],
            "owner_review_decision_receipt_created_count": requirements["owner_review_decision_receipt_created_count"] + policies["owner_review_decision_receipt_created_count"],
            "owner_review_decision_receipt_finalized_count": requirements["owner_review_decision_receipt_finalized_count"] + policies["owner_review_decision_receipt_finalized_count"],
            "provider_backed_decision_receipt_created_count": requirements["provider_backed_decision_receipt_created_count"] + policies["provider_backed_decision_receipt_created_count"],
            "decision_receipt_identity_hash_computed_count": requirements["decision_receipt_identity_hash_computed_count"] + policies["decision_receipt_identity_hash_computed_count"],
            "decision_receipt_reason_recorded_count": requirements["decision_receipt_reason_recorded_count"] + policies["decision_receipt_reason_recorded_count"],
            "decision_receipt_packet_created_count": requirements["decision_receipt_packet_created_count"] + policies["decision_receipt_packet_created_count"],
            "owner_decision_recorded_count": requirements["owner_decision_recorded_count"] + policies["owner_decision_recorded_count"],
            "owner_decision_approved_count": requirements["owner_decision_approved_count"] + policies["owner_decision_approved_count"],
            "owner_decision_denied_count": requirements["owner_decision_denied_count"] + policies["owner_decision_denied_count"],
            "owner_approval_granted_count": requirements["owner_approval_granted_count"] + policies["owner_approval_granted_count"],
            "tower_unlock_granted_count": requirements["tower_unlock_granted_count"] + policies["tower_unlock_granted_count"],
            "provider_packet_attached_count": requirements["provider_packet_attached_count"] + policies["provider_packet_attached_count"],
            "object_identifier_attached_count": requirements["object_identifier_attached_count"] + policies["object_identifier_attached_count"],
            "object_body_attached_count": requirements["object_body_attached_count"] + policies["object_body_attached_count"],
            "decision_receipt_download_enabled_count": requirements["decision_receipt_download_enabled_count"] + policies["decision_receipt_download_enabled_count"],
            "direct_upload_enabled_count": requirements["direct_upload_enabled_count"] + policies["direct_upload_enabled_count"],
            "export_enabled_count": requirements["export_enabled_count"] + policies["export_enabled_count"],
            "execution_enabled_count": requirements["execution_enabled_count"] + policies["execution_enabled_count"],
            "blocks_owner_review_decision_receipt_count": blockers["blocks_owner_review_decision_receipt_count"],
            "blocks_provider_backed_receipt_record_count": blockers["blocks_provider_backed_receipt_record_count"],
            "blocks_receipt_finalization_count": blockers["blocks_receipt_finalization_count"],
            "blocks_receipt_identity_hash_count": blockers["blocks_receipt_identity_hash_count"],
            "blocks_decision_receipt_reason_count": blockers["blocks_decision_receipt_reason_count"],
            "blocks_tower_unlock_count": blockers["blocks_tower_unlock_count"],
            "blocks_provider_packet_attachment_count": blockers["blocks_provider_packet_attachment_count"],
            "blocks_object_body_attachment_count": blockers["blocks_object_body_attachment_count"],
            "blocks_direct_upload_count": blockers["blocks_direct_upload_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "tower_review_granted_count": blockers["tower_review_granted_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp079": validation["safe_to_continue_to_gp079"],
            "foundation_status": "owner_review_decision_receipt_lock_contract_ready_safe_to_continue_not_done",
            "owner_review_decision_receipt_configured": contract["owner_review_decision_receipt_configured"],
            "owner_review_decision_receipt_attempted": contract["owner_review_decision_receipt_attempted"],
            "owner_review_decision_receipt_enabled": contract["owner_review_decision_receipt_enabled"],
            "owner_review_decision_receipt_created": contract["owner_review_decision_receipt_created"],
            "owner_review_decision_receipt_published": contract["owner_review_decision_receipt_published"],
            "owner_review_decision_receipt_finalized": contract["owner_review_decision_receipt_finalized"],
            "provider_backed_decision_receipt_created": contract["provider_backed_decision_receipt_created"],
            "provider_backed_decision_receipt_attached": contract["provider_backed_decision_receipt_attached"],
            "decision_receipt_identity_hash_computed": contract["decision_receipt_identity_hash_computed"],
            "decision_receipt_identity_hash_chained": contract["decision_receipt_identity_hash_chained"],
            "decision_receipt_reason_requested": contract["decision_receipt_reason_requested"],
            "decision_receipt_reason_recorded": contract["decision_receipt_reason_recorded"],
            "decision_receipt_packet_created": contract["decision_receipt_packet_created"],
            "decision_receipt_packet_finalized": contract["decision_receipt_packet_finalized"],
            "owner_decision_recorded": contract["owner_decision_recorded"],
            "owner_decision_approved": contract["owner_decision_approved"],
            "owner_decision_denied": contract["owner_decision_denied"],
            "owner_approval_granted": contract["owner_approval_granted"],
            "owner_denial_recorded": contract["owner_denial_recorded"],
            "tower_unlock_requested": contract["tower_unlock_requested"],
            "tower_unlock_granted": contract["tower_unlock_granted"],
            "provider_packet_attached": contract["provider_packet_attached"],
            "provider_access_view_attached": contract["provider_access_view_attached"],
            "provider_metadata_view_attached": contract["provider_metadata_view_attached"],
            "object_identifier_attached": contract["object_identifier_attached"],
            "object_key_attached": contract["object_key_attached"],
            "object_body_attached": contract["object_body_attached"],
            "plaintext_receipt_enabled": contract["plaintext_receipt_enabled"],
            "decision_receipt_download_enabled": contract["decision_receipt_download_enabled"],
            "direct_upload_enabled": contract["direct_upload_enabled"],
            "export_enabled": contract["export_enabled"],
            "execution_enabled": contract["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp078",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "owner_review_decision_receipt_truth": home["owner_review_decision_receipt_truth"],
        "routes": home["routes"],
        "owner_review_decision_receipt_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }

def render_real_storage_provider_owner_review_decision_receipt_lock_contract_page() -> str:
    home = get_real_storage_provider_owner_review_decision_receipt_lock_contract_home()
    truth = home["owner_review_decision_receipt_truth"]
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
<title>Vault Real Storage Provider Owner Review Decision Receipt Lock Contract · GP078</title>
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
    <div class="eyebrow">Archive Vault · Giant Pack 078</div>
    <div class="eyebrow">Real Provider Receipt and Redacted Access Layer · GP071-GP080</div>
    <h1>Real Storage Provider Owner Review Decision Receipt Lock Contract</h1>
    <p>GP078 creates a real owner review decision receipt lock contract in template-only mode. It does not create or finalize receipts, approve, deny, unlock, export, or execute.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['requirement_count']}</strong><span>receipt requirements</span></div>
      <div class="metric"><strong>{truth['policy_count']}</strong><span>receipt policies</span></div>
      <div class="metric"><strong>{truth['owner_review_decision_receipt_created']}</strong><span>receipts created</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">Decision receipt contract ready</span>
      <span class="pill ok">Template-only</span>
      <span class="pill ok">Real SQLite-backed</span>
      <span class="pill danger">No receipt</span>
      <span class="pill danger">No finalization</span>
      <span class="pill danger">No receipt hash</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Owner Review Decision Receipt Requirements Preview</h2>
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
    <h2>GP078 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['requirements_route'])}</code>
      <code>{escape(routes['policies_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_step_route'])}</code>
      <code>{escape(routes['gp078_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
