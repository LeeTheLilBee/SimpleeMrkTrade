from typing import Dict


def evaluate_clarity(
    alignment: Dict,
    thesis: Dict,
    contradiction: Dict,
    threat: Dict,
    edge_quality: Dict,
) -> Dict:
    alignment_score = float(alignment.get("alignment_score", 0) or 0)
    thesis_quality = str(
        thesis.get("thesis_quality", {}).get("thesis_quality", "weak") or "weak"
    )
    contradiction_state = str(
        contradiction.get("contradiction_state", "none") or "none"
    )
    threat_level = str(threat.get("threat_score", {}).get("threat_level", "low") or "low")
    edge_quality_state = str(
        edge_quality.get("edge_quality_state", "weak") or "weak"
    )

    score = 0

    score += alignment_score * 0.5
    score += {"strong": 20, "moderate": 10, "weak": 0}.get(thesis_quality, 0)
    score += {"elite": 20, "strong": 15, "usable": 8, "marginal": 2, "weak": 0}.get(edge_quality_state, 0)
    score += {"none": 15, "light": 5, "meaningful": -10, "severe": -25}.get(contradiction_state, 0)
    score += {"low": 10, "medium": 0, "high": -10, "extreme": -20}.get(threat_level, 0)

    if score >= 75:
        state = "clear"
        reason = "trade reads cleanly across multiple layers"
    elif score >= 55:
        state = "usable"
        reason = "trade is readable, but not perfectly clean"
    elif score >= 35:
        state = "murky"
        reason = "trade contains enough ambiguity to reduce confidence"
    else:
        state = "unclear"
        reason = "trade does not currently read clearly enough"

    return {
        "clarity_state": state,
        "clarity_score": round(score, 2),
        "clarity_reason": reason,
    }
