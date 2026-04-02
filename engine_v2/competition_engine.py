from typing import Dict, List


def evaluate_trade_competition(decisions: List[Dict]) -> Dict:
    valid = [d for d in decisions if isinstance(d, dict)]

    ranked = sorted(
        valid,
        key=lambda d: (
            d.get("edge_score", 0),
            d.get("timing_quality_score", d.get("timing_score", 0)),
            1 if d.get("portfolio_fit") == "strong" else 0,
        ),
        reverse=True,
    )

    leaders = [d.get("symbol") for d in ranked[:3]]

    return {
        "leaders": leaders,
        "competition_count": len(ranked),
        "competition_state": "active" if len(ranked) > 1 else "simple",
    }
