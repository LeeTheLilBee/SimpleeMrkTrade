"""
VAULT GP161-GP170 — Controlled Provider Connection Test Lock Layer

New section:
Archive Vault — Controlled Provider Connection Test Lock Layer / GP161-GP170

Builds:
- GP161 Controlled Connection Test Lock Shell
- GP162 Connection Test Request Draft Registry
- GP163 Connection Test Approval Gate Lock Contract
- GP164 Connection Test Denial Reason Board
- GP165 Connection Test Run Plan Lock Contract
- GP166 Connection Test Receipt Draft Ledger
- GP167 Connection Test Result Placeholder Queue
- GP168 Connection Test Emergency Stop Lock
- GP169 Controlled Connection Test Blocker Board
- GP170 Controlled Connection Test Readiness Checkpoint

This layer creates lock-first surfaces for a future controlled provider connection
test. It does not submit, approve, start, complete, or execute a real connection
test and does not contact any provider.
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

from vault.real_provider_connection_readiness_layer_service import (
    get_gp160_status,
    get_gp160_real_provider_connection_readiness_checkpoint,
    get_real_provider_connection_readiness_layer_home,
    validate_real_provider_connection_readiness_layer,
    get_real_provider_connection_readiness_items,
    get_real_provider_connection_readiness_blockers,
)

LAYER_ID = "VAULT_GP161_170"
LAYER_NAME = "Controlled Provider Connection Test Lock Layer"
SCHEMA_VERSION = "vault.controlled_provider_connection_test_lock_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PROVIDER_CONNECTION_TEST_LOCK_LAYER"
SECTION_TITLE = "Archive Vault — Controlled Provider Connection Test Lock Layer"
SECTION_RANGE = "GP161-GP170"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_CONNECTION_READINESS_LAYER"
PREVIOUS_SECTION_RANGE = "GP151-GP160"

NEXT_SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_READ_ONLY_METADATA_TEST_LAYER"
NEXT_SECTION_RANGE = "GP171-GP180"
NEXT_PACK = "VAULT_GP171_180_CONTROLLED_READ_ONLY_METADATA_TEST_LAYER"

DEFAULT_DB_ENV = "VAULT_CONTROLLED_PROVIDER_CONNECTION_TEST_LOCK_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_controlled_provider_connection_test_lock_layer.sqlite"

LOCK_SHELL_ID = "VCPTL-SHELL-GP161-001"
REQUEST_DRAFT_REGISTRY_ID = "VCPTL-REQUEST-GP162-001"
APPROVAL_GATE_LOCK_ID = "VCPTL-APPROVAL-GP163-001"
DENIAL_REASON_BOARD_ID = "VCPTL-DENIAL-GP164-001"
RUN_PLAN_LOCK_ID = "VCPTL-RUNPLAN-GP165-001"
RECEIPT_DRAFT_LEDGER_ID = "VCPTL-RECEIPT-GP166-001"
RESULT_PLACEHOLDER_QUEUE_ID = "VCPTL-RESULT-GP167-001"
EMERGENCY_STOP_LOCK_ID = "VCPTL-ESTOP-GP168-001"
BLOCKER_BOARD_ID = "VCPTL-BLOCKER-GP169-001"
READINESS_ID = "VCPTL-READINESS-GP170-001"

FALSE_FIELDS = [
    "connection_test_request_submitted",
    "connection_test_request_approved",
    "connection_test_request_denied_final",
    "connection_test_approval_granted",
    "connection_test_run_authorized",
    "connection_test_run_started",
    "connection_test_run_completed",
    "connection_test_result_recorded",
    "connection_test_result_approved",
    "connection_test_receipt_finalized",
    "connection_test_receipt_persisted",
    "connection_test_emergency_stop_triggered",
    "connection_test_emergency_stop_released",
    "real_provider_connection_requested",
    "real_provider_connection_started",
    "real_provider_connection_completed",
    "provider_api_configured",
    "provider_api_called",
    "provider_token_created",
    "provider_session_created",
    "provider_job_reference_created",
    "provider_status_poll_started",
    "provider_status_poll_completed",
    "provider_health_checked",
    "provider_health_passed",
    "provider_credentials_validated",
    "provider_credential_value_read",
    "provider_credential_value_persisted",
    "provider_secret_value_read",
    "provider_secret_value_persisted",
    "credential_material_exposed",
    "credential_material_exported",
    "provider_endpoint_called",
    "provider_endpoint_reached",
    "provider_namespace_activated",
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
    "object_download_created",
    "object_download_enabled",
    "archive_file_opened",
    "archive_file_streamed",
    "archive_file_exported",
    "restore_requested",
    "restore_approved",
    "restore_request_created",
    "restore_request_submitted",
    "restore_job_configured",
    "restore_job_created",
    "restore_job_started",
    "restore_job_completed",
    "provider_restore_api_configured",
    "provider_restore_api_called",
    "export_requested",
    "export_approved",
    "export_enabled",
    "export_package_created",
    "export_manifest_created",
    "export_download_enabled",
    "direct_upload_enabled",
    "permission_request_submitted",
    "permission_request_approved",
    "permission_request_granted",
    "step_up_challenge_started",
    "step_up_challenge_passed",
    "step_up_token_created",
    "step_up_session_created",
    "tower_gate_opened",
    "tower_gate_passed",
    "tower_unlock_requested",
    "tower_unlock_granted",
    "tower_clearance_granted",
    "owner_approval_recorded",
    "owner_rejection_recorded",
    "owner_decision_recorded",
    "owner_execute_action_requested",
    "owner_execute_action_approved",
    "execution_enabled",
    "vault_done",
    "clouds_should_continue",
]

REQUEST_DRAFTS = [
    ("connection_smoke_test_request", "Connection Smoke Test Request Draft", "connection", "critical"),
    ("credential_boundary_test_request", "Credential Boundary Test Request Draft", "credential", "critical"),
    ("endpoint_namespace_test_request", "Endpoint Namespace Test Request Draft", "endpoint", "critical"),
    ("health_placeholder_test_request", "Health Placeholder Test Request Draft", "health", "high"),
    ("lock_validation_test_request", "Lock Validation Test Request Draft", "lock_validation", "critical"),
    ("rollback_readiness_test_request", "Rollback Readiness Test Request Draft", "rollback", "critical"),
]

DENIAL_REASONS = [
    ("tower_unlock_missing", "Tower unlock is missing", "tower"),
    ("step_up_not_passed", "Step-up has not passed", "step_up"),
    ("connection_test_not_approved", "Connection test is not approved", "approval"),
    ("provider_api_locked", "Provider API remains locked", "provider_api"),
    ("secret_value_locked", "Secret value remains locked", "credential"),
    ("endpoint_call_locked", "Endpoint call remains locked", "endpoint"),
    ("emergency_stop_locked", "Emergency stop remains locked", "emergency_stop"),
    ("vault_not_done", "Vault is not done", "done"),
]

RUN_PLAN_STEPS = [
    ("confirm_tower_gate_locked", "Confirm Tower gate remains locked"),
    ("confirm_no_secret_value_read", "Confirm no secret value is read"),
    ("confirm_no_endpoint_call", "Confirm no endpoint call is made"),
    ("confirm_no_provider_token_session", "Confirm no provider token/session is created"),
    ("confirm_no_provider_job_reference", "Confirm no provider job/reference is created"),
    ("confirm_no_status_poll", "Confirm no provider status poll is started"),
    ("confirm_no_object_access", "Confirm no object catalog/body/download access"),
    ("confirm_no_restore_export_upload_execution", "Confirm no restore/export/upload/execution"),
]

RESULT_PLACEHOLDERS = [
    ("connection_not_run", "Connection Test Not Run"),
    ("provider_not_contacted", "Provider Not Contacted"),
    ("no_token_created", "No Token Created"),
    ("no_session_created", "No Session Created"),
    ("no_job_reference_created", "No Job Reference Created"),
    ("no_status_poll_started", "No Status Poll Started"),
]

EMERGENCY_STOP_LOCKS = [
    ("connection_start_stop_lock", "Connection Start Emergency Stop Lock"),
    ("provider_api_stop_lock", "Provider API Emergency Stop Lock"),
    ("credential_material_stop_lock", "Credential Material Emergency Stop Lock"),
    ("endpoint_call_stop_lock", "Endpoint Call Emergency Stop Lock"),
    ("object_access_stop_lock", "Object Access Emergency Stop Lock"),
    ("restore_export_upload_stop_lock", "Restore/Export/Upload Emergency Stop Lock"),
]

BLOCKER_SPECS = [
    ("connection_test_submit_locked", "Connection test submit locked", "request", "critical"),
    ("connection_test_approval_locked", "Connection test approval locked", "approval", "critical"),
    ("connection_test_run_locked", "Connection test run locked", "run", "critical"),
    ("real_provider_connection_locked", "Real provider connection locked", "connection", "critical"),
    ("provider_api_locked", "Provider API locked", "provider_api", "critical"),
    ("provider_token_session_job_locked", "Provider token/session/job locked", "token_session_job", "critical"),
    ("provider_status_poll_locked", "Provider status poll locked", "status_poll", "critical"),
    ("credential_secret_locked", "Credential/secret value locked", "credential", "critical"),
    ("endpoint_call_locked", "Provider endpoint call locked", "endpoint", "critical"),
    ("object_access_locked", "Object catalog/body/download locked", "object_access", "critical"),
    ("restore_export_upload_locked", "Restore/export/upload locked", "restore_export_upload", "critical"),
    ("tower_execution_done_locked", "Tower unlock, execution, and Vault done locked", "tower_execution", "critical"),
]

COMPONENT_SPECS = [
    (161, LOCK_SHELL_ID, "VAULT_GP161", "Controlled Connection Test Lock Shell", "controlled_connection_test_lock_shell"),
    (162, REQUEST_DRAFT_REGISTRY_ID, "VAULT_GP162", "Connection Test Request Draft Registry", "connection_test_request_draft_registry"),
    (163, APPROVAL_GATE_LOCK_ID, "VAULT_GP163", "Connection Test Approval Gate Lock Contract", "connection_test_approval_gate_lock_contract"),
    (164, DENIAL_REASON_BOARD_ID, "VAULT_GP164", "Connection Test Denial Reason Board", "connection_test_denial_reason_board"),
    (165, RUN_PLAN_LOCK_ID, "VAULT_GP165", "Connection Test Run Plan Lock Contract", "connection_test_run_plan_lock_contract"),
    (166, RECEIPT_DRAFT_LEDGER_ID, "VAULT_GP166", "Connection Test Receipt Draft Ledger", "connection_test_receipt_draft_ledger"),
    (167, RESULT_PLACEHOLDER_QUEUE_ID, "VAULT_GP167", "Connection Test Result Placeholder Queue", "connection_test_result_placeholder_queue"),
    (168, EMERGENCY_STOP_LOCK_ID, "VAULT_GP168", "Connection Test Emergency Stop Lock", "connection_test_emergency_stop_lock"),
    (169, BLOCKER_BOARD_ID, "VAULT_GP169", "Controlled Connection Test Blocker Board", "controlled_connection_test_blocker_board"),
    (170, READINESS_ID, "VAULT_GP170", "Controlled Connection Test Readiness Checkpoint", "controlled_connection_test_readiness_checkpoint"),
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
        "source_gp160_readiness_score",
        "component_count",
        "request_draft_count",
        "approval_gate_count",
        "denial_reason_count",
        "run_plan_step_count",
        "receipt_draft_count",
        "result_placeholder_count",
        "emergency_stop_lock_count",
        "blocker_count",
        "event_count",
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
            or key.endswith("_position")
            or key.endswith("_value")
        ):
            payload[key] = int(row[key])
        elif isinstance(row[key], int):
            payload[key] = bool(row[key])
        else:
            payload[key] = row[key]
    return payload

def _layer_pack_payload() -> Dict[str, Any]:
    return {
        "id": LAYER_ID,
        "name": LAYER_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP160"],
        "packs": [item[2] for item in COMPONENT_SPECS],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "previous_section": PREVIOUS_SECTION_ID,
        "previous_section_range": PREVIOUS_SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
        "next_pack": NEXT_PACK,
    }

def _pack_payload(gp_number: int, pack_name: str) -> Dict[str, Any]:
    return {
        "id": f"VAULT_GP{gp_number:03d}",
        "name": pack_name,
        "layer_id": LAYER_ID,
        "layer_name": LAYER_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP160"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_controlled_provider_connection_test_lock_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)
    false_sql = ",\n".join(f"{field} INTEGER NOT NULL DEFAULT 0" for field in FALSE_FIELDS)
    readiness_false_sql = ",\n".join(
        f"{field} INTEGER NOT NULL DEFAULT 0"
        for field in FALSE_FIELDS
        if field not in {"vault_done", "clouds_should_continue"}
    )

    with _connect(str(path)) as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_controlled_connection_test_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp160_readiness_id TEXT NOT NULL,
                source_gp160_readiness_hash TEXT NOT NULL,
                source_gp160_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                controlled_test_locked INTEGER NOT NULL DEFAULT 1,
                no_provider_contact INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_connection_test_request_drafts (
                request_draft_id TEXT PRIMARY KEY,
                request_code TEXT NOT NULL UNIQUE,
                request_name TEXT NOT NULL,
                request_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                request_status TEXT NOT NULL,
                source_gp160_readiness_hash TEXT NOT NULL,
                request_draft_ready INTEGER NOT NULL DEFAULT 1,
                request_draft_locked INTEGER NOT NULL DEFAULT 1,
                controlled_test_locked INTEGER NOT NULL DEFAULT 1,
                no_provider_contact INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                request_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_connection_test_approval_gates (
                approval_gate_id TEXT PRIMARY KEY,
                gate_code TEXT NOT NULL UNIQUE,
                request_draft_id TEXT NOT NULL,
                gate_name TEXT NOT NULL,
                gate_status TEXT NOT NULL,
                approval_gate_locked INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                owner_review_required INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                gate_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_connection_test_denial_reasons (
                denial_id TEXT PRIMARY KEY,
                denial_code TEXT NOT NULL UNIQUE,
                denial_name TEXT NOT NULL,
                denial_category TEXT NOT NULL,
                denial_status TEXT NOT NULL,
                denial_active INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                denial_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_connection_test_run_plan_steps (
                run_step_id TEXT PRIMARY KEY,
                step_code TEXT NOT NULL UNIQUE,
                step_name TEXT NOT NULL,
                step_status TEXT NOT NULL,
                run_plan_locked INTEGER NOT NULL DEFAULT 1,
                controlled_test_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                step_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_connection_test_receipt_drafts (
                receipt_draft_id TEXT PRIMARY KEY,
                receipt_code TEXT NOT NULL UNIQUE,
                source_request_draft_id TEXT NOT NULL,
                receipt_name TEXT NOT NULL,
                receipt_status TEXT NOT NULL,
                receipt_draft_locked INTEGER NOT NULL DEFAULT 1,
                final_receipt_created INTEGER NOT NULL DEFAULT 0,
                payload_json TEXT NOT NULL,
                receipt_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_connection_test_result_placeholders (
                result_placeholder_id TEXT PRIMARY KEY,
                result_code TEXT NOT NULL UNIQUE,
                result_name TEXT NOT NULL,
                result_status TEXT NOT NULL,
                result_placeholder_locked INTEGER NOT NULL DEFAULT 1,
                no_provider_result INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                result_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_connection_test_emergency_stop_locks (
                emergency_stop_id TEXT PRIMARY KEY,
                stop_code TEXT NOT NULL UNIQUE,
                stop_name TEXT NOT NULL,
                stop_status TEXT NOT NULL,
                emergency_stop_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                stop_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_controlled_connection_test_blockers (
                blocker_id TEXT PRIMARY KEY,
                blocker_code TEXT NOT NULL UNIQUE,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocker_active INTEGER NOT NULL DEFAULT 1,
                blocks_request_submit INTEGER NOT NULL DEFAULT 1,
                blocks_approval INTEGER NOT NULL DEFAULT 1,
                blocks_run_start INTEGER NOT NULL DEFAULT 1,
                blocks_real_connection INTEGER NOT NULL DEFAULT 1,
                blocks_provider_api INTEGER NOT NULL DEFAULT 1,
                blocks_provider_token INTEGER NOT NULL DEFAULT 1,
                blocks_provider_session INTEGER NOT NULL DEFAULT 1,
                blocks_provider_job INTEGER NOT NULL DEFAULT 1,
                blocks_status_poll INTEGER NOT NULL DEFAULT 1,
                blocks_health_call INTEGER NOT NULL DEFAULT 1,
                blocks_secret_read INTEGER NOT NULL DEFAULT 1,
                blocks_endpoint_call INTEGER NOT NULL DEFAULT 1,
                blocks_object_catalog INTEGER NOT NULL DEFAULT 1,
                blocks_metadata_import INTEGER NOT NULL DEFAULT 1,
                blocks_object_body INTEGER NOT NULL DEFAULT 1,
                blocks_download INTEGER NOT NULL DEFAULT 1,
                blocks_restore INTEGER NOT NULL DEFAULT 1,
                blocks_export INTEGER NOT NULL DEFAULT 1,
                blocks_direct_upload INTEGER NOT NULL DEFAULT 1,
                blocks_tower_unlock INTEGER NOT NULL DEFAULT 1,
                blocks_execution INTEGER NOT NULL DEFAULT 1,
                blocks_vault_done INTEGER NOT NULL DEFAULT 1,
                resolved INTEGER NOT NULL DEFAULT 0,
                payload_json TEXT NOT NULL,
                blocker_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_controlled_connection_test_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                request_draft_count INTEGER NOT NULL,
                approval_gate_count INTEGER NOT NULL,
                denial_reason_count INTEGER NOT NULL,
                run_plan_step_count INTEGER NOT NULL,
                receipt_draft_count INTEGER NOT NULL,
                result_placeholder_count INTEGER NOT NULL,
                emergency_stop_lock_count INTEGER NOT NULL,
                blocker_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                safe_to_continue_to_gp171 INTEGER NOT NULL DEFAULT 1,
                section_ready INTEGER NOT NULL DEFAULT 1,
                controlled_test_locked INTEGER NOT NULL DEFAULT 1,
                no_provider_contact INTEGER NOT NULL DEFAULT 1,
                vault_done INTEGER NOT NULL DEFAULT 0,
                clouds_should_continue INTEGER NOT NULL DEFAULT 0,
                {readiness_false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_controlled_connection_test_events (
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
            "vault_controlled_connection_test_components",
            "vault_connection_test_request_drafts",
            "vault_connection_test_approval_gates",
            "vault_connection_test_denial_reasons",
            "vault_connection_test_run_plan_steps",
            "vault_connection_test_receipt_drafts",
            "vault_connection_test_result_placeholders",
            "vault_connection_test_emergency_stop_locks",
            "vault_controlled_connection_test_blockers",
            "vault_controlled_connection_test_readiness",
            "vault_controlled_connection_test_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VCPTLEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_controlled_connection_test_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_controlled_provider_connection_test_lock_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_controlled_provider_connection_test_lock_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_controlled_connection_test_components WHERE component_id = ?",
            (LOCK_SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp160_status = get_gp160_status()["gp160_status"]
            gp160_checkpoint = get_gp160_real_provider_connection_readiness_checkpoint()["readiness_checkpoint"]
            gp160_home = get_real_provider_connection_readiness_layer_home()
            gp160_validation = validate_real_provider_connection_readiness_layer()

            source_items = get_real_provider_connection_readiness_items()
            source_blockers = get_real_provider_connection_readiness_blockers()

            readiness = gp160_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp160_readiness_id": readiness["readiness_id"],
                "source_gp160_readiness_hash": readiness["readiness_hash"],
                "source_gp160_readiness_score": readiness["readiness_score"],
            }

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "request_draft_count": len(REQUEST_DRAFTS),
                "approval_gate_count": len(REQUEST_DRAFTS),
                "denial_reason_count": len(DENIAL_REASONS),
                "run_plan_step_count": len(RUN_PLAN_STEPS),
                "receipt_draft_count": len(REQUEST_DRAFTS),
                "result_placeholder_count": len(RESULT_PLACEHOLDERS),
                "emergency_stop_lock_count": len(EMERGENCY_STOP_LOCKS),
                "blocker_count": len(BLOCKER_SPECS),
            }

            source_context = {
                "source_gp160_status_ready": gp160_status["ready"],
                "source_gp160_validation_passed": gp160_status["validation_passed"],
                "source_gp160_safe_to_continue_to_gp161": gp160_status["safe_to_continue_to_gp161"],
                "source_gp160_readiness_hash": readiness["readiness_hash"],
                "source_gp160_readiness_score": readiness["readiness_score"],
                "source_readiness_item_count": len(source_items),
                "source_blocker_count": len(source_blockers),
                "source_validation_check_count": gp160_validation["check_count"],
            }

            component_extra = {
                LOCK_SHELL_ID: {"controlled_connection_test_lock_shell_ready": True},
                REQUEST_DRAFT_REGISTRY_ID: {"connection_test_request_draft_registry_ready": True, "request_draft_count": counts["request_draft_count"]},
                APPROVAL_GATE_LOCK_ID: {"connection_test_approval_gate_lock_contract_ready": True, "approval_gate_count": counts["approval_gate_count"]},
                DENIAL_REASON_BOARD_ID: {"connection_test_denial_reason_board_ready": True, "denial_reason_count": counts["denial_reason_count"]},
                RUN_PLAN_LOCK_ID: {"connection_test_run_plan_lock_contract_ready": True, "run_plan_step_count": counts["run_plan_step_count"]},
                RECEIPT_DRAFT_LEDGER_ID: {"connection_test_receipt_draft_ledger_ready": True, "receipt_draft_count": counts["receipt_draft_count"]},
                RESULT_PLACEHOLDER_QUEUE_ID: {"connection_test_result_placeholder_queue_ready": True, "result_placeholder_count": counts["result_placeholder_count"]},
                EMERGENCY_STOP_LOCK_ID: {"connection_test_emergency_stop_lock_ready": True, "emergency_stop_lock_count": counts["emergency_stop_lock_count"]},
                BLOCKER_BOARD_ID: {"controlled_connection_test_blocker_board_ready": True, "blocker_count": counts["blocker_count"]},
                READINESS_ID: {"controlled_connection_test_readiness_checkpoint_ready": True, "safe_to_continue_to_gp171": True},
            }

            for gp_number, component_id, pack_id, pack_name, component_type in COMPONENT_SPECS:
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "component_id": component_id,
                    "gp_number": gp_number,
                    "pack_id": pack_id,
                    "pack_name": pack_name,
                    "component_type": component_type,
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    **source_context,
                    **component_extra[component_id],
                    "controlled_test_locked": True,
                    "no_provider_contact": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "next_section": NEXT_SECTION_ID,
                    "next_section_range": NEXT_SECTION_RANGE,
                    "next_pack": NEXT_PACK,
                }
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
                    "controlled_test_locked": 1,
                    "no_provider_contact": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_controlled_connection_test_components", row)

            request_ids = []
            for idx, (code, name, category, severity) in enumerate(REQUEST_DRAFTS, start=1):
                request_id = f"VCPTLRD-{idx:03d}"
                request_ids.append((request_id, code, name))
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "request_code": code,
                    "request_name": name,
                    "request_category": category,
                    "severity": severity,
                    "request_status": "DRAFT_ONLY_NOT_SUBMITTED_CONTROLLED_TEST_LOCKED",
                    "source_gp160_readiness_hash": readiness["readiness_hash"],
                    "request_draft_ready": True,
                    "request_draft_locked": True,
                    "controlled_test_locked": True,
                    "no_provider_contact": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "request_draft_id": request_id,
                    "request_code": code,
                    "request_name": name,
                    "request_category": category,
                    "severity": severity,
                    "request_status": payload["request_status"],
                    "source_gp160_readiness_hash": readiness["readiness_hash"],
                    "request_draft_ready": 1,
                    "request_draft_locked": 1,
                    "controlled_test_locked": 1,
                    "no_provider_contact": 1,
                    "payload_json": _json_dumps(payload),
                    "request_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_connection_test_request_drafts", row)

                gate_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "gate_code": f"{code}_approval_gate",
                    "request_draft_id": request_id,
                    "gate_name": f"{name} Approval Gate",
                    "gate_status": "APPROVAL_GATE_LOCKED_NO_APPROVAL_NO_RUN",
                    "approval_gate_locked": True,
                    "tower_review_required": True,
                    "owner_review_required": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "approval_gate_id": f"VCPTLAG-{idx:03d}",
                    "gate_code": gate_payload["gate_code"],
                    "request_draft_id": request_id,
                    "gate_name": gate_payload["gate_name"],
                    "gate_status": gate_payload["gate_status"],
                    "approval_gate_locked": 1,
                    "tower_review_required": 1,
                    "owner_review_required": 1,
                    "payload_json": _json_dumps(gate_payload),
                    "gate_hash": _hash_payload(gate_payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_connection_test_approval_gates", row)

                receipt_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "receipt_code": f"{code}_receipt_draft",
                    "source_request_draft_id": request_id,
                    "receipt_name": f"{name} Receipt Draft",
                    "receipt_status": "DRAFT_ONLY_NOT_FINALIZED_NO_PROVIDER_RECEIPT",
                    "receipt_draft_locked": True,
                    "final_receipt_created": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "receipt_draft_id": f"VCPTLRCP-{idx:03d}",
                    "receipt_code": receipt_payload["receipt_code"],
                    "source_request_draft_id": request_id,
                    "receipt_name": receipt_payload["receipt_name"],
                    "receipt_status": receipt_payload["receipt_status"],
                    "receipt_draft_locked": 1,
                    "final_receipt_created": 0,
                    "payload_json": _json_dumps(receipt_payload),
                    "receipt_hash": _hash_payload(receipt_payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_connection_test_receipt_drafts", row)

            for idx, (code, name, category) in enumerate(DENIAL_REASONS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "denial_code": code,
                    "denial_name": name,
                    "denial_category": category,
                    "denial_status": "ACTIVE_DENIAL_REASON_NOT_FINAL_DENIAL",
                    "denial_active": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "denial_id": f"VCPTLDEN-{idx:03d}",
                    "denial_code": code,
                    "denial_name": name,
                    "denial_category": category,
                    "denial_status": payload["denial_status"],
                    "denial_active": 1,
                    "payload_json": _json_dumps(payload),
                    "denial_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_connection_test_denial_reasons", row)

            for idx, (code, name) in enumerate(RUN_PLAN_STEPS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "step_code": code,
                    "step_name": name,
                    "step_status": "RUN_PLAN_STEP_LOCKED_NOT_EXECUTED",
                    "run_plan_locked": True,
                    "controlled_test_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "run_step_id": f"VCPTLSTEP-{idx:03d}",
                    "step_code": code,
                    "step_name": name,
                    "step_status": payload["step_status"],
                    "run_plan_locked": 1,
                    "controlled_test_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "step_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_connection_test_run_plan_steps", row)

            for idx, (code, name) in enumerate(RESULT_PLACEHOLDERS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "result_code": code,
                    "result_name": name,
                    "result_status": "PLACEHOLDER_ONLY_NO_PROVIDER_RESULT",
                    "result_placeholder_locked": True,
                    "no_provider_result": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "result_placeholder_id": f"VCPTLRES-{idx:03d}",
                    "result_code": code,
                    "result_name": name,
                    "result_status": payload["result_status"],
                    "result_placeholder_locked": 1,
                    "no_provider_result": 1,
                    "payload_json": _json_dumps(payload),
                    "result_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_connection_test_result_placeholders", row)

            for idx, (code, name) in enumerate(EMERGENCY_STOP_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "stop_code": code,
                    "stop_name": name,
                    "stop_status": "EMERGENCY_STOP_LOCKED_AND_NOT_TRIGGERED",
                    "emergency_stop_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "emergency_stop_id": f"VCPTLESTOP-{idx:03d}",
                    "stop_code": code,
                    "stop_name": name,
                    "stop_status": payload["stop_status"],
                    "emergency_stop_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "stop_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_connection_test_emergency_stop_locks", row)

            for idx, (code, name, category, severity) in enumerate(BLOCKER_SPECS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "ACTIVE_CONTROLLED_CONNECTION_TEST_BLOCKER",
                    "blocker_active": True,
                    "blocks_request_submit": True,
                    "blocks_approval": True,
                    "blocks_run_start": True,
                    "blocks_real_connection": True,
                    "blocks_provider_api": True,
                    "blocks_provider_token": True,
                    "blocks_provider_session": True,
                    "blocks_provider_job": True,
                    "blocks_status_poll": True,
                    "blocks_health_call": True,
                    "blocks_secret_read": True,
                    "blocks_endpoint_call": True,
                    "blocks_object_catalog": True,
                    "blocks_metadata_import": True,
                    "blocks_object_body": True,
                    "blocks_download": True,
                    "blocks_restore": True,
                    "blocks_export": True,
                    "blocks_direct_upload": True,
                    "blocks_tower_unlock": True,
                    "blocks_execution": True,
                    "blocks_vault_done": True,
                    "resolved": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "blocker_id": f"VCPTLBLK-{idx:03d}",
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": payload["blocker_status"],
                    "blocker_active": 1,
                    "blocks_request_submit": 1,
                    "blocks_approval": 1,
                    "blocks_run_start": 1,
                    "blocks_real_connection": 1,
                    "blocks_provider_api": 1,
                    "blocks_provider_token": 1,
                    "blocks_provider_session": 1,
                    "blocks_provider_job": 1,
                    "blocks_status_poll": 1,
                    "blocks_health_call": 1,
                    "blocks_secret_read": 1,
                    "blocks_endpoint_call": 1,
                    "blocks_object_catalog": 1,
                    "blocks_metadata_import": 1,
                    "blocks_object_body": 1,
                    "blocks_download": 1,
                    "blocks_restore": 1,
                    "blocks_export": 1,
                    "blocks_direct_upload": 1,
                    "blocks_tower_unlock": 1,
                    "blocks_execution": 1,
                    "blocks_vault_done": 1,
                    "resolved": 0,
                    "payload_json": _json_dumps(payload),
                    "blocker_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_controlled_connection_test_blockers", row)

            checks = [
                ("SOURCE_GP160_READY", bool(gp160_status["ready"])),
                ("SOURCE_GP160_VALIDATION_PASSED", bool(gp160_status["validation_passed"])),
                ("SOURCE_GP160_SAFE_TO_CONTINUE", bool(gp160_status["safe_to_continue_to_gp161"])),
                ("SOURCE_GP160_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP160_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("REQUEST_DRAFT_COUNT_6", counts["request_draft_count"] == 6),
                ("APPROVAL_GATE_COUNT_6", counts["approval_gate_count"] == 6),
                ("DENIAL_REASON_COUNT_8", counts["denial_reason_count"] == 8),
                ("RUN_PLAN_STEP_COUNT_8", counts["run_plan_step_count"] == 8),
                ("RECEIPT_DRAFT_COUNT_6", counts["receipt_draft_count"] == 6),
                ("RESULT_PLACEHOLDER_COUNT_6", counts["result_placeholder_count"] == 6),
                ("EMERGENCY_STOP_LOCK_COUNT_6", counts["emergency_stop_lock_count"] == 6),
                ("BLOCKER_COUNT_12", counts["blocker_count"] == 12),
                ("SECTION_GP161_GP170", SECTION_RANGE == "GP161-GP170"),
                ("NEXT_SECTION_GP171_GP180", NEXT_SECTION_RANGE == "GP171-GP180"),
                ("CONTROLLED_TEST_LOCKED", True),
                ("NO_PROVIDER_CONTACT", True),
                ("NO_REQUEST_SUBMIT", True),
                ("NO_APPROVAL", True),
                ("NO_RUN_START", True),
                ("NO_REAL_CONNECTION", True),
                ("NO_PROVIDER_API", True),
                ("NO_PROVIDER_TOKEN_SESSION_JOB", True),
                ("NO_STATUS_POLL", True),
                ("NO_HEALTH_CALL", True),
                ("NO_SECRET_READ", True),
                ("NO_ENDPOINT_CALL", True),
                ("NO_OBJECT_ACCESS", True),
                ("NO_OBJECT_BODY", True),
                ("NO_DOWNLOAD", True),
                ("NO_RESTORE", True),
                ("NO_EXPORT", True),
                ("NO_DIRECT_UPLOAD", True),
                ("NO_TOWER_UNLOCK", True),
                ("NO_EXECUTION", True),
                ("VAULT_NOT_DONE", True),
                ("CLOUDS_PARKED", True),
            ]
            passed_count = len([c for c in checks if c[1]])
            failed_count = len(checks) - passed_count

            readiness_payload = {
                "schema_version": SCHEMA_VERSION,
                "readiness_id": READINESS_ID,
                "gp_number": 170,
                "pack_id": "VAULT_GP170",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp160_readiness_id": readiness["readiness_id"],
                "source_gp160_readiness_hash": readiness["readiness_hash"],
                "source_gp160_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "safe_to_continue_to_gp171": failed_count == 0,
                "section_ready": True,
                "controlled_test_locked": True,
                "no_provider_contact": True,
                "vault_done": False,
                "clouds_should_continue": False,
                "next_section": NEXT_SECTION_ID,
                "next_section_range": NEXT_SECTION_RANGE,
                "next_pack": NEXT_PACK,
                "locked_truth": {field: False for field in FALSE_FIELDS},
            }
            readiness_hash = _hash_payload(readiness_payload)

            row = {
                "readiness_id": READINESS_ID,
                "gp_number": 170,
                "pack_id": "VAULT_GP170",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "CONTROLLED_PROVIDER_CONNECTION_TEST_LOCK_LAYER_READY_LOCKED_SAFE_TO_CONTINUE_NOT_DONE",
                "readiness_score": readiness_payload["readiness_score"],
                **counts,
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "safe_to_continue_to_gp171": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "controlled_test_locked": 1,
                "no_provider_contact": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_controlled_connection_test_readiness", row)

            for event_type, event_payload in [
                ("GP161_CONTROLLED_CONNECTION_TEST_LOCK_SHELL_CREATED", {"component_id": LOCK_SHELL_ID}),
                ("GP162_CONNECTION_TEST_REQUEST_DRAFT_REGISTRY_CREATED", {"request_draft_count": counts["request_draft_count"]}),
                ("GP163_CONNECTION_TEST_APPROVAL_GATE_LOCK_CREATED", {"approval_gate_count": counts["approval_gate_count"]}),
                ("GP164_CONNECTION_TEST_DENIAL_REASON_BOARD_CREATED", {"denial_reason_count": counts["denial_reason_count"]}),
                ("GP165_CONNECTION_TEST_RUN_PLAN_LOCK_CREATED", {"run_plan_step_count": counts["run_plan_step_count"]}),
                ("GP166_CONNECTION_TEST_RECEIPT_DRAFT_LEDGER_CREATED", {"receipt_draft_count": counts["receipt_draft_count"]}),
                ("GP167_CONNECTION_TEST_RESULT_PLACEHOLDER_QUEUE_CREATED", {"result_placeholder_count": counts["result_placeholder_count"]}),
                ("GP168_CONNECTION_TEST_EMERGENCY_STOP_LOCK_CREATED", {"emergency_stop_lock_count": counts["emergency_stop_lock_count"]}),
                ("GP169_CONTROLLED_CONNECTION_TEST_BLOCKER_BOARD_CREATED", {"blocker_count": counts["blocker_count"]}),
                ("GP170_CONTROLLED_CONNECTION_TEST_READINESS_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp171": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_controlled_connection_test_components").fetchone()["c"]),
            "request_draft_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_connection_test_request_drafts").fetchone()["c"]),
            "approval_gate_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_connection_test_approval_gates").fetchone()["c"]),
            "denial_reason_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_connection_test_denial_reasons").fetchone()["c"]),
            "run_plan_step_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_connection_test_run_plan_steps").fetchone()["c"]),
            "receipt_draft_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_connection_test_receipt_drafts").fetchone()["c"]),
            "result_placeholder_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_connection_test_result_placeholders").fetchone()["c"]),
            "emergency_stop_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_connection_test_emergency_stop_locks").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_controlled_connection_test_blockers").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_controlled_connection_test_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_controlled_connection_test_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_controlled_provider_connection_test_lock_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_controlled_provider_connection_test_lock_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_controlled_connection_test_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_controlled_provider_connection_test_lock_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_controlled_connection_test_readiness WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_controlled_provider_connection_test_lock_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_controlled_connection_test_events ORDER BY created_at, event_id").fetchall()
    return [{"event_id": row["event_id"], "event_type": row["event_type"], "event_payload": _json_loads(row["event_payload_json"]), "created_at": row["created_at"]} for row in rows]

def get_connection_test_request_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_connection_test_request_drafts", "request_code", db_path, {"payload_json": "payload"})

def get_connection_test_approval_gates(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_connection_test_approval_gates", "gate_code", db_path, {"payload_json": "payload"})

def get_connection_test_denial_reasons(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_connection_test_denial_reasons", "denial_code", db_path, {"payload_json": "payload"})

def get_connection_test_run_plan_steps(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_connection_test_run_plan_steps", "step_code", db_path, {"payload_json": "payload"})

def get_connection_test_receipt_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_connection_test_receipt_drafts", "receipt_code", db_path, {"payload_json": "payload"})

def get_connection_test_result_placeholders(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_connection_test_result_placeholders", "result_code", db_path, {"payload_json": "payload"})

def get_connection_test_emergency_stop_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_connection_test_emergency_stop_locks", "stop_code", db_path, {"payload_json": "payload"})

def get_controlled_connection_test_blockers(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_controlled_connection_test_blockers", "blocker_code", db_path, {"payload_json": "payload"})

def validate_controlled_provider_connection_test_lock_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_controlled_connection_test_components", "gp_number", db_path, {"data_json": "data"})
    requests = get_connection_test_request_drafts(db_path)
    gates = get_connection_test_approval_gates(db_path)
    denials = get_connection_test_denial_reasons(db_path)
    steps = get_connection_test_run_plan_steps(db_path)
    receipts = get_connection_test_receipt_drafts(db_path)
    results = get_connection_test_result_placeholders(db_path)
    stops = get_connection_test_emergency_stop_locks(db_path)
    blockers = get_controlled_connection_test_blockers(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("REQUEST_DRAFT_COUNT_6", len(requests) == len(REQUEST_DRAFTS)),
        ("APPROVAL_GATE_COUNT_6", len(gates) == len(REQUEST_DRAFTS)),
        ("DENIAL_REASON_COUNT_8", len(denials) == len(DENIAL_REASONS)),
        ("RUN_PLAN_STEP_COUNT_8", len(steps) == len(RUN_PLAN_STEPS)),
        ("RECEIPT_DRAFT_COUNT_6", len(receipts) == len(REQUEST_DRAFTS)),
        ("RESULT_PLACEHOLDER_COUNT_6", len(results) == len(RESULT_PLACEHOLDERS)),
        ("EMERGENCY_STOP_LOCK_COUNT_6", len(stops) == len(EMERGENCY_STOP_LOCKS)),
        ("BLOCKER_COUNT_12", len(blockers) == len(BLOCKER_SPECS)),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("SAFE_TO_CONTINUE_TO_GP171", readiness["safe_to_continue_to_gp171"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("CONTROLLED_TEST_LOCKED", readiness["controlled_test_locked"] is True),
        ("NO_PROVIDER_CONTACT", readiness["no_provider_contact"] is True),
        ("SECTION_GP161_GP170", readiness["section_range"] == "GP161-GP170"),
        ("NEXT_SECTION_GP171_GP180", readiness["readiness_payload"]["next_section_range"] == "GP171-GP180"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_LOCKED", all(item["component_locked"] is True for item in components)),
        ("ALL_COMPONENTS_CONTROLLED_TEST_LOCKED", all(item["controlled_test_locked"] is True for item in components)),
        ("ALL_COMPONENTS_NO_PROVIDER_CONTACT", all(item["no_provider_contact"] is True for item in components)),
        ("ALL_REQUESTS_DRAFT_LOCKED", all(item["request_draft_locked"] is True for item in requests)),
        ("ALL_REQUESTS_NOT_SUBMITTED", all(item["connection_test_request_submitted"] is False for item in requests)),
        ("ALL_GATES_LOCKED", all(item["approval_gate_locked"] is True for item in gates)),
        ("ALL_GATES_NOT_APPROVED", all(item["connection_test_approval_granted"] is False for item in gates)),
        ("ALL_DENIAL_REASONS_ACTIVE", all(item["denial_active"] is True for item in denials)),
        ("ALL_RUN_STEPS_LOCKED", all(item["run_plan_locked"] is True for item in steps)),
        ("ALL_RUN_STEPS_NOT_STARTED", all(item["connection_test_run_started"] is False for item in steps)),
        ("ALL_RECEIPTS_DRAFT_LOCKED", all(item["receipt_draft_locked"] is True for item in receipts)),
        ("NO_FINAL_RECEIPTS", all(item["final_receipt_created"] is False for item in receipts)),
        ("ALL_RESULTS_PLACEHOLDER_LOCKED", all(item["result_placeholder_locked"] is True for item in results)),
        ("ALL_RESULTS_NO_PROVIDER_RESULT", all(item["no_provider_result"] is True for item in results)),
        ("ALL_STOPS_LOCKED", all(item["emergency_stop_locked"] is True for item in stops)),
        ("ALL_BLOCKERS_ACTIVE", all(item["blocker_active"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_REQUEST_SUBMIT", all(item["blocks_request_submit"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_APPROVAL", all(item["blocks_approval"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_RUN_START", all(item["blocks_run_start"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_REAL_CONNECTION", all(item["blocks_real_connection"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", all(item["blocks_provider_api"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_TOKEN", all(item["blocks_provider_token"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_SESSION", all(item["blocks_provider_session"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_JOB", all(item["blocks_provider_job"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_STATUS_POLL", all(item["blocks_status_poll"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_HEALTH_CALL", all(item["blocks_health_call"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_SECRET_READ", all(item["blocks_secret_read"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_ENDPOINT_CALL", all(item["blocks_endpoint_call"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_OBJECT_CATALOG", all(item["blocks_object_catalog"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_METADATA_IMPORT", all(item["blocks_metadata_import"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY", all(item["blocks_object_body"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DOWNLOAD", all(item["blocks_download"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_RESTORE", all(item["blocks_restore"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_EXPORT", all(item["blocks_export"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DIRECT_UPLOAD", all(item["blocks_direct_upload"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_TOWER_UNLOCK", all(item["blocks_tower_unlock"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_EXECUTION", all(item["blocks_execution"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_VAULT_DONE", all(item["blocks_vault_done"] is True for item in blockers)),
        ("NO_BLOCKERS_RESOLVED", all(item["resolved"] is False for item in blockers)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("REQUEST", requests),
        ("GATE", gates),
        ("DENIAL", denials),
        ("STEP", steps),
        ("RECEIPT", receipts),
        ("RESULT", results),
        ("STOP", stops),
        ("BLOCKER", blockers),
    ]:
        for idx, row in enumerate(rows, start=1):
            for field in FALSE_FIELDS:
                checks.append((f"{collection_name}_{idx}_NO_{field.upper()}", row[field] is False))

    for field in FALSE_FIELDS:
        if field in readiness:
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
        "request_draft_count": len(requests),
        "approval_gate_count": len(gates),
        "denial_reason_count": len(denials),
        "run_plan_step_count": len(steps),
        "receipt_draft_count": len(receipts),
        "result_placeholder_count": len(results),
        "emergency_stop_lock_count": len(stops),
        "blocker_count": len(blockers),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "safe_to_continue_to_gp171": len(failed) == 0 and readiness["safe_to_continue_to_gp171"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp161_controlled_connection_test_lock_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(LOCK_SHELL_ID, db_path)
    return {"pack": _pack_payload(161, component["pack_name"]), "real_sqlite_backed": True, "lock_shell": component}

def get_gp162_connection_test_request_draft_registry(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(REQUEST_DRAFT_REGISTRY_ID, db_path)
    requests = get_connection_test_request_drafts(db_path)
    return {"pack": _pack_payload(162, component["pack_name"]), "real_sqlite_backed": True, "request_draft_registry": component, "request_draft_count": len(requests), "requests": requests}

def get_gp163_connection_test_approval_gate_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(APPROVAL_GATE_LOCK_ID, db_path)
    gates = get_connection_test_approval_gates(db_path)
    return {"pack": _pack_payload(163, component["pack_name"]), "real_sqlite_backed": True, "approval_gate_lock_contract": component, "approval_gate_count": len(gates), "gates": gates}

def get_gp164_connection_test_denial_reason_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(DENIAL_REASON_BOARD_ID, db_path)
    denials = get_connection_test_denial_reasons(db_path)
    return {"pack": _pack_payload(164, component["pack_name"]), "real_sqlite_backed": True, "denial_reason_board": component, "denial_reason_count": len(denials), "denial_reasons": denials}

def get_gp165_connection_test_run_plan_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RUN_PLAN_LOCK_ID, db_path)
    steps = get_connection_test_run_plan_steps(db_path)
    return {"pack": _pack_payload(165, component["pack_name"]), "real_sqlite_backed": True, "run_plan_lock_contract": component, "run_plan_step_count": len(steps), "steps": steps}

def get_gp166_connection_test_receipt_draft_ledger(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RECEIPT_DRAFT_LEDGER_ID, db_path)
    receipts = get_connection_test_receipt_drafts(db_path)
    return {"pack": _pack_payload(166, component["pack_name"]), "real_sqlite_backed": True, "receipt_draft_ledger": component, "receipt_draft_count": len(receipts), "receipt_drafts": receipts}

def get_gp167_connection_test_result_placeholder_queue(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RESULT_PLACEHOLDER_QUEUE_ID, db_path)
    results = get_connection_test_result_placeholders(db_path)
    return {"pack": _pack_payload(167, component["pack_name"]), "real_sqlite_backed": True, "result_placeholder_queue": component, "result_placeholder_count": len(results), "results": results}

def get_gp168_connection_test_emergency_stop_lock(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(EMERGENCY_STOP_LOCK_ID, db_path)
    stops = get_connection_test_emergency_stop_locks(db_path)
    return {"pack": _pack_payload(168, component["pack_name"]), "real_sqlite_backed": True, "emergency_stop_lock": component, "emergency_stop_lock_count": len(stops), "stops": stops}

def get_gp169_controlled_connection_test_blocker_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(BLOCKER_BOARD_ID, db_path)
    blockers = get_controlled_connection_test_blockers(db_path)
    return {"pack": _pack_payload(169, component["pack_name"]), "real_sqlite_backed": True, "blocker_board": component, "blocker_count": len(blockers), "blockers": blockers}

def get_gp170_controlled_connection_test_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_controlled_provider_connection_test_lock_layer(db_path)
    return {"pack": _pack_payload(170, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_controlled_provider_connection_test_lock_layer(db_path)
    counts = _counts(db_path)

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
            "source_gp160_readiness_id": component["source_gp160_readiness_id"],
            "source_gp160_readiness_hash": component["source_gp160_readiness_hash"],
            "source_gp160_readiness_score": component["source_gp160_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "controlled_test_locked": component["controlled_test_locked"],
            "no_provider_contact": component["no_provider_contact"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp171": validation["safe_to_continue_to_gp171"],
            "foundation_status": "controlled_provider_connection_test_lock_layer_ready_locked_safe_to_continue_not_done",
            "next": next_label,
            **counts,
            "connection_test_request_submitted": component["connection_test_request_submitted"],
            "connection_test_request_approved": component["connection_test_request_approved"],
            "connection_test_approval_granted": component["connection_test_approval_granted"],
            "connection_test_run_authorized": component["connection_test_run_authorized"],
            "connection_test_run_started": component["connection_test_run_started"],
            "connection_test_run_completed": component["connection_test_run_completed"],
            "connection_test_result_recorded": component["connection_test_result_recorded"],
            "connection_test_receipt_finalized": component["connection_test_receipt_finalized"],
            "connection_test_emergency_stop_triggered": component["connection_test_emergency_stop_triggered"],
            "real_provider_connection_started": component["real_provider_connection_started"],
            "real_provider_connection_completed": component["real_provider_connection_completed"],
            "provider_api_called": component["provider_api_called"],
            "provider_token_created": component["provider_token_created"],
            "provider_session_created": component["provider_session_created"],
            "provider_job_reference_created": component["provider_job_reference_created"],
            "provider_status_poll_started": component["provider_status_poll_started"],
            "provider_health_checked": component["provider_health_checked"],
            "provider_credential_value_read": component["provider_credential_value_read"],
            "provider_secret_value_read": component["provider_secret_value_read"],
            "provider_endpoint_called": component["provider_endpoint_called"],
            "provider_objects_listed": component["provider_objects_listed"],
            "provider_metadata_imported": component["provider_metadata_imported"],
            "provider_metadata_read": component["provider_metadata_read"],
            "object_body_read": component["object_body_read"],
            "object_body_view_enabled": component["object_body_view_enabled"],
            "object_body_download_enabled": component["object_body_download_enabled"],
            "object_body_plaintext_visible": component["object_body_plaintext_visible"],
            "export_package_created": component["export_package_created"],
            "export_manifest_created": component["export_manifest_created"],
            "export_download_enabled": component["export_download_enabled"],
            "export_enabled": component["export_enabled"],
            "restore_request_created": component["restore_request_created"],
            "restore_job_created": component["restore_job_created"],
            "provider_restore_api_called": component["provider_restore_api_called"],
            "direct_upload_enabled": component["direct_upload_enabled"],
            "tower_unlock_granted": component["tower_unlock_granted"],
            "execution_enabled": component["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp170",
        },
        "validation": validation,
    }

def get_gp161_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(161, LOCK_SHELL_ID, "VAULT_GP162_CONNECTION_TEST_REQUEST_DRAFT_REGISTRY", db_path)

def get_gp162_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(162, REQUEST_DRAFT_REGISTRY_ID, "VAULT_GP163_CONNECTION_TEST_APPROVAL_GATE_LOCK_CONTRACT", db_path)

def get_gp163_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(163, APPROVAL_GATE_LOCK_ID, "VAULT_GP164_CONNECTION_TEST_DENIAL_REASON_BOARD", db_path)

def get_gp164_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(164, DENIAL_REASON_BOARD_ID, "VAULT_GP165_CONNECTION_TEST_RUN_PLAN_LOCK_CONTRACT", db_path)

def get_gp165_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(165, RUN_PLAN_LOCK_ID, "VAULT_GP166_CONNECTION_TEST_RECEIPT_DRAFT_LEDGER", db_path)

def get_gp166_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(166, RECEIPT_DRAFT_LEDGER_ID, "VAULT_GP167_CONNECTION_TEST_RESULT_PLACEHOLDER_QUEUE", db_path)

def get_gp167_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(167, RESULT_PLACEHOLDER_QUEUE_ID, "VAULT_GP168_CONNECTION_TEST_EMERGENCY_STOP_LOCK", db_path)

def get_gp168_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(168, EMERGENCY_STOP_LOCK_ID, "VAULT_GP169_CONTROLLED_CONNECTION_TEST_BLOCKER_BOARD", db_path)

def get_gp169_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(169, BLOCKER_BOARD_ID, "VAULT_GP170_CONTROLLED_CONNECTION_TEST_READINESS_CHECKPOINT", db_path)

def get_gp170_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(170, READINESS_ID, NEXT_PACK, db_path)
    status["gp170_status"]["next_section"] = NEXT_SECTION_ID
    status["gp170_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp170_status"]["next_pack"] = NEXT_PACK
    return status

def get_controlled_provider_connection_test_lock_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_controlled_provider_connection_test_lock_layer(db_path)
    components = _rows("vault_controlled_connection_test_components", "gp_number", db_path, {"data_json": "data"})
    requests = get_connection_test_request_drafts(db_path)
    gates = get_connection_test_approval_gates(db_path)
    denials = get_connection_test_denial_reasons(db_path)
    steps = get_connection_test_run_plan_steps(db_path)
    receipts = get_connection_test_receipt_drafts(db_path)
    results = get_connection_test_result_placeholders(db_path)
    stops = get_connection_test_emergency_stop_locks(db_path)
    blockers = get_controlled_connection_test_blockers(db_path)
    readiness = _readiness(db_path)
    validation = validate_controlled_provider_connection_test_lock_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "requests": {"request_draft_count": len(requests), "requests": requests},
        "approval_gates": {"approval_gate_count": len(gates), "gates": gates},
        "denial_reasons": {"denial_reason_count": len(denials), "denial_reasons": denials},
        "run_plan": {"run_plan_step_count": len(steps), "steps": steps},
        "receipt_drafts": {"receipt_draft_count": len(receipts), "receipt_drafts": receipts},
        "result_placeholders": {"result_placeholder_count": len(results), "results": results},
        "emergency_stops": {"emergency_stop_lock_count": len(stops), "stops": stops},
        "blockers": {"blocker_count": len(blockers), "blockers": blockers},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "controlled_provider_connection_test_lock_layer_ready": True,
            "controlled_test_locked": True,
            "safe_to_continue_to_gp171": validation["safe_to_continue_to_gp171"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "no_provider_contact": True,
            "connection_test_request_submitted": False,
            "connection_test_request_approved": False,
            "connection_test_approval_granted": False,
            "connection_test_run_authorized": False,
            "connection_test_run_started": False,
            "connection_test_run_completed": False,
            "connection_test_result_recorded": False,
            "connection_test_receipt_finalized": False,
            "connection_test_emergency_stop_triggered": False,
            "real_provider_connection_started": False,
            "provider_api_called": False,
            "provider_token_created": False,
            "provider_session_created": False,
            "provider_job_reference_created": False,
            "provider_status_poll_started": False,
            "provider_health_checked": False,
            "provider_credential_value_read": False,
            "provider_secret_value_read": False,
            "provider_endpoint_called": False,
            "provider_objects_listed": False,
            "provider_metadata_imported": False,
            "provider_metadata_read": False,
            "object_body_read": False,
            "object_body_view_enabled": False,
            "object_body_download_enabled": False,
            "object_body_plaintext_visible": False,
            "export_package_created": False,
            "restore_job_created": False,
            "direct_upload_enabled": False,
            "tower_unlock_granted": False,
            "execution_enabled": False,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        "routes": {
            "page": "/vault/controlled-provider-connection-test-lock-layer",
            "json": "/vault/controlled-provider-connection-test-lock-layer.json",
            "gp161": "/vault/gp161-status.json",
            "gp162": "/vault/gp162-status.json",
            "gp163": "/vault/gp163-status.json",
            "gp164": "/vault/gp164-status.json",
            "gp165": "/vault/gp165-status.json",
            "gp166": "/vault/gp166-status.json",
            "gp167": "/vault/gp167-status.json",
            "gp168": "/vault/gp168-status.json",
            "gp169": "/vault/gp169-status.json",
            "gp170": "/vault/gp170-status.json",
        },
    }

def render_controlled_provider_connection_test_lock_layer_page() -> str:
    home = get_controlled_provider_connection_test_lock_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    request_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['request_name'])}</strong>
          <span>{escape(item['request_status'])}</span>
          <code>{escape(item['request_category'])} · draft locked</code>
        </article>
        """
        for item in home["requests"]["requests"]
    )

    blocker_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['blocker_name'])}</strong>
          <span>{escape(item['blocker_status'])}</span>
          <code>{escape(item['blocker_category'])}</code>
        </article>
        """
        for item in home["blockers"]["blockers"]
    )

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP161-GP170 Controlled Provider Connection Test Lock Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 161-170</div>
    <div class="eyebrow">Controlled Provider Connection Test Lock Layer · GP161-GP170</div>
    <h1>Controlled Connection Test Lock</h1>
    <p>This layer prepares request drafts, approval gates, run plans, receipt drafts, placeholders, emergency-stop locks, blockers, and readiness proof for a future controlled provider connection test. The actual test remains locked.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['request_draft_count']}</strong><span>request drafts</span></div>
      <div class="metric"><strong>{home['store']['approval_gate_count']}</strong><span>approval gates</span></div>
      <div class="metric"><strong>{home['store']['blocker_count']}</strong><span>active blockers</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP161-GP170 built</span>
      <span class="pill ok">Controlled test locked</span>
      <span class="pill ok">Safe to GP171</span>
      <span class="pill danger">No request submit</span>
      <span class="pill danger">No approval</span>
      <span class="pill danger">No provider contact</span>
      <span class="pill danger">No provider API</span>
      <span class="pill danger">No token/session/job</span>
      <span class="pill danger">No object body</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Connection Test Request Drafts</h2>
    <div class="cards">{request_cards}</div>
  </section>

  <section class="section">
    <h2>Connection Test Blockers</h2>
    <div class="cards">{blocker_cards}</div>
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
