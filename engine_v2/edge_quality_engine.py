from typing import Dict


def evaluate_edge_quality(
    decision: Dict,
    alignment: Dict,
    timeline: Dict,
    thesis: Dict,
    threat: Dict,
    decay: Dict,
) -> Dict:
    edge_score = float(decision.get("edge_score", 0) or 0)
    alignment_score = float(alignment.get("alignment_score", 0) or 0)
    timing_quality = float(timeline.get("timing_quality_score", 0) or 0)
    thesis_quality = str(
        thesis.get("thesis_quality", {}).get("thesis_quality", "weak") or "weak"
    )
    threat_level = str(threat.get("threat_score", {}).get("threat_level", "low") or "low")
    decay_state = str(decay.get("decay_state", "active") or "active")

    thesis_bonus = {
        "strong": 15,
        "moderate": 7,
        "weak": 0,
    }.get(thesis_quality, 0)

    threat_penalty = {
        "low": 0,
        "medium": -10,
        "high": -25,
        "extreme": -45,
    }.get(threat_level, 0)

    decay_penalty = {
        "durable": 0,
        "active": -5,
        "decaying": -20,
        "expired": -40,
    }.get(decay_state, 0)

    total = (
        edge_score * 0.35
        + alignment_score * 0.25
        + timing_quality * 0.20
        + thesis_bonus
        + threat_penalty
        + decay_penalty
    )

    if total >= 85:
        state = "elite"
    elif total >= 70:
        state = "strong"
    elif total >= 55:
        state = "usable"
    elif total >= 40:
        state = "marginal"
    else:
        state = "weak"

    return {
        "edge_quality_state": state,
        "edge_quality_score": round(total, 2),
    }
