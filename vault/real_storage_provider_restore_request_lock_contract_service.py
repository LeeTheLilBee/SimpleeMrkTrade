"""
VAULT GP081 — Real Storage Provider Restore Request Lock Contract

Current section:
Archive Vault — Real Provider Restore and Export Governance Layer / GP081-GP090

This pack opens the restore/export governance layer with a real SQLite-backed
restore request lock contract sourced from GP080 readiness.

It prepares durable restore request rules but keeps restore requests, restore
eligibility, provider restore APIs, object selection, object body reads,
exports, direct uploads, and execution locked.
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

from vault.real_provider_receipt_redacted_access_readiness_checkpoint_service import (
    DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,
    get_gp080_status,
    get_provider_receipt_redacted_access_readiness_blockers,
    get_provider_receipt_redacted_access_readiness_checkpoint_record,
    get_provider_receipt_redacted_access_readiness_components,
)

PACK_ID = "VAULT_GP081"
PACK_NAME = "Real Storage Provider Restore Request Lock Contract"
SCHEMA_VERSION = "vault.real_storage_provider_restore_request_lock_contract.v1"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RECEIPT_AND_REDACTED_ACCESS_LAYER"
PREVIOUS_SECTION_TITLE = "Archive Vault — Real Provider Receipt and Redacted Access Layer"
PREVIOUS_SECTION_RANGE = "GP071-GP080"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Restore and Export Governance Layer"
SECTION_RANGE = "GP081-GP090"

NEXT_PACK = "VAULT_GP082_REAL_STORAGE_PROVIDER_RESTORE_ELIGIBILITY_LOCK_CONTRACT"
NEXT_PACK_TITLE = "Real Storage Provider Restore Eligibility Lock Contract"

DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID = "VSPRQLC-GP081-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_restore_request_lock_contract.sqlite"

RESTORE_REQUEST_REQUIREMENT_SPECS = [
    ("restore_request_lock_record_required", "Restore request lock record required", "restore_request_lock"),
    ("source_gp080_readiness_checkpoint_link_required", "Source GP080 readiness checkpoint link required", "source_readiness"),
    ("restore_request_template_only_required", "Restore request template-only state required", "template_only"),
    ("restore_scope_boundary_required", "Restore scope boundary required", "restore_scope"),
    ("restore_authority_boundary_required", "Restore authority boundary required", "restore_authority"),
    ("tower_restore_unlock_required", "Tower restore unlock required", "tower_gate"),
]

RESTORE_REQUEST_POLICIES = [
    ("no_live_restore_request", "No live restore request", "restore_request_lock"),
    ("no_restore_request_submission", "No restore request submission", "submission_lock"),
    ("no_restore_eligibility_check", "No restore eligibility check", "eligibility_lock"),
    ("no_provider_restore_api_configuration", "No provider restore API configuration", "provider_api_lock"),
    ("no_provider_restore_api_call", "No provider restore API call", "provider_call_lock"),
    ("no_restore_job_creation", "No restore job creation", "restore_job_lock"),
    ("no_restore_object_selection", "No restore object selection", "object_selection_lock"),
    ("no_object_body_restore_read", "No object body restore read", "object_body_lock"),
    ("no_export_from_restore_request", "No export from restore request", "export_lock"),
    ("no_execution_from_restore_request", "No execution from restore request", "execution_lock"),
]

FALSE_FIELDS = [
    "restore_request_configured",
    "restore_request_attempted",
    "restore_request_enabled",
    "restore_request_created",
    "restore_request_submitted",
    "restore_request_published",
    "restore_request_finalized",
    "restore_request_approved",
    "restore_request_denied",
    "restore_request_deferred",
    "restore_request_canceled",
    "restore_request_owner_ack_requested",
    "restore_request_owner_ack_recorded",
    "restore_eligibility_check_configured",
    "restore_eligibility_checked",
    "restore_eligibility_passed",
    "restore_authority_verified",
    "restore_scope_selected",
    "restore_target_selected",
    "restore_object_selected",
    "restore_object_identifier_attached",
    "restore_object_key_attached",
    "restore_object_version_attached",
    "restore_object_metadata_attached",
    "restore_object_body_attached",
    "restore_job_configured",
    "restore_job_created",
    "restore_job_started",
    "restore_job_completed",
    "restore_job_failed",
    "provider_restore_api_configured",
    "provider_restore_api_called",
    "provider_restore_session_created",
    "provider_restore_token_created",
    "provider_object_catalog_unlocked",
    "provider_object_listing_configured",
    "provider_object_list_attempted",
    "provider_objects_listed",
    "provider_metadata_imported",
    "provider_metadata_read",
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
    "owner_review_packet_created",
    "owner_review_queue_created",
    "owner_decision_recorded",
    "owner_review_decision_receipt_created",
    "owner_review_closeout_created",
    "tower_unlock_requested",
    "tower_unlock_granted",
    "provider_packet_attached",
    "provider_access_view_attached",
    "provider_metadata_view_attached",
    "export_package_created",
    "export_manifest_created",
    "export_download_enabled",
    "direct_upload_enabled",
    "export_enabled",
    "execution_enabled",
    "vault_done",
]

TRUE_CONTRACT_FIELDS = [
    "restore_request_lock_contract_ready",
    "restore_request_requirements_ready",
    "restore_request_policies_ready",
    "restore_request_blockers_ready",
    "restore_request_validation_ready",
    "restore_request_locked",
    "restore_request_template_only",
    "restore_request_redaction_required",
    "source_gp080_readiness_checkpoint_attached",
    "safe_to_continue_to_gp082",
]

TRUE_REQUIREMENT_FIELDS = [
    "requirement_required",
    "restore_request_locked",
    "template_only",
    "restore_redaction_required",
    "tower_review_required",
]

TRUE_BLOCKER_FIELDS = [
    "blocker_active",
    "blocks_restore_request",
    "blocks_restore_submission",
    "blocks_restore_eligibility_check",
    "blocks_provider_restore_api",
    "blocks_restore_job",
    "blocks_restore_object_selection",
    "blocks_provider_unlock",
    "blocks_object_body_read",
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

def ensure_storage_provider_restore_request_lock_contract_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_CONTRACT_FIELDS)
        false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_restore_request_lock_contracts (
                restore_request_lock_contract_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_title TEXT NOT NULL,
                section_range TEXT NOT NULL,
                previous_section_id TEXT NOT NULL,
                previous_section_range TEXT NOT NULL,
                source_readiness_checkpoint_id TEXT NOT NULL,
                source_readiness_pack_id TEXT NOT NULL,
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
            "restore_request_configured",
            "restore_request_attempted",
            "restore_request_enabled",
            "restore_request_created",
            "restore_request_submitted",
            "restore_request_finalized",
            "restore_request_approved",
            "restore_request_denied",
            "restore_eligibility_checked",
            "restore_authority_verified",
            "restore_scope_selected",
            "restore_target_selected",
            "restore_object_selected",
            "restore_object_identifier_attached",
            "restore_object_key_attached",
            "restore_object_body_attached",
            "restore_job_created",
            "restore_job_started",
            "restore_job_completed",
            "provider_restore_api_configured",
            "provider_restore_api_called",
            "provider_restore_session_created",
            "provider_object_catalog_unlocked",
            "provider_objects_listed",
            "provider_metadata_imported",
            "provider_metadata_read",
            "object_identifier_collected",
            "object_body_read",
            "object_body_view_enabled",
            "object_body_download_enabled",
            "tower_unlock_requested",
            "tower_unlock_granted",
            "export_package_created",
            "export_download_enabled",
            "direct_upload_enabled",
            "export_enabled",
            "execution_enabled",
            "tower_review_granted",
        ]
        req_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_REQUIREMENT_FIELDS)
        req_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in req_false)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_restore_request_requirements (
                restore_request_requirement_id TEXT PRIMARY KEY,
                restore_request_lock_contract_id TEXT NOT NULL,
                source_component_id TEXT NOT NULL,
                source_pack_id TEXT NOT NULL,
                source_component_name TEXT NOT NULL,
                requirement_code TEXT NOT NULL,
                requirement_name TEXT NOT NULL,
                requirement_category TEXT NOT NULL,
                requirement_message TEXT NOT NULL,
                requirement_status TEXT NOT NULL,
                {req_true_sql},
                {req_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(restore_request_lock_contract_id)
                    REFERENCES vault_storage_provider_restore_request_lock_contracts(restore_request_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(restore_request_lock_contract_id, source_component_id, requirement_code)
            )
            """
        )

        policy_false = [
            "policy_verified",
            "restore_request_created",
            "restore_request_submitted",
            "restore_request_finalized",
            "restore_request_approved",
            "restore_request_denied",
            "restore_eligibility_checked",
            "restore_authority_verified",
            "restore_scope_selected",
            "restore_object_selected",
            "restore_object_identifier_attached",
            "restore_object_key_attached",
            "restore_object_body_attached",
            "restore_job_created",
            "restore_job_started",
            "restore_job_completed",
            "provider_restore_api_configured",
            "provider_restore_api_called",
            "provider_restore_session_created",
            "provider_object_catalog_unlocked",
            "provider_objects_listed",
            "provider_metadata_imported",
            "object_identifier_collected",
            "object_body_read",
            "object_body_view_enabled",
            "object_body_download_enabled",
            "tower_unlock_requested",
            "tower_unlock_granted",
            "export_package_created",
            "export_download_enabled",
            "direct_upload_enabled",
            "export_enabled",
            "execution_enabled",
            "tower_review_granted",
        ]
        policy_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in policy_false)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_restore_request_policies (
                restore_request_policy_id TEXT PRIMARY KEY,
                restore_request_lock_contract_id TEXT NOT NULL,
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
                FOREIGN KEY(restore_request_lock_contract_id)
                    REFERENCES vault_storage_provider_restore_request_lock_contracts(restore_request_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(restore_request_lock_contract_id, policy_code)
            )
            """
        )

        blocker_false_sql = ",\n".join(
            f"{field} INTEGER NOT NULL DEFAULT 0"
            for field in ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]
        )
        blocker_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_BLOCKER_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_restore_request_blockers (
                restore_request_blocker_id TEXT PRIMARY KEY,
                restore_request_lock_contract_id TEXT NOT NULL,
                source_readiness_blocker_id TEXT NOT NULL,
                source_blocker_code TEXT NOT NULL,
                source_blocker_category TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                {blocker_true_sql},
                {blocker_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(restore_request_lock_contract_id)
                    REFERENCES vault_storage_provider_restore_request_lock_contracts(restore_request_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(restore_request_lock_contract_id, source_readiness_blocker_id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_restore_request_events (
                event_id TEXT PRIMARY KEY,
                restore_request_lock_contract_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(restore_request_lock_contract_id)
                    REFERENCES vault_storage_provider_restore_request_lock_contracts(restore_request_lock_contract_id)
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
            "vault_storage_provider_restore_request_lock_contracts",
            "vault_storage_provider_restore_request_requirements",
            "vault_storage_provider_restore_request_policies",
            "vault_storage_provider_restore_request_blockers",
            "vault_storage_provider_restore_request_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, contract_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VSPRQLCEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_storage_provider_restore_request_events",
        {
            "event_id": event_id,
            "restore_request_lock_contract_id": contract_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "contract_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_restore_request_lock_contracts").fetchone()["c"]),
            "requirement_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_restore_request_requirements").fetchone()["c"]),
            "policy_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_restore_request_policies").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_restore_request_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_restore_request_events").fetchone()["c"]),
        }

def initialize_real_storage_provider_restore_request_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_restore_request_lock_contract_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            """
            SELECT restore_request_lock_contract_id
            FROM vault_storage_provider_restore_request_lock_contracts
            WHERE restore_request_lock_contract_id = ?
            """,
            (DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,),
        ).fetchone()

        if exists is None:
            source_status = get_gp080_status()["gp080_status"]
            source_checkpoint = get_provider_receipt_redacted_access_readiness_checkpoint_record()["readiness_checkpoint"]
            source_components = get_provider_receipt_redacted_access_readiness_components()["components"]
            source_blockers = get_provider_receipt_redacted_access_readiness_blockers()["blockers"]
            now = _now_iso()

            requirement_count = len(source_components) * len(RESTORE_REQUEST_REQUIREMENT_SPECS)

            contract_data = {
                "schema_version": SCHEMA_VERSION,
                "contract_type": "REAL_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT",
                "source_pack": "VAULT_GP080",
                "source_readiness_checkpoint_id": source_checkpoint["readiness_checkpoint_id"],
                "source_readiness_score": source_status["readiness_score"],
                "source_section_closed": source_status["section_closed"],
                "source_safe_to_continue_to_gp081": source_status["safe_to_continue_to_gp081"],
                "previous_section": PREVIOUS_SECTION_ID,
                "previous_section_title": PREVIOUS_SECTION_TITLE,
                "previous_section_range": PREVIOUS_SECTION_RANGE,
                "section": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "restore_request_requirement_source_component_count": len(source_components),
                "restore_request_requirement_code_count": len(RESTORE_REQUEST_REQUIREMENT_SPECS),
                "restore_request_requirement_count": requirement_count,
                "restore_request_policy_count": len(RESTORE_REQUEST_POLICIES),
                "carried_readiness_blocker_count": len(source_blockers),
                "restore_request_locked": True,
                "restore_request_template_only": True,
                "restore_request_created": False,
                "restore_request_submitted": False,
                "restore_eligibility_checked": False,
                "provider_restore_api_configured": False,
                "provider_restore_api_called": False,
                "restore_job_created": False,
                "restore_object_selected": False,
                "object_body_read": False,
                "export_package_created": False,
                "direct_upload_enabled": False,
                "export_enabled": False,
                "execution_enabled": False,
                "vault_done": False,
                "next_pack": NEXT_PACK,
                "next_pack_title": NEXT_PACK_TITLE,
                "safe_to_continue_to_gp082": True,
            }

            contract_payload = {
                "restore_request_lock_contract_id": DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,
                "pack_id": PACK_ID,
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "previous_section_id": PREVIOUS_SECTION_ID,
                "previous_section_range": PREVIOUS_SECTION_RANGE,
                "source_readiness_checkpoint_id": source_checkpoint["readiness_checkpoint_id"],
                "source_readiness_pack_id": source_checkpoint["pack_id"],
                "contract_status": "REAL_RESTORE_REQUEST_LOCK_CONTRACT_OPEN_TEMPLATE_ONLY_TOWER_LOCKED",
                "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED_FOR_RESTORE_REQUEST",
                "contract_data_json": _json_dumps(contract_data),
                "created_at": now,
                "updated_at": now,
            }
            for field in TRUE_CONTRACT_FIELDS:
                contract_payload[field] = 1
            for field in FALSE_FIELDS:
                contract_payload[field] = 0
            _insert_dict(conn, "vault_storage_provider_restore_request_lock_contracts", contract_payload)

            for component in source_components:
                for code, name, category in RESTORE_REQUEST_REQUIREMENT_SPECS:
                    payload = {
                        "restore_request_requirement_id": f"VSPRQR-{component['pack_id'].replace('VAULT_', '')}-{code.upper().replace('_', '-')}",
                        "restore_request_lock_contract_id": DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,
                        "source_component_id": component["readiness_component_id"],
                        "source_pack_id": component["pack_id"],
                        "source_component_name": component["component_name"],
                        "requirement_code": code,
                        "requirement_name": name,
                        "requirement_category": category,
                        "requirement_message": f"{name} remains required before any restore request can be created.",
                        "requirement_status": "REAL_RESTORE_REQUEST_REQUIREMENT_RECORDED_TEMPLATE_ONLY_TOWER_LOCKED",
                        "created_at": now,
                        "updated_at": now,
                    }
                    for field in TRUE_REQUIREMENT_FIELDS:
                        payload[field] = 1
                    for field in [
                        "requirement_verified",
                        "restore_request_configured",
                        "restore_request_attempted",
                        "restore_request_enabled",
                        "restore_request_created",
                        "restore_request_submitted",
                        "restore_request_finalized",
                        "restore_request_approved",
                        "restore_request_denied",
                        "restore_eligibility_checked",
                        "restore_authority_verified",
                        "restore_scope_selected",
                        "restore_target_selected",
                        "restore_object_selected",
                        "restore_object_identifier_attached",
                        "restore_object_key_attached",
                        "restore_object_body_attached",
                        "restore_job_created",
                        "restore_job_started",
                        "restore_job_completed",
                        "provider_restore_api_configured",
                        "provider_restore_api_called",
                        "provider_restore_session_created",
                        "provider_object_catalog_unlocked",
                        "provider_objects_listed",
                        "provider_metadata_imported",
                        "provider_metadata_read",
                        "object_identifier_collected",
                        "object_body_read",
                        "object_body_view_enabled",
                        "object_body_download_enabled",
                        "tower_unlock_requested",
                        "tower_unlock_granted",
                        "export_package_created",
                        "export_download_enabled",
                        "direct_upload_enabled",
                        "export_enabled",
                        "execution_enabled",
                        "tower_review_granted",
                    ]:
                        payload[field] = 0
                    _insert_dict(conn, "vault_storage_provider_restore_request_requirements", payload)

            for code, name, category in RESTORE_REQUEST_POLICIES:
                payload = {
                    "restore_request_policy_id": f"VSPRQP-{code.upper().replace('_', '-')}",
                    "restore_request_lock_contract_id": DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,
                    "policy_code": code,
                    "policy_name": name,
                    "policy_category": category,
                    "policy_message": f"{name}; GP081 cannot create restore requests, call providers, read object bodies, export, upload, or execute.",
                    "policy_status": "REAL_RESTORE_REQUEST_POLICY_RECORDED_TEMPLATE_ONLY_TOWER_LOCKED",
                    "policy_required": 1,
                    "tower_review_required": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in [
                    "policy_verified",
                    "restore_request_created",
                    "restore_request_submitted",
                    "restore_request_finalized",
                    "restore_request_approved",
                    "restore_request_denied",
                    "restore_eligibility_checked",
                    "restore_authority_verified",
                    "restore_scope_selected",
                    "restore_object_selected",
                    "restore_object_identifier_attached",
                    "restore_object_key_attached",
                    "restore_object_body_attached",
                    "restore_job_created",
                    "restore_job_started",
                    "restore_job_completed",
                    "provider_restore_api_configured",
                    "provider_restore_api_called",
                    "provider_restore_session_created",
                    "provider_object_catalog_unlocked",
                    "provider_objects_listed",
                    "provider_metadata_imported",
                    "object_identifier_collected",
                    "object_body_read",
                    "object_body_view_enabled",
                    "object_body_download_enabled",
                    "tower_unlock_requested",
                    "tower_unlock_granted",
                    "export_package_created",
                    "export_download_enabled",
                    "direct_upload_enabled",
                    "export_enabled",
                    "execution_enabled",
                    "tower_review_granted",
                ]:
                    payload[field] = 0
                _insert_dict(conn, "vault_storage_provider_restore_request_policies", payload)

            for blocker in source_blockers:
                payload = {
                    "restore_request_blocker_id": f"VSPRQB-{blocker['readiness_blocker_id'].replace('VPRRARC-BLOCK-', '')}",
                    "restore_request_lock_contract_id": DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,
                    "source_readiness_blocker_id": blocker["readiness_blocker_id"],
                    "source_blocker_code": blocker["blocker_code"],
                    "source_blocker_category": blocker["blocker_category"],
                    "blocker_name": blocker["blocker_name"],
                    "severity": blocker["severity"],
                    "blocker_status": "REAL_RESTORE_REQUEST_BLOCKER_ACTIVE_CARRIED_FROM_GP080",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_BLOCKER_FIELDS:
                    payload[field] = 1
                for field in ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]:
                    payload[field] = 0
                _insert_dict(conn, "vault_storage_provider_restore_request_blockers", payload)

            for event_type, event_payload in [
                ("REAL_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_CONTRACT_CREATED", contract_data),
                ("SOURCE_GP080_READINESS_CHECKPOINT_ATTACHED", {
                    "source_readiness_checkpoint_id": source_checkpoint["readiness_checkpoint_id"],
                    "source_readiness_pack_id": source_checkpoint["pack_id"],
                    "source_readiness_score": source_status["readiness_score"],
                    "source_section_closed": source_status["section_closed"],
                    "source_safe_to_continue_to_gp081": source_status["safe_to_continue_to_gp081"],
                }),
                ("REAL_RESTORE_REQUEST_REQUIREMENTS_CREATED_TEMPLATE_ONLY", {
                    "requirement_count": requirement_count,
                    "source_component_count": len(source_components),
                }),
                ("REAL_RESTORE_REQUEST_POLICIES_CREATED_TEMPLATE_ONLY", {
                    "policy_count": len(RESTORE_REQUEST_POLICIES),
                }),
                ("REAL_RESTORE_REQUEST_BLOCKERS_CARRIED_FORWARD", {
                    "blocker_count": len(source_blockers),
                }),
                ("RESTORE_REQUEST_LOCKS_CONFIRMED", {
                    "restore_request_created": False,
                    "restore_request_submitted": False,
                    "restore_eligibility_checked": False,
                    "provider_restore_api_configured": False,
                    "provider_restore_api_called": False,
                    "restore_job_created": False,
                    "restore_object_selected": False,
                    "object_body_read": False,
                    "direct_upload_enabled": False,
                    "export_enabled": False,
                    "execution_enabled": False,
                    "vault_done": False,
                }),
            ]:
                _insert_event(conn, DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _sum_counts(table: str, contract_id: str, fields: list[str], db_path: Optional[str] = None) -> Dict[str, int]:
    selects = ["COUNT(*) AS total_count"]
    for field in fields:
        selects.append(f"SUM(CASE WHEN {field} = 1 THEN 1 ELSE 0 END) AS {field}_count")
    with _connect(db_path) as conn:
        row = conn.execute(
            f"SELECT {', '.join(selects)} FROM {table} WHERE restore_request_lock_contract_id = ?",
            (contract_id,),
        ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}

def get_storage_provider_restore_request_lock_contract_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_restore_request_lock_contract(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_restore_request_lock_contracts
            WHERE restore_request_lock_contract_id = ?
            """,
            (DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,),
        ).fetchone()
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "restore_request_lock_contract": _boolify(row, {"contract_data_json": "contract_data"}),
    }

def get_storage_provider_restore_request_requirements(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_restore_request_lock_contract(db_path)
    fields = [
        "requirement_required",
        "requirement_verified",
        "restore_request_locked",
        "template_only",
        "restore_redaction_required",
        "tower_review_required",
        "tower_review_granted",
        "restore_request_created",
        "restore_request_submitted",
        "restore_request_finalized",
        "restore_request_approved",
        "restore_request_denied",
        "restore_eligibility_checked",
        "restore_authority_verified",
        "restore_scope_selected",
        "restore_target_selected",
        "restore_object_selected",
        "restore_object_identifier_attached",
        "restore_object_key_attached",
        "restore_object_body_attached",
        "restore_job_created",
        "restore_job_started",
        "restore_job_completed",
        "provider_restore_api_configured",
        "provider_restore_api_called",
        "provider_restore_session_created",
        "provider_object_catalog_unlocked",
        "provider_objects_listed",
        "provider_metadata_imported",
        "provider_metadata_read",
        "object_identifier_collected",
        "object_body_read",
        "object_body_view_enabled",
        "object_body_download_enabled",
        "tower_unlock_requested",
        "tower_unlock_granted",
        "export_package_created",
        "export_download_enabled",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
    ]
    counts = _sum_counts("vault_storage_provider_restore_request_requirements", DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_restore_request_requirements
            WHERE restore_request_lock_contract_id = ?
            ORDER BY source_pack_id, requirement_category, requirement_code
            """,
            (DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,),
        ).fetchall()
        source_component_count = conn.execute(
            """
            SELECT COUNT(DISTINCT source_component_id) AS c
            FROM vault_storage_provider_restore_request_requirements
            WHERE restore_request_lock_contract_id = ?
            """,
            (DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]
        requirement_code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT requirement_code) AS c
            FROM vault_storage_provider_restore_request_requirements
            WHERE restore_request_lock_contract_id = ?
            """,
            (DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]

    counts["requirement_count"] = counts.pop("total_count")
    counts["source_component_count"] = int(source_component_count)
    counts["requirement_code_count"] = int(requirement_code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "requirements": [_boolify(row) for row in rows]}

def get_storage_provider_restore_request_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_restore_request_lock_contract(db_path)
    fields = [
        "policy_required",
        "policy_verified",
        "tower_review_required",
        "tower_review_granted",
        "restore_request_created",
        "restore_request_submitted",
        "restore_request_finalized",
        "restore_request_approved",
        "restore_request_denied",
        "restore_eligibility_checked",
        "restore_authority_verified",
        "restore_scope_selected",
        "restore_object_selected",
        "restore_object_identifier_attached",
        "restore_object_key_attached",
        "restore_object_body_attached",
        "restore_job_created",
        "restore_job_started",
        "restore_job_completed",
        "provider_restore_api_configured",
        "provider_restore_api_called",
        "provider_restore_session_created",
        "provider_object_catalog_unlocked",
        "provider_objects_listed",
        "provider_metadata_imported",
        "object_identifier_collected",
        "object_body_read",
        "object_body_view_enabled",
        "object_body_download_enabled",
        "tower_unlock_requested",
        "tower_unlock_granted",
        "export_package_created",
        "export_download_enabled",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
    ]
    counts = _sum_counts("vault_storage_provider_restore_request_policies", DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_restore_request_policies
            WHERE restore_request_lock_contract_id = ?
            ORDER BY policy_category, policy_code
            """,
            (DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,),
        ).fetchall()
        policy_code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT policy_code) AS c
            FROM vault_storage_provider_restore_request_policies
            WHERE restore_request_lock_contract_id = ?
            """,
            (DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]

    counts["policy_count"] = counts.pop("total_count")
    counts["policy_code_count"] = int(policy_code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "policies": [_boolify(row) for row in rows]}

def get_storage_provider_restore_request_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_restore_request_lock_contract(db_path)
    fields = TRUE_BLOCKER_FIELDS + ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]
    counts = _sum_counts("vault_storage_provider_restore_request_blockers", DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_restore_request_blockers
            WHERE restore_request_lock_contract_id = ?
            ORDER BY source_blocker_category, source_blocker_code
            """,
            (DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,),
        ).fetchall()

    counts["blocker_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "blockers": [_boolify(row) for row in rows]}

def get_storage_provider_restore_request_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_restore_request_lock_contract(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_restore_request_events
            WHERE restore_request_lock_contract_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,),
        ).fetchall()
    events = [
        {
            "event_id": row["event_id"],
            "restore_request_lock_contract_id": row["restore_request_lock_contract_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def record_storage_provider_restore_request_event(event_type: str, event_payload: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_restore_request_lock_contract(db_path)
    payload = dict(event_payload or {})
    payload.update({
        "write_type": "REAL_STORAGE_PROVIDER_RESTORE_REQUEST_LOCK_EVENT",
        "restore_request_lock_contract_ready": True,
        "restore_request_locked": True,
        "restore_request_template_only": True,
        "restore_request_created": False,
        "restore_request_submitted": False,
        "restore_eligibility_checked": False,
        "provider_restore_api_configured": False,
        "provider_restore_api_called": False,
        "restore_job_created": False,
        "restore_object_selected": False,
        "object_body_read": False,
        "direct_upload_enabled": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    })
    with _connect(db_path) as conn:
        event_id = _insert_event(conn, DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID, event_type, payload)
        conn.commit()
    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "restore_request_lock_contract_id": DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID,
        "real_sqlite_backed": True,
        **payload,
    }

def validate_storage_provider_restore_request_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    contract = get_storage_provider_restore_request_lock_contract_record(db_path)["restore_request_lock_contract"]
    requirements = get_storage_provider_restore_request_requirements(db_path)
    policies = get_storage_provider_restore_request_policies(db_path)
    blockers = get_storage_provider_restore_request_blockers(db_path)
    events = get_storage_provider_restore_request_events(db_path)

    expected_requirements = 9 * len(RESTORE_REQUEST_REQUIREMENT_SPECS)
    expected_policies = len(RESTORE_REQUEST_POLICIES)
    expected_blockers = 18

    false_checks = [(f"NO_CONTRACT_{field.upper()}", contract[field] is False) for field in FALSE_FIELDS]

    checks = [
        ("REAL_SQLITE_RESTORE_REQUEST_LOCK_CONTRACT_EXISTS", contract["restore_request_lock_contract_id"] == DEFAULT_RESTORE_REQUEST_LOCK_CONTRACT_ID),
        ("SOURCE_GP080_READINESS_CHECKPOINT_ATTACHED", contract["source_readiness_checkpoint_id"] == DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID),
        ("NEW_SECTION_GP081_GP090", contract["section_id"] == SECTION_ID and contract["section_range"] == SECTION_RANGE),
        ("PREVIOUS_SECTION_GP071_GP080_ATTACHED", contract["previous_section_id"] == PREVIOUS_SECTION_ID),
        ("RESTORE_REQUEST_LOCK_CONTRACT_READY", contract["restore_request_lock_contract_ready"] is True),
        ("RESTORE_REQUEST_REQUIREMENTS_READY", contract["restore_request_requirements_ready"] is True),
        ("RESTORE_REQUEST_POLICIES_READY", contract["restore_request_policies_ready"] is True),
        ("RESTORE_REQUEST_BLOCKERS_READY", contract["restore_request_blockers_ready"] is True),
        ("RESTORE_REQUEST_VALIDATION_READY", contract["restore_request_validation_ready"] is True),
        ("RESTORE_REQUEST_LOCKED", contract["restore_request_locked"] is True),
        ("RESTORE_REQUEST_TEMPLATE_ONLY", contract["restore_request_template_only"] is True),
        ("SAFE_TO_CONTINUE_TO_GP082", contract["safe_to_continue_to_gp082"] is True),
        ("RESTORE_REQUEST_REQUIREMENTS_EXIST", requirements["requirement_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_REQUIRED", requirements["requirement_required_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_LOCKED", requirements["restore_request_locked_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_TEMPLATE_ONLY", requirements["template_only_count"] == expected_requirements),
        ("NO_REQUIREMENT_RESTORE_REQUEST_CREATED", requirements["restore_request_created_count"] == 0),
        ("NO_REQUIREMENT_RESTORE_REQUEST_SUBMITTED", requirements["restore_request_submitted_count"] == 0),
        ("NO_REQUIREMENT_RESTORE_ELIGIBILITY_CHECKED", requirements["restore_eligibility_checked_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_RESTORE_API_CONFIGURED", requirements["provider_restore_api_configured_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_RESTORE_API_CALLED", requirements["provider_restore_api_called_count"] == 0),
        ("NO_REQUIREMENT_RESTORE_JOB_CREATED", requirements["restore_job_created_count"] == 0),
        ("NO_REQUIREMENT_RESTORE_OBJECT_SELECTED", requirements["restore_object_selected_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY_READ", requirements["object_body_read_count"] == 0),
        ("NO_REQUIREMENT_DIRECT_UPLOAD", requirements["direct_upload_enabled_count"] == 0),
        ("NO_REQUIREMENT_EXPORT", requirements["export_enabled_count"] == 0),
        ("NO_REQUIREMENT_EXECUTION", requirements["execution_enabled_count"] == 0),
        ("RESTORE_REQUEST_POLICIES_EXIST", policies["policy_count"] == expected_policies),
        ("NO_POLICY_RESTORE_REQUEST_CREATED", policies["restore_request_created_count"] == 0),
        ("NO_POLICY_RESTORE_REQUEST_SUBMITTED", policies["restore_request_submitted_count"] == 0),
        ("NO_POLICY_RESTORE_ELIGIBILITY_CHECKED", policies["restore_eligibility_checked_count"] == 0),
        ("NO_POLICY_PROVIDER_RESTORE_API_CONFIGURED", policies["provider_restore_api_configured_count"] == 0),
        ("NO_POLICY_PROVIDER_RESTORE_API_CALLED", policies["provider_restore_api_called_count"] == 0),
        ("NO_POLICY_RESTORE_JOB_CREATED", policies["restore_job_created_count"] == 0),
        ("NO_POLICY_RESTORE_OBJECT_SELECTED", policies["restore_object_selected_count"] == 0),
        ("NO_POLICY_OBJECT_BODY_READ", policies["object_body_read_count"] == 0),
        ("NO_POLICY_DIRECT_UPLOAD", policies["direct_upload_enabled_count"] == 0),
        ("NO_POLICY_EXPORT", policies["export_enabled_count"] == 0),
        ("NO_POLICY_EXECUTION", policies["execution_enabled_count"] == 0),
        ("READINESS_BLOCKERS_CARRIED_FORWARD", blockers["blocker_count"] == expected_blockers),
        ("ALL_BLOCKERS_ACTIVE", blockers["blocker_active_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_RESTORE_REQUEST", blockers["blocks_restore_request_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_RESTORE_SUBMISSION", blockers["blocks_restore_submission_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_RESTORE_ELIGIBILITY_CHECK", blockers["blocks_restore_eligibility_check_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_RESTORE_API", blockers["blocks_provider_restore_api_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_RESTORE_JOB", blockers["blocks_restore_job_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_RESTORE_OBJECT_SELECTION", blockers["blocks_restore_object_selection_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_UNLOCK", blockers["blocks_provider_unlock_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY_READ", blockers["blocks_object_body_read_count"] == expected_blockers),
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
        "safe_to_continue_to_gp082": len(failed) == 0,
        "vault_done": False,
    }

def get_storage_provider_restore_request_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "previous_section": PREVIOUS_SECTION_ID,
            "previous_section_range": PREVIOUS_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp082": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP081 opens the GP081-GP090 restore/export governance layer with a restore request lock contract. Continue to GP082 with restore eligibility while restore creation, provider restore APIs, object selection, object body reads, direct upload, export, and execution remain locked.",
            "carry_forward_rules": [
                "Keep GP080 readiness checkpoint attached.",
                "Keep restore request creation locked.",
                "Keep restore request submission locked.",
                "Keep restore eligibility checks locked until GP082.",
                "Keep provider restore API configuration locked.",
                "Keep provider restore API calls locked.",
                "Keep restore jobs locked.",
                "Keep restore object selection locked.",
                "Keep provider object catalog unlock locked.",
                "Keep provider object listing and metadata import locked.",
                "Keep object body read/view/download locked.",
                "Keep direct upload locked.",
                "Keep export locked.",
                "Keep execution locked.",
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
        "depends_on": ["VAULT_GP080"],
        "foundation_status": "restore_request_lock_contract_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_restore_request_lock_contract",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "previous_section": PREVIOUS_SECTION_ID,
        "previous_section_range": PREVIOUS_SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-storage-provider-restore-request-lock-contract",
        "json_route": "/vault/real-storage-provider-restore-request-lock-contract.json",
        "record_route": "/vault/storage-provider-restore-request-lock-contract-record.json",
        "requirements_route": "/vault/storage-provider-restore-request-requirements.json",
        "policies_route": "/vault/storage-provider-restore-request-policies.json",
        "blockers_route": "/vault/storage-provider-restore-request-blockers.json",
        "events_route": "/vault/storage-provider-restore-request-events.json",
        "validation_route": "/vault/storage-provider-restore-request-validation.json",
        "next_step_route": "/vault/storage-provider-restore-request-next-step.json",
        "gp081_status_route": "/vault/gp081-status.json",
    }

def get_real_storage_provider_restore_request_lock_contract_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_restore_request_lock_contract(db_path)
    contract = get_storage_provider_restore_request_lock_contract_record(db_path)["restore_request_lock_contract"]
    requirements = get_storage_provider_restore_request_requirements(db_path)
    policies = get_storage_provider_restore_request_policies(db_path)
    blockers = get_storage_provider_restore_request_blockers(db_path)
    events = get_storage_provider_restore_request_events(db_path)
    validation = validate_storage_provider_restore_request_lock_contract(db_path)

    truth = {
        "real_storage_provider_restore_request_lock_contract_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "source_gp080_readiness_checkpoint_attached": contract["source_readiness_checkpoint_id"] == DEFAULT_PROVIDER_RECEIPT_REDACTED_ACCESS_READINESS_CHECKPOINT_ID,
        "validation_passed": validation["valid"],
        "restore_request_lock_contract_ready": contract["restore_request_lock_contract_ready"],
        "restore_request_locked": contract["restore_request_locked"],
        "restore_request_template_only": contract["restore_request_template_only"],
        "requirement_count": requirements["requirement_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "event_count": events["event_count"],
        "restore_request_created": contract["restore_request_created"],
        "restore_request_submitted": contract["restore_request_submitted"],
        "restore_eligibility_checked": contract["restore_eligibility_checked"],
        "provider_restore_api_configured": contract["provider_restore_api_configured"],
        "provider_restore_api_called": contract["provider_restore_api_called"],
        "restore_job_created": contract["restore_job_created"],
        "restore_object_selected": contract["restore_object_selected"],
        "provider_object_catalog_unlocked": contract["provider_object_catalog_unlocked"],
        "provider_objects_listed": contract["provider_objects_listed"],
        "provider_metadata_imported": contract["provider_metadata_imported"],
        "object_identifier_collected": contract["object_identifier_collected"],
        "object_body_read": contract["object_body_read"],
        "object_body_view_enabled": contract["object_body_view_enabled"],
        "object_body_download_enabled": contract["object_body_download_enabled"],
        "tower_unlock_requested": contract["tower_unlock_requested"],
        "tower_unlock_granted": contract["tower_unlock_granted"],
        "export_package_created": contract["export_package_created"],
        "export_download_enabled": contract["export_download_enabled"],
        "direct_upload_enabled": contract["direct_upload_enabled"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "safe_to_continue_to_gp082": validation["safe_to_continue_to_gp082"],
        "vault_done": contract["vault_done"],
    }

    return {
        "pack": _pack_payload(),
        "restore_request_truth": truth,
        "store": init,
        "restore_request_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_restore_request_next_step()["next_step"],
    }

def get_gp081_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_restore_request_lock_contract_home(db_path)
    contract = home["restore_request_lock_contract"]
    requirements = home["requirements"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp081_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "previous_section_id": PREVIOUS_SECTION_ID,
            "previous_section_range": PREVIOUS_SECTION_RANGE,
            "real_storage_provider_restore_request_lock_contract_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_contract_count": home["store"]["contract_count"],
            "real_requirement_count": home["store"]["requirement_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp080_readiness_checkpoint_attached": True,
            "restore_request_lock_contract_ready": contract["restore_request_lock_contract_ready"],
            "restore_request_requirements_ready": contract["restore_request_requirements_ready"],
            "restore_request_policies_ready": contract["restore_request_policies_ready"],
            "restore_request_blockers_ready": contract["restore_request_blockers_ready"],
            "restore_request_validation_ready": contract["restore_request_validation_ready"],
            "restore_request_locked": contract["restore_request_locked"],
            "restore_request_template_only": contract["restore_request_template_only"],
            "restore_request_redaction_required": contract["restore_request_redaction_required"],
            "source_component_count": requirements["source_component_count"],
            "requirement_code_count": requirements["requirement_code_count"],
            "policy_code_count": policies["policy_code_count"],
            "blocker_count": blockers["blocker_count"],
            "restore_request_created_count": requirements["restore_request_created_count"] + policies["restore_request_created_count"],
            "restore_request_submitted_count": requirements["restore_request_submitted_count"] + policies["restore_request_submitted_count"],
            "restore_request_finalized_count": requirements["restore_request_finalized_count"] + policies["restore_request_finalized_count"],
            "restore_eligibility_checked_count": requirements["restore_eligibility_checked_count"] + policies["restore_eligibility_checked_count"],
            "provider_restore_api_configured_count": requirements["provider_restore_api_configured_count"] + policies["provider_restore_api_configured_count"],
            "provider_restore_api_called_count": requirements["provider_restore_api_called_count"] + policies["provider_restore_api_called_count"],
            "restore_job_created_count": requirements["restore_job_created_count"] + policies["restore_job_created_count"],
            "restore_object_selected_count": requirements["restore_object_selected_count"] + policies["restore_object_selected_count"],
            "provider_object_catalog_unlocked_count": requirements["provider_object_catalog_unlocked_count"] + policies["provider_object_catalog_unlocked_count"],
            "provider_objects_listed_count": requirements["provider_objects_listed_count"] + policies["provider_objects_listed_count"],
            "provider_metadata_imported_count": requirements["provider_metadata_imported_count"] + policies["provider_metadata_imported_count"],
            "object_identifier_collected_count": requirements["object_identifier_collected_count"] + policies["object_identifier_collected_count"],
            "object_body_read_count": requirements["object_body_read_count"] + policies["object_body_read_count"],
            "object_body_view_enabled_count": requirements["object_body_view_enabled_count"] + policies["object_body_view_enabled_count"],
            "object_body_download_enabled_count": requirements["object_body_download_enabled_count"] + policies["object_body_download_enabled_count"],
            "tower_unlock_requested_count": requirements["tower_unlock_requested_count"] + policies["tower_unlock_requested_count"],
            "tower_unlock_granted_count": requirements["tower_unlock_granted_count"] + policies["tower_unlock_granted_count"],
            "export_package_created_count": requirements["export_package_created_count"] + policies["export_package_created_count"],
            "direct_upload_enabled_count": requirements["direct_upload_enabled_count"] + policies["direct_upload_enabled_count"],
            "export_enabled_count": requirements["export_enabled_count"] + policies["export_enabled_count"],
            "execution_enabled_count": requirements["execution_enabled_count"] + policies["execution_enabled_count"],
            "blocks_restore_request_count": blockers["blocks_restore_request_count"],
            "blocks_restore_submission_count": blockers["blocks_restore_submission_count"],
            "blocks_restore_eligibility_check_count": blockers["blocks_restore_eligibility_check_count"],
            "blocks_provider_restore_api_count": blockers["blocks_provider_restore_api_count"],
            "blocks_restore_job_count": blockers["blocks_restore_job_count"],
            "blocks_restore_object_selection_count": blockers["blocks_restore_object_selection_count"],
            "blocks_provider_unlock_count": blockers["blocks_provider_unlock_count"],
            "blocks_object_body_read_count": blockers["blocks_object_body_read_count"],
            "blocks_direct_upload_count": blockers["blocks_direct_upload_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "tower_review_granted_count": blockers["tower_review_granted_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp082": validation["safe_to_continue_to_gp082"],
            "foundation_status": "restore_request_lock_contract_ready_safe_to_continue_not_done",
            "restore_request_configured": contract["restore_request_configured"],
            "restore_request_attempted": contract["restore_request_attempted"],
            "restore_request_enabled": contract["restore_request_enabled"],
            "restore_request_created": contract["restore_request_created"],
            "restore_request_submitted": contract["restore_request_submitted"],
            "restore_request_finalized": contract["restore_request_finalized"],
            "restore_request_approved": contract["restore_request_approved"],
            "restore_request_denied": contract["restore_request_denied"],
            "restore_eligibility_checked": contract["restore_eligibility_checked"],
            "restore_authority_verified": contract["restore_authority_verified"],
            "restore_scope_selected": contract["restore_scope_selected"],
            "restore_target_selected": contract["restore_target_selected"],
            "restore_object_selected": contract["restore_object_selected"],
            "restore_object_identifier_attached": contract["restore_object_identifier_attached"],
            "restore_object_key_attached": contract["restore_object_key_attached"],
            "restore_object_body_attached": contract["restore_object_body_attached"],
            "restore_job_created": contract["restore_job_created"],
            "restore_job_started": contract["restore_job_started"],
            "restore_job_completed": contract["restore_job_completed"],
            "provider_restore_api_configured": contract["provider_restore_api_configured"],
            "provider_restore_api_called": contract["provider_restore_api_called"],
            "provider_restore_session_created": contract["provider_restore_session_created"],
            "provider_object_catalog_unlocked": contract["provider_object_catalog_unlocked"],
            "provider_objects_listed": contract["provider_objects_listed"],
            "provider_metadata_imported": contract["provider_metadata_imported"],
            "object_identifier_collected": contract["object_identifier_collected"],
            "object_body_read": contract["object_body_read"],
            "object_body_view_enabled": contract["object_body_view_enabled"],
            "object_body_download_enabled": contract["object_body_download_enabled"],
            "tower_unlock_requested": contract["tower_unlock_requested"],
            "tower_unlock_granted": contract["tower_unlock_granted"],
            "export_package_created": contract["export_package_created"],
            "export_download_enabled": contract["export_download_enabled"],
            "direct_upload_enabled": contract["direct_upload_enabled"],
            "export_enabled": contract["export_enabled"],
            "execution_enabled": contract["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp081",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "restore_request_truth": home["restore_request_truth"],
        "routes": home["routes"],
        "restore_request_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }

def render_real_storage_provider_restore_request_lock_contract_page() -> str:
    home = get_real_storage_provider_restore_request_lock_contract_home()
    truth = home["restore_request_truth"]
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
<title>Vault Real Storage Provider Restore Request Lock Contract · GP081</title>
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
    <div class="eyebrow">Archive Vault · Giant Pack 081</div>
    <div class="eyebrow">Real Provider Restore and Export Governance Layer · GP081-GP090</div>
    <h1>Real Storage Provider Restore Request Lock Contract</h1>
    <p>GP081 opens the restore/export governance layer with a real restore request lock contract. It does not create restore requests, call provider APIs, read object bodies, export, upload, or execute.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['requirement_count']}</strong><span>restore requirements</span></div>
      <div class="metric"><strong>{truth['policy_count']}</strong><span>restore policies</span></div>
      <div class="metric"><strong>{truth['restore_request_created']}</strong><span>restore requests created</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">New section opened</span>
      <span class="pill ok">Restore request locked</span>
      <span class="pill ok">Real SQLite-backed</span>
      <span class="pill danger">No restore request</span>
      <span class="pill danger">No provider API</span>
      <span class="pill danger">No object body read</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Restore Request Requirements Preview</h2>
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
    <h2>GP081 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['requirements_route'])}</code>
      <code>{escape(routes['policies_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_step_route'])}</code>
      <code>{escape(routes['gp081_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
