from typing import Dict, List


def evaluate_contribution(positions: List[Dict], new_decision: Dict) -> Dict:
    cluster = new_decision.get("correlation_cluster")

    same_cluster = [p for p in positions if p.get("correlation_cluster") == cluster]

    if not same_cluster:
        impact = "positive"
        reason = "adds diversification"
    elif len(same_cluster) <= 2:
        impact = "neutral"
        reason = "adds exposure but remains controlled"
    else:
        impact = "negative"
        reason = "increases concentration risk"

    return {
        "contribution": impact,
        "contribution_reason": reason,
    }
