from datetime import datetime, timedelta, timezone

from tower.tower_observatory_walkthrough_store import (
    save_guided_progress,
)
from tower.tower_observatory_walkthrough_store_ops import (
    corruption_recovery_assessment,
    create_backup_snapshot,
    execute_controlled_restore,
    execute_retention_cleanup,
    inspect_schema,
    ledger_health_check,
    owner_export_preview,
    restore_preview,
    retention_preview,
    validate_hosted_configuration,
    verify_backup_snapshot,
)


def sample_progress(
    walkthrough_id="obwalk_ops_test",
):
    return {
        "walkthrough_id": walkthrough_id,
        "guided_mode": True,
        "status": "in_progress",
        "started_at": (
            datetime.now(
                timezone.utc
            )
            - timedelta(
                minutes=20
            )
        ).isoformat(),
        "updated_at": (
            datetime.now(
                timezone.utc
            )
        ).isoformat(),
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


def test_configuration_and_schema(
    tmp_path,
):
    database = (
        tmp_path / "ledger.sqlite3"
    )

    backups = (
        tmp_path / "backups"
    )

    configuration = (
        validate_hosted_configuration(
            database_override=database,
            backup_override=backups,
        )
    )

    assert configuration["ready"] is True
    assert configuration[
        "direct_vault_write"
    ] is False

    schema = inspect_schema(
        database_override=database
    )

    assert schema["ready"] is True
    assert schema["schema_version"] == 1


def test_health_backup_and_verification(
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

    health = ledger_health_check(
        database_override=database
    )

    assert health["healthy"] is True
    assert health["counts"]["runs"] == 1

    backup = create_backup_snapshot(
        database_override=database,
        backup_override=backups,
        label="test",
    )

    assert backup["created"] is True

    verification = (
        verify_backup_snapshot(
            backup["backup_path"]
        )
    )

    assert verification["verified"] is True


def test_restore_requires_confirmation(
    tmp_path,
):
    source = (
        tmp_path / "source.sqlite3"
    )

    destination = (
        tmp_path / "destination.sqlite3"
    )

    backups = (
        tmp_path / "backups"
    )

    save_guided_progress(
        owner_id="owner_test",
        progress=sample_progress(),
        override=source,
    )

    backup = create_backup_snapshot(
        database_override=source,
        backup_override=backups,
    )

    preview = restore_preview(
        backup_path=backup["backup_path"],
        destination_override=destination,
    )

    assert preview["ready"] is True
    assert preview[
        "automatic_restore_performed"
    ] is False

    blocked = execute_controlled_restore(
        backup_path=backup["backup_path"],
        destination_override=destination,
        explicit_owner_confirmation=False,
    )

    assert blocked["restored"] is False

    restored = execute_controlled_restore(
        backup_path=backup["backup_path"],
        destination_override=destination,
        explicit_owner_confirmation=True,
    )

    assert restored["restored"] is True


def test_retention_never_deletes_in_progress(
    tmp_path,
):
    database = (
        tmp_path / "ledger.sqlite3"
    )

    save_guided_progress(
        owner_id="owner_test",
        progress=sample_progress(),
        override=database,
    )

    preview = retention_preview(
        owner_id="owner_test",
        retention_days=30,
        database_override=database,
    )

    assert preview["eligible_count"] == 0
    assert preview[
        "automatic_deletion_performed"
    ] is False

    cleanup = execute_retention_cleanup(
        owner_id="owner_test",
        walkthrough_ids=[
            "obwalk_ops_test"
        ],
        explicit_owner_confirmation=True,
        database_override=database,
    )

    assert cleanup["deleted_count"] == 0
    assert cleanup[
        "in_progress_runs_deleted"
    ] is False


def test_export_and_recovery_assessment(
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

    export = owner_export_preview(
        owner_id="owner_test",
        walkthrough_id="obwalk_ops_test",
        database_override=database,
    )

    assert export["available"] is True
    assert export["file_written"] is False
    assert export[
        "public_link_created"
    ] is False
    assert export[
        "direct_vault_write"
    ] is False

    create_backup_snapshot(
        database_override=database,
        backup_override=backups,
    )

    assessment = (
        corruption_recovery_assessment(
            database_override=database,
            backup_override=backups,
        )
    )

    assert assessment[
        "database_healthy"
    ] is True
    assert assessment[
        "recommendation"
    ] == "NO_RECOVERY_REQUIRED"
    assert assessment[
        "automatic_restore_performed"
    ] is False
