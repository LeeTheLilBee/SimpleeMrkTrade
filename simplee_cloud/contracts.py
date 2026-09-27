"""Cloud-side storage interface; Vault retains document and archival authority."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

MAX_ENVELOPE_BYTES = 25 * 1024 * 1024 + 64
_OBJECT_REF = re.compile(r"objects/[0-9a-f]{48}\Z")
_BACKUP_REF = re.compile(r"backups/[0-9a-f]{48}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_ENTITY = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")
_IDENTIFIER = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")


class CloudError(ValueError):
    pass


class AccessDenied(CloudError):
    pass


class IntegrityError(CloudError):
    pass


class AlreadyExists(CloudError):
    pass


class ObjectMissing(CloudError):
    pass


@dataclass(frozen=True)
class StorageContext:
    # Request data is never authority in itself. A trusted server-side gate
    # must independently authenticate Vault, the Tower decision, expiry,
    # scope, purpose, operation, approvals, revocation, and replay constraints.
    request_id: str
    caller_service: str
    tower_decision_ref: str
    entity_id: str
    purpose: str
    operation: str

    def validate_shape(self, expected_operation: str) -> None:
        for name in ("request_id", "caller_service", "tower_decision_ref", "purpose"):
            value = getattr(self, name)
            if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
                raise AccessDenied("invalid internal storage context")
        if not isinstance(self.entity_id, str) or not _ENTITY.fullmatch(self.entity_id):
            raise AccessDenied("invalid entity scope")
        if self.caller_service != "archive_vault" or self.operation != expected_operation:
            raise AccessDenied("Vault-only operation mismatch")


class StorageAuthority(Protocol):
    def authorize(self, context: StorageContext, operation: str) -> None:
        """Raise unless trusted external Tower/Vault verification succeeds."""
        ...


class DenyAllAuthority:
    def authorize(self, context: StorageContext, operation: str) -> None:
        raise AccessDenied("Tower/Vault runtime verifier not connected")


class CiphertextBackend(Protocol):
    def put_if_absent(self, namespace: str, object_ref: str, body: bytes) -> None: ...
    def get(self, namespace: str, object_ref: str) -> bytes: ...


@dataclass(frozen=True)
class StorageReceipt:
    # Service-internal only. Never send object_ref or namespace to BuyBox/Teller.
    object_ref: str
    ciphertext_sha256: str
    ciphertext_size: int
    namespace_digest: str


@dataclass(frozen=True)
class BackupReceipt:
    backup_ref: str
    backup_sha256: str
    source_object_ref: str
    source_ciphertext_sha256: str
    namespace_digest: str
    key_reference: str


def valid_object_ref(value: str) -> bool:
    return isinstance(value, str) and _OBJECT_REF.fullmatch(value) is not None


def valid_backup_ref(value: str) -> bool:
    return isinstance(value, str) and _BACKUP_REF.fullmatch(value) is not None


def valid_sha256(value: str) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None
