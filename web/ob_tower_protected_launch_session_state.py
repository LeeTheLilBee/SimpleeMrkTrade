
"""OB GP047 — Protected Launch Session State and Active Room Binding.

Tower remains the source of authority for identity, clearance, step-up,
route approval, launch approval, expiration, revocation and lockback.

OB only binds an accepted GP046 launch intake to one local, temporary,
single-room operating session. The local session never grants production
Manual Live authority and never extends the Tower-issued expiration.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import tempfile

from web.ob_tower_protected_launch_handoff_consumer import (
    ROOM_REGISTRY,
    consume_tower_protected_launch_handoff,
    get_tower_protected_launch_handoff,
    verify_tower_protected_launch_handoff,
)


OB_GIANT_PACK_047_PROTECTED_LAUNCH_SESSION_STATE_SERVICE = True

PACK = "GP047"
CONTRACT_VERSION = "ob.protected_launch_session.v1"
ZERO_HASH = "0" * 64

ACTIVE_STATES = {
    "reserved",
    "active",
}

TERMINAL_STATES = {
    "closed",
    "expired",
    "activation_failed",
}


def _default_database_path() -> Path:
    configured = (
        os.environ.get(
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
        / "ob_tower_protected_launch_gp047.sqlite3"
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


def init_session_database(
    path: Optional[Any] = None,
) -> str:
    database = _database_path(
        path
    )

    with _connect(
        database
    ) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS
            ob_tower_launch_sessions (
                session_state_id TEXT PRIMARY KEY,
                intake_id TEXT NOT NULL UNIQUE,
                handoff_id TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                tower_session_id TEXT NOT NULL,
                room_id TEXT NOT NULL,
                canonical_route TEXT NOT NULL,
                mode TEXT NOT NULL,
                state TEXT NOT NULL,
                started_at TEXT,
                last_seen_at TEXT,
                expires_at TEXT NOT NULL,
                closed_at TEXT,
                close_reason TEXT,
                launch_packet_hash TEXT NOT NULL,
                launch_record_hash TEXT NOT NULL,
                previous_session_hash TEXT NOT NULL,
                session_hash TEXT NOT NULL UNIQUE,
                close_hash TEXT,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_tower_launch_session_owner
            ON ob_tower_launch_sessions(
                owner_id,
                state
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_tower_launch_session_tower_session
            ON ob_tower_launch_sessions(
                tower_session_id
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_tower_launch_session_room
            ON ob_tower_launch_sessions(
                room_id,
                state
            );

            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_ob_tower_one_active_owner
            ON ob_tower_launch_sessions(
                owner_id
            )
            WHERE state IN (
                'reserved',
                'active'
            );

            CREATE TABLE IF NOT EXISTS
            ob_tower_launch_session_events (
                event_id TEXT PRIMARY KEY,
                session_state_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                previous_event_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                FOREIGN KEY(
                    session_state_id
                )
                REFERENCES ob_tower_launch_sessions(
                    session_state_id
                )
            );

            CREATE INDEX IF NOT EXISTS
idx_ob_tower_launch_session_events_session
ON ob_tower_launch_session_events(
    session_state_id,
    created_at
);
            """
        )

    return str(
        database
    )


def _latest_session_hash(
    connection: sqlite3.Connection,
) -> str:
    row = connection.execute(
        """
        SELECT session_hash
        FROM ob_tower_launch_sessions
        ORDER BY rowid DESC
        LIMIT 1
        """
    ).fetchone()

    if row is None:
        return ZERO_HASH

    return str(
        row["session_hash"]
    )


def _latest_event_hash(
    connection: sqlite3.Connection,
    session_state_id: str,
) -> str:
    row = connection.execute(
        """
        SELECT event_hash
        FROM ob_tower_launch_session_events
        WHERE session_state_id = ?
        ORDER BY rowid DESC
        LIMIT 1
        """,
        (
            str(
                session_state_id
            ),
        ),
    ).fetchone()

    if row is None:
        return ZERO_HASH

    return str(
        row["event_hash"]
    )


def _session_hash_material(
    record: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "session_state_id": record[
            "session_state_id"
        ],
        "intake_id": record[
            "intake_id"
        ],
        "handoff_id": record[
            "handoff_id"
        ],
        "owner_id": record[
            "owner_id"
        ],
        "tower_session_id": record[
            "tower_session_id"
        ],
        "room_id": record[
            "room_id"
        ],
        "canonical_route": record[
            "canonical_route"
        ],
        "mode": record[
            "mode"
        ],
        "expires_at": record[
            "expires_at"
        ],
        "launch_packet_hash": record[
            "launch_packet_hash"
        ],
        "launch_record_hash": record[
            "launch_record_hash"
        ],
        "previous_session_hash": record[
            "previous_session_hash"
        ],
        "created_at": record[
            "created_at"
        ],
        "tower_authority_required": True,
        "ob_self_authorization_allowed": False,
        "production_authority_granted": False,
    }


def _close_hash_material(
    row: sqlite3.Row,
    *,
    state: str,
    closed_at: str,
    close_reason: str,
) -> Dict[str, Any]:
    return {
        "session_state_id": row[
            "session_state_id"
        ],
        "session_hash": row[
            "session_hash"
        ],
        "state": state,
        "closed_at": closed_at,
        "close_reason": close_reason,
        "tower_lockback_required": True,
        "ob_room_access_active": False,
        "production_authority_granted": False,
    }


def _append_event(
    connection: sqlite3.Connection,
    *,
    session_state_id: str,
    event_type: str,
    payload: Dict[str, Any],
    created_at: str,
) -> Dict[str, Any]:
    previous_event_hash = (
        _latest_event_hash(
            connection,
            session_state_id,
        )
    )

    event_id = (
        "ob_session_evt_"
        + secrets.token_urlsafe(
            18
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

    material = {
        "event_id": event_id,
        "session_state_id": (
            session_state_id
        ),
        "event_type": (
            event_type
        ),
        "payload": payload,
        "previous_event_hash": (
            previous_event_hash
        ),
        "created_at": (
            created_at
        ),
    }

    event_hash = _sha256_text(
        _canonical_json(
            material
        )
    )

    connection.execute(
        """
        INSERT INTO
        ob_tower_launch_session_events (
            event_id,
            session_state_id,
            event_type,
            payload_json,
            previous_event_hash,
            event_hash,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            session_state_id,
            event_type,
            _json_text(
                payload
            ),
            previous_event_hash,
            event_hash,
            created_at,
        ),
    )

    return {
        **material,
        "event_hash": (
            event_hash
        ),
    }


def _public_session(
    row: sqlite3.Row,
) -> Dict[str, Any]:
    return {
        "session_state_id": row[
            "session_state_id"
        ],
        "intake_id": row[
            "intake_id"
        ],
        "handoff_id": row[
            "handoff_id"
        ],
        "owner_id": row[
            "owner_id"
        ],
        "tower_session_id": row[
            "tower_session_id"
        ],
        "room_id": row[
            "room_id"
        ],
        "canonical_route": row[
            "canonical_route"
        ],
        "mode": row[
            "mode"
        ],
        "state": row[
            "state"
        ],
        "active": (
            row["state"]
            == "active"
        ),
        "started_at": row[
            "started_at"
        ],
        "last_seen_at": row[
            "last_seen_at"
        ],
        "expires_at": row[
            "expires_at"
        ],
        "closed_at": row[
            "closed_at"
        ],
        "close_reason": row[
            "close_reason"
        ],
        "launch_packet_hash": row[
            "launch_packet_hash"
        ],
        "launch_record_hash": row[
            "launch_record_hash"
        ],
        "previous_session_hash": row[
            "previous_session_hash"
        ],
        "session_hash": row[
            "session_hash"
        ],
        "close_hash": row[
            "close_hash"
        ],
        "created_at": row[
            "created_at"
        ],
        "tower_authority_required": True,
        "ob_self_authorization_allowed": False,
        "room_switch_allowed": False,
        "expiration_extension_allowed": False,
        "tower_lockback_required_on_close": True,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
    }


def get_protected_launch_session(
    session_state_id: str,
    *,
    path: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    init_session_database(
        path
    )

    with _connect(
        path
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_tower_launch_sessions
            WHERE session_state_id = ?
            """,
            (
                str(
                    session_state_id
                ),
            ),
        ).fetchone()

    if row is None:
        return None

    return _public_session(
        row
    )


def list_protected_launch_sessions(
    *,
    owner_id: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 100,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    expire_stale_protected_launch_sessions(
        path=path,
        now=now,
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
        FROM ob_tower_launch_sessions
    """

    clauses: List[str] = []
    parameters: List[Any] = []

    if owner_id:
        clauses.append(
            "owner_id = ?"
        )

        parameters.append(
            str(owner_id)
        )

    if state:
        clauses.append(
            "state = ?"
        )

        parameters.append(
            str(state)
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
        _public_session(
            row
        )
        for row in rows
    ]


def _expire_row(
    connection: sqlite3.Connection,
    row: sqlite3.Row,
    *,
    current_time: datetime,
) -> Dict[str, Any]:
    closed_at = _iso(
        current_time
    )

    close_reason = (
        "tower_launch_expired"
    )

    close_hash = _sha256_text(
        _canonical_json(
            _close_hash_material(
                row,
                state="expired",
                closed_at=closed_at,
                close_reason=(
                    close_reason
                ),
            )
        )
    )

    connection.execute(
        """
        UPDATE ob_tower_launch_sessions
        SET
            state = 'expired',
            closed_at = ?,
            close_reason = ?,
            close_hash = ?
        WHERE session_state_id = ?
          AND state IN (
              'reserved',
              'active'
          )
        """,
        (
            closed_at,
            close_reason,
            close_hash,
            row[
                "session_state_id"
            ],
        ),
    )

    _append_event(
        connection,
        session_state_id=row[
            "session_state_id"
        ],
        event_type=(
            "session_expired"
        ),
        payload={
            "expired_at": (
                closed_at
            ),
            "tower_expiration": row[
                "expires_at"
            ],
            "tower_lockback_required": True,
            "ob_room_access_active": False,
        },
        created_at=closed_at,
    )

    return {
        "session_state_id": row[
            "session_state_id"
        ],
        "state": "expired",
        "closed_at": closed_at,
        "close_hash": close_hash,
    }


def expire_stale_protected_launch_sessions(
    *,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_session_database(
        database
    )

    current_time = _now(
        now
    )

    expired = []

    with _connect(
        database
    ) as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM ob_tower_launch_sessions
            WHERE state IN (
                'reserved',
                'active'
            )
            """
        ).fetchall()

        for row in rows:
            try:
                expires_at = (
                    _parse_time(
                        row[
                            "expires_at"
                        ]
                    )
                )

            except Exception:
                expires_at = (
                    current_time
                )

            if (
                expires_at.timestamp()
                <= current_time.timestamp()
            ):
                expired.append(
                    _expire_row(
                        connection,
                        row,
                        current_time=(
                            current_time
                        ),
                    )
                )

        connection.commit()

    return {
        "ok": True,
        "expired_count": len(
            expired
        ),
        "expired": expired,
        "production_authority_granted": False,
    }


def resolve_active_room_binding(
    *,
    owner_id: str,
    tower_session_id: Optional[str] = None,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    expire_stale_protected_launch_sessions(
        path=path,
        now=now,
    )

    query = """
        SELECT *
        FROM ob_tower_launch_sessions
        WHERE owner_id = ?
          AND state = 'active'
    """

    parameters: List[Any] = [
        str(owner_id),
    ]

    if tower_session_id:
        query += """
          AND tower_session_id = ?
        """

        parameters.append(
            str(
                tower_session_id
            )
        )

    query += """
        ORDER BY rowid DESC
        LIMIT 1
    """

    with _connect(
        path
    ) as connection:
        row = connection.execute(
            query,
            parameters,
        ).fetchone()

    if row is None:
        return {
            "ok": True,
            "active": False,
            "binding": None,
            "reason_code": (
                "no_active_room_binding"
            ),
            "production_authority_granted": False,
        }

    session = _public_session(
        row
    )

    return {
        "ok": True,
        "active": True,
        "binding": {
            "session_state_id": session[
                "session_state_id"
            ],
            "owner_id": session[
                "owner_id"
            ],
            "tower_session_id": session[
                "tower_session_id"
            ],
            "room_id": session[
                "room_id"
            ],
            "canonical_route": session[
                "canonical_route"
            ],
            "mode": session[
                "mode"
            ],
            "expires_at": session[
                "expires_at"
            ],
            "room_switch_allowed": False,
            "expiration_extension_allowed": False,
        },
        "reason_code": (
            "active_room_bound"
        ),
        "production_authority_granted": False,
    }


def start_protected_launch_session(
    intake_id: str,
    *,
    owner_id: Optional[str] = None,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_session_database(
        database
    )

    current_time = _now(
        now
    )

    expire_stale_protected_launch_sessions(
        path=database,
        now=current_time,
    )

    existing = None

    with _connect(
        database
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_tower_launch_sessions
            WHERE intake_id = ?
            """,
            (
                str(
                    intake_id
                ),
            ),
        ).fetchone()

        if row is not None:
            existing = (
                _public_session(
                    row
                )
            )

    if existing is not None:
        if existing[
            "state"
        ] == "active":
            return {
                "ok": True,
                "created": False,
                "idempotent": True,
                "reason_code": (
                    "session_already_active"
                ),
                "session": existing,
                "production_authority_granted": False,
            }

        return {
            "ok": False,
            "created": False,
            "idempotent": True,
            "reason_code": (
                "launch_intake_already_bound"
            ),
            "session": existing,
            "production_authority_granted": False,
        }

    intake = (
        get_tower_protected_launch_handoff(
            intake_id,
            path=database,
        )
    )

    if intake is None:
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "launch_intake_not_found"
            ),
            "production_authority_granted": False,
        }

    if not intake.get(
        "accepted"
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "launch_intake_not_accepted"
            ),
            "intake": intake,
            "production_authority_granted": False,
        }

    intake_verification = (
        verify_tower_protected_launch_handoff(
            intake_id,
            path=database,
        )
    )

    if not intake_verification.get(
        "verified"
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "launch_intake_integrity_failed"
            ),
            "verification": (
                intake_verification
            ),
            "production_authority_granted": False,
        }

    if intake.get(
        "consumed"
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "launch_handoff_already_consumed"
            ),
            "production_authority_granted": False,
        }

    expected_owner_id = str(
        intake.get(
            "owner_id"
        )
        or ""
    )

    if (
        owner_id
        and expected_owner_id
        and str(owner_id)
        != expected_owner_id
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "owner_identity_mismatch"
            ),
            "production_authority_granted": False,
        }

    normalized = intake.get(
        "normalized_packet"
    )

    if not isinstance(
        normalized,
        dict,
    ):
        normalized = {}

    tower_session_id = str(
        intake.get(
            "session_id"
        )
        or normalized.get(
            "session_id"
        )
        or ""
    )

    room_id = str(
        intake.get(
            "room_id"
        )
        or normalized.get(
            "room_id"
        )
        or ""
    )

    canonical_route = str(
        intake.get(
            "canonical_route"
        )
        or normalized.get(
            "canonical_route"
        )
        or ""
    )

    mode = str(
        intake.get(
            "mode"
        )
        or normalized.get(
            "mode"
        )
        or ""
    )

    handoff_id = str(
        intake.get(
            "handoff_id"
        )
        or normalized.get(
            "handoff_id"
        )
        or ""
    )

    expires_at_text = str(
        intake.get(
            "expires_at"
        )
        or normalized.get(
            "expires_at"
        )
        or ""
    )

    if room_id not in ROOM_REGISTRY:
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "unknown_room_id"
            ),
            "production_authority_granted": False,
        }

    room = ROOM_REGISTRY[
        room_id
    ]

    accepted_routes = {
        room[
            "canonical_route"
        ],
        *room[
            "accepted_aliases"
        ],
    }

    if (
        canonical_route
        not in accepted_routes
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "active_room_route_mismatch"
            ),
            "production_authority_granted": False,
        }

    try:
        expires_at = _parse_time(
            expires_at_text
        )

    except Exception:
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "invalid_launch_expiration"
            ),
            "production_authority_granted": False,
        }

    if (
        expires_at.timestamp()
        <= current_time.timestamp()
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "launch_expired_before_session_start"
            ),
            "production_authority_granted": False,
        }

    session_state_id = (
        "ob_session_"
        + secrets.token_urlsafe(
            18
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
        current_time
    )

    record = {
        "session_state_id": (
            session_state_id
        ),
        "intake_id": str(
            intake_id
        ),
        "handoff_id": (
            handoff_id
        ),
        "owner_id": (
            expected_owner_id
        ),
        "tower_session_id": (
            tower_session_id
        ),
        "room_id": (
            room_id
        ),
        "canonical_route": (
            canonical_route
        ),
        "mode": (
            mode
        ),
        "expires_at": (
            expires_at_text
        ),
        "launch_packet_hash": str(
            intake.get(
                "packet_hash"
            )
            or ""
        ),
        "launch_record_hash": str(
            intake.get(
                "record_hash"
            )
            or ""
        ),
        "previous_session_hash": "",
        "created_at": (
            created_at
        ),
    }

    try:
        with _connect(
            database
        ) as connection:
            active_owner = (
                connection.execute(
                    """
                    SELECT *
                    FROM ob_tower_launch_sessions
                    WHERE owner_id = ?
                      AND state IN (
                          'reserved',
                          'active'
                      )
                    ORDER BY rowid DESC
                    LIMIT 1
                    """,
                    (
                        expected_owner_id,
                    ),
                ).fetchone()
            )

            if active_owner is not None:
                return {
                    "ok": False,
                    "created": False,
                    "reason_code": (
                        "owner_active_room_conflict"
                    ),
                    "active_session": (
                        _public_session(
                            active_owner
                        )
                    ),
                    "production_authority_granted": False,
                }

            record[
                "previous_session_hash"
            ] = _latest_session_hash(
                connection
            )

            session_hash = _sha256_text(
                _canonical_json(
                    _session_hash_material(
                        record
                    )
                )
            )

            connection.execute(
                """
                INSERT INTO
                ob_tower_launch_sessions (
                    session_state_id,
                    intake_id,
                    handoff_id,
                    owner_id,
                    tower_session_id,
                    room_id,
                    canonical_route,
                    mode,
                    state,
                    started_at,
                    last_seen_at,
                    expires_at,
                    closed_at,
                    close_reason,
                    launch_packet_hash,
                    launch_record_hash,
                    previous_session_hash,
                    session_hash,
                    close_hash,
                    created_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, 'reserved',
                    NULL, NULL, ?, NULL, NULL, ?, ?, ?, ?, NULL, ?
                )
                """,
                (
                    session_state_id,
                    str(
                        intake_id
                    ),
                    handoff_id,
                    expected_owner_id,
                    tower_session_id,
                    room_id,
                    canonical_route,
                    mode,
                    expires_at_text,
                    record[
                        "launch_packet_hash"
                    ],
                    record[
                        "launch_record_hash"
                    ],
                    record[
                        "previous_session_hash"
                    ],
                    session_hash,
                    created_at,
                ),
            )

            _append_event(
                connection,
                session_state_id=(
                    session_state_id
                ),
                event_type=(
                    "session_reserved"
                ),
                payload={
                    "intake_id": (
                        str(
                            intake_id
                        )
                    ),
                    "room_id": (
                        room_id
                    ),
                    "canonical_route": (
                        canonical_route
                    ),
                    "expires_at": (
                        expires_at_text
                    ),
                    "tower_authority_required": True,
                },
                created_at=(
                    created_at
                ),
            )

            connection.commit()

    except sqlite3.IntegrityError:
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "owner_active_room_conflict"
            ),
            "production_authority_granted": False,
        }

    consume_result = (
        consume_tower_protected_launch_handoff(
            intake_id,
            owner_id=(
                expected_owner_id
            ),
            path=database,
            now=current_time,
        )
    )

    if not consume_result.get(
        "ok"
    ):
        failed_at = _iso(
            current_time
        )

        with _connect(
            database
        ) as connection:
            row = connection.execute(
                """
                SELECT *
                FROM ob_tower_launch_sessions
                WHERE session_state_id = ?
                """,
                (
                    session_state_id,
                ),
            ).fetchone()

            if row is not None:
                close_reason = str(
                    consume_result.get(
                        "reason_code"
                    )
                    or "handoff_consumption_failed"
                )

                close_hash = _sha256_text(
                    _canonical_json(
                        _close_hash_material(
                            row,
                            state=(
                                "activation_failed"
                            ),
                            closed_at=(
                                failed_at
                            ),
                            close_reason=(
                                close_reason
                            ),
                        )
                    )
                )

                connection.execute(
                    """
                    UPDATE ob_tower_launch_sessions
                    SET
                        state = 'activation_failed',
                        closed_at = ?,
                        close_reason = ?,
                        close_hash = ?
                    WHERE session_state_id = ?
                    """,
                    (
                        failed_at,
                        close_reason,
                        close_hash,
                        session_state_id,
                    ),
                )

                _append_event(
                    connection,
                    session_state_id=(
                        session_state_id
                    ),
                    event_type=(
                        "session_activation_failed"
                    ),
                    payload={
                        "reason_code": (
                            close_reason
                        ),
                        "tower_lockback_required": True,
                        "ob_room_access_active": False,
                    },
                    created_at=(
                        failed_at
                    ),
                )

                connection.commit()

        return {
            "ok": False,
            "created": True,
            "reason_code": (
                "handoff_consumption_failed"
            ),
            "consume_result": (
                consume_result
            ),
            "session": (
                get_protected_launch_session(
                    session_state_id,
                    path=database,
                )
            ),
            "production_authority_granted": False,
        }

    started_at = _iso(
        current_time
    )

    with _connect(
        database
    ) as connection:
        connection.execute(
            """
            UPDATE ob_tower_launch_sessions
            SET
                state = 'active',
                started_at = ?,
                last_seen_at = ?
            WHERE session_state_id = ?
              AND state = 'reserved'
            """,
            (
                started_at,
                started_at,
                session_state_id,
            ),
        )

        _append_event(
            connection,
            session_state_id=(
                session_state_id
            ),
            event_type=(
                "session_started"
            ),
            payload={
                "started_at": (
                    started_at
                ),
                "room_id": (
                    room_id
                ),
                "canonical_route": (
                    canonical_route
                ),
                "handoff_consumed": True,
                "room_switch_allowed": False,
                "expiration_extension_allowed": False,
                "production_authority_granted": False,
            },
            created_at=(
                started_at
            ),
        )

        connection.commit()

    session = (
        get_protected_launch_session(
            session_state_id,
            path=database,
        )
    )

    return {
        "ok": True,
        "created": True,
        "idempotent": False,
        "reason_code": (
            "protected_launch_session_started"
        ),
        "session": session,
        "handoff_consumed": True,
        "tower_lockback_required_on_close": True,
        "production_authority_granted": False,
    }


def touch_protected_launch_session(
    session_state_id: str,
    *,
    owner_id: Optional[str] = None,
    tower_session_id: Optional[str] = None,
    room_id: Optional[str] = None,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_session_database(
        database
    )

    current_time = _now(
        now
    )

    expire_stale_protected_launch_sessions(
        path=database,
        now=current_time,
    )

    with _connect(
        database
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_tower_launch_sessions
            WHERE session_state_id = ?
            """,
            (
                str(
                    session_state_id
                ),
            ),
        ).fetchone()

        if row is None:
            return {
                "ok": False,
                "touched": False,
                "reason_code": (
                    "protected_launch_session_not_found"
                ),
            }

        if row["state"] != "active":
            return {
                "ok": False,
                "touched": False,
                "reason_code": (
                    "protected_launch_session_not_active"
                ),
                "session": (
                    _public_session(
                        row
                    )
                ),
            }

        if (
            owner_id
            and str(owner_id)
            != str(
                row[
                    "owner_id"
                ]
            )
        ):
            return {
                "ok": False,
                "touched": False,
                "reason_code": (
                    "owner_identity_mismatch"
                ),
            }

        if (
            tower_session_id
            and str(
                tower_session_id
            )
            != str(
                row[
                    "tower_session_id"
                ]
            )
        ):
            return {
                "ok": False,
                "touched": False,
                "reason_code": (
                    "tower_session_identity_mismatch"
                ),
            }

        if (
            room_id
            and str(room_id)
            != str(
                row[
                    "room_id"
                ]
            )
        ):
            return {
                "ok": False,
                "touched": False,
                "reason_code": (
                    "active_room_binding_mismatch"
                ),
                "bound_room_id": row[
                    "room_id"
                ],
            }

        touched_at = _iso(
            current_time
        )

        connection.execute(
            """
            UPDATE ob_tower_launch_sessions
            SET last_seen_at = ?
            WHERE session_state_id = ?
              AND state = 'active'
            """,
            (
                touched_at,
                str(
                    session_state_id
                ),
            ),
        )

        _append_event(
            connection,
            session_state_id=str(
                session_state_id
            ),
            event_type=(
                "session_touched"
            ),
            payload={
                "touched_at": (
                    touched_at
                ),
                "room_id": row[
                    "room_id"
                ],
                "expiration_unchanged": True,
                "expires_at": row[
                    "expires_at"
                ],
            },
            created_at=(
                touched_at
            ),
        )

        connection.commit()

    return {
        "ok": True,
        "touched": True,
        "reason_code": (
            "protected_launch_session_touched"
        ),
        "session": (
            get_protected_launch_session(
                session_state_id,
                path=database,
            )
        ),
        "expiration_extended": False,
        "production_authority_granted": False,
    }


def close_protected_launch_session(
    session_state_id: str,
    *,
    owner_id: Optional[str] = None,
    reason: str = (
        "owner_session_complete"
    ),
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_session_database(
        database
    )

    current_time = _now(
        now
    )

    with _connect(
        database
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_tower_launch_sessions
            WHERE session_state_id = ?
            """,
            (
                str(
                    session_state_id
                ),
            ),
        ).fetchone()

        if row is None:
            return {
                "ok": False,
                "closed": False,
                "reason_code": (
                    "protected_launch_session_not_found"
                ),
            }

        if (
            owner_id
            and str(owner_id)
            != str(
                row[
                    "owner_id"
                ]
            )
        ):
            return {
                "ok": False,
                "closed": False,
                "reason_code": (
                    "owner_identity_mismatch"
                ),
            }

        if row[
            "state"
        ] in TERMINAL_STATES:
            return {
                "ok": True,
                "closed": True,
                "idempotent": True,
                "reason_code": (
                    "protected_launch_session_already_closed"
                ),
                "session": (
                    _public_session(
                        row
                    )
                ),
                "tower_lockback_required": True,
                "production_authority_granted": False,
            }

        closed_at = _iso(
            current_time
        )

        close_reason = str(
            reason
            or "owner_session_complete"
        ).strip()

        close_hash = _sha256_text(
            _canonical_json(
                _close_hash_material(
                    row,
                    state="closed",
                    closed_at=(
                        closed_at
                    ),
                    close_reason=(
                        close_reason
                    ),
                )
            )
        )

        connection.execute(
            """
            UPDATE ob_tower_launch_sessions
            SET
                state = 'closed',
                closed_at = ?,
                close_reason = ?,
                close_hash = ?
            WHERE session_state_id = ?
              AND state IN (
                  'reserved',
                  'active'
              )
            """,
            (
                closed_at,
                close_reason,
                close_hash,
                str(
                    session_state_id
                ),
            ),
        )

        _append_event(
            connection,
            session_state_id=str(
                session_state_id
            ),
            event_type=(
                "session_closed"
            ),
            payload={
                "closed_at": (
                    closed_at
                ),
                "close_reason": (
                    close_reason
                ),
                "tower_lockback_required": True,
                "ob_room_access_active": False,
                "step_up_reuse_allowed": False,
                "production_authority_granted": False,
            },
            created_at=(
                closed_at
            ),
        )

        connection.commit()

    return {
        "ok": True,
        "closed": True,
        "idempotent": False,
        "reason_code": (
            "protected_launch_session_closed"
        ),
        "session": (
            get_protected_launch_session(
                session_state_id,
                path=database,
            )
        ),
        "tower_lockback_required": True,
        "ob_room_access_active": False,
        "production_authority_granted": False,
    }


def verify_protected_launch_session(
    session_state_id: str,
    *,
    path: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_session_database(
        database
    )

    with _connect(
        database
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_tower_launch_sessions
            WHERE session_state_id = ?
            """,
            (
                str(
                    session_state_id
                ),
            ),
        ).fetchone()

        if row is None:
            return {
                "verified": False,
                "reason_codes": [
                    "protected_launch_session_not_found"
                ],
            }

        record = {
            "session_state_id": row[
                "session_state_id"
            ],
            "intake_id": row[
                "intake_id"
            ],
            "handoff_id": row[
                "handoff_id"
            ],
            "owner_id": row[
                "owner_id"
            ],
            "tower_session_id": row[
                "tower_session_id"
            ],
            "room_id": row[
                "room_id"
            ],
            "canonical_route": row[
                "canonical_route"
            ],
            "mode": row[
                "mode"
            ],
            "expires_at": row[
                "expires_at"
            ],
            "launch_packet_hash": row[
                "launch_packet_hash"
            ],
            "launch_record_hash": row[
                "launch_record_hash"
            ],
            "previous_session_hash": row[
                "previous_session_hash"
            ],
            "created_at": row[
                "created_at"
            ],
        }

        computed_session_hash = (
            _sha256_text(
                _canonical_json(
                    _session_hash_material(
                        record
                    )
                )
            )
        )

        checks = {
            "session_hash_matches": (
                hmac.compare_digest(
                    computed_session_hash,
                    str(
                        row[
                            "session_hash"
                        ]
                    ),
                )
            ),
            "previous_session_hash_valid": True,
            "launch_intake_verified": False,
            "launch_handoff_consumed": False,
            "launch_record_hash_matches": False,
            "room_registry_matches": False,
            "close_hash_valid": True,
            "event_chain_valid": True,
        }

        if (
            row[
                "previous_session_hash"
            ]
            != ZERO_HASH
        ):
            previous = connection.execute(
                """
                SELECT 1
                FROM ob_tower_launch_sessions
                WHERE session_hash = ?
                LIMIT 1
                """,
                (
                    row[
                        "previous_session_hash"
                    ],
                ),
            ).fetchone()

            checks[
                "previous_session_hash_valid"
            ] = previous is not None

        room = ROOM_REGISTRY.get(
            row[
                "room_id"
            ]
        )

        if room is not None:
            checks[
                "room_registry_matches"
            ] = (
                row[
                    "canonical_route"
                ]
                in {
                    room[
                        "canonical_route"
                    ],
                    *room[
                        "accepted_aliases"
                    ],
                }
            )

        if row[
            "state"
        ] in TERMINAL_STATES:
            expected_close_hash = (
                _sha256_text(
                    _canonical_json(
                        _close_hash_material(
                            row,
                            state=row[
                                "state"
                            ],
                            closed_at=str(
                                row[
                                    "closed_at"
                                ]
                                or ""
                            ),
                            close_reason=str(
                                row[
                                    "close_reason"
                                ]
                                or ""
                            ),
                        )
                    )
                )
            )

            checks[
                "close_hash_valid"
            ] = hmac.compare_digest(
                str(
                    row[
                        "close_hash"
                    ]
                    or ""
                ),
                expected_close_hash,
            )

        events = connection.execute(
            """
            SELECT *
            FROM ob_tower_launch_session_events
            WHERE session_state_id = ?
            ORDER BY rowid ASC
            """,
            (
                str(
                    session_state_id
                ),
            ),
        ).fetchall()

        previous_event_hash = (
            ZERO_HASH
        )

        for event in events:
            try:
                payload = json.loads(
                    event[
                        "payload_json"
                    ]
                )

            except Exception:
                checks[
                    "event_chain_valid"
                ] = False
                break

            material = {
                "event_id": event[
                    "event_id"
                ],
                "session_state_id": event[
                    "session_state_id"
                ],
                "event_type": event[
                    "event_type"
                ],
                "payload": payload,
                "previous_event_hash": event[
                    "previous_event_hash"
                ],
                "created_at": event[
                    "created_at"
                ],
            }

            computed_event_hash = (
                _sha256_text(
                    _canonical_json(
                        material
                    )
                )
            )

            if (
                event[
                    "previous_event_hash"
                ]
                != previous_event_hash
            ):
                checks[
                    "event_chain_valid"
                ] = False
                break

            if not hmac.compare_digest(
                computed_event_hash,
                str(
                    event[
                        "event_hash"
                    ]
                ),
            ):
                checks[
                    "event_chain_valid"
                ] = False
                break

            previous_event_hash = (
                event[
                    "event_hash"
                ]
            )

    intake = (
        get_tower_protected_launch_handoff(
            row[
                "intake_id"
            ],
            path=database,
        )
    )

    intake_verification = (
        verify_tower_protected_launch_handoff(
            row[
                "intake_id"
            ],
            path=database,
        )
    )

    checks[
        "launch_intake_verified"
    ] = bool(
        intake_verification.get(
            "verified"
        )
    )

    checks[
        "launch_handoff_consumed"
    ] = bool(
        intake
        and intake.get(
            "consumed"
        )
    )

    checks[
        "launch_record_hash_matches"
    ] = bool(
        intake
        and hmac.compare_digest(
            str(
                row[
                    "launch_record_hash"
                ]
            ),
            str(
                intake.get(
                    "record_hash"
                )
                or ""
            ),
        )
    )

    return {
        "verified": all(
            checks.values()
        ),
        "checks": checks,
        "session_state_id": str(
            session_state_id
        ),
        "state": row[
            "state"
        ],
        "event_count": len(
            events
        ),
        "session_hash": row[
            "session_hash"
        ],
        "close_hash": row[
            "close_hash"
        ],
        "production_authority_granted": False,
    }


def protected_launch_session_status(
    *,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_session_database(
        database
    )

    expiration = (
        expire_stale_protected_launch_sessions(
            path=database,
            now=now,
        )
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
                        WHEN state = 'active'
                        THEN 1 ELSE 0
                    END
                ) AS active,
                SUM(
                    CASE
                        WHEN state = 'closed'
                        THEN 1 ELSE 0
                    END
                ) AS closed,
                SUM(
                    CASE
                        WHEN state = 'expired'
                        THEN 1 ELSE 0
                    END
                ) AS expired,
                SUM(
                    CASE
                        WHEN state = 'activation_failed'
                        THEN 1 ELSE 0
                    END
                ) AS activation_failed
            FROM ob_tower_launch_sessions
            """
        ).fetchone()

        event_total = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM ob_tower_launch_session_events
            """
        ).fetchone()

    return {
        "ok": True,
        "pack": PACK,
        "contract_version": CONTRACT_VERSION,
        "database_path": str(
            database
        ),
        "total": int(
            totals[
                "total"
            ]
            or 0
        ),
        "active": int(
            totals[
                "active"
            ]
            or 0
        ),
        "closed": int(
            totals[
                "closed"
            ]
            or 0
        ),
        "expired": int(
            totals[
                "expired"
            ]
            or 0
        ),
        "activation_failed": int(
            totals[
                "activation_failed"
            ]
            or 0
        ),
        "event_total": int(
            event_total[
                "total"
            ]
            or 0
        ),
        "expired_during_check": (
            expiration[
                "expired_count"
            ]
        ),
        "single_active_room_per_owner": True,
        "room_switch_allowed": False,
        "expiration_extension_allowed": False,
        "tower_authority_required": True,
        "ob_self_authorization_allowed": False,
        "http_session_mutation_enabled": (
            os.environ.get(
                "OB_TOWER_LAUNCH_SESSION_HTTP_ENABLED",
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
