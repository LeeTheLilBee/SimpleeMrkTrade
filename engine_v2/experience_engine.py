from typing import Dict

from engine_v2.explanation_engine import build_explanation
from engine_v2.next_action_engine import determine_next_action
from engine_v2.user_state_engine import detect_user_state
from engine_v2.coaching_engine import generate_coaching


def build_experience(signal: Dict, decision: Dict, execution: Dict, user_data: Dict, tier: str) -> Dict:
    explanation = build_explanation(decision, execution, tier)
    action = determine_next_action(decision, execution)
    user_state = detect_user_state(user_data)
    coaching = generate_coaching(user_state, decision)

    return {
        **explanation,
        **action,
        **user_state,
        **coaching,
    }
