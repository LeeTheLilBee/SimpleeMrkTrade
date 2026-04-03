from typing import Dict


def build_enhanced_decision_package(
    enhanced_state: Dict,
    enhanced_voice: Dict,
    override: Dict,
    fusion_adjustments: Dict,
) -> Dict:
    return {
        "enhanced_summary": {
            "state": enhanced_state.get("enhanced_soulaana_state"),
            "score": enhanced_state.get("enhanced_soulaana_score"),
            "reasons": enhanced_state.get("enhanced_soulaana_reasons", []),
            "verdict": enhanced_voice.get("enhanced_verdict"),
            "insight": enhanced_voice.get("enhanced_insight"),
            "command": enhanced_voice.get("enhanced_command_phrase"),
            "final_action": override.get("enhanced_final_action"),
            "final_confidence": override.get("enhanced_final_confidence"),
        },
        "enhanced_notes": {
            "override_reason": override.get("enhanced_override_reason"),
            "deception_penalty": fusion_adjustments.get("deception_penalty", {}),
            "memory_adjustment": fusion_adjustments.get("memory_adjustment", {}),
            "intent_adjustment": fusion_adjustments.get("intent_adjustment", {}),
        },
    }
