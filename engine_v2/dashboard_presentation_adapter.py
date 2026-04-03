from typing import Dict


def build_dashboard_presentation(context: Dict) -> Dict:
    posture = context.get("posture", "wait")
    confidence = context.get("confidence", "low")
    grade = context.get("grade", "F")

    if posture == "act" and confidence == "high":
        message = "This is a high-quality setup with strong alignment."
    elif posture in {"act", "cautious_act"} and confidence in {"medium", "high"}:
        message = "The current lead setup is usable, but still requires precision."
    elif posture == "wait":
        message = "The board is active, but patience is still the edge."
    else:
        message = "Current conditions do not justify action."

    context["message"] = message
    return context
