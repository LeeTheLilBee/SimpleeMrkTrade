from typing import Dict, List


def evaluate_cross_symbol_strength(target_symbol: str, opportunities: List[Dict]) -> Dict:
    valid = [o for o in opportunities if isinstance(o, dict)]
    if not valid:
        return {
            "relative_state": "unknown",
            "relative_rank": None,
            "relative_reason": "no opportunities available for comparison",
        }

    ranked = sorted(
        valid,
        key=lambda o: float(o.get("edge_quality_score", o.get("edge_score", 0)) or 0),
        reverse=True,
    )

    rank = None
    for i, item in enumerate(ranked, start=1):
        if item.get("symbol") == target_symbol:
            rank = i
            break

    if rank is None:
        return {
            "relative_state": "unknown",
            "relative_rank": None,
            "relative_reason": "target symbol is not present in the comparison set",
        }

    if rank == 1:
        state = "best_expression"
        reason = "this symbol is currently the strongest expression in the active set"
    elif rank <= 3:
        state = "competitive"
        reason = "this symbol is valid, but stronger alternatives may exist"
    else:
        state = "secondary"
        reason = "this symbol is being outclassed by stronger opportunities"

    return {
        "relative_state": state,
        "relative_rank": rank,
        "relative_reason": reason,
        "comparison_count": len(ranked),
    }
