from typing import Dict, List

from engine_v2.opportunity_ranking_engine import rank_opportunities
from engine_v2.capital_priority_engine import assign_capital_priority
from engine_v2.displacement_engine import evaluate_displacement
from engine_v2.allocation_efficiency_engine import evaluate_allocation_efficiency


def build_opportunity_cost_intelligence(decisions: List[Dict]) -> Dict:
    ranked = rank_opportunities(decisions)
    priorities = assign_capital_priority(ranked)
    displacement = evaluate_displacement(ranked)
    efficiency = evaluate_allocation_efficiency(ranked)

    return {
        "ranked": ranked,
        "priorities": priorities,
        "displacement": displacement,
        "allocation_efficiency": efficiency,
    }
