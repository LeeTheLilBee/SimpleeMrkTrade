# OB_GIANT_PACK_036_REAL_MANUAL_LIVE_DRY_RUN_PERSISTENCE_ENGINE_SERVICE
"""
Real DB-backed dry-run persistence for OB Manual Live Level 1 rehearsals.

This module creates and writes durable SQLite records for dry-run/manual-live
practice records. It does not submit broker orders, read broker accounts,
move capital, call bank APIs, or unlock Real Manual Live.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


SERVICE_VERSION = "OB_GIANT_PACK_036_REAL_MANUAL_LIVE_DRY_RUN_PERSISTENCE_ENGINE"
DEFAULT_DB_RELATIVE_PATH = Path("data") / "ob_manual_live_dry_run.sqlite3"
SCHEMA_VERSION = 1

ALLOWED_OUTCOMES = {
    "not_placed",
    "fake_fill",
    "cancelled",
    "skipped",
    "needs_review",
}

ALLOWED_LANES = {
    "Proof/Demo",
    "Owner Review",
    "Manual Live Rehearsal",
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


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def db_path() -> Path:
    override = os.environ.get("OB_DRY_RUN_DB_PATH", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return repo_root() / DEFAULT_DB_RELATIVE_PATH


def connect(path: Optional[Path] = None) -> sqlite3.Connection:
    target = Path(path) if path else db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def stable_payload_hash(payload: Dict[str, Any]) -> str:
    safe = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(safe.encode("utf-8")).hexdigest()


def init_db(path: Optional[Path] = None) -> Dict[str, Any]:
    with connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ob_schema_state (
                schema_name TEXT PRIMARY KEY,
                schema_version INTEGER NOT NULL,
                service_version TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ob_manual_live_dry_run_records (
                record_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                owner_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                lane TEXT NOT NULL,
                symbol TEXT NOT NULL,
                instrument_type TEXT NOT NULL,
                direction TEXT NOT NULL,
                strategy TEXT NOT NULL,

                candidate_snapshot_json TEXT NOT NULL,
                checklist_snapshot_json TEXT NOT NULL,
                scenario_snapshot_json TEXT NOT NULL,
                confidence_snapshot_json TEXT NOT NULL,

                intended_action TEXT NOT NULL,
                dry_run_outcome TEXT NOT NULL,
                risk_notes TEXT NOT NULL,
                operator_notes TEXT NOT NULL,

                real_broker_order_submitted INTEGER NOT NULL DEFAULT 0,
                broker_api_used INTEGER NOT NULL DEFAULT 0,
                broker_account_read INTEGER NOT NULL DEFAULT 0,
                bank_account_read INTEGER NOT NULL DEFAULT 0,
                real_capital_moved INTEGER NOT NULL DEFAULT 0,
                direct_vault_upload INTEGER NOT NULL DEFAULT 0,
                real_manual_live_ready_claim INTEGER NOT NULL DEFAULT 0,

                payload_hash TEXT NOT NULL,
                service_version TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_dry_run_owner_created ON ob_manual_live_dry_run_records(owner_id, created_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_dry_run_symbol_created ON ob_manual_live_dry_run_records(symbol, created_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_dry_run_session ON ob_manual_live_dry_run_records(session_id)"
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
            ("ob_manual_live_dry_run_records", SCHEMA_VERSION, SERVICE_VERSION, now, now),
        )
        conn.commit()

    return {
        "ok": True,
        "schema_name": "ob_manual_live_dry_run_records",
        "schema_version": SCHEMA_VERSION,
        "service_version": SERVICE_VERSION,
        "db_path": str(path or db_path()),
        "real_sqlite_persistence": True,
    }


def _clean_string(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _clean_json_obj(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if value is None or value == "":
        return {}
    if isinstance(value, str):
        try:
            loaded = json.loads(value)
            return loaded if isinstance(loaded, dict) else {"value": loaded}
        except Exception:
            return {"raw": value}
    return {"value": value}


def normalize_record_input(payload: Dict[str, Any]) -> Dict[str, Any]:
    lane = _clean_string(payload.get("lane"), "Proof/Demo")
    if lane not in ALLOWED_LANES:
        lane = "Proof/Demo"

    dry_run_outcome = _clean_string(payload.get("dry_run_outcome"), "needs_review")
    if dry_run_outcome not in ALLOWED_OUTCOMES:
        dry_run_outcome = "needs_review"

    symbol = _clean_string(payload.get("symbol"), "UNKNOWN").upper()
    instrument_type = _clean_string(payload.get("instrument_type"), "unknown").lower()
    direction = _clean_string(payload.get("direction"), "review").lower()

    normalized = {
        "owner_id": _clean_string(payload.get("owner_id"), "owner_unknown"),
        "session_id": _clean_string(payload.get("session_id"), f"dryrun_{uuid.uuid4().hex[:12]}"),
        "lane": lane,
        "symbol": symbol,
        "instrument_type": instrument_type,
        "direction": direction,
        "strategy": _clean_string(payload.get("strategy"), "manual_live_level_1_dry_run"),
        "candidate_snapshot": _clean_json_obj(payload.get("candidate_snapshot")),
        "checklist_snapshot": _clean_json_obj(payload.get("checklist_snapshot")),
        "scenario_snapshot": _clean_json_obj(payload.get("scenario_snapshot")),
        "confidence_snapshot": _clean_json_obj(payload.get("confidence_snapshot")),
        "intended_action": _clean_string(payload.get("intended_action"), "manual_review_only"),
        "dry_run_outcome": dry_run_outcome,
        "risk_notes": _clean_string(payload.get("risk_notes"), "No real order. Dry-run record only."),
        "operator_notes": _clean_string(payload.get("operator_notes"), "Dry-run persisted for owner review."),
    }

    return normalized


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
    ]
    violations = [field for field in forbidden_truthy_fields if bool(payload.get(field))]
    if violations:
        raise ValueError("Dry-run persistence cannot carry live-action flags: " + ", ".join(violations))


def record_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "record_id": row["record_id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "owner_id": row["owner_id"],
        "session_id": row["session_id"],
        "lane": row["lane"],
        "symbol": row["symbol"],
        "instrument_type": row["instrument_type"],
        "direction": row["direction"],
        "strategy": row["strategy"],
        "candidate_snapshot": json.loads(row["candidate_snapshot_json"] or "{}"),
        "checklist_snapshot": json.loads(row["checklist_snapshot_json"] or "{}"),
        "scenario_snapshot": json.loads(row["scenario_snapshot_json"] or "{}"),
        "confidence_snapshot": json.loads(row["confidence_snapshot_json"] or "{}"),
        "intended_action": row["intended_action"],
        "dry_run_outcome": row["dry_run_outcome"],
        "risk_notes": row["risk_notes"],
        "operator_notes": row["operator_notes"],
        "locks": {
            "real_broker_order_submitted": bool(row["real_broker_order_submitted"]),
            "broker_api_used": bool(row["broker_api_used"]),
            "broker_account_read": bool(row["broker_account_read"]),
            "bank_account_read": bool(row["bank_account_read"]),
            "real_capital_moved": bool(row["real_capital_moved"]),
            "direct_vault_upload": bool(row["direct_vault_upload"]),
            "real_manual_live_ready_claim": bool(row["real_manual_live_ready_claim"]),
        },
        "payload_hash": row["payload_hash"],
        "service_version": row["service_version"],
    }


def create_dry_run_record(payload: Dict[str, Any], path: Optional[Path] = None) -> Dict[str, Any]:
    init_db(path)
    validate_no_live_action_flags(payload)
    normalized = normalize_record_input(payload)

    now = utc_now_iso()
    record_id = _clean_string(payload.get("record_id"), f"obdry_{uuid.uuid4().hex}")

    hash_payload = {
        "record_id": record_id,
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
    payload_hash = stable_payload_hash(hash_payload)

    with connect(path) as conn:
        conn.execute(
            """
            INSERT INTO ob_manual_live_dry_run_records (
                record_id, created_at, updated_at,
                owner_id, session_id, lane, symbol, instrument_type, direction, strategy,
                candidate_snapshot_json, checklist_snapshot_json, scenario_snapshot_json, confidence_snapshot_json,
                intended_action, dry_run_outcome, risk_notes, operator_notes,
                real_broker_order_submitted, broker_api_used, broker_account_read, bank_account_read,
                real_capital_moved, direct_vault_upload, real_manual_live_ready_claim,
                payload_hash, service_version
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0, 0, 0, ?, ?)
            """,
            (
                record_id,
                now,
                now,
                normalized["owner_id"],
                normalized["session_id"],
                normalized["lane"],
                normalized["symbol"],
                normalized["instrument_type"],
                normalized["direction"],
                normalized["strategy"],
                json.dumps(normalized["candidate_snapshot"], sort_keys=True),
                json.dumps(normalized["checklist_snapshot"], sort_keys=True),
                json.dumps(normalized["scenario_snapshot"], sort_keys=True),
                json.dumps(normalized["confidence_snapshot"], sort_keys=True),
                normalized["intended_action"],
                normalized["dry_run_outcome"],
                normalized["risk_notes"],
                normalized["operator_notes"],
                payload_hash,
                SERVICE_VERSION,
            ),
        )
        conn.commit()

    created = get_dry_run_record(record_id, path)
    if not created:
        raise RuntimeError("Dry-run record was not found after insert.")

    return {
        "ok": True,
        "created": True,
        "real_sqlite_persistence": True,
        "record": created,
        "blocked_actions": LOCKED_ACTIONS,
        "boundaries": real_boundaries(),
    }


def get_dry_run_record(record_id: str, path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    init_db(path)
    with connect(path) as conn:
        row = conn.execute(
            "SELECT * FROM ob_manual_live_dry_run_records WHERE record_id = ?",
            (record_id,),
        ).fetchone()
    return record_to_dict(row) if row else None


def list_dry_run_records(
    owner_id: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 25,
    path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    init_db(path)
    limit = max(1, min(int(limit or 25), 100))

    clauses = []
    params: List[Any] = []
    if owner_id:
        clauses.append("owner_id = ?")
        params.append(owner_id)
    if symbol:
        clauses.append("symbol = ?")
        params.append(symbol.upper())

    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    sql = f"""
        SELECT *
        FROM ob_manual_live_dry_run_records
        {where}
        ORDER BY created_at DESC
        LIMIT ?
    """
    params.append(limit)

    with connect(path) as conn:
        rows = conn.execute(sql, params).fetchall()

    return [record_to_dict(row) for row in rows]


def service_status(path: Optional[Path] = None) -> Dict[str, Any]:
    init_db(path)
    target = Path(path) if path else db_path()
    with connect(path) as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM ob_manual_live_dry_run_records").fetchone()["c"]
        schema = conn.execute(
            "SELECT * FROM ob_schema_state WHERE schema_name = ?",
            ("ob_manual_live_dry_run_records",),
        ).fetchone()

    return {
        "ok": True,
        "version": SERVICE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "db_path": str(target),
        "record_count": int(total),
        "schema": dict(schema) if schema else None,
        "real_sqlite_persistence": True,
        "real_durable_records": True,
        "real_create_endpoint_enabled": True,
        "real_list_endpoint_enabled": True,
        "real_read_endpoint_enabled": True,
        "blocked_actions": LOCKED_ACTIONS,
        "boundaries": real_boundaries(),
    }


def real_boundaries() -> Dict[str, Any]:
    return {
        "manual_live_dry_run_persistence_only": True,
        "real_sqlite_persistence": True,
        "real_durable_records": True,
        "real_database_write_enabled_for_dry_run_records": True,
        "real_save_endpoint_enabled_for_dry_run_records": True,
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


def build_demo_payload(owner_id: str = "owner_solice") -> Dict[str, Any]:
    return {
        "owner_id": owner_id,
        "session_id": f"demo_session_{uuid.uuid4().hex[:10]}",
        "lane": "Proof/Demo",
        "symbol": "MU",
        "instrument_type": "option",
        "direction": "call_review",
        "strategy": "manual_live_level_1_dry_run",
        "candidate_snapshot": {
            "symbol": "MU",
            "setup": "practice_candidate",
            "score_preview": 74,
            "real_market_data_used": False,
        },
        "checklist_snapshot": {
            "checklist_complete": True,
            "missing_fields": [],
            "manual_review_only": True,
        },
        "scenario_snapshot": {
            "scenario_id": "clean_candidate_scenario",
            "scenario_status": "ready",
        },
        "confidence_snapshot": {
            "operator_confidence_label": "forming",
            "real_manual_live_ready": False,
        },
        "intended_action": "manual_review_only",
        "dry_run_outcome": "not_placed",
        "risk_notes": "Practice-only dry-run. No order submitted.",
        "operator_notes": "Persisted for owner review.",
    }


__all__ = [
    "SERVICE_VERSION",
    "SCHEMA_VERSION",
    "init_db",
    "service_status",
    "create_dry_run_record",
    "get_dry_run_record",
    "list_dry_run_records",
    "build_demo_payload",
    "real_boundaries",
]
