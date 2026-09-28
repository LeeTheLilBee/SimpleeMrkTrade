"""SC005 isolated encrypted-copy restore drill, no primary mutation or plaintext.

This tests the SCB1 -> VLT1 ciphertext path using a separately injected
backup backend/key. It cannot certify offsite DR, original Vault AES-GCM,
RPO/RTO, real hardware separation, or real Tower authorization.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import time
from dataclasses import dataclass

from .backup import IndependentBackupService
from .contracts import (
    AccessDenied, BackupReceipt, CloudError, IntegrityError, ObjectMissing,
    StorageContext, valid_sha256,
)
from .journal import SQLiteOperationalJournal

_ID = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")


@dataclass(frozen=True)
class SyntheticRecoveryEvidence:
    drill_id: str
    verified_ciphertext: bool
    elapsed_ms: int
    status: str = "SOURCE_ONLY_ENCRYPTED_COPY_VERIFIED"
    primary_rewritten: bool = False
    vault_original_authenticated: bool = False
    external_failure_domain_verified: bool = False
    recovery_point_objective_certified: bool = False
    recovery_time_objective_certified: bool = False
    production_recovery_authorized: bool = False


def run_source_restore_drill(
    *, backup: IndependentBackupService, journal: SQLiteOperationalJournal,
    context: StorageContext, receipt: BackupReceipt,
    expected_inner_sha256: str, drill_id: str,
    mode: str = "disabled",
) -> SyntheticRecoveryEvidence:
    if mode != "source_test":
        raise AccessDenied("live recovery drill disabled")
    if not isinstance(backup, IndependentBackupService) or not isinstance(
        journal, SQLiteOperationalJournal
    ) or getattr(backup.source._audit_event, "__self__", None) is not journal:
        raise CloudError("durable source journal and isolated backup service required")
    if not isinstance(drill_id, str) or not _ID.fullmatch(drill_id) or not valid_sha256(
        expected_inner_sha256
    ) or not isinstance(receipt, BackupReceipt):
        raise CloudError("invalid internal drill binding")
    if not hmac.compare_digest(expected_inner_sha256, receipt.source_ciphertext_sha256):
        raise IntegrityError("drill expected digest differs from canonical backup receipt")
    began = time.monotonic_ns()
    try:
        inner = backup.verify_restore_copy(context=context, receipt=receipt)
        if not hmac.compare_digest(hashlib.sha256(inner).hexdigest(), expected_inner_sha256):
            raise IntegrityError("restored encrypted copy fails digest")
    except (IntegrityError, ObjectMissing):
        # The SC001 backup already records verification intent; this records
        # a durable source-only incident before surfacing the failure.
        journal.record_backup_incident(
            namespace=receipt.namespace_digest, request_id=context.request_id,
        )
        raise
    except AccessDenied:
        # Rejected authority is NOT a storage provider outage.
        raise
    except CloudError:
        # Do not relabel local shape/configuration errors as provider failure.
        raise
    except Exception:
        journal.record_backend_incident(
            namespace=receipt.namespace_digest, request_id=context.request_id,
            code="BACKUP_VERIFY_BACKEND_ERROR",
        )
        raise
    duration_ms = max(0, (time.monotonic_ns() - began) // 1_000_000)
    return SyntheticRecoveryEvidence(
        drill_id=drill_id, verified_ciphertext=True, elapsed_ms=duration_ms,
    )
