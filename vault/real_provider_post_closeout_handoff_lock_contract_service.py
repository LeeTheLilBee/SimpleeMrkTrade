"""
VAULT GP091 — Real Provider Post-Closeout Handoff Lock Contract

Starts:
Archive Vault — Real Provider Post-Closeout Handoff Governance Layer / GP091-GP100

This pack creates a real SQLite-backed handoff lock contract sourced from
GP090. It carries the GP090 readiness hash into the new section while keeping
restore, provider API calls, object body access, export, direct upload,
execution, and Vault done locked.
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

from vault.real_provider_restore_and_export_governance_readiness_checkpoint_service import (
    DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID,
    get_gp090_status,
    get_restore_export_governance_next_section,
    get_restore_export_governance_readiness_checkpoint_record,
)

PACK_ID = "VAULT_GP091"
PACK_NAME = "Real Provider Post-Closeout Handoff Lock Contract"
SCHEMA_VERSION = "vault.real_provider_post_closeout_handoff_lock_contract.v1"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_LAYER"
PREVIOUS_SECTION_TITLE = "Archive Vault — Real Provider Restore and Export Governance Layer"
PREVIOUS_SECTION_RANGE = "GP081-GP090"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_GOVERNANCE_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Post-Closeout Handoff Governance Layer"
SECTION_RANGE = "GP091-GP100"

NEXT_PACK = "VAULT_GP092_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER"
NEXT_PACK_TITLE = "Real Provider Post-Closeout Handoff Receipt Ledger"

DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID = "VPPCHLC-GP091-001"
DEFAULT_DB_ENV = "VAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_DB"
DEFAULT_DB_PATH = "data/vault_post_closeout_handoff_lock_contract.sqlite"

HANDOFF_REQUIREMENT_SPECS = [
    ("source_gp090_closeout_hash_required", "Source GP090 closeout hash required", "source_hash"),
    ("source_gp090_readiness_score_required", "Source GP090 readiness score required", "source_readiness"),
    ("post_closeout_handoff_lock_record_required", "Post-closeout handoff lock record required", "handoff_record"),
    ("post_closeout_no_unlock_required", "Post-closeout no-unlock boundary required", "lock_boundary"),
    ("post_closeout_next_section_boundary_required", "Post-closeout next-section boundary required", "next_section"),
    ("tower_handoff_review_required", "Tower handoff review required", "tower_gate"),
]

HANDOFF_POLICIES = [
    ("no_restore_unlock_from_handoff", "No restore unlock from handoff", "restore_lock"),
    ("no_provider_restore_api_from_handoff", "No provider restore API from handoff", "provider_api_lock"),
    ("no_object_body_access_from_handoff", "No object body access from handoff", "object_body_lock"),
    ("no_export_from_handoff", "No export from handoff", "export_lock"),
    ("no_direct_upload_from_handoff", "No direct upload from handoff", "direct_upload_lock"),
    ("no_execution_from_handoff", "No execution from handoff", "execution_lock"),
    ("no_vault_done_from_handoff", "No Vault done from handoff", "vault_done_lock"),
    ("preserve_gp090_readiness_hash", "Preserve GP090 readiness hash", "hash_preservation"),
    ("preserve_gp081_gp090_closeout_boundary", "Preserve GP081-GP090 closeout boundary", "section_boundary"),
    ("require_gp092_receipt_ledger_next", "Require GP092 receipt ledger next", "next_pack"),
]

FALSE_FIELDS = [
    "handoff_unlock_configured",
    "handoff_unlock_attempted",
    "handoff_unlock_enabled",
    "handoff_approval_granted",
    "handoff_execution_enabled",
    "restore_request_created",
    "restore_request_submitted",
    "restore_request_finalized",
    "restore_eligibility_checked",
    "restore_eligibility_passed",
    "restore_eligibility_failed",
    "restore_authority_verified",
    "restore_actor_authority_granted",
    "restore_scope_selected",
    "restore_target_selected",
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
    "clouds_should_continue",
]

TRUE_CONTRACT_FIELDS = [
    "post_closeout_handoff_lock_contract_ready",
    "post_closeout_handoff_requirements_ready",
    "post_closeout_handoff_policies_ready",
    "post_closeout_handoff_blockers_ready",
    "post_closeout_handoff_validation_ready",
    "source_gp090_checkpoint_attached",
    "source_gp090_readiness_hash_attached",
    "source_gp090_section_closed",
    "post_closeout_handoff_locked",
    "post_closeout_template_only",
    "restore_locks_carried_forward",
    "export_locks_carried_forward",
    "provider_restore_api_locks_carried_forward",
    "object_body_access_locks_carried_forward",
    "direct_upload_locks_carried_forward",
    "execution_locks_carried_forward",
    "safe_to_continue_to_gp092",
]

TRUE_REQUIREMENT_FIELDS = [
    "requirement_required",
    "handoff_locked",
    "template_only",
    "tower_review_required",
]

TRUE_BLOCKER_FIELDS = [
    "blocker_active",
    "blocks_restore_unlock",
    "blocks_provider_restore_api",
    "blocks_object_body_access",
    "blocks_export",
    "blocks_direct_upload",
    "blocks_execution",
    "blocks_vault_done",
    "tower_review_required",
]

def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _resolve_db_path(db_path: Optional[str] = None) -> Path:
    return Path(db_path or os.environ.get(DEFAULT_DB_ENV) or DEFAULT_DB_PATH)

def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)

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

def _ensure_integer_columns(conn: sqlite3.Connection, table: str, columns: Dict[str, str]) -> None:
    existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    for column_name, column_sql in columns.items():
        if column_name not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_sql}")

def _boolify(row: sqlite3.Row, json_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    json_fields = json_fields or {}
    numeric_fields = {
        "source_gp090_readiness_score",
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
        ):
            payload[key] = int(row[key])
        elif isinstance(row[key], int):
            payload[key] = bool(row[key])
        else:
            payload[key] = row[key]
    return payload

def ensure_post_closeout_handoff_lock_contract_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_CONTRACT_FIELDS)
        false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_lock_contracts (
                handoff_lock_contract_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                previous_section_id TEXT NOT NULL,
                previous_section_title TEXT NOT NULL,
                previous_section_range TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_title TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp090_checkpoint_id TEXT NOT NULL,
                source_gp090_readiness_hash TEXT NOT NULL,
                source_gp090_readiness_score INTEGER NOT NULL,
                source_gp090_next_pack TEXT NOT NULL,
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
            "handoff_unlock_configured",
            "handoff_unlock_attempted",
            "handoff_unlock_enabled",
            "handoff_approval_granted",
            "restore_request_submitted",
            "restore_object_selected",
            "restore_job_created",
            "provider_restore_api_called",
            "provider_restore_session_created",
            "provider_restore_token_created",
            "object_body_read",
            "object_body_view_enabled",
            "object_body_download_enabled",
            "restore_export_package_created",
            "export_package_created",
            "direct_upload_enabled",
            "export_enabled",
            "execution_enabled",
            "tower_unlock_granted",
            "vault_done",
            "clouds_should_continue",
        ]
        req_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_REQUIREMENT_FIELDS)
        req_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in req_false)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_requirements (
                handoff_requirement_id TEXT PRIMARY KEY,
                handoff_lock_contract_id TEXT NOT NULL,
                requirement_code TEXT NOT NULL,
                requirement_name TEXT NOT NULL,
                requirement_category TEXT NOT NULL,
                requirement_message TEXT NOT NULL,
                requirement_status TEXT NOT NULL,
                {req_true_sql},
                {req_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(handoff_lock_contract_id)
                    REFERENCES vault_post_closeout_handoff_lock_contracts(handoff_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(handoff_lock_contract_id, requirement_code)
            )
            """
        )

        policy_false = [
            "policy_verified",
            "handoff_unlock_configured",
            "handoff_unlock_enabled",
            "handoff_approval_granted",
            "restore_request_submitted",
            "restore_object_selected",
            "restore_job_created",
            "provider_restore_api_called",
            "object_body_read",
            "restore_export_package_created",
            "export_package_created",
            "direct_upload_enabled",
            "export_enabled",
            "execution_enabled",
            "tower_unlock_granted",
            "vault_done",
            "clouds_should_continue",
        ]
        policy_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in policy_false)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_policies (
                handoff_policy_id TEXT PRIMARY KEY,
                handoff_lock_contract_id TEXT NOT NULL,
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
                FOREIGN KEY(handoff_lock_contract_id)
                    REFERENCES vault_post_closeout_handoff_lock_contracts(handoff_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(handoff_lock_contract_id, policy_code)
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
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_blockers (
                handoff_blocker_id TEXT PRIMARY KEY,
                handoff_lock_contract_id TEXT NOT NULL,
                blocker_code TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                {blocker_true_sql},
                {blocker_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(handoff_lock_contract_id)
                    REFERENCES vault_post_closeout_handoff_lock_contracts(handoff_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(handoff_lock_contract_id, blocker_code)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_events (
                event_id TEXT PRIMARY KEY,
                handoff_lock_contract_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(handoff_lock_contract_id)
                    REFERENCES vault_post_closeout_handoff_lock_contracts(handoff_lock_contract_id)
                    ON DELETE CASCADE
            )
            """
        )


        _ensure_integer_columns(
            conn,
            "vault_post_closeout_handoff_requirements",
            {"tower_review_granted": "INTEGER NOT NULL DEFAULT 0"},
        )
        _ensure_integer_columns(
            conn,
            "vault_post_closeout_handoff_policies",
            {"tower_review_granted": "INTEGER NOT NULL DEFAULT 0"},
        )

        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "real_sqlite_backed": True,
        "tables": [
            "vault_post_closeout_handoff_lock_contracts",
            "vault_post_closeout_handoff_requirements",
            "vault_post_closeout_handoff_policies",
            "vault_post_closeout_handoff_blockers",
            "vault_post_closeout_handoff_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, contract_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VPPCHLEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_post_closeout_handoff_events",
        {
            "event_id": event_id,
            "handoff_lock_contract_id": contract_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "contract_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_lock_contracts").fetchone()["c"]),
            "requirement_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_requirements").fetchone()["c"]),
            "policy_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_policies").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_events").fetchone()["c"]),
        }

def initialize_real_provider_post_closeout_handoff_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_post_closeout_handoff_lock_contract_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            """
            SELECT handoff_lock_contract_id
            FROM vault_post_closeout_handoff_lock_contracts
            WHERE handoff_lock_contract_id = ?
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID,),
        ).fetchone()

        if exists is None:
            source_status = get_gp090_status()["gp090_status"]
            source_checkpoint = get_restore_export_governance_readiness_checkpoint_record()["checkpoint"]
            source_next = get_restore_export_governance_next_section()["next_section"]
            now = _now_iso()

            contract_data = {
                "schema_version": SCHEMA_VERSION,
                "contract_type": "REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT",
                "source_pack": "VAULT_GP090",
                "source_checkpoint_id": source_checkpoint["checkpoint_id"],
                "source_readiness_hash": source_checkpoint["readiness_hash"],
                "source_readiness_score": source_checkpoint["readiness_score"],
                "source_section_closed": source_checkpoint["section_closed"],
                "source_safe_to_continue_to_gp091": source_checkpoint["safe_to_continue_to_gp091"],
                "source_next_pack": source_next["next_pack"],
                "previous_section_id": PREVIOUS_SECTION_ID,
                "previous_section_title": PREVIOUS_SECTION_TITLE,
                "previous_section_range": PREVIOUS_SECTION_RANGE,
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "handoff_locked": True,
                "template_only": True,
                "no_unlocks_created": True,
                "restore_locks_carried_forward": True,
                "export_locks_carried_forward": True,
                "provider_restore_api_locks_carried_forward": True,
                "object_body_access_locks_carried_forward": True,
                "direct_upload_locks_carried_forward": True,
                "execution_locks_carried_forward": True,
                "vault_done": False,
                "clouds_should_continue": False,
                "next_pack": NEXT_PACK,
                "next_pack_title": NEXT_PACK_TITLE,
                "safe_to_continue_to_gp092": True,
            }

            contract_payload = {
                "handoff_lock_contract_id": DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID,
                "pack_id": PACK_ID,
                "previous_section_id": PREVIOUS_SECTION_ID,
                "previous_section_title": PREVIOUS_SECTION_TITLE,
                "previous_section_range": PREVIOUS_SECTION_RANGE,
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp090_checkpoint_id": source_checkpoint["checkpoint_id"],
                "source_gp090_readiness_hash": source_checkpoint["readiness_hash"],
                "source_gp090_readiness_score": source_checkpoint["readiness_score"],
                "source_gp090_next_pack": source_next["next_pack"],
                "contract_status": "REAL_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_OPEN_TEMPLATE_ONLY_TOWER_LOCKED",
                "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED_FOR_POST_CLOSEOUT_HANDOFF",
                "contract_data_json": _json_dumps(contract_data),
                "created_at": now,
                "updated_at": now,
            }
            for field in TRUE_CONTRACT_FIELDS:
                contract_payload[field] = 1
            for field in FALSE_FIELDS:
                contract_payload[field] = 0
            _insert_dict(conn, "vault_post_closeout_handoff_lock_contracts", contract_payload)

            req_false_fields = [
                "requirement_verified",
                "handoff_unlock_configured",
                "handoff_unlock_attempted",
                "handoff_unlock_enabled",
                "handoff_approval_granted",
                "restore_request_submitted",
                "restore_object_selected",
                "restore_job_created",
                "provider_restore_api_called",
                "provider_restore_session_created",
                "provider_restore_token_created",
                "object_body_read",
                "object_body_view_enabled",
                "object_body_download_enabled",
                "restore_export_package_created",
                "export_package_created",
                "direct_upload_enabled",
                "export_enabled",
                "execution_enabled",
                "tower_unlock_granted",
                "vault_done",
                "clouds_should_continue",
            ]

            for code, name, category in HANDOFF_REQUIREMENT_SPECS:
                payload = {
                    "handoff_requirement_id": f"VPPCHLR-{code.upper().replace('_', '-')}",
                    "handoff_lock_contract_id": DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID,
                    "requirement_code": code,
                    "requirement_name": name,
                    "requirement_category": category,
                    "requirement_message": f"{name}; GP091 carries GP090 closeout forward without creating any unlock, restore, export, upload, body access, execution, or Vault-done state.",
                    "requirement_status": "REAL_POST_CLOSEOUT_HANDOFF_REQUIREMENT_RECORDED_TEMPLATE_ONLY_TOWER_LOCKED",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_REQUIREMENT_FIELDS:
                    payload[field] = 1
                for field in req_false_fields:
                    payload[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_requirements", payload)

            policy_false_fields = [
                "policy_verified",
                "handoff_unlock_configured",
                "handoff_unlock_enabled",
                "handoff_approval_granted",
                "restore_request_submitted",
                "restore_object_selected",
                "restore_job_created",
                "provider_restore_api_called",
                "object_body_read",
                "restore_export_package_created",
                "export_package_created",
                "direct_upload_enabled",
                "export_enabled",
                "execution_enabled",
                "tower_unlock_granted",
                "vault_done",
                "clouds_should_continue",
            ]

            for code, name, category in HANDOFF_POLICIES:
                payload = {
                    "handoff_policy_id": f"VPPCHLP-{code.upper().replace('_', '-')}",
                    "handoff_lock_contract_id": DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID,
                    "policy_code": code,
                    "policy_name": name,
                    "policy_category": category,
                    "policy_message": f"{name}; GP091 is a lock-only handoff and cannot unlock restore/export/provider/body/upload/execution surfaces.",
                    "policy_status": "REAL_POST_CLOSEOUT_HANDOFF_POLICY_RECORDED_TEMPLATE_ONLY_TOWER_LOCKED",
                    "policy_required": 1,
                    "tower_review_required": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in policy_false_fields:
                    payload[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_policies", payload)

            blocker_specs = [
                ("block_restore_unlock", "Blocks restore unlock from post-closeout handoff", "restore", "critical"),
                ("block_provider_restore_api", "Blocks provider restore API from post-closeout handoff", "provider_api", "critical"),
                ("block_object_body_access", "Blocks object body access from post-closeout handoff", "object_body", "critical"),
                ("block_export", "Blocks export from post-closeout handoff", "export", "critical"),
                ("block_direct_upload", "Blocks direct upload from post-closeout handoff", "direct_upload", "critical"),
                ("block_execution", "Blocks execution from post-closeout handoff", "execution", "critical"),
                ("block_vault_done", "Blocks Vault done from post-closeout handoff", "vault_done", "critical"),
            ]
            for code, name, category, severity in blocker_specs:
                payload = {
                    "handoff_blocker_id": f"VPPCHLB-{code.upper().replace('_', '-')}",
                    "handoff_lock_contract_id": DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "REAL_POST_CLOSEOUT_HANDOFF_BLOCKER_ACTIVE",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_BLOCKER_FIELDS:
                    payload[field] = 1
                for field in ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]:
                    payload[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_blockers", payload)

            for event_type, event_payload in [
                ("REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_CREATED", contract_data),
                ("SOURCE_GP090_READINESS_CHECKPOINT_ATTACHED", {
                    "checkpoint_id": source_checkpoint["checkpoint_id"],
                    "readiness_hash": source_checkpoint["readiness_hash"],
                    "readiness_score": source_checkpoint["readiness_score"],
                    "section_closed": source_checkpoint["section_closed"],
                }),
                ("GP091_NEW_SECTION_OPENED_LOCK_ONLY", {
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    "previous_section_id": PREVIOUS_SECTION_ID,
                    "previous_section_range": PREVIOUS_SECTION_RANGE,
                }),
                ("POST_CLOSEOUT_HANDOFF_REQUIREMENTS_CREATED", {"requirement_count": len(HANDOFF_REQUIREMENT_SPECS)}),
                ("POST_CLOSEOUT_HANDOFF_POLICIES_CREATED", {"policy_count": len(HANDOFF_POLICIES)}),
                ("POST_CLOSEOUT_HANDOFF_LOCKS_CONFIRMED", {
                    "restore_request_submitted": False,
                    "provider_restore_api_called": False,
                    "object_body_read": False,
                    "export_package_created": False,
                    "direct_upload_enabled": False,
                    "execution_enabled": False,
                    "vault_done": False,
                }),
            ]:
                _insert_event(conn, DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _sum_counts(table: str, contract_id: str, fields: list[str], db_path: Optional[str] = None) -> Dict[str, int]:
    selects = ["COUNT(*) AS total_count"]
    for field in fields:
        selects.append(f"SUM(CASE WHEN {field} = 1 THEN 1 ELSE 0 END) AS {field}_count")
    with _connect(db_path) as conn:
        row = conn.execute(
            f"SELECT {', '.join(selects)} FROM {table} WHERE handoff_lock_contract_id = ?",
            (contract_id,),
        ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}

def get_post_closeout_handoff_lock_contract_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_lock_contract(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_lock_contracts
            WHERE handoff_lock_contract_id = ?
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID,),
        ).fetchone()
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "handoff_lock_contract": _boolify(row, {"contract_data_json": "contract_data"}),
    }

def get_post_closeout_handoff_requirements(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_lock_contract(db_path)
    fields = [
        "requirement_required",
        "requirement_verified",
        "handoff_locked",
        "template_only",
        "tower_review_required",
        "tower_review_granted",
        "handoff_unlock_configured",
        "handoff_unlock_attempted",
        "handoff_unlock_enabled",
        "handoff_approval_granted",
        "restore_request_submitted",
        "restore_object_selected",
        "restore_job_created",
        "provider_restore_api_called",
        "provider_restore_session_created",
        "provider_restore_token_created",
        "object_body_read",
        "object_body_view_enabled",
        "object_body_download_enabled",
        "restore_export_package_created",
        "export_package_created",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
        "vault_done",
        "clouds_should_continue",
    ]
    counts = _sum_counts("vault_post_closeout_handoff_requirements", DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_requirements
            WHERE handoff_lock_contract_id = ?
            ORDER BY requirement_category, requirement_code
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID,),
        ).fetchall()
    counts["requirement_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "requirements": [_boolify(row) for row in rows]}

def get_post_closeout_handoff_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_lock_contract(db_path)
    fields = [
        "policy_required",
        "policy_verified",
        "tower_review_required",
        "tower_review_granted",
        "handoff_unlock_configured",
        "handoff_unlock_enabled",
        "handoff_approval_granted",
        "restore_request_submitted",
        "restore_object_selected",
        "restore_job_created",
        "provider_restore_api_called",
        "object_body_read",
        "restore_export_package_created",
        "export_package_created",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
        "vault_done",
        "clouds_should_continue",
    ]
    counts = _sum_counts("vault_post_closeout_handoff_policies", DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_policies
            WHERE handoff_lock_contract_id = ?
            ORDER BY policy_category, policy_code
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID,),
        ).fetchall()
    counts["policy_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "policies": [_boolify(row) for row in rows]}

def get_post_closeout_handoff_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_lock_contract(db_path)
    fields = TRUE_BLOCKER_FIELDS + ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]
    counts = _sum_counts("vault_post_closeout_handoff_blockers", DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_blockers
            WHERE handoff_lock_contract_id = ?
            ORDER BY blocker_category, blocker_code
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID,),
        ).fetchall()
    counts["blocker_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "blockers": [_boolify(row) for row in rows]}

def get_post_closeout_handoff_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_lock_contract(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_events
            WHERE handoff_lock_contract_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID,),
        ).fetchall()
    events = [
        {
            "event_id": row["event_id"],
            "handoff_lock_contract_id": row["handoff_lock_contract_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def record_post_closeout_handoff_event(event_type: str, event_payload: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_lock_contract(db_path)
    payload = dict(event_payload or {})
    payload.update({
        "write_type": "REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_LOCK_EVENT",
        "post_closeout_handoff_locked": True,
        "source_gp090_checkpoint_attached": True,
        "handoff_unlock_enabled": False,
        "restore_request_submitted": False,
        "provider_restore_api_called": False,
        "object_body_read": False,
        "export_package_created": False,
        "direct_upload_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
        "clouds_should_continue": False,
    })
    with _connect(db_path) as conn:
        event_id = _insert_event(conn, DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID, event_type, payload)
        conn.commit()
    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "handoff_lock_contract_id": DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID,
        "real_sqlite_backed": True,
        **payload,
    }

def validate_post_closeout_handoff_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    contract = get_post_closeout_handoff_lock_contract_record(db_path)["handoff_lock_contract"]
    requirements = get_post_closeout_handoff_requirements(db_path)
    policies = get_post_closeout_handoff_policies(db_path)
    blockers = get_post_closeout_handoff_blockers(db_path)
    events = get_post_closeout_handoff_events(db_path)

    false_checks = [(f"NO_CONTRACT_{field.upper()}", contract[field] is False) for field in FALSE_FIELDS]

    checks = [
        ("REAL_SQLITE_POST_CLOSEOUT_HANDOFF_CONTRACT_EXISTS", contract["handoff_lock_contract_id"] == DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID),
        ("SOURCE_GP090_CHECKPOINT_ATTACHED", contract["source_gp090_checkpoint_id"] == DEFAULT_RESTORE_EXPORT_GOVERNANCE_READINESS_CHECKPOINT_ID),
        ("SOURCE_GP090_READINESS_SCORE_100", contract["source_gp090_readiness_score"] == 100),
        ("SOURCE_GP090_HASH_ATTACHED", isinstance(contract["source_gp090_readiness_hash"], str) and len(contract["source_gp090_readiness_hash"]) == 64),
        ("NEW_SECTION_GP091_GP100", contract["section_id"] == SECTION_ID and contract["section_range"] == SECTION_RANGE),
        ("PREVIOUS_SECTION_GP081_GP090", contract["previous_section_id"] == PREVIOUS_SECTION_ID and contract["previous_section_range"] == PREVIOUS_SECTION_RANGE),
        ("HANDOFF_CONTRACT_READY", contract["post_closeout_handoff_lock_contract_ready"] is True),
        ("HANDOFF_REQUIREMENTS_READY", contract["post_closeout_handoff_requirements_ready"] is True),
        ("HANDOFF_POLICIES_READY", contract["post_closeout_handoff_policies_ready"] is True),
        ("HANDOFF_BLOCKERS_READY", contract["post_closeout_handoff_blockers_ready"] is True),
        ("HANDOFF_VALIDATION_READY", contract["post_closeout_handoff_validation_ready"] is True),
        ("HANDOFF_LOCKED", contract["post_closeout_handoff_locked"] is True),
        ("HANDOFF_TEMPLATE_ONLY", contract["post_closeout_template_only"] is True),
        ("RESTORE_LOCKS_CARRIED_FORWARD", contract["restore_locks_carried_forward"] is True),
        ("EXPORT_LOCKS_CARRIED_FORWARD", contract["export_locks_carried_forward"] is True),
        ("PROVIDER_API_LOCKS_CARRIED_FORWARD", contract["provider_restore_api_locks_carried_forward"] is True),
        ("OBJECT_BODY_LOCKS_CARRIED_FORWARD", contract["object_body_access_locks_carried_forward"] is True),
        ("DIRECT_UPLOAD_LOCKS_CARRIED_FORWARD", contract["direct_upload_locks_carried_forward"] is True),
        ("EXECUTION_LOCKS_CARRIED_FORWARD", contract["execution_locks_carried_forward"] is True),
        ("REQUIREMENTS_EXIST", requirements["requirement_count"] == len(HANDOFF_REQUIREMENT_SPECS)),
        ("ALL_REQUIREMENTS_REQUIRED", requirements["requirement_required_count"] == len(HANDOFF_REQUIREMENT_SPECS)),
        ("ALL_REQUIREMENTS_LOCKED", requirements["handoff_locked_count"] == len(HANDOFF_REQUIREMENT_SPECS)),
        ("NO_REQUIREMENT_HANDOFF_UNLOCK", requirements["handoff_unlock_enabled_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_API", requirements["provider_restore_api_called_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY", requirements["object_body_read_count"] == 0),
        ("NO_REQUIREMENT_EXPORT", requirements["export_enabled_count"] == 0),
        ("NO_REQUIREMENT_EXECUTION", requirements["execution_enabled_count"] == 0),
        ("POLICIES_EXIST", policies["policy_count"] == len(HANDOFF_POLICIES)),
        ("NO_POLICY_HANDOFF_UNLOCK", policies["handoff_unlock_enabled_count"] == 0),
        ("NO_POLICY_PROVIDER_API", policies["provider_restore_api_called_count"] == 0),
        ("NO_POLICY_OBJECT_BODY", policies["object_body_read_count"] == 0),
        ("NO_POLICY_EXPORT", policies["export_enabled_count"] == 0),
        ("NO_POLICY_EXECUTION", policies["execution_enabled_count"] == 0),
        ("BLOCKERS_EXIST", blockers["blocker_count"] == 7),
        ("ALL_BLOCKERS_ACTIVE", blockers["blocker_active_count"] == 7),
        ("ALL_BLOCKERS_BLOCK_RESTORE", blockers["blocks_restore_unlock_count"] == 7),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", blockers["blocks_provider_restore_api_count"] == 7),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY", blockers["blocks_object_body_access_count"] == 7),
        ("ALL_BLOCKERS_BLOCK_EXPORT", blockers["blocks_export_count"] == 7),
        ("ALL_BLOCKERS_BLOCK_DIRECT_UPLOAD", blockers["blocks_direct_upload_count"] == 7),
        ("ALL_BLOCKERS_BLOCK_EXECUTION", blockers["blocks_execution_count"] == 7),
        ("ALL_BLOCKERS_BLOCK_VAULT_DONE", blockers["blocks_vault_done_count"] == 7),
        ("NO_BLOCKERS_RESOLVED", blockers["resolved_count"] == 0),
        ("EVENT_LOG_EXISTS", events["event_count"] >= 6),
        ("SAFE_TO_CONTINUE_TO_GP092", contract["safe_to_continue_to_gp092"] is True),
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
        "safe_to_continue_to_gp092": len(failed) == 0,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_post_closeout_handoff_next_step() -> Dict[str, Any]:
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
            "safe_to_continue_to_gp092": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP091 opens GP091-GP100 with a lock-only post-closeout handoff. Continue to GP092 receipt ledger while restore, provider API, object body access, export, direct upload, execution, and Vault done remain locked.",
            "carry_forward_rules": [
                "Carry GP090 readiness hash forward.",
                "Keep GP081-GP090 section closed.",
                "Keep restore request submission locked.",
                "Keep restore job/API/export surfaces locked.",
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
        "depends_on": ["VAULT_GP090"],
        "foundation_status": "post_closeout_handoff_lock_contract_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_provider_post_closeout_handoff_lock_contract",
        "previous_section": PREVIOUS_SECTION_ID,
        "previous_section_title": PREVIOUS_SECTION_TITLE,
        "previous_section_range": PREVIOUS_SECTION_RANGE,
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-provider-post-closeout-handoff-lock-contract",
        "json_route": "/vault/real-provider-post-closeout-handoff-lock-contract.json",
        "record_route": "/vault/post-closeout-handoff-lock-contract-record.json",
        "requirements_route": "/vault/post-closeout-handoff-requirements.json",
        "policies_route": "/vault/post-closeout-handoff-policies.json",
        "blockers_route": "/vault/post-closeout-handoff-blockers.json",
        "events_route": "/vault/post-closeout-handoff-events.json",
        "validation_route": "/vault/post-closeout-handoff-validation.json",
        "next_step_route": "/vault/post-closeout-handoff-next-step.json",
        "gp091_status_route": "/vault/gp091-status.json",
    }

def get_real_provider_post_closeout_handoff_lock_contract_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_real_provider_post_closeout_handoff_lock_contract(db_path)
    contract = get_post_closeout_handoff_lock_contract_record(db_path)["handoff_lock_contract"]
    requirements = get_post_closeout_handoff_requirements(db_path)
    policies = get_post_closeout_handoff_policies(db_path)
    blockers = get_post_closeout_handoff_blockers(db_path)
    events = get_post_closeout_handoff_events(db_path)
    validation = validate_post_closeout_handoff_lock_contract(db_path)

    truth = {
        "real_provider_post_closeout_handoff_lock_contract_ready": True,
        "real_sqlite_backed": True,
        "source_gp090_checkpoint_attached": contract["source_gp090_checkpoint_attached"],
        "source_gp090_readiness_hash": contract["source_gp090_readiness_hash"],
        "source_gp090_readiness_score": contract["source_gp090_readiness_score"],
        "source_gp090_section_closed": contract["source_gp090_section_closed"],
        "post_closeout_handoff_locked": contract["post_closeout_handoff_locked"],
        "post_closeout_template_only": contract["post_closeout_template_only"],
        "requirement_count": requirements["requirement_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "event_count": events["event_count"],
        "handoff_unlock_enabled": contract["handoff_unlock_enabled"],
        "restore_request_submitted": contract["restore_request_submitted"],
        "provider_restore_api_called": contract["provider_restore_api_called"],
        "object_body_read": contract["object_body_read"],
        "export_package_created": contract["export_package_created"],
        "direct_upload_enabled": contract["direct_upload_enabled"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "safe_to_continue_to_gp092": validation["safe_to_continue_to_gp092"],
        "vault_done": contract["vault_done"],
        "clouds_should_continue": contract["clouds_should_continue"],
    }

    return {
        "pack": _pack_payload(),
        "handoff_truth": truth,
        "store": store,
        "handoff_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "events": events,
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_post_closeout_handoff_next_step()["next_step"],
    }

def get_gp091_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_provider_post_closeout_handoff_lock_contract_home(db_path)
    contract = home["handoff_lock_contract"]
    requirements = home["requirements"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp091_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "previous_section_id": PREVIOUS_SECTION_ID,
            "previous_section_title": PREVIOUS_SECTION_TITLE,
            "previous_section_range": PREVIOUS_SECTION_RANGE,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_provider_post_closeout_handoff_lock_contract_ready": True,
            "real_sqlite_backed": True,
            "real_contract_count": home["store"]["contract_count"],
            "real_requirement_count": home["store"]["requirement_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp090_checkpoint_attached": contract["source_gp090_checkpoint_attached"],
            "source_gp090_checkpoint_id": contract["source_gp090_checkpoint_id"],
            "source_gp090_readiness_hash": contract["source_gp090_readiness_hash"],
            "source_gp090_readiness_score": contract["source_gp090_readiness_score"],
            "source_gp090_section_closed": contract["source_gp090_section_closed"],
            "post_closeout_handoff_lock_contract_ready": contract["post_closeout_handoff_lock_contract_ready"],
            "post_closeout_handoff_requirements_ready": contract["post_closeout_handoff_requirements_ready"],
            "post_closeout_handoff_policies_ready": contract["post_closeout_handoff_policies_ready"],
            "post_closeout_handoff_blockers_ready": contract["post_closeout_handoff_blockers_ready"],
            "post_closeout_handoff_validation_ready": contract["post_closeout_handoff_validation_ready"],
            "post_closeout_handoff_locked": contract["post_closeout_handoff_locked"],
            "post_closeout_template_only": contract["post_closeout_template_only"],
            "restore_locks_carried_forward": contract["restore_locks_carried_forward"],
            "export_locks_carried_forward": contract["export_locks_carried_forward"],
            "provider_restore_api_locks_carried_forward": contract["provider_restore_api_locks_carried_forward"],
            "object_body_access_locks_carried_forward": contract["object_body_access_locks_carried_forward"],
            "direct_upload_locks_carried_forward": contract["direct_upload_locks_carried_forward"],
            "execution_locks_carried_forward": contract["execution_locks_carried_forward"],
            "requirement_count": requirements["requirement_count"],
            "policy_count": policies["policy_count"],
            "blocker_count": blockers["blocker_count"],
            "handoff_unlock_enabled_count": requirements["handoff_unlock_enabled_count"] + policies["handoff_unlock_enabled_count"],
            "provider_restore_api_called_count": requirements["provider_restore_api_called_count"] + policies["provider_restore_api_called_count"],
            "object_body_read_count": requirements["object_body_read_count"] + policies["object_body_read_count"],
            "export_enabled_count": requirements["export_enabled_count"] + policies["export_enabled_count"],
            "direct_upload_enabled_count": requirements["direct_upload_enabled_count"] + policies["direct_upload_enabled_count"],
            "execution_enabled_count": requirements["execution_enabled_count"] + policies["execution_enabled_count"],
            "vault_done_count": requirements["vault_done_count"] + policies["vault_done_count"],
            "blocks_restore_unlock_count": blockers["blocks_restore_unlock_count"],
            "blocks_provider_restore_api_count": blockers["blocks_provider_restore_api_count"],
            "blocks_object_body_access_count": blockers["blocks_object_body_access_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_direct_upload_count": blockers["blocks_direct_upload_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "blocks_vault_done_count": blockers["blocks_vault_done_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp092": validation["safe_to_continue_to_gp092"],
            "foundation_status": "post_closeout_handoff_lock_contract_ready_safe_to_continue_not_done",
            "handoff_unlock_enabled": contract["handoff_unlock_enabled"],
            "provider_restore_api_called": contract["provider_restore_api_called"],
            "object_body_read": contract["object_body_read"],
            "export_package_created": contract["export_package_created"],
            "direct_upload_enabled": contract["direct_upload_enabled"],
            "export_enabled": contract["export_enabled"],
            "execution_enabled": contract["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp091",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "handoff_truth": home["handoff_truth"],
        "routes": home["routes"],
        "handoff_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }

def render_real_provider_post_closeout_handoff_lock_contract_page() -> str:
    home = get_real_provider_post_closeout_handoff_lock_contract_home()
    truth = home["handoff_truth"]
    routes = home["routes"]
    next_step = home["next_step"]

    requirement_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['requirement_code'])}</strong>
          <span>{escape(item['requirement_name'])}</span>
          <code>{escape(item['requirement_category'])}</code>
        </article>
        """
        for item in home["requirements"]["requirements"]
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
<title>Vault Post-Closeout Handoff Lock Contract · GP091</title>
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
    <div class="eyebrow">Archive Vault · Giant Pack 091</div>
    <div class="eyebrow">Post-Closeout Handoff Governance Layer · GP091-GP100</div>
    <h1>Real Provider Post-Closeout Handoff Lock Contract</h1>
    <p>GP091 opens the new section by carrying the GP090 readiness hash forward without unlocking restore, provider APIs, object body access, exports, direct upload, execution, or Vault done.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['source_gp090_readiness_score']}</strong><span>source readiness</span></div>
      <div class="metric"><strong>{truth['requirement_count']}</strong><span>requirements</span></div>
      <div class="metric"><strong>{truth['blocker_count']}</strong><span>active lock blockers</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP090 hash attached</span>
      <span class="pill ok">New section opened</span>
      <span class="pill ok">Handoff locked</span>
      <span class="pill danger">No provider API</span>
      <span class="pill danger">No body read</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Handoff Requirements</h2>
    <div class="cards">{requirement_cards}</div>
  </section>

  <section class="section">
    <h2>Validation Checks</h2>
    {checks}
  </section>

  <section class="section">
    <h2>Next Step</h2>
    <p>{escape(next_step['owner_notebook_note'])}</p>
    <p><code>{escape(next_step['next_pack'])}</code> · {escape(next_step['next_pack_title'])}</p>
    <ul>{rules}</ul>
  </section>

  <section class="section">
    <h2>GP091 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['requirements_route'])}</code>
      <code>{escape(routes['policies_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_step_route'])}</code>
      <code>{escape(routes['gp091_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
