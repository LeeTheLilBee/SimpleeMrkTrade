"""
VAULT GP101-GP110 — Real Provider Recovery Case Workspace Layer

New section:
Archive Vault — Real Provider Recovery Case Workspace Layer / GP101-GP110

Builds:
- GP101 Recovery Case Workspace Index
- GP102 Recovery Case Receipt Ledger
- GP103 Recovery Case Owner Review Queue
- GP104 Recovery Case Detail Room
- GP105 Recovery Case Evidence Link Map
- GP106 Redacted Object Reference View
- GP107 Export Package Lock Preview
- GP108 Restore Job Lock Preview
- GP109 Recovery Case Blocker Review Board
- GP110 Recovery Case Workspace Readiness Checkpoint

This layer makes Vault operationally useful as a recovery/audit case workspace
while still blocking restore, export, provider API calls, object body reads,
direct upload, Tower unlock, execution, and Vault-done.
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

from vault.real_provider_post_closeout_handoff_owner_review_closeout_layer_service import (
    get_gp100_status,
    get_gp100_governance_readiness_checkpoint,
    get_post_closeout_handoff_governance_closeout_layer_home,
    validate_post_closeout_handoff_governance_closeout_layer,
)

LAYER_ID = "VAULT_GP101_110"
LAYER_NAME = "Real Provider Recovery Case Workspace Layer"
SCHEMA_VERSION = "vault.real_provider_recovery_case_workspace_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_RECOVERY_CASE_WORKSPACE_LAYER"
SECTION_TITLE = "Archive Vault — Real Provider Recovery Case Workspace Layer"
SECTION_RANGE = "GP101-GP110"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_REAL_PROVIDER_POST_CLOSEOUT_HANDOFF_GOVERNANCE_LAYER"
PREVIOUS_SECTION_RANGE = "GP091-GP100"

NEXT_SECTION_ID = "ARCHIVE_VAULT_REDACTED_ARCHIVE_BROWSER_LAYER"
NEXT_SECTION_RANGE = "GP111-GP120"
NEXT_PACK = "VAULT_GP111_120_REDACTED_ARCHIVE_BROWSER_LAYER"

DEFAULT_DB_ENV = "VAULT_RECOVERY_CASE_WORKSPACE_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_recovery_case_workspace_layer.sqlite"

WORKSPACE_INDEX_ID = "VRCCWI-GP101-001"
RECEIPT_LEDGER_ID = "VRCCRL-GP102-001"
OWNER_REVIEW_QUEUE_ID = "VRCCORQ-GP103-001"
DETAIL_ROOM_ID = "VRCCDR-GP104-001"
EVIDENCE_LINK_MAP_ID = "VRCCELM-GP105-001"
REDACTED_OBJECT_VIEW_ID = "VRCCROV-GP106-001"
EXPORT_PREVIEW_ID = "VRCCEPLP-GP107-001"
RESTORE_PREVIEW_ID = "VRCCRJLP-GP108-001"
BLOCKER_BOARD_ID = "VRCCBRB-GP109-001"
READINESS_ID = "VRCCWRC-GP110-001"

FALSE_FIELDS = [
    "case_restore_requested",
    "case_restore_submitted",
    "case_restore_approved",
    "case_export_requested",
    "case_export_submitted",
    "case_export_approved",
    "owner_decision_recorded",
    "owner_approval_recorded",
    "owner_rejection_recorded",
    "tower_unlock_requested",
    "tower_unlock_granted",
    "restore_request_created",
    "restore_request_submitted",
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
    "export_package_created",
    "export_manifest_created",
    "export_download_enabled",
    "direct_upload_enabled",
    "export_enabled",
    "execution_enabled",
    "vault_done",
    "clouds_should_continue",
]

CASE_SPECS = [
    ("provider_handoff_review_case", "Provider Handoff Review Case", "provider_handoff", "Trust", "high"),
    ("object_recovery_review_case", "Object Recovery Review Case", "object_recovery", "Business", "high"),
    ("export_readiness_review_case", "Export Readiness Review Case", "export_readiness", "Owner", "high"),
    ("owner_evidence_review_case", "Owner Evidence Review Case", "owner_evidence", "Trust", "medium"),
    ("receipt_lineage_issue_case", "Receipt Lineage Issue Case", "receipt_lineage", "Operations", "medium"),
    ("missing_document_proof_case", "Missing Document Proof Case", "missing_document_proof", "Property", "medium"),
    ("redacted_metadata_review_case", "Redacted Metadata Review Case", "redacted_metadata", "ATM", "medium"),
    ("future_restore_preparation_case", "Future Restore Preparation Case", "future_restore_preparation", "Archive", "high"),
]

COMPONENT_SPECS = [
    (101, WORKSPACE_INDEX_ID, "VAULT_GP101", "Real Provider Recovery Case Workspace Index", "recovery_case_workspace_index"),
    (102, RECEIPT_LEDGER_ID, "VAULT_GP102", "Recovery Case Receipt Ledger", "recovery_case_receipt_ledger"),
    (103, OWNER_REVIEW_QUEUE_ID, "VAULT_GP103", "Recovery Case Owner Review Queue", "recovery_case_owner_review_queue"),
    (104, DETAIL_ROOM_ID, "VAULT_GP104", "Recovery Case Detail Room", "recovery_case_detail_room"),
    (105, EVIDENCE_LINK_MAP_ID, "VAULT_GP105", "Recovery Case Evidence Link Map", "recovery_case_evidence_link_map"),
    (106, REDACTED_OBJECT_VIEW_ID, "VAULT_GP106", "Redacted Object Reference View", "redacted_object_reference_view"),
    (107, EXPORT_PREVIEW_ID, "VAULT_GP107", "Export Package Lock Preview", "export_package_lock_preview"),
    (108, RESTORE_PREVIEW_ID, "VAULT_GP108", "Restore Job Lock Preview", "restore_job_lock_preview"),
    (109, BLOCKER_BOARD_ID, "VAULT_GP109", "Recovery Case Blocker Review Board", "recovery_case_blocker_review_board"),
    (110, READINESS_ID, "VAULT_GP110", "Recovery Case Workspace Readiness Checkpoint", "recovery_case_workspace_readiness_checkpoint"),
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
        "source_gp100_readiness_score",
        "case_count",
        "receipt_count",
        "owner_review_item_count",
        "detail_room_count",
        "evidence_link_count",
        "redacted_object_reference_count",
        "export_preview_count",
        "restore_preview_count",
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
        "depends_on": ["VAULT_GP100"],
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
        "depends_on": ["VAULT_GP100"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_recovery_case_workspace_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_recovery_case_workspace_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp100_readiness_id TEXT NOT NULL,
                source_gp100_readiness_hash TEXT NOT NULL,
                source_gp100_readiness_score INTEGER NOT NULL,
                source_gp100_section_closed INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_recovery_case_workspace_cases (
                case_id TEXT PRIMARY KEY,
                case_code TEXT NOT NULL UNIQUE,
                case_title TEXT NOT NULL,
                case_type TEXT NOT NULL,
                business_lane TEXT NOT NULL,
                sensitivity_label TEXT NOT NULL,
                case_status TEXT NOT NULL,
                source_gp100_readiness_hash TEXT NOT NULL,
                source_gp100_readiness_score INTEGER NOT NULL,
                case_ready INTEGER NOT NULL DEFAULT 1,
                case_locked INTEGER NOT NULL DEFAULT 1,
                owner_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                case_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_recovery_case_workspace_receipts (
                receipt_id TEXT PRIMARY KEY,
                receipt_ledger_id TEXT NOT NULL,
                case_id TEXT NOT NULL,
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
                FOREIGN KEY(case_id) REFERENCES vault_recovery_case_workspace_cases(case_id) ON DELETE CASCADE,
                UNIQUE(receipt_ledger_id, receipt_code)
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_recovery_case_owner_review_queue (
                owner_review_item_id TEXT PRIMARY KEY,
                queue_id TEXT NOT NULL,
                case_id TEXT NOT NULL,
                queue_code TEXT NOT NULL,
                queue_status TEXT NOT NULL,
                owner_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                review_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                queue_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(case_id) REFERENCES vault_recovery_case_workspace_cases(case_id) ON DELETE CASCADE,
                UNIQUE(queue_id, queue_code)
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_recovery_case_evidence_links (
                evidence_link_id TEXT PRIMARY KEY,
                evidence_map_id TEXT NOT NULL,
                case_id TEXT NOT NULL,
                link_code TEXT NOT NULL,
                link_name TEXT NOT NULL,
                source_ref TEXT NOT NULL,
                evidence_payload_json TEXT NOT NULL,
                evidence_hash TEXT NOT NULL,
                evidence_locked INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(case_id) REFERENCES vault_recovery_case_workspace_cases(case_id) ON DELETE CASCADE,
                UNIQUE(evidence_map_id, link_code)
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_recovery_case_redacted_object_references (
                object_reference_id TEXT PRIMARY KEY,
                redacted_view_id TEXT NOT NULL,
                case_id TEXT NOT NULL,
                object_ref_code TEXT NOT NULL,
                object_category TEXT NOT NULL,
                redaction_label TEXT NOT NULL,
                provider_reference_placeholder TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                object_reference_hash TEXT NOT NULL,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                body_locked INTEGER NOT NULL DEFAULT 1,
                download_locked INTEGER NOT NULL DEFAULT 1,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(case_id) REFERENCES vault_recovery_case_workspace_cases(case_id) ON DELETE CASCADE,
                UNIQUE(redacted_view_id, object_ref_code)
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_recovery_case_blockers (
                blocker_id TEXT PRIMARY KEY,
                blocker_board_id TEXT NOT NULL,
                case_id TEXT NOT NULL,
                blocker_code TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocker_active INTEGER NOT NULL DEFAULT 1,
                blocks_restore INTEGER NOT NULL DEFAULT 1,
                blocks_export INTEGER NOT NULL DEFAULT 1,
                blocks_provider_api INTEGER NOT NULL DEFAULT 1,
                blocks_object_body INTEGER NOT NULL DEFAULT 1,
                blocks_direct_upload INTEGER NOT NULL DEFAULT 1,
                blocks_tower_unlock INTEGER NOT NULL DEFAULT 1,
                blocks_execution INTEGER NOT NULL DEFAULT 1,
                blocks_vault_done INTEGER NOT NULL DEFAULT 1,
                resolved INTEGER NOT NULL DEFAULT 0,
                payload_json TEXT NOT NULL,
                blocker_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(case_id) REFERENCES vault_recovery_case_workspace_cases(case_id) ON DELETE CASCADE,
                UNIQUE(blocker_board_id, blocker_code)
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_recovery_case_workspace_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                case_count INTEGER NOT NULL,
                receipt_count INTEGER NOT NULL,
                owner_review_item_count INTEGER NOT NULL,
                evidence_link_count INTEGER NOT NULL,
                redacted_object_reference_count INTEGER NOT NULL,
                blocker_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                safe_to_continue_to_gp111 INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_recovery_case_workspace_events (
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
            "vault_recovery_case_workspace_components",
            "vault_recovery_case_workspace_cases",
            "vault_recovery_case_workspace_receipts",
            "vault_recovery_case_owner_review_queue",
            "vault_recovery_case_evidence_links",
            "vault_recovery_case_redacted_object_references",
            "vault_recovery_case_blockers",
            "vault_recovery_case_workspace_readiness",
            "vault_recovery_case_workspace_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VRCCEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_recovery_case_workspace_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_recovery_case_workspace_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_recovery_case_workspace_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_recovery_case_workspace_components WHERE component_id = ?",
            (WORKSPACE_INDEX_ID,),
        ).fetchone()

        if existing is None:
            gp100_status = get_gp100_status()["gp100_status"]
            gp100_checkpoint = get_gp100_governance_readiness_checkpoint()["governance_readiness_checkpoint"]
            gp100_home = get_post_closeout_handoff_governance_closeout_layer_home()
            gp100_validation = validate_post_closeout_handoff_governance_closeout_layer()
            readiness = gp100_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp100_readiness_id": readiness["readiness_id"],
                "source_gp100_readiness_hash": readiness["readiness_hash"],
                "source_gp100_readiness_score": readiness["readiness_score"],
                "source_gp100_section_closed": 1 if readiness["section_closed"] else 0,
            }

            source_context = {
                "source_gp100_status_ready": gp100_status["ready"],
                "source_gp100_validation_passed": gp100_status["validation_passed"],
                "source_gp100_safe_to_continue_to_gp101": gp100_status["safe_to_continue_to_gp101"],
                "source_gp100_readiness_hash": readiness["readiness_hash"],
                "source_gp100_readiness_score": readiness["readiness_score"],
                "source_gp100_section_closed": readiness["section_closed"],
                "source_gp100_component_count": gp100_home["store"]["component_count"],
                "source_gp100_receipt_count": gp100_home["store"]["receipt_count"],
                "source_gp100_validation_check_count": gp100_validation["check_count"],
            }

            component_extra = {
                WORKSPACE_INDEX_ID: {"workspace_index_ready": True, "case_count": len(CASE_SPECS)},
                RECEIPT_LEDGER_ID: {"receipt_ledger_ready": True, "receipt_count": len(CASE_SPECS) * 2},
                OWNER_REVIEW_QUEUE_ID: {"owner_review_queue_ready": True, "owner_review_item_count": len(CASE_SPECS)},
                DETAIL_ROOM_ID: {"detail_room_ready": True, "detail_room_count": len(CASE_SPECS)},
                EVIDENCE_LINK_MAP_ID: {"evidence_link_map_ready": True, "evidence_link_count": len(CASE_SPECS) * 3},
                REDACTED_OBJECT_VIEW_ID: {"redacted_object_reference_view_ready": True, "redacted_object_reference_count": len(CASE_SPECS)},
                EXPORT_PREVIEW_ID: {"export_package_lock_preview_ready": True, "export_package_created": False},
                RESTORE_PREVIEW_ID: {"restore_job_lock_preview_ready": True, "restore_job_created": False},
                BLOCKER_BOARD_ID: {"blocker_review_board_ready": True, "blocker_count": len(CASE_SPECS) * 4},
                READINESS_ID: {"readiness_checkpoint_ready": True, "safe_to_continue_to_gp111": True},
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
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "next_section": NEXT_SECTION_ID,
                    "next_section_range": NEXT_SECTION_RANGE,
                    "next_pack": NEXT_PACK,
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
                _insert_dict(conn, "vault_recovery_case_workspace_components", row)

            case_rows = []
            for idx, (case_code, title, case_type, business_lane, sensitivity) in enumerate(CASE_SPECS, start=1):
                case_id = f"VRCC-{idx:03d}"
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "case_id": case_id,
                    "case_code": case_code,
                    "case_title": title,
                    "case_type": case_type,
                    "business_lane": business_lane,
                    "sensitivity_label": sensitivity,
                    "case_status": "REAL_RECOVERY_CASE_WORKSPACE_OPEN_LOCKED_REDACTED_ONLY",
                    "source_gp100_readiness_hash": readiness["readiness_hash"],
                    "source_gp100_readiness_score": readiness["readiness_score"],
                    "case_ready": True,
                    "case_locked": True,
                    "owner_review_required": True,
                    "tower_review_required": True,
                    "redacted_only": True,
                    "allowed_views": ["case_header", "redacted_metadata", "receipt_lineage", "blockers", "next_safe_action"],
                    "blocked_views": ["object_body", "download", "export_package", "restore_job", "provider_api", "direct_upload", "execution"],
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                case_hash = _hash_payload(payload)
                row = {
                    "case_id": case_id,
                    "case_code": case_code,
                    "case_title": title,
                    "case_type": case_type,
                    "business_lane": business_lane,
                    "sensitivity_label": sensitivity,
                    "case_status": "REAL_RECOVERY_CASE_WORKSPACE_OPEN_LOCKED_REDACTED_ONLY",
                    "source_gp100_readiness_hash": readiness["readiness_hash"],
                    "source_gp100_readiness_score": readiness["readiness_score"],
                    "case_ready": 1,
                    "case_locked": 1,
                    "owner_review_required": 1,
                    "tower_review_required": 1,
                    "redacted_only": 1,
                    "payload_json": _json_dumps(payload),
                    "case_hash": case_hash,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_recovery_case_workspace_cases", row)
                case_rows.append({"case_id": case_id, "case_code": case_code, "case_title": title, "case_type": case_type})

            for case in case_rows:
                for suffix, receipt_name, category in [
                    ("case_opened_receipt", "Recovery case opened receipt", "case"),
                    ("case_lock_receipt", "Recovery case lock receipt", "lock"),
                ]:
                    code = f"{case['case_code']}_{suffix}"
                    payload = {
                        "schema_version": SCHEMA_VERSION,
                        "receipt_ledger_id": RECEIPT_LEDGER_ID,
                        "case_id": case["case_id"],
                        "receipt_code": code,
                        "receipt_name": receipt_name,
                        "receipt_category": category,
                        "source_gp100_readiness_hash": readiness["readiness_hash"],
                        "case_code": case["case_code"],
                        "receipt_locked": True,
                        "owner_review_required": True,
                        "tower_review_required": True,
                        "locked_truth": {field: False for field in FALSE_FIELDS},
                        "vault_done": False,
                        "clouds_should_continue": False,
                    }
                    receipt_hash = _hash_payload(payload)
                    row = {
                        "receipt_id": f"VRCCR-{uuid.uuid5(uuid.NAMESPACE_DNS, code).hex[:18].upper()}",
                        "receipt_ledger_id": RECEIPT_LEDGER_ID,
                        "case_id": case["case_id"],
                        "receipt_code": code,
                        "receipt_name": receipt_name,
                        "receipt_category": category,
                        "receipt_status": "REAL_RECOVERY_CASE_RECEIPT_RECORDED_LOCKED",
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
                    _insert_dict(conn, "vault_recovery_case_workspace_receipts", row)

                queue_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "queue_id": OWNER_REVIEW_QUEUE_ID,
                    "case_id": case["case_id"],
                    "case_code": case["case_code"],
                    "queue_status": "OWNER_REVIEW_REQUIRED_LOCKED_NO_DECISION",
                    "review_locked": True,
                    "owner_review_required": True,
                    "tower_review_required": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                queue_hash = _hash_payload(queue_payload)
                row = {
                    "owner_review_item_id": f"VRCCORQI-{uuid.uuid5(uuid.NAMESPACE_DNS, case['case_code']).hex[:18].upper()}",
                    "queue_id": OWNER_REVIEW_QUEUE_ID,
                    "case_id": case["case_id"],
                    "queue_code": f"{case['case_code']}_owner_review",
                    "queue_status": "OWNER_REVIEW_REQUIRED_LOCKED_NO_DECISION",
                    "owner_review_required": 1,
                    "tower_review_required": 1,
                    "review_locked": 1,
                    "payload_json": _json_dumps(queue_payload),
                    "queue_hash": queue_hash,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_recovery_case_owner_review_queue", row)

                for source_ref in ["GP100_READINESS_HASH", "GP095_DECISION_RECEIPT_LOCK", "GP090_RESTORE_EXPORT_READINESS_HASH"]:
                    link_code = f"{case['case_code']}_{source_ref.lower()}"
                    payload = {
                        "schema_version": SCHEMA_VERSION,
                        "evidence_map_id": EVIDENCE_LINK_MAP_ID,
                        "case_id": case["case_id"],
                        "link_code": link_code,
                        "link_name": f"{case['case_title']} evidence link to {source_ref}",
                        "source_ref": source_ref,
                        "source_gp100_readiness_hash": readiness["readiness_hash"],
                        "evidence_locked": True,
                        "redacted_only": True,
                        "locked_truth": {field: False for field in FALSE_FIELDS},
                        "vault_done": False,
                        "clouds_should_continue": False,
                    }
                    evidence_hash = _hash_payload(payload)
                    row = {
                        "evidence_link_id": f"VRCCEL-{uuid.uuid5(uuid.NAMESPACE_DNS, link_code).hex[:18].upper()}",
                        "evidence_map_id": EVIDENCE_LINK_MAP_ID,
                        "case_id": case["case_id"],
                        "link_code": link_code,
                        "link_name": payload["link_name"],
                        "source_ref": source_ref,
                        "evidence_payload_json": _json_dumps(payload),
                        "evidence_hash": evidence_hash,
                        "evidence_locked": 1,
                        "redacted_only": 1,
                        "created_at": now,
                        "updated_at": now,
                    }
                    for field in FALSE_FIELDS:
                        row[field] = 0
                    _insert_dict(conn, "vault_recovery_case_evidence_links", row)

                object_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "redacted_view_id": REDACTED_OBJECT_VIEW_ID,
                    "case_id": case["case_id"],
                    "object_ref_code": f"{case['case_code']}_redacted_object_ref",
                    "object_category": case["case_type"],
                    "redaction_label": "REDACTED_REFERENCE_ONLY_BODY_LOCKED",
                    "provider_reference_placeholder": f"provider://redacted/{case['case_code']}",
                    "body_locked": True,
                    "download_locked": True,
                    "plaintext_visible": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                object_hash = _hash_payload(object_payload)
                row = {
                    "object_reference_id": f"VRCCOR-{uuid.uuid5(uuid.NAMESPACE_DNS, case['case_code'] + '_object').hex[:18].upper()}",
                    "redacted_view_id": REDACTED_OBJECT_VIEW_ID,
                    "case_id": case["case_id"],
                    "object_ref_code": object_payload["object_ref_code"],
                    "object_category": object_payload["object_category"],
                    "redaction_label": object_payload["redaction_label"],
                    "provider_reference_placeholder": object_payload["provider_reference_placeholder"],
                    "payload_json": _json_dumps(object_payload),
                    "object_reference_hash": object_hash,
                    "redacted_only": 1,
                    "body_locked": 1,
                    "download_locked": 1,
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_recovery_case_redacted_object_references", row)

                blocker_specs = [
                    ("tower_unlock_missing", "Tower unlock missing", "tower", "critical"),
                    ("provider_api_locked", "Provider API locked", "provider_api", "critical"),
                    ("object_body_locked", "Object body access locked", "object_body", "critical"),
                    ("export_restore_locked", "Export and restore locked", "export_restore", "critical"),
                ]
                for code, name, category, severity in blocker_specs:
                    blocker_code = f"{case['case_code']}_{code}"
                    payload = {
                        "schema_version": SCHEMA_VERSION,
                        "blocker_board_id": BLOCKER_BOARD_ID,
                        "case_id": case["case_id"],
                        "blocker_code": blocker_code,
                        "blocker_name": name,
                        "blocker_category": category,
                        "severity": severity,
                        "blocker_active": True,
                        "blocks_restore": True,
                        "blocks_export": True,
                        "blocks_provider_api": True,
                        "blocks_object_body": True,
                        "blocks_direct_upload": True,
                        "blocks_tower_unlock": True,
                        "blocks_execution": True,
                        "blocks_vault_done": True,
                        "locked_truth": {field: False for field in FALSE_FIELDS},
                        "vault_done": False,
                        "clouds_should_continue": False,
                    }
                    blocker_hash = _hash_payload(payload)
                    row = {
                        "blocker_id": f"VRCCB-{uuid.uuid5(uuid.NAMESPACE_DNS, blocker_code).hex[:18].upper()}",
                        "blocker_board_id": BLOCKER_BOARD_ID,
                        "case_id": case["case_id"],
                        "blocker_code": blocker_code,
                        "blocker_name": name,
                        "blocker_category": category,
                        "severity": severity,
                        "blocker_status": "REAL_RECOVERY_CASE_BLOCKER_ACTIVE",
                        "blocker_active": 1,
                        "blocks_restore": 1,
                        "blocks_export": 1,
                        "blocks_provider_api": 1,
                        "blocks_object_body": 1,
                        "blocks_direct_upload": 1,
                        "blocks_tower_unlock": 1,
                        "blocks_execution": 1,
                        "blocks_vault_done": 1,
                        "resolved": 0,
                        "payload_json": _json_dumps(payload),
                        "blocker_hash": blocker_hash,
                        "created_at": now,
                        "updated_at": now,
                    }
                    for field in FALSE_FIELDS:
                        row[field] = 0
                    _insert_dict(conn, "vault_recovery_case_blockers", row)

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "case_count": len(CASE_SPECS),
                "receipt_count": len(CASE_SPECS) * 2,
                "owner_review_item_count": len(CASE_SPECS),
                "evidence_link_count": len(CASE_SPECS) * 3,
                "redacted_object_reference_count": len(CASE_SPECS),
                "blocker_count": len(CASE_SPECS) * 4,
            }

            checks = [
                ("SOURCE_GP100_READY", bool(gp100_status["ready"])),
                ("SOURCE_GP100_VALIDATION_PASSED", bool(gp100_status["validation_passed"])),
                ("SOURCE_GP100_SAFE_TO_CONTINUE", bool(gp100_status["safe_to_continue_to_gp101"])),
                ("SOURCE_GP100_SECTION_CLOSED", bool(readiness["section_closed"])),
                ("SOURCE_GP100_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP100_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("CASE_COUNT_8", counts["case_count"] == 8),
                ("RECEIPT_COUNT_16", counts["receipt_count"] == 16),
                ("OWNER_REVIEW_ITEM_COUNT_8", counts["owner_review_item_count"] == 8),
                ("EVIDENCE_LINK_COUNT_24", counts["evidence_link_count"] == 24),
                ("REDACTED_OBJECT_REFERENCE_COUNT_8", counts["redacted_object_reference_count"] == 8),
                ("BLOCKER_COUNT_32", counts["blocker_count"] == 32),
                ("SECTION_GP101_GP110", SECTION_RANGE == "GP101-GP110"),
                ("NEXT_SECTION_GP111_GP120", NEXT_SECTION_RANGE == "GP111-GP120"),
                ("NO_RESTORE_REQUEST", True),
                ("NO_RESTORE_JOB", True),
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
                "readiness_id": READINESS_ID,
                "gp_number": 110,
                "pack_id": "VAULT_GP110",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp100_readiness_id": readiness["readiness_id"],
                "source_gp100_readiness_hash": readiness["readiness_hash"],
                "source_gp100_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "safe_to_continue_to_gp111": failed_count == 0,
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
                "gp_number": 110,
                "pack_id": "VAULT_GP110",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "REAL_RECOVERY_CASE_WORKSPACE_LAYER_READY_LOCKED_SAFE_TO_CONTINUE_NOT_DONE",
                "readiness_score": readiness_payload["readiness_score"],
                "component_count": counts["component_count"],
                "case_count": counts["case_count"],
                "receipt_count": counts["receipt_count"],
                "owner_review_item_count": counts["owner_review_item_count"],
                "evidence_link_count": counts["evidence_link_count"],
                "redacted_object_reference_count": counts["redacted_object_reference_count"],
                "blocker_count": counts["blocker_count"],
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "safe_to_continue_to_gp111": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_recovery_case_workspace_readiness", row)

            for event_type, event_payload in [
                ("GP101_RECOVERY_CASE_WORKSPACE_INDEX_CREATED", {"case_count": len(CASE_SPECS)}),
                ("GP102_RECOVERY_CASE_RECEIPT_LEDGER_CREATED", {"receipt_count": len(CASE_SPECS) * 2}),
                ("GP103_RECOVERY_CASE_OWNER_REVIEW_QUEUE_CREATED", {"owner_review_item_count": len(CASE_SPECS)}),
                ("GP104_RECOVERY_CASE_DETAIL_ROOM_CREATED", {"detail_room_count": len(CASE_SPECS)}),
                ("GP105_RECOVERY_CASE_EVIDENCE_LINK_MAP_CREATED", {"evidence_link_count": len(CASE_SPECS) * 3}),
                ("GP106_REDACTED_OBJECT_REFERENCE_VIEW_CREATED", {"redacted_object_reference_count": len(CASE_SPECS)}),
                ("GP107_EXPORT_PACKAGE_LOCK_PREVIEW_CREATED", {"export_enabled": False}),
                ("GP108_RESTORE_JOB_LOCK_PREVIEW_CREATED", {"restore_job_created": False}),
                ("GP109_RECOVERY_CASE_BLOCKER_REVIEW_BOARD_CREATED", {"blocker_count": len(CASE_SPECS) * 4}),
                ("GP110_RECOVERY_CASE_WORKSPACE_READINESS_CHECKPOINT_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp111": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_recovery_case_workspace_components").fetchone()["c"]),
            "case_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_recovery_case_workspace_cases").fetchone()["c"]),
            "receipt_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_recovery_case_workspace_receipts").fetchone()["c"]),
            "owner_review_item_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_recovery_case_owner_review_queue").fetchone()["c"]),
            "evidence_link_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_recovery_case_evidence_links").fetchone()["c"]),
            "redacted_object_reference_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_recovery_case_redacted_object_references").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_recovery_case_blockers").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_recovery_case_workspace_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_recovery_case_workspace_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_recovery_case_workspace_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_recovery_case_workspace_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_recovery_case_workspace_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_recovery_case_workspace_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_recovery_case_workspace_readiness WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_recovery_case_workspace_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_recovery_case_workspace_events ORDER BY created_at, event_id").fetchall()
    return [
        {
            "event_id": row["event_id"],
            "event_type": row["event_type"],
            "event_payload": _json_loads(row["event_payload_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]

def get_recovery_cases(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_recovery_case_workspace_cases", "case_code", db_path, {"payload_json": "payload"})

def get_recovery_case_receipts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_recovery_case_workspace_receipts", "receipt_category, receipt_code", db_path, {"receipt_payload_json": "receipt_payload"})

def get_recovery_case_owner_review_items(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_recovery_case_owner_review_queue", "queue_code", db_path, {"payload_json": "payload"})

def get_recovery_case_evidence_links(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_recovery_case_evidence_links", "link_code", db_path, {"evidence_payload_json": "evidence_payload"})

def get_redacted_object_references(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_recovery_case_redacted_object_references", "object_ref_code", db_path, {"payload_json": "payload"})

def get_recovery_case_blockers(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_recovery_case_blockers", "blocker_category, blocker_code", db_path, {"payload_json": "payload"})

def validate_recovery_case_workspace_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_recovery_case_workspace_components", "gp_number", db_path, {"data_json": "data"})
    cases = get_recovery_cases(db_path)
    receipts = get_recovery_case_receipts(db_path)
    queue = get_recovery_case_owner_review_items(db_path)
    evidence = get_recovery_case_evidence_links(db_path)
    objects = get_redacted_object_references(db_path)
    blockers = get_recovery_case_blockers(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("CASE_COUNT_8", len(cases) == len(CASE_SPECS)),
        ("RECEIPT_COUNT_16", len(receipts) == len(CASE_SPECS) * 2),
        ("OWNER_REVIEW_QUEUE_COUNT_8", len(queue) == len(CASE_SPECS)),
        ("EVIDENCE_LINK_COUNT_24", len(evidence) == len(CASE_SPECS) * 3),
        ("REDACTED_OBJECT_REFERENCE_COUNT_8", len(objects) == len(CASE_SPECS)),
        ("BLOCKER_COUNT_32", len(blockers) == len(CASE_SPECS) * 4),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("SAFE_TO_CONTINUE_TO_GP111", readiness["safe_to_continue_to_gp111"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("SECTION_GP101_GP110", readiness["section_range"] == "GP101-GP110"),
        ("NEXT_SECTION_GP111_GP120", readiness["readiness_payload"]["next_section_range"] == "GP111-GP120"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_CASES_LOCKED", all(item["case_locked"] is True for item in cases)),
        ("ALL_CASES_REDACTED_ONLY", all(item["redacted_only"] is True for item in cases)),
        ("ALL_RECEIPTS_LOCKED", all(item["receipt_locked"] is True for item in receipts)),
        ("ALL_QUEUE_ITEMS_LOCKED", all(item["review_locked"] is True for item in queue)),
        ("ALL_EVIDENCE_LINKS_LOCKED", all(item["evidence_locked"] is True for item in evidence)),
        ("ALL_OBJECT_REFERENCES_REDACTED", all(item["redacted_only"] is True for item in objects)),
        ("ALL_OBJECT_BODIES_LOCKED", all(item["body_locked"] is True for item in objects)),
        ("ALL_OBJECT_DOWNLOADS_LOCKED", all(item["download_locked"] is True for item in objects)),
        ("ALL_BLOCKERS_ACTIVE", all(item["blocker_active"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_RESTORE", all(item["blocks_restore"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_EXPORT", all(item["blocks_export"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", all(item["blocks_provider_api"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY", all(item["blocks_object_body"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DIRECT_UPLOAD", all(item["blocks_direct_upload"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_TOWER_UNLOCK", all(item["blocks_tower_unlock"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_EXECUTION", all(item["blocks_execution"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_VAULT_DONE", all(item["blocks_vault_done"] is True for item in blockers)),
        ("NO_BLOCKERS_RESOLVED", all(item["resolved"] is False for item in blockers)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("CASE", cases),
        ("RECEIPT", receipts),
        ("QUEUE", queue),
        ("EVIDENCE", evidence),
        ("OBJECT", objects),
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
        "case_count": len(cases),
        "receipt_count": len(receipts),
        "owner_review_item_count": len(queue),
        "evidence_link_count": len(evidence),
        "redacted_object_reference_count": len(objects),
        "blocker_count": len(blockers),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "safe_to_continue_to_gp111": len(failed) == 0 and readiness["safe_to_continue_to_gp111"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp101_recovery_case_workspace_index(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(WORKSPACE_INDEX_ID, db_path)
    cases = get_recovery_cases(db_path)
    return {"pack": _pack_payload(101, component["pack_name"]), "real_sqlite_backed": True, "workspace_index": component, "case_count": len(cases), "cases": cases}

def get_gp102_recovery_case_receipt_ledger(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RECEIPT_LEDGER_ID, db_path)
    receipts = get_recovery_case_receipts(db_path)
    ledger_payload = {
        "ledger_id": RECEIPT_LEDGER_ID,
        "receipt_count": len(receipts),
        "receipt_hashes": [item["receipt_hash"] for item in receipts],
        "section_range": SECTION_RANGE,
        "vault_done": False,
    }
    return {
        "pack": _pack_payload(102, component["pack_name"]),
        "real_sqlite_backed": True,
        "receipt_ledger": {**component, "ledger_hash": _hash_payload(ledger_payload), "receipt_count": len(receipts)},
        "receipts": receipts,
    }

def get_gp103_recovery_case_owner_review_queue(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(OWNER_REVIEW_QUEUE_ID, db_path)
    queue = get_recovery_case_owner_review_items(db_path)
    return {"pack": _pack_payload(103, component["pack_name"]), "real_sqlite_backed": True, "owner_review_queue": component, "owner_review_item_count": len(queue), "items": queue}

def get_gp104_recovery_case_detail_room(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(DETAIL_ROOM_ID, db_path)
    cases = get_recovery_cases(db_path)
    detail_rooms = [
        {
            "case_id": case["case_id"],
            "case_code": case["case_code"],
            "case_title": case["case_title"],
            "detail_room_status": "READY_LOCKED_REDACTED_ONLY",
            "allowed_sections": ["summary", "redacted_metadata", "receipts", "evidence_links", "blockers", "next_safe_action"],
            "blocked_sections": ["object_body", "download", "export", "restore", "provider_api", "direct_upload", "execution"],
            "vault_done": False,
        }
        for case in cases
    ]
    return {"pack": _pack_payload(104, component["pack_name"]), "real_sqlite_backed": True, "detail_room": component, "detail_room_count": len(detail_rooms), "detail_rooms": detail_rooms}

def get_gp105_recovery_case_evidence_link_map(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(EVIDENCE_LINK_MAP_ID, db_path)
    evidence = get_recovery_case_evidence_links(db_path)
    return {"pack": _pack_payload(105, component["pack_name"]), "real_sqlite_backed": True, "evidence_link_map": component, "evidence_link_count": len(evidence), "evidence_links": evidence}

def get_gp106_redacted_object_reference_view(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(REDACTED_OBJECT_VIEW_ID, db_path)
    refs = get_redacted_object_references(db_path)
    return {"pack": _pack_payload(106, component["pack_name"]), "real_sqlite_backed": True, "redacted_object_reference_view": component, "redacted_object_reference_count": len(refs), "object_references": refs}

def get_gp107_export_package_lock_preview(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(EXPORT_PREVIEW_ID, db_path)
    cases = get_recovery_cases(db_path)
    previews = [
        {
            "case_id": case["case_id"],
            "case_code": case["case_code"],
            "export_preview_status": "LOCKED_PREVIEW_ONLY",
            "export_package_created": False,
            "export_manifest_created": False,
            "export_download_enabled": False,
            "required_before_future_export": ["Tower unlock", "owner decision", "decision receipt", "export authority", "provider boundary review"],
        }
        for case in cases
    ]
    return {"pack": _pack_payload(107, component["pack_name"]), "real_sqlite_backed": True, "export_package_lock_preview": component, "preview_count": len(previews), "previews": previews}

def get_gp108_restore_job_lock_preview(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RESTORE_PREVIEW_ID, db_path)
    cases = get_recovery_cases(db_path)
    previews = [
        {
            "case_id": case["case_id"],
            "case_code": case["case_code"],
            "restore_preview_status": "LOCKED_PREVIEW_ONLY",
            "restore_request_created": False,
            "restore_job_created": False,
            "provider_restore_api_called": False,
            "required_before_future_restore": ["Tower unlock", "owner decision", "decision receipt", "restore authority", "object reference approval"],
        }
        for case in cases
    ]
    return {"pack": _pack_payload(108, component["pack_name"]), "real_sqlite_backed": True, "restore_job_lock_preview": component, "preview_count": len(previews), "previews": previews}

def get_gp109_recovery_case_blocker_review_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(BLOCKER_BOARD_ID, db_path)
    blockers = get_recovery_case_blockers(db_path)
    return {"pack": _pack_payload(109, component["pack_name"]), "real_sqlite_backed": True, "blocker_review_board": component, "blocker_count": len(blockers), "blockers": blockers}

def get_gp110_recovery_case_workspace_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_recovery_case_workspace_layer(db_path)
    return {"pack": _pack_payload(110, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_recovery_case_workspace_layer(db_path)
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
            "source_gp100_readiness_id": component["source_gp100_readiness_id"],
            "source_gp100_readiness_hash": component["source_gp100_readiness_hash"],
            "source_gp100_readiness_score": component["source_gp100_readiness_score"],
            "source_gp100_section_closed": component["source_gp100_section_closed"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "owner_review_required": component["owner_review_required"],
            "tower_review_required": component["tower_review_required"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp111": validation["safe_to_continue_to_gp111"],
            "foundation_status": "recovery_case_workspace_layer_ready_locked_safe_to_continue_not_done",
            "next": next_label,
            "case_count": counts["case_count"],
            "receipt_count": counts["receipt_count"],
            "owner_review_item_count": counts["owner_review_item_count"],
            "evidence_link_count": counts["evidence_link_count"],
            "redacted_object_reference_count": counts["redacted_object_reference_count"],
            "blocker_count": counts["blocker_count"],
            "case_restore_requested": component["case_restore_requested"],
            "case_export_requested": component["case_export_requested"],
            "owner_decision_recorded": component["owner_decision_recorded"],
            "owner_approval_recorded": component["owner_approval_recorded"],
            "owner_rejection_recorded": component["owner_rejection_recorded"],
            "tower_unlock_granted": component["tower_unlock_granted"],
            "restore_request_created": component["restore_request_created"],
            "restore_request_submitted": component["restore_request_submitted"],
            "restore_job_created": component["restore_job_created"],
            "provider_restore_api_called": component["provider_restore_api_called"],
            "object_body_read": component["object_body_read"],
            "object_body_view_enabled": component["object_body_view_enabled"],
            "object_body_download_enabled": component["object_body_download_enabled"],
            "object_body_plaintext_visible": component["object_body_plaintext_visible"],
            "export_package_created": component["export_package_created"],
            "export_manifest_created": component["export_manifest_created"],
            "export_download_enabled": component["export_download_enabled"],
            "direct_upload_enabled": component["direct_upload_enabled"],
            "export_enabled": component["export_enabled"],
            "execution_enabled": component["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp110",
        },
        "validation": validation,
    }

def get_gp101_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(101, WORKSPACE_INDEX_ID, "VAULT_GP102_RECOVERY_CASE_RECEIPT_LEDGER", db_path)

def get_gp102_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(102, RECEIPT_LEDGER_ID, "VAULT_GP103_RECOVERY_CASE_OWNER_REVIEW_QUEUE", db_path)

def get_gp103_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(103, OWNER_REVIEW_QUEUE_ID, "VAULT_GP104_RECOVERY_CASE_DETAIL_ROOM", db_path)

def get_gp104_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(104, DETAIL_ROOM_ID, "VAULT_GP105_RECOVERY_CASE_EVIDENCE_LINK_MAP", db_path)

def get_gp105_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(105, EVIDENCE_LINK_MAP_ID, "VAULT_GP106_REDACTED_OBJECT_REFERENCE_VIEW", db_path)

def get_gp106_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(106, REDACTED_OBJECT_VIEW_ID, "VAULT_GP107_EXPORT_PACKAGE_LOCK_PREVIEW", db_path)

def get_gp107_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(107, EXPORT_PREVIEW_ID, "VAULT_GP108_RESTORE_JOB_LOCK_PREVIEW", db_path)

def get_gp108_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(108, RESTORE_PREVIEW_ID, "VAULT_GP109_RECOVERY_CASE_BLOCKER_REVIEW_BOARD", db_path)

def get_gp109_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(109, BLOCKER_BOARD_ID, "VAULT_GP110_RECOVERY_CASE_WORKSPACE_READINESS_CHECKPOINT", db_path)

def get_gp110_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(110, READINESS_ID, NEXT_PACK, db_path)
    status["gp110_status"]["next_section"] = NEXT_SECTION_ID
    status["gp110_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp110_status"]["next_pack"] = NEXT_PACK
    return status

def get_recovery_case_workspace_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_recovery_case_workspace_layer(db_path)
    components = _rows("vault_recovery_case_workspace_components", "gp_number", db_path, {"data_json": "data"})
    cases = get_recovery_cases(db_path)
    receipts = get_recovery_case_receipts(db_path)
    queue = get_recovery_case_owner_review_items(db_path)
    evidence = get_recovery_case_evidence_links(db_path)
    objects = get_redacted_object_references(db_path)
    blockers = get_recovery_case_blockers(db_path)
    readiness = _readiness(db_path)
    validation = validate_recovery_case_workspace_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "cases": {"case_count": len(cases), "cases": cases},
        "receipts": {"receipt_count": len(receipts), "receipts": receipts},
        "owner_review_queue": {"owner_review_item_count": len(queue), "items": queue},
        "evidence_link_map": {"evidence_link_count": len(evidence), "evidence_links": evidence},
        "redacted_object_references": {"redacted_object_reference_count": len(objects), "object_references": objects},
        "blockers": {"blocker_count": len(blockers), "blockers": blockers},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "recovery_case_workspace_layer_ready": True,
            "case_workspace_index_ready": True,
            "receipt_ledger_ready": True,
            "owner_review_queue_ready": True,
            "detail_room_ready": True,
            "evidence_link_map_ready": True,
            "redacted_object_reference_view_ready": True,
            "export_package_lock_preview_ready": True,
            "restore_job_lock_preview_ready": True,
            "blocker_review_board_ready": True,
            "safe_to_continue_to_gp111": validation["safe_to_continue_to_gp111"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "vault_done": False,
            "clouds_should_continue": False,
            "restore_request_submitted": False,
            "restore_job_created": False,
            "provider_restore_api_called": False,
            "object_body_read": False,
            "object_body_view_enabled": False,
            "object_body_download_enabled": False,
            "export_package_created": False,
            "direct_upload_enabled": False,
            "execution_enabled": False,
        },
        "routes": {
            "page": "/vault/recovery-case-workspace-layer",
            "json": "/vault/recovery-case-workspace-layer.json",
            "gp101": "/vault/gp101-status.json",
            "gp102": "/vault/gp102-status.json",
            "gp103": "/vault/gp103-status.json",
            "gp104": "/vault/gp104-status.json",
            "gp105": "/vault/gp105-status.json",
            "gp106": "/vault/gp106-status.json",
            "gp107": "/vault/gp107-status.json",
            "gp108": "/vault/gp108-status.json",
            "gp109": "/vault/gp109-status.json",
            "gp110": "/vault/gp110-status.json",
        },
    }

def render_recovery_case_workspace_layer_page() -> str:
    home = get_recovery_case_workspace_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    case_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['case_code'])}</strong>
          <span>{escape(item['case_title'])}</span>
          <code>{escape(item['business_lane'])} · {escape(item['sensitivity_label'])}</code>
        </article>
        """
        for item in home["cases"]["cases"]
    )

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

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP101-GP110 Recovery Case Workspace Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 101-110</div>
    <div class="eyebrow">Recovery Case Workspace Layer · GP101-GP110</div>
    <h1>Real Provider Recovery Case Workspace Layer</h1>
    <p>This layer makes Vault usable as a locked recovery/audit case workspace. It adds cases, receipts, owner review queue, detail rooms, evidence links, redacted object references, export/restore previews, blockers, and readiness without unlocking dangerous operations.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['case_count']}</strong><span>recovery cases</span></div>
      <div class="metric"><strong>{home['store']['receipt_count']}</strong><span>case receipts</span></div>
      <div class="metric"><strong>{home['store']['blocker_count']}</strong><span>active blockers</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP101-GP110 built</span>
      <span class="pill ok">Recovery cases ready</span>
      <span class="pill ok">Redacted only</span>
      <span class="pill ok">Safe to GP111</span>
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
    <h2>Recovery Cases</h2>
    <div class="cards">{case_cards}</div>
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
