"""
VAULT GP211-GP220 — Beta Access and Invite Lock Layer

New section:
Archive Vault — Beta Access and Invite Lock Layer / GP211-GP220

Builds:
- GP211 Beta Access and Invite Lock Shell
- GP212 Beta Invite Draft Registry
- GP213 Tester Candidate Intake Lock Board
- GP214 Invite Send Lock Contract
- GP215 Access Grant Lock Contract
- GP216 Beta Role Permission Preview Matrix
- GP217 Tower Beta Gate Handoff Preview
- GP218 Billing Subscription Lock Handoff Preview
- GP219 Beta Access Risk and Blocker Board
- GP220 Beta Access and Invite Lock Readiness Checkpoint

This layer creates locked beta access/invite governance records. It does not
send invites, add testers, grant access, create access tokens/sessions, open Tower
gates, create billing/subscription flows, call providers, read object bodies,
restore/export/upload/delete, execute, or mark Vault done.
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

from vault.owner_productization_beta_readiness_layer_service import (
    get_gp210_status,
    get_gp210_owner_productization_beta_readiness_checkpoint,
    get_owner_productization_beta_readiness_layer_home,
    validate_owner_productization_beta_readiness_layer,
    get_beta_access_locks,
    get_launch_risk_blockers,
)

LAYER_ID = "VAULT_GP211_220"
LAYER_NAME = "Beta Access and Invite Lock Layer"
SCHEMA_VERSION = "vault.beta_access_invite_lock_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_BETA_ACCESS_AND_INVITE_LOCK_LAYER"
SECTION_TITLE = "Archive Vault — Beta Access and Invite Lock Layer"
SECTION_RANGE = "GP211-GP220"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_OWNER_PRODUCTIZATION_BETA_READINESS_LAYER"
PREVIOUS_SECTION_RANGE = "GP201-GP210"

NEXT_SECTION_ID = "ARCHIVE_VAULT_BETA_ONBOARDING_LOCKED_EXPERIENCE_LAYER"
NEXT_SECTION_RANGE = "GP221-GP230"
NEXT_PACK = "VAULT_GP221_230_BETA_ONBOARDING_LOCKED_EXPERIENCE_LAYER"

DEFAULT_DB_ENV = "VAULT_BETA_ACCESS_INVITE_LOCK_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_beta_access_invite_lock_layer.sqlite"

SHELL_ID = "VBAIL-SHELL-GP211-001"
INVITE_DRAFT_REGISTRY_ID = "VBAIL-INVITE-GP212-001"
TESTER_INTAKE_LOCK_ID = "VBAIL-TESTER-GP213-001"
INVITE_SEND_LOCK_ID = "VBAIL-SENDLOCK-GP214-001"
ACCESS_GRANT_LOCK_ID = "VBAIL-GRANTLOCK-GP215-001"
ROLE_PERMISSION_MATRIX_ID = "VBAIL-ROLEMATRIX-GP216-001"
TOWER_GATE_HANDOFF_ID = "VBAIL-TOWER-GP217-001"
BILLING_HANDOFF_ID = "VBAIL-BILLING-GP218-001"
RISK_BLOCKER_ID = "VBAIL-RISK-GP219-001"
READINESS_ID = "VBAIL-READINESS-GP220-001"

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

INVITE_DRAFTS = [
    ("owner_internal_beta_invite", "Owner Internal Beta Invite", "owner", "draft_locked"),
    ("trusted_admin_beta_invite", "Trusted Admin Beta Invite", "admin", "draft_locked"),
    ("tower_reviewer_beta_invite", "Tower Reviewer Beta Invite", "tower", "draft_locked"),
    ("vault_reviewer_beta_invite", "Vault Reviewer Beta Invite", "vault", "draft_locked"),
    ("receipt_reviewer_beta_invite", "Receipt Reviewer Beta Invite", "receipt", "draft_locked"),
    ("support_observer_beta_invite", "Support Observer Beta Invite", "support", "draft_locked"),
]

TESTER_CANDIDATES = [
    ("owner_candidate_slot", "Owner Candidate Slot", "owner", "locked_not_submitted"),
    ("admin_candidate_slot", "Admin Candidate Slot", "admin", "locked_not_submitted"),
    ("tower_candidate_slot", "Tower Candidate Slot", "tower", "locked_not_submitted"),
    ("vault_candidate_slot", "Vault Candidate Slot", "vault", "locked_not_submitted"),
    ("support_candidate_slot", "Support Candidate Slot", "support", "locked_not_submitted"),
    ("qa_candidate_slot", "QA Candidate Slot", "qa", "locked_not_submitted"),
]

INVITE_SEND_LOCKS = [
    ("invite_creation_lock", "Invite Creation Lock"),
    ("invite_owner_approval_lock", "Invite Owner Approval Lock"),
    ("invite_send_lock", "Invite Send Lock"),
    ("invite_delivery_lock", "Invite Delivery Lock"),
    ("invite_resend_lock", "Invite Resend Lock"),
    ("invite_revocation_preview_lock", "Invite Revocation Preview Lock"),
]

ACCESS_GRANT_LOCKS = [
    ("tester_add_lock", "Tester Add Lock"),
    ("access_request_lock", "Access Request Lock"),
    ("access_approval_lock", "Access Approval Lock"),
    ("access_grant_lock", "Access Grant Lock"),
    ("role_assignment_lock", "Role Assignment Lock"),
    ("permission_enable_lock", "Permission Enable Lock"),
    ("token_creation_lock", "Token Creation Lock"),
    ("session_creation_lock", "Session Creation Lock"),
]

ROLE_PERMISSION_PREVIEWS = [
    ("vault_beta_owner", "Vault Beta Owner", ["view_owner_readiness", "view_receipts", "view_redacted_archive"], "preview_only"),
    ("vault_beta_admin", "Vault Beta Admin", ["view_readiness", "view_blockers", "view_support_plan"], "preview_only"),
    ("vault_beta_reviewer", "Vault Beta Reviewer", ["view_redacted_archive", "view_receipt_packet"], "preview_only"),
    ("vault_beta_support", "Vault Beta Support", ["view_support_intake", "view_qa_scenarios"], "preview_only"),
    ("vault_beta_observer", "Vault Beta Observer", ["view_summary_only"], "preview_only"),
]

TOWER_HANDOFF_PREVIEWS = [
    ("tower_identity_gate_preview", "Tower Identity Gate Preview", "identity", "preview_locked"),
    ("tower_clearance_gate_preview", "Tower Clearance Gate Preview", "clearance", "preview_locked"),
    ("tower_role_gate_preview", "Tower Role Gate Preview", "role", "preview_locked"),
    ("tower_step_up_gate_preview", "Tower Step-Up Gate Preview", "step_up", "preview_locked"),
    ("tower_audit_receipt_preview", "Tower Audit Receipt Preview", "audit", "preview_locked"),
]

BILLING_HANDOFF_PREVIEWS = [
    ("tower_billing_boundary_preview", "Tower Billing Boundary Preview", "billing", "preview_locked"),
    ("subscription_plan_boundary_preview", "Subscription Plan Boundary Preview", "subscription", "preview_locked"),
    ("customer_portal_boundary_preview", "Customer Portal Boundary Preview", "portal", "preview_locked"),
    ("payment_processor_boundary_preview", "Payment Processor Boundary Preview", "processor", "preview_locked"),
    ("invoice_receipt_boundary_preview", "Invoice Receipt Boundary Preview", "receipt", "preview_locked"),
]

RISK_BLOCKERS = [
    ("beta_launch_locked", "Beta launch locked", "launch", "critical"),
    ("invite_creation_locked", "Invite creation locked", "invite", "critical"),
    ("invite_send_locked", "Invite send locked", "invite", "critical"),
    ("tester_add_locked", "Tester add locked", "tester", "critical"),
    ("access_grant_locked", "Access grant locked", "access", "critical"),
    ("token_session_locked", "Access token/session locked", "access", "critical"),
    ("tower_gate_locked", "Tower gate locked", "tower", "critical"),
    ("billing_subscription_locked", "Billing/subscription locked", "billing", "critical"),
    ("provider_unlock_locked", "Provider unlock locked", "provider", "critical"),
    ("object_body_download_locked", "Object body/download locked", "object_body", "critical"),
    ("restore_export_upload_delete_locked", "Restore/export/upload/delete locked", "dangerous_ops", "critical"),
    ("vault_not_done", "Vault not done", "done_state", "critical"),
    ("execution_locked", "Execution locked", "execution", "critical"),
    ("clouds_parked", "Clouds parked", "clouds", "medium"),
]

COMPONENT_SPECS = [
    (211, SHELL_ID, "VAULT_GP211", "Beta Access and Invite Lock Shell", "beta_access_invite_lock_shell"),
    (212, INVITE_DRAFT_REGISTRY_ID, "VAULT_GP212", "Beta Invite Draft Registry", "beta_invite_draft_registry"),
    (213, TESTER_INTAKE_LOCK_ID, "VAULT_GP213", "Tester Candidate Intake Lock Board", "tester_candidate_intake_lock_board"),
    (214, INVITE_SEND_LOCK_ID, "VAULT_GP214", "Invite Send Lock Contract", "invite_send_lock_contract"),
    (215, ACCESS_GRANT_LOCK_ID, "VAULT_GP215", "Access Grant Lock Contract", "access_grant_lock_contract"),
    (216, ROLE_PERMISSION_MATRIX_ID, "VAULT_GP216", "Beta Role Permission Preview Matrix", "beta_role_permission_preview_matrix"),
    (217, TOWER_GATE_HANDOFF_ID, "VAULT_GP217", "Tower Beta Gate Handoff Preview", "tower_beta_gate_handoff_preview"),
    (218, BILLING_HANDOFF_ID, "VAULT_GP218", "Billing Subscription Lock Handoff Preview", "billing_subscription_lock_handoff_preview"),
    (219, RISK_BLOCKER_ID, "VAULT_GP219", "Beta Access Risk and Blocker Board", "beta_access_risk_blocker_board"),
    (220, READINESS_ID, "VAULT_GP220", "Beta Access and Invite Lock Readiness Checkpoint", "beta_access_invite_lock_readiness_checkpoint"),
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
        "source_gp210_readiness_score",
        "component_count",
        "invite_draft_count",
        "tester_candidate_count",
        "invite_send_lock_count",
        "access_grant_lock_count",
        "role_permission_preview_count",
        "tower_handoff_preview_count",
        "billing_handoff_preview_count",
        "risk_blocker_count",
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
        "depends_on": ["VAULT_GP210"],
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
        "depends_on": ["VAULT_GP210"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_beta_access_invite_lock_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_beta_access_invite_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp210_readiness_id TEXT NOT NULL,
                source_gp210_readiness_hash TEXT NOT NULL,
                source_gp210_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                beta_access_layer_ready INTEGER NOT NULL DEFAULT 1,
                invite_lock_active INTEGER NOT NULL DEFAULT 1,
                access_grant_lock_active INTEGER NOT NULL DEFAULT 1,
                tower_gate_preview_only INTEGER NOT NULL DEFAULT 1,
                billing_preview_only INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_beta_invite_draft_registry (
                invite_id TEXT PRIMARY KEY,
                invite_code TEXT NOT NULL UNIQUE,
                invite_name TEXT NOT NULL,
                invite_audience TEXT NOT NULL,
                invite_status TEXT NOT NULL,
                draft_ready INTEGER NOT NULL DEFAULT 1,
                draft_locked INTEGER NOT NULL DEFAULT 1,
                send_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                invite_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_tester_candidate_intake_locks (
                candidate_id TEXT PRIMARY KEY,
                candidate_code TEXT NOT NULL UNIQUE,
                candidate_name TEXT NOT NULL,
                candidate_lane TEXT NOT NULL,
                candidate_status TEXT NOT NULL,
                intake_locked INTEGER NOT NULL DEFAULT 1,
                approval_locked INTEGER NOT NULL DEFAULT 1,
                add_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                candidate_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_invite_send_lock_contracts (
                lock_id TEXT PRIMARY KEY,
                lock_code TEXT NOT NULL UNIQUE,
                lock_name TEXT NOT NULL,
                lock_status TEXT NOT NULL,
                invite_send_locked INTEGER NOT NULL DEFAULT 1,
                invite_delivery_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_access_grant_lock_contracts (
                lock_id TEXT PRIMARY KEY,
                lock_code TEXT NOT NULL UNIQUE,
                lock_name TEXT NOT NULL,
                lock_status TEXT NOT NULL,
                access_grant_locked INTEGER NOT NULL DEFAULT 1,
                token_session_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_beta_role_permission_preview_matrix (
                matrix_id TEXT PRIMARY KEY,
                role_code TEXT NOT NULL UNIQUE,
                role_name TEXT NOT NULL,
                permission_preview_json TEXT NOT NULL,
                matrix_status TEXT NOT NULL,
                preview_only INTEGER NOT NULL DEFAULT 1,
                role_assignment_locked INTEGER NOT NULL DEFAULT 1,
                permission_grant_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                matrix_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_tower_beta_gate_handoff_previews (
                handoff_id TEXT PRIMARY KEY,
                handoff_code TEXT NOT NULL UNIQUE,
                handoff_name TEXT NOT NULL,
                handoff_category TEXT NOT NULL,
                handoff_status TEXT NOT NULL,
                preview_only INTEGER NOT NULL DEFAULT 1,
                tower_gate_locked INTEGER NOT NULL DEFAULT 1,
                tower_unlock_locked INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_billing_subscription_lock_handoff_previews (
                billing_id TEXT PRIMARY KEY,
                billing_code TEXT NOT NULL UNIQUE,
                billing_name TEXT NOT NULL,
                billing_category TEXT NOT NULL,
                billing_status TEXT NOT NULL,
                preview_only INTEGER NOT NULL DEFAULT 1,
                billing_locked INTEGER NOT NULL DEFAULT 1,
                subscription_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                billing_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_beta_access_risk_blockers (
                blocker_id TEXT PRIMARY KEY,
                blocker_code TEXT NOT NULL UNIQUE,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocker_active INTEGER NOT NULL DEFAULT 1,
                blocks_beta_launch INTEGER NOT NULL DEFAULT 1,
                blocks_invite_send INTEGER NOT NULL DEFAULT 1,
                blocks_tester_add INTEGER NOT NULL DEFAULT 1,
                blocks_access_grant INTEGER NOT NULL DEFAULT 1,
                blocks_token_session INTEGER NOT NULL DEFAULT 1,
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
                blocker_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_beta_access_invite_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                invite_draft_count INTEGER NOT NULL,
                tester_candidate_count INTEGER NOT NULL,
                invite_send_lock_count INTEGER NOT NULL,
                access_grant_lock_count INTEGER NOT NULL,
                role_permission_preview_count INTEGER NOT NULL,
                tower_handoff_preview_count INTEGER NOT NULL,
                billing_handoff_preview_count INTEGER NOT NULL,
                risk_blocker_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                beta_access_layer_ready INTEGER NOT NULL DEFAULT 1,
                invite_lock_active INTEGER NOT NULL DEFAULT 1,
                access_grant_lock_active INTEGER NOT NULL DEFAULT 1,
                safe_to_continue_to_gp221 INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_beta_access_invite_events (
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
            "vault_beta_access_invite_components",
            "vault_beta_invite_draft_registry",
            "vault_tester_candidate_intake_locks",
            "vault_invite_send_lock_contracts",
            "vault_access_grant_lock_contracts",
            "vault_beta_role_permission_preview_matrix",
            "vault_tower_beta_gate_handoff_previews",
            "vault_billing_subscription_lock_handoff_previews",
            "vault_beta_access_risk_blockers",
            "vault_beta_access_invite_readiness",
            "vault_beta_access_invite_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VBAILEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_beta_access_invite_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_beta_access_invite_lock_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_beta_access_invite_lock_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_beta_access_invite_components WHERE component_id = ?",
            (SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp210_status = get_gp210_status()["gp210_status"]
            gp210_checkpoint = get_gp210_owner_productization_beta_readiness_checkpoint()["readiness_checkpoint"]
            gp210_home = get_owner_productization_beta_readiness_layer_home()
            gp210_validation = validate_owner_productization_beta_readiness_layer()
            source_access_locks = get_beta_access_locks()
            source_launch_blockers = get_launch_risk_blockers()

            readiness = gp210_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp210_readiness_id": readiness["readiness_id"],
                "source_gp210_readiness_hash": readiness["readiness_hash"],
                "source_gp210_readiness_score": readiness["readiness_score"],
            }

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "invite_draft_count": len(INVITE_DRAFTS),
                "tester_candidate_count": len(TESTER_CANDIDATES),
                "invite_send_lock_count": len(INVITE_SEND_LOCKS),
                "access_grant_lock_count": len(ACCESS_GRANT_LOCKS),
                "role_permission_preview_count": len(ROLE_PERMISSION_PREVIEWS),
                "tower_handoff_preview_count": len(TOWER_HANDOFF_PREVIEWS),
                "billing_handoff_preview_count": len(BILLING_HANDOFF_PREVIEWS),
                "risk_blocker_count": len(RISK_BLOCKERS),
            }

            source_context = {
                "source_gp210_status_ready": gp210_status["ready"],
                "source_gp210_validation_passed": gp210_status["validation_passed"],
                "source_gp210_safe_to_continue_to_gp211": gp210_status["safe_to_continue_to_gp211"],
                "source_gp210_readiness_hash": readiness["readiness_hash"],
                "source_gp210_readiness_score": readiness["readiness_score"],
                "source_beta_access_lock_count": len(source_access_locks),
                "source_launch_blocker_count": len(source_launch_blockers),
                "source_validation_check_count": gp210_validation["check_count"],
            }

            component_extra = {
                SHELL_ID: {"beta_access_invite_lock_shell_ready": True},
                INVITE_DRAFT_REGISTRY_ID: {"beta_invite_draft_registry_ready": True, "invite_draft_count": counts["invite_draft_count"]},
                TESTER_INTAKE_LOCK_ID: {"tester_candidate_intake_lock_board_ready": True, "tester_candidate_count": counts["tester_candidate_count"]},
                INVITE_SEND_LOCK_ID: {"invite_send_lock_contract_ready": True, "invite_send_lock_count": counts["invite_send_lock_count"]},
                ACCESS_GRANT_LOCK_ID: {"access_grant_lock_contract_ready": True, "access_grant_lock_count": counts["access_grant_lock_count"]},
                ROLE_PERMISSION_MATRIX_ID: {"beta_role_permission_preview_matrix_ready": True, "role_permission_preview_count": counts["role_permission_preview_count"]},
                TOWER_GATE_HANDOFF_ID: {"tower_beta_gate_handoff_preview_ready": True, "tower_handoff_preview_count": counts["tower_handoff_preview_count"]},
                BILLING_HANDOFF_ID: {"billing_subscription_lock_handoff_preview_ready": True, "billing_handoff_preview_count": counts["billing_handoff_preview_count"]},
                RISK_BLOCKER_ID: {"beta_access_risk_blocker_board_ready": True, "risk_blocker_count": counts["risk_blocker_count"]},
                READINESS_ID: {"beta_access_invite_lock_readiness_checkpoint_ready": True, "safe_to_continue_to_gp221": True},
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
                    "beta_access_layer_ready": True,
                    "invite_lock_active": True,
                    "access_grant_lock_active": True,
                    "tower_gate_preview_only": True,
                    "billing_preview_only": True,
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
                    "beta_access_layer_ready": 1,
                    "invite_lock_active": 1,
                    "access_grant_lock_active": 1,
                    "tower_gate_preview_only": 1,
                    "billing_preview_only": 1,
                    "vault_not_done": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_access_invite_components", row)

            for idx, (code, name, audience, status) in enumerate(INVITE_DRAFTS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "invite_code": code,
                    "invite_name": name,
                    "invite_audience": audience,
                    "invite_status": status,
                    "draft_ready": True,
                    "draft_locked": True,
                    "send_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "invite_id": f"VBAILINV-{idx:03d}",
                    "invite_code": code,
                    "invite_name": name,
                    "invite_audience": audience,
                    "invite_status": status,
                    "draft_ready": 1,
                    "draft_locked": 1,
                    "send_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "invite_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_invite_draft_registry", row)

            for idx, (code, name, lane, status) in enumerate(TESTER_CANDIDATES, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "candidate_code": code,
                    "candidate_name": name,
                    "candidate_lane": lane,
                    "candidate_status": status,
                    "intake_locked": True,
                    "approval_locked": True,
                    "add_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "candidate_id": f"VBAILCAND-{idx:03d}",
                    "candidate_code": code,
                    "candidate_name": name,
                    "candidate_lane": lane,
                    "candidate_status": status,
                    "intake_locked": 1,
                    "approval_locked": 1,
                    "add_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "candidate_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_tester_candidate_intake_locks", row)

            for idx, (code, name) in enumerate(INVITE_SEND_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "lock_code": code,
                    "lock_name": name,
                    "lock_status": "INVITE_SEND_LOCK_ACTIVE",
                    "invite_send_locked": True,
                    "invite_delivery_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "lock_id": f"VBAILSEND-{idx:03d}",
                    "lock_code": code,
                    "lock_name": name,
                    "lock_status": payload["lock_status"],
                    "invite_send_locked": 1,
                    "invite_delivery_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "lock_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_invite_send_lock_contracts", row)

            for idx, (code, name) in enumerate(ACCESS_GRANT_LOCKS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "lock_code": code,
                    "lock_name": name,
                    "lock_status": "ACCESS_GRANT_LOCK_ACTIVE",
                    "access_grant_locked": True,
                    "token_session_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "lock_id": f"VBAILGRANT-{idx:03d}",
                    "lock_code": code,
                    "lock_name": name,
                    "lock_status": payload["lock_status"],
                    "access_grant_locked": 1,
                    "token_session_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "lock_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_access_grant_lock_contracts", row)

            for idx, (code, name, permissions, status) in enumerate(ROLE_PERMISSION_PREVIEWS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "role_code": code,
                    "role_name": name,
                    "permission_preview": permissions,
                    "matrix_status": status,
                    "preview_only": True,
                    "role_assignment_locked": True,
                    "permission_grant_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "matrix_id": f"VBAILROLE-{idx:03d}",
                    "role_code": code,
                    "role_name": name,
                    "permission_preview_json": _json_dumps(permissions),
                    "matrix_status": status,
                    "preview_only": 1,
                    "role_assignment_locked": 1,
                    "permission_grant_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "matrix_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_role_permission_preview_matrix", row)

            for idx, (code, name, category, status) in enumerate(TOWER_HANDOFF_PREVIEWS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "handoff_code": code,
                    "handoff_name": name,
                    "handoff_category": category,
                    "handoff_status": status,
                    "preview_only": True,
                    "tower_gate_locked": True,
                    "tower_unlock_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "handoff_id": f"VBAILTOWER-{idx:03d}",
                    "handoff_code": code,
                    "handoff_name": name,
                    "handoff_category": category,
                    "handoff_status": status,
                    "preview_only": 1,
                    "tower_gate_locked": 1,
                    "tower_unlock_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "handoff_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_tower_beta_gate_handoff_previews", row)

            for idx, (code, name, category, status) in enumerate(BILLING_HANDOFF_PREVIEWS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "billing_code": code,
                    "billing_name": name,
                    "billing_category": category,
                    "billing_status": status,
                    "preview_only": True,
                    "billing_locked": True,
                    "subscription_locked": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "billing_id": f"VBAILBILL-{idx:03d}",
                    "billing_code": code,
                    "billing_name": name,
                    "billing_category": category,
                    "billing_status": status,
                    "preview_only": 1,
                    "billing_locked": 1,
                    "subscription_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "billing_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_billing_subscription_lock_handoff_previews", row)

            for idx, (code, name, category, severity) in enumerate(RISK_BLOCKERS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "ACTIVE_BETA_ACCESS_INVITE_LOCK_BLOCKER",
                    "blocker_active": True,
                    "blocks_beta_launch": True,
                    "blocks_invite_send": True,
                    "blocks_tester_add": True,
                    "blocks_access_grant": True,
                    "blocks_token_session": True,
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
                    "blocker_id": f"VBAILRISK-{idx:03d}",
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": payload["blocker_status"],
                    "blocker_active": 1,
                    "blocks_beta_launch": 1,
                    "blocks_invite_send": 1,
                    "blocks_tester_add": 1,
                    "blocks_access_grant": 1,
                    "blocks_token_session": 1,
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
                    "blocker_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_beta_access_risk_blockers", row)

            checks = [
                ("SOURCE_GP210_READY", bool(gp210_status["ready"])),
                ("SOURCE_GP210_VALIDATION_PASSED", bool(gp210_status["validation_passed"])),
                ("SOURCE_GP210_SAFE_TO_CONTINUE", bool(gp210_status["safe_to_continue_to_gp211"])),
                ("SOURCE_GP210_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP210_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("INVITE_DRAFT_COUNT_6", counts["invite_draft_count"] == 6),
                ("TESTER_CANDIDATE_COUNT_6", counts["tester_candidate_count"] == 6),
                ("INVITE_SEND_LOCK_COUNT_6", counts["invite_send_lock_count"] == 6),
                ("ACCESS_GRANT_LOCK_COUNT_8", counts["access_grant_lock_count"] == 8),
                ("ROLE_PERMISSION_PREVIEW_COUNT_5", counts["role_permission_preview_count"] == 5),
                ("TOWER_HANDOFF_PREVIEW_COUNT_5", counts["tower_handoff_preview_count"] == 5),
                ("BILLING_HANDOFF_PREVIEW_COUNT_5", counts["billing_handoff_preview_count"] == 5),
                ("RISK_BLOCKER_COUNT_14", counts["risk_blocker_count"] == 14),
                ("SECTION_GP211_GP220", SECTION_RANGE == "GP211-GP220"),
                ("NEXT_SECTION_GP221_GP230", NEXT_SECTION_RANGE == "GP221-GP230"),
                ("BETA_ACCESS_LAYER_READY", True),
                ("INVITE_LOCK_ACTIVE", True),
                ("ACCESS_GRANT_LOCK_ACTIVE", True),
                ("NO_BETA_LAUNCH", True),
                ("NO_INVITE_CREATED_SENT", True),
                ("NO_TESTER_ADDED", True),
                ("NO_ACCESS_GRANTED", True),
                ("NO_TOKEN_SESSION", True),
                ("NO_TOWER_GATE_PASS", True),
                ("NO_BILLING_SUBSCRIPTION", True),
                ("NO_PROVIDER_UNLOCK", True),
                ("NO_PROVIDER_API", True),
                ("NO_PROVIDER_METADATA_READ", True),
                ("NO_OBJECT_BODY", True),
                ("NO_DOWNLOAD", True),
                ("NO_RESTORE_EXPORT_UPLOAD_DELETE", True),
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
                "gp_number": 220,
                "pack_id": "VAULT_GP220",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp210_readiness_id": readiness["readiness_id"],
                "source_gp210_readiness_hash": readiness["readiness_hash"],
                "source_gp210_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "beta_access_layer_ready": True,
                "invite_lock_active": True,
                "access_grant_lock_active": True,
                "safe_to_continue_to_gp221": failed_count == 0,
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
                "gp_number": 220,
                "pack_id": "VAULT_GP220",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "BETA_ACCESS_INVITE_LOCK_LAYER_READY_INVITES_ACCESS_TOWER_BILLING_LOCKED_VAULT_NOT_DONE_SAFE_TO_CONTINUE",
                "readiness_score": readiness_payload["readiness_score"],
                **counts,
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "beta_access_layer_ready": 1,
                "invite_lock_active": 1,
                "access_grant_lock_active": 1,
                "safe_to_continue_to_gp221": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_beta_access_invite_readiness", row)

            for event_type, event_payload in [
                ("GP211_BETA_ACCESS_INVITE_LOCK_SHELL_CREATED", {"component_id": SHELL_ID}),
                ("GP212_BETA_INVITE_DRAFT_REGISTRY_CREATED", {"invite_draft_count": counts["invite_draft_count"]}),
                ("GP213_TESTER_CANDIDATE_INTAKE_LOCK_BOARD_CREATED", {"tester_candidate_count": counts["tester_candidate_count"]}),
                ("GP214_INVITE_SEND_LOCK_CONTRACT_CREATED", {"invite_send_lock_count": counts["invite_send_lock_count"]}),
                ("GP215_ACCESS_GRANT_LOCK_CONTRACT_CREATED", {"access_grant_lock_count": counts["access_grant_lock_count"]}),
                ("GP216_BETA_ROLE_PERMISSION_PREVIEW_MATRIX_CREATED", {"role_permission_preview_count": counts["role_permission_preview_count"]}),
                ("GP217_TOWER_BETA_GATE_HANDOFF_PREVIEW_CREATED", {"tower_handoff_preview_count": counts["tower_handoff_preview_count"]}),
                ("GP218_BILLING_SUBSCRIPTION_LOCK_HANDOFF_PREVIEW_CREATED", {"billing_handoff_preview_count": counts["billing_handoff_preview_count"]}),
                ("GP219_BETA_ACCESS_RISK_BLOCKER_BOARD_CREATED", {"risk_blocker_count": counts["risk_blocker_count"]}),
                ("GP220_BETA_ACCESS_INVITE_LOCK_READINESS_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp221": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_access_invite_components").fetchone()["c"]),
            "invite_draft_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_invite_draft_registry").fetchone()["c"]),
            "tester_candidate_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_tester_candidate_intake_locks").fetchone()["c"]),
            "invite_send_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_invite_send_lock_contracts").fetchone()["c"]),
            "access_grant_lock_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_access_grant_lock_contracts").fetchone()["c"]),
            "role_permission_preview_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_role_permission_preview_matrix").fetchone()["c"]),
            "tower_handoff_preview_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_tower_beta_gate_handoff_previews").fetchone()["c"]),
            "billing_handoff_preview_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_billing_subscription_lock_handoff_previews").fetchone()["c"]),
            "risk_blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_access_risk_blockers").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_access_invite_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_beta_access_invite_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_beta_access_invite_lock_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_beta_access_invite_lock_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_beta_access_invite_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_beta_access_invite_lock_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_beta_access_invite_readiness WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_beta_access_invite_lock_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_beta_access_invite_events ORDER BY created_at, event_id").fetchall()
    return [{"event_id": row["event_id"], "event_type": row["event_type"], "event_payload": _json_loads(row["event_payload_json"]), "created_at": row["created_at"]} for row in rows]

def get_beta_invite_drafts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_beta_invite_draft_registry", "invite_code", db_path, {"payload_json": "payload"})

def get_tester_candidate_intake_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_tester_candidate_intake_locks", "candidate_code", db_path, {"payload_json": "payload"})

def get_invite_send_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_invite_send_lock_contracts", "lock_code", db_path, {"payload_json": "payload"})

def get_access_grant_locks(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_access_grant_lock_contracts", "lock_code", db_path, {"payload_json": "payload"})

def get_beta_role_permission_previews(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_beta_role_permission_preview_matrix", "role_code", db_path, {"payload_json": "payload", "permission_preview_json": "permission_preview"})

def get_tower_beta_gate_handoff_previews(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_tower_beta_gate_handoff_previews", "handoff_code", db_path, {"payload_json": "payload"})

def get_billing_subscription_handoff_previews(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_billing_subscription_lock_handoff_previews", "billing_code", db_path, {"payload_json": "payload"})

def get_beta_access_risk_blockers(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_beta_access_risk_blockers", "blocker_code", db_path, {"payload_json": "payload"})

def validate_beta_access_invite_lock_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_beta_access_invite_components", "gp_number", db_path, {"data_json": "data"})
    invites = get_beta_invite_drafts(db_path)
    candidates = get_tester_candidate_intake_locks(db_path)
    send_locks = get_invite_send_locks(db_path)
    grant_locks = get_access_grant_locks(db_path)
    roles = get_beta_role_permission_previews(db_path)
    tower = get_tower_beta_gate_handoff_previews(db_path)
    billing = get_billing_subscription_handoff_previews(db_path)
    blockers = get_beta_access_risk_blockers(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("INVITE_DRAFT_COUNT_6", len(invites) == len(INVITE_DRAFTS)),
        ("TESTER_CANDIDATE_COUNT_6", len(candidates) == len(TESTER_CANDIDATES)),
        ("INVITE_SEND_LOCK_COUNT_6", len(send_locks) == len(INVITE_SEND_LOCKS)),
        ("ACCESS_GRANT_LOCK_COUNT_8", len(grant_locks) == len(ACCESS_GRANT_LOCKS)),
        ("ROLE_PERMISSION_PREVIEW_COUNT_5", len(roles) == len(ROLE_PERMISSION_PREVIEWS)),
        ("TOWER_HANDOFF_PREVIEW_COUNT_5", len(tower) == len(TOWER_HANDOFF_PREVIEWS)),
        ("BILLING_HANDOFF_PREVIEW_COUNT_5", len(billing) == len(BILLING_HANDOFF_PREVIEWS)),
        ("RISK_BLOCKER_COUNT_14", len(blockers) == len(RISK_BLOCKERS)),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("BETA_ACCESS_LAYER_READY", readiness["beta_access_layer_ready"] is True),
        ("INVITE_LOCK_ACTIVE", readiness["invite_lock_active"] is True),
        ("ACCESS_GRANT_LOCK_ACTIVE", readiness["access_grant_lock_active"] is True),
        ("SAFE_TO_CONTINUE_TO_GP221", readiness["safe_to_continue_to_gp221"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("VAULT_NOT_DONE", readiness["vault_done"] is False),
        ("CLOUDS_PARKED", readiness["clouds_should_continue"] is False),
        ("SECTION_GP211_GP220", readiness["section_range"] == "GP211-GP220"),
        ("NEXT_SECTION_GP221_GP230", readiness["readiness_payload"]["next_section_range"] == "GP221-GP230"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_READY", all(item["component_ready"] is True for item in components)),
        ("ALL_COMPONENTS_LOCKED", all(item["component_locked"] is True for item in components)),
        ("ALL_COMPONENTS_INVITE_ACCESS_LOCKED", all(item["invite_lock_active"] and item["access_grant_lock_active"] for item in components)),
        ("ALL_COMPONENTS_TOWER_BILLING_PREVIEW_ONLY", all(item["tower_gate_preview_only"] and item["billing_preview_only"] for item in components)),
        ("ALL_INVITES_DRAFT_READY", all(item["draft_ready"] is True for item in invites)),
        ("ALL_INVITES_DRAFT_LOCKED", all(item["draft_locked"] is True for item in invites)),
        ("ALL_INVITES_SEND_LOCKED", all(item["send_locked"] is True for item in invites)),
        ("ALL_CANDIDATES_INTAKE_LOCKED", all(item["intake_locked"] is True for item in candidates)),
        ("ALL_CANDIDATES_APPROVAL_LOCKED", all(item["approval_locked"] is True for item in candidates)),
        ("ALL_CANDIDATES_ADD_LOCKED", all(item["add_locked"] is True for item in candidates)),
        ("ALL_SEND_LOCKS_ACTIVE", all(item["invite_send_locked"] and item["invite_delivery_locked"] for item in send_locks)),
        ("ALL_GRANT_LOCKS_ACTIVE", all(item["access_grant_locked"] and item["token_session_locked"] for item in grant_locks)),
        ("ALL_ROLES_PREVIEW_ONLY", all(item["preview_only"] for item in roles)),
        ("ALL_ROLES_ASSIGNMENT_LOCKED", all(item["role_assignment_locked"] and item["permission_grant_locked"] for item in roles)),
        ("ALL_TOWER_PREVIEW_ONLY", all(item["preview_only"] and item["tower_gate_locked"] and item["tower_unlock_locked"] for item in tower)),
        ("ALL_BILLING_PREVIEW_ONLY", all(item["preview_only"] and item["billing_locked"] and item["subscription_locked"] for item in billing)),
        ("ALL_BLOCKERS_ACTIVE", all(item["blocker_active"] for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_BETA_LAUNCH", all(item["blocks_beta_launch"] for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_INVITES_ACCESS", all(item["blocks_invite_send"] and item["blocks_tester_add"] and item["blocks_access_grant"] for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_TOKEN_SESSION", all(item["blocks_token_session"] for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_TOWER_BILLING", all(item["blocks_tower_gate"] and item["blocks_billing_subscription"] for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_AND_BODY", all(item["blocks_provider_unlock"] and item["blocks_provider_api"] and item["blocks_object_body"] and item["blocks_download"] for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DANGEROUS_OPS", all(item["blocks_restore"] and item["blocks_export"] and item["blocks_direct_upload"] and item["blocks_delete"] for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_EXECUTION_DONE", all(item["blocks_execution"] and item["blocks_vault_done"] for item in blockers)),
        ("NO_BLOCKERS_RESOLVED", all(item["resolved"] is False for item in blockers)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("INVITE", invites),
        ("CANDIDATE", candidates),
        ("SENDLOCK", send_locks),
        ("GRANTLOCK", grant_locks),
        ("ROLE", roles),
        ("TOWER", tower),
        ("BILLING", billing),
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
        "invite_draft_count": len(invites),
        "tester_candidate_count": len(candidates),
        "invite_send_lock_count": len(send_locks),
        "access_grant_lock_count": len(grant_locks),
        "role_permission_preview_count": len(roles),
        "tower_handoff_preview_count": len(tower),
        "billing_handoff_preview_count": len(billing),
        "risk_blocker_count": len(blockers),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "beta_access_layer_ready": len(failed) == 0 and readiness["beta_access_layer_ready"] is True,
        "safe_to_continue_to_gp221": len(failed) == 0 and readiness["safe_to_continue_to_gp221"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp211_beta_access_invite_lock_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SHELL_ID, db_path)
    return {"pack": _pack_payload(211, component["pack_name"]), "real_sqlite_backed": True, "shell": component}

def get_gp212_beta_invite_draft_registry(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(INVITE_DRAFT_REGISTRY_ID, db_path)
    rows = get_beta_invite_drafts(db_path)
    return {"pack": _pack_payload(212, component["pack_name"]), "real_sqlite_backed": True, "invite_draft_registry": component, "invite_draft_count": len(rows), "invites": rows}

def get_gp213_tester_candidate_intake_lock_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(TESTER_INTAKE_LOCK_ID, db_path)
    rows = get_tester_candidate_intake_locks(db_path)
    return {"pack": _pack_payload(213, component["pack_name"]), "real_sqlite_backed": True, "tester_candidate_intake_lock_board": component, "tester_candidate_count": len(rows), "candidates": rows}

def get_gp214_invite_send_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(INVITE_SEND_LOCK_ID, db_path)
    rows = get_invite_send_locks(db_path)
    return {"pack": _pack_payload(214, component["pack_name"]), "real_sqlite_backed": True, "invite_send_lock_contract": component, "invite_send_lock_count": len(rows), "locks": rows}

def get_gp215_access_grant_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(ACCESS_GRANT_LOCK_ID, db_path)
    rows = get_access_grant_locks(db_path)
    return {"pack": _pack_payload(215, component["pack_name"]), "real_sqlite_backed": True, "access_grant_lock_contract": component, "access_grant_lock_count": len(rows), "locks": rows}

def get_gp216_beta_role_permission_preview_matrix(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(ROLE_PERMISSION_MATRIX_ID, db_path)
    rows = get_beta_role_permission_previews(db_path)
    return {"pack": _pack_payload(216, component["pack_name"]), "real_sqlite_backed": True, "role_permission_matrix": component, "role_permission_preview_count": len(rows), "roles": rows}

def get_gp217_tower_beta_gate_handoff_preview(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(TOWER_GATE_HANDOFF_ID, db_path)
    rows = get_tower_beta_gate_handoff_previews(db_path)
    return {"pack": _pack_payload(217, component["pack_name"]), "real_sqlite_backed": True, "tower_handoff_preview": component, "tower_handoff_preview_count": len(rows), "handoffs": rows}

def get_gp218_billing_subscription_lock_handoff_preview(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(BILLING_HANDOFF_ID, db_path)
    rows = get_billing_subscription_handoff_previews(db_path)
    return {"pack": _pack_payload(218, component["pack_name"]), "real_sqlite_backed": True, "billing_handoff_preview": component, "billing_handoff_preview_count": len(rows), "handoffs": rows}

def get_gp219_beta_access_risk_blocker_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RISK_BLOCKER_ID, db_path)
    rows = get_beta_access_risk_blockers(db_path)
    return {"pack": _pack_payload(219, component["pack_name"]), "real_sqlite_backed": True, "risk_blocker_board": component, "risk_blocker_count": len(rows), "blockers": rows}

def get_gp220_beta_access_invite_lock_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_access_invite_lock_layer(db_path)
    return {"pack": _pack_payload(220, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_access_invite_lock_layer(db_path)
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
            "source_gp210_readiness_id": component["source_gp210_readiness_id"],
            "source_gp210_readiness_hash": component["source_gp210_readiness_hash"],
            "source_gp210_readiness_score": component["source_gp210_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "beta_access_layer_ready": component["beta_access_layer_ready"],
            "invite_lock_active": component["invite_lock_active"],
            "access_grant_lock_active": component["access_grant_lock_active"],
            "tower_gate_preview_only": component["tower_gate_preview_only"],
            "billing_preview_only": component["billing_preview_only"],
            "vault_not_done": component["vault_not_done"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp221": validation["safe_to_continue_to_gp221"],
            "foundation_status": "beta_access_invite_lock_layer_ready_invites_access_tower_billing_locked_vault_not_done_safe_to_continue",
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
            "beta_role_assigned": component["beta_role_assigned"],
            "beta_permission_granted": component["beta_permission_granted"],
            "billing_flow_created": component["billing_flow_created"],
            "subscription_flow_created": component["subscription_flow_created"],
            "customer_portal_created": component["customer_portal_created"],
            "payment_processor_called": component["payment_processor_called"],
            "tower_billing_handoff_created": component["tower_billing_handoff_created"],
            "provider_unlock_requested": component["provider_unlock_requested"],
            "provider_unlock_approved": component["provider_unlock_approved"],
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
            "clouds_status": "parked_do_not_continue_from_vault_gp220",
        },
        "validation": validation,
    }

def get_gp211_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(211, SHELL_ID, "VAULT_GP212_BETA_INVITE_DRAFT_REGISTRY", db_path)

def get_gp212_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(212, INVITE_DRAFT_REGISTRY_ID, "VAULT_GP213_TESTER_CANDIDATE_INTAKE_LOCK_BOARD", db_path)

def get_gp213_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(213, TESTER_INTAKE_LOCK_ID, "VAULT_GP214_INVITE_SEND_LOCK_CONTRACT", db_path)

def get_gp214_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(214, INVITE_SEND_LOCK_ID, "VAULT_GP215_ACCESS_GRANT_LOCK_CONTRACT", db_path)

def get_gp215_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(215, ACCESS_GRANT_LOCK_ID, "VAULT_GP216_BETA_ROLE_PERMISSION_PREVIEW_MATRIX", db_path)

def get_gp216_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(216, ROLE_PERMISSION_MATRIX_ID, "VAULT_GP217_TOWER_BETA_GATE_HANDOFF_PREVIEW", db_path)

def get_gp217_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(217, TOWER_GATE_HANDOFF_ID, "VAULT_GP218_BILLING_SUBSCRIPTION_LOCK_HANDOFF_PREVIEW", db_path)

def get_gp218_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(218, BILLING_HANDOFF_ID, "VAULT_GP219_BETA_ACCESS_RISK_BLOCKER_BOARD", db_path)

def get_gp219_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(219, RISK_BLOCKER_ID, "VAULT_GP220_BETA_ACCESS_INVITE_LOCK_READINESS_CHECKPOINT", db_path)

def get_gp220_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(220, READINESS_ID, NEXT_PACK, db_path)
    status["gp220_status"]["next_section"] = NEXT_SECTION_ID
    status["gp220_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp220_status"]["next_pack"] = NEXT_PACK
    return status

def get_beta_access_invite_lock_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_beta_access_invite_lock_layer(db_path)
    components = _rows("vault_beta_access_invite_components", "gp_number", db_path, {"data_json": "data"})
    invites = get_beta_invite_drafts(db_path)
    candidates = get_tester_candidate_intake_locks(db_path)
    send_locks = get_invite_send_locks(db_path)
    grant_locks = get_access_grant_locks(db_path)
    roles = get_beta_role_permission_previews(db_path)
    tower = get_tower_beta_gate_handoff_previews(db_path)
    billing = get_billing_subscription_handoff_previews(db_path)
    blockers = get_beta_access_risk_blockers(db_path)
    readiness = _readiness(db_path)
    validation = validate_beta_access_invite_lock_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "invite_drafts": {"invite_draft_count": len(invites), "invites": invites},
        "tester_candidates": {"tester_candidate_count": len(candidates), "candidates": candidates},
        "invite_send_locks": {"invite_send_lock_count": len(send_locks), "locks": send_locks},
        "access_grant_locks": {"access_grant_lock_count": len(grant_locks), "locks": grant_locks},
        "role_permission_previews": {"role_permission_preview_count": len(roles), "roles": roles},
        "tower_handoff_previews": {"tower_handoff_preview_count": len(tower), "handoffs": tower},
        "billing_handoff_previews": {"billing_handoff_preview_count": len(billing), "handoffs": billing},
        "blockers": {"risk_blocker_count": len(blockers), "blockers": blockers},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "beta_access_invite_lock_layer_ready": True,
            "beta_access_layer_ready": validation["beta_access_layer_ready"],
            "safe_to_continue_to_gp221": validation["safe_to_continue_to_gp221"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "invite_lock_active": True,
            "access_grant_lock_active": True,
            "beta_launch_approved": False,
            "beta_invite_created": False,
            "beta_invite_sent": False,
            "tester_candidate_submitted": False,
            "tester_candidate_approved": False,
            "beta_tester_added": False,
            "beta_tester_access_granted": False,
            "beta_tester_access_enabled": False,
            "beta_access_token_created": False,
            "beta_access_session_created": False,
            "beta_role_assigned": False,
            "beta_permission_granted": False,
            "billing_flow_created": False,
            "subscription_flow_created": False,
            "customer_portal_created": False,
            "payment_processor_called": False,
            "tower_billing_handoff_created": False,
            "provider_unlock_requested": False,
            "provider_unlock_approved": False,
            "provider_api_called": False,
            "provider_search_executed": False,
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
            "page": "/vault/beta-access-invite-lock-layer",
            "json": "/vault/beta-access-invite-lock-layer.json",
            "gp211": "/vault/gp211-status.json",
            "gp212": "/vault/gp212-status.json",
            "gp213": "/vault/gp213-status.json",
            "gp214": "/vault/gp214-status.json",
            "gp215": "/vault/gp215-status.json",
            "gp216": "/vault/gp216-status.json",
            "gp217": "/vault/gp217-status.json",
            "gp218": "/vault/gp218-status.json",
            "gp219": "/vault/gp219-status.json",
            "gp220": "/vault/gp220-status.json",
        },
    }

def render_beta_access_invite_lock_layer_page() -> str:
    home = get_beta_access_invite_lock_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    invite_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['invite_name'])}</strong>
          <span>{escape(item['invite_status'])}</span>
          <code>{escape(item['invite_audience'])} · send locked</code>
        </article>
        """
        for item in home["invite_drafts"]["invites"]
    )

    lock_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['lock_name'])}</strong>
          <span>{escape(item['lock_status'])}</span>
          <code>access grant locked</code>
        </article>
        """
        for item in home["access_grant_locks"]["locks"]
    )

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP211-GP220 Beta Access Invite Lock Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 211-220</div>
    <div class="eyebrow">Beta Access and Invite Lock Layer · GP211-GP220</div>
    <h1>Beta Access + Invite Locks</h1>
    <p>This layer builds invite drafts, tester intake locks, access grant locks, role previews, Tower handoff previews, billing previews, and risk blockers. Nothing is sent or granted.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['invite_draft_count']}</strong><span>invite drafts</span></div>
      <div class="metric"><strong>{home['store']['access_grant_lock_count']}</strong><span>access locks</span></div>
      <div class="metric"><strong>{home['store']['risk_blocker_count']}</strong><span>risk blockers</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP211-GP220 built</span>
      <span class="pill ok">Safe to GP221</span>
      <span class="pill danger">No invite sent</span>
      <span class="pill danger">No tester added</span>
      <span class="pill danger">No access granted</span>
      <span class="pill danger">No token/session</span>
      <span class="pill danger">No Tower gate</span>
      <span class="pill danger">No billing flow</span>
      <span class="pill danger">No execution</span>
      <span class="pill danger">Vault not done</span>
    </div>
  </section>

  <section class="section">
    <h2>Invite Draft Registry</h2>
    <div class="cards">{invite_cards}</div>
  </section>

  <section class="section">
    <h2>Access Grant Locks</h2>
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
