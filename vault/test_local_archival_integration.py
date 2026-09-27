import hashlib
import pytest
from vault.archival_transaction_journal import ArchivalJournal
from vault.canonical_evidence_registry import CanonicalEvidenceRegistry
from vault.local_archival_integration import LocalCipherStore,VaultLocalOrchestrator,IntegrationError

class SyntheticTrustedVerifier:
    """Explicit fake for tests; never configure as live authority."""
    def authorize(self,**kwargs):return "tower-synthetic"
    def scan(self,*,original,request_id):return hashlib.sha256(original).hexdigest()
    def verify_cloud(self,*,request_id,object_ref,ciphertext_sha256):
        return hashlib.sha256((request_id+object_ref+ciphertext_sha256).encode()).hexdigest()

def fixture(tmp_path,verifier=None):
    store=LocalCipherStore({})
    journal=ArchivalJournal(tmp_path/"journal.sqlite")
    registry=CanonicalEvidenceRegistry(tmp_path/"registry.sqlite")
    return VaultLocalOrchestrator(journal,registry,store,verifier or SyntheticTrustedVerifier())

def params():
    return dict(original=b"synthetic acquisition evidence",key=b"k"*32,
        request_id="request-1",entity_id="entity-1",evidence_id="evidence-1",
        version_id="version-1",retention_policy_id="policy-1")

def test_archive_restore_and_corrupt_backup(tmp_path):
    app=fixture(tmp_path)
    receipt,ref,meta=app.archive(**params())
    assert app.journal.status("request-1")=="ARCHIVED"
    assert app.journal.verify_chain("request-1")
    assert app.registry.redacted_receipt(receipt,"entity-1")["version_id"]=="version-1"
    assert app.registry.redacted_receipt(receipt,"other") is None
    encrypted=app.store.get(ref)
    assert b"synthetic acquisition evidence" not in encrypted
    assert app.restore_drill(ref=ref,key=b"k"*32,entity_id="entity-1",
        evidence_id="evidence-1",version_id="version-1",
        expected_ciphertext_sha256=meta["ciphertext_sha256"],
        expected_original_sha256=meta["original_sha256"],backup=bytes(encrypted))==meta["original_sha256"]
    with pytest.raises(IntegrationError,match="backup ciphertext corrupt"):
        app.restore_drill(ref=ref,key=b"k"*32,entity_id="entity-1",
            evidence_id="evidence-1",version_id="version-1",
            expected_ciphertext_sha256=meta["ciphertext_sha256"],
            expected_original_sha256=meta["original_sha256"],backup=encrypted[:-1]+b"x")

def test_post_cloud_crash_never_archived(tmp_path):
    app=fixture(tmp_path)
    with pytest.raises(IntegrationError,match="injected"):
        app.archive(**params(),fail_after_cloud=True)
    assert app.journal.status("request-1")=="RECONCILE_REQUIRED"
    assert app.journal.verify_chain("request-1")
    assert app.registry.redacted_receipt("nonexistent","entity-1") is None
    assert len(app.store.objects)==1
    with pytest.raises(IntegrationError,match="explicit reconciliation"):
        app.archive(**params())

def test_scan_mismatch_fails_closed(tmp_path):
    class BadScan(SyntheticTrustedVerifier):
        def scan(self,*,original,request_id):return "0"*64
    app=fixture(tmp_path,BadScan())
    with pytest.raises(IntegrationError,match="scanner digest mismatch"):
        app.archive(**params())
    assert app.journal.status("request-1")=="REJECTED"
    assert app.store.objects=={}

def test_wrong_entity_restore_rejected(tmp_path):
    app=fixture(tmp_path)
    _,ref,meta=app.archive(**params())
    with pytest.raises(Exception):
        app.restore_drill(ref=ref,key=b"k"*32,entity_id="other",
            evidence_id="evidence-1",version_id="version-1",
            expected_ciphertext_sha256=meta["ciphertext_sha256"],
            expected_original_sha256=meta["original_sha256"],backup=app.store.get(ref))
