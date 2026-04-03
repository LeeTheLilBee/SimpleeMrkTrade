from typing import Dict


def evaluate_narrative_pressure(context: Dict, threat: Dict) -> Dict:
    news_heat = float(context.get("news_heat_score", 0) or 0)
    hype_score = float(context.get("hype_score", 0) or 0)
    contradictory_news = bool(context.get("contradictory_news", False))
    headline_risk = str(
        threat.get("headline_risk", {}).get("headline_risk_level", "low") or "low"
    )

    score = 0
    score += news_heat * 0.4
    score += hype_score * 0.35

    if contradictory_news:
        score += 20

    if headline_risk == "medium":
        score += 10
    elif headline_risk == "high":
        score += 20

    if score >= 85:
        state = "high"
        reason = "setup is under strong narrative pressure and may behave less cleanly"
    elif score >= 50:
        state = "medium"
        reason = "narrative participation is meaningful and may distort clean reads"
    else:
        state = "low"
        reason = "narrative pressure is not dominating the setup"

    return {
        "narrative_pressure_state": state,
        "narrative_pressure_score": round(score, 2),
        "narrative_pressure_reason": reason,
    }
