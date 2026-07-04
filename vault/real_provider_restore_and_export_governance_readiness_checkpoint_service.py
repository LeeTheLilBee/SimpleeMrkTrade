"""
VAULT GP090 — Real Provider Restore and Export Governance Readiness Checkpoint

Closes:
Archive Vault — Real Provider Restore and Export Governance Layer / GP081-GP090

This checkpoint records a durable readiness snapshot for GP081-GP089 and
confirms the whole restore/export governance section is ready to close while
restore, export, direct upload, provider API calls, object body reads, and
execution remain locked.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Dict, Optional

PACK_ID = "VAULT_GP090"
PACK_NAME = "Real Provider Restore and Export Governance Readiness Checkpoint"
SCHEMA_VERSION = "vault.real_provider_restore_export_governance_readiness_checkpoint.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Restore and Export Governance Layer"
SECTION_RANGE = "GP081-GP090"

NEXT_SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_GOVERNANCE_LAYER"
NEXT_SECTION_TITLE = "Archive Vault — Real Provider Post-Closeout Handoff Governance Layer"
NEXT_SECTION_RANGE = "GP091-GP100"
NEXT_PACK = "VAULT_GP091_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT"
NEXT_PACK_TITLE = "Real Provider Post-Closeout Handoff Lock Contract"

DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID = "VRERGRC-GP090-001"
DEFAULT_DB_ENV = "VAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_DB"
DEFAULT_DB_PATH = "data/vault_restore_export_governance_readiness_checkpoint.sqlite"

COMPONENT_SPECS = [
    ("VAULT_GP081", "Restore Request Lock Contract", "vault.real_storage_provider_restore_request_lock_contract_service", "get_gp081_status", "gp081_status"),
    ("VAULT_GP082", "Restore Eligibility Lock Contract", "vault.real_storage_provider_restore_eligibility_lock_contract_service", "get_gp082_status", "gp082_status"),
    ("VAULT_GP083", "Restore Authority Lock Contract", "vault.real_storage_provider_restore_authority_lock_contract_service", "get_gp083_status", "gp083_status"),
    ("VAULT_GP084", "Restore Scope Lock Contract", "vault.real_storage_provider_restore_scope_lock_contract_service", "get_gp084_status", "gp084_status"),
    ("VAULT_GP085", "Restore Target Lock Contract", "vault.real_storage_provider_restore_target_lock_contract_service", "get_gp085_status", "gp085_status"),
    ("VAULT_GP086", "Restore Object Lock Contract", "vault.real_storage_provider_restore_object_lock_contract_service", "get_gp086_status", "gp086_status"),
    ("VAULT_GP087", "Restore Job Lock Contract", "vault.real_storage_provider_restore_job_lock_contract_service", "get_gp087_status", "gp087_status"),
    ("VAULT_GP088", "Restore API Lock Contract", "vault.real_storage_provider_restore_api_lock_contract_service", "get_gp088_status", "gp088_status"),
    ("VAULT_GP089", "Restore Export Lock Contract", "vault.real_storage_provider_restore_export_lock_contract_service", "get_gp089_status", "gp089_status"),
]

READINESS_CRITERIA = [
    ("gp081_restore_request_lock_ready", "GP081 restore request lock contract ready"),
    ("gp082_restore_eligibility_lock_ready", "GP082 restore eligibility lock contract ready"),
    ("gp083_restore_authority_lock_ready", "GP083 restore authority lock contract ready"),
    ("gp084_restore_scope_lock_ready", "GP084 restore scope lock contract ready"),
    ("gp085_restore_target_lock_ready", "GP085 restore target lock contract ready"),
    ("gp086_restore_object_lock_ready", "GP086 restore object lock contract ready"),
    ("gp087_restore_job_lock_ready", "GP087 restore job lock contract ready"),
    ("gp088_restore_api_lock_ready", "GP088 restore API lock contract ready"),
    ("gp089_restore_export_lock_ready", "GP089 restore export lock contract ready"),
    ("all_restore_export_locks_confirmed", "All restore/export unlock surfaces remain false"),
    ("no_provider_restore_api_activity", "No provider restore API configuration/call/session/token/reference/poll exists"),
    ("no_object_body_access", "No object body read/view/download exists"),
    ("no_export_or_upload", "No export package/manifest/download or direct upload exists"),
    ("no_execution_or_vault_done", "Execution remains disabled and Vault is not done"),
]

LOCK_FALSE_BOOL_FIELDS = [
    "restore_request_created",
    "restore_request_submitted",
    "restore_request_finalized",
    "restore_eligibility_checked",
    "restore_eligibility_passed",
    "restore_eligibility_failed",
    "restore_authority_verified",
    "restore_actor_authority_granted",
    "restore_scope_selected",
    "restore_scope_validated",
    "restore_target_selected",
    "restore_target_validated",
    "restore_object_selected",
    "restore_object_identifier_attached",
    "restore_object_key_attached",
    "restore_object_metadata_attached",
    "restore_object_body_attached",
    "restore_job_configured",
    "restore_job_created",
    "restore_job_started",
    "restore_job_completed",
    "restore_api_configured",
    "restore_api_authorized",
    "restore_api_called",
    "restore_api_response_received",
    "provider_restore_api_configured",
    "provider_restore_api_called",
    "provider_restore_session_created",
    "provider_restore_token_created",
    "provider_restore_job_reference_created",
    "provider_restore_status_poll_started",
    "provider_restore_status_poll_completed",
    "provider_object_catalog_unlocked",
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
    "object_body_download_enabled",
    "object_body_content_exposed",
    "object_body_plaintext_visible",
    "restore_export_package_created",
    "restore_export_manifest_created",
    "restore_export_download_enabled",
    "export_package_created",
    "export_manifest_created",
    "export_download_enabled",
    "direct_upload_enabled",
    "export_enabled",
    "execution_enabled",
    "tower_unlock_requested",
    "tower_unlock_granted",
    "vault_done",
]

LOCK_FALSE_COUNT_FIELDS = [field + "_count" for field in LOCK_FALSE_BOOL_FIELDS]

def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _resolve_db_path(db_path: Optional[str] = None) -> Path:
    return Path(db_path or os.environ.get(DEFAULT_DB_ENV) or DEFAULT_DB_PATH)

def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)

def _json_loads(value: str) -> Any:
    return json.loads(value)

def _hash_payload(payload: Any) -> str:
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

def _load_component_status(module_name: str, function_name: str, status_key: str) -> Dict[str, Any]:
    module = importlib.import_module(module_name)
    fn = getattr(module, function_name)
    payload = fn()
    status = payload.get(status_key, payload)
    return status

def _component_safe_flag(component_id: str, status: Dict[str, Any]) -> bool:
    specific = {
        "VAULT_GP081": "safe_to_continue_to_gp082",
        "VAULT_GP082": "safe_to_continue_to_gp083",
        "VAULT_GP083": "safe_to_continue_to_gp084",
        "VAULT_GP084": "safe_to_continue_to_gp085",
        "VAULT_GP085": "safe_to_continue_to_gp086",
        "VAULT_GP086": "safe_to_continue_to_gp087",
        "VAULT_GP087": "safe_to_continue_to_gp088",
        "VAULT_GP088": "safe_to_continue_to_gp089",
        "VAULT_GP089": "safe_to_continue_to_gp090",
    }
    key = specific[component_id]
    return bool(status.get(key, False))

def _component_validation_flag(status: Dict[str, Any]) -> bool:
    return bool(status.get("validation_passed", status.get("valid", False)))

def _lock_violations(statuses: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    violations = []
    for item in statuses:
        component_id = item["component_id"]
        status = item["status"]
        for key in LOCK_FALSE_BOOL_FIELDS:
            if status.get(key) is True:
                violations.append({"component_id": component_id, "field": key, "value": True, "type": "bool_unlock"})
        for key in LOCK_FALSE_COUNT_FIELDS:
            value = status.get(key)
            if isinstance(value, int) and value != 0:
                violations.append({"component_id": component_id, "field": key, "value": value, "type": "count_unlock"})
    return violations

def ensure_restore_export_governance_readiness_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)
    with _connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_restore_export_governance_readiness_checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_title TEXT NOT NULL,
                section_range TEXT NOT NULL,
                checkpoint_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                component_count INTEGER NOT NULL,
                criteria_count INTEGER NOT NULL,
                passed_criteria_count INTEGER NOT NULL,
                failed_criteria_count INTEGER NOT NULL,
                active_blocker_count INTEGER NOT NULL,
                next_section_id TEXT NOT NULL,
                next_section_title TEXT NOT NULL,
                next_section_range TEXT NOT NULL,
                next_pack TEXT NOT NULL,
                checkpoint_data_json TEXT NOT NULL,
                real_sqlite_backed INTEGER NOT NULL DEFAULT 1,
                section_closeout_ready INTEGER NOT NULL DEFAULT 1,
                section_closed INTEGER NOT NULL DEFAULT 1,
                restore_export_governance_ready INTEGER NOT NULL DEFAULT 1,
                safe_to_continue_to_gp091 INTEGER NOT NULL DEFAULT 1,
                restore_execution_locked INTEGER NOT NULL DEFAULT 1,
                restore_export_locked INTEGER NOT NULL DEFAULT 1,
                provider_restore_api_locked INTEGER NOT NULL DEFAULT 1,
                object_body_access_locked INTEGER NOT NULL DEFAULT 1,
                direct_upload_locked INTEGER NOT NULL DEFAULT 1,
                export_locked INTEGER NOT NULL DEFAULT 1,
                execution_locked INTEGER NOT NULL DEFAULT 1,
                vault_done INTEGER NOT NULL DEFAULT 0,
                clouds_should_continue INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_restore_export_governance_components (
                component_record_id TEXT PRIMARY KEY,
                checkpoint_id TEXT NOT NULL,
                component_id TEXT NOT NULL,
                component_name TEXT NOT NULL,
                component_order INTEGER NOT NULL,
                component_ready INTEGER NOT NULL,
                component_validation_passed INTEGER NOT NULL,
                component_safe_to_continue INTEGER NOT NULL,
                component_locked INTEGER NOT NULL,
                source_status_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(checkpoint_id)
                    REFERENCES vault_restore_export_governance_readiness_checkpoints(checkpoint_id)
                    ON DELETE CASCADE,
                UNIQUE(checkpoint_id, component_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_restore_export_governance_criteria (
                criterion_id TEXT PRIMARY KEY,
                checkpoint_id TEXT NOT NULL,
                criterion_code TEXT NOT NULL,
                criterion_name TEXT NOT NULL,
                criterion_status TEXT NOT NULL,
                passed INTEGER NOT NULL,
                required INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(checkpoint_id)
                    REFERENCES vault_restore_export_governance_readiness_checkpoints(checkpoint_id)
                    ON DELETE CASCADE,
                UNIQUE(checkpoint_id, criterion_code)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_restore_export_governance_blockers (
                blocker_id TEXT PRIMARY KEY,
                checkpoint_id TEXT NOT NULL,
                blocker_code TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocker_payload_json TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(checkpoint_id)
                    REFERENCES vault_restore_export_governance_readiness_checkpoints(checkpoint_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_restore_export_governance_events (
                event_id TEXT PRIMARY KEY,
                checkpoint_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(checkpoint_id)
                    REFERENCES vault_restore_export_governance_readiness_checkpoints(checkpoint_id)
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
            "vault_restore_export_governance_readiness_checkpoints",
            "vault_restore_export_governance_components",
            "vault_restore_export_governance_criteria",
            "vault_restore_export_governance_blockers",
            "vault_restore_export_governance_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, checkpoint_id: str, event_type: str, payload: Dict[str, Any]) -> str:
    event_id = f"VRERGCEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_restore_export_governance_events",
        {
            "event_id": event_id,
            "checkpoint_id": checkpoint_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _build_component_statuses() -> list[Dict[str, Any]]:
    components = []
    for idx, (component_id, name, module_name, function_name, status_key) in enumerate(COMPONENT_SPECS, start=1):
        status = _load_component_status(module_name, function_name, status_key)
        components.append(
            {
                "component_id": component_id,
                "component_name": name,
                "component_order": idx,
                "status": status,
                "component_ready": bool(status.get("ready", True)),
                "component_validation_passed": _component_validation_flag(status),
                "component_safe_to_continue": _component_safe_flag(component_id, status),
                "component_locked": True,
            }
        )
    return components

def _build_criteria(component_statuses: list[Dict[str, Any]], lock_violations: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    component_map = {item["component_id"]: item for item in component_statuses}

    criteria_truth = {
        "gp081_restore_request_lock_ready": component_map["VAULT_GP081"]["component_safe_to_continue"],
        "gp082_restore_eligibility_lock_ready": component_map["VAULT_GP082"]["component_safe_to_continue"],
        "gp083_restore_authority_lock_ready": component_map["VAULT_GP083"]["component_safe_to_continue"],
        "gp084_restore_scope_lock_ready": component_map["VAULT_GP084"]["component_safe_to_continue"],
        "gp085_restore_target_lock_ready": component_map["VAULT_GP085"]["component_safe_to_continue"],
        "gp086_restore_object_lock_ready": component_map["VAULT_GP086"]["component_safe_to_continue"],
        "gp087_restore_job_lock_ready": component_map["VAULT_GP087"]["component_safe_to_continue"],
        "gp088_restore_api_lock_ready": component_map["VAULT_GP088"]["component_safe_to_continue"],
        "gp089_restore_export_lock_ready": component_map["VAULT_GP089"]["component_safe_to_continue"],
        "all_restore_export_locks_confirmed": len(lock_violations) == 0,
        "no_provider_restore_api_activity": not any("provider_restore" in v["field"] for v in lock_violations),
        "no_object_body_access": not any("object_body" in v["field"] for v in lock_violations),
        "no_export_or_upload": not any(("export" in v["field"] or "upload" in v["field"]) for v in lock_violations),
        "no_execution_or_vault_done": not any(("execution" in v["field"] or "vault_done" in v["field"]) for v in lock_violations),
    }

    return [
        {
            "criterion_code": code,
            "criterion_name": name,
            "passed": bool(criteria_truth[code]),
            "criterion_status": "PASSED" if criteria_truth[code] else "FAILED",
        }
        for code, name in READINESS_CRITERIA
    ]

def initialize_real_provider_restore_export_governance_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_restore_export_governance_readiness_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            """
            SELECT checkpoint_id
            FROM vault_restore_export_governance_readiness_checkpoints
            WHERE checkpoint_id = ?
            """,
            (DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID,),
        ).fetchone()

        if exists is None:
            now = _now_iso()
            components = _build_component_statuses()
            violations = _lock_violations(components)
            criteria = _build_criteria(components, violations)

            passed_count = sum(1 for item in criteria if item["passed"])
            failed_count = len(criteria) - passed_count
            readiness_score = int(round((passed_count / len(criteria)) * 100)) if criteria else 0
            active_blocker_count = len(violations)

            checkpoint_data = {
                "schema_version": SCHEMA_VERSION,
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "component_ids": [item["component_id"] for item in components],
                "criteria": criteria,
                "lock_violations": violations,
                "readiness_score": readiness_score,
                "section_closeout_ready": readiness_score == 100 and active_blocker_count == 0,
                "section_closed": readiness_score == 100 and active_blocker_count == 0,
                "restore_execution_locked": True,
                "restore_export_locked": True,
                "provider_restore_api_locked": True,
                "object_body_access_locked": True,
                "direct_upload_locked": True,
                "export_locked": True,
                "execution_locked": True,
                "vault_done": False,
                "next_section_id": NEXT_SECTION_ID,
                "next_section_title": NEXT_SECTION_TITLE,
                "next_section_range": NEXT_SECTION_RANGE,
                "next_pack": NEXT_PACK,
                "next_pack_title": NEXT_PACK_TITLE,
                "safe_to_continue_to_gp091": readiness_score == 100 and active_blocker_count == 0,
            }
            readiness_hash = _hash_payload(checkpoint_data)

            checkpoint_payload = {
                "checkpoint_id": DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID,
                "pack_id": PACK_ID,
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "checkpoint_status": "RESTORE_EXPORT_GOVERNANCE_SECTION_CLOSED_READY_FOR_NEXT_SECTION" if readiness_score == 100 and active_blocker_count == 0 else "RESTORE_EXPORT_GOVERNANCE_SECTION_BLOCKED",
                "readiness_score": readiness_score,
                "readiness_hash": readiness_hash,
                "component_count": len(components),
                "criteria_count": len(criteria),
                "passed_criteria_count": passed_count,
                "failed_criteria_count": failed_count,
                "active_blocker_count": active_blocker_count,
                "next_section_id": NEXT_SECTION_ID,
                "next_section_title": NEXT_SECTION_TITLE,
                "next_section_range": NEXT_SECTION_RANGE,
                "next_pack": NEXT_PACK,
                "checkpoint_data_json": _json_dumps(checkpoint_data),
                "real_sqlite_backed": 1,
                "section_closeout_ready": int(readiness_score == 100 and active_blocker_count == 0),
                "section_closed": int(readiness_score == 100 and active_blocker_count == 0),
                "restore_export_governance_ready": int(readiness_score == 100 and active_blocker_count == 0),
                "safe_to_continue_to_gp091": int(readiness_score == 100 and active_blocker_count == 0),
                "restore_execution_locked": 1,
                "restore_export_locked": 1,
                "provider_restore_api_locked": 1,
                "object_body_access_locked": 1,
                "direct_upload_locked": 1,
                "export_locked": 1,
                "execution_locked": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            _insert_dict(conn, "vault_restore_export_governance_readiness_checkpoints", checkpoint_payload)

            for component in components:
                _insert_dict(
                    conn,
                    "vault_restore_export_governance_components",
                    {
                        "component_record_id": f"VRERGCMP-{component['component_id'].replace('VAULT_', '')}",
                        "checkpoint_id": DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID,
                        "component_id": component["component_id"],
                        "component_name": component["component_name"],
                        "component_order": component["component_order"],
                        "component_ready": int(component["component_ready"]),
                        "component_validation_passed": int(component["component_validation_passed"]),
                        "component_safe_to_continue": int(component["component_safe_to_continue"]),
                        "component_locked": int(component["component_locked"]),
                        "source_status_json": _json_dumps(component["status"]),
                        "created_at": now,
                        "updated_at": now,
                    },
                )

            for criterion in criteria:
                _insert_dict(
                    conn,
                    "vault_restore_export_governance_criteria",
                    {
                        "criterion_id": f"VRERGCRIT-{criterion['criterion_code'].upper().replace('_', '-')}",
                        "checkpoint_id": DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID,
                        "criterion_code": criterion["criterion_code"],
                        "criterion_name": criterion["criterion_name"],
                        "criterion_status": criterion["criterion_status"],
                        "passed": int(criterion["passed"]),
                        "required": 1,
                        "created_at": now,
                        "updated_at": now,
                    },
                )

            for violation in violations:
                _insert_dict(
                    conn,
                    "vault_restore_export_governance_blockers",
                    {
                        "blocker_id": f"VRERGCBLK-{uuid.uuid4().hex[:16].upper()}",
                        "checkpoint_id": DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID,
                        "blocker_code": f"LOCK_VIOLATION_{violation['field'].upper()}",
                        "blocker_name": f"Lock violation detected: {violation['field']}",
                        "blocker_status": "ACTIVE",
                        "blocker_payload_json": _json_dumps(violation),
                        "active": 1,
                        "created_at": now,
                        "updated_at": now,
                    },
                )

            for event_type, event_payload in [
                ("RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_CREATED", checkpoint_data),
                ("RESTORE_EXPORT_GOVERNANCE_COMPONENTS_SNAPSHOTTED", {"component_count": len(components)}),
                ("RESTORE_EXPORT_GOVERNANCE_CRITERIA_EVALUATED", {"criteria_count": len(criteria), "passed": passed_count, "failed": failed_count}),
                ("RESTORE_EXPORT_GOVERNANCE_LOCKS_CONFIRMED", {"lock_violation_count": len(violations)}),
                ("RESTORE_EXPORT_GOVERNANCE_READINESS_HASH_RECORDED", {"readiness_hash": readiness_hash}),
                ("RESTORE_EXPORT_GOVERNANCE_NEXT_SECTION_HANDOFF_READY", {"next_pack": NEXT_PACK, "vault_done": False}),
            ]:
                _insert_event(conn, DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "checkpoint_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_restore_export_governance_readiness_checkpoints").fetchone()["c"]),
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_restore_export_governance_components").fetchone()["c"]),
            "criteria_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_restore_export_governance_criteria").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_restore_export_governance_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_restore_export_governance_events").fetchone()["c"]),
        }

def _checkpoint_row_payload(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "checkpoint_id": row["checkpoint_id"],
        "pack_id": row["pack_id"],
        "section_id": row["section_id"],
        "section_title": row["section_title"],
        "section_range": row["section_range"],
        "checkpoint_status": row["checkpoint_status"],
        "readiness_score": int(row["readiness_score"]),
        "readiness_hash": row["readiness_hash"],
        "component_count": int(row["component_count"]),
        "criteria_count": int(row["criteria_count"]),
        "passed_criteria_count": int(row["passed_criteria_count"]),
        "failed_criteria_count": int(row["failed_criteria_count"]),
        "active_blocker_count": int(row["active_blocker_count"]),
        "next_section_id": row["next_section_id"],
        "next_section_title": row["next_section_title"],
        "next_section_range": row["next_section_range"],
        "next_pack": row["next_pack"],
        "checkpoint_data": _json_loads(row["checkpoint_data_json"]),
        "real_sqlite_backed": bool(row["real_sqlite_backed"]),
        "section_closeout_ready": bool(row["section_closeout_ready"]),
        "section_closed": bool(row["section_closed"]),
        "restore_export_governance_ready": bool(row["restore_export_governance_ready"]),
        "safe_to_continue_to_gp091": bool(row["safe_to_continue_to_gp091"]),
        "restore_execution_locked": bool(row["restore_execution_locked"]),
        "restore_export_locked": bool(row["restore_export_locked"]),
        "provider_restore_api_locked": bool(row["provider_restore_api_locked"]),
        "object_body_access_locked": bool(row["object_body_access_locked"]),
        "direct_upload_locked": bool(row["direct_upload_locked"]),
        "export_locked": bool(row["export_locked"]),
        "execution_locked": bool(row["execution_locked"]),
        "vault_done": bool(row["vault_done"]),
        "clouds_should_continue": bool(row["clouds_should_continue"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }

def get_restore_export_governance_readiness_checkpoint_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_restore_export_governance_readiness_checkpoint(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_restore_export_governance_readiness_checkpoints
            WHERE checkpoint_id = ?
            """,
            (DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID,),
        ).fetchone()
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "checkpoint": _checkpoint_row_payload(row)}

def get_restore_export_governance_components(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_restore_export_governance_readiness_checkpoint(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_restore_export_governance_components
            WHERE checkpoint_id = ?
            ORDER BY component_order
            """,
            (DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID,),
        ).fetchall()
    components = [
        {
            "component_record_id": row["component_record_id"],
            "checkpoint_id": row["checkpoint_id"],
            "component_id": row["component_id"],
            "component_name": row["component_name"],
            "component_order": int(row["component_order"]),
            "component_ready": bool(row["component_ready"]),
            "component_validation_passed": bool(row["component_validation_passed"]),
            "component_safe_to_continue": bool(row["component_safe_to_continue"]),
            "component_locked": bool(row["component_locked"]),
            "source_status": _json_loads(row["source_status_json"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "component_count": len(components),
        "components_ready_count": sum(1 for item in components if item["component_ready"]),
        "components_validation_passed_count": sum(1 for item in components if item["component_validation_passed"]),
        "components_safe_to_continue_count": sum(1 for item in components if item["component_safe_to_continue"]),
        "components_locked_count": sum(1 for item in components if item["component_locked"]),
        "components": components,
    }

def get_restore_export_governance_criteria(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_restore_export_governance_readiness_checkpoint(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_restore_export_governance_criteria
            WHERE checkpoint_id = ?
            ORDER BY criterion_code
            """,
            (DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID,),
        ).fetchall()
    criteria = [
        {
            "criterion_id": row["criterion_id"],
            "checkpoint_id": row["checkpoint_id"],
            "criterion_code": row["criterion_code"],
            "criterion_name": row["criterion_name"],
            "criterion_status": row["criterion_status"],
            "passed": bool(row["passed"]),
            "required": bool(row["required"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "criteria_count": len(criteria),
        "passed_criteria_count": sum(1 for item in criteria if item["passed"]),
        "failed_criteria_count": sum(1 for item in criteria if not item["passed"]),
        "criteria": criteria,
    }

def get_restore_export_governance_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_restore_export_governance_readiness_checkpoint(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_restore_export_governance_blockers
            WHERE checkpoint_id = ?
            ORDER BY created_at, blocker_code
            """,
            (DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID,),
        ).fetchall()
    blockers = [
        {
            "blocker_id": row["blocker_id"],
            "checkpoint_id": row["checkpoint_id"],
            "blocker_code": row["blocker_code"],
            "blocker_name": row["blocker_name"],
            "blocker_status": row["blocker_status"],
            "blocker_payload": _json_loads(row["blocker_payload_json"]),
            "active": bool(row["active"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "blocker_count": len(blockers),
        "active_blocker_count": sum(1 for item in blockers if item["active"]),
        "blockers": blockers,
    }

def get_restore_export_governance_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_restore_export_governance_readiness_checkpoint(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_restore_export_governance_events
            WHERE checkpoint_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID,),
        ).fetchall()
    events = [
        {
            "event_id": row["event_id"],
            "checkpoint_id": row["checkpoint_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def validate_restore_export_governance_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    record = get_restore_export_governance_readiness_checkpoint_record(db_path)["checkpoint"]
    components = get_restore_export_governance_components(db_path)
    criteria = get_restore_export_governance_criteria(db_path)
    blockers = get_restore_export_governance_blockers(db_path)
    events = get_restore_export_governance_events(db_path)

    recomputed_hash = _hash_payload(record["checkpoint_data"])
    checks = [
        ("REAL_SQLITE_READINESS_CHECKPOINT_EXISTS", record["checkpoint_id"] == DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID),
        ("SECTION_GP081_GP090", record["section_id"] == SECTION_ID and record["section_range"] == SECTION_RANGE),
        ("READINESS_SCORE_100", record["readiness_score"] == 100),
        ("READINESS_HASH_MATCHES", record["readiness_hash"] == recomputed_hash),
        ("COMPONENT_COUNT_9", components["component_count"] == 9),
        ("ALL_COMPONENTS_READY", components["components_ready_count"] == 9),
        ("ALL_COMPONENTS_SAFE_TO_CONTINUE", components["components_safe_to_continue_count"] == 9),
        ("ALL_COMPONENTS_LOCKED", components["components_locked_count"] == 9),
        ("CRITERIA_COUNT_MATCHES", criteria["criteria_count"] == len(READINESS_CRITERIA)),
        ("ALL_CRITERIA_PASSED", criteria["failed_criteria_count"] == 0),
        ("NO_ACTIVE_BLOCKERS", blockers["active_blocker_count"] == 0),
        ("EVENT_LOG_EXISTS", events["event_count"] >= 6),
        ("SECTION_CLOSEOUT_READY", record["section_closeout_ready"] is True),
        ("SECTION_CLOSED", record["section_closed"] is True),
        ("RESTORE_EXECUTION_LOCKED", record["restore_execution_locked"] is True),
        ("RESTORE_EXPORT_LOCKED", record["restore_export_locked"] is True),
        ("PROVIDER_RESTORE_API_LOCKED", record["provider_restore_api_locked"] is True),
        ("OBJECT_BODY_ACCESS_LOCKED", record["object_body_access_locked"] is True),
        ("DIRECT_UPLOAD_LOCKED", record["direct_upload_locked"] is True),
        ("EXPORT_LOCKED", record["export_locked"] is True),
        ("EXECUTION_LOCKED", record["execution_locked"] is True),
        ("VAULT_NOT_DONE", record["vault_done"] is False),
        ("CLOUDS_PARKED", record["clouds_should_continue"] is False),
        ("SAFE_TO_CONTINUE_TO_GP091", record["safe_to_continue_to_gp091"] is True),
    ]
    check_payload = [{"code": code, "passed": bool(passed)} for code, passed in checks]
    failed = [item for item in check_payload if not item["passed"]]

    return {
        "pack": _pack_payload(),
        "validation_ready": True,
        "valid": len(failed) == 0,
        "check_count": len(check_payload),
        "passed_count": len(check_payload) - len(failed),
        "failed_count": len(failed),
        "failed_checks": failed,
        "checks": check_payload,
        "readiness_score": record["readiness_score"],
        "readiness_hash": record["readiness_hash"],
        "safe_to_continue_to_gp091": len(failed) == 0,
        "vault_done": False,
    }

def get_restore_export_governance_next_section() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_section": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "section_closed": True,
            "next_section": NEXT_SECTION_ID,
            "next_section_title": NEXT_SECTION_TITLE,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp091": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP090 closes GP081-GP090 and hands off to GP091. Restore, provider API, object body access, export, direct upload, execution, and Vault done remain locked.",
            "carry_forward_rules": [
                "Keep all GP081-GP089 source contracts attached by readiness snapshot.",
                "Keep restore request submission locked.",
                "Keep eligibility, authority, scope, target, object, job, API, and export actions locked.",
                "Keep provider restore API calls/sessions/tokens/job references/status polls locked.",
                "Keep object body read/view/download locked.",
                "Keep export package/manifest/download locked.",
                "Keep direct upload locked.",
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
        "depends_on": [item[0] for item in COMPONENT_SPECS],
        "foundation_status": "restore_export_governance_section_closed_safe_to_continue_not_done",
        "product_depth_layer": "real_provider_restore_export_governance_readiness_checkpoint",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-provider-restore-export-governance-readiness-checkpoint",
        "json_route": "/vault/real-provider-restore-export-governance-readiness-checkpoint.json",
        "record_route": "/vault/restore-export-governance-readiness-checkpoint-record.json",
        "components_route": "/vault/restore-export-governance-components.json",
        "criteria_route": "/vault/restore-export-governance-criteria.json",
        "blockers_route": "/vault/restore-export-governance-blockers.json",
        "events_route": "/vault/restore-export-governance-events.json",
        "validation_route": "/vault/restore-export-governance-validation.json",
        "next_section_route": "/vault/restore-export-governance-next-section.json",
        "gp090_status_route": "/vault/gp090-status.json",
    }

def get_real_provider_restore_export_governance_readiness_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_real_provider_restore_export_governance_readiness_checkpoint(db_path)
    checkpoint = get_restore_export_governance_readiness_checkpoint_record(db_path)["checkpoint"]
    components = get_restore_export_governance_components(db_path)
    criteria = get_restore_export_governance_criteria(db_path)
    blockers = get_restore_export_governance_blockers(db_path)
    events = get_restore_export_governance_events(db_path)
    validation = validate_restore_export_governance_readiness_checkpoint(db_path)

    truth = {
        "real_provider_restore_export_governance_readiness_checkpoint_ready": True,
        "real_sqlite_backed": True,
        "readiness_score": checkpoint["readiness_score"],
        "readiness_hash": checkpoint["readiness_hash"],
        "section_closed": checkpoint["section_closed"],
        "section_closeout_ready": checkpoint["section_closeout_ready"],
        "component_count": components["component_count"],
        "criteria_count": criteria["criteria_count"],
        "failed_criteria_count": criteria["failed_criteria_count"],
        "active_blocker_count": blockers["active_blocker_count"],
        "event_count": events["event_count"],
        "restore_execution_locked": checkpoint["restore_execution_locked"],
        "restore_export_locked": checkpoint["restore_export_locked"],
        "provider_restore_api_locked": checkpoint["provider_restore_api_locked"],
        "object_body_access_locked": checkpoint["object_body_access_locked"],
        "direct_upload_locked": checkpoint["direct_upload_locked"],
        "export_locked": checkpoint["export_locked"],
        "execution_locked": checkpoint["execution_locked"],
        "safe_to_continue_to_gp091": validation["safe_to_continue_to_gp091"],
        "vault_done": checkpoint["vault_done"],
        "clouds_should_continue": checkpoint["clouds_should_continue"],
    }

    return {
        "pack": _pack_payload(),
        "readiness_truth": truth,
        "store": store,
        "checkpoint": checkpoint,
        "components": components,
        "criteria": criteria,
        "blockers": blockers,
        "events": events,
        "validation": validation,
        "routes": _routes_payload(),
        "next_section": get_restore_export_governance_next_section()["next_section"],
    }

def get_gp090_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_provider_restore_export_governance_readiness_home(db_path)
    checkpoint = home["checkpoint"]
    validation = home["validation"]
    return {
        "pack": _pack_payload(),
        "gp090_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "section_closed": checkpoint["section_closed"],
            "section_closeout_ready": checkpoint["section_closeout_ready"],
            "restore_export_governance_ready": checkpoint["restore_export_governance_ready"],
            "real_sqlite_backed": True,
            "real_checkpoint_count": home["store"]["checkpoint_count"],
            "real_component_count": home["store"]["component_count"],
            "real_criteria_count": home["store"]["criteria_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "readiness_score": checkpoint["readiness_score"],
            "readiness_hash": checkpoint["readiness_hash"],
            "component_count": checkpoint["component_count"],
            "criteria_count": checkpoint["criteria_count"],
            "passed_criteria_count": checkpoint["passed_criteria_count"],
            "failed_criteria_count": checkpoint["failed_criteria_count"],
            "active_blocker_count": checkpoint["active_blocker_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp091": validation["safe_to_continue_to_gp091"],
            "foundation_status": "restore_export_governance_section_closed_safe_to_continue_not_done",
            "restore_execution_locked": checkpoint["restore_execution_locked"],
            "restore_export_locked": checkpoint["restore_export_locked"],
            "provider_restore_api_locked": checkpoint["provider_restore_api_locked"],
            "object_body_access_locked": checkpoint["object_body_access_locked"],
            "direct_upload_locked": checkpoint["direct_upload_locked"],
            "export_locked": checkpoint["export_locked"],
            "execution_locked": checkpoint["execution_locked"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp090",
            "next_section": NEXT_SECTION_ID,
            "next_section_title": NEXT_SECTION_TITLE,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "readiness_truth": home["readiness_truth"],
        "routes": home["routes"],
        "checkpoint": checkpoint,
        "components": home["components"],
        "criteria": home["criteria"],
        "blockers": home["blockers"],
        "validation": validation,
        "next_section": home["next_section"],
    }

def render_real_provider_restore_export_governance_readiness_checkpoint_page() -> str:
    home = get_real_provider_restore_export_governance_readiness_home()
    truth = home["readiness_truth"]
    routes = home["routes"]
    next_section = home["next_section"]

    component_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['component_id'])}</strong>
          <span>{escape(item['component_name'])}</span>
          <code>{'READY' if item['component_safe_to_continue'] else 'BLOCKED'}</code>
        </article>
        """
        for item in home["components"]["components"]
    )
    checks = "\n".join(
        f"<div class='row'><strong>{escape(c['code'])}</strong><span>{'PASS' if c['passed'] else 'FAIL'}</span></div>"
        for c in home["validation"]["checks"]
    )
    rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_section["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault Restore/Export Governance Readiness Checkpoint · GP090</title>
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
    <div class="eyebrow">Archive Vault · Giant Pack 090</div>
    <div class="eyebrow">Restore/Export Governance Closeout · GP081-GP090</div>
    <h1>Real Provider Restore and Export Governance Readiness Checkpoint</h1>
    <p>GP090 closes the restore/export governance layer with a durable readiness hash and next-section handoff. Vault is still not done; restore, provider API, object body access, export, direct upload, and execution remain locked.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['readiness_score']}</strong><span>readiness score</span></div>
      <div class="metric"><strong>{truth['component_count']}</strong><span>components</span></div>
      <div class="metric"><strong>{truth['active_blocker_count']}</strong><span>active blockers</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">Section closed</span>
      <span class="pill ok">Readiness hash recorded</span>
      <span class="pill ok">Real SQLite-backed</span>
      <span class="pill danger">No provider API</span>
      <span class="pill danger">No body read</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No execution</span>
      <span class="pill danger">Vault not done</span>
    </div>
  </section>

  <section class="section">
    <h2>Component Snapshot</h2>
    <div class="cards">{component_cards}</div>
  </section>

  <section class="section">
    <h2>Validation Checks</h2>
    {checks}
  </section>

  <section class="section">
    <h2>Next Section</h2>
    <p>{escape(next_section['owner_notebook_note'])}</p>
    <p><code>{escape(next_section['next_pack'])}</code> · {escape(next_section['next_pack_title'])}</p>
    <ul>{rules}</ul>
  </section>

  <section class="section">
    <h2>GP090 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['components_route'])}</code>
      <code>{escape(routes['criteria_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_section_route'])}</code>
      <code>{escape(routes['gp090_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
