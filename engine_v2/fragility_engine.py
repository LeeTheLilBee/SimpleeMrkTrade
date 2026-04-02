from typing import Dict


def evaluate_fragility(signal: Dict, decision: Dict, regime: Dict) -> Dict:
    trend = float(signal.get("trend_strength", 0) or 0)
    volume = float(signal.get("volume_confirmation", 0) or 0)
    breadth = float(regime.get("breadth_score", 0) or 0)
    ready_state = str(decision.get("ready_state", "watch") or "watch")

    score = 0

    if trend < 50:
        score += 30
    if volume < 50:
        score += 30
    if breadth < 45:
        score += 20
    if ready_state == "ready_now" and volume < 40:
        score += 20

    if score >= 70:
        state = "highly_fragile"
        reason = "setup looks active, but support underneath is unstable"
    elif score >= 40:
        state = "fragile"
        reason = "setup has visible weakness beneath surface strength"
    else:
        state = "stable"
        reason = "structure support appears durable enough"

    return {
        "fragility_state": state,
        "fragility_score": score,
        "fragility_reason": reason,
    }
