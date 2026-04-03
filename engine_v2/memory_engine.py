from typing import Dict, List


def build_memory_snapshot(trade_results: List[Dict]) -> Dict:
    if not trade_results:
        return {
            "recent_win_rate": 0.0,
            "recent_loss_rate": 0.0,
            "recent_count": 0,
            "memory_state": "empty",
            "memory_reason": "no trade history available",
        }

    valid = [t for t in trade_results if isinstance(t, dict)]
    total = len(valid)

    wins = sum(1 for t in valid if str(t.get("outcome", "")).lower() == "win")
    losses = sum(1 for t in valid if str(t.get("outcome", "")).lower() == "loss")

    win_rate = wins / total if total else 0.0
    loss_rate = losses / total if total else 0.0

    if total < 5:
        memory_state = "thin"
        reason = "history exists, but sample is still thin"
    elif win_rate >= 0.60:
        memory_state = "healthy"
        reason = "recent memory supports current trust"
    elif win_rate >= 0.45:
        memory_state = "mixed"
        reason = "recent memory is usable, but not clean"
    else:
        memory_state = "strained"
        reason = "recent memory suggests weakening quality"

    return {
        "recent_win_rate": round(win_rate, 4),
        "recent_loss_rate": round(loss_rate, 4),
        "recent_count": total,
        "memory_state": memory_state,
        "memory_reason": reason,
    }
