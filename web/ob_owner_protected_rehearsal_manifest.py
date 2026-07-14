
"""OB GP051 — Owner Protected Rehearsal Run Manifest and Step Sequence.

A run manifest is a local Observatory rehearsal plan. It does not grant Tower
identity, clearance, step-up, launch approval, room access, production Manual
Live authority, broker authority, or capital-movement authority.

Each completed step must carry an external evidence reference and SHA-256
evidence hash. OB records that evidence; it does not manufacture it.
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

from web.ob_tower_protected_launch_handoff_consumer import (
    ROOM_REGISTRY,
)

from web.ob_protected_launch_corridor_readiness import (
    READY_RECOMMENDATION,
    get_readiness_assessment,
    verify_readiness_assessment,
)


OB_GIANT_PACK_051_OWNER_PROTECTED_REHEARSAL_MANIFEST_SERVICE = True

PACK = "GP051"
CONTRACT_VERSION = "ob.owner_protected_rehearsal_manifest.v1"

ZERO_HASH = "0" * 64

OPEN_RUN_STATES = {
    "planned",
    "active",
    "on_hold",
}

TERMINAL_RUN_STATES = {
    "completed",
}

CANONICAL_REHEARSAL_STEPS = [
    {
        "step_index": 1,
        "step_code": "corridor_readiness_confirmed",
        "title": "Confirm GP050 corridor readiness",
    },
    {
        "step_index": 2,
        "step_code": "tower_launch_handoff_received",
        "title": "Receive Tower-protected launch handoff",
    },
    {
        "step_index": 3,
        "step_code": "protected_launch_session_started",
        "title": "Start the protected OB launch session",
    },
    {
        "step_index": 4,
        "step_code": "protected_room_context_issued",
        "title": "Issue the exact protected-room context",
    },
    {
        "step_index": 5,
        "step_code": "candidate_review_confirmed",
        "title": "Confirm candidate review and owner decision",
    },
    {
        "step_index": 6,
        "step_code": "manual_checklist_saved",
        "title": "Save the Manual Live Level 1 checklist record",
    },
    {
        "step_index": 7,
        "step_code": "dry_run_outcome_finalized",
        "title": "Finalize the dry-run outcome",
    },
    {
        "step_index": 8,
        "step_code": "receipt_review_verified",
        "title": "Verify the outcome receipt in Review Center",
    },
    {
        "step_index": 9,
        "step_code": "protected_room_exit_closed",
        "title": "Close protected-room entry and the local session",
    },
    {
        "step_index": 10,
        "step_code": "tower_lockback_acknowledged",
        "title": "Record Tower lockback acknowledgment",
    },
]


def _default_database_path() -> Path:
    configured = (
        os.environ.get(
            "OB_OWNER_REHEARSAL_DB_PATH"
        )
        or os.environ.get(
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
        / "ob_owner_rehearsal_gp051.sqlite3"
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


def _valid_identifier(
    value: Any,
    *,
    minimum: int = 3,
    maximum: int = 200,
) -> bool:
    rendered = str(
        value or ""
    ).strip()

    return bool(
        re.fullmatch(
            rf"[A-Za-z0-9_.:\-]{{{minimum},{maximum}}}",
            rendered,
        )
    )


def _valid_evidence_hash(
    value: Any,
) -> bool:
    return bool(
        re.fullmatch(
            r"[0-9a-fA-F]{64}",
            str(
                value or ""
            ).strip(),
        )
    )


def init_rehearsal_database(
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
            ob_owner_rehearsal_runs (
                run_id TEXT PRIMARY KEY,
                owner_id TEXT NOT NULL,
                readiness_assessment_id TEXT NOT NULL UNIQUE,
                readiness_assessment_hash TEXT NOT NULL,
                room_id TEXT NOT NULL,
                canonical_route TEXT NOT NULL,
                status TEXT NOT NULL,
                current_step_index INTEGER NOT NULL,
                step_count INTEGER NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                hold_reason TEXT,
                previous_manifest_hash TEXT NOT NULL,
                manifest_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            );

            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_ob_one_open_rehearsal_per_owner
            ON ob_owner_rehearsal_runs(
                owner_id
            )
            WHERE status IN (
                'planned',
                'active',
                'on_hold'
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_rehearsal_run_owner
            ON ob_owner_rehearsal_runs(
                owner_id,
                created_at
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_rehearsal_run_status
            ON ob_owner_rehearsal_runs(
                status,
                created_at
            );

            CREATE TABLE IF NOT EXISTS
            ob_owner_rehearsal_steps (
                run_id TEXT NOT NULL,
                step_index INTEGER NOT NULL,
                step_code TEXT NOT NULL,
                title TEXT NOT NULL,
                state TEXT NOT NULL,
                evidence_ref TEXT,
                evidence_hash TEXT,
                previous_step_hash TEXT,
                step_hash TEXT,
                completed_at TEXT,
                PRIMARY KEY(
                    run_id,
                    step_index
                ),
                UNIQUE(
                    run_id,
                    step_code
                ),
                FOREIGN KEY(
                    run_id
                )
                REFERENCES ob_owner_rehearsal_runs(
                    run_id
                )
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_rehearsal_step_state
            ON ob_owner_rehearsal_steps(
                run_id,
                state,
                step_index
            );

            CREATE TABLE IF NOT EXISTS
            ob_owner_rehearsal_events (
                event_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                previous_event_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                FOREIGN KEY(
                    run_id
                )
                REFERENCES ob_owner_rehearsal_runs(
                    run_id
                )
            );

            CREATE INDEX IF NOT EXISTS
            idx_ob_rehearsal_event_run
            ON ob_owner_rehearsal_events(
                run_id,
                created_at
            );
            """
        )

    return str(
        database
    )


def _latest_manifest_hash(
    connection: sqlite3.Connection,
) -> str:
    row = connection.execute(
        """
        SELECT manifest_hash
        FROM ob_owner_rehearsal_runs
        ORDER BY rowid DESC
        LIMIT 1
        """
    ).fetchone()

    if row is None:
        return ZERO_HASH

    return str(
        row[
            "manifest_hash"
        ]
    )


def _latest_event_hash(
    connection: sqlite3.Connection,
    run_id: str,
) -> str:
    row = connection.execute(
        """
        SELECT event_hash
        FROM ob_owner_rehearsal_events
        WHERE run_id = ?
        ORDER BY rowid DESC
        LIMIT 1
        """,
        (
            str(
                run_id
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


def _latest_completed_step_hash(
    connection: sqlite3.Connection,
    run_id: str,
) -> str:
    row = connection.execute(
        """
        SELECT step_hash
        FROM ob_owner_rehearsal_steps
        WHERE run_id = ?
          AND state = 'completed'
        ORDER BY step_index DESC
        LIMIT 1
        """,
        (
            str(
                run_id
            ),
        ),
    ).fetchone()

    if row is None:
        return ZERO_HASH

    return str(
        row[
            "step_hash"
        ]
    )


def _manifest_hash_material(
    record: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "run_id": record[
            "run_id"
        ],
        "owner_id": record[
            "owner_id"
        ],
        "readiness_assessment_id": record[
            "readiness_assessment_id"
        ],
        "readiness_assessment_hash": record[
            "readiness_assessment_hash"
        ],
        "room_id": record[
            "room_id"
        ],
        "canonical_route": record[
            "canonical_route"
        ],
        "step_sequence": (
            CANONICAL_REHEARSAL_STEPS
        ),
        "step_count": len(
            CANONICAL_REHEARSAL_STEPS
        ),
        "previous_manifest_hash": record[
            "previous_manifest_hash"
        ],
        "created_at": record[
            "created_at"
        ],
        "dry_run_only": True,
        "tower_launch_authorized": False,
        "room_entry_authorized": False,
        "production_authority_granted": False,
    }


def _step_hash_material(
    record: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "run_id": record[
            "run_id"
        ],
        "step_index": record[
            "step_index"
        ],
        "step_code": record[
            "step_code"
        ],
        "evidence_ref": record[
            "evidence_ref"
        ],
        "evidence_hash": record[
            "evidence_hash"
        ],
        "previous_step_hash": record[
            "previous_step_hash"
        ],
        "completed_at": record[
            "completed_at"
        ],
        "dry_run_only": True,
        "production_authority_granted": False,
    }


def _append_event(
    connection: sqlite3.Connection,
    *,
    run_id: str,
    event_type: str,
    payload: Dict[str, Any],
    created_at: str,
) -> Dict[str, Any]:
    previous_event_hash = (
        _latest_event_hash(
            connection,
            run_id,
        )
    )

    event_id = (
        "ob_rehearsal_event_"
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
        "run_id": run_id,
        "event_type": event_type,
        "payload": payload,
        "previous_event_hash": (
            previous_event_hash
        ),
        "created_at": created_at,
    }

    event_hash = _sha256_text(
        _canonical_json(
            material
        )
    )

    connection.execute(
        """
        INSERT INTO
        ob_owner_rehearsal_events (
            event_id,
            run_id,
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
            run_id,
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


def _public_step(
    row: sqlite3.Row,
) -> Dict[str, Any]:
    return {
        "step_index": row[
            "step_index"
        ],
        "step_code": row[
            "step_code"
        ],
        "title": row[
            "title"
        ],
        "state": row[
            "state"
        ],
        "evidence_ref": row[
            "evidence_ref"
        ],
        "evidence_hash": row[
            "evidence_hash"
        ],
        "previous_step_hash": row[
            "previous_step_hash"
        ],
        "step_hash": row[
            "step_hash"
        ],
        "completed_at": row[
            "completed_at"
        ],
    }


def _public_run(
    row: sqlite3.Row,
    steps: List[sqlite3.Row],
) -> Dict[str, Any]:
    current_step = None

    for step in steps:
        if step[
            "state"
        ] == "current":
            current_step = _public_step(
                step
            )
            break

    completed_count = sum(
        1
        for step in steps
        if step[
            "state"
        ] == "completed"
    )

    return {
        "run_id": row[
            "run_id"
        ],
        "owner_id": row[
            "owner_id"
        ],
        "readiness_assessment_id": row[
            "readiness_assessment_id"
        ],
        "readiness_assessment_hash": row[
            "readiness_assessment_hash"
        ],
        "room_id": row[
            "room_id"
        ],
        "canonical_route": row[
            "canonical_route"
        ],
        "status": row[
            "status"
        ],
        "current_step_index": row[
            "current_step_index"
        ],
        "step_count": row[
            "step_count"
        ],
        "completed_step_count": (
            completed_count
        ),
        "current_step": (
            current_step
        ),
        "steps": [
            _public_step(
                step
            )
            for step in steps
        ],
        "started_at": row[
            "started_at"
        ],
        "completed_at": row[
            "completed_at"
        ],
        "hold_reason": row[
            "hold_reason"
        ],
        "previous_manifest_hash": row[
            "previous_manifest_hash"
        ],
        "manifest_hash": row[
            "manifest_hash"
        ],
        "created_at": row[
            "created_at"
        ],
        "dry_run_only": True,
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


def get_owner_rehearsal_run(
    run_id: str,
    *,
    path: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    init_rehearsal_database(
        path
    )

    with _connect(
        path
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_owner_rehearsal_runs
            WHERE run_id = ?
            """,
            (
                str(
                    run_id
                ),
            ),
        ).fetchone()

        if row is None:
            return None

        steps = connection.execute(
            """
            SELECT *
            FROM ob_owner_rehearsal_steps
            WHERE run_id = ?
            ORDER BY step_index ASC
            """,
            (
                str(
                    run_id
                ),
            ),
        ).fetchall()

    return _public_run(
        row,
        steps,
    )


def list_owner_rehearsal_runs(
    *,
    owner_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    path: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    init_rehearsal_database(
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
        FROM ob_owner_rehearsal_runs
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

    if status:
        clauses.append(
            "status = ?"
        )

        parameters.append(
            str(
                status
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

    output = []

    with _connect(
        path
    ) as connection:
        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

        for row in rows:
            steps = connection.execute(
                """
                SELECT *
                FROM ob_owner_rehearsal_steps
                WHERE run_id = ?
                ORDER BY step_index ASC
                """,
                (
                    row[
                        "run_id"
                    ],
                ),
            ).fetchall()

            output.append(
                _public_run(
                    row,
                    steps,
                )
            )

    return output


def create_owner_rehearsal_manifest(
    *,
    owner_id: str,
    readiness_assessment_id: str,
    room_id: str,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_rehearsal_database(
        database
    )

    normalized_owner = str(
        owner_id
        or ""
    ).strip()

    normalized_assessment = str(
        readiness_assessment_id
        or ""
    ).strip()

    normalized_room = str(
        room_id
        or ""
    ).strip()

    if not _valid_identifier(
        normalized_owner
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "valid_owner_id_required"
            ),
            "production_authority_granted": False,
        }

    if not _valid_identifier(
        normalized_assessment,
        minimum=8,
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "valid_readiness_assessment_id_required"
            ),
            "production_authority_granted": False,
        }

    if normalized_room not in ROOM_REGISTRY:
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "unknown_rehearsal_room"
            ),
            "production_authority_granted": False,
        }

    assessment = (
        get_readiness_assessment(
            normalized_assessment,
            path=database,
        )
    )

    if assessment is None:
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "readiness_assessment_not_found"
            ),
            "production_authority_granted": False,
        }

    if (
        assessment[
            "owner_id"
        ]
        != normalized_owner
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "readiness_owner_mismatch"
            ),
            "production_authority_granted": False,
        }

    assessment_verification = (
        verify_readiness_assessment(
            normalized_assessment,
            path=database,
        )
    )

    if not assessment_verification.get(
        "verified"
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "readiness_assessment_integrity_failed"
            ),
            "verification": (
                assessment_verification
            ),
            "production_authority_granted": False,
        }

    if (
        assessment[
            "local_readiness_passed"
        ]
        is not True
        or assessment[
            "recommendation"
        ]
        != READY_RECOMMENDATION
    ):
        return {
            "ok": False,
            "created": False,
            "reason_code": (
                "gp050_ready_assessment_required"
            ),
            "assessment": (
                assessment
            ),
            "production_authority_granted": False,
        }

    canonical_route = str(
        ROOM_REGISTRY[
            normalized_room
        ][
            "canonical_route"
        ]
    )

    with _connect(
        database
    ) as connection:
        existing = connection.execute(
            """
            SELECT *
            FROM ob_owner_rehearsal_runs
            WHERE readiness_assessment_id = ?
            """,
            (
                normalized_assessment,
            ),
        ).fetchone()

        if existing is not None:
            steps = connection.execute(
                """
                SELECT *
                FROM ob_owner_rehearsal_steps
                WHERE run_id = ?
                ORDER BY step_index ASC
                """,
                (
                    existing[
                        "run_id"
                    ],
                ),
            ).fetchall()

            existing_run = (
                _public_run(
                    existing,
                    steps,
                )
            )

            exact_match = (
                existing_run[
                    "owner_id"
                ]
                == normalized_owner
                and existing_run[
                    "room_id"
                ]
                == normalized_room
            )

            if exact_match:
                return {
                    "ok": True,
                    "created": False,
                    "idempotent": True,
                    "reason_code": (
                        "owner_rehearsal_manifest_already_exists"
                    ),
                    "run": existing_run,
                    "production_authority_granted": False,
                }

            return {
                "ok": False,
                "created": False,
                "reason_code": (
                    "readiness_assessment_manifest_conflict"
                ),
                "production_authority_granted": False,
            }

        open_run = connection.execute(
            """
            SELECT *
            FROM ob_owner_rehearsal_runs
            WHERE owner_id = ?
              AND status IN (
                  'planned',
                  'active',
                  'on_hold'
              )
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (
                normalized_owner,
            ),
        ).fetchone()

        if open_run is not None:
            return {
                "ok": False,
                "created": False,
                "reason_code": (
                    "owner_open_rehearsal_run_exists"
                ),
                "open_run_id": open_run[
                    "run_id"
                ],
                "production_authority_granted": False,
            }

        run_id = (
            "ob_rehearsal_run_"
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

        previous_manifest_hash = (
            _latest_manifest_hash(
                connection
            )
        )

        record = {
            "run_id": run_id,
            "owner_id": (
                normalized_owner
            ),
            "readiness_assessment_id": (
                normalized_assessment
            ),
            "readiness_assessment_hash": (
                assessment[
                    "assessment_hash"
                ]
            ),
            "room_id": (
                normalized_room
            ),
            "canonical_route": (
                canonical_route
            ),
            "previous_manifest_hash": (
                previous_manifest_hash
            ),
            "created_at": (
                created_at
            ),
        }

        manifest_hash = _sha256_text(
            _canonical_json(
                _manifest_hash_material(
                    record
                )
            )
        )

        connection.execute(
            """
            INSERT INTO
            ob_owner_rehearsal_runs (
                run_id,
                owner_id,
                readiness_assessment_id,
                readiness_assessment_hash,
                room_id,
                canonical_route,
                status,
                current_step_index,
                step_count,
                started_at,
                completed_at,
                hold_reason,
                previous_manifest_hash,
                manifest_hash,
                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?,
                'planned', 1, ?,
                NULL, NULL, NULL,
                ?, ?, ?
            )
            """,
            (
                run_id,
                normalized_owner,
                normalized_assessment,
                assessment[
                    "assessment_hash"
                ],
                normalized_room,
                canonical_route,
                len(
                    CANONICAL_REHEARSAL_STEPS
                ),
                previous_manifest_hash,
                manifest_hash,
                created_at,
            ),
        )

        for step in (
            CANONICAL_REHEARSAL_STEPS
        ):
            state = (
                "current"
                if step[
                    "step_index"
                ]
                == 1
                else "pending"
            )

            connection.execute(
                """
                INSERT INTO
                ob_owner_rehearsal_steps (
                    run_id,
                    step_index,
                    step_code,
                    title,
                    state,
                    evidence_ref,
                    evidence_hash,
                    previous_step_hash,
                    step_hash,
                    completed_at
                )
                VALUES (
                    ?, ?, ?, ?, ?,
                    NULL, NULL, NULL, NULL, NULL
                )
                """,
                (
                    run_id,
                    step[
                        "step_index"
                    ],
                    step[
                        "step_code"
                    ],
                    step[
                        "title"
                    ],
                    state,
                ),
            )

        _append_event(
            connection,
            run_id=run_id,
            event_type=(
                "rehearsal_manifest_created"
            ),
            payload={
                "owner_id": (
                    normalized_owner
                ),
                "room_id": (
                    normalized_room
                ),
                "canonical_route": (
                    canonical_route
                ),
                "readiness_assessment_id": (
                    normalized_assessment
                ),
                "step_count": len(
                    CANONICAL_REHEARSAL_STEPS
                ),
                "dry_run_only": True,
                "tower_launch_authorized": False,
                "production_authority_granted": False,
            },
            created_at=(
                created_at
            ),
        )

        connection.commit()

    return {
        "ok": True,
        "created": True,
        "idempotent": False,
        "reason_code": (
            "owner_rehearsal_manifest_created"
        ),
        "run": (
            get_owner_rehearsal_run(
                run_id,
                path=database,
            )
        ),
        "tower_launch_authorized": False,
        "room_entry_authorized": False,
        "production_authority_granted": False,
    }


def start_owner_rehearsal_run(
    run_id: str,
    *,
    owner_id: str,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_rehearsal_database(
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
            FROM ob_owner_rehearsal_runs
            WHERE run_id = ?
            """,
            (
                str(
                    run_id
                ),
            ),
        ).fetchone()

        if row is None:
            return {
                "ok": False,
                "started": False,
                "reason_code": (
                    "owner_rehearsal_run_not_found"
                ),
            }

        if (
            str(
                owner_id
            )
            != str(
                row[
                    "owner_id"
                ]
            )
        ):
            return {
                "ok": False,
                "started": False,
                "reason_code": (
                    "owner_identity_mismatch"
                ),
            }

        if row[
            "status"
        ] == "active":
            return {
                "ok": True,
                "started": True,
                "idempotent": True,
                "reason_code": (
                    "owner_rehearsal_run_already_active"
                ),
                "run": (
                    get_owner_rehearsal_run(
                        run_id,
                        path=database,
                    )
                ),
                "production_authority_granted": False,
            }

        if row[
            "status"
        ] != "planned":
            return {
                "ok": False,
                "started": False,
                "reason_code": (
                    "owner_rehearsal_run_not_startable"
                ),
                "status": row[
                    "status"
                ],
            }

        started_at = _iso(
            current_time
        )

        connection.execute(
            """
            UPDATE ob_owner_rehearsal_runs
            SET
                status = 'active',
                started_at = ?
            WHERE run_id = ?
              AND status = 'planned'
            """,
            (
                started_at,
                str(
                    run_id
                ),
            ),
        )

        _append_event(
            connection,
            run_id=str(
                run_id
            ),
            event_type=(
                "rehearsal_run_started"
            ),
            payload={
                "started_at": (
                    started_at
                ),
                "current_step_index": 1,
                "dry_run_only": True,
                "tower_launch_authorized": False,
            },
            created_at=(
                started_at
            ),
        )

        connection.commit()

    return {
        "ok": True,
        "started": True,
        "idempotent": False,
        "reason_code": (
            "owner_rehearsal_run_started"
        ),
        "run": (
            get_owner_rehearsal_run(
                run_id,
                path=database,
            )
        ),
        "production_authority_granted": False,
    }


def advance_owner_rehearsal_step(
    run_id: str,
    *,
    owner_id: str,
    step_code: str,
    evidence_ref: str,
    evidence_hash: str,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_rehearsal_database(
        database
    )

    current_time = _now(
        now
    )

    normalized_step_code = str(
        step_code
        or ""
    ).strip()

    normalized_evidence_ref = str(
        evidence_ref
        or ""
    ).strip()

    normalized_evidence_hash = str(
        evidence_hash
        or ""
    ).strip().lower()

    if not _valid_identifier(
        normalized_evidence_ref,
        minimum=6,
    ):
        return {
            "ok": False,
            "advanced": False,
            "reason_code": (
                "valid_evidence_ref_required"
            ),
        }

    if not _valid_evidence_hash(
        normalized_evidence_hash
    ):
        return {
            "ok": False,
            "advanced": False,
            "reason_code": (
                "valid_sha256_evidence_hash_required"
            ),
        }

    with _connect(
        database
    ) as connection:
        run_row = connection.execute(
            """
            SELECT *
            FROM ob_owner_rehearsal_runs
            WHERE run_id = ?
            """,
            (
                str(
                    run_id
                ),
            ),
        ).fetchone()

        if run_row is None:
            return {
                "ok": False,
                "advanced": False,
                "reason_code": (
                    "owner_rehearsal_run_not_found"
                ),
            }

        if (
            str(
                owner_id
            )
            != str(
                run_row[
                    "owner_id"
                ]
            )
        ):
            return {
                "ok": False,
                "advanced": False,
                "reason_code": (
                    "owner_identity_mismatch"
                ),
            }

        requested_step = connection.execute(
            """
            SELECT *
            FROM ob_owner_rehearsal_steps
            WHERE run_id = ?
              AND step_code = ?
            """,
            (
                str(
                    run_id
                ),
                normalized_step_code,
            ),
        ).fetchone()

        if requested_step is None:
            return {
                "ok": False,
                "advanced": False,
                "reason_code": (
                    "unknown_rehearsal_step"
                ),
            }

        if (
            requested_step[
                "state"
            ]
            == "completed"
        ):
            exact_retry = (
                requested_step[
                    "evidence_ref"
                ]
                == normalized_evidence_ref
                and requested_step[
                    "evidence_hash"
                ]
                == normalized_evidence_hash
            )

            if exact_retry:
                return {
                    "ok": True,
                    "advanced": False,
                    "idempotent": True,
                    "reason_code": (
                        "rehearsal_step_already_completed"
                    ),
                    "step": (
                        _public_step(
                            requested_step
                        )
                    ),
                    "run": (
                        get_owner_rehearsal_run(
                            run_id,
                            path=database,
                        )
                    ),
                    "production_authority_granted": False,
                }

            return {
                "ok": False,
                "advanced": False,
                "reason_code": (
                    "completed_step_evidence_conflict"
                ),
            }

        if run_row[
            "status"
        ] == "planned":
            return {
                "ok": False,
                "advanced": False,
                "reason_code": (
                    "owner_rehearsal_run_not_started"
                ),
            }

        if run_row[
            "status"
        ] == "on_hold":
            return {
                "ok": False,
                "advanced": False,
                "reason_code": (
                    "owner_rehearsal_run_on_hold"
                ),
            }

        if run_row[
            "status"
        ] == "completed":
            return {
                "ok": False,
                "advanced": False,
                "reason_code": (
                    "owner_rehearsal_run_completed"
                ),
            }

        if run_row[
            "status"
        ] != "active":
            return {
                "ok": False,
                "advanced": False,
                "reason_code": (
                    "owner_rehearsal_run_not_active"
                ),
            }

        current_step = connection.execute(
            """
            SELECT *
            FROM ob_owner_rehearsal_steps
            WHERE run_id = ?
              AND state = 'current'
            ORDER BY step_index ASC
            LIMIT 1
            """,
            (
                str(
                    run_id
                ),
            ),
        ).fetchone()

        if current_step is None:
            return {
                "ok": False,
                "advanced": False,
                "reason_code": (
                    "current_rehearsal_step_missing"
                ),
            }

        if (
            current_step[
                "step_code"
            ]
            != normalized_step_code
        ):
            return {
                "ok": False,
                "advanced": False,
                "reason_code": (
                    "rehearsal_step_out_of_order"
                ),
                "expected_step_code": current_step[
                    "step_code"
                ],
                "requested_step_code": (
                    normalized_step_code
                ),
            }

        completed_at = _iso(
            current_time
        )

        previous_step_hash = (
            _latest_completed_step_hash(
                connection,
                str(
                    run_id
                ),
            )
        )

        step_record = {
            "run_id": str(
                run_id
            ),
            "step_index": current_step[
                "step_index"
            ],
            "step_code": current_step[
                "step_code"
            ],
            "evidence_ref": (
                normalized_evidence_ref
            ),
            "evidence_hash": (
                normalized_evidence_hash
            ),
            "previous_step_hash": (
                previous_step_hash
            ),
            "completed_at": (
                completed_at
            ),
        }

        step_hash = _sha256_text(
            _canonical_json(
                _step_hash_material(
                    step_record
                )
            )
        )

        connection.execute(
            """
            UPDATE ob_owner_rehearsal_steps
            SET
                state = 'completed',
                evidence_ref = ?,
                evidence_hash = ?,
                previous_step_hash = ?,
                step_hash = ?,
                completed_at = ?
            WHERE run_id = ?
              AND step_index = ?
              AND state = 'current'
            """,
            (
                normalized_evidence_ref,
                normalized_evidence_hash,
                previous_step_hash,
                step_hash,
                completed_at,
                str(
                    run_id
                ),
                current_step[
                    "step_index"
                ],
            ),
        )

        next_step_index = (
            int(
                current_step[
                    "step_index"
                ]
            )
            + 1
        )

        completed_run = (
            next_step_index
            > int(
                run_row[
                    "step_count"
                ]
            )
        )

        if completed_run:
            connection.execute(
                """
                UPDATE ob_owner_rehearsal_runs
                SET
                    status = 'completed',
                    current_step_index = ?,
                    completed_at = ?,
                    hold_reason = NULL
                WHERE run_id = ?
                """,
                (
                    next_step_index,
                    completed_at,
                    str(
                        run_id
                    ),
                ),
            )

        else:
            connection.execute(
                """
                UPDATE ob_owner_rehearsal_steps
                SET state = 'current'
                WHERE run_id = ?
                  AND step_index = ?
                  AND state = 'pending'
                """,
                (
                    str(
                        run_id
                    ),
                    next_step_index,
                ),
            )

            connection.execute(
                """
                UPDATE ob_owner_rehearsal_runs
                SET current_step_index = ?
                WHERE run_id = ?
                """,
                (
                    next_step_index,
                    str(
                        run_id
                    ),
                ),
            )

        _append_event(
            connection,
            run_id=str(
                run_id
            ),
            event_type=(
                "rehearsal_step_completed"
            ),
            payload={
                "step_index": current_step[
                    "step_index"
                ],
                "step_code": current_step[
                    "step_code"
                ],
                "evidence_ref": (
                    normalized_evidence_ref
                ),
                "evidence_hash": (
                    normalized_evidence_hash
                ),
                "step_hash": (
                    step_hash
                ),
                "run_completed": (
                    completed_run
                ),
                "dry_run_only": True,
                "production_authority_granted": False,
            },
            created_at=(
                completed_at
            ),
        )

        if completed_run:
            _append_event(
                connection,
                run_id=str(
                    run_id
                ),
                event_type=(
                    "rehearsal_run_completed"
                ),
                payload={
                    "completed_at": (
                        completed_at
                    ),
                    "completed_step_count": (
                        run_row[
                            "step_count"
                        ]
                    ),
                    "tower_launch_authorized": False,
                    "production_authority_granted": False,
                },
                created_at=(
                    completed_at
                ),
            )

        connection.commit()

    return {
        "ok": True,
        "advanced": True,
        "idempotent": False,
        "reason_code": (
            "owner_rehearsal_step_completed"
        ),
        "completed_step_code": (
            normalized_step_code
        ),
        "run_completed": (
            completed_run
        ),
        "run": (
            get_owner_rehearsal_run(
                run_id,
                path=database,
            )
        ),
        "production_authority_granted": False,
    }


def hold_owner_rehearsal_run(
    run_id: str,
    *,
    owner_id: str,
    reason: str,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_rehearsal_database(
        database
    )

    hold_reason = str(
        reason
        or ""
    ).strip()

    if len(
        hold_reason
    ) < 3:
        return {
            "ok": False,
            "held": False,
            "reason_code": (
                "hold_reason_required"
            ),
        }

    current_time = _now(
        now
    )

    with _connect(
        database
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_owner_rehearsal_runs
            WHERE run_id = ?
            """,
            (
                str(
                    run_id
                ),
            ),
        ).fetchone()

        if row is None:
            return {
                "ok": False,
                "held": False,
                "reason_code": (
                    "owner_rehearsal_run_not_found"
                ),
            }

        if (
            str(
                owner_id
            )
            != str(
                row[
                    "owner_id"
                ]
            )
        ):
            return {
                "ok": False,
                "held": False,
                "reason_code": (
                    "owner_identity_mismatch"
                ),
            }

        if row[
            "status"
        ] == "on_hold":
            if (
                row[
                    "hold_reason"
                ]
                == hold_reason
            ):
                return {
                    "ok": True,
                    "held": True,
                    "idempotent": True,
                    "reason_code": (
                        "owner_rehearsal_run_already_on_hold"
                    ),
                    "run": (
                        get_owner_rehearsal_run(
                            run_id,
                            path=database,
                        )
                    ),
                }

            return {
                "ok": False,
                "held": False,
                "reason_code": (
                    "rehearsal_hold_reason_conflict"
                ),
            }

        if row[
            "status"
        ] != "active":
            return {
                "ok": False,
                "held": False,
                "reason_code": (
                    "owner_rehearsal_run_not_active"
                ),
                "status": row[
                    "status"
                ],
            }

        held_at = _iso(
            current_time
        )

        connection.execute(
            """
            UPDATE ob_owner_rehearsal_runs
            SET
                status = 'on_hold',
                hold_reason = ?
            WHERE run_id = ?
              AND status = 'active'
            """,
            (
                hold_reason,
                str(
                    run_id
                ),
            ),
        )

        _append_event(
            connection,
            run_id=str(
                run_id
            ),
            event_type=(
                "rehearsal_run_held"
            ),
            payload={
                "hold_reason": (
                    hold_reason
                ),
                "held_at": (
                    held_at
                ),
                "current_step_index": row[
                    "current_step_index"
                ],
                "production_authority_granted": False,
            },
            created_at=(
                held_at
            ),
        )

        connection.commit()

    return {
        "ok": True,
        "held": True,
        "idempotent": False,
        "reason_code": (
            "owner_rehearsal_run_held"
        ),
        "run": (
            get_owner_rehearsal_run(
                run_id,
                path=database,
            )
        ),
        "production_authority_granted": False,
    }


def resume_owner_rehearsal_run(
    run_id: str,
    *,
    owner_id: str,
    path: Optional[Any] = None,
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_rehearsal_database(
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
            FROM ob_owner_rehearsal_runs
            WHERE run_id = ?
            """,
            (
                str(
                    run_id
                ),
            ),
        ).fetchone()

        if row is None:
            return {
                "ok": False,
                "resumed": False,
                "reason_code": (
                    "owner_rehearsal_run_not_found"
                ),
            }

        if (
            str(
                owner_id
            )
            != str(
                row[
                    "owner_id"
                ]
            )
        ):
            return {
                "ok": False,
                "resumed": False,
                "reason_code": (
                    "owner_identity_mismatch"
                ),
            }

        if row[
            "status"
        ] == "active":
            return {
                "ok": True,
                "resumed": True,
                "idempotent": True,
                "reason_code": (
                    "owner_rehearsal_run_already_active"
                ),
                "run": (
                    get_owner_rehearsal_run(
                        run_id,
                        path=database,
                    )
                ),
            }

        if row[
            "status"
        ] != "on_hold":
            return {
                "ok": False,
                "resumed": False,
                "reason_code": (
                    "owner_rehearsal_run_not_on_hold"
                ),
                "status": row[
                    "status"
                ],
            }

        resumed_at = _iso(
            current_time
        )

        previous_hold_reason = row[
            "hold_reason"
        ]

        connection.execute(
            """
            UPDATE ob_owner_rehearsal_runs
            SET
                status = 'active',
                hold_reason = NULL
            WHERE run_id = ?
              AND status = 'on_hold'
            """,
            (
                str(
                    run_id
                ),
            ),
        )

        _append_event(
            connection,
            run_id=str(
                run_id
            ),
            event_type=(
                "rehearsal_run_resumed"
            ),
            payload={
                "resumed_at": (
                    resumed_at
                ),
                "previous_hold_reason": (
                    previous_hold_reason
                ),
                "current_step_index": row[
                    "current_step_index"
                ],
                "production_authority_granted": False,
            },
            created_at=(
                resumed_at
            ),
        )

        connection.commit()

    return {
        "ok": True,
        "resumed": True,
        "idempotent": False,
        "reason_code": (
            "owner_rehearsal_run_resumed"
        ),
        "run": (
            get_owner_rehearsal_run(
                run_id,
                path=database,
            )
        ),
        "production_authority_granted": False,
    }


def verify_owner_rehearsal_run(
    run_id: str,
    *,
    path: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_rehearsal_database(
        database
    )

    with _connect(
        database
    ) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ob_owner_rehearsal_runs
            WHERE run_id = ?
            """,
            (
                str(
                    run_id
                ),
            ),
        ).fetchone()

        if row is None:
            return {
                "verified": False,
                "reason_codes": [
                    "owner_rehearsal_run_not_found"
                ],
            }

        steps = connection.execute(
            """
            SELECT *
            FROM ob_owner_rehearsal_steps
            WHERE run_id = ?
            ORDER BY step_index ASC
            """,
            (
                str(
                    run_id
                ),
            ),
        ).fetchall()

        events = connection.execute(
            """
            SELECT *
            FROM ob_owner_rehearsal_events
            WHERE run_id = ?
            ORDER BY rowid ASC
            """,
            (
                str(
                    run_id
                ),
            ),
        ).fetchall()

        record = {
            "run_id": row[
                "run_id"
            ],
            "owner_id": row[
                "owner_id"
            ],
            "readiness_assessment_id": row[
                "readiness_assessment_id"
            ],
            "readiness_assessment_hash": row[
                "readiness_assessment_hash"
            ],
            "room_id": row[
                "room_id"
            ],
            "canonical_route": row[
                "canonical_route"
            ],
            "previous_manifest_hash": row[
                "previous_manifest_hash"
            ],
            "created_at": row[
                "created_at"
            ],
        }

        computed_manifest_hash = (
            _sha256_text(
                _canonical_json(
                    _manifest_hash_material(
                        record
                    )
                )
            )
        )

        checks = {
            "manifest_hash_matches": (
                hmac.compare_digest(
                    computed_manifest_hash,
                    str(
                        row[
                            "manifest_hash"
                        ]
                    ),
                )
            ),
            "previous_manifest_hash_valid": True,
            "readiness_assessment_exists": False,
            "readiness_assessment_hash_matches": False,
            "readiness_assessment_verified": False,
            "readiness_owner_matches": False,
            "readiness_passed": False,
            "room_registry_matches": False,
            "step_count_matches": (
                len(
                    steps
                )
                == len(
                    CANONICAL_REHEARSAL_STEPS
                )
                == int(
                    row[
                        "step_count"
                    ]
                )
            ),
            "step_definitions_match": True,
            "step_state_sequence_valid": True,
            "step_hash_chain_valid": True,
            "event_chain_valid": True,
            "run_status_valid": (
                row[
                    "status"
                ]
                in (
                    OPEN_RUN_STATES
                    | TERMINAL_RUN_STATES
                )
            ),
            "safety_boundary_preserved": True,
        }

        if (
            row[
                "previous_manifest_hash"
            ]
            != ZERO_HASH
        ):
            previous = connection.execute(
                """
                SELECT 1
                FROM ob_owner_rehearsal_runs
                WHERE manifest_hash = ?
                LIMIT 1
                """,
                (
                    row[
                        "previous_manifest_hash"
                    ],
                ),
            ).fetchone()

            checks[
                "previous_manifest_hash_valid"
            ] = previous is not None

        room = ROOM_REGISTRY.get(
            row[
                "room_id"
            ]
        )

        checks[
            "room_registry_matches"
        ] = bool(
            room
            and room[
                "canonical_route"
            ]
            == row[
                "canonical_route"
            ]
        )

        previous_step_hash = (
            ZERO_HASH
        )

        completed_count = 0
        current_count = 0

        for position, step in enumerate(
            steps,
            start=1,
        ):
            expected = (
                CANONICAL_REHEARSAL_STEPS[
                    position - 1
                ]
            )

            if (
                step[
                    "step_index"
                ]
                != expected[
                    "step_index"
                ]
                or step[
                    "step_code"
                ]
                != expected[
                    "step_code"
                ]
                or step[
                    "title"
                ]
                != expected[
                    "title"
                ]
            ):
                checks[
                    "step_definitions_match"
                ] = False

            if step[
                "state"
            ] == "completed":
                completed_count += 1

                if (
                    not step[
                        "evidence_ref"
                    ]
                    or not _valid_evidence_hash(
                        step[
                            "evidence_hash"
                        ]
                    )
                    or not step[
                        "completed_at"
                    ]
                    or not step[
                        "step_hash"
                    ]
                ):
                    checks[
                        "step_hash_chain_valid"
                    ] = False
                    continue

                step_record = {
                    "run_id": row[
                        "run_id"
                    ],
                    "step_index": step[
                        "step_index"
                    ],
                    "step_code": step[
                        "step_code"
                    ],
                    "evidence_ref": step[
                        "evidence_ref"
                    ],
                    "evidence_hash": step[
                        "evidence_hash"
                    ],
                    "previous_step_hash": step[
                        "previous_step_hash"
                    ],
                    "completed_at": step[
                        "completed_at"
                    ],
                }

                computed_step_hash = (
                    _sha256_text(
                        _canonical_json(
                            _step_hash_material(
                                step_record
                            )
                        )
                    )
                )

                if (
                    step[
                        "previous_step_hash"
                    ]
                    != previous_step_hash
                ):
                    checks[
                        "step_hash_chain_valid"
                    ] = False

                if not hmac.compare_digest(
                    computed_step_hash,
                    str(
                        step[
                            "step_hash"
                        ]
                    ),
                ):
                    checks[
                        "step_hash_chain_valid"
                    ] = False

                previous_step_hash = (
                    step[
                        "step_hash"
                    ]
                )

            elif step[
                "state"
            ] == "current":
                current_count += 1

                if any(
                    value is not None
                    for value in (
                        step[
                            "evidence_ref"
                        ],
                        step[
                            "evidence_hash"
                        ],
                        step[
                            "previous_step_hash"
                        ],
                        step[
                            "step_hash"
                        ],
                        step[
                            "completed_at"
                        ],
                    )
                ):
                    checks[
                        "step_state_sequence_valid"
                    ] = False

            elif step[
                "state"
            ] == "pending":
                if any(
                    value is not None
                    for value in (
                        step[
                            "evidence_ref"
                        ],
                        step[
                            "evidence_hash"
                        ],
                        step[
                            "previous_step_hash"
                        ],
                        step[
                            "step_hash"
                        ],
                        step[
                            "completed_at"
                        ],
                    )
                ):
                    checks[
                        "step_state_sequence_valid"
                    ] = False

            else:
                checks[
                    "step_state_sequence_valid"
                ] = False

        if row[
            "status"
        ] == "completed":
            if (
                completed_count
                != int(
                    row[
                        "step_count"
                    ]
                )
                or current_count != 0
                or row[
                    "completed_at"
                ]
                is None
                or int(
                    row[
                        "current_step_index"
                    ]
                )
                != int(
                    row[
                        "step_count"
                    ]
                )
                + 1
            ):
                checks[
                    "step_state_sequence_valid"
                ] = False

        else:
            expected_completed = (
                int(
                    row[
                        "current_step_index"
                    ]
                )
                - 1
            )

            if (
                completed_count
                != expected_completed
                or current_count != 1
                or row[
                    "completed_at"
                ]
                is not None
            ):
                checks[
                    "step_state_sequence_valid"
                ] = False

            for step in steps:
                if (
                    step[
                        "step_index"
                    ]
                    < row[
                        "current_step_index"
                    ]
                    and step[
                        "state"
                    ]
                    != "completed"
                ):
                    checks[
                        "step_state_sequence_valid"
                    ] = False

                if (
                    step[
                        "step_index"
                    ]
                    == row[
                        "current_step_index"
                    ]
                    and step[
                        "state"
                    ]
                    != "current"
                ):
                    checks[
                        "step_state_sequence_valid"
                    ] = False

                if (
                    step[
                        "step_index"
                    ]
                    > row[
                        "current_step_index"
                    ]
                    and step[
                        "state"
                    ]
                    != "pending"
                ):
                    checks[
                        "step_state_sequence_valid"
                    ] = False

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
                "run_id": event[
                    "run_id"
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

    assessment = (
        get_readiness_assessment(
            row[
                "readiness_assessment_id"
            ],
            path=database,
        )
    )

    checks[
        "readiness_assessment_exists"
    ] = assessment is not None

    checks[
        "readiness_assessment_hash_matches"
    ] = bool(
        assessment
        and hmac.compare_digest(
            str(
                row[
                    "readiness_assessment_hash"
                ]
            ),
            str(
                assessment[
                    "assessment_hash"
                ]
            ),
        )
    )

    assessment_verification = (
        verify_readiness_assessment(
            row[
                "readiness_assessment_id"
            ],
            path=database,
        )
    )

    checks[
        "readiness_assessment_verified"
    ] = bool(
        assessment_verification.get(
            "verified"
        )
    )

    checks[
        "readiness_owner_matches"
    ] = bool(
        assessment
        and assessment[
            "owner_id"
        ]
        == row[
            "owner_id"
        ]
    )

    checks[
        "readiness_passed"
    ] = bool(
        assessment
        and assessment[
            "local_readiness_passed"
        ]
        is True
        and assessment[
            "recommendation"
        ]
        == READY_RECOMMENDATION
    )

    return {
        "verified": all(
            checks.values()
        ),
        "checks": checks,
        "run_id": str(
            run_id
        ),
        "status": row[
            "status"
        ],
        "completed_step_count": (
            completed_count
        ),
        "step_count": row[
            "step_count"
        ],
        "event_count": len(
            events
        ),
        "manifest_hash": row[
            "manifest_hash"
        ],
        "dry_run_only": True,
        "tower_launch_authorized": False,
        "room_entry_authorized": False,
        "production_authority_granted": False,
    }


def owner_rehearsal_status(
    *,
    path: Optional[Any] = None,
) -> Dict[str, Any]:
    database = _database_path(
        path
    )

    init_rehearsal_database(
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
                        WHEN status = 'planned'
                        THEN 1 ELSE 0
                    END
                ) AS planned,
                SUM(
                    CASE
                        WHEN status = 'active'
                        THEN 1 ELSE 0
                    END
                ) AS active,
                SUM(
                    CASE
                        WHEN status = 'on_hold'
                        THEN 1 ELSE 0
                    END
                ) AS on_hold,
                SUM(
                    CASE
                        WHEN status = 'completed'
                        THEN 1 ELSE 0
                    END
                ) AS completed
            FROM ob_owner_rehearsal_runs
            """
        ).fetchone()

        event_total = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM ob_owner_rehearsal_events
            """
        ).fetchone()

    return {
        "ok": True,
        "pack": PACK,
        "contract_version": CONTRACT_VERSION,
        "database_path": str(
            database
        ),
        "run_total": int(
            totals[
                "total"
            ]
            or 0
        ),
        "run_planned": int(
            totals[
                "planned"
            ]
            or 0
        ),
        "run_active": int(
            totals[
                "active"
            ]
            or 0
        ),
        "run_on_hold": int(
            totals[
                "on_hold"
            ]
            or 0
        ),
        "run_completed": int(
            totals[
                "completed"
            ]
            or 0
        ),
        "event_total": int(
            event_total[
                "total"
            ]
            or 0
        ),
        "canonical_step_count": len(
            CANONICAL_REHEARSAL_STEPS
        ),
        "canonical_steps": (
            CANONICAL_REHEARSAL_STEPS
        ),
        "gp050_ready_assessment_required": True,
        "one_open_run_per_owner": True,
        "strict_step_order_required": True,
        "step_evidence_required": True,
        "dry_run_only": True,
        "tower_launch_authorized": False,
        "tower_identity_approved": False,
        "tower_clearance_approved": False,
        "tower_step_up_approved": False,
        "room_entry_authorized": False,
        "http_run_mutation_enabled": (
            os.environ.get(
                "OB_OWNER_REHEARSAL_HTTP_ENABLED",
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
