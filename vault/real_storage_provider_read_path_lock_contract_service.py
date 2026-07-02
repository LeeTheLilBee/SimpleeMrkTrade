"""
VAULT GIANT PACK 068 — Real Storage Provider Read Path Lock Contract

CURRENT SECTION:
Archive Vault — Real Storage Provider Configuration Layer
GP061-GP070

This pack creates a real durable read-path lock contract from the GP067
write-path lock contract without configuring or enabling any provider read path.

Purpose:
- Create a real SQLite-backed read-path lock contract schema.
- Persist a real contract record sourced from GP067.
- Persist real read-path requirement rows per provider candidate.
- Persist real read-path policy rows.
- Carry forward real blockers from GP067.
- Persist a real event log.
- Validate that no provider read path, object listing, object body read,
  object body view, direct upload, export, or execution is enabled.

Important truth:
- GP068 creates the contract that keeps provider read paths locked.
- GP068 does not configure read path, object listing, or object body read.
- GP068 does not enable provider read or provider write.
- GP068 does not configure credentials, endpoint, namespace, or encryption.
- GP068 does not approve, activate, select, configure, read, write, export, or execute.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Dict, Optional

from vault.real_storage_provider_write_path_lock_contract_service import (
    DEFAULT_WRITE_PATH_LOCK_CONTRACT_ID,
    get_storage_provider_write_path_blockers,
    get_storage_provider_write_path_lock_contract_record,
    get_storage_provider_write_path_requirements,
)


PACK_ID = "VAULT_GP068"
PACK_NAME = "Real Storage Provider Read Path Lock Contract"
SCHEMA_VERSION = "vault.real_storage_provider_read_path_lock_contract.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
SECTION_TITLE = "Archive Vault — Real Storage Provider Configuration Layer"
SECTION_RANGE = "GP061-GP070"

NEXT_PACK = "VAULT_GP069_REAL_STORAGE_PROVIDER_OBJECT_BODY_VIEW_LOCK_CONTRACT"
NEXT_PACK_TITLE = "Real Storage Provider Object Body View Lock Contract"

DEFAULT_READ_PATH_LOCK_CONTRACT_ID = "VSPRPLC-GP068-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_read_path_lock_contract.sqlite"


READ_PATH_REQUIREMENT_SPECS = [
    {
        "requirement_code": "read_path_lock_record_required",
        "requirement_name": "Read path lock record required",
        "requirement_category": "read_path_lock",
        "requirement_message": "A durable lock record must exist before provider read paths can ever be considered.",
    },
    {
        "requirement_code": "tower_read_unlock_required",
        "requirement_name": "Tower read unlock required",
        "requirement_category": "tower_gate",
        "requirement_message": "Tower must explicitly unlock a later read step before any provider read path.",
    },
    {
        "requirement_code": "owner_read_review_required",
        "requirement_name": "Owner read review required",
        "requirement_category": "owner_review",
        "requirement_message": "Owner review must occur before any provider read path can be configured.",
    },
    {
        "requirement_code": "write_path_precondition_required",
        "requirement_name": "Write path precondition required",
        "requirement_category": "write_precondition",
        "requirement_message": "Provider write paths remain locked and cannot imply read enablement in GP068.",
    },
    {
        "requirement_code": "read_receipt_precondition_required",
        "requirement_name": "Read receipt precondition required",
        "requirement_category": "receipt_precondition",
        "requirement_message": "A future read path must require its own receipt layer; GP068 does not create that receipt.",
    },
    {
        "requirement_code": "object_listing_lock_required",
        "requirement_name": "Object listing lock required",
        "requirement_category": "object_listing_lock",
        "requirement_message": "Provider object listing must remain locked through GP068.",
    },
    {
        "requirement_code": "object_body_read_lock_required",
        "requirement_name": "Object body read lock required",
        "requirement_category": "object_body_lock",
        "requirement_message": "Provider object body reading must remain locked through GP068.",
    },
    {
        "requirement_code": "read_write_separation_required",
        "requirement_name": "Read/write separation required",
        "requirement_category": "read_write_boundary",
        "requirement_message": "Read lock must not imply write unlock; both read and write remain locked.",
    },
]


READ_PATH_POLICIES = [
    {
        "policy_code": "no_read_path_configuration",
        "policy_name": "No read path configuration",
        "policy_category": "read_lock",
        "policy_message": "This contract cannot configure provider read paths.",
    },
    {
        "policy_code": "no_read_attempt",
        "policy_name": "No read attempt",
        "policy_category": "read_lock",
        "policy_message": "This contract cannot attempt provider reads.",
    },
    {
        "policy_code": "no_read_success_claim",
        "policy_name": "No read success claim",
        "policy_category": "truth_lock",
        "policy_message": "This contract cannot claim provider read success.",
    },
    {
        "policy_code": "no_object_listing",
        "policy_name": "No object listing",
        "policy_category": "object_listing_lock",
        "policy_message": "This contract cannot list provider objects.",
    },
    {
        "policy_code": "no_object_body_read",
        "policy_name": "No object body read",
        "policy_category": "object_body_lock",
        "policy_message": "This contract cannot read provider object bodies.",
    },
    {
        "policy_code": "tower_read_review_required",
        "policy_name": "Tower read review required",
        "policy_category": "tower_gate",
        "policy_message": "Tower review is required before read path configuration can be considered later.",
    },
    {
        "policy_code": "owner_redacted_read_view_only",
        "policy_name": "Owner redacted read view only",
        "policy_category": "redaction",
        "policy_message": "Owner-facing read-path views must remain redacted and non-operational.",
    },
    {
        "policy_code": "no_write_unlock_from_read_contract",
        "policy_name": "No write unlock from read contract",
        "policy_category": "write_lock",
        "policy_message": "This contract cannot enable provider write.",
    },
    {
        "policy_code": "no_export_from_read_contract",
        "policy_name": "No export from read contract",
        "policy_category": "export_lock",
        "policy_message": "This contract cannot unlock external delivery or export.",
    },
    {
        "policy_code": "no_execution_from_read_contract",
        "policy_name": "No execution from read contract",
        "policy_category": "execution_lock",
        "policy_message": "This contract cannot unlock execution.",
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_db_path(db_path: Optional[str] = None) -> Path:
    chosen = db_path or os.environ.get(DEFAULT_DB_ENV) or DEFAULT_DB_PATH
    return Path(chosen)


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _json_loads(value: str) -> Any:
    return json.loads(value)


def _connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = _resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _insert_dict(conn: sqlite3.Connection, table: str, payload: Dict[str, Any]) -> None:
    columns = list(payload.keys())
    placeholders = ", ".join(["?"] * len(columns))
    column_sql = ", ".join(columns)
    conn.execute(
        f"INSERT INTO {table} ({column_sql}) VALUES ({placeholders})",
        tuple(payload[column] for column in columns),
    )


def ensure_storage_provider_read_path_lock_contract_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_read_path_lock_contracts (
                read_path_lock_contract_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_write_path_lock_contract_id TEXT NOT NULL,
                source_write_path_pack_id TEXT NOT NULL,
                contract_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                contract_data_json TEXT NOT NULL,
                read_path_lock_contract_ready INTEGER NOT NULL DEFAULT 1,
                read_path_requirements_ready INTEGER NOT NULL DEFAULT 1,
                read_path_policy_ready INTEGER NOT NULL DEFAULT 1,
                read_path_locked INTEGER NOT NULL DEFAULT 1,
                read_path_alias_only INTEGER NOT NULL DEFAULT 1,
                read_path_configured INTEGER NOT NULL DEFAULT 0,
                read_path_attempted INTEGER NOT NULL DEFAULT 0,
                read_path_enabled INTEGER NOT NULL DEFAULT 0,
                read_receipt_created INTEGER NOT NULL DEFAULT 0,
                object_listing_configured INTEGER NOT NULL DEFAULT 0,
                object_list_attempted INTEGER NOT NULL DEFAULT 0,
                object_listed INTEGER NOT NULL DEFAULT 0,
                object_body_read_attempted INTEGER NOT NULL DEFAULT 0,
                object_body_read INTEGER NOT NULL DEFAULT 0,
                object_body_view_enabled INTEGER NOT NULL DEFAULT 0,
                actual_secret_values_stored INTEGER NOT NULL DEFAULT 0,
                secret_values_present INTEGER NOT NULL DEFAULT 0,
                token_material_present INTEGER NOT NULL DEFAULT 0,
                encrypted_secret_payload_present INTEGER NOT NULL DEFAULT 0,
                key_material_stored INTEGER NOT NULL DEFAULT 0,
                kms_key_id_stored INTEGER NOT NULL DEFAULT 0,
                key_locator_present INTEGER NOT NULL DEFAULT 0,
                encryption_policy_configured INTEGER NOT NULL DEFAULT 0,
                secret_references_created INTEGER NOT NULL DEFAULT 0,
                secret_references_activated INTEGER NOT NULL DEFAULT 0,
                credentials_configured INTEGER NOT NULL DEFAULT 0,
                provider_endpoint_configured INTEGER NOT NULL DEFAULT 0,
                storage_container_configured INTEGER NOT NULL DEFAULT 0,
                namespace_configured INTEGER NOT NULL DEFAULT 0,
                connection_probe_configured INTEGER NOT NULL DEFAULT 0,
                connection_test_attempted INTEGER NOT NULL DEFAULT 0,
                provider_connection_tested INTEGER NOT NULL DEFAULT 0,
                write_path_configured INTEGER NOT NULL DEFAULT 0,
                write_path_attempted INTEGER NOT NULL DEFAULT 0,
                upload_path_configured INTEGER NOT NULL DEFAULT 0,
                object_create_attempted INTEGER NOT NULL DEFAULT 0,
                object_created INTEGER NOT NULL DEFAULT 0,
                provider_approval_ready INTEGER NOT NULL DEFAULT 0,
                provider_activation_ready INTEGER NOT NULL DEFAULT 0,
                provider_configuration_ready INTEGER NOT NULL DEFAULT 0,
                provider_read_write_ready INTEGER NOT NULL DEFAULT 0,
                provider_approved INTEGER NOT NULL DEFAULT 0,
                provider_activated INTEGER NOT NULL DEFAULT 0,
                provider_recommended INTEGER NOT NULL DEFAULT 0,
                provider_selected INTEGER NOT NULL DEFAULT 0,
                provider_configured INTEGER NOT NULL DEFAULT 0,
                provider_read_enabled INTEGER NOT NULL DEFAULT 0,
                provider_write_enabled INTEGER NOT NULL DEFAULT 0,
                provider_object_read_claimed INTEGER NOT NULL DEFAULT 0,
                provider_object_write_claimed INTEGER NOT NULL DEFAULT 0,
                risk_accepted INTEGER NOT NULL DEFAULT 0,
                risk_waived INTEGER NOT NULL DEFAULT 0,
                mitigation_approved INTEGER NOT NULL DEFAULT 0,
                official_storage_receipt INTEGER NOT NULL DEFAULT 0,
                finalized_storage_receipt INTEGER NOT NULL DEFAULT 0,
                closed_storage_receipt INTEGER NOT NULL DEFAULT 0,
                direct_upload_enabled INTEGER NOT NULL DEFAULT 0,
                export_enabled INTEGER NOT NULL DEFAULT 0,
                execution_enabled INTEGER NOT NULL DEFAULT 0,
                vault_done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_read_path_requirements (
                read_path_requirement_id TEXT PRIMARY KEY,
                read_path_lock_contract_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                requirement_code TEXT NOT NULL,
                requirement_name TEXT NOT NULL,
                requirement_category TEXT NOT NULL,
                requirement_message TEXT NOT NULL,
                requirement_status TEXT NOT NULL,
                requirement_required INTEGER NOT NULL DEFAULT 1,
                requirement_verified INTEGER NOT NULL DEFAULT 0,
                read_path_locked INTEGER NOT NULL DEFAULT 1,
                read_path_alias_only INTEGER NOT NULL DEFAULT 1,
                read_path_configured INTEGER NOT NULL DEFAULT 0,
                read_path_attempted INTEGER NOT NULL DEFAULT 0,
                read_path_enabled INTEGER NOT NULL DEFAULT 0,
                read_receipt_created INTEGER NOT NULL DEFAULT 0,
                object_listing_configured INTEGER NOT NULL DEFAULT 0,
                object_list_attempted INTEGER NOT NULL DEFAULT 0,
                object_listed INTEGER NOT NULL DEFAULT 0,
                object_body_read_attempted INTEGER NOT NULL DEFAULT 0,
                object_body_read INTEGER NOT NULL DEFAULT 0,
                object_body_view_enabled INTEGER NOT NULL DEFAULT 0,
                credentials_configured INTEGER NOT NULL DEFAULT 0,
                secret_references_activated INTEGER NOT NULL DEFAULT 0,
                provider_endpoint_configured INTEGER NOT NULL DEFAULT 0,
                storage_container_configured INTEGER NOT NULL DEFAULT 0,
                namespace_configured INTEGER NOT NULL DEFAULT 0,
                encryption_policy_configured INTEGER NOT NULL DEFAULT 0,
                provider_connection_tested INTEGER NOT NULL DEFAULT 0,
                write_path_configured INTEGER NOT NULL DEFAULT 0,
                write_path_attempted INTEGER NOT NULL DEFAULT 0,
                object_created INTEGER NOT NULL DEFAULT 0,
                provider_read_enabled INTEGER NOT NULL DEFAULT 0,
                provider_write_enabled INTEGER NOT NULL DEFAULT 0,
                direct_upload_enabled INTEGER NOT NULL DEFAULT 0,
                export_enabled INTEGER NOT NULL DEFAULT 0,
                execution_enabled INTEGER NOT NULL DEFAULT 0,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_granted INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(read_path_lock_contract_id)
                    REFERENCES vault_storage_provider_read_path_lock_contracts(read_path_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(read_path_lock_contract_id, provider_candidate_id, requirement_code)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_read_path_policies (
                read_path_policy_id TEXT PRIMARY KEY,
                read_path_lock_contract_id TEXT NOT NULL,
                policy_code TEXT NOT NULL,
                policy_name TEXT NOT NULL,
                policy_category TEXT NOT NULL,
                policy_message TEXT NOT NULL,
                policy_status TEXT NOT NULL,
                policy_required INTEGER NOT NULL DEFAULT 1,
                policy_verified INTEGER NOT NULL DEFAULT 0,
                read_path_configured INTEGER NOT NULL DEFAULT 0,
                read_path_attempted INTEGER NOT NULL DEFAULT 0,
                read_path_enabled INTEGER NOT NULL DEFAULT 0,
                read_receipt_created INTEGER NOT NULL DEFAULT 0,
                object_listing_configured INTEGER NOT NULL DEFAULT 0,
                object_list_attempted INTEGER NOT NULL DEFAULT 0,
                object_listed INTEGER NOT NULL DEFAULT 0,
                object_body_read_attempted INTEGER NOT NULL DEFAULT 0,
                object_body_read INTEGER NOT NULL DEFAULT 0,
                object_body_view_enabled INTEGER NOT NULL DEFAULT 0,
                actual_secret_values_stored INTEGER NOT NULL DEFAULT 0,
                secret_values_present INTEGER NOT NULL DEFAULT 0,
                token_material_present INTEGER NOT NULL DEFAULT 0,
                secret_references_created INTEGER NOT NULL DEFAULT 0,
                secret_references_activated INTEGER NOT NULL DEFAULT 0,
                credentials_configured INTEGER NOT NULL DEFAULT 0,
                provider_read_enabled INTEGER NOT NULL DEFAULT 0,
                provider_write_enabled INTEGER NOT NULL DEFAULT 0,
                direct_upload_enabled INTEGER NOT NULL DEFAULT 0,
                export_enabled INTEGER NOT NULL DEFAULT 0,
                execution_enabled INTEGER NOT NULL DEFAULT 0,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_granted INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(read_path_lock_contract_id)
                    REFERENCES vault_storage_provider_read_path_lock_contracts(read_path_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(read_path_lock_contract_id, policy_code)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_read_path_blockers (
                read_path_blocker_id TEXT PRIMARY KEY,
                read_path_lock_contract_id TEXT NOT NULL,
                source_write_path_blocker_id TEXT NOT NULL,
                source_connection_test_blocker_id TEXT NOT NULL,
                source_encryption_blocker_id TEXT NOT NULL,
                source_endpoint_namespace_blocker_id TEXT NOT NULL,
                source_ledger_blocker_id TEXT NOT NULL,
                source_credential_blocker_id TEXT NOT NULL,
                source_config_blocker_id TEXT NOT NULL,
                source_readiness_blocker_id TEXT NOT NULL,
                source_receipt_line_id TEXT NOT NULL,
                source_finding_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                blocker_code TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocks_provider_approval INTEGER NOT NULL DEFAULT 1,
                blocks_provider_activation INTEGER NOT NULL DEFAULT 1,
                blocks_provider_selection INTEGER NOT NULL DEFAULT 1,
                blocks_provider_configuration INTEGER NOT NULL DEFAULT 1,
                blocks_provider_read_write INTEGER NOT NULL DEFAULT 1,
                blocks_object_body_view INTEGER NOT NULL DEFAULT 1,
                blocks_export INTEGER NOT NULL DEFAULT 1,
                blocks_execution INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_granted INTEGER NOT NULL DEFAULT 0,
                risk_accepted INTEGER NOT NULL DEFAULT 0,
                risk_waived INTEGER NOT NULL DEFAULT 0,
                mitigation_approved INTEGER NOT NULL DEFAULT 0,
                resolved INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(read_path_lock_contract_id)
                    REFERENCES vault_storage_provider_read_path_lock_contracts(read_path_lock_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(read_path_lock_contract_id, source_write_path_blocker_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_read_path_events (
                event_id TEXT PRIMARY KEY,
                read_path_lock_contract_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(read_path_lock_contract_id)
                    REFERENCES vault_storage_provider_read_path_lock_contracts(read_path_lock_contract_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_read_path_requirements_contract
            ON vault_storage_provider_read_path_requirements(read_path_lock_contract_id, provider_candidate_id, requirement_category)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_read_path_blockers_contract
            ON vault_storage_provider_read_path_blockers(read_path_lock_contract_id, provider_candidate_id, blocker_category)
            """
        )
        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "tables": [
            "vault_storage_provider_read_path_lock_contracts",
            "vault_storage_provider_read_path_requirements",
            "vault_storage_provider_read_path_policies",
            "vault_storage_provider_read_path_blockers",
            "vault_storage_provider_read_path_events",
        ],
        "real_sqlite_backed": True,
    }


def initialize_real_storage_provider_read_path_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_read_path_lock_contract_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            """
            SELECT read_path_lock_contract_id
            FROM vault_storage_provider_read_path_lock_contracts
            WHERE read_path_lock_contract_id = ?
            """,
            (DEFAULT_READ_PATH_LOCK_CONTRACT_ID,),
        ).fetchone()

        if existing is None:
            source_contract = get_storage_provider_write_path_lock_contract_record()["write_path_lock_contract"]
            source_requirements_payload = get_storage_provider_write_path_requirements()
            blockers_payload = get_storage_provider_write_path_blockers()
            source_requirements = source_requirements_payload["requirements"]
            blockers = blockers_payload["blockers"]
            candidates = _unique_provider_candidates(source_requirements)
            contract_data = _build_contract_data(source_contract, source_requirements_payload, blockers_payload, candidates)
            now = _now_iso()

            _insert_dict(
                conn,
                "vault_storage_provider_read_path_lock_contracts",
                {
                    "read_path_lock_contract_id": DEFAULT_READ_PATH_LOCK_CONTRACT_ID,
                    "pack_id": PACK_ID,
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    "source_write_path_lock_contract_id": source_contract["write_path_lock_contract_id"],
                    "source_write_path_pack_id": source_contract["pack_id"],
                    "contract_status": "REAL_READ_PATH_LOCK_CONTRACT_OPEN_TOWER_LOCKED",
                    "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    "contract_data_json": _json_dumps(contract_data),
                    "read_path_lock_contract_ready": 1,
                    "read_path_requirements_ready": 1,
                    "read_path_policy_ready": 1,
                    "read_path_locked": 1,
                    "read_path_alias_only": 1,
                    "read_path_configured": 0,
                    "read_path_attempted": 0,
                    "read_path_enabled": 0,
                    "read_receipt_created": 0,
                    "object_listing_configured": 0,
                    "object_list_attempted": 0,
                    "object_listed": 0,
                    "object_body_read_attempted": 0,
                    "object_body_read": 0,
                    "object_body_view_enabled": 0,
                    "actual_secret_values_stored": 0,
                    "secret_values_present": 0,
                    "token_material_present": 0,
                    "encrypted_secret_payload_present": 0,
                    "key_material_stored": 0,
                    "kms_key_id_stored": 0,
                    "key_locator_present": 0,
                    "encryption_policy_configured": 0,
                    "secret_references_created": 0,
                    "secret_references_activated": 0,
                    "credentials_configured": 0,
                    "provider_endpoint_configured": 0,
                    "storage_container_configured": 0,
                    "namespace_configured": 0,
                    "connection_probe_configured": 0,
                    "connection_test_attempted": 0,
                    "provider_connection_tested": 0,
                    "write_path_configured": 0,
                    "write_path_attempted": 0,
                    "upload_path_configured": 0,
                    "object_create_attempted": 0,
                    "object_created": 0,
                    "provider_approval_ready": 0,
                    "provider_activation_ready": 0,
                    "provider_configuration_ready": 0,
                    "provider_read_write_ready": 0,
                    "provider_approved": 0,
                    "provider_activated": 0,
                    "provider_recommended": 0,
                    "provider_selected": 0,
                    "provider_configured": 0,
                    "provider_read_enabled": 0,
                    "provider_write_enabled": 0,
                    "provider_object_read_claimed": 0,
                    "provider_object_write_claimed": 0,
                    "risk_accepted": 0,
                    "risk_waived": 0,
                    "mitigation_approved": 0,
                    "official_storage_receipt": 0,
                    "finalized_storage_receipt": 0,
                    "closed_storage_receipt": 0,
                    "direct_upload_enabled": 0,
                    "export_enabled": 0,
                    "execution_enabled": 0,
                    "vault_done": 0,
                    "created_at": now,
                    "updated_at": now,
                },
            )

            for candidate in candidates:
                for requirement in READ_PATH_REQUIREMENT_SPECS:
                    _insert_requirement(conn, DEFAULT_READ_PATH_LOCK_CONTRACT_ID, candidate, requirement, now)

            for policy in READ_PATH_POLICIES:
                _insert_policy(conn, DEFAULT_READ_PATH_LOCK_CONTRACT_ID, policy, now)

            for blocker in blockers:
                _insert_blocker(conn, DEFAULT_READ_PATH_LOCK_CONTRACT_ID, blocker, now)

            _insert_event(
                conn,
                DEFAULT_READ_PATH_LOCK_CONTRACT_ID,
                "REAL_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT_CREATED",
                {
                    "pack_id": PACK_ID,
                    "source_write_path_lock_contract_id": source_contract["write_path_lock_contract_id"],
                    "source_write_path_pack_id": source_contract["pack_id"],
                    "real_sqlite_backed": True,
                    "read_path_lock_contract_ready": True,
                    "read_path_locked": True,
                    "read_path_configured": False,
                    "read_path_attempted": False,
                    "read_path_enabled": False,
                    "object_body_read": False,
                    "provider_read_enabled": False,
                    "vault_done": False,
                },
            )
            _insert_event(
                conn,
                DEFAULT_READ_PATH_LOCK_CONTRACT_ID,
                "SOURCE_GP067_WRITE_PATH_LOCK_CONTRACT_ATTACHED",
                _compact_source_snapshot(source_contract, source_requirements_payload, blockers_payload),
            )
            _insert_event(
                conn,
                DEFAULT_READ_PATH_LOCK_CONTRACT_ID,
                "REAL_READ_PATH_REQUIREMENTS_CREATED_LOCKED",
                _get_requirement_counts(conn, DEFAULT_READ_PATH_LOCK_CONTRACT_ID),
            )
            _insert_event(
                conn,
                DEFAULT_READ_PATH_LOCK_CONTRACT_ID,
                "REAL_READ_PATH_POLICIES_CREATED",
                _get_policy_counts(conn, DEFAULT_READ_PATH_LOCK_CONTRACT_ID),
            )
            _insert_event(
                conn,
                DEFAULT_READ_PATH_LOCK_CONTRACT_ID,
                "REAL_READ_PATH_BLOCKERS_CARRIED_FORWARD",
                _get_blocker_counts(conn, DEFAULT_READ_PATH_LOCK_CONTRACT_ID),
            )
            _insert_event(
                conn,
                DEFAULT_READ_PATH_LOCK_CONTRACT_ID,
                "READ_PATH_LOCKS_CONFIRMED",
                {
                    "no_read_path_configured": True,
                    "no_read_path_attempted": True,
                    "no_read_path_enabled": True,
                    "no_read_receipt_created": True,
                    "no_object_listing_configured": True,
                    "no_object_list_attempted": True,
                    "no_object_listed": True,
                    "no_object_body_read_attempted": True,
                    "no_object_body_read": True,
                    "no_object_body_view": True,
                    "provider_read_write_blocked": True,
                    "direct_upload_blocked": True,
                    "export_blocked": True,
                    "execution_blocked": True,
                },
            )
            conn.commit()

    counts = _get_counts(path)
    return {
        "initialized": True,
        "schema": schema,
        "read_path_lock_contract_id": DEFAULT_READ_PATH_LOCK_CONTRACT_ID,
        "contract_count": counts["contract_count"],
        "requirement_count": counts["requirement_count"],
        "policy_count": counts["policy_count"],
        "blocker_count": counts["blocker_count"],
        "event_count": counts["event_count"],
        "real_sqlite_backed": True,
    }


def _unique_provider_candidates(requirements: list[Dict[str, Any]]) -> list[Dict[str, str]]:
    seen = {}
    for requirement in requirements:
        provider_candidate_id = requirement["provider_candidate_id"]
        if provider_candidate_id not in seen:
            seen[provider_candidate_id] = {"provider_candidate_id": provider_candidate_id}
    return [seen[key] for key in sorted(seen.keys())]


def _insert_requirement(conn, contract_id: str, candidate: Dict[str, str], requirement: Dict[str, str], now: str) -> str:
    requirement_id = (
        f"VSPRPR-{candidate['provider_candidate_id'].replace('VSPC-', '')}-"
        f"{requirement['requirement_code'].upper().replace('_', '-')}"
    )
    _insert_dict(
        conn,
        "vault_storage_provider_read_path_requirements",
        {
            "read_path_requirement_id": requirement_id,
            "read_path_lock_contract_id": contract_id,
            "provider_candidate_id": candidate["provider_candidate_id"],
            "requirement_code": requirement["requirement_code"],
            "requirement_name": requirement["requirement_name"],
            "requirement_category": requirement["requirement_category"],
            "requirement_message": requirement["requirement_message"],
            "requirement_status": "REAL_READ_PATH_REQUIREMENT_RECORDED_LOCKED_TOWER_LOCKED",
            "requirement_required": 1,
            "requirement_verified": 0,
            "read_path_locked": 1,
            "read_path_alias_only": 1,
            "read_path_configured": 0,
            "read_path_attempted": 0,
            "read_path_enabled": 0,
            "read_receipt_created": 0,
            "object_listing_configured": 0,
            "object_list_attempted": 0,
            "object_listed": 0,
            "object_body_read_attempted": 0,
            "object_body_read": 0,
            "object_body_view_enabled": 0,
            "credentials_configured": 0,
            "secret_references_activated": 0,
            "provider_endpoint_configured": 0,
            "storage_container_configured": 0,
            "namespace_configured": 0,
            "encryption_policy_configured": 0,
            "provider_connection_tested": 0,
            "write_path_configured": 0,
            "write_path_attempted": 0,
            "object_created": 0,
            "provider_read_enabled": 0,
            "provider_write_enabled": 0,
            "direct_upload_enabled": 0,
            "export_enabled": 0,
            "execution_enabled": 0,
            "tower_review_required": 1,
            "tower_review_granted": 0,
            "created_at": now,
            "updated_at": now,
        },
    )
    return requirement_id


def _insert_policy(conn, contract_id: str, policy: Dict[str, str], now: str) -> str:
    policy_id = f"VSPRPP-{policy['policy_code'].upper().replace('_', '-')}"
    _insert_dict(
        conn,
        "vault_storage_provider_read_path_policies",
        {
            "read_path_policy_id": policy_id,
            "read_path_lock_contract_id": contract_id,
            "policy_code": policy["policy_code"],
            "policy_name": policy["policy_name"],
            "policy_category": policy["policy_category"],
            "policy_message": policy["policy_message"],
            "policy_status": "REAL_READ_PATH_POLICY_RECORDED_TOWER_LOCKED",
            "policy_required": 1,
            "policy_verified": 0,
            "read_path_configured": 0,
            "read_path_attempted": 0,
            "read_path_enabled": 0,
            "read_receipt_created": 0,
            "object_listing_configured": 0,
            "object_list_attempted": 0,
            "object_listed": 0,
            "object_body_read_attempted": 0,
            "object_body_read": 0,
            "object_body_view_enabled": 0,
            "actual_secret_values_stored": 0,
            "secret_values_present": 0,
            "token_material_present": 0,
            "secret_references_created": 0,
            "secret_references_activated": 0,
            "credentials_configured": 0,
            "provider_read_enabled": 0,
            "provider_write_enabled": 0,
            "direct_upload_enabled": 0,
            "export_enabled": 0,
            "execution_enabled": 0,
            "tower_review_required": 1,
            "tower_review_granted": 0,
            "created_at": now,
            "updated_at": now,
        },
    )
    return policy_id


def _insert_blocker(conn, contract_id: str, blocker: Dict[str, Any], now: str) -> str:
    blocker_id = f"VSPRPB-{blocker['write_path_blocker_id'].replace('VSPWPB-', '')}"
    _insert_dict(
        conn,
        "vault_storage_provider_read_path_blockers",
        {
            "read_path_blocker_id": blocker_id,
            "read_path_lock_contract_id": contract_id,
            "source_write_path_blocker_id": blocker["write_path_blocker_id"],
            "source_connection_test_blocker_id": blocker["source_connection_test_blocker_id"],
            "source_encryption_blocker_id": blocker["source_encryption_blocker_id"],
            "source_endpoint_namespace_blocker_id": blocker["source_endpoint_namespace_blocker_id"],
            "source_ledger_blocker_id": blocker["source_ledger_blocker_id"],
            "source_credential_blocker_id": blocker["source_credential_blocker_id"],
            "source_config_blocker_id": blocker["source_config_blocker_id"],
            "source_readiness_blocker_id": blocker["source_readiness_blocker_id"],
            "source_receipt_line_id": blocker["source_receipt_line_id"],
            "source_finding_id": blocker["source_finding_id"],
            "provider_candidate_id": blocker["provider_candidate_id"],
            "blocker_category": blocker["blocker_category"],
            "blocker_code": blocker["blocker_code"],
            "blocker_name": blocker["blocker_name"],
            "severity": blocker["severity"],
            "blocker_status": "REAL_READ_PATH_BLOCKER_ACTIVE_CARRIED_FROM_GP067",
            "blocks_provider_approval": 1 if blocker["blocks_provider_approval"] else 0,
            "blocks_provider_activation": 1 if blocker["blocks_provider_activation"] else 0,
            "blocks_provider_selection": 1 if blocker["blocks_provider_selection"] else 0,
            "blocks_provider_configuration": 1 if blocker["blocks_provider_configuration"] else 0,
            "blocks_provider_read_write": 1 if blocker["blocks_provider_read_write"] else 0,
            "blocks_object_body_view": 1 if blocker["blocks_object_body_view"] else 0,
            "blocks_export": 1 if blocker["blocks_export"] else 0,
            "blocks_execution": 1 if blocker["blocks_execution"] else 0,
            "tower_review_required": 1 if blocker["tower_review_required"] else 0,
            "tower_review_granted": 1 if blocker["tower_review_granted"] else 0,
            "risk_accepted": 1 if blocker["risk_accepted"] else 0,
            "risk_waived": 1 if blocker["risk_waived"] else 0,
            "mitigation_approved": 1 if blocker["mitigation_approved"] else 0,
            "resolved": 1 if blocker["resolved"] else 0,
            "created_at": now,
            "updated_at": now,
        },
    )
    return blocker_id


def _insert_event(conn, contract_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VSPRPEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_storage_provider_read_path_events",
        {
            "event_id": event_id,
            "read_path_lock_contract_id": contract_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id


def _get_counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        contract_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_read_path_lock_contracts").fetchone()["c"]
        requirement_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_read_path_requirements").fetchone()["c"]
        policy_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_read_path_policies").fetchone()["c"]
        blocker_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_read_path_blockers").fetchone()["c"]
        event_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_read_path_events").fetchone()["c"]

    return {
        "contract_count": int(contract_count),
        "requirement_count": int(requirement_count),
        "policy_count": int(policy_count),
        "blocker_count": int(blocker_count),
        "event_count": int(event_count),
    }


def _get_requirement_counts(conn: sqlite3.Connection, contract_id: str) -> Dict[str, int]:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS requirement_count,
            COUNT(DISTINCT provider_candidate_id) AS provider_candidate_count,
            COUNT(DISTINCT requirement_code) AS requirement_code_count,
            SUM(CASE WHEN requirement_required = 1 THEN 1 ELSE 0 END) AS requirement_required_count,
            SUM(CASE WHEN requirement_verified = 1 THEN 1 ELSE 0 END) AS requirement_verified_count,
            SUM(CASE WHEN read_path_locked = 1 THEN 1 ELSE 0 END) AS read_path_locked_count,
            SUM(CASE WHEN read_path_alias_only = 1 THEN 1 ELSE 0 END) AS read_path_alias_only_count,
            SUM(CASE WHEN read_path_configured = 1 THEN 1 ELSE 0 END) AS read_path_configured_count,
            SUM(CASE WHEN read_path_attempted = 1 THEN 1 ELSE 0 END) AS read_path_attempted_count,
            SUM(CASE WHEN read_path_enabled = 1 THEN 1 ELSE 0 END) AS read_path_enabled_count,
            SUM(CASE WHEN read_receipt_created = 1 THEN 1 ELSE 0 END) AS read_receipt_created_count,
            SUM(CASE WHEN object_listing_configured = 1 THEN 1 ELSE 0 END) AS object_listing_configured_count,
            SUM(CASE WHEN object_list_attempted = 1 THEN 1 ELSE 0 END) AS object_list_attempted_count,
            SUM(CASE WHEN object_listed = 1 THEN 1 ELSE 0 END) AS object_listed_count,
            SUM(CASE WHEN object_body_read_attempted = 1 THEN 1 ELSE 0 END) AS object_body_read_attempted_count,
            SUM(CASE WHEN object_body_read = 1 THEN 1 ELSE 0 END) AS object_body_read_count,
            SUM(CASE WHEN object_body_view_enabled = 1 THEN 1 ELSE 0 END) AS object_body_view_enabled_count,
            SUM(CASE WHEN credentials_configured = 1 THEN 1 ELSE 0 END) AS credentials_configured_count,
            SUM(CASE WHEN secret_references_activated = 1 THEN 1 ELSE 0 END) AS secret_references_activated_count,
            SUM(CASE WHEN provider_endpoint_configured = 1 THEN 1 ELSE 0 END) AS provider_endpoint_configured_count,
            SUM(CASE WHEN storage_container_configured = 1 THEN 1 ELSE 0 END) AS storage_container_configured_count,
            SUM(CASE WHEN namespace_configured = 1 THEN 1 ELSE 0 END) AS namespace_configured_count,
            SUM(CASE WHEN encryption_policy_configured = 1 THEN 1 ELSE 0 END) AS encryption_policy_configured_count,
            SUM(CASE WHEN provider_connection_tested = 1 THEN 1 ELSE 0 END) AS provider_connection_tested_count,
            SUM(CASE WHEN write_path_configured = 1 THEN 1 ELSE 0 END) AS write_path_configured_count,
            SUM(CASE WHEN write_path_attempted = 1 THEN 1 ELSE 0 END) AS write_path_attempted_count,
            SUM(CASE WHEN object_created = 1 THEN 1 ELSE 0 END) AS object_created_count,
            SUM(CASE WHEN provider_read_enabled = 1 THEN 1 ELSE 0 END) AS provider_read_enabled_count,
            SUM(CASE WHEN provider_write_enabled = 1 THEN 1 ELSE 0 END) AS provider_write_enabled_count,
            SUM(CASE WHEN direct_upload_enabled = 1 THEN 1 ELSE 0 END) AS direct_upload_enabled_count,
            SUM(CASE WHEN export_enabled = 1 THEN 1 ELSE 0 END) AS export_enabled_count,
            SUM(CASE WHEN execution_enabled = 1 THEN 1 ELSE 0 END) AS execution_enabled_count,
            SUM(CASE WHEN tower_review_required = 1 THEN 1 ELSE 0 END) AS tower_review_required_count,
            SUM(CASE WHEN tower_review_granted = 1 THEN 1 ELSE 0 END) AS tower_review_granted_count
        FROM vault_storage_provider_read_path_requirements
        WHERE read_path_lock_contract_id = ?
        """,
        (contract_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _get_policy_counts(conn: sqlite3.Connection, contract_id: str) -> Dict[str, int]:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS policy_count,
            COUNT(DISTINCT policy_code) AS policy_code_count,
            SUM(CASE WHEN policy_required = 1 THEN 1 ELSE 0 END) AS policy_required_count,
            SUM(CASE WHEN policy_verified = 1 THEN 1 ELSE 0 END) AS policy_verified_count,
            SUM(CASE WHEN read_path_configured = 1 THEN 1 ELSE 0 END) AS read_path_configured_count,
            SUM(CASE WHEN read_path_attempted = 1 THEN 1 ELSE 0 END) AS read_path_attempted_count,
            SUM(CASE WHEN read_path_enabled = 1 THEN 1 ELSE 0 END) AS read_path_enabled_count,
            SUM(CASE WHEN read_receipt_created = 1 THEN 1 ELSE 0 END) AS read_receipt_created_count,
            SUM(CASE WHEN object_listing_configured = 1 THEN 1 ELSE 0 END) AS object_listing_configured_count,
            SUM(CASE WHEN object_list_attempted = 1 THEN 1 ELSE 0 END) AS object_list_attempted_count,
            SUM(CASE WHEN object_listed = 1 THEN 1 ELSE 0 END) AS object_listed_count,
            SUM(CASE WHEN object_body_read_attempted = 1 THEN 1 ELSE 0 END) AS object_body_read_attempted_count,
            SUM(CASE WHEN object_body_read = 1 THEN 1 ELSE 0 END) AS object_body_read_count,
            SUM(CASE WHEN object_body_view_enabled = 1 THEN 1 ELSE 0 END) AS object_body_view_enabled_count,
            SUM(CASE WHEN actual_secret_values_stored = 1 THEN 1 ELSE 0 END) AS actual_secret_values_stored_count,
            SUM(CASE WHEN secret_values_present = 1 THEN 1 ELSE 0 END) AS secret_values_present_count,
            SUM(CASE WHEN token_material_present = 1 THEN 1 ELSE 0 END) AS token_material_present_count,
            SUM(CASE WHEN secret_references_created = 1 THEN 1 ELSE 0 END) AS secret_references_created_count,
            SUM(CASE WHEN secret_references_activated = 1 THEN 1 ELSE 0 END) AS secret_references_activated_count,
            SUM(CASE WHEN credentials_configured = 1 THEN 1 ELSE 0 END) AS credentials_configured_count,
            SUM(CASE WHEN provider_read_enabled = 1 THEN 1 ELSE 0 END) AS provider_read_enabled_count,
            SUM(CASE WHEN provider_write_enabled = 1 THEN 1 ELSE 0 END) AS provider_write_enabled_count,
            SUM(CASE WHEN direct_upload_enabled = 1 THEN 1 ELSE 0 END) AS direct_upload_enabled_count,
            SUM(CASE WHEN export_enabled = 1 THEN 1 ELSE 0 END) AS export_enabled_count,
            SUM(CASE WHEN execution_enabled = 1 THEN 1 ELSE 0 END) AS execution_enabled_count,
            SUM(CASE WHEN tower_review_required = 1 THEN 1 ELSE 0 END) AS tower_review_required_count,
            SUM(CASE WHEN tower_review_granted = 1 THEN 1 ELSE 0 END) AS tower_review_granted_count
        FROM vault_storage_provider_read_path_policies
        WHERE read_path_lock_contract_id = ?
        """,
        (contract_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _get_blocker_counts(conn: sqlite3.Connection, contract_id: str) -> Dict[str, int]:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS blocker_count,
            SUM(CASE WHEN blocker_category = 'capability_contract' THEN 1 ELSE 0 END) AS capability_blocker_count,
            SUM(CASE WHEN blocker_category = 'criteria_validation' THEN 1 ELSE 0 END) AS criteria_blocker_count,
            SUM(CASE WHEN blocker_category = 'risk_validation' THEN 1 ELSE 0 END) AS risk_blocker_count,
            SUM(CASE WHEN blocks_provider_approval = 1 THEN 1 ELSE 0 END) AS blocks_provider_approval_count,
            SUM(CASE WHEN blocks_provider_activation = 1 THEN 1 ELSE 0 END) AS blocks_provider_activation_count,
            SUM(CASE WHEN blocks_provider_selection = 1 THEN 1 ELSE 0 END) AS blocks_provider_selection_count,
            SUM(CASE WHEN blocks_provider_configuration = 1 THEN 1 ELSE 0 END) AS blocks_provider_configuration_count,
            SUM(CASE WHEN blocks_provider_read_write = 1 THEN 1 ELSE 0 END) AS blocks_provider_read_write_count,
            SUM(CASE WHEN blocks_object_body_view = 1 THEN 1 ELSE 0 END) AS blocks_object_body_view_count,
            SUM(CASE WHEN blocks_export = 1 THEN 1 ELSE 0 END) AS blocks_export_count,
            SUM(CASE WHEN blocks_execution = 1 THEN 1 ELSE 0 END) AS blocks_execution_count,
            SUM(CASE WHEN tower_review_required = 1 THEN 1 ELSE 0 END) AS tower_review_required_count,
            SUM(CASE WHEN tower_review_granted = 1 THEN 1 ELSE 0 END) AS tower_review_granted_count,
            SUM(CASE WHEN risk_accepted = 1 THEN 1 ELSE 0 END) AS risk_accepted_count,
            SUM(CASE WHEN risk_waived = 1 THEN 1 ELSE 0 END) AS risk_waived_count,
            SUM(CASE WHEN mitigation_approved = 1 THEN 1 ELSE 0 END) AS mitigation_approved_count,
            SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) AS resolved_count
        FROM vault_storage_provider_read_path_blockers
        WHERE read_path_lock_contract_id = ?
        """,
        (contract_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _compact_source_snapshot(source_contract, source_requirements_payload, blockers_payload):
    return {
        "source_write_path_lock_contract_id": source_contract["write_path_lock_contract_id"],
        "source_write_path_pack_id": source_contract["pack_id"],
        "source_contract_status": source_contract["contract_status"],
        "source_section": source_contract["section_id"],
        "source_section_range": source_contract["section_range"],
        "write_path_lock_contract_ready": source_contract["write_path_lock_contract_ready"],
        "write_path_locked": source_contract["write_path_locked"],
        "write_path_alias_only": source_contract["write_path_alias_only"],
        "requirement_count": source_requirements_payload["requirement_count"],
        "provider_candidate_count": source_requirements_payload["provider_candidate_count"],
        "requirement_code_count": source_requirements_payload["requirement_code_count"],
        "write_path_configured_count": source_requirements_payload["write_path_configured_count"],
        "write_path_attempted_count": source_requirements_payload["write_path_attempted_count"],
        "object_created_count": source_requirements_payload["object_created_count"],
        "provider_write_enabled_count": source_requirements_payload["provider_write_enabled_count"],
        "provider_read_enabled_count": source_requirements_payload["provider_read_enabled_count"],
        "blocker_count": blockers_payload["blocker_count"],
        "blocks_provider_configuration_count": blockers_payload["blocks_provider_configuration_count"],
        "blocks_provider_read_write_count": blockers_payload["blocks_provider_read_write_count"],
        "blocks_object_body_view_count": blockers_payload["blocks_object_body_view_count"],
        "blocks_export_count": blockers_payload["blocks_export_count"],
        "blocks_execution_count": blockers_payload["blocks_execution_count"],
        "provider_configured": source_contract["provider_configured"],
        "provider_connection_tested": source_contract["provider_connection_tested"],
        "provider_write_enabled": source_contract["provider_write_enabled"],
        "provider_read_enabled": source_contract["provider_read_enabled"],
        "object_body_view_enabled": source_contract["object_body_view_enabled"],
        "direct_upload_enabled": source_contract["direct_upload_enabled"],
        "export_enabled": source_contract["export_enabled"],
        "execution_enabled": source_contract["execution_enabled"],
        "vault_done": source_contract["vault_done"],
    }


def _build_contract_data(source_contract, source_requirements_payload, blockers_payload, candidates):
    return {
        "read_path_lock_schema_version": SCHEMA_VERSION,
        "contract_type": "REAL_STORAGE_PROVIDER_READ_PATH_LOCK_CONTRACT",
        "contract_status": "REAL_READ_PATH_LOCK_CONTRACT_OPEN_TOWER_LOCKED",
        "real_durable_read_path_lock_contract": True,
        "metadata_source": "VAULT_GP067_REAL_STORAGE_PROVIDER_WRITE_PATH_LOCK_CONTRACT",
        "source_write_path_lock_contract_id": source_contract["write_path_lock_contract_id"],
        "source_write_path_pack_id": source_contract["pack_id"],
        "current_section": {
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "provider_candidate_count": len(candidates),
        "requirement_code_count": len(READ_PATH_REQUIREMENT_SPECS),
        "requirement_count": len(candidates) * len(READ_PATH_REQUIREMENT_SPECS),
        "policy_count": len(READ_PATH_POLICIES),
        "carried_blocker_count": blockers_payload["blocker_count"],
        "read_path_requirements": READ_PATH_REQUIREMENT_SPECS,
        "read_path_policies": READ_PATH_POLICIES,
        "read_path_truth": {
            "read_path_lock_contract_ready": True,
            "read_path_requirements_ready": True,
            "read_path_policy_ready": True,
            "read_path_locked": True,
            "read_path_alias_only": True,
            "read_path_configured": False,
            "read_path_attempted": False,
            "read_path_enabled": False,
            "read_receipt_created": False,
            "object_listing_configured": False,
            "object_list_attempted": False,
            "object_listed": False,
            "object_body_read_attempted": False,
            "object_body_read": False,
            "object_body_view_enabled": False,
            "provider_read_enabled": False,
        },
        "provider_truth": {
            "provider_read_enabled": False,
            "provider_write_enabled": False,
            "provider_object_read_claimed": False,
            "provider_object_write_claimed": False,
            "object_body_view_enabled": False,
            "direct_upload_enabled": False,
            "export_enabled": False,
            "execution_enabled": False,
            "vault_done": False,
        },
        "next_pack": NEXT_PACK,
        "next_pack_title": NEXT_PACK_TITLE,
        "safe_to_continue_to_gp069": True,
    }


def _boolify_row(row: sqlite3.Row, json_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    json_map = json_map or {}
    payload = {}
    for key in row.keys():
        if key in json_map:
            payload[json_map[key]] = _json_loads(row[key])
        elif isinstance(row[key], int):
            payload[key] = bool(row[key])
        else:
            payload[key] = row[key]
    return payload


def get_storage_provider_read_path_lock_contract_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_read_path_lock_contract(db_path)

    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_read_path_lock_contracts
            WHERE read_path_lock_contract_id = ?
            """,
            (DEFAULT_READ_PATH_LOCK_CONTRACT_ID,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Real storage provider read path lock contract was not initialized.")

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "read_path_lock_contract": _boolify_row(row, {"contract_data_json": "contract_data"}),
    }


def get_storage_provider_read_path_requirements(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_read_path_lock_contract(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_read_path_requirements
            WHERE read_path_lock_contract_id = ?
            ORDER BY provider_candidate_id ASC, requirement_category ASC, requirement_code ASC
            """,
            (DEFAULT_READ_PATH_LOCK_CONTRACT_ID,),
        ).fetchall()
        counts = _get_requirement_counts(conn, DEFAULT_READ_PATH_LOCK_CONTRACT_ID)

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "requirements": [_boolify_row(row) for row in rows],
    }


def get_storage_provider_read_path_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_read_path_lock_contract(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_read_path_policies
            WHERE read_path_lock_contract_id = ?
            ORDER BY policy_category ASC, policy_code ASC
            """,
            (DEFAULT_READ_PATH_LOCK_CONTRACT_ID,),
        ).fetchall()
        counts = _get_policy_counts(conn, DEFAULT_READ_PATH_LOCK_CONTRACT_ID)

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "policies": [_boolify_row(row) for row in rows],
    }


def get_storage_provider_read_path_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_read_path_lock_contract(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_read_path_blockers
            WHERE read_path_lock_contract_id = ?
            ORDER BY provider_candidate_id ASC, blocker_category ASC, blocker_code ASC
            """,
            (DEFAULT_READ_PATH_LOCK_CONTRACT_ID,),
        ).fetchall()
        counts = _get_blocker_counts(conn, DEFAULT_READ_PATH_LOCK_CONTRACT_ID)

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "blockers": [_boolify_row(row) for row in rows],
    }


def get_storage_provider_read_path_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_read_path_lock_contract(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_read_path_events
            WHERE read_path_lock_contract_id = ?
            ORDER BY created_at ASC, event_id ASC
            """,
            (DEFAULT_READ_PATH_LOCK_CONTRACT_ID,),
        ).fetchall()

    events = []
    for row in rows:
        events.append(
            {
                "event_id": row["event_id"],
                "read_path_lock_contract_id": row["read_path_lock_contract_id"],
                "event_type": row["event_type"],
                "event_payload": _json_loads(row["event_payload_json"]),
                "created_at": row["created_at"],
            }
        )

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "event_count": len(events),
        "events": events,
    }


def record_storage_provider_read_path_event(
    event_type: str,
    event_payload: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    initialize_real_storage_provider_read_path_lock_contract(db_path)
    payload = dict(event_payload or {})
    payload.update(
        {
            "write_type": "REAL_STORAGE_PROVIDER_READ_PATH_LOCK_EVENT",
            "read_path_lock_contract_ready": True,
            "read_path_locked": True,
            "read_path_alias_only": True,
            "read_path_configured": False,
            "read_path_attempted": False,
            "read_path_enabled": False,
            "read_receipt_created": False,
            "object_listing_configured": False,
            "object_list_attempted": False,
            "object_listed": False,
            "object_body_read_attempted": False,
            "object_body_read": False,
            "object_body_view_enabled": False,
            "actual_secret_values_stored": False,
            "secret_values_present": False,
            "token_material_present": False,
            "secret_references_created": False,
            "secret_references_activated": False,
            "credentials_configured": False,
            "provider_read_enabled": False,
            "provider_write_enabled": False,
            "direct_upload_enabled": False,
            "export_enabled": False,
            "execution_enabled": False,
            "vault_done": False,
        }
    )

    with _connect(db_path) as conn:
        event_id = _insert_event(conn, DEFAULT_READ_PATH_LOCK_CONTRACT_ID, event_type, payload)
        conn.commit()

    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "read_path_lock_contract_id": DEFAULT_READ_PATH_LOCK_CONTRACT_ID,
        "real_sqlite_backed": True,
        **payload,
    }


def validate_storage_provider_read_path_lock_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    contract = get_storage_provider_read_path_lock_contract_record(db_path)["read_path_lock_contract"]
    requirements = get_storage_provider_read_path_requirements(db_path)
    policies = get_storage_provider_read_path_policies(db_path)
    blockers = get_storage_provider_read_path_blockers(db_path)
    events = get_storage_provider_read_path_events(db_path)

    expected_requirements = 5 * len(READ_PATH_REQUIREMENT_SPECS)
    expected_policies = len(READ_PATH_POLICIES)
    expected_blockers = 140

    checks = [
        {"code": "REAL_SQLITE_READ_PATH_LOCK_CONTRACT_EXISTS", "passed": contract["read_path_lock_contract_id"] == DEFAULT_READ_PATH_LOCK_CONTRACT_ID},
        {"code": "SOURCE_GP067_WRITE_PATH_LOCK_CONTRACT_ATTACHED", "passed": contract["source_write_path_lock_contract_id"] == DEFAULT_WRITE_PATH_LOCK_CONTRACT_ID},
        {"code": "READ_PATH_LOCK_CONTRACT_READY", "passed": contract["read_path_lock_contract_ready"] is True},
        {"code": "READ_PATH_REQUIREMENTS_READY", "passed": contract["read_path_requirements_ready"] is True},
        {"code": "READ_PATH_POLICY_READY", "passed": contract["read_path_policy_ready"] is True},
        {"code": "READ_PATH_LOCKED", "passed": contract["read_path_locked"] is True},
        {"code": "READ_PATH_ALIAS_ONLY", "passed": contract["read_path_alias_only"] is True},
        {"code": "REAL_READ_PATH_REQUIREMENTS_EXIST", "passed": requirements["requirement_count"] == expected_requirements},
        {"code": "ALL_REQUIREMENTS_REQUIRED", "passed": requirements["requirement_required_count"] == expected_requirements},
        {"code": "NO_REQUIREMENTS_VERIFIED_YET", "passed": requirements["requirement_verified_count"] == 0},
        {"code": "ALL_REQUIREMENTS_READ_PATH_LOCKED", "passed": requirements["read_path_locked_count"] == expected_requirements},
        {"code": "ALL_REQUIREMENTS_READ_ALIAS_ONLY", "passed": requirements["read_path_alias_only_count"] == expected_requirements},
        {"code": "NO_REQUIREMENT_READ_PATH_CONFIGURED", "passed": requirements["read_path_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_READ_PATH_ATTEMPTED", "passed": requirements["read_path_attempted_count"] == 0},
        {"code": "NO_REQUIREMENT_READ_PATH_ENABLED", "passed": requirements["read_path_enabled_count"] == 0},
        {"code": "NO_REQUIREMENT_READ_RECEIPT_CREATED", "passed": requirements["read_receipt_created_count"] == 0},
        {"code": "NO_REQUIREMENT_OBJECT_LISTING_CONFIGURED", "passed": requirements["object_listing_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_OBJECT_LIST_ATTEMPTED", "passed": requirements["object_list_attempted_count"] == 0},
        {"code": "NO_REQUIREMENT_OBJECT_LISTED", "passed": requirements["object_listed_count"] == 0},
        {"code": "NO_REQUIREMENT_OBJECT_BODY_READ_ATTEMPTED", "passed": requirements["object_body_read_attempted_count"] == 0},
        {"code": "NO_REQUIREMENT_OBJECT_BODY_READ", "passed": requirements["object_body_read_count"] == 0},
        {"code": "NO_REQUIREMENT_OBJECT_BODY_VIEW", "passed": requirements["object_body_view_enabled_count"] == 0},
        {"code": "NO_REQUIREMENT_CREDENTIALS_CONFIGURED", "passed": requirements["credentials_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_SECRET_REFERENCES_ACTIVATED", "passed": requirements["secret_references_activated_count"] == 0},
        {"code": "NO_REQUIREMENT_PROVIDER_ENDPOINT_CONFIGURED", "passed": requirements["provider_endpoint_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_STORAGE_CONTAINER_CONFIGURED", "passed": requirements["storage_container_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_NAMESPACE_CONFIGURED", "passed": requirements["namespace_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_ENCRYPTION_CONFIGURED", "passed": requirements["encryption_policy_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_CONNECTION_TESTED", "passed": requirements["provider_connection_tested_count"] == 0},
        {"code": "NO_REQUIREMENT_WRITE_PATH_CONFIGURED", "passed": requirements["write_path_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_WRITE_PATH_ATTEMPTED", "passed": requirements["write_path_attempted_count"] == 0},
        {"code": "NO_REQUIREMENT_OBJECT_CREATED", "passed": requirements["object_created_count"] == 0},
        {"code": "NO_REQUIREMENT_READ_WRITE", "passed": requirements["provider_read_enabled_count"] == 0 and requirements["provider_write_enabled_count"] == 0},
        {"code": "NO_REQUIREMENT_DIRECT_UPLOAD", "passed": requirements["direct_upload_enabled_count"] == 0},
        {"code": "NO_REQUIREMENT_EXPORT", "passed": requirements["export_enabled_count"] == 0},
        {"code": "NO_REQUIREMENT_EXECUTION", "passed": requirements["execution_enabled_count"] == 0},
        {"code": "NO_REQUIREMENT_TOWER_REVIEW_GRANTED", "passed": requirements["tower_review_granted_count"] == 0},
        {"code": "REAL_READ_PATH_POLICIES_EXIST", "passed": policies["policy_count"] == expected_policies},
        {"code": "ALL_POLICIES_REQUIRED", "passed": policies["policy_required_count"] == expected_policies},
        {"code": "NO_POLICIES_VERIFIED_YET", "passed": policies["policy_verified_count"] == 0},
        {"code": "NO_POLICY_READ_PATH_CONFIGURED", "passed": policies["read_path_configured_count"] == 0},
        {"code": "NO_POLICY_READ_PATH_ATTEMPTED", "passed": policies["read_path_attempted_count"] == 0},
        {"code": "NO_POLICY_READ_PATH_ENABLED", "passed": policies["read_path_enabled_count"] == 0},
        {"code": "NO_POLICY_READ_RECEIPT_CREATED", "passed": policies["read_receipt_created_count"] == 0},
        {"code": "NO_POLICY_OBJECT_LISTING_CONFIGURED", "passed": policies["object_listing_configured_count"] == 0},
        {"code": "NO_POLICY_OBJECT_LIST_ATTEMPTED", "passed": policies["object_list_attempted_count"] == 0},
        {"code": "NO_POLICY_OBJECT_LISTED", "passed": policies["object_listed_count"] == 0},
        {"code": "NO_POLICY_OBJECT_BODY_READ_ATTEMPTED", "passed": policies["object_body_read_attempted_count"] == 0},
        {"code": "NO_POLICY_OBJECT_BODY_READ", "passed": policies["object_body_read_count"] == 0},
        {"code": "NO_POLICY_OBJECT_BODY_VIEW", "passed": policies["object_body_view_enabled_count"] == 0},
        {"code": "NO_POLICY_SECRETS_PRESENT", "passed": policies["secret_values_present_count"] == 0 and policies["token_material_present_count"] == 0},
        {"code": "NO_POLICY_SECRET_REFERENCES_CREATED", "passed": policies["secret_references_created_count"] == 0},
        {"code": "NO_POLICY_SECRET_REFERENCES_ACTIVATED", "passed": policies["secret_references_activated_count"] == 0},
        {"code": "NO_POLICY_CREDENTIALS_CONFIGURED", "passed": policies["credentials_configured_count"] == 0},
        {"code": "NO_POLICY_READ_WRITE", "passed": policies["provider_read_enabled_count"] == 0 and policies["provider_write_enabled_count"] == 0},
        {"code": "NO_POLICY_DIRECT_UPLOAD", "passed": policies["direct_upload_enabled_count"] == 0},
        {"code": "NO_POLICY_EXPORT", "passed": policies["export_enabled_count"] == 0},
        {"code": "NO_POLICY_EXECUTION", "passed": policies["execution_enabled_count"] == 0},
        {"code": "REAL_READ_PATH_BLOCKERS_CARRIED_FORWARD", "passed": blockers["blocker_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_PROVIDER_CONFIGURATION", "passed": blockers["blocks_provider_configuration_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_PROVIDER_READ_WRITE", "passed": blockers["blocks_provider_read_write_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_OBJECT_BODY_VIEW", "passed": blockers["blocks_object_body_view_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_EXPORT", "passed": blockers["blocks_export_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_EXECUTION", "passed": blockers["blocks_execution_count"] == expected_blockers},
        {"code": "NO_BLOCKERS_TOWER_REVIEW_GRANTED", "passed": blockers["tower_review_granted_count"] == 0},
        {"code": "NO_BLOCKERS_RESOLVED", "passed": blockers["resolved_count"] == 0},
        {"code": "NO_CONTRACT_READ_PATH_CONFIGURED", "passed": contract["read_path_configured"] is False},
        {"code": "NO_CONTRACT_READ_PATH_ATTEMPTED", "passed": contract["read_path_attempted"] is False},
        {"code": "NO_CONTRACT_READ_PATH_ENABLED", "passed": contract["read_path_enabled"] is False},
        {"code": "NO_CONTRACT_READ_RECEIPT_CREATED", "passed": contract["read_receipt_created"] is False},
        {"code": "NO_CONTRACT_OBJECT_LISTING_CONFIGURED", "passed": contract["object_listing_configured"] is False},
        {"code": "NO_CONTRACT_OBJECT_LIST_ATTEMPTED", "passed": contract["object_list_attempted"] is False},
        {"code": "NO_CONTRACT_OBJECT_LISTED", "passed": contract["object_listed"] is False},
        {"code": "NO_CONTRACT_OBJECT_BODY_READ_ATTEMPTED", "passed": contract["object_body_read_attempted"] is False},
        {"code": "NO_CONTRACT_OBJECT_BODY_READ", "passed": contract["object_body_read"] is False},
        {"code": "NO_CONTRACT_OBJECT_BODY_VIEW", "passed": contract["object_body_view_enabled"] is False},
        {"code": "NO_CONTRACT_SECRETS_PRESENT", "passed": contract["secret_values_present"] is False and contract["token_material_present"] is False},
        {"code": "NO_CONTRACT_KEY_MATERIAL_STORED", "passed": contract["key_material_stored"] is False},
        {"code": "NO_CONTRACT_KMS_KEY_ID_STORED", "passed": contract["kms_key_id_stored"] is False},
        {"code": "NO_CONTRACT_ENCRYPTION_CONFIGURED", "passed": contract["encryption_policy_configured"] is False},
        {"code": "NO_CONTRACT_SECRET_REFERENCES_CREATED", "passed": contract["secret_references_created"] is False},
        {"code": "NO_CONTRACT_SECRET_REFERENCES_ACTIVATED", "passed": contract["secret_references_activated"] is False},
        {"code": "NO_CREDENTIALS_CONFIGURED", "passed": contract["credentials_configured"] is False},
        {"code": "NO_PROVIDER_ENDPOINT_CONFIGURED", "passed": contract["provider_endpoint_configured"] is False},
        {"code": "NO_STORAGE_CONTAINER_CONFIGURED", "passed": contract["storage_container_configured"] is False},
        {"code": "NO_NAMESPACE_CONFIGURED", "passed": contract["namespace_configured"] is False},
        {"code": "NO_CONNECTION_TESTED", "passed": contract["provider_connection_tested"] is False},
        {"code": "NO_WRITE_PATH_CONFIGURED", "passed": contract["write_path_configured"] is False},
        {"code": "NO_WRITE_PATH_ATTEMPTED", "passed": contract["write_path_attempted"] is False},
        {"code": "NO_OBJECT_CREATED", "passed": contract["object_created"] is False},
        {"code": "NO_PROVIDER_CONFIGURATION_READY", "passed": contract["provider_configuration_ready"] is False},
        {"code": "NO_PROVIDER_CONFIGURED", "passed": contract["provider_configured"] is False},
        {"code": "NO_PROVIDER_READ_WRITE", "passed": contract["provider_read_enabled"] is False and contract["provider_write_enabled"] is False},
        {"code": "NO_PROVIDER_OBJECT_READ_CLAIMED", "passed": contract["provider_object_read_claimed"] is False},
        {"code": "NO_PROVIDER_OBJECT_WRITE_CLAIMED", "passed": contract["provider_object_write_claimed"] is False},
        {"code": "NO_DIRECT_UPLOAD", "passed": contract["direct_upload_enabled"] is False},
        {"code": "NO_EXPORT", "passed": contract["export_enabled"] is False},
        {"code": "NO_EXECUTION", "passed": contract["execution_enabled"] is False},
        {"code": "VAULT_NOT_DONE", "passed": contract["vault_done"] is False},
        {"code": "EVENT_LOG_EXISTS", "passed": events["event_count"] >= 6},
    ]

    failed = [item for item in checks if not item["passed"]]

    return {
        "pack": _pack_payload(),
        "validation_ready": True,
        "valid": len(failed) == 0,
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "failed_checks": failed,
        "checks": checks,
        "real_sqlite_backed": True,
        "safe_to_continue_to_gp069": len(failed) == 0,
    }


def get_storage_provider_read_path_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp069": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "Continue under ARCHIVE VAULT — REAL STORAGE PROVIDER CONFIGURATION LAYER / GP061-GP070. GP069 should build the real provider object body view lock contract while keeping read path, object listing, object body read, export, and execution locked.",
            "carry_forward_rules": [
                "Keep the real SQLite read-path lock contract.",
                "Keep real read-path requirement rows.",
                "Keep real read-path policy rows.",
                "Keep real blockers carried from GP067.",
                "Build GP069 Real Storage Provider Object Body View Lock Contract next.",
                "Do not configure read paths.",
                "Do not attempt provider reads.",
                "Do not enable provider read.",
                "Do not create read receipts yet.",
                "Do not configure object listing.",
                "Do not attempt object listing.",
                "Do not list provider objects.",
                "Do not attempt object body read.",
                "Do not read object bodies.",
                "Do not unlock object body view.",
                "Do not enable provider write.",
                "Do not unlock direct upload.",
                "Do not unlock export.",
                "Do not unlock execution.",
                "Do not treat Vault as done.",
            ],
        },
    }


def get_real_storage_provider_read_path_lock_contract_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_read_path_lock_contract(db_path)
    contract = get_storage_provider_read_path_lock_contract_record(db_path)["read_path_lock_contract"]
    requirements = get_storage_provider_read_path_requirements(db_path)
    policies = get_storage_provider_read_path_policies(db_path)
    blockers = get_storage_provider_read_path_blockers(db_path)
    events = get_storage_provider_read_path_events(db_path)
    validation = validate_storage_provider_read_path_lock_contract(db_path)

    return {
        "pack": _pack_payload(),
        "read_path_truth": _read_path_truth(contract, requirements, policies, blockers, events["event_count"], validation),
        "store": init,
        "read_path_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_read_path_next_step()["next_step"],
    }


def get_gp068_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_read_path_lock_contract_home(db_path)
    contract = home["read_path_lock_contract"]
    requirements = home["requirements"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp068_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_read_path_lock_contract_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_contract_count": home["store"]["contract_count"],
            "real_requirement_count": home["store"]["requirement_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp067_write_path_lock_contract_attached": True,
            "read_path_lock_contract_ready": contract["read_path_lock_contract_ready"],
            "read_path_requirements_ready": contract["read_path_requirements_ready"],
            "read_path_policy_ready": contract["read_path_policy_ready"],
            "read_path_locked": contract["read_path_locked"],
            "read_path_alias_only": contract["read_path_alias_only"],
            "provider_candidate_count": requirements["provider_candidate_count"],
            "requirement_code_count": requirements["requirement_code_count"],
            "policy_code_count": policies["policy_code_count"],
            "read_path_configured_count": requirements["read_path_configured_count"] + policies["read_path_configured_count"],
            "read_path_attempted_count": requirements["read_path_attempted_count"] + policies["read_path_attempted_count"],
            "read_path_enabled_count": requirements["read_path_enabled_count"] + policies["read_path_enabled_count"],
            "read_receipt_created_count": requirements["read_receipt_created_count"] + policies["read_receipt_created_count"],
            "object_listing_configured_count": requirements["object_listing_configured_count"] + policies["object_listing_configured_count"],
            "object_list_attempted_count": requirements["object_list_attempted_count"] + policies["object_list_attempted_count"],
            "object_listed_count": requirements["object_listed_count"] + policies["object_listed_count"],
            "object_body_read_attempted_count": requirements["object_body_read_attempted_count"] + policies["object_body_read_attempted_count"],
            "object_body_read_count": requirements["object_body_read_count"] + policies["object_body_read_count"],
            "object_body_view_enabled_count": requirements["object_body_view_enabled_count"] + policies["object_body_view_enabled_count"],
            "secret_value_present_count": policies["secret_values_present_count"],
            "token_material_present_count": policies["token_material_present_count"],
            "secret_references_created_count": policies["secret_references_created_count"],
            "secret_references_activated_count": requirements["secret_references_activated_count"] + policies["secret_references_activated_count"],
            "credentials_configured_count": requirements["credentials_configured_count"] + policies["credentials_configured_count"],
            "provider_read_enabled_count": requirements["provider_read_enabled_count"] + policies["provider_read_enabled_count"],
            "provider_write_enabled_count": requirements["provider_write_enabled_count"] + policies["provider_write_enabled_count"],
            "direct_upload_enabled_count": requirements["direct_upload_enabled_count"] + policies["direct_upload_enabled_count"],
            "capability_blocker_count": blockers["capability_blocker_count"],
            "criteria_blocker_count": blockers["criteria_blocker_count"],
            "risk_blocker_count": blockers["risk_blocker_count"],
            "blocks_provider_configuration_count": blockers["blocks_provider_configuration_count"],
            "blocks_provider_read_write_count": blockers["blocks_provider_read_write_count"],
            "blocks_object_body_view_count": blockers["blocks_object_body_view_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "tower_review_granted_count": blockers["tower_review_granted_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp069": validation["safe_to_continue_to_gp069"],
            "vault_done": False,
            "foundation_status": "read_path_lock_contract_ready_safe_to_continue_not_done",
            "read_path_configured": contract["read_path_configured"],
            "read_path_attempted": contract["read_path_attempted"],
            "read_path_enabled": contract["read_path_enabled"],
            "read_receipt_created": contract["read_receipt_created"],
            "object_listing_configured": contract["object_listing_configured"],
            "object_list_attempted": contract["object_list_attempted"],
            "object_listed": contract["object_listed"],
            "object_body_read_attempted": contract["object_body_read_attempted"],
            "object_body_read": contract["object_body_read"],
            "object_body_view_enabled": contract["object_body_view_enabled"],
            "actual_secret_values_stored": contract["actual_secret_values_stored"],
            "secret_values_present": contract["secret_values_present"],
            "token_material_present": contract["token_material_present"],
            "credentials_configured": contract["credentials_configured"],
            "provider_endpoint_configured": contract["provider_endpoint_configured"],
            "storage_container_configured": contract["storage_container_configured"],
            "namespace_configured": contract["namespace_configured"],
            "encryption_policy_configured": contract["encryption_policy_configured"],
            "provider_connection_tested": contract["provider_connection_tested"],
            "write_path_configured": contract["write_path_configured"],
            "write_path_attempted": contract["write_path_attempted"],
            "object_created": contract["object_created"],
            "provider_configuration_ready": contract["provider_configuration_ready"],
            "provider_read_write_ready": contract["provider_read_write_ready"],
            "provider_approved": contract["provider_approved"],
            "provider_activated": contract["provider_activated"],
            "provider_recommended": contract["provider_recommended"],
            "provider_selected": contract["provider_selected"],
            "provider_configured": contract["provider_configured"],
            "provider_write_enabled": contract["provider_write_enabled"],
            "provider_read_enabled": contract["provider_read_enabled"],
            "provider_object_read_claimed": contract["provider_object_read_claimed"],
            "provider_object_write_claimed": contract["provider_object_write_claimed"],
            "direct_upload_enabled": contract["direct_upload_enabled"],
            "export_enabled": contract["export_enabled"],
            "execution_enabled": contract["execution_enabled"],
            "clouds_status": "parked_do_not_continue_from_vault_gp068",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "read_path_truth": home["read_path_truth"],
        "routes": home["routes"],
        "read_path_lock_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }


def _pack_payload() -> Dict[str, Any]:
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP067"],
        "foundation_status": "read_path_lock_contract_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_read_path_lock_contract",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }


def _routes_payload() -> Dict[str, str]:
    return {
        "room_title": "Vault Real Storage Provider Read Path Lock Contract",
        "section_header": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "route": "/vault/real-storage-provider-read-path-lock-contract",
        "json_route": "/vault/real-storage-provider-read-path-lock-contract.json",
        "record_route": "/vault/storage-provider-read-path-lock-contract-record.json",
        "requirements_route": "/vault/storage-provider-read-path-requirements.json",
        "policies_route": "/vault/storage-provider-read-path-policies.json",
        "blockers_route": "/vault/storage-provider-read-path-blockers.json",
        "events_route": "/vault/storage-provider-read-path-events.json",
        "validation_route": "/vault/storage-provider-read-path-validation.json",
        "next_step_route": "/vault/storage-provider-read-path-next-step.json",
        "gp068_status_route": "/vault/gp068-status.json",
    }


def _read_path_truth(contract, requirements, policies, blockers, event_count, validation) -> Dict[str, Any]:
    return {
        "real_storage_provider_read_path_lock_contract_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "real_read_path_lock_contract_exists": contract["read_path_lock_contract_id"] == DEFAULT_READ_PATH_LOCK_CONTRACT_ID,
        "real_read_path_requirement_rows_exist": requirements["requirement_count"] == 40,
        "real_read_path_policy_rows_exist": policies["policy_count"] == len(READ_PATH_POLICIES),
        "real_read_path_blocker_rows_exist": blockers["blocker_count"] == 140,
        "real_event_log_exists": event_count >= 6,
        "source_gp067_write_path_lock_contract_attached": contract["source_write_path_lock_contract_id"] == DEFAULT_WRITE_PATH_LOCK_CONTRACT_ID,
        "validation_passed": validation["valid"],
        "read_path_lock_contract_ready": contract["read_path_lock_contract_ready"],
        "read_path_requirements_ready": contract["read_path_requirements_ready"],
        "read_path_policy_ready": contract["read_path_policy_ready"],
        "read_path_locked": contract["read_path_locked"],
        "read_path_alias_only": contract["read_path_alias_only"],
        "requirement_count": requirements["requirement_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "read_path_configured_count": requirements["read_path_configured_count"] + policies["read_path_configured_count"],
        "read_path_attempted_count": requirements["read_path_attempted_count"] + policies["read_path_attempted_count"],
        "read_path_enabled_count": requirements["read_path_enabled_count"] + policies["read_path_enabled_count"],
        "read_receipt_created_count": requirements["read_receipt_created_count"] + policies["read_receipt_created_count"],
        "object_listing_configured_count": requirements["object_listing_configured_count"] + policies["object_listing_configured_count"],
        "object_list_attempted_count": requirements["object_list_attempted_count"] + policies["object_list_attempted_count"],
        "object_listed_count": requirements["object_listed_count"] + policies["object_listed_count"],
        "object_body_read_attempted_count": requirements["object_body_read_attempted_count"] + policies["object_body_read_attempted_count"],
        "object_body_read_count": requirements["object_body_read_count"] + policies["object_body_read_count"],
        "object_body_view_enabled_count": requirements["object_body_view_enabled_count"] + policies["object_body_view_enabled_count"],
        "provider_read_enabled": contract["provider_read_enabled"],
        "provider_write_enabled": contract["provider_write_enabled"],
        "provider_object_read_claimed": contract["provider_object_read_claimed"],
        "provider_object_write_claimed": contract["provider_object_write_claimed"],
        "object_body_view_enabled": contract["object_body_view_enabled"],
        "direct_upload_enabled": contract["direct_upload_enabled"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "vault_done": contract["vault_done"],
        "safe_to_continue_to_gp069": validation["safe_to_continue_to_gp069"],
    }


def render_real_storage_provider_read_path_lock_contract_page() -> str:
    home = get_real_storage_provider_read_path_lock_contract_home()
    truth = home["read_path_truth"]
    requirements = home["requirements"]["requirements"]
    policies = home["policies"]["policies"]
    routes = home["routes"]
    next_step = home["next_step"]

    requirement_cards = "\n".join(_render_requirement_card(item) for item in requirements[:9])
    policy_cards = "\n".join(_render_policy_card(item) for item in policies[:9])
    checks = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['code'])}</strong>
            <span>{'passed' if item['passed'] else 'failed'}</span>
          </div>
          <div class="pill {'ok' if item['passed'] else 'danger'}">{'Pass' if item['passed'] else 'Fail'}</div>
        </div>
        """
        for item in home["validation"]["checks"]
    )
    rules_html = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Real Storage Provider Read Path Lock Contract · GP068</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg0: #040612;
      --bg1: #090d22;
      --panel: rgba(15, 23, 52, 0.84);
      --panel2: rgba(21, 32, 74, 0.76);
      --line: rgba(160, 179, 255, 0.24);
      --text: #eef3ff;
      --muted: #9da9d7;
      --gold: #f5d17e;
      --cyan: #83eaff;
      --danger: #ff8c9c;
      --ok: #9dffca;
      --shadow: rgba(0, 0, 0, 0.50);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 13% 9%, rgba(173, 141, 255, 0.18), transparent 34%),
        radial-gradient(circle at 88% 5%, rgba(131, 234, 255, 0.13), transparent 30%),
        radial-gradient(circle at 70% 90%, rgba(245, 209, 126, 0.09), transparent 32%),
        linear-gradient(135deg, var(--bg0), var(--bg1) 52%, #03040b);
    }}
    .shell {{ width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 34px 0 48px; }}
    .hero {{
      border: 1px solid var(--line);
      border-radius: 30px;
      padding: 30px;
      background: linear-gradient(145deg, rgba(15, 23, 52, 0.94), rgba(6, 10, 25, 0.74));
      box-shadow: 0 28px 74px var(--shadow);
    }}
    .eyebrow {{ color: var(--gold); letter-spacing: .18em; text-transform: uppercase; font-size: 12px; font-weight: 850; }}
    h1 {{ margin: 14px 0 14px; font-size: clamp(34px, 5vw, 62px); line-height: .95; }}
    p {{ color: var(--muted); line-height: 1.62; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-top: 22px; }}
    .metric {{ border: 1px solid var(--line); background: rgba(5, 8, 20, 0.48); border-radius: 20px; padding: 16px; }}
    .metric strong {{ display: block; font-size: 26px; }}
    .metric span {{ color: var(--muted); font-size: 13px; }}
    .section {{ margin-top: 18px; border: 1px solid var(--line); background: var(--panel); border-radius: 24px; padding: 22px; box-shadow: 0 20px 50px rgba(0, 0, 0, .28); }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
    .pill {{ display: inline-flex; align-items: center; border: 1px solid var(--line); border-radius: 999px; padding: 7px 10px; font-size: 12px; font-weight: 800; color: var(--text); background: rgba(10, 16, 38, .72); white-space: nowrap; }}
    .pill.ok {{ color: var(--ok); border-color: rgba(157, 255, 202, .32); }}
    .pill.danger {{ color: var(--danger); border-color: rgba(255, 140, 156, .32); }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }}
    .card {{ border: 1px solid var(--line); background: var(--panel2); border-radius: 20px; padding: 16px; }}
    .title {{ font-weight: 900; font-size: 15px; }}
    .meta {{ color: var(--muted); font-size: 13px; margin-top: 8px; line-height: 1.55; }}
    .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    .status-row {{ display: flex; align-items: center; justify-content: space-between; gap: 14px; padding: 12px 0; border-bottom: 1px solid rgba(160, 179, 255, .14); }}
    .status-row span {{ display: block; color: var(--muted); font-size: 12px; margin-top: 4px; }}
    code {{ color: var(--cyan); background: rgba(0, 0, 0, .28); border: 1px solid var(--line); border-radius: 8px; padding: 2px 6px; }}
    ul {{ margin: 14px 0 0; color: var(--muted); line-height: 1.75; }}
    @media (max-width: 1020px) {{ .metrics, .grid, .two-col {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="eyebrow">Archive Vault · Giant Pack 068</div>
      <div class="eyebrow">Real Storage Provider Configuration Layer · GP061-GP070</div>
      <h1>Real Storage Provider Read Path Lock Contract</h1>
      <p>
        GP068 creates a real read-path lock contract with requirement rows,
        policy rows, carried blockers, and event history. It does not configure reads,
        object listing, object body reading, object body view, export, or execution.
      </p>
      <div class="metrics">
        <div class="metric"><strong>{home['store']['requirement_count']}</strong><span>read-path requirements</span></div>
        <div class="metric"><strong>{home['store']['policy_count']}</strong><span>read-path policies</span></div>
        <div class="metric"><strong>{truth['read_path_attempted_count']}</strong><span>read attempts</span></div>
        <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
      </div>
      <div class="chips">
        <span class="pill ok">Read-path lock ready</span>
        <span class="pill ok">Real SQLite-backed</span>
        <span class="pill danger">No read path</span>
        <span class="pill danger">No object listing</span>
        <span class="pill danger">No object body read</span>
        <span class="pill danger">No execution</span>
      </div>
    </section>

    <section class="section">
      <h2>Read-Path Requirements</h2>
      <p>These are real requirement rows. They lock provider reads and prove no object listing/body read path is configured.</p>
      <div class="grid">{requirement_cards}</div>
    </section>

    <section class="section">
      <h2>Read-Path Policies</h2>
      <p>These are real policy rows governing read path, object listing, object body read, write lock, export, and execution.</p>
      <div class="grid">{policy_cards}</div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Validation Checks</h2>
        <p>GP068 proves the contract is durable while provider read paths remain locked.</p>
        {checks}
      </div>
      <div>
        <h2>Carry Forward to GP069</h2>
        <p>{escape(next_step['owner_notebook_note'])}</p>
        <ul>{rules_html}</ul>
      </div>
    </section>

    <section class="section">
      <h2>GP068 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['record_route'])}</code>
        <code>{escape(routes['requirements_route'])}</code>
        <code>{escape(routes['policies_route'])}</code>
        <code>{escape(routes['blockers_route'])}</code>
        <code>{escape(routes['events_route'])}</code>
        <code>{escape(routes['validation_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp068_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_requirement_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="title">{escape(item['requirement_name'])}</div>
        <div class="meta">
          Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
          Category: <code>{escape(item['requirement_category'])}</code><br>
          Code: <code>{escape(item['requirement_code'])}</code><br>
          Read configured: <code>{str(item['read_path_configured']).lower()}</code><br>
          Body read: <code>{str(item['object_body_read']).lower()}</code>
        </div>
      </article>
    """


def _render_policy_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="title">{escape(item['policy_name'])}</div>
        <div class="meta">
          Category: <code>{escape(item['policy_category'])}</code><br>
          Code: <code>{escape(item['policy_code'])}</code><br>
          Read attempted: <code>{str(item['read_path_attempted']).lower()}</code><br>
          Export: <code>{str(item['export_enabled']).lower()}</code><br>
          Execution: <code>{str(item['execution_enabled']).lower()}</code>
        </div>
      </article>
    """
