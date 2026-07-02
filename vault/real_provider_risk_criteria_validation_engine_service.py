"""
VAULT GIANT PACK 058 — Real Provider Risk / Criteria Validation Engine

CURRENT SECTION:
Archive Vault — Storage Provider Prep Layer
GP051-GP060

This pack adds a real durable SQLite-backed validation engine over the provider
capability contract from GP057.

Purpose:
- Create a real provider risk/criteria validation schema.
- Persist a real validation run sourced from GP057.
- Persist real capability validation findings from GP057 requirement rows.
- Persist real criteria validation findings.
- Persist real risk validation findings.
- Persist real validation engine events.
- Validate that blockers remain active until Tower/provider review is real.

Important truth:
- GP058 creates real validation rows and blocker findings.
- GP058 links to the real GP057 capability contract.
- GP058 does not approve a provider.
- GP058 does not activate a provider.
- GP058 does not recommend or select a provider.
- GP058 does not configure a provider.
- GP058 does not enable provider read/write.
- GP058 does not accept/waive risk or approve mitigation.
- GP058 does not unlock object bodies, raw storage, upload, export, or execution.
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

from vault.real_storage_provider_capability_contract_service import (
    DEFAULT_CAPABILITY_CONTRACT_ID,
    get_storage_provider_capability_contract_record,
    get_storage_provider_capability_requirements,
)


PACK_ID = "VAULT_GP058"
PACK_NAME = "Real Provider Risk / Criteria Validation Engine"
SCHEMA_VERSION = "vault.real_provider_risk_criteria_validation_engine.v1"

SECTION_ID = "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
SECTION_TITLE = "Archive Vault — Storage Provider Prep Layer"
SECTION_RANGE = "GP051-GP060"

NEXT_PACK = "VAULT_GP059_REAL_PROVIDER_SELECTION_REVIEW_RECEIPT"
NEXT_PACK_TITLE = "Real Provider Selection Review Receipt"

DEFAULT_VALIDATION_RUN_ID = "VSPRCV-GP058-001"
DEFAULT_DB_ENV = "VAULT_PROVIDER_RISK_CRITERIA_VALIDATION_DB"
DEFAULT_DB_PATH = "data/vault_provider_risk_criteria_validation.sqlite"

CRITERIA_RULES = [
    {
        "rule_code": "tower_authority_required",
        "rule_name": "Tower authority required",
        "severity": "critical",
        "message": "Provider cannot advance unless Tower authority remains attached.",
    },
    {
        "rule_code": "metadata_persistence_required",
        "rule_name": "Metadata persistence required",
        "severity": "high",
        "message": "Provider must support durable metadata before storage activation.",
    },
    {
        "rule_code": "object_body_lock_required",
        "rule_name": "Object body lock required",
        "severity": "critical",
        "message": "Object bodies must remain locked until Tower grants visibility.",
    },
    {
        "rule_code": "audit_trace_required",
        "rule_name": "Audit trace required",
        "severity": "high",
        "message": "Storage provider actions must produce audit trace evidence.",
    },
    {
        "rule_code": "checksum_hash_required",
        "rule_name": "Checksum / hash required",
        "severity": "high",
        "message": "Provider must support hash/integrity verification before real storage use.",
    },
    {
        "rule_code": "export_lock_required",
        "rule_name": "Export lock required",
        "severity": "critical",
        "message": "Provider must respect export locks and external delivery denial.",
    },
    {
        "rule_code": "redaction_boundary_required",
        "rule_name": "Redaction boundary required",
        "severity": "high",
        "message": "Provider use must preserve owner/private vs shareable redaction boundaries.",
    },
    {
        "rule_code": "restore_test_required",
        "rule_name": "Restore test required",
        "severity": "high",
        "message": "Provider must support restore testing before activation.",
    },
]

RISK_RULES = [
    {
        "rule_code": "access_control_risk",
        "rule_name": "Access control risk",
        "severity": "critical",
        "message": "Provider access must remain denied until Tower grants access.",
    },
    {
        "rule_code": "privacy_boundary_risk",
        "rule_name": "Privacy boundary risk",
        "severity": "critical",
        "message": "Provider cannot expose sensitive Vault records externally.",
    },
    {
        "rule_code": "data_integrity_risk",
        "rule_name": "Data integrity risk",
        "severity": "high",
        "message": "Provider integrity behavior is not verified yet.",
    },
    {
        "rule_code": "retention_hold_risk",
        "rule_name": "Retention hold risk",
        "severity": "high",
        "message": "Retention and deletion controls are not verified yet.",
    },
    {
        "rule_code": "export_leakage_risk",
        "rule_name": "Export leakage risk",
        "severity": "critical",
        "message": "Export remains locked to prevent unauthorized external delivery.",
    },
    {
        "rule_code": "credential_boundary_risk",
        "rule_name": "Credential boundary risk",
        "severity": "critical",
        "message": "Provider credentials are not configured and must not be assumed.",
    },
    {
        "rule_code": "availability_restore_risk",
        "rule_name": "Availability / restore risk",
        "severity": "high",
        "message": "Restore behavior is not tested yet.",
    },
    {
        "rule_code": "audit_gap_risk",
        "rule_name": "Audit gap risk",
        "severity": "high",
        "message": "Official immutable audit writes are not enabled yet.",
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


def ensure_risk_criteria_validation_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    path = _resolve_db_path(db_path)

    with _connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_provider_risk_criteria_validation_runs (
                validation_run_id TEXT PRIMARY KEY,
                pack_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_range TEXT NOT NULL,
                source_capability_contract_id TEXT NOT NULL,
                source_capability_pack_id TEXT NOT NULL,
                run_status TEXT NOT NULL,
                tower_authority_status TEXT NOT NULL,
                engine_data_json TEXT NOT NULL,
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
            CREATE TABLE IF NOT EXISTS vault_provider_risk_criteria_validation_findings (
                finding_id TEXT PRIMARY KEY,
                validation_run_id TEXT NOT NULL,
                provider_candidate_id TEXT NOT NULL,
                candidate_type TEXT NOT NULL,
                finding_category TEXT NOT NULL,
                finding_code TEXT NOT NULL,
                finding_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                validation_status TEXT NOT NULL,
                finding_message TEXT NOT NULL,
                source_requirement_id TEXT,
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
                FOREIGN KEY(validation_run_id)
                    REFERENCES vault_provider_risk_criteria_validation_runs(validation_run_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_provider_risk_criteria_validation_events (
                event_id TEXT PRIMARY KEY,
                validation_run_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(validation_run_id)
                    REFERENCES vault_provider_risk_criteria_validation_runs(validation_run_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_validation_findings_run
            ON vault_provider_risk_criteria_validation_findings(validation_run_id, provider_candidate_id, finding_category)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vault_provider_validation_events_run
            ON vault_provider_risk_criteria_validation_events(validation_run_id, created_at)
            """
        )
        conn.commit()

    return {
        "schema_ready": True,
        "db_path": str(path),
        "tables": [
            "vault_provider_risk_criteria_validation_runs",
            "vault_provider_risk_criteria_validation_findings",
            "vault_provider_risk_criteria_validation_events",
        ],
        "real_sqlite_backed": True,
    }


def initialize_real_provider_risk_criteria_validation_engine(db_path: Optional[str] = None) -> Dict[str, Any]:
    schema = ensure_risk_criteria_validation_schema(db_path)
    path = schema["db_path"]

    with _connect(path) as conn:
        existing = conn.execute(
            """
            SELECT validation_run_id
            FROM vault_provider_risk_criteria_validation_runs
            WHERE validation_run_id = ?
            """,
            (DEFAULT_VALIDATION_RUN_ID,),
        ).fetchone()

        if existing is None:
            contract = get_storage_provider_capability_contract_record()["contract"]
            requirements = get_storage_provider_capability_requirements()["requirements"]
            engine_data = _build_engine_data(contract, requirements)
            now = _now_iso()

            conn.execute(
                """
                INSERT INTO vault_provider_risk_criteria_validation_runs (
                    validation_run_id,
                    pack_id,
                    section_id,
                    section_range,
                    source_capability_contract_id,
                    source_capability_pack_id,
                    run_status,
                    tower_authority_status,
                    engine_data_json,
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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    DEFAULT_VALIDATION_RUN_ID,
                    PACK_ID,
                    SECTION_ID,
                    SECTION_RANGE,
                    contract["contract_id"],
                    contract["pack_id"],
                    "REAL_VALIDATION_RUN_COMPLETE_BLOCKERS_ACTIVE_TOWER_LOCKED",
                    "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
                    _json_dumps(engine_data),
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

            _insert_capability_findings(conn, DEFAULT_VALIDATION_RUN_ID, requirements, now)
            _insert_criteria_findings(conn, DEFAULT_VALIDATION_RUN_ID, requirements, now)
            _insert_risk_findings(conn, DEFAULT_VALIDATION_RUN_ID, requirements, now)

            finding_counts = _get_finding_counts(conn, DEFAULT_VALIDATION_RUN_ID)

            _insert_event(
                conn,
                DEFAULT_VALIDATION_RUN_ID,
                "REAL_PROVIDER_RISK_CRITERIA_VALIDATION_RUN_CREATED",
                {
                    "pack_id": PACK_ID,
                    "source_capability_contract_id": contract["contract_id"],
                    "source_capability_pack_id": contract["pack_id"],
                    "real_sqlite_backed": True,
                    "run_status": "REAL_VALIDATION_RUN_COMPLETE_BLOCKERS_ACTIVE_TOWER_LOCKED",
                    "provider_approved": False,
                    "provider_activated": False,
                    "provider_selected": False,
                    "provider_configured": False,
                },
            )
            _insert_event(
                conn,
                DEFAULT_VALIDATION_RUN_ID,
                "SOURCE_GP057_CAPABILITY_CONTRACT_ATTACHED",
                _compact_contract_source_snapshot(contract),
            )
            _insert_event(
                conn,
                DEFAULT_VALIDATION_RUN_ID,
                "REAL_VALIDATION_FINDINGS_CREATED",
                finding_counts,
            )
            _insert_event(
                conn,
                DEFAULT_VALIDATION_RUN_ID,
                "TOWER_VALIDATION_LOCKS_CONFIRMED",
                {
                    "tower_authority_status": "TOWER_REVIEW_REQUIRED_NOT_GRANTED",
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
        "validation_run_id": DEFAULT_VALIDATION_RUN_ID,
        "run_count": counts["run_count"],
        "finding_count": counts["finding_count"],
        "event_count": counts["event_count"],
        "real_sqlite_backed": True,
    }


def _candidate_key(requirement: Dict[str, Any]) -> tuple[str, str]:
    return requirement["provider_candidate_id"], requirement["candidate_type"]


def _unique_candidates(requirements: list[Dict[str, Any]]) -> list[Dict[str, str]]:
    seen = {}
    for requirement in requirements:
        key = _candidate_key(requirement)
        if key not in seen:
            seen[key] = {
                "provider_candidate_id": requirement["provider_candidate_id"],
                "candidate_type": requirement["candidate_type"],
            }
    return list(seen.values())


def _insert_capability_findings(
    conn: sqlite3.Connection,
    validation_run_id: str,
    requirements: list[Dict[str, Any]],
    now: str,
) -> None:
    for requirement in requirements:
        finding_id = f"VSPRCF-CAP-{requirement['capability_requirement_id'].replace('VSPCR-', '')}"
        conn.execute(
            _finding_insert_sql(),
            _finding_values(
                finding_id=finding_id,
                validation_run_id=validation_run_id,
                provider_candidate_id=requirement["provider_candidate_id"],
                candidate_type=requirement["candidate_type"],
                finding_category="capability_contract",
                finding_code=requirement["capability_code"],
                finding_name=requirement["capability_name"],
                severity="high",
                validation_status="REQUIRED_CAPABILITY_RECORDED_NOT_CLAIMED_NOT_VERIFIED",
                finding_message=requirement["contract_reason"],
                source_requirement_id=requirement["capability_requirement_id"],
                now=now,
            ),
        )


def _insert_criteria_findings(
    conn: sqlite3.Connection,
    validation_run_id: str,
    requirements: list[Dict[str, Any]],
    now: str,
) -> None:
    for candidate in _unique_candidates(requirements):
        for rule in CRITERIA_RULES:
            finding_id = (
                f"VSPRCF-CRT-{candidate['provider_candidate_id'].split('-', 1)[-1]}-"
                f"{rule['rule_code'].upper().replace('_', '-')}"
            )
            conn.execute(
                _finding_insert_sql(),
                _finding_values(
                    finding_id=finding_id,
                    validation_run_id=validation_run_id,
                    provider_candidate_id=candidate["provider_candidate_id"],
                    candidate_type=candidate["candidate_type"],
                    finding_category="criteria_validation",
                    finding_code=rule["rule_code"],
                    finding_name=rule["rule_name"],
                    severity=rule["severity"],
                    validation_status="CRITERIA_RECORDED_REQUIRES_TOWER_PROVIDER_REVIEW",
                    finding_message=rule["message"],
                    source_requirement_id=None,
                    now=now,
                ),
            )


def _insert_risk_findings(
    conn: sqlite3.Connection,
    validation_run_id: str,
    requirements: list[Dict[str, Any]],
    now: str,
) -> None:
    for candidate in _unique_candidates(requirements):
        for rule in RISK_RULES:
            finding_id = (
                f"VSPRCF-RSK-{candidate['provider_candidate_id'].split('-', 1)[-1]}-"
                f"{rule['rule_code'].upper().replace('_', '-')}"
            )
            conn.execute(
                _finding_insert_sql(),
                _finding_values(
                    finding_id=finding_id,
                    validation_run_id=validation_run_id,
                    provider_candidate_id=candidate["provider_candidate_id"],
                    candidate_type=candidate["candidate_type"],
                    finding_category="risk_validation",
                    finding_code=rule["rule_code"],
                    finding_name=rule["rule_name"],
                    severity=rule["severity"],
                    validation_status="RISK_RECORDED_ACTIVE_NOT_ACCEPTED_NOT_WAIVED",
                    finding_message=rule["message"],
                    source_requirement_id=None,
                    now=now,
                ),
            )


def _finding_insert_sql() -> str:
    return """
        INSERT INTO vault_provider_risk_criteria_validation_findings (
            finding_id,
            validation_run_id,
            provider_candidate_id,
            candidate_type,
            finding_category,
            finding_code,
            finding_name,
            severity,
            validation_status,
            finding_message,
            source_requirement_id,
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
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """


def _finding_values(
    *,
    finding_id: str,
    validation_run_id: str,
    provider_candidate_id: str,
    candidate_type: str,
    finding_category: str,
    finding_code: str,
    finding_name: str,
    severity: str,
    validation_status: str,
    finding_message: str,
    source_requirement_id: Optional[str],
    now: str,
) -> tuple[Any, ...]:
    return (
        finding_id,
        validation_run_id,
        provider_candidate_id,
        candidate_type,
        finding_category,
        finding_code,
        finding_name,
        severity,
        validation_status,
        finding_message,
        source_requirement_id,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        0,
        now,
        now,
    )


def _insert_event(
    conn: sqlite3.Connection,
    validation_run_id: str,
    event_type: str,
    event_payload: Dict[str, Any],
) -> str:
    event_id = f"VSPVE-{uuid.uuid4().hex[:16].upper()}"
    conn.execute(
        """
        INSERT INTO vault_provider_risk_criteria_validation_events (
            event_id,
            validation_run_id,
            event_type,
            event_payload_json,
            created_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            event_id,
            validation_run_id,
            event_type,
            _json_dumps(event_payload),
            _now_iso(),
        ),
    )
    return event_id


def _get_counts(db_path: Optional[str] = None) -> Dict[str, int]:
    with _connect(db_path) as conn:
        run_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_provider_risk_criteria_validation_runs"
        ).fetchone()["c"]
        finding_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_provider_risk_criteria_validation_findings"
        ).fetchone()["c"]
        event_count = conn.execute(
            "SELECT COUNT(*) AS c FROM vault_provider_risk_criteria_validation_events"
        ).fetchone()["c"]

    return {
        "run_count": int(run_count),
        "finding_count": int(finding_count),
        "event_count": int(event_count),
    }


def _get_finding_counts(conn: sqlite3.Connection, validation_run_id: str) -> Dict[str, int]:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS finding_count,
            SUM(CASE WHEN finding_category = 'capability_contract' THEN 1 ELSE 0 END) AS capability_finding_count,
            SUM(CASE WHEN finding_category = 'criteria_validation' THEN 1 ELSE 0 END) AS criteria_finding_count,
            SUM(CASE WHEN finding_category = 'risk_validation' THEN 1 ELSE 0 END) AS risk_finding_count,
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
        FROM vault_provider_risk_criteria_validation_findings
        WHERE validation_run_id = ?
        """,
        (validation_run_id,),
    ).fetchone()

    return {key: int(row[key] or 0) for key in row.keys()}


def _compact_contract_source_snapshot(contract: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source_capability_contract_id": contract["contract_id"],
        "source_capability_pack_id": contract["pack_id"],
        "source_contract_status": contract["contract_status"],
        "source_section": contract["section_id"],
        "source_section_range": contract["section_range"],
        "source_selection_registry_id": contract["source_selection_registry_id"],
        "provider_candidate_count": contract["contract_data"]["provider_candidate_count"],
        "capability_code_count": contract["contract_data"]["capability_code_count"],
        "capability_requirement_count": contract["contract_data"]["capability_requirement_count"],
        "provider_activated": contract["provider_activated"],
        "provider_recommended": contract["provider_recommended"],
        "provider_selected": contract["provider_selected"],
        "provider_configured": contract["provider_configured"],
        "provider_read_enabled": contract["provider_read_enabled"],
        "provider_write_enabled": contract["provider_write_enabled"],
        "risk_accepted": contract["risk_accepted"],
        "risk_waived": contract["risk_waived"],
        "mitigation_approved": contract["mitigation_approved"],
        "export_enabled": contract["export_enabled"],
        "execution_enabled": contract["execution_enabled"],
        "vault_done": contract["vault_done"],
    }


def _build_engine_data(contract: Dict[str, Any], requirements: list[Dict[str, Any]]) -> Dict[str, Any]:
    provider_candidate_count = len({item["provider_candidate_id"] for item in requirements})
    capability_finding_count = len(requirements)
    criteria_finding_count = provider_candidate_count * len(CRITERIA_RULES)
    risk_finding_count = provider_candidate_count * len(RISK_RULES)
    total_finding_count = capability_finding_count + criteria_finding_count + risk_finding_count

    return {
        "engine_schema_version": SCHEMA_VERSION,
        "engine_type": "REAL_PROVIDER_RISK_CRITERIA_VALIDATION_ENGINE",
        "run_status": "REAL_VALIDATION_RUN_COMPLETE_BLOCKERS_ACTIVE_TOWER_LOCKED",
        "real_durable_validation_engine": True,
        "metadata_source": "VAULT_GP057_REAL_STORAGE_PROVIDER_CAPABILITY_CONTRACT",
        "source_capability_contract_id": contract["contract_id"],
        "source_capability_pack_id": contract["pack_id"],
        "provider_candidate_count": provider_candidate_count,
        "capability_code_count": contract["contract_data"]["capability_code_count"],
        "capability_requirement_count": capability_finding_count,
        "criteria_rule_count": len(CRITERIA_RULES),
        "risk_rule_count": len(RISK_RULES),
        "capability_finding_count": capability_finding_count,
        "criteria_finding_count": criteria_finding_count,
        "risk_finding_count": risk_finding_count,
        "total_finding_count": total_finding_count,
        "criteria_rules": CRITERIA_RULES,
        "risk_rules": RISK_RULES,
        "validation_summary": {
            "provider_approved": False,
            "provider_activated": False,
            "provider_recommended": False,
            "provider_selected": False,
            "provider_configured": False,
            "provider_read_enabled": False,
            "provider_write_enabled": False,
            "candidate_claimed_supported_count": 0,
            "contract_verified_count": 0,
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
        "safe_to_continue_to_gp059": True,
    }


def _row_to_run(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "validation_run_id": row["validation_run_id"],
        "pack_id": row["pack_id"],
        "section_id": row["section_id"],
        "section_range": row["section_range"],
        "source_capability_contract_id": row["source_capability_contract_id"],
        "source_capability_pack_id": row["source_capability_pack_id"],
        "run_status": row["run_status"],
        "tower_authority_status": row["tower_authority_status"],
        "engine_data": _json_loads(row["engine_data_json"]),
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


def _row_to_finding(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "finding_id": row["finding_id"],
        "validation_run_id": row["validation_run_id"],
        "provider_candidate_id": row["provider_candidate_id"],
        "candidate_type": row["candidate_type"],
        "finding_category": row["finding_category"],
        "finding_code": row["finding_code"],
        "finding_name": row["finding_name"],
        "severity": row["severity"],
        "validation_status": row["validation_status"],
        "finding_message": row["finding_message"],
        "source_requirement_id": row["source_requirement_id"],
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
        "validation_run_id": row["validation_run_id"],
        "event_type": row["event_type"],
        "event_payload": _json_loads(row["event_payload_json"]),
        "created_at": row["created_at"],
    }


def get_provider_risk_criteria_validation_run(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_risk_criteria_validation_engine(db_path)

    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM vault_provider_risk_criteria_validation_runs
            WHERE validation_run_id = ?
            """,
            (DEFAULT_VALIDATION_RUN_ID,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Real provider risk/criteria validation run was not initialized.")

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "validation_run": _row_to_run(row),
    }


def get_provider_risk_criteria_validation_findings(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_risk_criteria_validation_engine(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_provider_risk_criteria_validation_findings
            WHERE validation_run_id = ?
            ORDER BY provider_candidate_id ASC, finding_category ASC, finding_code ASC
            """,
            (DEFAULT_VALIDATION_RUN_ID,),
        ).fetchall()
        counts = _get_finding_counts(conn, DEFAULT_VALIDATION_RUN_ID)

    findings = [_row_to_finding(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        **counts,
        "findings": findings,
    }


def get_provider_risk_criteria_validation_events(db_path: Optional[str] = None) -> Dict[str, Any]:
    initialize_real_provider_risk_criteria_validation_engine(db_path)

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM vault_provider_risk_criteria_validation_events
            WHERE validation_run_id = ?
            ORDER BY created_at ASC, event_id ASC
            """,
            (DEFAULT_VALIDATION_RUN_ID,),
        ).fetchall()

    events = [_row_to_event(row) for row in rows]

    return {
        "pack": _pack_payload(),
        "real_sqlite_backed": True,
        "event_count": len(events),
        "events": events,
    }


def record_provider_risk_criteria_validation_review_event(
    event_type: str,
    event_payload: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    initialize_real_provider_risk_criteria_validation_engine(db_path)
    payload = dict(event_payload or {})
    payload.update(
        {
            "write_type": "REAL_RISK_CRITERIA_VALIDATION_REVIEW_EVENT",
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
            DEFAULT_VALIDATION_RUN_ID,
            event_type,
            payload,
        )
        conn.commit()

    return {
        "pack": _pack_payload(),
        "event_written": True,
        "event_id": event_id,
        "validation_run_id": DEFAULT_VALIDATION_RUN_ID,
        "real_sqlite_backed": True,
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


def validate_provider_risk_criteria_validation_engine(db_path: Optional[str] = None) -> Dict[str, Any]:
    run = get_provider_risk_criteria_validation_run(db_path)["validation_run"]
    findings = get_provider_risk_criteria_validation_findings(db_path)
    events = get_provider_risk_criteria_validation_events(db_path)

    expected_capability = 60
    expected_criteria = 40
    expected_risk = 40
    expected_total = expected_capability + expected_criteria + expected_risk

    checks = [
        {
            "code": "REAL_SQLITE_VALIDATION_RUN_EXISTS",
            "passed": run["validation_run_id"] == DEFAULT_VALIDATION_RUN_ID,
        },
        {
            "code": "SOURCE_GP057_CAPABILITY_CONTRACT_ATTACHED",
            "passed": run["source_capability_contract_id"] == DEFAULT_CAPABILITY_CONTRACT_ID,
        },
        {
            "code": "REAL_CAPABILITY_FINDINGS_EXIST",
            "passed": findings["capability_finding_count"] == expected_capability,
        },
        {
            "code": "REAL_CRITERIA_FINDINGS_EXIST",
            "passed": findings["criteria_finding_count"] == expected_criteria,
        },
        {
            "code": "REAL_RISK_FINDINGS_EXIST",
            "passed": findings["risk_finding_count"] == expected_risk,
        },
        {
            "code": "REAL_TOTAL_FINDINGS_EXIST",
            "passed": findings["finding_count"] == expected_total,
        },
        {
            "code": "ALL_FINDINGS_BLOCK_PROVIDER_APPROVAL",
            "passed": findings["blocks_provider_approval_count"] == expected_total,
        },
        {
            "code": "ALL_FINDINGS_BLOCK_PROVIDER_ACTIVATION",
            "passed": findings["blocks_provider_activation_count"] == expected_total,
        },
        {
            "code": "ALL_FINDINGS_BLOCK_PROVIDER_SELECTION",
            "passed": findings["blocks_provider_selection_count"] == expected_total,
        },
        {
            "code": "ALL_FINDINGS_BLOCK_PROVIDER_CONFIGURATION",
            "passed": findings["blocks_provider_configuration_count"] == expected_total,
        },
        {
            "code": "ALL_FINDINGS_BLOCK_PROVIDER_READ_WRITE",
            "passed": findings["blocks_provider_read_write_count"] == expected_total,
        },
        {
            "code": "ALL_FINDINGS_BLOCK_OBJECT_BODY_VIEW",
            "passed": findings["blocks_object_body_view_count"] == expected_total,
        },
        {
            "code": "ALL_FINDINGS_BLOCK_EXPORT",
            "passed": findings["blocks_export_count"] == expected_total,
        },
        {
            "code": "ALL_FINDINGS_BLOCK_EXECUTION",
            "passed": findings["blocks_execution_count"] == expected_total,
        },
        {
            "code": "NO_TOWER_REVIEW_GRANTED",
            "passed": findings["tower_review_granted_count"] == 0,
        },
        {
            "code": "NO_FINDINGS_RESOLVED",
            "passed": findings["resolved_count"] == 0,
        },
        {
            "code": "NO_PROVIDER_APPROVED",
            "passed": run["provider_approved"] is False,
        },
        {
            "code": "NO_PROVIDER_ACTIVATED",
            "passed": run["provider_activated"] is False,
        },
        {
            "code": "NO_PROVIDER_RECOMMENDED",
            "passed": run["provider_recommended"] is False,
        },
        {
            "code": "NO_PROVIDER_SELECTED",
            "passed": run["provider_selected"] is False,
        },
        {
            "code": "NO_PROVIDER_CONFIGURED",
            "passed": run["provider_configured"] is False,
        },
        {
            "code": "NO_PROVIDER_READ_ENABLED",
            "passed": run["provider_read_enabled"] is False,
        },
        {
            "code": "NO_PROVIDER_WRITE_ENABLED",
            "passed": run["provider_write_enabled"] is False,
        },
        {
            "code": "NO_PROVIDER_OBJECT_READ_CLAIMED",
            "passed": run["provider_object_read_claimed"] is False,
        },
        {
            "code": "NO_PROVIDER_CONNECTION_TESTED",
            "passed": run["provider_connection_tested"] is False,
        },
        {
            "code": "NO_RISK_ACCEPTED",
            "passed": run["risk_accepted"] is False and findings["risk_accepted_count"] == 0,
        },
        {
            "code": "NO_RISK_WAIVED",
            "passed": run["risk_waived"] is False and findings["risk_waived_count"] == 0,
        },
        {
            "code": "NO_MITIGATION_APPROVED",
            "passed": run["mitigation_approved"] is False and findings["mitigation_approved_count"] == 0,
        },
        {
            "code": "NO_OBJECT_BODY_VIEW",
            "passed": run["object_body_view_enabled"] is False,
        },
        {
            "code": "NO_DIRECT_UPLOAD",
            "passed": run["direct_upload_enabled"] is False,
        },
        {
            "code": "NO_EXPORT",
            "passed": run["export_enabled"] is False,
        },
        {
            "code": "NO_EXECUTION",
            "passed": run["execution_enabled"] is False,
        },
        {
            "code": "VAULT_NOT_DONE",
            "passed": run["vault_done"] is False,
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
        "safe_to_continue_to_gp059": len(failed) == 0,
    }


def get_provider_risk_criteria_validation_next_step() -> Dict[str, Any]:
    return {
        "pack": _pack_payload(),
        "next_step": {
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
            "safe_to_continue_to_gp059": True,
            "vault_done": False,
            "clouds_should_continue": False,
            "owner_notebook_note": "Continue under ARCHIVE VAULT — STORAGE PROVIDER PREP LAYER / GP051-GP060. Keep Vault real and durable. Do not switch to Clouds unless Solice explicitly asks.",
            "carry_forward_rules": [
                "Keep real SQLite risk/criteria validation engine.",
                "Keep real validation run records.",
                "Keep real capability validation findings.",
                "Keep real criteria validation findings.",
                "Keep real risk validation findings.",
                "Keep real blocker rollups active.",
                "Build the real provider selection review receipt next.",
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


def get_real_provider_risk_criteria_validation_engine_home(db_path: Optional[str] = None) -> Dict[str, Any]:
    init = initialize_real_provider_risk_criteria_validation_engine(db_path)
    run = get_provider_risk_criteria_validation_run(db_path)["validation_run"]
    findings = get_provider_risk_criteria_validation_findings(db_path)
    events = get_provider_risk_criteria_validation_events(db_path)
    validation = validate_provider_risk_criteria_validation_engine(db_path)

    return {
        "pack": _pack_payload(),
        "engine_truth": _engine_truth(run, findings, events["event_count"], validation),
        "store": init,
        "validation_run": run,
        "findings": findings,
        "event_count": events["event_count"],
        "validation": validation,
        "routes": _routes_payload(),
        "next_step": get_provider_risk_criteria_validation_next_step()["next_step"],
    }


def get_gp058_status(db_path: Optional[str] = None) -> Dict[str, Any]:
    home = get_real_provider_risk_criteria_validation_engine_home(db_path)
    run = home["validation_run"]
    findings = home["findings"]
    validation = home["validation"]

    return {
        "pack": _pack_payload(),
        "gp058_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "real_provider_risk_criteria_validation_engine_ready": True,
            "real_sqlite_backed": True,
            "real_schema_ready": True,
            "real_validation_run_count": home["store"]["run_count"],
            "real_finding_count": home["store"]["finding_count"],
            "real_event_count": home["store"]["event_count"],
            "source_gp057_capability_contract_attached": True,
            "capability_finding_count": findings["capability_finding_count"],
            "criteria_finding_count": findings["criteria_finding_count"],
            "risk_finding_count": findings["risk_finding_count"],
            "blocks_provider_approval_count": findings["blocks_provider_approval_count"],
            "blocks_provider_activation_count": findings["blocks_provider_activation_count"],
            "blocks_provider_selection_count": findings["blocks_provider_selection_count"],
            "blocks_provider_configuration_count": findings["blocks_provider_configuration_count"],
            "blocks_provider_read_write_count": findings["blocks_provider_read_write_count"],
            "blocks_object_body_view_count": findings["blocks_object_body_view_count"],
            "blocks_export_count": findings["blocks_export_count"],
            "blocks_execution_count": findings["blocks_execution_count"],
            "tower_review_granted_count": findings["tower_review_granted_count"],
            "resolved_count": findings["resolved_count"],
            "validation_ready": True,
            "validation_passed": validation["valid"],
            "safe_to_continue_to_gp059": validation["safe_to_continue_to_gp059"],
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "provider_approved": run["provider_approved"],
            "provider_activated": run["provider_activated"],
            "provider_recommended": run["provider_recommended"],
            "provider_selected": run["provider_selected"],
            "provider_configured": run["provider_configured"],
            "provider_write_enabled": run["provider_write_enabled"],
            "provider_read_enabled": run["provider_read_enabled"],
            "provider_object_read_claimed": run["provider_object_read_claimed"],
            "provider_connection_tested": run["provider_connection_tested"],
            "risk_accepted": run["risk_accepted"],
            "risk_waived": run["risk_waived"],
            "mitigation_approved": run["mitigation_approved"],
            "object_body_view_enabled": run["object_body_view_enabled"],
            "direct_upload_enabled": run["direct_upload_enabled"],
            "export_enabled": run["export_enabled"],
            "execution_enabled": run["execution_enabled"],
            "clouds_status": "parked_do_not_continue_from_vault_gp058",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
        "engine_truth": home["engine_truth"],
        "routes": home["routes"],
        "validation_run": run,
        "findings": findings,
        "validation": validation,
        "next_step": home["next_step"],
    }


def _pack_payload() -> Dict[str, Any]:
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "depends_on": ["VAULT_GP057"],
        "foundation_status": "safe_to_continue_not_done",
        "product_depth_layer": "real_provider_risk_criteria_validation_engine",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
    }


def _routes_payload() -> Dict[str, str]:
    return {
        "room_title": "Vault Real Provider Risk / Criteria Validation Engine",
        "section_header": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "route": "/vault/real-provider-risk-criteria-validation-engine",
        "json_route": "/vault/real-provider-risk-criteria-validation-engine.json",
        "run_route": "/vault/provider-risk-criteria-validation-run.json",
        "findings_route": "/vault/provider-risk-criteria-validation-findings.json",
        "events_route": "/vault/provider-risk-criteria-validation-events.json",
        "validation_route": "/vault/provider-risk-criteria-validation-summary.json",
        "next_step_route": "/vault/provider-risk-criteria-validation-next-step.json",
        "gp058_status_route": "/vault/gp058-status.json",
    }


def _engine_truth(
    run: Dict[str, Any],
    findings: Dict[str, Any],
    event_count: int,
    validation: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "real_provider_risk_criteria_validation_engine_ready": True,
        "real_sqlite_backed": True,
        "real_schema_ready": True,
        "real_validation_run_exists": run["validation_run_id"] == DEFAULT_VALIDATION_RUN_ID,
        "real_findings_exist": findings["finding_count"] == 140,
        "real_event_log_exists": event_count >= 4,
        "source_gp057_capability_contract_attached": run["source_capability_contract_id"] == DEFAULT_CAPABILITY_CONTRACT_ID,
        "validation_passed": validation["valid"],
        "provider_candidate_count": run["engine_data"]["provider_candidate_count"],
        "capability_finding_count": findings["capability_finding_count"],
        "criteria_finding_count": findings["criteria_finding_count"],
        "risk_finding_count": findings["risk_finding_count"],
        "finding_count": findings["finding_count"],
        "blocks_provider_approval_count": findings["blocks_provider_approval_count"],
        "blocks_provider_activation_count": findings["blocks_provider_activation_count"],
        "blocks_provider_selection_count": findings["blocks_provider_selection_count"],
        "blocks_provider_configuration_count": findings["blocks_provider_configuration_count"],
        "blocks_provider_read_write_count": findings["blocks_provider_read_write_count"],
        "blocks_object_body_view_count": findings["blocks_object_body_view_count"],
        "blocks_export_count": findings["blocks_export_count"],
        "blocks_execution_count": findings["blocks_execution_count"],
        "provider_approved": run["provider_approved"],
        "provider_activated": run["provider_activated"],
        "provider_recommended": run["provider_recommended"],
        "provider_selected": run["provider_selected"],
        "provider_configured": run["provider_configured"],
        "provider_read_enabled": run["provider_read_enabled"],
        "provider_write_enabled": run["provider_write_enabled"],
        "risk_accepted": run["risk_accepted"],
        "risk_waived": run["risk_waived"],
        "mitigation_approved": run["mitigation_approved"],
        "object_body_view_enabled": run["object_body_view_enabled"],
        "direct_upload_enabled": run["direct_upload_enabled"],
        "export_enabled": run["export_enabled"],
        "execution_enabled": run["execution_enabled"],
        "vault_done": run["vault_done"],
        "safe_to_continue_to_gp059": validation["safe_to_continue_to_gp059"],
    }


def render_real_provider_risk_criteria_validation_engine_page() -> str:
    home = get_real_provider_risk_criteria_validation_engine_home()
    truth = home["engine_truth"]
    findings = home["findings"]["findings"]
    routes = home["routes"]
    next_step = home["next_step"]

    finding_cards = "\n".join(_render_finding_card(item) for item in findings[:12])
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
  <title>Vault Real Provider Risk / Criteria Validation Engine · GP058</title>
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
      <div class="eyebrow">Archive Vault · Giant Pack 058</div>
      <div class="eyebrow">Storage Provider Prep Layer · GP051-GP060</div>
      <h1>Real Provider Risk / Criteria Validation Engine</h1>
      <p>
        GP058 creates a real SQLite-backed validation engine with durable validation runs,
        findings, risk/criteria blocker rollups, and event records. It validates the current
        provider-prep stack without approving or activating any provider.
      </p>
      <div class="metrics">
        <div class="metric"><strong>{home['store']['run_count']}</strong><span>real validation runs</span></div>
        <div class="metric"><strong>{home['store']['finding_count']}</strong><span>real findings</span></div>
        <div class="metric"><strong>{home['store']['event_count']}</strong><span>real validation events</span></div>
        <div class="metric"><strong>{str(truth['vault_done']).lower()}</strong><span>vault done</span></div>
      </div>
      <div class="chips">
        <span class="pill ok">Real SQLite-backed</span>
        <span class="pill ok">Real validation findings</span>
        <span class="pill ok">Real blocker rollups</span>
        <span class="pill danger">No provider approved</span>
        <span class="pill danger">No export</span>
        <span class="pill danger">No execution</span>
      </div>
    </section>

    <section class="section">
      <h2>Validation Findings</h2>
      <p>These are real findings and blocker rows. They are not provider approval or risk acceptance.</p>
      <div class="grid">{finding_cards}</div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Validation Checks</h2>
        <p>GP058 validates the real validation engine against active Tower/Vault locks.</p>
        {checks}
      </div>
      <div>
        <h2>Carry Forward to GP059</h2>
        <p>{escape(next_step['owner_notebook_note'])}</p>
        <ul>{rules}</ul>
      </div>
    </section>

    <section class="section">
      <h2>GP058 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['run_route'])}</code>
        <code>{escape(routes['findings_route'])}</code>
        <code>{escape(routes['events_route'])}</code>
        <code>{escape(routes['validation_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp058_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_finding_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="title">{escape(item['finding_name'])}</div>
        <div class="meta">
          Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
          Category: <code>{escape(item['finding_category'])}</code><br>
          Code: <code>{escape(item['finding_code'])}</code><br>
          Severity: <code>{escape(item['severity'])}</code><br>
          Resolved: <code>{str(item['resolved']).lower()}</code>
        </div>
      </article>
    """
