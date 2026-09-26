"""Read-only contextual Soulaana intelligence for REAL owner records.

This is a grounded deterministic explanation service, not a live generative
model, not Tower authentication, and not any kind of approval authority.
Nothing here writes opportunity truth or invents unavailable integrations.
"""
from __future__ import annotations
from .core import evaluate, soulaana_brief
from .registry import get_vertical
from .dealroom import current_tasks

INTENTS = frozenset({
    "overview", "evidence", "economics", "changes", "red_team", "next_action"
})

def context(op, intent="overview"):
    if intent not in INTENTS:
        raise ValueError("UNSUPPORTED_SOULAANA_INTENT")
    analysis = evaluate(op)
    manifest = get_vertical(op["vertical"])
    evidence = analysis["evidence"]
    entries=[]
    def note(kind, message, refs=None, label=None):
        entries.append({"classification":kind,"text":message,
                        "references":list(refs or []),"label":label})
    relevant = {
        "overview":{"evidence","economics","changes"},
        "evidence":{"evidence"},
        "economics":{"economics"},
        "changes":{"changes"},
        "red_team":{"economics","evidence"},
        "next_action":{"evidence","changes"},
    }[intent]
    if "evidence" in relevant:
        for row in evidence["rows"]:
            kind=row["kind"].replace("_"," ").title()
            if row["state"] in ("DOCUMENT_SUPPORTED","THIRD_PARTY_VERIFIED"):
                note("DOCUMENTARY_SUPPORT",
                    kind+" has recorded support; this does not independently certify the asset or claim.",
                    [row["reference"]] if row["reference"] else [],
                    row["state"])
            elif row["state"]=="CONFLICTED":
                note("CONFLICT",kind+" contains unresolved contradictory evidence.",
                     [row["reference"]] if row["reference"] else [],"REVIEW_REQUIRED")
            elif row["critical"]:
                note("MISSING_OR_UNVERIFIED",
                     kind+" is not established at the required documentary standard.",
                     [row["reference"]] if row["reference"] else [],row["state"])
    if "economics" in relevant:
        result=analysis["financials"]
        if result["status"]=="CALCULATED":
            revenue=op.get("metrics",{}).get("annual_revenue",{})
            expenses=op.get("metrics",{}).get("annual_expenses",{})
            refs=[x.get("evidence_id") for x in (revenue,expenses) if x.get("evidence_id")]
            note("BUYBOX_CALCULATION",
                 "Annual operating difference is $"+result["net"]+
                 " from the recorded revenue and expense figures for the same reported period. "
                 "It is not independently verified net profit or a complete acquisition valuation.",
                 refs,"PRELIMINARY_FORMULA")
        else:
            note("MISSING_OR_UNVERIFIED",
                 "Financial calculation is unavailable: "+result["status"].replace("_"," ").lower()+
                 ". Documented revenue and expenses must cover matching periods.",
                 label=result["status"])
    if "changes" in relevant:
        change=op.get("last_material_change")
        if change:
            note("RECORDED_EVENT",
                 change["reason"]+". Affected fields: "+", ".join(change["fields"])+
                 ". Previously held external readiness and protected approvals cannot be reused.",
                 [change["source_reference"]],"STALE_ANALYSIS")
        else:
            note("RECORDED_STATE","No material change has been recorded for this opportunity.")
    for finding in analysis["findings"]:
        note("POLICY_RESULT",finding["reason"],[finding["rule_id"]],finding["level"])
    if intent=="red_team":
        note("MODELING_LIMITATION",
             "A full stress result requires accepted vertical-specific assumptions and inputs. "
             "BuyBox will not invent lost locations, loan terms, vault cash or property operating figures.",
             label="NO_INVENTED_SCENARIO")
    if intent=="next_action":
        tasks=[x for x in current_tasks(op) if x["status"] in ("OPEN","WAITING")]
        if tasks:
            first=tasks[0]
            note("OWNER_RECORDED_TASK",
                 "Next recorded task: "+first["title"]+"; due "+first["due_date"]+".",
                 [first["id"]],first["status"])
        elif evidence["missing_critical"]:
            note("RULE_DERIVED_ACTION",
                 "Request or verify "+evidence["missing_critical"][0].replace("_"," ")+".",
                 label="PROPOSED_NOT_EXECUTED")
        else:
            note("RULE_DERIVED_ACTION",
                 "Review the dossier and applicable stage requirements. No protected action is authorized.",
                 label="PROPOSED_NOT_EXECUTED")
    brief=soulaana_brief(op,analysis)
    return {
        "speaker":"Soulaana", "mode":"DETERMINISTIC_GROUNDED_CONTEXT",
        "live_ai_connected":False, "opportunity_id":op["id"],
        "opportunity_revision":op.get("version"), "intent":intent,
        "vertical":manifest["label"],"judgment":analysis["judgment"],
        "summary":brief["summary"],"entries":entries,
        "readiness":analysis["teller_readiness"],
        "can_edit_evidence":False,"can_authorize":False,"can_send_offers":False,
        "source_note":"Owner-recorded inputs and BuyBox calculations; external integrations are not connected.",
    }
