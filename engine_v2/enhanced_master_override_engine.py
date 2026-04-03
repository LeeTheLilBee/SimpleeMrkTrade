from typing import Dict


def apply_enhanced_master_override(
    base_action: str,
    base_confidence: str,
    enhanced_state: Dict,
) -> Dict:
    state = str(
        enhanced_state.get("enhanced_soulaana_state", "reject") or "reject"
    )
    score = float(
        enhanced_state.get("enhanced_soulaana_score", 0) or 0
    )

    final_action = base_action
    final_confidence = base_confidence
    override_reason = "no enhanced override required"

    if state == "reject":
        final_action = "reject"
        final_confidence = "none"
        override_reason = "enhanced state rejected the trade"

    elif state == "weak":
        if base_action in {"act", "cautious_act"}:
            final_action = "wait"
        final_confidence = "low"
        override_reason = "enhanced state reduced conviction below action threshold"

    elif state == "valid":
        if base_action == "act":
            final_action = "cautious_act"
        if final_confidence == "high":
            final_confidence = "medium"
        override_reason = "enhanced state supports participation, but with less aggression"

    elif state == "conviction":
        if final_action == "wait" and score >= 80:
            final_action = "act"
            final_confidence = "high"
            override_reason = "enhanced state restored conviction strongly enough to act"

    return {
        "enhanced_final_action": final_action,
        "enhanced_final_confidence": final_confidence,
        "enhanced_override_reason": override_reason,
    }
