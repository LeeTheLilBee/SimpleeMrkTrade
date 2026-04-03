from typing import Dict


def determine_counterfactual_trigger(trade: Dict) -> Dict:
    timing_quality = float(trade.get("timing_quality_score", 0) or 0)
    deception_level = str(trade.get("deception_level", "low") or "low")
    intent_state = str(trade.get("intent_state", "neutral") or "neutral")
    thesis_quality = str(trade.get("thesis_quality", "weak") or "weak")
    structure_quality = str(trade.get("contract_quality", "weak") or "weak")
    threat_level = str(trade.get("threat_level", "low") or "low")

    trigger = "unclear"
    reason = "no dominant missing condition identified"

    if deception_level in {"high", "severe"}:
        trigger = "deception"
        reason = "deception pressure was the dominant blocker"
    elif timing_quality < 55:
        trigger = "timing"
        reason = "timing quality was too weak"
    elif intent_state in {"trap_attempt", "distribution", "hostile"}:
        trigger = "intent"
        reason = "market intent was hostile to conviction"
    elif structure_quality in {"weak", "poor"}:
        trigger = "structure"
        reason = "trade structure quality was insufficient"
    elif thesis_quality == "weak":
        trigger = "thesis"
        reason = "the underlying thesis was not strong enough"
    elif threat_level in {"high", "extreme"}:
        trigger = "environment"
        reason = "environmental pressure was too elevated"

    return {
        "counterfactual_trigger": trigger,
        "counterfactual_trigger_reason": reason,
    }
