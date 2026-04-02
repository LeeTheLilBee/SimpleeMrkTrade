from typing import Dict


def calibrate_confidence(decision: Dict, outcome: Dict) -> Dict:
    edge = decision.get("edge_score", 0)
    result = outcome.get("outcome")

    adjustment = 0

    if edge > 85 and result == "loss":
        adjustment = -5
    elif edge < 70 and result == "win":
        adjustment = +5

    return {
        "confidence_adjustment": adjustment
    }
