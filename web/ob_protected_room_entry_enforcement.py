
"""OB GP048 — Protected Room Entry Enforcement.

Tower remains the authority for identity, clearance, step-up, route approval,
launch issuance, revocation and lockback.

GP048 adds a second default-deny boundary inside OB. A request must already
have an active GP047 protected launch session and a matching short-lived local
room context. This service never manufactures Tower authority.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
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

from web.ob_tower_protected_launch_handoff_consumer import (
    ROOM_REGISTRY,
)

from web.ob_tower_protected_launch_session_state import (
    get_protected_launch_session,
    resolve_active_room_binding,
    verify_protected_launch_session,
)


OB_GIANT_PACK_048_PROTECTED_ROOM_ENTRY_ENFORCEMENT_SERVICE = True

PACK = "GP048"
CONTRACT_VERSION = "ob.protected_room_entry_context.v1"

ZERO_HASH = "0" * 64

DEFAULT_CONTEXT_TTL_SECONDS = 120
MAX_CONTEXT_TTL_SECONDS = 300

ACTIVE_CONTEXT_STATES = {
    "active",
}

TERMINAL_CONTEXT_STATES = {
    "revoked",
    "expired",
}

PROTECTED_ROOM_PATHS = {
    "dashboard": {
        "canonical_route": "/dashboard",
        "accepted_paths": {
            "/dashboard",
            "/ob/dashboard",
        },
    },
    "market_map": {
        "canonical_route": "/market-map",
        "accepted_paths": {
            "/market-map",
            "/ob/market-map",
        },
    },
    "trade_center": {
        "canonical_route": "/trade-center",
        "accepted_paths": {
            "/trade-center",
            "/ob/trade-center",
        },
    },
    "review_center": {
        "canonical_route": "/review-center",
        "accepted_paths": {
            "/review-center",
            "/ob/review-center",
        },
    },
    "owner_console": {
        "canonical_route": "/owner-console",
        "accepted_paths": {
            "/owner-console",
            "/ob/owner-console",
        },
    },
}


def _default_database_path() -> Path:
    configured = (
        os.environ.get(
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
        / "ob_protected_room_entry_gp048.sqlite3"
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


def normalize_request_path(
    value: Any,
) -> str:
    rendered = str(
        value or ""
    ).strip()

    if not rendered:
        return ""

    rendered = rendered.split(
        "?",
        1,
    )[0]

    if not rendered.startswith(
        "/"
    ):
        rendered = (
            "/"
            + rendered
        )

    if (
        len(rendered) > 1
        and rendered.endswith("/")
    ):
        rendered = rendered.rstrip(
            "/"
        )

    return rendered


def match_protected_room_path(
    requested_path: Any,
) -> Optional[Dict[str, Any]]:
    path = normalize_request_path(
        requested_path
    )

    for room_id, contract in (
        PROTECTED_ROOM_PATHS.items()
    ):
        if path in contract[
            "accepted_paths"
        ]:
            return {
                "room_id": room_id,
                "canonical_route": contract[
                    "canonical_route"
                ],
                "requested_path": path,
                "route_parameters": {},
            }

    symbol_match = re.fullmatch(
        r"/(?:ob/)?symbol/"
        r"([A-Za-z][A-Za-z0-9.\-]{0,14})",
        path,
    )

    if symbol_match:
        symbol = (
            symbol_match.group(1)
            .upper()
        )

        return {
            "room_id": "symbol_page",
            "canonical_route": (
                "/symbol/<symbol>"
            ),
            "requested_path": path,
            "route_parameters": {
                "symbol": symbol,
            },
        }

    return None


def is_protected_room_path(
    requested_path: Any,
) -> bool:
    return (
        match_protected_room_path(
            requested_path
        )
        is not None
    )


def init_entry_database(
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
            ob_protected_room_contexts (
                context_id TEXT PRIMARY KEY,
                session_state_id TEXT NOT NULL,
                intake_id TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                tower_session_id TEXT NOT NULL,
                room_id TEXT NOT NULL,
                canonical_route TEXT NOT NULL,
                requested_path TEXT NOT NULL,
                route_parameters_json TEXT NOT NULL,
                mode TEXT NOT NULL,
                state TEXT NOT NULL,
                issued_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked_at TEXT,
                revoke_reason TEXT,
                session_hash TEXT NOT NULL,
                previous_context_hash TEXT NOT NULL,
                context_hash TEXT NOT NULL UNIQUE,
                revoke_hash TEXT,
                created_at TEXT NOT NULL
            );

            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_ob_one_active_context_per_session
            ON ob_protected_room_contexts(
                session_state_id
            )
            WHERE state = 'active';

            CREATE INDEX IF NOT EXISTS
            idx_ob_room_context_owner
            ON ob_protected_room_contexts(
                owner_id,
                state
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_room_context_room
            ON ob_protected_room_contexts(
                room_id,
                state
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_room_context_created
            ON ob_protected_room_contexts(
                created_at
            );

            CREATE TABLE IF NOT EXISTS
            ob_protected_room_entry_attempts (
                attempt_id TEXT PRIMARY KEY,
                context_id TEXT,
                session_state_id TEXT,
                owner_id TEXT,
                tower_session_id TEXT,
                room_id TEXT,
                requested_path TEXT NOT NULL,
                decision TEXT NOT NULL,
                reason_codes_json TEXT NOT NULL,
                previous_attempt_hash TEXT NOT NULL,
                attempt_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_room_entry_attempt_context
            ON ob_protected_room_entry_attempts(
                context_id,
                created_at
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_room_entry_attempt_decision
            ON ob_protected_room_entry_attempts(
                decision,
                created_at
            );
            """
        )

    return str(
        database
    )


def _latest_context_hash(
    connection: sqlite3.Connection,
) -> str:
    row = connection.execute(
        """
        SELECT context_hash
        FROM ob_protected_room_contexts
        ORDER BY rowid DESC
        LIMIT 1
        """
    ).fetchone()

    if row is None:
        return ZERO_HASH

    return str(
        row[
            "context_hash"
        ]
    )


def _latest_attempt_hash(
    connection: sqlite3.Connection,
) -> str:
    row = connection.execute(
        """
        SELECT attempt_hash
        FROM ob_protected_room_entry_attempts
        ORDER BY rowid DESC
        LIMIT 1
        """
    ).fetchone()

    if row is None:
        return ZERO_HASH

    return str(
        row[
            "attempt_hash"
        ]
    )


def _context_hash_material(
    record: Dict[str, Any],
) -> Dict[str, Any]:
    return {
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
        "requested_path": record[
            "requested_path"
        ],
        "route_parameters": record[
            "route_parameters"
        ],
        "mode": record[
            "mode"
        ],
        "issued_at": record[
            "issued_at"
        ],
        "expires_at": record[
            "expires_at"
        ],
        "session_hash": record[
            "session_hash"
        ],
        "previous_context_hash": record[
            "previous_context_hash"
        ],
        "created_at": record[
            "created_at"
        ],
        "tower_authority_required": True,
        "ob_self_authorization_allowed": False,
        "room_switch_allowed": False,
        "expiration_extension_allowed": False,
        "production_authority_granted": False,
    }


def _revoke_hash_material(
    row: sqlite3.Row,
    *,
    state: str,
    revoked_at: str,
    revoke_reason: str,
) -> Dict[str, Any]:
    return {
        "context_id": row[
            "context_id"
        ],
        "context_hash": row[
            "context_hash"
        ],
        "state": state,
        "revoked_at": revoked_at,
        "revoke_reason": revoke_reason,
        "room_entry_allowed": False,
        "tower_lockback_required": True,
        "production_authority_granted": False,
    }


def _public_context(
    row: sqlite3.Row,
) -> Dict[str, Any]:
    return {
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
        "requested_path": row[
            "requested_path"
        ],
        "route_parameters": json.loads(
            row[
                "route_parameters_json"
            ]
        ),
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
        "issued_at": row[
            "issued_at"
        ],
        "expires_at": row[
            "expires_at"
        ],
        "revoked_at": row[
            "revoked_at"
        ],
        "revoke_reason": row[
            "revoke_reason"
        ],
        "session_hash": row[
            "session_hash"
        ],
        "previous_context_hash": row[
            "previous_context_hash"
        ],
        "context_hash": row[
            "context_hash"
        ],
        "revoke_hash": row[
            "revoke_hash"
        ],
        "created_at": row[
            "created_at"
        ],
        "tower_authority_required": True,
        "ob_self_authorization_allowed": False,
        "room_switch_allowed": False,
        "expiration_extension_allowed": False,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
    }


def get_protected_room_context(
    context_id: str,
    *,
    path: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    init_entry_database(
        path
    )

    with _connect(
        path
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_contexts
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

    return _public_context(
        row
    )


def list_protected_room_contexts(
    *,
    owner_id: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 100,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    expire_stale_protected_room_contexts(
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
        FROM ob_protected_room_contexts
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

    if state:
        clauses.append(
            "state = ?"
        )

        parameters.append(
            str(
                state
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
        _public_context(
            row
        )
        for row in rows
    ]


def _record_entry_attempt(
    *,
    context_id: Optional[str],
    session_state_id: Optional[str],
    owner_id: Optional[str],
    tower_session_id: Optional[str],
    room_id: Optional[str],
    requested_path: str,
    decision: str,
    reason_codes: List[str],
    current_time: datetime,
    path: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_entry_database(
        database
    )

    created_at = _iso(
        current_time
    )

    attempt_id = (
        "ob_entry_attempt_"
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

    with _connect(
        database
    ) as connection:
        previous_attempt_hash = (
            _latest_attempt_hash(
                connection
            )
        )

        material = {
            "attempt_id": attempt_id,
            "context_id": (
                context_id
            ),
            "session_state_id": (
                session_state_id
            ),
            "owner_id": (
                owner_id
            ),
            "tower_session_id": (
                tower_session_id
            ),
            "room_id": (
                room_id
            ),
            "requested_path": (
                requested_path
            ),
            "decision": (
                decision
            ),
            "reason_codes": (
                reason_codes
            ),
            "previous_attempt_hash": (
                previous_attempt_hash
            ),
            "created_at": (
                created_at
            ),
        }

        attempt_hash = _sha256_text(
            _canonical_json(
                material
            )
        )

        connection.execute(
            """
            INSERT INTO
            ob_protected_room_entry_attempts (
                attempt_id,
                context_id,
                session_state_id,
                owner_id,
                tower_session_id,
                room_id,
                requested_path,
                decision,
                reason_codes_json,
                previous_attempt_hash,
                attempt_hash,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attempt_id,
                context_id,
                session_state_id,
                owner_id,
                tower_session_id,
                room_id,
                requested_path,
                decision,
                _json_text(
                    reason_codes
                ),
                previous_attempt_hash,
                attempt_hash,
                created_at,
            ),
        )

        connection.commit()

    return {
        **material,
        "attempt_hash": (
            attempt_hash
        ),
    }


def revoke_protected_room_context(
    context_id: str,
    *,
    reason: str = (
        "protected_room_context_revoked"
    ),
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_entry_database(
        database
    )

    current_time = _now(
        now
    )

    revoked_at = _iso(
        current_time
    )

    with _connect(
        database
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_contexts
            WHERE context_id = ?
            """,
            (
                str(
                    context_id
                ),
            ),
        ).fetchone()

        if row is None:
            return {
                "ok": False,
                "revoked": False,
                "reason_code": (
                    "protected_room_context_not_found"
                ),
            }

        if row[
            "state"
        ] in TERMINAL_CONTEXT_STATES:
            return {
                "ok": True,
                "revoked": True,
                "idempotent": True,
                "reason_code": (
                    "protected_room_context_already_inactive"
                ),
                "context": (
                    _public_context(
                        row
                    )
                ),
                "room_entry_allowed": False,
            }

        revoke_reason = str(
            reason
            or "protected_room_context_revoked"
        ).strip()

        revoke_hash = _sha256_text(
            _canonical_json(
                _revoke_hash_material(
                    row,
                    state="revoked",
                    revoked_at=(
                        revoked_at
                    ),
                    revoke_reason=(
                        revoke_reason
                    ),
                )
            )
        )

        connection.execute(
            """
            UPDATE ob_protected_room_contexts
            SET
                state = 'revoked',
                revoked_at = ?,
                revoke_reason = ?,
                revoke_hash = ?
            WHERE context_id = ?
              AND state = 'active'
            """,
            (
                revoked_at,
                revoke_reason,
                revoke_hash,
                str(
                    context_id
                ),
            ),
        )

        connection.commit()

    return {
        "ok": True,
        "revoked": True,
        "idempotent": False,
        "reason_code": (
            "protected_room_context_revoked"
        ),
        "context": (
            get_protected_room_context(
                context_id,
                path=database,
            )
        ),
        "room_entry_allowed": False,
        "tower_lockback_required": True,
        "production_authority_granted": False,
    }


def expire_stale_protected_room_contexts(
    *,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_entry_database(
        database
    )

    current_time = _now(
        now
    )

    expired = []
    revoked = []

    with _connect(
        database
    ) as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_contexts
            WHERE state = 'active'
            """
        ).fetchall()

    for row in rows:
        context_id = str(
            row[
                "context_id"
            ]
        )

        try:
            context_expiration = _parse_time(
                row[
                    "expires_at"
                ]
            )

        except Exception:
            context_expiration = (
                current_time
            )

        if (
            context_expiration.timestamp()
            <= current_time.timestamp()
        ):
            revoked_at = _iso(
                current_time
            )

            with _connect(
                database
            ) as connection:
                current_row = connection.execute(
                    """
                    SELECT *
                    FROM ob_protected_room_contexts
                    WHERE context_id = ?
                    """,
                    (
                        context_id,
                    ),
                ).fetchone()

                if (
                    current_row is not None
                    and current_row[
                        "state"
                    ] == "active"
                ):
                    revoke_reason = (
                        "protected_room_context_expired"
                    )

                    revoke_hash = _sha256_text(
                        _canonical_json(
                            _revoke_hash_material(
                                current_row,
                                state="expired",
                                revoked_at=(
                                    revoked_at
                                ),
                                revoke_reason=(
                                    revoke_reason
                                ),
                            )
                        )
                    )

                    connection.execute(
                        """
                        UPDATE ob_protected_room_contexts
                        SET
                            state = 'expired',
                            revoked_at = ?,
                            revoke_reason = ?,
                            revoke_hash = ?
                        WHERE context_id = ?
                          AND state = 'active'
                        """,
                        (
                            revoked_at,
                            revoke_reason,
                            revoke_hash,
                            context_id,
                        ),
                    )

                    connection.commit()

                    expired.append(
                        context_id
                    )

            continue

        session = (
            get_protected_launch_session(
                row[
                    "session_state_id"
                ],
                path=database,
            )
        )

        if (
            session is None
            or session.get(
                "state"
            )
            != "active"
        ):
            result = (
                revoke_protected_room_context(
                    context_id,
                    reason=(
                        "protected_launch_session_inactive"
                    ),
                    path=database,
                    now=current_time,
                )
            )

            if result.get(
                "revoked"
            ):
                revoked.append(
                    context_id
                )

    return {
        "ok": True,
        "expired_count": len(
            expired
        ),
        "revoked_count": len(
            revoked
        ),
        "expired_context_ids": (
            expired
        ),
        "revoked_context_ids": (
            revoked
        ),
        "production_authority_granted": False,
    }


def resolve_active_protected_room_context(
    *,
    session_state_id: str,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    expire_stale_protected_room_contexts(
        path=path,
        now=now,
    )

    with _connect(
        path
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_contexts
            WHERE session_state_id = ?
              AND state = 'active'
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
        return {
            "ok": True,
            "active": False,
            "context": None,
            "reason_code": (
                "no_active_protected_room_context"
            ),
            "production_authority_granted": False,
        }

    return {
        "ok": True,
        "active": True,
        "context": (
            _public_context(
                row
            )
        ),
        "reason_code": (
            "active_protected_room_context"
        ),
        "production_authority_granted": False,
    }


def issue_protected_room_context(
    session_state_id: str,
    *,
    owner_id: str,
    tower_session_id: str,
    requested_path: str,
    ttl_seconds: int = (
        DEFAULT_CONTEXT_TTL_SECONDS
    ),
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_entry_database(
        database
    )

    current_time = _now(
        now
    )

    expire_stale_protected_room_contexts(
        path=database,
        now=current_time,
    )

    session = (
        get_protected_launch_session(
            session_state_id,
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

    if session.get(
        "state"
    ) != "active":
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "protected_launch_session_not_active"
            ),
            "session": session,
            "production_authority_granted": False,
        }

    if (
        str(owner_id)
        != str(
            session[
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
        str(tower_session_id)
        != str(
            session[
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

    session_verification = (
        verify_protected_launch_session(
            session_state_id,
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

    matched = (
        match_protected_room_path(
            requested_path
        )
    )

    if matched is None:
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "unrecognized_protected_room_path"
            ),
            "production_authority_granted": False,
        }

    if (
        matched[
            "room_id"
        ]
        != session[
            "room_id"
        ]
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "protected_room_switch_denied"
            ),
            "bound_room_id": session[
                "room_id"
            ],
            "requested_room_id": matched[
                "room_id"
            ],
            "production_authority_granted": False,
        }

    session_route = str(
        session[
            "canonical_route"
        ]
    )

    if (
        matched[
            "canonical_route"
        ]
        != session_route
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "protected_room_route_mismatch"
            ),
            "production_authority_granted": False,
        }

    try:
        session_expires_at = (
            _parse_time(
                session[
                    "expires_at"
                ]
            )
        )

    except Exception:
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "invalid_protected_launch_expiration"
            ),
            "production_authority_granted": False,
        }

    if (
        session_expires_at.timestamp()
        <= current_time.timestamp()
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "protected_launch_session_expired"
            ),
            "production_authority_granted": False,
        }

    ttl = max(
        1,
        min(
            int(
                ttl_seconds
            ),
            MAX_CONTEXT_TTL_SECONDS,
        ),
    )

    requested_expiration = (
        current_time
        + timedelta(
            seconds=ttl
        )
    )

    context_expires_at = min(
        requested_expiration,
        session_expires_at,
    )

    normalized_requested_path = (
        matched[
            "requested_path"
        ]
    )

    with _connect(
        database
    ) as connection:
        existing = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_contexts
            WHERE session_state_id = ?
              AND state = 'active'
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (
                str(
                    session_state_id
                ),
            ),
        ).fetchone()

        if existing is not None:
            existing_context = (
                _public_context(
                    existing
                )
            )

            exact_match = (
                existing_context[
                    "owner_id"
                ]
                == str(
                    owner_id
                )
                and existing_context[
                    "tower_session_id"
                ]
                == str(
                    tower_session_id
                )
                and existing_context[
                    "room_id"
                ]
                == matched[
                    "room_id"
                ]
                and existing_context[
                    "requested_path"
                ]
                == normalized_requested_path
            )

            if exact_match:
                return {
                    "ok": True,
                    "created": False,
                    "idempotent": True,
                    "reason_code": (
                        "protected_room_context_already_active"
                    ),
                    "context": (
                        existing_context
                    ),
                    "production_authority_granted": False,
                }

            return {
                "ok": False,
                "created": False,
                "reason_code": (
                    "active_context_route_conflict"
                ),
                "active_context": (
                    existing_context
                ),
                "production_authority_granted": False,
            }

        context_id = (
            "ob_room_context_"
            + secrets.token_urlsafe(
                24
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

        expires_at_text = _iso(
            context_expires_at
        )

        previous_context_hash = (
            _latest_context_hash(
                connection
            )
        )

        record = {
            "context_id": context_id,
            "session_state_id": str(
                session_state_id
            ),
            "intake_id": str(
                session[
                    "intake_id"
                ]
            ),
            "owner_id": str(
                owner_id
            ),
            "tower_session_id": str(
                tower_session_id
            ),
            "room_id": matched[
                "room_id"
            ],
            "canonical_route": matched[
                "canonical_route"
            ],
            "requested_path": (
                normalized_requested_path
            ),
            "route_parameters": matched[
                "route_parameters"
            ],
            "mode": str(
                session[
                    "mode"
                ]
            ),
            "issued_at": (
                created_at
            ),
            "expires_at": (
                expires_at_text
            ),
            "session_hash": str(
                session[
                    "session_hash"
                ]
            ),
            "previous_context_hash": (
                previous_context_hash
            ),
            "created_at": (
                created_at
            ),
        }

        context_hash = _sha256_text(
            _canonical_json(
                _context_hash_material(
                    record
                )
            )
        )

        connection.execute(
            """
            INSERT INTO
            ob_protected_room_contexts (
                context_id,
                session_state_id,
                intake_id,
                owner_id,
                tower_session_id,
                room_id,
                canonical_route,
                requested_path,
                route_parameters_json,
                mode,
                state,
                issued_at,
                expires_at,
                revoked_at,
                revoke_reason,
                session_hash,
                previous_context_hash,
                context_hash,
                revoke_hash,
                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                'active', ?, ?, NULL, NULL, ?, ?, ?, NULL, ?
            )
            """,
            (
                context_id,
                str(
                    session_state_id
                ),
                str(
                    session[
                        "intake_id"
                    ]
                ),
                str(
                    owner_id
                ),
                str(
                    tower_session_id
                ),
                matched[
                    "room_id"
                ],
                matched[
                    "canonical_route"
                ],
                normalized_requested_path,
                _json_text(
                    matched[
                        "route_parameters"
                    ]
                ),
                str(
                    session[
                        "mode"
                    ]
                ),
                created_at,
                expires_at_text,
                str(
                    session[
                        "session_hash"
                    ]
                ),
                previous_context_hash,
                context_hash,
                created_at,
            ),
        )

        connection.commit()

    context = (
        get_protected_room_context(
            context_id,
            path=database,
        )
    )

    return {
        "ok": True,
        "created": True,
        "idempotent": False,
        "reason_code": (
            "protected_room_context_issued"
        ),
        "context": context,
        "context_cannot_outlive_session": True,
        "room_switch_allowed": False,
        "expiration_extension_allowed": False,
        "production_authority_granted": False,
    }


def authorize_protected_room_entry(
    *,
    context_id: Optional[str],
    owner_id: Optional[str],
    tower_session_id: Optional[str],
    requested_path: str,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_entry_database(
        database
    )

    current_time = _now(
        now
    )

    normalized_path = (
        normalize_request_path(
            requested_path
        )
    )

    matched = (
        match_protected_room_path(
            normalized_path
        )
    )

    if matched is None:
        return {
            "allowed": True,
            "protected_room": False,
            "reason_codes": [
                "path_not_protected_room"
            ],
            "context": None,
            "production_authority_granted": False,
        }

    expire_stale_protected_room_contexts(
        path=database,
        now=current_time,
    )

    reasons: List[str] = []

    if not context_id:
        reasons.append(
            "protected_room_context_required"
        )

    if not owner_id:
        reasons.append(
            "tower_owner_identity_required"
        )

    if not tower_session_id:
        reasons.append(
            "tower_session_identity_required"
        )

    context = None

    if context_id:
        context = (
            get_protected_room_context(
                context_id,
                path=database,
            )
        )

        if context is None:
            reasons.append(
                "protected_room_context_not_found"
            )

    if context is not None:
        if context[
            "state"
        ] != "active":
            reasons.append(
                "protected_room_context_not_active"
            )

        if (
            owner_id
            and str(
                owner_id
            )
            != str(
                context[
                    "owner_id"
                ]
            )
        ):
            reasons.append(
                "owner_identity_mismatch"
            )

        if (
            tower_session_id
            and str(
                tower_session_id
            )
            != str(
                context[
                    "tower_session_id"
                ]
            )
        ):
            reasons.append(
                "tower_session_identity_mismatch"
            )

        if (
            context[
                "room_id"
            ]
            != matched[
                "room_id"
            ]
        ):
            reasons.append(
                "protected_room_switch_denied"
            )

        if (
            context[
                "canonical_route"
            ]
            != matched[
                "canonical_route"
            ]
        ):
            reasons.append(
                "protected_room_route_mismatch"
            )

        if (
            context[
                "requested_path"
            ]
            != matched[
                "requested_path"
            ]
        ):
            reasons.append(
                "protected_room_path_mismatch"
            )

        try:
            context_expiration = (
                _parse_time(
                    context[
                        "expires_at"
                    ]
                )
            )

            if (
                context_expiration.timestamp()
                <= current_time.timestamp()
            ):
                reasons.append(
                    "protected_room_context_expired"
                )

        except Exception:
            reasons.append(
                "invalid_protected_room_context_expiration"
            )

        session = (
            get_protected_launch_session(
                context[
                    "session_state_id"
                ],
                path=database,
            )
        )

        if session is None:
            reasons.append(
                "protected_launch_session_not_found"
            )

        else:
            if (
                session[
                    "state"
                ]
                != "active"
            ):
                reasons.append(
                    "protected_launch_session_not_active"
                )

            if (
                session[
                    "owner_id"
                ]
                != context[
                    "owner_id"
                ]
            ):
                reasons.append(
                    "session_owner_binding_mismatch"
                )

            if (
                session[
                    "tower_session_id"
                ]
                != context[
                    "tower_session_id"
                ]
            ):
                reasons.append(
                    "session_identity_binding_mismatch"
                )

            if (
                session[
                    "room_id"
                ]
                != context[
                    "room_id"
                ]
            ):
                reasons.append(
                    "session_room_binding_mismatch"
                )

            if (
                session[
                    "session_hash"
                ]
                != context[
                    "session_hash"
                ]
            ):
                reasons.append(
                    "session_hash_binding_mismatch"
                )

            verification = (
                verify_protected_launch_session(
                    context[
                        "session_state_id"
                    ],
                    path=database,
                )
            )

            if not verification.get(
                "verified"
            ):
                reasons.append(
                    "protected_launch_session_integrity_failed"
                )

    reasons = _unique(
        reasons
    )

    allowed = not bool(
        reasons
    )

    attempt = _record_entry_attempt(
        context_id=(
            context[
                "context_id"
            ]
            if context
            else (
                str(
                    context_id
                )
                if context_id
                else None
            )
        ),
        session_state_id=(
            context[
                "session_state_id"
            ]
            if context
            else None
        ),
        owner_id=(
            str(
                owner_id
            )
            if owner_id
            else None
        ),
        tower_session_id=(
            str(
                tower_session_id
            )
            if tower_session_id
            else None
        ),
        room_id=matched[
            "room_id"
        ],
        requested_path=(
            normalized_path
        ),
        decision=(
            "allowed"
            if allowed
            else "denied"
        ),
        reason_codes=(
            reasons
        ),
        current_time=(
            current_time
        ),
        path=database,
    )

    return {
        "allowed": allowed,
        "protected_room": True,
        "reason_codes": reasons,
        "reason_code": (
            "protected_room_entry_allowed"
            if allowed
            else (
                reasons[0]
                if reasons
                else "protected_room_entry_denied"
            )
        ),
        "room": matched,
        "context": (
            context
            if allowed
            else None
        ),
        "attempt": attempt,
        "tower_authority_required": True,
        "ob_self_authorization_allowed": False,
        "production_authority_granted": False,
    }


def verify_protected_room_context(
    context_id: str,
    *,
    path: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_entry_database(
        database
    )

    with _connect(
        database
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_contexts
            WHERE context_id = ?
            """,
            (
                str(
                    context_id
                ),
            ),
        ).fetchone()

        if row is None:
            return {
                "verified": False,
                "reason_codes": [
                    "protected_room_context_not_found"
                ],
            }

        route_parameters = json.loads(
            row[
                "route_parameters_json"
            ]
        )

        record = {
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
            "requested_path": row[
                "requested_path"
            ],
            "route_parameters": (
                route_parameters
            ),
            "mode": row[
                "mode"
            ],
            "issued_at": row[
                "issued_at"
            ],
            "expires_at": row[
                "expires_at"
            ],
            "session_hash": row[
                "session_hash"
            ],
            "previous_context_hash": row[
                "previous_context_hash"
            ],
            "created_at": row[
                "created_at"
            ],
        }

        computed_context_hash = (
            _sha256_text(
                _canonical_json(
                    _context_hash_material(
                        record
                    )
                )
            )
        )

        checks = {
            "context_hash_matches": (
                hmac.compare_digest(
                    computed_context_hash,
                    str(
                        row[
                            "context_hash"
                        ]
                    ),
                )
            ),
            "previous_context_hash_valid": True,
            "route_contract_matches": False,
            "session_exists": False,
            "session_hash_matches": False,
            "session_verified": False,
            "revoke_hash_valid": True,
            "attempt_chain_valid": True,
        }

        if (
            row[
                "previous_context_hash"
            ]
            != ZERO_HASH
        ):
            previous = connection.execute(
                """
                SELECT 1
                FROM ob_protected_room_contexts
                WHERE context_hash = ?
                LIMIT 1
                """,
                (
                    row[
                        "previous_context_hash"
                    ],
                ),
            ).fetchone()

            checks[
                "previous_context_hash_valid"
            ] = previous is not None

        matched = (
            match_protected_room_path(
                row[
                    "requested_path"
                ]
            )
        )

        checks[
            "route_contract_matches"
        ] = bool(
            matched
            and matched[
                "room_id"
            ]
            == row[
                "room_id"
            ]
            and matched[
                "canonical_route"
            ]
            == row[
                "canonical_route"
            ]
        )

        if (
            row[
                "state"
            ]
            in TERMINAL_CONTEXT_STATES
        ):
            expected_revoke_hash = (
                _sha256_text(
                    _canonical_json(
                        _revoke_hash_material(
                            row,
                            state=row[
                                "state"
                            ],
                            revoked_at=str(
                                row[
                                    "revoked_at"
                                ]
                                or ""
                            ),
                            revoke_reason=str(
                                row[
                                    "revoke_reason"
                                ]
                                or ""
                            ),
                        )
                    )
                )
            )

            checks[
                "revoke_hash_valid"
            ] = hmac.compare_digest(
                str(
                    row[
                        "revoke_hash"
                    ]
                    or ""
                ),
                expected_revoke_hash,
            )

        attempts = connection.execute(
            """
            SELECT *
            FROM ob_protected_room_entry_attempts
            ORDER BY rowid ASC
            """
        ).fetchall()

        previous_attempt_hash = (
            ZERO_HASH
        )

        for attempt in attempts:
            try:
                reason_codes = json.loads(
                    attempt[
                        "reason_codes_json"
                    ]
                )

            except Exception:
                checks[
                    "attempt_chain_valid"
                ] = False
                break

            material = {
                "attempt_id": attempt[
                    "attempt_id"
                ],
                "context_id": attempt[
                    "context_id"
                ],
                "session_state_id": attempt[
                    "session_state_id"
                ],
                "owner_id": attempt[
                    "owner_id"
                ],
                "tower_session_id": attempt[
                    "tower_session_id"
                ],
                "room_id": attempt[
                    "room_id"
                ],
                "requested_path": attempt[
                    "requested_path"
                ],
                "decision": attempt[
                    "decision"
                ],
                "reason_codes": (
                    reason_codes
                ),
                "previous_attempt_hash": attempt[
                    "previous_attempt_hash"
                ],
                "created_at": attempt[
                    "created_at"
                ],
            }

            computed_attempt_hash = (
                _sha256_text(
                    _canonical_json(
                        material
                    )
                )
            )

            if (
                attempt[
                    "previous_attempt_hash"
                ]
                != previous_attempt_hash
            ):
                checks[
                    "attempt_chain_valid"
                ] = False
                break

            if not hmac.compare_digest(
                computed_attempt_hash,
                str(
                    attempt[
                        "attempt_hash"
                    ]
                ),
            ):
                checks[
                    "attempt_chain_valid"
                ] = False
                break

            previous_attempt_hash = (
                attempt[
                    "attempt_hash"
                ]
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
        "context_id": str(
            context_id
        ),
        "state": row[
            "state"
        ],
        "context_hash": row[
            "context_hash"
        ],
        "revoke_hash": row[
            "revoke_hash"
        ],
        "production_authority_granted": False,
    }


def protected_room_entry_status(
    *,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_entry_database(
        database
    )

    expiration = (
        expire_stale_protected_room_contexts(
            path=database,
            now=now,
        )
    )

    with _connect(
        database
    ) as connection:
        context_totals = connection.execute(
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
                        WHEN state = 'revoked'
                        THEN 1 ELSE 0
                    END
                ) AS revoked,
                SUM(
                    CASE
                        WHEN state = 'expired'
                        THEN 1 ELSE 0
                    END
                ) AS expired
            FROM ob_protected_room_contexts
            """
        ).fetchone()

        attempt_totals = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE
                        WHEN decision = 'allowed'
                        THEN 1 ELSE 0
                    END
                ) AS allowed,
                SUM(
                    CASE
                        WHEN decision = 'denied'
                        THEN 1 ELSE 0
                    END
                ) AS denied
            FROM ob_protected_room_entry_attempts
            """
        ).fetchone()

    return {
        "ok": True,
        "pack": PACK,
        "contract_version": CONTRACT_VERSION,
        "database_path": str(
            database
        ),
        "context_total": int(
            context_totals[
                "total"
            ]
            or 0
        ),
        "context_active": int(
            context_totals[
                "active"
            ]
            or 0
        ),
        "context_revoked": int(
            context_totals[
                "revoked"
            ]
            or 0
        ),
        "context_expired": int(
            context_totals[
                "expired"
            ]
            or 0
        ),
        "entry_attempt_total": int(
            attempt_totals[
                "total"
            ]
            or 0
        ),
        "entry_allowed": int(
            attempt_totals[
                "allowed"
            ]
            or 0
        ),
        "entry_denied": int(
            attempt_totals[
                "denied"
            ]
            or 0
        ),
        "expired_during_check": (
            expiration[
                "expired_count"
            ]
        ),
        "revoked_during_check": (
            expiration[
                "revoked_count"
            ]
        ),
        "protected_room_count": 6,
        "default_deny": True,
        "one_active_context_per_session": True,
        "room_switch_allowed": False,
        "context_can_outlive_session": False,
        "expiration_extension_allowed": False,
        "tower_authority_required": True,
        "ob_self_authorization_allowed": False,
        "http_context_mutation_enabled": (
            os.environ.get(
                "OB_PROTECTED_ROOM_ENTRY_HTTP_ENABLED",
                "0",
            )
            == "1"
        ),
        "room_entry_guard_enabled": (
            os.environ.get(
                "OB_PROTECTED_ROOM_ENTRY_GUARD_ENABLED",
                "1",
            )
            == "1"
        ),
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
    }
