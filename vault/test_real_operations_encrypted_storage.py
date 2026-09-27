import hashlib
import os
import pytest
from vault.real_operations_encrypted_storage import (
    InMemoryObjectStore, StorageError, TowerStorageDecision,
    archive_encrypted_original, decrypt_original, encrypted_local_backup,
)

def decision(**changes):
    d=dict(request_id="req-1",principal_ref="principal-1",entity_id="entity-1",
      purpose="acquisition_due_diligence",operation="ARCHIVE_ORIGINAL",
      evidence_id="evidence-1",document_version_id="version-1",
      verified_by_tower=True,approval_receipt_ref="approval-1",
      malware_scan_receipt_ref="scan-1")
    d.update(changes)
    return TowerStorageDecision(**d)

def test_encrypted_archive_and_local_backup(tmp_path):
    key=os.urandom(32)
    original=b"%PDF-1.4 test original bytes"
    store=InMemoryObjectStore()
    receipt=archive_encrypted_original(store,original,key=key,decision=decision(),
      verified_scan_sha256=hashlib.sha256(original).hexdigest())
    envelope=store.get(receipt["object_key"])
    assert original not in envelope
    assert decrypt_original(envelope,key=key,entity_id="entity-1",evidence_id="evidence-1",
      version_id="version-1",expected_sha256=receipt["original_sha256"])==original
    destination=tmp_path/"backup"/"object.enc"
    assert encrypted_local_backup(envelope,destination=destination)==receipt["ciphertext_sha256"]
    assert destination.read_bytes()==envelope
    with pytest.raises(FileExistsError):
        encrypted_local_backup(envelope,destination=destination)

def test_tamper_wrong_scope_and_wrong_key_fail():
    key=os.urandom(32)
    original=b"real object"
    store=InMemoryObjectStore()
    receipt=archive_encrypted_original(store,original,key=key,decision=decision(),
      verified_scan_sha256=hashlib.sha256(original).hexdigest())
    envelope=store.get(receipt["object_key"])
    args=dict(key=key,entity_id="entity-1",evidence_id="evidence-1",
      version_id="version-1",expected_sha256=receipt["original_sha256"])
    with pytest.raises(StorageError):
        decrypt_original(envelope[:-1]+bytes([envelope[-1]^1]),**args)
    with pytest.raises(StorageError):
        decrypt_original(envelope,**(args|{"entity_id":"entity-2"}))
    with pytest.raises(StorageError):
        decrypt_original(envelope,**(args|{"key":os.urandom(32)}))

def test_no_archive_without_tower_or_matching_scan():
    store=InMemoryObjectStore()
    data=b"original"
    digest=hashlib.sha256(data).hexdigest()
    for d in (decision(verified_by_tower=False),decision(operation="DOWNLOAD_ORIGINAL")):
        with pytest.raises(StorageError):
            archive_encrypted_original(store,data,key=os.urandom(32),decision=d,verified_scan_sha256=digest)
    with pytest.raises(StorageError,match="malware-screened"):
        archive_encrypted_original(store,data,key=os.urandom(32),decision=decision(),verified_scan_sha256="0"*64)
    assert store.objects=={}
