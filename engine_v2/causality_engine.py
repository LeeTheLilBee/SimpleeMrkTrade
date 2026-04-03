from typing import Dict


def determine_trade_causality(trade: Dict) -> Dict:
    outcome = str(trade.get("outcome", "unknown") or "unknown")
    thesis_quality = str(trade.get("thesis_quality", "weak") or "weak")
    timing_quality = float(trade.get("timing_quality_score", 0) or 0)
    structure_quality = str(trade.get("contract_quality", "weak") or "weak")
    threat_level = str(trade.get("threat_level", "low") or "low")
    deception_level = str(trade.get("deception_level", "low") or "low")

    cause = "unclear"
    reason = "causality remains unclear"

    if outcome == "win":
        if thesis_quality == "strong" and timing_quality >= 70 and deception_level in {"low", "moderate"}:
            cause = "correct_thesis_correct_execution"
            reason = "trade worked because the thesis was right and execution held"
        elif thesis_quality == "strong" and timing_quality < 70:
            cause = "correct_thesis_imperfect_timing"
            reason = "trade worked, but timing quality was not optimal"
        elif deception_level in {"high", "severe"}:
            cause = "lucky_win_under_bad_conditions"
            reason = "trade won, but the environment was deceptive enough to reduce trust in the win"
        else:
            cause = "usable_win"
            reason = "trade worked, though the exact edge source is mixed"

    elif outcome == "loss":
        if thesis_quality == "strong" and timing_quality < 55:
            cause = "correct_thesis_bad_timing"
            reason = "the idea may have been right, but timing degraded the trade"
        elif thesis_quality == "weak":
            cause = "bad_thesis"
            reason = "the setup failed because the underlying thesis was weak"
        elif structure_quality in {"weak", "poor"}:
            cause = "bad_structure"
            reason = "the setup failed because contract or structure quality was too weak"
        elif threat_level in {"high", "extreme"} or deception_level in {"high", "severe"}:
            cause = "environment_overpowered_trade"
            reason = "market conditions were hostile enough to overpower the idea"
        else:
            cause = "execution_failure"
            reason = "the trade failed, but the failure appears more executional than conceptual"

    return {
        "causality_state": cause,
        "causality_reason": reason,
    }
