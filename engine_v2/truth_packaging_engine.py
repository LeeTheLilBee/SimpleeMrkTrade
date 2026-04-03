from typing import Dict


def build_truth_packaged_decision(
    enhanced_state: Dict,
    truth_override: Dict,
    fusion_adjustments: Dict,
    hard_rejection: Dict,
) -> Dict:
    return {
        "truth_summary": {
            "state": enhanced_state.get("enhanced_soulaana_state"),
            "score": enhanced_state.get("enhanced_soulaana_score"),
            "reasons": enhanced_state.get("enhanced_soulaana_reasons", []),
            "verdict": truth_override.get("truth_verdict"),
            "insight": truth_override.get("truth_insight"),
            "command": truth_override.get("truth_command_phrase"),
            "final_action": truth_override.get("truth_final_action"),
            "final_confidence": truth_override.get("truth_final_confidence"),
        },
        "truth_notes": {
            "override_reason": truth_override.get("truth_override_reason"),
            "hard_reject": hard_rejection.get("hard_reject", False),
            "hard_reject_reason": hard_rejection.get("hard_reject_reason"),
            "hard_reject_triggers": hard_rejection.get("hard_reject_triggers", []),
            "truth_snapshot": hard_rejection.get("truth_snapshot", {}),
            "deception_penalty": fusion_adjustments.get("deception_penalty", {}),
            "memory_adjustment": fusion_adjustments.get("memory_adjustment", {}),
            "intent_adjustment": fusion_adjustments.get("intent_adjustment", {}),
        },
    }
