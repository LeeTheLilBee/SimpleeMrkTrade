from typing import Dict, List


def rank_opportunities(decisions: List[Dict]) -> List[Dict]:
    def score(d: Dict) -> float:
        base = float(d.get("edge_score", 0))
        timing = float(d.get("timing_quality_score", 0))
        thesis = 20 if d.get("thesis_quality") == "strong" else 10
        portfolio = 15 if d.get("portfolio_fit") == "strong" else 5

        threat = d.get("threat_level", "low")
        threat_penalty = {"low": 0, "medium": -15, "high": -30, "extreme": -50}.get(threat, 0)

        return base + timing + thesis + portfolio + threat_penalty

    ranked = sorted(decisions, key=score, reverse=True)

    return [
        {
            "symbol": d.get("symbol"),
            "total_score": round(score(d), 2),
            "priority_rank": i + 1,
        }
        for i, d in enumerate(ranked)
    ]
