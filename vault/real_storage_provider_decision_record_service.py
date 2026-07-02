"""
VAULT GIANT PACK 055 — Real Storage Provider Decision Record

CURRENT SECTION:
Archive Vault — Storage Provider Prep Layer
GP051-GP060

This pack replaces placeholder-only provider decision work with a real durable
SQLite-backed storage provider decision record.

Purpose:
- Create a real storage provider decision SQLite schema.
- Persist a real decision record sourced from GP054 comparison state.
- Persist a real decision event log.
- Validate the decision record against Tower/Vault locks.
- Provide real read/list/validate/event routes.

Important truth:
- GP055 creates a real durable decision record.
- GP055 does not recommend a provider.
- GP055 does not select a provider.
- GP055 does not configure a provider.
- GP055 does not enable provider read/write.
- GP055 does not accept/waive risk or approve mitigation.
- GP055 does not unlock object bodies, raw storage, upload, export, or execution.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Dict, List, Optional

from vault.storage_provider_comparison_board_service import get_storage_provider_comparison_board_payload


PACK_ID = "VAULT_GP055"
PACK_NAME = "Real Storage Provider Decision Record"
SCHEMA_VERSION = "vault.real_storage_provider_decision_record.v1"

SECTION_ID = "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
SECTION_TITLE = "Archive Vault — Storage Provider Prep Layer"
SECTION_RANGE = "GP051-GP060"

NEXT_PACK = "VAULT_GP056_REAL_STORAGE_PROVIDER_SELECTION_REGISTRY"
NEXT_PACK_TITLE = "Real Storage Provider Selection Registry"

DEFAULT_DECISION_RECORD_ID = "VSPDR-GP055-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_DECISION_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_decisions.sqlite"


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


def ensure_decision_store_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)
    with _connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_decision_records (
                record_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                decision_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                source_pack_id TEXT NOT NULL,
                source_record_json TEXT NOT NULL,
                decision_data_json TEXT NOT NULL,
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
            CREATE TABLE IF NOT EXISTS vault_storage_provider_decision_events (
                event_id TEXT PRIMARY KEY,
                record_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(record_id)
                    REFERENCES vault_storage_provider_decision_records(record_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_storage_provider_decision_events_record
            ON vault_storage_provider_decision_events(record_id, created_at)
            """
        )
        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "tables": [
            "vault_storage_provider_decision_records",
            "vault_storage_provider_decision_events",
        ],
        "real_sqlite_backed": True,
    }


def initialize_real_storage_provider_decision_store(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_decision_store_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            """
            SELECT record_id
            FROM vault_storage_provider_decision_records
            WHERE record_id = ?
            """,
            (DEFAULT_DECISION_RECORD_ID,),
        ).fetchone()

        if existing is None:
            gp054 = get_storage_provider_comparison_board_payload()
            decision_data = _build_decision_record_data(gp054)
            now = _now_iso()

            conn.execute(
                """
                INSERT INTO vault_storage_provider_decision_records (
                    record_id,
                    pack_id,
                    section_id,
                    section_range,
                    decision_status,
                    tower_authority_status,
                    source_pack_id,
                    source_record_json,
                    decision_data_json,
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
                    DEFAULT_DECISION_RECORD_ID,
                    PACK_ID,
                    SECTION_ID,
                    SECTION_RANGE,
                    "REAL_DECISION_RECORD_OPEN_TOWER_LOCKED",
                    "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    "VAULT_GP054",
                    _json_dumps(_compact_gp054_source_snapshot(gp054)),
                    _json_dumps(decision_data),
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

            _insert_event(
                conn,
                DEFAULT_DECISION_RECORD_ID,
                "REAL_DECISION_RECORD_CREATED",
                {
                    "pack_id": PACK_ID,
                    "source_pack_id": "VAULT_GP054",
                    "real_sqlite_backed": True,
                    "decision_status": "REAL_DECISION_RECORD_OPEN_TOWER_LOCKED",
                    "provider_selected": False,
                    "provider_recommended": False,
                    "provider_configured": False,
                    "provider_read_enabled": False,
                    "provider_write_enabled": False,
                },
            )
            _insert_event(
                conn,
                DEFAULT_DECISION_RECORD_ID,
                "SOURCE_GP054_COMPARISON_ATTACHED",
                _compact_gp054_source_snapshot(gp054),
            )
            _insert_event(
                conn,
                DEFAULT_DECISION_RECORD_ID,
                "TOWER_LOCKS_CONFIRMED",
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
        "record_id": DEFAULT_DECISION_RECORD_ID,
        "record_count": counts["record_count"],
        "event_count": counts["event_count"],
        "real_sqlite_backed": True,
    }


def _insert_event(
    conn: sqlite3.Connection,
    record_id: str,
    event_type: str,
    event_payload: Dict[str, Any],
) -> str:
    event_id = f"VSPDE-{uuid.uuid4().hex[:16].upper()}"
    conn.execute(
        """
        INSERT INTO vault_storage_provider_decision_events (
            event_id,
            record_id,
            event_type,
            event_payload_json,
            created_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            event_id,
            record_id,
            event_type,
            _json_dumps(event_payload),
            _now_iso(),
        ),
    )
    return event_id


def _get_counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        record_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_decision_records"
        ).fetchone()["c"]
        event_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_decision_events"
        ).fetchone()["c"]
    return {
        "record_count": int(record_count),
        "event_count": int(event_count),
    }


def _compact_gp054_source_snapshot(gp054: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source_pack_id": gp054["pack"]["id"],
        "source_pack_name": gp054["pack"]["name"],
        "source_section": gp054["pack"]["section"],
        "source_section_range": gp054["pack"]["section_range"],
        "gp054_ready": gp054["gp054_status"]["ready"],
        "safe_to_continue_to_gp055": gp054["gp054_status"]["safe_to_continue_to_gp055"],
        "vault_done": gp054["gp054_status"]["vault_done"],
        "provider_candidate_count": gp054["comparison_counts"]["provider_candidate_count"],
        "comparison_row_count": gp054["comparison_counts"]["comparison_row_count"],
        "ranking_placeholder_count": gp054["comparison_counts"]["ranking_placeholder_count"],
        "recommendation_blocker_count": gp054["comparison_counts"]["recommendation_blocker_count"],
        "provider_recommended_count": gp054["comparison_counts"]["provider_recommended_count"],
        "provider_selected_count": gp054["comparison_counts"]["provider_selected_count"],
        "provider_configured_count": gp054["comparison_counts"]["provider_configured_count"],
        "provider_read_enabled_count": gp054["comparison_counts"]["provider_read_enabled_count"],
        "provider_write_enabled_count": gp054["comparison_counts"]["provider_write_enabled_count"],
        "risk_accepted_count": gp054["comparison_counts"]["risk_accepted_count"],
        "risk_waived_count": gp054["comparison_counts"]["risk_waived_count"],
        "mitigation_approved_count": gp054["comparison_counts"]["mitigation_approved_count"],
        "object_body_view_enabled_count": gp054["comparison_counts"]["object_body_view_enabled_count"],
        "execution_allowed_count": gp054["comparison_counts"]["execution_allowed_count"],
        "vault_done_count": gp054["comparison_counts"]["vault_done_count"],
    }


def _build_decision_record_data(gp054: Dict[str, Any]) -> Dict[str, Any]:
    rows = gp054["comparison_rows"]["comparison_row_items"]
    candidates = []

    for row in rows:
        candidates.append(
            {
                "provider_candidate_id": row["provider_candidate_id"],
                "candidate_type": row["candidate_type"],
                "comparison_row_id": row["comparison_row_id"],
                "decision_state": "REAL_CANDIDATE_RECORDED_NOT_RECOMMENDED_NOT_SELECTED",
                "criteria_card_count": row["criteria_card_count"],
                "risk_card_count": row["risk_card_count"],
                "comparison_factor_count": row["comparison_factor_count"],
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
                "safe_to_continue_to_gp056": True,
            }
        )

    return {
        "record_schema_version": SCHEMA_VERSION,
        "record_type": "REAL_STORAGE_PROVIDER_DECISION_RECORD",
        "record_status": "REAL_DECISION_RECORD_OPEN_TOWER_LOCKED",
        "real_durable_record": True,
        "metadata_source": "VAULT_GP054_COMPARISON_BOARD",
        "provider_candidate_count": len(candidates),
        "candidate_records": candidates,
        "decision_summary": {
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
        "safe_to_continue_to_gp056": True,
    }


def _row_to_decision_record(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "record_id": row["record_id"],
        "pack_id": row["pack_id"],
        "section_id": row["section_id"],
        "section_range": row["section_range"],
        "decision_status": row["decision_status"],
        "tower_authority_status": row["tower_authority_status"],
        "source_pack_id": row["source_pack_id"],
        "source_record": _json_loads(row["source_record_json"]),
        "decision_data": _json_loads(row["decision_data_json"]),
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


def _row_to_decision_event(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "event_id": row["event_id"],
        "record_id": row["record_id"],
        "event_type": row["event_type"],
        "event_payload": _json_loads(row["event_payload_json"]),
        "created_at": row["created_at"],
    }


def get_storage_provider_decision_records(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_decision_store(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_decision_records
            ORDER BY created_at ASC, record_id ASC
            """
        ).fetchall()

    records = [_row_to_decision_record(row) for row in rows]
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "record_count": len(records),
        "records": records,
    }


def get_current_storage_provider_decision_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_decision_store(db_path)

    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_decision_records
            WHERE record_id = ?
            """,
            (DEFAULT_DECISION_RECORD_ID,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Real storage provider decision record was not initialized.")

    record = _row_to_decision_record(row)
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "current_record": record,
    }


def get_storage_provider_decision_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_storage_provider_decision_store(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_decision_events
            ORDER BY created_at ASC, event_id ASC
            """
        ).fetchall()

    events = [_row_to_decision_event(row) for row in rows]
    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "event_count": len(events),
        "events": events,
    }


def record_storage_provider_decision_review_event(
    event_type: str,
    event_payload: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    initialize_real_storage_provider_decision_store(db_path)
    payload = dict(event_payload or {})
    payload.update(
        {
            "write_type": "REAL_DECISION_REVIEW_EVENT",
            "provider_selected": False,
            "provider_recommended": False,
            "provider_configured": False,
            "provider_read_enabled": False,
            "provider_write_enabled": False,
            "export_enabled": False,
            "execution_enabled": False,
            "vault_done": False,
        }
    )

    with _connect(db_path) as conn:
        event_id = _insert_event(
            conn,
            DEFAULT_DECISION_RECORD_ID,
            event_type,
            payload,
        )
        conn.commit()

    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "record_id": DEFAULT_DECISION_RECORD_ID,
        "real_sqlite_backed": True,
        "provider_selected": False,
        "provider_recommended": False,
        "provider_configured": False,
        "provider_read_enabled": False,
        "provider_write_enabled": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    }


def validate_storage_provider_decision_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    current = get_current_storage_provider_decision_record(db_path)["current_record"]
    events = get_storage_provider_decision_events(db_path)["events"]

    checks = [
        {
            "code": "REAL_SQLITE_DECISION_RECORD_EXISTS",
            "passed": current["record_id"] == DEFAULT_DECISION_RECORD_ID,
        },
        {
            "code": "SOURCE_GP054_ATTACHED",
            "passed": current["source_pack_id"] == "VAULT_GP054",
        },
        {
            "code": "NO_PROVIDER_RECOMMENDED",
            "passed": current["recommended_provider_id"] is None,
        },
        {
            "code": "NO_PROVIDER_SELECTED",
            "passed": current["selected_provider_id"] is None,
        },
        {
            "code": "NO_PROVIDER_CONFIGURED",
            "passed": current["provider_configured"] is False,
        },
        {
            "code": "NO_PROVIDER_READ_ENABLED",
            "passed": current["provider_read_enabled"] is False,
        },
        {
            "code": "NO_PROVIDER_WRITE_ENABLED",
            "passed": current["provider_write_enabled"] is False,
        },
        {
            "code": "NO_PROVIDER_OBJECT_READ_CLAIMED",
            "passed": current["provider_object_read_claimed"] is False,
        },
        {
            "code": "NO_PROVIDER_CONNECTION_TESTED",
            "passed": current["provider_connection_tested"] is False,
        },
        {
            "code": "NO_RISK_ACCEPTED",
            "passed": current["risk_accepted"] is False,
        },
        {
            "code": "NO_RISK_WAIVED",
            "passed": current["risk_waived"] is False,
        },
        {
            "code": "NO_MITIGATION_APPROVED",
            "passed": current["mitigation_approved"] is False,
        },
        {
            "code": "NO_OBJECT_BODY_VIEW",
            "passed": current["object_body_view_enabled"] is False,
        },
        {
            "code": "NO_DIRECT_UPLOAD",
            "passed": current["direct_upload_enabled"] is False,
        },
        {
            "code": "NO_EXPORT",
            "passed": current["export_enabled"] is False,
        },
        {
            "code": "NO_EXECUTION",
            "passed": current["execution_enabled"] is False,
        },
        {
            "code": "VAULT_NOT_DONE",
            "passed": current["vault_done"] is False,
        },
        {
            "code": "EVENT_LOG_EXISTS",
            "passed": len(events) >= 3,
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
        "safe_to_continue_to_gp056": len(failed) == 0,
    }


def get_storage_provider_decision_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp056": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "Continue under ARCHIVE VAULT — STORAGE PROVIDER PREP LAYER / GP051-GP060. Keep Vault real and durable. Do not switch to Clouds unless Solice explicitly asks.",
            "carry_forward_rules": [
                "Keep real SQLite decision records.",
                "Keep real decision events.",
                "Build the real provider selection registry next.",
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


def get_real_storage_provider_decision_record_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_storage_provider_decision_store(db_path)
    current = get_current_storage_provider_decision_record(db_path)["current_record"]
    events = get_storage_provider_decision_events(db_path)
    validation = validate_storage_provider_decision_record(db_path)

    return {
        "pack": _pack_payload(),
        "decision_truth": _decision_truth(current, events["event_count"], validation),
        "store": init,
        "current_record": current,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_decision_next_step()["next_step"],
    }


def get_gp055_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_storage_provider_decision_record_home(db_path)
    current = home["current_record"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp055_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_storage_provider_decision_record_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_record_count": home["store"]["record_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp054_attached": True,
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp056": validation["safe_to_continue_to_gp056"],
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "provider_recommended": current["recommended_provider_id"] is not None,
            "provider_selected": current["selected_provider_id"] is not None,
            "provider_configured": current["provider_configured"],
            "provider_write_enabled": current["provider_write_enabled"],
            "provider_read_enabled": current["provider_read_enabled"],
            "provider_object_read_claimed": current["provider_object_read_claimed"],
            "provider_connection_tested": current["provider_connection_tested"],
            "risk_accepted": current["risk_accepted"],
            "risk_waived": current["risk_waived"],
            "mitigation_approved": current["mitigation_approved"],
            "object_body_view_enabled": current["object_body_view_enabled"],
            "direct_upload_enabled": current["direct_upload_enabled"],
            "export_enabled": current["export_enabled"],
            "execution_enabled": current["execution_enabled"],
            "clouds_status": "parked_do_not_continue_from_vault_gp055",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "decision_truth": home["decision_truth"],
        "routes": home["routes"],
        "current_record": current,
        "validation": validation,
        "next_step": home["next_step"],
    }


def _pack_payload() -> Dict[str, Any]:
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP054"],
        "foundation_status": "safe_to_continue_not_done",
        "product_depth_layer": "real_storage_provider_decision_record",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }


def _routes_payload() -> Dict[str, str]:
    return {
        "room_title": "Vault Real Storage Provider Decision Record",
        "section_header": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "route": "/vault/real-storage-provider-decision-record",
        "json_route": "/vault/real-storage-provider-decision-record.json",
        "records_route": "/vault/storage-provider-decision-records.json",
        "current_record_route": "/vault/storage-provider-current-decision-record.json",
        "events_route": "/vault/storage-provider-decision-events.json",
        "validation_route": "/vault/storage-provider-decision-validation.json",
        "next_step_route": "/vault/storage-provider-decision-next-step.json",
        "gp055_status_route": "/vault/gp055-status.json",
    }


def _decision_truth(
    current: Dict[str, Any],
    event_count: int,
    validation: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "real_storage_provider_decision_record_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "real_decision_record_exists": current["record_id"] == DEFAULT_DECISION_RECORD_ID,
        "real_event_log_exists": event_count >= 3,
        "source_gp054_attached": current["source_pack_id"] == "VAULT_GP054",
        "validation_passed": validation["valid"],
        "provider_candidate_count": current["decision_data"]["provider_candidate_count"],
        "provider_recommended": current["recommended_provider_id"] is not None,
        "provider_selected": current["selected_provider_id"] is not None,
        "provider_configured": current["provider_configured"],
        "provider_read_enabled": current["provider_read_enabled"],
        "provider_write_enabled": current["provider_write_enabled"],
        "provider_object_read_claimed": current["provider_object_read_claimed"],
        "provider_connection_tested": current["provider_connection_tested"],
        "risk_accepted": current["risk_accepted"],
        "risk_waived": current["risk_waived"],
        "mitigation_approved": current["mitigation_approved"],
        "object_body_view_enabled": current["object_body_view_enabled"],
        "direct_upload_enabled": current["direct_upload_enabled"],
        "export_enabled": current["export_enabled"],
        "execution_enabled": current["execution_enabled"],
        "vault_done": current["vault_done"],
        "safe_to_continue_to_gp056": validation["safe_to_continue_to_gp056"],
    }


def render_real_storage_provider_decision_record_page() -> str:
    home = get_real_storage_provider_decision_record_home()
    current = home["current_record"]
    truth = home["decision_truth"]
    routes = home["routes"]
    next_step = home["next_step"]

    candidate_cards = "\n".join(
        _render_candidate_card(item)
        for item in current["decision_data"]["candidate_records"]
    )
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
  <title>Vault Real Storage Provider Decision Record · GP055</title>
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
      <div class="eyebrow">Archive Vault · Giant Pack 055</div>
      <div class="eyebrow">Storage Provider Prep Layer · GP051-GP060</div>
      <h1>Real Storage Provider Decision Record</h1>
      <p>
        GP055 creates a real SQLite-backed decision record and decision event log.
        The record is durable, sourced from GP054, and validated against Tower/Vault locks.
      </p>
      <div class="metrics">
        <div class="metric"><strong>{home['store']['record_count']}</strong><span>real decision records</span></div>
        <div class="metric"><strong>{home['store']['event_count']}</strong><span>real decision events</span></div>
        <div class="metric"><strong>{truth['provider_candidate_count']}</strong><span>provider candidates recorded</span></div>
        <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
      </div>
      <div class="chips">
        <span class="pill ok">Real SQLite-backed</span>
        <span class="pill ok">Real decision record</span>
        <span class="pill ok">Real event log</span>
        <span class="pill danger">No provider selected</span>
        <span class="pill danger">No export</span>
        <span class="pill danger">No execution</span>
      </div>
    </section>

    <section class="section">
      <h2>Recorded Provider Candidates</h2>
      <p>These are real decision-record candidate entries. They are not recommendations or selections.</p>
      <div class="grid">{candidate_cards}</div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Validation Checks</h2>
        <p>GP055 validates the real decision record against active Vault/Tower locks.</p>
        {checks}
      </div>
      <div>
        <h2>Carry Forward to GP056</h2>
        <p>{escape(next_step['owner_notebook_note'])}</p>
        <ul>{rules}</ul>
      </div>
    </section>

    <section class="section">
      <h2>GP055 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['records_route'])}</code>
        <code>{escape(routes['current_record_route'])}</code>
        <code>{escape(routes['events_route'])}</code>
        <code>{escape(routes['validation_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp055_status_route'])}</code>
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
          Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
          State: <code>{escape(item['decision_state'])}</code><br>
          Recommended: <code>{str(item['provider_recommended']).lower()}</code><br>
          Selected: <code>{str(item['provider_selected']).lower()}</code><br>
          Read/write: <code>{str(item['provider_read_enabled']).lower()} / {str(item['provider_write_enabled']).lower()}</code>
        </div>
      </article>
    """
