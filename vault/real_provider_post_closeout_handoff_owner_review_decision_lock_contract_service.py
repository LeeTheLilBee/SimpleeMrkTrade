"""
VAULT GP094 — Real Provider Post-Closeout Handoff Owner Review Decision Lock Contract

Current section:
Archive Vault — Real Provider Post-Closeout Handoff Governance Layer / GP091-GP100

This pack creates a real SQLite-backed owner review decision lock contract
sourced from GP093. It defines decision requirements, policies, blockers,
events, and validation while preventing any actual owner decision, owner
approval/rejection, Tower unlock, restore action, provider API call, object body
read, export, direct upload, execution, or Vault-done state.
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

from vault.real_provider_post_closeout_handoff_owner_review_queue_service import (
    DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID,
    get_gp093_status,
    get_post_closeout_handoff_owner_review_blockers,
    get_post_closeout_handoff_owner_review_events,
    get_post_closeout_handoff_owner_review_items,
    get_post_closeout_handoff_owner_review_policies,
    get_post_closeout_handoff_owner_review_queue_record,
)

PACK_ID = "VAULT_GP094"
PACK_NAME = "Real Provider Post-Closeout Handoff Owner Review Decision Lock Contract"
SCHEMA_VERSION = "vault.real_provider_post_closeout_handoff_owner_review_decision_lock_contract.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_GOVERNANCE_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Post-Closeout Handoff Governance Layer"
SECTION_RANGE = "GP091-GP100"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_LAYER"
PREVIOUS_SECTION_RANGE = "GP081-GP090"

NEXT_PACK = "VAULT_GP095_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT"
NEXT_PACK_TITLE = "Real Provider Post-Closeout Handoff Owner Review Decision Receipt Lock Contract"

DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID = "VPPCHORDLC-GP094-001"
DEFAULT_DB_ENV = "VAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_DB"
DEFAULT_DB_PATH = "data/vault_post_closeout_handoff_owner_review_decision_lock_contract.sqlite"

DECISION_REQUIREMENT_SPECS = [
    ("source_gp093_owner_review_queue_required", "Source GP093 owner review queue required", "source_queue"),
    ("source_gp092_receipt_ledger_required", "Source GP092 receipt ledger required", "source_ledger"),
    ("source_gp090_readiness_hash_required", "Source GP090 readiness hash required", "source_hash"),
    ("decision_lock_record_required", "Decision lock record required", "decision_lock"),
    ("owner_decision_template_only_required", "Owner decision template-only boundary required", "decision_boundary"),
    ("tower_decision_unlock_required", "Tower decision unlock required before any future decision", "tower_gate"),
]

DECISION_POLICIES = [
    ("decision_lock_no_owner_decision", "Decision lock cannot record owner decision", "decision_lock"),
    ("decision_lock_no_owner_approval", "Decision lock cannot record owner approval", "approval_lock"),
    ("decision_lock_no_owner_rejection", "Decision lock cannot record owner rejection", "rejection_lock"),
    ("decision_lock_no_tower_unlock", "Decision lock cannot grant Tower unlock", "tower_lock"),
    ("decision_lock_no_restore_submit", "Decision lock cannot submit restore", "restore_lock"),
    ("decision_lock_no_provider_api", "Decision lock cannot call provider API", "provider_api_lock"),
    ("decision_lock_no_object_body", "Decision lock cannot read object bodies", "object_body_lock"),
    ("decision_lock_no_export", "Decision lock cannot export", "export_lock"),
    ("decision_lock_no_direct_upload", "Decision lock cannot direct upload", "direct_upload_lock"),
    ("decision_lock_no_execution", "Decision lock cannot execute or mark Vault done", "execution_lock"),
]

FALSE_FIELDS = [
    "owner_review_decision_configured",
    "owner_review_decision_prepared",
    "owner_review_decision_recorded",
    "owner_review_approval_recorded",
    "owner_review_rejection_recorded",
    "owner_review_escalation_recorded",
    "owner_review_closed",
    "decision_receipt_created",
    "handoff_unlock_configured",
    "handoff_unlock_attempted",
    "handoff_unlock_enabled",
    "receipt_unlock_configured",
    "receipt_unlock_attempted",
    "receipt_unlock_enabled",
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
    "owner_review_decision_lock_contract_ready",
    "source_gp093_owner_review_queue_attached",
    "source_gp092_receipt_ledger_attached",
    "source_gp091_handoff_contract_attached",
    "source_gp090_readiness_hash_attached",
    "decision_requirements_ready",
    "decision_policies_ready",
    "decision_blockers_ready",
    "decision_events_ready",
    "decision_validation_ready",
    "owner_review_decision_locked",
    "owner_review_decision_template_only",
    "owner_review_required",
    "tower_review_required",
    "restore_locks_carried_forward",
    "export_locks_carried_forward",
    "provider_restore_api_locks_carried_forward",
    "object_body_access_locks_carried_forward",
    "direct_upload_locks_carried_forward",
    "execution_locks_carried_forward",
    "safe_to_continue_to_gp095",
]

TRUE_REQUIREMENT_FIELDS = [
    "requirement_required",
    "decision_locked",
    "template_only",
    "owner_review_required",
    "tower_review_required",
]

TRUE_BLOCKER_FIELDS = [
    "blocker_active",
    "blocks_owner_decision",
    "blocks_owner_approval",
    "blocks_owner_rejection",
    "blocks_decision_receipt",
    "blocks_tower_unlock",
    "blocks_restore_unlock",
    "blocks_provider_restore_api",
    "blocks_object_body_access",
    "blocks_export",
    "blocks_direct_upload",
    "blocks_execution",
    "blocks_vault_done",
    "owner_review_required",
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

def _boolify(row: sqlite3.Row, json_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    json_fields = json_fields or {}
    numeric_fields = {
        "source_gp090_readiness_score",
        "source_review_item_count",
        "requirement_count",
        "policy_count",
        "blocker_count",
        "event_count",
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
            or key.endswith("_position")
        ):
            payload[key] = int(row[key])
        elif isinstance(row[key], int):
            payload[key] = bool(row[key])
        else:
            payload[key] = row[key]
    return payload

def ensure_post_closeout_handoff_owner_review_decision_lock_contract_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_CONTRACT_FIELDS)
        false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_owner_review_decision_lock_contracts (
                decision_lock_contract_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_title TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_owner_review_queue_id TEXT NOT NULL,
                source_receipt_ledger_id TEXT NOT NULL,
                source_ledger_hash TEXT NOT NULL,
                source_gp090_readiness_hash TEXT NOT NULL,
                source_gp090_readiness_score INTEGER NOT NULL,
                source_review_item_count INTEGER NOT NULL,
                requirement_count INTEGER NOT NULL,
                policy_count INTEGER NOT NULL,
                blocker_count INTEGER NOT NULL,
                event_count INTEGER NOT NULL,
                contract_status TEXT NOT NULL,
                contract_data_json TEXT NOT NULL,
                {true_sql},
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        req_false_fields = [
            "requirement_verified",
            "owner_review_decision_recorded",
            "owner_review_approval_recorded",
            "owner_review_rejection_recorded",
            "decision_receipt_created",
            "tower_unlock_granted",
            "restore_request_submitted",
            "restore_object_selected",
            "restore_job_created",
            "provider_restore_api_called",
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
        req_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_REQUIREMENT_FIELDS)
        req_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in req_false_fields)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_owner_review_decision_requirements (
                decision_requirement_id TEXT PRIMARY KEY,
                decision_lock_contract_id TEXT NOT NULL,
                requirement_code TEXT NOT NULL,
                requirement_name TEXT NOT NULL,
                requirement_category TEXT NOT NULL,
                requirement_message TEXT NOT NULL,
                requirement_status TEXT NOT NULL,
                {req_true_sql},
                {req_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(decision_lock_contract_id)
                    REFERENCES vault_post_closeout_handoff_owner_review_decision_lock_contracts(decision_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(decision_lock_contract_id, requirement_code)
            )
            """
        )

        policy_false_fields = [
            "policy_verified",
            "owner_review_decision_recorded",
            "owner_review_approval_recorded",
            "owner_review_rejection_recorded",
            "decision_receipt_created",
            "tower_unlock_granted",
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
        policy_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in policy_false_fields)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_owner_review_decision_policies (
                decision_policy_id TEXT PRIMARY KEY,
                decision_lock_contract_id TEXT NOT NULL,
                policy_code TEXT NOT NULL,
                policy_name TEXT NOT NULL,
                policy_category TEXT NOT NULL,
                policy_message TEXT NOT NULL,
                policy_status TEXT NOT NULL,
                policy_required INTEGER NOT NULL DEFAULT 1,
                owner_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                {policy_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(decision_lock_contract_id)
                    REFERENCES vault_post_closeout_handoff_owner_review_decision_lock_contracts(decision_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(decision_lock_contract_id, policy_code)
            )
            """
        )

        blocker_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_BLOCKER_FIELDS)
        blocker_false_sql = ",\n".join(
            f"{field} INTEGER NOT NULL DEFAULT 0"
            for field in ["owner_review_completed", "tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_owner_review_decision_blockers (
                decision_blocker_id TEXT PRIMARY KEY,
                decision_lock_contract_id TEXT NOT NULL,
                blocker_code TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                {blocker_true_sql},
                {blocker_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(decision_lock_contract_id)
                    REFERENCES vault_post_closeout_handoff_owner_review_decision_lock_contracts(decision_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(decision_lock_contract_id, blocker_code)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_owner_review_decision_events (
                event_id TEXT PRIMARY KEY,
                decision_lock_contract_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(decision_lock_contract_id)
                    REFERENCES vault_post_closeout_handoff_owner_review_decision_lock_contracts(decision_lock_contract_id)
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
            "vault_post_closeout_handoff_owner_review_decision_lock_contracts",
            "vault_post_closeout_handoff_owner_review_decision_requirements",
            "vault_post_closeout_handoff_owner_review_decision_policies",
            "vault_post_closeout_handoff_owner_review_decision_blockers",
            "vault_post_closeout_handoff_owner_review_decision_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, contract_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VPPCHORDLCEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_post_closeout_handoff_owner_review_decision_events",
        {
            "event_id": event_id,
            "decision_lock_contract_id": contract_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "contract_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_owner_review_decision_lock_contracts").fetchone()["c"]),
            "requirement_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_owner_review_decision_requirements").fetchone()["c"]),
            "policy_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_owner_review_decision_policies").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_owner_review_decision_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_owner_review_decision_events").fetchone()["c"]),
        }

def initialize_real_provider_post_closeout_handoff_owner_review_decision_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_post_closeout_handoff_owner_review_decision_lock_contract_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            """
            SELECT decision_lock_contract_id
            FROM vault_post_closeout_handoff_owner_review_decision_lock_contracts
            WHERE decision_lock_contract_id = ?
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,),
        ).fetchone()

        if exists is None:
            source_status = get_gp093_status()["gp093_status"]
            source_queue = get_post_closeout_handoff_owner_review_queue_record()["owner_review_queue"]
            source_items = get_post_closeout_handoff_owner_review_items()
            source_policies = get_post_closeout_handoff_owner_review_policies()
            source_blockers = get_post_closeout_handoff_owner_review_blockers()
            source_events = get_post_closeout_handoff_owner_review_events()
            now = _now_iso()

            contract_data = {
                "schema_version": SCHEMA_VERSION,
                "contract_type": "REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT",
                "source_pack": "VAULT_GP093",
                "source_owner_review_queue_id": source_queue["owner_review_queue_id"],
                "source_receipt_ledger_id": source_queue["source_receipt_ledger_id"],
                "source_ledger_hash": source_queue["source_ledger_hash"],
                "source_gp090_readiness_hash": source_queue["source_gp090_readiness_hash"],
                "source_gp090_readiness_score": source_queue["source_gp090_readiness_score"],
                "source_review_item_count": source_items["review_item_count"],
                "source_policy_count": source_policies["policy_count"],
                "source_blocker_count": source_blockers["blocker_count"],
                "source_event_count": source_events["event_count"],
                "source_validation_passed": source_status["validation_passed"],
                "source_safe_to_continue_to_gp094": source_status["safe_to_continue_to_gp094"],
                "owner_review_decision_locked": True,
                "owner_review_decision_template_only": True,
                "owner_review_decision_recorded": False,
                "owner_review_approval_recorded": False,
                "owner_review_rejection_recorded": False,
                "decision_receipt_created": False,
                "tower_unlock_granted": False,
                "vault_done": False,
                "next_pack": NEXT_PACK,
                "next_pack_title": NEXT_PACK_TITLE,
                "safe_to_continue_to_gp095": True,
            }

            contract_row = {
                "decision_lock_contract_id": DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,
                "pack_id": PACK_ID,
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_owner_review_queue_id": source_queue["owner_review_queue_id"],
                "source_receipt_ledger_id": source_queue["source_receipt_ledger_id"],
                "source_ledger_hash": source_queue["source_ledger_hash"],
                "source_gp090_readiness_hash": source_queue["source_gp090_readiness_hash"],
                "source_gp090_readiness_score": source_queue["source_gp090_readiness_score"],
                "source_review_item_count": source_items["review_item_count"],
                "requirement_count": len(DECISION_REQUIREMENT_SPECS),
                "policy_count": len(DECISION_POLICIES),
                "blocker_count": 10,
                "event_count": 6,
                "contract_status": "REAL_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_OPEN_TEMPLATE_ONLY",
                "contract_data_json": _json_dumps(contract_data),
                "created_at": now,
                "updated_at": now,
            }
            for field in TRUE_CONTRACT_FIELDS:
                contract_row[field] = 1
            for field in FALSE_FIELDS:
                contract_row[field] = 0
            _insert_dict(conn, "vault_post_closeout_handoff_owner_review_decision_lock_contracts", contract_row)

            req_false_fields = [
                "requirement_verified",
                "owner_review_decision_recorded",
                "owner_review_approval_recorded",
                "owner_review_rejection_recorded",
                "decision_receipt_created",
                "tower_unlock_granted",
                "restore_request_submitted",
                "restore_object_selected",
                "restore_job_created",
                "provider_restore_api_called",
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

            for code, name, category in DECISION_REQUIREMENT_SPECS:
                row = {
                    "decision_requirement_id": f"VPPCHORDLCR-{code.upper().replace('_', '-')}",
                    "decision_lock_contract_id": DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,
                    "requirement_code": code,
                    "requirement_name": name,
                    "requirement_category": category,
                    "requirement_message": f"{name}; GP094 records the decision lock only and cannot record owner decision, approval, rejection, Tower unlock, restore/API/body/export/upload/execution/Vault-done.",
                    "requirement_status": "REAL_OWNER_REVIEW_DECISION_REQUIREMENT_RECORDED_LOCKED_TEMPLATE_ONLY",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_REQUIREMENT_FIELDS:
                    row[field] = 1
                for field in req_false_fields:
                    row[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_owner_review_decision_requirements", row)

            policy_false_fields = [
                "policy_verified",
                "owner_review_decision_recorded",
                "owner_review_approval_recorded",
                "owner_review_rejection_recorded",
                "decision_receipt_created",
                "tower_unlock_granted",
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

            for code, name, category in DECISION_POLICIES:
                row = {
                    "decision_policy_id": f"VPPCHORDLCP-{code.upper().replace('_', '-')}",
                    "decision_lock_contract_id": DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,
                    "policy_code": code,
                    "policy_name": name,
                    "policy_category": category,
                    "policy_message": f"{name}; GP094 is lock-only and cannot produce a decision, approval, unlock, restore, API call, body read, export, upload, execution, or Vault done state.",
                    "policy_status": "REAL_OWNER_REVIEW_DECISION_POLICY_RECORDED_LOCKED_TEMPLATE_ONLY",
                    "policy_required": 1,
                    "owner_review_required": 1,
                    "tower_review_required": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in policy_false_fields:
                    row[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_owner_review_decision_policies", row)

            blocker_specs = [
                ("block_owner_decision", "Blocks owner decision from GP094", "owner_decision", "critical"),
                ("block_owner_approval", "Blocks owner approval from GP094", "owner_approval", "critical"),
                ("block_owner_rejection", "Blocks owner rejection from GP094", "owner_rejection", "critical"),
                ("block_decision_receipt", "Blocks decision receipt creation from GP094", "decision_receipt", "critical"),
                ("block_tower_unlock", "Blocks Tower unlock from GP094", "tower_unlock", "critical"),
                ("block_restore_unlock", "Blocks restore unlock from GP094", "restore", "critical"),
                ("block_provider_restore_api", "Blocks provider restore API from GP094", "provider_api", "critical"),
                ("block_object_body_access", "Blocks object body access from GP094", "object_body", "critical"),
                ("block_export_and_upload", "Blocks export and direct upload from GP094", "export_upload", "critical"),
                ("block_execution_and_vault_done", "Blocks execution and Vault done from GP094", "execution", "critical"),
            ]

            for code, name, category, severity in blocker_specs:
                row = {
                    "decision_blocker_id": f"VPPCHORDLCB-{code.upper().replace('_', '-')}",
                    "decision_lock_contract_id": DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "REAL_OWNER_REVIEW_DECISION_BLOCKER_ACTIVE",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_BLOCKER_FIELDS:
                    row[field] = 1
                for field in ["owner_review_completed", "tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]:
                    row[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_owner_review_decision_blockers", row)

            for event_type, event_payload in [
                ("REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_CREATED", contract_data),
                ("SOURCE_GP093_OWNER_REVIEW_QUEUE_ATTACHED", {
                    "source_owner_review_queue_id": source_queue["owner_review_queue_id"],
                    "source_validation_passed": source_status["validation_passed"],
                    "source_safe_to_continue_to_gp094": source_status["safe_to_continue_to_gp094"],
                }),
                ("SOURCE_GP092_LEDGER_AND_GP090_HASH_CARRIED_FORWARD", {
                    "source_receipt_ledger_id": source_queue["source_receipt_ledger_id"],
                    "source_ledger_hash": source_queue["source_ledger_hash"],
                    "source_gp090_readiness_hash": source_queue["source_gp090_readiness_hash"],
                    "source_gp090_readiness_score": source_queue["source_gp090_readiness_score"],
                }),
                ("OWNER_REVIEW_DECISION_REQUIREMENTS_CREATED", {"requirement_count": len(DECISION_REQUIREMENT_SPECS)}),
                ("OWNER_REVIEW_DECISION_POLICIES_AND_BLOCKERS_RECORDED", {"policy_count": len(DECISION_POLICIES), "blocker_count": 10}),
                ("OWNER_REVIEW_DECISION_LOCKS_CONFIRMED", {
                    "owner_review_decision_recorded": False,
                    "owner_review_approval_recorded": False,
                    "owner_review_rejection_recorded": False,
                    "tower_unlock_granted": False,
                    "provider_restore_api_called": False,
                    "object_body_read": False,
                    "export_package_created": False,
                    "direct_upload_enabled": False,
                    "execution_enabled": False,
                    "vault_done": False,
                }),
            ]:
                _insert_event(conn, DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _sum_counts(table: str, contract_id: str, fields: list[str], db_path: Optional[str] = None) -> Dict[str, int]:
    selects = ["COUNT(*) AS total_count"]
    for field in fields:
        selects.append(f"SUM(CASE WHEN {field} = 1 THEN 1 ELSE 0 END) AS {field}_count")
    with _connect(db_path) as conn:
        row = conn.execute(
            f"SELECT {', '.join(selects)} FROM {table} WHERE decision_lock_contract_id = ?",
            (contract_id,),
        ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}

def get_post_closeout_handoff_owner_review_decision_lock_contract_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_owner_review_decision_lock_contract(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_owner_review_decision_lock_contracts
            WHERE decision_lock_contract_id = ?
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,),
        ).fetchone()
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "decision_lock_contract": _boolify(row, {"contract_data_json": "contract_data"}),
    }

def get_post_closeout_handoff_owner_review_decision_requirements(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_owner_review_decision_lock_contract(db_path)
    fields = [
        "requirement_required",
        "requirement_verified",
        "decision_locked",
        "template_only",
        "owner_review_required",
        "tower_review_required",
        "owner_review_decision_recorded",
        "owner_review_approval_recorded",
        "owner_review_rejection_recorded",
        "decision_receipt_created",
        "tower_unlock_granted",
        "restore_request_submitted",
        "restore_object_selected",
        "restore_job_created",
        "provider_restore_api_called",
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
    counts = _sum_counts("vault_post_closeout_handoff_owner_review_decision_requirements", DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_owner_review_decision_requirements
            WHERE decision_lock_contract_id = ?
            ORDER BY requirement_category, requirement_code
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,),
        ).fetchall()
    counts["requirement_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "requirements": [_boolify(row) for row in rows]}

def get_post_closeout_handoff_owner_review_decision_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_owner_review_decision_lock_contract(db_path)
    fields = [
        "policy_required",
        "policy_verified",
        "owner_review_required",
        "tower_review_required",
        "owner_review_decision_recorded",
        "owner_review_approval_recorded",
        "owner_review_rejection_recorded",
        "decision_receipt_created",
        "tower_unlock_granted",
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
    counts = _sum_counts("vault_post_closeout_handoff_owner_review_decision_policies", DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_owner_review_decision_policies
            WHERE decision_lock_contract_id = ?
            ORDER BY policy_category, policy_code
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,),
        ).fetchall()
    counts["policy_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "policies": [_boolify(row) for row in rows]}

def get_post_closeout_handoff_owner_review_decision_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_owner_review_decision_lock_contract(db_path)
    fields = TRUE_BLOCKER_FIELDS + ["owner_review_completed", "tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]
    counts = _sum_counts("vault_post_closeout_handoff_owner_review_decision_blockers", DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_owner_review_decision_blockers
            WHERE decision_lock_contract_id = ?
            ORDER BY blocker_category, blocker_code
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,),
        ).fetchall()
    counts["blocker_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "blockers": [_boolify(row) for row in rows]}

def get_post_closeout_handoff_owner_review_decision_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_owner_review_decision_lock_contract(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_owner_review_decision_events
            WHERE decision_lock_contract_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,),
        ).fetchall()
    events = [
        {
            "event_id": row["event_id"],
            "decision_lock_contract_id": row["decision_lock_contract_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def record_post_closeout_handoff_owner_review_decision_event(event_type: str, event_payload: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_owner_review_decision_lock_contract(db_path)
    payload = dict(event_payload or {})
    payload.update({
        "write_type": "REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_EVENT",
        "owner_review_decision_locked": True,
        "owner_review_decision_recorded": False,
        "owner_review_approval_recorded": False,
        "owner_review_rejection_recorded": False,
        "decision_receipt_created": False,
        "tower_unlock_granted": False,
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
        event_id = _insert_event(conn, DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID, event_type, payload)
        conn.commit()
    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "decision_lock_contract_id": DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID,
        "real_sqlite_backed": True,
        **payload,
    }

def validate_post_closeout_handoff_owner_review_decision_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    contract = get_post_closeout_handoff_owner_review_decision_lock_contract_record(db_path)["decision_lock_contract"]
    requirements = get_post_closeout_handoff_owner_review_decision_requirements(db_path)
    policies = get_post_closeout_handoff_owner_review_decision_policies(db_path)
    blockers = get_post_closeout_handoff_owner_review_decision_blockers(db_path)
    events = get_post_closeout_handoff_owner_review_decision_events(db_path)

    false_checks = [(f"NO_CONTRACT_{field.upper()}", contract[field] is False) for field in FALSE_FIELDS]

    checks = [
        ("REAL_SQLITE_OWNER_REVIEW_DECISION_LOCK_CONTRACT_EXISTS", contract["decision_lock_contract_id"] == DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT_ID),
        ("SOURCE_GP093_OWNER_REVIEW_QUEUE_ATTACHED", contract["source_owner_review_queue_id"] == DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID),
        ("SOURCE_GP092_LEDGER_ATTACHED", contract["source_receipt_ledger_id"] == "VPPCHRL-GP092-001"),
        ("SOURCE_LEDGER_HASH_ATTACHED", isinstance(contract["source_ledger_hash"], str) and len(contract["source_ledger_hash"]) == 64),
        ("SOURCE_GP090_READINESS_HASH_ATTACHED", isinstance(contract["source_gp090_readiness_hash"], str) and len(contract["source_gp090_readiness_hash"]) == 64),
        ("SOURCE_GP090_READINESS_SCORE_100", contract["source_gp090_readiness_score"] == 100),
        ("SECTION_GP091_GP100", contract["section_id"] == SECTION_ID and contract["section_range"] == SECTION_RANGE),
        ("CONTRACT_READY", contract["owner_review_decision_lock_contract_ready"] is True),
        ("DECISION_REQUIREMENTS_READY", contract["decision_requirements_ready"] is True),
        ("DECISION_POLICIES_READY", contract["decision_policies_ready"] is True),
        ("DECISION_BLOCKERS_READY", contract["decision_blockers_ready"] is True),
        ("DECISION_EVENTS_READY", contract["decision_events_ready"] is True),
        ("DECISION_VALIDATION_READY", contract["decision_validation_ready"] is True),
        ("DECISION_LOCKED", contract["owner_review_decision_locked"] is True),
        ("DECISION_TEMPLATE_ONLY", contract["owner_review_decision_template_only"] is True),
        ("REQUIREMENTS_EXIST", requirements["requirement_count"] == len(DECISION_REQUIREMENT_SPECS)),
        ("ALL_REQUIREMENTS_LOCKED", requirements["decision_locked_count"] == len(DECISION_REQUIREMENT_SPECS)),
        ("NO_REQUIREMENT_DECISION", requirements["owner_review_decision_recorded_count"] == 0),
        ("NO_REQUIREMENT_APPROVAL", requirements["owner_review_approval_recorded_count"] == 0),
        ("NO_REQUIREMENT_REJECTION", requirements["owner_review_rejection_recorded_count"] == 0),
        ("NO_REQUIREMENT_DECISION_RECEIPT", requirements["decision_receipt_created_count"] == 0),
        ("NO_REQUIREMENT_TOWER_UNLOCK", requirements["tower_unlock_granted_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_API", requirements["provider_restore_api_called_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY", requirements["object_body_read_count"] == 0),
        ("NO_REQUIREMENT_EXPORT", requirements["export_enabled_count"] == 0),
        ("NO_REQUIREMENT_DIRECT_UPLOAD", requirements["direct_upload_enabled_count"] == 0),
        ("NO_REQUIREMENT_EXECUTION", requirements["execution_enabled_count"] == 0),
        ("NO_REQUIREMENT_VAULT_DONE", requirements["vault_done_count"] == 0),
        ("POLICIES_EXIST", policies["policy_count"] == len(DECISION_POLICIES)),
        ("NO_POLICY_DECISION", policies["owner_review_decision_recorded_count"] == 0),
        ("NO_POLICY_APPROVAL", policies["owner_review_approval_recorded_count"] == 0),
        ("NO_POLICY_REJECTION", policies["owner_review_rejection_recorded_count"] == 0),
        ("NO_POLICY_DECISION_RECEIPT", policies["decision_receipt_created_count"] == 0),
        ("NO_POLICY_TOWER_UNLOCK", policies["tower_unlock_granted_count"] == 0),
        ("NO_POLICY_PROVIDER_API", policies["provider_restore_api_called_count"] == 0),
        ("NO_POLICY_OBJECT_BODY", policies["object_body_read_count"] == 0),
        ("NO_POLICY_EXPORT", policies["export_enabled_count"] == 0),
        ("NO_POLICY_DIRECT_UPLOAD", policies["direct_upload_enabled_count"] == 0),
        ("NO_POLICY_EXECUTION", policies["execution_enabled_count"] == 0),
        ("NO_POLICY_VAULT_DONE", policies["vault_done_count"] == 0),
        ("BLOCKERS_EXIST", blockers["blocker_count"] == 10),
        ("ALL_BLOCKERS_ACTIVE", blockers["blocker_active_count"] == 10),
        ("ALL_BLOCKERS_BLOCK_OWNER_DECISION", blockers["blocks_owner_decision_count"] == 10),
        ("ALL_BLOCKERS_BLOCK_OWNER_APPROVAL", blockers["blocks_owner_approval_count"] == 10),
        ("ALL_BLOCKERS_BLOCK_OWNER_REJECTION", blockers["blocks_owner_rejection_count"] == 10),
        ("ALL_BLOCKERS_BLOCK_DECISION_RECEIPT", blockers["blocks_decision_receipt_count"] == 10),
        ("ALL_BLOCKERS_BLOCK_TOWER_UNLOCK", blockers["blocks_tower_unlock_count"] == 10),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", blockers["blocks_provider_restore_api_count"] == 10),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY", blockers["blocks_object_body_access_count"] == 10),
        ("ALL_BLOCKERS_BLOCK_EXPORT", blockers["blocks_export_count"] == 10),
        ("ALL_BLOCKERS_BLOCK_DIRECT_UPLOAD", blockers["blocks_direct_upload_count"] == 10),
        ("ALL_BLOCKERS_BLOCK_EXECUTION", blockers["blocks_execution_count"] == 10),
        ("ALL_BLOCKERS_BLOCK_VAULT_DONE", blockers["blocks_vault_done_count"] == 10),
        ("NO_BLOCKERS_RESOLVED", blockers["resolved_count"] == 0),
        ("EVENT_LOG_EXISTS", events["event_count"] >= 6),
        ("SAFE_TO_CONTINUE_TO_GP095", contract["safe_to_continue_to_gp095"] is True),
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
        "safe_to_continue_to_gp095": len(failed) == 0,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_post_closeout_handoff_owner_review_decision_next_step() -> Dict[str, Any]:
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
            "safe_to_continue_to_gp095": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP094 records the owner review decision lock contract only. Continue to GP095 decision receipt lock contract while no decision, approval, rejection, Tower unlock, restore, provider API, body access, export, direct upload, execution, or Vault done is allowed.",
            "carry_forward_rules": [
                "Carry GP093 owner review queue forward.",
                "Carry GP092 receipt ledger forward.",
                "Carry GP090 readiness hash forward.",
                "Do not record owner decision in GP094.",
                "Do not record owner approval or rejection in GP094.",
                "Do not create decision receipt in GP094.",
                "Keep Tower unlock locked.",
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
        "depends_on": ["VAULT_GP093"],
        "foundation_status": "post_closeout_handoff_owner_review_decision_lock_contract_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_provider_post_closeout_handoff_owner_review_decision_lock_contract",
        "previous_section": PREVIOUS_SECTION_ID,
        "previous_section_range": PREVIOUS_SECTION_RANGE,
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-provider-post-closeout-handoff-owner-review-decision-lock-contract",
        "json_route": "/vault/real-provider-post-closeout-handoff-owner-review-decision-lock-contract.json",
        "record_route": "/vault/post-closeout-handoff-owner-review-decision-lock-contract-record.json",
        "requirements_route": "/vault/post-closeout-handoff-owner-review-decision-requirements.json",
        "policies_route": "/vault/post-closeout-handoff-owner-review-decision-policies.json",
        "blockers_route": "/vault/post-closeout-handoff-owner-review-decision-blockers.json",
        "events_route": "/vault/post-closeout-handoff-owner-review-decision-events.json",
        "validation_route": "/vault/post-closeout-handoff-owner-review-decision-validation.json",
        "next_step_route": "/vault/post-closeout-handoff-owner-review-decision-next-step.json",
        "gp094_status_route": "/vault/gp094-status.json",
    }

def get_real_provider_post_closeout_handoff_owner_review_decision_lock_contract_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_real_provider_post_closeout_handoff_owner_review_decision_lock_contract(db_path)
    contract = get_post_closeout_handoff_owner_review_decision_lock_contract_record(db_path)["decision_lock_contract"]
    requirements = get_post_closeout_handoff_owner_review_decision_requirements(db_path)
    policies = get_post_closeout_handoff_owner_review_decision_policies(db_path)
    blockers = get_post_closeout_handoff_owner_review_decision_blockers(db_path)
    events = get_post_closeout_handoff_owner_review_decision_events(db_path)
    validation = validate_post_closeout_handoff_owner_review_decision_lock_contract(db_path)

    truth = {
        "real_provider_post_closeout_handoff_owner_review_decision_lock_contract_ready": True,
        "real_sqlite_backed": True,
        "source_gp093_owner_review_queue_attached": contract["source_gp093_owner_review_queue_attached"],
        "source_owner_review_queue_id": contract["source_owner_review_queue_id"],
        "source_receipt_ledger_id": contract["source_receipt_ledger_id"],
        "source_ledger_hash": contract["source_ledger_hash"],
        "source_gp090_readiness_hash": contract["source_gp090_readiness_hash"],
        "source_gp090_readiness_score": contract["source_gp090_readiness_score"],
        "requirement_count": requirements["requirement_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "event_count": events["event_count"],
        "owner_review_decision_locked": contract["owner_review_decision_locked"],
        "owner_review_decision_template_only": contract["owner_review_decision_template_only"],
        "owner_review_decision_recorded": contract["owner_review_decision_recorded"],
        "owner_review_approval_recorded": contract["owner_review_approval_recorded"],
        "owner_review_rejection_recorded": contract["owner_review_rejection_recorded"],
        "decision_receipt_created": contract["decision_receipt_created"],
        "tower_unlock_granted": contract["tower_unlock_granted"],
        "provider_restore_api_called": contract["provider_restore_api_called"],
        "object_body_read": contract["object_body_read"],
        "export_package_created": contract["export_package_created"],
        "direct_upload_enabled": contract["direct_upload_enabled"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "safe_to_continue_to_gp095": validation["safe_to_continue_to_gp095"],
        "vault_done": contract["vault_done"],
        "clouds_should_continue": contract["clouds_should_continue"],
    }

    return {
        "pack": _pack_payload(),
        "decision_lock_truth": truth,
        "store": store,
        "decision_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "events": events,
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_post_closeout_handoff_owner_review_decision_next_step()["next_step"],
    }

def get_gp094_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_provider_post_closeout_handoff_owner_review_decision_lock_contract_home(db_path)
    contract = home["decision_lock_contract"]
    requirements = home["requirements"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp094_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_provider_post_closeout_handoff_owner_review_decision_lock_contract_ready": True,
            "real_sqlite_backed": True,
            "real_contract_count": home["store"]["contract_count"],
            "real_requirement_count": home["store"]["requirement_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp093_owner_review_queue_attached": contract["source_gp093_owner_review_queue_attached"],
            "source_owner_review_queue_id": contract["source_owner_review_queue_id"],
            "source_receipt_ledger_id": contract["source_receipt_ledger_id"],
            "source_ledger_hash": contract["source_ledger_hash"],
            "source_gp090_readiness_hash": contract["source_gp090_readiness_hash"],
            "source_gp090_readiness_score": contract["source_gp090_readiness_score"],
            "source_review_item_count": contract["source_review_item_count"],
            "decision_requirements_ready": contract["decision_requirements_ready"],
            "decision_policies_ready": contract["decision_policies_ready"],
            "decision_blockers_ready": contract["decision_blockers_ready"],
            "decision_events_ready": contract["decision_events_ready"],
            "decision_validation_ready": contract["decision_validation_ready"],
            "owner_review_decision_locked": contract["owner_review_decision_locked"],
            "owner_review_decision_template_only": contract["owner_review_decision_template_only"],
            "requirement_count": requirements["requirement_count"],
            "policy_count": policies["policy_count"],
            "blocker_count": blockers["blocker_count"],
            "owner_review_decision_recorded_count": requirements["owner_review_decision_recorded_count"] + policies["owner_review_decision_recorded_count"],
            "owner_review_approval_recorded_count": requirements["owner_review_approval_recorded_count"] + policies["owner_review_approval_recorded_count"],
            "owner_review_rejection_recorded_count": requirements["owner_review_rejection_recorded_count"] + policies["owner_review_rejection_recorded_count"],
            "decision_receipt_created_count": requirements["decision_receipt_created_count"] + policies["decision_receipt_created_count"],
            "tower_unlock_granted_count": requirements["tower_unlock_granted_count"] + policies["tower_unlock_granted_count"],
            "provider_restore_api_called_count": requirements["provider_restore_api_called_count"] + policies["provider_restore_api_called_count"],
            "object_body_read_count": requirements["object_body_read_count"] + policies["object_body_read_count"],
            "export_enabled_count": requirements["export_enabled_count"] + policies["export_enabled_count"],
            "direct_upload_enabled_count": requirements["direct_upload_enabled_count"] + policies["direct_upload_enabled_count"],
            "execution_enabled_count": requirements["execution_enabled_count"] + policies["execution_enabled_count"],
            "vault_done_count": requirements["vault_done_count"] + policies["vault_done_count"],
            "blocks_owner_decision_count": blockers["blocks_owner_decision_count"],
            "blocks_owner_approval_count": blockers["blocks_owner_approval_count"],
            "blocks_owner_rejection_count": blockers["blocks_owner_rejection_count"],
            "blocks_decision_receipt_count": blockers["blocks_decision_receipt_count"],
            "blocks_tower_unlock_count": blockers["blocks_tower_unlock_count"],
            "blocks_provider_restore_api_count": blockers["blocks_provider_restore_api_count"],
            "blocks_object_body_access_count": blockers["blocks_object_body_access_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_direct_upload_count": blockers["blocks_direct_upload_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "blocks_vault_done_count": blockers["blocks_vault_done_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp095": validation["safe_to_continue_to_gp095"],
            "foundation_status": "post_closeout_handoff_owner_review_decision_lock_contract_ready_safe_to_continue_not_done",
            "owner_review_decision_recorded": contract["owner_review_decision_recorded"],
            "owner_review_approval_recorded": contract["owner_review_approval_recorded"],
            "owner_review_rejection_recorded": contract["owner_review_rejection_recorded"],
            "decision_receipt_created": contract["decision_receipt_created"],
            "tower_unlock_granted": contract["tower_unlock_granted"],
            "provider_restore_api_called": contract["provider_restore_api_called"],
            "object_body_read": contract["object_body_read"],
            "export_package_created": contract["export_package_created"],
            "direct_upload_enabled": contract["direct_upload_enabled"],
            "export_enabled": contract["export_enabled"],
            "execution_enabled": contract["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp094",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "decision_lock_truth": home["decision_lock_truth"],
        "routes": home["routes"],
        "decision_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }

def render_real_provider_post_closeout_handoff_owner_review_decision_lock_contract_page() -> str:
    home = get_real_provider_post_closeout_handoff_owner_review_decision_lock_contract_home()
    truth = home["decision_lock_truth"]
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
<title>Vault Owner Review Decision Lock Contract · GP094</title>
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
    <div class="eyebrow">Archive Vault · Giant Pack 094</div>
    <div class="eyebrow">Post-Closeout Handoff Governance Layer · GP091-GP100</div>
    <h1>Real Provider Post-Closeout Handoff Owner Review Decision Lock Contract</h1>
    <p>GP094 defines the owner review decision lock contract. It does not record a decision, approval, rejection, Tower unlock, provider call, body read, export, upload, execution, or Vault-done state.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['requirement_count']}</strong><span>requirements</span></div>
      <div class="metric"><strong>{truth['policy_count']}</strong><span>policies</span></div>
      <div class="metric"><strong>{truth['blocker_count']}</strong><span>lock blockers</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">Decision lock built</span>
      <span class="pill ok">GP093 queue attached</span>
      <span class="pill ok">GP090 hash carried</span>
      <span class="pill danger">No decision</span>
      <span class="pill danger">No approval</span>
      <span class="pill danger">No Tower unlock</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Decision Requirements</h2>
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
    <h2>GP094 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['requirements_route'])}</code>
      <code>{escape(routes['policies_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_step_route'])}</code>
      <code>{escape(routes['gp094_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
