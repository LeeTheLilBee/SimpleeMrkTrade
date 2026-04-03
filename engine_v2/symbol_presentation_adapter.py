from typing import Dict
from engine_v2.presentation_layer import get_highlight_set, get_tone_message


def build_symbol_presentation(context: Dict) -> Dict:
    action = context.get("hero_action")
    confidence = context.get("hero_confidence")
    grade = context.get("hero_grade")
    tone = context.get("hero_tone")

    context["highlights"] = get_highlight_set(action, confidence, grade, tone)
    context["message"] = get_tone_message(context.get("hero_state"))

    return context
