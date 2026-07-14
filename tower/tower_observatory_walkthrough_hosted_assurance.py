"""
Hosted persistence assurance for the Tower-owned
Observatory walkthrough ledger.

The module provides runtime gates, readiness decisions,
backup cadence inspection, restore drills, retention
approval records, export review, and storage incidents.

No direct Archive Vault write is performed.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from tower.tower_observatory_walkthrough_store import (
    DATABASE_ENVIRONMENT_KEY,
    database_path,
)
from tower.tower_observatory_walkthrough_store_ops import (
    BACKUP_DIRECTORY_ENVIRONMENT_KEY,
    RETENTION_DAYS_ENVIRONMENT_KEY,
    configured_backup_directory,
    configured_retention_days,
    corruption_recovery_assessment,
    create_backup_snapshot,
    ledger_health_check,
    owner_export_preview,
    retention_preview,
    validate_hosted_configuration,
    verify_backup_snapshot,
)


BACKUP_MAX_AGE_HOURS_ENVIRONMENT_KEY = (
    "TOWER_OB_WALKTHROUGH_BACKUP_MAX_AGE_HOURS"
)

DEFAULT_BACKUP_MAX_AGE_HOURS = 24

HOSTED_MODE_ENVIRONMENT_KEY = (
    "TOWER_HOSTED_MODE"
)

INCIDENT_DIRECTORY_ENVIRONMENT_KEY = (
    "TOWER_OB_WALKTHROUGH_INCIDENT_DIR"
)

DEFAULT_INCIDENT_DIRECTORY = Path(
    "/tmp/simplee_tower_ob_walkthrough_incidents"
)

RETENTION_APPROVAL_DIRECTORY_ENVIRONMENT_KEY = (
    "TOWER_OB_WALKTHROUGH_RETENTION_APPROVAL_DIR"
)

DEFAULT_RETENTION_APPROVAL_DIRECTORY = Path(
    "/tmp/"
    "simplee_tower_ob_walkthrough_retention_approvals"
)


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


def _canonical_json(
    payload: Dict[str, Any],
) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )


def _payload_hash(
    payload: Dict[str, Any],
) -> str:
    return hashlib.sha256(
        _canonical_json(
            payload
        ).encode("utf-8")
    ).hexdigest()


def _safe_identifier(
    value: str,
) -> str:
    safe = "".join(
        character
        for character in str(value)
        if character.isalnum()
        or character in {
            "-",
            "_",
        }
    )

    return safe[:100]


def hosted_mode_enabled() -> bool:
    return os.environ.get(
        HOSTED_MODE_ENVIRONMENT_KEY,
        "",
    ).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def configured_backup_max_age_hours() -> int:
    raw = os.environ.get(
        BACKUP_MAX_AGE_HOURS_ENVIRONMENT_KEY
    )

    if not raw:
        return DEFAULT_BACKUP_MAX_AGE_HOURS

    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_BACKUP_MAX_AGE_HOURS

    return max(
        1,
        min(
            value,
            24 * 30,
        ),
    )


def configured_incident_directory(
    override: str | Path | None = None,
) -> Path:
    if override is not None:
        return Path(override)

    configured = os.environ.get(
        INCIDENT_DIRECTORY_ENVIRONMENT_KEY
    )

    if configured:
        return Path(configured)

    return DEFAULT_INCIDENT_DIRECTORY


def configured_retention_approval_directory(
    override: str | Path | None = None,
) -> Path:
    if override is not None:
        return Path(override)

    configured = os.environ.get(
        RETENTION_APPROVAL_DIRECTORY_ENVIRONMENT_KEY
    )

    if configured:
        return Path(configured)

    return DEFAULT_RETENTION_APPROVAL_DIRECTORY


def hosted_runtime_gate(
    *,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
    require_hosted_mode: bool = False,
) -> Dict[str, Any]:
    configuration = validate_hosted_configuration(
        database_override=database_override,
        backup_override=backup_override,
    )

    hosted_mode = hosted_mode_enabled()

    database_environment_present = bool(
        os.environ.get(
            DATABASE_ENVIRONMENT_KEY
        )
    )

    backup_environment_present = bool(
        os.environ.get(
            BACKUP_DIRECTORY_ENVIRONMENT_KEY
        )
    )

    checks = {
        "configuration_ready": (
            configuration["ready"]
        ),
        "database_path_absolute": (
            configuration["checks"][
                "database_path_absolute"
            ]
        ),
        "backup_path_absolute": (
            configuration["checks"][
                "backup_path_absolute"
            ]
        ),
        "database_outside_repository": (
            configuration["checks"][
                "database_not_inside_repository"
            ]
        ),
        "backup_outside_repository": (
            configuration["checks"][
                "backup_not_inside_repository"
            ]
        ),
        "hosted_mode_requirement_satisfied": (
            hosted_mode
            if require_hosted_mode
            else True
        ),
        "hosted_database_environment_present": (
            database_environment_present
            if hosted_mode
            else True
        ),
        "hosted_backup_environment_present": (
            backup_environment_present
            if hosted_mode
            else True
        ),
    }

    ready = all(
        checks.values()
    )

    return {
        "ready": ready,
        "hosted_mode": hosted_mode,
        "require_hosted_mode": (
            require_hosted_mode
        ),
        "checks": checks,
        "configuration": configuration,
        "database_environment_present": (
            database_environment_present
        ),
        "backup_environment_present": (
            backup_environment_present
        ),
        "backup_max_age_hours": (
            configured_backup_max_age_hours()
        ),
        "retention_days": (
            configured_retention_days()
        ),
        "tower_owned_storage": True,
        "direct_vault_write": False,
        "public_links": False,
    }


def startup_fail_closed_decision(
    *,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
    require_hosted_mode: bool = False,
) -> Dict[str, Any]:
    runtime = hosted_runtime_gate(
        database_override=database_override,
        backup_override=backup_override,
        require_hosted_mode=require_hosted_mode,
    )

    health = None

    try:
        health = ledger_health_check(
            database_override=database_override
        )
    except Exception as exc:
        health = {
            "healthy": False,
            "error": repr(exc),
        }

    allowed = all([
        runtime["ready"],
        bool(
            health.get(
                "healthy"
            )
        ),
    ])

    if allowed:
        decision = (
            "ALLOW_GUIDED_RUN_PERSISTENCE"
        )
    else:
        decision = (
            "DENY_GUIDED_RUN_PERSISTENCE_STARTUP"
        )

    return {
        "allowed": allowed,
        "decision": decision,
        "runtime_gate": runtime,
        "ledger_health": health,
        "fail_closed": True,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
    }


def backup_rotation_inventory(
    *,
    backup_override: str | Path | None = None,
    max_items: int = 100,
) -> Dict[str, Any]:
    backup_directory = (
        configured_backup_directory(
            backup_override
        )
    )

    safe_limit = max(
        1,
        min(
            int(max_items),
            500,
        ),
    )

    candidates = []

    if backup_directory.exists():
        candidates = sorted(
            backup_directory.glob(
                "*.sqlite3"
            ),
            key=lambda path: (
                path.stat().st_mtime
            ),
            reverse=True,
        )[:safe_limit]

    records = []

    for candidate in candidates:
        verification = (
            verify_backup_snapshot(
                candidate
            )
        )

        modified = datetime.fromtimestamp(
            candidate.stat().st_mtime,
            timezone.utc,
        )

        age_hours = (
            utc_now() - modified
        ).total_seconds() / 3600

        records.append({
            "backup_path": str(
                candidate
            ),
            "modified_at": (
                modified.isoformat()
            ),
            "age_hours": round(
                age_hours,
                3,
            ),
            "size_bytes": (
                candidate.stat().st_size
            ),
            "verified": (
                verification.get(
                    "verified",
                    False,
                )
            ),
            "verification": verification,
        })

    verified = [
        record
        for record in records
        if record["verified"]
    ]

    newest = (
        verified[0]
        if verified
        else None
    )

    max_age = (
        configured_backup_max_age_hours()
    )

    cadence_ready = bool(
        newest
        and newest["age_hours"]
        <= max_age
    )

    return {
        "backup_directory": str(
            backup_directory
        ),
        "backup_count": len(
            records
        ),
        "verified_backup_count": len(
            verified
        ),
        "records": records,
        "newest_verified_backup": newest,
        "maximum_age_hours": max_age,
        "cadence_ready": cadence_ready,
        "automatic_deletion": False,
        "direct_vault_write": False,
    }


def backup_cadence_readiness(
    *,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
) -> Dict[str, Any]:
    health = ledger_health_check(
        database_override=database_override
    )

    inventory = backup_rotation_inventory(
        backup_override=backup_override
    )

    ready = all([
        health["healthy"],
        inventory["cadence_ready"],
    ])

    return {
        "ready": ready,
        "ledger_healthy": (
            health["healthy"]
        ),
        "cadence_ready": (
            inventory["cadence_ready"]
        ),
        "maximum_age_hours": (
            inventory["maximum_age_hours"]
        ),
        "newest_verified_backup": (
            inventory[
                "newest_verified_backup"
            ]
        ),
        "backup_count": (
            inventory["backup_count"]
        ),
        "verified_backup_count": (
            inventory[
                "verified_backup_count"
            ]
        ),
        "automatic_backup_triggered": False,
        "automatic_deletion": False,
    }


def controlled_restore_drill(
    *,
    backup_path: str | Path,
) -> Dict[str, Any]:
    verification = verify_backup_snapshot(
        backup_path
    )

    if not verification.get(
        "verified"
    ):
        return {
            "passed": False,
            "reason_code": (
                "tower_ob_restore_drill_"
                "backup_not_verified"
            ),
            "verification": verification,
            "production_database_replaced": False,
        }

    drill_root = Path(
        tempfile.mkdtemp(
            prefix="tower_ob_restore_drill_"
        )
    )

    drill_database = (
        drill_root / "restored.sqlite3"
    )

    shutil.copy2(
        backup_path,
        drill_database,
    )

    try:
        drill_health = ledger_health_check(
            database_override=drill_database
        )

        with sqlite3.connect(
            drill_database
        ) as database:
            database.row_factory = sqlite3.Row

            counts = {
                "runs": database.execute(
                    """
                    SELECT COUNT(*)
                    FROM guided_runs
                    """
                ).fetchone()[0],
                "room_receipts": database.execute(
                    """
                    SELECT COUNT(*)
                    FROM guided_room_receipts
                    """
                ).fetchone()[0],
                "final_receipts": database.execute(
                    """
                    SELECT COUNT(*)
                    FROM guided_final_receipts
                    """
                ).fetchone()[0],
            }

        passed = drill_health["healthy"]

        return {
            "passed": passed,
            "reason_code": (
                "tower_ob_restore_drill_passed"
                if passed
                else (
                    "tower_ob_restore_drill_"
                    "health_failed"
                )
            ),
            "verification": verification,
            "drill_health": drill_health,
            "counts": counts,
            "temporary_database": str(
                drill_database
            ),
            "production_database_replaced": False,
            "automatic_restore": False,
            "direct_vault_write": False,
        }

    finally:
        shutil.rmtree(
            drill_root,
            ignore_errors=True,
        )


def create_retention_approval_preview(
    *,
    owner_id: str,
    database_override: str | Path | None = None,
    approval_directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    preview = retention_preview(
        owner_id=owner_id,
        database_override=database_override,
    )

    source = {
        "owner_id": owner_id,
        "created_at": (
            utc_now().isoformat()
        ),
        "retention_days": (
            preview["retention_days"]
        ),
        "cutoff": preview["cutoff"],
        "eligible_walkthrough_ids": [
            run["walkthrough_id"]
            for run in (
                preview["eligible_runs"]
            )
        ],
        "eligible_count": (
            preview["eligible_count"]
        ),
        "status": (
            "awaiting_owner_decision"
        ),
        "automatic_cleanup": False,
        "in_progress_runs_selected": False,
        "direct_vault_write": False,
    }

    approval_id = (
        "obretention_"
        + _payload_hash(
            source
        )[:24]
    )

    source["approval_id"] = approval_id

    directory = (
        configured_retention_approval_directory(
            approval_directory_override
        )
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        directory
        / f"{approval_id}.json"
    )

    path.write_text(
        json.dumps(
            source,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "created": True,
        "approval_id": approval_id,
        "record_path": str(
            path
        ),
        "record": source,
        "cleanup_performed": False,
        "owner_decision_required": True,
    }


def list_retention_approval_records(
    *,
    approval_directory_override: str | Path | None = None,
) -> List[Dict[str, Any]]:
    directory = (
        configured_retention_approval_directory(
            approval_directory_override
        )
    )

    if not directory.exists():
        return []

    records = []

    for path in sorted(
        directory.glob(
            "obretention_*.json"
        ),
        key=lambda item: (
            item.stat().st_mtime
        ),
        reverse=True,
    ):
        try:
            record = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )
        except (
            OSError,
            json.JSONDecodeError,
        ):
            continue

        records.append({
            **record,
            "record_path": str(
                path
            ),
        })

    return records


def export_evidence_review(
    *,
    owner_id: str,
    walkthrough_id: str,
    database_override: str | Path | None = None,
) -> Dict[str, Any]:
    preview = owner_export_preview(
        owner_id=owner_id,
        walkthrough_id=walkthrough_id,
        database_override=database_override,
    )

    if not preview.get(
        "available"
    ):
        return {
            **preview,
            "review_ready": False,
        }

    payload = preview[
        "export_payload"
    ]

    evidence = payload.get(
        "evidence",
        {}
    )

    room_receipts = evidence.get(
        "room_receipts",
        [],
    )

    final_receipt = evidence.get(
        "final_receipt"
    )

    run_payload = evidence.get(
        "run",
        {}
    )

    run_status = run_payload.get(
        "status"
    )

    completed_count = int(
        run_payload.get(
            "completed_count",
            0,
        )
    )

    total_room_count = int(
        run_payload.get(
            "total_room_count",
            6,
        )
    )

    stored_room_receipt_count = len(
        room_receipts
    )

    checks = {
        "run_present": bool(
            run_payload
        ),
        "integrity_valid": bool(
            evidence.get(
                "integrity_valid"
            )
        ),
        "room_receipt_count_consistent": (
            stored_room_receipt_count
            == completed_count
        ),
        "completed_run_has_all_room_receipts": (
            stored_room_receipt_count
            == total_room_count
            if run_status == "completed"
            else True
        ),
        "final_receipt_consistent": (
            final_receipt is not None
            if run_status == "completed"
            else final_receipt is None
        ),
        "public_link_created": (
            preview[
                "public_link_created"
            ]
            is False
        ),
        "direct_vault_write": (
            preview[
                "direct_vault_write"
            ]
            is False
        ),
    }

    review_ready = all(
        checks.values()
    )

    return {
        "review_ready": review_ready,
        "walkthrough_id": (
            walkthrough_id
        ),
        "checks": checks,
        "export_sha256": (
            preview["export_sha256"]
        ),
        "room_receipt_count": len(
            room_receipts
        ),
        "final_receipt_present": (
            final_receipt is not None
        ),
        "file_written": False,
        "public_link_created": False,
        "direct_vault_write": False,
    }


def create_storage_incident_receipt(
    *,
    incident_type: str,
    severity: str,
    summary: str,
    evidence: Dict[str, Any],
    owner_id: str,
    incident_directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    normalized_severity = (
        str(severity)
        .strip()
        .lower()
    )

    if normalized_severity not in {
        "info",
        "warning",
        "critical",
    }:
        raise ValueError(
            "Unsupported incident severity"
        )

    source = {
        "incident_type": (
            _safe_identifier(
                incident_type
            )
        ),
        "severity": (
            normalized_severity
        ),
        "summary": str(
            summary
        )[:1000],
        "owner_id": str(
            owner_id
        ),
        "created_at": (
            utc_now().isoformat()
        ),
        "evidence": deepcopy(
            evidence
        ),
        "status": "open",
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
        "public_link_created": False,
    }

    incident_id = (
        "obstorageincident_"
        + _payload_hash(
            source
        )[:24]
    )

    source["incident_id"] = (
        incident_id
    )

    source["integrity_hash"] = (
        _payload_hash(
            source
        )
    )

    directory = (
        configured_incident_directory(
            incident_directory_override
        )
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        directory
        / f"{incident_id}.json"
    )

    path.write_text(
        json.dumps(
            source,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "created": True,
        "incident_id": incident_id,
        "record_path": str(
            path
        ),
        "receipt": source,
    }


def hosted_operations_readiness(
    *,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
    require_hosted_mode: bool = False,
) -> Dict[str, Any]:
    startup = startup_fail_closed_decision(
        database_override=database_override,
        backup_override=backup_override,
        require_hosted_mode=require_hosted_mode,
    )

    cadence = backup_cadence_readiness(
        database_override=database_override,
        backup_override=backup_override,
    )

    recovery = (
        corruption_recovery_assessment(
            database_override=database_override,
            backup_override=backup_override,
        )
    )

    blockers = []

    if not startup["allowed"]:
        blockers.append(
            "startup_gate_not_allowed"
        )

    if not cadence["ready"]:
        blockers.append(
            "backup_cadence_not_ready"
        )

    if not recovery[
        "database_healthy"
    ]:
        blockers.append(
            "database_health_failed"
        )

    ready = not blockers

    return {
        "ready": ready,
        "decision": (
            "READY_FOR_HOSTED_PERSISTENCE"
            if ready
            else (
                "NO_GO_HOSTED_PERSISTENCE"
            )
        ),
        "blockers": blockers,
        "startup": startup,
        "backup_cadence": cadence,
        "recovery": recovery,
        "fail_closed": True,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
        "public_links": False,
    }
