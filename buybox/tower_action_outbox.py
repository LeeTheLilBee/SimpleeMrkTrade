"""BBX022-026: durable, source-bound, strictly UNSENT Tower action draft outbox.

This is local preparation, not a Tower transport, request authorization, status
callback, or receipt inbox. A row can only be PREPARED_UNSENT, STALE_LOCAL, or
EXPIRED_LOCAL. No function can mark it approved, sent, funded, archived or ready.

The caller must provide a fresh SQLite connection with no active transaction;
each operation uses BEGIN IMMEDIATE to couple source inspection, idempotency and
state changes. The backing file is only suitable for a separately certified
private durable BuyBox store. Test databases are synthetic.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any

from .tower_action_draft import (
    BuyBoxTowerActionPreparationError,
    prepare_untrusted_tower_action_draft,
    stored_source_snapshot,
)

SCHEMA_VERSION = "buybox.tower.action.outbox.v1"
PENDING = "PREPARED_UNSENT"
STALE = "STALE_LOCAL"
EXPIRED = "EXPIRED_LOCAL"
KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{7,127}$")
_TABLE = """
CREATE TABLE IF NOT EXISTS buybox_tower_action_drafts (
    idempotency_key TEXT PRIMARY KEY,
    request_id TEXT NOT NULL UNIQUE,
    opportunity_id TEXT NOT NULL,
    opportunity_revision INTEGER NOT NULL,
    input_snapshot_digest TEXT NOT NULL,
    requested_action TEXT NOT NULL,
    parameter_fingerprint TEXT NOT NULL,
    packet_sha256 TEXT NOT NULL,
    packet_json TEXT NOT NULL,
    valid_until_epoch INTEGER NOT NULL,
    prepared_at_epoch INTEGER NOT NULL,
    state TEXT NOT NULL CHECK(
        state IN ('PREPARED_UNSENT','STALE_LOCAL','EXPIRED_LOCAL')
    ),
    terminal_at_epoch INTEGER,
    terminal_reason TEXT
);
CREATE INDEX IF NOT EXISTS idx_buybox_action_drafts_opportunity
ON buybox_tower_action_drafts(opportunity_id, state);
"""


class BuyBoxActionOutboxError(ValueError):
    """A local state or idempotency failure, never a Tower denial or grant."""


def _epoch(now_utc: datetime | None) -> int:
    value = now_utc if now_utc is not None else datetime.now(timezone.utc)
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise BuyBoxActionOutboxError("UTC_TIME_REQUIRED")
    return int(value.astimezone(timezone.utc).timestamp())


def _canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _params(
    opportunity_id: str,
    requested_action: str,
    claimed_identity_ref: str,
    claimed_entity_ref: str,
    classification: str,
) -> dict[str, str]:
    return {
        "opportunity_id": opportunity_id,
        "requested_action": requested_action,
        "claimed_identity_ref": claimed_identity_ref,
        "claimed_entity_ref": claimed_entity_ref,
        "classification": classification,
    }


def _begin(db: sqlite3.Connection) -> None:
    if not isinstance(db, sqlite3.Connection) or db.in_transaction:
        raise BuyBoxActionOutboxError("FRESH_DATABASE_TRANSACTION_REQUIRED")
    db.execute("BEGIN IMMEDIATE")
    for statement in _TABLE.strip().split(";"):
        if statement.strip():
            db.execute(statement)


def _close(db: sqlite3.Connection, row: sqlite3.Row, state: str,
           reason: str, now_epoch: int) -> None:
    db.execute(
        "UPDATE buybox_tower_action_drafts "
        "SET state=?, terminal_at_epoch=?, terminal_reason=? "
        "WHERE idempotency_key=? AND state=?",
        (state, now_epoch, reason, row["idempotency_key"], PENDING),
    )


def _summary(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": row["request_id"],
        "idempotency_key": row["idempotency_key"],
        "opportunity_id": row["opportunity_id"],
        "opportunity_revision": row["opportunity_revision"],
        "input_snapshot_digest": row["input_snapshot_digest"],
        "requested_action": row["requested_action"],
        "packet_sha256": row["packet_sha256"],
        "state": row["state"],
        "terminal_reason": row["terminal_reason"],
        "authorizes_action": False,
        "submitted_to_tower": False,
        "tower_receipt_present": False,
        "teller_readiness": "UNKNOWN",
    }


def _current_source(db: sqlite3.Connection, opportunity_id: str) -> dict[str, Any] | None:
    try:
        return stored_source_snapshot(db, opportunity_id)
    except (BuyBoxTowerActionPreparationError, sqlite3.DatabaseError):
        return None


def _reconcile_one(db: sqlite3.Connection, row: sqlite3.Row,
                   current: dict[str, Any] | None, now_epoch: int) -> dict[str, Any]:
    if row["state"] != PENDING:
        return _summary(row)
    if current is None or any(
        row[field] != current[field]
        for field in ("opportunity_id", "opportunity_revision", "input_snapshot_digest")
    ):
        _close(db, row, STALE, "CURRENT_SOURCE_CHANGED_OR_UNAVAILABLE", now_epoch)
    elif now_epoch >= row["valid_until_epoch"]:
        _close(db, row, EXPIRED, "LOCAL_DRAFT_EXPIRED", now_epoch)
    updated = db.execute(
        "SELECT * FROM buybox_tower_action_drafts WHERE idempotency_key=?",
        (row["idempotency_key"],),
    ).fetchone()
    return _summary(updated)


def prepare_local_tower_action_draft(
    db: sqlite3.Connection, opportunity_id: str, *,
    requested_action: str,
    claimed_identity_ref: str,
    claimed_entity_ref: str,
    classification: str,
    idempotency_key: str,
    now_utc: datetime | None = None,
    lifetime_seconds: int = 120,
) -> dict[str, Any]:
    """Atomically pin source, preserve one local request per exact retry key.

    Reusing a key for another request is a conflict; reusing it after source
    change/expiry returns a permanent local terminal state. A fresh key is
    needed for a new snapshot. A retry never renews an old draft's expiry.
    """
    if not isinstance(idempotency_key, str) or KEY.fullmatch(idempotency_key) is None:
        raise BuyBoxActionOutboxError("IDEMPOTENCY_KEY_INVALID")
    now_epoch = _epoch(now_utc)
    params = _params(
        opportunity_id, requested_action, claimed_identity_ref,
        claimed_entity_ref, classification,
    )
    fingerprint = _digest(params)
    _begin(db)
    try:
        existing = db.execute(
            "SELECT * FROM buybox_tower_action_drafts WHERE idempotency_key=?",
            (idempotency_key,),
        ).fetchone()
        if existing is not None:
            if existing["parameter_fingerprint"] != fingerprint:
                raise BuyBoxActionOutboxError("IDEMPOTENCY_KEY_CONFLICT")
            response = _reconcile_one(
                db, existing, _current_source(db, existing["opportunity_id"]), now_epoch,
            )
            db.commit()
            return response

        prepared = prepare_untrusted_tower_action_draft(
            db, opportunity_id, requested_action=requested_action,
            claimed_identity_ref=claimed_identity_ref,
            claimed_entity_ref=claimed_entity_ref,
            classification=classification,
            now_utc=now_utc,
            lifetime_seconds=lifetime_seconds,
        )
        if prepared["state"] != "UNTRUSTED_DRAFT" or prepared["authorizes_action"] is not False:
            raise BuyBoxActionOutboxError("SOURCE_DRAFT_NOT_UNTRUSTED")
        packet = prepared["packet"]
        if packet["opportunity_id"] != opportunity_id:
            raise BuyBoxActionOutboxError("SOURCE_IDENTITY_MISMATCH")
        expires_at = datetime.fromisoformat(packet["valid_until"].replace("Z", "+00:00"))
        expires_epoch = int(expires_at.timestamp())
        if expires_epoch <= now_epoch:
            raise BuyBoxActionOutboxError("LOCAL_DRAFT_ALREADY_EXPIRED")
        payload = _canonical(packet)
        packet_sha = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        db.execute(
            "INSERT INTO buybox_tower_action_drafts VALUES "
            "(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                idempotency_key, packet["request_id"], opportunity_id,
                packet["opportunity_revision"], packet["input_snapshot_digest"],
                requested_action, fingerprint, packet_sha, payload,
                expires_epoch, now_epoch, PENDING, None, None,
            ),
        )
        row = db.execute(
            "SELECT * FROM buybox_tower_action_drafts WHERE idempotency_key=?",
            (idempotency_key,),
        ).fetchone()
        result = _summary(row)
        db.commit()
        return result
    except BaseException:
        db.rollback()
        raise


def reconcile_local_tower_action_drafts(
    db: sqlite3.Connection, opportunity_id: str, *,
    now_utc: datetime | None = None,
) -> list[dict[str, Any]]:
    """Recompute local state from a real current persisted source.

    Missing/corrupt stored source makes every outstanding local draft stale.
    Historical packets/digests stay immutable. No outbound call is made.
    """
    now_epoch = _epoch(now_utc)
    _begin(db)
    try:
        rows = db.execute(
            "SELECT * FROM buybox_tower_action_drafts "
            "WHERE opportunity_id=? ORDER BY prepared_at_epoch, request_id",
            (opportunity_id,),
        ).fetchall()
        current = _current_source(db, opportunity_id)
        results = [_reconcile_one(db, row, current, now_epoch) for row in rows]
        db.commit()
        return results
    except BaseException:
        db.rollback()
        raise


def read_local_tower_action_draft(
    db: sqlite3.Connection, idempotency_key: str, *,
    now_utc: datetime | None = None,
) -> dict[str, Any] | None:
    """Return a safe local summary only after fresh source/expiry reconciliation."""
    now_epoch = _epoch(now_utc)
    _begin(db)
    try:
        row = db.execute(
            "SELECT * FROM buybox_tower_action_drafts WHERE idempotency_key=?",
            (idempotency_key,),
        ).fetchone()
        result = None if row is None else _reconcile_one(
            db, row, _current_source(db, row["opportunity_id"]), now_epoch,
        )
        db.commit()
        return result
    except BaseException:
        db.rollback()
        raise
