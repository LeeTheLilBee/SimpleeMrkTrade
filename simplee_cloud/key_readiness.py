"""SC035 redacted source preflight for historical backup key references.

This checks only whether an injected key resolver can return a bounded 32-byte
value for every key reference used by ACKNOWLEDGED local backup intents. It
does NOT read backup bytes, authenticate SCB1, certify KMS/HSM custody or GO.
"""
from __future__ import annotations

from .contracts import AccessDenied, CloudError
from .journaled_backup import JournaledBackupOperations


def source_backup_key_readiness(
    operations: JournaledBackupOperations,
) -> dict:
    if not isinstance(operations, JournaledBackupOperations):
        raise CloudError("journaled backup operations required")
    inventory = operations.journal.source_backup_key_reference_inventory()
    counts = inventory["acknowledged_key_counts"]
    if not isinstance(counts, dict):
        raise CloudError("verified backup key inventory required")

    resolvable_refs = 0
    unavailable_refs = 0
    affected_backups = 0
    for key_reference, backup_count in counts.items():
        if type(backup_count) is not int or backup_count < 1:
            raise CloudError("invalid verified backup key inventory")
        try:
            operations.backup._key_for(key_reference)
        except AccessDenied:
            unavailable_refs += 1
            affected_backups += backup_count
        else:
            resolvable_refs += 1

    acknowledged_count = sum(counts.values())
    return {
        "schema": "simplee.cloud.backup-key-readiness.v1",
        "status": (
            "SOURCE_ONLY_KEY_REFERENCE_HOLD"
            if unavailable_refs
            else "SOURCE_ONLY_KEY_REFERENCES_RESOLVABLE"
        ),
        "acknowledged_backup_count": acknowledged_count,
        "distinct_key_reference_count": len(counts),
        "resolvable_key_reference_count": resolvable_refs,
        "unavailable_key_reference_count": unavailable_refs,
        "acknowledged_backups_depending_on_unavailable_key_count": affected_backups,
        "pending_backup_count": inventory["pending_backup_count"],
        "integrity_hold_backup_count": inventory["integrity_hold_backup_count"],
        "provider_bytes_read": False,
        "backup_ciphertext_authenticated_in_this_check": False,
        "resolved_key_material_correct_for_ciphertext_certified": False,
        "external_kms_hsm_custody_certified": False,
        "rotation_ceremony_certified": False,
        "old_key_recovery_drill_certified": False,
        "production_authorized": False,
    }
