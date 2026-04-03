from typing import Dict, List


def filter_only_the_ones(opportunities: List[Dict], max_keep: int = 3) -> Dict:
    valid = [o for o in opportunities if isinstance(o, dict)]

    ranked = sorted(
        valid,
        key=lambda o: float(o.get("edge_quality_score", o.get("edge_score", 0)) or 0),
        reverse=True,
    )

    kept = ranked[:max_keep]
    suppressed = ranked[max_keep:]

    return {
        "kept_symbols": [item.get("symbol") for item in kept],
        "suppressed_symbols": [item.get("symbol") for item in suppressed],
        "kept_count": len(kept),
        "suppressed_count": len(suppressed),
    }
