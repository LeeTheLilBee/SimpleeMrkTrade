"""
VAULT GP151-GP160 — Real Provider Connection Readiness Layer

New section:
Archive Vault — Real Provider Connection Readiness Layer / GP151-GP160

Builds:
- GP151 Real Provider Connection Readiness Shell
- GP152 Provider Configuration Status Dashboard
- GP153 Credential Boundary Review Panel
- GP154 Endpoint Namespace Review Panel
- GP155 Encryption Readiness Review Panel
- GP156 Provider Connection Preflight Checklist
- GP157 Provider Health Placeholder Panel
- GP158 Connection Test Lock Validation
- GP159 Real Provider Connection Readiness Blocker Board
- GP160 Real Provider Connection Readiness Checkpoint

This is readiness-only. It organizes the connection-readiness surface for future
real provider work without connecting, calling provider APIs, reading secrets,
creating tokens/sessions/jobs, listing objects, importing metadata, reading body
content, downloading, restoring, exporting, uploading, executing, or marking
Vault done.
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

from vault.provider_readiness_simulation_dry_run_layer_service import (
    get_gp150_status,
    get_gp150_provider_readiness_simulation_checkpoint,
    get_provider_readiness_simulation_dry_run_layer_home,
    validate_provider_readiness_simulation_dry_run_layer,
    get_provider_dry_run_scenarios,
    get_provider_dry_run_plans,
    get_provider_dry_run_review_queue,
    get_provider_simulation_blockers,
)

LAYER_ID = "VAULT_GP151_160"
LAYER_NAME = "Real Provider Connection Readiness Layer"
SCHEMA_VERSION = "vault.real_provider_connection_readiness_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_CONNECTION_READINESS_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Connection Readiness Layer"
SECTION_RANGE = "GP151-GP160"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_PROVIDER_READINESS_SIMULATION_AND_DRY_RUN_LAYER"
PREVIOUS_SECTION_RANGE = "GP141-GP150"

NEXT_SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PROVIDER_CONNECTION_TEST_LOCK_LAYER"
NEXT_SECTION_RANGE = "GP161-GP170"
NEXT_PACK = "VAULT_GP161_170_CONTROLLED_PROVIDER_CONNECTION_TEST_LOCK_LAYER"

DEFAULT_DB_ENV = "VAULT_REAL_PROVIDER_CONNECTION_READINESS_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_real_provider_connection_readiness_layer.sqlite"

CONNECTION_READINESS_SHELL_ID = "VRPCR-SHELL-GP151-001"
CONFIG_STATUS_DASHBOARD_ID = "VRPCR-CONFIG-GP152-001"
CREDENTIAL_BOUNDARY_PANEL_ID = "VRPCR-CREDENTIAL-GP153-001"
ENDPOINT_NAMESPACE_PANEL_ID = "VRPCR-ENDPOINT-GP154-001"
ENCRYPTION_READINESS_PANEL_ID = "VRPCR-ENCRYPTION-GP155-001"
CONNECTION_PREFLIGHT_ID = "VRPCR-PREFLIGHT-GP156-001"
PROVIDER_HEALTH_PLACEHOLDER_ID = "VRPCR-HEALTH-GP157-001"
CONNECTION_LOCK_VALIDATION_ID = "VRPCR-LOCKVAL-GP158-001"
READINESS_BLOCKER_BOARD_ID = "VRPCR-BLOCKER-GP159-001"
READINESS_ID = "VRPCR-READINESS-GP160-001"

FALSE_FIELDS = [
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

CONFIG_ITEMS = [
    ("provider_adapter_placeholder", "Provider Adapter Placeholder", "config", "READINESS_PLACEHOLDER_LOCKED"),
    ("provider_region_placeholder", "Provider Region Placeholder", "config", "READINESS_PLACEHOLDER_LOCKED"),
    ("provider_account_scope_placeholder", "Provider Account Scope Placeholder", "config", "READINESS_PLACEHOLDER_LOCKED"),
    ("provider_mode_gate_placeholder", "Provider Mode Gate Placeholder", "config", "READINESS_PLACEHOLDER_LOCKED"),
]

CREDENTIAL_ITEMS = [
    ("credential_reference_key_present", "Credential Reference Key Present", "credential", "REFERENCE_ONLY_NO_SECRET_VALUE"),
    ("credential_storage_boundary_reviewed", "Credential Storage Boundary Reviewed", "credential", "REFERENCE_ONLY_NO_SECRET_VALUE"),
    ("secret_value_redaction_enforced", "Secret Value Redaction Enforced", "credential", "REFERENCE_ONLY_NO_SECRET_VALUE"),
    ("credential_rotation_placeholder", "Credential Rotation Placeholder", "credential", "REFERENCE_ONLY_NO_SECRET_VALUE"),
]

ENDPOINT_ITEMS = [
    ("endpoint_namespace_placeholder", "Endpoint Namespace Placeholder", "endpoint", "NAMESPACE_ONLY_NO_ENDPOINT_CALL"),
    ("endpoint_allowlist_placeholder", "Endpoint Allowlist Placeholder", "endpoint", "NAMESPACE_ONLY_NO_ENDPOINT_CALL"),
    ("endpoint_method_scope_placeholder", "Endpoint Method Scope Placeholder", "endpoint", "NAMESPACE_ONLY_NO_ENDPOINT_CALL"),
    ("endpoint_timeout_policy_placeholder", "Endpoint Timeout Policy Placeholder", "endpoint", "NAMESPACE_ONLY_NO_ENDPOINT_CALL"),
]

ENCRYPTION_ITEMS = [
    ("encryption_policy_reference", "Encryption Policy Reference", "encryption", "POLICY_READY_NO_DATA_ACCESS"),
    ("key_reference_boundary", "Key Reference Boundary", "encryption", "POLICY_READY_NO_KEY_VALUE"),
    ("at_rest_encryption_placeholder", "At-Rest Encryption Placeholder", "encryption", "POLICY_READY_NO_DATA_ACCESS"),
    ("in_transit_encryption_placeholder", "In-Transit Encryption Placeholder", "encryption", "POLICY_READY_NO_ENDPOINT_CALL"),
]

PREFLIGHT_ITEMS = [
    ("tower_gate_lock_confirmed", "Tower Gate Lock Confirmed", "preflight", "LOCK_CONFIRMED"),
    ("provider_api_lock_confirmed", "Provider API Lock Confirmed", "preflight", "LOCK_CONFIRMED"),
    ("secret_value_lock_confirmed", "Secret Value Lock Confirmed", "preflight", "LOCK_CONFIRMED"),
    ("object_body_lock_confirmed", "Object Body Lock Confirmed", "preflight", "LOCK_CONFIRMED"),
    ("export_restore_lock_confirmed", "Export/Restore Lock Confirmed", "preflight", "LOCK_CONFIRMED"),
    ("execution_lock_confirmed", "Execution Lock Confirmed", "preflight", "LOCK_CONFIRMED"),
]

HEALTH_PLACEHOLDERS = [
    ("provider_health_placeholder", "Provider Health Placeholder", "health", "PLACEHOLDER_NO_HEALTH_CALL"),
    ("provider_latency_placeholder", "Provider Latency Placeholder", "health", "PLACEHOLDER_NO_HEALTH_CALL"),
    ("provider_availability_placeholder", "Provider Availability Placeholder", "health", "PLACEHOLDER_NO_HEALTH_CALL"),
    ("provider_error_budget_placeholder", "Provider Error Budget Placeholder", "health", "PLACEHOLDER_NO_HEALTH_CALL"),
]

LOCK_VALIDATIONS = [
    ("connection_start_lock", "Connection Start Lock", "connection_lock", "LOCKED"),
    ("provider_api_call_lock", "Provider API Call Lock", "connection_lock", "LOCKED"),
    ("provider_token_session_lock", "Provider Token/Session Lock", "connection_lock", "LOCKED"),
    ("provider_job_reference_lock", "Provider Job Reference Lock", "connection_lock", "LOCKED"),
    ("provider_status_poll_lock", "Provider Status Poll Lock", "connection_lock", "LOCKED"),
    ("object_catalog_lock", "Object Catalog Lock", "connection_lock", "LOCKED"),
    ("secret_value_lock", "Secret Value Lock", "connection_lock", "LOCKED"),
    ("object_body_download_lock", "Object Body/Download Lock", "connection_lock", "LOCKED"),
]

READINESS_ITEM_GROUPS = {
    "configuration": CONFIG_ITEMS,
    "credential_boundary": CREDENTIAL_ITEMS,
    "endpoint_namespace": ENDPOINT_ITEMS,
    "encryption": ENCRYPTION_ITEMS,
    "preflight": PREFLIGHT_ITEMS,
    "health_placeholder": HEALTH_PLACEHOLDERS,
    "connection_lock_validation": LOCK_VALIDATIONS,
}

BLOCKER_SPECS = [
    ("tower_unlock_missing", "Tower unlock missing", "tower", "critical"),
    ("step_up_not_passed", "Step-up not passed", "tower", "critical"),
    ("real_connection_locked", "Real provider connection locked", "connection", "critical"),
    ("provider_api_locked", "Provider API locked", "provider_api", "critical"),
    ("credential_secret_value_locked", "Credential/secret value locked", "credential", "critical"),
    ("endpoint_call_locked", "Endpoint call locked", "endpoint", "critical"),
    ("provider_token_session_locked", "Provider token/session locked", "token_session", "critical"),
    ("provider_job_status_locked", "Provider job/status poll locked", "provider_job", "critical"),
    ("object_catalog_metadata_locked", "Object catalog and metadata import locked", "metadata", "high"),
    ("object_body_download_locked", "Object body and download locked", "object_body", "critical"),
    ("restore_export_upload_locked", "Restore/export/upload locked", "restore_export_upload", "critical"),
    ("execution_vault_done_locked", "Execution and Vault done locked", "execution", "critical"),
]

COMPONENT_SPECS = [
    (151, CONNECTION_READINESS_SHELL_ID, "VAULT_GP151", "Real Provider Connection Readiness Shell", "real_provider_connection_readiness_shell"),
    (152, CONFIG_STATUS_DASHBOARD_ID, "VAULT_GP152", "Provider Configuration Status Dashboard", "provider_configuration_status_dashboard"),
    (153, CREDENTIAL_BOUNDARY_PANEL_ID, "VAULT_GP153", "Credential Boundary Review Panel", "credential_boundary_review_panel"),
    (154, ENDPOINT_NAMESPACE_PANEL_ID, "VAULT_GP154", "Endpoint Namespace Review Panel", "endpoint_namespace_review_panel"),
    (155, ENCRYPTION_READINESS_PANEL_ID, "VAULT_GP155", "Encryption Readiness Review Panel", "encryption_readiness_review_panel"),
    (156, CONNECTION_PREFLIGHT_ID, "VAULT_GP156", "Provider Connection Preflight Checklist", "provider_connection_preflight_checklist"),
    (157, PROVIDER_HEALTH_PLACEHOLDER_ID, "VAULT_GP157", "Provider Health Placeholder Panel", "provider_health_placeholder_panel"),
    (158, CONNECTION_LOCK_VALIDATION_ID, "VAULT_GP158", "Connection Test Lock Validation", "connection_test_lock_validation"),
    (159, READINESS_BLOCKER_BOARD_ID, "VAULT_GP159", "Real Provider Connection Readiness Blocker Board", "real_provider_connection_readiness_blocker_board"),
    (160, READINESS_ID, "VAULT_GP160", "Real Provider Connection Readiness Checkpoint", "real_provider_connection_readiness_checkpoint"),
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
        "source_gp150_readiness_score",
        "component_count",
        "configuration_item_count",
        "credential_item_count",
        "endpoint_item_count",
        "encryption_item_count",
        "preflight_item_count",
        "health_placeholder_count",
        "connection_lock_count",
        "readiness_item_count",
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
        "depends_on": ["VAULT_GP150"],
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
        "depends_on": ["VAULT_GP150"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_real_provider_connection_readiness_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_real_provider_connection_readiness_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp150_readiness_id TEXT NOT NULL,
                source_gp150_readiness_hash TEXT NOT NULL,
                source_gp150_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                readiness_only INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_real_provider_connection_readiness_items (
                item_id TEXT PRIMARY KEY,
                item_code TEXT NOT NULL UNIQUE,
                item_name TEXT NOT NULL,
                item_group TEXT NOT NULL,
                item_category TEXT NOT NULL,
                item_status TEXT NOT NULL,
                source_gp150_readiness_hash TEXT NOT NULL,
                item_ready INTEGER NOT NULL DEFAULT 1,
                item_locked INTEGER NOT NULL DEFAULT 1,
                readiness_only INTEGER NOT NULL DEFAULT 1,
                no_provider_contact INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                item_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_real_provider_connection_readiness_blockers (
                blocker_id TEXT PRIMARY KEY,
                blocker_code TEXT NOT NULL UNIQUE,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocker_active INTEGER NOT NULL DEFAULT 1,
                blocks_real_connection INTEGER NOT NULL DEFAULT 1,
                blocks_provider_api INTEGER NOT NULL DEFAULT 1,
                blocks_credentials INTEGER NOT NULL DEFAULT 1,
                blocks_secret_read INTEGER NOT NULL DEFAULT 1,
                blocks_endpoint_call INTEGER NOT NULL DEFAULT 1,
                blocks_provider_token INTEGER NOT NULL DEFAULT 1,
                blocks_provider_session INTEGER NOT NULL DEFAULT 1,
                blocks_provider_job INTEGER NOT NULL DEFAULT 1,
                blocks_status_poll INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_real_provider_connection_readiness_checkpoint (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                configuration_item_count INTEGER NOT NULL,
                credential_item_count INTEGER NOT NULL,
                endpoint_item_count INTEGER NOT NULL,
                encryption_item_count INTEGER NOT NULL,
                preflight_item_count INTEGER NOT NULL,
                health_placeholder_count INTEGER NOT NULL,
                connection_lock_count INTEGER NOT NULL,
                readiness_item_count INTEGER NOT NULL,
                blocker_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                safe_to_continue_to_gp161 INTEGER NOT NULL DEFAULT 1,
                section_ready INTEGER NOT NULL DEFAULT 1,
                readiness_only INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_real_provider_connection_readiness_events (
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
            "vault_real_provider_connection_readiness_components",
            "vault_real_provider_connection_readiness_items",
            "vault_real_provider_connection_readiness_blockers",
            "vault_real_provider_connection_readiness_checkpoint",
            "vault_real_provider_connection_readiness_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VRPCREVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_real_provider_connection_readiness_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_real_provider_connection_readiness_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_real_provider_connection_readiness_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_real_provider_connection_readiness_components WHERE component_id = ?",
            (CONNECTION_READINESS_SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp150_status = get_gp150_status()["gp150_status"]
            gp150_checkpoint = get_gp150_provider_readiness_simulation_checkpoint()["readiness_checkpoint"]
            gp150_home = get_provider_readiness_simulation_dry_run_layer_home()
            gp150_validation = validate_provider_readiness_simulation_dry_run_layer()

            source_scenarios = get_provider_dry_run_scenarios()
            source_plans = get_provider_dry_run_plans()
            source_reviews = get_provider_dry_run_review_queue()
            source_blockers = get_provider_simulation_blockers()

            readiness = gp150_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp150_readiness_id": readiness["readiness_id"],
                "source_gp150_readiness_hash": readiness["readiness_hash"],
                "source_gp150_readiness_score": readiness["readiness_score"],
            }

            group_counts = {
                "configuration_item_count": len(CONFIG_ITEMS),
                "credential_item_count": len(CREDENTIAL_ITEMS),
                "endpoint_item_count": len(ENDPOINT_ITEMS),
                "encryption_item_count": len(ENCRYPTION_ITEMS),
                "preflight_item_count": len(PREFLIGHT_ITEMS),
                "health_placeholder_count": len(HEALTH_PLACEHOLDERS),
                "connection_lock_count": len(LOCK_VALIDATIONS),
            }
            readiness_item_count = sum(group_counts.values())

            source_context = {
                "source_gp150_status_ready": gp150_status["ready"],
                "source_gp150_validation_passed": gp150_status["validation_passed"],
                "source_gp150_safe_to_continue_to_gp151": gp150_status["safe_to_continue_to_gp151"],
                "source_gp150_readiness_hash": readiness["readiness_hash"],
                "source_gp150_readiness_score": readiness["readiness_score"],
                "source_scenario_count": len(source_scenarios),
                "source_plan_count": len(source_plans),
                "source_review_item_count": len(source_reviews),
                "source_blocker_count": len(source_blockers),
                "source_validation_check_count": gp150_validation["check_count"],
            }

            component_extra = {
                CONNECTION_READINESS_SHELL_ID: {"real_provider_connection_readiness_shell_ready": True},
                CONFIG_STATUS_DASHBOARD_ID: {"provider_configuration_status_dashboard_ready": True, "configuration_item_count": len(CONFIG_ITEMS)},
                CREDENTIAL_BOUNDARY_PANEL_ID: {"credential_boundary_review_panel_ready": True, "credential_item_count": len(CREDENTIAL_ITEMS)},
                ENDPOINT_NAMESPACE_PANEL_ID: {"endpoint_namespace_review_panel_ready": True, "endpoint_item_count": len(ENDPOINT_ITEMS)},
                ENCRYPTION_READINESS_PANEL_ID: {"encryption_readiness_review_panel_ready": True, "encryption_item_count": len(ENCRYPTION_ITEMS)},
                CONNECTION_PREFLIGHT_ID: {"provider_connection_preflight_checklist_ready": True, "preflight_item_count": len(PREFLIGHT_ITEMS)},
                PROVIDER_HEALTH_PLACEHOLDER_ID: {"provider_health_placeholder_panel_ready": True, "health_placeholder_count": len(HEALTH_PLACEHOLDERS)},
                CONNECTION_LOCK_VALIDATION_ID: {"connection_test_lock_validation_ready": True, "connection_lock_count": len(LOCK_VALIDATIONS)},
                READINESS_BLOCKER_BOARD_ID: {"real_provider_connection_readiness_blocker_board_ready": True, "blocker_count": len(BLOCKER_SPECS)},
                READINESS_ID: {"real_provider_connection_readiness_checkpoint_ready": True, "safe_to_continue_to_gp161": True},
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
                    "readiness_only": True,
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
                    "readiness_only": 1,
                    "no_provider_contact": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_real_provider_connection_readiness_components", row)

            item_index = 1
            for group_name, item_specs in READINESS_ITEM_GROUPS.items():
                for code, name, category, status in item_specs:
                    item_id = f"VRPCRI-{item_index:03d}"
                    payload = {
                        "schema_version": SCHEMA_VERSION,
                        "item_id": item_id,
                        "item_code": code,
                        "item_name": name,
                        "item_group": group_name,
                        "item_category": category,
                        "item_status": status,
                        "source_gp150_readiness_hash": readiness["readiness_hash"],
                        "item_ready": True,
                        "item_locked": True,
                        "readiness_only": True,
                        "no_provider_contact": True,
                        "allowed_actions": ["view_status", "review_boundary", "confirm_lock", "prepare_questions"],
                        "blocked_actions": ["connect_provider", "call_endpoint", "read_secret_value", "persist_secret_value", "create_token", "create_session", "list_objects", "import_metadata", "read_body", "download", "restore", "export", "upload", "execute"],
                        "locked_truth": {field: False for field in FALSE_FIELDS},
                        "vault_done": False,
                        "clouds_should_continue": False,
                    }
                    row = {
                        "item_id": item_id,
                        "item_code": code,
                        "item_name": name,
                        "item_group": group_name,
                        "item_category": category,
                        "item_status": status,
                        "source_gp150_readiness_hash": readiness["readiness_hash"],
                        "item_ready": 1,
                        "item_locked": 1,
                        "readiness_only": 1,
                        "no_provider_contact": 1,
                        "payload_json": _json_dumps(payload),
                        "item_hash": _hash_payload(payload),
                        "created_at": now,
                        "updated_at": now,
                    }
                    for field in FALSE_FIELDS:
                        row[field] = 0
                    _insert_dict(conn, "vault_real_provider_connection_readiness_items", row)
                    item_index += 1

            for idx, (code, name, category, severity) in enumerate(BLOCKER_SPECS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "ACTIVE_REAL_PROVIDER_CONNECTION_READINESS_BLOCKER",
                    "blocker_active": True,
                    "blocks_real_connection": True,
                    "blocks_provider_api": True,
                    "blocks_credentials": True,
                    "blocks_secret_read": True,
                    "blocks_endpoint_call": True,
                    "blocks_provider_token": True,
                    "blocks_provider_session": True,
                    "blocks_provider_job": True,
                    "blocks_status_poll": True,
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
                    "blocker_id": f"VRPCRB-{idx:03d}",
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": payload["blocker_status"],
                    "blocker_active": 1,
                    "blocks_real_connection": 1,
                    "blocks_provider_api": 1,
                    "blocks_credentials": 1,
                    "blocks_secret_read": 1,
                    "blocks_endpoint_call": 1,
                    "blocks_provider_token": 1,
                    "blocks_provider_session": 1,
                    "blocks_provider_job": 1,
                    "blocks_status_poll": 1,
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
                _insert_dict(conn, "vault_real_provider_connection_readiness_blockers", row)

            counts = {
                "component_count": len(COMPONENT_SPECS),
                **group_counts,
                "readiness_item_count": readiness_item_count,
                "blocker_count": len(BLOCKER_SPECS),
            }

            checks = [
                ("SOURCE_GP150_READY", bool(gp150_status["ready"])),
                ("SOURCE_GP150_VALIDATION_PASSED", bool(gp150_status["validation_passed"])),
                ("SOURCE_GP150_SAFE_TO_CONTINUE", bool(gp150_status["safe_to_continue_to_gp151"])),
                ("SOURCE_GP150_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP150_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("CONFIGURATION_ITEM_COUNT_4", counts["configuration_item_count"] == 4),
                ("CREDENTIAL_ITEM_COUNT_4", counts["credential_item_count"] == 4),
                ("ENDPOINT_ITEM_COUNT_4", counts["endpoint_item_count"] == 4),
                ("ENCRYPTION_ITEM_COUNT_4", counts["encryption_item_count"] == 4),
                ("PREFLIGHT_ITEM_COUNT_6", counts["preflight_item_count"] == 6),
                ("HEALTH_PLACEHOLDER_COUNT_4", counts["health_placeholder_count"] == 4),
                ("CONNECTION_LOCK_COUNT_8", counts["connection_lock_count"] == 8),
                ("READINESS_ITEM_COUNT_34", counts["readiness_item_count"] == 34),
                ("BLOCKER_COUNT_12", counts["blocker_count"] == 12),
                ("SECTION_GP151_GP160", SECTION_RANGE == "GP151-GP160"),
                ("NEXT_SECTION_GP161_GP170", NEXT_SECTION_RANGE == "GP161-GP170"),
                ("READINESS_ONLY", True),
                ("NO_PROVIDER_CONTACT", True),
                ("NO_REAL_CONNECTION", True),
                ("NO_PROVIDER_API", True),
                ("NO_CREDENTIAL_SECRET_VALUE_READ", True),
                ("NO_CREDENTIAL_SECRET_VALUE_PERSIST", True),
                ("NO_ENDPOINT_CALL", True),
                ("NO_PROVIDER_TOKEN_SESSION_JOB", True),
                ("NO_STATUS_POLL", True),
                ("NO_OBJECT_CATALOG", True),
                ("NO_METADATA_IMPORT", True),
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
                "gp_number": 160,
                "pack_id": "VAULT_GP160",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp150_readiness_id": readiness["readiness_id"],
                "source_gp150_readiness_hash": readiness["readiness_hash"],
                "source_gp150_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "safe_to_continue_to_gp161": failed_count == 0,
                "section_ready": True,
                "readiness_only": True,
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
                "gp_number": 160,
                "pack_id": "VAULT_GP160",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "REAL_PROVIDER_CONNECTION_READINESS_LAYER_READY_LOCKED_SAFE_TO_CONTINUE_NOT_DONE",
                "readiness_score": readiness_payload["readiness_score"],
                **counts,
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "safe_to_continue_to_gp161": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "readiness_only": 1,
                "no_provider_contact": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_real_provider_connection_readiness_checkpoint", row)

            for event_type, event_payload in [
                ("GP151_REAL_PROVIDER_CONNECTION_READINESS_SHELL_CREATED", {"component_id": CONNECTION_READINESS_SHELL_ID}),
                ("GP152_PROVIDER_CONFIGURATION_STATUS_DASHBOARD_CREATED", {"configuration_item_count": counts["configuration_item_count"]}),
                ("GP153_CREDENTIAL_BOUNDARY_REVIEW_PANEL_CREATED", {"credential_item_count": counts["credential_item_count"]}),
                ("GP154_ENDPOINT_NAMESPACE_REVIEW_PANEL_CREATED", {"endpoint_item_count": counts["endpoint_item_count"]}),
                ("GP155_ENCRYPTION_READINESS_REVIEW_PANEL_CREATED", {"encryption_item_count": counts["encryption_item_count"]}),
                ("GP156_PROVIDER_CONNECTION_PREFLIGHT_CHECKLIST_CREATED", {"preflight_item_count": counts["preflight_item_count"]}),
                ("GP157_PROVIDER_HEALTH_PLACEHOLDER_PANEL_CREATED", {"health_placeholder_count": counts["health_placeholder_count"]}),
                ("GP158_CONNECTION_TEST_LOCK_VALIDATION_CREATED", {"connection_lock_count": counts["connection_lock_count"]}),
                ("GP159_REAL_PROVIDER_CONNECTION_READINESS_BLOCKER_BOARD_CREATED", {"blocker_count": counts["blocker_count"]}),
                ("GP160_REAL_PROVIDER_CONNECTION_READINESS_CHECKPOINT_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp161": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_real_provider_connection_readiness_components").fetchone()["c"]),
            "configuration_item_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_real_provider_connection_readiness_items WHERE item_group='configuration'").fetchone()["c"]),
            "credential_item_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_real_provider_connection_readiness_items WHERE item_group='credential_boundary'").fetchone()["c"]),
            "endpoint_item_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_real_provider_connection_readiness_items WHERE item_group='endpoint_namespace'").fetchone()["c"]),
            "encryption_item_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_real_provider_connection_readiness_items WHERE item_group='encryption'").fetchone()["c"]),
            "preflight_item_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_real_provider_connection_readiness_items WHERE item_group='preflight'").fetchone()["c"]),
            "health_placeholder_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_real_provider_connection_readiness_items WHERE item_group='health_placeholder'").fetchone()["c"]),
            "connection_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_real_provider_connection_readiness_items WHERE item_group='connection_lock_validation'").fetchone()["c"]),
            "readiness_item_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_real_provider_connection_readiness_items").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_real_provider_connection_readiness_blockers").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_real_provider_connection_readiness_checkpoint").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_real_provider_connection_readiness_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_real_provider_connection_readiness_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_connection_readiness_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_real_provider_connection_readiness_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_connection_readiness_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_real_provider_connection_readiness_checkpoint WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_real_provider_connection_readiness_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_real_provider_connection_readiness_events ORDER BY created_at, event_id").fetchall()
    return [{"event_id": row["event_id"], "event_type": row["event_type"], "event_payload": _json_loads(row["event_payload_json"]), "created_at": row["created_at"]} for row in rows]

def get_real_provider_connection_readiness_items(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_real_provider_connection_readiness_items", "item_group, item_code", db_path, {"payload_json": "payload"})

def get_real_provider_connection_readiness_items_by_group(group: str, db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_real_provider_connection_readiness_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM vault_real_provider_connection_readiness_items WHERE item_group = ? ORDER BY item_code",
            (group,),
        ).fetchall()
    return [_boolify(row, {"payload_json": "payload"}) for row in rows]

def get_real_provider_connection_readiness_blockers(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_real_provider_connection_readiness_blockers", "blocker_code", db_path, {"payload_json": "payload"})

def validate_real_provider_connection_readiness_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_real_provider_connection_readiness_components", "gp_number", db_path, {"data_json": "data"})
    items = get_real_provider_connection_readiness_items(db_path)
    config = get_real_provider_connection_readiness_items_by_group("configuration", db_path)
    credentials = get_real_provider_connection_readiness_items_by_group("credential_boundary", db_path)
    endpoints = get_real_provider_connection_readiness_items_by_group("endpoint_namespace", db_path)
    encryption = get_real_provider_connection_readiness_items_by_group("encryption", db_path)
    preflight = get_real_provider_connection_readiness_items_by_group("preflight", db_path)
    health = get_real_provider_connection_readiness_items_by_group("health_placeholder", db_path)
    locks = get_real_provider_connection_readiness_items_by_group("connection_lock_validation", db_path)
    blockers = get_real_provider_connection_readiness_blockers(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("CONFIGURATION_ITEM_COUNT_4", len(config) == len(CONFIG_ITEMS)),
        ("CREDENTIAL_ITEM_COUNT_4", len(credentials) == len(CREDENTIAL_ITEMS)),
        ("ENDPOINT_ITEM_COUNT_4", len(endpoints) == len(ENDPOINT_ITEMS)),
        ("ENCRYPTION_ITEM_COUNT_4", len(encryption) == len(ENCRYPTION_ITEMS)),
        ("PREFLIGHT_ITEM_COUNT_6", len(preflight) == len(PREFLIGHT_ITEMS)),
        ("HEALTH_PLACEHOLDER_COUNT_4", len(health) == len(HEALTH_PLACEHOLDERS)),
        ("CONNECTION_LOCK_COUNT_8", len(locks) == len(LOCK_VALIDATIONS)),
        ("READINESS_ITEM_COUNT_34", len(items) == 34),
        ("BLOCKER_COUNT_12", len(blockers) == len(BLOCKER_SPECS)),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("SAFE_TO_CONTINUE_TO_GP161", readiness["safe_to_continue_to_gp161"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("READINESS_ONLY", readiness["readiness_only"] is True),
        ("NO_PROVIDER_CONTACT", readiness["no_provider_contact"] is True),
        ("SECTION_GP151_GP160", readiness["section_range"] == "GP151-GP160"),
        ("NEXT_SECTION_GP161_GP170", readiness["readiness_payload"]["next_section_range"] == "GP161-GP170"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_READINESS_ONLY", all(item["readiness_only"] is True for item in components)),
        ("ALL_COMPONENTS_NO_PROVIDER_CONTACT", all(item["no_provider_contact"] is True for item in components)),
        ("ALL_ITEMS_READY", all(item["item_ready"] is True for item in items)),
        ("ALL_ITEMS_LOCKED", all(item["item_locked"] is True for item in items)),
        ("ALL_ITEMS_READINESS_ONLY", all(item["readiness_only"] is True for item in items)),
        ("ALL_ITEMS_NO_PROVIDER_CONTACT", all(item["no_provider_contact"] is True for item in items)),
        ("ALL_BLOCKERS_ACTIVE", all(item["blocker_active"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_REAL_CONNECTION", all(item["blocks_real_connection"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", all(item["blocks_provider_api"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_CREDENTIALS", all(item["blocks_credentials"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_SECRET_READ", all(item["blocks_secret_read"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_ENDPOINT_CALL", all(item["blocks_endpoint_call"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_TOKEN", all(item["blocks_provider_token"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_SESSION", all(item["blocks_provider_session"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_JOB", all(item["blocks_provider_job"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_STATUS_POLL", all(item["blocks_status_poll"] is True for item in blockers)),
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
        ("ITEM", items),
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
        "configuration_item_count": len(config),
        "credential_item_count": len(credentials),
        "endpoint_item_count": len(endpoints),
        "encryption_item_count": len(encryption),
        "preflight_item_count": len(preflight),
        "health_placeholder_count": len(health),
        "connection_lock_count": len(locks),
        "readiness_item_count": len(items),
        "blocker_count": len(blockers),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "safe_to_continue_to_gp161": len(failed) == 0 and readiness["safe_to_continue_to_gp161"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp151_real_provider_connection_readiness_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(CONNECTION_READINESS_SHELL_ID, db_path)
    return {"pack": _pack_payload(151, component["pack_name"]), "real_sqlite_backed": True, "connection_readiness_shell": component}

def get_gp152_provider_configuration_status_dashboard(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(CONFIG_STATUS_DASHBOARD_ID, db_path)
    items = get_real_provider_connection_readiness_items_by_group("configuration", db_path)
    return {"pack": _pack_payload(152, component["pack_name"]), "real_sqlite_backed": True, "configuration_status_dashboard": component, "configuration_item_count": len(items), "items": items}

def get_gp153_credential_boundary_review_panel(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(CREDENTIAL_BOUNDARY_PANEL_ID, db_path)
    items = get_real_provider_connection_readiness_items_by_group("credential_boundary", db_path)
    return {"pack": _pack_payload(153, component["pack_name"]), "real_sqlite_backed": True, "credential_boundary_review_panel": component, "credential_item_count": len(items), "items": items}

def get_gp154_endpoint_namespace_review_panel(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(ENDPOINT_NAMESPACE_PANEL_ID, db_path)
    items = get_real_provider_connection_readiness_items_by_group("endpoint_namespace", db_path)
    return {"pack": _pack_payload(154, component["pack_name"]), "real_sqlite_backed": True, "endpoint_namespace_review_panel": component, "endpoint_item_count": len(items), "items": items}

def get_gp155_encryption_readiness_review_panel(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(ENCRYPTION_READINESS_PANEL_ID, db_path)
    items = get_real_provider_connection_readiness_items_by_group("encryption", db_path)
    return {"pack": _pack_payload(155, component["pack_name"]), "real_sqlite_backed": True, "encryption_readiness_review_panel": component, "encryption_item_count": len(items), "items": items}

def get_gp156_provider_connection_preflight_checklist(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(CONNECTION_PREFLIGHT_ID, db_path)
    items = get_real_provider_connection_readiness_items_by_group("preflight", db_path)
    return {"pack": _pack_payload(156, component["pack_name"]), "real_sqlite_backed": True, "provider_connection_preflight_checklist": component, "preflight_item_count": len(items), "items": items}

def get_gp157_provider_health_placeholder_panel(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(PROVIDER_HEALTH_PLACEHOLDER_ID, db_path)
    items = get_real_provider_connection_readiness_items_by_group("health_placeholder", db_path)
    return {"pack": _pack_payload(157, component["pack_name"]), "real_sqlite_backed": True, "provider_health_placeholder_panel": component, "health_placeholder_count": len(items), "items": items}

def get_gp158_connection_test_lock_validation(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(CONNECTION_LOCK_VALIDATION_ID, db_path)
    items = get_real_provider_connection_readiness_items_by_group("connection_lock_validation", db_path)
    return {"pack": _pack_payload(158, component["pack_name"]), "real_sqlite_backed": True, "connection_test_lock_validation": component, "connection_lock_count": len(items), "items": items}

def get_gp159_real_provider_connection_readiness_blocker_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_BLOCKER_BOARD_ID, db_path)
    blockers = get_real_provider_connection_readiness_blockers(db_path)
    return {"pack": _pack_payload(159, component["pack_name"]), "real_sqlite_backed": True, "readiness_blocker_board": component, "blocker_count": len(blockers), "blockers": blockers}

def get_gp160_real_provider_connection_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_real_provider_connection_readiness_layer(db_path)
    return {"pack": _pack_payload(160, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_real_provider_connection_readiness_layer(db_path)
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
            "source_gp150_readiness_id": component["source_gp150_readiness_id"],
            "source_gp150_readiness_hash": component["source_gp150_readiness_hash"],
            "source_gp150_readiness_score": component["source_gp150_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "readiness_only": component["readiness_only"],
            "no_provider_contact": component["no_provider_contact"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp161": validation["safe_to_continue_to_gp161"],
            "foundation_status": "real_provider_connection_readiness_layer_ready_locked_safe_to_continue_not_done",
            "next": next_label,
            **counts,
            "real_provider_connection_requested": component["real_provider_connection_requested"],
            "real_provider_connection_started": component["real_provider_connection_started"],
            "real_provider_connection_completed": component["real_provider_connection_completed"],
            "provider_api_called": component["provider_api_called"],
            "provider_token_created": component["provider_token_created"],
            "provider_session_created": component["provider_session_created"],
            "provider_job_reference_created": component["provider_job_reference_created"],
            "provider_status_poll_started": component["provider_status_poll_started"],
            "provider_health_checked": component["provider_health_checked"],
            "provider_credentials_validated": component["provider_credentials_validated"],
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
            "clouds_status": "parked_do_not_continue_from_vault_gp160",
        },
        "validation": validation,
    }

def get_gp151_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(151, CONNECTION_READINESS_SHELL_ID, "VAULT_GP152_PROVIDER_CONFIGURATION_STATUS_DASHBOARD", db_path)

def get_gp152_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(152, CONFIG_STATUS_DASHBOARD_ID, "VAULT_GP153_CREDENTIAL_BOUNDARY_REVIEW_PANEL", db_path)

def get_gp153_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(153, CREDENTIAL_BOUNDARY_PANEL_ID, "VAULT_GP154_ENDPOINT_NAMESPACE_REVIEW_PANEL", db_path)

def get_gp154_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(154, ENDPOINT_NAMESPACE_PANEL_ID, "VAULT_GP155_ENCRYPTION_READINESS_REVIEW_PANEL", db_path)

def get_gp155_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(155, ENCRYPTION_READINESS_PANEL_ID, "VAULT_GP156_PROVIDER_CONNECTION_PREFLIGHT_CHECKLIST", db_path)

def get_gp156_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(156, CONNECTION_PREFLIGHT_ID, "VAULT_GP157_PROVIDER_HEALTH_PLACEHOLDER_PANEL", db_path)

def get_gp157_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(157, PROVIDER_HEALTH_PLACEHOLDER_ID, "VAULT_GP158_CONNECTION_TEST_LOCK_VALIDATION", db_path)

def get_gp158_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(158, CONNECTION_LOCK_VALIDATION_ID, "VAULT_GP159_REAL_PROVIDER_CONNECTION_READINESS_BLOCKER_BOARD", db_path)

def get_gp159_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(159, READINESS_BLOCKER_BOARD_ID, "VAULT_GP160_REAL_PROVIDER_CONNECTION_READINESS_CHECKPOINT", db_path)

def get_gp160_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(160, READINESS_ID, NEXT_PACK, db_path)
    status["gp160_status"]["next_section"] = NEXT_SECTION_ID
    status["gp160_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp160_status"]["next_pack"] = NEXT_PACK
    return status

def get_real_provider_connection_readiness_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_real_provider_connection_readiness_layer(db_path)
    components = _rows("vault_real_provider_connection_readiness_components", "gp_number", db_path, {"data_json": "data"})
    items = get_real_provider_connection_readiness_items(db_path)
    blockers = get_real_provider_connection_readiness_blockers(db_path)
    readiness = _readiness(db_path)
    validation = validate_real_provider_connection_readiness_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "configuration": {"configuration_item_count": store["configuration_item_count"], "items": get_real_provider_connection_readiness_items_by_group("configuration", db_path)},
        "credential_boundary": {"credential_item_count": store["credential_item_count"], "items": get_real_provider_connection_readiness_items_by_group("credential_boundary", db_path)},
        "endpoint_namespace": {"endpoint_item_count": store["endpoint_item_count"], "items": get_real_provider_connection_readiness_items_by_group("endpoint_namespace", db_path)},
        "encryption": {"encryption_item_count": store["encryption_item_count"], "items": get_real_provider_connection_readiness_items_by_group("encryption", db_path)},
        "preflight": {"preflight_item_count": store["preflight_item_count"], "items": get_real_provider_connection_readiness_items_by_group("preflight", db_path)},
        "health_placeholder": {"health_placeholder_count": store["health_placeholder_count"], "items": get_real_provider_connection_readiness_items_by_group("health_placeholder", db_path)},
        "connection_locks": {"connection_lock_count": store["connection_lock_count"], "items": get_real_provider_connection_readiness_items_by_group("connection_lock_validation", db_path)},
        "all_items": {"readiness_item_count": len(items), "items": items},
        "blockers": {"blocker_count": len(blockers), "blockers": blockers},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "real_provider_connection_readiness_layer_ready": True,
            "connection_readiness_shell_ready": True,
            "provider_configuration_status_dashboard_ready": True,
            "credential_boundary_review_panel_ready": True,
            "endpoint_namespace_review_panel_ready": True,
            "encryption_readiness_review_panel_ready": True,
            "provider_connection_preflight_checklist_ready": True,
            "provider_health_placeholder_panel_ready": True,
            "connection_test_lock_validation_ready": True,
            "real_provider_connection_readiness_blocker_board_ready": True,
            "safe_to_continue_to_gp161": validation["safe_to_continue_to_gp161"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "readiness_only": True,
            "no_provider_contact": True,
            "real_provider_connection_requested": False,
            "real_provider_connection_started": False,
            "real_provider_connection_completed": False,
            "provider_api_called": False,
            "provider_token_created": False,
            "provider_session_created": False,
            "provider_job_reference_created": False,
            "provider_status_poll_started": False,
            "provider_health_checked": False,
            "provider_credentials_validated": False,
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
            "page": "/vault/real-provider-connection-readiness-layer",
            "json": "/vault/real-provider-connection-readiness-layer.json",
            "gp151": "/vault/gp151-status.json",
            "gp152": "/vault/gp152-status.json",
            "gp153": "/vault/gp153-status.json",
            "gp154": "/vault/gp154-status.json",
            "gp155": "/vault/gp155-status.json",
            "gp156": "/vault/gp156-status.json",
            "gp157": "/vault/gp157-status.json",
            "gp158": "/vault/gp158-status.json",
            "gp159": "/vault/gp159-status.json",
            "gp160": "/vault/gp160-status.json",
        },
    }

def render_real_provider_connection_readiness_layer_page() -> str:
    home = get_real_provider_connection_readiness_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    item_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['item_name'])}</strong>
          <span>{escape(item['item_status'])}</span>
          <code>{escape(item['item_group'])} · readiness only</code>
        </article>
        """
        for item in home["all_items"]["items"][:12]
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
<title>Vault GP151-GP160 Real Provider Connection Readiness Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 151-160</div>
    <div class="eyebrow">Real Provider Connection Readiness Layer · GP151-GP160</div>
    <h1>Real Provider Connection Readiness</h1>
    <p>This layer organizes the real-provider readiness surfaces without making provider contact. It prepares configuration status, credential boundaries, endpoint namespace review, encryption review, preflight, health placeholders, lock validation, blockers, and readiness proof.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['readiness_item_count']}</strong><span>readiness items</span></div>
      <div class="metric"><strong>{home['store']['connection_lock_count']}</strong><span>connection locks</span></div>
      <div class="metric"><strong>{home['store']['blocker_count']}</strong><span>active blockers</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP151-GP160 built</span>
      <span class="pill ok">Readiness only</span>
      <span class="pill ok">Safe to GP161</span>
      <span class="pill danger">No provider contact</span>
      <span class="pill danger">No provider API</span>
      <span class="pill danger">No secret read</span>
      <span class="pill danger">No token/session/job</span>
      <span class="pill danger">No object body</span>
      <span class="pill danger">No export/restore</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Readiness Items</h2>
    <div class="cards">{item_cards}</div>
  </section>

  <section class="section">
    <h2>Connection Readiness Blockers</h2>
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
