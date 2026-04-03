from typing import Dict


def evaluate_capital_gatekeeper(
    edge_quality: Dict,
    clarity: Dict,
    contradiction: Dict,
    decay: Dict,
    threat: Dict,
) -> Dict:
    edge_state = str(edge_quality.get("edge_quality_state", "weak") or "weak")
    clarity_state = str(clarity.get("clarity_state", "unclear") or "unclear")
    contradiction_state = str(contradiction.get("contradiction_state", "none") or "none")
    decay_state = str(decay.get("decay_state", "active") or "active")
    threat_level = str(threat.get("threat_score", {}).get("threat_level", "low") or "low")

    if threat_level == "extreme" or decay_state == "expired" or contradiction_state == "severe":
        return {
            "capital_gate_state": "deny",
            "capital_gate_reason": "trade fails the minimum safety standard for capital",
        }

    if edge_state in {"elite", "strong"} and clarity_state in {"clear", "usable"} and threat_level == "low":
        return {
            "capital_gate_state": "allow",
            "capital_gate_reason": "trade deserves capital based on quality, clarity, and risk profile",
        }

    return {
        "capital_gate_state": "caution",
        "capital_gate_reason": "trade is not fully denied, but capital should remain selective",
    }
