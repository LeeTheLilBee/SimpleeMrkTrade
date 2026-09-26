"""Vault Real Operations 1: encrypted object envelope and managed-storage adapter.

This module is intentionally not an HTTP route. Tower supplies an independently
verified authorization decision to the application service. No provider is selected,
configured, contacted or unlocked by importing this module.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

MAX_ORIGINAL_BYTES = 25 * 1024 * 1024
ENVELOPE_VERSION = "vault.encrypted-object.v1"

class StorageError(ValueError):
    pass

@dataclass(frozen=True)
class TowerStorageDecision:
    request_id: str
    principal_ref: str
    entity_id: str
    purpose: str
    operation: str
    evidence_id: str
    document_version_id: str
    verified_by_tower: bool
    approval_receipt_ref: str
    malware_scan_receipt_ref: str

    def validate(self, *, operation: str) -> None:
        # This is a typed internal contract, NOT an authentication mechanism.
        # The caller MUST obtain this from trusted Tower middleware, never user JSON.
        if not self.verified_by_tower or self.operation != operation:
            raise StorageError("Tower authorization required")
        for value in (self.request_id,self.principal_ref,self.entity_id,self.purpose,
                      self.evidence_id,self.document_version_id,self.approval_receipt_ref,
                      self.malware_scan_receipt_ref):
            if not isinstance(value,str) or not value or len(value)>128:
                raise StorageError("missing or invalid Tower decision binding")

class ManagedObjectStore(Protocol):
    def put_if_absent(self, object_key: str, ciphertext: bytes) -> None: ...
    def get(self, object_key: str) -> bytes: ...

class InMemoryObjectStore:
    """Test-only implementation. Never use as production archival storage."""
    def __init__(self):
        self.objects: dict[str,bytes] = {}
    def put_if_absent(self, object_key: str, ciphertext: bytes) -> None:
        if object_key in self.objects:
            raise StorageError("immutable object already exists")
        self.objects[object_key] = bytes(ciphertext)
    def get(self, object_key: str) -> bytes:
        return self.objects[object_key]

def _aesgcm():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as exc:
        raise StorageError("cryptography dependency required") from exc
    return AESGCM

def _key(key: bytes) -> bytes:
    if not isinstance(key,bytes) or len(key)!=32:
        raise StorageError("32-byte key required from approved secret manager")
    return key

def _aad(entity_id: str, evidence_id: str, version_id: str) -> bytes:
    return json.dumps({"schema":ENVELOPE_VERSION,"entity_id":entity_id,
        "evidence_id":evidence_id,"version_id":version_id},sort_keys=True,separators=(",",":")).encode()

def encrypt_original(original: bytes, *, key: bytes, entity_id: str,
                     evidence_id: str, version_id: str) -> tuple[bytes,dict]:
    _key(key)
    if not isinstance(original,bytes) or not 0<len(original)<=MAX_ORIGINAL_BYTES:
        raise StorageError("invalid original size")
    aad=_aad(entity_id,evidence_id,version_id)
    nonce=secrets.token_bytes(12)
    ciphertext=_aesgcm()(_key(key)).encrypt(nonce,original,aad)
    envelope=b"VLT1"+nonce+ciphertext
    return envelope, {"envelope_version":ENVELOPE_VERSION,
        "original_sha256":hashlib.sha256(original).hexdigest(),
        "ciphertext_sha256":hashlib.sha256(envelope).hexdigest(),
        "original_size":len(original)}

def decrypt_original(envelope: bytes, *, key: bytes, entity_id: str,
                     evidence_id: str, version_id: str, expected_sha256: str) -> bytes:
    _key(key)
    if not isinstance(envelope,bytes) or not envelope.startswith(b"VLT1") or len(envelope)<33:
        raise StorageError("invalid encrypted envelope")
    try:
        original=_aesgcm()(key).decrypt(envelope[4:16],envelope[16:],
            _aad(entity_id,evidence_id,version_id))
    except Exception as exc:
        raise StorageError("envelope authentication failed") from exc
    if hashlib.sha256(original).hexdigest()!=expected_sha256:
        raise StorageError("original hash mismatch")
    return original

def archive_encrypted_original(store: ManagedObjectStore, original: bytes, *,
        key: bytes, decision: TowerStorageDecision, verified_scan_sha256: str) -> dict:
    decision.validate(operation="ARCHIVE_ORIGINAL")
    digest=hashlib.sha256(original).hexdigest()
    if digest!=verified_scan_sha256:
        raise StorageError("original does not match malware-screened bytes")
    envelope,meta=encrypt_original(original,key=key,entity_id=decision.entity_id,
        evidence_id=decision.evidence_id,version_id=decision.document_version_id)
    object_key="objects/"+secrets.token_hex(24)
    store.put_if_absent(object_key,envelope)
    # Internal receipt: never return object_key in a BuyBox-facing response.
    return {"object_key":object_key,"request_id":decision.request_id,
        "entity_id":decision.entity_id,"evidence_id":decision.evidence_id,
        "version_id":decision.document_version_id,"scan_receipt_ref":decision.malware_scan_receipt_ref,
        "approval_receipt_ref":decision.approval_receipt_ref,**meta}

def encrypted_local_backup(envelope: bytes, *, destination: Path) -> str:
    """Write only an already encrypted envelope; atomic, exclusive, restrictive permissions."""
    if not isinstance(envelope,bytes) or not envelope.startswith(b"VLT1"):
        raise StorageError("backup requires encrypted envelope")
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,"wb") as out:
            out.write(envelope)
            out.flush()
            os.fsync(out.fileno())
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    return hashlib.sha256(envelope).hexdigest()
