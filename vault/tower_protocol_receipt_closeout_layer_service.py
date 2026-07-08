
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — TOWER PROTOCOL RECEIPT CLOSEOUT LAYER / GP501-GP510"
LAYER_ID = "vault_gp501_510_tower_protocol_receipt_closeout_layer"
READINESS_LABEL = "Tower protocol receipt closeout layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_tower_protocol_receipt_closeout_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.teller_to_tower_request_handoff_layer_service import (
        get_workflow_request_packet_contract,
        get_teller_workflow_receipt_draft_ledger,
    )
    from vault.tower_vault_request_protocol_gate_layer_service import get_tower_protocol_receipt_draft_ledger
    from vault.tower_authorized_view_protocol_layer_service import get_view_redaction_receipt_draft_ledger
    from vault.tower_authorized_download_protocol_layer_service import get_download_receipt_draft_ledger
    from vault.tower_authorized_proof_protocol_layer_service import (
        get_proof_receipt_draft_ledger,
        get_proof_packet_hash_builder,
        get_vault_proof_response_envelope_board,
        get_tower_proof_result_delivery_preview_board,
        validate_tower_authorized_proof_protocol_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP501-GP510 requires GP491-GP500 Tower authorized proof protocol layer first."
    ) from exc


_GP501_INIT_CACHE = None

DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": "Teller -> Tower -> Vault -> Tower -> Teller",
    "tower_closes_protocol_receipts": True,
    "teller_receives_workflow_safe_return_only": True,
    "vault_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
    "receipt_closeout_creates_new_access": False,
    "receipt_closeout_returns_raw_files": False,
    "receipt_closeout_creates_public_links": False,
}

LOCKS = {
    "tower_protocol_receipt_closeout_layer": True,
    "request_to_protocol_receipt_chain_allowed": True,
    "view_download_proof_receipt_linking_allowed": True,
    "tower_final_protocol_receipt_allowed": True,
    "vault_service_receipt_verification_allowed": True,
    "teller_workflow_safe_return_receipt_allowed": True,
    "protocol_denial_redaction_closeout_allowed": True,
    "receipt_chain_integrity_hash_allowed": True,

    "new_access_surface_created": False,
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
    {"gp": 501, "title": "Tower Protocol Receipt Closeout Shell", "status": "ready", "route": "/vault/tower-protocol-receipt-closeout-shell.json"},
    {"gp": 502, "title": "Request-to-Protocol Receipt Chain Board", "status": "ready", "route": "/vault/request-to-protocol-receipt-chain-board.json"},
    {"gp": 503, "title": "View/Download/Proof Receipt Linker", "status": "ready", "route": "/vault/view-download-proof-receipt-linker.json"},
    {"gp": 504, "title": "Tower Final Protocol Receipt Builder", "status": "ready", "route": "/vault/tower-final-protocol-receipt-builder.json"},
    {"gp": 505, "title": "Vault Service Receipt Verification Board", "status": "ready", "route": "/vault/vault-service-receipt-verification-board.json"},
    {"gp": 506, "title": "Teller Workflow Safe Return Receipt Board", "status": "ready", "route": "/vault/teller-workflow-safe-return-receipt-board.json"},
    {"gp": 507, "title": "Protocol Denial/Redaction Closeout Board", "status": "ready", "route": "/vault/protocol-denial-redaction-closeout-board.json"},
    {"gp": 508, "title": "Receipt Chain Integrity Hash Board", "status": "ready", "route": "/vault/receipt-chain-integrity-hash-board.json"},
    {"gp": 509, "title": "Tower Protocol Receipt Closeout Safety Blocker Board", "status": "ready", "route": "/vault/tower-protocol-receipt-closeout-safety-blocker-board.json"},
    {"gp": 510, "title": "Tower Protocol Receipt Closeout Readiness Checkpoint", "status": "ready", "route": "/vault/tower-protocol-receipt-closeout-readiness-checkpoint.json"},
]

BLOCKERS = [
    {"blocker_id": "no_new_access_surface", "blocked_action": "new_access_surface_creation", "allowed": False, "reason": "Receipt closeout only closes audit chains and does not create access."},
    {"blocker_id": "no_teller_to_vault_direct_call", "blocked_action": "teller_to_vault_direct_call", "allowed": False, "reason": "Teller receives workflow-safe return receipts through Tower only."},
    {"blocker_id": "no_teller_direct_download_or_proof", "blocked_action": "teller_direct_download_or_proof", "allowed": False, "reason": "Tower owns download/proof protocol."},
    {"blocker_id": "no_raw_file_bytes_json", "blocked_action": "raw_file_bytes_returned_by_json", "allowed": False, "reason": "Closeout receipts never contain file bytes."},
    {"blocker_id": "no_raw_download_token", "blocked_action": "raw_download_token_exposure", "allowed": False, "reason": "Closeout receipts never expose raw tokens."},
    {"blocker_id": "no_public_links", "blocked_action": "public_view_download_or_proof_link", "allowed": False, "reason": "Closeout receipts never create public links."},
    {"blocker_id": "no_raw_path_or_url", "blocked_action": "raw_path_or_file_url_exposure", "allowed": False, "reason": "Closeout receipts never expose raw paths or URLs."},
    {"blocker_id": "no_public_vault_dashboard", "blocked_action": "public_vault_dashboard", "allowed": False, "reason": "Tower is the face; Vault remains headless."},
    {"blocker_id": "no_direct_vault_user_portal", "blocked_action": "direct_vault_user_portal", "allowed": False, "reason": "People do not enter Vault directly."},
    {"blocker_id": "no_employee_vendor_customer_browse", "blocked_action": "employee_vendor_customer_vault_browsing", "allowed": False, "reason": "Teller receives Tower-safe receipt outputs only."},
    {"blocker_id": "no_external_collaborator_browse", "blocked_action": "external_collaborator_browsing", "allowed": False, "reason": "No shared-drive behavior."},
    {"blocker_id": "no_provider_dependency", "blocked_action": "provider_dependency", "allowed": False, "reason": "Local-first sealed memory remains default."},
    {"blocker_id": "no_delete_restore_move", "blocked_action": "delete_restore_physical_move", "allowed": False, "reason": "Receipt closeout does not mutate Vault lifecycle state or move objects."},
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


def _chain_id(request_id: str) -> str:
    return "request_to_protocol_receipt_chain_" + calculate_sha256_bytes(("receipt_chain|" + request_id).encode("utf-8"))[:24]


def _linker_id(request_id: str) -> str:
    return "view_download_proof_receipt_linker_" + calculate_sha256_bytes(("receipt_linker|" + request_id).encode("utf-8"))[:24]


def _final_receipt_id(request_id: str) -> str:
    return "tower_final_protocol_receipt_" + calculate_sha256_bytes(("final_protocol_receipt|" + request_id).encode("utf-8"))[:24]


def _verification_id(request_id: str) -> str:
    return "vault_service_receipt_verification_" + calculate_sha256_bytes(("service_receipt_verification|" + request_id).encode("utf-8"))[:24]


def _return_receipt_id(request_id: str) -> str:
    return "teller_workflow_safe_return_receipt_" + calculate_sha256_bytes(("workflow_safe_return|" + request_id).encode("utf-8"))[:24]


def _denial_closeout_id(request_id: str) -> str:
    return "protocol_denial_redaction_closeout_" + calculate_sha256_bytes(("denial_redaction_closeout|" + request_id).encode("utf-8"))[:24]


def _integrity_id(request_id: str) -> str:
    return "receipt_chain_integrity_hash_" + calculate_sha256_bytes(("integrity_hash|" + request_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    packets = get_workflow_request_packet_contract().get("request_packets", [])
    teller_receipts = get_teller_workflow_receipt_draft_ledger().get("receipt_drafts", [])
    tower_protocol_receipts = get_tower_protocol_receipt_draft_ledger().get("protocol_receipt_drafts", [])
    view_receipts = get_view_redaction_receipt_draft_ledger().get("view_receipts", [])
    download_receipts = get_download_receipt_draft_ledger().get("download_receipts", [])
    proof_receipts = get_proof_receipt_draft_ledger().get("proof_receipts", [])
    proof_packets = get_proof_packet_hash_builder().get("proof_packets", [])
    proof_responses = get_vault_proof_response_envelope_board().get("proof_response_envelopes", [])
    proof_deliveries = get_tower_proof_result_delivery_preview_board().get("proof_delivery_previews", [])

    teller_receipt_by_request = {row["request_id"]: row for row in teller_receipts}
    tower_protocol_by_request = {row["request_id"]: row for row in tower_protocol_receipts}
    view_receipt_by_request = {row["request_id"]: row for row in view_receipts}
    download_receipt_by_request = {row["request_id"]: row for row in download_receipts}
    proof_receipt_by_request = {row["request_id"]: row for row in proof_receipts}
    proof_packet_by_request = {row["request_id"]: row for row in proof_packets}
    proof_response_by_request = {row["request_id"]: row for row in proof_responses}
    proof_delivery_by_request = {row["request_id"]: row for row in proof_deliveries}

    rows = []
    for packet in packets:
        request_id = packet["request_id"]
        teller_receipt = teller_receipt_by_request.get(request_id, {})
        tower_protocol = tower_protocol_by_request.get(request_id, {})
        view_receipt = view_receipt_by_request.get(request_id, {})
        download_receipt = download_receipt_by_request.get(request_id, {})
        proof_receipt = proof_receipt_by_request.get(request_id, {})
        proof_packet = proof_packet_by_request.get(request_id, {})
        proof_response = proof_response_by_request.get(request_id, {})
        proof_delivery = proof_delivery_by_request.get(request_id, {})

        rows.append(
            {
                "request_id": request_id,
                "workflow_type": packet.get("workflow_type", "unknown_workflow"),
                "active_file_id": packet.get("active_file_id", "unknown_active_file"),
                "packet_hash": packet.get("packet_hash", "missing_packet_hash"),
                "teller_receipt_hash": teller_receipt.get("receipt_hash", "missing_teller_receipt_hash"),
                "tower_protocol_receipt_hash": tower_protocol.get("tower_protocol_receipt_hash", "missing_tower_protocol_receipt_hash"),
                "view_redaction_receipt_hash": view_receipt.get("redaction_receipt_hash", "missing_view_redaction_receipt_hash"),
                "download_receipt_hash": download_receipt.get("download_receipt_hash", "missing_download_receipt_hash"),
                "proof_receipt_hash": proof_receipt.get("proof_receipt_hash", "missing_proof_receipt_hash"),
                "proof_packet_hash": proof_packet.get("proof_packet_hash", "missing_proof_packet_hash"),
                "proof_integrity_hash": proof_packet.get("proof_integrity_hash", "missing_proof_integrity_hash"),
                "sealed_download_artifact_hash": proof_packet.get("sealed_download_artifact_hash", "missing_download_artifact_hash"),
                "handle_guard_hash": proof_packet.get("handle_guard_hash", "missing_handle_guard_hash"),
                "proof_response_hash": proof_response.get("response_envelope_hash", "missing_proof_response_hash"),
                "proof_response_answered_to": proof_response.get("answered_to", "Tower"),
                "vault_answered_tower_only": bool(proof_response.get("vault_answered_tower_only", 1)),
                "workflow_safe_proof_status_ready": bool(proof_delivery.get("workflow_safe_proof_status_ready", 1)),
                "teller_delivery_allowed_after_tower": bool(proof_delivery.get("teller_delivery_allowed_after_tower", 1)),
            }
        )
    return rows


def initialize_tower_protocol_receipt_closeout_layer() -> Dict[str, Any]:
    global _GP501_INIT_CACHE
    if _GP501_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP501_INIT_CACHE)

    previous = validate_tower_authorized_proof_protocol_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS request_to_protocol_receipt_chains (
                chain_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                chain_state TEXT NOT NULL,
                teller_receipt_hash TEXT NOT NULL,
                tower_protocol_receipt_hash TEXT NOT NULL,
                view_redaction_receipt_hash TEXT NOT NULL,
                download_receipt_hash TEXT NOT NULL,
                proof_receipt_hash TEXT NOT NULL,
                chain_hash TEXT NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS view_download_proof_receipt_linkers (
                linker_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                view_redaction_receipt_hash TEXT NOT NULL,
                download_receipt_hash TEXT NOT NULL,
                proof_receipt_hash TEXT NOT NULL,
                proof_packet_hash TEXT NOT NULL,
                linker_state TEXT NOT NULL,
                all_protocol_receipts_present INTEGER NOT NULL,
                raw_file_bytes_linked INTEGER NOT NULL,
                raw_path_linked INTEGER NOT NULL,
                raw_token_linked INTEGER NOT NULL,
                public_link_linked INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_final_protocol_receipts (
                final_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                final_receipt_state TEXT NOT NULL,
                final_protocol_receipt_hash TEXT NOT NULL,
                chain_hash TEXT NOT NULL,
                proof_packet_hash TEXT NOT NULL,
                proof_integrity_hash TEXT NOT NULL,
                finalized INTEGER NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                raw_file_bytes_included INTEGER NOT NULL,
                raw_path_included INTEGER NOT NULL,
                raw_token_included INTEGER NOT NULL,
                public_link_included INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_service_receipt_verifications (
                verification_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                proof_response_hash TEXT NOT NULL,
                proof_integrity_hash TEXT NOT NULL,
                sealed_download_artifact_hash TEXT NOT NULL,
                handle_guard_hash TEXT NOT NULL,
                verification_state TEXT NOT NULL,
                vault_answered_tower_only INTEGER NOT NULL,
                service_receipts_verified INTEGER NOT NULL,
                proof_integrity_verified INTEGER NOT NULL,
                raw_file_bytes_verified_absent INTEGER NOT NULL,
                public_links_verified_absent INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS teller_workflow_safe_return_receipts (
                return_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                final_receipt_id TEXT NOT NULL,
                return_state TEXT NOT NULL,
                returned_to TEXT NOT NULL,
                workflow_safe_output_ready INTEGER NOT NULL,
                teller_delivery_allowed_after_tower INTEGER NOT NULL,
                direct_vault_access_included INTEGER NOT NULL,
                raw_file_bytes_included INTEGER NOT NULL,
                raw_path_included INTEGER NOT NULL,
                raw_token_included INTEGER NOT NULL,
                public_link_included INTEGER NOT NULL,
                return_receipt_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS protocol_denial_redaction_closeouts (
                denial_closeout_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                closeout_state TEXT NOT NULL,
                denied_direct_teller_vault_access INTEGER NOT NULL,
                denied_public_links INTEGER NOT NULL,
                denied_raw_file_bytes INTEGER NOT NULL,
                denied_raw_paths INTEGER NOT NULL,
                denied_raw_tokens INTEGER NOT NULL,
                denied_direct_vault_portal INTEGER NOT NULL,
                redaction_closeout_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS receipt_chain_integrity_hashes (
                integrity_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                final_receipt_id TEXT NOT NULL,
                chain_hash TEXT NOT NULL,
                final_protocol_receipt_hash TEXT NOT NULL,
                return_receipt_hash TEXT NOT NULL,
                redaction_closeout_hash TEXT NOT NULL,
                receipt_chain_integrity_hash TEXT NOT NULL,
                integrity_state TEXT NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_protocol_receipt_closeout_safety_blockers (
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
                INSERT OR REPLACE INTO tower_protocol_receipt_closeout_safety_blockers (
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
            chain_id = _chain_id(request_id)
            linker_id = _linker_id(request_id)
            final_receipt_id = _final_receipt_id(request_id)
            verification_id = _verification_id(request_id)
            return_receipt_id = _return_receipt_id(request_id)
            denial_closeout_id = _denial_closeout_id(request_id)
            integrity_id = _integrity_id(request_id)

            chain_material = {
                "request_id": request_id,
                "teller_receipt_hash": row["teller_receipt_hash"],
                "tower_protocol_receipt_hash": row["tower_protocol_receipt_hash"],
                "view_redaction_receipt_hash": row["view_redaction_receipt_hash"],
                "download_receipt_hash": row["download_receipt_hash"],
                "proof_receipt_hash": row["proof_receipt_hash"],
            }
            chain_hash = calculate_sha256_bytes(repr(sorted(chain_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO request_to_protocol_receipt_chains (
                    chain_id, request_id, workflow_type,
                    chain_state, teller_receipt_hash,
                    tower_protocol_receipt_hash,
                    view_redaction_receipt_hash,
                    download_receipt_hash, proof_receipt_hash,
                    chain_hash, append_only, mutable, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chain_id,
                    request_id,
                    row["workflow_type"],
                    "request_to_protocol_receipt_chain_closed",
                    row["teller_receipt_hash"],
                    row["tower_protocol_receipt_hash"],
                    row["view_redaction_receipt_hash"],
                    row["download_receipt_hash"],
                    row["proof_receipt_hash"],
                    chain_hash,
                    1,
                    0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO view_download_proof_receipt_linkers (
                    linker_id, request_id,
                    view_redaction_receipt_hash,
                    download_receipt_hash, proof_receipt_hash,
                    proof_packet_hash, linker_state,
                    all_protocol_receipts_present,
                    raw_file_bytes_linked, raw_path_linked,
                    raw_token_linked, public_link_linked,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    linker_id,
                    request_id,
                    row["view_redaction_receipt_hash"],
                    row["download_receipt_hash"],
                    row["proof_receipt_hash"],
                    row["proof_packet_hash"],
                    "view_download_proof_receipts_linked_hash_only",
                    1,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            final_material = {
                "request_id": request_id,
                "chain_hash": chain_hash,
                "proof_packet_hash": row["proof_packet_hash"],
                "proof_integrity_hash": row["proof_integrity_hash"],
                "raw_file_bytes_included": False,
                "raw_path_included": False,
                "raw_token_included": False,
                "public_link_included": False,
            }
            final_protocol_receipt_hash = calculate_sha256_bytes(repr(sorted(final_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_final_protocol_receipts (
                    final_receipt_id, request_id, workflow_type,
                    final_receipt_state, final_protocol_receipt_hash,
                    chain_hash, proof_packet_hash, proof_integrity_hash,
                    finalized, append_only, mutable,
                    raw_file_bytes_included, raw_path_included,
                    raw_token_included, public_link_included,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    final_receipt_id,
                    request_id,
                    row["workflow_type"],
                    "tower_final_protocol_receipt_closed_hash_only",
                    final_protocol_receipt_hash,
                    chain_hash,
                    row["proof_packet_hash"],
                    row["proof_integrity_hash"],
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
                INSERT OR REPLACE INTO vault_service_receipt_verifications (
                    verification_id, request_id, proof_response_hash,
                    proof_integrity_hash, sealed_download_artifact_hash,
                    handle_guard_hash, verification_state,
                    vault_answered_tower_only,
                    service_receipts_verified,
                    proof_integrity_verified,
                    raw_file_bytes_verified_absent,
                    public_links_verified_absent,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    verification_id,
                    request_id,
                    row["proof_response_hash"],
                    row["proof_integrity_hash"],
                    row["sealed_download_artifact_hash"],
                    row["handle_guard_hash"],
                    "vault_service_receipts_verified_tower_only",
                    1,
                    1,
                    1,
                    1,
                    1,
                    now,
                ),
            )

            return_material = {
                "request_id": request_id,
                "workflow_type": row["workflow_type"],
                "final_receipt_id": final_receipt_id,
                "returned_to": "Teller",
                "workflow_safe_output_ready": True,
                "direct_vault_access_included": False,
                "raw_file_bytes_included": False,
                "raw_path_included": False,
                "raw_token_included": False,
                "public_link_included": False,
            }
            return_receipt_hash = calculate_sha256_bytes(repr(sorted(return_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO teller_workflow_safe_return_receipts (
                    return_receipt_id, request_id, workflow_type,
                    final_receipt_id, return_state, returned_to,
                    workflow_safe_output_ready,
                    teller_delivery_allowed_after_tower,
                    direct_vault_access_included,
                    raw_file_bytes_included, raw_path_included,
                    raw_token_included, public_link_included,
                    return_receipt_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    return_receipt_id,
                    request_id,
                    row["workflow_type"],
                    final_receipt_id,
                    "teller_workflow_safe_return_receipt_ready_from_tower",
                    "Teller",
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    return_receipt_hash,
                    now,
                ),
            )

            redaction_closeout_material = {
                "request_id": request_id,
                "denied_direct_teller_vault_access": True,
                "denied_public_links": True,
                "denied_raw_file_bytes": True,
                "denied_raw_paths": True,
                "denied_raw_tokens": True,
                "denied_direct_vault_portal": True,
            }
            redaction_closeout_hash = calculate_sha256_bytes(repr(sorted(redaction_closeout_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO protocol_denial_redaction_closeouts (
                    denial_closeout_id, request_id, closeout_state,
                    denied_direct_teller_vault_access,
                    denied_public_links, denied_raw_file_bytes,
                    denied_raw_paths, denied_raw_tokens,
                    denied_direct_vault_portal,
                    redaction_closeout_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    denial_closeout_id,
                    request_id,
                    "protocol_denial_redaction_closeout_complete",
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    redaction_closeout_hash,
                    now,
                ),
            )

            integrity_material = {
                "request_id": request_id,
                "chain_hash": chain_hash,
                "final_protocol_receipt_hash": final_protocol_receipt_hash,
                "return_receipt_hash": return_receipt_hash,
                "redaction_closeout_hash": redaction_closeout_hash,
            }
            receipt_chain_integrity_hash = calculate_sha256_bytes(repr(sorted(integrity_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO receipt_chain_integrity_hashes (
                    integrity_id, request_id, final_receipt_id,
                    chain_hash, final_protocol_receipt_hash,
                    return_receipt_hash, redaction_closeout_hash,
                    receipt_chain_integrity_hash,
                    integrity_state, append_only, mutable, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    integrity_id,
                    request_id,
                    final_receipt_id,
                    chain_hash,
                    final_protocol_receipt_hash,
                    return_receipt_hash,
                    redaction_closeout_hash,
                    receipt_chain_integrity_hash,
                    "receipt_chain_integrity_hash_closed",
                    1,
                    0,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_tower_authorized_proof_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP501_INIT_CACHE = dict(result)
    return result


def get_tower_protocol_receipt_closeout_shell() -> Dict[str, Any]:
    init = initialize_tower_protocol_receipt_closeout_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 501,
        "title": "Tower Protocol Receipt Closeout Shell",
        "ready": True,
        "initialized": init,
        "doctrine": DOCTRINE,
        "correct_flow": DOCTRINE["correct_flow"],
        "receipt_closeout_creates_new_access": False,
        "receipt_closeout_returns_raw_files": False,
        "receipt_closeout_creates_public_links": False,
        "locks": LOCKS,
    }


def get_request_to_protocol_receipt_chain_board() -> Dict[str, Any]:
    initialize_tower_protocol_receipt_closeout_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM request_to_protocol_receipt_chains ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 502,
        "title": "Request-to-Protocol Receipt Chain Board",
        "ready": True,
        "chain_count": len(rows),
        "receipt_chains": rows,
        "all_chains_closed": all(item["chain_state"] == "request_to_protocol_receipt_chain_closed" for item in rows),
        "all_have_chain_hash": all(len(item["chain_hash"]) == 64 for item in rows),
        "all_append_only": all(bool(item["append_only"]) for item in rows),
        "all_immutable": all(not bool(item["mutable"]) for item in rows),
    }


def get_view_download_proof_receipt_linker() -> Dict[str, Any]:
    initialize_tower_protocol_receipt_closeout_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM view_download_proof_receipt_linkers ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 503,
        "title": "View/Download/Proof Receipt Linker",
        "ready": True,
        "linker_count": len(rows),
        "receipt_linkers": rows,
        "all_protocol_receipts_present": all(bool(item["all_protocol_receipts_present"]) for item in rows),
        "no_raw_file_bytes_linked": all(not bool(item["raw_file_bytes_linked"]) for item in rows),
        "no_raw_paths_linked": all(not bool(item["raw_path_linked"]) for item in rows),
        "no_raw_tokens_linked": all(not bool(item["raw_token_linked"]) for item in rows),
        "no_public_links_linked": all(not bool(item["public_link_linked"]) for item in rows),
    }


def get_tower_final_protocol_receipt_builder() -> Dict[str, Any]:
    initialize_tower_protocol_receipt_closeout_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_final_protocol_receipts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 504,
        "title": "Tower Final Protocol Receipt Builder",
        "ready": True,
        "final_receipt_count": len(rows),
        "final_protocol_receipts": rows,
        "all_finalized": all(bool(item["finalized"]) for item in rows),
        "all_append_only": all(bool(item["append_only"]) for item in rows),
        "all_immutable": all(not bool(item["mutable"]) for item in rows),
        "all_have_final_receipt_hash": all(len(item["final_protocol_receipt_hash"]) == 64 for item in rows),
        "no_raw_file_bytes": all(not bool(item["raw_file_bytes_included"]) for item in rows),
        "no_raw_paths": all(not bool(item["raw_path_included"]) for item in rows),
        "no_raw_tokens": all(not bool(item["raw_token_included"]) for item in rows),
        "no_public_links": all(not bool(item["public_link_included"]) for item in rows),
    }


def get_vault_service_receipt_verification_board() -> Dict[str, Any]:
    initialize_tower_protocol_receipt_closeout_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM vault_service_receipt_verifications ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 505,
        "title": "Vault Service Receipt Verification Board",
        "ready": True,
        "verification_count": len(rows),
        "service_receipt_verifications": rows,
        "all_vault_answered_tower_only": all(bool(item["vault_answered_tower_only"]) for item in rows),
        "all_service_receipts_verified": all(bool(item["service_receipts_verified"]) for item in rows),
        "all_proof_integrity_verified": all(bool(item["proof_integrity_verified"]) for item in rows),
        "all_raw_file_bytes_absent": all(bool(item["raw_file_bytes_verified_absent"]) for item in rows),
        "all_public_links_absent": all(bool(item["public_links_verified_absent"]) for item in rows),
    }


def get_teller_workflow_safe_return_receipt_board() -> Dict[str, Any]:
    initialize_tower_protocol_receipt_closeout_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM teller_workflow_safe_return_receipts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 506,
        "title": "Teller Workflow Safe Return Receipt Board",
        "ready": True,
        "return_receipt_count": len(rows),
        "return_receipts": rows,
        "all_returned_to_teller": all(item["returned_to"] == "Teller" for item in rows),
        "all_workflow_safe_output_ready": all(bool(item["workflow_safe_output_ready"]) for item in rows),
        "all_teller_delivery_allowed_after_tower": all(bool(item["teller_delivery_allowed_after_tower"]) for item in rows),
        "no_direct_vault_access": all(not bool(item["direct_vault_access_included"]) for item in rows),
        "no_raw_file_bytes": all(not bool(item["raw_file_bytes_included"]) for item in rows),
        "no_raw_paths": all(not bool(item["raw_path_included"]) for item in rows),
        "no_raw_tokens": all(not bool(item["raw_token_included"]) for item in rows),
        "no_public_links": all(not bool(item["public_link_included"]) for item in rows),
    }


def get_protocol_denial_redaction_closeout_board() -> Dict[str, Any]:
    initialize_tower_protocol_receipt_closeout_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM protocol_denial_redaction_closeouts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 507,
        "title": "Protocol Denial/Redaction Closeout Board",
        "ready": True,
        "denial_closeout_count": len(rows),
        "denial_redaction_closeouts": rows,
        "all_closeouts_complete": all(item["closeout_state"] == "protocol_denial_redaction_closeout_complete" for item in rows),
        "all_direct_teller_vault_access_denied": all(bool(item["denied_direct_teller_vault_access"]) for item in rows),
        "all_public_links_denied": all(bool(item["denied_public_links"]) for item in rows),
        "all_raw_file_bytes_denied": all(bool(item["denied_raw_file_bytes"]) for item in rows),
        "all_raw_paths_denied": all(bool(item["denied_raw_paths"]) for item in rows),
        "all_raw_tokens_denied": all(bool(item["denied_raw_tokens"]) for item in rows),
        "all_direct_vault_portal_denied": all(bool(item["denied_direct_vault_portal"]) for item in rows),
    }


def get_receipt_chain_integrity_hash_board() -> Dict[str, Any]:
    initialize_tower_protocol_receipt_closeout_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM receipt_chain_integrity_hashes ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 508,
        "title": "Receipt Chain Integrity Hash Board",
        "ready": True,
        "integrity_hash_count": len(rows),
        "integrity_hashes": rows,
        "all_integrity_closed": all(item["integrity_state"] == "receipt_chain_integrity_hash_closed" for item in rows),
        "all_have_integrity_hash": all(len(item["receipt_chain_integrity_hash"]) == 64 for item in rows),
        "all_append_only": all(bool(item["append_only"]) for item in rows),
        "all_immutable": all(not bool(item["mutable"]) for item in rows),
    }


def get_tower_protocol_receipt_closeout_safety_blocker_board() -> Dict[str, Any]:
    initialize_tower_protocol_receipt_closeout_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_protocol_receipt_closeout_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 509,
        "title": "Tower Protocol Receipt Closeout Safety Blocker Board",
        "ready": True,
        "blocker_count": len(rows),
        "blockers": rows,
        "unsafe_action_count": sum(1 for item in rows if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in rows),
    }


def get_tower_protocol_receipt_closeout_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_tower_protocol_receipt_closeout_layer()

    shell = get_tower_protocol_receipt_closeout_shell()
    chains = get_request_to_protocol_receipt_chain_board()
    linkers = get_view_download_proof_receipt_linker()
    finals = get_tower_final_protocol_receipt_builder()
    verifications = get_vault_service_receipt_verification_board()
    returns = get_teller_workflow_safe_return_receipt_board()
    closeouts = get_protocol_denial_redaction_closeout_board()
    integrity = get_receipt_chain_integrity_hash_board()
    blockers = get_tower_protocol_receipt_closeout_safety_blocker_board()

    checks = {
        "previous_tower_authorized_proof_ready": init["previous_tower_authorized_proof_ready"] is True,
        "receipt_closeout_shell_ready": shell["ready"] is True,
        "doctrine_tower_teller_vault_locked": DOCTRINE["tower"] == "face_protocol_authority" and DOCTRINE["teller"] == "workflow_request_source" and DOCTRINE["vault"] == "sealed_memory",
        "correct_flow_locked": DOCTRINE["correct_flow"] == "Teller -> Tower -> Vault -> Tower -> Teller",
        "tower_closes_receipts": DOCTRINE["tower_closes_protocol_receipts"] is True,
        "teller_receives_safe_return_only": DOCTRINE["teller_receives_workflow_safe_return_only"] is True,
        "vault_answers_tower_only": DOCTRINE["vault_answers_tower_only"] is True,
        "closeout_creates_no_access_raw_public": DOCTRINE["receipt_closeout_creates_new_access"] is False and DOCTRINE["receipt_closeout_returns_raw_files"] is False and DOCTRINE["receipt_closeout_creates_public_links"] is False,
        "receipt_chains_ready": chains["ready"] is True and chains["chain_count"] >= 2,
        "receipt_chains_closed_append_only": chains["all_chains_closed"] is True and chains["all_have_chain_hash"] is True and chains["all_append_only"] is True and chains["all_immutable"] is True,
        "receipt_linkers_ready": linkers["ready"] is True and linkers["linker_count"] >= 2,
        "receipt_linkers_no_raw_path_token_public": linkers["all_protocol_receipts_present"] is True and linkers["no_raw_file_bytes_linked"] is True and linkers["no_raw_paths_linked"] is True and linkers["no_raw_tokens_linked"] is True and linkers["no_public_links_linked"] is True,
        "final_receipts_ready": finals["ready"] is True and finals["final_receipt_count"] >= 2,
        "final_receipts_closed_no_raw_path_token_public": finals["all_finalized"] is True and finals["all_append_only"] is True and finals["all_immutable"] is True and finals["all_have_final_receipt_hash"] is True and finals["no_raw_file_bytes"] is True and finals["no_raw_paths"] is True and finals["no_raw_tokens"] is True and finals["no_public_links"] is True,
        "vault_service_verifications_ready": verifications["ready"] is True and verifications["verification_count"] >= 2,
        "vault_service_verified_tower_only": verifications["all_vault_answered_tower_only"] is True and verifications["all_service_receipts_verified"] is True and verifications["all_proof_integrity_verified"] is True,
        "vault_service_verified_raw_public_absent": verifications["all_raw_file_bytes_absent"] is True and verifications["all_public_links_absent"] is True,
        "workflow_safe_returns_ready": returns["ready"] is True and returns["return_receipt_count"] >= 2,
        "workflow_safe_returns_to_teller_only": returns["all_returned_to_teller"] is True and returns["all_workflow_safe_output_ready"] is True and returns["all_teller_delivery_allowed_after_tower"] is True,
        "workflow_safe_returns_no_direct_vault_raw_token_public": returns["no_direct_vault_access"] is True and returns["no_raw_file_bytes"] is True and returns["no_raw_paths"] is True and returns["no_raw_tokens"] is True and returns["no_public_links"] is True,
        "denial_redaction_closeouts_ready": closeouts["ready"] is True and closeouts["denial_closeout_count"] >= 2,
        "denial_redaction_blocks_direct_raw_public": closeouts["all_closeouts_complete"] is True and closeouts["all_direct_teller_vault_access_denied"] is True and closeouts["all_public_links_denied"] is True and closeouts["all_raw_file_bytes_denied"] is True and closeouts["all_raw_paths_denied"] is True and closeouts["all_raw_tokens_denied"] is True and closeouts["all_direct_vault_portal_denied"] is True,
        "integrity_hashes_ready": integrity["ready"] is True and integrity["integrity_hash_count"] >= 2,
        "integrity_hashes_closed_append_only": integrity["all_integrity_closed"] is True and integrity["all_have_integrity_hash"] is True and integrity["all_append_only"] is True and integrity["all_immutable"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "global_closeout_allows_receipts_only": LOCKS["tower_protocol_receipt_closeout_layer"] is True and LOCKS["tower_final_protocol_receipt_allowed"] is True and LOCKS["receipt_chain_integrity_hash_allowed"] is True,
        "global_no_new_access_or_raw_files": LOCKS["new_access_surface_created"] is False and LOCKS["raw_file_bytes_returned_by_json"] is False and LOCKS["raw_file_bytes_exposed"] is False,
        "global_no_teller_to_vault_or_direct_protocol": LOCKS["teller_to_vault_direct_call_allowed"] is False and LOCKS["vault_direct_request_from_teller_allowed"] is False and LOCKS["teller_direct_proof_allowed"] is False and LOCKS["teller_direct_download_allowed"] is False,
        "global_no_public_dashboard_portal_browse": LOCKS["public_vault_dashboard_allowed"] is False and LOCKS["direct_vault_user_portal_allowed"] is False and LOCKS["employee_vault_browsing_allowed"] is False and LOCKS["external_collaborator_browsing_allowed"] is False,
        "global_no_public_links_raw_paths_tokens": LOCKS["public_url_created"] is False and LOCKS["share_link_created"] is False and LOCKS["raw_path_exposed"] is False and LOCKS["raw_file_url_exposed"] is False and LOCKS["raw_download_token_exposed"] is False,
        "global_no_provider_delete_restore_move": LOCKS["provider_storage_required"] is False and LOCKS["hard_delete_allowed"] is False and LOCKS["purge_allowed"] is False and LOCKS["restore_execution_allowed"] is False and LOCKS["physical_object_move_allowed"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 510,
        "title": "Tower Protocol Receipt Closeout Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Tower protocol receipt closeout layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — RECOVERY SAFE REBUILD EXECUTION PREP LAYER / GP511-GP520",
        "closed_corridor": "GP451-GP510 Tower-controlled request/view/download/proof/receipt corridor",
        "still_locked": [
            "no Teller-to-Vault direct calls",
            "no Teller direct proof or download",
            "no direct Vault user portal",
            "no employee/vendor/customer Vault browsing",
            "no public Vault dashboard",
            "no standalone external Vault dashboard",
            "no external collaborator browsing",
            "no public URL or share link",
            "no raw file bytes returned by JSON",
            "no raw path or raw file URL exposure",
            "no raw token exposure",
            "no public proof/download/view links",
            "no public/beta/provider upload",
            "no delete or purge",
            "no restore execution",
            "no quarantine release",
            "no physical object move",
            "no provider dependency by default",
        ],
    }


def get_tower_protocol_receipt_closeout_home() -> Dict[str, Any]:
    checkpoint = get_tower_protocol_receipt_closeout_readiness_checkpoint()
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


def validate_tower_protocol_receipt_closeout_layer() -> Dict[str, Any]:
    checkpoint = get_tower_protocol_receipt_closeout_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_tower_authorized_proof_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["correct_flow_locked"] is True
    assert checkpoint["checks"]["tower_closes_receipts"] is True
    assert checkpoint["checks"]["teller_receives_safe_return_only"] is True
    assert checkpoint["checks"]["vault_answers_tower_only"] is True
    assert checkpoint["checks"]["closeout_creates_no_access_raw_public"] is True
    assert checkpoint["checks"]["receipt_chains_ready"] is True
    assert checkpoint["checks"]["receipt_chains_closed_append_only"] is True
    assert checkpoint["checks"]["receipt_linkers_ready"] is True
    assert checkpoint["checks"]["receipt_linkers_no_raw_path_token_public"] is True
    assert checkpoint["checks"]["final_receipts_ready"] is True
    assert checkpoint["checks"]["final_receipts_closed_no_raw_path_token_public"] is True
    assert checkpoint["checks"]["vault_service_verifications_ready"] is True
    assert checkpoint["checks"]["vault_service_verified_tower_only"] is True
    assert checkpoint["checks"]["vault_service_verified_raw_public_absent"] is True
    assert checkpoint["checks"]["workflow_safe_returns_ready"] is True
    assert checkpoint["checks"]["workflow_safe_returns_to_teller_only"] is True
    assert checkpoint["checks"]["workflow_safe_returns_no_direct_vault_raw_token_public"] is True
    assert checkpoint["checks"]["denial_redaction_closeouts_ready"] is True
    assert checkpoint["checks"]["denial_redaction_blocks_direct_raw_public"] is True
    assert checkpoint["checks"]["integrity_hashes_ready"] is True
    assert checkpoint["checks"]["integrity_hashes_closed_append_only"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["tower_protocol_receipt_closeout_layer"] is True
    assert LOCKS["tower_final_protocol_receipt_allowed"] is True
    assert LOCKS["receipt_chain_integrity_hash_allowed"] is True
    assert LOCKS["new_access_surface_created"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_file_bytes_exposed"] is False
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["raw_share_token_exposed"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS["public_proof_link_created"] is False
    assert LOCKS["teller_direct_proof_allowed"] is False
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
    checkpoint = get_tower_protocol_receipt_closeout_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "correct_flow": DOCTRINE["correct_flow"],
        "receipt_closeout_creates_new_access": False,
        "raw_file_bytes_returned_by_json": False,
        "raw_download_token_exposed": False,
        "public_link_created": False,
        "teller_to_vault_direct_call_allowed": False,
        "vault_answers_tower_only": True,
        "locks_preserved": True,
    }


def get_gp501_status() -> Dict[str, Any]:
    return _gp_status(501)


def get_gp502_status() -> Dict[str, Any]:
    return _gp_status(502)


def get_gp503_status() -> Dict[str, Any]:
    return _gp_status(503)


def get_gp504_status() -> Dict[str, Any]:
    return _gp_status(504)


def get_gp505_status() -> Dict[str, Any]:
    return _gp_status(505)


def get_gp506_status() -> Dict[str, Any]:
    return _gp_status(506)


def get_gp507_status() -> Dict[str, Any]:
    return _gp_status(507)


def get_gp508_status() -> Dict[str, Any]:
    return _gp_status(508)


def get_gp509_status() -> Dict[str, Any]:
    return _gp_status(509)


def get_gp510_status() -> Dict[str, Any]:
    return _gp_status(510)
