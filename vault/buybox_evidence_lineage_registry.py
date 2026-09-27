"""Local-safe immutable acquisition evidence lineage and receipt preparation.

No binary storage, provider connection, Vault ingress, or authority grant.
"""
from __future__ import annotations
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Mapping, Any
from vault.buybox_evidence_handoff_contract import validate_buybox_evidence_request, ContractError, request_fingerprint

def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

class EvidenceLineageRegistry:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS evidence_versions (
                    evidence_id TEXT NOT NULL, source_version_id TEXT NOT NULL,
                    source_document_id TEXT NOT NULL, parent_version_id TEXT,
                    correction_of_version_id TEXT, source_sha256 TEXT NOT NULL,
                    request_id TEXT NOT NULL UNIQUE, request_fingerprint TEXT NOT NULL,
                    request_json TEXT NOT NULL, state TEXT NOT NULL CHECK(state='PENDING_TOWER_ARCHIVAL'),
                    PRIMARY KEY(evidence_id,source_version_id)
                );
                CREATE TABLE IF NOT EXISTS decision_snapshots (
                    snapshot_id TEXT PRIMARY KEY, deal_id TEXT NOT NULL,
                    evidence_versions_json TEXT NOT NULL, rule_version TEXT NOT NULL,
                    snapshot_sha256 TEXT NOT NULL
                );
                CREATE TRIGGER IF NOT EXISTS versions_immutable BEFORE UPDATE ON evidence_versions BEGIN SELECT RAISE(ABORT,'immutable version'); END;
                CREATE TRIGGER IF NOT EXISTS versions_no_delete BEFORE DELETE ON evidence_versions BEGIN SELECT RAISE(ABORT,'immutable version'); END;
                CREATE TRIGGER IF NOT EXISTS snapshots_immutable BEFORE UPDATE ON decision_snapshots BEGIN SELECT RAISE(ABORT,'immutable snapshot'); END;
                CREATE TRIGGER IF NOT EXISTS snapshots_no_delete BEFORE DELETE ON decision_snapshots BEGIN SELECT RAISE(ABORT,'immutable snapshot'); END;
            """)

    def _db(self):
        db = sqlite3.connect(self.db_path)
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA busy_timeout=5000")
        return db

    def register_pending_version(self, packet: Mapping[str, Any]) -> dict:
        p = validate_buybox_evidence_request(packet)
        d, a = p["document"], p["acquisition"]
        fingerprint = request_fingerprint(p)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute("SELECT request_fingerprint,evidence_id,source_version_id FROM evidence_versions WHERE request_id=?", (p["request_id"],)).fetchone()
            if prior:
                if prior[0] != fingerprint:
                    raise ContractError("changed replay rejected")
                return {"evidence_id": prior[1], "source_version_id": prior[2], "state": "PENDING_TOWER_ARCHIVAL", "idempotent_replay": True}
            previous = db.execute("SELECT source_sha256 FROM evidence_versions WHERE evidence_id=? AND source_version_id=?", (a["evidence_id"], d["parent_version_id"])).fetchone() if d["parent_version_id"] else None
            if d["parent_version_id"] and not previous:
                raise ContractError("parent version missing")
            if d["correction_of_version_id"] and not db.execute("SELECT 1 FROM evidence_versions WHERE evidence_id=? AND source_version_id=?", (a["evidence_id"],d["correction_of_version_id"])).fetchone():
                raise ContractError("correction target missing")
            if d["parent_version_id"] is None and db.execute("SELECT 1 FROM evidence_versions WHERE evidence_id=?", (a["evidence_id"],)).fetchone():
                raise ContractError("subsequent version requires parent")
            db.execute("INSERT INTO evidence_versions VALUES (?,?,?,?,?,?,?,?,?,?)", (a["evidence_id"],d["source_version_id"],d["source_document_id"],d["parent_version_id"],d["correction_of_version_id"],d["sha256"],p["request_id"],fingerprint,_json(p),"PENDING_TOWER_ARCHIVAL"))
        return {"evidence_id": a["evidence_id"], "source_version_id": d["source_version_id"], "state": "PENDING_TOWER_ARCHIVAL", "idempotent_replay": False}

    def seal_decision_snapshot(self, snapshot_id: str, deal_id: str, versions: list[dict], rule_version: str) -> dict:
        from vault.buybox_evidence_handoff_contract import _id
        for value, label in ((snapshot_id,"snapshot_id"),(deal_id,"deal_id"),(rule_version,"rule_version")):
            _id(value,label)
        if not isinstance(versions,list) or not versions:
            raise ContractError("snapshot requires evidence versions")
        normalized = []
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            for item in versions:
                if not isinstance(item,dict) or set(item)!={"evidence_id","source_version_id","sha256"}:
                    raise ContractError("invalid evidence version reference")
                for key,value in item.items(): _id(value,key) if key!="sha256" else None
                row=db.execute("SELECT source_sha256 FROM evidence_versions WHERE evidence_id=? AND source_version_id=?", (item["evidence_id"],item["source_version_id"])).fetchone()
                if not row or row[0]!=item["sha256"]:
                    raise ContractError("unverified evidence version reference")
                normalized.append(dict(item))
            material={"snapshot_id":snapshot_id,"deal_id":deal_id,"evidence_versions":normalized,"rule_version":rule_version}
            digest=hashlib.sha256(_json(material).encode()).hexdigest()
            prior=db.execute("SELECT snapshot_sha256 FROM decision_snapshots WHERE snapshot_id=?",(snapshot_id,)).fetchone()
            if prior:
                if prior[0]!=digest: raise ContractError("changed snapshot replay rejected")
                return {"snapshot_id":snapshot_id,"snapshot_sha256":digest,"idempotent_replay":True}
            db.execute("INSERT INTO decision_snapshots VALUES (?,?,?,?,?)",(snapshot_id,deal_id,_json(normalized),rule_version,digest))
        return {"snapshot_id":snapshot_id,"snapshot_sha256":digest,"idempotent_replay":False}
