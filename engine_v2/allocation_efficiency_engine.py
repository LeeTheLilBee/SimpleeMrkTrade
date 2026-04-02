from typing import List, Dict


def evaluate_allocation_efficiency(ranked: List[Dict]) -> Dict:
    if not ranked:
        return {"efficiency": "unknown", "reason": "no opportunities available"}

    top_scores = [r["total_score"] for r in ranked[:3]]

    spread = max(top_scores) - min(top_scores) if len(top_scores) > 1 else 0

    if spread > 30:
        state = "high"
        reason = "clear separation between top and mid-tier opportunities"
    elif spread > 10:
        state = "moderate"
        reason = "some separation exists, but not dominant"
    else:
        state = "low"
        reason = "opportunities are clustered with little differentiation"

    return {
        "allocation_efficiency": state,
        "efficiency_reason": reason,
    }
