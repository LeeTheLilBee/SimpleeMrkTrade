from typing import Dict


def suggest_dynamic_weighting(meta: Dict, regime: Dict) -> Dict:
    confidence = meta.get("confidence_honesty", {})
    drift = meta.get("drift", {})
    signal_quality = meta.get("signal_quality", {})

    suggestions = {}

    if confidence.get("confidence_state") in {"inflated", "dishonest"}:
        suggestions["confidence_weight"] = "decrease"

    if drift.get("drift_state") in {"soft_drift", "hard_drift"}:
        suggestions["timing_weight"] = "increase"

    if signal_quality.get("signal_quality_state") in {"crowded", "noisy"}:
        suggestions["selectivity_weight"] = "increase"

    if not suggestions:
        suggestions["weighting"] = "hold"

    return suggestions
