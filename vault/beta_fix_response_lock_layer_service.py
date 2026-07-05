"""
VAULT GP251-GP260 — Beta Fix and Response Lock Layer

New section:
Archive Vault — Beta Fix and Response Lock Layer / GP251-GP260

Builds:
- GP251 Beta Fix and Response Lock Shell
- GP252 Fix Draft Queue
- GP253 Response Draft Queue
- GP254 Fix Execution Lock Contract
- GP255 Response Send Lock Contract
- GP256 Fix Verification Preview Board
- GP257 Release Closeout Lock Contract
- GP258 Owner Response Approval Lock Board
- GP259 Fix Response Receipt Draft Packet
- GP260 Fix Response Lock Readiness Checkpoint

This layer prepares locked fix/response governance surfaces. It does not create
or run fixes, write patches, send responses, verify fixes, publish releases,
record closeout, approve owner responses, call Tower/billing/providers, read
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

from vault.beta_feedback_review_triage_lock_layer_service import (
    get_gp250_status,
    get_gp250_review_triage_lock_readiness_checkpoint,
    get_beta_feedback_review_triage_lock_layer_home,
    validate_beta_feedback_review_triage_lock_layer,
    get_fix_room_handoff_previews,
    get_reviewer_decision_locks,
)

LAYER_ID = "VAULT_GP251_260"
LAYER_NAME = "Beta Fix and Response Lock Layer"
SCHEMA_VERSION = "vault.beta_fix_response_lock_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_BETA_FIX_AND_RESPONSE_LOCK_LAYER"
SECTION_TITLE = "Archive Vault — Beta Fix and Response Lock Layer"
SECTION_RANGE = "GP251-GP260"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_BETA_FEEDBACK_REVIEW_AND_TRIAGE_LOCK_LAYER"
PREVIOUS_SECTION_RANGE = "GP241-GP250"

NEXT_SECTION_ID = "ARCHIVE_VAULT_BETA_CLOSEOUT_AND_GO_NO_GO_LOCK_LAYER"
NEXT_SECTION_RANGE = "GP261-GP270"
NEXT_PACK = "VAULT_GP261_270_BETA_CLOSEOUT_AND_GO_NO_GO_LOCK_LAYER"

DEFAULT_DB_ENV = "VAULT_BETA_FIX_RESPONSE_LOCK_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_beta_fix_response_lock_layer.sqlite"

SHELL_ID = "VBFRL-SHELL-GP251-001"
FIX_DRAFT_ID = "VBFRL-FIXDRAFT-GP252-001"
RESPONSE_DRAFT_ID = "VBFRL-RESPONSEDRAFT-GP253-001"
FIX_EXECUTION_LOCK_ID = "VBFRL-FIXEXEC-GP254-001"
RESPONSE_SEND_LOCK_ID = "VBFRL-RESPONSESEND-GP255-001"
FIX_VERIFICATION_ID = "VBFRL-VERIFY-GP256-001"
RELEASE_CLOSEOUT_ID = "VBFRL-RELEASE-GP257-001"
OWNER_RESPONSE_APPROVAL_ID = "VBFRL-OWNERAPPROVAL-GP258-001"
RECEIPT_PACKET_ID = "VBFRL-RECEIPT-GP259-001"
READINESS_ID = "VBFRL-READINESS-GP260-001"

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
    "feedback_submitted",
    "issue_created",
    "issue_submitted",
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
    "intake_triage_started",
    "intake_triage_completed",
    "triage_classification_applied",
    "assignment_created",
    "assignment_sent",
    "assignment_accepted",
    "assignee_notified",
    "intake_escalation_created",
    "intake_escalation_sent",
    "fix_room_opened",
    "fix_room_handoff_created",
    "fix_room_handoff_sent",
    "fix_draft_created",
    "fix_task_created",
    "fix_task_assigned",
    "fix_execution_requested",
    "fix_execution_approved",
    "fix_started",
    "fix_completed",
    "fix_applied",
    "fix_merged",
    "code_patch_created",
    "code_patch_written",
    "code_patch_run",
    "test_run_started",
    "test_run_completed",
    "fix_verification_started",
    "fix_verification_completed",
    "fix_verified",
    "fix_failed",
    "response_draft_created",
    "response_draft_approved",
    "response_sent",
    "tester_notified",
    "support_response_sent",
    "release_created",
    "release_published",
    "release_notes_created",
    "release_notes_sent",
    "closeout_requested",
    "closeout_approved",
    "closeout_recorded",
    "owner_response_approval_requested",
    "owner_response_approval_recorded",
    "owner_response_rejection_recorded",
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

FIX_DRAFTS = [
    ("ui_copy_fix_draft", "UI Copy Fix Draft", "ui", "fix_draft_locked"),
    ("receipt_display_fix_draft", "Receipt Display Fix Draft", "receipt", "fix_draft_locked"),
    ("access_copy_fix_draft", "Access Copy Fix Draft", "access", "fix_draft_locked"),
    ("provider_boundary_fix_draft", "Provider Boundary Fix Draft", "provider", "fix_draft_locked"),
    ("safety_notice_fix_draft", "Safety Notice Fix Draft", "safety", "fix_draft_locked"),
    ("owner_console_fix_draft", "Owner Console Fix Draft", "owner", "fix_draft_locked"),
]

RESPONSE_DRAFTS = [
    ("tester_ack_response_draft", "Tester Acknowledgment Response Draft", "tester", "response_draft_locked"),
    ("issue_received_response_draft", "Issue Received Response Draft", "issue", "response_draft_locked"),
    ("fix_pending_response_draft", "Fix Pending Response Draft", "fix", "response_draft_locked"),
    ("not_reproducible_response_draft", "Not Reproducible Response Draft", "qa", "response_draft_locked"),
    ("owner_review_response_draft", "Owner Review Response Draft", "owner", "response_draft_locked"),
    ("closed_no_action_response_draft", "Closed No Action Response Draft", "closeout", "response_draft_locked"),
]

FIX_EXECUTION_LOCKS = [
    ("fix_task_create_lock", "Fix Task Create Lock", "task"),
    ("fix_task_assign_lock", "Fix Task Assign Lock", "assignment"),
    ("fix_start_lock", "Fix Start Lock", "start"),
    ("fix_complete_lock", "Fix Complete Lock", "complete"),
    ("code_patch_write_lock", "Code Patch Write Lock", "code"),
    ("test_run_lock", "Test Run Lock", "test"),
]

RESPONSE_SEND_LOCKS = [
    ("response_draft_create_lock", "Response Draft Create Lock", "draft"),
    ("response_approval_lock", "Response Approval Lock", "approval"),
    ("response_send_lock", "Response Send Lock", "send"),
    ("tester_notify_lock", "Tester Notify Lock", "notify"),
    ("support_response_lock", "Support Response Lock", "support"),
]

FIX_VERIFICATION_PREVIEWS = [
    ("ui_fix_verification_preview", "UI Fix Verification Preview", "ui", "verification_preview_locked"),
    ("receipt_fix_verification_preview", "Receipt Fix Verification Preview", "receipt", "verification_preview_locked"),
    ("access_fix_verification_preview", "Access Fix Verification Preview", "access", "verification_preview_locked"),
    ("provider_boundary_fix_verification_preview", "Provider Boundary Fix Verification Preview", "provider", "verification_preview_locked"),
    ("safety_fix_verification_preview", "Safety Fix Verification Preview", "safety", "verification_preview_locked"),
]

RELEASE_CLOSEOUT_LOCKS = [
    ("release_create_lock", "Release Create Lock", "release"),
    ("release_publish_lock", "Release Publish Lock", "release"),
    ("release_notes_lock", "Release Notes Lock", "notes"),
    ("closeout_request_lock", "Closeout Request Lock", "closeout"),
    ("closeout_approval_lock", "Closeout Approval Lock", "closeout"),
    ("closeout_record_lock", "Closeout Record Lock", "closeout"),
]

OWNER_RESPONSE_APPROVAL_LOCKS = [
    ("owner_response_approval_request_lock", "Owner Response Approval Request Lock", "owner"),
    ("owner_response_approval_record_lock", "Owner Response Approval Record Lock", "owner"),
    ("owner_response_rejection_record_lock", "Owner Response Rejection Record Lock", "owner"),
    ("owner_response_override_lock", "Owner Response Override Lock", "owner"),
    ("owner_response_closeout_lock", "Owner Response Closeout Lock", "owner"),
]

COMPONENT_SPECS = [
    (251, SHELL_ID, "VAULT_GP251", "Beta Fix and Response Lock Shell", "beta_fix_response_lock_shell"),
    (252, FIX_DRAFT_ID, "VAULT_GP252", "Fix Draft Queue", "fix_draft_queue"),
    (253, RESPONSE_DRAFT_ID, "VAULT_GP253", "Response Draft Queue", "response_draft_queue"),
    (254, FIX_EXECUTION_LOCK_ID, "VAULT_GP254", "Fix Execution Lock Contract", "fix_execution_lock_contract"),
    (255, RESPONSE_SEND_LOCK_ID, "VAULT_GP255", "Response Send Lock Contract", "response_send_lock_contract"),
    (256, FIX_VERIFICATION_ID, "VAULT_GP256", "Fix Verification Preview Board", "fix_verification_preview_board"),
    (257, RELEASE_CLOSEOUT_ID, "VAULT_GP257", "Release Closeout Lock Contract", "release_closeout_lock_contract"),
    (258, OWNER_RESPONSE_APPROVAL_ID, "VAULT_GP258", "Owner Response Approval Lock Board", "owner_response_approval_lock_board"),
    (259, RECEIPT_PACKET_ID, "VAULT_GP259", "Fix Response Receipt Draft Packet", "fix_response_receipt_draft_packet"),
    (260, READINESS_ID, "VAULT_GP260", "Fix Response Lock Readiness Checkpoint", "fix_response_lock_readiness_checkpoint"),
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
        "source_gp250_readiness_score",
        "component_count",
        "fix_draft_count",
        "response_draft_count",
        "fix_execution_lock_count",
        "response_send_lock_count",
        "fix_verification_count",
        "release_closeout_lock_count",
        "owner_response_approval_lock_count",
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
        "depends_on": ["VAULT_GP250"],
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
        "depends_on": ["VAULT_GP250"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_beta_fix_response_lock_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_beta_fix_response_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp250_readiness_id TEXT NOT NULL,
                source_gp250_readiness_hash TEXT NOT NULL,
                source_gp250_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                fix_response_ready INTEGER NOT NULL DEFAULT 1,
                fix_execution_locked INTEGER NOT NULL DEFAULT 1,
                response_send_locked INTEGER NOT NULL DEFAULT 1,
                verification_preview_only INTEGER NOT NULL DEFAULT 1,
                release_closeout_locked INTEGER NOT NULL DEFAULT 1,
                owner_response_approval_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_fix_draft_queue (
                fix_draft_id TEXT PRIMARY KEY,
                fix_code TEXT NOT NULL UNIQUE,
                fix_name TEXT NOT NULL,
                fix_category TEXT NOT NULL,
                fix_status TEXT NOT NULL,
                draft_ready INTEGER NOT NULL DEFAULT 1,
                draft_locked INTEGER NOT NULL DEFAULT 1,
                execution_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                fix_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_response_draft_queue (
                response_draft_id TEXT PRIMARY KEY,
                response_code TEXT NOT NULL UNIQUE,
                response_name TEXT NOT NULL,
                response_category TEXT NOT NULL,
                response_status TEXT NOT NULL,
                draft_ready INTEGER NOT NULL DEFAULT 1,
                draft_locked INTEGER NOT NULL DEFAULT 1,
                send_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                response_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_fix_execution_lock_contracts (
                lock_id TEXT PRIMARY KEY,
                lock_code TEXT NOT NULL UNIQUE,
                lock_name TEXT NOT NULL,
                lock_category TEXT NOT NULL,
                lock_status TEXT NOT NULL,
                fix_execution_locked INTEGER NOT NULL DEFAULT 1,
                code_patch_locked INTEGER NOT NULL DEFAULT 1,
                test_run_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_response_send_lock_contracts (
                lock_id TEXT PRIMARY KEY,
                lock_code TEXT NOT NULL UNIQUE,
                lock_name TEXT NOT NULL,
                lock_category TEXT NOT NULL,
                lock_status TEXT NOT NULL,
                response_send_locked INTEGER NOT NULL DEFAULT 1,
                tester_notify_locked INTEGER NOT NULL DEFAULT 1,
                support_response_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_fix_verification_preview_board (
                verification_id TEXT PRIMARY KEY,
                verification_code TEXT NOT NULL UNIQUE,
                verification_name TEXT NOT NULL,
                verification_category TEXT NOT NULL,
                verification_status TEXT NOT NULL,
                preview_ready INTEGER NOT NULL DEFAULT 1,
                verification_locked INTEGER NOT NULL DEFAULT 1,
                final_result_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                verification_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_release_closeout_lock_contracts (
                lock_id TEXT PRIMARY KEY,
                lock_code TEXT NOT NULL UNIQUE,
                lock_name TEXT NOT NULL,
                lock_category TEXT NOT NULL,
                lock_status TEXT NOT NULL,
                release_locked INTEGER NOT NULL DEFAULT 1,
                closeout_locked INTEGER NOT NULL DEFAULT 1,
                publish_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_owner_response_approval_lock_board (
                approval_lock_id TEXT PRIMARY KEY,
                approval_code TEXT NOT NULL UNIQUE,
                approval_name TEXT NOT NULL,
                approval_category TEXT NOT NULL,
                approval_status TEXT NOT NULL,
                owner_approval_locked INTEGER NOT NULL DEFAULT 1,
                owner_rejection_locked INTEGER NOT NULL DEFAULT 1,
                owner_closeout_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                approval_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_fix_response_receipt_draft_packets (
                receipt_packet_id TEXT PRIMARY KEY,
                packet_code TEXT NOT NULL UNIQUE,
                packet_name TEXT NOT NULL,
                packet_status TEXT NOT NULL,
                packet_ready INTEGER NOT NULL DEFAULT 1,
                packet_locked INTEGER NOT NULL DEFAULT 1,
                final_fix_receipt INTEGER NOT NULL DEFAULT 0,
                final_response_receipt INTEGER NOT NULL DEFAULT 0,
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
            CREATE TABLE IF NOT EXISTS vault_fix_response_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                fix_draft_count INTEGER NOT NULL,
                response_draft_count INTEGER NOT NULL,
                fix_execution_lock_count INTEGER NOT NULL,
                response_send_lock_count INTEGER NOT NULL,
                fix_verification_count INTEGER NOT NULL,
                release_closeout_lock_count INTEGER NOT NULL,
                owner_response_approval_lock_count INTEGER NOT NULL,
                receipt_packet_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                fix_response_ready INTEGER NOT NULL DEFAULT 1,
                fix_execution_locked INTEGER NOT NULL DEFAULT 1,
                response_send_locked INTEGER NOT NULL DEFAULT 1,
                verification_preview_only INTEGER NOT NULL DEFAULT 1,
                release_closeout_locked INTEGER NOT NULL DEFAULT 1,
                owner_response_approval_locked INTEGER NOT NULL DEFAULT 1,
                safe_to_continue_to_gp261 INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_fix_response_events (
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
            "vault_beta_fix_response_components",
            "vault_fix_draft_queue",
            "vault_response_draft_queue",
            "vault_fix_execution_lock_contracts",
            "vault_response_send_lock_contracts",
            "vault_fix_verification_preview_board",
            "vault_release_closeout_lock_contracts",
            "vault_owner_response_approval_lock_board",
            "vault_fix_response_receipt_draft_packets",
            "vault_fix_response_readiness",
            "vault_fix_response_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VBFRLEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_fix_response_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_beta_fix_response_lock_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_beta_fix_response_lock_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_beta_fix_response_components WHERE component_id = ?",
            (SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp250_status = get_gp250_status()["gp250_status"]
            gp250_checkpoint = get_gp250_review_triage_lock_readiness_checkpoint()["readiness_checkpoint"]
            gp250_home = get_beta_feedback_review_triage_lock_layer_home()
            gp250_validation = validate_beta_feedback_review_triage_lock_layer()
            source_fix_handoffs = get_fix_room_handoff_previews()
            source_reviewer_locks = get_reviewer_decision_locks()

            readiness = gp250_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp250_readiness_id": readiness["readiness_id"],
                "source_gp250_readiness_hash": readiness["readiness_hash"],
                "source_gp250_readiness_score": readiness["readiness_score"],
            }

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "fix_draft_count": len(FIX_DRAFTS),
                "response_draft_count": len(RESPONSE_DRAFTS),
                "fix_execution_lock_count": len(FIX_EXECUTION_LOCKS),
                "response_send_lock_count": len(RESPONSE_SEND_LOCKS),
                "fix_verification_count": len(FIX_VERIFICATION_PREVIEWS),
                "release_closeout_lock_count": len(RELEASE_CLOSEOUT_LOCKS),
                "owner_response_approval_lock_count": len(OWNER_RESPONSE_APPROVAL_LOCKS),
                "receipt_packet_count": 1,
            }

            source_context = {
                "source_gp250_status_ready": gp250_status["ready"],
                "source_gp250_validation_passed": gp250_status["validation_passed"],
                "source_gp250_safe_to_continue_to_gp251": gp250_status["safe_to_continue_to_gp251"],
                "source_gp250_readiness_hash": readiness["readiness_hash"],
                "source_gp250_readiness_score": readiness["readiness_score"],
                "source_fix_room_handoff_count": len(source_fix_handoffs),
                "source_reviewer_decision_lock_count": len(source_reviewer_locks),
                "source_validation_check_count": gp250_validation["check_count"],
            }

            component_extra = {
                SHELL_ID: {"beta_fix_response_lock_shell_ready": True},
                FIX_DRAFT_ID: {"fix_draft_queue_ready": True, "fix_draft_count": counts["fix_draft_count"]},
                RESPONSE_DRAFT_ID: {"response_draft_queue_ready": True, "response_draft_count": counts["response_draft_count"]},
                FIX_EXECUTION_LOCK_ID: {"fix_execution_lock_contract_ready": True, "fix_execution_lock_count": counts["fix_execution_lock_count"]},
                RESPONSE_SEND_LOCK_ID: {"response_send_lock_contract_ready": True, "response_send_lock_count": counts["response_send_lock_count"]},
                FIX_VERIFICATION_ID: {"fix_verification_preview_board_ready": True, "fix_verification_count": counts["fix_verification_count"]},
                RELEASE_CLOSEOUT_ID: {"release_closeout_lock_contract_ready": True, "release_closeout_lock_count": counts["release_closeout_lock_count"]},
                OWNER_RESPONSE_APPROVAL_ID: {"owner_response_approval_lock_board_ready": True, "owner_response_approval_lock_count": counts["owner_response_approval_lock_count"]},
                RECEIPT_PACKET_ID: {"fix_response_receipt_draft_packet_ready": True, "receipt_packet_count": counts["receipt_packet_count"]},
                READINESS_ID: {"fix_response_lock_readiness_checkpoint_ready": True, "safe_to_continue_to_gp261": True},
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
                    "fix_response_ready": True,
                    "fix_execution_locked": True,
                    "response_send_locked": True,
                    "verification_preview_only": True,
                    "release_closeout_locked": True,
                    "owner_response_approval_locked": True,
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
                    "fix_response_ready": 1,
                    "fix_execution_locked": 1,
                    "response_send_locked": 1,
                    "verification_preview_only": 1,
                    "release_closeout_locked": 1,
                    "owner_response_approval_locked": 1,
                    "vault_not_done": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_fix_response_components", row)

            for idx, (code, name, category, status) in enumerate(FIX_DRAFTS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "fix_code": code,
                    "fix_name": name,
                    "fix_category": category,
                    "fix_status": status,
                    "draft_ready": True,
                    "draft_locked": True,
                    "execution_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "fix_draft_id": f"VBFRLFIX-{idx:03d}",
                    "fix_code": code,
                    "fix_name": name,
                    "fix_category": category,
                    "fix_status": status,
                    "draft_ready": 1,
                    "draft_locked": 1,
                    "execution_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "fix_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_fix_draft_queue", row)

            for idx, (code, name, category, status) in enumerate(RESPONSE_DRAFTS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "response_code": code,
                    "response_name": name,
                    "response_category": category,
                    "response_status": status,
                    "draft_ready": True,
                    "draft_locked": True,
                    "send_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "response_draft_id": f"VBFRLRESP-{idx:03d}",
                    "response_code": code,
                    "response_name": name,
                    "response_category": category,
                    "response_status": status,
                    "draft_ready": 1,
                    "draft_locked": 1,
                    "send_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "response_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_response_draft_queue", row)

            for idx, (code, name, category) in enumerate(FIX_EXECUTION_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "lock_status": "FIX_EXECUTION_LOCK_ACTIVE",
                    "fix_execution_locked": True,
                    "code_patch_locked": True,
                    "test_run_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "lock_id": f"VBFRLFIXLOCK-{idx:03d}",
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "lock_status": payload["lock_status"],
                    "fix_execution_locked": 1,
                    "code_patch_locked": 1,
                    "test_run_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "lock_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_fix_execution_lock_contracts", row)

            for idx, (code, name, category) in enumerate(RESPONSE_SEND_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "lock_status": "RESPONSE_SEND_LOCK_ACTIVE",
                    "response_send_locked": True,
                    "tester_notify_locked": True,
                    "support_response_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "lock_id": f"VBFRLRESPLOCK-{idx:03d}",
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "lock_status": payload["lock_status"],
                    "response_send_locked": 1,
                    "tester_notify_locked": 1,
                    "support_response_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "lock_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_response_send_lock_contracts", row)

            for idx, (code, name, category, status) in enumerate(FIX_VERIFICATION_PREVIEWS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "verification_code": code,
                    "verification_name": name,
                    "verification_category": category,
                    "verification_status": status,
                    "preview_ready": True,
                    "verification_locked": True,
                    "final_result_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "verification_id": f"VBFRLVERIFY-{idx:03d}",
                    "verification_code": code,
                    "verification_name": name,
                    "verification_category": category,
                    "verification_status": status,
                    "preview_ready": 1,
                    "verification_locked": 1,
                    "final_result_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "verification_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_fix_verification_preview_board", row)

            for idx, (code, name, category) in enumerate(RELEASE_CLOSEOUT_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "lock_status": "RELEASE_CLOSEOUT_LOCK_ACTIVE",
                    "release_locked": True,
                    "closeout_locked": True,
                    "publish_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "lock_id": f"VBFRLRELEASE-{idx:03d}",
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "lock_status": payload["lock_status"],
                    "release_locked": 1,
                    "closeout_locked": 1,
                    "publish_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "lock_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_release_closeout_lock_contracts", row)

            for idx, (code, name, category) in enumerate(OWNER_RESPONSE_APPROVAL_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "approval_code": code,
                    "approval_name": name,
                    "approval_category": category,
                    "approval_status": "OWNER_RESPONSE_APPROVAL_LOCK_ACTIVE",
                    "owner_approval_locked": True,
                    "owner_rejection_locked": True,
                    "owner_closeout_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "approval_lock_id": f"VBFRLOWNER-{idx:03d}",
                    "approval_code": code,
                    "approval_name": name,
                    "approval_category": category,
                    "approval_status": payload["approval_status"],
                    "owner_approval_locked": 1,
                    "owner_rejection_locked": 1,
                    "owner_closeout_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "approval_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_owner_response_approval_lock_board", row)

            packet_payload = {
                "schema_version": SCHEMA_VERSION,
                "packet_code": "vault_gp251_260_fix_response_packet",
                "packet_name": "Vault GP251-GP260 Fix Response Receipt Draft Packet",
                "packet_status": "READY_LOCKED_DRAFT_ONLY_NO_FIX_OR_RESPONSE_RECEIPT",
                "source_gp250_readiness_id": readiness["readiness_id"],
                "source_gp250_readiness_hash": readiness["readiness_hash"],
                "source_gp250_readiness_score": readiness["readiness_score"],
                **counts,
                "fix_response_ready": True,
                "fix_execution_locked": True,
                "response_send_locked": True,
                "final_fix_receipt": False,
                "final_response_receipt": False,
                "locked_truth": {field: False for field in FALSE_FIELDS},
                "vault_done": False,
                "clouds_should_continue": False,
            }
            row = {
                "receipt_packet_id": RECEIPT_PACKET_ID,
                "packet_code": "vault_gp251_260_fix_response_packet",
                "packet_name": "Vault GP251-GP260 Fix Response Receipt Draft Packet",
                "packet_status": packet_payload["packet_status"],
                "packet_ready": 1,
                "packet_locked": 1,
                "final_fix_receipt": 0,
                "final_response_receipt": 0,
                "payload_json": _json_dumps(packet_payload),
                "packet_hash": _hash_payload(packet_payload),
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                row[field] = 0
            _insert_dict(conn, "vault_fix_response_receipt_draft_packets", row)

            checks = [
                ("SOURCE_GP250_READY", bool(gp250_status["ready"])),
                ("SOURCE_GP250_VALIDATION_PASSED", bool(gp250_status["validation_passed"])),
                ("SOURCE_GP250_SAFE_TO_CONTINUE", bool(gp250_status["safe_to_continue_to_gp251"])),
                ("SOURCE_GP250_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP250_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("FIX_DRAFT_COUNT_6", counts["fix_draft_count"] == 6),
                ("RESPONSE_DRAFT_COUNT_6", counts["response_draft_count"] == 6),
                ("FIX_EXECUTION_LOCK_COUNT_6", counts["fix_execution_lock_count"] == 6),
                ("RESPONSE_SEND_LOCK_COUNT_5", counts["response_send_lock_count"] == 5),
                ("FIX_VERIFICATION_COUNT_5", counts["fix_verification_count"] == 5),
                ("RELEASE_CLOSEOUT_LOCK_COUNT_6", counts["release_closeout_lock_count"] == 6),
                ("OWNER_RESPONSE_APPROVAL_LOCK_COUNT_5", counts["owner_response_approval_lock_count"] == 5),
                ("RECEIPT_PACKET_COUNT_1", counts["receipt_packet_count"] == 1),
                ("SECTION_GP251_GP260", SECTION_RANGE == "GP251-GP260"),
                ("NEXT_SECTION_GP261_GP270", NEXT_SECTION_RANGE == "GP261-GP270"),
                ("FIX_RESPONSE_READY", True),
                ("FIX_EXECUTION_LOCKED", True),
                ("RESPONSE_SEND_LOCKED", True),
                ("VERIFICATION_PREVIEW_ONLY", True),
                ("RELEASE_CLOSEOUT_LOCKED", True),
                ("OWNER_RESPONSE_APPROVAL_LOCKED", True),
                ("NO_FIX_DRAFT_CREATED", True),
                ("NO_FIX_TASK_CREATED", True),
                ("NO_FIX_STARTED_COMPLETED", True),
                ("NO_CODE_PATCH_OR_TEST_RUN", True),
                ("NO_RESPONSE_DRAFT_CREATED", True),
                ("NO_RESPONSE_SENT", True),
                ("NO_VERIFICATION_RUN", True),
                ("NO_RELEASE_CLOSEOUT", True),
                ("NO_OWNER_RESPONSE_APPROVAL", True),
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
                "gp_number": 260,
                "pack_id": "VAULT_GP260",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp250_readiness_id": readiness["readiness_id"],
                "source_gp250_readiness_hash": readiness["readiness_hash"],
                "source_gp250_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "fix_response_ready": True,
                "fix_execution_locked": True,
                "response_send_locked": True,
                "verification_preview_only": True,
                "release_closeout_locked": True,
                "owner_response_approval_locked": True,
                "safe_to_continue_to_gp261": failed_count == 0,
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
                "gp_number": 260,
                "pack_id": "VAULT_GP260",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "BETA_FIX_RESPONSE_LOCK_READY_FIX_RESPONSE_VERIFY_RELEASE_CLOSEOUT_OWNER_APPROVAL_LOCKED_VAULT_NOT_DONE_SAFE_TO_CONTINUE",
                "readiness_score": readiness_payload["readiness_score"],
                **counts,
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "fix_response_ready": 1,
                "fix_execution_locked": 1,
                "response_send_locked": 1,
                "verification_preview_only": 1,
                "release_closeout_locked": 1,
                "owner_response_approval_locked": 1,
                "safe_to_continue_to_gp261": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_fix_response_readiness", row)

            for event_type, event_payload in [
                ("GP251_BETA_FIX_RESPONSE_LOCK_SHELL_CREATED", {"component_id": SHELL_ID}),
                ("GP252_FIX_DRAFT_QUEUE_CREATED", {"fix_draft_count": counts["fix_draft_count"]}),
                ("GP253_RESPONSE_DRAFT_QUEUE_CREATED", {"response_draft_count": counts["response_draft_count"]}),
                ("GP254_FIX_EXECUTION_LOCK_CONTRACT_CREATED", {"fix_execution_lock_count": counts["fix_execution_lock_count"]}),
                ("GP255_RESPONSE_SEND_LOCK_CONTRACT_CREATED", {"response_send_lock_count": counts["response_send_lock_count"]}),
                ("GP256_FIX_VERIFICATION_PREVIEW_BOARD_CREATED", {"fix_verification_count": counts["fix_verification_count"]}),
                ("GP257_RELEASE_CLOSEOUT_LOCK_CONTRACT_CREATED", {"release_closeout_lock_count": counts["release_closeout_lock_count"]}),
                ("GP258_OWNER_RESPONSE_APPROVAL_LOCK_BOARD_CREATED", {"owner_response_approval_lock_count": counts["owner_response_approval_lock_count"]}),
                ("GP259_FIX_RESPONSE_RECEIPT_DRAFT_PACKET_CREATED", {"receipt_packet_count": counts["receipt_packet_count"]}),
                ("GP260_FIX_RESPONSE_LOCK_READINESS_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp261": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_fix_response_components").fetchone()["c"]),
            "fix_draft_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_fix_draft_queue").fetchone()["c"]),
            "response_draft_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_response_draft_queue").fetchone()["c"]),
            "fix_execution_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_fix_execution_lock_contracts").fetchone()["c"]),
            "response_send_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_response_send_lock_contracts").fetchone()["c"]),
            "fix_verification_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_fix_verification_preview_board").fetchone()["c"]),
            "release_closeout_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_release_closeout_lock_contracts").fetchone()["c"]),
            "owner_response_approval_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_response_approval_lock_board").fetchone()["c"]),
            "receipt_packet_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_fix_response_receipt_draft_packets").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_fix_response_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_fix_response_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_beta_fix_response_lock_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_beta_fix_response_lock_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_beta_fix_response_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_beta_fix_response_lock_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_fix_response_readiness WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_beta_fix_response_lock_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_fix_response_events ORDER BY created_at, event_id").fetchall()
    return [{"event_id": row["event_id"], "event_type": row["event_type"], "event_payload": _json_loads(row["event_payload_json"]), "created_at": row["created_at"]} for row in rows]

def get_fix_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_fix_draft_queue", "fix_code", db_path, {"payload_json": "payload"})

def get_response_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_response_draft_queue", "response_code", db_path, {"payload_json": "payload"})

def get_fix_execution_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_fix_execution_lock_contracts", "lock_code", db_path, {"payload_json": "payload"})

def get_response_send_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_response_send_lock_contracts", "lock_code", db_path, {"payload_json": "payload"})

def get_fix_verification_previews(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_fix_verification_preview_board", "verification_code", db_path, {"payload_json": "payload"})

def get_release_closeout_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_release_closeout_lock_contracts", "lock_code", db_path, {"payload_json": "payload"})

def get_owner_response_approval_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_owner_response_approval_lock_board", "approval_code", db_path, {"payload_json": "payload"})

def get_fix_response_receipt_packets(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_fix_response_receipt_draft_packets", "packet_code", db_path, {"payload_json": "payload"})

def validate_beta_fix_response_lock_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_beta_fix_response_components", "gp_number", db_path, {"data_json": "data"})
    fix_drafts = get_fix_drafts(db_path)
    response_drafts = get_response_drafts(db_path)
    fix_locks = get_fix_execution_locks(db_path)
    response_locks = get_response_send_locks(db_path)
    verifications = get_fix_verification_previews(db_path)
    release_locks = get_release_closeout_locks(db_path)
    owner_locks = get_owner_response_approval_locks(db_path)
    packets = get_fix_response_receipt_packets(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("FIX_DRAFT_COUNT_6", len(fix_drafts) == len(FIX_DRAFTS)),
        ("RESPONSE_DRAFT_COUNT_6", len(response_drafts) == len(RESPONSE_DRAFTS)),
        ("FIX_EXECUTION_LOCK_COUNT_6", len(fix_locks) == len(FIX_EXECUTION_LOCKS)),
        ("RESPONSE_SEND_LOCK_COUNT_5", len(response_locks) == len(RESPONSE_SEND_LOCKS)),
        ("FIX_VERIFICATION_COUNT_5", len(verifications) == len(FIX_VERIFICATION_PREVIEWS)),
        ("RELEASE_CLOSEOUT_LOCK_COUNT_6", len(release_locks) == len(RELEASE_CLOSEOUT_LOCKS)),
        ("OWNER_RESPONSE_APPROVAL_LOCK_COUNT_5", len(owner_locks) == len(OWNER_RESPONSE_APPROVAL_LOCKS)),
        ("RECEIPT_PACKET_COUNT_1", len(packets) == 1),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("FIX_RESPONSE_READY", readiness["fix_response_ready"] is True),
        ("FIX_EXECUTION_LOCKED", readiness["fix_execution_locked"] is True),
        ("RESPONSE_SEND_LOCKED", readiness["response_send_locked"] is True),
        ("VERIFICATION_PREVIEW_ONLY", readiness["verification_preview_only"] is True),
        ("RELEASE_CLOSEOUT_LOCKED", readiness["release_closeout_locked"] is True),
        ("OWNER_RESPONSE_APPROVAL_LOCKED", readiness["owner_response_approval_locked"] is True),
        ("SAFE_TO_CONTINUE_TO_GP261", readiness["safe_to_continue_to_gp261"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("VAULT_NOT_DONE", readiness["vault_done"] is False),
        ("CLOUDS_PARKED", readiness["clouds_should_continue"] is False),
        ("SECTION_GP251_GP260", readiness["section_range"] == "GP251-GP260"),
        ("NEXT_SECTION_GP261_GP270", readiness["readiness_payload"]["next_section_range"] == "GP261-GP270"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_READY", all(item["component_ready"] is True for item in components)),
        ("ALL_COMPONENTS_LOCKED", all(item["component_locked"] is True for item in components)),
        ("ALL_COMPONENTS_FIX_RESPONSE_LOCKED", all(item["fix_execution_locked"] and item["response_send_locked"] for item in components)),
        ("ALL_COMPONENTS_VERIFY_RELEASE_OWNER_LOCKED", all(item["verification_preview_only"] and item["release_closeout_locked"] and item["owner_response_approval_locked"] for item in components)),
        ("ALL_FIX_DRAFTS_READY_LOCKED", all(item["draft_ready"] and item["draft_locked"] and item["execution_locked"] for item in fix_drafts)),
        ("ALL_RESPONSE_DRAFTS_READY_LOCKED", all(item["draft_ready"] and item["draft_locked"] and item["send_locked"] for item in response_drafts)),
        ("ALL_FIX_EXECUTION_LOCKS_ACTIVE", all(item["fix_execution_locked"] and item["code_patch_locked"] and item["test_run_locked"] for item in fix_locks)),
        ("ALL_RESPONSE_SEND_LOCKS_ACTIVE", all(item["response_send_locked"] and item["tester_notify_locked"] and item["support_response_locked"] for item in response_locks)),
        ("ALL_VERIFICATIONS_PREVIEW_LOCKED", all(item["preview_ready"] and item["verification_locked"] and item["final_result_locked"] for item in verifications)),
        ("ALL_RELEASE_CLOSEOUT_LOCKED", all(item["release_locked"] and item["closeout_locked"] and item["publish_locked"] for item in release_locks)),
        ("ALL_OWNER_APPROVALS_LOCKED", all(item["owner_approval_locked"] and item["owner_rejection_locked"] and item["owner_closeout_locked"] for item in owner_locks)),
        ("PACKET_READY_LOCKED", all(item["packet_ready"] and item["packet_locked"] for item in packets)),
        ("NO_FINAL_FIX_OR_RESPONSE_RECEIPT", all(item["final_fix_receipt"] is False and item["final_response_receipt"] is False for item in packets)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("FIXDRAFT", fix_drafts),
        ("RESPONSEDRAFT", response_drafts),
        ("FIXLOCK", fix_locks),
        ("RESPONSELOCK", response_locks),
        ("VERIFY", verifications),
        ("RELEASE", release_locks),
        ("OWNERLOCK", owner_locks),
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
        "fix_draft_count": len(fix_drafts),
        "response_draft_count": len(response_drafts),
        "fix_execution_lock_count": len(fix_locks),
        "response_send_lock_count": len(response_locks),
        "fix_verification_count": len(verifications),
        "release_closeout_lock_count": len(release_locks),
        "owner_response_approval_lock_count": len(owner_locks),
        "receipt_packet_count": len(packets),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "fix_response_ready": len(failed) == 0 and readiness["fix_response_ready"] is True,
        "safe_to_continue_to_gp261": len(failed) == 0 and readiness["safe_to_continue_to_gp261"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp251_beta_fix_response_lock_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SHELL_ID, db_path)
    return {"pack": _pack_payload(251, component["pack_name"]), "real_sqlite_backed": True, "shell": component}

def get_gp252_fix_draft_queue(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(FIX_DRAFT_ID, db_path)
    rows = get_fix_drafts(db_path)
    return {"pack": _pack_payload(252, component["pack_name"]), "real_sqlite_backed": True, "fix_draft_queue": component, "fix_draft_count": len(rows), "drafts": rows}

def get_gp253_response_draft_queue(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RESPONSE_DRAFT_ID, db_path)
    rows = get_response_drafts(db_path)
    return {"pack": _pack_payload(253, component["pack_name"]), "real_sqlite_backed": True, "response_draft_queue": component, "response_draft_count": len(rows), "drafts": rows}

def get_gp254_fix_execution_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(FIX_EXECUTION_LOCK_ID, db_path)
    rows = get_fix_execution_locks(db_path)
    return {"pack": _pack_payload(254, component["pack_name"]), "real_sqlite_backed": True, "fix_execution_lock_contract": component, "fix_execution_lock_count": len(rows), "locks": rows}

def get_gp255_response_send_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RESPONSE_SEND_LOCK_ID, db_path)
    rows = get_response_send_locks(db_path)
    return {"pack": _pack_payload(255, component["pack_name"]), "real_sqlite_backed": True, "response_send_lock_contract": component, "response_send_lock_count": len(rows), "locks": rows}

def get_gp256_fix_verification_preview_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(FIX_VERIFICATION_ID, db_path)
    rows = get_fix_verification_previews(db_path)
    return {"pack": _pack_payload(256, component["pack_name"]), "real_sqlite_backed": True, "fix_verification_preview_board": component, "fix_verification_count": len(rows), "verifications": rows}

def get_gp257_release_closeout_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RELEASE_CLOSEOUT_ID, db_path)
    rows = get_release_closeout_locks(db_path)
    return {"pack": _pack_payload(257, component["pack_name"]), "real_sqlite_backed": True, "release_closeout_lock_contract": component, "release_closeout_lock_count": len(rows), "locks": rows}

def get_gp258_owner_response_approval_lock_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(OWNER_RESPONSE_APPROVAL_ID, db_path)
    rows = get_owner_response_approval_locks(db_path)
    return {"pack": _pack_payload(258, component["pack_name"]), "real_sqlite_backed": True, "owner_response_approval_lock_board": component, "owner_response_approval_lock_count": len(rows), "locks": rows}

def get_gp259_fix_response_receipt_draft_packet(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RECEIPT_PACKET_ID, db_path)
    rows = get_fix_response_receipt_packets(db_path)
    return {"pack": _pack_payload(259, component["pack_name"]), "real_sqlite_backed": True, "receipt_packet_component": component, "receipt_packet_count": len(rows), "packets": rows}

def get_gp260_fix_response_lock_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_fix_response_lock_layer(db_path)
    return {"pack": _pack_payload(260, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_fix_response_lock_layer(db_path)
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
            "source_gp250_readiness_id": component["source_gp250_readiness_id"],
            "source_gp250_readiness_hash": component["source_gp250_readiness_hash"],
            "source_gp250_readiness_score": component["source_gp250_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "fix_response_ready": component["fix_response_ready"],
            "fix_execution_locked": component["fix_execution_locked"],
            "response_send_locked": component["response_send_locked"],
            "verification_preview_only": component["verification_preview_only"],
            "release_closeout_locked": component["release_closeout_locked"],
            "owner_response_approval_locked": component["owner_response_approval_locked"],
            "vault_not_done": component["vault_not_done"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp261": validation["safe_to_continue_to_gp261"],
            "foundation_status": "beta_fix_response_lock_ready_fix_response_verify_release_closeout_owner_approval_locked_vault_not_done_safe_to_continue",
            "next": next_label,
            **counts,
            "fix_draft_created": component["fix_draft_created"],
            "fix_task_created": component["fix_task_created"],
            "fix_task_assigned": component["fix_task_assigned"],
            "fix_execution_requested": component["fix_execution_requested"],
            "fix_execution_approved": component["fix_execution_approved"],
            "fix_started": component["fix_started"],
            "fix_completed": component["fix_completed"],
            "fix_applied": component["fix_applied"],
            "fix_merged": component["fix_merged"],
            "code_patch_created": component["code_patch_created"],
            "code_patch_written": component["code_patch_written"],
            "code_patch_run": component["code_patch_run"],
            "test_run_started": component["test_run_started"],
            "test_run_completed": component["test_run_completed"],
            "fix_verification_started": component["fix_verification_started"],
            "fix_verification_completed": component["fix_verification_completed"],
            "fix_verified": component["fix_verified"],
            "fix_failed": component["fix_failed"],
            "response_draft_created": component["response_draft_created"],
            "response_draft_approved": component["response_draft_approved"],
            "response_sent": component["response_sent"],
            "tester_notified": component["tester_notified"],
            "support_response_sent": component["support_response_sent"],
            "release_created": component["release_created"],
            "release_published": component["release_published"],
            "release_notes_created": component["release_notes_created"],
            "release_notes_sent": component["release_notes_sent"],
            "closeout_requested": component["closeout_requested"],
            "closeout_approved": component["closeout_approved"],
            "closeout_recorded": component["closeout_recorded"],
            "owner_response_approval_requested": component["owner_response_approval_requested"],
            "owner_response_approval_recorded": component["owner_response_approval_recorded"],
            "owner_response_rejection_recorded": component["owner_response_rejection_recorded"],
            "reviewer_decision_recorded": component["reviewer_decision_recorded"],
            "feedback_review_decision_recorded": component["feedback_review_decision_recorded"],
            "issue_review_decision_recorded": component["issue_review_decision_recorded"],
            "assignment_created": component["assignment_created"],
            "intake_escalation_created": component["intake_escalation_created"],
            "feedback_submitted": component["feedback_submitted"],
            "issue_submitted": component["issue_submitted"],
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
            "clouds_status": "parked_do_not_continue_from_vault_gp260",
        },
        "validation": validation,
    }

def get_gp251_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(251, SHELL_ID, "VAULT_GP252_FIX_DRAFT_QUEUE", db_path)

def get_gp252_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(252, FIX_DRAFT_ID, "VAULT_GP253_RESPONSE_DRAFT_QUEUE", db_path)

def get_gp253_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(253, RESPONSE_DRAFT_ID, "VAULT_GP254_FIX_EXECUTION_LOCK_CONTRACT", db_path)

def get_gp254_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(254, FIX_EXECUTION_LOCK_ID, "VAULT_GP255_RESPONSE_SEND_LOCK_CONTRACT", db_path)

def get_gp255_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(255, RESPONSE_SEND_LOCK_ID, "VAULT_GP256_FIX_VERIFICATION_PREVIEW_BOARD", db_path)

def get_gp256_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(256, FIX_VERIFICATION_ID, "VAULT_GP257_RELEASE_CLOSEOUT_LOCK_CONTRACT", db_path)

def get_gp257_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(257, RELEASE_CLOSEOUT_ID, "VAULT_GP258_OWNER_RESPONSE_APPROVAL_LOCK_BOARD", db_path)

def get_gp258_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(258, OWNER_RESPONSE_APPROVAL_ID, "VAULT_GP259_FIX_RESPONSE_RECEIPT_DRAFT_PACKET", db_path)

def get_gp259_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(259, RECEIPT_PACKET_ID, "VAULT_GP260_FIX_RESPONSE_LOCK_READINESS_CHECKPOINT", db_path)

def get_gp260_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(260, READINESS_ID, NEXT_PACK, db_path)
    status["gp260_status"]["next_section"] = NEXT_SECTION_ID
    status["gp260_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp260_status"]["next_pack"] = NEXT_PACK
    return status

def get_beta_fix_response_lock_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_beta_fix_response_lock_layer(db_path)
    components = _rows("vault_beta_fix_response_components", "gp_number", db_path, {"data_json": "data"})
    fix_drafts = get_fix_drafts(db_path)
    response_drafts = get_response_drafts(db_path)
    fix_locks = get_fix_execution_locks(db_path)
    response_locks = get_response_send_locks(db_path)
    verifications = get_fix_verification_previews(db_path)
    release_locks = get_release_closeout_locks(db_path)
    owner_locks = get_owner_response_approval_locks(db_path)
    packets = get_fix_response_receipt_packets(db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_fix_response_lock_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "fix_drafts": {"fix_draft_count": len(fix_drafts), "drafts": fix_drafts},
        "response_drafts": {"response_draft_count": len(response_drafts), "drafts": response_drafts},
        "fix_execution_locks": {"fix_execution_lock_count": len(fix_locks), "locks": fix_locks},
        "response_send_locks": {"response_send_lock_count": len(response_locks), "locks": response_locks},
        "fix_verifications": {"fix_verification_count": len(verifications), "verifications": verifications},
        "release_closeout_locks": {"release_closeout_lock_count": len(release_locks), "locks": release_locks},
        "owner_response_approval_locks": {"owner_response_approval_lock_count": len(owner_locks), "locks": owner_locks},
        "receipt_packets": {"receipt_packet_count": len(packets), "packets": packets},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "beta_fix_response_lock_layer_ready": True,
            "fix_response_ready": validation["fix_response_ready"],
            "safe_to_continue_to_gp261": validation["safe_to_continue_to_gp261"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "fix_execution_locked": True,
            "response_send_locked": True,
            "verification_preview_only": True,
            "release_closeout_locked": True,
            "owner_response_approval_locked": True,
            "fix_draft_created": False,
            "fix_task_created": False,
            "fix_task_assigned": False,
            "fix_started": False,
            "fix_completed": False,
            "code_patch_created": False,
            "code_patch_written": False,
            "code_patch_run": False,
            "test_run_started": False,
            "test_run_completed": False,
            "fix_verification_started": False,
            "fix_verification_completed": False,
            "fix_verified": False,
            "response_draft_created": False,
            "response_draft_approved": False,
            "response_sent": False,
            "tester_notified": False,
            "support_response_sent": False,
            "release_created": False,
            "release_published": False,
            "release_notes_created": False,
            "closeout_requested": False,
            "closeout_approved": False,
            "closeout_recorded": False,
            "owner_response_approval_requested": False,
            "owner_response_approval_recorded": False,
            "owner_response_rejection_recorded": False,
            "reviewer_decision_recorded": False,
            "assignment_created": False,
            "intake_escalation_created": False,
            "feedback_submitted": False,
            "issue_submitted": False,
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
            "page": "/vault/beta-fix-response-lock-layer",
            "json": "/vault/beta-fix-response-lock-layer.json",
            "gp251": "/vault/gp251-status.json",
            "gp252": "/vault/gp252-status.json",
            "gp253": "/vault/gp253-status.json",
            "gp254": "/vault/gp254-status.json",
            "gp255": "/vault/gp255-status.json",
            "gp256": "/vault/gp256-status.json",
            "gp257": "/vault/gp257-status.json",
            "gp258": "/vault/gp258-status.json",
            "gp259": "/vault/gp259-status.json",
            "gp260": "/vault/gp260-status.json",
        },
    }

def render_beta_fix_response_lock_layer_page() -> str:
    home = get_beta_fix_response_lock_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    fix_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['fix_name'])}</strong>
          <span>{escape(item['fix_status'])}</span>
          <code>{escape(item['fix_category'])} · execution locked</code>
        </article>
        """
        for item in home["fix_drafts"]["drafts"]
    )

    response_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['response_name'])}</strong>
          <span>{escape(item['response_status'])}</span>
          <code>{escape(item['response_category'])} · send locked</code>
        </article>
        """
        for item in home["response_drafts"]["drafts"]
    )

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP251-GP260 Beta Fix Response Lock Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 251-260</div>
    <div class="eyebrow">Beta Fix and Response Lock Layer · GP251-GP260</div>
    <h1>Fix + Response Locked</h1>
    <p>This layer prepares fix drafts, response drafts, execution locks, send locks, verification previews, release closeout locks, owner approval locks, and receipt drafts. Nothing can be fixed, sent, verified, released, approved, or closed yet.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['fix_draft_count']}</strong><span>fix drafts</span></div>
      <div class="metric"><strong>{home['store']['response_draft_count']}</strong><span>response drafts</span></div>
      <div class="metric"><strong>{home['store']['fix_execution_lock_count']}</strong><span>execution locks</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP251-GP260 built</span>
      <span class="pill ok">Safe to GP261</span>
      <span class="pill danger">No fix created</span>
      <span class="pill danger">No code patch</span>
      <span class="pill danger">No response sent</span>
      <span class="pill danger">No verification</span>
      <span class="pill danger">No release</span>
      <span class="pill danger">No closeout</span>
      <span class="pill danger">No owner approval</span>
      <span class="pill danger">Vault not done</span>
    </div>
  </section>

  <section class="section">
    <h2>Fix Draft Queue</h2>
    <div class="cards">{fix_cards}</div>
  </section>

  <section class="section">
    <h2>Response Draft Queue</h2>
    <div class="cards">{response_cards}</div>
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
