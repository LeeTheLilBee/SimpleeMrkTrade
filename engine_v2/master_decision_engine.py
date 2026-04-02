from typing import Dict


def build_master_decision(
    signal: Dict,
    decision: Dict,
    execution: Dict,
    learning: Dict,
    experience: Dict,
    meta: Dict,
    portfolio: Dict,
    regime: Dict,
    evolution: Dict,
    thesis: Dict,
    timeline: Dict,
    coordination: Dict,
    threat: Dict,
    opportunity: Dict,
    governance: Dict,
    conflicts: Dict,
) -> Dict:
    threat_level = threat.get("threat_score", {}).get("threat_level", "low")
    capital_action = opportunity.get("priorities", {}).get("priorities", [])
    governance_blocked = conflicts.get("blocked", False)

    if governance_blocked:
        final_state = "blocked"
    elif decision.get("ready_state") == "ready_now" and execution.get("entry_state") in {"clean", "acceptable"}:
        final_state = "actionable"
    elif decision.get("ready_state") == "ready_soon":
        final_state = "prepare"
    elif decision.get("ready_state") == "watch":
        final_state = "monitor"
    else:
        final_state = "reject"

    return {
        "symbol": signal.get("symbol"),
        "company_name": signal.get("company_name", signal.get("symbol")),
        "final_state": final_state,
        "decision": decision,
        "execution": execution,
        "learning": learning,
        "experience": experience,
        "meta": meta,
        "portfolio": portfolio,
        "regime": regime,
        "evolution": evolution,
        "thesis": thesis,
        "timeline": timeline,
        "coordination": coordination,
        "threat": threat,
        "opportunity": opportunity,
        "governance": governance,
        "conflicts": conflicts,
        "threat_level": threat_level,
        "governance_blocked": governance_blocked,
        "capital_priority_snapshot": capital_action,
    }
