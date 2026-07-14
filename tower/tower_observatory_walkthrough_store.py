"""
Tower-owned durable storage for Observatory guided runs.

This ledger stores structured walkthrough state and receipts.
It is not Archive Vault and exposes no public file links.

Default path:
    /tmp/simplee_tower_ob_walkthrough.sqlite3

Production hosts should set:
    TOWER_OB_WALKTHROUGH_DB=/private/managed/path/file.sqlite3
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterator, List


DEFAULT_DATABASE_PATH = Path(
    "/tmp/simplee_tower_ob_walkthrough.sqlite3"
)

DATABASE_ENVIRONMENT_KEY = (
    "TOWER_OB_WALKTHROUGH_DB"
)

SCHEMA_VERSION = 1


def database_path(
    override: str | Path | None = None,
) -> Path:
    if override is not None:
        return Path(override)

    configured = os.environ.get(
        DATABASE_ENVIRONMENT_KEY
    )

    if configured:
        return Path(configured)

    return DEFAULT_DATABASE_PATH


def _canonical_json(
    payload: Dict[str, Any],
) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )


def payload_hash(
    payload: Dict[str, Any],
) -> str:
    return hashlib.sha256(
        _canonical_json(
            payload
        ).encode("utf-8")
    ).hexdigest()


@contextmanager
def connection(
    override: str | Path | None = None,
) -> Iterator[sqlite3.Connection]:
    path = database_path(
        override
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    database = sqlite3.connect(
        path
    )

    database.row_factory = (
        sqlite3.Row
    )

    try:
        database.execute(
            "PRAGMA foreign_keys = ON"
        )

        database.execute(
            "PRAGMA journal_mode = WAL"
        )

        initialize_schema(
            database
        )

        yield database

        database.commit()

    except Exception:
        database.rollback()
        raise

    finally:
        database.close()


def initialize_schema(
    database: sqlite3.Connection,
) -> None:
    database.executescript(
        """
        CREATE TABLE IF NOT EXISTS
        guided_runs (
            walkthrough_id TEXT PRIMARY KEY,
            owner_id TEXT NOT NULL,
            status TEXT NOT NULL,
            started_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            completed_at TEXT,
            completed_count INTEGER NOT NULL,
            total_room_count INTEGER NOT NULL,
            next_room_id TEXT,
            payload_json TEXT NOT NULL,
            payload_hash TEXT NOT NULL,
            schema_version INTEGER NOT NULL,
            preview_only INTEGER NOT NULL,
            contract_only INTEGER NOT NULL,
            writes_state INTEGER NOT NULL
        );

        CREATE INDEX IF NOT EXISTS
        idx_guided_runs_owner_updated
        ON guided_runs (
            owner_id,
            updated_at DESC
        );

        CREATE TABLE IF NOT EXISTS
        guided_room_receipts (
            room_completion_receipt_id TEXT PRIMARY KEY,
            walkthrough_id TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            room_id TEXT NOT NULL,
            position INTEGER NOT NULL,
            completed_at TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            payload_hash TEXT NOT NULL,
            schema_version INTEGER NOT NULL,
            FOREIGN KEY (
                walkthrough_id
            )
            REFERENCES guided_runs (
                walkthrough_id
            )
            ON DELETE CASCADE
        );

        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_room_receipt_run_room
        ON guided_room_receipts (
            walkthrough_id,
            room_id
        );

        CREATE TABLE IF NOT EXISTS
        guided_final_receipts (
            final_completion_receipt_id
                TEXT PRIMARY KEY,
            walkthrough_id TEXT NOT NULL UNIQUE,
            owner_id TEXT NOT NULL,
            completed_at TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            payload_hash TEXT NOT NULL,
            schema_version INTEGER NOT NULL,
            FOREIGN KEY (
                walkthrough_id
            )
            REFERENCES guided_runs (
                walkthrough_id
            )
            ON DELETE CASCADE
        );
        """
    )


def save_guided_progress(
    *,
    owner_id: str,
    progress: Dict[str, Any],
    override: str | Path | None = None,
) -> Dict[str, Any]:
    if not owner_id:
        raise ValueError(
            "owner_id is required"
        )

    walkthrough_id = str(
        progress.get(
            "walkthrough_id",
            "",
        )
    ).strip()

    if not walkthrough_id:
        raise ValueError(
            "walkthrough_id is required"
        )

    status = str(
        progress.get(
            "status",
            "in_progress",
        )
    )

    completed_at = None

    final_receipt = progress.get(
        "final_receipt"
    )

    if isinstance(
        final_receipt,
        dict,
    ):
        completed_at = (
            final_receipt.get(
                "completed_at"
            )
        )

    payload = deepcopy(
        progress
    )

    encoded = _canonical_json(
        payload
    )

    integrity = payload_hash(
        payload
    )

    with connection(
        override
    ) as database:
        database.execute(
            """
            INSERT INTO guided_runs (
                walkthrough_id,
                owner_id,
                status,
                started_at,
                updated_at,
                completed_at,
                completed_count,
                total_room_count,
                next_room_id,
                payload_json,
                payload_hash,
                schema_version,
                preview_only,
                contract_only,
                writes_state
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            ON CONFLICT (
                walkthrough_id
            )
            DO UPDATE SET
                owner_id = excluded.owner_id,
                status = excluded.status,
                updated_at = excluded.updated_at,
                completed_at = excluded.completed_at,
                completed_count = excluded.completed_count,
                total_room_count = excluded.total_room_count,
                next_room_id = excluded.next_room_id,
                payload_json = excluded.payload_json,
                payload_hash = excluded.payload_hash,
                schema_version = excluded.schema_version,
                preview_only = excluded.preview_only,
                contract_only = excluded.contract_only,
                writes_state = excluded.writes_state
            """,
            (
                walkthrough_id,
                owner_id,
                status,
                progress.get(
                    "started_at"
                ),
                progress.get(
                    "updated_at"
                ),
                completed_at,
                int(
                    progress.get(
                        "completed_count",
                        0,
                    )
                ),
                int(
                    progress.get(
                        "total_room_count",
                        6,
                    )
                ),
                progress.get(
                    "next_room_id"
                ),
                encoded,
                integrity,
                SCHEMA_VERSION,
                int(
                    bool(
                        progress.get(
                            "preview_only",
                            True,
                        )
                    )
                ),
                int(
                    bool(
                        progress.get(
                            "contract_only",
                            True,
                        )
                    )
                ),
                int(
                    bool(
                        progress.get(
                            "writes_state",
                            False,
                        )
                    )
                ),
            ),
        )

        room_receipts = (
            progress.get(
                "room_receipts",
                {}
            )
        )

        if isinstance(
            room_receipts,
            dict,
        ):
            for receipt in (
                room_receipts.values()
            ):
                if not isinstance(
                    receipt,
                    dict,
                ):
                    continue

                save_room_receipt(
                    database=database,
                    owner_id=owner_id,
                    walkthrough_id=walkthrough_id,
                    receipt=receipt,
                )

        if isinstance(
            final_receipt,
            dict,
        ):
            save_final_receipt(
                database=database,
                owner_id=owner_id,
                walkthrough_id=walkthrough_id,
                receipt=final_receipt,
            )

    return {
        "saved": True,
        "walkthrough_id": walkthrough_id,
        "owner_id": owner_id,
        "status": status,
        "payload_hash": integrity,
        "schema_version": SCHEMA_VERSION,
    }


def save_room_receipt(
    *,
    database: sqlite3.Connection,
    owner_id: str,
    walkthrough_id: str,
    receipt: Dict[str, Any],
) -> None:
    receipt_id = str(
        receipt.get(
            "room_completion_receipt_id",
            "",
        )
    ).strip()

    if not receipt_id:
        raise ValueError(
            "room completion receipt ID is required"
        )

    payload = deepcopy(
        receipt
    )

    encoded = _canonical_json(
        payload
    )

    integrity = payload_hash(
        payload
    )

    database.execute(
        """
        INSERT INTO guided_room_receipts (
            room_completion_receipt_id,
            walkthrough_id,
            owner_id,
            room_id,
            position,
            completed_at,
            payload_json,
            payload_hash,
            schema_version
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (
            room_completion_receipt_id
        )
        DO UPDATE SET
            payload_json = excluded.payload_json,
            payload_hash = excluded.payload_hash,
            schema_version = excluded.schema_version
        """,
        (
            receipt_id,
            walkthrough_id,
            owner_id,
            receipt.get(
                "room_id"
            ),
            int(
                receipt.get(
                    "position",
                    0,
                )
            ),
            receipt.get(
                "completed_at"
            ),
            encoded,
            integrity,
            SCHEMA_VERSION,
        ),
    )


def save_final_receipt(
    *,
    database: sqlite3.Connection,
    owner_id: str,
    walkthrough_id: str,
    receipt: Dict[str, Any],
) -> None:
    receipt_id = str(
        receipt.get(
            "final_completion_receipt_id",
            "",
        )
    ).strip()

    if not receipt_id:
        raise ValueError(
            "final completion receipt ID is required"
        )

    payload = deepcopy(
        receipt
    )

    encoded = _canonical_json(
        payload
    )

    integrity = payload_hash(
        payload
    )

    database.execute(
        """
        INSERT INTO guided_final_receipts (
            final_completion_receipt_id,
            walkthrough_id,
            owner_id,
            completed_at,
            payload_json,
            payload_hash,
            schema_version
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (
            final_completion_receipt_id
        )
        DO UPDATE SET
            payload_json = excluded.payload_json,
            payload_hash = excluded.payload_hash,
            schema_version = excluded.schema_version
        """,
        (
            receipt_id,
            walkthrough_id,
            owner_id,
            receipt.get(
                "completed_at"
            ),
            encoded,
            integrity,
            SCHEMA_VERSION,
        ),
    )


def load_guided_run(
    *,
    owner_id: str,
    walkthrough_id: str,
    override: str | Path | None = None,
) -> Dict[str, Any] | None:
    with connection(
        override
    ) as database:
        row = database.execute(
            """
            SELECT *
            FROM guided_runs
            WHERE owner_id = ?
              AND walkthrough_id = ?
            """,
            (
                owner_id,
                walkthrough_id,
            ),
        ).fetchone()

    if row is None:
        return None

    payload = json.loads(
        row["payload_json"]
    )

    return {
        "walkthrough_id": row[
            "walkthrough_id"
        ],
        "owner_id": row[
            "owner_id"
        ],
        "status": row["status"],
        "started_at": row[
            "started_at"
        ],
        "updated_at": row[
            "updated_at"
        ],
        "completed_at": row[
            "completed_at"
        ],
        "completed_count": row[
            "completed_count"
        ],
        "total_room_count": row[
            "total_room_count"
        ],
        "next_room_id": row[
            "next_room_id"
        ],
        "payload": payload,
        "stored_payload_hash": row[
            "payload_hash"
        ],
        "calculated_payload_hash": (
            payload_hash(
                payload
            )
        ),
        "integrity_valid": (
            payload_hash(
                payload
            )
            == row["payload_hash"]
        ),
        "schema_version": row[
            "schema_version"
        ],
    }


def list_owner_runs(
    *,
    owner_id: str,
    limit: int = 50,
    override: str | Path | None = None,
) -> List[Dict[str, Any]]:
    safe_limit = max(
        1,
        min(
            int(limit),
            200,
        ),
    )

    with connection(
        override
    ) as database:
        rows = database.execute(
            """
            SELECT
                walkthrough_id,
                owner_id,
                status,
                started_at,
                updated_at,
                completed_at,
                completed_count,
                total_room_count,
                next_room_id,
                payload_hash,
                schema_version
            FROM guided_runs
            WHERE owner_id = ?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (
                owner_id,
                safe_limit,
            ),
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def load_run_evidence(
    *,
    owner_id: str,
    walkthrough_id: str,
    override: str | Path | None = None,
) -> Dict[str, Any] | None:
    run = load_guided_run(
        owner_id=owner_id,
        walkthrough_id=walkthrough_id,
        override=override,
    )

    if run is None:
        return None

    with connection(
        override
    ) as database:
        room_rows = database.execute(
            """
            SELECT *
            FROM guided_room_receipts
            WHERE owner_id = ?
              AND walkthrough_id = ?
            ORDER BY position ASC
            """,
            (
                owner_id,
                walkthrough_id,
            ),
        ).fetchall()

        final_row = database.execute(
            """
            SELECT *
            FROM guided_final_receipts
            WHERE owner_id = ?
              AND walkthrough_id = ?
            """,
            (
                owner_id,
                walkthrough_id,
            ),
        ).fetchone()

    room_receipts = []

    for row in room_rows:
        payload = json.loads(
            row["payload_json"]
        )

        room_receipts.append({
            "receipt_id": row[
                "room_completion_receipt_id"
            ],
            "room_id": row[
                "room_id"
            ],
            "position": row[
                "position"
            ],
            "completed_at": row[
                "completed_at"
            ],
            "payload": payload,
            "stored_payload_hash": row[
                "payload_hash"
            ],
            "integrity_valid": (
                payload_hash(
                    payload
                )
                == row["payload_hash"]
            ),
        })

    final_receipt = None

    if final_row is not None:
        payload = json.loads(
            final_row["payload_json"]
        )

        final_receipt = {
            "receipt_id": final_row[
                "final_completion_receipt_id"
            ],
            "completed_at": final_row[
                "completed_at"
            ],
            "payload": payload,
            "stored_payload_hash": final_row[
                "payload_hash"
            ],
            "integrity_valid": (
                payload_hash(
                    payload
                )
                == final_row[
                    "payload_hash"
                ]
            ),
        }

    return {
        "run": run,
        "room_receipts": room_receipts,
        "final_receipt": final_receipt,
        "integrity_valid": all([
            run["integrity_valid"],
            all(
                receipt[
                    "integrity_valid"
                ]
                for receipt in room_receipts
            ),
            (
                final_receipt is None
                or final_receipt[
                    "integrity_valid"
                ]
            ),
        ]),
        "preview_only": True,
        "vault_write_performed": False,
    }


def verify_owner_run(
    *,
    owner_id: str,
    walkthrough_id: str,
    override: str | Path | None = None,
) -> Dict[str, Any]:
    evidence = load_run_evidence(
        owner_id=owner_id,
        walkthrough_id=walkthrough_id,
        override=override,
    )

    if evidence is None:
        return {
            "verified": False,
            "reason_code": (
                "tower_ob_guided_run_not_found"
            ),
        }

    room_receipts = evidence[
        "room_receipts"
    ]

    run_status = evidence[
        "run"
    ]["status"]

    completed_run = (
        run_status == "completed"
    )

    expected_room_receipts = (
        6 if completed_run else len(
            room_receipts
        )
    )

    verified = all([
        evidence["integrity_valid"],
        len(room_receipts)
        == expected_room_receipts,
        (
            not completed_run
            or evidence[
                "final_receipt"
            ]
            is not None
        ),
    ])

    return {
        "verified": verified,
        "reason_code": (
            "tower_ob_guided_run_verified"
            if verified
            else (
                "tower_ob_guided_run_"
                "integrity_or_completeness_failed"
            )
        ),
        "walkthrough_id": walkthrough_id,
        "status": run_status,
        "room_receipt_count": len(
            room_receipts
        ),
        "final_receipt_present": (
            evidence[
                "final_receipt"
            ]
            is not None
        ),
        "preview_only": True,
        "vault_write_performed": False,
    }
