from typing import Dict


def generate_coaching(user_state: Dict, decision: Dict) -> Dict:
    state = user_state.get("user_state")

    if state == "overtrading":
        msg = "Slow down. Focus on the best setup only."
    elif state == "hesitating":
        msg = "You have a valid setup. Trust the process."
    elif decision.get("ready_state") == "reject":
        msg = "Skip this one. It’s not worth it."
    else:
        msg = "Stay focused on quality over quantity."

    return {
        "coaching_message": msg
    }
