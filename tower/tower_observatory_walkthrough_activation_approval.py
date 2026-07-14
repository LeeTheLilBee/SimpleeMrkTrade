"""
Tower Observatory hosted activation owner approval boundary.

This layer creates reviewable owner approval evidence while
keeping production activation explicitly disabled.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

from tower.tower_observatory_walkthrough_deployment_boundary import (
    activation_packet_preview,
    deployment_environment_name,
    deployment_record_directory,
    hosted_activation_recommendation,
    operations_release_evidence_packet,
    persist_record,
)
from tower.tower_observatory_walkthrough_hosted_assurance import (
    backup_rotation_inventory,
)
from tower.tower_observatory_walkthrough_store import (
    database_path,
)
from tower.tower_observatory_walkthrough_store_ops import (
    configured_backup_directory,
    ledger_health_check,
)


ACTIVATION_APPROVAL_DIRECTORY_ENVIRONMENT_KEY = (
    "TOWER_OB_WALKTHROUGH_ACTIVATION_APPROVAL_DIR"
)

DEFAULT_ACTIVATION_APPROVAL_DIRECTORY = Path(
    "/tmp/"
    "simplee_tower_ob_walkthrough_activation_approvals"
)

ACTIVATION_COMMAND_TEMPLATE_ENVIRONMENT_KEY = (
    "TOWER_OB_WALKTHROUGH_ACTIVATION_COMMAND_TEMPLATE"
)

DEFAULT_ACTIVATION_COMMAND_TEMPLATE = (
    "hosted-platform release "
    "--service tower "
    "--component observatory-walkthrough-persistence"
)


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


def canonical_json(
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
        canonical_json(
            payload
        ).encode("utf-8")
    ).hexdigest()


def approval_directory(
    override: str | Path | None = None,
) -> Path:
    if override is not None:
        return Path(override)

    configured = os.environ.get(
        ACTIVATION_APPROVAL_DIRECTORY_ENVIRONMENT_KEY
    )

    if configured:
        return Path(configured)

    return DEFAULT_ACTIVATION_APPROVAL_DIRECTORY


def activation_command_template() -> str:
    configured = os.environ.get(
        ACTIVATION_COMMAND_TEMPLATE_ENVIRONMENT_KEY
    )

    if configured:
        return configured.strip()

    return DEFAULT_ACTIVATION_COMMAND_TEMPLATE


def persist_approval_record(
    *,
    prefix: str,
    payload: Dict[str, Any],
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    directory = approval_directory(
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
        prefix
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


def activation_scope_freeze(
    *,
    owner_id: str,
) -> Dict[str, Any]:
    release_packet = (
        operations_release_evidence_packet(
            owner_id=owner_id
        )
    )

    scope = {
        "environment": (
            deployment_environment_name()
        ),
        "component": (
            "observatory_walkthrough_persistence"
        ),
        "database_path": str(
            database_path()
        ),
        "backup_directory": str(
            configured_backup_directory()
        ),
        "release_packet_hash": (
            release_packet[
                "packet_hash"
            ]
        ),
        "allowed_operations": [
            "bind_hosted_environment",
            "enable_guided_run_persistence_startup",
            "enable_backup_cadence_checks",
            "enable_owner_operations_views",
        ],
        "prohibited_operations": [
            "broker_submission",
            "capital_movement",
            "manual_live_activation",
            "live_auto_activation",
            "direct_vault_write",
            "public_link_creation",
            "automatic_restore",
            "automatic_cleanup",
        ],
        "production_database_replacement": False,
        "activation_execution": False,
    }

    scope["scope_hash"] = payload_hash(
        scope
    )

    return scope


def create_activation_approval_request(
    *,
    owner_id: str,
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    recommendation = (
        hosted_activation_recommendation(
            owner_id=owner_id
        )
    )

    scope = activation_scope_freeze(
        owner_id=owner_id
    )

    source = {
        "record_type": (
            "tower_ob_activation_approval_request"
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
        "recommendation_ready": (
            recommendation["ready"]
        ),
        "release_packet_hash": (
            recommendation[
                "packet_hash"
            ]
        ),
        "scope_hash": (
            scope["scope_hash"]
        ),
        "step_up_required": True,
        "owner_decision_required": True,
        "approval_status": "pending",
        "activation_performed": False,
        "deployment_command_executed": False,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
    }

    return persist_approval_record(
        prefix="obactivationrequest",
        payload=source,
        directory_override=directory_override,
    )


def create_step_up_challenge(
    *,
    owner_id: str,
    approval_request_id: str,
    valid_minutes: int = 15,
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    safe_minutes = max(
        5,
        min(
            int(valid_minutes),
            60,
        ),
    )

    created_at = utc_now()

    expires_at = (
        created_at
        + timedelta(
            minutes=safe_minutes
        )
    )

    source = {
        "record_type": (
            "tower_ob_activation_step_up_challenge"
        ),
        "owner_id": owner_id,
        "approval_request_id": (
            approval_request_id
        ),
        "challenge_nonce": (
            secrets.token_urlsafe(
                18
            )
        ),
        "created_at": (
            created_at.isoformat()
        ),
        "expires_at": (
            expires_at.isoformat()
        ),
        "valid_minutes": (
            safe_minutes
        ),
        "required_assurance": (
            "owner_step_up_verified"
        ),
        "verification_status": (
            "awaiting_external_step_up"
        ),
        "credential_material_stored": False,
        "activation_performed": False,
    }

    return persist_approval_record(
        prefix="obstepupchallenge",
        payload=source,
        directory_override=directory_override,
    )


def create_step_up_evidence_receipt(
    *,
    owner_id: str,
    approval_request_id: str,
    challenge_id: str,
    externally_verified: bool,
    verification_method: str,
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    source = {
        "record_type": (
            "tower_ob_activation_step_up_evidence"
        ),
        "owner_id": owner_id,
        "approval_request_id": (
            approval_request_id
        ),
        "challenge_id": challenge_id,
        "created_at": (
            utc_now().isoformat()
        ),
        "externally_verified": bool(
            externally_verified
        ),
        "verification_method": str(
            verification_method
        )[:200],
        "credential_material_stored": False,
        "verification_secret_stored": False,
        "activation_performed": False,
    }

    return persist_approval_record(
        prefix="obstepupevidence",
        payload=source,
        directory_override=directory_override,
    )


def activation_window_preview(
    *,
    requested_start: str,
    duration_minutes: int = 30,
) -> Dict[str, Any]:
    start = datetime.fromisoformat(
        requested_start
    )

    if start.tzinfo is None:
        raise ValueError(
            "Activation window start must include timezone"
        )

    safe_duration = max(
        15,
        min(
            int(duration_minutes),
            120,
        ),
    )

    end = start + timedelta(
        minutes=safe_duration
    )

    now = utc_now()

    checks = {
        "start_is_future": (
            start > now
        ),
        "duration_supported": (
            15
            <= safe_duration
            <= 120
        ),
        "timezone_present": (
            start.tzinfo is not None
        ),
    }

    return {
        "ready": all(
            checks.values()
        ),
        "requested_start": (
            start.isoformat()
        ),
        "requested_end": (
            end.isoformat()
        ),
        "duration_minutes": (
            safe_duration
        ),
        "checks": checks,
        "window_opened": False,
        "activation_performed": False,
    }


def rollback_readiness_receipt(
    *,
    owner_id: str,
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    health = ledger_health_check()

    backups = backup_rotation_inventory()

    newest = backups.get(
        "newest_verified_backup"
    )

    readiness_checks = {
        "ledger_healthy": (
            health["healthy"]
        ),
        "verified_backup_available": (
            newest is not None
        ),
        "backup_cadence_ready": (
            backups["cadence_ready"]
        ),
    }

    safety_checks = {
        "production_database_replacement_planned": False,
        "automatic_restore_disabled": True,
    }

    ready = all(
        readiness_checks.values()
    ) and all([
        safety_checks[
            "production_database_replacement_planned"
        ] is False,
        safety_checks[
            "automatic_restore_disabled"
        ] is True,
    ])

    checks = {
        **readiness_checks,
        **safety_checks,
    }

    source = {
        "record_type": (
            "tower_ob_activation_rollback_readiness"
        ),
        "owner_id": owner_id,
        "created_at": (
            utc_now().isoformat()
        ),
        "ready": ready,
        "checks": checks,
        "newest_verified_backup": newest,
        "rollback_execution_performed": False,
        "production_database_replaced": False,
        "automatic_restore": False,
    }

    return persist_approval_record(
        prefix="obrollbackready",
        payload=source,
        directory_override=directory_override,
    )


def deployment_command_dry_run(
    *,
    owner_id: str,
    scope_hash: str,
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    command = activation_command_template()

    source = {
        "record_type": (
            "tower_ob_activation_command_dry_run"
        ),
        "owner_id": owner_id,
        "created_at": (
            utc_now().isoformat()
        ),
        "scope_hash": scope_hash,
        "command_template": command,
        "rendered_command": (
            command
            + " --scope-hash "
            + scope_hash
        ),
        "dry_run": True,
        "command_executed": False,
        "activation_performed": False,
        "shell_invoked": False,
        "production_database_replaced": False,
    }

    return persist_approval_record(
        prefix="obcommanddryrun",
        payload=source,
        directory_override=directory_override,
    )


def create_owner_approval_decision(
    *,
    owner_id: str,
    approval_request_id: str,
    decision: str,
    rationale: str,
    step_up_verified: bool,
    frozen_scope_hash: str,
    submitted_scope_hash: str,
    activation_window_ready: bool,
    rollback_ready: bool,
    directory_override: str | Path | None = None,
) -> Dict[str, Any]:
    normalized = (
        str(decision)
        .strip()
        .lower()
    )

    if normalized not in {
        "approve",
        "reject",
        "defer",
    }:
        raise ValueError(
            "Decision must be approve, reject, or defer"
        )

    scope_matches = (
        frozen_scope_hash
        == submitted_scope_hash
    )

    approval_requirements_met = all([
        bool(
            step_up_verified
        ),
        scope_matches,
        bool(
            activation_window_ready
        ),
        bool(
            rollback_ready
        ),
    ])

    valid_approval = all([
        normalized == "approve",
        approval_requirements_met,
    ])

    if normalized == "approve" and not valid_approval:
        effective_decision = (
            "hold_requirements_not_met"
        )
    else:
        effective_decision = normalized

    source = {
        "record_type": (
            "tower_ob_activation_owner_decision"
        ),
        "owner_id": owner_id,
        "approval_request_id": (
            approval_request_id
        ),
        "created_at": (
            utc_now().isoformat()
        ),
        "submitted_decision": normalized,
        "effective_decision": (
            effective_decision
        ),
        "rationale": str(
            rationale
        )[:2000],
        "step_up_verified": bool(
            step_up_verified
        ),
        "scope_matches": (
            scope_matches
        ),
        "activation_window_ready": bool(
            activation_window_ready
        ),
        "rollback_ready": bool(
            rollback_ready
        ),
        "approval_requirements_met": (
            approval_requirements_met
        ),
        "valid_owner_approval": (
            valid_approval
        ),
        "activation_authorized_for_future_execution": (
            valid_approval
        ),
        "activation_performed": False,
        "deployment_command_executed": False,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
    }

    return persist_approval_record(
        prefix="obownerdecision",
        payload=source,
        directory_override=directory_override,
    )


def activation_execution_hold(
    *,
    owner_id: str,
    owner_decision: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    valid_approval = bool(
        owner_decision
        and owner_decision.get(
            "valid_owner_approval"
        )
    )

    return {
        "owner_id": owner_id,
        "hold_active": True,
        "reason_code": (
            "tower_ob_activation_execution_separate_corridor_required"
        ),
        "valid_owner_approval_present": (
            valid_approval
        ),
        "activation_performed": False,
        "deployment_command_executed": False,
        "production_database_replaced": False,
        "automatic_restore": False,
        "automatic_cleanup": False,
        "direct_vault_write": False,
    }


def owner_approval_readiness(
    *,
    owner_id: str,
) -> Dict[str, Any]:
    release = hosted_activation_recommendation(
        owner_id=owner_id
    )

    scope = activation_scope_freeze(
        owner_id=owner_id
    )

    hold = activation_execution_hold(
        owner_id=owner_id
    )

    checks = {
        "release_recommendation_ready": (
            release["ready"]
        ),
        "scope_hash_present": bool(
            scope["scope_hash"]
        ),
        "owner_approval_required": True,
        "step_up_required": True,
        "execution_hold_active": (
            hold["hold_active"]
        ),
        "activation_not_performed": (
            hold[
                "activation_performed"
            ]
            is False
        ),
    }

    return {
        "ready_for_owner_approval_process": (
            all(
                checks.values()
            )
        ),
        "checks": checks,
        "release_recommendation": (
            release[
                "recommendation"
            ]
        ),
        "scope_hash": (
            scope["scope_hash"]
        ),
        "execution_hold": hold,
        "activation_performed": False,
        "deployment_command_executed": False,
        "owner_approval_recorded": False,
        "next_action": (
            "OWNER_REVIEW_AND_STEP_UP"
        ),
    }
