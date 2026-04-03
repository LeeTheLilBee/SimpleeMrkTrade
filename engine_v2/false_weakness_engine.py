from typing import Dict


def detect_false_weakness(signal: Dict, context: Dict, regime: Dict) -> Dict:
    trend = float(signal.get("trend_strength", 0) or 0)
    pullback_quality = float(signal.get("pullback_quality", 0) or 0)
    volume = float(signal.get("volume_confirmation", 0) or 0)
    follow_through = float(context.get("follow_through_score", 0) or 0)
    hidden_risk = float(context.get("hidden_risk_score", 0) or 0)

    score = 0

    if trend >= 55 and pullback_quality >= 65:
        score += 30

    if volume >= 55 and follow_through >= 55:
        score += 25

    if hidden_risk < 40:
        score += 15

    if trend >= 60 and volume < 50:
        score += 10

    if score >= 60:
        state = "strong"
        reason = "visible weakness may be hiding real structural improvement"
    elif score >= 35:
        state = "present"
        reason = "setup may look weaker than it actually is"
    else:
        state = "absent"
        reason = "visible weakness appears mostly real"

    return {
        "false_weakness_state": state,
        "false_weakness_score": score,
        "false_weakness_reason": reason,
    }
