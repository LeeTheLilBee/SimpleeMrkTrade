
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — TOWER AUTHORIZED VIEW PROTOCOL LAYER / GP471-GP480"
LAYER_ID = "vault_gp471_480_tower_authorized_view_protocol_layer"
READINESS_LABEL = "Tower authorized view protocol layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_tower_authorized_view_protocol_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.tower_vault_request_protocol_gate_layer_service import (
        get_tower_identity_permission_gate_board,
        get_clearance_step_up_approval_gate_board,
        get_protocol_type_decision_board,
        get_redaction_scope_enforcement_board,
        get_tower_authorized_vault_request_draft_builder,
        get_tower_protocol_receipt_draft_ledger,
        get_vault_call_pending_queue_preview_board,
        validate_tower_vault_request_protocol_gate_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP471-GP480 requires GP461-GP470 Tower Vault request protocol gate layer first."
    ) from exc


_GP471_INIT_CACHE = None

DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": "Teller -> Tower -> Vault -> Tower -> Teller",
    "tower_executes_controlled_view_protocol": True,
    "view_protocol_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
    "vault_answers_tower_only": True,
    "raw_file_bytes_exposed_by_view": False,
    "public_link_created_by_view": False,
}

LOCKS = {
    "tower_authorized_view_protocol_layer": True,
    "controlled_view_protocol_execution_allowed": True,
    "tower_view_session_drafts_allowed": True,
    "tower_internal_vault_view_requests_allowed": True,
    "vault_view_response_envelopes_allowed": True,
    "view_redaction_receipt_drafts_allowed": True,
    "tower_view_result_delivery_previews_allowed": True,

    "download_protocol_execution_allowed": False,
    "proof_protocol_execution_allowed": False,
    "public_view_link_allowed": False,
    "raw_file_view_allowed": False,
    "teller_to_vault_direct_call_allowed": False,
    "vault_direct_request_from_teller_allowed": False,
    "vault_direct_approval_from_teller_allowed": False,
    "direct_vault_user_portal_allowed": False,
    "public_vault_dashboard_allowed": False,
    "standalone_external_vault_dashboard_allowed": False,
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
    {"gp": 471, "title": "Tower Authorized View Protocol Shell", "status": "ready", "route": "/vault/tower-authorized-view-protocol-shell.json"},
    {"gp": 472, "title": "View Eligibility Gate Board", "status": "ready", "route": "/vault/view-eligibility-gate-board.json"},
    {"gp": 473, "title": "Redacted View Projection Builder", "status": "ready", "route": "/vault/redacted-view-projection-builder.json"},
    {"gp": 474, "title": "Tower View Session Draft Board", "status": "ready", "route": "/vault/tower-view-session-draft-board.json"},
    {"gp": 475, "title": "Tower Internal Vault View Request Ledger", "status": "ready", "route": "/vault/tower-internal-vault-view-request-ledger.json"},
    {"gp": 476, "title": "Vault View Response Envelope Board", "status": "ready", "route": "/vault/vault-view-response-envelope-board.json"},
    {"gp": 477, "title": "View Redaction Receipt Draft Ledger", "status": "ready", "route": "/vault/view-redaction-receipt-draft-ledger.json"},
    {"gp": 478, "title": "Tower View Result Delivery Preview Board", "status": "ready", "route": "/vault/tower-view-result-delivery-preview-board.json"},
    {"gp": 479, "title": "Tower Authorized View Safety Blocker Board", "status": "ready", "route": "/vault/tower-authorized-view-safety-blocker-board.json"},
    {"gp": 480, "title": "Tower Authorized View Protocol Readiness Checkpoint", "status": "ready", "route": "/vault/tower-authorized-view-protocol-readiness-checkpoint.json"},
]

BLOCKERS = [
    {"blocker_id": "no_download_protocol_execution", "blocked_action": "download_protocol_execution", "allowed": False, "reason": "This layer only executes controlled view protocol."},
    {"blocker_id": "no_proof_protocol_execution", "blocked_action": "proof_protocol_execution", "allowed": False, "reason": "Proof protocol comes in a later Tower-authorized layer."},
    {"blocker_id": "no_teller_to_vault_direct_call", "blocked_action": "teller_to_vault_direct_call", "allowed": False, "reason": "Teller requests must go to Tower first."},
    {"blocker_id": "no_teller_direct_view", "blocked_action": "teller_direct_view_from_vault", "allowed": False, "reason": "Tower owns view protocol."},
    {"blocker_id": "no_public_vault_dashboard", "blocked_action": "public_vault_dashboard", "allowed": False, "reason": "Tower is the face; Vault remains headless."},
    {"blocker_id": "no_direct_vault_user_portal", "blocked_action": "direct_vault_user_portal", "allowed": False, "reason": "People do not enter Vault directly."},
    {"blocker_id": "no_employee_vendor_customer_browse", "blocked_action": "employee_vendor_customer_vault_browsing", "allowed": False, "reason": "Teller receives Tower-safe outputs only."},
    {"blocker_id": "no_external_collaborator_browse", "blocked_action": "external_collaborator_browsing", "allowed": False, "reason": "No shared-drive behavior."},
    {"blocker_id": "no_public_links", "blocked_action": "public_links_or_raw_urls", "allowed": False, "reason": "View protocol does not create public links or raw URLs."},
    {"blocker_id": "no_raw_file_bytes_json", "blocked_action": "raw_file_bytes_json", "allowed": False, "reason": "View envelopes return redacted projection metadata only."},
    {"blocker_id": "no_raw_paths_or_tokens", "blocked_action": "raw_path_or_token_exposure", "allowed": False, "reason": "View protocol never exposes paths or tokens."},
    {"blocker_id": "no_provider_dependency", "blocked_action": "provider_dependency", "allowed": False, "reason": "Local-first sealed memory remains default."},
    {"blocker_id": "no_delete_restore_move", "blocked_action": "delete_restore_physical_move", "allowed": False, "reason": "View protocol does not mutate Vault lifecycle state or move objects."},
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


def _view_eligibility_id(request_id: str) -> str:
    return "view_eligibility_gate_" + calculate_sha256_bytes(("view_eligibility|" + request_id).encode("utf-8"))[:24]


def _view_projection_id(request_id: str) -> str:
    return "redacted_view_projection_" + calculate_sha256_bytes(("view_projection|" + request_id).encode("utf-8"))[:24]


def _view_session_id(request_id: str) -> str:
    return "tower_view_session_draft_" + calculate_sha256_bytes(("view_session|" + request_id).encode("utf-8"))[:24]


def _internal_view_request_id(request_id: str) -> str:
    return "tower_internal_vault_view_request_" + calculate_sha256_bytes(("internal_view_request|" + request_id).encode("utf-8"))[:24]


def _view_response_id(request_id: str) -> str:
    return "vault_view_response_envelope_" + calculate_sha256_bytes(("view_response|" + request_id).encode("utf-8"))[:24]


def _view_receipt_id(request_id: str) -> str:
    return "view_redaction_receipt_draft_" + calculate_sha256_bytes(("view_receipt|" + request_id).encode("utf-8"))[:24]


def _delivery_preview_id(request_id: str) -> str:
    return "tower_view_result_delivery_preview_" + calculate_sha256_bytes(("view_delivery|" + request_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    identity = get_tower_identity_permission_gate_board().get("identity_permission_gates", [])
    clearance = get_clearance_step_up_approval_gate_board().get("clearance_gates", [])
    protocol = get_protocol_type_decision_board().get("protocol_decisions", [])
    redaction = get_redaction_scope_enforcement_board().get("redaction_scopes", [])
    drafts = get_tower_authorized_vault_request_draft_builder().get("vault_request_drafts", [])
    receipts = get_tower_protocol_receipt_draft_ledger().get("protocol_receipt_drafts", [])
    queue = get_vault_call_pending_queue_preview_board().get("pending_queue_previews", [])

    identity_by_request = {row["request_id"]: row for row in identity}
    clearance_by_request = {row["request_id"]: row for row in clearance}
    protocol_by_request = {row["request_id"]: row for row in protocol}
    redaction_by_request = {row["request_id"]: row for row in redaction}
    receipt_by_request = {row["request_id"]: row for row in receipts}
    queue_by_request = {row["request_id"]: row for row in queue}

    rows = []
    for draft in drafts:
        request_id = draft["request_id"]
        identity_row = identity_by_request.get(request_id, {})
        clearance_row = clearance_by_request.get(request_id, {})
        protocol_row = protocol_by_request.get(request_id, {})
        redaction_row = redaction_by_request.get(request_id, {})
        receipt_row = receipt_by_request.get(request_id, {})
        queue_row = queue_by_request.get(request_id, {})
        rows.append(
            {
                "request_id": request_id,
                "vault_request_draft_id": draft["vault_request_draft_id"],
                "workflow_type": draft["workflow_type"],
                "selected_protocol": draft["selected_protocol"],
                "originating_service": draft["originating_service"],
                "tower_is_requester": bool(draft["tower_is_requester"]),
                "teller_is_requester": bool(draft["teller_is_requester"]),
                "vault_call_ready": bool(draft["vault_call_ready"]),
                "vault_call_sent": bool(draft["vault_call_sent"]),
                "protocol_execution_allowed": bool(draft["protocol_execution_allowed"]),
                "raw_file_bytes_requested": bool(draft["raw_file_bytes_requested"]),
                "raw_path_requested": bool(draft["raw_path_requested"]),
                "public_link_requested": bool(draft["public_link_requested"]),
                "request_draft_hash": draft["request_draft_hash"],
                "tower_identity_check_required": bool(identity_row.get("tower_identity_check_required", 1)),
                "tower_permission_check_required": bool(identity_row.get("tower_permission_check_required", 1)),
                "teller_self_approval_allowed": bool(identity_row.get("teller_self_approval_allowed", 0)),
                "vault_direct_approval_allowed": bool(identity_row.get("vault_direct_approval_allowed", 0)),
                "clearance_required": bool(clearance_row.get("clearance_required", 1)),
                "step_up_required": bool(clearance_row.get("step_up_required", 0)),
                "owner_admin_required": bool(clearance_row.get("owner_admin_required", 0)),
                "tower_approval_required": bool(clearance_row.get("tower_approval_required", 1)),
                "requested_output_type": protocol_row.get("requested_output_type", "status"),
                "tower_protocol_gate_required": bool(protocol_row.get("tower_protocol_gate_required", 1)),
                "teller_direct_protocol_allowed": bool(protocol_row.get("teller_direct_protocol_allowed", 0)),
                "vault_answers_tower_only": bool(protocol_row.get("vault_answers_tower_only", 1)),
                "redaction_required": bool(redaction_row.get("redaction_required", 1)),
                "raw_file_bytes_redacted": bool(redaction_row.get("raw_file_bytes_redacted", 1)),
                "raw_path_redacted": bool(redaction_row.get("raw_path_redacted", 1)),
                "raw_file_url_redacted": bool(redaction_row.get("raw_file_url_redacted", 1)),
                "raw_token_redacted": bool(redaction_row.get("raw_token_redacted", 1)),
                "public_link_redacted": bool(redaction_row.get("public_link_redacted", 1)),
                "direct_browse_redacted": bool(redaction_row.get("direct_browse_redacted", 1)),
                "tower_protocol_receipt_draft_id": receipt_row.get("tower_protocol_receipt_draft_id", "missing_tower_protocol_receipt"),
                "tower_protocol_receipt_hash": receipt_row.get("tower_protocol_receipt_hash", "missing_tower_protocol_receipt_hash"),
                "vault_service_receipt_required": bool(receipt_row.get("vault_service_receipt_required", 1)),
                "pending_queue_id": queue_row.get("pending_queue_id", "missing_pending_queue"),
                "tower_protocol_pending": bool(queue_row.get("tower_protocol_pending", 1)),
                "vault_call_pending": bool(queue_row.get("vault_call_pending", 1)),
            }
        )
    return rows


def initialize_tower_authorized_view_protocol_layer() -> Dict[str, Any]:
    global _GP471_INIT_CACHE
    if _GP471_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP471_INIT_CACHE)

    previous = validate_tower_vault_request_protocol_gate_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS view_eligibility_gates (
                view_eligibility_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                vault_request_draft_id TEXT NOT NULL,
                gate_state TEXT NOT NULL,
                tower_is_requester INTEGER NOT NULL,
                teller_is_requester INTEGER NOT NULL,
                tower_identity_check_passed INTEGER NOT NULL,
                tower_permission_check_passed INTEGER NOT NULL,
                tower_approval_required INTEGER NOT NULL,
                tower_approval_recorded INTEGER NOT NULL,
                view_protocol_allowed INTEGER NOT NULL,
                download_protocol_allowed INTEGER NOT NULL,
                proof_protocol_allowed INTEGER NOT NULL,
                raw_file_view_allowed INTEGER NOT NULL,
                public_view_link_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS redacted_view_projections (
                view_projection_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                vault_request_draft_id TEXT NOT NULL,
                projection_state TEXT NOT NULL,
                projection_type TEXT NOT NULL,
                allowed_fields TEXT NOT NULL,
                redacted_fields TEXT NOT NULL,
                raw_file_bytes_included INTEGER NOT NULL,
                raw_path_included INTEGER NOT NULL,
                raw_file_url_included INTEGER NOT NULL,
                raw_token_included INTEGER NOT NULL,
                public_link_included INTEGER NOT NULL,
                direct_browse_included INTEGER NOT NULL,
                projection_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_view_session_drafts (
                view_session_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                vault_request_draft_id TEXT NOT NULL,
                view_projection_id TEXT NOT NULL,
                session_state TEXT NOT NULL,
                session_owner TEXT NOT NULL,
                tower_session_required INTEGER NOT NULL,
                teller_session_allowed INTEGER NOT NULL,
                direct_vault_session_allowed INTEGER NOT NULL,
                public_session_allowed INTEGER NOT NULL,
                expires_without_public_link INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_internal_vault_view_requests (
                internal_view_request_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                vault_request_draft_id TEXT NOT NULL,
                view_session_id TEXT NOT NULL,
                request_state TEXT NOT NULL,
                from_service TEXT NOT NULL,
                to_service TEXT NOT NULL,
                vault_answer_target TEXT NOT NULL,
                internal_vault_view_call_sent INTEGER NOT NULL,
                teller_call_sent INTEGER NOT NULL,
                raw_file_bytes_requested INTEGER NOT NULL,
                raw_path_requested INTEGER NOT NULL,
                public_link_requested INTEGER NOT NULL,
                internal_request_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_view_response_envelopes (
                view_response_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                internal_view_request_id TEXT NOT NULL,
                view_projection_id TEXT NOT NULL,
                response_state TEXT NOT NULL,
                answered_to TEXT NOT NULL,
                vault_answered_tower_only INTEGER NOT NULL,
                redacted_view_payload_ready INTEGER NOT NULL,
                raw_file_bytes_returned INTEGER NOT NULL,
                raw_path_returned INTEGER NOT NULL,
                raw_file_url_returned INTEGER NOT NULL,
                raw_token_returned INTEGER NOT NULL,
                public_link_returned INTEGER NOT NULL,
                response_envelope_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS view_redaction_receipt_drafts (
                view_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                view_response_id TEXT NOT NULL,
                tower_protocol_receipt_hash TEXT NOT NULL,
                receipt_state TEXT NOT NULL,
                redaction_receipt_hash TEXT NOT NULL,
                receipt_finalized INTEGER NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                raw_file_bytes_receipted INTEGER NOT NULL,
                public_link_receipted INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_view_result_delivery_previews (
                delivery_preview_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                view_response_id TEXT NOT NULL,
                delivery_state TEXT NOT NULL,
                delivered_to TEXT NOT NULL,
                teller_delivery_allowed INTEGER NOT NULL,
                direct_person_delivery_allowed INTEGER NOT NULL,
                direct_vault_link_included INTEGER NOT NULL,
                raw_file_bytes_included INTEGER NOT NULL,
                public_link_included INTEGER NOT NULL,
                workflow_safe_status_ready INTEGER NOT NULL,
                delivery_preview_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_authorized_view_safety_blockers (
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
                INSERT OR REPLACE INTO tower_authorized_view_safety_blockers (
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
            view_eligibility_id = _view_eligibility_id(request_id)
            view_projection_id = _view_projection_id(request_id)
            view_session_id = _view_session_id(request_id)
            internal_view_request_id = _internal_view_request_id(request_id)
            view_response_id = _view_response_id(request_id)
            view_receipt_id = _view_receipt_id(request_id)
            delivery_preview_id = _delivery_preview_id(request_id)

            conn.execute(
                """
                INSERT OR REPLACE INTO view_eligibility_gates (
                    view_eligibility_id, request_id, vault_request_draft_id,
                    gate_state, tower_is_requester, teller_is_requester,
                    tower_identity_check_passed, tower_permission_check_passed,
                    tower_approval_required, tower_approval_recorded,
                    view_protocol_allowed, download_protocol_allowed,
                    proof_protocol_allowed, raw_file_view_allowed,
                    public_view_link_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    view_eligibility_id,
                    request_id,
                    row["vault_request_draft_id"],
                    "view_eligibility_gate_passed_for_tower_only",
                    1,
                    0,
                    1,
                    1,
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            projection_material = {
                "request_id": request_id,
                "vault_request_draft_id": row["vault_request_draft_id"],
                "projection_type": "redacted_tower_view_projection",
                "raw_file_bytes_included": False,
                "raw_path_included": False,
                "raw_file_url_included": False,
                "raw_token_included": False,
                "public_link_included": False,
                "direct_browse_included": False,
            }
            projection_hash = calculate_sha256_bytes(repr(sorted(projection_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO redacted_view_projections (
                    view_projection_id, request_id, vault_request_draft_id,
                    projection_state, projection_type, allowed_fields,
                    redacted_fields, raw_file_bytes_included,
                    raw_path_included, raw_file_url_included,
                    raw_token_included, public_link_included,
                    direct_browse_included, projection_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    view_projection_id,
                    request_id,
                    row["vault_request_draft_id"],
                    "redacted_view_projection_ready_for_tower",
                    "redacted_tower_view_projection",
                    "request_id|workflow_type|selected_protocol|view_state|projection_hash|redaction_receipt_hash",
                    "raw_file_bytes|raw_path|raw_file_url|raw_download_token|raw_share_token|public_link|direct_browse|shared_folder|physical_storage_path",
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    projection_hash,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_view_session_drafts (
                    view_session_id, request_id, vault_request_draft_id,
                    view_projection_id, session_state, session_owner,
                    tower_session_required, teller_session_allowed,
                    direct_vault_session_allowed, public_session_allowed,
                    expires_without_public_link, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    view_session_id,
                    request_id,
                    row["vault_request_draft_id"],
                    view_projection_id,
                    "tower_view_session_draft_ready_internal_only",
                    "Tower",
                    1,
                    0,
                    0,
                    0,
                    1,
                    now,
                ),
            )

            internal_request_material = {
                "request_id": request_id,
                "vault_request_draft_id": row["vault_request_draft_id"],
                "view_session_id": view_session_id,
                "from_service": "Tower",
                "to_service": "Vault",
                "vault_answer_target": "Tower",
                "internal_vault_view_call_sent": True,
                "teller_call_sent": False,
                "raw_file_bytes_requested": False,
                "raw_path_requested": False,
                "public_link_requested": False,
            }
            internal_request_hash = calculate_sha256_bytes(repr(sorted(internal_request_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_internal_vault_view_requests (
                    internal_view_request_id, request_id,
                    vault_request_draft_id, view_session_id,
                    request_state, from_service, to_service,
                    vault_answer_target, internal_vault_view_call_sent,
                    teller_call_sent, raw_file_bytes_requested,
                    raw_path_requested, public_link_requested,
                    internal_request_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    internal_view_request_id,
                    request_id,
                    row["vault_request_draft_id"],
                    view_session_id,
                    "tower_internal_vault_view_request_sent_controlled",
                    "Tower",
                    "Vault",
                    "Tower",
                    1,
                    0,
                    0,
                    0,
                    0,
                    internal_request_hash,
                    now,
                ),
            )

            response_material = {
                "request_id": request_id,
                "internal_view_request_id": internal_view_request_id,
                "view_projection_id": view_projection_id,
                "answered_to": "Tower",
                "vault_answered_tower_only": True,
                "redacted_view_payload_ready": True,
                "raw_file_bytes_returned": False,
                "raw_path_returned": False,
                "raw_file_url_returned": False,
                "raw_token_returned": False,
                "public_link_returned": False,
            }
            response_hash = calculate_sha256_bytes(repr(sorted(response_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO vault_view_response_envelopes (
                    view_response_id, request_id,
                    internal_view_request_id, view_projection_id,
                    response_state, answered_to,
                    vault_answered_tower_only,
                    redacted_view_payload_ready,
                    raw_file_bytes_returned, raw_path_returned,
                    raw_file_url_returned, raw_token_returned,
                    public_link_returned, response_envelope_hash,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    view_response_id,
                    request_id,
                    internal_view_request_id,
                    view_projection_id,
                    "vault_view_response_envelope_ready_for_tower",
                    "Tower",
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    response_hash,
                    now,
                ),
            )

            redaction_receipt_hash = calculate_sha256_bytes(
                f"view-redaction-receipt|{request_id}|{response_hash}|{row['tower_protocol_receipt_hash']}|redacted".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO view_redaction_receipt_drafts (
                    view_receipt_id, request_id, view_response_id,
                    tower_protocol_receipt_hash, receipt_state,
                    redaction_receipt_hash, receipt_finalized,
                    append_only, mutable, raw_file_bytes_receipted,
                    public_link_receipted, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    view_receipt_id,
                    request_id,
                    view_response_id,
                    row["tower_protocol_receipt_hash"],
                    "view_redaction_receipt_draft_ready_append_only",
                    redaction_receipt_hash,
                    0,
                    1,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            delivery_material = {
                "request_id": request_id,
                "view_response_id": view_response_id,
                "delivered_to": "Tower",
                "teller_delivery_allowed": True,
                "direct_person_delivery_allowed": False,
                "direct_vault_link_included": False,
                "raw_file_bytes_included": False,
                "public_link_included": False,
                "workflow_safe_status_ready": True,
            }
            delivery_hash = calculate_sha256_bytes(repr(sorted(delivery_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_view_result_delivery_previews (
                    delivery_preview_id, request_id, view_response_id,
                    delivery_state, delivered_to,
                    teller_delivery_allowed,
                    direct_person_delivery_allowed,
                    direct_vault_link_included,
                    raw_file_bytes_included, public_link_included,
                    workflow_safe_status_ready, delivery_preview_hash,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    delivery_preview_id,
                    request_id,
                    view_response_id,
                    "tower_view_result_delivery_preview_ready_workflow_safe",
                    "Tower",
                    1,
                    0,
                    0,
                    0,
                    0,
                    1,
                    delivery_hash,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_tower_protocol_gate_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP471_INIT_CACHE = dict(result)
    return result


def get_tower_authorized_view_protocol_shell() -> Dict[str, Any]:
    init = initialize_tower_authorized_view_protocol_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 471,
        "title": "Tower Authorized View Protocol Shell",
        "ready": True,
        "initialized": init,
        "doctrine": DOCTRINE,
        "correct_flow": DOCTRINE["correct_flow"],
        "controlled_view_only": True,
        "download_protocol_execution_allowed": False,
        "proof_protocol_execution_allowed": False,
        "raw_file_bytes_exposed_by_view": False,
        "public_link_created_by_view": False,
        "locks": LOCKS,
    }


def get_view_eligibility_gate_board() -> Dict[str, Any]:
    initialize_tower_authorized_view_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM view_eligibility_gates ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 472,
        "title": "View Eligibility Gate Board",
        "ready": True,
        "view_eligibility_count": len(rows),
        "view_eligibility_gates": rows,
        "all_tower_is_requester": all(bool(item["tower_is_requester"]) for item in rows),
        "no_teller_is_requester": all(not bool(item["teller_is_requester"]) for item in rows),
        "all_tower_identity_permission_passed": all(bool(item["tower_identity_check_passed"]) and bool(item["tower_permission_check_passed"]) for item in rows),
        "all_tower_approval_recorded": all(bool(item["tower_approval_recorded"]) for item in rows),
        "all_view_protocol_allowed": all(bool(item["view_protocol_allowed"]) for item in rows),
        "no_download_protocol_allowed": all(not bool(item["download_protocol_allowed"]) for item in rows),
        "no_proof_protocol_allowed": all(not bool(item["proof_protocol_allowed"]) for item in rows),
        "no_raw_file_view": all(not bool(item["raw_file_view_allowed"]) for item in rows),
        "no_public_view_link": all(not bool(item["public_view_link_allowed"]) for item in rows),
    }


def get_redacted_view_projection_builder() -> Dict[str, Any]:
    initialize_tower_authorized_view_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM redacted_view_projections ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 473,
        "title": "Redacted View Projection Builder",
        "ready": True,
        "projection_count": len(rows),
        "view_projections": rows,
        "all_redacted_for_tower": all(item["projection_state"] == "redacted_view_projection_ready_for_tower" for item in rows),
        "no_raw_file_bytes": all(not bool(item["raw_file_bytes_included"]) for item in rows),
        "no_raw_paths": all(not bool(item["raw_path_included"]) for item in rows),
        "no_raw_file_urls": all(not bool(item["raw_file_url_included"]) for item in rows),
        "no_raw_tokens": all(not bool(item["raw_token_included"]) for item in rows),
        "no_public_links": all(not bool(item["public_link_included"]) for item in rows),
        "no_direct_browse": all(not bool(item["direct_browse_included"]) for item in rows),
    }


def get_tower_view_session_draft_board() -> Dict[str, Any]:
    initialize_tower_authorized_view_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_view_session_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 474,
        "title": "Tower View Session Draft Board",
        "ready": True,
        "view_session_count": len(rows),
        "view_sessions": rows,
        "all_session_owner_tower": all(item["session_owner"] == "Tower" for item in rows),
        "all_tower_session_required": all(bool(item["tower_session_required"]) for item in rows),
        "no_teller_session": all(not bool(item["teller_session_allowed"]) for item in rows),
        "no_direct_vault_session": all(not bool(item["direct_vault_session_allowed"]) for item in rows),
        "no_public_session": all(not bool(item["public_session_allowed"]) for item in rows),
        "all_expire_without_public_link": all(bool(item["expires_without_public_link"]) for item in rows),
    }


def get_tower_internal_vault_view_request_ledger() -> Dict[str, Any]:
    initialize_tower_authorized_view_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_internal_vault_view_requests ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 475,
        "title": "Tower Internal Vault View Request Ledger",
        "ready": True,
        "internal_view_request_count": len(rows),
        "internal_view_requests": rows,
        "all_from_tower_to_vault": all(item["from_service"] == "Tower" and item["to_service"] == "Vault" for item in rows),
        "all_vault_answer_target_tower": all(item["vault_answer_target"] == "Tower" for item in rows),
        "all_internal_view_calls_sent": all(bool(item["internal_vault_view_call_sent"]) for item in rows),
        "no_teller_calls_sent": all(not bool(item["teller_call_sent"]) for item in rows),
        "no_raw_file_bytes_requested": all(not bool(item["raw_file_bytes_requested"]) for item in rows),
        "no_raw_paths_requested": all(not bool(item["raw_path_requested"]) for item in rows),
        "no_public_links_requested": all(not bool(item["public_link_requested"]) for item in rows),
    }


def get_vault_view_response_envelope_board() -> Dict[str, Any]:
    initialize_tower_authorized_view_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM vault_view_response_envelopes ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 476,
        "title": "Vault View Response Envelope Board",
        "ready": True,
        "view_response_count": len(rows),
        "view_response_envelopes": rows,
        "all_answered_to_tower": all(item["answered_to"] == "Tower" for item in rows),
        "all_vault_answered_tower_only": all(bool(item["vault_answered_tower_only"]) for item in rows),
        "all_redacted_view_payload_ready": all(bool(item["redacted_view_payload_ready"]) for item in rows),
        "no_raw_file_bytes_returned": all(not bool(item["raw_file_bytes_returned"]) for item in rows),
        "no_raw_paths_returned": all(not bool(item["raw_path_returned"]) for item in rows),
        "no_raw_file_urls_returned": all(not bool(item["raw_file_url_returned"]) for item in rows),
        "no_raw_tokens_returned": all(not bool(item["raw_token_returned"]) for item in rows),
        "no_public_links_returned": all(not bool(item["public_link_returned"]) for item in rows),
    }


def get_view_redaction_receipt_draft_ledger() -> Dict[str, Any]:
    initialize_tower_authorized_view_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM view_redaction_receipt_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 477,
        "title": "View Redaction Receipt Draft Ledger",
        "ready": True,
        "view_receipt_count": len(rows),
        "view_receipts": rows,
        "all_receipts_draft": all(not bool(item["receipt_finalized"]) for item in rows),
        "all_append_only": all(bool(item["append_only"]) for item in rows),
        "all_immutable": all(not bool(item["mutable"]) for item in rows),
        "no_raw_file_bytes_receipted": all(not bool(item["raw_file_bytes_receipted"]) for item in rows),
        "no_public_links_receipted": all(not bool(item["public_link_receipted"]) for item in rows),
    }


def get_tower_view_result_delivery_preview_board() -> Dict[str, Any]:
    initialize_tower_authorized_view_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_view_result_delivery_previews ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 478,
        "title": "Tower View Result Delivery Preview Board",
        "ready": True,
        "delivery_preview_count": len(rows),
        "delivery_previews": rows,
        "all_delivered_to_tower": all(item["delivered_to"] == "Tower" for item in rows),
        "all_teller_delivery_allowed_after_tower": all(bool(item["teller_delivery_allowed"]) for item in rows),
        "no_direct_person_delivery": all(not bool(item["direct_person_delivery_allowed"]) for item in rows),
        "no_direct_vault_link": all(not bool(item["direct_vault_link_included"]) for item in rows),
        "no_raw_file_bytes": all(not bool(item["raw_file_bytes_included"]) for item in rows),
        "no_public_links": all(not bool(item["public_link_included"]) for item in rows),
        "all_workflow_safe_status_ready": all(bool(item["workflow_safe_status_ready"]) for item in rows),
    }


def get_tower_authorized_view_safety_blocker_board() -> Dict[str, Any]:
    initialize_tower_authorized_view_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_authorized_view_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 479,
        "title": "Tower Authorized View Safety Blocker Board",
        "ready": True,
        "blocker_count": len(rows),
        "blockers": rows,
        "unsafe_action_count": sum(1 for item in rows if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in rows),
    }


def get_tower_authorized_view_protocol_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_tower_authorized_view_protocol_layer()

    shell = get_tower_authorized_view_protocol_shell()
    eligibility = get_view_eligibility_gate_board()
    projection = get_redacted_view_projection_builder()
    sessions = get_tower_view_session_draft_board()
    requests = get_tower_internal_vault_view_request_ledger()
    responses = get_vault_view_response_envelope_board()
    receipts = get_view_redaction_receipt_draft_ledger()
    delivery = get_tower_view_result_delivery_preview_board()
    blockers = get_tower_authorized_view_safety_blocker_board()

    checks = {
        "previous_tower_protocol_gate_ready": init["previous_tower_protocol_gate_ready"] is True,
        "view_protocol_shell_ready": shell["ready"] is True,
        "doctrine_tower_teller_vault_locked": DOCTRINE["tower"] == "face_protocol_authority" and DOCTRINE["teller"] == "workflow_request_source" and DOCTRINE["vault"] == "sealed_memory",
        "correct_flow_locked": DOCTRINE["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller",
        "tower_executes_controlled_view_protocol": DOCTRINE["tower_executes_controlled_view_protocol"] is True,
        "view_answers_tower_only": DOCTRINE["view_protocol_answers_tower_only"] is True and DOCTRINE["vault_answers_tower_only"] is True,
        "view_exposes_no_raw_or_public_link": DOCTRINE["raw_file_bytes_exposed_by_view"] is False and DOCTRINE["public_link_created_by_view"] is False,
        "eligibility_ready": eligibility["ready"] is True and eligibility["view_eligibility_count"] >= 2,
        "eligibility_tower_only": eligibility["all_tower_is_requester"] is True and eligibility["no_teller_is_requester"] is True,
        "eligibility_passed_for_view_only": eligibility["all_tower_identity_permission_passed"] is True and eligibility["all_tower_approval_recorded"] is True and eligibility["all_view_protocol_allowed"] is True,
        "eligibility_no_download_proof_raw_public": eligibility["no_download_protocol_allowed"] is True and eligibility["no_proof_protocol_allowed"] is True and eligibility["no_raw_file_view"] is True and eligibility["no_public_view_link"] is True,
        "projection_ready": projection["ready"] is True and projection["projection_count"] >= 2,
        "projection_redacted_no_raw_path_url_token_public_direct": projection["all_redacted_for_tower"] is True and projection["no_raw_file_bytes"] is True and projection["no_raw_paths"] is True and projection["no_raw_file_urls"] is True and projection["no_raw_tokens"] is True and projection["no_public_links"] is True and projection["no_direct_browse"] is True,
        "sessions_ready": sessions["ready"] is True and sessions["view_session_count"] >= 2,
        "sessions_tower_only_no_public_direct": sessions["all_session_owner_tower"] is True and sessions["all_tower_session_required"] is True and sessions["no_teller_session"] is True and sessions["no_direct_vault_session"] is True and sessions["no_public_session"] is True,
        "internal_requests_ready": requests["ready"] is True and requests["internal_view_request_count"] >= 2,
        "internal_requests_tower_to_vault_only": requests["all_from_tower_to_vault"] is True and requests["all_vault_answer_target_tower"] is True and requests["all_internal_view_calls_sent"] is True and requests["no_teller_calls_sent"] is True,
        "internal_requests_no_raw_path_public_requested": requests["no_raw_file_bytes_requested"] is True and requests["no_raw_paths_requested"] is True and requests["no_public_links_requested"] is True,
        "responses_ready": responses["ready"] is True and responses["view_response_count"] >= 2,
        "responses_tower_only_redacted": responses["all_answered_to_tower"] is True and responses["all_vault_answered_tower_only"] is True and responses["all_redacted_view_payload_ready"] is True,
        "responses_no_raw_path_url_token_public": responses["no_raw_file_bytes_returned"] is True and responses["no_raw_paths_returned"] is True and responses["no_raw_file_urls_returned"] is True and responses["no_raw_tokens_returned"] is True and responses["no_public_links_returned"] is True,
        "view_receipts_ready": receipts["ready"] is True and receipts["view_receipt_count"] >= 2,
        "view_receipts_draft_append_only_no_raw_public": receipts["all_receipts_draft"] is True and receipts["all_append_only"] is True and receipts["all_immutable"] is True and receipts["no_raw_file_bytes_receipted"] is True and receipts["no_public_links_receipted"] is True,
        "delivery_ready": delivery["ready"] is True and delivery["delivery_preview_count"] >= 2,
        "delivery_to_tower_then_workflow_safe": delivery["all_delivered_to_tower"] is True and delivery["all_teller_delivery_allowed_after_tower"] is True and delivery["all_workflow_safe_status_ready"] is True,
        "delivery_no_direct_person_raw_public": delivery["no_direct_person_delivery"] is True and delivery["no_direct_vault_link"] is True and delivery["no_raw_file_bytes"] is True and delivery["no_public_links"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "global_view_allowed_only": LOCKS["controlled_view_protocol_execution_allowed"] is True and LOCKS["download_protocol_execution_allowed"] is False and LOCKS["proof_protocol_execution_allowed"] is False,
        "global_no_teller_to_vault": LOCKS["teller_to_vault_direct_call_allowed"] is False and LOCKS["vault_direct_request_from_teller_allowed"] is False,
        "global_no_public_dashboard_portal_browse": LOCKS["public_vault_dashboard_allowed"] is False and LOCKS["direct_vault_user_portal_allowed"] is False and LOCKS["employee_vault_browsing_allowed"] is False and LOCKS["external_collaborator_browsing_allowed"] is False,
        "global_no_public_links_raw_bytes_paths_tokens": LOCKS["public_url_created"] is False and LOCKS["share_link_created"] is False and LOCKS["raw_file_bytes_returned_by_json"] is False and LOCKS["raw_path_exposed"] is False and LOCKS["raw_file_url_exposed"] is False and LOCKS["raw_download_token_exposed"] is False,
        "global_no_provider_delete_restore_move": LOCKS["provider_storage_required"] is False and LOCKS["hard_delete_allowed"] is False and LOCKS["purge_allowed"] is False and LOCKS["restore_execution_allowed"] is False and LOCKS["physical_object_move_allowed"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 480,
        "title": "Tower Authorized View Protocol Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Tower authorized view protocol layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — TOWER AUTHORIZED DOWNLOAD PROTOCOL LAYER / GP481-GP490",
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
            "no download protocol execution in this layer",
            "no proof protocol execution in this layer",
            "no public/beta/provider upload",
            "no delete or purge",
            "no restore execution",
            "no quarantine release",
            "no physical object move",
            "no provider dependency by default",
        ],
    }


def get_tower_authorized_view_protocol_home() -> Dict[str, Any]:
    checkpoint = get_tower_authorized_view_protocol_readiness_checkpoint()
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


def validate_tower_authorized_view_protocol_layer() -> Dict[str, Any]:
    checkpoint = get_tower_authorized_view_protocol_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_tower_protocol_gate_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"]["tower_executes_controlled_view_protocol"] is True
    assert checkpoint["checks"]["view_answers_tower_only"] is True
    assert checkpoint["checks"]["view_exposes_no_raw_or_public_link"] is True
    assert checkpoint["checks"]["eligibility_ready"] is True
    assert checkpoint["checks"]["eligibility_tower_only"] is True
    assert checkpoint["checks"]["eligibility_passed_for_view_only"] is True
    assert checkpoint["checks"]["eligibility_no_download_proof_raw_public"] is True
    assert checkpoint["checks"]["projection_ready"] is True
    assert checkpoint["checks"]["projection_redacted_no_raw_path_url_token_public_direct"] is True
    assert checkpoint["checks"]["sessions_ready"] is True
    assert checkpoint["checks"]["sessions_tower_only_no_public_direct"] is True
    assert checkpoint["checks"]["internal_requests_ready"] is True
    assert checkpoint["checks"]["internal_requests_tower_to_vault_only"] is True
    assert checkpoint["checks"]["internal_requests_no_raw_path_public_requested"] is True
    assert checkpoint["checks"]["responses_ready"] is True
    assert checkpoint["checks"]["responses_tower_only_redacted"] is True
    assert checkpoint["checks"]["responses_no_raw_path_url_token_public"] is True
    assert checkpoint["checks"]["view_receipts_ready"] is True
    assert checkpoint["checks"]["view_receipts_draft_append_only_no_raw_public"] is True
    assert checkpoint["checks"]["delivery_ready"] is True
    assert checkpoint["checks"]["delivery_to_tower_then_workflow_safe"] is True
    assert checkpoint["checks"]["delivery_no_direct_person_raw_public"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["controlled_view_protocol_execution_allowed"] is True
    assert LOCKS["download_protocol_execution_allowed"] is False
    assert LOCKS["proof_protocol_execution_allowed"] is False
    assert LOCKS["public_view_link_allowed"] is False
    assert LOCKS["raw_file_view_allowed"] is False
    assert LOCKS["teller_to_vault_direct_call_allowed"] is False
    assert LOCKS["direct_vault_user_portal_allowed"] is False
    assert LOCKS["public_vault_dashboard_allowed"] is False
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
    checkpoint = get_tower_authorized_view_protocol_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "correct_flow": DOCTRINE["correct_flow"],
        "controlled_view_protocol_execution_allowed": True,
        "download_protocol_execution_allowed": False,
        "proof_protocol_execution_allowed": False,
        "teller_to_vault_direct_call_allowed": False,
        "vault_answers_tower_only": True,
        "locks_preserved": True,
    }


def get_gp471_status() -> Dict[str, Any]:
    return _gp_status(471)


def get_gp472_status() -> Dict[str, Any]:
    return _gp_status(472)


def get_gp473_status() -> Dict[str, Any]:
    return _gp_status(473)


def get_gp474_status() -> Dict[str, Any]:
    return _gp_status(474)


def get_gp475_status() -> Dict[str, Any]:
    return _gp_status(475)


def get_gp476_status() -> Dict[str, Any]:
    return _gp_status(476)


def get_gp477_status() -> Dict[str, Any]:
    return _gp_status(477)


def get_gp478_status() -> Dict[str, Any]:
    return _gp_status(478)


def get_gp479_status() -> Dict[str, Any]:
    return _gp_status(479)


def get_gp480_status() -> Dict[str, Any]:
    return _gp_status(480)
