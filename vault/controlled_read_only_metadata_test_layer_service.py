"""
VAULT GP171-GP180 — Controlled Read-Only Metadata Test Layer

New section:
Archive Vault — Controlled Read-Only Metadata Test Layer / GP171-GP180

Builds:
- GP171 Controlled Read-Only Metadata Test Shell
- GP172 Metadata Test Request Draft Registry
- GP173 Metadata Scope Contract
- GP174 Metadata Read Approval Gate Lock
- GP175 Metadata Query Plan Lock Contract
- GP176 Metadata Result Placeholder Queue
- GP177 Metadata Receipt Draft Ledger
- GP178 Object Body and Download Prohibition Contract
- GP179 Controlled Metadata Test Blocker Board
- GP180 Controlled Metadata Test Readiness Checkpoint

This layer prepares metadata-only test governance surfaces. It does not submit,
approve, start, or complete a metadata test and does not contact any provider.
Object bodies, downloads, restore/export/upload/delete/execution remain locked.
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

from vault.controlled_provider_connection_test_lock_layer_service import (
    get_gp170_status,
    get_gp170_controlled_connection_test_readiness_checkpoint,
    get_controlled_provider_connection_test_lock_layer_home,
    validate_controlled_provider_connection_test_lock_layer,
    get_connection_test_request_drafts,
    get_controlled_connection_test_blockers,
)

LAYER_ID = "VAULT_GP171_180"
LAYER_NAME = "Controlled Read-Only Metadata Test Layer"
SCHEMA_VERSION = "vault.controlled_read_only_metadata_test_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_READ_ONLY_METADATA_TEST_LAYER"
SECTION_TITLE = "Archive Vault — Controlled Read-Only Metadata Test Layer"
SECTION_RANGE = "GP171-GP180"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PROVIDER_CONNECTION_TEST_LOCK_LAYER"
PREVIOUS_SECTION_RANGE = "GP161-GP170"

NEXT_SECTION_ID = "ARCHIVE_VAULT_REAL_ARCHIVE_INDEX_AND_SEARCH_LAYER"
NEXT_SECTION_RANGE = "GP181-GP190"
NEXT_PACK = "VAULT_GP181_190_REAL_ARCHIVE_INDEX_AND_SEARCH_LAYER"

DEFAULT_DB_ENV = "VAULT_CONTROLLED_READ_ONLY_METADATA_TEST_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_controlled_read_only_metadata_test_layer.sqlite"

METADATA_TEST_SHELL_ID = "VCROMT-SHELL-GP171-001"
REQUEST_DRAFT_REGISTRY_ID = "VCROMT-REQUEST-GP172-001"
METADATA_SCOPE_CONTRACT_ID = "VCROMT-SCOPE-GP173-001"
APPROVAL_GATE_LOCK_ID = "VCROMT-APPROVAL-GP174-001"
QUERY_PLAN_LOCK_ID = "VCROMT-QUERY-GP175-001"
RESULT_PLACEHOLDER_QUEUE_ID = "VCROMT-RESULT-GP176-001"
RECEIPT_DRAFT_LEDGER_ID = "VCROMT-RECEIPT-GP177-001"
BODY_DOWNLOAD_PROHIBITION_ID = "VCROMT-BODYLOCK-GP178-001"
BLOCKER_BOARD_ID = "VCROMT-BLOCKER-GP179-001"
READINESS_ID = "VCROMT-READINESS-GP180-001"

FALSE_FIELDS = [
    "metadata_test_request_submitted",
    "metadata_test_request_approved",
    "metadata_test_request_denied_final",
    "metadata_read_approval_granted",
    "metadata_test_authorized",
    "metadata_test_run_started",
    "metadata_test_run_completed",
    "metadata_test_result_recorded",
    "metadata_test_result_approved",
    "metadata_test_receipt_finalized",
    "metadata_test_receipt_persisted",
    "metadata_scope_activated",
    "metadata_query_executed",
    "metadata_query_result_imported",
    "metadata_query_result_persisted",
    "read_only_metadata_test_live",
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
    "object_delete_requested",
    "object_delete_approved",
    "object_delete_executed",
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
    ("metadata_shape_probe_request", "Metadata Shape Probe Request Draft", "metadata_shape", "high"),
    ("metadata_lineage_probe_request", "Metadata Lineage Probe Request Draft", "metadata_lineage", "high"),
    ("metadata_timestamp_probe_request", "Metadata Timestamp Probe Request Draft", "metadata_timestamp", "medium"),
    ("metadata_hash_reference_probe_request", "Metadata Hash Reference Probe Request Draft", "metadata_hash_reference", "high"),
    ("metadata_storage_class_probe_request", "Metadata Storage Class Probe Request Draft", "metadata_storage_class", "medium"),
    ("metadata_retention_probe_request", "Metadata Retention Probe Request Draft", "metadata_retention", "high"),
]

METADATA_SCOPE_ITEMS = [
    ("object_reference_hash", "Object Reference Hash", "safe_metadata_placeholder"),
    ("object_size_bytes", "Object Size Bytes", "safe_metadata_placeholder"),
    ("content_type_label", "Content Type Label", "safe_metadata_placeholder"),
    ("created_at_timestamp", "Created At Timestamp", "safe_metadata_placeholder"),
    ("updated_at_timestamp", "Updated At Timestamp", "safe_metadata_placeholder"),
    ("etag_or_checksum_reference", "ETag or Checksum Reference", "safe_metadata_placeholder"),
    ("storage_class_label", "Storage Class Label", "safe_metadata_placeholder"),
    ("retention_policy_reference", "Retention Policy Reference", "safe_metadata_placeholder"),
]

QUERY_PLAN_STEPS = [
    ("confirm_tower_gate_locked", "Confirm Tower gate remains locked"),
    ("confirm_metadata_scope_only", "Confirm metadata-only scope"),
    ("confirm_no_object_identifier_collection", "Confirm no object identifier collection"),
    ("confirm_no_object_body_access", "Confirm no object body access"),
    ("confirm_no_download_or_stream", "Confirm no download or stream"),
    ("confirm_no_restore_export_upload_delete", "Confirm no restore/export/upload/delete"),
    ("confirm_no_provider_call", "Confirm no provider call in this layer"),
    ("record_placeholder_result_only", "Record placeholder result only"),
]

RESULT_PLACEHOLDERS = [
    ("metadata_test_not_run", "Metadata Test Not Run"),
    ("provider_not_contacted", "Provider Not Contacted"),
    ("metadata_not_read", "Metadata Not Read"),
    ("object_body_not_accessed", "Object Body Not Accessed"),
    ("download_not_created", "Download Not Created"),
    ("restore_export_upload_delete_not_created", "Restore/Export/Upload/Delete Not Created"),
]

PROHIBITION_ITEMS = [
    ("object_body_read_prohibited", "Object Body Read Prohibited"),
    ("object_body_view_prohibited", "Object Body View Prohibited"),
    ("object_body_download_prohibited", "Object Body Download Prohibited"),
    ("object_body_plaintext_prohibited", "Object Body Plaintext Prohibited"),
    ("file_stream_prohibited", "File Stream Prohibited"),
    ("file_download_prohibited", "File Download Prohibited"),
    ("restore_export_upload_delete_prohibited", "Restore/Export/Upload/Delete Prohibited"),
    ("execution_prohibited", "Execution Prohibited"),
]

BLOCKER_SPECS = [
    ("metadata_test_submit_locked", "Metadata test submit locked", "request", "critical"),
    ("metadata_read_approval_locked", "Metadata read approval locked", "approval", "critical"),
    ("metadata_query_locked", "Metadata query locked", "query", "critical"),
    ("provider_connection_locked", "Provider connection locked", "connection", "critical"),
    ("provider_api_locked", "Provider API locked", "provider_api", "critical"),
    ("provider_token_session_job_locked", "Provider token/session/job locked", "token_session_job", "critical"),
    ("credential_secret_locked", "Credential/secret value locked", "credential", "critical"),
    ("endpoint_call_locked", "Endpoint call locked", "endpoint", "critical"),
    ("object_catalog_metadata_locked", "Object catalog/metadata read locked", "metadata", "critical"),
    ("object_body_download_locked", "Object body/download locked", "object_body", "critical"),
    ("restore_export_upload_delete_locked", "Restore/export/upload/delete locked", "dangerous_ops", "critical"),
    ("tower_execution_done_locked", "Tower unlock, execution, and Vault done locked", "tower_execution", "critical"),
]

COMPONENT_SPECS = [
    (171, METADATA_TEST_SHELL_ID, "VAULT_GP171", "Controlled Read-Only Metadata Test Shell", "controlled_read_only_metadata_test_shell"),
    (172, REQUEST_DRAFT_REGISTRY_ID, "VAULT_GP172", "Metadata Test Request Draft Registry", "metadata_test_request_draft_registry"),
    (173, METADATA_SCOPE_CONTRACT_ID, "VAULT_GP173", "Metadata Scope Contract", "metadata_scope_contract"),
    (174, APPROVAL_GATE_LOCK_ID, "VAULT_GP174", "Metadata Read Approval Gate Lock", "metadata_read_approval_gate_lock"),
    (175, QUERY_PLAN_LOCK_ID, "VAULT_GP175", "Metadata Query Plan Lock Contract", "metadata_query_plan_lock_contract"),
    (176, RESULT_PLACEHOLDER_QUEUE_ID, "VAULT_GP176", "Metadata Result Placeholder Queue", "metadata_result_placeholder_queue"),
    (177, RECEIPT_DRAFT_LEDGER_ID, "VAULT_GP177", "Metadata Receipt Draft Ledger", "metadata_receipt_draft_ledger"),
    (178, BODY_DOWNLOAD_PROHIBITION_ID, "VAULT_GP178", "Object Body and Download Prohibition Contract", "object_body_download_prohibition_contract"),
    (179, BLOCKER_BOARD_ID, "VAULT_GP179", "Controlled Metadata Test Blocker Board", "controlled_metadata_test_blocker_board"),
    (180, READINESS_ID, "VAULT_GP180", "Controlled Metadata Test Readiness Checkpoint", "controlled_metadata_test_readiness_checkpoint"),
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
        "source_gp170_readiness_score",
        "component_count",
        "request_draft_count",
        "metadata_scope_count",
        "approval_gate_count",
        "query_plan_step_count",
        "result_placeholder_count",
        "receipt_draft_count",
        "prohibition_count",
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
        "depends_on": ["VAULT_GP170"],
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
        "depends_on": ["VAULT_GP170"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_controlled_read_only_metadata_test_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_controlled_metadata_test_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp170_readiness_id TEXT NOT NULL,
                source_gp170_readiness_hash TEXT NOT NULL,
                source_gp170_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                metadata_test_locked INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                body_download_prohibited INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_metadata_test_request_drafts (
                request_draft_id TEXT PRIMARY KEY,
                request_code TEXT NOT NULL UNIQUE,
                request_name TEXT NOT NULL,
                request_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                request_status TEXT NOT NULL,
                source_gp170_readiness_hash TEXT NOT NULL,
                request_draft_ready INTEGER NOT NULL DEFAULT 1,
                request_draft_locked INTEGER NOT NULL DEFAULT 1,
                metadata_test_locked INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                body_download_prohibited INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_metadata_scope_items (
                scope_item_id TEXT PRIMARY KEY,
                scope_code TEXT NOT NULL UNIQUE,
                scope_name TEXT NOT NULL,
                scope_category TEXT NOT NULL,
                scope_status TEXT NOT NULL,
                scope_locked INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                body_download_prohibited INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                scope_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_metadata_read_approval_gates (
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
            CREATE TABLE IF NOT EXISTS vault_metadata_query_plan_steps (
                query_step_id TEXT PRIMARY KEY,
                step_code TEXT NOT NULL UNIQUE,
                step_name TEXT NOT NULL,
                step_status TEXT NOT NULL,
                query_plan_locked INTEGER NOT NULL DEFAULT 1,
                metadata_test_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_metadata_result_placeholders (
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
            CREATE TABLE IF NOT EXISTS vault_metadata_receipt_drafts (
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
            CREATE TABLE IF NOT EXISTS vault_object_body_download_prohibitions (
                prohibition_id TEXT PRIMARY KEY,
                prohibition_code TEXT NOT NULL UNIQUE,
                prohibition_name TEXT NOT NULL,
                prohibition_status TEXT NOT NULL,
                prohibition_active INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                prohibition_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_controlled_metadata_test_blockers (
                blocker_id TEXT PRIMARY KEY,
                blocker_code TEXT NOT NULL UNIQUE,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocker_active INTEGER NOT NULL DEFAULT 1,
                blocks_request_submit INTEGER NOT NULL DEFAULT 1,
                blocks_metadata_approval INTEGER NOT NULL DEFAULT 1,
                blocks_metadata_query INTEGER NOT NULL DEFAULT 1,
                blocks_real_connection INTEGER NOT NULL DEFAULT 1,
                blocks_provider_api INTEGER NOT NULL DEFAULT 1,
                blocks_provider_token INTEGER NOT NULL DEFAULT 1,
                blocks_provider_session INTEGER NOT NULL DEFAULT 1,
                blocks_provider_job INTEGER NOT NULL DEFAULT 1,
                blocks_status_poll INTEGER NOT NULL DEFAULT 1,
                blocks_secret_read INTEGER NOT NULL DEFAULT 1,
                blocks_endpoint_call INTEGER NOT NULL DEFAULT 1,
                blocks_object_catalog INTEGER NOT NULL DEFAULT 1,
                blocks_metadata_read INTEGER NOT NULL DEFAULT 1,
                blocks_object_body INTEGER NOT NULL DEFAULT 1,
                blocks_download INTEGER NOT NULL DEFAULT 1,
                blocks_restore INTEGER NOT NULL DEFAULT 1,
                blocks_export INTEGER NOT NULL DEFAULT 1,
                blocks_direct_upload INTEGER NOT NULL DEFAULT 1,
                blocks_delete INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_controlled_metadata_test_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                request_draft_count INTEGER NOT NULL,
                metadata_scope_count INTEGER NOT NULL,
                approval_gate_count INTEGER NOT NULL,
                query_plan_step_count INTEGER NOT NULL,
                result_placeholder_count INTEGER NOT NULL,
                receipt_draft_count INTEGER NOT NULL,
                prohibition_count INTEGER NOT NULL,
                blocker_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                safe_to_continue_to_gp181 INTEGER NOT NULL DEFAULT 1,
                section_ready INTEGER NOT NULL DEFAULT 1,
                metadata_test_locked INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                body_download_prohibited INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_controlled_metadata_test_events (
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
            "vault_controlled_metadata_test_components",
            "vault_metadata_test_request_drafts",
            "vault_metadata_scope_items",
            "vault_metadata_read_approval_gates",
            "vault_metadata_query_plan_steps",
            "vault_metadata_result_placeholders",
            "vault_metadata_receipt_drafts",
            "vault_object_body_download_prohibitions",
            "vault_controlled_metadata_test_blockers",
            "vault_controlled_metadata_test_readiness",
            "vault_controlled_metadata_test_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VCROMTEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_controlled_metadata_test_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_controlled_read_only_metadata_test_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_controlled_read_only_metadata_test_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_controlled_metadata_test_components WHERE component_id = ?",
            (METADATA_TEST_SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp170_status = get_gp170_status()["gp170_status"]
            gp170_checkpoint = get_gp170_controlled_connection_test_readiness_checkpoint()["readiness_checkpoint"]
            gp170_home = get_controlled_provider_connection_test_lock_layer_home()
            gp170_validation = validate_controlled_provider_connection_test_lock_layer()

            source_requests = get_connection_test_request_drafts()
            source_blockers = get_controlled_connection_test_blockers()

            readiness = gp170_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp170_readiness_id": readiness["readiness_id"],
                "source_gp170_readiness_hash": readiness["readiness_hash"],
                "source_gp170_readiness_score": readiness["readiness_score"],
            }

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "request_draft_count": len(REQUEST_DRAFTS),
                "metadata_scope_count": len(METADATA_SCOPE_ITEMS),
                "approval_gate_count": len(REQUEST_DRAFTS),
                "query_plan_step_count": len(QUERY_PLAN_STEPS),
                "result_placeholder_count": len(RESULT_PLACEHOLDERS),
                "receipt_draft_count": len(REQUEST_DRAFTS),
                "prohibition_count": len(PROHIBITION_ITEMS),
                "blocker_count": len(BLOCKER_SPECS),
            }

            source_context = {
                "source_gp170_status_ready": gp170_status["ready"],
                "source_gp170_validation_passed": gp170_status["validation_passed"],
                "source_gp170_safe_to_continue_to_gp171": gp170_status["safe_to_continue_to_gp171"],
                "source_gp170_readiness_hash": readiness["readiness_hash"],
                "source_gp170_readiness_score": readiness["readiness_score"],
                "source_connection_request_draft_count": len(source_requests),
                "source_connection_blocker_count": len(source_blockers),
                "source_validation_check_count": gp170_validation["check_count"],
            }

            component_extra = {
                METADATA_TEST_SHELL_ID: {"controlled_read_only_metadata_test_shell_ready": True},
                REQUEST_DRAFT_REGISTRY_ID: {"metadata_test_request_draft_registry_ready": True, "request_draft_count": counts["request_draft_count"]},
                METADATA_SCOPE_CONTRACT_ID: {"metadata_scope_contract_ready": True, "metadata_scope_count": counts["metadata_scope_count"]},
                APPROVAL_GATE_LOCK_ID: {"metadata_read_approval_gate_lock_ready": True, "approval_gate_count": counts["approval_gate_count"]},
                QUERY_PLAN_LOCK_ID: {"metadata_query_plan_lock_contract_ready": True, "query_plan_step_count": counts["query_plan_step_count"]},
                RESULT_PLACEHOLDER_QUEUE_ID: {"metadata_result_placeholder_queue_ready": True, "result_placeholder_count": counts["result_placeholder_count"]},
                RECEIPT_DRAFT_LEDGER_ID: {"metadata_receipt_draft_ledger_ready": True, "receipt_draft_count": counts["receipt_draft_count"]},
                BODY_DOWNLOAD_PROHIBITION_ID: {"object_body_download_prohibition_contract_ready": True, "prohibition_count": counts["prohibition_count"]},
                BLOCKER_BOARD_ID: {"controlled_metadata_test_blocker_board_ready": True, "blocker_count": counts["blocker_count"]},
                READINESS_ID: {"controlled_metadata_test_readiness_checkpoint_ready": True, "safe_to_continue_to_gp181": True},
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
                    "metadata_test_locked": True,
                    "metadata_only": True,
                    "body_download_prohibited": True,
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
                    "metadata_test_locked": 1,
                    "metadata_only": 1,
                    "body_download_prohibited": 1,
                    "no_provider_contact": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_controlled_metadata_test_components", row)

            request_ids = []
            for idx, (code, name, category, severity) in enumerate(REQUEST_DRAFTS, start=1):
                request_id = f"VCROMTRD-{idx:03d}"
                request_ids.append((request_id, code, name))
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "request_code": code,
                    "request_name": name,
                    "request_category": category,
                    "severity": severity,
                    "request_status": "DRAFT_ONLY_NOT_SUBMITTED_METADATA_TEST_LOCKED",
                    "source_gp170_readiness_hash": readiness["readiness_hash"],
                    "request_draft_ready": True,
                    "request_draft_locked": True,
                    "metadata_test_locked": True,
                    "metadata_only": True,
                    "body_download_prohibited": True,
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
                    "source_gp170_readiness_hash": readiness["readiness_hash"],
                    "request_draft_ready": 1,
                    "request_draft_locked": 1,
                    "metadata_test_locked": 1,
                    "metadata_only": 1,
                    "body_download_prohibited": 1,
                    "no_provider_contact": 1,
                    "payload_json": _json_dumps(payload),
                    "request_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_metadata_test_request_drafts", row)

                gate_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "gate_code": f"{code}_metadata_read_gate",
                    "request_draft_id": request_id,
                    "gate_name": f"{name} Metadata Read Approval Gate",
                    "gate_status": "APPROVAL_GATE_LOCKED_NO_METADATA_READ_APPROVAL",
                    "approval_gate_locked": True,
                    "tower_review_required": True,
                    "owner_review_required": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "approval_gate_id": f"VCROMTAG-{idx:03d}",
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
                _insert_dict(conn, "vault_metadata_read_approval_gates", row)

                receipt_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "receipt_code": f"{code}_metadata_receipt_draft",
                    "source_request_draft_id": request_id,
                    "receipt_name": f"{name} Metadata Receipt Draft",
                    "receipt_status": "DRAFT_ONLY_NOT_FINALIZED_NO_METADATA_RESULT",
                    "receipt_draft_locked": True,
                    "final_receipt_created": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "receipt_draft_id": f"VCROMTRCP-{idx:03d}",
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
                _insert_dict(conn, "vault_metadata_receipt_drafts", row)

            for idx, (code, name, category) in enumerate(METADATA_SCOPE_ITEMS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "scope_code": code,
                    "scope_name": name,
                    "scope_category": category,
                    "scope_status": "SCOPE_DECLARED_PLACEHOLDER_ONLY_NOT_ACTIVATED",
                    "scope_locked": True,
                    "metadata_only": True,
                    "body_download_prohibited": True,
                    "blocked_content_types": ["object_body", "plaintext", "download", "stream", "restore", "export", "upload", "delete"],
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "scope_item_id": f"VCROMTSCOPE-{idx:03d}",
                    "scope_code": code,
                    "scope_name": name,
                    "scope_category": category,
                    "scope_status": payload["scope_status"],
                    "scope_locked": 1,
                    "metadata_only": 1,
                    "body_download_prohibited": 1,
                    "payload_json": _json_dumps(payload),
                    "scope_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_metadata_scope_items", row)

            for idx, (code, name) in enumerate(QUERY_PLAN_STEPS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "step_code": code,
                    "step_name": name,
                    "step_status": "QUERY_PLAN_STEP_LOCKED_NOT_EXECUTED",
                    "query_plan_locked": True,
                    "metadata_test_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "query_step_id": f"VCROMTSTEP-{idx:03d}",
                    "step_code": code,
                    "step_name": name,
                    "step_status": payload["step_status"],
                    "query_plan_locked": 1,
                    "metadata_test_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "step_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_metadata_query_plan_steps", row)

            for idx, (code, name) in enumerate(RESULT_PLACEHOLDERS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "result_code": code,
                    "result_name": name,
                    "result_status": "PLACEHOLDER_ONLY_NO_METADATA_RESULT",
                    "result_placeholder_locked": True,
                    "no_provider_result": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "result_placeholder_id": f"VCROMTRES-{idx:03d}",
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
                _insert_dict(conn, "vault_metadata_result_placeholders", row)

            for idx, (code, name) in enumerate(PROHIBITION_ITEMS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "prohibition_code": code,
                    "prohibition_name": name,
                    "prohibition_status": "ACTIVE_PROHIBITION",
                    "prohibition_active": True,
                    "blocked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "prohibition_id": f"VCROMTPROH-{idx:03d}",
                    "prohibition_code": code,
                    "prohibition_name": name,
                    "prohibition_status": payload["prohibition_status"],
                    "prohibition_active": 1,
                    "payload_json": _json_dumps(payload),
                    "prohibition_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_object_body_download_prohibitions", row)

            for idx, (code, name, category, severity) in enumerate(BLOCKER_SPECS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "ACTIVE_CONTROLLED_METADATA_TEST_BLOCKER",
                    "blocker_active": True,
                    "blocks_request_submit": True,
                    "blocks_metadata_approval": True,
                    "blocks_metadata_query": True,
                    "blocks_real_connection": True,
                    "blocks_provider_api": True,
                    "blocks_provider_token": True,
                    "blocks_provider_session": True,
                    "blocks_provider_job": True,
                    "blocks_status_poll": True,
                    "blocks_secret_read": True,
                    "blocks_endpoint_call": True,
                    "blocks_object_catalog": True,
                    "blocks_metadata_read": True,
                    "blocks_object_body": True,
                    "blocks_download": True,
                    "blocks_restore": True,
                    "blocks_export": True,
                    "blocks_direct_upload": True,
                    "blocks_delete": True,
                    "blocks_tower_unlock": True,
                    "blocks_execution": True,
                    "blocks_vault_done": True,
                    "resolved": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "blocker_id": f"VCROMTBLK-{idx:03d}",
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": payload["blocker_status"],
                    "blocker_active": 1,
                    "blocks_request_submit": 1,
                    "blocks_metadata_approval": 1,
                    "blocks_metadata_query": 1,
                    "blocks_real_connection": 1,
                    "blocks_provider_api": 1,
                    "blocks_provider_token": 1,
                    "blocks_provider_session": 1,
                    "blocks_provider_job": 1,
                    "blocks_status_poll": 1,
                    "blocks_secret_read": 1,
                    "blocks_endpoint_call": 1,
                    "blocks_object_catalog": 1,
                    "blocks_metadata_read": 1,
                    "blocks_object_body": 1,
                    "blocks_download": 1,
                    "blocks_restore": 1,
                    "blocks_export": 1,
                    "blocks_direct_upload": 1,
                    "blocks_delete": 1,
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
                _insert_dict(conn, "vault_controlled_metadata_test_blockers", row)

            checks = [
                ("SOURCE_GP170_READY", bool(gp170_status["ready"])),
                ("SOURCE_GP170_VALIDATION_PASSED", bool(gp170_status["validation_passed"])),
                ("SOURCE_GP170_SAFE_TO_CONTINUE", bool(gp170_status["safe_to_continue_to_gp171"])),
                ("SOURCE_GP170_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP170_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("REQUEST_DRAFT_COUNT_6", counts["request_draft_count"] == 6),
                ("METADATA_SCOPE_COUNT_8", counts["metadata_scope_count"] == 8),
                ("APPROVAL_GATE_COUNT_6", counts["approval_gate_count"] == 6),
                ("QUERY_PLAN_STEP_COUNT_8", counts["query_plan_step_count"] == 8),
                ("RESULT_PLACEHOLDER_COUNT_6", counts["result_placeholder_count"] == 6),
                ("RECEIPT_DRAFT_COUNT_6", counts["receipt_draft_count"] == 6),
                ("PROHIBITION_COUNT_8", counts["prohibition_count"] == 8),
                ("BLOCKER_COUNT_12", counts["blocker_count"] == 12),
                ("SECTION_GP171_GP180", SECTION_RANGE == "GP171-GP180"),
                ("NEXT_SECTION_GP181_GP190", NEXT_SECTION_RANGE == "GP181-GP190"),
                ("METADATA_TEST_LOCKED", True),
                ("METADATA_ONLY", True),
                ("BODY_DOWNLOAD_PROHIBITED", True),
                ("NO_PROVIDER_CONTACT", True),
                ("NO_REQUEST_SUBMIT", True),
                ("NO_METADATA_APPROVAL", True),
                ("NO_METADATA_QUERY", True),
                ("NO_PROVIDER_API", True),
                ("NO_PROVIDER_TOKEN_SESSION_JOB", True),
                ("NO_STATUS_POLL", True),
                ("NO_SECRET_READ", True),
                ("NO_ENDPOINT_CALL", True),
                ("NO_OBJECT_CATALOG", True),
                ("NO_METADATA_READ", True),
                ("NO_OBJECT_BODY", True),
                ("NO_DOWNLOAD", True),
                ("NO_RESTORE_EXPORT_UPLOAD_DELETE", True),
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
                "gp_number": 180,
                "pack_id": "VAULT_GP180",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp170_readiness_id": readiness["readiness_id"],
                "source_gp170_readiness_hash": readiness["readiness_hash"],
                "source_gp170_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "safe_to_continue_to_gp181": failed_count == 0,
                "section_ready": True,
                "metadata_test_locked": True,
                "metadata_only": True,
                "body_download_prohibited": True,
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
                "gp_number": 180,
                "pack_id": "VAULT_GP180",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "CONTROLLED_READ_ONLY_METADATA_TEST_LAYER_READY_LOCKED_SAFE_TO_CONTINUE_NOT_DONE",
                "readiness_score": readiness_payload["readiness_score"],
                **counts,
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "safe_to_continue_to_gp181": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "metadata_test_locked": 1,
                "metadata_only": 1,
                "body_download_prohibited": 1,
                "no_provider_contact": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_controlled_metadata_test_readiness", row)

            for event_type, event_payload in [
                ("GP171_CONTROLLED_METADATA_TEST_SHELL_CREATED", {"component_id": METADATA_TEST_SHELL_ID}),
                ("GP172_METADATA_TEST_REQUEST_DRAFT_REGISTRY_CREATED", {"request_draft_count": counts["request_draft_count"]}),
                ("GP173_METADATA_SCOPE_CONTRACT_CREATED", {"metadata_scope_count": counts["metadata_scope_count"]}),
                ("GP174_METADATA_READ_APPROVAL_GATE_LOCK_CREATED", {"approval_gate_count": counts["approval_gate_count"]}),
                ("GP175_METADATA_QUERY_PLAN_LOCK_CREATED", {"query_plan_step_count": counts["query_plan_step_count"]}),
                ("GP176_METADATA_RESULT_PLACEHOLDER_QUEUE_CREATED", {"result_placeholder_count": counts["result_placeholder_count"]}),
                ("GP177_METADATA_RECEIPT_DRAFT_LEDGER_CREATED", {"receipt_draft_count": counts["receipt_draft_count"]}),
                ("GP178_OBJECT_BODY_DOWNLOAD_PROHIBITION_CREATED", {"prohibition_count": counts["prohibition_count"]}),
                ("GP179_CONTROLLED_METADATA_TEST_BLOCKER_BOARD_CREATED", {"blocker_count": counts["blocker_count"]}),
                ("GP180_CONTROLLED_METADATA_TEST_READINESS_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp181": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_controlled_metadata_test_components").fetchone()["c"]),
            "request_draft_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_metadata_test_request_drafts").fetchone()["c"]),
            "metadata_scope_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_metadata_scope_items").fetchone()["c"]),
            "approval_gate_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_metadata_read_approval_gates").fetchone()["c"]),
            "query_plan_step_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_metadata_query_plan_steps").fetchone()["c"]),
            "result_placeholder_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_metadata_result_placeholders").fetchone()["c"]),
            "receipt_draft_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_metadata_receipt_drafts").fetchone()["c"]),
            "prohibition_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_object_body_download_prohibitions").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_controlled_metadata_test_blockers").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_controlled_metadata_test_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_controlled_metadata_test_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_controlled_read_only_metadata_test_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_controlled_read_only_metadata_test_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_controlled_metadata_test_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_controlled_read_only_metadata_test_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_controlled_metadata_test_readiness WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_controlled_read_only_metadata_test_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_controlled_metadata_test_events ORDER BY created_at, event_id").fetchall()
    return [{"event_id": row["event_id"], "event_type": row["event_type"], "event_payload": _json_loads(row["event_payload_json"]), "created_at": row["created_at"]} for row in rows]

def get_metadata_test_request_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_metadata_test_request_drafts", "request_code", db_path, {"payload_json": "payload"})

def get_metadata_scope_items(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_metadata_scope_items", "scope_code", db_path, {"payload_json": "payload"})

def get_metadata_read_approval_gates(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_metadata_read_approval_gates", "gate_code", db_path, {"payload_json": "payload"})

def get_metadata_query_plan_steps(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_metadata_query_plan_steps", "step_code", db_path, {"payload_json": "payload"})

def get_metadata_result_placeholders(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_metadata_result_placeholders", "result_code", db_path, {"payload_json": "payload"})

def get_metadata_receipt_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_metadata_receipt_drafts", "receipt_code", db_path, {"payload_json": "payload"})

def get_object_body_download_prohibitions(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_object_body_download_prohibitions", "prohibition_code", db_path, {"payload_json": "payload"})

def get_controlled_metadata_test_blockers(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_controlled_metadata_test_blockers", "blocker_code", db_path, {"payload_json": "payload"})

def validate_controlled_read_only_metadata_test_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_controlled_metadata_test_components", "gp_number", db_path, {"data_json": "data"})
    requests = get_metadata_test_request_drafts(db_path)
    scopes = get_metadata_scope_items(db_path)
    gates = get_metadata_read_approval_gates(db_path)
    steps = get_metadata_query_plan_steps(db_path)
    results = get_metadata_result_placeholders(db_path)
    receipts = get_metadata_receipt_drafts(db_path)
    prohibitions = get_object_body_download_prohibitions(db_path)
    blockers = get_controlled_metadata_test_blockers(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("REQUEST_DRAFT_COUNT_6", len(requests) == len(REQUEST_DRAFTS)),
        ("METADATA_SCOPE_COUNT_8", len(scopes) == len(METADATA_SCOPE_ITEMS)),
        ("APPROVAL_GATE_COUNT_6", len(gates) == len(REQUEST_DRAFTS)),
        ("QUERY_PLAN_STEP_COUNT_8", len(steps) == len(QUERY_PLAN_STEPS)),
        ("RESULT_PLACEHOLDER_COUNT_6", len(results) == len(RESULT_PLACEHOLDERS)),
        ("RECEIPT_DRAFT_COUNT_6", len(receipts) == len(REQUEST_DRAFTS)),
        ("PROHIBITION_COUNT_8", len(prohibitions) == len(PROHIBITION_ITEMS)),
        ("BLOCKER_COUNT_12", len(blockers) == len(BLOCKER_SPECS)),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("SAFE_TO_CONTINUE_TO_GP181", readiness["safe_to_continue_to_gp181"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("METADATA_TEST_LOCKED", readiness["metadata_test_locked"] is True),
        ("METADATA_ONLY", readiness["metadata_only"] is True),
        ("BODY_DOWNLOAD_PROHIBITED", readiness["body_download_prohibited"] is True),
        ("NO_PROVIDER_CONTACT", readiness["no_provider_contact"] is True),
        ("SECTION_GP171_GP180", readiness["section_range"] == "GP171-GP180"),
        ("NEXT_SECTION_GP181_GP190", readiness["readiness_payload"]["next_section_range"] == "GP181-GP190"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_LOCKED", all(item["component_locked"] is True for item in components)),
        ("ALL_COMPONENTS_METADATA_LOCKED", all(item["metadata_test_locked"] is True for item in components)),
        ("ALL_COMPONENTS_BODY_DOWNLOAD_PROHIBITED", all(item["body_download_prohibited"] is True for item in components)),
        ("ALL_REQUESTS_LOCKED", all(item["request_draft_locked"] is True for item in requests)),
        ("ALL_REQUESTS_NOT_SUBMITTED", all(item["metadata_test_request_submitted"] is False for item in requests)),
        ("ALL_SCOPES_LOCKED", all(item["scope_locked"] is True for item in scopes)),
        ("ALL_SCOPES_METADATA_ONLY", all(item["metadata_only"] is True for item in scopes)),
        ("ALL_SCOPES_BODY_DOWNLOAD_PROHIBITED", all(item["body_download_prohibited"] is True for item in scopes)),
        ("ALL_GATES_LOCKED", all(item["approval_gate_locked"] is True for item in gates)),
        ("ALL_GATES_NOT_APPROVED", all(item["metadata_read_approval_granted"] is False for item in gates)),
        ("ALL_QUERY_STEPS_LOCKED", all(item["query_plan_locked"] is True for item in steps)),
        ("ALL_QUERY_STEPS_NOT_EXECUTED", all(item["metadata_query_executed"] is False for item in steps)),
        ("ALL_RESULTS_PLACEHOLDER_LOCKED", all(item["result_placeholder_locked"] is True for item in results)),
        ("ALL_RESULTS_NO_PROVIDER_RESULT", all(item["no_provider_result"] is True for item in results)),
        ("ALL_RECEIPTS_DRAFT_LOCKED", all(item["receipt_draft_locked"] is True for item in receipts)),
        ("NO_FINAL_RECEIPTS", all(item["final_receipt_created"] is False for item in receipts)),
        ("ALL_PROHIBITIONS_ACTIVE", all(item["prohibition_active"] is True for item in prohibitions)),
        ("ALL_BLOCKERS_ACTIVE", all(item["blocker_active"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_REQUEST_SUBMIT", all(item["blocks_request_submit"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_METADATA_APPROVAL", all(item["blocks_metadata_approval"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_METADATA_QUERY", all(item["blocks_metadata_query"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", all(item["blocks_provider_api"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_METADATA_READ", all(item["blocks_metadata_read"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY", all(item["blocks_object_body"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DOWNLOAD", all(item["blocks_download"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DANGEROUS_OPS", all(item["blocks_restore"] and item["blocks_export"] and item["blocks_direct_upload"] and item["blocks_delete"] for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_EXECUTION_DONE", all(item["blocks_execution"] and item["blocks_vault_done"] for item in blockers)),
        ("NO_BLOCKERS_RESOLVED", all(item["resolved"] is False for item in blockers)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("REQUEST", requests),
        ("SCOPE", scopes),
        ("GATE", gates),
        ("STEP", steps),
        ("RESULT", results),
        ("RECEIPT", receipts),
        ("PROHIBITION", prohibitions),
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
        "metadata_scope_count": len(scopes),
        "approval_gate_count": len(gates),
        "query_plan_step_count": len(steps),
        "result_placeholder_count": len(results),
        "receipt_draft_count": len(receipts),
        "prohibition_count": len(prohibitions),
        "blocker_count": len(blockers),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "safe_to_continue_to_gp181": len(failed) == 0 and readiness["safe_to_continue_to_gp181"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp171_controlled_read_only_metadata_test_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(METADATA_TEST_SHELL_ID, db_path)
    return {"pack": _pack_payload(171, component["pack_name"]), "real_sqlite_backed": True, "metadata_test_shell": component}

def get_gp172_metadata_test_request_draft_registry(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(REQUEST_DRAFT_REGISTRY_ID, db_path)
    requests = get_metadata_test_request_drafts(db_path)
    return {"pack": _pack_payload(172, component["pack_name"]), "real_sqlite_backed": True, "request_draft_registry": component, "request_draft_count": len(requests), "requests": requests}

def get_gp173_metadata_scope_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(METADATA_SCOPE_CONTRACT_ID, db_path)
    scopes = get_metadata_scope_items(db_path)
    return {"pack": _pack_payload(173, component["pack_name"]), "real_sqlite_backed": True, "metadata_scope_contract": component, "metadata_scope_count": len(scopes), "scopes": scopes}

def get_gp174_metadata_read_approval_gate_lock(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(APPROVAL_GATE_LOCK_ID, db_path)
    gates = get_metadata_read_approval_gates(db_path)
    return {"pack": _pack_payload(174, component["pack_name"]), "real_sqlite_backed": True, "approval_gate_lock": component, "approval_gate_count": len(gates), "gates": gates}

def get_gp175_metadata_query_plan_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(QUERY_PLAN_LOCK_ID, db_path)
    steps = get_metadata_query_plan_steps(db_path)
    return {"pack": _pack_payload(175, component["pack_name"]), "real_sqlite_backed": True, "query_plan_lock_contract": component, "query_plan_step_count": len(steps), "steps": steps}

def get_gp176_metadata_result_placeholder_queue(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RESULT_PLACEHOLDER_QUEUE_ID, db_path)
    results = get_metadata_result_placeholders(db_path)
    return {"pack": _pack_payload(176, component["pack_name"]), "real_sqlite_backed": True, "result_placeholder_queue": component, "result_placeholder_count": len(results), "results": results}

def get_gp177_metadata_receipt_draft_ledger(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RECEIPT_DRAFT_LEDGER_ID, db_path)
    receipts = get_metadata_receipt_drafts(db_path)
    return {"pack": _pack_payload(177, component["pack_name"]), "real_sqlite_backed": True, "receipt_draft_ledger": component, "receipt_draft_count": len(receipts), "receipt_drafts": receipts}

def get_gp178_object_body_download_prohibition_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(BODY_DOWNLOAD_PROHIBITION_ID, db_path)
    prohibitions = get_object_body_download_prohibitions(db_path)
    return {"pack": _pack_payload(178, component["pack_name"]), "real_sqlite_backed": True, "object_body_download_prohibition_contract": component, "prohibition_count": len(prohibitions), "prohibitions": prohibitions}

def get_gp179_controlled_metadata_test_blocker_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(BLOCKER_BOARD_ID, db_path)
    blockers = get_controlled_metadata_test_blockers(db_path)
    return {"pack": _pack_payload(179, component["pack_name"]), "real_sqlite_backed": True, "blocker_board": component, "blocker_count": len(blockers), "blockers": blockers}

def get_gp180_controlled_metadata_test_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_controlled_read_only_metadata_test_layer(db_path)
    return {"pack": _pack_payload(180, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_controlled_read_only_metadata_test_layer(db_path)
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
            "source_gp170_readiness_id": component["source_gp170_readiness_id"],
            "source_gp170_readiness_hash": component["source_gp170_readiness_hash"],
            "source_gp170_readiness_score": component["source_gp170_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "metadata_test_locked": component["metadata_test_locked"],
            "metadata_only": component["metadata_only"],
            "body_download_prohibited": component["body_download_prohibited"],
            "no_provider_contact": component["no_provider_contact"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp181": validation["safe_to_continue_to_gp181"],
            "foundation_status": "controlled_read_only_metadata_test_layer_ready_locked_safe_to_continue_not_done",
            "next": next_label,
            **counts,
            "metadata_test_request_submitted": component["metadata_test_request_submitted"],
            "metadata_test_request_approved": component["metadata_test_request_approved"],
            "metadata_read_approval_granted": component["metadata_read_approval_granted"],
            "metadata_test_authorized": component["metadata_test_authorized"],
            "metadata_test_run_started": component["metadata_test_run_started"],
            "metadata_test_run_completed": component["metadata_test_run_completed"],
            "metadata_query_executed": component["metadata_query_executed"],
            "metadata_query_result_imported": component["metadata_query_result_imported"],
            "metadata_query_result_persisted": component["metadata_query_result_persisted"],
            "metadata_test_result_recorded": component["metadata_test_result_recorded"],
            "metadata_test_receipt_finalized": component["metadata_test_receipt_finalized"],
            "real_provider_connection_started": component["real_provider_connection_started"],
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
            "object_download_enabled": component["object_download_enabled"],
            "object_delete_executed": component["object_delete_executed"],
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
            "clouds_status": "parked_do_not_continue_from_vault_gp180",
        },
        "validation": validation,
    }

def get_gp171_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(171, METADATA_TEST_SHELL_ID, "VAULT_GP172_METADATA_TEST_REQUEST_DRAFT_REGISTRY", db_path)

def get_gp172_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(172, REQUEST_DRAFT_REGISTRY_ID, "VAULT_GP173_METADATA_SCOPE_CONTRACT", db_path)

def get_gp173_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(173, METADATA_SCOPE_CONTRACT_ID, "VAULT_GP174_METADATA_READ_APPROVAL_GATE_LOCK", db_path)

def get_gp174_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(174, APPROVAL_GATE_LOCK_ID, "VAULT_GP175_METADATA_QUERY_PLAN_LOCK_CONTRACT", db_path)

def get_gp175_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(175, QUERY_PLAN_LOCK_ID, "VAULT_GP176_METADATA_RESULT_PLACEHOLDER_QUEUE", db_path)

def get_gp176_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(176, RESULT_PLACEHOLDER_QUEUE_ID, "VAULT_GP177_METADATA_RECEIPT_DRAFT_LEDGER", db_path)

def get_gp177_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(177, RECEIPT_DRAFT_LEDGER_ID, "VAULT_GP178_OBJECT_BODY_DOWNLOAD_PROHIBITION_CONTRACT", db_path)

def get_gp178_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(178, BODY_DOWNLOAD_PROHIBITION_ID, "VAULT_GP179_CONTROLLED_METADATA_TEST_BLOCKER_BOARD", db_path)

def get_gp179_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(179, BLOCKER_BOARD_ID, "VAULT_GP180_CONTROLLED_METADATA_TEST_READINESS_CHECKPOINT", db_path)

def get_gp180_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(180, READINESS_ID, NEXT_PACK, db_path)
    status["gp180_status"]["next_section"] = NEXT_SECTION_ID
    status["gp180_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp180_status"]["next_pack"] = NEXT_PACK
    return status

def get_controlled_read_only_metadata_test_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_controlled_read_only_metadata_test_layer(db_path)
    components = _rows("vault_controlled_metadata_test_components", "gp_number", db_path, {"data_json": "data"})
    requests = get_metadata_test_request_drafts(db_path)
    scopes = get_metadata_scope_items(db_path)
    gates = get_metadata_read_approval_gates(db_path)
    steps = get_metadata_query_plan_steps(db_path)
    results = get_metadata_result_placeholders(db_path)
    receipts = get_metadata_receipt_drafts(db_path)
    prohibitions = get_object_body_download_prohibitions(db_path)
    blockers = get_controlled_metadata_test_blockers(db_path)
    readiness = _readiness(db_path)
    validation = validate_controlled_read_only_metadata_test_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "requests": {"request_draft_count": len(requests), "requests": requests},
        "metadata_scope": {"metadata_scope_count": len(scopes), "scopes": scopes},
        "approval_gates": {"approval_gate_count": len(gates), "gates": gates},
        "query_plan": {"query_plan_step_count": len(steps), "steps": steps},
        "results": {"result_placeholder_count": len(results), "results": results},
        "receipts": {"receipt_draft_count": len(receipts), "receipt_drafts": receipts},
        "prohibitions": {"prohibition_count": len(prohibitions), "prohibitions": prohibitions},
        "blockers": {"blocker_count": len(blockers), "blockers": blockers},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "controlled_read_only_metadata_test_layer_ready": True,
            "metadata_test_locked": True,
            "metadata_only": True,
            "body_download_prohibited": True,
            "safe_to_continue_to_gp181": validation["safe_to_continue_to_gp181"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "no_provider_contact": True,
            "metadata_test_request_submitted": False,
            "metadata_test_request_approved": False,
            "metadata_read_approval_granted": False,
            "metadata_test_authorized": False,
            "metadata_test_run_started": False,
            "metadata_test_run_completed": False,
            "metadata_query_executed": False,
            "metadata_query_result_imported": False,
            "metadata_test_result_recorded": False,
            "metadata_test_receipt_finalized": False,
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
            "object_download_enabled": False,
            "object_delete_executed": False,
            "export_package_created": False,
            "restore_job_created": False,
            "direct_upload_enabled": False,
            "tower_unlock_granted": False,
            "execution_enabled": False,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        "routes": {
            "page": "/vault/controlled-read-only-metadata-test-layer",
            "json": "/vault/controlled-read-only-metadata-test-layer.json",
            "gp171": "/vault/gp171-status.json",
            "gp172": "/vault/gp172-status.json",
            "gp173": "/vault/gp173-status.json",
            "gp174": "/vault/gp174-status.json",
            "gp175": "/vault/gp175-status.json",
            "gp176": "/vault/gp176-status.json",
            "gp177": "/vault/gp177-status.json",
            "gp178": "/vault/gp178-status.json",
            "gp179": "/vault/gp179-status.json",
            "gp180": "/vault/gp180-status.json",
        },
    }

def render_controlled_read_only_metadata_test_layer_page() -> str:
    home = get_controlled_read_only_metadata_test_layer_home()
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

    scope_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['scope_name'])}</strong>
          <span>{escape(item['scope_status'])}</span>
          <code>metadata only · no body</code>
        </article>
        """
        for item in home["metadata_scope"]["scopes"]
    )

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP171-GP180 Controlled Read-Only Metadata Test Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 171-180</div>
    <div class="eyebrow">Controlled Read-Only Metadata Test Layer · GP171-GP180</div>
    <h1>Controlled Read-Only Metadata Test</h1>
    <p>This layer prepares a metadata-only test surface while keeping the actual provider read locked. Object bodies, downloads, restore, export, upload, delete, and execution are prohibited.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['request_draft_count']}</strong><span>request drafts</span></div>
      <div class="metric"><strong>{home['store']['metadata_scope_count']}</strong><span>metadata scope items</span></div>
      <div class="metric"><strong>{home['store']['blocker_count']}</strong><span>active blockers</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP171-GP180 built</span>
      <span class="pill ok">Metadata only</span>
      <span class="pill ok">Body/download prohibited</span>
      <span class="pill ok">Safe to GP181</span>
      <span class="pill danger">No metadata read</span>
      <span class="pill danger">No provider API</span>
      <span class="pill danger">No object body</span>
      <span class="pill danger">No download</span>
      <span class="pill danger">No restore/export/upload/delete</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Metadata Test Request Drafts</h2>
    <div class="cards">{request_cards}</div>
  </section>

  <section class="section">
    <h2>Metadata Scope</h2>
    <div class="cards">{scope_cards}</div>
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
