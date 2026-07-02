"""
VAULT GIANT PACK 062 — Real Storage Provider Credential Boundary

CURRENT SECTION:
Archive Vault — Real Storage Provider Configuration Layer
GP061-GP070

This pack creates the real credential boundary for future storage provider
configuration without storing secrets.

Purpose:
- Create a real SQLite-backed credential boundary schema.
- Persist a real credential boundary sourced from GP061.
- Persist real credential boundary rule rows per provider candidate.
- Persist real secret-reference slot rows per provider candidate.
- Carry forward real blockers from GP061.
- Persist real credential boundary events.
- Validate that no secret material, credential values, endpoint credentials, or
  usable tokens are stored.

Important truth:
- GP062 defines the boundary for credentials.
- GP062 does not store actual secrets.
- GP062 does not configure provider credentials.
- GP062 does not activate secret references.
- GP062 does not configure endpoints, storage containers, or encryption.
- GP062 does not approve, activate, select, configure, read, write, export, or execute.
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

from vault.real_storage_provider_config_contract_service import (
    DEFAULT_CONFIG_CONTRACT_ID,
    get_storage_provider_config_blockers,
    get_storage_provider_config_contract_record,
    get_storage_provider_config_requirements,
)


PACK_ID = "VAULT_GP062"
PACK_NAME = "Real Storage Provider Credential Boundary"
SCHEMA_VERSION = "vault.real_storage_provider_credential_boundary.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
SECTION_TITLE = "Archive Vault — Real Storage Provider Configuration Layer"
SECTION_RANGE = "GP061-GP070"

NEXT_PACK = "VAULT_GP063_REAL_STORAGE_PROVIDER_SECRET_REFERENCE_LEDGER"
NEXT_PACK_TITLE = "Real Storage Provider Secret Reference Ledger"

DEFAULT_CREDENTIAL_BOUNDARY_ID = "VSPCB-GP062-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_credential_boundary.sqlite"


BOUNDARY_RULES = [
    {
        "rule_code": "no_plaintext_secret_storage",
        "rule_name": "No plaintext secret storage",
        "rule_category": "secret_safety",
        "rule_message": "Actual secret values must never be stored in repo, notebook cells, JSON responses, logs, or SQLite rows.",
    },
    {
        "rule_code": "tower_secret_authority_required",
        "rule_name": "Tower secret authority required",
        "rule_category": "tower_gate",
        "rule_message": "Tower must remain the authority for any credential reference or credential access.",
    },
    {
        "rule_code": "secret_reference_only",
        "rule_name": "Secret reference only",
        "rule_category": "reference_model",
        "rule_message": "Vault may store secret reference metadata only, not usable credential material.",
    },
    {
        "rule_code": "credential_scope_required",
        "rule_name": "Credential scope required",
        "rule_category": "least_privilege",
        "rule_message": "Each credential reference must define intended scope before any use is possible.",
    },
    {
        "rule_code": "rotation_policy_required",
        "rule_name": "Rotation policy required",
        "rule_category": "lifecycle",
        "rule_message": "Credential rotation policy must exist before provider credentials can be configured.",
    },
    {
        "rule_code": "revocation_policy_required",
        "rule_name": "Revocation policy required",
        "rule_category": "lifecycle",
        "rule_message": "Credential revocation policy must exist before provider credentials can be configured.",
    },
    {
        "rule_code": "access_audit_required",
        "rule_name": "Access audit required",
        "rule_category": "audit",
        "rule_message": "Credential reference access must produce audit events before any provider connection attempt.",
    },
    {
        "rule_code": "environment_separation_required",
        "rule_name": "Environment separation required",
        "rule_category": "environment",
        "rule_message": "Development, test, and production credential references must remain separated.",
    },
    {
        "rule_code": "owner_visibility_redaction_required",
        "rule_name": "Owner visibility redaction required",
        "rule_category": "redaction",
        "rule_message": "Credential boundary views must redact all usable secret material.",
    },
    {
        "rule_code": "no_connection_test_until_boundary_passes",
        "rule_name": "No connection test until boundary passes",
        "rule_category": "connection_lock",
        "rule_message": "Provider connection tests remain locked until the credential boundary is reviewed.",
    },
    {
        "rule_code": "no_write_path_until_credential_boundary_passes",
        "rule_name": "No write path until credential boundary passes",
        "rule_category": "write_lock",
        "rule_message": "Provider write path remains locked until credential boundaries and Tower gates pass.",
    },
    {
        "rule_code": "no_export_until_credential_boundary_passes",
        "rule_name": "No export until credential boundary passes",
        "rule_category": "export_lock",
        "rule_message": "External delivery/export remains locked through the credential boundary layer.",
    },
]


SECRET_REFERENCE_SLOT_SPECS = [
    {
        "slot_code": "provider_access_key_reference",
        "slot_name": "Provider access key reference",
        "slot_category": "access_identity",
    },
    {
        "slot_code": "provider_secret_key_reference",
        "slot_name": "Provider secret key reference",
        "slot_category": "access_secret",
    },
    {
        "slot_code": "provider_token_reference",
        "slot_name": "Provider token reference",
        "slot_category": "session_or_oauth_token",
    },
    {
        "slot_code": "provider_region_or_endpoint_reference",
        "slot_name": "Provider region / endpoint reference",
        "slot_category": "endpoint_reference",
    },
    {
        "slot_code": "provider_container_reference",
        "slot_name": "Provider bucket / container reference",
        "slot_category": "storage_namespace",
    },
    {
        "slot_code": "provider_kms_key_reference",
        "slot_name": "Provider KMS / encryption key reference",
        "slot_category": "encryption_reference",
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


def ensure_storage_provider_credential_boundary_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_credential_boundaries (
                credential_boundary_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_config_contract_id TEXT NOT NULL,
                source_config_pack_id TEXT NOT NULL,
                boundary_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                boundary_data_json TEXT NOT NULL,
                credential_boundary_ready INTEGER NOT NULL DEFAULT 1,
                credential_model_ready INTEGER NOT NULL DEFAULT 1,
                secret_reference_slots_ready INTEGER NOT NULL DEFAULT 1,
                secret_values_stored INTEGER NOT NULL DEFAULT 0,
                secret_values_present INTEGER NOT NULL DEFAULT 0,
                token_material_present INTEGER NOT NULL DEFAULT 0,
                credentials_configured INTEGER NOT NULL DEFAULT 0,
                secret_references_activated INTEGER NOT NULL DEFAULT 0,
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_credential_boundary_rules (
                boundary_rule_id TEXT PRIMARY KEY,
                credential_boundary_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                rule_code TEXT NOT NULL,
                rule_name TEXT NOT NULL,
                rule_category TEXT NOT NULL,
                rule_message TEXT NOT NULL,
                rule_status TEXT NOT NULL,
                rule_required INTEGER NOT NULL DEFAULT 1,
                rule_verified INTEGER NOT NULL DEFAULT 0,
                secret_values_stored INTEGER NOT NULL DEFAULT 0,
                secret_values_present INTEGER NOT NULL DEFAULT 0,
                token_material_present INTEGER NOT NULL DEFAULT 0,
                credentials_configured INTEGER NOT NULL DEFAULT 0,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_granted INTEGER NOT NULL DEFAULT 0,
                provider_connection_tested INTEGER NOT NULL DEFAULT 0,
                provider_read_enabled INTEGER NOT NULL DEFAULT 0,
                provider_write_enabled INTEGER NOT NULL DEFAULT 0,
                export_enabled INTEGER NOT NULL DEFAULT 0,
                execution_enabled INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(credential_boundary_id)
                    REFERENCES vault_storage_provider_credential_boundaries(credential_boundary_id)
                    ON DELETE CASCADE,
                UNIQUE(credential_boundary_id, provider_candidate_id, rule_code)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_secret_reference_slots (
                secret_reference_slot_id TEXT PRIMARY KEY,
                credential_boundary_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                slot_code TEXT NOT NULL,
                slot_name TEXT NOT NULL,
                slot_category TEXT NOT NULL,
                slot_status TEXT NOT NULL,
                reference_required INTEGER NOT NULL DEFAULT 1,
                reference_created INTEGER NOT NULL DEFAULT 0,
                reference_activated INTEGER NOT NULL DEFAULT 0,
                secret_value_stored INTEGER NOT NULL DEFAULT 0,
                secret_value_present INTEGER NOT NULL DEFAULT 0,
                token_material_present INTEGER NOT NULL DEFAULT 0,
                encrypted_secret_present INTEGER NOT NULL DEFAULT 0,
                redacted_view_only INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_granted INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(credential_boundary_id)
                    REFERENCES vault_storage_provider_credential_boundaries(credential_boundary_id)
                    ON DELETE CASCADE,
                UNIQUE(credential_boundary_id, provider_candidate_id, slot_code)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_credential_boundary_blockers (
                credential_blocker_id TEXT PRIMARY KEY,
                credential_boundary_id TEXT NOT NULL,
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
                FOREIGN KEY(credential_boundary_id)
                    REFERENCES vault_storage_provider_credential_boundaries(credential_boundary_id)
                    ON DELETE CASCADE,
                UNIQUE(credential_boundary_id, source_config_blocker_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_credential_boundary_events (
                event_id TEXT PRIMARY KEY,
                credential_boundary_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(credential_boundary_id)
                    REFERENCES vault_storage_provider_credential_boundaries(credential_boundary_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_credential_rules_boundary
            ON vault_storage_provider_credential_boundary_rules(credential_boundary_id, provider_candidate_id, rule_category)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_secret_slots_boundary
            ON vault_storage_provider_secret_reference_slots(credential_boundary_id, provider_candidate_id, slot_category)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_credential_blockers_boundary
            ON vault_storage_provider_credential_boundary_blockers(credential_boundary_id, provider_candidate_id, blocker_category)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_credential_events_boundary
            ON vault_storage_provider_credential_boundary_events(credential_boundary_id, created_at)
            """
        )
        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "tables": [
            "vault_storage_provider_credential_boundaries",
            "vault_storage_provider_credential_boundary_rules",
            "vault_storage_provider_secret_reference_slots",
            "vault_storage_provider_credential_boundary_blockers",
            "vault_storage_provider_credential_boundary_events",
        ],
        "real_sqlite_backed": True,
    }


def initialize_real_storage_provider_credential_boundary(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_credential_boundary_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            """
            SELECT credential_boundary_id
            FROM vault_storage_provider_credential_boundaries
            WHERE credential_boundary_id = ?
            """,
            (DEFAULT_CREDENTIAL_BOUNDARY_ID,),
        ).fetchone()

        if existing is None:
            contract = get_storage_provider_config_contract_record()["contract"]
            requirements_payload = get_storage_provider_config_requirements()
            blockers_payload = get_storage_provider_config_blockers()
            blockers = blockers_payload["blockers"]
            candidates = _unique_provider_candidates(requirements_payload["requirements"])
            boundary_data = _build_boundary_data(contract, requirements_payload, blockers_payload, candidates)
            now = _now_iso()

            _insert_dict(
                conn,
                "vault_storage_provider_credential_boundaries",
                {
                    "credential_boundary_id": DEFAULT_CREDENTIAL_BOUNDARY_ID,
                    "pack_id": PACK_ID,
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    "source_config_contract_id": contract["config_contract_id"],
                    "source_config_pack_id": contract["pack_id"],
                    "boundary_status": "REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_OPEN_SECRET_FREE_TOWER_LOCKED",
                    "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    "boundary_data_json": _json_dumps(boundary_data),
                    "credential_boundary_ready": 1,
                    "credential_model_ready": 1,
                    "secret_reference_slots_ready": 1,
                    "secret_values_stored": 0,
                    "secret_values_present": 0,
                    "token_material_present": 0,
                    "credentials_configured": 0,
                    "secret_references_activated": 0,
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

            for candidate in candidates:
                for rule in BOUNDARY_RULES:
                    _insert_boundary_rule(conn, DEFAULT_CREDENTIAL_BOUNDARY_ID, candidate, rule, now)
                for slot in SECRET_REFERENCE_SLOT_SPECS:
                    _insert_secret_reference_slot(conn, DEFAULT_CREDENTIAL_BOUNDARY_ID, candidate, slot, now)

            for blocker in blockers:
                _insert_credential_blocker(conn, DEFAULT_CREDENTIAL_BOUNDARY_ID, blocker, now)

            rule_counts = _get_rule_counts(conn, DEFAULT_CREDENTIAL_BOUNDARY_ID)
            slot_counts = _get_slot_counts(conn, DEFAULT_CREDENTIAL_BOUNDARY_ID)
            blocker_counts = _get_blocker_counts(conn, DEFAULT_CREDENTIAL_BOUNDARY_ID)

            _insert_event(
                conn,
                DEFAULT_CREDENTIAL_BOUNDARY_ID,
                "REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_CREATED",
                {
                    "pack_id": PACK_ID,
                    "source_config_contract_id": contract["config_contract_id"],
                    "source_config_pack_id": contract["pack_id"],
                    "real_sqlite_backed": True,
                    "credential_boundary_ready": True,
                    "credential_model_ready": True,
                    "secret_reference_slots_ready": True,
                    "secret_values_stored": False,
                    "secret_values_present": False,
                    "token_material_present": False,
                    "credentials_configured": False,
                    "vault_done": False,
                },
            )
            _insert_event(
                conn,
                DEFAULT_CREDENTIAL_BOUNDARY_ID,
                "SOURCE_GP061_CONFIG_CONTRACT_ATTACHED",
                _compact_config_source_snapshot(contract, requirements_payload, blockers_payload),
            )
            _insert_event(
                conn,
                DEFAULT_CREDENTIAL_BOUNDARY_ID,
                "REAL_CREDENTIAL_BOUNDARY_RULES_CREATED",
                rule_counts,
            )
            _insert_event(
                conn,
                DEFAULT_CREDENTIAL_BOUNDARY_ID,
                "REAL_SECRET_REFERENCE_SLOTS_CREATED_SECRET_FREE",
                slot_counts,
            )
            _insert_event(
                conn,
                DEFAULT_CREDENTIAL_BOUNDARY_ID,
                "REAL_CREDENTIAL_BOUNDARY_BLOCKERS_CARRIED_FORWARD",
                blocker_counts,
            )
            _insert_event(
                conn,
                DEFAULT_CREDENTIAL_BOUNDARY_ID,
                "CREDENTIAL_BOUNDARY_LOCKS_CONFIRMED",
                {
                    "no_actual_secrets_stored": True,
                    "credential_configuration_blocked": True,
                    "secret_reference_activation_blocked": True,
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
        "credential_boundary_id": DEFAULT_CREDENTIAL_BOUNDARY_ID,
        "boundary_count": counts["boundary_count"],
        "rule_count": counts["rule_count"],
        "slot_count": counts["slot_count"],
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


def _insert_boundary_rule(
    conn: sqlite3.Connection,
    credential_boundary_id: str,
    candidate: Dict[str, str],
    rule: Dict[str, str],
    now: str,
) -> str:
    boundary_rule_id = (
        f"VSPCBR-{candidate['provider_candidate_id'].split('-', 1)[-1]}-"
        f"{rule['rule_code'].upper().replace('_', '-')}"
    )
    _insert_dict(
        conn,
        "vault_storage_provider_credential_boundary_rules",
        {
            "boundary_rule_id": boundary_rule_id,
            "credential_boundary_id": credential_boundary_id,
            "provider_candidate_id": candidate["provider_candidate_id"],
            "rule_code": rule["rule_code"],
            "rule_name": rule["rule_name"],
            "rule_category": rule["rule_category"],
            "rule_message": rule["rule_message"],
            "rule_status": "REAL_CREDENTIAL_BOUNDARY_RULE_RECORDED_SECRET_FREE_TOWER_LOCKED",
            "rule_required": 1,
            "rule_verified": 0,
            "secret_values_stored": 0,
            "secret_values_present": 0,
            "token_material_present": 0,
            "credentials_configured": 0,
            "tower_review_required": 1,
            "tower_review_granted": 0,
            "provider_connection_tested": 0,
            "provider_read_enabled": 0,
            "provider_write_enabled": 0,
            "export_enabled": 0,
            "execution_enabled": 0,
            "created_at": now,
            "updated_at": now,
        },
    )
    return boundary_rule_id


def _insert_secret_reference_slot(
    conn: sqlite3.Connection,
    credential_boundary_id: str,
    candidate: Dict[str, str],
    slot: Dict[str, str],
    now: str,
) -> str:
    secret_reference_slot_id = (
        f"VSPSRS-{candidate['provider_candidate_id'].split('-', 1)[-1]}-"
        f"{slot['slot_code'].upper().replace('_', '-')}"
    )
    _insert_dict(
        conn,
        "vault_storage_provider_secret_reference_slots",
        {
            "secret_reference_slot_id": secret_reference_slot_id,
            "credential_boundary_id": credential_boundary_id,
            "provider_candidate_id": candidate["provider_candidate_id"],
            "slot_code": slot["slot_code"],
            "slot_name": slot["slot_name"],
            "slot_category": slot["slot_category"],
            "slot_status": "REAL_SECRET_REFERENCE_SLOT_RESERVED_NO_SECRET_VALUE",
            "reference_required": 1,
            "reference_created": 0,
            "reference_activated": 0,
            "secret_value_stored": 0,
            "secret_value_present": 0,
            "token_material_present": 0,
            "encrypted_secret_present": 0,
            "redacted_view_only": 1,
            "tower_review_required": 1,
            "tower_review_granted": 0,
            "created_at": now,
            "updated_at": now,
        },
    )
    return secret_reference_slot_id


def _insert_credential_blocker(
    conn: sqlite3.Connection,
    credential_boundary_id: str,
    blocker: Dict[str, Any],
    now: str,
) -> str:
    credential_blocker_id = f"VSPCBB-{blocker['config_blocker_id'].replace('VSPCFGB-', '')}"
    _insert_dict(
        conn,
        "vault_storage_provider_credential_boundary_blockers",
        {
            "credential_blocker_id": credential_blocker_id,
            "credential_boundary_id": credential_boundary_id,
            "source_config_blocker_id": blocker["config_blocker_id"],
            "source_readiness_blocker_id": blocker["source_readiness_blocker_id"],
            "source_receipt_line_id": blocker["source_receipt_line_id"],
            "source_finding_id": blocker["source_finding_id"],
            "provider_candidate_id": blocker["provider_candidate_id"],
            "blocker_category": blocker["blocker_category"],
            "blocker_code": blocker["blocker_code"],
            "blocker_name": blocker["blocker_name"],
            "severity": blocker["severity"],
            "blocker_status": "REAL_CREDENTIAL_BOUNDARY_BLOCKER_ACTIVE_CARRIED_FROM_GP061",
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
    return credential_blocker_id


def _insert_event(
    conn: sqlite3.Connection,
    credential_boundary_id: str,
    event_type: str,
    event_payload: Dict[str, Any],
) -> str:
    event_id = f"VSPCBE-{uuid.uuid4().hex[:16].upper()}"
    _insert_dict(
        conn,
        "vault_storage_provider_credential_boundary_events",
        {
            "event_id": event_id,
            "credential_boundary_id": credential_boundary_id,
            "event_type": event_type,
            "event_payload_json": _json_dumps(event_payload),
            "created_at": _now_iso(),
        },
    )
    return event_id


def _get_counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        boundary_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_credential_boundaries"
        ).fetchone()["c"]
        rule_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_credential_boundary_rules"
        ).fetchone()["c"]
        slot_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_secret_reference_slots"
        ).fetchone()["c"]
        blocker_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_credential_boundary_blockers"
        ).fetchone()["c"]
        event_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_credential_boundary_events"
        ).fetchone()["c"]

    return {
        "boundary_count": int(boundary_count),
        "rule_count": int(rule_count),
        "slot_count": int(slot_count),
        "blocker_count": int(blocker_count),
        "event_count": int(event_count),
    }


def _get_rule_counts(conn: sqlite3.Connection, credential_boundary_id: str) -> Dict[str, int]:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS rule_count,
            COUNT(DISTINCT provider_candidate_id) AS provider_candidate_count,
            COUNT(DISTINCT rule_code) AS rule_code_count,
            SUM(CASE WHEN rule_required = 1 THEN 1 ELSE 0 END) AS rule_required_count,
            SUM(CASE WHEN rule_verified = 1 THEN 1 ELSE 0 END) AS rule_verified_count,
            SUM(CASE WHEN secret_values_stored = 1 THEN 1 ELSE 0 END) AS secret_values_stored_count,
            SUM(CASE WHEN secret_values_present = 1 THEN 1 ELSE 0 END) AS secret_values_present_count,
            SUM(CASE WHEN token_material_present = 1 THEN 1 ELSE 0 END) AS token_material_present_count,
            SUM(CASE WHEN credentials_configured = 1 THEN 1 ELSE 0 END) AS credentials_configured_count,
            SUM(CASE WHEN tower_review_required = 1 THEN 1 ELSE 0 END) AS tower_review_required_count,
            SUM(CASE WHEN tower_review_granted = 1 THEN 1 ELSE 0 END) AS tower_review_granted_count,
            SUM(CASE WHEN provider_connection_tested = 1 THEN 1 ELSE 0 END) AS provider_connection_tested_count,
            SUM(CASE WHEN provider_read_enabled = 1 THEN 1 ELSE 0 END) AS provider_read_enabled_count,
            SUM(CASE WHEN provider_write_enabled = 1 THEN 1 ELSE 0 END) AS provider_write_enabled_count,
            SUM(CASE WHEN export_enabled = 1 THEN 1 ELSE 0 END) AS export_enabled_count,
            SUM(CASE WHEN execution_enabled = 1 THEN 1 ELSE 0 END) AS execution_enabled_count
        FROM vault_storage_provider_credential_boundary_rules
        WHERE credential_boundary_id = ?
        """,
        (credential_boundary_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _get_slot_counts(conn: sqlite3.Connection, credential_boundary_id: str) -> Dict[str, int]:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS slot_count,
            COUNT(DISTINCT provider_candidate_id) AS provider_candidate_count,
            COUNT(DISTINCT slot_code) AS slot_code_count,
            SUM(CASE WHEN reference_required = 1 THEN 1 ELSE 0 END) AS reference_required_count,
            SUM(CASE WHEN reference_created = 1 THEN 1 ELSE 0 END) AS reference_created_count,
            SUM(CASE WHEN reference_activated = 1 THEN 1 ELSE 0 END) AS reference_activated_count,
            SUM(CASE WHEN secret_value_stored = 1 THEN 1 ELSE 0 END) AS secret_value_stored_count,
            SUM(CASE WHEN secret_value_present = 1 THEN 1 ELSE 0 END) AS secret_value_present_count,
            SUM(CASE WHEN token_material_present = 1 THEN 1 ELSE 0 END) AS token_material_present_count,
            SUM(CASE WHEN encrypted_secret_present = 1 THEN 1 ELSE 0 END) AS encrypted_secret_present_count,
            SUM(CASE WHEN redacted_view_only = 1 THEN 1 ELSE 0 END) AS redacted_view_only_count,
            SUM(CASE WHEN tower_review_required = 1 THEN 1 ELSE 0 END) AS tower_review_required_count,
            SUM(CASE WHEN tower_review_granted = 1 THEN 1 ELSE 0 END) AS tower_review_granted_count
        FROM vault_storage_provider_secret_reference_slots
        WHERE credential_boundary_id = ?
        """,
        (credential_boundary_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _get_blocker_counts(conn: sqlite3.Connection, credential_boundary_id: str) -> Dict[str, int]:
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
        FROM vault_storage_provider_credential_boundary_blockers
        WHERE credential_boundary_id = ?
        """,
        (credential_boundary_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _compact_config_source_snapshot(
    contract: Dict[str, Any],
    requirements_payload: Dict[str, Any],
    blockers_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "source_config_contract_id": contract["config_contract_id"],
        "source_config_pack_id": contract["pack_id"],
        "source_contract_status": contract["contract_status"],
        "source_section": contract["section_id"],
        "source_section_range": contract["section_range"],
        "source_readiness_checkpoint_id": contract["source_readiness_checkpoint_id"],
        "config_contract_ready": contract["config_contract_ready"],
        "provider_candidate_count": requirements_payload["provider_candidate_count"],
        "config_requirement_count": requirements_payload["requirement_count"],
        "config_value_present_count": requirements_payload["config_value_present_count"],
        "secret_value_present_count": requirements_payload["secret_value_present_count"],
        "config_verified_count": requirements_payload["config_verified_count"],
        "blocker_count": blockers_payload["blocker_count"],
        "blocks_provider_configuration_count": blockers_payload["blocks_provider_configuration_count"],
        "blocks_provider_read_write_count": blockers_payload["blocks_provider_read_write_count"],
        "blocks_export_count": blockers_payload["blocks_export_count"],
        "blocks_execution_count": blockers_payload["blocks_execution_count"],
        "provider_configuration_ready": contract["provider_configuration_ready"],
        "provider_configured": contract["provider_configured"],
        "credentials_configured": contract["credentials_configured"],
        "provider_endpoint_configured": contract["provider_endpoint_configured"],
        "storage_container_configured": contract["storage_container_configured"],
        "encryption_configured": contract["encryption_configured"],
        "provider_read_enabled": contract["provider_read_enabled"],
        "provider_write_enabled": contract["provider_write_enabled"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "vault_done": contract["vault_done"],
    }


def _build_boundary_data(
    contract: Dict[str, Any],
    requirements_payload: Dict[str, Any],
    blockers_payload: Dict[str, Any],
    candidates: list[Dict[str, str]],
) -> Dict[str, Any]:
    return {
        "credential_boundary_schema_version": SCHEMA_VERSION,
        "boundary_type": "REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY",
        "boundary_status": "REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_OPEN_SECRET_FREE_TOWER_LOCKED",
        "real_durable_credential_boundary": True,
        "metadata_source": "VAULT_GP061_REAL_STORAGE_PROVIDER_CONFIG_CONTRACT",
        "source_config_contract_id": contract["config_contract_id"],
        "source_config_pack_id": contract["pack_id"],
        "current_section": {
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "provider_candidate_count": len(candidates),
        "boundary_rule_code_count": len(BOUNDARY_RULES),
        "boundary_rule_count": len(candidates) * len(BOUNDARY_RULES),
        "secret_reference_slot_code_count": len(SECRET_REFERENCE_SLOT_SPECS),
        "secret_reference_slot_count": len(candidates) * len(SECRET_REFERENCE_SLOT_SPECS),
        "carried_blocker_count": blockers_payload["blocker_count"],
        "credential_boundary_rules": BOUNDARY_RULES,
        "secret_reference_slot_specs": SECRET_REFERENCE_SLOT_SPECS,
        "secret_safety_truth": {
            "actual_secret_values_stored": False,
            "secret_values_present": False,
            "token_material_present": False,
            "encrypted_secret_present": False,
            "secret_references_activated": False,
            "credentials_configured": False,
            "provider_endpoint_configured": False,
            "storage_container_configured": False,
            "encryption_configured": False,
        },
        "provider_truth": {
            "credential_boundary_ready": True,
            "credential_model_ready": True,
            "secret_reference_slots_ready": True,
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
        "safe_to_continue_to_gp063": True,
    }


def _row_to_boundary(row: sqlite3.Row) -> Dict[str, Any]:
    bool_fields = {
        "credential_boundary_ready",
        "credential_model_ready",
        "secret_reference_slots_ready",
        "secret_values_stored",
        "secret_values_present",
        "token_material_present",
        "credentials_configured",
        "secret_references_activated",
        "provider_endpoint_configured",
        "storage_container_configured",
        "encryption_configured",
        "provider_approval_ready",
        "provider_activation_ready",
        "provider_configuration_ready",
        "provider_read_write_ready",
        "provider_approved",
        "provider_activated",
        "provider_recommended",
        "provider_selected",
        "provider_configured",
        "provider_read_enabled",
        "provider_write_enabled",
        "provider_object_read_claimed",
        "provider_connection_tested",
        "risk_accepted",
        "risk_waived",
        "mitigation_approved",
        "official_storage_receipt",
        "finalized_storage_receipt",
        "closed_storage_receipt",
        "object_body_view_enabled",
        "direct_upload_enabled",
        "export_enabled",
        "execution_enabled",
        "vault_done",
    }
    payload = {}
    for key in row.keys():
        if key == "boundary_data_json":
            payload["boundary_data"] = _json_loads(row[key])
        elif key in bool_fields:
            payload[key] = bool(row[key])
        else:
            payload[key] = row[key]
    return payload


def _row_to_rule(row: sqlite3.Row) -> Dict[str, Any]:
    bool_fields = {
        "rule_required",
        "rule_verified",
        "secret_values_stored",
        "secret_values_present",
        "token_material_present",
        "credentials_configured",
        "tower_review_required",
        "tower_review_granted",
        "provider_connection_tested",
        "provider_read_enabled",
        "provider_write_enabled",
        "export_enabled",
        "execution_enabled",
    }
    return {key: (bool(row[key]) if key in bool_fields else row[key]) for key in row.keys()}


def _row_to_slot(row: sqlite3.Row) -> Dict[str, Any]:
    bool_fields = {
        "reference_required",
        "reference_created",
        "reference_activated",
        "secret_value_stored",
        "secret_value_present",
        "token_material_present",
        "encrypted_secret_present",
        "redacted_view_only",
        "tower_review_required",
        "tower_review_granted",
    }
    return {key: (bool(row[key]) if key in bool_fields else row[key]) for key in row.keys()}


def _row_to_blocker(row: sqlite3.Row) -> Dict[str, Any]:
    bool_fields = {
        "blocks_provider_approval",
        "blocks_provider_activation",
        "blocks_provider_selection",
        "blocks_provider_configuration",
        "blocks_provider_read_write",
        "blocks_object_body_view",
        "blocks_export",
        "blocks_execution",
        "tower_review_required",
        "tower_review_granted",
        "risk_accepted",
        "risk_waived",
        "mitigation_approved",
        "resolved",
    }
    return {key: (bool(row[key]) if key in bool_fields else row[key]) for key in row.keys()}


def _row_to_event(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "event_id": row["event_id"],
        "credential_boundary_id": row["credential_boundary_id"],
        "event_type": row["event_type"],
        "event_payload": _json_loads(row["event_payload_json"]),
        "created_at": row["created_at"],
    }


def get_storage_provider_credential_boundary_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_credential_boundary(db_path)

    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_credential_boundaries
            WHERE credential_boundary_id = ?
            """,
            (DEFAULT_CREDENTIAL_BOUNDARY_ID,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Real storage provider credential boundary was not initialized.")

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "credential_boundary": _row_to_boundary(row),
    }


def get_storage_provider_credential_boundary_rules(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_credential_boundary(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_credential_boundary_rules
            WHERE credential_boundary_id = ?
            ORDER BY provider_candidate_id ASC, rule_category ASC, rule_code ASC
            """,
            (DEFAULT_CREDENTIAL_BOUNDARY_ID,),
        ).fetchall()
        counts = _get_rule_counts(conn, DEFAULT_CREDENTIAL_BOUNDARY_ID)

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "rules": [_row_to_rule(row) for row in rows],
    }


def get_storage_provider_secret_reference_slots(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_credential_boundary(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_secret_reference_slots
            WHERE credential_boundary_id = ?
            ORDER BY provider_candidate_id ASC, slot_category ASC, slot_code ASC
            """,
            (DEFAULT_CREDENTIAL_BOUNDARY_ID,),
        ).fetchall()
        counts = _get_slot_counts(conn, DEFAULT_CREDENTIAL_BOUNDARY_ID)

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "slots": [_row_to_slot(row) for row in rows],
    }


def get_storage_provider_credential_boundary_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_credential_boundary(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_credential_boundary_blockers
            WHERE credential_boundary_id = ?
            ORDER BY provider_candidate_id ASC, blocker_category ASC, blocker_code ASC
            """,
            (DEFAULT_CREDENTIAL_BOUNDARY_ID,),
        ).fetchall()
        counts = _get_blocker_counts(conn, DEFAULT_CREDENTIAL_BOUNDARY_ID)

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "blockers": [_row_to_blocker(row) for row in rows],
    }


def get_storage_provider_credential_boundary_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_credential_boundary(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_credential_boundary_events
            WHERE credential_boundary_id = ?
            ORDER BY created_at ASC, event_id ASC
            """,
            (DEFAULT_CREDENTIAL_BOUNDARY_ID,),
        ).fetchall()

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "event_count": len(rows),
        "events": [_row_to_event(row) for row in rows],
    }


def record_storage_provider_credential_boundary_event(
    event_type: str,
    event_payload: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    initialize_real_storage_provider_credential_boundary(db_path)
    payload = dict(event_payload or {})
    payload.update(
        {
            "write_type": "REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY_EVENT",
            "credential_boundary_ready": True,
            "secret_values_stored": False,
            "secret_values_present": False,
            "token_material_present": False,
            "credentials_configured": False,
            "secret_references_activated": False,
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
        event_id = _insert_event(conn, DEFAULT_CREDENTIAL_BOUNDARY_ID, event_type, payload)
        conn.commit()

    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "credential_boundary_id": DEFAULT_CREDENTIAL_BOUNDARY_ID,
        "real_sqlite_backed": True,
        "credential_boundary_ready": True,
        "secret_values_stored": False,
        "secret_values_present": False,
        "token_material_present": False,
        "credentials_configured": False,
        "secret_references_activated": False,
        "provider_configuration_ready": False,
        "provider_configured": False,
        "provider_read_enabled": False,
        "provider_write_enabled": False,
        "provider_connection_tested": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    }


def validate_storage_provider_credential_boundary(db_path: Optional[str] = None) -> Dict[str, Any]:
    boundary = get_storage_provider_credential_boundary_record(db_path)["credential_boundary"]
    rules = get_storage_provider_credential_boundary_rules(db_path)
    slots = get_storage_provider_secret_reference_slots(db_path)
    blockers = get_storage_provider_credential_boundary_blockers(db_path)
    events = get_storage_provider_credential_boundary_events(db_path)

    expected_rule_count = 5 * len(BOUNDARY_RULES)
    expected_slot_count = 5 * len(SECRET_REFERENCE_SLOT_SPECS)
    expected_blocker_count = 140

    checks = [
        {"code": "REAL_SQLITE_CREDENTIAL_BOUNDARY_EXISTS", "passed": boundary["credential_boundary_id"] == DEFAULT_CREDENTIAL_BOUNDARY_ID},
        {"code": "SOURCE_GP061_CONFIG_CONTRACT_ATTACHED", "passed": boundary["source_config_contract_id"] == DEFAULT_CONFIG_CONTRACT_ID},
        {"code": "CREDENTIAL_BOUNDARY_READY", "passed": boundary["credential_boundary_ready"] is True},
        {"code": "CREDENTIAL_MODEL_READY", "passed": boundary["credential_model_ready"] is True},
        {"code": "SECRET_REFERENCE_SLOTS_READY", "passed": boundary["secret_reference_slots_ready"] is True},
        {"code": "REAL_BOUNDARY_RULE_ROWS_EXIST", "passed": rules["rule_count"] == expected_rule_count},
        {"code": "ALL_BOUNDARY_RULES_REQUIRED", "passed": rules["rule_required_count"] == expected_rule_count},
        {"code": "NO_BOUNDARY_RULES_VERIFIED_YET", "passed": rules["rule_verified_count"] == 0},
        {"code": "NO_RULE_SECRET_VALUES_STORED", "passed": rules["secret_values_stored_count"] == 0},
        {"code": "NO_RULE_SECRET_VALUES_PRESENT", "passed": rules["secret_values_present_count"] == 0},
        {"code": "NO_RULE_TOKEN_MATERIAL_PRESENT", "passed": rules["token_material_present_count"] == 0},
        {"code": "NO_RULE_CREDENTIALS_CONFIGURED", "passed": rules["credentials_configured_count"] == 0},
        {"code": "NO_RULE_TOWER_REVIEW_GRANTED", "passed": rules["tower_review_granted_count"] == 0},
        {"code": "NO_RULE_PROVIDER_CONNECTION_TESTED", "passed": rules["provider_connection_tested_count"] == 0},
        {"code": "NO_RULE_READ_ENABLED", "passed": rules["provider_read_enabled_count"] == 0},
        {"code": "NO_RULE_WRITE_ENABLED", "passed": rules["provider_write_enabled_count"] == 0},
        {"code": "REAL_SECRET_REFERENCE_SLOTS_EXIST", "passed": slots["slot_count"] == expected_slot_count},
        {"code": "ALL_SECRET_REFERENCE_SLOTS_REQUIRED", "passed": slots["reference_required_count"] == expected_slot_count},
        {"code": "NO_SECRET_REFERENCES_CREATED", "passed": slots["reference_created_count"] == 0},
        {"code": "NO_SECRET_REFERENCES_ACTIVATED", "passed": slots["reference_activated_count"] == 0},
        {"code": "NO_SLOT_SECRET_VALUES_STORED", "passed": slots["secret_value_stored_count"] == 0},
        {"code": "NO_SLOT_SECRET_VALUES_PRESENT", "passed": slots["secret_value_present_count"] == 0},
        {"code": "NO_SLOT_TOKEN_MATERIAL_PRESENT", "passed": slots["token_material_present_count"] == 0},
        {"code": "NO_SLOT_ENCRYPTED_SECRET_PRESENT", "passed": slots["encrypted_secret_present_count"] == 0},
        {"code": "ALL_SECRET_SLOTS_REDACTED_VIEW_ONLY", "passed": slots["redacted_view_only_count"] == expected_slot_count},
        {"code": "NO_SLOT_TOWER_REVIEW_GRANTED", "passed": slots["tower_review_granted_count"] == 0},
        {"code": "REAL_CREDENTIAL_BLOCKERS_CARRIED_FORWARD", "passed": blockers["blocker_count"] == expected_blocker_count},
        {"code": "ALL_BLOCKERS_BLOCK_PROVIDER_CONFIGURATION", "passed": blockers["blocks_provider_configuration_count"] == expected_blocker_count},
        {"code": "ALL_BLOCKERS_BLOCK_PROVIDER_READ_WRITE", "passed": blockers["blocks_provider_read_write_count"] == expected_blocker_count},
        {"code": "ALL_BLOCKERS_BLOCK_EXPORT", "passed": blockers["blocks_export_count"] == expected_blocker_count},
        {"code": "ALL_BLOCKERS_BLOCK_EXECUTION", "passed": blockers["blocks_execution_count"] == expected_blocker_count},
        {"code": "NO_BLOCKERS_TOWER_REVIEW_GRANTED", "passed": blockers["tower_review_granted_count"] == 0},
        {"code": "NO_BLOCKERS_RESOLVED", "passed": blockers["resolved_count"] == 0},
        {"code": "NO_BOUNDARY_SECRET_VALUES_STORED", "passed": boundary["secret_values_stored"] is False},
        {"code": "NO_BOUNDARY_SECRET_VALUES_PRESENT", "passed": boundary["secret_values_present"] is False},
        {"code": "NO_BOUNDARY_TOKEN_MATERIAL_PRESENT", "passed": boundary["token_material_present"] is False},
        {"code": "NO_CREDENTIALS_CONFIGURED", "passed": boundary["credentials_configured"] is False},
        {"code": "NO_SECRET_REFERENCES_ACTIVATED_BOUNDARY", "passed": boundary["secret_references_activated"] is False},
        {"code": "NO_ENDPOINT_CONFIGURED", "passed": boundary["provider_endpoint_configured"] is False},
        {"code": "NO_STORAGE_CONTAINER_CONFIGURED", "passed": boundary["storage_container_configured"] is False},
        {"code": "NO_ENCRYPTION_CONFIGURED", "passed": boundary["encryption_configured"] is False},
        {"code": "NO_PROVIDER_CONFIGURATION_READY", "passed": boundary["provider_configuration_ready"] is False},
        {"code": "NO_PROVIDER_CONFIGURED", "passed": boundary["provider_configured"] is False},
        {"code": "NO_PROVIDER_READ_ENABLED", "passed": boundary["provider_read_enabled"] is False},
        {"code": "NO_PROVIDER_WRITE_ENABLED", "passed": boundary["provider_write_enabled"] is False},
        {"code": "NO_PROVIDER_CONNECTION_TESTED", "passed": boundary["provider_connection_tested"] is False},
        {"code": "NO_OBJECT_BODY_VIEW", "passed": boundary["object_body_view_enabled"] is False},
        {"code": "NO_DIRECT_UPLOAD", "passed": boundary["direct_upload_enabled"] is False},
        {"code": "NO_EXPORT", "passed": boundary["export_enabled"] is False},
        {"code": "NO_EXECUTION", "passed": boundary["execution_enabled"] is False},
        {"code": "VAULT_NOT_DONE", "passed": boundary["vault_done"] is False},
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
        "safe_to_continue_to_gp063": len(failed) == 0,
    }


def get_storage_provider_credential_boundary_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp063": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "Continue under ARCHIVE VAULT — REAL STORAGE PROVIDER CONFIGURATION LAYER / GP061-GP070. GP063 should build the real secret-reference ledger while still storing no actual secret material.",
            "carry_forward_rules": [
                "Keep the real SQLite credential boundary.",
                "Keep real credential boundary rule rows.",
                "Keep real secret-reference slot rows.",
                "Keep real blockers carried from GP061.",
                "Build GP063 Real Storage Provider Secret Reference Ledger next.",
                "Do not store actual provider secrets.",
                "Do not store tokens, keys, passwords, or credential material.",
                "Do not activate secret references yet.",
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


def get_real_storage_provider_credential_boundary_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_credential_boundary(db_path)
    boundary = get_storage_provider_credential_boundary_record(db_path)["credential_boundary"]
    rules = get_storage_provider_credential_boundary_rules(db_path)
    slots = get_storage_provider_secret_reference_slots(db_path)
    blockers = get_storage_provider_credential_boundary_blockers(db_path)
    events = get_storage_provider_credential_boundary_events(db_path)
    validation = validate_storage_provider_credential_boundary(db_path)

    return {
        "pack": _pack_payload(),
        "credential_truth": _credential_truth(boundary, rules, slots, blockers, events["event_count"], validation),
        "store": init,
        "credential_boundary": boundary,
        "rules": rules,
        "slots": slots,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_credential_boundary_next_step()["next_step"],
    }


def get_gp062_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_credential_boundary_home(db_path)
    boundary = home["credential_boundary"]
    rules = home["rules"]
    slots = home["slots"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp062_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_credential_boundary_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_boundary_count": home["store"]["boundary_count"],
            "real_rule_count": home["store"]["rule_count"],
            "real_slot_count": home["store"]["slot_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp061_config_contract_attached": True,
            "credential_boundary_ready": boundary["credential_boundary_ready"],
            "credential_model_ready": boundary["credential_model_ready"],
            "secret_reference_slots_ready": boundary["secret_reference_slots_ready"],
            "provider_candidate_count": rules["provider_candidate_count"],
            "rule_code_count": rules["rule_code_count"],
            "slot_code_count": slots["slot_code_count"],
            "rule_verified_count": rules["rule_verified_count"],
            "reference_created_count": slots["reference_created_count"],
            "reference_activated_count": slots["reference_activated_count"],
            "secret_values_stored_count": rules["secret_values_stored_count"] + slots["secret_value_stored_count"],
            "secret_values_present_count": rules["secret_values_present_count"] + slots["secret_value_present_count"],
            "token_material_present_count": rules["token_material_present_count"] + slots["token_material_present_count"],
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
            "safe_to_continue_to_gp063": validation["safe_to_continue_to_gp063"],
            "vault_done": False,
            "foundation_status": "credential_boundary_ready_safe_to_continue_not_done",
            "secret_values_stored": boundary["secret_values_stored"],
            "secret_values_present": boundary["secret_values_present"],
            "token_material_present": boundary["token_material_present"],
            "credentials_configured": boundary["credentials_configured"],
            "secret_references_activated": boundary["secret_references_activated"],
            "provider_endpoint_configured": boundary["provider_endpoint_configured"],
            "storage_container_configured": boundary["storage_container_configured"],
            "encryption_configured": boundary["encryption_configured"],
            "provider_approval_ready": boundary["provider_approval_ready"],
            "provider_activation_ready": boundary["provider_activation_ready"],
            "provider_configuration_ready": boundary["provider_configuration_ready"],
            "provider_read_write_ready": boundary["provider_read_write_ready"],
            "provider_approved": boundary["provider_approved"],
            "provider_activated": boundary["provider_activated"],
            "provider_recommended": boundary["provider_recommended"],
            "provider_selected": boundary["provider_selected"],
            "provider_configured": boundary["provider_configured"],
            "provider_write_enabled": boundary["provider_write_enabled"],
            "provider_read_enabled": boundary["provider_read_enabled"],
            "provider_object_read_claimed": boundary["provider_object_read_claimed"],
            "provider_connection_tested": boundary["provider_connection_tested"],
            "risk_accepted": boundary["risk_accepted"],
            "risk_waived": boundary["risk_waived"],
            "mitigation_approved": boundary["mitigation_approved"],
            "official_storage_receipt": boundary["official_storage_receipt"],
            "finalized_storage_receipt": boundary["finalized_storage_receipt"],
            "closed_storage_receipt": boundary["closed_storage_receipt"],
            "object_body_view_enabled": boundary["object_body_view_enabled"],
            "direct_upload_enabled": boundary["direct_upload_enabled"],
            "export_enabled": boundary["export_enabled"],
            "execution_enabled": boundary["execution_enabled"],
            "clouds_status": "parked_do_not_continue_from_vault_gp062",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "credential_truth": home["credential_truth"],
        "routes": home["routes"],
        "credential_boundary": boundary,
        "rules": rules,
        "slots": slots,
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
        "depends_on": ["VAULT_GP061"],
        "foundation_status": "credential_boundary_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_credential_boundary",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }


def _routes_payload() -> Dict[str, str]:
    return {
        "room_title": "Vault Real Storage Provider Credential Boundary",
        "section_header": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "route": "/vault/real-storage-provider-credential-boundary",
        "json_route": "/vault/real-storage-provider-credential-boundary.json",
        "record_route": "/vault/storage-provider-credential-boundary-record.json",
        "rules_route": "/vault/storage-provider-credential-boundary-rules.json",
        "slots_route": "/vault/storage-provider-secret-reference-slots.json",
        "blockers_route": "/vault/storage-provider-credential-boundary-blockers.json",
        "events_route": "/vault/storage-provider-credential-boundary-events.json",
        "validation_route": "/vault/storage-provider-credential-boundary-validation.json",
        "next_step_route": "/vault/storage-provider-credential-boundary-next-step.json",
        "gp062_status_route": "/vault/gp062-status.json",
    }


def _credential_truth(
    boundary: Dict[str, Any],
    rules: Dict[str, Any],
    slots: Dict[str, Any],
    blockers: Dict[str, Any],
    event_count: int,
    validation: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "real_storage_provider_credential_boundary_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "real_credential_boundary_exists": boundary["credential_boundary_id"] == DEFAULT_CREDENTIAL_BOUNDARY_ID,
        "real_credential_rule_rows_exist": rules["rule_count"] == 5 * len(BOUNDARY_RULES),
        "real_secret_reference_slot_rows_exist": slots["slot_count"] == 5 * len(SECRET_REFERENCE_SLOT_SPECS),
        "real_credential_blocker_rows_exist": blockers["blocker_count"] == 140,
        "real_event_log_exists": event_count >= 6,
        "source_gp061_config_contract_attached": boundary["source_config_contract_id"] == DEFAULT_CONFIG_CONTRACT_ID,
        "validation_passed": validation["valid"],
        "credential_boundary_ready": boundary["credential_boundary_ready"],
        "credential_model_ready": boundary["credential_model_ready"],
        "secret_reference_slots_ready": boundary["secret_reference_slots_ready"],
        "rule_count": rules["rule_count"],
        "slot_count": slots["slot_count"],
        "blocker_count": blockers["blocker_count"],
        "secret_values_stored_count": rules["secret_values_stored_count"] + slots["secret_value_stored_count"],
        "secret_values_present_count": rules["secret_values_present_count"] + slots["secret_value_present_count"],
        "token_material_present_count": rules["token_material_present_count"] + slots["token_material_present_count"],
        "reference_created_count": slots["reference_created_count"],
        "reference_activated_count": slots["reference_activated_count"],
        "credentials_configured": boundary["credentials_configured"],
        "provider_configured": boundary["provider_configured"],
        "provider_read_enabled": boundary["provider_read_enabled"],
        "provider_write_enabled": boundary["provider_write_enabled"],
        "provider_connection_tested": boundary["provider_connection_tested"],
        "object_body_view_enabled": boundary["object_body_view_enabled"],
        "direct_upload_enabled": boundary["direct_upload_enabled"],
        "export_enabled": boundary["export_enabled"],
        "execution_enabled": boundary["execution_enabled"],
        "vault_done": boundary["vault_done"],
        "safe_to_continue_to_gp063": validation["safe_to_continue_to_gp063"],
    }


def render_real_storage_provider_credential_boundary_page() -> str:
    home = get_real_storage_provider_credential_boundary_home()
    truth = home["credential_truth"]
    rules = home["rules"]["rules"]
    slots = home["slots"]["slots"]
    routes = home["routes"]
    next_step = home["next_step"]

    rule_cards = "\n".join(_render_rule_card(item) for item in rules[:9])
    slot_cards = "\n".join(_render_slot_card(item) for item in slots[:9])
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
  <title>Vault Real Storage Provider Credential Boundary · GP062</title>
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
      <div class="eyebrow">Archive Vault · Giant Pack 062</div>
      <div class="eyebrow">Real Storage Provider Configuration Layer · GP061-GP070</div>
      <h1>Real Storage Provider Credential Boundary</h1>
      <p>
        GP062 creates a real credential boundary with secret-free rule rows,
        secret-reference slots, carried blockers, and event history. It stores no actual
        provider secrets, keys, tokens, passwords, or usable credential material.
      </p>
      <div class="metrics">
        <div class="metric"><strong>{home['store']['rule_count']}</strong><span>credential boundary rules</span></div>
        <div class="metric"><strong>{home['store']['slot_count']}</strong><span>secret-reference slots</span></div>
        <div class="metric"><strong>{truth['secret_values_present_count']}</strong><span>secret values present</span></div>
        <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
      </div>
      <div class="chips">
        <span class="pill ok">Credential boundary ready</span>
        <span class="pill ok">Secret-reference slots reserved</span>
        <span class="pill ok">Real SQLite-backed</span>
        <span class="pill danger">No secrets stored</span>
        <span class="pill danger">No credentials configured</span>
        <span class="pill danger">No execution</span>
      </div>
    </section>

    <section class="section">
      <h2>Credential Boundary Rules</h2>
      <p>These are real rule rows. They are secret-free and Tower-locked.</p>
      <div class="grid">{rule_cards}</div>
    </section>

    <section class="section">
      <h2>Secret-Reference Slots</h2>
      <p>These are reserved reference slots only. They contain no credential material.</p>
      <div class="grid">{slot_cards}</div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Validation Checks</h2>
        <p>GP062 proves the boundary is durable while secrets and provider access remain locked.</p>
        {checks}
      </div>
      <div>
        <h2>Carry Forward to GP063</h2>
        <p>{escape(next_step['owner_notebook_note'])}</p>
        <ul>{rules_html}</ul>
      </div>
    </section>

    <section class="section">
      <h2>GP062 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['record_route'])}</code>
        <code>{escape(routes['rules_route'])}</code>
        <code>{escape(routes['slots_route'])}</code>
        <code>{escape(routes['blockers_route'])}</code>
        <code>{escape(routes['events_route'])}</code>
        <code>{escape(routes['validation_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp062_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_rule_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="title">{escape(item['rule_name'])}</div>
        <div class="meta">
          Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
          Category: <code>{escape(item['rule_category'])}</code><br>
          Code: <code>{escape(item['rule_code'])}</code><br>
          Secret present: <code>{str(item['secret_values_present']).lower()}</code><br>
          Credentials configured: <code>{str(item['credentials_configured']).lower()}</code>
        </div>
      </article>
    """


def _render_slot_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="title">{escape(item['slot_name'])}</div>
        <div class="meta">
          Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
          Category: <code>{escape(item['slot_category'])}</code><br>
          Code: <code>{escape(item['slot_code'])}</code><br>
          Reference active: <code>{str(item['reference_activated']).lower()}</code><br>
          Secret stored: <code>{str(item['secret_value_stored']).lower()}</code>
        </div>
      </article>
    """
