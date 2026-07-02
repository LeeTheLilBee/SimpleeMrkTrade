"""
VAULT GIANT PACK 056 — Real Storage Provider Selection Registry

CURRENT SECTION:
Archive Vault — Storage Provider Prep Layer
GP051-GP060

This pack adds a real durable SQLite-backed provider selection registry.

Purpose:
- Create a real provider selection registry schema.
- Persist a real selection registry record sourced from GP055.
- Persist real candidate registry entries.
- Persist a real registry event log.
- Validate the registry against Tower/Vault locks.
- Provide real read/list/validate/event routes.

Important truth:
- GP056 creates real provider candidate registry rows.
- GP056 links to the real GP055 decision record.
- GP056 does not recommend a provider.
- GP056 does not select a provider.
- GP056 does not configure a provider.
- GP056 does not enable provider read/write.
- GP056 does not accept/waive risk or approve mitigation.
- GP056 does not unlock object bodies, raw storage, upload, export, or execution.
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

from vault.real_storage_provider_decision_record_service import (
    DEFAULT_DECISION_RECORD_ID,
    get_current_storage_provider_decision_record,
)


PACK_ID = "VAULT_GP056"
PACK_NAME = "Real Storage Provider Selection Registry"
SCHEMA_VERSION = "vault.real_storage_provider_selection_registry.v1"

SECTION_ID = "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
SECTION_TITLE = "Archive Vault — Storage Provider Prep Layer"
SECTION_RANGE = "GP051-GP060"

NEXT_PACK = "VAULT_GP057_REAL_STORAGE_PROVIDER_CAPABILITY_CONTRACT"
NEXT_PACK_TITLE = "Real Storage Provider Capability Contract"

DEFAULT_SELECTION_REGISTRY_ID = "VSPSR-GP056-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_SELECTION_REGISTRY_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_selection_registry.sqlite"


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


def ensure_selection_registry_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_selection_registries (
                registry_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_decision_record_id TEXT NOT NULL,
                source_decision_pack_id TEXT NOT NULL,
                registry_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                registry_data_json TEXT NOT NULL,
                recommended_provider_id TEXT,
                selected_provider_id TEXT,
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_selection_candidates (
                candidate_entry_id TEXT PRIMARY KEY,
                registry_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                candidate_type TEXT NOT NULL,
                decision_state TEXT NOT NULL,
                comparison_row_id TEXT NOT NULL,
                criteria_card_count INTEGER NOT NULL,
                risk_card_count INTEGER NOT NULL,
                comparison_factor_count INTEGER NOT NULL,
                rank_present INTEGER NOT NULL DEFAULT 0,
                rank_finalized INTEGER NOT NULL DEFAULT 0,
                comparison_score_present INTEGER NOT NULL DEFAULT 0,
                comparison_score_finalized INTEGER NOT NULL DEFAULT 0,
                provider_recommended INTEGER NOT NULL DEFAULT 0,
                provider_selected INTEGER NOT NULL DEFAULT 0,
                provider_configured INTEGER NOT NULL DEFAULT 0,
                provider_read_enabled INTEGER NOT NULL DEFAULT 0,
                provider_write_enabled INTEGER NOT NULL DEFAULT 0,
                risk_accepted INTEGER NOT NULL DEFAULT 0,
                risk_waived INTEGER NOT NULL DEFAULT 0,
                mitigation_approved INTEGER NOT NULL DEFAULT 0,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_granted INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(registry_id)
                    REFERENCES vault_storage_provider_selection_registries(registry_id)
                    ON DELETE CASCADE,
                UNIQUE(registry_id, provider_candidate_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_selection_events (
                event_id TEXT PRIMARY KEY,
                registry_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(registry_id)
                    REFERENCES vault_storage_provider_selection_registries(registry_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_storage_provider_selection_candidates_registry
            ON vault_storage_provider_selection_candidates(registry_id, provider_candidate_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_storage_provider_selection_events_registry
            ON vault_storage_provider_selection_events(registry_id, created_at)
            """
        )
        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "tables": [
            "vault_storage_provider_selection_registries",
            "vault_storage_provider_selection_candidates",
            "vault_storage_provider_selection_events",
        ],
        "real_sqlite_backed": True,
    }


def initialize_real_storage_provider_selection_registry(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_selection_registry_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            """
            SELECT registry_id
            FROM vault_storage_provider_selection_registries
            WHERE registry_id = ?
            """,
            (DEFAULT_SELECTION_REGISTRY_ID,),
        ).fetchone()

        if existing is None:
            decision_record = get_current_storage_provider_decision_record()["current_record"]
            registry_data = _build_registry_data(decision_record)
            now = _now_iso()

            conn.execute(
                """
                INSERT INTO vault_storage_provider_selection_registries (
                    registry_id,
                    pack_id,
                    section_id,
                    section_range,
                    source_decision_record_id,
                    source_decision_pack_id,
                    registry_status,
                    tower_authority_status,
                    registry_data_json,
                    recommended_provider_id,
                    selected_provider_id,
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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    DEFAULT_SELECTION_REGISTRY_ID,
                    PACK_ID,
                    SECTION_ID,
                    SECTION_RANGE,
                    decision_record["record_id"],
                    decision_record["pack_id"],
                    "REAL_SELECTION_REGISTRY_OPEN_TOWER_LOCKED",
                    "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    _json_dumps(registry_data),
                    None,
                    None,
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

            for candidate in decision_record["decision_data"]["candidate_records"]:
                _insert_candidate_entry(conn, DEFAULT_SELECTION_REGISTRY_ID, candidate, now)

            _insert_event(
                conn,
                DEFAULT_SELECTION_REGISTRY_ID,
                "REAL_SELECTION_REGISTRY_CREATED",
                {
                    "pack_id": PACK_ID,
                    "source_decision_record_id": decision_record["record_id"],
                    "source_decision_pack_id": decision_record["pack_id"],
                    "real_sqlite_backed": True,
                    "registry_status": "REAL_SELECTION_REGISTRY_OPEN_TOWER_LOCKED",
                    "provider_selected": False,
                    "provider_recommended": False,
                    "provider_configured": False,
                    "provider_read_enabled": False,
                    "provider_write_enabled": False,
                },
            )
            _insert_event(
                conn,
                DEFAULT_SELECTION_REGISTRY_ID,
                "SOURCE_GP055_DECISION_RECORD_ATTACHED",
                _compact_decision_source_snapshot(decision_record),
            )
            _insert_event(
                conn,
                DEFAULT_SELECTION_REGISTRY_ID,
                "REAL_CANDIDATE_REGISTRY_ENTRIES_CREATED",
                {
                    "candidate_entry_count": len(decision_record["decision_data"]["candidate_records"]),
                    "provider_selected_count": 0,
                    "provider_recommended_count": 0,
                    "provider_configured_count": 0,
                    "provider_read_enabled_count": 0,
                    "provider_write_enabled_count": 0,
                },
            )
            _insert_event(
                conn,
                DEFAULT_SELECTION_REGISTRY_ID,
                "TOWER_SELECTION_LOCKS_CONFIRMED",
                {
                    "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    "provider_recommendation_blocked": True,
                    "provider_selection_blocked": True,
                    "provider_configuration_blocked": True,
                    "provider_read_write_blocked": True,
                    "export_blocked": True,
                    "execution_blocked": True,
                },
            )
            conn.commit()

    counts = _get_counts(path)
    return {
        "initialized": True,
        "schema": schema,
        "registry_id": DEFAULT_SELECTION_REGISTRY_ID,
        "registry_count": counts["registry_count"],
        "candidate_count": counts["candidate_count"],
        "event_count": counts["event_count"],
        "real_sqlite_backed": True,
    }


def _insert_candidate_entry(
    conn: sqlite3.Connection,
    registry_id: str,
    candidate: Dict[str, Any],
    now: str,
) -> str:
    candidate_entry_id = f"VSPSC-{candidate['provider_candidate_id'].split('-', 1)[-1]}"
    conn.execute(
        """
        INSERT INTO vault_storage_provider_selection_candidates (
            candidate_entry_id,
            registry_id,
            provider_candidate_id,
            candidate_type,
            decision_state,
            comparison_row_id,
            criteria_card_count,
            risk_card_count,
            comparison_factor_count,
            rank_present,
            rank_finalized,
            comparison_score_present,
            comparison_score_finalized,
            provider_recommended,
            provider_selected,
            provider_configured,
            provider_read_enabled,
            provider_write_enabled,
            risk_accepted,
            risk_waived,
            mitigation_approved,
            tower_review_required,
            tower_review_granted,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            candidate_entry_id,
            registry_id,
            candidate["provider_candidate_id"],
            candidate["candidate_type"],
            "REAL_SELECTION_CANDIDATE_REGISTERED_NOT_RECOMMENDED_NOT_SELECTED",
            candidate["comparison_row_id"],
            int(candidate["criteria_card_count"]),
            int(candidate["risk_card_count"]),
            int(candidate["comparison_factor_count"]),
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
            1,
            0,
            now,
            now,
        ),
    )
    return candidate_entry_id


def _insert_event(
    conn: sqlite3.Connection,
    registry_id: str,
    event_type: str,
    event_payload: Dict[str, Any],
) -> str:
    event_id = f"VSPSE-{uuid.uuid4().hex[:16].upper()}"
    conn.execute(
        """
        INSERT INTO vault_storage_provider_selection_events (
            event_id,
            registry_id,
            event_type,
            event_payload_json,
            created_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            event_id,
            registry_id,
            event_type,
            _json_dumps(event_payload),
            _now_iso(),
        ),
    )
    return event_id


def _get_counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        registry_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_selection_registries"
        ).fetchone()["c"]
        candidate_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_selection_candidates"
        ).fetchone()["c"]
        event_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_selection_events"
        ).fetchone()["c"]

    return {
        "registry_count": int(registry_count),
        "candidate_count": int(candidate_count),
        "event_count": int(event_count),
    }


def _compact_decision_source_snapshot(decision_record: Dict[str, Any]) -> Dict[str, Any]:
    decision_data = decision_record["decision_data"]
    return {
        "source_decision_record_id": decision_record["record_id"],
        "source_decision_pack_id": decision_record["pack_id"],
        "source_decision_status": decision_record["decision_status"],
        "source_section": decision_record["section_id"],
        "source_section_range": decision_record["section_range"],
        "provider_candidate_count": decision_data["provider_candidate_count"],
        "recommended_provider_id": decision_record["recommended_provider_id"],
        "selected_provider_id": decision_record["selected_provider_id"],
        "provider_configured": decision_record["provider_configured"],
        "provider_read_enabled": decision_record["provider_read_enabled"],
        "provider_write_enabled": decision_record["provider_write_enabled"],
        "risk_accepted": decision_record["risk_accepted"],
        "risk_waived": decision_record["risk_waived"],
        "mitigation_approved": decision_record["mitigation_approved"],
        "export_enabled": decision_record["export_enabled"],
        "execution_enabled": decision_record["execution_enabled"],
        "vault_done": decision_record["vault_done"],
    }


def _build_registry_data(decision_record: Dict[str, Any]) -> Dict[str, Any]:
    candidate_entries = []

    for candidate in decision_record["decision_data"]["candidate_records"]:
        candidate_entries.append(
            {
                "provider_candidate_id": candidate["provider_candidate_id"],
                "candidate_type": candidate["candidate_type"],
                "comparison_row_id": candidate["comparison_row_id"],
                "registry_state": "REAL_SELECTION_CANDIDATE_REGISTERED_NOT_RECOMMENDED_NOT_SELECTED",
                "criteria_card_count": candidate["criteria_card_count"],
                "risk_card_count": candidate["risk_card_count"],
                "comparison_factor_count": candidate["comparison_factor_count"],
                "rank_present": False,
                "rank_finalized": False,
                "comparison_score_present": False,
                "comparison_score_finalized": False,
                "provider_recommended": False,
                "provider_selected": False,
                "provider_configured": False,
                "provider_read_enabled": False,
                "provider_write_enabled": False,
                "risk_accepted": False,
                "risk_waived": False,
                "mitigation_approved": False,
                "tower_review_required": True,
                "tower_review_granted": False,
                "safe_to_continue_to_gp057": True,
            }
        )

    return {
        "registry_schema_version": SCHEMA_VERSION,
        "registry_type": "REAL_STORAGE_PROVIDER_SELECTION_REGISTRY",
        "registry_status": "REAL_SELECTION_REGISTRY_OPEN_TOWER_LOCKED",
        "real_durable_registry": True,
        "metadata_source": "VAULT_GP055_REAL_STORAGE_PROVIDER_DECISION_RECORD",
        "source_decision_record_id": decision_record["record_id"],
        "source_decision_pack_id": decision_record["pack_id"],
        "provider_candidate_count": len(candidate_entries),
        "candidate_entries": candidate_entries,
        "selection_summary": {
            "provider_recommended": False,
            "recommended_provider_id": None,
            "provider_selected": False,
            "selected_provider_id": None,
            "provider_configured": False,
            "provider_read_enabled": False,
            "provider_write_enabled": False,
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
            "provider_recommendation_blocked": True,
            "provider_selection_blocked": True,
            "provider_configuration_blocked": True,
            "provider_read_write_blocked": True,
            "risk_acceptance_blocked": True,
            "mitigation_approval_blocked": True,
            "object_body_view_blocked": True,
            "direct_upload_blocked": True,
            "export_blocked": True,
            "execution_blocked": True,
        },
        "next_pack": NEXT_PACK,
        "next_pack_title": NEXT_PACK_TITLE,
        "safe_to_continue_to_gp057": True,
    }


def _row_to_registry(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "registry_id": row["registry_id"],
        "pack_id": row["pack_id"],
        "section_id": row["section_id"],
        "section_range": row["section_range"],
        "source_decision_record_id": row["source_decision_record_id"],
        "source_decision_pack_id": row["source_decision_pack_id"],
        "registry_status": row["registry_status"],
        "tower_authority_status": row["tower_authority_status"],
        "registry_data": _json_loads(row["registry_data_json"]),
        "recommended_provider_id": row["recommended_provider_id"],
        "selected_provider_id": row["selected_provider_id"],
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


def _row_to_candidate(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "candidate_entry_id": row["candidate_entry_id"],
        "registry_id": row["registry_id"],
        "provider_candidate_id": row["provider_candidate_id"],
        "candidate_type": row["candidate_type"],
        "decision_state": row["decision_state"],
        "comparison_row_id": row["comparison_row_id"],
        "criteria_card_count": int(row["criteria_card_count"]),
        "risk_card_count": int(row["risk_card_count"]),
        "comparison_factor_count": int(row["comparison_factor_count"]),
        "rank_present": bool(row["rank_present"]),
        "rank_finalized": bool(row["rank_finalized"]),
        "comparison_score_present": bool(row["comparison_score_present"]),
        "comparison_score_finalized": bool(row["comparison_score_finalized"]),
        "provider_recommended": bool(row["provider_recommended"]),
        "provider_selected": bool(row["provider_selected"]),
        "provider_configured": bool(row["provider_configured"]),
        "provider_read_enabled": bool(row["provider_read_enabled"]),
        "provider_write_enabled": bool(row["provider_write_enabled"]),
        "risk_accepted": bool(row["risk_accepted"]),
        "risk_waived": bool(row["risk_waived"]),
        "mitigation_approved": bool(row["mitigation_approved"]),
        "tower_review_required": bool(row["tower_review_required"]),
        "tower_review_granted": bool(row["tower_review_granted"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_event(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "event_id": row["event_id"],
        "registry_id": row["registry_id"],
        "event_type": row["event_type"],
        "event_payload": _json_loads(row["event_payload_json"]),
        "created_at": row["created_at"],
    }


def get_storage_provider_selection_registry_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_selection_registry(db_path)

    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_selection_registries
            WHERE registry_id = ?
            """,
            (DEFAULT_SELECTION_REGISTRY_ID,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Real storage provider selection registry was not initialized.")

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "registry": _row_to_registry(row),
    }


def get_storage_provider_selection_candidates(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_selection_registry(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_selection_candidates
            WHERE registry_id = ?
            ORDER BY provider_candidate_id ASC
            """,
            (DEFAULT_SELECTION_REGISTRY_ID,),
        ).fetchall()

    candidates = [_row_to_candidate(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "candidate_count": len(candidates),
        "provider_recommended_count": sum(1 for item in candidates if item["provider_recommended"]),
        "provider_selected_count": sum(1 for item in candidates if item["provider_selected"]),
        "provider_configured_count": sum(1 for item in candidates if item["provider_configured"]),
        "provider_read_enabled_count": sum(1 for item in candidates if item["provider_read_enabled"]),
        "provider_write_enabled_count": sum(1 for item in candidates if item["provider_write_enabled"]),
        "risk_accepted_count": sum(1 for item in candidates if item["risk_accepted"]),
        "risk_waived_count": sum(1 for item in candidates if item["risk_waived"]),
        "mitigation_approved_count": sum(1 for item in candidates if item["mitigation_approved"]),
        "tower_review_required_count": sum(1 for item in candidates if item["tower_review_required"]),
        "tower_review_granted_count": sum(1 for item in candidates if item["tower_review_granted"]),
        "candidates": candidates,
    }


def get_storage_provider_selection_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_selection_registry(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_selection_events
            WHERE registry_id = ?
            ORDER BY created_at ASC, event_id ASC
            """,
            (DEFAULT_SELECTION_REGISTRY_ID,),
        ).fetchall()

    events = [_row_to_event(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "event_count": len(events),
        "events": events,
    }


def record_storage_provider_selection_review_event(
    event_type: str,
    event_payload: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    initialize_real_storage_provider_selection_registry(db_path)
    payload = dict(event_payload or {})
    payload.update(
        {
            "write_type": "REAL_SELECTION_REGISTRY_REVIEW_EVENT",
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
            DEFAULT_SELECTION_REGISTRY_ID,
            event_type,
            payload,
        )
        conn.commit()

    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "registry_id": DEFAULT_SELECTION_REGISTRY_ID,
        "real_sqlite_backed": True,
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


def validate_storage_provider_selection_registry(db_path: Optional[str] = None) -> Dict[str, Any]:
    registry = get_storage_provider_selection_registry_record(db_path)["registry"]
    candidates_payload = get_storage_provider_selection_candidates(db_path)
    events_payload = get_storage_provider_selection_events(db_path)

    candidates = candidates_payload["candidates"]
    checks = [
        {
            "code": "REAL_SQLITE_SELECTION_REGISTRY_EXISTS",
            "passed": registry["registry_id"] == DEFAULT_SELECTION_REGISTRY_ID,
        },
        {
            "code": "SOURCE_GP055_DECISION_RECORD_ATTACHED",
            "passed": registry["source_decision_record_id"] == DEFAULT_DECISION_RECORD_ID,
        },
        {
            "code": "REAL_CANDIDATE_REGISTRY_ROWS_EXIST",
            "passed": len(candidates) == 5,
        },
        {
            "code": "NO_PROVIDER_RECOMMENDED",
            "passed": registry["recommended_provider_id"] is None and candidates_payload["provider_recommended_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_SELECTED",
            "passed": registry["selected_provider_id"] is None and candidates_payload["provider_selected_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_CONFIGURED",
            "passed": registry["provider_configured"] is False and candidates_payload["provider_configured_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_READ_ENABLED",
            "passed": registry["provider_read_enabled"] is False and candidates_payload["provider_read_enabled_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_WRITE_ENABLED",
            "passed": registry["provider_write_enabled"] is False and candidates_payload["provider_write_enabled_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_OBJECT_READ_CLAIMED",
            "passed": registry["provider_object_read_claimed"] is False,
        },
        {
            "code": "NO_PROVIDER_CONNECTION_TESTED",
            "passed": registry["provider_connection_tested"] is False,
        },
        {
            "code": "NO_RISK_ACCEPTED",
            "passed": registry["risk_accepted"] is False and candidates_payload["risk_accepted_count"] == 0,
        },
        {
            "code": "NO_RISK_WAIVED",
            "passed": registry["risk_waived"] is False and candidates_payload["risk_waived_count"] == 0,
        },
        {
            "code": "NO_MITIGATION_APPROVED",
            "passed": registry["mitigation_approved"] is False and candidates_payload["mitigation_approved_count"] == 0,
        },
        {
            "code": "NO_OBJECT_BODY_VIEW",
            "passed": registry["object_body_view_enabled"] is False,
        },
        {
            "code": "NO_DIRECT_UPLOAD",
            "passed": registry["direct_upload_enabled"] is False,
        },
        {
            "code": "NO_EXPORT",
            "passed": registry["export_enabled"] is False,
        },
        {
            "code": "NO_EXECUTION",
            "passed": registry["execution_enabled"] is False,
        },
        {
            "code": "VAULT_NOT_DONE",
            "passed": registry["vault_done"] is False,
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
        "safe_to_continue_to_gp057": len(failed) == 0,
    }


def get_storage_provider_selection_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp057": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "Continue under ARCHIVE VAULT — STORAGE PROVIDER PREP LAYER / GP051-GP060. Keep Vault real and durable. Do not switch to Clouds unless Solice explicitly asks.",
            "carry_forward_rules": [
                "Keep real SQLite selection registry.",
                "Keep real candidate registry rows.",
                "Keep real selection registry events.",
                "Build the real storage provider capability contract next.",
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


def get_real_storage_provider_selection_registry_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_selection_registry(db_path)
    registry = get_storage_provider_selection_registry_record(db_path)["registry"]
    candidates = get_storage_provider_selection_candidates(db_path)
    events = get_storage_provider_selection_events(db_path)
    validation = validate_storage_provider_selection_registry(db_path)

    return {
        "pack": _pack_payload(),
        "selection_truth": _selection_truth(registry, candidates, events["event_count"], validation),
        "store": init,
        "registry": registry,
        "candidates": candidates,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_selection_next_step()["next_step"],
    }


def get_gp056_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_selection_registry_home(db_path)
    registry = home["registry"]
    candidates = home["candidates"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp056_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_selection_registry_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_registry_count": home["store"]["registry_count"],
            "real_candidate_count": home["store"]["candidate_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp055_decision_record_attached": True,
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp057": validation["safe_to_continue_to_gp057"],
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "provider_recommended": registry["recommended_provider_id"] is not None,
            "provider_selected": registry["selected_provider_id"] is not None,
            "provider_configured": registry["provider_configured"],
            "provider_write_enabled": registry["provider_write_enabled"],
            "provider_read_enabled": registry["provider_read_enabled"],
            "provider_object_read_claimed": registry["provider_object_read_claimed"],
            "provider_connection_tested": registry["provider_connection_tested"],
            "candidate_provider_recommended_count": candidates["provider_recommended_count"],
            "candidate_provider_selected_count": candidates["provider_selected_count"],
            "candidate_provider_configured_count": candidates["provider_configured_count"],
            "candidate_provider_read_enabled_count": candidates["provider_read_enabled_count"],
            "candidate_provider_write_enabled_count": candidates["provider_write_enabled_count"],
            "risk_accepted": registry["risk_accepted"],
            "risk_waived": registry["risk_waived"],
            "mitigation_approved": registry["mitigation_approved"],
            "object_body_view_enabled": registry["object_body_view_enabled"],
            "direct_upload_enabled": registry["direct_upload_enabled"],
            "export_enabled": registry["export_enabled"],
            "execution_enabled": registry["execution_enabled"],
            "clouds_status": "parked_do_not_continue_from_vault_gp056",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "selection_truth": home["selection_truth"],
        "routes": home["routes"],
        "registry": registry,
        "candidates": candidates,
        "validation": validation,
        "next_step": home["next_step"],
    }


def _pack_payload() -> Dict[str, Any]:
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP055"],
        "foundation_status": "safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_selection_registry",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }


def _routes_payload() -> Dict[str, str]:
    return {
        "room_title": "Vault Real Storage Provider Selection Registry",
        "section_header": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "route": "/vault/real-storage-provider-selection-registry",
        "json_route": "/vault/real-storage-provider-selection-registry.json",
        "registry_route": "/vault/storage-provider-selection-registry-record.json",
        "candidates_route": "/vault/storage-provider-selection-candidates.json",
        "events_route": "/vault/storage-provider-selection-events.json",
        "validation_route": "/vault/storage-provider-selection-validation.json",
        "next_step_route": "/vault/storage-provider-selection-next-step.json",
        "gp056_status_route": "/vault/gp056-status.json",
    }


def _selection_truth(
    registry: Dict[str, Any],
    candidates: Dict[str, Any],
    event_count: int,
    validation: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "real_storage_provider_selection_registry_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "real_selection_registry_exists": registry["registry_id"] == DEFAULT_SELECTION_REGISTRY_ID,
        "real_candidate_registry_rows_exist": candidates["candidate_count"] == 5,
        "real_event_log_exists": event_count >= 4,
        "source_gp055_decision_record_attached": registry["source_decision_record_id"] == DEFAULT_DECISION_RECORD_ID,
        "validation_passed": validation["valid"],
        "provider_candidate_count": candidates["candidate_count"],
        "provider_recommended": registry["recommended_provider_id"] is not None,
        "provider_selected": registry["selected_provider_id"] is not None,
        "provider_configured": registry["provider_configured"],
        "provider_read_enabled": registry["provider_read_enabled"],
        "provider_write_enabled": registry["provider_write_enabled"],
        "candidate_provider_recommended_count": candidates["provider_recommended_count"],
        "candidate_provider_selected_count": candidates["provider_selected_count"],
        "candidate_provider_configured_count": candidates["provider_configured_count"],
        "candidate_provider_read_enabled_count": candidates["provider_read_enabled_count"],
        "candidate_provider_write_enabled_count": candidates["provider_write_enabled_count"],
        "risk_accepted": registry["risk_accepted"],
        "risk_waived": registry["risk_waived"],
        "mitigation_approved": registry["mitigation_approved"],
        "object_body_view_enabled": registry["object_body_view_enabled"],
        "direct_upload_enabled": registry["direct_upload_enabled"],
        "export_enabled": registry["export_enabled"],
        "execution_enabled": registry["execution_enabled"],
        "vault_done": registry["vault_done"],
        "safe_to_continue_to_gp057": validation["safe_to_continue_to_gp057"],
    }


def render_real_storage_provider_selection_registry_page() -> str:
    home = get_real_storage_provider_selection_registry_home()
    truth = home["selection_truth"]
    candidates = home["candidates"]["candidates"]
    routes = home["routes"]
    next_step = home["next_step"]

    candidate_cards = "\n".join(_render_candidate_card(item) for item in candidates)
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
  <title>Vault Real Storage Provider Selection Registry · GP056</title>
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
      <div class="eyebrow">Archive Vault · Giant Pack 056</div>
      <div class="eyebrow">Storage Provider Prep Layer · GP051-GP060</div>
      <h1>Real Storage Provider Selection Registry</h1>
      <p>
        GP056 creates a real SQLite-backed provider selection registry with durable candidate entries,
        a source link to GP055, and a registry event log. The registry is real, but selection remains locked.
      </p>
      <div class="metrics">
        <div class="metric"><strong>{home['store']['registry_count']}</strong><span>real registries</span></div>
        <div class="metric"><strong>{home['store']['candidate_count']}</strong><span>real candidate rows</span></div>
        <div class="metric"><strong>{home['store']['event_count']}</strong><span>real registry events</span></div>
        <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
      </div>
      <div class="chips">
        <span class="pill ok">Real SQLite-backed</span>
        <span class="pill ok">Real candidate rows</span>
        <span class="pill ok">Real event log</span>
        <span class="pill danger">No provider selected</span>
        <span class="pill danger">No export</span>
        <span class="pill danger">No execution</span>
      </div>
    </section>

    <section class="section">
      <h2>Registered Provider Candidates</h2>
      <p>These are real registry rows. They are not recommendations or selections.</p>
      <div class="grid">{candidate_cards}</div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Validation Checks</h2>
        <p>GP056 validates the real selection registry against active Tower/Vault locks.</p>
        {checks}
      </div>
      <div>
        <h2>Carry Forward to GP057</h2>
        <p>{escape(next_step['owner_notebook_note'])}</p>
        <ul>{rules}</ul>
      </div>
    </section>

    <section class="section">
      <h2>GP056 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['registry_route'])}</code>
        <code>{escape(routes['candidates_route'])}</code>
        <code>{escape(routes['events_route'])}</code>
        <code>{escape(routes['validation_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp056_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_candidate_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="title">{escape(item['candidate_type'])}</div>
        <div class="meta">
          Entry: <code>{escape(item['candidate_entry_id'])}</code><br>
          Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
          State: <code>{escape(item['decision_state'])}</code><br>
          Recommended: <code>{str(item['provider_recommended']).lower()}</code><br>
          Selected: <code>{str(item['provider_selected']).lower()}</code><br>
          Read/write: <code>{str(item['provider_read_enabled']).lower()} / {str(item['provider_write_enabled']).lower()}</code>
        </div>
      </article>
    """
