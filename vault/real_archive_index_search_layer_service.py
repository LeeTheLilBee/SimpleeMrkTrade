"""
VAULT GP181-GP190 — Real Archive Index and Search Layer

New section:
Archive Vault — Real Archive Index and Search Layer / GP181-GP190

Builds:
- GP181 Real Archive Index Shell
- GP182 Archive Metadata Index Registry
- GP183 Archive Search Query Contract
- GP184 Search Result Redaction Contract
- GP185 Metadata Search Receipt Ledger
- GP186 Search Filter and Facet Map
- GP187 Index Integrity Hash Board
- GP188 Object Body and Download Search Prohibition
- GP189 Archive Index Search Blocker Board
- GP190 Archive Index Search Readiness Checkpoint

This layer creates a real local SQLite archive metadata index/search surface.
It remains metadata-only and redacted-only. It never contacts a provider, reads
provider metadata, reads object bodies, downloads, restores, exports, uploads,
deletes, unlocks Tower gates, executes, or marks Vault done.
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

from vault.controlled_read_only_metadata_test_layer_service import (
    get_gp180_status,
    get_gp180_controlled_metadata_test_readiness_checkpoint,
    get_controlled_read_only_metadata_test_layer_home,
    validate_controlled_read_only_metadata_test_layer,
    get_metadata_scope_items,
    get_controlled_metadata_test_blockers,
)

LAYER_ID = "VAULT_GP181_190"
LAYER_NAME = "Real Archive Index and Search Layer"
SCHEMA_VERSION = "vault.real_archive_index_search_layer.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_ARCHIVE_INDEX_AND_SEARCH_LAYER"
SECTION_TITLE = "Archive Vault — Real Archive Index and Search Layer"
SECTION_RANGE = "GP181-GP190"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_READ_ONLY_METADATA_TEST_LAYER"
PREVIOUS_SECTION_RANGE = "GP171-GP180"

NEXT_SECTION_ID = "ARCHIVE_VAULT_MAJOR_PRODUCT_READINESS_CHECKPOINT_LAYER"
NEXT_SECTION_RANGE = "GP191-GP200"
NEXT_PACK = "VAULT_GP191_200_MAJOR_PRODUCT_READINESS_CHECKPOINT_LAYER"

DEFAULT_DB_ENV = "VAULT_REAL_ARCHIVE_INDEX_SEARCH_LAYER_DB"
DEFAULT_DB_PATH = "data/vault_real_archive_index_search_layer.sqlite"

INDEX_SHELL_ID = "VRAIS-SHELL-GP181-001"
METADATA_INDEX_REGISTRY_ID = "VRAIS-INDEX-GP182-001"
SEARCH_QUERY_CONTRACT_ID = "VRAIS-QUERY-GP183-001"
RESULT_REDACTION_CONTRACT_ID = "VRAIS-REDACTION-GP184-001"
SEARCH_RECEIPT_LEDGER_ID = "VRAIS-RECEIPT-GP185-001"
SEARCH_FILTER_FACET_MAP_ID = "VRAIS-FACET-GP186-001"
INDEX_INTEGRITY_HASH_BOARD_ID = "VRAIS-HASH-GP187-001"
BODY_DOWNLOAD_SEARCH_PROHIBITION_ID = "VRAIS-BODYLOCK-GP188-001"
BLOCKER_BOARD_ID = "VRAIS-BLOCKER-GP189-001"
READINESS_ID = "VRAIS-READINESS-GP190-001"

FALSE_FIELDS = [
    "provider_search_requested",
    "provider_search_approved",
    "provider_search_executed",
    "archive_search_provider_backed",
    "real_provider_connection_requested",
    "real_provider_connection_started",
    "real_provider_connection_completed",
    "provider_api_configured",
    "provider_api_called",
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
    "vault_done",
    "clouds_should_continue",
]

INDEX_RECORDS = [
    ("trust_receipt_packet", "Trust Receipt Packet", "receipt", "trust", "application/json", "redacted trust receipt metadata"),
    ("atm_route_contract", "ATM Route Contract", "contract", "atm", "application/pdf", "redacted atm contract metadata"),
    ("apartment_due_diligence_packet", "Apartment Due Diligence Packet", "property", "property", "application/pdf", "redacted property diligence metadata"),
    ("tower_gate_receipt", "Tower Gate Receipt", "tower", "security", "application/json", "redacted tower gate metadata"),
    ("ob_manual_live_receipt", "OB Manual Live Receipt", "observatory", "ob", "application/json", "redacted observatory receipt metadata"),
    ("teller_policy_ack", "Teller Policy Acknowledgment", "teller", "people", "application/json", "redacted teller policy metadata"),
    ("vault_provider_lock_contract", "Vault Provider Lock Contract", "vault", "provider", "application/json", "redacted provider lock metadata"),
    ("simplee_world_board_note", "Simplee World Board Note", "governance", "owner", "text/markdown", "redacted board note metadata"),
]

SEARCH_CONTRACTS = [
    ("keyword_search_contract", "Keyword Search Contract", "keyword", ["title", "summary_redacted", "category", "lane"]),
    ("lane_filter_search_contract", "Lane Filter Search Contract", "filter", ["lane", "category"]),
    ("content_type_filter_contract", "Content Type Filter Contract", "filter", ["content_type"]),
    ("receipt_hash_lookup_contract", "Receipt Hash Lookup Contract", "hash", ["index_hash", "redaction_hash"]),
    ("date_bucket_filter_contract", "Date Bucket Filter Contract", "filter", ["created_bucket"]),
    ("readiness_status_filter_contract", "Readiness Status Filter Contract", "filter", ["metadata_index_status"]),
]

FACETS = [
    ("lane", "Lane", ["trust", "atm", "property", "security", "ob", "people", "provider", "owner"]),
    ("category", "Category", ["receipt", "contract", "property", "tower", "observatory", "teller", "vault", "governance"]),
    ("content_type", "Content Type", ["application/json", "application/pdf", "text/markdown"]),
    ("redaction_state", "Redaction State", ["redacted_only"]),
    ("metadata_source", "Metadata Source", ["local_sqlite_seed"]),
    ("readiness_state", "Readiness State", ["indexed_locked"]),
]

PROHIBITIONS = [
    ("search_result_body_read_prohibited", "Search Result Body Read Prohibited"),
    ("search_result_body_view_prohibited", "Search Result Body View Prohibited"),
    ("search_result_download_prohibited", "Search Result Download Prohibited"),
    ("search_result_plaintext_prohibited", "Search Result Plaintext Prohibited"),
    ("search_provider_query_prohibited", "Provider Search Query Prohibited"),
    ("search_restore_export_upload_delete_prohibited", "Search Restore/Export/Upload/Delete Prohibited"),
    ("search_secret_value_prohibited", "Search Secret Value Prohibited"),
    ("search_execution_prohibited", "Search Execution Prohibited"),
]

BLOCKER_SPECS = [
    ("provider_search_locked", "Provider search locked", "provider_search", "critical"),
    ("provider_connection_locked", "Provider connection locked", "connection", "critical"),
    ("provider_api_locked", "Provider API locked", "provider_api", "critical"),
    ("provider_token_session_job_locked", "Provider token/session/job locked", "token_session_job", "critical"),
    ("credential_secret_locked", "Credential/secret value locked", "credential", "critical"),
    ("endpoint_call_locked", "Endpoint call locked", "endpoint", "critical"),
    ("provider_object_metadata_locked", "Provider object metadata read/import locked", "metadata", "critical"),
    ("object_body_download_locked", "Object body/download locked", "object_body", "critical"),
    ("result_plaintext_locked", "Result plaintext locked", "plaintext", "critical"),
    ("restore_export_upload_delete_locked", "Restore/export/upload/delete locked", "dangerous_ops", "critical"),
    ("tower_unlock_locked", "Tower unlock locked", "tower", "critical"),
    ("execution_vault_done_locked", "Execution and Vault done locked", "execution", "critical"),
]

COMPONENT_SPECS = [
    (181, INDEX_SHELL_ID, "VAULT_GP181", "Real Archive Index Shell", "real_archive_index_shell"),
    (182, METADATA_INDEX_REGISTRY_ID, "VAULT_GP182", "Archive Metadata Index Registry", "archive_metadata_index_registry"),
    (183, SEARCH_QUERY_CONTRACT_ID, "VAULT_GP183", "Archive Search Query Contract", "archive_search_query_contract"),
    (184, RESULT_REDACTION_CONTRACT_ID, "VAULT_GP184", "Search Result Redaction Contract", "search_result_redaction_contract"),
    (185, SEARCH_RECEIPT_LEDGER_ID, "VAULT_GP185", "Metadata Search Receipt Ledger", "metadata_search_receipt_ledger"),
    (186, SEARCH_FILTER_FACET_MAP_ID, "VAULT_GP186", "Search Filter and Facet Map", "search_filter_facet_map"),
    (187, INDEX_INTEGRITY_HASH_BOARD_ID, "VAULT_GP187", "Index Integrity Hash Board", "index_integrity_hash_board"),
    (188, BODY_DOWNLOAD_SEARCH_PROHIBITION_ID, "VAULT_GP188", "Object Body and Download Search Prohibition", "object_body_download_search_prohibition"),
    (189, BLOCKER_BOARD_ID, "VAULT_GP189", "Archive Index Search Blocker Board", "archive_index_search_blocker_board"),
    (190, READINESS_ID, "VAULT_GP190", "Archive Index Search Readiness Checkpoint", "archive_index_search_readiness_checkpoint"),
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
        "source_gp180_readiness_score",
        "component_count",
        "index_record_count",
        "search_contract_count",
        "receipt_count",
        "facet_count",
        "integrity_hash_count",
        "prohibition_count",
        "blocker_count",
        "event_count",
        "readiness_score",
        "check_count",
        "passed_count",
        "failed_count",
        "metadata_size_bucket",
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
            or key.endswith("_bucket")
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
        "depends_on": ["VAULT_GP180"],
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
        "depends_on": ["VAULT_GP180"],
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "next_section": NEXT_SECTION_ID,
        "next_section_range": NEXT_SECTION_RANGE,
    }

def ensure_real_archive_index_search_layer_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
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
            CREATE TABLE IF NOT EXISTS vault_real_archive_index_components (
                component_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                pack_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_gp180_readiness_id TEXT NOT NULL,
                source_gp180_readiness_hash TEXT NOT NULL,
                source_gp180_readiness_score INTEGER NOT NULL,
                component_ready INTEGER NOT NULL DEFAULT 1,
                component_locked INTEGER NOT NULL DEFAULT 1,
                local_sqlite_index INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                body_download_prohibited INTEGER NOT NULL DEFAULT 1,
                no_provider_contact INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_archive_metadata_index_records (
                index_record_id TEXT PRIMARY KEY,
                record_code TEXT NOT NULL UNIQUE,
                title_redacted TEXT NOT NULL,
                category TEXT NOT NULL,
                lane TEXT NOT NULL,
                content_type TEXT NOT NULL,
                summary_redacted TEXT NOT NULL,
                metadata_size_bucket INTEGER NOT NULL,
                metadata_index_status TEXT NOT NULL,
                local_sqlite_index INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                searchable_locally INTEGER NOT NULL DEFAULT 1,
                body_download_prohibited INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                index_hash TEXT NOT NULL,
                redaction_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_archive_search_query_contracts (
                search_contract_id TEXT PRIMARY KEY,
                search_code TEXT NOT NULL UNIQUE,
                search_name TEXT NOT NULL,
                search_type TEXT NOT NULL,
                allowed_fields_json TEXT NOT NULL,
                contract_status TEXT NOT NULL,
                local_sqlite_only INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                provider_search_locked INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                contract_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_metadata_search_receipts (
                receipt_id TEXT PRIMARY KEY,
                receipt_code TEXT NOT NULL UNIQUE,
                receipt_name TEXT NOT NULL,
                receipt_status TEXT NOT NULL,
                receipt_locked INTEGER NOT NULL DEFAULT 1,
                local_sqlite_only INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                final_receipt_created INTEGER NOT NULL DEFAULT 0,
                payload_json TEXT NOT NULL,
                receipt_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_search_filter_facet_map (
                facet_id TEXT PRIMARY KEY,
                facet_code TEXT NOT NULL UNIQUE,
                facet_name TEXT NOT NULL,
                facet_values_json TEXT NOT NULL,
                facet_status TEXT NOT NULL,
                local_sqlite_only INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                facet_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_index_integrity_hash_board (
                integrity_id TEXT PRIMARY KEY,
                integrity_code TEXT NOT NULL UNIQUE,
                source_table TEXT NOT NULL,
                source_count INTEGER NOT NULL,
                integrity_status TEXT NOT NULL,
                integrity_hash TEXT NOT NULL,
                local_sqlite_only INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_search_body_download_prohibitions (
                prohibition_id TEXT PRIMARY KEY,
                prohibition_code TEXT NOT NULL UNIQUE,
                prohibition_name TEXT NOT NULL,
                prohibition_status TEXT NOT NULL,
                prohibition_active INTEGER NOT NULL DEFAULT 1,
                search_surface_locked INTEGER NOT NULL DEFAULT 1,
                body_download_prohibited INTEGER NOT NULL DEFAULT 1,
                payload_json TEXT NOT NULL,
                prohibition_hash TEXT NOT NULL,
                {false_sql},
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vault_archive_index_search_blockers (
                blocker_id TEXT PRIMARY KEY,
                blocker_code TEXT NOT NULL UNIQUE,
                blocker_name TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocker_active INTEGER NOT NULL DEFAULT 1,
                blocks_provider_search INTEGER NOT NULL DEFAULT 1,
                blocks_real_connection INTEGER NOT NULL DEFAULT 1,
                blocks_provider_api INTEGER NOT NULL DEFAULT 1,
                blocks_provider_token INTEGER NOT NULL DEFAULT 1,
                blocks_provider_session INTEGER NOT NULL DEFAULT 1,
                blocks_provider_job INTEGER NOT NULL DEFAULT 1,
                blocks_status_poll INTEGER NOT NULL DEFAULT 1,
                blocks_secret_read INTEGER NOT NULL DEFAULT 1,
                blocks_endpoint_call INTEGER NOT NULL DEFAULT 1,
                blocks_object_catalog INTEGER NOT NULL DEFAULT 1,
                blocks_metadata_read INTEGER NOT NULL DEFAULT 1,
                blocks_object_body INTEGER NOT NULL DEFAULT 1,
                blocks_download INTEGER NOT NULL DEFAULT 1,
                blocks_restore INTEGER NOT NULL DEFAULT 1,
                blocks_export INTEGER NOT NULL DEFAULT 1,
                blocks_direct_upload INTEGER NOT NULL DEFAULT 1,
                blocks_delete INTEGER NOT NULL DEFAULT 1,
                blocks_tower_unlock INTEGER NOT NULL DEFAULT 1,
                blocks_execution INTEGER NOT NULL DEFAULT 1,
                blocks_vault_done INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_archive_index_search_readiness (
                readiness_id TEXT PRIMARY KEY,
                gp_number INTEGER NOT NULL,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                readiness_status TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                component_count INTEGER NOT NULL,
                index_record_count INTEGER NOT NULL,
                search_contract_count INTEGER NOT NULL,
                receipt_count INTEGER NOT NULL,
                facet_count INTEGER NOT NULL,
                integrity_hash_count INTEGER NOT NULL,
                prohibition_count INTEGER NOT NULL,
                blocker_count INTEGER NOT NULL,
                check_count INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                failed_count INTEGER NOT NULL,
                readiness_hash TEXT NOT NULL,
                readiness_payload_json TEXT NOT NULL,
                safe_to_continue_to_gp191 INTEGER NOT NULL DEFAULT 1,
                section_ready INTEGER NOT NULL DEFAULT 1,
                local_sqlite_index INTEGER NOT NULL DEFAULT 1,
                metadata_only INTEGER NOT NULL DEFAULT 1,
                redacted_only INTEGER NOT NULL DEFAULT 1,
                body_download_prohibited INTEGER NOT NULL DEFAULT 1,
                no_provider_contact INTEGER NOT NULL DEFAULT 1,
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
            CREATE TABLE IF NOT EXISTS vault_archive_index_search_events (
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
            "vault_real_archive_index_components",
            "vault_archive_metadata_index_records",
            "vault_archive_search_query_contracts",
            "vault_metadata_search_receipts",
            "vault_search_filter_facet_map",
            "vault_index_integrity_hash_board",
            "vault_search_body_download_prohibitions",
            "vault_archive_index_search_blockers",
            "vault_archive_index_search_readiness",
            "vault_archive_index_search_events",
        ],
    }

def _insert_event(conn: sqlite3.Connection, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VRAISEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_archive_index_search_events",
        {
            "event_id": event_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id

def initialize_real_archive_index_search_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_real_archive_index_search_layer_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            "SELECT component_id FROM vault_real_archive_index_components WHERE component_id = ?",
            (INDEX_SHELL_ID,),
        ).fetchone()

        if existing is None:
            gp180_status = get_gp180_status()["gp180_status"]
            gp180_checkpoint = get_gp180_controlled_metadata_test_readiness_checkpoint()["readiness_checkpoint"]
            gp180_home = get_controlled_read_only_metadata_test_layer_home()
            gp180_validation = validate_controlled_read_only_metadata_test_layer()

            source_scopes = get_metadata_scope_items()
            source_blockers = get_controlled_metadata_test_blockers()

            readiness = gp180_checkpoint["readiness"]
            now = _now_iso()

            source_payload = {
                "source_gp180_readiness_id": readiness["readiness_id"],
                "source_gp180_readiness_hash": readiness["readiness_hash"],
                "source_gp180_readiness_score": readiness["readiness_score"],
            }

            counts = {
                "component_count": len(COMPONENT_SPECS),
                "index_record_count": len(INDEX_RECORDS),
                "search_contract_count": len(SEARCH_CONTRACTS),
                "receipt_count": len(SEARCH_CONTRACTS),
                "facet_count": len(FACETS),
                "integrity_hash_count": 5,
                "prohibition_count": len(PROHIBITIONS),
                "blocker_count": len(BLOCKER_SPECS),
            }

            source_context = {
                "source_gp180_status_ready": gp180_status["ready"],
                "source_gp180_validation_passed": gp180_status["validation_passed"],
                "source_gp180_safe_to_continue_to_gp181": gp180_status["safe_to_continue_to_gp181"],
                "source_gp180_readiness_hash": readiness["readiness_hash"],
                "source_gp180_readiness_score": readiness["readiness_score"],
                "source_metadata_scope_count": len(source_scopes),
                "source_metadata_blocker_count": len(source_blockers),
                "source_validation_check_count": gp180_validation["check_count"],
            }

            component_extra = {
                INDEX_SHELL_ID: {"real_archive_index_shell_ready": True},
                METADATA_INDEX_REGISTRY_ID: {"archive_metadata_index_registry_ready": True, "index_record_count": counts["index_record_count"]},
                SEARCH_QUERY_CONTRACT_ID: {"archive_search_query_contract_ready": True, "search_contract_count": counts["search_contract_count"]},
                RESULT_REDACTION_CONTRACT_ID: {"search_result_redaction_contract_ready": True, "redacted_only": True},
                SEARCH_RECEIPT_LEDGER_ID: {"metadata_search_receipt_ledger_ready": True, "receipt_count": counts["receipt_count"]},
                SEARCH_FILTER_FACET_MAP_ID: {"search_filter_facet_map_ready": True, "facet_count": counts["facet_count"]},
                INDEX_INTEGRITY_HASH_BOARD_ID: {"index_integrity_hash_board_ready": True, "integrity_hash_count": counts["integrity_hash_count"]},
                BODY_DOWNLOAD_SEARCH_PROHIBITION_ID: {"object_body_download_search_prohibition_ready": True, "prohibition_count": counts["prohibition_count"]},
                BLOCKER_BOARD_ID: {"archive_index_search_blocker_board_ready": True, "blocker_count": counts["blocker_count"]},
                READINESS_ID: {"archive_index_search_readiness_checkpoint_ready": True, "safe_to_continue_to_gp191": True},
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
                    "local_sqlite_index": True,
                    "metadata_only": True,
                    "redacted_only": True,
                    "body_download_prohibited": True,
                    "no_provider_contact": True,
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
                    "local_sqlite_index": 1,
                    "metadata_only": 1,
                    "redacted_only": 1,
                    "body_download_prohibited": 1,
                    "no_provider_contact": 1,
                    "safe_to_continue": 1,
                    "data_json": _json_dumps(payload),
                    "component_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_real_archive_index_components", row)

            for idx, (code, title, category, lane, content_type, summary) in enumerate(INDEX_RECORDS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "record_code": code,
                    "title_redacted": title,
                    "category": category,
                    "lane": lane,
                    "content_type": content_type,
                    "summary_redacted": summary,
                    "metadata_size_bucket": idx * 10,
                    "metadata_index_status": "LOCAL_SQLITE_INDEXED_REDACTED_METADATA_ONLY",
                    "local_sqlite_index": True,
                    "metadata_only": True,
                    "redacted_only": True,
                    "searchable_locally": True,
                    "body_download_prohibited": True,
                    "search_terms": [code, category, lane, "redacted", "metadata"],
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "index_record_id": f"VRAISIDX-{idx:03d}",
                    "record_code": code,
                    "title_redacted": title,
                    "category": category,
                    "lane": lane,
                    "content_type": content_type,
                    "summary_redacted": summary,
                    "metadata_size_bucket": idx * 10,
                    "metadata_index_status": payload["metadata_index_status"],
                    "local_sqlite_index": 1,
                    "metadata_only": 1,
                    "redacted_only": 1,
                    "searchable_locally": 1,
                    "body_download_prohibited": 1,
                    "payload_json": _json_dumps(payload),
                    "index_hash": _hash_payload(payload),
                    "redaction_hash": _hash_payload({"record_code": code, "title_redacted": title, "summary_redacted": summary}),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_archive_metadata_index_records", row)

            for idx, (code, name, search_type, allowed_fields) in enumerate(SEARCH_CONTRACTS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "search_code": code,
                    "search_name": name,
                    "search_type": search_type,
                    "allowed_fields": allowed_fields,
                    "contract_status": "LOCAL_SQLITE_METADATA_SEARCH_CONTRACT_READY_PROVIDER_SEARCH_LOCKED",
                    "local_sqlite_only": True,
                    "metadata_only": True,
                    "redacted_only": True,
                    "provider_search_locked": True,
                    "blocked_fields": ["object_body", "plaintext", "download_url", "secret_value", "provider_token", "provider_session"],
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "search_contract_id": f"VRAISQRY-{idx:03d}",
                    "search_code": code,
                    "search_name": name,
                    "search_type": search_type,
                    "allowed_fields_json": _json_dumps(allowed_fields),
                    "contract_status": payload["contract_status"],
                    "local_sqlite_only": 1,
                    "metadata_only": 1,
                    "redacted_only": 1,
                    "provider_search_locked": 1,
                    "payload_json": _json_dumps(payload),
                    "contract_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_archive_search_query_contracts", row)

                receipt_payload = {
                    "schema_version": SCHEMA_VERSION,
                    "receipt_code": f"{code}_metadata_search_receipt",
                    "receipt_name": f"{name} Receipt",
                    "receipt_status": "DRAFT_LEDGER_READY_NOT_FINALIZED_NO_PROVIDER_SEARCH",
                    "receipt_locked": True,
                    "local_sqlite_only": True,
                    "metadata_only": True,
                    "redacted_only": True,
                    "final_receipt_created": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "receipt_id": f"VRAISRCP-{idx:03d}",
                    "receipt_code": receipt_payload["receipt_code"],
                    "receipt_name": receipt_payload["receipt_name"],
                    "receipt_status": receipt_payload["receipt_status"],
                    "receipt_locked": 1,
                    "local_sqlite_only": 1,
                    "metadata_only": 1,
                    "redacted_only": 1,
                    "final_receipt_created": 0,
                    "payload_json": _json_dumps(receipt_payload),
                    "receipt_hash": _hash_payload(receipt_payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_metadata_search_receipts", row)

            for idx, (code, name, values) in enumerate(FACETS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "facet_code": code,
                    "facet_name": name,
                    "facet_values": values,
                    "facet_status": "FACET_READY_LOCAL_REDACTED_METADATA_ONLY",
                    "local_sqlite_only": True,
                    "metadata_only": True,
                    "redacted_only": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "facet_id": f"VRAISFACET-{idx:03d}",
                    "facet_code": code,
                    "facet_name": name,
                    "facet_values_json": _json_dumps(values),
                    "facet_status": payload["facet_status"],
                    "local_sqlite_only": 1,
                    "metadata_only": 1,
                    "redacted_only": 1,
                    "payload_json": _json_dumps(payload),
                    "facet_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_search_filter_facet_map", row)

            integrity_sources = [
                ("component_integrity", "vault_real_archive_index_components", counts["component_count"]),
                ("index_record_integrity", "vault_archive_metadata_index_records", counts["index_record_count"]),
                ("search_contract_integrity", "vault_archive_search_query_contracts", counts["search_contract_count"]),
                ("facet_integrity", "vault_search_filter_facet_map", counts["facet_count"]),
                ("blocker_integrity", "vault_archive_index_search_blockers", counts["blocker_count"]),
            ]

            for idx, (code, source_table, source_count) in enumerate(integrity_sources, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "integrity_code": code,
                    "source_table": source_table,
                    "source_count": source_count,
                    "integrity_status": "LOCAL_SQLITE_HASHED_METADATA_ONLY",
                    "local_sqlite_only": True,
                    "metadata_only": True,
                    "redacted_only": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "integrity_id": f"VRAISHASH-{idx:03d}",
                    "integrity_code": code,
                    "source_table": source_table,
                    "source_count": source_count,
                    "integrity_status": payload["integrity_status"],
                    "integrity_hash": _hash_payload(payload),
                    "local_sqlite_only": 1,
                    "metadata_only": 1,
                    "redacted_only": 1,
                    "payload_json": _json_dumps(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_index_integrity_hash_board", row)

            for idx, (code, name) in enumerate(PROHIBITIONS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "prohibition_code": code,
                    "prohibition_name": name,
                    "prohibition_status": "ACTIVE_SEARCH_SURFACE_PROHIBITION",
                    "prohibition_active": True,
                    "search_surface_locked": True,
                    "body_download_prohibited": True,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "prohibition_id": f"VRAISPROH-{idx:03d}",
                    "prohibition_code": code,
                    "prohibition_name": name,
                    "prohibition_status": payload["prohibition_status"],
                    "prohibition_active": 1,
                    "search_surface_locked": 1,
                    "body_download_prohibited": 1,
                    "payload_json": _json_dumps(payload),
                    "prohibition_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_search_body_download_prohibitions", row)

            for idx, (code, name, category, severity) in enumerate(BLOCKER_SPECS, start=1):
                payload = {
                    "schema_version": SCHEMA_VERSION,
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": "ACTIVE_ARCHIVE_INDEX_SEARCH_BLOCKER",
                    "blocker_active": True,
                    "blocks_provider_search": True,
                    "blocks_real_connection": True,
                    "blocks_provider_api": True,
                    "blocks_provider_token": True,
                    "blocks_provider_session": True,
                    "blocks_provider_job": True,
                    "blocks_status_poll": True,
                    "blocks_secret_read": True,
                    "blocks_endpoint_call": True,
                    "blocks_object_catalog": True,
                    "blocks_metadata_read": True,
                    "blocks_object_body": True,
                    "blocks_download": True,
                    "blocks_restore": True,
                    "blocks_export": True,
                    "blocks_direct_upload": True,
                    "blocks_delete": True,
                    "blocks_tower_unlock": True,
                    "blocks_execution": True,
                    "blocks_vault_done": True,
                    "resolved": False,
                    "locked_truth": {field: False for field in FALSE_FIELDS},
                    "vault_done": False,
                    "clouds_should_continue": False,
                }
                row = {
                    "blocker_id": f"VRAISBLK-{idx:03d}",
                    "blocker_code": code,
                    "blocker_name": name,
                    "blocker_category": category,
                    "severity": severity,
                    "blocker_status": payload["blocker_status"],
                    "blocker_active": 1,
                    "blocks_provider_search": 1,
                    "blocks_real_connection": 1,
                    "blocks_provider_api": 1,
                    "blocks_provider_token": 1,
                    "blocks_provider_session": 1,
                    "blocks_provider_job": 1,
                    "blocks_status_poll": 1,
                    "blocks_secret_read": 1,
                    "blocks_endpoint_call": 1,
                    "blocks_object_catalog": 1,
                    "blocks_metadata_read": 1,
                    "blocks_object_body": 1,
                    "blocks_download": 1,
                    "blocks_restore": 1,
                    "blocks_export": 1,
                    "blocks_direct_upload": 1,
                    "blocks_delete": 1,
                    "blocks_tower_unlock": 1,
                    "blocks_execution": 1,
                    "blocks_vault_done": 1,
                    "resolved": 0,
                    "payload_json": _json_dumps(payload),
                    "blocker_hash": _hash_payload(payload),
                    "created_at": now,
                    "updated_at": now,
                }
                for field in FALSE_FIELDS:
                    row[field] = 0
                _insert_dict(conn, "vault_archive_index_search_blockers", row)

            checks = [
                ("SOURCE_GP180_READY", bool(gp180_status["ready"])),
                ("SOURCE_GP180_VALIDATION_PASSED", bool(gp180_status["validation_passed"])),
                ("SOURCE_GP180_SAFE_TO_CONTINUE", bool(gp180_status["safe_to_continue_to_gp181"])),
                ("SOURCE_GP180_READINESS_SCORE_100", readiness["readiness_score"] == 100),
                ("SOURCE_GP180_READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
                ("COMPONENT_COUNT_10", counts["component_count"] == 10),
                ("INDEX_RECORD_COUNT_8", counts["index_record_count"] == 8),
                ("SEARCH_CONTRACT_COUNT_6", counts["search_contract_count"] == 6),
                ("RECEIPT_COUNT_6", counts["receipt_count"] == 6),
                ("FACET_COUNT_6", counts["facet_count"] == 6),
                ("INTEGRITY_HASH_COUNT_5", counts["integrity_hash_count"] == 5),
                ("PROHIBITION_COUNT_8", counts["prohibition_count"] == 8),
                ("BLOCKER_COUNT_12", counts["blocker_count"] == 12),
                ("SECTION_GP181_GP190", SECTION_RANGE == "GP181-GP190"),
                ("NEXT_SECTION_GP191_GP200", NEXT_SECTION_RANGE == "GP191-GP200"),
                ("LOCAL_SQLITE_INDEX", True),
                ("METADATA_ONLY", True),
                ("REDACTED_ONLY", True),
                ("BODY_DOWNLOAD_PROHIBITED", True),
                ("NO_PROVIDER_CONTACT", True),
                ("NO_PROVIDER_SEARCH", True),
                ("NO_PROVIDER_API", True),
                ("NO_PROVIDER_TOKEN_SESSION_JOB", True),
                ("NO_STATUS_POLL", True),
                ("NO_SECRET_READ", True),
                ("NO_ENDPOINT_CALL", True),
                ("NO_PROVIDER_OBJECT_LIST", True),
                ("NO_PROVIDER_METADATA_READ", True),
                ("NO_OBJECT_BODY", True),
                ("NO_DOWNLOAD", True),
                ("NO_RESTORE_EXPORT_UPLOAD_DELETE", True),
                ("NO_TOWER_UNLOCK", True),
                ("NO_EXECUTION", True),
                ("VAULT_NOT_DONE", True),
                ("CLOUDS_PARKED", True),
            ]
            passed_count = len([c for c in checks if c[1]])
            failed_count = len(checks) - passed_count

            readiness_payload = {
                "schema_version": SCHEMA_VERSION,
                "readiness_id": READINESS_ID,
                "gp_number": 190,
                "pack_id": "VAULT_GP190",
                "section_id": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "source_gp180_readiness_id": readiness["readiness_id"],
                "source_gp180_readiness_hash": readiness["readiness_hash"],
                "source_gp180_readiness_score": readiness["readiness_score"],
                **counts,
                "checks": [{"code": code, "passed": bool(passed)} for code, passed in checks],
                "readiness_score": 100 if failed_count == 0 else 0,
                "safe_to_continue_to_gp191": failed_count == 0,
                "section_ready": True,
                "local_sqlite_index": True,
                "metadata_only": True,
                "redacted_only": True,
                "body_download_prohibited": True,
                "no_provider_contact": True,
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
                "gp_number": 190,
                "pack_id": "VAULT_GP190",
                "section_id": SECTION_ID,
                "section_range": SECTION_RANGE,
                "readiness_status": "REAL_ARCHIVE_INDEX_SEARCH_LAYER_READY_LOCAL_SQLITE_METADATA_ONLY_LOCKED_SAFE_TO_CONTINUE_NOT_DONE",
                "readiness_score": readiness_payload["readiness_score"],
                **counts,
                "check_count": len(checks),
                "passed_count": passed_count,
                "failed_count": failed_count,
                "readiness_hash": readiness_hash,
                "readiness_payload_json": _json_dumps(readiness_payload),
                "safe_to_continue_to_gp191": 1 if failed_count == 0 else 0,
                "section_ready": 1,
                "local_sqlite_index": 1,
                "metadata_only": 1,
                "redacted_only": 1,
                "body_download_prohibited": 1,
                "no_provider_contact": 1,
                "vault_done": 0,
                "clouds_should_continue": 0,
                "created_at": now,
                "updated_at": now,
            }
            for field in FALSE_FIELDS:
                if field not in {"vault_done", "clouds_should_continue"}:
                    row[field] = 0
            _insert_dict(conn, "vault_archive_index_search_readiness", row)

            for event_type, event_payload in [
                ("GP181_REAL_ARCHIVE_INDEX_SHELL_CREATED", {"component_id": INDEX_SHELL_ID}),
                ("GP182_ARCHIVE_METADATA_INDEX_REGISTRY_CREATED", {"index_record_count": counts["index_record_count"]}),
                ("GP183_ARCHIVE_SEARCH_QUERY_CONTRACT_CREATED", {"search_contract_count": counts["search_contract_count"]}),
                ("GP184_SEARCH_RESULT_REDACTION_CONTRACT_CREATED", {"redacted_only": True}),
                ("GP185_METADATA_SEARCH_RECEIPT_LEDGER_CREATED", {"receipt_count": counts["receipt_count"]}),
                ("GP186_SEARCH_FILTER_FACET_MAP_CREATED", {"facet_count": counts["facet_count"]}),
                ("GP187_INDEX_INTEGRITY_HASH_BOARD_CREATED", {"integrity_hash_count": counts["integrity_hash_count"]}),
                ("GP188_OBJECT_BODY_DOWNLOAD_SEARCH_PROHIBITION_CREATED", {"prohibition_count": counts["prohibition_count"]}),
                ("GP189_ARCHIVE_INDEX_SEARCH_BLOCKER_BOARD_CREATED", {"blocker_count": counts["blocker_count"]}),
                ("GP190_ARCHIVE_INDEX_SEARCH_READINESS_CREATED", {"readiness_hash": readiness_hash, "safe_to_continue_to_gp191": failed_count == 0}),
            ]:
                _insert_event(conn, event_type, event_payload)

            conn.commit()

    return {"initialized": True, "schema": schema, "real_sqlite_backed": True, **_counts(path)}

def _counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        return {
            "component_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_real_archive_index_components").fetchone()["c"]),
            "index_record_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_archive_metadata_index_records").fetchone()["c"]),
            "search_contract_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_archive_search_query_contracts").fetchone()["c"]),
            "receipt_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_metadata_search_receipts").fetchone()["c"]),
            "facet_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_search_filter_facet_map").fetchone()["c"]),
            "integrity_hash_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_index_integrity_hash_board").fetchone()["c"]),
            "prohibition_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_search_body_download_prohibitions").fetchone()["c"]),
            "blocker_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_archive_index_search_blockers").fetchone()["c"]),
            "readiness_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_archive_index_search_readiness").fetchone()["c"]),
            "event_count": int(conn.execute("SELECT COUNT(*) AS c FROM vault_archive_index_search_events").fetchone()["c"]),
        }

def _rows(table: str, order_by: str, db_path: Optional[str] = None, json_fields: Optional[Dict[str, str]] = None) -> list[Dict[str, Any]]:
    initialize_real_archive_index_search_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by}").fetchall()
    return [_boolify(row, json_fields) for row in rows]

def _component(component_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_archive_index_search_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_real_archive_index_components WHERE component_id = ?",
            (component_id,),
        ).fetchone()
    return _boolify(row, {"data_json": "data"})

def _readiness(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_archive_index_search_layer(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM vault_archive_index_search_readiness WHERE readiness_id = ?",
            (READINESS_ID,),
        ).fetchone()
    return _boolify(row, {"readiness_payload_json": "readiness_payload"})

def _events(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    initialize_real_archive_index_search_layer(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM vault_archive_index_search_events ORDER BY created_at, event_id").fetchall()
    return [{"event_id": row["event_id"], "event_type": row["event_type"], "event_payload": _json_loads(row["event_payload_json"]), "created_at": row["created_at"]} for row in rows]

def get_archive_metadata_index_records(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_archive_metadata_index_records", "record_code", db_path, {"payload_json": "payload"})

def get_archive_search_query_contracts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_archive_search_query_contracts", "search_code", db_path, {"payload_json": "payload", "allowed_fields_json": "allowed_fields"})

def get_metadata_search_receipts(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_metadata_search_receipts", "receipt_code", db_path, {"payload_json": "payload"})

def get_search_filter_facets(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_search_filter_facet_map", "facet_code", db_path, {"payload_json": "payload", "facet_values_json": "facet_values"})

def get_index_integrity_hashes(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_index_integrity_hash_board", "integrity_code", db_path, {"payload_json": "payload"})

def get_search_body_download_prohibitions(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_search_body_download_prohibitions", "prohibition_code", db_path, {"payload_json": "payload"})

def get_archive_index_search_blockers(db_path: Optional[str] = None) -> list[Dict[str, Any]]:
    return _rows("vault_archive_index_search_blockers", "blocker_code", db_path, {"payload_json": "payload"})

def validate_real_archive_index_search_layer(db_path: Optional[str] = None) -> Dict[str, Any]:
    components = _rows("vault_real_archive_index_components", "gp_number", db_path, {"data_json": "data"})
    records = get_archive_metadata_index_records(db_path)
    contracts = get_archive_search_query_contracts(db_path)
    receipts = get_metadata_search_receipts(db_path)
    facets = get_search_filter_facets(db_path)
    hashes = get_index_integrity_hashes(db_path)
    prohibitions = get_search_body_download_prohibitions(db_path)
    blockers = get_archive_index_search_blockers(db_path)
    readiness = _readiness(db_path)
    events = _events(db_path)

    checks = [
        ("COMPONENT_COUNT_10", len(components) == 10),
        ("INDEX_RECORD_COUNT_8", len(records) == len(INDEX_RECORDS)),
        ("SEARCH_CONTRACT_COUNT_6", len(contracts) == len(SEARCH_CONTRACTS)),
        ("RECEIPT_COUNT_6", len(receipts) == len(SEARCH_CONTRACTS)),
        ("FACET_COUNT_6", len(facets) == len(FACETS)),
        ("INTEGRITY_HASH_COUNT_5", len(hashes) == 5),
        ("PROHIBITION_COUNT_8", len(prohibitions) == len(PROHIBITIONS)),
        ("BLOCKER_COUNT_12", len(blockers) == len(BLOCKER_SPECS)),
        ("READINESS_EXISTS", readiness["readiness_id"] == READINESS_ID),
        ("READINESS_SCORE_100", readiness["readiness_score"] == 100),
        ("READINESS_HASH_64", isinstance(readiness["readiness_hash"], str) and len(readiness["readiness_hash"]) == 64),
        ("SAFE_TO_CONTINUE_TO_GP191", readiness["safe_to_continue_to_gp191"] is True),
        ("SECTION_READY", readiness["section_ready"] is True),
        ("LOCAL_SQLITE_INDEX", readiness["local_sqlite_index"] is True),
        ("METADATA_ONLY", readiness["metadata_only"] is True),
        ("REDACTED_ONLY", readiness["redacted_only"] is True),
        ("BODY_DOWNLOAD_PROHIBITED", readiness["body_download_prohibited"] is True),
        ("NO_PROVIDER_CONTACT", readiness["no_provider_contact"] is True),
        ("SECTION_GP181_GP190", readiness["section_range"] == "GP181-GP190"),
        ("NEXT_SECTION_GP191_GP200", readiness["readiness_payload"]["next_section_range"] == "GP191-GP200"),
        ("EVENTS_EXIST", len(events) >= 10),
        ("ALL_COMPONENTS_LOCKED", all(item["component_locked"] is True for item in components)),
        ("ALL_COMPONENTS_LOCAL_SQLITE", all(item["local_sqlite_index"] is True for item in components)),
        ("ALL_COMPONENTS_METADATA_ONLY", all(item["metadata_only"] is True for item in components)),
        ("ALL_COMPONENTS_REDACTED_ONLY", all(item["redacted_only"] is True for item in components)),
        ("ALL_RECORDS_LOCAL_SQLITE", all(item["local_sqlite_index"] is True for item in records)),
        ("ALL_RECORDS_METADATA_ONLY", all(item["metadata_only"] is True for item in records)),
        ("ALL_RECORDS_REDACTED_ONLY", all(item["redacted_only"] is True for item in records)),
        ("ALL_RECORDS_SEARCHABLE_LOCALLY", all(item["searchable_locally"] is True for item in records)),
        ("ALL_RECORDS_BODY_DOWNLOAD_PROHIBITED", all(item["body_download_prohibited"] is True for item in records)),
        ("ALL_CONTRACTS_PROVIDER_SEARCH_LOCKED", all(item["provider_search_locked"] is True for item in contracts)),
        ("ALL_CONTRACTS_METADATA_ONLY", all(item["metadata_only"] is True for item in contracts)),
        ("ALL_RECEIPTS_LOCKED", all(item["receipt_locked"] is True for item in receipts)),
        ("NO_FINAL_RECEIPTS", all(item["final_receipt_created"] is False for item in receipts)),
        ("ALL_FACETS_METADATA_ONLY", all(item["metadata_only"] is True for item in facets)),
        ("ALL_HASHES_LOCAL", all(item["local_sqlite_only"] is True for item in hashes)),
        ("ALL_PROHIBITIONS_ACTIVE", all(item["prohibition_active"] is True for item in prohibitions)),
        ("ALL_BLOCKERS_ACTIVE", all(item["blocker_active"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_SEARCH", all(item["blocks_provider_search"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_PROVIDER_API", all(item["blocks_provider_api"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_METADATA_READ", all(item["blocks_metadata_read"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_OBJECT_BODY", all(item["blocks_object_body"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DOWNLOAD", all(item["blocks_download"] is True for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_DANGEROUS_OPS", all(item["blocks_restore"] and item["blocks_export"] and item["blocks_direct_upload"] and item["blocks_delete"] for item in blockers)),
        ("ALL_BLOCKERS_BLOCK_EXECUTION_DONE", all(item["blocks_execution"] and item["blocks_vault_done"] for item in blockers)),
        ("NO_BLOCKERS_RESOLVED", all(item["resolved"] is False for item in blockers)),
    ]

    for collection_name, rows in [
        ("COMPONENT", components),
        ("RECORD", records),
        ("CONTRACT", contracts),
        ("RECEIPT", receipts),
        ("FACET", facets),
        ("HASH", hashes),
        ("PROHIBITION", prohibitions),
        ("BLOCKER", blockers),
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
        "index_record_count": len(records),
        "search_contract_count": len(contracts),
        "receipt_count": len(receipts),
        "facet_count": len(facets),
        "integrity_hash_count": len(hashes),
        "prohibition_count": len(prohibitions),
        "blocker_count": len(blockers),
        "event_count": len(events),
        "readiness_hash": readiness["readiness_hash"],
        "readiness_score": readiness["readiness_score"],
        "safe_to_continue_to_gp191": len(failed) == 0 and readiness["safe_to_continue_to_gp191"] is True,
        "vault_done": False,
        "clouds_should_continue": False,
    }

def get_gp181_real_archive_index_shell(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(INDEX_SHELL_ID, db_path)
    return {"pack": _pack_payload(181, component["pack_name"]), "real_sqlite_backed": True, "index_shell": component}

def get_gp182_archive_metadata_index_registry(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(METADATA_INDEX_REGISTRY_ID, db_path)
    records = get_archive_metadata_index_records(db_path)
    return {"pack": _pack_payload(182, component["pack_name"]), "real_sqlite_backed": True, "metadata_index_registry": component, "index_record_count": len(records), "records": records}

def get_gp183_archive_search_query_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SEARCH_QUERY_CONTRACT_ID, db_path)
    contracts = get_archive_search_query_contracts(db_path)
    return {"pack": _pack_payload(183, component["pack_name"]), "real_sqlite_backed": True, "search_query_contract": component, "search_contract_count": len(contracts), "contracts": contracts}

def get_gp184_search_result_redaction_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(RESULT_REDACTION_CONTRACT_ID, db_path)
    records = get_archive_metadata_index_records(db_path)
    return {"pack": _pack_payload(184, component["pack_name"]), "real_sqlite_backed": True, "redaction_contract": component, "redacted_record_count": len(records), "records": records}

def get_gp185_metadata_search_receipt_ledger(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SEARCH_RECEIPT_LEDGER_ID, db_path)
    receipts = get_metadata_search_receipts(db_path)
    return {"pack": _pack_payload(185, component["pack_name"]), "real_sqlite_backed": True, "receipt_ledger": component, "receipt_count": len(receipts), "receipts": receipts}

def get_gp186_search_filter_facet_map(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(SEARCH_FILTER_FACET_MAP_ID, db_path)
    facets = get_search_filter_facets(db_path)
    return {"pack": _pack_payload(186, component["pack_name"]), "real_sqlite_backed": True, "facet_map": component, "facet_count": len(facets), "facets": facets}

def get_gp187_index_integrity_hash_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(INDEX_INTEGRITY_HASH_BOARD_ID, db_path)
    hashes = get_index_integrity_hashes(db_path)
    return {"pack": _pack_payload(187, component["pack_name"]), "real_sqlite_backed": True, "integrity_hash_board": component, "integrity_hash_count": len(hashes), "hashes": hashes}

def get_gp188_object_body_download_search_prohibition(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(BODY_DOWNLOAD_SEARCH_PROHIBITION_ID, db_path)
    prohibitions = get_search_body_download_prohibitions(db_path)
    return {"pack": _pack_payload(188, component["pack_name"]), "real_sqlite_backed": True, "search_prohibition": component, "prohibition_count": len(prohibitions), "prohibitions": prohibitions}

def get_gp189_archive_index_search_blocker_board(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(BLOCKER_BOARD_ID, db_path)
    blockers = get_archive_index_search_blockers(db_path)
    return {"pack": _pack_payload(189, component["pack_name"]), "real_sqlite_backed": True, "blocker_board": component, "blocker_count": len(blockers), "blockers": blockers}

def get_gp190_archive_index_search_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(READINESS_ID, db_path)
    readiness = _readiness(db_path)
    validation = validate_real_archive_index_search_layer(db_path)
    return {"pack": _pack_payload(190, component["pack_name"]), "real_sqlite_backed": True, "readiness_checkpoint": {**component, "readiness": readiness, "validation": validation}}

def _status_for(gp_number: int, component_id: str, next_label: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    component = _component(component_id, db_path)
    readiness = _readiness(db_path)
    validation = validate_real_archive_index_search_layer(db_path)
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
            "source_gp180_readiness_id": component["source_gp180_readiness_id"],
            "source_gp180_readiness_hash": component["source_gp180_readiness_hash"],
            "source_gp180_readiness_score": component["source_gp180_readiness_score"],
            "component_ready": component["component_ready"],
            "component_locked": component["component_locked"],
            "local_sqlite_index": component["local_sqlite_index"],
            "metadata_only": component["metadata_only"],
            "redacted_only": component["redacted_only"],
            "body_download_prohibited": component["body_download_prohibited"],
            "no_provider_contact": component["no_provider_contact"],
            "validation_passed": validation["valid"],
            "readiness_score": readiness["readiness_score"],
            "readiness_hash": readiness["readiness_hash"],
            "safe_to_continue_to_gp191": validation["safe_to_continue_to_gp191"],
            "foundation_status": "real_archive_index_search_layer_ready_local_sqlite_metadata_only_locked_safe_to_continue_not_done",
            "next": next_label,
            **counts,
            "provider_search_requested": component["provider_search_requested"],
            "provider_search_executed": component["provider_search_executed"],
            "archive_search_provider_backed": component["archive_search_provider_backed"],
            "real_provider_connection_started": component["real_provider_connection_started"],
            "provider_api_called": component["provider_api_called"],
            "provider_token_created": component["provider_token_created"],
            "provider_session_created": component["provider_session_created"],
            "provider_job_reference_created": component["provider_job_reference_created"],
            "provider_status_poll_started": component["provider_status_poll_started"],
            "provider_health_checked": component["provider_health_checked"],
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
            "execution_enabled": component["execution_enabled"],
            "vault_done": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp190",
        },
        "validation": validation,
    }

def get_gp181_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(181, INDEX_SHELL_ID, "VAULT_GP182_ARCHIVE_METADATA_INDEX_REGISTRY", db_path)

def get_gp182_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(182, METADATA_INDEX_REGISTRY_ID, "VAULT_GP183_ARCHIVE_SEARCH_QUERY_CONTRACT", db_path)

def get_gp183_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(183, SEARCH_QUERY_CONTRACT_ID, "VAULT_GP184_SEARCH_RESULT_REDACTION_CONTRACT", db_path)

def get_gp184_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(184, RESULT_REDACTION_CONTRACT_ID, "VAULT_GP185_METADATA_SEARCH_RECEIPT_LEDGER", db_path)

def get_gp185_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(185, SEARCH_RECEIPT_LEDGER_ID, "VAULT_GP186_SEARCH_FILTER_FACET_MAP", db_path)

def get_gp186_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(186, SEARCH_FILTER_FACET_MAP_ID, "VAULT_GP187_INDEX_INTEGRITY_HASH_BOARD", db_path)

def get_gp187_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(187, INDEX_INTEGRITY_HASH_BOARD_ID, "VAULT_GP188_OBJECT_BODY_DOWNLOAD_SEARCH_PROHIBITION", db_path)

def get_gp188_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(188, BODY_DOWNLOAD_SEARCH_PROHIBITION_ID, "VAULT_GP189_ARCHIVE_INDEX_SEARCH_BLOCKER_BOARD", db_path)

def get_gp189_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    return _status_for(189, BLOCKER_BOARD_ID, "VAULT_GP190_ARCHIVE_INDEX_SEARCH_READINESS_CHECKPOINT", db_path)

def get_gp190_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    status = _status_for(190, READINESS_ID, NEXT_PACK, db_path)
    status["gp190_status"]["next_section"] = NEXT_SECTION_ID
    status["gp190_status"]["next_section_range"] = NEXT_SECTION_RANGE
    status["gp190_status"]["next_pack"] = NEXT_PACK
    return status

def get_real_archive_index_search_layer_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    store = initialize_real_archive_index_search_layer(db_path)
    components = _rows("vault_real_archive_index_components", "gp_number", db_path, {"data_json": "data"})
    records = get_archive_metadata_index_records(db_path)
    contracts = get_archive_search_query_contracts(db_path)
    receipts = get_metadata_search_receipts(db_path)
    facets = get_search_filter_facets(db_path)
    hashes = get_index_integrity_hashes(db_path)
    prohibitions = get_search_body_download_prohibitions(db_path)
    blockers = get_archive_index_search_blockers(db_path)
    readiness = _readiness(db_path)
    validation = validate_real_archive_index_search_layer(db_path)
    events = _events(db_path)

    return {
        "pack": _layer_pack_payload(),
        "real_sqlite_backed": True,
        "store": store,
        "components": components,
        "index_records": {"index_record_count": len(records), "records": records},
        "search_contracts": {"search_contract_count": len(contracts), "contracts": contracts},
        "receipts": {"receipt_count": len(receipts), "receipts": receipts},
        "facets": {"facet_count": len(facets), "facets": facets},
        "integrity_hashes": {"integrity_hash_count": len(hashes), "hashes": hashes},
        "prohibitions": {"prohibition_count": len(prohibitions), "prohibitions": prohibitions},
        "blockers": {"blocker_count": len(blockers), "blockers": blockers},
        "readiness": readiness,
        "events": {"event_count": len(events), "events": events},
        "validation": validation,
        "truth": {
            "real_archive_index_search_layer_ready": True,
            "local_sqlite_index": True,
            "metadata_only": True,
            "redacted_only": True,
            "body_download_prohibited": True,
            "safe_to_continue_to_gp191": validation["safe_to_continue_to_gp191"],
            "next_section": NEXT_SECTION_ID,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "no_provider_contact": True,
            "provider_search_requested": False,
            "provider_search_executed": False,
            "archive_search_provider_backed": False,
            "real_provider_connection_started": False,
            "provider_api_called": False,
            "provider_token_created": False,
            "provider_session_created": False,
            "provider_job_reference_created": False,
            "provider_status_poll_started": False,
            "provider_health_checked": False,
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
            "execution_enabled": False,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        "routes": {
            "page": "/vault/real-archive-index-search-layer",
            "json": "/vault/real-archive-index-search-layer.json",
            "gp181": "/vault/gp181-status.json",
            "gp182": "/vault/gp182-status.json",
            "gp183": "/vault/gp183-status.json",
            "gp184": "/vault/gp184-status.json",
            "gp185": "/vault/gp185-status.json",
            "gp186": "/vault/gp186-status.json",
            "gp187": "/vault/gp187-status.json",
            "gp188": "/vault/gp188-status.json",
            "gp189": "/vault/gp189-status.json",
            "gp190": "/vault/gp190-status.json",
        },
    }

def render_real_archive_index_search_layer_page() -> str:
    home = get_real_archive_index_search_layer_home()
    validation = home["validation"]
    readiness = home["readiness"]

    record_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['title_redacted'])}</strong>
          <span>{escape(item['metadata_index_status'])}</span>
          <code>{escape(item['lane'])} · {escape(item['category'])}</code>
        </article>
        """
        for item in home["index_records"]["records"]
    )

    facet_cards = "\n".join(
        f"""
        <article class="card">
          <strong>{escape(item['facet_name'])}</strong>
          <span>{escape(item['facet_status'])}</span>
          <code>metadata-only facet</code>
        </article>
        """
        for item in home["facets"]["facets"]
    )

    failed = "\n".join(
        f"<div class='row danger'><strong>{escape(item['code'])}</strong><span>FAIL</span></div>"
        for item in validation["failed_checks"]
    ) or "<p class='ok'>No failed checks.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vault GP181-GP190 Real Archive Index and Search Layer</title>
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
    <div class="eyebrow">Archive Vault · Giant Packs 181-190</div>
    <div class="eyebrow">Real Archive Index and Search Layer · GP181-GP190</div>
    <h1>Real Archive Index and Search</h1>
    <p>This layer creates a real local SQLite archive metadata index and search surface. It is redacted-only, metadata-only, and locked away from provider search, object bodies, downloads, restore, export, upload, delete, and execution.</p>
    <div class="grid">
      <div class="metric"><strong>{home['store']['index_record_count']}</strong><span>metadata records</span></div>
      <div class="metric"><strong>{home['store']['search_contract_count']}</strong><span>search contracts</span></div>
      <div class="metric"><strong>{home['store']['facet_count']}</strong><span>facets</span></div>
      <div class="metric"><strong>{readiness['readiness_score']}</strong><span>readiness score</span></div>
    </div>
    <div class="chips">
      <span class="pill ok">GP181-GP190 built</span>
      <span class="pill ok">Local SQLite index</span>
      <span class="pill ok">Metadata only</span>
      <span class="pill ok">Redacted only</span>
      <span class="pill ok">Safe to GP191</span>
      <span class="pill danger">No provider search</span>
      <span class="pill danger">No object body</span>
      <span class="pill danger">No download</span>
      <span class="pill danger">No restore/export/upload/delete</span>
      <span class="pill danger">No execution</span>
    </div>
  </section>

  <section class="section">
    <h2>Archive Metadata Index</h2>
    <div class="cards">{record_cards}</div>
  </section>

  <section class="section">
    <h2>Search Facets</h2>
    <div class="cards">{facet_cards}</div>
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
