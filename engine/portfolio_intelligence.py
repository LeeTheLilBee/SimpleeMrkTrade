def evaluate_portfolio(positions):
    total = len(positions)

    if total == 0:
        return {
            "health": "No positions",
            "risk": "None",
            "concentration": "None"
        }

    avg_health = sum(p["health"]["score"] for p in positions) / total

    deteriorating = [p for p in positions if p["health"]["direction"] == "deteriorating"]

    if avg_health >= 75:
        health = "Strong portfolio structure"
    elif avg_health >= 55:
        health = "Moderate structure"
    else:
        health = "Weak / deteriorating portfolio"

    if len(deteriorating) > total * 0.5:
        risk = "High degradation risk"
    elif len(deteriorating) > 0:
        risk = "Some positions weakening"
    else:
        risk = "Stable"

    return {
        "avg_health": int(avg_health),
        "health": health,
        "risk": risk,
        "weak_positions": len(deteriorating)
    }
