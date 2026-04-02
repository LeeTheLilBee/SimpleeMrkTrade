from typing import Dict


def build_threat_score(
    event_risk: Dict,
    headline_risk: Dict,
    fragility: Dict,
    false_calm: Dict,
    market_deception: Dict,
) -> Dict:
    score = 0

    score += {"low": 10, "medium": 30, "high": 55}.get(event_risk.get("event_risk_level", "low"), 0)
    score += {"low": 5, "medium": 20, "high": 40}.get(headline_risk.get("headline_risk_level", "low"), 0)
    score += {"stable": 5, "fragile": 25, "highly_fragile": 45}.get(fragility.get("fragility_state", "stable"), 0)
    score += {"absent": 0, "present": 20}.get(false_calm.get("false_calm_state", "absent"), 0)
    score += {"low": 5, "medium": 20, "high": 35}.get(market_deception.get("market_deception_level", "low"), 0)

    if score >= 130:
        level = "extreme"
    elif score >= 90:
        level = "high"
    elif score >= 45:
        level = "medium"
    else:
        level = "low"

    return {
        "threat_level": level,
        "threat_score": score,
    }
