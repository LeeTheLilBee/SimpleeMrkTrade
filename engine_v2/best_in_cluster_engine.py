from typing import Dict, List


def select_best_in_cluster(target_symbol: str, opportunities: List[Dict]) -> Dict:
    valid = [o for o in opportunities if isinstance(o, dict)]
    if not valid:
        return {
            "cluster_best_symbol": None,
            "is_best_in_cluster": False,
            "cluster_reason": "no cluster opportunities available",
        }

    target = next((o for o in valid if o.get("symbol") == target_symbol), None)
    if not target:
        return {
            "cluster_best_symbol": None,
            "is_best_in_cluster": False,
            "cluster_reason": "target symbol is not in the cluster set",
        }

    cluster = target.get("correlation_cluster")
    same_cluster = [o for o in valid if o.get("correlation_cluster") == cluster]

    if not same_cluster:
        return {
            "cluster_best_symbol": target_symbol,
            "is_best_in_cluster": True,
            "cluster_reason": "no competing symbols exist in this cluster",
        }

    ranked = sorted(
        same_cluster,
        key=lambda o: float(o.get("edge_quality_score", o.get("edge_score", 0)) or 0),
        reverse=True,
    )

    leader = ranked[0].get("symbol")
    is_best = leader == target_symbol

    if is_best:
        reason = "this symbol is the cleanest expression in its cluster"
    else:
        reason = f"{leader} currently appears stronger inside the same cluster"

    return {
        "cluster_best_symbol": leader,
        "is_best_in_cluster": is_best,
        "cluster_reason": reason,
        "cluster_name": cluster,
        "cluster_competition_count": len(ranked),
    }
