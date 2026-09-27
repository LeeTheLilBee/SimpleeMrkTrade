"""BBX057-061: source-bound, owner-entered financing term-sheet comparisons.

Never a lender approval, loan application, funding commitment or Teller
readiness response. Models fixed-rate, fully amortizing USD terms only; other
structures must have dedicated later rules, not a fabricated monthly payment.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import date
from decimal import Decimal, ROUND_HALF_UP, localcontext
from uuid import uuid4
import re

CENTS=Decimal("0.01")
MAX_USD=Decimal("1000000000000.00")
MONEY=re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?\Z")
RATE=re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{1,4})?\Z")
MAX_APR=Decimal("100")
FINANCING_EVIDENCE_KIND="financing_terms"

class FinancingError(ValueError):
    pass

def _text(value, code, length):
    if not isinstance(value,str) or not value.strip() or len(value)>length or "\x00" in value:
        raise FinancingError(code)
    return value.strip()

def _usd(value,code,positive=False):
    if not isinstance(value,str) or len(value)>30 or not MONEY.fullmatch(value):
        raise FinancingError(code)
    v=Decimal(value)
    if v>MAX_USD or (v<=0 if positive else v<0):
        raise FinancingError(code)
    return v.quantize(CENTS)

def _apr(value):
    if not isinstance(value,str) or not RATE.fullmatch(value) or len(value)>12:
        raise FinancingError("APR_FORMAT_INVALID")
    value=Decimal(value)
    if value>MAX_APR:
        raise FinancingError("APR_OUT_OF_RANGE")
    return value

def _date(value,code):
    try:
        result=date.fromisoformat(value)
        if result.isoformat()!=value: raise ValueError
        return result
    except (TypeError, ValueError):
        raise FinancingError(code) from None

def _source(op,evidence_id):
    records=[e for e in op.get("evidence",[]) if e.get("id")==evidence_id
             and e.get("kind")==FINANCING_EVIDENCE_KIND
             and e.get("status") in ("RECEIVED","DOCUMENT_SUPPORTED")]
    if len(records)!=1 or not records[0].get("artifact_id"):
        raise FinancingError("ACTUAL_ACTIVE_FINANCING_ORIGINAL_REQUIRED")
    e=records[0]
    artifacts=[a for a in op.get("artifacts",[]) if a.get("id")==e["artifact_id"]
               and re.fullmatch(r"[a-f0-9]{64}",str(a.get("sha256","")))]
    if len(artifacts)!=1: raise FinancingError("ORIGINAL_DIGEST_UNAVAILABLE")
    return e,artifacts[0]

def current_options(op):
    options=op.get("financing_options",[])
    superseded={x.get("supersedes") for x in options if x.get("supersedes")}
    return deepcopy([x for x in options if x.get("id") not in superseded])

def record_financing_option(op, *, evidence_id, lender_name, program_name,
                            source_locator, source_date, expiration_date,
                            purchase_price, principal, apr_percent, term_months,
                            origination_fee, lender_fee, other_closing_cost,
                            reserve_cash, vault_cash, actor_ref,
                            structure="FIXED_FULLY_AMORTIZING",
                            supersedes=None, correction_reason=None):
    """Transcribe a real original; never silently accept or send its terms."""
    if structure!="FIXED_FULLY_AMORTIZING":
        raise FinancingError("LOAN_STRUCTURE_NOT_SUPPORTED")
    e,a=_source(op,evidence_id)
    lender=_text(lender_name,"LENDER_LABEL_REQUIRED",120)
    program=_text(program_name,"PROGRAM_LABEL_REQUIRED",120)
    locator=_text(source_locator,"DOCUMENT_LOCATOR_REQUIRED",240)
    actor=_text(actor_ref,"REVIEWER_REFERENCE_REQUIRED",128)
    source_day=_date(source_date,"SOURCE_DATE_REQUIRED")
    expiration=_date(expiration_date,"EXPIRATION_DATE_REQUIRED") if expiration_date else None
    if expiration and expiration<source_day:
        raise FinancingError("EXPIRES_BEFORE_SOURCE_DATE")
    price=_usd(purchase_price,"PRICE_INVALID",positive=True)
    loan=_usd(principal,"PRINCIPAL_INVALID",positive=True)
    rate=_apr(apr_percent)
    if isinstance(term_months,bool) or not isinstance(term_months,str) or not re.fullmatch(r"[1-9][0-9]*",term_months):
        raise FinancingError("MONTHS_INVALID")
    months=int(term_months)
    if not 12<=months<=360: raise FinancingError("ONLY_12_TO_360_MONTH_AMORTIZING_TERMS_SUPPORTED")
    fees={
        "origination_fee":_usd(origination_fee,"ORIGINATION_FEE_INVALID"),
        "lender_fee":_usd(lender_fee,"LENDER_FEE_INVALID"),
        "other_closing_cost":_usd(other_closing_cost,"OTHER_CLOSING_COST_INVALID"),
        "reserve_cash":_usd(reserve_cash,"RESERVE_INVALID"),
        "vault_cash":_usd(vault_cash,"VAULT_CASH_INVALID"),
    }
    if op["vertical"]!="atm" and fees["vault_cash"]!=0:
        raise FinancingError("ATM_VAULT_CASH_ONLY")
    capital_required=price+sum(fees.values(),Decimal("0"))
    if loan>capital_required:
        raise FinancingError("LOAN_EXCEEDS_RECORDED_PROJECT_COST")
    prior=None
    if supersedes:
        prior=next((q for q in current_options(op) if q["id"]==supersedes),None)
        if prior is None: raise FinancingError("CURRENT_OPTION_CORRECTION_TARGET_REQUIRED")
        if (prior["lender_label"].casefold()!=lender.casefold()
                or prior["program_label"].casefold()!=program.casefold()):
            raise FinancingError("CORRECTION_PROVIDER_AND_PROGRAM_SCOPE_MISMATCH")
        _text(correction_reason,"CORRECTION_REASON_REQUIRED",1000)
    elif correction_reason not in (None,""):
        raise FinancingError("CORRECTION_TARGET_REQUIRED")
    record={
        "id":str(uuid4()),"source_evidence_id":e["id"],
        "source_artifact_id":a["id"],"source_sha256":a["sha256"],
        "source_locator":locator,"source_date":source_day.isoformat(),
        "expiration_date":expiration.isoformat() if expiration else None,
        "source_evidence_status":e["status"],
        "lender_label":lender,"program_label":program,
        "term_structure":structure,"currency":"USD",
        "purchase_price":str(price),"principal":str(loan),
        "apr_percent":str(rate),"term_months":months,
        **{k:str(v) for k,v in fees.items()},
        "asking_price_basis":op.get("asking_price"),
        "recorded_against_revision":op.get("version"),
        "recorded_by":actor,
        "record_type":"OWNER_TRANSCRIBED_ORIGINAL",
        "source_term_fields":["lender_label","program_label","principal","apr_percent","term_months",
                              "origination_fee","lender_fee","source_date","expiration_date"],
        "owner_cost_assumption_fields":["purchase_price","other_closing_cost","reserve_cash","vault_cash"],
        "lender_approval_confirmed":False,"teller_readiness":"UNKNOWN",
        "authorizes_money":False,"authorizes_acquisition":False,
        "supersedes":prior["id"] if prior else None,
        "correction_reason":correction_reason.strip() if prior else None,
    }
    revised=deepcopy(op)
    revised.setdefault("financing_options",[]).append(record)
    from .workflow import invalidate_on_change
    revised=invalidate_on_change(revised,
        changed_fields=["financing_options"],
        reason="Owner recorded source-bound alternative financing terms",
        source_reference=a["id"])
    return revised,deepcopy(record)

def monthly_payment(principal,apr,months):
    principal=Decimal(principal); rate=Decimal(apr)
    with localcontext() as ctx:
        ctx.prec=48
        r=rate/Decimal("1200")
        amount=(principal/Decimal(months) if r==0 else
                principal*r/(Decimal("1")-(Decimal("1")+r)**(-months)))
    return amount.quantize(CENTS,rounding=ROUND_HALF_UP)

def scheduled_cashflows(principal, apr, months):
    """Cent-rounded fixed amortization with an adjusted final payment."""
    balance=Decimal(principal)
    rate=Decimal(apr)/Decimal("1200")
    nominal=monthly_payment(principal,apr,months)
    payments=[]
    accrued=Decimal("0")
    with localcontext() as ctx:
        ctx.prec=48
        for month in range(1,months+1):
            interest=(balance*rate).quantize(CENTS,rounding=ROUND_HALF_UP)
            due=(balance+interest).quantize(CENTS,rounding=ROUND_HALF_UP)
            actual=due if month==months or due<nominal else nominal
            principal_paid=actual-interest
            if principal_paid<0:
                raise FinancingError("NON_AMORTIZING_MODEL_NOT_SUPPORTED")
            balance=(balance-principal_paid).quantize(CENTS,rounding=ROUND_HALF_UP)
            accrued+=interest
            payments.append(actual)
    return {
        "nominal_payment":nominal,
        "first_year_payment":sum(payments[:12],Decimal("0")),
        "total":sum(payments,Decimal("0")),
        "interest":accrued.quantize(CENTS),
        "last_payment":payments[-1],
        "end_balance":balance,
    }

def option_analysis(op, quote, *, today=None):
    today=today or date.today()
    if isinstance(today,str):today=_date(today,"EVALUATION_DATE_INVALID")
    if not isinstance(today,date):raise FinancingError("EVALUATION_DATE_INVALID")
    a=next((item for item in op.get("artifacts",[])
            if item.get("id")==quote["source_artifact_id"]),None)
    evidence=next((item for item in op.get("evidence",[])
                   if item.get("id")==quote["source_evidence_id"]),None)
    source_ok=bool(a and a.get("sha256")==quote["source_sha256"] and
                   evidence and evidence.get("artifact_id")==a["id"])
    reviewed_current=bool(source_ok and (
        evidence.get("status")=="DOCUMENT_SUPPORTED" or
        any(e.get("supersedes")==evidence["id"] and
            e.get("artifact_id")==a["id"] and
            e.get("status")=="DOCUMENT_SUPPORTED"
            for e in op.get("evidence",[]))))
    expiration=quote.get("expiration_date")
    reasons=[]
    if not source_ok:reasons.append("ORIGINAL_DOCUMENT_LINK_OR_HASH_CHANGED")
    if expiration and _date(expiration,"EXPIRATION_DATE_INVALID")<today:
        reasons.append("RECORDED_TERMS_EXPIRED")
    if _date(quote["source_date"],"SOURCE_DATE_REQUIRED")>today:
        reasons.append("RECORDED_SOURCE_DATE_IN_FUTURE")
    if quote.get("asking_price_basis")!=op.get("asking_price"):
        reasons.append("OPPORTUNITY_ASKING_PRICE_CHANGED")
    schedule=scheduled_cashflows(quote["principal"],quote["apr_percent"],quote["term_months"])
    payment=schedule["nominal_payment"]
    principal=Decimal(quote["principal"])
    total=schedule["total"]
    modeled_interest=schedule["interest"]
    cost_fields=("origination_fee","lender_fee","other_closing_cost","reserve_cash","vault_cash")
    total_project=Decimal(quote["purchase_price"])+sum((Decimal(quote[k]) for k in cost_fields),Decimal("0"))
    owner_gap=total_project-principal
    from .core import scenario_calculation
    base=scenario_calculation(op)
    annual=schedule["first_year_payment"]
    operating=None
    coverage=None
    if base["status"]=="CALCULATED":
        operating=Decimal(base["net"])
        coverage=(operating/annual).quantize(Decimal("0.001"),rounding=ROUND_HALF_UP) if annual else None
    return {
        "option_id":quote["id"],"record_type":"SOURCE_TRANSCRIPTION_AND_MODELED_FINANCING",
        "review_flags":reasons,
        "status":"RECHECK_SOURCE_OR_PRICE" if reasons else "RECORDED_NOT_APPROVED",
        "source_documentary_reviewed":reviewed_current,
        "modeled_monthly_payment":str(payment),
        "modeled_annual_debt_service":str(annual),
        "modeled_total_scheduled_payments":str(total),
        "modeled_adjusted_final_payment":str(schedule["last_payment"]),
        "modeled_interest":str(modeled_interest),
        "recorded_project_cash_needed":str(total_project.quantize(CENTS)),
        "unverified_buyer_cash_gap":str(owner_gap.quantize(CENTS)),
        "reserve_cash_is_cost":False,"vault_cash_is_cost":False,
        "annual_operating_difference":str(operating) if operating is not None else None,
        "illustrative_operating_to_debt_ratio":str(coverage) if coverage is not None else None,
        "source_scope":"ORIGINAL_DOCUMENT_PLUS_OWNER_ENTERED_COST_ASSUMPTIONS",
        "bank_commitment":False,"loan_approval":False,"teller_readiness":"UNKNOWN",
        "money_and_management_readiness":"UNKNOWN",
        "tower_authorization":False,"funding_available":False,
    }

def financing_snapshot(op, *, today=None):
    quotes=current_options(op)
    return {"opportunity_id":op["id"],"active_option_count":len(quotes),
            "options":[{"quote":q,"analysis":option_analysis(op,q,today=today)}
                       for q in quotes],
            "teller_readiness":"UNKNOWN","bank_commitment_confirmed":False,
            "offers_sent_by_buybox":False,"authorizes_acquisition":False}
