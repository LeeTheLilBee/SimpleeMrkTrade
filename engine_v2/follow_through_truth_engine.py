from typing import Dict


def evaluate_follow_through_truth(signal: Dict, context: Dict) -> Dict:
    volume = float(signal.get("volume_confirmation", 0) or 0)
    trend = float(signal.get("trend_strength", 0) or 0)
    extension = float(signal.get("extension_score", 0) or 0)
    follow_through = float(context.get("follow_through_score", 0) or 0)

    score = 0

    score += follow_through * 0.5
    score += volume * 0.25
    score += trend * 0.15
    score += max(0, 100 - extension) * 0.10

    if score >= 65:
        state = "real"
        reason = "price movement is being converted into real continuation"
    elif score >= 45:
        state = "mixed"
        reason = "follow-through exists, but conversion quality is uneven"
    else:
        state = "hollow"
        reason = "movement is active, but not converting into trustworthy continuation"

    return {
        "follow_through_truth_state": state,
        "follow_through_truth_score": round(score, 2),
        "follow_through_truth_reason": reason,
    }
