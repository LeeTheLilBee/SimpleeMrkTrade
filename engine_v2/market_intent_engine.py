from typing import Dict


def detect_market_intent(signal: Dict, context: Dict, regime: Dict) -> Dict:
    trend = float(signal.get("trend_strength", 0) or 0)
    volume = float(signal.get("volume_confirmation", 0) or 0)
    extension = float(signal.get("extension_score", 0) or 0)
    pullback_quality = float(signal.get("pullback_quality", 0) or 0)
    follow_through = float(context.get("follow_through_score", 0) or 0)
    hidden_risk = float(context.get("hidden_risk_score", 0) or 0)
    breadth = float(regime.get("breadth_score", 0) or 0)

    intent_state = "unclear"
    intent_reason = "market intent is not yet readable"

    if trend >= 70 and volume >= 60 and follow_through >= 60 and extension < 75:
        intent_state = "continuation"
        intent_reason = "trend, participation, and follow-through suggest real continuation"

    elif trend >= 55 and pullback_quality >= 60 and extension < 55:
        intent_state = "accumulation"
        intent_reason = "structure suggests controlled building rather than impulsive exhaustion"

    elif trend >= 60 and extension >= 75 and follow_through < 45:
        intent_state = "expansion_attempt"
        intent_reason = "market is trying to expand, but follow-through is not fully confirming"

    elif hidden_risk >= 65 and breadth < 45 and follow_through < 45:
        intent_state = "distribution"
        intent_reason = "surface activity appears active, but underlying support is deteriorating"

    elif extension >= 70 and volume < 45 and follow_through < 40:
        intent_state = "trap_attempt"
        intent_reason = "move is extended without enough support, suggesting possible trap behavior"

    return {
        "intent_state": intent_state,
        "intent_reason": intent_reason,
    }
