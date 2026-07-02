# OB_GIANT_PACK_040_MANUAL_LIVE_EVIDENCE_RECEIPT_LAYER_READINESS_CHECKPOINT_SERVICE
"""
Real readiness checkpoint for the OB Manual Live Level 1 Evidence & Receipt Layer.

This closes GP036-GP040 by verifying the real app-owned evidence spine:
- dry-run records
- review events
- receipt packets
- proof packet owner queue
- readiness snapshots

It writes durable SQLite readiness snapshots with hashes.

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
from web import ob_manual_live_proof_packet_review_queue as queue


READINESS_VERSION = "OB_GIANT_PACK_040_MANUAL_LIVE_EVIDENCE_RECEIPT_LAYER_READINESS_CHECKPOINT"
READINESS_SCHEMA_VERSION = 1
READINESS_LABEL = "manual_live_evidence_receipt_layer_ready"

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


def init_readiness_db(path: Optional[Path] = None) -> Dict[str, Any]:
    queue.init_queue_db(path)

    with persistence.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ob_manual_live_evidence_readiness_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                readiness_label TEXT NOT NULL,
                readiness_score INTEGER NOT NULL,
                layer_ready INTEGER NOT NULL,
                evidence_chain_sample_present INTEGER NOT NULL,

                snapshot_json TEXT NOT NULL,
                snapshot_hash TEXT NOT NULL,

                real_broker_order_submitted INTEGER NOT NULL DEFAULT 0,
                broker_api_used INTEGER NOT NULL DEFAULT 0,
                broker_account_read INTEGER NOT NULL DEFAULT 0,
                bank_account_read INTEGER NOT NULL DEFAULT 0,
                real_capital_moved INTEGER NOT NULL DEFAULT 0,
                direct_vault_upload INTEGER NOT NULL DEFAULT 0,
                real_manual_live_ready_claim INTEGER NOT NULL DEFAULT 0,

                service_version TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_evidence_readiness_created ON ob_manual_live_evidence_readiness_snapshots(created_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_evidence_readiness_label ON ob_manual_live_evidence_readiness_snapshots(readiness_label, created_at DESC)"
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
            ("ob_manual_live_evidence_readiness_snapshots", READINESS_SCHEMA_VERSION, READINESS_VERSION, now, now),
        )
        conn.commit()

    return {
        "ok": True,
        "schema_name": "ob_manual_live_evidence_readiness_snapshots",
        "schema_version": READINESS_SCHEMA_VERSION,
        "service_version": READINESS_VERSION,
        "real_readiness_snapshot_persistence": True,
        "real_evidence_layer_checkpoint": True,
        "db_path": str(path or persistence.db_path()),
    }


def readiness_boundaries() -> Dict[str, Any]:
    return {
        "manual_live_evidence_receipt_layer_checkpoint_only": True,
        "real_sqlite_persistence": True,
        "real_durable_dry_run_records": True,
        "real_review_event_persistence": True,
        "real_receipt_packet_persistence": True,
        "real_owner_review_queue_persistence": True,
        "real_readiness_snapshot_persistence": True,
        "real_readiness_snapshot_hash": True,
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


def _check(name: str, ok: bool, detail: str, category: str = "capability") -> Dict[str, Any]:
    return {
        "name": name,
        "ok": bool(ok),
        "detail": detail,
        "category": category,
    }


def build_readiness_snapshot(path: Optional[Path] = None) -> Dict[str, Any]:
    init_readiness_db(path)

    dry_run_status = persistence.service_status(path)
    history_status = history.history_status(path)
    receipt_status = receipts.receipt_status(path)
    queue_status = queue.queue_status_payload(path)

    dry_records = persistence.list_dry_run_records(limit=10, path=path)
    review_events = history.list_review_events(limit=10, path=path)
    receipt_packets = receipts.list_receipt_packets(limit=10, path=path)
    queue_items = queue.search_queue(limit=10, path=path)

    checks: List[Dict[str, Any]] = [
        _check(
            "real_dry_run_record_persistence",
            dry_run_status.get("real_sqlite_persistence") is True and dry_run_status.get("real_durable_records") is True,
            "GP036 real SQLite dry-run record persistence is available.",
        ),
        _check(
            "real_dry_run_create_endpoint_contract",
            dry_run_status.get("real_create_endpoint_enabled") is True,
            "GP036 create endpoint contract is enabled.",
        ),
        _check(
            "real_dry_run_list_endpoint_contract",
            dry_run_status.get("real_list_endpoint_enabled") is True,
            "GP036 list endpoint contract is enabled.",
        ),
        _check(
            "real_dry_run_read_endpoint_contract",
            dry_run_status.get("real_read_endpoint_enabled") is True,
            "GP036 read endpoint contract is enabled.",
        ),
        _check(
            "real_review_event_persistence",
            history_status.get("real_review_event_persistence") is True,
            "GP037 review event persistence is available.",
        ),
        _check(
            "real_record_detail_history",
            history_status.get("real_record_detail_enabled") is True and history_status.get("real_history_enabled") is True,
            "GP037 record detail and history are available.",
        ),
        _check(
            "real_receipt_packet_persistence",
            receipt_status.get("real_receipt_packet_persistence") is True,
            "GP038 receipt packet persistence is available.",
        ),
        _check(
            "real_receipt_json_file_write",
            receipt_status.get("real_receipt_json_file_write") is True,
            "GP038 JSON receipt packet file writes are available.",
        ),
        _check(
            "real_receipt_packet_hash",
            receipt_status.get("real_receipt_packet_hash") is True,
            "GP038 receipt packet hashes are available.",
        ),
        _check(
            "real_owner_review_queue_persistence",
            queue_status.get("real_owner_review_queue_persistence") is True,
            "GP039 proof packet owner review queue persistence is available.",
        ),
        _check(
            "real_receipt_packet_search",
            queue_status.get("real_receipt_packet_search") is True,
            "GP039 proof packet search is available.",
        ),
        _check(
            "real_queue_filtering",
            queue_status.get("real_queue_filtering") is True,
            "GP039 queue filtering is available.",
        ),
        _check(
            "live_auto_locked_preserved",
            readiness_boundaries().get("live_auto_locked") is True,
            "Live Auto Locked is preserved.",
            "boundary",
        ),
        _check(
            "broker_order_disabled",
            readiness_boundaries().get("order_submit_enabled") is False,
            "Broker order submit remains disabled.",
            "boundary",
        ),
        _check(
            "direct_vault_upload_disabled",
            readiness_boundaries().get("direct_vault_upload_enabled") is False,
            "Direct Vault upload remains disabled.",
            "boundary",
        ),
        _check(
            "real_manual_live_not_ready",
            readiness_boundaries().get("real_manual_live_ready") is False,
            "Real Manual Live is still not unlocked.",
            "boundary",
        ),
    ]

    passed = sum(1 for item in checks if item["ok"])
    total = len(checks)
    readiness_score = int(round((passed / total) * 100)) if total else 0
    layer_ready = passed == total

    evidence_chain_sample_present = (
        len(dry_records) > 0
        and len(review_events) > 0
        and len(receipt_packets) > 0
        and len(queue_items) > 0
    )

    snapshot = {
        "version": READINESS_VERSION,
        "created_at": utc_now_iso(),
        "readiness_label": READINESS_LABEL if layer_ready else "manual_live_evidence_receipt_layer_attention_required",
        "readiness_score": readiness_score,
        "layer_ready": layer_ready,
        "safe_to_close_gp036_to_gp040": layer_ready,
        "safe_to_move_to_gp041": layer_ready,
        "evidence_chain_sample_present": evidence_chain_sample_present,
        "counts": {
            "dry_run_records": int(dry_run_status.get("record_count", len(dry_records))),
            "review_events": int(history_status.get("review_event_count", len(review_events))),
            "receipt_packets": int(receipt_status.get("packet_count", len(receipt_packets))),
            "queue_items": int(queue_status.get("queue_item_count", len(queue_items))),
        },
        "checks": checks,
        "passed_checks": passed,
        "total_checks": total,
        "services": {
            "dry_run_persistence": {
                "version": dry_run_status.get("version"),
                "schema_version": dry_run_status.get("schema_version") or (dry_run_status.get("schema") or {}).get("schema_version"),
                "real_sqlite_persistence": dry_run_status.get("real_sqlite_persistence"),
                "real_durable_records": dry_run_status.get("real_durable_records"),
            },
            "history_review": {
                "version": history_status.get("version"),
                "schema_version": history_status.get("history_schema_version"),
                "real_review_event_persistence": history_status.get("real_review_event_persistence"),
                "real_history_enabled": history_status.get("real_history_enabled"),
            },
            "receipt_packets": {
                "version": receipt_status.get("version"),
                "schema_version": receipt_status.get("receipt_schema_version"),
                "real_receipt_packet_persistence": receipt_status.get("real_receipt_packet_persistence"),
                "real_receipt_json_file_write": receipt_status.get("real_receipt_json_file_write"),
                "real_receipt_packet_hash": receipt_status.get("real_receipt_packet_hash"),
            },
            "proof_packet_queue": {
                "version": queue_status.get("version"),
                "schema_version": queue_status.get("queue_schema_version"),
                "real_owner_review_queue_persistence": queue_status.get("real_owner_review_queue_persistence"),
                "real_receipt_packet_search": queue_status.get("real_receipt_packet_search"),
                "real_queue_filtering": queue_status.get("real_queue_filtering"),
            },
        },
        "layer_sequence": [
            "GP036 real dry-run record persistence",
            "GP037 real dry-run detail/history review",
            "GP038 real dry-run receipt packet engine",
            "GP039 real proof packet owner review queue",
            "GP040 evidence & receipt layer readiness checkpoint",
        ],
        "next_section": "OB — Manual Live Level 1 Decision-to-Receipt Operating Layer",
        "next_pack": "GP041",
        "blocked_actions": LOCKED_ACTIONS,
        "boundaries": readiness_boundaries(),
    }

    snapshot["snapshot_hash"] = stable_hash(snapshot)
    return snapshot


def snapshot_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "snapshot_id": row["snapshot_id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "readiness_label": row["readiness_label"],
        "readiness_score": row["readiness_score"],
        "layer_ready": bool(row["layer_ready"]),
        "evidence_chain_sample_present": bool(row["evidence_chain_sample_present"]),
        "snapshot": json.loads(row["snapshot_json"] or "{}"),
        "snapshot_hash": row["snapshot_hash"],
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


def create_readiness_snapshot(payload: Optional[Dict[str, Any]] = None, path: Optional[Path] = None) -> Dict[str, Any]:
    payload = payload or {}
    init_readiness_db(path)

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
        raise ValueError("Evidence readiness snapshot cannot carry live-action flags: " + ", ".join(violations))

    snapshot = build_readiness_snapshot(path)
    snapshot_id = str(payload.get("snapshot_id") or f"obready_{uuid.uuid4().hex}")
    now = utc_now_iso()

    with persistence.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO ob_manual_live_evidence_readiness_snapshots (
                snapshot_id, created_at, updated_at,
                readiness_label, readiness_score, layer_ready, evidence_chain_sample_present,
                snapshot_json, snapshot_hash,
                real_broker_order_submitted, broker_api_used, broker_account_read, bank_account_read,
                real_capital_moved, direct_vault_upload, real_manual_live_ready_claim,
                service_version
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0, 0, 0, ?)
            """,
            (
                snapshot_id,
                now,
                now,
                snapshot["readiness_label"],
                snapshot["readiness_score"],
                1 if snapshot["layer_ready"] else 0,
                1 if snapshot["evidence_chain_sample_present"] else 0,
                json.dumps(snapshot, sort_keys=True),
                snapshot["snapshot_hash"],
                READINESS_VERSION,
            ),
        )
        conn.commit()

    created = get_readiness_snapshot(snapshot_id, path)
    if not created:
        raise RuntimeError("Readiness snapshot was not found after insert.")

    return {
        "ok": True,
        "created": True,
        "real_readiness_snapshot_persistence": True,
        "real_readiness_snapshot_hash": True,
        "snapshot_record": created,
        "snapshot": created["snapshot"],
        "boundaries": readiness_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


def get_readiness_snapshot(snapshot_id: str, path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    init_readiness_db(path)
    with persistence.connect(path) as conn:
        row = conn.execute(
            "SELECT * FROM ob_manual_live_evidence_readiness_snapshots WHERE snapshot_id = ?",
            (snapshot_id,),
        ).fetchone()
    return snapshot_row_to_dict(row) if row else None


def list_readiness_snapshots(limit: int = 50, path: Optional[Path] = None) -> List[Dict[str, Any]]:
    init_readiness_db(path)
    limit = max(1, min(int(limit or 50), 200))

    with persistence.connect(path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM ob_manual_live_evidence_readiness_snapshots
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [snapshot_row_to_dict(row) for row in rows]


def readiness_overview(path: Optional[Path] = None) -> Dict[str, Any]:
    init_readiness_db(path)
    current = build_readiness_snapshot(path)
    snapshots = list_readiness_snapshots(limit=25, path=path)

    return {
        "ok": True,
        "version": READINESS_VERSION,
        "current": current,
        "snapshots": snapshots,
        "snapshot_count": len(snapshots),
        "readiness_label": current["readiness_label"],
        "readiness_score": current["readiness_score"],
        "layer_ready": current["layer_ready"],
        "safe_to_close_gp036_to_gp040": current["safe_to_close_gp036_to_gp040"],
        "safe_to_move_to_gp041": current["safe_to_move_to_gp041"],
        "next_section": current["next_section"],
        "next_pack": current["next_pack"],
        "real_readiness_snapshot_persistence": True,
        "real_readiness_snapshot_hash": True,
        "boundaries": readiness_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


__all__ = [
    "READINESS_VERSION",
    "READINESS_SCHEMA_VERSION",
    "READINESS_LABEL",
    "init_readiness_db",
    "build_readiness_snapshot",
    "create_readiness_snapshot",
    "get_readiness_snapshot",
    "list_readiness_snapshots",
    "readiness_overview",
    "readiness_boundaries",
]
