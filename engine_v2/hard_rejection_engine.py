from typing import Dict


def evaluate_hard_rejection(
    enhanced_state: Dict,
    enhanced_voice: Dict,
    fusion_adjustments: Dict,
) -> Dict:
    state = str(enhanced_state.get("enhanced_soulaana_state", "reject") or "reject")
    score = float(enhanced_state.get("enhanced_soulaana_score", 0) or 0)
    verdict = str(enhanced_voice.get("enhanced_verdict", "") or "")

    deception = fusion_adjustments.get("deception_penalty", {}) if isinstance(fusion_adjustments, dict) else {}
    memory = fusion_adjustments.get("memory_adjustment", {}) if isinstance(fusion_adjustments, dict) else {}
    intent = fusion_adjustments.get("intent_adjustment", {}) if isinstance(fusion_adjustments, dict) else {}
    edge = fusion_adjustments.get("enhanced_edge_quality", {}) if isinstance(fusion_adjustments, dict) else {}

    deception_state = str(deception.get("deception_penalty_state", "no_penalty") or "no_penalty")
    deception_score = float(deception.get("deception_penalty_score", 0) or 0)
    memory_state = str(memory.get("memory_adjustment_state", "neutral") or "neutral")
    intent_state = str(intent.get("intent_adjustment_state", "neutral") or "neutral")
    enhanced_edge_state = str(edge.get("enhanced_edge_quality_state", "weak") or "weak")
    enhanced_edge_score = float(edge.get("enhanced_edge_quality_score", 0) or 0)

    hard_reject = False
    hard_reject_reason = "no hard rejection trigger fired"
    hard_reject_triggers = []

    if deception_state == "severe_penalty":
        hard_reject = True
        hard_reject_triggers.append("severe_deception")

    if deception_score >= 90 and enhanced_edge_score < 30:
        hard_reject = True
        hard_reject_triggers.append("deception_destroyed_edge")

    if verdict.strip().lower() == "this is lying.":
        hard_reject = True
        hard_reject_triggers.append("voice_truth_layer")

    if state == "reject":
        hard_reject = True
        hard_reject_triggers.append("enhanced_state_reject")

    if enhanced_edge_state == "weak" and deception_state == "severe_penalty" and intent_state in {"cautious", "hostile"}:
        hard_reject = True
        hard_reject_triggers.append("hostile_conviction_profile")

    if hard_reject:
        hard_reject_reason = "trade failed truth enforcement and should be rejected"

    return {
        "hard_reject": hard_reject,
        "hard_reject_reason": hard_reject_reason,
        "hard_reject_triggers": hard_reject_triggers,
        "truth_snapshot": {
            "enhanced_state": state,
            "enhanced_score": round(score, 2),
            "deception_state": deception_state,
            "deception_score": round(deception_score, 2),
            "memory_state": memory_state,
            "intent_state": intent_state,
            "enhanced_edge_state": enhanced_edge_state,
            "enhanced_edge_score": round(enhanced_edge_score, 2),
        },
    }
