
"""OB GP049 — Protected Room Exit, Lockback Receipt and Session Closeout.

The Observatory may close its local room context and local protected launch
session, but Tower remains the authority that performs and confirms lockback.

A local closeout receipt therefore starts with lockback_state='required'.
OB cannot change that state without a separately supplied Tower acknowledgment
reference.
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

from web.ob_tower_protected_launch_session_state import (
    close_protected_launch_session,
    get_protected_launch_session,
    verify_protected_launch_session,
)

from web.ob_protected_room_entry_enforcement import (
    get_protected_room_context,
    revoke_protected_room_context,
    verify_protected_room_context,
)


OB_GIANT_PACK_049_PROTECTED_ROOM_EXIT_CLOSEOUT_SERVICE = True

PACK = "GP049"
CONTRACT_VERSION = "ob.protected_room_exit_closeout.v1"

ZERO_HASH = "0" * 64

LOCKBACK_REQUIRED = "required"
LOCKBACK_ACKNOWLEDGED = "acknowledged"

VALID_LOCKBACK_STATES = {
    LOCKBACK_REQUIRED,
    LOCKBACK_ACKNOWLEDGED,
}

TERMINAL_CONTEXT_STATES = {
    "revoked",
    "expired",
}

TERMINAL_SESSION_STATES = {
    "closed",
    "expired",
    "activation_failed",
}


def _default_database_path() -> Path:
    configured = (
        os.environ.get(
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
        / "ob_protected_room_exit_gp049.sqlite3"
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


def init_exit_database(
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
            ob_protected_room_exit_closeouts (
                closeout_id TEXT PRIMARY KEY,
                context_id TEXT NOT NULL UNIQUE,
                session_state_id TEXT NOT NULL,
                intake_id TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                tower_session_id TEXT NOT NULL,
                room_id TEXT NOT NULL,
                canonical_route TEXT NOT NULL,
                mode TEXT NOT NULL,
                exit_reason TEXT NOT NULL,
                context_state_before TEXT NOT NULL,
                context_state_after TEXT NOT NULL,
                session_state_before TEXT NOT NULL,
                session_state_after TEXT NOT NULL,
                context_hash TEXT NOT NULL,
                context_revoke_hash TEXT,
                session_hash TEXT NOT NULL,
                session_close_hash TEXT,
                lockback_state TEXT NOT NULL,
                lockback_ack_ref TEXT,
                lockback_ack_at TEXT,
                previous_closeout_hash TEXT NOT NULL,
                closeout_hash TEXT NOT NULL UNIQUE,
                lockback_ack_hash TEXT,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_exit_closeout_owner
            ON ob_protected_room_exit_closeouts(
                owner_id,
                created_at
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_exit_closeout_session
            ON ob_protected_room_exit_closeouts(
                session_state_id,
                created_at
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_exit_closeout_lockback
            ON ob_protected_room_exit_closeouts(
                lockback_state,
                created_at
            );

            CREATE TABLE IF NOT EXISTS
            ob_protected_room_exit_events (
                event_id TEXT PRIMARY KEY,
                closeout_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                previous_event_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                FOREIGN KEY(
                    closeout_id
                )
                REFERENCES
                ob_protected_room_exit_closeouts(
                    closeout_id
                )
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_exit_event_closeout
            ON ob_protected_room_exit_events(
                closeout_id,
                created_at
            );
            """
        )

    return str(
        database
    )


def _latest_closeout_hash(
    connection: sqlite3.Connection,
) -> str:
    row = connection.execute(
        """
        SELECT closeout_hash
        FROM ob_protected_room_exit_closeouts
        ORDER BY rowid DESC
        LIMIT 1
        """
    ).fetchone()

    if row is None:
        return ZERO_HASH

    return str(
        row[
            "closeout_hash"
        ]
    )


def _latest_event_hash(
    connection: sqlite3.Connection,
    closeout_id: str,
) -> str:
    row = connection.execute(
        """
        SELECT event_hash
        FROM ob_protected_room_exit_events
        WHERE closeout_id = ?
        ORDER BY rowid DESC
        LIMIT 1
        """,
        (
            str(
                closeout_id
            ),
        ),
    ).fetchone()

    if row is None:
        return ZERO_HASH

    return str(
        row[
            "event_hash"
        ]
    )


def _closeout_hash_material(
    record: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "closeout_id": record[
            "closeout_id"
        ],
        "context_id": record[
            "context_id"
        ],
        "session_state_id": record[
            "session_state_id"
        ],
        "intake_id": record[
            "intake_id"
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
        "exit_reason": record[
            "exit_reason"
        ],
        "context_state_before": record[
            "context_state_before"
        ],
        "context_state_after": record[
            "context_state_after"
        ],
        "session_state_before": record[
            "session_state_before"
        ],
        "session_state_after": record[
            "session_state_after"
        ],
        "context_hash": record[
            "context_hash"
        ],
        "context_revoke_hash": record[
            "context_revoke_hash"
        ],
        "session_hash": record[
            "session_hash"
        ],
        "session_close_hash": record[
            "session_close_hash"
        ],
        "initial_lockback_state": (
            LOCKBACK_REQUIRED
        ),
        "previous_closeout_hash": record[
            "previous_closeout_hash"
        ],
        "created_at": record[
            "created_at"
        ],
        "room_entry_allowed": False,
        "tower_lockback_required": True,
        "tower_lockback_confirmed": False,
        "ob_self_lockback_allowed": False,
        "production_authority_granted": False,
    }


def _ack_hash_material(
    row: sqlite3.Row,
    *,
    lockback_ack_ref: str,
    lockback_ack_at: str,
) -> Dict[str, Any]:
    return {
        "closeout_id": row[
            "closeout_id"
        ],
        "closeout_hash": row[
            "closeout_hash"
        ],
        "lockback_state": (
            LOCKBACK_ACKNOWLEDGED
        ),
        "lockback_ack_ref": (
            lockback_ack_ref
        ),
        "lockback_ack_at": (
            lockback_ack_at
        ),
        "tower_acknowledgment_required": True,
        "ob_self_lockback_allowed": False,
        "production_authority_granted": False,
    }


def _append_event(
    connection: sqlite3.Connection,
    *,
    closeout_id: str,
    event_type: str,
    payload: Dict[str, Any],
    created_at: str,
) -> Dict[str, Any]:
    previous_event_hash = (
        _latest_event_hash(
            connection,
            closeout_id,
        )
    )

    event_id = (
        "ob_exit_event_"
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
        "closeout_id": (
            closeout_id
        ),
        "event_type": (
            event_type
        ),
        "payload": (
            payload
        ),
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
        ob_protected_room_exit_events (
            event_id,
            closeout_id,
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
            closeout_id,
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


def _public_closeout(
    row: sqlite3.Row,
) -> Dict[str, Any]:
    return {
        "closeout_id": row[
            "closeout_id"
        ],
        "context_id": row[
            "context_id"
        ],
        "session_state_id": row[
            "session_state_id"
        ],
        "intake_id": row[
            "intake_id"
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
        "exit_reason": row[
            "exit_reason"
        ],
        "context_state_before": row[
            "context_state_before"
        ],
        "context_state_after": row[
            "context_state_after"
        ],
        "session_state_before": row[
            "session_state_before"
        ],
        "session_state_after": row[
            "session_state_after"
        ],
        "context_hash": row[
            "context_hash"
        ],
        "context_revoke_hash": row[
            "context_revoke_hash"
        ],
        "session_hash": row[
            "session_hash"
        ],
        "session_close_hash": row[
            "session_close_hash"
        ],
        "lockback_state": row[
            "lockback_state"
        ],
        "lockback_required": True,
        "lockback_acknowledged": (
            row[
                "lockback_state"
            ]
            == LOCKBACK_ACKNOWLEDGED
        ),
        "lockback_ack_ref": row[
            "lockback_ack_ref"
        ],
        "lockback_ack_at": row[
            "lockback_ack_at"
        ],
        "previous_closeout_hash": row[
            "previous_closeout_hash"
        ],
        "closeout_hash": row[
            "closeout_hash"
        ],
        "lockback_ack_hash": row[
            "lockback_ack_hash"
        ],
        "created_at": row[
            "created_at"
        ],
        "room_entry_allowed": False,
        "session_active": False,
        "context_active": False,
        "tower_lockback_authority": True,
        "ob_self_lockback_allowed": False,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
    }


def get_protected_room_exit_closeout(
    closeout_id: str,
    *,
    path: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    init_exit_database(
        path
    )

    with _connect(
        path
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_exit_closeouts
            WHERE closeout_id = ?
            """,
            (
                str(
                    closeout_id
                ),
            ),
        ).fetchone()

    if row is None:
        return None

    return _public_closeout(
        row
    )


def _get_closeout_by_context(
    context_id: str,
    *,
    path: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    init_exit_database(
        path
    )

    with _connect(
        path
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_exit_closeouts
            WHERE context_id = ?
            """,
            (
                str(
                    context_id
                ),
            ),
        ).fetchone()

    if row is None:
        return None

    return _public_closeout(
        row
    )


def list_protected_room_exit_closeouts(
    *,
    owner_id: Optional[str] = None,
    lockback_state: Optional[str] = None,
    limit: int = 100,
    path: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    init_exit_database(
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
        FROM ob_protected_room_exit_closeouts
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

    if lockback_state:
        clauses.append(
            "lockback_state = ?"
        )

        parameters.append(
            str(
                lockback_state
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
        _public_closeout(
            row
        )
        for row in rows
    ]


def list_protected_room_exit_events(
    closeout_id: str,
    *,
    path: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    init_exit_database(
        path
    )

    with _connect(
        path
    ) as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_exit_events
            WHERE closeout_id = ?
            ORDER BY rowid ASC
            """,
            (
                str(
                    closeout_id
                ),
            ),
        ).fetchall()

    output = []

    for row in rows:
        output.append(
            {
                "event_id": row[
                    "event_id"
                ],
                "closeout_id": row[
                    "closeout_id"
                ],
                "event_type": row[
                    "event_type"
                ],
                "payload": json.loads(
                    row[
                        "payload_json"
                    ]
                ),
                "previous_event_hash": row[
                    "previous_event_hash"
                ],
                "event_hash": row[
                    "event_hash"
                ],
                "created_at": row[
                    "created_at"
                ],
            }
        )

    return output


def close_protected_room_exit(
    context_id: str,
    *,
    owner_id: str,
    tower_session_id: str,
    exit_reason: str = (
        "owner_protected_room_exit"
    ),
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_exit_database(
        database
    )

    current_time = _now(
        now
    )

    existing = (
        _get_closeout_by_context(
            context_id,
            path=database,
        )
    )

    if existing is not None:
        exact_identity = (
            str(
                owner_id
            )
            == str(
                existing[
                    "owner_id"
                ]
            )
            and str(
                tower_session_id
            )
            == str(
                existing[
                    "tower_session_id"
                ]
            )
        )

        if exact_identity:
            return {
                "ok": True,
                "created": False,
                "idempotent": True,
                "reason_code": (
                    "protected_room_exit_already_closed"
                ),
                "closeout": (
                    existing
                ),
                "tower_lockback_required": True,
                "production_authority_granted": False,
            }

        return {
            "ok": False,
            "created": False,
            "idempotent": False,
            "reason_code": (
                "existing_closeout_identity_conflict"
            ),
            "production_authority_granted": False,
        }

    context = (
        get_protected_room_context(
            context_id,
            path=database,
        )
    )

    if context is None:
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "protected_room_context_not_found"
            ),
            "production_authority_granted": False,
        }

    if (
        str(
            owner_id
        )
        != str(
            context[
                "owner_id"
            ]
        )
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "owner_identity_mismatch"
            ),
            "production_authority_granted": False,
        }

    if (
        str(
            tower_session_id
        )
        != str(
            context[
                "tower_session_id"
            ]
        )
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "tower_session_identity_mismatch"
            ),
            "production_authority_granted": False,
        }

    context_verification = (
        verify_protected_room_context(
            context_id,
            path=database,
        )
    )

    if not context_verification.get(
        "verified"
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "protected_room_context_integrity_failed"
            ),
            "verification": (
                context_verification
            ),
            "production_authority_granted": False,
        }

    session = (
        get_protected_launch_session(
            context[
                "session_state_id"
            ],
            path=database,
        )
    )

    if session is None:
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "protected_launch_session_not_found"
            ),
            "production_authority_granted": False,
        }

    if (
        str(
            session[
                "owner_id"
            ]
        )
        != str(
            context[
                "owner_id"
            ]
        )
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "session_owner_binding_mismatch"
            ),
            "production_authority_granted": False,
        }

    if (
        str(
            session[
                "tower_session_id"
            ]
        )
        != str(
            context[
                "tower_session_id"
            ]
        )
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "session_identity_binding_mismatch"
            ),
            "production_authority_granted": False,
        }

    if (
        str(
            session[
                "room_id"
            ]
        )
        != str(
            context[
                "room_id"
            ]
        )
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "session_room_binding_mismatch"
            ),
            "production_authority_granted": False,
        }

    session_verification = (
        verify_protected_launch_session(
            session[
                "session_state_id"
            ],
            path=database,
        )
    )

    if not session_verification.get(
        "verified"
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "protected_launch_session_integrity_failed"
            ),
            "verification": (
                session_verification
            ),
            "production_authority_granted": False,
        }

    context_state_before = str(
        context[
            "state"
        ]
    )

    session_state_before = str(
        session[
            "state"
        ]
    )

    normalized_exit_reason = str(
        exit_reason
        or "owner_protected_room_exit"
    ).strip()

    context_revoke_result = None

    if (
        context_state_before
        not in TERMINAL_CONTEXT_STATES
    ):
        context_revoke_result = (
            revoke_protected_room_context(
                context_id,
                reason=(
                    "protected_room_exit:"
                    + normalized_exit_reason
                ),
                path=database,
                now=current_time,
            )
        )

        if not context_revoke_result.get(
            "ok"
        ):
            return {
                "ok": False,
                "created": False,
                "reason_code": (
                    "protected_room_context_revoke_failed"
                ),
                "revoke_result": (
                    context_revoke_result
                ),
                "production_authority_granted": False,
            }

    session_close_result = None

    if (
        session_state_before
        not in TERMINAL_SESSION_STATES
    ):
        session_close_result = (
            close_protected_launch_session(
                session[
                    "session_state_id"
                ],
                owner_id=(
                    owner_id
                ),
                reason=(
                    "protected_room_exit:"
                    + normalized_exit_reason
                ),
                path=database,
                now=current_time,
            )
        )

        if not session_close_result.get(
            "ok"
        ):
            return {
                "ok": False,
                "created": False,
                "reason_code": (
                    "protected_launch_session_close_failed"
                ),
                "close_result": (
                    session_close_result
                ),
                "tower_lockback_required": True,
                "production_authority_granted": False,
            }

    final_context = (
        get_protected_room_context(
            context_id,
            path=database,
        )
    )

    final_session = (
        get_protected_launch_session(
            session[
                "session_state_id"
            ],
            path=database,
        )
    )

    if (
        final_context is None
        or final_context[
            "state"
        ]
        not in TERMINAL_CONTEXT_STATES
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "protected_room_context_not_closed"
            ),
            "tower_lockback_required": True,
            "production_authority_granted": False,
        }

    if (
        final_session is None
        or final_session[
            "state"
        ]
        not in TERMINAL_SESSION_STATES
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "protected_launch_session_not_closed"
            ),
            "tower_lockback_required": True,
            "production_authority_granted": False,
        }

    final_context_verification = (
        verify_protected_room_context(
            context_id,
            path=database,
        )
    )

    final_session_verification = (
        verify_protected_launch_session(
            final_session[
                "session_state_id"
            ],
            path=database,
        )
    )

    if not final_context_verification.get(
        "verified"
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "closed_context_integrity_failed"
            ),
            "production_authority_granted": False,
        }

    if not final_session_verification.get(
        "verified"
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "closed_session_integrity_failed"
            ),
            "production_authority_granted": False,
        }

    closeout_id = (
        "ob_room_exit_"
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
        current_time
    )

    with _connect(
        database
    ) as connection:
        previous_closeout_hash = (
            _latest_closeout_hash(
                connection
            )
        )

        record = {
            "closeout_id": closeout_id,
            "context_id": context_id,
            "session_state_id": (
                final_session[
                    "session_state_id"
                ]
            ),
            "intake_id": (
                final_session[
                    "intake_id"
                ]
            ),
            "owner_id": owner_id,
            "tower_session_id": (
                tower_session_id
            ),
            "room_id": (
                final_context[
                    "room_id"
                ]
            ),
            "canonical_route": (
                final_context[
                    "canonical_route"
                ]
            ),
            "mode": (
                final_context[
                    "mode"
                ]
            ),
            "exit_reason": (
                normalized_exit_reason
            ),
            "context_state_before": (
                context_state_before
            ),
            "context_state_after": (
                final_context[
                    "state"
                ]
            ),
            "session_state_before": (
                session_state_before
            ),
            "session_state_after": (
                final_session[
                    "state"
                ]
            ),
            "context_hash": (
                final_context[
                    "context_hash"
                ]
            ),
            "context_revoke_hash": (
                final_context[
                    "revoke_hash"
                ]
            ),
            "session_hash": (
                final_session[
                    "session_hash"
                ]
            ),
            "session_close_hash": (
                final_session[
                    "close_hash"
                ]
            ),
            "previous_closeout_hash": (
                previous_closeout_hash
            ),
            "created_at": (
                created_at
            ),
        }

        closeout_hash = _sha256_text(
            _canonical_json(
                _closeout_hash_material(
                    record
                )
            )
        )

        connection.execute(
            """
            INSERT INTO
            ob_protected_room_exit_closeouts (
                closeout_id,
                context_id,
                session_state_id,
                intake_id,
                owner_id,
                tower_session_id,
                room_id,
                canonical_route,
                mode,
                exit_reason,
                context_state_before,
                context_state_after,
                session_state_before,
                session_state_after,
                context_hash,
                context_revoke_hash,
                session_hash,
                session_close_hash,
                lockback_state,
                lockback_ack_ref,
                lockback_ack_at,
                previous_closeout_hash,
                closeout_hash,
                lockback_ack_hash,
                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, NULL, NULL, ?, ?, NULL, ?
            )
            """,
            (
                closeout_id,
                context_id,
                final_session[
                    "session_state_id"
                ],
                final_session[
                    "intake_id"
                ],
                owner_id,
                tower_session_id,
                final_context[
                    "room_id"
                ],
                final_context[
                    "canonical_route"
                ],
                final_context[
                    "mode"
                ],
                normalized_exit_reason,
                context_state_before,
                final_context[
                    "state"
                ],
                session_state_before,
                final_session[
                    "state"
                ],
                final_context[
                    "context_hash"
                ],
                final_context[
                    "revoke_hash"
                ],
                final_session[
                    "session_hash"
                ],
                final_session[
                    "close_hash"
                ],
                LOCKBACK_REQUIRED,
                previous_closeout_hash,
                closeout_hash,
                created_at,
            ),
        )

        _append_event(
            connection,
            closeout_id=(
                closeout_id
            ),
            event_type=(
                "protected_room_exit_closed"
            ),
            payload={
                "context_id": (
                    context_id
                ),
                "session_state_id": (
                    final_session[
                        "session_state_id"
                    ]
                ),
                "room_id": (
                    final_context[
                        "room_id"
                    ]
                ),
                "context_state_after": (
                    final_context[
                        "state"
                    ]
                ),
                "session_state_after": (
                    final_session[
                        "state"
                    ]
                ),
                "lockback_state": (
                    LOCKBACK_REQUIRED
                ),
                "tower_lockback_required": True,
                "tower_lockback_confirmed": False,
                "ob_self_lockback_allowed": False,
                "room_entry_allowed": False,
            },
            created_at=(
                created_at
            ),
        )

        connection.commit()

    closeout = (
        get_protected_room_exit_closeout(
            closeout_id,
            path=database,
        )
    )

    return {
        "ok": True,
        "created": True,
        "idempotent": False,
        "reason_code": (
            "protected_room_exit_closed"
        ),
        "closeout": closeout,
        "context_revoked": True,
        "session_closed": True,
        "room_entry_allowed": False,
        "tower_lockback_required": True,
        "tower_lockback_acknowledged": False,
        "production_authority_granted": False,
    }


def acknowledge_tower_lockback(
    closeout_id: str,
    *,
    tower_lockback_ack_ref: str,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_exit_database(
        database
    )

    current_time = _now(
        now
    )

    ack_ref = str(
        tower_lockback_ack_ref
        or ""
    ).strip()

    if not re.fullmatch(
        r"[A-Za-z0-9_.:\-]{16,200}",
        ack_ref,
    ):
        return {
            "ok": False,
            "acknowledged": False,
            "reason_code": (
                "valid_tower_lockback_ack_ref_required"
            ),
            "production_authority_granted": False,
        }

    with _connect(
        database
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_exit_closeouts
            WHERE closeout_id = ?
            """,
            (
                str(
                    closeout_id
                ),
            ),
        ).fetchone()

        if row is None:
            return {
                "ok": False,
                "acknowledged": False,
                "reason_code": (
                    "protected_room_exit_closeout_not_found"
                ),
                "production_authority_granted": False,
            }

        if (
            row[
                "lockback_state"
            ]
            == LOCKBACK_ACKNOWLEDGED
        ):
            if (
                str(
                    row[
                        "lockback_ack_ref"
                    ]
                )
                == ack_ref
            ):
                return {
                    "ok": True,
                    "acknowledged": True,
                    "idempotent": True,
                    "reason_code": (
                        "tower_lockback_already_acknowledged"
                    ),
                    "closeout": (
                        _public_closeout(
                            row
                        )
                    ),
                    "production_authority_granted": False,
                }

            return {
                "ok": False,
                "acknowledged": False,
                "idempotent": False,
                "reason_code": (
                    "tower_lockback_ack_conflict"
                ),
                "production_authority_granted": False,
            }

    verification = (
        verify_protected_room_exit_closeout(
            closeout_id,
            path=database,
        )
    )

    if not verification.get(
        "verified"
    ):
        return {
            "ok": False,
            "acknowledged": False,
            "reason_code": (
                "protected_room_exit_closeout_integrity_failed"
            ),
            "verification": (
                verification
            ),
            "production_authority_granted": False,
        }

    acknowledged_at = _iso(
        current_time
    )

    with _connect(
        database
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_exit_closeouts
            WHERE closeout_id = ?
            """,
            (
                str(
                    closeout_id
                ),
            ),
        ).fetchone()

        ack_hash = _sha256_text(
            _canonical_json(
                _ack_hash_material(
                    row,
                    lockback_ack_ref=(
                        ack_ref
                    ),
                    lockback_ack_at=(
                        acknowledged_at
                    ),
                )
            )
        )

        connection.execute(
            """
            UPDATE ob_protected_room_exit_closeouts
            SET
                lockback_state = ?,
                lockback_ack_ref = ?,
                lockback_ack_at = ?,
                lockback_ack_hash = ?
            WHERE closeout_id = ?
              AND lockback_state = ?
            """,
            (
                LOCKBACK_ACKNOWLEDGED,
                ack_ref,
                acknowledged_at,
                ack_hash,
                str(
                    closeout_id
                ),
                LOCKBACK_REQUIRED,
            ),
        )

        _append_event(
            connection,
            closeout_id=str(
                closeout_id
            ),
            event_type=(
                "tower_lockback_acknowledged"
            ),
            payload={
                "tower_lockback_ack_ref": (
                    ack_ref
                ),
                "tower_lockback_ack_at": (
                    acknowledged_at
                ),
                "tower_lockback_confirmed": True,
                "ob_self_lockback_allowed": False,
                "room_entry_allowed": False,
            },
            created_at=(
                acknowledged_at
            ),
        )

        connection.commit()

    return {
        "ok": True,
        "acknowledged": True,
        "idempotent": False,
        "reason_code": (
            "tower_lockback_acknowledged"
        ),
        "closeout": (
            get_protected_room_exit_closeout(
                closeout_id,
                path=database,
            )
        ),
        "production_authority_granted": False,
    }


def verify_protected_room_exit_closeout(
    closeout_id: str,
    *,
    path: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_exit_database(
        database
    )

    with _connect(
        database
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_exit_closeouts
            WHERE closeout_id = ?
            """,
            (
                str(
                    closeout_id
                ),
            ),
        ).fetchone()

        if row is None:
            return {
                "verified": False,
                "reason_codes": [
                    "protected_room_exit_closeout_not_found"
                ],
            }

        record = {
            "closeout_id": row[
                "closeout_id"
            ],
            "context_id": row[
                "context_id"
            ],
            "session_state_id": row[
                "session_state_id"
            ],
            "intake_id": row[
                "intake_id"
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
            "exit_reason": row[
                "exit_reason"
            ],
            "context_state_before": row[
                "context_state_before"
            ],
            "context_state_after": row[
                "context_state_after"
            ],
            "session_state_before": row[
                "session_state_before"
            ],
            "session_state_after": row[
                "session_state_after"
            ],
            "context_hash": row[
                "context_hash"
            ],
            "context_revoke_hash": row[
                "context_revoke_hash"
            ],
            "session_hash": row[
                "session_hash"
            ],
            "session_close_hash": row[
                "session_close_hash"
            ],
            "previous_closeout_hash": row[
                "previous_closeout_hash"
            ],
            "created_at": row[
                "created_at"
            ],
        }

        computed_closeout_hash = (
            _sha256_text(
                _canonical_json(
                    _closeout_hash_material(
                        record
                    )
                )
            )
        )

        checks = {
            "closeout_hash_matches": (
                hmac.compare_digest(
                    computed_closeout_hash,
                    str(
                        row[
                            "closeout_hash"
                        ]
                    ),
                )
            ),
            "previous_closeout_hash_valid": True,
            "context_exists": False,
            "context_hash_matches": False,
            "context_inactive": False,
            "context_verified": False,
            "session_exists": False,
            "session_hash_matches": False,
            "session_inactive": False,
            "session_verified": False,
            "lockback_state_valid": (
                row[
                    "lockback_state"
                ]
                in VALID_LOCKBACK_STATES
            ),
            "lockback_ack_hash_valid": True,
            "event_chain_valid": True,
        }

        if (
            row[
                "previous_closeout_hash"
            ]
            != ZERO_HASH
        ):
            previous = connection.execute(
                """
                SELECT 1
                FROM ob_protected_room_exit_closeouts
                WHERE closeout_hash = ?
                LIMIT 1
                """,
                (
                    row[
                        "previous_closeout_hash"
                    ],
                ),
            ).fetchone()

            checks[
                "previous_closeout_hash_valid"
            ] = previous is not None

        if (
            row[
                "lockback_state"
            ]
            == LOCKBACK_ACKNOWLEDGED
        ):
            expected_ack_hash = (
                _sha256_text(
                    _canonical_json(
                        _ack_hash_material(
                            row,
                            lockback_ack_ref=str(
                                row[
                                    "lockback_ack_ref"
                                ]
                                or ""
                            ),
                            lockback_ack_at=str(
                                row[
                                    "lockback_ack_at"
                                ]
                                or ""
                            ),
                        )
                    )
                )
            )

            checks[
                "lockback_ack_hash_valid"
            ] = hmac.compare_digest(
                str(
                    row[
                        "lockback_ack_hash"
                    ]
                    or ""
                ),
                expected_ack_hash,
            )

        else:
            checks[
                "lockback_ack_hash_valid"
            ] = (
                row[
                    "lockback_ack_ref"
                ]
                is None
                and row[
                    "lockback_ack_at"
                ]
                is None
                and row[
                    "lockback_ack_hash"
                ]
                is None
            )

        events = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_exit_events
            WHERE closeout_id = ?
            ORDER BY rowid ASC
            """,
            (
                str(
                    closeout_id
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
                "closeout_id": event[
                    "closeout_id"
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

    context = (
        get_protected_room_context(
            row[
                "context_id"
            ],
            path=database,
        )
    )

    session = (
        get_protected_launch_session(
            row[
                "session_state_id"
            ],
            path=database,
        )
    )

    checks[
        "context_exists"
    ] = context is not None

    checks[
        "context_hash_matches"
    ] = bool(
        context
        and hmac.compare_digest(
            str(
                row[
                    "context_hash"
                ]
            ),
            str(
                context[
                    "context_hash"
                ]
            ),
        )
    )

    checks[
        "context_inactive"
    ] = bool(
        context
        and context[
            "state"
        ]
        in TERMINAL_CONTEXT_STATES
    )

    context_verification = (
        verify_protected_room_context(
            row[
                "context_id"
            ],
            path=database,
        )
    )

    checks[
        "context_verified"
    ] = bool(
        context_verification.get(
            "verified"
        )
    )

    checks[
        "session_exists"
    ] = session is not None

    checks[
        "session_hash_matches"
    ] = bool(
        session
        and hmac.compare_digest(
            str(
                row[
                    "session_hash"
                ]
            ),
            str(
                session[
                    "session_hash"
                ]
            ),
        )
    )

    checks[
        "session_inactive"
    ] = bool(
        session
        and session[
            "state"
        ]
        in TERMINAL_SESSION_STATES
    )

    session_verification = (
        verify_protected_launch_session(
            row[
                "session_state_id"
            ],
            path=database,
        )
    )

    checks[
        "session_verified"
    ] = bool(
        session_verification.get(
            "verified"
        )
    )

    return {
        "verified": all(
            checks.values()
        ),
        "checks": checks,
        "closeout_id": str(
            closeout_id
        ),
        "lockback_state": row[
            "lockback_state"
        ],
        "lockback_required": True,
        "lockback_acknowledged": (
            row[
                "lockback_state"
            ]
            == LOCKBACK_ACKNOWLEDGED
        ),
        "event_count": len(
            events
        ),
        "closeout_hash": row[
            "closeout_hash"
        ],
        "lockback_ack_hash": row[
            "lockback_ack_hash"
        ],
        "room_entry_allowed": False,
        "production_authority_granted": False,
    }


def protected_room_exit_status(
    *,
    path: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_exit_database(
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
                        WHEN lockback_state = 'required'
                        THEN 1 ELSE 0
                    END
                ) AS lockback_required,
                SUM(
                    CASE
                        WHEN lockback_state = 'acknowledged'
                        THEN 1 ELSE 0
                    END
                ) AS lockback_acknowledged
            FROM ob_protected_room_exit_closeouts
            """
        ).fetchone()

        event_total = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM ob_protected_room_exit_events
            """
        ).fetchone()

    return {
        "ok": True,
        "pack": PACK,
        "contract_version": CONTRACT_VERSION,
        "database_path": str(
            database
        ),
        "closeout_total": int(
            totals[
                "total"
            ]
            or 0
        ),
        "lockback_required": int(
            totals[
                "lockback_required"
            ]
            or 0
        ),
        "lockback_acknowledged": int(
            totals[
                "lockback_acknowledged"
            ]
            or 0
        ),
        "event_total": int(
            event_total[
                "total"
            ]
            or 0
        ),
        "context_revocation_required": True,
        "session_close_required": True,
        "tower_lockback_authority": True,
        "tower_ack_reference_required": True,
        "ob_self_lockback_allowed": False,
        "room_entry_allowed_after_closeout": False,
        "http_closeout_mutation_enabled": (
            os.environ.get(
                "OB_PROTECTED_ROOM_EXIT_HTTP_ENABLED",
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
