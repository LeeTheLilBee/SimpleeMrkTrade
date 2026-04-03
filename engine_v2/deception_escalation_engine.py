from typing import Dict


def build_deception_escalation(
    false_strength: Dict,
    false_weakness: Dict,
    follow_through_truth: Dict,
    market_intent: Dict,
    narrative_pressure: Dict,
) -> Dict:
    score = 0

    score += {
        "absent": 0,
        "present": 25,
        "severe": 45,
    }.get(false_strength.get("false_strength_state", "absent"), 0)

    score += {
        "absent": 0,
        "present": 5,
        "strong": 10,
    }.get(false_weakness.get("false_weakness_state", "absent"), 0)

    score += {
        "real": 0,
        "mixed": 15,
        "hollow": 35,
    }.get(follow_through_truth.get("follow_through_truth_state", "mixed"), 0)

    score += {
        "continuation": 0,
        "accumulation": 5,
        "expansion_attempt": 15,
        "distribution": 30,
        "trap_attempt": 40,
        "unclear": 10,
    }.get(market_intent.get("intent_state", "unclear"), 0)

    score += {
        "low": 0,
        "medium": 10,
        "high": 20,
    }.get(narrative_pressure.get("narrative_pressure_state", "low"), 0)

    if score >= 90:
        level = "severe"
        reason = "multiple deception signals are stacking and trust should be sharply reduced"
    elif score >= 60:
        level = "high"
        reason = "deception pressure is elevated and the setup should be treated cautiously"
    elif score >= 30:
        level = "moderate"
        reason = "some deception signals are present beneath the surface"
    else:
        level = "low"
        reason = "deception pressure is currently limited"

    return {
        "deception_level": level,
        "deception_score": score,
        "deception_reason": reason,
    }
