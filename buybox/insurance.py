"""BBX077–081: original-backed, owner-recorded acquisition insurance desk.

A quote, certificate, binder, or policy-shaped uploaded document is not evidence
of live coverage merely because its name or an owner transcription says so.
No insurer lookup, binding, underwriting, lender compliance, Tower permission,
or Teller readiness is performed here. Figures are source-linked/owner-entered.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import date
from decimal import Decimal
from uuid import uuid4
import re

INSURANCE_EVIDENCE_KIND="insurance_document"
SOURCE_KINDS=frozenset({"insurance_document","insurance_quote"})
DOCUMENT_KINDS=frozenset({"QUOTE","BINDER","POLICY","CERTIFICATE"})
COVERAGE_CODES={
    "PROPERTY","GENERAL_LIABILITY","BUSINESS_INTERRUPTION","EQUIPMENT_BREAKDOWN",
    "CRIME_CASH","CYBER","AUTO","WORKERS_COMPENSATION","FLOOD",
    "WINDSTORM","ENVIRONMENTAL","UMBRELLA","OTHER",
}
# Review prompts, NOT declarations of legal, lender or underwriting requirements.
VERTICAL_PROMPTS={
    "atm":("GENERAL_LIABILITY","CRIME_CASH","EQUIPMENT_BREAKDOWN","CYBER"),
    "multifamily":("PROPERTY","GENERAL_LIABILITY","BUSINESS_INTERRUPTION","FLOOD"),
    "commercial":("PROPERTY","GENERAL_LIABILITY","BUSINESS_INTERRUPTION","WINDSTORM"),
    "laundromat":("PROPERTY","GENERAL_LIABILITY","EQUIPMENT_BREAKDOWN","BUSINESS_INTERRUPTION"),
    "land_farm":("PROPERTY","GENERAL_LIABILITY","ENVIRONMENTAL","FLOOD"),
    "business":("GENERAL_LIABILITY","BUSINESS_INTERRUPTION","CYBER","WORKERS_COMPENSATION"),
    "equipment":("PROPERTY","EQUIPMENT_BREAKDOWN","GENERAL_LIABILITY"),
}
MONEY=re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?\Z")
MAX_USD=Decimal("1000000000000.00")

class InsuranceError(ValueError):
    pass

def _text(value,code,limit=240,required=True):
    if not isinstance(value,str) or len(value)>limit or "\x00" in value or (required and not value.strip()):
        raise InsuranceError(code)
    return value.strip()

def _amount(value,code,positive=False):
    if not isinstance(value,str) or len(value)>30 or MONEY.fullmatch(value) is None:
        raise InsuranceError(code)
    number=Decimal(value)
    if number>MAX_USD or (number<=0 if positive else number<0):
        raise InsuranceError(code)
    return str(number.quantize(Decimal("0.01")))

def _day(value,code,required=False):
    if value is None or value=="":
        if required:raise InsuranceError(code)
        return None
    if not isinstance(value,str):raise InsuranceError(code)
    try:
        parsed=date.fromisoformat(value)
        if parsed.isoformat()!=value:raise ValueError
        return value
    except ValueError as exc:
        raise InsuranceError(code) from exc

def _yes_no(value,code):
    if value not in (True,False) or type(value) is not bool:
        raise InsuranceError(code)
    return value

def _source(op,evidence_id):
    candidates=[e for e in op.get("evidence",[]) if
                e.get("id")==evidence_id and e.get("kind") in SOURCE_KINDS
                and e.get("status") in ("RECEIVED","DOCUMENT_SUPPORTED")]
    if len(candidates)!=1 or not candidates[0].get("artifact_id"):
        raise InsuranceError("ACTIVE_INSURANCE_ORIGINAL_REQUIRED")
    e=candidates[0]
    artifacts=[a for a in op.get("artifacts",[]) if
               a.get("id")==e["artifact_id"] and
               isinstance(a.get("sha256"),str) and
               re.fullmatch(r"[a-f0-9]{64}",a["sha256"])]
    if len(artifacts)!=1:raise InsuranceError("ORIGINAL_DIGEST_UNAVAILABLE")
    return e,artifacts[0]

def current_insurance_records(op):
    all_records=op.get("insurance_records",[])
    displaced={r.get("supersedes") for r in all_records if r.get("supersedes")}
    return deepcopy([r for r in all_records if r.get("id") not in displaced])

def record_insurance_document(
    op, *, evidence_id, document_kind, carrier_label, broker_label,
    source_locator, source_date, quote_valid_until, effective_date, expiration_date,
    planned_closing_date, coverage_codes, annual_premium, upfront_premium_due,
    limits_note, deductible_note, exclusion_note, actor_ref,
    upfront_in_financing_costs=False, annual_in_operating_expenses=False,
    supersedes=None, correction_reason=None,
):
    """Append an actual-source transcription, without selecting or binding it."""
    if document_kind not in DOCUMENT_KINDS:
        raise InsuranceError("UNSUPPORTED_INSURANCE_DOCUMENT_TYPE")
    e,a=_source(op,evidence_id)
    carrier=_text(carrier_label,"CARRIER_LABEL_REQUIRED",120)
    broker=_text(broker_label,"BROKER_LABEL_INVALID",120,required=False)
    locator=_text(source_locator,"SOURCE_LOCATOR_REQUIRED",240)
    actor=_text(actor_ref,"OWNER_ACTOR_REQUIRED",128)
    source_date=_day(source_date,"SOURCE_DATE_REQUIRED",required=True)
    expiry=_day(quote_valid_until,"QUOTE_EXPIRY_INVALID")
    start=_day(effective_date,"EFFECTIVE_DATE_INVALID")
    end=_day(expiration_date,"POLICY_END_DATE_INVALID")
    closing=_day(planned_closing_date,"PLANNED_CLOSING_DATE_INVALID")
    if document_kind=="QUOTE":
        if expiry is None:raise InsuranceError("WRITTEN_QUOTE_VALIDITY_REQUIRED")
        if expiry<source_date:raise InsuranceError("QUOTE_EXPIRES_BEFORE_SOURCE")
    elif expiry:
        raise InsuranceError("QUOTE_VALIDITY_ONLY_FOR_QUOTE")
    if (start is None)!=(end is None):
        raise InsuranceError("BOTH_COVERAGE_DATES_OR_NEITHER")
    if start and end<=start:raise InsuranceError("COVERAGE_END_MUST_FOLLOW_START")
    if not isinstance(coverage_codes,(tuple,list)) or not coverage_codes or len(coverage_codes)>len(COVERAGE_CODES):
        raise InsuranceError("COVERAGE_CODES_REQUIRED")
    if (any(not isinstance(code,str) or code not in COVERAGE_CODES for code in coverage_codes)
            or len(coverage_codes)!=len(set(coverage_codes))):
        raise InsuranceError("INVALID_OR_DUPLICATED_COVERAGE")
    if document_kind=="CERTIFICATE" and annual_premium in ("",None) and upfront_premium_due in ("",None):
        premium=None
        upfront=None
    else:
        premium=_amount(annual_premium,"ANNUAL_PREMIUM_INVALID",positive=True)
        upfront=_amount(upfront_premium_due,"UPFRONT_PREMIUM_INVALID")
    included_closing=_yes_no(upfront_in_financing_costs,"CLOSING_COST_TREATMENT_REQUIRED")
    included_ops=_yes_no(annual_in_operating_expenses,"OPERATING_EXPENSE_TREATMENT_REQUIRED")
    notes={
        "limits_note":_text(limits_note,"LIMITS_NOTE_INVALID",1000,required=False),
        "deductible_note":_text(deductible_note,"DEDUCTIBLE_NOTE_INVALID",1000,required=False),
        "exclusion_note":_text(exclusion_note,"EXCLUSION_NOTE_INVALID",1000,required=False),
    }
    prior=None
    if supersedes:
        prior=next((q for q in current_insurance_records(op)
                    if q.get("id")==supersedes),None)
        if prior is None:raise InsuranceError("ACTIVE_CORRECTION_TARGET_REQUIRED")
        if (prior["carrier_label"].casefold()!=carrier.casefold() or
                prior["document_kind"]!=document_kind):
            raise InsuranceError("CORRECTION_SOURCE_SCOPE_MISMATCH")
        _text(correction_reason,"CORRECTION_REASON_REQUIRED",1000)
    elif correction_reason not in ("",None):
        raise InsuranceError("CORRECTION_TARGET_REQUIRED")
    record={
        "id":str(uuid4()),"source_evidence_id":e["id"],
        "source_artifact_id":a["id"],"source_sha256":a["sha256"],
        "document_kind":document_kind,"carrier_label":carrier,"broker_label":broker,
        "source_locator":locator,"source_date":source_date,
        "quote_valid_until":expiry,"effective_date":start,"expiration_date":end,
        "planned_closing_date":closing,"coverage_codes":list(coverage_codes),
        "annual_premium":premium,"upfront_premium_due":upfront,
        **notes,
        "upfront_in_financing_costs":included_closing,
        "annual_in_operating_expenses":included_ops,
        "recorded_by":actor,"source_evidence_status":e["status"],
        "record_type":"OWNER_TRANSCRIBED_INSURANCE_ORIGINAL",
        "supersedes":prior["id"] if prior else None,
        "correction_reason":correction_reason.strip() if prior else None,
        "coverage_in_force":"UNKNOWN","insurer_confirmation_verified":False,
        "lender_compliance_verified":False,"teller_readiness":"UNKNOWN",
        "premium_paid_verified":False,"insurance_purchased_by_buybox":False,
        "authorizes_acquisition":False,
    }
    from .workflow import invalidate_on_change
    revised=deepcopy(op)
    revised.setdefault("insurance_records",[]).append(record)
    revised=invalidate_on_change(revised,changed_fields=["insurance_records"],
            reason="Original-backed owner insurance terms added or corrected",
            source_reference=a["id"])
    return revised,deepcopy(record)

def _reviewed_original(op,record):
    a=next((x for x in op.get("artifacts",[]) if
            x.get("id")==record.get("source_artifact_id")),None)
    original=next((x for x in op.get("evidence",[]) if
                   x.get("id")==record.get("source_evidence_id")),None)
    if not a or a.get("sha256")!=record.get("source_sha256") or not original or original.get("artifact_id")!=a["id"]:
        return False,False
    if original.get("status")=="DOCUMENT_SUPPORTED":return True,True
    reviewed=any(x.get("supersedes")==original["id"] and
                 x.get("artifact_id")==a["id"] and
                 x.get("status")=="DOCUMENT_SUPPORTED" for x in op.get("evidence",[]))
    return True,reviewed

def inspect_insurance_record(op,record,*,today=None):
    if today is None:today=date.today()
    if isinstance(today,str):today=date.fromisoformat(today)
    if not isinstance(today,date):raise InsuranceError("REVIEW_DATE_INVALID")
    linked,reviewed=_reviewed_original(op,record)
    flags=[]
    if not linked:flags.append("ORIGINAL_LINK_OR_DIGEST_CHANGED")
    if date.fromisoformat(record["source_date"])>today:
        flags.append("DOCUMENT_DATE_IN_FUTURE")
    quote_expiry=record.get("quote_valid_until")
    if quote_expiry and date.fromisoformat(quote_expiry)<today:
        flags.append("QUOTE_RECORD_EXPIRED")
    closing=record.get("planned_closing_date")
    if closing:
        if quote_expiry and quote_expiry<closing:
            flags.append("QUOTE_VALIDITY_BEFORE_PROPOSED_CLOSING")
        if record.get("effective_date") is None:
            flags.append("COVERAGE_DATES_UNSTATED_FOR_CLOSING")
        elif not(record["effective_date"]<=closing<record["expiration_date"]):
            flags.append("COVERAGE_DATES_DO_NOT_INCLUDE_PROPOSED_CLOSING")
    elif not record.get("effective_date"):
        flags.append("COVERAGE_PERIOD_UNKNOWN")
    if record["document_kind"]=="CERTIFICATE":
        flags.append("CERTIFICATE_ALONE_DOES_NOT_VERIFY_CURRENT_COVERAGE")
    if record["document_kind"]=="QUOTE":
        flags.append("QUOTE_IS_NOT_BOUND_POLICY")
    annual=(Decimal(record["annual_premium"])
            if record["annual_premium"] is not None else None)
    upfront=(Decimal(record["upfront_premium_due"])
             if record["upfront_premium_due"] is not None else None)
    return {
        "record_id":record["id"],
        "status":"SOURCE_RECHECK_REQUIRED" if flags else "DOCUMENT_RECORDED_UNVERIFIED",
        "review_flags":flags,
        "source_documentary_reviewed":reviewed,
        "annual_premium":str(annual) if annual is not None else None,
        "upfront_premium_due":str(upfront) if upfront is not None else None,
        "illustrative_monthly_premium":(
            str((annual/12).quantize(Decimal("0.01"))) if annual is not None else None),
        "source_link_intact":linked,
        "coverage_in_force":"UNKNOWN","bound_coverage_verified":False,
        "premium_paid_verified":False,"lender_compliance_verified":False,
        "external_insurer_contact":False,"authorizes_acquisition":False,
    }

def insurance_snapshot(op,*,today=None):
    rows=current_insurance_records(op)
    return {
        "opportunity_id":op["id"],"current_document_count":len(rows),
        "records":[{"record":record,"assessment":inspect_insurance_record(op,record,today=today)}
                   for record in rows],
        "review_prompts":list(VERTICAL_PROMPTS[op["vertical"]]),
        "review_prompts_are_requirements":False,
        "coverage_in_force":"UNKNOWN","insurer_verified":False,
        "lender_conditions_satisfied":False,"teller_readiness":"UNKNOWN",
        "coverage_purchased_by_buybox":False,"authorizes_acquisition":False,
    }

def project_financing_with_insurance(op, insurance_record, financing_option, *,today=None):
    """Owner-assumed side-by-side overlay; never mutates either financial source.

    Double-count protection comes from explicit owner indication of whether the
    proposed premium was already included in existing acquisition/annual costs.
    No insurance record is silently selected for a loan or summed with alternative
    packages. Working capital and ATM vault float remain distinct liquidity.
    """
    from .financing import option_analysis
    base=option_analysis(op,financing_option,today=today)
    ins=inspect_insurance_record(op,insurance_record,today=today)
    if (insurance_record.get("annual_premium") is None or
            insurance_record.get("upfront_premium_due") is None):
        raise InsuranceError("DOCUMENT_HAS_NO_RECORDED_PREMIUM_TO_MODEL")
    upfront=Decimal(insurance_record["upfront_premium_due"])
    annual=Decimal(insurance_record["annual_premium"])
    additional_upfront=(Decimal("0") if insurance_record["upfront_in_financing_costs"] else upfront)
    adjusted_cash=(Decimal(base["unverified_buyer_cash_gap"])+additional_upfront).quantize(Decimal("0.01"))
    operating=base["annual_operating_difference"]
    adjusted_operating=None
    if operating is not None:
        adjusted_operating=Decimal(operating)-(
            Decimal("0") if insurance_record["annual_in_operating_expenses"] else annual)
    return {
        "financing_option_id":financing_option["id"],
        "insurance_record_id":insurance_record["id"],
        "financing_freshness_flags":base["review_flags"],
        "insurance_freshness_flags":ins["review_flags"],
        "illustrative_buyer_cash_gap_with_premium":str(adjusted_cash),
        "additional_upfront_premium_if_not_already_counted":str(additional_upfront.quantize(Decimal("0.01"))),
        "illustrative_annual_operating_after_premium":str(adjusted_operating) if adjusted_operating is not None else None,
        "premium_inclusion_is_owner_assumption":True,
        "premium_not_double_counted_by_model":True,
        "teller_money_and_management":"UNKNOWN",
        "coverage_in_force":"UNKNOWN","loan_approved":False,
        "authorizes_purchase_or_spend":False,
    }
