# OB_GIANT_PACK_037_REAL_MANUAL_LIVE_DRY_RUN_RECORD_DETAIL_HISTORY_REVIEW_SERVICE
"""
Real detail/history review for OB Manual Live dry-run records.

This module persists review events tied to real dry-run records created by GP036.
It creates a durable SQLite review-event table and exposes history/detail helpers.

It does not submit broker orders, read broker accounts, move capital, call bank APIs,
upload directly to Vault, or unlock Real Manual Live.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from web import ob_manual_live_dry_run_persistence as persistence


HISTORY_VERSION = "OB_GIANT_PACK_037_REAL_MANUAL_LIVE_DRY_RUN_RECORD_DETAIL_HISTORY_REVIEW"
HISTORY_SCHEMA_VERSION = 1

ALLOWED_EVENT_TYPES = {
    "owner_review",
    "confidence_note",
    "risk_note",
    "scenario_review",
    "checklist_review",
    "status_change",
}

ALLOWED_REVIEW_STATUSES = {
    "reviewed",
    "needs_reps",
    "clean",
    "blocked_live",
    "locked",
    "watch",
}

LOCKED_ACTIONS = [
    "submit_real_broker_order",
    "read_broker_account",
    "auto_execute_trade",
    "read_bank_account",
    "move_real_capital",
    "upload_direct_to_vault",
    "mark_real_manual_live_ready",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_hash(payload: Dict[str, Any]) -> str:
    safe = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(safe.encode("utf-8")).hexdigest()


def init_history_db(path: Optional[Path] = None) -> Dict[str, Any]:
    persistence.init_db(path)
    with persistence.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ob_manual_live_dry_run_review_events (
                event_id TEXT PRIMARY KEY,
                record_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                reviewer_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                review_status TEXT NOT NULL,
                review_notes TEXT NOT NULL,

                confidence_delta INTEGER NOT NULL DEFAULT 0,
                checklist_delta INTEGER NOT NULL DEFAULT 0,
                scenario_delta INTEGER NOT NULL DEFAULT 0,

                real_broker_order_submitted INTEGER NOT NULL DEFAULT 0,
                broker_api_used INTEGER NOT NULL DEFAULT 0,
                broker_account_read INTEGER NOT NULL DEFAULT 0,
                bank_account_read INTEGER NOT NULL DEFAULT 0,
                real_capital_moved INTEGER NOT NULL DEFAULT 0,
                direct_vault_upload INTEGER NOT NULL DEFAULT 0,
                real_manual_live_ready_claim INTEGER NOT NULL DEFAULT 0,

                event_hash TEXT NOT NULL,
                service_version TEXT NOT NULL,

                FOREIGN KEY(record_id) REFERENCES ob_manual_live_dry_run_records(record_id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_dry_run_review_record_created ON ob_manual_live_dry_run_review_events(record_id, created_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_dry_run_review_status ON ob_manual_live_dry_run_review_events(review_status, created_at DESC)"
        )

        now = utc_now_iso()
        conn.execute(
            """
            INSERT INTO ob_schema_state(schema_name, schema_version, service_version, created_at, updated_at)
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(schema_name) DO UPDATE SET
                schema_version=excluded.schema_version,
                service_version=excluded.service_version,
                updated_at=excluded.updated_at
            """,
            ("ob_manual_live_dry_run_review_events", HISTORY_SCHEMA_VERSION, HISTORY_VERSION, now, now),
        )
        conn.commit()

    return {
        "ok": True,
        "schema_name": "ob_manual_live_dry_run_review_events",
        "schema_version": HISTORY_SCHEMA_VERSION,
        "service_version": HISTORY_VERSION,
        "real_review_event_persistence": True,
        "real_record_detail_enabled": True,
        "real_history_enabled": True,
        "db_path": str(path or persistence.db_path()),
    }


def _clean_string(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _clean_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return fallback


def validate_no_live_action_flags(payload: Dict[str, Any]) -> None:
    forbidden_truthy_fields = [
        "real_broker_order_submitted",
        "broker_api_used",
        "broker_account_read",
        "bank_account_read",
        "real_capital_moved",
        "direct_vault_upload",
        "real_manual_live_ready_claim",
        "submit_order",
        "auto_execute",
        "move_capital",
        "mark_real_manual_live_ready",
    ]
    violations = [field for field in forbidden_truthy_fields if bool(payload.get(field))]
    if violations:
        raise ValueError("Dry-run review cannot carry live-action flags: " + ", ".join(violations))


def normalize_event_input(record_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    event_type = _clean_string(payload.get("event_type"), "owner_review")
    if event_type not in ALLOWED_EVENT_TYPES:
        event_type = "owner_review"

    review_status = _clean_string(payload.get("review_status"), "reviewed")
    if review_status not in ALLOWED_REVIEW_STATUSES:
        review_status = "reviewed"

    confidence_delta = max(-100, min(100, _clean_int(payload.get("confidence_delta"), 0)))
    checklist_delta = max(-100, min(100, _clean_int(payload.get("checklist_delta"), 0)))
    scenario_delta = max(-100, min(100, _clean_int(payload.get("scenario_delta"), 0)))

    return {
        "record_id": _clean_string(record_id),
        "reviewer_id": _clean_string(payload.get("reviewer_id"), "owner_solice"),
        "event_type": event_type,
        "review_status": review_status,
        "review_notes": _clean_string(payload.get("review_notes"), "Owner reviewed dry-run record."),
        "confidence_delta": confidence_delta,
        "checklist_delta": checklist_delta,
        "scenario_delta": scenario_delta,
    }


def event_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "event_id": row["event_id"],
        "record_id": row["record_id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "reviewer_id": row["reviewer_id"],
        "event_type": row["event_type"],
        "review_status": row["review_status"],
        "review_notes": row["review_notes"],
        "confidence_delta": row["confidence_delta"],
        "checklist_delta": row["checklist_delta"],
        "scenario_delta": row["scenario_delta"],
        "locks": {
            "real_broker_order_submitted": bool(row["real_broker_order_submitted"]),
            "broker_api_used": bool(row["broker_api_used"]),
            "broker_account_read": bool(row["broker_account_read"]),
            "bank_account_read": bool(row["bank_account_read"]),
            "real_capital_moved": bool(row["real_capital_moved"]),
            "direct_vault_upload": bool(row["direct_vault_upload"]),
            "real_manual_live_ready_claim": bool(row["real_manual_live_ready_claim"]),
        },
        "event_hash": row["event_hash"],
        "service_version": row["service_version"],
    }


def create_review_event(record_id: str, payload: Dict[str, Any], path: Optional[Path] = None) -> Dict[str, Any]:
    init_history_db(path)
    validate_no_live_action_flags(payload)

    record = persistence.get_dry_run_record(record_id, path)
    if not record:
        raise KeyError(f"Dry-run record not found: {record_id}")

    normalized = normalize_event_input(record_id, payload)
    now = utc_now_iso()
    event_id = _clean_string(payload.get("event_id"), f"obrev_{uuid.uuid4().hex}")

    hash_payload = {
        "event_id": event_id,
        "created_at": now,
        **normalized,
        "real_broker_order_submitted": False,
        "broker_api_used": False,
        "broker_account_read": False,
        "bank_account_read": False,
        "real_capital_moved": False,
        "direct_vault_upload": False,
        "real_manual_live_ready_claim": False,
    }
    event_hash = stable_hash(hash_payload)

    with persistence.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO ob_manual_live_dry_run_review_events (
                event_id, record_id, created_at, updated_at,
                reviewer_id, event_type, review_status, review_notes,
                confidence_delta, checklist_delta, scenario_delta,
                real_broker_order_submitted, broker_api_used, broker_account_read, bank_account_read,
                real_capital_moved, direct_vault_upload, real_manual_live_ready_claim,
                event_hash, service_version
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0, 0, 0, ?, ?)
            """,
            (
                event_id,
                normalized["record_id"],
                now,
                now,
                normalized["reviewer_id"],
                normalized["event_type"],
                normalized["review_status"],
                normalized["review_notes"],
                normalized["confidence_delta"],
                normalized["checklist_delta"],
                normalized["scenario_delta"],
                event_hash,
                HISTORY_VERSION,
            ),
        )
        conn.commit()

    event = get_review_event(event_id, path)
    if not event:
        raise RuntimeError("Review event was not found after insert.")

    return {
        "ok": True,
        "created": True,
        "real_review_event_persistence": True,
        "event": event,
        "record": record,
        "boundaries": history_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


def get_review_event(event_id: str, path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    init_history_db(path)
    with persistence.connect(path) as conn:
        row = conn.execute(
            "SELECT * FROM ob_manual_live_dry_run_review_events WHERE event_id = ?",
            (event_id,),
        ).fetchone()
    return event_to_dict(row) if row else None


def list_review_events(
    record_id: Optional[str] = None,
    review_status: Optional[str] = None,
    limit: int = 50,
    path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    init_history_db(path)
    limit = max(1, min(int(limit or 50), 200))

    clauses = []
    params: List[Any] = []

    if record_id:
        clauses.append("record_id = ?")
        params.append(record_id)
    if review_status:
        clauses.append("review_status = ?")
        params.append(review_status)

    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    sql = f"""
        SELECT *
        FROM ob_manual_live_dry_run_review_events
        {where}
        ORDER BY created_at DESC
        LIMIT ?
    """
    params.append(limit)

    with persistence.connect(path) as conn:
        rows = conn.execute(sql, params).fetchall()

    return [event_to_dict(row) for row in rows]


def build_record_timeline(record: Dict[str, Any], events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    timeline = [
        {
            "timeline_id": f"{record['record_id']}_created",
            "record_id": record["record_id"],
            "created_at": record["created_at"],
            "type": "record_created",
            "label": "Dry-run record created",
            "notes": f"{record['symbol']} · {record['dry_run_outcome']} · {record['lane']}",
            "hash": record.get("payload_hash"),
            "status": "persisted",
        }
    ]

    for event in events:
        timeline.append(
            {
                "timeline_id": event["event_id"],
                "record_id": event["record_id"],
                "created_at": event["created_at"],
                "type": event["event_type"],
                "label": f"Review event: {event['review_status']}",
                "notes": event["review_notes"],
                "hash": event.get("event_hash"),
                "status": event["review_status"],
            }
        )

    return sorted(timeline, key=lambda item: item["created_at"])


def build_record_detail(record_id: str, path: Optional[Path] = None) -> Dict[str, Any]:
    init_history_db(path)

    record = persistence.get_dry_run_record(record_id, path)
    if not record:
        return {
            "ok": False,
            "error": "record_not_found",
            "record_id": record_id,
            "boundaries": history_boundaries(),
            "blocked_actions": LOCKED_ACTIONS,
        }

    events = list_review_events(record_id=record_id, limit=100, path=path)
    timeline = build_record_timeline(record, events)

    return {
        "ok": True,
        "version": HISTORY_VERSION,
        "record": record,
        "events": events,
        "timeline": timeline,
        "event_count": len(events),
        "real_record_detail_enabled": True,
        "real_history_enabled": True,
        "boundaries": history_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


def build_history_overview(
    owner_id: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 25,
    path: Optional[Path] = None,
) -> Dict[str, Any]:
    init_history_db(path)

    records = persistence.list_dry_run_records(owner_id=owner_id, symbol=symbol, limit=limit, path=path)
    events = list_review_events(limit=200, path=path)

    events_by_record: Dict[str, int] = {}
    for event in events:
        events_by_record[event["record_id"]] = events_by_record.get(event["record_id"], 0) + 1

    outcome_counts: Dict[str, int] = {}
    symbol_counts: Dict[str, int] = {}
    for record in records:
        outcome_counts[record["dry_run_outcome"]] = outcome_counts.get(record["dry_run_outcome"], 0) + 1
        symbol_counts[record["symbol"]] = symbol_counts.get(record["symbol"], 0) + 1
        record["review_event_count"] = events_by_record.get(record["record_id"], 0)

    return {
        "ok": True,
        "version": HISTORY_VERSION,
        "records": records,
        "record_count": len(records),
        "review_event_count": len(events),
        "outcome_counts": outcome_counts,
        "symbol_counts": symbol_counts,
        "real_record_detail_enabled": True,
        "real_history_enabled": True,
        "real_review_event_persistence": True,
        "boundaries": history_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


def history_status(path: Optional[Path] = None) -> Dict[str, Any]:
    init_history_db(path)

    overview = build_history_overview(limit=10, path=path)

    return {
        "ok": True,
        "version": HISTORY_VERSION,
        "history_schema_version": HISTORY_SCHEMA_VERSION,
        "real_record_detail_enabled": True,
        "real_history_enabled": True,
        "real_review_event_persistence": True,
        "record_count": overview["record_count"],
        "review_event_count": overview["review_event_count"],
        "db_path": str(path or persistence.db_path()),
        "boundaries": history_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


def history_boundaries() -> Dict[str, Any]:
    return {
        "manual_live_dry_run_history_review_only": True,
        "real_sqlite_persistence": True,
        "real_durable_dry_run_records": True,
        "real_review_event_persistence": True,
        "real_record_detail_enabled": True,
        "real_history_enabled": True,
        "real_review_event_write_enabled": True,
        "real_manual_live_ready": False,
        "manual_live_real_locked": True,
        "hybrid_locked": True,
        "automated_locked": True,
        "broker_api_used": False,
        "broker_account_read": False,
        "order_submit_enabled": False,
        "auto_execution_enabled": False,
        "bank_account_read": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
    }


__all__ = [
    "HISTORY_VERSION",
    "HISTORY_SCHEMA_VERSION",
    "init_history_db",
    "history_status",
    "create_review_event",
    "get_review_event",
    "list_review_events",
    "build_record_detail",
    "build_history_overview",
    "history_boundaries",
]
