from typing import Dict


def determine_next_action(decision: Dict, execution: Dict) -> Dict:
    state = decision.get("ready_state")
    entry = execution.get("entry_state")

    if state == "ready_now" and entry in {"clean", "acceptable"}:
        action = "act_now"
    elif state == "ready_soon":
        action = "prepare"
    elif state == "watch":
        action = "wait"
    else:
        action = "ignore"

    return {
        "next_action": action
    }
