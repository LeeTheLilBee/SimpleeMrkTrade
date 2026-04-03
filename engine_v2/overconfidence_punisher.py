from typing import Dict


def evaluate_overconfidence(
    edge_quality: Dict,
    clarity: Dict,
    contradiction: Dict,
    threat: Dict,
) -> Dict:
    edge_state = str(edge_quality.get("edge_quality_state", "weak"))
    clarity_state = str(clarity.get("clarity_state", "unclear"))
    contradiction_state = str(contradiction.get("contradiction_state", "none"))
    threat_level = str(threat.get("threat_score", {}).get("threat_level", "low"))

    penalty = 0
    reasons = []

    if edge_state in {"elite", "strong"}:
        if clarity_state in {"murky", "unclear"}:
            penalty += 25
            reasons.append("strong edge without clarity")

        if contradiction_state in {"meaningful", "severe"}:
            penalty += 35
            reasons.append("strong edge with internal conflict")

        if threat_level in {"high", "extreme"}:
            penalty += 20
            reasons.append("strong edge under elevated threat")

    state = "clean"
    if penalty >= 50:
        state = "dangerous"
    elif penalty >= 25:
        state = "inflated"

    return {
        "overconfidence_state": state,
        "overconfidence_penalty": penalty,
        "overconfidence_reasons": reasons,
    }
