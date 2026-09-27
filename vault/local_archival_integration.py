"""Internal synthetic/local Vault integration harness, NOT a production HTTP endpoint.

Trusted adapters must independently authenticate Tower/scan/Cloud evidence.
The in-memory object store is test-only. The registry is the sole archival
receipt authority; the journal tracks workflow progress and reconciliation.
"""
from __future__ import annotations
import hashlib
import secrets
from dataclasses import dataclass
from typing import Protocol
from vault.archival_transaction_journal import ArchivalJournal
from vault.canonical_evidence_registry import CanonicalEvidenceRegistry
from vault.real_operations_encrypted_storage import encrypt_original, decrypt_original, StorageError

class IntegrationError(ValueError): pass
class TrustedVerifier(Protocol):
    def authorize(self, *, request_id:str,entity_id:str,evidence_id:str,version_id:str)->str: ...
    def scan(self, *, original:bytes,request_id:str)->str: ...
    def verify_cloud(self, *, request_id:str,object_ref:str,ciphertext_sha256:str)->str: ...

@dataclass
class LocalCipherStore:
    """Synthetic drill adapter only: create-only ciphertext, no network."""
    objects:dict[str,bytes]
    def put_if_absent(self,ref,blob):
        if ref in self.objects:raise IntegrationError("immutable object exists")
        self.objects[ref]=bytes(blob)
    def get(self,ref):return self.objects[ref]

class VaultLocalOrchestrator:
    def __init__(self,journal:ArchivalJournal,registry:CanonicalEvidenceRegistry,
                 store:LocalCipherStore,verifier:TrustedVerifier):
        self.journal,self.registry,self.store,self.verifier=journal,registry,store,verifier

    def archive(self,*,original:bytes,key:bytes,request_id:str,entity_id:str,
                evidence_id:str,version_id:str,retention_policy_id:str,
                parent_version_id=None,fail_after_cloud=False):
        state=self.journal.begin(request_id=request_id,entity_id=entity_id,
                                 evidence_id=evidence_id,version_id=version_id)
        if state!="RECEIVED":raise IntegrationError("existing request needs explicit reconciliation")
        try:
            tower=self.verifier.authorize(request_id=request_id,entity_id=entity_id,
                evidence_id=evidence_id,version_id=version_id)
            self.journal.advance(request_id=request_id,expected_state="RECEIVED",to_state="QUARANTINED")
            scan=self.verifier.scan(original=original,request_id=request_id)
            original_digest=hashlib.sha256(original).hexdigest()
            if scan!=original_digest:raise IntegrationError("scanner digest mismatch")
            self.journal.advance(request_id=request_id,expected_state="QUARANTINED",
                to_state="VERIFIED",receipt_digest=scan)
            envelope,meta=encrypt_original(original,key=key,entity_id=entity_id,
                evidence_id=evidence_id,version_id=version_id)
            self.journal.advance(request_id=request_id,expected_state="VERIFIED",
                to_state="ENCRYPTED",receipt_digest=meta["ciphertext_sha256"])
            ref="objects/"+secrets.token_hex(24)
            self.store.put_if_absent(ref,envelope)
            cloud=self.verifier.verify_cloud(request_id=request_id,object_ref=ref,
                ciphertext_sha256=meta["ciphertext_sha256"])
            if hashlib.sha256(self.store.get(ref)).hexdigest()!=meta["ciphertext_sha256"]:
                raise IntegrationError("Cloud ciphertext mismatch")
            self.journal.advance(request_id=request_id,expected_state="ENCRYPTED",
                to_state="CLOUD_COMMITTED",receipt_digest=cloud)
            if fail_after_cloud:raise IntegrationError("injected post-cloud crash")
            receipt_id="receipt-"+secrets.token_hex(16)
            self.registry.record_archival(receipt_id=receipt_id,request_id=request_id,
                entity_id=entity_id,evidence_id=evidence_id,version_id=version_id,
                parent_version_id=parent_version_id,original_sha256=original_digest,
                ciphertext_sha256=meta["ciphertext_sha256"],object_ref=ref,
                scan_receipt_ref="scan-"+scan[:32],tower_receipt_ref=tower,
                retention_policy_id=retention_policy_id)
            registry_digest=hashlib.sha256(receipt_id.encode()).hexdigest()
            self.journal.advance(request_id=request_id,expected_state="CLOUD_COMMITTED",
                to_state="ARCHIVED",receipt_digest=registry_digest)
            return receipt_id,ref,meta
        except Exception:
            current=self.journal.status(request_id)
            if current in {"ENCRYPTED","CLOUD_COMMITTED"}:
                self.journal.advance(request_id=request_id,expected_state=current,
                    to_state="RECONCILE_REQUIRED")
            raise

    def restore_drill(self,*,ref:str,key:bytes,entity_id:str,evidence_id:str,
                      version_id:str,expected_ciphertext_sha256:str,
                      expected_original_sha256:str,backup:bytes):
        live=self.store.get(ref)
        if hashlib.sha256(live).hexdigest()!=expected_ciphertext_sha256:
            raise IntegrationError("live ciphertext corrupt")
        if hashlib.sha256(backup).hexdigest()!=expected_ciphertext_sha256:
            raise IntegrationError("backup ciphertext corrupt")
        restored=decrypt_original(backup,key=key,entity_id=entity_id,
            evidence_id=evidence_id,version_id=version_id,
            expected_sha256=expected_original_sha256)
        if restored!=decrypt_original(live,key=key,entity_id=entity_id,
            evidence_id=evidence_id,version_id=version_id,
            expected_sha256=expected_original_sha256):
            raise IntegrationError("restore mismatch")
        return hashlib.sha256(restored).hexdigest()
