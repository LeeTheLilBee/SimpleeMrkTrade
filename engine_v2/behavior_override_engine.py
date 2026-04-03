from typing import Dict


def apply_behavior_override(
    decision: Dict,
    emotional_bias: Dict,
    behavior_pattern: Dict,
    risk_discipline: Dict,
) -> Dict:
    action = str(decision.get("action", "wait") or "wait")
    confidence = str(decision.get("confidence", "low") or "low")

    bias = emotional_bias.get("emotional_bias")
    behavior = behavior_pattern.get("behavior_pattern")
    discipline = risk_discipline.get("risk_discipline")

    override = False
    override_reason = "no override applied"

    if discipline == "overrisking":
        action = "reject"
        confidence = "none"
        override = True
        override_reason = "risk discipline violation"
    elif bias == "revenge_trading_risk" and action == "act":
        action = "wait"
        override = True
        override_reason = "emotional bias restriction"
    elif behavior == "rule_breaking":
        action = "wait"
        override = True
        override_reason = "behavioral inconsistency"

    return {
        "behavior_final_action": action,
        "behavior_final_confidence": confidence,
        "behavior_override": override,
        "behavior_override_reason": override_reason,
    }
