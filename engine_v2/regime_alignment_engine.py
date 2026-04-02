from typing import Dict


def evaluate_regime_alignment(regime: Dict, decision: Dict) -> Dict:
    state = regime.get("market_regime")
    setup_type = decision.get("setup_type", "unknown")

    alignment = "neutral"
    reason = "no strong alignment detected"

    if state == "trending" and setup_type == "continuation":
        alignment = "favored"
        reason = "trend supports continuation setups"

    elif state == "choppy" and setup_type == "breakout":
        alignment = "suppressed"
        reason = "choppy conditions reduce breakout reliability"

    elif state == "volatile":
        alignment = "caution"
        reason = "high volatility increases risk"

    return {
        "regime_alignment": alignment,
        "regime_reason": reason,
    }
