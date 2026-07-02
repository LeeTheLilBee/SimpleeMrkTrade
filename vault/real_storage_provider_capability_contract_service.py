"""
VAULT GIANT PACK 057 — Real Storage Provider Capability Contract

CURRENT SECTION:
Archive Vault — Storage Provider Prep Layer
GP051-GP060

This pack adds a real durable SQLite-backed capability contract for storage providers.

Purpose:
- Create a real provider capability contract schema.
- Persist a real contract record sourced from GP056.
- Persist real capability requirement rows for each registered provider candidate.
- Persist a real capability event log.
- Validate the contract against Tower/Vault locks.
- Provide real read/list/validate/event routes.

Important truth:
- GP057 creates real capability contract rows.
- GP057 links to the real GP056 selection registry.
- GP057 does not activate a provider.
- GP057 does not recommend or select a provider.
- GP057 does not configure a provider.
- GP057 does not enable provider read/write.
- GP057 does not accept/waive risk or approve mitigation.
- GP057 does not unlock object bodies, raw storage, upload, export, or execution.
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

from vault.real_storage_provider_selection_registry_service import (
    DEFAULT_SELECTION_REGISTRY_ID,
    get_storage_provider_selection_candidates,
    get_storage_provider_selection_registry_record,
)


PACK_ID = "VAULT_GP057"
PACK_NAME = "Real Storage Provider Capability Contract"
SCHEMA_VERSION = "vault.real_storage_provider_capability_contract.v1"

SECTION_ID = "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
SECTION_TITLE = "Archive Vault — Storage Provider Prep Layer"
SECTION_RANGE = "GP051-GP060"

NEXT_PACK = "VAULT_GP058_REAL_PROVIDER_RISK_CRITERIA_VALIDATION_ENGINE"
NEXT_PACK_TITLE = "Real Provider Risk / Criteria Validation Engine"

DEFAULT_CAPABILITY_CONTRACT_ID = "VSPCC-GP057-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_CAPABILITY_CONTRACT_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_capability_contract.sqlite"

CAPABILITY_REQUIREMENTS = [
    {
        "capability_code": "metadata_record_persistence",
        "capability_name": "Metadata record persistence",
        "required_for_beta": True,
        "contract_reason": "Vault needs durable metadata before object bodies or external storage are unlocked.",
    },
    {
        "capability_code": "durable_object_write",
        "capability_name": "Durable object write",
        "required_for_beta": True,
        "contract_reason": "Provider must support durable write behavior before any storage activation.",
    },
    {
        "capability_code": "durable_object_read",
        "capability_name": "Durable object read",
        "required_for_beta": True,
        "contract_reason": "Provider must support controlled read behavior before any object view can exist.",
    },
    {
        "capability_code": "checksum_hash_integrity",
        "capability_name": "Checksum / hash integrity",
        "required_for_beta": True,
        "contract_reason": "Vault needs integrity proof for stored objects.",
    },
    {
        "capability_code": "version_history_support",
        "capability_name": "Version history support",
        "required_for_beta": True,
        "contract_reason": "Vault must track replacement/version history for serious records.",
    },
    {
        "capability_code": "encryption_at_rest",
        "capability_name": "Encryption at rest",
        "required_for_beta": True,
        "contract_reason": "Sensitive documents require encrypted storage boundaries.",
    },
    {
        "capability_code": "tower_permission_gate",
        "capability_name": "Tower permission gate",
        "required_for_beta": True,
        "contract_reason": "Tower must control access, clearance, and unlocks.",
    },
    {
        "capability_code": "audit_event_stream",
        "capability_name": "Audit event stream",
        "required_for_beta": True,
        "contract_reason": "Storage actions must produce reviewable event evidence.",
    },
    {
        "capability_code": "export_lock_support",
        "capability_name": "Export lock support",
        "required_for_beta": True,
        "contract_reason": "External delivery and export must stay locked until Tower allows it.",
    },
    {
        "capability_code": "redaction_boundary_support",
        "capability_name": "Redaction boundary support",
        "required_for_beta": True,
        "contract_reason": "Vault must keep owner/private views separated from shareable views.",
    },
    {
        "capability_code": "retention_hold_support",
        "capability_name": "Retention hold support",
        "required_for_beta": True,
        "contract_reason": "Important records need preservation and deletion controls.",
    },
    {
        "capability_code": "restore_test_support",
        "capability_name": "Restore test support",
        "required_for_beta": True,
        "contract_reason": "Vault must be able to prove that archived records can be restored.",
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


def ensure_capability_contract_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_capability_contracts (
                contract_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_selection_registry_id TEXT NOT NULL,
                source_selection_pack_id TEXT NOT NULL,
                contract_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                contract_data_json TEXT NOT NULL,
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_capability_requirements (
                capability_requirement_id TEXT PRIMARY KEY,
                contract_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                candidate_type TEXT NOT NULL,
                capability_code TEXT NOT NULL,
                capability_name TEXT NOT NULL,
                contract_reason TEXT NOT NULL,
                requirement_status TEXT NOT NULL,
                required_for_beta INTEGER NOT NULL DEFAULT 1,
                candidate_claimed_supported INTEGER NOT NULL DEFAULT 0,
                contract_verified INTEGER NOT NULL DEFAULT 0,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_granted INTEGER NOT NULL DEFAULT 0,
                provider_activated INTEGER NOT NULL DEFAULT 0,
                provider_recommended INTEGER NOT NULL DEFAULT 0,
                provider_selected INTEGER NOT NULL DEFAULT 0,
                provider_configured INTEGER NOT NULL DEFAULT 0,
                provider_read_enabled INTEGER NOT NULL DEFAULT 0,
                provider_write_enabled INTEGER NOT NULL DEFAULT 0,
                object_body_view_enabled INTEGER NOT NULL DEFAULT 0,
                export_enabled INTEGER NOT NULL DEFAULT 0,
                execution_enabled INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(contract_id)
                    REFERENCES vault_storage_provider_capability_contracts(contract_id)
                    ON DELETE CASCADE,
                UNIQUE(contract_id, provider_candidate_id, capability_code)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_capability_events (
                event_id TEXT PRIMARY KEY,
                contract_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(contract_id)
                    REFERENCES vault_storage_provider_capability_contracts(contract_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_storage_provider_capability_requirements_contract
            ON vault_storage_provider_capability_requirements(contract_id, provider_candidate_id, capability_code)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_storage_provider_capability_events_contract
            ON vault_storage_provider_capability_events(contract_id, created_at)
            """
        )
        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "tables": [
            "vault_storage_provider_capability_contracts",
            "vault_storage_provider_capability_requirements",
            "vault_storage_provider_capability_events",
        ],
        "real_sqlite_backed": True,
    }


def initialize_real_storage_provider_capability_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_capability_contract_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            """
            SELECT contract_id
            FROM vault_storage_provider_capability_contracts
            WHERE contract_id = ?
            """,
            (DEFAULT_CAPABILITY_CONTRACT_ID,),
        ).fetchone()

        if existing is None:
            selection_registry = get_storage_provider_selection_registry_record()["registry"]
            candidates = get_storage_provider_selection_candidates()["candidates"]
            contract_data = _build_contract_data(selection_registry, candidates)
            now = _now_iso()

            conn.execute(
                """
                INSERT INTO vault_storage_provider_capability_contracts (
                    contract_id,
                    pack_id,
                    section_id,
                    section_range,
                    source_selection_registry_id,
                    source_selection_pack_id,
                    contract_status,
                    tower_authority_status,
                    contract_data_json,
                    provider_activated,
                    provider_recommended,
                    provider_selected,
                    provider_configured,
                    provider_read_enabled,
                    provider_write_enabled,
                    provider_object_read_claimed,
                    provider_connection_tested,
                    risk_accepted,
                    risk_waived,
                    mitigation_approved,
                    object_body_view_enabled,
                    direct_upload_enabled,
                    export_enabled,
                    execution_enabled,
                    vault_done,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    DEFAULT_CAPABILITY_CONTRACT_ID,
                    PACK_ID,
                    SECTION_ID,
                    SECTION_RANGE,
                    selection_registry["registry_id"],
                    selection_registry["pack_id"],
                    "REAL_CAPABILITY_CONTRACT_OPEN_TOWER_LOCKED",
                    "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    _json_dumps(contract_data),
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
                for requirement in CAPABILITY_REQUIREMENTS:
                    _insert_capability_requirement(
                        conn,
                        DEFAULT_CAPABILITY_CONTRACT_ID,
                        candidate,
                        requirement,
                        now,
                    )

            _insert_event(
                conn,
                DEFAULT_CAPABILITY_CONTRACT_ID,
                "REAL_CAPABILITY_CONTRACT_CREATED",
                {
                    "pack_id": PACK_ID,
                    "source_selection_registry_id": selection_registry["registry_id"],
                    "source_selection_pack_id": selection_registry["pack_id"],
                    "real_sqlite_backed": True,
                    "contract_status": "REAL_CAPABILITY_CONTRACT_OPEN_TOWER_LOCKED",
                    "provider_activated": False,
                    "provider_selected": False,
                    "provider_configured": False,
                    "provider_read_enabled": False,
                    "provider_write_enabled": False,
                },
            )
            _insert_event(
                conn,
                DEFAULT_CAPABILITY_CONTRACT_ID,
                "SOURCE_GP056_SELECTION_REGISTRY_ATTACHED",
                _compact_selection_source_snapshot(selection_registry),
            )
            _insert_event(
                conn,
                DEFAULT_CAPABILITY_CONTRACT_ID,
                "REAL_CAPABILITY_REQUIREMENTS_CREATED",
                {
                    "candidate_count": len(candidates),
                    "capability_code_count": len(CAPABILITY_REQUIREMENTS),
                    "capability_requirement_count": len(candidates) * len(CAPABILITY_REQUIREMENTS),
                    "contract_verified_count": 0,
                    "candidate_claimed_supported_count": 0,
                },
            )
            _insert_event(
                conn,
                DEFAULT_CAPABILITY_CONTRACT_ID,
                "TOWER_CAPABILITY_LOCKS_CONFIRMED",
                {
                    "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    "provider_activation_blocked": True,
                    "provider_selection_blocked": True,
                    "provider_configuration_blocked": True,
                    "provider_read_write_blocked": True,
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
        "contract_id": DEFAULT_CAPABILITY_CONTRACT_ID,
        "contract_count": counts["contract_count"],
        "capability_requirement_count": counts["capability_requirement_count"],
        "event_count": counts["event_count"],
        "real_sqlite_backed": True,
    }


def _insert_capability_requirement(
    conn: sqlite3.Connection,
    contract_id: str,
    candidate: Dict[str, Any],
    requirement: Dict[str, Any],
    now: str,
) -> str:
    capability_requirement_id = (
        f"VSPCR-{candidate['provider_candidate_id'].split('-', 1)[-1]}-"
        f"{requirement['capability_code'].upper().replace('_', '-')}"
    )

    conn.execute(
        """
        INSERT INTO vault_storage_provider_capability_requirements (
            capability_requirement_id,
            contract_id,
            provider_candidate_id,
            candidate_type,
            capability_code,
            capability_name,
            contract_reason,
            requirement_status,
            required_for_beta,
            candidate_claimed_supported,
            contract_verified,
            tower_review_required,
            tower_review_granted,
            provider_activated,
            provider_recommended,
            provider_selected,
            provider_configured,
            provider_read_enabled,
            provider_write_enabled,
            object_body_view_enabled,
            export_enabled,
            execution_enabled,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            capability_requirement_id,
            contract_id,
            candidate["provider_candidate_id"],
            candidate["candidate_type"],
            requirement["capability_code"],
            requirement["capability_name"],
            requirement["contract_reason"],
            "REQUIRED_CONTRACT_ROW_NOT_CLAIMED_NOT_VERIFIED_TOWER_LOCKED",
            1 if requirement["required_for_beta"] else 0,
            0,
            0,
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
            now,
            now,
        ),
    )

    return capability_requirement_id


def _insert_event(
    conn: sqlite3.Connection,
    contract_id: str,
    event_type: str,
    event_payload: Dict[str, Any],
) -> str:
    event_id = f"VSPCE-{uuid.uuid4().hex[:16].upper()}"
    conn.execute(
        """
        INSERT INTO vault_storage_provider_capability_events (
            event_id,
            contract_id,
            event_type,
            event_payload_json,
            created_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            event_id,
            contract_id,
            event_type,
            _json_dumps(event_payload),
            _now_iso(),
        ),
    )
    return event_id


def _get_counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        contract_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_capability_contracts"
        ).fetchone()["c"]
        capability_requirement_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_capability_requirements"
        ).fetchone()["c"]
        event_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_capability_events"
        ).fetchone()["c"]

    return {
        "contract_count": int(contract_count),
        "capability_requirement_count": int(capability_requirement_count),
        "event_count": int(event_count),
    }


def _compact_selection_source_snapshot(selection_registry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source_selection_registry_id": selection_registry["registry_id"],
        "source_selection_pack_id": selection_registry["pack_id"],
        "source_selection_status": selection_registry["registry_status"],
        "source_section": selection_registry["section_id"],
        "source_section_range": selection_registry["section_range"],
        "source_decision_record_id": selection_registry["source_decision_record_id"],
        "provider_candidate_count": selection_registry["registry_data"]["provider_candidate_count"],
        "recommended_provider_id": selection_registry["recommended_provider_id"],
        "selected_provider_id": selection_registry["selected_provider_id"],
        "provider_configured": selection_registry["provider_configured"],
        "provider_read_enabled": selection_registry["provider_read_enabled"],
        "provider_write_enabled": selection_registry["provider_write_enabled"],
        "risk_accepted": selection_registry["risk_accepted"],
        "risk_waived": selection_registry["risk_waived"],
        "mitigation_approved": selection_registry["mitigation_approved"],
        "export_enabled": selection_registry["export_enabled"],
        "execution_enabled": selection_registry["execution_enabled"],
        "vault_done": selection_registry["vault_done"],
    }


def _build_contract_data(selection_registry: Dict[str, Any], candidates: list[Dict[str, Any]]) -> Dict[str, Any]:
    candidate_summaries = []
    for candidate in candidates:
        candidate_summaries.append(
            {
                "provider_candidate_id": candidate["provider_candidate_id"],
                "candidate_type": candidate["candidate_type"],
                "candidate_entry_id": candidate["candidate_entry_id"],
                "capability_contract_state": "REAL_CAPABILITY_REQUIREMENTS_ATTACHED_NOT_VERIFIED_NOT_ACTIVATED",
                "capability_requirement_count": len(CAPABILITY_REQUIREMENTS),
                "capability_codes": [item["capability_code"] for item in CAPABILITY_REQUIREMENTS],
                "provider_activated": False,
                "provider_recommended": False,
                "provider_selected": False,
                "provider_configured": False,
                "provider_read_enabled": False,
                "provider_write_enabled": False,
                "tower_review_required": True,
                "tower_review_granted": False,
                "safe_to_continue_to_gp058": True,
            }
        )

    return {
        "contract_schema_version": SCHEMA_VERSION,
        "contract_type": "REAL_STORAGE_PROVIDER_CAPABILITY_CONTRACT",
        "contract_status": "REAL_CAPABILITY_CONTRACT_OPEN_TOWER_LOCKED",
        "real_durable_contract": True,
        "metadata_source": "VAULT_GP056_REAL_STORAGE_PROVIDER_SELECTION_REGISTRY",
        "source_selection_registry_id": selection_registry["registry_id"],
        "source_selection_pack_id": selection_registry["pack_id"],
        "provider_candidate_count": len(candidates),
        "capability_code_count": len(CAPABILITY_REQUIREMENTS),
        "capability_requirement_count": len(candidates) * len(CAPABILITY_REQUIREMENTS),
        "required_capabilities": CAPABILITY_REQUIREMENTS,
        "candidate_contract_summaries": candidate_summaries,
        "capability_summary": {
            "provider_activated": False,
            "provider_recommended": False,
            "provider_selected": False,
            "provider_configured": False,
            "provider_read_enabled": False,
            "provider_write_enabled": False,
            "candidate_claimed_supported_count": 0,
            "contract_verified_count": 0,
            "risk_accepted": False,
            "risk_waived": False,
            "mitigation_approved": False,
            "object_body_view_enabled": False,
            "direct_upload_enabled": False,
            "export_enabled": False,
            "execution_enabled": False,
            "vault_done": False,
        },
        "tower_lock_summary": {
            "tower_review_required": True,
            "tower_review_granted": False,
            "provider_activation_blocked": True,
            "provider_recommendation_blocked": True,
            "provider_selection_blocked": True,
            "provider_configuration_blocked": True,
            "provider_read_write_blocked": True,
            "object_body_view_blocked": True,
            "direct_upload_blocked": True,
            "export_blocked": True,
            "execution_blocked": True,
        },
        "next_pack": NEXT_PACK,
        "next_pack_title": NEXT_PACK_TITLE,
        "safe_to_continue_to_gp058": True,
    }


def _row_to_contract(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "contract_id": row["contract_id"],
        "pack_id": row["pack_id"],
        "section_id": row["section_id"],
        "section_range": row["section_range"],
        "source_selection_registry_id": row["source_selection_registry_id"],
        "source_selection_pack_id": row["source_selection_pack_id"],
        "contract_status": row["contract_status"],
        "tower_authority_status": row["tower_authority_status"],
        "contract_data": _json_loads(row["contract_data_json"]),
        "provider_activated": bool(row["provider_activated"]),
        "provider_recommended": bool(row["provider_recommended"]),
        "provider_selected": bool(row["provider_selected"]),
        "provider_configured": bool(row["provider_configured"]),
        "provider_read_enabled": bool(row["provider_read_enabled"]),
        "provider_write_enabled": bool(row["provider_write_enabled"]),
        "provider_object_read_claimed": bool(row["provider_object_read_claimed"]),
        "provider_connection_tested": bool(row["provider_connection_tested"]),
        "risk_accepted": bool(row["risk_accepted"]),
        "risk_waived": bool(row["risk_waived"]),
        "mitigation_approved": bool(row["mitigation_approved"]),
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
        "capability_requirement_id": row["capability_requirement_id"],
        "contract_id": row["contract_id"],
        "provider_candidate_id": row["provider_candidate_id"],
        "candidate_type": row["candidate_type"],
        "capability_code": row["capability_code"],
        "capability_name": row["capability_name"],
        "contract_reason": row["contract_reason"],
        "requirement_status": row["requirement_status"],
        "required_for_beta": bool(row["required_for_beta"]),
        "candidate_claimed_supported": bool(row["candidate_claimed_supported"]),
        "contract_verified": bool(row["contract_verified"]),
        "tower_review_required": bool(row["tower_review_required"]),
        "tower_review_granted": bool(row["tower_review_granted"]),
        "provider_activated": bool(row["provider_activated"]),
        "provider_recommended": bool(row["provider_recommended"]),
        "provider_selected": bool(row["provider_selected"]),
        "provider_configured": bool(row["provider_configured"]),
        "provider_read_enabled": bool(row["provider_read_enabled"]),
        "provider_write_enabled": bool(row["provider_write_enabled"]),
        "object_body_view_enabled": bool(row["object_body_view_enabled"]),
        "export_enabled": bool(row["export_enabled"]),
        "execution_enabled": bool(row["execution_enabled"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_event(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "event_id": row["event_id"],
        "contract_id": row["contract_id"],
        "event_type": row["event_type"],
        "event_payload": _json_loads(row["event_payload_json"]),
        "created_at": row["created_at"],
    }


def get_storage_provider_capability_contract_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_capability_contract(db_path)

    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_capability_contracts
            WHERE contract_id = ?
            """,
            (DEFAULT_CAPABILITY_CONTRACT_ID,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Real storage provider capability contract was not initialized.")

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "contract": _row_to_contract(row),
    }


def get_storage_provider_capability_requirements(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_capability_contract(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_capability_requirements
            WHERE contract_id = ?
            ORDER BY provider_candidate_id ASC, capability_code ASC
            """,
            (DEFAULT_CAPABILITY_CONTRACT_ID,),
        ).fetchall()

    requirements = [_row_to_requirement(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "capability_requirement_count": len(requirements),
        "provider_candidate_count": len({item["provider_candidate_id"] for item in requirements}),
        "capability_code_count": len({item["capability_code"] for item in requirements}),
        "required_for_beta_count": sum(1 for item in requirements if item["required_for_beta"]),
        "candidate_claimed_supported_count": sum(1 for item in requirements if item["candidate_claimed_supported"]),
        "contract_verified_count": sum(1 for item in requirements if item["contract_verified"]),
        "tower_review_required_count": sum(1 for item in requirements if item["tower_review_required"]),
        "tower_review_granted_count": sum(1 for item in requirements if item["tower_review_granted"]),
        "provider_activated_count": sum(1 for item in requirements if item["provider_activated"]),
        "provider_recommended_count": sum(1 for item in requirements if item["provider_recommended"]),
        "provider_selected_count": sum(1 for item in requirements if item["provider_selected"]),
        "provider_configured_count": sum(1 for item in requirements if item["provider_configured"]),
        "provider_read_enabled_count": sum(1 for item in requirements if item["provider_read_enabled"]),
        "provider_write_enabled_count": sum(1 for item in requirements if item["provider_write_enabled"]),
        "object_body_view_enabled_count": sum(1 for item in requirements if item["object_body_view_enabled"]),
        "export_enabled_count": sum(1 for item in requirements if item["export_enabled"]),
        "execution_enabled_count": sum(1 for item in requirements if item["execution_enabled"]),
        "requirements": requirements,
    }


def get_storage_provider_capability_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_capability_contract(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_capability_events
            WHERE contract_id = ?
            ORDER BY created_at ASC, event_id ASC
            """,
            (DEFAULT_CAPABILITY_CONTRACT_ID,),
        ).fetchall()

    events = [_row_to_event(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "event_count": len(events),
        "events": events,
    }


def record_storage_provider_capability_review_event(
    event_type: str,
    event_payload: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    initialize_real_storage_provider_capability_contract(db_path)
    payload = dict(event_payload or {})
    payload.update(
        {
            "write_type": "REAL_CAPABILITY_CONTRACT_REVIEW_EVENT",
            "provider_activated": False,
            "provider_selected": False,
            "provider_recommended": False,
            "provider_configured": False,
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
            DEFAULT_CAPABILITY_CONTRACT_ID,
            event_type,
            payload,
        )
        conn.commit()

    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "contract_id": DEFAULT_CAPABILITY_CONTRACT_ID,
        "real_sqlite_backed": True,
        "provider_activated": False,
        "provider_selected": False,
        "provider_recommended": False,
        "provider_configured": False,
        "provider_read_enabled": False,
        "provider_write_enabled": False,
        "risk_accepted": False,
        "risk_waived": False,
        "mitigation_approved": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    }


def validate_storage_provider_capability_contract(db_path: Optional[str] = None) -> Dict[str, Any]:
    contract = get_storage_provider_capability_contract_record(db_path)["contract"]
    requirements_payload = get_storage_provider_capability_requirements(db_path)
    events_payload = get_storage_provider_capability_events(db_path)

    expected_requirement_count = 5 * len(CAPABILITY_REQUIREMENTS)

    checks = [
        {
            "code": "REAL_SQLITE_CAPABILITY_CONTRACT_EXISTS",
            "passed": contract["contract_id"] == DEFAULT_CAPABILITY_CONTRACT_ID,
        },
        {
            "code": "SOURCE_GP056_SELECTION_REGISTRY_ATTACHED",
            "passed": contract["source_selection_registry_id"] == DEFAULT_SELECTION_REGISTRY_ID,
        },
        {
            "code": "REAL_CAPABILITY_REQUIREMENT_ROWS_EXIST",
            "passed": requirements_payload["capability_requirement_count"] == expected_requirement_count,
        },
        {
            "code": "ALL_REQUIRED_CAPABILITIES_RECORDED",
            "passed": requirements_payload["required_for_beta_count"] == expected_requirement_count,
        },
        {
            "code": "NO_CAPABILITY_SUPPORT_CLAIMED_YET",
            "passed": requirements_payload["candidate_claimed_supported_count"] == 0,
        },
        {
            "code": "NO_CAPABILITY_CONTRACT_VERIFIED_YET",
            "passed": requirements_payload["contract_verified_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_ACTIVATED",
            "passed": contract["provider_activated"] is False and requirements_payload["provider_activated_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_RECOMMENDED",
            "passed": contract["provider_recommended"] is False and requirements_payload["provider_recommended_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_SELECTED",
            "passed": contract["provider_selected"] is False and requirements_payload["provider_selected_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_CONFIGURED",
            "passed": contract["provider_configured"] is False and requirements_payload["provider_configured_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_READ_ENABLED",
            "passed": contract["provider_read_enabled"] is False and requirements_payload["provider_read_enabled_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_WRITE_ENABLED",
            "passed": contract["provider_write_enabled"] is False and requirements_payload["provider_write_enabled_count"] == 0,
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
            "passed": contract["risk_accepted"] is False,
        },
        {
            "code": "NO_RISK_WAIVED",
            "passed": contract["risk_waived"] is False,
        },
        {
            "code": "NO_MITIGATION_APPROVED",
            "passed": contract["mitigation_approved"] is False,
        },
        {
            "code": "NO_OBJECT_BODY_VIEW",
            "passed": contract["object_body_view_enabled"] is False and requirements_payload["object_body_view_enabled_count"] == 0,
        },
        {
            "code": "NO_DIRECT_UPLOAD",
            "passed": contract["direct_upload_enabled"] is False,
        },
        {
            "code": "NO_EXPORT",
            "passed": contract["export_enabled"] is False and requirements_payload["export_enabled_count"] == 0,
        },
        {
            "code": "NO_EXECUTION",
            "passed": contract["execution_enabled"] is False and requirements_payload["execution_enabled_count"] == 0,
        },
        {
            "code": "VAULT_NOT_DONE",
            "passed": contract["vault_done"] is False,
        },
        {
            "code": "EVENT_LOG_EXISTS",
            "passed": events_payload["event_count"] >= 4,
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
        "safe_to_continue_to_gp058": len(failed) == 0,
    }


def get_storage_provider_capability_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp058": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "Continue under ARCHIVE VAULT — STORAGE PROVIDER PREP LAYER / GP051-GP060. Keep Vault real and durable. Do not switch to Clouds unless Solice explicitly asks.",
            "carry_forward_rules": [
                "Keep real SQLite capability contract.",
                "Keep real capability requirement rows.",
                "Keep real capability event log.",
                "Build the real provider risk/criteria validation engine next.",
                "Do not activate a provider yet.",
                "Do not recommend a provider yet.",
                "Do not select a provider yet.",
                "Do not configure a provider yet.",
                "Do not enable provider read or write yet.",
                "Do not claim provider object reads.",
                "Do not accept or waive risk.",
                "Do not approve mitigation.",
                "Do not unlock object body view.",
                "Do not unlock direct upload.",
                "Do not unlock export.",
                "Do not unlock execution.",
                "Treat this as safe to continue, not Vault done.",
            ],
        },
    }


def get_real_storage_provider_capability_contract_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_capability_contract(db_path)
    contract = get_storage_provider_capability_contract_record(db_path)["contract"]
    requirements = get_storage_provider_capability_requirements(db_path)
    events = get_storage_provider_capability_events(db_path)
    validation = validate_storage_provider_capability_contract(db_path)

    return {
        "pack": _pack_payload(),
        "capability_truth": _capability_truth(contract, requirements, events["event_count"], validation),
        "store": init,
        "contract": contract,
        "requirements": requirements,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_capability_next_step()["next_step"],
    }


def get_gp057_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_capability_contract_home(db_path)
    contract = home["contract"]
    requirements = home["requirements"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp057_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_capability_contract_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_contract_count": home["store"]["contract_count"],
            "real_capability_requirement_count": home["store"]["capability_requirement_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp056_selection_registry_attached": True,
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp058": validation["safe_to_continue_to_gp058"],
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "provider_activated": contract["provider_activated"],
            "provider_recommended": contract["provider_recommended"],
            "provider_selected": contract["provider_selected"],
            "provider_configured": contract["provider_configured"],
            "provider_write_enabled": contract["provider_write_enabled"],
            "provider_read_enabled": contract["provider_read_enabled"],
            "provider_object_read_claimed": contract["provider_object_read_claimed"],
            "provider_connection_tested": contract["provider_connection_tested"],
            "capability_candidate_claimed_supported_count": requirements["candidate_claimed_supported_count"],
            "capability_contract_verified_count": requirements["contract_verified_count"],
            "risk_accepted": contract["risk_accepted"],
            "risk_waived": contract["risk_waived"],
            "mitigation_approved": contract["mitigation_approved"],
            "object_body_view_enabled": contract["object_body_view_enabled"],
            "direct_upload_enabled": contract["direct_upload_enabled"],
            "export_enabled": contract["export_enabled"],
            "execution_enabled": contract["execution_enabled"],
            "clouds_status": "parked_do_not_continue_from_vault_gp057",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "capability_truth": home["capability_truth"],
        "routes": home["routes"],
        "contract": contract,
        "requirements": requirements,
        "validation": validation,
        "next_step": home["next_step"],
    }


def _pack_payload() -> Dict[str, Any]:
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP056"],
        "foundation_status": "safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_capability_contract",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }


def _routes_payload() -> Dict[str, str]:
    return {
        "room_title": "Vault Real Storage Provider Capability Contract",
        "section_header": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "route": "/vault/real-storage-provider-capability-contract",
        "json_route": "/vault/real-storage-provider-capability-contract.json",
        "contract_route": "/vault/storage-provider-capability-contract-record.json",
        "requirements_route": "/vault/storage-provider-capability-requirements.json",
        "events_route": "/vault/storage-provider-capability-events.json",
        "validation_route": "/vault/storage-provider-capability-validation.json",
        "next_step_route": "/vault/storage-provider-capability-next-step.json",
        "gp057_status_route": "/vault/gp057-status.json",
    }


def _capability_truth(
    contract: Dict[str, Any],
    requirements: Dict[str, Any],
    event_count: int,
    validation: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "real_storage_provider_capability_contract_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "real_capability_contract_exists": contract["contract_id"] == DEFAULT_CAPABILITY_CONTRACT_ID,
        "real_capability_requirement_rows_exist": requirements["capability_requirement_count"] == 5 * len(CAPABILITY_REQUIREMENTS),
        "real_event_log_exists": event_count >= 4,
        "source_gp056_selection_registry_attached": contract["source_selection_registry_id"] == DEFAULT_SELECTION_REGISTRY_ID,
        "validation_passed": validation["valid"],
        "provider_candidate_count": requirements["provider_candidate_count"],
        "capability_code_count": requirements["capability_code_count"],
        "capability_requirement_count": requirements["capability_requirement_count"],
        "provider_activated": contract["provider_activated"],
        "provider_recommended": contract["provider_recommended"],
        "provider_selected": contract["provider_selected"],
        "provider_configured": contract["provider_configured"],
        "provider_read_enabled": contract["provider_read_enabled"],
        "provider_write_enabled": contract["provider_write_enabled"],
        "candidate_claimed_supported_count": requirements["candidate_claimed_supported_count"],
        "contract_verified_count": requirements["contract_verified_count"],
        "risk_accepted": contract["risk_accepted"],
        "risk_waived": contract["risk_waived"],
        "mitigation_approved": contract["mitigation_approved"],
        "object_body_view_enabled": contract["object_body_view_enabled"],
        "direct_upload_enabled": contract["direct_upload_enabled"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "vault_done": contract["vault_done"],
        "safe_to_continue_to_gp058": validation["safe_to_continue_to_gp058"],
    }


def render_real_storage_provider_capability_contract_page() -> str:
    home = get_real_storage_provider_capability_contract_home()
    truth = home["capability_truth"]
    requirements = home["requirements"]["requirements"]
    routes = home["routes"]
    next_step = home["next_step"]

    requirement_cards = "\n".join(_render_requirement_card(item) for item in requirements[:12])
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
  <title>Vault Real Storage Provider Capability Contract · GP057</title>
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
      <div class="eyebrow">Archive Vault · Giant Pack 057</div>
      <div class="eyebrow">Storage Provider Prep Layer · GP051-GP060</div>
      <h1>Real Storage Provider Capability Contract</h1>
      <p>
        GP057 creates a real SQLite-backed capability contract with concrete capability requirement rows.
        The contract is real and durable, but provider activation remains locked.
      </p>
      <div class="metrics">
        <div class="metric"><strong>{home['store']['contract_count']}</strong><span>real contracts</span></div>
        <div class="metric"><strong>{home['store']['capability_requirement_count']}</strong><span>capability rows</span></div>
        <div class="metric"><strong>{home['store']['event_count']}</strong><span>real contract events</span></div>
        <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
      </div>
      <div class="chips">
        <span class="pill ok">Real SQLite-backed</span>
        <span class="pill ok">Real capability contract</span>
        <span class="pill ok">Real requirement rows</span>
        <span class="pill danger">No provider activated</span>
        <span class="pill danger">No export</span>
        <span class="pill danger">No execution</span>
      </div>
    </section>

    <section class="section">
      <h2>Capability Requirements</h2>
      <p>These are real contract requirement rows. They are not provider activation, selection, or verification claims.</p>
      <div class="grid">{requirement_cards}</div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Validation Checks</h2>
        <p>GP057 validates the real capability contract against active Tower/Vault locks.</p>
        {checks}
      </div>
      <div>
        <h2>Carry Forward to GP058</h2>
        <p>{escape(next_step['owner_notebook_note'])}</p>
        <ul>{rules}</ul>
      </div>
    </section>

    <section class="section">
      <h2>GP057 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['contract_route'])}</code>
        <code>{escape(routes['requirements_route'])}</code>
        <code>{escape(routes['events_route'])}</code>
        <code>{escape(routes['validation_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp057_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_requirement_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="title">{escape(item['capability_name'])}</div>
        <div class="meta">
          Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
          Capability: <code>{escape(item['capability_code'])}</code><br>
          Required: <code>{str(item['required_for_beta']).lower()}</code><br>
          Claimed: <code>{str(item['candidate_claimed_supported']).lower()}</code><br>
          Verified: <code>{str(item['contract_verified']).lower()}</code>
        </div>
      </article>
    """
