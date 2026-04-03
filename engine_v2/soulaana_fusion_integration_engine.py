from typing import Dict

from engine_v2.deception_penalty_engine import build_deception_penalty
from engine_v2.memory_trust_adjustment_engine import build_memory_trust_adjustment
from engine_v2.intent_conviction_adjustment_engine import build_intent_conviction_adjustment
from engine_v2.enhanced_edge_quality_engine import build_enhanced_edge_quality
from engine_v2.enhanced_clarity_engine import build_enhanced_clarity


def build_soulaana_fusion_adjustments(
    edge_quality: Dict,
    clarity: Dict,
    market_intent_intelligence: Dict,
    memory_intelligence: Dict,
) -> Dict:
    deception_penalty = build_deception_penalty(market_intent_intelligence)
    memory_adjustment = build_memory_trust_adjustment(memory_intelligence)
    intent_adjustment = build_intent_conviction_adjustment(market_intent_intelligence)

    enhanced_edge_quality = build_enhanced_edge_quality(
        edge_quality=edge_quality,
        deception_penalty=deception_penalty,
        memory_adjustment=memory_adjustment,
        intent_adjustment=intent_adjustment,
    )

    enhanced_clarity = build_enhanced_clarity(
        clarity=clarity,
        deception_penalty=deception_penalty,
        memory_adjustment=memory_adjustment,
        intent_adjustment=intent_adjustment,
    )

    return {
        "deception_penalty": deception_penalty,
        "memory_adjustment": memory_adjustment,
        "intent_adjustment": intent_adjustment,
        "enhanced_edge_quality": enhanced_edge_quality,
        "enhanced_clarity": enhanced_clarity,
    }
