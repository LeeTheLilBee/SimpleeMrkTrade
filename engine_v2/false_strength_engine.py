from typing import Dict


def detect_false_strength(signal: Dict, context: Dict, regime: Dict) -> Dict:
    trend = float(signal.get("trend_strength", 0) or 0)
    extension = float(signal.get("extension_score", 0) or 0)
    volume = float(signal.get("volume_confirmation", 0) or 0)
    follow_through = float(context.get("follow_through_score", 0) or 0)
    breadth = float(regime.get("breadth_score", 0) or 0)

    score = 0

    if trend >= 65 and follow_through < 45:
        score += 35

    if extension >= 75 and volume < 45:
        score += 25

    if breadth < 45:
        score += 20

    if trend >= 70 and volume < 40:
        score += 20

    if score >= 70:
        state = "severe"
        reason = "visible strength is not supported by durable market quality"
    elif score >= 35:
        state = "present"
        reason = "setup looks strong, but support underneath is weaker than it appears"
    else:
        state = "absent"
        reason = "strength appears reasonably supported"

    return {
        "false_strength_state": state,
        "false_strength_score": score,
        "false_strength_reason": reason,
    }
