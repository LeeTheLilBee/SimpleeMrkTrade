from typing import Dict, List


def evaluate_overlap(positions: List[Dict], new_decision: Dict) -> Dict:
    direction = new_decision.get("direction")

    overlaps = [
        p for p in positions
        if p.get("direction") == direction
    ]

    if len(overlaps) >= 3:
        state = "high_overlap"
    elif len(overlaps) >= 1:
        state = "moderate_overlap"
    else:
        state = "low_overlap"

    return {
        "overlap_state": state,
        "overlap_count": len(overlaps),
    }
