from typing import Dict


def build_final_coaching(
    behavior_intelligence: Dict,
    final_action_resolution: Dict,
    final_confidence_resolution: Dict,
) -> Dict:
    coaching = behavior_intelligence.get("coaching", {}) if isinstance(behavior_intelligence, dict) else {}
    behavior_override = behavior_intelligence.get("behavior_override", {}) if isinstance(behavior_intelligence, dict) else {}

    action = str(final_action_resolution.get("final_action", "wait") or "wait")
    confidence = str(final_confidence_resolution.get("final_confidence", "low") or "low")

    base_message = str(coaching.get("coaching_message", "Stay disciplined and follow the system.") or "Stay disciplined and follow the system.")
    base_tone = str(coaching.get("coaching_tone", "neutral") or "neutral")

    message = base_message
    tone = base_tone

    if action == "reject":
        message = "Do not press this. Protect capital and reset."
        tone = "warning"
    elif action == "wait":
        message = "Patience is still the edge. Let the setup improve."
        tone = "caution"
    elif action == "cautious_act":
        message = "There is a path here, but it requires precision and restraint."
        tone = "guided"
    elif action == "act" and confidence == "high":
        message = "This is actionable. Stay clean and execute with discipline."
        tone = "conviction"

    return {
        "final_coaching_message": message,
        "final_coaching_tone": tone,
        "behavior_override_applied": behavior_override.get("behavior_override", False),
    }
