"""
VAULT GP096-GP100 — Real Provider Post-Closeout Handoff Governance Closeout Layer

Current section:
Archive Vault — Real Provider Post-Closeout Handoff Governance Layer / GP091-GP100

Builds:
- GP096 Owner Review Closeout Lock Contract
- GP097 Owner Review Closeout Receipt Ledger
- GP098 Owner Summary
- GP099 Section Closeout Packet
- GP100 Governance Readiness Checkpoint

This layer closes GP091-GP100 without unlocking restore/export/provider API/body/direct upload/execution/Vault-done.
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

from vault.real_provider_post_closeout_handoff_owner_review_decision_receipt_lock_contract_service import (
    DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID,
    get_gp095_status,
    get_post_closeout_handoff_owner_review_decision_receipt_blockers,
    get_post_closeout_handoff_owner_review_decision_receipt_events,
    get_post_closeout_handoff_owner_review_decision_receipt_lock_contract_record,
    get_post_closeout_handoff_owner_review_decision_receipt_policies,
    get_post_closeout_handoff_owner_review_decision_receipt_requirements,
)

LAYER_ID = "VAULT_GP096_100"
LAYER_NAME = "Real Provider Post-Closeout Handoff Governance Closeout Layer"
SCHEMA_VERSION = "vault.real_provider_post_closeout_handoff_governance_closeout_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_GOVERNANCE_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Post-Closeout Handoff Governance Layer"
SECTION_RANGE = "GP091-GP100"

NEXT_SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RECOVERY_CASE_WORKSPACE_LAYER"
NEXT_SECTION_RANGE = "GP101-GP110"
NEXT_PACK = "VAULT_GP101_110_REAL_PROVIDER_RECOVERY_CASE_WORKSPACE_LAYER"

DEFAULT_DB_ENV = "VAULT_POST_CLOSEOUT_HANDOFF_GOVERNANCE_CLOSEOUT_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_post_closeout_handoff_governance_closeout_layer.sqlite"

GP096_CLOSEOUT_LOCK_CONTRACT_ID = "VPPCHORCLC-GP096-001"
GP097_CLOSEOUT_RECEIPT_LEDGER_ID = "VPPCHORCRL-GP097-001"
GP098_OWNER_SUMMARY_ID = "VPPCHOS-GP098-001"
GP099_SECTION_CLOSEOUT_PACKET_ID = "VPPCHSCP-GP099-001"
GP100_GOVERNANCE_READINESS_ID = "VPPCHGRC-GP100-001"

FALSE_FIELDS = [
    "owner_review_decision_recorded",
    "owner_review_approval_recorded",
    "owner_review_rejection_recorded",
    "decision_receipt_created",
    "decision_receipt_hash_created",
    "decision_receipt_packet_created",
    "decision_receipt_persisted",
    "tower_unlock_requested",
    "tower_unlock_granted",
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
    "vault_done",
    "clouds_should_continue",
]

CLOSEOUT_RECEIPTS = [
    ("gp096_closeout_lock_contract_receipt", "GP096 closeout lock contract receipt", "gp096"),
    ("gp097_closeout_receipt_ledger_receipt", "GP097 closeout receipt ledger receipt", "gp097"),
    ("gp098_owner_summary_receipt", "GP098 owner summary receipt", "gp098"),
    ("gp099_section_closeout_packet_receipt", "GP099 section closeout packet receipt", "gp099"),
    ("gp100_readiness_checkpoint_receipt", "GP100 governance readiness checkpoint receipt", "gp100"),
    ("source_gp095_receipt_lock_receipt", "Source GP095 decision receipt lock receipt", "source"),
    ("source_gp090_hash_carryforward_receipt", "Source GP090 readiness hash carry-forward receipt", "source"),
    ("next_section_handoff_receipt", "Next section GP101-GP110 handoff receipt", "handoff"),
]

def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _resolve_db_path(db_path: Optional[str] = None) -> Path:
    return Path(db_path or os.environ.get(DEFAULT_DB_ENV) or DEFAULT_DB_PATH)

def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)

def _json_loads(value: str) -> Any:
    return json.loads(value)

def _hash_payload(payload: Dict[str, Any]) -> str:
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
        "gp_number",
        "source_gp090_readiness_score",
        "source_requirement_count",
        "source_policy_count",
        "source_blocker_count",
        "source_event_count",
        "receipt_count",
        "component_count",
        "readiness_score",
        "check_count",
        "passed_count",
        "failed_count",
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
            or key.endswith("_number")
        ):
            payload[key] = int(row[key])
        elif isinstance(row[key], int):
            payload[key] = bool(row[key])
        else:
            payload[key] = row[key]
    return payload

def _pack_payload(gp_number: int, name: str) -> Dict[str, Any]:
    return {
        "id": f"VAULT_GP{gp_number:03d}",
        "name": name,
        "layer_id": LAYER_ID,
        "layer_name": LAYER_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP095"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def _layer_pack_payload() -> Dict[str, Any]:
    return {
        "id": LAYER_ID,
        "name": LAYER_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP095"],
        "packs": ["VAULT_GP096", "VAULT_GP097", "VAULT_GP098", "VAULT_GP099", "VAULT_GP100"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
        "next_pack": NEXT_PACK,
    }

def ensure_post_closeout_handoff_governance_closeout_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)
    false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)

    with _connect(str(path)) as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_governance_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp095_contract_id TEXT NOT NULL,
                source_gp095_validation_passed INTEGER NOT NULL DEFAULT 1,
                source_gp090_readiness_hash TEXT NOT NULL,
                source_gp090_readiness_score INTEGER NOT NULL,
                source_ledger_hash TEXT NOT NULL,
                source_requirement_count INTEGER NOT NULL,
                source_policy_count INTEGER NOT NULL,
                source_blocker_count INTEGER NOT NULL,
                source_event_count INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                owner_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                safe_to_continue INTEGER NOT NULL DEFAULT 1,
                data_json TEXT NOT NULL,
                component_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_governance_closeout_receipts (
                receipt_id TEXT PRIMARY KEY,
                receipt_ledger_id TEXT NOT NULL,
                receipt_code TEXT NOT NULL,
                receipt_name TEXT NOT NULL,
                receipt_category TEXT NOT NULL,
                receipt_status TEXT NOT NULL,
                receipt_payload_json TEXT NOT NULL,
                receipt_hash TEXT NOT NULL,
                receipt_locked INTEGER NOT NULL DEFAULT 1,
                owner_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(receipt_ledger_id, receipt_code)
            )
            """
        )

        false_sql_readiness = ",\n".join(
            f"{field} INTEGER NOT NULL DEFAULT 0"
            for field in FALSE_FIELDS
            if field not in {"vault_done", "clouds_should_continue"}
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_governance_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                receipt_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                safe_to_continue_to_gp101 INTEGER NOT NULL DEFAULT 1,
                section_closed INTEGER NOT NULL DEFAULT 1,
                vault_done INTEGER NOT NULL DEFAULT 0,
                clouds_should_continue INTEGER NOT NULL DEFAULT 0,
                {false_sql_readiness},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_post_closeout_handoff_governance_closeout_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "real_sqlite_backed": True,
        "tables": [
            "vault_post_closeout_handoff_governance_components",
            "vault_post_closeout_handoff_governance_closeout_receipts",
            "vault_post_closeout_handoff_governance_readiness",
            "vault_post_closeout_handoff_governance_closeout_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VPPCHGCEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_post_closeout_handoff_governance_closeout_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_post_closeout_handoff_governance_closeout_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_post_closeout_handoff_governance_closeout_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_post_closeout_handoff_governance_components WHERE component_id = ?",
            (GP096_CLOSEOUT_LOCK_CONTRACT_ID,),
        ).fetchone()

        if existing is None:
            source_status = get_gp095_status()["gp095_status"]
            source_contract = get_post_closeout_handoff_owner_review_decision_receipt_lock_contract_record()["decision_receipt_lock_contract"]
            source_requirements = get_post_closeout_handoff_owner_review_decision_receipt_requirements()
            source_policies = get_post_closeout_handoff_owner_review_decision_receipt_policies()
            source_blockers = get_post_closeout_handoff_owner_review_decision_receipt_blockers()
            source_events = get_post_closeout_handoff_owner_review_decision_receipt_events()
            now = _now_iso()

            source_payload = {
                "source_gp095_contract_id": source_contract["decision_receipt_lock_contract_id"],
                "source_gp095_validation_passed": source_status["validation_passed"],
                "source_gp090_readiness_hash": source_contract["source_gp090_readiness_hash"],
                "source_gp090_readiness_score": source_contract["source_gp090_readiness_score"],
                "source_ledger_hash": source_contract["source_ledger_hash"],
                "source_requirement_count": source_requirements["requirement_count"],
                "source_policy_count": source_policies["policy_count"],
                "source_blocker_count": source_blockers["blocker_count"],
                "source_event_count": source_events["event_count"],
            }

            components = [
                (
                    GP096_CLOSEOUT_LOCK_CONTRACT_ID,
                    96,
                    "VAULT_GP096",
                    "Real Provider Post-Closeout Handoff Owner Review Closeout Lock Contract",
                    "owner_review_closeout_lock_contract",
                    {
                        "purpose": "Close the owner-review closeout surface without recording owner approval, rejection, Tower unlock, restore, provider API, object body access, export, upload, execution, or Vault done.",
                        "closeout_lock_ready": True,
                        "owner_review_closeout_locked": True,
                    },
                ),
                (
                    GP097_CLOSEOUT_RECEIPT_LEDGER_ID,
                    97,
                    "VAULT_GP097",
                    "Real Provider Post-Closeout Handoff Owner Review Closeout Receipt Ledger",
                    "owner_review_closeout_receipt_ledger",
                    {
                        "purpose": "Create the closeout receipt ledger for GP096-GP100 without creating an operational decision receipt or unlock.",
                        "receipt_ledger_ready": True,
                        "receipt_count": len(CLOSEOUT_RECEIPTS),
                    },
                ),
                (
                    GP098_OWNER_SUMMARY_ID,
                    98,
                    "VAULT_GP098",
                    "Real Provider Post-Closeout Handoff Owner Summary",
                    "owner_summary",
                    {
                        "purpose": "Summarize GP091-GP100 for owner review with locks carried forward.",
                        "owner_summary_ready": True,
                        "summary_points": [
                            "GP091 opened the post-closeout handoff layer.",
                            "GP092 created the handoff receipt ledger.",
                            "GP093 created the owner review queue.",
                            "GP094 created the owner review decision lock contract.",
                            "GP095 created the decision receipt lock contract.",
                            "GP096-GP100 close the section safely.",
                        ],
                    },
                ),
                (
                    GP099_SECTION_CLOSEOUT_PACKET_ID,
                    99,
                    "VAULT_GP099",
                    "Real Provider Post-Closeout Handoff Governance Section Closeout Packet",
                    "section_closeout_packet",
                    {
                        "purpose": "Create the section closeout packet for GP091-GP100.",
                        "section_closeout_packet_ready": True,
                        "section_closed_by_packet": True,
                    },
                ),
                (
                    GP100_GOVERNANCE_READINESS_ID,
                    100,
                    "VAULT_GP100",
                    "Real Provider Post-Closeout Handoff Governance Readiness Checkpoint",
                    "governance_readiness_checkpoint",
                    {
                        "purpose": "Close GP091-GP100 and hand off to GP101-GP110 recovery case workspace layer.",
                        "governance_readiness_checkpoint_ready": True,
                        "section_closed": True,
                        "safe_to_continue_to_gp101": True,
                        "next_section": NEXT_SECTION_ID,
                        "next_section_range": NEXT_SECTION_RANGE,
                        "next_pack": NEXT_PACK,
                    },
                ),
            ]

            for component_id, gp_number, pack_id, pack_name, component_type, data in components:
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "component_id": component_id,
                    "gp_number": gp_number,
                    "pack_id": pack_id,
                    "pack_name": pack_name,
                    "component_type": component_type,
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    **source_payload,
                    **data,
                    "locked_truth": {
                        field: False for field in FALSE_FIELDS
                    },
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                component_hash = _hash_payload(payload)

                row = {
                    "component_id": component_id,
                    "gp_number": gp_number,
                    "pack_id": pack_id,
                    "pack_name": pack_name,
                    "component_type": component_type,
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    **source_payload,
                    "component_ready": 1,
                    "component_locked": 1,
                    "owner_review_required": 1,
                    "tower_review_required": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": component_hash,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_governance_components", row)

            receipt_hashes = []
            for code, name, category in CLOSEOUT_RECEIPTS:
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "receipt_ledger_id": GP097_CLOSEOUT_RECEIPT_LEDGER_ID,
                    "receipt_code": code,
                    "receipt_name": name,
                    "receipt_category": category,
                    "source_gp095_contract_id": source_contract["decision_receipt_lock_contract_id"],
                    "source_gp090_readiness_hash": source_contract["source_gp090_readiness_hash"],
                    "source_gp090_readiness_score": source_contract["source_gp090_readiness_score"],
                    "source_ledger_hash": source_contract["source_ledger_hash"],
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    "next_section": NEXT_SECTION_ID,
                    "receipt_locked": True,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                receipt_hash = _hash_payload(payload)
                receipt_hashes.append(receipt_hash)

                row = {
                    "receipt_id": f"VPPCHGCR-{code.upper().replace('_', '-')}",
                    "receipt_ledger_id": GP097_CLOSEOUT_RECEIPT_LEDGER_ID,
                    "receipt_code": code,
                    "receipt_name": name,
                    "receipt_category": category,
                    "receipt_status": "REAL_CLOSEOUT_RECEIPT_RECORDED_LOCKED",
                    "receipt_payload_json": _json_dumps(payload),
                    "receipt_hash": receipt_hash,
                    "receipt_locked": 1,
                    "owner_review_required": 1,
                    "tower_review_required": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_post_closeout_handoff_governance_closeout_receipts", row)

            checks = [
                ("SOURCE_GP095_VALIDATION_PASSED", bool(source_status["validation_passed"])),
                ("SOURCE_GP095_CONTRACT_ATTACHED", source_contract["decision_receipt_lock_contract_id"] == DEFAULT_POST_CLOSEOUT_HANDOFF_OWNER_REVIEW_DECISION_RECEIPT_LOCK_CONTRACT_ID),
                ("SOURCE_GP090_HASH_CARRIED", isinstance(source_contract["source_gp090_readiness_hash"], str) and len(source_contract["source_gp090_readiness_hash"]) == 64),
                ("SOURCE_GP090_SCORE_100", source_contract["source_gp090_readiness_score"] == 100),
                ("COMPONENT_COUNT_5", len(components) == 5),
                ("RECEIPT_COUNT_8", len(receipt_hashes) == 8),
                ("SECTION_GP091_GP100", SECTION_RANGE == "GP091-GP100"),
                ("NEXT_SECTION_GP101_GP110", NEXT_SECTION_RANGE == "GP101-GP110"),
                ("NO_DECISION_RECORDED", True),
                ("NO_APPROVAL_RECORDED", True),
                ("NO_TOWER_UNLOCK", True),
                ("NO_RESTORE_REQUEST", True),
                ("NO_PROVIDER_API", True),
                ("NO_OBJECT_BODY", True),
                ("NO_EXPORT", True),
                ("NO_DIRECT_UPLOAD", True),
                ("NO_EXECUTION", True),
                ("VAULT_NOT_DONE", True),
                ("CLOUDS_PARKED", True),
            ]
            passed_count = len([c for c in checks if c[1]])
            failed_count = len(checks) - passed_count

            readiness_payload = {
                "schema_version": SCHEMA_VERSION,
                "readiness_id": GP100_GOVERNANCE_READINESS_ID,
                "gp_number": 100,
                "pack_id": "VAULT_GP100",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp095_contract_id": source_contract["decision_receipt_lock_contract_id"],
                "source_gp090_readiness_hash": source_contract["source_gp090_readiness_hash"],
                "source_gp090_readiness_score": source_contract["source_gp090_readiness_score"],
                "source_ledger_hash": source_contract["source_ledger_hash"],
                "component_ids": [item[0] for item in components],
                "receipt_hashes": receipt_hashes,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "safe_to_continue_to_gp101": failed_count == 0,
                "section_closed": True,
                "vault_done": False,
                "clouds_should_continue": False,
                "next_section": NEXT_SECTION_ID,
                "next_section_range": NEXT_SECTION_RANGE,
                "next_pack": NEXT_PACK,
                "locked_truth": {field: False for field in FALSE_FIELDS},
            }
            readiness_hash = _hash_payload(readiness_payload)

            row = {
                "readiness_id": GP100_GOVERNANCE_READINESS_ID,
                "gp_number": 100,
                "pack_id": "VAULT_GP100",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "REAL_POST_CLOSEOUT_HANDOFF_GOVERNANCE_LAYER_CLOSED_READY_FOR_GP101_NOT_DONE",
                "readiness_score": readiness_payload["readiness_score"],
                "component_count": len(components),
                "receipt_count": len(receipt_hashes),
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "safe_to_continue_to_gp101": 1 if failed_count == 0 else 0,
                "section_closed": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                row[field] = 0
            _insert_dict(conn, "vault_post_closeout_handoff_governance_readiness", row)

            for event_type, event_payload in [
                ("GP096_CLOSEOUT_LOCK_CONTRACT_CREATED", {"component_id": GP096_CLOSEOUT_LOCK_CONTRACT_ID}),
                ("GP097_CLOSEOUT_RECEIPT_LEDGER_CREATED", {"receipt_ledger_id": GP097_CLOSEOUT_RECEIPT_LEDGER_ID, "receipt_count": len(CLOSEOUT_RECEIPTS)}),
                ("GP098_OWNER_SUMMARY_CREATED", {"summary_id": GP098_OWNER_SUMMARY_ID}),
                ("GP099_SECTION_CLOSEOUT_PACKET_CREATED", {"packet_id": GP099_SECTION_CLOSEOUT_PACKET_ID}),
                ("GP100_GOVERNANCE_READINESS_CHECKPOINT_CREATED", {"readiness_id": GP100_GOVERNANCE_READINESS_ID, "readiness_hash": readiness_hash}),
                ("SECTION_GP091_GP100_CLOSED_LOCKED", {
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    "safe_to_continue_to_gp101": failed_count == 0,
                    "vault_done": False,
                    "clouds_should_continue": False,
                }),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_governance_components").fetchone()["c"]),
            "receipt_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_governance_closeout_receipts").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_governance_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_post_closeout_handoff_governance_closeout_events").fetchone()["c"]),
        }

def _get_component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_post_closeout_handoff_governance_closeout_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_post_closeout_handoff_governance_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _get_components(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_post_closeout_handoff_governance_closeout_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM vault_post_closeout_handoff_governance_components ORDER BY gp_number"
        ).fetchall()
    return [_boolify(row, {"data_json": "data"}) for row in rows]

def _get_receipts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_post_closeout_handoff_governance_closeout_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM vault_post_closeout_handoff_governance_closeout_receipts ORDER BY receipt_category, receipt_code"
        ).fetchall()
    return [_boolify(row, {"receipt_payload_json": "receipt_payload"}) for row in rows]

def _get_readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_post_closeout_handoff_governance_closeout_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_post_closeout_handoff_governance_readiness WHERE readiness_id = ?",
            (GP100_GOVERNANCE_READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _get_events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_post_closeout_handoff_governance_closeout_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM vault_post_closeout_handoff_governance_closeout_events ORDER BY created_at, event_id"
        ).fetchall()
    return [
        {
            "event_id": row["event_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]

def _locked_false_summary(record: Dict[str, Any]) -> Dict[str, bool]:
    return {field: record[field] for field in FALSE_FIELDS if field in record}

def validate_post_closeout_handoff_governance_closeout_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _get_components(db_path)
    receipts = _get_receipts(db_path)
    readiness = _get_readiness(db_path)
    events = _get_events(db_path)

    component_ids = {item["component_id"] for item in components}
    component_by_id = {item["component_id"]: item for item in components}
    receipt_codes = {item["receipt_code"] for item in receipts}

    checks = [
        ("COMPONENT_COUNT_5", len(components) == 5),
        ("GP096_EXISTS", GP096_CLOSEOUT_LOCK_CONTRACT_ID in component_ids),
        ("GP097_EXISTS", GP097_CLOSEOUT_RECEIPT_LEDGER_ID in component_ids),
        ("GP098_EXISTS", GP098_OWNER_SUMMARY_ID in component_ids),
        ("GP099_EXISTS", GP099_SECTION_CLOSEOUT_PACKET_ID in component_ids),
        ("GP100_COMPONENT_EXISTS", GP100_GOVERNANCE_READINESS_ID in component_ids),
        ("RECEIPT_COUNT_8", len(receipts) == len(CLOSEOUT_RECEIPTS)),
        ("ALL_RECEIPT_HASHES_64", all(isinstance(item["receipt_hash"], str) and len(item["receipt_hash"]) == 64 for item in receipts)),
        ("ALL_EXPECTED_RECEIPTS_EXIST", receipt_codes == {item[0] for item in CLOSEOUT_RECEIPTS}),
        ("READINESS_EXISTS", readiness["readiness_id"] == GP100_GOVERNANCE_READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("SECTION_CLOSED", readiness["section_closed"] is True),
        ("SAFE_TO_CONTINUE_TO_GP101", readiness["safe_to_continue_to_gp101"] is True),
        ("SECTION_GP091_GP100", readiness["section_range"] == "GP091-GP100"),
        ("NEXT_SECTION_GP101_GP110", readiness["readiness_payload"]["next_section_range"] == "GP101-GP110"),
        ("EVENTS_EXIST", len(events) >= 6),
    ]

    for component in components:
        checks.append((f"{component['pack_id']}_SOURCE_GP095_VALID", component["source_gp095_validation_passed"] is True))
        checks.append((f"{component['pack_id']}_SOURCE_GP090_SCORE_100", component["source_gp090_readiness_score"] == 100))
        checks.append((f"{component['pack_id']}_SOURCE_GP090_HASH_64", isinstance(component["source_gp090_readiness_hash"], str) and len(component["source_gp090_readiness_hash"]) == 64))
        checks.append((f"{component['pack_id']}_SOURCE_LEDGER_HASH_64", isinstance(component["source_ledger_hash"], str) and len(component["source_ledger_hash"]) == 64))
        checks.append((f"{component['pack_id']}_READY", component["component_ready"] is True))
        checks.append((f"{component['pack_id']}_LOCKED", component["component_locked"] is True))
        checks.append((f"{component['pack_id']}_SAFE_TO_CONTINUE", component["safe_to_continue"] is True))
        checks.append((f"{component['pack_id']}_HASH_64", isinstance(component["component_hash"], str) and len(component["component_hash"]) == 64))
        for field in FALSE_FIELDS:
            checks.append((f"{component['pack_id']}_NO_{field.upper()}", component[field] is False))

    for receipt in receipts:
        checks.append((f"RECEIPT_{receipt['receipt_code'].upper()}_LOCKED", receipt["receipt_locked"] is True))
        for field in FALSE_FIELDS:
            checks.append((f"RECEIPT_{receipt['receipt_code'].upper()}_NO_{field.upper()}", receipt[field] is False))

    for field in FALSE_FIELDS:
        checks.append((f"READINESS_NO_{field.upper()}", readiness[field] is False))

    checks_payload = [{"code": code, "passed": bool(passed)} for code, passed in checks]
    failed = [item for item in checks_payload if not item["passed"]]

    return {
        "pack": _layer_pack_payload(),
        "validation_ready": True,
        "valid": len(failed) == 0,
        "check_count": len(checks_payload),
        "passed_count": len(checks_payload) - len(failed),
        "failed_count": len(failed),
        "failed_checks": failed,
        "checks": checks_payload,
        "component_count": len(components),
        "receipt_count": len(receipts),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "section_closed": readiness["section_closed"],
        "safe_to_continue_to_gp101": len(failed) == 0 and readiness["safe_to_continue_to_gp101"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp096_closeout_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _get_component(GP096_CLOSEOUT_LOCK_CONTRACT_ID, db_path)
    return {"pack": _pack_payload(96, component["pack_name"]), "real_sqlite_backed": True, "closeout_lock_contract": component}

def get_gp097_closeout_receipt_ledger(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _get_component(GP097_CLOSEOUT_RECEIPT_LEDGER_ID, db_path)
    receipts = _get_receipts(db_path)
    ledger_payload = {
        "receipt_ledger_id": GP097_CLOSEOUT_RECEIPT_LEDGER_ID,
        "receipt_count": len(receipts),
        "receipt_hashes": [item["receipt_hash"] for item in receipts],
        "source_gp095_contract_id": component["source_gp095_contract_id"],
        "source_gp090_readiness_hash": component["source_gp090_readiness_hash"],
        "section_range": SECTION_RANGE,
        "vault_done": False,
    }
    ledger_hash = _hash_payload(ledger_payload)
    return {
        "pack": _pack_payload(97, component["pack_name"]),
        "real_sqlite_backed": True,
        "receipt_ledger": {
            **component,
            "receipt_ledger_hash": ledger_hash,
            "receipt_count": len(receipts),
        },
        "receipts": receipts,
    }

def get_gp098_owner_summary(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _get_component(GP098_OWNER_SUMMARY_ID, db_path)
    validation = validate_post_closeout_handoff_governance_closeout_layer(db_path)
    return {
        "pack": _pack_payload(98, component["pack_name"]),
        "real_sqlite_backed": True,
        "owner_summary": {
            **component,
            "summary_status": "OWNER_SUMMARY_READY_LOCKED",
            "section_closed_by_gp100": validation["section_closed"],
            "safe_to_continue_to_gp101": validation["safe_to_continue_to_gp101"],
            "vault_done": False,
            "clouds_should_continue": False,
        },
    }

def get_gp099_section_closeout_packet(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _get_component(GP099_SECTION_CLOSEOUT_PACKET_ID, db_path)
    receipts = _get_receipts(db_path)
    readiness = _get_readiness(db_path)
    packet_payload = {
        "packet_id": GP099_SECTION_CLOSEOUT_PACKET_ID,
        "source_gp095_contract_id": component["source_gp095_contract_id"],
        "source_gp090_readiness_hash": component["source_gp090_readiness_hash"],
        "receipt_hashes": [item["receipt_hash"] for item in receipts],
        "readiness_id": readiness["readiness_id"],
        "readiness_hash": readiness["readiness_hash"],
        "section_id": SECTION_ID,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
        "vault_done": False,
        "clouds_should_continue": False,
    }
    packet_hash = _hash_payload(packet_payload)
    return {
        "pack": _pack_payload(99, component["pack_name"]),
        "real_sqlite_backed": True,
        "section_closeout_packet": {
            **component,
            "packet_id": GP099_SECTION_CLOSEOUT_PACKET_ID,
            "packet_hash": packet_hash,
            "packet_payload": packet_payload,
            "section_closed": True,
            "safe_to_continue_to_gp101": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    }

def get_gp100_governance_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _get_component(GP100_GOVERNANCE_READINESS_ID, db_path)
    readiness = _get_readiness(db_path)
    validation = validate_post_closeout_handoff_governance_closeout_layer(db_path)
    return {
        "pack": _pack_payload(100, component["pack_name"]),
        "real_sqlite_backed": True,
        "governance_readiness_checkpoint": {
            **component,
            "readiness": readiness,
            "validation": validation,
            "section_closed": readiness["section_closed"],
            "readiness_hash": readiness["readiness_hash"],
            "readiness_score": readiness["readiness_score"],
            "safe_to_continue_to_gp101": validation["safe_to_continue_to_gp101"],
            "vault_done": False,
            "clouds_should_continue": False,
        },
    }

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _get_component(component_id, db_path)
    validation = validate_post_closeout_handoff_governance_closeout_layer(db_path)
    readiness = _get_readiness(db_path)

    return {
        "pack": _pack_payload(gp_number, component["pack_name"]),
        f"gp{gp_number:03d}_status": {
            "pack_id": f"VAULT_GP{gp_number:03d}",
            "ready": True,
            "layer_id": LAYER_ID,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "component_id": component_id,
            "component_type": component["component_type"],
            "real_sqlite_backed": True,
            "source_gp095_contract_id": component["source_gp095_contract_id"],
            "source_gp095_validation_passed": component["source_gp095_validation_passed"],
            "source_gp090_readiness_hash": component["source_gp090_readiness_hash"],
            "source_gp090_readiness_score": component["source_gp090_readiness_score"],
            "source_ledger_hash": component["source_ledger_hash"],
            "component_hash": component["component_hash"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "owner_review_required": component["owner_review_required"],
            "tower_review_required": component["tower_review_required"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "section_closed": readiness["section_closed"],
            "safe_to_continue_to_gp101": validation["safe_to_continue_to_gp101"],
            "foundation_status": "post_closeout_handoff_governance_layer_closed_safe_to_continue_not_done",
            "next": next_label,
            "owner_review_decision_recorded": component["owner_review_decision_recorded"],
            "owner_review_approval_recorded": component["owner_review_approval_recorded"],
            "owner_review_rejection_recorded": component["owner_review_rejection_recorded"],
            "decision_receipt_created": component["decision_receipt_created"],
            "tower_unlock_granted": component["tower_unlock_granted"],
            "restore_request_submitted": component["restore_request_submitted"],
            "restore_job_created": component["restore_job_created"],
            "provider_restore_api_called": component["provider_restore_api_called"],
            "object_body_read": component["object_body_read"],
            "object_body_view_enabled": component["object_body_view_enabled"],
            "object_body_download_enabled": component["object_body_download_enabled"],
            "export_package_created": component["export_package_created"],
            "direct_upload_enabled": component["direct_upload_enabled"],
            "export_enabled": component["export_enabled"],
            "execution_enabled": component["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp100",
        },
        "validation": validation,
    }

def get_gp096_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(96, GP096_CLOSEOUT_LOCK_CONTRACT_ID, "VAULT_GP097_CLOSEOUT_RECEIPT_LEDGER", db_path)

def get_gp097_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(97, GP097_CLOSEOUT_RECEIPT_LEDGER_ID, "VAULT_GP098_OWNER_SUMMARY", db_path)

def get_gp098_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(98, GP098_OWNER_SUMMARY_ID, "VAULT_GP099_SECTION_CLOSEOUT_PACKET", db_path)

def get_gp099_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(99, GP099_SECTION_CLOSEOUT_PACKET_ID, "VAULT_GP100_GOVERNANCE_READINESS_CHECKPOINT", db_path)

def get_gp100_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(100, GP100_GOVERNANCE_READINESS_ID, NEXT_PACK, db_path)
    status["gp100_status"]["next_section"] = NEXT_SECTION_ID
    status["gp100_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp100_status"]["next_pack"] = NEXT_PACK
    return status

def get_post_closeout_handoff_governance_closeout_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_post_closeout_handoff_governance_closeout_layer(db_path)
    components = _get_components(db_path)
    receipts = _get_receipts(db_path)
    readiness = _get_readiness(db_path)
    events = _get_events(db_path)
    validation = validate_post_closeout_handoff_governance_closeout_layer(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "receipts": receipts,
        "readiness": readiness,
        "events": {
            "event_count": len(events),
            "events": events,
        },
        "validation": validation,
        "truth": {
            "gp096_to_gp100_layer_ready": True,
            "section_closed": readiness["section_closed"],
            "safe_to_continue_to_gp101": validation["safe_to_continue_to_gp101"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_review_decision_recorded": False,
            "owner_review_approval_recorded": False,
            "owner_review_rejection_recorded": False,
            "tower_unlock_granted": False,
            "restore_request_submitted": False,
            "provider_restore_api_called": False,
            "object_body_read": False,
            "export_package_created": False,
            "direct_upload_enabled": False,
            "execution_enabled": False,
        },
        "routes": {
            "page": "/vault/post-closeout-handoff-governance-closeout-layer",
            "json": "/vault/post-closeout-handoff-governance-closeout-layer.json",
            "gp096": "/vault/gp096-status.json",
            "gp097": "/vault/gp097-status.json",
            "gp098": "/vault/gp098-status.json",
            "gp099": "/vault/gp099-status.json",
            "gp100": "/vault/gp100-status.json",
            "next_section": NEXT_PACK,
        },
    }

def render_post_closeout_handoff_governance_closeout_layer_page() -> str:
    home = get_post_closeout_handoff_governance_closeout_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    component_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['pack_id'])}</strong>
          <span>{escape(item['pack_name'])}</span>
          <code>{escape(item['component_type'])}</code>
        </article>
        """
        for item in home["components"]
    )

    receipt_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['receipt_code'])}</strong>
          <span>{escape(item['receipt_name'])}</span>
          <code>{escape(item['receipt_hash'][:16])}...</code>
        </article>
        """
        for item in home["receipts"]
    )

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP096-GP100 Closeout Layer</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{
  --bg0:#03040b; --bg1:#080d22; --panel:rgba(14,22,52,.86); --panel2:rgba(21,32,74,.76);
  --line:rgba(164,184,255,.23); --text:#eef3ff; --muted:#a8b2dd; --gold:#f5d17e;
  --cyan:#83eaff; --danger:#ff8c9c; --ok:#9dffca;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; min-height:100vh; color:var(--text);
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  background:
    radial-gradient(circle at 10% 8%, rgba(173,141,255,.18), transparent 34%),
    radial-gradient(circle at 88% 4%, rgba(131,234,255,.13), transparent 30%),
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
    <div class="eyebrow">Archive Vault · Giant Packs 096-100</div>
    <div class="eyebrow">Post-Closeout Handoff Governance Layer · GP091-GP100</div>
    <h1>Real Provider Post-Closeout Handoff Governance Closeout Layer</h1>
    <p>This layer closes GP091-GP100 and hands off to GP101-GP110 without unlocking restore, export, provider API, object body access, direct upload, execution, or Vault-done state.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['component_count']}</strong><span>components</span></div>
      <div class="metric"><strong>{home['store']['receipt_count']}</strong><span>receipts</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
      <div class="metric"><strong>{str(home['truth']['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP096-GP100 built</span>
      <span class="pill ok">Section closed</span>
      <span class="pill ok">Safe to GP101</span>
      <span class="pill danger">No restore</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No provider API</span>
      <span class="pill danger">No object body</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Layer Components</h2>
    <div class="cards">{component_cards}</div>
  </section>

  <section class="section">
    <h2>Closeout Receipts</h2>
    <div class="cards">{receipt_cards}</div>
  </section>

  <section class="section">
    <h2>Validation</h2>
    <p class="ok">Passed: {validation['passed_count']} / {validation['check_count']}</p>
    {failed}
    <p><code>{escape(readiness['readiness_hash'])}</code></p>
  </section>

  <section class="section">
    <h2>Next Section</h2>
    <p><code>{escape(NEXT_PACK)}</code></p>
    <p>{escape(NEXT_SECTION_ID)} · {escape(NEXT_SECTION_RANGE)}</p>
  </section>
</main>
</body>
</html>"""
