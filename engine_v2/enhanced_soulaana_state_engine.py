from typing import Dict


def build_enhanced_soulaana_state(
    base_soulaana: Dict,
    enhanced_edge_quality: Dict,
    enhanced_clarity: Dict,
    deception_penalty: Dict,
    memory_adjustment: Dict,
    intent_adjustment: Dict,
) -> Dict:
    base_score = float(base_soulaana.get("soulaana_score", 0) or 0)
    enhanced_edge_score = float(
        enhanced_edge_quality.get("enhanced_edge_quality_score", 0) or 0
    )
    enhanced_clarity_score = float(
        enhanced_clarity.get("enhanced_clarity_score", 0) or 0
    )
    deception_state = str(
        deception_penalty.get("deception_penalty_state", "no_penalty") or "no_penalty"
    )
    memory_state = str(
        memory_adjustment.get("memory_adjustment_state", "neutral") or "neutral"
    )
    intent_state = str(
        intent_adjustment.get("intent_adjustment_state", "neutral") or "neutral"
    )

    reasons = []

    fused_score = (
        enhanced_edge_score * 0.55
        + enhanced_clarity_score * 0.25
        + base_score * 0.20
    )

    if deception_state == "severe_penalty":
        fused_score -= 15
        reasons.append("severe deception reduces final conviction")
    elif deception_state == "material_penalty":
        fused_score -= 8
        reasons.append("deception pressure reduces conviction")

    if memory_state == "strong_support":
        fused_score += 8
        reasons.append("memory support reinforces trust")
    elif memory_state == "punitive":
        fused_score -= 8
        reasons.append("memory weakness reduces trust")

    if intent_state == "supportive":
        fused_score += 5
        reasons.append("market intent supports conviction")
    elif intent_state == "hostile":
        fused_score -= 10
        reasons.append("market intent is hostile to conviction")

    if fused_score >= 75:
        state = "conviction"
    elif fused_score >= 52:
        state = "valid"
    elif fused_score >= 30:
        state = "weak"
    else:
        state = "reject"

    reasons.extend(base_soulaana.get("soulaana_reasons", []))

    return {
        "enhanced_soulaana_state": state,
        "enhanced_soulaana_score": round(fused_score, 2),
        "enhanced_soulaana_reasons": reasons,
    }
