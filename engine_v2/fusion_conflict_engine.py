from typing import Dict, List


def resolve_fusion_conflicts(
    decision: Dict,
    execution: Dict,
    portfolio: Dict,
    regime: Dict,
    threat: Dict,
    opportunity: Dict,
    governance: Dict,
) -> Dict:
    issues: List[str] = []
    final_blocked = False

    if governance.get("kill_switch", {}).get("kill_switch_active"):
        issues.append("governance kill switch overrides all execution")
        final_blocked = True

    if governance.get("hard_stops", {}).get("hard_stop_blocked"):
        issues.append("hard stop blocks deployment")
        final_blocked = True

    if governance.get("integrity", {}).get("integrity_ok") is False:
        issues.append("system integrity not verified")
        final_blocked = True

    if threat.get("threat_score", {}).get("threat_level") == "extreme":
        issues.append("extreme threat level suppresses normal execution")
        final_blocked = True

    if regime.get("regime_block") is True:
        issues.append("regime filter blocks this setup")
        final_blocked = True

    if portfolio.get("contribution", {}).get("contribution") == "negative":
        issues.append("portfolio contribution is negative")
    
    if execution.get("entry_state") == "missed":
        issues.append("entry window has already been missed")
        final_blocked = True

    if decision.get("ready_state") == "reject":
        issues.append("decision layer rejected the trade")
        final_blocked = True

    if opportunity.get("displacement", {}).get("displacement") == "strong":
        issues.append("capital should strongly favor the top-ranked alternative")

    return {
        "conflict_count": len(issues),
        "blocked": final_blocked,
        "issues": issues,
    }
