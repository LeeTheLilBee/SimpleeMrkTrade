"""BBX107-130 persistence for owner-authored expansion intelligence.

These tables store owner research/workflow records only. They never create
Tower/Teller/Vault/Grounds/ATM authority and never promote a user-entered
observation into verified evidence.
"""
from __future__ import annotations
import json, sqlite3
from uuid import uuid4
from .core import now

SCHEMA="""
CREATE TABLE IF NOT EXISTS buybox_owner_thesis (
 id INTEGER PRIMARY KEY CHECK(id=1), payload_json TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS buybox_intelligence_records (
 id TEXT PRIMARY KEY, opportunity_id TEXT, kind TEXT NOT NULL,
 payload_json TEXT NOT NULL, created_at TEXT NOT NULL, actor_ref TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_bbir_op_kind
 ON buybox_intelligence_records(opportunity_id,kind,created_at);
"""

KINDS=frozenset({
 "COUNTERPARTY","CAPEX_ITEM","MARKET_OBSERVATION","PERFORMANCE_ACTUAL",
 "AUTOPSY","QUICK_CAPTURE","TEAM_LANE","COMMUNITY_IMPACT",
})

def ensure_schema(db: sqlite3.Connection):
    db.executescript(SCHEMA)

def _clean_text(value,limit=1000):
    return str(value or "").strip()[:limit]

def load_thesis(db):
    ensure_schema(db)
    row=db.execute("SELECT payload_json,updated_at FROM buybox_owner_thesis WHERE id=1").fetchone()
    if not row:
        return {"priorities":[],"preferred_regions":[],"avoid":[],"sequence":[],"notes":"","updated_at":None}
    value=json.loads(row["payload_json"]); value["updated_at"]=row["updated_at"]; return value

def save_thesis(db,*,priorities,preferred_regions,avoid,sequence,notes):
    ensure_schema(db)
    value={
      "priorities":[_clean_text(x,120) for x in priorities if _clean_text(x,120)][:20],
      "preferred_regions":[_clean_text(x,120) for x in preferred_regions if _clean_text(x,120)][:20],
      "avoid":[_clean_text(x,120) for x in avoid if _clean_text(x,120)][:20],
      "sequence":[_clean_text(x,120) for x in sequence if _clean_text(x,120)][:20],
      "notes":_clean_text(notes,2000),
    }
    at=now()
    db.execute("""INSERT INTO buybox_owner_thesis(id,payload_json,updated_at) VALUES(1,?,?)
      ON CONFLICT(id) DO UPDATE SET payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
      (json.dumps(value,sort_keys=True,separators=(",",":")),at))
    db.commit(); value["updated_at"]=at; return value

def add_record(db,opportunity_id,kind,payload,actor_ref="local_owner"):
    ensure_schema(db)
    if kind not in KINDS: raise ValueError("INTELLIGENCE_KIND_INVALID")
    if not isinstance(payload,dict): raise ValueError("INTELLIGENCE_PAYLOAD_INVALID")
    rid=str(uuid4()); at=now()
    db.execute("INSERT INTO buybox_intelligence_records VALUES(?,?,?,?,?,?)",
      (rid,opportunity_id,kind,json.dumps(payload,sort_keys=True,separators=(",",":")),at,actor_ref))
    db.commit()
    return {"id":rid,"opportunity_id":opportunity_id,"kind":kind,"payload":payload,
            "created_at":at,"actor_ref":actor_ref}

def records(db,*,opportunity_id=None,kind=None):
    ensure_schema(db)
    where=[]; args=[]
    if opportunity_id is not None: where.append("opportunity_id=?"); args.append(opportunity_id)
    if kind is not None: where.append("kind=?"); args.append(kind)
    sql="SELECT * FROM buybox_intelligence_records"
    if where: sql+=" WHERE "+" AND ".join(where)
    sql+=" ORDER BY created_at DESC,id DESC"
    rows=db.execute(sql,args).fetchall()
    return [{"id":r["id"],"opportunity_id":r["opportunity_id"],"kind":r["kind"],
             "payload":json.loads(r["payload_json"]),"created_at":r["created_at"],
             "actor_ref":r["actor_ref"]} for r in rows]
