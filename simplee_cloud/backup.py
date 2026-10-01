"""Independent, doubly encrypted backup and isolated restore-verification seam.

Vault's VLT1 inner encryption stays in Vault. SCB1 is a second AES-256-GCM
layer using an independently supplied backup key. Restore NEVER overwrites a
primary object and does not constitute an authorized Vault recovery commit.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
from collections.abc import Callable

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
        backup_backend: CiphertextBackend, backup_key: bytes | None = None,
        key_reference: str,
        backup_key_resolver: Callable[[str], bytes] | None = None,
    ):
        if backup_backend is None or backup_backend is source._backend:
            raise CloudError("primary and backup must use separate backends")
        if not isinstance(key_reference, str) or not re.fullmatch(
            r"[A-Za-z0-9_.:-]{1,128}", key_reference
        ):
            raise CloudError("approved backup key reference required")
        if backup_key_resolver is None:
            if not isinstance(backup_key, bytes) or len(backup_key) != 32:
                raise CloudError("separate 32-byte backup key required")
        elif backup_key is not None or not callable(backup_key_resolver):
            raise CloudError("use either fixed backup key or resolver, never both")
        self.source = source
        self.backup_backend = backup_backend
        # Fixed-key mode remains for legacy source fixtures. Resolver mode
        # models rotation without storing a key catalog in Cloud source.
        self._backup_key = backup_key
        self._backup_key_resolver = backup_key_resolver
        self.key_reference = key_reference
        self._key_for(self.key_reference)

    def _key_for(self, key_reference: str) -> bytes:
        if not isinstance(key_reference, str) or not re.fullmatch(
            r"[A-Za-z0-9_.:-]{1,128}", key_reference
        ):
            raise AccessDenied("invalid backup key reference")
        if self._backup_key_resolver is None:
            if key_reference != self.key_reference:
                raise AccessDenied("backup key reference unavailable")
            key = self._backup_key
        else:
            try:
                key = self._backup_key_resolver(key_reference)
            except Exception as exc:
                raise AccessDenied("backup key unavailable") from exc
        if not isinstance(key, bytes) or len(key) != 32:
            raise AccessDenied("backup key unavailable")
        return key

    def create(
        self, *, context: StorageContext, source_object_ref: str,
        source_ciphertext_sha256: str,
    ) -> BackupReceipt:
        scope = self.source._gate(context, "BACKUP_CIPHERTEXT")
        if not valid_object_ref(source_object_ref) or not valid_sha256(source_ciphertext_sha256):
            raise CloudError("invalid backup source reference")
        key = self._key_for(self.key_reference)
        self.source._audit(action="backup_intent", context=context, namespace=scope)
        inner = self.source._read_verified(scope, source_object_ref, source_ciphertext_sha256)
        nonce = secrets.token_bytes(12)
        outer = b"SCB1" + nonce + _aesgcm()(key).encrypt(
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
        if receipt.namespace_digest != scope:
            raise AccessDenied("backup entity mismatch")
        # Resolve the historical receipt's exact key reference BEFORE provider
        # access. Rotation may change the active key for NEW backups without
        # silently re-encrypting or re-labeling older immutable copies.
        key = self._key_for(receipt.key_reference)
        self.source._audit(action="restore_verification_intent", context=context, namespace=scope)
        outer = self.backup_backend.get(scope, receipt.backup_ref)
        if not isinstance(outer, bytes) or not outer.startswith(b"SCB1") or not (
            33 <= len(outer) <= MAX_ENVELOPE_BYTES + 64
        ):
            raise IntegrityError("invalid backup envelope")
        if not hmac.compare_digest(hashlib.sha256(outer).hexdigest(), receipt.backup_sha256):
            raise IntegrityError("backup ciphertext integrity mismatch")
        try:
            inner = _aesgcm()(key).decrypt(
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
