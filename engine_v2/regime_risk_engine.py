from typing import Dict


def adjust_risk_for_regime(regime: Dict, decision: Dict) -> Dict:
    state = regime.get("market_regime")

    if state == "volatile":
        return {
            "regime_risk_adjustment": "reduce",
            "risk_reason": "high volatility environment",
        }

    if state == "choppy":
        return {
            "regime_risk_adjustment": "tighten",
            "risk_reason": "low directional clarity",
        }

    if state == "trending":
        return {
            "regime_risk_adjustment": "allow",
            "risk_reason": "favorable directional environment",
        }

    return {
        "regime_risk_adjustment": "neutral",
        "risk_reason": "no strong regime signal",
    }
