# OB_GIANT_PACK_038_REAL_MANUAL_LIVE_DRY_RUN_RECEIPT_PACKET_ENGINE_SERVICE
"""
Real receipt packet generation for OB Manual Live dry-run records.

This module creates durable receipt packets from real dry-run records and
review events. It writes:
- a SQLite receipt packet row
- a durable JSON receipt packet file
- a SHA-256 receipt hash

It does not submit broker orders, read broker accounts, move capital, call bank
APIs, upload directly to Vault, or unlock Real Manual Live.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from web import ob_manual_live_dry_run_persistence as persistence
from web import ob_manual_live_dry_run_history as history


RECEIPT_VERSION = "OB_GIANT_PACK_038_REAL_MANUAL_LIVE_DRY_RUN_RECEIPT_PACKET_ENGINE"
RECEIPT_SCHEMA_VERSION = 1
DEFAULT_RECEIPT_DIR_RELATIVE = Path("data") / "ob_manual_live_receipt_packets"

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


def receipt_dir() -> Path:
    override = os.environ.get("OB_DRY_RUN_RECEIPT_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return repo_root() / DEFAULT_RECEIPT_DIR_RELATIVE


def stable_hash(payload: Dict[str, Any]) -> str:
    safe = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(safe.encode("utf-8")).hexdigest()


def init_receipt_db(path: Optional[Path] = None) -> Dict[str, Any]:
    history.init_history_db(path)

    with persistence.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ob_manual_live_dry_run_receipt_packets (
                packet_id TEXT PRIMARY KEY,
                record_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                packet_type TEXT NOT NULL,
                packet_status TEXT NOT NULL,
                receipt_label TEXT NOT NULL,

                packet_json TEXT NOT NULL,
                packet_hash TEXT NOT NULL,
                packet_file_path TEXT NOT NULL,

                real_broker_order_submitted INTEGER NOT NULL DEFAULT 0,
                broker_api_used INTEGER NOT NULL DEFAULT 0,
                broker_account_read INTEGER NOT NULL DEFAULT 0,
                bank_account_read INTEGER NOT NULL DEFAULT 0,
                real_capital_moved INTEGER NOT NULL DEFAULT 0,
                direct_vault_upload INTEGER NOT NULL DEFAULT 0,
                real_manual_live_ready_claim INTEGER NOT NULL DEFAULT 0,

                service_version TEXT NOT NULL,

                FOREIGN KEY(record_id) REFERENCES ob_manual_live_dry_run_records(record_id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_dry_run_receipt_record_created ON ob_manual_live_dry_run_receipt_packets(record_id, created_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_dry_run_receipt_status_created ON ob_manual_live_dry_run_receipt_packets(packet_status, created_at DESC)"
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
            ("ob_manual_live_dry_run_receipt_packets", RECEIPT_SCHEMA_VERSION, RECEIPT_VERSION, now, now),
        )
        conn.commit()

    receipt_dir().mkdir(parents=True, exist_ok=True)

    return {
        "ok": True,
        "schema_name": "ob_manual_live_dry_run_receipt_packets",
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "service_version": RECEIPT_VERSION,
        "real_receipt_packet_persistence": True,
        "real_receipt_json_file_write": True,
        "real_receipt_packet_hash": True,
        "receipt_dir": str(receipt_dir()),
        "db_path": str(path or persistence.db_path()),
    }


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
        "upload_to_vault",
    ]
    violations = [field for field in forbidden_truthy_fields if bool(payload.get(field))]
    if violations:
        raise ValueError("Dry-run receipt packet cannot carry live-action flags: " + ", ".join(violations))


def _clean_string(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def receipt_boundaries() -> Dict[str, Any]:
    return {
        "manual_live_dry_run_receipt_packet_only": True,
        "real_sqlite_persistence": True,
        "real_durable_dry_run_records": True,
        "real_review_event_persistence": True,
        "real_receipt_packet_persistence": True,
        "real_receipt_json_file_write": True,
        "real_receipt_packet_hash": True,
        "real_receipt_packet_create_endpoint": True,
        "real_receipt_packet_list_endpoint": True,
        "real_receipt_packet_read_endpoint": True,
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


def packet_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "packet_id": row["packet_id"],
        "record_id": row["record_id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "packet_type": row["packet_type"],
        "packet_status": row["packet_status"],
        "receipt_label": row["receipt_label"],
        "packet": json.loads(row["packet_json"] or "{}"),
        "packet_hash": row["packet_hash"],
        "packet_file_path": row["packet_file_path"],
        "locks": {
            "real_broker_order_submitted": bool(row["real_broker_order_submitted"]),
            "broker_api_used": bool(row["broker_api_used"]),
            "broker_account_read": bool(row["broker_account_read"]),
            "bank_account_read": bool(row["bank_account_read"]),
            "real_capital_moved": bool(row["real_capital_moved"]),
            "direct_vault_upload": bool(row["direct_vault_upload"]),
            "real_manual_live_ready_claim": bool(row["real_manual_live_ready_claim"]),
        },
        "service_version": row["service_version"],
    }


def build_receipt_packet_payload(
    record_id: str,
    packet_type: str = "manual_live_dry_run_receipt",
    packet_status: str = "finalized_dry_run_receipt",
    path: Optional[Path] = None,
) -> Dict[str, Any]:
    detail = history.build_record_detail(record_id, path)
    if not detail.get("ok"):
        raise KeyError(f"Dry-run record not found: {record_id}")

    record = detail["record"]
    events = detail.get("events", [])
    timeline = detail.get("timeline", [])
    created_at = utc_now_iso()

    packet = {
        "version": RECEIPT_VERSION,
        "packet_type": packet_type,
        "packet_status": packet_status,
        "created_at": created_at,
        "receipt_label": f"OB dry-run receipt · {record['symbol']} · {record['dry_run_outcome']}",
        "record": record,
        "review_events": events,
        "timeline": timeline,
        "summary": {
            "record_id": record["record_id"],
            "symbol": record["symbol"],
            "lane": record["lane"],
            "dry_run_outcome": record["dry_run_outcome"],
            "review_event_count": len(events),
            "timeline_event_count": len(timeline),
            "payload_hash": record["payload_hash"],
        },
        "boundaries": receipt_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }

    packet["packet_hash"] = stable_hash(packet)
    return packet


def create_receipt_packet(record_id: str, payload: Optional[Dict[str, Any]] = None, path: Optional[Path] = None) -> Dict[str, Any]:
    payload = payload or {}
    validate_no_live_action_flags(payload)
    init_receipt_db(path)

    packet_type = _clean_string(payload.get("packet_type"), "manual_live_dry_run_receipt")
    packet_status = _clean_string(payload.get("packet_status"), "finalized_dry_run_receipt")

    packet = build_receipt_packet_payload(
        record_id=record_id,
        packet_type=packet_type,
        packet_status=packet_status,
        path=path,
    )

    packet_id = _clean_string(payload.get("packet_id"), f"obrec_{uuid.uuid4().hex}")
    now = utc_now_iso()

    packet["packet_id"] = packet_id
    packet["packet_hash"] = stable_hash(packet)

    target_dir = receipt_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    packet_file = target_dir / f"{packet_id}.json"
    packet_file.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")

    file_hash = hashlib.sha256(packet_file.read_bytes()).hexdigest()
    if file_hash != packet["packet_hash"]:
        # Re-read/write with packet hash anchored in file content can differ if hash was included.
        # Anchor final file hash as explicit file hash without changing packet_hash.
        packet["packet_file_hash"] = file_hash
        packet_file.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")

    with persistence.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO ob_manual_live_dry_run_receipt_packets (
                packet_id, record_id, created_at, updated_at,
                packet_type, packet_status, receipt_label,
                packet_json, packet_hash, packet_file_path,
                real_broker_order_submitted, broker_api_used, broker_account_read, bank_account_read,
                real_capital_moved, direct_vault_upload, real_manual_live_ready_claim,
                service_version
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0, 0, 0, ?)
            """,
            (
                packet_id,
                record_id,
                now,
                now,
                packet_type,
                packet_status,
                packet["receipt_label"],
                json.dumps(packet, sort_keys=True),
                packet["packet_hash"],
                str(packet_file),
                RECEIPT_VERSION,
            ),
        )
        conn.commit()

    created = get_receipt_packet(packet_id, path)
    if not created:
        raise RuntimeError("Receipt packet was not found after insert.")

    return {
        "ok": True,
        "created": True,
        "real_receipt_packet_persistence": True,
        "real_receipt_json_file_write": True,
        "real_receipt_packet_hash": True,
        "packet": created,
        "boundaries": receipt_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


def get_receipt_packet(packet_id: str, path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    init_receipt_db(path)
    with persistence.connect(path) as conn:
        row = conn.execute(
            "SELECT * FROM ob_manual_live_dry_run_receipt_packets WHERE packet_id = ?",
            (packet_id,),
        ).fetchone()
    return packet_row_to_dict(row) if row else None


def list_receipt_packets(
    record_id: Optional[str] = None,
    packet_status: Optional[str] = None,
    limit: int = 50,
    path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    init_receipt_db(path)
    limit = max(1, min(int(limit or 50), 200))

    clauses = []
    params: List[Any] = []

    if record_id:
        clauses.append("record_id = ?")
        params.append(record_id)
    if packet_status:
        clauses.append("packet_status = ?")
        params.append(packet_status)

    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    sql = f"""
        SELECT *
        FROM ob_manual_live_dry_run_receipt_packets
        {where}
        ORDER BY created_at DESC
        LIMIT ?
    """
    params.append(limit)

    with persistence.connect(path) as conn:
        rows = conn.execute(sql, params).fetchall()

    return [packet_row_to_dict(row) for row in rows]


def receipt_overview(limit: int = 50, path: Optional[Path] = None) -> Dict[str, Any]:
    init_receipt_db(path)

    packets = list_receipt_packets(limit=limit, path=path)

    status_counts: Dict[str, int] = {}
    symbol_counts: Dict[str, int] = {}

    for packet in packets:
        status_counts[packet["packet_status"]] = status_counts.get(packet["packet_status"], 0) + 1
        symbol = packet.get("packet", {}).get("summary", {}).get("symbol", "UNKNOWN")
        symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

    return {
        "ok": True,
        "version": RECEIPT_VERSION,
        "packets": packets,
        "packet_count": len(packets),
        "status_counts": status_counts,
        "symbol_counts": symbol_counts,
        "receipt_dir": str(receipt_dir()),
        "real_receipt_packet_persistence": True,
        "real_receipt_json_file_write": True,
        "real_receipt_packet_hash": True,
        "boundaries": receipt_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


def receipt_status(path: Optional[Path] = None) -> Dict[str, Any]:
    init_receipt_db(path)

    overview = receipt_overview(limit=10, path=path)

    return {
        "ok": True,
        "version": RECEIPT_VERSION,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "real_receipt_packet_persistence": True,
        "real_receipt_json_file_write": True,
        "real_receipt_packet_hash": True,
        "packet_count": overview["packet_count"],
        "receipt_dir": str(receipt_dir()),
        "db_path": str(path or persistence.db_path()),
        "boundaries": receipt_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


__all__ = [
    "RECEIPT_VERSION",
    "RECEIPT_SCHEMA_VERSION",
    "init_receipt_db",
    "receipt_status",
    "build_receipt_packet_payload",
    "create_receipt_packet",
    "get_receipt_packet",
    "list_receipt_packets",
    "receipt_overview",
    "receipt_boundaries",
]
