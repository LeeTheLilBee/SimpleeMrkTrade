from typing import Dict
from engine_v2.presentation_layer import get_highlight_set, get_tone_message


def build_spotlight_presentation(card: Dict) -> Dict:
    action = card.get("action")
    confidence = card.get("confidence")
    grade = card.get("grade")
    tone = card.get("tone")

    card["highlights"] = get_highlight_set(action, confidence, grade, tone)
    card["message"] = get_tone_message(card.get("state"))

    return card
