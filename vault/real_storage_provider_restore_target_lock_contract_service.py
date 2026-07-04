"""
VAULT GP085 — Real Storage Provider Restore Target Lock Contract

Current section:
Archive Vault — Real Provider Restore and Export Governance Layer / GP081-GP090

This pack builds a real SQLite-backed restore target lock contract sourced from
GP084. It creates durable target requirements, policies, blockers, events, and
validation while keeping restore target selection/validation and restore actions
locked.

It does not select a target, validate a target, select an object, call provider
restore APIs, create jobs, read object bodies, export, upload, or execute.
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

from vault.real_storage_provider_restore_scope_lock_contract_service import (
    DEFAULT_RESTORE_SCOPE_LOCK_CONTRACT_ID,
    get_gp084_status,
    get_storage_provider_restore_scope_blockers,
    get_storage_provider_restore_scope_lock_contract_record,
    get_storage_provider_restore_scope_policies,
    get_storage_provider_restore_scope_requirements,
)

PACK_ID = "VAULT_GP085"
PACK_NAME = "Real Storage Provider Restore Target Lock Contract"
SCHEMA_VERSION = "vault.real_storage_provider_restore_target_lock_contract.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RESTORE_AND_EXPORT_GOVERNANCE_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Restore and Export Governance Layer"
SECTION_RANGE = "GP081-GP090"

NEXT_PACK = "VAULT_GP086_REAL_STORAGE_PROVIDER_RESTORE_OBJECT_LOCK_CONTRACT"
NEXT_PACK_TITLE = "Real Storage Provider Restore Object Lock Contract"

DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID = "VSPRTLC-GP085-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_RESTORE_TARGET_LOCK_CONTRACT_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_restore_target_lock_contract.sqlite"

RESTORE_TARGET_REQUIREMENT_SPECS = [
    ("restore_target_lock_record_required", "Restore target lock record required", "target_lock"),
    ("source_restore_scope_contract_link_required", "Source restore scope contract link required", "source_scope"),
    ("restore_target_template_only_required", "Restore target template-only state required", "template_only"),
    ("restore_target_boundary_rule_set_required", "Restore target boundary rule set required", "target_boundary"),
    ("restore_target_no_live_selection_required", "Restore target no-live-selection boundary required", "target_selection_lock"),
    ("tower_target_unlock_required", "Tower target unlock required", "tower_gate"),
]

RESTORE_TARGET_POLICIES = [
    ("no_live_restore_target_selection", "No live restore target selection", "target_lock"),
    ("no_restore_target_validation", "No restore target validation", "target_validation_lock"),
    ("no_restore_target_pass_or_fail", "No restore target pass or fail", "target_result_lock"),
    ("no_restore_object_selection", "No restore object selection", "object_selection_lock"),
    ("no_provider_object_catalog_unlock", "No provider object catalog unlock", "provider_catalog_lock"),
    ("no_provider_restore_api_call", "No provider restore API call", "provider_call_lock"),
    ("no_restore_job_creation", "No restore job creation", "restore_job_lock"),
    ("no_object_body_read_for_target", "No object body read for target", "object_body_lock"),
    ("no_export_from_target", "No export from target", "export_lock"),
    ("no_execution_from_target", "No execution from target", "execution_lock"),
]

FALSE_FIELDS = [
    "restore_target_configured",
    "restore_target_attempted",
    "restore_target_enabled",
    "restore_target_selected",
    "restore_target_selection_started",
    "restore_target_selection_completed",
    "restore_target_validated",
    "restore_target_passed",
    "restore_target_failed",
    "restore_target_result_recorded",
    "restore_target_reason_requested",
    "restore_target_reason_recorded",
    "restore_target_owner_ack_requested",
    "restore_target_owner_ack_recorded",
    "restore_target_boundary_rule_set_finalized",
    "restore_target_boundary_evaluation_started",
    "restore_target_boundary_evaluation_completed",
    "restore_scope_configured",
    "restore_scope_attempted",
    "restore_scope_enabled",
    "restore_scope_selected",
    "restore_scope_validated",
    "restore_scope_passed",
    "restore_scope_failed",
    "restore_authority_verified",
    "restore_authority_passed",
    "restore_authority_failed",
    "restore_actor_authority_granted",
    "restore_eligibility_checked",
    "restore_eligibility_passed",
    "restore_eligibility_failed",
    "restore_object_selected",
    "restore_object_identifier_attached",
    "restore_object_key_attached",
    "restore_object_version_attached",
    "restore_object_metadata_attached",
    "restore_object_body_attached",
    "restore_request_configured",
    "restore_request_attempted",
    "restore_request_enabled",
    "restore_request_created",
    "restore_request_submitted",
    "restore_request_finalized",
    "restore_request_approved",
    "restore_request_denied",
    "restore_job_configured",
    "restore_job_created",
    "restore_job_started",
    "restore_job_completed",
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
    "restore_target_lock_contract_ready",
    "restore_target_requirements_ready",
    "restore_target_policies_ready",
    "restore_target_blockers_ready",
    "restore_target_validation_ready",
    "restore_target_locked",
    "restore_target_template_only",
    "restore_target_redaction_required",
    "source_restore_scope_lock_contract_attached",
    "safe_to_continue_to_gp086",
]

TRUE_REQUIREMENT_FIELDS = [
    "requirement_required",
    "restore_target_locked",
    "template_only",
    "target_redaction_required",
    "tower_review_required",
]

TRUE_BLOCKER_FIELDS = [
    "blocker_active",
    "blocks_restore_target_selection",
    "blocks_restore_target_validation",
    "blocks_restore_target_result",
    "blocks_restore_object_selection",
    "blocks_provider_object_catalog_unlock",
    "blocks_provider_restore_api",
    "blocks_restore_job",
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

def ensure_storage_provider_restore_target_lock_contract_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        true_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 1" for field in TRUE_CONTRACT_FIELDS)
        false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_storage_provider_restore_target_lock_contracts (
                restore_target_lock_contract_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_title TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_restore_scope_lock_contract_id TEXT NOT NULL,
                source_restore_scope_pack_id TEXT NOT NULL,
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
            "restore_target_configured",
            "restore_target_attempted",
            "restore_target_enabled",
            "restore_target_selected",
            "restore_target_selection_started",
            "restore_target_selection_completed",
            "restore_target_validated",
            "restore_target_passed",
            "restore_target_failed",
            "restore_target_result_recorded",
            "restore_target_reason_recorded",
            "restore_target_boundary_rule_set_finalized",
            "restore_target_boundary_evaluation_started",
            "restore_target_boundary_evaluation_completed",
            "restore_scope_selected",
            "restore_scope_validated",
            "restore_scope_passed",
            "restore_scope_failed",
            "restore_authority_verified",
            "restore_authority_passed",
            "restore_authority_failed",
            "restore_actor_authority_granted",
            "restore_eligibility_checked",
            "restore_eligibility_passed",
            "restore_eligibility_failed",
            "restore_object_selected",
            "restore_object_identifier_attached",
            "restore_object_key_attached",
            "restore_object_body_attached",
            "restore_request_created",
            "restore_request_submitted",
            "restore_request_finalized",
            "restore_job_created",
            "restore_job_started",
            "restore_job_completed",
            "provider_restore_api_configured",
            "provider_restore_api_called",
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_restore_target_requirements (
                restore_target_requirement_id TEXT PRIMARY KEY,
                restore_target_lock_contract_id TEXT NOT NULL,
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
                FOREIGN KEY(restore_target_lock_contract_id)
                    REFERENCES vault_storage_provider_restore_target_lock_contracts(restore_target_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(restore_target_lock_contract_id, source_requirement_id, requirement_code)
            )
            """
        )

        policy_false = [
            "policy_verified",
            "restore_target_selected",
            "restore_target_selection_started",
            "restore_target_selection_completed",
            "restore_target_validated",
            "restore_target_passed",
            "restore_target_failed",
            "restore_target_result_recorded",
            "restore_target_boundary_rule_set_finalized",
            "restore_target_boundary_evaluation_started",
            "restore_target_boundary_evaluation_completed",
            "restore_scope_selected",
            "restore_scope_validated",
            "restore_authority_verified",
            "restore_actor_authority_granted",
            "restore_eligibility_checked",
            "restore_object_selected",
            "restore_object_identifier_attached",
            "restore_object_key_attached",
            "restore_object_body_attached",
            "restore_request_created",
            "restore_request_submitted",
            "restore_request_finalized",
            "restore_job_created",
            "provider_restore_api_configured",
            "provider_restore_api_called",
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_restore_target_policies (
                restore_target_policy_id TEXT PRIMARY KEY,
                restore_target_lock_contract_id TEXT NOT NULL,
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
                FOREIGN KEY(restore_target_lock_contract_id)
                    REFERENCES vault_storage_provider_restore_target_lock_contracts(restore_target_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(restore_target_lock_contract_id, policy_code)
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_restore_target_blockers (
                restore_target_blocker_id TEXT PRIMARY KEY,
                restore_target_lock_contract_id TEXT NOT NULL,
                source_restore_scope_blocker_id TEXT NOT NULL,
                source_blocker_code TEXT NOT NULL,
                source_blocker_category TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                {blocker_true_sql},
                {blocker_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(restore_target_lock_contract_id)
                    REFERENCES vault_storage_provider_restore_target_lock_contracts(restore_target_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(restore_target_lock_contract_id, source_restore_scope_blocker_id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_restore_target_events (
                event_id TEXT PRIMARY KEY,
                restore_target_lock_contract_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(restore_target_lock_contract_id)
                    REFERENCES vault_storage_provider_restore_target_lock_contracts(restore_target_lock_contract_id)
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
            "vault_storage_provider_restore_target_lock_contracts",
            "vault_storage_provider_restore_target_requirements",
            "vault_storage_provider_restore_target_policies",
            "vault_storage_provider_restore_target_blockers",
            "vault_storage_provider_restore_target_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, contract_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VSPRTLCEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_storage_provider_restore_target_events",
        {
            "event_id": event_id,
            "restore_target_lock_contract_id": contract_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "contract_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_restore_target_lock_contracts").fetchone()["c"]),
            "requirement_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_restore_target_requirements").fetchone()["c"]),
            "policy_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_restore_target_policies").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_restore_target_blockers").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_restore_target_events").fetchone()["c"]),
        }

def _select_requirement_seed(source_requirements: list[dict], limit: int = 54) -> list[dict]:
    selected = []
    seen = set()

    for item in source_requirements:
        source_requirement_id = item["restore_scope_requirement_id"]
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

def initialize_real_storage_provider_restore_target_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_restore_target_lock_contract_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        exists = conn.execute(
            """
            SELECT restore_target_lock_contract_id
            FROM vault_storage_provider_restore_target_lock_contracts
            WHERE restore_target_lock_contract_id = ?
            """,
            (DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,),
        ).fetchone()

        if exists is None:
            source_status = get_gp084_status()["gp084_status"]
            source_contract = get_storage_provider_restore_scope_lock_contract_record()["restore_scope_lock_contract"]
            source_requirements = get_storage_provider_restore_scope_requirements()["requirements"]
            source_policies = get_storage_provider_restore_scope_policies()["policies"]
            source_blockers = get_storage_provider_restore_scope_blockers()["blockers"]
            now = _now_iso()

            requirement_seed = _select_requirement_seed(source_requirements, 54)
            requirement_count = len(requirement_seed) * len(RESTORE_TARGET_REQUIREMENT_SPECS)

            contract_data = {
                "schema_version": SCHEMA_VERSION,
                "contract_type": "REAL_STORAGE_PROVIDER_RESTORE_TARGET_LOCK_CONTRACT",
                "source_pack": "VAULT_GP084",
                "source_restore_scope_lock_contract_id": source_contract["restore_scope_lock_contract_id"],
                "source_restore_scope_validation_passed": source_status["validation_passed"],
                "source_safe_to_continue_to_gp085": source_status["safe_to_continue_to_gp085"],
                "section": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "restore_target_requirement_seed_count": len(requirement_seed),
                "restore_target_requirement_code_count": len(RESTORE_TARGET_REQUIREMENT_SPECS),
                "restore_target_requirement_count": requirement_count,
                "restore_target_policy_count": len(RESTORE_TARGET_POLICIES),
                "carried_restore_scope_blocker_count": len(source_blockers),
                "source_restore_scope_policy_count": len(source_policies),
                "restore_target_locked": True,
                "restore_target_template_only": True,
                "restore_target_selected": False,
                "restore_target_validated": False,
                "restore_target_passed": False,
                "restore_target_failed": False,
                "restore_target_result_recorded": False,
                "restore_object_selected": False,
                "restore_scope_selected": False,
                "restore_scope_validated": False,
                "restore_authority_verified": False,
                "restore_eligibility_checked": False,
                "provider_restore_api_called": False,
                "provider_object_catalog_unlocked": False,
                "restore_request_created": False,
                "restore_request_submitted": False,
                "restore_job_created": False,
                "object_body_read": False,
                "direct_upload_enabled": False,
                "export_enabled": False,
                "execution_enabled": False,
                "vault_done": False,
                "next_pack": NEXT_PACK,
                "next_pack_title": NEXT_PACK_TITLE,
                "safe_to_continue_to_gp086": True,
            }

            contract_payload = {
                "restore_target_lock_contract_id": DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,
                "pack_id": PACK_ID,
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_restore_scope_lock_contract_id": source_contract["restore_scope_lock_contract_id"],
                "source_restore_scope_pack_id": source_contract["pack_id"],
                "contract_status": "REAL_RESTORE_TARGET_LOCK_CONTRACT_OPEN_TEMPLATE_ONLY_TOWER_LOCKED",
                "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED_FOR_RESTORE_TARGET",
                "contract_data_json": _json_dumps(contract_data),
                "created_at": now,
                "updated_at": now,
            }
            for field in TRUE_CONTRACT_FIELDS:
                contract_payload[field] = 1
            for field in FALSE_FIELDS:
                contract_payload[field] = 0
            _insert_dict(conn, "vault_storage_provider_restore_target_lock_contracts", contract_payload)

            for source_requirement in requirement_seed:
                for code, name, category in RESTORE_TARGET_REQUIREMENT_SPECS:
                    payload = {
                        "restore_target_requirement_id": f"VSPRTR-{source_requirement['restore_scope_requirement_id'].replace('VSPRSR-', '')}-{code.upper().replace('_', '-')}",
                        "restore_target_lock_contract_id": DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,
                        "source_requirement_id": source_requirement["restore_scope_requirement_id"],
                        "source_pack_id": source_requirement["source_pack_id"],
                        "source_requirement_code": source_requirement["requirement_code"],
                        "requirement_code": code,
                        "requirement_name": name,
                        "requirement_category": category,
                        "requirement_message": f"{name} remains required before a restore target can be selected or validated.",
                        "requirement_status": "REAL_RESTORE_TARGET_REQUIREMENT_RECORDED_TEMPLATE_ONLY_TOWER_LOCKED",
                        "created_at": now,
                        "updated_at": now,
                    }
                    for field in TRUE_REQUIREMENT_FIELDS:
                        payload[field] = 1
                    for field in [
                        "requirement_verified",
                        "restore_target_configured",
                        "restore_target_attempted",
                        "restore_target_enabled",
                        "restore_target_selected",
                        "restore_target_selection_started",
                        "restore_target_selection_completed",
                        "restore_target_validated",
                        "restore_target_passed",
                        "restore_target_failed",
                        "restore_target_result_recorded",
                        "restore_target_reason_recorded",
                        "restore_target_boundary_rule_set_finalized",
                        "restore_target_boundary_evaluation_started",
                        "restore_target_boundary_evaluation_completed",
                        "restore_scope_selected",
                        "restore_scope_validated",
                        "restore_scope_passed",
                        "restore_scope_failed",
                        "restore_authority_verified",
                        "restore_authority_passed",
                        "restore_authority_failed",
                        "restore_actor_authority_granted",
                        "restore_eligibility_checked",
                        "restore_eligibility_passed",
                        "restore_eligibility_failed",
                        "restore_object_selected",
                        "restore_object_identifier_attached",
                        "restore_object_key_attached",
                        "restore_object_body_attached",
                        "restore_request_created",
                        "restore_request_submitted",
                        "restore_request_finalized",
                        "restore_job_created",
                        "restore_job_started",
                        "restore_job_completed",
                        "provider_restore_api_configured",
                        "provider_restore_api_called",
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
                    _insert_dict(conn, "vault_storage_provider_restore_target_requirements", payload)

            for code, name, category in RESTORE_TARGET_POLICIES:
                payload = {
                    "restore_target_policy_id": f"VSPRTP-{code.upper().replace('_', '-')}",
                    "restore_target_lock_contract_id": DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,
                    "policy_code": code,
                    "policy_name": name,
                    "policy_category": category,
                    "policy_message": f"{name}; GP085 cannot select or validate a target, select objects, unlock provider catalogs, call providers, create jobs, export, upload, or execute.",
                    "policy_status": "REAL_RESTORE_TARGET_POLICY_RECORDED_TEMPLATE_ONLY_TOWER_LOCKED",
                    "policy_required": 1,
                    "tower_review_required": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in [
                    "policy_verified",
                    "restore_target_selected",
                    "restore_target_selection_started",
                    "restore_target_selection_completed",
                    "restore_target_validated",
                    "restore_target_passed",
                    "restore_target_failed",
                    "restore_target_result_recorded",
                    "restore_target_boundary_rule_set_finalized",
                    "restore_target_boundary_evaluation_started",
                    "restore_target_boundary_evaluation_completed",
                    "restore_scope_selected",
                    "restore_scope_validated",
                    "restore_authority_verified",
                    "restore_actor_authority_granted",
                    "restore_eligibility_checked",
                    "restore_object_selected",
                    "restore_object_identifier_attached",
                    "restore_object_key_attached",
                    "restore_object_body_attached",
                    "restore_request_created",
                    "restore_request_submitted",
                    "restore_request_finalized",
                    "restore_job_created",
                    "provider_restore_api_configured",
                    "provider_restore_api_called",
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
                _insert_dict(conn, "vault_storage_provider_restore_target_policies", payload)

            for blocker in source_blockers:
                payload = {
                    "restore_target_blocker_id": f"VSPRTB-{blocker['restore_scope_blocker_id'].replace('VSPRSB-', '')}",
                    "restore_target_lock_contract_id": DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,
                    "source_restore_scope_blocker_id": blocker["restore_scope_blocker_id"],
                    "source_blocker_code": blocker["source_blocker_code"],
                    "source_blocker_category": blocker["source_blocker_category"],
                    "blocker_name": blocker["blocker_name"],
                    "severity": blocker["severity"],
                    "blocker_status": "REAL_RESTORE_TARGET_BLOCKER_ACTIVE_CARRIED_FROM_GP084",
                    "created_at": now,
                    "updated_at": now,
                }
                for field in TRUE_BLOCKER_FIELDS:
                    payload[field] = 1
                for field in ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]:
                    payload[field] = 0
                _insert_dict(conn, "vault_storage_provider_restore_target_blockers", payload)

            for event_type, event_payload in [
                ("REAL_STORAGE_PROVIDER_RESTORE_TARGET_LOCK_CONTRACT_CREATED", contract_data),
                ("SOURCE_GP084_RESTORE_SCOPE_LOCK_CONTRACT_ATTACHED", {
                    "source_restore_scope_lock_contract_id": source_contract["restore_scope_lock_contract_id"],
                    "source_restore_scope_pack_id": source_contract["pack_id"],
                    "source_validation_passed": source_status["validation_passed"],
                    "source_safe_to_continue_to_gp085": source_status["safe_to_continue_to_gp085"],
                }),
                ("REAL_RESTORE_TARGET_REQUIREMENTS_CREATED_TEMPLATE_ONLY", {
                    "requirement_count": requirement_count,
                    "requirement_seed_count": len(requirement_seed),
                }),
                ("REAL_RESTORE_TARGET_POLICIES_CREATED_TEMPLATE_ONLY", {
                    "policy_count": len(RESTORE_TARGET_POLICIES),
                }),
                ("REAL_RESTORE_TARGET_BLOCKERS_CARRIED_FORWARD", {
                    "blocker_count": len(source_blockers),
                }),
                ("RESTORE_TARGET_LOCKS_CONFIRMED", {
                    "restore_target_selected": False,
                    "restore_target_validated": False,
                    "restore_target_passed": False,
                    "restore_target_failed": False,
                    "restore_object_selected": False,
                    "restore_scope_selected": False,
                    "restore_authority_verified": False,
                    "restore_eligibility_checked": False,
                    "provider_restore_api_called": False,
                    "provider_object_catalog_unlocked": False,
                    "restore_request_created": False,
                    "restore_request_submitted": False,
                    "restore_job_created": False,
                    "object_body_read": False,
                    "direct_upload_enabled": False,
                    "export_enabled": False,
                    "execution_enabled": False,
                    "vault_done": False,
                }),
            ]:
                _insert_event(conn, DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _sum_counts(table: str, contract_id: str, fields: list[str], db_path: Optional[str] = None) -> Dict[str, int]:
    selects = ["COUNT(*) AS total_count"]
    for field in fields:
        selects.append(f"SUM(CASE WHEN {field} = 1 THEN 1 ELSE 0 END) AS {field}_count")
    with _connect(db_path) as conn:
        row = conn.execute(
            f"SELECT {', '.join(selects)} FROM {table} WHERE restore_target_lock_contract_id = ?",
            (contract_id,),
        ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}

def get_storage_provider_restore_target_lock_contract_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_restore_target_lock_contract(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_restore_target_lock_contracts
            WHERE restore_target_lock_contract_id = ?
            """,
            (DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,),
        ).fetchone()
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "restore_target_lock_contract": _boolify(row, {"contract_data_json": "contract_data"}),
    }

def get_storage_provider_restore_target_requirements(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_restore_target_lock_contract(db_path)
    fields = [
        "requirement_required",
        "requirement_verified",
        "restore_target_locked",
        "template_only",
        "target_redaction_required",
        "tower_review_required",
        "tower_review_granted",
        "restore_target_configured",
        "restore_target_attempted",
        "restore_target_enabled",
        "restore_target_selected",
        "restore_target_selection_started",
        "restore_target_selection_completed",
        "restore_target_validated",
        "restore_target_passed",
        "restore_target_failed",
        "restore_target_result_recorded",
        "restore_target_reason_recorded",
        "restore_target_boundary_rule_set_finalized",
        "restore_target_boundary_evaluation_started",
        "restore_target_boundary_evaluation_completed",
        "restore_scope_selected",
        "restore_scope_validated",
        "restore_scope_passed",
        "restore_scope_failed",
        "restore_authority_verified",
        "restore_authority_passed",
        "restore_authority_failed",
        "restore_actor_authority_granted",
        "restore_eligibility_checked",
        "restore_eligibility_passed",
        "restore_eligibility_failed",
        "restore_object_selected",
        "restore_object_identifier_attached",
        "restore_object_key_attached",
        "restore_object_body_attached",
        "restore_request_created",
        "restore_request_submitted",
        "restore_request_finalized",
        "restore_job_created",
        "restore_job_started",
        "restore_job_completed",
        "provider_restore_api_configured",
        "provider_restore_api_called",
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
    counts = _sum_counts("vault_storage_provider_restore_target_requirements", DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_restore_target_requirements
            WHERE restore_target_lock_contract_id = ?
            ORDER BY source_requirement_id, requirement_category, requirement_code
            """,
            (DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,),
        ).fetchall()
        source_requirement_count = conn.execute(
            """
            SELECT COUNT(DISTINCT source_requirement_id) AS c
            FROM vault_storage_provider_restore_target_requirements
            WHERE restore_target_lock_contract_id = ?
            """,
            (DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]
        requirement_code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT requirement_code) AS c
            FROM vault_storage_provider_restore_target_requirements
            WHERE restore_target_lock_contract_id = ?
            """,
            (DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]

    counts["requirement_count"] = counts.pop("total_count")
    counts["source_requirement_count"] = int(source_requirement_count)
    counts["requirement_code_count"] = int(requirement_code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "requirements": [_boolify(row) for row in rows]}

def get_storage_provider_restore_target_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_restore_target_lock_contract(db_path)
    fields = [
        "policy_required",
        "policy_verified",
        "tower_review_required",
        "tower_review_granted",
        "restore_target_selected",
        "restore_target_selection_started",
        "restore_target_selection_completed",
        "restore_target_validated",
        "restore_target_passed",
        "restore_target_failed",
        "restore_target_result_recorded",
        "restore_target_boundary_rule_set_finalized",
        "restore_target_boundary_evaluation_started",
        "restore_target_boundary_evaluation_completed",
        "restore_scope_selected",
        "restore_scope_validated",
        "restore_authority_verified",
        "restore_actor_authority_granted",
        "restore_eligibility_checked",
        "restore_object_selected",
        "restore_object_identifier_attached",
        "restore_object_key_attached",
        "restore_object_body_attached",
        "restore_request_created",
        "restore_request_submitted",
        "restore_request_finalized",
        "restore_job_created",
        "provider_restore_api_configured",
        "provider_restore_api_called",
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
    counts = _sum_counts("vault_storage_provider_restore_target_policies", DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_restore_target_policies
            WHERE restore_target_lock_contract_id = ?
            ORDER BY policy_category, policy_code
            """,
            (DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,),
        ).fetchall()
        policy_code_count = conn.execute(
            """
            SELECT COUNT(DISTINCT policy_code) AS c
            FROM vault_storage_provider_restore_target_policies
            WHERE restore_target_lock_contract_id = ?
            """,
            (DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,),
        ).fetchone()["c"]

    counts["policy_count"] = counts.pop("total_count")
    counts["policy_code_count"] = int(policy_code_count)
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "policies": [_boolify(row) for row in rows]}

def get_storage_provider_restore_target_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_restore_target_lock_contract(db_path)
    fields = TRUE_BLOCKER_FIELDS + ["tower_review_granted", "risk_accepted", "risk_waived", "mitigation_approved", "resolved"]
    counts = _sum_counts("vault_storage_provider_restore_target_blockers", DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID, fields, db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_restore_target_blockers
            WHERE restore_target_lock_contract_id = ?
            ORDER BY source_blocker_category, source_blocker_code
            """,
            (DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,),
        ).fetchall()

    counts["blocker_count"] = counts.pop("total_count")
    return {"pack": _pack_payload(), "real_sqlite_backed": True, **counts, "blockers": [_boolify(row) for row in rows]}

def get_storage_provider_restore_target_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_restore_target_lock_contract(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_restore_target_events
            WHERE restore_target_lock_contract_id = ?
            ORDER BY created_at, event_id
            """,
            (DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,),
        ).fetchall()
    events = [
        {
            "event_id": row["event_id"],
            "restore_target_lock_contract_id": row["restore_target_lock_contract_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return {"pack": _pack_payload(), "real_sqlite_backed": True, "event_count": len(events), "events": events}

def record_storage_provider_restore_target_event(event_type: str, event_payload: Optional[Dict[str, Any]] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_restore_target_lock_contract(db_path)
    payload = dict(event_payload or {})
    payload.update({
        "write_type": "REAL_STORAGE_PROVIDER_RESTORE_TARGET_LOCK_EVENT",
        "restore_target_lock_contract_ready": True,
        "restore_target_locked": True,
        "restore_target_template_only": True,
        "restore_target_selected": False,
        "restore_target_validated": False,
        "restore_target_passed": False,
        "restore_target_failed": False,
        "restore_object_selected": False,
        "restore_scope_selected": False,
        "restore_authority_verified": False,
        "restore_eligibility_checked": False,
        "provider_restore_api_called": False,
        "provider_object_catalog_unlocked": False,
        "restore_request_created": False,
        "restore_request_submitted": False,
        "restore_job_created": False,
        "object_body_read": False,
        "direct_upload_enabled": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    })
    with _connect(db_path) as conn:
        event_id = _insert_event(conn, DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID, event_type, payload)
        conn.commit()
    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "restore_target_lock_contract_id": DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID,
        "real_sqlite_backed": True,
        **payload,
    }

def validate_storage_provider_restore_target_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    contract = get_storage_provider_restore_target_lock_contract_record(db_path)["restore_target_lock_contract"]
    requirements = get_storage_provider_restore_target_requirements(db_path)
    policies = get_storage_provider_restore_target_policies(db_path)
    blockers = get_storage_provider_restore_target_blockers(db_path)
    events = get_storage_provider_restore_target_events(db_path)

    expected_requirements = 54 * len(RESTORE_TARGET_REQUIREMENT_SPECS)
    expected_policies = len(RESTORE_TARGET_POLICIES)
    expected_blockers = 18

    false_checks = [(f"NO_CONTRACT_{field.upper()}", contract[field] is False) for field in FALSE_FIELDS]

    checks = [
        ("REAL_SQLITE_RESTORE_TARGET_LOCK_CONTRACT_EXISTS", contract["restore_target_lock_contract_id"] == DEFAULT_RESTORE_TARGET_LOCK_CONTRACT_ID),
        ("SOURCE_GP084_RESTORE_SCOPE_LOCK_CONTRACT_ATTACHED", contract["source_restore_scope_lock_contract_id"] == DEFAULT_RESTORE_SCOPE_LOCK_CONTRACT_ID),
        ("SECTION_GP081_GP090", contract["section_id"] == SECTION_ID and contract["section_range"] == SECTION_RANGE),
        ("RESTORE_TARGET_LOCK_CONTRACT_READY", contract["restore_target_lock_contract_ready"] is True),
        ("RESTORE_TARGET_REQUIREMENTS_READY", contract["restore_target_requirements_ready"] is True),
        ("RESTORE_TARGET_POLICIES_READY", contract["restore_target_policies_ready"] is True),
        ("RESTORE_TARGET_BLOCKERS_READY", contract["restore_target_blockers_ready"] is True),
        ("RESTORE_TARGET_VALIDATION_READY", contract["restore_target_validation_ready"] is True),
        ("RESTORE_TARGET_LOCKED", contract["restore_target_locked"] is True),
        ("RESTORE_TARGET_TEMPLATE_ONLY", contract["restore_target_template_only"] is True),
        ("SAFE_TO_CONTINUE_TO_GP086", contract["safe_to_continue_to_gp086"] is True),
        ("RESTORE_TARGET_REQUIREMENTS_EXIST", requirements["requirement_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_REQUIRED", requirements["requirement_required_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_LOCKED", requirements["restore_target_locked_count"] == expected_requirements),
        ("ALL_REQUIREMENTS_TEMPLATE_ONLY", requirements["template_only_count"] == expected_requirements),
        ("NO_REQUIREMENT_TARGET_SELECTED", requirements["restore_target_selected_count"] == 0),
        ("NO_REQUIREMENT_TARGET_STARTED", requirements["restore_target_selection_started_count"] == 0),
        ("NO_REQUIREMENT_TARGET_COMPLETED", requirements["restore_target_selection_completed_count"] == 0),
        ("NO_REQUIREMENT_TARGET_VALIDATED", requirements["restore_target_validated_count"] == 0),
        ("NO_REQUIREMENT_TARGET_RESULT", requirements["restore_target_passed_count"] == 0 and requirements["restore_target_failed_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_SELECTED", requirements["restore_object_selected_count"] == 0),
        ("NO_REQUIREMENT_SCOPE_SELECTED", requirements["restore_scope_selected_count"] == 0),
        ("NO_REQUIREMENT_SCOPE_VALIDATED", requirements["restore_scope_validated_count"] == 0),
        ("NO_REQUIREMENT_AUTHORITY_VERIFIED", requirements["restore_authority_verified_count"] == 0),
        ("NO_REQUIREMENT_ELIGIBILITY_CHECKED", requirements["restore_eligibility_checked_count"] == 0),
        ("NO_REQUIREMENT_RESTORE_REQUEST_CREATED", requirements["restore_request_created_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_RESTORE_API_CALLED", requirements["provider_restore_api_called_count"] == 0),
        ("NO_REQUIREMENT_PROVIDER_CATALOG_UNLOCKED", requirements["provider_object_catalog_unlocked_count"] == 0),
        ("NO_REQUIREMENT_RESTORE_JOB_CREATED", requirements["restore_job_created_count"] == 0),
        ("NO_REQUIREMENT_OBJECT_BODY_READ", requirements["object_body_read_count"] == 0),
        ("NO_REQUIREMENT_DIRECT_UPLOAD", requirements["direct_upload_enabled_count"] == 0),
        ("NO_REQUIREMENT_EXPORT", requirements["export_enabled_count"] == 0),
        ("NO_REQUIREMENT_EXECUTION", requirements["execution_enabled_count"] == 0),
        ("RESTORE_TARGET_POLICIES_EXIST", policies["policy_count"] == expected_policies),
        ("NO_POLICY_TARGET_SELECTED", policies["restore_target_selected_count"] == 0),
        ("NO_POLICY_TARGET_VALIDATED", policies["restore_target_validated_count"] == 0),
        ("NO_POLICY_TARGET_RESULT", policies["restore_target_passed_count"] == 0 and policies["restore_target_failed_count"] == 0),
        ("NO_POLICY_OBJECT_SELECTED", policies["restore_object_selected_count"] == 0),
        ("NO_POLICY_SCOPE_SELECTED", policies["restore_scope_selected_count"] == 0),
        ("NO_POLICY_SCOPE_VALIDATED", policies["restore_scope_validated_count"] == 0),
        ("NO_POLICY_AUTHORITY_VERIFIED", policies["restore_authority_verified_count"] == 0),
        ("NO_POLICY_ELIGIBILITY_CHECKED", policies["restore_eligibility_checked_count"] == 0),
        ("NO_POLICY_PROVIDER_RESTORE_API_CALLED", policies["provider_restore_api_called_count"] == 0),
        ("NO_POLICY_PROVIDER_CATALOG_UNLOCKED", policies["provider_object_catalog_unlocked_count"] == 0),
        ("NO_POLICY_RESTORE_JOB_CREATED", policies["restore_job_created_count"] == 0),
        ("NO_POLICY_OBJECT_BODY_READ", policies["object_body_read_count"] == 0),
        ("NO_POLICY_DIRECT_UPLOAD", policies["direct_upload_enabled_count"] == 0),
        ("NO_POLICY_EXPORT", policies["export_enabled_count"] == 0),
        ("NO_POLICY_EXECUTION", policies["execution_enabled_count"] == 0),
        ("RESTORE_SCOPE_BLOCKERS_CARRIED_FORWARD", blockers["blocker_count"] == expected_blockers),
        ("ALL_BLOCKERS_ACTIVE", blockers["blocker_active_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_TARGET_SELECTION", blockers["blocks_restore_target_selection_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_TARGET_VALIDATION", blockers["blocks_restore_target_validation_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_TARGET_RESULT", blockers["blocks_restore_target_result_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_OBJECT_SELECTION", blockers["blocks_restore_object_selection_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_CATALOG_UNLOCK", blockers["blocks_provider_object_catalog_unlock_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_RESTORE_API", blockers["blocks_provider_restore_api_count"] == expected_blockers),
        ("ALL_BLOCKERS_BLOCK_RESTORE_JOB", blockers["blocks_restore_job_count"] == expected_blockers),
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
        "safe_to_continue_to_gp086": len(failed) == 0,
        "vault_done": False,
    }

def get_storage_provider_restore_target_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp086": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP085 adds the restore target lock contract. Continue to GP086 with restore object while target selection/validation, object selection, provider restore API calls, object body reads, direct upload, export, and execution remain locked.",
            "carry_forward_rules": [
                "Keep GP084 restore scope lock contract attached.",
                "Keep restore target selection locked.",
                "Keep restore target validation locked.",
                "Keep target pass/fail/result recording locked.",
                "Keep restore object selection locked.",
                "Keep provider object catalog unlock locked.",
                "Keep provider restore API calls locked.",
                "Keep restore jobs locked.",
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
        "depends_on": ["VAULT_GP084"],
        "foundation_status": "restore_target_lock_contract_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_restore_target_lock_contract",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }

def _routes_payload() -> Dict[str, str]:
    return {
        "route": "/vault/real-storage-provider-restore-target-lock-contract",
        "json_route": "/vault/real-storage-provider-restore-target-lock-contract.json",
        "record_route": "/vault/storage-provider-restore-target-lock-contract-record.json",
        "requirements_route": "/vault/storage-provider-restore-target-requirements.json",
        "policies_route": "/vault/storage-provider-restore-target-policies.json",
        "blockers_route": "/vault/storage-provider-restore-target-blockers.json",
        "events_route": "/vault/storage-provider-restore-target-events.json",
        "validation_route": "/vault/storage-provider-restore-target-validation.json",
        "next_step_route": "/vault/storage-provider-restore-target-next-step.json",
        "gp085_status_route": "/vault/gp085-status.json",
    }

def get_real_storage_provider_restore_target_lock_contract_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_restore_target_lock_contract(db_path)
    contract = get_storage_provider_restore_target_lock_contract_record(db_path)["restore_target_lock_contract"]
    requirements = get_storage_provider_restore_target_requirements(db_path)
    policies = get_storage_provider_restore_target_policies(db_path)
    blockers = get_storage_provider_restore_target_blockers(db_path)
    events = get_storage_provider_restore_target_events(db_path)
    validation = validate_storage_provider_restore_target_lock_contract(db_path)

    truth = {
        "real_storage_provider_restore_target_lock_contract_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "source_gp084_restore_scope_lock_contract_attached": contract["source_restore_scope_lock_contract_id"] == DEFAULT_RESTORE_SCOPE_LOCK_CONTRACT_ID,
        "validation_passed": validation["valid"],
        "restore_target_lock_contract_ready": contract["restore_target_lock_contract_ready"],
        "restore_target_locked": contract["restore_target_locked"],
        "restore_target_template_only": contract["restore_target_template_only"],
        "requirement_count": requirements["requirement_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "event_count": events["event_count"],
        "restore_target_selected": contract["restore_target_selected"],
        "restore_target_validated": contract["restore_target_validated"],
        "restore_target_passed": contract["restore_target_passed"],
        "restore_target_failed": contract["restore_target_failed"],
        "restore_object_selected": contract["restore_object_selected"],
        "restore_scope_selected": contract["restore_scope_selected"],
        "restore_scope_validated": contract["restore_scope_validated"],
        "restore_authority_verified": contract["restore_authority_verified"],
        "restore_eligibility_checked": contract["restore_eligibility_checked"],
        "restore_request_created": contract["restore_request_created"],
        "restore_request_submitted": contract["restore_request_submitted"],
        "provider_restore_api_configured": contract["provider_restore_api_configured"],
        "provider_restore_api_called": contract["provider_restore_api_called"],
        "provider_object_catalog_unlocked": contract["provider_object_catalog_unlocked"],
        "restore_job_created": contract["restore_job_created"],
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
        "safe_to_continue_to_gp086": validation["safe_to_continue_to_gp086"],
        "vault_done": contract["vault_done"],
    }

    return {
        "pack": _pack_payload(),
        "restore_target_truth": truth,
        "store": init,
        "restore_target_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_restore_target_next_step()["next_step"],
    }

def get_gp085_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_restore_target_lock_contract_home(db_path)
    contract = home["restore_target_lock_contract"]
    requirements = home["requirements"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp085_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_restore_target_lock_contract_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_contract_count": home["store"]["contract_count"],
            "real_requirement_count": home["store"]["requirement_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp084_restore_scope_lock_contract_attached": True,
            "restore_target_lock_contract_ready": contract["restore_target_lock_contract_ready"],
            "restore_target_requirements_ready": contract["restore_target_requirements_ready"],
            "restore_target_policies_ready": contract["restore_target_policies_ready"],
            "restore_target_blockers_ready": contract["restore_target_blockers_ready"],
            "restore_target_validation_ready": contract["restore_target_validation_ready"],
            "restore_target_locked": contract["restore_target_locked"],
            "restore_target_template_only": contract["restore_target_template_only"],
            "restore_target_redaction_required": contract["restore_target_redaction_required"],
            "source_requirement_count": requirements["source_requirement_count"],
            "requirement_code_count": requirements["requirement_code_count"],
            "policy_code_count": policies["policy_code_count"],
            "blocker_count": blockers["blocker_count"],
            "restore_target_selected_count": requirements["restore_target_selected_count"] + policies["restore_target_selected_count"],
            "restore_target_selection_started_count": requirements["restore_target_selection_started_count"] + policies["restore_target_selection_started_count"],
            "restore_target_selection_completed_count": requirements["restore_target_selection_completed_count"] + policies["restore_target_selection_completed_count"],
            "restore_target_validated_count": requirements["restore_target_validated_count"] + policies["restore_target_validated_count"],
            "restore_target_passed_count": requirements["restore_target_passed_count"] + policies["restore_target_passed_count"],
            "restore_target_failed_count": requirements["restore_target_failed_count"] + policies["restore_target_failed_count"],
            "restore_target_result_recorded_count": requirements["restore_target_result_recorded_count"] + policies["restore_target_result_recorded_count"],
            "restore_scope_selected_count": requirements["restore_scope_selected_count"] + policies["restore_scope_selected_count"],
            "restore_scope_validated_count": requirements["restore_scope_validated_count"] + policies["restore_scope_validated_count"],
            "restore_authority_verified_count": requirements["restore_authority_verified_count"] + policies["restore_authority_verified_count"],
            "restore_actor_authority_granted_count": requirements["restore_actor_authority_granted_count"] + policies["restore_actor_authority_granted_count"],
            "restore_eligibility_checked_count": requirements["restore_eligibility_checked_count"] + policies["restore_eligibility_checked_count"],
            "restore_object_selected_count": requirements["restore_object_selected_count"] + policies["restore_object_selected_count"],
            "restore_request_created_count": requirements["restore_request_created_count"] + policies["restore_request_created_count"],
            "restore_request_submitted_count": requirements["restore_request_submitted_count"] + policies["restore_request_submitted_count"],
            "provider_restore_api_configured_count": requirements["provider_restore_api_configured_count"] + policies["provider_restore_api_configured_count"],
            "provider_restore_api_called_count": requirements["provider_restore_api_called_count"] + policies["provider_restore_api_called_count"],
            "provider_object_catalog_unlocked_count": requirements["provider_object_catalog_unlocked_count"] + policies["provider_object_catalog_unlocked_count"],
            "restore_job_created_count": requirements["restore_job_created_count"] + policies["restore_job_created_count"],
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
            "blocks_restore_target_selection_count": blockers["blocks_restore_target_selection_count"],
            "blocks_restore_target_validation_count": blockers["blocks_restore_target_validation_count"],
            "blocks_restore_target_result_count": blockers["blocks_restore_target_result_count"],
            "blocks_restore_object_selection_count": blockers["blocks_restore_object_selection_count"],
            "blocks_provider_object_catalog_unlock_count": blockers["blocks_provider_object_catalog_unlock_count"],
            "blocks_provider_restore_api_count": blockers["blocks_provider_restore_api_count"],
            "blocks_restore_job_count": blockers["blocks_restore_job_count"],
            "blocks_object_body_read_count": blockers["blocks_object_body_read_count"],
            "blocks_direct_upload_count": blockers["blocks_direct_upload_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "tower_review_granted_count": blockers["tower_review_granted_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp086": validation["safe_to_continue_to_gp086"],
            "foundation_status": "restore_target_lock_contract_ready_safe_to_continue_not_done",
            "restore_target_configured": contract["restore_target_configured"],
            "restore_target_attempted": contract["restore_target_attempted"],
            "restore_target_enabled": contract["restore_target_enabled"],
            "restore_target_selected": contract["restore_target_selected"],
            "restore_target_selection_started": contract["restore_target_selection_started"],
            "restore_target_selection_completed": contract["restore_target_selection_completed"],
            "restore_target_validated": contract["restore_target_validated"],
            "restore_target_passed": contract["restore_target_passed"],
            "restore_target_failed": contract["restore_target_failed"],
            "restore_target_result_recorded": contract["restore_target_result_recorded"],
            "restore_scope_selected": contract["restore_scope_selected"],
            "restore_scope_validated": contract["restore_scope_validated"],
            "restore_scope_passed": contract["restore_scope_passed"],
            "restore_scope_failed": contract["restore_scope_failed"],
            "restore_authority_verified": contract["restore_authority_verified"],
            "restore_authority_passed": contract["restore_authority_passed"],
            "restore_authority_failed": contract["restore_authority_failed"],
            "restore_actor_authority_granted": contract["restore_actor_authority_granted"],
            "restore_eligibility_checked": contract["restore_eligibility_checked"],
            "restore_eligibility_passed": contract["restore_eligibility_passed"],
            "restore_eligibility_failed": contract["restore_eligibility_failed"],
            "restore_object_selected": contract["restore_object_selected"],
            "restore_request_created": contract["restore_request_created"],
            "restore_request_submitted": contract["restore_request_submitted"],
            "restore_request_finalized": contract["restore_request_finalized"],
            "restore_job_created": contract["restore_job_created"],
            "provider_restore_api_configured": contract["provider_restore_api_configured"],
            "provider_restore_api_called": contract["provider_restore_api_called"],
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
            "clouds_status": "parked_do_not_continue_from_vault_gp085",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "restore_target_truth": home["restore_target_truth"],
        "routes": home["routes"],
        "restore_target_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }

def render_real_storage_provider_restore_target_lock_contract_page() -> str:
    home = get_real_storage_provider_restore_target_lock_contract_home()
    truth = home["restore_target_truth"]
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
<title>Vault Real Storage Provider Restore Target Lock Contract · GP085</title>
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
    <div class="eyebrow">Archive Vault · Giant Pack 085</div>
    <div class="eyebrow">Real Provider Restore and Export Governance Layer · GP081-GP090</div>
    <h1>Real Storage Provider Restore Target Lock Contract</h1>
    <p>GP085 creates real restore target rules in template-only mode. It does not select or validate a target, select objects, unlock provider catalogs, call provider APIs, read object bodies, export, upload, or execute.</p>
    <div class="grid">
      <div class="metric"><strong>{truth['requirement_count']}</strong><span>target requirements</span></div>
      <div class="metric"><strong>{truth['policy_count']}</strong><span>target policies</span></div>
      <div class="metric"><strong>{truth['restore_target_selected']}</strong><span>target selected</span></div>
      <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">Target locked</span>
      <span class="pill ok">Template-only</span>
      <span class="pill ok">Real SQLite-backed</span>
      <span class="pill danger">No target selection</span>
      <span class="pill danger">No object selection</span>
      <span class="pill danger">No provider catalog unlock</span>
      <span class="pill danger">No export</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Restore Target Requirements Preview</h2>
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
    <h2>GP085 JSON Endpoints</h2>
    <p>
      <code>{escape(routes['json_route'])}</code>
      <code>{escape(routes['record_route'])}</code>
      <code>{escape(routes['requirements_route'])}</code>
      <code>{escape(routes['policies_route'])}</code>
      <code>{escape(routes['blockers_route'])}</code>
      <code>{escape(routes['events_route'])}</code>
      <code>{escape(routes['validation_route'])}</code>
      <code>{escape(routes['next_step_route'])}</code>
      <code>{escape(routes['gp085_status_route'])}</code>
    </p>
  </section>
</main>
</body>
</html>"""
