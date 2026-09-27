"""Vault internal archival workflow journal, not an authorization or upload endpoint.

A trusted orchestrator must verify Tower/scan/Cloud receipts before supplying
receipt digests. This module prevents skipped states and false ARCHIVED labels;
it does not independently authenticate external receipts.
"""
from __future__ import annotations
import hashlib
import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path

ID=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
SHA=re.compile(r"^[a-f0-9]{64}$")
STATES=("RECEIVED","QUARANTINED","VERIFIED","ENCRYPTED","CLOUD_COMMITTED","ARCHIVED","RECONCILE_REQUIRED","REJECTED")
NEXT={
 "RECEIVED":{"QUARANTINED","REJECTED"},
 "QUARANTINED":{"VERIFIED","REJECTED"},
 "VERIFIED":{"ENCRYPTED","REJECTED"},
 "ENCRYPTED":{"CLOUD_COMMITTED","RECONCILE_REQUIRED","REJECTED"},
 "CLOUD_COMMITTED":{"ARCHIVED","RECONCILE_REQUIRED"},
 "RECONCILE_REQUIRED":{"CLOUD_COMMITTED","REJECTED"},
 "ARCHIVED":set(),"REJECTED":set()
}
class JournalError(ValueError): pass

def valid_id(v):
    if not isinstance(v,str) or not ID.fullmatch(v): raise JournalError("invalid identifier")
    return v

def valid_hash(v):
    if not isinstance(v,str) or not SHA.fullmatch(v): raise JournalError("invalid receipt digest")
    return v

class ArchivalJournal:
    def __init__(self,path: str | Path):
        self.path=str(path)
        with self.db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS workflows(
                request_id TEXT PRIMARY KEY,entity_id TEXT NOT NULL,evidence_id TEXT NOT NULL,
                version_id TEXT NOT NULL,state TEXT NOT NULL,step INTEGER NOT NULL,
                cloud_digest TEXT,registry_digest TEXT,UNIQUE(entity_id,version_id));
            CREATE TABLE IF NOT EXISTS workflow_events(
                request_id TEXT NOT NULL,step INTEGER NOT NULL,from_state TEXT,
                to_state TEXT NOT NULL,receipt_digest TEXT,previous_hash TEXT,
                event_hash TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT
                (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                PRIMARY KEY(request_id,step),
                FOREIGN KEY(request_id) REFERENCES workflows(request_id));
            CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON workflow_events
                BEGIN SELECT RAISE(ABORT,'immutable event'); END;
            CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON workflow_events
                BEGIN SELECT RAISE(ABORT,'immutable event'); END;
            """)
    @contextmanager
    def db(self):
        db=sqlite3.connect(self.path,timeout=10)
        try:
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA busy_timeout=10000")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally: db.close()
    @staticmethod
    def digest(request_id,step,old,new,receipt,previous):
        data=json.dumps([request_id,step,old,new,receipt,previous],separators=(",",":"))
        return hashlib.sha256(data.encode()).hexdigest()
    def begin(self,*,request_id,entity_id,evidence_id,version_id):
        for v in (request_id,entity_id,evidence_id,version_id):valid_id(v)
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            existing=db.execute("SELECT entity_id,evidence_id,version_id FROM workflows WHERE request_id=?",(request_id,)).fetchone()
            if existing:
                if existing==(entity_id,evidence_id,version_id):
                    return db.execute("SELECT state FROM workflows WHERE request_id=?",(request_id,)).fetchone()[0]
                raise JournalError("conflicting request replay")
            event=self.digest(request_id,0,None,"RECEIVED",None,None)
            db.execute("INSERT INTO workflows VALUES (?,?,?,?,?,?,NULL,NULL)",
                (request_id,entity_id,evidence_id,version_id,"RECEIVED",0))
            db.execute("INSERT INTO workflow_events(request_id,step,from_state,to_state,receipt_digest,previous_hash,event_hash) VALUES (?,?,?,?,?,?,?)",
                (request_id,0,None,"RECEIVED",None,None,event))
        return "RECEIVED"
    def status(self,request_id):
        valid_id(request_id)
        with self.db() as db:
            row=db.execute("SELECT state FROM workflows WHERE request_id=?",(request_id,)).fetchone()
        return row[0] if row else None
    def advance(self,*,request_id,to_state,receipt_digest=None,expected_state):
        valid_id(request_id)
        if to_state not in STATES:raise JournalError("invalid state")
        if receipt_digest is not None:valid_hash(receipt_digest)
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT state,step,cloud_digest,registry_digest FROM workflows WHERE request_id=?",(request_id,)).fetchone()
            if not row:raise JournalError("unknown workflow")
            old,step,cloud,registry=row
            if old!=expected_state:raise JournalError("stale state or replay")
            if to_state not in NEXT[old]:raise JournalError("invalid state transition")
            if to_state in {"VERIFIED","ENCRYPTED","CLOUD_COMMITTED","ARCHIVED"} and receipt_digest is None:
                raise JournalError("verified transition requires receipt digest")
            if to_state=="CLOUD_COMMITTED":cloud=receipt_digest
            if to_state=="ARCHIVED":
                if not cloud:raise JournalError("cloud commit missing")
                registry=receipt_digest
                if registry==cloud:raise JournalError("registry and cloud receipts must be distinct")
            prior=db.execute("SELECT event_hash FROM workflow_events WHERE request_id=? AND step=?",(request_id,step)).fetchone()[0]
            event=self.digest(request_id,step+1,old,to_state,receipt_digest,prior)
            db.execute("UPDATE workflows SET state=?,step=?,cloud_digest=?,registry_digest=? WHERE request_id=?",
                (to_state,step+1,cloud,registry,request_id))
            db.execute("INSERT INTO workflow_events(request_id,step,from_state,to_state,receipt_digest,previous_hash,event_hash) VALUES (?,?,?,?,?,?,?)",
                (request_id,step+1,old,to_state,receipt_digest,prior,event))
        return to_state
    def verify_chain(self,request_id):
        valid_id(request_id)
        with self.db() as db:
            rows=db.execute("SELECT step,from_state,to_state,receipt_digest,previous_hash,event_hash FROM workflow_events WHERE request_id=? ORDER BY step",(request_id,)).fetchall()
            state=db.execute("SELECT state,step FROM workflows WHERE request_id=?",(request_id,)).fetchone()
        if not rows or not state:return False
        prior=None
        for index,(step,old,new,receipt,prev,digest) in enumerate(rows):
            if step!=index or prev!=prior or (index and old!=rows[index-1][2]):return False
            if self.digest(request_id,step,old,new,receipt,prev)!=digest:return False
            prior=digest
        if (rows[-1][2],rows[-1][0])!=state:return False
        if rows[0][1] is not None or rows[0][2]!="RECEIVED":return False
        for i in range(1,len(rows)):
            old,new=rows[i][1],rows[i][2]
            if new not in NEXT.get(old,set()):return False
            if new in {"VERIFIED","ENCRYPTED","CLOUD_COMMITTED","ARCHIVED"} and not rows[i][3]:return False
        return True
    def owner_summary(self,entity_id):
        valid_id(entity_id)
        with self.db() as db:
            rows=db.execute("SELECT state,COUNT(*) FROM workflows WHERE entity_id=? GROUP BY state",(entity_id,)).fetchall()
        return dict(rows)
