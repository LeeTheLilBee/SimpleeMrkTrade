
"""OB GP050 — Protected Launch Corridor Closeout Readiness.

This service assesses whether the Observatory side of the protected launch
corridor is locally clean and ready for an owner rehearsal request.

A passing result is not Tower authorization. It does not create identity,
clearance, step-up, a Tower launch packet, room access, broker authority,
production Manual Live authority or capital-movement authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import tempfile

import web.ob_tower_protected_launch_handoff_consumer as gp046
import web.ob_tower_protected_launch_session_state as gp047
import web.ob_protected_room_entry_enforcement as gp048
import web.ob_protected_room_exit_closeout as gp049


OB_GIANT_PACK_050_PROTECTED_LAUNCH_CORRIDOR_READINESS_SERVICE = True

PACK = "GP050"
CONTRACT_VERSION = "ob.protected_launch_corridor_readiness.v1"

ZERO_HASH = "0" * 64

READY_RECOMMENDATION = (
    "READY_FOR_TOWER_OWNER_REHEARSAL_REQUEST"
)

HOLD_RECOMMENDATION = (
    "HOLD_OWNER_REHEARSAL"
)

EXPECTED_ROOM_IDS = {
    "dashboard",
    "market_map",
    "symbol_page",
    "trade_center",
    "review_center",
    "owner_console",
}


def _default_database_path() -> Path:
    configured = (
        os.environ.get(
            "OB_PROTECTED_LAUNCH_READINESS_DB_PATH"
        )
        or os.environ.get(
            "OB_PROTECTED_ROOM_EXIT_DB_PATH"
        )
        or os.environ.get(
            "OB_PROTECTED_ROOM_ENTRY_DB_PATH"
        )
        or os.environ.get(
            "OB_TOWER_LAUNCH_SESSION_DB_PATH"
        )
        or os.environ.get(
            "OB_TOWER_LAUNCH_DB_PATH"
        )
        or os.environ.get(
            "OB_DRY_RUN_DB_PATH"
        )
    )

    if configured:
        return Path(
            configured
        ).expanduser().resolve()

    return (
        Path(tempfile.gettempdir())
        / "ob_protected_launch_readiness_gp050.sqlite3"
    )


def _database_path(
    path: Optional[Any] = None,
) -> Path:
    if path is None:
        return _default_database_path()

    return Path(
        path
    ).expanduser().resolve()


def _connect(
    path: Optional[Any] = None,
) -> sqlite3.Connection:
    database = _database_path(
        path
    )

    database.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        str(database),
        timeout=30,
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    connection.execute(
        "PRAGMA journal_mode = WAL"
    )

    return connection


def _canonical_json(
    value: Any,
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _json_text(
    value: Any,
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )


def _sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def _iso(
    value: datetime,
) -> str:
    return (
        value.astimezone(
            timezone.utc
        )
        .isoformat()
        .replace(
            "+00:00",
            "Z",
        )
    )


def _parse_time(
    value: Any,
) -> datetime:
    if isinstance(
        value,
        datetime,
    ):
        parsed = value

    elif isinstance(
        value,
        str,
    ):
        rendered = value.strip()

        if rendered.endswith("Z"):
            rendered = (
                rendered[:-1]
                + "+00:00"
            )

        parsed = datetime.fromisoformat(
            rendered
        )

    else:
        raise ValueError(
            "timestamp must be an ISO string"
        )

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )

    return parsed.astimezone(
        timezone.utc
    )


def _now(
    value: Optional[Any] = None,
) -> datetime:
    if value is None:
        return datetime.now(
            timezone.utc
        )

    return _parse_time(
        value
    )


def _unique(
    values: Iterable[str],
) -> List[str]:
    output: List[str] = []
    seen = set()

    for value in values:
        rendered = str(
            value or ""
        ).strip()

        if not rendered:
            continue

        if rendered in seen:
            continue

        seen.add(
            rendered
        )

        output.append(
            rendered
        )

    return output


def _valid_owner_id(
    value: Any,
) -> bool:
    rendered = str(
        value or ""
    ).strip()

    return bool(
        re.fullmatch(
            r"[A-Za-z0-9_.:\-]{3,200}",
            rendered,
        )
    )


def init_readiness_database(
    path: Optional[Any] = None,
) -> str:
    database = _database_path(
        path
    )

    gp047.init_session_database(
        database
    )

    gp048.init_entry_database(
        database
    )

    gp049.init_exit_database(
        database
    )

    with _connect(
        database
    ) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS
            ob_protected_launch_readiness_assessments (
                assessment_id TEXT PRIMARY KEY,
                owner_id TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                local_readiness_passed INTEGER NOT NULL,
                reason_codes_json TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                snapshot_hash TEXT NOT NULL,
                previous_assessment_hash TEXT NOT NULL,
                assessment_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_readiness_owner
            ON ob_protected_launch_readiness_assessments(
                owner_id,
                created_at
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_readiness_recommendation
            ON ob_protected_launch_readiness_assessments(
                recommendation,
                created_at
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_readiness_snapshot
            ON ob_protected_launch_readiness_assessments(
                owner_id,
                snapshot_hash
            );
            """
        )

    return str(
        database
    )


def _latest_assessment_hash(
    connection: sqlite3.Connection,
) -> str:
    row = connection.execute(
        """
        SELECT assessment_hash
        FROM ob_protected_launch_readiness_assessments
        ORDER BY rowid DESC
        LIMIT 1
        """
    ).fetchone()

    if row is None:
        return ZERO_HASH

    return str(
        row[
            "assessment_hash"
        ]
    )


def _assessment_hash_material(
    record: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "assessment_id": record[
            "assessment_id"
        ],
        "owner_id": record[
            "owner_id"
        ],
        "recommendation": record[
            "recommendation"
        ],
        "local_readiness_passed": record[
            "local_readiness_passed"
        ],
        "reason_codes": record[
            "reason_codes"
        ],
        "evidence": record[
            "evidence"
        ],
        "snapshot_hash": record[
            "snapshot_hash"
        ],
        "previous_assessment_hash": record[
            "previous_assessment_hash"
        ],
        "created_at": record[
            "created_at"
        ],
        "tower_launch_authorized": False,
        "tower_identity_approved": False,
        "tower_clearance_approved": False,
        "tower_step_up_approved": False,
        "production_authority_granted": False,
    }


def _public_assessment(
    row: sqlite3.Row,
) -> Dict[str, Any]:
    return {
        "assessment_id": row[
            "assessment_id"
        ],
        "owner_id": row[
            "owner_id"
        ],
        "recommendation": row[
            "recommendation"
        ],
        "local_readiness_passed": bool(
            row[
                "local_readiness_passed"
            ]
        ),
        "reason_codes": json.loads(
            row[
                "reason_codes_json"
            ]
        ),
        "evidence": json.loads(
            row[
                "evidence_json"
            ]
        ),
        "snapshot_hash": row[
            "snapshot_hash"
        ],
        "previous_assessment_hash": row[
            "previous_assessment_hash"
        ],
        "assessment_hash": row[
            "assessment_hash"
        ],
        "created_at": row[
            "created_at"
        ],
        "tower_launch_authorized": False,
        "tower_identity_approved": False,
        "tower_clearance_approved": False,
        "tower_step_up_approved": False,
        "room_entry_authorized": False,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
    }


def get_readiness_assessment(
    assessment_id: str,
    *,
    path: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    init_readiness_database(
        path
    )

    with _connect(
        path
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_protected_launch_readiness_assessments
            WHERE assessment_id = ?
            """,
            (
                str(
                    assessment_id
                ),
            ),
        ).fetchone()

    if row is None:
        return None

    return _public_assessment(
        row
    )


def get_latest_readiness_assessment(
    owner_id: str,
    *,
    path: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    init_readiness_database(
        path
    )

    with _connect(
        path
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_protected_launch_readiness_assessments
            WHERE owner_id = ?
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (
                str(
                    owner_id
                ),
            ),
        ).fetchone()

    if row is None:
        return None

    return _public_assessment(
        row
    )


def list_readiness_assessments(
    *,
    owner_id: Optional[str] = None,
    recommendation: Optional[str] = None,
    limit: int = 100,
    path: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    init_readiness_database(
        path
    )

    limit = max(
        1,
        min(
            int(limit),
            500,
        ),
    )

    query = """
        SELECT *
        FROM ob_protected_launch_readiness_assessments
    """

    clauses: List[str] = []
    parameters: List[Any] = []

    if owner_id:
        clauses.append(
            "owner_id = ?"
        )

        parameters.append(
            str(
                owner_id
            )
        )

    if recommendation:
        clauses.append(
            "recommendation = ?"
        )

        parameters.append(
            str(
                recommendation
            )
        )

    if clauses:
        query += (
            " WHERE "
            + " AND ".join(
                clauses
            )
        )

    query += """
        ORDER BY rowid DESC
        LIMIT ?
    """

    parameters.append(
        limit
    )

    with _connect(
        path
    ) as connection:
        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

    return [
        _public_assessment(
            row
        )
        for row in rows
    ]


def _collect_readiness_evidence(
    *,
    owner_id: str,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_readiness_database(
        database
    )

    current_time = _now(
        now
    )

    gp047_status = (
        gp047.protected_launch_session_status(
            path=database,
            now=current_time,
        )
    )

    gp048_status = (
        gp048.protected_room_entry_status(
            path=database,
            now=current_time,
        )
    )

    gp049_status = (
        gp049.protected_room_exit_status(
            path=database,
        )
    )

    owner_sessions = (
        gp047.list_protected_launch_sessions(
            owner_id=owner_id,
            limit=500,
            path=database,
            now=current_time,
        )
    )

    owner_contexts = (
        gp048.list_protected_room_contexts(
            owner_id=owner_id,
            limit=500,
            path=database,
            now=current_time,
        )
    )

    owner_closeouts = (
        gp049.list_protected_room_exit_closeouts(
            owner_id=owner_id,
            limit=500,
            path=database,
        )
    )

    active_sessions = [
        item
        for item in owner_sessions
        if item.get(
            "state"
        )
        in {
            "reserved",
            "active",
        }
    ]

    active_contexts = [
        item
        for item in owner_contexts
        if item.get(
            "state"
        )
        == "active"
    ]

    pending_lockbacks = [
        item
        for item in owner_closeouts
        if item.get(
            "lockback_state"
        )
        == "required"
    ]

    room_registry = getattr(
        gp046,
        "ROOM_REGISTRY",
        {},
    )

    room_ids = sorted(
        str(key)
        for key in room_registry.keys()
    )

    service_markers = {
        "gp046": bool(
            getattr(
                gp046,
                (
                    "OB_GIANT_PACK_046_"
                    "TOWER_PROTECTED_LAUNCH_HANDOFF_CONSUMER_SERVICE"
                ),
                False,
            )
        ),
        "gp047": bool(
            getattr(
                gp047,
                (
                    "OB_GIANT_PACK_047_"
                    "PROTECTED_LAUNCH_SESSION_STATE_SERVICE"
                ),
                False,
            )
        ),
        "gp048": bool(
            getattr(
                gp048,
                (
                    "OB_GIANT_PACK_048_"
                    "PROTECTED_ROOM_ENTRY_ENFORCEMENT_SERVICE"
                ),
                False,
            )
        ),
        "gp049": bool(
            getattr(
                gp049,
                (
                    "OB_GIANT_PACK_049_"
                    "PROTECTED_ROOM_EXIT_CLOSEOUT_SERVICE"
                ),
                False,
            )
        ),
    }

    safety_checks = {
        "gp047_production_manual_live_unauthorized": (
            gp047_status.get(
                "production_manual_live_authorized"
            )
            is False
        ),
        "gp047_broker_submission_disabled": (
            gp047_status.get(
                "broker_submission_enabled"
            )
            is False
        ),
        "gp047_real_capital_disabled": (
            gp047_status.get(
                "real_capital_movement_enabled"
            )
            is False
        ),
        "gp047_direct_vault_upload_disabled": (
            gp047_status.get(
                "direct_vault_upload_enabled"
            )
            is False
        ),
        "gp047_live_auto_locked": (
            gp047_status.get(
                "live_auto_locked"
            )
            is True
        ),
        "gp048_default_deny": (
            gp048_status.get(
                "default_deny"
            )
            is True
        ),
        "gp048_one_active_context_per_session": (
            gp048_status.get(
                "one_active_context_per_session"
            )
            is True
        ),
        "gp048_room_switch_disabled": (
            gp048_status.get(
                "room_switch_allowed"
            )
            is False
        ),
        "gp048_context_cannot_outlive_session": (
            gp048_status.get(
                "context_can_outlive_session"
            )
            is False
        ),
        "gp049_context_revocation_required": (
            gp049_status.get(
                "context_revocation_required"
            )
            is True
        ),
        "gp049_session_close_required": (
            gp049_status.get(
                "session_close_required"
            )
            is True
        ),
        "gp049_tower_lockback_authority": (
            gp049_status.get(
                "tower_lockback_authority"
            )
            is True
        ),
        "gp049_ob_self_lockback_denied": (
            gp049_status.get(
                "ob_self_lockback_allowed"
            )
            is False
        ),
        "gp049_room_entry_after_closeout_disabled": (
            gp049_status.get(
                "room_entry_allowed_after_closeout"
            )
            is False
        ),
    }

    return {
        "owner_id": owner_id,
        "evaluated_at": _iso(
            current_time
        ),
        "service_markers": (
            service_markers
        ),
        "room_registry": {
            "expected_count": 6,
            "actual_count": len(
                room_ids
            ),
            "room_ids": room_ids,
            "matches_expected": (
                set(
                    room_ids
                )
                == EXPECTED_ROOM_IDS
            ),
        },
        "owner_state": {
            "session_total": len(
                owner_sessions
            ),
            "active_session_count": len(
                active_sessions
            ),
            "active_session_ids": [
                item[
                    "session_state_id"
                ]
                for item in active_sessions
            ],
            "context_total": len(
                owner_contexts
            ),
            "active_context_count": len(
                active_contexts
            ),
            "active_context_ids": [
                item[
                    "context_id"
                ]
                for item in active_contexts
            ],
            "closeout_total": len(
                owner_closeouts
            ),
            "pending_lockback_count": len(
                pending_lockbacks
            ),
            "pending_lockback_ids": [
                item[
                    "closeout_id"
                ]
                for item in pending_lockbacks
            ],
        },
        "corridor_status": {
            "gp047": {
                "active": gp047_status.get(
                    "active",
                    0,
                ),
                "closed": gp047_status.get(
                    "closed",
                    0,
                ),
                "expired": gp047_status.get(
                    "expired",
                    0,
                ),
                "activation_failed": (
                    gp047_status.get(
                        "activation_failed",
                        0,
                    )
                ),
            },
            "gp048": {
                "context_active": (
                    gp048_status.get(
                        "context_active",
                        0,
                    )
                ),
                "context_revoked": (
                    gp048_status.get(
                        "context_revoked",
                        0,
                    )
                ),
                "context_expired": (
                    gp048_status.get(
                        "context_expired",
                        0,
                    )
                ),
                "entry_allowed": (
                    gp048_status.get(
                        "entry_allowed",
                        0,
                    )
                ),
                "entry_denied": (
                    gp048_status.get(
                        "entry_denied",
                        0,
                    )
                ),
            },
            "gp049": {
                "closeout_total": (
                    gp049_status.get(
                        "closeout_total",
                        0,
                    )
                ),
                "lockback_required": (
                    gp049_status.get(
                        "lockback_required",
                        0,
                    )
                ),
                "lockback_acknowledged": (
                    gp049_status.get(
                        "lockback_acknowledged",
                        0,
                    )
                ),
            },
        },
        "safety_checks": (
            safety_checks
        ),
        "authority_boundary": {
            "tower_launch_authorized": False,
            "tower_identity_approved": False,
            "tower_clearance_approved": False,
            "tower_step_up_approved": False,
            "room_entry_authorized": False,
            "production_authority_granted": False,
        },
    }


def evaluate_owner_rehearsal_readiness(
    owner_id: str,
    *,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
    persist: bool = True,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_readiness_database(
        database
    )

    normalized_owner_id = str(
        owner_id
        or ""
    ).strip()

    if not _valid_owner_id(
        normalized_owner_id
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "valid_owner_id_required"
            ),
            "local_readiness_passed": False,
            "recommendation": (
                HOLD_RECOMMENDATION
            ),
            "tower_launch_authorized": False,
            "production_authority_granted": False,
        }

    evidence = (
        _collect_readiness_evidence(
            owner_id=normalized_owner_id,
            path=database,
            now=now,
        )
    )

    blockers: List[str] = []

    service_markers = evidence[
        "service_markers"
    ]

    for pack_name, passed in (
        service_markers.items()
    ):
        if not passed:
            blockers.append(
                f"{pack_name}_service_marker_missing"
            )

    if not evidence[
        "room_registry"
    ][
        "matches_expected"
    ]:
        blockers.append(
            "six_room_registry_mismatch"
        )

    owner_state = evidence[
        "owner_state"
    ]

    if owner_state[
        "active_session_count"
    ] > 0:
        blockers.append(
            "owner_active_protected_launch_session"
        )

    if owner_state[
        "active_context_count"
    ] > 0:
        blockers.append(
            "owner_active_protected_room_context"
        )

    if owner_state[
        "pending_lockback_count"
    ] > 0:
        blockers.append(
            "owner_pending_tower_lockback"
        )

    for check_name, passed in (
        evidence[
            "safety_checks"
        ].items()
    ):
        if not passed:
            blockers.append(
                "safety_check_failed:"
                + check_name
            )

    blockers = _unique(
        blockers
    )

    local_readiness_passed = (
        len(blockers) == 0
    )

    recommendation = (
        READY_RECOMMENDATION
        if local_readiness_passed
        else HOLD_RECOMMENDATION
    )

    snapshot_material = {
        "owner_id": (
            normalized_owner_id
        ),
        "recommendation": (
            recommendation
        ),
        "local_readiness_passed": (
            local_readiness_passed
        ),
        "reason_codes": (
            blockers
        ),
        "service_markers": evidence[
            "service_markers"
        ],
        "room_registry": evidence[
            "room_registry"
        ],
        "owner_state": evidence[
            "owner_state"
        ],
        "corridor_status": evidence[
            "corridor_status"
        ],
        "safety_checks": evidence[
            "safety_checks"
        ],
        "authority_boundary": evidence[
            "authority_boundary"
        ],
    }

    snapshot_hash = _sha256_text(
        _canonical_json(
            snapshot_material
        )
    )

    if not persist:
        return {
            "ok": True,
            "created": False,
            "persisted": False,
            "idempotent": False,
            "recommendation": (
                recommendation
            ),
            "local_readiness_passed": (
                local_readiness_passed
            ),
            "reason_codes": (
                blockers
            ),
            "evidence": evidence,
            "snapshot_hash": (
                snapshot_hash
            ),
            "tower_launch_authorized": False,
            "tower_identity_approved": False,
            "tower_clearance_approved": False,
            "tower_step_up_approved": False,
            "room_entry_authorized": False,
            "production_authority_granted": False,
        }

    with _connect(
        database
    ) as connection:
        existing = connection.execute(
            """
            SELECT *
            FROM ob_protected_launch_readiness_assessments
            WHERE owner_id = ?
              AND snapshot_hash = ?
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (
                normalized_owner_id,
                snapshot_hash,
            ),
        ).fetchone()

        if existing is not None:
            return {
                "ok": True,
                "created": False,
                "persisted": True,
                "idempotent": True,
                "reason_code": (
                    "readiness_snapshot_already_recorded"
                ),
                "assessment": (
                    _public_assessment(
                        existing
                    )
                ),
                "tower_launch_authorized": False,
                "production_authority_granted": False,
            }

        assessment_id = (
            "ob_readiness_"
            + secrets.token_urlsafe(
                20
            )
            .replace(
                "-",
                "",
            )
            .replace(
                "_",
                "",
            )
        )

        created_at = _iso(
            _now(
                now
            )
        )

        previous_assessment_hash = (
            _latest_assessment_hash(
                connection
            )
        )

        record = {
            "assessment_id": (
                assessment_id
            ),
            "owner_id": (
                normalized_owner_id
            ),
            "recommendation": (
                recommendation
            ),
            "local_readiness_passed": (
                local_readiness_passed
            ),
            "reason_codes": (
                blockers
            ),
            "evidence": evidence,
            "snapshot_hash": (
                snapshot_hash
            ),
            "previous_assessment_hash": (
                previous_assessment_hash
            ),
            "created_at": (
                created_at
            ),
        }

        assessment_hash = _sha256_text(
            _canonical_json(
                _assessment_hash_material(
                    record
                )
            )
        )

        connection.execute(
            """
            INSERT INTO
            ob_protected_launch_readiness_assessments (
                assessment_id,
                owner_id,
                recommendation,
                local_readiness_passed,
                reason_codes_json,
                evidence_json,
                snapshot_hash,
                previous_assessment_hash,
                assessment_hash,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                assessment_id,
                normalized_owner_id,
                recommendation,
                (
                    1
                    if local_readiness_passed
                    else 0
                ),
                _json_text(
                    blockers
                ),
                _json_text(
                    evidence
                ),
                snapshot_hash,
                previous_assessment_hash,
                assessment_hash,
                created_at,
            ),
        )

        connection.commit()

    assessment = (
        get_readiness_assessment(
            assessment_id,
            path=database,
        )
    )

    return {
        "ok": True,
        "created": True,
        "persisted": True,
        "idempotent": False,
        "reason_code": (
            "owner_rehearsal_readiness_recorded"
        ),
        "assessment": assessment,
        "tower_launch_authorized": False,
        "tower_identity_approved": False,
        "tower_clearance_approved": False,
        "tower_step_up_approved": False,
        "room_entry_authorized": False,
        "production_authority_granted": False,
    }


def verify_readiness_assessment(
    assessment_id: str,
    *,
    path: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_readiness_database(
        database
    )

    with _connect(
        database
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_protected_launch_readiness_assessments
            WHERE assessment_id = ?
            """,
            (
                str(
                    assessment_id
                ),
            ),
        ).fetchone()

        if row is None:
            return {
                "verified": False,
                "reason_codes": [
                    "readiness_assessment_not_found"
                ],
            }

        try:
            reason_codes = json.loads(
                row[
                    "reason_codes_json"
                ]
            )

            evidence = json.loads(
                row[
                    "evidence_json"
                ]
            )

        except Exception:
            return {
                "verified": False,
                "reason_codes": [
                    "readiness_assessment_json_invalid"
                ],
            }

        record = {
            "assessment_id": row[
                "assessment_id"
            ],
            "owner_id": row[
                "owner_id"
            ],
            "recommendation": row[
                "recommendation"
            ],
            "local_readiness_passed": bool(
                row[
                    "local_readiness_passed"
                ]
            ),
            "reason_codes": (
                reason_codes
            ),
            "evidence": evidence,
            "snapshot_hash": row[
                "snapshot_hash"
            ],
            "previous_assessment_hash": row[
                "previous_assessment_hash"
            ],
            "created_at": row[
                "created_at"
            ],
        }

        computed_assessment_hash = (
            _sha256_text(
                _canonical_json(
                    _assessment_hash_material(
                        record
                    )
                )
            )
        )

        snapshot_material = {
            "owner_id": row[
                "owner_id"
            ],
            "recommendation": row[
                "recommendation"
            ],
            "local_readiness_passed": bool(
                row[
                    "local_readiness_passed"
                ]
            ),
            "reason_codes": (
                reason_codes
            ),
            "service_markers": evidence[
                "service_markers"
            ],
            "room_registry": evidence[
                "room_registry"
            ],
            "owner_state": evidence[
                "owner_state"
            ],
            "corridor_status": evidence[
                "corridor_status"
            ],
            "safety_checks": evidence[
                "safety_checks"
            ],
            "authority_boundary": evidence[
                "authority_boundary"
            ],
        }

        computed_snapshot_hash = (
            _sha256_text(
                _canonical_json(
                    snapshot_material
                )
            )
        )

        checks = {
            "assessment_hash_matches": (
                hmac.compare_digest(
                    computed_assessment_hash,
                    str(
                        row[
                            "assessment_hash"
                        ]
                    ),
                )
            ),
            "snapshot_hash_matches": (
                hmac.compare_digest(
                    computed_snapshot_hash,
                    str(
                        row[
                            "snapshot_hash"
                        ]
                    ),
                )
            ),
            "previous_assessment_hash_valid": True,
            "recommendation_valid": (
                row[
                    "recommendation"
                ]
                in {
                    READY_RECOMMENDATION,
                    HOLD_RECOMMENDATION,
                }
            ),
            "ready_state_consistent": (
                (
                    bool(
                        row[
                            "local_readiness_passed"
                        ]
                    )
                    and row[
                        "recommendation"
                    ]
                    == READY_RECOMMENDATION
                    and len(
                        reason_codes
                    )
                    == 0
                )
                or (
                    not bool(
                        row[
                            "local_readiness_passed"
                        ]
                    )
                    and row[
                        "recommendation"
                    ]
                    == HOLD_RECOMMENDATION
                    and len(
                        reason_codes
                    )
                    > 0
                )
            ),
            "authority_boundary_preserved": (
                evidence[
                    "authority_boundary"
                ][
                    "tower_launch_authorized"
                ]
                is False
                and evidence[
                    "authority_boundary"
                ][
                    "production_authority_granted"
                ]
                is False
            ),
        }

        if (
            row[
                "previous_assessment_hash"
            ]
            != ZERO_HASH
        ):
            previous = connection.execute(
                """
                SELECT 1
                FROM ob_protected_launch_readiness_assessments
                WHERE assessment_hash = ?
                LIMIT 1
                """,
                (
                    row[
                        "previous_assessment_hash"
                    ],
                ),
            ).fetchone()

            checks[
                "previous_assessment_hash_valid"
            ] = previous is not None

    return {
        "verified": all(
            checks.values()
        ),
        "checks": checks,
        "assessment_id": str(
            assessment_id
        ),
        "recommendation": row[
            "recommendation"
        ],
        "local_readiness_passed": bool(
            row[
                "local_readiness_passed"
            ]
        ),
        "assessment_hash": row[
            "assessment_hash"
        ],
        "snapshot_hash": row[
            "snapshot_hash"
        ],
        "tower_launch_authorized": False,
        "production_authority_granted": False,
    }


def protected_launch_corridor_status(
    *,
    path: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_readiness_database(
        database
    )

    with _connect(
        database
    ) as connection:
        totals = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE
                        WHEN local_readiness_passed = 1
                        THEN 1 ELSE 0
                    END
                ) AS ready,
                SUM(
                    CASE
                        WHEN local_readiness_passed = 0
                        THEN 1 ELSE 0
                    END
                ) AS hold
            FROM ob_protected_launch_readiness_assessments
            """
        ).fetchone()

    return {
        "ok": True,
        "pack": PACK,
        "contract_version": CONTRACT_VERSION,
        "database_path": str(
            database
        ),
        "assessment_total": int(
            totals[
                "total"
            ]
            or 0
        ),
        "ready_assessment_total": int(
            totals[
                "ready"
            ]
            or 0
        ),
        "hold_assessment_total": int(
            totals[
                "hold"
            ]
            or 0
        ),
        "corridor_packs": [
            "GP046",
            "GP047",
            "GP048",
            "GP049",
            "GP050",
        ],
        "expected_room_count": 6,
        "ready_means_local_ob_readiness_only": True,
        "tower_launch_authorized": False,
        "tower_identity_approved": False,
        "tower_clearance_approved": False,
        "tower_step_up_approved": False,
        "room_entry_authorized": False,
        "tower_remains_launch_authority": True,
        "http_assessment_enabled": (
            os.environ.get(
                "OB_PROTECTED_LAUNCH_READINESS_HTTP_ENABLED",
                "0",
            )
            == "1"
        ),
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
    }
