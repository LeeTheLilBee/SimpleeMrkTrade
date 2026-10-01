"""Acquisition workflow commands and invalidation. No unverified external authority.

The workflow is a state machine, separate from BuyBox's analytical judgment.
Only pre-authorization states can transition locally. Protected transitions need
verified Tower/Teller adapters that are NOT part of this package yet.
"""
from __future__ import annotations
from copy import deepcopy
from uuid import uuid4
from .core import LIFECYCLE, now, evaluate, evidence_summary

TRANSITIONS = {
    "DISCOVERED": ("WATCHING", "SCREENING", "ARCHIVED"),
    "WATCHING": ("SCREENING", "ARCHIVED"),
    "SCREENING": ("EVIDENCE_GATHERING", "WATCHING", "ARCHIVED"),
    "EVIDENCE_GATHERING": ("UNDERWRITING", "SCREENING", "ARCHIVED"),
    "UNDERWRITING": ("OWNER_REVIEW", "EVIDENCE_GATHERING", "ARCHIVED"),
    "OWNER_REVIEW": ("UNDERWRITING", "ARCHIVED"),
    "NEGOTIATION": ("OWNER_REVIEW", "ARCHIVED"),
    "LOI": ("NEGOTIATION", "ARCHIVED"),
    "DILIGENCE": ("LOI", "EVIDENCE_GATHERING", "ARCHIVED"),
    "FINANCING": ("DILIGENCE", "ARCHIVED"),
    "CLOSING_READY": ("FINANCING", "DILIGENCE", "ARCHIVED"),
    "CLOSING": ("CLOSING_READY", "ARCHIVED"),
    "ACQUIRED": ("HANDOFF",),
    "HANDOFF": ("PERFORMANCE_REVIEW",),
    "PERFORMANCE_REVIEW": ("ARCHIVED",),
    "ARCHIVED": ("WATCHING",),
}
# Owner review can be requested locally, but no code path in this module may
# progress past owner review or into contractual, financial, or acquired states.
PROTECTED_TARGETS = frozenset({
    "NEGOTIATION", "LOI", "DILIGENCE", "FINANCING", "CLOSING_READY",
    "CLOSING", "ACQUIRED", "HANDOFF", "PERFORMANCE_REVIEW",
})
REQUIRED_EVIDENCE_GATES = frozenset({"UNDERWRITING", "OWNER_REVIEW"})

def _event(op, kind, details):
    return {"id":str(uuid4()), "type":kind, "at":now(), "details":deepcopy(details),
            "opportunity_id":op["id"], "snapshot_revision":op.get("version")}

def gate_report(op, target):
    """Return reasons without raising, suitable for a focus-card explanation."""
    if target not in LIFECYCLE:
        return {"ready":False, "reasons":["UNKNOWN_STAGE"]}
    current=op.get("lifecycle")
    if target not in TRANSITIONS.get(current,()):
        return {"ready":False, "reasons":["INVALID_TRANSITION"]}
    if target in PROTECTED_TARGETS:
        return {"ready":False, "reasons":["VERIFIED_TOWER_AND_TELLER_ADAPTERS_NOT_CONNECTED"]}
    if target in REQUIRED_EVIDENCE_GATES:
        assessment=evaluate(op)
        if assessment["evidence"]["conflicts"]:
            return {"ready":False,"reasons":["EVIDENCE_CONFLICT"]}
        if target=="OWNER_REVIEW" and assessment["financials"]["status"]!="CALCULATED":
            return {"ready":False,"reasons":["UNDERWRITING_INPUTS_INCOMPLETE"]}
    return {"ready":True,"reasons":[]}

def transition(op,target,*,actor_reference,reason):
    if not isinstance(actor_reference,str) or not actor_reference.strip():
        raise ValueError("ACTOR_REQUIRED")
    if not isinstance(reason,str) or not reason.strip():
        raise ValueError("TRANSITION_REASON_REQUIRED")
    report=gate_report(op,target)
    if not report["ready"]:
        raise ValueError("STAGE_GATE_BLOCKED:"+",".join(report["reasons"]))
    revised=deepcopy(op)
    before=revised["lifecycle"]
    revised["lifecycle"]=target
    revised.setdefault("events",[]).append(_event(revised,"StageTransitioned",
                     {"from":before,"to":target,"actor":actor_reference,"reason":reason}))
    revised["updated_at"]=now()
    return revised

def invalidate_on_change(op,*,changed_fields,reason,source_reference):
    """Invalidate downstream analysis, readiness and protected authorizations.

    This routine does not delete historical snapshots or source documents.
    A newer analysis may be produced only after a fresh evaluation.
    """
    if not changed_fields or not reason or not source_reference:
        raise ValueError("CHANGE_PROVENANCE_REQUIRED")
    revised=deepcopy(op)
    revised["last_material_change"]={"fields":list(changed_fields),"reason":reason,
        "source_reference":source_reference,"at":now()}
    revised["analysis_state"]="STALE"
    revised["readiness"]={"teller":None,"grounds":None}
    revised["tower_authorizations"]=[]
    revised["attention"]="ACTION_NEEDED"
    revised.setdefault("events",[]).append(_event(revised,"MaterialChangeInvalidated",
        {"fields":list(changed_fields),"reason":reason,"source_reference":source_reference}))
    revised["updated_at"]=now()
    return revised

def add_decision_snapshot(op,assessment,*,actor_reference,reason):
    """Local analytical decision note, explicitly NOT an approval to progress."""
    if not actor_reference or not reason:
        raise ValueError("DECISION_ATTRIBUTION_REQUIRED")
    revised=deepcopy(op)
    revised.setdefault("decisions",[]).append({
        "id":str(uuid4()),"kind":"ANALYTICAL_OWNER_NOTE","actor":actor_reference,
        "reason":reason,"at":now(),"opportunity_revision":op.get("version"),
        "judgment":assessment["judgment"],
        "financials":deepcopy(assessment["financials"]),
        "finding_ids":[f["rule_id"] for f in assessment["findings"]],
        "tower_authorization":None, "authorizes_purchase":False,
    })
    return revised
