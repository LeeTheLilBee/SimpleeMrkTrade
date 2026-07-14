import os
from datetime import datetime, timedelta, timezone

from tower.tower_observatory_walkthrough_activation_approval import (
    activation_execution_hold,
    activation_scope_freeze,
    activation_window_preview,
    create_activation_approval_request,
    create_owner_approval_decision,
    create_step_up_challenge,
    create_step_up_evidence_receipt,
    deployment_command_dry_run,
    owner_approval_readiness,
    rollback_readiness_receipt,
)
from tower.tower_observatory_walkthrough_store import (
    save_guided_progress,
)
from tower.tower_observatory_walkthrough_store_ops import (
    create_backup_snapshot,
)


def configure(tmp_path):
    database = (
        tmp_path / "ledger.sqlite3"
    )

    backups = (
        tmp_path / "backups"
    )

    records = (
        tmp_path / "deployment"
    )

    approvals = (
        tmp_path / "approval"
    )

    incidents = (
        tmp_path / "incidents"
    )

    retention = (
        tmp_path / "retention"
    )

    os.environ[
        "TOWER_OB_WALKTHROUGH_DB"
    ] = str(database)

    os.environ[
        "TOWER_OB_WALKTHROUGH_BACKUP_DIR"
    ] = str(backups)

    os.environ[
        "TOWER_OB_WALKTHROUGH_DEPLOYMENT_RECORD_DIR"
    ] = str(records)

    os.environ[
        "TOWER_OB_WALKTHROUGH_ACTIVATION_APPROVAL_DIR"
    ] = str(approvals)

    os.environ[
        "TOWER_OB_WALKTHROUGH_INCIDENT_DIR"
    ] = str(incidents)

    os.environ[
        "TOWER_OB_WALKTHROUGH_RETENTION_APPROVAL_DIR"
    ] = str(retention)

    os.environ[
        "TOWER_DEPLOYMENT_ENVIRONMENT"
    ] = "staging"

    os.environ[
        "TOWER_HOSTED_MODE"
    ] = "true"

    os.environ[
        "TOWER_OB_WALKTHROUGH_BACKUP_MAX_AGE_HOURS"
    ] = "24"

    progress = {
        "walkthrough_id": (
            "obwalk_activation_test"
        ),
        "guided_mode": True,
        "status": "in_progress",
        "started_at": (
            "2026-07-14T12:00:00+00:00"
        ),
        "updated_at": (
            "2026-07-14T12:05:00+00:00"
        ),
        "completed_room_ids": [],
        "room_receipts": {},
        "next_room_id": (
            "ob_room_dashboard"
        ),
        "completed_count": 0,
        "total_room_count": 6,
        "final_receipt": None,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    save_guided_progress(
        owner_id="owner_test",
        progress=progress,
        override=database,
    )

    create_backup_snapshot(
        database_override=database,
        backup_override=backups,
        label="approval",
    )

    return {
        "database": database,
        "backups": backups,
        "records": records,
        "approvals": approvals,
    }


def test_request_scope_and_step_up(
    tmp_path,
):
    paths = configure(
        tmp_path
    )

    scope = activation_scope_freeze(
        owner_id="owner_test"
    )

    assert scope["scope_hash"]
    assert scope[
        "activation_execution"
    ] is False

    request = create_activation_approval_request(
        owner_id="owner_test",
        directory_override=paths[
            "approvals"
        ],
    )

    assert request["created"] is True
    assert request["record"][
        "step_up_required"
    ] is True
    assert request["record"][
        "activation_performed"
    ] is False

    challenge = create_step_up_challenge(
        owner_id="owner_test",
        approval_request_id=(
            request["record_id"]
        ),
        directory_override=paths[
            "approvals"
        ],
    )

    assert challenge["created"] is True
    assert challenge["record"][
        "credential_material_stored"
    ] is False

    evidence = create_step_up_evidence_receipt(
        owner_id="owner_test",
        approval_request_id=(
            request["record_id"]
        ),
        challenge_id=(
            challenge["record_id"]
        ),
        externally_verified=True,
        verification_method=(
            "tower_mfa_step_up"
        ),
        directory_override=paths[
            "approvals"
        ],
    )

    assert evidence["created"] is True
    assert evidence["record"][
        "externally_verified"
    ] is True
    assert evidence["record"][
        "verification_secret_stored"
    ] is False


def test_window_rollback_and_dry_run(
    tmp_path,
):
    paths = configure(
        tmp_path
    )

    future = (
        datetime.now(
            timezone.utc
        )
        + timedelta(
            hours=2
        )
    )

    window = activation_window_preview(
        requested_start=(
            future.isoformat()
        ),
        duration_minutes=30,
    )

    assert window["ready"] is True
    assert window["window_opened"] is False

    rollback = rollback_readiness_receipt(
        owner_id="owner_test",
        directory_override=paths[
            "approvals"
        ],
    )

    assert rollback["created"] is True
    assert rollback["record"][
        "ready"
    ] is True

    assert rollback["record"][
        "checks"
    ][
        "ledger_healthy"
    ] is True

    assert rollback["record"][
        "checks"
    ][
        "verified_backup_available"
    ] is True

    assert rollback["record"][
        "checks"
    ][
        "backup_cadence_ready"
    ] is True

    assert rollback["record"][
        "checks"
    ][
        "production_database_replacement_planned"
    ] is False

    assert rollback["record"][
        "checks"
    ][
        "automatic_restore_disabled"
    ] is True

    assert rollback["record"][
        "rollback_execution_performed"
    ] is False

    scope = activation_scope_freeze(
        owner_id="owner_test"
    )

    dry_run = deployment_command_dry_run(
        owner_id="owner_test",
        scope_hash=scope[
            "scope_hash"
        ],
        directory_override=paths[
            "approvals"
        ],
    )

    assert dry_run["created"] is True
    assert dry_run["record"][
        "dry_run"
    ] is True
    assert dry_run["record"][
        "command_executed"
    ] is False
    assert dry_run["record"][
        "shell_invoked"
    ] is False


def test_owner_approval_and_execution_hold(
    tmp_path,
):
    paths = configure(
        tmp_path
    )

    scope = activation_scope_freeze(
        owner_id="owner_test"
    )

    decision = create_owner_approval_decision(
        owner_id="owner_test",
        approval_request_id=(
            "obactivationrequest_test"
        ),
        decision="approve",
        rationale=(
            "Evidence reviewed."
        ),
        step_up_verified=True,
        frozen_scope_hash=(
            scope["scope_hash"]
        ),
        submitted_scope_hash=(
            scope["scope_hash"]
        ),
        activation_window_ready=True,
        rollback_ready=True,
        directory_override=paths[
            "approvals"
        ],
    )

    assert decision["created"] is True
    assert decision["record"][
        "valid_owner_approval"
    ] is True
    assert decision["record"][
        "activation_performed"
    ] is False
    assert decision["record"][
        "deployment_command_executed"
    ] is False

    hold = activation_execution_hold(
        owner_id="owner_test",
        owner_decision=(
            decision["record"]
        ),
    )

    assert hold["hold_active"] is True
    assert hold[
        "valid_owner_approval_present"
    ] is True
    assert hold[
        "activation_performed"
    ] is False


def test_invalid_approval_is_held(
    tmp_path,
):
    paths = configure(
        tmp_path
    )

    decision = create_owner_approval_decision(
        owner_id="owner_test",
        approval_request_id=(
            "obactivationrequest_test"
        ),
        decision="approve",
        rationale=(
            "Missing step-up."
        ),
        step_up_verified=False,
        frozen_scope_hash="scope_a",
        submitted_scope_hash="scope_b",
        activation_window_ready=False,
        rollback_ready=False,
        directory_override=paths[
            "approvals"
        ],
    )

    assert decision["record"][
        "valid_owner_approval"
    ] is False

    assert decision["record"][
        "effective_decision"
    ] == "hold_requirements_not_met"

    assert decision["record"][
        "activation_authorized_for_future_execution"
    ] is False


def test_owner_approval_readiness(
    tmp_path,
):
    configure(
        tmp_path
    )

    readiness = owner_approval_readiness(
        owner_id="owner_test"
    )

    assert readiness[
        "ready_for_owner_approval_process"
    ] is True

    assert readiness[
        "execution_hold"
    ]["hold_active"] is True

    assert readiness[
        "activation_performed"
    ] is False

    assert readiness[
        "owner_approval_recorded"
    ] is False
