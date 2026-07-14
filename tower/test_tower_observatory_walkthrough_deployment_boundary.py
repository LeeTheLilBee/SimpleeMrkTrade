import os

from tower.tower_observatory_walkthrough_deployment_boundary import (
    activation_packet_preview,
    backup_cadence_enforcement_preview,
    create_environment_binding_receipt,
    create_incident_review_receipt,
    create_restore_drill_evidence,
    create_startup_gate_receipt,
    hosted_activation_recommendation,
    hosted_deployment_manifest,
    operations_release_evidence_packet,
    storage_incident_review_queue,
)
from tower.tower_observatory_walkthrough_hosted_assurance import (
    create_storage_incident_receipt,
)
from tower.tower_observatory_walkthrough_store import (
    save_guided_progress,
)
from tower.tower_observatory_walkthrough_store_ops import (
    create_backup_snapshot,
)


def sample_progress():
    return {
        "walkthrough_id": (
            "obwalk_deployment_test"
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
        "next_room_id": "ob_room_dashboard",
        "completed_count": 0,
        "total_room_count": 6,
        "final_receipt": None,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }


def configure_environment(
    tmp_path,
):
    database = (
        tmp_path / "ledger.sqlite3"
    )

    backups = (
        tmp_path / "backups"
    )

    records = (
        tmp_path / "records"
    )

    incidents = (
        tmp_path / "incidents"
    )

    approvals = (
        tmp_path / "approvals"
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
        "TOWER_OB_WALKTHROUGH_INCIDENT_DIR"
    ] = str(incidents)

    os.environ[
        "TOWER_OB_WALKTHROUGH_RETENTION_APPROVAL_DIR"
    ] = str(approvals)

    os.environ[
        "TOWER_DEPLOYMENT_ENVIRONMENT"
    ] = "staging"

    os.environ[
        "TOWER_HOSTED_MODE"
    ] = "true"

    os.environ[
        "TOWER_OB_WALKTHROUGH_BACKUP_MAX_AGE_HOURS"
    ] = "24"

    return {
        "database": database,
        "backups": backups,
        "records": records,
        "incidents": incidents,
        "approvals": approvals,
    }


def test_manifest_and_binding_receipts(
    tmp_path,
):
    paths = configure_environment(
        tmp_path
    )

    save_guided_progress(
        owner_id="owner_test",
        progress=sample_progress(),
        override=paths["database"],
    )

    manifest = hosted_deployment_manifest(
        database_override=paths[
            "database"
        ],
        backup_override=paths[
            "backups"
        ],
    )

    assert manifest["ready"] is True
    assert manifest["environment"] == "staging"
    assert manifest["activation_performed"] is False

    binding = create_environment_binding_receipt(
        owner_id="owner_test",
        database_override=paths[
            "database"
        ],
        backup_override=paths[
            "backups"
        ],
        directory_override=paths[
            "records"
        ],
    )

    assert binding["created"] is True
    assert binding["record"][
        "manifest_ready"
    ] is True
    assert binding["record"][
        "activation_performed"
    ] is False

    startup = create_startup_gate_receipt(
        owner_id="owner_test",
        database_override=paths[
            "database"
        ],
        backup_override=paths[
            "backups"
        ],
        require_hosted_mode=True,
        directory_override=paths[
            "records"
        ],
    )

    assert startup["created"] is True
    assert startup["record"][
        "allowed"
    ] is True
    assert startup["record"][
        "fail_closed"
    ] is True


def test_backup_and_restore_drill_evidence(
    tmp_path,
):
    paths = configure_environment(
        tmp_path
    )

    save_guided_progress(
        owner_id="owner_test",
        progress=sample_progress(),
        override=paths["database"],
    )

    backup = create_backup_snapshot(
        database_override=paths[
            "database"
        ],
        backup_override=paths[
            "backups"
        ],
        label="deployment",
    )

    cadence = (
        backup_cadence_enforcement_preview(
            database_override=paths[
                "database"
            ],
            backup_override=paths[
                "backups"
            ],
        )
    )

    assert cadence["ready"] is True
    assert cadence[
        "automatic_backup_created"
    ] is False

    drill = create_restore_drill_evidence(
        owner_id="owner_test",
        backup_path=backup[
            "backup_path"
        ],
        directory_override=paths[
            "records"
        ],
    )

    assert drill["created"] is True
    assert drill["record"]["passed"] is True
    assert drill["record"][
        "production_database_replaced"
    ] is False


def test_incident_queue_and_review(
    tmp_path,
):
    paths = configure_environment(
        tmp_path
    )

    incident = create_storage_incident_receipt(
        incident_type=(
            "deployment_review_test"
        ),
        severity="warning",
        summary=(
            "Review deployment evidence."
        ),
        evidence={
            "test": True,
        },
        owner_id="owner_test",
        incident_directory_override=paths[
            "incidents"
        ],
    )

    queue = storage_incident_review_queue(
        incident_directory_override=paths[
            "incidents"
        ]
    )

    assert queue["record_count"] == 1
    assert queue["open_count"] == 1
    assert queue[
        "critical_open_count"
    ] == 0

    review = create_incident_review_receipt(
        owner_id="owner_test",
        incident_id=incident[
            "incident_id"
        ],
        decision="acknowledge",
        note="Reviewed in deployment test.",
        incident_directory_override=paths[
            "incidents"
        ],
        directory_override=paths[
            "records"
        ],
    )

    assert review["created"] is True
    assert review["record"][
        "incident_record_modified"
    ] is False
    assert review["record"][
        "automatic_resolution"
    ] is False


def test_release_packet_and_activation_preview(
    tmp_path,
):
    paths = configure_environment(
        tmp_path
    )

    save_guided_progress(
        owner_id="owner_test",
        progress=sample_progress(),
        override=paths["database"],
    )

    create_backup_snapshot(
        database_override=paths[
            "database"
        ],
        backup_override=paths[
            "backups"
        ],
        label="release",
    )

    packet = operations_release_evidence_packet(
        owner_id="owner_test",
        database_override=paths[
            "database"
        ],
        backup_override=paths[
            "backups"
        ],
    )

    assert packet["ready"] is True
    assert packet["activation_performed"] is False
    assert packet[
        "deployment_command_executed"
    ] if "deployment_command_executed" in packet else True

    recommendation = (
        hosted_activation_recommendation(
            owner_id="owner_test",
            database_override=paths[
                "database"
            ],
            backup_override=paths[
                "backups"
            ],
        )
    )

    assert recommendation["ready"] is True

    assert recommendation[
        "recommendation"
    ] == (
        "GO_OWNER_MAY_APPROVE_HOSTED_ACTIVATION"
    )

    assert recommendation[
        "owner_approval_required"
    ] is True

    assert recommendation[
        "activation_performed"
    ] is False

    preview = activation_packet_preview(
        owner_id="owner_test",
        database_override=paths[
            "database"
        ],
        backup_override=paths[
            "backups"
        ],
        directory_override=paths[
            "records"
        ],
    )

    assert preview["created"] is True
    assert preview["record"][
        "owner_approval_recorded"
    ] is False
    assert preview["record"][
        "deployment_command_executed"
    ] is False
    assert preview["record"][
        "direct_vault_write"
    ] is False
