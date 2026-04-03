from typing import Dict

from engine_v2.emotional_bias_engine import detect_emotional_bias
from engine_v2.behavior_pattern_engine import detect_behavior_pattern
from engine_v2.risk_discipline_engine import evaluate_risk_discipline
from engine_v2.coaching_engine import generate_coaching
from engine_v2.behavior_override_engine import apply_behavior_override


def build_behavior_intelligence(decision: Dict, user_state: Dict) -> Dict:
    emotional = detect_emotional_bias(user_state, decision)
    behavior = detect_behavior_pattern(user_state)
    discipline = evaluate_risk_discipline(decision, user_state)
    coaching = generate_coaching(emotional, behavior, discipline)
    override = apply_behavior_override(decision, emotional, behavior, discipline)

    return {
        "emotional_bias": emotional,
        "behavior_pattern": behavior,
        "risk_discipline": discipline,
        "coaching": coaching,
        "behavior_override": override,
    }
