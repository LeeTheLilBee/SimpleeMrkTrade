"""BBX136–155 owner-experience, provenance, search and acceptance helpers.

This layer improves navigation and review speed only. It never upgrades owner
notes into evidence, fabricates external readiness, or creates acquisition
authority.
"""
from __future__ import annotations
import json, sqlite3
from datetime import datetime, timezone
from .external_proof_gate import integration_readiness

UX_SCHEMA="""
CREATE TABLE IF NOT EXISTS buybox_owner_preferences (
 id INTEGER PRIMARY KEY CHECK(id=1),
 density TEXT NOT NULL CHECK(density IN ('CALM','STANDARD','DEEP')),
 pulse_seen_at TEXT,
 updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS buybox_owner_triage (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 opportunity_id TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('FOCUS','WATCH','PARKED','ARCHIVE_CANDIDATE')),
 note TEXT NOT NULL,
 actor_ref TEXT NOT NULL,
 created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_bbx_triage_op_created
 ON buybox_owner_triage(opportunity_id,created_at DESC,id DESC);
CREATE INDEX IF NOT EXISTS idx_bbx_events_occurred
 ON events(occurred_at DESC,event_id DESC);
CREATE TABLE IF NOT EXISTS buybox_acceptance_defects (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 area TEXT NOT NULL, severity TEXT NOT NULL,
 title TEXT NOT NULL, detail TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('OPEN','RESOLVED')),
 actor_ref TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_bbx_acceptance_defects
 ON buybox_acceptance_defects(status,id DESC);
CREATE INDEX IF NOT EXISTS idx_bbx_opportunities_vertical_name
 ON opportunities(vertical,name);
"""
DENSITIES=frozenset({"CALM","STANDARD","DEEP"})
TRIAGE_STATES=frozenset({"FOCUS","WATCH","PARKED","ARCHIVE_CANDIDATE"})

def _now():
    return datetime.now(timezone.utc).isoformat()

def ensure_ux_schema(db: sqlite3.Connection):
    db.executescript(UX_SCHEMA)
    row=db.execute("SELECT id FROM buybox_owner_preferences WHERE id=1").fetchone()
    if row is None:
        at=_now()
        db.execute("INSERT INTO buybox_owner_preferences VALUES(1,'STANDARD',NULL,?)",(at,))
        db.commit()

def preferences(db):
    ensure_ux_schema(db)
    row=db.execute("SELECT density,pulse_seen_at,updated_at FROM buybox_owner_preferences WHERE id=1").fetchone()
    return dict(row)

def set_density(db,density):
    ensure_ux_schema(db)
    density=str(density or "").upper()
    if density not in DENSITIES: raise ValueError("DENSITY_INVALID")
    at=_now()
    db.execute("UPDATE buybox_owner_preferences SET density=?,updated_at=? WHERE id=1",(density,at))
    db.commit()
    return preferences(db)

def mark_pulse_seen(db):
    ensure_ux_schema(db)
    at=_now()
    db.execute("UPDATE buybox_owner_preferences SET pulse_seen_at=?,updated_at=? WHERE id=1",(at,at))
    db.commit()
    return preferences(db)

def record_triage(db,opportunity_id,state,note,actor_ref):
    ensure_ux_schema(db)
    state=str(state or "").upper()
    if state not in TRIAGE_STATES: raise ValueError("TRIAGE_STATE_INVALID")
    note=str(note or "").strip()[:500]
    actor=str(actor_ref or "").strip()[:255]
    if not actor: raise ValueError("TRIAGE_ACTOR_REQUIRED")
    if db.execute("SELECT 1 FROM opportunities WHERE id=?",(opportunity_id,)).fetchone() is None:
        raise ValueError("OPPORTUNITY_NOT_FOUND")
    at=_now()
    db.execute("INSERT INTO buybox_owner_triage(opportunity_id,state,note,actor_ref,created_at) VALUES(?,?,?,?,?)",
               (opportunity_id,state,note,actor,at))
    db.commit()
    return {"opportunity_id":opportunity_id,"state":state,"note":note,"actor_ref":actor,"created_at":at}

def latest_triage(db,opportunity_id):
    ensure_ux_schema(db)
    row=db.execute("""SELECT opportunity_id,state,note,actor_ref,created_at
      FROM buybox_owner_triage WHERE opportunity_id=?
      ORDER BY id DESC LIMIT 1""",(opportunity_id,)).fetchone()
    return dict(row) if row else None

def triage_map(db,ids):
    ensure_ux_schema(db)
    wanted=set(ids)
    if not wanted: return {}
    rows=db.execute("""SELECT t.opportunity_id,t.state,t.note,t.actor_ref,t.created_at
      FROM buybox_owner_triage t
      JOIN (SELECT opportunity_id,MAX(id) AS max_id FROM buybox_owner_triage
            GROUP BY opportunity_id) latest ON latest.max_id=t.id""").fetchall()
    return {r["opportunity_id"]:dict(r) for r in rows if r["opportunity_id"] in wanted}

def universal_search(db,query,*,limit=40):
    ensure_ux_schema(db)
    q=str(query or "").strip()
    if not q: return []
    limit=max(1,min(int(limit),100))
    like="%"+q.replace("%","\\%").replace("_","\\_")+"%"
    rows=db.execute("""SELECT id,vertical,name,current_json FROM opportunities
      WHERE name LIKE ? ESCAPE '\\' OR vertical LIKE ? ESCAPE '\\'
         OR current_json LIKE ? ESCAPE '\\'
      ORDER BY name LIMIT ?""",(like,like,like,limit)).fetchall()
    out=[]
    for row in rows:
        op=json.loads(row["current_json"])
        where=[]
        if q.lower() in op.get("name","").lower(): where.append("name")
        loc=op.get("location",{})
        if q.lower() in (loc.get("city") or "").lower() or q.lower() in (loc.get("region") or "").lower():
            where.append("location")
        if any(q.lower() in str(x).lower() for x in op.get("sources",[])): where.append("source")
        if any(q.lower() in str(x).lower() for x in op.get("evidence",[])): where.append("evidence")
        if any(q.lower() in str(x).lower() for x in op.get("owner_notes",[])): where.append("owner note")
        out.append({"id":op["id"],"name":op["name"],"vertical":op["vertical"],
                    "location":op.get("location",{}),"lifecycle":op.get("lifecycle"),
                    "matched_in":where or ["record"]})
    return out

def paged_opportunities(db,*,vertical=None,query="",page=1,page_size=24):
    ensure_ux_schema(db)
    page=max(1,int(page)); page_size=max(6,min(int(page_size),60))
    where=[]; args=[]
    if vertical:
        where.append("vertical=?"); args.append(vertical)
    q=str(query or "").strip()
    if q:
        like="%"+q.replace("%","\\%").replace("_","\\_")+"%"
        where.append("(name LIKE ? ESCAPE '\\' OR current_json LIKE ? ESCAPE '\\')")
        args.extend([like,like])
    clause=(" WHERE "+" AND ".join(where)) if where else ""
    total=db.execute("SELECT COUNT(*) AS n FROM opportunities"+clause,args).fetchone()["n"]
    rows=db.execute("SELECT current_json FROM opportunities"+clause+" ORDER BY name LIMIT ? OFFSET ?",
                    [*args,page_size,(page-1)*page_size]).fetchall()
    return {"items":[json.loads(r["current_json"]) for r in rows],"total":total,
            "page":page,"page_size":page_size,
            "pages":max(1,(total+page_size-1)//page_size)}

def pulse_snapshot(db):
    ensure_ux_schema(db)
    pref=preferences(db)
    rows=db.execute("SELECT current_json FROM opportunities").fetchall()
    ops=[json.loads(r["current_json"]) for r in rows]
    active=[op for op in ops if op.get("lifecycle")!="ARCHIVED"]
    triage=triage_map(db,[op["id"] for op in active])
    needs=sum(1 for op in active if triage.get(op["id"],{}).get("state")=="FOCUS")
    blockers=0
    for op in active:
        ready=integration_readiness(op)
        if ready.get("source_state")!="EXTERNAL_PROOFS_COMPLETE_OWNER_RELEASE_STILL_REQUIRED":
            blockers+=1
    since=pref.get("pulse_seen_at")
    if since:
        changed=db.execute("SELECT COUNT(*) AS n FROM events WHERE occurred_at>?",(since,)).fetchone()["n"]
    else:
        changed=db.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]
    return {"active_opportunities":len(active),"needs_owner":needs,
            "external_blockers":blockers,"changed_since_seen":changed,
            "seen_at":since,"density":pref["density"]}

def integration_cockpit(opportunities):
    systems=("TOWER_PROTECTED_ACTION","TELLER_MONEY_AND_MANAGEMENT","VAULT_CANONICAL_ARCHIVAL","OPERATIONS_RECEIVER_ACCEPTANCE")
    labels={
      "TOWER_PROTECTED_ACTION":"Tower protected action",
      "TELLER_MONEY_AND_MANAGEMENT":"Teller money + management",
      "VAULT_CANONICAL_ARCHIVAL":"Vault canonical archival",
      "OPERATIONS_RECEIVER_ACCEPTANCE":"Operations receiver",
    }
    reports=[(op,integration_readiness(op)) for op in opportunities]
    rows=[]
    for kind in systems:
        applicable=[(op,report) for op,report in reports
                    if kind!="OPERATIONS_RECEIVER_ACCEPTANCE"
                    or op.get("vertical") in ("atm","multifamily")]
        required=len(applicable)
        present=sum(kind not in report.get("missing",[]) for _,report in applicable)
        rows.append({"kind":kind,"label":labels[kind],"present":present,"required":required,
                     "state":"COMPLETE" if required and present==required else
                             "NOT_APPLICABLE" if required==0 else
                             "PARTIAL" if present else "AWAITING_EXTERNAL_PROOF"})
    return rows

def _flatten(prefix,value,out):
    if isinstance(value,dict):
        for key in sorted(value):
            if key in ("updated_at","version","external_proofs"): continue
            _flatten(prefix+"."+key if prefix else key,value[key],out)
    elif isinstance(value,list):
        out[prefix]=f"{len(value)} item(s)"
    else:
        out[prefix]=value

def revision_diff(db,opportunity_id):
    rows=db.execute("""SELECT revision,snapshot_json,occurred_at FROM revisions
      WHERE opportunity_id=? ORDER BY revision DESC LIMIT 2""",(opportunity_id,)).fetchall()
    if len(rows)<2:
        return {"from_revision":None,"to_revision":rows[0]["revision"] if rows else None,"changes":[]}
    newer,older=rows[0],rows[1]
    left={}; right={}
    _flatten("",json.loads(older["snapshot_json"]),left)
    _flatten("",json.loads(newer["snapshot_json"]),right)
    changes=[]
    for key in sorted(set(left)|set(right)):
        if left.get(key)!=right.get(key):
            changes.append({"field":key,"before":left.get(key),"after":right.get(key)})
    return {"from_revision":older["revision"],"to_revision":newer["revision"],
            "occurred_at":newer["occurred_at"],"changes":changes[:80]}

def provenance(op,analysis):
    rows=[]
    for finding in analysis.get("findings",[]):
        rows.append({"kind":"RULE_FINDING","label":finding.get("rule_id"),
                     "value":finding.get("reason"),"source":"BuyBox deterministic rules"})
    for e in op.get("evidence",[]):
        rows.append({"kind":"EVIDENCE","label":e.get("kind"),"value":e.get("status"),
                     "source":e.get("source") or e.get("reference") or "Recorded source"})
    for key,val in op.get("metrics",{}).items():
        rows.append({"kind":"METRIC","label":key,"value":val.get("value"),
                     "source":val.get("evidence_id") or "Linked reviewed evidence"})
    for proof in op.get("external_proofs",[]):
        rows.append({"kind":"EXTERNAL_PROOF","label":proof.get("kind"),
                     "value":proof.get("receipt_ref"),"source":proof.get("issuer")})
    return rows

def acceptance_steps():
    return [
      {"id":"discover","label":"Discover","path":"/","check":"Create/find a real opportunity and verify empty/search states."},
      {"id":"diligence","label":"Diligence","path":None,"check":"Open a deal and verify evidence, provenance and source review."},
      {"id":"finance","label":"Financing + Insurance","path":None,"check":"Verify stale/recheck states and source-linked cost modeling."},
      {"id":"decision","label":"Decision + Offer","path":None,"check":"Review Red Team, Decision Desk and Offer Lab authority boundaries."},
      {"id":"closing","label":"Closing","path":None,"check":"Verify closing review never claims external authority."},
      {"id":"integration","label":"Integration","path":"/integration-cockpit","check":"Verify Tower/Teller/Vault/operations proof states."},
      {"id":"handoff","label":"Handoff","path":None,"check":"Verify post-close receiver acceptance remains externally proven."},
    ]

def record_acceptance_defect(db,*,area,severity,title,detail,actor_ref):
    ensure_ux_schema(db)
    sev=str(severity or "").upper()
    if sev not in {"LOW","MEDIUM","HIGH","BLOCKER"}: raise ValueError("DEFECT_SEVERITY_INVALID")
    area=str(area or "").strip()[:100]; title=str(title or "").strip()[:180]
    detail=str(detail or "").strip()[:2000]; actor=str(actor_ref or "").strip()[:255]
    if not area or not title or not detail or not actor: raise ValueError("DEFECT_FIELDS_REQUIRED")
    at=_now()
    cur=db.execute("""INSERT INTO buybox_acceptance_defects
      (area,severity,title,detail,status,actor_ref,created_at)
      VALUES(?,?,?,?, 'OPEN',?,?)""",(area,sev,title,detail,actor,at))
    db.commit()
    return {"id":cur.lastrowid,"area":area,"severity":sev,"title":title,
            "detail":detail,"status":"OPEN","actor_ref":actor,"created_at":at}

def acceptance_defects(db):
    ensure_ux_schema(db)
    return [dict(r) for r in db.execute("""SELECT id,area,severity,title,detail,status,actor_ref,created_at
      FROM buybox_acceptance_defects ORDER BY CASE status WHEN 'OPEN' THEN 0 ELSE 1 END,id DESC""").fetchall()]

def resolve_acceptance_defect(db,defect_id,*,actor_ref):
    ensure_ux_schema(db)
    actor=str(actor_ref or "").strip()
    if not actor: raise ValueError("DEFECT_ACTOR_REQUIRED")
    changed=db.execute("UPDATE buybox_acceptance_defects SET status='RESOLVED' WHERE id=? AND status='OPEN'",(int(defect_id),)).rowcount
    db.commit()
    if changed!=1: raise ValueError("DEFECT_NOT_OPEN")
    return True
