"""BBX087–091 — source-bound local closing review, never closing authority.

This room assembles current BuyBox records so the owner can see exactly what is
missing before a protected close request. It cannot verify title/ownership,
bind insurance, approve a loan, establish Teller capacity, issue Tower approval,
move money, sign documents, or update the protected lifecycle.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timezone
from hashlib import sha256
from uuid import uuid4
import json
import sqlite3

from .core import evaluate
from .diligence import diligence_snapshot
from .claim_register import integrity_report
from .financing import current_options, option_analysis
from .insurance import current_insurance_records, inspect_insurance_record
from .dealroom import current_tasks
from .store import encode
from .tower_action_draft import stored_source_snapshot, BuyBoxTowerActionPreparationError

KIND="OWNER_LOCAL_CLOSING_REVIEW"

class ClosingReviewError(ValueError): pass

def _text(value,code,limit):
    if not isinstance(value,str) or not value.strip() or len(value)>limit or "\x00" in value:
        raise ClosingReviewError(code)
    return value.strip()

def _day(value):
    if value in ("",None): return None
    if not isinstance(value,str): raise ClosingReviewError("PLANNED_CLOSING_DATE_INVALID")
    try:
        d=date.fromisoformat(value)
        if d.isoformat()!=value: raise ValueError
        return value
    except ValueError as exc:
        raise ClosingReviewError("PLANNED_CLOSING_DATE_INVALID") from exc

def _today(value=None):
    if value is None:return date.today()
    if isinstance(value,str):
        try:return date.fromisoformat(value)
        except ValueError as exc:raise ClosingReviewError("REVIEW_DATE_INVALID") from exc
    if not isinstance(value,date):raise ClosingReviewError("REVIEW_DATE_INVALID")
    return value

def closing_review_snapshot(op, *, today=None):
    day=_today(today)
    evaluation=evaluate(op)
    diligence=diligence_snapshot(op)
    integrity=integrity_report(op)
    financing=current_options(op)
    insurance=current_insurance_records(op)
    financing_rows=[{"record":q,"assessment":option_analysis(op,q,today=day)}
                    for q in financing]
    insurance_rows=[{"record":r,"assessment":inspect_insurance_record(op,r,today=day)}
                    for r in insurance]

    source_blockers=[]
    if diligence["critical_outstanding"]:
        source_blockers.append("CRITICAL_DILIGENCE_OUTSTANDING")
    if integrity["unresolved_count"]:
        source_blockers.append("UNRESOLVED_SOURCE_DISCREPANCIES")
    if not financing_rows:
        source_blockers.append("NO_DOCUMENTED_FINANCING_OPTION")
    elif not any(not x["assessment"]["review_flags"] for x in financing_rows):
        source_blockers.append("ALL_FINANCING_OPTIONS_REQUIRE_RECHECK")
    if not insurance_rows:
        source_blockers.append("NO_DOCUMENTED_INSURANCE_RECORD")
    elif not any(x["record"]["document_kind"] in ("BINDER","POLICY")
                 and not x["assessment"]["review_flags"] for x in insurance_rows):
        source_blockers.append("NO_CLEAN_BINDER_OR_POLICY_RECORD")
    open_tasks=[t for t in current_tasks(op) if t["status"] in ("OPEN","WAITING")]
    if open_tasks:
        source_blockers.append("OPEN_OWNER_TASKS_REMAIN")
    if evaluation["financials"]["status"]!="CALCULATED":
        source_blockers.append("DOCUMENT_LINKED_OPERATING_BASELINE_INCOMPLETE")

    external_blockers=[
        "TELLER_MONEY_READINESS_UNKNOWN",
        "TELLER_MANAGEMENT_CAPACITY_UNKNOWN",
        "TOWER_CLOSING_AUTHORIZATION_ABSENT",
        "LENDER_COMMITMENT_NOT_INDEPENDENTLY_VERIFIED",
        "INSURANCE_IN_FORCE_NOT_INDEPENDENTLY_VERIFIED",
        "TITLE_OWNERSHIP_LIEN_AND_TRANSFER_NOT_INDEPENDENTLY_VERIFIED",
        "SETTLEMENT_AND_CLOSING_AGENT_COMPLETION_NOT_VERIFIED",
    ]
    reviews=[]
    for review in reversed(deepcopy(op.get("closing_reviews",[]))):
        review["display_state"]=("CURRENT_RECORDED_REVIEW" if review.get("recorded_opportunity_revision")==op["version"] else "HISTORICAL_OPPORTUNITY_VERSION")
        reviews.append(review)
    return {
        "opportunity_id":op["id"],"opportunity_revision":op["version"],
        "vertical":op["vertical"],"lifecycle":op["lifecycle"],
        "local_source_state":("SOURCE_REVIEW_ASSEMBLED"
                              if not source_blockers else "SOURCE_GAPS_OR_RECHECKS"),
        "source_blockers":source_blockers,
        "external_blockers":external_blockers,
        "critical_diligence_outstanding":diligence["critical_outstanding"],
        "unresolved_source_discrepancies":integrity["unresolved_count"],
        "open_owner_tasks":len(open_tasks),
        "financial_status":evaluation["financials"]["status"],
        "financing_options":financing_rows,
        "insurance_records":insurance_rows,
        "historical_reviews":reviews,
        "teller_money_ready":"UNKNOWN","teller_management_ready":"UNKNOWN",
        "tower_closing_authorized":False,"title_transfer_verified":False,
        "bank_commitment_verified":False,"insurance_in_force":"UNKNOWN",
        "settlement_completed":False,"authorizes_closing":False,
        "authorizes_money":False,"updates_lifecycle":False,
    }

def record_local_closing_review(
    db: sqlite3.Connection, op, *, actor_ref, rationale,
    financing_option_id="", insurance_record_id="", planned_closing_date="",
    today=None,
):
    """Freeze what the owner reviewed locally; never prepare/submit Tower action."""
    actor=_text(actor_ref,"OWNER_ACTOR_REQUIRED",128)
    reason=_text(rationale,"CLOSING_REVIEW_REASON_REQUIRED",2000)
    planned=_day(planned_closing_date)
    if not isinstance(db,sqlite3.Connection):
        raise ClosingReviewError("PERSISTED_SOURCE_REQUIRED")
    try:source=stored_source_snapshot(db,op["id"])
    except (BuyBoxTowerActionPreparationError,sqlite3.DatabaseError) as exc:
        raise ClosingReviewError("CURRENT_PERSISTED_SOURCE_UNAVAILABLE") from exc
    calculated=sha256(encode(op).encode("utf-8")).hexdigest()
    if (source["opportunity_revision"]!=op["version"]
            or source["vertical_id"]!=op["vertical"]
            or source["input_snapshot_digest"]!=calculated):
        raise ClosingReviewError("CLOSING_REVIEW_SOURCE_CHANGED")

    finance=None
    if financing_option_id:
        finance=next((q for q in current_options(op) if q["id"]==financing_option_id),None)
        if finance is None:raise ClosingReviewError("CURRENT_FINANCING_OPTION_REQUIRED")
    insurance=None
    if insurance_record_id:
        insurance=next((r for r in current_insurance_records(op)
                        if r["id"]==insurance_record_id),None)
        if insurance is None:raise ClosingReviewError("CURRENT_INSURANCE_RECORD_REQUIRED")

    snapshot=closing_review_snapshot(op,today=today)
    body={
        "id":str(uuid4()),"record_kind":KIND,
        "source_opportunity_id":op["id"],
        "source_opportunity_revision":op["version"],
        "source_snapshot_digest":calculated,
        "recorded_opportunity_revision":op["version"]+1,
        "recorded_at":datetime.now(timezone.utc).isoformat(),
        "actor":actor,"rationale":reason,
        "planned_closing_date":planned,
        "selected_financing_option_id":finance["id"] if finance else None,
        "selected_financing_source_sha256":finance["source_sha256"] if finance else None,
        "selected_financing_review_flags":(
            option_analysis(op,finance,today=_today(today))["review_flags"] if finance else []),
        "selected_insurance_record_id":insurance["id"] if insurance else None,
        "selected_insurance_source_sha256":insurance["source_sha256"] if insurance else None,
        "selected_insurance_review_flags":(
            inspect_insurance_record(op,insurance,today=_today(today))["review_flags"]
            if insurance else []),
        "captured_local_source_state":snapshot["local_source_state"],
        "captured_source_blockers":snapshot["source_blockers"],
        "captured_external_blockers":snapshot["external_blockers"],
        "captured_critical_diligence_outstanding":snapshot["critical_diligence_outstanding"],
        "captured_unresolved_source_discrepancies":snapshot["unresolved_source_discrepancies"],
        "captured_open_owner_tasks":snapshot["open_owner_tasks"],
        "teller_money_ready":"UNKNOWN","teller_management_ready":"UNKNOWN",
        "tower_closing_authorization":None,
        "title_transfer_verified":False,"bank_commitment_verified":False,
        "insurance_in_force":"UNKNOWN","settlement_completed":False,
        "authorizes_closing":False,"authorizes_money":False,
        "transmitted_externally":False,"updates_lifecycle":False,
    }
    digest=sha256(json.dumps(body,sort_keys=True,separators=(",",":"),
                             ensure_ascii=False).encode()).hexdigest()
    record={**body,"local_snapshot_sha256":digest}
    revised=deepcopy(op)
    revised.setdefault("closing_reviews",[]).append(record)
    return revised,deepcopy(record)
