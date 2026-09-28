"""SC014 source-only owner summary of VERIFIED local Cloud journal counts.

Not an authenticated hosted dashboard or notification endpoint. No raw entity,
request tag, object ref, path, provider exception, credential or document body.
An empty LOCAL test journal is never evidence of live operational readiness.
"""
from __future__ import annotations

from .contracts import CloudError
from .journal import SQLiteOperationalJournal


def owner_safe_source_snapshot(journal: SQLiteOperationalJournal) -> dict:
    """Make a bounded action-first summary only from a verified local journal."""
    if not isinstance(journal, SQLiteOperationalJournal):
        raise CloudError("verified Cloud source journal required")
    # Both aggregates are verified within ONE local SQLite read transaction;
    # two separately timed reads could describe different commit positions.
    health, coverage = journal.source_owner_metrics()
    if health["status"] != "SOURCE_ONLY_NO_GO":
        raise CloudError("source journal supplied unexpected runtime state")

    pending_primary = health["pending_writes"]
    pending_backup = health["pending_backups"]
    integrity_primary = health["missing_or_corrupt"]
    integrity_backup = health["backup_missing_or_corrupt"]
    restore_requests = health["restore_request_count"]
    restore_completed = health["restore_completed_count"]
    restore_integrity = health["restore_integrity_hold_count"]
    restore_pending = health["restore_pending_count"]
    restore_pending_without_outage = health["restore_pending_without_outage_count"]
    restore_retryable_outage = health["restore_retryable_outage_count"]
    uncovered = coverage["uncovered_primary_object_count"]
    uncovered_pending = coverage["uncovered_with_pending_backup_count"]
    uncovered_without_pending = coverage["uncovered_without_pending_backup_count"]
    backend_events = health["backend_error_events"]
    restore_integrity_events = health["restore_integrity_incident_events"]
    other_incident_events = (
        health["incident_count"] - backend_events - restore_integrity_events
    )
    values = (
        pending_primary, pending_backup, integrity_primary, integrity_backup,
        backend_events, restore_integrity_events, other_incident_events,
        health["event_count"],
        uncovered, uncovered_pending, uncovered_without_pending,
        restore_requests, restore_completed, restore_integrity, restore_pending,
        restore_pending_without_outage, restore_retryable_outage,
    )
    if any(type(n) is not int or n < 0 for n in values):
        raise CloudError("invalid verified journal metric")

    # This is a fixed local source triage order, NOT a production incident
    # severity assignment. External alert routing and owner acceptance remain
    # independent workstream gates.
    cards = (
        ("primary_integrity", "Primary integrity holds", integrity_primary,
         "Do not release or auto-rewrite. Review the original signed Vault receipt, physical hash and incident."),
        ("backup_integrity", "Backup integrity holds", integrity_backup,
         "Do not declare recovery. Verify the original Vault backup receipt, encrypted copy and independent key."),
        ("restore_integrity", "Restore request integrity holds", restore_integrity,
         "Do not reuse the failed restore request. Repair or investigate the backup, then require a fresh Tower/Vault restore authorization and request ID."),
        ("primary_reconciliation", "Pending primary reconciliations", pending_primary,
         "Use a fresh Tower-authorized reconciliation of the ORIGINAL write ID. Never retry physical PUT automatically."),
        ("backup_reconciliation", "Pending backup reconciliations", pending_backup,
         "Reconcile the ORIGINAL reserved backup ref under a fresh grant. Never silently generate another backup."),
        ("restore_pending", "Pending restore verifications (non-outage)", restore_pending_without_outage,
         "Keep the exact restore binding on HOLD until the bound verification finishes or records an integrity result. Do not infer recoverability from reservation alone."),
        ("backup_coverage", "Acknowledged primary objects without matched backup ACK", uncovered,
         "Review exact Vault-owned source/backup receipt and authorized backup intent. Pending or failed backups cannot count as protected. Physical backup restoration and independent site proof remain unverified."),
        ("backend_outages", "Recorded backend-error events", backend_events,
         "Check provider/service reachability and preserve pending state; outage alone is not proof of lost/corrupt bytes."),
        ("other_incidents", "Other journal incident records", other_incident_events,
         "Review the owning source incident ledger and its independently anchored checkpoint when available."),
    )
    work_queue = [
        {"key": key, "label": label, "count": count, "next_action": action}
        for key, label, count, action in cards if count
    ]
    source_flags = any(count for _, _, count, _ in cards)
    if not source_flags:
        work_queue = [{
            "key": "source_only_external_gates",
            "label": "No flags in this local source-test journal",
            "count": 0,
            "next_action": (
                "Do not infer live health. Tower/Vault identity, offsite custody, "
                "hosted provider, real alerts and owner release remain unverified."
            ),
        }]
    return {
        "schema": "simplee.cloud.owner-safe-source-snapshot.v1",
        "status": "SOURCE_ONLY_NO_GO",
        "attention": "LOCAL_SOURCE_REVIEW_REQUIRED" if source_flags else "NO_LOCAL_SOURCE_FLAGS",
        "production_authorized": False,
        "live_provider_health_verified": False,
        "external_alert_delivery_certified": False,
        "external_checkpoint_certified": False,
        "independent_recovery_certified": False,
        "local_storage_point_in_time_consistent": True,
        "cross_ledger_point_in_time_certified": False,
        "journal_event_count": health["event_count"],
        "primary_write_count": health["write_count"],
        "backup_reservation_count": health["backup_count"],
        "restore_request_count": restore_requests,
        "restore_completed_count": restore_completed,
        "restore_integrity_hold_count": restore_integrity,
        "restore_pending_count": restore_pending,
        "restore_pending_without_outage_count": restore_pending_without_outage,
        "restore_retryable_outage_count": restore_retryable_outage,
        "restore_physical_recovery_certified": False,
        "restore_vault_original_authenticated": False,
        "acknowledged_primary_object_count": coverage["acknowledged_primary_object_count"],
        "matched_backup_ack_count": coverage["matched_backup_ack_count"],
        "uncovered_primary_object_count": uncovered,
        "uncovered_with_pending_backup_count": uncovered_pending,
        "uncovered_without_pending_backup_count": uncovered_without_pending,
        "actual_backup_bytes_reverified": False,
        "independent_failure_domain_certified": False,
        "pending_primary_count": pending_primary,
        "pending_backup_count": pending_backup,
        "primary_integrity_hold_count": integrity_primary,
        "backup_integrity_hold_count": integrity_backup,
        "backend_error_event_count": backend_events,
        "total_incident_records": health["incident_count"],
        "work_queue": work_queue,
    }


def owner_safe_source_markdown(journal: SQLiteOperationalJournal) -> str:
    """Fixed prose and aggregate numbers; safe for owner-local source review."""
    snapshot = owner_safe_source_snapshot(journal)
    lines = [
        "# Simplee Sovereign Cloud — Local Owner Source Snapshot",
        "",
        "**SOURCE ONLY · NO GO · NOT A LIVE PROVIDER STATUS**",
        "",
        "The counts and backup coverage below share one verified local SQLite "
        "read snapshot. The separate Tower-shaped replay ledger is NOT "
        "transactionally included; these are neither hosted health nor delivered alerts.",
        "",
        "## Safe local counts",
        "",
        "| Review area | Count |",
        "| --- | ---: |",
        f"| Primary write reservations | {snapshot['primary_write_count']} |",
        f"| Backup reservations | {snapshot['backup_reservation_count']} |",
        f"| Bound restore requests | {snapshot['restore_request_count']} |",
        f"| Completed source restore verifications | {snapshot['restore_completed_count']} |",
        f"| Restore integrity holds | {snapshot['restore_integrity_hold_count']} |",
        f"| Pending restore verifications | {snapshot['restore_pending_count']} |",
        f"| Restore requests retryable after provider outage | {snapshot['restore_retryable_outage_count']} |",
        f"| Acknowledged primary objects | {snapshot['acknowledged_primary_object_count']} |",
        f"| Objects with matched backup ACK (journal only) | {snapshot['matched_backup_ack_count']} |",
        f"| Objects without backup ACK | {snapshot['uncovered_primary_object_count']} |",
        f"| Of those, pending backup | {snapshot['uncovered_with_pending_backup_count']} |",
        f"| Pending primary reconciliation | {snapshot['pending_primary_count']} |",
        f"| Pending backup reconciliation | {snapshot['pending_backup_count']} |",
        f"| Primary integrity holds | {snapshot['primary_integrity_hold_count']} |",
        f"| Backup integrity holds | {snapshot['backup_integrity_hold_count']} |",
        f"| Backend-error events | {snapshot['backend_error_event_count']} |",
        f"| Total incident records | {snapshot['total_incident_records']} |",
        "",
        "## Focus cards and next safe actions",
        "",
    ]
    for card in snapshot["work_queue"]:
        lines.extend([
            f"### {card['label']} ({card['count']})",
            "",
            card["next_action"],
            "",
        ])
    lines.extend([
        "**Production, hosted alert delivery, independent audit custody and "
        "physical site-loss recovery are NOT certified.**",
        "",
    ])
    return "\n".join(lines)
