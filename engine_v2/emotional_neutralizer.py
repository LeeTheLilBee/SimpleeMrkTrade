from typing import Dict


def evaluate_emotional_bias(
    signal: Dict,
    edge_quality: Dict,
) -> Dict:
    hype_score = float(signal.get("hype_score", 0) or 0)
    edge_state = str(edge_quality.get("edge_quality_state", "weak"))

    bias_detected = False
    reason = "no emotional distortion detected"

    if hype_score > 70 and edge_state not in {"elite", "strong"}:
        bias_detected = True
        reason = "high excitement without strong edge"

    return {
        "emotional_bias_detected": bias_detected,
        "emotional_bias_reason": reason,
    }
