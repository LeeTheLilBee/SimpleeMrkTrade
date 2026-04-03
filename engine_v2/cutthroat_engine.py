from typing import Dict

from engine_v2.overconfidence_punisher import evaluate_overconfidence
from engine_v2.weak_setup_suppression import evaluate_weak_setup
from engine_v2.contradiction_enforcer import enforce_contradictions
from engine_v2.stand_down_engine import evaluate_stand_down
from engine_v2.emotional_neutralizer import evaluate_emotional_bias
from engine_v2.only_the_ones_enforcer import enforce_only_the_ones


def build_cutthroat_layer(
    signal: Dict,
    edge_quality: Dict,
    clarity: Dict,
    alignment: Dict,
    contradiction: Dict,
    threat: Dict,
    capital_gate: Dict,
    late_entry: Dict,
    cross_symbol: Dict,
    best_in_cluster: Dict,
) -> Dict:
    overconfidence = evaluate_overconfidence(
        edge_quality=edge_quality,
        clarity=clarity,
        contradiction=contradiction,
        threat=threat,
    )

    weak_setup = evaluate_weak_setup(
        edge_quality=edge_quality,
        clarity=clarity,
        alignment=alignment,
    )

    contradiction_enforcement = enforce_contradictions(
        contradiction=contradiction,
    )

    stand_down = evaluate_stand_down(
        capital_gate=capital_gate,
        late_entry=late_entry,
        contradiction=contradiction,
    )

    emotional = evaluate_emotional_bias(
        signal=signal,
        edge_quality=edge_quality,
    )

    only_the_ones = enforce_only_the_ones(
        cross_symbol=cross_symbol,
        best_in_cluster=best_in_cluster,
    )

    final_block = (
        stand_down["stand_down"]
        or weak_setup["suppressed"]
        or not only_the_ones["only_the_ones_allowed"]
    )

    return {
        "overconfidence": overconfidence,
        "weak_setup": weak_setup,
        "contradiction_enforcement": contradiction_enforcement,
        "stand_down": stand_down,
        "emotional": emotional,
        "only_the_ones": only_the_ones,
        "final_block": final_block,
    }
