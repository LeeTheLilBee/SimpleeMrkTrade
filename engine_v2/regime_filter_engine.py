from typing import Dict


def apply_regime_filter(regime: Dict, decision: Dict) -> Dict:
    state = regime.get("market_regime")
    setup = decision.get("setup_type", "unknown")

    if state == "choppy" and setup == "breakout":
        return {
            "regime_block": True,
            "regime_block_reason": "breakouts unreliable in chop",
        }

    if state == "volatile":
        return {
            "regime_block": False,
            "regime_block_reason": "allowed with caution",
        }

    return {
        "regime_block": False,
        "regime_block_reason": "no regime conflict",
    }
