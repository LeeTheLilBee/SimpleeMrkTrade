from pathlib import Path

from tower.tower_observatory_walkthrough_hosted_assurance import (
    backup_cadence_readiness,
    backup_rotation_inventory,
    controlled_restore_drill,
    create_retention_approval_preview,
    create_storage_incident_receipt,
    export_evidence_review,
    hosted_operations_readiness,
    hosted_runtime_gate,
    startup_fail_closed_decision,
)
from tower.tower_observatory_walkthrough_store import (
    save_guided_progress,
)
from tower.tower_observatory_walkthrough_store_ops import (
    create_backup_snapshot,
)


def sample_progress():
    return {
        "walkthrough_id": "obwalk_assurance_test",
        "guided_mode": True,
        "status": "in_progress",
        "started_at": (
            "2026-07-14T12:00:00+00:00"
        ),
        "updated_at": (
            "2026-07-14T12:10:00+00:00"
        ),
        "completed_room_ids": [],
        "room_receipts": {},
        "next_room_id": "ob_room_dashboard",
        "completed_count": 0,
        "total_room_count": 6,
        "final_receipt": None,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }


def test_runtime_and_startup_gate(
    tmp_path,
):
    database = (
        tmp_path / "ledger.sqlite3"
    )

    backups = (
        tmp_path / "backups"
    )

    runtime = hosted_runtime_gate(
        database_override=database,
        backup_override=backups,
    )

    assert runtime["ready"] is True
    assert runtime[
        "direct_vault_write"
    ] is False

    startup = startup_fail_closed_decision(
        database_override=database,
        backup_override=backups,
    )

    assert startup["allowed"] is True
    assert startup["fail_closed"] is True


def test_backup_inventory_cadence_and_drill(
    tmp_path,
):
    database = (
        tmp_path / "ledger.sqlite3"
    )

    backups = (
        tmp_path / "backups"
    )

    save_guided_progress(
        owner_id="owner_test",
        progress=sample_progress(),
        override=database,
    )

    backup = create_backup_snapshot(
        database_override=database,
        backup_override=backups,
        label="assurance",
    )

    inventory = backup_rotation_inventory(
        backup_override=backups
    )

    assert inventory["backup_count"] == 1
    assert inventory[
        "verified_backup_count"
    ] == 1
    assert inventory["cadence_ready"] is True

    cadence = backup_cadence_readiness(
        database_override=database,
        backup_override=backups,
    )

    assert cadence["ready"] is True

    drill = controlled_restore_drill(
        backup_path=backup[
            "backup_path"
        ]
    )

    assert drill["passed"] is True
    assert drill[
        "production_database_replaced"
    ] is False


def test_retention_approval_and_export_review(
    tmp_path,
):
    database = (
        tmp_path / "ledger.sqlite3"
    )

    approvals = (
        tmp_path / "approvals"
    )

    save_guided_progress(
        owner_id="owner_test",
        progress=sample_progress(),
        override=database,
    )

    approval = (
        create_retention_approval_preview(
            owner_id="owner_test",
            database_override=database,
            approval_directory_override=approvals,
        )
    )

    assert approval["created"] is True
    assert approval[
        "cleanup_performed"
    ] is False
    assert approval[
        "owner_decision_required"
    ] is True

    export_review = (
        export_evidence_review(
            owner_id="owner_test",
            walkthrough_id=(
                "obwalk_assurance_test"
            ),
            database_override=database,
        )
    )

    assert export_review[
        "review_ready"
    ] is True

    assert export_review[
        "room_receipt_count"
    ] == 0

    assert export_review[
        "checks"
    ][
        "room_receipt_count_consistent"
    ] is True

    assert export_review[
        "checks"
    ][
        "completed_run_has_all_room_receipts"
    ] is True

    assert export_review[
        "file_written"
    ] is False
    assert export_review[
        "public_link_created"
    ] is False


def test_incident_receipt(
    tmp_path,
):
    incidents = (
        tmp_path / "incidents"
    )

    receipt = (
        create_storage_incident_receipt(
            incident_type=(
                "backup_cadence_missed"
            ),
            severity="warning",
            summary=(
                "No verified backup inside "
                "the configured cadence."
            ),
            evidence={
                "cadence_ready": False,
            },
            owner_id="owner_test",
            incident_directory_override=incidents,
        )
    )

    assert receipt["created"] is True
    assert receipt[
        "incident_id"
    ].startswith(
        "obstorageincident_"
    )

    assert Path(
        receipt["record_path"]
    ).exists()

    assert receipt["receipt"][
        "automatic_restore"
    ] is False


def test_hosted_readiness(
    tmp_path,
):
    database = (
        tmp_path / "ledger.sqlite3"
    )

    backups = (
        tmp_path / "backups"
    )

    save_guided_progress(
        owner_id="owner_test",
        progress=sample_progress(),
        override=database,
    )

    create_backup_snapshot(
        database_override=database,
        backup_override=backups,
        label="readiness",
    )

    readiness = (
        hosted_operations_readiness(
            database_override=database,
            backup_override=backups,
        )
    )

    assert readiness["ready"] is True

    assert readiness[
        "decision"
    ] == "READY_FOR_HOSTED_PERSISTENCE"

    assert readiness["blockers"] == []
    assert readiness["fail_closed"] is True
    assert readiness[
        "automatic_restore"
    ] is False
