from typing import Dict

from engine_v2.counterfactual_trigger_engine import determine_counterfactual_trigger
from engine_v2.minimum_change_engine import determine_minimum_change
from engine_v2.alternate_path_engine import determine_alternate_path
from engine_v2.salvageability_engine import evaluate_salvageability
from engine_v2.counterfactual_explainer_engine import explain_counterfactual


def build_counterfactual_intelligence(trade: Dict) -> Dict:
    trigger = determine_counterfactual_trigger(trade)
    minimum_change = determine_minimum_change(trade, trigger)
    alternate_path = determine_alternate_path(trade, trigger)
    salvageability = evaluate_salvageability(trade, trigger, minimum_change)
    explainer = explain_counterfactual(trigger, minimum_change, alternate_path, salvageability)

    return {
        "counterfactual_trigger": trigger,
        "minimum_change": minimum_change,
        "alternate_path": alternate_path,
        "salvageability": salvageability,
        "counterfactual_explainer": explainer,
    }
