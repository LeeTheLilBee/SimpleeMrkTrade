from typing import Dict


def evaluate_win_quality(trade: Dict) -> Dict:
    outcome = str(trade.get("outcome", "unknown") or "unknown")
    thesis_quality = str(trade.get("thesis_quality", "weak") or "weak")
    timing_quality = float(trade.get("timing_quality_score", 0) or 0)
    deception_level = str(trade.get("deception_level", "low") or "low")

    if outcome != "win":
        return {
            "win_quality": "not_applicable",
            "win_quality_reason": "trade was not a win",
        }

    if thesis_quality == "strong" and timing_quality >= 70 and deception_level == "low":
        state = "clean_win"
        reason = "win confirms both idea quality and execution quality"
    elif deception_level in {"high", "severe"}:
        state = "suspect_win"
        reason = "win occurred under deceptive conditions and should not be overtrusted"
    else:
        state = "mixed_win"
        reason = "win was real, but not fully clean"

    return {
        "win_quality": state,
        "win_quality_reason": reason,
    }
