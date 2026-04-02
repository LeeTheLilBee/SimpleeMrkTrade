from typing import Dict, List


def evaluate_cluster_exposure(positions: List[Dict], new_decision: Dict) -> Dict:
    cluster = new_decision.get("correlation_cluster")

    same_cluster = [p for p in positions if p.get("correlation_cluster") == cluster]
    count = len(same_cluster)

    if count <= 1:
        state = "balanced"
    elif count <= 3:
        state = "elevated"
    else:
        state = "concentrated"

    return {
        "cluster": cluster,
        "existing_positions": count,
        "cluster_state": state,
    }
