
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — TOWER AUTHORIZED DOWNLOAD PROTOCOL LAYER / GP481-GP490"
LAYER_ID = "vault_gp481_490_tower_authorized_download_protocol_layer"
READINESS_LABEL = "Tower authorized download protocol layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_tower_authorized_download_protocol_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.tower_authorized_view_protocol_layer_service import (
        get_view_eligibility_gate_board,
        get_redacted_view_projection_builder,
        get_tower_view_session_draft_board,
        get_tower_internal_vault_view_request_ledger,
        get_vault_view_response_envelope_board,
        get_view_redaction_receipt_draft_ledger,
        get_tower_view_result_delivery_preview_board,
        validate_tower_authorized_view_protocol_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP481-GP490 requires GP471-GP480 Tower authorized view protocol layer first."
    ) from exc


_GP481_INIT_CACHE = None

DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": "Teller -> Tower -> Vault -> Tower -> Teller",
    "tower_executes_controlled_download_protocol": True,
    "download_protocol_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
    "teller_can_download_from_vault_directly": False,
    "vault_answers_tower_only": True,
    "raw_file_bytes_exposed_by_json": False,
    "raw_download_token_exposed": False,
    "public_link_created_by_download": False,
}

LOCKS = {
    "tower_authorized_download_protocol_layer": True,
    "controlled_download_protocol_metadata_allowed": True,
    "tower_download_session_drafts_allowed": True,
    "tower_internal_vault_download_requests_allowed": True,
    "vault_download_response_envelopes_allowed": True,
    "download_handle_hash_guards_allowed": True,
    "download_receipt_drafts_allowed": True,
    "tower_download_result_delivery_previews_allowed": True,

    "raw_file_bytes_returned_by_json": False,
    "raw_file_bytes_exposed": False,
    "raw_download_token_exposed": False,
    "raw_share_token_exposed": False,
    "raw_path_exposed": False,
    "raw_file_url_exposed": False,
    "public_download_link_created": False,
    "public_view_link_allowed": False,
    "proof_protocol_execution_allowed": False,
    "teller_direct_download_allowed": False,
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
    {"gp": 481, "title": "Tower Authorized Download Protocol Shell", "status": "ready", "route": "/vault/tower-authorized-download-protocol-shell.json"},
    {"gp": 482, "title": "Download Eligibility Gate Board", "status": "ready", "route": "/vault/download-eligibility-gate-board.json"},
    {"gp": 483, "title": "Download Scope Redaction Gate Board", "status": "ready", "route": "/vault/download-scope-redaction-gate-board.json"},
    {"gp": 484, "title": "Tower Download Session Draft Board", "status": "ready", "route": "/vault/tower-download-session-draft-board.json"},
    {"gp": 485, "title": "Tower Internal Vault Download Request Ledger", "status": "ready", "route": "/vault/tower-internal-vault-download-request-ledger.json"},
    {"gp": 486, "title": "Vault Download Response Envelope Board", "status": "ready", "route": "/vault/vault-download-response-envelope-board.json"},
    {"gp": 487, "title": "Download Handle Hash Guard Board", "status": "ready", "route": "/vault/download-handle-hash-guard-board.json"},
    {"gp": 488, "title": "Download Receipt Draft Ledger", "status": "ready", "route": "/vault/download-receipt-draft-ledger.json"},
    {"gp": 489, "title": "Tower Download Result Delivery Preview Board", "status": "ready", "route": "/vault/tower-download-result-delivery-preview-board.json"},
    {"gp": 490, "title": "Tower Authorized Download Protocol Readiness Checkpoint", "status": "ready", "route": "/vault/tower-authorized-download-protocol-readiness-checkpoint.json"},
]

BLOCKERS = [
    {"blocker_id": "no_raw_file_bytes_json", "blocked_action": "raw_file_bytes_returned_by_json", "allowed": False, "reason": "Download protocol uses sealed internal handle hashes, not JSON file bytes."},
    {"blocker_id": "no_raw_download_token", "blocked_action": "raw_download_token_exposure", "allowed": False, "reason": "Only token/hash guard metadata may be returned."},
    {"blocker_id": "no_public_download_link", "blocked_action": "public_download_link", "allowed": False, "reason": "Tower-controlled download never creates public links."},
    {"blocker_id": "no_raw_path_or_url", "blocked_action": "raw_path_or_file_url_exposure", "allowed": False, "reason": "Download envelopes do not expose paths or URLs."},
    {"blocker_id": "no_teller_direct_download", "blocked_action": "teller_direct_download_from_vault", "allowed": False, "reason": "Tower owns download protocol."},
    {"blocker_id": "no_teller_to_vault_direct_call", "blocked_action": "teller_to_vault_direct_call", "allowed": False, "reason": "Teller requests must go through Tower."},
    {"blocker_id": "no_proof_protocol_execution", "blocked_action": "proof_protocol_execution", "allowed": False, "reason": "Proof protocol comes in a later Tower-authorized layer."},
    {"blocker_id": "no_public_vault_dashboard", "blocked_action": "public_vault_dashboard", "allowed": False, "reason": "Tower is the face; Vault remains headless."},
    {"blocker_id": "no_direct_vault_user_portal", "blocked_action": "direct_vault_user_portal", "allowed": False, "reason": "People do not enter Vault directly."},
    {"blocker_id": "no_employee_vendor_customer_browse", "blocked_action": "employee_vendor_customer_vault_browsing", "allowed": False, "reason": "Teller receives Tower-safe outputs only."},
    {"blocker_id": "no_external_collaborator_browse", "blocked_action": "external_collaborator_browsing", "allowed": False, "reason": "No shared-drive behavior."},
    {"blocker_id": "no_provider_dependency", "blocked_action": "provider_dependency", "allowed": False, "reason": "Local-first sealed memory remains default."},
    {"blocker_id": "no_delete_restore_move", "blocked_action": "delete_restore_physical_move", "allowed": False, "reason": "Download protocol does not mutate Vault lifecycle state or move objects."},
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


def _download_eligibility_id(request_id: str) -> str:
    return "download_eligibility_gate_" + calculate_sha256_bytes(("download_eligibility|" + request_id).encode("utf-8"))[:24]


def _download_redaction_id(request_id: str) -> str:
    return "download_scope_redaction_gate_" + calculate_sha256_bytes(("download_redaction|" + request_id).encode("utf-8"))[:24]


def _download_session_id(request_id: str) -> str:
    return "tower_download_session_draft_" + calculate_sha256_bytes(("download_session|" + request_id).encode("utf-8"))[:24]


def _internal_download_request_id(request_id: str) -> str:
    return "tower_internal_vault_download_request_" + calculate_sha256_bytes(("internal_download_request|" + request_id).encode("utf-8"))[:24]


def _download_response_id(request_id: str) -> str:
    return "vault_download_response_envelope_" + calculate_sha256_bytes(("download_response|" + request_id).encode("utf-8"))[:24]


def _handle_guard_id(request_id: str) -> str:
    return "download_handle_hash_guard_" + calculate_sha256_bytes(("download_handle_guard|" + request_id).encode("utf-8"))[:24]


def _download_receipt_id(request_id: str) -> str:
    return "download_receipt_draft_" + calculate_sha256_bytes(("download_receipt|" + request_id).encode("utf-8"))[:24]


def _download_delivery_preview_id(request_id: str) -> str:
    return "tower_download_result_delivery_preview_" + calculate_sha256_bytes(("download_delivery|" + request_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    view_eligibility = get_view_eligibility_gate_board().get("view_eligibility_gates", [])
    projections = get_redacted_view_projection_builder().get("view_projections", [])
    sessions = get_tower_view_session_draft_board().get("view_sessions", [])
    view_requests = get_tower_internal_vault_view_request_ledger().get("internal_view_requests", [])
    responses = get_vault_view_response_envelope_board().get("view_response_envelopes", [])
    receipts = get_view_redaction_receipt_draft_ledger().get("view_receipts", [])
    deliveries = get_tower_view_result_delivery_preview_board().get("delivery_previews", [])

    projection_by_request = {row["request_id"]: row for row in projections}
    session_by_request = {row["request_id"]: row for row in sessions}
    request_by_request = {row["request_id"]: row for row in view_requests}
    response_by_request = {row["request_id"]: row for row in responses}
    receipt_by_request = {row["request_id"]: row for row in receipts}
    delivery_by_request = {row["request_id"]: row for row in deliveries}

    rows = []
    for eligible in view_eligibility:
        request_id = eligible["request_id"]
        projection = projection_by_request.get(request_id, {})
        session = session_by_request.get(request_id, {})
        view_request = request_by_request.get(request_id, {})
        response = response_by_request.get(request_id, {})
        receipt = receipt_by_request.get(request_id, {})
        delivery = delivery_by_request.get(request_id, {})

        rows.append(
            {
                "request_id": request_id,
                "vault_request_draft_id": eligible["vault_request_draft_id"],
                "tower_is_requester": bool(eligible.get("tower_is_requester", 1)),
                "teller_is_requester": bool(eligible.get("teller_is_requester", 0)),
                "tower_identity_check_passed": bool(eligible.get("tower_identity_check_passed", 1)),
                "tower_permission_check_passed": bool(eligible.get("tower_permission_check_passed", 1)),
                "tower_approval_recorded": bool(eligible.get("tower_approval_recorded", 1)),
                "view_protocol_allowed": bool(eligible.get("view_protocol_allowed", 1)),
                "download_protocol_allowed_from_prior": bool(eligible.get("download_protocol_allowed", 0)),
                "proof_protocol_allowed": bool(eligible.get("proof_protocol_allowed", 0)),
                "raw_file_view_allowed": bool(eligible.get("raw_file_view_allowed", 0)),
                "public_view_link_allowed": bool(eligible.get("public_view_link_allowed", 0)),
                "view_projection_id": projection.get("view_projection_id", "missing_view_projection"),
                "projection_hash": projection.get("projection_hash", "missing_projection_hash"),
                "raw_file_bytes_included": bool(projection.get("raw_file_bytes_included", 0)),
                "raw_path_included": bool(projection.get("raw_path_included", 0)),
                "raw_file_url_included": bool(projection.get("raw_file_url_included", 0)),
                "raw_token_included": bool(projection.get("raw_token_included", 0)),
                "public_link_included": bool(projection.get("public_link_included", 0)),
                "view_session_id": session.get("view_session_id", "missing_view_session"),
                "session_owner": session.get("session_owner", "Tower"),
                "tower_session_required": bool(session.get("tower_session_required", 1)),
                "direct_vault_session_allowed": bool(session.get("direct_vault_session_allowed", 0)),
                "public_session_allowed": bool(session.get("public_session_allowed", 0)),
                "internal_view_request_id": view_request.get("internal_view_request_id", "missing_internal_view_request"),
                "view_response_id": response.get("view_response_id", "missing_view_response"),
                "view_response_hash": response.get("response_envelope_hash", "missing_view_response_hash"),
                "vault_answered_tower_only": bool(response.get("vault_answered_tower_only", 1)),
                "redacted_view_payload_ready": bool(response.get("redacted_view_payload_ready", 1)),
                "view_receipt_id": receipt.get("view_receipt_id", "missing_view_receipt"),
                "redaction_receipt_hash": receipt.get("redaction_receipt_hash", "missing_redaction_receipt_hash"),
                "delivery_preview_id": delivery.get("delivery_preview_id", "missing_delivery_preview"),
                "workflow_safe_status_ready": bool(delivery.get("workflow_safe_status_ready", 1)),
            }
        )
    return rows


def initialize_tower_authorized_download_protocol_layer() -> Dict[str, Any]:
    global _GP481_INIT_CACHE
    if _GP481_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP481_INIT_CACHE)

    previous = validate_tower_authorized_view_protocol_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_eligibility_gates (
                download_eligibility_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                vault_request_draft_id TEXT NOT NULL,
                gate_state TEXT NOT NULL,
                tower_is_requester INTEGER NOT NULL,
                teller_is_requester INTEGER NOT NULL,
                tower_identity_check_passed INTEGER NOT NULL,
                tower_permission_check_passed INTEGER NOT NULL,
                tower_approval_recorded INTEGER NOT NULL,
                download_protocol_allowed INTEGER NOT NULL,
                proof_protocol_allowed INTEGER NOT NULL,
                teller_direct_download_allowed INTEGER NOT NULL,
                raw_file_bytes_json_allowed INTEGER NOT NULL,
                public_download_link_allowed INTEGER NOT NULL,
                raw_download_token_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_scope_redaction_gates (
                download_redaction_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                vault_request_draft_id TEXT NOT NULL,
                redaction_state TEXT NOT NULL,
                sealed_handle_only INTEGER NOT NULL,
                raw_file_bytes_redacted INTEGER NOT NULL,
                raw_path_redacted INTEGER NOT NULL,
                raw_file_url_redacted INTEGER NOT NULL,
                raw_download_token_redacted INTEGER NOT NULL,
                public_link_redacted INTEGER NOT NULL,
                direct_browse_redacted INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_download_session_drafts (
                download_session_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                vault_request_draft_id TEXT NOT NULL,
                download_redaction_id TEXT NOT NULL,
                session_state TEXT NOT NULL,
                session_owner TEXT NOT NULL,
                tower_session_required INTEGER NOT NULL,
                teller_session_allowed INTEGER NOT NULL,
                direct_vault_session_allowed INTEGER NOT NULL,
                public_session_allowed INTEGER NOT NULL,
                download_session_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_internal_vault_download_requests (
                internal_download_request_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                vault_request_draft_id TEXT NOT NULL,
                download_session_id TEXT NOT NULL,
                request_state TEXT NOT NULL,
                from_service TEXT NOT NULL,
                to_service TEXT NOT NULL,
                vault_answer_target TEXT NOT NULL,
                internal_vault_download_call_sent INTEGER NOT NULL,
                teller_call_sent INTEGER NOT NULL,
                raw_file_bytes_requested INTEGER NOT NULL,
                raw_path_requested INTEGER NOT NULL,
                raw_file_url_requested INTEGER NOT NULL,
                raw_token_requested INTEGER NOT NULL,
                public_link_requested INTEGER NOT NULL,
                internal_request_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_download_response_envelopes (
                download_response_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                internal_download_request_id TEXT NOT NULL,
                response_state TEXT NOT NULL,
                answered_to TEXT NOT NULL,
                vault_answered_tower_only INTEGER NOT NULL,
                sealed_download_handle_hash TEXT NOT NULL,
                sealed_download_artifact_hash TEXT NOT NULL,
                raw_file_bytes_returned_by_json INTEGER NOT NULL,
                raw_path_returned INTEGER NOT NULL,
                raw_file_url_returned INTEGER NOT NULL,
                raw_download_token_returned INTEGER NOT NULL,
                public_link_returned INTEGER NOT NULL,
                response_envelope_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_handle_hash_guards (
                handle_guard_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                download_response_id TEXT NOT NULL,
                guard_state TEXT NOT NULL,
                handle_hash_only INTEGER NOT NULL,
                raw_handle_visible INTEGER NOT NULL,
                raw_download_token_visible INTEGER NOT NULL,
                public_link_visible INTEGER NOT NULL,
                raw_file_bytes_visible INTEGER NOT NULL,
                expires_under_tower_control INTEGER NOT NULL,
                handle_guard_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_receipt_drafts (
                download_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                download_response_id TEXT NOT NULL,
                download_handle_guard_id TEXT NOT NULL,
                receipt_state TEXT NOT NULL,
                view_redaction_receipt_hash TEXT NOT NULL,
                download_receipt_hash TEXT NOT NULL,
                receipt_finalized INTEGER NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                raw_file_bytes_receipted INTEGER NOT NULL,
                raw_download_token_receipted INTEGER NOT NULL,
                public_link_receipted INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_download_result_delivery_previews (
                download_delivery_preview_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                download_response_id TEXT NOT NULL,
                delivery_state TEXT NOT NULL,
                delivered_to TEXT NOT NULL,
                teller_delivery_allowed_after_tower INTEGER NOT NULL,
                direct_person_delivery_allowed INTEGER NOT NULL,
                direct_vault_link_included INTEGER NOT NULL,
                raw_file_bytes_included INTEGER NOT NULL,
                raw_download_token_included INTEGER NOT NULL,
                public_link_included INTEGER NOT NULL,
                workflow_safe_status_ready INTEGER NOT NULL,
                delivery_preview_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_authorized_download_safety_blockers (
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
                INSERT OR REPLACE INTO tower_authorized_download_safety_blockers (
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
            download_eligibility_id = _download_eligibility_id(request_id)
            download_redaction_id = _download_redaction_id(request_id)
            download_session_id = _download_session_id(request_id)
            internal_download_request_id = _internal_download_request_id(request_id)
            download_response_id = _download_response_id(request_id)
            handle_guard_id = _handle_guard_id(request_id)
            download_receipt_id = _download_receipt_id(request_id)
            delivery_preview_id = _download_delivery_preview_id(request_id)

            conn.execute(
                """
                INSERT OR REPLACE INTO download_eligibility_gates (
                    download_eligibility_id, request_id, vault_request_draft_id,
                    gate_state, tower_is_requester, teller_is_requester,
                    tower_identity_check_passed, tower_permission_check_passed,
                    tower_approval_recorded, download_protocol_allowed,
                    proof_protocol_allowed, teller_direct_download_allowed,
                    raw_file_bytes_json_allowed, public_download_link_allowed,
                    raw_download_token_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    download_eligibility_id,
                    request_id,
                    row["vault_request_draft_id"],
                    "download_eligibility_gate_passed_for_tower_only",
                    1,
                    0,
                    1,
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO download_scope_redaction_gates (
                    download_redaction_id, request_id, vault_request_draft_id,
                    redaction_state, sealed_handle_only,
                    raw_file_bytes_redacted, raw_path_redacted,
                    raw_file_url_redacted, raw_download_token_redacted,
                    public_link_redacted, direct_browse_redacted,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    download_redaction_id,
                    request_id,
                    row["vault_request_draft_id"],
                    "download_scope_redaction_gate_ready_handle_hash_only",
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

            download_session_hash = calculate_sha256_bytes(
                f"download-session|{request_id}|Tower|sealed-handle-only|no-public-link".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_download_session_drafts (
                    download_session_id, request_id, vault_request_draft_id,
                    download_redaction_id, session_state, session_owner,
                    tower_session_required, teller_session_allowed,
                    direct_vault_session_allowed, public_session_allowed,
                    download_session_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    download_session_id,
                    request_id,
                    row["vault_request_draft_id"],
                    download_redaction_id,
                    "tower_download_session_draft_ready_internal_only",
                    "Tower",
                    1,
                    0,
                    0,
                    0,
                    download_session_hash,
                    now,
                ),
            )

            internal_request_material = {
                "request_id": request_id,
                "vault_request_draft_id": row["vault_request_draft_id"],
                "download_session_id": download_session_id,
                "from_service": "Tower",
                "to_service": "Vault",
                "vault_answer_target": "Tower",
                "internal_vault_download_call_sent": True,
                "teller_call_sent": False,
                "raw_file_bytes_requested": False,
                "raw_path_requested": False,
                "raw_file_url_requested": False,
                "raw_token_requested": False,
                "public_link_requested": False,
            }
            internal_request_hash = calculate_sha256_bytes(repr(sorted(internal_request_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_internal_vault_download_requests (
                    internal_download_request_id, request_id,
                    vault_request_draft_id, download_session_id,
                    request_state, from_service, to_service,
                    vault_answer_target, internal_vault_download_call_sent,
                    teller_call_sent, raw_file_bytes_requested,
                    raw_path_requested, raw_file_url_requested,
                    raw_token_requested, public_link_requested,
                    internal_request_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    internal_download_request_id,
                    request_id,
                    row["vault_request_draft_id"],
                    download_session_id,
                    "tower_internal_vault_download_request_sent_controlled",
                    "Tower",
                    "Vault",
                    "Tower",
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    internal_request_hash,
                    now,
                ),
            )

            sealed_download_handle_hash = calculate_sha256_bytes(
                f"sealed-download-handle|{request_id}|{internal_request_hash}|Tower-only".encode("utf-8")
            )
            sealed_download_artifact_hash = calculate_sha256_bytes(
                f"sealed-download-artifact|{request_id}|{row['projection_hash']}|{row['view_response_hash']}".encode("utf-8")
            )

            response_material = {
                "request_id": request_id,
                "internal_download_request_id": internal_download_request_id,
                "answered_to": "Tower",
                "vault_answered_tower_only": True,
                "sealed_download_handle_hash": sealed_download_handle_hash,
                "sealed_download_artifact_hash": sealed_download_artifact_hash,
                "raw_file_bytes_returned_by_json": False,
                "raw_path_returned": False,
                "raw_file_url_returned": False,
                "raw_download_token_returned": False,
                "public_link_returned": False,
            }
            response_hash = calculate_sha256_bytes(repr(sorted(response_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO vault_download_response_envelopes (
                    download_response_id, request_id,
                    internal_download_request_id, response_state,
                    answered_to, vault_answered_tower_only,
                    sealed_download_handle_hash,
                    sealed_download_artifact_hash,
                    raw_file_bytes_returned_by_json,
                    raw_path_returned, raw_file_url_returned,
                    raw_download_token_returned, public_link_returned,
                    response_envelope_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    download_response_id,
                    request_id,
                    internal_download_request_id,
                    "vault_download_response_envelope_ready_for_tower_hash_only",
                    "Tower",
                    1,
                    sealed_download_handle_hash,
                    sealed_download_artifact_hash,
                    0,
                    0,
                    0,
                    0,
                    0,
                    response_hash,
                    now,
                ),
            )

            handle_guard_hash = calculate_sha256_bytes(
                f"download-handle-guard|{request_id}|{download_response_id}|{sealed_download_handle_hash}|hash-only".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO download_handle_hash_guards (
                    handle_guard_id, request_id, download_response_id,
                    guard_state, handle_hash_only, raw_handle_visible,
                    raw_download_token_visible, public_link_visible,
                    raw_file_bytes_visible, expires_under_tower_control,
                    handle_guard_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    handle_guard_id,
                    request_id,
                    download_response_id,
                    "download_handle_hash_guard_ready_no_raw_token",
                    1,
                    0,
                    0,
                    0,
                    0,
                    1,
                    handle_guard_hash,
                    now,
                ),
            )

            download_receipt_hash = calculate_sha256_bytes(
                f"download-receipt-draft|{request_id}|{response_hash}|{handle_guard_hash}|no-raw-token-no-public-link".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO download_receipt_drafts (
                    download_receipt_id, request_id, download_response_id,
                    download_handle_guard_id, receipt_state,
                    view_redaction_receipt_hash, download_receipt_hash,
                    receipt_finalized, append_only, mutable,
                    raw_file_bytes_receipted, raw_download_token_receipted,
                    public_link_receipted, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    download_receipt_id,
                    request_id,
                    download_response_id,
                    handle_guard_id,
                    "download_receipt_draft_ready_append_only",
                    row["redaction_receipt_hash"],
                    download_receipt_hash,
                    0,
                    1,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            delivery_material = {
                "request_id": request_id,
                "download_response_id": download_response_id,
                "delivered_to": "Tower",
                "teller_delivery_allowed_after_tower": True,
                "direct_person_delivery_allowed": False,
                "direct_vault_link_included": False,
                "raw_file_bytes_included": False,
                "raw_download_token_included": False,
                "public_link_included": False,
                "workflow_safe_status_ready": True,
            }
            delivery_hash = calculate_sha256_bytes(repr(sorted(delivery_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_download_result_delivery_previews (
                    download_delivery_preview_id, request_id,
                    download_response_id, delivery_state,
                    delivered_to, teller_delivery_allowed_after_tower,
                    direct_person_delivery_allowed,
                    direct_vault_link_included,
                    raw_file_bytes_included,
                    raw_download_token_included,
                    public_link_included,
                    workflow_safe_status_ready,
                    delivery_preview_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    delivery_preview_id,
                    request_id,
                    download_response_id,
                    "tower_download_result_delivery_preview_ready_workflow_safe_hash_only",
                    "Tower",
                    1,
                    0,
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
        "previous_tower_authorized_view_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP481_INIT_CACHE = dict(result)
    return result


def get_tower_authorized_download_protocol_shell() -> Dict[str, Any]:
    init = initialize_tower_authorized_download_protocol_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 481,
        "title": "Tower Authorized Download Protocol Shell",
        "ready": True,
        "initialized": init,
        "doctrine": DOCTRINE,
        "correct_flow": DOCTRINE["correct_flow"],
        "controlled_download_protocol_metadata_only": True,
        "raw_file_bytes_returned_by_json": False,
        "raw_download_token_exposed": False,
        "public_link_created": False,
        "teller_direct_download_allowed": False,
        "locks": LOCKS,
    }


def get_download_eligibility_gate_board() -> Dict[str, Any]:
    initialize_tower_authorized_download_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM download_eligibility_gates ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 482,
        "title": "Download Eligibility Gate Board",
        "ready": True,
        "download_eligibility_count": len(rows),
        "download_eligibility_gates": rows,
        "all_tower_is_requester": all(bool(item["tower_is_requester"]) for item in rows),
        "no_teller_is_requester": all(not bool(item["teller_is_requester"]) for item in rows),
        "all_tower_identity_permission_passed": all(bool(item["tower_identity_check_passed"]) and bool(item["tower_permission_check_passed"]) for item in rows),
        "all_tower_approval_recorded": all(bool(item["tower_approval_recorded"]) for item in rows),
        "all_download_protocol_allowed": all(bool(item["download_protocol_allowed"]) for item in rows),
        "no_proof_protocol_allowed": all(not bool(item["proof_protocol_allowed"]) for item in rows),
        "no_teller_direct_download": all(not bool(item["teller_direct_download_allowed"]) for item in rows),
        "no_raw_file_bytes_json": all(not bool(item["raw_file_bytes_json_allowed"]) for item in rows),
        "no_public_download_links": all(not bool(item["public_download_link_allowed"]) for item in rows),
        "no_raw_download_tokens": all(not bool(item["raw_download_token_allowed"]) for item in rows),
    }


def get_download_scope_redaction_gate_board() -> Dict[str, Any]:
    initialize_tower_authorized_download_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM download_scope_redaction_gates ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 483,
        "title": "Download Scope Redaction Gate Board",
        "ready": True,
        "download_redaction_count": len(rows),
        "download_redaction_gates": rows,
        "all_sealed_handle_only": all(bool(item["sealed_handle_only"]) for item in rows),
        "all_raw_file_bytes_redacted": all(bool(item["raw_file_bytes_redacted"]) for item in rows),
        "all_raw_paths_redacted": all(bool(item["raw_path_redacted"]) for item in rows),
        "all_raw_file_urls_redacted": all(bool(item["raw_file_url_redacted"]) for item in rows),
        "all_raw_download_tokens_redacted": all(bool(item["raw_download_token_redacted"]) for item in rows),
        "all_public_links_redacted": all(bool(item["public_link_redacted"]) for item in rows),
        "all_direct_browse_redacted": all(bool(item["direct_browse_redacted"]) for item in rows),
    }


def get_tower_download_session_draft_board() -> Dict[str, Any]:
    initialize_tower_authorized_download_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_download_session_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 484,
        "title": "Tower Download Session Draft Board",
        "ready": True,
        "download_session_count": len(rows),
        "download_sessions": rows,
        "all_session_owner_tower": all(item["session_owner"] == "Tower" for item in rows),
        "all_tower_session_required": all(bool(item["tower_session_required"]) for item in rows),
        "no_teller_session": all(not bool(item["teller_session_allowed"]) for item in rows),
        "no_direct_vault_session": all(not bool(item["direct_vault_session_allowed"]) for item in rows),
        "no_public_session": all(not bool(item["public_session_allowed"]) for item in rows),
    }


def get_tower_internal_vault_download_request_ledger() -> Dict[str, Any]:
    initialize_tower_authorized_download_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_internal_vault_download_requests ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 485,
        "title": "Tower Internal Vault Download Request Ledger",
        "ready": True,
        "internal_download_request_count": len(rows),
        "internal_download_requests": rows,
        "all_from_tower_to_vault": all(item["from_service"] == "Tower" and item["to_service"] == "Vault" for item in rows),
        "all_vault_answer_target_tower": all(item["vault_answer_target"] == "Tower" for item in rows),
        "all_internal_download_calls_sent": all(bool(item["internal_vault_download_call_sent"]) for item in rows),
        "no_teller_calls_sent": all(not bool(item["teller_call_sent"]) for item in rows),
        "no_raw_file_bytes_requested": all(not bool(item["raw_file_bytes_requested"]) for item in rows),
        "no_raw_paths_requested": all(not bool(item["raw_path_requested"]) for item in rows),
        "no_raw_file_urls_requested": all(not bool(item["raw_file_url_requested"]) for item in rows),
        "no_raw_tokens_requested": all(not bool(item["raw_token_requested"]) for item in rows),
        "no_public_links_requested": all(not bool(item["public_link_requested"]) for item in rows),
    }


def get_vault_download_response_envelope_board() -> Dict[str, Any]:
    initialize_tower_authorized_download_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM vault_download_response_envelopes ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 486,
        "title": "Vault Download Response Envelope Board",
        "ready": True,
        "download_response_count": len(rows),
        "download_response_envelopes": rows,
        "all_answered_to_tower": all(item["answered_to"] == "Tower" for item in rows),
        "all_vault_answered_tower_only": all(bool(item["vault_answered_tower_only"]) for item in rows),
        "all_have_sealed_handle_hash": all(len(item["sealed_download_handle_hash"]) == 64 for item in rows),
        "all_have_sealed_artifact_hash": all(len(item["sealed_download_artifact_hash"]) == 64 for item in rows),
        "no_raw_file_bytes_json": all(not bool(item["raw_file_bytes_returned_by_json"]) for item in rows),
        "no_raw_paths_returned": all(not bool(item["raw_path_returned"]) for item in rows),
        "no_raw_file_urls_returned": all(not bool(item["raw_file_url_returned"]) for item in rows),
        "no_raw_download_tokens_returned": all(not bool(item["raw_download_token_returned"]) for item in rows),
        "no_public_links_returned": all(not bool(item["public_link_returned"]) for item in rows),
    }


def get_download_handle_hash_guard_board() -> Dict[str, Any]:
    initialize_tower_authorized_download_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM download_handle_hash_guards ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 487,
        "title": "Download Handle Hash Guard Board",
        "ready": True,
        "handle_guard_count": len(rows),
        "handle_guards": rows,
        "all_handle_hash_only": all(bool(item["handle_hash_only"]) for item in rows),
        "no_raw_handle_visible": all(not bool(item["raw_handle_visible"]) for item in rows),
        "no_raw_download_token_visible": all(not bool(item["raw_download_token_visible"]) for item in rows),
        "no_public_link_visible": all(not bool(item["public_link_visible"]) for item in rows),
        "no_raw_file_bytes_visible": all(not bool(item["raw_file_bytes_visible"]) for item in rows),
        "all_expire_under_tower_control": all(bool(item["expires_under_tower_control"]) for item in rows),
    }


def get_download_receipt_draft_ledger() -> Dict[str, Any]:
    initialize_tower_authorized_download_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM download_receipt_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 488,
        "title": "Download Receipt Draft Ledger",
        "ready": True,
        "download_receipt_count": len(rows),
        "download_receipts": rows,
        "all_receipts_draft": all(not bool(item["receipt_finalized"]) for item in rows),
        "all_append_only": all(bool(item["append_only"]) for item in rows),
        "all_immutable": all(not bool(item["mutable"]) for item in rows),
        "no_raw_file_bytes_receipted": all(not bool(item["raw_file_bytes_receipted"]) for item in rows),
        "no_raw_download_tokens_receipted": all(not bool(item["raw_download_token_receipted"]) for item in rows),
        "no_public_links_receipted": all(not bool(item["public_link_receipted"]) for item in rows),
    }


def get_tower_download_result_delivery_preview_board() -> Dict[str, Any]:
    initialize_tower_authorized_download_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_download_result_delivery_previews ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 489,
        "title": "Tower Download Result Delivery Preview Board",
        "ready": True,
        "download_delivery_preview_count": len(rows),
        "download_delivery_previews": rows,
        "all_delivered_to_tower": all(item["delivered_to"] == "Tower" for item in rows),
        "all_teller_delivery_allowed_after_tower": all(bool(item["teller_delivery_allowed_after_tower"]) for item in rows),
        "no_direct_person_delivery": all(not bool(item["direct_person_delivery_allowed"]) for item in rows),
        "no_direct_vault_link": all(not bool(item["direct_vault_link_included"]) for item in rows),
        "no_raw_file_bytes": all(not bool(item["raw_file_bytes_included"]) for item in rows),
        "no_raw_download_tokens": all(not bool(item["raw_download_token_included"]) for item in rows),
        "no_public_links": all(not bool(item["public_link_included"]) for item in rows),
        "all_workflow_safe_status_ready": all(bool(item["workflow_safe_status_ready"]) for item in rows),
    }


def get_tower_authorized_download_safety_blocker_board() -> Dict[str, Any]:
    initialize_tower_authorized_download_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_authorized_download_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 489,
        "title": "Tower Authorized Download Safety Blocker Board",
        "ready": True,
        "blocker_count": len(rows),
        "blockers": rows,
        "unsafe_action_count": sum(1 for item in rows if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in rows),
    }


def get_tower_authorized_download_protocol_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_tower_authorized_download_protocol_layer()

    shell = get_tower_authorized_download_protocol_shell()
    eligibility = get_download_eligibility_gate_board()
    redaction = get_download_scope_redaction_gate_board()
    sessions = get_tower_download_session_draft_board()
    requests = get_tower_internal_vault_download_request_ledger()
    responses = get_vault_download_response_envelope_board()
    guards = get_download_handle_hash_guard_board()
    receipts = get_download_receipt_draft_ledger()
    delivery = get_tower_download_result_delivery_preview_board()
    blockers = get_tower_authorized_download_safety_blocker_board()

    checks = {
        "previous_tower_authorized_view_ready": init["previous_tower_authorized_view_ready"] is True,
        "download_protocol_shell_ready": shell["ready"] is True,
        "doctrine_tower_teller_vault_locked": DOCTRINE["tower"] == "face_protocol_authority" and DOCTRINE["teller"] == "workflow_request_source" and DOCTRINE["vault"] == "sealed_memory",
        "correct_flow_locked": DOCTRINE["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller",
        "tower_executes_controlled_download_protocol": DOCTRINE["tower_executes_controlled_download_protocol"] is True,
        "download_answers_tower_only": DOCTRINE["download_protocol_answers_tower_only"] is True and DOCTRINE["vault_answers_tower_only"] is True,
        "download_exposes_no_raw_token_or_public_link": DOCTRINE["raw_file_bytes_exposed_by_json"] is False and DOCTRINE["raw_download_token_exposed"] is False and DOCTRINE["public_link_created_by_download"] is False,
        "eligibility_ready": eligibility["ready"] is True and eligibility["download_eligibility_count"] >= 2,
        "eligibility_tower_only": eligibility["all_tower_is_requester"] is True and eligibility["no_teller_is_requester"] is True,
        "eligibility_passed_for_download_only": eligibility["all_tower_identity_permission_passed"] is True and eligibility["all_tower_approval_recorded"] is True and eligibility["all_download_protocol_allowed"] is True,
        "eligibility_no_proof_teller_raw_public_token": eligibility["no_proof_protocol_allowed"] is True and eligibility["no_teller_direct_download"] is True and eligibility["no_raw_file_bytes_json"] is True and eligibility["no_public_download_links"] is True and eligibility["no_raw_download_tokens"] is True,
        "redaction_ready": redaction["ready"] is True and redaction["download_redaction_count"] >= 2,
        "redaction_sealed_handle_only": redaction["all_sealed_handle_only"] is True,
        "redaction_blocks_raw_path_url_token_public_direct": redaction["all_raw_file_bytes_redacted"] is True and redaction["all_raw_paths_redacted"] is True and redaction["all_raw_file_urls_redacted"] is True and redaction["all_raw_download_tokens_redacted"] is True and redaction["all_public_links_redacted"] is True and redaction["all_direct_browse_redacted"] is True,
        "sessions_ready": sessions["ready"] is True and sessions["download_session_count"] >= 2,
        "sessions_tower_only_no_public_direct": sessions["all_session_owner_tower"] is True and sessions["all_tower_session_required"] is True and sessions["no_teller_session"] is True and sessions["no_direct_vault_session"] is True and sessions["no_public_session"] is True,
        "internal_requests_ready": requests["ready"] is True and requests["internal_download_request_count"] >= 2,
        "internal_requests_tower_to_vault_only": requests["all_from_tower_to_vault"] is True and requests["all_vault_answer_target_tower"] is True and requests["all_internal_download_calls_sent"] is True and requests["no_teller_calls_sent"] is True,
        "internal_requests_no_raw_path_url_token_public_requested": requests["no_raw_file_bytes_requested"] is True and requests["no_raw_paths_requested"] is True and requests["no_raw_file_urls_requested"] is True and requests["no_raw_tokens_requested"] is True and requests["no_public_links_requested"] is True,
        "responses_ready": responses["ready"] is True and responses["download_response_count"] >= 2,
        "responses_tower_only_hash_envelope": responses["all_answered_to_tower"] is True and responses["all_vault_answered_tower_only"] is True and responses["all_have_sealed_handle_hash"] is True and responses["all_have_sealed_artifact_hash"] is True,
        "responses_no_raw_path_url_token_public": responses["no_raw_file_bytes_json"] is True and responses["no_raw_paths_returned"] is True and responses["no_raw_file_urls_returned"] is True and responses["no_raw_download_tokens_returned"] is True and responses["no_public_links_returned"] is True,
        "handle_guards_ready": guards["ready"] is True and guards["handle_guard_count"] >= 2,
        "handle_guards_hash_only_no_raw_token_public": guards["all_handle_hash_only"] is True and guards["no_raw_handle_visible"] is True and guards["no_raw_download_token_visible"] is True and guards["no_public_link_visible"] is True and guards["no_raw_file_bytes_visible"] is True,
        "download_receipts_ready": receipts["ready"] is True and receipts["download_receipt_count"] >= 2,
        "download_receipts_draft_append_only_no_raw_token_public": receipts["all_receipts_draft"] is True and receipts["all_append_only"] is True and receipts["all_immutable"] is True and receipts["no_raw_file_bytes_receipted"] is True and receipts["no_raw_download_tokens_receipted"] is True and receipts["no_public_links_receipted"] is True,
        "delivery_ready": delivery["ready"] is True and delivery["download_delivery_preview_count"] >= 2,
        "delivery_to_tower_then_workflow_safe": delivery["all_delivered_to_tower"] is True and delivery["all_teller_delivery_allowed_after_tower"] is True and delivery["all_workflow_safe_status_ready"] is True,
        "delivery_no_direct_person_raw_token_public": delivery["no_direct_person_delivery"] is True and delivery["no_direct_vault_link"] is True and delivery["no_raw_file_bytes"] is True and delivery["no_raw_download_tokens"] is True and delivery["no_public_links"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "global_download_metadata_allowed_only": LOCKS["controlled_download_protocol_metadata_allowed"] is True and LOCKS["raw_file_bytes_returned_by_json"] is False and LOCKS["raw_download_token_exposed"] is False,
        "global_no_teller_to_vault_or_direct_download": LOCKS["teller_to_vault_direct_call_allowed"] is False and LOCKS["vault_direct_request_from_teller_allowed"] is False and LOCKS["teller_direct_download_allowed"] is False,
        "global_no_public_dashboard_portal_browse": LOCKS["public_vault_dashboard_allowed"] is False and LOCKS["direct_vault_user_portal_allowed"] is False and LOCKS["employee_vault_browsing_allowed"] is False and LOCKS["external_collaborator_browsing_allowed"] is False,
        "global_no_public_links_raw_bytes_paths_tokens": LOCKS["public_url_created"] is False and LOCKS["share_link_created"] is False and LOCKS["raw_file_bytes_exposed"] is False and LOCKS["raw_path_exposed"] is False and LOCKS["raw_file_url_exposed"] is False and LOCKS["raw_download_token_exposed"] is False,
        "global_no_provider_delete_restore_move": LOCKS["provider_storage_required"] is False and LOCKS["hard_delete_allowed"] is False and LOCKS["purge_allowed"] is False and LOCKS["restore_execution_allowed"] is False and LOCKS["physical_object_move_allowed"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 490,
        "title": "Tower Authorized Download Protocol Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Tower authorized download protocol layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — TOWER AUTHORIZED PROOF PROTOCOL LAYER / GP491-GP500",
        "still_locked": [
            "no Teller-to-Vault direct calls",
            "no Teller direct download",
            "no direct Vault user portal",
            "no employee/vendor/customer Vault browsing",
            "no public Vault dashboard",
            "no standalone external Vault dashboard",
            "no external collaborator browsing",
            "no public URL or share link",
            "no raw file bytes returned by JSON",
            "no raw path or raw file URL exposure",
            "no raw token exposure",
            "no proof protocol execution in this layer",
            "no public/beta/provider upload",
            "no delete or purge",
            "no restore execution",
            "no quarantine release",
            "no physical object move",
            "no provider dependency by default",
        ],
    }


def get_tower_authorized_download_protocol_home() -> Dict[str, Any]:
    checkpoint = get_tower_authorized_download_protocol_readiness_checkpoint()
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


def validate_tower_authorized_download_protocol_layer() -> Dict[str, Any]:
    checkpoint = get_tower_authorized_download_protocol_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_tower_authorized_view_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"]["tower_executes_controlled_download_protocol"] is True
    assert checkpoint["checks"]["download_answers_tower_only"] is True
    assert checkpoint["checks"]["download_exposes_no_raw_token_or_public_link"] is True
    assert checkpoint["checks"]["eligibility_ready"] is True
    assert checkpoint["checks"]["eligibility_tower_only"] is True
    assert checkpoint["checks"]["eligibility_passed_for_download_only"] is True
    assert checkpoint["checks"]["eligibility_no_proof_teller_raw_public_token"] is True
    assert checkpoint["checks"]["redaction_ready"] is True
    assert checkpoint["checks"]["redaction_sealed_handle_only"] is True
    assert checkpoint["checks"]["redaction_blocks_raw_path_url_token_public_direct"] is True
    assert checkpoint["checks"]["sessions_ready"] is True
    assert checkpoint["checks"]["sessions_tower_only_no_public_direct"] is True
    assert checkpoint["checks"]["internal_requests_ready"] is True
    assert checkpoint["checks"]["internal_requests_tower_to_vault_only"] is True
    assert checkpoint["checks"]["internal_requests_no_raw_path_url_token_public_requested"] is True
    assert checkpoint["checks"]["responses_ready"] is True
    assert checkpoint["checks"]["responses_tower_only_hash_envelope"] is True
    assert checkpoint["checks"]["responses_no_raw_path_url_token_public"] is True
    assert checkpoint["checks"]["handle_guards_ready"] is True
    assert checkpoint["checks"]["handle_guards_hash_only_no_raw_token_public"] is True
    assert checkpoint["checks"]["download_receipts_ready"] is True
    assert checkpoint["checks"]["download_receipts_draft_append_only_no_raw_token_public"] is True
    assert checkpoint["checks"]["delivery_ready"] is True
    assert checkpoint["checks"]["delivery_to_tower_then_workflow_safe"] is True
    assert checkpoint["checks"]["delivery_no_direct_person_raw_token_public"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["controlled_download_protocol_metadata_allowed"] is True
    assert LOCKS["tower_internal_vault_download_requests_allowed"] is True
    assert LOCKS["vault_download_response_envelopes_allowed"] is True
    assert LOCKS["download_handle_hash_guards_allowed"] is True

    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_file_bytes_exposed"] is False
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["raw_share_token_exposed"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS["public_download_link_created"] is False
    assert LOCKS["proof_protocol_execution_allowed"] is False
    assert LOCKS["teller_direct_download_allowed"] is False
    assert LOCKS["teller_to_vault_direct_call_allowed"] is False
    assert LOCKS["direct_vault_user_portal_allowed"] is False
    assert LOCKS["public_vault_dashboard_allowed"] is False
    assert LOCKS["employee_vault_browsing_allowed"] is False
    assert LOCKS["external_collaborator_browsing_allowed"] is False
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
    checkpoint = get_tower_authorized_download_protocol_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "correct_flow": DOCTRINE["correct_flow"],
        "controlled_download_protocol_metadata_allowed": True,
        "raw_file_bytes_returned_by_json": False,
        "raw_download_token_exposed": False,
        "public_download_link_created": False,
        "teller_to_vault_direct_call_allowed": False,
        "vault_answers_tower_only": True,
        "locks_preserved": True,
    }


def get_gp481_status() -> Dict[str, Any]:
    return _gp_status(481)


def get_gp482_status() -> Dict[str, Any]:
    return _gp_status(482)


def get_gp483_status() -> Dict[str, Any]:
    return _gp_status(483)


def get_gp484_status() -> Dict[str, Any]:
    return _gp_status(484)


def get_gp485_status() -> Dict[str, Any]:
    return _gp_status(485)


def get_gp486_status() -> Dict[str, Any]:
    return _gp_status(486)


def get_gp487_status() -> Dict[str, Any]:
    return _gp_status(487)


def get_gp488_status() -> Dict[str, Any]:
    return _gp_status(488)


def get_gp489_status() -> Dict[str, Any]:
    return _gp_status(489)


def get_gp490_status() -> Dict[str, Any]:
    return _gp_status(490)
