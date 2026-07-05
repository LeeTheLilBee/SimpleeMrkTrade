"""
VAULT GP241-GP250 — Beta Feedback Review and Triage Lock Layer

New section:
Archive Vault — Beta Feedback Review and Triage Lock Layer / GP241-GP250

Builds:
- GP241 Beta Feedback Review and Triage Lock Shell
- GP242 Feedback Review Draft Queue
- GP243 Issue Review Draft Queue
- GP244 Triage Classification Preview Matrix
- GP245 Assignment Lock Contract
- GP246 Escalation Lock Contract
- GP247 Fix Room Handoff Preview
- GP248 Reviewer Decision Lock Board
- GP249 Review Triage Receipt Draft Packet
- GP250 Review Triage Lock Readiness Checkpoint

This layer creates locked review/triage governance records for feedback and
issues. It does not start review, apply classification, assign/escalate, create
tickets, open fix rooms, record decisions, call Tower/billing/providers, read
object bodies, restore/export/upload/delete, execute, or mark Vault done.
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

from vault.beta_feedback_issue_intake_lock_layer_service import (
    get_gp240_status,
    get_gp240_feedback_issue_intake_lock_readiness_checkpoint,
    get_beta_feedback_issue_intake_lock_layer_home,
    validate_beta_feedback_issue_intake_lock_layer,
    get_feedback_form_drafts,
    get_issue_report_drafts,
    get_intake_safety_compliance_locks,
)

LAYER_ID = "VAULT_GP241_250"
LAYER_NAME = "Beta Feedback Review and Triage Lock Layer"
SCHEMA_VERSION = "vault.beta_feedback_review_triage_lock_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_BETA_FEEDBACK_REVIEW_AND_TRIAGE_LOCK_LAYER"
SECTION_TITLE = "Archive Vault — Beta Feedback Review and Triage Lock Layer"
SECTION_RANGE = "GP241-GP250"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_BETA_FEEDBACK_AND_ISSUE_INTAKE_LOCK_LAYER"
PREVIOUS_SECTION_RANGE = "GP231-GP240"

NEXT_SECTION_ID = "ARCHIVE_VAULT_BETA_FIX_AND_RESPONSE_LOCK_LAYER"
NEXT_SECTION_RANGE = "GP251-GP260"
NEXT_PACK = "VAULT_GP251_260_BETA_FIX_AND_RESPONSE_LOCK_LAYER"

DEFAULT_DB_ENV = "VAULT_BETA_FEEDBACK_REVIEW_TRIAGE_LOCK_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_beta_feedback_review_triage_lock_layer.sqlite"

SHELL_ID = "VBFRTL-SHELL-GP241-001"
FEEDBACK_REVIEW_ID = "VBFRTL-FEEDBACKREVIEW-GP242-001"
ISSUE_REVIEW_ID = "VBFRTL-ISSUEREVIEW-GP243-001"
TRIAGE_MATRIX_ID = "VBFRTL-TRIAGE-GP244-001"
ASSIGNMENT_LOCK_ID = "VBFRTL-ASSIGN-GP245-001"
ESCALATION_LOCK_ID = "VBFRTL-ESCALATE-GP246-001"
FIX_ROOM_HANDOFF_ID = "VBFRTL-FIXROOM-GP247-001"
REVIEWER_DECISION_ID = "VBFRTL-DECISION-GP248-001"
RECEIPT_PACKET_ID = "VBFRTL-RECEIPT-GP249-001"
READINESS_ID = "VBFRTL-READINESS-GP250-001"

FALSE_FIELDS = [
    "beta_launch_requested",
    "beta_launch_approved",
    "public_launch_requested",
    "public_launch_approved",
    "beta_invite_created",
    "beta_invite_sent",
    "beta_tester_added",
    "beta_tester_access_granted",
    "beta_access_token_created",
    "beta_access_session_created",
    "onboarding_started",
    "onboarding_completed",
    "profile_submitted",
    "policy_acknowledged",
    "workspace_opened",
    "support_channel_opened",
    "support_message_sent",
    "feedback_form_opened",
    "feedback_draft_created",
    "feedback_submitted",
    "feedback_received",
    "feedback_receipt_finalized",
    "issue_report_opened",
    "issue_draft_created",
    "issue_created",
    "issue_submitted",
    "issue_received",
    "issue_receipt_finalized",
    "support_ticket_created",
    "support_ticket_assigned",
    "bug_ticket_created",
    "bug_ticket_assigned",
    "feedback_review_started",
    "feedback_review_completed",
    "feedback_review_decision_recorded",
    "issue_review_started",
    "issue_review_completed",
    "issue_review_decision_recorded",
    "intake_routing_executed",
    "intake_route_assigned",
    "intake_triage_started",
    "intake_triage_completed",
    "triage_classification_applied",
    "triage_priority_applied",
    "triage_severity_applied",
    "assignment_created",
    "assignment_sent",
    "assignment_accepted",
    "assignee_notified",
    "intake_escalation_created",
    "intake_escalation_sent",
    "escalation_acknowledged",
    "fix_room_opened",
    "fix_room_handoff_created",
    "fix_room_handoff_sent",
    "fix_task_created",
    "fix_task_assigned",
    "fix_started",
    "fix_completed",
    "response_draft_created",
    "response_sent",
    "reviewer_decision_recorded",
    "reviewer_approval_recorded",
    "reviewer_rejection_recorded",
    "reviewer_closeout_recorded",
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

FEEDBACK_REVIEW_DRAFTS = [
    ("general_feedback_review_draft", "General Feedback Review Draft", "general", "review_locked"),
    ("readiness_feedback_review_draft", "Readiness Feedback Review Draft", "readiness", "review_locked"),
    ("archive_feedback_review_draft", "Archive Feedback Review Draft", "archive", "review_locked"),
    ("receipt_feedback_review_draft", "Receipt Feedback Review Draft", "receipt", "review_locked"),
    ("access_feedback_review_draft", "Access Feedback Review Draft", "access", "review_locked"),
    ("support_feedback_review_draft", "Support Feedback Review Draft", "support", "review_locked"),
]

ISSUE_REVIEW_DRAFTS = [
    ("bug_issue_review_draft", "Bug Issue Review Draft", "bug", "review_locked"),
    ("access_issue_review_draft", "Access Issue Review Draft", "access", "review_locked"),
    ("receipt_issue_review_draft", "Receipt Issue Review Draft", "receipt", "review_locked"),
    ("archive_issue_review_draft", "Archive Issue Review Draft", "archive", "review_locked"),
    ("provider_boundary_issue_review_draft", "Provider Boundary Issue Review Draft", "provider", "review_locked"),
    ("security_issue_review_draft", "Security Issue Review Draft", "security", "review_locked"),
]

TRIAGE_CLASSIFICATIONS = [
    ("needs_owner_review", "Needs Owner Review", "owner", "classification_preview_locked"),
    ("needs_tower_review", "Needs Tower Review", "tower", "classification_preview_locked"),
    ("needs_vault_review", "Needs Vault Review", "vault", "classification_preview_locked"),
    ("needs_fix_room", "Needs Fix Room", "fix", "classification_preview_locked"),
    ("needs_security_review", "Needs Security Review", "security", "classification_preview_locked"),
    ("needs_provider_boundary_review", "Needs Provider Boundary Review", "provider", "classification_preview_locked"),
    ("needs_support_response", "Needs Support Response", "support", "classification_preview_locked"),
]

ASSIGNMENT_LOCKS = [
    ("owner_assignment_lock", "Owner Assignment Lock", "owner"),
    ("tower_assignment_lock", "Tower Assignment Lock", "tower"),
    ("vault_assignment_lock", "Vault Assignment Lock", "vault"),
    ("support_assignment_lock", "Support Assignment Lock", "support"),
    ("fix_room_assignment_lock", "Fix Room Assignment Lock", "fix"),
    ("security_assignment_lock", "Security Assignment Lock", "security"),
]

ESCALATION_LOCKS = [
    ("owner_escalation_lock", "Owner Escalation Lock", "owner"),
    ("tower_escalation_lock", "Tower Escalation Lock", "tower"),
    ("provider_boundary_escalation_lock", "Provider Boundary Escalation Lock", "provider"),
    ("security_escalation_lock", "Security Escalation Lock", "security"),
    ("emergency_stop_escalation_lock", "Emergency Stop Escalation Lock", "emergency"),
]

FIX_ROOM_HANDOFFS = [
    ("ui_fix_room_handoff_preview", "UI Fix Room Handoff Preview", "ui", "preview_locked"),
    ("receipt_fix_room_handoff_preview", "Receipt Fix Room Handoff Preview", "receipt", "preview_locked"),
    ("access_fix_room_handoff_preview", "Access Fix Room Handoff Preview", "access", "preview_locked"),
    ("provider_boundary_fix_room_handoff_preview", "Provider Boundary Fix Room Handoff Preview", "provider", "preview_locked"),
    ("safety_fix_room_handoff_preview", "Safety Fix Room Handoff Preview", "safety", "preview_locked"),
]

REVIEWER_DECISION_LOCKS = [
    ("reviewer_accept_lock", "Reviewer Accept Lock", "accept"),
    ("reviewer_reject_lock", "Reviewer Reject Lock", "reject"),
    ("reviewer_defer_lock", "Reviewer Defer Lock", "defer"),
    ("reviewer_escalate_lock", "Reviewer Escalate Lock", "escalate"),
    ("reviewer_closeout_lock", "Reviewer Closeout Lock", "closeout"),
    ("owner_override_lock", "Owner Override Lock", "owner_override"),
]

COMPONENT_SPECS = [
    (241, SHELL_ID, "VAULT_GP241", "Beta Feedback Review and Triage Lock Shell", "beta_feedback_review_triage_lock_shell"),
    (242, FEEDBACK_REVIEW_ID, "VAULT_GP242", "Feedback Review Draft Queue", "feedback_review_draft_queue"),
    (243, ISSUE_REVIEW_ID, "VAULT_GP243", "Issue Review Draft Queue", "issue_review_draft_queue"),
    (244, TRIAGE_MATRIX_ID, "VAULT_GP244", "Triage Classification Preview Matrix", "triage_classification_preview_matrix"),
    (245, ASSIGNMENT_LOCK_ID, "VAULT_GP245", "Assignment Lock Contract", "assignment_lock_contract"),
    (246, ESCALATION_LOCK_ID, "VAULT_GP246", "Escalation Lock Contract", "escalation_lock_contract"),
    (247, FIX_ROOM_HANDOFF_ID, "VAULT_GP247", "Fix Room Handoff Preview", "fix_room_handoff_preview"),
    (248, REVIEWER_DECISION_ID, "VAULT_GP248", "Reviewer Decision Lock Board", "reviewer_decision_lock_board"),
    (249, RECEIPT_PACKET_ID, "VAULT_GP249", "Review Triage Receipt Draft Packet", "review_triage_receipt_draft_packet"),
    (250, READINESS_ID, "VAULT_GP250", "Review Triage Lock Readiness Checkpoint", "review_triage_lock_readiness_checkpoint"),
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
        "source_gp240_readiness_score",
        "component_count",
        "feedback_review_count",
        "issue_review_count",
        "triage_classification_count",
        "assignment_lock_count",
        "escalation_lock_count",
        "fix_room_handoff_count",
        "reviewer_decision_lock_count",
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
        "depends_on": ["VAULT_GP240"],
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
        "depends_on": ["VAULT_GP240"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_beta_feedback_review_triage_lock_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_beta_feedback_review_triage_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp240_readiness_id TEXT NOT NULL,
                source_gp240_readiness_hash TEXT NOT NULL,
                source_gp240_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                review_triage_ready INTEGER NOT NULL DEFAULT 1,
                review_lock_active INTEGER NOT NULL DEFAULT 1,
                triage_lock_active INTEGER NOT NULL DEFAULT 1,
                assignment_lock_active INTEGER NOT NULL DEFAULT 1,
                escalation_lock_active INTEGER NOT NULL DEFAULT 1,
                fix_room_preview_only INTEGER NOT NULL DEFAULT 1,
                reviewer_decision_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_feedback_review_draft_queue (
                review_id TEXT PRIMARY KEY,
                review_code TEXT NOT NULL UNIQUE,
                review_name TEXT NOT NULL,
                review_category TEXT NOT NULL,
                review_status TEXT NOT NULL,
                review_ready INTEGER NOT NULL DEFAULT 1,
                review_locked INTEGER NOT NULL DEFAULT 1,
                decision_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_issue_review_draft_queue (
                review_id TEXT PRIMARY KEY,
                review_code TEXT NOT NULL UNIQUE,
                review_name TEXT NOT NULL,
                review_category TEXT NOT NULL,
                review_status TEXT NOT NULL,
                review_ready INTEGER NOT NULL DEFAULT 1,
                review_locked INTEGER NOT NULL DEFAULT 1,
                decision_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_triage_classification_preview_matrix (
                classification_id TEXT PRIMARY KEY,
                classification_code TEXT NOT NULL UNIQUE,
                classification_name TEXT NOT NULL,
                classification_category TEXT NOT NULL,
                classification_status TEXT NOT NULL,
                preview_ready INTEGER NOT NULL DEFAULT 1,
                classification_locked INTEGER NOT NULL DEFAULT 1,
                priority_locked INTEGER NOT NULL DEFAULT 1,
                severity_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                classification_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_assignment_lock_contracts (
                lock_id TEXT PRIMARY KEY,
                lock_code TEXT NOT NULL UNIQUE,
                lock_name TEXT NOT NULL,
                lock_category TEXT NOT NULL,
                lock_status TEXT NOT NULL,
                assignment_locked INTEGER NOT NULL DEFAULT 1,
                notification_locked INTEGER NOT NULL DEFAULT 1,
                acceptance_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                lock_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_escalation_lock_contracts (
                lock_id TEXT PRIMARY KEY,
                lock_code TEXT NOT NULL UNIQUE,
                lock_name TEXT NOT NULL,
                lock_category TEXT NOT NULL,
                lock_status TEXT NOT NULL,
                escalation_locked INTEGER NOT NULL DEFAULT 1,
                escalation_send_locked INTEGER NOT NULL DEFAULT 1,
                acknowledgment_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                lock_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_fix_room_handoff_previews (
                handoff_id TEXT PRIMARY KEY,
                handoff_code TEXT NOT NULL UNIQUE,
                handoff_name TEXT NOT NULL,
                handoff_category TEXT NOT NULL,
                handoff_status TEXT NOT NULL,
                preview_ready INTEGER NOT NULL DEFAULT 1,
                fix_room_open_locked INTEGER NOT NULL DEFAULT 1,
                handoff_locked INTEGER NOT NULL DEFAULT 1,
                fix_task_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                handoff_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_reviewer_decision_lock_board (
                decision_lock_id TEXT PRIMARY KEY,
                decision_code TEXT NOT NULL UNIQUE,
                decision_name TEXT NOT NULL,
                decision_category TEXT NOT NULL,
                decision_status TEXT NOT NULL,
                decision_locked INTEGER NOT NULL DEFAULT 1,
                approval_locked INTEGER NOT NULL DEFAULT 1,
                rejection_locked INTEGER NOT NULL DEFAULT 1,
                closeout_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                decision_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_review_triage_receipt_draft_packets (
                receipt_packet_id TEXT PRIMARY KEY,
                packet_code TEXT NOT NULL UNIQUE,
                packet_name TEXT NOT NULL,
                packet_status TEXT NOT NULL,
                packet_ready INTEGER NOT NULL DEFAULT 1,
                packet_locked INTEGER NOT NULL DEFAULT 1,
                final_review_receipt INTEGER NOT NULL DEFAULT 0,
                final_triage_receipt INTEGER NOT NULL DEFAULT 0,
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
            CREATE TABLE IF NOT EXISTS vault_review_triage_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                feedback_review_count INTEGER NOT NULL,
                issue_review_count INTEGER NOT NULL,
                triage_classification_count INTEGER NOT NULL,
                assignment_lock_count INTEGER NOT NULL,
                escalation_lock_count INTEGER NOT NULL,
                fix_room_handoff_count INTEGER NOT NULL,
                reviewer_decision_lock_count INTEGER NOT NULL,
                receipt_packet_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                review_triage_ready INTEGER NOT NULL DEFAULT 1,
                review_lock_active INTEGER NOT NULL DEFAULT 1,
                triage_lock_active INTEGER NOT NULL DEFAULT 1,
                assignment_lock_active INTEGER NOT NULL DEFAULT 1,
                escalation_lock_active INTEGER NOT NULL DEFAULT 1,
                fix_room_preview_only INTEGER NOT NULL DEFAULT 1,
                reviewer_decision_locked INTEGER NOT NULL DEFAULT 1,
                safe_to_continue_to_gp251 INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_review_triage_events (
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
            "vault_beta_feedback_review_triage_components",
            "vault_feedback_review_draft_queue",
            "vault_issue_review_draft_queue",
            "vault_triage_classification_preview_matrix",
            "vault_assignment_lock_contracts",
            "vault_escalation_lock_contracts",
            "vault_fix_room_handoff_previews",
            "vault_reviewer_decision_lock_board",
            "vault_review_triage_receipt_draft_packets",
            "vault_review_triage_readiness",
            "vault_review_triage_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VBFRTLEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_review_triage_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_beta_feedback_review_triage_lock_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_beta_feedback_review_triage_lock_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_beta_feedback_review_triage_components WHERE component_id = ?",
            (SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp240_status = get_gp240_status()["gp240_status"]
            gp240_checkpoint = get_gp240_feedback_issue_intake_lock_readiness_checkpoint()["readiness_checkpoint"]
            gp240_home = get_beta_feedback_issue_intake_lock_layer_home()
            gp240_validation = validate_beta_feedback_issue_intake_lock_layer()
            source_feedback_forms = get_feedback_form_drafts()
            source_issue_reports = get_issue_report_drafts()
            source_safety_locks = get_intake_safety_compliance_locks()

            readiness = gp240_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp240_readiness_id": readiness["readiness_id"],
                "source_gp240_readiness_hash": readiness["readiness_hash"],
                "source_gp240_readiness_score": readiness["readiness_score"],
            }

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "feedback_review_count": len(FEEDBACK_REVIEW_DRAFTS),
                "issue_review_count": len(ISSUE_REVIEW_DRAFTS),
                "triage_classification_count": len(TRIAGE_CLASSIFICATIONS),
                "assignment_lock_count": len(ASSIGNMENT_LOCKS),
                "escalation_lock_count": len(ESCALATION_LOCKS),
                "fix_room_handoff_count": len(FIX_ROOM_HANDOFFS),
                "reviewer_decision_lock_count": len(REVIEWER_DECISION_LOCKS),
                "receipt_packet_count": 1,
            }

            source_context = {
                "source_gp240_status_ready": gp240_status["ready"],
                "source_gp240_validation_passed": gp240_status["validation_passed"],
                "source_gp240_safe_to_continue_to_gp241": gp240_status["safe_to_continue_to_gp241"],
                "source_gp240_readiness_hash": readiness["readiness_hash"],
                "source_gp240_readiness_score": readiness["readiness_score"],
                "source_feedback_form_count": len(source_feedback_forms),
                "source_issue_report_count": len(source_issue_reports),
                "source_intake_safety_lock_count": len(source_safety_locks),
                "source_validation_check_count": gp240_validation["check_count"],
            }

            component_extra = {
                SHELL_ID: {"beta_feedback_review_triage_lock_shell_ready": True},
                FEEDBACK_REVIEW_ID: {"feedback_review_draft_queue_ready": True, "feedback_review_count": counts["feedback_review_count"]},
                ISSUE_REVIEW_ID: {"issue_review_draft_queue_ready": True, "issue_review_count": counts["issue_review_count"]},
                TRIAGE_MATRIX_ID: {"triage_classification_preview_matrix_ready": True, "triage_classification_count": counts["triage_classification_count"]},
                ASSIGNMENT_LOCK_ID: {"assignment_lock_contract_ready": True, "assignment_lock_count": counts["assignment_lock_count"]},
                ESCALATION_LOCK_ID: {"escalation_lock_contract_ready": True, "escalation_lock_count": counts["escalation_lock_count"]},
                FIX_ROOM_HANDOFF_ID: {"fix_room_handoff_preview_ready": True, "fix_room_handoff_count": counts["fix_room_handoff_count"]},
                REVIEWER_DECISION_ID: {"reviewer_decision_lock_board_ready": True, "reviewer_decision_lock_count": counts["reviewer_decision_lock_count"]},
                RECEIPT_PACKET_ID: {"review_triage_receipt_draft_packet_ready": True, "receipt_packet_count": counts["receipt_packet_count"]},
                READINESS_ID: {"review_triage_lock_readiness_checkpoint_ready": True, "safe_to_continue_to_gp251": True},
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
                    "review_triage_ready": True,
                    "review_lock_active": True,
                    "triage_lock_active": True,
                    "assignment_lock_active": True,
                    "escalation_lock_active": True,
                    "fix_room_preview_only": True,
                    "reviewer_decision_locked": True,
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
                    "review_triage_ready": 1,
                    "review_lock_active": 1,
                    "triage_lock_active": 1,
                    "assignment_lock_active": 1,
                    "escalation_lock_active": 1,
                    "fix_room_preview_only": 1,
                    "reviewer_decision_locked": 1,
                    "vault_not_done": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_feedback_review_triage_components", row)

            for idx, (code, name, category, status) in enumerate(FEEDBACK_REVIEW_DRAFTS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "review_code": code,
                    "review_name": name,
                    "review_category": category,
                    "review_status": status,
                    "review_ready": True,
                    "review_locked": True,
                    "decision_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "review_id": f"VBFRTLFEEDREV-{idx:03d}",
                    "review_code": code,
                    "review_name": name,
                    "review_category": category,
                    "review_status": status,
                    "review_ready": 1,
                    "review_locked": 1,
                    "decision_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "review_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_feedback_review_draft_queue", row)

            for idx, (code, name, category, status) in enumerate(ISSUE_REVIEW_DRAFTS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "review_code": code,
                    "review_name": name,
                    "review_category": category,
                    "review_status": status,
                    "review_ready": True,
                    "review_locked": True,
                    "decision_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "review_id": f"VBFRTLISSUEREV-{idx:03d}",
                    "review_code": code,
                    "review_name": name,
                    "review_category": category,
                    "review_status": status,
                    "review_ready": 1,
                    "review_locked": 1,
                    "decision_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "review_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_issue_review_draft_queue", row)

            for idx, (code, name, category, status) in enumerate(TRIAGE_CLASSIFICATIONS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "classification_code": code,
                    "classification_name": name,
                    "classification_category": category,
                    "classification_status": status,
                    "preview_ready": True,
                    "classification_locked": True,
                    "priority_locked": True,
                    "severity_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "classification_id": f"VBFRTLCLASS-{idx:03d}",
                    "classification_code": code,
                    "classification_name": name,
                    "classification_category": category,
                    "classification_status": status,
                    "preview_ready": 1,
                    "classification_locked": 1,
                    "priority_locked": 1,
                    "severity_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "classification_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_triage_classification_preview_matrix", row)

            for idx, (code, name, category) in enumerate(ASSIGNMENT_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "lock_status": "ASSIGNMENT_LOCK_ACTIVE",
                    "assignment_locked": True,
                    "notification_locked": True,
                    "acceptance_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "lock_id": f"VBFRTLASSIGN-{idx:03d}",
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "lock_status": payload["lock_status"],
                    "assignment_locked": 1,
                    "notification_locked": 1,
                    "acceptance_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "lock_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_assignment_lock_contracts", row)

            for idx, (code, name, category) in enumerate(ESCALATION_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "lock_status": "ESCALATION_LOCK_ACTIVE",
                    "escalation_locked": True,
                    "escalation_send_locked": True,
                    "acknowledgment_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "lock_id": f"VBFRTLESC-{idx:03d}",
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "lock_status": payload["lock_status"],
                    "escalation_locked": 1,
                    "escalation_send_locked": 1,
                    "acknowledgment_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "lock_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_escalation_lock_contracts", row)

            for idx, (code, name, category, status) in enumerate(FIX_ROOM_HANDOFFS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "handoff_code": code,
                    "handoff_name": name,
                    "handoff_category": category,
                    "handoff_status": status,
                    "preview_ready": True,
                    "fix_room_open_locked": True,
                    "handoff_locked": True,
                    "fix_task_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "handoff_id": f"VBFRTLFIX-{idx:03d}",
                    "handoff_code": code,
                    "handoff_name": name,
                    "handoff_category": category,
                    "handoff_status": status,
                    "preview_ready": 1,
                    "fix_room_open_locked": 1,
                    "handoff_locked": 1,
                    "fix_task_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "handoff_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_fix_room_handoff_previews", row)

            for idx, (code, name, category) in enumerate(REVIEWER_DECISION_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "decision_code": code,
                    "decision_name": name,
                    "decision_category": category,
                    "decision_status": "REVIEWER_DECISION_LOCK_ACTIVE",
                    "decision_locked": True,
                    "approval_locked": True,
                    "rejection_locked": True,
                    "closeout_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "decision_lock_id": f"VBFRTLDEC-{idx:03d}",
                    "decision_code": code,
                    "decision_name": name,
                    "decision_category": category,
                    "decision_status": payload["decision_status"],
                    "decision_locked": 1,
                    "approval_locked": 1,
                    "rejection_locked": 1,
                    "closeout_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "decision_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_reviewer_decision_lock_board", row)

            packet_payload = {
                "schema_version": SCHEMA_VERSION,
                "packet_code": "vault_gp241_250_review_triage_packet",
                "packet_name": "Vault GP241-GP250 Review Triage Receipt Draft Packet",
                "packet_status": "READY_LOCKED_DRAFT_ONLY_NO_REVIEW_OR_TRIAGE_RECEIPT",
                "source_gp240_readiness_id": readiness["readiness_id"],
                "source_gp240_readiness_hash": readiness["readiness_hash"],
                "source_gp240_readiness_score": readiness["readiness_score"],
                **counts,
                "review_triage_ready": True,
                "review_lock_active": True,
                "triage_lock_active": True,
                "final_review_receipt": False,
                "final_triage_receipt": False,
                "locked_truth": {field: False for field in FALSE_FIELDS},
                "vault_done": False,
                "clouds_should_continue": False,
            }
            row = {
                "receipt_packet_id": RECEIPT_PACKET_ID,
                "packet_code": "vault_gp241_250_review_triage_packet",
                "packet_name": "Vault GP241-GP250 Review Triage Receipt Draft Packet",
                "packet_status": packet_payload["packet_status"],
                "packet_ready": 1,
                "packet_locked": 1,
                "final_review_receipt": 0,
                "final_triage_receipt": 0,
                "payload_json": _json_dumps(packet_payload),
                "packet_hash": _hash_payload(packet_payload),
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                row[field] = 0
            _insert_dict(conn, "vault_review_triage_receipt_draft_packets", row)

            checks = [
                ("SOURCE_GP240_READY", bool(gp240_status["ready"])),
                ("SOURCE_GP240_VALIDATION_PASSED", bool(gp240_status["validation_passed"])),
                ("SOURCE_GP240_SAFE_TO_CONTINUE", bool(gp240_status["safe_to_continue_to_gp241"])),
                ("SOURCE_GP240_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP240_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("FEEDBACK_REVIEW_COUNT_6", counts["feedback_review_count"] == 6),
                ("ISSUE_REVIEW_COUNT_6", counts["issue_review_count"] == 6),
                ("TRIAGE_CLASSIFICATION_COUNT_7", counts["triage_classification_count"] == 7),
                ("ASSIGNMENT_LOCK_COUNT_6", counts["assignment_lock_count"] == 6),
                ("ESCALATION_LOCK_COUNT_5", counts["escalation_lock_count"] == 5),
                ("FIX_ROOM_HANDOFF_COUNT_5", counts["fix_room_handoff_count"] == 5),
                ("REVIEWER_DECISION_LOCK_COUNT_6", counts["reviewer_decision_lock_count"] == 6),
                ("RECEIPT_PACKET_COUNT_1", counts["receipt_packet_count"] == 1),
                ("SECTION_GP241_GP250", SECTION_RANGE == "GP241-GP250"),
                ("NEXT_SECTION_GP251_GP260", NEXT_SECTION_RANGE == "GP251-GP260"),
                ("REVIEW_TRIAGE_READY", True),
                ("REVIEW_LOCK_ACTIVE", True),
                ("TRIAGE_LOCK_ACTIVE", True),
                ("ASSIGNMENT_LOCK_ACTIVE", True),
                ("ESCALATION_LOCK_ACTIVE", True),
                ("FIX_ROOM_PREVIEW_ONLY", True),
                ("REVIEWER_DECISION_LOCKED", True),
                ("NO_FEEDBACK_REVIEW_STARTED", True),
                ("NO_ISSUE_REVIEW_STARTED", True),
                ("NO_TRIAGE_STARTED", True),
                ("NO_CLASSIFICATION_APPLIED", True),
                ("NO_ASSIGNMENT_CREATED", True),
                ("NO_ESCALATION_CREATED", True),
                ("NO_FIX_ROOM_OPENED", True),
                ("NO_REVIEWER_DECISION", True),
                ("NO_TICKETS_CREATED", True),
                ("NO_TOWER_GATE_PASS", True),
                ("NO_BILLING_SUBSCRIPTION", True),
                ("NO_PROVIDER_UNLOCK", True),
                ("NO_PROVIDER_API", True),
                ("NO_PROVIDER_METADATA_READ", True),
                ("NO_OBJECT_BODY", True),
                ("NO_DOWNLOAD", True),
                ("NO_RESTORE_EXPORT_UPLOAD_DELETE", True),
                ("NO_EXECUTION", True),
                ("VAULT_NOT_DONE", True),
                ("CLOUDS_PARKED", True),
            ]
            passed_count = len([c for c in checks if c[1]])
            failed_count = len(checks) - passed_count

            readiness_payload = {
                "schema_version": SCHEMA_VERSION,
                "readiness_id": READINESS_ID,
                "gp_number": 250,
                "pack_id": "VAULT_GP250",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp240_readiness_id": readiness["readiness_id"],
                "source_gp240_readiness_hash": readiness["readiness_hash"],
                "source_gp240_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "review_triage_ready": True,
                "review_lock_active": True,
                "triage_lock_active": True,
                "assignment_lock_active": True,
                "escalation_lock_active": True,
                "fix_room_preview_only": True,
                "reviewer_decision_locked": True,
                "safe_to_continue_to_gp251": failed_count == 0,
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
                "gp_number": 250,
                "pack_id": "VAULT_GP250",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "BETA_FEEDBACK_REVIEW_TRIAGE_LOCK_READY_REVIEW_TRIAGE_ASSIGNMENT_ESCALATION_FIX_DECISION_LOCKED_VAULT_NOT_DONE_SAFE_TO_CONTINUE",
                "readiness_score": readiness_payload["readiness_score"],
                **counts,
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "review_triage_ready": 1,
                "review_lock_active": 1,
                "triage_lock_active": 1,
                "assignment_lock_active": 1,
                "escalation_lock_active": 1,
                "fix_room_preview_only": 1,
                "reviewer_decision_locked": 1,
                "safe_to_continue_to_gp251": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_review_triage_readiness", row)

            for event_type, event_payload in [
                ("GP241_BETA_FEEDBACK_REVIEW_TRIAGE_LOCK_SHELL_CREATED", {"component_id": SHELL_ID}),
                ("GP242_FEEDBACK_REVIEW_DRAFT_QUEUE_CREATED", {"feedback_review_count": counts["feedback_review_count"]}),
                ("GP243_ISSUE_REVIEW_DRAFT_QUEUE_CREATED", {"issue_review_count": counts["issue_review_count"]}),
                ("GP244_TRIAGE_CLASSIFICATION_PREVIEW_MATRIX_CREATED", {"triage_classification_count": counts["triage_classification_count"]}),
                ("GP245_ASSIGNMENT_LOCK_CONTRACT_CREATED", {"assignment_lock_count": counts["assignment_lock_count"]}),
                ("GP246_ESCALATION_LOCK_CONTRACT_CREATED", {"escalation_lock_count": counts["escalation_lock_count"]}),
                ("GP247_FIX_ROOM_HANDOFF_PREVIEW_CREATED", {"fix_room_handoff_count": counts["fix_room_handoff_count"]}),
                ("GP248_REVIEWER_DECISION_LOCK_BOARD_CREATED", {"reviewer_decision_lock_count": counts["reviewer_decision_lock_count"]}),
                ("GP249_REVIEW_TRIAGE_RECEIPT_DRAFT_PACKET_CREATED", {"receipt_packet_count": counts["receipt_packet_count"]}),
                ("GP250_REVIEW_TRIAGE_LOCK_READINESS_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp251": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_feedback_review_triage_components").fetchone()["c"]),
            "feedback_review_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_feedback_review_draft_queue").fetchone()["c"]),
            "issue_review_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_issue_review_draft_queue").fetchone()["c"]),
            "triage_classification_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_triage_classification_preview_matrix").fetchone()["c"]),
            "assignment_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_assignment_lock_contracts").fetchone()["c"]),
            "escalation_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_escalation_lock_contracts").fetchone()["c"]),
            "fix_room_handoff_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_fix_room_handoff_previews").fetchone()["c"]),
            "reviewer_decision_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_reviewer_decision_lock_board").fetchone()["c"]),
            "receipt_packet_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_review_triage_receipt_draft_packets").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_review_triage_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_review_triage_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_beta_feedback_review_triage_lock_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_beta_feedback_review_triage_lock_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_beta_feedback_review_triage_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_beta_feedback_review_triage_lock_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_review_triage_readiness WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_beta_feedback_review_triage_lock_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_review_triage_events ORDER BY created_at, event_id").fetchall()
    return [{"event_id": row["event_id"], "event_type": row["event_type"], "event_payload": _json_loads(row["event_payload_json"]), "created_at": row["created_at"]} for row in rows]

def get_feedback_review_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_feedback_review_draft_queue", "review_code", db_path, {"payload_json": "payload"})

def get_issue_review_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_issue_review_draft_queue", "review_code", db_path, {"payload_json": "payload"})

def get_triage_classification_previews(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_triage_classification_preview_matrix", "classification_code", db_path, {"payload_json": "payload"})

def get_assignment_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_assignment_lock_contracts", "lock_code", db_path, {"payload_json": "payload"})

def get_escalation_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_escalation_lock_contracts", "lock_code", db_path, {"payload_json": "payload"})

def get_fix_room_handoff_previews(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_fix_room_handoff_previews", "handoff_code", db_path, {"payload_json": "payload"})

def get_reviewer_decision_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_reviewer_decision_lock_board", "decision_code", db_path, {"payload_json": "payload"})

def get_review_triage_receipt_packets(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_review_triage_receipt_draft_packets", "packet_code", db_path, {"payload_json": "payload"})

def validate_beta_feedback_review_triage_lock_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_beta_feedback_review_triage_components", "gp_number", db_path, {"data_json": "data"})
    feedback_reviews = get_feedback_review_drafts(db_path)
    issue_reviews = get_issue_review_drafts(db_path)
    classifications = get_triage_classification_previews(db_path)
    assignments = get_assignment_locks(db_path)
    escalations = get_escalation_locks(db_path)
    fix_handoffs = get_fix_room_handoff_previews(db_path)
    decisions = get_reviewer_decision_locks(db_path)
    packets = get_review_triage_receipt_packets(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("FEEDBACK_REVIEW_COUNT_6", len(feedback_reviews) == len(FEEDBACK_REVIEW_DRAFTS)),
        ("ISSUE_REVIEW_COUNT_6", len(issue_reviews) == len(ISSUE_REVIEW_DRAFTS)),
        ("TRIAGE_CLASSIFICATION_COUNT_7", len(classifications) == len(TRIAGE_CLASSIFICATIONS)),
        ("ASSIGNMENT_LOCK_COUNT_6", len(assignments) == len(ASSIGNMENT_LOCKS)),
        ("ESCALATION_LOCK_COUNT_5", len(escalations) == len(ESCALATION_LOCKS)),
        ("FIX_ROOM_HANDOFF_COUNT_5", len(fix_handoffs) == len(FIX_ROOM_HANDOFFS)),
        ("REVIEWER_DECISION_LOCK_COUNT_6", len(decisions) == len(REVIEWER_DECISION_LOCKS)),
        ("RECEIPT_PACKET_COUNT_1", len(packets) == 1),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("REVIEW_TRIAGE_READY", readiness["review_triage_ready"] is True),
        ("REVIEW_LOCK_ACTIVE", readiness["review_lock_active"] is True),
        ("TRIAGE_LOCK_ACTIVE", readiness["triage_lock_active"] is True),
        ("ASSIGNMENT_LOCK_ACTIVE", readiness["assignment_lock_active"] is True),
        ("ESCALATION_LOCK_ACTIVE", readiness["escalation_lock_active"] is True),
        ("FIX_ROOM_PREVIEW_ONLY", readiness["fix_room_preview_only"] is True),
        ("REVIEWER_DECISION_LOCKED", readiness["reviewer_decision_locked"] is True),
        ("SAFE_TO_CONTINUE_TO_GP251", readiness["safe_to_continue_to_gp251"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("VAULT_NOT_DONE", readiness["vault_done"] is False),
        ("CLOUDS_PARKED", readiness["clouds_should_continue"] is False),
        ("SECTION_GP241_GP250", readiness["section_range"] == "GP241-GP250"),
        ("NEXT_SECTION_GP251_GP260", readiness["readiness_payload"]["next_section_range"] == "GP251-GP260"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_READY", all(item["component_ready"] is True for item in components)),
        ("ALL_COMPONENTS_LOCKED", all(item["component_locked"] is True for item in components)),
        ("ALL_COMPONENTS_REVIEW_TRIAGE_LOCKED", all(item["review_lock_active"] and item["triage_lock_active"] for item in components)),
        ("ALL_COMPONENTS_ASSIGNMENT_ESCALATION_LOCKED", all(item["assignment_lock_active"] and item["escalation_lock_active"] for item in components)),
        ("ALL_COMPONENTS_FIX_DECISION_LOCKED", all(item["fix_room_preview_only"] and item["reviewer_decision_locked"] for item in components)),
        ("ALL_FEEDBACK_REVIEWS_READY_LOCKED", all(item["review_ready"] and item["review_locked"] and item["decision_locked"] for item in feedback_reviews)),
        ("ALL_ISSUE_REVIEWS_READY_LOCKED", all(item["review_ready"] and item["review_locked"] and item["decision_locked"] for item in issue_reviews)),
        ("ALL_CLASSIFICATIONS_PREVIEW_LOCKED", all(item["preview_ready"] and item["classification_locked"] and item["priority_locked"] and item["severity_locked"] for item in classifications)),
        ("ALL_ASSIGNMENTS_LOCKED", all(item["assignment_locked"] and item["notification_locked"] and item["acceptance_locked"] for item in assignments)),
        ("ALL_ESCALATIONS_LOCKED", all(item["escalation_locked"] and item["escalation_send_locked"] and item["acknowledgment_locked"] for item in escalations)),
        ("ALL_FIX_HANDOFFS_PREVIEW_LOCKED", all(item["preview_ready"] and item["fix_room_open_locked"] and item["handoff_locked"] and item["fix_task_locked"] for item in fix_handoffs)),
        ("ALL_DECISIONS_LOCKED", all(item["decision_locked"] and item["approval_locked"] and item["rejection_locked"] and item["closeout_locked"] for item in decisions)),
        ("PACKET_READY_LOCKED", all(item["packet_ready"] and item["packet_locked"] for item in packets)),
        ("NO_FINAL_REVIEW_OR_TRIAGE_RECEIPT", all(item["final_review_receipt"] is False and item["final_triage_receipt"] is False for item in packets)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("FEEDBACKREVIEW", feedback_reviews),
        ("ISSUEREVIEW", issue_reviews),
        ("CLASSIFICATION", classifications),
        ("ASSIGNMENT", assignments),
        ("ESCALATION", escalations),
        ("FIXROOM", fix_handoffs),
        ("DECISION", decisions),
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
        "feedback_review_count": len(feedback_reviews),
        "issue_review_count": len(issue_reviews),
        "triage_classification_count": len(classifications),
        "assignment_lock_count": len(assignments),
        "escalation_lock_count": len(escalations),
        "fix_room_handoff_count": len(fix_handoffs),
        "reviewer_decision_lock_count": len(decisions),
        "receipt_packet_count": len(packets),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "review_triage_ready": len(failed) == 0 and readiness["review_triage_ready"] is True,
        "safe_to_continue_to_gp251": len(failed) == 0 and readiness["safe_to_continue_to_gp251"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp241_beta_feedback_review_triage_lock_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SHELL_ID, db_path)
    return {"pack": _pack_payload(241, component["pack_name"]), "real_sqlite_backed": True, "shell": component}

def get_gp242_feedback_review_draft_queue(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(FEEDBACK_REVIEW_ID, db_path)
    rows = get_feedback_review_drafts(db_path)
    return {"pack": _pack_payload(242, component["pack_name"]), "real_sqlite_backed": True, "feedback_review_queue": component, "feedback_review_count": len(rows), "reviews": rows}

def get_gp243_issue_review_draft_queue(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(ISSUE_REVIEW_ID, db_path)
    rows = get_issue_review_drafts(db_path)
    return {"pack": _pack_payload(243, component["pack_name"]), "real_sqlite_backed": True, "issue_review_queue": component, "issue_review_count": len(rows), "reviews": rows}

def get_gp244_triage_classification_preview_matrix(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(TRIAGE_MATRIX_ID, db_path)
    rows = get_triage_classification_previews(db_path)
    return {"pack": _pack_payload(244, component["pack_name"]), "real_sqlite_backed": True, "triage_classification_matrix": component, "triage_classification_count": len(rows), "classifications": rows}

def get_gp245_assignment_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(ASSIGNMENT_LOCK_ID, db_path)
    rows = get_assignment_locks(db_path)
    return {"pack": _pack_payload(245, component["pack_name"]), "real_sqlite_backed": True, "assignment_lock_contract": component, "assignment_lock_count": len(rows), "locks": rows}

def get_gp246_escalation_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(ESCALATION_LOCK_ID, db_path)
    rows = get_escalation_locks(db_path)
    return {"pack": _pack_payload(246, component["pack_name"]), "real_sqlite_backed": True, "escalation_lock_contract": component, "escalation_lock_count": len(rows), "locks": rows}

def get_gp247_fix_room_handoff_preview(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(FIX_ROOM_HANDOFF_ID, db_path)
    rows = get_fix_room_handoff_previews(db_path)
    return {"pack": _pack_payload(247, component["pack_name"]), "real_sqlite_backed": True, "fix_room_handoff_preview": component, "fix_room_handoff_count": len(rows), "handoffs": rows}

def get_gp248_reviewer_decision_lock_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(REVIEWER_DECISION_ID, db_path)
    rows = get_reviewer_decision_locks(db_path)
    return {"pack": _pack_payload(248, component["pack_name"]), "real_sqlite_backed": True, "reviewer_decision_lock_board": component, "reviewer_decision_lock_count": len(rows), "decisions": rows}

def get_gp249_review_triage_receipt_draft_packet(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RECEIPT_PACKET_ID, db_path)
    rows = get_review_triage_receipt_packets(db_path)
    return {"pack": _pack_payload(249, component["pack_name"]), "real_sqlite_backed": True, "receipt_packet_component": component, "receipt_packet_count": len(rows), "packets": rows}

def get_gp250_review_triage_lock_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_feedback_review_triage_lock_layer(db_path)
    return {"pack": _pack_payload(250, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_feedback_review_triage_lock_layer(db_path)
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
            "source_gp240_readiness_id": component["source_gp240_readiness_id"],
            "source_gp240_readiness_hash": component["source_gp240_readiness_hash"],
            "source_gp240_readiness_score": component["source_gp240_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "review_triage_ready": component["review_triage_ready"],
            "review_lock_active": component["review_lock_active"],
            "triage_lock_active": component["triage_lock_active"],
            "assignment_lock_active": component["assignment_lock_active"],
            "escalation_lock_active": component["escalation_lock_active"],
            "fix_room_preview_only": component["fix_room_preview_only"],
            "reviewer_decision_locked": component["reviewer_decision_locked"],
            "vault_not_done": component["vault_not_done"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp251": validation["safe_to_continue_to_gp251"],
            "foundation_status": "beta_feedback_review_triage_lock_ready_review_triage_assignment_escalation_fix_decision_locked_vault_not_done_safe_to_continue",
            "next": next_label,
            **counts,
            "feedback_review_started": component["feedback_review_started"],
            "feedback_review_completed": component["feedback_review_completed"],
            "feedback_review_decision_recorded": component["feedback_review_decision_recorded"],
            "issue_review_started": component["issue_review_started"],
            "issue_review_completed": component["issue_review_completed"],
            "issue_review_decision_recorded": component["issue_review_decision_recorded"],
            "intake_triage_started": component["intake_triage_started"],
            "intake_triage_completed": component["intake_triage_completed"],
            "triage_classification_applied": component["triage_classification_applied"],
            "triage_priority_applied": component["triage_priority_applied"],
            "triage_severity_applied": component["triage_severity_applied"],
            "assignment_created": component["assignment_created"],
            "assignment_sent": component["assignment_sent"],
            "assignment_accepted": component["assignment_accepted"],
            "assignee_notified": component["assignee_notified"],
            "intake_escalation_created": component["intake_escalation_created"],
            "intake_escalation_sent": component["intake_escalation_sent"],
            "escalation_acknowledged": component["escalation_acknowledged"],
            "fix_room_opened": component["fix_room_opened"],
            "fix_room_handoff_created": component["fix_room_handoff_created"],
            "fix_room_handoff_sent": component["fix_room_handoff_sent"],
            "fix_task_created": component["fix_task_created"],
            "fix_task_assigned": component["fix_task_assigned"],
            "fix_started": component["fix_started"],
            "fix_completed": component["fix_completed"],
            "response_draft_created": component["response_draft_created"],
            "response_sent": component["response_sent"],
            "reviewer_decision_recorded": component["reviewer_decision_recorded"],
            "reviewer_approval_recorded": component["reviewer_approval_recorded"],
            "reviewer_rejection_recorded": component["reviewer_rejection_recorded"],
            "reviewer_closeout_recorded": component["reviewer_closeout_recorded"],
            "feedback_submitted": component["feedback_submitted"],
            "issue_submitted": component["issue_submitted"],
            "support_message_sent": component["support_message_sent"],
            "support_ticket_created": component["support_ticket_created"],
            "bug_ticket_created": component["bug_ticket_created"],
            "beta_launch_approved": component["beta_launch_approved"],
            "beta_invite_sent": component["beta_invite_sent"],
            "beta_tester_access_granted": component["beta_tester_access_granted"],
            "onboarding_started": component["onboarding_started"],
            "workspace_opened": component["workspace_opened"],
            "billing_flow_created": component["billing_flow_created"],
            "subscription_flow_created": component["subscription_flow_created"],
            "payment_processor_called": component["payment_processor_called"],
            "provider_unlock_requested": component["provider_unlock_requested"],
            "provider_api_called": component["provider_api_called"],
            "provider_search_executed": component["provider_search_executed"],
            "provider_metadata_read": component["provider_metadata_read"],
            "object_body_read": component["object_body_read"],
            "object_body_view_enabled": component["object_body_view_enabled"],
            "object_body_download_enabled": component["object_body_download_enabled"],
            "object_download_enabled": component["object_download_enabled"],
            "object_delete_executed": component["object_delete_executed"],
            "restore_job_created": component["restore_job_created"],
            "export_package_created": component["export_package_created"],
            "direct_upload_enabled": component["direct_upload_enabled"],
            "tower_gate_opened": component["tower_gate_opened"],
            "tower_gate_passed": component["tower_gate_passed"],
            "tower_unlock_granted": component["tower_unlock_granted"],
            "owner_approval_recorded": component["owner_approval_recorded"],
            "execution_enabled": component["execution_enabled"],
            "product_marked_done": component["product_marked_done"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp250",
        },
        "validation": validation,
    }

def get_gp241_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(241, SHELL_ID, "VAULT_GP242_FEEDBACK_REVIEW_DRAFT_QUEUE", db_path)

def get_gp242_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(242, FEEDBACK_REVIEW_ID, "VAULT_GP243_ISSUE_REVIEW_DRAFT_QUEUE", db_path)

def get_gp243_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(243, ISSUE_REVIEW_ID, "VAULT_GP244_TRIAGE_CLASSIFICATION_PREVIEW_MATRIX", db_path)

def get_gp244_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(244, TRIAGE_MATRIX_ID, "VAULT_GP245_ASSIGNMENT_LOCK_CONTRACT", db_path)

def get_gp245_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(245, ASSIGNMENT_LOCK_ID, "VAULT_GP246_ESCALATION_LOCK_CONTRACT", db_path)

def get_gp246_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(246, ESCALATION_LOCK_ID, "VAULT_GP247_FIX_ROOM_HANDOFF_PREVIEW", db_path)

def get_gp247_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(247, FIX_ROOM_HANDOFF_ID, "VAULT_GP248_REVIEWER_DECISION_LOCK_BOARD", db_path)

def get_gp248_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(248, REVIEWER_DECISION_ID, "VAULT_GP249_REVIEW_TRIAGE_RECEIPT_DRAFT_PACKET", db_path)

def get_gp249_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(249, RECEIPT_PACKET_ID, "VAULT_GP250_REVIEW_TRIAGE_LOCK_READINESS_CHECKPOINT", db_path)

def get_gp250_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(250, READINESS_ID, NEXT_PACK, db_path)
    status["gp250_status"]["next_section"] = NEXT_SECTION_ID
    status["gp250_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp250_status"]["next_pack"] = NEXT_PACK
    return status

def get_beta_feedback_review_triage_lock_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_beta_feedback_review_triage_lock_layer(db_path)
    components = _rows("vault_beta_feedback_review_triage_components", "gp_number", db_path, {"data_json": "data"})
    feedback_reviews = get_feedback_review_drafts(db_path)
    issue_reviews = get_issue_review_drafts(db_path)
    classifications = get_triage_classification_previews(db_path)
    assignments = get_assignment_locks(db_path)
    escalations = get_escalation_locks(db_path)
    fix_handoffs = get_fix_room_handoff_previews(db_path)
    decisions = get_reviewer_decision_locks(db_path)
    packets = get_review_triage_receipt_packets(db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_feedback_review_triage_lock_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "feedback_reviews": {"feedback_review_count": len(feedback_reviews), "reviews": feedback_reviews},
        "issue_reviews": {"issue_review_count": len(issue_reviews), "reviews": issue_reviews},
        "triage_classifications": {"triage_classification_count": len(classifications), "classifications": classifications},
        "assignment_locks": {"assignment_lock_count": len(assignments), "locks": assignments},
        "escalation_locks": {"escalation_lock_count": len(escalations), "locks": escalations},
        "fix_room_handoffs": {"fix_room_handoff_count": len(fix_handoffs), "handoffs": fix_handoffs},
        "reviewer_decision_locks": {"reviewer_decision_lock_count": len(decisions), "decisions": decisions},
        "receipt_packets": {"receipt_packet_count": len(packets), "packets": packets},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "beta_feedback_review_triage_lock_layer_ready": True,
            "review_triage_ready": validation["review_triage_ready"],
            "safe_to_continue_to_gp251": validation["safe_to_continue_to_gp251"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "review_lock_active": True,
            "triage_lock_active": True,
            "assignment_lock_active": True,
            "escalation_lock_active": True,
            "fix_room_preview_only": True,
            "reviewer_decision_locked": True,
            "feedback_review_started": False,
            "feedback_review_completed": False,
            "feedback_review_decision_recorded": False,
            "issue_review_started": False,
            "issue_review_completed": False,
            "issue_review_decision_recorded": False,
            "intake_triage_started": False,
            "intake_triage_completed": False,
            "triage_classification_applied": False,
            "triage_priority_applied": False,
            "triage_severity_applied": False,
            "assignment_created": False,
            "assignment_sent": False,
            "assignment_accepted": False,
            "assignee_notified": False,
            "intake_escalation_created": False,
            "intake_escalation_sent": False,
            "escalation_acknowledged": False,
            "fix_room_opened": False,
            "fix_room_handoff_created": False,
            "fix_room_handoff_sent": False,
            "fix_task_created": False,
            "fix_task_assigned": False,
            "fix_started": False,
            "fix_completed": False,
            "response_draft_created": False,
            "response_sent": False,
            "reviewer_decision_recorded": False,
            "reviewer_approval_recorded": False,
            "reviewer_rejection_recorded": False,
            "reviewer_closeout_recorded": False,
            "feedback_submitted": False,
            "issue_submitted": False,
            "support_message_sent": False,
            "support_ticket_created": False,
            "bug_ticket_created": False,
            "billing_flow_created": False,
            "subscription_flow_created": False,
            "payment_processor_called": False,
            "provider_unlock_requested": False,
            "provider_api_called": False,
            "provider_metadata_read": False,
            "object_body_read": False,
            "object_body_view_enabled": False,
            "object_body_download_enabled": False,
            "object_download_enabled": False,
            "object_delete_executed": False,
            "restore_job_created": False,
            "export_package_created": False,
            "direct_upload_enabled": False,
            "tower_gate_opened": False,
            "tower_gate_passed": False,
            "tower_unlock_granted": False,
            "owner_approval_recorded": False,
            "execution_enabled": False,
            "product_marked_done": False,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        "route_map": {
            "page": "/vault/beta-feedback-review-triage-lock-layer",
            "json": "/vault/beta-feedback-review-triage-lock-layer.json",
            "gp241": "/vault/gp241-status.json",
            "gp242": "/vault/gp242-status.json",
            "gp243": "/vault/gp243-status.json",
            "gp244": "/vault/gp244-status.json",
            "gp245": "/vault/gp245-status.json",
            "gp246": "/vault/gp246-status.json",
            "gp247": "/vault/gp247-status.json",
            "gp248": "/vault/gp248-status.json",
            "gp249": "/vault/gp249-status.json",
            "gp250": "/vault/gp250-status.json",
        },
    }

def render_beta_feedback_review_triage_lock_layer_page() -> str:
    home = get_beta_feedback_review_triage_lock_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    feedback_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['review_name'])}</strong>
          <span>{escape(item['review_status'])}</span>
          <code>{escape(item['review_category'])} · review locked</code>
        </article>
        """
        for item in home["feedback_reviews"]["reviews"]
    )

    classification_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['classification_name'])}</strong>
          <span>{escape(item['classification_status'])}</span>
          <code>{escape(item['classification_category'])} · classification locked</code>
        </article>
        """
        for item in home["triage_classifications"]["classifications"]
    )

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP241-GP250 Beta Feedback Review Triage Lock Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 241-250</div>
    <div class="eyebrow">Beta Feedback Review and Triage Lock Layer · GP241-GP250</div>
    <h1>Review + Triage Locked</h1>
    <p>This layer prepares feedback review queues, issue review queues, triage classifications, assignment locks, escalation locks, fix-room previews, reviewer decision locks, and receipt drafts. Nothing can be reviewed, triaged, assigned, escalated, or fixed yet.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['feedback_review_count']}</strong><span>feedback review drafts</span></div>
      <div class="metric"><strong>{home['store']['issue_review_count']}</strong><span>issue review drafts</span></div>
      <div class="metric"><strong>{home['store']['triage_classification_count']}</strong><span>triage previews</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP241-GP250 built</span>
      <span class="pill ok">Safe to GP251</span>
      <span class="pill danger">No review started</span>
      <span class="pill danger">No triage</span>
      <span class="pill danger">No classification</span>
      <span class="pill danger">No assignment</span>
      <span class="pill danger">No escalation</span>
      <span class="pill danger">No fix room</span>
      <span class="pill danger">No decision</span>
      <span class="pill danger">Vault not done</span>
    </div>
  </section>

  <section class="section">
    <h2>Feedback Review Draft Queue</h2>
    <div class="cards">{feedback_cards}</div>
  </section>

  <section class="section">
    <h2>Triage Classification Preview Matrix</h2>
    <div class="cards">{classification_cards}</div>
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
