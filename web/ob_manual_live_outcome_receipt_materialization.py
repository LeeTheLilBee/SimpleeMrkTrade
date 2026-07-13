# OB_GIANT_PACK_044_OUTCOME_TO_RECEIPT_MATERIALIZATION_SERVICE
"""
OB GP044 — Real Outcome-to-Receipt Materialization.

A finalized GP043 dry-run outcome becomes one durable,
hash-linked, verifiable receipt packet.

Boundaries:
- no broker order submission
- no real capital movement
- no direct Vault upload
- no raw public receipt URL
- Live Auto remains locked
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import importlib
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


SERVICE_VERSION = "gp044"

BOUNDARIES = {
    "broker_order_submission_enabled": False,
    "real_capital_movement_enabled": False,
    "direct_vault_upload_enabled": False,
    "raw_public_receipt_url_enabled": False,
    "live_auto_locked": True,
}


GP043_MODULE_CANDIDATES = (
    "web.ob_manual_live_dry_run_outcome_finalization",
    "web.ob_manual_live_outcome_finalization",
    "web.ob_manual_live_real_dry_run_outcome_finalization",
)


GP043_GETTER_NAMES = (
    "get_dry_run_outcome_finalization",
    "get_outcome_finalization",
    "get_finalized_outcome",
    "get_finalization",
)


GP043_LIST_NAMES = (
    "list_dry_run_outcome_finalizations",
    "list_outcome_finalizations",
    "list_finalized_outcomes",
    "list_finalizations",
)


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


def _receipt_directory(
    receipt_dir=None,
):
    if receipt_dir:
        directory = Path(receipt_dir)

    elif os.environ.get(
        "OB_MANUAL_LIVE_RECEIPT_DIR"
    ):
        directory = Path(
            os.environ[
                "OB_MANUAL_LIVE_RECEIPT_DIR"
            ]
        )

    else:
        directory = (
            Path(__file__)
            .resolve()
            .parents[1]
            / "data"
            / "ob_manual_live_receipts"
        )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory


def _connect(path=None):
    conn = sqlite3.connect(
        _database_path(path)
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_receipt_db(path=None):
    with _connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS
            ob_manual_live_outcome_receipts (
                receipt_id TEXT PRIMARY KEY,
                finalization_id TEXT NOT NULL UNIQUE,
                flow_id TEXT NOT NULL,
                handoff_id TEXT,
                evidence_record_id TEXT,
                candidate_id TEXT,
                symbol TEXT,
                owner_id TEXT,
                final_outcome TEXT NOT NULL,
                simulated_price REAL,
                simulated_quantity REAL,
                checklist_score INTEGER,
                checklist_passed INTEGER,
                checklist_snapshot_hash TEXT,
                flow_hash TEXT,
                finalization_hash TEXT NOT NULL,
                receipt_hash TEXT NOT NULL,
                storage_ref TEXT NOT NULL,
                packet_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_gp044_receipt_symbol
            ON ob_manual_live_outcome_receipts (
                symbol,
                created_at
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_gp044_receipt_flow
            ON ob_manual_live_outcome_receipts (
                flow_id
            )
            """
        )

        conn.commit()

    return str(_database_path(path))


def _gp043_module():
    errors = []

    for module_name in (
        GP043_MODULE_CANDIDATES
    ):
        try:
            return importlib.import_module(
                module_name
            )
        except Exception as exc:
            errors.append(
                f"{module_name}: {exc}"
            )

    web_directory = Path(
        __file__
    ).resolve().parent

    for candidate in sorted(
        web_directory.glob(
            "ob_manual_live_*outcome*final*.py"
        )
    ):
        if candidate.stem == Path(
            __file__
        ).stem:
            continue

        module_name = (
            "web." + candidate.stem
        )

        try:
            return importlib.import_module(
                module_name
            )
        except Exception as exc:
            errors.append(
                f"{module_name}: {exc}"
            )

    for candidate in sorted(
        web_directory.glob(
            "ob_manual_live_*.py"
        )
    ):
        if candidate.stem == Path(
            __file__
        ).stem:
            continue

        try:
            text = candidate.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except Exception:
            continue

        if (
            "GP043" not in text
            or "outcome" not in text.lower()
            or "final" not in text.lower()
        ):
            continue

        module_name = (
            "web." + candidate.stem
        )

        try:
            return importlib.import_module(
                module_name
            )
        except Exception as exc:
            errors.append(
                f"{module_name}: {exc}"
            )

    raise ImportError(
        "GP043 module could not be loaded: "
        + " | ".join(errors)
    )


def _unwrap(value):
    if not isinstance(value, dict):
        return value

    for key in (
        "finalization",
        "outcome_finalization",
        "finalized_outcome",
        "record",
        "result",
    ):
        candidate = value.get(key)

        if isinstance(candidate, dict):
            return candidate

    return value


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
        "No compatible function call."
    )


def _get_finalization(
    finalization_id,
    path=None,
):
    module = _gp043_module()

    for name in GP043_GETTER_NAMES:
        function = getattr(
            module,
            name,
            None,
        )

        if not callable(function):
            continue

        result = _call_path_aware(
            function,
            (finalization_id,),
            path=path,
            keyword_values={
                "finalization_id": (
                    finalization_id
                ),
                "outcome_finalization_id": (
                    finalization_id
                ),
                "record_id": finalization_id,
            },
        )

        result = _unwrap(result)

        if isinstance(result, dict):
            return result

    for name in GP043_LIST_NAMES:
        function = getattr(
            module,
            name,
            None,
        )

        if not callable(function):
            continue

        result = _call_path_aware(
            function,
            (),
            path=path,
            keyword_values={
                "limit": 300,
            },
        )

        if isinstance(result, dict):
            for key in (
                "finalizations",
                "outcomes",
                "records",
                "items",
            ):
                if isinstance(
                    result.get(key),
                    list,
                ):
                    result = result[key]
                    break

        if not isinstance(result, list):
            continue

        for item in result:
            if not isinstance(item, dict):
                continue

            item_id = (
                item.get(
                    "finalization_id"
                )
                or item.get(
                    "outcome_finalization_id"
                )
                or item.get("id")
            )

            if str(item_id) == str(
                finalization_id
            ):
                return item

    raise LookupError(
        "GP043 finalization not found: "
        + str(finalization_id)
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
        return result

    raise LookupError(
        "GP042 flow not found: "
        + str(flow_id)
    )


def _decode_row(row):
    result = dict(row)

    raw = result.pop(
        "packet_json",
        "{}",
    )

    try:
        result["packet"] = json.loads(
            raw
        )
    except Exception:
        result["packet"] = {}

    result["checklist_passed"] = bool(
        result.get(
            "checklist_passed"
        )
    )

    result["boundaries"] = dict(
        BOUNDARIES
    )

    return result


def _packet_path(
    storage_ref,
    receipt_dir=None,
):
    return (
        _receipt_directory(receipt_dir)
        / Path(storage_ref).name
    )


def _write_packet(
    packet,
    storage_ref,
    receipt_dir=None,
):
    destination = _packet_path(
        storage_ref,
        receipt_dir=receipt_dir,
    )

    temporary = destination.with_suffix(
        destination.suffix + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            packet,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    try:
        os.chmod(
            temporary,
            0o600,
        )
    except Exception:
        pass

    temporary.replace(destination)

    try:
        os.chmod(
            destination,
            0o600,
        )
    except Exception:
        pass

    return destination


def materialize_outcome_receipt(
    finalization_id,
    payload=None,
    path=None,
    receipt_dir=None,
):
    init_receipt_db(path)

    payload = dict(payload or {})

    existing = get_outcome_receipt_by_finalization(
        finalization_id,
        path=path,
    )

    if existing is not None:
        return {
            "ok": True,
            "created": False,
            "idempotent": True,
            "receipt": existing,
        }

    finalization = _get_finalization(
        finalization_id,
        path=path,
    )

    flow_id = (
        finalization.get("flow_id")
        or finalization.get(
            "checklist_flow_id"
        )
        or finalization.get(
            "record_save_flow_id"
        )
    )

    if not flow_id:
        raise ValueError(
            "GP043 finalization has no flow_id."
        )

    flow = _get_flow(
        flow_id,
        path=path,
    )

    outcome = (
        finalization.get(
            "final_outcome"
        )
        or finalization.get("outcome")
        or finalization.get(
            "dry_run_outcome"
        )
        or finalization.get(
            "outcome_status"
        )
        or "needs_review"
    )

    simulated_fill = (
        finalization.get(
            "simulated_fill"
        )
        or {}
    )

    if not isinstance(
        simulated_fill,
        dict,
    ):
        simulated_fill = {}

    simulated_price = (
        simulated_fill.get("price")
        or finalization.get(
            "simulated_price"
        )
        or finalization.get(
            "fill_price"
        )
    )

    simulated_quantity = (
        simulated_fill.get("quantity")
        or finalization.get(
            "simulated_quantity"
        )
        or finalization.get(
            "fill_quantity"
        )
    )

    finalization_hash = (
        finalization.get(
            "finalization_hash"
        )
        or finalization.get(
            "outcome_hash"
        )
        or finalization.get(
            "final_hash"
        )
        or _sha256(finalization)
    )

    receipt_id = (
        "ob-gp044-receipt-"
        + uuid.uuid4().hex
    )

    created_at = _utc_now()

    packet_without_hash = {
        "receipt_id": receipt_id,
        "receipt_type": (
            "manual_live_dry_run_outcome_receipt"
        ),
        "service_version": (
            SERVICE_VERSION
        ),
        "finalization_id": (
            str(finalization_id)
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
            or finalization.get(
                "owner_id"
            )
            or flow.get("owner_id")
        ),
        "final_outcome": outcome,
        "simulated_fill": {
            "price": simulated_price,
            "quantity": (
                simulated_quantity
            ),
            "is_real_market_execution": (
                False
            ),
        },
        "checklist": {
            "score": flow.get(
                "checklist_score"
            ),
            "passed": bool(
                flow.get(
                    "checklist_passed"
                )
            ),
            "snapshot_hash": flow.get(
                "checklist_snapshot_hash"
            ),
        },
        "hash_chain": {
            "flow_hash": flow.get(
                "flow_hash"
            ),
            "finalization_hash": (
                finalization_hash
            ),
        },
        "finalization": finalization,
        "boundaries": dict(
            BOUNDARIES
        ),
        "created_at": created_at,
    }

    receipt_hash = _sha256(
        packet_without_hash
    )

    packet = {
        **packet_without_hash,
        "receipt_hash": receipt_hash,
    }

    storage_ref = (
        receipt_id + ".json"
    )

    _write_packet(
        packet,
        storage_ref,
        receipt_dir=receipt_dir,
    )

    with _connect(path) as conn:
        conn.execute(
            """
            INSERT INTO
            ob_manual_live_outcome_receipts (
                receipt_id,
                finalization_id,
                flow_id,
                handoff_id,
                evidence_record_id,
                candidate_id,
                symbol,
                owner_id,
                final_outcome,
                simulated_price,
                simulated_quantity,
                checklist_score,
                checklist_passed,
                checklist_snapshot_hash,
                flow_hash,
                finalization_hash,
                receipt_hash,
                storage_ref,
                packet_json,
                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                receipt_id,
                str(finalization_id),
                str(flow_id),
                flow.get("handoff_id"),
                flow.get(
                    "evidence_record_id"
                ),
                flow.get("candidate_id"),
                flow.get("symbol"),
                packet.get("owner_id"),
                str(outcome),
                simulated_price,
                simulated_quantity,
                flow.get(
                    "checklist_score"
                ),
                int(
                    bool(
                        flow.get(
                            "checklist_passed"
                        )
                    )
                ),
                flow.get(
                    "checklist_snapshot_hash"
                ),
                flow.get("flow_hash"),
                finalization_hash,
                receipt_hash,
                storage_ref,
                _canonical(packet),
                created_at,
            ),
        )

        conn.commit()

    event = None

    record_event = getattr(
        history,
        "record_gp042_review_event",
        None,
    )

    evidence_record_id = flow.get(
        "evidence_record_id"
    )

    if (
        callable(record_event)
        and evidence_record_id
    ):
        event = record_event(
            evidence_record_id,
            "outcome_receipt_materialized",
            {
                "receipt_id": receipt_id,
                "finalization_id": (
                    str(finalization_id)
                ),
                "flow_id": str(flow_id),
                "final_outcome": (
                    str(outcome)
                ),
                "receipt_hash": (
                    receipt_hash
                ),
                "broker_order_submission_enabled": (
                    False
                ),
                "real_capital_movement_enabled": (
                    False
                ),
                "direct_vault_upload_enabled": (
                    False
                ),
                "live_auto_locked": True,
            },
            path=path,
        )

    receipt = get_outcome_receipt(
        receipt_id,
        path=path,
    )

    verification = verify_outcome_receipt(
        receipt_id,
        path=path,
        receipt_dir=receipt_dir,
    )

    return {
        "ok": True,
        "created": True,
        "idempotent": False,
        "receipt": receipt,
        "verification": verification,
        "review_event": event,
    }


def get_outcome_receipt(
    receipt_id,
    path=None,
):
    init_receipt_db(path)

    with _connect(path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM
                ob_manual_live_outcome_receipts
            WHERE
                receipt_id = ?
            """,
            (str(receipt_id),),
        ).fetchone()

    if row is None:
        return None

    return _decode_row(row)


def get_outcome_receipt_by_finalization(
    finalization_id,
    path=None,
):
    init_receipt_db(path)

    with _connect(path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM
                ob_manual_live_outcome_receipts
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


def list_outcome_receipts(
    symbol=None,
    final_outcome=None,
    limit=100,
    path=None,
):
    init_receipt_db(path)

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
            str(final_outcome)
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
                ob_manual_live_outcome_receipts
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


def verify_outcome_receipt(
    receipt_id,
    path=None,
    receipt_dir=None,
):
    receipt = get_outcome_receipt(
        receipt_id,
        path=path,
    )

    if receipt is None:
        return {
            "ok": False,
            "verified": False,
            "error": (
                "receipt_not_found"
            ),
        }

    packet_path = _packet_path(
        receipt["storage_ref"],
        receipt_dir=receipt_dir,
    )

    if not packet_path.exists():
        return {
            "ok": False,
            "verified": False,
            "error": (
                "receipt_packet_missing"
            ),
            "receipt_id": receipt_id,
        }

    try:
        packet = json.loads(
            packet_path.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return {
            "ok": False,
            "verified": False,
            "error": (
                "receipt_packet_invalid_json"
            ),
            "receipt_id": receipt_id,
        }

    stored_hash = packet.pop(
        "receipt_hash",
        None,
    )

    calculated_hash = _sha256(
        packet
    )

    verified = (
        stored_hash
        == calculated_hash
        == receipt.get(
            "receipt_hash"
        )
    )

    return {
        "ok": verified,
        "verified": verified,
        "receipt_id": receipt_id,
        "stored_hash": stored_hash,
        "database_hash": receipt.get(
            "receipt_hash"
        ),
        "calculated_hash": (
            calculated_hash
        ),
        "packet_exists": True,
        "boundaries": dict(
            BOUNDARIES
        ),
    }


def receipt_overview(
    symbol=None,
    path=None,
):
    receipts = list_outcome_receipts(
        symbol=symbol,
        limit=300,
        path=path,
    )

    outcome_counts = {}

    for receipt in receipts:
        outcome = receipt.get(
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
        "receipt_count": len(receipts),
        "outcome_counts": (
            outcome_counts
        ),
        "symbols": sorted(
            {
                receipt.get("symbol")
                for receipt in receipts
                if receipt.get("symbol")
            }
        ),
        "latest_receipt": (
            receipts[0]
            if receipts
            else None
        ),
        "boundaries": dict(
            BOUNDARIES
        ),
    }


__all__ = [
    "BOUNDARIES",
    "SERVICE_VERSION",
    "init_receipt_db",
    "materialize_outcome_receipt",
    "get_outcome_receipt",
    "get_outcome_receipt_by_finalization",
    "list_outcome_receipts",
    "verify_outcome_receipt",
    "receipt_overview",
]
