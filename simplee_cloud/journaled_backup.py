"""SC005B durable backup creation and explicit uncertain-write reconciliation.

Source-test only. A provider may accept an SCB1 object then lose the ACK;
the append-only journal reserves its opaque backup reference BEFORE PUT.
Never regenerate and re-PUT on retry. The legacy backup helper remains useful
for prior source tests but MUST NOT be wired directly to a production route.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets

from .backup import IndependentBackupService, _aad, _aesgcm
from .contracts import (
    AccessDenied, BackupReceipt, CloudError, IntegrityError, MAX_ENVELOPE_BYTES,
    ObjectMissing, StorageContext, valid_object_ref, valid_sha256,
)
from .operations import JournaledCiphertextOperations


class JournaledBackupOperations:
    def __init__(
        self, *, operations: JournaledCiphertextOperations,
        backup: IndependentBackupService, mode: str = "disabled",
    ):
        if mode != "source_test":
            raise CloudError("durable backup runtime not production-authorized")
        if not isinstance(operations, JournaledCiphertextOperations) or not isinstance(
            backup, IndependentBackupService
        ) or backup.source is not operations.source:
            raise CloudError("backup requires exact journaled primary source")
        self.operations = operations
        self.backup = backup
        self.journal = operations.journal

    @staticmethod
    def _receipt(intent: dict) -> BackupReceipt:
        return BackupReceipt(
            intent["backup_ref"], intent["backup_sha256"],
            intent["source_object_ref"], intent["source_ciphertext_sha256"],
            intent["namespace_digest"], intent["key_reference"],
        )

    def _read_verified(self, intent: dict) -> bytes:
        data = self.backup.backup_backend.get(
            intent["namespace_digest"], intent["backup_ref"],
        )
        if not isinstance(data, bytes) or not data.startswith(b"SCB1") or not (
            33 <= len(data) <= MAX_ENVELOPE_BYTES + 64
        ) or len(data) != intent["backup_size"] or not hmac.compare_digest(
            hashlib.sha256(data).hexdigest(), intent["backup_sha256"]
        ):
            raise IntegrityError("physical backup differs from reserved ciphertext")
        # This only verifies stored ciphertext against our separate journal;
        # cryptographic SCB1 authentication still occurs on isolated restore.
        return data

    def create(
        self, *, context: StorageContext, source_object_ref: str,
        source_ciphertext_sha256: str,
    ) -> BackupReceipt:
        scope = self.backup.source._gate(context, "BACKUP_CIPHERTEXT")
        if not valid_object_ref(source_object_ref) or not valid_sha256(
            source_ciphertext_sha256
        ):
            raise CloudError("invalid canonical source ref/digest")
        existing = self.journal.backup_intent(
            namespace=scope, request_id=context.request_id,
        )
        if existing is not None:
            if (
                existing["source_object_ref"] != source_object_ref or
                not hmac.compare_digest(
                    existing["source_ciphertext_sha256"], source_ciphertext_sha256
                ) or existing["key_reference"] != self.backup.key_reference
            ):
                raise CloudError("conflicting backup idempotency reservation")
            if existing["state"] not in (
                "BACKUP_ACKNOWLEDGED", "BACKUP_RECONCILE_PRESENT"
            ):
                raise CloudError("backup unresolved/held; new authorized reconciliation required")
            try:
                self._read_verified(existing)
            except (ObjectMissing, IntegrityError) as exc:
                self.journal.backup_transition(
                    namespace=scope, request_id=context.request_id,
                    next_state="BACKUP_REPLAY_INTEGRITY_FAILURE",
                )
                raise IntegrityError("acknowledged backup missing or corrupted") from exc
            return self._receipt(existing)

        # Source is a bound VLT1; the second SCB1 encryption has its own
        # distinct 32-byte backup key and cryptographically bound AAD.
        self.backup.source._audit(
            action="backup_intent", context=context, namespace=scope,
        )
        inner = self.backup.source._read_verified(
            scope, source_object_ref, source_ciphertext_sha256,
        )
        nonce = secrets.token_bytes(12)
        outer = b"SCB1" + nonce + _aesgcm()(self.backup._backup_key).encrypt(
            nonce, inner, _aad(scope, source_object_ref, source_ciphertext_sha256),
        )
        if not 33 <= len(outer) <= MAX_ENVELOPE_BYTES + 64:
            raise CloudError("backup exceeds bounded envelope")
        backup_ref = "backups/" + secrets.token_hex(24)
        backup_sha = hashlib.sha256(outer).hexdigest()
        self.journal.reserve_backup(
            namespace=scope, request_id=context.request_id,
            source_object_ref=source_object_ref, source_digest=source_ciphertext_sha256,
            backup_ref=backup_ref, backup_digest=backup_sha,
            backup_size=len(outer), key_reference=self.backup.key_reference,
        )
        try:
            self.backup.backup_backend.put_if_absent(scope, backup_ref, outer)
        except Exception:
            self.journal.backup_transition(
                namespace=scope, request_id=context.request_id,
                next_state="BACKUP_UNCERTAIN",
            )
            raise
        # ACK must be durable before any success result. If this transaction
        # or following source audit fails, caller gets no success and can only
        # check/reconcile the original journaled ref.
        self.journal.backup_transition(
            namespace=scope, request_id=context.request_id,
            next_state="BACKUP_ACKNOWLEDGED",
        )
        self.backup.source._audit(
            action="backup_acknowledged", context=context, namespace=scope,
        )
        return BackupReceipt(
            backup_ref, backup_sha, source_object_ref,
            source_ciphertext_sha256, scope, self.backup.key_reference,
        )

    def reconcile_original_backup(
        self, *, context: StorageContext, original_request_id: str,
        canonical_source_object_ref: str, canonical_source_sha256: str,
    ) -> dict:
        scope = self.backup.source._gate(context, "RECONCILE_BACKUP")
        if context.request_id != original_request_id or not (
            valid_object_ref(canonical_source_object_ref) and
            valid_sha256(canonical_source_sha256)
        ):
            raise AccessDenied("fresh grant must bind original backup request")
        original = self.journal.backup_intent(
            namespace=scope, request_id=original_request_id,
        )
        if original is None or (
            original["source_object_ref"] != canonical_source_object_ref or
            not hmac.compare_digest(
                original["source_ciphertext_sha256"], canonical_source_sha256,
            )
        ):
            raise AccessDenied("source ref/hash differs from durable backup intent")
        if original["state"] not in ("BACKUP_RESERVED", "BACKUP_UNCERTAIN"):
            raise CloudError("backup not pending reconciliation")
        self.journal.record_backup_reconcile_intent(
            namespace=scope, request_id=original_request_id,
        )
        try:
            self._read_verified(original)
        except ObjectMissing:
            self.journal.backup_transition(
                namespace=scope, request_id=original_request_id,
                next_state="BACKUP_RECONCILE_MISSING",
            )
            return {
                "status": "BACKUP_MISSING_HOLD", "backup_receipt": None,
                "vault_backup_committed": False,
            }
        except IntegrityError:
            self.journal.backup_transition(
                namespace=scope, request_id=original_request_id,
                next_state="BACKUP_RECONCILE_CORRUPT",
            )
            return {
                "status": "BACKUP_CORRUPT_HOLD", "backup_receipt": None,
                "vault_backup_committed": False,
            }
        # Other provider failures propagate. No terminal state is inferred.
        self.journal.backup_transition(
            namespace=scope, request_id=original_request_id,
            next_state="BACKUP_RECONCILE_PRESENT",
        )
        return {
            "status": "PRESENT_INTERNAL_BACKUP_ONLY",
            "backup_receipt": self._receipt(original),
            "vault_backup_committed": False,
        }

    def health(self) -> dict:
        status = self.journal.health()
        return {
            "status": "SOURCE_ONLY_NO_GO",
            "production_authorized": False,
            "pending_backups": status["pending_backups"],
            "backup_missing_or_corrupt": status["backup_missing_or_corrupt"],
            "incident_count": status["incident_count"],
            "offsite_recovery_certified": False,
        }
