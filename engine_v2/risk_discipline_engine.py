from typing import Dict


def evaluate_risk_discipline(decision: Dict, user_state: Dict) -> Dict:
    action = str(decision.get("action", "wait") or "wait")
    confidence = str(decision.get("confidence", "low") or "low")

    max_risk = float(user_state.get("max_risk_per_trade", 1.0) or 1.0)
    current_risk = float(user_state.get("current_risk", 1.0) or 1.0)

    discipline = "aligned"
    reason = "risk behavior is acceptable"

    if current_risk > max_risk:
        discipline = "overrisking"
        reason = "user is exceeding defined risk limits"
    elif action == "act" and confidence == "low":
        discipline = "undisciplined_entry"
        reason = "low confidence trade should not receive capital"

    return {
        "risk_discipline": discipline,
        "risk_discipline_reason": reason,
    }
