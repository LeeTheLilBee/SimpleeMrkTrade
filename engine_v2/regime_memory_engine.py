from typing import Dict


def evaluate_regime_memory(setup_type: str, regime: Dict, setup_stats: Dict) -> Dict:
    market_regime = str(regime.get("market_regime", "neutral") or "neutral")
    families = setup_stats.get("families", {}) if isinstance(setup_stats, dict) else {}
    stats = families.get(setup_type, {})

    win_rate = float(stats.get("win_rate", 0) or 0)

    adjustment = 0
    reason = "no specific regime memory adjustment"

    if market_regime == "trending" and setup_type in {"continuation", "steady_continuation"}:
        adjustment = 10
        reason = "regime memory favors continuation behavior in trend"
    elif market_regime == "choppy" and setup_type in {"breakout", "breakout_extension"}:
        adjustment = -15
        reason = "regime memory penalizes breakout behavior in chop"
    elif market_regime == "volatile" and win_rate < 0.45:
        adjustment = -10
        reason = "volatile regime plus weak family history reduces trust"

    return {
        "regime_memory_adjustment": adjustment,
        "regime_memory_reason": reason,
        "regime_memory_family_win_rate": round(win_rate, 4),
    }
