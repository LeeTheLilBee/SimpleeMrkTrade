from typing import Dict


def build_enhanced_soulaana_voice(
    enhanced_state: Dict,
    deception_penalty: Dict,
    memory_adjustment: Dict,
    intent_adjustment: Dict,
) -> Dict:
    state = str(
        enhanced_state.get("enhanced_soulaana_state", "reject") or "reject"
    )
    score = float(
        enhanced_state.get("enhanced_soulaana_score", 0) or 0
    )
    deception_state = str(
        deception_penalty.get("deception_penalty_state", "no_penalty") or "no_penalty"
    )
    memory_state = str(
        memory_adjustment.get("memory_adjustment_state", "neutral") or "neutral"
    )
    intent_state = str(
        intent_adjustment.get("intent_adjustment_state", "neutral") or "neutral"
    )

    if deception_state == "severe_penalty":
        verdict = "This is lying."
        insight = "Visible strength is not earning trust."
        command = "Do not act."
        return {
            "enhanced_verdict": verdict,
            "enhanced_insight": insight,
            "enhanced_command_phrase": command,
        }

    if state == "conviction":
        if memory_state == "strong_support":
            verdict = "This holds."
            insight = "The setup is aligned, reinforced, and deserving of trust."
            command = "You can act."
        else:
            verdict = "This is real."
            insight = "The setup is strong enough to justify action."
            command = "You can act."

    elif state == "valid":
        if intent_state == "cautious":
            verdict = "This is workable."
            insight = "There is edge here, but the market still requires respect."
            command = "Proceed carefully."
        else:
            verdict = "This can work."
            insight = "The setup is usable, but not fully dominant."
            command = "Be selective."

    elif state == "weak":
        verdict = "This is fragile."
        insight = "The setup does not deserve normal conviction."
        command = "Size down or wait."

    else:
        verdict = "This does not hold."
        insight = "The trade loses trust after full adjustment."
        command = "Stand down."

    return {
        "enhanced_verdict": verdict,
        "enhanced_insight": insight,
        "enhanced_command_phrase": command,
    }
