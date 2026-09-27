import sqlite3
import pytest
from vault.test_buybox_evidence_handoff_contract import packet
from vault.buybox_evidence_lineage_registry import EvidenceLineageRegistry
from vault.buybox_evidence_handoff_contract import ContractError

def test_version_correction_snapshot_and_replay(tmp_path):
    registry=EvidenceLineageRegistry(tmp_path/"lineage.sqlite")
    p=packet()
    first=registry.register_pending_version(p)
    assert first["state"]=="PENDING_TOWER_ARCHIVAL"
    assert registry.register_pending_version(p)["idempotent_replay"] is True
    changed=packet()
    changed["document"]["sha256"]="b"*64
    with pytest.raises(ContractError,match="changed replay"):
        registry.register_pending_version(changed)
    corrected=packet()
    corrected["request_id"]="request-2"
    corrected["idempotency_key"]="request-2-v1"
    corrected["document"].update(source_version_id="version-2",parent_version_id="version-1",correction_of_version_id="version-1",sha256="b"*64)
    assert registry.register_pending_version(corrected)["source_version_id"]=="version-2"
    refs=[{"evidence_id":"evidence-1","source_version_id":"version-1","sha256":"a"*64}]
    snapshot=registry.seal_decision_snapshot("snapshot-1","deal-1",refs,"rules-1")
    assert registry.seal_decision_snapshot("snapshot-1","deal-1",refs,"rules-1")["idempotent_replay"]
    with pytest.raises(ContractError,match="changed snapshot"):
        registry.seal_decision_snapshot("snapshot-1","deal-1",[{"evidence_id":"evidence-1","source_version_id":"version-2","sha256":"b"*64}],"rules-1")
    with sqlite3.connect(registry.db_path) as db:
        with pytest.raises(sqlite3.IntegrityError,match="immutable"):
            db.execute("DELETE FROM evidence_versions")
        db.rollback()
        with pytest.raises(sqlite3.IntegrityError,match="immutable"):
            db.execute("UPDATE decision_snapshots SET rule_version='changed'")
        db.rollback()

def test_missing_parent_and_unknown_evidence_rejected(tmp_path):
    registry=EvidenceLineageRegistry(tmp_path/"lineage.sqlite")
    p=packet()
    p["document"]["parent_version_id"]="missing"
    with pytest.raises(ContractError,match="parent version"):
        registry.register_pending_version(p)
    with pytest.raises(ContractError,match="unverified"):
        registry.seal_decision_snapshot("snapshot-1","deal-1",[{"evidence_id":"unknown","source_version_id":"v1","sha256":"a"*64}],"rules-1")
