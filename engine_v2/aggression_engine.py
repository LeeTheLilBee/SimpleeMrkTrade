from typing import Dict

from engine_v2.risk_philosophy import should_reduce_aggression


def determine_aggression(decision: Dict) -> Dict:
    edge = decision.get("edge_score", 0)
    timing = decision.get("timing_score", 0)

    if should_reduce_aggression(decision):
        return {
            "aggression_level": "low",
            "aggression_reason": "risk philosophy reduced aggression",
        }

    if edge > 85 and timing > 70:
        level = "high"
        reason = "strong edge and clean timing"
    elif edge > 70 and timing > 55:
        level = "medium"
        reason = "good setup but not max conviction"
    else:
        level = "low"
        reason = "setup quality does not justify aggression"

    return {
        "aggression_level": level,
        "aggression_reason": reason,
    }
