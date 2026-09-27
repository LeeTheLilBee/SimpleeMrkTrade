"""Vault canonical evidence metadata ledger v1.

This is a persistent *metadata* ledger, not an object-storage or authorization
endpoint. The trusted Tower/Vault orchestration layer must verify authorization,
scan original bytes, commit encrypted storage and reconcile its receipt BEFORE
calling record_archival. No client-supplied 'authorized' boolean is accepted.
"""
from __future__ import annotations
import hashlib
import json
import re
import sqlite3
from pathlib import Path

_ID=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_SHA=re.compile(r"^[a-f0-9]{64}$")
class RegistryError(ValueError): pass

def _id(value):
    if not isinstance(value,str) or not _ID.fullmatch(value):
        raise RegistryError("invalid opaque identifier")
    return value

def _hash(value):
    if not isinstance(value,str) or not _SHA.fullmatch(value):
        raise RegistryError("invalid sha256")
    return value

class CanonicalEvidenceRegistry:
    def __init__(self, db_path: str | Path):
        self.path=str(db_path)
        with self._db() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS archival_receipts(
                  receipt_id TEXT PRIMARY KEY, request_id TEXT UNIQUE NOT NULL,
                  entity_id TEXT NOT NULL, evidence_id TEXT NOT NULL,
                  version_id TEXT NOT NULL UNIQUE, parent_version_id TEXT,
                  original_sha256 TEXT NOT NULL, ciphertext_sha256 TEXT NOT NULL,
                  object_ref TEXT NOT NULL UNIQUE, scan_receipt_ref TEXT NOT NULL,
                  tower_receipt_ref TEXT NOT NULL, retention_policy_id TEXT NOT NULL,
                  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                  UNIQUE(entity_id,evidence_id,version_id),
                  FOREIGN KEY(parent_version_id) REFERENCES archival_receipts(version_id),
                  UNIQUE(parent_version_id)
                );
                CREATE TABLE IF NOT EXISTS decision_snapshots(
                  snapshot_id TEXT PRIMARY KEY, entity_id TEXT NOT NULL,
                  acquisition_id TEXT NOT NULL, rule_version TEXT NOT NULL,
                  evidence_versions_json TEXT NOT NULL, snapshot_sha256 TEXT NOT NULL,
                  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                );
                CREATE TRIGGER IF NOT EXISTS archival_no_update BEFORE UPDATE ON archival_receipts
                  BEGIN SELECT RAISE(ABORT,'append-only archival receipts'); END;
                CREATE TRIGGER IF NOT EXISTS archival_no_delete BEFORE DELETE ON archival_receipts
                  BEGIN SELECT RAISE(ABORT,'append-only archival receipts'); END;
                CREATE TRIGGER IF NOT EXISTS snapshot_no_update BEFORE UPDATE ON decision_snapshots
                  BEGIN SELECT RAISE(ABORT,'append-only snapshots'); END;
                CREATE TRIGGER IF NOT EXISTS snapshot_no_delete BEFORE DELETE ON decision_snapshots
                  BEGIN SELECT RAISE(ABORT,'append-only snapshots'); END;
            """)
    def _db(self):
        db=sqlite3.connect(self.path,timeout=10)
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA busy_timeout=10000")
        return db

    def record_archival(self, *, receipt_id, request_id, entity_id, evidence_id,
        version_id, original_sha256, ciphertext_sha256, object_ref,
        scan_receipt_ref, tower_receipt_ref, retention_policy_id,
        parent_version_id=None):
        ids=[receipt_id,request_id,entity_id,evidence_id,version_id,object_ref,
             scan_receipt_ref,tower_receipt_ref,retention_policy_id]
        for item in ids: _id(item)
        _hash(original_sha256);_hash(ciphertext_sha256)
        if parent_version_id is not None: _id(parent_version_id)
        values=(receipt_id,request_id,entity_id,evidence_id,version_id,parent_version_id,
                original_sha256,ciphertext_sha256,object_ref,scan_receipt_ref,
                tower_receipt_ref,retention_policy_id)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            prior=db.execute("SELECT receipt_id,request_id,entity_id,evidence_id,version_id,parent_version_id,original_sha256,ciphertext_sha256,object_ref,scan_receipt_ref,tower_receipt_ref,retention_policy_id FROM archival_receipts WHERE request_id=?",(request_id,)).fetchone()
            if prior is not None:
                if prior==values: return receipt_id
                raise RegistryError("conflicting request replay")
            if parent_version_id:
                parent=db.execute("SELECT entity_id,evidence_id FROM archival_receipts WHERE version_id=?",(parent_version_id,)).fetchone()
                if parent!=(entity_id,evidence_id): raise RegistryError("missing or cross-entity parent version")
                if db.execute("SELECT 1 FROM archival_receipts WHERE parent_version_id=?",(parent_version_id,)).fetchone():
                    raise RegistryError("parent already has a successor; resolve correction conflict")
            else:
                if db.execute("SELECT 1 FROM archival_receipts WHERE entity_id=? AND evidence_id=?",(entity_id,evidence_id)).fetchone():
                    raise RegistryError("subsequent version requires parent")
            try:
                db.execute("""INSERT INTO archival_receipts(receipt_id,request_id,entity_id,evidence_id,version_id,parent_version_id,original_sha256,ciphertext_sha256,object_ref,scan_receipt_ref,tower_receipt_ref,retention_policy_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",values)
            except sqlite3.IntegrityError as exc: raise RegistryError("duplicate archival identity") from exc
        return receipt_id

    def seal_decision_snapshot(self, *, snapshot_id, entity_id, acquisition_id,
                               rule_version, evidence_versions):
        for value in (snapshot_id,entity_id,acquisition_id,rule_version): _id(value)
        if not isinstance(evidence_versions,list) or not evidence_versions:
            raise RegistryError("snapshot needs evidence versions")
        for value in evidence_versions: _id(value)
        if len(evidence_versions)!=len(set(evidence_versions)):
            raise RegistryError("duplicate evidence version")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            for version in evidence_versions:
                if not db.execute("SELECT 1 FROM archival_receipts WHERE version_id=? AND entity_id=?",(version,entity_id)).fetchone():
                    raise RegistryError("snapshot references unarchived or cross-entity evidence")
            payload=json.dumps({"entity_id":entity_id,"acquisition_id":acquisition_id,
              "rule_version":rule_version,"evidence_versions":sorted(evidence_versions)},
              sort_keys=True,separators=(",",":"))
            digest=hashlib.sha256(payload.encode()).hexdigest()
            previous=db.execute("SELECT snapshot_sha256 FROM decision_snapshots WHERE snapshot_id=?",(snapshot_id,)).fetchone()
            if previous:
                if previous[0]==digest: return digest
                raise RegistryError("conflicting snapshot replay")
            db.execute("INSERT INTO decision_snapshots(snapshot_id,entity_id,acquisition_id,rule_version,evidence_versions_json,snapshot_sha256) VALUES (?,?,?,?,?,?)",
                (snapshot_id,entity_id,acquisition_id,rule_version,payload,digest))
        return digest

    def redacted_receipt(self, receipt_id: str, entity_id: str):
        _id(receipt_id);_id(entity_id)
        with self._db() as db:
            row=db.execute("SELECT receipt_id,evidence_id,version_id,parent_version_id,original_sha256,created_at FROM archival_receipts WHERE receipt_id=? AND entity_id=?",(receipt_id,entity_id)).fetchone()
        if row is None: return None
        return dict(zip(("receipt_id","evidence_id","version_id","parent_version_id","verified_original_sha256","created_at"),row))
