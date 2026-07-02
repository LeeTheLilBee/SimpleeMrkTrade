"""
VAULT GIANT PACK 059 — Real Provider Selection Review Receipt

CURRENT SECTION:
Archive Vault — Storage Provider Prep Layer
GP051-GP060

This pack adds a real durable SQLite-backed review receipt for the provider
selection validation work produced by GP058.

Purpose:
- Create a real provider selection review receipt schema.
- Persist a real review receipt sourced from GP058.
- Persist one real receipt line per GP058 validation finding.
- Persist real blocker rollups into the receipt layer.
- Persist a real receipt event log.
- Validate the review receipt without pretending provider approval.

Important truth:
- GP059 creates a real review receipt and real receipt lines.
- GP059 links to the real GP058 validation run.
- GP059 is not an official/final/closed receipt.
- GP059 does not approve a provider.
- GP059 does not activate a provider.
- GP059 does not recommend or select a provider.
- GP059 does not configure a provider.
- GP059 does not enable provider read/write.
- GP059 does not accept/waive risk or approve mitigation.
- GP059 does not unlock object bodies, raw storage, upload, export, or execution.
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

from vault.real_provider_risk_criteria_validation_engine_service import (
    DEFAULT_VALIDATION_RUN_ID,
    get_provider_risk_criteria_validation_findings,
    get_provider_risk_criteria_validation_run,
)


PACK_ID = "VAULT_GP059"
PACK_NAME = "Real Provider Selection Review Receipt"
SCHEMA_VERSION = "vault.real_provider_selection_review_receipt.v1"

SECTION_ID = "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
SECTION_TITLE = "Archive Vault — Storage Provider Prep Layer"
SECTION_RANGE = "GP051-GP060"

NEXT_PACK = "VAULT_GP060_STORAGE_PROVIDER_PREP_READINESS_CHECKPOINT"
NEXT_PACK_TITLE = "Storage Provider Prep Readiness Checkpoint"

DEFAULT_REVIEW_RECEIPT_ID = "VSPRR-GP059-001"
DEFAULT_DB_ENV = "VAULT_PROVIDER_SELECTION_REVIEW_RECEIPT_DB"
DEFAULT_DB_PATH = "data/vault_provider_selection_review_receipt.sqlite"


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


def ensure_provider_selection_review_receipt_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_provider_selection_review_receipts (
                receipt_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_validation_run_id TEXT NOT NULL,
                source_validation_pack_id TEXT NOT NULL,
                receipt_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                receipt_data_json TEXT NOT NULL,
                internal_review_receipt INTEGER NOT NULL DEFAULT 1,
                official_receipt INTEGER NOT NULL DEFAULT 0,
                finalized_receipt INTEGER NOT NULL DEFAULT 0,
                closed_receipt INTEGER NOT NULL DEFAULT 0,
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
            CREATE TABLE IF NOT EXISTS vault_provider_selection_review_receipt_lines (
                receipt_line_id TEXT PRIMARY KEY,
                receipt_id TEXT NOT NULL,
                source_finding_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                candidate_type TEXT NOT NULL,
                line_category TEXT NOT NULL,
                line_code TEXT NOT NULL,
                line_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                line_status TEXT NOT NULL,
                line_message TEXT NOT NULL,
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
                official_receipt_line INTEGER NOT NULL DEFAULT 0,
                finalized_receipt_line INTEGER NOT NULL DEFAULT 0,
                closed_receipt_line INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(receipt_id)
                    REFERENCES vault_provider_selection_review_receipts(receipt_id)
                    ON DELETE CASCADE,
                UNIQUE(receipt_id, source_finding_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_provider_selection_review_receipt_events (
                event_id TEXT PRIMARY KEY,
                receipt_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(receipt_id)
                    REFERENCES vault_provider_selection_review_receipts(receipt_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_selection_receipt_lines_receipt
            ON vault_provider_selection_review_receipt_lines(receipt_id, provider_candidate_id, line_category)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_selection_receipt_events_receipt
            ON vault_provider_selection_review_receipt_events(receipt_id, created_at)
            """
        )
        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "tables": [
            "vault_provider_selection_review_receipts",
            "vault_provider_selection_review_receipt_lines",
            "vault_provider_selection_review_receipt_events",
        ],
        "real_sqlite_backed": True,
    }


def initialize_real_provider_selection_review_receipt(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_provider_selection_review_receipt_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            """
            SELECT receipt_id
            FROM vault_provider_selection_review_receipts
            WHERE receipt_id = ?
            """,
            (DEFAULT_REVIEW_RECEIPT_ID,),
        ).fetchone()

        if existing is None:
            validation_run = get_provider_risk_criteria_validation_run()["validation_run"]
            findings_payload = get_provider_risk_criteria_validation_findings()
            findings = findings_payload["findings"]
            receipt_data = _build_receipt_data(validation_run, findings_payload)
            now = _now_iso()

            conn.execute(
                """
                INSERT INTO vault_provider_selection_review_receipts (
                    receipt_id,
                    pack_id,
                    section_id,
                    section_range,
                    source_validation_run_id,
                    source_validation_pack_id,
                    receipt_status,
                    tower_authority_status,
                    receipt_data_json,
                    internal_review_receipt,
                    official_receipt,
                    finalized_receipt,
                    closed_receipt,
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
                    object_body_view_enabled,
                    direct_upload_enabled,
                    export_enabled,
                    execution_enabled,
                    vault_done,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    DEFAULT_REVIEW_RECEIPT_ID,
                    PACK_ID,
                    SECTION_ID,
                    SECTION_RANGE,
                    validation_run["validation_run_id"],
                    validation_run["pack_id"],
                    "REAL_PROVIDER_SELECTION_REVIEW_RECEIPT_OPEN_TOWER_LOCKED",
                    "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    _json_dumps(receipt_data),
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
                    now,
                    now,
                ),
            )

            for finding in findings:
                _insert_receipt_line(conn, DEFAULT_REVIEW_RECEIPT_ID, finding, now)

            line_counts = _get_line_counts(conn, DEFAULT_REVIEW_RECEIPT_ID)

            _insert_event(
                conn,
                DEFAULT_REVIEW_RECEIPT_ID,
                "REAL_PROVIDER_SELECTION_REVIEW_RECEIPT_CREATED",
                {
                    "pack_id": PACK_ID,
                    "source_validation_run_id": validation_run["validation_run_id"],
                    "source_validation_pack_id": validation_run["pack_id"],
                    "real_sqlite_backed": True,
                    "receipt_status": "REAL_PROVIDER_SELECTION_REVIEW_RECEIPT_OPEN_TOWER_LOCKED",
                    "internal_review_receipt": True,
                    "official_receipt": False,
                    "finalized_receipt": False,
                    "closed_receipt": False,
                    "provider_approved": False,
                    "provider_activated": False,
                    "provider_selected": False,
                    "provider_configured": False,
                },
            )
            _insert_event(
                conn,
                DEFAULT_REVIEW_RECEIPT_ID,
                "SOURCE_GP058_VALIDATION_RUN_ATTACHED",
                _compact_validation_source_snapshot(validation_run, findings_payload),
            )
            _insert_event(
                conn,
                DEFAULT_REVIEW_RECEIPT_ID,
                "REAL_REVIEW_RECEIPT_LINES_CREATED",
                line_counts,
            )
            _insert_event(
                conn,
                DEFAULT_REVIEW_RECEIPT_ID,
                "TOWER_REVIEW_RECEIPT_LOCKS_CONFIRMED",
                {
                    "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    "official_receipt_blocked": True,
                    "finalized_receipt_blocked": True,
                    "closed_receipt_blocked": True,
                    "provider_approval_blocked": True,
                    "provider_activation_blocked": True,
                    "provider_selection_blocked": True,
                    "provider_configuration_blocked": True,
                    "provider_read_write_blocked": True,
                    "object_body_view_blocked": True,
                    "export_blocked": True,
                    "execution_blocked": True,
                },
            )
            conn.commit()

    counts = _get_counts(path)
    return {
        "initialized": True,
        "schema": schema,
        "receipt_id": DEFAULT_REVIEW_RECEIPT_ID,
        "receipt_count": counts["receipt_count"],
        "receipt_line_count": counts["receipt_line_count"],
        "event_count": counts["event_count"],
        "real_sqlite_backed": True,
    }


def _insert_receipt_line(
    conn: sqlite3.Connection,
    receipt_id: str,
    finding: Dict[str, Any],
    now: str,
) -> str:
    receipt_line_id = f"VSPRL-{finding['finding_id'].replace('VSPRCF-', '')}"

    conn.execute(
        """
        INSERT INTO vault_provider_selection_review_receipt_lines (
            receipt_line_id,
            receipt_id,
            source_finding_id,
            provider_candidate_id,
            candidate_type,
            line_category,
            line_code,
            line_name,
            severity,
            line_status,
            line_message,
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
            official_receipt_line,
            finalized_receipt_line,
            closed_receipt_line,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            receipt_line_id,
            receipt_id,
            finding["finding_id"],
            finding["provider_candidate_id"],
            finding["candidate_type"],
            finding["finding_category"],
            finding["finding_code"],
            finding["finding_name"],
            finding["severity"],
            "REAL_REVIEW_RECEIPT_LINE_RECORDED_BLOCKER_ACTIVE",
            finding["finding_message"],
            1 if finding["blocks_provider_approval"] else 0,
            1 if finding["blocks_provider_activation"] else 0,
            1 if finding["blocks_provider_selection"] else 0,
            1 if finding["blocks_provider_configuration"] else 0,
            1 if finding["blocks_provider_read_write"] else 0,
            1 if finding["blocks_object_body_view"] else 0,
            1 if finding["blocks_export"] else 0,
            1 if finding["blocks_execution"] else 0,
            1 if finding["tower_review_required"] else 0,
            1 if finding["tower_review_granted"] else 0,
            1 if finding["risk_accepted"] else 0,
            1 if finding["risk_waived"] else 0,
            1 if finding["mitigation_approved"] else 0,
            1 if finding["resolved"] else 0,
            0,
            0,
            0,
            now,
            now,
        ),
    )

    return receipt_line_id


def _insert_event(
    conn: sqlite3.Connection,
    receipt_id: str,
    event_type: str,
    event_payload: Dict[str, Any],
) -> str:
    event_id = f"VSPRE-{uuid.uuid4().hex[:16].upper()}"
    conn.execute(
        """
        INSERT INTO vault_provider_selection_review_receipt_events (
            event_id,
            receipt_id,
            event_type,
            event_payload_json,
            created_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            event_id,
            receipt_id,
            event_type,
            _json_dumps(event_payload),
            _now_iso(),
        ),
    )
    return event_id


def _get_counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        receipt_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_provider_selection_review_receipts"
        ).fetchone()["c"]
        receipt_line_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_provider_selection_review_receipt_lines"
        ).fetchone()["c"]
        event_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_provider_selection_review_receipt_events"
        ).fetchone()["c"]

    return {
        "receipt_count": int(receipt_count),
        "receipt_line_count": int(receipt_line_count),
        "event_count": int(event_count),
    }


def _get_line_counts(conn: sqlite3.Connection, receipt_id: str) -> Dict[str, int]:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS receipt_line_count,
            SUM(CASE WHEN line_category = 'capability_contract' THEN 1 ELSE 0 END) AS capability_line_count,
            SUM(CASE WHEN line_category = 'criteria_validation' THEN 1 ELSE 0 END) AS criteria_line_count,
            SUM(CASE WHEN line_category = 'risk_validation' THEN 1 ELSE 0 END) AS risk_line_count,
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
            SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) AS resolved_count,
            SUM(CASE WHEN official_receipt_line = 1 THEN 1 ELSE 0 END) AS official_receipt_line_count,
            SUM(CASE WHEN finalized_receipt_line = 1 THEN 1 ELSE 0 END) AS finalized_receipt_line_count,
            SUM(CASE WHEN closed_receipt_line = 1 THEN 1 ELSE 0 END) AS closed_receipt_line_count
        FROM vault_provider_selection_review_receipt_lines
        WHERE receipt_id = ?
        """,
        (receipt_id,),
    ).fetchone()

    return {key: int(row[key] or 0) for key in row.keys()}


def _compact_validation_source_snapshot(
    validation_run: Dict[str, Any],
    findings_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "source_validation_run_id": validation_run["validation_run_id"],
        "source_validation_pack_id": validation_run["pack_id"],
        "source_run_status": validation_run["run_status"],
        "source_section": validation_run["section_id"],
        "source_section_range": validation_run["section_range"],
        "source_capability_contract_id": validation_run["source_capability_contract_id"],
        "provider_candidate_count": validation_run["engine_data"]["provider_candidate_count"],
        "finding_count": findings_payload["finding_count"],
        "capability_finding_count": findings_payload["capability_finding_count"],
        "criteria_finding_count": findings_payload["criteria_finding_count"],
        "risk_finding_count": findings_payload["risk_finding_count"],
        "blocks_provider_approval_count": findings_payload["blocks_provider_approval_count"],
        "blocks_provider_activation_count": findings_payload["blocks_provider_activation_count"],
        "blocks_provider_selection_count": findings_payload["blocks_provider_selection_count"],
        "blocks_export_count": findings_payload["blocks_export_count"],
        "blocks_execution_count": findings_payload["blocks_execution_count"],
        "provider_approved": validation_run["provider_approved"],
        "provider_activated": validation_run["provider_activated"],
        "provider_selected": validation_run["provider_selected"],
        "provider_configured": validation_run["provider_configured"],
        "provider_read_enabled": validation_run["provider_read_enabled"],
        "provider_write_enabled": validation_run["provider_write_enabled"],
        "risk_accepted": validation_run["risk_accepted"],
        "risk_waived": validation_run["risk_waived"],
        "mitigation_approved": validation_run["mitigation_approved"],
        "export_enabled": validation_run["export_enabled"],
        "execution_enabled": validation_run["execution_enabled"],
        "vault_done": validation_run["vault_done"],
    }


def _build_receipt_data(
    validation_run: Dict[str, Any],
    findings_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "receipt_schema_version": SCHEMA_VERSION,
        "receipt_type": "REAL_PROVIDER_SELECTION_REVIEW_RECEIPT",
        "receipt_status": "REAL_PROVIDER_SELECTION_REVIEW_RECEIPT_OPEN_TOWER_LOCKED",
        "real_durable_receipt": True,
        "internal_review_receipt": True,
        "official_receipt": False,
        "finalized_receipt": False,
        "closed_receipt": False,
        "metadata_source": "VAULT_GP058_REAL_PROVIDER_RISK_CRITERIA_VALIDATION_ENGINE",
        "source_validation_run_id": validation_run["validation_run_id"],
        "source_validation_pack_id": validation_run["pack_id"],
        "provider_candidate_count": validation_run["engine_data"]["provider_candidate_count"],
        "receipt_line_count": findings_payload["finding_count"],
        "capability_line_count": findings_payload["capability_finding_count"],
        "criteria_line_count": findings_payload["criteria_finding_count"],
        "risk_line_count": findings_payload["risk_finding_count"],
        "blocker_summary": {
            "blocks_provider_approval_count": findings_payload["blocks_provider_approval_count"],
            "blocks_provider_activation_count": findings_payload["blocks_provider_activation_count"],
            "blocks_provider_selection_count": findings_payload["blocks_provider_selection_count"],
            "blocks_provider_configuration_count": findings_payload["blocks_provider_configuration_count"],
            "blocks_provider_read_write_count": findings_payload["blocks_provider_read_write_count"],
            "blocks_object_body_view_count": findings_payload["blocks_object_body_view_count"],
            "blocks_export_count": findings_payload["blocks_export_count"],
            "blocks_execution_count": findings_payload["blocks_execution_count"],
            "tower_review_required_count": findings_payload["tower_review_required_count"],
            "tower_review_granted_count": findings_payload["tower_review_granted_count"],
            "resolved_count": findings_payload["resolved_count"],
        },
        "receipt_truth": {
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
            "object_body_view_enabled": False,
            "direct_upload_enabled": False,
            "export_enabled": False,
            "execution_enabled": False,
            "vault_done": False,
        },
        "tower_lock_summary": {
            "tower_review_required": True,
            "tower_review_granted": False,
            "official_receipt_blocked": True,
            "finalized_receipt_blocked": True,
            "closed_receipt_blocked": True,
            "provider_approval_blocked": True,
            "provider_activation_blocked": True,
            "provider_recommendation_blocked": True,
            "provider_selection_blocked": True,
            "provider_configuration_blocked": True,
            "provider_read_write_blocked": True,
            "object_body_view_blocked": True,
            "direct_upload_blocked": True,
            "export_blocked": True,
            "execution_blocked": True,
        },
        "next_pack": NEXT_PACK,
        "next_pack_title": NEXT_PACK_TITLE,
        "safe_to_continue_to_gp060": True,
    }


def _row_to_receipt(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "receipt_id": row["receipt_id"],
        "pack_id": row["pack_id"],
        "section_id": row["section_id"],
        "section_range": row["section_range"],
        "source_validation_run_id": row["source_validation_run_id"],
        "source_validation_pack_id": row["source_validation_pack_id"],
        "receipt_status": row["receipt_status"],
        "tower_authority_status": row["tower_authority_status"],
        "receipt_data": _json_loads(row["receipt_data_json"]),
        "internal_review_receipt": bool(row["internal_review_receipt"]),
        "official_receipt": bool(row["official_receipt"]),
        "finalized_receipt": bool(row["finalized_receipt"]),
        "closed_receipt": bool(row["closed_receipt"]),
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
        "object_body_view_enabled": bool(row["object_body_view_enabled"]),
        "direct_upload_enabled": bool(row["direct_upload_enabled"]),
        "export_enabled": bool(row["export_enabled"]),
        "execution_enabled": bool(row["execution_enabled"]),
        "vault_done": bool(row["vault_done"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_line(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "receipt_line_id": row["receipt_line_id"],
        "receipt_id": row["receipt_id"],
        "source_finding_id": row["source_finding_id"],
        "provider_candidate_id": row["provider_candidate_id"],
        "candidate_type": row["candidate_type"],
        "line_category": row["line_category"],
        "line_code": row["line_code"],
        "line_name": row["line_name"],
        "severity": row["severity"],
        "line_status": row["line_status"],
        "line_message": row["line_message"],
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
        "official_receipt_line": bool(row["official_receipt_line"]),
        "finalized_receipt_line": bool(row["finalized_receipt_line"]),
        "closed_receipt_line": bool(row["closed_receipt_line"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_event(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "event_id": row["event_id"],
        "receipt_id": row["receipt_id"],
        "event_type": row["event_type"],
        "event_payload": _json_loads(row["event_payload_json"]),
        "created_at": row["created_at"],
    }


def get_provider_selection_review_receipt_record(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_selection_review_receipt(db_path)

    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_provider_selection_review_receipts
            WHERE receipt_id = ?
            """,
            (DEFAULT_REVIEW_RECEIPT_ID,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Real provider selection review receipt was not initialized.")

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "receipt": _row_to_receipt(row),
    }


def get_provider_selection_review_receipt_lines(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_selection_review_receipt(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_provider_selection_review_receipt_lines
            WHERE receipt_id = ?
            ORDER BY provider_candidate_id ASC, line_category ASC, line_code ASC
            """,
            (DEFAULT_REVIEW_RECEIPT_ID,),
        ).fetchall()
        counts = _get_line_counts(conn, DEFAULT_REVIEW_RECEIPT_ID)

    lines = [_row_to_line(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "lines": lines,
    }


def get_provider_selection_review_receipt_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_selection_review_receipt(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_provider_selection_review_receipt_events
            WHERE receipt_id = ?
            ORDER BY created_at ASC, event_id ASC
            """,
            (DEFAULT_REVIEW_RECEIPT_ID,),
        ).fetchall()

    events = [_row_to_event(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "event_count": len(events),
        "events": events,
    }


def record_provider_selection_review_receipt_event(
    event_type: str,
    event_payload: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    initialize_real_provider_selection_review_receipt(db_path)
    payload = dict(event_payload or {})
    payload.update(
        {
            "write_type": "REAL_PROVIDER_SELECTION_REVIEW_RECEIPT_EVENT",
            "internal_review_receipt": True,
            "official_receipt": False,
            "finalized_receipt": False,
            "closed_receipt": False,
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
            "export_enabled": False,
            "execution_enabled": False,
            "vault_done": False,
        }
    )

    with _connect(db_path) as conn:
        event_id = _insert_event(
            conn,
            DEFAULT_REVIEW_RECEIPT_ID,
            event_type,
            payload,
        )
        conn.commit()

    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "receipt_id": DEFAULT_REVIEW_RECEIPT_ID,
        "real_sqlite_backed": True,
        "internal_review_receipt": True,
        "official_receipt": False,
        "finalized_receipt": False,
        "closed_receipt": False,
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
        "export_enabled": False,
        "execution_enabled": False,
        "vault_done": False,
    }


def validate_provider_selection_review_receipt(db_path: Optional[str] = None) -> Dict[str, Any]:
    receipt = get_provider_selection_review_receipt_record(db_path)["receipt"]
    lines = get_provider_selection_review_receipt_lines(db_path)
    events = get_provider_selection_review_receipt_events(db_path)

    expected_total = 140

    checks = [
        {
            "code": "REAL_SQLITE_REVIEW_RECEIPT_EXISTS",
            "passed": receipt["receipt_id"] == DEFAULT_REVIEW_RECEIPT_ID,
        },
        {
            "code": "SOURCE_GP058_VALIDATION_RUN_ATTACHED",
            "passed": receipt["source_validation_run_id"] == DEFAULT_VALIDATION_RUN_ID,
        },
        {
            "code": "REAL_REVIEW_RECEIPT_LINES_EXIST",
            "passed": lines["receipt_line_count"] == expected_total,
        },
        {
            "code": "RECEIPT_HAS_CAPABILITY_LINES",
            "passed": lines["capability_line_count"] == 60,
        },
        {
            "code": "RECEIPT_HAS_CRITERIA_LINES",
            "passed": lines["criteria_line_count"] == 40,
        },
        {
            "code": "RECEIPT_HAS_RISK_LINES",
            "passed": lines["risk_line_count"] == 40,
        },
        {
            "code": "ALL_RECEIPT_LINES_BLOCK_PROVIDER_APPROVAL",
            "passed": lines["blocks_provider_approval_count"] == expected_total,
        },
        {
            "code": "ALL_RECEIPT_LINES_BLOCK_PROVIDER_ACTIVATION",
            "passed": lines["blocks_provider_activation_count"] == expected_total,
        },
        {
            "code": "ALL_RECEIPT_LINES_BLOCK_PROVIDER_SELECTION",
            "passed": lines["blocks_provider_selection_count"] == expected_total,
        },
        {
            "code": "ALL_RECEIPT_LINES_BLOCK_PROVIDER_CONFIGURATION",
            "passed": lines["blocks_provider_configuration_count"] == expected_total,
        },
        {
            "code": "ALL_RECEIPT_LINES_BLOCK_PROVIDER_READ_WRITE",
            "passed": lines["blocks_provider_read_write_count"] == expected_total,
        },
        {
            "code": "ALL_RECEIPT_LINES_BLOCK_OBJECT_BODY_VIEW",
            "passed": lines["blocks_object_body_view_count"] == expected_total,
        },
        {
            "code": "ALL_RECEIPT_LINES_BLOCK_EXPORT",
            "passed": lines["blocks_export_count"] == expected_total,
        },
        {
            "code": "ALL_RECEIPT_LINES_BLOCK_EXECUTION",
            "passed": lines["blocks_execution_count"] == expected_total,
        },
        {
            "code": "NO_TOWER_REVIEW_GRANTED",
            "passed": lines["tower_review_granted_count"] == 0,
        },
        {
            "code": "NO_LINES_RESOLVED",
            "passed": lines["resolved_count"] == 0,
        },
        {
            "code": "INTERNAL_REVIEW_RECEIPT_ONLY",
            "passed": receipt["internal_review_receipt"] is True,
        },
        {
            "code": "NO_OFFICIAL_RECEIPT",
            "passed": receipt["official_receipt"] is False and lines["official_receipt_line_count"] == 0,
        },
        {
            "code": "NO_FINALIZED_RECEIPT",
            "passed": receipt["finalized_receipt"] is False and lines["finalized_receipt_line_count"] == 0,
        },
        {
            "code": "NO_CLOSED_RECEIPT",
            "passed": receipt["closed_receipt"] is False and lines["closed_receipt_line_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_APPROVED",
            "passed": receipt["provider_approved"] is False,
        },
        {
            "code": "NO_PROVIDER_ACTIVATED",
            "passed": receipt["provider_activated"] is False,
        },
        {
            "code": "NO_PROVIDER_RECOMMENDED",
            "passed": receipt["provider_recommended"] is False,
        },
        {
            "code": "NO_PROVIDER_SELECTED",
            "passed": receipt["provider_selected"] is False,
        },
        {
            "code": "NO_PROVIDER_CONFIGURED",
            "passed": receipt["provider_configured"] is False,
        },
        {
            "code": "NO_PROVIDER_READ_ENABLED",
            "passed": receipt["provider_read_enabled"] is False,
        },
        {
            "code": "NO_PROVIDER_WRITE_ENABLED",
            "passed": receipt["provider_write_enabled"] is False,
        },
        {
            "code": "NO_PROVIDER_OBJECT_READ_CLAIMED",
            "passed": receipt["provider_object_read_claimed"] is False,
        },
        {
            "code": "NO_PROVIDER_CONNECTION_TESTED",
            "passed": receipt["provider_connection_tested"] is False,
        },
        {
            "code": "NO_RISK_ACCEPTED",
            "passed": receipt["risk_accepted"] is False and lines["risk_accepted_count"] == 0,
        },
        {
            "code": "NO_RISK_WAIVED",
            "passed": receipt["risk_waived"] is False and lines["risk_waived_count"] == 0,
        },
        {
            "code": "NO_MITIGATION_APPROVED",
            "passed": receipt["mitigation_approved"] is False and lines["mitigation_approved_count"] == 0,
        },
        {
            "code": "NO_OBJECT_BODY_VIEW",
            "passed": receipt["object_body_view_enabled"] is False,
        },
        {
            "code": "NO_DIRECT_UPLOAD",
            "passed": receipt["direct_upload_enabled"] is False,
        },
        {
            "code": "NO_EXPORT",
            "passed": receipt["export_enabled"] is False,
        },
        {
            "code": "NO_EXECUTION",
            "passed": receipt["execution_enabled"] is False,
        },
        {
            "code": "VAULT_NOT_DONE",
            "passed": receipt["vault_done"] is False,
        },
        {
            "code": "EVENT_LOG_EXISTS",
            "passed": events["event_count"] >= 4,
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
        "safe_to_continue_to_gp060": len(failed) == 0,
    }


def get_provider_selection_review_receipt_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp060": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "Continue under ARCHIVE VAULT — STORAGE PROVIDER PREP LAYER / GP051-GP060. GP060 should close this section with a real readiness checkpoint, not placeholder work.",
            "carry_forward_rules": [
                "Keep real SQLite provider selection review receipt.",
                "Keep real receipt lines sourced from GP058 findings.",
                "Keep real receipt event log.",
                "Keep blocker rollups active.",
                "Build the real storage provider prep readiness checkpoint next.",
                "Do not make the receipt official yet.",
                "Do not finalize or close the receipt yet.",
                "Do not approve a provider yet.",
                "Do not activate a provider yet.",
                "Do not recommend a provider yet.",
                "Do not select a provider yet.",
                "Do not configure a provider yet.",
                "Do not enable provider read or write yet.",
                "Do not claim provider object reads.",
                "Do not accept or waive risk.",
                "Do not approve mitigation.",
                "Do not unlock object body view.",
                "Do not unlock direct upload.",
                "Do not unlock export.",
                "Do not unlock execution.",
                "Treat this as safe to continue, not Vault done.",
            ],
        },
    }


def get_real_provider_selection_review_receipt_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_provider_selection_review_receipt(db_path)
    receipt = get_provider_selection_review_receipt_record(db_path)["receipt"]
    lines = get_provider_selection_review_receipt_lines(db_path)
    events = get_provider_selection_review_receipt_events(db_path)
    validation = validate_provider_selection_review_receipt(db_path)

    return {
        "pack": _pack_payload(),
        "receipt_truth": _receipt_truth(receipt, lines, events["event_count"], validation),
        "store": init,
        "receipt": receipt,
        "lines": lines,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_provider_selection_review_receipt_next_step()["next_step"],
    }


def get_gp059_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_provider_selection_review_receipt_home(db_path)
    receipt = home["receipt"]
    lines = home["lines"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp059_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_provider_selection_review_receipt_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_receipt_count": home["store"]["receipt_count"],
            "real_receipt_line_count": home["store"]["receipt_line_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp058_validation_run_attached": True,
            "capability_line_count": lines["capability_line_count"],
            "criteria_line_count": lines["criteria_line_count"],
            "risk_line_count": lines["risk_line_count"],
            "blocks_provider_approval_count": lines["blocks_provider_approval_count"],
            "blocks_provider_activation_count": lines["blocks_provider_activation_count"],
            "blocks_provider_selection_count": lines["blocks_provider_selection_count"],
            "blocks_provider_configuration_count": lines["blocks_provider_configuration_count"],
            "blocks_provider_read_write_count": lines["blocks_provider_read_write_count"],
            "blocks_object_body_view_count": lines["blocks_object_body_view_count"],
            "blocks_export_count": lines["blocks_export_count"],
            "blocks_execution_count": lines["blocks_execution_count"],
            "tower_review_granted_count": lines["tower_review_granted_count"],
            "resolved_count": lines["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp060": validation["safe_to_continue_to_gp060"],
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "internal_review_receipt": receipt["internal_review_receipt"],
            "official_receipt": receipt["official_receipt"],
            "finalized_receipt": receipt["finalized_receipt"],
            "closed_receipt": receipt["closed_receipt"],
            "provider_approved": receipt["provider_approved"],
            "provider_activated": receipt["provider_activated"],
            "provider_recommended": receipt["provider_recommended"],
            "provider_selected": receipt["provider_selected"],
            "provider_configured": receipt["provider_configured"],
            "provider_write_enabled": receipt["provider_write_enabled"],
            "provider_read_enabled": receipt["provider_read_enabled"],
            "provider_object_read_claimed": receipt["provider_object_read_claimed"],
            "provider_connection_tested": receipt["provider_connection_tested"],
            "risk_accepted": receipt["risk_accepted"],
            "risk_waived": receipt["risk_waived"],
            "mitigation_approved": receipt["mitigation_approved"],
            "object_body_view_enabled": receipt["object_body_view_enabled"],
            "direct_upload_enabled": receipt["direct_upload_enabled"],
            "export_enabled": receipt["export_enabled"],
            "execution_enabled": receipt["execution_enabled"],
            "clouds_status": "parked_do_not_continue_from_vault_gp059",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "receipt_truth": home["receipt_truth"],
        "routes": home["routes"],
        "receipt": receipt,
        "lines": lines,
        "validation": validation,
        "next_step": home["next_step"],
    }


def _pack_payload() -> Dict[str, Any]:
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP058"],
        "foundation_status": "safe_to_continue_not_done",
        "product_depth_layer": "real_provider_selection_review_receipt",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }


def _routes_payload() -> Dict[str, str]:
    return {
        "room_title": "Vault Real Provider Selection Review Receipt",
        "section_header": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "route": "/vault/real-provider-selection-review-receipt",
        "json_route": "/vault/real-provider-selection-review-receipt.json",
        "receipt_route": "/vault/provider-selection-review-receipt-record.json",
        "lines_route": "/vault/provider-selection-review-receipt-lines.json",
        "events_route": "/vault/provider-selection-review-receipt-events.json",
        "validation_route": "/vault/provider-selection-review-receipt-validation.json",
        "next_step_route": "/vault/provider-selection-review-receipt-next-step.json",
        "gp059_status_route": "/vault/gp059-status.json",
    }


def _receipt_truth(
    receipt: Dict[str, Any],
    lines: Dict[str, Any],
    event_count: int,
    validation: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "real_provider_selection_review_receipt_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "real_review_receipt_exists": receipt["receipt_id"] == DEFAULT_REVIEW_RECEIPT_ID,
        "real_receipt_lines_exist": lines["receipt_line_count"] == 140,
        "real_event_log_exists": event_count >= 4,
        "source_gp058_validation_run_attached": receipt["source_validation_run_id"] == DEFAULT_VALIDATION_RUN_ID,
        "validation_passed": validation["valid"],
        "receipt_line_count": lines["receipt_line_count"],
        "capability_line_count": lines["capability_line_count"],
        "criteria_line_count": lines["criteria_line_count"],
        "risk_line_count": lines["risk_line_count"],
        "blocks_provider_approval_count": lines["blocks_provider_approval_count"],
        "blocks_provider_activation_count": lines["blocks_provider_activation_count"],
        "blocks_provider_selection_count": lines["blocks_provider_selection_count"],
        "blocks_provider_configuration_count": lines["blocks_provider_configuration_count"],
        "blocks_provider_read_write_count": lines["blocks_provider_read_write_count"],
        "blocks_object_body_view_count": lines["blocks_object_body_view_count"],
        "blocks_export_count": lines["blocks_export_count"],
        "blocks_execution_count": lines["blocks_execution_count"],
        "internal_review_receipt": receipt["internal_review_receipt"],
        "official_receipt": receipt["official_receipt"],
        "finalized_receipt": receipt["finalized_receipt"],
        "closed_receipt": receipt["closed_receipt"],
        "provider_approved": receipt["provider_approved"],
        "provider_activated": receipt["provider_activated"],
        "provider_recommended": receipt["provider_recommended"],
        "provider_selected": receipt["provider_selected"],
        "provider_configured": receipt["provider_configured"],
        "provider_read_enabled": receipt["provider_read_enabled"],
        "provider_write_enabled": receipt["provider_write_enabled"],
        "risk_accepted": receipt["risk_accepted"],
        "risk_waived": receipt["risk_waived"],
        "mitigation_approved": receipt["mitigation_approved"],
        "object_body_view_enabled": receipt["object_body_view_enabled"],
        "direct_upload_enabled": receipt["direct_upload_enabled"],
        "export_enabled": receipt["export_enabled"],
        "execution_enabled": receipt["execution_enabled"],
        "vault_done": receipt["vault_done"],
        "safe_to_continue_to_gp060": validation["safe_to_continue_to_gp060"],
    }


def render_real_provider_selection_review_receipt_page() -> str:
    home = get_real_provider_selection_review_receipt_home()
    truth = home["receipt_truth"]
    lines = home["lines"]["lines"]
    routes = home["routes"]
    next_step = home["next_step"]

    line_cards = "\n".join(_render_receipt_line_card(item) for item in lines[:12])
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
  <title>Vault Real Provider Selection Review Receipt · GP059</title>
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
      <div class="eyebrow">Archive Vault · Giant Pack 059</div>
      <div class="eyebrow">Storage Provider Prep Layer · GP051-GP060</div>
      <h1>Real Provider Selection Review Receipt</h1>
      <p>
        GP059 creates a real SQLite-backed provider selection review receipt with one receipt line
        per GP058 validation finding. It is a real internal review receipt, not an official, finalized,
        closed, approval, selection, export, or execution receipt.
      </p>
      <div class="metrics">
        <div class="metric"><strong>{home['store']['receipt_count']}</strong><span>real review receipts</span></div>
        <div class="metric"><strong>{home['store']['receipt_line_count']}</strong><span>real receipt lines</span></div>
        <div class="metric"><strong>{home['store']['event_count']}</strong><span>real receipt events</span></div>
        <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
      </div>
      <div class="chips">
        <span class="pill ok">Real SQLite-backed</span>
        <span class="pill ok">Real receipt lines</span>
        <span class="pill ok">Internal review receipt</span>
        <span class="pill danger">No official receipt</span>
        <span class="pill danger">No provider approved</span>
        <span class="pill danger">No execution</span>
      </div>
    </section>

    <section class="section">
      <h2>Review Receipt Lines</h2>
      <p>These are real receipt lines copied from GP058 validation findings. They preserve blockers.</p>
      <div class="grid">{line_cards}</div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Validation Checks</h2>
        <p>GP059 validates the real review receipt against active Tower/Vault locks.</p>
        {checks}
      </div>
      <div>
        <h2>Carry Forward to GP060</h2>
        <p>{escape(next_step['owner_notebook_note'])}</p>
        <ul>{rules}</ul>
      </div>
    </section>

    <section class="section">
      <h2>GP059 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['receipt_route'])}</code>
        <code>{escape(routes['lines_route'])}</code>
        <code>{escape(routes['events_route'])}</code>
        <code>{escape(routes['validation_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp059_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_receipt_line_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="title">{escape(item['line_name'])}</div>
        <div class="meta">
          Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
          Source: <code>{escape(item['source_finding_id'])}</code><br>
          Category: <code>{escape(item['line_category'])}</code><br>
          Code: <code>{escape(item['line_code'])}</code><br>
          Official: <code>{str(item['official_receipt_line']).lower()}</code><br>
          Closed: <code>{str(item['closed_receipt_line']).lower()}</code>
        </div>
      </article>
    """
