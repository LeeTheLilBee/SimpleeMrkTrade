"""BBX092–096 — private owner Offer Lab; never sends or signs an offer.

Offer scenarios are analytical owner records bound to the exact saved BuyBox
source revision. They are not LOIs, seller communications, Tower approvals,
Teller readiness, broker/lender instructions, or legally binding instruments.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from uuid import uuid4
import json
import re
import sqlite3

from .store import encode
from .tower_action_draft import stored_source_snapshot, BuyBoxTowerActionPreparationError
from .financing import current_options, option_analysis
from .insurance import current_insurance_records, inspect_insurance_record

MONEY=re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?\Z")
MAX_USD=Decimal("1000000000000.00")
KIND="OWNER_INTERNAL_OFFER_SCENARIO"

class OfferLabError(ValueError): pass

def _text(value,code,limit,required=True):
    if not isinstance(value,str) or len(value)>limit or "\x00" in value or (required and not value.strip()):
        raise OfferLabError(code)
    return value.strip()

def _money(value,code,positive=False):
    if not isinstance(value,str) or not MONEY.fullmatch(value) or len(value)>30:
        raise OfferLabError(code)
    amount=Decimal(value)
    if amount>MAX_USD or (amount<=0 if positive else amount<0):
        raise OfferLabError(code)
    return amount.quantize(Decimal("0.01"))

def _day(value,code,required=False):
    if value in ("",None):
        if required:raise OfferLabError(code)
        return None
    if not isinstance(value,str):raise OfferLabError(code)
    try:
        parsed=date.fromisoformat(value)
        if parsed.isoformat()!=value:raise ValueError
        return parsed
    except ValueError as exc:
        raise OfferLabError(code) from exc

def _bool(value,code):
    if type(value) is not bool:raise OfferLabError(code)
    return value

def _today(value=None):
    if value is None:return date.today()
    if isinstance(value,str):return _day(value,"REVIEW_DATE_INVALID",required=True)
    if not isinstance(value,date):raise OfferLabError("REVIEW_DATE_INVALID")
    return value

def current_offer_scenarios(op):
    all_rows=op.get("offer_scenarios",[])
    superseded={x.get("supersedes") for x in all_rows if x.get("supersedes")}
    return deepcopy([x for x in all_rows if x.get("id") not in superseded])

def _source(db,op):
    if not isinstance(db,sqlite3.Connection):
        raise OfferLabError("PERSISTED_SOURCE_REQUIRED")
    try:stored=stored_source_snapshot(db,op["id"])
    except (BuyBoxTowerActionPreparationError,sqlite3.DatabaseError) as exc:
        raise OfferLabError("CURRENT_PERSISTED_SOURCE_UNAVAILABLE") from exc
    digest=sha256(encode(op).encode("utf-8")).hexdigest()
    if (stored["opportunity_revision"]!=op.get("version")
            or stored["vertical_id"]!=op.get("vertical")
            or stored["input_snapshot_digest"]!=digest):
        raise OfferLabError("OFFER_SCENARIO_SOURCE_CHANGED")
    return stored,digest

def record_offer_scenario(
    db,op,*,name,proposed_purchase_price,earnest_money,requested_seller_credit,
    due_diligence_days,financing_contingency,planned_closing_date,
    financing_option_id="",insurance_record_id="",rationale="",terms_note="",
    actor_ref, supersedes="", correction_reason="", today=None,
):
    """Record a private scenario without affecting actual seller/deal truth."""
    _,digest=_source(db,op)
    actor=_text(actor_ref,"OWNER_ACTOR_REQUIRED",128)
    label=_text(name,"SCENARIO_NAME_REQUIRED",120)
    reason=_text(rationale,"SCENARIO_RATIONALE_REQUIRED",2000)
    note=_text(terms_note,"TERMS_NOTE_INVALID",2000,required=False)
    price=_money(proposed_purchase_price,"PROPOSED_PRICE_INVALID",positive=True)
    earnest=_money(earnest_money,"EARNEST_MONEY_INVALID")
    credit=_money(requested_seller_credit,"SELLER_CREDIT_INVALID")
    if credit>price:raise OfferLabError("SELLER_CREDIT_EXCEEDS_PROPOSED_PRICE")
    if earnest>price:raise OfferLabError("EARNEST_MONEY_EXCEEDS_PROPOSED_PRICE")
    if not isinstance(due_diligence_days,str) or not re.fullmatch(r"(?:0|[1-9][0-9]*)",due_diligence_days):
        raise OfferLabError("DUE_DILIGENCE_DAYS_INVALID")
    dd=int(due_diligence_days)
    if dd>365:raise OfferLabError("DUE_DILIGENCE_DAYS_OUT_OF_RANGE")
    contingency=_bool(financing_contingency,"FINANCING_CONTINGENCY_REQUIRED")
    closing=_day(planned_closing_date,"PLANNED_CLOSING_DATE_REQUIRED",required=True)
    if closing<_today(today):raise OfferLabError("PLANNED_CLOSING_DATE_IN_PAST")

    financing=None
    if financing_option_id:
        financing=next((x for x in current_options(op) if x["id"]==financing_option_id),None)
        if financing is None:raise OfferLabError("CURRENT_FINANCING_OPTION_REQUIRED")
    insurance=None
    if insurance_record_id:
        insurance=next((x for x in current_insurance_records(op) if x["id"]==insurance_record_id),None)
        if insurance is None:raise OfferLabError("CURRENT_INSURANCE_RECORD_REQUIRED")

    prior=None
    if supersedes:
        prior=next((x for x in current_offer_scenarios(op) if x["id"]==supersedes),None)
        if prior is None:raise OfferLabError("CURRENT_SCENARIO_CORRECTION_TARGET_REQUIRED")
        _text(correction_reason,"CORRECTION_REASON_REQUIRED",1000)
    elif correction_reason not in ("",None):
        raise OfferLabError("CORRECTION_TARGET_REQUIRED")

    record={
        "id":str(uuid4()),"record_kind":KIND,"name":label,
        "proposed_purchase_price":str(price),"earnest_money":str(earnest),
        "requested_seller_credit":str(credit),"due_diligence_days":dd,
        "financing_contingency":contingency,
        "planned_closing_date":closing.isoformat(),
        "financing_option_id":financing["id"] if financing else None,
        "financing_source_sha256":financing["source_sha256"] if financing else None,
        "insurance_record_id":insurance["id"] if insurance else None,
        "insurance_source_sha256":insurance["source_sha256"] if insurance else None,
        "rationale":reason,"terms_note":note,"actor":actor,
        "source_opportunity_id":op["id"],
        "source_opportunity_revision":op["version"],
        "source_snapshot_digest":digest,
        "asking_price_basis":op.get("asking_price"),
        "recorded_at":datetime.now(timezone.utc).isoformat(),
        "supersedes":prior["id"] if prior else None,
        "correction_reason":correction_reason.strip() if prior else None,
        "transmitted_to_seller":False,"is_loi":False,"is_contract":False,
        "tower_authorization":None,"teller_readiness":"UNKNOWN",
        "authorizes_offer":False,"authorizes_purchase":False,
        "authorizes_money":False,"updates_lifecycle":False,
    }
    record["local_record_sha256"]=sha256(json.dumps(
        record,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    revised=deepcopy(op)
    revised.setdefault("offer_scenarios",[]).append(record)
    return revised,deepcopy(record)

def analyze_offer_scenario(op,scenario,*,today=None):
    day=_today(today)
    reasons=[]
    if scenario.get("asking_price_basis")!=op.get("asking_price"):
        reasons.append("CURRENT_ASKING_PRICE_CHANGED")
    if scenario.get("source_opportunity_revision")!=op.get("version"):
        reasons.append("SCENARIO_SOURCE_REVISION_IS_HISTORICAL")
    asking=Decimal(op["asking_price"]) if op.get("asking_price") is not None else None
    proposed=Decimal(scenario["proposed_purchase_price"])
    delta=None
    pct=None
    if asking is not None:
        delta=(proposed-asking).quantize(Decimal("0.01"))
        if asking!=0:
            pct=((delta/asking)*100).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)

    finance=None
    if scenario.get("financing_option_id"):
        selected=next((x for x in current_options(op)
                       if x["id"]==scenario["financing_option_id"]),None)
        if selected is None:
            reasons.append("SELECTED_FINANCING_OPTION_NOT_CURRENT")
        else:
            finance=option_analysis(op,selected,today=day)
            if selected["source_sha256"]!=scenario.get("financing_source_sha256"):
                reasons.append("SELECTED_FINANCING_SOURCE_CHANGED")
            reasons.extend("FINANCING_"+x for x in finance["review_flags"])
            if Decimal(selected["purchase_price"])!=proposed:
                reasons.append("FINANCING_PRICE_BASIS_DIFFERS_FROM_PROPOSED_OFFER")

    insurance=None
    if scenario.get("insurance_record_id"):
        selected=next((x for x in current_insurance_records(op)
                       if x["id"]==scenario["insurance_record_id"]),None)
        if selected is None:
            reasons.append("SELECTED_INSURANCE_RECORD_NOT_CURRENT")
        else:
            insurance=inspect_insurance_record(op,selected,today=day)
            if selected["source_sha256"]!=scenario.get("insurance_source_sha256"):
                reasons.append("SELECTED_INSURANCE_SOURCE_CHANGED")
            reasons.extend("INSURANCE_"+x for x in insurance["review_flags"])
            start=selected.get("effective_date"); end=selected.get("expiration_date")
            close=scenario["planned_closing_date"]
            if start is None or end is None:
                reasons.append("INSURANCE_COVERAGE_DATES_UNKNOWN_FOR_PROPOSED_CLOSE")
            elif not(start<=close<end):
                reasons.append("INSURANCE_DATES_DO_NOT_COVER_PROPOSED_CLOSE")
            expiry=selected.get("quote_valid_until")
            if expiry and expiry<close:
                reasons.append("INSURANCE_QUOTE_EXPIRES_BEFORE_PROPOSED_CLOSE")

    return {
        "scenario_id":scenario["id"],"status":("RECHECK_INPUTS" if reasons else "PRIVATE_SCENARIO_CURRENT"),
        "review_flags":list(dict.fromkeys(reasons)),
        "current_asking_price":str(asking) if asking is not None else None,
        "proposed_purchase_price":str(proposed),
        "price_delta_from_current_asking":str(delta) if delta is not None else None,
        "price_delta_percent":str(pct) if pct is not None else None,
        "net_price_before_other_costs":str((proposed-Decimal(scenario["requested_seller_credit"])).quantize(Decimal("0.01"))),
        "earnest_money":scenario["earnest_money"],
        "financing_analysis":finance,"insurance_analysis":insurance,
        "transmitted_to_seller":False,"loi_created":False,
        "tower_authorized":False,"teller_readiness":"UNKNOWN",
        "authorizes_offer":False,"authorizes_purchase":False,
        "recommended_option":False,
    }

def offer_lab_snapshot(op,*,today=None):
    current=current_offer_scenarios(op)
    current_ids={x["id"] for x in current}
    rows=[]
    for raw in reversed(op.get("offer_scenarios",[])):
        row=deepcopy(raw)
        row["display_state"]=(
            "CURRENT_PRIVATE_SCENARIO" if row["id"] in current_ids
            else "SUPERSEDED_PRIVATE_SCENARIO")
        row["analysis"]=analyze_offer_scenario(op,row,today=today)
        rows.append(row)
    return {
        "opportunity_id":op["id"],"opportunity_revision":op["version"],
        "current_scenario_count":len(current),
        "scenarios":rows,
        "asking_price":op.get("asking_price"),
        "seller_contact_sent":False,"loi_created":False,
        "tower_authorized":False,"teller_readiness":"UNKNOWN",
        "recommended_scenario_id":None,"authorizes_offer":False,
        "authorizes_purchase":False,"authorizes_money":False,
    }
