"""Independent, doubly encrypted backup and isolated restore-verification seam.

Vault's VLT1 inner encryption stays in Vault. SCB1 is a second AES-256-GCM
layer using an independently supplied backup key. Restore NEVER overwrites a
primary object and does not constitute an authorized Vault recovery commit.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets

from .contracts import (
    AccessDenied, BackupReceipt, CiphertextBackend, CloudError, IntegrityError,
    MAX_ENVELOPE_BYTES, StorageContext, valid_backup_ref, valid_object_ref,
    valid_sha256,
)
from .service import CiphertextStorageService


def _aesgcm():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as exc:
        raise CloudError("audited cryptography dependency required") from exc
    return AESGCM


def _aad(namespace: str, object_ref: str, digest: str) -> bytes:
    return json.dumps({
        "schema": "simplee-cloud.backup.v1", "namespace": namespace,
        "object_ref": object_ref, "source_sha256": digest,
    }, sort_keys=True, separators=(",", ":")).encode()


class IndependentBackupService:
    def __init__(
        self, *, source: CiphertextStorageService,
        backup_backend: CiphertextBackend, backup_key: bytes,
        key_reference: str,
    ):
        if backup_backend is None or backup_backend is source._backend:
            raise CloudError("primary and backup must use separate backends")
        if not isinstance(backup_key, bytes) or len(backup_key) != 32:
            raise CloudError("separate 32-byte backup key required")
        if not isinstance(key_reference, str) or not key_reference or len(key_reference) > 128:
            raise CloudError("approved backup key reference required")
        self.source = source
        self.backup_backend = backup_backend
        self._backup_key = backup_key
        self.key_reference = key_reference

    def create(
        self, *, context: StorageContext, source_object_ref: str,
        source_ciphertext_sha256: str,
    ) -> BackupReceipt:
        scope = self.source._gate(context, "BACKUP_CIPHERTEXT")
        if not valid_object_ref(source_object_ref) or not valid_sha256(source_ciphertext_sha256):
            raise CloudError("invalid backup source reference")
        self.source._audit(action="backup_intent", context=context, namespace=scope)
        inner = self.source._read_verified(scope, source_object_ref, source_ciphertext_sha256)
        nonce = secrets.token_bytes(12)
        outer = b"SCB1" + nonce + _aesgcm()(self._backup_key).encrypt(
            nonce, inner, _aad(scope, source_object_ref, source_ciphertext_sha256)
        )
        if len(outer) > MAX_ENVELOPE_BYTES + 64:
            raise CloudError("backup exceeds bounded storage limit")
        backup_ref = "backups/" + secrets.token_hex(24)
        self.backup_backend.put_if_absent(scope, backup_ref, outer)
        self.source._audit(action="backup_acknowledged", context=context, namespace=scope)
        return BackupReceipt(
            backup_ref, hashlib.sha256(outer).hexdigest(), source_object_ref,
            source_ciphertext_sha256, scope, self.key_reference,
        )

    def verify_restore_copy(self, *, context: StorageContext, receipt: BackupReceipt) -> bytes:
        # This returns a verified inner encrypted envelope to the isolated
        # recovery operator ONLY. It never writes primary or releases plaintext.
        scope = self.source._gate(context, "VERIFY_BACKUP")
        if not isinstance(receipt, BackupReceipt) or not (
            valid_backup_ref(receipt.backup_ref) and
            valid_object_ref(receipt.source_object_ref) and
            valid_sha256(receipt.backup_sha256) and
            valid_sha256(receipt.source_ciphertext_sha256)
        ):
            raise CloudError("invalid backup receipt")
        if receipt.namespace_digest != scope or receipt.key_reference != self.key_reference:
            raise AccessDenied("backup entity or key reference mismatch")
        self.source._audit(action="restore_verification_intent", context=context, namespace=scope)
        outer = self.backup_backend.get(scope, receipt.backup_ref)
        if not isinstance(outer, bytes) or not outer.startswith(b"SCB1") or not (
            33 <= len(outer) <= MAX_ENVELOPE_BYTES + 64
        ):
            raise IntegrityError("invalid backup envelope")
        if not hmac.compare_digest(hashlib.sha256(outer).hexdigest(), receipt.backup_sha256):
            raise IntegrityError("backup ciphertext integrity mismatch")
        try:
            inner = _aesgcm()(self._backup_key).decrypt(
                outer[4:16], outer[16:],
                _aad(scope, receipt.source_object_ref, receipt.source_ciphertext_sha256),
            )
        except Exception as exc:
            raise IntegrityError("backup authentication failed") from exc
        if not inner.startswith(b"VLT1") or not (
            33 <= len(inner) <= MAX_ENVELOPE_BYTES
        ) or not hmac.compare_digest(
            hashlib.sha256(inner).hexdigest(), receipt.source_ciphertext_sha256
        ):
            raise IntegrityError("restored inner ciphertext integrity mismatch")
        self.source._audit(action="restore_copy_verified", context=context, namespace=scope)
        return inner
