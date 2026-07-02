# OB_GIANT_PACK_039_REAL_MANUAL_LIVE_PROOF_PACKET_OWNER_REVIEW_QUEUE_SERVICE
"""
Real owner review queue for OB Manual Live proof packets.

This module materializes queue items from real dry-run receipt packets and
provides durable owner-review queue search/filter/update support.

It does not submit broker orders, read broker accounts, move capital, call bank
APIs, upload directly to Vault, or unlock Real Manual Live.
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
from web import ob_manual_live_dry_run_history as history
from web import ob_manual_live_dry_run_receipts as receipts


QUEUE_VERSION = "OB_GIANT_PACK_039_REAL_MANUAL_LIVE_PROOF_PACKET_OWNER_REVIEW_QUEUE"
QUEUE_SCHEMA_VERSION = 1

ALLOWED_QUEUE_STATUSES = {
    "new",
    "needs_review",
    "clean",
    "blocked_live",
    "watch",
    "archived",
}

ALLOWED_PRIORITY = {
    "low",
    "normal",
    "high",
    "urgent",
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


def init_queue_db(path: Optional[Path] = None) -> Dict[str, Any]:
    receipts.init_receipt_db(path)

    with persistence.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ob_manual_live_proof_packet_review_queue (
                queue_item_id TEXT PRIMARY KEY,
                packet_id TEXT NOT NULL UNIQUE,
                record_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                owner_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                dry_run_outcome TEXT NOT NULL,
                packet_status TEXT NOT NULL,
                queue_status TEXT NOT NULL,
                priority TEXT NOT NULL,
                review_lane TEXT NOT NULL,
                review_reason TEXT NOT NULL,

                packet_hash TEXT NOT NULL,
                packet_snapshot_json TEXT NOT NULL,
                queue_hash TEXT NOT NULL,

                real_broker_order_submitted INTEGER NOT NULL DEFAULT 0,
                broker_api_used INTEGER NOT NULL DEFAULT 0,
                broker_account_read INTEGER NOT NULL DEFAULT 0,
                bank_account_read INTEGER NOT NULL DEFAULT 0,
                real_capital_moved INTEGER NOT NULL DEFAULT 0,
                direct_vault_upload INTEGER NOT NULL DEFAULT 0,
                real_manual_live_ready_claim INTEGER NOT NULL DEFAULT 0,

                service_version TEXT NOT NULL,

                FOREIGN KEY(packet_id) REFERENCES ob_manual_live_dry_run_receipt_packets(packet_id) ON DELETE CASCADE,
                FOREIGN KEY(record_id) REFERENCES ob_manual_live_dry_run_records(record_id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_proof_queue_status_updated ON ob_manual_live_proof_packet_review_queue(queue_status, updated_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_proof_queue_symbol_updated ON ob_manual_live_proof_packet_review_queue(symbol, updated_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_proof_queue_owner_updated ON ob_manual_live_proof_packet_review_queue(owner_id, updated_at DESC)"
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
            ("ob_manual_live_proof_packet_review_queue", QUEUE_SCHEMA_VERSION, QUEUE_VERSION, now, now),
        )
        conn.commit()

    return {
        "ok": True,
        "schema_name": "ob_manual_live_proof_packet_review_queue",
        "schema_version": QUEUE_SCHEMA_VERSION,
        "service_version": QUEUE_VERSION,
        "real_owner_review_queue_persistence": True,
        "real_receipt_packet_search": True,
        "real_queue_filtering": True,
        "db_path": str(path or persistence.db_path()),
    }


def _clean_string(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _default_queue_status(packet: Dict[str, Any]) -> str:
    inner = packet.get("packet") or {}
    summary = inner.get("summary") or {}
    outcome = _clean_string(summary.get("dry_run_outcome"), packet.get("packet_status", "")).lower()
    event_count = int(summary.get("review_event_count") or 0)

    if outcome in {"needs_review", "cancelled"}:
        return "needs_review"
    if outcome in {"fake_fill", "not_placed"} and event_count > 0:
        return "clean"
    if outcome in {"fake_fill", "not_placed"}:
        return "watch"
    return "needs_review"


def _default_priority(packet: Dict[str, Any]) -> str:
    inner = packet.get("packet") or {}
    summary = inner.get("summary") or {}
    outcome = _clean_string(summary.get("dry_run_outcome"), "").lower()
    event_count = int(summary.get("review_event_count") or 0)

    if outcome == "needs_review":
        return "high"
    if event_count == 0:
        return "normal"
    return "low"


def _default_review_reason(packet: Dict[str, Any]) -> str:
    inner = packet.get("packet") or {}
    summary = inner.get("summary") or {}
    symbol = summary.get("symbol") or "UNKNOWN"
    outcome = summary.get("dry_run_outcome") or "unknown"
    event_count = summary.get("review_event_count") or 0
    return f"Review proof packet for {symbol}: outcome={outcome}, review_events={event_count}."


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
        raise ValueError("Proof packet review queue cannot carry live-action flags: " + ", ".join(violations))


def queue_boundaries() -> Dict[str, Any]:
    return {
        "manual_live_proof_packet_owner_review_queue_only": True,
        "real_sqlite_persistence": True,
        "real_durable_dry_run_records": True,
        "real_review_event_persistence": True,
        "real_receipt_packet_persistence": True,
        "real_owner_review_queue_persistence": True,
        "real_receipt_packet_search": True,
        "real_queue_filtering": True,
        "real_queue_status_update": True,
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


def queue_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "queue_item_id": row["queue_item_id"],
        "packet_id": row["packet_id"],
        "record_id": row["record_id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "owner_id": row["owner_id"],
        "symbol": row["symbol"],
        "dry_run_outcome": row["dry_run_outcome"],
        "packet_status": row["packet_status"],
        "queue_status": row["queue_status"],
        "priority": row["priority"],
        "review_lane": row["review_lane"],
        "review_reason": row["review_reason"],
        "packet_hash": row["packet_hash"],
        "packet_snapshot": json.loads(row["packet_snapshot_json"] or "{}"),
        "queue_hash": row["queue_hash"],
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


def materialize_queue_item(packet_id: str, payload: Optional[Dict[str, Any]] = None, path: Optional[Path] = None) -> Dict[str, Any]:
    payload = payload or {}
    validate_no_live_action_flags(payload)
    init_queue_db(path)

    packet = receipts.get_receipt_packet(packet_id, path)
    if not packet:
        raise KeyError(f"Receipt packet not found: {packet_id}")

    inner = packet.get("packet") or {}
    summary = inner.get("summary") or {}
    record = inner.get("record") or {}

    with persistence.connect(path) as conn:
        existing = conn.execute(
            "SELECT * FROM ob_manual_live_proof_packet_review_queue WHERE packet_id = ?",
            (packet_id,),
        ).fetchone()

    existing_item = queue_row_to_dict(existing) if existing else None

    # GP039 repair:
    # Re-materialization should refresh the packet snapshot/hash from the receipt,
    # but it must not erase owner/manual queue decisions unless the caller
    # explicitly sends a new value. This keeps owner review real and durable.
    queue_status = _clean_string(
        payload.get("queue_status"),
        existing_item["queue_status"] if existing_item else _default_queue_status(packet),
    )
    if queue_status not in ALLOWED_QUEUE_STATUSES:
        queue_status = existing_item["queue_status"] if existing_item else "needs_review"

    priority = _clean_string(
        payload.get("priority"),
        existing_item["priority"] if existing_item else _default_priority(packet),
    )
    if priority not in ALLOWED_PRIORITY:
        priority = existing_item["priority"] if existing_item else "normal"

    owner_id = _clean_string(
        payload.get("owner_id"),
        existing_item["owner_id"] if existing_item else record.get("owner_id") or "owner_solice",
    )
    symbol = _clean_string(
        payload.get("symbol"),
        existing_item["symbol"] if existing_item else summary.get("symbol") or record.get("symbol") or "UNKNOWN",
    ).upper()
    dry_run_outcome = _clean_string(
        payload.get("dry_run_outcome"),
        existing_item["dry_run_outcome"] if existing_item else summary.get("dry_run_outcome") or record.get("dry_run_outcome") or "unknown",
    )
    packet_status = _clean_string(
        payload.get("packet_status"),
        packet.get("packet_status") or (existing_item["packet_status"] if existing_item else "unknown"),
    )
    review_lane = _clean_string(
        payload.get("review_lane"),
        existing_item["review_lane"] if existing_item else "Owner Proof Packet Review",
    )
    review_reason = _clean_string(
        payload.get("review_reason"),
        existing_item["review_reason"] if existing_item else _default_review_reason(packet),
    )

    now = utc_now_iso()
    queue_item_id = _clean_string(
        payload.get("queue_item_id"),
        existing_item["queue_item_id"] if existing_item else f"obq_{uuid.uuid4().hex}",
    )

    queue_hash_payload = {
        "packet_id": packet_id,
        "record_id": packet["record_id"],
        "owner_id": owner_id,
        "symbol": symbol,
        "dry_run_outcome": dry_run_outcome,
        "packet_status": packet_status,
        "queue_status": queue_status,
        "priority": priority,
        "review_lane": review_lane,
        "review_reason": review_reason,
        "packet_hash": packet["packet_hash"],
    }
    queue_hash = stable_hash(queue_hash_payload)

    with persistence.connect(path) as conn:
        if existing_item:
            conn.execute(
                """
                UPDATE ob_manual_live_proof_packet_review_queue
                SET updated_at = ?,
                    owner_id = ?,
                    symbol = ?,
                    dry_run_outcome = ?,
                    packet_status = ?,
                    queue_status = ?,
                    priority = ?,
                    review_lane = ?,
                    review_reason = ?,
                    packet_hash = ?,
                    packet_snapshot_json = ?,
                    queue_hash = ?,
                    service_version = ?
                WHERE packet_id = ?
                """,
                (
                    now,
                    owner_id,
                    symbol,
                    dry_run_outcome,
                    packet_status,
                    queue_status,
                    priority,
                    review_lane,
                    review_reason,
                    packet["packet_hash"],
                    json.dumps(packet, sort_keys=True),
                    queue_hash,
                    QUEUE_VERSION,
                    packet_id,
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO ob_manual_live_proof_packet_review_queue (
                    queue_item_id, packet_id, record_id, created_at, updated_at,
                    owner_id, symbol, dry_run_outcome, packet_status, queue_status,
                    priority, review_lane, review_reason, packet_hash, packet_snapshot_json, queue_hash,
                    real_broker_order_submitted, broker_api_used, broker_account_read, bank_account_read,
                    real_capital_moved, direct_vault_upload, real_manual_live_ready_claim,
                    service_version
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0, 0, 0, ?)
                """,
                (
                    queue_item_id,
                    packet_id,
                    packet["record_id"],
                    now,
                    now,
                    owner_id,
                    symbol,
                    dry_run_outcome,
                    packet_status,
                    queue_status,
                    priority,
                    review_lane,
                    review_reason,
                    packet["packet_hash"],
                    json.dumps(packet, sort_keys=True),
                    queue_hash,
                    QUEUE_VERSION,
                ),
            )
        conn.commit()

    item = get_queue_item(queue_item_id, path)
    if not item:
        raise RuntimeError("Queue item was not found after materialization.")

    return {
        "ok": True,
        "materialized": True,
        "real_owner_review_queue_persistence": True,
        "queue_item": item,
        "boundaries": queue_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }



def materialize_all_receipt_packets(path: Optional[Path] = None) -> Dict[str, Any]:
    init_queue_db(path)
    packets = receipts.list_receipt_packets(limit=200, path=path)
    items = []
    for packet in packets:
        items.append(materialize_queue_item(packet["packet_id"], path=path)["queue_item"])

    return {
        "ok": True,
        "materialized_count": len(items),
        "queue_items": items,
        "real_owner_review_queue_persistence": True,
        "boundaries": queue_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


def get_queue_item(queue_item_id: str, path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    init_queue_db(path)
    with persistence.connect(path) as conn:
        row = conn.execute(
            "SELECT * FROM ob_manual_live_proof_packet_review_queue WHERE queue_item_id = ?",
            (queue_item_id,),
        ).fetchone()
    return queue_row_to_dict(row) if row else None


def get_queue_item_by_packet(packet_id: str, path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    init_queue_db(path)
    with persistence.connect(path) as conn:
        row = conn.execute(
            "SELECT * FROM ob_manual_live_proof_packet_review_queue WHERE packet_id = ?",
            (packet_id,),
        ).fetchone()
    return queue_row_to_dict(row) if row else None


def update_queue_item(queue_item_id: str, payload: Dict[str, Any], path: Optional[Path] = None) -> Dict[str, Any]:
    validate_no_live_action_flags(payload)
    init_queue_db(path)

    item = get_queue_item(queue_item_id, path)
    if not item:
        raise KeyError(f"Queue item not found: {queue_item_id}")

    queue_status = _clean_string(payload.get("queue_status"), item["queue_status"])
    if queue_status not in ALLOWED_QUEUE_STATUSES:
        queue_status = item["queue_status"]

    priority = _clean_string(payload.get("priority"), item["priority"])
    if priority not in ALLOWED_PRIORITY:
        priority = item["priority"]

    review_reason = _clean_string(payload.get("review_reason"), item["review_reason"])
    review_lane = _clean_string(payload.get("review_lane"), item["review_lane"])

    queue_hash_payload = {
        "queue_item_id": queue_item_id,
        "packet_id": item["packet_id"],
        "record_id": item["record_id"],
        "owner_id": item["owner_id"],
        "symbol": item["symbol"],
        "dry_run_outcome": item["dry_run_outcome"],
        "packet_status": item["packet_status"],
        "queue_status": queue_status,
        "priority": priority,
        "review_lane": review_lane,
        "review_reason": review_reason,
        "packet_hash": item["packet_hash"],
    }
    queue_hash = stable_hash(queue_hash_payload)

    with persistence.connect(path) as conn:
        conn.execute(
            """
            UPDATE ob_manual_live_proof_packet_review_queue
            SET updated_at = ?,
                queue_status = ?,
                priority = ?,
                review_lane = ?,
                review_reason = ?,
                queue_hash = ?,
                service_version = ?
            WHERE queue_item_id = ?
            """,
            (
                utc_now_iso(),
                queue_status,
                priority,
                review_lane,
                review_reason,
                queue_hash,
                QUEUE_VERSION,
                queue_item_id,
            ),
        )
        conn.commit()

    updated = get_queue_item(queue_item_id, path)
    return {
        "ok": True,
        "updated": True,
        "queue_item": updated,
        "real_queue_status_update": True,
        "boundaries": queue_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


def search_queue(
    q: Optional[str] = None,
    symbol: Optional[str] = None,
    queue_status: Optional[str] = None,
    dry_run_outcome: Optional[str] = None,
    packet_status: Optional[str] = None,
    owner_id: Optional[str] = None,
    limit: int = 100,
    path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    init_queue_db(path)
    limit = max(1, min(int(limit or 100), 300))

    clauses = []
    params: List[Any] = []

    if q:
        like = f"%{q.lower()}%"
        clauses.append(
            "(lower(symbol) LIKE ? OR lower(review_reason) LIKE ? OR lower(packet_id) LIKE ? OR lower(record_id) LIKE ?)"
        )
        params.extend([like, like, like, like])
    if symbol:
        clauses.append("symbol = ?")
        params.append(symbol.upper())
    if queue_status:
        clauses.append("queue_status = ?")
        params.append(queue_status)
    if dry_run_outcome:
        clauses.append("dry_run_outcome = ?")
        params.append(dry_run_outcome)
    if packet_status:
        clauses.append("packet_status = ?")
        params.append(packet_status)
    if owner_id:
        clauses.append("owner_id = ?")
        params.append(owner_id)

    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    sql = f"""
        SELECT *
        FROM ob_manual_live_proof_packet_review_queue
        {where}
        ORDER BY
            CASE priority
                WHEN 'urgent' THEN 1
                WHEN 'high' THEN 2
                WHEN 'normal' THEN 3
                WHEN 'low' THEN 4
                ELSE 5
            END,
            updated_at DESC
        LIMIT ?
    """
    params.append(limit)

    with persistence.connect(path) as conn:
        rows = conn.execute(sql, params).fetchall()

    return [queue_row_to_dict(row) for row in rows]


def queue_overview(
    q: Optional[str] = None,
    symbol: Optional[str] = None,
    queue_status: Optional[str] = None,
    dry_run_outcome: Optional[str] = None,
    packet_status: Optional[str] = None,
    owner_id: Optional[str] = None,
    limit: int = 100,
    materialize: bool = True,
    path: Optional[Path] = None,
) -> Dict[str, Any]:
    init_queue_db(path)

    if materialize:
        materialize_all_receipt_packets(path)

    items = search_queue(
        q=q,
        symbol=symbol,
        queue_status=queue_status,
        dry_run_outcome=dry_run_outcome,
        packet_status=packet_status,
        owner_id=owner_id,
        limit=limit,
        path=path,
    )

    status_counts: Dict[str, int] = {}
    symbol_counts: Dict[str, int] = {}
    priority_counts: Dict[str, int] = {}
    outcome_counts: Dict[str, int] = {}

    for item in items:
        status_counts[item["queue_status"]] = status_counts.get(item["queue_status"], 0) + 1
        symbol_counts[item["symbol"]] = symbol_counts.get(item["symbol"], 0) + 1
        priority_counts[item["priority"]] = priority_counts.get(item["priority"], 0) + 1
        outcome_counts[item["dry_run_outcome"]] = outcome_counts.get(item["dry_run_outcome"], 0) + 1

    return {
        "ok": True,
        "version": QUEUE_VERSION,
        "queue_items": items,
        "queue_item_count": len(items),
        "filters": {
            "q": q,
            "symbol": symbol,
            "queue_status": queue_status,
            "dry_run_outcome": dry_run_outcome,
            "packet_status": packet_status,
            "owner_id": owner_id,
            "limit": limit,
        },
        "status_counts": status_counts,
        "symbol_counts": symbol_counts,
        "priority_counts": priority_counts,
        "outcome_counts": outcome_counts,
        "real_owner_review_queue_persistence": True,
        "real_receipt_packet_search": True,
        "real_queue_filtering": True,
        "boundaries": queue_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


def queue_status_payload(path: Optional[Path] = None) -> Dict[str, Any]:
    init_queue_db(path)
    overview = queue_overview(limit=25, materialize=True, path=path)

    return {
        "ok": True,
        "version": QUEUE_VERSION,
        "queue_schema_version": QUEUE_SCHEMA_VERSION,
        "queue_item_count": overview["queue_item_count"],
        "status_counts": overview["status_counts"],
        "symbol_counts": overview["symbol_counts"],
        "priority_counts": overview["priority_counts"],
        "real_owner_review_queue_persistence": True,
        "real_receipt_packet_search": True,
        "real_queue_filtering": True,
        "db_path": str(path or persistence.db_path()),
        "boundaries": queue_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


__all__ = [
    "QUEUE_VERSION",
    "QUEUE_SCHEMA_VERSION",
    "init_queue_db",
    "materialize_queue_item",
    "materialize_all_receipt_packets",
    "get_queue_item",
    "get_queue_item_by_packet",
    "update_queue_item",
    "search_queue",
    "queue_overview",
    "queue_status_payload",
    "queue_boundaries",
]
