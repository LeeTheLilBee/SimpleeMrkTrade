"""BBX062-066: source-bound comparable observations across seven asset classes.

This is descriptive market research, NOT an appraisal, price recommendation,
independently verified sale, lender valuation, or purchase authorization.
Only owner-transcribed fields from a real uploaded original can enter a cohort.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from statistics import median
from uuid import uuid4
import re

COMPARABLE_EVIDENCE_KIND="comparable_original"
BASIS_BY_VERTICAL={
    "atm":{"PRICE_PER_INCLUDED_MACHINE":"USD_PER_MACHINE"},
    "multifamily":{"PRICE_PER_UNIT":"USD_PER_UNIT",
                   "PRICE_PER_SQUARE_FOOT":"USD_PER_SQUARE_FOOT"},
    "commercial":{"PRICE_PER_SQUARE_FOOT":"USD_PER_SQUARE_FOOT"},
    "laundromat":{"PRICE_PER_MACHINE":"USD_PER_MACHINE"},
    "land_farm":{"PRICE_PER_USABLE_ACRE":"USD_PER_USABLE_ACRE"},
    "business":{"PRICE_TO_DOCUMENTED_ANNUAL_EARNINGS":"OBSERVED_PRICE_TO_EARNINGS_RATIO"},
    "equipment":{"PRICE_PER_ASSET_UNIT":"USD_PER_ASSET_UNIT"},
}
SOURCE_KINDS=frozenset({"DOCUMENTED_LISTING_ASK","OWNER_RECORDED_REPORTED_SALE"})
AMOUNT=re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?\Z")
DENOMINATOR=re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{1,4})?\Z")
MAX_AMT=Decimal("1000000000000.00")
MAX_DENOM=Decimal("1000000000.0000")
CENTS=Decimal("0.01")

class ComparableError(ValueError): pass

def _text(value,code,limit):
    if not isinstance(value,str) or not value.strip() or len(value)>limit or "\x00" in value:
        raise ComparableError(code)
    return value.strip()

def _value(raw,kind,code):
    pattern=AMOUNT if kind=="MONEY" else DENOMINATOR
    if not isinstance(raw,str) or len(raw)>30 or not pattern.fullmatch(raw):
        raise ComparableError(code)
    v=Decimal(raw)
    if v<=0 or v>(MAX_AMT if kind=="MONEY" else MAX_DENOM):
        raise ComparableError(code)
    return v

def _date(raw):
    try:
        parsed=date.fromisoformat(raw)
        if parsed.isoformat()!=raw or parsed>date.today():raise ValueError
        return raw
    except (TypeError,ValueError):
        raise ComparableError("SOURCE_EVENT_DATE_INVALID_OR_FUTURE") from None

def _source(op,evidence_id):
    rows=[e for e in op.get("evidence",[]) if e.get("id")==evidence_id
          and e.get("kind")==COMPARABLE_EVIDENCE_KIND
          and e.get("status") in ("RECEIVED","DOCUMENT_SUPPORTED")
          and e.get("artifact_id")]
    if len(rows)!=1:
        raise ComparableError("ACTIVE_COMPARABLE_ORIGINAL_REQUIRED")
    e=rows[0]
    artifacts=[a for a in op.get("artifacts",[]) if a.get("id")==e["artifact_id"]
               and re.fullmatch(r"[a-f0-9]{64}",str(a.get("sha256","")))]
    if len(artifacts)!=1:
        raise ComparableError("ORIGINAL_DIGEST_UNAVAILABLE")
    return e,artifacts[0]

def current_comparables(op):
    records=op.get("comparable_observations",[])
    superseded={x.get("supersedes") for x in records if x.get("supersedes")}
    return deepcopy([x for x in records if x.get("id") not in superseded])

def record_comparable(op, *, evidence_id, subject_id, market, source_kind,
                      basis, price, denominator, event_date, locator, actor_ref,
                      supersedes=None, correction_reason=None):
    allowed=BASIS_BY_VERTICAL.get(op["vertical"],{})
    if basis not in allowed:raise ComparableError("UNSUPPORTED_BASIS_FOR_VERTICAL")
    if source_kind not in SOURCE_KINDS:raise ComparableError("INVALID_SOURCE_KIND")
    e,a=_source(op,evidence_id)
    subject=_text(subject_id,"COMPARABLE_SUBJECT_REQUIRED",128)
    market=_text(market,"MARKET_REQUIRED",120)
    locator=_text(locator,"SOURCE_LOCATOR_REQUIRED",240)
    actor=_text(actor_ref,"ACTOR_REQUIRED",128)
    day=_date(event_date)
    original_price=_value(price,"MONEY","SOURCE_PRICE_INVALID")
    denominator_value=_value(denominator,"DENOMINATOR","DENOMINATOR_INVALID")
    value=(original_price/denominator_value).quantize(CENTS,rounding=ROUND_HALF_UP)
    old=None
    if supersedes:
        old=next((x for x in current_comparables(op) if x["id"]==supersedes),None)
        if old is None:raise ComparableError("ACTIVE_COMPARABLE_CORRECTION_REQUIRED")
        if (old["subject_id"].casefold()!=subject.casefold() or
            old["market"].casefold()!=market.casefold() or
            old["source_kind"]!=source_kind or old["basis"]!=basis or
            old["event_date"]!=day):
            raise ComparableError("COMPARABLE_CORRECTION_SCOPE_MISMATCH")
        _text(correction_reason,"CORRECTION_REASON_REQUIRED",1000)
    elif correction_reason not in (None,""):
        raise ComparableError("CORRECTION_TARGET_REQUIRED")
    if old is None:
        for c in current_comparables(op):
            if (c["subject_id"].casefold()==subject.casefold() and
                c["market"].casefold()==market.casefold() and
                c["source_kind"]==source_kind and c["basis"]==basis and
                c["event_date"]==day):
                raise ComparableError("DUPLICATE_SUBJECT_EVENT_REVIEW_REQUIRED")
    record={
        "id":str(uuid4()),"source_evidence_id":e["id"],
        "source_artifact_id":a["id"],"source_sha256":a["sha256"],
        "source_locator":locator,"source_evidence_status_at_entry":e["status"],
        "subject_id":subject,"market":market,"market_match_method":"EXACT_OWNER_TEXT",
        "source_kind":source_kind,"event_date":day,
        "vertical":op["vertical"],"basis":basis,"basis_unit":allowed[basis],
        "documented_price":str(original_price.quantize(CENTS)),
        "documented_denominator":str(denominator_value),
        "normalized_observed_value":str(value),"currency":"USD",
        "recorded_by":actor,"recorded_at":datetime.now(timezone.utc).isoformat(),
        "record_type":"OWNER_TRANSCRIPTION_FROM_ORIGINAL",
        "independent_sale_verified":False,"independent_appraisal":False,
        "selected_property_valuation":False,"purchase_authorized":False,
        "supersedes":old["id"] if old else None,
        "correction_reason":correction_reason.strip() if old else None,
    }
    revised=deepcopy(op)
    revised.setdefault("comparable_observations",[]).append(record)
    from .workflow import invalidate_on_change
    revised=invalidate_on_change(revised,
        changed_fields=["comparable_observations"],
        reason="Owner recorded a source-bound comparable or correction",
        source_reference=a["id"])
    return revised,deepcopy(record)

def market_evidence_report(op):
    current=current_comparables(op)
    groups={}
    for c in current:
        key=(c["basis"],c["market"].casefold(),c["source_kind"])
        groups.setdefault(key,[]).append(c)
    cohorts=[]
    for (basis,_,kind),members in groups.items():
        distinct={c["subject_id"].casefold() for c in members}
        documented=[Decimal(c["normalized_observed_value"]) for c in members]
        complete=len(distinct)>=2
        cohorts.append({
            "basis":basis,"unit":members[0]["basis_unit"],
            "market":members[0]["market"],"source_kind":kind,
            "count":len(members),"distinct_subject_count":len(distinct),
            "status":"DESCRIPTIVE_COHORT_ONLY" if complete else "INSUFFICIENT_DISTINCT_SUBJECTS",
            "observed_min":str(min(documented)) if complete else None,
            "observed_median":str(median(documented).quantize(CENTS,rounding=ROUND_HALF_UP)) if complete else None,
            "observed_max":str(max(documented)) if complete else None,
            "earliest_event_date":min(c["event_date"] for c in members),
            "latest_event_date":max(c["event_date"] for c in members),
            "observation_ids":[c["id"] for c in members],
            "source_artifact_ids":[c["source_artifact_id"] for c in members],
            "independently_verified":False,"appraised_value":None,
            "recommended_purchase_price":None,
            "asking_and_reported_sales_separated":True,
        })
    cohorts.sort(key=lambda c:(c["basis"],c["market"].casefold(),c["source_kind"]))
    return {
        "opportunity_id":op["id"],"vertical":op["vertical"],
        "active_observations":current,"active_count":len(current),
        "cohorts":cohorts,"cohort_count":len(cohorts),
        "no_comparables_fabricated":True,
        "target_value_calculated":False,"external_data_retrieved":False,
        "tower_approval":False,"teller_readiness":"UNKNOWN",
    }
