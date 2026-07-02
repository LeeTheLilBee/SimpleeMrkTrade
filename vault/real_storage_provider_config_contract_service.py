"""
VAULT GIANT PACK 061 — Real Storage Provider Config Contract

CURRENT SECTION:
Archive Vault — Real Storage Provider Configuration Layer
GP061-GP070

This pack starts the real storage provider configuration layer with a durable
SQLite-backed configuration contract.

Purpose:
- Create a real storage provider config contract schema.
- Persist a real config contract sourced from GP060.
- Persist real config requirement rows per provider candidate.
- Carry forward real blockers from GP060 readiness.
- Persist a real config contract event log.
- Validate that configuration remains locked until real credential/config steps are built.

Important truth:
- GP061 creates the real configuration contract.
- GP061 does not configure credentials, endpoints, containers, or encryption.
- GP061 does not approve, activate, recommend, select, or configure a provider.
- GP061 does not enable provider read/write.
- GP061 does not accept/waive risk or approve mitigation.
- GP061 does not unlock object bodies, raw storage, upload, export, or execution.
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

from vault.storage_provider_prep_readiness_checkpoint_service import (
    DEFAULT_READINESS_CHECKPOINT_ID,
    get_storage_provider_prep_readiness_blockers,
    get_storage_provider_prep_readiness_checkpoint_record,
)


PACK_ID = "VAULT_GP061"
PACK_NAME = "Real Storage Provider Config Contract"
SCHEMA_VERSION = "vault.real_storage_provider_config_contract.v1"

SECTION_ID = "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
SECTION_TITLE = "Archive Vault — Real Storage Provider Configuration Layer"
SECTION_RANGE = "GP061-GP070"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
PREVIOUS_SECTION_RANGE = "GP051-GP060"

NEXT_PACK = "VAULT_GP062_REAL_STORAGE_PROVIDER_CREDENTIAL_BOUNDARY"
NEXT_PACK_TITLE = "Real Storage Provider Credential Boundary"

DEFAULT_CONFIG_CONTRACT_ID = "VSPCCFG-GP061-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_CONFIG_CONTRACT_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_config_contract.sqlite"


CONFIG_REQUIREMENTS = [
    {
        "requirement_code": "credential_boundary_contract",
        "requirement_name": "Credential boundary contract",
        "requirement_category": "credentials",
        "requirement_message": "Provider credentials must be modeled through a Tower-controlled boundary before any secret exists.",
    },
    {
        "requirement_code": "secret_storage_policy",
        "requirement_name": "Secret storage policy",
        "requirement_category": "credentials",
        "requirement_message": "Secrets cannot be stored in repo, config files, notebook output, or plain text.",
    },
    {
        "requirement_code": "provider_endpoint_contract",
        "requirement_name": "Provider endpoint contract",
        "requirement_category": "endpoint",
        "requirement_message": "Provider endpoint/region/account namespace must be explicitly recorded before connection testing.",
    },
    {
        "requirement_code": "storage_namespace_contract",
        "requirement_name": "Storage namespace contract",
        "requirement_category": "namespace",
        "requirement_message": "Bucket/container/project namespace must be explicitly recorded and locked before object writes.",
    },
    {
        "requirement_code": "object_key_policy",
        "requirement_name": "Object key policy",
        "requirement_category": "object_mapping",
        "requirement_message": "Object key/path mapping must be controlled before upload or object persistence.",
    },
    {
        "requirement_code": "metadata_schema_binding",
        "requirement_name": "Metadata schema binding",
        "requirement_category": "metadata",
        "requirement_message": "Provider metadata fields must bind to Vault metadata records before any write path.",
    },
    {
        "requirement_code": "checksum_integrity_policy",
        "requirement_name": "Checksum integrity policy",
        "requirement_category": "integrity",
        "requirement_message": "Checksum/hash policy must be required before stored objects can be trusted.",
    },
    {
        "requirement_code": "encryption_key_policy",
        "requirement_name": "Encryption key policy",
        "requirement_category": "encryption",
        "requirement_message": "Encryption policy and key ownership must be recorded before provider activation.",
    },
    {
        "requirement_code": "write_path_policy",
        "requirement_name": "Write path policy",
        "requirement_category": "write_path",
        "requirement_message": "Provider write path must stay locked until credential and permission contracts pass.",
    },
    {
        "requirement_code": "read_path_policy",
        "requirement_name": "Read path policy",
        "requirement_category": "read_path",
        "requirement_message": "Provider read path must stay locked until object visibility and redaction rules pass.",
    },
    {
        "requirement_code": "audit_event_binding",
        "requirement_name": "Audit event binding",
        "requirement_category": "audit",
        "requirement_message": "Provider storage actions must bind to immutable Vault/Tower audit events.",
    },
    {
        "requirement_code": "retention_hold_policy",
        "requirement_name": "Retention hold policy",
        "requirement_category": "retention",
        "requirement_message": "Retention and deletion behavior must be recorded before production storage.",
    },
    {
        "requirement_code": "restore_test_policy",
        "requirement_name": "Restore test policy",
        "requirement_category": "restore",
        "requirement_message": "Restore testing must be defined before provider activation can be considered.",
    },
    {
        "requirement_code": "redaction_view_policy",
        "requirement_name": "Redaction view policy",
        "requirement_category": "redaction",
        "requirement_message": "Provider reads must preserve private/owner/shareable redaction boundaries.",
    },
    {
        "requirement_code": "tower_permission_gate",
        "requirement_name": "Tower permission gate",
        "requirement_category": "tower_gate",
        "requirement_message": "Tower permission gates must remain the authority for any provider config or access.",
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


def ensure_storage_provider_config_contract_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_config_contracts (
                config_contract_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_readiness_checkpoint_id TEXT NOT NULL,
                source_readiness_pack_id TEXT NOT NULL,
                contract_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                contract_data_json TEXT NOT NULL,
                config_contract_ready INTEGER NOT NULL DEFAULT 1,
                provider_approval_ready INTEGER NOT NULL DEFAULT 0,
                provider_activation_ready INTEGER NOT NULL DEFAULT 0,
                provider_configuration_ready INTEGER NOT NULL DEFAULT 0,
                provider_read_write_ready INTEGER NOT NULL DEFAULT 0,
                provider_approved INTEGER NOT NULL DEFAULT 0,
                provider_activated INTEGER NOT NULL DEFAULT 0,
                provider_recommended INTEGER NOT NULL DEFAULT 0,
                provider_selected INTEGER NOT NULL DEFAULT 0,
                provider_configured INTEGER NOT NULL DEFAULT 0,
                credentials_configured INTEGER NOT NULL DEFAULT 0,
                provider_endpoint_configured INTEGER NOT NULL DEFAULT 0,
                storage_container_configured INTEGER NOT NULL DEFAULT 0,
                encryption_configured INTEGER NOT NULL DEFAULT 0,
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_config_requirements (
                config_requirement_id TEXT PRIMARY KEY,
                config_contract_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                requirement_code TEXT NOT NULL,
                requirement_name TEXT NOT NULL,
                requirement_category TEXT NOT NULL,
                requirement_message TEXT NOT NULL,
                requirement_status TEXT NOT NULL,
                required_for_configuration INTEGER NOT NULL DEFAULT 1,
                config_value_present INTEGER NOT NULL DEFAULT 0,
                secret_value_present INTEGER NOT NULL DEFAULT 0,
                config_verified INTEGER NOT NULL DEFAULT 0,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_granted INTEGER NOT NULL DEFAULT 0,
                provider_configured INTEGER NOT NULL DEFAULT 0,
                provider_read_enabled INTEGER NOT NULL DEFAULT 0,
                provider_write_enabled INTEGER NOT NULL DEFAULT 0,
                export_enabled INTEGER NOT NULL DEFAULT 0,
                execution_enabled INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(config_contract_id)
                    REFERENCES vault_storage_provider_config_contracts(config_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(config_contract_id, provider_candidate_id, requirement_code)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_config_blockers (
                config_blocker_id TEXT PRIMARY KEY,
                config_contract_id TEXT NOT NULL,
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
                FOREIGN KEY(config_contract_id)
                    REFERENCES vault_storage_provider_config_contracts(config_contract_id)
                    ON DELETE CASCADE,
                UNIQUE(config_contract_id, source_readiness_blocker_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_config_events (
                event_id TEXT PRIMARY KEY,
                config_contract_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(config_contract_id)
                    REFERENCES vault_storage_provider_config_contracts(config_contract_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_config_requirements_contract
            ON vault_storage_provider_config_requirements(config_contract_id, provider_candidate_id, requirement_category)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_config_blockers_contract
            ON vault_storage_provider_config_blockers(config_contract_id, provider_candidate_id, blocker_category)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_config_events_contract
            ON vault_storage_provider_config_events(config_contract_id, created_at)
            """
        )
        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "tables": [
            "vault_storage_provider_config_contracts",
            "vault_storage_provider_config_requirements",
            "vault_storage_provider_config_blockers",
            "vault_storage_provider_config_events",
        ],
        "real_sqlite_backed": True,
    }


def initialize_real_storage_provider_config_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_config_contract_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            """
            SELECT config_contract_id
            FROM vault_storage_provider_config_contracts
            WHERE config_contract_id = ?
            """,
            (DEFAULT_CONFIG_CONTRACT_ID,),
        ).fetchone()

        if existing is None:
            readiness = get_storage_provider_prep_readiness_checkpoint_record()["checkpoint"]
            blockers_payload = get_storage_provider_prep_readiness_blockers()
            blockers = blockers_payload["blockers"]
            candidates = _unique_provider_candidates(blockers)
            contract_data = _build_contract_data(readiness, blockers_payload, candidates)
            now = _now_iso()

            conn.execute(
                """
                INSERT INTO vault_storage_provider_config_contracts (
                    config_contract_id,
                    pack_id,
                    section_id,
                    section_range,
                    source_readiness_checkpoint_id,
                    source_readiness_pack_id,
                    contract_status,
                    tower_authority_status,
                    contract_data_json,
                    config_contract_ready,
                    provider_approval_ready,
                    provider_activation_ready,
                    provider_configuration_ready,
                    provider_read_write_ready,
                    provider_approved,
                    provider_activated,
                    provider_recommended,
                    provider_selected,
                    provider_configured,
                    credentials_configured,
                    provider_endpoint_configured,
                    storage_container_configured,
                    encryption_configured,
                    provider_read_enabled,
                    provider_write_enabled,
                    provider_object_read_claimed,
                    provider_connection_tested,
                    risk_accepted,
                    risk_waived,
                    mitigation_approved,
                    official_storage_receipt,
                    finalized_storage_receipt,
                    closed_storage_receipt,
                    object_body_view_enabled,
                    direct_upload_enabled,
                    export_enabled,
                    execution_enabled,
                    vault_done,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    DEFAULT_CONFIG_CONTRACT_ID,
                    PACK_ID,
                    SECTION_ID,
                    SECTION_RANGE,
                    readiness["checkpoint_id"],
                    readiness["pack_id"],
                    "REAL_STORAGE_PROVIDER_CONFIG_CONTRACT_OPEN_TOWER_LOCKED",
                    "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    _json_dumps(contract_data),
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    now,
                    now,
                ),
            )

            for candidate in candidates:
                for requirement in CONFIG_REQUIREMENTS:
                    _insert_config_requirement(conn, DEFAULT_CONFIG_CONTRACT_ID, candidate, requirement, now)

            for blocker in blockers:
                _insert_config_blocker(conn, DEFAULT_CONFIG_CONTRACT_ID, blocker, now)

            requirement_counts = _get_requirement_counts(conn, DEFAULT_CONFIG_CONTRACT_ID)
            blocker_counts = _get_blocker_counts(conn, DEFAULT_CONFIG_CONTRACT_ID)

            _insert_event(
                conn,
                DEFAULT_CONFIG_CONTRACT_ID,
                "REAL_STORAGE_PROVIDER_CONFIG_CONTRACT_CREATED",
                {
                    "pack_id": PACK_ID,
                    "source_readiness_checkpoint_id": readiness["checkpoint_id"],
                    "source_readiness_pack_id": readiness["pack_id"],
                    "real_sqlite_backed": True,
                    "contract_status": "REAL_STORAGE_PROVIDER_CONFIG_CONTRACT_OPEN_TOWER_LOCKED",
                    "config_contract_ready": True,
                    "provider_configuration_ready": False,
                    "provider_configured": False,
                    "credentials_configured": False,
                    "export_enabled": False,
                    "execution_enabled": False,
                    "vault_done": False,
                },
            )
            _insert_event(
                conn,
                DEFAULT_CONFIG_CONTRACT_ID,
                "SOURCE_GP060_READINESS_CHECKPOINT_ATTACHED",
                _compact_readiness_source_snapshot(readiness, blockers_payload),
            )
            _insert_event(
                conn,
                DEFAULT_CONFIG_CONTRACT_ID,
                "REAL_CONFIG_REQUIREMENTS_CREATED",
                requirement_counts,
            )
            _insert_event(
                conn,
                DEFAULT_CONFIG_CONTRACT_ID,
                "REAL_CONFIG_BLOCKERS_CARRIED_FORWARD",
                blocker_counts,
            )
            _insert_event(
                conn,
                DEFAULT_CONFIG_CONTRACT_ID,
                "CONFIG_CONTRACT_LOCKS_CONFIRMED",
                {
                    "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    "provider_approval_blocked": True,
                    "provider_activation_blocked": True,
                    "provider_selection_blocked": True,
                    "provider_configuration_blocked": True,
                    "provider_read_write_blocked": True,
                    "credential_configuration_blocked": True,
                    "endpoint_configuration_blocked": True,
                    "container_configuration_blocked": True,
                    "encryption_configuration_blocked": True,
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
        "config_contract_id": DEFAULT_CONFIG_CONTRACT_ID,
        "contract_count": counts["contract_count"],
        "requirement_count": counts["requirement_count"],
        "blocker_count": counts["blocker_count"],
        "event_count": counts["event_count"],
        "real_sqlite_backed": True,
    }


def _unique_provider_candidates(blockers: list[Dict[str, Any]]) -> list[Dict[str, str]]:
    seen = {}
    for blocker in blockers:
        candidate_id = blocker["provider_candidate_id"]
        if candidate_id not in seen:
            seen[candidate_id] = {"provider_candidate_id": candidate_id}
    return [seen[key] for key in sorted(seen.keys())]


def _insert_config_requirement(
    conn: sqlite3.Connection,
    config_contract_id: str,
    candidate: Dict[str, str],
    requirement: Dict[str, str],
    now: str,
) -> str:
    config_requirement_id = (
        f"VSPCFGREQ-{candidate['provider_candidate_id'].split('-', 1)[-1]}-"
        f"{requirement['requirement_code'].upper().replace('_', '-')}"
    )

    conn.execute(
        """
        INSERT INTO vault_storage_provider_config_requirements (
            config_requirement_id,
            config_contract_id,
            provider_candidate_id,
            requirement_code,
            requirement_name,
            requirement_category,
            requirement_message,
            requirement_status,
            required_for_configuration,
            config_value_present,
            secret_value_present,
            config_verified,
            tower_review_required,
            tower_review_granted,
            provider_configured,
            provider_read_enabled,
            provider_write_enabled,
            export_enabled,
            execution_enabled,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            config_requirement_id,
            config_contract_id,
            candidate["provider_candidate_id"],
            requirement["requirement_code"],
            requirement["requirement_name"],
            requirement["requirement_category"],
            requirement["requirement_message"],
            "REAL_CONFIG_REQUIREMENT_RECORDED_NOT_CONFIGURED_TOWER_LOCKED",
            1,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            now,
            now,
        ),
    )
    return config_requirement_id


def _insert_config_blocker(
    conn: sqlite3.Connection,
    config_contract_id: str,
    blocker: Dict[str, Any],
    now: str,
) -> str:
    config_blocker_id = f"VSPCFGB-{blocker['blocker_id'].replace('VSPPB-', '')}"
    conn.execute(
        """
        INSERT INTO vault_storage_provider_config_blockers (
            config_blocker_id,
            config_contract_id,
            source_readiness_blocker_id,
            source_receipt_line_id,
            source_finding_id,
            provider_candidate_id,
            blocker_category,
            blocker_code,
            blocker_name,
            severity,
            blocker_status,
            blocks_provider_approval,
            blocks_provider_activation,
            blocks_provider_selection,
            blocks_provider_configuration,
            blocks_provider_read_write,
            blocks_object_body_view,
            blocks_export,
            blocks_execution,
            tower_review_required,
            tower_review_granted,
            risk_accepted,
            risk_waived,
            mitigation_approved,
            resolved,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            config_blocker_id,
            config_contract_id,
            blocker["blocker_id"],
            blocker["source_receipt_line_id"],
            blocker["source_finding_id"],
            blocker["provider_candidate_id"],
            blocker["blocker_category"],
            blocker["blocker_code"],
            blocker["blocker_name"],
            blocker["severity"],
            "REAL_CONFIG_CONTRACT_BLOCKER_ACTIVE_CARRIED_FROM_GP060",
            1 if blocker["blocks_provider_approval"] else 0,
            1 if blocker["blocks_provider_activation"] else 0,
            1 if blocker["blocks_provider_selection"] else 0,
            1 if blocker["blocks_provider_configuration"] else 0,
            1 if blocker["blocks_provider_read_write"] else 0,
            1 if blocker["blocks_object_body_view"] else 0,
            1 if blocker["blocks_export"] else 0,
            1 if blocker["blocks_execution"] else 0,
            1 if blocker["tower_review_required"] else 0,
            1 if blocker["tower_review_granted"] else 0,
            1 if blocker["risk_accepted"] else 0,
            1 if blocker["risk_waived"] else 0,
            1 if blocker["mitigation_approved"] else 0,
            1 if blocker["resolved"] else 0,
            now,
            now,
        ),
    )
    return config_blocker_id


def _insert_event(
    conn: sqlite3.Connection,
    config_contract_id: str,
    event_type: str,
    event_payload: Dict[str, Any],
) -> str:
    event_id = f"VSPCFGE-{uuid.uuid4().hex[:16].upper()}"
    conn.execute(
        """
        INSERT INTO vault_storage_provider_config_events (
            event_id,
            config_contract_id,
            event_type,
            event_payload_json,
            created_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            event_id,
            config_contract_id,
            event_type,
            _json_dumps(event_payload),
            _now_iso(),
        ),
    )
    return event_id


def _get_counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        contract_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_config_contracts"
        ).fetchone()["c"]
        requirement_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_config_requirements"
        ).fetchone()["c"]
        blocker_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_config_blockers"
        ).fetchone()["c"]
        event_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_config_events"
        ).fetchone()["c"]

    return {
        "contract_count": int(contract_count),
        "requirement_count": int(requirement_count),
        "blocker_count": int(blocker_count),
        "event_count": int(event_count),
    }


def _get_requirement_counts(conn: sqlite3.Connection, config_contract_id: str) -> Dict[str, int]:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS requirement_count,
            COUNT(DISTINCT provider_candidate_id) AS provider_candidate_count,
            COUNT(DISTINCT requirement_code) AS requirement_code_count,
            SUM(CASE WHEN required_for_configuration = 1 THEN 1 ELSE 0 END) AS required_for_configuration_count,
            SUM(CASE WHEN config_value_present = 1 THEN 1 ELSE 0 END) AS config_value_present_count,
            SUM(CASE WHEN secret_value_present = 1 THEN 1 ELSE 0 END) AS secret_value_present_count,
            SUM(CASE WHEN config_verified = 1 THEN 1 ELSE 0 END) AS config_verified_count,
            SUM(CASE WHEN tower_review_required = 1 THEN 1 ELSE 0 END) AS tower_review_required_count,
            SUM(CASE WHEN tower_review_granted = 1 THEN 1 ELSE 0 END) AS tower_review_granted_count,
            SUM(CASE WHEN provider_configured = 1 THEN 1 ELSE 0 END) AS provider_configured_count,
            SUM(CASE WHEN provider_read_enabled = 1 THEN 1 ELSE 0 END) AS provider_read_enabled_count,
            SUM(CASE WHEN provider_write_enabled = 1 THEN 1 ELSE 0 END) AS provider_write_enabled_count,
            SUM(CASE WHEN export_enabled = 1 THEN 1 ELSE 0 END) AS export_enabled_count,
            SUM(CASE WHEN execution_enabled = 1 THEN 1 ELSE 0 END) AS execution_enabled_count
        FROM vault_storage_provider_config_requirements
        WHERE config_contract_id = ?
        """,
        (config_contract_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _get_blocker_counts(conn: sqlite3.Connection, config_contract_id: str) -> Dict[str, int]:
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
        FROM vault_storage_provider_config_blockers
        WHERE config_contract_id = ?
        """,
        (config_contract_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _compact_readiness_source_snapshot(
    readiness: Dict[str, Any],
    blockers_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "source_readiness_checkpoint_id": readiness["checkpoint_id"],
        "source_readiness_pack_id": readiness["pack_id"],
        "source_checkpoint_status": readiness["checkpoint_status"],
        "source_section": readiness["section_id"],
        "source_section_range": readiness["section_range"],
        "source_review_receipt_id": readiness["source_review_receipt_id"],
        "prep_layer_complete": readiness["prep_layer_complete"],
        "safe_to_continue_to_gp061": readiness["safe_to_continue_to_gp061"],
        "readiness_score": readiness["readiness_score"],
        "blocker_count": blockers_payload["blocker_count"],
        "capability_blocker_count": blockers_payload["capability_blocker_count"],
        "criteria_blocker_count": blockers_payload["criteria_blocker_count"],
        "risk_blocker_count": blockers_payload["risk_blocker_count"],
        "blocks_provider_approval_count": blockers_payload["blocks_provider_approval_count"],
        "blocks_provider_activation_count": blockers_payload["blocks_provider_activation_count"],
        "blocks_provider_selection_count": blockers_payload["blocks_provider_selection_count"],
        "blocks_provider_configuration_count": blockers_payload["blocks_provider_configuration_count"],
        "blocks_provider_read_write_count": blockers_payload["blocks_provider_read_write_count"],
        "blocks_export_count": blockers_payload["blocks_export_count"],
        "blocks_execution_count": blockers_payload["blocks_execution_count"],
        "provider_approval_ready": readiness["provider_approval_ready"],
        "provider_activation_ready": readiness["provider_activation_ready"],
        "provider_configuration_ready": readiness["provider_configuration_ready"],
        "provider_read_write_ready": readiness["provider_read_write_ready"],
        "provider_approved": readiness["provider_approved"],
        "provider_activated": readiness["provider_activated"],
        "provider_selected": readiness["provider_selected"],
        "provider_configured": readiness["provider_configured"],
        "export_enabled": readiness["export_enabled"],
        "execution_enabled": readiness["execution_enabled"],
        "vault_done": readiness["vault_done"],
    }


def _build_contract_data(
    readiness: Dict[str, Any],
    blockers_payload: Dict[str, Any],
    candidates: list[Dict[str, str]],
) -> Dict[str, Any]:
    return {
        "config_contract_schema_version": SCHEMA_VERSION,
        "contract_type": "REAL_STORAGE_PROVIDER_CONFIG_CONTRACT",
        "contract_status": "REAL_STORAGE_PROVIDER_CONFIG_CONTRACT_OPEN_TOWER_LOCKED",
        "real_durable_config_contract": True,
        "metadata_source": "VAULT_GP060_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT",
        "source_readiness_checkpoint_id": readiness["checkpoint_id"],
        "source_readiness_pack_id": readiness["pack_id"],
        "previous_section": {
            "section_id": PREVIOUS_SECTION_ID,
            "section_range": PREVIOUS_SECTION_RANGE,
            "closed": True,
        },
        "current_section": {
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "started": True,
        },
        "provider_candidate_count": len(candidates),
        "config_requirement_code_count": len(CONFIG_REQUIREMENTS),
        "config_requirement_count": len(candidates) * len(CONFIG_REQUIREMENTS),
        "carried_blocker_count": blockers_payload["blocker_count"],
        "config_requirements": CONFIG_REQUIREMENTS,
        "config_truth": {
            "config_contract_ready": True,
            "provider_approval_ready": False,
            "provider_activation_ready": False,
            "provider_configuration_ready": False,
            "provider_read_write_ready": False,
            "provider_approved": False,
            "provider_activated": False,
            "provider_recommended": False,
            "provider_selected": False,
            "provider_configured": False,
            "credentials_configured": False,
            "provider_endpoint_configured": False,
            "storage_container_configured": False,
            "encryption_configured": False,
            "provider_read_enabled": False,
            "provider_write_enabled": False,
            "provider_object_read_claimed": False,
            "provider_connection_tested": False,
            "risk_accepted": False,
            "risk_waived": False,
            "mitigation_approved": False,
            "official_storage_receipt": False,
            "finalized_storage_receipt": False,
            "closed_storage_receipt": False,
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
            "tower_review_required_count": blockers_payload["tower_review_required_count"],
            "tower_review_granted_count": blockers_payload["tower_review_granted_count"],
            "resolved_count": blockers_payload["resolved_count"],
        },
        "next_pack": NEXT_PACK,
        "next_pack_title": NEXT_PACK_TITLE,
        "safe_to_continue_to_gp062": True,
    }


def _row_to_contract(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "config_contract_id": row["config_contract_id"],
        "pack_id": row["pack_id"],
        "section_id": row["section_id"],
        "section_range": row["section_range"],
        "source_readiness_checkpoint_id": row["source_readiness_checkpoint_id"],
        "source_readiness_pack_id": row["source_readiness_pack_id"],
        "contract_status": row["contract_status"],
        "tower_authority_status": row["tower_authority_status"],
        "contract_data": _json_loads(row["contract_data_json"]),
        "config_contract_ready": bool(row["config_contract_ready"]),
        "provider_approval_ready": bool(row["provider_approval_ready"]),
        "provider_activation_ready": bool(row["provider_activation_ready"]),
        "provider_configuration_ready": bool(row["provider_configuration_ready"]),
        "provider_read_write_ready": bool(row["provider_read_write_ready"]),
        "provider_approved": bool(row["provider_approved"]),
        "provider_activated": bool(row["provider_activated"]),
        "provider_recommended": bool(row["provider_recommended"]),
        "provider_selected": bool(row["provider_selected"]),
        "provider_configured": bool(row["provider_configured"]),
        "credentials_configured": bool(row["credentials_configured"]),
        "provider_endpoint_configured": bool(row["provider_endpoint_configured"]),
        "storage_container_configured": bool(row["storage_container_configured"]),
        "encryption_configured": bool(row["encryption_configured"]),
        "provider_read_enabled": bool(row["provider_read_enabled"]),
        "provider_write_enabled": bool(row["provider_write_enabled"]),
        "provider_object_read_claimed": bool(row["provider_object_read_claimed"]),
        "provider_connection_tested": bool(row["provider_connection_tested"]),
        "risk_accepted": bool(row["risk_accepted"]),
        "risk_waived": bool(row["risk_waived"]),
        "mitigation_approved": bool(row["mitigation_approved"]),
        "official_storage_receipt": bool(row["official_storage_receipt"]),
        "finalized_storage_receipt": bool(row["finalized_storage_receipt"]),
        "closed_storage_receipt": bool(row["closed_storage_receipt"]),
        "object_body_view_enabled": bool(row["object_body_view_enabled"]),
        "direct_upload_enabled": bool(row["direct_upload_enabled"]),
        "export_enabled": bool(row["export_enabled"]),
        "execution_enabled": bool(row["execution_enabled"]),
        "vault_done": bool(row["vault_done"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_requirement(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "config_requirement_id": row["config_requirement_id"],
        "config_contract_id": row["config_contract_id"],
        "provider_candidate_id": row["provider_candidate_id"],
        "requirement_code": row["requirement_code"],
        "requirement_name": row["requirement_name"],
        "requirement_category": row["requirement_category"],
        "requirement_message": row["requirement_message"],
        "requirement_status": row["requirement_status"],
        "required_for_configuration": bool(row["required_for_configuration"]),
        "config_value_present": bool(row["config_value_present"]),
        "secret_value_present": bool(row["secret_value_present"]),
        "config_verified": bool(row["config_verified"]),
        "tower_review_required": bool(row["tower_review_required"]),
        "tower_review_granted": bool(row["tower_review_granted"]),
        "provider_configured": bool(row["provider_configured"]),
        "provider_read_enabled": bool(row["provider_read_enabled"]),
        "provider_write_enabled": bool(row["provider_write_enabled"]),
        "export_enabled": bool(row["export_enabled"]),
        "execution_enabled": bool(row["execution_enabled"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_blocker(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "config_blocker_id": row["config_blocker_id"],
        "config_contract_id": row["config_contract_id"],
        "source_readiness_blocker_id": row["source_readiness_blocker_id"],
        "source_receipt_line_id": row["source_receipt_line_id"],
        "source_finding_id": row["source_finding_id"],
        "provider_candidate_id": row["provider_candidate_id"],
        "blocker_category": row["blocker_category"],
        "blocker_code": row["blocker_code"],
        "blocker_name": row["blocker_name"],
        "severity": row["severity"],
        "blocker_status": row["blocker_status"],
        "blocks_provider_approval": bool(row["blocks_provider_approval"]),
        "blocks_provider_activation": bool(row["blocks_provider_activation"]),
        "blocks_provider_selection": bool(row["blocks_provider_selection"]),
        "blocks_provider_configuration": bool(row["blocks_provider_configuration"]),
        "blocks_provider_read_write": bool(row["blocks_provider_read_write"]),
        "blocks_object_body_view": bool(row["blocks_object_body_view"]),
        "blocks_export": bool(row["blocks_export"]),
        "blocks_execution": bool(row["blocks_execution"]),
        "tower_review_required": bool(row["tower_review_required"]),
        "tower_review_granted": bool(row["tower_review_granted"]),
        "risk_accepted": bool(row["risk_accepted"]),
        "risk_waived": bool(row["risk_waived"]),
        "mitigation_approved": bool(row["mitigation_approved"]),
        "resolved": bool(row["resolved"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_event(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "event_id": row["event_id"],
        "config_contract_id": row["config_contract_id"],
        "event_type": row["event_type"],
        "event_payload": _json_loads(row["event_payload_json"]),
        "created_at": row["created_at"],
    }


def get_storage_provider_config_contract_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_config_contract(db_path)

    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_config_contracts
            WHERE config_contract_id = ?
            """,
            (DEFAULT_CONFIG_CONTRACT_ID,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Real storage provider config contract was not initialized.")

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "contract": _row_to_contract(row),
    }


def get_storage_provider_config_requirements(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_config_contract(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_config_requirements
            WHERE config_contract_id = ?
            ORDER BY provider_candidate_id ASC, requirement_category ASC, requirement_code ASC
            """,
            (DEFAULT_CONFIG_CONTRACT_ID,),
        ).fetchall()
        counts = _get_requirement_counts(conn, DEFAULT_CONFIG_CONTRACT_ID)

    requirements = [_row_to_requirement(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "requirements": requirements,
    }


def get_storage_provider_config_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_config_contract(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_config_blockers
            WHERE config_contract_id = ?
            ORDER BY provider_candidate_id ASC, blocker_category ASC, blocker_code ASC
            """,
            (DEFAULT_CONFIG_CONTRACT_ID,),
        ).fetchall()
        counts = _get_blocker_counts(conn, DEFAULT_CONFIG_CONTRACT_ID)

    blockers = [_row_to_blocker(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "blockers": blockers,
    }


def get_storage_provider_config_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_config_contract(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_config_events
            WHERE config_contract_id = ?
            ORDER BY created_at ASC, event_id ASC
            """,
            (DEFAULT_CONFIG_CONTRACT_ID,),
        ).fetchall()

    events = [_row_to_event(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "event_count": len(events),
        "events": events,
    }


def record_storage_provider_config_event(
    event_type: str,
    event_payload: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    initialize_real_storage_provider_config_contract(db_path)
    payload = dict(event_payload or {})
    payload.update(
        {
            "write_type": "REAL_STORAGE_PROVIDER_CONFIG_CONTRACT_EVENT",
            "config_contract_ready": True,
            "provider_configuration_ready": False,
            "provider_approval_ready": False,
            "provider_activation_ready": False,
            "provider_read_write_ready": False,
            "provider_approved": False,
            "provider_activated": False,
            "provider_selected": False,
            "provider_recommended": False,
            "provider_configured": False,
            "credentials_configured": False,
            "provider_endpoint_configured": False,
            "storage_container_configured": False,
            "encryption_configured": False,
            "provider_read_enabled": False,
            "provider_write_enabled": False,
            "risk_accepted": False,
            "risk_waived": False,
            "mitigation_approved": False,
            "export_enabled": False,
            "execution_enabled": False,
            "vault_done": False,
        }
    )

    with _connect(db_path) as conn:
        event_id = _insert_event(
            conn,
            DEFAULT_CONFIG_CONTRACT_ID,
            event_type,
            payload,
        )
        conn.commit()

    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "config_contract_id": DEFAULT_CONFIG_CONTRACT_ID,
        "real_sqlite_backed": True,
        "config_contract_ready": True,
        "provider_configuration_ready": False,
        "provider_approval_ready": False,
        "provider_activation_ready": False,
        "provider_read_write_ready": False,
        "provider_approved": False,
        "provider_activated": False,
        "provider_selected": False,
        "provider_recommended": False,
        "provider_configured": False,
        "credentials_configured": False,
        "provider_endpoint_configured": False,
        "storage_container_configured": False,
        "encryption_configured": False,
        "provider_read_enabled": False,
        "provider_write_enabled": False,
        "risk_accepted": False,
        "risk_waived": False,
        "mitigation_approved": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    }


def validate_storage_provider_config_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    contract = get_storage_provider_config_contract_record(db_path)["contract"]
    requirements = get_storage_provider_config_requirements(db_path)
    blockers = get_storage_provider_config_blockers(db_path)
    events = get_storage_provider_config_events(db_path)

    expected_requirement_count = 5 * len(CONFIG_REQUIREMENTS)
    expected_blocker_count = 140

    checks = [
        {
            "code": "REAL_SQLITE_CONFIG_CONTRACT_EXISTS",
            "passed": contract["config_contract_id"] == DEFAULT_CONFIG_CONTRACT_ID,
        },
        {
            "code": "SOURCE_GP060_READINESS_CHECKPOINT_ATTACHED",
            "passed": contract["source_readiness_checkpoint_id"] == DEFAULT_READINESS_CHECKPOINT_ID,
        },
        {
            "code": "CONFIG_CONTRACT_READY",
            "passed": contract["config_contract_ready"] is True,
        },
        {
            "code": "NEW_CONFIG_SECTION_STARTED",
            "passed": contract["section_id"] == SECTION_ID and contract["section_range"] == SECTION_RANGE,
        },
        {
            "code": "REAL_CONFIG_REQUIREMENT_ROWS_EXIST",
            "passed": requirements["requirement_count"] == expected_requirement_count,
        },
        {
            "code": "ALL_CONFIG_REQUIREMENTS_REQUIRED",
            "passed": requirements["required_for_configuration_count"] == expected_requirement_count,
        },
        {
            "code": "NO_CONFIG_VALUES_PRESENT",
            "passed": requirements["config_value_present_count"] == 0,
        },
        {
            "code": "NO_SECRET_VALUES_PRESENT",
            "passed": requirements["secret_value_present_count"] == 0,
        },
        {
            "code": "NO_CONFIG_REQUIREMENTS_VERIFIED",
            "passed": requirements["config_verified_count"] == 0,
        },
        {
            "code": "NO_REQUIREMENTS_TOWER_GRANTED",
            "passed": requirements["tower_review_granted_count"] == 0,
        },
        {
            "code": "NO_REQUIREMENTS_PROVIDER_CONFIGURED",
            "passed": requirements["provider_configured_count"] == 0,
        },
        {
            "code": "NO_REQUIREMENTS_READ_ENABLED",
            "passed": requirements["provider_read_enabled_count"] == 0,
        },
        {
            "code": "NO_REQUIREMENTS_WRITE_ENABLED",
            "passed": requirements["provider_write_enabled_count"] == 0,
        },
        {
            "code": "REAL_CONFIG_BLOCKERS_CARRIED_FORWARD",
            "passed": blockers["blocker_count"] == expected_blocker_count,
        },
        {
            "code": "CONFIG_BLOCKERS_HAVE_CAPABILITY_ROWS",
            "passed": blockers["capability_blocker_count"] == 60,
        },
        {
            "code": "CONFIG_BLOCKERS_HAVE_CRITERIA_ROWS",
            "passed": blockers["criteria_blocker_count"] == 40,
        },
        {
            "code": "CONFIG_BLOCKERS_HAVE_RISK_ROWS",
            "passed": blockers["risk_blocker_count"] == 40,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_PROVIDER_APPROVAL",
            "passed": blockers["blocks_provider_approval_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_PROVIDER_ACTIVATION",
            "passed": blockers["blocks_provider_activation_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_PROVIDER_SELECTION",
            "passed": blockers["blocks_provider_selection_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_PROVIDER_CONFIGURATION",
            "passed": blockers["blocks_provider_configuration_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_PROVIDER_READ_WRITE",
            "passed": blockers["blocks_provider_read_write_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_OBJECT_BODY_VIEW",
            "passed": blockers["blocks_object_body_view_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_EXPORT",
            "passed": blockers["blocks_export_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_EXECUTION",
            "passed": blockers["blocks_execution_count"] == expected_blocker_count,
        },
        {
            "code": "NO_BLOCKERS_TOWER_REVIEW_GRANTED",
            "passed": blockers["tower_review_granted_count"] == 0,
        },
        {
            "code": "NO_BLOCKERS_RESOLVED",
            "passed": blockers["resolved_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_APPROVAL_READY",
            "passed": contract["provider_approval_ready"] is False,
        },
        {
            "code": "NO_PROVIDER_ACTIVATION_READY",
            "passed": contract["provider_activation_ready"] is False,
        },
        {
            "code": "NO_PROVIDER_CONFIGURATION_READY",
            "passed": contract["provider_configuration_ready"] is False,
        },
        {
            "code": "NO_PROVIDER_READ_WRITE_READY",
            "passed": contract["provider_read_write_ready"] is False,
        },
        {
            "code": "NO_PROVIDER_APPROVED",
            "passed": contract["provider_approved"] is False,
        },
        {
            "code": "NO_PROVIDER_ACTIVATED",
            "passed": contract["provider_activated"] is False,
        },
        {
            "code": "NO_PROVIDER_RECOMMENDED",
            "passed": contract["provider_recommended"] is False,
        },
        {
            "code": "NO_PROVIDER_SELECTED",
            "passed": contract["provider_selected"] is False,
        },
        {
            "code": "NO_PROVIDER_CONFIGURED",
            "passed": contract["provider_configured"] is False,
        },
        {
            "code": "NO_CREDENTIALS_CONFIGURED",
            "passed": contract["credentials_configured"] is False,
        },
        {
            "code": "NO_ENDPOINT_CONFIGURED",
            "passed": contract["provider_endpoint_configured"] is False,
        },
        {
            "code": "NO_STORAGE_CONTAINER_CONFIGURED",
            "passed": contract["storage_container_configured"] is False,
        },
        {
            "code": "NO_ENCRYPTION_CONFIGURED",
            "passed": contract["encryption_configured"] is False,
        },
        {
            "code": "NO_PROVIDER_READ_ENABLED",
            "passed": contract["provider_read_enabled"] is False,
        },
        {
            "code": "NO_PROVIDER_WRITE_ENABLED",
            "passed": contract["provider_write_enabled"] is False,
        },
        {
            "code": "NO_PROVIDER_OBJECT_READ_CLAIMED",
            "passed": contract["provider_object_read_claimed"] is False,
        },
        {
            "code": "NO_PROVIDER_CONNECTION_TESTED",
            "passed": contract["provider_connection_tested"] is False,
        },
        {
            "code": "NO_RISK_ACCEPTED",
            "passed": contract["risk_accepted"] is False and blockers["risk_accepted_count"] == 0,
        },
        {
            "code": "NO_RISK_WAIVED",
            "passed": contract["risk_waived"] is False and blockers["risk_waived_count"] == 0,
        },
        {
            "code": "NO_MITIGATION_APPROVED",
            "passed": contract["mitigation_approved"] is False and blockers["mitigation_approved_count"] == 0,
        },
        {
            "code": "NO_OFFICIAL_STORAGE_RECEIPT",
            "passed": contract["official_storage_receipt"] is False,
        },
        {
            "code": "NO_FINALIZED_STORAGE_RECEIPT",
            "passed": contract["finalized_storage_receipt"] is False,
        },
        {
            "code": "NO_CLOSED_STORAGE_RECEIPT",
            "passed": contract["closed_storage_receipt"] is False,
        },
        {
            "code": "NO_OBJECT_BODY_VIEW",
            "passed": contract["object_body_view_enabled"] is False,
        },
        {
            "code": "NO_DIRECT_UPLOAD",
            "passed": contract["direct_upload_enabled"] is False,
        },
        {
            "code": "NO_EXPORT",
            "passed": contract["export_enabled"] is False,
        },
        {
            "code": "NO_EXECUTION",
            "passed": contract["execution_enabled"] is False,
        },
        {
            "code": "VAULT_NOT_DONE",
            "passed": contract["vault_done"] is False,
        },
        {
            "code": "EVENT_LOG_EXISTS",
            "passed": events["event_count"] >= 5,
        },
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
        "safe_to_continue_to_gp062": len(failed) == 0,
    }


def get_storage_provider_config_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp062": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "Continue under ARCHIVE VAULT — REAL STORAGE PROVIDER CONFIGURATION LAYER / GP061-GP070. GP062 should build the real credential boundary without storing secrets in code, repo, logs, or notebooks.",
            "carry_forward_rules": [
                "Keep the real SQLite storage provider config contract.",
                "Keep real config requirement rows.",
                "Keep real blockers carried from GP060.",
                "Build GP062 Real Storage Provider Credential Boundary next.",
                "Do not store provider secrets in repo, files, notebooks, logs, or JSON responses.",
                "Do not configure credentials yet.",
                "Do not configure provider endpoint yet.",
                "Do not configure storage container yet.",
                "Do not configure encryption yet.",
                "Do not approve a provider yet.",
                "Do not activate a provider yet.",
                "Do not recommend or select a provider yet.",
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


def get_real_storage_provider_config_contract_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_config_contract(db_path)
    contract = get_storage_provider_config_contract_record(db_path)["contract"]
    requirements = get_storage_provider_config_requirements(db_path)
    blockers = get_storage_provider_config_blockers(db_path)
    events = get_storage_provider_config_events(db_path)
    validation = validate_storage_provider_config_contract(db_path)

    return {
        "pack": _pack_payload(),
        "config_truth": _config_truth(contract, requirements, blockers, events["event_count"], validation),
        "store": init,
        "contract": contract,
        "requirements": requirements,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_config_next_step()["next_step"],
    }


def get_gp061_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_config_contract_home(db_path)
    contract = home["contract"]
    requirements = home["requirements"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp061_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_config_contract_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_contract_count": home["store"]["contract_count"],
            "real_requirement_count": home["store"]["requirement_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp060_readiness_checkpoint_attached": True,
            "config_contract_ready": contract["config_contract_ready"],
            "provider_candidate_count": requirements["provider_candidate_count"],
            "requirement_code_count": requirements["requirement_code_count"],
            "config_value_present_count": requirements["config_value_present_count"],
            "secret_value_present_count": requirements["secret_value_present_count"],
            "config_verified_count": requirements["config_verified_count"],
            "capability_blocker_count": blockers["capability_blocker_count"],
            "criteria_blocker_count": blockers["criteria_blocker_count"],
            "risk_blocker_count": blockers["risk_blocker_count"],
            "blocks_provider_approval_count": blockers["blocks_provider_approval_count"],
            "blocks_provider_activation_count": blockers["blocks_provider_activation_count"],
            "blocks_provider_selection_count": blockers["blocks_provider_selection_count"],
            "blocks_provider_configuration_count": blockers["blocks_provider_configuration_count"],
            "blocks_provider_read_write_count": blockers["blocks_provider_read_write_count"],
            "blocks_object_body_view_count": blockers["blocks_object_body_view_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "tower_review_granted_count": blockers["tower_review_granted_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp062": validation["safe_to_continue_to_gp062"],
            "vault_done": False,
            "foundation_status": "config_contract_ready_safe_to_continue_not_done",
            "provider_approval_ready": contract["provider_approval_ready"],
            "provider_activation_ready": contract["provider_activation_ready"],
            "provider_configuration_ready": contract["provider_configuration_ready"],
            "provider_read_write_ready": contract["provider_read_write_ready"],
            "provider_approved": contract["provider_approved"],
            "provider_activated": contract["provider_activated"],
            "provider_recommended": contract["provider_recommended"],
            "provider_selected": contract["provider_selected"],
            "provider_configured": contract["provider_configured"],
            "credentials_configured": contract["credentials_configured"],
            "provider_endpoint_configured": contract["provider_endpoint_configured"],
            "storage_container_configured": contract["storage_container_configured"],
            "encryption_configured": contract["encryption_configured"],
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
            "clouds_status": "parked_do_not_continue_from_vault_gp061",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "config_truth": home["config_truth"],
        "routes": home["routes"],
        "contract": contract,
        "requirements": requirements,
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
        "depends_on": ["VAULT_GP060"],
        "foundation_status": "config_contract_ready_safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_config_contract",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }


def _routes_payload() -> Dict[str, str]:
    return {
        "room_title": "Vault Real Storage Provider Config Contract",
        "section_header": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "route": "/vault/real-storage-provider-config-contract",
        "json_route": "/vault/real-storage-provider-config-contract.json",
        "record_route": "/vault/storage-provider-config-contract-record.json",
        "requirements_route": "/vault/storage-provider-config-requirements.json",
        "blockers_route": "/vault/storage-provider-config-blockers.json",
        "events_route": "/vault/storage-provider-config-events.json",
        "validation_route": "/vault/storage-provider-config-validation.json",
        "next_step_route": "/vault/storage-provider-config-next-step.json",
        "gp061_status_route": "/vault/gp061-status.json",
    }


def _config_truth(
    contract: Dict[str, Any],
    requirements: Dict[str, Any],
    blockers: Dict[str, Any],
    event_count: int,
    validation: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "real_storage_provider_config_contract_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "real_config_contract_exists": contract["config_contract_id"] == DEFAULT_CONFIG_CONTRACT_ID,
        "real_config_requirement_rows_exist": requirements["requirement_count"] == 5 * len(CONFIG_REQUIREMENTS),
        "real_config_blocker_rows_exist": blockers["blocker_count"] == 140,
        "real_event_log_exists": event_count >= 5,
        "source_gp060_readiness_checkpoint_attached": contract["source_readiness_checkpoint_id"] == DEFAULT_READINESS_CHECKPOINT_ID,
        "validation_passed": validation["valid"],
        "config_contract_ready": contract["config_contract_ready"],
        "provider_candidate_count": requirements["provider_candidate_count"],
        "requirement_count": requirements["requirement_count"],
        "requirement_code_count": requirements["requirement_code_count"],
        "config_value_present_count": requirements["config_value_present_count"],
        "secret_value_present_count": requirements["secret_value_present_count"],
        "config_verified_count": requirements["config_verified_count"],
        "blocker_count": blockers["blocker_count"],
        "blocks_provider_configuration_count": blockers["blocks_provider_configuration_count"],
        "blocks_provider_read_write_count": blockers["blocks_provider_read_write_count"],
        "blocks_export_count": blockers["blocks_export_count"],
        "blocks_execution_count": blockers["blocks_execution_count"],
        "provider_approval_ready": contract["provider_approval_ready"],
        "provider_activation_ready": contract["provider_activation_ready"],
        "provider_configuration_ready": contract["provider_configuration_ready"],
        "provider_read_write_ready": contract["provider_read_write_ready"],
        "provider_approved": contract["provider_approved"],
        "provider_activated": contract["provider_activated"],
        "provider_recommended": contract["provider_recommended"],
        "provider_selected": contract["provider_selected"],
        "provider_configured": contract["provider_configured"],
        "credentials_configured": contract["credentials_configured"],
        "provider_endpoint_configured": contract["provider_endpoint_configured"],
        "storage_container_configured": contract["storage_container_configured"],
        "encryption_configured": contract["encryption_configured"],
        "provider_read_enabled": contract["provider_read_enabled"],
        "provider_write_enabled": contract["provider_write_enabled"],
        "provider_connection_tested": contract["provider_connection_tested"],
        "object_body_view_enabled": contract["object_body_view_enabled"],
        "direct_upload_enabled": contract["direct_upload_enabled"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "vault_done": contract["vault_done"],
        "safe_to_continue_to_gp062": validation["safe_to_continue_to_gp062"],
    }


def render_real_storage_provider_config_contract_page() -> str:
    home = get_real_storage_provider_config_contract_home()
    truth = home["config_truth"]
    requirements = home["requirements"]["requirements"]
    blockers = home["blockers"]["blockers"]
    routes = home["routes"]
    next_step = home["next_step"]

    requirement_cards = "\n".join(_render_requirement_card(item) for item in requirements[:12])
    blocker_cards = "\n".join(_render_blocker_card(item) for item in blockers[:12])
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
    rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Real Storage Provider Config Contract · GP061</title>
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
      <div class="eyebrow">Archive Vault · Giant Pack 061</div>
      <div class="eyebrow">Real Storage Provider Configuration Layer · GP061-GP070</div>
      <h1>Real Storage Provider Config Contract</h1>
      <p>
        GP061 starts the real configuration layer with a durable config contract,
        real config requirement rows, carried blockers, and event history. It does not
        configure credentials, endpoints, containers, encryption, provider access, export, or execution.
      </p>
      <div class="metrics">
        <div class="metric"><strong>{home['store']['contract_count']}</strong><span>real config contracts</span></div>
        <div class="metric"><strong>{home['store']['requirement_count']}</strong><span>real config requirements</span></div>
        <div class="metric"><strong>{home['store']['blocker_count']}</strong><span>active blockers carried</span></div>
        <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
      </div>
      <div class="chips">
        <span class="pill ok">New section started</span>
        <span class="pill ok">Real SQLite-backed</span>
        <span class="pill ok">Config contract ready</span>
        <span class="pill danger">No credentials configured</span>
        <span class="pill danger">No provider configured</span>
        <span class="pill danger">No execution</span>
      </div>
    </section>

    <section class="section">
      <h2>Config Requirements</h2>
      <p>These are real configuration contract rows. They do not contain secrets or live provider configuration.</p>
      <div class="grid">{requirement_cards}</div>
    </section>

    <section class="section">
      <h2>Carried Forward Blockers</h2>
      <p>These are real blocker rows carried from GP060 to preserve all safety locks.</p>
      <div class="grid">{blocker_cards}</div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Validation Checks</h2>
        <p>GP061 validates the real config contract and confirms configuration is still locked.</p>
        {checks}
      </div>
      <div>
        <h2>Carry Forward to GP062</h2>
        <p>{escape(next_step['owner_notebook_note'])}</p>
        <ul>{rules}</ul>
      </div>
    </section>

    <section class="section">
      <h2>GP061 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['record_route'])}</code>
        <code>{escape(routes['requirements_route'])}</code>
        <code>{escape(routes['blockers_route'])}</code>
        <code>{escape(routes['events_route'])}</code>
        <code>{escape(routes['validation_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp061_status_route'])}</code>
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
          Config present: <code>{str(item['config_value_present']).lower()}</code><br>
          Secret present: <code>{str(item['secret_value_present']).lower()}</code>
        </div>
      </article>
    """


def _render_blocker_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="title">{escape(item['blocker_name'])}</div>
        <div class="meta">
          Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
          Category: <code>{escape(item['blocker_category'])}</code><br>
          Source: <code>{escape(item['source_readiness_blocker_id'])}</code><br>
          Blocks config: <code>{str(item['blocks_provider_configuration']).lower()}</code><br>
          Blocks execution: <code>{str(item['blocks_execution']).lower()}</code>
        </div>
      </article>
    """
