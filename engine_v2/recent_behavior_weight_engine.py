from typing import Dict, List


def build_recent_behavior_weight(trade_results: List[Dict]) -> Dict:
    if not trade_results:
        return {
            "behavior_weight_adjustment": 0,
            "behavior_state": "neutral",
            "behavior_reason": "no recent behavior data available",
        }

    valid = [t for t in trade_results if isinstance(t, dict)]
    recent = valid[-10:] if len(valid) > 10 else valid

    wins = sum(1 for t in recent if str(t.get("outcome", "")).lower() == "win")
    total = len(recent)
    win_rate = wins / total if total else 0.0

    if win_rate >= 0.65:
        adj = 10
        state = "supportive"
        reason = "recent behavior supports current deployment confidence"
    elif win_rate >= 0.50:
        adj = 0
        state = "neutral"
        reason = "recent behavior does not justify major adjustment"
    elif win_rate >= 0.35:
        adj = -10
        state = "cautious"
        reason = "recent behavior suggests some trust reduction"
    else:
        adj = -20
        state = "punitive"
        reason = "recent behavior should materially reduce trust"

    return {
        "behavior_weight_adjustment": adj,
        "behavior_state": state,
        "behavior_reason": reason,
        "recent_behavior_win_rate": round(win_rate, 4),
    }
