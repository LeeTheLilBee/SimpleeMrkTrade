from typing import List, Dict

from engine_v2.portfolio_gate_engine import evaluate_portfolio_fit


def rank_positions(decisions: List[Dict]) -> List[Dict]:
    ranked = sorted(
        [d for d in decisions if isinstance(d, dict)],
        key=lambda d: (
            d.get("edge_score", 0),
            d.get("timing_score", 0),
        ),
        reverse=True,
    )

    for i, d in enumerate(ranked):
        d["priority_rank"] = i + 1

        if i == 0:
            d["priority_label"] = "kill_shot"
        elif i < 3:
            d["priority_label"] = "high"
        elif i < 6:
            d["priority_label"] = "medium"
        else:
            d["priority_label"] = "low"

        d.update(evaluate_portfolio_fit(d))

    return ranked
