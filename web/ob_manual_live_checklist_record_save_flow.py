# OB_GIANT_PACK_042_REAL_CHECKLIST_TO_RECORD_SAVE_FLOW_SERVICE
"""
OB GP042 — Real Checklist-to-Record Save Flow.

Boundaries:
- no broker order submission
- no real capital movement
- no direct Vault upload
- Manual Live Level 1 remains owner-controlled
- Live Auto remains locked
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import inspect
import json
import os
import sqlite3
import uuid

from web import (
    ob_manual_live_dry_run_persistence
    as persistence
)

from web import (
    ob_manual_live_candidate_decision_handoff
    as handoff_service
)

from web import (
    ob_manual_live_dry_run_history
    as history
)


REQUIRED_CHECKS = (
    "candidate_reviewed",
    "risk_reviewed",
    "account_lane_confirmed",
    "capital_boundary_confirmed",
    "live_lock_acknowledged",
    "no_broker_order_acknowledged",
)


BOUNDARIES = {
    "order_submit_enabled": False,
    "broker_api_enabled": False,
    "capital_movement_enabled": False,
    "direct_vault_upload_enabled": False,
    "live_auto_locked": True,
}


def _utc_now():
    return datetime.now(
        timezone.utc
    ).isoformat()


def _canonical(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _sha256(value):
    return hashlib.sha256(
        _canonical(value).encode("utf-8")
    ).hexdigest()


def _db_path(path=None):
    if path:
        database = Path(path)

    elif os.environ.get(
        "OB_DRY_RUN_DB_PATH"
    ):
        database = Path(
            os.environ[
                "OB_DRY_RUN_DB_PATH"
            ]
        )

    else:
        candidate = getattr(
            persistence,
            "db_path",
            None,
        )

        if callable(candidate):
            database = Path(candidate())
        else:
            database = (
                Path(__file__)
                .resolve()
                .parents[1]
                / "data"
                / "ob_manual_live_dry_run.sqlite3"
            )

    database.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return database


def _connect(path=None):
    conn = sqlite3.connect(
        _db_path(path)
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_flow_db(path=None):
    with _connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS
            ob_manual_live_checklist_record_save_flows (
                flow_id TEXT PRIMARY KEY,
                handoff_id TEXT NOT NULL,
                evidence_record_id TEXT NOT NULL,
                candidate_id TEXT,
                symbol TEXT,
                owner_id TEXT,
                dry_run_outcome TEXT NOT NULL,
                checklist_json TEXT NOT NULL,
                checklist_score INTEGER NOT NULL,
                checklist_passed INTEGER NOT NULL,
                checklist_snapshot_hash TEXT NOT NULL,
                flow_hash TEXT NOT NULL,
                boundaries_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_gp042_flow_handoff
            ON
            ob_manual_live_checklist_record_save_flows (
                handoff_id
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_gp042_flow_symbol
            ON
            ob_manual_live_checklist_record_save_flows (
                symbol,
                created_at
            )
            """
        )

        conn.commit()

    history.init_gp042_review_event_db(
        path
    )

    return str(_db_path(path))


def _unwrap(value, keys):
    if not isinstance(value, dict):
        return value

    for key in keys:
        candidate = value.get(key)

        if isinstance(candidate, dict):
            return candidate

    return value


def _call_path_aware(
    function,
    positional,
    path=None,
    keyword_payload=None,
):
    attempts = []

    if path is not None:
        attempts.extend(
            [
                lambda: function(
                    *positional,
                    path=path,
                ),
                lambda: function(
                    *positional,
                    path,
                ),
            ]
        )

    attempts.append(
        lambda: function(*positional)
    )

    if keyword_payload:
        try:
            signature = inspect.signature(
                function
            )

            accepted = {
                name: value
                for name, value
                in keyword_payload.items()
                if name in signature.parameters
            }

            if (
                path is not None
                and "path"
                in signature.parameters
            ):
                accepted["path"] = path

            if accepted:
                attempts.append(
                    lambda: function(
                        **accepted
                    )
                )

        except Exception:
            pass

    last_error = None

    for attempt in attempts:
        try:
            return attempt()
        except TypeError as exc:
            last_error = exc

    if last_error:
        raise last_error

    raise RuntimeError(
        "No compatible invocation was found."
    )


def _get_handoff(handoff_id, path=None):
    names = (
        "get_candidate_decision_handoff",
        "get_decision_handoff",
        "get_handoff",
    )

    for name in names:
        function = getattr(
            handoff_service,
            name,
            None,
        )

        if not callable(function):
            continue

        result = _call_path_aware(
            function,
            (handoff_id,),
            path=path,
            keyword_payload={
                "handoff_id": handoff_id,
            },
        )

        result = _unwrap(
            result,
            (
                "handoff",
                "decision_handoff",
                "record",
            ),
        )

        if isinstance(result, dict):
            return result

    raise LookupError(
        f"Candidate decision handoff "
        f"not found: {handoff_id}"
    )


def _demo_payload(symbol):
    function = getattr(
        persistence,
        "build_demo_payload",
        None,
    )

    if not callable(function):
        return {}

    attempts = (
        lambda: function(
            symbol=symbol
        ),
        lambda: function(symbol),
        lambda: function(),
    )

    for attempt in attempts:
        try:
            result = attempt()

            if isinstance(result, dict):
                return result

        except TypeError:
            continue

    return {}


def _create_evidence_record(
    handoff,
    handoff_id,
    payload,
    checklist,
    checklist_score,
    checklist_passed,
    path=None,
):
    candidate = handoff.get(
        "candidate",
        {}
    )

    if not isinstance(candidate, dict):
        candidate = {}

    symbol = (
        candidate.get("symbol")
        or handoff.get("symbol")
        or payload.get("symbol")
        or "UNKNOWN"
    )

    outcome = (
        payload.get("dry_run_outcome")
        or payload.get("outcome")
        or "not_placed"
    )

    evidence_payload = _demo_payload(
        symbol
    )

    evidence_payload.update(
        {
            "record_type": (
                "manual_live_checklist_record"
            ),
            "mode": (
                "manual_live_level_1_dry_run"
            ),
            "symbol": symbol,
            "candidate_id": (
                candidate.get(
                    "candidate_id"
                )
                or handoff.get(
                    "candidate_id"
                )
            ),
            "handoff_id": handoff_id,
            "owner_id": (
                payload.get("owner_id")
                or handoff.get("owner_id")
                or "owner"
            ),
            "strategy": (
                candidate.get("strategy")
                or "manual_live_review"
            ),
            "direction": (
                candidate.get("direction")
                or candidate.get("side")
                or "watch"
            ),
            "decision_status": (
                handoff.get(
                    "decision_status"
                )
                or "owner_reviewed"
            ),
            "dry_run_outcome": outcome,
            "outcome": outcome,
            "checklist": checklist,
            "checklist_score": (
                checklist_score
            ),
            "checklist_passed": (
                checklist_passed
            ),
            "notes": (
                checklist.get(
                    "owner_notes"
                )
                or payload.get("notes")
                or (
                    "GP042 checklist-to-record "
                    "save flow."
                )
            ),
            "source": "ob_gp042",
            "submitted_at": _utc_now(),
            "live_order_submitted": False,
            "broker_order_id": None,
            "capital_moved": False,
            "direct_vault_upload": False,
        }
    )

    function = getattr(
        persistence,
        "create_dry_run_record",
        None,
    )

    if not callable(function):
        raise RuntimeError(
            "GP036 create_dry_run_record "
            "is unavailable."
        )

    result = _call_path_aware(
        function,
        (evidence_payload,),
        path=path,
        keyword_payload={
            "payload": evidence_payload,
            "record": evidence_payload,
            "data": evidence_payload,
        },
    )

    record = _unwrap(
        result,
        (
            "record",
            "dry_run_record",
            "evidence_record",
        ),
    )

    if not isinstance(record, dict):
        raise RuntimeError(
            "GP036 did not return a record."
        )

    record_id = (
        record.get("record_id")
        or record.get(
            "dry_run_record_id"
        )
        or record.get(
            "evidence_record_id"
        )
        or record.get("id")
    )

    if not record_id:
        raise RuntimeError(
            "GP036 evidence record has no ID."
        )

    return record, str(record_id)


def _decode_row(row):
    result = dict(row)

    for source, target in (
        (
            "checklist_json",
            "checklist",
        ),
        (
            "boundaries_json",
            "boundaries",
        ),
    ):
        raw = result.pop(
            source,
            "{}",
        )

        try:
            result[target] = json.loads(raw)
        except Exception:
            result[target] = {}

    result["checklist_passed"] = bool(
        result.get(
            "checklist_passed"
        )
    )

    result["locks"] = {
        "broker_order_submitted": False,
        "real_capital_moved": False,
        "direct_vault_upload": False,
        "live_auto_enabled": False,
    }

    return result


def create_checklist_record_save_flow(
    handoff_id,
    payload=None,
    path=None,
):
    init_flow_db(path)

    payload = dict(payload or {})

    handoff = _get_handoff(
        handoff_id,
        path=path,
    )

    checklist = dict(
        payload.get("checklist")
        or {}
    )

    completed = sum(
        1
        for key in REQUIRED_CHECKS
        if checklist.get(key) is True
    )

    checklist_score = round(
        completed
        / len(REQUIRED_CHECKS)
        * 100
    )

    checklist_passed = (
        completed
        == len(REQUIRED_CHECKS)
    )

    if not checklist_passed:
        missing = [
            key
            for key in REQUIRED_CHECKS
            if checklist.get(key)
            is not True
        ]

        return {
            "ok": False,
            "created": False,
            "error": (
                "required_checklist_items_missing"
            ),
            "missing": missing,
            "checklist_score": (
                checklist_score
            ),
        }

    evidence, evidence_record_id = (
        _create_evidence_record(
            handoff=handoff,
            handoff_id=handoff_id,
            payload=payload,
            checklist=checklist,
            checklist_score=checklist_score,
            checklist_passed=(
                checklist_passed
            ),
            path=path,
        )
    )

    candidate = handoff.get(
        "candidate",
        {}
    )

    if not isinstance(candidate, dict):
        candidate = {}

    candidate_id = (
        candidate.get("candidate_id")
        or handoff.get("candidate_id")
    )

    symbol = (
        candidate.get("symbol")
        or handoff.get("symbol")
        or evidence.get("symbol")
        or "UNKNOWN"
    )

    owner_id = (
        payload.get("owner_id")
        or handoff.get("owner_id")
        or "owner"
    )

    outcome = (
        payload.get("dry_run_outcome")
        or payload.get("outcome")
        or "not_placed"
    )

    timestamp = _utc_now()

    snapshot = {
        "handoff_id": handoff_id,
        "evidence_record_id": (
            evidence_record_id
        ),
        "candidate_id": candidate_id,
        "symbol": symbol,
        "owner_id": owner_id,
        "dry_run_outcome": outcome,
        "checklist": checklist,
        "checklist_score": (
            checklist_score
        ),
        "checklist_passed": (
            checklist_passed
        ),
        "boundaries": BOUNDARIES,
        "created_at": timestamp,
    }

    checklist_snapshot_hash = _sha256(
        {
            "handoff_id": handoff_id,
            "checklist": checklist,
            "score": checklist_score,
        }
    )

    flow_hash = _sha256(
        {
            **snapshot,
            "checklist_snapshot_hash": (
                checklist_snapshot_hash
            ),
        }
    )

    flow = {
        "flow_id": (
            "ob-gp042-flow-"
            + uuid.uuid4().hex
        ),
        **snapshot,
        "checklist_snapshot_hash": (
            checklist_snapshot_hash
        ),
        "flow_hash": flow_hash,
        "updated_at": timestamp,
    }

    with _connect(path) as conn:
        conn.execute(
            """
            INSERT INTO
            ob_manual_live_checklist_record_save_flows (
                flow_id,
                handoff_id,
                evidence_record_id,
                candidate_id,
                symbol,
                owner_id,
                dry_run_outcome,
                checklist_json,
                checklist_score,
                checklist_passed,
                checklist_snapshot_hash,
                flow_hash,
                boundaries_json,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?
            )
            """,
            (
                flow["flow_id"],
                flow["handoff_id"],
                flow[
                    "evidence_record_id"
                ],
                flow["candidate_id"],
                flow["symbol"],
                flow["owner_id"],
                flow["dry_run_outcome"],
                _canonical(
                    flow["checklist"]
                ),
                flow["checklist_score"],
                int(
                    flow[
                        "checklist_passed"
                    ]
                ),
                flow[
                    "checklist_snapshot_hash"
                ],
                flow["flow_hash"],
                _canonical(
                    flow["boundaries"]
                ),
                flow["created_at"],
                flow["updated_at"],
            ),
        )

        conn.commit()

    event = history.record_gp042_review_event(
        evidence_record_id,
        "checklist_record_saved",
        {
            "flow_id": flow["flow_id"],
            "handoff_id": handoff_id,
            "symbol": symbol,
            "dry_run_outcome": outcome,
            "checklist_score": (
                checklist_score
            ),
            "flow_hash": flow_hash,
            "order_submit_enabled": False,
            "capital_movement_enabled": False,
            "direct_vault_upload_enabled": False,
            "live_auto_locked": True,
        },
        path=path,
    )

    flow["review_event_id"] = (
        event["event_id"]
    )

    flow["locks"] = {
        "broker_order_submitted": False,
        "real_capital_moved": False,
        "direct_vault_upload": False,
        "live_auto_enabled": False,
    }

    return {
        "ok": True,
        "created": True,
        "flow": flow,
        "evidence_record": evidence,
        "review_event": event,
    }


def get_checklist_record_save_flow(
    flow_id,
    path=None,
):
    init_flow_db(path)

    with _connect(path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM
                ob_manual_live_checklist_record_save_flows
            WHERE
                flow_id = ?
            """,
            (str(flow_id),),
        ).fetchone()

    if row is None:
        return None

    return _decode_row(row)


def list_checklist_record_save_flows(
    symbol=None,
    handoff_id=None,
    limit=100,
    path=None,
):
    init_flow_db(path)

    clauses = []
    values = []

    if symbol:
        clauses.append(
            "symbol = ?"
        )
        values.append(
            str(symbol).upper()
        )

    if handoff_id:
        clauses.append(
            "handoff_id = ?"
        )
        values.append(
            str(handoff_id)
        )

    where = ""

    if clauses:
        where = (
            "WHERE "
            + " AND ".join(clauses)
        )

    safe_limit = max(
        1,
        min(
            int(limit or 100),
            300,
        ),
    )

    values.append(safe_limit)

    with _connect(path) as conn:
        rows = conn.execute(
            f"""
            SELECT *
            FROM
                ob_manual_live_checklist_record_save_flows
            {where}
            ORDER BY
                created_at DESC
            LIMIT ?
            """,
            values,
        ).fetchall()

    return [
        _decode_row(row)
        for row in rows
    ]


def flow_overview(
    symbol=None,
    path=None,
):
    flows = list_checklist_record_save_flows(
        symbol=symbol,
        limit=300,
        path=path,
    )

    return {
        "flow_count": len(flows),
        "passed_count": sum(
            1
            for flow in flows
            if flow.get(
                "checklist_passed"
            )
        ),
        "not_placed_count": sum(
            1
            for flow in flows
            if flow.get(
                "dry_run_outcome"
            )
            == "not_placed"
        ),
        "symbols": sorted(
            {
                flow.get("symbol")
                for flow in flows
                if flow.get("symbol")
            }
        ),
        "boundaries": dict(
            BOUNDARIES
        ),
        "latest_flow": (
            flows[0]
            if flows
            else None
        ),
    }


__all__ = [
    "BOUNDARIES",
    "REQUIRED_CHECKS",
    "init_flow_db",
    "create_checklist_record_save_flow",
    "get_checklist_record_save_flow",
    "list_checklist_record_save_flows",
    "flow_overview",
]
