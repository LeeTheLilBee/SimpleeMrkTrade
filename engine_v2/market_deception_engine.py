from typing import Dict


def detect_market_deception(signal: Dict, regime: Dict, context: Dict) -> Dict:
    follow_through = float(context.get("follow_through_score", 0) or 0)
    breadth = float(regime.get("breadth_score", 0) or 0)
    trend = float(regime.get("trend_strength", 0) or 0)

    if trend > 60 and follow_through < 40:
        state = "high"
        reason = "surface trend strength is not producing real follow-through"
    elif breadth < 40 and trend > 50:
        state = "medium"
        reason = "leadership appears narrow and potentially deceptive"
    else:
        state = "low"
        reason = "market behavior is not showing a strong deception profile"

    return {
        "market_deception_level": state,
        "market_deception_reason": reason,
    }
