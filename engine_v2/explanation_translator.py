def translate_decision(decision: dict, tier: str) -> str:
    state = decision.get("ready_state")

    if tier in ["Free", "Starter", "Guest"]:
        if state == "ready_now":
            return "This one looks strong right now."
        if state == "ready_soon":
            return "Looks good, but not quite ready yet."
        if state == "watch":
            return "Worth watching for now."
        return "Nothing to do here right now."

    if tier in ["Pro", "Elite"]:
        if state == "ready_now":
            return "Setup is clean with favorable timing."
        if state == "ready_soon":
            return "Setup is valid, but timing still needs refinement."
        if state == "watch":
            return "Structure is forming but not actionable yet."
        return "Rejected due to weak edge or poor timing."

    return ""
