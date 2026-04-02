from typing import List, Dict


def select_kill_shot(decisions: List[Dict]) -> Dict:
    ranked = sorted(
        decisions,
        key=lambda d: (
            d.get("edge_score", 0),
            d.get("timing_score", 0)
        ),
        reverse=True
    )

    if not ranked:
        return {"symbol": None}

    best = ranked[0]

    return {
        "symbol": best.get("symbol"),
        "reason": "highest edge + clean timing",
        "ready_state": best.get("ready_state"),
        "edge_score": best.get("edge_score"),
    }
