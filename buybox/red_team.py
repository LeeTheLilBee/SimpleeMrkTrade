"""BBX072–076: owner-entered, source-bound financial stress records.

Only models alternative assumptions against the ACTUAL saved, original-backed,
owner-reviewed annual revenue/expense figures from an identical 12-month period.
Never historical performance, vertical hazard modeling, lender coverage, Teller
readiness, Tower approval, a deal recommendation or money authorization.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from uuid import uuid4
import re
import sqlite3

from .core import scenario_calculation
from .store import encode
from .tower_action_draft import stored_source_snapshot, BuyBoxTowerActionPreparationError

FACTORS = re.compile(r"(?:0|[1-3])(?:\.[0-9]{1,4})?\Z")
SOURCE_STATES = frozenset({"DOCUMENT_SUPPORTED", "THIRD_PARTY_VERIFIED"})
MONEY = Decimal("0.01")
VERSION = "buybox.owner_stress.financial.v1"

class RedTeamError(ValueError):
    pass

def _text(value, code, limit):
    if not isinstance(value, str) or not value.strip() or len(value)>limit or "\x00" in value:
        raise RedTeamError(code)
    return value.strip()

def _factor(value):
    if not isinstance(value,str) or len(value)>10 or not FACTORS.fullmatch(value):
        raise RedTeamError("STRESS_FACTOR_MUST_BE_BETWEEN_0_AND_3")
    d=Decimal(value)
    if d>3:
        raise RedTeamError("STRESS_FACTOR_MUST_BE_BETWEEN_0_AND_3")
    return d

def _source_metric(op, key):
    m=op.get("metrics",{}).get(key)
    if not isinstance(m,dict) or m.get("state") not in SOURCE_STATES:
        raise RedTeamError("DOCUMENT_SUPPORTED_ANNUAL_METRICS_REQUIRED")
    evid=[e for e in op.get("evidence",[]) if e.get("id")==m.get("evidence_id")
          and e.get("status") in SOURCE_STATES and e.get("artifact_id")]
    if len(evid)!=1:
        raise RedTeamError("CURRENT_SOURCE_EVIDENCE_REQUIRED")
    artifact=[a for a in op.get("artifacts",[]) if a.get("id")==evid[0]["artifact_id"]
              and re.fullmatch(r"[a-f0-9]{64}",str(a.get("sha256","")))]
    if len(artifact)!=1:
        raise RedTeamError("ORIGINAL_SOURCE_DIGEST_REQUIRED")
    return {"metric":key,"evidence_id":evid[0]["id"],
            "original_id":artifact[0]["id"],
            "original_sha256":artifact[0]["sha256"],
            "period":m.get("period")}

def model_financial_stress(op, *, revenue_factor, expense_factor):
    """No stored state or original truth is changed by calculating a model."""
    r,e=_factor(revenue_factor),_factor(expense_factor)
    source_a=_source_metric(op,"annual_revenue")
    source_b=_source_metric(op,"annual_expenses")
    if not source_a["period"] or source_a["period"]!=source_b["period"]:
        raise RedTeamError("MATCHING_SOURCE_PERIODS_REQUIRED")
    base=scenario_calculation(op)
    stressed=scenario_calculation(op,str(r),str(e))
    if base.get("status")!="CALCULATED" or stressed.get("status")!="CALCULATED":
        raise RedTeamError("DOCUMENTED_FINANCIAL_MODEL_UNAVAILABLE")
    baseline=Decimal(base["net"])
    changed=Decimal(stressed["net"])
    return {
        "source_metrics":[source_a,source_b],
        "reporting_period":source_a["period"],
        "revenue_factor":str(r),
        "expense_factor":str(e),
        "recorded_operating_difference":str(baseline.quantize(MONEY)),
        "modeled_operating_difference":str(changed.quantize(MONEY)),
        "modeled_difference_from_base":str((changed-baseline).quantize(MONEY)),
        "modeled_purchase_multiple":stressed.get("purchase_multiple"),
        "source_record_scope":"OWNER_REVIEWED_DOCUMENTARY_SUPPORT_NOT_INDEPENDENT_AUDIT",
        "model_scope":"FINANCIAL_MULTIPLIER_ONLY_NO_VERTICAL_HAZARD_OR_DEBT_MODEL",
        "teller_money_and_management_readiness":"UNKNOWN",
        "funds_spendable":False,"bank_financing_approved":False,
        "tower_authorized":False,"automatically_favorable":False,
    }

def record_owner_financial_stress(db: sqlite3.Connection, op, *,
                                  name, rationale, revenue_factor,
                                  expense_factor, actor_ref):
    if not isinstance(db,sqlite3.Connection):
        raise RedTeamError("PERSISTED_SOURCE_REQUIRED")
    title=_text(name,"SCENARIO_TITLE_REQUIRED",120)
    reason=_text(rationale,"OWNER_ASSUMPTION_REASON_REQUIRED",1500)
    actor=_text(actor_ref,"OWNER_ACTOR_REQUIRED",128)
    try:
        saved=stored_source_snapshot(db,op["id"])
    except (BuyBoxTowerActionPreparationError,sqlite3.DatabaseError) as exc:
        raise RedTeamError("CURRENT_PERSISTED_SOURCE_UNAVAILABLE") from exc
    if (saved["opportunity_revision"]!=op.get("version") or
        saved["input_snapshot_digest"]!=sha256(encode(op).encode("utf-8")).hexdigest()):
        raise RedTeamError("SOURCE_CHANGED_BEFORE_STRESS_RECORDED")
    model=model_financial_stress(op,revenue_factor=revenue_factor,
                                 expense_factor=expense_factor)
    item={
        "id":str(uuid4()),"record_type":"OWNER_ASSUMPTION_NOT_HISTORICAL_FACT",
        "schema_version":VERSION,"name":title,"rationale":reason,
        "actor_ref":actor,
        "source_opportunity_id":op["id"],
        "source_opportunity_revision":saved["opportunity_revision"],
        "source_snapshot_digest":saved["input_snapshot_digest"],
        "recorded_opportunity_revision":op["version"]+1,
        "recorded_at":datetime.now(timezone.utc).isoformat(),
        **model,
        "executed":False,"changes_underwriting_metrics":False,
        "authorizes_offer":False,"authorizes_purchase":False,
    }
    revised=deepcopy(op)
    revised.setdefault("owner_stress_records",[]).append(item)
    return revised,deepcopy(item)

def red_team_report(op):
    """Previously recorded findings stay immutable and become stale on revisions."""
    records=[]
    for original in reversed(op.get("owner_stress_records",[])):
        x=deepcopy(original)
        x["freshness"]=("CURRENT_SOURCE_VERSION"
                        if op.get("version")==x["recorded_opportunity_revision"]
                        else "HISTORICAL_RECHECK_REQUIRED")
        records.append(x)
    return {"opportunity_id":op["id"],"records":records,
            "count":len(records),"has_current":any(x["freshness"]=="CURRENT_SOURCE_VERSION"
                                                   for x in records),
            "live_external_stress_feed":False,
            "live_teller_readiness":"UNKNOWN",
            "recommendation_made":False,"protected_action_authorized":False}
