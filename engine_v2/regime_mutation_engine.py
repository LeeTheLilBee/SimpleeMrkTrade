from typing import Dict


def suggest_regime_mutation(regime: Dict, meta: Dict) -> Dict:
    state = regime.get("market_regime", "neutral")

    if state == "trending":
        return {
            "mutation_mode": "trend_bias",
            "reason": "favor continuation and directional setups",
        }

    if state == "volatile":
        return {
            "mutation_mode": "risk_contraction",
            "reason": "tighten execution and suppress aggressive behavior",
        }

    if state == "choppy":
        return {
            "mutation_mode": "breakout_suppression",
            "reason": "reduce breakout trust and increase caution",
        }

    return {
        "mutation_mode": "neutral_balance",
        "reason": "no strong regime mutation required",
    }
