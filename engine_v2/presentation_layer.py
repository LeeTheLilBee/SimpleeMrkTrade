from typing import Dict, List


def get_highlight_set(action: str, confidence: str, grade: str, tone: str) -> List[str]:
    # 🔥 upgraded branded highlight logic

    if action == "act" and confidence == "high":
        return [
            "High conviction alignment",
            "Clean execution window",
            "Top-tier opportunity",
        ]

    if action in ["act", "cautious_act"] and confidence in ["medium", "high"]:
        return [
            "Actionable but requires precision",
            "Structure is supportive",
            "Execution must be selective",
        ]

    if action == "wait":
        return [
            "Structure is not fully aligned",
            "Patience is the edge here",
            "Better expressions likely exist",
        ]

    return [
        "No actionable structure",
        "Capital should remain protected",
        "Stand aside",
    ]


def get_tone_message(state: str) -> str:
    tone_map = {
        "conviction": "This is a high-quality setup with strong alignment.",
        "valid": "This setup is workable, but requires control and precision.",
        "weak": "This setup lacks strength and should not be forced.",
        "reject": "This setup does not meet execution standards.",
    }

    return tone_map.get(state, "No clear signal detected.")
