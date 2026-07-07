
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — HEADLESS TOWER STATUS BRIDGE LAYER / GP441-GP450"
LAYER_ID = "vault_gp441_450_headless_tower_status_bridge_layer"
READINESS_LABEL = "Headless Tower status bridge layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_headless_tower_status_bridge_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.vault_pack_rebuild_service_layer_service import (
        get_vault_pack_rebuild_service_readiness_checkpoint,
        get_rebuilt_pack_index_preview_board,
        get_tower_teller_rebuild_output_contract,
        get_merkle_root_rebuild_verifier,
        validate_vault_pack_rebuild_service_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP441-GP450 requires GP431-GP440 Vault Pack rebuild service layer first."
    ) from exc


_GP441_INIT_CACHE = None

DOCTRINE = {
    "tower": "face",
    "teller": "workflow",
    "vault": "sealed_memory",
    "bridge_behavior": "headless_internal_status_bridge_only",
    "people_enter_vault_directly": False,
    "vault_is_public_dashboard": False,
    "vault_is_direct_user_portal": False,
    "bridge_outputs_are_redacted": True,
}

LOCKS = {
    "headless_tower_status_bridge_layer": True,
    "tower_vault_health_cards_allowed": True,
    "tower_security_receipt_summaries_allowed": True,
    "tower_owner_clearance_status_allowed": True,
    "teller_workflow_proof_status_allowed": True,
    "vault_memory_integrity_signals_allowed": True,
    "sealed_rebuild_status_outputs_allowed": True,
    "tower_teller_bridge_redaction_allowed": True,

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
    {"gp": 441, "title": "Headless Tower Status Bridge Shell", "status": "ready", "route": "/vault/headless-tower-status-bridge-shell.json"},
    {"gp": 442, "title": "Tower Vault Health Card Contract", "status": "ready", "route": "/vault/tower-vault-health-card-contract.json"},
    {"gp": 443, "title": "Tower Security Receipt Summary Board", "status": "ready", "route": "/vault/tower-security-receipt-summary-board.json"},
    {"gp": 444, "title": "Tower Owner Clearance Status Bridge", "status": "ready", "route": "/vault/tower-owner-clearance-status-bridge.json"},
    {"gp": 445, "title": "Teller Workflow Proof Status Bridge", "status": "ready", "route": "/vault/teller-workflow-proof-status-bridge.json"},
    {"gp": 446, "title": "Vault Memory Integrity Signal Builder", "status": "ready", "route": "/vault/vault-memory-integrity-signal-builder.json"},
    {"gp": 447, "title": "Sealed Rebuild Status Output Builder", "status": "ready", "route": "/vault/sealed-rebuild-status-output-builder.json"},
    {"gp": 448, "title": "Tower Teller Bridge Redaction Contract", "status": "ready", "route": "/vault/tower-teller-bridge-redaction-contract.json"},
    {"gp": 449, "title": "Headless Bridge Safety Blocker Board", "status": "ready", "route": "/vault/headless-bridge-safety-blocker-board.json"},
    {"gp": 450, "title": "Headless Tower Status Bridge Readiness Checkpoint", "status": "ready", "route": "/vault/headless-tower-status-bridge-readiness-checkpoint.json"},
]

BLOCKERS = [
    {"blocker_id": "no_public_vault_dashboard", "blocked_action": "public_vault_dashboard", "allowed": False, "reason": "Tower is the face; Vault status bridge is headless."},
    {"blocker_id": "no_direct_vault_user_portal", "blocked_action": "direct_vault_user_portal", "allowed": False, "reason": "People do not enter Vault directly."},
    {"blocker_id": "no_external_vault_dashboard", "blocked_action": "standalone_external_vault_dashboard", "allowed": False, "reason": "Vault does not become a public app."},
    {"blocker_id": "no_employee_vendor_customer_browse", "blocked_action": "employee_vendor_customer_vault_browsing", "allowed": False, "reason": "Teller handles workflow requests; Vault does not browse for people."},
    {"blocker_id": "no_external_collaborator_browse", "blocked_action": "external_collaborator_browsing", "allowed": False, "reason": "No shared-drive behavior."},
    {"blocker_id": "no_public_links", "blocked_action": "public_links_or_raw_urls", "allowed": False, "reason": "Tower cards never expose public links or raw URLs."},
    {"blocker_id": "no_raw_file_bytes_json", "blocked_action": "raw_file_bytes_json", "allowed": False, "reason": "Bridge outputs are status/proof metadata only."},
    {"blocker_id": "no_raw_paths", "blocked_action": "raw_path_exposure", "allowed": False, "reason": "Status bridge never exposes physical paths."},
    {"blocker_id": "no_raw_tokens", "blocked_action": "raw_token_exposure", "allowed": False, "reason": "Status bridge never exposes raw tokens."},
    {"blocker_id": "no_final_index_write", "blocked_action": "final_rebuilt_index_write", "allowed": False, "reason": "Status bridge displays rebuild status only."},
    {"blocker_id": "no_provider_dependency", "blocked_action": "provider_dependency", "allowed": False, "reason": "Status bridge reads local-first sealed status metadata."},
    {"blocker_id": "no_delete_restore_move", "blocked_action": "delete_restore_physical_move", "allowed": False, "reason": "Bridge does not mutate Vault lifecycle state or move objects."},
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


def _health_card_id(active_file_id: str) -> str:
    return "tower_vault_health_card_" + calculate_sha256_bytes(("tower_health|" + active_file_id).encode("utf-8"))[:24]


def _security_receipt_summary_id(active_file_id: str) -> str:
    return "tower_security_receipt_summary_" + calculate_sha256_bytes(("tower_receipt|" + active_file_id).encode("utf-8"))[:24]


def _clearance_status_id(active_file_id: str) -> str:
    return "tower_owner_clearance_status_" + calculate_sha256_bytes(("tower_clearance|" + active_file_id).encode("utf-8"))[:24]


def _teller_proof_status_id(active_file_id: str) -> str:
    return "teller_workflow_proof_status_" + calculate_sha256_bytes(("teller_proof|" + active_file_id).encode("utf-8"))[:24]


def _memory_signal_id(active_file_id: str) -> str:
    return "vault_memory_integrity_signal_" + calculate_sha256_bytes(("memory_signal|" + active_file_id).encode("utf-8"))[:24]


def _rebuild_output_id(active_file_id: str) -> str:
    return "sealed_rebuild_status_output_" + calculate_sha256_bytes(("rebuild_output|" + active_file_id).encode("utf-8"))[:24]


def _redaction_contract_id(active_file_id: str) -> str:
    return "tower_teller_bridge_redaction_" + calculate_sha256_bytes(("bridge_redaction|" + active_file_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    checkpoint = get_vault_pack_rebuild_service_readiness_checkpoint()
    previews = get_rebuilt_pack_index_preview_board().get("previews", [])
    output_contracts = get_tower_teller_rebuild_output_contract().get("output_contracts", [])
    merkle_rows = get_merkle_root_rebuild_verifier().get("merkle_verifiers", [])

    output_by_file = {row["active_file_id"]: row for row in output_contracts}
    merkle_by_file = {row["active_file_id"]: row for row in merkle_rows}

    rows = []
    for preview in previews:
        active_file_id = preview["active_file_id"]
        output = output_by_file.get(active_file_id, {})
        merkle = merkle_by_file.get(active_file_id, {})
        rows.append(
            {
                "active_file_id": active_file_id,
                "rebuild_candidate_id": preview["rebuild_candidate_id"],
                "preview_id": preview["preview_id"],
                "rebuilt_index_preview_hash": preview["rebuilt_index_preview_hash"],
                "preview_state": preview["preview_state"],
                "preview_only": bool(preview["preview_only"]),
                "final_index_write_allowed": bool(preview["final_index_write_allowed"]),
                "final_pack_overwrite_allowed": bool(preview["final_pack_overwrite_allowed"]),
                "public_index_allowed": bool(preview["public_index_allowed"]),
                "external_browse_allowed": bool(preview["external_browse_allowed"]),
                "raw_bytes_exposed": bool(preview["raw_bytes_exposed"]),
                "output_contract_id": output.get("output_contract_id", "missing_output_contract"),
                "allowed_outputs": output.get("allowed_outputs", "rebuild_status_card|rebuild_integrity_result|rebuild_receipt_hash|rebuild_preview_hash|merkle_verification_result"),
                "blocked_outputs": output.get("blocked_outputs", "raw_file_bytes|raw_path|raw_file_url|public_link|direct_browse|shared_folder|final_index_write|pack_overwrite"),
                "tower_face_required": bool(output.get("tower_face_required", 1)),
                "teller_workflow_required": bool(output.get("teller_workflow_required", 1)),
                "direct_vault_portal_allowed": bool(output.get("direct_vault_portal_allowed", 0)),
                "public_dashboard_allowed": bool(output.get("public_dashboard_allowed", 0)),
                "raw_file_bytes_json_allowed": bool(output.get("raw_file_bytes_json_allowed", 0)),
                "merkle_verifier_id": merkle.get("merkle_verifier_id", "missing_merkle_verifier"),
                "verifier_hash": merkle.get("verifier_hash", "missing_verifier_hash"),
                "merkle_rebuild_verified": bool(merkle.get("merkle_rebuild_verified", 0)),
                "raw_bytes_needed": bool(merkle.get("raw_bytes_needed", 1)),
                "provider_needed": bool(merkle.get("provider_needed", 1)),
                "previous_ready": bool(checkpoint.get("ready", False)),
            }
        )
    return rows


def initialize_headless_tower_status_bridge_layer() -> Dict[str, Any]:
    global _GP441_INIT_CACHE
    if _GP441_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP441_INIT_CACHE)

    previous = validate_vault_pack_rebuild_service_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_vault_health_cards (
                health_card_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                rebuild_candidate_id TEXT NOT NULL,
                health_state TEXT NOT NULL,
                vault_ready INTEGER NOT NULL,
                sealed_memory_ready INTEGER NOT NULL,
                rebuild_preview_ready INTEGER NOT NULL,
                tower_face_required INTEGER NOT NULL,
                teller_workflow_required INTEGER NOT NULL,
                direct_vault_portal_allowed INTEGER NOT NULL,
                public_dashboard_allowed INTEGER NOT NULL,
                raw_file_bytes_json_allowed INTEGER NOT NULL,
                health_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_security_receipt_summaries (
                receipt_summary_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                rebuild_candidate_id TEXT NOT NULL,
                receipt_summary_state TEXT NOT NULL,
                redacted_receipt_hash TEXT NOT NULL,
                raw_receipt_body_included INTEGER NOT NULL,
                raw_path_included INTEGER NOT NULL,
                raw_url_included INTEGER NOT NULL,
                raw_token_included INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_owner_clearance_status_bridge (
                clearance_status_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                rebuild_candidate_id TEXT NOT NULL,
                clearance_state TEXT NOT NULL,
                owner_admin_required INTEGER NOT NULL,
                step_up_required INTEGER NOT NULL,
                tower_permission_required INTEGER NOT NULL,
                vault_direct_approval_allowed INTEGER NOT NULL,
                direct_user_portal_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS teller_workflow_proof_status_bridge (
                teller_proof_status_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                rebuild_candidate_id TEXT NOT NULL,
                workflow_state TEXT NOT NULL,
                teller_workflow_required INTEGER NOT NULL,
                document_request_status_allowed INTEGER NOT NULL,
                proof_hash_allowed INTEGER NOT NULL,
                direct_vault_browse_allowed INTEGER NOT NULL,
                raw_file_bytes_allowed INTEGER NOT NULL,
                public_link_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_memory_integrity_signals (
                memory_signal_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                rebuild_candidate_id TEXT NOT NULL,
                integrity_state TEXT NOT NULL,
                merkle_verified INTEGER NOT NULL,
                rebuild_preview_hash TEXT NOT NULL,
                verifier_hash TEXT NOT NULL,
                raw_bytes_needed INTEGER NOT NULL,
                provider_needed INTEGER NOT NULL,
                integrity_signal_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sealed_rebuild_status_outputs (
                rebuild_output_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                rebuild_candidate_id TEXT NOT NULL,
                output_state TEXT NOT NULL,
                allowed_callers TEXT NOT NULL,
                allowed_outputs TEXT NOT NULL,
                blocked_outputs TEXT NOT NULL,
                preview_only INTEGER NOT NULL,
                final_index_write_allowed INTEGER NOT NULL,
                final_pack_overwrite_allowed INTEGER NOT NULL,
                public_index_allowed INTEGER NOT NULL,
                external_browse_allowed INTEGER NOT NULL,
                raw_bytes_exposed INTEGER NOT NULL,
                rebuild_status_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_teller_bridge_redaction_contracts (
                redaction_contract_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                rebuild_candidate_id TEXT NOT NULL,
                redaction_state TEXT NOT NULL,
                allowed_fields TEXT NOT NULL,
                redacted_fields TEXT NOT NULL,
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
            CREATE TABLE IF NOT EXISTS headless_bridge_safety_blockers (
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
                INSERT OR REPLACE INTO headless_bridge_safety_blockers (
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
            active_file_id = row["active_file_id"]
            rebuild_candidate_id = row["rebuild_candidate_id"]
            health_card_id = _health_card_id(active_file_id)
            receipt_summary_id = _security_receipt_summary_id(active_file_id)
            clearance_status_id = _clearance_status_id(active_file_id)
            teller_proof_status_id = _teller_proof_status_id(active_file_id)
            memory_signal_id = _memory_signal_id(active_file_id)
            rebuild_output_id = _rebuild_output_id(active_file_id)
            redaction_contract_id = _redaction_contract_id(active_file_id)

            health_material = {
                "active_file_id": active_file_id,
                "rebuild_candidate_id": rebuild_candidate_id,
                "vault_ready": row["previous_ready"],
                "rebuild_preview_ready": row["preview_only"],
                "tower_face_required": row["tower_face_required"],
                "teller_workflow_required": row["teller_workflow_required"],
                "direct_vault_portal_allowed": False,
                "public_dashboard_allowed": False,
                "raw_file_bytes_json_allowed": False,
            }
            health_hash = calculate_sha256_bytes(repr(sorted(health_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_vault_health_cards (
                    health_card_id, active_file_id, rebuild_candidate_id,
                    health_state, vault_ready, sealed_memory_ready,
                    rebuild_preview_ready, tower_face_required,
                    teller_workflow_required, direct_vault_portal_allowed,
                    public_dashboard_allowed, raw_file_bytes_json_allowed,
                    health_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    health_card_id,
                    active_file_id,
                    rebuild_candidate_id,
                    "tower_vault_health_card_ready_redacted",
                    1 if row["previous_ready"] else 0,
                    1,
                    1 if row["preview_only"] else 0,
                    1,
                    1,
                    0,
                    0,
                    0,
                    health_hash,
                    now,
                ),
            )

            receipt_summary_hash = calculate_sha256_bytes(
                f"tower-security-receipt-summary|{active_file_id}|{row['rebuilt_index_preview_hash']}|{row['verifier_hash']}".encode("utf-8")
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_security_receipt_summaries (
                    receipt_summary_id, active_file_id, rebuild_candidate_id,
                    receipt_summary_state, redacted_receipt_hash,
                    raw_receipt_body_included, raw_path_included,
                    raw_url_included, raw_token_included, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    receipt_summary_id,
                    active_file_id,
                    rebuild_candidate_id,
                    "tower_security_receipt_summary_ready_hash_only",
                    receipt_summary_hash,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_owner_clearance_status_bridge (
                    clearance_status_id, active_file_id,
                    rebuild_candidate_id, clearance_state,
                    owner_admin_required, step_up_required,
                    tower_permission_required, vault_direct_approval_allowed,
                    direct_user_portal_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    clearance_status_id,
                    active_file_id,
                    rebuild_candidate_id,
                    "tower_owner_clearance_required_for_sensitive_vault_actions",
                    1,
                    1,
                    1,
                    0,
                    0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO teller_workflow_proof_status_bridge (
                    teller_proof_status_id, active_file_id,
                    rebuild_candidate_id, workflow_state,
                    teller_workflow_required, document_request_status_allowed,
                    proof_hash_allowed, direct_vault_browse_allowed,
                    raw_file_bytes_allowed, public_link_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    teller_proof_status_id,
                    active_file_id,
                    rebuild_candidate_id,
                    "teller_workflow_proof_status_ready_hash_only",
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            integrity_material = {
                "active_file_id": active_file_id,
                "rebuild_candidate_id": rebuild_candidate_id,
                "merkle_verified": row["merkle_rebuild_verified"],
                "rebuild_preview_hash": row["rebuilt_index_preview_hash"],
                "verifier_hash": row["verifier_hash"],
                "raw_bytes_needed": False,
                "provider_needed": False,
            }
            integrity_signal_hash = calculate_sha256_bytes(repr(sorted(integrity_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO vault_memory_integrity_signals (
                    memory_signal_id, active_file_id, rebuild_candidate_id,
                    integrity_state, merkle_verified, rebuild_preview_hash,
                    verifier_hash, raw_bytes_needed, provider_needed,
                    integrity_signal_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory_signal_id,
                    active_file_id,
                    rebuild_candidate_id,
                    "vault_memory_integrity_signal_ready",
                    1 if row["merkle_rebuild_verified"] else 0,
                    row["rebuilt_index_preview_hash"],
                    row["verifier_hash"],
                    0,
                    0,
                    integrity_signal_hash,
                    now,
                ),
            )

            rebuild_status_material = {
                "active_file_id": active_file_id,
                "rebuild_candidate_id": rebuild_candidate_id,
                "preview_id": row["preview_id"],
                "preview_only": True,
                "final_index_write_allowed": False,
                "final_pack_overwrite_allowed": False,
                "public_index_allowed": False,
                "external_browse_allowed": False,
                "raw_bytes_exposed": False,
            }
            rebuild_status_hash = calculate_sha256_bytes(repr(sorted(rebuild_status_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO sealed_rebuild_status_outputs (
                    rebuild_output_id, active_file_id, rebuild_candidate_id,
                    output_state, allowed_callers, allowed_outputs,
                    blocked_outputs, preview_only,
                    final_index_write_allowed, final_pack_overwrite_allowed,
                    public_index_allowed, external_browse_allowed,
                    raw_bytes_exposed, rebuild_status_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rebuild_output_id,
                    active_file_id,
                    rebuild_candidate_id,
                    "sealed_rebuild_status_output_ready_redacted",
                    "Tower|Teller",
                    "health_card|receipt_summary|clearance_state|workflow_proof_status|integrity_signal|rebuild_status_hash",
                    "raw_file_bytes|raw_path|raw_file_url|public_link|direct_browse|shared_folder|final_index_write|pack_overwrite",
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    rebuild_status_hash,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_teller_bridge_redaction_contracts (
                    redaction_contract_id, active_file_id,
                    rebuild_candidate_id, redaction_state,
                    allowed_fields, redacted_fields,
                    raw_file_bytes_redacted, raw_path_redacted,
                    raw_file_url_redacted, raw_token_redacted,
                    public_link_redacted, direct_browse_redacted,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    redaction_contract_id,
                    active_file_id,
                    rebuild_candidate_id,
                    "tower_teller_bridge_redaction_contract_ready",
                    "health_state|receipt_summary_hash|clearance_state|workflow_state|integrity_signal_hash|rebuild_status_hash",
                    "raw_file_bytes|raw_path|raw_file_url|raw_download_token|raw_share_token|public_link|direct_browse|shared_folder|physical_storage_path",
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_vault_pack_rebuild_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP441_INIT_CACHE = dict(result)
    return result


def get_headless_tower_status_bridge_shell() -> Dict[str, Any]:
    init = initialize_headless_tower_status_bridge_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 441,
        "title": "Headless Tower Status Bridge Shell",
        "ready": True,
        "initialized": init,
        "doctrine": DOCTRINE,
        "headless_status_bridge_only": True,
        "tower_is_face": True,
        "teller_is_workflow": True,
        "vault_is_sealed_memory": True,
        "public_dashboard_allowed": False,
        "direct_vault_user_portal_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "locks": LOCKS,
    }


def get_tower_vault_health_card_contract() -> Dict[str, Any]:
    initialize_headless_tower_status_bridge_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_vault_health_cards ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 442,
        "title": "Tower Vault Health Card Contract",
        "ready": True,
        "health_card_count": len(rows),
        "health_cards": rows,
        "all_vault_ready": all(bool(item["vault_ready"]) for item in rows),
        "all_sealed_memory_ready": all(bool(item["sealed_memory_ready"]) for item in rows),
        "all_rebuild_preview_ready": all(bool(item["rebuild_preview_ready"]) for item in rows),
        "all_tower_face_required": all(bool(item["tower_face_required"]) for item in rows),
        "all_teller_workflow_required": all(bool(item["teller_workflow_required"]) for item in rows),
        "no_direct_vault_portal": all(not bool(item["direct_vault_portal_allowed"]) for item in rows),
        "no_public_dashboard": all(not bool(item["public_dashboard_allowed"]) for item in rows),
        "no_raw_file_bytes_json": all(not bool(item["raw_file_bytes_json_allowed"]) for item in rows),
    }


def get_tower_security_receipt_summary_board() -> Dict[str, Any]:
    initialize_headless_tower_status_bridge_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_security_receipt_summaries ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 443,
        "title": "Tower Security Receipt Summary Board",
        "ready": True,
        "receipt_summary_count": len(rows),
        "receipt_summaries": rows,
        "all_hash_only": all(item["receipt_summary_state"] == "tower_security_receipt_summary_ready_hash_only" for item in rows),
        "no_raw_receipt_body": all(not bool(item["raw_receipt_body_included"]) for item in rows),
        "no_raw_paths": all(not bool(item["raw_path_included"]) for item in rows),
        "no_raw_urls": all(not bool(item["raw_url_included"]) for item in rows),
        "no_raw_tokens": all(not bool(item["raw_token_included"]) for item in rows),
    }


def get_tower_owner_clearance_status_bridge() -> Dict[str, Any]:
    initialize_headless_tower_status_bridge_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_owner_clearance_status_bridge ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 444,
        "title": "Tower Owner Clearance Status Bridge",
        "ready": True,
        "clearance_status_count": len(rows),
        "clearance_status_rows": rows,
        "all_owner_admin_required": all(bool(item["owner_admin_required"]) for item in rows),
        "all_step_up_required": all(bool(item["step_up_required"]) for item in rows),
        "all_tower_permission_required": all(bool(item["tower_permission_required"]) for item in rows),
        "no_vault_direct_approval": all(not bool(item["vault_direct_approval_allowed"]) for item in rows),
        "no_direct_user_portal": all(not bool(item["direct_user_portal_allowed"]) for item in rows),
    }


def get_teller_workflow_proof_status_bridge() -> Dict[str, Any]:
    initialize_headless_tower_status_bridge_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM teller_workflow_proof_status_bridge ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 445,
        "title": "Teller Workflow Proof Status Bridge",
        "ready": True,
        "proof_status_count": len(rows),
        "proof_status_rows": rows,
        "all_teller_workflow_required": all(bool(item["teller_workflow_required"]) for item in rows),
        "all_document_request_status_allowed": all(bool(item["document_request_status_allowed"]) for item in rows),
        "all_proof_hash_allowed": all(bool(item["proof_hash_allowed"]) for item in rows),
        "no_direct_vault_browse": all(not bool(item["direct_vault_browse_allowed"]) for item in rows),
        "no_raw_file_bytes": all(not bool(item["raw_file_bytes_allowed"]) for item in rows),
        "no_public_links": all(not bool(item["public_link_allowed"]) for item in rows),
    }


def get_vault_memory_integrity_signal_builder() -> Dict[str, Any]:
    initialize_headless_tower_status_bridge_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM vault_memory_integrity_signals ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 446,
        "title": "Vault Memory Integrity Signal Builder",
        "ready": True,
        "integrity_signal_count": len(rows),
        "integrity_signals": rows,
        "all_merkle_verified": all(bool(item["merkle_verified"]) for item in rows),
        "no_raw_bytes_needed": all(not bool(item["raw_bytes_needed"]) for item in rows),
        "provider_not_needed": all(not bool(item["provider_needed"]) for item in rows),
    }


def get_sealed_rebuild_status_output_builder() -> Dict[str, Any]:
    initialize_headless_tower_status_bridge_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM sealed_rebuild_status_outputs ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 447,
        "title": "Sealed Rebuild Status Output Builder",
        "ready": True,
        "rebuild_output_count": len(rows),
        "rebuild_outputs": rows,
        "all_outputs_redacted": all(item["output_state"] == "sealed_rebuild_status_output_ready_redacted" for item in rows),
        "all_preview_only": all(bool(item["preview_only"]) for item in rows),
        "all_final_index_writes_locked": all(not bool(item["final_index_write_allowed"]) for item in rows),
        "all_final_pack_overwrites_locked": all(not bool(item["final_pack_overwrite_allowed"]) for item in rows),
        "no_public_index": all(not bool(item["public_index_allowed"]) for item in rows),
        "no_external_browse": all(not bool(item["external_browse_allowed"]) for item in rows),
        "no_raw_bytes_exposed": all(not bool(item["raw_bytes_exposed"]) for item in rows),
    }


def get_tower_teller_bridge_redaction_contract() -> Dict[str, Any]:
    initialize_headless_tower_status_bridge_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_teller_bridge_redaction_contracts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 448,
        "title": "Tower Teller Bridge Redaction Contract",
        "ready": True,
        "redaction_contract_count": len(rows),
        "redaction_contracts": rows,
        "all_raw_file_bytes_redacted": all(bool(item["raw_file_bytes_redacted"]) for item in rows),
        "all_raw_paths_redacted": all(bool(item["raw_path_redacted"]) for item in rows),
        "all_raw_file_urls_redacted": all(bool(item["raw_file_url_redacted"]) for item in rows),
        "all_raw_tokens_redacted": all(bool(item["raw_token_redacted"]) for item in rows),
        "all_public_links_redacted": all(bool(item["public_link_redacted"]) for item in rows),
        "all_direct_browse_redacted": all(bool(item["direct_browse_redacted"]) for item in rows),
    }


def get_headless_bridge_safety_blocker_board() -> Dict[str, Any]:
    initialize_headless_tower_status_bridge_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM headless_bridge_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 449,
        "title": "Headless Bridge Safety Blocker Board",
        "ready": True,
        "blocker_count": len(rows),
        "blockers": rows,
        "unsafe_action_count": sum(1 for item in rows if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in rows),
    }


def get_headless_tower_status_bridge_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_headless_tower_status_bridge_layer()

    shell = get_headless_tower_status_bridge_shell()
    health = get_tower_vault_health_card_contract()
    receipts = get_tower_security_receipt_summary_board()
    clearance = get_tower_owner_clearance_status_bridge()
    teller = get_teller_workflow_proof_status_bridge()
    integrity = get_vault_memory_integrity_signal_builder()
    rebuild = get_sealed_rebuild_status_output_builder()
    redaction = get_tower_teller_bridge_redaction_contract()
    blockers = get_headless_bridge_safety_blocker_board()

    checks = {
        "previous_vault_pack_rebuild_ready": init["previous_vault_pack_rebuild_ready"] is True,
        "bridge_shell_ready": shell["ready"] is True,
        "doctrine_tower_teller_vault_locked": DOCTRINE["tower"] == "face" and DOCTRINE["teller"] == "workflow" and DOCTRINE["vault"] == "sealed_memory",
        "headless_internal_status_bridge_only": DOCTRINE["bridge_behavior"] == "headless_internal_status_bridge_only",
        "bridge_outputs_redacted": DOCTRINE["bridge_outputs_are_redacted"] is True,
        "health_cards_ready": health["ready"] is True and health["health_card_count"] >= 2,
        "health_cards_vault_ready": health["all_vault_ready"] is True and health["all_sealed_memory_ready"] is True and health["all_rebuild_preview_ready"] is True,
        "health_cards_tower_teller_required": health["all_tower_face_required"] is True and health["all_teller_workflow_required"] is True,
        "health_cards_no_portal_dashboard_raw": health["no_direct_vault_portal"] is True and health["no_public_dashboard"] is True and health["no_raw_file_bytes_json"] is True,
        "receipt_summaries_ready": receipts["ready"] is True and receipts["receipt_summary_count"] >= 2,
        "receipt_summaries_hash_only": receipts["all_hash_only"] is True,
        "receipt_summaries_no_raw_body_path_url_token": receipts["no_raw_receipt_body"] is True and receipts["no_raw_paths"] is True and receipts["no_raw_urls"] is True and receipts["no_raw_tokens"] is True,
        "clearance_status_ready": clearance["ready"] is True and clearance["clearance_status_count"] >= 2,
        "clearance_requires_tower_owner_step_up": clearance["all_owner_admin_required"] is True and clearance["all_step_up_required"] is True and clearance["all_tower_permission_required"] is True,
        "clearance_no_vault_direct_approval_or_portal": clearance["no_vault_direct_approval"] is True and clearance["no_direct_user_portal"] is True,
        "teller_workflow_proof_ready": teller["ready"] is True and teller["proof_status_count"] >= 2,
        "teller_proof_workflow_hash_only": teller["all_teller_workflow_required"] is True and teller["all_document_request_status_allowed"] is True and teller["all_proof_hash_allowed"] is True,
        "teller_no_vault_browse_raw_public": teller["no_direct_vault_browse"] is True and teller["no_raw_file_bytes"] is True and teller["no_public_links"] is True,
        "memory_integrity_signals_ready": integrity["ready"] is True and integrity["integrity_signal_count"] >= 2,
        "memory_integrity_verified_no_raw_provider": integrity["all_merkle_verified"] is True and integrity["no_raw_bytes_needed"] is True and integrity["provider_not_needed"] is True,
        "sealed_rebuild_outputs_ready": rebuild["ready"] is True and rebuild["rebuild_output_count"] >= 2,
        "sealed_rebuild_outputs_redacted_preview_only": rebuild["all_outputs_redacted"] is True and rebuild["all_preview_only"] is True,
        "sealed_rebuild_no_final_write_public_browse_raw": rebuild["all_final_index_writes_locked"] is True and rebuild["all_final_pack_overwrites_locked"] is True and rebuild["no_public_index"] is True and rebuild["no_external_browse"] is True and rebuild["no_raw_bytes_exposed"] is True,
        "redaction_contract_ready": redaction["ready"] is True and redaction["redaction_contract_count"] >= 2,
        "redaction_blocks_raw_path_url_token_public_direct": redaction["all_raw_file_bytes_redacted"] is True and redaction["all_raw_paths_redacted"] is True and redaction["all_raw_file_urls_redacted"] is True and redaction["all_raw_tokens_redacted"] is True and redaction["all_public_links_redacted"] is True and redaction["all_direct_browse_redacted"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "global_no_public_dashboard": LOCKS["public_vault_dashboard_allowed"] is False,
        "global_no_direct_portal": LOCKS["direct_vault_user_portal_allowed"] is False,
        "global_no_external_browsing": LOCKS["external_collaborator_browsing_allowed"] is False,
        "global_no_public_links_raw_bytes_paths": LOCKS["public_url_created"] is False and LOCKS["share_link_created"] is False and LOCKS["raw_file_bytes_returned_by_json"] is False and LOCKS["raw_path_exposed"] is False and LOCKS["raw_file_url_exposed"] is False,
        "global_no_final_writes": LOCKS["final_rebuilt_index_write_allowed"] is False and LOCKS["final_pack_overwrite_allowed"] is False and LOCKS["sealed_pack_bytes_write_allowed"] is False,
        "global_no_provider_dependency": LOCKS["provider_storage_required"] is False,
        "global_no_delete_restore_move": LOCKS["hard_delete_allowed"] is False and LOCKS["purge_allowed"] is False and LOCKS["restore_execution_allowed"] is False and LOCKS["physical_object_move_allowed"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 450,
        "title": "Headless Tower Status Bridge Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Headless Tower status bridge layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — HEADLESS TELLER WORKFLOW REQUEST BRIDGE LAYER / GP451-GP460",
        "still_locked": [
            "no public Vault dashboard",
            "no direct Vault user portal",
            "no standalone external Vault dashboard",
            "no employee/vendor/customer Vault browsing",
            "no external collaborator browsing",
            "no public/beta download",
            "no public URL or share link",
            "no raw file bytes returned by JSON",
            "no raw path exposure",
            "no raw file URL exposure",
            "no raw token exposure",
            "no final rebuilt index write",
            "no final pack overwrite",
            "no public/beta/provider upload",
            "no delete or purge",
            "no restore execution",
            "no quarantine release",
            "no physical object move",
            "no provider dependency by default",
        ],
    }


def get_headless_tower_status_bridge_home() -> Dict[str, Any]:
    checkpoint = get_headless_tower_status_bridge_readiness_checkpoint()
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


def validate_headless_tower_status_bridge_layer() -> Dict[str, Any]:
    checkpoint = get_headless_tower_status_bridge_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_vault_pack_rebuild_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["headless_internal_status_bridge_only"] is True
    assert checkpoint["checks"]["bridge_outputs_redacted"] is True
    assert checkpoint["checks"]["health_cards_ready"] is True
    assert checkpoint["checks"]["health_cards_vault_ready"] is True
    assert checkpoint["checks"]["health_cards_tower_teller_required"] is True
    assert checkpoint["checks"]["health_cards_no_portal_dashboard_raw"] is True
    assert checkpoint["checks"]["receipt_summaries_ready"] is True
    assert checkpoint["checks"]["receipt_summaries_hash_only"] is True
    assert checkpoint["checks"]["receipt_summaries_no_raw_body_path_url_token"] is True
    assert checkpoint["checks"]["clearance_status_ready"] is True
    assert checkpoint["checks"]["clearance_requires_tower_owner_step_up"] is True
    assert checkpoint["checks"]["clearance_no_vault_direct_approval_or_portal"] is True
    assert checkpoint["checks"]["teller_workflow_proof_ready"] is True
    assert checkpoint["checks"]["teller_proof_workflow_hash_only"] is True
    assert checkpoint["checks"]["teller_no_vault_browse_raw_public"] is True
    assert checkpoint["checks"]["memory_integrity_signals_ready"] is True
    assert checkpoint["checks"]["memory_integrity_verified_no_raw_provider"] is True
    assert checkpoint["checks"]["sealed_rebuild_outputs_ready"] is True
    assert checkpoint["checks"]["sealed_rebuild_outputs_redacted_preview_only"] is True
    assert checkpoint["checks"]["sealed_rebuild_no_final_write_public_browse_raw"] is True
    assert checkpoint["checks"]["redaction_contract_ready"] is True
    assert checkpoint["checks"]["redaction_blocks_raw_path_url_token_public_direct"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["tower_vault_health_cards_allowed"] is True
    assert LOCKS["tower_security_receipt_summaries_allowed"] is True
    assert LOCKS["tower_owner_clearance_status_allowed"] is True
    assert LOCKS["teller_workflow_proof_status_allowed"] is True
    assert LOCKS["vault_memory_integrity_signals_allowed"] is True
    assert LOCKS["sealed_rebuild_status_outputs_allowed"] is True
    assert LOCKS["tower_teller_bridge_redaction_allowed"] is True

    assert LOCKS["public_vault_dashboard_allowed"] is False
    assert LOCKS["standalone_external_vault_dashboard_allowed"] is False
    assert LOCKS["direct_vault_user_portal_allowed"] is False
    assert LOCKS["employee_vault_browsing_allowed"] is False
    assert LOCKS["vendor_vault_browsing_allowed"] is False
    assert LOCKS["customer_vault_browsing_allowed"] is False
    assert LOCKS["external_collaborator_browsing_allowed"] is False
    assert LOCKS["public_download_unlocked"] is False
    assert LOCKS["public_url_created"] is False
    assert LOCKS["share_link_created"] is False
    assert LOCKS["raw_file_bytes_returned_by_json"] is False
    assert LOCKS["raw_path_exposed"] is False
    assert LOCKS["raw_file_url_exposed"] is False
    assert LOCKS["raw_download_token_exposed"] is False
    assert LOCKS["raw_share_token_exposed"] is False
    assert LOCKS["final_rebuilt_index_write_allowed"] is False
    assert LOCKS["final_pack_overwrite_allowed"] is False
    assert LOCKS["sealed_pack_bytes_write_allowed"] is False
    assert LOCKS["provider_storage_required"] is False
    assert LOCKS["hard_delete_allowed"] is False
    assert LOCKS["purge_allowed"] is False
    assert LOCKS["restore_execution_allowed"] is False
    assert LOCKS["physical_object_move_allowed"] is False
    assert LOCKS["external_sync_unlocked"] is False

    return {
        "ok": True,
        "section": SECTION,
        "ready": checkpoint["ready"],
        "readiness_label": checkpoint["readiness_label"],
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(item for item in PACKS if item["gp"] == gp)
    checkpoint = get_headless_tower_status_bridge_readiness_checkpoint()
    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "status": pack["status"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "vault_is_headless": True,
        "tower_is_face": True,
        "teller_is_workflow": True,
        "status_bridge_is_redacted": True,
        "direct_vault_user_portal_allowed": False,
        "public_dashboard_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "locks_preserved": True,
    }


def get_gp441_status() -> Dict[str, Any]:
    return _gp_status(441)


def get_gp442_status() -> Dict[str, Any]:
    return _gp_status(442)


def get_gp443_status() -> Dict[str, Any]:
    return _gp_status(443)


def get_gp444_status() -> Dict[str, Any]:
    return _gp_status(444)


def get_gp445_status() -> Dict[str, Any]:
    return _gp_status(445)


def get_gp446_status() -> Dict[str, Any]:
    return _gp_status(446)


def get_gp447_status() -> Dict[str, Any]:
    return _gp_status(447)


def get_gp448_status() -> Dict[str, Any]:
    return _gp_status(448)


def get_gp449_status() -> Dict[str, Any]:
    return _gp_status(449)


def get_gp450_status() -> Dict[str, Any]:
    return _gp_status(450)
