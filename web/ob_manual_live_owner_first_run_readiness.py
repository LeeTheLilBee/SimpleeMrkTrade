# OB_GIANT_PACK_045_OWNER_FIRST_RUN_READINESS_CHECKPOINT_SERVICE
"""
OB GP045 — Owner First-Run Readiness Checkpoint.

Confirms whether one complete Manual Live Level 1 dry-run chain
is ready for the owner's first protected rehearsal.

This checkpoint does not grant production or real-money authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import sqlite3
import uuid

from web import (
    ob_manual_live_checklist_record_save_flow
    as gp042_flow
)

from web import (
    ob_manual_live_dry_run_outcome_finalization
    as gp043_finalization
)

from web import (
    ob_manual_live_outcome_receipt_materialization
    as gp044_receipt
)

from web import (
    ob_manual_live_dry_run_history
    as history
)


SERVICE_VERSION = "gp045"

READY_STATUS = (
    "READY_FOR_OWNER_FIRST_RUN"
)

HOLD_STATUS = (
    "HOLD_NOT_READY"
)

REQUIRED_OWNER_ASSERTIONS = (
    "tower_owner_session_confirmed",
    "tower_step_up_confirmed",
    "protected_ob_access_confirmed",
    "dry_run_only_confirmed",
    "live_auto_lock_confirmed",
    "emergency_lockback_confirmed",
    "review_center_receipt_confirmed",
    "safe_session_close_plan_confirmed",
)

BOUNDARIES = {
    "broker_order_submission_enabled": False,
    "real_capital_movement_enabled": False,
    "direct_vault_upload_enabled": False,
    "live_auto_locked": True,
    "production_manual_live_authorized": False,
    "owner_first_run_is_rehearsal_only": True,
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


def init_owner_first_run_readiness_db(
    path=None,
):
    with _connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS
            ob_manual_live_owner_first_run_readiness (
                checkpoint_id TEXT PRIMARY KEY,
                owner_id TEXT NOT NULL,
                receipt_id TEXT NOT NULL,
                finalization_id TEXT NOT NULL,
                flow_id TEXT NOT NULL,
                handoff_id TEXT,
                evidence_record_id TEXT,
                symbol TEXT,
                final_outcome TEXT,
                readiness_status TEXT NOT NULL,
                ready INTEGER NOT NULL,
                technical_checks_json TEXT NOT NULL,
                owner_assertions_json TEXT NOT NULL,
                missing_owner_assertions_json TEXT NOT NULL,
                blocking_reasons_json TEXT NOT NULL,
                flow_hash TEXT,
                finalization_hash TEXT,
                receipt_hash TEXT,
                checkpoint_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_gp045_readiness_owner
            ON
            ob_manual_live_owner_first_run_readiness (
                owner_id,
                created_at
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_gp045_readiness_receipt
            ON
            ob_manual_live_owner_first_run_readiness (
                receipt_id,
                created_at
            )
            """
        )

        conn.commit()

    return str(
        _database_path(path)
    )


def _decode_row(row):
    result = dict(row)

    for source, target in (
        (
            "technical_checks_json",
            "technical_checks",
        ),
        (
            "owner_assertions_json",
            "owner_assertions",
        ),
        (
            "missing_owner_assertions_json",
            "missing_owner_assertions",
        ),
        (
            "blocking_reasons_json",
            "blocking_reasons",
        ),
    ):
        raw = result.pop(
            source,
            "{}",
        )

        try:
            result[target] = json.loads(
                raw
            )
        except Exception:
            if target in (
                "missing_owner_assertions",
                "blocking_reasons",
            ):
                result[target] = []
            else:
                result[target] = {}

    result["ready"] = bool(
        result.get("ready")
    )

    result["boundaries"] = dict(
        BOUNDARIES
    )

    return result


def _checkpoint_hash_basis(
    checkpoint,
):
    return {
        "service_version": (
            SERVICE_VERSION
        ),
        "checkpoint_id": (
            checkpoint.get(
                "checkpoint_id"
            )
        ),
        "owner_id": checkpoint.get(
            "owner_id"
        ),
        "receipt_id": checkpoint.get(
            "receipt_id"
        ),
        "finalization_id": (
            checkpoint.get(
                "finalization_id"
            )
        ),
        "flow_id": checkpoint.get(
            "flow_id"
        ),
        "handoff_id": checkpoint.get(
            "handoff_id"
        ),
        "evidence_record_id": (
            checkpoint.get(
                "evidence_record_id"
            )
        ),
        "symbol": checkpoint.get(
            "symbol"
        ),
        "final_outcome": (
            checkpoint.get(
                "final_outcome"
            )
        ),
        "readiness_status": (
            checkpoint.get(
                "readiness_status"
            )
        ),
        "ready": bool(
            checkpoint.get("ready")
        ),
        "technical_checks": (
            checkpoint.get(
                "technical_checks"
            )
        ),
        "owner_assertions": (
            checkpoint.get(
                "owner_assertions"
            )
        ),
        "missing_owner_assertions": (
            checkpoint.get(
                "missing_owner_assertions"
            )
        ),
        "blocking_reasons": (
            checkpoint.get(
                "blocking_reasons"
            )
        ),
        "flow_hash": checkpoint.get(
            "flow_hash"
        ),
        "finalization_hash": (
            checkpoint.get(
                "finalization_hash"
            )
        ),
        "receipt_hash": (
            checkpoint.get(
                "receipt_hash"
            )
        ),
        "created_at": checkpoint.get(
            "created_at"
        ),
        "boundaries": dict(
            BOUNDARIES
        ),
    }


def evaluate_owner_first_run_readiness(
    receipt_id,
    payload=None,
    path=None,
    receipt_dir=None,
):
    init_owner_first_run_readiness_db(
        path
    )

    payload = dict(payload or {})

    owner_id = str(
        payload.get("owner_id")
        or "owner"
    )

    raw_assertions = payload.get(
        "owner_assertions"
    )

    if not isinstance(
        raw_assertions,
        dict,
    ):
        raw_assertions = {}

    owner_assertions = {
        key: (
            raw_assertions.get(key)
            is True
        )
        for key in REQUIRED_OWNER_ASSERTIONS
    }

    missing_owner_assertions = [
        key
        for key, confirmed
        in owner_assertions.items()
        if not confirmed
    ]

    receipt = (
        gp044_receipt.get_outcome_receipt(
            receipt_id,
            path=path,
        )
    )

    finalization = None
    flow = None
    receipt_verification = {
        "verified": False,
    }
    finalization_verification = {
        "verified": False,
    }

    if receipt is not None:
        receipt_verification = (
            gp044_receipt.verify_outcome_receipt(
                receipt_id,
                path=path,
                receipt_dir=receipt_dir,
            )
        )

        finalization_id = (
            receipt.get(
                "finalization_id"
            )
        )

        flow_id = receipt.get(
            "flow_id"
        )

        if finalization_id:
            finalization = (
                gp043_finalization.get_dry_run_outcome_finalization(
                    finalization_id,
                    path=path,
                )
            )

            if finalization is not None:
                finalization_verification = (
                    gp043_finalization.verify_dry_run_outcome_finalization(
                        finalization_id,
                        path=path,
                    )
                )

        if flow_id:
            flow = (
                gp042_flow.get_checklist_record_save_flow(
                    flow_id,
                    path=path,
                )
            )

    flow_id = (
        receipt.get("flow_id")
        if receipt
        else None
    )

    finalization_id = (
        receipt.get(
            "finalization_id"
        )
        if receipt
        else None
    )

    flow_hash = (
        flow.get("flow_hash")
        if flow
        else None
    )

    finalization_hash = (
        finalization.get(
            "finalization_hash"
        )
        if finalization
        else None
    )

    receipt_hash = (
        receipt.get(
            "receipt_hash"
        )
        if receipt
        else None
    )

    receipt_packet = (
        receipt.get("packet")
        if receipt
        else None
    )

    if not isinstance(
        receipt_packet,
        dict,
    ):
        receipt_packet = {}

    packet_hash_chain = (
        receipt_packet.get(
            "hash_chain"
        )
    )

    if not isinstance(
        packet_hash_chain,
        dict,
    ):
        packet_hash_chain = {}

    technical_checks = {
        "receipt_exists": (
            receipt is not None
        ),
        "finalization_exists": (
            finalization is not None
        ),
        "flow_exists": (
            flow is not None
        ),
        "gp042_checklist_passed": (
            bool(
                flow.get(
                    "checklist_passed"
                )
            )
            if flow
            else False
        ),
        "gp043_finalization_verified": (
            finalization_verification.get(
                "verified"
            )
            is True
        ),
        "gp044_receipt_verified": (
            receipt_verification.get(
                "verified"
            )
            is True
        ),
        "flow_id_continuity": (
            receipt is not None
            and finalization is not None
            and flow is not None
            and str(
                receipt.get("flow_id")
            )
            == str(
                finalization.get(
                    "flow_id"
                )
            )
            == str(
                flow.get("flow_id")
            )
        ),
        "finalization_id_continuity": (
            receipt is not None
            and finalization is not None
            and str(
                receipt.get(
                    "finalization_id"
                )
            )
            == str(
                finalization.get(
                    "finalization_id"
                )
            )
        ),
        "outcome_continuity": (
            receipt is not None
            and finalization is not None
            and str(
                receipt.get(
                    "final_outcome"
                )
            )
            == str(
                finalization.get(
                    "final_outcome"
                )
            )
        ),
        "flow_hash_continuity": (
            bool(flow_hash)
            and (
                receipt.get(
                    "flow_hash"
                )
                == flow_hash
                if receipt
                else False
            )
            and (
                finalization.get(
                    "flow_hash"
                )
                == flow_hash
                if finalization
                else False
            )
            and (
                packet_hash_chain.get(
                    "flow_hash"
                )
                == flow_hash
            )
        ),
        "finalization_hash_continuity": (
            bool(finalization_hash)
            and (
                receipt.get(
                    "finalization_hash"
                )
                == finalization_hash
                if receipt
                else False
            )
            and (
                packet_hash_chain.get(
                    "finalization_hash"
                )
                == finalization_hash
            )
        ),
        "receipt_hash_present": (
            isinstance(
                receipt_hash,
                str,
            )
            and len(receipt_hash)
            == 64
        ),
        "broker_submission_locked": (
            BOUNDARIES[
                "broker_order_submission_enabled"
            ]
            is False
        ),
        "real_capital_locked": (
            BOUNDARIES[
                "real_capital_movement_enabled"
            ]
            is False
        ),
        "direct_vault_upload_locked": (
            BOUNDARIES[
                "direct_vault_upload_enabled"
            ]
            is False
        ),
        "live_auto_locked": (
            BOUNDARIES[
                "live_auto_locked"
            ]
            is True
        ),
        "production_authority_not_granted": (
            BOUNDARIES[
                "production_manual_live_authorized"
            ]
            is False
        ),
    }

    failed_technical_checks = [
        key
        for key, passed
        in technical_checks.items()
        if not passed
    ]

    blocking_reasons = [
        (
            "technical_check_failed:"
            + key
        )
        for key in failed_technical_checks
    ]

    blocking_reasons.extend(
        (
            "owner_assertion_missing:"
            + key
        )
        for key
        in missing_owner_assertions
    )

    ready = (
        not failed_technical_checks
        and not missing_owner_assertions
    )

    readiness_status = (
        READY_STATUS
        if ready
        else HOLD_STATUS
    )

    timestamp = _utc_now()

    checkpoint = {
        "checkpoint_id": (
            "ob-gp045-readiness-"
            + uuid.uuid4().hex
        ),
        "owner_id": owner_id,
        "receipt_id": str(
            receipt_id
        ),
        "finalization_id": (
            str(finalization_id)
            if finalization_id
            else ""
        ),
        "flow_id": (
            str(flow_id)
            if flow_id
            else ""
        ),
        "handoff_id": (
            flow.get("handoff_id")
            if flow
            else None
        ),
        "evidence_record_id": (
            flow.get(
                "evidence_record_id"
            )
            if flow
            else None
        ),
        "symbol": (
            receipt.get("symbol")
            if receipt
            else None
        ),
        "final_outcome": (
            receipt.get(
                "final_outcome"
            )
            if receipt
            else None
        ),
        "readiness_status": (
            readiness_status
        ),
        "ready": ready,
        "technical_checks": (
            technical_checks
        ),
        "owner_assertions": (
            owner_assertions
        ),
        "missing_owner_assertions": (
            missing_owner_assertions
        ),
        "blocking_reasons": (
            blocking_reasons
        ),
        "flow_hash": flow_hash,
        "finalization_hash": (
            finalization_hash
        ),
        "receipt_hash": receipt_hash,
        "created_at": timestamp,
        "boundaries": dict(
            BOUNDARIES
        ),
    }

    checkpoint_hash = _sha256(
        _checkpoint_hash_basis(
            checkpoint
        )
    )

    checkpoint[
        "checkpoint_hash"
    ] = checkpoint_hash

    with _connect(path) as conn:
        conn.execute(
            """
            INSERT INTO
            ob_manual_live_owner_first_run_readiness (
                checkpoint_id,
                owner_id,
                receipt_id,
                finalization_id,
                flow_id,
                handoff_id,
                evidence_record_id,
                symbol,
                final_outcome,
                readiness_status,
                ready,
                technical_checks_json,
                owner_assertions_json,
                missing_owner_assertions_json,
                blocking_reasons_json,
                flow_hash,
                finalization_hash,
                receipt_hash,
                checkpoint_hash,
                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                checkpoint[
                    "checkpoint_id"
                ],
                checkpoint[
                    "owner_id"
                ],
                checkpoint[
                    "receipt_id"
                ],
                checkpoint[
                    "finalization_id"
                ],
                checkpoint["flow_id"],
                checkpoint.get(
                    "handoff_id"
                ),
                checkpoint.get(
                    "evidence_record_id"
                ),
                checkpoint.get(
                    "symbol"
                ),
                checkpoint.get(
                    "final_outcome"
                ),
                checkpoint[
                    "readiness_status"
                ],
                int(
                    checkpoint["ready"]
                ),
                _canonical(
                    technical_checks
                ),
                _canonical(
                    owner_assertions
                ),
                _canonical(
                    missing_owner_assertions
                ),
                _canonical(
                    blocking_reasons
                ),
                flow_hash,
                finalization_hash,
                receipt_hash,
                checkpoint_hash,
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
        checkpoint.get(
            "evidence_record_id"
        )
    )

    if (
        callable(event_function)
        and evidence_record_id
    ):
        review_event = event_function(
            evidence_record_id,
            (
                "owner_first_run_ready"
                if ready
                else "owner_first_run_hold"
            ),
            {
                "checkpoint_id": (
                    checkpoint[
                        "checkpoint_id"
                    ]
                ),
                "receipt_id": (
                    checkpoint[
                        "receipt_id"
                    ]
                ),
                "readiness_status": (
                    readiness_status
                ),
                "ready": ready,
                "blocking_reasons": (
                    blocking_reasons
                ),
                "checkpoint_hash": (
                    checkpoint_hash
                ),
                "production_manual_live_authorized": (
                    False
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

    stored = (
        get_owner_first_run_readiness_checkpoint(
            checkpoint[
                "checkpoint_id"
            ],
            path=path,
        )
    )

    verification = (
        verify_owner_first_run_readiness_checkpoint(
            checkpoint[
                "checkpoint_id"
            ],
            path=path,
        )
    )

    return {
        "ok": True,
        "created": True,
        "ready": ready,
        "readiness_status": (
            readiness_status
        ),
        "checkpoint": stored,
        "verification": (
            verification
        ),
        "review_event": (
            review_event
        ),
    }


def get_owner_first_run_readiness_checkpoint(
    checkpoint_id,
    path=None,
):
    init_owner_first_run_readiness_db(
        path
    )

    with _connect(path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM
                ob_manual_live_owner_first_run_readiness
            WHERE
                checkpoint_id = ?
            """,
            (
                str(checkpoint_id),
            ),
        ).fetchone()

    if row is None:
        return None

    return _decode_row(row)


def list_owner_first_run_readiness_checkpoints(
    owner_id=None,
    readiness_status=None,
    limit=100,
    path=None,
):
    init_owner_first_run_readiness_db(
        path
    )

    clauses = []
    values = []

    if owner_id:
        clauses.append(
            "owner_id = ?"
        )
        values.append(
            str(owner_id)
        )

    if readiness_status:
        clauses.append(
            "readiness_status = ?"
        )
        values.append(
            str(
                readiness_status
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
                ob_manual_live_owner_first_run_readiness
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


def verify_owner_first_run_readiness_checkpoint(
    checkpoint_id,
    path=None,
):
    checkpoint = (
        get_owner_first_run_readiness_checkpoint(
            checkpoint_id,
            path=path,
        )
    )

    if checkpoint is None:
        return {
            "ok": False,
            "verified": False,
            "error": (
                "checkpoint_not_found"
            ),
        }

    calculated_hash = _sha256(
        _checkpoint_hash_basis(
            checkpoint
        )
    )

    stored_hash = (
        checkpoint.get(
            "checkpoint_hash"
        )
    )

    verified = (
        stored_hash
        == calculated_hash
    )

    return {
        "ok": verified,
        "verified": verified,
        "checkpoint_id": (
            checkpoint_id
        ),
        "readiness_status": (
            checkpoint.get(
                "readiness_status"
            )
        ),
        "ready": bool(
            checkpoint.get("ready")
        ),
        "stored_hash": stored_hash,
        "calculated_hash": (
            calculated_hash
        ),
        "boundaries": dict(
            BOUNDARIES
        ),
    }


def owner_first_run_readiness_overview(
    owner_id=None,
    path=None,
):
    checkpoints = (
        list_owner_first_run_readiness_checkpoints(
            owner_id=owner_id,
            limit=300,
            path=path,
        )
    )

    ready_count = sum(
        1
        for checkpoint in checkpoints
        if checkpoint.get("ready")
    )

    hold_count = (
        len(checkpoints)
        - ready_count
    )

    return {
        "checkpoint_count": len(
            checkpoints
        ),
        "ready_count": ready_count,
        "hold_count": hold_count,
        "latest_checkpoint": (
            checkpoints[0]
            if checkpoints
            else None
        ),
        "required_owner_assertions": list(
            REQUIRED_OWNER_ASSERTIONS
        ),
        "boundaries": dict(
            BOUNDARIES
        ),
    }


__all__ = [
    "BOUNDARIES",
    "HOLD_STATUS",
    "READY_STATUS",
    "REQUIRED_OWNER_ASSERTIONS",
    "SERVICE_VERSION",
    "init_owner_first_run_readiness_db",
    "evaluate_owner_first_run_readiness",
    "get_owner_first_run_readiness_checkpoint",
    "list_owner_first_run_readiness_checkpoints",
    "verify_owner_first_run_readiness_checkpoint",
    "owner_first_run_readiness_overview",
]
