# OB_GIANT_PACK_041_REAL_CANDIDATE_TO_DECISION_HANDOFF_SERVICE
"""
Real candidate-to-decision handoff service for OB Manual Live Level 1.

This starts the Decision-to-Receipt Operating Layer by persisting real candidate
handoff records before any checklist, receipt, or live action happens.

It writes durable SQLite records with candidate payload fingerprints and owner
decision state.

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
from web import ob_manual_live_evidence_readiness_checkpoint as evidence_readiness


HANDOFF_VERSION = "OB_GIANT_PACK_041_REAL_CANDIDATE_TO_DECISION_HANDOFF"
HANDOFF_SCHEMA_VERSION = 1

ALLOWED_DECISION_STATUSES = {
    "queued_for_owner_decision",
    "owner_reviewing",
    "decided_not_placed",
    "decided_fake_fill",
    "needs_review",
    "blocked_live",
    "archived",
}

ALLOWED_DECISION_INTENTS = {
    "review_candidate",
    "create_evidence_record_next",
    "create_receipt_after_record",
    "watch_only",
    "blocked_live_review",
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


def init_handoff_db(path: Optional[Path] = None) -> Dict[str, Any]:
    evidence_readiness.init_readiness_db(path)

    with persistence.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ob_manual_live_candidate_decision_handoffs (
                handoff_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                owner_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                candidate_id TEXT NOT NULL,
                candidate_source TEXT NOT NULL,
                candidate_strategy TEXT NOT NULL,
                candidate_direction TEXT NOT NULL,
                candidate_score REAL NOT NULL,
                candidate_confidence TEXT NOT NULL,
                lane TEXT NOT NULL,

                decision_status TEXT NOT NULL,
                decision_intent TEXT NOT NULL,
                review_lane TEXT NOT NULL,
                handoff_reason TEXT NOT NULL,

                candidate_payload_json TEXT NOT NULL,
                candidate_fingerprint TEXT NOT NULL,
                handoff_hash TEXT NOT NULL,

                linked_evidence_record_id TEXT,
                linked_receipt_packet_id TEXT,

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
            "CREATE INDEX IF NOT EXISTS idx_ob_candidate_handoff_symbol_updated ON ob_manual_live_candidate_decision_handoffs(symbol, updated_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_candidate_handoff_status_updated ON ob_manual_live_candidate_decision_handoffs(decision_status, updated_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ob_candidate_handoff_owner_updated ON ob_manual_live_candidate_decision_handoffs(owner_id, updated_at DESC)"
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
            ("ob_manual_live_candidate_decision_handoffs", HANDOFF_SCHEMA_VERSION, HANDOFF_VERSION, now, now),
        )
        conn.commit()

    return {
        "ok": True,
        "schema_name": "ob_manual_live_candidate_decision_handoffs",
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "service_version": HANDOFF_VERSION,
        "real_candidate_decision_handoff_persistence": True,
        "real_candidate_payload_fingerprint": True,
        "real_owner_decision_state": True,
        "db_path": str(path or persistence.db_path()),
    }


def _clean_string(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _clean_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
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
        "upload_to_vault",
        "place_trade",
        "place_order",
        "broker_read",
        "bank_read",
    ]
    violations = [field for field in forbidden_truthy_fields if bool(payload.get(field))]
    if violations:
        raise ValueError("Candidate decision handoff cannot carry live-action flags: " + ", ".join(violations))


def handoff_boundaries() -> Dict[str, Any]:
    return {
        "manual_live_candidate_to_decision_handoff_only": True,
        "decision_to_receipt_operating_layer_started": True,
        "real_sqlite_persistence": True,
        "real_candidate_decision_handoff_persistence": True,
        "real_candidate_payload_fingerprint": True,
        "real_owner_decision_state": True,
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


def normalize_candidate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    candidate = payload.get("candidate") if isinstance(payload.get("candidate"), dict) else payload

    symbol = _clean_string(candidate.get("symbol"), "UNKNOWN").upper()
    candidate_id = _clean_string(candidate.get("candidate_id"), candidate.get("id") or f"candidate_{symbol.lower()}_{uuid.uuid4().hex[:12]}")
    candidate_source = _clean_string(candidate.get("candidate_source"), candidate.get("source") or "ob_engine_feed")
    candidate_strategy = _clean_string(candidate.get("strategy"), candidate.get("candidate_strategy") or "manual_live_review")
    candidate_direction = _clean_string(candidate.get("direction"), candidate.get("side") or "watch")
    candidate_score = _clean_float(candidate.get("score"), 0.0)
    candidate_confidence = _clean_string(candidate.get("confidence"), candidate.get("confidence_label") or "unscored")

    normalized = {
        "symbol": symbol,
        "candidate_id": candidate_id,
        "candidate_source": candidate_source,
        "candidate_strategy": candidate_strategy,
        "candidate_direction": candidate_direction,
        "candidate_score": candidate_score,
        "candidate_confidence": candidate_confidence,
        "candidate_payload": candidate,
    }
    return normalized


def handoff_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "handoff_id": row["handoff_id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "owner_id": row["owner_id"],
        "symbol": row["symbol"],
        "candidate_id": row["candidate_id"],
        "candidate_source": row["candidate_source"],
        "candidate_strategy": row["candidate_strategy"],
        "candidate_direction": row["candidate_direction"],
        "candidate_score": row["candidate_score"],
        "candidate_confidence": row["candidate_confidence"],
        "lane": row["lane"],
        "decision_status": row["decision_status"],
        "decision_intent": row["decision_intent"],
        "review_lane": row["review_lane"],
        "handoff_reason": row["handoff_reason"],
        "candidate_payload": json.loads(row["candidate_payload_json"] or "{}"),
        "candidate_fingerprint": row["candidate_fingerprint"],
        "handoff_hash": row["handoff_hash"],
        "linked_evidence_record_id": row["linked_evidence_record_id"],
        "linked_receipt_packet_id": row["linked_receipt_packet_id"],
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


def create_candidate_decision_handoff(payload: Dict[str, Any], path: Optional[Path] = None) -> Dict[str, Any]:
    validate_no_live_action_flags(payload)
    init_handoff_db(path)

    candidate = normalize_candidate_payload(payload)
    decision_status = _clean_string(payload.get("decision_status"), "queued_for_owner_decision")
    if decision_status not in ALLOWED_DECISION_STATUSES:
        decision_status = "queued_for_owner_decision"

    decision_intent = _clean_string(payload.get("decision_intent"), "review_candidate")
    if decision_intent not in ALLOWED_DECISION_INTENTS:
        decision_intent = "review_candidate"

    owner_id = _clean_string(payload.get("owner_id"), "owner_solice")
    lane = _clean_string(payload.get("lane"), "Manual Live Level 1")
    review_lane = _clean_string(payload.get("review_lane"), "Candidate-to-Decision Handoff")
    handoff_reason = _clean_string(
        payload.get("handoff_reason"),
        f"Candidate {candidate['symbol']} is queued for owner Manual Live decision review.",
    )

    handoff_id = _clean_string(payload.get("handoff_id"), f"obhand_{uuid.uuid4().hex}")
    now = utc_now_iso()

    candidate_fingerprint = stable_hash({
        "symbol": candidate["symbol"],
        "candidate_id": candidate["candidate_id"],
        "candidate_source": candidate["candidate_source"],
        "candidate_strategy": candidate["candidate_strategy"],
        "candidate_direction": candidate["candidate_direction"],
        "candidate_score": candidate["candidate_score"],
        "candidate_confidence": candidate["candidate_confidence"],
        "candidate_payload": candidate["candidate_payload"],
    })

    handoff_hash = stable_hash({
        "handoff_id": handoff_id,
        "owner_id": owner_id,
        "symbol": candidate["symbol"],
        "candidate_id": candidate["candidate_id"],
        "decision_status": decision_status,
        "decision_intent": decision_intent,
        "candidate_fingerprint": candidate_fingerprint,
        "lane": lane,
        "review_lane": review_lane,
        "handoff_reason": handoff_reason,
    })

    with persistence.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO ob_manual_live_candidate_decision_handoffs (
                handoff_id, created_at, updated_at,
                owner_id, symbol, candidate_id, candidate_source, candidate_strategy,
                candidate_direction, candidate_score, candidate_confidence, lane,
                decision_status, decision_intent, review_lane, handoff_reason,
                candidate_payload_json, candidate_fingerprint, handoff_hash,
                linked_evidence_record_id, linked_receipt_packet_id,
                real_broker_order_submitted, broker_api_used, broker_account_read, bank_account_read,
                real_capital_moved, direct_vault_upload, real_manual_live_ready_claim,
                service_version
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, 0, 0, 0, 0, 0, 0, 0, ?)
            """,
            (
                handoff_id,
                now,
                now,
                owner_id,
                candidate["symbol"],
                candidate["candidate_id"],
                candidate["candidate_source"],
                candidate["candidate_strategy"],
                candidate["candidate_direction"],
                candidate["candidate_score"],
                candidate["candidate_confidence"],
                lane,
                decision_status,
                decision_intent,
                review_lane,
                handoff_reason,
                json.dumps(candidate["candidate_payload"], sort_keys=True),
                candidate_fingerprint,
                handoff_hash,
                HANDOFF_VERSION,
            ),
        )
        conn.commit()

    handoff = get_candidate_decision_handoff(handoff_id, path)
    if not handoff:
        raise RuntimeError("Candidate decision handoff was not found after insert.")

    return {
        "ok": True,
        "created": True,
        "real_candidate_decision_handoff_persistence": True,
        "real_candidate_payload_fingerprint": True,
        "real_owner_decision_state": True,
        "handoff": handoff,
        "boundaries": handoff_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


def get_candidate_decision_handoff(handoff_id: str, path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    init_handoff_db(path)
    with persistence.connect(path) as conn:
        row = conn.execute(
            "SELECT * FROM ob_manual_live_candidate_decision_handoffs WHERE handoff_id = ?",
            (handoff_id,),
        ).fetchone()
    return handoff_row_to_dict(row) if row else None


def update_candidate_decision_handoff(handoff_id: str, payload: Dict[str, Any], path: Optional[Path] = None) -> Dict[str, Any]:
    validate_no_live_action_flags(payload)
    init_handoff_db(path)

    existing = get_candidate_decision_handoff(handoff_id, path)
    if not existing:
        raise KeyError(f"Candidate decision handoff not found: {handoff_id}")

    decision_status = _clean_string(payload.get("decision_status"), existing["decision_status"])
    if decision_status not in ALLOWED_DECISION_STATUSES:
        decision_status = existing["decision_status"]

    decision_intent = _clean_string(payload.get("decision_intent"), existing["decision_intent"])
    if decision_intent not in ALLOWED_DECISION_INTENTS:
        decision_intent = existing["decision_intent"]

    review_lane = _clean_string(payload.get("review_lane"), existing["review_lane"])
    handoff_reason = _clean_string(payload.get("handoff_reason"), existing["handoff_reason"])
    linked_evidence_record_id = payload.get("linked_evidence_record_id", existing["linked_evidence_record_id"])
    linked_receipt_packet_id = payload.get("linked_receipt_packet_id", existing["linked_receipt_packet_id"])

    handoff_hash = stable_hash({
        "handoff_id": handoff_id,
        "owner_id": existing["owner_id"],
        "symbol": existing["symbol"],
        "candidate_id": existing["candidate_id"],
        "decision_status": decision_status,
        "decision_intent": decision_intent,
        "candidate_fingerprint": existing["candidate_fingerprint"],
        "lane": existing["lane"],
        "review_lane": review_lane,
        "handoff_reason": handoff_reason,
        "linked_evidence_record_id": linked_evidence_record_id,
        "linked_receipt_packet_id": linked_receipt_packet_id,
    })

    with persistence.connect(path) as conn:
        conn.execute(
            """
            UPDATE ob_manual_live_candidate_decision_handoffs
            SET updated_at = ?,
                decision_status = ?,
                decision_intent = ?,
                review_lane = ?,
                handoff_reason = ?,
                linked_evidence_record_id = ?,
                linked_receipt_packet_id = ?,
                handoff_hash = ?,
                service_version = ?
            WHERE handoff_id = ?
            """,
            (
                utc_now_iso(),
                decision_status,
                decision_intent,
                review_lane,
                handoff_reason,
                linked_evidence_record_id,
                linked_receipt_packet_id,
                handoff_hash,
                HANDOFF_VERSION,
                handoff_id,
            ),
        )
        conn.commit()

    updated = get_candidate_decision_handoff(handoff_id, path)
    return {
        "ok": True,
        "updated": True,
        "handoff": updated,
        "real_owner_decision_state": True,
        "boundaries": handoff_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


def list_candidate_decision_handoffs(
    q: Optional[str] = None,
    symbol: Optional[str] = None,
    decision_status: Optional[str] = None,
    owner_id: Optional[str] = None,
    limit: int = 100,
    path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    init_handoff_db(path)
    limit = max(1, min(int(limit or 100), 300))

    clauses = []
    params: List[Any] = []

    if q:
        like = f"%{q.lower()}%"
        clauses.append(
            "(lower(symbol) LIKE ? OR lower(candidate_id) LIKE ? OR lower(candidate_source) LIKE ? OR lower(handoff_reason) LIKE ?)"
        )
        params.extend([like, like, like, like])
    if symbol:
        clauses.append("symbol = ?")
        params.append(symbol.upper())
    if decision_status:
        clauses.append("decision_status = ?")
        params.append(decision_status)
    if owner_id:
        clauses.append("owner_id = ?")
        params.append(owner_id)

    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    sql = f"""
        SELECT *
        FROM ob_manual_live_candidate_decision_handoffs
        {where}
        ORDER BY updated_at DESC
        LIMIT ?
    """
    params.append(limit)

    with persistence.connect(path) as conn:
        rows = conn.execute(sql, params).fetchall()

    return [handoff_row_to_dict(row) for row in rows]


def handoff_overview(
    q: Optional[str] = None,
    symbol: Optional[str] = None,
    decision_status: Optional[str] = None,
    owner_id: Optional[str] = None,
    limit: int = 100,
    path: Optional[Path] = None,
) -> Dict[str, Any]:
    init_handoff_db(path)
    handoffs = list_candidate_decision_handoffs(
        q=q,
        symbol=symbol,
        decision_status=decision_status,
        owner_id=owner_id,
        limit=limit,
        path=path,
    )

    status_counts: Dict[str, int] = {}
    symbol_counts: Dict[str, int] = {}
    source_counts: Dict[str, int] = {}

    for item in handoffs:
        status_counts[item["decision_status"]] = status_counts.get(item["decision_status"], 0) + 1
        symbol_counts[item["symbol"]] = symbol_counts.get(item["symbol"], 0) + 1
        source_counts[item["candidate_source"]] = source_counts.get(item["candidate_source"], 0) + 1

    return {
        "ok": True,
        "version": HANDOFF_VERSION,
        "handoffs": handoffs,
        "handoff_count": len(handoffs),
        "filters": {
            "q": q,
            "symbol": symbol,
            "decision_status": decision_status,
            "owner_id": owner_id,
            "limit": limit,
        },
        "status_counts": status_counts,
        "symbol_counts": symbol_counts,
        "source_counts": source_counts,
        "real_candidate_decision_handoff_persistence": True,
        "real_candidate_payload_fingerprint": True,
        "real_owner_decision_state": True,
        "next_expected_step": "GP042 — Real Checklist-to-Record Save Flow",
        "section": "OB — Manual Live Level 1 Decision-to-Receipt Operating Layer",
        "boundaries": handoff_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


def handoff_status_payload(path: Optional[Path] = None) -> Dict[str, Any]:
    init_handoff_db(path)
    overview = handoff_overview(limit=25, path=path)

    return {
        "ok": True,
        "version": HANDOFF_VERSION,
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "handoff_count": overview["handoff_count"],
        "status_counts": overview["status_counts"],
        "symbol_counts": overview["symbol_counts"],
        "real_candidate_decision_handoff_persistence": True,
        "real_candidate_payload_fingerprint": True,
        "real_owner_decision_state": True,
        "db_path": str(path or persistence.db_path()),
        "boundaries": handoff_boundaries(),
        "blocked_actions": LOCKED_ACTIONS,
    }


__all__ = [
    "HANDOFF_VERSION",
    "HANDOFF_SCHEMA_VERSION",
    "init_handoff_db",
    "create_candidate_decision_handoff",
    "get_candidate_decision_handoff",
    "update_candidate_decision_handoff",
    "list_candidate_decision_handoffs",
    "handoff_overview",
    "handoff_status_payload",
    "handoff_boundaries",
]
