from typing import Dict, List


def evaluate_portfolio_stress(positions: List[Dict]) -> Dict:
    count = len(positions)

    if count <= 3:
        state = "low"
    elif count <= 6:
        state = "moderate"
    else:
        state = "high"

    return {
        "position_count": count,
        "stress_state": state,
    }
