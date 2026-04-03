from typing import Dict


def enforce_only_the_ones(
    cross_symbol: Dict,
    best_in_cluster: Dict,
) -> Dict:
    relative_state = str(cross_symbol.get("relative_state", "unknown"))
    is_best_cluster = bool(best_in_cluster.get("is_best_in_cluster", False))

    allowed = True
    reason = "passes selectivity filter"

    if relative_state not in {"best_expression", "competitive"}:
        allowed = False
        reason = "not strong enough relative to alternatives"

    if not is_best_cluster:
        allowed = False
        reason = "not the best expression in its cluster"

    return {
        "only_the_ones_allowed": allowed,
        "only_the_ones_reason": reason,
    }
