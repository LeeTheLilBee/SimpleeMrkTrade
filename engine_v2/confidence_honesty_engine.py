from typing import Dict, List


def evaluate_confidence_honesty(trade_results: List[Dict]) -> Dict:
    if not trade_results:
        return {
            "confidence_state": "unknown",
            "confidence_gap": 0,
            "confidence_reason": "no trade results available",
        }

    high_conf = [t for t in trade_results if float(t.get("edge_score", 0)) >= 85]
    low_conf = [t for t in trade_results if float(t.get("edge_score", 0)) < 70]

    def _win_rate(items: List[Dict]) -> float:
        if not items:
            return 0.0
        wins = sum(1 for t in items if t.get("outcome") == "win")
        return wins / len(items)

    high_rate = _win_rate(high_conf)
    low_rate = _win_rate(low_conf)
    gap = high_rate - low_rate

    if gap >= 0.12:
        state = "honest"
        reason = "higher-confidence trades are materially outperforming"
    elif gap >= -0.03:
        state = "inflated"
        reason = "confidence separation is too weak"
    else:
        state = "dishonest"
        reason = "higher-confidence trades are not outperforming lower-confidence ones"

    return {
        "confidence_state": state,
        "confidence_gap": round(gap, 4),
        "confidence_reason": reason,
        "high_conf_win_rate": round(high_rate, 4),
        "low_conf_win_rate": round(low_rate, 4),
    }
