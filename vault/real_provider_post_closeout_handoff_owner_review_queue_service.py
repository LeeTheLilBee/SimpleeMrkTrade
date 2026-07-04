"""
VAULT GP093 — Real Provider Post-Closeout Handoff Owner Review Queue

Current section:
Archive Vault — Real Provider Post-Closeout Handoff Governance Layer / GP091-GP100

This pack creates a real SQLite-backed owner review queue sourced from GP092.
It queues receipt-ledger review items and preserves all restore/export/provider
API/object body/direct upload/execution locks. It does not record an owner
decision, approval, Tower unlock, export, provider call, object body access, or
Vault-done state.
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

from vault.real_provider_post_closeout_handoff_receipt_ledger_service import (
    DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID,
    get_gp092_status,
    get_post_closeout_handoff_receipt_blockers,
    get_post_closeout_handoff_receipt_events,
    get_post_closeout_handoff_receipt_ledger_record,
    get_post_closeout_handoff_receipt_policies,
    get_post_closeout_handoff_receipts,
)

PACK_ID = "VAULT_GP093"
PACK_NAME = "Real Provider Post-Closeout Handoff Owner Review Queue"
SCHEMA_VERSION = "vault.real_provider_post_closeout_handoff_owner_review_queue.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_GOVERNANCE_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Post-Closeout Handoff Governance Layer"
SECTION_RANGE = "GP091-GP100"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_LAYER"
PREVIOUS_SECTION_RANGE = "GP081-GP090"

NEXT_PACK = "VAULT_GP094_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_LOCK_CONTRACT"
NEXT_PACK_TITLE = "Real Provider Post-Closeout Handoff Owner Review Decision Lock Contract"

DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID = "VPPCHORQ-GP093-001"
DEFAULT_DB_ENV = "VAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_DB"
DEFAULT_DB_PATH = "data/vault_post_closeout_handoff_owner_review_queue.sqlite"

OWNER_REVIEW_POLICIES = [
    ("owner_review_queue_no_decision", "Owner review queue cannot record decision", "decision_lock"),
    ("owner_review_queue_no_approval", "Owner review queue cannot approve handoff", "approval_lock"),
    ("owner_review_queue_no_tower_unlock", "Owner review queue cannot grant Tower unlock", "tower_lock"),
    ("owner_review_queue_no_restore_submit", "Owner review queue cannot submit restore", "restore_lock"),
    ("owner_review_queue_no_provider_api", "Owner review queue cannot call provider API", "provider_api_lock"),
    ("owner_review_queue_no_object_body", "Owner review queue cannot read object bodies", "object_body_lock"),
    ("owner_review_queue_no_export", "Owner review queue cannot export", "export_lock"),
    ("owner_review_queue_no_direct_upload", "Owner review queue cannot direct upload", "direct_upload_lock"),
    ("owner_review_queue_no_execution", "Owner review queue cannot execute", "execution_lock"),
    ("owner_review_queue_no_vault_done", "Owner review queue cannot mark Vault done", "vault_done_lock"),
]

FALSE_FIELDS = [
    "owner_review_decision_recorded",
    "owner_review_approval_recorded",
    "owner_review_rejection_recorded",
    "owner_review_escalation_recorded",
    "owner_review_closed",
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

TRUE_QUEUE_FIELDS = [
    "owner_review_queue_ready",
    "source_gp092_receipt_ledger_attached",
    "source_gp091_handoff_contract_attached",
    "source_gp090_readiness_hash_attached",
    "review_items_ready",
    "review_policies_ready",
    "review_blockers_ready",
    "review_events_ready",
    "review_validation_ready",
    "owner_review_required",
    "owner_review_queue_locked",
    "owner_review_template_only",
    "restore_locks_carried_forward",
    "export_locks_carried_forward",
    "provider_restore_api_locks_carried_forward",
    "object_body_access_locks_carried_forward",
    "direct_upload_locks_carried_forward",
    "execution_locks_carried_forward",
    "safe_to_continue_to_gp094",
]

TRUE_ITEM_FIELDS = [
    "review_required",
    "item_queued",
    "item_locked",
    "template_only",
    "owner_review_required",
    "tower_review_required",
]

TRUE_BLOCKER_FIELDS = [
    "blocker_active",
    "blocks_owner_decision",
    "blocks_owner_approval",
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
        "review_item_count",
        "policy_count",
        "blocker_count",
        "event_count",
        "queue_position",
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

def ensure_post_closeout_handoff_owner_review_queue_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_QUEUE_FIELDS)
        false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_owner_review_queues (
                owner_review_queue_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_title TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_receipt_ledger_id TEXT NOT NULL,
                source_ledger_hash TEXT NOT NULL,
                source_gp090_readiness_hash TEXT NOT NULL,
                source_gp090_readiness_score INTEGER NOT NULL,
                review_item_count INTEGER NOT NULL,
                policy_count INTEGER NOT NULL,
                blocker_count INTEGER NOT NULL,
                event_count INTEGER NOT NULL,
                queue_status TEXT NOT NULL,
                queue_data_json TEXT NOT NULL,
                {true_sql},
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        item_false_fields = [
            "item_reviewed",
            "item_decision_recorded",
            "item_approved",
            "item_rejected",
            "item_escalated",
            "owner_review_decision_recorded",
            "owner_review_approval_recorded",
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
        item_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_ITEM_FIELDS)
        item_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in item_false_fields)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_owner_review_items (
                owner_review_item_id TEXT PRIMARY KEY,
                owner_review_queue_id TEXT NOT NULL,
                source_receipt_id TEXT NOT NULL,
                source_receipt_code TEXT NOT NULL,
                source_receipt_hash TEXT NOT NULL,
                queue_position INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                item_category TEXT NOT NULL,
                item_payload_json TEXT NOT NULL,
                item_status TEXT NOT NULL,
                {item_true_sql},
                {item_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(owner_review_queue_id)
                    REFERENCES vault_post_closeout_handoff_owner_review_queues(owner_review_queue_id)
                    ON DELETE CASCADE,
                UNIQUE(owner_review_queue_id, source_receipt_id)
            )
            """
        )

        policy_false_fields = [
            "policy_verified",
            "owner_review_decision_recorded",
            "owner_review_approval_recorded",
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
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_owner_review_policies (
                owner_review_policy_id TEXT PRIMARY KEY,
                owner_review_queue_id TEXT NOT NULL,
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
                FOREIGN KEY(owner_review_queue_id)
                    REFERENCES vault_post_closeout_handoff_owner_review_queues(owner_review_queue_id)
                    ON DELETE CASCADE,
                UNIQUE(owner_review_queue_id, policy_code)
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
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_owner_review_blockers (
                owner_review_blocker_id TEXT PRIMARY KEY,
                owner_review_queue_id TEXT NOT NULL,
                blocker_code TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                {blocker_true_sql},
                {blocker_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(owner_review_queue_id)
                    REFERENCES vault_post_closeout_handoff_owner_review_queues(owner_review_queue_id)
                    ON DELETE CASCADE,
                UNIQUE(owner_review_queue_id, blocker_code)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_owner_review_events (
                event_id TEXT PRIMARY KEY,
                owner_review_queue_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(owner_review_queue_id)
                    REFERENCES vault_post_closeout_handoff_owner_review_queues(owner_review_queue_id)
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
            "vault_post_closeout_handoff_owner_review_queues",
            "vault_post_closeout_handoff_owner_review_items",
            "vault_post_closeout_handoff_owner_review_policies",
            "vault_post_closeout_handoff_owner_review_blockers",
            "vault_post_closeout_handoff_owner_review_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, queue_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VPPCHORQEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_post_closeout_handoff_owner_review_events",
        {
            "event_id": event_id,
            "owner_review_queue_id": queue_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "queue_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_owner_review_queues").fetchone()["c"]),
            "review_item_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_owner_review_items").fetchone()["c"]),
            "policy_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_owner_review_policies").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_owner_review_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_owner_review_events").fetchone()["c"]),
        }

def initialize_real_provider_post_closeout_handoff_owner_review_queue(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_post_closeout_handoff_owner_review_queue_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            """
            SELECT owner_review_queue_id
            FROM vault_post_closeout_handoff_owner_review_queues
            WHERE owner_review_queue_id = ?
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID,),
        ).fetchone()

        if exists is None:
            source_status = get_gp092_status()["gp092_status"]
            source_ledger = get_post_closeout_handoff_receipt_ledger_record()["receipt_ledger"]
            source_receipts = get_post_closeout_handoff_receipts()["receipts"]
            source_policies = get_post_closeout_handoff_receipt_policies()
            source_blockers = get_post_closeout_handoff_receipt_blockers()
            source_events = get_post_closeout_handoff_receipt_events()
            now = _now_iso()

            queue_data = {
                "schema_version": SCHEMA_VERSION,
                "queue_type": "REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE",
                "source_pack": "VAULT_GP092",
                "source_receipt_ledger_id": source_ledger["receipt_ledger_id"],
                "source_ledger_hash": source_ledger["ledger_hash"],
                "source_gp090_readiness_hash": source_ledger["source_gp090_readiness_hash"],
                "source_gp090_readiness_score": source_ledger["source_gp090_readiness_score"],
                "source_validation_passed": source_status["validation_passed"],
                "source_safe_to_continue_to_gp093": source_status["safe_to_continue_to_gp093"],
                "source_receipt_count": len(source_receipts),
                "source_policy_count": source_policies["policy_count"],
                "source_blocker_count": source_blockers["blocker_count"],
                "source_event_count": source_events["event_count"],
                "owner_review_required": True,
                "owner_decision_recorded": False,
                "owner_approval_recorded": False,
                "tower_unlock_granted": False,
                "vault_done": False,
                "next_pack": NEXT_PACK,
                "next_pack_title": NEXT_PACK_TITLE,
                "safe_to_continue_to_gp094": True,
            }

            queue_row = {
                "owner_review_queue_id": DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID,
                "pack_id": PACK_ID,
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_receipt_ledger_id": source_ledger["receipt_ledger_id"],
                "source_ledger_hash": source_ledger["ledger_hash"],
                "source_gp090_readiness_hash": source_ledger["source_gp090_readiness_hash"],
                "source_gp090_readiness_score": source_ledger["source_gp090_readiness_score"],
                "review_item_count": len(source_receipts),
                "policy_count": len(OWNER_REVIEW_POLICIES),
                "blocker_count": 9,
                "event_count": 6,
                "queue_status": "REAL_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_OPEN_LOCKED_TEMPLATE_ONLY",
                "queue_data_json": _json_dumps(queue_data),
                "created_at": now,
                "updated_at": now,
            }
            for field in TRUE_QUEUE_FIELDS:
                queue_row[field] = 1
            for field in FALSE_FIELDS:
                queue_row[field] = 0
            _insert_dict(conn, "vault_post_closeout_handoff_owner_review_queues", queue_row)

            item_false_fields = [
                "item_reviewed",
                "item_decision_recorded",
                "item_approved",
                "item_rejected",
                "item_escalated",
                "owner_review_decision_recorded",
                "owner_review_approval_recorded",
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

            for position, receipt in enumerate(source_receipts, start=1):
                item_payload = {
                    "source_receipt_id": receipt["receipt_id"],
                    "source_receipt_code": receipt["receipt_code"],
                    "source_receipt_hash": receipt["receipt_hash"],
                    "source_receipt_category": receipt["receipt_category"],
                    "source_receipt_payload": receipt["receipt_payload"],
                    "owner_review_required": True,
                    "owner_review_decision_recorded": False,
                    "owner_review_approval_recorded": False,
                    "tower_unlock_granted": False,
                    "vault_done": False,
                }
                row = {
                    "owner_review_item_id": f"VPPCHORQI-{receipt['receipt_code'].upper().replace('_', '-')}",
                    "owner_review_queue_id": DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID,
                    "source_receipt_id": receipt["receipt_id"],
                    "source_receipt_code": receipt["receipt_code"],
                    "source_receipt_hash": receipt["receipt_hash"],
                    "queue_position": position,
                    "item_name": f"Owner review item for {receipt['receipt_name']}",
                    "item_category": receipt["receipt_category"],
                    "item_payload_json": _json_dumps(item_payload),
                    "item_status": "QUEUED_FOR_OWNER_REVIEW_LOCKED_TEMPLATE_ONLY",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_ITEM_FIELDS:
                    row[field] = 1
                for field in item_false_fields:
                    row[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_owner_review_items", row)

            policy_false_fields = [
                "policy_verified",
                "owner_review_decision_recorded",
                "owner_review_approval_recorded",
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

            for code, name, category in OWNER_REVIEW_POLICIES:
                row = {
                    "owner_review_policy_id": f"VPPCHORQP-{code.upper().replace('_', '-')}",
                    "owner_review_queue_id": DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID,
                    "policy_code": code,
                    "policy_name": name,
                    "policy_category": category,
                    "policy_message": f"{name}; GP093 queues owner review only and cannot approve, unlock, restore, call provider APIs, read bodies, export, upload, execute, or mark Vault done.",
                    "policy_status": "REAL_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_POLICY_RECORDED_LOCKED",
                    "policy_required": 1,
                    "owner_review_required": 1,
                    "tower_review_required": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in policy_false_fields:
                    row[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_owner_review_policies", row)

            blocker_specs = [
                ("block_owner_decision", "Blocks owner decision from queue", "owner_decision", "critical"),
                ("block_owner_approval", "Blocks owner approval from queue", "owner_approval", "critical"),
                ("block_tower_unlock", "Blocks Tower unlock from queue", "tower_unlock", "critical"),
                ("block_restore_unlock", "Blocks restore unlock from queue", "restore", "critical"),
                ("block_provider_restore_api", "Blocks provider restore API from queue", "provider_api", "critical"),
                ("block_object_body_access", "Blocks object body access from queue", "object_body", "critical"),
                ("block_export", "Blocks export from queue", "export", "critical"),
                ("block_direct_upload", "Blocks direct upload from queue", "direct_upload", "critical"),
                ("block_execution_and_vault_done", "Blocks execution and Vault done from queue", "execution", "critical"),
            ]

            for code, name, category, severity in blocker_specs:
                row = {
                    "owner_review_blocker_id": f"VPPCHORQB-{code.upper().replace('_', '-')}",
                    "owner_review_queue_id": DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "REAL_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_BLOCKER_ACTIVE",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_BLOCKER_FIELDS:
                    row[field] = 1
                for field in ["owner_review_completed", "tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]:
                    row[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_owner_review_blockers", row)

            for event_type, event_payload in [
                ("REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_CREATED", queue_data),
                ("SOURCE_GP092_RECEIPT_LEDGER_ATTACHED", {
                    "source_receipt_ledger_id": source_ledger["receipt_ledger_id"],
                    "source_ledger_hash": source_ledger["ledger_hash"],
                    "source_validation_passed": source_status["validation_passed"],
                    "source_safe_to_continue_to_gp093": source_status["safe_to_continue_to_gp093"],
                }),
                ("SOURCE_GP090_READINESS_HASH_CARRIED_FORWARD", {
                    "source_gp090_readiness_hash": source_ledger["source_gp090_readiness_hash"],
                    "source_gp090_readiness_score": source_ledger["source_gp090_readiness_score"],
                }),
                ("OWNER_REVIEW_ITEMS_QUEUED", {"review_item_count": len(source_receipts)}),
                ("OWNER_REVIEW_POLICIES_AND_BLOCKERS_RECORDED", {"policy_count": len(OWNER_REVIEW_POLICIES), "blocker_count": 9}),
                ("OWNER_REVIEW_QUEUE_LOCKS_CONFIRMED", {
                    "owner_review_decision_recorded": False,
                    "owner_review_approval_recorded": False,
                    "tower_unlock_granted": False,
                    "provider_restore_api_called": False,
                    "object_body_read": False,
                    "export_package_created": False,
                    "direct_upload_enabled": False,
                    "execution_enabled": False,
                    "vault_done": False,
                }),
            ]:
                _insert_event(conn, DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _sum_counts(table: str, queue_id: str, fields: list[str], db_path: Optional[str] = None) -> Dict[str, int]:
    selects = ["COUNT(*) AS total_count"]
    for field in fields:
        selects.append(f"SUM(CASE WHEN {field} = 1 THEN 1 ELSE 0 END) AS {field}_count")
    with _connect(db_path) as conn:
        row = conn.execute(
            f"SELECT {', '.join(selects)} FROM {table} WHERE owner_review_queue_id = ?",
            (queue_id,),
        ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}

def get_post_closeout_handoff_owner_review_queue_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_owner_review_queue(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_owner_review_queues
            WHERE owner_review_queue_id = ?
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID,),
        ).fetchone()
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "owner_review_queue": _boolify(row, {"queue_data_json": "queue_data"}),
    }

def get_post_closeout_handoff_owner_review_items(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_owner_review_queue(db_path)
    fields = [
        "review_required",
        "item_queued",
        "item_locked",
        "template_only",
        "owner_review_required",
        "tower_review_required",
        "item_reviewed",
        "item_decision_recorded",
        "item_approved",
        "item_rejected",
        "item_escalated",
        "owner_review_decision_recorded",
        "owner_review_approval_recorded",
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
    counts = _sum_counts("vault_post_closeout_handoff_owner_review_items", DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_owner_review_items
            WHERE owner_review_queue_id = ?
            ORDER BY queue_position
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID,),
        ).fetchall()
    items = [_boolify(row, {"item_payload_json": "item_payload"}) for row in rows]
    counts["review_item_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "items": items}

def get_post_closeout_handoff_owner_review_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_owner_review_queue(db_path)
    fields = [
        "policy_required",
        "policy_verified",
        "owner_review_required",
        "tower_review_required",
        "owner_review_decision_recorded",
        "owner_review_approval_recorded",
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
    counts = _sum_counts("vault_post_closeout_handoff_owner_review_policies", DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_owner_review_policies
            WHERE owner_review_queue_id = ?
            ORDER BY policy_category, policy_code
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID,),
        ).fetchall()
    counts["policy_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "policies": [_boolify(row) for row in rows]}

def get_post_closeout_handoff_owner_review_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_owner_review_queue(db_path)
    fields = TRUE_BLOCKER_FIELDS + ["owner_review_completed", "tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]
    counts = _sum_counts("vault_post_closeout_handoff_owner_review_blockers", DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_owner_review_blockers
            WHERE owner_review_queue_id = ?
            ORDER BY blocker_category, blocker_code
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID,),
        ).fetchall()
    counts["blocker_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "blockers": [_boolify(row) for row in rows]}

def get_post_closeout_handoff_owner_review_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_owner_review_queue(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_owner_review_events
            WHERE owner_review_queue_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID,),
        ).fetchall()
    events = [
        {
            "event_id": row["event_id"],
            "owner_review_queue_id": row["owner_review_queue_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def record_post_closeout_handoff_owner_review_event(event_type: str, event_payload: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_owner_review_queue(db_path)
    payload = dict(event_payload or {})
    payload.update({
        "write_type": "REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_EVENT",
        "owner_review_queue_locked": True,
        "owner_review_decision_recorded": False,
        "owner_review_approval_recorded": False,
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
        event_id = _insert_event(conn, DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID, event_type, payload)
        conn.commit()
    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "owner_review_queue_id": DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID,
        "real_sqlite_backed": True,
        **payload,
    }

def validate_post_closeout_handoff_owner_review_queue(db_path: Optional[str] = None) -> Dict[str, Any]:
    queue = get_post_closeout_handoff_owner_review_queue_record(db_path)["owner_review_queue"]
    items = get_post_closeout_handoff_owner_review_items(db_path)
    policies = get_post_closeout_handoff_owner_review_policies(db_path)
    blockers = get_post_closeout_handoff_owner_review_blockers(db_path)
    events = get_post_closeout_handoff_owner_review_events(db_path)

    false_checks = [(f"NO_QUEUE_{field.upper()}", queue[field] is False) for field in FALSE_FIELDS]

    checks = [
        ("REAL_SQLITE_POST_CLOSEOUT_OWNER_REVIEW_QUEUE_EXISTS", queue["owner_review_queue_id"] == DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE_ID),
        ("SOURCE_GP092_RECEIPT_LEDGER_ATTACHED", queue["source_receipt_ledger_id"] == DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID),
        ("SOURCE_LEDGER_HASH_ATTACHED", isinstance(queue["source_ledger_hash"], str) and len(queue["source_ledger_hash"]) == 64),
        ("SOURCE_GP090_READINESS_HASH_ATTACHED", isinstance(queue["source_gp090_readiness_hash"], str) and len(queue["source_gp090_readiness_hash"]) == 64),
        ("SOURCE_GP090_READINESS_SCORE_100", queue["source_gp090_readiness_score"] == 100),
        ("SECTION_GP091_GP100", queue["section_id"] == SECTION_ID and queue["section_range"] == SECTION_RANGE),
        ("QUEUE_READY", queue["owner_review_queue_ready"] is True),
        ("REVIEW_ITEMS_READY", queue["review_items_ready"] is True),
        ("REVIEW_POLICIES_READY", queue["review_policies_ready"] is True),
        ("REVIEW_BLOCKERS_READY", queue["review_blockers_ready"] is True),
        ("REVIEW_EVENTS_READY", queue["review_events_ready"] is True),
        ("REVIEW_VALIDATION_READY", queue["review_validation_ready"] is True),
        ("OWNER_REVIEW_REQUIRED", queue["owner_review_required"] is True),
        ("QUEUE_LOCKED", queue["owner_review_queue_locked"] is True),
        ("QUEUE_TEMPLATE_ONLY", queue["owner_review_template_only"] is True),
        ("ITEM_COUNT_MATCHES", items["review_item_count"] == 8),
        ("ALL_ITEMS_QUEUED", items["item_queued_count"] == 8),
        ("ALL_ITEMS_LOCKED", items["item_locked_count"] == 8),
        ("NO_ITEM_REVIEWED", items["item_reviewed_count"] == 0),
        ("NO_ITEM_DECISION", items["item_decision_recorded_count"] == 0),
        ("NO_ITEM_APPROVAL", items["item_approved_count"] == 0),
        ("NO_ITEM_PROVIDER_API", items["provider_restore_api_called_count"] == 0),
        ("NO_ITEM_OBJECT_BODY", items["object_body_read_count"] == 0),
        ("NO_ITEM_EXPORT", items["export_enabled_count"] == 0),
        ("NO_ITEM_DIRECT_UPLOAD", items["direct_upload_enabled_count"] == 0),
        ("NO_ITEM_EXECUTION", items["execution_enabled_count"] == 0),
        ("NO_ITEM_VAULT_DONE", items["vault_done_count"] == 0),
        ("POLICIES_EXIST", policies["policy_count"] == len(OWNER_REVIEW_POLICIES)),
        ("NO_POLICY_OWNER_DECISION", policies["owner_review_decision_recorded_count"] == 0),
        ("NO_POLICY_OWNER_APPROVAL", policies["owner_review_approval_recorded_count"] == 0),
        ("NO_POLICY_TOWER_UNLOCK", policies["tower_unlock_granted_count"] == 0),
        ("NO_POLICY_PROVIDER_API", policies["provider_restore_api_called_count"] == 0),
        ("NO_POLICY_OBJECT_BODY", policies["object_body_read_count"] == 0),
        ("NO_POLICY_EXPORT", policies["export_enabled_count"] == 0),
        ("NO_POLICY_DIRECT_UPLOAD", policies["direct_upload_enabled_count"] == 0),
        ("NO_POLICY_EXECUTION", policies["execution_enabled_count"] == 0),
        ("NO_POLICY_VAULT_DONE", policies["vault_done_count"] == 0),
        ("BLOCKERS_EXIST", blockers["blocker_count"] == 9),
        ("ALL_BLOCKERS_ACTIVE", blockers["blocker_active_count"] == 9),
        ("ALL_BLOCKERS_BLOCK_OWNER_DECISION", blockers["blocks_owner_decision_count"] == 9),
        ("ALL_BLOCKERS_BLOCK_OWNER_APPROVAL", blockers["blocks_owner_approval_count"] == 9),
        ("ALL_BLOCKERS_BLOCK_TOWER_UNLOCK", blockers["blocks_tower_unlock_count"] == 9),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", blockers["blocks_provider_restore_api_count"] == 9),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY", blockers["blocks_object_body_access_count"] == 9),
        ("ALL_BLOCKERS_BLOCK_EXPORT", blockers["blocks_export_count"] == 9),
        ("ALL_BLOCKERS_BLOCK_DIRECT_UPLOAD", blockers["blocks_direct_upload_count"] == 9),
        ("ALL_BLOCKERS_BLOCK_EXECUTION", blockers["blocks_execution_count"] == 9),
        ("ALL_BLOCKERS_BLOCK_VAULT_DONE", blockers["blocks_vault_done_count"] == 9),
        ("NO_BLOCKERS_RESOLVED", blockers["resolved_count"] == 0),
        ("EVENT_LOG_EXISTS", events["event_count"] >= 6),
        ("SAFE_TO_CONTINUE_TO_GP094", queue["safe_to_continue_to_gp094"] is True),
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
        "safe_to_continue_to_gp094": len(failed) == 0,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_post_closeout_handoff_owner_review_next_step() -> Dict[str, Any]:
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
            "safe_to_continue_to_gp094": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP093 queues the post-closeout handoff for owner review. Continue to GP094 decision lock contract while no decision, approval, Tower unlock, restore, provider API, object body access, export, direct upload, execution, or Vault done is allowed.",
            "carry_forward_rules": [
                "Carry GP092 receipt ledger forward.",
                "Carry GP091 handoff contract forward.",
                "Carry GP090 readiness hash forward.",
                "Keep owner review as queued only.",
                "Do not record owner approval or rejection in GP093.",
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
        "depends_on": ["VAULT_GP092"],
        "foundation_status": "post_closeout_handoff_owner_review_queue_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_provider_post_closeout_handoff_owner_review_queue",
        "previous_section": PREVIOUS_SECTION_ID,
        "previous_section_range": PREVIOUS_SECTION_RANGE,
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-provider-post-closeout-handoff-owner-review-queue",
        "json_route": "/vault/real-provider-post-closeout-handoff-owner-review-queue.json",
        "record_route": "/vault/post-closeout-handoff-owner-review-queue-record.json",
        "items_route": "/vault/post-closeout-handoff-owner-review-items.json",
        "policies_route": "/vault/post-closeout-handoff-owner-review-policies.json",
        "blockers_route": "/vault/post-closeout-handoff-owner-review-blockers.json",
        "events_route": "/vault/post-closeout-handoff-owner-review-events.json",
        "validation_route": "/vault/post-closeout-handoff-owner-review-validation.json",
        "next_step_route": "/vault/post-closeout-handoff-owner-review-next-step.json",
        "gp093_status_route": "/vault/gp093-status.json",
    }

def get_real_provider_post_closeout_handoff_owner_review_queue_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_real_provider_post_closeout_handoff_owner_review_queue(db_path)
    queue = get_post_closeout_handoff_owner_review_queue_record(db_path)["owner_review_queue"]
    items = get_post_closeout_handoff_owner_review_items(db_path)
    policies = get_post_closeout_handoff_owner_review_policies(db_path)
    blockers = get_post_closeout_handoff_owner_review_blockers(db_path)
    events = get_post_closeout_handoff_owner_review_events(db_path)
    validation = validate_post_closeout_handoff_owner_review_queue(db_path)

    truth = {
        "real_provider_post_closeout_handoff_owner_review_queue_ready": True,
        "real_sqlite_backed": True,
        "source_gp092_receipt_ledger_attached": queue["source_gp092_receipt_ledger_attached"],
        "source_receipt_ledger_id": queue["source_receipt_ledger_id"],
        "source_ledger_hash": queue["source_ledger_hash"],
        "source_gp090_readiness_hash": queue["source_gp090_readiness_hash"],
        "source_gp090_readiness_score": queue["source_gp090_readiness_score"],
        "review_item_count": items["review_item_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "event_count": events["event_count"],
        "owner_review_required": queue["owner_review_required"],
        "owner_review_queue_locked": queue["owner_review_queue_locked"],
        "owner_review_template_only": queue["owner_review_template_only"],
        "owner_review_decision_recorded": queue["owner_review_decision_recorded"],
        "owner_review_approval_recorded": queue["owner_review_approval_recorded"],
        "tower_unlock_granted": queue["tower_unlock_granted"],
        "provider_restore_api_called": queue["provider_restore_api_called"],
        "object_body_read": queue["object_body_read"],
        "export_package_created": queue["export_package_created"],
        "direct_upload_enabled": queue["direct_upload_enabled"],
        "export_enabled": queue["export_enabled"],
        "execution_enabled": queue["execution_enabled"],
        "safe_to_continue_to_gp094": validation["safe_to_continue_to_gp094"],
        "vault_done": queue["vault_done"],
        "clouds_should_continue": queue["clouds_should_continue"],
    }

    return {
        "pack": _pack_payload(),
        "owner_review_queue_truth": truth,
        "store": store,
        "owner_review_queue": queue,
        "items": items,
        "policies": policies,
        "blockers": blockers,
        "events": events,
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_post_closeout_handoff_owner_review_next_step()["next_step"],
    }

def get_gp093_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_provider_post_closeout_handoff_owner_review_queue_home(db_path)
    queue = home["owner_review_queue"]
    items = home["items"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp093_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_provider_post_closeout_handoff_owner_review_queue_ready": True,
            "real_sqlite_backed": True,
            "real_queue_count": home["store"]["queue_count"],
            "real_review_item_count": home["store"]["review_item_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp092_receipt_ledger_attached": queue["source_gp092_receipt_ledger_attached"],
            "source_receipt_ledger_id": queue["source_receipt_ledger_id"],
            "source_ledger_hash": queue["source_ledger_hash"],
            "source_gp090_readiness_hash": queue["source_gp090_readiness_hash"],
            "source_gp090_readiness_score": queue["source_gp090_readiness_score"],
            "review_items_ready": queue["review_items_ready"],
            "review_policies_ready": queue["review_policies_ready"],
            "review_blockers_ready": queue["review_blockers_ready"],
            "review_events_ready": queue["review_events_ready"],
            "review_validation_ready": queue["review_validation_ready"],
            "owner_review_required": queue["owner_review_required"],
            "owner_review_queue_locked": queue["owner_review_queue_locked"],
            "owner_review_template_only": queue["owner_review_template_only"],
            "review_item_count": items["review_item_count"],
            "policy_count": policies["policy_count"],
            "blocker_count": blockers["blocker_count"],
            "owner_review_decision_recorded_count": items["owner_review_decision_recorded_count"] + policies["owner_review_decision_recorded_count"],
            "owner_review_approval_recorded_count": items["owner_review_approval_recorded_count"] + policies["owner_review_approval_recorded_count"],
            "tower_unlock_granted_count": items["tower_unlock_granted_count"] + policies["tower_unlock_granted_count"],
            "provider_restore_api_called_count": items["provider_restore_api_called_count"] + policies["provider_restore_api_called_count"],
            "object_body_read_count": items["object_body_read_count"] + policies["object_body_read_count"],
            "export_enabled_count": items["export_enabled_count"] + policies["export_enabled_count"],
            "direct_upload_enabled_count": items["direct_upload_enabled_count"] + policies["direct_upload_enabled_count"],
            "execution_enabled_count": items["execution_enabled_count"] + policies["execution_enabled_count"],
            "vault_done_count": items["vault_done_count"] + policies["vault_done_count"],
            "blocks_owner_decision_count": blockers["blocks_owner_decision_count"],
            "blocks_owner_approval_count": blockers["blocks_owner_approval_count"],
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
            "safe_to_continue_to_gp094": validation["safe_to_continue_to_gp094"],
            "foundation_status": "post_closeout_handoff_owner_review_queue_ready_safe_to_continue_not_done",
            "owner_review_decision_recorded": queue["owner_review_decision_recorded"],
            "owner_review_approval_recorded": queue["owner_review_approval_recorded"],
            "tower_unlock_granted": queue["tower_unlock_granted"],
            "provider_restore_api_called": queue["provider_restore_api_called"],
            "object_body_read": queue["object_body_read"],
            "export_package_created": queue["export_package_created"],
            "direct_upload_enabled": queue["direct_upload_enabled"],
            "export_enabled": queue["export_enabled"],
            "execution_enabled": queue["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp093",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "owner_review_queue_truth": home["owner_review_queue_truth"],
        "routes": home["routes"],
        "owner_review_queue": queue,
        "items": items,
        "policies": policies,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }

def render_real_provider_post_closeout_handoff_owner_review_queue_page() -> str:
    home = get_real_provider_post_closeout_handoff_owner_review_queue_home()
    truth = home["owner_review_queue_truth"]
    routes = home["routes"]
    next_step = home["next_step"]

    item_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['source_receipt_code'])}</strong>
          <span>{escape(item['item_name'])}</span>
          <code>Queue #{item['queue_position']}</code>
        </article>
        """
        for item in home["items"]["items"]
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
<title>Vault Post-Closeout Handoff Owner Review Queue · GP093</title>
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
.cards {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin-top:18px; }}
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
    <div class="eyebrow">Archive Vault · Giant Pack 093</div>
    <div class="eyebrow">Post-Closeout Handoff Governance Layer · GP091-GP100</div>
    <h1>Real Provider Post-Closeout Handoff Owner Review Queue</h1>
    <p>GP093 queues the GP092 receipt ledger for owner review. It does not record a decision, approval, Tower unlock, restore action, provider call, object body read, export, direct upload, execution, or Vault-done state.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['review_item_count']}</strong><span>review items</span></div>
      <div class="metric"><strong>{truth['policy_count']}</strong><span>policies</span></div>
      <div class="metric"><strong>{truth['blocker_count']}</strong><span>lock blockers</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">Owner review queued</span>
      <span class="pill ok">GP092 ledger attached</span>
      <span class="pill ok">GP090 hash carried</span>
      <span class="pill danger">No approval</span>
      <span class="pill danger">No Tower unlock</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Owner Review Items</h2>
    <div class="cards">{item_cards}</div>
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
    <h2>GP093 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['items_route'])}</code>
      <code>{escape(routes['policies_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_step_route'])}</code>
      <code>{escape(routes['gp093_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
