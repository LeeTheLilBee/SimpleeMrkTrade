# OB_GIANT_PACK_043_REAL_DRY_RUN_OUTCOME_FINALIZATION_SERVICE
"""
OB GP043 — Real Dry-Run Outcome Finalization.

Finalizes one GP042 checklist-to-record flow into one durable,
immutable dry-run outcome.

Supported outcomes:
- not_placed
- fake_fill
- cancelled
- needs_review
- blocked_live

Boundaries:
- no broker order submission
- no real capital movement
- no direct Vault upload
- no Live Auto activation
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
    ob_manual_live_checklist_record_save_flow
    as gp042_flow
)

from web import (
    ob_manual_live_dry_run_history
    as history
)


SERVICE_VERSION = "gp043"

ALLOWED_OUTCOMES = (
    "not_placed",
    "fake_fill",
    "cancelled",
    "needs_review",
    "blocked_live",
)

LIVE_ACTION_FLAGS = (
    "broker_order_submitted",
    "order_submitted",
    "real_order_submitted",
    "capital_moved",
    "real_capital_moved",
    "direct_vault_upload",
    "live_auto_enabled",
    "automated_execution_enabled",
)

BOUNDARIES = {
    "broker_order_submission_enabled": False,
    "real_capital_movement_enabled": False,
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
        _canonical(value).encode(
            "utf-8"
        )
    ).hexdigest()


def _database_path(path=None):
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
        _database_path(path)
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_outcome_finalization_db(
    path=None,
):
    with _connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS
            ob_manual_live_dry_run_outcome_finalizations (
                finalization_id TEXT PRIMARY KEY,
                flow_id TEXT NOT NULL UNIQUE,
                handoff_id TEXT,
                evidence_record_id TEXT,
                candidate_id TEXT,
                symbol TEXT,
                owner_id TEXT,
                final_outcome TEXT NOT NULL,
                reason TEXT NOT NULL,
                notes TEXT,
                simulated_price REAL,
                simulated_quantity REAL,
                simulated_side TEXT,
                checklist_score INTEGER,
                checklist_passed INTEGER,
                checklist_snapshot_hash TEXT,
                flow_hash TEXT,
                finalization_hash TEXT NOT NULL,
                broker_order_submitted INTEGER NOT NULL,
                real_capital_moved INTEGER NOT NULL,
                direct_vault_upload INTEGER NOT NULL,
                live_auto_enabled INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_gp043_finalization_symbol
            ON
            ob_manual_live_dry_run_outcome_finalizations (
                symbol,
                created_at
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_gp043_finalization_outcome
            ON
            ob_manual_live_dry_run_outcome_finalizations (
                final_outcome,
                created_at
            )
            """
        )

        conn.commit()

    return str(
        _database_path(path)
    )


def _call_path_aware(
    function,
    positional,
    path=None,
    keyword_values=None,
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
        lambda: function(
            *positional
        )
    )

    if keyword_values:
        try:
            signature = inspect.signature(
                function
            )

            accepted = {
                key: value
                for key, value
                in keyword_values.items()
                if key in signature.parameters
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
        "No compatible service invocation."
    )


def _get_flow(
    flow_id,
    path=None,
):
    function = getattr(
        gp042_flow,
        "get_checklist_record_save_flow",
        None,
    )

    if not callable(function):
        raise RuntimeError(
            "GP042 flow getter is unavailable."
        )

    result = _call_path_aware(
        function,
        (flow_id,),
        path=path,
        keyword_values={
            "flow_id": flow_id,
        },
    )

    if isinstance(result, dict):
        for key in (
            "flow",
            "record_save_flow",
            "record",
        ):
            candidate = result.get(key)

            if isinstance(
                candidate,
                dict,
            ):
                return candidate

        return result

    raise LookupError(
        "GP042 flow not found: "
        + str(flow_id)
    )


def _normalize_outcome(value):
    normalized = str(
        value or ""
    ).strip().lower()

    normalized = (
        normalized
        .replace("-", "_")
        .replace(" ", "_")
    )

    aliases = {
        "notplaced": "not_placed",
        "fakefill": "fake_fill",
        "blocked": "blocked_live",
        "review": "needs_review",
    }

    normalized = aliases.get(
        normalized,
        normalized,
    )

    return normalized


def _positive_float(
    value,
    field_name,
):
    try:
        converted = float(value)
    except Exception as exc:
        raise ValueError(
            f"{field_name} must be numeric."
        ) from exc

    if converted <= 0:
        raise ValueError(
            f"{field_name} must be greater than zero."
        )

    return converted


def _live_flags_requested(payload):
    return sorted(
        key
        for key in LIVE_ACTION_FLAGS
        if payload.get(key) is True
    )


def _decode_row(row):
    result = dict(row)

    for key in (
        "checklist_passed",
        "broker_order_submitted",
        "real_capital_moved",
        "direct_vault_upload",
        "live_auto_enabled",
    ):
        result[key] = bool(
            result.get(key)
        )

    result["simulated_fill"] = {
        "price": result.get(
            "simulated_price"
        ),
        "quantity": result.get(
            "simulated_quantity"
        ),
        "side": result.get(
            "simulated_side"
        ),
        "is_real_market_execution": False,
    }

    result["boundaries"] = dict(
        BOUNDARIES
    )

    return result


def _hash_basis(finalization):
    return {
        "service_version": (
            SERVICE_VERSION
        ),
        "finalization_id": (
            finalization.get(
                "finalization_id"
            )
        ),
        "flow_id": finalization.get(
            "flow_id"
        ),
        "handoff_id": (
            finalization.get(
                "handoff_id"
            )
        ),
        "evidence_record_id": (
            finalization.get(
                "evidence_record_id"
            )
        ),
        "candidate_id": (
            finalization.get(
                "candidate_id"
            )
        ),
        "symbol": finalization.get(
            "symbol"
        ),
        "owner_id": finalization.get(
            "owner_id"
        ),
        "final_outcome": (
            finalization.get(
                "final_outcome"
            )
        ),
        "reason": finalization.get(
            "reason"
        ),
        "notes": finalization.get(
            "notes"
        ),
        "simulated_price": (
            finalization.get(
                "simulated_price"
            )
        ),
        "simulated_quantity": (
            finalization.get(
                "simulated_quantity"
            )
        ),
        "simulated_side": (
            finalization.get(
                "simulated_side"
            )
        ),
        "checklist_score": (
            finalization.get(
                "checklist_score"
            )
        ),
        "checklist_passed": bool(
            finalization.get(
                "checklist_passed"
            )
        ),
        "checklist_snapshot_hash": (
            finalization.get(
                "checklist_snapshot_hash"
            )
        ),
        "flow_hash": finalization.get(
            "flow_hash"
        ),
        "broker_order_submitted": False,
        "real_capital_moved": False,
        "direct_vault_upload": False,
        "live_auto_enabled": False,
        "created_at": finalization.get(
            "created_at"
        ),
    }


def finalize_dry_run_outcome(
    flow_id,
    payload=None,
    path=None,
):
    init_outcome_finalization_db(
        path
    )

    payload = dict(payload or {})

    requested_live_flags = (
        _live_flags_requested(
            payload
        )
    )

    if requested_live_flags:
        return {
            "ok": False,
            "created": False,
            "error": (
                "live_action_flags_rejected"
            ),
            "rejected_flags": (
                requested_live_flags
            ),
            "boundaries": dict(
                BOUNDARIES
            ),
        }

    final_outcome = _normalize_outcome(
        payload.get(
            "final_outcome"
        )
        or payload.get("outcome")
        or payload.get(
            "dry_run_outcome"
        )
    )

    if final_outcome not in (
        ALLOWED_OUTCOMES
    ):
        return {
            "ok": False,
            "created": False,
            "error": (
                "unsupported_final_outcome"
            ),
            "allowed_outcomes": list(
                ALLOWED_OUTCOMES
            ),
        }

    existing = (
        get_dry_run_outcome_finalization_by_flow(
            flow_id,
            path=path,
        )
    )

    if existing is not None:
        if (
            existing.get(
                "final_outcome"
            )
            == final_outcome
        ):
            return {
                "ok": True,
                "created": False,
                "idempotent": True,
                "finalization": existing,
            }

        return {
            "ok": False,
            "created": False,
            "idempotent": False,
            "error": (
                "flow_already_finalized"
            ),
            "existing_finalization": (
                existing
            ),
        }

    flow = _get_flow(
        flow_id,
        path=path,
    )

    if not bool(
        flow.get(
            "checklist_passed"
        )
    ):
        return {
            "ok": False,
            "created": False,
            "error": (
                "gp042_checklist_not_passed"
            ),
            "flow_id": str(flow_id),
        }

    reason = str(
        payload.get("reason")
        or payload.get(
            "outcome_reason"
        )
        or ""
    ).strip()

    default_reasons = {
        "not_placed": (
            "Owner chose not to place "
            "the dry-run candidate."
        ),
        "fake_fill": (
            "A simulated fill was recorded "
            "for rehearsal only."
        ),
        "cancelled": (
            "The dry-run workflow was cancelled."
        ),
        "needs_review": (
            "The dry-run workflow requires "
            "additional owner review."
        ),
        "blocked_live": (
            "Live execution remained blocked "
            "by the operating boundary."
        ),
    }

    if not reason:
        reason = default_reasons[
            final_outcome
        ]

    notes = str(
        payload.get("notes")
        or payload.get(
            "owner_notes"
        )
        or ""
    ).strip()

    simulated_price = None
    simulated_quantity = None
    simulated_side = None

    simulated_fill = payload.get(
        "simulated_fill"
    )

    if not isinstance(
        simulated_fill,
        dict,
    ):
        simulated_fill = {}

    if final_outcome == "fake_fill":
        simulated_price = (
            simulated_fill.get("price")
            if simulated_fill.get(
                "price"
            )
            is not None
            else payload.get(
                "simulated_price"
            )
        )

        simulated_quantity = (
            simulated_fill.get(
                "quantity"
            )
            if simulated_fill.get(
                "quantity"
            )
            is not None
            else payload.get(
                "simulated_quantity"
            )
        )

        simulated_side = str(
            simulated_fill.get("side")
            or payload.get(
                "simulated_side"
            )
            or "buy"
        ).strip().lower()

        if simulated_side not in (
            "buy",
            "sell",
        ):
            return {
                "ok": False,
                "created": False,
                "error": (
                    "invalid_simulated_side"
                ),
                "allowed_sides": [
                    "buy",
                    "sell",
                ],
            }

        try:
            simulated_price = (
                _positive_float(
                    simulated_price,
                    "simulated_price",
                )
            )

            simulated_quantity = (
                _positive_float(
                    simulated_quantity,
                    "simulated_quantity",
                )
            )

        except ValueError as exc:
            return {
                "ok": False,
                "created": False,
                "error": (
                    "invalid_simulated_fill"
                ),
                "message": str(exc),
            }

    timestamp = _utc_now()

    finalization = {
        "finalization_id": (
            "ob-gp043-finalization-"
            + uuid.uuid4().hex
        ),
        "flow_id": str(flow_id),
        "handoff_id": flow.get(
            "handoff_id"
        ),
        "evidence_record_id": flow.get(
            "evidence_record_id"
        ),
        "candidate_id": flow.get(
            "candidate_id"
        ),
        "symbol": flow.get("symbol"),
        "owner_id": (
            payload.get("owner_id")
            or flow.get("owner_id")
            or "owner"
        ),
        "final_outcome": (
            final_outcome
        ),
        "reason": reason,
        "notes": notes,
        "simulated_price": (
            simulated_price
        ),
        "simulated_quantity": (
            simulated_quantity
        ),
        "simulated_side": (
            simulated_side
        ),
        "checklist_score": (
            flow.get(
                "checklist_score"
            )
        ),
        "checklist_passed": bool(
            flow.get(
                "checklist_passed"
            )
        ),
        "checklist_snapshot_hash": (
            flow.get(
                "checklist_snapshot_hash"
            )
        ),
        "flow_hash": flow.get(
            "flow_hash"
        ),
        "broker_order_submitted": False,
        "real_capital_moved": False,
        "direct_vault_upload": False,
        "live_auto_enabled": False,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    finalization_hash = _sha256(
        _hash_basis(finalization)
    )

    finalization[
        "finalization_hash"
    ] = finalization_hash

    with _connect(path) as conn:
        conn.execute(
            """
            INSERT INTO
            ob_manual_live_dry_run_outcome_finalizations (
                finalization_id,
                flow_id,
                handoff_id,
                evidence_record_id,
                candidate_id,
                symbol,
                owner_id,
                final_outcome,
                reason,
                notes,
                simulated_price,
                simulated_quantity,
                simulated_side,
                checklist_score,
                checklist_passed,
                checklist_snapshot_hash,
                flow_hash,
                finalization_hash,
                broker_order_submitted,
                real_capital_moved,
                direct_vault_upload,
                live_auto_enabled,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?
            )
            """,
            (
                finalization[
                    "finalization_id"
                ],
                finalization["flow_id"],
                finalization.get(
                    "handoff_id"
                ),
                finalization.get(
                    "evidence_record_id"
                ),
                finalization.get(
                    "candidate_id"
                ),
                finalization.get(
                    "symbol"
                ),
                finalization.get(
                    "owner_id"
                ),
                finalization[
                    "final_outcome"
                ],
                finalization["reason"],
                finalization["notes"],
                finalization.get(
                    "simulated_price"
                ),
                finalization.get(
                    "simulated_quantity"
                ),
                finalization.get(
                    "simulated_side"
                ),
                finalization.get(
                    "checklist_score"
                ),
                int(
                    finalization[
                        "checklist_passed"
                    ]
                ),
                finalization.get(
                    "checklist_snapshot_hash"
                ),
                finalization.get(
                    "flow_hash"
                ),
                finalization_hash,
                0,
                0,
                0,
                0,
                timestamp,
                timestamp,
            ),
        )

        conn.commit()

    review_event = None

    event_function = getattr(
        history,
        "record_gp042_review_event",
        None,
    )

    evidence_record_id = (
        finalization.get(
            "evidence_record_id"
        )
    )

    if (
        callable(event_function)
        and evidence_record_id
    ):
        review_event = event_function(
            evidence_record_id,
            "dry_run_outcome_finalized",
            {
                "finalization_id": (
                    finalization[
                        "finalization_id"
                    ]
                ),
                "flow_id": str(flow_id),
                "final_outcome": (
                    final_outcome
                ),
                "reason": reason,
                "simulated_fill": {
                    "price": (
                        simulated_price
                    ),
                    "quantity": (
                        simulated_quantity
                    ),
                    "side": (
                        simulated_side
                    ),
                    "is_real_market_execution": (
                        False
                    ),
                },
                "finalization_hash": (
                    finalization_hash
                ),
                "broker_order_submitted": (
                    False
                ),
                "real_capital_moved": False,
                "direct_vault_upload": False,
                "live_auto_enabled": False,
            },
            path=path,
        )

    stored = (
        get_dry_run_outcome_finalization(
            finalization[
                "finalization_id"
            ],
            path=path,
        )
    )

    verification = (
        verify_dry_run_outcome_finalization(
            finalization[
                "finalization_id"
            ],
            path=path,
        )
    )

    return {
        "ok": True,
        "created": True,
        "idempotent": False,
        "finalization": stored,
        "verification": verification,
        "review_event": review_event,
    }


def create_dry_run_outcome_finalization(
    flow_id,
    payload=None,
    path=None,
):
    return finalize_dry_run_outcome(
        flow_id,
        payload=payload,
        path=path,
    )


def finalize_outcome(
    flow_id,
    payload=None,
    path=None,
):
    return finalize_dry_run_outcome(
        flow_id,
        payload=payload,
        path=path,
    )


def create_outcome_finalization(
    flow_id,
    payload=None,
    path=None,
):
    return finalize_dry_run_outcome(
        flow_id,
        payload=payload,
        path=path,
    )


def get_dry_run_outcome_finalization(
    finalization_id,
    path=None,
):
    init_outcome_finalization_db(
        path
    )

    with _connect(path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM
                ob_manual_live_dry_run_outcome_finalizations
            WHERE
                finalization_id = ?
            """,
            (
                str(finalization_id),
            ),
        ).fetchone()

    if row is None:
        return None

    return _decode_row(row)


def get_outcome_finalization(
    finalization_id,
    path=None,
):
    return get_dry_run_outcome_finalization(
        finalization_id,
        path=path,
    )


def get_finalization(
    finalization_id,
    path=None,
):
    return get_dry_run_outcome_finalization(
        finalization_id,
        path=path,
    )


def get_dry_run_outcome_finalization_by_flow(
    flow_id,
    path=None,
):
    init_outcome_finalization_db(
        path
    )

    with _connect(path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM
                ob_manual_live_dry_run_outcome_finalizations
            WHERE
                flow_id = ?
            """,
            (str(flow_id),),
        ).fetchone()

    if row is None:
        return None

    return _decode_row(row)


def list_dry_run_outcome_finalizations(
    symbol=None,
    final_outcome=None,
    limit=100,
    path=None,
):
    init_outcome_finalization_db(
        path
    )

    clauses = []
    values = []

    if symbol:
        clauses.append(
            "symbol = ?"
        )
        values.append(
            str(symbol).upper()
        )

    if final_outcome:
        clauses.append(
            "final_outcome = ?"
        )
        values.append(
            _normalize_outcome(
                final_outcome
            )
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
                ob_manual_live_dry_run_outcome_finalizations
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


def list_outcome_finalizations(
    symbol=None,
    final_outcome=None,
    limit=100,
    path=None,
):
    return list_dry_run_outcome_finalizations(
        symbol=symbol,
        final_outcome=final_outcome,
        limit=limit,
        path=path,
    )


def list_finalizations(
    symbol=None,
    final_outcome=None,
    limit=100,
    path=None,
):
    return list_dry_run_outcome_finalizations(
        symbol=symbol,
        final_outcome=final_outcome,
        limit=limit,
        path=path,
    )


def verify_dry_run_outcome_finalization(
    finalization_id,
    path=None,
):
    finalization = (
        get_dry_run_outcome_finalization(
            finalization_id,
            path=path,
        )
    )

    if finalization is None:
        return {
            "ok": False,
            "verified": False,
            "error": (
                "finalization_not_found"
            ),
        }

    calculated_hash = _sha256(
        _hash_basis(finalization)
    )

    stored_hash = (
        finalization.get(
            "finalization_hash"
        )
    )

    verified = (
        stored_hash
        == calculated_hash
    )

    return {
        "ok": verified,
        "verified": verified,
        "finalization_id": (
            finalization_id
        ),
        "stored_hash": stored_hash,
        "calculated_hash": (
            calculated_hash
        ),
        "boundaries": dict(
            BOUNDARIES
        ),
    }


def outcome_finalization_overview(
    symbol=None,
    path=None,
):
    finalizations = (
        list_dry_run_outcome_finalizations(
            symbol=symbol,
            limit=300,
            path=path,
        )
    )

    outcome_counts = {}

    for finalization in finalizations:
        outcome = finalization.get(
            "final_outcome"
        )

        outcome_counts[outcome] = (
            outcome_counts.get(
                outcome,
                0,
            )
            + 1
        )

    return {
        "finalization_count": len(
            finalizations
        ),
        "outcome_counts": (
            outcome_counts
        ),
        "symbols": sorted(
            {
                item.get("symbol")
                for item in finalizations
                if item.get("symbol")
            }
        ),
        "latest_finalization": (
            finalizations[0]
            if finalizations
            else None
        ),
        "allowed_outcomes": list(
            ALLOWED_OUTCOMES
        ),
        "boundaries": dict(
            BOUNDARIES
        ),
    }


__all__ = [
    "ALLOWED_OUTCOMES",
    "BOUNDARIES",
    "SERVICE_VERSION",
    "init_outcome_finalization_db",
    "finalize_dry_run_outcome",
    "create_dry_run_outcome_finalization",
    "finalize_outcome",
    "create_outcome_finalization",
    "get_dry_run_outcome_finalization",
    "get_outcome_finalization",
    "get_finalization",
    "get_dry_run_outcome_finalization_by_flow",
    "list_dry_run_outcome_finalizations",
    "list_outcome_finalizations",
    "list_finalizations",
    "verify_dry_run_outcome_finalization",
    "outcome_finalization_overview",
]
