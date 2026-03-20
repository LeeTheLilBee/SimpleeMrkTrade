def _health_label(score):
    if score >= 80:
        return "Strong"
    if score >= 65:
        return "Healthy"
    if score >= 45:
        return "At Risk"
    return "Weak"

def _score_position(position):
    pnl = float(position.get("pnl", 0) or 0)
    distance_to_stop = float(position.get("distance_to_stop_pct", 8) or 0)
    trend_alignment = float(position.get("trend_alignment", 1) or 0)  # 1 good, 0 neutral, -1 bad
    conviction = float(position.get("conviction", 60) or 60)

    score = 55

    score += min(20, max(-20, pnl * 2))
    score += min(15, max(-15, distance_to_stop))
    score += 10 if trend_alignment > 0 else (-10 if trend_alignment < 0 else 0)
    score += min(15, max(-5, (conviction - 50) / 2))

    score = max(0, min(100, round(score)))
    return score

def build_user_position_health(portfolio):
    positions = portfolio.get("positions", [])
    enriched = []

    for p in positions:
        score = _score_position(p)
        label = _health_label(score)

        enriched.append({
            **p,
            "health_score": score,
            "health_label": label,
        })

    portfolio_health = round(
        sum([p["health_score"] for p in enriched]) / len(enriched), 2
    ) if enriched else 0

    return {
        "broker": portfolio.get("broker"),
        "linked": portfolio.get("linked", False),
        "cash": portfolio.get("cash", 0),
        "buying_power": portfolio.get("buying_power", 0),
        "notes": portfolio.get("notes", ""),
        "positions": enriched,
        "portfolio_health": portfolio_health,
    }
