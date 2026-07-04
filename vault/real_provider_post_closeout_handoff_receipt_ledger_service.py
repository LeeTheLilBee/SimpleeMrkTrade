"""
VAULT GP092 — Real Provider Post-Closeout Handoff Receipt Ledger

Current section:
Archive Vault — Real Provider Post-Closeout Handoff Governance Layer / GP091-GP100

This pack builds a real SQLite-backed receipt ledger sourced from GP091. It
records durable handoff receipts, receipt hashes, policy rows, blocker rows,
events, validation, and a ledger hash while keeping restore, provider API calls,
object body access, exports, direct upload, execution, and Vault done locked.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Dict, Optional

from vault.real_provider_post_closeout_handoff_lock_contract_service import (
    DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID,
    get_gp091_status,
    get_post_closeout_handoff_blockers,
    get_post_closeout_handoff_events,
    get_post_closeout_handoff_lock_contract_record,
    get_post_closeout_handoff_policies,
    get_post_closeout_handoff_requirements,
)

PACK_ID = "VAULT_GP092"
PACK_NAME = "Real Provider Post-Closeout Handoff Receipt Ledger"
SCHEMA_VERSION = "vault.real_provider_post_closeout_handoff_receipt_ledger.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_GOVERNANCE_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Post-Closeout Handoff Governance Layer"
SECTION_RANGE = "GP091-GP100"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_LAYER"
PREVIOUS_SECTION_RANGE = "GP081-GP090"

NEXT_PACK = "VAULT_GP093_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_QUEUE"
NEXT_PACK_TITLE = "Real Provider Post-Closeout Handoff Owner Review Queue"

DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID = "VPPCHRL-GP092-001"
DEFAULT_DB_ENV = "VAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_DB"
DEFAULT_DB_PATH = "data/vault_post_closeout_handoff_receipt_ledger.sqlite"

RECEIPT_SPECS = [
    ("source_gp091_contract_receipt", "Source GP091 contract receipt", "source_contract"),
    ("source_gp090_hash_receipt", "Source GP090 readiness hash receipt", "source_hash"),
    ("section_handoff_receipt", "GP091-GP100 section handoff receipt", "section_handoff"),
    ("lock_carryforward_receipt", "Lock carry-forward receipt", "lock_carryforward"),
    ("policy_snapshot_receipt", "Post-closeout policy snapshot receipt", "policy_snapshot"),
    ("blocker_snapshot_receipt", "Post-closeout blocker snapshot receipt", "blocker_snapshot"),
    ("event_snapshot_receipt", "Post-closeout event snapshot receipt", "event_snapshot"),
    ("next_pack_receipt", "GP093 next-pack handoff receipt", "next_pack"),
]

RECEIPT_POLICIES = [
    ("receipt_ledger_no_unlock", "Receipt ledger cannot unlock", "ledger_lock"),
    ("receipt_ledger_no_restore_submit", "Receipt ledger cannot submit restore", "restore_lock"),
    ("receipt_ledger_no_provider_api", "Receipt ledger cannot call provider API", "provider_api_lock"),
    ("receipt_ledger_no_object_body", "Receipt ledger cannot read object bodies", "object_body_lock"),
    ("receipt_ledger_no_export", "Receipt ledger cannot export", "export_lock"),
    ("receipt_ledger_no_direct_upload", "Receipt ledger cannot direct upload", "direct_upload_lock"),
    ("receipt_ledger_no_execution", "Receipt ledger cannot execute", "execution_lock"),
    ("receipt_ledger_no_vault_done", "Receipt ledger cannot mark Vault done", "vault_done_lock"),
    ("receipt_ledger_hash_required", "Receipt ledger hash required", "hash_required"),
    ("receipt_ledger_next_review_required", "Receipt ledger next owner review required", "next_review"),
]

FALSE_FIELDS = [
    "receipt_unlock_configured",
    "receipt_unlock_attempted",
    "receipt_unlock_enabled",
    "receipt_approval_granted",
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

TRUE_LEDGER_FIELDS = [
    "post_closeout_handoff_receipt_ledger_ready",
    "source_gp091_handoff_contract_attached",
    "source_gp090_readiness_hash_attached",
    "receipt_rows_ready",
    "receipt_hashes_ready",
    "ledger_hash_ready",
    "receipt_policies_ready",
    "receipt_blockers_ready",
    "receipt_validation_ready",
    "receipt_ledger_locked",
    "receipt_ledger_template_only",
    "restore_locks_carried_forward",
    "export_locks_carried_forward",
    "provider_restore_api_locks_carried_forward",
    "object_body_access_locks_carried_forward",
    "direct_upload_locks_carried_forward",
    "execution_locks_carried_forward",
    "safe_to_continue_to_gp093",
]

TRUE_RECEIPT_FIELDS = [
    "receipt_required",
    "receipt_recorded",
    "receipt_hash_recorded",
    "receipt_locked",
    "template_only",
    "tower_review_required",
]

TRUE_BLOCKER_FIELDS = [
    "blocker_active",
    "blocks_receipt_unlock",
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

def _boolify(row: sqlite3.Row, json_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    json_fields = json_fields or {}
    numeric_fields = {
        "source_gp090_readiness_score",
        "receipt_count",
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
        ):
            payload[key] = int(row[key])
        elif isinstance(row[key], int):
            payload[key] = bool(row[key])
        else:
            payload[key] = row[key]
    return payload

def ensure_post_closeout_handoff_receipt_ledger_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_LEDGER_FIELDS)
        false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_receipt_ledgers (
                receipt_ledger_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_title TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_handoff_lock_contract_id TEXT NOT NULL,
                source_gp090_readiness_hash TEXT NOT NULL,
                source_gp090_readiness_score INTEGER NOT NULL,
                receipt_count INTEGER NOT NULL,
                policy_count INTEGER NOT NULL,
                blocker_count INTEGER NOT NULL,
                event_count INTEGER NOT NULL,
                ledger_hash TEXT NOT NULL,
                ledger_status TEXT NOT NULL,
                ledger_data_json TEXT NOT NULL,
                {true_sql},
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        receipt_false_fields = [
            "receipt_unlock_configured",
            "receipt_unlock_attempted",
            "receipt_unlock_enabled",
            "receipt_approval_granted",
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
        receipt_true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_RECEIPT_FIELDS)
        receipt_false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in receipt_false_fields)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_receipts (
                receipt_id TEXT PRIMARY KEY,
                receipt_ledger_id TEXT NOT NULL,
                receipt_code TEXT NOT NULL,
                receipt_name TEXT NOT NULL,
                receipt_category TEXT NOT NULL,
                receipt_payload_json TEXT NOT NULL,
                receipt_hash TEXT NOT NULL,
                receipt_status TEXT NOT NULL,
                {receipt_true_sql},
                {receipt_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(receipt_ledger_id)
                    REFERENCES vault_post_closeout_handoff_receipt_ledgers(receipt_ledger_id)
                    ON DELETE CASCADE,
                UNIQUE(receipt_ledger_id, receipt_code)
            )
            """
        )

        policy_false_fields = [
            "policy_verified",
            "receipt_unlock_configured",
            "receipt_unlock_enabled",
            "receipt_approval_granted",
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
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_receipt_policies (
                receipt_policy_id TEXT PRIMARY KEY,
                receipt_ledger_id TEXT NOT NULL,
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
                FOREIGN KEY(receipt_ledger_id)
                    REFERENCES vault_post_closeout_handoff_receipt_ledgers(receipt_ledger_id)
                    ON DELETE CASCADE,
                UNIQUE(receipt_ledger_id, policy_code)
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
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_receipt_blockers (
                receipt_blocker_id TEXT PRIMARY KEY,
                receipt_ledger_id TEXT NOT NULL,
                blocker_code TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                {blocker_true_sql},
                {blocker_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(receipt_ledger_id)
                    REFERENCES vault_post_closeout_handoff_receipt_ledgers(receipt_ledger_id)
                    ON DELETE CASCADE,
                UNIQUE(receipt_ledger_id, blocker_code)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_receipt_events (
                event_id TEXT PRIMARY KEY,
                receipt_ledger_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(receipt_ledger_id)
                    REFERENCES vault_post_closeout_handoff_receipt_ledgers(receipt_ledger_id)
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
            "vault_post_closeout_handoff_receipt_ledgers",
            "vault_post_closeout_handoff_receipts",
            "vault_post_closeout_handoff_receipt_policies",
            "vault_post_closeout_handoff_receipt_blockers",
            "vault_post_closeout_handoff_receipt_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, ledger_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VPPCHRLEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_post_closeout_handoff_receipt_events",
        {
            "event_id": event_id,
            "receipt_ledger_id": ledger_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "ledger_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_receipt_ledgers").fetchone()["c"]),
            "receipt_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_receipts").fetchone()["c"]),
            "policy_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_receipt_policies").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_receipt_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_receipt_events").fetchone()["c"]),
        }

def _build_receipt_payloads(source_status: Dict[str, Any], source_contract: Dict[str, Any]) -> list[Dict[str, Any]]:
    source_requirements = get_post_closeout_handoff_requirements()
    source_policies = get_post_closeout_handoff_policies()
    source_blockers = get_post_closeout_handoff_blockers()
    source_events = get_post_closeout_handoff_events()

    payloads = {
        "source_gp091_contract_receipt": {
            "source_contract_id": source_contract["handoff_lock_contract_id"],
            "source_pack": source_contract["pack_id"],
            "source_section": source_contract["section_id"],
            "source_section_range": source_contract["section_range"],
            "source_safe_to_continue_to_gp092": source_status["safe_to_continue_to_gp092"],
        },
        "source_gp090_hash_receipt": {
            "source_gp090_checkpoint_id": source_contract["source_gp090_checkpoint_id"],
            "source_gp090_readiness_hash": source_contract["source_gp090_readiness_hash"],
            "source_gp090_readiness_score": source_contract["source_gp090_readiness_score"],
            "source_gp090_section_closed": source_contract["source_gp090_section_closed"],
        },
        "section_handoff_receipt": {
            "previous_section_id": PREVIOUS_SECTION_ID,
            "previous_section_range": PREVIOUS_SECTION_RANGE,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "next_pack": NEXT_PACK,
        },
        "lock_carryforward_receipt": {
            "restore_locks_carried_forward": source_contract["restore_locks_carried_forward"],
            "export_locks_carried_forward": source_contract["export_locks_carried_forward"],
            "provider_restore_api_locks_carried_forward": source_contract["provider_restore_api_locks_carried_forward"],
            "object_body_access_locks_carried_forward": source_contract["object_body_access_locks_carried_forward"],
            "direct_upload_locks_carried_forward": source_contract["direct_upload_locks_carried_forward"],
            "execution_locks_carried_forward": source_contract["execution_locks_carried_forward"],
        },
        "policy_snapshot_receipt": {
            "source_policy_count": source_policies["policy_count"],
            "source_handoff_unlock_enabled_count": source_policies["handoff_unlock_enabled_count"],
            "source_provider_restore_api_called_count": source_policies["provider_restore_api_called_count"],
            "source_object_body_read_count": source_policies["object_body_read_count"],
            "source_export_enabled_count": source_policies["export_enabled_count"],
            "source_execution_enabled_count": source_policies["execution_enabled_count"],
            "source_vault_done_count": source_policies["vault_done_count"],
        },
        "blocker_snapshot_receipt": {
            "source_blocker_count": source_blockers["blocker_count"],
            "source_blocks_restore_unlock_count": source_blockers["blocks_restore_unlock_count"],
            "source_blocks_provider_restore_api_count": source_blockers["blocks_provider_restore_api_count"],
            "source_blocks_object_body_access_count": source_blockers["blocks_object_body_access_count"],
            "source_blocks_export_count": source_blockers["blocks_export_count"],
            "source_blocks_direct_upload_count": source_blockers["blocks_direct_upload_count"],
            "source_blocks_execution_count": source_blockers["blocks_execution_count"],
            "source_blocks_vault_done_count": source_blockers["blocks_vault_done_count"],
            "source_resolved_count": source_blockers["resolved_count"],
        },
        "event_snapshot_receipt": {
            "source_event_count": source_events["event_count"],
            "source_requirement_count": source_requirements["requirement_count"],
            "source_validation_passed": source_status["validation_passed"],
        },
        "next_pack_receipt": {
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp093": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    }

    receipts = []
    for code, name, category in RECEIPT_SPECS:
        receipt_payload = payloads[code]
        receipts.append(
            {
                "receipt_code": code,
                "receipt_name": name,
                "receipt_category": category,
                "receipt_payload": receipt_payload,
                "receipt_hash": _hash_payload(receipt_payload),
            }
        )
    return receipts

def initialize_real_provider_post_closeout_handoff_receipt_ledger(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_post_closeout_handoff_receipt_ledger_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            """
            SELECT receipt_ledger_id
            FROM vault_post_closeout_handoff_receipt_ledgers
            WHERE receipt_ledger_id = ?
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID,),
        ).fetchone()

        if exists is None:
            source_status = get_gp091_status()["gp091_status"]
            source_contract = get_post_closeout_handoff_lock_contract_record()["handoff_lock_contract"]
            receipts = _build_receipt_payloads(source_status, source_contract)
            ledger_payload_for_hash = {
                "schema_version": SCHEMA_VERSION,
                "pack_id": PACK_ID,
                "source_handoff_lock_contract_id": source_contract["handoff_lock_contract_id"],
                "source_gp090_readiness_hash": source_contract["source_gp090_readiness_hash"],
                "source_gp090_readiness_score": source_contract["source_gp090_readiness_score"],
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "receipt_hashes": [item["receipt_hash"] for item in receipts],
                "policies": [code for code, _name, _category in RECEIPT_POLICIES],
                "receipt_ledger_locked": True,
                "safe_to_continue_to_gp093": True,
                "vault_done": False,
            }
            ledger_hash = _hash_payload(ledger_payload_for_hash)
            now = _now_iso()

            ledger_data = {
                **ledger_payload_for_hash,
                "ledger_hash": ledger_hash,
                "receipt_count": len(receipts),
                "policy_count": len(RECEIPT_POLICIES),
                "blocker_count": 8,
                "next_pack": NEXT_PACK,
                "next_pack_title": NEXT_PACK_TITLE,
            }

            ledger_row = {
                "receipt_ledger_id": DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID,
                "pack_id": PACK_ID,
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_handoff_lock_contract_id": source_contract["handoff_lock_contract_id"],
                "source_gp090_readiness_hash": source_contract["source_gp090_readiness_hash"],
                "source_gp090_readiness_score": source_contract["source_gp090_readiness_score"],
                "receipt_count": len(receipts),
                "policy_count": len(RECEIPT_POLICIES),
                "blocker_count": 8,
                "event_count": 6,
                "ledger_hash": ledger_hash,
                "ledger_status": "REAL_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_OPEN_LOCKED_TEMPLATE_ONLY",
                "ledger_data_json": _json_dumps(ledger_data),
                "created_at": now,
                "updated_at": now,
            }
            for field in TRUE_LEDGER_FIELDS:
                ledger_row[field] = 1
            for field in FALSE_FIELDS:
                ledger_row[field] = 0
            _insert_dict(conn, "vault_post_closeout_handoff_receipt_ledgers", ledger_row)

            receipt_false_fields = [
                "receipt_unlock_configured",
                "receipt_unlock_attempted",
                "receipt_unlock_enabled",
                "receipt_approval_granted",
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

            for receipt in receipts:
                row = {
                    "receipt_id": f"VPPCHR-{receipt['receipt_code'].upper().replace('_', '-')}",
                    "receipt_ledger_id": DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID,
                    "receipt_code": receipt["receipt_code"],
                    "receipt_name": receipt["receipt_name"],
                    "receipt_category": receipt["receipt_category"],
                    "receipt_payload_json": _json_dumps(receipt["receipt_payload"]),
                    "receipt_hash": receipt["receipt_hash"],
                    "receipt_status": "REAL_POST_CLOSEOUT_HANDOFF_RECEIPT_RECORDED_LOCKED",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_RECEIPT_FIELDS:
                    row[field] = 1
                for field in receipt_false_fields:
                    row[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_receipts", row)

            policy_false_fields = [
                "policy_verified",
                "receipt_unlock_configured",
                "receipt_unlock_enabled",
                "receipt_approval_granted",
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

            for code, name, category in RECEIPT_POLICIES:
                row = {
                    "receipt_policy_id": f"VPPCHRLP-{code.upper().replace('_', '-')}",
                    "receipt_ledger_id": DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID,
                    "policy_code": code,
                    "policy_name": name,
                    "policy_category": category,
                    "policy_message": f"{name}; GP092 records receipts only and cannot unlock restore/API/body/export/upload/execution/Vault-done surfaces.",
                    "policy_status": "REAL_POST_CLOSEOUT_HANDOFF_RECEIPT_POLICY_RECORDED_LOCKED",
                    "policy_required": 1,
                    "tower_review_required": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in policy_false_fields:
                    row[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_receipt_policies", row)

            blocker_specs = [
                ("block_receipt_unlock", "Blocks receipt-ledger unlock", "receipt_unlock", "critical"),
                ("block_restore_unlock", "Blocks restore unlock from receipt ledger", "restore", "critical"),
                ("block_provider_restore_api", "Blocks provider restore API from receipt ledger", "provider_api", "critical"),
                ("block_object_body_access", "Blocks object body access from receipt ledger", "object_body", "critical"),
                ("block_export", "Blocks export from receipt ledger", "export", "critical"),
                ("block_direct_upload", "Blocks direct upload from receipt ledger", "direct_upload", "critical"),
                ("block_execution", "Blocks execution from receipt ledger", "execution", "critical"),
                ("block_vault_done", "Blocks Vault done from receipt ledger", "vault_done", "critical"),
            ]
            for code, name, category, severity in blocker_specs:
                row = {
                    "receipt_blocker_id": f"VPPCHRLB-{code.upper().replace('_', '-')}",
                    "receipt_ledger_id": DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "REAL_POST_CLOSEOUT_HANDOFF_RECEIPT_BLOCKER_ACTIVE",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_BLOCKER_FIELDS:
                    row[field] = 1
                for field in ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]:
                    row[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_receipt_blockers", row)

            for event_type, event_payload in [
                ("REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_CREATED", ledger_data),
                ("SOURCE_GP091_HANDOFF_CONTRACT_ATTACHED", {
                    "source_handoff_lock_contract_id": source_contract["handoff_lock_contract_id"],
                    "source_validation_passed": source_status["validation_passed"],
                    "source_safe_to_continue_to_gp092": source_status["safe_to_continue_to_gp092"],
                }),
                ("SOURCE_GP090_READINESS_HASH_CARRIED_FORWARD", {
                    "source_gp090_readiness_hash": source_contract["source_gp090_readiness_hash"],
                    "source_gp090_readiness_score": source_contract["source_gp090_readiness_score"],
                }),
                ("POST_CLOSEOUT_HANDOFF_RECEIPTS_RECORDED", {"receipt_count": len(receipts)}),
                ("POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_HASH_RECORDED", {"ledger_hash": ledger_hash}),
                ("POST_CLOSEOUT_HANDOFF_RECEIPT_LOCKS_CONFIRMED", {
                    "receipt_unlock_enabled": False,
                    "provider_restore_api_called": False,
                    "object_body_read": False,
                    "export_package_created": False,
                    "direct_upload_enabled": False,
                    "execution_enabled": False,
                    "vault_done": False,
                }),
            ]:
                _insert_event(conn, DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _sum_counts(table: str, ledger_id: str, fields: list[str], db_path: Optional[str] = None) -> Dict[str, int]:
    selects = ["COUNT(*) AS total_count"]
    for field in fields:
        selects.append(f"SUM(CASE WHEN {field} = 1 THEN 1 ELSE 0 END) AS {field}_count")
    with _connect(db_path) as conn:
        row = conn.execute(
            f"SELECT {', '.join(selects)} FROM {table} WHERE receipt_ledger_id = ?",
            (ledger_id,),
        ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}

def get_post_closeout_handoff_receipt_ledger_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_receipt_ledger(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_receipt_ledgers
            WHERE receipt_ledger_id = ?
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID,),
        ).fetchone()
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "receipt_ledger": _boolify(row, {"ledger_data_json": "ledger_data"}),
    }

def get_post_closeout_handoff_receipts(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_receipt_ledger(db_path)
    fields = [
        "receipt_required",
        "receipt_recorded",
        "receipt_hash_recorded",
        "receipt_locked",
        "template_only",
        "tower_review_required",
        "receipt_unlock_configured",
        "receipt_unlock_attempted",
        "receipt_unlock_enabled",
        "receipt_approval_granted",
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
    counts = _sum_counts("vault_post_closeout_handoff_receipts", DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_receipts
            WHERE receipt_ledger_id = ?
            ORDER BY receipt_category, receipt_code
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID,),
        ).fetchall()
    receipts = [_boolify(row, {"receipt_payload_json": "receipt_payload"}) for row in rows]
    counts["receipt_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "receipts": receipts}

def get_post_closeout_handoff_receipt_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_receipt_ledger(db_path)
    fields = [
        "policy_required",
        "policy_verified",
        "tower_review_required",
        "receipt_unlock_configured",
        "receipt_unlock_enabled",
        "receipt_approval_granted",
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
    counts = _sum_counts("vault_post_closeout_handoff_receipt_policies", DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_receipt_policies
            WHERE receipt_ledger_id = ?
            ORDER BY policy_category, policy_code
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID,),
        ).fetchall()
    counts["policy_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "policies": [_boolify(row) for row in rows]}

def get_post_closeout_handoff_receipt_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_receipt_ledger(db_path)
    fields = TRUE_BLOCKER_FIELDS + ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]
    counts = _sum_counts("vault_post_closeout_handoff_receipt_blockers", DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_receipt_blockers
            WHERE receipt_ledger_id = ?
            ORDER BY blocker_category, blocker_code
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID,),
        ).fetchall()
    counts["blocker_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "blockers": [_boolify(row) for row in rows]}

def get_post_closeout_handoff_receipt_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_receipt_ledger(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_post_closeout_handoff_receipt_events
            WHERE receipt_ledger_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID,),
        ).fetchall()
    events = [
        {
            "event_id": row["event_id"],
            "receipt_ledger_id": row["receipt_ledger_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def record_post_closeout_handoff_receipt_event(event_type: str, event_payload: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_post_closeout_handoff_receipt_ledger(db_path)
    payload = dict(event_payload or {})
    payload.update({
        "write_type": "REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_EVENT",
        "receipt_ledger_locked": True,
        "receipt_unlock_enabled": False,
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
        event_id = _insert_event(conn, DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID, event_type, payload)
        conn.commit()
    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "receipt_ledger_id": DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID,
        "real_sqlite_backed": True,
        **payload,
    }

def validate_post_closeout_handoff_receipt_ledger(db_path: Optional[str] = None) -> Dict[str, Any]:
    ledger = get_post_closeout_handoff_receipt_ledger_record(db_path)["receipt_ledger"]
    receipts = get_post_closeout_handoff_receipts(db_path)
    policies = get_post_closeout_handoff_receipt_policies(db_path)
    blockers = get_post_closeout_handoff_receipt_blockers(db_path)
    events = get_post_closeout_handoff_receipt_events(db_path)

    false_checks = [(f"NO_LEDGER_{field.upper()}", ledger[field] is False) for field in FALSE_FIELDS]

    receipt_order = {code: idx for idx, (code, _name, _category) in enumerate(RECEIPT_SPECS)}
    ordered_receipts = sorted(
        receipts["receipts"],
        key=lambda item: receipt_order.get(item["receipt_code"], 9999),
    )

    recomputed_ledger_hash = _hash_payload({
        "schema_version": SCHEMA_VERSION,
        "pack_id": PACK_ID,
        "source_handoff_lock_contract_id": ledger["source_handoff_lock_contract_id"],
        "source_gp090_readiness_hash": ledger["source_gp090_readiness_hash"],
        "source_gp090_readiness_score": ledger["source_gp090_readiness_score"],
        "section_id": SECTION_ID,
        "section_range": SECTION_RANGE,
        "receipt_hashes": [item["receipt_hash"] for item in ordered_receipts],
        "policies": [code for code, _name, _category in RECEIPT_POLICIES],
        "receipt_ledger_locked": True,
        "safe_to_continue_to_gp093": True,
        "vault_done": False,
    })

    receipt_hash_checks = []
    for item in receipts["receipts"]:
        receipt_hash_checks.append(
            item["receipt_hash"] == _hash_payload(item["receipt_payload"])
        )

    checks = [
        ("REAL_SQLITE_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_EXISTS", ledger["receipt_ledger_id"] == DEFAULT_POST_CLOSEOUT_HANDOFF_RECEIPT_LEDGER_ID),
        ("SOURCE_GP091_HANDOFF_CONTRACT_ATTACHED", ledger["source_handoff_lock_contract_id"] == DEFAULT_POST_CLOSEOUT_HANDOFF_LOCK_CONTRACT_ID),
        ("SOURCE_GP090_READINESS_HASH_ATTACHED", isinstance(ledger["source_gp090_readiness_hash"], str) and len(ledger["source_gp090_readiness_hash"]) == 64),
        ("SOURCE_GP090_READINESS_SCORE_100", ledger["source_gp090_readiness_score"] == 100),
        ("SECTION_GP091_GP100", ledger["section_id"] == SECTION_ID and ledger["section_range"] == SECTION_RANGE),
        ("RECEIPT_LEDGER_READY", ledger["post_closeout_handoff_receipt_ledger_ready"] is True),
        ("RECEIPT_ROWS_READY", ledger["receipt_rows_ready"] is True),
        ("RECEIPT_HASHES_READY", ledger["receipt_hashes_ready"] is True),
        ("LEDGER_HASH_READY", ledger["ledger_hash_ready"] is True),
        ("LEDGER_HASH_MATCHES", ledger["ledger_hash"] == recomputed_ledger_hash),
        ("ALL_RECEIPT_HASHES_MATCH", all(receipt_hash_checks)),
        ("RECEIPT_COUNT_MATCHES", receipts["receipt_count"] == len(RECEIPT_SPECS)),
        ("ALL_RECEIPTS_RECORDED", receipts["receipt_recorded_count"] == len(RECEIPT_SPECS)),
        ("ALL_RECEIPTS_LOCKED", receipts["receipt_locked_count"] == len(RECEIPT_SPECS)),
        ("ALL_RECEIPTS_HASHED", receipts["receipt_hash_recorded_count"] == len(RECEIPT_SPECS)),
        ("NO_RECEIPT_UNLOCK", receipts["receipt_unlock_enabled_count"] == 0),
        ("NO_RECEIPT_PROVIDER_API", receipts["provider_restore_api_called_count"] == 0),
        ("NO_RECEIPT_OBJECT_BODY", receipts["object_body_read_count"] == 0),
        ("NO_RECEIPT_EXPORT", receipts["export_enabled_count"] == 0),
        ("NO_RECEIPT_DIRECT_UPLOAD", receipts["direct_upload_enabled_count"] == 0),
        ("NO_RECEIPT_EXECUTION", receipts["execution_enabled_count"] == 0),
        ("NO_RECEIPT_VAULT_DONE", receipts["vault_done_count"] == 0),
        ("POLICIES_EXIST", policies["policy_count"] == len(RECEIPT_POLICIES)),
        ("NO_POLICY_RECEIPT_UNLOCK", policies["receipt_unlock_enabled_count"] == 0),
        ("NO_POLICY_PROVIDER_API", policies["provider_restore_api_called_count"] == 0),
        ("NO_POLICY_OBJECT_BODY", policies["object_body_read_count"] == 0),
        ("NO_POLICY_EXPORT", policies["export_enabled_count"] == 0),
        ("NO_POLICY_DIRECT_UPLOAD", policies["direct_upload_enabled_count"] == 0),
        ("NO_POLICY_EXECUTION", policies["execution_enabled_count"] == 0),
        ("NO_POLICY_VAULT_DONE", policies["vault_done_count"] == 0),
        ("BLOCKERS_EXIST", blockers["blocker_count"] == 8),
        ("ALL_BLOCKERS_ACTIVE", blockers["blocker_active_count"] == 8),
        ("ALL_BLOCKERS_BLOCK_RECEIPT_UNLOCK", blockers["blocks_receipt_unlock_count"] == 8),
        ("ALL_BLOCKERS_BLOCK_RESTORE", blockers["blocks_restore_unlock_count"] == 8),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", blockers["blocks_provider_restore_api_count"] == 8),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY", blockers["blocks_object_body_access_count"] == 8),
        ("ALL_BLOCKERS_BLOCK_EXPORT", blockers["blocks_export_count"] == 8),
        ("ALL_BLOCKERS_BLOCK_DIRECT_UPLOAD", blockers["blocks_direct_upload_count"] == 8),
        ("ALL_BLOCKERS_BLOCK_EXECUTION", blockers["blocks_execution_count"] == 8),
        ("ALL_BLOCKERS_BLOCK_VAULT_DONE", blockers["blocks_vault_done_count"] == 8),
        ("NO_BLOCKERS_RESOLVED", blockers["resolved_count"] == 0),
        ("EVENT_LOG_EXISTS", events["event_count"] >= 6),
        ("SAFE_TO_CONTINUE_TO_GP093", ledger["safe_to_continue_to_gp093"] is True),
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
        "ledger_hash": ledger["ledger_hash"],
        "real_sqlite_backed": True,
        "safe_to_continue_to_gp093": len(failed) == 0,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_post_closeout_handoff_receipt_next_step() -> Dict[str, Any]:
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
            "safe_to_continue_to_gp093": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP092 records the post-closeout handoff receipt ledger. Continue to GP093 owner review queue while restore, provider API, object body access, export, direct upload, execution, and Vault done remain locked.",
            "carry_forward_rules": [
                "Carry GP091 handoff contract forward.",
                "Carry GP090 readiness hash forward.",
                "Keep all receipts hash-backed and immutable by policy.",
                "Keep restore request submission locked.",
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
        "depends_on": ["VAULT_GP091"],
        "foundation_status": "post_closeout_handoff_receipt_ledger_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_provider_post_closeout_handoff_receipt_ledger",
        "previous_section": PREVIOUS_SECTION_ID,
        "previous_section_range": PREVIOUS_SECTION_RANGE,
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-provider-post-closeout-handoff-receipt-ledger",
        "json_route": "/vault/real-provider-post-closeout-handoff-receipt-ledger.json",
        "record_route": "/vault/post-closeout-handoff-receipt-ledger-record.json",
        "receipts_route": "/vault/post-closeout-handoff-receipts.json",
        "policies_route": "/vault/post-closeout-handoff-receipt-policies.json",
        "blockers_route": "/vault/post-closeout-handoff-receipt-blockers.json",
        "events_route": "/vault/post-closeout-handoff-receipt-events.json",
        "validation_route": "/vault/post-closeout-handoff-receipt-validation.json",
        "next_step_route": "/vault/post-closeout-handoff-receipt-next-step.json",
        "gp092_status_route": "/vault/gp092-status.json",
    }

def get_real_provider_post_closeout_handoff_receipt_ledger_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_real_provider_post_closeout_handoff_receipt_ledger(db_path)
    ledger = get_post_closeout_handoff_receipt_ledger_record(db_path)["receipt_ledger"]
    receipts = get_post_closeout_handoff_receipts(db_path)
    policies = get_post_closeout_handoff_receipt_policies(db_path)
    blockers = get_post_closeout_handoff_receipt_blockers(db_path)
    events = get_post_closeout_handoff_receipt_events(db_path)
    validation = validate_post_closeout_handoff_receipt_ledger(db_path)

    truth = {
        "real_provider_post_closeout_handoff_receipt_ledger_ready": True,
        "real_sqlite_backed": True,
        "source_gp091_handoff_contract_attached": ledger["source_gp091_handoff_contract_attached"],
        "source_gp090_readiness_hash": ledger["source_gp090_readiness_hash"],
        "source_gp090_readiness_score": ledger["source_gp090_readiness_score"],
        "receipt_count": receipts["receipt_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "event_count": events["event_count"],
        "ledger_hash": ledger["ledger_hash"],
        "receipt_ledger_locked": ledger["receipt_ledger_locked"],
        "receipt_ledger_template_only": ledger["receipt_ledger_template_only"],
        "receipt_unlock_enabled": ledger["receipt_unlock_enabled"],
        "restore_request_submitted": ledger["restore_request_submitted"],
        "provider_restore_api_called": ledger["provider_restore_api_called"],
        "object_body_read": ledger["object_body_read"],
        "export_package_created": ledger["export_package_created"],
        "direct_upload_enabled": ledger["direct_upload_enabled"],
        "export_enabled": ledger["export_enabled"],
        "execution_enabled": ledger["execution_enabled"],
        "safe_to_continue_to_gp093": validation["safe_to_continue_to_gp093"],
        "vault_done": ledger["vault_done"],
        "clouds_should_continue": ledger["clouds_should_continue"],
    }

    return {
        "pack": _pack_payload(),
        "receipt_ledger_truth": truth,
        "store": store,
        "receipt_ledger": ledger,
        "receipts": receipts,
        "policies": policies,
        "blockers": blockers,
        "events": events,
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_post_closeout_handoff_receipt_next_step()["next_step"],
    }

def get_gp092_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_provider_post_closeout_handoff_receipt_ledger_home(db_path)
    ledger = home["receipt_ledger"]
    receipts = home["receipts"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp092_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_provider_post_closeout_handoff_receipt_ledger_ready": True,
            "real_sqlite_backed": True,
            "real_ledger_count": home["store"]["ledger_count"],
            "real_receipt_count": home["store"]["receipt_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp091_handoff_contract_attached": ledger["source_gp091_handoff_contract_attached"],
            "source_handoff_lock_contract_id": ledger["source_handoff_lock_contract_id"],
            "source_gp090_readiness_hash": ledger["source_gp090_readiness_hash"],
            "source_gp090_readiness_score": ledger["source_gp090_readiness_score"],
            "receipt_rows_ready": ledger["receipt_rows_ready"],
            "receipt_hashes_ready": ledger["receipt_hashes_ready"],
            "ledger_hash_ready": ledger["ledger_hash_ready"],
            "ledger_hash": ledger["ledger_hash"],
            "receipt_policies_ready": ledger["receipt_policies_ready"],
            "receipt_blockers_ready": ledger["receipt_blockers_ready"],
            "receipt_validation_ready": ledger["receipt_validation_ready"],
            "receipt_ledger_locked": ledger["receipt_ledger_locked"],
            "receipt_ledger_template_only": ledger["receipt_ledger_template_only"],
            "receipt_count": receipts["receipt_count"],
            "policy_count": policies["policy_count"],
            "blocker_count": blockers["blocker_count"],
            "receipt_unlock_enabled_count": receipts["receipt_unlock_enabled_count"] + policies["receipt_unlock_enabled_count"],
            "provider_restore_api_called_count": receipts["provider_restore_api_called_count"] + policies["provider_restore_api_called_count"],
            "object_body_read_count": receipts["object_body_read_count"] + policies["object_body_read_count"],
            "export_enabled_count": receipts["export_enabled_count"] + policies["export_enabled_count"],
            "direct_upload_enabled_count": receipts["direct_upload_enabled_count"] + policies["direct_upload_enabled_count"],
            "execution_enabled_count": receipts["execution_enabled_count"] + policies["execution_enabled_count"],
            "vault_done_count": receipts["vault_done_count"] + policies["vault_done_count"],
            "blocks_receipt_unlock_count": blockers["blocks_receipt_unlock_count"],
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
            "safe_to_continue_to_gp093": validation["safe_to_continue_to_gp093"],
            "foundation_status": "post_closeout_handoff_receipt_ledger_ready_safe_to_continue_not_done",
            "receipt_unlock_enabled": ledger["receipt_unlock_enabled"],
            "provider_restore_api_called": ledger["provider_restore_api_called"],
            "object_body_read": ledger["object_body_read"],
            "export_package_created": ledger["export_package_created"],
            "direct_upload_enabled": ledger["direct_upload_enabled"],
            "export_enabled": ledger["export_enabled"],
            "execution_enabled": ledger["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp092",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "receipt_ledger_truth": home["receipt_ledger_truth"],
        "routes": home["routes"],
        "receipt_ledger": ledger,
        "receipts": receipts,
        "policies": policies,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }

def render_real_provider_post_closeout_handoff_receipt_ledger_page() -> str:
    home = get_real_provider_post_closeout_handoff_receipt_ledger_home()
    truth = home["receipt_ledger_truth"]
    routes = home["routes"]
    next_step = home["next_step"]

    receipt_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['receipt_code'])}</strong>
          <span>{escape(item['receipt_name'])}</span>
          <code>{escape(item['receipt_hash'][:16])}</code>
        </article>
        """
        for item in home["receipts"]["receipts"]
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
<title>Vault Post-Closeout Handoff Receipt Ledger · GP092</title>
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
    <div class="eyebrow">Archive Vault · Giant Pack 092</div>
    <div class="eyebrow">Post-Closeout Handoff Governance Layer · GP091-GP100</div>
    <h1>Real Provider Post-Closeout Handoff Receipt Ledger</h1>
    <p>GP092 records a hash-backed receipt ledger for the GP091 handoff. It preserves the GP090 readiness hash and keeps restore, provider APIs, object body access, export, direct upload, execution, and Vault done locked.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['receipt_count']}</strong><span>receipts</span></div>
      <div class="metric"><strong>{truth['policy_count']}</strong><span>policies</span></div>
      <div class="metric"><strong>{truth['blocker_count']}</strong><span>lock blockers</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">Ledger hash recorded</span>
      <span class="pill ok">Receipt hashes recorded</span>
      <span class="pill ok">GP090 hash carried</span>
      <span class="pill danger">No provider API</span>
      <span class="pill danger">No body read</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Receipt Ledger Rows</h2>
    <div class="cards">{receipt_cards}</div>
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
    <h2>GP092 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['receipts_route'])}</code>
      <code>{escape(routes['policies_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_step_route'])}</code>
      <code>{escape(routes['gp092_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
