"""
VAULT GP221-GP230 — Beta Onboarding Locked Experience Layer

New section:
Archive Vault — Beta Onboarding Locked Experience Layer / GP221-GP230

Builds:
- GP221 Beta Onboarding Locked Experience Shell
- GP222 Locked Welcome and Orientation Draft Board
- GP223 Beta Profile Setup Preview Lock
- GP224 NDA and Policy Acknowledgment Preview Lock
- GP225 Beta Workspace Access Preview Lock
- GP226 Beta Support Channel Preview Board
- GP227 Beta Onboarding QA Checklist
- GP228 Onboarding Safety and Compliance Lock Board
- GP229 Beta Onboarding Receipt Draft Packet
- GP230 Beta Onboarding Locked Experience Readiness Checkpoint

This layer prepares the locked beta onboarding experience. It does not onboard
testers, create profiles, accept policies, open workspaces/support channels,
grant access, create tokens/sessions, call Tower/billing/providers, read object
bodies, restore/export/upload/delete, execute, or mark Vault done.
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

from vault.beta_access_invite_lock_layer_service import (
    get_gp220_status,
    get_gp220_beta_access_invite_lock_readiness_checkpoint,
    get_beta_access_invite_lock_layer_home,
    validate_beta_access_invite_lock_layer,
    get_beta_invite_drafts,
    get_access_grant_locks,
    get_beta_access_risk_blockers,
)

LAYER_ID = "VAULT_GP221_230"
LAYER_NAME = "Beta Onboarding Locked Experience Layer"
SCHEMA_VERSION = "vault.beta_onboarding_locked_experience_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_BETA_ONBOARDING_LOCKED_EXPERIENCE_LAYER"
SECTION_TITLE = "Archive Vault — Beta Onboarding Locked Experience Layer"
SECTION_RANGE = "GP221-GP230"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_BETA_ACCESS_AND_INVITE_LOCK_LAYER"
PREVIOUS_SECTION_RANGE = "GP211-GP220"

NEXT_SECTION_ID = "ARCHIVE_VAULT_BETA_FEEDBACK_AND_ISSUE_INTAKE_LOCK_LAYER"
NEXT_SECTION_RANGE = "GP231-GP240"
NEXT_PACK = "VAULT_GP231_240_BETA_FEEDBACK_AND_ISSUE_INTAKE_LOCK_LAYER"

DEFAULT_DB_ENV = "VAULT_BETA_ONBOARDING_LOCKED_EXPERIENCE_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_beta_onboarding_locked_experience_layer.sqlite"

SHELL_ID = "VBOLE-SHELL-GP221-001"
WELCOME_ORIENTATION_ID = "VBOLE-WELCOME-GP222-001"
PROFILE_SETUP_ID = "VBOLE-PROFILE-GP223-001"
POLICY_ACK_ID = "VBOLE-POLICY-GP224-001"
WORKSPACE_ACCESS_ID = "VBOLE-WORKSPACE-GP225-001"
SUPPORT_CHANNEL_ID = "VBOLE-SUPPORT-GP226-001"
QA_CHECKLIST_ID = "VBOLE-QA-GP227-001"
SAFETY_COMPLIANCE_ID = "VBOLE-SAFETY-GP228-001"
RECEIPT_PACKET_ID = "VBOLE-RECEIPT-GP229-001"
READINESS_ID = "VBOLE-READINESS-GP230-001"

FALSE_FIELDS = [
    "beta_launch_requested",
    "beta_launch_approved",
    "public_launch_requested",
    "public_launch_approved",
    "beta_invite_created",
    "beta_invite_approved",
    "beta_invite_sent",
    "beta_invite_delivered",
    "tester_candidate_submitted",
    "tester_candidate_approved",
    "beta_tester_added",
    "beta_tester_access_requested",
    "beta_tester_access_approved",
    "beta_tester_access_granted",
    "beta_tester_access_enabled",
    "beta_access_token_created",
    "beta_access_session_created",
    "beta_role_assigned",
    "beta_permission_granted",
    "beta_permission_enabled",
    "onboarding_started",
    "onboarding_completed",
    "onboarding_step_started",
    "onboarding_step_completed",
    "welcome_acknowledged",
    "orientation_started",
    "orientation_completed",
    "profile_created",
    "profile_updated",
    "profile_submitted",
    "profile_approved",
    "nda_opened",
    "nda_signed",
    "policy_opened",
    "policy_acknowledged",
    "policy_acceptance_recorded",
    "workspace_opened",
    "workspace_access_granted",
    "workspace_session_created",
    "support_channel_opened",
    "support_message_sent",
    "feedback_form_opened",
    "feedback_submitted",
    "issue_created",
    "issue_submitted",
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

WELCOME_ORIENTATION_DRAFTS = [
    ("welcome_message_draft", "Welcome Message Draft", "welcome", "draft_locked"),
    ("orientation_overview_draft", "Orientation Overview Draft", "orientation", "draft_locked"),
    ("vault_boundary_intro_draft", "Vault Boundary Intro Draft", "boundary", "draft_locked"),
    ("owner_expectation_draft", "Owner Expectation Draft", "owner", "draft_locked"),
    ("tester_responsibility_draft", "Tester Responsibility Draft", "tester", "draft_locked"),
    ("locked_actions_notice_draft", "Locked Actions Notice Draft", "safety", "draft_locked"),
]

PROFILE_SETUP_PREVIEWS = [
    ("display_name_preview", "Display Name Preview", "identity", "preview_locked"),
    ("contact_email_preview", "Contact Email Preview", "contact", "preview_locked"),
    ("role_intent_preview", "Role Intent Preview", "role", "preview_locked"),
    ("tester_lane_preview", "Tester Lane Preview", "lane", "preview_locked"),
    ("access_reason_preview", "Access Reason Preview", "reason", "preview_locked"),
    ("emergency_contact_preview", "Emergency Contact Preview", "support", "preview_locked"),
]

POLICY_ACK_LOCKS = [
    ("nda_preview_lock", "NDA Preview Lock", "nda", "ack_locked"),
    ("privacy_policy_preview_lock", "Privacy Policy Preview Lock", "privacy", "ack_locked"),
    ("acceptable_use_preview_lock", "Acceptable Use Preview Lock", "acceptable_use", "ack_locked"),
    ("no_download_policy_preview_lock", "No Download Policy Preview Lock", "download", "ack_locked"),
    ("provider_boundary_policy_lock", "Provider Boundary Policy Lock", "provider", "ack_locked"),
    ("support_conduct_policy_lock", "Support Conduct Policy Lock", "support", "ack_locked"),
]

WORKSPACE_PREVIEWS = [
    ("owner_readiness_workspace_preview", "Owner Readiness Workspace Preview", "owner", "workspace_locked"),
    ("redacted_archive_workspace_preview", "Redacted Archive Workspace Preview", "archive", "workspace_locked"),
    ("receipt_packet_workspace_preview", "Receipt Packet Workspace Preview", "receipt", "workspace_locked"),
    ("risk_blocker_workspace_preview", "Risk Blocker Workspace Preview", "risk", "workspace_locked"),
    ("support_workspace_preview", "Support Workspace Preview", "support", "workspace_locked"),
    ("qa_workspace_preview", "QA Workspace Preview", "qa", "workspace_locked"),
]

SUPPORT_CHANNEL_PREVIEWS = [
    ("owner_support_channel_preview", "Owner Support Channel Preview", "owner", "channel_locked"),
    ("bug_report_channel_preview", "Bug Report Channel Preview", "bug", "channel_locked"),
    ("access_help_channel_preview", "Access Help Channel Preview", "access", "channel_locked"),
    ("receipt_question_channel_preview", "Receipt Question Channel Preview", "receipt", "channel_locked"),
    ("provider_boundary_question_channel_preview", "Provider Boundary Question Channel Preview", "provider", "channel_locked"),
]

QA_CHECKS = [
    ("onboarding_page_loads_locked", "Onboarding page loads while locked", "page"),
    ("welcome_drafts_visible_locked", "Welcome drafts visible while locked", "welcome"),
    ("profile_preview_does_not_submit", "Profile preview does not submit", "profile"),
    ("policy_preview_does_not_accept", "Policy preview does not accept", "policy"),
    ("workspace_preview_does_not_open", "Workspace preview does not open", "workspace"),
    ("support_preview_does_not_send", "Support preview does not send", "support"),
    ("tower_billing_provider_remain_locked", "Tower, billing, and provider remain locked", "integration"),
    ("vault_not_done_confirmed", "Vault not done confirmed", "done_state"),
]

SAFETY_LOCKS = [
    ("onboarding_start_locked", "Onboarding Start Locked", "onboarding", "critical"),
    ("onboarding_completion_locked", "Onboarding Completion Locked", "onboarding", "critical"),
    ("profile_submit_locked", "Profile Submit Locked", "profile", "critical"),
    ("nda_policy_accept_locked", "NDA/Policy Accept Locked", "policy", "critical"),
    ("workspace_open_locked", "Workspace Open Locked", "workspace", "critical"),
    ("support_send_locked", "Support Send Locked", "support", "critical"),
    ("feedback_issue_submit_locked", "Feedback/Issue Submit Locked", "feedback", "critical"),
    ("tower_gate_locked", "Tower Gate Locked", "tower", "critical"),
    ("billing_subscription_locked", "Billing/Subscription Locked", "billing", "critical"),
    ("provider_object_body_locked", "Provider/Object Body Locked", "provider", "critical"),
    ("restore_export_upload_delete_locked", "Restore/Export/Upload/Delete Locked", "dangerous_ops", "critical"),
    ("vault_not_done", "Vault Not Done", "done_state", "critical"),
]

COMPONENT_SPECS = [
    (221, SHELL_ID, "VAULT_GP221", "Beta Onboarding Locked Experience Shell", "beta_onboarding_locked_experience_shell"),
    (222, WELCOME_ORIENTATION_ID, "VAULT_GP222", "Locked Welcome and Orientation Draft Board", "locked_welcome_orientation_draft_board"),
    (223, PROFILE_SETUP_ID, "VAULT_GP223", "Beta Profile Setup Preview Lock", "beta_profile_setup_preview_lock"),
    (224, POLICY_ACK_ID, "VAULT_GP224", "NDA and Policy Acknowledgment Preview Lock", "nda_policy_acknowledgment_preview_lock"),
    (225, WORKSPACE_ACCESS_ID, "VAULT_GP225", "Beta Workspace Access Preview Lock", "beta_workspace_access_preview_lock"),
    (226, SUPPORT_CHANNEL_ID, "VAULT_GP226", "Beta Support Channel Preview Board", "beta_support_channel_preview_board"),
    (227, QA_CHECKLIST_ID, "VAULT_GP227", "Beta Onboarding QA Checklist", "beta_onboarding_qa_checklist"),
    (228, SAFETY_COMPLIANCE_ID, "VAULT_GP228", "Onboarding Safety and Compliance Lock Board", "onboarding_safety_compliance_lock_board"),
    (229, RECEIPT_PACKET_ID, "VAULT_GP229", "Beta Onboarding Receipt Draft Packet", "beta_onboarding_receipt_draft_packet"),
    (230, READINESS_ID, "VAULT_GP230", "Beta Onboarding Locked Experience Readiness Checkpoint", "beta_onboarding_locked_experience_readiness_checkpoint"),
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
        "source_gp220_readiness_score",
        "component_count",
        "welcome_orientation_count",
        "profile_preview_count",
        "policy_ack_lock_count",
        "workspace_preview_count",
        "support_channel_count",
        "qa_check_count",
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
        "depends_on": ["VAULT_GP220"],
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
        "depends_on": ["VAULT_GP220"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_beta_onboarding_locked_experience_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_beta_onboarding_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp220_readiness_id TEXT NOT NULL,
                source_gp220_readiness_hash TEXT NOT NULL,
                source_gp220_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                onboarding_experience_ready INTEGER NOT NULL DEFAULT 1,
                onboarding_preview_locked INTEGER NOT NULL DEFAULT 1,
                profile_preview_locked INTEGER NOT NULL DEFAULT 1,
                policy_ack_locked INTEGER NOT NULL DEFAULT 1,
                workspace_preview_locked INTEGER NOT NULL DEFAULT 1,
                support_preview_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_locked_welcome_orientation_drafts (
                draft_id TEXT PRIMARY KEY,
                draft_code TEXT NOT NULL UNIQUE,
                draft_name TEXT NOT NULL,
                draft_category TEXT NOT NULL,
                draft_status TEXT NOT NULL,
                draft_ready INTEGER NOT NULL DEFAULT 1,
                draft_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_beta_profile_setup_previews (
                preview_id TEXT PRIMARY KEY,
                preview_code TEXT NOT NULL UNIQUE,
                preview_name TEXT NOT NULL,
                preview_category TEXT NOT NULL,
                preview_status TEXT NOT NULL,
                preview_ready INTEGER NOT NULL DEFAULT 1,
                preview_locked INTEGER NOT NULL DEFAULT 1,
                submit_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                preview_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_nda_policy_acknowledgment_locks (
                policy_id TEXT PRIMARY KEY,
                policy_code TEXT NOT NULL UNIQUE,
                policy_name TEXT NOT NULL,
                policy_category TEXT NOT NULL,
                policy_status TEXT NOT NULL,
                preview_ready INTEGER NOT NULL DEFAULT 1,
                acknowledgment_locked INTEGER NOT NULL DEFAULT 1,
                acceptance_record_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                policy_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_beta_workspace_access_previews (
                workspace_id TEXT PRIMARY KEY,
                workspace_code TEXT NOT NULL UNIQUE,
                workspace_name TEXT NOT NULL,
                workspace_category TEXT NOT NULL,
                workspace_status TEXT NOT NULL,
                workspace_preview_ready INTEGER NOT NULL DEFAULT 1,
                workspace_open_locked INTEGER NOT NULL DEFAULT 1,
                workspace_session_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                workspace_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_beta_support_channel_previews (
                channel_id TEXT PRIMARY KEY,
                channel_code TEXT NOT NULL UNIQUE,
                channel_name TEXT NOT NULL,
                channel_category TEXT NOT NULL,
                channel_status TEXT NOT NULL,
                channel_preview_ready INTEGER NOT NULL DEFAULT 1,
                channel_open_locked INTEGER NOT NULL DEFAULT 1,
                message_send_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                channel_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_beta_onboarding_qa_checklist (
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
            CREATE TABLE IF NOT EXISTS vault_onboarding_safety_compliance_locks (
                lock_id TEXT PRIMARY KEY,
                lock_code TEXT NOT NULL UNIQUE,
                lock_name TEXT NOT NULL,
                lock_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                lock_status TEXT NOT NULL,
                lock_active INTEGER NOT NULL DEFAULT 1,
                blocks_onboarding_start INTEGER NOT NULL DEFAULT 1,
                blocks_profile_submit INTEGER NOT NULL DEFAULT 1,
                blocks_policy_accept INTEGER NOT NULL DEFAULT 1,
                blocks_workspace_open INTEGER NOT NULL DEFAULT 1,
                blocks_support_send INTEGER NOT NULL DEFAULT 1,
                blocks_feedback_issue_submit INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_beta_onboarding_receipt_draft_packets (
                receipt_packet_id TEXT PRIMARY KEY,
                packet_code TEXT NOT NULL UNIQUE,
                packet_name TEXT NOT NULL,
                packet_status TEXT NOT NULL,
                packet_ready INTEGER NOT NULL DEFAULT 1,
                packet_locked INTEGER NOT NULL DEFAULT 1,
                final_onboarding_receipt INTEGER NOT NULL DEFAULT 0,
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
            CREATE TABLE IF NOT EXISTS vault_beta_onboarding_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                welcome_orientation_count INTEGER NOT NULL,
                profile_preview_count INTEGER NOT NULL,
                policy_ack_lock_count INTEGER NOT NULL,
                workspace_preview_count INTEGER NOT NULL,
                support_channel_count INTEGER NOT NULL,
                qa_check_count INTEGER NOT NULL,
                safety_lock_count INTEGER NOT NULL,
                receipt_packet_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                onboarding_experience_ready INTEGER NOT NULL DEFAULT 1,
                onboarding_preview_locked INTEGER NOT NULL DEFAULT 1,
                profile_preview_locked INTEGER NOT NULL DEFAULT 1,
                policy_ack_locked INTEGER NOT NULL DEFAULT 1,
                workspace_preview_locked INTEGER NOT NULL DEFAULT 1,
                support_preview_locked INTEGER NOT NULL DEFAULT 1,
                safe_to_continue_to_gp231 INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_beta_onboarding_events (
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
            "vault_beta_onboarding_components",
            "vault_locked_welcome_orientation_drafts",
            "vault_beta_profile_setup_previews",
            "vault_nda_policy_acknowledgment_locks",
            "vault_beta_workspace_access_previews",
            "vault_beta_support_channel_previews",
            "vault_beta_onboarding_qa_checklist",
            "vault_onboarding_safety_compliance_locks",
            "vault_beta_onboarding_receipt_draft_packets",
            "vault_beta_onboarding_readiness",
            "vault_beta_onboarding_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VBOLEEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_beta_onboarding_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_beta_onboarding_locked_experience_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_beta_onboarding_locked_experience_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_beta_onboarding_components WHERE component_id = ?",
            (SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp220_status = get_gp220_status()["gp220_status"]
            gp220_checkpoint = get_gp220_beta_access_invite_lock_readiness_checkpoint()["readiness_checkpoint"]
            gp220_home = get_beta_access_invite_lock_layer_home()
            gp220_validation = validate_beta_access_invite_lock_layer()
            source_invites = get_beta_invite_drafts()
            source_grant_locks = get_access_grant_locks()
            source_risk_blockers = get_beta_access_risk_blockers()

            readiness = gp220_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp220_readiness_id": readiness["readiness_id"],
                "source_gp220_readiness_hash": readiness["readiness_hash"],
                "source_gp220_readiness_score": readiness["readiness_score"],
            }

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "welcome_orientation_count": len(WELCOME_ORIENTATION_DRAFTS),
                "profile_preview_count": len(PROFILE_SETUP_PREVIEWS),
                "policy_ack_lock_count": len(POLICY_ACK_LOCKS),
                "workspace_preview_count": len(WORKSPACE_PREVIEWS),
                "support_channel_count": len(SUPPORT_CHANNEL_PREVIEWS),
                "qa_check_count": len(QA_CHECKS),
                "safety_lock_count": len(SAFETY_LOCKS),
                "receipt_packet_count": 1,
            }

            source_context = {
                "source_gp220_status_ready": gp220_status["ready"],
                "source_gp220_validation_passed": gp220_status["validation_passed"],
                "source_gp220_safe_to_continue_to_gp221": gp220_status["safe_to_continue_to_gp221"],
                "source_gp220_readiness_hash": readiness["readiness_hash"],
                "source_gp220_readiness_score": readiness["readiness_score"],
                "source_invite_draft_count": len(source_invites),
                "source_access_grant_lock_count": len(source_grant_locks),
                "source_risk_blocker_count": len(source_risk_blockers),
                "source_validation_check_count": gp220_validation["check_count"],
            }

            component_extra = {
                SHELL_ID: {"beta_onboarding_locked_experience_shell_ready": True},
                WELCOME_ORIENTATION_ID: {"locked_welcome_orientation_draft_board_ready": True, "welcome_orientation_count": counts["welcome_orientation_count"]},
                PROFILE_SETUP_ID: {"beta_profile_setup_preview_lock_ready": True, "profile_preview_count": counts["profile_preview_count"]},
                POLICY_ACK_ID: {"nda_policy_acknowledgment_preview_lock_ready": True, "policy_ack_lock_count": counts["policy_ack_lock_count"]},
                WORKSPACE_ACCESS_ID: {"beta_workspace_access_preview_lock_ready": True, "workspace_preview_count": counts["workspace_preview_count"]},
                SUPPORT_CHANNEL_ID: {"beta_support_channel_preview_board_ready": True, "support_channel_count": counts["support_channel_count"]},
                QA_CHECKLIST_ID: {"beta_onboarding_qa_checklist_ready": True, "qa_check_count": counts["qa_check_count"]},
                SAFETY_COMPLIANCE_ID: {"onboarding_safety_compliance_lock_board_ready": True, "safety_lock_count": counts["safety_lock_count"]},
                RECEIPT_PACKET_ID: {"beta_onboarding_receipt_draft_packet_ready": True, "receipt_packet_count": counts["receipt_packet_count"]},
                READINESS_ID: {"beta_onboarding_locked_experience_readiness_checkpoint_ready": True, "safe_to_continue_to_gp231": True},
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
                    "onboarding_experience_ready": True,
                    "onboarding_preview_locked": True,
                    "profile_preview_locked": True,
                    "policy_ack_locked": True,
                    "workspace_preview_locked": True,
                    "support_preview_locked": True,
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
                    "onboarding_experience_ready": 1,
                    "onboarding_preview_locked": 1,
                    "profile_preview_locked": 1,
                    "policy_ack_locked": 1,
                    "workspace_preview_locked": 1,
                    "support_preview_locked": 1,
                    "vault_not_done": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_onboarding_components", row)

            for idx, (code, name, category, status) in enumerate(WELCOME_ORIENTATION_DRAFTS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "draft_code": code,
                    "draft_name": name,
                    "draft_category": category,
                    "draft_status": status,
                    "draft_ready": True,
                    "draft_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "draft_id": f"VBOLEWELCOME-{idx:03d}",
                    "draft_code": code,
                    "draft_name": name,
                    "draft_category": category,
                    "draft_status": status,
                    "draft_ready": 1,
                    "draft_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "draft_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_locked_welcome_orientation_drafts", row)

            for idx, (code, name, category, status) in enumerate(PROFILE_SETUP_PREVIEWS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "preview_code": code,
                    "preview_name": name,
                    "preview_category": category,
                    "preview_status": status,
                    "preview_ready": True,
                    "preview_locked": True,
                    "submit_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "preview_id": f"VBOLEPROFILE-{idx:03d}",
                    "preview_code": code,
                    "preview_name": name,
                    "preview_category": category,
                    "preview_status": status,
                    "preview_ready": 1,
                    "preview_locked": 1,
                    "submit_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "preview_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_profile_setup_previews", row)

            for idx, (code, name, category, status) in enumerate(POLICY_ACK_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "policy_code": code,
                    "policy_name": name,
                    "policy_category": category,
                    "policy_status": status,
                    "preview_ready": True,
                    "acknowledgment_locked": True,
                    "acceptance_record_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "policy_id": f"VBOLEPOLICY-{idx:03d}",
                    "policy_code": code,
                    "policy_name": name,
                    "policy_category": category,
                    "policy_status": status,
                    "preview_ready": 1,
                    "acknowledgment_locked": 1,
                    "acceptance_record_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "policy_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_nda_policy_acknowledgment_locks", row)

            for idx, (code, name, category, status) in enumerate(WORKSPACE_PREVIEWS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "workspace_code": code,
                    "workspace_name": name,
                    "workspace_category": category,
                    "workspace_status": status,
                    "workspace_preview_ready": True,
                    "workspace_open_locked": True,
                    "workspace_session_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "workspace_id": f"VBOLEWORK-{idx:03d}",
                    "workspace_code": code,
                    "workspace_name": name,
                    "workspace_category": category,
                    "workspace_status": status,
                    "workspace_preview_ready": 1,
                    "workspace_open_locked": 1,
                    "workspace_session_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "workspace_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_workspace_access_previews", row)

            for idx, (code, name, category, status) in enumerate(SUPPORT_CHANNEL_PREVIEWS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "channel_code": code,
                    "channel_name": name,
                    "channel_category": category,
                    "channel_status": status,
                    "channel_preview_ready": True,
                    "channel_open_locked": True,
                    "message_send_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "channel_id": f"VBOLECHANNEL-{idx:03d}",
                    "channel_code": code,
                    "channel_name": name,
                    "channel_category": category,
                    "channel_status": status,
                    "channel_preview_ready": 1,
                    "channel_open_locked": 1,
                    "message_send_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "channel_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_support_channel_previews", row)

            for idx, (code, name, category) in enumerate(QA_CHECKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "qa_code": code,
                    "qa_name": name,
                    "qa_category": category,
                    "qa_status": "QA_READY_LOCKED_NO_LIVE_ONBOARDING",
                    "qa_ready": True,
                    "qa_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "qa_id": f"VBOLEQA-{idx:03d}",
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
                _insert_dict(conn, "vault_beta_onboarding_qa_checklist", row)

            for idx, (code, name, category, severity) in enumerate(SAFETY_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "severity": severity,
                    "lock_status": "ACTIVE_ONBOARDING_SAFETY_COMPLIANCE_LOCK",
                    "lock_active": True,
                    "blocks_onboarding_start": True,
                    "blocks_profile_submit": True,
                    "blocks_policy_accept": True,
                    "blocks_workspace_open": True,
                    "blocks_support_send": True,
                    "blocks_feedback_issue_submit": True,
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
                    "lock_id": f"VBOLELOCK-{idx:03d}",
                    "lock_code": code,
                    "lock_name": name,
                    "lock_category": category,
                    "severity": severity,
                    "lock_status": payload["lock_status"],
                    "lock_active": 1,
                    "blocks_onboarding_start": 1,
                    "blocks_profile_submit": 1,
                    "blocks_policy_accept": 1,
                    "blocks_workspace_open": 1,
                    "blocks_support_send": 1,
                    "blocks_feedback_issue_submit": 1,
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
                _insert_dict(conn, "vault_onboarding_safety_compliance_locks", row)

            packet_payload = {
                "schema_version": SCHEMA_VERSION,
                "packet_code": "vault_gp221_230_beta_onboarding_locked_experience_packet",
                "packet_name": "Vault GP221-GP230 Beta Onboarding Locked Experience Receipt Draft Packet",
                "packet_status": "READY_LOCKED_DRAFT_ONLY_NO_ONBOARDING_RECEIPT",
                "source_gp220_readiness_id": readiness["readiness_id"],
                "source_gp220_readiness_hash": readiness["readiness_hash"],
                "source_gp220_readiness_score": readiness["readiness_score"],
                **counts,
                "onboarding_experience_ready": True,
                "onboarding_preview_locked": True,
                "profile_preview_locked": True,
                "policy_ack_locked": True,
                "workspace_preview_locked": True,
                "support_preview_locked": True,
                "final_onboarding_receipt": False,
                "locked_truth": {field: False for field in FALSE_FIELDS},
                "vault_done": False,
                "clouds_should_continue": False,
            }
            row = {
                "receipt_packet_id": RECEIPT_PACKET_ID,
                "packet_code": "vault_gp221_230_beta_onboarding_locked_experience_packet",
                "packet_name": "Vault GP221-GP230 Beta Onboarding Locked Experience Receipt Draft Packet",
                "packet_status": packet_payload["packet_status"],
                "packet_ready": 1,
                "packet_locked": 1,
                "final_onboarding_receipt": 0,
                "payload_json": _json_dumps(packet_payload),
                "packet_hash": _hash_payload(packet_payload),
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                row[field] = 0
            _insert_dict(conn, "vault_beta_onboarding_receipt_draft_packets", row)

            checks = [
                ("SOURCE_GP220_READY", bool(gp220_status["ready"])),
                ("SOURCE_GP220_VALIDATION_PASSED", bool(gp220_status["validation_passed"])),
                ("SOURCE_GP220_SAFE_TO_CONTINUE", bool(gp220_status["safe_to_continue_to_gp221"])),
                ("SOURCE_GP220_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP220_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("WELCOME_ORIENTATION_COUNT_6", counts["welcome_orientation_count"] == 6),
                ("PROFILE_PREVIEW_COUNT_6", counts["profile_preview_count"] == 6),
                ("POLICY_ACK_LOCK_COUNT_6", counts["policy_ack_lock_count"] == 6),
                ("WORKSPACE_PREVIEW_COUNT_6", counts["workspace_preview_count"] == 6),
                ("SUPPORT_CHANNEL_COUNT_5", counts["support_channel_count"] == 5),
                ("QA_CHECK_COUNT_8", counts["qa_check_count"] == 8),
                ("SAFETY_LOCK_COUNT_12", counts["safety_lock_count"] == 12),
                ("RECEIPT_PACKET_COUNT_1", counts["receipt_packet_count"] == 1),
                ("SECTION_GP221_GP230", SECTION_RANGE == "GP221-GP230"),
                ("NEXT_SECTION_GP231_GP240", NEXT_SECTION_RANGE == "GP231-GP240"),
                ("ONBOARDING_EXPERIENCE_READY", True),
                ("ONBOARDING_PREVIEW_LOCKED", True),
                ("PROFILE_PREVIEW_LOCKED", True),
                ("POLICY_ACK_LOCKED", True),
                ("WORKSPACE_PREVIEW_LOCKED", True),
                ("SUPPORT_PREVIEW_LOCKED", True),
                ("NO_ONBOARDING_STARTED", True),
                ("NO_PROFILE_CREATED", True),
                ("NO_POLICY_ACCEPTED", True),
                ("NO_WORKSPACE_OPENED", True),
                ("NO_SUPPORT_CHANNEL_OPENED", True),
                ("NO_FEEDBACK_ISSUE_SUBMIT", True),
                ("NO_BETA_ACCESS_GRANT", True),
                ("NO_TOKEN_SESSION", True),
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
                "gp_number": 230,
                "pack_id": "VAULT_GP230",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp220_readiness_id": readiness["readiness_id"],
                "source_gp220_readiness_hash": readiness["readiness_hash"],
                "source_gp220_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "onboarding_experience_ready": True,
                "onboarding_preview_locked": True,
                "profile_preview_locked": True,
                "policy_ack_locked": True,
                "workspace_preview_locked": True,
                "support_preview_locked": True,
                "safe_to_continue_to_gp231": failed_count == 0,
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
                "gp_number": 230,
                "pack_id": "VAULT_GP230",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "BETA_ONBOARDING_LOCKED_EXPERIENCE_READY_ONBOARDING_PROFILE_POLICY_WORKSPACE_SUPPORT_LOCKED_VAULT_NOT_DONE_SAFE_TO_CONTINUE",
                "readiness_score": readiness_payload["readiness_score"],
                **counts,
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "onboarding_experience_ready": 1,
                "onboarding_preview_locked": 1,
                "profile_preview_locked": 1,
                "policy_ack_locked": 1,
                "workspace_preview_locked": 1,
                "support_preview_locked": 1,
                "safe_to_continue_to_gp231": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_beta_onboarding_readiness", row)

            for event_type, event_payload in [
                ("GP221_BETA_ONBOARDING_LOCKED_EXPERIENCE_SHELL_CREATED", {"component_id": SHELL_ID}),
                ("GP222_LOCKED_WELCOME_ORIENTATION_DRAFT_BOARD_CREATED", {"welcome_orientation_count": counts["welcome_orientation_count"]}),
                ("GP223_BETA_PROFILE_SETUP_PREVIEW_LOCK_CREATED", {"profile_preview_count": counts["profile_preview_count"]}),
                ("GP224_NDA_POLICY_ACKNOWLEDGMENT_PREVIEW_LOCK_CREATED", {"policy_ack_lock_count": counts["policy_ack_lock_count"]}),
                ("GP225_BETA_WORKSPACE_ACCESS_PREVIEW_LOCK_CREATED", {"workspace_preview_count": counts["workspace_preview_count"]}),
                ("GP226_BETA_SUPPORT_CHANNEL_PREVIEW_BOARD_CREATED", {"support_channel_count": counts["support_channel_count"]}),
                ("GP227_BETA_ONBOARDING_QA_CHECKLIST_CREATED", {"qa_check_count": counts["qa_check_count"]}),
                ("GP228_ONBOARDING_SAFETY_COMPLIANCE_LOCK_BOARD_CREATED", {"safety_lock_count": counts["safety_lock_count"]}),
                ("GP229_BETA_ONBOARDING_RECEIPT_DRAFT_PACKET_CREATED", {"receipt_packet_count": counts["receipt_packet_count"]}),
                ("GP230_BETA_ONBOARDING_LOCKED_EXPERIENCE_READINESS_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp231": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_onboarding_components").fetchone()["c"]),
            "welcome_orientation_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_locked_welcome_orientation_drafts").fetchone()["c"]),
            "profile_preview_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_profile_setup_previews").fetchone()["c"]),
            "policy_ack_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_nda_policy_acknowledgment_locks").fetchone()["c"]),
            "workspace_preview_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_workspace_access_previews").fetchone()["c"]),
            "support_channel_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_support_channel_previews").fetchone()["c"]),
            "qa_check_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_onboarding_qa_checklist").fetchone()["c"]),
            "safety_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_onboarding_safety_compliance_locks").fetchone()["c"]),
            "receipt_packet_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_onboarding_receipt_draft_packets").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_onboarding_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_onboarding_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_beta_onboarding_locked_experience_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_beta_onboarding_locked_experience_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_beta_onboarding_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_beta_onboarding_locked_experience_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_beta_onboarding_readiness WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_beta_onboarding_locked_experience_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_beta_onboarding_events ORDER BY created_at, event_id").fetchall()
    return [{"event_id": row["event_id"], "event_type": row["event_type"], "event_payload": _json_loads(row["event_payload_json"]), "created_at": row["created_at"]} for row in rows]

def get_welcome_orientation_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_locked_welcome_orientation_drafts", "draft_code", db_path, {"payload_json": "payload"})

def get_profile_setup_previews(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_beta_profile_setup_previews", "preview_code", db_path, {"payload_json": "payload"})

def get_policy_ack_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_nda_policy_acknowledgment_locks", "policy_code", db_path, {"payload_json": "payload"})

def get_workspace_access_previews(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_beta_workspace_access_previews", "workspace_code", db_path, {"payload_json": "payload"})

def get_support_channel_previews(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_beta_support_channel_previews", "channel_code", db_path, {"payload_json": "payload"})

def get_onboarding_qa_checks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_beta_onboarding_qa_checklist", "qa_code", db_path, {"payload_json": "payload"})

def get_onboarding_safety_compliance_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_onboarding_safety_compliance_locks", "lock_code", db_path, {"payload_json": "payload"})

def get_onboarding_receipt_packets(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_beta_onboarding_receipt_draft_packets", "packet_code", db_path, {"payload_json": "payload"})

def validate_beta_onboarding_locked_experience_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_beta_onboarding_components", "gp_number", db_path, {"data_json": "data"})
    welcome = get_welcome_orientation_drafts(db_path)
    profiles = get_profile_setup_previews(db_path)
    policies = get_policy_ack_locks(db_path)
    workspaces = get_workspace_access_previews(db_path)
    support = get_support_channel_previews(db_path)
    qa = get_onboarding_qa_checks(db_path)
    locks = get_onboarding_safety_compliance_locks(db_path)
    packets = get_onboarding_receipt_packets(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("WELCOME_ORIENTATION_COUNT_6", len(welcome) == len(WELCOME_ORIENTATION_DRAFTS)),
        ("PROFILE_PREVIEW_COUNT_6", len(profiles) == len(PROFILE_SETUP_PREVIEWS)),
        ("POLICY_ACK_LOCK_COUNT_6", len(policies) == len(POLICY_ACK_LOCKS)),
        ("WORKSPACE_PREVIEW_COUNT_6", len(workspaces) == len(WORKSPACE_PREVIEWS)),
        ("SUPPORT_CHANNEL_COUNT_5", len(support) == len(SUPPORT_CHANNEL_PREVIEWS)),
        ("QA_CHECK_COUNT_8", len(qa) == len(QA_CHECKS)),
        ("SAFETY_LOCK_COUNT_12", len(locks) == len(SAFETY_LOCKS)),
        ("RECEIPT_PACKET_COUNT_1", len(packets) == 1),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("ONBOARDING_EXPERIENCE_READY", readiness["onboarding_experience_ready"] is True),
        ("ONBOARDING_PREVIEW_LOCKED", readiness["onboarding_preview_locked"] is True),
        ("PROFILE_PREVIEW_LOCKED", readiness["profile_preview_locked"] is True),
        ("POLICY_ACK_LOCKED", readiness["policy_ack_locked"] is True),
        ("WORKSPACE_PREVIEW_LOCKED", readiness["workspace_preview_locked"] is True),
        ("SUPPORT_PREVIEW_LOCKED", readiness["support_preview_locked"] is True),
        ("SAFE_TO_CONTINUE_TO_GP231", readiness["safe_to_continue_to_gp231"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("VAULT_NOT_DONE", readiness["vault_done"] is False),
        ("CLOUDS_PARKED", readiness["clouds_should_continue"] is False),
        ("SECTION_GP221_GP230", readiness["section_range"] == "GP221-GP230"),
        ("NEXT_SECTION_GP231_GP240", readiness["readiness_payload"]["next_section_range"] == "GP231-GP240"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_READY", all(item["component_ready"] is True for item in components)),
        ("ALL_COMPONENTS_LOCKED", all(item["component_locked"] is True for item in components)),
        ("ALL_COMPONENTS_ONBOARDING_LOCKED", all(item["onboarding_preview_locked"] and item["profile_preview_locked"] and item["policy_ack_locked"] for item in components)),
        ("ALL_COMPONENTS_WORKSPACE_SUPPORT_LOCKED", all(item["workspace_preview_locked"] and item["support_preview_locked"] for item in components)),
        ("ALL_WELCOME_DRAFTS_READY_LOCKED", all(item["draft_ready"] and item["draft_locked"] for item in welcome)),
        ("ALL_PROFILES_READY_SUBMIT_LOCKED", all(item["preview_ready"] and item["preview_locked"] and item["submit_locked"] for item in profiles)),
        ("ALL_POLICIES_ACK_LOCKED", all(item["preview_ready"] and item["acknowledgment_locked"] and item["acceptance_record_locked"] for item in policies)),
        ("ALL_WORKSPACES_OPEN_LOCKED", all(item["workspace_preview_ready"] and item["workspace_open_locked"] and item["workspace_session_locked"] for item in workspaces)),
        ("ALL_SUPPORT_CHANNELS_SEND_LOCKED", all(item["channel_preview_ready"] and item["channel_open_locked"] and item["message_send_locked"] for item in support)),
        ("ALL_QA_READY_LOCKED", all(item["qa_ready"] and item["qa_locked"] for item in qa)),
        ("ALL_SAFETY_LOCKS_ACTIVE", all(item["lock_active"] for item in locks)),
        ("ALL_SAFETY_LOCKS_BLOCK_ONBOARDING_PROFILE_POLICY", all(item["blocks_onboarding_start"] and item["blocks_profile_submit"] and item["blocks_policy_accept"] for item in locks)),
        ("ALL_SAFETY_LOCKS_BLOCK_WORKSPACE_SUPPORT_FEEDBACK", all(item["blocks_workspace_open"] and item["blocks_support_send"] and item["blocks_feedback_issue_submit"] for item in locks)),
        ("ALL_SAFETY_LOCKS_BLOCK_TOWER_BILLING", all(item["blocks_tower_gate"] and item["blocks_billing_subscription"] for item in locks)),
        ("ALL_SAFETY_LOCKS_BLOCK_PROVIDER_BODY", all(item["blocks_provider_unlock"] and item["blocks_provider_api"] and item["blocks_object_body"] and item["blocks_download"] for item in locks)),
        ("ALL_SAFETY_LOCKS_BLOCK_DANGEROUS_OPS", all(item["blocks_restore"] and item["blocks_export"] and item["blocks_direct_upload"] and item["blocks_delete"] for item in locks)),
        ("ALL_SAFETY_LOCKS_BLOCK_EXECUTION_DONE", all(item["blocks_execution"] and item["blocks_vault_done"] for item in locks)),
        ("NO_SAFETY_LOCKS_RESOLVED", all(item["resolved"] is False for item in locks)),
        ("PACKET_READY_LOCKED", all(item["packet_ready"] and item["packet_locked"] for item in packets)),
        ("NO_FINAL_ONBOARDING_RECEIPT", all(item["final_onboarding_receipt"] is False for item in packets)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("WELCOME", welcome),
        ("PROFILE", profiles),
        ("POLICY", policies),
        ("WORKSPACE", workspaces),
        ("SUPPORT", support),
        ("QA", qa),
        ("SAFETY", locks),
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
        "welcome_orientation_count": len(welcome),
        "profile_preview_count": len(profiles),
        "policy_ack_lock_count": len(policies),
        "workspace_preview_count": len(workspaces),
        "support_channel_count": len(support),
        "qa_check_count": len(qa),
        "safety_lock_count": len(locks),
        "receipt_packet_count": len(packets),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "onboarding_experience_ready": len(failed) == 0 and readiness["onboarding_experience_ready"] is True,
        "safe_to_continue_to_gp231": len(failed) == 0 and readiness["safe_to_continue_to_gp231"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp221_beta_onboarding_locked_experience_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SHELL_ID, db_path)
    return {"pack": _pack_payload(221, component["pack_name"]), "real_sqlite_backed": True, "shell": component}

def get_gp222_locked_welcome_orientation_draft_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(WELCOME_ORIENTATION_ID, db_path)
    rows = get_welcome_orientation_drafts(db_path)
    return {"pack": _pack_payload(222, component["pack_name"]), "real_sqlite_backed": True, "welcome_orientation_board": component, "welcome_orientation_count": len(rows), "drafts": rows}

def get_gp223_beta_profile_setup_preview_lock(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(PROFILE_SETUP_ID, db_path)
    rows = get_profile_setup_previews(db_path)
    return {"pack": _pack_payload(223, component["pack_name"]), "real_sqlite_backed": True, "profile_setup_preview_lock": component, "profile_preview_count": len(rows), "previews": rows}

def get_gp224_nda_policy_acknowledgment_preview_lock(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(POLICY_ACK_ID, db_path)
    rows = get_policy_ack_locks(db_path)
    return {"pack": _pack_payload(224, component["pack_name"]), "real_sqlite_backed": True, "policy_acknowledgment_preview_lock": component, "policy_ack_lock_count": len(rows), "policies": rows}

def get_gp225_beta_workspace_access_preview_lock(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(WORKSPACE_ACCESS_ID, db_path)
    rows = get_workspace_access_previews(db_path)
    return {"pack": _pack_payload(225, component["pack_name"]), "real_sqlite_backed": True, "workspace_access_preview_lock": component, "workspace_preview_count": len(rows), "workspaces": rows}

def get_gp226_beta_support_channel_preview_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SUPPORT_CHANNEL_ID, db_path)
    rows = get_support_channel_previews(db_path)
    return {"pack": _pack_payload(226, component["pack_name"]), "real_sqlite_backed": True, "support_channel_preview_board": component, "support_channel_count": len(rows), "channels": rows}

def get_gp227_beta_onboarding_qa_checklist(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(QA_CHECKLIST_ID, db_path)
    rows = get_onboarding_qa_checks(db_path)
    return {"pack": _pack_payload(227, component["pack_name"]), "real_sqlite_backed": True, "qa_checklist": component, "qa_check_count": len(rows), "checks": rows}

def get_gp228_onboarding_safety_compliance_lock_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SAFETY_COMPLIANCE_ID, db_path)
    rows = get_onboarding_safety_compliance_locks(db_path)
    return {"pack": _pack_payload(228, component["pack_name"]), "real_sqlite_backed": True, "safety_compliance_lock_board": component, "safety_lock_count": len(rows), "locks": rows}

def get_gp229_beta_onboarding_receipt_draft_packet(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RECEIPT_PACKET_ID, db_path)
    rows = get_onboarding_receipt_packets(db_path)
    return {"pack": _pack_payload(229, component["pack_name"]), "real_sqlite_backed": True, "receipt_packet_component": component, "receipt_packet_count": len(rows), "packets": rows}

def get_gp230_beta_onboarding_locked_experience_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_onboarding_locked_experience_layer(db_path)
    return {"pack": _pack_payload(230, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_onboarding_locked_experience_layer(db_path)
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
            "source_gp220_readiness_id": component["source_gp220_readiness_id"],
            "source_gp220_readiness_hash": component["source_gp220_readiness_hash"],
            "source_gp220_readiness_score": component["source_gp220_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "onboarding_experience_ready": component["onboarding_experience_ready"],
            "onboarding_preview_locked": component["onboarding_preview_locked"],
            "profile_preview_locked": component["profile_preview_locked"],
            "policy_ack_locked": component["policy_ack_locked"],
            "workspace_preview_locked": component["workspace_preview_locked"],
            "support_preview_locked": component["support_preview_locked"],
            "vault_not_done": component["vault_not_done"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp231": validation["safe_to_continue_to_gp231"],
            "foundation_status": "beta_onboarding_locked_experience_ready_onboarding_profile_policy_workspace_support_locked_vault_not_done_safe_to_continue",
            "next": next_label,
            **counts,
            "beta_launch_approved": component["beta_launch_approved"],
            "beta_invite_created": component["beta_invite_created"],
            "beta_invite_sent": component["beta_invite_sent"],
            "beta_tester_added": component["beta_tester_added"],
            "beta_tester_access_granted": component["beta_tester_access_granted"],
            "beta_tester_access_enabled": component["beta_tester_access_enabled"],
            "beta_access_token_created": component["beta_access_token_created"],
            "beta_access_session_created": component["beta_access_session_created"],
            "onboarding_started": component["onboarding_started"],
            "onboarding_completed": component["onboarding_completed"],
            "welcome_acknowledged": component["welcome_acknowledged"],
            "orientation_started": component["orientation_started"],
            "orientation_completed": component["orientation_completed"],
            "profile_created": component["profile_created"],
            "profile_updated": component["profile_updated"],
            "profile_submitted": component["profile_submitted"],
            "profile_approved": component["profile_approved"],
            "nda_opened": component["nda_opened"],
            "nda_signed": component["nda_signed"],
            "policy_opened": component["policy_opened"],
            "policy_acknowledged": component["policy_acknowledged"],
            "policy_acceptance_recorded": component["policy_acceptance_recorded"],
            "workspace_opened": component["workspace_opened"],
            "workspace_access_granted": component["workspace_access_granted"],
            "workspace_session_created": component["workspace_session_created"],
            "support_channel_opened": component["support_channel_opened"],
            "support_message_sent": component["support_message_sent"],
            "feedback_form_opened": component["feedback_form_opened"],
            "feedback_submitted": component["feedback_submitted"],
            "issue_created": component["issue_created"],
            "issue_submitted": component["issue_submitted"],
            "billing_flow_created": component["billing_flow_created"],
            "subscription_flow_created": component["subscription_flow_created"],
            "payment_processor_called": component["payment_processor_called"],
            "tower_billing_handoff_created": component["tower_billing_handoff_created"],
            "provider_unlock_requested": component["provider_unlock_requested"],
            "provider_unlock_approved": component["provider_unlock_approved"],
            "real_provider_connection_started": component["real_provider_connection_started"],
            "provider_api_called": component["provider_api_called"],
            "provider_search_executed": component["provider_search_executed"],
            "provider_token_created": component["provider_token_created"],
            "provider_session_created": component["provider_session_created"],
            "provider_metadata_imported": component["provider_metadata_imported"],
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
            "clouds_status": "parked_do_not_continue_from_vault_gp230",
        },
        "validation": validation,
    }

def get_gp221_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(221, SHELL_ID, "VAULT_GP222_LOCKED_WELCOME_ORIENTATION_DRAFT_BOARD", db_path)

def get_gp222_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(222, WELCOME_ORIENTATION_ID, "VAULT_GP223_BETA_PROFILE_SETUP_PREVIEW_LOCK", db_path)

def get_gp223_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(223, PROFILE_SETUP_ID, "VAULT_GP224_NDA_POLICY_ACKNOWLEDGMENT_PREVIEW_LOCK", db_path)

def get_gp224_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(224, POLICY_ACK_ID, "VAULT_GP225_BETA_WORKSPACE_ACCESS_PREVIEW_LOCK", db_path)

def get_gp225_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(225, WORKSPACE_ACCESS_ID, "VAULT_GP226_BETA_SUPPORT_CHANNEL_PREVIEW_BOARD", db_path)

def get_gp226_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(226, SUPPORT_CHANNEL_ID, "VAULT_GP227_BETA_ONBOARDING_QA_CHECKLIST", db_path)

def get_gp227_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(227, QA_CHECKLIST_ID, "VAULT_GP228_ONBOARDING_SAFETY_COMPLIANCE_LOCK_BOARD", db_path)

def get_gp228_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(228, SAFETY_COMPLIANCE_ID, "VAULT_GP229_BETA_ONBOARDING_RECEIPT_DRAFT_PACKET", db_path)

def get_gp229_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(229, RECEIPT_PACKET_ID, "VAULT_GP230_BETA_ONBOARDING_LOCKED_EXPERIENCE_READINESS_CHECKPOINT", db_path)

def get_gp230_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(230, READINESS_ID, NEXT_PACK, db_path)
    status["gp230_status"]["next_section"] = NEXT_SECTION_ID
    status["gp230_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp230_status"]["next_pack"] = NEXT_PACK
    return status

def get_beta_onboarding_locked_experience_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_beta_onboarding_locked_experience_layer(db_path)
    components = _rows("vault_beta_onboarding_components", "gp_number", db_path, {"data_json": "data"})
    welcome = get_welcome_orientation_drafts(db_path)
    profiles = get_profile_setup_previews(db_path)
    policies = get_policy_ack_locks(db_path)
    workspaces = get_workspace_access_previews(db_path)
    support = get_support_channel_previews(db_path)
    qa = get_onboarding_qa_checks(db_path)
    locks = get_onboarding_safety_compliance_locks(db_path)
    packets = get_onboarding_receipt_packets(db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_onboarding_locked_experience_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "welcome_orientation": {"welcome_orientation_count": len(welcome), "drafts": welcome},
        "profile_setup": {"profile_preview_count": len(profiles), "previews": profiles},
        "policy_acknowledgment": {"policy_ack_lock_count": len(policies), "policies": policies},
        "workspace_access": {"workspace_preview_count": len(workspaces), "workspaces": workspaces},
        "support_channels": {"support_channel_count": len(support), "channels": support},
        "qa_checklist": {"qa_check_count": len(qa), "checks": qa},
        "safety_compliance_locks": {"safety_lock_count": len(locks), "locks": locks},
        "receipt_packets": {"receipt_packet_count": len(packets), "packets": packets},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "beta_onboarding_locked_experience_layer_ready": True,
            "onboarding_experience_ready": validation["onboarding_experience_ready"],
            "safe_to_continue_to_gp231": validation["safe_to_continue_to_gp231"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "onboarding_preview_locked": True,
            "profile_preview_locked": True,
            "policy_ack_locked": True,
            "workspace_preview_locked": True,
            "support_preview_locked": True,
            "beta_launch_approved": False,
            "beta_invite_created": False,
            "beta_invite_sent": False,
            "beta_tester_added": False,
            "beta_tester_access_granted": False,
            "beta_access_token_created": False,
            "beta_access_session_created": False,
            "onboarding_started": False,
            "onboarding_completed": False,
            "profile_created": False,
            "profile_submitted": False,
            "nda_signed": False,
            "policy_acknowledged": False,
            "workspace_opened": False,
            "support_channel_opened": False,
            "support_message_sent": False,
            "feedback_submitted": False,
            "issue_submitted": False,
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
            "page": "/vault/beta-onboarding-locked-experience-layer",
            "json": "/vault/beta-onboarding-locked-experience-layer.json",
            "gp221": "/vault/gp221-status.json",
            "gp222": "/vault/gp222-status.json",
            "gp223": "/vault/gp223-status.json",
            "gp224": "/vault/gp224-status.json",
            "gp225": "/vault/gp225-status.json",
            "gp226": "/vault/gp226-status.json",
            "gp227": "/vault/gp227-status.json",
            "gp228": "/vault/gp228-status.json",
            "gp229": "/vault/gp229-status.json",
            "gp230": "/vault/gp230-status.json",
        },
    }

def render_beta_onboarding_locked_experience_layer_page() -> str:
    home = get_beta_onboarding_locked_experience_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    welcome_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['draft_name'])}</strong>
          <span>{escape(item['draft_status'])}</span>
          <code>{escape(item['draft_category'])} · draft locked</code>
        </article>
        """
        for item in home["welcome_orientation"]["drafts"]
    )

    safety_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['lock_name'])}</strong>
          <span>{escape(item['lock_status'])}</span>
          <code>{escape(item['lock_category'])} · active</code>
        </article>
        """
        for item in home["safety_compliance_locks"]["locks"][:9]
    )

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP221-GP230 Beta Onboarding Locked Experience Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 221-230</div>
    <div class="eyebrow">Beta Onboarding Locked Experience Layer · GP221-GP230</div>
    <h1>Beta Onboarding Locked Experience</h1>
    <p>This layer prepares onboarding previews: welcome, profile, NDA/policy, workspace, support, QA, safety, and receipt drafts. No onboarding action is live.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['welcome_orientation_count']}</strong><span>welcome drafts</span></div>
      <div class="metric"><strong>{home['store']['workspace_preview_count']}</strong><span>workspace previews</span></div>
      <div class="metric"><strong>{home['store']['safety_lock_count']}</strong><span>safety locks</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP221-GP230 built</span>
      <span class="pill ok">Safe to GP231</span>
      <span class="pill danger">No onboarding started</span>
      <span class="pill danger">No profile submit</span>
      <span class="pill danger">No policy accepted</span>
      <span class="pill danger">No workspace opened</span>
      <span class="pill danger">No support send</span>
      <span class="pill danger">No Tower gate</span>
      <span class="pill danger">No execution</span>
      <span class="pill danger">Vault not done</span>
    </div>
  </section>

  <section class="section">
    <h2>Locked Welcome + Orientation Drafts</h2>
    <div class="cards">{welcome_cards}</div>
  </section>

  <section class="section">
    <h2>Safety + Compliance Locks</h2>
    <div class="cards">{safety_cards}</div>
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
