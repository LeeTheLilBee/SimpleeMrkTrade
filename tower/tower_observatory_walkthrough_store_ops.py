"""
Operational controls for the Tower-owned Observatory
guided-run SQLite ledger.

No backup or export is sent to Archive Vault.
No public links are created.
Restore and cleanup require explicit owner action.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from tower.tower_observatory_walkthrough_store import (
    DATABASE_ENVIRONMENT_KEY,
    DEFAULT_DATABASE_PATH,
    SCHEMA_VERSION,
    connection,
    database_path,
    initialize_schema,
    list_owner_runs,
    load_run_evidence,
)


BACKUP_DIRECTORY_ENVIRONMENT_KEY = (
    "TOWER_OB_WALKTHROUGH_BACKUP_DIR"
)

DEFAULT_BACKUP_DIRECTORY = Path(
    "/tmp/simplee_tower_ob_walkthrough_backups"
)

RETENTION_DAYS_ENVIRONMENT_KEY = (
    "TOWER_OB_WALKTHROUGH_RETENTION_DAYS"
)

DEFAULT_RETENTION_DAYS = 365


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


def configured_backup_directory(
    override: str | Path | None = None,
) -> Path:
    if override is not None:
        return Path(override)

    configured = os.environ.get(
        BACKUP_DIRECTORY_ENVIRONMENT_KEY
    )

    if configured:
        return Path(configured)

    return DEFAULT_BACKUP_DIRECTORY


def configured_retention_days() -> int:
    raw = os.environ.get(
        RETENTION_DAYS_ENVIRONMENT_KEY
    )

    if not raw:
        return DEFAULT_RETENTION_DAYS

    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_RETENTION_DAYS

    return max(
        30,
        min(
            value,
            3650,
        ),
    )


def file_sha256(
    path: str | Path,
) -> str:
    digest = hashlib.sha256()

    with Path(path).open(
        "rb"
    ) as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def validate_hosted_configuration(
    *,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
) -> Dict[str, Any]:
    database = database_path(
        database_override
    )

    backup_directory = (
        configured_backup_directory(
            backup_override
        )
    )

    database_parent = (
        database.parent
    )

    checks = {
        "database_path_absolute": (
            database.is_absolute()
        ),
        "backup_path_absolute": (
            backup_directory.is_absolute()
        ),
        "database_not_inside_repository": (
            "/content/SimpleeMrkTrade"
            not in str(database)
        ),
        "backup_not_inside_repository": (
            "/content/SimpleeMrkTrade"
            not in str(
                backup_directory
            )
        ),
        "database_parent_creatable": True,
        "backup_directory_creatable": True,
    }

    try:
        database_parent.mkdir(
            parents=True,
            exist_ok=True,
        )
    except OSError:
        checks[
            "database_parent_creatable"
        ] = False

    try:
        backup_directory.mkdir(
            parents=True,
            exist_ok=True,
        )
    except OSError:
        checks[
            "backup_directory_creatable"
        ] = False

    ready = all(
        checks.values()
    )

    return {
        "ready": ready,
        "database_path": str(
            database
        ),
        "backup_directory": str(
            backup_directory
        ),
        "database_environment_key": (
            DATABASE_ENVIRONMENT_KEY
        ),
        "backup_environment_key": (
            BACKUP_DIRECTORY_ENVIRONMENT_KEY
        ),
        "retention_environment_key": (
            RETENTION_DAYS_ENVIRONMENT_KEY
        ),
        "retention_days": (
            configured_retention_days()
        ),
        "checks": checks,
        "tower_owned_storage": True,
        "direct_vault_write": False,
        "public_links": False,
    }


def inspect_schema(
    *,
    database_override: str | Path | None = None,
) -> Dict[str, Any]:
    path = database_path(
        database_override
    )

    with connection(
        path
    ) as database:
        tables = {
            row["name"]
            for row in database.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()
        }

        required_tables = {
            "guided_runs",
            "guided_room_receipts",
            "guided_final_receipts",
        }

        user_version = database.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

        if user_version == 0:
            database.execute(
                f"PRAGMA user_version = {SCHEMA_VERSION}"
            )

            user_version = SCHEMA_VERSION

    checks = {
        "required_tables_present": (
            required_tables.issubset(
                tables
            )
        ),
        "schema_version_supported": (
            user_version
            <= SCHEMA_VERSION
        ),
        "schema_version_current": (
            user_version
            == SCHEMA_VERSION
        ),
    }

    return {
        "ready": all(
            checks.values()
        ),
        "database_path": str(
            path
        ),
        "schema_version": (
            user_version
        ),
        "supported_schema_version": (
            SCHEMA_VERSION
        ),
        "tables": sorted(
            tables
        ),
        "checks": checks,
    }


def ledger_health_check(
    *,
    database_override: str | Path | None = None,
) -> Dict[str, Any]:
    path = database_path(
        database_override
    )

    schema = inspect_schema(
        database_override=path
    )

    with connection(
        path
    ) as database:
        integrity_rows = database.execute(
            "PRAGMA integrity_check"
        ).fetchall()

        integrity_messages = [
            row[0]
            for row in integrity_rows
        ]

        quick_rows = database.execute(
            "PRAGMA quick_check"
        ).fetchall()

        quick_messages = [
            row[0]
            for row in quick_rows
        ]

        run_count = database.execute(
            """
            SELECT COUNT(*)
            FROM guided_runs
            """
        ).fetchone()[0]

        room_receipt_count = database.execute(
            """
            SELECT COUNT(*)
            FROM guided_room_receipts
            """
        ).fetchone()[0]

        final_receipt_count = database.execute(
            """
            SELECT COUNT(*)
            FROM guided_final_receipts
            """
        ).fetchone()[0]

    checks = {
        "schema_ready": (
            schema["ready"]
        ),
        "integrity_check_ok": (
            integrity_messages
            == ["ok"]
        ),
        "quick_check_ok": (
            quick_messages
            == ["ok"]
        ),
        "database_exists": (
            path.exists()
        ),
    }

    return {
        "healthy": all(
            checks.values()
        ),
        "database_path": str(
            path
        ),
        "checks": checks,
        "schema": schema,
        "integrity_messages": (
            integrity_messages
        ),
        "quick_messages": (
            quick_messages
        ),
        "counts": {
            "runs": run_count,
            "room_receipts": (
                room_receipt_count
            ),
            "final_receipts": (
                final_receipt_count
            ),
        },
        "direct_vault_write": False,
    }


def create_backup_snapshot(
    *,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
    label: str = "manual",
) -> Dict[str, Any]:
    source_path = database_path(
        database_override
    )

    backup_directory = (
        configured_backup_directory(
            backup_override
        )
    )

    backup_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Ensure the source database exists
    # and has the current schema.
    with connection(
        source_path
    ):
        pass

    timestamp = utc_now().strftime(
        "%Y%m%dT%H%M%SZ"
    )

    safe_label = "".join(
        character
        for character in label.lower()
        if character.isalnum()
        or character in {
            "-",
            "_",
        }
    )[:40] or "manual"

    backup_path = (
        backup_directory
        / (
            "tower_ob_walkthrough_"
            f"{timestamp}_{safe_label}.sqlite3"
        )
    )

    with sqlite3.connect(
        source_path
    ) as source_database:
        with sqlite3.connect(
            backup_path
        ) as backup_database:
            source_database.backup(
                backup_database
            )

    integrity = file_sha256(
        backup_path
    )

    manifest = {
        "backup_path": str(
            backup_path
        ),
        "source_path": str(
            source_path
        ),
        "created_at": (
            utc_now().isoformat()
        ),
        "sha256": integrity,
        "size_bytes": (
            backup_path.stat().st_size
        ),
        "schema_version": (
            SCHEMA_VERSION
        ),
        "tower_owned_storage": True,
        "direct_vault_write": False,
        "public_link_created": False,
    }

    manifest_path = backup_path.with_suffix(
        ".manifest.json"
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "created": True,
        "backup_path": str(
            backup_path
        ),
        "manifest_path": str(
            manifest_path
        ),
        "manifest": manifest,
    }


def verify_backup_snapshot(
    backup_path: str | Path,
) -> Dict[str, Any]:
    path = Path(
        backup_path
    )

    manifest_path = path.with_suffix(
        ".manifest.json"
    )

    if (
        not path.exists()
        or not manifest_path.exists()
    ):
        return {
            "verified": False,
            "reason_code": (
                "tower_ob_backup_missing"
            ),
        }

    manifest = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )

    actual_hash = file_sha256(
        path
    )

    try:
        with sqlite3.connect(
            path
        ) as database:
            integrity = [
                row[0]
                for row in database.execute(
                    "PRAGMA integrity_check"
                ).fetchall()
            ]
    except sqlite3.DatabaseError as exc:
        return {
            "verified": False,
            "reason_code": (
                "tower_ob_backup_database_invalid"
            ),
            "error": str(exc),
        }

    checks = {
        "hash_matches": (
            actual_hash
            == manifest.get(
                "sha256"
            )
        ),
        "integrity_ok": (
            integrity == ["ok"]
        ),
        "schema_version_supported": (
            int(
                manifest.get(
                    "schema_version",
                    0,
                )
            )
            <= SCHEMA_VERSION
        ),
    }

    return {
        "verified": all(
            checks.values()
        ),
        "reason_code": (
            "tower_ob_backup_verified"
            if all(
                checks.values()
            )
            else (
                "tower_ob_backup_verification_failed"
            )
        ),
        "backup_path": str(
            path
        ),
        "manifest_path": str(
            manifest_path
        ),
        "stored_sha256": (
            manifest.get(
                "sha256"
            )
        ),
        "actual_sha256": (
            actual_hash
        ),
        "integrity_messages": (
            integrity
        ),
        "checks": checks,
    }


def restore_preview(
    *,
    backup_path: str | Path,
    destination_override: str | Path | None = None,
) -> Dict[str, Any]:
    verification = (
        verify_backup_snapshot(
            backup_path
        )
    )

    destination = database_path(
        destination_override
    )

    return {
        "ready": (
            verification[
                "verified"
            ]
        ),
        "verification": verification,
        "source_backup_path": str(
            Path(
                backup_path
            )
        ),
        "destination_database_path": str(
            destination
        ),
        "destination_exists": (
            destination.exists()
        ),
        "replacement_required": (
            destination.exists()
        ),
        "automatic_restore_performed": False,
        "explicit_owner_action_required": True,
        "direct_vault_write": False,
    }


def execute_controlled_restore(
    *,
    backup_path: str | Path,
    destination_override: str | Path | None = None,
    explicit_owner_confirmation: bool,
) -> Dict[str, Any]:
    preview = restore_preview(
        backup_path=backup_path,
        destination_override=destination_override,
    )

    if not explicit_owner_confirmation:
        return {
            **preview,
            "restored": False,
            "reason_code": (
                "tower_ob_restore_owner_confirmation_required"
            ),
        }

    if not preview["ready"]:
        return {
            **preview,
            "restored": False,
            "reason_code": (
                "tower_ob_restore_backup_not_verified"
            ),
        }

    source = Path(
        backup_path
    )

    destination = database_path(
        destination_override
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    safety_backup = None

    if destination.exists():
        safety_backup = (
            destination.with_suffix(
                ".pre_restore.sqlite3"
            )
        )

        shutil.copy2(
            destination,
            safety_backup,
        )

    temporary_destination = (
        destination.with_suffix(
            ".restore_tmp.sqlite3"
        )
    )

    shutil.copy2(
        source,
        temporary_destination,
    )

    temporary_verification = (
        ledger_health_check(
            database_override=(
                temporary_destination
            )
        )
    )

    if not temporary_verification[
        "healthy"
    ]:
        temporary_destination.unlink(
            missing_ok=True
        )

        return {
            **preview,
            "restored": False,
            "reason_code": (
                "tower_ob_restore_temporary_copy_invalid"
            ),
            "temporary_health": (
                temporary_verification
            ),
        }

    temporary_destination.replace(
        destination
    )

    final_health = ledger_health_check(
        database_override=destination
    )

    return {
        **preview,
        "restored": (
            final_health[
                "healthy"
            ]
        ),
        "reason_code": (
            "tower_ob_restore_completed"
            if final_health[
                "healthy"
            ]
            else (
                "tower_ob_restore_final_health_failed"
            )
        ),
        "safety_backup_path": (
            str(
                safety_backup
            )
            if safety_backup
            else None
        ),
        "final_health": final_health,
    }


def retention_preview(
    *,
    owner_id: str,
    retention_days: int | None = None,
    database_override: str | Path | None = None,
) -> Dict[str, Any]:
    days = (
        configured_retention_days()
        if retention_days is None
        else max(
            30,
            min(
                int(
                    retention_days
                ),
                3650,
            ),
        )
    )

    cutoff = utc_now() - timedelta(
        days=days
    )

    runs = list_owner_runs(
        owner_id=owner_id,
        limit=200,
        override=database_override,
    )

    eligible = []

    retained = []

    for run in runs:
        updated = datetime.fromisoformat(
            run["updated_at"]
        )

        if (
            run["status"]
            == "completed"
            and updated < cutoff
        ):
            eligible.append(
                run
            )
        else:
            retained.append(
                run
            )

    return {
        "owner_id": owner_id,
        "retention_days": days,
        "cutoff": cutoff.isoformat(),
        "eligible_count": len(
            eligible
        ),
        "eligible_runs": eligible,
        "retained_count": len(
            retained
        ),
        "automatic_deletion_performed": False,
        "explicit_owner_action_required": True,
        "in_progress_runs_never_selected": all(
            run["status"] == "completed"
            for run in eligible
        ),
    }


def execute_retention_cleanup(
    *,
    owner_id: str,
    walkthrough_ids: List[str],
    explicit_owner_confirmation: bool,
    database_override: str | Path | None = None,
) -> Dict[str, Any]:
    if not explicit_owner_confirmation:
        return {
            "deleted": False,
            "deleted_count": 0,
            "reason_code": (
                "tower_ob_retention_owner_confirmation_required"
            ),
        }

    requested = {
        str(
            walkthrough_id
        )
        for walkthrough_id
        in walkthrough_ids
        if str(
            walkthrough_id
        ).strip()
    }

    deleted = []

    with connection(
        database_override
    ) as database:
        for walkthrough_id in sorted(
            requested
        ):
            row = database.execute(
                """
                SELECT status
                FROM guided_runs
                WHERE owner_id = ?
                  AND walkthrough_id = ?
                """,
                (
                    owner_id,
                    walkthrough_id,
                ),
            ).fetchone()

            if (
                row is None
                or row["status"]
                != "completed"
            ):
                continue

            database.execute(
                """
                DELETE FROM guided_runs
                WHERE owner_id = ?
                  AND walkthrough_id = ?
                """,
                (
                    owner_id,
                    walkthrough_id,
                ),
            )

            deleted.append(
                walkthrough_id
            )

    return {
        "deleted": bool(
            deleted
        ),
        "deleted_count": len(
            deleted
        ),
        "deleted_walkthrough_ids": (
            deleted
        ),
        "in_progress_runs_deleted": False,
        "explicit_owner_confirmation": True,
    }


def owner_export_preview(
    *,
    owner_id: str,
    walkthrough_id: str,
    database_override: str | Path | None = None,
) -> Dict[str, Any]:
    evidence = load_run_evidence(
        owner_id=owner_id,
        walkthrough_id=walkthrough_id,
        override=database_override,
    )

    if evidence is None:
        return {
            "available": False,
            "reason_code": (
                "tower_ob_export_run_not_found"
            ),
        }

    export_payload = {
        "export_type": (
            "tower_ob_guided_run_evidence_preview"
        ),
        "owner_id": owner_id,
        "walkthrough_id": (
            walkthrough_id
        ),
        "generated_at": (
            utc_now().isoformat()
        ),
        "evidence": evidence,
        "public_link_created": False,
        "direct_vault_write": False,
        "preview_only": True,
    }

    return {
        "available": True,
        "export_payload": (
            export_payload
        ),
        "export_sha256": hashlib.sha256(
            json.dumps(
                export_payload,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
        "file_written": False,
        "public_link_created": False,
        "direct_vault_write": False,
    }


def corruption_recovery_assessment(
    *,
    database_override: str | Path | None = None,
    backup_override: str | Path | None = None,
) -> Dict[str, Any]:
    health = ledger_health_check(
        database_override=database_override
    )

    backup_directory = (
        configured_backup_directory(
            backup_override
        )
    )

    candidates = sorted(
        backup_directory.glob(
            "*.sqlite3"
        ),
        key=lambda path: (
            path.stat().st_mtime
        ),
        reverse=True,
    ) if backup_directory.exists() else []

    verified_backups = []

    for candidate in candidates[:20]:
        verification = (
            verify_backup_snapshot(
                candidate
            )
        )

        if verification[
            "verified"
        ]:
            verified_backups.append(
                verification
            )

    if health["healthy"]:
        recommendation = (
            "NO_RECOVERY_REQUIRED"
        )

    elif verified_backups:
        recommendation = (
            "OWNER_REVIEW_VERIFIED_BACKUP_RESTORE"
        )

    else:
        recommendation = (
            "NO_GO_NO_VERIFIED_RECOVERY_SOURCE"
        )

    return {
        "database_healthy": (
            health["healthy"]
        ),
        "health": health,
        "verified_backup_count": len(
            verified_backups
        ),
        "verified_backups": (
            verified_backups
        ),
        "recommendation": (
            recommendation
        ),
        "automatic_restore_performed": False,
        "explicit_owner_action_required": True,
        "direct_vault_write": False,
    }
