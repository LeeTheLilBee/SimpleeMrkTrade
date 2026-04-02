from typing import Dict


def evaluate_headline_risk(signal: Dict, context: Dict) -> Dict:
    news_heat = float(context.get("news_heat_score", 0) or 0)
    contradictory_news = bool(context.get("contradictory_news", False))
    hype_score = float(context.get("hype_score", 0) or 0)

    if contradictory_news and news_heat > 60:
        level = "high"
        reason = "headline environment is active and contradictory"
    elif news_heat > 75 or hype_score > 70:
        level = "medium"
        reason = "headline intensity may distort normal setup behavior"
    else:
        level = "low"
        reason = "headline flow is not strong enough to dominate the trade"

    return {
        "headline_risk_level": level,
        "headline_risk_reason": reason,
        "news_heat_score": round(news_heat, 2),
        "hype_score": round(hype_score, 2),
    }
