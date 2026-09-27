import sqlite3
import pytest
from vault.canonical_evidence_registry import CanonicalEvidenceRegistry,RegistryError

def record(reg,**changes):
    p=dict(receipt_id="receipt-1",request_id="request-1",entity_id="entity-1",
        evidence_id="evidence-1",version_id="version-1",original_sha256="a"*64,
        ciphertext_sha256="b"*64,object_ref="objects/"+"1"*48,scan_receipt_ref="scan-1",
        tower_receipt_ref="tower-1",retention_policy_id="policy-1")
    p.update(changes)
    return reg.record_archival(**p)

def test_idempotency_and_correction_lineage(tmp_path):
    reg=CanonicalEvidenceRegistry(tmp_path/"vault.sqlite")
    assert record(reg)=="receipt-1"
    assert record(reg)=="receipt-1"
    assert record(reg,receipt_id="receipt-2",request_id="request-2",
        version_id="version-2",object_ref="objects/"+"2"*48,parent_version_id="version-1")=="receipt-2"
    assert reg.redacted_receipt("receipt-2","entity-1")["parent_version_id"]=="version-1"
    assert reg.redacted_receipt("receipt-2","entity-2") is None
    with pytest.raises(RegistryError,match="conflicting request"):
        record(reg,original_sha256="c"*64)
    with pytest.raises(RegistryError,match="parent"):
        record(reg,receipt_id="receipt-3",request_id="request-3",
            version_id="version-3",object_ref="objects/"+"3"*48,parent_version_id="missing")

def test_snapshot_exact_versions_and_append_only(tmp_path):
    path=tmp_path/"vault.sqlite"
    reg=CanonicalEvidenceRegistry(path)
    record(reg)
    args=dict(snapshot_id="snapshot-1",entity_id="entity-1",acquisition_id="deal-1",
              rule_version="rules-1",evidence_versions=["version-1"])
    digest=reg.seal_decision_snapshot(**args)
    assert reg.seal_decision_snapshot(**args)==digest
    with pytest.raises(RegistryError,match="conflicting snapshot"):
        reg.seal_decision_snapshot(**(args|{"rule_version":"rules-2"}))
    with pytest.raises(RegistryError,match="cross-entity"):
        reg.seal_decision_snapshot(**(args|{"snapshot_id":"snapshot-2","entity_id":"entity-2"}))
    with sqlite3.connect(path) as db:
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("DELETE FROM archival_receipts")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("UPDATE decision_snapshots SET rule_version='other'")

def test_rejects_raw_locations_and_invalid_hash(tmp_path):
    reg=CanonicalEvidenceRegistry(tmp_path/"vault.sqlite")
    with pytest.raises(RegistryError):
        record(reg,object_ref="/tmp/private/file.pdf")
    with pytest.raises(RegistryError):
        record(reg,original_sha256="not-a-hash")

def test_correction_cannot_fork(tmp_path):
    reg=CanonicalEvidenceRegistry(tmp_path/"vault.sqlite")
    record(reg)
    record(reg,receipt_id="receipt-2",request_id="request-2",
        version_id="version-2",object_ref="object-2",parent_version_id="version-1")
    with pytest.raises(RegistryError,match="successor"):
        record(reg,receipt_id="receipt-3",request_id="request-3",
            version_id="version-3",object_ref="object-3",parent_version_id="version-1")
    assert record(reg,receipt_id="receipt-3",request_id="request-3",
        version_id="version-3",object_ref="object-3",parent_version_id="version-2")=="receipt-3"

def test_snapshot_rejects_unhashable_version_input_cleanly(tmp_path):
    reg=CanonicalEvidenceRegistry(tmp_path/"vault.sqlite")
    with pytest.raises(RegistryError,match="invalid opaque"):
        reg.seal_decision_snapshot(snapshot_id="snap-1",entity_id="entity-1",
            acquisition_id="deal-1",rule_version="rules-1",evidence_versions=[["bad"]])
