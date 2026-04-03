from typing import Dict


def detect_emotional_bias(user_state: Dict, decision: Dict) -> Dict:
    confidence = str(decision.get("confidence", "low") or "low")
    score = float(decision.get("score", 0) or 0)

    recent_losses = int(user_state.get("recent_losses", 0) or 0)
    recent_wins = int(user_state.get("recent_wins", 0) or 0)
    streak = str(user_state.get("streak_type", "none") or "none")

    bias = "none"
    reason = "no emotional distortion detected"

    if recent_losses >= 2 and confidence == "low":
        bias = "revenge_trading_risk"
        reason = "recent losses may push forced trades"
    elif recent_wins >= 3 and score > 80:
        bias = "overconfidence_risk"
        reason = "strong recent performance may reduce caution"
    elif confidence == "low" and score > 70:
        bias = "hesitation_conflict"
        reason = "system sees opportunity but user may hesitate"
    elif score < 40 and confidence != "none":
        bias = "forcing_trades"
        reason = "user may act despite weak setup"

    return {
        "emotional_bias": bias,
        "emotional_bias_reason": reason,
    }
