"""
VAULT GP131-GP140 — Tower-Gated Permission and Step-Up Layer

New section:
Archive Vault — Tower-Gated Permission and Step-Up Layer / GP131-GP140

Builds:
- GP131 Tower Permission Handoff Shell
- GP132 Permission Request Draft Registry
- GP133 Step-Up Challenge Lock Contract
- GP134 Tower Gate Review Queue
- GP135 Owner Authority Boundary View
- GP136 Permission Receipt Draft Ledger
- GP137 Denial and Block Reason Board
- GP138 Tower Handoff Evidence Map
- GP139 Tower-Gated Permission Blocker Board
- GP140 Tower-Gated Permission Readiness Checkpoint

This layer creates Tower permission/step-up handoff governance surfaces without
submitting permissions, passing step-up, granting Tower unlock, or enabling
restore/export/provider APIs/object body/download/direct upload/execution.
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

from vault.owner_console_operating_dashboard_layer_service import (
    get_gp130_status,
    get_gp130_owner_console_readiness_checkpoint,
    get_owner_console_operating_dashboard_layer_home,
    validate_owner_console_operating_dashboard_layer,
    get_owner_console_metrics,
    get_owner_console_panels,
    get_owner_console_safe_actions,
    get_owner_console_blockers,
)

LAYER_ID = "VAULT_GP131_140"
LAYER_NAME = "Tower-Gated Permission and Step-Up Layer"
SCHEMA_VERSION = "vault.tower_gated_permission_step_up_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_TOWER_GATED_PERMISSION_AND_STEP_UP_LAYER"
SECTION_TITLE = "Archive Vault — Tower-Gated Permission and Step-Up Layer"
SECTION_RANGE = "GP131-GP140"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_OWNER_CONSOLE_AND_OPERATING_DASHBOARD_LAYER"
PREVIOUS_SECTION_RANGE = "GP121-GP130"

NEXT_SECTION_ID = "ARCHIVE_VAULT_PROVIDER_READINESS_SIMULATION_AND_DRY_RUN_LAYER"
NEXT_SECTION_RANGE = "GP141-GP150"
NEXT_PACK = "VAULT_GP141_150_PROVIDER_READINESS_SIMULATION_AND_DRY_RUN_LAYER"

DEFAULT_DB_ENV = "VAULT_TOWER_GATED_PERMISSION_STEP_UP_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_tower_gated_permission_step_up_layer.sqlite"

HANDOFF_SHELL_ID = "VTGPS-HS-GP131-001"
PERMISSION_DRAFT_REGISTRY_ID = "VTGPS-PDR-GP132-001"
STEP_UP_LOCK_ID = "VTGPS-SULC-GP133-001"
TOWER_REVIEW_QUEUE_ID = "VTGPS-TGRQ-GP134-001"
OWNER_AUTHORITY_BOUNDARY_ID = "VTGPS-OABV-GP135-001"
PERMISSION_RECEIPT_LEDGER_ID = "VTGPS-PRDL-GP136-001"
DENIAL_BLOCK_REASON_ID = "VTGPS-DBRB-GP137-001"
TOWER_EVIDENCE_MAP_ID = "VTGPS-THEM-GP138-001"
PERMISSION_BLOCKER_BOARD_ID = "VTGPS-PBB-GP139-001"
READINESS_ID = "VTGPS-RC-GP140-001"

FALSE_FIELDS = [
    "permission_request_submitted",
    "permission_request_approved",
    "permission_request_granted",
    "permission_request_denied_final",
    "permission_receipt_finalized",
    "permission_receipt_persisted",
    "step_up_challenge_started",
    "step_up_challenge_passed",
    "step_up_challenge_failed_final",
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
    "provider_api_configured",
    "provider_api_called",
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
    "export_requested",
    "export_approved",
    "export_enabled",
    "export_package_created",
    "export_manifest_created",
    "export_download_enabled",
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
    "direct_upload_enabled",
    "execution_enabled",
    "vault_done",
    "clouds_should_continue",
]

PERMISSION_SURFACES = [
    ("restore_permission", "Future Restore Permission", "restore", "critical"),
    ("export_permission", "Future Export Permission", "export", "critical"),
    ("provider_metadata_permission", "Future Provider Metadata Permission", "provider_metadata", "high"),
    ("provider_connection_permission", "Future Provider Connection Permission", "provider_connection", "critical"),
    ("object_reference_permission", "Future Object Reference Permission", "object_reference", "high"),
    ("owner_review_permission", "Owner Review Permission", "owner_review", "medium"),
    ("proof_packet_permission", "Proof Packet Permission", "proof_packet", "medium"),
    ("tower_step_up_permission", "Tower Step-Up Permission", "tower", "critical"),
]

DENIAL_REASONS = [
    ("tower_gate_locked", "Tower gate remains locked", "tower"),
    ("step_up_not_passed", "Step-up challenge not passed", "step_up"),
    ("owner_decision_missing", "Owner decision not recorded", "owner"),
    ("provider_api_locked", "Provider API remains locked", "provider"),
    ("object_body_locked", "Object body remains locked", "object_body"),
    ("export_locked", "Export remains locked", "export"),
    ("restore_locked", "Restore remains locked", "restore"),
    ("vault_not_done", "Vault is not done", "done"),
]

COMPONENT_SPECS = [
    (131, HANDOFF_SHELL_ID, "VAULT_GP131", "Tower Permission Handoff Shell", "tower_permission_handoff_shell"),
    (132, PERMISSION_DRAFT_REGISTRY_ID, "VAULT_GP132", "Permission Request Draft Registry", "permission_request_draft_registry"),
    (133, STEP_UP_LOCK_ID, "VAULT_GP133", "Step-Up Challenge Lock Contract", "step_up_challenge_lock_contract"),
    (134, TOWER_REVIEW_QUEUE_ID, "VAULT_GP134", "Tower Gate Review Queue", "tower_gate_review_queue"),
    (135, OWNER_AUTHORITY_BOUNDARY_ID, "VAULT_GP135", "Owner Authority Boundary View", "owner_authority_boundary_view"),
    (136, PERMISSION_RECEIPT_LEDGER_ID, "VAULT_GP136", "Permission Receipt Draft Ledger", "permission_receipt_draft_ledger"),
    (137, DENIAL_BLOCK_REASON_ID, "VAULT_GP137", "Denial and Block Reason Board", "denial_and_block_reason_board"),
    (138, TOWER_EVIDENCE_MAP_ID, "VAULT_GP138", "Tower Handoff Evidence Map", "tower_handoff_evidence_map"),
    (139, PERMISSION_BLOCKER_BOARD_ID, "VAULT_GP139", "Tower-Gated Permission Blocker Board", "tower_gated_permission_blocker_board"),
    (140, READINESS_ID, "VAULT_GP140", "Tower-Gated Permission Readiness Checkpoint", "tower_gated_permission_readiness_checkpoint"),
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
        "source_gp130_readiness_score",
        "permission_draft_count",
        "step_up_challenge_count",
        "tower_review_item_count",
        "authority_boundary_count",
        "permission_receipt_draft_count",
        "denial_reason_count",
        "evidence_link_count",
        "blocker_count",
        "component_count",
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
        "depends_on": ["VAULT_GP130"],
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
        "depends_on": ["VAULT_GP130"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_tower_gated_permission_step_up_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_tower_permission_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp130_readiness_id TEXT NOT NULL,
                source_gp130_readiness_hash TEXT NOT NULL,
                source_gp130_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                tower_gated INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_permission_request_drafts (
                draft_id TEXT PRIMARY KEY,
                draft_code TEXT NOT NULL UNIQUE,
                permission_name TEXT NOT NULL,
                permission_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                draft_status TEXT NOT NULL,
                source_gp130_readiness_hash TEXT NOT NULL,
                draft_ready INTEGER NOT NULL DEFAULT 1,
                draft_locked INTEGER NOT NULL DEFAULT 1,
                tower_gated INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                draft_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_step_up_challenge_locks (
                challenge_id TEXT PRIMARY KEY,
                challenge_code TEXT NOT NULL UNIQUE,
                permission_draft_id TEXT NOT NULL,
                challenge_name TEXT NOT NULL,
                challenge_status TEXT NOT NULL,
                challenge_locked INTEGER NOT NULL DEFAULT 1,
                tower_gated INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                challenge_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_tower_gate_review_queue (
                review_item_id TEXT PRIMARY KEY,
                queue_code TEXT NOT NULL UNIQUE,
                permission_draft_id TEXT NOT NULL,
                review_status TEXT NOT NULL,
                review_locked INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                owner_review_required INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_owner_authority_boundaries (
                boundary_id TEXT PRIMARY KEY,
                boundary_code TEXT NOT NULL UNIQUE,
                boundary_name TEXT NOT NULL,
                boundary_category TEXT NOT NULL,
                boundary_status TEXT NOT NULL,
                boundary_locked INTEGER NOT NULL DEFAULT 1,
                owner_visible INTEGER NOT NULL DEFAULT 1,
                tower_gated INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                boundary_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_permission_receipt_drafts (
                receipt_draft_id TEXT PRIMARY KEY,
                receipt_code TEXT NOT NULL UNIQUE,
                permission_draft_id TEXT NOT NULL,
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
            CREATE TABLE IF NOT EXISTS vault_permission_denial_reasons (
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
            CREATE TABLE IF NOT EXISTS vault_tower_handoff_evidence_links (
                evidence_id TEXT PRIMARY KEY,
                evidence_code TEXT NOT NULL UNIQUE,
                source_ref TEXT NOT NULL,
                evidence_name TEXT NOT NULL,
                evidence_status TEXT NOT NULL,
                evidence_locked INTEGER NOT NULL DEFAULT 1,
                tower_gated INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                evidence_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_tower_permission_blockers (
                blocker_id TEXT PRIMARY KEY,
                blocker_code TEXT NOT NULL UNIQUE,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocker_active INTEGER NOT NULL DEFAULT 1,
                blocks_permission_submit INTEGER NOT NULL DEFAULT 1,
                blocks_step_up_pass INTEGER NOT NULL DEFAULT 1,
                blocks_tower_unlock INTEGER NOT NULL DEFAULT 1,
                blocks_owner_execution INTEGER NOT NULL DEFAULT 1,
                blocks_provider_api INTEGER NOT NULL DEFAULT 1,
                blocks_object_body INTEGER NOT NULL DEFAULT 1,
                blocks_download INTEGER NOT NULL DEFAULT 1,
                blocks_export INTEGER NOT NULL DEFAULT 1,
                blocks_restore INTEGER NOT NULL DEFAULT 1,
                blocks_direct_upload INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_tower_permission_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                permission_draft_count INTEGER NOT NULL,
                step_up_challenge_count INTEGER NOT NULL,
                tower_review_item_count INTEGER NOT NULL,
                authority_boundary_count INTEGER NOT NULL,
                permission_receipt_draft_count INTEGER NOT NULL,
                denial_reason_count INTEGER NOT NULL,
                evidence_link_count INTEGER NOT NULL,
                blocker_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                safe_to_continue_to_gp141 INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_tower_permission_events (
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
            "vault_tower_permission_components",
            "vault_permission_request_drafts",
            "vault_step_up_challenge_locks",
            "vault_tower_gate_review_queue",
            "vault_owner_authority_boundaries",
            "vault_permission_receipt_drafts",
            "vault_permission_denial_reasons",
            "vault_tower_handoff_evidence_links",
            "vault_tower_permission_blockers",
            "vault_tower_permission_readiness",
            "vault_tower_permission_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VTGPSEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_tower_permission_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_tower_gated_permission_step_up_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_tower_gated_permission_step_up_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_tower_permission_components WHERE component_id = ?",
            (HANDOFF_SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp130_status = get_gp130_status()["gp130_status"]
            gp130_checkpoint = get_gp130_owner_console_readiness_checkpoint()["readiness_checkpoint"]
            gp130_home = get_owner_console_operating_dashboard_layer_home()
            gp130_validation = validate_owner_console_operating_dashboard_layer()

            source_metrics = get_owner_console_metrics()
            source_panels = get_owner_console_panels()
            source_actions = get_owner_console_safe_actions()
            source_blockers = get_owner_console_blockers()

            readiness = gp130_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp130_readiness_id": readiness["readiness_id"],
                "source_gp130_readiness_hash": readiness["readiness_hash"],
                "source_gp130_readiness_score": readiness["readiness_score"],
            }

            source_context = {
                "source_gp130_status_ready": gp130_status["ready"],
                "source_gp130_validation_passed": gp130_status["validation_passed"],
                "source_gp130_safe_to_continue_to_gp131": gp130_status["safe_to_continue_to_gp131"],
                "source_gp130_readiness_hash": readiness["readiness_hash"],
                "source_gp130_readiness_score": readiness["readiness_score"],
                "source_metric_count": len(source_metrics),
                "source_panel_count": len(source_panels),
                "source_safe_action_count": len(source_actions),
                "source_blocker_count": len(source_blockers),
                "source_validation_check_count": gp130_validation["check_count"],
            }

            component_extra = {
                HANDOFF_SHELL_ID: {"tower_permission_handoff_shell_ready": True},
                PERMISSION_DRAFT_REGISTRY_ID: {"permission_request_draft_registry_ready": True, "permission_draft_count": len(PERMISSION_SURFACES)},
                STEP_UP_LOCK_ID: {"step_up_challenge_lock_contract_ready": True, "step_up_challenge_count": len(PERMISSION_SURFACES)},
                TOWER_REVIEW_QUEUE_ID: {"tower_gate_review_queue_ready": True, "tower_review_item_count": len(PERMISSION_SURFACES)},
                OWNER_AUTHORITY_BOUNDARY_ID: {"owner_authority_boundary_view_ready": True, "authority_boundary_count": len(PERMISSION_SURFACES)},
                PERMISSION_RECEIPT_LEDGER_ID: {"permission_receipt_draft_ledger_ready": True, "permission_receipt_draft_count": len(PERMISSION_SURFACES)},
                DENIAL_BLOCK_REASON_ID: {"denial_and_block_reason_board_ready": True, "denial_reason_count": len(DENIAL_REASONS)},
                TOWER_EVIDENCE_MAP_ID: {"tower_handoff_evidence_map_ready": True, "evidence_link_count": 8},
                PERMISSION_BLOCKER_BOARD_ID: {"tower_gated_permission_blocker_board_ready": True, "blocker_count": 10},
                READINESS_ID: {"tower_gated_permission_readiness_checkpoint_ready": True, "safe_to_continue_to_gp141": True},
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
                    "tower_gated": True,
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
                    "tower_gated": 1,
                    "owner_review_required": 1,
                    "tower_review_required": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_tower_permission_components", row)

            draft_ids = []
            for idx, (code, name, category, severity) in enumerate(PERMISSION_SURFACES, start=1):
                draft_id = f"VTGPSD-{idx:03d}"
                draft_ids.append((draft_id, code))
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "draft_id": draft_id,
                    "draft_code": code,
                    "permission_name": name,
                    "permission_category": category,
                    "severity": severity,
                    "draft_status": "DRAFT_ONLY_NOT_SUBMITTED_TOWER_GATED",
                    "source_gp130_readiness_hash": readiness["readiness_hash"],
                    "draft_ready": True,
                    "draft_locked": True,
                    "tower_gated": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "draft_id": draft_id,
                    "draft_code": code,
                    "permission_name": name,
                    "permission_category": category,
                    "severity": severity,
                    "draft_status": payload["draft_status"],
                    "source_gp130_readiness_hash": readiness["readiness_hash"],
                    "draft_ready": 1,
                    "draft_locked": 1,
                    "tower_gated": 1,
                    "payload_json": _json_dumps(payload),
                    "draft_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_permission_request_drafts", row)

                challenge_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "challenge_code": f"{code}_step_up_lock",
                    "permission_draft_id": draft_id,
                    "challenge_name": f"{name} Step-Up Lock",
                    "challenge_status": "LOCKED_NOT_STARTED_NOT_PASSED",
                    "challenge_locked": True,
                    "tower_gated": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "challenge_id": f"VTGPSC-{idx:03d}",
                    "challenge_code": challenge_payload["challenge_code"],
                    "permission_draft_id": draft_id,
                    "challenge_name": challenge_payload["challenge_name"],
                    "challenge_status": challenge_payload["challenge_status"],
                    "challenge_locked": 1,
                    "tower_gated": 1,
                    "payload_json": _json_dumps(challenge_payload),
                    "challenge_hash": _hash_payload(challenge_payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_step_up_challenge_locks", row)

                review_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "queue_code": f"{code}_tower_review",
                    "permission_draft_id": draft_id,
                    "review_status": "TOWER_REVIEW_REQUIRED_LOCKED_NO_DECISION",
                    "review_locked": True,
                    "tower_review_required": True,
                    "owner_review_required": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "review_item_id": f"VTGPSRQ-{idx:03d}",
                    "queue_code": review_payload["queue_code"],
                    "permission_draft_id": draft_id,
                    "review_status": review_payload["review_status"],
                    "review_locked": 1,
                    "tower_review_required": 1,
                    "owner_review_required": 1,
                    "payload_json": _json_dumps(review_payload),
                    "review_hash": _hash_payload(review_payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_tower_gate_review_queue", row)

                boundary_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "boundary_code": f"{code}_authority_boundary",
                    "boundary_name": f"{name} Authority Boundary",
                    "boundary_category": category,
                    "boundary_status": "OWNER_CAN_VIEW_CANNOT_APPROVE_EXECUTE_OR_UNLOCK",
                    "boundary_locked": True,
                    "owner_visible": True,
                    "tower_gated": True,
                    "allowed_owner_actions": ["view", "review", "prepare_questions"],
                    "blocked_owner_actions": ["approve", "reject_final", "submit_permission", "pass_step_up", "unlock_tower", "execute"],
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "boundary_id": f"VTGPSB-{idx:03d}",
                    "boundary_code": boundary_payload["boundary_code"],
                    "boundary_name": boundary_payload["boundary_name"],
                    "boundary_category": category,
                    "boundary_status": boundary_payload["boundary_status"],
                    "boundary_locked": 1,
                    "owner_visible": 1,
                    "tower_gated": 1,
                    "payload_json": _json_dumps(boundary_payload),
                    "boundary_hash": _hash_payload(boundary_payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_owner_authority_boundaries", row)

                receipt_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "receipt_code": f"{code}_permission_receipt_draft",
                    "permission_draft_id": draft_id,
                    "receipt_name": f"{name} Permission Receipt Draft",
                    "receipt_status": "DRAFT_ONLY_NOT_FINALIZED_NOT_PERSISTED",
                    "receipt_draft_locked": True,
                    "final_receipt_created": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "receipt_draft_id": f"VTGPSRD-{idx:03d}",
                    "receipt_code": receipt_payload["receipt_code"],
                    "permission_draft_id": draft_id,
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
                _insert_dict(conn, "vault_permission_receipt_drafts", row)

            for idx, (code, name, category) in enumerate(DENIAL_REASONS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "denial_code": code,
                    "denial_name": name,
                    "denial_category": category,
                    "denial_status": "ACTIVE_BLOCK_REASON_NOT_FINAL_DENIAL",
                    "denial_active": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "denial_id": f"VTGPSDEN-{idx:03d}",
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
                _insert_dict(conn, "vault_permission_denial_reasons", row)

            evidence_refs = [
                "GP130_OWNER_CONSOLE_READINESS",
                "GP120_REDACTED_BROWSER_READINESS",
                "GP110_RECOVERY_CASE_WORKSPACE",
                "OWNER_CONSOLE_METRICS",
                "OWNER_CONSOLE_PANELS",
                "OWNER_SAFE_ACTIONS",
                "OWNER_CONSOLE_BLOCKERS",
                "NEXT_GP141_HANDOFF",
            ]
            for idx, ref in enumerate(evidence_refs, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "evidence_code": ref.lower(),
                    "source_ref": ref,
                    "evidence_name": f"Tower handoff evidence: {ref}",
                    "evidence_status": "EVIDENCE_LINK_LOCKED_FOR_TOWER_HANDOFF",
                    "evidence_locked": True,
                    "tower_gated": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "evidence_id": f"VTGPSE-{idx:03d}",
                    "evidence_code": payload["evidence_code"],
                    "source_ref": ref,
                    "evidence_name": payload["evidence_name"],
                    "evidence_status": payload["evidence_status"],
                    "evidence_locked": 1,
                    "tower_gated": 1,
                    "payload_json": _json_dumps(payload),
                    "evidence_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_tower_handoff_evidence_links", row)

            blocker_specs = [
                ("permission_submit_locked", "Permission submit locked", "permission", "critical"),
                ("step_up_pass_locked", "Step-up pass locked", "step_up", "critical"),
                ("tower_unlock_locked", "Tower unlock locked", "tower", "critical"),
                ("owner_execution_locked", "Owner execution locked", "owner_execution", "critical"),
                ("provider_api_locked", "Provider API locked", "provider", "critical"),
                ("object_body_locked", "Object body locked", "object_body", "critical"),
                ("export_restore_locked", "Export and restore locked", "export_restore", "critical"),
                ("direct_upload_locked", "Direct upload locked", "upload", "critical"),
                ("execution_locked", "Execution locked", "execution", "critical"),
                ("vault_done_locked", "Vault done locked", "done", "critical"),
            ]
            for idx, (code, name, category, severity) in enumerate(blocker_specs, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "ACTIVE_TOWER_PERMISSION_BLOCKER",
                    "blocker_active": True,
                    "blocks_permission_submit": True,
                    "blocks_step_up_pass": True,
                    "blocks_tower_unlock": True,
                    "blocks_owner_execution": True,
                    "blocks_provider_api": True,
                    "blocks_object_body": True,
                    "blocks_download": True,
                    "blocks_export": True,
                    "blocks_restore": True,
                    "blocks_direct_upload": True,
                    "blocks_execution": True,
                    "blocks_vault_done": True,
                    "resolved": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "blocker_id": f"VTGPSBLK-{idx:03d}",
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": payload["blocker_status"],
                    "blocker_active": 1,
                    "blocks_permission_submit": 1,
                    "blocks_step_up_pass": 1,
                    "blocks_tower_unlock": 1,
                    "blocks_owner_execution": 1,
                    "blocks_provider_api": 1,
                    "blocks_object_body": 1,
                    "blocks_download": 1,
                    "blocks_export": 1,
                    "blocks_restore": 1,
                    "blocks_direct_upload": 1,
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
                _insert_dict(conn, "vault_tower_permission_blockers", row)

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "permission_draft_count": len(PERMISSION_SURFACES),
                "step_up_challenge_count": len(PERMISSION_SURFACES),
                "tower_review_item_count": len(PERMISSION_SURFACES),
                "authority_boundary_count": len(PERMISSION_SURFACES),
                "permission_receipt_draft_count": len(PERMISSION_SURFACES),
                "denial_reason_count": len(DENIAL_REASONS),
                "evidence_link_count": len(evidence_refs),
                "blocker_count": len(blocker_specs),
            }

            checks = [
                ("SOURCE_GP130_READY", bool(gp130_status["ready"])),
                ("SOURCE_GP130_VALIDATION_PASSED", bool(gp130_status["validation_passed"])),
                ("SOURCE_GP130_SAFE_TO_CONTINUE", bool(gp130_status["safe_to_continue_to_gp131"])),
                ("SOURCE_GP130_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP130_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("PERMISSION_DRAFT_COUNT_8", counts["permission_draft_count"] == 8),
                ("STEP_UP_CHALLENGE_COUNT_8", counts["step_up_challenge_count"] == 8),
                ("TOWER_REVIEW_ITEM_COUNT_8", counts["tower_review_item_count"] == 8),
                ("AUTHORITY_BOUNDARY_COUNT_8", counts["authority_boundary_count"] == 8),
                ("PERMISSION_RECEIPT_DRAFT_COUNT_8", counts["permission_receipt_draft_count"] == 8),
                ("DENIAL_REASON_COUNT_8", counts["denial_reason_count"] == 8),
                ("EVIDENCE_LINK_COUNT_8", counts["evidence_link_count"] == 8),
                ("BLOCKER_COUNT_10", counts["blocker_count"] == 10),
                ("SECTION_GP131_GP140", SECTION_RANGE == "GP131-GP140"),
                ("NEXT_SECTION_GP141_GP150", NEXT_SECTION_RANGE == "GP141-GP150"),
                ("NO_PERMISSION_SUBMIT", True),
                ("NO_STEP_UP_PASS", True),
                ("NO_TOWER_UNLOCK", True),
                ("NO_OWNER_EXECUTION", True),
                ("NO_PROVIDER_API", True),
                ("NO_OBJECT_BODY", True),
                ("NO_DOWNLOAD", True),
                ("NO_EXPORT", True),
                ("NO_RESTORE", True),
                ("NO_DIRECT_UPLOAD", True),
                ("NO_EXECUTION", True),
                ("VAULT_NOT_DONE", True),
                ("CLOUDS_PARKED", True),
            ]
            passed_count = len([c for c in checks if c[1]])
            failed_count = len(checks) - passed_count

            readiness_payload = {
                "schema_version": SCHEMA_VERSION,
                "readiness_id": READINESS_ID,
                "gp_number": 140,
                "pack_id": "VAULT_GP140",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp130_readiness_id": readiness["readiness_id"],
                "source_gp130_readiness_hash": readiness["readiness_hash"],
                "source_gp130_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "safe_to_continue_to_gp141": failed_count == 0,
                "section_ready": True,
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
                "gp_number": 140,
                "pack_id": "VAULT_GP140",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "TOWER_GATED_PERMISSION_STEP_UP_LAYER_READY_LOCKED_SAFE_TO_CONTINUE_NOT_DONE",
                "readiness_score": readiness_payload["readiness_score"],
                **counts,
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "safe_to_continue_to_gp141": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_tower_permission_readiness", row)

            for event_type, event_payload in [
                ("GP131_TOWER_PERMISSION_HANDOFF_SHELL_CREATED", {"component_id": HANDOFF_SHELL_ID}),
                ("GP132_PERMISSION_REQUEST_DRAFT_REGISTRY_CREATED", {"permission_draft_count": counts["permission_draft_count"]}),
                ("GP133_STEP_UP_CHALLENGE_LOCK_CONTRACT_CREATED", {"step_up_challenge_count": counts["step_up_challenge_count"]}),
                ("GP134_TOWER_GATE_REVIEW_QUEUE_CREATED", {"tower_review_item_count": counts["tower_review_item_count"]}),
                ("GP135_OWNER_AUTHORITY_BOUNDARY_VIEW_CREATED", {"authority_boundary_count": counts["authority_boundary_count"]}),
                ("GP136_PERMISSION_RECEIPT_DRAFT_LEDGER_CREATED", {"permission_receipt_draft_count": counts["permission_receipt_draft_count"]}),
                ("GP137_DENIAL_AND_BLOCK_REASON_BOARD_CREATED", {"denial_reason_count": counts["denial_reason_count"]}),
                ("GP138_TOWER_HANDOFF_EVIDENCE_MAP_CREATED", {"evidence_link_count": counts["evidence_link_count"]}),
                ("GP139_TOWER_GATED_PERMISSION_BLOCKER_BOARD_CREATED", {"blocker_count": counts["blocker_count"]}),
                ("GP140_TOWER_GATED_PERMISSION_READINESS_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp141": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_tower_permission_components").fetchone()["c"]),
            "permission_draft_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_permission_request_drafts").fetchone()["c"]),
            "step_up_challenge_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_step_up_challenge_locks").fetchone()["c"]),
            "tower_review_item_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_tower_gate_review_queue").fetchone()["c"]),
            "authority_boundary_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_authority_boundaries").fetchone()["c"]),
            "permission_receipt_draft_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_permission_receipt_drafts").fetchone()["c"]),
            "denial_reason_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_permission_denial_reasons").fetchone()["c"]),
            "evidence_link_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_tower_handoff_evidence_links").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_tower_permission_blockers").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_tower_permission_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_tower_permission_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_tower_gated_permission_step_up_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_tower_gated_permission_step_up_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute("SELECT * FROM vault_tower_permission_components WHERE component_id = ?", (component_id,)).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_tower_gated_permission_step_up_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute("SELECT * FROM vault_tower_permission_readiness WHERE readiness_id = ?", (READINESS_ID,)).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_tower_gated_permission_step_up_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_tower_permission_events ORDER BY created_at, event_id").fetchall()
    return [{"event_id": row["event_id"], "event_type": row["event_type"], "event_payload": _json_loads(row["event_payload_json"]), "created_at": row["created_at"]} for row in rows]

def get_permission_request_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_permission_request_drafts", "draft_code", db_path, {"payload_json": "payload"})

def get_step_up_challenge_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_step_up_challenge_locks", "challenge_code", db_path, {"payload_json": "payload"})

def get_tower_gate_review_queue(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_tower_gate_review_queue", "queue_code", db_path, {"payload_json": "payload"})

def get_owner_authority_boundaries(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_owner_authority_boundaries", "boundary_code", db_path, {"payload_json": "payload"})

def get_permission_receipt_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_permission_receipt_drafts", "receipt_code", db_path, {"payload_json": "payload"})

def get_permission_denial_reasons(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_permission_denial_reasons", "denial_code", db_path, {"payload_json": "payload"})

def get_tower_handoff_evidence_links(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_tower_handoff_evidence_links", "evidence_code", db_path, {"payload_json": "payload"})

def get_tower_permission_blockers(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_tower_permission_blockers", "blocker_code", db_path, {"payload_json": "payload"})

def validate_tower_gated_permission_step_up_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_tower_permission_components", "gp_number", db_path, {"data_json": "data"})
    drafts = get_permission_request_drafts(db_path)
    challenges = get_step_up_challenge_locks(db_path)
    queue = get_tower_gate_review_queue(db_path)
    boundaries = get_owner_authority_boundaries(db_path)
    receipts = get_permission_receipt_drafts(db_path)
    denials = get_permission_denial_reasons(db_path)
    evidence = get_tower_handoff_evidence_links(db_path)
    blockers = get_tower_permission_blockers(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("PERMISSION_DRAFT_COUNT_8", len(drafts) == len(PERMISSION_SURFACES)),
        ("STEP_UP_CHALLENGE_COUNT_8", len(challenges) == len(PERMISSION_SURFACES)),
        ("TOWER_REVIEW_QUEUE_COUNT_8", len(queue) == len(PERMISSION_SURFACES)),
        ("AUTHORITY_BOUNDARY_COUNT_8", len(boundaries) == len(PERMISSION_SURFACES)),
        ("PERMISSION_RECEIPT_DRAFT_COUNT_8", len(receipts) == len(PERMISSION_SURFACES)),
        ("DENIAL_REASON_COUNT_8", len(denials) == len(DENIAL_REASONS)),
        ("EVIDENCE_LINK_COUNT_8", len(evidence) == 8),
        ("BLOCKER_COUNT_10", len(blockers) == 10),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("SAFE_TO_CONTINUE_TO_GP141", readiness["safe_to_continue_to_gp141"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("SECTION_GP131_GP140", readiness["section_range"] == "GP131-GP140"),
        ("NEXT_SECTION_GP141_GP150", readiness["readiness_payload"]["next_section_range"] == "GP141-GP150"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_TOWER_GATED", all(item["tower_gated"] is True for item in components)),
        ("ALL_DRAFTS_LOCKED", all(item["draft_locked"] is True for item in drafts)),
        ("ALL_DRAFTS_NOT_SUBMITTED", all(item["permission_request_submitted"] is False for item in drafts)),
        ("ALL_CHALLENGES_LOCKED", all(item["challenge_locked"] is True for item in challenges)),
        ("ALL_CHALLENGES_NOT_STARTED", all(item["step_up_challenge_started"] is False for item in challenges)),
        ("ALL_CHALLENGES_NOT_PASSED", all(item["step_up_challenge_passed"] is False for item in challenges)),
        ("ALL_REVIEWS_LOCKED", all(item["review_locked"] is True for item in queue)),
        ("ALL_BOUNDARIES_LOCKED", all(item["boundary_locked"] is True for item in boundaries)),
        ("ALL_RECEIPTS_DRAFT_LOCKED", all(item["receipt_draft_locked"] is True for item in receipts)),
        ("NO_FINAL_RECEIPTS_CREATED", all(item["final_receipt_created"] is False for item in receipts)),
        ("ALL_DENIAL_REASONS_ACTIVE", all(item["denial_active"] is True for item in denials)),
        ("ALL_EVIDENCE_LOCKED", all(item["evidence_locked"] is True for item in evidence)),
        ("ALL_BLOCKERS_ACTIVE", all(item["blocker_active"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PERMISSION_SUBMIT", all(item["blocks_permission_submit"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_STEP_UP_PASS", all(item["blocks_step_up_pass"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_TOWER_UNLOCK", all(item["blocks_tower_unlock"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_OWNER_EXECUTION", all(item["blocks_owner_execution"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", all(item["blocks_provider_api"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY", all(item["blocks_object_body"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DOWNLOAD", all(item["blocks_download"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_EXPORT", all(item["blocks_export"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_RESTORE", all(item["blocks_restore"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DIRECT_UPLOAD", all(item["blocks_direct_upload"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_EXECUTION", all(item["blocks_execution"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_VAULT_DONE", all(item["blocks_vault_done"] is True for item in blockers)),
        ("NO_BLOCKERS_RESOLVED", all(item["resolved"] is False for item in blockers)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("DRAFT", drafts),
        ("CHALLENGE", challenges),
        ("QUEUE", queue),
        ("BOUNDARY", boundaries),
        ("RECEIPT", receipts),
        ("DENIAL", denials),
        ("EVIDENCE", evidence),
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
        "permission_draft_count": len(drafts),
        "step_up_challenge_count": len(challenges),
        "tower_review_item_count": len(queue),
        "authority_boundary_count": len(boundaries),
        "permission_receipt_draft_count": len(receipts),
        "denial_reason_count": len(denials),
        "evidence_link_count": len(evidence),
        "blocker_count": len(blockers),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "safe_to_continue_to_gp141": len(failed) == 0 and readiness["safe_to_continue_to_gp141"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp131_tower_permission_handoff_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(HANDOFF_SHELL_ID, db_path)
    return {"pack": _pack_payload(131, component["pack_name"]), "real_sqlite_backed": True, "handoff_shell": component}

def get_gp132_permission_request_draft_registry(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(PERMISSION_DRAFT_REGISTRY_ID, db_path)
    drafts = get_permission_request_drafts(db_path)
    return {"pack": _pack_payload(132, component["pack_name"]), "real_sqlite_backed": True, "permission_request_draft_registry": component, "permission_draft_count": len(drafts), "drafts": drafts}

def get_gp133_step_up_challenge_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(STEP_UP_LOCK_ID, db_path)
    challenges = get_step_up_challenge_locks(db_path)
    return {"pack": _pack_payload(133, component["pack_name"]), "real_sqlite_backed": True, "step_up_challenge_lock_contract": component, "step_up_challenge_count": len(challenges), "challenges": challenges}

def get_gp134_tower_gate_review_queue(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(TOWER_REVIEW_QUEUE_ID, db_path)
    queue = get_tower_gate_review_queue(db_path)
    return {"pack": _pack_payload(134, component["pack_name"]), "real_sqlite_backed": True, "tower_gate_review_queue": component, "tower_review_item_count": len(queue), "queue": queue}

def get_gp135_owner_authority_boundary_view(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(OWNER_AUTHORITY_BOUNDARY_ID, db_path)
    boundaries = get_owner_authority_boundaries(db_path)
    return {"pack": _pack_payload(135, component["pack_name"]), "real_sqlite_backed": True, "owner_authority_boundary_view": component, "authority_boundary_count": len(boundaries), "boundaries": boundaries}

def get_gp136_permission_receipt_draft_ledger(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(PERMISSION_RECEIPT_LEDGER_ID, db_path)
    receipts = get_permission_receipt_drafts(db_path)
    return {"pack": _pack_payload(136, component["pack_name"]), "real_sqlite_backed": True, "permission_receipt_draft_ledger": component, "permission_receipt_draft_count": len(receipts), "receipt_drafts": receipts}

def get_gp137_denial_and_block_reason_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(DENIAL_BLOCK_REASON_ID, db_path)
    reasons = get_permission_denial_reasons(db_path)
    return {"pack": _pack_payload(137, component["pack_name"]), "real_sqlite_backed": True, "denial_and_block_reason_board": component, "denial_reason_count": len(reasons), "denial_reasons": reasons}

def get_gp138_tower_handoff_evidence_map(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(TOWER_EVIDENCE_MAP_ID, db_path)
    evidence = get_tower_handoff_evidence_links(db_path)
    return {"pack": _pack_payload(138, component["pack_name"]), "real_sqlite_backed": True, "tower_handoff_evidence_map": component, "evidence_link_count": len(evidence), "evidence_links": evidence}

def get_gp139_tower_gated_permission_blocker_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(PERMISSION_BLOCKER_BOARD_ID, db_path)
    blockers = get_tower_permission_blockers(db_path)
    return {"pack": _pack_payload(139, component["pack_name"]), "real_sqlite_backed": True, "tower_gated_permission_blocker_board": component, "blocker_count": len(blockers), "blockers": blockers}

def get_gp140_tower_gated_permission_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_tower_gated_permission_step_up_layer(db_path)
    return {"pack": _pack_payload(140, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_tower_gated_permission_step_up_layer(db_path)
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
            "source_gp130_readiness_id": component["source_gp130_readiness_id"],
            "source_gp130_readiness_hash": component["source_gp130_readiness_hash"],
            "source_gp130_readiness_score": component["source_gp130_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "tower_gated": component["tower_gated"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp141": validation["safe_to_continue_to_gp141"],
            "foundation_status": "tower_gated_permission_step_up_layer_ready_locked_safe_to_continue_not_done",
            "next": next_label,
            **counts,
            "permission_request_submitted": component["permission_request_submitted"],
            "permission_request_approved": component["permission_request_approved"],
            "permission_request_granted": component["permission_request_granted"],
            "step_up_challenge_started": component["step_up_challenge_started"],
            "step_up_challenge_passed": component["step_up_challenge_passed"],
            "step_up_token_created": component["step_up_token_created"],
            "step_up_session_created": component["step_up_session_created"],
            "tower_gate_opened": component["tower_gate_opened"],
            "tower_gate_passed": component["tower_gate_passed"],
            "tower_unlock_requested": component["tower_unlock_requested"],
            "tower_unlock_granted": component["tower_unlock_granted"],
            "tower_clearance_granted": component["tower_clearance_granted"],
            "owner_decision_recorded": component["owner_decision_recorded"],
            "owner_approval_recorded": component["owner_approval_recorded"],
            "owner_execute_action_approved": component["owner_execute_action_approved"],
            "provider_api_called": component["provider_api_called"],
            "provider_objects_listed": component["provider_objects_listed"],
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
            "execution_enabled": component["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp140",
        },
        "validation": validation,
    }

def get_gp131_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(131, HANDOFF_SHELL_ID, "VAULT_GP132_PERMISSION_REQUEST_DRAFT_REGISTRY", db_path)

def get_gp132_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(132, PERMISSION_DRAFT_REGISTRY_ID, "VAULT_GP133_STEP_UP_CHALLENGE_LOCK_CONTRACT", db_path)

def get_gp133_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(133, STEP_UP_LOCK_ID, "VAULT_GP134_TOWER_GATE_REVIEW_QUEUE", db_path)

def get_gp134_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(134, TOWER_REVIEW_QUEUE_ID, "VAULT_GP135_OWNER_AUTHORITY_BOUNDARY_VIEW", db_path)

def get_gp135_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(135, OWNER_AUTHORITY_BOUNDARY_ID, "VAULT_GP136_PERMISSION_RECEIPT_DRAFT_LEDGER", db_path)

def get_gp136_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(136, PERMISSION_RECEIPT_LEDGER_ID, "VAULT_GP137_DENIAL_AND_BLOCK_REASON_BOARD", db_path)

def get_gp137_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(137, DENIAL_BLOCK_REASON_ID, "VAULT_GP138_TOWER_HANDOFF_EVIDENCE_MAP", db_path)

def get_gp138_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(138, TOWER_EVIDENCE_MAP_ID, "VAULT_GP139_TOWER_GATED_PERMISSION_BLOCKER_BOARD", db_path)

def get_gp139_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(139, PERMISSION_BLOCKER_BOARD_ID, "VAULT_GP140_TOWER_GATED_PERMISSION_READINESS_CHECKPOINT", db_path)

def get_gp140_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(140, READINESS_ID, NEXT_PACK, db_path)
    status["gp140_status"]["next_section"] = NEXT_SECTION_ID
    status["gp140_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp140_status"]["next_pack"] = NEXT_PACK
    return status

def get_tower_gated_permission_step_up_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_tower_gated_permission_step_up_layer(db_path)
    components = _rows("vault_tower_permission_components", "gp_number", db_path, {"data_json": "data"})
    drafts = get_permission_request_drafts(db_path)
    challenges = get_step_up_challenge_locks(db_path)
    queue = get_tower_gate_review_queue(db_path)
    boundaries = get_owner_authority_boundaries(db_path)
    receipts = get_permission_receipt_drafts(db_path)
    denials = get_permission_denial_reasons(db_path)
    evidence = get_tower_handoff_evidence_links(db_path)
    blockers = get_tower_permission_blockers(db_path)
    readiness = _readiness(db_path)
    validation = validate_tower_gated_permission_step_up_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "permission_drafts": {"permission_draft_count": len(drafts), "drafts": drafts},
        "step_up_challenges": {"step_up_challenge_count": len(challenges), "challenges": challenges},
        "tower_review_queue": {"tower_review_item_count": len(queue), "queue": queue},
        "owner_authority_boundaries": {"authority_boundary_count": len(boundaries), "boundaries": boundaries},
        "permission_receipt_drafts": {"permission_receipt_draft_count": len(receipts), "receipt_drafts": receipts},
        "denial_reasons": {"denial_reason_count": len(denials), "denial_reasons": denials},
        "evidence_map": {"evidence_link_count": len(evidence), "evidence_links": evidence},
        "blockers": {"blocker_count": len(blockers), "blockers": blockers},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "tower_gated_permission_step_up_layer_ready": True,
            "permission_handoff_shell_ready": True,
            "permission_draft_registry_ready": True,
            "step_up_challenge_lock_contract_ready": True,
            "tower_gate_review_queue_ready": True,
            "owner_authority_boundary_view_ready": True,
            "permission_receipt_draft_ledger_ready": True,
            "denial_and_block_reason_board_ready": True,
            "tower_handoff_evidence_map_ready": True,
            "tower_gated_permission_blocker_board_ready": True,
            "safe_to_continue_to_gp141": validation["safe_to_continue_to_gp141"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "permission_request_submitted": False,
            "permission_request_approved": False,
            "step_up_challenge_passed": False,
            "step_up_token_created": False,
            "tower_unlock_granted": False,
            "tower_clearance_granted": False,
            "owner_approval_recorded": False,
            "provider_api_called": False,
            "provider_objects_listed": False,
            "provider_metadata_read": False,
            "object_body_read": False,
            "object_body_view_enabled": False,
            "object_body_download_enabled": False,
            "object_body_plaintext_visible": False,
            "export_package_created": False,
            "restore_job_created": False,
            "direct_upload_enabled": False,
            "execution_enabled": False,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        "routes": {
            "page": "/vault/tower-gated-permission-step-up-layer",
            "json": "/vault/tower-gated-permission-step-up-layer.json",
            "gp131": "/vault/gp131-status.json",
            "gp132": "/vault/gp132-status.json",
            "gp133": "/vault/gp133-status.json",
            "gp134": "/vault/gp134-status.json",
            "gp135": "/vault/gp135-status.json",
            "gp136": "/vault/gp136-status.json",
            "gp137": "/vault/gp137-status.json",
            "gp138": "/vault/gp138-status.json",
            "gp139": "/vault/gp139-status.json",
            "gp140": "/vault/gp140-status.json",
        },
    }

def render_tower_gated_permission_step_up_layer_page() -> str:
    home = get_tower_gated_permission_step_up_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    draft_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['permission_name'])}</strong>
          <span>{escape(item['draft_status'])}</span>
          <code>{escape(item['permission_category'])} · {escape(item['severity'])}</code>
        </article>
        """
        for item in home["permission_drafts"]["drafts"]
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
<title>Vault GP131-GP140 Tower-Gated Permission Step-Up Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 131-140</div>
    <div class="eyebrow">Tower-Gated Permission and Step-Up Layer · GP131-GP140</div>
    <h1>Tower-Gated Permission and Step-Up Layer</h1>
    <p>This layer creates the Tower handoff, permission draft, step-up lock, review queue, boundary, receipt draft, denial reason, evidence, blocker, and readiness surfaces. It does not grant permission, pass step-up, or unlock anything.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['permission_draft_count']}</strong><span>permission drafts</span></div>
      <div class="metric"><strong>{home['store']['step_up_challenge_count']}</strong><span>step-up locks</span></div>
      <div class="metric"><strong>{home['store']['blocker_count']}</strong><span>active blockers</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP131-GP140 built</span>
      <span class="pill ok">Tower handoff ready</span>
      <span class="pill ok">Safe to GP141</span>
      <span class="pill danger">No permission submit</span>
      <span class="pill danger">No step-up pass</span>
      <span class="pill danger">No Tower unlock</span>
      <span class="pill danger">No provider API</span>
      <span class="pill danger">No object body</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Permission Drafts</h2>
    <div class="cards">{draft_cards}</div>
  </section>

  <section class="section">
    <h2>Tower Permission Blockers</h2>
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
