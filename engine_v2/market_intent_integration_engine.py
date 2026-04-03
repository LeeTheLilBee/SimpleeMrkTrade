from typing import Dict

from engine_v2.market_intent_engine import detect_market_intent
from engine_v2.false_strength_engine import detect_false_strength
from engine_v2.false_weakness_engine import detect_false_weakness
from engine_v2.follow_through_truth_engine import evaluate_follow_through_truth
from engine_v2.narrative_pressure_engine import evaluate_narrative_pressure
from engine_v2.deception_escalation_engine import build_deception_escalation


def build_market_intent_intelligence(
    signal: Dict,
    context: Dict,
    regime: Dict,
    threat: Dict,
) -> Dict:
    market_intent = detect_market_intent(signal=signal, context=context, regime=regime)
    false_strength = detect_false_strength(signal=signal, context=context, regime=regime)
    false_weakness = detect_false_weakness(signal=signal, context=context, regime=regime)
    follow_through_truth = evaluate_follow_through_truth(signal=signal, context=context)
    narrative_pressure = evaluate_narrative_pressure(context=context, threat=threat)

    deception = build_deception_escalation(
        false_strength=false_strength,
        false_weakness=false_weakness,
        follow_through_truth=follow_through_truth,
        market_intent=market_intent,
        narrative_pressure=narrative_pressure,
    )

    return {
        "market_intent": market_intent,
        "false_strength": false_strength,
        "false_weakness": false_weakness,
        "follow_through_truth": follow_through_truth,
        "narrative_pressure": narrative_pressure,
        "deception": deception,
    }
