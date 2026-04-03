from typing import Dict


def build_intent_conviction_adjustment(market_intent_intelligence: Dict) -> Dict:
    market_intent = market_intelligence = market_intent_intelligence.get("market_intent", {}) if isinstance(market_intent_intelligence, dict) else {}
    false_weakness = market_intent_intelligence.get("false_weakness", {}) if isinstance(market_intent_intelligence, dict) else {}

    intent_state = str(market_intent.get("intent_state", "unclear") or "unclear")
    false_weakness_state = str(false_weakness.get("false_weakness_state", "absent") or "absent")

    adjustment = 0
    reasons = []

    if intent_state == "continuation":
        adjustment += 15
        reasons.append("market intent supports real continuation")
    elif intent_state == "accumulation":
        adjustment += 10
        reasons.append("market intent suggests controlled building")
    elif intent_state == "expansion_attempt":
        adjustment -= 5
        reasons.append("market is trying to expand, but trust should remain measured")
    elif intent_state == "distribution":
        adjustment -= 18
        reasons.append("market intent suggests distribution under the surface")
    elif intent_state == "trap_attempt":
        adjustment -= 25
        reasons.append("market intent suggests trap behavior")
    else:
        adjustment -= 3
        reasons.append("market intent is not fully clear")

    if false_weakness_state == "present":
        adjustment += 4
        reasons.append("visible weakness may be overstating actual risk")
    elif false_weakness_state == "strong":
        adjustment += 8
        reasons.append("market may be hiding improving structure beneath apparent weakness")

    if adjustment >= 12:
        state = "supportive"
    elif adjustment > 0:
        state = "slightly_supportive"
    elif adjustment == 0:
        state = "neutral"
    elif adjustment > -15:
        state = "cautious"
    else:
        state = "hostile"

    return {
        "intent_adjustment_state": state,
        "intent_adjustment_score": adjustment,
        "intent_adjustment_reasons": reasons,
    }
