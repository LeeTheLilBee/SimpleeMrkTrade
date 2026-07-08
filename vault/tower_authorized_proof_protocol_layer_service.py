
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — TOWER AUTHORIZED PROOF PROTOCOL LAYER / GP491-GP500"
LAYER_ID = "vault_gp491_500_tower_authorized_proof_protocol_layer"
READINESS_LABEL = "Tower authorized proof protocol layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_tower_authorized_proof_protocol_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.tower_authorized_download_protocol_layer_service import (
        get_download_eligibility_gate_board,
        get_download_scope_redaction_gate_board,
        get_tower_internal_vault_download_request_ledger,
        get_vault_download_response_envelope_board,
        get_download_handle_hash_guard_board,
        get_download_receipt_draft_ledger,
        get_tower_download_result_delivery_preview_board,
        validate_tower_authorized_download_protocol_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP491-GP500 requires GP481-GP490 Tower authorized download protocol layer first."
    ) from exc


_GP491_INIT_CACHE = None

DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": "Teller -> Tower -> Vault -> Tower -> Teller",
    "tower_executes_controlled_proof_protocol": True,
    "proof_protocol_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
    "teller_can_request_proof_directly_from_vault": False,
    "vault_answers_tower_only": True,
    "proof_packet_hash_only": True,
    "raw_file_bytes_exposed_by_proof": False,
    "raw_download_token_exposed_by_proof": False,
    "public_link_created_by_proof": False,
}

LOCKS = {
    "tower_authorized_proof_protocol_layer": True,
    "controlled_proof_protocol_allowed": True,
    "tower_internal_vault_proof_requests_allowed": True,
    "vault_proof_response_envelopes_allowed": True,
    "proof_packet_hashes_allowed": True,
    "proof_receipt_drafts_allowed": True,
    "tower_proof_result_delivery_previews_allowed": True,

    "raw_file_bytes_returned_by_json": False,
    "raw_file_bytes_exposed": False,
    "raw_download_token_exposed": False,
    "raw_share_token_exposed": False,
    "raw_path_exposed": False,
    "raw_file_url_exposed": False,
    "public_download_link_created": False,
    "public_proof_link_created": False,
    "public_view_link_allowed": False,
    "teller_direct_proof_allowed": False,
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
    {"gp": 491, "title": "Tower Authorized Proof Protocol Shell", "status": "ready", "route": "/vault/tower-authorized-proof-protocol-shell.json"},
    {"gp": 492, "title": "Proof Eligibility Gate Board", "status": "ready", "route": "/vault/proof-eligibility-gate-board.json"},
    {"gp": 493, "title": "Proof Scope Redaction Gate Board", "status": "ready", "route": "/vault/proof-scope-redaction-gate-board.json"},
    {"gp": 494, "title": "Tower Internal Vault Proof Request Ledger", "status": "ready", "route": "/vault/tower-internal-vault-proof-request-ledger.json"},
    {"gp": 495, "title": "Vault Proof Response Envelope Board", "status": "ready", "route": "/vault/vault-proof-response-envelope-board.json"},
    {"gp": 496, "title": "Proof Packet Hash Builder", "status": "ready", "route": "/vault/proof-packet-hash-builder.json"},
    {"gp": 497, "title": "Proof Receipt Draft Ledger", "status": "ready", "route": "/vault/proof-receipt-draft-ledger.json"},
    {"gp": 498, "title": "Tower Proof Result Delivery Preview Board", "status": "ready", "route": "/vault/tower-proof-result-delivery-preview-board.json"},
    {"gp": 499, "title": "Tower Authorized Proof Safety Blocker Board", "status": "ready", "route": "/vault/tower-authorized-proof-safety-blocker-board.json"},
    {"gp": 500, "title": "Tower Authorized Proof Protocol Readiness Checkpoint", "status": "ready", "route": "/vault/tower-authorized-proof-protocol-readiness-checkpoint.json"},
]

BLOCKERS = [
    {"blocker_id": "no_teller_direct_proof", "blocked_action": "teller_direct_proof_call_to_vault", "allowed": False, "reason": "Tower owns proof protocol."},
    {"blocker_id": "no_teller_to_vault_direct_call", "blocked_action": "teller_to_vault_direct_call", "allowed": False, "reason": "Teller requests must go through Tower."},
    {"blocker_id": "no_raw_file_bytes_json", "blocked_action": "raw_file_bytes_returned_by_json", "allowed": False, "reason": "Proof protocol returns proof hashes and receipts, not file bytes."},
    {"blocker_id": "no_raw_download_token", "blocked_action": "raw_download_token_exposure", "allowed": False, "reason": "Proof packets never expose raw tokens."},
    {"blocker_id": "no_public_proof_link", "blocked_action": "public_proof_link", "allowed": False, "reason": "Proof packets are Tower-controlled outputs, not public links."},
    {"blocker_id": "no_raw_path_or_url", "blocked_action": "raw_path_or_file_url_exposure", "allowed": False, "reason": "Proof envelopes do not expose paths or URLs."},
    {"blocker_id": "no_public_download_link", "blocked_action": "public_download_link", "allowed": False, "reason": "Proof layer does not create public download links."},
    {"blocker_id": "no_public_vault_dashboard", "blocked_action": "public_vault_dashboard", "allowed": False, "reason": "Tower is the face; Vault remains headless."},
    {"blocker_id": "no_direct_vault_user_portal", "blocked_action": "direct_vault_user_portal", "allowed": False, "reason": "People do not enter Vault directly."},
    {"blocker_id": "no_employee_vendor_customer_browse", "blocked_action": "employee_vendor_customer_vault_browsing", "allowed": False, "reason": "Teller receives Tower-safe proof outputs only."},
    {"blocker_id": "no_external_collaborator_browse", "blocked_action": "external_collaborator_browsing", "allowed": False, "reason": "No shared-drive behavior."},
    {"blocker_id": "no_provider_dependency", "blocked_action": "provider_dependency", "allowed": False, "reason": "Local-first sealed memory remains default."},
    {"blocker_id": "no_delete_restore_move", "blocked_action": "delete_restore_physical_move", "allowed": False, "reason": "Proof protocol does not mutate Vault lifecycle state or move objects."},
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


def _proof_eligibility_id(request_id: str) -> str:
    return "proof_eligibility_gate_" + calculate_sha256_bytes(("proof_eligibility|" + request_id).encode("utf-8"))[:24]


def _proof_redaction_id(request_id: str) -> str:
    return "proof_scope_redaction_gate_" + calculate_sha256_bytes(("proof_redaction|" + request_id).encode("utf-8"))[:24]


def _internal_proof_request_id(request_id: str) -> str:
    return "tower_internal_vault_proof_request_" + calculate_sha256_bytes(("internal_proof_request|" + request_id).encode("utf-8"))[:24]


def _proof_response_id(request_id: str) -> str:
    return "vault_proof_response_envelope_" + calculate_sha256_bytes(("proof_response|" + request_id).encode("utf-8"))[:24]


def _proof_packet_id(request_id: str) -> str:
    return "proof_packet_hash_" + calculate_sha256_bytes(("proof_packet|" + request_id).encode("utf-8"))[:24]


def _proof_receipt_id(request_id: str) -> str:
    return "proof_receipt_draft_" + calculate_sha256_bytes(("proof_receipt|" + request_id).encode("utf-8"))[:24]


def _proof_delivery_preview_id(request_id: str) -> str:
    return "tower_proof_result_delivery_preview_" + calculate_sha256_bytes(("proof_delivery|" + request_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    eligibility = get_download_eligibility_gate_board().get("download_eligibility_gates", [])
    redaction = get_download_scope_redaction_gate_board().get("download_redaction_gates", [])
    download_requests = get_tower_internal_vault_download_request_ledger().get("internal_download_requests", [])
    download_responses = get_vault_download_response_envelope_board().get("download_response_envelopes", [])
    handle_guards = get_download_handle_hash_guard_board().get("handle_guards", [])
    download_receipts = get_download_receipt_draft_ledger().get("download_receipts", [])
    delivery = get_tower_download_result_delivery_preview_board().get("download_delivery_previews", [])

    redaction_by_request = {row["request_id"]: row for row in redaction}
    download_request_by_request = {row["request_id"]: row for row in download_requests}
    download_response_by_request = {row["request_id"]: row for row in download_responses}
    handle_guard_by_request = {row["request_id"]: row for row in handle_guards}
    download_receipt_by_request = {row["request_id"]: row for row in download_receipts}
    delivery_by_request = {row["request_id"]: row for row in delivery}

    rows = []
    for eligible in eligibility:
        request_id = eligible["request_id"]
        redaction_row = redaction_by_request.get(request_id, {})
        download_request = download_request_by_request.get(request_id, {})
        download_response = download_response_by_request.get(request_id, {})
        handle_guard = handle_guard_by_request.get(request_id, {})
        download_receipt = download_receipt_by_request.get(request_id, {})
        delivery_row = delivery_by_request.get(request_id, {})

        rows.append(
            {
                "request_id": request_id,
                "vault_request_draft_id": eligible["vault_request_draft_id"],
                "tower_is_requester": bool(eligible.get("tower_is_requester", 1)),
                "teller_is_requester": bool(eligible.get("teller_is_requester", 0)),
                "tower_identity_check_passed": bool(eligible.get("tower_identity_check_passed", 1)),
                "tower_permission_check_passed": bool(eligible.get("tower_permission_check_passed", 1)),
                "tower_approval_recorded": bool(eligible.get("tower_approval_recorded", 1)),
                "download_protocol_allowed": bool(eligible.get("download_protocol_allowed", 1)),
                "proof_protocol_allowed_from_prior": bool(eligible.get("proof_protocol_allowed", 0)),
                "teller_direct_download_allowed": bool(eligible.get("teller_direct_download_allowed", 0)),
                "raw_file_bytes_json_allowed": bool(eligible.get("raw_file_bytes_json_allowed", 0)),
                "public_download_link_allowed": bool(eligible.get("public_download_link_allowed", 0)),
                "raw_download_token_allowed": bool(eligible.get("raw_download_token_allowed", 0)),
                "download_redaction_id": redaction_row.get("download_redaction_id", "missing_download_redaction"),
                "sealed_handle_only": bool(redaction_row.get("sealed_handle_only", 1)),
                "raw_file_bytes_redacted": bool(redaction_row.get("raw_file_bytes_redacted", 1)),
                "raw_path_redacted": bool(redaction_row.get("raw_path_redacted", 1)),
                "raw_file_url_redacted": bool(redaction_row.get("raw_file_url_redacted", 1)),
                "raw_download_token_redacted": bool(redaction_row.get("raw_download_token_redacted", 1)),
                "public_link_redacted": bool(redaction_row.get("public_link_redacted", 1)),
                "direct_browse_redacted": bool(redaction_row.get("direct_browse_redacted", 1)),
                "internal_download_request_id": download_request.get("internal_download_request_id", "missing_internal_download_request"),
                "download_response_id": download_response.get("download_response_id", "missing_download_response"),
                "sealed_download_handle_hash": download_response.get("sealed_download_handle_hash", "missing_handle_hash"),
                "sealed_download_artifact_hash": download_response.get("sealed_download_artifact_hash", "missing_artifact_hash"),
                "download_response_hash": download_response.get("response_envelope_hash", "missing_download_response_hash"),
                "vault_answered_tower_only": bool(download_response.get("vault_answered_tower_only", 1)),
                "handle_guard_id": handle_guard.get("handle_guard_id", "missing_handle_guard"),
                "handle_guard_hash": handle_guard.get("handle_guard_hash", "missing_handle_guard_hash"),
                "download_receipt_id": download_receipt.get("download_receipt_id", "missing_download_receipt"),
                "download_receipt_hash": download_receipt.get("download_receipt_hash", "missing_download_receipt_hash"),
                "delivery_preview_id": delivery_row.get("download_delivery_preview_id", "missing_download_delivery_preview"),
                "workflow_safe_status_ready": bool(delivery_row.get("workflow_safe_status_ready", 1)),
            }
        )
    return rows


def initialize_tower_authorized_proof_protocol_layer() -> Dict[str, Any]:
    global _GP491_INIT_CACHE
    if _GP491_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP491_INIT_CACHE)

    previous = validate_tower_authorized_download_protocol_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS proof_eligibility_gates (
                proof_eligibility_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                vault_request_draft_id TEXT NOT NULL,
                gate_state TEXT NOT NULL,
                tower_is_requester INTEGER NOT NULL,
                teller_is_requester INTEGER NOT NULL,
                tower_identity_check_passed INTEGER NOT NULL,
                tower_permission_check_passed INTEGER NOT NULL,
                tower_approval_recorded INTEGER NOT NULL,
                proof_protocol_allowed INTEGER NOT NULL,
                teller_direct_proof_allowed INTEGER NOT NULL,
                raw_file_bytes_json_allowed INTEGER NOT NULL,
                public_proof_link_allowed INTEGER NOT NULL,
                raw_token_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS proof_scope_redaction_gates (
                proof_redaction_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                vault_request_draft_id TEXT NOT NULL,
                redaction_state TEXT NOT NULL,
                proof_hash_only INTEGER NOT NULL,
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
            CREATE TABLE IF NOT EXISTS tower_internal_vault_proof_requests (
                internal_proof_request_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                vault_request_draft_id TEXT NOT NULL,
                request_state TEXT NOT NULL,
                from_service TEXT NOT NULL,
                to_service TEXT NOT NULL,
                vault_answer_target TEXT NOT NULL,
                internal_vault_proof_call_sent INTEGER NOT NULL,
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
            CREATE TABLE IF NOT EXISTS vault_proof_response_envelopes (
                proof_response_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                internal_proof_request_id TEXT NOT NULL,
                response_state TEXT NOT NULL,
                answered_to TEXT NOT NULL,
                vault_answered_tower_only INTEGER NOT NULL,
                proof_integrity_hash TEXT NOT NULL,
                proof_subject_hash TEXT NOT NULL,
                proof_receipt_reference_hash TEXT NOT NULL,
                raw_file_bytes_returned_by_json INTEGER NOT NULL,
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
            CREATE TABLE IF NOT EXISTS proof_packet_hashes (
                proof_packet_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                proof_response_id TEXT NOT NULL,
                packet_state TEXT NOT NULL,
                proof_packet_hash TEXT NOT NULL,
                proof_integrity_hash TEXT NOT NULL,
                sealed_download_artifact_hash TEXT NOT NULL,
                download_receipt_hash TEXT NOT NULL,
                handle_guard_hash TEXT NOT NULL,
                raw_file_bytes_included INTEGER NOT NULL,
                raw_path_included INTEGER NOT NULL,
                raw_file_url_included INTEGER NOT NULL,
                raw_token_included INTEGER NOT NULL,
                public_link_included INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS proof_receipt_drafts (
                proof_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                proof_packet_id TEXT NOT NULL,
                proof_response_id TEXT NOT NULL,
                receipt_state TEXT NOT NULL,
                proof_receipt_hash TEXT NOT NULL,
                receipt_finalized INTEGER NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                raw_file_bytes_receipted INTEGER NOT NULL,
                raw_token_receipted INTEGER NOT NULL,
                public_link_receipted INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_proof_result_delivery_previews (
                proof_delivery_preview_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                proof_response_id TEXT NOT NULL,
                proof_packet_id TEXT NOT NULL,
                delivery_state TEXT NOT NULL,
                delivered_to TEXT NOT NULL,
                teller_delivery_allowed_after_tower INTEGER NOT NULL,
                direct_person_delivery_allowed INTEGER NOT NULL,
                direct_vault_link_included INTEGER NOT NULL,
                raw_file_bytes_included INTEGER NOT NULL,
                raw_token_included INTEGER NOT NULL,
                public_link_included INTEGER NOT NULL,
                workflow_safe_proof_status_ready INTEGER NOT NULL,
                delivery_preview_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_authorized_proof_safety_blockers (
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
                INSERT OR REPLACE INTO tower_authorized_proof_safety_blockers (
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
            proof_eligibility_id = _proof_eligibility_id(request_id)
            proof_redaction_id = _proof_redaction_id(request_id)
            internal_proof_request_id = _internal_proof_request_id(request_id)
            proof_response_id = _proof_response_id(request_id)
            proof_packet_id = _proof_packet_id(request_id)
            proof_receipt_id = _proof_receipt_id(request_id)
            delivery_preview_id = _proof_delivery_preview_id(request_id)

            conn.execute(
                """
                INSERT OR REPLACE INTO proof_eligibility_gates (
                    proof_eligibility_id, request_id, vault_request_draft_id,
                    gate_state, tower_is_requester, teller_is_requester,
                    tower_identity_check_passed, tower_permission_check_passed,
                    tower_approval_recorded, proof_protocol_allowed,
                    teller_direct_proof_allowed, raw_file_bytes_json_allowed,
                    public_proof_link_allowed, raw_token_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proof_eligibility_id,
                    request_id,
                    row["vault_request_draft_id"],
                    "proof_eligibility_gate_passed_for_tower_only",
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
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO proof_scope_redaction_gates (
                    proof_redaction_id, request_id, vault_request_draft_id,
                    redaction_state, proof_hash_only,
                    raw_file_bytes_redacted, raw_path_redacted,
                    raw_file_url_redacted, raw_token_redacted,
                    public_link_redacted, direct_browse_redacted,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proof_redaction_id,
                    request_id,
                    row["vault_request_draft_id"],
                    "proof_scope_redaction_gate_ready_hash_only",
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

            internal_request_material = {
                "request_id": request_id,
                "vault_request_draft_id": row["vault_request_draft_id"],
                "from_service": "Tower",
                "to_service": "Vault",
                "vault_answer_target": "Tower",
                "internal_vault_proof_call_sent": True,
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
                INSERT OR REPLACE INTO tower_internal_vault_proof_requests (
                    internal_proof_request_id, request_id,
                    vault_request_draft_id, request_state,
                    from_service, to_service, vault_answer_target,
                    internal_vault_proof_call_sent, teller_call_sent,
                    raw_file_bytes_requested, raw_path_requested,
                    raw_file_url_requested, raw_token_requested,
                    public_link_requested, internal_request_hash,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    internal_proof_request_id,
                    request_id,
                    row["vault_request_draft_id"],
                    "tower_internal_vault_proof_request_sent_controlled",
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

            proof_integrity_hash = calculate_sha256_bytes(
                f"proof-integrity|{request_id}|{row['sealed_download_artifact_hash']}|{row['download_receipt_hash']}".encode("utf-8")
            )
            proof_subject_hash = calculate_sha256_bytes(
                f"proof-subject|{request_id}|redacted-subject-reference".encode("utf-8")
            )
            proof_receipt_reference_hash = calculate_sha256_bytes(
                f"proof-receipt-reference|{request_id}|{row['download_receipt_hash']}|{row['handle_guard_hash']}".encode("utf-8")
            )

            response_material = {
                "request_id": request_id,
                "internal_proof_request_id": internal_proof_request_id,
                "answered_to": "Tower",
                "vault_answered_tower_only": True,
                "proof_integrity_hash": proof_integrity_hash,
                "proof_subject_hash": proof_subject_hash,
                "proof_receipt_reference_hash": proof_receipt_reference_hash,
                "raw_file_bytes_returned_by_json": False,
                "raw_path_returned": False,
                "raw_file_url_returned": False,
                "raw_token_returned": False,
                "public_link_returned": False,
            }
            response_hash = calculate_sha256_bytes(repr(sorted(response_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO vault_proof_response_envelopes (
                    proof_response_id, request_id,
                    internal_proof_request_id, response_state,
                    answered_to, vault_answered_tower_only,
                    proof_integrity_hash, proof_subject_hash,
                    proof_receipt_reference_hash,
                    raw_file_bytes_returned_by_json,
                    raw_path_returned, raw_file_url_returned,
                    raw_token_returned, public_link_returned,
                    response_envelope_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proof_response_id,
                    request_id,
                    internal_proof_request_id,
                    "vault_proof_response_envelope_ready_for_tower_hash_only",
                    "Tower",
                    1,
                    proof_integrity_hash,
                    proof_subject_hash,
                    proof_receipt_reference_hash,
                    0,
                    0,
                    0,
                    0,
                    0,
                    response_hash,
                    now,
                ),
            )

            proof_packet_material = {
                "request_id": request_id,
                "proof_response_id": proof_response_id,
                "proof_integrity_hash": proof_integrity_hash,
                "sealed_download_artifact_hash": row["sealed_download_artifact_hash"],
                "download_receipt_hash": row["download_receipt_hash"],
                "handle_guard_hash": row["handle_guard_hash"],
                "raw_file_bytes_included": False,
                "raw_path_included": False,
                "raw_file_url_included": False,
                "raw_token_included": False,
                "public_link_included": False,
            }
            proof_packet_hash = calculate_sha256_bytes(repr(sorted(proof_packet_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO proof_packet_hashes (
                    proof_packet_id, request_id, proof_response_id,
                    packet_state, proof_packet_hash,
                    proof_integrity_hash, sealed_download_artifact_hash,
                    download_receipt_hash, handle_guard_hash,
                    raw_file_bytes_included, raw_path_included,
                    raw_file_url_included, raw_token_included,
                    public_link_included, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proof_packet_id,
                    request_id,
                    proof_response_id,
                    "proof_packet_hash_ready_for_tower",
                    proof_packet_hash,
                    proof_integrity_hash,
                    row["sealed_download_artifact_hash"],
                    row["download_receipt_hash"],
                    row["handle_guard_hash"],
                    0,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            proof_receipt_hash = calculate_sha256_bytes(
                f"proof-receipt-draft|{request_id}|{proof_packet_hash}|{response_hash}|no-raw-no-public".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO proof_receipt_drafts (
                    proof_receipt_id, request_id, proof_packet_id,
                    proof_response_id, receipt_state, proof_receipt_hash,
                    receipt_finalized, append_only, mutable,
                    raw_file_bytes_receipted, raw_token_receipted,
                    public_link_receipted, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proof_receipt_id,
                    request_id,
                    proof_packet_id,
                    proof_response_id,
                    "proof_receipt_draft_ready_append_only",
                    proof_receipt_hash,
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
                "proof_response_id": proof_response_id,
                "proof_packet_id": proof_packet_id,
                "delivered_to": "Tower",
                "teller_delivery_allowed_after_tower": True,
                "direct_person_delivery_allowed": False,
                "direct_vault_link_included": False,
                "raw_file_bytes_included": False,
                "raw_token_included": False,
                "public_link_included": False,
                "workflow_safe_proof_status_ready": True,
            }
            delivery_hash = calculate_sha256_bytes(repr(sorted(delivery_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_proof_result_delivery_previews (
                    proof_delivery_preview_id, request_id,
                    proof_response_id, proof_packet_id,
                    delivery_state, delivered_to,
                    teller_delivery_allowed_after_tower,
                    direct_person_delivery_allowed,
                    direct_vault_link_included,
                    raw_file_bytes_included, raw_token_included,
                    public_link_included,
                    workflow_safe_proof_status_ready,
                    delivery_preview_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    delivery_preview_id,
                    request_id,
                    proof_response_id,
                    proof_packet_id,
                    "tower_proof_result_delivery_preview_ready_workflow_safe_hash_only",
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
        "previous_tower_authorized_download_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP491_INIT_CACHE = dict(result)
    return result


def get_tower_authorized_proof_protocol_shell() -> Dict[str, Any]:
    init = initialize_tower_authorized_proof_protocol_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 491,
        "title": "Tower Authorized Proof Protocol Shell",
        "ready": True,
        "initialized": init,
        "doctrine": DOCTRINE,
        "correct_flow": DOCTRINE["correct_flow"],
        "controlled_proof_protocol_hash_only": True,
        "raw_file_bytes_returned_by_json": False,
        "raw_download_token_exposed": False,
        "public_link_created": False,
        "teller_direct_proof_allowed": False,
        "locks": LOCKS,
    }


def get_proof_eligibility_gate_board() -> Dict[str, Any]:
    initialize_tower_authorized_proof_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM proof_eligibility_gates ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 492,
        "title": "Proof Eligibility Gate Board",
        "ready": True,
        "proof_eligibility_count": len(rows),
        "proof_eligibility_gates": rows,
        "all_tower_is_requester": all(bool(item["tower_is_requester"]) for item in rows),
        "no_teller_is_requester": all(not bool(item["teller_is_requester"]) for item in rows),
        "all_tower_identity_permission_passed": all(bool(item["tower_identity_check_passed"]) and bool(item["tower_permission_check_passed"]) for item in rows),
        "all_tower_approval_recorded": all(bool(item["tower_approval_recorded"]) for item in rows),
        "all_proof_protocol_allowed": all(bool(item["proof_protocol_allowed"]) for item in rows),
        "no_teller_direct_proof": all(not bool(item["teller_direct_proof_allowed"]) for item in rows),
        "no_raw_file_bytes_json": all(not bool(item["raw_file_bytes_json_allowed"]) for item in rows),
        "no_public_proof_links": all(not bool(item["public_proof_link_allowed"]) for item in rows),
        "no_raw_tokens": all(not bool(item["raw_token_allowed"]) for item in rows),
    }


def get_proof_scope_redaction_gate_board() -> Dict[str, Any]:
    initialize_tower_authorized_proof_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM proof_scope_redaction_gates ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 493,
        "title": "Proof Scope Redaction Gate Board",
        "ready": True,
        "proof_redaction_count": len(rows),
        "proof_redaction_gates": rows,
        "all_proof_hash_only": all(bool(item["proof_hash_only"]) for item in rows),
        "all_raw_file_bytes_redacted": all(bool(item["raw_file_bytes_redacted"]) for item in rows),
        "all_raw_paths_redacted": all(bool(item["raw_path_redacted"]) for item in rows),
        "all_raw_file_urls_redacted": all(bool(item["raw_file_url_redacted"]) for item in rows),
        "all_raw_tokens_redacted": all(bool(item["raw_token_redacted"]) for item in rows),
        "all_public_links_redacted": all(bool(item["public_link_redacted"]) for item in rows),
        "all_direct_browse_redacted": all(bool(item["direct_browse_redacted"]) for item in rows),
    }


def get_tower_internal_vault_proof_request_ledger() -> Dict[str, Any]:
    initialize_tower_authorized_proof_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_internal_vault_proof_requests ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 494,
        "title": "Tower Internal Vault Proof Request Ledger",
        "ready": True,
        "internal_proof_request_count": len(rows),
        "internal_proof_requests": rows,
        "all_from_tower_to_vault": all(item["from_service"] == "Tower" and item["to_service"] == "Vault" for item in rows),
        "all_vault_answer_target_tower": all(item["vault_answer_target"] == "Tower" for item in rows),
        "all_internal_proof_calls_sent": all(bool(item["internal_vault_proof_call_sent"]) for item in rows),
        "no_teller_calls_sent": all(not bool(item["teller_call_sent"]) for item in rows),
        "no_raw_file_bytes_requested": all(not bool(item["raw_file_bytes_requested"]) for item in rows),
        "no_raw_paths_requested": all(not bool(item["raw_path_requested"]) for item in rows),
        "no_raw_file_urls_requested": all(not bool(item["raw_file_url_requested"]) for item in rows),
        "no_raw_tokens_requested": all(not bool(item["raw_token_requested"]) for item in rows),
        "no_public_links_requested": all(not bool(item["public_link_requested"]) for item in rows),
    }


def get_vault_proof_response_envelope_board() -> Dict[str, Any]:
    initialize_tower_authorized_proof_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM vault_proof_response_envelopes ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 495,
        "title": "Vault Proof Response Envelope Board",
        "ready": True,
        "proof_response_count": len(rows),
        "proof_response_envelopes": rows,
        "all_answered_to_tower": all(item["answered_to"] == "Tower" for item in rows),
        "all_vault_answered_tower_only": all(bool(item["vault_answered_tower_only"]) for item in rows),
        "all_have_proof_integrity_hash": all(len(item["proof_integrity_hash"]) == 64 for item in rows),
        "all_have_proof_subject_hash": all(len(item["proof_subject_hash"]) == 64 for item in rows),
        "all_have_receipt_reference_hash": all(len(item["proof_receipt_reference_hash"]) == 64 for item in rows),
        "no_raw_file_bytes_json": all(not bool(item["raw_file_bytes_returned_by_json"]) for item in rows),
        "no_raw_paths_returned": all(not bool(item["raw_path_returned"]) for item in rows),
        "no_raw_file_urls_returned": all(not bool(item["raw_file_url_returned"]) for item in rows),
        "no_raw_tokens_returned": all(not bool(item["raw_token_returned"]) for item in rows),
        "no_public_links_returned": all(not bool(item["public_link_returned"]) for item in rows),
    }


def get_proof_packet_hash_builder() -> Dict[str, Any]:
    initialize_tower_authorized_proof_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM proof_packet_hashes ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 496,
        "title": "Proof Packet Hash Builder",
        "ready": True,
        "proof_packet_count": len(rows),
        "proof_packets": rows,
        "all_proof_packets_hash_ready": all(item["packet_state"] == "proof_packet_hash_ready_for_tower" for item in rows),
        "all_have_proof_packet_hash": all(len(item["proof_packet_hash"]) == 64 for item in rows),
        "no_raw_file_bytes": all(not bool(item["raw_file_bytes_included"]) for item in rows),
        "no_raw_paths": all(not bool(item["raw_path_included"]) for item in rows),
        "no_raw_file_urls": all(not bool(item["raw_file_url_included"]) for item in rows),
        "no_raw_tokens": all(not bool(item["raw_token_included"]) for item in rows),
        "no_public_links": all(not bool(item["public_link_included"]) for item in rows),
    }


def get_proof_receipt_draft_ledger() -> Dict[str, Any]:
    initialize_tower_authorized_proof_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM proof_receipt_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 497,
        "title": "Proof Receipt Draft Ledger",
        "ready": True,
        "proof_receipt_count": len(rows),
        "proof_receipts": rows,
        "all_receipts_draft": all(not bool(item["receipt_finalized"]) for item in rows),
        "all_append_only": all(bool(item["append_only"]) for item in rows),
        "all_immutable": all(not bool(item["mutable"]) for item in rows),
        "no_raw_file_bytes_receipted": all(not bool(item["raw_file_bytes_receipted"]) for item in rows),
        "no_raw_tokens_receipted": all(not bool(item["raw_token_receipted"]) for item in rows),
        "no_public_links_receipted": all(not bool(item["public_link_receipted"]) for item in rows),
    }


def get_tower_proof_result_delivery_preview_board() -> Dict[str, Any]:
    initialize_tower_authorized_proof_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_proof_result_delivery_previews ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 498,
        "title": "Tower Proof Result Delivery Preview Board",
        "ready": True,
        "proof_delivery_preview_count": len(rows),
        "proof_delivery_previews": rows,
        "all_delivered_to_tower": all(item["delivered_to"] == "Tower" for item in rows),
        "all_teller_delivery_allowed_after_tower": all(bool(item["teller_delivery_allowed_after_tower"]) for item in rows),
        "no_direct_person_delivery": all(not bool(item["direct_person_delivery_allowed"]) for item in rows),
        "no_direct_vault_link": all(not bool(item["direct_vault_link_included"]) for item in rows),
        "no_raw_file_bytes": all(not bool(item["raw_file_bytes_included"]) for item in rows),
        "no_raw_tokens": all(not bool(item["raw_token_included"]) for item in rows),
        "no_public_links": all(not bool(item["public_link_included"]) for item in rows),
        "all_workflow_safe_proof_status_ready": all(bool(item["workflow_safe_proof_status_ready"]) for item in rows),
    }


def get_tower_authorized_proof_safety_blocker_board() -> Dict[str, Any]:
    initialize_tower_authorized_proof_protocol_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_authorized_proof_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 499,
        "title": "Tower Authorized Proof Safety Blocker Board",
        "ready": True,
        "blocker_count": len(rows),
        "blockers": rows,
        "unsafe_action_count": sum(1 for item in rows if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in rows),
    }


def get_tower_authorized_proof_protocol_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_tower_authorized_proof_protocol_layer()

    shell = get_tower_authorized_proof_protocol_shell()
    eligibility = get_proof_eligibility_gate_board()
    redaction = get_proof_scope_redaction_gate_board()
    requests = get_tower_internal_vault_proof_request_ledger()
    responses = get_vault_proof_response_envelope_board()
    packets = get_proof_packet_hash_builder()
    receipts = get_proof_receipt_draft_ledger()
    delivery = get_tower_proof_result_delivery_preview_board()
    blockers = get_tower_authorized_proof_safety_blocker_board()

    checks = {
        "previous_tower_authorized_download_ready": init["previous_tower_authorized_download_ready"] is True,
        "proof_protocol_shell_ready": shell["ready"] is True,
        "doctrine_tower_teller_vault_locked": DOCTRINE["tower"] == "face_protocol_authority" and DOCTRINE["teller"] == "workflow_request_source" and DOCTRINE["vault"] == "sealed_memory",
        "correct_flow_locked": DOCTRINE["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller",
        "tower_executes_controlled_proof_protocol": DOCTRINE["tower_executes_controlled_proof_protocol"] is True,
        "proof_answers_tower_only": DOCTRINE["proof_protocol_answers_tower_only"] is True and DOCTRINE["vault_answers_tower_only"] is True,
        "proof_hash_only_no_raw_token_public": DOCTRINE["proof_packet_hash_only"] is True and DOCTRINE["raw_file_bytes_exposed_by_proof"] is False and DOCTRINE["raw_download_token_exposed_by_proof"] is False and DOCTRINE["public_link_created_by_proof"] is False,
        "eligibility_ready": eligibility["ready"] is True and eligibility["proof_eligibility_count"] >= 2,
        "eligibility_tower_only": eligibility["all_tower_is_requester"] is True and eligibility["no_teller_is_requester"] is True,
        "eligibility_passed_for_proof": eligibility["all_tower_identity_permission_passed"] is True and eligibility["all_tower_approval_recorded"] is True and eligibility["all_proof_protocol_allowed"] is True,
        "eligibility_no_teller_raw_public_token": eligibility["no_teller_direct_proof"] is True and eligibility["no_raw_file_bytes_json"] is True and eligibility["no_public_proof_links"] is True and eligibility["no_raw_tokens"] is True,
        "redaction_ready": redaction["ready"] is True and redaction["proof_redaction_count"] >= 2,
        "redaction_hash_only": redaction["all_proof_hash_only"] is True,
        "redaction_blocks_raw_path_url_token_public_direct": redaction["all_raw_file_bytes_redacted"] is True and redaction["all_raw_paths_redacted"] is True and redaction["all_raw_file_urls_redacted"] is True and redaction["all_raw_tokens_redacted"] is True and redaction["all_public_links_redacted"] is True and redaction["all_direct_browse_redacted"] is True,
        "internal_requests_ready": requests["ready"] is True and requests["internal_proof_request_count"] >= 2,
        "internal_requests_tower_to_vault_only": requests["all_from_tower_to_vault"] is True and requests["all_vault_answer_target_tower"] is True and requests["all_internal_proof_calls_sent"] is True and requests["no_teller_calls_sent"] is True,
        "internal_requests_no_raw_path_url_token_public_requested": requests["no_raw_file_bytes_requested"] is True and requests["no_raw_paths_requested"] is True and requests["no_raw_file_urls_requested"] is True and requests["no_raw_tokens_requested"] is True and requests["no_public_links_requested"] is True,
        "responses_ready": responses["ready"] is True and responses["proof_response_count"] >= 2,
        "responses_tower_only_hash_envelope": responses["all_answered_to_tower"] is True and responses["all_vault_answered_tower_only"] is True and responses["all_have_proof_integrity_hash"] is True and responses["all_have_proof_subject_hash"] is True and responses["all_have_receipt_reference_hash"] is True,
        "responses_no_raw_path_url_token_public": responses["no_raw_file_bytes_json"] is True and responses["no_raw_paths_returned"] is True and responses["no_raw_file_urls_returned"] is True and responses["no_raw_tokens_returned"] is True and responses["no_public_links_returned"] is True,
        "proof_packets_ready": packets["ready"] is True and packets["proof_packet_count"] >= 2,
        "proof_packets_hash_ready": packets["all_proof_packets_hash_ready"] is True and packets["all_have_proof_packet_hash"] is True,
        "proof_packets_no_raw_path_url_token_public": packets["no_raw_file_bytes"] is True and packets["no_raw_paths"] is True and packets["no_raw_file_urls"] is True and packets["no_raw_tokens"] is True and packets["no_public_links"] is True,
        "proof_receipts_ready": receipts["ready"] is True and receipts["proof_receipt_count"] >= 2,
        "proof_receipts_draft_append_only_no_raw_token_public": receipts["all_receipts_draft"] is True and receipts["all_append_only"] is True and receipts["all_immutable"] is True and receipts["no_raw_file_bytes_receipted"] is True and receipts["no_raw_tokens_receipted"] is True and receipts["no_public_links_receipted"] is True,
        "delivery_ready": delivery["ready"] is True and delivery["proof_delivery_preview_count"] >= 2,
        "delivery_to_tower_then_workflow_safe": delivery["all_delivered_to_tower"] is True and delivery["all_teller_delivery_allowed_after_tower"] is True and delivery["all_workflow_safe_proof_status_ready"] is True,
        "delivery_no_direct_person_raw_token_public": delivery["no_direct_person_delivery"] is True and delivery["no_direct_vault_link"] is True and delivery["no_raw_file_bytes"] is True and delivery["no_raw_tokens"] is True and delivery["no_public_links"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "global_proof_allowed_hash_only": LOCKS["controlled_proof_protocol_allowed"] is True and LOCKS["proof_packet_hashes_allowed"] is True and LOCKS["raw_file_bytes_returned_by_json"] is False and LOCKS["raw_download_token_exposed"] is False,
        "global_no_teller_to_vault_or_direct_proof": LOCKS["teller_to_vault_direct_call_allowed"] is False and LOCKS["vault_direct_request_from_teller_allowed"] is False and LOCKS["teller_direct_proof_allowed"] is False,
        "global_no_public_dashboard_portal_browse": LOCKS["public_vault_dashboard_allowed"] is False and LOCKS["direct_vault_user_portal_allowed"] is False and LOCKS["employee_vault_browsing_allowed"] is False and LOCKS["external_collaborator_browsing_allowed"] is False,
        "global_no_public_links_raw_bytes_paths_tokens": LOCKS["public_url_created"] is False and LOCKS["share_link_created"] is False and LOCKS["raw_file_bytes_exposed"] is False and LOCKS["raw_path_exposed"] is False and LOCKS["raw_file_url_exposed"] is False and LOCKS["raw_download_token_exposed"] is False,
        "global_no_provider_delete_restore_move": LOCKS["provider_storage_required"] is False and LOCKS["hard_delete_allowed"] is False and LOCKS["purge_allowed"] is False and LOCKS["restore_execution_allowed"] is False and LOCKS["physical_object_move_allowed"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 500,
        "title": "Tower Authorized Proof Protocol Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Tower authorized proof protocol layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — TOWER PROTOCOL RECEIPT CLOSEOUT LAYER / GP501-GP510",
        "still_locked": [
            "no Teller-to-Vault direct calls",
            "no Teller direct proof calls",
            "no direct Vault user portal",
            "no employee/vendor/customer Vault browsing",
            "no public Vault dashboard",
            "no standalone external Vault dashboard",
            "no external collaborator browsing",
            "no public URL or share link",
            "no raw file bytes returned by JSON",
            "no raw path or raw file URL exposure",
            "no raw token exposure",
            "no public download or public proof links",
            "no public/beta/provider upload",
            "no delete or purge",
            "no restore execution",
            "no quarantine release",
            "no physical object move",
            "no provider dependency by default",
        ],
    }


def get_tower_authorized_proof_protocol_home() -> Dict[str, Any]:
    checkpoint = get_tower_authorized_proof_protocol_readiness_checkpoint()
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


def validate_tower_authorized_proof_protocol_layer() -> Dict[str, Any]:
    checkpoint = get_tower_authorized_proof_protocol_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_tower_authorized_download_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"]["tower_executes_controlled_proof_protocol"] is True
    assert checkpoint["checks"]["proof_answers_tower_only"] is True
    assert checkpoint["checks"]["proof_hash_only_no_raw_token_public"] is True
    assert checkpoint["checks"]["eligibility_ready"] is True
    assert checkpoint["checks"]["eligibility_tower_only"] is True
    assert checkpoint["checks"]["eligibility_passed_for_proof"] is True
    assert checkpoint["checks"]["eligibility_no_teller_raw_public_token"] is True
    assert checkpoint["checks"]["redaction_ready"] is True
    assert checkpoint["checks"]["redaction_hash_only"] is True
    assert checkpoint["checks"]["redaction_blocks_raw_path_url_token_public_direct"] is True
    assert checkpoint["checks"]["internal_requests_ready"] is True
    assert checkpoint["checks"]["internal_requests_tower_to_vault_only"] is True
    assert checkpoint["checks"]["internal_requests_no_raw_path_url_token_public_requested"] is True
    assert checkpoint["checks"]["responses_ready"] is True
    assert checkpoint["checks"]["responses_tower_only_hash_envelope"] is True
    assert checkpoint["checks"]["responses_no_raw_path_url_token_public"] is True
    assert checkpoint["checks"]["proof_packets_ready"] is True
    assert checkpoint["checks"]["proof_packets_hash_ready"] is True
    assert checkpoint["checks"]["proof_packets_no_raw_path_url_token_public"] is True
    assert checkpoint["checks"]["proof_receipts_ready"] is True
    assert checkpoint["checks"]["proof_receipts_draft_append_only_no_raw_token_public"] is True
    assert checkpoint["checks"]["delivery_ready"] is True
    assert checkpoint["checks"]["delivery_to_tower_then_workflow_safe"] is True
    assert checkpoint["checks"]["delivery_no_direct_person_raw_token_public"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["controlled_proof_protocol_allowed"] is True
    assert LOCKS["tower_internal_vault_proof_requests_allowed"] is True
    assert LOCKS["vault_proof_response_envelopes_allowed"] is True
    assert LOCKS["proof_packet_hashes_allowed"] is True

    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_file_bytes_exposed"] is False
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["raw_share_token_exposed"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS["public_proof_link_created"] is False
    assert LOCKS["teller_direct_proof_allowed"] is False
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
    checkpoint = get_tower_authorized_proof_protocol_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "correct_flow": DOCTRINE["correct_flow"],
        "controlled_proof_protocol_allowed": True,
        "proof_packet_hash_only": True,
        "raw_file_bytes_returned_by_json": False,
        "raw_download_token_exposed": False,
        "public_proof_link_created": False,
        "teller_to_vault_direct_call_allowed": False,
        "vault_answers_tower_only": True,
        "locks_preserved": True,
    }


def get_gp491_status() -> Dict[str, Any]:
    return _gp_status(491)


def get_gp492_status() -> Dict[str, Any]:
    return _gp_status(492)


def get_gp493_status() -> Dict[str, Any]:
    return _gp_status(493)


def get_gp494_status() -> Dict[str, Any]:
    return _gp_status(494)


def get_gp495_status() -> Dict[str, Any]:
    return _gp_status(495)


def get_gp496_status() -> Dict[str, Any]:
    return _gp_status(496)


def get_gp497_status() -> Dict[str, Any]:
    return _gp_status(497)


def get_gp498_status() -> Dict[str, Any]:
    return _gp_status(498)


def get_gp499_status() -> Dict[str, Any]:
    return _gp_status(499)


def get_gp500_status() -> Dict[str, Any]:
    return _gp_status(500)
