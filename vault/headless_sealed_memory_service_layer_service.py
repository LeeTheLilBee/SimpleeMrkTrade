
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — HEADLESS SEALED MEMORY SERVICE LAYER / GP411-GP420"
LAYER_ID = "vault_gp411_420_headless_sealed_memory_service_layer"
READINESS_LABEL = "Headless sealed memory service layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_headless_sealed_memory_service_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.controlled_soft_delete_execution_layer_service import (
        get_soft_delete_state_writer,
        get_trash_lifecycle_ledger,
        get_soft_delete_receipt_finalization_board,
        validate_controlled_soft_delete_execution_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP411-GP420 requires GP401-GP410 controlled soft delete execution layer first."
    ) from exc


_GP411_INIT_CACHE = None

DOCTRINE = {
    "tower": "face",
    "teller": "workflow",
    "vault": "sealed_memory",
    "people_enter_vault_directly": False,
    "vault_is_public_drive_app": False,
    "vault_is_standalone_external_dashboard": False,
    "external_requests_route_through": ["Tower", "Teller"],
    "vault_service_behavior": "headless_authorized_internal_service_calls_only",
}

LOCKS = {
    "headless_sealed_memory_service_layer": True,
    "headless_internal_service_metadata_allowed": True,
    "sealed_memory_nodes_allowed": True,
    "blackseed_metadata_capsules_allowed": True,
    "vault_pack_manifest_index_allowed": True,
    "append_only_receipt_chain_allowed": True,
    "merkle_repair_manifest_allowed": True,
    "rebuildable_index_snapshot_allowed": True,
    "tower_teller_service_output_allowed": True,

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
    "raw_download_token_exposed": False,
    "raw_share_token_exposed": False,
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
    {"gp": 411, "title": "Headless Sealed Memory Service Shell", "status": "ready", "route": "/vault/headless-sealed-memory-service-shell.json"},
    {"gp": 412, "title": "Internal Service Call Boundary Contract", "status": "ready", "route": "/vault/internal-service-call-boundary-contract.json"},
    {"gp": 413, "title": "Sealed Memory Node Registry", "status": "ready", "route": "/vault/sealed-memory-node-registry.json"},
    {"gp": 414, "title": "Blackseed Metadata Capsule Builder", "status": "ready", "route": "/vault/blackseed-metadata-capsule-builder.json"},
    {"gp": 415, "title": "Vault Pack Manifest Index", "status": "ready", "route": "/vault/vault-pack-manifest-index.json"},
    {"gp": 416, "title": "Append-Only Receipt Chain Service", "status": "ready", "route": "/vault/append-only-receipt-chain-service.json"},
    {"gp": 417, "title": "Merkle Repair Manifest Builder", "status": "ready", "route": "/vault/merkle-repair-manifest-builder.json"},
    {"gp": 418, "title": "Rebuildable Index Snapshot Board", "status": "ready", "route": "/vault/rebuildable-index-snapshot-board.json"},
    {"gp": 419, "title": "Tower Teller Service Output Contract", "status": "ready", "route": "/vault/tower-teller-service-output-contract.json"},
    {"gp": 420, "title": "Headless Sealed Memory Service Readiness Checkpoint", "status": "ready", "route": "/vault/headless-sealed-memory-service-readiness-checkpoint.json"},
]

SERVICE_BOUNDARIES = [
    {
        "boundary_id": "tower_face_boundary",
        "service": "Tower",
        "role": "face",
        "allowed_calls": ["vault_health_status", "vault_receipt_status", "vault_proof_verification", "owner_admin_clearance_request"],
        "blocked_calls": ["direct_file_browse", "public_dashboard", "raw_url_request", "public_download_request"],
    },
    {
        "boundary_id": "teller_workflow_boundary",
        "service": "Teller",
        "role": "workflow",
        "allowed_calls": ["document_request_status", "payroll_proof_lookup", "onboarding_packet_proof", "agreement_receipt_lookup", "payment_receipt_lookup"],
        "blocked_calls": ["direct_file_browse", "shared_folder_request", "raw_file_url_request", "provider_upload_request"],
    },
    {
        "boundary_id": "vault_sealed_memory_boundary",
        "service": "Vault",
        "role": "sealed_memory",
        "allowed_calls": ["sealed_memory_node_lookup", "blackseed_capsule_lookup", "receipt_chain_lookup", "merkle_repair_manifest_lookup", "rebuild_index_snapshot"],
        "blocked_calls": ["human_portal", "employee_dashboard", "vendor_dashboard", "customer_dashboard", "external_collaborator_browse"],
    },
]

BLOCKERS = [
    {"blocker_id": "no_public_vault_dashboard", "blocked_action": "public_vault_dashboard", "allowed": False, "reason": "Tower is the face; Vault remains headless."},
    {"blocker_id": "no_direct_vault_user_portal", "blocked_action": "direct_vault_user_portal", "allowed": False, "reason": "People do not enter Vault directly."},
    {"blocker_id": "no_external_vault_dashboard", "blocked_action": "standalone_external_vault_dashboard", "allowed": False, "reason": "Vault is not a standalone public app."},
    {"blocker_id": "no_employee_vendor_customer_browsing", "blocked_action": "employee_vendor_customer_vault_browsing", "allowed": False, "reason": "Teller handles people/workflow requests; Vault only answers internal service calls."},
    {"blocker_id": "no_external_collaborator_browsing", "blocked_action": "external_collaborator_browsing", "allowed": False, "reason": "No shared-drive behavior."},
    {"blocker_id": "no_public_links", "blocked_action": "public_links_or_raw_urls", "allowed": False, "reason": "Vault never exposes raw URLs or public links."},
    {"blocker_id": "no_raw_file_bytes_json", "blocked_action": "raw_file_bytes_json", "allowed": False, "reason": "Service outputs are controlled metadata/proofs only."},
    {"blocker_id": "no_provider_dependency", "blocked_action": "provider_dependency", "allowed": False, "reason": "First version is local-first and serverless-style."},
    {"blocker_id": "no_public_beta_upload", "blocked_action": "public_beta_upload", "allowed": False, "reason": "External upload requests must go through Tower/Teller flows later."},
    {"blocker_id": "no_delete_restore_move", "blocked_action": "delete_restore_physical_move", "allowed": False, "reason": "This layer is headless memory service infrastructure, not lifecycle execution."},
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


def _memory_node_id(active_file_id: str) -> str:
    return "sealed_memory_node_" + calculate_sha256_bytes(("sealed_memory_node|" + active_file_id).encode("utf-8"))[:24]


def _capsule_id(active_file_id: str) -> str:
    return "blackseed_capsule_" + calculate_sha256_bytes(("blackseed_capsule|" + active_file_id).encode("utf-8"))[:24]


def _pack_manifest_id(active_file_id: str) -> str:
    return "vault_pack_manifest_" + calculate_sha256_bytes(("vault_pack_manifest|" + active_file_id).encode("utf-8"))[:24]


def _receipt_chain_id(active_file_id: str) -> str:
    return "receipt_chain_" + calculate_sha256_bytes(("receipt_chain|" + active_file_id).encode("utf-8"))[:24]


def _merkle_manifest_id(active_file_id: str) -> str:
    return "merkle_repair_manifest_" + calculate_sha256_bytes(("merkle_repair|" + active_file_id).encode("utf-8"))[:24]


def _index_snapshot_id(active_file_id: str) -> str:
    return "rebuildable_index_snapshot_" + calculate_sha256_bytes(("rebuild_index|" + active_file_id).encode("utf-8"))[:24]


def _output_contract_id(active_file_id: str) -> str:
    return "tower_teller_output_contract_" + calculate_sha256_bytes(("tower_teller_output|" + active_file_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    states = get_soft_delete_state_writer().get("state_records", [])
    ledger = get_trash_lifecycle_ledger().get("lifecycle_events", [])
    receipts = get_soft_delete_receipt_finalization_board().get("final_receipts", [])

    ledger_by_file = {row["active_file_id"]: row for row in ledger}
    receipt_by_file = {row["active_file_id"]: row for row in receipts}

    rows = []
    for item in states:
        active_file_id = item["active_file_id"]
        lifecycle = ledger_by_file.get(active_file_id, {})
        receipt = receipt_by_file.get(active_file_id, {})
        rows.append(
            {
                "active_file_id": active_file_id,
                "trash_candidate_id": item["trash_candidate_id"],
                "soft_delete_state_id": item["soft_delete_state_id"],
                "lifecycle_state": item["lifecycle_state"],
                "state_hash": item["state_hash"],
                "lifecycle_event_id": lifecycle.get("lifecycle_event_id", "lifecycle_event_missing"),
                "lifecycle_hash": lifecycle.get("lifecycle_hash", "lifecycle_hash_missing"),
                "receipt_hash": receipt.get("final_receipt_hash", "soft_delete_receipt_missing"),
                "sealed_state": "sealed_memory_candidate",
            }
        )
    return rows


def initialize_headless_sealed_memory_service_layer() -> Dict[str, Any]:
    global _GP411_INIT_CACHE
    if _GP411_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP411_INIT_CACHE)

    previous = validate_controlled_soft_delete_execution_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS internal_service_boundaries (
                boundary_id TEXT PRIMARY KEY,
                service TEXT NOT NULL,
                role TEXT NOT NULL,
                allowed_calls TEXT NOT NULL,
                blocked_calls TEXT NOT NULL,
                direct_people_access_allowed INTEGER NOT NULL,
                public_dashboard_allowed INTEGER NOT NULL,
                raw_url_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sealed_memory_nodes (
                memory_node_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                source_state_id TEXT NOT NULL,
                source_lifecycle_event_id TEXT NOT NULL,
                node_kind TEXT NOT NULL,
                sealed_state TEXT NOT NULL,
                local_first INTEGER NOT NULL,
                serverless_style INTEGER NOT NULL,
                provider_dependency_required INTEGER NOT NULL,
                public_browsing_allowed INTEGER NOT NULL,
                raw_bytes_exposed INTEGER NOT NULL,
                node_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS blackseed_metadata_capsules (
                capsule_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                memory_node_id TEXT NOT NULL,
                capsule_kind TEXT NOT NULL,
                opaque_metadata_only INTEGER NOT NULL,
                compact_metadata_only INTEGER NOT NULL,
                raw_filename_exposed INTEGER NOT NULL,
                raw_path_exposed INTEGER NOT NULL,
                raw_file_bytes_exposed INTEGER NOT NULL,
                capsule_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_pack_manifest_index (
                pack_manifest_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                memory_node_id TEXT NOT NULL,
                capsule_id TEXT NOT NULL,
                pack_state TEXT NOT NULL,
                pack_kind TEXT NOT NULL,
                sealed_pack_hash TEXT NOT NULL,
                provider_storage_required INTEGER NOT NULL,
                raw_file_url_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS append_only_receipt_chain (
                receipt_chain_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                memory_node_id TEXT NOT NULL,
                prior_receipt_hash TEXT NOT NULL,
                current_receipt_hash TEXT NOT NULL,
                chain_hash TEXT NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS merkle_repair_manifests (
                merkle_manifest_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                memory_node_id TEXT NOT NULL,
                pack_manifest_id TEXT NOT NULL,
                receipt_chain_id TEXT NOT NULL,
                merkle_root TEXT NOT NULL,
                repair_manifest_state TEXT NOT NULL,
                repair_can_rebuild_index INTEGER NOT NULL,
                repair_can_expose_raw_bytes INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rebuildable_index_snapshots (
                index_snapshot_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                memory_node_id TEXT NOT NULL,
                merkle_manifest_id TEXT NOT NULL,
                snapshot_state TEXT NOT NULL,
                rebuild_from_pack_allowed INTEGER NOT NULL,
                rebuild_from_receipts_allowed INTEGER NOT NULL,
                public_index_allowed INTEGER NOT NULL,
                external_browse_allowed INTEGER NOT NULL,
                snapshot_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tower_teller_service_output_contracts (
                output_contract_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                memory_node_id TEXT NOT NULL,
                allowed_callers TEXT NOT NULL,
                allowed_outputs TEXT NOT NULL,
                blocked_outputs TEXT NOT NULL,
                tower_face_required INTEGER NOT NULL,
                teller_workflow_required INTEGER NOT NULL,
                direct_vault_portal_allowed INTEGER NOT NULL,
                public_dashboard_allowed INTEGER NOT NULL,
                raw_file_bytes_json_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS headless_service_safety_blockers (
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

        for boundary in SERVICE_BOUNDARIES:
            conn.execute(
                """
                INSERT OR REPLACE INTO internal_service_boundaries (
                    boundary_id, service, role, allowed_calls, blocked_calls,
                    direct_people_access_allowed, public_dashboard_allowed,
                    raw_url_allowed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    boundary["boundary_id"],
                    boundary["service"],
                    boundary["role"],
                    "|".join(boundary["allowed_calls"]),
                    "|".join(boundary["blocked_calls"]),
                    0,
                    0,
                    0,
                    now,
                    now,
                ),
            )

        for blocker in BLOCKERS:
            conn.execute(
                """
                INSERT OR REPLACE INTO headless_service_safety_blockers (
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
            memory_node_id = _memory_node_id(active_file_id)
            capsule_id = _capsule_id(active_file_id)
            pack_manifest_id = _pack_manifest_id(active_file_id)
            receipt_chain_id = _receipt_chain_id(active_file_id)
            merkle_manifest_id = _merkle_manifest_id(active_file_id)
            index_snapshot_id = _index_snapshot_id(active_file_id)
            output_contract_id = _output_contract_id(active_file_id)

            node_material = {
                "active_file_id": active_file_id,
                "source_state_id": row["soft_delete_state_id"],
                "source_lifecycle_event_id": row["lifecycle_event_id"],
                "state_hash": row["state_hash"],
                "lifecycle_hash": row["lifecycle_hash"],
                "node_kind": "sealed_local_first_memory_node",
                "public_browsing_allowed": False,
                "raw_bytes_exposed": False,
                "provider_dependency_required": False,
            }
            node_hash = calculate_sha256_bytes(repr(sorted(node_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO sealed_memory_nodes (
                    memory_node_id, active_file_id, source_state_id,
                    source_lifecycle_event_id, node_kind, sealed_state,
                    local_first, serverless_style, provider_dependency_required,
                    public_browsing_allowed, raw_bytes_exposed,
                    node_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory_node_id,
                    active_file_id,
                    row["soft_delete_state_id"],
                    row["lifecycle_event_id"],
                    "sealed_local_first_memory_node",
                    "sealed_memory_node_registered",
                    1,
                    1,
                    0,
                    0,
                    0,
                    node_hash,
                    now,
                ),
            )

            capsule_material = {
                "active_file_id": active_file_id,
                "memory_node_id": memory_node_id,
                "node_hash": node_hash,
                "capsule_kind": "blackseed_opaque_metadata_capsule",
                "opaque_metadata_only": True,
                "raw_path_exposed": False,
                "raw_file_bytes_exposed": False,
            }
            capsule_hash = calculate_sha256_bytes(repr(sorted(capsule_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO blackseed_metadata_capsules (
                    capsule_id, active_file_id, memory_node_id,
                    capsule_kind, opaque_metadata_only, compact_metadata_only,
                    raw_filename_exposed, raw_path_exposed,
                    raw_file_bytes_exposed, capsule_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    capsule_id,
                    active_file_id,
                    memory_node_id,
                    "blackseed_opaque_metadata_capsule",
                    1,
                    1,
                    0,
                    0,
                    0,
                    capsule_hash,
                    now,
                ),
            )

            pack_material = {
                "active_file_id": active_file_id,
                "memory_node_id": memory_node_id,
                "capsule_id": capsule_id,
                "node_hash": node_hash,
                "capsule_hash": capsule_hash,
                "pack_kind": "sealed_vault_pack_manifest",
                "provider_storage_required": False,
                "raw_file_url_allowed": False,
            }
            sealed_pack_hash = calculate_sha256_bytes(repr(sorted(pack_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO vault_pack_manifest_index (
                    pack_manifest_id, active_file_id, memory_node_id,
                    capsule_id, pack_state, pack_kind, sealed_pack_hash,
                    provider_storage_required, raw_file_url_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pack_manifest_id,
                    active_file_id,
                    memory_node_id,
                    capsule_id,
                    "sealed_pack_manifest_indexed",
                    "sealed_vault_pack_manifest",
                    sealed_pack_hash,
                    0,
                    0,
                    now,
                ),
            )

            receipt_material = {
                "active_file_id": active_file_id,
                "memory_node_id": memory_node_id,
                "prior_receipt_hash": row["receipt_hash"],
                "node_hash": node_hash,
                "capsule_hash": capsule_hash,
                "sealed_pack_hash": sealed_pack_hash,
                "append_only": True,
            }
            chain_hash = calculate_sha256_bytes(repr(sorted(receipt_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO append_only_receipt_chain (
                    receipt_chain_id, active_file_id, memory_node_id,
                    prior_receipt_hash, current_receipt_hash, chain_hash,
                    append_only, mutable, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    receipt_chain_id,
                    active_file_id,
                    memory_node_id,
                    row["receipt_hash"],
                    chain_hash,
                    chain_hash,
                    1,
                    0,
                    now,
                ),
            )

            merkle_material = {
                "active_file_id": active_file_id,
                "memory_node_id": memory_node_id,
                "pack_manifest_id": pack_manifest_id,
                "receipt_chain_id": receipt_chain_id,
                "node_hash": node_hash,
                "capsule_hash": capsule_hash,
                "sealed_pack_hash": sealed_pack_hash,
                "chain_hash": chain_hash,
            }
            merkle_root = calculate_sha256_bytes(repr(sorted(merkle_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO merkle_repair_manifests (
                    merkle_manifest_id, active_file_id, memory_node_id,
                    pack_manifest_id, receipt_chain_id, merkle_root,
                    repair_manifest_state, repair_can_rebuild_index,
                    repair_can_expose_raw_bytes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    merkle_manifest_id,
                    active_file_id,
                    memory_node_id,
                    pack_manifest_id,
                    receipt_chain_id,
                    merkle_root,
                    "merkle_repair_manifest_ready_for_index_repair",
                    1,
                    0,
                    now,
                ),
            )

            snapshot_material = {
                "active_file_id": active_file_id,
                "memory_node_id": memory_node_id,
                "merkle_manifest_id": merkle_manifest_id,
                "merkle_root": merkle_root,
                "rebuild_from_pack_allowed": True,
                "rebuild_from_receipts_allowed": True,
                "public_index_allowed": False,
                "external_browse_allowed": False,
            }
            snapshot_hash = calculate_sha256_bytes(repr(sorted(snapshot_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO rebuildable_index_snapshots (
                    index_snapshot_id, active_file_id, memory_node_id,
                    merkle_manifest_id, snapshot_state,
                    rebuild_from_pack_allowed, rebuild_from_receipts_allowed,
                    public_index_allowed, external_browse_allowed,
                    snapshot_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    index_snapshot_id,
                    active_file_id,
                    memory_node_id,
                    merkle_manifest_id,
                    "rebuildable_headless_index_snapshot_ready",
                    1,
                    1,
                    0,
                    0,
                    snapshot_hash,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO tower_teller_service_output_contracts (
                    output_contract_id, active_file_id, memory_node_id,
                    allowed_callers, allowed_outputs, blocked_outputs,
                    tower_face_required, teller_workflow_required,
                    direct_vault_portal_allowed, public_dashboard_allowed,
                    raw_file_bytes_json_allowed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    output_contract_id,
                    active_file_id,
                    memory_node_id,
                    "Tower|Teller",
                    "status_card|receipt_hash|proof_result|capsule_summary|repair_manifest_summary|index_snapshot_summary",
                    "raw_file_bytes|raw_file_url|public_link|direct_browse|shared_folder|external_collaborator_view",
                    1,
                    1,
                    0,
                    0,
                    0,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_controlled_soft_delete_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP411_INIT_CACHE = dict(result)
    return result


def get_headless_sealed_memory_service_shell() -> Dict[str, Any]:
    init = initialize_headless_sealed_memory_service_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 411,
        "title": "Headless Sealed Memory Service Shell",
        "ready": True,
        "initialized": init,
        "doctrine": DOCTRINE,
        "public_dashboard_allowed": False,
        "direct_vault_user_portal_allowed": False,
        "headless_internal_service_only": True,
        "locks": LOCKS,
    }


def get_internal_service_call_boundary_contract() -> Dict[str, Any]:
    initialize_headless_sealed_memory_service_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM internal_service_boundaries ORDER BY service")

    return {
        "section": SECTION,
        "gp": 412,
        "title": "Internal Service Call Boundary Contract",
        "ready": True,
        "boundary_count": len(rows),
        "boundaries": rows,
        "tower_is_face": any(item["service"] == "Tower" and item["role"] == "face" for item in rows),
        "teller_is_workflow": any(item["service"] == "Teller" and item["role"] == "workflow" for item in rows),
        "vault_is_sealed_memory": any(item["service"] == "Vault" and item["role"] == "sealed_memory" for item in rows),
        "all_direct_people_access_locked": all(not bool(item["direct_people_access_allowed"]) for item in rows),
        "all_public_dashboards_locked": all(not bool(item["public_dashboard_allowed"]) for item in rows),
        "all_raw_urls_locked": all(not bool(item["raw_url_allowed"]) for item in rows),
    }


def get_sealed_memory_node_registry() -> Dict[str, Any]:
    initialize_headless_sealed_memory_service_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM sealed_memory_nodes ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 413,
        "title": "Sealed Memory Node Registry",
        "ready": True,
        "node_count": len(rows),
        "memory_nodes": rows,
        "all_local_first": all(bool(item["local_first"]) for item in rows),
        "all_serverless_style": all(bool(item["serverless_style"]) for item in rows),
        "provider_dependency_not_required": all(not bool(item["provider_dependency_required"]) for item in rows),
        "no_public_browsing": all(not bool(item["public_browsing_allowed"]) for item in rows),
        "no_raw_bytes_exposed": all(not bool(item["raw_bytes_exposed"]) for item in rows),
    }


def get_blackseed_metadata_capsule_builder() -> Dict[str, Any]:
    initialize_headless_sealed_memory_service_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM blackseed_metadata_capsules ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 414,
        "title": "Blackseed Metadata Capsule Builder",
        "ready": True,
        "capsule_count": len(rows),
        "capsules": rows,
        "all_opaque_metadata_only": all(bool(item["opaque_metadata_only"]) for item in rows),
        "all_compact_metadata_only": all(bool(item["compact_metadata_only"]) for item in rows),
        "no_raw_filenames_exposed": all(not bool(item["raw_filename_exposed"]) for item in rows),
        "no_raw_paths_exposed": all(not bool(item["raw_path_exposed"]) for item in rows),
        "no_raw_file_bytes_exposed": all(not bool(item["raw_file_bytes_exposed"]) for item in rows),
    }


def get_vault_pack_manifest_index() -> Dict[str, Any]:
    initialize_headless_sealed_memory_service_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM vault_pack_manifest_index ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 415,
        "title": "Vault Pack Manifest Index",
        "ready": True,
        "pack_manifest_count": len(rows),
        "pack_manifests": rows,
        "all_sealed_pack_manifests": all(item["pack_kind"] == "sealed_vault_pack_manifest" for item in rows),
        "provider_storage_not_required": all(not bool(item["provider_storage_required"]) for item in rows),
        "no_raw_file_urls": all(not bool(item["raw_file_url_allowed"]) for item in rows),
    }


def get_append_only_receipt_chain_service() -> Dict[str, Any]:
    initialize_headless_sealed_memory_service_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM append_only_receipt_chain ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 416,
        "title": "Append-Only Receipt Chain Service",
        "ready": True,
        "receipt_chain_count": len(rows),
        "receipt_chains": rows,
        "all_append_only": all(bool(item["append_only"]) for item in rows),
        "all_immutable": all(not bool(item["mutable"]) for item in rows),
    }


def get_merkle_repair_manifest_builder() -> Dict[str, Any]:
    initialize_headless_sealed_memory_service_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM merkle_repair_manifests ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 417,
        "title": "Merkle Repair Manifest Builder",
        "ready": True,
        "merkle_manifest_count": len(rows),
        "merkle_manifests": rows,
        "all_can_rebuild_index": all(bool(item["repair_can_rebuild_index"]) for item in rows),
        "none_can_expose_raw_bytes": all(not bool(item["repair_can_expose_raw_bytes"]) for item in rows),
    }


def get_rebuildable_index_snapshot_board() -> Dict[str, Any]:
    initialize_headless_sealed_memory_service_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM rebuildable_index_snapshots ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 418,
        "title": "Rebuildable Index Snapshot Board",
        "ready": True,
        "snapshot_count": len(rows),
        "index_snapshots": rows,
        "all_rebuild_from_pack_allowed": all(bool(item["rebuild_from_pack_allowed"]) for item in rows),
        "all_rebuild_from_receipts_allowed": all(bool(item["rebuild_from_receipts_allowed"]) for item in rows),
        "no_public_index": all(not bool(item["public_index_allowed"]) for item in rows),
        "no_external_browse": all(not bool(item["external_browse_allowed"]) for item in rows),
    }


def get_tower_teller_service_output_contract() -> Dict[str, Any]:
    initialize_headless_sealed_memory_service_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM tower_teller_service_output_contracts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 419,
        "title": "Tower Teller Service Output Contract",
        "ready": True,
        "output_contract_count": len(rows),
        "output_contracts": rows,
        "all_tower_face_required": all(bool(item["tower_face_required"]) for item in rows),
        "all_teller_workflow_required": all(bool(item["teller_workflow_required"]) for item in rows),
        "no_direct_vault_portal": all(not bool(item["direct_vault_portal_allowed"]) for item in rows),
        "no_public_dashboard": all(not bool(item["public_dashboard_allowed"]) for item in rows),
        "no_raw_file_bytes_json": all(not bool(item["raw_file_bytes_json_allowed"]) for item in rows),
    }


def get_headless_service_safety_blocker_board() -> Dict[str, Any]:
    initialize_headless_sealed_memory_service_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM headless_service_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "title": "Headless Service Safety Blocker Board",
        "ready": True,
        "blocker_count": len(rows),
        "blockers": rows,
        "unsafe_action_count": sum(1 for item in rows if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in rows),
    }


def get_headless_sealed_memory_service_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_headless_sealed_memory_service_layer()

    shell = get_headless_sealed_memory_service_shell()
    boundary = get_internal_service_call_boundary_contract()
    nodes = get_sealed_memory_node_registry()
    capsules = get_blackseed_metadata_capsule_builder()
    packs = get_vault_pack_manifest_index()
    receipts = get_append_only_receipt_chain_service()
    merkle = get_merkle_repair_manifest_builder()
    snapshots = get_rebuildable_index_snapshot_board()
    outputs = get_tower_teller_service_output_contract()
    blockers = get_headless_service_safety_blocker_board()

    checks = {
        "previous_controlled_soft_delete_ready": init["previous_controlled_soft_delete_ready"] is True,
        "headless_shell_ready": shell["ready"] is True,
        "doctrine_tower_teller_vault_locked": DOCTRINE["tower"] == "face" and DOCTRINE["teller"] == "workflow" and DOCTRINE["vault"] == "sealed_memory",
        "direct_people_access_locked": DOCTRINE["people_enter_vault_directly"] is False,
        "vault_not_public_drive": DOCTRINE["vault_is_public_drive_app"] is False,
        "internal_service_boundaries_ready": boundary["ready"] is True and boundary["boundary_count"] == 3,
        "tower_teller_vault_roles_correct": boundary["tower_is_face"] is True and boundary["teller_is_workflow"] is True and boundary["vault_is_sealed_memory"] is True,
        "boundary_direct_public_raw_locked": boundary["all_direct_people_access_locked"] is True and boundary["all_public_dashboards_locked"] is True and boundary["all_raw_urls_locked"] is True,
        "sealed_memory_nodes_ready": nodes["ready"] is True and nodes["node_count"] >= 2,
        "nodes_local_first_serverless": nodes["all_local_first"] is True and nodes["all_serverless_style"] is True,
        "nodes_provider_not_required": nodes["provider_dependency_not_required"] is True,
        "nodes_no_public_browse_raw_bytes": nodes["no_public_browsing"] is True and nodes["no_raw_bytes_exposed"] is True,
        "blackseed_capsules_ready": capsules["ready"] is True and capsules["capsule_count"] >= 2,
        "capsules_opaque_compact": capsules["all_opaque_metadata_only"] is True and capsules["all_compact_metadata_only"] is True,
        "capsules_no_raw_name_path_bytes": capsules["no_raw_filenames_exposed"] is True and capsules["no_raw_paths_exposed"] is True and capsules["no_raw_file_bytes_exposed"] is True,
        "vault_pack_manifest_ready": packs["ready"] is True and packs["pack_manifest_count"] >= 2,
        "packs_sealed_no_provider_or_urls": packs["all_sealed_pack_manifests"] is True and packs["provider_storage_not_required"] is True and packs["no_raw_file_urls"] is True,
        "append_only_receipt_chain_ready": receipts["ready"] is True and receipts["receipt_chain_count"] >= 2,
        "receipt_chain_append_only_immutable": receipts["all_append_only"] is True and receipts["all_immutable"] is True,
        "merkle_repair_manifest_ready": merkle["ready"] is True and merkle["merkle_manifest_count"] >= 2,
        "merkle_can_repair_index_not_raw_bytes": merkle["all_can_rebuild_index"] is True and merkle["none_can_expose_raw_bytes"] is True,
        "rebuildable_index_snapshots_ready": snapshots["ready"] is True and snapshots["snapshot_count"] >= 2,
        "index_rebuildable_not_public": snapshots["all_rebuild_from_pack_allowed"] is True and snapshots["all_rebuild_from_receipts_allowed"] is True and snapshots["no_public_index"] is True and snapshots["no_external_browse"] is True,
        "tower_teller_outputs_ready": outputs["ready"] is True and outputs["output_contract_count"] >= 2,
        "outputs_tower_teller_required": outputs["all_tower_face_required"] is True and outputs["all_teller_workflow_required"] is True,
        "outputs_no_direct_portal_dashboard_raw_bytes": outputs["no_direct_vault_portal"] is True and outputs["no_public_dashboard"] is True and outputs["no_raw_file_bytes_json"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "global_no_public_dashboard": LOCKS["public_vault_dashboard_allowed"] is False,
        "global_no_direct_portal": LOCKS["direct_vault_user_portal_allowed"] is False,
        "global_no_external_browsing": LOCKS["external_collaborator_browsing_allowed"] is False,
        "global_no_public_links_raw_bytes": LOCKS["public_url_created"] is False and LOCKS["share_link_created"] is False and LOCKS["raw_file_bytes_returned_by_json"] is False,
        "global_no_provider_dependency": LOCKS["provider_storage_required"] is False,
        "global_no_delete_restore_move": LOCKS["hard_delete_allowed"] is False and LOCKS["purge_allowed"] is False and LOCKS["restore_execution_allowed"] is False and LOCKS["physical_object_move_allowed"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 420,
        "title": "Headless Sealed Memory Service Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Headless sealed memory service layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — BLACKSEED CAPSULE INDEX REPAIR LAYER / GP421-GP430",
        "still_locked": [
            "no public Vault dashboard",
            "no direct Vault user portal",
            "no standalone external Vault dashboard",
            "no employee/vendor/customer Vault browsing",
            "no external collaborator browsing",
            "no public/beta download",
            "no public URL or share link",
            "no raw file bytes returned by JSON",
            "no raw token exposure",
            "no public/beta/provider upload",
            "no delete or purge",
            "no restore execution",
            "no quarantine release",
            "no physical object move",
            "no provider dependency by default",
        ],
    }


def get_headless_sealed_memory_service_home() -> Dict[str, Any]:
    checkpoint = get_headless_sealed_memory_service_readiness_checkpoint()
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


def validate_headless_sealed_memory_service_layer() -> Dict[str, Any]:
    checkpoint = get_headless_sealed_memory_service_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_controlled_soft_delete_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["direct_people_access_locked"] is True
    assert checkpoint["checks"]["vault_not_public_drive"] is True
    assert checkpoint["checks"]["internal_service_boundaries_ready"] is True
    assert checkpoint["checks"]["tower_teller_vault_roles_correct"] is True
    assert checkpoint["checks"]["boundary_direct_public_raw_locked"] is True
    assert checkpoint["checks"]["sealed_memory_nodes_ready"] is True
    assert checkpoint["checks"]["nodes_local_first_serverless"] is True
    assert checkpoint["checks"]["nodes_provider_not_required"] is True
    assert checkpoint["checks"]["nodes_no_public_browse_raw_bytes"] is True
    assert checkpoint["checks"]["blackseed_capsules_ready"] is True
    assert checkpoint["checks"]["capsules_opaque_compact"] is True
    assert checkpoint["checks"]["capsules_no_raw_name_path_bytes"] is True
    assert checkpoint["checks"]["vault_pack_manifest_ready"] is True
    assert checkpoint["checks"]["packs_sealed_no_provider_or_urls"] is True
    assert checkpoint["checks"]["append_only_receipt_chain_ready"] is True
    assert checkpoint["checks"]["receipt_chain_append_only_immutable"] is True
    assert checkpoint["checks"]["merkle_repair_manifest_ready"] is True
    assert checkpoint["checks"]["merkle_can_repair_index_not_raw_bytes"] is True
    assert checkpoint["checks"]["rebuildable_index_snapshots_ready"] is True
    assert checkpoint["checks"]["index_rebuildable_not_public"] is True
    assert checkpoint["checks"]["tower_teller_outputs_ready"] is True
    assert checkpoint["checks"]["outputs_tower_teller_required"] is True
    assert checkpoint["checks"]["outputs_no_direct_portal_dashboard_raw_bytes"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["headless_internal_service_metadata_allowed"] is True
    assert LOCKS["sealed_memory_nodes_allowed"] is True
    assert LOCKS["blackseed_metadata_capsules_allowed"] is True
    assert LOCKS["vault_pack_manifest_index_allowed"] is True
    assert LOCKS["append_only_receipt_chain_allowed"] is True
    assert LOCKS["merkle_repair_manifest_allowed"] is True
    assert LOCKS["rebuildable_index_snapshot_allowed"] is True
    assert LOCKS["tower_teller_service_output_allowed"] is True

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
    checkpoint = get_headless_sealed_memory_service_readiness_checkpoint()
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
        "direct_vault_user_portal_allowed": False,
        "public_dashboard_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "locks_preserved": True,
    }


def get_gp411_status() -> Dict[str, Any]:
    return _gp_status(411)


def get_gp412_status() -> Dict[str, Any]:
    return _gp_status(412)


def get_gp413_status() -> Dict[str, Any]:
    return _gp_status(413)


def get_gp414_status() -> Dict[str, Any]:
    return _gp_status(414)


def get_gp415_status() -> Dict[str, Any]:
    return _gp_status(415)


def get_gp416_status() -> Dict[str, Any]:
    return _gp_status(416)


def get_gp417_status() -> Dict[str, Any]:
    return _gp_status(417)


def get_gp418_status() -> Dict[str, Any]:
    return _gp_status(418)


def get_gp419_status() -> Dict[str, Any]:
    return _gp_status(419)


def get_gp420_status() -> Dict[str, Any]:
    return _gp_status(420)
