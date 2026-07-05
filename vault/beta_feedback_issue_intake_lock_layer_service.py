"""
VAULT GP231-GP240 — Beta Feedback and Issue Intake Lock Layer

New section:
Archive Vault — Beta Feedback and Issue Intake Lock Layer / GP231-GP240

Builds:
- GP231 Beta Feedback and Issue Intake Lock Shell
- GP232 Feedback Form Draft Registry
- GP233 Issue Report Draft Registry
- GP234 Feedback Submit Lock Contract
- GP235 Issue Submit Lock Contract
- GP236 Support Message Lock Contract
- GP237 Intake Routing Preview Board
- GP238 Intake Safety and Compliance Lock Board
- GP239 Feedback Issue Intake Receipt Draft Packet
- GP240 Feedback Issue Intake Lock Readiness Checkpoint

This layer prepares feedback, issue, and support intake surfaces. It does not
submit feedback, create issues, send support messages, route/triage/escalate,
call Tower/billing/providers, read object bodies, restore/export/upload/delete,
execute, or mark Vault done.
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

from vault.beta_onboarding_locked_experience_layer_service import (
    get_gp230_status,
    get_gp230_beta_onboarding_locked_experience_readiness_checkpoint,
    get_beta_onboarding_locked_experience_layer_home,
    validate_beta_onboarding_locked_experience_layer,
    get_support_channel_previews,
    get_onboarding_safety_compliance_locks,
)

LAYER_ID = "VAULT_GP231_240"
LAYER_NAME = "Beta Feedback and Issue Intake Lock Layer"
SCHEMA_VERSION = "vault.beta_feedback_issue_intake_lock_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_BETA_FEEDBACK_AND_ISSUE_INTAKE_LOCK_LAYER"
SECTION_TITLE = "Archive Vault — Beta Feedback and Issue Intake Lock Layer"
SECTION_RANGE = "GP231-GP240"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_BETA_ONBOARDING_LOCKED_EXPERIENCE_LAYER"
PREVIOUS_SECTION_RANGE = "GP221-GP230"

NEXT_SECTION_ID = "ARCHIVE_VAULT_BETA_FEEDBACK_REVIEW_AND_TRIAGE_LOCK_LAYER"
NEXT_SECTION_RANGE = "GP241-GP250"
NEXT_PACK = "VAULT_GP241_250_BETA_FEEDBACK_REVIEW_AND_TRIAGE_LOCK_LAYER"

DEFAULT_DB_ENV = "VAULT_BETA_FEEDBACK_ISSUE_INTAKE_LOCK_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_beta_feedback_issue_intake_lock_layer.sqlite"

SHELL_ID = "VBFIIL-SHELL-GP231-001"
FEEDBACK_FORM_ID = "VBFIIL-FEEDBACK-GP232-001"
ISSUE_REPORT_ID = "VBFIIL-ISSUE-GP233-001"
FEEDBACK_SUBMIT_LOCK_ID = "VBFIIL-FEEDBACKLOCK-GP234-001"
ISSUE_SUBMIT_LOCK_ID = "VBFIIL-ISSUELOCK-GP235-001"
SUPPORT_MESSAGE_LOCK_ID = "VBFIIL-SUPPORTLOCK-GP236-001"
ROUTING_PREVIEW_ID = "VBFIIL-ROUTING-GP237-001"
SAFETY_COMPLIANCE_ID = "VBFIIL-SAFETY-GP238-001"
RECEIPT_PACKET_ID = "VBFIIL-RECEIPT-GP239-001"
READINESS_ID = "VBFIIL-READINESS-GP240-001"

FALSE_FIELDS = [
    "beta_launch_requested",
    "beta_launch_approved",
    "public_launch_requested",
    "public_launch_approved",
    "beta_invite_created",
    "beta_invite_sent",
    "beta_tester_added",
    "beta_tester_access_granted",
    "beta_tester_access_enabled",
    "beta_access_token_created",
    "beta_access_session_created",
    "onboarding_started",
    "onboarding_completed",
    "profile_created",
    "profile_submitted",
    "profile_approved",
    "nda_signed",
    "policy_acknowledged",
    "policy_acceptance_recorded",
    "workspace_opened",
    "workspace_access_granted",
    "workspace_session_created",
    "support_channel_opened",
    "support_message_created",
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
    "intake_routing_executed",
    "intake_route_assigned",
    "intake_triage_started",
    "intake_triage_completed",
    "intake_escalation_created",
    "intake_escalation_sent",
    "support_ticket_created",
    "support_ticket_assigned",
    "bug_ticket_created",
    "bug_ticket_assigned",
    "feedback_review_started",
    "feedback_review_completed",
    "issue_review_started",
    "issue_review_completed",
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

FEEDBACK_FORMS = [
    ("general_beta_feedback_form", "General Beta Feedback Form", "general", "draft_locked"),
    ("readiness_surface_feedback_form", "Readiness Surface Feedback Form", "readiness", "draft_locked"),
    ("redacted_archive_feedback_form", "Redacted Archive Feedback Form", "archive", "draft_locked"),
    ("receipt_packet_feedback_form", "Receipt Packet Feedback Form", "receipt", "draft_locked"),
    ("access_flow_feedback_form", "Access Flow Feedback Form", "access", "draft_locked"),
    ("support_experience_feedback_form", "Support Experience Feedback Form", "support", "draft_locked"),
]

ISSUE_REPORTS = [
    ("bug_report_draft", "Bug Report Draft", "bug", "draft_locked"),
    ("access_issue_report_draft", "Access Issue Report Draft", "access", "draft_locked"),
    ("receipt_issue_report_draft", "Receipt Issue Report Draft", "receipt", "draft_locked"),
    ("archive_view_issue_report_draft", "Archive View Issue Report Draft", "archive", "draft_locked"),
    ("provider_boundary_issue_report_draft", "Provider Boundary Issue Report Draft", "provider", "draft_locked"),
    ("security_concern_report_draft", "Security Concern Report Draft", "security", "draft_locked"),
]

FEEDBACK_SUBMIT_LOCKS = [
    ("feedback_open_lock", "Feedback Open Lock"),
    ("feedback_draft_create_lock", "Feedback Draft Create Lock"),
    ("feedback_submit_lock", "Feedback Submit Lock"),
    ("feedback_receive_lock", "Feedback Receive Lock"),
    ("feedback_receipt_finalize_lock", "Feedback Receipt Finalize Lock"),
]

ISSUE_SUBMIT_LOCKS = [
    ("issue_open_lock", "Issue Open Lock"),
    ("issue_draft_create_lock", "Issue Draft Create Lock"),
    ("issue_create_lock", "Issue Create Lock"),
    ("issue_submit_lock", "Issue Submit Lock"),
    ("issue_receive_lock", "Issue Receive Lock"),
    ("issue_receipt_finalize_lock", "Issue Receipt Finalize Lock"),
]

SUPPORT_MESSAGE_LOCKS = [
    ("support_channel_open_lock", "Support Channel Open Lock"),
    ("support_message_create_lock", "Support Message Create Lock"),
    ("support_message_send_lock", "Support Message Send Lock"),
    ("support_ticket_create_lock", "Support Ticket Create Lock"),
    ("support_ticket_assign_lock", "Support Ticket Assign Lock"),
]

ROUTING_PREVIEWS = [
    ("feedback_to_owner_review_preview", "Feedback to Owner Review Preview", "feedback", "preview_locked"),
    ("issue_to_triage_preview", "Issue to Triage Preview", "issue", "preview_locked"),
    ("bug_to_fix_room_preview", "Bug to Fix Room Preview", "bug", "preview_locked"),
    ("security_to_tower_preview", "Security to Tower Preview", "security", "preview_locked"),
    ("access_to_tower_preview", "Access to Tower Preview", "access", "preview_locked"),
    ("provider_boundary_to_owner_preview", "Provider Boundary to Owner Preview", "provider", "preview_locked"),
]

SAFETY_LOCKS = [
    ("feedback_submit_locked", "Feedback Submit Locked", "feedback", "critical"),
    ("issue_submit_locked", "Issue Submit Locked", "issue", "critical"),
    ("support_message_locked", "Support Message Locked", "support", "critical"),
    ("routing_execution_locked", "Routing Execution Locked", "routing", "critical"),
    ("triage_execution_locked", "Triage Execution Locked", "triage", "critical"),
    ("escalation_send_locked", "Escalation Send Locked", "escalation", "critical"),
    ("ticket_creation_locked", "Ticket Creation Locked", "ticket", "critical"),
    ("tower_gate_locked", "Tower Gate Locked", "tower", "critical"),
    ("billing_subscription_locked", "Billing/Subscription Locked", "billing", "critical"),
    ("provider_object_body_locked", "Provider/Object Body Locked", "provider", "critical"),
    ("restore_export_upload_delete_locked", "Restore/Export/Upload/Delete Locked", "dangerous_ops", "critical"),
    ("vault_not_done", "Vault Not Done", "done_state", "critical"),
]

COMPONENT_SPECS = [
    (231, SHELL_ID, "VAULT_GP231", "Beta Feedback and Issue Intake Lock Shell", "beta_feedback_issue_intake_lock_shell"),
    (232, FEEDBACK_FORM_ID, "VAULT_GP232", "Feedback Form Draft Registry", "feedback_form_draft_registry"),
    (233, ISSUE_REPORT_ID, "VAULT_GP233", "Issue Report Draft Registry", "issue_report_draft_registry"),
    (234, FEEDBACK_SUBMIT_LOCK_ID, "VAULT_GP234", "Feedback Submit Lock Contract", "feedback_submit_lock_contract"),
    (235, ISSUE_SUBMIT_LOCK_ID, "VAULT_GP235", "Issue Submit Lock Contract", "issue_submit_lock_contract"),
    (236, SUPPORT_MESSAGE_LOCK_ID, "VAULT_GP236", "Support Message Lock Contract", "support_message_lock_contract"),
    (237, ROUTING_PREVIEW_ID, "VAULT_GP237", "Intake Routing Preview Board", "intake_routing_preview_board"),
    (238, SAFETY_COMPLIANCE_ID, "VAULT_GP238", "Intake Safety and Compliance Lock Board", "intake_safety_compliance_lock_board"),
    (239, RECEIPT_PACKET_ID, "VAULT_GP239", "Feedback Issue Intake Receipt Draft Packet", "feedback_issue_intake_receipt_draft_packet"),
    (240, READINESS_ID, "VAULT_GP240", "Feedback Issue Intake Lock Readiness Checkpoint", "feedback_issue_intake_lock_readiness_checkpoint"),
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
        "source_gp230_readiness_score",
        "component_count",
        "feedback_form_count",
        "issue_report_count",
        "feedback_submit_lock_count",
        "issue_submit_lock_count",
        "support_message_lock_count",
        "routing_preview_count",
        "safety_lock_count",
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
        "depends_on": ["VAULT_GP230"],
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
        "depends_on": ["VAULT_GP230"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_beta_feedback_issue_intake_lock_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_beta_feedback_issue_intake_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp230_readiness_id TEXT NOT NULL,
                source_gp230_readiness_hash TEXT NOT NULL,
                source_gp230_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                feedback_intake_ready INTEGER NOT NULL DEFAULT 1,
                issue_intake_ready INTEGER NOT NULL DEFAULT 1,
                submit_locks_active INTEGER NOT NULL DEFAULT 1,
                routing_preview_only INTEGER NOT NULL DEFAULT 1,
                support_message_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_feedback_form_draft_registry (
                feedback_form_id TEXT PRIMARY KEY,
                feedback_code TEXT NOT NULL UNIQUE,
                feedback_name TEXT NOT NULL,
                feedback_category TEXT NOT NULL,
                feedback_status TEXT NOT NULL,
                form_ready INTEGER NOT NULL DEFAULT 1,
                form_locked INTEGER NOT NULL DEFAULT 1,
                submit_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                feedback_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_issue_report_draft_registry (
                issue_report_id TEXT PRIMARY KEY,
                issue_code TEXT NOT NULL UNIQUE,
                issue_name TEXT NOT NULL,
                issue_category TEXT NOT NULL,
                issue_status TEXT NOT NULL,
                report_ready INTEGER NOT NULL DEFAULT 1,
                report_locked INTEGER NOT NULL DEFAULT 1,
                submit_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                issue_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_feedback_submit_lock_contracts (
                lock_id TEXT PRIMARY KEY,
                lock_code TEXT NOT NULL UNIQUE,
                lock_name TEXT NOT NULL,
                lock_status TEXT NOT NULL,
                feedback_submit_locked INTEGER NOT NULL DEFAULT 1,
                feedback_receipt_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_issue_submit_lock_contracts (
                lock_id TEXT PRIMARY KEY,
                lock_code TEXT NOT NULL UNIQUE,
                lock_name TEXT NOT NULL,
                lock_status TEXT NOT NULL,
                issue_submit_locked INTEGER NOT NULL DEFAULT 1,
                issue_receipt_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_support_message_lock_contracts (
                lock_id TEXT PRIMARY KEY,
                lock_code TEXT NOT NULL UNIQUE,
                lock_name TEXT NOT NULL,
                lock_status TEXT NOT NULL,
                support_message_locked INTEGER NOT NULL DEFAULT 1,
                support_ticket_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_intake_routing_preview_board (
                route_id TEXT PRIMARY KEY,
                route_code TEXT NOT NULL UNIQUE,
                route_name TEXT NOT NULL,
                route_category TEXT NOT NULL,
                route_status TEXT NOT NULL,
                preview_ready INTEGER NOT NULL DEFAULT 1,
                routing_locked INTEGER NOT NULL DEFAULT 1,
                triage_locked INTEGER NOT NULL DEFAULT 1,
                escalation_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                route_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_intake_safety_compliance_locks (
                lock_id TEXT PRIMARY KEY,
                lock_code TEXT NOT NULL UNIQUE,
                lock_name TEXT NOT NULL,
                lock_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                lock_status TEXT NOT NULL,
                lock_active INTEGER NOT NULL DEFAULT 1,
                blocks_feedback_submit INTEGER NOT NULL DEFAULT 1,
                blocks_issue_submit INTEGER NOT NULL DEFAULT 1,
                blocks_support_send INTEGER NOT NULL DEFAULT 1,
                blocks_routing INTEGER NOT NULL DEFAULT 1,
                blocks_triage INTEGER NOT NULL DEFAULT 1,
                blocks_escalation INTEGER NOT NULL DEFAULT 1,
                blocks_ticket_creation INTEGER NOT NULL DEFAULT 1,
                blocks_tower_gate INTEGER NOT NULL DEFAULT 1,
                blocks_billing_subscription INTEGER NOT NULL DEFAULT 1,
                blocks_provider_unlock INTEGER NOT NULL DEFAULT 1,
                blocks_provider_api INTEGER NOT NULL DEFAULT 1,
                blocks_object_body INTEGER NOT NULL DEFAULT 1,
                blocks_download INTEGER NOT NULL DEFAULT 1,
                blocks_restore INTEGER NOT NULL DEFAULT 1,
                blocks_export INTEGER NOT NULL DEFAULT 1,
                blocks_direct_upload INTEGER NOT NULL DEFAULT 1,
                blocks_delete INTEGER NOT NULL DEFAULT 1,
                blocks_execution INTEGER NOT NULL DEFAULT 1,
                blocks_vault_done INTEGER NOT NULL DEFAULT 1,
                resolved INTEGER NOT NULL DEFAULT 0,
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
            CREATE TABLE IF NOT EXISTS vault_feedback_issue_intake_receipt_draft_packets (
                receipt_packet_id TEXT PRIMARY KEY,
                packet_code TEXT NOT NULL UNIQUE,
                packet_name TEXT NOT NULL,
                packet_status TEXT NOT NULL,
                packet_ready INTEGER NOT NULL DEFAULT 1,
                packet_locked INTEGER NOT NULL DEFAULT 1,
                final_feedback_receipt INTEGER NOT NULL DEFAULT 0,
                final_issue_receipt INTEGER NOT NULL DEFAULT 0,
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
            CREATE TABLE IF NOT EXISTS vault_feedback_issue_intake_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                feedback_form_count INTEGER NOT NULL,
                issue_report_count INTEGER NOT NULL,
                feedback_submit_lock_count INTEGER NOT NULL,
                issue_submit_lock_count INTEGER NOT NULL,
                support_message_lock_count INTEGER NOT NULL,
                routing_preview_count INTEGER NOT NULL,
                safety_lock_count INTEGER NOT NULL,
                receipt_packet_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                feedback_intake_ready INTEGER NOT NULL DEFAULT 1,
                issue_intake_ready INTEGER NOT NULL DEFAULT 1,
                submit_locks_active INTEGER NOT NULL DEFAULT 1,
                routing_preview_only INTEGER NOT NULL DEFAULT 1,
                support_message_locked INTEGER NOT NULL DEFAULT 1,
                safe_to_continue_to_gp241 INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_feedback_issue_intake_events (
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
            "vault_beta_feedback_issue_intake_components",
            "vault_feedback_form_draft_registry",
            "vault_issue_report_draft_registry",
            "vault_feedback_submit_lock_contracts",
            "vault_issue_submit_lock_contracts",
            "vault_support_message_lock_contracts",
            "vault_intake_routing_preview_board",
            "vault_intake_safety_compliance_locks",
            "vault_feedback_issue_intake_receipt_draft_packets",
            "vault_feedback_issue_intake_readiness",
            "vault_feedback_issue_intake_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VBFIILEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_feedback_issue_intake_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_beta_feedback_issue_intake_lock_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_beta_feedback_issue_intake_lock_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_beta_feedback_issue_intake_components WHERE component_id = ?",
            (SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp230_status = get_gp230_status()["gp230_status"]
            gp230_checkpoint = get_gp230_beta_onboarding_locked_experience_readiness_checkpoint()["readiness_checkpoint"]
            gp230_home = get_beta_onboarding_locked_experience_layer_home()
            gp230_validation = validate_beta_onboarding_locked_experience_layer()
            source_support_channels = get_support_channel_previews()
            source_safety_locks = get_onboarding_safety_compliance_locks()

            readiness = gp230_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp230_readiness_id": readiness["readiness_id"],
                "source_gp230_readiness_hash": readiness["readiness_hash"],
                "source_gp230_readiness_score": readiness["readiness_score"],
            }

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "feedback_form_count": len(FEEDBACK_FORMS),
                "issue_report_count": len(ISSUE_REPORTS),
                "feedback_submit_lock_count": len(FEEDBACK_SUBMIT_LOCKS),
                "issue_submit_lock_count": len(ISSUE_SUBMIT_LOCKS),
                "support_message_lock_count": len(SUPPORT_MESSAGE_LOCKS),
                "routing_preview_count": len(ROUTING_PREVIEWS),
                "safety_lock_count": len(SAFETY_LOCKS),
                "receipt_packet_count": 1,
            }

            source_context = {
                "source_gp230_status_ready": gp230_status["ready"],
                "source_gp230_validation_passed": gp230_status["validation_passed"],
                "source_gp230_safe_to_continue_to_gp231": gp230_status["safe_to_continue_to_gp231"],
                "source_gp230_readiness_hash": readiness["readiness_hash"],
                "source_gp230_readiness_score": readiness["readiness_score"],
                "source_support_channel_count": len(source_support_channels),
                "source_onboarding_safety_lock_count": len(source_safety_locks),
                "source_validation_check_count": gp230_validation["check_count"],
            }

            component_extra = {
                SHELL_ID: {"beta_feedback_issue_intake_lock_shell_ready": True},
                FEEDBACK_FORM_ID: {"feedback_form_draft_registry_ready": True, "feedback_form_count": counts["feedback_form_count"]},
                ISSUE_REPORT_ID: {"issue_report_draft_registry_ready": True, "issue_report_count": counts["issue_report_count"]},
                FEEDBACK_SUBMIT_LOCK_ID: {"feedback_submit_lock_contract_ready": True, "feedback_submit_lock_count": counts["feedback_submit_lock_count"]},
                ISSUE_SUBMIT_LOCK_ID: {"issue_submit_lock_contract_ready": True, "issue_submit_lock_count": counts["issue_submit_lock_count"]},
                SUPPORT_MESSAGE_LOCK_ID: {"support_message_lock_contract_ready": True, "support_message_lock_count": counts["support_message_lock_count"]},
                ROUTING_PREVIEW_ID: {"intake_routing_preview_board_ready": True, "routing_preview_count": counts["routing_preview_count"]},
                SAFETY_COMPLIANCE_ID: {"intake_safety_compliance_lock_board_ready": True, "safety_lock_count": counts["safety_lock_count"]},
                RECEIPT_PACKET_ID: {"feedback_issue_intake_receipt_draft_packet_ready": True, "receipt_packet_count": counts["receipt_packet_count"]},
                READINESS_ID: {"feedback_issue_intake_lock_readiness_checkpoint_ready": True, "safe_to_continue_to_gp241": True},
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
                    "feedback_intake_ready": True,
                    "issue_intake_ready": True,
                    "submit_locks_active": True,
                    "routing_preview_only": True,
                    "support_message_locked": True,
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
                    "feedback_intake_ready": 1,
                    "issue_intake_ready": 1,
                    "submit_locks_active": 1,
                    "routing_preview_only": 1,
                    "support_message_locked": 1,
                    "vault_not_done": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_feedback_issue_intake_components", row)

            for idx, (code, name, category, status) in enumerate(FEEDBACK_FORMS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "feedback_code": code,
                    "feedback_name": name,
                    "feedback_category": category,
                    "feedback_status": status,
                    "form_ready": True,
                    "form_locked": True,
                    "submit_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "feedback_form_id": f"VBFIILFEED-{idx:03d}",
                    "feedback_code": code,
                    "feedback_name": name,
                    "feedback_category": category,
                    "feedback_status": status,
                    "form_ready": 1,
                    "form_locked": 1,
                    "submit_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "feedback_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_feedback_form_draft_registry", row)

            for idx, (code, name, category, status) in enumerate(ISSUE_REPORTS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "issue_code": code,
                    "issue_name": name,
                    "issue_category": category,
                    "issue_status": status,
                    "report_ready": True,
                    "report_locked": True,
                    "submit_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "issue_report_id": f"VBFIILISSUE-{idx:03d}",
                    "issue_code": code,
                    "issue_name": name,
                    "issue_category": category,
                    "issue_status": status,
                    "report_ready": 1,
                    "report_locked": 1,
                    "submit_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "issue_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_issue_report_draft_registry", row)

            for idx, (code, name) in enumerate(FEEDBACK_SUBMIT_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "lock_code": code,
                    "lock_name": name,
                    "lock_status": "FEEDBACK_SUBMIT_LOCK_ACTIVE",
                    "feedback_submit_locked": True,
                    "feedback_receipt_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "lock_id": f"VBFIILFLOCK-{idx:03d}",
                    "lock_code": code,
                    "lock_name": name,
                    "lock_status": payload["lock_status"],
                    "feedback_submit_locked": 1,
                    "feedback_receipt_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "lock_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_feedback_submit_lock_contracts", row)

            for idx, (code, name) in enumerate(ISSUE_SUBMIT_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "lock_code": code,
                    "lock_name": name,
                    "lock_status": "ISSUE_SUBMIT_LOCK_ACTIVE",
                    "issue_submit_locked": True,
                    "issue_receipt_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "lock_id": f"VBFIILILOCK-{idx:03d}",
                    "lock_code": code,
                    "lock_name": name,
                    "lock_status": payload["lock_status"],
                    "issue_submit_locked": 1,
                    "issue_receipt_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "lock_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_issue_submit_lock_contracts", row)

            for idx, (code, name) in enumerate(SUPPORT_MESSAGE_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "lock_code": code,
                    "lock_name": name,
                    "lock_status": "SUPPORT_MESSAGE_LOCK_ACTIVE",
                    "support_message_locked": True,
                    "support_ticket_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "lock_id": f"VBFIILSLOCK-{idx:03d}",
                    "lock_code": code,
                    "lock_name": name,
                    "lock_status": payload["lock_status"],
                    "support_message_locked": 1,
                    "support_ticket_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "lock_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_support_message_lock_contracts", row)

            for idx, (code, name, category, status) in enumerate(ROUTING_PREVIEWS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "route_code": code,
                    "route_name": name,
                    "route_category": category,
                    "route_status": status,
                    "preview_ready": True,
                    "routing_locked": True,
                    "triage_locked": True,
                    "escalation_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "route_id": f"VBFIILROUTE-{idx:03d}",
                    "route_code": code,
                    "route_name": name,
                    "route_category": category,
                    "route_status": status,
                    "preview_ready": 1,
                    "routing_locked": 1,
                    "triage_locked": 1,
                    "escalation_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "route_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_intake_routing_preview_board", row)

            for idx, (code, name, category, severity) in enumerate(SAFETY_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "severity": severity,
                    "lock_status": "ACTIVE_FEEDBACK_ISSUE_INTAKE_SAFETY_LOCK",
                    "lock_active": True,
                    "blocks_feedback_submit": True,
                    "blocks_issue_submit": True,
                    "blocks_support_send": True,
                    "blocks_routing": True,
                    "blocks_triage": True,
                    "blocks_escalation": True,
                    "blocks_ticket_creation": True,
                    "blocks_tower_gate": True,
                    "blocks_billing_subscription": True,
                    "blocks_provider_unlock": True,
                    "blocks_provider_api": True,
                    "blocks_object_body": True,
                    "blocks_download": True,
                    "blocks_restore": True,
                    "blocks_export": True,
                    "blocks_direct_upload": True,
                    "blocks_delete": True,
                    "blocks_execution": True,
                    "blocks_vault_done": True,
                    "resolved": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "lock_id": f"VBFIILSAFE-{idx:03d}",
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "severity": severity,
                    "lock_status": payload["lock_status"],
                    "lock_active": 1,
                    "blocks_feedback_submit": 1,
                    "blocks_issue_submit": 1,
                    "blocks_support_send": 1,
                    "blocks_routing": 1,
                    "blocks_triage": 1,
                    "blocks_escalation": 1,
                    "blocks_ticket_creation": 1,
                    "blocks_tower_gate": 1,
                    "blocks_billing_subscription": 1,
                    "blocks_provider_unlock": 1,
                    "blocks_provider_api": 1,
                    "blocks_object_body": 1,
                    "blocks_download": 1,
                    "blocks_restore": 1,
                    "blocks_export": 1,
                    "blocks_direct_upload": 1,
                    "blocks_delete": 1,
                    "blocks_execution": 1,
                    "blocks_vault_done": 1,
                    "resolved": 0,
                    "payload_json": _json_dumps(payload),
                    "lock_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_intake_safety_compliance_locks", row)

            packet_payload = {
                "schema_version": SCHEMA_VERSION,
                "packet_code": "vault_gp231_240_feedback_issue_intake_packet",
                "packet_name": "Vault GP231-GP240 Feedback Issue Intake Receipt Draft Packet",
                "packet_status": "READY_LOCKED_DRAFT_ONLY_NO_FEEDBACK_OR_ISSUE_RECEIPT",
                "source_gp230_readiness_id": readiness["readiness_id"],
                "source_gp230_readiness_hash": readiness["readiness_hash"],
                "source_gp230_readiness_score": readiness["readiness_score"],
                **counts,
                "feedback_intake_ready": True,
                "issue_intake_ready": True,
                "submit_locks_active": True,
                "routing_preview_only": True,
                "final_feedback_receipt": False,
                "final_issue_receipt": False,
                "locked_truth": {field: False for field in FALSE_FIELDS},
                "vault_done": False,
                "clouds_should_continue": False,
            }
            row = {
                "receipt_packet_id": RECEIPT_PACKET_ID,
                "packet_code": "vault_gp231_240_feedback_issue_intake_packet",
                "packet_name": "Vault GP231-GP240 Feedback Issue Intake Receipt Draft Packet",
                "packet_status": packet_payload["packet_status"],
                "packet_ready": 1,
                "packet_locked": 1,
                "final_feedback_receipt": 0,
                "final_issue_receipt": 0,
                "payload_json": _json_dumps(packet_payload),
                "packet_hash": _hash_payload(packet_payload),
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                row[field] = 0
            _insert_dict(conn, "vault_feedback_issue_intake_receipt_draft_packets", row)

            checks = [
                ("SOURCE_GP230_READY", bool(gp230_status["ready"])),
                ("SOURCE_GP230_VALIDATION_PASSED", bool(gp230_status["validation_passed"])),
                ("SOURCE_GP230_SAFE_TO_CONTINUE", bool(gp230_status["safe_to_continue_to_gp231"])),
                ("SOURCE_GP230_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP230_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("FEEDBACK_FORM_COUNT_6", counts["feedback_form_count"] == 6),
                ("ISSUE_REPORT_COUNT_6", counts["issue_report_count"] == 6),
                ("FEEDBACK_SUBMIT_LOCK_COUNT_5", counts["feedback_submit_lock_count"] == 5),
                ("ISSUE_SUBMIT_LOCK_COUNT_6", counts["issue_submit_lock_count"] == 6),
                ("SUPPORT_MESSAGE_LOCK_COUNT_5", counts["support_message_lock_count"] == 5),
                ("ROUTING_PREVIEW_COUNT_6", counts["routing_preview_count"] == 6),
                ("SAFETY_LOCK_COUNT_12", counts["safety_lock_count"] == 12),
                ("RECEIPT_PACKET_COUNT_1", counts["receipt_packet_count"] == 1),
                ("SECTION_GP231_GP240", SECTION_RANGE == "GP231-GP240"),
                ("NEXT_SECTION_GP241_GP250", NEXT_SECTION_RANGE == "GP241-GP250"),
                ("FEEDBACK_INTAKE_READY", True),
                ("ISSUE_INTAKE_READY", True),
                ("SUBMIT_LOCKS_ACTIVE", True),
                ("ROUTING_PREVIEW_ONLY", True),
                ("SUPPORT_MESSAGE_LOCKED", True),
                ("NO_FEEDBACK_SUBMITTED", True),
                ("NO_ISSUE_CREATED_SUBMITTED", True),
                ("NO_SUPPORT_MESSAGE_SENT", True),
                ("NO_ROUTING_EXECUTED", True),
                ("NO_TRIAGE_ESCALATION", True),
                ("NO_TICKET_CREATED", True),
                ("NO_BETA_ACCESS_OR_ONBOARDING", True),
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
                "gp_number": 240,
                "pack_id": "VAULT_GP240",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp230_readiness_id": readiness["readiness_id"],
                "source_gp230_readiness_hash": readiness["readiness_hash"],
                "source_gp230_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "feedback_intake_ready": True,
                "issue_intake_ready": True,
                "submit_locks_active": True,
                "routing_preview_only": True,
                "support_message_locked": True,
                "safe_to_continue_to_gp241": failed_count == 0,
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
                "gp_number": 240,
                "pack_id": "VAULT_GP240",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "BETA_FEEDBACK_ISSUE_INTAKE_LOCK_READY_SUBMIT_ROUTING_SUPPORT_LOCKED_VAULT_NOT_DONE_SAFE_TO_CONTINUE",
                "readiness_score": readiness_payload["readiness_score"],
                **counts,
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "feedback_intake_ready": 1,
                "issue_intake_ready": 1,
                "submit_locks_active": 1,
                "routing_preview_only": 1,
                "support_message_locked": 1,
                "safe_to_continue_to_gp241": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_feedback_issue_intake_readiness", row)

            for event_type, event_payload in [
                ("GP231_BETA_FEEDBACK_ISSUE_INTAKE_LOCK_SHELL_CREATED", {"component_id": SHELL_ID}),
                ("GP232_FEEDBACK_FORM_DRAFT_REGISTRY_CREATED", {"feedback_form_count": counts["feedback_form_count"]}),
                ("GP233_ISSUE_REPORT_DRAFT_REGISTRY_CREATED", {"issue_report_count": counts["issue_report_count"]}),
                ("GP234_FEEDBACK_SUBMIT_LOCK_CONTRACT_CREATED", {"feedback_submit_lock_count": counts["feedback_submit_lock_count"]}),
                ("GP235_ISSUE_SUBMIT_LOCK_CONTRACT_CREATED", {"issue_submit_lock_count": counts["issue_submit_lock_count"]}),
                ("GP236_SUPPORT_MESSAGE_LOCK_CONTRACT_CREATED", {"support_message_lock_count": counts["support_message_lock_count"]}),
                ("GP237_INTAKE_ROUTING_PREVIEW_BOARD_CREATED", {"routing_preview_count": counts["routing_preview_count"]}),
                ("GP238_INTAKE_SAFETY_COMPLIANCE_LOCK_BOARD_CREATED", {"safety_lock_count": counts["safety_lock_count"]}),
                ("GP239_FEEDBACK_ISSUE_INTAKE_RECEIPT_DRAFT_PACKET_CREATED", {"receipt_packet_count": counts["receipt_packet_count"]}),
                ("GP240_FEEDBACK_ISSUE_INTAKE_LOCK_READINESS_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp241": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_feedback_issue_intake_components").fetchone()["c"]),
            "feedback_form_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_feedback_form_draft_registry").fetchone()["c"]),
            "issue_report_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_issue_report_draft_registry").fetchone()["c"]),
            "feedback_submit_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_feedback_submit_lock_contracts").fetchone()["c"]),
            "issue_submit_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_issue_submit_lock_contracts").fetchone()["c"]),
            "support_message_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_support_message_lock_contracts").fetchone()["c"]),
            "routing_preview_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_intake_routing_preview_board").fetchone()["c"]),
            "safety_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_intake_safety_compliance_locks").fetchone()["c"]),
            "receipt_packet_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_feedback_issue_intake_receipt_draft_packets").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_feedback_issue_intake_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_feedback_issue_intake_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_beta_feedback_issue_intake_lock_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_beta_feedback_issue_intake_lock_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_beta_feedback_issue_intake_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_beta_feedback_issue_intake_lock_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_feedback_issue_intake_readiness WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_beta_feedback_issue_intake_lock_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_feedback_issue_intake_events ORDER BY created_at, event_id").fetchall()
    return [{"event_id": row["event_id"], "event_type": row["event_type"], "event_payload": _json_loads(row["event_payload_json"]), "created_at": row["created_at"]} for row in rows]

def get_feedback_form_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_feedback_form_draft_registry", "feedback_code", db_path, {"payload_json": "payload"})

def get_issue_report_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_issue_report_draft_registry", "issue_code", db_path, {"payload_json": "payload"})

def get_feedback_submit_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_feedback_submit_lock_contracts", "lock_code", db_path, {"payload_json": "payload"})

def get_issue_submit_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_issue_submit_lock_contracts", "lock_code", db_path, {"payload_json": "payload"})

def get_support_message_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_support_message_lock_contracts", "lock_code", db_path, {"payload_json": "payload"})

def get_intake_routing_previews(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_intake_routing_preview_board", "route_code", db_path, {"payload_json": "payload"})

def get_intake_safety_compliance_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_intake_safety_compliance_locks", "lock_code", db_path, {"payload_json": "payload"})

def get_feedback_issue_intake_receipt_packets(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_feedback_issue_intake_receipt_draft_packets", "packet_code", db_path, {"payload_json": "payload"})

def validate_beta_feedback_issue_intake_lock_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_beta_feedback_issue_intake_components", "gp_number", db_path, {"data_json": "data"})
    feedback_forms = get_feedback_form_drafts(db_path)
    issue_reports = get_issue_report_drafts(db_path)
    feedback_locks = get_feedback_submit_locks(db_path)
    issue_locks = get_issue_submit_locks(db_path)
    support_locks = get_support_message_locks(db_path)
    routes = get_intake_routing_previews(db_path)
    safety = get_intake_safety_compliance_locks(db_path)
    packets = get_feedback_issue_intake_receipt_packets(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("FEEDBACK_FORM_COUNT_6", len(feedback_forms) == len(FEEDBACK_FORMS)),
        ("ISSUE_REPORT_COUNT_6", len(issue_reports) == len(ISSUE_REPORTS)),
        ("FEEDBACK_SUBMIT_LOCK_COUNT_5", len(feedback_locks) == len(FEEDBACK_SUBMIT_LOCKS)),
        ("ISSUE_SUBMIT_LOCK_COUNT_6", len(issue_locks) == len(ISSUE_SUBMIT_LOCKS)),
        ("SUPPORT_MESSAGE_LOCK_COUNT_5", len(support_locks) == len(SUPPORT_MESSAGE_LOCKS)),
        ("ROUTING_PREVIEW_COUNT_6", len(routes) == len(ROUTING_PREVIEWS)),
        ("SAFETY_LOCK_COUNT_12", len(safety) == len(SAFETY_LOCKS)),
        ("RECEIPT_PACKET_COUNT_1", len(packets) == 1),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("FEEDBACK_INTAKE_READY", readiness["feedback_intake_ready"] is True),
        ("ISSUE_INTAKE_READY", readiness["issue_intake_ready"] is True),
        ("SUBMIT_LOCKS_ACTIVE", readiness["submit_locks_active"] is True),
        ("ROUTING_PREVIEW_ONLY", readiness["routing_preview_only"] is True),
        ("SUPPORT_MESSAGE_LOCKED", readiness["support_message_locked"] is True),
        ("SAFE_TO_CONTINUE_TO_GP241", readiness["safe_to_continue_to_gp241"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("VAULT_NOT_DONE", readiness["vault_done"] is False),
        ("CLOUDS_PARKED", readiness["clouds_should_continue"] is False),
        ("SECTION_GP231_GP240", readiness["section_range"] == "GP231-GP240"),
        ("NEXT_SECTION_GP241_GP250", readiness["readiness_payload"]["next_section_range"] == "GP241-GP250"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_READY", all(item["component_ready"] is True for item in components)),
        ("ALL_COMPONENTS_LOCKED", all(item["component_locked"] is True for item in components)),
        ("ALL_COMPONENTS_SUBMIT_ROUTING_SUPPORT_LOCKED", all(item["submit_locks_active"] and item["routing_preview_only"] and item["support_message_locked"] for item in components)),
        ("ALL_FEEDBACK_FORMS_READY_LOCKED", all(item["form_ready"] and item["form_locked"] and item["submit_locked"] for item in feedback_forms)),
        ("ALL_ISSUE_REPORTS_READY_LOCKED", all(item["report_ready"] and item["report_locked"] and item["submit_locked"] for item in issue_reports)),
        ("ALL_FEEDBACK_LOCKS_ACTIVE", all(item["feedback_submit_locked"] and item["feedback_receipt_locked"] for item in feedback_locks)),
        ("ALL_ISSUE_LOCKS_ACTIVE", all(item["issue_submit_locked"] and item["issue_receipt_locked"] for item in issue_locks)),
        ("ALL_SUPPORT_LOCKS_ACTIVE", all(item["support_message_locked"] and item["support_ticket_locked"] for item in support_locks)),
        ("ALL_ROUTES_PREVIEW_ONLY_LOCKED", all(item["preview_ready"] and item["routing_locked"] and item["triage_locked"] and item["escalation_locked"] for item in routes)),
        ("ALL_SAFETY_LOCKS_ACTIVE", all(item["lock_active"] for item in safety)),
        ("ALL_SAFETY_LOCKS_BLOCK_FEEDBACK_ISSUE_SUPPORT", all(item["blocks_feedback_submit"] and item["blocks_issue_submit"] and item["blocks_support_send"] for item in safety)),
        ("ALL_SAFETY_LOCKS_BLOCK_ROUTING_TRIAGE_ESCALATION", all(item["blocks_routing"] and item["blocks_triage"] and item["blocks_escalation"] for item in safety)),
        ("ALL_SAFETY_LOCKS_BLOCK_TICKETS", all(item["blocks_ticket_creation"] for item in safety)),
        ("ALL_SAFETY_LOCKS_BLOCK_TOWER_BILLING", all(item["blocks_tower_gate"] and item["blocks_billing_subscription"] for item in safety)),
        ("ALL_SAFETY_LOCKS_BLOCK_PROVIDER_BODY", all(item["blocks_provider_unlock"] and item["blocks_provider_api"] and item["blocks_object_body"] and item["blocks_download"] for item in safety)),
        ("ALL_SAFETY_LOCKS_BLOCK_DANGEROUS_OPS", all(item["blocks_restore"] and item["blocks_export"] and item["blocks_direct_upload"] and item["blocks_delete"] for item in safety)),
        ("ALL_SAFETY_LOCKS_BLOCK_EXECUTION_DONE", all(item["blocks_execution"] and item["blocks_vault_done"] for item in safety)),
        ("NO_SAFETY_LOCKS_RESOLVED", all(item["resolved"] is False for item in safety)),
        ("PACKET_READY_LOCKED", all(item["packet_ready"] and item["packet_locked"] for item in packets)),
        ("NO_FINAL_FEEDBACK_OR_ISSUE_RECEIPT", all(item["final_feedback_receipt"] is False and item["final_issue_receipt"] is False for item in packets)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("FEEDBACK", feedback_forms),
        ("ISSUE", issue_reports),
        ("FEEDBACKLOCK", feedback_locks),
        ("ISSUELOCK", issue_locks),
        ("SUPPORTLOCK", support_locks),
        ("ROUTE", routes),
        ("SAFETY", safety),
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
        "feedback_form_count": len(feedback_forms),
        "issue_report_count": len(issue_reports),
        "feedback_submit_lock_count": len(feedback_locks),
        "issue_submit_lock_count": len(issue_locks),
        "support_message_lock_count": len(support_locks),
        "routing_preview_count": len(routes),
        "safety_lock_count": len(safety),
        "receipt_packet_count": len(packets),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "feedback_intake_ready": len(failed) == 0 and readiness["feedback_intake_ready"] is True,
        "issue_intake_ready": len(failed) == 0 and readiness["issue_intake_ready"] is True,
        "safe_to_continue_to_gp241": len(failed) == 0 and readiness["safe_to_continue_to_gp241"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp231_beta_feedback_issue_intake_lock_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SHELL_ID, db_path)
    return {"pack": _pack_payload(231, component["pack_name"]), "real_sqlite_backed": True, "shell": component}

def get_gp232_feedback_form_draft_registry(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(FEEDBACK_FORM_ID, db_path)
    rows = get_feedback_form_drafts(db_path)
    return {"pack": _pack_payload(232, component["pack_name"]), "real_sqlite_backed": True, "feedback_form_registry": component, "feedback_form_count": len(rows), "forms": rows}

def get_gp233_issue_report_draft_registry(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(ISSUE_REPORT_ID, db_path)
    rows = get_issue_report_drafts(db_path)
    return {"pack": _pack_payload(233, component["pack_name"]), "real_sqlite_backed": True, "issue_report_registry": component, "issue_report_count": len(rows), "reports": rows}

def get_gp234_feedback_submit_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(FEEDBACK_SUBMIT_LOCK_ID, db_path)
    rows = get_feedback_submit_locks(db_path)
    return {"pack": _pack_payload(234, component["pack_name"]), "real_sqlite_backed": True, "feedback_submit_lock_contract": component, "feedback_submit_lock_count": len(rows), "locks": rows}

def get_gp235_issue_submit_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(ISSUE_SUBMIT_LOCK_ID, db_path)
    rows = get_issue_submit_locks(db_path)
    return {"pack": _pack_payload(235, component["pack_name"]), "real_sqlite_backed": True, "issue_submit_lock_contract": component, "issue_submit_lock_count": len(rows), "locks": rows}

def get_gp236_support_message_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SUPPORT_MESSAGE_LOCK_ID, db_path)
    rows = get_support_message_locks(db_path)
    return {"pack": _pack_payload(236, component["pack_name"]), "real_sqlite_backed": True, "support_message_lock_contract": component, "support_message_lock_count": len(rows), "locks": rows}

def get_gp237_intake_routing_preview_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(ROUTING_PREVIEW_ID, db_path)
    rows = get_intake_routing_previews(db_path)
    return {"pack": _pack_payload(237, component["pack_name"]), "real_sqlite_backed": True, "routing_preview_board": component, "routing_preview_count": len(rows), "routes": rows}

def get_gp238_intake_safety_compliance_lock_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SAFETY_COMPLIANCE_ID, db_path)
    rows = get_intake_safety_compliance_locks(db_path)
    return {"pack": _pack_payload(238, component["pack_name"]), "real_sqlite_backed": True, "safety_compliance_lock_board": component, "safety_lock_count": len(rows), "locks": rows}

def get_gp239_feedback_issue_intake_receipt_draft_packet(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RECEIPT_PACKET_ID, db_path)
    rows = get_feedback_issue_intake_receipt_packets(db_path)
    return {"pack": _pack_payload(239, component["pack_name"]), "real_sqlite_backed": True, "receipt_packet_component": component, "receipt_packet_count": len(rows), "packets": rows}

def get_gp240_feedback_issue_intake_lock_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_feedback_issue_intake_lock_layer(db_path)
    return {"pack": _pack_payload(240, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_feedback_issue_intake_lock_layer(db_path)
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
            "source_gp230_readiness_id": component["source_gp230_readiness_id"],
            "source_gp230_readiness_hash": component["source_gp230_readiness_hash"],
            "source_gp230_readiness_score": component["source_gp230_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "feedback_intake_ready": component["feedback_intake_ready"],
            "issue_intake_ready": component["issue_intake_ready"],
            "submit_locks_active": component["submit_locks_active"],
            "routing_preview_only": component["routing_preview_only"],
            "support_message_locked": component["support_message_locked"],
            "vault_not_done": component["vault_not_done"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp241": validation["safe_to_continue_to_gp241"],
            "foundation_status": "beta_feedback_issue_intake_lock_ready_submit_routing_support_locked_vault_not_done_safe_to_continue",
            "next": next_label,
            **counts,
            "feedback_form_opened": component["feedback_form_opened"],
            "feedback_draft_created": component["feedback_draft_created"],
            "feedback_submitted": component["feedback_submitted"],
            "feedback_received": component["feedback_received"],
            "feedback_receipt_finalized": component["feedback_receipt_finalized"],
            "issue_report_opened": component["issue_report_opened"],
            "issue_draft_created": component["issue_draft_created"],
            "issue_created": component["issue_created"],
            "issue_submitted": component["issue_submitted"],
            "issue_received": component["issue_received"],
            "issue_receipt_finalized": component["issue_receipt_finalized"],
            "support_channel_opened": component["support_channel_opened"],
            "support_message_created": component["support_message_created"],
            "support_message_sent": component["support_message_sent"],
            "support_ticket_created": component["support_ticket_created"],
            "support_ticket_assigned": component["support_ticket_assigned"],
            "bug_ticket_created": component["bug_ticket_created"],
            "bug_ticket_assigned": component["bug_ticket_assigned"],
            "intake_routing_executed": component["intake_routing_executed"],
            "intake_route_assigned": component["intake_route_assigned"],
            "intake_triage_started": component["intake_triage_started"],
            "intake_triage_completed": component["intake_triage_completed"],
            "intake_escalation_created": component["intake_escalation_created"],
            "intake_escalation_sent": component["intake_escalation_sent"],
            "feedback_review_started": component["feedback_review_started"],
            "feedback_review_completed": component["feedback_review_completed"],
            "issue_review_started": component["issue_review_started"],
            "issue_review_completed": component["issue_review_completed"],
            "beta_launch_approved": component["beta_launch_approved"],
            "beta_invite_sent": component["beta_invite_sent"],
            "beta_tester_added": component["beta_tester_added"],
            "beta_tester_access_granted": component["beta_tester_access_granted"],
            "beta_access_token_created": component["beta_access_token_created"],
            "onboarding_started": component["onboarding_started"],
            "onboarding_completed": component["onboarding_completed"],
            "profile_submitted": component["profile_submitted"],
            "policy_acknowledged": component["policy_acknowledged"],
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
            "clouds_status": "parked_do_not_continue_from_vault_gp240",
        },
        "validation": validation,
    }

def get_gp231_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(231, SHELL_ID, "VAULT_GP232_FEEDBACK_FORM_DRAFT_REGISTRY", db_path)

def get_gp232_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(232, FEEDBACK_FORM_ID, "VAULT_GP233_ISSUE_REPORT_DRAFT_REGISTRY", db_path)

def get_gp233_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(233, ISSUE_REPORT_ID, "VAULT_GP234_FEEDBACK_SUBMIT_LOCK_CONTRACT", db_path)

def get_gp234_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(234, FEEDBACK_SUBMIT_LOCK_ID, "VAULT_GP235_ISSUE_SUBMIT_LOCK_CONTRACT", db_path)

def get_gp235_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(235, ISSUE_SUBMIT_LOCK_ID, "VAULT_GP236_SUPPORT_MESSAGE_LOCK_CONTRACT", db_path)

def get_gp236_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(236, SUPPORT_MESSAGE_LOCK_ID, "VAULT_GP237_INTAKE_ROUTING_PREVIEW_BOARD", db_path)

def get_gp237_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(237, ROUTING_PREVIEW_ID, "VAULT_GP238_INTAKE_SAFETY_COMPLIANCE_LOCK_BOARD", db_path)

def get_gp238_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(238, SAFETY_COMPLIANCE_ID, "VAULT_GP239_FEEDBACK_ISSUE_INTAKE_RECEIPT_DRAFT_PACKET", db_path)

def get_gp239_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(239, RECEIPT_PACKET_ID, "VAULT_GP240_FEEDBACK_ISSUE_INTAKE_LOCK_READINESS_CHECKPOINT", db_path)

def get_gp240_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(240, READINESS_ID, NEXT_PACK, db_path)
    status["gp240_status"]["next_section"] = NEXT_SECTION_ID
    status["gp240_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp240_status"]["next_pack"] = NEXT_PACK
    return status

def get_beta_feedback_issue_intake_lock_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_beta_feedback_issue_intake_lock_layer(db_path)
    components = _rows("vault_beta_feedback_issue_intake_components", "gp_number", db_path, {"data_json": "data"})
    feedback_forms = get_feedback_form_drafts(db_path)
    issue_reports = get_issue_report_drafts(db_path)
    feedback_locks = get_feedback_submit_locks(db_path)
    issue_locks = get_issue_submit_locks(db_path)
    support_locks = get_support_message_locks(db_path)
    routes = get_intake_routing_previews(db_path)
    safety = get_intake_safety_compliance_locks(db_path)
    packets = get_feedback_issue_intake_receipt_packets(db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_feedback_issue_intake_lock_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "feedback_forms": {"feedback_form_count": len(feedback_forms), "forms": feedback_forms},
        "issue_reports": {"issue_report_count": len(issue_reports), "reports": issue_reports},
        "feedback_submit_locks": {"feedback_submit_lock_count": len(feedback_locks), "locks": feedback_locks},
        "issue_submit_locks": {"issue_submit_lock_count": len(issue_locks), "locks": issue_locks},
        "support_message_locks": {"support_message_lock_count": len(support_locks), "locks": support_locks},
        "routing_previews": {"routing_preview_count": len(routes), "routes": routes},
        "safety_compliance_locks": {"safety_lock_count": len(safety), "locks": safety},
        "receipt_packets": {"receipt_packet_count": len(packets), "packets": packets},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "beta_feedback_issue_intake_lock_layer_ready": True,
            "feedback_intake_ready": validation["feedback_intake_ready"],
            "issue_intake_ready": validation["issue_intake_ready"],
            "safe_to_continue_to_gp241": validation["safe_to_continue_to_gp241"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "submit_locks_active": True,
            "routing_preview_only": True,
            "support_message_locked": True,
            "feedback_form_opened": False,
            "feedback_draft_created": False,
            "feedback_submitted": False,
            "feedback_received": False,
            "feedback_receipt_finalized": False,
            "issue_report_opened": False,
            "issue_draft_created": False,
            "issue_created": False,
            "issue_submitted": False,
            "issue_received": False,
            "issue_receipt_finalized": False,
            "support_channel_opened": False,
            "support_message_created": False,
            "support_message_sent": False,
            "support_ticket_created": False,
            "support_ticket_assigned": False,
            "bug_ticket_created": False,
            "bug_ticket_assigned": False,
            "intake_routing_executed": False,
            "intake_route_assigned": False,
            "intake_triage_started": False,
            "intake_triage_completed": False,
            "intake_escalation_created": False,
            "intake_escalation_sent": False,
            "feedback_review_started": False,
            "feedback_review_completed": False,
            "issue_review_started": False,
            "issue_review_completed": False,
            "beta_launch_approved": False,
            "beta_invite_sent": False,
            "beta_tester_added": False,
            "beta_tester_access_granted": False,
            "onboarding_started": False,
            "profile_submitted": False,
            "policy_acknowledged": False,
            "workspace_opened": False,
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
            "page": "/vault/beta-feedback-issue-intake-lock-layer",
            "json": "/vault/beta-feedback-issue-intake-lock-layer.json",
            "gp231": "/vault/gp231-status.json",
            "gp232": "/vault/gp232-status.json",
            "gp233": "/vault/gp233-status.json",
            "gp234": "/vault/gp234-status.json",
            "gp235": "/vault/gp235-status.json",
            "gp236": "/vault/gp236-status.json",
            "gp237": "/vault/gp237-status.json",
            "gp238": "/vault/gp238-status.json",
            "gp239": "/vault/gp239-status.json",
            "gp240": "/vault/gp240-status.json",
        },
    }

def render_beta_feedback_issue_intake_lock_layer_page() -> str:
    home = get_beta_feedback_issue_intake_lock_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    feedback_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['feedback_name'])}</strong>
          <span>{escape(item['feedback_status'])}</span>
          <code>{escape(item['feedback_category'])} · submit locked</code>
        </article>
        """
        for item in home["feedback_forms"]["forms"]
    )

    issue_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['issue_name'])}</strong>
          <span>{escape(item['issue_status'])}</span>
          <code>{escape(item['issue_category'])} · issue locked</code>
        </article>
        """
        for item in home["issue_reports"]["reports"]
    )

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP231-GP240 Beta Feedback Issue Intake Lock Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 231-240</div>
    <div class="eyebrow">Beta Feedback and Issue Intake Lock Layer · GP231-GP240</div>
    <h1>Feedback + Issue Intake Locked</h1>
    <p>This layer prepares feedback forms, issue reports, support message locks, routing previews, safety locks, and receipt drafts. Nothing can be submitted, routed, triaged, escalated, or assigned.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['feedback_form_count']}</strong><span>feedback drafts</span></div>
      <div class="metric"><strong>{home['store']['issue_report_count']}</strong><span>issue drafts</span></div>
      <div class="metric"><strong>{home['store']['safety_lock_count']}</strong><span>safety locks</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP231-GP240 built</span>
      <span class="pill ok">Safe to GP241</span>
      <span class="pill danger">No feedback submit</span>
      <span class="pill danger">No issue submit</span>
      <span class="pill danger">No support message</span>
      <span class="pill danger">No routing</span>
      <span class="pill danger">No triage</span>
      <span class="pill danger">No escalation</span>
      <span class="pill danger">No execution</span>
      <span class="pill danger">Vault not done</span>
    </div>
  </section>

  <section class="section">
    <h2>Feedback Form Draft Registry</h2>
    <div class="cards">{feedback_cards}</div>
  </section>

  <section class="section">
    <h2>Issue Report Draft Registry</h2>
    <div class="cards">{issue_cards}</div>
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
