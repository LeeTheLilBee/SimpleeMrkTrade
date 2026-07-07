
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — TELLER TO TOWER REQUEST HANDOFF LAYER / GP451-GP460"
LAYER_ID = "vault_gp451_460_teller_to_tower_request_handoff_layer"
READINESS_LABEL = "Teller-to-Tower request handoff layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_teller_to_tower_request_handoff_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.headless_tower_status_bridge_layer_service import (
        get_teller_workflow_proof_status_bridge,
        get_tower_owner_clearance_status_bridge,
        get_tower_teller_bridge_redaction_contract,
        validate_headless_tower_status_bridge_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP451-GP460 requires GP441-GP450 Headless Tower status bridge layer first."
    ) from exc


_GP451_INIT_CACHE = None

DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": "Teller -> Tower -> Vault -> Tower -> Teller",
    "teller_can_create_requests": True,
    "teller_can_call_vault_directly": False,
    "tower_must_authorize_protocol": True,
    "vault_answers_tower_only": True,
    "people_enter_vault_directly": False,
}

LOCKS = {
    "teller_to_tower_request_handoff_layer": True,
    "workflow_request_packet_creation_allowed": True,
    "tower_addressed_handoff_allowed": True,
    "requester_role_context_allowed": True,
    "document_proof_scope_metadata_allowed": True,
    "sensitivity_redaction_classifier_allowed": True,
    "tower_approval_flag_allowed": True,
    "teller_workflow_receipt_draft_allowed": True,
    "tower_intake_payload_preview_allowed": True,

    "teller_to_vault_direct_call_allowed": False,
    "vault_direct_request_from_teller_allowed": False,
    "vault_direct_approval_from_teller_allowed": False,
    "view_protocol_execution_allowed": False,
    "download_protocol_execution_allowed": False,
    "proof_protocol_execution_allowed": False,
    "public_vault_dashboard_allowed": False,
    "standalone_external_vault_dashboard_allowed": False,
    "direct_vault_user_portal_allowed": False,
    "employee_vault_browsing_allowed": False,
    "vendor_vault_browsing_allowed": False,
    "customer_vault_browsing_allowed": False,
    "external_collaborator_browsing_allowed": False,
    "public_download_unlocked": False,
    "beta_download_unlocked": False,
    "public_url_created": False,
    "share_link_created": False,
    "raw_file_bytes_returned_by_json": False,
    "raw_path_exposed": False,
    "raw_file_url_exposed": False,
    "raw_download_token_exposed": False,
    "raw_share_token_exposed": False,
    "final_rebuilt_index_write_allowed": False,
    "final_pack_overwrite_allowed": False,
    "sealed_pack_bytes_write_allowed": False,
    "public_upload_unlocked": False,
    "beta_upload_unlocked": False,
    "provider_upload_unlocked": False,
    "provider_storage_required": False,
    "file_delete_unlocked": False,
    "hard_delete_allowed": False,
    "purge_allowed": False,
    "restore_execution_allowed": False,
    "quarantine_release_allowed": False,
    "physical_object_move_allowed": False,
    "external_sync_unlocked": False,
}

PACKS = [
    {"gp": 451, "title": "Teller-to-Tower Request Handoff Shell", "status": "ready", "route": "/vault/teller-to-tower-request-handoff-shell.json"},
    {"gp": 452, "title": "Workflow Request Packet Contract", "status": "ready", "route": "/vault/workflow-request-packet-contract.json"},
    {"gp": 453, "title": "Requester Role Context Board", "status": "ready", "route": "/vault/requester-role-context-board.json"},
    {"gp": 454, "title": "Document/Proof Type Scope Board", "status": "ready", "route": "/vault/document-proof-type-scope-board.json"},
    {"gp": 455, "title": "Sensitivity and Redaction Need Classifier", "status": "ready", "route": "/vault/sensitivity-redaction-need-classifier.json"},
    {"gp": 456, "title": "Tower Approval Required Flag Builder", "status": "ready", "route": "/vault/tower-approval-required-flag-builder.json"},
    {"gp": 457, "title": "Teller Workflow Receipt Draft Ledger", "status": "ready", "route": "/vault/teller-workflow-receipt-draft-ledger.json"},
    {"gp": 458, "title": "Tower Intake Payload Preview Board", "status": "ready", "route": "/vault/tower-intake-payload-preview-board.json"},
    {"gp": 459, "title": "Teller-to-Tower Handoff Safety Blocker Board", "status": "ready", "route": "/vault/teller-to-tower-handoff-safety-blocker-board.json"},
    {"gp": 460, "title": "Teller-to-Tower Request Handoff Readiness Checkpoint", "status": "ready", "route": "/vault/teller-to-tower-request-handoff-readiness-checkpoint.json"},
]

WORKFLOW_TYPES = [
    {
        "workflow_type": "employee_document_request",
        "requester_role": "employee",
        "document_or_proof_type": "employee_document_status",
        "requested_output_type": "status",
        "sensitivity_level": "restricted",
    },
    {
        "workflow_type": "vendor_document_request",
        "requester_role": "vendor",
        "document_or_proof_type": "vendor_document_status",
        "requested_output_type": "proof",
        "sensitivity_level": "restricted",
    },
    {
        "workflow_type": "payroll_proof_request",
        "requester_role": "payroll_admin",
        "document_or_proof_type": "payroll_proof",
        "requested_output_type": "proof",
        "sensitivity_level": "confidential",
    },
    {
        "workflow_type": "onboarding_packet_request",
        "requester_role": "manager",
        "document_or_proof_type": "onboarding_packet",
        "requested_output_type": "receipt",
        "sensitivity_level": "restricted",
    },
    {
        "workflow_type": "agreement_proof_request",
        "requester_role": "owner_admin",
        "document_or_proof_type": "agreement_proof",
        "requested_output_type": "preview",
        "sensitivity_level": "high",
    },
    {
        "workflow_type": "payment_receipt_request",
        "requester_role": "finance_admin",
        "document_or_proof_type": "payment_receipt",
        "requested_output_type": "receipt",
        "sensitivity_level": "confidential",
    },
]

BLOCKERS = [
    {"blocker_id": "no_teller_to_vault_direct_call", "blocked_action": "teller_to_vault_direct_call", "allowed": False, "reason": "Teller requests must go to Tower first."},
    {"blocker_id": "no_teller_vault_download", "blocked_action": "teller_direct_download_from_vault", "allowed": False, "reason": "Tower owns download protocol."},
    {"blocker_id": "no_teller_vault_view", "blocked_action": "teller_direct_view_from_vault", "allowed": False, "reason": "Tower owns view protocol."},
    {"blocker_id": "no_teller_vault_proof_call", "blocked_action": "teller_direct_proof_call_to_vault", "allowed": False, "reason": "Tower owns proof protocol."},
    {"blocker_id": "no_public_vault_dashboard", "blocked_action": "public_vault_dashboard", "allowed": False, "reason": "Tower is the face; Vault remains headless."},
    {"blocker_id": "no_direct_vault_user_portal", "blocked_action": "direct_vault_user_portal", "allowed": False, "reason": "People do not enter Vault directly."},
    {"blocker_id": "no_employee_vendor_customer_browse", "blocked_action": "employee_vendor_customer_vault_browsing", "allowed": False, "reason": "Teller handles workflows, not Vault browsing."},
    {"blocker_id": "no_external_collaborator_browse", "blocked_action": "external_collaborator_browsing", "allowed": False, "reason": "No shared-drive behavior."},
    {"blocker_id": "no_public_links", "blocked_action": "public_links_or_raw_urls", "allowed": False, "reason": "Request packets never include public links or raw URLs."},
    {"blocker_id": "no_raw_file_bytes_json", "blocked_action": "raw_file_bytes_json", "allowed": False, "reason": "Handoff packets are metadata only."},
    {"blocker_id": "no_raw_paths_or_tokens", "blocked_action": "raw_path_or_token_exposure", "allowed": False, "reason": "Handoff packets never expose paths or tokens."},
    {"blocker_id": "no_protocol_execution", "blocked_action": "view_download_proof_protocol_execution", "allowed": False, "reason": "This layer only hands requests to Tower; protocol comes next."},
    {"blocker_id": "no_provider_dependency", "blocked_action": "provider_dependency", "allowed": False, "reason": "Local-first sealed memory remains default."},
    {"blocker_id": "no_delete_restore_move", "blocked_action": "delete_restore_physical_move", "allowed": False, "reason": "Handoff does not mutate Vault lifecycle state or move objects."},
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _rows(conn: sqlite3.Connection, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    return [dict(row) for row in conn.execute(query, params).fetchall()]


def _request_id(workflow_type: str, active_file_id: str) -> str:
    return "teller_to_tower_request_" + calculate_sha256_bytes((workflow_type + "|" + active_file_id).encode("utf-8"))[:24]


def _role_context_id(request_id: str) -> str:
    return "requester_role_context_" + calculate_sha256_bytes(("role_context|" + request_id).encode("utf-8"))[:24]


def _scope_id(request_id: str) -> str:
    return "document_proof_scope_" + calculate_sha256_bytes(("doc_proof_scope|" + request_id).encode("utf-8"))[:24]


def _classifier_id(request_id: str) -> str:
    return "sensitivity_redaction_classifier_" + calculate_sha256_bytes(("sensitivity|" + request_id).encode("utf-8"))[:24]


def _approval_flag_id(request_id: str) -> str:
    return "tower_approval_flag_" + calculate_sha256_bytes(("tower_approval|" + request_id).encode("utf-8"))[:24]


def _receipt_draft_id(request_id: str) -> str:
    return "teller_workflow_receipt_draft_" + calculate_sha256_bytes(("teller_receipt|" + request_id).encode("utf-8"))[:24]


def _intake_preview_id(request_id: str) -> str:
    return "tower_intake_payload_preview_" + calculate_sha256_bytes(("tower_intake|" + request_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    teller_proofs = get_teller_workflow_proof_status_bridge().get("proof_status_rows", [])
    clearances = get_tower_owner_clearance_status_bridge().get("clearance_status_rows", [])
    redactions = get_tower_teller_bridge_redaction_contract().get("redaction_contracts", [])

    clearance_by_file = {row["active_file_id"]: row for row in clearances}
    redaction_by_file = {row["active_file_id"]: row for row in redactions}

    rows = []
    for index, proof in enumerate(teller_proofs):
        active_file_id = proof["active_file_id"]
        workflow = WORKFLOW_TYPES[index % len(WORKFLOW_TYPES)]
        clearance = clearance_by_file.get(active_file_id, {})
        redaction = redaction_by_file.get(active_file_id, {})
        rows.append(
            {
                "active_file_id": active_file_id,
                "rebuild_candidate_id": proof["rebuild_candidate_id"],
                "workflow_type": workflow["workflow_type"],
                "requester_role": workflow["requester_role"],
                "requester_entity": "Simplee ecosystem internal workflow",
                "subject_person_or_vendor": "redacted_subject_reference",
                "document_or_proof_type": workflow["document_or_proof_type"],
                "requested_output_type": workflow["requested_output_type"],
                "sensitivity_level": workflow["sensitivity_level"],
                "reason_for_request": "workflow_required_status_or_proof",
                "business_context": "Tower-controlled Vault request handoff",
                "deadline_status": "standard",
                "teller_workflow_required": bool(proof.get("teller_workflow_required", 1)),
                "document_request_status_allowed": bool(proof.get("document_request_status_allowed", 1)),
                "proof_hash_allowed": bool(proof.get("proof_hash_allowed", 1)),
                "direct_vault_browse_allowed": bool(proof.get("direct_vault_browse_allowed", 0)),
                "raw_file_bytes_allowed": bool(proof.get("raw_file_bytes_allowed", 0)),
                "public_link_allowed": bool(proof.get("public_link_allowed", 0)),
                "owner_admin_required": bool(clearance.get("owner_admin_required", 1)),
                "step_up_required": bool(clearance.get("step_up_required", 1)),
                "tower_permission_required": bool(clearance.get("tower_permission_required", 1)),
                "vault_direct_approval_allowed": bool(clearance.get("vault_direct_approval_allowed", 0)),
                "redacted_fields": redaction.get("redacted_fields", "raw_file_bytes|raw_path|raw_file_url|raw_download_token|raw_share_token|public_link|direct_browse|shared_folder|physical_storage_path"),
                "raw_file_bytes_redacted": bool(redaction.get("raw_file_bytes_redacted", 1)),
                "raw_path_redacted": bool(redaction.get("raw_path_redacted", 1)),
                "raw_file_url_redacted": bool(redaction.get("raw_file_url_redacted", 1)),
                "raw_token_redacted": bool(redaction.get("raw_token_redacted", 1)),
                "public_link_redacted": bool(redaction.get("public_link_redacted", 1)),
                "direct_browse_redacted": bool(redaction.get("direct_browse_redacted", 1)),
            }
        )
    return rows


def initialize_teller_to_tower_request_handoff_layer() -> Dict[str, Any]:
    global _GP451_INIT_CACHE
    if _GP451_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP451_INIT_CACHE)

    previous = validate_headless_tower_status_bridge_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_request_packets (
                request_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                rebuild_candidate_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                requester_role TEXT NOT NULL,
                requester_entity TEXT NOT NULL,
                subject_person_or_vendor TEXT NOT NULL,
                document_or_proof_type TEXT NOT NULL,
                requested_output_type TEXT NOT NULL,
                reason_for_request TEXT NOT NULL,
                business_context TEXT NOT NULL,
                deadline_status TEXT NOT NULL,
                addressed_to TEXT NOT NULL,
                vault_direct_request_allowed INTEGER NOT NULL,
                tower_approval_required INTEGER NOT NULL,
                packet_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS requester_role_contexts (
                role_context_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                requester_role TEXT NOT NULL,
                requester_entity TEXT NOT NULL,
                role_context_state TEXT NOT NULL,
                tower_identity_check_required INTEGER NOT NULL,
                tower_permission_check_required INTEGER NOT NULL,
                teller_can_self_approve INTEGER NOT NULL,
                vault_direct_approval_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS document_proof_type_scopes (
                scope_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                document_or_proof_type TEXT NOT NULL,
                requested_output_type TEXT NOT NULL,
                scope_state TEXT NOT NULL,
                tower_protocol_required TEXT NOT NULL,
                vault_direct_access_allowed INTEGER NOT NULL,
                raw_file_bytes_allowed INTEGER NOT NULL,
                public_link_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sensitivity_redaction_classifiers (
                classifier_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                sensitivity_level TEXT NOT NULL,
                classifier_state TEXT NOT NULL,
                redaction_required INTEGER NOT NULL,
                step_up_required INTEGER NOT NULL,
                owner_admin_required INTEGER NOT NULL,
                raw_file_bytes_redacted INTEGER NOT NULL,
                raw_path_redacted INTEGER NOT NULL,
                raw_file_url_redacted INTEGER NOT NULL,
                raw_token_redacted INTEGER NOT NULL,
                public_link_redacted INTEGER NOT NULL,
                direct_browse_redacted INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_approval_required_flags (
                approval_flag_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                approval_state TEXT NOT NULL,
                tower_approval_required INTEGER NOT NULL,
                tower_permission_required INTEGER NOT NULL,
                tower_protocol_gate_required INTEGER NOT NULL,
                owner_admin_required INTEGER NOT NULL,
                step_up_required INTEGER NOT NULL,
                teller_to_vault_direct_call_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS teller_workflow_receipt_drafts (
                receipt_draft_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                receipt_state TEXT NOT NULL,
                receipt_finalized INTEGER NOT NULL,
                tower_receipt_required INTEGER NOT NULL,
                vault_service_receipt_required INTEGER NOT NULL,
                receipt_hash TEXT NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_intake_payload_previews (
                intake_preview_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                preview_state TEXT NOT NULL,
                addressed_to TEXT NOT NULL,
                tower_intake_ready INTEGER NOT NULL,
                vault_request_ready INTEGER NOT NULL,
                tower_protocol_pending INTEGER NOT NULL,
                payload_preview_only INTEGER NOT NULL,
                raw_file_bytes_included INTEGER NOT NULL,
                raw_path_included INTEGER NOT NULL,
                public_link_included INTEGER NOT NULL,
                intake_payload_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS teller_to_tower_handoff_safety_blockers (
                blocker_id TEXT PRIMARY KEY,
                blocked_action TEXT NOT NULL,
                allowed INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        now = _now()

        for blocker in BLOCKERS:
            conn.execute(
                """
                INSERT OR REPLACE INTO teller_to_tower_handoff_safety_blockers (
                    blocker_id, blocked_action, allowed, reason, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    blocker["blocker_id"],
                    blocker["blocked_action"],
                    1 if blocker["allowed"] else 0,
                    blocker["reason"],
                    now,
                    now,
                ),
            )

        for row in _candidate_source_rows():
            request_id = _request_id(row["workflow_type"], row["active_file_id"])
            role_context_id = _role_context_id(request_id)
            scope_id = _scope_id(request_id)
            classifier_id = _classifier_id(request_id)
            approval_flag_id = _approval_flag_id(request_id)
            receipt_draft_id = _receipt_draft_id(request_id)
            intake_preview_id = _intake_preview_id(request_id)

            packet_material = {
                "active_file_id": row["active_file_id"],
                "workflow_type": row["workflow_type"],
                "requester_role": row["requester_role"],
                "document_or_proof_type": row["document_or_proof_type"],
                "requested_output_type": row["requested_output_type"],
                "addressed_to": "Tower",
                "vault_direct_request_allowed": False,
                "tower_approval_required": True,
            }
            packet_hash = calculate_sha256_bytes(repr(sorted(packet_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO workflow_request_packets (
                    request_id, active_file_id, rebuild_candidate_id,
                    workflow_type, requester_role, requester_entity,
                    subject_person_or_vendor, document_or_proof_type,
                    requested_output_type, reason_for_request,
                    business_context, deadline_status, addressed_to,
                    vault_direct_request_allowed, tower_approval_required,
                    packet_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_id,
                    row["active_file_id"],
                    row["rebuild_candidate_id"],
                    row["workflow_type"],
                    row["requester_role"],
                    row["requester_entity"],
                    row["subject_person_or_vendor"],
                    row["document_or_proof_type"],
                    row["requested_output_type"],
                    row["reason_for_request"],
                    row["business_context"],
                    row["deadline_status"],
                    "Tower",
                    0,
                    1,
                    packet_hash,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO requester_role_contexts (
                    role_context_id, request_id, requester_role,
                    requester_entity, role_context_state,
                    tower_identity_check_required,
                    tower_permission_check_required,
                    teller_can_self_approve,
                    vault_direct_approval_allowed,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    role_context_id,
                    request_id,
                    row["requester_role"],
                    row["requester_entity"],
                    "requester_role_context_ready_for_tower_review",
                    1,
                    1,
                    0,
                    0,
                    now,
                ),
            )

            tower_protocol = {
                "status": "status_protocol",
                "proof": "proof_protocol",
                "receipt": "receipt_protocol",
                "preview": "view_protocol",
                "download": "download_protocol",
            }.get(row["requested_output_type"], "status_protocol")

            conn.execute(
                """
                INSERT OR REPLACE INTO document_proof_type_scopes (
                    scope_id, request_id, document_or_proof_type,
                    requested_output_type, scope_state,
                    tower_protocol_required, vault_direct_access_allowed,
                    raw_file_bytes_allowed, public_link_allowed,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scope_id,
                    request_id,
                    row["document_or_proof_type"],
                    row["requested_output_type"],
                    "document_proof_scope_ready_for_tower_protocol_gate",
                    tower_protocol,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO sensitivity_redaction_classifiers (
                    classifier_id, request_id, sensitivity_level,
                    classifier_state, redaction_required,
                    step_up_required, owner_admin_required,
                    raw_file_bytes_redacted, raw_path_redacted,
                    raw_file_url_redacted, raw_token_redacted,
                    public_link_redacted, direct_browse_redacted,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    classifier_id,
                    request_id,
                    row["sensitivity_level"],
                    "sensitivity_redaction_classified_for_tower",
                    1,
                    1 if row["sensitivity_level"] in {"confidential", "high"} else 0,
                    1 if row["sensitivity_level"] in {"confidential", "high"} else 0,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_approval_required_flags (
                    approval_flag_id, request_id, approval_state,
                    tower_approval_required, tower_permission_required,
                    tower_protocol_gate_required, owner_admin_required,
                    step_up_required, teller_to_vault_direct_call_allowed,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval_flag_id,
                    request_id,
                    "tower_approval_required_before_vault_protocol",
                    1,
                    1,
                    1,
                    1 if row["sensitivity_level"] in {"confidential", "high"} else 0,
                    1 if row["sensitivity_level"] in {"confidential", "high"} else 0,
                    0,
                    now,
                ),
            )

            receipt_hash = calculate_sha256_bytes(
                f"teller-workflow-receipt-draft|{request_id}|{packet_hash}|Tower|no-vault-direct".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO teller_workflow_receipt_drafts (
                    receipt_draft_id, request_id, workflow_type,
                    receipt_state, receipt_finalized,
                    tower_receipt_required, vault_service_receipt_required,
                    receipt_hash, append_only, mutable, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    receipt_draft_id,
                    request_id,
                    row["workflow_type"],
                    "teller_workflow_receipt_draft_ready_for_tower_intake",
                    0,
                    1,
                    1,
                    receipt_hash,
                    1,
                    0,
                    now,
                ),
            )

            intake_material = {
                "request_id": request_id,
                "workflow_type": row["workflow_type"],
                "addressed_to": "Tower",
                "packet_hash": packet_hash,
                "receipt_hash": receipt_hash,
                "tower_protocol_pending": True,
                "vault_request_ready": False,
                "raw_file_bytes_included": False,
                "raw_path_included": False,
                "public_link_included": False,
            }
            intake_hash = calculate_sha256_bytes(repr(sorted(intake_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_intake_payload_previews (
                    intake_preview_id, request_id, workflow_type,
                    preview_state, addressed_to, tower_intake_ready,
                    vault_request_ready, tower_protocol_pending,
                    payload_preview_only, raw_file_bytes_included,
                    raw_path_included, public_link_included,
                    intake_payload_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    intake_preview_id,
                    request_id,
                    row["workflow_type"],
                    "tower_intake_payload_preview_ready_no_vault_call",
                    "Tower",
                    1,
                    0,
                    1,
                    1,
                    0,
                    0,
                    0,
                    intake_hash,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_headless_tower_status_bridge_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP451_INIT_CACHE = dict(result)
    return result


def get_teller_to_tower_request_handoff_shell() -> Dict[str, Any]:
    init = initialize_teller_to_tower_request_handoff_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 451,
        "title": "Teller-to-Tower Request Handoff Shell",
        "ready": True,
        "initialized": init,
        "doctrine": DOCTRINE,
        "correct_flow": DOCTRINE["correct_flow"],
        "teller_direct_vault_call_allowed": False,
        "vault_answers_tower_only": True,
        "locks": LOCKS,
    }


def get_workflow_request_packet_contract() -> Dict[str, Any]:
    initialize_teller_to_tower_request_handoff_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM workflow_request_packets ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 452,
        "title": "Workflow Request Packet Contract",
        "ready": True,
        "packet_count": len(rows),
        "request_packets": rows,
        "all_addressed_to_tower": all(item["addressed_to"] == "Tower" for item in rows),
        "no_vault_direct_request": all(not bool(item["vault_direct_request_allowed"]) for item in rows),
        "all_tower_approval_required": all(bool(item["tower_approval_required"]) for item in rows),
    }


def get_requester_role_context_board() -> Dict[str, Any]:
    initialize_teller_to_tower_request_handoff_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM requester_role_contexts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 453,
        "title": "Requester Role Context Board",
        "ready": True,
        "role_context_count": len(rows),
        "role_contexts": rows,
        "all_tower_identity_check_required": all(bool(item["tower_identity_check_required"]) for item in rows),
        "all_tower_permission_check_required": all(bool(item["tower_permission_check_required"]) for item in rows),
        "no_teller_self_approval": all(not bool(item["teller_can_self_approve"]) for item in rows),
        "no_vault_direct_approval": all(not bool(item["vault_direct_approval_allowed"]) for item in rows),
    }


def get_document_proof_type_scope_board() -> Dict[str, Any]:
    initialize_teller_to_tower_request_handoff_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM document_proof_type_scopes ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 454,
        "title": "Document/Proof Type Scope Board",
        "ready": True,
        "scope_count": len(rows),
        "scopes": rows,
        "all_tower_protocol_required": all(bool(item["tower_protocol_required"]) for item in rows),
        "no_vault_direct_access": all(not bool(item["vault_direct_access_allowed"]) for item in rows),
        "no_raw_file_bytes_allowed": all(not bool(item["raw_file_bytes_allowed"]) for item in rows),
        "no_public_links_allowed": all(not bool(item["public_link_allowed"]) for item in rows),
    }


def get_sensitivity_redaction_need_classifier() -> Dict[str, Any]:
    initialize_teller_to_tower_request_handoff_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM sensitivity_redaction_classifiers ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 455,
        "title": "Sensitivity and Redaction Need Classifier",
        "ready": True,
        "classifier_count": len(rows),
        "classifiers": rows,
        "all_redaction_required": all(bool(item["redaction_required"]) for item in rows),
        "all_raw_file_bytes_redacted": all(bool(item["raw_file_bytes_redacted"]) for item in rows),
        "all_raw_paths_redacted": all(bool(item["raw_path_redacted"]) for item in rows),
        "all_raw_file_urls_redacted": all(bool(item["raw_file_url_redacted"]) for item in rows),
        "all_raw_tokens_redacted": all(bool(item["raw_token_redacted"]) for item in rows),
        "all_public_links_redacted": all(bool(item["public_link_redacted"]) for item in rows),
        "all_direct_browse_redacted": all(bool(item["direct_browse_redacted"]) for item in rows),
    }


def get_tower_approval_required_flag_builder() -> Dict[str, Any]:
    initialize_teller_to_tower_request_handoff_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_approval_required_flags ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 456,
        "title": "Tower Approval Required Flag Builder",
        "ready": True,
        "approval_flag_count": len(rows),
        "approval_flags": rows,
        "all_tower_approval_required": all(bool(item["tower_approval_required"]) for item in rows),
        "all_tower_permission_required": all(bool(item["tower_permission_required"]) for item in rows),
        "all_tower_protocol_gate_required": all(bool(item["tower_protocol_gate_required"]) for item in rows),
        "no_teller_to_vault_direct_call": all(not bool(item["teller_to_vault_direct_call_allowed"]) for item in rows),
    }


def get_teller_workflow_receipt_draft_ledger() -> Dict[str, Any]:
    initialize_teller_to_tower_request_handoff_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM teller_workflow_receipt_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 457,
        "title": "Teller Workflow Receipt Draft Ledger",
        "ready": True,
        "receipt_draft_count": len(rows),
        "receipt_drafts": rows,
        "all_receipts_draft": all(not bool(item["receipt_finalized"]) for item in rows),
        "all_tower_receipts_required": all(bool(item["tower_receipt_required"]) for item in rows),
        "all_vault_service_receipts_required": all(bool(item["vault_service_receipt_required"]) for item in rows),
        "all_append_only": all(bool(item["append_only"]) for item in rows),
        "all_immutable": all(not bool(item["mutable"]) for item in rows),
    }


def get_tower_intake_payload_preview_board() -> Dict[str, Any]:
    initialize_teller_to_tower_request_handoff_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_intake_payload_previews ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 458,
        "title": "Tower Intake Payload Preview Board",
        "ready": True,
        "intake_preview_count": len(rows),
        "intake_previews": rows,
        "all_addressed_to_tower": all(item["addressed_to"] == "Tower" for item in rows),
        "all_tower_intake_ready": all(bool(item["tower_intake_ready"]) for item in rows),
        "all_vault_request_not_ready_yet": all(not bool(item["vault_request_ready"]) for item in rows),
        "all_tower_protocol_pending": all(bool(item["tower_protocol_pending"]) for item in rows),
        "all_preview_only": all(bool(item["payload_preview_only"]) for item in rows),
        "no_raw_file_bytes": all(not bool(item["raw_file_bytes_included"]) for item in rows),
        "no_raw_paths": all(not bool(item["raw_path_included"]) for item in rows),
        "no_public_links": all(not bool(item["public_link_included"]) for item in rows),
    }


def get_teller_to_tower_handoff_safety_blocker_board() -> Dict[str, Any]:
    initialize_teller_to_tower_request_handoff_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM teller_to_tower_handoff_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 459,
        "title": "Teller-to-Tower Handoff Safety Blocker Board",
        "ready": True,
        "blocker_count": len(rows),
        "blockers": rows,
        "unsafe_action_count": sum(1 for item in rows if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in rows),
    }


def get_teller_to_tower_request_handoff_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_teller_to_tower_request_handoff_layer()

    shell = get_teller_to_tower_request_handoff_shell()
    packets = get_workflow_request_packet_contract()
    roles = get_requester_role_context_board()
    scopes = get_document_proof_type_scope_board()
    classifiers = get_sensitivity_redaction_need_classifier()
    approvals = get_tower_approval_required_flag_builder()
    receipts = get_teller_workflow_receipt_draft_ledger()
    intake = get_tower_intake_payload_preview_board()
    blockers = get_teller_to_tower_handoff_safety_blocker_board()

    checks = {
        "previous_headless_tower_status_bridge_ready": init["previous_headless_tower_status_bridge_ready"] is True,
        "handoff_shell_ready": shell["ready"] is True,
        "doctrine_tower_teller_vault_locked": DOCTRINE["tower"] == "face_protocol_authority" and DOCTRINE["teller"] == "workflow_request_source" and DOCTRINE["vault"] == "sealed_memory",
        "correct_flow_locked": DOCTRINE["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller",
        "teller_cannot_call_vault_directly": DOCTRINE["teller_can_call_vault_directly"] is False,
        "tower_must_authorize_protocol": DOCTRINE["tower_must_authorize_protocol"] is True,
        "vault_answers_tower_only": DOCTRINE["vault_answers_tower_only"] is True,
        "workflow_packets_ready": packets["ready"] is True and packets["packet_count"] >= 2,
        "packets_addressed_to_tower_only": packets["all_addressed_to_tower"] is True and packets["no_vault_direct_request"] is True,
        "packets_require_tower_approval": packets["all_tower_approval_required"] is True,
        "requester_roles_ready": roles["ready"] is True and roles["role_context_count"] >= 2,
        "roles_require_tower_checks": roles["all_tower_identity_check_required"] is True and roles["all_tower_permission_check_required"] is True,
        "roles_no_teller_self_or_vault_direct_approval": roles["no_teller_self_approval"] is True and roles["no_vault_direct_approval"] is True,
        "document_scope_ready": scopes["ready"] is True and scopes["scope_count"] >= 2,
        "scope_requires_tower_protocol": scopes["all_tower_protocol_required"] is True,
        "scope_no_vault_direct_raw_public": scopes["no_vault_direct_access"] is True and scopes["no_raw_file_bytes_allowed"] is True and scopes["no_public_links_allowed"] is True,
        "redaction_classifier_ready": classifiers["ready"] is True and classifiers["classifier_count"] >= 2,
        "redaction_blocks_raw_path_url_token_public_direct": classifiers["all_redaction_required"] is True and classifiers["all_raw_file_bytes_redacted"] is True and classifiers["all_raw_paths_redacted"] is True and classifiers["all_raw_file_urls_redacted"] is True and classifiers["all_raw_tokens_redacted"] is True and classifiers["all_public_links_redacted"] is True and classifiers["all_direct_browse_redacted"] is True,
        "tower_approval_flags_ready": approvals["ready"] is True and approvals["approval_flag_count"] >= 2,
        "tower_approval_gate_required": approvals["all_tower_approval_required"] is True and approvals["all_tower_permission_required"] is True and approvals["all_tower_protocol_gate_required"] is True,
        "approval_no_teller_to_vault_direct_call": approvals["no_teller_to_vault_direct_call"] is True,
        "teller_receipt_drafts_ready": receipts["ready"] is True and receipts["receipt_draft_count"] >= 2,
        "receipts_draft_append_only_with_tower_and_vault_receipts": receipts["all_receipts_draft"] is True and receipts["all_tower_receipts_required"] is True and receipts["all_vault_service_receipts_required"] is True and receipts["all_append_only"] is True and receipts["all_immutable"] is True,
        "tower_intake_previews_ready": intake["ready"] is True and intake["intake_preview_count"] >= 2,
        "intake_addressed_to_tower_and_protocol_pending": intake["all_addressed_to_tower"] is True and intake["all_tower_intake_ready"] is True and intake["all_vault_request_not_ready_yet"] is True and intake["all_tower_protocol_pending"] is True,
        "intake_preview_only_no_raw_path_public": intake["all_preview_only"] is True and intake["no_raw_file_bytes"] is True and intake["no_raw_paths"] is True and intake["no_public_links"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "global_no_teller_to_vault": LOCKS["teller_to_vault_direct_call_allowed"] is False and LOCKS["vault_direct_request_from_teller_allowed"] is False,
        "global_no_protocol_execution_yet": LOCKS["view_protocol_execution_allowed"] is False and LOCKS["download_protocol_execution_allowed"] is False and LOCKS["proof_protocol_execution_allowed"] is False,
        "global_no_public_dashboard_portal_browse": LOCKS["public_vault_dashboard_allowed"] is False and LOCKS["direct_vault_user_portal_allowed"] is False and LOCKS["employee_vault_browsing_allowed"] is False and LOCKS["external_collaborator_browsing_allowed"] is False,
        "global_no_public_links_raw_bytes_paths_tokens": LOCKS["public_url_created"] is False and LOCKS["share_link_created"] is False and LOCKS["raw_file_bytes_returned_by_json"] is False and LOCKS["raw_path_exposed"] is False and LOCKS["raw_file_url_exposed"] is False and LOCKS["raw_download_token_exposed"] is False,
        "global_no_provider_delete_restore_move": LOCKS["provider_storage_required"] is False and LOCKS["hard_delete_allowed"] is False and LOCKS["purge_allowed"] is False and LOCKS["restore_execution_allowed"] is False and LOCKS["physical_object_move_allowed"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 460,
        "title": "Teller-to-Tower Request Handoff Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Teller-to-Tower request handoff layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — TOWER VAULT REQUEST PROTOCOL GATE LAYER / GP461-GP470",
        "still_locked": [
            "no Teller-to-Vault direct calls",
            "no direct Vault user portal",
            "no employee/vendor/customer Vault browsing",
            "no public Vault dashboard",
            "no standalone external Vault dashboard",
            "no external collaborator browsing",
            "no public URL or share link",
            "no raw file bytes returned by JSON",
            "no raw path or raw file URL exposure",
            "no raw token exposure",
            "no view/download/proof protocol execution in this layer",
            "no public/beta/provider upload",
            "no delete or purge",
            "no restore execution",
            "no quarantine release",
            "no physical object move",
            "no provider dependency by default",
        ],
    }


def get_teller_to_tower_request_handoff_home() -> Dict[str, Any]:
    checkpoint = get_teller_to_tower_request_handoff_readiness_checkpoint()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "doctrine": DOCTRINE,
        "packs": PACKS,
        "locks": LOCKS,
        "checkpoint": checkpoint,
    }


def validate_teller_to_tower_request_handoff_layer() -> Dict[str, Any]:
    checkpoint = get_teller_to_tower_request_handoff_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_headless_tower_status_bridge_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"]["teller_cannot_call_vault_directly"] is True
    assert checkpoint["checks"]["tower_must_authorize_protocol"] is True
    assert checkpoint["checks"]["vault_answers_tower_only"] is True
    assert checkpoint["checks"]["workflow_packets_ready"] is True
    assert checkpoint["checks"]["packets_addressed_to_tower_only"] is True
    assert checkpoint["checks"]["packets_require_tower_approval"] is True
    assert checkpoint["checks"]["requester_roles_ready"] is True
    assert checkpoint["checks"]["roles_require_tower_checks"] is True
    assert checkpoint["checks"]["roles_no_teller_self_or_vault_direct_approval"] is True
    assert checkpoint["checks"]["document_scope_ready"] is True
    assert checkpoint["checks"]["scope_requires_tower_protocol"] is True
    assert checkpoint["checks"]["scope_no_vault_direct_raw_public"] is True
    assert checkpoint["checks"]["redaction_classifier_ready"] is True
    assert checkpoint["checks"]["redaction_blocks_raw_path_url_token_public_direct"] is True
    assert checkpoint["checks"]["tower_approval_flags_ready"] is True
    assert checkpoint["checks"]["tower_approval_gate_required"] is True
    assert checkpoint["checks"]["approval_no_teller_to_vault_direct_call"] is True
    assert checkpoint["checks"]["teller_receipt_drafts_ready"] is True
    assert checkpoint["checks"]["receipts_draft_append_only_with_tower_and_vault_receipts"] is True
    assert checkpoint["checks"]["tower_intake_previews_ready"] is True
    assert checkpoint["checks"]["intake_addressed_to_tower_and_protocol_pending"] is True
    assert checkpoint["checks"]["intake_preview_only_no_raw_path_public"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["workflow_request_packet_creation_allowed"] is True
    assert LOCKS["tower_addressed_handoff_allowed"] is True
    assert LOCKS["teller_to_vault_direct_call_allowed"] is False
    assert LOCKS["vault_direct_request_from_teller_allowed"] is False
    assert LOCKS["vault_direct_approval_from_teller_allowed"] is False
    assert LOCKS["view_protocol_execution_allowed"] is False
    assert LOCKS["download_protocol_execution_allowed"] is False
    assert LOCKS["proof_protocol_execution_allowed"] is False
    assert LOCKS["public_vault_dashboard_allowed"] is False
    assert LOCKS["direct_vault_user_portal_allowed"] is False
    assert LOCKS["employee_vault_browsing_allowed"] is False
    assert LOCKS["external_collaborator_browsing_allowed"] is False
    assert LOCKS["public_url_created"] is False
    assert LOCKS["share_link_created"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False

    return {
        "ok": True,
        "section": SECTION,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(item for item in PACKS if item["gp"] == gp)
    checkpoint = get_teller_to_tower_request_handoff_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "correct_flow": DOCTRINE["correct_flow"],
        "teller_to_vault_direct_call_allowed": False,
        "tower_protocol_required": True,
        "vault_answers_tower_only": True,
        "locks_preserved": True,
    }


def get_gp451_status() -> Dict[str, Any]:
    return _gp_status(451)


def get_gp452_status() -> Dict[str, Any]:
    return _gp_status(452)


def get_gp453_status() -> Dict[str, Any]:
    return _gp_status(453)


def get_gp454_status() -> Dict[str, Any]:
    return _gp_status(454)


def get_gp455_status() -> Dict[str, Any]:
    return _gp_status(455)


def get_gp456_status() -> Dict[str, Any]:
    return _gp_status(456)


def get_gp457_status() -> Dict[str, Any]:
    return _gp_status(457)


def get_gp458_status() -> Dict[str, Any]:
    return _gp_status(458)


def get_gp459_status() -> Dict[str, Any]:
    return _gp_status(459)


def get_gp460_status() -> Dict[str, Any]:
    return _gp_status(460)
