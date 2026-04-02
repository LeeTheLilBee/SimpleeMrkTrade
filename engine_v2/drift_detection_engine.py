from typing import Dict, List


def detect_drift(trade_results: List[Dict]) -> Dict:
    if not trade_results:
        return {
            "drift_state": "unknown",
            "drift_score": 0,
            "drift_reason": "no trade results available",
        }

    wins = sum(1 for t in trade_results if t.get("outcome") == "win")
    losses = sum(1 for t in trade_results if t.get("outcome") == "loss")
    total = max(1, wins + losses)

    win_rate = wins / total

    if win_rate >= 0.55:
        state = "stable"
        score = 15
        reason = "recent performance remains healthy"
    elif win_rate >= 0.45:
        state = "soft_drift"
        score = 55
        reason = "recent performance is weakening"
    else:
        state = "hard_drift"
        score = 85
        reason = "recent performance suggests meaningful degradation"

    return {
        "drift_state": state,
        "drift_score": round(score, 2),
        "drift_reason": reason,
        "recent_win_rate": round(win_rate, 4),
    }
