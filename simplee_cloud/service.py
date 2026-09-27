"""Internal, closed-by-default encrypted object service.

This service stores Vault-created VLT1 envelopes without decrypting originals,
choosing Vault retention, or accepting direct users. It has no HTTP route.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from collections.abc import Callable

from .contracts import (
    AccessDenied, CiphertextBackend, CloudError, DenyAllAuthority, IntegrityError,
    MAX_ENVELOPE_BYTES, StorageAuthority, StorageContext, StorageReceipt,
    valid_object_ref, valid_sha256,
)


def namespace_digest(entity_id: str, *, namespace_key: bytes) -> str:
    # HMAC prevents exposing raw entity IDs in physical paths or enabling
    # unkeyed enumeration of likely tenant names.
    if not isinstance(namespace_key, bytes) or len(namespace_key) != 32:
        raise CloudError("approved 32-byte namespace secret required")
    if not isinstance(entity_id, str) or not entity_id:
        raise CloudError("missing entity")
    return hmac.new(namespace_key, b"simplee-cloud:entity:v1:" + entity_id.encode(),
                    hashlib.sha256).hexdigest()


class CiphertextStorageService:
    def __init__(
        self, *,
        backend: CiphertextBackend,
        namespace_key: bytes,
        authority: StorageAuthority | None = None,
        audit_event: Callable[[dict], None] | None = None,
        mode: str = "disabled",
    ):
        # There is intentionally NO production mode. A future independently
        # reviewed runtime/transport will have to introduce that separately.
        if mode not in ("disabled", "source_test"):
            raise CloudError("production storage not authorized")
        if backend is None or not isinstance(namespace_key, bytes) or len(namespace_key) != 32:
            raise CloudError("explicit backend and approved namespace secret required")
        self._backend = backend
        self._namespace_key = namespace_key
        self._authority = authority if authority is not None else DenyAllAuthority()
        self._audit_event = audit_event
        self.mode = mode

    @staticmethod
    def new_object_ref() -> str:
        return "objects/" + secrets.token_hex(24)

    def _gate(self, context: StorageContext, operation: str) -> str:
        if self.mode != "source_test":
            raise AccessDenied("Cloud object operations disabled")
        if self._audit_event is None:
            raise AccessDenied("auditable service runtime required")
        if not isinstance(context, StorageContext):
            raise AccessDenied("trusted internal context required")
        context.validate_shape(operation)
        # A context or asserted boolean cannot grant access. Production must
        # inject a REAL verifier checking authenticated service transport,
        # Tower-issued scope/decision, expiry, revocation and replay state.
        self._authority.authorize(context, operation)
        return namespace_digest(context.entity_id, namespace_key=self._namespace_key)

    def _audit(self, *, action: str, context: StorageContext, namespace: str) -> None:
        # No plaintext, object body, raw entity name or reusable bearer tokens.
        self._audit_event({
            "event": action, "request_id": context.request_id,
            "tower_decision_ref": context.tower_decision_ref,
            "namespace_digest": namespace,
        })

    def put_if_absent(
        self, *, context: StorageContext, object_ref: str,
        envelope: bytes, expected_sha256: str,
    ) -> StorageReceipt:
        scope = self._gate(context, "WRITE_CIPHERTEXT")
        if not valid_object_ref(object_ref) or not valid_sha256(expected_sha256):
            raise CloudError("invalid internal object reference or digest")
        if not isinstance(envelope, bytes) or not envelope.startswith(b"VLT1") or not (
            33 <= len(envelope) <= MAX_ENVELOPE_BYTES
        ):
            raise CloudError("bounded VLT1 ciphertext only")
        actual = hashlib.sha256(envelope).hexdigest()
        if not hmac.compare_digest(actual, expected_sha256):
            raise IntegrityError("ciphertext digest mismatch before write")
        self._audit(action="write_intent", context=context, namespace=scope)
        self._backend.put_if_absent(scope, object_ref, envelope)
        # If audit fails after write, operation remains uncertain and must be
        # reconciled. Never report success or overwrite the object to retry.
        self._audit(action="write_acknowledged", context=context, namespace=scope)
        return StorageReceipt(object_ref, actual, len(envelope), scope)

    def _read_verified(self, namespace: str, object_ref: str, expected_sha256: str) -> bytes:
        if not valid_object_ref(object_ref) or not valid_sha256(expected_sha256):
            raise CloudError("invalid internal object reference or expected digest")
        envelope = self._backend.get(namespace, object_ref)
        if not isinstance(envelope, bytes) or not envelope.startswith(b"VLT1") or not (
            33 <= len(envelope) <= MAX_ENVELOPE_BYTES
        ):
            raise IntegrityError("stored object is not bounded encrypted envelope")
        if not hmac.compare_digest(hashlib.sha256(envelope).hexdigest(), expected_sha256):
            raise IntegrityError("stored ciphertext integrity mismatch")
        # AES-GCM authenticity and original SHA remain Vault's job at decrypt.
        return envelope

    def get(
        self, *, context: StorageContext, object_ref: str, expected_sha256: str,
    ) -> bytes:
        scope = self._gate(context, "READ_CIPHERTEXT")
        self._audit(action="read_intent", context=context, namespace=scope)
        envelope = self._read_verified(scope, object_ref, expected_sha256)
        self._audit(action="read_verified", context=context, namespace=scope)
        return envelope

    def health(self) -> dict:
        # Safe readiness metadata; no storage listing, file bodies or false GO.
        return {
            "service": "simplee_sovereign_cloud",
            "mode": self.mode,
            "production_authorized": False,
            "external_provider_connected": False,
            "tower_runtime_verifier_certified": False,
            "backup_restore_drill_certified": False,
            "status": "SOURCE_ONLY_NO_GO",
        }
