from typing import Dict


def enforce_contradictions(
    contradiction: Dict,
) -> Dict:
    state = str(contradiction.get("contradiction_state", "none"))

    penalty = 0
    action = "none"

    if state == "light":
        penalty = 5
        action = "monitor"
    elif state == "meaningful":
        penalty = 20
        action = "restrict"
    elif state == "severe":
        penalty = 50
        action = "block"

    return {
        "contradiction_penalty": penalty,
        "contradiction_action": action,
    }
