"""BBX067–071 — actual saved-source owner analytical Decision Desk.

A non-authorizing owner research disposition. A local decision record is NOT
Tower step-up, LOI, contract, capital movement, seller communication, lender
confirmation or closing authorization. Persist through normal revisioned store.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4
import json
import sqlite3

from .core import evaluate
from .store import encode
from .tower_action_draft import stored_source_snapshot, BuyBoxTowerActionPreparationError
from .diligence import diligence_snapshot
from .dealroom import current_tasks
from .financing import current_options
from .comparables import current_comparables

CHOICES=frozenset({"WATCH", "DEFER", "REQUEST_EVIDENCE", "DECLINE"})
KIND="OWNER_RESEARCH_DISPOSITION"

class DecisionDeskError(ValueError): pass

def _text(value,code,limit):
    if not isinstance(value,str) or not value.strip() or len(value)>limit or "\x00" in value:
        raise DecisionDeskError(code)
    return value.strip()

def decision_dossier(op):
    ev=evaluate(op)
    diligence=diligence_snapshot(op)
    notes=op.get("research_decisions",[])
    decisions=[]
    for d in reversed(notes):
        entry=deepcopy(d)
        entry["display_state"]=(
            "LATEST_RECORDED_ANALYTICAL_NOTE"
            if op["version"]==d["recorded_opportunity_revision"]
            else "HISTORICAL_OPPORTUNITY_VERSION"
        )
        decisions.append(entry)
    return {
        "opportunity_id":op["id"],"opportunity_revision":op["version"],
        "judgment":ev["judgment"],"rule_findings":deepcopy(ev["findings"]),
        "missing_critical_kinds":list(ev["evidence"]["missing_critical"]),
        "unresolved_source_discrepancies":ev["deal_integrity"]["unresolved_count"],
        "financial_status":ev["financials"]["status"],
        "actual_recorded_financing_options":len(current_options(op)),
        "actual_recorded_comparables":len(current_comparables(op)),
        "critical_diligence_outstanding":diligence["critical_outstanding"],
        "actual_open_tasks":sum(t["status"] in ("OPEN","WAITING") for t in current_tasks(op)),
        "historical_notes":decisions,
        "teller_money_ready":"UNKNOWN","teller_management_ready":"UNKNOWN",
        "tower_protected_action_authorized":False,
        "acquisition_authorized":False,"seller_contact_sent":False,
    }

def record_owner_research_disposition(db, op, *, choice, rationale, actor_ref,
                                      cited_evidence_ids=()):
    if choice not in CHOICES:raise DecisionDeskError("UNAUTHORIZED_OR_UNKNOWN_DISPOSITION")
    rationale=_text(rationale,"OWNER_REASON_REQUIRED",2000)
    actor=_text(actor_ref,"OWNER_ACTOR_REQUIRED",128)
    if isinstance(cited_evidence_ids,(str,bytes)) or not isinstance(cited_evidence_ids,(list,tuple)):
        raise DecisionDeskError("EVIDENCE_IDS_INVALID")
    selected=[]
    valid={e["id"] for e in op.get("evidence",[]) if isinstance(e,dict) and e.get("id")}
    for ref in cited_evidence_ids:
        if not isinstance(ref,str) or ref not in valid:
            raise DecisionDeskError("EVIDENCE_REFERENCE_NOT_IN_OPPORTUNITY")
        if ref not in selected:selected.append(ref)
    if len(selected)>20:raise DecisionDeskError("TOO_MANY_EVIDENCE_REFERENCES")
    if not isinstance(db,sqlite3.Connection):
        raise DecisionDeskError("PERSISTED_SOURCE_REQUIRED")
    try:source=stored_source_snapshot(db,op["id"])
    except (BuyBoxTowerActionPreparationError, sqlite3.DatabaseError) as exc:
        raise DecisionDeskError("CURRENT_PERSISTED_SOURCE_UNAVAILABLE") from exc
    calculated=sha256(encode(op).encode("utf-8")).hexdigest()
    if (source["opportunity_revision"]!=op["version"]
            or source["vertical_id"]!=op["vertical"]
            or source["input_snapshot_digest"]!=calculated):
        raise DecisionDeskError("OWNER_NOTE_SOURCE_SNAPSHOT_CHANGED")
    assessment=decision_dossier(op)
    body={
        "id":str(uuid4()),"record_kind":KIND,"choice":choice,
        "rationale":rationale,"actor":actor,
        "source_opportunity_id":op["id"],
        "source_opportunity_revision":op["version"],
        "source_snapshot_digest":calculated,
        "recorded_opportunity_revision":op["version"]+1,
        "recorded_at":datetime.now(timezone.utc).isoformat(),
        "cited_evidence_ids":selected,
        "captured_analytical_judgment":assessment["judgment"],
        "captured_rule_ids":[x["rule_id"] for x in assessment["rule_findings"]],
        "captured_critical_outstanding":assessment["critical_diligence_outstanding"],
        "captured_unresolved_discrepancies":assessment["unresolved_source_discrepancies"],
        "captured_financial_status":assessment["financial_status"],
        "captured_option_count":assessment["actual_recorded_financing_options"],
        "captured_comparable_count":assessment["actual_recorded_comparables"],
        "teller_money_ready":"UNKNOWN","teller_management_ready":"UNKNOWN",
        "tower_authorization":None,"authorizes_purchase":False,
        "authorizes_offer_or_loi":False,"authorizes_closing":False,
        "transmitted_externally":False,"updates_lifecycle":False,
    }
    digest=sha256(json.dumps(body,sort_keys=True,separators=(",",":"),
                            ensure_ascii=False).encode("utf-8")).hexdigest()
    record={**body,"local_snapshot_sha256":digest}
    revised=deepcopy(op)
    revised.setdefault("research_decisions",[]).append(record)
    return revised,deepcopy(record)
