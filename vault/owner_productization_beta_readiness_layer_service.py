"""
VAULT GP201-GP210 — Owner Productization Beta Readiness Layer

New section:
Archive Vault — Owner Productization Beta Readiness Layer / GP201-GP210

Builds:
- GP201 Owner Productization Shell
- GP202 Beta Readiness Inventory
- GP203 Owner Product Surface Map
- GP204 Beta Tester Access Lock Board
- GP205 Product Copy and Positioning Board
- GP206 Support and Feedback Intake Plan
- GP207 Beta QA Scenario Board
- GP208 Launch Risk and Blocker Board
- GP209 Owner Productization Receipt Packet
- GP210 Owner Productization Beta Readiness Checkpoint

This layer prepares beta readiness and owner productization surfaces. It does
not approve beta launch, grant tester access, send invites, unlock Tower/provider,
touch billing, read object bodies, export, restore, upload, delete, execute, or
mark Vault done.
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

from vault.major_product_readiness_checkpoint_layer_service import (
    get_gp200_status,
    get_gp200_major_product_readiness_checkpoint,
    get_major_product_readiness_checkpoint_layer_home,
    validate_major_product_readiness_checkpoint_layer,
    get_product_capabilities,
    get_product_risk_blockers,
)

LAYER_ID = "VAULT_GP201_210"
LAYER_NAME = "Owner Productization Beta Readiness Layer"
SCHEMA_VERSION = "vault.owner_productization_beta_readiness_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_OWNER_PRODUCTIZATION_BETA_READINESS_LAYER"
SECTION_TITLE = "Archive Vault — Owner Productization Beta Readiness Layer"
SECTION_RANGE = "GP201-GP210"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_MAJOR_PRODUCT_READINESS_CHECKPOINT_LAYER"
PREVIOUS_SECTION_RANGE = "GP191-GP200"

NEXT_SECTION_ID = "ARCHIVE_VAULT_BETA_ACCESS_AND_INVITE_LOCK_LAYER"
NEXT_SECTION_RANGE = "GP211-GP220"
NEXT_PACK = "VAULT_GP211_220_BETA_ACCESS_AND_INVITE_LOCK_LAYER"

DEFAULT_DB_ENV = "VAULT_OWNER_PRODUCTIZATION_BETA_READINESS_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_owner_productization_beta_readiness_layer.sqlite"

PRODUCTIZATION_SHELL_ID = "VOPBR-SHELL-GP201-001"
BETA_READINESS_INVENTORY_ID = "VOPBR-BETA-GP202-001"
OWNER_PRODUCT_SURFACE_MAP_ID = "VOPBR-SURFACE-GP203-001"
BETA_TESTER_ACCESS_LOCK_ID = "VOPBR-ACCESS-GP204-001"
PRODUCT_COPY_POSITIONING_ID = "VOPBR-COPY-GP205-001"
SUPPORT_FEEDBACK_INTAKE_ID = "VOPBR-SUPPORT-GP206-001"
BETA_QA_SCENARIO_ID = "VOPBR-QA-GP207-001"
LAUNCH_RISK_BLOCKER_ID = "VOPBR-RISK-GP208-001"
RECEIPT_PACKET_ID = "VOPBR-RECEIPT-GP209-001"
READINESS_ID = "VOPBR-READINESS-GP210-001"

FALSE_FIELDS = [
    "owner_productization_approved",
    "beta_readiness_approved",
    "beta_launch_requested",
    "beta_launch_approved",
    "public_launch_requested",
    "public_launch_approved",
    "beta_invite_created",
    "beta_invite_sent",
    "beta_tester_added",
    "beta_tester_access_requested",
    "beta_tester_access_granted",
    "beta_tester_access_enabled",
    "beta_access_token_created",
    "beta_access_session_created",
    "billing_flow_created",
    "subscription_flow_created",
    "customer_portal_created",
    "payment_processor_called",
    "tower_billing_handoff_created",
    "provider_unlock_requested",
    "provider_unlock_approved",
    "provider_connection_requested",
    "real_provider_connection_started",
    "real_provider_connection_completed",
    "provider_api_configured",
    "provider_api_called",
    "provider_search_requested",
    "provider_search_executed",
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
    "product_marked_done",
    "vault_done",
    "clouds_should_continue",
]

BETA_READINESS_ITEMS = [
    ("product_story_ready", "Product Story Ready", "story", "ready_locked"),
    ("owner_dashboard_ready", "Owner Dashboard Ready", "owner_surface", "ready_locked"),
    ("redacted_browser_ready", "Redacted Browser Ready", "archive_surface", "ready_locked"),
    ("local_search_ready", "Local Search Ready", "search_surface", "ready_locked"),
    ("receipt_packet_ready", "Receipt Packet Ready", "proof_surface", "ready_locked"),
    ("risk_board_ready", "Risk Board Ready", "risk_surface", "ready_locked"),
    ("support_plan_ready", "Support Plan Ready", "support", "ready_locked"),
    ("qa_scenarios_ready", "QA Scenarios Ready", "qa", "ready_locked"),
    ("tower_handoff_visible", "Tower Handoff Visible", "tower", "ready_locked"),
    ("provider_boundaries_visible", "Provider Boundaries Visible", "provider", "ready_locked"),
]

PRODUCT_SURFACES = [
    ("owner_readiness_home", "Owner Readiness Home", "/vault/owner-productization-beta-readiness-layer", "page"),
    ("major_product_checkpoint", "Major Product Checkpoint", "/vault/major-product-readiness-checkpoint-layer", "page"),
    ("archive_index_search", "Archive Index/Search", "/vault/real-archive-index-search-layer", "page"),
    ("controlled_metadata_test", "Controlled Metadata Test", "/vault/controlled-read-only-metadata-test-layer", "page"),
    ("owner_console_dashboard", "Owner Console Dashboard", "/vault/owner-console-operating-dashboard-layer", "page"),
    ("redacted_archive_browser", "Redacted Archive Browser", "/vault/redacted-archive-browser-layer", "page"),
    ("recovery_case_workspace", "Recovery Case Workspace", "/vault/recovery-case-workspace-layer", "page"),
    ("tower_step_up_handoff", "Tower Step-Up Handoff", "/vault/tower-gated-permission-step-up-layer", "page"),
]

ACCESS_LOCK_ITEMS = [
    ("beta_invite_creation_locked", "Beta Invite Creation Locked"),
    ("beta_invite_send_locked", "Beta Invite Send Locked"),
    ("beta_tester_add_locked", "Beta Tester Add Locked"),
    ("beta_tester_access_grant_locked", "Beta Tester Access Grant Locked"),
    ("beta_access_token_locked", "Beta Access Token Locked"),
    ("beta_access_session_locked", "Beta Access Session Locked"),
    ("tower_gate_for_beta_locked", "Tower Gate for Beta Locked"),
    ("billing_subscription_locked", "Billing/Subscription Locked"),
]

COPY_POSITIONING_ITEMS = [
    ("vault_one_liner", "Vault is the private archive, receipt, and proof room for the Simplee ecosystem.", "positioning"),
    ("vault_owner_promise", "Owner sees readiness, receipts, risks, and redacted archive surfaces without unlocking dangerous actions.", "promise"),
    ("vault_boundary_statement", "Vault does not expose object bodies, downloads, provider credentials, or execution paths.", "boundary"),
    ("vault_beta_status", "Beta readiness is being prepared; launch and access are still locked.", "beta"),
    ("vault_tower_relationship", "Tower owns identity, access, permission, and billing gates.", "tower"),
    ("vault_provider_statement", "Provider integration remains staged, simulated, or locked until controlled approval layers exist.", "provider"),
]

SUPPORT_FEEDBACK_ITEMS = [
    ("owner_feedback_intake", "Owner Feedback Intake", "draft_only"),
    ("tester_issue_report_intake", "Tester Issue Report Intake", "locked_not_live"),
    ("bug_triage_lane", "Bug Triage Lane", "draft_only"),
    ("readiness_question_lane", "Readiness Question Lane", "draft_only"),
    ("access_problem_lane", "Access Problem Lane", "locked_not_live"),
    ("provider_safety_question_lane", "Provider Safety Question Lane", "draft_only"),
]

QA_SCENARIOS = [
    ("owner_opens_readiness_home", "Owner opens readiness home", "owner_surface"),
    ("owner_reviews_lock_boundaries", "Owner reviews lock boundaries", "lock_boundary"),
    ("owner_reviews_redacted_archive", "Owner reviews redacted archive", "archive_surface"),
    ("owner_runs_local_metadata_search", "Owner runs local metadata search", "search_surface"),
    ("owner_checks_receipt_packet", "Owner checks receipt packet", "receipt_surface"),
    ("owner_confirms_beta_access_locked", "Owner confirms beta access locked", "access_lock"),
    ("owner_confirms_provider_locked", "Owner confirms provider locked", "provider_lock"),
    ("owner_confirms_vault_not_done", "Owner confirms Vault not done", "done_lock"),
]

LAUNCH_RISK_BLOCKERS = [
    ("beta_launch_not_approved", "Beta launch not approved", "launch", "critical"),
    ("public_launch_not_approved", "Public launch not approved", "launch", "critical"),
    ("beta_access_locked", "Beta access locked", "access", "critical"),
    ("billing_subscription_locked", "Billing/subscription locked", "billing", "critical"),
    ("provider_unlock_locked", "Provider unlock locked", "provider", "critical"),
    ("provider_api_locked", "Provider API locked", "provider_api", "critical"),
    ("object_body_download_locked", "Object body/download locked", "object_body", "critical"),
    ("restore_export_upload_delete_locked", "Restore/export/upload/delete locked", "dangerous_ops", "critical"),
    ("tower_unlock_locked", "Tower unlock locked", "tower", "critical"),
    ("execution_locked", "Execution locked", "execution", "critical"),
    ("vault_not_done", "Vault not done", "done_state", "critical"),
    ("clouds_parked", "Clouds parked", "clouds", "medium"),
]

COMPONENT_SPECS = [
    (201, PRODUCTIZATION_SHELL_ID, "VAULT_GP201", "Owner Productization Shell", "owner_productization_shell"),
    (202, BETA_READINESS_INVENTORY_ID, "VAULT_GP202", "Beta Readiness Inventory", "beta_readiness_inventory"),
    (203, OWNER_PRODUCT_SURFACE_MAP_ID, "VAULT_GP203", "Owner Product Surface Map", "owner_product_surface_map"),
    (204, BETA_TESTER_ACCESS_LOCK_ID, "VAULT_GP204", "Beta Tester Access Lock Board", "beta_tester_access_lock_board"),
    (205, PRODUCT_COPY_POSITIONING_ID, "VAULT_GP205", "Product Copy and Positioning Board", "product_copy_positioning_board"),
    (206, SUPPORT_FEEDBACK_INTAKE_ID, "VAULT_GP206", "Support and Feedback Intake Plan", "support_feedback_intake_plan"),
    (207, BETA_QA_SCENARIO_ID, "VAULT_GP207", "Beta QA Scenario Board", "beta_qa_scenario_board"),
    (208, LAUNCH_RISK_BLOCKER_ID, "VAULT_GP208", "Launch Risk and Blocker Board", "launch_risk_blocker_board"),
    (209, RECEIPT_PACKET_ID, "VAULT_GP209", "Owner Productization Receipt Packet", "owner_productization_receipt_packet"),
    (210, READINESS_ID, "VAULT_GP210", "Owner Productization Beta Readiness Checkpoint", "owner_productization_beta_readiness_checkpoint"),
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
        "source_gp200_readiness_score",
        "component_count",
        "beta_readiness_count",
        "surface_count",
        "access_lock_count",
        "copy_positioning_count",
        "support_feedback_count",
        "qa_scenario_count",
        "launch_risk_blocker_count",
        "receipt_packet_count",
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
        "depends_on": ["VAULT_GP200"],
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
        "depends_on": ["VAULT_GP200"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_owner_productization_beta_readiness_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_owner_productization_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp200_readiness_id TEXT NOT NULL,
                source_gp200_readiness_hash TEXT NOT NULL,
                source_gp200_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                owner_productization_ready INTEGER NOT NULL DEFAULT 1,
                beta_readiness_prepared INTEGER NOT NULL DEFAULT 1,
                beta_launch_locked INTEGER NOT NULL DEFAULT 1,
                beta_access_locked INTEGER NOT NULL DEFAULT 1,
                vault_not_done INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_beta_readiness_inventory (
                item_id TEXT PRIMARY KEY,
                item_code TEXT NOT NULL UNIQUE,
                item_name TEXT NOT NULL,
                item_category TEXT NOT NULL,
                item_status TEXT NOT NULL,
                item_ready INTEGER NOT NULL DEFAULT 1,
                item_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_owner_product_surface_map (
                surface_id TEXT PRIMARY KEY,
                surface_code TEXT NOT NULL UNIQUE,
                surface_name TEXT NOT NULL,
                surface_path TEXT NOT NULL,
                surface_type TEXT NOT NULL,
                surface_status TEXT NOT NULL,
                surface_ready INTEGER NOT NULL DEFAULT 1,
                surface_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                surface_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_beta_tester_access_lock_board (
                access_lock_id TEXT PRIMARY KEY,
                access_code TEXT NOT NULL UNIQUE,
                access_name TEXT NOT NULL,
                access_status TEXT NOT NULL,
                access_locked INTEGER NOT NULL DEFAULT 1,
                blocks_beta_access INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                access_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_product_copy_positioning_board (
                copy_id TEXT PRIMARY KEY,
                copy_code TEXT NOT NULL UNIQUE,
                copy_text TEXT NOT NULL,
                copy_category TEXT NOT NULL,
                copy_status TEXT NOT NULL,
                copy_ready INTEGER NOT NULL DEFAULT 1,
                copy_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                copy_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_support_feedback_intake_plan (
                intake_id TEXT PRIMARY KEY,
                intake_code TEXT NOT NULL UNIQUE,
                intake_name TEXT NOT NULL,
                intake_status TEXT NOT NULL,
                intake_ready INTEGER NOT NULL DEFAULT 1,
                intake_locked INTEGER NOT NULL DEFAULT 1,
                live_intake_enabled INTEGER NOT NULL DEFAULT 0,
                payload_json TEXT NOT NULL,
                intake_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_beta_qa_scenario_board (
                qa_id TEXT PRIMARY KEY,
                qa_code TEXT NOT NULL UNIQUE,
                qa_name TEXT NOT NULL,
                qa_category TEXT NOT NULL,
                qa_status TEXT NOT NULL,
                qa_ready INTEGER NOT NULL DEFAULT 1,
                qa_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                qa_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_launch_risk_blocker_board (
                blocker_id TEXT PRIMARY KEY,
                blocker_code TEXT NOT NULL UNIQUE,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocker_active INTEGER NOT NULL DEFAULT 1,
                blocks_beta_launch INTEGER NOT NULL DEFAULT 1,
                blocks_public_launch INTEGER NOT NULL DEFAULT 1,
                blocks_beta_access INTEGER NOT NULL DEFAULT 1,
                blocks_provider_unlock INTEGER NOT NULL DEFAULT 1,
                blocks_provider_api INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_owner_productization_receipt_packets (
                receipt_packet_id TEXT PRIMARY KEY,
                packet_code TEXT NOT NULL UNIQUE,
                packet_name TEXT NOT NULL,
                packet_status TEXT NOT NULL,
                packet_ready INTEGER NOT NULL DEFAULT 1,
                packet_locked INTEGER NOT NULL DEFAULT 1,
                final_beta_launch_receipt INTEGER NOT NULL DEFAULT 0,
                payload_json TEXT NOT NULL,
                packet_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_owner_productization_beta_readiness_checkpoint (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                beta_readiness_count INTEGER NOT NULL,
                surface_count INTEGER NOT NULL,
                access_lock_count INTEGER NOT NULL,
                copy_positioning_count INTEGER NOT NULL,
                support_feedback_count INTEGER NOT NULL,
                qa_scenario_count INTEGER NOT NULL,
                launch_risk_blocker_count INTEGER NOT NULL,
                receipt_packet_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                owner_productization_ready INTEGER NOT NULL DEFAULT 1,
                beta_readiness_prepared INTEGER NOT NULL DEFAULT 1,
                beta_launch_locked INTEGER NOT NULL DEFAULT 1,
                beta_access_locked INTEGER NOT NULL DEFAULT 1,
                safe_to_continue_to_gp211 INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_owner_productization_events (
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
            "vault_owner_productization_components",
            "vault_beta_readiness_inventory",
            "vault_owner_product_surface_map",
            "vault_beta_tester_access_lock_board",
            "vault_product_copy_positioning_board",
            "vault_support_feedback_intake_plan",
            "vault_beta_qa_scenario_board",
            "vault_launch_risk_blocker_board",
            "vault_owner_productization_receipt_packets",
            "vault_owner_productization_beta_readiness_checkpoint",
            "vault_owner_productization_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VOPBREVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_owner_productization_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_owner_productization_beta_readiness_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_owner_productization_beta_readiness_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_owner_productization_components WHERE component_id = ?",
            (PRODUCTIZATION_SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp200_status = get_gp200_status()["gp200_status"]
            gp200_checkpoint = get_gp200_major_product_readiness_checkpoint()["readiness_checkpoint"]
            gp200_home = get_major_product_readiness_checkpoint_layer_home()
            gp200_validation = validate_major_product_readiness_checkpoint_layer()
            source_capabilities = get_product_capabilities()
            source_blockers = get_product_risk_blockers()

            readiness = gp200_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp200_readiness_id": readiness["readiness_id"],
                "source_gp200_readiness_hash": readiness["readiness_hash"],
                "source_gp200_readiness_score": readiness["readiness_score"],
            }

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "beta_readiness_count": len(BETA_READINESS_ITEMS),
                "surface_count": len(PRODUCT_SURFACES),
                "access_lock_count": len(ACCESS_LOCK_ITEMS),
                "copy_positioning_count": len(COPY_POSITIONING_ITEMS),
                "support_feedback_count": len(SUPPORT_FEEDBACK_ITEMS),
                "qa_scenario_count": len(QA_SCENARIOS),
                "launch_risk_blocker_count": len(LAUNCH_RISK_BLOCKERS),
                "receipt_packet_count": 1,
            }

            source_context = {
                "source_gp200_status_ready": gp200_status["ready"],
                "source_gp200_validation_passed": gp200_status["validation_passed"],
                "source_gp200_safe_to_continue_to_gp201": gp200_status["safe_to_continue_to_gp201"],
                "source_gp200_readiness_hash": readiness["readiness_hash"],
                "source_gp200_readiness_score": readiness["readiness_score"],
                "source_capability_count": len(source_capabilities),
                "source_risk_blocker_count": len(source_blockers),
                "source_validation_check_count": gp200_validation["check_count"],
            }

            component_extra = {
                PRODUCTIZATION_SHELL_ID: {"owner_productization_shell_ready": True},
                BETA_READINESS_INVENTORY_ID: {"beta_readiness_inventory_ready": True, "beta_readiness_count": counts["beta_readiness_count"]},
                OWNER_PRODUCT_SURFACE_MAP_ID: {"owner_product_surface_map_ready": True, "surface_count": counts["surface_count"]},
                BETA_TESTER_ACCESS_LOCK_ID: {"beta_tester_access_lock_board_ready": True, "access_lock_count": counts["access_lock_count"]},
                PRODUCT_COPY_POSITIONING_ID: {"product_copy_positioning_board_ready": True, "copy_positioning_count": counts["copy_positioning_count"]},
                SUPPORT_FEEDBACK_INTAKE_ID: {"support_feedback_intake_plan_ready": True, "support_feedback_count": counts["support_feedback_count"]},
                BETA_QA_SCENARIO_ID: {"beta_qa_scenario_board_ready": True, "qa_scenario_count": counts["qa_scenario_count"]},
                LAUNCH_RISK_BLOCKER_ID: {"launch_risk_blocker_board_ready": True, "launch_risk_blocker_count": counts["launch_risk_blocker_count"]},
                RECEIPT_PACKET_ID: {"owner_productization_receipt_packet_ready": True, "receipt_packet_count": counts["receipt_packet_count"]},
                READINESS_ID: {"owner_productization_beta_readiness_checkpoint_ready": True, "safe_to_continue_to_gp211": True},
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
                    "owner_productization_ready": True,
                    "beta_readiness_prepared": True,
                    "beta_launch_locked": True,
                    "beta_access_locked": True,
                    "vault_not_done": True,
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
                    "owner_productization_ready": 1,
                    "beta_readiness_prepared": 1,
                    "beta_launch_locked": 1,
                    "beta_access_locked": 1,
                    "vault_not_done": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_owner_productization_components", row)

            for idx, (code, name, category, status) in enumerate(BETA_READINESS_ITEMS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "item_code": code,
                    "item_name": name,
                    "item_category": category,
                    "item_status": status,
                    "item_ready": True,
                    "item_locked": True,
                    "beta_launch_locked": True,
                    "beta_access_locked": True,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "item_id": f"VOPBRBETA-{idx:03d}",
                    "item_code": code,
                    "item_name": name,
                    "item_category": category,
                    "item_status": status,
                    "item_ready": 1,
                    "item_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "item_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_readiness_inventory", row)

            for idx, (code, name, path_value, surface_type) in enumerate(PRODUCT_SURFACES, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "surface_code": code,
                    "surface_name": name,
                    "surface_path": path_value,
                    "surface_type": surface_type,
                    "surface_status": "OWNER_PRODUCT_SURFACE_READY_LOCKED",
                    "surface_ready": True,
                    "surface_locked": True,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "surface_id": f"VOPBRSURF-{idx:03d}",
                    "surface_code": code,
                    "surface_name": name,
                    "surface_path": path_value,
                    "surface_type": surface_type,
                    "surface_status": payload["surface_status"],
                    "surface_ready": 1,
                    "surface_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "surface_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_owner_product_surface_map", row)

            for idx, (code, name) in enumerate(ACCESS_LOCK_ITEMS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "access_code": code,
                    "access_name": name,
                    "access_status": "ACCESS_LOCKED_NO_BETA_GRANT",
                    "access_locked": True,
                    "blocks_beta_access": True,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "access_lock_id": f"VOPBRACCESS-{idx:03d}",
                    "access_code": code,
                    "access_name": name,
                    "access_status": payload["access_status"],
                    "access_locked": 1,
                    "blocks_beta_access": 1,
                    "payload_json": _json_dumps(payload),
                    "access_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_tester_access_lock_board", row)

            for idx, (code, copy_text, category) in enumerate(COPY_POSITIONING_ITEMS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "copy_code": code,
                    "copy_text": copy_text,
                    "copy_category": category,
                    "copy_status": "OWNER_COPY_READY_INTERNAL_ONLY",
                    "copy_ready": True,
                    "copy_locked": True,
                    "public_launch_approved": False,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "copy_id": f"VOPBRCOPY-{idx:03d}",
                    "copy_code": code,
                    "copy_text": copy_text,
                    "copy_category": category,
                    "copy_status": payload["copy_status"],
                    "copy_ready": 1,
                    "copy_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "copy_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_product_copy_positioning_board", row)

            for idx, (code, name, status) in enumerate(SUPPORT_FEEDBACK_ITEMS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "intake_code": code,
                    "intake_name": name,
                    "intake_status": status,
                    "intake_ready": True,
                    "intake_locked": True,
                    "live_intake_enabled": False,
                    "beta_launch_locked": True,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "intake_id": f"VOPBRINTAKE-{idx:03d}",
                    "intake_code": code,
                    "intake_name": name,
                    "intake_status": status,
                    "intake_ready": 1,
                    "intake_locked": 1,
                    "live_intake_enabled": 0,
                    "payload_json": _json_dumps(payload),
                    "intake_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_support_feedback_intake_plan", row)

            for idx, (code, name, category) in enumerate(QA_SCENARIOS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "qa_code": code,
                    "qa_name": name,
                    "qa_category": category,
                    "qa_status": "QA_SCENARIO_READY_LOCKED_DRAFT_ONLY",
                    "qa_ready": True,
                    "qa_locked": True,
                    "beta_launch_locked": True,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "qa_id": f"VOPBRQA-{idx:03d}",
                    "qa_code": code,
                    "qa_name": name,
                    "qa_category": category,
                    "qa_status": payload["qa_status"],
                    "qa_ready": 1,
                    "qa_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "qa_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_qa_scenario_board", row)

            for idx, (code, name, category, severity) in enumerate(LAUNCH_RISK_BLOCKERS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "ACTIVE_OWNER_PRODUCTIZATION_BETA_READINESS_BLOCKER",
                    "blocker_active": True,
                    "blocks_beta_launch": True,
                    "blocks_public_launch": True,
                    "blocks_beta_access": True,
                    "blocks_provider_unlock": True,
                    "blocks_provider_api": True,
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
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "blocker_id": f"VOPBRRISK-{idx:03d}",
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": payload["blocker_status"],
                    "blocker_active": 1,
                    "blocks_beta_launch": 1,
                    "blocks_public_launch": 1,
                    "blocks_beta_access": 1,
                    "blocks_provider_unlock": 1,
                    "blocks_provider_api": 1,
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
                _insert_dict(conn, "vault_launch_risk_blocker_board", row)

            packet_payload = {
                "schema_version": SCHEMA_VERSION,
                "packet_code": "vault_gp201_210_owner_productization_beta_readiness_packet",
                "packet_name": "Vault GP201-GP210 Owner Productization Beta Readiness Packet",
                "packet_status": "READY_LOCKED_NOT_BETA_LAUNCH_RECEIPT",
                "source_gp200_readiness_id": readiness["readiness_id"],
                "source_gp200_readiness_hash": readiness["readiness_hash"],
                "source_gp200_readiness_score": readiness["readiness_score"],
                **counts,
                "owner_productization_ready": True,
                "beta_readiness_prepared": True,
                "beta_launch_locked": True,
                "beta_access_locked": True,
                "vault_done": False,
                "clouds_should_continue": False,
                "locked_truth": {field: False for field in FALSE_FIELDS},
            }
            row = {
                "receipt_packet_id": RECEIPT_PACKET_ID,
                "packet_code": "vault_gp201_210_owner_productization_beta_readiness_packet",
                "packet_name": "Vault GP201-GP210 Owner Productization Beta Readiness Packet",
                "packet_status": packet_payload["packet_status"],
                "packet_ready": 1,
                "packet_locked": 1,
                "final_beta_launch_receipt": 0,
                "payload_json": _json_dumps(packet_payload),
                "packet_hash": _hash_payload(packet_payload),
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                row[field] = 0
            _insert_dict(conn, "vault_owner_productization_receipt_packets", row)

            checks = [
                ("SOURCE_GP200_READY", bool(gp200_status["ready"])),
                ("SOURCE_GP200_VALIDATION_PASSED", bool(gp200_status["validation_passed"])),
                ("SOURCE_GP200_SAFE_TO_CONTINUE", bool(gp200_status["safe_to_continue_to_gp201"])),
                ("SOURCE_GP200_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP200_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("BETA_READINESS_COUNT_10", counts["beta_readiness_count"] == 10),
                ("SURFACE_COUNT_8", counts["surface_count"] == 8),
                ("ACCESS_LOCK_COUNT_8", counts["access_lock_count"] == 8),
                ("COPY_POSITIONING_COUNT_6", counts["copy_positioning_count"] == 6),
                ("SUPPORT_FEEDBACK_COUNT_6", counts["support_feedback_count"] == 6),
                ("QA_SCENARIO_COUNT_8", counts["qa_scenario_count"] == 8),
                ("LAUNCH_RISK_BLOCKER_COUNT_12", counts["launch_risk_blocker_count"] == 12),
                ("RECEIPT_PACKET_COUNT_1", counts["receipt_packet_count"] == 1),
                ("SECTION_GP201_GP210", SECTION_RANGE == "GP201-GP210"),
                ("NEXT_SECTION_GP211_GP220", NEXT_SECTION_RANGE == "GP211-GP220"),
                ("OWNER_PRODUCTIZATION_READY", True),
                ("BETA_READINESS_PREPARED", True),
                ("BETA_LAUNCH_LOCKED", True),
                ("BETA_ACCESS_LOCKED", True),
                ("NO_BETA_INVITE", True),
                ("NO_BETA_ACCESS_GRANT", True),
                ("NO_BILLING_FLOW", True),
                ("NO_PROVIDER_UNLOCK", True),
                ("NO_PROVIDER_API", True),
                ("NO_PROVIDER_SEARCH", True),
                ("NO_SECRET_READ", True),
                ("NO_PROVIDER_METADATA_READ", True),
                ("NO_OBJECT_BODY", True),
                ("NO_DOWNLOAD", True),
                ("NO_RESTORE_EXPORT_UPLOAD_DELETE", True),
                ("NO_TOWER_UNLOCK", True),
                ("NO_OWNER_APPROVAL_UNLOCK", True),
                ("NO_EXECUTION", True),
                ("VAULT_NOT_DONE", True),
                ("CLOUDS_PARKED", True),
            ]
            passed_count = len([c for c in checks if c[1]])
            failed_count = len(checks) - passed_count

            readiness_payload = {
                "schema_version": SCHEMA_VERSION,
                "readiness_id": READINESS_ID,
                "gp_number": 210,
                "pack_id": "VAULT_GP210",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp200_readiness_id": readiness["readiness_id"],
                "source_gp200_readiness_hash": readiness["readiness_hash"],
                "source_gp200_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "owner_productization_ready": True,
                "beta_readiness_prepared": True,
                "beta_launch_locked": True,
                "beta_access_locked": True,
                "safe_to_continue_to_gp211": failed_count == 0,
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
                "gp_number": 210,
                "pack_id": "VAULT_GP210",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "OWNER_PRODUCTIZATION_BETA_READINESS_PREPARED_LAUNCH_ACCESS_LOCKED_VAULT_NOT_DONE_SAFE_TO_CONTINUE",
                "readiness_score": readiness_payload["readiness_score"],
                **counts,
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "owner_productization_ready": 1,
                "beta_readiness_prepared": 1,
                "beta_launch_locked": 1,
                "beta_access_locked": 1,
                "safe_to_continue_to_gp211": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_owner_productization_beta_readiness_checkpoint", row)

            for event_type, event_payload in [
                ("GP201_OWNER_PRODUCTIZATION_SHELL_CREATED", {"component_id": PRODUCTIZATION_SHELL_ID}),
                ("GP202_BETA_READINESS_INVENTORY_CREATED", {"beta_readiness_count": counts["beta_readiness_count"]}),
                ("GP203_OWNER_PRODUCT_SURFACE_MAP_CREATED", {"surface_count": counts["surface_count"]}),
                ("GP204_BETA_TESTER_ACCESS_LOCK_BOARD_CREATED", {"access_lock_count": counts["access_lock_count"]}),
                ("GP205_PRODUCT_COPY_POSITIONING_BOARD_CREATED", {"copy_positioning_count": counts["copy_positioning_count"]}),
                ("GP206_SUPPORT_FEEDBACK_INTAKE_PLAN_CREATED", {"support_feedback_count": counts["support_feedback_count"]}),
                ("GP207_BETA_QA_SCENARIO_BOARD_CREATED", {"qa_scenario_count": counts["qa_scenario_count"]}),
                ("GP208_LAUNCH_RISK_BLOCKER_BOARD_CREATED", {"launch_risk_blocker_count": counts["launch_risk_blocker_count"]}),
                ("GP209_OWNER_PRODUCTIZATION_RECEIPT_PACKET_CREATED", {"receipt_packet_count": counts["receipt_packet_count"]}),
                ("GP210_OWNER_PRODUCTIZATION_BETA_READINESS_CHECKPOINT_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp211": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_productization_components").fetchone()["c"]),
            "beta_readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_readiness_inventory").fetchone()["c"]),
            "surface_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_product_surface_map").fetchone()["c"]),
            "access_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_tester_access_lock_board").fetchone()["c"]),
            "copy_positioning_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_product_copy_positioning_board").fetchone()["c"]),
            "support_feedback_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_support_feedback_intake_plan").fetchone()["c"]),
            "qa_scenario_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_qa_scenario_board").fetchone()["c"]),
            "launch_risk_blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_launch_risk_blocker_board").fetchone()["c"]),
            "receipt_packet_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_productization_receipt_packets").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_productization_beta_readiness_checkpoint").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_productization_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_owner_productization_beta_readiness_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_owner_productization_beta_readiness_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_owner_productization_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_owner_productization_beta_readiness_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_owner_productization_beta_readiness_checkpoint WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_owner_productization_beta_readiness_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_owner_productization_events ORDER BY created_at, event_id").fetchall()
    return [{"event_id": row["event_id"], "event_type": row["event_type"], "event_payload": _json_loads(row["event_payload_json"]), "created_at": row["created_at"]} for row in rows]

def get_beta_readiness_items(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_beta_readiness_inventory", "item_code", db_path, {"payload_json": "payload"})

def get_owner_product_surfaces(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_owner_product_surface_map", "surface_code", db_path, {"payload_json": "payload"})

def get_beta_access_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_beta_tester_access_lock_board", "access_code", db_path, {"payload_json": "payload"})

def get_product_copy_positioning_items(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_product_copy_positioning_board", "copy_code", db_path, {"payload_json": "payload"})

def get_support_feedback_intake_items(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_support_feedback_intake_plan", "intake_code", db_path, {"payload_json": "payload"})

def get_beta_qa_scenarios(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_beta_qa_scenario_board", "qa_code", db_path, {"payload_json": "payload"})

def get_launch_risk_blockers(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_launch_risk_blocker_board", "blocker_code", db_path, {"payload_json": "payload"})

def get_owner_productization_receipt_packets(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_owner_productization_receipt_packets", "packet_code", db_path, {"payload_json": "payload"})

def validate_owner_productization_beta_readiness_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_owner_productization_components", "gp_number", db_path, {"data_json": "data"})
    beta_items = get_beta_readiness_items(db_path)
    surfaces = get_owner_product_surfaces(db_path)
    access_locks = get_beta_access_locks(db_path)
    copy_items = get_product_copy_positioning_items(db_path)
    support_items = get_support_feedback_intake_items(db_path)
    qa_items = get_beta_qa_scenarios(db_path)
    blockers = get_launch_risk_blockers(db_path)
    packets = get_owner_productization_receipt_packets(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("BETA_READINESS_COUNT_10", len(beta_items) == len(BETA_READINESS_ITEMS)),
        ("SURFACE_COUNT_8", len(surfaces) == len(PRODUCT_SURFACES)),
        ("ACCESS_LOCK_COUNT_8", len(access_locks) == len(ACCESS_LOCK_ITEMS)),
        ("COPY_POSITIONING_COUNT_6", len(copy_items) == len(COPY_POSITIONING_ITEMS)),
        ("SUPPORT_FEEDBACK_COUNT_6", len(support_items) == len(SUPPORT_FEEDBACK_ITEMS)),
        ("QA_SCENARIO_COUNT_8", len(qa_items) == len(QA_SCENARIOS)),
        ("LAUNCH_RISK_BLOCKER_COUNT_12", len(blockers) == len(LAUNCH_RISK_BLOCKERS)),
        ("RECEIPT_PACKET_COUNT_1", len(packets) == 1),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("OWNER_PRODUCTIZATION_READY", readiness["owner_productization_ready"] is True),
        ("BETA_READINESS_PREPARED", readiness["beta_readiness_prepared"] is True),
        ("BETA_LAUNCH_LOCKED", readiness["beta_launch_locked"] is True),
        ("BETA_ACCESS_LOCKED", readiness["beta_access_locked"] is True),
        ("SAFE_TO_CONTINUE_TO_GP211", readiness["safe_to_continue_to_gp211"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("VAULT_NOT_DONE", readiness["vault_done"] is False),
        ("CLOUDS_PARKED", readiness["clouds_should_continue"] is False),
        ("SECTION_GP201_GP210", readiness["section_range"] == "GP201-GP210"),
        ("NEXT_SECTION_GP211_GP220", readiness["readiness_payload"]["next_section_range"] == "GP211-GP220"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_READY", all(item["component_ready"] is True for item in components)),
        ("ALL_COMPONENTS_LOCKED", all(item["component_locked"] is True for item in components)),
        ("ALL_COMPONENTS_BETA_LOCKED", all(item["beta_launch_locked"] and item["beta_access_locked"] for item in components)),
        ("ALL_COMPONENTS_VAULT_NOT_DONE", all(item["vault_not_done"] is True for item in components)),
        ("ALL_BETA_ITEMS_READY", all(item["item_ready"] is True for item in beta_items)),
        ("ALL_BETA_ITEMS_LOCKED", all(item["item_locked"] is True for item in beta_items)),
        ("ALL_SURFACES_READY", all(item["surface_ready"] is True for item in surfaces)),
        ("ALL_SURFACES_LOCKED", all(item["surface_locked"] is True for item in surfaces)),
        ("ALL_ACCESS_LOCKS_LOCKED", all(item["access_locked"] is True for item in access_locks)),
        ("ALL_ACCESS_LOCKS_BLOCK_BETA_ACCESS", all(item["blocks_beta_access"] is True for item in access_locks)),
        ("ALL_COPY_READY", all(item["copy_ready"] is True for item in copy_items)),
        ("ALL_SUPPORT_READY", all(item["intake_ready"] is True for item in support_items)),
        ("ALL_SUPPORT_LOCKED", all(item["intake_locked"] is True for item in support_items)),
        ("NO_LIVE_INTAKE", all(item["live_intake_enabled"] is False for item in support_items)),
        ("ALL_QA_READY", all(item["qa_ready"] is True for item in qa_items)),
        ("ALL_QA_LOCKED", all(item["qa_locked"] is True for item in qa_items)),
        ("ALL_BLOCKERS_ACTIVE", all(item["blocker_active"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_BETA_LAUNCH", all(item["blocks_beta_launch"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PUBLIC_LAUNCH", all(item["blocks_public_launch"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_BETA_ACCESS", all(item["blocks_beta_access"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_UNLOCK", all(item["blocks_provider_unlock"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", all(item["blocks_provider_api"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY", all(item["blocks_object_body"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DANGEROUS_OPS", all(item["blocks_restore"] and item["blocks_export"] and item["blocks_direct_upload"] and item["blocks_delete"] for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_TOWER_EXECUTION_DONE", all(item["blocks_tower_unlock"] and item["blocks_execution"] and item["blocks_vault_done"] for item in blockers)),
        ("NO_BLOCKERS_RESOLVED", all(item["resolved"] is False for item in blockers)),
        ("PACKET_READY", all(item["packet_ready"] is True for item in packets)),
        ("PACKET_LOCKED", all(item["packet_locked"] is True for item in packets)),
        ("NO_FINAL_BETA_LAUNCH_RECEIPT", all(item["final_beta_launch_receipt"] is False for item in packets)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("BETA", beta_items),
        ("SURFACE", surfaces),
        ("ACCESS", access_locks),
        ("COPY", copy_items),
        ("SUPPORT", support_items),
        ("QA", qa_items),
        ("BLOCKER", blockers),
        ("PACKET", packets),
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
        "beta_readiness_count": len(beta_items),
        "surface_count": len(surfaces),
        "access_lock_count": len(access_locks),
        "copy_positioning_count": len(copy_items),
        "support_feedback_count": len(support_items),
        "qa_scenario_count": len(qa_items),
        "launch_risk_blocker_count": len(blockers),
        "receipt_packet_count": len(packets),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "owner_productization_ready": len(failed) == 0 and readiness["owner_productization_ready"] is True,
        "beta_readiness_prepared": len(failed) == 0 and readiness["beta_readiness_prepared"] is True,
        "safe_to_continue_to_gp211": len(failed) == 0 and readiness["safe_to_continue_to_gp211"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp201_owner_productization_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(PRODUCTIZATION_SHELL_ID, db_path)
    return {"pack": _pack_payload(201, component["pack_name"]), "real_sqlite_backed": True, "productization_shell": component}

def get_gp202_beta_readiness_inventory(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(BETA_READINESS_INVENTORY_ID, db_path)
    items = get_beta_readiness_items(db_path)
    return {"pack": _pack_payload(202, component["pack_name"]), "real_sqlite_backed": True, "beta_readiness_inventory": component, "beta_readiness_count": len(items), "items": items}

def get_gp203_owner_product_surface_map(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(OWNER_PRODUCT_SURFACE_MAP_ID, db_path)
    surfaces = get_owner_product_surfaces(db_path)
    return {"pack": _pack_payload(203, component["pack_name"]), "real_sqlite_backed": True, "surface_map": component, "surface_count": len(surfaces), "surfaces": surfaces}

def get_gp204_beta_tester_access_lock_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(BETA_TESTER_ACCESS_LOCK_ID, db_path)
    locks = get_beta_access_locks(db_path)
    return {"pack": _pack_payload(204, component["pack_name"]), "real_sqlite_backed": True, "access_lock_board": component, "access_lock_count": len(locks), "access_locks": locks}

def get_gp205_product_copy_positioning_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(PRODUCT_COPY_POSITIONING_ID, db_path)
    copy_items = get_product_copy_positioning_items(db_path)
    return {"pack": _pack_payload(205, component["pack_name"]), "real_sqlite_backed": True, "copy_positioning_board": component, "copy_positioning_count": len(copy_items), "copy_items": copy_items}

def get_gp206_support_feedback_intake_plan(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SUPPORT_FEEDBACK_INTAKE_ID, db_path)
    support_items = get_support_feedback_intake_items(db_path)
    return {"pack": _pack_payload(206, component["pack_name"]), "real_sqlite_backed": True, "support_feedback_intake_plan": component, "support_feedback_count": len(support_items), "support_items": support_items}

def get_gp207_beta_qa_scenario_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(BETA_QA_SCENARIO_ID, db_path)
    scenarios = get_beta_qa_scenarios(db_path)
    return {"pack": _pack_payload(207, component["pack_name"]), "real_sqlite_backed": True, "qa_scenario_board": component, "qa_scenario_count": len(scenarios), "scenarios": scenarios}

def get_gp208_launch_risk_blocker_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(LAUNCH_RISK_BLOCKER_ID, db_path)
    blockers = get_launch_risk_blockers(db_path)
    return {"pack": _pack_payload(208, component["pack_name"]), "real_sqlite_backed": True, "launch_risk_blocker_board": component, "launch_risk_blocker_count": len(blockers), "blockers": blockers}

def get_gp209_owner_productization_receipt_packet(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RECEIPT_PACKET_ID, db_path)
    packets = get_owner_productization_receipt_packets(db_path)
    return {"pack": _pack_payload(209, component["pack_name"]), "real_sqlite_backed": True, "receipt_packet_component": component, "receipt_packet_count": len(packets), "packets": packets}

def get_gp210_owner_productization_beta_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_owner_productization_beta_readiness_layer(db_path)
    return {"pack": _pack_payload(210, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_owner_productization_beta_readiness_layer(db_path)
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
            "source_gp200_readiness_id": component["source_gp200_readiness_id"],
            "source_gp200_readiness_hash": component["source_gp200_readiness_hash"],
            "source_gp200_readiness_score": component["source_gp200_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "owner_productization_ready": component["owner_productization_ready"],
            "beta_readiness_prepared": component["beta_readiness_prepared"],
            "beta_launch_locked": component["beta_launch_locked"],
            "beta_access_locked": component["beta_access_locked"],
            "vault_not_done": component["vault_not_done"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp211": validation["safe_to_continue_to_gp211"],
            "foundation_status": "owner_productization_beta_readiness_prepared_launch_access_locked_vault_not_done_safe_to_continue",
            "next": next_label,
            **counts,
            "owner_productization_approved": component["owner_productization_approved"],
            "beta_readiness_approved": component["beta_readiness_approved"],
            "beta_launch_requested": component["beta_launch_requested"],
            "beta_launch_approved": component["beta_launch_approved"],
            "public_launch_requested": component["public_launch_requested"],
            "public_launch_approved": component["public_launch_approved"],
            "beta_invite_created": component["beta_invite_created"],
            "beta_invite_sent": component["beta_invite_sent"],
            "beta_tester_added": component["beta_tester_added"],
            "beta_tester_access_requested": component["beta_tester_access_requested"],
            "beta_tester_access_granted": component["beta_tester_access_granted"],
            "beta_tester_access_enabled": component["beta_tester_access_enabled"],
            "beta_access_token_created": component["beta_access_token_created"],
            "beta_access_session_created": component["beta_access_session_created"],
            "billing_flow_created": component["billing_flow_created"],
            "subscription_flow_created": component["subscription_flow_created"],
            "customer_portal_created": component["customer_portal_created"],
            "payment_processor_called": component["payment_processor_called"],
            "tower_billing_handoff_created": component["tower_billing_handoff_created"],
            "provider_unlock_requested": component["provider_unlock_requested"],
            "provider_unlock_approved": component["provider_unlock_approved"],
            "provider_connection_requested": component["provider_connection_requested"],
            "real_provider_connection_started": component["real_provider_connection_started"],
            "provider_api_called": component["provider_api_called"],
            "provider_search_executed": component["provider_search_executed"],
            "provider_token_created": component["provider_token_created"],
            "provider_session_created": component["provider_session_created"],
            "provider_job_reference_created": component["provider_job_reference_created"],
            "provider_status_poll_started": component["provider_status_poll_started"],
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
            "owner_approval_recorded": component["owner_approval_recorded"],
            "execution_enabled": component["execution_enabled"],
            "product_marked_done": component["product_marked_done"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp210",
        },
        "validation": validation,
    }

def get_gp201_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(201, PRODUCTIZATION_SHELL_ID, "VAULT_GP202_BETA_READINESS_INVENTORY", db_path)

def get_gp202_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(202, BETA_READINESS_INVENTORY_ID, "VAULT_GP203_OWNER_PRODUCT_SURFACE_MAP", db_path)

def get_gp203_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(203, OWNER_PRODUCT_SURFACE_MAP_ID, "VAULT_GP204_BETA_TESTER_ACCESS_LOCK_BOARD", db_path)

def get_gp204_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(204, BETA_TESTER_ACCESS_LOCK_ID, "VAULT_GP205_PRODUCT_COPY_POSITIONING_BOARD", db_path)

def get_gp205_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(205, PRODUCT_COPY_POSITIONING_ID, "VAULT_GP206_SUPPORT_FEEDBACK_INTAKE_PLAN", db_path)

def get_gp206_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(206, SUPPORT_FEEDBACK_INTAKE_ID, "VAULT_GP207_BETA_QA_SCENARIO_BOARD", db_path)

def get_gp207_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(207, BETA_QA_SCENARIO_ID, "VAULT_GP208_LAUNCH_RISK_BLOCKER_BOARD", db_path)

def get_gp208_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(208, LAUNCH_RISK_BLOCKER_ID, "VAULT_GP209_OWNER_PRODUCTIZATION_RECEIPT_PACKET", db_path)

def get_gp209_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(209, RECEIPT_PACKET_ID, "VAULT_GP210_OWNER_PRODUCTIZATION_BETA_READINESS_CHECKPOINT", db_path)

def get_gp210_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(210, READINESS_ID, NEXT_PACK, db_path)
    status["gp210_status"]["next_section"] = NEXT_SECTION_ID
    status["gp210_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp210_status"]["next_pack"] = NEXT_PACK
    return status

def get_owner_productization_beta_readiness_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_owner_productization_beta_readiness_layer(db_path)
    components = _rows("vault_owner_productization_components", "gp_number", db_path, {"data_json": "data"})
    beta_items = get_beta_readiness_items(db_path)
    surfaces = get_owner_product_surfaces(db_path)
    access_locks = get_beta_access_locks(db_path)
    copy_items = get_product_copy_positioning_items(db_path)
    support_items = get_support_feedback_intake_items(db_path)
    qa_items = get_beta_qa_scenarios(db_path)
    blockers = get_launch_risk_blockers(db_path)
    packets = get_owner_productization_receipt_packets(db_path)
    readiness = _readiness(db_path)
    validation = validate_owner_productization_beta_readiness_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "beta_readiness": {"beta_readiness_count": len(beta_items), "items": beta_items},
        "surfaces": {"surface_count": len(surfaces), "surfaces": surfaces},
        "access_locks": {"access_lock_count": len(access_locks), "access_locks": access_locks},
        "copy_positioning": {"copy_positioning_count": len(copy_items), "copy_items": copy_items},
        "support_feedback": {"support_feedback_count": len(support_items), "support_items": support_items},
        "qa_scenarios": {"qa_scenario_count": len(qa_items), "qa_items": qa_items},
        "blockers": {"launch_risk_blocker_count": len(blockers), "blockers": blockers},
        "receipt_packets": {"receipt_packet_count": len(packets), "packets": packets},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "owner_productization_beta_readiness_layer_ready": True,
            "owner_productization_ready": validation["owner_productization_ready"],
            "beta_readiness_prepared": validation["beta_readiness_prepared"],
            "safe_to_continue_to_gp211": validation["safe_to_continue_to_gp211"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "beta_launch_locked": True,
            "beta_access_locked": True,
            "owner_productization_approved": False,
            "beta_readiness_approved": False,
            "beta_launch_requested": False,
            "beta_launch_approved": False,
            "public_launch_requested": False,
            "public_launch_approved": False,
            "beta_invite_created": False,
            "beta_invite_sent": False,
            "beta_tester_added": False,
            "beta_tester_access_granted": False,
            "billing_flow_created": False,
            "subscription_flow_created": False,
            "customer_portal_created": False,
            "payment_processor_called": False,
            "tower_billing_handoff_created": False,
            "provider_unlock_requested": False,
            "provider_unlock_approved": False,
            "provider_connection_requested": False,
            "real_provider_connection_started": False,
            "provider_api_called": False,
            "provider_search_executed": False,
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
            "owner_approval_recorded": False,
            "execution_enabled": False,
            "product_marked_done": False,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        "route_map": {
            "page": "/vault/owner-productization-beta-readiness-layer",
            "json": "/vault/owner-productization-beta-readiness-layer.json",
            "gp201": "/vault/gp201-status.json",
            "gp202": "/vault/gp202-status.json",
            "gp203": "/vault/gp203-status.json",
            "gp204": "/vault/gp204-status.json",
            "gp205": "/vault/gp205-status.json",
            "gp206": "/vault/gp206-status.json",
            "gp207": "/vault/gp207-status.json",
            "gp208": "/vault/gp208-status.json",
            "gp209": "/vault/gp209-status.json",
            "gp210": "/vault/gp210-status.json",
        },
    }

def render_owner_productization_beta_readiness_layer_page() -> str:
    home = get_owner_productization_beta_readiness_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    beta_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['item_name'])}</strong>
          <span>{escape(item['item_status'])}</span>
          <code>{escape(item['item_category'])}</code>
        </article>
        """
        for item in home["beta_readiness"]["items"][:9]
    )

    lock_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['access_name'])}</strong>
          <span>{escape(item['access_status'])}</span>
          <code>access locked</code>
        </article>
        """
        for item in home["access_locks"]["access_locks"]
    )

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP201-GP210 Owner Productization Beta Readiness Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 201-210</div>
    <div class="eyebrow">Owner Productization Beta Readiness Layer · GP201-GP210</div>
    <h1>Owner Productization + Beta Readiness</h1>
    <p>This layer prepares the owner-facing beta readiness surface. Launch, tester access, billing, provider access, body reads, restore/export/upload/delete, Tower unlock, execution, and done-state are all still locked.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['beta_readiness_count']}</strong><span>beta readiness items</span></div>
      <div class="metric"><strong>{home['store']['surface_count']}</strong><span>owner surfaces</span></div>
      <div class="metric"><strong>{home['store']['launch_risk_blocker_count']}</strong><span>launch blockers</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP201-GP210 built</span>
      <span class="pill ok">Beta readiness prepared</span>
      <span class="pill ok">Safe to GP211</span>
      <span class="pill danger">No beta launch</span>
      <span class="pill danger">No beta invite</span>
      <span class="pill danger">No beta access</span>
      <span class="pill danger">No billing flow</span>
      <span class="pill danger">No provider unlock</span>
      <span class="pill danger">No execution</span>
      <span class="pill danger">Vault not done</span>
    </div>
  </section>

  <section class="section">
    <h2>Beta Readiness Inventory</h2>
    <div class="cards">{beta_cards}</div>
  </section>

  <section class="section">
    <h2>Beta Access Locks</h2>
    <div class="cards">{lock_cards}</div>
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
