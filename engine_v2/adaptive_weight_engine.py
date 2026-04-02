from typing import Dict


def suggest_weight_adjustments(
    drift: Dict,
    confidence: Dict,
    setup_health: Dict,
    signal_quality: Dict,
) -> Dict:
    suggestions = []

    if drift.get("drift_state") in {"soft_drift", "hard_drift"}:
        suggestions.append("tighten timing thresholds")

    if confidence.get("confidence_state") in {"inflated", "dishonest"}:
        suggestions.append("reduce confidence weighting until honesty improves")

    weakest_family = setup_health.get("weakest_family")
    if weakest_family:
        family_info = setup_health.get("families", {}).get(weakest_family, {})
        if family_info.get("state") in {"weak", "failing"}:
            suggestions.append(f"downweight setup family: {weakest_family}")

    if signal_quality.get("signal_quality_state") in {"crowded", "noisy"}:
        suggestions.append("increase selectivity and compress mediocre output")

    if not suggestions:
        suggestions.append("no major adaptive changes suggested")

    return {
        "suggestions": suggestions
    }
