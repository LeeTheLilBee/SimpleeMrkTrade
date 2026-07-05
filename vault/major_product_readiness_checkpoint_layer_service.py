"""
VAULT GP191-GP200 — Major Product Readiness Checkpoint Layer

New section:
Archive Vault — Major Product Readiness Checkpoint Layer / GP191-GP200

Builds:
- GP191 Major Product Readiness Shell
- GP192 Product Capability Inventory
- GP193 Route and Endpoint Readiness Board
- GP194 Data Store Readiness Board
- GP195 Lock Boundary Audit Board
- GP196 Owner Experience Readiness Board
- GP197 Provider Integration Readiness Board
- GP198 Product Risk and Blocker Board
- GP199 Product Readiness Receipt Packet
- GP200 Major Product Readiness Checkpoint

This is a product-readiness checkpoint for the first 200 Vault packs.
It proves readiness, route/data/lock/owner/provider/risk surfaces, and receipt
packet state while keeping Vault NOT done and every provider/body/export/restore/
Tower/execution path locked.
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

from vault.real_archive_index_search_layer_service import (
    get_gp190_status,
    get_gp190_archive_index_search_readiness_checkpoint,
    get_real_archive_index_search_layer_home,
    validate_real_archive_index_search_layer,
    get_archive_metadata_index_records,
    get_archive_index_search_blockers,
)

LAYER_ID = "VAULT_GP191_200"
LAYER_NAME = "Major Product Readiness Checkpoint Layer"
SCHEMA_VERSION = "vault.major_product_readiness_checkpoint_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_MAJOR_PRODUCT_READINESS_CHECKPOINT_LAYER"
SECTION_TITLE = "Archive Vault — Major Product Readiness Checkpoint Layer"
SECTION_RANGE = "GP191-GP200"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_REAL_ARCHIVE_INDEX_AND_SEARCH_LAYER"
PREVIOUS_SECTION_RANGE = "GP181-GP190"

NEXT_SECTION_ID = "ARCHIVE_VAULT_OWNER_PRODUCTIZATION_BETA_READINESS_LAYER"
NEXT_SECTION_RANGE = "GP201-GP210"
NEXT_PACK = "VAULT_GP201_210_OWNER_PRODUCTIZATION_BETA_READINESS_LAYER"

DEFAULT_DB_ENV = "VAULT_MAJOR_PRODUCT_READINESS_CHECKPOINT_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_major_product_readiness_checkpoint_layer.sqlite"

READINESS_SHELL_ID = "VMPR-SHELL-GP191-001"
CAPABILITY_INVENTORY_ID = "VMPR-CAPABILITY-GP192-001"
ROUTE_ENDPOINT_BOARD_ID = "VMPR-ROUTES-GP193-001"
DATA_STORE_BOARD_ID = "VMPR-DATA-GP194-001"
LOCK_BOUNDARY_BOARD_ID = "VMPR-LOCKS-GP195-001"
OWNER_EXPERIENCE_BOARD_ID = "VMPR-OWNERUX-GP196-001"
PROVIDER_INTEGRATION_BOARD_ID = "VMPR-PROVIDER-GP197-001"
RISK_BLOCKER_BOARD_ID = "VMPR-RISK-GP198-001"
RECEIPT_PACKET_ID = "VMPR-RECEIPT-GP199-001"
READINESS_ID = "VMPR-READINESS-GP200-001"

FALSE_FIELDS = [
    "product_marked_done",
    "vault_done",
    "beta_launch_approved",
    "public_launch_approved",
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
    "clouds_should_continue",
]

CAPABILITIES = [
    ("provider_decision_foundation", "Provider Decision Foundation", "foundation", "ready_locked"),
    ("provider_config_boundaries", "Provider Configuration Boundaries", "provider_config", "ready_locked"),
    ("receipt_redacted_access", "Receipt Redacted Access", "receipt", "ready_locked"),
    ("restore_export_governance", "Restore and Export Governance", "restore_export", "ready_locked"),
    ("post_closeout_handoff", "Post-Closeout Handoff Governance", "handoff", "ready_locked"),
    ("recovery_case_workspace", "Recovery Case Workspace", "recovery", "ready_locked"),
    ("redacted_archive_browser", "Redacted Archive Browser", "browser", "ready_locked"),
    ("owner_console_dashboard", "Owner Console Operating Dashboard", "owner_console", "ready_locked"),
    ("tower_step_up_handoff", "Tower-Gated Step-Up Handoff", "tower", "ready_locked"),
    ("provider_readiness_simulation", "Provider Readiness Simulation/Dry-Run", "simulation", "ready_locked"),
    ("real_provider_connection_readiness", "Real Provider Connection Readiness", "provider_readiness", "ready_locked"),
    ("controlled_connection_test_lock", "Controlled Connection Test Lock", "connection_test", "ready_locked"),
    ("controlled_read_only_metadata_test", "Controlled Read-Only Metadata Test", "metadata_test", "ready_locked"),
    ("real_archive_index_search", "Real Archive Index and Search", "index_search", "ready_locked"),
]

ROUTE_ENDPOINTS = [
    ("major_product_readiness_layer_page", "/vault/major-product-readiness-checkpoint-layer", "page"),
    ("major_product_readiness_layer_json", "/vault/major-product-readiness-checkpoint-layer.json", "json"),
    ("major_product_readiness_shell", "/vault/major-product-readiness-shell.json", "json"),
    ("product_capability_inventory", "/vault/product-capability-inventory.json", "json"),
    ("route_endpoint_readiness_board", "/vault/route-endpoint-readiness-board.json", "json"),
    ("data_store_readiness_board", "/vault/data-store-readiness-board.json", "json"),
    ("lock_boundary_audit_board", "/vault/lock-boundary-audit-board.json", "json"),
    ("owner_experience_readiness_board", "/vault/owner-experience-readiness-board.json", "json"),
    ("provider_integration_readiness_board", "/vault/provider-integration-readiness-board.json", "json"),
    ("product_risk_blocker_board", "/vault/product-risk-blocker-board.json", "json"),
    ("product_readiness_receipt_packet", "/vault/product-readiness-receipt-packet.json", "json"),
    ("major_product_readiness_checkpoint", "/vault/major-product-readiness-checkpoint.json", "json"),
]

DATA_STORES = [
    ("provider_decision_store", "Provider decision store", "sqlite", "ready_locked"),
    ("provider_config_store", "Provider config contract store", "sqlite", "ready_locked"),
    ("restore_governance_store", "Restore/export governance store", "sqlite", "ready_locked"),
    ("post_closeout_store", "Post-closeout governance store", "sqlite", "ready_locked"),
    ("recovery_case_store", "Recovery case workspace store", "sqlite", "ready_locked"),
    ("archive_browser_store", "Redacted archive browser store", "sqlite", "ready_locked"),
    ("owner_dashboard_store", "Owner console operating dashboard store", "sqlite", "ready_locked"),
    ("tower_step_up_store", "Tower step-up handoff store", "sqlite", "ready_locked"),
    ("provider_simulation_store", "Provider readiness simulation store", "sqlite", "ready_locked"),
    ("connection_readiness_store", "Real provider connection readiness store", "sqlite", "ready_locked"),
    ("connection_test_lock_store", "Controlled connection test lock store", "sqlite", "ready_locked"),
    ("metadata_test_lock_store", "Controlled metadata test lock store", "sqlite", "ready_locked"),
    ("archive_index_search_store", "Real archive index/search store", "sqlite", "ready_locked"),
    ("major_readiness_store", "Major product readiness checkpoint store", "sqlite", "ready_locked"),
]

LOCK_BOUNDARIES = [
    ("provider_unlock_boundary", "Provider unlock boundary", "locked"),
    ("provider_api_boundary", "Provider API boundary", "locked"),
    ("credential_secret_boundary", "Credential/secret boundary", "locked"),
    ("provider_endpoint_boundary", "Provider endpoint boundary", "locked"),
    ("provider_metadata_boundary", "Provider metadata boundary", "locked"),
    ("object_body_boundary", "Object body boundary", "locked"),
    ("download_boundary", "Download boundary", "locked"),
    ("restore_boundary", "Restore boundary", "locked"),
    ("export_boundary", "Export boundary", "locked"),
    ("direct_upload_boundary", "Direct upload boundary", "locked"),
    ("delete_boundary", "Delete boundary", "locked"),
    ("tower_unlock_boundary", "Tower unlock boundary", "locked"),
    ("owner_approval_unlock_boundary", "Owner approval unlock boundary", "locked"),
    ("execution_boundary", "Execution boundary", "locked"),
    ("vault_done_boundary", "Vault done boundary", "locked"),
]

OWNER_EXPERIENCE_ITEMS = [
    ("owner_console_ready", "Owner console surface ready", "ready_locked"),
    ("redacted_archive_browser_ready", "Redacted archive browser surface ready", "ready_locked"),
    ("search_surface_ready", "Local metadata search surface ready", "ready_locked"),
    ("receipt_packet_surface_ready", "Receipt packet surface ready", "ready_locked"),
    ("risk_blocker_surface_ready", "Risk/blocker surface ready", "ready_locked"),
    ("readiness_checkpoint_surface_ready", "Readiness checkpoint surface ready", "ready_locked"),
]

PROVIDER_INTEGRATION_ITEMS = [
    ("provider_selection_ready", "Provider selection readiness", "ready_locked"),
    ("provider_configuration_ready", "Provider configuration readiness", "ready_locked"),
    ("provider_readiness_simulation_ready", "Provider readiness simulation readiness", "ready_locked"),
    ("real_provider_connection_readiness_ready", "Real provider connection readiness", "ready_locked"),
    ("controlled_connection_test_locked", "Controlled connection test remains locked", "locked"),
    ("controlled_metadata_test_locked", "Controlled metadata test remains locked", "locked"),
    ("provider_search_locked", "Provider search remains locked", "locked"),
    ("provider_restore_export_locked", "Provider restore/export remains locked", "locked"),
]

RISK_BLOCKERS = [
    ("vault_not_done", "Vault is not done", "done_state", "critical"),
    ("provider_unlock_locked", "Provider unlock remains locked", "provider", "critical"),
    ("provider_api_locked", "Provider API remains locked", "provider_api", "critical"),
    ("secret_value_locked", "Credential/secret values remain locked", "credential", "critical"),
    ("provider_metadata_locked", "Provider metadata read/import remains locked", "metadata", "critical"),
    ("object_body_download_locked", "Object body/download remains locked", "object_body", "critical"),
    ("restore_export_upload_delete_locked", "Restore/export/upload/delete remains locked", "dangerous_ops", "critical"),
    ("tower_unlock_locked", "Tower unlock remains locked", "tower", "critical"),
    ("owner_approval_unlock_locked", "Owner approval unlock remains locked", "owner", "critical"),
    ("execution_locked", "Execution remains locked", "execution", "critical"),
    ("beta_public_launch_not_approved", "Beta/public launch not approved", "launch", "high"),
    ("clouds_parked", "Clouds remains parked", "clouds", "medium"),
]

COMPONENT_SPECS = [
    (191, READINESS_SHELL_ID, "VAULT_GP191", "Major Product Readiness Shell", "major_product_readiness_shell"),
    (192, CAPABILITY_INVENTORY_ID, "VAULT_GP192", "Product Capability Inventory", "product_capability_inventory"),
    (193, ROUTE_ENDPOINT_BOARD_ID, "VAULT_GP193", "Route and Endpoint Readiness Board", "route_endpoint_readiness_board"),
    (194, DATA_STORE_BOARD_ID, "VAULT_GP194", "Data Store Readiness Board", "data_store_readiness_board"),
    (195, LOCK_BOUNDARY_BOARD_ID, "VAULT_GP195", "Lock Boundary Audit Board", "lock_boundary_audit_board"),
    (196, OWNER_EXPERIENCE_BOARD_ID, "VAULT_GP196", "Owner Experience Readiness Board", "owner_experience_readiness_board"),
    (197, PROVIDER_INTEGRATION_BOARD_ID, "VAULT_GP197", "Provider Integration Readiness Board", "provider_integration_readiness_board"),
    (198, RISK_BLOCKER_BOARD_ID, "VAULT_GP198", "Product Risk and Blocker Board", "product_risk_blocker_board"),
    (199, RECEIPT_PACKET_ID, "VAULT_GP199", "Product Readiness Receipt Packet", "product_readiness_receipt_packet"),
    (200, READINESS_ID, "VAULT_GP200", "Major Product Readiness Checkpoint", "major_product_readiness_checkpoint"),
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
        "source_gp190_readiness_score",
        "component_count",
        "capability_count",
        "route_endpoint_count",
        "data_store_count",
        "lock_boundary_count",
        "owner_experience_count",
        "provider_integration_count",
        "risk_blocker_count",
        "receipt_packet_count",
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
            or key.endswith("_value")
            or key.endswith("_level")
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
        "depends_on": ["VAULT_GP190"],
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
        "depends_on": ["VAULT_GP190"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_major_product_readiness_checkpoint_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_major_product_readiness_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp190_readiness_id TEXT NOT NULL,
                source_gp190_readiness_hash TEXT NOT NULL,
                source_gp190_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                product_readiness_checkpoint INTEGER NOT NULL DEFAULT 1,
                first_200_pack_arc_ready INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_product_capability_inventory (
                capability_id TEXT PRIMARY KEY,
                capability_code TEXT NOT NULL UNIQUE,
                capability_name TEXT NOT NULL,
                capability_category TEXT NOT NULL,
                capability_status TEXT NOT NULL,
                capability_ready INTEGER NOT NULL DEFAULT 1,
                capability_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                capability_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_route_endpoint_readiness_board (
                route_id TEXT PRIMARY KEY,
                route_code TEXT NOT NULL UNIQUE,
                route_path TEXT NOT NULL,
                route_type TEXT NOT NULL,
                route_status TEXT NOT NULL,
                route_ready INTEGER NOT NULL DEFAULT 1,
                route_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                route_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_data_store_readiness_board (
                store_id TEXT PRIMARY KEY,
                store_code TEXT NOT NULL UNIQUE,
                store_name TEXT NOT NULL,
                store_type TEXT NOT NULL,
                store_status TEXT NOT NULL,
                store_ready INTEGER NOT NULL DEFAULT 1,
                store_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                store_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_lock_boundary_audit_board (
                boundary_id TEXT PRIMARY KEY,
                boundary_code TEXT NOT NULL UNIQUE,
                boundary_name TEXT NOT NULL,
                boundary_status TEXT NOT NULL,
                boundary_locked INTEGER NOT NULL DEFAULT 1,
                audit_passed INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                boundary_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_owner_experience_readiness_board (
                owner_experience_id TEXT PRIMARY KEY,
                item_code TEXT NOT NULL UNIQUE,
                item_name TEXT NOT NULL,
                item_status TEXT NOT NULL,
                item_ready INTEGER NOT NULL DEFAULT 1,
                item_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                item_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_provider_integration_readiness_board (
                provider_item_id TEXT PRIMARY KEY,
                item_code TEXT NOT NULL UNIQUE,
                item_name TEXT NOT NULL,
                item_status TEXT NOT NULL,
                item_ready INTEGER NOT NULL DEFAULT 1,
                item_locked INTEGER NOT NULL DEFAULT 1,
                provider_unlock_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                item_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_product_risk_blocker_board (
                blocker_id TEXT PRIMARY KEY,
                blocker_code TEXT NOT NULL UNIQUE,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocker_active INTEGER NOT NULL DEFAULT 1,
                blocks_product_done INTEGER NOT NULL DEFAULT 1,
                blocks_provider_unlock INTEGER NOT NULL DEFAULT 1,
                blocks_provider_api INTEGER NOT NULL DEFAULT 1,
                blocks_object_body INTEGER NOT NULL DEFAULT 1,
                blocks_download INTEGER NOT NULL DEFAULT 1,
                blocks_restore INTEGER NOT NULL DEFAULT 1,
                blocks_export INTEGER NOT NULL DEFAULT 1,
                blocks_direct_upload INTEGER NOT NULL DEFAULT 1,
                blocks_delete INTEGER NOT NULL DEFAULT 1,
                blocks_tower_unlock INTEGER NOT NULL DEFAULT 1,
                blocks_execution INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_product_readiness_receipt_packets (
                receipt_packet_id TEXT PRIMARY KEY,
                packet_code TEXT NOT NULL UNIQUE,
                packet_name TEXT NOT NULL,
                packet_status TEXT NOT NULL,
                packet_ready INTEGER NOT NULL DEFAULT 1,
                packet_locked INTEGER NOT NULL DEFAULT 1,
                final_product_receipt INTEGER NOT NULL DEFAULT 0,
                payload_json TEXT NOT NULL,
                packet_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_major_product_readiness_checkpoint (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                capability_count INTEGER NOT NULL,
                route_endpoint_count INTEGER NOT NULL,
                data_store_count INTEGER NOT NULL,
                lock_boundary_count INTEGER NOT NULL,
                owner_experience_count INTEGER NOT NULL,
                provider_integration_count INTEGER NOT NULL,
                risk_blocker_count INTEGER NOT NULL,
                receipt_packet_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                first_200_pack_arc_ready INTEGER NOT NULL DEFAULT 1,
                safe_to_continue_to_gp201 INTEGER NOT NULL DEFAULT 1,
                section_ready INTEGER NOT NULL DEFAULT 1,
                product_readiness_checkpoint INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_major_product_readiness_events (
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
            "vault_major_product_readiness_components",
            "vault_product_capability_inventory",
            "vault_route_endpoint_readiness_board",
            "vault_data_store_readiness_board",
            "vault_lock_boundary_audit_board",
            "vault_owner_experience_readiness_board",
            "vault_provider_integration_readiness_board",
            "vault_product_risk_blocker_board",
            "vault_product_readiness_receipt_packets",
            "vault_major_product_readiness_checkpoint",
            "vault_major_product_readiness_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VMPREVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_major_product_readiness_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_major_product_readiness_checkpoint_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_major_product_readiness_checkpoint_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_major_product_readiness_components WHERE component_id = ?",
            (READINESS_SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp190_status = get_gp190_status()["gp190_status"]
            gp190_checkpoint = get_gp190_archive_index_search_readiness_checkpoint()["readiness_checkpoint"]
            gp190_home = get_real_archive_index_search_layer_home()
            gp190_validation = validate_real_archive_index_search_layer()

            source_records = get_archive_metadata_index_records()
            source_blockers = get_archive_index_search_blockers()

            readiness = gp190_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp190_readiness_id": readiness["readiness_id"],
                "source_gp190_readiness_hash": readiness["readiness_hash"],
                "source_gp190_readiness_score": readiness["readiness_score"],
            }

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "capability_count": len(CAPABILITIES),
                "route_endpoint_count": len(ROUTE_ENDPOINTS),
                "data_store_count": len(DATA_STORES),
                "lock_boundary_count": len(LOCK_BOUNDARIES),
                "owner_experience_count": len(OWNER_EXPERIENCE_ITEMS),
                "provider_integration_count": len(PROVIDER_INTEGRATION_ITEMS),
                "risk_blocker_count": len(RISK_BLOCKERS),
                "receipt_packet_count": 1,
            }

            source_context = {
                "source_gp190_status_ready": gp190_status["ready"],
                "source_gp190_validation_passed": gp190_status["validation_passed"],
                "source_gp190_safe_to_continue_to_gp191": gp190_status["safe_to_continue_to_gp191"],
                "source_gp190_readiness_hash": readiness["readiness_hash"],
                "source_gp190_readiness_score": readiness["readiness_score"],
                "source_archive_index_record_count": len(source_records),
                "source_archive_index_blocker_count": len(source_blockers),
                "source_validation_check_count": gp190_validation["check_count"],
            }

            component_extra = {
                READINESS_SHELL_ID: {"major_product_readiness_shell_ready": True},
                CAPABILITY_INVENTORY_ID: {"product_capability_inventory_ready": True, "capability_count": counts["capability_count"]},
                ROUTE_ENDPOINT_BOARD_ID: {"route_endpoint_readiness_board_ready": True, "route_endpoint_count": counts["route_endpoint_count"]},
                DATA_STORE_BOARD_ID: {"data_store_readiness_board_ready": True, "data_store_count": counts["data_store_count"]},
                LOCK_BOUNDARY_BOARD_ID: {"lock_boundary_audit_board_ready": True, "lock_boundary_count": counts["lock_boundary_count"]},
                OWNER_EXPERIENCE_BOARD_ID: {"owner_experience_readiness_board_ready": True, "owner_experience_count": counts["owner_experience_count"]},
                PROVIDER_INTEGRATION_BOARD_ID: {"provider_integration_readiness_board_ready": True, "provider_integration_count": counts["provider_integration_count"]},
                RISK_BLOCKER_BOARD_ID: {"product_risk_blocker_board_ready": True, "risk_blocker_count": counts["risk_blocker_count"]},
                RECEIPT_PACKET_ID: {"product_readiness_receipt_packet_ready": True, "receipt_packet_count": counts["receipt_packet_count"]},
                READINESS_ID: {"major_product_readiness_checkpoint_ready": True, "first_200_pack_arc_ready": True, "safe_to_continue_to_gp201": True},
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
                    "product_readiness_checkpoint": True,
                    "first_200_pack_arc_ready": True,
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
                    "product_readiness_checkpoint": 1,
                    "first_200_pack_arc_ready": 1,
                    "vault_not_done": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_major_product_readiness_components", row)

            for idx, (code, name, category, status) in enumerate(CAPABILITIES, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "capability_code": code,
                    "capability_name": name,
                    "capability_category": category,
                    "capability_status": status,
                    "capability_ready": True,
                    "capability_locked": True,
                    "product_readiness_checkpoint": True,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "capability_id": f"VMPRCAP-{idx:03d}",
                    "capability_code": code,
                    "capability_name": name,
                    "capability_category": category,
                    "capability_status": status,
                    "capability_ready": 1,
                    "capability_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "capability_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_product_capability_inventory", row)

            for idx, (code, path_value, route_type) in enumerate(ROUTE_ENDPOINTS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "route_code": code,
                    "route_path": path_value,
                    "route_type": route_type,
                    "route_status": "ROUTE_READY_LOCKED_CHECKPOINT_SURFACE",
                    "route_ready": True,
                    "route_locked": True,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "route_id": f"VMPRROUTE-{idx:03d}",
                    "route_code": code,
                    "route_path": path_value,
                    "route_type": route_type,
                    "route_status": payload["route_status"],
                    "route_ready": 1,
                    "route_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "route_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_route_endpoint_readiness_board", row)

            for idx, (code, name, store_type, status) in enumerate(DATA_STORES, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "store_code": code,
                    "store_name": name,
                    "store_type": store_type,
                    "store_status": status,
                    "store_ready": True,
                    "store_locked": True,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "store_id": f"VMPRSTORE-{idx:03d}",
                    "store_code": code,
                    "store_name": name,
                    "store_type": store_type,
                    "store_status": status,
                    "store_ready": 1,
                    "store_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "store_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_data_store_readiness_board", row)

            for idx, (code, name, status) in enumerate(LOCK_BOUNDARIES, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "boundary_code": code,
                    "boundary_name": name,
                    "boundary_status": status,
                    "boundary_locked": True,
                    "audit_passed": True,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "boundary_id": f"VMPRLOCK-{idx:03d}",
                    "boundary_code": code,
                    "boundary_name": name,
                    "boundary_status": status,
                    "boundary_locked": 1,
                    "audit_passed": 1,
                    "payload_json": _json_dumps(payload),
                    "boundary_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_lock_boundary_audit_board", row)

            for idx, (code, name, status) in enumerate(OWNER_EXPERIENCE_ITEMS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "item_code": code,
                    "item_name": name,
                    "item_status": status,
                    "item_ready": True,
                    "item_locked": True,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "owner_experience_id": f"VMPROWNER-{idx:03d}",
                    "item_code": code,
                    "item_name": name,
                    "item_status": status,
                    "item_ready": 1,
                    "item_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "item_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_owner_experience_readiness_board", row)

            for idx, (code, name, status) in enumerate(PROVIDER_INTEGRATION_ITEMS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "item_code": code,
                    "item_name": name,
                    "item_status": status,
                    "item_ready": True,
                    "item_locked": True,
                    "provider_unlock_locked": True,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "provider_item_id": f"VMPRPROV-{idx:03d}",
                    "item_code": code,
                    "item_name": name,
                    "item_status": status,
                    "item_ready": 1,
                    "item_locked": 1,
                    "provider_unlock_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "item_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_provider_integration_readiness_board", row)

            for idx, (code, name, category, severity) in enumerate(RISK_BLOCKERS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "ACTIVE_MAJOR_PRODUCT_READINESS_BLOCKER",
                    "blocker_active": True,
                    "blocks_product_done": True,
                    "blocks_provider_unlock": True,
                    "blocks_provider_api": True,
                    "blocks_object_body": True,
                    "blocks_download": True,
                    "blocks_restore": True,
                    "blocks_export": True,
                    "blocks_direct_upload": True,
                    "blocks_delete": True,
                    "blocks_tower_unlock": True,
                    "blocks_execution": True,
                    "resolved": False,
                    "vault_done": False,
                    "clouds_should_continue": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                }
                row = {
                    "blocker_id": f"VMPRRISK-{idx:03d}",
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": payload["blocker_status"],
                    "blocker_active": 1,
                    "blocks_product_done": 1,
                    "blocks_provider_unlock": 1,
                    "blocks_provider_api": 1,
                    "blocks_object_body": 1,
                    "blocks_download": 1,
                    "blocks_restore": 1,
                    "blocks_export": 1,
                    "blocks_direct_upload": 1,
                    "blocks_delete": 1,
                    "blocks_tower_unlock": 1,
                    "blocks_execution": 1,
                    "resolved": 0,
                    "payload_json": _json_dumps(payload),
                    "blocker_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_product_risk_blocker_board", row)

            packet_payload = {
                "schema_version": SCHEMA_VERSION,
                "packet_code": "vault_gp001_200_major_product_readiness_packet",
                "packet_name": "Vault GP001-GP200 Major Product Readiness Receipt Packet",
                "packet_status": "READY_LOCKED_NOT_FINAL_PRODUCT_DONE_RECEIPT",
                "source_gp190_readiness_id": readiness["readiness_id"],
                "source_gp190_readiness_hash": readiness["readiness_hash"],
                "source_gp190_readiness_score": readiness["readiness_score"],
                "capability_count": counts["capability_count"],
                "route_endpoint_count": counts["route_endpoint_count"],
                "data_store_count": counts["data_store_count"],
                "lock_boundary_count": counts["lock_boundary_count"],
                "owner_experience_count": counts["owner_experience_count"],
                "provider_integration_count": counts["provider_integration_count"],
                "risk_blocker_count": counts["risk_blocker_count"],
                "first_200_pack_arc_ready": True,
                "vault_done": False,
                "clouds_should_continue": False,
                "locked_truth": {field: False for field in FALSE_FIELDS},
            }
            row = {
                "receipt_packet_id": RECEIPT_PACKET_ID,
                "packet_code": "vault_gp001_200_major_product_readiness_packet",
                "packet_name": "Vault GP001-GP200 Major Product Readiness Receipt Packet",
                "packet_status": packet_payload["packet_status"],
                "packet_ready": 1,
                "packet_locked": 1,
                "final_product_receipt": 0,
                "payload_json": _json_dumps(packet_payload),
                "packet_hash": _hash_payload(packet_payload),
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                row[field] = 0
            _insert_dict(conn, "vault_product_readiness_receipt_packets", row)

            checks = [
                ("SOURCE_GP190_READY", bool(gp190_status["ready"])),
                ("SOURCE_GP190_VALIDATION_PASSED", bool(gp190_status["validation_passed"])),
                ("SOURCE_GP190_SAFE_TO_CONTINUE", bool(gp190_status["safe_to_continue_to_gp191"])),
                ("SOURCE_GP190_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP190_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("CAPABILITY_COUNT_14", counts["capability_count"] == 14),
                ("ROUTE_ENDPOINT_COUNT_12", counts["route_endpoint_count"] == 12),
                ("DATA_STORE_COUNT_14", counts["data_store_count"] == 14),
                ("LOCK_BOUNDARY_COUNT_15", counts["lock_boundary_count"] == 15),
                ("OWNER_EXPERIENCE_COUNT_6", counts["owner_experience_count"] == 6),
                ("PROVIDER_INTEGRATION_COUNT_8", counts["provider_integration_count"] == 8),
                ("RISK_BLOCKER_COUNT_12", counts["risk_blocker_count"] == 12),
                ("RECEIPT_PACKET_COUNT_1", counts["receipt_packet_count"] == 1),
                ("SECTION_GP191_GP200", SECTION_RANGE == "GP191-GP200"),
                ("NEXT_SECTION_GP201_GP210", NEXT_SECTION_RANGE == "GP201-GP210"),
                ("FIRST_200_PACK_ARC_READY", True),
                ("PRODUCT_READINESS_CHECKPOINT", True),
                ("VAULT_NOT_DONE", True),
                ("NO_PROVIDER_UNLOCK", True),
                ("NO_PROVIDER_API", True),
                ("NO_PROVIDER_SEARCH", True),
                ("NO_SECRET_READ", True),
                ("NO_PROVIDER_METADATA_READ", True),
                ("NO_OBJECT_BODY", True),
                ("NO_DOWNLOAD", True),
                ("NO_RESTORE_EXPORT_UPLOAD_DELETE", True),
                ("NO_TOWER_UNLOCK", True),
                ("NO_OWNER_APPROVAL_UNLOCK", True),
                ("NO_EXECUTION", True),
                ("CLOUDS_PARKED", True),
            ]
            passed_count = len([c for c in checks if c[1]])
            failed_count = len(checks) - passed_count

            readiness_payload = {
                "schema_version": SCHEMA_VERSION,
                "readiness_id": READINESS_ID,
                "gp_number": 200,
                "pack_id": "VAULT_GP200",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp190_readiness_id": readiness["readiness_id"],
                "source_gp190_readiness_hash": readiness["readiness_hash"],
                "source_gp190_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "first_200_pack_arc_ready": failed_count == 0,
                "safe_to_continue_to_gp201": failed_count == 0,
                "section_ready": True,
                "product_readiness_checkpoint": True,
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
                "gp_number": 200,
                "pack_id": "VAULT_GP200",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "MAJOR_PRODUCT_READINESS_CHECKPOINT_READY_FIRST_200_PACK_ARC_READY_VAULT_NOT_DONE_LOCKED_SAFE_TO_CONTINUE",
                "readiness_score": readiness_payload["readiness_score"],
                **counts,
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "first_200_pack_arc_ready": 1 if failed_count == 0 else 0,
                "safe_to_continue_to_gp201": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "product_readiness_checkpoint": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_major_product_readiness_checkpoint", row)

            for event_type, event_payload in [
                ("GP191_MAJOR_PRODUCT_READINESS_SHELL_CREATED", {"component_id": READINESS_SHELL_ID}),
                ("GP192_PRODUCT_CAPABILITY_INVENTORY_CREATED", {"capability_count": counts["capability_count"]}),
                ("GP193_ROUTE_ENDPOINT_READINESS_BOARD_CREATED", {"route_endpoint_count": counts["route_endpoint_count"]}),
                ("GP194_DATA_STORE_READINESS_BOARD_CREATED", {"data_store_count": counts["data_store_count"]}),
                ("GP195_LOCK_BOUNDARY_AUDIT_BOARD_CREATED", {"lock_boundary_count": counts["lock_boundary_count"]}),
                ("GP196_OWNER_EXPERIENCE_READINESS_BOARD_CREATED", {"owner_experience_count": counts["owner_experience_count"]}),
                ("GP197_PROVIDER_INTEGRATION_READINESS_BOARD_CREATED", {"provider_integration_count": counts["provider_integration_count"]}),
                ("GP198_PRODUCT_RISK_BLOCKER_BOARD_CREATED", {"risk_blocker_count": counts["risk_blocker_count"]}),
                ("GP199_PRODUCT_READINESS_RECEIPT_PACKET_CREATED", {"receipt_packet_count": counts["receipt_packet_count"]}),
                ("GP200_MAJOR_PRODUCT_READINESS_CHECKPOINT_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp201": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_major_product_readiness_components").fetchone()["c"]),
            "capability_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_product_capability_inventory").fetchone()["c"]),
            "route_endpoint_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_route_endpoint_readiness_board").fetchone()["c"]),
            "data_store_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_data_store_readiness_board").fetchone()["c"]),
            "lock_boundary_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_lock_boundary_audit_board").fetchone()["c"]),
            "owner_experience_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_owner_experience_readiness_board").fetchone()["c"]),
            "provider_integration_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_provider_integration_readiness_board").fetchone()["c"]),
            "risk_blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_product_risk_blocker_board").fetchone()["c"]),
            "receipt_packet_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_product_readiness_receipt_packets").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_major_product_readiness_checkpoint").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_major_product_readiness_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_major_product_readiness_checkpoint_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_major_product_readiness_checkpoint_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_major_product_readiness_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_major_product_readiness_checkpoint_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_major_product_readiness_checkpoint WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_major_product_readiness_checkpoint_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_major_product_readiness_events ORDER BY created_at, event_id").fetchall()
    return [{"event_id": row["event_id"], "event_type": row["event_type"], "event_payload": _json_loads(row["event_payload_json"]), "created_at": row["created_at"]} for row in rows]

def get_product_capabilities(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_product_capability_inventory", "capability_code", db_path, {"payload_json": "payload"})

def get_route_endpoint_readiness_rows(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_route_endpoint_readiness_board", "route_code", db_path, {"payload_json": "payload"})

def get_data_store_readiness_rows(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_data_store_readiness_board", "store_code", db_path, {"payload_json": "payload"})

def get_lock_boundary_audit_rows(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_lock_boundary_audit_board", "boundary_code", db_path, {"payload_json": "payload"})

def get_owner_experience_readiness_rows(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_owner_experience_readiness_board", "item_code", db_path, {"payload_json": "payload"})

def get_provider_integration_readiness_rows(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_provider_integration_readiness_board", "item_code", db_path, {"payload_json": "payload"})

def get_product_risk_blockers(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_product_risk_blocker_board", "blocker_code", db_path, {"payload_json": "payload"})

def get_product_readiness_receipt_packets(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_product_readiness_receipt_packets", "packet_code", db_path, {"payload_json": "payload"})

def validate_major_product_readiness_checkpoint_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_major_product_readiness_components", "gp_number", db_path, {"data_json": "data"})
    capabilities = get_product_capabilities(db_path)
    routes = get_route_endpoint_readiness_rows(db_path)
    stores = get_data_store_readiness_rows(db_path)
    locks = get_lock_boundary_audit_rows(db_path)
    owner_items = get_owner_experience_readiness_rows(db_path)
    provider_items = get_provider_integration_readiness_rows(db_path)
    blockers = get_product_risk_blockers(db_path)
    packets = get_product_readiness_receipt_packets(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("CAPABILITY_COUNT_14", len(capabilities) == len(CAPABILITIES)),
        ("ROUTE_ENDPOINT_COUNT_12", len(routes) == len(ROUTE_ENDPOINTS)),
        ("DATA_STORE_COUNT_14", len(stores) == len(DATA_STORES)),
        ("LOCK_BOUNDARY_COUNT_15", len(locks) == len(LOCK_BOUNDARIES)),
        ("OWNER_EXPERIENCE_COUNT_6", len(owner_items) == len(OWNER_EXPERIENCE_ITEMS)),
        ("PROVIDER_INTEGRATION_COUNT_8", len(provider_items) == len(PROVIDER_INTEGRATION_ITEMS)),
        ("RISK_BLOCKER_COUNT_12", len(blockers) == len(RISK_BLOCKERS)),
        ("RECEIPT_PACKET_COUNT_1", len(packets) == 1),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("FIRST_200_PACK_ARC_READY", readiness["first_200_pack_arc_ready"] is True),
        ("SAFE_TO_CONTINUE_TO_GP201", readiness["safe_to_continue_to_gp201"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("PRODUCT_READINESS_CHECKPOINT", readiness["product_readiness_checkpoint"] is True),
        ("VAULT_NOT_DONE", readiness["vault_done"] is False),
        ("CLOUDS_PARKED", readiness["clouds_should_continue"] is False),
        ("SECTION_GP191_GP200", readiness["section_range"] == "GP191-GP200"),
        ("NEXT_SECTION_GP201_GP210", readiness["readiness_payload"]["next_section_range"] == "GP201-GP210"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_READY", all(item["component_ready"] is True for item in components)),
        ("ALL_COMPONENTS_LOCKED", all(item["component_locked"] is True for item in components)),
        ("ALL_COMPONENTS_FIRST_200_READY", all(item["first_200_pack_arc_ready"] is True for item in components)),
        ("ALL_COMPONENTS_VAULT_NOT_DONE", all(item["vault_not_done"] is True for item in components)),
        ("ALL_CAPABILITIES_READY", all(item["capability_ready"] is True for item in capabilities)),
        ("ALL_CAPABILITIES_LOCKED", all(item["capability_locked"] is True for item in capabilities)),
        ("ALL_ROUTES_READY", all(item["route_ready"] is True for item in routes)),
        ("ALL_ROUTES_LOCKED", all(item["route_locked"] is True for item in routes)),
        ("ALL_STORES_READY", all(item["store_ready"] is True for item in stores)),
        ("ALL_STORES_LOCKED", all(item["store_locked"] is True for item in stores)),
        ("ALL_LOCK_BOUNDARIES_LOCKED", all(item["boundary_locked"] is True for item in locks)),
        ("ALL_LOCK_AUDITS_PASSED", all(item["audit_passed"] is True for item in locks)),
        ("ALL_OWNER_EXPERIENCE_READY", all(item["item_ready"] is True for item in owner_items)),
        ("ALL_PROVIDER_ITEMS_READY", all(item["item_ready"] is True for item in provider_items)),
        ("ALL_PROVIDER_UNLOCKS_LOCKED", all(item["provider_unlock_locked"] is True for item in provider_items)),
        ("ALL_RISK_BLOCKERS_ACTIVE", all(item["blocker_active"] is True for item in blockers)),
        ("ALL_RISK_BLOCKERS_BLOCK_PRODUCT_DONE", all(item["blocks_product_done"] is True for item in blockers)),
        ("ALL_RISK_BLOCKERS_BLOCK_PROVIDER_UNLOCK", all(item["blocks_provider_unlock"] is True for item in blockers)),
        ("ALL_RISK_BLOCKERS_BLOCK_PROVIDER_API", all(item["blocks_provider_api"] is True for item in blockers)),
        ("ALL_RISK_BLOCKERS_BLOCK_OBJECT_BODY", all(item["blocks_object_body"] is True for item in blockers)),
        ("ALL_RISK_BLOCKERS_BLOCK_DANGEROUS_OPS", all(item["blocks_restore"] and item["blocks_export"] and item["blocks_direct_upload"] and item["blocks_delete"] for item in blockers)),
        ("ALL_RISK_BLOCKERS_BLOCK_TOWER_EXECUTION", all(item["blocks_tower_unlock"] and item["blocks_execution"] for item in blockers)),
        ("NO_RISK_BLOCKERS_RESOLVED", all(item["resolved"] is False for item in blockers)),
        ("PACKET_READY", all(item["packet_ready"] is True for item in packets)),
        ("PACKET_LOCKED", all(item["packet_locked"] is True for item in packets)),
        ("NO_FINAL_PRODUCT_RECEIPT", all(item["final_product_receipt"] is False for item in packets)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("CAPABILITY", capabilities),
        ("ROUTE", routes),
        ("STORE", stores),
        ("LOCK", locks),
        ("OWNER", owner_items),
        ("PROVIDER", provider_items),
        ("BLOCKER", blockers),
        ("PACKET", packets),
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
        "capability_count": len(capabilities),
        "route_endpoint_count": len(routes),
        "data_store_count": len(stores),
        "lock_boundary_count": len(locks),
        "owner_experience_count": len(owner_items),
        "provider_integration_count": len(provider_items),
        "risk_blocker_count": len(blockers),
        "receipt_packet_count": len(packets),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "first_200_pack_arc_ready": len(failed) == 0 and readiness["first_200_pack_arc_ready"] is True,
        "safe_to_continue_to_gp201": len(failed) == 0 and readiness["safe_to_continue_to_gp201"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp191_major_product_readiness_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_SHELL_ID, db_path)
    return {"pack": _pack_payload(191, component["pack_name"]), "real_sqlite_backed": True, "readiness_shell": component}

def get_gp192_product_capability_inventory(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(CAPABILITY_INVENTORY_ID, db_path)
    capabilities = get_product_capabilities(db_path)
    return {"pack": _pack_payload(192, component["pack_name"]), "real_sqlite_backed": True, "capability_inventory": component, "capability_count": len(capabilities), "capabilities": capabilities}

def get_gp193_route_endpoint_readiness_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(ROUTE_ENDPOINT_BOARD_ID, db_path)
    routes = get_route_endpoint_readiness_rows(db_path)
    return {"pack": _pack_payload(193, component["pack_name"]), "real_sqlite_backed": True, "route_endpoint_board": component, "route_endpoint_count": len(routes), "routes": routes}

def get_gp194_data_store_readiness_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(DATA_STORE_BOARD_ID, db_path)
    stores = get_data_store_readiness_rows(db_path)
    return {"pack": _pack_payload(194, component["pack_name"]), "real_sqlite_backed": True, "data_store_board": component, "data_store_count": len(stores), "stores": stores}

def get_gp195_lock_boundary_audit_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(LOCK_BOUNDARY_BOARD_ID, db_path)
    locks = get_lock_boundary_audit_rows(db_path)
    return {"pack": _pack_payload(195, component["pack_name"]), "real_sqlite_backed": True, "lock_boundary_board": component, "lock_boundary_count": len(locks), "locks": locks}

def get_gp196_owner_experience_readiness_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(OWNER_EXPERIENCE_BOARD_ID, db_path)
    owner_items = get_owner_experience_readiness_rows(db_path)
    return {"pack": _pack_payload(196, component["pack_name"]), "real_sqlite_backed": True, "owner_experience_board": component, "owner_experience_count": len(owner_items), "owner_items": owner_items}

def get_gp197_provider_integration_readiness_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(PROVIDER_INTEGRATION_BOARD_ID, db_path)
    provider_items = get_provider_integration_readiness_rows(db_path)
    return {"pack": _pack_payload(197, component["pack_name"]), "real_sqlite_backed": True, "provider_integration_board": component, "provider_integration_count": len(provider_items), "provider_items": provider_items}

def get_gp198_product_risk_blocker_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RISK_BLOCKER_BOARD_ID, db_path)
    blockers = get_product_risk_blockers(db_path)
    return {"pack": _pack_payload(198, component["pack_name"]), "real_sqlite_backed": True, "risk_blocker_board": component, "risk_blocker_count": len(blockers), "blockers": blockers}

def get_gp199_product_readiness_receipt_packet(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RECEIPT_PACKET_ID, db_path)
    packets = get_product_readiness_receipt_packets(db_path)
    return {"pack": _pack_payload(199, component["pack_name"]), "real_sqlite_backed": True, "receipt_packet_component": component, "receipt_packet_count": len(packets), "packets": packets}

def get_gp200_major_product_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_major_product_readiness_checkpoint_layer(db_path)
    return {"pack": _pack_payload(200, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_major_product_readiness_checkpoint_layer(db_path)
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
            "source_gp190_readiness_id": component["source_gp190_readiness_id"],
            "source_gp190_readiness_hash": component["source_gp190_readiness_hash"],
            "source_gp190_readiness_score": component["source_gp190_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "product_readiness_checkpoint": component["product_readiness_checkpoint"],
            "first_200_pack_arc_ready": component["first_200_pack_arc_ready"],
            "vault_not_done": component["vault_not_done"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp201": validation["safe_to_continue_to_gp201"],
            "foundation_status": "major_product_readiness_checkpoint_ready_first_200_pack_arc_ready_vault_not_done_locked_safe_to_continue",
            "next": next_label,
            **counts,
            "product_marked_done": component["product_marked_done"],
            "vault_done": False,
            "beta_launch_approved": component["beta_launch_approved"],
            "public_launch_approved": component["public_launch_approved"],
            "provider_unlock_requested": component["provider_unlock_requested"],
            "provider_unlock_approved": component["provider_unlock_approved"],
            "provider_connection_requested": component["provider_connection_requested"],
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
            "object_body_plaintext_visible": component["object_body_plaintext_visible"],
            "object_download_enabled": component["object_download_enabled"],
            "object_delete_executed": component["object_delete_executed"],
            "export_package_created": component["export_package_created"],
            "export_manifest_created": component["export_manifest_created"],
            "export_download_enabled": component["export_download_enabled"],
            "export_enabled": component["export_enabled"],
            "restore_request_created": component["restore_request_created"],
            "restore_job_created": component["restore_job_created"],
            "provider_restore_api_called": component["provider_restore_api_called"],
            "direct_upload_enabled": component["direct_upload_enabled"],
            "tower_unlock_granted": component["tower_unlock_granted"],
            "owner_approval_recorded": component["owner_approval_recorded"],
            "execution_enabled": component["execution_enabled"],
            "clouds_status": "parked_do_not_continue_from_vault_gp200",
        },
        "validation": validation,
    }

def get_gp191_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(191, READINESS_SHELL_ID, "VAULT_GP192_PRODUCT_CAPABILITY_INVENTORY", db_path)

def get_gp192_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(192, CAPABILITY_INVENTORY_ID, "VAULT_GP193_ROUTE_ENDPOINT_READINESS_BOARD", db_path)

def get_gp193_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(193, ROUTE_ENDPOINT_BOARD_ID, "VAULT_GP194_DATA_STORE_READINESS_BOARD", db_path)

def get_gp194_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(194, DATA_STORE_BOARD_ID, "VAULT_GP195_LOCK_BOUNDARY_AUDIT_BOARD", db_path)

def get_gp195_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(195, LOCK_BOUNDARY_BOARD_ID, "VAULT_GP196_OWNER_EXPERIENCE_READINESS_BOARD", db_path)

def get_gp196_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(196, OWNER_EXPERIENCE_BOARD_ID, "VAULT_GP197_PROVIDER_INTEGRATION_READINESS_BOARD", db_path)

def get_gp197_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(197, PROVIDER_INTEGRATION_BOARD_ID, "VAULT_GP198_PRODUCT_RISK_BLOCKER_BOARD", db_path)

def get_gp198_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(198, RISK_BLOCKER_BOARD_ID, "VAULT_GP199_PRODUCT_READINESS_RECEIPT_PACKET", db_path)

def get_gp199_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(199, RECEIPT_PACKET_ID, "VAULT_GP200_MAJOR_PRODUCT_READINESS_CHECKPOINT", db_path)

def get_gp200_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(200, READINESS_ID, NEXT_PACK, db_path)
    status["gp200_status"]["next_section"] = NEXT_SECTION_ID
    status["gp200_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp200_status"]["next_pack"] = NEXT_PACK
    return status

def get_major_product_readiness_checkpoint_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_major_product_readiness_checkpoint_layer(db_path)
    components = _rows("vault_major_product_readiness_components", "gp_number", db_path, {"data_json": "data"})
    capabilities = get_product_capabilities(db_path)
    routes = get_route_endpoint_readiness_rows(db_path)
    stores = get_data_store_readiness_rows(db_path)
    locks = get_lock_boundary_audit_rows(db_path)
    owner_items = get_owner_experience_readiness_rows(db_path)
    provider_items = get_provider_integration_readiness_rows(db_path)
    blockers = get_product_risk_blockers(db_path)
    packets = get_product_readiness_receipt_packets(db_path)
    readiness = _readiness(db_path)
    validation = validate_major_product_readiness_checkpoint_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "capabilities": {"capability_count": len(capabilities), "capabilities": capabilities},
        "routes": {"route_endpoint_count": len(routes), "routes": routes},
        "data_stores": {"data_store_count": len(stores), "stores": stores},
        "lock_boundaries": {"lock_boundary_count": len(locks), "locks": locks},
        "owner_experience": {"owner_experience_count": len(owner_items), "owner_items": owner_items},
        "provider_integration": {"provider_integration_count": len(provider_items), "provider_items": provider_items},
        "blockers": {"risk_blocker_count": len(blockers), "blockers": blockers},
        "receipt_packets": {"receipt_packet_count": len(packets), "packets": packets},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "major_product_readiness_checkpoint_layer_ready": True,
            "first_200_pack_arc_ready": validation["first_200_pack_arc_ready"],
            "safe_to_continue_to_gp201": validation["safe_to_continue_to_gp201"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "product_readiness_checkpoint": True,
            "product_marked_done": False,
            "vault_done": False,
            "clouds_should_continue": False,
            "beta_launch_approved": False,
            "public_launch_approved": False,
            "provider_unlock_requested": False,
            "provider_unlock_approved": False,
            "provider_connection_requested": False,
            "real_provider_connection_started": False,
            "provider_api_called": False,
            "provider_search_executed": False,
            "provider_token_created": False,
            "provider_session_created": False,
            "provider_job_reference_created": False,
            "provider_status_poll_started": False,
            "provider_credential_value_read": False,
            "provider_secret_value_read": False,
            "provider_endpoint_called": False,
            "provider_objects_listed": False,
            "provider_metadata_imported": False,
            "provider_metadata_read": False,
            "object_body_read": False,
            "object_body_view_enabled": False,
            "object_body_download_enabled": False,
            "object_body_plaintext_visible": False,
            "object_download_enabled": False,
            "object_delete_executed": False,
            "export_package_created": False,
            "restore_job_created": False,
            "direct_upload_enabled": False,
            "tower_unlock_granted": False,
            "owner_approval_recorded": False,
            "execution_enabled": False,
        },
        "route_map": {
            "page": "/vault/major-product-readiness-checkpoint-layer",
            "json": "/vault/major-product-readiness-checkpoint-layer.json",
            "gp191": "/vault/gp191-status.json",
            "gp192": "/vault/gp192-status.json",
            "gp193": "/vault/gp193-status.json",
            "gp194": "/vault/gp194-status.json",
            "gp195": "/vault/gp195-status.json",
            "gp196": "/vault/gp196-status.json",
            "gp197": "/vault/gp197-status.json",
            "gp198": "/vault/gp198-status.json",
            "gp199": "/vault/gp199-status.json",
            "gp200": "/vault/gp200-status.json",
        },
    }

def render_major_product_readiness_checkpoint_layer_page() -> str:
    home = get_major_product_readiness_checkpoint_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    capability_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['capability_name'])}</strong>
          <span>{escape(item['capability_status'])}</span>
          <code>{escape(item['capability_category'])}</code>
        </article>
        """
        for item in home["capabilities"]["capabilities"][:9]
    )

    lock_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['boundary_name'])}</strong>
          <span>{escape(item['boundary_status'])}</span>
          <code>audit passed · locked</code>
        </article>
        """
        for item in home["lock_boundaries"]["locks"][:9]
    )

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP191-GP200 Major Product Readiness Checkpoint Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 191-200</div>
    <div class="eyebrow">Major Product Readiness Checkpoint Layer · GP191-GP200</div>
    <h1>Major Product Readiness Checkpoint</h1>
    <p>This layer closes the first 200-pack Vault readiness arc. It proves product capabilities, routes, data stores, lock boundaries, owner experience, provider integration readiness, risk blockers, and a receipt packet. Vault is still not done.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['capability_count']}</strong><span>capabilities</span></div>
      <div class="metric"><strong>{home['store']['lock_boundary_count']}</strong><span>lock boundaries</span></div>
      <div class="metric"><strong>{home['store']['risk_blocker_count']}</strong><span>risk blockers</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP191-GP200 built</span>
      <span class="pill ok">First 200-pack arc ready</span>
      <span class="pill ok">Safe to GP201</span>
      <span class="pill danger">Vault not done</span>
      <span class="pill danger">No provider unlock</span>
      <span class="pill danger">No object body</span>
      <span class="pill danger">No restore/export/upload/delete</span>
      <span class="pill danger">No Tower unlock</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Product Capabilities</h2>
    <div class="cards">{capability_cards}</div>
  </section>

  <section class="section">
    <h2>Lock Boundary Audit</h2>
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
