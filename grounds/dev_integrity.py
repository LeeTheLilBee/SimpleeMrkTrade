"""GRD061: local development integrity/backup/restore checks; NO hosted infrastructure.

Only use with synthetic developer fixtures. Backups are UNENCRYPTED, local,
explicit and refused when the target path already exists. This is not tenant
retention, production migration, secure cloud backup or a restoration SLA.
Reports contain invariant counts, never resident/lease names or descriptions.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from .storage import GroundsStore


REQUIRED_TABLES=frozenset((
    "properties","buildings","units","leases","lease_members",
    "work_orders","work_events","work_resource_events","work_appointments",
    "event_outbox","inspections","inspection_findings","inspection_resolutions",
    "turnovers","turnover_inspections","turnover_events",
    "property_notices","notice_reads","appointment_events","emergency_reviews",
    "work_entry_preferences","lease_member_events","work_evidence_refs",
    "property_acquisition_receipts","event_delivery_receipts","work_messages",
    "move_task_events","resident_access_events","work_completion_events",
))

# Detect old local developer schemas without treating CREATE TABLE IF NOT EXISTS
# as a migration. Never automatically mutate a database of unknown provenance.
REQUIRED_COLUMNS={
    "leases":("lease_ref","property_ref","unit_ref","resident_ref","status"),
    "lease_members":("lease_ref","property_ref","unit_ref","subject_ref","status"),
    "work_messages":("message_ref","work_ref","property_ref","author_ref","audience"),
    "move_task_events":("event_ref","lease_ref","property_ref","unit_ref",
                        "subject_ref","phase","task_ref","status","revision"),
    "resident_access_events":("access_ref","lease_ref","property_ref","unit_ref",
                             "actor_ref","resource_kind","resource_ref"),
    "work_completion_events":("event_ref","work_ref","property_ref","unit_ref","lease_ref",
                              "resident_ref","outcome","from_revision","to_revision","resulting_state"),
    "work_orders":("work_ref","property_ref","unit_ref","lease_ref","state",
                   "emergency_flag","revision"),
    "property_notices":("notice_ref","property_ref","unit_ref","lease_ref"),
    "notice_reads":("notice_ref","subject_ref","lease_ref","property_ref","unit_ref"),
    "work_appointments":("appointment_ref","work_ref","property_ref","unit_ref",
                         "requested_by","state","revision"),
    "work_resource_events":("event_ref","work_ref","action","resource_type",
                            "reverses_event_ref"),
    "emergency_reviews":("work_ref","reviewed_by","urgency"),
    "turnovers":("turnover_ref","property_ref","unit_ref","lease_ref","state"),
    "turnover_inspections":("turnover_ref","inspection_ref"),
    "property_acquisition_receipts":("handoff_ref","property_ref","opportunity_id",
                                     "opportunity_revision","receipt_digest"),
    "event_delivery_receipts":("receipt_ref","event_ref","property_ref",
                               "receipt_kind","delivery_state","receipt_digest"),
}


class LocalIntegrityError(RuntimeError):
    """No private row values are included in this exception."""


def inspect_local_store(store: GroundsStore) -> dict:
    if not isinstance(store,GroundsStore) or not store.path.is_file():
        raise LocalIntegrityError("existing local Grounds fixture required")
    try:
        with store.transaction() as db:
            tables={row[0] for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'",
            )}
            missing=sorted(REQUIRED_TABLES-tables)
            missing_columns={}
            for table,expected in REQUIRED_COLUMNS.items():
                if table in tables:
                    actual={row["name"] for row in db.execute(
                        'PRAGMA table_info("'+table+'")',
                    )}
                    absent=sorted(set(expected)-actual)
                    if absent:
                        missing_columns[table]=absent
            integrity=[row[0] for row in db.execute("PRAGMA integrity_check")]
            foreign_keys=sum(1 for _ in db.execute("PRAGMA foreign_key_check"))
            checks={
                "occupied_unit_without_active_lease":"""
                    SELECT COUNT(*) FROM units u WHERE lifecycle='occupied' AND
                      NOT EXISTS(SELECT 1 FROM leases l WHERE l.unit_ref=u.unit_ref
                        AND l.property_ref=u.property_ref AND l.status='active')""",
                "active_lease_unit_not_occupied":"""
                    SELECT COUNT(*) FROM leases l JOIN units u ON u.unit_ref=l.unit_ref
                      AND u.property_ref=l.property_ref
                      WHERE l.status='active' AND u.lifecycle!='occupied'""",
                "active_lease_without_primary_member":"""
                    SELECT COUNT(*) FROM leases l WHERE l.status='active'
                      AND NOT EXISTS(SELECT 1 FROM lease_members m
                        WHERE m.lease_ref=l.lease_ref AND m.subject_ref=l.resident_ref
                          AND m.relationship='primary' AND m.status='active')""",
                "ended_lease_with_active_members":"""
                    SELECT COUNT(*) FROM lease_members m JOIN leases l
                      ON l.lease_ref=m.lease_ref WHERE l.status='ended' AND m.status='active'""",
                "wrong_scope_lease_bound_work":"""
                    SELECT COUNT(*) FROM work_orders w JOIN leases l ON l.lease_ref=w.lease_ref
                      WHERE l.property_ref!=w.property_ref OR l.unit_ref!=w.unit_ref""",
                "untriaged_urgent_work_advanced":"""
                    SELECT COUNT(*) FROM work_orders w WHERE w.emergency_flag=1
                      AND w.state!='submitted' AND NOT EXISTS(
                        SELECT 1 FROM emergency_reviews r WHERE r.work_ref=w.work_ref)""",
                "invalid_resource_reversal":"""
                    SELECT COUNT(*) FROM work_resource_events r
                      LEFT JOIN work_resource_events o ON o.event_ref=r.reverses_event_ref
                      WHERE r.action='reverse' AND (
                        o.event_ref IS NULL OR o.action!='record'
                        OR o.work_ref!=r.work_ref OR o.property_ref!=r.property_ref
                        OR o.unit_ref!=r.unit_ref OR o.resource_type!=r.resource_type
                        OR o.label!=r.label OR o.quantity!=r.quantity
                        OR o.quantity_unit!=r.quantity_unit)""",
                "advanced_turnover_missing_linked_closed_inspection":"""
                    SELECT COUNT(*) FROM turnovers t WHERE t.state IN
                      ('work','final_review','complete') AND NOT EXISTS(
                        SELECT 1 FROM turnover_inspections ti
                        JOIN inspections i ON i.inspection_ref=ti.inspection_ref
                        WHERE ti.turnover_ref=t.turnover_ref
                          AND i.property_ref=t.property_ref AND i.unit_ref=t.unit_ref
                          AND i.category='turnover' AND i.state='closed')""",
            }
            issue_counts=({name:db.execute(sql).fetchone()[0] for name,sql in checks.items()}
                          if not missing and not missing_columns else {})
            healthy=(not missing and not missing_columns and integrity==["ok"]
                     and foreign_keys==0
                     and all(count==0 for count in issue_counts.values()))
            return {
                "mode":"local_fixture_only","healthy":healthy,
                "missing_tables":missing,"missing_columns":missing_columns,
                "sqlite_integrity_ok":integrity==["ok"],
                "foreign_key_violations":foreign_keys,
                "domain_issue_counts":issue_counts,
                "migration_certified":False,"production_restore_certified":False,
                "contains_raw_row_data":False,
            }
    except sqlite3.DatabaseError as exc:
        raise LocalIntegrityError("local Grounds fixture cannot be checked") from exc


def make_local_fixture_backup(store: GroundsStore, destination: str|Path) -> dict:
    """Create a new local SQLite copy via online backup API, never overwrite."""
    if not isinstance(store,GroundsStore):
        raise TypeError("GroundsStore required")
    dest=Path(destination)
    if not dest.name or dest.exists() or dest.is_symlink() or not dest.parent.is_dir():
        raise LocalIntegrityError("backup destination must be a new file in an existing directory")
    if store.path.resolve()==dest.resolve():
        raise LocalIntegrityError("cannot overwrite source fixture")
    source_report=inspect_local_store(store)
    if not source_report["healthy"]:
        raise LocalIntegrityError("refusing backup from an inconsistent local fixture")
    created=False
    try:
        # Exclusive creation closes the check-then-open race: another file
        # appearing at destination must never be overwritten or later deleted.
        with dest.open("xb"):
            pass
        created=True
        with sqlite3.connect(str(store.path)) as source:
            with sqlite3.connect(str(dest)) as target:
                source.backup(target)
        dest_report=inspect_local_store(GroundsStore(dest))
        if not dest_report["healthy"]:
            raise LocalIntegrityError("copied local fixture failed integrity validation")
    except Exception as exc:
        if created and dest.is_file():
            dest.unlink()
        if isinstance(exc,LocalIntegrityError):
            raise
        raise LocalIntegrityError("local fixture backup failed") from exc
    return {"mode":"local_fixture_only","backup_created":True,
            "source_integrity_ok":True,"backup_integrity_ok":True,
            "unencrypted_local_copy":True,"production_backup_enabled":False,
            "cloud_upload_occurred":False}
