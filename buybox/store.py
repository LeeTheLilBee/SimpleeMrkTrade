"""Revisioned, transactionally stored opportunities."""
import hashlib
import json
import sqlite3
from copy import deepcopy
from .core import now

SCHEMA = """
CREATE TABLE IF NOT EXISTS opportunities (
 id TEXT PRIMARY KEY, vertical TEXT NOT NULL, name TEXT NOT NULL,
 revision INTEGER NOT NULL, current_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS revisions (
 opportunity_id TEXT NOT NULL, revision INTEGER NOT NULL, snapshot_json TEXT NOT NULL,
 digest TEXT NOT NULL, occurred_at TEXT NOT NULL,
 PRIMARY KEY(opportunity_id,revision)
);
CREATE TABLE IF NOT EXISTS events (
 event_id INTEGER PRIMARY KEY AUTOINCREMENT, opportunity_id TEXT NOT NULL,
 revision INTEGER NOT NULL, event_type TEXT NOT NULL,
 occurred_at TEXT NOT NULL, details_json TEXT NOT NULL
);
"""

def connect(path=":memory:"):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db

def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def save(db, opportunity, event_type="OpportunityUpdated", details=None, expected_revision=None):
    op = deepcopy(opportunity)
    with db:
        row = db.execute("SELECT revision FROM opportunities WHERE id=?", (op["id"],)).fetchone()
        previous = row["revision"] if row else 0
        if expected_revision is not None and previous != expected_revision:
            raise ValueError("REVISION_CONFLICT")
        revision = previous + 1
        op["version"] = revision
        op["updated_at"] = now()
        snapshot = encode(op)
        if previous:
            changed = db.execute(
                "UPDATE opportunities SET vertical=?,name=?,revision=?,current_json=? WHERE id=? AND revision=?",
                (op["vertical"], op["name"], revision, snapshot, op["id"], previous)
            ).rowcount
            if changed != 1:
                raise ValueError("REVISION_CONFLICT")
        else:
            db.execute("INSERT INTO opportunities VALUES (?,?,?,?,?)",
                       (op["id"], op["vertical"], op["name"], revision, snapshot))
        db.execute("INSERT INTO revisions VALUES (?,?,?,?,?)",
                   (op["id"], revision, snapshot,
                    hashlib.sha256(snapshot.encode("utf-8")).hexdigest(), op["updated_at"]))
        db.execute("INSERT INTO events (opportunity_id,revision,event_type,occurred_at,details_json) VALUES (?,?,?,?,?)",
                   (op["id"], revision, event_type, op["updated_at"], encode(details or {})))
    return op

def load(db, opportunity_id):
    row = db.execute("SELECT current_json FROM opportunities WHERE id=?", (opportunity_id,)).fetchone()
    return json.loads(row["current_json"]) if row else None

def list_opportunities(db, vertical=None):
    if vertical:
        rows = db.execute("SELECT current_json FROM opportunities WHERE vertical=? ORDER BY name", (vertical,))
    else:
        rows = db.execute("SELECT current_json FROM opportunities ORDER BY name")
    return [json.loads(row["current_json"]) for row in rows.fetchall()]

def history(db, opportunity_id):
    rows = db.execute("SELECT revision,digest,occurred_at FROM revisions WHERE opportunity_id=? ORDER BY revision",
                      (opportunity_id,)).fetchall()
    return [dict(row) for row in rows]

def activity(db, opportunity_id):
    rows = db.execute("SELECT revision,event_type,occurred_at,details_json FROM events WHERE opportunity_id=? ORDER BY event_id",
                      (opportunity_id,)).fetchall()
    return [{"revision": r["revision"], "event_type": r["event_type"], "occurred_at": r["occurred_at"],
             "details": json.loads(r["details_json"])} for r in rows]
