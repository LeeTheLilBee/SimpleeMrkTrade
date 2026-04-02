from typing import Dict

from engine_v2.threshold_tuning_engine import suggest_threshold_tuning
from engine_v2.dynamic_weighting_engine import suggest_dynamic_weighting
from engine_v2.family_penalty_engine import suggest_family_penalties
from engine_v2.signal_compression_engine import suggest_signal_compression
from engine_v2.regime_mutation_engine import suggest_regime_mutation


def build_autonomous_evolution(meta: Dict, regime: Dict) -> Dict:
    threshold_tuning = suggest_threshold_tuning(meta, regime)
    dynamic_weighting = suggest_dynamic_weighting(meta, regime)
    family_penalties = suggest_family_penalties(meta)
    signal_compression = suggest_signal_compression(meta)
    regime_mutation = suggest_regime_mutation(regime, meta)

    return {
        "threshold_tuning": threshold_tuning,
        "dynamic_weighting": dynamic_weighting,
        "family_penalties": family_penalties,
        "signal_compression": signal_compression,
        "regime_mutation": regime_mutation,
    }
