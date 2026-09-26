"""Deterministic, fail-closed acquisition evaluations.

Readiness and authorization are external, signed/verified by their owning systems.
No seller claim is silently promoted to verified fact. No scoring changes policy.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import uuid4
from .registry import get_vertical

JUDGMENTS = ("MISSING_EVIDENCE", "REVIEW", "QUALIFIED", "EXCEPTION_REQUIRED", "REJECTED")
EVIDENCE_STATES = ("CLAIMED", "RECEIVED", "DOCUMENT_SUPPORTED", "THIRD_PARTY_VERIFIED",
                   "CONFLICTED", "STALE", "MISSING", "NOT_APPLICABLE")
LIFECYCLE = ("DISCOVERED", "WATCHING", "SCREENING", "EVIDENCE_GATHERING",
             "UNDERWRITING", "OWNER_REVIEW", "NEGOTIATION", "LOI", "DILIGENCE",
             "FINANCING", "CLOSING_READY", "CLOSING", "ACQUIRED", "HANDOFF",
             "PERFORMANCE_REVIEW", "ARCHIVED")
SENSITIVE_ACTIONS = ("LOI", "CLOSING_READY", "CLOSING", "ACQUIRED", "HANDOFF")

def now():
    return datetime.now(timezone.utc).isoformat()

def money(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        x = Decimal(str(value))
        return x if x.is_finite() else None
    except (InvalidOperation, TypeError, ValueError):
        return None

def string_money(value):
    x = money(value)
    return str(x.quantize(Decimal("0.01"))) if x is not None else None

def new_opportunity(vertical, name, asking_price=None, source=None, location=None):
    get_vertical(vertical)
    oid = str(uuid4())
    timestamp = now()
    return {
        "id": oid, "vertical": vertical, "name": str(name).strip() or "Untitled Opportunity",
        "created_at": timestamp, "updated_at": timestamp, "version": 1,
        "lifecycle": "DISCOVERED", "attention": "WATCH",
        "asking_price": string_money(asking_price), "location": location or {},
        "sources": [source] if source else [], "evidence": [], "metrics": {},
        "assumptions": {}, "vertical_data": {}, "events": [], "decisions": [],
        "snapshots": [], "readiness": {"teller": None, "grounds": None},
        "tower_authorizations": [], "owner_notes": [],
        "scenario_overrides": {}, "handoff": None,
    }

def add_evidence(op, kind, status="RECEIVED", reference=None, source=None,
                 effective_at=None, observed_at=None, notes=""):
    get_vertical(op["vertical"])
    if status not in EVIDENCE_STATES:
        raise ValueError("Invalid evidence state")
    record = {"id": str(uuid4()), "kind": kind, "status": status,
              "reference": reference, "source": source, "effective_at": effective_at,
              "observed_at": observed_at or now(), "notes": notes}
    op["evidence"].append(record)
    return record

def evidence_summary(op):
    manifest = get_vertical(op["vertical"])
    rows, total, supported = [], 0, 0
    latest = {}
    for e in op.get("evidence", []):
        previous = latest.get(e["kind"])
        if not previous or (e.get("observed_at") or "") >= (previous.get("observed_at") or ""):
            latest[e["kind"]] = e
    for req in manifest["evidence"]:
        evidence = latest.get(req["kind"])
        state = evidence["status"] if evidence else "MISSING"
        good = state in ("DOCUMENT_SUPPORTED", "THIRD_PARTY_VERIFIED")
        total += req["weight"]
        supported += req["weight"] if good else 0
        rows.append({"kind":req["kind"],"state":state,"critical":req["critical"],
                     "weight":req["weight"],"reference":evidence.get("reference") if evidence else None})
    conflicts = [r["kind"] for r in rows if r["state"]=="CONFLICTED"]
    missing_critical = [r["kind"] for r in rows if r["critical"] and r["state"] not in
                        ("DOCUMENT_SUPPORTED", "THIRD_PARTY_VERIFIED")]
    return {"confidence_percent":int(Decimal(supported * 100 / total).quantize(Decimal("1"))) if total else 0,
            "rows":rows,"missing_critical":missing_critical,"conflicts":conflicts}

def _metric(op, key):
    record = op.get("metrics", {}).get(key)
    if not isinstance(record, dict) or record.get("state") not in ("DOCUMENT_SUPPORTED", "THIRD_PARTY_VERIFIED", "BUYBOX_CALCULATED"):
        return None
    return money(record.get("value"))

def _readiness(op, name):
    """An arbitrary serialized dictionary is NOT evidence of live readiness.

    An authenticated cross-app verification adapter has not been connected.
    Return unknown regardless of user-stored or shaped integration fields until
    we have a trusted, non-user-supplied connector result bound to the request.
    """
    return "UNKNOWN"

def scenario_calculation(op, revenue_factor="1", expense_factor="1"):
    revenue_record = op.get("metrics", {}).get("annual_revenue", {})
    expense_record = op.get("metrics", {}).get("annual_expenses", {})
    revenue = _metric(op, "annual_revenue")
    expenses = _metric(op, "annual_expenses")
    rf, ef = money(revenue_factor), money(expense_factor)
    if revenue is None or expenses is None or rf is None or ef is None or rf < 0 or ef < 0:
        return {"status":"INSUFFICIENT_DATA", "net":None, "purchase_multiple":None}
    revenue_period = revenue_record.get("period") if isinstance(revenue_record, dict) else None
    expense_period = expense_record.get("period") if isinstance(expense_record, dict) else None
    if not revenue_period or not expense_period or revenue_period != expense_period:
        return {"status":"PERIOD_MISMATCH", "net":None, "purchase_multiple":None}
    net = revenue*rf - expenses*ef
    asking = money(op.get("asking_price"))
    multiple = asking/net if asking is not None and net > 0 else None
    return {"status":"CALCULATED", "net":string_money(net),
            "purchase_multiple":string_money(multiple) if multiple is not None else None,
            "revenue_factor":str(rf),"expense_factor":str(ef)}

def _atm_rules(op, ev):
    findings = []
    def finding(rule, level, reason):
        findings.append({"rule_id":rule,"level":level,"reason":reason})
    inventory = op.get("vertical_data", {}).get("machine_inventory", [])
    if inventory:
        for machine in inventory:
            if machine.get("included",True) and machine.get("ownership") == "THIRD_PARTY":
                finding("ATM-R001","BLOCK","Included machine has third-party ownership: "+str(machine.get("id","unknown")))
            if machine.get("included",True) and machine.get("ownership") not in ("SELLER_OWNED","THIRD_PARTY"):
                finding("ATM-R001","BLOCK","Included machine ownership not verified: "+str(machine.get("id","unknown")))
        included = [m for m in inventory if m.get("included",True)]
        ids=[m.get("id") for m in included]
        if any(not x for x in ids) or len(set(ids)) != len(ids):
            finding("ATM-R002","BLOCK","Included machine inventory has missing/duplicate identifiers")
    elif op.get("lifecycle") in ("DILIGENCE","FINANCING","CLOSING_READY","CLOSING"):
        finding("ATM-R002","BLOCK","No serial-numbered machine inventory")
    if ev["conflicts"]:
        finding("ATM-R017","BLOCK","Conflicted evidence: "+", ".join(ev["conflicts"]))
    if op.get("lifecycle") in ("CLOSING_READY","CLOSING") and ev["missing_critical"]:
        finding("ATM-R003","BLOCK","Critical evidence is not verified for closing")
    largest=_metric(op,"largest_location_share")
    if largest is not None and largest > Decimal("0.30"):
        finding("ATM-R009","REVIEW","Largest location exceeds proposed 30% concentration warning")
    return findings

def evaluate(op):
    vertical=get_vertical(op["vertical"])
    ev=evidence_summary(op)
    base=scenario_calculation(op)
    findings=_atm_rules(op,ev) if op["vertical"]=="atm" else (
        [{"rule_id":"CORE-EVIDENCE","level":"BLOCK","reason":"Conflicted source evidence"}]
        if ev["conflicts"] else [])
    teller=_readiness(op,"teller")
    # External readiness is not assumed merely because the financial model is positive.
    if teller=="BLOCKED":
        findings.append({"rule_id":"CORE-TELLER","level":"BLOCK","reason":"Teller reports blocked deployment or capacity"})
    if teller=="UNKNOWN":
        findings.append({"rule_id":"CORE-TELLER","level":"UNKNOWN","reason":"No current authoritative Teller readiness"})
    net=money(base.get("net"))
    if net is not None and net <= 0:
        findings.append({"rule_id":"CORE-ECONOMICS","level":"REVIEW","reason":"Non-positive normalized annual cash flow"})
    if any(f["level"]=="BLOCK" for f in findings):
        judgment="REJECTED" if any(f["rule_id"]=="ATM-R001" and "third-party" in f["reason"] for f in findings) else "REVIEW"
    elif ev["missing_critical"]:
        judgment="MISSING_EVIDENCE"
    elif base["status"]!="CALCULATED":
        judgment="MISSING_EVIDENCE"
    elif teller!="READY" or findings:
        judgment="REVIEW"
    else:
        judgment="QUALIFIED"
    # Qualified means analytical screening only; never authorization to buy.
    return {"opportunity_id":op["id"],"vertical":op["vertical"],
            "registry_version":vertical["version"],"evaluated_at":now(),
            "judgment":judgment,"evidence":ev,"financials":base,
            "findings":findings,"teller_readiness":teller,
            "closing_authorized":False,"purchase_authorized":False}

def compare_opportunities(ops):
    if not 2<=len(ops)<=4:
        raise ValueError("Compare between two and four opportunities")
    return [{"id":op["id"],"name":op["name"],"asking_price":op["asking_price"],
             "vertical":op["vertical"],"evaluation":evaluate(op)} for op in ops]

def soulaana_brief(op, result=None):
    """A grounded, deterministic explanation stub, not an AI or decision authority."""
    r=result or evaluate(op)
    reasons=[f["reason"] for f in r["findings"]]
    if r["evidence"]["missing_critical"]:
        reasons.append("Critical proof outstanding: "+", ".join(r["evidence"]["missing_critical"][:3]))
    if not reasons:
        reasons=["No rule findings in the current snapshot; review all stage requirements before proceeding."]
    return {"speaker":"Soulaana", "type":"GROUNDED_BUYBOX_BRIEF",
            "judgment":r["judgment"],"summary":reasons[0],
            "next_action":"Resolve the first outstanding finding or review the evidence dossier." if
                (r["findings"] or r["evidence"]["missing_critical"]) else "Review the opportunity dossier.",
            "grounding":{"opportunity_id":op["id"],
                         "rule_ids":[x["rule_id"] for x in r["findings"]],
                         "evidence_kinds":r["evidence"]["missing_critical"]},
            "can_approve":False,"can_change_evidence":False}
