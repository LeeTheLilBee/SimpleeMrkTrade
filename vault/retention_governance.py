"""Internal Vault retention/hold metadata. No object deletion capability.

Retention policy and legal holds are append-only events. Disposition is a
review decision only; a separate Tower-approved deletion workflow is required.
"""
from __future__ import annotations
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from vault.archival_transaction_journal import valid_id

class GovernanceError(ValueError):pass
class RetentionGovernance:
    def __init__(self,path: str | Path):
        self.path=str(path)
        with self.db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS governance_events(
              event_id TEXT PRIMARY KEY,entity_id TEXT NOT NULL,version_id TEXT NOT NULL,
              action TEXT NOT NULL,policy_id TEXT,reason TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
            CREATE TRIGGER IF NOT EXISTS governance_no_update BEFORE UPDATE ON governance_events
              BEGIN SELECT RAISE(ABORT,'append-only governance'); END;
            CREATE TRIGGER IF NOT EXISTS governance_no_delete BEFORE DELETE ON governance_events
              BEGIN SELECT RAISE(ABORT,'append-only governance'); END;
            """)
    @contextmanager
    def db(self):
        db=sqlite3.connect(self.path,timeout=10)
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:db.close()
    def record(self,*,event_id,entity_id,version_id,action,reason,policy_id=None):
        for v in (event_id,entity_id,version_id):valid_id(v)
        if action not in {"POLICY_SET","HOLD_PLACED","HOLD_RELEASED","DISPOSITION_REVIEWED"}:
            raise GovernanceError("unsupported governance action")
        if not isinstance(reason,str) or not reason.strip() or len(reason)>1024:
            raise GovernanceError("reason required")
        if action=="POLICY_SET":
            valid_id(policy_id)
        elif policy_id is not None:raise GovernanceError("policy only valid on POLICY_SET")
        with self.db() as db:
            previous=db.execute("SELECT entity_id,version_id,action,policy_id,reason FROM governance_events WHERE event_id=?",(event_id,)).fetchone()
            expected=(entity_id,version_id,action,policy_id,reason)
            if previous:
                if previous==expected:return event_id
                raise GovernanceError("conflicting event replay")
            events=db.execute("SELECT action FROM governance_events WHERE entity_id=? AND version_id=? ORDER BY rowid",(entity_id,version_id)).fetchall()
            held=False
            for (prior,) in events:
                if prior=="HOLD_PLACED":held=True
                elif prior=="HOLD_RELEASED":held=False
            if action=="HOLD_PLACED" and held:raise GovernanceError("hold already active")
            if action=="HOLD_RELEASED" and not held:raise GovernanceError("no active hold")
            if action=="DISPOSITION_REVIEWED" and held:raise GovernanceError("legal hold blocks disposition")
            db.execute("INSERT INTO governance_events(event_id,entity_id,version_id,action,policy_id,reason) VALUES (?,?,?,?,?,?)",
                       (event_id,entity_id,version_id,action,policy_id,reason))
        return event_id
    def status(self,*,entity_id,version_id):
        valid_id(entity_id);valid_id(version_id)
        with self.db() as db:
            events=db.execute("SELECT action,policy_id FROM governance_events WHERE entity_id=? AND version_id=? ORDER BY rowid",(entity_id,version_id)).fetchall()
        held=False;policy=None
        for action,p in events:
            if action=="POLICY_SET":policy=p
            elif action=="HOLD_PLACED":held=True
            elif action=="HOLD_RELEASED":held=False
        return {"policy_id":policy,"legal_hold":held,"disposition_blocked":held or policy is None}
