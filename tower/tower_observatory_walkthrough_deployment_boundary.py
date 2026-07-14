"""
Tower Observatory hosted deployment boundary.

This module produces reviewable deployment evidence and
owner decisions. It does not activate production, replace a
database, delete retained runs, write to Archive Vault, or
create public links.
"""

from __future__ import annotations

import hashlib
import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from tower.tower_observatory_walkthrough_hosted_assurance import (
    BACKUP_MAX_AGE_HOURS_ENVIRONMENT_KEY,
    HOSTED_MODE_ENVIRONMENT_KEY,
    INCIDENT_DIRECTORY_ENVIRONMENT_KEY,
    RETENTION_APPROVAL_DIRECTORY_ENVIRONMENT_KEY,
    backup_rotation_inventory,
    configured_incident_directory,
    configured_retention_approval_directory,
    controlled_restore_drill,
    hosted_operations_readiness,
    hosted_runtime_gate,
    list_retention_approval_records,
    startup_fail_closed_decision,
)
from tower.tower_observatory_walkthrough_store import (
    DATABASE_ENVIRONMENT_KEY,
    database_path,
)
from tower.tower_observatory_walkthrough_store_ops import (
    BACKUP_DIRECTORY_ENVIRONMENT_KEY,
    RETENTION_DAYS_ENVIRONMENT_KEY,
    configured_backup_directory,
)


DEPLOYMENT_RECORD_DIRECTORY_ENVIRONMENT_KEY = (
    "TOWER_OB_WALKTHROUGH_DEPLOYMENT_RECORD_DIR"
)

DEFAULT_DEPLOYMENT_RECORD_DIRECTORY = Path(
    "/tmp/"
    "simplee_tower_ob_walkthrough_deployment_records"
)

DEPLOYMENT_ENVIRONMENT_NAME_KEY = (
    "TOWER_DEPLOYMENT_ENVIRONMENT"
)

SUPPORTED_DEPLOYMENT_ENVIRONMENTS = {
    "development",
    "staging",
    "production",
}


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


def payload_hash(
    payload: Dict[str, Any],
) -> str:
    return hashlib.sha256(
        _canonical_json(
            payload
        ).encode("utf-8")
    ).hexdigest()


def safe_identifier(
    value: str,
) -> str:
    return "".join(
        character
        for character in str(value)
        if character.isalnum()
        or character in {
            "-",
            "_",
        }
    )[:120]


def deployment_record_directory(
    override: str | Path | None = None,
) -> Path:
    if override is not None:
        return Path(override)

    configured = os.environ.get(
        DEPLOYMENT_RECORD_DIRECTORY_ENVIRONMENT_KEY
    )

    if configured:
        return Path(configured)

    return DEFAULT_DEPLOYMENT_RECORD_DIRECTORY


def deployment_environment_name() -> str:
    value = os.environ.get(
        DEPLOYMENT_ENVIRONMENT_NAME_KEY,
        "development",
    ).strip().lower()

    if (
        value
        not in SUPPORTED_DEPLOYMENT_ENVIRONMENTS
    ):
        return "invalid"

    return value


def persist_record(
    *,
    prefix: str,
    payload: Dict[str, Any],
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    directory = deployment_record_directory(
        directory_override
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    source = deepcopy(
        payload
    )

    source["integrity_hash"] = payload_hash(
        source
    )

    record_id = (
        safe_identifier(prefix)
        + "_"
        + source["integrity_hash"][:24]
    )

    source["record_id"] = record_id

    path = (
        directory
        / f"{record_id}.json"
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
        "record_id": record_id,
        "record_path": str(
            path
        ),
        "record": source,
    }


def hosted_deployment_manifest(
    *,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
) -> Dict[str, Any]:
    environment = (
        deployment_environment_name()
    )

    runtime = hosted_runtime_gate(
        database_override=database_override,
        backup_override=backup_override,
    )

    database = database_path(
        database_override
    )

    backup_directory = (
        configured_backup_directory(
            backup_override
        )
    )

    required_environment_keys = [
        DATABASE_ENVIRONMENT_KEY,
        BACKUP_DIRECTORY_ENVIRONMENT_KEY,
        HOSTED_MODE_ENVIRONMENT_KEY,
        BACKUP_MAX_AGE_HOURS_ENVIRONMENT_KEY,
        RETENTION_DAYS_ENVIRONMENT_KEY,
        INCIDENT_DIRECTORY_ENVIRONMENT_KEY,
        RETENTION_APPROVAL_DIRECTORY_ENVIRONMENT_KEY,
        DEPLOYMENT_RECORD_DIRECTORY_ENVIRONMENT_KEY,
        DEPLOYMENT_ENVIRONMENT_NAME_KEY,
    ]

    environment_presence = {
        key: bool(
            os.environ.get(
                key
            )
        )
        for key in required_environment_keys
    }

    checks = {
        "supported_environment": (
            environment
            in SUPPORTED_DEPLOYMENT_ENVIRONMENTS
        ),
        "runtime_configuration_ready": (
            runtime["ready"]
        ),
        "database_path_absolute": (
            database.is_absolute()
        ),
        "backup_path_absolute": (
            backup_directory.is_absolute()
        ),
        "database_outside_repository": (
            "/content/SimpleeMrkTrade"
            not in str(database)
        ),
        "backup_outside_repository": (
            "/content/SimpleeMrkTrade"
            not in str(
                backup_directory
            )
        ),
    }

    ready = all(
        checks.values()
    )

    return {
        "ready": ready,
        "environment": environment,
        "generated_at": (
            utc_now().isoformat()
        ),
        "database_path": str(
            database
        ),
        "backup_directory": str(
            backup_directory
        ),
        "required_environment_keys": (
            required_environment_keys
        ),
        "environment_presence": (
            environment_presence
        ),
        "checks": checks,
        "runtime_gate": runtime,
        "activation_performed": False,
        "production_database_replaced": False,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
        "public_link_created": False,
    }


def create_environment_binding_receipt(
    *,
    owner_id: str,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    manifest = hosted_deployment_manifest(
        database_override=database_override,
        backup_override=backup_override,
    )

    source = {
        "receipt_type": (
            "tower_ob_environment_binding"
        ),
        "owner_id": owner_id,
        "created_at": (
            utc_now().isoformat()
        ),
        "environment": (
            manifest["environment"]
        ),
        "database_path": (
            manifest["database_path"]
        ),
        "backup_directory": (
            manifest["backup_directory"]
        ),
        "manifest_ready": (
            manifest["ready"]
        ),
        "checks": (
            manifest["checks"]
        ),
        "environment_presence": (
            manifest[
                "environment_presence"
            ]
        ),
        "activation_performed": False,
        "direct_vault_write": False,
        "public_link_created": False,
    }

    return persist_record(
        prefix="obenvironment",
        payload=source,
        directory_override=directory_override,
    )


def create_startup_gate_receipt(
    *,
    owner_id: str,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
    require_hosted_mode: bool = False,
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    decision = startup_fail_closed_decision(
        database_override=database_override,
        backup_override=backup_override,
        require_hosted_mode=require_hosted_mode,
    )

    source = {
        "receipt_type": (
            "tower_ob_startup_gate"
        ),
        "owner_id": owner_id,
        "created_at": (
            utc_now().isoformat()
        ),
        "allowed": decision[
            "allowed"
        ],
        "decision": decision[
            "decision"
        ],
        "fail_closed": True,
        "runtime_gate_ready": (
            decision[
                "runtime_gate"
            ]["ready"]
        ),
        "ledger_healthy": bool(
            decision[
                "ledger_health"
            ].get(
                "healthy"
            )
        ),
        "automatic_restore": False,
        "automatic_cleanup": False,
        "activation_performed": False,
        "direct_vault_write": False,
    }

    return persist_record(
        prefix="obstartupgate",
        payload=source,
        directory_override=directory_override,
    )


def backup_cadence_enforcement_preview(
    *,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
) -> Dict[str, Any]:
    inventory = backup_rotation_inventory(
        backup_override=backup_override
    )

    newest = inventory.get(
        "newest_verified_backup"
    )

    action_required = not inventory[
        "cadence_ready"
    ]

    if action_required:
        recommendation = (
            "OWNER_CREATE_VERIFIED_BACKUP"
        )
    else:
        recommendation = (
            "NO_BACKUP_ACTION_REQUIRED"
        )

    return {
        "ready": (
            inventory["cadence_ready"]
        ),
        "recommendation": (
            recommendation
        ),
        "maximum_age_hours": (
            inventory[
                "maximum_age_hours"
            ]
        ),
        "newest_verified_backup": newest,
        "verified_backup_count": (
            inventory[
                "verified_backup_count"
            ]
        ),
        "backup_count": (
            inventory["backup_count"]
        ),
        "automatic_backup_created": False,
        "automatic_backup_deleted": False,
        "owner_action_required": (
            action_required
        ),
        "direct_vault_write": False,
    }


def create_restore_drill_evidence(
    *,
    owner_id: str,
    backup_path: str | Path,
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    drill = controlled_restore_drill(
        backup_path=backup_path
    )

    source = {
        "receipt_type": (
            "tower_ob_restore_drill"
        ),
        "owner_id": owner_id,
        "created_at": (
            utc_now().isoformat()
        ),
        "backup_path": str(
            backup_path
        ),
        "passed": drill[
            "passed"
        ],
        "reason_code": drill[
            "reason_code"
        ],
        "counts": drill.get(
            "counts",
            {},
        ),
        "production_database_replaced": False,
        "automatic_restore": False,
        "direct_vault_write": False,
    }

    return persist_record(
        prefix="obrestoredrill",
        payload=source,
        directory_override=directory_override,
    )


def create_retention_owner_decision(
    *,
    owner_id: str,
    approval_id: str,
    decision: str,
    rationale: str,
    approval_directory_override: str | Path | None = None,
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    normalized_decision = (
        str(decision)
        .strip()
        .lower()
    )

    if normalized_decision not in {
        "approve",
        "reject",
        "defer",
    }:
        raise ValueError(
            "Decision must be approve, reject, or defer"
        )

    approvals = list_retention_approval_records(
        approval_directory_override=(
            approval_directory_override
        )
    )

    selected = next(
        (
            record
            for record in approvals
            if record.get(
                "approval_id"
            ) == approval_id
        ),
        None,
    )

    if selected is None:
        raise ValueError(
            "Retention approval record not found"
        )

    source = {
        "receipt_type": (
            "tower_ob_retention_owner_decision"
        ),
        "owner_id": owner_id,
        "approval_id": approval_id,
        "created_at": (
            utc_now().isoformat()
        ),
        "decision": normalized_decision,
        "rationale": str(
            rationale
        )[:2000],
        "eligible_count": (
            selected.get(
                "eligible_count",
                0,
            )
        ),
        "eligible_walkthrough_ids": (
            selected.get(
                "eligible_walkthrough_ids",
                [],
            )
        ),
        "cleanup_performed": False,
        "cleanup_authorized_by_this_receipt": False,
        "separate_cleanup_execution_required": (
            normalized_decision
            == "approve"
        ),
        "in_progress_runs_selected": False,
        "direct_vault_write": False,
    }

    return persist_record(
        prefix="obretentiondecision",
        payload=source,
        directory_override=directory_override,
    )


def storage_incident_review_queue(
    *,
    incident_directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    directory = configured_incident_directory(
        incident_directory_override
    )

    records: List[Dict[str, Any]] = []

    if directory.exists():
        for path in sorted(
            directory.glob(
                "obstorageincident_*.json"
            ),
            key=lambda item: (
                item.stat().st_mtime
            ),
            reverse=True,
        ):
            try:
                payload = json.loads(
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
                **payload,
                "record_path": str(
                    path
                ),
            })

    open_records = [
        record
        for record in records
        if record.get(
            "status"
        ) == "open"
    ]

    critical_open = [
        record
        for record in open_records
        if record.get(
            "severity"
        ) == "critical"
    ]

    return {
        "incident_directory": str(
            directory
        ),
        "record_count": len(
            records
        ),
        "open_count": len(
            open_records
        ),
        "critical_open_count": len(
            critical_open
        ),
        "records": records,
        "activation_blocked_by_critical_incident": (
            bool(
                critical_open
            )
        ),
        "automatic_resolution": False,
        "direct_vault_write": False,
    }


def create_incident_review_receipt(
    *,
    owner_id: str,
    incident_id: str,
    decision: str,
    note: str,
    incident_directory_override: str | Path | None = None,
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    queue = storage_incident_review_queue(
        incident_directory_override=(
            incident_directory_override
        )
    )

    incident = next(
        (
            record
            for record in queue[
                "records"
            ]
            if record.get(
                "incident_id"
            ) == incident_id
        ),
        None,
    )

    if incident is None:
        raise ValueError(
            "Storage incident not found"
        )

    normalized_decision = (
        str(decision)
        .strip()
        .lower()
    )

    if normalized_decision not in {
        "acknowledge",
        "hold",
        "resolve",
    }:
        raise ValueError(
            "Unsupported incident review decision"
        )

    source = {
        "receipt_type": (
            "tower_ob_storage_incident_review"
        ),
        "owner_id": owner_id,
        "incident_id": incident_id,
        "created_at": (
            utc_now().isoformat()
        ),
        "decision": (
            normalized_decision
        ),
        "note": str(
            note
        )[:2000],
        "incident_severity": (
            incident.get(
                "severity"
            )
        ),
        "incident_type": (
            incident.get(
                "incident_type"
            )
        ),
        "incident_record_modified": False,
        "automatic_resolution": False,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
    }

    return persist_record(
        prefix="obincidentreview",
        payload=source,
        directory_override=directory_override,
    )


def operations_release_evidence_packet(
    *,
    owner_id: str,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
) -> Dict[str, Any]:
    manifest = hosted_deployment_manifest(
        database_override=database_override,
        backup_override=backup_override,
    )

    startup = startup_fail_closed_decision(
        database_override=database_override,
        backup_override=backup_override,
    )

    assurance = hosted_operations_readiness(
        database_override=database_override,
        backup_override=backup_override,
    )

    backup = backup_cadence_enforcement_preview(
        database_override=database_override,
        backup_override=backup_override,
    )

    incidents = storage_incident_review_queue()

    checks = {
        "manifest_ready": (
            manifest["ready"]
        ),
        "startup_allowed": (
            startup["allowed"]
        ),
        "hosted_assurance_ready": (
            assurance["ready"]
        ),
        "backup_cadence_ready": (
            backup["ready"]
        ),
        "no_critical_open_incidents": (
            incidents[
                "critical_open_count"
            ]
            == 0
        ),
        "fail_closed": (
            startup["fail_closed"]
        ),
        "automatic_restore_disabled": (
            assurance[
                "automatic_restore"
            ]
            is False
        ),
        "automatic_cleanup_disabled": (
            assurance[
                "automatic_cleanup"
            ]
            is False
        ),
    }

    ready = all(
        checks.values()
    )

    packet = {
        "packet_type": (
            "tower_ob_hosted_release_evidence"
        ),
        "owner_id": owner_id,
        "created_at": (
            utc_now().isoformat()
        ),
        "ready": ready,
        "checks": checks,
        "manifest": manifest,
        "startup": startup,
        "assurance": assurance,
        "backup": backup,
        "incident_summary": {
            "record_count": (
                incidents[
                    "record_count"
                ]
            ),
            "open_count": (
                incidents[
                    "open_count"
                ]
            ),
            "critical_open_count": (
                incidents[
                    "critical_open_count"
                ]
            ),
        },
        "activation_performed": False,
        "production_database_replaced": False,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
        "public_link_created": False,
    }

    packet["packet_hash"] = (
        payload_hash(
            packet
        )
    )

    return packet


def hosted_activation_recommendation(
    *,
    owner_id: str,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
) -> Dict[str, Any]:
    packet = operations_release_evidence_packet(
        owner_id=owner_id,
        database_override=database_override,
        backup_override=backup_override,
    )

    blockers = [
        key
        for key, value
        in packet["checks"].items()
        if value is not True
    ]

    if packet["ready"]:
        recommendation = (
            "GO_OWNER_MAY_APPROVE_HOSTED_ACTIVATION"
        )
    else:
        recommendation = (
            "NO_GO_HOSTED_ACTIVATION_HOLD"
        )

    return {
        "ready": (
            packet["ready"]
        ),
        "recommendation": (
            recommendation
        ),
        "blockers": blockers,
        "packet_hash": (
            packet["packet_hash"]
        ),
        "owner_approval_required": True,
        "activation_performed": False,
        "deployment_command_executed": False,
        "production_database_replaced": False,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
        "public_link_created": False,
    }


def activation_packet_preview(
    *,
    owner_id: str,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    recommendation = (
        hosted_activation_recommendation(
            owner_id=owner_id,
            database_override=database_override,
            backup_override=backup_override,
        )
    )

    source = {
        "packet_type": (
            "tower_ob_hosted_activation_preview"
        ),
        "owner_id": owner_id,
        "created_at": (
            utc_now().isoformat()
        ),
        "recommendation": (
            recommendation[
                "recommendation"
            ]
        ),
        "ready": (
            recommendation["ready"]
        ),
        "blockers": (
            recommendation["blockers"]
        ),
        "release_packet_hash": (
            recommendation[
                "packet_hash"
            ]
        ),
        "owner_approval_required": True,
        "owner_approval_recorded": False,
        "activation_performed": False,
        "deployment_command_executed": False,
        "production_database_replaced": False,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
        "public_link_created": False,
    }

    return persist_record(
        prefix="obactivationpreview",
        payload=source,
        directory_override=directory_override,
    )
