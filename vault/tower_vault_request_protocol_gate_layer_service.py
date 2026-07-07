
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — TOWER VAULT REQUEST PROTOCOL GATE LAYER / GP461-GP470"
LAYER_ID = "vault_gp461_470_tower_vault_request_protocol_gate_layer"
READINESS_LABEL = "Tower Vault request protocol gate layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_tower_vault_request_protocol_gate_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.teller_to_tower_request_handoff_layer_service import (
        get_workflow_request_packet_contract,
        get_requester_role_context_board,
        get_document_proof_type_scope_board,
        get_sensitivity_redaction_need_classifier,
        get_tower_approval_required_flag_builder,
        get_teller_workflow_receipt_draft_ledger,
        get_tower_intake_payload_preview_board,
        validate_teller_to_tower_request_handoff_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP461-GP470 requires GP451-GP460 Teller-to-Tower request handoff layer first."
    ) from exc


_GP461_INIT_CACHE = None

DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": "Teller -> Tower -> Vault -> Tower -> Teller",
    "tower_owns_protocol_gate": True,
    "teller_can_call_vault_directly": False,
    "vault_answers_tower_only": True,
    "protocol_gate_executes_vault_call": False,
    "protocol_gate_prepares_vault_request_drafts": True,
}

LOCKS = {
    "tower_vault_request_protocol_gate_layer": True,
    "tower_identity_permission_gate_allowed": True,
    "clearance_step_up_approval_gate_allowed": True,
    "protocol_type_decision_allowed": True,
    "redaction_scope_enforcement_allowed": True,
    "tower_authorized_vault_request_drafts_allowed": True,
    "tower_protocol_receipt_drafts_allowed": True,
    "vault_call_pending_queue_preview_allowed": True,

    "actual_vault_call_execution_allowed": False,
    "vault_call_sent": False,
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
    {"gp": 461, "title": "Tower Vault Request Protocol Gate Shell", "status": "ready", "route": "/vault/tower-vault-request-protocol-gate-shell.json"},
    {"gp": 462, "title": "Tower Identity Permission Gate Board", "status": "ready", "route": "/vault/tower-identity-permission-gate-board.json"},
    {"gp": 463, "title": "Clearance Step-Up Approval Gate Board", "status": "ready", "route": "/vault/clearance-step-up-approval-gate-board.json"},
    {"gp": 464, "title": "Protocol Type Decision Board", "status": "ready", "route": "/vault/protocol-type-decision-board.json"},
    {"gp": 465, "title": "Redaction Scope Enforcement Board", "status": "ready", "route": "/vault/redaction-scope-enforcement-board.json"},
    {"gp": 466, "title": "Tower Authorized Vault Request Draft Builder", "status": "ready", "route": "/vault/tower-authorized-vault-request-draft-builder.json"},
    {"gp": 467, "title": "Tower Protocol Receipt Draft Ledger", "status": "ready", "route": "/vault/tower-protocol-receipt-draft-ledger.json"},
    {"gp": 468, "title": "Vault Call Pending Queue Preview Board", "status": "ready", "route": "/vault/vault-call-pending-queue-preview-board.json"},
    {"gp": 469, "title": "Tower Protocol Gate Safety Blocker Board", "status": "ready", "route": "/vault/tower-protocol-gate-safety-blocker-board.json"},
    {"gp": 470, "title": "Tower Vault Request Protocol Gate Readiness Checkpoint", "status": "ready", "route": "/vault/tower-vault-request-protocol-gate-readiness-checkpoint.json"},
]

BLOCKERS = [
    {"blocker_id": "no_actual_vault_call_execution", "blocked_action": "actual_vault_call_execution", "allowed": False, "reason": "This layer only prepares Tower protocol gate metadata and pending Vault request drafts."},
    {"blocker_id": "no_teller_to_vault_direct_call", "blocked_action": "teller_to_vault_direct_call", "allowed": False, "reason": "Teller requests must go to Tower first."},
    {"blocker_id": "no_teller_vault_download", "blocked_action": "teller_direct_download_from_vault", "allowed": False, "reason": "Tower owns download protocol."},
    {"blocker_id": "no_teller_vault_view", "blocked_action": "teller_direct_view_from_vault", "allowed": False, "reason": "Tower owns view protocol."},
    {"blocker_id": "no_teller_vault_proof_call", "blocked_action": "teller_direct_proof_call_to_vault", "allowed": False, "reason": "Tower owns proof protocol."},
    {"blocker_id": "no_public_vault_dashboard", "blocked_action": "public_vault_dashboard", "allowed": False, "reason": "Tower is the face; Vault remains headless."},
    {"blocker_id": "no_direct_vault_user_portal", "blocked_action": "direct_vault_user_portal", "allowed": False, "reason": "People do not enter Vault directly."},
    {"blocker_id": "no_employee_vendor_customer_browse", "blocked_action": "employee_vendor_customer_vault_browsing", "allowed": False, "reason": "Teller handles workflows, not Vault browsing."},
    {"blocker_id": "no_external_collaborator_browse", "blocked_action": "external_collaborator_browsing", "allowed": False, "reason": "No shared-drive behavior."},
    {"blocker_id": "no_public_links", "blocked_action": "public_links_or_raw_urls", "allowed": False, "reason": "Protocol drafts never include public links or raw URLs."},
    {"blocker_id": "no_raw_file_bytes_json", "blocked_action": "raw_file_bytes_json", "allowed": False, "reason": "Protocol gate outputs are metadata only."},
    {"blocker_id": "no_raw_paths_or_tokens", "blocked_action": "raw_path_or_token_exposure", "allowed": False, "reason": "Protocol gate never exposes paths or tokens."},
    {"blocker_id": "no_protocol_execution", "blocked_action": "view_download_proof_protocol_execution", "allowed": False, "reason": "Protocol execution comes in later Tower authorized protocol layers."},
    {"blocker_id": "no_provider_dependency", "blocked_action": "provider_dependency", "allowed": False, "reason": "Local-first sealed memory remains default."},
    {"blocker_id": "no_delete_restore_move", "blocked_action": "delete_restore_physical_move", "allowed": False, "reason": "Protocol gate does not mutate Vault lifecycle state or move objects."},
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


def _identity_gate_id(request_id: str) -> str:
    return "tower_identity_permission_gate_" + calculate_sha256_bytes(("identity_gate|" + request_id).encode("utf-8"))[:24]


def _clearance_gate_id(request_id: str) -> str:
    return "clearance_step_up_gate_" + calculate_sha256_bytes(("clearance_gate|" + request_id).encode("utf-8"))[:24]


def _protocol_decision_id(request_id: str) -> str:
    return "protocol_type_decision_" + calculate_sha256_bytes(("protocol_decision|" + request_id).encode("utf-8"))[:24]


def _redaction_scope_id(request_id: str) -> str:
    return "redaction_scope_enforcement_" + calculate_sha256_bytes(("redaction_scope|" + request_id).encode("utf-8"))[:24]


def _vault_request_draft_id(request_id: str) -> str:
    return "tower_authorized_vault_request_draft_" + calculate_sha256_bytes(("vault_request_draft|" + request_id).encode("utf-8"))[:24]


def _tower_protocol_receipt_draft_id(request_id: str) -> str:
    return "tower_protocol_receipt_draft_" + calculate_sha256_bytes(("tower_protocol_receipt|" + request_id).encode("utf-8"))[:24]


def _pending_queue_id(request_id: str) -> str:
    return "vault_call_pending_queue_preview_" + calculate_sha256_bytes(("vault_call_pending|" + request_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    packets = get_workflow_request_packet_contract().get("request_packets", [])
    roles = get_requester_role_context_board().get("role_contexts", [])
    scopes = get_document_proof_type_scope_board().get("scopes", [])
    classifiers = get_sensitivity_redaction_need_classifier().get("classifiers", [])
    approvals = get_tower_approval_required_flag_builder().get("approval_flags", [])
    receipts = get_teller_workflow_receipt_draft_ledger().get("receipt_drafts", [])
    intake = get_tower_intake_payload_preview_board().get("intake_previews", [])

    role_by_request = {row["request_id"]: row for row in roles}
    scope_by_request = {row["request_id"]: row for row in scopes}
    classifier_by_request = {row["request_id"]: row for row in classifiers}
    approval_by_request = {row["request_id"]: row for row in approvals}
    receipt_by_request = {row["request_id"]: row for row in receipts}
    intake_by_request = {row["request_id"]: row for row in intake}

    rows = []
    for packet in packets:
        request_id = packet["request_id"]
        role = role_by_request.get(request_id, {})
        scope = scope_by_request.get(request_id, {})
        classifier = classifier_by_request.get(request_id, {})
        approval = approval_by_request.get(request_id, {})
        receipt = receipt_by_request.get(request_id, {})
        intake_row = intake_by_request.get(request_id, {})
        rows.append(
            {
                "request_id": request_id,
                "active_file_id": packet["active_file_id"],
                "rebuild_candidate_id": packet["rebuild_candidate_id"],
                "workflow_type": packet["workflow_type"],
                "requester_role": packet["requester_role"],
                "requester_entity": packet["requester_entity"],
                "document_or_proof_type": packet["document_or_proof_type"],
                "requested_output_type": packet["requested_output_type"],
                "addressed_to": packet["addressed_to"],
                "vault_direct_request_allowed": bool(packet["vault_direct_request_allowed"]),
                "tower_approval_required": bool(packet["tower_approval_required"]),
                "packet_hash": packet["packet_hash"],
                "tower_identity_check_required": bool(role.get("tower_identity_check_required", 1)),
                "tower_permission_check_required": bool(role.get("tower_permission_check_required", 1)),
                "teller_can_self_approve": bool(role.get("teller_can_self_approve", 0)),
                "vault_direct_approval_allowed": bool(role.get("vault_direct_approval_allowed", 0)),
                "tower_protocol_required": scope.get("tower_protocol_required", "status_protocol"),
                "vault_direct_access_allowed": bool(scope.get("vault_direct_access_allowed", 0)),
                "raw_file_bytes_allowed": bool(scope.get("raw_file_bytes_allowed", 0)),
                "public_link_allowed": bool(scope.get("public_link_allowed", 0)),
                "sensitivity_level": classifier.get("sensitivity_level", "restricted"),
                "redaction_required": bool(classifier.get("redaction_required", 1)),
                "step_up_required": bool(classifier.get("step_up_required", 0)),
                "owner_admin_required": bool(classifier.get("owner_admin_required", 0)),
                "raw_file_bytes_redacted": bool(classifier.get("raw_file_bytes_redacted", 1)),
                "raw_path_redacted": bool(classifier.get("raw_path_redacted", 1)),
                "raw_file_url_redacted": bool(classifier.get("raw_file_url_redacted", 1)),
                "raw_token_redacted": bool(classifier.get("raw_token_redacted", 1)),
                "public_link_redacted": bool(classifier.get("public_link_redacted", 1)),
                "direct_browse_redacted": bool(classifier.get("direct_browse_redacted", 1)),
                "tower_protocol_gate_required": bool(approval.get("tower_protocol_gate_required", 1)),
                "teller_to_vault_direct_call_allowed": bool(approval.get("teller_to_vault_direct_call_allowed", 0)),
                "teller_receipt_draft_id": receipt.get("receipt_draft_id", "missing_teller_receipt_draft"),
                "teller_receipt_hash": receipt.get("receipt_hash", "missing_teller_receipt_hash"),
                "tower_receipt_required": bool(receipt.get("tower_receipt_required", 1)),
                "vault_service_receipt_required": bool(receipt.get("vault_service_receipt_required", 1)),
                "tower_intake_ready": bool(intake_row.get("tower_intake_ready", 1)),
                "vault_request_ready": bool(intake_row.get("vault_request_ready", 0)),
                "tower_protocol_pending": bool(intake_row.get("tower_protocol_pending", 1)),
                "intake_payload_hash": intake_row.get("intake_payload_hash", "missing_intake_payload_hash"),
            }
        )
    return rows


def initialize_tower_vault_request_protocol_gate_layer() -> Dict[str, Any]:
    global _GP461_INIT_CACHE
    if _GP461_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP461_INIT_CACHE)

    previous = validate_teller_to_tower_request_handoff_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_identity_permission_gates (
                identity_gate_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                requester_role TEXT NOT NULL,
                requester_entity TEXT NOT NULL,
                gate_state TEXT NOT NULL,
                tower_identity_check_required INTEGER NOT NULL,
                tower_permission_check_required INTEGER NOT NULL,
                teller_self_approval_allowed INTEGER NOT NULL,
                vault_direct_approval_allowed INTEGER NOT NULL,
                gate_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clearance_step_up_approval_gates (
                clearance_gate_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                sensitivity_level TEXT NOT NULL,
                gate_state TEXT NOT NULL,
                clearance_required INTEGER NOT NULL,
                step_up_required INTEGER NOT NULL,
                owner_admin_required INTEGER NOT NULL,
                tower_approval_required INTEGER NOT NULL,
                vault_direct_approval_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS protocol_type_decisions (
                protocol_decision_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                requested_output_type TEXT NOT NULL,
                selected_protocol TEXT NOT NULL,
                decision_state TEXT NOT NULL,
                tower_protocol_gate_required INTEGER NOT NULL,
                protocol_execution_allowed INTEGER NOT NULL,
                teller_direct_protocol_allowed INTEGER NOT NULL,
                vault_answers_tower_only INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS redaction_scope_enforcements (
                redaction_scope_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                sensitivity_level TEXT NOT NULL,
                redaction_state TEXT NOT NULL,
                redaction_required INTEGER NOT NULL,
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
            CREATE TABLE IF NOT EXISTS tower_authorized_vault_request_drafts (
                vault_request_draft_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                selected_protocol TEXT NOT NULL,
                draft_state TEXT NOT NULL,
                addressed_to TEXT NOT NULL,
                originating_service TEXT NOT NULL,
                tower_is_requester INTEGER NOT NULL,
                teller_is_requester INTEGER NOT NULL,
                vault_call_ready INTEGER NOT NULL,
                vault_call_sent INTEGER NOT NULL,
                protocol_execution_allowed INTEGER NOT NULL,
                raw_file_bytes_requested INTEGER NOT NULL,
                raw_path_requested INTEGER NOT NULL,
                public_link_requested INTEGER NOT NULL,
                request_draft_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_protocol_receipt_drafts (
                tower_protocol_receipt_draft_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                vault_request_draft_id TEXT NOT NULL,
                receipt_state TEXT NOT NULL,
                teller_receipt_hash TEXT NOT NULL,
                tower_protocol_receipt_hash TEXT NOT NULL,
                vault_service_receipt_required INTEGER NOT NULL,
                receipt_finalized INTEGER NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_call_pending_queue_previews (
                pending_queue_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                vault_request_draft_id TEXT NOT NULL,
                queue_state TEXT NOT NULL,
                tower_protocol_pending INTEGER NOT NULL,
                vault_call_pending INTEGER NOT NULL,
                vault_call_sent INTEGER NOT NULL,
                vault_response_received INTEGER NOT NULL,
                preview_only INTEGER NOT NULL,
                raw_file_bytes_included INTEGER NOT NULL,
                raw_path_included INTEGER NOT NULL,
                public_link_included INTEGER NOT NULL,
                pending_queue_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_protocol_gate_safety_blockers (
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
                INSERT OR REPLACE INTO tower_protocol_gate_safety_blockers (
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
            request_id = row["request_id"]
            identity_gate_id = _identity_gate_id(request_id)
            clearance_gate_id = _clearance_gate_id(request_id)
            protocol_decision_id = _protocol_decision_id(request_id)
            redaction_scope_id = _redaction_scope_id(request_id)
            vault_request_draft_id = _vault_request_draft_id(request_id)
            tower_protocol_receipt_draft_id = _tower_protocol_receipt_draft_id(request_id)
            pending_queue_id = _pending_queue_id(request_id)

            selected_protocol = row["tower_protocol_required"]

            identity_material = {
                "request_id": request_id,
                "requester_role": row["requester_role"],
                "tower_identity_check_required": True,
                "tower_permission_check_required": True,
                "teller_self_approval_allowed": False,
                "vault_direct_approval_allowed": False,
            }
            gate_hash = calculate_sha256_bytes(repr(sorted(identity_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_identity_permission_gates (
                    identity_gate_id, request_id, workflow_type,
                    requester_role, requester_entity, gate_state,
                    tower_identity_check_required,
                    tower_permission_check_required,
                    teller_self_approval_allowed,
                    vault_direct_approval_allowed,
                    gate_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identity_gate_id,
                    request_id,
                    row["workflow_type"],
                    row["requester_role"],
                    row["requester_entity"],
                    "tower_identity_permission_gate_required",
                    1,
                    1,
                    0,
                    0,
                    gate_hash,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO clearance_step_up_approval_gates (
                    clearance_gate_id, request_id, sensitivity_level,
                    gate_state, clearance_required, step_up_required,
                    owner_admin_required, tower_approval_required,
                    vault_direct_approval_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    clearance_gate_id,
                    request_id,
                    row["sensitivity_level"],
                    "clearance_step_up_owner_approval_gate_required",
                    1,
                    1 if row["sensitivity_level"] in {"confidential", "high"} else 0,
                    1 if row["sensitivity_level"] in {"confidential", "high"} else 0,
                    1,
                    0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO protocol_type_decisions (
                    protocol_decision_id, request_id,
                    requested_output_type, selected_protocol,
                    decision_state, tower_protocol_gate_required,
                    protocol_execution_allowed,
                    teller_direct_protocol_allowed,
                    vault_answers_tower_only, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    protocol_decision_id,
                    request_id,
                    row["requested_output_type"],
                    selected_protocol,
                    "protocol_type_selected_pending_tower_authorization",
                    1,
                    0,
                    0,
                    1,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO redaction_scope_enforcements (
                    redaction_scope_id, request_id, sensitivity_level,
                    redaction_state, redaction_required,
                    raw_file_bytes_redacted, raw_path_redacted,
                    raw_file_url_redacted, raw_token_redacted,
                    public_link_redacted, direct_browse_redacted,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    redaction_scope_id,
                    request_id,
                    row["sensitivity_level"],
                    "redaction_scope_enforced_for_tower_protocol",
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    now,
                ),
            )

            request_draft_material = {
                "request_id": request_id,
                "workflow_type": row["workflow_type"],
                "selected_protocol": selected_protocol,
                "addressed_to": "Vault",
                "originating_service": "Tower",
                "tower_is_requester": True,
                "teller_is_requester": False,
                "vault_call_ready": False,
                "vault_call_sent": False,
                "protocol_execution_allowed": False,
                "raw_file_bytes_requested": False,
                "raw_path_requested": False,
                "public_link_requested": False,
            }
            request_draft_hash = calculate_sha256_bytes(repr(sorted(request_draft_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_authorized_vault_request_drafts (
                    vault_request_draft_id, request_id, workflow_type,
                    selected_protocol, draft_state, addressed_to,
                    originating_service, tower_is_requester,
                    teller_is_requester, vault_call_ready,
                    vault_call_sent, protocol_execution_allowed,
                    raw_file_bytes_requested, raw_path_requested,
                    public_link_requested, request_draft_hash,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    vault_request_draft_id,
                    request_id,
                    row["workflow_type"],
                    selected_protocol,
                    "tower_authorized_vault_request_draft_pending_protocol_execution",
                    "Vault",
                    "Tower",
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    request_draft_hash,
                    now,
                ),
            )

            tower_protocol_receipt_hash = calculate_sha256_bytes(
                f"tower-protocol-receipt-draft|{request_id}|{vault_request_draft_id}|{request_draft_hash}|pending".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_protocol_receipt_drafts (
                    tower_protocol_receipt_draft_id, request_id,
                    vault_request_draft_id, receipt_state,
                    teller_receipt_hash, tower_protocol_receipt_hash,
                    vault_service_receipt_required, receipt_finalized,
                    append_only, mutable, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tower_protocol_receipt_draft_id,
                    request_id,
                    vault_request_draft_id,
                    "tower_protocol_receipt_draft_ready_pending_vault_call",
                    row["teller_receipt_hash"],
                    tower_protocol_receipt_hash,
                    1,
                    0,
                    1,
                    0,
                    now,
                ),
            )

            pending_material = {
                "request_id": request_id,
                "vault_request_draft_id": vault_request_draft_id,
                "tower_protocol_pending": True,
                "vault_call_pending": True,
                "vault_call_sent": False,
                "vault_response_received": False,
                "preview_only": True,
                "raw_file_bytes_included": False,
                "raw_path_included": False,
                "public_link_included": False,
            }
            pending_queue_hash = calculate_sha256_bytes(repr(sorted(pending_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO vault_call_pending_queue_previews (
                    pending_queue_id, request_id, vault_request_draft_id,
                    queue_state, tower_protocol_pending,
                    vault_call_pending, vault_call_sent,
                    vault_response_received, preview_only,
                    raw_file_bytes_included, raw_path_included,
                    public_link_included, pending_queue_hash,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pending_queue_id,
                    request_id,
                    vault_request_draft_id,
                    "vault_call_pending_queue_preview_ready_not_sent",
                    1,
                    1,
                    0,
                    0,
                    1,
                    0,
                    0,
                    0,
                    pending_queue_hash,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_teller_to_tower_handoff_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP461_INIT_CACHE = dict(result)
    return result


def get_tower_vault_request_protocol_gate_shell() -> Dict[str, Any]:
    init = initialize_tower_vault_request_protocol_gate_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 461,
        "title": "Tower Vault Request Protocol Gate Shell",
        "ready": True,
        "initialized": init,
        "doctrine": DOCTRINE,
        "correct_flow": DOCTRINE["correct_flow"],
        "tower_owns_protocol_gate": True,
        "teller_direct_vault_call_allowed": False,
        "vault_call_execution_allowed": False,
        "locks": LOCKS,
    }


def get_tower_identity_permission_gate_board() -> Dict[str, Any]:
    initialize_tower_vault_request_protocol_gate_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_identity_permission_gates ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 462,
        "title": "Tower Identity Permission Gate Board",
        "ready": True,
        "identity_gate_count": len(rows),
        "identity_permission_gates": rows,
        "all_tower_identity_check_required": all(bool(item["tower_identity_check_required"]) for item in rows),
        "all_tower_permission_check_required": all(bool(item["tower_permission_check_required"]) for item in rows),
        "no_teller_self_approval": all(not bool(item["teller_self_approval_allowed"]) for item in rows),
        "no_vault_direct_approval": all(not bool(item["vault_direct_approval_allowed"]) for item in rows),
    }


def get_clearance_step_up_approval_gate_board() -> Dict[str, Any]:
    initialize_tower_vault_request_protocol_gate_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM clearance_step_up_approval_gates ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 463,
        "title": "Clearance Step-Up Approval Gate Board",
        "ready": True,
        "clearance_gate_count": len(rows),
        "clearance_gates": rows,
        "all_clearance_required": all(bool(item["clearance_required"]) for item in rows),
        "all_tower_approval_required": all(bool(item["tower_approval_required"]) for item in rows),
        "no_vault_direct_approval": all(not bool(item["vault_direct_approval_allowed"]) for item in rows),
        "sensitive_request_count": sum(1 for item in rows if item["sensitivity_level"] in {"confidential", "high"}),
        "all_sensitive_have_step_up_and_owner_admin": all(
            bool(item["step_up_required"]) and bool(item["owner_admin_required"])
            for item in rows
            if item["sensitivity_level"] in {"confidential", "high"}
        ),
    }


def get_protocol_type_decision_board() -> Dict[str, Any]:
    initialize_tower_vault_request_protocol_gate_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM protocol_type_decisions ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 464,
        "title": "Protocol Type Decision Board",
        "ready": True,
        "protocol_decision_count": len(rows),
        "protocol_decisions": rows,
        "all_tower_protocol_gate_required": all(bool(item["tower_protocol_gate_required"]) for item in rows),
        "no_protocol_execution_yet": all(not bool(item["protocol_execution_allowed"]) for item in rows),
        "no_teller_direct_protocol": all(not bool(item["teller_direct_protocol_allowed"]) for item in rows),
        "vault_answers_tower_only": all(bool(item["vault_answers_tower_only"]) for item in rows),
    }


def get_redaction_scope_enforcement_board() -> Dict[str, Any]:
    initialize_tower_vault_request_protocol_gate_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM redaction_scope_enforcements ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 465,
        "title": "Redaction Scope Enforcement Board",
        "ready": True,
        "redaction_scope_count": len(rows),
        "redaction_scopes": rows,
        "all_redaction_required": all(bool(item["redaction_required"]) for item in rows),
        "all_raw_file_bytes_redacted": all(bool(item["raw_file_bytes_redacted"]) for item in rows),
        "all_raw_paths_redacted": all(bool(item["raw_path_redacted"]) for item in rows),
        "all_raw_file_urls_redacted": all(bool(item["raw_file_url_redacted"]) for item in rows),
        "all_raw_tokens_redacted": all(bool(item["raw_token_redacted"]) for item in rows),
        "all_public_links_redacted": all(bool(item["public_link_redacted"]) for item in rows),
        "all_direct_browse_redacted": all(bool(item["direct_browse_redacted"]) for item in rows),
    }


def get_tower_authorized_vault_request_draft_builder() -> Dict[str, Any]:
    initialize_tower_vault_request_protocol_gate_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_authorized_vault_request_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 466,
        "title": "Tower Authorized Vault Request Draft Builder",
        "ready": True,
        "vault_request_draft_count": len(rows),
        "vault_request_drafts": rows,
        "all_addressed_to_vault": all(item["addressed_to"] == "Vault" for item in rows),
        "all_originating_from_tower": all(item["originating_service"] == "Tower" for item in rows),
        "all_tower_is_requester": all(bool(item["tower_is_requester"]) for item in rows),
        "no_teller_is_requester": all(not bool(item["teller_is_requester"]) for item in rows),
        "all_vault_calls_not_ready_yet": all(not bool(item["vault_call_ready"]) for item in rows),
        "no_vault_calls_sent": all(not bool(item["vault_call_sent"]) for item in rows),
        "no_protocol_execution_yet": all(not bool(item["protocol_execution_allowed"]) for item in rows),
        "no_raw_file_bytes_requested": all(not bool(item["raw_file_bytes_requested"]) for item in rows),
        "no_raw_paths_requested": all(not bool(item["raw_path_requested"]) for item in rows),
        "no_public_links_requested": all(not bool(item["public_link_requested"]) for item in rows),
    }


def get_tower_protocol_receipt_draft_ledger() -> Dict[str, Any]:
    initialize_tower_vault_request_protocol_gate_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_protocol_receipt_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 467,
        "title": "Tower Protocol Receipt Draft Ledger",
        "ready": True,
        "protocol_receipt_draft_count": len(rows),
        "protocol_receipt_drafts": rows,
        "all_vault_service_receipts_required": all(bool(item["vault_service_receipt_required"]) for item in rows),
        "all_receipts_draft": all(not bool(item["receipt_finalized"]) for item in rows),
        "all_append_only": all(bool(item["append_only"]) for item in rows),
        "all_immutable": all(not bool(item["mutable"]) for item in rows),
    }


def get_vault_call_pending_queue_preview_board() -> Dict[str, Any]:
    initialize_tower_vault_request_protocol_gate_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM vault_call_pending_queue_previews ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 468,
        "title": "Vault Call Pending Queue Preview Board",
        "ready": True,
        "pending_queue_count": len(rows),
        "pending_queue_previews": rows,
        "all_tower_protocol_pending": all(bool(item["tower_protocol_pending"]) for item in rows),
        "all_vault_call_pending": all(bool(item["vault_call_pending"]) for item in rows),
        "no_vault_calls_sent": all(not bool(item["vault_call_sent"]) for item in rows),
        "no_vault_response_received": all(not bool(item["vault_response_received"]) for item in rows),
        "all_preview_only": all(bool(item["preview_only"]) for item in rows),
        "no_raw_file_bytes": all(not bool(item["raw_file_bytes_included"]) for item in rows),
        "no_raw_paths": all(not bool(item["raw_path_included"]) for item in rows),
        "no_public_links": all(not bool(item["public_link_included"]) for item in rows),
    }


def get_tower_protocol_gate_safety_blocker_board() -> Dict[str, Any]:
    initialize_tower_vault_request_protocol_gate_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_protocol_gate_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 469,
        "title": "Tower Protocol Gate Safety Blocker Board",
        "ready": True,
        "blocker_count": len(rows),
        "blockers": rows,
        "unsafe_action_count": sum(1 for item in rows if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in rows),
    }


def get_tower_vault_request_protocol_gate_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_tower_vault_request_protocol_gate_layer()

    shell = get_tower_vault_request_protocol_gate_shell()
    identity = get_tower_identity_permission_gate_board()
    clearance = get_clearance_step_up_approval_gate_board()
    protocol = get_protocol_type_decision_board()
    redaction = get_redaction_scope_enforcement_board()
    request_drafts = get_tower_authorized_vault_request_draft_builder()
    receipts = get_tower_protocol_receipt_draft_ledger()
    queue = get_vault_call_pending_queue_preview_board()
    blockers = get_tower_protocol_gate_safety_blocker_board()

    checks = {
        "previous_teller_to_tower_handoff_ready": init["previous_teller_to_tower_handoff_ready"] is True,
        "protocol_gate_shell_ready": shell["ready"] is True,
        "doctrine_tower_teller_vault_locked": DOCTRINE["tower"] == "face_protocol_authority" and DOCTRINE["teller"] == "workflow_request_source" and DOCTRINE["vault"] == "sealed_memory",
        "correct_flow_locked": DOCTRINE["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller",
        "tower_owns_protocol_gate": DOCTRINE["tower_owns_protocol_gate"] is True,
        "teller_cannot_call_vault_directly": DOCTRINE["teller_can_call_vault_directly"] is False,
        "vault_answers_tower_only": DOCTRINE["vault_answers_tower_only"] is True,
        "protocol_gate_does_not_execute_vault_call": DOCTRINE["protocol_gate_executes_vault_call"] is False,
        "identity_permission_gates_ready": identity["ready"] is True and identity["identity_gate_count"] >= 2,
        "identity_permission_require_tower_checks": identity["all_tower_identity_check_required"] is True and identity["all_tower_permission_check_required"] is True,
        "identity_permission_no_teller_self_or_vault_direct_approval": identity["no_teller_self_approval"] is True and identity["no_vault_direct_approval"] is True,
        "clearance_gates_ready": clearance["ready"] is True and clearance["clearance_gate_count"] >= 2,
        "clearance_tower_approval_required": clearance["all_clearance_required"] is True and clearance["all_tower_approval_required"] is True,
        "clearance_no_vault_direct_approval": clearance["no_vault_direct_approval"] is True,
        "protocol_decisions_ready": protocol["ready"] is True and protocol["protocol_decision_count"] >= 2,
        "protocol_decision_tower_gate_no_execution": protocol["all_tower_protocol_gate_required"] is True and protocol["no_protocol_execution_yet"] is True,
        "protocol_decision_no_teller_direct_and_vault_answers_tower": protocol["no_teller_direct_protocol"] is True and protocol["vault_answers_tower_only"] is True,
        "redaction_scopes_ready": redaction["ready"] is True and redaction["redaction_scope_count"] >= 2,
        "redaction_enforces_raw_path_url_token_public_direct_blocks": redaction["all_redaction_required"] is True and redaction["all_raw_file_bytes_redacted"] is True and redaction["all_raw_paths_redacted"] is True and redaction["all_raw_file_urls_redacted"] is True and redaction["all_raw_tokens_redacted"] is True and redaction["all_public_links_redacted"] is True and redaction["all_direct_browse_redacted"] is True,
        "tower_vault_request_drafts_ready": request_drafts["ready"] is True and request_drafts["vault_request_draft_count"] >= 2,
        "drafts_addressed_to_vault_from_tower_only": request_drafts["all_addressed_to_vault"] is True and request_drafts["all_originating_from_tower"] is True and request_drafts["all_tower_is_requester"] is True and request_drafts["no_teller_is_requester"] is True,
        "drafts_no_vault_call_or_protocol_execution_yet": request_drafts["all_vault_calls_not_ready_yet"] is True and request_drafts["no_vault_calls_sent"] is True and request_drafts["no_protocol_execution_yet"] is True,
        "drafts_no_raw_path_public_requested": request_drafts["no_raw_file_bytes_requested"] is True and request_drafts["no_raw_paths_requested"] is True and request_drafts["no_public_links_requested"] is True,
        "protocol_receipts_ready": receipts["ready"] is True and receipts["protocol_receipt_draft_count"] >= 2,
        "protocol_receipts_draft_append_only_immutable": receipts["all_vault_service_receipts_required"] is True and receipts["all_receipts_draft"] is True and receipts["all_append_only"] is True and receipts["all_immutable"] is True,
        "pending_queue_ready": queue["ready"] is True and queue["pending_queue_count"] >= 2,
        "pending_queue_not_sent_or_received": queue["all_tower_protocol_pending"] is True and queue["all_vault_call_pending"] is True and queue["no_vault_calls_sent"] is True and queue["no_vault_response_received"] is True,
        "pending_queue_preview_only_no_raw_path_public": queue["all_preview_only"] is True and queue["no_raw_file_bytes"] is True and queue["no_raw_paths"] is True and queue["no_public_links"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "global_no_actual_vault_call": LOCKS["actual_vault_call_execution_allowed"] is False and LOCKS["vault_call_sent"] is False,
        "global_no_teller_to_vault": LOCKS["teller_to_vault_direct_call_allowed"] is False and LOCKS["vault_direct_request_from_teller_allowed"] is False,
        "global_no_protocol_execution_yet": LOCKS["view_protocol_execution_allowed"] is False and LOCKS["download_protocol_execution_allowed"] is False and LOCKS["proof_protocol_execution_allowed"] is False,
        "global_no_public_dashboard_portal_browse": LOCKS["public_vault_dashboard_allowed"] is False and LOCKS["direct_vault_user_portal_allowed"] is False and LOCKS["employee_vault_browsing_allowed"] is False and LOCKS["external_collaborator_browsing_allowed"] is False,
        "global_no_public_links_raw_bytes_paths_tokens": LOCKS["public_url_created"] is False and LOCKS["share_link_created"] is False and LOCKS["raw_file_bytes_returned_by_json"] is False and LOCKS["raw_path_exposed"] is False and LOCKS["raw_file_url_exposed"] is False and LOCKS["raw_download_token_exposed"] is False,
        "global_no_provider_delete_restore_move": LOCKS["provider_storage_required"] is False and LOCKS["hard_delete_allowed"] is False and LOCKS["purge_allowed"] is False and LOCKS["restore_execution_allowed"] is False and LOCKS["physical_object_move_allowed"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 470,
        "title": "Tower Vault Request Protocol Gate Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Tower Vault request protocol gate layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — TOWER AUTHORIZED VIEW PROTOCOL LAYER / GP471-GP480",
        "still_locked": [
            "no actual Vault call execution in this layer",
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


def get_tower_vault_request_protocol_gate_home() -> Dict[str, Any]:
    checkpoint = get_tower_vault_request_protocol_gate_readiness_checkpoint()
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


def validate_tower_vault_request_protocol_gate_layer() -> Dict[str, Any]:
    checkpoint = get_tower_vault_request_protocol_gate_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_teller_to_tower_handoff_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"]["tower_owns_protocol_gate"] is True
    assert checkpoint["checks"]["teller_cannot_call_vault_directly"] is True
    assert checkpoint["checks"]["vault_answers_tower_only"] is True
    assert checkpoint["checks"]["protocol_gate_does_not_execute_vault_call"] is True
    assert checkpoint["checks"]["identity_permission_gates_ready"] is True
    assert checkpoint["checks"]["identity_permission_require_tower_checks"] is True
    assert checkpoint["checks"]["identity_permission_no_teller_self_or_vault_direct_approval"] is True
    assert checkpoint["checks"]["clearance_gates_ready"] is True
    assert checkpoint["checks"]["clearance_tower_approval_required"] is True
    assert checkpoint["checks"]["clearance_no_vault_direct_approval"] is True
    assert checkpoint["checks"]["protocol_decisions_ready"] is True
    assert checkpoint["checks"]["protocol_decision_tower_gate_no_execution"] is True
    assert checkpoint["checks"]["protocol_decision_no_teller_direct_and_vault_answers_tower"] is True
    assert checkpoint["checks"]["redaction_scopes_ready"] is True
    assert checkpoint["checks"]["redaction_enforces_raw_path_url_token_public_direct_blocks"] is True
    assert checkpoint["checks"]["tower_vault_request_drafts_ready"] is True
    assert checkpoint["checks"]["drafts_addressed_to_vault_from_tower_only"] is True
    assert checkpoint["checks"]["drafts_no_vault_call_or_protocol_execution_yet"] is True
    assert checkpoint["checks"]["drafts_no_raw_path_public_requested"] is True
    assert checkpoint["checks"]["protocol_receipts_ready"] is True
    assert checkpoint["checks"]["protocol_receipts_draft_append_only_immutable"] is True
    assert checkpoint["checks"]["pending_queue_ready"] is True
    assert checkpoint["checks"]["pending_queue_not_sent_or_received"] is True
    assert checkpoint["checks"]["pending_queue_preview_only_no_raw_path_public"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["tower_identity_permission_gate_allowed"] is True
    assert LOCKS["clearance_step_up_approval_gate_allowed"] is True
    assert LOCKS["protocol_type_decision_allowed"] is True
    assert LOCKS["redaction_scope_enforcement_allowed"] is True
    assert LOCKS["tower_authorized_vault_request_drafts_allowed"] is True
    assert LOCKS["tower_protocol_receipt_drafts_allowed"] is True
    assert LOCKS["vault_call_pending_queue_preview_allowed"] is True

    assert LOCKS["actual_vault_call_execution_allowed"] is False
    assert LOCKS["vault_call_sent"] is False
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
    checkpoint = get_tower_vault_request_protocol_gate_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "correct_flow": DOCTRINE["correct_flow"],
        "tower_owns_protocol_gate": True,
        "teller_to_vault_direct_call_allowed": False,
        "actual_vault_call_execution_allowed": False,
        "vault_answers_tower_only": True,
        "locks_preserved": True,
    }


def get_gp461_status() -> Dict[str, Any]:
    return _gp_status(461)


def get_gp462_status() -> Dict[str, Any]:
    return _gp_status(462)


def get_gp463_status() -> Dict[str, Any]:
    return _gp_status(463)


def get_gp464_status() -> Dict[str, Any]:
    return _gp_status(464)


def get_gp465_status() -> Dict[str, Any]:
    return _gp_status(465)


def get_gp466_status() -> Dict[str, Any]:
    return _gp_status(466)


def get_gp467_status() -> Dict[str, Any]:
    return _gp_status(467)


def get_gp468_status() -> Dict[str, Any]:
    return _gp_status(468)


def get_gp469_status() -> Dict[str, Any]:
    return _gp_status(469)


def get_gp470_status() -> Dict[str, Any]:
    return _gp_status(470)
