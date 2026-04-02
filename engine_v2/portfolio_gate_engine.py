from typing import Dict

from engine_v2.risk_philosophy import is_capital_worthy


def evaluate_portfolio_fit(decision: Dict) -> Dict:
    if not is_capital_worthy(decision):
        return {
            "portfolio_fit": "weak",
            "portfolio_reason": "does not currently justify capital deployment",
        }

    priority = decision.get("priority_label", "low")

    if priority == "kill_shot":
        fit = "strong"
        reason = "best available use of capital"
    elif priority == "high":
        fit = "good"
        reason = "supports portfolio quality"
    elif priority == "medium":
        fit = "neutral"
        reason = "valid but not a priority use of capital"
    else:
        fit = "weak"
        reason = "low impact addition"

    return {
        "portfolio_fit": fit,
        "portfolio_reason": reason,
    }
