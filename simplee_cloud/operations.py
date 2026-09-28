"""SC002 source-only Cloud write/reconcile seam.

Never retry an uncertain physical write. The journal's append-only intent
reserves (namespace, request_id) before touching the backend. A separate fresh
Tower-approved reconciliation request verifies the original object's digest;
this creates only an INTERNAL storage acknowledgement, never a Vault receipt.
"""
from __future__ import annotations

import hashlib
import hmac

from .contracts import (
    AccessDenied, CloudError, IntegrityError, MAX_ENVELOPE_BYTES,
    ObjectMissing, StorageContext, StorageReceipt, valid_object_ref, valid_sha256,
)
from .journal import SQLiteOperationalJournal
from .service import CiphertextStorageService


class JournaledCiphertextOperations:
    def __init__(self, *, source: CiphertextStorageService,
                 journal: SQLiteOperationalJournal):
        if source.mode != "source_test" or journal is None:
            raise CloudError("journaled operations are source-test only")
        # Ensure the SC001 base and its backup paths use this same durable
        # audit sink rather than silently falling back to a list/no-op.
        if getattr(source._audit_event, "__self__", None) is not journal:
            raise CloudError("source must use this journal as its audit sink")
        self.source = source
        self.journal = journal

    def put_if_absent(
        self, *, context: StorageContext, object_ref: str,
        envelope: bytes, expected_sha256: str,
    ) -> StorageReceipt:
        scope = self.source._gate(context, "WRITE_CIPHERTEXT")
        if not valid_object_ref(object_ref) or not valid_sha256(expected_sha256):
            raise CloudError("invalid internal reference or expected digest")
        if not isinstance(envelope, bytes) or not envelope.startswith(b"VLT1") or not (
            33 <= len(envelope) <= MAX_ENVELOPE_BYTES
        ):
            raise CloudError("only bounded Vault ciphertext can be written")
        if not hmac.compare_digest(
            hashlib.sha256(envelope).hexdigest(), expected_sha256
        ):
            raise IntegrityError("ciphertext hash mismatch before reservation")

        state = self.journal.reserve_write(
            namespace=scope, request_id=context.request_id,
            object_ref=object_ref, digest=expected_sha256, size=len(envelope),
        )
        if state in ("WRITE_ACKNOWLEDGED", "RECONCILE_PRESENT"):
            # Fresh Tower gate already happened. Verify physical bytes even
            # for acknowledged replay; never mistake the journal for storage.
            try:
                stored = self.source._read_verified(scope, object_ref, expected_sha256)
                if len(stored) != len(envelope):
                    raise IntegrityError("acknowledged object size changed")
            except (ObjectMissing, IntegrityError):
                self.journal.transition(
                    namespace=scope, request_id=context.request_id,
                    next_state="REPLAY_INTEGRITY_FAILURE",
                )
                raise IntegrityError("acknowledged ciphertext missing or corrupted")
            except Exception:
                # Provider outage is not evidence that acknowledged bytes are
                # missing/corrupt. Preserve the durable ACK and report safely.
                self.journal.record_backend_incident(
                    namespace=scope, request_id=context.request_id,
                    code="PRIMARY_REPLAY_BACKEND_ERROR",
                )
                raise
            return StorageReceipt(object_ref, expected_sha256, len(stored), scope)

        if state != "WRITE_RESERVED_NEW":
            # Existing incomplete or failed intent is a HOLD, not a second PUT.
            raise CloudError("write intent unresolved; authorized reconciliation required")

        try:
            self.source._backend.put_if_absent(scope, object_ref, envelope)
        except Exception:
            # Failure may occur AFTER storage accepted the bytes; never infer
            # absence from a network error. If journal fails, reservation still
            # remains unresolved and no success receipt is emitted.
            self.journal.transition(
                namespace=scope, request_id=context.request_id,
                next_state="WRITE_UNCERTAIN",
            )
            raise

        # If durable acknowledgement fails, reservation remains unresolved.
        # Caller receives an error and must perform independent reconciliation.
        self.journal.transition(
            namespace=scope, request_id=context.request_id,
            next_state="WRITE_ACKNOWLEDGED",
        )
        return StorageReceipt(object_ref, expected_sha256, len(envelope), scope)

    def reconcile_write(
        self, *, context: StorageContext, original_request_id: str,
    ) -> dict:
        scope = self.source._gate(context, "RECONCILE_WRITE")
        stored_intent = self.journal.intent(
            namespace=scope, request_id=original_request_id,
        )
        if stored_intent["state"] not in ("WRITE_RESERVED", "WRITE_UNCERTAIN"):
            raise CloudError("write is not pending reconciliation")
        self.journal.record_reconcile_intent(
            namespace=scope, original_request_id=original_request_id,
        )
        ref = stored_intent["object_ref"]
        digest = stored_intent["ciphertext_sha256"]
        try:
            envelope = self.source._read_verified(scope, ref, digest)
            if len(envelope) != stored_intent["ciphertext_size"]:
                raise IntegrityError("reconciled physical size mismatch")
        except ObjectMissing:
            self.journal.transition(
                namespace=scope, request_id=original_request_id,
                next_state="RECONCILE_MISSING",
            )
            return {"status": "MISSING_HOLD", "storage_receipt": None,
                    "vault_archive_committed": False}
        except IntegrityError:
            self.journal.transition(
                namespace=scope, request_id=original_request_id,
                next_state="RECONCILE_CORRUPT",
            )
            return {"status": "CORRUPT_HOLD", "storage_receipt": None,
                    "vault_archive_committed": False}
        except Exception:
            # Fail closed but do not infer a missing/corrupt object from an
            # unreachable provider. The original intent stays reconcilable.
            self.journal.record_backend_incident(
                namespace=scope, request_id=original_request_id,
                code="PRIMARY_RECONCILE_BACKEND_ERROR",
            )
            raise
        # Reconciliation only returns storage acknowledgement, never Vault finality.
        self.journal.transition(
            namespace=scope, request_id=original_request_id,
            next_state="RECONCILE_PRESENT",
        )
        return {
            "status": "PRESENT_INTERNAL_STORAGE_ONLY",
            "storage_receipt": StorageReceipt(ref, digest, len(envelope), scope),
            "vault_archive_committed": False,
        }

    def get(
        self, *, context: StorageContext, object_ref: str,
        expected_sha256: str,
    ) -> bytes:
        scope = self.source._gate(context, "READ_CIPHERTEXT")
        # A signed Vault read scope and physically matching object are not
        # sufficient without the Cloud's own durable primary provenance.
        # Deny before any provider GET or read audit success; backup recovery
        # retains its separate canonical receipt/verification path.
        self.journal.reserve_read(
            namespace=scope, request_id=context.request_id,
            object_ref=object_ref, digest=expected_sha256,
        )
        self.source._audit(action="read_intent", context=context, namespace=scope)
        try:
            envelope = self.source._read_verified(scope, object_ref, expected_sha256)
        except (ObjectMissing, IntegrityError):
            self.journal.record_read_incident(
                namespace=scope, request_id=context.request_id,
            )
            raise
        except Exception:
            self.journal.record_backend_incident(
                namespace=scope, request_id=context.request_id,
                code="PRIMARY_READ_BACKEND_ERROR",
            )
            raise
        self.source._audit(action="read_verified", context=context, namespace=scope)
        return envelope

    def health(self) -> dict:
        return {
            **self.source.health(),
            "operational_journal": self.journal.health(),
            "production_authorized": False,
            "status": "SOURCE_ONLY_NO_GO",
        }
