"""
VAULT GIANT PACK 065 — Real Storage Provider Encryption Policy Contract

CURRENT SECTION:
Archive Vault — Real Storage Provider Configuration Layer
GP061-GP070

This pack creates a real durable encryption policy contract from the GP064
endpoint/namespace contract without configuring encryption or storing key material.

Purpose:
- Create a real SQLite-backed encryption policy contract schema.
- Persist a real contract record sourced from GP064.
- Persist real encryption requirement rows per provider candidate.
- Persist real key-management policy rows.
- Carry forward real blockers from GP064.
- Persist a real event log.
- Validate that no key material, KMS key ID, encryption setting, credential,
  provider connection, read/write path, export, or execution is enabled.

Important truth:
- GP065 creates the contract for encryption/key-management requirements.
- GP065 does not configure encryption.
- GP065 does not store key material or KMS key IDs.
- GP065 does not configure credentials or activate secret references.
- GP065 does not test provider connection.
- GP065 does not approve, activate, select, configure, read, write, export, or execute.
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

from vault.real_storage_provider_endpoint_namespace_contract_service import (
    DEFAULT_ENDPOINT_NAMESPACE_CONTRACT_ID,
    get_storage_provider_endpoint_namespace_blockers,
    get_storage_provider_endpoint_namespace_contract_record,
    get_storage_provider_endpoint_namespace_requirements,
)


PACK_ID = "VAULT_GP065"
PACK_NAME = "Real Storage Provider Encryption Policy Contract"
SCHEMA_VERSION = "vault.real_storage_provider_encryption_policy_contract.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
SECTION_TITLE = "Archive Vault — Real Storage Provider Configuration Layer"
SECTION_RANGE = "GP061-GP070"

NEXT_PACK = "VAULT_GP066_REAL_STORAGE_PROVIDER_CONNECTION_TEST_LOCK_CONTRACT"
NEXT_PACK_TITLE = "Real Storage Provider Connection Test Lock Contract"

DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID = "VSPEPC-GP065-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_encryption_policy_contract.sqlite"


ENCRYPTION_REQUIREMENT_SPECS = [
    {
        "requirement_code": "encryption_at_rest_policy_required",
        "requirement_name": "Encryption-at-rest policy required",
        "requirement_category": "encryption_at_rest",
        "requirement_message": "Future storage must define encryption-at-rest policy before any write path can be enabled.",
    },
    {
        "requirement_code": "encryption_in_transit_policy_required",
        "requirement_name": "Encryption-in-transit policy required",
        "requirement_category": "encryption_in_transit",
        "requirement_message": "Future storage must define encryption-in-transit policy before any connection can be tested.",
    },
    {
        "requirement_code": "key_management_alias_required",
        "requirement_name": "Key management alias required",
        "requirement_category": "key_management",
        "requirement_message": "Future key-management configuration must use approved aliases before any key reference can be configured.",
    },
    {
        "requirement_code": "kms_boundary_required",
        "requirement_name": "KMS boundary required",
        "requirement_category": "key_boundary",
        "requirement_message": "Future provider configuration must define a KMS/key boundary without storing KMS key IDs here.",
    },
    {
        "requirement_code": "rotation_policy_required",
        "requirement_name": "Rotation policy required",
        "requirement_category": "key_lifecycle",
        "requirement_message": "Future key usage requires a rotation policy before provider configuration.",
    },
    {
        "requirement_code": "revocation_policy_required",
        "requirement_name": "Revocation policy required",
        "requirement_category": "key_lifecycle",
        "requirement_message": "Future key usage requires a revocation policy before provider configuration.",
    },
    {
        "requirement_code": "algorithm_policy_required",
        "requirement_name": "Algorithm policy required",
        "requirement_category": "algorithm_policy",
        "requirement_message": "Future encryption configuration must define an approved algorithm policy before use.",
    },
    {
        "requirement_code": "provider_default_encryption_review_required",
        "requirement_name": "Provider default encryption review required",
        "requirement_category": "provider_default_review",
        "requirement_message": "Future provider default encryption must be reviewed before any endpoint/namespace activation.",
    },
]


ENCRYPTION_POLICIES = [
    {
        "policy_code": "no_key_material_storage",
        "policy_name": "No key material storage",
        "policy_category": "key_safety",
        "policy_message": "This contract may store requirement metadata only, not key material.",
    },
    {
        "policy_code": "no_kms_key_id_storage",
        "policy_name": "No KMS key ID storage",
        "policy_category": "key_safety",
        "policy_message": "This contract may store key aliases only, not KMS key IDs or live key locators.",
    },
    {
        "policy_code": "no_encryption_enablement_from_contract",
        "policy_name": "No encryption enablement from contract",
        "policy_category": "encryption_lock",
        "policy_message": "This contract cannot enable encryption or set provider encryption configuration.",
    },
    {
        "policy_code": "tower_encryption_review_required",
        "policy_name": "Tower encryption review required",
        "policy_category": "tower_gate",
        "policy_message": "Tower review is required before encryption/key-management values may be configured later.",
    },
    {
        "policy_code": "no_customer_managed_key_configuration",
        "policy_name": "No customer-managed key configuration",
        "policy_category": "key_configuration_lock",
        "policy_message": "Customer-managed keys cannot be configured from this contract.",
    },
    {
        "policy_code": "no_provider_managed_key_configuration",
        "policy_name": "No provider-managed key configuration",
        "policy_category": "key_configuration_lock",
        "policy_message": "Provider-managed encryption cannot be configured from this contract.",
    },
    {
        "policy_code": "owner_redacted_key_view_only",
        "policy_name": "Owner redacted key view only",
        "policy_category": "redaction",
        "policy_message": "Owner-facing key/encryption views must remain redacted and non-operational.",
    },
    {
        "policy_code": "no_connection_test_from_encryption_contract",
        "policy_name": "No connection test from encryption contract",
        "policy_category": "connection_lock",
        "policy_message": "This contract cannot test provider connectivity.",
    },
    {
        "policy_code": "no_export_from_encryption_contract",
        "policy_name": "No export from encryption contract",
        "policy_category": "export_lock",
        "policy_message": "This contract cannot unlock external delivery or export.",
    },
    {
        "policy_code": "no_execution_from_encryption_contract",
        "policy_name": "No execution from encryption contract",
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


def ensure_storage_provider_encryption_policy_contract_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_encryption_policy_contracts (
                encryption_policy_contract_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_endpoint_namespace_contract_id TEXT NOT NULL,
                source_endpoint_namespace_pack_id TEXT NOT NULL,
                contract_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                contract_data_json TEXT NOT NULL,
                encryption_policy_contract_ready INTEGER NOT NULL DEFAULT 1,
                encryption_requirements_ready INTEGER NOT NULL DEFAULT 1,
                key_management_policy_ready INTEGER NOT NULL DEFAULT 1,
                encryption_policy_alias_only INTEGER NOT NULL DEFAULT 1,
                key_alias_only INTEGER NOT NULL DEFAULT 1,
                key_material_stored INTEGER NOT NULL DEFAULT 0,
                kms_key_id_stored INTEGER NOT NULL DEFAULT 0,
                key_locator_present INTEGER NOT NULL DEFAULT 0,
                encryption_policy_configured INTEGER NOT NULL DEFAULT 0,
                encryption_algorithm_configured INTEGER NOT NULL DEFAULT 0,
                encryption_at_rest_configured INTEGER NOT NULL DEFAULT 0,
                encryption_in_transit_configured INTEGER NOT NULL DEFAULT 0,
                customer_managed_key_configured INTEGER NOT NULL DEFAULT 0,
                provider_managed_key_configured INTEGER NOT NULL DEFAULT 0,
                actual_secret_values_stored INTEGER NOT NULL DEFAULT 0,
                secret_values_present INTEGER NOT NULL DEFAULT 0,
                token_material_present INTEGER NOT NULL DEFAULT 0,
                encrypted_secret_payload_present INTEGER NOT NULL DEFAULT 0,
                secret_references_created INTEGER NOT NULL DEFAULT 0,
                secret_references_activated INTEGER NOT NULL DEFAULT 0,
                credentials_configured INTEGER NOT NULL DEFAULT 0,
                provider_endpoint_configured INTEGER NOT NULL DEFAULT 0,
                storage_container_configured INTEGER NOT NULL DEFAULT 0,
                namespace_configured INTEGER NOT NULL DEFAULT 0,
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
                provider_connection_tested INTEGER NOT NULL DEFAULT 0,
                risk_accepted INTEGER NOT NULL DEFAULT 0,
                risk_waived INTEGER NOT NULL DEFAULT 0,
                mitigation_approved INTEGER NOT NULL DEFAULT 0,
                official_storage_receipt INTEGER NOT NULL DEFAULT 0,
                finalized_storage_receipt INTEGER NOT NULL DEFAULT 0,
                closed_storage_receipt INTEGER NOT NULL DEFAULT 0,
                object_body_view_enabled INTEGER NOT NULL DEFAULT 0,
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_encryption_requirements (
                encryption_requirement_id TEXT PRIMARY KEY,
                encryption_policy_contract_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                requirement_code TEXT NOT NULL,
                requirement_name TEXT NOT NULL,
                requirement_category TEXT NOT NULL,
                requirement_message TEXT NOT NULL,
                requirement_status TEXT NOT NULL,
                requirement_required INTEGER NOT NULL DEFAULT 1,
                requirement_verified INTEGER NOT NULL DEFAULT 0,
                encryption_policy_alias_only INTEGER NOT NULL DEFAULT 1,
                key_alias_only INTEGER NOT NULL DEFAULT 1,
                key_material_stored INTEGER NOT NULL DEFAULT 0,
                kms_key_id_stored INTEGER NOT NULL DEFAULT 0,
                key_locator_present INTEGER NOT NULL DEFAULT 0,
                encryption_policy_configured INTEGER NOT NULL DEFAULT 0,
                encryption_algorithm_configured INTEGER NOT NULL DEFAULT 0,
                encryption_at_rest_configured INTEGER NOT NULL DEFAULT 0,
                encryption_in_transit_configured INTEGER NOT NULL DEFAULT 0,
                customer_managed_key_configured INTEGER NOT NULL DEFAULT 0,
                provider_managed_key_configured INTEGER NOT NULL DEFAULT 0,
                credentials_configured INTEGER NOT NULL DEFAULT 0,
                secret_references_activated INTEGER NOT NULL DEFAULT 0,
                provider_endpoint_configured INTEGER NOT NULL DEFAULT 0,
                storage_container_configured INTEGER NOT NULL DEFAULT 0,
                namespace_configured INTEGER NOT NULL DEFAULT 0,
                provider_connection_tested INTEGER NOT NULL DEFAULT 0,
                provider_read_enabled INTEGER NOT NULL DEFAULT 0,
                provider_write_enabled INTEGER NOT NULL DEFAULT 0,
                object_body_view_enabled INTEGER NOT NULL DEFAULT 0,
                direct_upload_enabled INTEGER NOT NULL DEFAULT 0,
                export_enabled INTEGER NOT NULL DEFAULT 0,
                execution_enabled INTEGER NOT NULL DEFAULT 0,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_granted INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(encryption_policy_contract_id)
                    REFERENCES vault_storage_provider_encryption_policy_contracts(encryption_policy_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(encryption_policy_contract_id, provider_candidate_id, requirement_code)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_encryption_policies (
                encryption_policy_id TEXT PRIMARY KEY,
                encryption_policy_contract_id TEXT NOT NULL,
                policy_code TEXT NOT NULL,
                policy_name TEXT NOT NULL,
                policy_category TEXT NOT NULL,
                policy_message TEXT NOT NULL,
                policy_status TEXT NOT NULL,
                policy_required INTEGER NOT NULL DEFAULT 1,
                policy_verified INTEGER NOT NULL DEFAULT 0,
                key_material_stored INTEGER NOT NULL DEFAULT 0,
                kms_key_id_stored INTEGER NOT NULL DEFAULT 0,
                key_locator_present INTEGER NOT NULL DEFAULT 0,
                encryption_policy_configured INTEGER NOT NULL DEFAULT 0,
                encryption_algorithm_configured INTEGER NOT NULL DEFAULT 0,
                encryption_at_rest_configured INTEGER NOT NULL DEFAULT 0,
                encryption_in_transit_configured INTEGER NOT NULL DEFAULT 0,
                customer_managed_key_configured INTEGER NOT NULL DEFAULT 0,
                provider_managed_key_configured INTEGER NOT NULL DEFAULT 0,
                actual_secret_values_stored INTEGER NOT NULL DEFAULT 0,
                secret_values_present INTEGER NOT NULL DEFAULT 0,
                token_material_present INTEGER NOT NULL DEFAULT 0,
                secret_references_created INTEGER NOT NULL DEFAULT 0,
                secret_references_activated INTEGER NOT NULL DEFAULT 0,
                credentials_configured INTEGER NOT NULL DEFAULT 0,
                provider_connection_tested INTEGER NOT NULL DEFAULT 0,
                provider_read_enabled INTEGER NOT NULL DEFAULT 0,
                provider_write_enabled INTEGER NOT NULL DEFAULT 0,
                object_body_view_enabled INTEGER NOT NULL DEFAULT 0,
                export_enabled INTEGER NOT NULL DEFAULT 0,
                execution_enabled INTEGER NOT NULL DEFAULT 0,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_granted INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(encryption_policy_contract_id)
                    REFERENCES vault_storage_provider_encryption_policy_contracts(encryption_policy_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(encryption_policy_contract_id, policy_code)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_encryption_blockers (
                encryption_blocker_id TEXT PRIMARY KEY,
                encryption_policy_contract_id TEXT NOT NULL,
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
                FOREIGN KEY(encryption_policy_contract_id)
                    REFERENCES vault_storage_provider_encryption_policy_contracts(encryption_policy_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(encryption_policy_contract_id, source_endpoint_namespace_blocker_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_encryption_events (
                event_id TEXT PRIMARY KEY,
                encryption_policy_contract_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(encryption_policy_contract_id)
                    REFERENCES vault_storage_provider_encryption_policy_contracts(encryption_policy_contract_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_encryption_requirements_contract
            ON vault_storage_provider_encryption_requirements(encryption_policy_contract_id, provider_candidate_id, requirement_category)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_encryption_blockers_contract
            ON vault_storage_provider_encryption_blockers(encryption_policy_contract_id, provider_candidate_id, blocker_category)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_encryption_events_contract
            ON vault_storage_provider_encryption_events(encryption_policy_contract_id, created_at)
            """
        )
        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "tables": [
            "vault_storage_provider_encryption_policy_contracts",
            "vault_storage_provider_encryption_requirements",
            "vault_storage_provider_encryption_policies",
            "vault_storage_provider_encryption_blockers",
            "vault_storage_provider_encryption_events",
        ],
        "real_sqlite_backed": True,
    }


def initialize_real_storage_provider_encryption_policy_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_encryption_policy_contract_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            """
            SELECT encryption_policy_contract_id
            FROM vault_storage_provider_encryption_policy_contracts
            WHERE encryption_policy_contract_id = ?
            """,
            (DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,),
        ).fetchone()

        if existing is None:
            endpoint_contract = get_storage_provider_endpoint_namespace_contract_record()["endpoint_namespace_contract"]
            requirements_payload = get_storage_provider_endpoint_namespace_requirements()
            blockers_payload = get_storage_provider_endpoint_namespace_blockers()
            endpoint_requirements = requirements_payload["requirements"]
            blockers = blockers_payload["blockers"]
            candidates = _unique_provider_candidates(endpoint_requirements)
            contract_data = _build_contract_data(endpoint_contract, requirements_payload, blockers_payload, candidates)
            now = _now_iso()

            _insert_dict(
                conn,
                "vault_storage_provider_encryption_policy_contracts",
                {
                    "encryption_policy_contract_id": DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,
                    "pack_id": PACK_ID,
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    "source_endpoint_namespace_contract_id": endpoint_contract["endpoint_namespace_contract_id"],
                    "source_endpoint_namespace_pack_id": endpoint_contract["pack_id"],
                    "contract_status": "REAL_ENCRYPTION_POLICY_CONTRACT_OPEN_ALIAS_ONLY_TOWER_LOCKED",
                    "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    "contract_data_json": _json_dumps(contract_data),
                    "encryption_policy_contract_ready": 1,
                    "encryption_requirements_ready": 1,
                    "key_management_policy_ready": 1,
                    "encryption_policy_alias_only": 1,
                    "key_alias_only": 1,
                    "key_material_stored": 0,
                    "kms_key_id_stored": 0,
                    "key_locator_present": 0,
                    "encryption_policy_configured": 0,
                    "encryption_algorithm_configured": 0,
                    "encryption_at_rest_configured": 0,
                    "encryption_in_transit_configured": 0,
                    "customer_managed_key_configured": 0,
                    "provider_managed_key_configured": 0,
                    "actual_secret_values_stored": 0,
                    "secret_values_present": 0,
                    "token_material_present": 0,
                    "encrypted_secret_payload_present": 0,
                    "secret_references_created": 0,
                    "secret_references_activated": 0,
                    "credentials_configured": 0,
                    "provider_endpoint_configured": 0,
                    "storage_container_configured": 0,
                    "namespace_configured": 0,
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
                    "provider_connection_tested": 0,
                    "risk_accepted": 0,
                    "risk_waived": 0,
                    "mitigation_approved": 0,
                    "official_storage_receipt": 0,
                    "finalized_storage_receipt": 0,
                    "closed_storage_receipt": 0,
                    "object_body_view_enabled": 0,
                    "direct_upload_enabled": 0,
                    "export_enabled": 0,
                    "execution_enabled": 0,
                    "vault_done": 0,
                    "created_at": now,
                    "updated_at": now,
                },
            )

            for candidate in candidates:
                for requirement in ENCRYPTION_REQUIREMENT_SPECS:
                    _insert_requirement(conn, DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID, candidate, requirement, now)

            for policy in ENCRYPTION_POLICIES:
                _insert_policy(conn, DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID, policy, now)

            for blocker in blockers:
                _insert_blocker(conn, DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID, blocker, now)

            requirement_counts = _get_requirement_counts(conn, DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID)
            policy_counts = _get_policy_counts(conn, DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID)
            blocker_counts = _get_blocker_counts(conn, DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID)

            _insert_event(
                conn,
                DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,
                "REAL_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT_CREATED",
                {
                    "pack_id": PACK_ID,
                    "source_endpoint_namespace_contract_id": endpoint_contract["endpoint_namespace_contract_id"],
                    "source_endpoint_namespace_pack_id": endpoint_contract["pack_id"],
                    "real_sqlite_backed": True,
                    "encryption_policy_contract_ready": True,
                    "key_alias_only": True,
                    "key_material_stored": False,
                    "kms_key_id_stored": False,
                    "encryption_policy_configured": False,
                    "encryption_at_rest_configured": False,
                    "encryption_in_transit_configured": False,
                    "vault_done": False,
                },
            )
            _insert_event(
                conn,
                DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,
                "SOURCE_GP064_ENDPOINT_NAMESPACE_CONTRACT_ATTACHED",
                _compact_endpoint_source_snapshot(endpoint_contract, requirements_payload, blockers_payload),
            )
            _insert_event(
                conn,
                DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,
                "REAL_ENCRYPTION_REQUIREMENTS_CREATED_ALIAS_ONLY",
                requirement_counts,
            )
            _insert_event(
                conn,
                DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,
                "REAL_KEY_MANAGEMENT_POLICIES_CREATED",
                policy_counts,
            )
            _insert_event(
                conn,
                DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,
                "REAL_ENCRYPTION_BLOCKERS_CARRIED_FORWARD",
                blocker_counts,
            )
            _insert_event(
                conn,
                DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,
                "ENCRYPTION_POLICY_LOCKS_CONFIRMED",
                {
                    "no_key_material_stored": True,
                    "no_kms_key_id_stored": True,
                    "no_key_locator_present": True,
                    "no_encryption_policy_configured": True,
                    "no_encryption_algorithm_configured": True,
                    "no_encryption_at_rest_configured": True,
                    "no_encryption_in_transit_configured": True,
                    "no_customer_managed_key_configured": True,
                    "no_provider_managed_key_configured": True,
                    "no_secret_reference_activation": True,
                    "no_credential_configuration": True,
                    "provider_read_write_blocked": True,
                    "provider_connection_test_blocked": True,
                    "object_body_view_blocked": True,
                    "export_blocked": True,
                    "execution_blocked": True,
                },
            )
            conn.commit()

    counts = _get_counts(path)
    return {
        "initialized": True,
        "schema": schema,
        "encryption_policy_contract_id": DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,
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
        f"VSPER-{candidate['provider_candidate_id'].replace('VSPC-', '')}-"
        f"{requirement['requirement_code'].upper().replace('_', '-')}"
    )
    _insert_dict(
        conn,
        "vault_storage_provider_encryption_requirements",
        {
            "encryption_requirement_id": requirement_id,
            "encryption_policy_contract_id": contract_id,
            "provider_candidate_id": candidate["provider_candidate_id"],
            "requirement_code": requirement["requirement_code"],
            "requirement_name": requirement["requirement_name"],
            "requirement_category": requirement["requirement_category"],
            "requirement_message": requirement["requirement_message"],
            "requirement_status": "REAL_ENCRYPTION_REQUIREMENT_RECORDED_ALIAS_ONLY_TOWER_LOCKED",
            "requirement_required": 1,
            "requirement_verified": 0,
            "encryption_policy_alias_only": 1,
            "key_alias_only": 1,
            "key_material_stored": 0,
            "kms_key_id_stored": 0,
            "key_locator_present": 0,
            "encryption_policy_configured": 0,
            "encryption_algorithm_configured": 0,
            "encryption_at_rest_configured": 0,
            "encryption_in_transit_configured": 0,
            "customer_managed_key_configured": 0,
            "provider_managed_key_configured": 0,
            "credentials_configured": 0,
            "secret_references_activated": 0,
            "provider_endpoint_configured": 0,
            "storage_container_configured": 0,
            "namespace_configured": 0,
            "provider_connection_tested": 0,
            "provider_read_enabled": 0,
            "provider_write_enabled": 0,
            "object_body_view_enabled": 0,
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
    policy_id = f"VSPEP-{policy['policy_code'].upper().replace('_', '-')}"
    _insert_dict(
        conn,
        "vault_storage_provider_encryption_policies",
        {
            "encryption_policy_id": policy_id,
            "encryption_policy_contract_id": contract_id,
            "policy_code": policy["policy_code"],
            "policy_name": policy["policy_name"],
            "policy_category": policy["policy_category"],
            "policy_message": policy["policy_message"],
            "policy_status": "REAL_ENCRYPTION_POLICY_RECORDED_TOWER_LOCKED",
            "policy_required": 1,
            "policy_verified": 0,
            "key_material_stored": 0,
            "kms_key_id_stored": 0,
            "key_locator_present": 0,
            "encryption_policy_configured": 0,
            "encryption_algorithm_configured": 0,
            "encryption_at_rest_configured": 0,
            "encryption_in_transit_configured": 0,
            "customer_managed_key_configured": 0,
            "provider_managed_key_configured": 0,
            "actual_secret_values_stored": 0,
            "secret_values_present": 0,
            "token_material_present": 0,
            "secret_references_created": 0,
            "secret_references_activated": 0,
            "credentials_configured": 0,
            "provider_connection_tested": 0,
            "provider_read_enabled": 0,
            "provider_write_enabled": 0,
            "object_body_view_enabled": 0,
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
    blocker_id = f"VSPEB-{blocker['endpoint_namespace_blocker_id'].replace('VSPENB-', '')}"
    _insert_dict(
        conn,
        "vault_storage_provider_encryption_blockers",
        {
            "encryption_blocker_id": blocker_id,
            "encryption_policy_contract_id": contract_id,
            "source_endpoint_namespace_blocker_id": blocker["endpoint_namespace_blocker_id"],
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
            "blocker_status": "REAL_ENCRYPTION_BLOCKER_ACTIVE_CARRIED_FROM_GP064",
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
    event_id = f"VSPEEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_storage_provider_encryption_events",
        {
            "event_id": event_id,
            "encryption_policy_contract_id": contract_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id


def _get_counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        contract_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_encryption_policy_contracts").fetchone()["c"]
        requirement_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_encryption_requirements").fetchone()["c"]
        policy_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_encryption_policies").fetchone()["c"]
        blocker_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_encryption_blockers").fetchone()["c"]
        event_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_encryption_events").fetchone()["c"]

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
            SUM(CASE WHEN encryption_policy_alias_only = 1 THEN 1 ELSE 0 END) AS encryption_policy_alias_only_count,
            SUM(CASE WHEN key_alias_only = 1 THEN 1 ELSE 0 END) AS key_alias_only_count,
            SUM(CASE WHEN key_material_stored = 1 THEN 1 ELSE 0 END) AS key_material_stored_count,
            SUM(CASE WHEN kms_key_id_stored = 1 THEN 1 ELSE 0 END) AS kms_key_id_stored_count,
            SUM(CASE WHEN key_locator_present = 1 THEN 1 ELSE 0 END) AS key_locator_present_count,
            SUM(CASE WHEN encryption_policy_configured = 1 THEN 1 ELSE 0 END) AS encryption_policy_configured_count,
            SUM(CASE WHEN encryption_algorithm_configured = 1 THEN 1 ELSE 0 END) AS encryption_algorithm_configured_count,
            SUM(CASE WHEN encryption_at_rest_configured = 1 THEN 1 ELSE 0 END) AS encryption_at_rest_configured_count,
            SUM(CASE WHEN encryption_in_transit_configured = 1 THEN 1 ELSE 0 END) AS encryption_in_transit_configured_count,
            SUM(CASE WHEN customer_managed_key_configured = 1 THEN 1 ELSE 0 END) AS customer_managed_key_configured_count,
            SUM(CASE WHEN provider_managed_key_configured = 1 THEN 1 ELSE 0 END) AS provider_managed_key_configured_count,
            SUM(CASE WHEN credentials_configured = 1 THEN 1 ELSE 0 END) AS credentials_configured_count,
            SUM(CASE WHEN secret_references_activated = 1 THEN 1 ELSE 0 END) AS secret_references_activated_count,
            SUM(CASE WHEN provider_endpoint_configured = 1 THEN 1 ELSE 0 END) AS provider_endpoint_configured_count,
            SUM(CASE WHEN storage_container_configured = 1 THEN 1 ELSE 0 END) AS storage_container_configured_count,
            SUM(CASE WHEN namespace_configured = 1 THEN 1 ELSE 0 END) AS namespace_configured_count,
            SUM(CASE WHEN provider_connection_tested = 1 THEN 1 ELSE 0 END) AS provider_connection_tested_count,
            SUM(CASE WHEN provider_read_enabled = 1 THEN 1 ELSE 0 END) AS provider_read_enabled_count,
            SUM(CASE WHEN provider_write_enabled = 1 THEN 1 ELSE 0 END) AS provider_write_enabled_count,
            SUM(CASE WHEN object_body_view_enabled = 1 THEN 1 ELSE 0 END) AS object_body_view_enabled_count,
            SUM(CASE WHEN direct_upload_enabled = 1 THEN 1 ELSE 0 END) AS direct_upload_enabled_count,
            SUM(CASE WHEN export_enabled = 1 THEN 1 ELSE 0 END) AS export_enabled_count,
            SUM(CASE WHEN execution_enabled = 1 THEN 1 ELSE 0 END) AS execution_enabled_count,
            SUM(CASE WHEN tower_review_required = 1 THEN 1 ELSE 0 END) AS tower_review_required_count,
            SUM(CASE WHEN tower_review_granted = 1 THEN 1 ELSE 0 END) AS tower_review_granted_count
        FROM vault_storage_provider_encryption_requirements
        WHERE encryption_policy_contract_id = ?
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
            SUM(CASE WHEN key_material_stored = 1 THEN 1 ELSE 0 END) AS key_material_stored_count,
            SUM(CASE WHEN kms_key_id_stored = 1 THEN 1 ELSE 0 END) AS kms_key_id_stored_count,
            SUM(CASE WHEN key_locator_present = 1 THEN 1 ELSE 0 END) AS key_locator_present_count,
            SUM(CASE WHEN encryption_policy_configured = 1 THEN 1 ELSE 0 END) AS encryption_policy_configured_count,
            SUM(CASE WHEN encryption_algorithm_configured = 1 THEN 1 ELSE 0 END) AS encryption_algorithm_configured_count,
            SUM(CASE WHEN encryption_at_rest_configured = 1 THEN 1 ELSE 0 END) AS encryption_at_rest_configured_count,
            SUM(CASE WHEN encryption_in_transit_configured = 1 THEN 1 ELSE 0 END) AS encryption_in_transit_configured_count,
            SUM(CASE WHEN customer_managed_key_configured = 1 THEN 1 ELSE 0 END) AS customer_managed_key_configured_count,
            SUM(CASE WHEN provider_managed_key_configured = 1 THEN 1 ELSE 0 END) AS provider_managed_key_configured_count,
            SUM(CASE WHEN actual_secret_values_stored = 1 THEN 1 ELSE 0 END) AS actual_secret_values_stored_count,
            SUM(CASE WHEN secret_values_present = 1 THEN 1 ELSE 0 END) AS secret_values_present_count,
            SUM(CASE WHEN token_material_present = 1 THEN 1 ELSE 0 END) AS token_material_present_count,
            SUM(CASE WHEN secret_references_created = 1 THEN 1 ELSE 0 END) AS secret_references_created_count,
            SUM(CASE WHEN secret_references_activated = 1 THEN 1 ELSE 0 END) AS secret_references_activated_count,
            SUM(CASE WHEN credentials_configured = 1 THEN 1 ELSE 0 END) AS credentials_configured_count,
            SUM(CASE WHEN provider_connection_tested = 1 THEN 1 ELSE 0 END) AS provider_connection_tested_count,
            SUM(CASE WHEN provider_read_enabled = 1 THEN 1 ELSE 0 END) AS provider_read_enabled_count,
            SUM(CASE WHEN provider_write_enabled = 1 THEN 1 ELSE 0 END) AS provider_write_enabled_count,
            SUM(CASE WHEN object_body_view_enabled = 1 THEN 1 ELSE 0 END) AS object_body_view_enabled_count,
            SUM(CASE WHEN export_enabled = 1 THEN 1 ELSE 0 END) AS export_enabled_count,
            SUM(CASE WHEN execution_enabled = 1 THEN 1 ELSE 0 END) AS execution_enabled_count,
            SUM(CASE WHEN tower_review_required = 1 THEN 1 ELSE 0 END) AS tower_review_required_count,
            SUM(CASE WHEN tower_review_granted = 1 THEN 1 ELSE 0 END) AS tower_review_granted_count
        FROM vault_storage_provider_encryption_policies
        WHERE encryption_policy_contract_id = ?
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
        FROM vault_storage_provider_encryption_blockers
        WHERE encryption_policy_contract_id = ?
        """,
        (contract_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _compact_endpoint_source_snapshot(endpoint_contract, requirements_payload, blockers_payload):
    return {
        "source_endpoint_namespace_contract_id": endpoint_contract["endpoint_namespace_contract_id"],
        "source_endpoint_namespace_pack_id": endpoint_contract["pack_id"],
        "source_contract_status": endpoint_contract["contract_status"],
        "source_section": endpoint_contract["section_id"],
        "source_section_range": endpoint_contract["section_range"],
        "endpoint_namespace_contract_ready": endpoint_contract["endpoint_namespace_contract_ready"],
        "endpoint_alias_only": endpoint_contract["endpoint_alias_only"],
        "namespace_alias_only": endpoint_contract["namespace_alias_only"],
        "requirement_count": requirements_payload["requirement_count"],
        "provider_candidate_count": requirements_payload["provider_candidate_count"],
        "requirement_code_count": requirements_payload["requirement_code_count"],
        "provider_endpoint_configured_count": requirements_payload["provider_endpoint_configured_count"],
        "storage_container_configured_count": requirements_payload["storage_container_configured_count"],
        "namespace_configured_count": requirements_payload["namespace_configured_count"],
        "blocker_count": blockers_payload["blocker_count"],
        "blocks_provider_configuration_count": blockers_payload["blocks_provider_configuration_count"],
        "blocks_provider_read_write_count": blockers_payload["blocks_provider_read_write_count"],
        "blocks_object_body_view_count": blockers_payload["blocks_object_body_view_count"],
        "blocks_export_count": blockers_payload["blocks_export_count"],
        "blocks_execution_count": blockers_payload["blocks_execution_count"],
        "provider_configured": endpoint_contract["provider_configured"],
        "provider_connection_tested": endpoint_contract["provider_connection_tested"],
        "export_enabled": endpoint_contract["export_enabled"],
        "execution_enabled": endpoint_contract["execution_enabled"],
        "vault_done": endpoint_contract["vault_done"],
    }


def _build_contract_data(endpoint_contract, requirements_payload, blockers_payload, candidates):
    return {
        "encryption_policy_schema_version": SCHEMA_VERSION,
        "contract_type": "REAL_STORAGE_PROVIDER_ENCRYPTION_POLICY_CONTRACT",
        "contract_status": "REAL_ENCRYPTION_POLICY_CONTRACT_OPEN_ALIAS_ONLY_TOWER_LOCKED",
        "real_durable_encryption_policy_contract": True,
        "metadata_source": "VAULT_GP064_REAL_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT",
        "source_endpoint_namespace_contract_id": endpoint_contract["endpoint_namespace_contract_id"],
        "source_endpoint_namespace_pack_id": endpoint_contract["pack_id"],
        "current_section": {
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "provider_candidate_count": len(candidates),
        "requirement_code_count": len(ENCRYPTION_REQUIREMENT_SPECS),
        "requirement_count": len(candidates) * len(ENCRYPTION_REQUIREMENT_SPECS),
        "policy_count": len(ENCRYPTION_POLICIES),
        "carried_blocker_count": blockers_payload["blocker_count"],
        "encryption_requirements": ENCRYPTION_REQUIREMENT_SPECS,
        "encryption_policies": ENCRYPTION_POLICIES,
        "encryption_truth": {
            "encryption_policy_contract_ready": True,
            "encryption_requirements_ready": True,
            "key_management_policy_ready": True,
            "encryption_policy_alias_only": True,
            "key_alias_only": True,
            "key_material_stored": False,
            "kms_key_id_stored": False,
            "key_locator_present": False,
            "encryption_policy_configured": False,
            "encryption_algorithm_configured": False,
            "encryption_at_rest_configured": False,
            "encryption_in_transit_configured": False,
            "customer_managed_key_configured": False,
            "provider_managed_key_configured": False,
        },
        "secret_and_provider_truth": {
            "actual_secret_values_stored": False,
            "secret_values_present": False,
            "token_material_present": False,
            "encrypted_secret_payload_present": False,
            "secret_references_created": False,
            "secret_references_activated": False,
            "credentials_configured": False,
            "provider_endpoint_configured": False,
            "storage_container_configured": False,
            "namespace_configured": False,
            "provider_approval_ready": False,
            "provider_activation_ready": False,
            "provider_configuration_ready": False,
            "provider_read_write_ready": False,
            "provider_approved": False,
            "provider_activated": False,
            "provider_recommended": False,
            "provider_selected": False,
            "provider_configured": False,
            "provider_read_enabled": False,
            "provider_write_enabled": False,
            "provider_object_read_claimed": False,
            "provider_connection_tested": False,
            "object_body_view_enabled": False,
            "direct_upload_enabled": False,
            "export_enabled": False,
            "execution_enabled": False,
            "vault_done": False,
        },
        "blocker_summary": {
            "blocks_provider_approval_count": blockers_payload["blocks_provider_approval_count"],
            "blocks_provider_activation_count": blockers_payload["blocks_provider_activation_count"],
            "blocks_provider_selection_count": blockers_payload["blocks_provider_selection_count"],
            "blocks_provider_configuration_count": blockers_payload["blocks_provider_configuration_count"],
            "blocks_provider_read_write_count": blockers_payload["blocks_provider_read_write_count"],
            "blocks_object_body_view_count": blockers_payload["blocks_object_body_view_count"],
            "blocks_export_count": blockers_payload["blocks_export_count"],
            "blocks_execution_count": blockers_payload["blocks_execution_count"],
            "tower_review_granted_count": blockers_payload["tower_review_granted_count"],
            "resolved_count": blockers_payload["resolved_count"],
        },
        "next_pack": NEXT_PACK,
        "next_pack_title": NEXT_PACK_TITLE,
        "safe_to_continue_to_gp066": True,
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


def get_storage_provider_encryption_policy_contract_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_encryption_policy_contract(db_path)

    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_encryption_policy_contracts
            WHERE encryption_policy_contract_id = ?
            """,
            (DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Real storage provider encryption policy contract was not initialized.")

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "encryption_policy_contract": _boolify_row(row, {"contract_data_json": "contract_data"}),
    }


def get_storage_provider_encryption_requirements(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_encryption_policy_contract(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_encryption_requirements
            WHERE encryption_policy_contract_id = ?
            ORDER BY provider_candidate_id ASC, requirement_category ASC, requirement_code ASC
            """,
            (DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,),
        ).fetchall()
        counts = _get_requirement_counts(conn, DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID)

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "requirements": [_boolify_row(row) for row in rows],
    }


def get_storage_provider_encryption_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_encryption_policy_contract(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_encryption_policies
            WHERE encryption_policy_contract_id = ?
            ORDER BY policy_category ASC, policy_code ASC
            """,
            (DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,),
        ).fetchall()
        counts = _get_policy_counts(conn, DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID)

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "policies": [_boolify_row(row) for row in rows],
    }


def get_storage_provider_encryption_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_encryption_policy_contract(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_encryption_blockers
            WHERE encryption_policy_contract_id = ?
            ORDER BY provider_candidate_id ASC, blocker_category ASC, blocker_code ASC
            """,
            (DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,),
        ).fetchall()
        counts = _get_blocker_counts(conn, DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID)

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "blockers": [_boolify_row(row) for row in rows],
    }


def get_storage_provider_encryption_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_encryption_policy_contract(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_encryption_events
            WHERE encryption_policy_contract_id = ?
            ORDER BY created_at ASC, event_id ASC
            """,
            (DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,),
        ).fetchall()

    events = []
    for row in rows:
        events.append(
            {
                "event_id": row["event_id"],
                "encryption_policy_contract_id": row["encryption_policy_contract_id"],
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


def record_storage_provider_encryption_event(
    event_type: str,
    event_payload: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    initialize_real_storage_provider_encryption_policy_contract(db_path)
    payload = dict(event_payload or {})
    payload.update(
        {
            "write_type": "REAL_STORAGE_PROVIDER_ENCRYPTION_EVENT",
            "encryption_policy_contract_ready": True,
            "encryption_policy_alias_only": True,
            "key_alias_only": True,
            "key_material_stored": False,
            "kms_key_id_stored": False,
            "key_locator_present": False,
            "encryption_policy_configured": False,
            "encryption_algorithm_configured": False,
            "encryption_at_rest_configured": False,
            "encryption_in_transit_configured": False,
            "customer_managed_key_configured": False,
            "provider_managed_key_configured": False,
            "actual_secret_values_stored": False,
            "secret_values_present": False,
            "token_material_present": False,
            "secret_references_created": False,
            "secret_references_activated": False,
            "credentials_configured": False,
            "provider_connection_tested": False,
            "provider_read_enabled": False,
            "provider_write_enabled": False,
            "export_enabled": False,
            "execution_enabled": False,
            "vault_done": False,
        }
    )

    with _connect(db_path) as conn:
        event_id = _insert_event(conn, DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID, event_type, payload)
        conn.commit()

    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "encryption_policy_contract_id": DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,
        "real_sqlite_backed": True,
        **payload,
    }


def validate_storage_provider_encryption_policy_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    contract = get_storage_provider_encryption_policy_contract_record(db_path)["encryption_policy_contract"]
    requirements = get_storage_provider_encryption_requirements(db_path)
    policies = get_storage_provider_encryption_policies(db_path)
    blockers = get_storage_provider_encryption_blockers(db_path)
    events = get_storage_provider_encryption_events(db_path)

    expected_requirements = 5 * len(ENCRYPTION_REQUIREMENT_SPECS)
    expected_policies = len(ENCRYPTION_POLICIES)
    expected_blockers = 140

    checks = [
        {"code": "REAL_SQLITE_ENCRYPTION_POLICY_CONTRACT_EXISTS", "passed": contract["encryption_policy_contract_id"] == DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID},
        {"code": "SOURCE_GP064_ENDPOINT_NAMESPACE_CONTRACT_ATTACHED", "passed": contract["source_endpoint_namespace_contract_id"] == DEFAULT_ENDPOINT_NAMESPACE_CONTRACT_ID},
        {"code": "ENCRYPTION_POLICY_CONTRACT_READY", "passed": contract["encryption_policy_contract_ready"] is True},
        {"code": "ENCRYPTION_REQUIREMENTS_READY", "passed": contract["encryption_requirements_ready"] is True},
        {"code": "KEY_MANAGEMENT_POLICY_READY", "passed": contract["key_management_policy_ready"] is True},
        {"code": "ENCRYPTION_POLICY_ALIAS_ONLY", "passed": contract["encryption_policy_alias_only"] is True},
        {"code": "KEY_ALIAS_ONLY", "passed": contract["key_alias_only"] is True},
        {"code": "REAL_ENCRYPTION_REQUIREMENTS_EXIST", "passed": requirements["requirement_count"] == expected_requirements},
        {"code": "ALL_REQUIREMENTS_REQUIRED", "passed": requirements["requirement_required_count"] == expected_requirements},
        {"code": "NO_REQUIREMENTS_VERIFIED_YET", "passed": requirements["requirement_verified_count"] == 0},
        {"code": "ALL_REQUIREMENTS_ENCRYPTION_ALIAS_ONLY", "passed": requirements["encryption_policy_alias_only_count"] == expected_requirements},
        {"code": "ALL_REQUIREMENTS_KEY_ALIAS_ONLY", "passed": requirements["key_alias_only_count"] == expected_requirements},
        {"code": "NO_REQUIREMENT_KEY_MATERIAL_STORED", "passed": requirements["key_material_stored_count"] == 0},
        {"code": "NO_REQUIREMENT_KMS_KEY_ID_STORED", "passed": requirements["kms_key_id_stored_count"] == 0},
        {"code": "NO_REQUIREMENT_KEY_LOCATOR_PRESENT", "passed": requirements["key_locator_present_count"] == 0},
        {"code": "NO_REQUIREMENT_ENCRYPTION_POLICY_CONFIGURED", "passed": requirements["encryption_policy_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_ENCRYPTION_ALGORITHM_CONFIGURED", "passed": requirements["encryption_algorithm_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_ENCRYPTION_AT_REST_CONFIGURED", "passed": requirements["encryption_at_rest_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_ENCRYPTION_IN_TRANSIT_CONFIGURED", "passed": requirements["encryption_in_transit_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_CUSTOMER_KEY_CONFIGURED", "passed": requirements["customer_managed_key_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_PROVIDER_KEY_CONFIGURED", "passed": requirements["provider_managed_key_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_CREDENTIALS_CONFIGURED", "passed": requirements["credentials_configured_count"] == 0},
        {"code": "NO_REQUIREMENT_SECRET_REFERENCES_ACTIVATED", "passed": requirements["secret_references_activated_count"] == 0},
        {"code": "NO_REQUIREMENT_PROVIDER_CONNECTION_TESTED", "passed": requirements["provider_connection_tested_count"] == 0},
        {"code": "NO_REQUIREMENT_READ_WRITE", "passed": requirements["provider_read_enabled_count"] == 0 and requirements["provider_write_enabled_count"] == 0},
        {"code": "NO_REQUIREMENT_OBJECT_BODY_VIEW", "passed": requirements["object_body_view_enabled_count"] == 0},
        {"code": "NO_REQUIREMENT_DIRECT_UPLOAD", "passed": requirements["direct_upload_enabled_count"] == 0},
        {"code": "NO_REQUIREMENT_EXPORT", "passed": requirements["export_enabled_count"] == 0},
        {"code": "NO_REQUIREMENT_EXECUTION", "passed": requirements["execution_enabled_count"] == 0},
        {"code": "NO_REQUIREMENT_TOWER_REVIEW_GRANTED", "passed": requirements["tower_review_granted_count"] == 0},
        {"code": "REAL_ENCRYPTION_POLICIES_EXIST", "passed": policies["policy_count"] == expected_policies},
        {"code": "ALL_POLICIES_REQUIRED", "passed": policies["policy_required_count"] == expected_policies},
        {"code": "NO_POLICIES_VERIFIED_YET", "passed": policies["policy_verified_count"] == 0},
        {"code": "NO_POLICY_KEY_MATERIAL_STORED", "passed": policies["key_material_stored_count"] == 0},
        {"code": "NO_POLICY_KMS_KEY_ID_STORED", "passed": policies["kms_key_id_stored_count"] == 0},
        {"code": "NO_POLICY_KEY_LOCATOR_PRESENT", "passed": policies["key_locator_present_count"] == 0},
        {"code": "NO_POLICY_ENCRYPTION_CONFIGURED", "passed": policies["encryption_policy_configured_count"] == 0},
        {"code": "NO_POLICY_ENCRYPTION_ALGORITHM_CONFIGURED", "passed": policies["encryption_algorithm_configured_count"] == 0},
        {"code": "NO_POLICY_ENCRYPTION_AT_REST_CONFIGURED", "passed": policies["encryption_at_rest_configured_count"] == 0},
        {"code": "NO_POLICY_ENCRYPTION_IN_TRANSIT_CONFIGURED", "passed": policies["encryption_in_transit_configured_count"] == 0},
        {"code": "NO_POLICY_CUSTOMER_KEY_CONFIGURED", "passed": policies["customer_managed_key_configured_count"] == 0},
        {"code": "NO_POLICY_PROVIDER_KEY_CONFIGURED", "passed": policies["provider_managed_key_configured_count"] == 0},
        {"code": "NO_POLICY_SECRETS_PRESENT", "passed": policies["secret_values_present_count"] == 0 and policies["token_material_present_count"] == 0},
        {"code": "NO_POLICY_SECRET_REFERENCES_CREATED", "passed": policies["secret_references_created_count"] == 0},
        {"code": "NO_POLICY_SECRET_REFERENCES_ACTIVATED", "passed": policies["secret_references_activated_count"] == 0},
        {"code": "NO_POLICY_CREDENTIALS_CONFIGURED", "passed": policies["credentials_configured_count"] == 0},
        {"code": "NO_POLICY_CONNECTION_TESTED", "passed": policies["provider_connection_tested_count"] == 0},
        {"code": "NO_POLICY_READ_WRITE", "passed": policies["provider_read_enabled_count"] == 0 and policies["provider_write_enabled_count"] == 0},
        {"code": "NO_POLICY_OBJECT_BODY_VIEW", "passed": policies["object_body_view_enabled_count"] == 0},
        {"code": "NO_POLICY_EXPORT", "passed": policies["export_enabled_count"] == 0},
        {"code": "NO_POLICY_EXECUTION", "passed": policies["execution_enabled_count"] == 0},
        {"code": "REAL_ENCRYPTION_BLOCKERS_CARRIED_FORWARD", "passed": blockers["blocker_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_PROVIDER_CONFIGURATION", "passed": blockers["blocks_provider_configuration_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_PROVIDER_READ_WRITE", "passed": blockers["blocks_provider_read_write_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_OBJECT_BODY_VIEW", "passed": blockers["blocks_object_body_view_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_EXPORT", "passed": blockers["blocks_export_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_EXECUTION", "passed": blockers["blocks_execution_count"] == expected_blockers},
        {"code": "NO_BLOCKERS_TOWER_REVIEW_GRANTED", "passed": blockers["tower_review_granted_count"] == 0},
        {"code": "NO_BLOCKERS_RESOLVED", "passed": blockers["resolved_count"] == 0},
        {"code": "NO_CONTRACT_KEY_MATERIAL_STORED", "passed": contract["key_material_stored"] is False},
        {"code": "NO_CONTRACT_KMS_KEY_ID_STORED", "passed": contract["kms_key_id_stored"] is False},
        {"code": "NO_CONTRACT_KEY_LOCATOR_PRESENT", "passed": contract["key_locator_present"] is False},
        {"code": "NO_CONTRACT_ENCRYPTION_POLICY_CONFIGURED", "passed": contract["encryption_policy_configured"] is False},
        {"code": "NO_CONTRACT_ENCRYPTION_ALGORITHM_CONFIGURED", "passed": contract["encryption_algorithm_configured"] is False},
        {"code": "NO_CONTRACT_ENCRYPTION_AT_REST_CONFIGURED", "passed": contract["encryption_at_rest_configured"] is False},
        {"code": "NO_CONTRACT_ENCRYPTION_IN_TRANSIT_CONFIGURED", "passed": contract["encryption_in_transit_configured"] is False},
        {"code": "NO_CONTRACT_CUSTOMER_KEY_CONFIGURED", "passed": contract["customer_managed_key_configured"] is False},
        {"code": "NO_CONTRACT_PROVIDER_KEY_CONFIGURED", "passed": contract["provider_managed_key_configured"] is False},
        {"code": "NO_CONTRACT_SECRETS_PRESENT", "passed": contract["secret_values_present"] is False and contract["token_material_present"] is False},
        {"code": "NO_CONTRACT_SECRET_REFERENCES_CREATED", "passed": contract["secret_references_created"] is False},
        {"code": "NO_CONTRACT_SECRET_REFERENCES_ACTIVATED", "passed": contract["secret_references_activated"] is False},
        {"code": "NO_CREDENTIALS_CONFIGURED", "passed": contract["credentials_configured"] is False},
        {"code": "NO_PROVIDER_ENDPOINT_CONFIGURED", "passed": contract["provider_endpoint_configured"] is False},
        {"code": "NO_STORAGE_CONTAINER_CONFIGURED", "passed": contract["storage_container_configured"] is False},
        {"code": "NO_NAMESPACE_CONFIGURED", "passed": contract["namespace_configured"] is False},
        {"code": "NO_PROVIDER_CONFIGURATION_READY", "passed": contract["provider_configuration_ready"] is False},
        {"code": "NO_PROVIDER_CONFIGURED", "passed": contract["provider_configured"] is False},
        {"code": "NO_PROVIDER_READ_WRITE", "passed": contract["provider_read_enabled"] is False and contract["provider_write_enabled"] is False},
        {"code": "NO_PROVIDER_CONNECTION_TESTED", "passed": contract["provider_connection_tested"] is False},
        {"code": "NO_OBJECT_BODY_VIEW", "passed": contract["object_body_view_enabled"] is False},
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
        "safe_to_continue_to_gp066": len(failed) == 0,
    }


def get_storage_provider_encryption_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp066": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "Continue under ARCHIVE VAULT — REAL STORAGE PROVIDER CONFIGURATION LAYER / GP061-GP070. GP066 should build the real provider connection-test lock contract while keeping encryption, keys, credentials, provider connection, read/write, export, and execution locked.",
            "carry_forward_rules": [
                "Keep the real SQLite encryption policy contract.",
                "Keep real encryption requirement rows.",
                "Keep real key-management policy rows.",
                "Keep real blockers carried from GP064.",
                "Build GP066 Real Storage Provider Connection Test Lock Contract next.",
                "Do not store key material.",
                "Do not store KMS key IDs.",
                "Do not store key locators.",
                "Do not configure encryption policy yet.",
                "Do not configure encryption algorithm yet.",
                "Do not configure encryption-at-rest yet.",
                "Do not configure encryption-in-transit yet.",
                "Do not configure customer-managed keys.",
                "Do not configure provider-managed keys.",
                "Do not store actual provider secrets.",
                "Do not store tokens, keys, passwords, or credential material.",
                "Do not create or activate secret references yet.",
                "Do not configure credentials yet.",
                "Do not configure provider endpoint yet.",
                "Do not configure storage container yet.",
                "Do not configure namespace yet.",
                "Do not approve, activate, recommend, or select a provider yet.",
                "Do not enable provider read or write yet.",
                "Do not test provider connection yet.",
                "Do not unlock object body view.",
                "Do not unlock direct upload.",
                "Do not unlock export.",
                "Do not unlock execution.",
                "Do not treat Vault as done.",
            ],
        },
    }


def get_real_storage_provider_encryption_policy_contract_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_encryption_policy_contract(db_path)
    contract = get_storage_provider_encryption_policy_contract_record(db_path)["encryption_policy_contract"]
    requirements = get_storage_provider_encryption_requirements(db_path)
    policies = get_storage_provider_encryption_policies(db_path)
    blockers = get_storage_provider_encryption_blockers(db_path)
    events = get_storage_provider_encryption_events(db_path)
    validation = validate_storage_provider_encryption_policy_contract(db_path)

    return {
        "pack": _pack_payload(),
        "encryption_truth": _encryption_truth(contract, requirements, policies, blockers, events["event_count"], validation),
        "store": init,
        "encryption_policy_contract": contract,
        "requirements": requirements,
        "policies": policies,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_encryption_next_step()["next_step"],
    }


def get_gp065_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_encryption_policy_contract_home(db_path)
    contract = home["encryption_policy_contract"]
    requirements = home["requirements"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp065_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_encryption_policy_contract_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_contract_count": home["store"]["contract_count"],
            "real_requirement_count": home["store"]["requirement_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp064_endpoint_namespace_contract_attached": True,
            "encryption_policy_contract_ready": contract["encryption_policy_contract_ready"],
            "encryption_requirements_ready": contract["encryption_requirements_ready"],
            "key_management_policy_ready": contract["key_management_policy_ready"],
            "encryption_policy_alias_only": contract["encryption_policy_alias_only"],
            "key_alias_only": contract["key_alias_only"],
            "provider_candidate_count": requirements["provider_candidate_count"],
            "requirement_code_count": requirements["requirement_code_count"],
            "policy_code_count": policies["policy_code_count"],
            "key_material_stored_count": requirements["key_material_stored_count"] + policies["key_material_stored_count"],
            "kms_key_id_stored_count": requirements["kms_key_id_stored_count"] + policies["kms_key_id_stored_count"],
            "key_locator_present_count": requirements["key_locator_present_count"] + policies["key_locator_present_count"],
            "encryption_policy_configured_count": requirements["encryption_policy_configured_count"] + policies["encryption_policy_configured_count"],
            "encryption_algorithm_configured_count": requirements["encryption_algorithm_configured_count"] + policies["encryption_algorithm_configured_count"],
            "encryption_at_rest_configured_count": requirements["encryption_at_rest_configured_count"] + policies["encryption_at_rest_configured_count"],
            "encryption_in_transit_configured_count": requirements["encryption_in_transit_configured_count"] + policies["encryption_in_transit_configured_count"],
            "customer_managed_key_configured_count": requirements["customer_managed_key_configured_count"] + policies["customer_managed_key_configured_count"],
            "provider_managed_key_configured_count": requirements["provider_managed_key_configured_count"] + policies["provider_managed_key_configured_count"],
            "secret_value_present_count": policies["secret_values_present_count"],
            "token_material_present_count": policies["token_material_present_count"],
            "secret_references_created_count": policies["secret_references_created_count"],
            "secret_references_activated_count": requirements["secret_references_activated_count"] + policies["secret_references_activated_count"],
            "credentials_configured_count": requirements["credentials_configured_count"] + policies["credentials_configured_count"],
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
            "safe_to_continue_to_gp066": validation["safe_to_continue_to_gp066"],
            "vault_done": False,
            "foundation_status": "encryption_policy_contract_ready_safe_to_continue_not_done",
            "key_material_stored": contract["key_material_stored"],
            "kms_key_id_stored": contract["kms_key_id_stored"],
            "key_locator_present": contract["key_locator_present"],
            "encryption_policy_configured": contract["encryption_policy_configured"],
            "encryption_algorithm_configured": contract["encryption_algorithm_configured"],
            "encryption_at_rest_configured": contract["encryption_at_rest_configured"],
            "encryption_in_transit_configured": contract["encryption_in_transit_configured"],
            "customer_managed_key_configured": contract["customer_managed_key_configured"],
            "provider_managed_key_configured": contract["provider_managed_key_configured"],
            "actual_secret_values_stored": contract["actual_secret_values_stored"],
            "secret_values_present": contract["secret_values_present"],
            "token_material_present": contract["token_material_present"],
            "encrypted_secret_payload_present": contract["encrypted_secret_payload_present"],
            "secret_references_created": contract["secret_references_created"],
            "secret_references_activated": contract["secret_references_activated"],
            "credentials_configured": contract["credentials_configured"],
            "provider_endpoint_configured": contract["provider_endpoint_configured"],
            "storage_container_configured": contract["storage_container_configured"],
            "namespace_configured": contract["namespace_configured"],
            "provider_approval_ready": contract["provider_approval_ready"],
            "provider_activation_ready": contract["provider_activation_ready"],
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
            "provider_connection_tested": contract["provider_connection_tested"],
            "risk_accepted": contract["risk_accepted"],
            "risk_waived": contract["risk_waived"],
            "mitigation_approved": contract["mitigation_approved"],
            "official_storage_receipt": contract["official_storage_receipt"],
            "finalized_storage_receipt": contract["finalized_storage_receipt"],
            "closed_storage_receipt": contract["closed_storage_receipt"],
            "object_body_view_enabled": contract["object_body_view_enabled"],
            "direct_upload_enabled": contract["direct_upload_enabled"],
            "export_enabled": contract["export_enabled"],
            "execution_enabled": contract["execution_enabled"],
            "clouds_status": "parked_do_not_continue_from_vault_gp065",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "encryption_truth": home["encryption_truth"],
        "routes": home["routes"],
        "encryption_policy_contract": contract,
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
        "depends_on": ["VAULT_GP064"],
        "foundation_status": "encryption_policy_contract_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_encryption_policy_contract",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }


def _routes_payload() -> Dict[str, str]:
    return {
        "room_title": "Vault Real Storage Provider Encryption Policy Contract",
        "section_header": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "route": "/vault/real-storage-provider-encryption-policy-contract",
        "json_route": "/vault/real-storage-provider-encryption-policy-contract.json",
        "record_route": "/vault/storage-provider-encryption-policy-contract-record.json",
        "requirements_route": "/vault/storage-provider-encryption-requirements.json",
        "policies_route": "/vault/storage-provider-encryption-policies.json",
        "blockers_route": "/vault/storage-provider-encryption-blockers.json",
        "events_route": "/vault/storage-provider-encryption-events.json",
        "validation_route": "/vault/storage-provider-encryption-validation.json",
        "next_step_route": "/vault/storage-provider-encryption-next-step.json",
        "gp065_status_route": "/vault/gp065-status.json",
    }


def _encryption_truth(contract, requirements, policies, blockers, event_count, validation) -> Dict[str, Any]:
    return {
        "real_storage_provider_encryption_policy_contract_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "real_encryption_policy_contract_exists": contract["encryption_policy_contract_id"] == DEFAULT_ENCRYPTION_POLICY_CONTRACT_ID,
        "real_encryption_requirement_rows_exist": requirements["requirement_count"] == 40,
        "real_key_management_policy_rows_exist": policies["policy_count"] == len(ENCRYPTION_POLICIES),
        "real_encryption_blocker_rows_exist": blockers["blocker_count"] == 140,
        "real_event_log_exists": event_count >= 6,
        "source_gp064_endpoint_namespace_contract_attached": contract["source_endpoint_namespace_contract_id"] == DEFAULT_ENDPOINT_NAMESPACE_CONTRACT_ID,
        "validation_passed": validation["valid"],
        "encryption_policy_contract_ready": contract["encryption_policy_contract_ready"],
        "encryption_requirements_ready": contract["encryption_requirements_ready"],
        "key_management_policy_ready": contract["key_management_policy_ready"],
        "encryption_policy_alias_only": contract["encryption_policy_alias_only"],
        "key_alias_only": contract["key_alias_only"],
        "requirement_count": requirements["requirement_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "key_material_stored_count": requirements["key_material_stored_count"] + policies["key_material_stored_count"],
        "kms_key_id_stored_count": requirements["kms_key_id_stored_count"] + policies["kms_key_id_stored_count"],
        "key_locator_present_count": requirements["key_locator_present_count"] + policies["key_locator_present_count"],
        "encryption_policy_configured_count": requirements["encryption_policy_configured_count"] + policies["encryption_policy_configured_count"],
        "encryption_algorithm_configured_count": requirements["encryption_algorithm_configured_count"] + policies["encryption_algorithm_configured_count"],
        "encryption_at_rest_configured_count": requirements["encryption_at_rest_configured_count"] + policies["encryption_at_rest_configured_count"],
        "encryption_in_transit_configured_count": requirements["encryption_in_transit_configured_count"] + policies["encryption_in_transit_configured_count"],
        "customer_managed_key_configured_count": requirements["customer_managed_key_configured_count"] + policies["customer_managed_key_configured_count"],
        "provider_managed_key_configured_count": requirements["provider_managed_key_configured_count"] + policies["provider_managed_key_configured_count"],
        "secret_value_present_count": policies["secret_values_present_count"],
        "token_material_present_count": policies["token_material_present_count"],
        "secret_references_activated_count": requirements["secret_references_activated_count"] + policies["secret_references_activated_count"],
        "credentials_configured_count": requirements["credentials_configured_count"] + policies["credentials_configured_count"],
        "provider_connection_tested": contract["provider_connection_tested"],
        "provider_read_enabled": contract["provider_read_enabled"],
        "provider_write_enabled": contract["provider_write_enabled"],
        "object_body_view_enabled": contract["object_body_view_enabled"],
        "direct_upload_enabled": contract["direct_upload_enabled"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "vault_done": contract["vault_done"],
        "safe_to_continue_to_gp066": validation["safe_to_continue_to_gp066"],
    }


def render_real_storage_provider_encryption_policy_contract_page() -> str:
    home = get_real_storage_provider_encryption_policy_contract_home()
    truth = home["encryption_truth"]
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
  <title>Vault Real Storage Provider Encryption Policy Contract · GP065</title>
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
      <div class="eyebrow">Archive Vault · Giant Pack 065</div>
      <div class="eyebrow">Real Storage Provider Configuration Layer · GP061-GP070</div>
      <h1>Real Storage Provider Encryption Policy Contract</h1>
      <p>
        GP065 creates a real encryption/key-management policy contract with alias-only requirements,
        policy rows, carried blockers, and event history. It stores no key material, KMS key ID,
        key locator, secret, credential, or usable encryption/provider configuration.
      </p>
      <div class="metrics">
        <div class="metric"><strong>{home['store']['requirement_count']}</strong><span>encryption requirements</span></div>
        <div class="metric"><strong>{home['store']['policy_count']}</strong><span>key-management policies</span></div>
        <div class="metric"><strong>{truth['key_material_stored_count']}</strong><span>key material stored</span></div>
        <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
      </div>
      <div class="chips">
        <span class="pill ok">Encryption policy contract ready</span>
        <span class="pill ok">Alias-only rows</span>
        <span class="pill ok">Real SQLite-backed</span>
        <span class="pill danger">No keys stored</span>
        <span class="pill danger">No encryption configured</span>
        <span class="pill danger">No execution</span>
      </div>
    </section>

    <section class="section">
      <h2>Encryption Requirements</h2>
      <p>These are real requirement rows. They are alias-only and non-operational.</p>
      <div class="grid">{requirement_cards}</div>
    </section>

    <section class="section">
      <h2>Key-Management Policies</h2>
      <p>These are real policy rows governing key material, KMS references, encryption configuration, export, and execution locks.</p>
      <div class="grid">{policy_cards}</div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Validation Checks</h2>
        <p>GP065 proves the contract is durable while encryption/key configuration and provider access remain locked.</p>
        {checks}
      </div>
      <div>
        <h2>Carry Forward to GP066</h2>
        <p>{escape(next_step['owner_notebook_note'])}</p>
        <ul>{rules_html}</ul>
      </div>
    </section>

    <section class="section">
      <h2>GP065 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['record_route'])}</code>
        <code>{escape(routes['requirements_route'])}</code>
        <code>{escape(routes['policies_route'])}</code>
        <code>{escape(routes['blockers_route'])}</code>
        <code>{escape(routes['events_route'])}</code>
        <code>{escape(routes['validation_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp065_status_route'])}</code>
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
          Key material stored: <code>{str(item['key_material_stored']).lower()}</code><br>
          Encryption configured: <code>{str(item['encryption_policy_configured']).lower()}</code>
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
          Verified: <code>{str(item['policy_verified']).lower()}</code><br>
          Export: <code>{str(item['export_enabled']).lower()}</code><br>
          Execution: <code>{str(item['execution_enabled']).lower()}</code>
        </div>
      </article>
    """
