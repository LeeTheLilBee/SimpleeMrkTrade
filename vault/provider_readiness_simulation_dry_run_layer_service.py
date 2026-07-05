"""
VAULT GP141-GP150 — Provider Readiness Simulation and Dry-Run Layer

New section:
Archive Vault — Provider Readiness Simulation and Dry-Run Layer / GP141-GP150

Builds:
- GP141 Provider Readiness Simulation Shell
- GP142 Provider Dry-Run Scenario Registry
- GP143 Provider Connection Dry-Run Plan
- GP144 Provider Metadata Dry-Run Plan
- GP145 Provider Restore Dry-Run Plan
- GP146 Provider Export Dry-Run Plan
- GP147 Dry-Run Receipt Draft Ledger
- GP148 Dry-Run Result Review Queue
- GP149 Provider Readiness Simulation Blocker Board
- GP150 Provider Readiness Simulation Checkpoint

This layer models provider readiness using simulation/dry-run records only.
It never opens a real provider connection, calls provider APIs, creates tokens,
reads object bodies, downloads files, restores, exports, uploads, executes,
or marks Vault done.
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

from vault.tower_gated_permission_step_up_layer_service import (
    get_gp140_status,
    get_gp140_tower_gated_permission_readiness_checkpoint,
    get_tower_gated_permission_step_up_layer_home,
    validate_tower_gated_permission_step_up_layer,
    get_permission_request_drafts,
    get_step_up_challenge_locks,
    get_tower_gate_review_queue,
    get_tower_permission_blockers,
)

LAYER_ID = "VAULT_GP141_150"
LAYER_NAME = "Provider Readiness Simulation and Dry-Run Layer"
SCHEMA_VERSION = "vault.provider_readiness_simulation_dry_run_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_PROVIDER_READINESS_SIMULATION_AND_DRY_RUN_LAYER"
SECTION_TITLE = "Archive Vault — Provider Readiness Simulation and Dry-Run Layer"
SECTION_RANGE = "GP141-GP150"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_TOWER_GATED_PERMISSION_AND_STEP_UP_LAYER"
PREVIOUS_SECTION_RANGE = "GP131-GP140"

NEXT_SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_CONNECTION_READINESS_LAYER"
NEXT_SECTION_RANGE = "GP151-GP160"
NEXT_PACK = "VAULT_GP151_160_REAL_PROVIDER_CONNECTION_READINESS_LAYER"

DEFAULT_DB_ENV = "VAULT_PROVIDER_READINESS_SIMULATION_DRY_RUN_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_provider_readiness_simulation_dry_run_layer.sqlite"

SIMULATION_SHELL_ID = "VPRS-SHELL-GP141-001"
SCENARIO_REGISTRY_ID = "VPRS-SCENARIO-GP142-001"
CONNECTION_PLAN_ID = "VPRS-CONNECTION-GP143-001"
METADATA_PLAN_ID = "VPRS-METADATA-GP144-001"
RESTORE_PLAN_ID = "VPRS-RESTORE-GP145-001"
EXPORT_PLAN_ID = "VPRS-EXPORT-GP146-001"
RECEIPT_DRAFT_LEDGER_ID = "VPRS-RECEIPT-GP147-001"
RESULT_REVIEW_QUEUE_ID = "VPRS-REVIEW-GP148-001"
SIMULATION_BLOCKER_BOARD_ID = "VPRS-BLOCKER-GP149-001"
READINESS_ID = "VPRS-READINESS-GP150-001"

FALSE_FIELDS = [
    "simulation_promoted_to_real",
    "dry_run_submitted_to_provider",
    "dry_run_completed_by_provider",
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

SCENARIOS = [
    ("connection_preflight_dry_run", "Connection Preflight Dry-Run", "connection", "critical"),
    ("metadata_shape_dry_run", "Metadata Shape Dry-Run", "metadata", "high"),
    ("restore_path_dry_run", "Restore Path Dry-Run", "restore", "critical"),
    ("export_path_dry_run", "Export Path Dry-Run", "export", "critical"),
    ("receipt_lineage_dry_run", "Receipt Lineage Dry-Run", "receipt", "medium"),
    ("tower_handoff_dry_run", "Tower Handoff Dry-Run", "tower", "critical"),
    ("object_reference_dry_run", "Object Reference Dry-Run", "object_reference", "high"),
    ("failure_mode_dry_run", "Failure Mode Dry-Run", "failure_mode", "critical"),
]

PLAN_GROUPS = [
    ("connection", CONNECTION_PLAN_ID, "Provider Connection Dry-Run Plan", "connection"),
    ("metadata", METADATA_PLAN_ID, "Provider Metadata Dry-Run Plan", "metadata"),
    ("restore", RESTORE_PLAN_ID, "Provider Restore Dry-Run Plan", "restore"),
    ("export", EXPORT_PLAN_ID, "Provider Export Dry-Run Plan", "export"),
]

COMPONENT_SPECS = [
    (141, SIMULATION_SHELL_ID, "VAULT_GP141", "Provider Readiness Simulation Shell", "provider_readiness_simulation_shell"),
    (142, SCENARIO_REGISTRY_ID, "VAULT_GP142", "Provider Dry-Run Scenario Registry", "provider_dry_run_scenario_registry"),
    (143, CONNECTION_PLAN_ID, "VAULT_GP143", "Provider Connection Dry-Run Plan", "provider_connection_dry_run_plan"),
    (144, METADATA_PLAN_ID, "VAULT_GP144", "Provider Metadata Dry-Run Plan", "provider_metadata_dry_run_plan"),
    (145, RESTORE_PLAN_ID, "VAULT_GP145", "Provider Restore Dry-Run Plan", "provider_restore_dry_run_plan"),
    (146, EXPORT_PLAN_ID, "VAULT_GP146", "Provider Export Dry-Run Plan", "provider_export_dry_run_plan"),
    (147, RECEIPT_DRAFT_LEDGER_ID, "VAULT_GP147", "Dry-Run Receipt Draft Ledger", "dry_run_receipt_draft_ledger"),
    (148, RESULT_REVIEW_QUEUE_ID, "VAULT_GP148", "Dry-Run Result Review Queue", "dry_run_result_review_queue"),
    (149, SIMULATION_BLOCKER_BOARD_ID, "VAULT_GP149", "Provider Readiness Simulation Blocker Board", "provider_readiness_simulation_blocker_board"),
    (150, READINESS_ID, "VAULT_GP150", "Provider Readiness Simulation Checkpoint", "provider_readiness_simulation_checkpoint"),
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
        "source_gp140_readiness_score",
        "scenario_count",
        "plan_count",
        "receipt_draft_count",
        "review_item_count",
        "blocker_count",
        "component_count",
        "event_count",
        "readiness_score",
        "check_count",
        "passed_count",
        "failed_count",
        "step_count",
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
        "depends_on": ["VAULT_GP140"],
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
        "depends_on": ["VAULT_GP140"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_provider_readiness_simulation_dry_run_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_provider_simulation_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp140_readiness_id TEXT NOT NULL,
                source_gp140_readiness_hash TEXT NOT NULL,
                source_gp140_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                simulation_only INTEGER NOT NULL DEFAULT 1,
                dry_run_only INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_provider_dry_run_scenarios (
                scenario_id TEXT PRIMARY KEY,
                scenario_code TEXT NOT NULL UNIQUE,
                scenario_name TEXT NOT NULL,
                scenario_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                scenario_status TEXT NOT NULL,
                source_gp140_readiness_hash TEXT NOT NULL,
                scenario_ready INTEGER NOT NULL DEFAULT 1,
                scenario_locked INTEGER NOT NULL DEFAULT 1,
                simulation_only INTEGER NOT NULL DEFAULT 1,
                dry_run_only INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                scenario_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_provider_dry_run_plans (
                plan_id TEXT PRIMARY KEY,
                plan_code TEXT NOT NULL UNIQUE,
                plan_name TEXT NOT NULL,
                plan_category TEXT NOT NULL,
                step_count INTEGER NOT NULL,
                plan_status TEXT NOT NULL,
                plan_ready INTEGER NOT NULL DEFAULT 1,
                plan_locked INTEGER NOT NULL DEFAULT 1,
                simulation_only INTEGER NOT NULL DEFAULT 1,
                dry_run_only INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                plan_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_provider_dry_run_receipt_drafts (
                receipt_draft_id TEXT PRIMARY KEY,
                receipt_code TEXT NOT NULL UNIQUE,
                source_scenario_id TEXT NOT NULL,
                receipt_name TEXT NOT NULL,
                receipt_status TEXT NOT NULL,
                receipt_draft_locked INTEGER NOT NULL DEFAULT 1,
                final_receipt_created INTEGER NOT NULL DEFAULT 0,
                simulation_only INTEGER NOT NULL DEFAULT 1,
                dry_run_only INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_provider_dry_run_review_queue (
                review_item_id TEXT PRIMARY KEY,
                review_code TEXT NOT NULL UNIQUE,
                source_scenario_id TEXT NOT NULL,
                review_name TEXT NOT NULL,
                review_status TEXT NOT NULL,
                review_locked INTEGER NOT NULL DEFAULT 1,
                owner_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                review_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_provider_simulation_blockers (
                blocker_id TEXT PRIMARY KEY,
                blocker_code TEXT NOT NULL UNIQUE,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocker_active INTEGER NOT NULL DEFAULT 1,
                blocks_real_provider_connection INTEGER NOT NULL DEFAULT 1,
                blocks_provider_api INTEGER NOT NULL DEFAULT 1,
                blocks_provider_token INTEGER NOT NULL DEFAULT 1,
                blocks_provider_session INTEGER NOT NULL DEFAULT 1,
                blocks_provider_job INTEGER NOT NULL DEFAULT 1,
                blocks_provider_status_poll INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_provider_simulation_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                scenario_count INTEGER NOT NULL,
                plan_count INTEGER NOT NULL,
                receipt_draft_count INTEGER NOT NULL,
                review_item_count INTEGER NOT NULL,
                blocker_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                safe_to_continue_to_gp151 INTEGER NOT NULL DEFAULT 1,
                section_ready INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_provider_simulation_events (
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
            "vault_provider_simulation_components",
            "vault_provider_dry_run_scenarios",
            "vault_provider_dry_run_plans",
            "vault_provider_dry_run_receipt_drafts",
            "vault_provider_dry_run_review_queue",
            "vault_provider_simulation_blockers",
            "vault_provider_simulation_readiness",
            "vault_provider_simulation_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VPRSEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_provider_simulation_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_provider_readiness_simulation_dry_run_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_provider_readiness_simulation_dry_run_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_provider_simulation_components WHERE component_id = ?",
            (SIMULATION_SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp140_status = get_gp140_status()["gp140_status"]
            gp140_checkpoint = get_gp140_tower_gated_permission_readiness_checkpoint()["readiness_checkpoint"]
            gp140_home = get_tower_gated_permission_step_up_layer_home()
            gp140_validation = validate_tower_gated_permission_step_up_layer()

            source_drafts = get_permission_request_drafts()
            source_challenges = get_step_up_challenge_locks()
            source_queue = get_tower_gate_review_queue()
            source_blockers = get_tower_permission_blockers()

            readiness = gp140_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp140_readiness_id": readiness["readiness_id"],
                "source_gp140_readiness_hash": readiness["readiness_hash"],
                "source_gp140_readiness_score": readiness["readiness_score"],
            }

            source_context = {
                "source_gp140_status_ready": gp140_status["ready"],
                "source_gp140_validation_passed": gp140_status["validation_passed"],
                "source_gp140_safe_to_continue_to_gp141": gp140_status["safe_to_continue_to_gp141"],
                "source_gp140_readiness_hash": readiness["readiness_hash"],
                "source_gp140_readiness_score": readiness["readiness_score"],
                "source_permission_draft_count": len(source_drafts),
                "source_step_up_challenge_count": len(source_challenges),
                "source_tower_review_item_count": len(source_queue),
                "source_permission_blocker_count": len(source_blockers),
                "source_validation_check_count": gp140_validation["check_count"],
            }

            component_extra = {
                SIMULATION_SHELL_ID: {"provider_readiness_simulation_shell_ready": True},
                SCENARIO_REGISTRY_ID: {"provider_dry_run_scenario_registry_ready": True, "scenario_count": len(SCENARIOS)},
                CONNECTION_PLAN_ID: {"provider_connection_dry_run_plan_ready": True, "plan_category": "connection"},
                METADATA_PLAN_ID: {"provider_metadata_dry_run_plan_ready": True, "plan_category": "metadata"},
                RESTORE_PLAN_ID: {"provider_restore_dry_run_plan_ready": True, "plan_category": "restore"},
                EXPORT_PLAN_ID: {"provider_export_dry_run_plan_ready": True, "plan_category": "export"},
                RECEIPT_DRAFT_LEDGER_ID: {"dry_run_receipt_draft_ledger_ready": True, "receipt_draft_count": len(SCENARIOS)},
                RESULT_REVIEW_QUEUE_ID: {"dry_run_result_review_queue_ready": True, "review_item_count": len(SCENARIOS)},
                SIMULATION_BLOCKER_BOARD_ID: {"provider_readiness_simulation_blocker_board_ready": True, "blocker_count": 12},
                READINESS_ID: {"provider_readiness_simulation_checkpoint_ready": True, "safe_to_continue_to_gp151": True},
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
                    "simulation_only": True,
                    "dry_run_only": True,
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
                    "simulation_only": 1,
                    "dry_run_only": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_provider_simulation_components", row)

            scenario_ids = []
            for idx, (code, name, category, severity) in enumerate(SCENARIOS, start=1):
                scenario_id = f"VPRSS-{idx:03d}"
                scenario_ids.append((scenario_id, code))
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "scenario_id": scenario_id,
                    "scenario_code": code,
                    "scenario_name": name,
                    "scenario_category": category,
                    "severity": severity,
                    "scenario_status": "SIMULATION_READY_DRY_RUN_ONLY_NO_PROVIDER_CONTACT",
                    "source_gp140_readiness_hash": readiness["readiness_hash"],
                    "scenario_ready": True,
                    "scenario_locked": True,
                    "simulation_only": True,
                    "dry_run_only": True,
                    "allowed_actions": ["view_plan", "review_assumptions", "inspect_blockers", "prepare_questions"],
                    "blocked_actions": ["connect_provider", "call_provider_api", "create_token", "create_session", "list_objects", "read_body", "download", "restore", "export", "upload", "execute"],
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "scenario_id": scenario_id,
                    "scenario_code": code,
                    "scenario_name": name,
                    "scenario_category": category,
                    "severity": severity,
                    "scenario_status": payload["scenario_status"],
                    "source_gp140_readiness_hash": readiness["readiness_hash"],
                    "scenario_ready": 1,
                    "scenario_locked": 1,
                    "simulation_only": 1,
                    "dry_run_only": 1,
                    "payload_json": _json_dumps(payload),
                    "scenario_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_provider_dry_run_scenarios", row)

                receipt_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "receipt_code": f"{code}_dry_run_receipt_draft",
                    "source_scenario_id": scenario_id,
                    "receipt_name": f"{name} Receipt Draft",
                    "receipt_status": "DRAFT_ONLY_NOT_FINALIZED_NO_PROVIDER_RECEIPT",
                    "receipt_draft_locked": True,
                    "final_receipt_created": False,
                    "simulation_only": True,
                    "dry_run_only": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "receipt_draft_id": f"VPRSRD-{idx:03d}",
                    "receipt_code": receipt_payload["receipt_code"],
                    "source_scenario_id": scenario_id,
                    "receipt_name": receipt_payload["receipt_name"],
                    "receipt_status": receipt_payload["receipt_status"],
                    "receipt_draft_locked": 1,
                    "final_receipt_created": 0,
                    "simulation_only": 1,
                    "dry_run_only": 1,
                    "payload_json": _json_dumps(receipt_payload),
                    "receipt_hash": _hash_payload(receipt_payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_provider_dry_run_receipt_drafts", row)

                review_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "review_code": f"{code}_dry_run_review",
                    "source_scenario_id": scenario_id,
                    "review_name": f"{name} Review",
                    "review_status": "OWNER_AND_TOWER_REVIEW_REQUIRED_LOCKED_NO_RESULT_APPROVAL",
                    "review_locked": True,
                    "owner_review_required": True,
                    "tower_review_required": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "review_item_id": f"VPRSRQ-{idx:03d}",
                    "review_code": review_payload["review_code"],
                    "source_scenario_id": scenario_id,
                    "review_name": review_payload["review_name"],
                    "review_status": review_payload["review_status"],
                    "review_locked": 1,
                    "owner_review_required": 1,
                    "tower_review_required": 1,
                    "payload_json": _json_dumps(review_payload),
                    "review_hash": _hash_payload(review_payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_provider_dry_run_review_queue", row)

            for idx, (code, component_id, name, category) in enumerate(PLAN_GROUPS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "plan_code": f"{code}_dry_run_plan",
                    "plan_name": name,
                    "plan_category": category,
                    "step_count": 5,
                    "plan_status": "PLAN_READY_SIMULATION_ONLY_NO_PROVIDER_CONTACT",
                    "plan_ready": True,
                    "plan_locked": True,
                    "simulation_only": True,
                    "dry_run_only": True,
                    "steps": [
                        "Confirm Tower gate remains locked",
                        "Confirm provider API remains unavailable",
                        "Confirm no token/session/job/reference is created",
                        "Confirm no object body/download/export/restore/upload occurs",
                        "Record dry-run assumptions only",
                    ],
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "plan_id": component_id,
                    "plan_code": payload["plan_code"],
                    "plan_name": name,
                    "plan_category": category,
                    "step_count": 5,
                    "plan_status": payload["plan_status"],
                    "plan_ready": 1,
                    "plan_locked": 1,
                    "simulation_only": 1,
                    "dry_run_only": 1,
                    "payload_json": _json_dumps(payload),
                    "plan_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_provider_dry_run_plans", row)

            blocker_specs = [
                ("real_provider_connection_locked", "Real provider connection locked", "connection", "critical"),
                ("provider_api_locked", "Provider API locked", "provider_api", "critical"),
                ("provider_token_locked", "Provider token/session locked", "token_session", "critical"),
                ("provider_job_reference_locked", "Provider job/reference locked", "provider_job", "critical"),
                ("status_poll_locked", "Provider status poll locked", "status_poll", "critical"),
                ("object_catalog_locked", "Provider object catalog locked", "catalog", "critical"),
                ("metadata_import_locked", "Provider metadata import locked", "metadata", "high"),
                ("object_body_locked", "Object body access locked", "object_body", "critical"),
                ("download_locked", "File download locked", "download", "critical"),
                ("restore_export_locked", "Restore/export locked", "restore_export", "critical"),
                ("direct_upload_locked", "Direct upload locked", "upload", "critical"),
                ("execution_done_locked", "Execution and Vault done locked", "execution", "critical"),
            ]
            for idx, (code, name, category, severity) in enumerate(blocker_specs, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "ACTIVE_PROVIDER_SIMULATION_BLOCKER",
                    "blocker_active": True,
                    "blocks_real_provider_connection": True,
                    "blocks_provider_api": True,
                    "blocks_provider_token": True,
                    "blocks_provider_session": True,
                    "blocks_provider_job": True,
                    "blocks_provider_status_poll": True,
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
                    "blocker_id": f"VPRSB-{idx:03d}",
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": payload["blocker_status"],
                    "blocker_active": 1,
                    "blocks_real_provider_connection": 1,
                    "blocks_provider_api": 1,
                    "blocks_provider_token": 1,
                    "blocks_provider_session": 1,
                    "blocks_provider_job": 1,
                    "blocks_provider_status_poll": 1,
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
                _insert_dict(conn, "vault_provider_simulation_blockers", row)

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "scenario_count": len(SCENARIOS),
                "plan_count": len(PLAN_GROUPS),
                "receipt_draft_count": len(SCENARIOS),
                "review_item_count": len(SCENARIOS),
                "blocker_count": len(blocker_specs),
            }

            checks = [
                ("SOURCE_GP140_READY", bool(gp140_status["ready"])),
                ("SOURCE_GP140_VALIDATION_PASSED", bool(gp140_status["validation_passed"])),
                ("SOURCE_GP140_SAFE_TO_CONTINUE", bool(gp140_status["safe_to_continue_to_gp141"])),
                ("SOURCE_GP140_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP140_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("SCENARIO_COUNT_8", counts["scenario_count"] == 8),
                ("PLAN_COUNT_4", counts["plan_count"] == 4),
                ("RECEIPT_DRAFT_COUNT_8", counts["receipt_draft_count"] == 8),
                ("REVIEW_ITEM_COUNT_8", counts["review_item_count"] == 8),
                ("BLOCKER_COUNT_12", counts["blocker_count"] == 12),
                ("SECTION_GP141_GP150", SECTION_RANGE == "GP141-GP150"),
                ("NEXT_SECTION_GP151_GP160", NEXT_SECTION_RANGE == "GP151-GP160"),
                ("SIMULATION_ONLY", True),
                ("DRY_RUN_ONLY", True),
                ("NO_REAL_PROVIDER_CONNECTION", True),
                ("NO_PROVIDER_API", True),
                ("NO_PROVIDER_TOKEN_SESSION_JOB", True),
                ("NO_PROVIDER_STATUS_POLL", True),
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
                "gp_number": 150,
                "pack_id": "VAULT_GP150",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp140_readiness_id": readiness["readiness_id"],
                "source_gp140_readiness_hash": readiness["readiness_hash"],
                "source_gp140_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "safe_to_continue_to_gp151": failed_count == 0,
                "section_ready": True,
                "simulation_only": True,
                "dry_run_only": True,
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
                "gp_number": 150,
                "pack_id": "VAULT_GP150",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "PROVIDER_READINESS_SIMULATION_DRY_RUN_LAYER_READY_LOCKED_SAFE_TO_CONTINUE_NOT_DONE",
                "readiness_score": readiness_payload["readiness_score"],
                **counts,
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "safe_to_continue_to_gp151": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_provider_simulation_readiness", row)

            for event_type, event_payload in [
                ("GP141_PROVIDER_READINESS_SIMULATION_SHELL_CREATED", {"component_id": SIMULATION_SHELL_ID}),
                ("GP142_PROVIDER_DRY_RUN_SCENARIO_REGISTRY_CREATED", {"scenario_count": counts["scenario_count"]}),
                ("GP143_PROVIDER_CONNECTION_DRY_RUN_PLAN_CREATED", {"plan_id": CONNECTION_PLAN_ID}),
                ("GP144_PROVIDER_METADATA_DRY_RUN_PLAN_CREATED", {"plan_id": METADATA_PLAN_ID}),
                ("GP145_PROVIDER_RESTORE_DRY_RUN_PLAN_CREATED", {"plan_id": RESTORE_PLAN_ID}),
                ("GP146_PROVIDER_EXPORT_DRY_RUN_PLAN_CREATED", {"plan_id": EXPORT_PLAN_ID}),
                ("GP147_DRY_RUN_RECEIPT_DRAFT_LEDGER_CREATED", {"receipt_draft_count": counts["receipt_draft_count"]}),
                ("GP148_DRY_RUN_RESULT_REVIEW_QUEUE_CREATED", {"review_item_count": counts["review_item_count"]}),
                ("GP149_PROVIDER_READINESS_SIMULATION_BLOCKER_BOARD_CREATED", {"blocker_count": counts["blocker_count"]}),
                ("GP150_PROVIDER_READINESS_SIMULATION_CHECKPOINT_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp151": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_provider_simulation_components").fetchone()["c"]),
            "scenario_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_provider_dry_run_scenarios").fetchone()["c"]),
            "plan_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_provider_dry_run_plans").fetchone()["c"]),
            "receipt_draft_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_provider_dry_run_receipt_drafts").fetchone()["c"]),
            "review_item_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_provider_dry_run_review_queue").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_provider_simulation_blockers").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_provider_simulation_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_provider_simulation_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_provider_readiness_simulation_dry_run_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_provider_readiness_simulation_dry_run_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute("SELECT * FROM vault_provider_simulation_components WHERE component_id = ?", (component_id,)).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_provider_readiness_simulation_dry_run_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute("SELECT * FROM vault_provider_simulation_readiness WHERE readiness_id = ?", (READINESS_ID,)).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_provider_readiness_simulation_dry_run_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_provider_simulation_events ORDER BY created_at, event_id").fetchall()
    return [{"event_id": row["event_id"], "event_type": row["event_type"], "event_payload": _json_loads(row["event_payload_json"]), "created_at": row["created_at"]} for row in rows]

def get_provider_dry_run_scenarios(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_provider_dry_run_scenarios", "scenario_code", db_path, {"payload_json": "payload"})

def get_provider_dry_run_plans(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_provider_dry_run_plans", "plan_code", db_path, {"payload_json": "payload"})

def get_provider_dry_run_receipt_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_provider_dry_run_receipt_drafts", "receipt_code", db_path, {"payload_json": "payload"})

def get_provider_dry_run_review_queue(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_provider_dry_run_review_queue", "review_code", db_path, {"payload_json": "payload"})

def get_provider_simulation_blockers(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_provider_simulation_blockers", "blocker_code", db_path, {"payload_json": "payload"})

def validate_provider_readiness_simulation_dry_run_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_provider_simulation_components", "gp_number", db_path, {"data_json": "data"})
    scenarios = get_provider_dry_run_scenarios(db_path)
    plans = get_provider_dry_run_plans(db_path)
    receipts = get_provider_dry_run_receipt_drafts(db_path)
    reviews = get_provider_dry_run_review_queue(db_path)
    blockers = get_provider_simulation_blockers(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("SCENARIO_COUNT_8", len(scenarios) == len(SCENARIOS)),
        ("PLAN_COUNT_4", len(plans) == len(PLAN_GROUPS)),
        ("RECEIPT_DRAFT_COUNT_8", len(receipts) == len(SCENARIOS)),
        ("REVIEW_ITEM_COUNT_8", len(reviews) == len(SCENARIOS)),
        ("BLOCKER_COUNT_12", len(blockers) == 12),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("SAFE_TO_CONTINUE_TO_GP151", readiness["safe_to_continue_to_gp151"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("SECTION_GP141_GP150", readiness["section_range"] == "GP141-GP150"),
        ("NEXT_SECTION_GP151_GP160", readiness["readiness_payload"]["next_section_range"] == "GP151-GP160"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_SIMULATION_ONLY", all(item["simulation_only"] is True for item in components)),
        ("ALL_COMPONENTS_DRY_RUN_ONLY", all(item["dry_run_only"] is True for item in components)),
        ("ALL_SCENARIOS_SIMULATION_ONLY", all(item["simulation_only"] is True for item in scenarios)),
        ("ALL_SCENARIOS_DRY_RUN_ONLY", all(item["dry_run_only"] is True for item in scenarios)),
        ("ALL_SCENARIOS_LOCKED", all(item["scenario_locked"] is True for item in scenarios)),
        ("ALL_PLANS_SIMULATION_ONLY", all(item["simulation_only"] is True for item in plans)),
        ("ALL_PLANS_DRY_RUN_ONLY", all(item["dry_run_only"] is True for item in plans)),
        ("ALL_PLANS_LOCKED", all(item["plan_locked"] is True for item in plans)),
        ("ALL_RECEIPTS_DRAFT_LOCKED", all(item["receipt_draft_locked"] is True for item in receipts)),
        ("NO_FINAL_RECEIPTS", all(item["final_receipt_created"] is False for item in receipts)),
        ("ALL_REVIEWS_LOCKED", all(item["review_locked"] is True for item in reviews)),
        ("ALL_BLOCKERS_ACTIVE", all(item["blocker_active"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_REAL_CONNECTION", all(item["blocks_real_provider_connection"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", all(item["blocks_provider_api"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_TOKEN", all(item["blocks_provider_token"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_SESSION", all(item["blocks_provider_session"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_JOB", all(item["blocks_provider_job"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_STATUS_POLL", all(item["blocks_provider_status_poll"] is True for item in blockers)),
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
        ("SCENARIO", scenarios),
        ("PLAN", plans),
        ("RECEIPT", receipts),
        ("REVIEW", reviews),
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
        "scenario_count": len(scenarios),
        "plan_count": len(plans),
        "receipt_draft_count": len(receipts),
        "review_item_count": len(reviews),
        "blocker_count": len(blockers),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "safe_to_continue_to_gp151": len(failed) == 0 and readiness["safe_to_continue_to_gp151"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp141_provider_readiness_simulation_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SIMULATION_SHELL_ID, db_path)
    return {"pack": _pack_payload(141, component["pack_name"]), "real_sqlite_backed": True, "simulation_shell": component}

def get_gp142_provider_dry_run_scenario_registry(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SCENARIO_REGISTRY_ID, db_path)
    scenarios = get_provider_dry_run_scenarios(db_path)
    return {"pack": _pack_payload(142, component["pack_name"]), "real_sqlite_backed": True, "scenario_registry": component, "scenario_count": len(scenarios), "scenarios": scenarios}

def get_gp143_provider_connection_dry_run_plan(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(CONNECTION_PLAN_ID, db_path)
    plans = [item for item in get_provider_dry_run_plans(db_path) if item["plan_category"] == "connection"]
    return {"pack": _pack_payload(143, component["pack_name"]), "real_sqlite_backed": True, "connection_dry_run_plan": component, "plans": plans}

def get_gp144_provider_metadata_dry_run_plan(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(METADATA_PLAN_ID, db_path)
    plans = [item for item in get_provider_dry_run_plans(db_path) if item["plan_category"] == "metadata"]
    return {"pack": _pack_payload(144, component["pack_name"]), "real_sqlite_backed": True, "metadata_dry_run_plan": component, "plans": plans}

def get_gp145_provider_restore_dry_run_plan(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RESTORE_PLAN_ID, db_path)
    plans = [item for item in get_provider_dry_run_plans(db_path) if item["plan_category"] == "restore"]
    return {"pack": _pack_payload(145, component["pack_name"]), "real_sqlite_backed": True, "restore_dry_run_plan": component, "plans": plans}

def get_gp146_provider_export_dry_run_plan(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(EXPORT_PLAN_ID, db_path)
    plans = [item for item in get_provider_dry_run_plans(db_path) if item["plan_category"] == "export"]
    return {"pack": _pack_payload(146, component["pack_name"]), "real_sqlite_backed": True, "export_dry_run_plan": component, "plans": plans}

def get_gp147_dry_run_receipt_draft_ledger(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RECEIPT_DRAFT_LEDGER_ID, db_path)
    receipts = get_provider_dry_run_receipt_drafts(db_path)
    return {"pack": _pack_payload(147, component["pack_name"]), "real_sqlite_backed": True, "receipt_draft_ledger": component, "receipt_draft_count": len(receipts), "receipt_drafts": receipts}

def get_gp148_dry_run_result_review_queue(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RESULT_REVIEW_QUEUE_ID, db_path)
    reviews = get_provider_dry_run_review_queue(db_path)
    return {"pack": _pack_payload(148, component["pack_name"]), "real_sqlite_backed": True, "result_review_queue": component, "review_item_count": len(reviews), "review_items": reviews}

def get_gp149_provider_readiness_simulation_blocker_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SIMULATION_BLOCKER_BOARD_ID, db_path)
    blockers = get_provider_simulation_blockers(db_path)
    return {"pack": _pack_payload(149, component["pack_name"]), "real_sqlite_backed": True, "simulation_blocker_board": component, "blocker_count": len(blockers), "blockers": blockers}

def get_gp150_provider_readiness_simulation_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_provider_readiness_simulation_dry_run_layer(db_path)
    return {"pack": _pack_payload(150, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_provider_readiness_simulation_dry_run_layer(db_path)
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
            "source_gp140_readiness_id": component["source_gp140_readiness_id"],
            "source_gp140_readiness_hash": component["source_gp140_readiness_hash"],
            "source_gp140_readiness_score": component["source_gp140_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "simulation_only": component["simulation_only"],
            "dry_run_only": component["dry_run_only"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp151": validation["safe_to_continue_to_gp151"],
            "foundation_status": "provider_readiness_simulation_dry_run_layer_ready_locked_safe_to_continue_not_done",
            "next": next_label,
            **counts,
            "simulation_promoted_to_real": component["simulation_promoted_to_real"],
            "dry_run_submitted_to_provider": component["dry_run_submitted_to_provider"],
            "dry_run_completed_by_provider": component["dry_run_completed_by_provider"],
            "real_provider_connection_requested": component["real_provider_connection_requested"],
            "real_provider_connection_started": component["real_provider_connection_started"],
            "real_provider_connection_completed": component["real_provider_connection_completed"],
            "provider_api_called": component["provider_api_called"],
            "provider_token_created": component["provider_token_created"],
            "provider_session_created": component["provider_session_created"],
            "provider_job_reference_created": component["provider_job_reference_created"],
            "provider_status_poll_started": component["provider_status_poll_started"],
            "provider_status_poll_completed": component["provider_status_poll_completed"],
            "provider_objects_listed": component["provider_objects_listed"],
            "provider_metadata_imported": component["provider_metadata_imported"],
            "provider_metadata_read": component["provider_metadata_read"],
            "object_body_read": component["object_body_read"],
            "object_body_view_enabled": component["object_body_view_enabled"],
            "object_body_download_enabled": component["object_body_download_enabled"],
            "object_body_plaintext_visible": component["object_body_plaintext_visible"],
            "object_download_enabled": component["object_download_enabled"],
            "restore_request_created": component["restore_request_created"],
            "restore_job_created": component["restore_job_created"],
            "provider_restore_api_called": component["provider_restore_api_called"],
            "export_package_created": component["export_package_created"],
            "export_manifest_created": component["export_manifest_created"],
            "export_download_enabled": component["export_download_enabled"],
            "export_enabled": component["export_enabled"],
            "direct_upload_enabled": component["direct_upload_enabled"],
            "tower_unlock_granted": component["tower_unlock_granted"],
            "execution_enabled": component["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp150",
        },
        "validation": validation,
    }

def get_gp141_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(141, SIMULATION_SHELL_ID, "VAULT_GP142_PROVIDER_DRY_RUN_SCENARIO_REGISTRY", db_path)

def get_gp142_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(142, SCENARIO_REGISTRY_ID, "VAULT_GP143_PROVIDER_CONNECTION_DRY_RUN_PLAN", db_path)

def get_gp143_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(143, CONNECTION_PLAN_ID, "VAULT_GP144_PROVIDER_METADATA_DRY_RUN_PLAN", db_path)

def get_gp144_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(144, METADATA_PLAN_ID, "VAULT_GP145_PROVIDER_RESTORE_DRY_RUN_PLAN", db_path)

def get_gp145_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(145, RESTORE_PLAN_ID, "VAULT_GP146_PROVIDER_EXPORT_DRY_RUN_PLAN", db_path)

def get_gp146_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(146, EXPORT_PLAN_ID, "VAULT_GP147_DRY_RUN_RECEIPT_DRAFT_LEDGER", db_path)

def get_gp147_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(147, RECEIPT_DRAFT_LEDGER_ID, "VAULT_GP148_DRY_RUN_RESULT_REVIEW_QUEUE", db_path)

def get_gp148_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(148, RESULT_REVIEW_QUEUE_ID, "VAULT_GP149_PROVIDER_READINESS_SIMULATION_BLOCKER_BOARD", db_path)

def get_gp149_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(149, SIMULATION_BLOCKER_BOARD_ID, "VAULT_GP150_PROVIDER_READINESS_SIMULATION_CHECKPOINT", db_path)

def get_gp150_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(150, READINESS_ID, NEXT_PACK, db_path)
    status["gp150_status"]["next_section"] = NEXT_SECTION_ID
    status["gp150_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp150_status"]["next_pack"] = NEXT_PACK
    return status

def get_provider_readiness_simulation_dry_run_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_provider_readiness_simulation_dry_run_layer(db_path)
    components = _rows("vault_provider_simulation_components", "gp_number", db_path, {"data_json": "data"})
    scenarios = get_provider_dry_run_scenarios(db_path)
    plans = get_provider_dry_run_plans(db_path)
    receipts = get_provider_dry_run_receipt_drafts(db_path)
    reviews = get_provider_dry_run_review_queue(db_path)
    blockers = get_provider_simulation_blockers(db_path)
    readiness = _readiness(db_path)
    validation = validate_provider_readiness_simulation_dry_run_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "scenarios": {"scenario_count": len(scenarios), "scenarios": scenarios},
        "plans": {"plan_count": len(plans), "plans": plans},
        "receipt_drafts": {"receipt_draft_count": len(receipts), "receipt_drafts": receipts},
        "review_queue": {"review_item_count": len(reviews), "review_items": reviews},
        "blockers": {"blocker_count": len(blockers), "blockers": blockers},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "provider_readiness_simulation_dry_run_layer_ready": True,
            "provider_readiness_simulation_shell_ready": True,
            "provider_dry_run_scenario_registry_ready": True,
            "provider_connection_dry_run_plan_ready": True,
            "provider_metadata_dry_run_plan_ready": True,
            "provider_restore_dry_run_plan_ready": True,
            "provider_export_dry_run_plan_ready": True,
            "dry_run_receipt_draft_ledger_ready": True,
            "dry_run_result_review_queue_ready": True,
            "provider_readiness_simulation_blocker_board_ready": True,
            "safe_to_continue_to_gp151": validation["safe_to_continue_to_gp151"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "simulation_only": True,
            "dry_run_only": True,
            "simulation_promoted_to_real": False,
            "dry_run_submitted_to_provider": False,
            "dry_run_completed_by_provider": False,
            "real_provider_connection_requested": False,
            "real_provider_connection_started": False,
            "real_provider_connection_completed": False,
            "provider_api_called": False,
            "provider_token_created": False,
            "provider_session_created": False,
            "provider_job_reference_created": False,
            "provider_status_poll_started": False,
            "provider_status_poll_completed": False,
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
            "page": "/vault/provider-readiness-simulation-dry-run-layer",
            "json": "/vault/provider-readiness-simulation-dry-run-layer.json",
            "gp141": "/vault/gp141-status.json",
            "gp142": "/vault/gp142-status.json",
            "gp143": "/vault/gp143-status.json",
            "gp144": "/vault/gp144-status.json",
            "gp145": "/vault/gp145-status.json",
            "gp146": "/vault/gp146-status.json",
            "gp147": "/vault/gp147-status.json",
            "gp148": "/vault/gp148-status.json",
            "gp149": "/vault/gp149-status.json",
            "gp150": "/vault/gp150-status.json",
        },
    }

def render_provider_readiness_simulation_dry_run_layer_page() -> str:
    home = get_provider_readiness_simulation_dry_run_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    scenario_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['scenario_name'])}</strong>
          <span>{escape(item['scenario_status'])}</span>
          <code>{escape(item['scenario_category'])} · dry-run only</code>
        </article>
        """
        for item in home["scenarios"]["scenarios"]
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
<title>Vault GP141-GP150 Provider Readiness Simulation Dry-Run Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 141-150</div>
    <div class="eyebrow">Provider Readiness Simulation and Dry-Run Layer · GP141-GP150</div>
    <h1>Provider Readiness Simulation Dry-Run</h1>
    <p>This layer models provider readiness through simulation and dry-run records only. It creates scenarios, plans, receipt drafts, review queue items, blockers, and a readiness checkpoint without contacting any provider.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['scenario_count']}</strong><span>dry-run scenarios</span></div>
      <div class="metric"><strong>{home['store']['plan_count']}</strong><span>dry-run plans</span></div>
      <div class="metric"><strong>{home['store']['blocker_count']}</strong><span>active blockers</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP141-GP150 built</span>
      <span class="pill ok">Simulation ready</span>
      <span class="pill ok">Dry-run only</span>
      <span class="pill ok">Safe to GP151</span>
      <span class="pill danger">No provider connection</span>
      <span class="pill danger">No provider API</span>
      <span class="pill danger">No token/session/job</span>
      <span class="pill danger">No object body</span>
      <span class="pill danger">No export/restore</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Dry-Run Scenarios</h2>
    <div class="cards">{scenario_cards}</div>
  </section>

  <section class="section">
    <h2>Simulation Blockers</h2>
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
