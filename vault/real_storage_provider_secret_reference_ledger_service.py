"""
VAULT GIANT PACK 063 — Real Storage Provider Secret Reference Ledger

CURRENT SECTION:
Archive Vault — Real Storage Provider Configuration Layer
GP061-GP070

This pack creates a real durable secret-reference ledger from the GP062
credential boundary slots without storing actual secret material.

Purpose:
- Create a real SQLite-backed secret-reference ledger schema.
- Persist a real ledger record sourced from GP062.
- Persist real ledger entries sourced from GP062 secret-reference slots.
- Persist real policy rows for alias-only lifecycle/audit requirements.
- Carry forward real blockers from GP062.
- Persist a real ledger event log.
- Validate that no secret values, tokens, encrypted secret payloads, or usable
  credentials are stored.

Important truth:
- GP063 creates the ledger for secret references.
- GP063 does not create or activate real secret references.
- GP063 does not store actual secrets, tokens, keys, passwords, or encrypted secret payloads.
- GP063 does not configure provider credentials.
- GP063 does not approve, activate, select, configure, read, write, export, or execute.
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

from vault.real_storage_provider_credential_boundary_service import (
    DEFAULT_CREDENTIAL_BOUNDARY_ID,
    get_storage_provider_credential_boundary_blockers,
    get_storage_provider_credential_boundary_record,
    get_storage_provider_secret_reference_slots,
)


PACK_ID = "VAULT_GP063"
PACK_NAME = "Real Storage Provider Secret Reference Ledger"
SCHEMA_VERSION = "vault.real_storage_provider_secret_reference_ledger.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
SECTION_TITLE = "Archive Vault — Real Storage Provider Configuration Layer"
SECTION_RANGE = "GP061-GP070"

NEXT_PACK = "VAULT_GP064_REAL_STORAGE_PROVIDER_ENDPOINT_NAMESPACE_CONTRACT"
NEXT_PACK_TITLE = "Real Storage Provider Endpoint Namespace Contract"

DEFAULT_SECRET_REFERENCE_LEDGER_ID = "VSPSRL-GP063-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_secret_reference_ledger.sqlite"


LEDGER_POLICIES = [
    {
        "policy_code": "alias_only_reference_required",
        "policy_name": "Alias-only reference required",
        "policy_category": "reference_model",
        "policy_message": "Ledger rows may store deterministic aliases only; no secret values or live secret locators.",
    },
    {
        "policy_code": "no_secret_material_in_ledger",
        "policy_name": "No secret material in ledger",
        "policy_category": "secret_safety",
        "policy_message": "Secret, token, key, password, credential, or encrypted secret payload values must never be stored here.",
    },
    {
        "policy_code": "tower_reference_activation_required",
        "policy_name": "Tower reference activation required",
        "policy_category": "tower_gate",
        "policy_message": "Secret references cannot be activated until Tower grants a later explicit step.",
    },
    {
        "policy_code": "owner_redacted_view_only",
        "policy_name": "Owner redacted view only",
        "policy_category": "redaction",
        "policy_message": "Owner-facing ledger views must remain redacted and secret-free.",
    },
    {
        "policy_code": "audit_event_required_before_reference_use",
        "policy_name": "Audit event required before reference use",
        "policy_category": "audit",
        "policy_message": "Any future reference use must be recorded as an audit event before provider connection testing.",
    },
    {
        "policy_code": "rotation_metadata_required",
        "policy_name": "Rotation metadata required",
        "policy_category": "lifecycle",
        "policy_message": "Future reference activation requires rotation metadata; this ledger only marks the requirement.",
    },
    {
        "policy_code": "revocation_metadata_required",
        "policy_name": "Revocation metadata required",
        "policy_category": "lifecycle",
        "policy_message": "Future reference activation requires revocation metadata; this ledger only marks the requirement.",
    },
    {
        "policy_code": "no_provider_connection_from_ledger",
        "policy_name": "No provider connection from ledger",
        "policy_category": "connection_lock",
        "policy_message": "The ledger cannot test provider connections or unlock read/write paths.",
    },
    {
        "policy_code": "no_export_from_ledger",
        "policy_name": "No export from ledger",
        "policy_category": "export_lock",
        "policy_message": "The ledger cannot unlock external delivery or export.",
    },
    {
        "policy_code": "no_execution_from_ledger",
        "policy_name": "No execution from ledger",
        "policy_category": "execution_lock",
        "policy_message": "The ledger cannot unlock execution.",
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


def ensure_storage_provider_secret_reference_ledger_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_secret_reference_ledgers (
                secret_reference_ledger_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_credential_boundary_id TEXT NOT NULL,
                source_credential_boundary_pack_id TEXT NOT NULL,
                ledger_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                ledger_data_json TEXT NOT NULL,
                secret_reference_ledger_ready INTEGER NOT NULL DEFAULT 1,
                ledger_entries_ready INTEGER NOT NULL DEFAULT 1,
                alias_only_references INTEGER NOT NULL DEFAULT 1,
                actual_secret_values_stored INTEGER NOT NULL DEFAULT 0,
                secret_values_present INTEGER NOT NULL DEFAULT 0,
                token_material_present INTEGER NOT NULL DEFAULT 0,
                encrypted_secret_payload_present INTEGER NOT NULL DEFAULT 0,
                secret_references_created INTEGER NOT NULL DEFAULT 0,
                secret_references_activated INTEGER NOT NULL DEFAULT 0,
                credentials_configured INTEGER NOT NULL DEFAULT 0,
                provider_endpoint_configured INTEGER NOT NULL DEFAULT 0,
                storage_container_configured INTEGER NOT NULL DEFAULT 0,
                encryption_configured INTEGER NOT NULL DEFAULT 0,
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_secret_reference_ledger_entries (
                ledger_entry_id TEXT PRIMARY KEY,
                secret_reference_ledger_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                source_secret_reference_slot_id TEXT NOT NULL,
                source_slot_code TEXT NOT NULL,
                source_slot_name TEXT NOT NULL,
                source_slot_category TEXT NOT NULL,
                secret_reference_alias TEXT NOT NULL,
                ledger_entry_status TEXT NOT NULL,
                reference_required INTEGER NOT NULL DEFAULT 1,
                reference_created INTEGER NOT NULL DEFAULT 0,
                reference_activated INTEGER NOT NULL DEFAULT 0,
                alias_only_reference INTEGER NOT NULL DEFAULT 1,
                actual_secret_value_stored INTEGER NOT NULL DEFAULT 0,
                secret_value_present INTEGER NOT NULL DEFAULT 0,
                token_material_present INTEGER NOT NULL DEFAULT 0,
                encrypted_secret_payload_present INTEGER NOT NULL DEFAULT 0,
                credential_material_exposed INTEGER NOT NULL DEFAULT 0,
                redacted_view_only INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_granted INTEGER NOT NULL DEFAULT 0,
                credentials_configured INTEGER NOT NULL DEFAULT 0,
                provider_connection_tested INTEGER NOT NULL DEFAULT 0,
                provider_read_enabled INTEGER NOT NULL DEFAULT 0,
                provider_write_enabled INTEGER NOT NULL DEFAULT 0,
                export_enabled INTEGER NOT NULL DEFAULT 0,
                execution_enabled INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(secret_reference_ledger_id)
                    REFERENCES vault_storage_provider_secret_reference_ledgers(secret_reference_ledger_id)
                    ON DELETE CASCADE,
                UNIQUE(secret_reference_ledger_id, source_secret_reference_slot_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_secret_reference_ledger_policies (
                ledger_policy_id TEXT PRIMARY KEY,
                secret_reference_ledger_id TEXT NOT NULL,
                policy_code TEXT NOT NULL,
                policy_name TEXT NOT NULL,
                policy_category TEXT NOT NULL,
                policy_message TEXT NOT NULL,
                policy_status TEXT NOT NULL,
                policy_required INTEGER NOT NULL DEFAULT 1,
                policy_verified INTEGER NOT NULL DEFAULT 0,
                actual_secret_values_stored INTEGER NOT NULL DEFAULT 0,
                secret_values_present INTEGER NOT NULL DEFAULT 0,
                token_material_present INTEGER NOT NULL DEFAULT 0,
                encrypted_secret_payload_present INTEGER NOT NULL DEFAULT 0,
                secret_references_created INTEGER NOT NULL DEFAULT 0,
                secret_references_activated INTEGER NOT NULL DEFAULT 0,
                provider_connection_tested INTEGER NOT NULL DEFAULT 0,
                provider_read_enabled INTEGER NOT NULL DEFAULT 0,
                provider_write_enabled INTEGER NOT NULL DEFAULT 0,
                export_enabled INTEGER NOT NULL DEFAULT 0,
                execution_enabled INTEGER NOT NULL DEFAULT 0,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_granted INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(secret_reference_ledger_id)
                    REFERENCES vault_storage_provider_secret_reference_ledgers(secret_reference_ledger_id)
                    ON DELETE CASCADE,
                UNIQUE(secret_reference_ledger_id, policy_code)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_secret_reference_ledger_blockers (
                ledger_blocker_id TEXT PRIMARY KEY,
                secret_reference_ledger_id TEXT NOT NULL,
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
                FOREIGN KEY(secret_reference_ledger_id)
                    REFERENCES vault_storage_provider_secret_reference_ledgers(secret_reference_ledger_id)
                    ON DELETE CASCADE,
                UNIQUE(secret_reference_ledger_id, source_credential_blocker_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_secret_reference_ledger_events (
                event_id TEXT PRIMARY KEY,
                secret_reference_ledger_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(secret_reference_ledger_id)
                    REFERENCES vault_storage_provider_secret_reference_ledgers(secret_reference_ledger_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_secret_reference_entries_ledger
            ON vault_storage_provider_secret_reference_ledger_entries(secret_reference_ledger_id, provider_candidate_id, source_slot_category)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_secret_reference_blockers_ledger
            ON vault_storage_provider_secret_reference_ledger_blockers(secret_reference_ledger_id, provider_candidate_id, blocker_category)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_secret_reference_events_ledger
            ON vault_storage_provider_secret_reference_ledger_events(secret_reference_ledger_id, created_at)
            """
        )
        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "tables": [
            "vault_storage_provider_secret_reference_ledgers",
            "vault_storage_provider_secret_reference_ledger_entries",
            "vault_storage_provider_secret_reference_ledger_policies",
            "vault_storage_provider_secret_reference_ledger_blockers",
            "vault_storage_provider_secret_reference_ledger_events",
        ],
        "real_sqlite_backed": True,
    }


def initialize_real_storage_provider_secret_reference_ledger(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_secret_reference_ledger_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            """
            SELECT secret_reference_ledger_id
            FROM vault_storage_provider_secret_reference_ledgers
            WHERE secret_reference_ledger_id = ?
            """,
            (DEFAULT_SECRET_REFERENCE_LEDGER_ID,),
        ).fetchone()

        if existing is None:
            boundary = get_storage_provider_credential_boundary_record()["credential_boundary"]
            slots_payload = get_storage_provider_secret_reference_slots()
            blockers_payload = get_storage_provider_credential_boundary_blockers()
            slots = slots_payload["slots"]
            blockers = blockers_payload["blockers"]
            ledger_data = _build_ledger_data(boundary, slots_payload, blockers_payload)
            now = _now_iso()

            _insert_dict(
                conn,
                "vault_storage_provider_secret_reference_ledgers",
                {
                    "secret_reference_ledger_id": DEFAULT_SECRET_REFERENCE_LEDGER_ID,
                    "pack_id": PACK_ID,
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    "source_credential_boundary_id": boundary["credential_boundary_id"],
                    "source_credential_boundary_pack_id": boundary["pack_id"],
                    "ledger_status": "REAL_SECRET_REFERENCE_LEDGER_OPEN_ALIAS_ONLY_TOWER_LOCKED",
                    "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    "ledger_data_json": _json_dumps(ledger_data),
                    "secret_reference_ledger_ready": 1,
                    "ledger_entries_ready": 1,
                    "alias_only_references": 1,
                    "actual_secret_values_stored": 0,
                    "secret_values_present": 0,
                    "token_material_present": 0,
                    "encrypted_secret_payload_present": 0,
                    "secret_references_created": 0,
                    "secret_references_activated": 0,
                    "credentials_configured": 0,
                    "provider_endpoint_configured": 0,
                    "storage_container_configured": 0,
                    "encryption_configured": 0,
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

            for slot in slots:
                _insert_ledger_entry(conn, DEFAULT_SECRET_REFERENCE_LEDGER_ID, slot, now)

            for policy in LEDGER_POLICIES:
                _insert_ledger_policy(conn, DEFAULT_SECRET_REFERENCE_LEDGER_ID, policy, now)

            for blocker in blockers:
                _insert_ledger_blocker(conn, DEFAULT_SECRET_REFERENCE_LEDGER_ID, blocker, now)

            entry_counts = _get_entry_counts(conn, DEFAULT_SECRET_REFERENCE_LEDGER_ID)
            policy_counts = _get_policy_counts(conn, DEFAULT_SECRET_REFERENCE_LEDGER_ID)
            blocker_counts = _get_blocker_counts(conn, DEFAULT_SECRET_REFERENCE_LEDGER_ID)

            _insert_event(
                conn,
                DEFAULT_SECRET_REFERENCE_LEDGER_ID,
                "REAL_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_CREATED",
                {
                    "pack_id": PACK_ID,
                    "source_credential_boundary_id": boundary["credential_boundary_id"],
                    "source_credential_boundary_pack_id": boundary["pack_id"],
                    "real_sqlite_backed": True,
                    "secret_reference_ledger_ready": True,
                    "alias_only_references": True,
                    "actual_secret_values_stored": False,
                    "secret_values_present": False,
                    "token_material_present": False,
                    "secret_references_created": False,
                    "secret_references_activated": False,
                    "vault_done": False,
                },
            )
            _insert_event(
                conn,
                DEFAULT_SECRET_REFERENCE_LEDGER_ID,
                "SOURCE_GP062_CREDENTIAL_BOUNDARY_ATTACHED",
                _compact_boundary_source_snapshot(boundary, slots_payload, blockers_payload),
            )
            _insert_event(
                conn,
                DEFAULT_SECRET_REFERENCE_LEDGER_ID,
                "REAL_SECRET_REFERENCE_LEDGER_ENTRIES_CREATED_ALIAS_ONLY",
                entry_counts,
            )
            _insert_event(
                conn,
                DEFAULT_SECRET_REFERENCE_LEDGER_ID,
                "REAL_SECRET_REFERENCE_LEDGER_POLICIES_CREATED",
                policy_counts,
            )
            _insert_event(
                conn,
                DEFAULT_SECRET_REFERENCE_LEDGER_ID,
                "REAL_SECRET_REFERENCE_LEDGER_BLOCKERS_CARRIED_FORWARD",
                blocker_counts,
            )
            _insert_event(
                conn,
                DEFAULT_SECRET_REFERENCE_LEDGER_ID,
                "SECRET_REFERENCE_LEDGER_LOCKS_CONFIRMED",
                {
                    "no_actual_secret_values_stored": True,
                    "no_token_material_present": True,
                    "no_encrypted_secret_payload_present": True,
                    "secret_reference_creation_blocked": True,
                    "secret_reference_activation_blocked": True,
                    "credential_configuration_blocked": True,
                    "provider_configuration_blocked": True,
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
        "secret_reference_ledger_id": DEFAULT_SECRET_REFERENCE_LEDGER_ID,
        "ledger_count": counts["ledger_count"],
        "entry_count": counts["entry_count"],
        "policy_count": counts["policy_count"],
        "blocker_count": counts["blocker_count"],
        "event_count": counts["event_count"],
        "real_sqlite_backed": True,
    }


def _safe_alias(slot: Dict[str, Any]) -> str:
    candidate_suffix = slot["provider_candidate_id"].replace("VSPC-", "CANDIDATE-")
    slot_code = slot["slot_code"].upper().replace("_", "-")
    return f"ALIAS-ONLY-{candidate_suffix}-{slot_code}-UNCREATED"


def _insert_ledger_entry(conn: sqlite3.Connection, ledger_id: str, slot: Dict[str, Any], now: str) -> str:
    ledger_entry_id = f"VSPSRLE-{slot['secret_reference_slot_id'].replace('VSPSRS-', '')}"
    _insert_dict(
        conn,
        "vault_storage_provider_secret_reference_ledger_entries",
        {
            "ledger_entry_id": ledger_entry_id,
            "secret_reference_ledger_id": ledger_id,
            "provider_candidate_id": slot["provider_candidate_id"],
            "source_secret_reference_slot_id": slot["secret_reference_slot_id"],
            "source_slot_code": slot["slot_code"],
            "source_slot_name": slot["slot_name"],
            "source_slot_category": slot["slot_category"],
            "secret_reference_alias": _safe_alias(slot),
            "ledger_entry_status": "REAL_LEDGER_ENTRY_ALIAS_ONLY_NO_SECRET_REFERENCE_CREATED",
            "reference_required": 1 if slot["reference_required"] else 0,
            "reference_created": 0,
            "reference_activated": 0,
            "alias_only_reference": 1,
            "actual_secret_value_stored": 0,
            "secret_value_present": 0,
            "token_material_present": 0,
            "encrypted_secret_payload_present": 0,
            "credential_material_exposed": 0,
            "redacted_view_only": 1,
            "tower_review_required": 1,
            "tower_review_granted": 0,
            "credentials_configured": 0,
            "provider_connection_tested": 0,
            "provider_read_enabled": 0,
            "provider_write_enabled": 0,
            "export_enabled": 0,
            "execution_enabled": 0,
            "created_at": now,
            "updated_at": now,
        },
    )
    return ledger_entry_id


def _insert_ledger_policy(conn: sqlite3.Connection, ledger_id: str, policy: Dict[str, str], now: str) -> str:
    ledger_policy_id = f"VSPSRLP-{policy['policy_code'].upper().replace('_', '-')}"
    _insert_dict(
        conn,
        "vault_storage_provider_secret_reference_ledger_policies",
        {
            "ledger_policy_id": ledger_policy_id,
            "secret_reference_ledger_id": ledger_id,
            "policy_code": policy["policy_code"],
            "policy_name": policy["policy_name"],
            "policy_category": policy["policy_category"],
            "policy_message": policy["policy_message"],
            "policy_status": "REAL_SECRET_REFERENCE_LEDGER_POLICY_RECORDED_TOWER_LOCKED",
            "policy_required": 1,
            "policy_verified": 0,
            "actual_secret_values_stored": 0,
            "secret_values_present": 0,
            "token_material_present": 0,
            "encrypted_secret_payload_present": 0,
            "secret_references_created": 0,
            "secret_references_activated": 0,
            "provider_connection_tested": 0,
            "provider_read_enabled": 0,
            "provider_write_enabled": 0,
            "export_enabled": 0,
            "execution_enabled": 0,
            "tower_review_required": 1,
            "tower_review_granted": 0,
            "created_at": now,
            "updated_at": now,
        },
    )
    return ledger_policy_id


def _insert_ledger_blocker(conn: sqlite3.Connection, ledger_id: str, blocker: Dict[str, Any], now: str) -> str:
    ledger_blocker_id = f"VSPSRLB-{blocker['credential_blocker_id'].replace('VSPCBB-', '')}"
    _insert_dict(
        conn,
        "vault_storage_provider_secret_reference_ledger_blockers",
        {
            "ledger_blocker_id": ledger_blocker_id,
            "secret_reference_ledger_id": ledger_id,
            "source_credential_blocker_id": blocker["credential_blocker_id"],
            "source_config_blocker_id": blocker["source_config_blocker_id"],
            "source_readiness_blocker_id": blocker["source_readiness_blocker_id"],
            "source_receipt_line_id": blocker["source_receipt_line_id"],
            "source_finding_id": blocker["source_finding_id"],
            "provider_candidate_id": blocker["provider_candidate_id"],
            "blocker_category": blocker["blocker_category"],
            "blocker_code": blocker["blocker_code"],
            "blocker_name": blocker["blocker_name"],
            "severity": blocker["severity"],
            "blocker_status": "REAL_SECRET_REFERENCE_LEDGER_BLOCKER_ACTIVE_CARRIED_FROM_GP062",
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
    return ledger_blocker_id


def _insert_event(conn: sqlite3.Connection, ledger_id: str, event_type: str, event_payload: Dict[str, Any]) -> str:
    event_id = f"VSPSRLEVT-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_storage_provider_secret_reference_ledger_events",
        {
            "event_id": event_id,
            "secret_reference_ledger_id": ledger_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id


def _get_counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        ledger_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_secret_reference_ledgers").fetchone()["c"]
        entry_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_secret_reference_ledger_entries").fetchone()["c"]
        policy_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_secret_reference_ledger_policies").fetchone()["c"]
        blocker_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_secret_reference_ledger_blockers").fetchone()["c"]
        event_count = conn.execute("SELECT COUNT(*) AS c FROM vault_storage_provider_secret_reference_ledger_events").fetchone()["c"]

    return {
        "ledger_count": int(ledger_count),
        "entry_count": int(entry_count),
        "policy_count": int(policy_count),
        "blocker_count": int(blocker_count),
        "event_count": int(event_count),
    }


def _get_entry_counts(conn: sqlite3.Connection, ledger_id: str) -> Dict[str, int]:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS entry_count,
            COUNT(DISTINCT provider_candidate_id) AS provider_candidate_count,
            COUNT(DISTINCT source_slot_code) AS slot_code_count,
            SUM(CASE WHEN reference_required = 1 THEN 1 ELSE 0 END) AS reference_required_count,
            SUM(CASE WHEN reference_created = 1 THEN 1 ELSE 0 END) AS reference_created_count,
            SUM(CASE WHEN reference_activated = 1 THEN 1 ELSE 0 END) AS reference_activated_count,
            SUM(CASE WHEN alias_only_reference = 1 THEN 1 ELSE 0 END) AS alias_only_reference_count,
            SUM(CASE WHEN actual_secret_value_stored = 1 THEN 1 ELSE 0 END) AS actual_secret_value_stored_count,
            SUM(CASE WHEN secret_value_present = 1 THEN 1 ELSE 0 END) AS secret_value_present_count,
            SUM(CASE WHEN token_material_present = 1 THEN 1 ELSE 0 END) AS token_material_present_count,
            SUM(CASE WHEN encrypted_secret_payload_present = 1 THEN 1 ELSE 0 END) AS encrypted_secret_payload_present_count,
            SUM(CASE WHEN credential_material_exposed = 1 THEN 1 ELSE 0 END) AS credential_material_exposed_count,
            SUM(CASE WHEN redacted_view_only = 1 THEN 1 ELSE 0 END) AS redacted_view_only_count,
            SUM(CASE WHEN tower_review_required = 1 THEN 1 ELSE 0 END) AS tower_review_required_count,
            SUM(CASE WHEN tower_review_granted = 1 THEN 1 ELSE 0 END) AS tower_review_granted_count,
            SUM(CASE WHEN credentials_configured = 1 THEN 1 ELSE 0 END) AS credentials_configured_count,
            SUM(CASE WHEN provider_connection_tested = 1 THEN 1 ELSE 0 END) AS provider_connection_tested_count,
            SUM(CASE WHEN provider_read_enabled = 1 THEN 1 ELSE 0 END) AS provider_read_enabled_count,
            SUM(CASE WHEN provider_write_enabled = 1 THEN 1 ELSE 0 END) AS provider_write_enabled_count,
            SUM(CASE WHEN export_enabled = 1 THEN 1 ELSE 0 END) AS export_enabled_count,
            SUM(CASE WHEN execution_enabled = 1 THEN 1 ELSE 0 END) AS execution_enabled_count
        FROM vault_storage_provider_secret_reference_ledger_entries
        WHERE secret_reference_ledger_id = ?
        """,
        (ledger_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _get_policy_counts(conn: sqlite3.Connection, ledger_id: str) -> Dict[str, int]:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS policy_count,
            COUNT(DISTINCT policy_code) AS policy_code_count,
            SUM(CASE WHEN policy_required = 1 THEN 1 ELSE 0 END) AS policy_required_count,
            SUM(CASE WHEN policy_verified = 1 THEN 1 ELSE 0 END) AS policy_verified_count,
            SUM(CASE WHEN actual_secret_values_stored = 1 THEN 1 ELSE 0 END) AS actual_secret_values_stored_count,
            SUM(CASE WHEN secret_values_present = 1 THEN 1 ELSE 0 END) AS secret_values_present_count,
            SUM(CASE WHEN token_material_present = 1 THEN 1 ELSE 0 END) AS token_material_present_count,
            SUM(CASE WHEN encrypted_secret_payload_present = 1 THEN 1 ELSE 0 END) AS encrypted_secret_payload_present_count,
            SUM(CASE WHEN secret_references_created = 1 THEN 1 ELSE 0 END) AS secret_references_created_count,
            SUM(CASE WHEN secret_references_activated = 1 THEN 1 ELSE 0 END) AS secret_references_activated_count,
            SUM(CASE WHEN provider_connection_tested = 1 THEN 1 ELSE 0 END) AS provider_connection_tested_count,
            SUM(CASE WHEN provider_read_enabled = 1 THEN 1 ELSE 0 END) AS provider_read_enabled_count,
            SUM(CASE WHEN provider_write_enabled = 1 THEN 1 ELSE 0 END) AS provider_write_enabled_count,
            SUM(CASE WHEN export_enabled = 1 THEN 1 ELSE 0 END) AS export_enabled_count,
            SUM(CASE WHEN execution_enabled = 1 THEN 1 ELSE 0 END) AS execution_enabled_count,
            SUM(CASE WHEN tower_review_required = 1 THEN 1 ELSE 0 END) AS tower_review_required_count,
            SUM(CASE WHEN tower_review_granted = 1 THEN 1 ELSE 0 END) AS tower_review_granted_count
        FROM vault_storage_provider_secret_reference_ledger_policies
        WHERE secret_reference_ledger_id = ?
        """,
        (ledger_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _get_blocker_counts(conn: sqlite3.Connection, ledger_id: str) -> Dict[str, int]:
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
        FROM vault_storage_provider_secret_reference_ledger_blockers
        WHERE secret_reference_ledger_id = ?
        """,
        (ledger_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _compact_boundary_source_snapshot(boundary: Dict[str, Any], slots_payload: Dict[str, Any], blockers_payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source_credential_boundary_id": boundary["credential_boundary_id"],
        "source_credential_boundary_pack_id": boundary["pack_id"],
        "source_boundary_status": boundary["boundary_status"],
        "source_section": boundary["section_id"],
        "source_section_range": boundary["section_range"],
        "source_config_contract_id": boundary["source_config_contract_id"],
        "credential_boundary_ready": boundary["credential_boundary_ready"],
        "secret_reference_slots_ready": boundary["secret_reference_slots_ready"],
        "slot_count": slots_payload["slot_count"],
        "slot_code_count": slots_payload["slot_code_count"],
        "reference_created_count": slots_payload["reference_created_count"],
        "reference_activated_count": slots_payload["reference_activated_count"],
        "secret_value_present_count": slots_payload["secret_value_present_count"],
        "token_material_present_count": slots_payload["token_material_present_count"],
        "blocker_count": blockers_payload["blocker_count"],
        "blocks_provider_configuration_count": blockers_payload["blocks_provider_configuration_count"],
        "blocks_provider_read_write_count": blockers_payload["blocks_provider_read_write_count"],
        "blocks_export_count": blockers_payload["blocks_export_count"],
        "blocks_execution_count": blockers_payload["blocks_execution_count"],
        "secret_values_stored": boundary["secret_values_stored"],
        "secret_values_present": boundary["secret_values_present"],
        "token_material_present": boundary["token_material_present"],
        "credentials_configured": boundary["credentials_configured"],
        "secret_references_activated": boundary["secret_references_activated"],
        "provider_configured": boundary["provider_configured"],
        "provider_connection_tested": boundary["provider_connection_tested"],
        "export_enabled": boundary["export_enabled"],
        "execution_enabled": boundary["execution_enabled"],
        "vault_done": boundary["vault_done"],
    }


def _build_ledger_data(boundary: Dict[str, Any], slots_payload: Dict[str, Any], blockers_payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "secret_reference_ledger_schema_version": SCHEMA_VERSION,
        "ledger_type": "REAL_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER",
        "ledger_status": "REAL_SECRET_REFERENCE_LEDGER_OPEN_ALIAS_ONLY_TOWER_LOCKED",
        "real_durable_secret_reference_ledger": True,
        "metadata_source": "VAULT_GP062_REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY",
        "source_credential_boundary_id": boundary["credential_boundary_id"],
        "source_credential_boundary_pack_id": boundary["pack_id"],
        "current_section": {
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "provider_candidate_count": slots_payload["provider_candidate_count"],
        "slot_code_count": slots_payload["slot_code_count"],
        "ledger_entry_count": slots_payload["slot_count"],
        "ledger_policy_count": len(LEDGER_POLICIES),
        "carried_blocker_count": blockers_payload["blocker_count"],
        "ledger_policies": LEDGER_POLICIES,
        "secret_safety_truth": {
            "alias_only_references": True,
            "actual_secret_values_stored": False,
            "secret_values_present": False,
            "token_material_present": False,
            "encrypted_secret_payload_present": False,
            "secret_references_created": False,
            "secret_references_activated": False,
            "credentials_configured": False,
            "provider_endpoint_configured": False,
            "storage_container_configured": False,
            "encryption_configured": False,
        },
        "provider_truth": {
            "secret_reference_ledger_ready": True,
            "ledger_entries_ready": True,
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
        "safe_to_continue_to_gp064": True,
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


def get_storage_provider_secret_reference_ledger_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_secret_reference_ledger(db_path)

    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_secret_reference_ledgers
            WHERE secret_reference_ledger_id = ?
            """,
            (DEFAULT_SECRET_REFERENCE_LEDGER_ID,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Real storage provider secret reference ledger was not initialized.")

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "secret_reference_ledger": _boolify_row(row, {"ledger_data_json": "ledger_data"}),
    }


def get_storage_provider_secret_reference_ledger_entries(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_secret_reference_ledger(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_secret_reference_ledger_entries
            WHERE secret_reference_ledger_id = ?
            ORDER BY provider_candidate_id ASC, source_slot_category ASC, source_slot_code ASC
            """,
            (DEFAULT_SECRET_REFERENCE_LEDGER_ID,),
        ).fetchall()
        counts = _get_entry_counts(conn, DEFAULT_SECRET_REFERENCE_LEDGER_ID)

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "entries": [_boolify_row(row) for row in rows],
    }


def get_storage_provider_secret_reference_ledger_policies(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_secret_reference_ledger(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_secret_reference_ledger_policies
            WHERE secret_reference_ledger_id = ?
            ORDER BY policy_category ASC, policy_code ASC
            """,
            (DEFAULT_SECRET_REFERENCE_LEDGER_ID,),
        ).fetchall()
        counts = _get_policy_counts(conn, DEFAULT_SECRET_REFERENCE_LEDGER_ID)

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "policies": [_boolify_row(row) for row in rows],
    }


def get_storage_provider_secret_reference_ledger_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_secret_reference_ledger(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_secret_reference_ledger_blockers
            WHERE secret_reference_ledger_id = ?
            ORDER BY provider_candidate_id ASC, blocker_category ASC, blocker_code ASC
            """,
            (DEFAULT_SECRET_REFERENCE_LEDGER_ID,),
        ).fetchall()
        counts = _get_blocker_counts(conn, DEFAULT_SECRET_REFERENCE_LEDGER_ID)

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "blockers": [_boolify_row(row) for row in rows],
    }


def get_storage_provider_secret_reference_ledger_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_secret_reference_ledger(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_secret_reference_ledger_events
            WHERE secret_reference_ledger_id = ?
            ORDER BY created_at ASC, event_id ASC
            """,
            (DEFAULT_SECRET_REFERENCE_LEDGER_ID,),
        ).fetchall()

    events = []
    for row in rows:
        events.append(
            {
                "event_id": row["event_id"],
                "secret_reference_ledger_id": row["secret_reference_ledger_id"],
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


def record_storage_provider_secret_reference_ledger_event(
    event_type: str,
    event_payload: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    initialize_real_storage_provider_secret_reference_ledger(db_path)
    payload = dict(event_payload or {})
    payload.update(
        {
            "write_type": "REAL_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER_EVENT",
            "secret_reference_ledger_ready": True,
            "alias_only_references": True,
            "actual_secret_values_stored": False,
            "secret_values_present": False,
            "token_material_present": False,
            "encrypted_secret_payload_present": False,
            "secret_references_created": False,
            "secret_references_activated": False,
            "credentials_configured": False,
            "provider_configuration_ready": False,
            "provider_configured": False,
            "provider_read_enabled": False,
            "provider_write_enabled": False,
            "provider_connection_tested": False,
            "export_enabled": False,
            "execution_enabled": False,
            "vault_done": False,
        }
    )

    with _connect(db_path) as conn:
        event_id = _insert_event(conn, DEFAULT_SECRET_REFERENCE_LEDGER_ID, event_type, payload)
        conn.commit()

    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "secret_reference_ledger_id": DEFAULT_SECRET_REFERENCE_LEDGER_ID,
        "real_sqlite_backed": True,
        "secret_reference_ledger_ready": True,
        "alias_only_references": True,
        "actual_secret_values_stored": False,
        "secret_values_present": False,
        "token_material_present": False,
        "encrypted_secret_payload_present": False,
        "secret_references_created": False,
        "secret_references_activated": False,
        "credentials_configured": False,
        "provider_configuration_ready": False,
        "provider_configured": False,
        "provider_read_enabled": False,
        "provider_write_enabled": False,
        "provider_connection_tested": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    }


def validate_storage_provider_secret_reference_ledger(db_path: Optional[str] = None) -> Dict[str, Any]:
    ledger = get_storage_provider_secret_reference_ledger_record(db_path)["secret_reference_ledger"]
    entries = get_storage_provider_secret_reference_ledger_entries(db_path)
    policies = get_storage_provider_secret_reference_ledger_policies(db_path)
    blockers = get_storage_provider_secret_reference_ledger_blockers(db_path)
    events = get_storage_provider_secret_reference_ledger_events(db_path)

    expected_entries = 30
    expected_policies = len(LEDGER_POLICIES)
    expected_blockers = 140

    checks = [
        {"code": "REAL_SQLITE_SECRET_REFERENCE_LEDGER_EXISTS", "passed": ledger["secret_reference_ledger_id"] == DEFAULT_SECRET_REFERENCE_LEDGER_ID},
        {"code": "SOURCE_GP062_CREDENTIAL_BOUNDARY_ATTACHED", "passed": ledger["source_credential_boundary_id"] == DEFAULT_CREDENTIAL_BOUNDARY_ID},
        {"code": "SECRET_REFERENCE_LEDGER_READY", "passed": ledger["secret_reference_ledger_ready"] is True},
        {"code": "LEDGER_ENTRIES_READY", "passed": ledger["ledger_entries_ready"] is True},
        {"code": "ALIAS_ONLY_REFERENCES", "passed": ledger["alias_only_references"] is True},
        {"code": "REAL_LEDGER_ENTRIES_EXIST", "passed": entries["entry_count"] == expected_entries},
        {"code": "ALL_ENTRIES_REFERENCE_REQUIRED", "passed": entries["reference_required_count"] == expected_entries},
        {"code": "ALL_ENTRIES_ALIAS_ONLY", "passed": entries["alias_only_reference_count"] == expected_entries},
        {"code": "NO_LEDGER_REFERENCES_CREATED", "passed": entries["reference_created_count"] == 0 and ledger["secret_references_created"] is False},
        {"code": "NO_LEDGER_REFERENCES_ACTIVATED", "passed": entries["reference_activated_count"] == 0 and ledger["secret_references_activated"] is False},
        {"code": "NO_ENTRY_ACTUAL_SECRET_VALUES_STORED", "passed": entries["actual_secret_value_stored_count"] == 0},
        {"code": "NO_ENTRY_SECRET_VALUES_PRESENT", "passed": entries["secret_value_present_count"] == 0},
        {"code": "NO_ENTRY_TOKEN_MATERIAL_PRESENT", "passed": entries["token_material_present_count"] == 0},
        {"code": "NO_ENTRY_ENCRYPTED_SECRET_PAYLOAD_PRESENT", "passed": entries["encrypted_secret_payload_present_count"] == 0},
        {"code": "NO_ENTRY_CREDENTIAL_MATERIAL_EXPOSED", "passed": entries["credential_material_exposed_count"] == 0},
        {"code": "ALL_ENTRIES_REDACTED_VIEW_ONLY", "passed": entries["redacted_view_only_count"] == expected_entries},
        {"code": "NO_ENTRY_TOWER_REVIEW_GRANTED", "passed": entries["tower_review_granted_count"] == 0},
        {"code": "NO_ENTRY_CREDENTIALS_CONFIGURED", "passed": entries["credentials_configured_count"] == 0},
        {"code": "NO_ENTRY_PROVIDER_CONNECTION_TESTED", "passed": entries["provider_connection_tested_count"] == 0},
        {"code": "REAL_LEDGER_POLICIES_EXIST", "passed": policies["policy_count"] == expected_policies},
        {"code": "ALL_POLICIES_REQUIRED", "passed": policies["policy_required_count"] == expected_policies},
        {"code": "NO_POLICIES_VERIFIED_YET", "passed": policies["policy_verified_count"] == 0},
        {"code": "NO_POLICY_SECRET_VALUES_PRESENT", "passed": policies["secret_values_present_count"] == 0},
        {"code": "NO_POLICY_TOKEN_MATERIAL_PRESENT", "passed": policies["token_material_present_count"] == 0},
        {"code": "NO_POLICY_REFERENCES_CREATED", "passed": policies["secret_references_created_count"] == 0},
        {"code": "NO_POLICY_REFERENCES_ACTIVATED", "passed": policies["secret_references_activated_count"] == 0},
        {"code": "NO_POLICY_EXPORT", "passed": policies["export_enabled_count"] == 0},
        {"code": "NO_POLICY_EXECUTION", "passed": policies["execution_enabled_count"] == 0},
        {"code": "REAL_LEDGER_BLOCKERS_CARRIED_FORWARD", "passed": blockers["blocker_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_PROVIDER_CONFIGURATION", "passed": blockers["blocks_provider_configuration_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_PROVIDER_READ_WRITE", "passed": blockers["blocks_provider_read_write_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_EXPORT", "passed": blockers["blocks_export_count"] == expected_blockers},
        {"code": "ALL_BLOCKERS_BLOCK_EXECUTION", "passed": blockers["blocks_execution_count"] == expected_blockers},
        {"code": "NO_BLOCKERS_TOWER_REVIEW_GRANTED", "passed": blockers["tower_review_granted_count"] == 0},
        {"code": "NO_BLOCKERS_RESOLVED", "passed": blockers["resolved_count"] == 0},
        {"code": "NO_LEDGER_ACTUAL_SECRET_VALUES_STORED", "passed": ledger["actual_secret_values_stored"] is False},
        {"code": "NO_LEDGER_SECRET_VALUES_PRESENT", "passed": ledger["secret_values_present"] is False},
        {"code": "NO_LEDGER_TOKEN_MATERIAL_PRESENT", "passed": ledger["token_material_present"] is False},
        {"code": "NO_LEDGER_ENCRYPTED_SECRET_PAYLOAD_PRESENT", "passed": ledger["encrypted_secret_payload_present"] is False},
        {"code": "NO_CREDENTIALS_CONFIGURED", "passed": ledger["credentials_configured"] is False},
        {"code": "NO_PROVIDER_ENDPOINT_CONFIGURED", "passed": ledger["provider_endpoint_configured"] is False},
        {"code": "NO_STORAGE_CONTAINER_CONFIGURED", "passed": ledger["storage_container_configured"] is False},
        {"code": "NO_ENCRYPTION_CONFIGURED", "passed": ledger["encryption_configured"] is False},
        {"code": "NO_PROVIDER_CONFIGURATION_READY", "passed": ledger["provider_configuration_ready"] is False},
        {"code": "NO_PROVIDER_CONFIGURED", "passed": ledger["provider_configured"] is False},
        {"code": "NO_PROVIDER_READ_ENABLED", "passed": ledger["provider_read_enabled"] is False},
        {"code": "NO_PROVIDER_WRITE_ENABLED", "passed": ledger["provider_write_enabled"] is False},
        {"code": "NO_PROVIDER_CONNECTION_TESTED", "passed": ledger["provider_connection_tested"] is False},
        {"code": "NO_OBJECT_BODY_VIEW", "passed": ledger["object_body_view_enabled"] is False},
        {"code": "NO_DIRECT_UPLOAD", "passed": ledger["direct_upload_enabled"] is False},
        {"code": "NO_EXPORT", "passed": ledger["export_enabled"] is False},
        {"code": "NO_EXECUTION", "passed": ledger["execution_enabled"] is False},
        {"code": "VAULT_NOT_DONE", "passed": ledger["vault_done"] is False},
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
        "safe_to_continue_to_gp064": len(failed) == 0,
    }


def get_storage_provider_secret_reference_ledger_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp064": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "Continue under ARCHIVE VAULT — REAL STORAGE PROVIDER CONFIGURATION LAYER / GP061-GP070. GP064 should build the real endpoint/namespace contract while still keeping credentials, provider connection, read/write, export, and execution locked.",
            "carry_forward_rules": [
                "Keep the real SQLite secret-reference ledger.",
                "Keep real ledger entries sourced from GP062 slots.",
                "Keep real alias-only references.",
                "Keep real ledger policies.",
                "Keep real blockers carried from GP062.",
                "Build GP064 Real Storage Provider Endpoint Namespace Contract next.",
                "Do not store actual provider secrets.",
                "Do not store tokens, keys, passwords, or credential material.",
                "Do not create or activate secret references yet.",
                "Do not configure credentials yet.",
                "Do not configure provider endpoint yet.",
                "Do not configure storage container yet.",
                "Do not configure encryption yet.",
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


def get_real_storage_provider_secret_reference_ledger_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_secret_reference_ledger(db_path)
    ledger = get_storage_provider_secret_reference_ledger_record(db_path)["secret_reference_ledger"]
    entries = get_storage_provider_secret_reference_ledger_entries(db_path)
    policies = get_storage_provider_secret_reference_ledger_policies(db_path)
    blockers = get_storage_provider_secret_reference_ledger_blockers(db_path)
    events = get_storage_provider_secret_reference_ledger_events(db_path)
    validation = validate_storage_provider_secret_reference_ledger(db_path)

    return {
        "pack": _pack_payload(),
        "ledger_truth": _ledger_truth(ledger, entries, policies, blockers, events["event_count"], validation),
        "store": init,
        "secret_reference_ledger": ledger,
        "entries": entries,
        "policies": policies,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_secret_reference_ledger_next_step()["next_step"],
    }


def get_gp063_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_secret_reference_ledger_home(db_path)
    ledger = home["secret_reference_ledger"]
    entries = home["entries"]
    policies = home["policies"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp063_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_secret_reference_ledger_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_ledger_count": home["store"]["ledger_count"],
            "real_entry_count": home["store"]["entry_count"],
            "real_policy_count": home["store"]["policy_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp062_credential_boundary_attached": True,
            "secret_reference_ledger_ready": ledger["secret_reference_ledger_ready"],
            "ledger_entries_ready": ledger["ledger_entries_ready"],
            "alias_only_references": ledger["alias_only_references"],
            "provider_candidate_count": entries["provider_candidate_count"],
            "slot_code_count": entries["slot_code_count"],
            "policy_code_count": policies["policy_code_count"],
            "reference_created_count": entries["reference_created_count"],
            "reference_activated_count": entries["reference_activated_count"],
            "actual_secret_value_stored_count": entries["actual_secret_value_stored_count"] + policies["actual_secret_values_stored_count"],
            "secret_value_present_count": entries["secret_value_present_count"] + policies["secret_values_present_count"],
            "token_material_present_count": entries["token_material_present_count"] + policies["token_material_present_count"],
            "encrypted_secret_payload_present_count": entries["encrypted_secret_payload_present_count"] + policies["encrypted_secret_payload_present_count"],
            "credential_material_exposed_count": entries["credential_material_exposed_count"],
            "capability_blocker_count": blockers["capability_blocker_count"],
            "criteria_blocker_count": blockers["criteria_blocker_count"],
            "risk_blocker_count": blockers["risk_blocker_count"],
            "blocks_provider_configuration_count": blockers["blocks_provider_configuration_count"],
            "blocks_provider_read_write_count": blockers["blocks_provider_read_write_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "tower_review_granted_count": blockers["tower_review_granted_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp064": validation["safe_to_continue_to_gp064"],
            "vault_done": False,
            "foundation_status": "secret_reference_ledger_ready_safe_to_continue_not_done",
            "actual_secret_values_stored": ledger["actual_secret_values_stored"],
            "secret_values_present": ledger["secret_values_present"],
            "token_material_present": ledger["token_material_present"],
            "encrypted_secret_payload_present": ledger["encrypted_secret_payload_present"],
            "secret_references_created": ledger["secret_references_created"],
            "secret_references_activated": ledger["secret_references_activated"],
            "credentials_configured": ledger["credentials_configured"],
            "provider_endpoint_configured": ledger["provider_endpoint_configured"],
            "storage_container_configured": ledger["storage_container_configured"],
            "encryption_configured": ledger["encryption_configured"],
            "provider_approval_ready": ledger["provider_approval_ready"],
            "provider_activation_ready": ledger["provider_activation_ready"],
            "provider_configuration_ready": ledger["provider_configuration_ready"],
            "provider_read_write_ready": ledger["provider_read_write_ready"],
            "provider_approved": ledger["provider_approved"],
            "provider_activated": ledger["provider_activated"],
            "provider_recommended": ledger["provider_recommended"],
            "provider_selected": ledger["provider_selected"],
            "provider_configured": ledger["provider_configured"],
            "provider_write_enabled": ledger["provider_write_enabled"],
            "provider_read_enabled": ledger["provider_read_enabled"],
            "provider_object_read_claimed": ledger["provider_object_read_claimed"],
            "provider_connection_tested": ledger["provider_connection_tested"],
            "risk_accepted": ledger["risk_accepted"],
            "risk_waived": ledger["risk_waived"],
            "mitigation_approved": ledger["mitigation_approved"],
            "official_storage_receipt": ledger["official_storage_receipt"],
            "finalized_storage_receipt": ledger["finalized_storage_receipt"],
            "closed_storage_receipt": ledger["closed_storage_receipt"],
            "object_body_view_enabled": ledger["object_body_view_enabled"],
            "direct_upload_enabled": ledger["direct_upload_enabled"],
            "export_enabled": ledger["export_enabled"],
            "execution_enabled": ledger["execution_enabled"],
            "clouds_status": "parked_do_not_continue_from_vault_gp063",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "ledger_truth": home["ledger_truth"],
        "routes": home["routes"],
        "secret_reference_ledger": ledger,
        "entries": entries,
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
        "depends_on": ["VAULT_GP062"],
        "foundation_status": "secret_reference_ledger_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_secret_reference_ledger",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }


def _routes_payload() -> Dict[str, str]:
    return {
        "room_title": "Vault Real Storage Provider Secret Reference Ledger",
        "section_header": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "route": "/vault/real-storage-provider-secret-reference-ledger",
        "json_route": "/vault/real-storage-provider-secret-reference-ledger.json",
        "record_route": "/vault/storage-provider-secret-reference-ledger-record.json",
        "entries_route": "/vault/storage-provider-secret-reference-ledger-entries.json",
        "policies_route": "/vault/storage-provider-secret-reference-ledger-policies.json",
        "blockers_route": "/vault/storage-provider-secret-reference-ledger-blockers.json",
        "events_route": "/vault/storage-provider-secret-reference-ledger-events.json",
        "validation_route": "/vault/storage-provider-secret-reference-ledger-validation.json",
        "next_step_route": "/vault/storage-provider-secret-reference-ledger-next-step.json",
        "gp063_status_route": "/vault/gp063-status.json",
    }


def _ledger_truth(ledger, entries, policies, blockers, event_count, validation) -> Dict[str, Any]:
    return {
        "real_storage_provider_secret_reference_ledger_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "real_secret_reference_ledger_exists": ledger["secret_reference_ledger_id"] == DEFAULT_SECRET_REFERENCE_LEDGER_ID,
        "real_secret_reference_ledger_entries_exist": entries["entry_count"] == 30,
        "real_secret_reference_policy_rows_exist": policies["policy_count"] == len(LEDGER_POLICIES),
        "real_secret_reference_blocker_rows_exist": blockers["blocker_count"] == 140,
        "real_event_log_exists": event_count >= 6,
        "source_gp062_credential_boundary_attached": ledger["source_credential_boundary_id"] == DEFAULT_CREDENTIAL_BOUNDARY_ID,
        "validation_passed": validation["valid"],
        "secret_reference_ledger_ready": ledger["secret_reference_ledger_ready"],
        "ledger_entries_ready": ledger["ledger_entries_ready"],
        "alias_only_references": ledger["alias_only_references"],
        "entry_count": entries["entry_count"],
        "policy_count": policies["policy_count"],
        "blocker_count": blockers["blocker_count"],
        "reference_created_count": entries["reference_created_count"],
        "reference_activated_count": entries["reference_activated_count"],
        "actual_secret_value_stored_count": entries["actual_secret_value_stored_count"] + policies["actual_secret_values_stored_count"],
        "secret_value_present_count": entries["secret_value_present_count"] + policies["secret_values_present_count"],
        "token_material_present_count": entries["token_material_present_count"] + policies["token_material_present_count"],
        "encrypted_secret_payload_present_count": entries["encrypted_secret_payload_present_count"] + policies["encrypted_secret_payload_present_count"],
        "credential_material_exposed_count": entries["credential_material_exposed_count"],
        "credentials_configured": ledger["credentials_configured"],
        "provider_configured": ledger["provider_configured"],
        "provider_read_enabled": ledger["provider_read_enabled"],
        "provider_write_enabled": ledger["provider_write_enabled"],
        "provider_connection_tested": ledger["provider_connection_tested"],
        "object_body_view_enabled": ledger["object_body_view_enabled"],
        "direct_upload_enabled": ledger["direct_upload_enabled"],
        "export_enabled": ledger["export_enabled"],
        "execution_enabled": ledger["execution_enabled"],
        "vault_done": ledger["vault_done"],
        "safe_to_continue_to_gp064": validation["safe_to_continue_to_gp064"],
    }


def render_real_storage_provider_secret_reference_ledger_page() -> str:
    home = get_real_storage_provider_secret_reference_ledger_home()
    truth = home["ledger_truth"]
    entries = home["entries"]["entries"]
    policies = home["policies"]["policies"]
    routes = home["routes"]
    next_step = home["next_step"]

    entry_cards = "\n".join(_render_entry_card(item) for item in entries[:9])
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
  <title>Vault Real Storage Provider Secret Reference Ledger · GP063</title>
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
      <div class="eyebrow">Archive Vault · Giant Pack 063</div>
      <div class="eyebrow">Real Storage Provider Configuration Layer · GP061-GP070</div>
      <h1>Real Storage Provider Secret Reference Ledger</h1>
      <p>
        GP063 creates a real secret-reference ledger with alias-only entries,
        policy rows, carried blockers, and event history. It stores no actual secrets,
        tokens, keys, passwords, encrypted secret payloads, or usable credentials.
      </p>
      <div class="metrics">
        <div class="metric"><strong>{home['store']['entry_count']}</strong><span>alias-only ledger entries</span></div>
        <div class="metric"><strong>{home['store']['policy_count']}</strong><span>ledger policies</span></div>
        <div class="metric"><strong>{truth['secret_value_present_count']}</strong><span>secret values present</span></div>
        <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
      </div>
      <div class="chips">
        <span class="pill ok">Secret-reference ledger ready</span>
        <span class="pill ok">Alias-only rows</span>
        <span class="pill ok">Real SQLite-backed</span>
        <span class="pill danger">No secrets stored</span>
        <span class="pill danger">No references activated</span>
        <span class="pill danger">No execution</span>
      </div>
    </section>

    <section class="section">
      <h2>Ledger Entries</h2>
      <p>These are real alias-only ledger entries sourced from GP062 slots. They contain no credential material.</p>
      <div class="grid">{entry_cards}</div>
    </section>

    <section class="section">
      <h2>Ledger Policies</h2>
      <p>These are real policy rows governing lifecycle, audit, redaction, and lock behavior.</p>
      <div class="grid">{policy_cards}</div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Validation Checks</h2>
        <p>GP063 proves the ledger is durable while secrets and provider access remain locked.</p>
        {checks}
      </div>
      <div>
        <h2>Carry Forward to GP064</h2>
        <p>{escape(next_step['owner_notebook_note'])}</p>
        <ul>{rules_html}</ul>
      </div>
    </section>

    <section class="section">
      <h2>GP063 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['record_route'])}</code>
        <code>{escape(routes['entries_route'])}</code>
        <code>{escape(routes['policies_route'])}</code>
        <code>{escape(routes['blockers_route'])}</code>
        <code>{escape(routes['events_route'])}</code>
        <code>{escape(routes['validation_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp063_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_entry_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="title">{escape(item['source_slot_name'])}</div>
        <div class="meta">
          Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
          Category: <code>{escape(item['source_slot_category'])}</code><br>
          Alias: <code>{escape(item['secret_reference_alias'])}</code><br>
          Reference active: <code>{str(item['reference_activated']).lower()}</code><br>
          Secret present: <code>{str(item['secret_value_present']).lower()}</code>
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
