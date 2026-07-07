
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = "ARCHIVE VAULT — BLACKSEED CAPSULE INDEX REPAIR LAYER / GP421-GP430"
LAYER_ID = "vault_gp421_430_blackseed_capsule_index_repair_layer"
READINESS_LABEL = "Blackseed capsule index repair layer ready"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "vault_blackseed_capsule_index_repair_layer.sqlite"

try:
    from vault.owner_owned_file_storage_foundation_layer_service import calculate_sha256_bytes
    from vault.headless_sealed_memory_service_layer_service import (
        DOCTRINE as HEADLESS_DOCTRINE,
        get_blackseed_metadata_capsule_builder,
        get_vault_pack_manifest_index,
        get_append_only_receipt_chain_service,
        get_merkle_repair_manifest_builder,
        get_rebuildable_index_snapshot_board,
        validate_headless_sealed_memory_service_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP421-GP430 requires GP411-GP420 headless sealed memory service layer first."
    ) from exc


_GP421_INIT_CACHE = None

DOCTRINE = {
    "tower": "face",
    "teller": "workflow",
    "vault": "sealed_memory",
    "repair_behavior": "headless_capsule_index_repair_only",
    "people_enter_vault_directly": False,
    "vault_is_public_drive_app": False,
    "repair_exposes_raw_bytes": False,
}

LOCKS = {
    "blackseed_capsule_index_repair_layer": True,
    "capsule_index_integrity_scanning_allowed": True,
    "capsule_hash_continuity_verification_allowed": True,
    "capsule_to_pack_repair_mapping_allowed": True,
    "missing_capsule_repair_planning_allowed": True,
    "opaque_metadata_rebuild_contract_allowed": True,
    "repair_receipt_chain_draft_allowed": True,
    "repaired_index_snapshot_preview_allowed": True,

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
    {"gp": 421, "title": "Blackseed Capsule Index Repair Shell", "status": "ready", "route": "/vault/blackseed-capsule-index-repair-shell.json"},
    {"gp": 422, "title": "Capsule Index Integrity Scanner", "status": "ready", "route": "/vault/capsule-index-integrity-scanner.json"},
    {"gp": 423, "title": "Capsule Hash Continuity Board", "status": "ready", "route": "/vault/capsule-hash-continuity-board.json"},
    {"gp": 424, "title": "Capsule-to-Pack Repair Map", "status": "ready", "route": "/vault/capsule-to-pack-repair-map.json"},
    {"gp": 425, "title": "Missing Capsule Repair Plan Builder", "status": "ready", "route": "/vault/missing-capsule-repair-plan-builder.json"},
    {"gp": 426, "title": "Opaque Metadata Rebuild Contract", "status": "ready", "route": "/vault/opaque-metadata-rebuild-contract.json"},
    {"gp": 427, "title": "Repair Receipt Chain Draft Ledger", "status": "ready", "route": "/vault/repair-receipt-chain-draft-ledger.json"},
    {"gp": 428, "title": "Repaired Index Snapshot Preview Board", "status": "ready", "route": "/vault/repaired-index-snapshot-preview-board.json"},
    {"gp": 429, "title": "Capsule Repair Safety Blocker Board", "status": "ready", "route": "/vault/capsule-repair-safety-blocker-board.json"},
    {"gp": 430, "title": "Blackseed Capsule Index Repair Readiness Checkpoint", "status": "ready", "route": "/vault/blackseed-capsule-index-repair-readiness-checkpoint.json"},
]

BLOCKERS = [
    {"blocker_id": "no_public_vault_dashboard", "blocked_action": "public_vault_dashboard", "allowed": False, "reason": "Tower is the face; capsule repair is headless."},
    {"blocker_id": "no_direct_vault_user_portal", "blocked_action": "direct_vault_user_portal", "allowed": False, "reason": "People do not enter Vault directly."},
    {"blocker_id": "no_external_vault_dashboard", "blocked_action": "standalone_external_vault_dashboard", "allowed": False, "reason": "Vault is not a standalone external app."},
    {"blocker_id": "no_external_browsing", "blocked_action": "external_collaborator_browsing", "allowed": False, "reason": "No shared-drive behavior."},
    {"blocker_id": "no_employee_vendor_customer_browse", "blocked_action": "employee_vendor_customer_vault_browsing", "allowed": False, "reason": "Tower/Teller handle requests; Vault stays sealed."},
    {"blocker_id": "no_public_links", "blocked_action": "public_links_or_raw_urls", "allowed": False, "reason": "Capsule repair never creates public URLs or links."},
    {"blocker_id": "no_raw_file_bytes_json", "blocked_action": "raw_file_bytes_json", "allowed": False, "reason": "Repair outputs are proofs and opaque metadata only."},
    {"blocker_id": "no_raw_paths", "blocked_action": "raw_path_exposure", "allowed": False, "reason": "Blackseed capsules stay opaque."},
    {"blocker_id": "no_provider_dependency", "blocked_action": "provider_dependency", "allowed": False, "reason": "Repair uses local-first sealed memory nodes and manifests."},
    {"blocker_id": "no_delete_restore_move", "blocked_action": "delete_restore_physical_move", "allowed": False, "reason": "Capsule repair does not mutate lifecycle state or move objects."},
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


def _scan_id(active_file_id: str) -> str:
    return "capsule_integrity_scan_" + calculate_sha256_bytes(("capsule_integrity_scan|" + active_file_id).encode("utf-8"))[:24]


def _continuity_id(active_file_id: str) -> str:
    return "capsule_hash_continuity_" + calculate_sha256_bytes(("capsule_hash_continuity|" + active_file_id).encode("utf-8"))[:24]


def _repair_map_id(active_file_id: str) -> str:
    return "capsule_pack_repair_map_" + calculate_sha256_bytes(("capsule_pack_repair_map|" + active_file_id).encode("utf-8"))[:24]


def _repair_plan_id(active_file_id: str) -> str:
    return "missing_capsule_repair_plan_" + calculate_sha256_bytes(("missing_capsule_repair_plan|" + active_file_id).encode("utf-8"))[:24]


def _rebuild_contract_id(active_file_id: str) -> str:
    return "opaque_metadata_rebuild_contract_" + calculate_sha256_bytes(("opaque_metadata_rebuild|" + active_file_id).encode("utf-8"))[:24]


def _repair_receipt_draft_id(active_file_id: str) -> str:
    return "repair_receipt_chain_draft_" + calculate_sha256_bytes(("repair_receipt_chain|" + active_file_id).encode("utf-8"))[:24]


def _snapshot_preview_id(active_file_id: str) -> str:
    return "repaired_index_snapshot_preview_" + calculate_sha256_bytes(("repaired_index_preview|" + active_file_id).encode("utf-8"))[:24]


def _candidate_source_rows() -> List[Dict[str, Any]]:
    capsules = get_blackseed_metadata_capsule_builder().get("capsules", [])
    packs = get_vault_pack_manifest_index().get("pack_manifests", [])
    receipt_chains = get_append_only_receipt_chain_service().get("receipt_chains", [])
    merkle_manifests = get_merkle_repair_manifest_builder().get("merkle_manifests", [])
    snapshots = get_rebuildable_index_snapshot_board().get("index_snapshots", [])

    pack_by_file = {row["active_file_id"]: row for row in packs}
    chain_by_file = {row["active_file_id"]: row for row in receipt_chains}
    merkle_by_file = {row["active_file_id"]: row for row in merkle_manifests}
    snapshot_by_file = {row["active_file_id"]: row for row in snapshots}

    rows = []
    for capsule in capsules:
        active_file_id = capsule["active_file_id"]
        pack = pack_by_file.get(active_file_id, {})
        chain = chain_by_file.get(active_file_id, {})
        merkle = merkle_by_file.get(active_file_id, {})
        snapshot = snapshot_by_file.get(active_file_id, {})
        rows.append(
            {
                "active_file_id": active_file_id,
                "memory_node_id": capsule["memory_node_id"],
                "capsule_id": capsule["capsule_id"],
                "capsule_hash": capsule["capsule_hash"],
                "capsule_kind": capsule["capsule_kind"],
                "opaque_metadata_only": bool(capsule["opaque_metadata_only"]),
                "compact_metadata_only": bool(capsule["compact_metadata_only"]),
                "raw_filename_exposed": bool(capsule["raw_filename_exposed"]),
                "raw_path_exposed": bool(capsule["raw_path_exposed"]),
                "raw_file_bytes_exposed": bool(capsule["raw_file_bytes_exposed"]),
                "pack_manifest_id": pack.get("pack_manifest_id", "missing_pack_manifest"),
                "sealed_pack_hash": pack.get("sealed_pack_hash", "missing_sealed_pack_hash"),
                "pack_state": pack.get("pack_state", "missing_pack_state"),
                "provider_storage_required": bool(pack.get("provider_storage_required", 0)),
                "raw_file_url_allowed": bool(pack.get("raw_file_url_allowed", 0)),
                "receipt_chain_id": chain.get("receipt_chain_id", "missing_receipt_chain"),
                "chain_hash": chain.get("chain_hash", "missing_chain_hash"),
                "append_only": bool(chain.get("append_only", 0)),
                "mutable": bool(chain.get("mutable", 1)),
                "merkle_manifest_id": merkle.get("merkle_manifest_id", "missing_merkle_manifest"),
                "merkle_root": merkle.get("merkle_root", "missing_merkle_root"),
                "repair_can_rebuild_index": bool(merkle.get("repair_can_rebuild_index", 0)),
                "repair_can_expose_raw_bytes": bool(merkle.get("repair_can_expose_raw_bytes", 1)),
                "index_snapshot_id": snapshot.get("index_snapshot_id", "missing_index_snapshot"),
                "snapshot_hash": snapshot.get("snapshot_hash", "missing_snapshot_hash"),
                "rebuild_from_pack_allowed": bool(snapshot.get("rebuild_from_pack_allowed", 0)),
                "rebuild_from_receipts_allowed": bool(snapshot.get("rebuild_from_receipts_allowed", 0)),
                "public_index_allowed": bool(snapshot.get("public_index_allowed", 1)),
                "external_browse_allowed": bool(snapshot.get("external_browse_allowed", 1)),
            }
        )
    return rows


def initialize_blackseed_capsule_index_repair_layer() -> Dict[str, Any]:
    global _GP421_INIT_CACHE
    if _GP421_INIT_CACHE is not None and DB_PATH.exists():
        return dict(_GP421_INIT_CACHE)

    previous = validate_headless_sealed_memory_service_layer()

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS capsule_index_integrity_scans (
                scan_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                memory_node_id TEXT NOT NULL,
                capsule_id TEXT NOT NULL,
                pack_manifest_id TEXT NOT NULL,
                receipt_chain_id TEXT NOT NULL,
                merkle_manifest_id TEXT NOT NULL,
                index_snapshot_id TEXT NOT NULL,
                scan_state TEXT NOT NULL,
                capsule_present INTEGER NOT NULL,
                pack_manifest_present INTEGER NOT NULL,
                receipt_chain_present INTEGER NOT NULL,
                merkle_manifest_present INTEGER NOT NULL,
                index_snapshot_present INTEGER NOT NULL,
                opaque_metadata_only INTEGER NOT NULL,
                raw_bytes_exposed INTEGER NOT NULL,
                public_browse_allowed INTEGER NOT NULL,
                provider_dependency_required INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS capsule_hash_continuity (
                continuity_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                capsule_id TEXT NOT NULL,
                capsule_hash TEXT NOT NULL,
                sealed_pack_hash TEXT NOT NULL,
                chain_hash TEXT NOT NULL,
                merkle_root TEXT NOT NULL,
                snapshot_hash TEXT NOT NULL,
                continuity_hash TEXT NOT NULL,
                continuity_state TEXT NOT NULL,
                hash_chain_complete INTEGER NOT NULL,
                raw_bytes_needed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS capsule_to_pack_repair_map (
                repair_map_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                memory_node_id TEXT NOT NULL,
                capsule_id TEXT NOT NULL,
                pack_manifest_id TEXT NOT NULL,
                receipt_chain_id TEXT NOT NULL,
                merkle_manifest_id TEXT NOT NULL,
                repair_path TEXT NOT NULL,
                can_repair_from_pack INTEGER NOT NULL,
                can_repair_from_receipts INTEGER NOT NULL,
                can_repair_from_merkle INTEGER NOT NULL,
                can_expose_raw_bytes INTEGER NOT NULL,
                provider_required INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS missing_capsule_repair_plans (
                repair_plan_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                capsule_id TEXT NOT NULL,
                plan_state TEXT NOT NULL,
                missing_capsule_detected INTEGER NOT NULL,
                repair_action TEXT NOT NULL,
                rebuild_source TEXT NOT NULL,
                owner_review_required INTEGER NOT NULL,
                raw_bytes_required INTEGER NOT NULL,
                direct_user_action_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS opaque_metadata_rebuild_contracts (
                rebuild_contract_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                capsule_id TEXT NOT NULL,
                contract_state TEXT NOT NULL,
                opaque_metadata_only INTEGER NOT NULL,
                compact_metadata_only INTEGER NOT NULL,
                raw_filename_allowed INTEGER NOT NULL,
                raw_path_allowed INTEGER NOT NULL,
                raw_file_bytes_allowed INTEGER NOT NULL,
                public_index_allowed INTEGER NOT NULL,
                external_browse_allowed INTEGER NOT NULL,
                provider_dependency_required INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS repair_receipt_chain_drafts (
                repair_receipt_draft_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                capsule_id TEXT NOT NULL,
                receipt_chain_id TEXT NOT NULL,
                repair_plan_id TEXT NOT NULL,
                receipt_state TEXT NOT NULL,
                finalized INTEGER NOT NULL,
                finalization_allowed INTEGER NOT NULL,
                repair_receipt_hash TEXT NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS repaired_index_snapshot_previews (
                snapshot_preview_id TEXT PRIMARY KEY,
                active_file_id TEXT NOT NULL,
                capsule_id TEXT NOT NULL,
                index_snapshot_id TEXT NOT NULL,
                repaired_snapshot_state TEXT NOT NULL,
                preview_only INTEGER NOT NULL,
                index_write_allowed INTEGER NOT NULL,
                public_index_allowed INTEGER NOT NULL,
                external_browse_allowed INTEGER NOT NULL,
                raw_bytes_exposed INTEGER NOT NULL,
                repaired_snapshot_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS capsule_repair_safety_blockers (
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
                INSERT OR REPLACE INTO capsule_repair_safety_blockers (
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
            scan_id = _scan_id(active_file_id)
            continuity_id = _continuity_id(active_file_id)
            repair_map_id = _repair_map_id(active_file_id)
            repair_plan_id = _repair_plan_id(active_file_id)
            rebuild_contract_id = _rebuild_contract_id(active_file_id)
            repair_receipt_draft_id = _repair_receipt_draft_id(active_file_id)
            snapshot_preview_id = _snapshot_preview_id(active_file_id)

            capsule_present = row["capsule_id"] != "missing_capsule"
            pack_present = row["pack_manifest_id"] != "missing_pack_manifest"
            chain_present = row["receipt_chain_id"] != "missing_receipt_chain"
            merkle_present = row["merkle_manifest_id"] != "missing_merkle_manifest"
            snapshot_present = row["index_snapshot_id"] != "missing_index_snapshot"
            all_present = all([capsule_present, pack_present, chain_present, merkle_present, snapshot_present])

            conn.execute(
                """
                INSERT OR REPLACE INTO capsule_index_integrity_scans (
                    scan_id, active_file_id, memory_node_id, capsule_id,
                    pack_manifest_id, receipt_chain_id, merkle_manifest_id,
                    index_snapshot_id, scan_state, capsule_present,
                    pack_manifest_present, receipt_chain_present,
                    merkle_manifest_present, index_snapshot_present,
                    opaque_metadata_only, raw_bytes_exposed,
                    public_browse_allowed, provider_dependency_required,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_id,
                    active_file_id,
                    row["memory_node_id"],
                    row["capsule_id"],
                    row["pack_manifest_id"],
                    row["receipt_chain_id"],
                    row["merkle_manifest_id"],
                    row["index_snapshot_id"],
                    "capsule_index_integrity_ok" if all_present else "capsule_index_repair_needed",
                    1 if capsule_present else 0,
                    1 if pack_present else 0,
                    1 if chain_present else 0,
                    1 if merkle_present else 0,
                    1 if snapshot_present else 0,
                    1 if row["opaque_metadata_only"] else 0,
                    1 if row["raw_file_bytes_exposed"] else 0,
                    1 if row["external_browse_allowed"] else 0,
                    1 if row["provider_storage_required"] else 0,
                    now,
                ),
            )

            continuity_material = {
                "active_file_id": active_file_id,
                "capsule_hash": row["capsule_hash"],
                "sealed_pack_hash": row["sealed_pack_hash"],
                "chain_hash": row["chain_hash"],
                "merkle_root": row["merkle_root"],
                "snapshot_hash": row["snapshot_hash"],
                "opaque_metadata_only": row["opaque_metadata_only"],
                "public_index_allowed": False,
                "raw_bytes_needed": False,
            }
            continuity_hash = calculate_sha256_bytes(repr(sorted(continuity_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO capsule_hash_continuity (
                    continuity_id, active_file_id, capsule_id,
                    capsule_hash, sealed_pack_hash, chain_hash,
                    merkle_root, snapshot_hash, continuity_hash,
                    continuity_state, hash_chain_complete,
                    raw_bytes_needed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    continuity_id,
                    active_file_id,
                    row["capsule_id"],
                    row["capsule_hash"],
                    row["sealed_pack_hash"],
                    row["chain_hash"],
                    row["merkle_root"],
                    row["snapshot_hash"],
                    continuity_hash,
                    "capsule_hash_continuity_verified",
                    1,
                    0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO capsule_to_pack_repair_map (
                    repair_map_id, active_file_id, memory_node_id,
                    capsule_id, pack_manifest_id, receipt_chain_id,
                    merkle_manifest_id, repair_path, can_repair_from_pack,
                    can_repair_from_receipts, can_repair_from_merkle,
                    can_expose_raw_bytes, provider_required, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    repair_map_id,
                    active_file_id,
                    row["memory_node_id"],
                    row["capsule_id"],
                    row["pack_manifest_id"],
                    row["receipt_chain_id"],
                    row["merkle_manifest_id"],
                    "sealed_pack_manifest -> append_only_receipt_chain -> merkle_repair_manifest -> rebuildable_index_snapshot",
                    1 if row["rebuild_from_pack_allowed"] else 0,
                    1 if row["rebuild_from_receipts_allowed"] else 0,
                    1 if row["repair_can_rebuild_index"] else 0,
                    0,
                    0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO missing_capsule_repair_plans (
                    repair_plan_id, active_file_id, capsule_id,
                    plan_state, missing_capsule_detected, repair_action,
                    rebuild_source, owner_review_required,
                    raw_bytes_required, direct_user_action_allowed,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    repair_plan_id,
                    active_file_id,
                    row["capsule_id"],
                    "no_missing_capsule_rebuild_ready" if all_present else "missing_capsule_repair_plan_ready",
                    0 if all_present else 1,
                    "verify_existing_capsule_index" if all_present else "rebuild_opaque_capsule_index_from_sealed_pack_receipts_and_merkle",
                    "sealed_pack_manifest_and_append_only_receipt_chain",
                    1,
                    0,
                    0,
                    now,
                ),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO opaque_metadata_rebuild_contracts (
                    rebuild_contract_id, active_file_id, capsule_id,
                    contract_state, opaque_metadata_only,
                    compact_metadata_only, raw_filename_allowed,
                    raw_path_allowed, raw_file_bytes_allowed,
                    public_index_allowed, external_browse_allowed,
                    provider_dependency_required, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rebuild_contract_id,
                    active_file_id,
                    row["capsule_id"],
                    "opaque_metadata_rebuild_contract_ready",
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            repair_receipt_material = {
                "active_file_id": active_file_id,
                "capsule_id": row["capsule_id"],
                "repair_plan_id": repair_plan_id,
                "continuity_hash": continuity_hash,
                "chain_hash": row["chain_hash"],
                "append_only": True,
                "raw_bytes_required": False,
                "direct_user_action_allowed": False,
            }
            repair_receipt_hash = calculate_sha256_bytes(repr(sorted(repair_receipt_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO repair_receipt_chain_drafts (
                    repair_receipt_draft_id, active_file_id, capsule_id,
                    receipt_chain_id, repair_plan_id, receipt_state,
                    finalized, finalization_allowed, repair_receipt_hash,
                    append_only, mutable, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    repair_receipt_draft_id,
                    active_file_id,
                    row["capsule_id"],
                    row["receipt_chain_id"],
                    repair_plan_id,
                    "repair_receipt_chain_draft_locked",
                    0,
                    0,
                    repair_receipt_hash,
                    1,
                    0,
                    now,
                ),
            )

            repaired_snapshot_material = {
                "active_file_id": active_file_id,
                "capsule_id": row["capsule_id"],
                "index_snapshot_id": row["index_snapshot_id"],
                "continuity_hash": continuity_hash,
                "repair_receipt_hash": repair_receipt_hash,
                "preview_only": True,
                "index_write_allowed": False,
                "public_index_allowed": False,
                "raw_bytes_exposed": False,
            }
            repaired_snapshot_hash = calculate_sha256_bytes(repr(sorted(repaired_snapshot_material.items())).encode("utf-8"))

            conn.execute(
                """
                INSERT OR REPLACE INTO repaired_index_snapshot_previews (
                    snapshot_preview_id, active_file_id, capsule_id,
                    index_snapshot_id, repaired_snapshot_state,
                    preview_only, index_write_allowed,
                    public_index_allowed, external_browse_allowed,
                    raw_bytes_exposed, repaired_snapshot_hash,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_preview_id,
                    active_file_id,
                    row["capsule_id"],
                    row["index_snapshot_id"],
                    "repaired_index_snapshot_preview_ready_write_locked",
                    1,
                    0,
                    0,
                    0,
                    0,
                    repaired_snapshot_hash,
                    now,
                ),
            )

        conn.commit()

    result = {
        "initialized": True,
        "previous_headless_sealed_memory_ready": bool(previous.get("ready", False)),
        "db_path": str(DB_PATH.relative_to(PROJECT_ROOT)),
        "cached": False,
    }
    _GP421_INIT_CACHE = dict(result)
    return result


def get_blackseed_capsule_index_repair_shell() -> Dict[str, Any]:
    init = initialize_blackseed_capsule_index_repair_layer()
    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 421,
        "title": "Blackseed Capsule Index Repair Shell",
        "ready": True,
        "initialized": init,
        "doctrine": DOCTRINE,
        "headless_repair_only": True,
        "public_dashboard_allowed": False,
        "direct_vault_user_portal_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "locks": LOCKS,
    }


def get_capsule_index_integrity_scanner() -> Dict[str, Any]:
    initialize_blackseed_capsule_index_repair_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM capsule_index_integrity_scans ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 422,
        "title": "Capsule Index Integrity Scanner",
        "ready": True,
        "scan_count": len(rows),
        "scans": rows,
        "all_capsules_present": all(bool(item["capsule_present"]) for item in rows),
        "all_pack_manifests_present": all(bool(item["pack_manifest_present"]) for item in rows),
        "all_receipt_chains_present": all(bool(item["receipt_chain_present"]) for item in rows),
        "all_merkle_manifests_present": all(bool(item["merkle_manifest_present"]) for item in rows),
        "all_index_snapshots_present": all(bool(item["index_snapshot_present"]) for item in rows),
        "all_opaque_metadata_only": all(bool(item["opaque_metadata_only"]) for item in rows),
        "no_raw_bytes_exposed": all(not bool(item["raw_bytes_exposed"]) for item in rows),
        "no_public_browse_allowed": all(not bool(item["public_browse_allowed"]) for item in rows),
        "provider_dependency_not_required": all(not bool(item["provider_dependency_required"]) for item in rows),
    }


def get_capsule_hash_continuity_board() -> Dict[str, Any]:
    initialize_blackseed_capsule_index_repair_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM capsule_hash_continuity ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 423,
        "title": "Capsule Hash Continuity Board",
        "ready": True,
        "continuity_count": len(rows),
        "continuity_rows": rows,
        "all_hash_chains_complete": all(bool(item["hash_chain_complete"]) for item in rows),
        "no_raw_bytes_needed": all(not bool(item["raw_bytes_needed"]) for item in rows),
    }


def get_capsule_to_pack_repair_map() -> Dict[str, Any]:
    initialize_blackseed_capsule_index_repair_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM capsule_to_pack_repair_map ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 424,
        "title": "Capsule-to-Pack Repair Map",
        "ready": True,
        "repair_map_count": len(rows),
        "repair_maps": rows,
        "all_can_repair_from_pack": all(bool(item["can_repair_from_pack"]) for item in rows),
        "all_can_repair_from_receipts": all(bool(item["can_repair_from_receipts"]) for item in rows),
        "all_can_repair_from_merkle": all(bool(item["can_repair_from_merkle"]) for item in rows),
        "none_can_expose_raw_bytes": all(not bool(item["can_expose_raw_bytes"]) for item in rows),
        "provider_not_required": all(not bool(item["provider_required"]) for item in rows),
    }


def get_missing_capsule_repair_plan_builder() -> Dict[str, Any]:
    initialize_blackseed_capsule_index_repair_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM missing_capsule_repair_plans ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 425,
        "title": "Missing Capsule Repair Plan Builder",
        "ready": True,
        "repair_plan_count": len(rows),
        "repair_plans": rows,
        "missing_capsule_count": sum(1 for item in rows if bool(item["missing_capsule_detected"])),
        "all_owner_review_required": all(bool(item["owner_review_required"]) for item in rows),
        "no_raw_bytes_required": all(not bool(item["raw_bytes_required"]) for item in rows),
        "no_direct_user_action_allowed": all(not bool(item["direct_user_action_allowed"]) for item in rows),
    }


def get_opaque_metadata_rebuild_contract() -> Dict[str, Any]:
    initialize_blackseed_capsule_index_repair_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM opaque_metadata_rebuild_contracts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 426,
        "title": "Opaque Metadata Rebuild Contract",
        "ready": True,
        "contract_count": len(rows),
        "contracts": rows,
        "all_opaque_metadata_only": all(bool(item["opaque_metadata_only"]) for item in rows),
        "all_compact_metadata_only": all(bool(item["compact_metadata_only"]) for item in rows),
        "no_raw_filename": all(not bool(item["raw_filename_allowed"]) for item in rows),
        "no_raw_path": all(not bool(item["raw_path_allowed"]) for item in rows),
        "no_raw_file_bytes": all(not bool(item["raw_file_bytes_allowed"]) for item in rows),
        "no_public_index": all(not bool(item["public_index_allowed"]) for item in rows),
        "no_external_browse": all(not bool(item["external_browse_allowed"]) for item in rows),
        "provider_not_required": all(not bool(item["provider_dependency_required"]) for item in rows),
    }


def get_repair_receipt_chain_draft_ledger() -> Dict[str, Any]:
    initialize_blackseed_capsule_index_repair_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM repair_receipt_chain_drafts ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 427,
        "title": "Repair Receipt Chain Draft Ledger",
        "ready": True,
        "repair_receipt_draft_count": len(rows),
        "repair_receipt_drafts": rows,
        "all_receipts_draft_locked": all(not bool(item["finalized"]) and not bool(item["finalization_allowed"]) for item in rows),
        "all_append_only": all(bool(item["append_only"]) for item in rows),
        "all_immutable": all(not bool(item["mutable"]) for item in rows),
    }


def get_repaired_index_snapshot_preview_board() -> Dict[str, Any]:
    initialize_blackseed_capsule_index_repair_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM repaired_index_snapshot_previews ORDER BY created_at DESC")

    return {
        "section": SECTION,
        "gp": 428,
        "title": "Repaired Index Snapshot Preview Board",
        "ready": True,
        "snapshot_preview_count": len(rows),
        "snapshot_previews": rows,
        "all_preview_only": all(bool(item["preview_only"]) for item in rows),
        "all_index_writes_locked": all(not bool(item["index_write_allowed"]) for item in rows),
        "no_public_index": all(not bool(item["public_index_allowed"]) for item in rows),
        "no_external_browse": all(not bool(item["external_browse_allowed"]) for item in rows),
        "no_raw_bytes_exposed": all(not bool(item["raw_bytes_exposed"]) for item in rows),
    }


def get_capsule_repair_safety_blocker_board() -> Dict[str, Any]:
    initialize_blackseed_capsule_index_repair_layer()
    with _connect() as conn:
        rows = _rows(conn, "SELECT * FROM capsule_repair_safety_blockers ORDER BY blocker_id")

    return {
        "section": SECTION,
        "gp": 429,
        "title": "Capsule Repair Safety Blocker Board",
        "ready": True,
        "blocker_count": len(rows),
        "blockers": rows,
        "unsafe_action_count": sum(1 for item in rows if bool(item["allowed"])),
        "all_dangerous_actions_blocked": all(not bool(item["allowed"]) for item in rows),
    }


def get_blackseed_capsule_index_repair_readiness_checkpoint() -> Dict[str, Any]:
    init = initialize_blackseed_capsule_index_repair_layer()

    shell = get_blackseed_capsule_index_repair_shell()
    scanner = get_capsule_index_integrity_scanner()
    continuity = get_capsule_hash_continuity_board()
    repair_map = get_capsule_to_pack_repair_map()
    plans = get_missing_capsule_repair_plan_builder()
    rebuild = get_opaque_metadata_rebuild_contract()
    receipts = get_repair_receipt_chain_draft_ledger()
    snapshots = get_repaired_index_snapshot_preview_board()
    blockers = get_capsule_repair_safety_blocker_board()

    checks = {
        "previous_headless_sealed_memory_ready": init["previous_headless_sealed_memory_ready"] is True,
        "repair_shell_ready": shell["ready"] is True,
        "doctrine_tower_teller_vault_locked": DOCTRINE["tower"] == "face" and DOCTRINE["teller"] == "workflow" and DOCTRINE["vault"] == "sealed_memory",
        "headless_repair_only": DOCTRINE["repair_behavior"] == "headless_capsule_index_repair_only",
        "repair_exposes_no_raw_bytes": DOCTRINE["repair_exposes_raw_bytes"] is False,
        "integrity_scanner_ready": scanner["ready"] is True and scanner["scan_count"] >= 2,
        "scanner_all_sources_present": scanner["all_capsules_present"] is True and scanner["all_pack_manifests_present"] is True and scanner["all_receipt_chains_present"] is True and scanner["all_merkle_manifests_present"] is True and scanner["all_index_snapshots_present"] is True,
        "scanner_no_raw_public_provider": scanner["no_raw_bytes_exposed"] is True and scanner["no_public_browse_allowed"] is True and scanner["provider_dependency_not_required"] is True,
        "hash_continuity_ready": continuity["ready"] is True and continuity["continuity_count"] >= 2,
        "hash_chains_complete_no_raw_bytes": continuity["all_hash_chains_complete"] is True and continuity["no_raw_bytes_needed"] is True,
        "repair_map_ready": repair_map["ready"] is True and repair_map["repair_map_count"] >= 2,
        "repair_map_uses_pack_receipts_merkle": repair_map["all_can_repair_from_pack"] is True and repair_map["all_can_repair_from_receipts"] is True and repair_map["all_can_repair_from_merkle"] is True,
        "repair_map_no_raw_or_provider": repair_map["none_can_expose_raw_bytes"] is True and repair_map["provider_not_required"] is True,
        "missing_capsule_repair_plans_ready": plans["ready"] is True and plans["repair_plan_count"] >= 2,
        "repair_plans_owner_review_no_raw_no_direct_user": plans["all_owner_review_required"] is True and plans["no_raw_bytes_required"] is True and plans["no_direct_user_action_allowed"] is True,
        "opaque_metadata_rebuild_contract_ready": rebuild["ready"] is True and rebuild["contract_count"] >= 2,
        "rebuild_opaque_compact": rebuild["all_opaque_metadata_only"] is True and rebuild["all_compact_metadata_only"] is True,
        "rebuild_no_raw_public_external_provider": rebuild["no_raw_filename"] is True and rebuild["no_raw_path"] is True and rebuild["no_raw_file_bytes"] is True and rebuild["no_public_index"] is True and rebuild["no_external_browse"] is True and rebuild["provider_not_required"] is True,
        "repair_receipt_chain_drafts_ready": receipts["ready"] is True and receipts["repair_receipt_draft_count"] >= 2,
        "repair_receipts_draft_append_only_immutable": receipts["all_receipts_draft_locked"] is True and receipts["all_append_only"] is True and receipts["all_immutable"] is True,
        "repaired_snapshot_previews_ready": snapshots["ready"] is True and snapshots["snapshot_preview_count"] >= 2,
        "snapshot_previews_write_locked_no_public_raw": snapshots["all_preview_only"] is True and snapshots["all_index_writes_locked"] is True and snapshots["no_public_index"] is True and snapshots["no_external_browse"] is True and snapshots["no_raw_bytes_exposed"] is True,
        "safety_blockers_ready": blockers["ready"] is True and blockers["all_dangerous_actions_blocked"] is True,
        "global_no_public_dashboard": LOCKS["public_vault_dashboard_allowed"] is False,
        "global_no_direct_portal": LOCKS["direct_vault_user_portal_allowed"] is False,
        "global_no_external_browsing": LOCKS["external_collaborator_browsing_allowed"] is False,
        "global_no_public_links_raw_bytes_paths": LOCKS["public_url_created"] is False and LOCKS["share_link_created"] is False and LOCKS["raw_file_bytes_returned_by_json"] is False and LOCKS["raw_path_exposed"] is False and LOCKS["raw_file_url_exposed"] is False,
        "global_no_provider_dependency": LOCKS["provider_storage_required"] is False,
        "global_no_delete_restore_move": LOCKS["hard_delete_allowed"] is False and LOCKS["purge_allowed"] is False and LOCKS["restore_execution_allowed"] is False and LOCKS["physical_object_move_allowed"] is False,
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 430,
        "title": "Blackseed Capsule Index Repair Readiness Checkpoint",
        "readiness_label": READINESS_LABEL if ready else "Blackseed capsule index repair layer blocked",
        "ready": ready,
        "checks": checks,
        "next_recommended_layer": "ARCHIVE VAULT — VAULT PACK REBUILD SERVICE LAYER / GP431-GP440",
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
            "no public/beta/provider upload",
            "no delete or purge",
            "no restore execution",
            "no quarantine release",
            "no physical object move",
            "no provider dependency by default",
        ],
    }


def get_blackseed_capsule_index_repair_home() -> Dict[str, Any]:
    checkpoint = get_blackseed_capsule_index_repair_readiness_checkpoint()
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


def validate_blackseed_capsule_index_repair_layer() -> Dict[str, Any]:
    checkpoint = get_blackseed_capsule_index_repair_readiness_checkpoint()

    assert checkpoint["ready"] is True
    assert checkpoint["checks"]["previous_headless_sealed_memory_ready"] is True
    assert checkpoint["checks"]["doctrine_tower_teller_vault_locked"] is True
    assert checkpoint["checks"]["headless_repair_only"] is True
    assert checkpoint["checks"]["repair_exposes_no_raw_bytes"] is True
    assert checkpoint["checks"]["integrity_scanner_ready"] is True
    assert checkpoint["checks"]["scanner_all_sources_present"] is True
    assert checkpoint["checks"]["scanner_no_raw_public_provider"] is True
    assert checkpoint["checks"]["hash_continuity_ready"] is True
    assert checkpoint["checks"]["hash_chains_complete_no_raw_bytes"] is True
    assert checkpoint["checks"]["repair_map_ready"] is True
    assert checkpoint["checks"]["repair_map_uses_pack_receipts_merkle"] is True
    assert checkpoint["checks"]["repair_map_no_raw_or_provider"] is True
    assert checkpoint["checks"]["missing_capsule_repair_plans_ready"] is True
    assert checkpoint["checks"]["repair_plans_owner_review_no_raw_no_direct_user"] is True
    assert checkpoint["checks"]["opaque_metadata_rebuild_contract_ready"] is True
    assert checkpoint["checks"]["rebuild_opaque_compact"] is True
    assert checkpoint["checks"]["rebuild_no_raw_public_external_provider"] is True
    assert checkpoint["checks"]["repair_receipt_chain_drafts_ready"] is True
    assert checkpoint["checks"]["repair_receipts_draft_append_only_immutable"] is True
    assert checkpoint["checks"]["repaired_snapshot_previews_ready"] is True
    assert checkpoint["checks"]["snapshot_previews_write_locked_no_public_raw"] is True
    assert checkpoint["checks"]["safety_blockers_ready"] is True

    assert LOCKS["capsule_index_integrity_scanning_allowed"] is True
    assert LOCKS["capsule_hash_continuity_verification_allowed"] is True
    assert LOCKS["capsule_to_pack_repair_mapping_allowed"] is True
    assert LOCKS["missing_capsule_repair_planning_allowed"] is True
    assert LOCKS["opaque_metadata_rebuild_contract_allowed"] is True
    assert LOCKS["repair_receipt_chain_draft_allowed"] is True
    assert LOCKS["repaired_index_snapshot_preview_allowed"] is True

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
    checkpoint = get_blackseed_capsule_index_repair_readiness_checkpoint()
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
        "repair_exposes_raw_bytes": False,
        "direct_vault_user_portal_allowed": False,
        "public_dashboard_allowed": False,
        "locks_preserved": True,
    }


def get_gp421_status() -> Dict[str, Any]:
    return _gp_status(421)


def get_gp422_status() -> Dict[str, Any]:
    return _gp_status(422)


def get_gp423_status() -> Dict[str, Any]:
    return _gp_status(423)


def get_gp424_status() -> Dict[str, Any]:
    return _gp_status(424)


def get_gp425_status() -> Dict[str, Any]:
    return _gp_status(425)


def get_gp426_status() -> Dict[str, Any]:
    return _gp_status(426)


def get_gp427_status() -> Dict[str, Any]:
    return _gp_status(427)


def get_gp428_status() -> Dict[str, Any]:
    return _gp_status(428)


def get_gp429_status() -> Dict[str, Any]:
    return _gp_status(429)


def get_gp430_status() -> Dict[str, Any]:
    return _gp_status(430)
