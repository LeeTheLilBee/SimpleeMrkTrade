from typing import Dict, List

from engine_v2.cluster_exposure_engine import evaluate_cluster_exposure
from engine_v2.position_overlap_engine import evaluate_overlap
from engine_v2.portfolio_stress_engine import evaluate_portfolio_stress
from engine_v2.portfolio_contribution_engine import evaluate_contribution


def build_portfolio_intelligence(positions: List[Dict], new_decision: Dict) -> Dict:
    cluster = evaluate_cluster_exposure(positions, new_decision)
    overlap = evaluate_overlap(positions, new_decision)
    stress = evaluate_portfolio_stress(positions)
    contribution = evaluate_contribution(positions, new_decision)

    return {
        "cluster_exposure": cluster,
        "overlap": overlap,
        "portfolio_stress": stress,
        "contribution": contribution,
    }
