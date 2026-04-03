from typing import Dict


def build_enhanced_clarity(
    clarity: Dict,
    deception_penalty: Dict,
    memory_adjustment: Dict,
    intent_adjustment: Dict,
) -> Dict:
    base_score = float(clarity.get("clarity_score", 0) or 0)

    deception_state = str(deception_penalty.get("deception_penalty_state", "no_penalty") or "no_penalty")
    memory_state = str(memory_adjustment.get("memory_adjustment_state", "neutral") or "neutral")
    intent_state = str(intent_adjustment.get("intent_adjustment_state", "neutral") or "neutral")

    adjustment = 0
    reasons = []

    if deception_state == "severe_penalty":
        adjustment -= 30
        reasons.append("severe deception sharply reduces clarity")
    elif deception_state == "material_penalty":
        adjustment -= 18
        reasons.append("deception pressure reduces clarity")
    elif deception_state == "light_penalty":
        adjustment -= 8
        reasons.append("minor deception pressure is present")

    if memory_state == "strong_support":
        adjustment += 10
        reasons.append("reinforced memory improves confidence in the read")
    elif memory_state == "supportive":
        adjustment += 5
        reasons.append("memory slightly supports clarity")
    elif memory_state == "punitive":
        adjustment -= 10
        reasons.append("memory weakens trust in the current read")

    if intent_state == "hostile":
        adjustment -= 10
        reasons.append("market intent is hostile to clean conviction")
    elif intent_state == "supportive":
        adjustment += 5
        reasons.append("market intent supports cleaner conviction")

    final_score = base_score + adjustment

    if final_score >= 75:
        state = "clear"
    elif final_score >= 55:
        state = "usable"
    elif final_score >= 35:
        state = "murky"
    else:
        state = "unclear"

    return {
        "base_clarity_score": round(base_score, 2),
        "enhanced_clarity_state": state,
        "enhanced_clarity_score": round(final_score, 2),
        "enhanced_clarity_reasons": reasons,
    }
