from typing import Dict


def resolve_final_confidence(
    base_decision: Dict,
    enhanced_integration: Dict,
    truth_integration: Dict,
    behavior_intelligence: Dict,
) -> Dict:
    base_confidence = str(base_decision.get("confidence", "low") or "low")

    enhanced_package = enhanced_integration.get("enhanced_package", {}) if isinstance(enhanced_integration, dict) else {}
    enhanced_summary = enhanced_package.get("enhanced_summary", {}) if isinstance(enhanced_package, dict) else {}
    enhanced_confidence = str(enhanced_summary.get("final_confidence", base_confidence) or base_confidence)

    truth_override = truth_integration.get("truth_override", {}) if isinstance(truth_integration, dict) else {}
    truth_confidence = str(truth_override.get("truth_final_confidence", enhanced_confidence) or enhanced_confidence)

    behavior_override = behavior_intelligence.get("behavior_override", {}) if isinstance(behavior_intelligence, dict) else {}
    behavior_confidence = str(behavior_override.get("behavior_final_confidence", truth_confidence) or truth_confidence)

    final_confidence = base_confidence
    source = "base_decision"
    reason = "base confidence remains valid"

    if truth_confidence == "none":
        final_confidence = "none"
        source = "truth_enforcement"
        reason = "truth enforcement removed confidence entirely"
    elif behavior_confidence == "none":
        final_confidence = "none"
        source = "behavior_override"
        reason = "behavior guardrail removed confidence entirely"
    elif behavior_confidence != truth_confidence:
        final_confidence = behavior_confidence
        source = "behavior_override"
        reason = "behavior override adjusted confidence"
    elif enhanced_confidence != base_confidence:
        final_confidence = enhanced_confidence
        source = "enhanced_soulaana"
        reason = "enhanced Soulaana adjusted confidence"
    else:
        final_confidence = base_confidence
        source = "base_decision"
        reason = "no higher-priority layer overrode confidence"

    return {
        "final_confidence": final_confidence,
        "final_confidence_source": source,
        "final_confidence_reason": reason,
    }
