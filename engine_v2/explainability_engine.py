def build_explanation(decision: dict) -> dict:
    summary = decision.get("summary", {})
    explanation = decision.get("explanation", {})

    state = summary.get("state", "neutral")
    reasons = explanation.get("why", [])

    tone_map = {
        "conviction": "This is a high-quality setup with strong alignment.",
        "valid": "This setup is workable, but requires awareness.",
        "weak": "This setup lacks strength and should be approached carefully.",
        "reject": "This setup does not meet execution standards."
    }

    base_message = tone_map.get(state, "No clear signal detected.")

    return {
        "state": state,
        "message": base_message,
        "reasons": reasons,
        "narrative": build_narrative(state, reasons)
    }


def build_narrative(state: str, reasons: list) -> str:
    if not reasons:
        return "No supporting factors were identified."

    reason_text = ", ".join(reasons)

    if state == "conviction":
        return f"All major layers are aligned. Key drivers: {reason_text}."
    elif state == "valid":
        return f"The setup has potential, supported by: {reason_text}."
    elif state == "weak":
        return f"The setup is fragile due to: {reason_text}."
    else:
        return f"The system rejected this setup due to: {reason_text}."
