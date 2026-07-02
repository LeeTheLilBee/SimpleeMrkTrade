"""
VAULT GIANT PACK 060 — Storage Provider Prep Readiness Checkpoint

CURRENT SECTION:
Archive Vault — Storage Provider Prep Layer
GP051-GP060

This pack closes GP051-GP060 with a real durable SQLite-backed readiness
checkpoint.

Purpose:
- Create a real storage provider prep readiness checkpoint schema.
- Persist a real readiness checkpoint sourced from GP059.
- Persist real readiness component rows for GP055-GP059.
- Persist real blocker rows sourced from GP059 receipt lines.
- Persist a real section-close event log.
- Validate that the prep layer is complete while provider activation remains locked.
- Produce a real GP061 handoff contract.

Important truth:
- GP060 marks the Storage Provider Prep Layer complete.
- GP060 does not mean Vault is done.
- GP060 does not approve, activate, recommend, select, or configure a provider.
- GP060 does not enable provider read/write.
- GP060 does not make a storage receipt official/final/closed.
- GP060 does not unlock object bodies, upload, export, or execution.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Dict, Optional

from vault.real_provider_selection_review_receipt_service import (
    DEFAULT_REVIEW_RECEIPT_ID,
    get_provider_selection_review_receipt_lines,
    get_provider_selection_review_receipt_record,
)


PACK_ID = "VAULT_GP060"
PACK_NAME = "Storage Provider Prep Readiness Checkpoint"
SCHEMA_VERSION = "vault.storage_provider_prep_readiness_checkpoint.v1"

SECTION_ID = "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
SECTION_TITLE = "Archive Vault — Storage Provider Prep Layer"
SECTION_RANGE = "GP051-GP060"

NEXT_SECTION_ID = "ARCHIVE_VAULT_REAL_STORAGE_PROVIDER_CONFIGURATION_LAYER"
NEXT_SECTION_TITLE = "Archive Vault — Real Storage Provider Configuration Layer"
NEXT_SECTION_RANGE = "GP061-GP070"
NEXT_PACK = "VAULT_GP061_REAL_STORAGE_PROVIDER_CONFIG_CONTRACT"
NEXT_PACK_TITLE = "Real Storage Provider Config Contract"

DEFAULT_READINESS_CHECKPOINT_ID = "VSPPRC-GP060-001"
DEFAULT_DB_ENV = "VAULT_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_DB"
DEFAULT_DB_PATH = "data/vault_storage_provider_prep_readiness_checkpoint.sqlite"


COMPONENT_SPECS = [
    {
        "component_code": "gp055_real_provider_decision_record",
        "component_name": "GP055 real provider decision record",
        "source_pack_id": "VAULT_GP055",
        "source_artifact": "real_sqlite_decision_record",
    },
    {
        "component_code": "gp056_real_provider_selection_registry",
        "component_name": "GP056 real provider selection registry",
        "source_pack_id": "VAULT_GP056",
        "source_artifact": "real_sqlite_selection_registry",
    },
    {
        "component_code": "gp057_real_provider_capability_contract",
        "component_name": "GP057 real provider capability contract",
        "source_pack_id": "VAULT_GP057",
        "source_artifact": "real_sqlite_capability_contract",
    },
    {
        "component_code": "gp058_real_provider_risk_criteria_validation_engine",
        "component_name": "GP058 real provider risk / criteria validation engine",
        "source_pack_id": "VAULT_GP058",
        "source_artifact": "real_sqlite_validation_engine",
    },
    {
        "component_code": "gp059_real_provider_selection_review_receipt",
        "component_name": "GP059 real provider selection review receipt",
        "source_pack_id": "VAULT_GP059",
        "source_artifact": "real_sqlite_review_receipt",
    },
    {
        "component_code": "real_persistence_chain_ready",
        "component_name": "Real persistence chain ready",
        "source_pack_id": "VAULT_GP055_GP059",
        "source_artifact": "sqlite_backed_prep_stack",
    },
    {
        "component_code": "real_blocker_chain_preserved",
        "component_name": "Real blocker chain preserved",
        "source_pack_id": "VAULT_GP058_GP059",
        "source_artifact": "active_blocker_rollups",
    },
    {
        "component_code": "tower_locks_preserved",
        "component_name": "Tower locks preserved",
        "source_pack_id": "VAULT_GP051_GP060",
        "source_artifact": "tower_locked_provider_prep",
    },
    {
        "component_code": "section_close_readiness_ready",
        "component_name": "Section close readiness ready",
        "source_pack_id": "VAULT_GP060",
        "source_artifact": "real_section_checkpoint",
    },
    {
        "component_code": "gp061_handoff_ready",
        "component_name": "GP061 handoff ready",
        "source_pack_id": "VAULT_GP060",
        "source_artifact": "real_configuration_layer_handoff",
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_db_path(db_path: Optional[str] = None) -> Path:
    chosen = db_path or os.environ.get(DEFAULT_DB_ENV) or DEFAULT_DB_PATH
    return Path(chosen)


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _json_loads(value: str) -> Any:
    return json.loads(value)


def _connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = _resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_storage_provider_prep_readiness_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_prep_readiness_checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_review_receipt_id TEXT NOT NULL,
                source_review_receipt_pack_id TEXT NOT NULL,
                checkpoint_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                readiness_data_json TEXT NOT NULL,
                prep_layer_complete INTEGER NOT NULL DEFAULT 1,
                readiness_score INTEGER NOT NULL DEFAULT 100,
                safe_to_continue_to_gp061 INTEGER NOT NULL DEFAULT 1,
                provider_approval_ready INTEGER NOT NULL DEFAULT 0,
                provider_activation_ready INTEGER NOT NULL DEFAULT 0,
                provider_configuration_ready INTEGER NOT NULL DEFAULT 0,
                provider_read_write_ready INTEGER NOT NULL DEFAULT 0,
                provider_approved INTEGER NOT NULL DEFAULT 0,
                provider_activated INTEGER NOT NULL DEFAULT 0,
                provider_recommended INTEGER NOT NULL DEFAULT 0,
                provider_selected INTEGER NOT NULL DEFAULT 0,
                provider_configured INTEGER NOT NULL DEFAULT 0,
                provider_read_enabled INTEGER NOT NULL DEFAULT 0,
                provider_write_enabled INTEGER NOT NULL DEFAULT 0,
                provider_object_read_claimed INTEGER NOT NULL DEFAULT 0,
                provider_connection_tested INTEGER NOT NULL DEFAULT 0,
                risk_accepted INTEGER NOT NULL DEFAULT 0,
                risk_waived INTEGER NOT NULL DEFAULT 0,
                mitigation_approved INTEGER NOT NULL DEFAULT 0,
                official_storage_receipt INTEGER NOT NULL DEFAULT 0,
                finalized_storage_receipt INTEGER NOT NULL DEFAULT 0,
                closed_storage_receipt INTEGER NOT NULL DEFAULT 0,
                object_body_view_enabled INTEGER NOT NULL DEFAULT 0,
                direct_upload_enabled INTEGER NOT NULL DEFAULT 0,
                export_enabled INTEGER NOT NULL DEFAULT 0,
                execution_enabled INTEGER NOT NULL DEFAULT 0,
                vault_done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_prep_readiness_components (
                component_id TEXT PRIMARY KEY,
                checkpoint_id TEXT NOT NULL,
                component_code TEXT NOT NULL,
                component_name TEXT NOT NULL,
                source_pack_id TEXT NOT NULL,
                source_artifact TEXT NOT NULL,
                component_status TEXT NOT NULL,
                real_sqlite_backed INTEGER NOT NULL DEFAULT 1,
                component_ready INTEGER NOT NULL DEFAULT 1,
                tower_locked INTEGER NOT NULL DEFAULT 1,
                provider_approval_unlocked INTEGER NOT NULL DEFAULT 0,
                provider_activation_unlocked INTEGER NOT NULL DEFAULT 0,
                export_unlocked INTEGER NOT NULL DEFAULT 0,
                execution_unlocked INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(checkpoint_id)
                    REFERENCES vault_storage_provider_prep_readiness_checkpoints(checkpoint_id)
                    ON DELETE CASCADE,
                UNIQUE(checkpoint_id, component_code)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_prep_readiness_blockers (
                blocker_id TEXT PRIMARY KEY,
                checkpoint_id TEXT NOT NULL,
                source_receipt_line_id TEXT NOT NULL,
                source_finding_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                blocker_category TEXT NOT NULL,
                blocker_code TEXT NOT NULL,
                blocker_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                blocker_status TEXT NOT NULL,
                blocks_provider_approval INTEGER NOT NULL DEFAULT 1,
                blocks_provider_activation INTEGER NOT NULL DEFAULT 1,
                blocks_provider_selection INTEGER NOT NULL DEFAULT 1,
                blocks_provider_configuration INTEGER NOT NULL DEFAULT 1,
                blocks_provider_read_write INTEGER NOT NULL DEFAULT 1,
                blocks_object_body_view INTEGER NOT NULL DEFAULT 1,
                blocks_export INTEGER NOT NULL DEFAULT 1,
                blocks_execution INTEGER NOT NULL DEFAULT 1,
                tower_review_required INTEGER NOT NULL DEFAULT 1,
                tower_review_granted INTEGER NOT NULL DEFAULT 0,
                risk_accepted INTEGER NOT NULL DEFAULT 0,
                risk_waived INTEGER NOT NULL DEFAULT 0,
                mitigation_approved INTEGER NOT NULL DEFAULT 0,
                resolved INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(checkpoint_id)
                    REFERENCES vault_storage_provider_prep_readiness_checkpoints(checkpoint_id)
                    ON DELETE CASCADE,
                UNIQUE(checkpoint_id, source_receipt_line_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_storage_provider_prep_readiness_events (
                event_id TEXT PRIMARY KEY,
                checkpoint_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(checkpoint_id)
                    REFERENCES vault_storage_provider_prep_readiness_checkpoints(checkpoint_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_prep_components_checkpoint
            ON vault_storage_provider_prep_readiness_components(checkpoint_id, component_code)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_prep_blockers_checkpoint
            ON vault_storage_provider_prep_readiness_blockers(checkpoint_id, provider_candidate_id, blocker_category)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_prep_events_checkpoint
            ON vault_storage_provider_prep_readiness_events(checkpoint_id, created_at)
            """
        )
        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "tables": [
            "vault_storage_provider_prep_readiness_checkpoints",
            "vault_storage_provider_prep_readiness_components",
            "vault_storage_provider_prep_readiness_blockers",
            "vault_storage_provider_prep_readiness_events",
        ],
        "real_sqlite_backed": True,
    }


def initialize_storage_provider_prep_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_storage_provider_prep_readiness_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            """
            SELECT checkpoint_id
            FROM vault_storage_provider_prep_readiness_checkpoints
            WHERE checkpoint_id = ?
            """,
            (DEFAULT_READINESS_CHECKPOINT_ID,),
        ).fetchone()

        if existing is None:
            receipt = get_provider_selection_review_receipt_record()["receipt"]
            receipt_lines_payload = get_provider_selection_review_receipt_lines()
            receipt_lines = receipt_lines_payload["lines"]
            readiness_data = _build_readiness_data(receipt, receipt_lines_payload)
            now = _now_iso()

            conn.execute(
                """
                INSERT INTO vault_storage_provider_prep_readiness_checkpoints (
                    checkpoint_id,
                    pack_id,
                    section_id,
                    section_range,
                    source_review_receipt_id,
                    source_review_receipt_pack_id,
                    checkpoint_status,
                    tower_authority_status,
                    readiness_data_json,
                    prep_layer_complete,
                    readiness_score,
                    safe_to_continue_to_gp061,
                    provider_approval_ready,
                    provider_activation_ready,
                    provider_configuration_ready,
                    provider_read_write_ready,
                    provider_approved,
                    provider_activated,
                    provider_recommended,
                    provider_selected,
                    provider_configured,
                    provider_read_enabled,
                    provider_write_enabled,
                    provider_object_read_claimed,
                    provider_connection_tested,
                    risk_accepted,
                    risk_waived,
                    mitigation_approved,
                    official_storage_receipt,
                    finalized_storage_receipt,
                    closed_storage_receipt,
                    object_body_view_enabled,
                    direct_upload_enabled,
                    export_enabled,
                    execution_enabled,
                    vault_done,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    DEFAULT_READINESS_CHECKPOINT_ID,
                    PACK_ID,
                    SECTION_ID,
                    SECTION_RANGE,
                    receipt["receipt_id"],
                    receipt["pack_id"],
                    "REAL_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_COMPLETE_LOCKED",
                    "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    _json_dumps(readiness_data),
                    1,
                    100,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    now,
                    now,
                ),
            )

            for component in COMPONENT_SPECS:
                _insert_component(conn, DEFAULT_READINESS_CHECKPOINT_ID, component, now)

            for line in receipt_lines:
                _insert_blocker(conn, DEFAULT_READINESS_CHECKPOINT_ID, line, now)

            component_counts = _get_component_counts(conn, DEFAULT_READINESS_CHECKPOINT_ID)
            blocker_counts = _get_blocker_counts(conn, DEFAULT_READINESS_CHECKPOINT_ID)

            _insert_event(
                conn,
                DEFAULT_READINESS_CHECKPOINT_ID,
                "REAL_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_CREATED",
                {
                    "pack_id": PACK_ID,
                    "source_review_receipt_id": receipt["receipt_id"],
                    "source_review_receipt_pack_id": receipt["pack_id"],
                    "real_sqlite_backed": True,
                    "checkpoint_status": "REAL_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_COMPLETE_LOCKED",
                    "prep_layer_complete": True,
                    "readiness_score": 100,
                    "safe_to_continue_to_gp061": True,
                    "provider_approval_ready": False,
                    "provider_activation_ready": False,
                    "provider_read_write_ready": False,
                    "vault_done": False,
                },
            )
            _insert_event(
                conn,
                DEFAULT_READINESS_CHECKPOINT_ID,
                "SOURCE_GP059_REVIEW_RECEIPT_ATTACHED",
                _compact_receipt_source_snapshot(receipt, receipt_lines_payload),
            )
            _insert_event(
                conn,
                DEFAULT_READINESS_CHECKPOINT_ID,
                "REAL_READINESS_COMPONENTS_CREATED",
                component_counts,
            )
            _insert_event(
                conn,
                DEFAULT_READINESS_CHECKPOINT_ID,
                "REAL_READINESS_BLOCKERS_CARRIED_FORWARD",
                blocker_counts,
            )
            _insert_event(
                conn,
                DEFAULT_READINESS_CHECKPOINT_ID,
                "SECTION_GP051_GP060_CLOSED_FOR_PREP_ONLY",
                {
                    "section_id": SECTION_ID,
                    "section_range": SECTION_RANGE,
                    "prep_layer_complete": True,
                    "next_section": NEXT_SECTION_ID,
                    "next_section_range": NEXT_SECTION_RANGE,
                    "next_pack": NEXT_PACK,
                    "provider_approval_blocked": True,
                    "provider_activation_blocked": True,
                    "export_blocked": True,
                    "execution_blocked": True,
                    "vault_done": False,
                },
            )
            conn.commit()

    counts = _get_counts(path)
    return {
        "initialized": True,
        "schema": schema,
        "checkpoint_id": DEFAULT_READINESS_CHECKPOINT_ID,
        "checkpoint_count": counts["checkpoint_count"],
        "component_count": counts["component_count"],
        "blocker_count": counts["blocker_count"],
        "event_count": counts["event_count"],
        "real_sqlite_backed": True,
    }


def _insert_component(
    conn: sqlite3.Connection,
    checkpoint_id: str,
    component: Dict[str, Any],
    now: str,
) -> str:
    component_id = f"VSPPC-{component['component_code'].upper().replace('_', '-')}"
    conn.execute(
        """
        INSERT INTO vault_storage_provider_prep_readiness_components (
            component_id,
            checkpoint_id,
            component_code,
            component_name,
            source_pack_id,
            source_artifact,
            component_status,
            real_sqlite_backed,
            component_ready,
            tower_locked,
            provider_approval_unlocked,
            provider_activation_unlocked,
            export_unlocked,
            execution_unlocked,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            component_id,
            checkpoint_id,
            component["component_code"],
            component["component_name"],
            component["source_pack_id"],
            component["source_artifact"],
            "REAL_COMPONENT_READY_FOR_PREP_SECTION_CLOSE_TOWER_LOCKED",
            1,
            1,
            1,
            0,
            0,
            0,
            0,
            now,
            now,
        ),
    )
    return component_id


def _insert_blocker(
    conn: sqlite3.Connection,
    checkpoint_id: str,
    line: Dict[str, Any],
    now: str,
) -> str:
    blocker_id = f"VSPPB-{line['receipt_line_id'].replace('VSPRL-', '')}"
    conn.execute(
        """
        INSERT INTO vault_storage_provider_prep_readiness_blockers (
            blocker_id,
            checkpoint_id,
            source_receipt_line_id,
            source_finding_id,
            provider_candidate_id,
            blocker_category,
            blocker_code,
            blocker_name,
            severity,
            blocker_status,
            blocks_provider_approval,
            blocks_provider_activation,
            blocks_provider_selection,
            blocks_provider_configuration,
            blocks_provider_read_write,
            blocks_object_body_view,
            blocks_export,
            blocks_execution,
            tower_review_required,
            tower_review_granted,
            risk_accepted,
            risk_waived,
            mitigation_approved,
            resolved,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            blocker_id,
            checkpoint_id,
            line["receipt_line_id"],
            line["source_finding_id"],
            line["provider_candidate_id"],
            line["line_category"],
            line["line_code"],
            line["line_name"],
            line["severity"],
            "REAL_PREP_READINESS_BLOCKER_ACTIVE_CARRIED_FROM_GP059",
            1 if line["blocks_provider_approval"] else 0,
            1 if line["blocks_provider_activation"] else 0,
            1 if line["blocks_provider_selection"] else 0,
            1 if line["blocks_provider_configuration"] else 0,
            1 if line["blocks_provider_read_write"] else 0,
            1 if line["blocks_object_body_view"] else 0,
            1 if line["blocks_export"] else 0,
            1 if line["blocks_execution"] else 0,
            1 if line["tower_review_required"] else 0,
            1 if line["tower_review_granted"] else 0,
            1 if line["risk_accepted"] else 0,
            1 if line["risk_waived"] else 0,
            1 if line["mitigation_approved"] else 0,
            1 if line["resolved"] else 0,
            now,
            now,
        ),
    )
    return blocker_id


def _insert_event(
    conn: sqlite3.Connection,
    checkpoint_id: str,
    event_type: str,
    event_payload: Dict[str, Any],
) -> str:
    event_id = f"VSPPE-{uuid.uuid4().hex[:16].upper()}"
    conn.execute(
        """
        INSERT INTO vault_storage_provider_prep_readiness_events (
            event_id,
            checkpoint_id,
            event_type,
            event_payload_json,
            created_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            event_id,
            checkpoint_id,
            event_type,
            _json_dumps(event_payload),
            _now_iso(),
        ),
    )
    return event_id


def _get_counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        checkpoint_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_prep_readiness_checkpoints"
        ).fetchone()["c"]
        component_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_prep_readiness_components"
        ).fetchone()["c"]
        blocker_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_prep_readiness_blockers"
        ).fetchone()["c"]
        event_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_storage_provider_prep_readiness_events"
        ).fetchone()["c"]

    return {
        "checkpoint_count": int(checkpoint_count),
        "component_count": int(component_count),
        "blocker_count": int(blocker_count),
        "event_count": int(event_count),
    }


def _get_component_counts(conn: sqlite3.Connection, checkpoint_id: str) -> Dict[str, int]:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS component_count,
            SUM(CASE WHEN real_sqlite_backed = 1 THEN 1 ELSE 0 END) AS real_sqlite_backed_count,
            SUM(CASE WHEN component_ready = 1 THEN 1 ELSE 0 END) AS component_ready_count,
            SUM(CASE WHEN tower_locked = 1 THEN 1 ELSE 0 END) AS tower_locked_count,
            SUM(CASE WHEN provider_approval_unlocked = 1 THEN 1 ELSE 0 END) AS provider_approval_unlocked_count,
            SUM(CASE WHEN provider_activation_unlocked = 1 THEN 1 ELSE 0 END) AS provider_activation_unlocked_count,
            SUM(CASE WHEN export_unlocked = 1 THEN 1 ELSE 0 END) AS export_unlocked_count,
            SUM(CASE WHEN execution_unlocked = 1 THEN 1 ELSE 0 END) AS execution_unlocked_count
        FROM vault_storage_provider_prep_readiness_components
        WHERE checkpoint_id = ?
        """,
        (checkpoint_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _get_blocker_counts(conn: sqlite3.Connection, checkpoint_id: str) -> Dict[str, int]:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS blocker_count,
            SUM(CASE WHEN blocker_category = 'capability_contract' THEN 1 ELSE 0 END) AS capability_blocker_count,
            SUM(CASE WHEN blocker_category = 'criteria_validation' THEN 1 ELSE 0 END) AS criteria_blocker_count,
            SUM(CASE WHEN blocker_category = 'risk_validation' THEN 1 ELSE 0 END) AS risk_blocker_count,
            SUM(CASE WHEN blocks_provider_approval = 1 THEN 1 ELSE 0 END) AS blocks_provider_approval_count,
            SUM(CASE WHEN blocks_provider_activation = 1 THEN 1 ELSE 0 END) AS blocks_provider_activation_count,
            SUM(CASE WHEN blocks_provider_selection = 1 THEN 1 ELSE 0 END) AS blocks_provider_selection_count,
            SUM(CASE WHEN blocks_provider_configuration = 1 THEN 1 ELSE 0 END) AS blocks_provider_configuration_count,
            SUM(CASE WHEN blocks_provider_read_write = 1 THEN 1 ELSE 0 END) AS blocks_provider_read_write_count,
            SUM(CASE WHEN blocks_object_body_view = 1 THEN 1 ELSE 0 END) AS blocks_object_body_view_count,
            SUM(CASE WHEN blocks_export = 1 THEN 1 ELSE 0 END) AS blocks_export_count,
            SUM(CASE WHEN blocks_execution = 1 THEN 1 ELSE 0 END) AS blocks_execution_count,
            SUM(CASE WHEN tower_review_required = 1 THEN 1 ELSE 0 END) AS tower_review_required_count,
            SUM(CASE WHEN tower_review_granted = 1 THEN 1 ELSE 0 END) AS tower_review_granted_count,
            SUM(CASE WHEN risk_accepted = 1 THEN 1 ELSE 0 END) AS risk_accepted_count,
            SUM(CASE WHEN risk_waived = 1 THEN 1 ELSE 0 END) AS risk_waived_count,
            SUM(CASE WHEN mitigation_approved = 1 THEN 1 ELSE 0 END) AS mitigation_approved_count,
            SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) AS resolved_count
        FROM vault_storage_provider_prep_readiness_blockers
        WHERE checkpoint_id = ?
        """,
        (checkpoint_id,),
    ).fetchone()
    return {key: int(row[key] or 0) for key in row.keys()}


def _compact_receipt_source_snapshot(
    receipt: Dict[str, Any],
    lines_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "source_review_receipt_id": receipt["receipt_id"],
        "source_review_receipt_pack_id": receipt["pack_id"],
        "source_receipt_status": receipt["receipt_status"],
        "source_section": receipt["section_id"],
        "source_section_range": receipt["section_range"],
        "source_validation_run_id": receipt["source_validation_run_id"],
        "receipt_line_count": lines_payload["receipt_line_count"],
        "capability_line_count": lines_payload["capability_line_count"],
        "criteria_line_count": lines_payload["criteria_line_count"],
        "risk_line_count": lines_payload["risk_line_count"],
        "blocks_provider_approval_count": lines_payload["blocks_provider_approval_count"],
        "blocks_provider_activation_count": lines_payload["blocks_provider_activation_count"],
        "blocks_provider_selection_count": lines_payload["blocks_provider_selection_count"],
        "blocks_export_count": lines_payload["blocks_export_count"],
        "blocks_execution_count": lines_payload["blocks_execution_count"],
        "internal_review_receipt": receipt["internal_review_receipt"],
        "official_receipt": receipt["official_receipt"],
        "finalized_receipt": receipt["finalized_receipt"],
        "closed_receipt": receipt["closed_receipt"],
        "provider_approved": receipt["provider_approved"],
        "provider_activated": receipt["provider_activated"],
        "provider_selected": receipt["provider_selected"],
        "provider_configured": receipt["provider_configured"],
        "export_enabled": receipt["export_enabled"],
        "execution_enabled": receipt["execution_enabled"],
        "vault_done": receipt["vault_done"],
    }


def _build_readiness_data(
    receipt: Dict[str, Any],
    lines_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "readiness_schema_version": SCHEMA_VERSION,
        "checkpoint_type": "REAL_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT",
        "checkpoint_status": "REAL_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT_COMPLETE_LOCKED",
        "real_durable_checkpoint": True,
        "metadata_source": "VAULT_GP059_REAL_PROVIDER_SELECTION_REVIEW_RECEIPT",
        "source_review_receipt_id": receipt["receipt_id"],
        "source_review_receipt_pack_id": receipt["pack_id"],
        "section_closed": True,
        "section_id": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "prep_layer_complete": True,
        "readiness_score": 100,
        "component_count": len(COMPONENT_SPECS),
        "blocker_count": lines_payload["receipt_line_count"],
        "capability_blocker_count": lines_payload["capability_line_count"],
        "criteria_blocker_count": lines_payload["criteria_line_count"],
        "risk_blocker_count": lines_payload["risk_line_count"],
        "provider_candidate_count": receipt["receipt_data"]["provider_candidate_count"],
        "real_stack_closed": {
            "gp055_real_provider_decision_record": True,
            "gp056_real_provider_selection_registry": True,
            "gp057_real_provider_capability_contract": True,
            "gp058_real_provider_risk_criteria_validation_engine": True,
            "gp059_real_provider_selection_review_receipt": True,
            "gp060_real_storage_provider_prep_readiness_checkpoint": True,
        },
        "blocker_summary": {
            "blocks_provider_approval_count": lines_payload["blocks_provider_approval_count"],
            "blocks_provider_activation_count": lines_payload["blocks_provider_activation_count"],
            "blocks_provider_selection_count": lines_payload["blocks_provider_selection_count"],
            "blocks_provider_configuration_count": lines_payload["blocks_provider_configuration_count"],
            "blocks_provider_read_write_count": lines_payload["blocks_provider_read_write_count"],
            "blocks_object_body_view_count": lines_payload["blocks_object_body_view_count"],
            "blocks_export_count": lines_payload["blocks_export_count"],
            "blocks_execution_count": lines_payload["blocks_execution_count"],
            "tower_review_required_count": lines_payload["tower_review_required_count"],
            "tower_review_granted_count": lines_payload["tower_review_granted_count"],
            "resolved_count": lines_payload["resolved_count"],
        },
        "checkpoint_truth": {
            "safe_to_continue_to_gp061": True,
            "next_section_ready": True,
            "provider_approval_ready": False,
            "provider_activation_ready": False,
            "provider_configuration_ready": False,
            "provider_read_write_ready": False,
            "provider_approved": False,
            "provider_activated": False,
            "provider_recommended": False,
            "provider_selected": False,
            "provider_configured": False,
            "provider_read_enabled": False,
            "provider_write_enabled": False,
            "risk_accepted": False,
            "risk_waived": False,
            "mitigation_approved": False,
            "official_storage_receipt": False,
            "finalized_storage_receipt": False,
            "closed_storage_receipt": False,
            "object_body_view_enabled": False,
            "direct_upload_enabled": False,
            "export_enabled": False,
            "execution_enabled": False,
            "vault_done": False,
        },
        "next_section": {
            "section_id": NEXT_SECTION_ID,
            "section_title": NEXT_SECTION_TITLE,
            "section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "safe_to_continue_to_gp061": True,
    }


def _row_to_checkpoint(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "checkpoint_id": row["checkpoint_id"],
        "pack_id": row["pack_id"],
        "section_id": row["section_id"],
        "section_range": row["section_range"],
        "source_review_receipt_id": row["source_review_receipt_id"],
        "source_review_receipt_pack_id": row["source_review_receipt_pack_id"],
        "checkpoint_status": row["checkpoint_status"],
        "tower_authority_status": row["tower_authority_status"],
        "readiness_data": _json_loads(row["readiness_data_json"]),
        "prep_layer_complete": bool(row["prep_layer_complete"]),
        "readiness_score": int(row["readiness_score"]),
        "safe_to_continue_to_gp061": bool(row["safe_to_continue_to_gp061"]),
        "provider_approval_ready": bool(row["provider_approval_ready"]),
        "provider_activation_ready": bool(row["provider_activation_ready"]),
        "provider_configuration_ready": bool(row["provider_configuration_ready"]),
        "provider_read_write_ready": bool(row["provider_read_write_ready"]),
        "provider_approved": bool(row["provider_approved"]),
        "provider_activated": bool(row["provider_activated"]),
        "provider_recommended": bool(row["provider_recommended"]),
        "provider_selected": bool(row["provider_selected"]),
        "provider_configured": bool(row["provider_configured"]),
        "provider_read_enabled": bool(row["provider_read_enabled"]),
        "provider_write_enabled": bool(row["provider_write_enabled"]),
        "provider_object_read_claimed": bool(row["provider_object_read_claimed"]),
        "provider_connection_tested": bool(row["provider_connection_tested"]),
        "risk_accepted": bool(row["risk_accepted"]),
        "risk_waived": bool(row["risk_waived"]),
        "mitigation_approved": bool(row["mitigation_approved"]),
        "official_storage_receipt": bool(row["official_storage_receipt"]),
        "finalized_storage_receipt": bool(row["finalized_storage_receipt"]),
        "closed_storage_receipt": bool(row["closed_storage_receipt"]),
        "object_body_view_enabled": bool(row["object_body_view_enabled"]),
        "direct_upload_enabled": bool(row["direct_upload_enabled"]),
        "export_enabled": bool(row["export_enabled"]),
        "execution_enabled": bool(row["execution_enabled"]),
        "vault_done": bool(row["vault_done"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_component(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "component_id": row["component_id"],
        "checkpoint_id": row["checkpoint_id"],
        "component_code": row["component_code"],
        "component_name": row["component_name"],
        "source_pack_id": row["source_pack_id"],
        "source_artifact": row["source_artifact"],
        "component_status": row["component_status"],
        "real_sqlite_backed": bool(row["real_sqlite_backed"]),
        "component_ready": bool(row["component_ready"]),
        "tower_locked": bool(row["tower_locked"]),
        "provider_approval_unlocked": bool(row["provider_approval_unlocked"]),
        "provider_activation_unlocked": bool(row["provider_activation_unlocked"]),
        "export_unlocked": bool(row["export_unlocked"]),
        "execution_unlocked": bool(row["execution_unlocked"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_blocker(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "blocker_id": row["blocker_id"],
        "checkpoint_id": row["checkpoint_id"],
        "source_receipt_line_id": row["source_receipt_line_id"],
        "source_finding_id": row["source_finding_id"],
        "provider_candidate_id": row["provider_candidate_id"],
        "blocker_category": row["blocker_category"],
        "blocker_code": row["blocker_code"],
        "blocker_name": row["blocker_name"],
        "severity": row["severity"],
        "blocker_status": row["blocker_status"],
        "blocks_provider_approval": bool(row["blocks_provider_approval"]),
        "blocks_provider_activation": bool(row["blocks_provider_activation"]),
        "blocks_provider_selection": bool(row["blocks_provider_selection"]),
        "blocks_provider_configuration": bool(row["blocks_provider_configuration"]),
        "blocks_provider_read_write": bool(row["blocks_provider_read_write"]),
        "blocks_object_body_view": bool(row["blocks_object_body_view"]),
        "blocks_export": bool(row["blocks_export"]),
        "blocks_execution": bool(row["blocks_execution"]),
        "tower_review_required": bool(row["tower_review_required"]),
        "tower_review_granted": bool(row["tower_review_granted"]),
        "risk_accepted": bool(row["risk_accepted"]),
        "risk_waived": bool(row["risk_waived"]),
        "mitigation_approved": bool(row["mitigation_approved"]),
        "resolved": bool(row["resolved"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_event(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "event_id": row["event_id"],
        "checkpoint_id": row["checkpoint_id"],
        "event_type": row["event_type"],
        "event_payload": _json_loads(row["event_payload_json"]),
        "created_at": row["created_at"],
    }


def get_storage_provider_prep_readiness_checkpoint_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_storage_provider_prep_readiness_checkpoint(db_path)

    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_prep_readiness_checkpoints
            WHERE checkpoint_id = ?
            """,
            (DEFAULT_READINESS_CHECKPOINT_ID,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Storage provider prep readiness checkpoint was not initialized.")

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "checkpoint": _row_to_checkpoint(row),
    }


def get_storage_provider_prep_readiness_components(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_storage_provider_prep_readiness_checkpoint(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_prep_readiness_components
            WHERE checkpoint_id = ?
            ORDER BY component_code ASC
            """,
            (DEFAULT_READINESS_CHECKPOINT_ID,),
        ).fetchall()
        counts = _get_component_counts(conn, DEFAULT_READINESS_CHECKPOINT_ID)

    components = [_row_to_component(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "components": components,
    }


def get_storage_provider_prep_readiness_blockers(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_storage_provider_prep_readiness_checkpoint(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_prep_readiness_blockers
            WHERE checkpoint_id = ?
            ORDER BY provider_candidate_id ASC, blocker_category ASC, blocker_code ASC
            """,
            (DEFAULT_READINESS_CHECKPOINT_ID,),
        ).fetchall()
        counts = _get_blocker_counts(conn, DEFAULT_READINESS_CHECKPOINT_ID)

    blockers = [_row_to_blocker(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "blockers": blockers,
    }


def get_storage_provider_prep_readiness_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_storage_provider_prep_readiness_checkpoint(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_storage_provider_prep_readiness_events
            WHERE checkpoint_id = ?
            ORDER BY created_at ASC, event_id ASC
            """,
            (DEFAULT_READINESS_CHECKPOINT_ID,),
        ).fetchall()

    events = [_row_to_event(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "event_count": len(events),
        "events": events,
    }


def record_storage_provider_prep_readiness_event(
    event_type: str,
    event_payload: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    initialize_storage_provider_prep_readiness_checkpoint(db_path)
    payload = dict(event_payload or {})
    payload.update(
        {
            "write_type": "REAL_STORAGE_PROVIDER_PREP_READINESS_EVENT",
            "prep_layer_complete": True,
            "safe_to_continue_to_gp061": True,
            "provider_approval_ready": False,
            "provider_activation_ready": False,
            "provider_configuration_ready": False,
            "provider_read_write_ready": False,
            "provider_approved": False,
            "provider_activated": False,
            "provider_selected": False,
            "provider_recommended": False,
            "provider_configured": False,
            "provider_read_enabled": False,
            "provider_write_enabled": False,
            "risk_accepted": False,
            "risk_waived": False,
            "mitigation_approved": False,
            "official_storage_receipt": False,
            "finalized_storage_receipt": False,
            "closed_storage_receipt": False,
            "export_enabled": False,
            "execution_enabled": False,
            "vault_done": False,
        }
    )

    with _connect(db_path) as conn:
        event_id = _insert_event(
            conn,
            DEFAULT_READINESS_CHECKPOINT_ID,
            event_type,
            payload,
        )
        conn.commit()

    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "checkpoint_id": DEFAULT_READINESS_CHECKPOINT_ID,
        "real_sqlite_backed": True,
        "prep_layer_complete": True,
        "safe_to_continue_to_gp061": True,
        "provider_approval_ready": False,
        "provider_activation_ready": False,
        "provider_configuration_ready": False,
        "provider_read_write_ready": False,
        "provider_approved": False,
        "provider_activated": False,
        "provider_selected": False,
        "provider_recommended": False,
        "provider_configured": False,
        "provider_read_enabled": False,
        "provider_write_enabled": False,
        "risk_accepted": False,
        "risk_waived": False,
        "mitigation_approved": False,
        "official_storage_receipt": False,
        "finalized_storage_receipt": False,
        "closed_storage_receipt": False,
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    }


def validate_storage_provider_prep_readiness_checkpoint(db_path: Optional[str] = None) -> Dict[str, Any]:
    checkpoint = get_storage_provider_prep_readiness_checkpoint_record(db_path)["checkpoint"]
    components = get_storage_provider_prep_readiness_components(db_path)
    blockers = get_storage_provider_prep_readiness_blockers(db_path)
    events = get_storage_provider_prep_readiness_events(db_path)

    expected_component_count = len(COMPONENT_SPECS)
    expected_blocker_count = 140

    checks = [
        {
            "code": "REAL_SQLITE_READINESS_CHECKPOINT_EXISTS",
            "passed": checkpoint["checkpoint_id"] == DEFAULT_READINESS_CHECKPOINT_ID,
        },
        {
            "code": "SOURCE_GP059_REVIEW_RECEIPT_ATTACHED",
            "passed": checkpoint["source_review_receipt_id"] == DEFAULT_REVIEW_RECEIPT_ID,
        },
        {
            "code": "PREP_LAYER_COMPLETE",
            "passed": checkpoint["prep_layer_complete"] is True,
        },
        {
            "code": "READINESS_SCORE_100_FOR_PREP_LAYER_ONLY",
            "passed": checkpoint["readiness_score"] == 100,
        },
        {
            "code": "SAFE_TO_CONTINUE_TO_GP061",
            "passed": checkpoint["safe_to_continue_to_gp061"] is True,
        },
        {
            "code": "REAL_COMPONENT_ROWS_EXIST",
            "passed": components["component_count"] == expected_component_count,
        },
        {
            "code": "ALL_COMPONENTS_READY",
            "passed": components["component_ready_count"] == expected_component_count,
        },
        {
            "code": "ALL_COMPONENTS_TOWER_LOCKED",
            "passed": components["tower_locked_count"] == expected_component_count,
        },
        {
            "code": "NO_COMPONENT_UNLOCKED_PROVIDER_APPROVAL",
            "passed": components["provider_approval_unlocked_count"] == 0,
        },
        {
            "code": "NO_COMPONENT_UNLOCKED_PROVIDER_ACTIVATION",
            "passed": components["provider_activation_unlocked_count"] == 0,
        },
        {
            "code": "NO_COMPONENT_UNLOCKED_EXPORT",
            "passed": components["export_unlocked_count"] == 0,
        },
        {
            "code": "NO_COMPONENT_UNLOCKED_EXECUTION",
            "passed": components["execution_unlocked_count"] == 0,
        },
        {
            "code": "REAL_BLOCKER_ROWS_CARRIED_FORWARD",
            "passed": blockers["blocker_count"] == expected_blocker_count,
        },
        {
            "code": "BLOCKERS_HAVE_CAPABILITY_ROWS",
            "passed": blockers["capability_blocker_count"] == 60,
        },
        {
            "code": "BLOCKERS_HAVE_CRITERIA_ROWS",
            "passed": blockers["criteria_blocker_count"] == 40,
        },
        {
            "code": "BLOCKERS_HAVE_RISK_ROWS",
            "passed": blockers["risk_blocker_count"] == 40,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_PROVIDER_APPROVAL",
            "passed": blockers["blocks_provider_approval_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_PROVIDER_ACTIVATION",
            "passed": blockers["blocks_provider_activation_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_PROVIDER_SELECTION",
            "passed": blockers["blocks_provider_selection_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_PROVIDER_CONFIGURATION",
            "passed": blockers["blocks_provider_configuration_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_PROVIDER_READ_WRITE",
            "passed": blockers["blocks_provider_read_write_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_OBJECT_BODY_VIEW",
            "passed": blockers["blocks_object_body_view_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_EXPORT",
            "passed": blockers["blocks_export_count"] == expected_blocker_count,
        },
        {
            "code": "ALL_BLOCKERS_BLOCK_EXECUTION",
            "passed": blockers["blocks_execution_count"] == expected_blocker_count,
        },
        {
            "code": "NO_TOWER_REVIEW_GRANTED",
            "passed": blockers["tower_review_granted_count"] == 0,
        },
        {
            "code": "NO_BLOCKERS_RESOLVED",
            "passed": blockers["resolved_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_APPROVAL_READY",
            "passed": checkpoint["provider_approval_ready"] is False,
        },
        {
            "code": "NO_PROVIDER_ACTIVATION_READY",
            "passed": checkpoint["provider_activation_ready"] is False,
        },
        {
            "code": "NO_PROVIDER_CONFIGURATION_READY",
            "passed": checkpoint["provider_configuration_ready"] is False,
        },
        {
            "code": "NO_PROVIDER_READ_WRITE_READY",
            "passed": checkpoint["provider_read_write_ready"] is False,
        },
        {
            "code": "NO_PROVIDER_APPROVED",
            "passed": checkpoint["provider_approved"] is False,
        },
        {
            "code": "NO_PROVIDER_ACTIVATED",
            "passed": checkpoint["provider_activated"] is False,
        },
        {
            "code": "NO_PROVIDER_RECOMMENDED",
            "passed": checkpoint["provider_recommended"] is False,
        },
        {
            "code": "NO_PROVIDER_SELECTED",
            "passed": checkpoint["provider_selected"] is False,
        },
        {
            "code": "NO_PROVIDER_CONFIGURED",
            "passed": checkpoint["provider_configured"] is False,
        },
        {
            "code": "NO_PROVIDER_READ_ENABLED",
            "passed": checkpoint["provider_read_enabled"] is False,
        },
        {
            "code": "NO_PROVIDER_WRITE_ENABLED",
            "passed": checkpoint["provider_write_enabled"] is False,
        },
        {
            "code": "NO_PROVIDER_OBJECT_READ_CLAIMED",
            "passed": checkpoint["provider_object_read_claimed"] is False,
        },
        {
            "code": "NO_PROVIDER_CONNECTION_TESTED",
            "passed": checkpoint["provider_connection_tested"] is False,
        },
        {
            "code": "NO_RISK_ACCEPTED",
            "passed": checkpoint["risk_accepted"] is False and blockers["risk_accepted_count"] == 0,
        },
        {
            "code": "NO_RISK_WAIVED",
            "passed": checkpoint["risk_waived"] is False and blockers["risk_waived_count"] == 0,
        },
        {
            "code": "NO_MITIGATION_APPROVED",
            "passed": checkpoint["mitigation_approved"] is False and blockers["mitigation_approved_count"] == 0,
        },
        {
            "code": "NO_OFFICIAL_STORAGE_RECEIPT",
            "passed": checkpoint["official_storage_receipt"] is False,
        },
        {
            "code": "NO_FINALIZED_STORAGE_RECEIPT",
            "passed": checkpoint["finalized_storage_receipt"] is False,
        },
        {
            "code": "NO_CLOSED_STORAGE_RECEIPT",
            "passed": checkpoint["closed_storage_receipt"] is False,
        },
        {
            "code": "NO_OBJECT_BODY_VIEW",
            "passed": checkpoint["object_body_view_enabled"] is False,
        },
        {
            "code": "NO_DIRECT_UPLOAD",
            "passed": checkpoint["direct_upload_enabled"] is False,
        },
        {
            "code": "NO_EXPORT",
            "passed": checkpoint["export_enabled"] is False,
        },
        {
            "code": "NO_EXECUTION",
            "passed": checkpoint["execution_enabled"] is False,
        },
        {
            "code": "VAULT_NOT_DONE",
            "passed": checkpoint["vault_done"] is False,
        },
        {
            "code": "EVENT_LOG_EXISTS",
            "passed": events["event_count"] >= 5,
        },
    ]

    failed = [item for item in checks if not item["passed"]]

    return {
        "pack": _pack_payload(),
        "validation_ready": True,
        "valid": len(failed) == 0,
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "failed_checks": failed,
        "checks": checks,
        "real_sqlite_backed": True,
        "section_closed": len(failed) == 0,
        "safe_to_continue_to_gp061": len(failed) == 0,
    }


def get_storage_provider_prep_readiness_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "current_section_closed": True,
            "closed_section": SECTION_ID,
            "closed_section_title": SECTION_TITLE,
            "closed_section_range": SECTION_RANGE,
            "next_section": NEXT_SECTION_ID,
            "next_section_title": NEXT_SECTION_TITLE,
            "next_section_range": NEXT_SECTION_RANGE,
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp061": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "GP051-GP060 is closed as real storage provider prep. Continue to GP061 under the Real Storage Provider Configuration Layer. Do not switch to Clouds unless Solice explicitly asks.",
            "carry_forward_rules": [
                "GP051-GP060 Storage Provider Prep Layer is complete.",
                "Keep the real SQLite prep readiness checkpoint.",
                "Keep the real component rows.",
                "Keep the real blocker rows carried from GP059.",
                "Keep provider approval blocked.",
                "Keep provider activation blocked.",
                "Keep provider selection blocked.",
                "Keep provider configuration blocked until GP061+ builds real config contracts.",
                "Keep provider read/write blocked.",
                "Keep object body view blocked.",
                "Keep direct upload blocked.",
                "Keep export blocked.",
                "Keep execution blocked.",
                "Build GP061 Real Storage Provider Config Contract next.",
                "Do not treat Vault as done.",
            ],
        },
    }


def get_storage_provider_prep_readiness_checkpoint_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_storage_provider_prep_readiness_checkpoint(db_path)
    checkpoint = get_storage_provider_prep_readiness_checkpoint_record(db_path)["checkpoint"]
    components = get_storage_provider_prep_readiness_components(db_path)
    blockers = get_storage_provider_prep_readiness_blockers(db_path)
    events = get_storage_provider_prep_readiness_events(db_path)
    validation = validate_storage_provider_prep_readiness_checkpoint(db_path)

    return {
        "pack": _pack_payload(),
        "readiness_truth": _readiness_truth(checkpoint, components, blockers, events["event_count"], validation),
        "store": init,
        "checkpoint": checkpoint,
        "components": components,
        "blockers": blockers,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_storage_provider_prep_readiness_next_step()["next_step"],
    }


def get_gp060_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_storage_provider_prep_readiness_checkpoint_home(db_path)
    checkpoint = home["checkpoint"]
    components = home["components"]
    blockers = home["blockers"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp060_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "storage_provider_prep_readiness_checkpoint_ready": True,
            "section_closed": validation["section_closed"],
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_checkpoint_count": home["store"]["checkpoint_count"],
            "real_component_count": home["store"]["component_count"],
            "real_blocker_count": home["store"]["blocker_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp059_review_receipt_attached": True,
            "prep_layer_complete": checkpoint["prep_layer_complete"],
            "readiness_score": checkpoint["readiness_score"],
            "component_ready_count": components["component_ready_count"],
            "tower_locked_component_count": components["tower_locked_count"],
            "capability_blocker_count": blockers["capability_blocker_count"],
            "criteria_blocker_count": blockers["criteria_blocker_count"],
            "risk_blocker_count": blockers["risk_blocker_count"],
            "blocks_provider_approval_count": blockers["blocks_provider_approval_count"],
            "blocks_provider_activation_count": blockers["blocks_provider_activation_count"],
            "blocks_provider_selection_count": blockers["blocks_provider_selection_count"],
            "blocks_provider_configuration_count": blockers["blocks_provider_configuration_count"],
            "blocks_provider_read_write_count": blockers["blocks_provider_read_write_count"],
            "blocks_object_body_view_count": blockers["blocks_object_body_view_count"],
            "blocks_export_count": blockers["blocks_export_count"],
            "blocks_execution_count": blockers["blocks_execution_count"],
            "tower_review_granted_count": blockers["tower_review_granted_count"],
            "resolved_count": blockers["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp061": validation["safe_to_continue_to_gp061"],
            "vault_done": False,
            "foundation_status": "section_closed_safe_to_continue_not_done",
            "next_section": NEXT_SECTION_ID,
            "next_section_title": NEXT_SECTION_TITLE,
            "next_section_range": NEXT_SECTION_RANGE,
            "provider_approval_ready": checkpoint["provider_approval_ready"],
            "provider_activation_ready": checkpoint["provider_activation_ready"],
            "provider_configuration_ready": checkpoint["provider_configuration_ready"],
            "provider_read_write_ready": checkpoint["provider_read_write_ready"],
            "provider_approved": checkpoint["provider_approved"],
            "provider_activated": checkpoint["provider_activated"],
            "provider_recommended": checkpoint["provider_recommended"],
            "provider_selected": checkpoint["provider_selected"],
            "provider_configured": checkpoint["provider_configured"],
            "provider_write_enabled": checkpoint["provider_write_enabled"],
            "provider_read_enabled": checkpoint["provider_read_enabled"],
            "provider_object_read_claimed": checkpoint["provider_object_read_claimed"],
            "provider_connection_tested": checkpoint["provider_connection_tested"],
            "risk_accepted": checkpoint["risk_accepted"],
            "risk_waived": checkpoint["risk_waived"],
            "mitigation_approved": checkpoint["mitigation_approved"],
            "official_storage_receipt": checkpoint["official_storage_receipt"],
            "finalized_storage_receipt": checkpoint["finalized_storage_receipt"],
            "closed_storage_receipt": checkpoint["closed_storage_receipt"],
            "object_body_view_enabled": checkpoint["object_body_view_enabled"],
            "direct_upload_enabled": checkpoint["direct_upload_enabled"],
            "export_enabled": checkpoint["export_enabled"],
            "execution_enabled": checkpoint["execution_enabled"],
            "clouds_status": "parked_do_not_continue_from_vault_gp060",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "readiness_truth": home["readiness_truth"],
        "routes": home["routes"],
        "checkpoint": checkpoint,
        "components": components,
        "blockers": blockers,
        "validation": validation,
        "next_step": home["next_step"],
    }


def _pack_payload() -> Dict[str, Any]:
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP059"],
        "foundation_status": "section_closed_safe_to_continue_not_done",
        "product_depth_layer": "storage_provider_prep_readiness_checkpoint",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }


def _routes_payload() -> Dict[str, str]:
    return {
        "room_title": "Vault Storage Provider Prep Readiness Checkpoint",
        "section_header": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "route": "/vault/storage-provider-prep-readiness-checkpoint",
        "json_route": "/vault/storage-provider-prep-readiness-checkpoint.json",
        "record_route": "/vault/storage-provider-prep-readiness-record.json",
        "components_route": "/vault/storage-provider-prep-readiness-components.json",
        "blockers_route": "/vault/storage-provider-prep-readiness-blockers.json",
        "events_route": "/vault/storage-provider-prep-readiness-events.json",
        "validation_route": "/vault/storage-provider-prep-readiness-validation.json",
        "next_step_route": "/vault/storage-provider-prep-readiness-next-step.json",
        "gp060_status_route": "/vault/gp060-status.json",
    }


def _readiness_truth(
    checkpoint: Dict[str, Any],
    components: Dict[str, Any],
    blockers: Dict[str, Any],
    event_count: int,
    validation: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "storage_provider_prep_readiness_checkpoint_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "real_checkpoint_exists": checkpoint["checkpoint_id"] == DEFAULT_READINESS_CHECKPOINT_ID,
        "real_component_rows_exist": components["component_count"] == len(COMPONENT_SPECS),
        "real_blocker_rows_exist": blockers["blocker_count"] == 140,
        "real_event_log_exists": event_count >= 5,
        "source_gp059_review_receipt_attached": checkpoint["source_review_receipt_id"] == DEFAULT_REVIEW_RECEIPT_ID,
        "section_closed": validation["section_closed"],
        "prep_layer_complete": checkpoint["prep_layer_complete"],
        "readiness_score": checkpoint["readiness_score"],
        "safe_to_continue_to_gp061": validation["safe_to_continue_to_gp061"],
        "component_count": components["component_count"],
        "component_ready_count": components["component_ready_count"],
        "tower_locked_component_count": components["tower_locked_count"],
        "blocker_count": blockers["blocker_count"],
        "capability_blocker_count": blockers["capability_blocker_count"],
        "criteria_blocker_count": blockers["criteria_blocker_count"],
        "risk_blocker_count": blockers["risk_blocker_count"],
        "blocks_provider_approval_count": blockers["blocks_provider_approval_count"],
        "blocks_provider_activation_count": blockers["blocks_provider_activation_count"],
        "blocks_provider_selection_count": blockers["blocks_provider_selection_count"],
        "blocks_provider_configuration_count": blockers["blocks_provider_configuration_count"],
        "blocks_provider_read_write_count": blockers["blocks_provider_read_write_count"],
        "blocks_object_body_view_count": blockers["blocks_object_body_view_count"],
        "blocks_export_count": blockers["blocks_export_count"],
        "blocks_execution_count": blockers["blocks_execution_count"],
        "provider_approval_ready": checkpoint["provider_approval_ready"],
        "provider_activation_ready": checkpoint["provider_activation_ready"],
        "provider_configuration_ready": checkpoint["provider_configuration_ready"],
        "provider_read_write_ready": checkpoint["provider_read_write_ready"],
        "provider_approved": checkpoint["provider_approved"],
        "provider_activated": checkpoint["provider_activated"],
        "provider_recommended": checkpoint["provider_recommended"],
        "provider_selected": checkpoint["provider_selected"],
        "provider_configured": checkpoint["provider_configured"],
        "provider_read_enabled": checkpoint["provider_read_enabled"],
        "provider_write_enabled": checkpoint["provider_write_enabled"],
        "risk_accepted": checkpoint["risk_accepted"],
        "risk_waived": checkpoint["risk_waived"],
        "mitigation_approved": checkpoint["mitigation_approved"],
        "official_storage_receipt": checkpoint["official_storage_receipt"],
        "finalized_storage_receipt": checkpoint["finalized_storage_receipt"],
        "closed_storage_receipt": checkpoint["closed_storage_receipt"],
        "object_body_view_enabled": checkpoint["object_body_view_enabled"],
        "direct_upload_enabled": checkpoint["direct_upload_enabled"],
        "export_enabled": checkpoint["export_enabled"],
        "execution_enabled": checkpoint["execution_enabled"],
        "vault_done": checkpoint["vault_done"],
    }


def render_storage_provider_prep_readiness_checkpoint_page() -> str:
    home = get_storage_provider_prep_readiness_checkpoint_home()
    truth = home["readiness_truth"]
    components = home["components"]["components"]
    blockers = home["blockers"]["blockers"]
    routes = home["routes"]
    next_step = home["next_step"]

    component_cards = "\n".join(_render_component_card(item) for item in components)
    blocker_cards = "\n".join(_render_blocker_card(item) for item in blockers[:12])
    checks = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['code'])}</strong>
            <span>{'passed' if item['passed'] else 'failed'}</span>
          </div>
          <div class="pill {'ok' if item['passed'] else 'danger'}">{'Pass' if item['passed'] else 'Fail'}</div>
        </div>
        """
        for item in home["validation"]["checks"]
    )
    rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Storage Provider Prep Readiness Checkpoint · GP060</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg0: #040612;
      --bg1: #090d22;
      --panel: rgba(15, 23, 52, 0.84);
      --panel2: rgba(21, 32, 74, 0.76);
      --line: rgba(160, 179, 255, 0.24);
      --text: #eef3ff;
      --muted: #9da9d7;
      --gold: #f5d17e;
      --cyan: #83eaff;
      --danger: #ff8c9c;
      --ok: #9dffca;
      --shadow: rgba(0, 0, 0, 0.50);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 13% 9%, rgba(173, 141, 255, 0.18), transparent 34%),
        radial-gradient(circle at 88% 5%, rgba(131, 234, 255, 0.13), transparent 30%),
        radial-gradient(circle at 70% 90%, rgba(245, 209, 126, 0.09), transparent 32%),
        linear-gradient(135deg, var(--bg0), var(--bg1) 52%, #03040b);
    }}
    .shell {{ width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 34px 0 48px; }}
    .hero {{
      border: 1px solid var(--line);
      border-radius: 30px;
      padding: 30px;
      background: linear-gradient(145deg, rgba(15, 23, 52, 0.94), rgba(6, 10, 25, 0.74));
      box-shadow: 0 28px 74px var(--shadow);
    }}
    .eyebrow {{ color: var(--gold); letter-spacing: .18em; text-transform: uppercase; font-size: 12px; font-weight: 850; }}
    h1 {{ margin: 14px 0 14px; font-size: clamp(34px, 5vw, 62px); line-height: .95; }}
    p {{ color: var(--muted); line-height: 1.62; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-top: 22px; }}
    .metric {{ border: 1px solid var(--line); background: rgba(5, 8, 20, 0.48); border-radius: 20px; padding: 16px; }}
    .metric strong {{ display: block; font-size: 26px; }}
    .metric span {{ color: var(--muted); font-size: 13px; }}
    .section {{ margin-top: 18px; border: 1px solid var(--line); background: var(--panel); border-radius: 24px; padding: 22px; box-shadow: 0 20px 50px rgba(0, 0, 0, .28); }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
    .pill {{ display: inline-flex; align-items: center; border: 1px solid var(--line); border-radius: 999px; padding: 7px 10px; font-size: 12px; font-weight: 800; color: var(--text); background: rgba(10, 16, 38, .72); white-space: nowrap; }}
    .pill.ok {{ color: var(--ok); border-color: rgba(157, 255, 202, .32); }}
    .pill.danger {{ color: var(--danger); border-color: rgba(255, 140, 156, .32); }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }}
    .card {{ border: 1px solid var(--line); background: var(--panel2); border-radius: 20px; padding: 16px; }}
    .title {{ font-weight: 900; font-size: 15px; }}
    .meta {{ color: var(--muted); font-size: 13px; margin-top: 8px; line-height: 1.55; }}
    .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    .status-row {{ display: flex; align-items: center; justify-content: space-between; gap: 14px; padding: 12px 0; border-bottom: 1px solid rgba(160, 179, 255, .14); }}
    .status-row span {{ display: block; color: var(--muted); font-size: 12px; margin-top: 4px; }}
    code {{ color: var(--cyan); background: rgba(0, 0, 0, .28); border: 1px solid var(--line); border-radius: 8px; padding: 2px 6px; }}
    ul {{ margin: 14px 0 0; color: var(--muted); line-height: 1.75; }}
    @media (max-width: 1020px) {{ .metrics, .grid, .two-col {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="eyebrow">Archive Vault · Giant Pack 060</div>
      <div class="eyebrow">Storage Provider Prep Layer · GP051-GP060</div>
      <h1>Storage Provider Prep Readiness Checkpoint</h1>
      <p>
        GP060 closes GP051-GP060 with a real SQLite-backed readiness checkpoint.
        The prep layer is complete and safe to continue to GP061, but provider approval,
        activation, read/write, export, and execution remain locked.
      </p>
      <div class="metrics">
        <div class="metric"><strong>{truth['readiness_score']}</strong><span>prep readiness score</span></div>
        <div class="metric"><strong>{truth['component_count']}</strong><span>real components</span></div>
        <div class="metric"><strong>{truth['blocker_count']}</strong><span>active blockers carried</span></div>
        <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
      </div>
      <div class="chips">
        <span class="pill ok">Section closed</span>
        <span class="pill ok">Safe to GP061</span>
        <span class="pill ok">Real SQLite-backed</span>
        <span class="pill danger">No provider approved</span>
        <span class="pill danger">No export</span>
        <span class="pill danger">No execution</span>
      </div>
    </section>

    <section class="section">
      <h2>Readiness Components</h2>
      <p>These are real component rows closing the GP055-GP060 provider prep stack.</p>
      <div class="grid">{component_cards}</div>
    </section>

    <section class="section">
      <h2>Carried Forward Blockers</h2>
      <p>These are real blocker rows carried from GP059 receipt lines. They preserve all safety locks.</p>
      <div class="grid">{blocker_cards}</div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Validation Checks</h2>
        <p>GP060 validates the real section checkpoint and preserves all provider locks.</p>
        {checks}
      </div>
      <div>
        <h2>Carry Forward to GP061</h2>
        <p>{escape(next_step['owner_notebook_note'])}</p>
        <ul>{rules}</ul>
      </div>
    </section>

    <section class="section">
      <h2>GP060 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['record_route'])}</code>
        <code>{escape(routes['components_route'])}</code>
        <code>{escape(routes['blockers_route'])}</code>
        <code>{escape(routes['events_route'])}</code>
        <code>{escape(routes['validation_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp060_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_component_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="title">{escape(item['component_name'])}</div>
        <div class="meta">
          Code: <code>{escape(item['component_code'])}</code><br>
          Source: <code>{escape(item['source_pack_id'])}</code><br>
          Ready: <code>{str(item['component_ready']).lower()}</code><br>
          Tower locked: <code>{str(item['tower_locked']).lower()}</code>
        </div>
      </article>
    """


def _render_blocker_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="title">{escape(item['blocker_name'])}</div>
        <div class="meta">
          Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
          Category: <code>{escape(item['blocker_category'])}</code><br>
          Code: <code>{escape(item['blocker_code'])}</code><br>
          Blocks export: <code>{str(item['blocks_export']).lower()}</code><br>
          Blocks execution: <code>{str(item['blocks_execution']).lower()}</code>
        </div>
      </article>
    """
