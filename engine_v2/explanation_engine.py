from typing import Dict


def build_explanation(decision: Dict, execution: Dict, tier: str) -> Dict:
    state = decision.get("ready_state")

    if tier in {"Free", "Starter", "Guest"}:
        if state == "ready_now":
            text = "This one looks strong right now."
        elif state == "ready_soon":
            text = "Looks good, but not quite ready yet."
        elif state == "watch":
            text = "Worth watching for now."
        else:
            text = "Nothing to do here right now."
    else:
        if state == "ready_now":
            text = "Setup is clean with favorable timing and execution alignment."
        elif state == "ready_soon":
            text = "Setup is valid, but timing and entry still need refinement."
        elif state == "watch":
            text = "Structure is forming but not actionable yet."
        else:
            text = "Rejected due to insufficient edge or execution quality."

    return {
        "explanation": text
    }
