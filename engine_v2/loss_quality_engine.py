from typing import Dict


def evaluate_loss_quality(trade: Dict) -> Dict:
    outcome = str(trade.get("outcome", "unknown") or "unknown")
    timing_quality = float(trade.get("timing_quality_score", 0) or 0)
    threat_level = str(trade.get("threat_level", "low") or "low")
    deception_level = str(trade.get("deception_level", "low") or "low")
    thesis_quality = str(trade.get("thesis_quality", "weak") or "weak")

    if outcome != "loss":
        return {
            "loss_quality": "not_applicable",
            "loss_quality_reason": "trade was not a loss",
        }

    if threat_level in {"high", "extreme"} or deception_level in {"high", "severe"}:
        state = "hostile_loss"
        reason = "loss occurred in a hostile environment"
    elif timing_quality < 55 or thesis_quality == "weak":
        state = "avoidable_loss"
        reason = "loss appears avoidable through better filtering or timing"
    else:
        state = "informative_loss"
        reason = "loss provides useful learning without necessarily invalidating the pattern"

    return {
        "loss_quality": state,
        "loss_quality_reason": reason,
    }
