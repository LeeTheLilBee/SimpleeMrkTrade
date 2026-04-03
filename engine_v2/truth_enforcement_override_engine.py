from typing import Dict


def apply_truth_enforcement_override(
    enhanced_override: Dict,
    enhanced_voice: Dict,
    hard_rejection: Dict,
) -> Dict:
    final_action = str(enhanced_override.get("enhanced_final_action", "wait") or "wait")
    final_confidence = str(enhanced_override.get("enhanced_final_confidence", "low") or "low")
    override_reason = str(enhanced_override.get("enhanced_override_reason", "no override reason") or "no override reason")

    verdict = str(enhanced_voice.get("enhanced_verdict", "") or "")
    insight = str(enhanced_voice.get("enhanced_insight", "") or "")
    command = str(enhanced_voice.get("enhanced_command_phrase", "") or "")

    hard_reject = bool(hard_rejection.get("hard_reject", False))
    hard_reject_reason = str(hard_rejection.get("hard_reject_reason", "") or "")

    if hard_reject:
        final_action = "reject"
        final_confidence = "none"
        verdict = "This is lying."
        insight = "Truth enforcement rejects this setup after full adjustment."
        command = "Do not act."
        override_reason = hard_reject_reason

    return {
        "truth_final_action": final_action,
        "truth_final_confidence": final_confidence,
        "truth_verdict": verdict,
        "truth_insight": insight,
        "truth_command_phrase": command,
        "truth_override_reason": override_reason,
    }
