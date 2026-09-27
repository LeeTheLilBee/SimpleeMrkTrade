"""BBX042-046 — persistent saved discovery filters and owner-run Opportunity Radar.

Only actually stored BuyBox opportunity revisions are read. A check observes
local source changes; it neither polls an external marketplace nor sends an
automatic notification. Baseline results are NOT called newly discovered deals.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from copy import deepcopy
import json
import re
import sqlite3
from uuid import uuid4

from .discovery import filter_opportunities
from .registry import VERTICALS
from .store import list_opportunities
from .tower_action_draft import stored_source_snapshot, BuyBoxTowerActionPreparationError

SCHEMA_VERSION="buybox.saved_search.v1"
AMOUNT=re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?\Z")
LIMIT=Decimal("1000000000000.00")


class SavedSearchError(ValueError):
    """No remote feed or privileged account detail is disclosed in errors."""


SCHEMA = """
CREATE TABLE IF NOT EXISTS buybox_saved_searches(
 id TEXT PRIMARY KEY,
 name TEXT NOT NULL,
 filters_json TEXT NOT NULL,
 created_at TEXT NOT NULL,
 created_by TEXT NOT NULL,
 archived_at TEXT
);
CREATE TABLE IF NOT EXISTS buybox_saved_search_checks(
 seq INTEGER PRIMARY KEY AUTOINCREMENT,
 check_id TEXT NOT NULL UNIQUE,
 search_id TEXT NOT NULL,
 checked_at TEXT NOT NULL,
 current_snapshot_json TEXT NOT NULL,
 result_json TEXT NOT NULL,
 FOREIGN KEY(search_id) REFERENCES buybox_saved_searches(id)
);
CREATE INDEX IF NOT EXISTS idx_buybox_saved_search_checks
 ON buybox_saved_search_checks(search_id,seq);
"""


def _encode(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),
                      ensure_ascii=False,allow_nan=False)


def _instant():
    return datetime.now(timezone.utc).isoformat()


def _schema(db):
    if not isinstance(db,sqlite3.Connection):
        raise SavedSearchError("PERSISTENT_BUYBOX_STORE_REQUIRED")
    # executescript() would COMMIT an in-flight BEGIN IMMEDIATE, defeating
    # concurrent check serialization. Execute each idempotent DDL statement
    # separately so read/compare/insert stays within one SQLite transaction.
    for statement in SCHEMA.split(";"):
        if statement.strip():
            db.execute(statement)


def normalize_filters(*, vertical=None, query="", max_price=None):
    vertical=vertical or None
    if vertical is not None and vertical not in VERTICALS:
        raise SavedSearchError("UNKNOWN_VERTICAL")
    if not isinstance(query,str) or len(query)>120 or "\x00" in query:
        raise SavedSearchError("INVALID_SEARCH_QUERY")
    query=" ".join(query.strip().split())
    if max_price in (None,""):
        amount=None
    else:
        if not isinstance(max_price,str) or len(max_price)>30 or not AMOUNT.fullmatch(max_price):
            raise SavedSearchError("INVALID_MAX_PRICE")
        figure=Decimal(max_price)
        if not figure.is_finite() or figure>LIMIT:
            raise SavedSearchError("MAX_PRICE_OUT_OF_RANGE")
        amount=str(figure.quantize(Decimal("0.01")))
    return {"vertical":vertical,"query":query,"max_price":amount}


def create_saved_search(db, *, name, filters, actor_reference="local_owner"):
    _schema(db)
    if (not isinstance(name,str) or not name.strip()
            or len(name)>100 or "\x00" in name):
        raise SavedSearchError("SEARCH_NAME_REQUIRED")
    if not isinstance(actor_reference,str) or not actor_reference.strip():
        raise SavedSearchError("ACTOR_REQUIRED")
    if not isinstance(filters,dict) or set(filters)!={"vertical","query","max_price"}:
        raise SavedSearchError("EXACT_FILTERS_REQUIRED")
    criteria=normalize_filters(**filters)
    record={
        "id":str(uuid4()),"name":name.strip(),
        "filters":criteria,"created_at":_instant(),
        "created_by":actor_reference,"archived_at":None,
    }
    with db:
        db.execute("INSERT INTO buybox_saved_searches VALUES (?,?,?,?,?,?)",
                   (record["id"],record["name"],_encode(criteria),
                    record["created_at"],record["created_by"],None))
    return deepcopy(record)


def _record(row):
    return {"id":row["id"],"name":row["name"],
            "filters":json.loads(row["filters_json"]),
            "created_at":row["created_at"],"created_by":row["created_by"],
            "archived_at":row["archived_at"]}


def saved_searches(db):
    _schema(db)
    rows=db.execute("""SELECT * FROM buybox_saved_searches
        ORDER BY (archived_at IS NOT NULL), created_at DESC,id""").fetchall()
    return [_record(row) for row in rows]


def get_saved_search(db, search_id):
    _schema(db)
    if not isinstance(search_id,str) or len(search_id)>128:
        raise SavedSearchError("INVALID_SEARCH_ID")
    row=db.execute("SELECT * FROM buybox_saved_searches WHERE id=?",
                   (search_id,)).fetchone()
    return _record(row) if row else None


def latest_check(db, search_id):
    _schema(db)
    row=db.execute("""SELECT * FROM buybox_saved_search_checks
        WHERE search_id=? ORDER BY seq DESC LIMIT 1""",(search_id,)).fetchone()
    if row is None:
        return None
    return {"check_id":row["check_id"],"search_id":row["search_id"],
            "checked_at":row["checked_at"],
            "current_snapshot":json.loads(row["current_snapshot_json"]),
            "result":json.loads(row["result_json"])}


def run_saved_search(db, search_id):
    """User-triggered, transactionally compare current saved-revision digests."""
    _schema(db)
    # Atomic select-compare-insert prevents two parallel checks from reporting
    # a new local change twice. No real-money or external action is involved.
    with db:
        db.execute("BEGIN IMMEDIATE")
        saved=get_saved_search(db,search_id)
        if saved is None:
            raise SavedSearchError("SAVED_SEARCH_NOT_FOUND")
        if saved["archived_at"] is not None:
            raise SavedSearchError("SAVED_SEARCH_ARCHIVED")
        previous=latest_check(db,search_id)
        actual=list_opportunities(db)
        filters=saved["filters"]
        matches=filter_opportunities(actual,
                    vertical=filters["vertical"],query=filters["query"],
                    max_price=filters["max_price"])
        now_ids={op["id"] for op in matches}
        source={}
        try:
            for op in matches:
                checkpoint=stored_source_snapshot(db,op["id"])
                source[op["id"]]={
                    "revision":checkpoint["opportunity_revision"],
                    "digest":checkpoint["input_snapshot_digest"],
                }
        except BuyBoxTowerActionPreparationError as exc:
            raise SavedSearchError("CURRENT_OPPORTUNITY_SOURCE_NOT_VERIFIED") from exc
        if previous is None:
            delta={"first_baseline":True,"newly_matching":[],
                   "revised":[], "no_longer_matching":[]}
        else:
            before=previous["current_snapshot"]
            new=sorted(now_ids-set(before))
            revised=sorted(
                ({"id":oid,
                  "previous_revision":before[oid]["revision"],
                  "current_revision":source[oid]["revision"]}
                 for oid in now_ids & set(before)
                 if before[oid]["digest"]!=source[oid]["digest"]),
                key=lambda x:x["id"])
            removed=sorted(set(before)-now_ids)
            delta={"first_baseline":False,"newly_matching":new,
                   "revised":revised,"no_longer_matching":removed}
        result={
            "schema_version":SCHEMA_VERSION,"search_id":saved["id"],
            "search_name":saved["name"],"filters":deepcopy(filters),
            "match_ids":sorted(now_ids),"match_count":len(now_ids),
            "delta":delta,
            "source":"PERSISTED_BUYBOX_OPPORTUNITY_REVISIONS",
            "external_listing_feed_connected":False,
            "automated_notification_sent":False,
            "claims_new_marketplace_listings":False,
            "requires_owner_requested_check":True,
            "authorizes_acquisition":False,
        }
        record={"check_id":str(uuid4()),"search_id":search_id,
                "checked_at":_instant(),
                "current_snapshot":source,"result":result}
        db.execute("""INSERT INTO buybox_saved_search_checks
            (check_id,search_id,checked_at,current_snapshot_json,result_json)
            VALUES (?,?,?,?,?)""",
            (record["check_id"],search_id,record["checked_at"],
             _encode(source),_encode(result)))
    return deepcopy(record)


def archive_saved_search(db, search_id, *, actor_reference="local_owner"):
    _schema(db)
    if not actor_reference:
        raise SavedSearchError("ACTOR_REQUIRED")
    with db:
        changed=db.execute("""UPDATE buybox_saved_searches
            SET archived_at=? WHERE id=? AND archived_at IS NULL""",
            (_instant(),search_id)).rowcount
    if changed!=1:
        raise SavedSearchError("SEARCH_NOT_FOUND_OR_ALREADY_ARCHIVED")
    return {"search_id":search_id,"archived":True,"external_request_made":False}
