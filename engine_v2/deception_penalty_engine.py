from typing import Dict


def build_deception_penalty(market_intent_intelligence: Dict) -> Dict:
    deception = market_intent_intelligence.get("deception", {}) if isinstance(market_intent_intelligence, dict) else {}
    false_strength = market_intent_intelligence.get("false_strength", {}) if isinstance(market_intent_intelligence, dict) else {}
    follow_truth = market_intent_intelligence.get("follow_through_truth", {}) if isinstance(market_intent_intelligence, dict) else {}
    market_intent = market_intent_intelligence.get("market_intent", {}) if isinstance(market_intent_intelligence, dict) else {}

    deception_level = str(deception.get("deception_level", "low") or "low")
    false_strength_state = str(false_strength.get("false_strength_state", "absent") or "absent")
    follow_truth_state = str(follow_truth.get("follow_through_truth_state", "mixed") or "mixed")
    intent_state = str(market_intent.get("intent_state", "unclear") or "unclear")

    penalty = 0
    reasons = []

    level_penalty = {
        "low": 0,
        "moderate": 10,
        "high": 25,
        "severe": 45,
    }.get(deception_level, 0)
    penalty += level_penalty
    if level_penalty:
        reasons.append(f"deception level is {deception_level}")

    fs_penalty = {
        "absent": 0,
        "present": 12,
        "severe": 25,
    }.get(false_strength_state, 0)
    penalty += fs_penalty
    if fs_penalty:
        reasons.append("false strength is present")

    ft_penalty = {
        "real": 0,
        "mixed": 8,
        "hollow": 20,
    }.get(follow_truth_state, 0)
    penalty += ft_penalty
    if ft_penalty:
        reasons.append(f"follow-through truth is {follow_truth_state}")

    if intent_state in {"trap_attempt", "distribution"}:
        penalty += 15
        reasons.append(f"market intent is {intent_state}")
    elif intent_state == "expansion_attempt":
        penalty += 8
        reasons.append("market is trying to expand without full confirmation")

    if penalty >= 70:
        state = "severe_penalty"
    elif penalty >= 35:
        state = "material_penalty"
    elif penalty > 0:
        state = "light_penalty"
    else:
        state = "no_penalty"

    return {
        "deception_penalty_state": state,
        "deception_penalty_score": penalty,
        "deception_penalty_reasons": reasons,
    }
