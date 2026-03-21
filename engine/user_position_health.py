"""
===========================================================
ENGINE
USER POSITION HEALTH
-----------------------------------------------------------
Stronger and more discriminating position health scoring.
===========================================================
"""

def build_user_position_health(portfolio):
    positions = portfolio.get("positions", [])
    enriched = []

    for p in positions:
        entry = float(p.get("entry", 0) or 0)
        current = float(p.get("current_price", entry) or entry)
        stop = float(p.get("stop", entry * 0.95) or (entry * 0.95))
        size = float(p.get("size", 1) or 1)

        pnl = (current - entry) * size if entry else 0

        if entry != stop:
            stop_distance_ratio = abs((current - stop) / (entry - stop))
        else:
            stop_distance_ratio = 1

        health_score = 100

        if pnl < 0:
            health_score -= 22

        if stop_distance_ratio < 0.35:
            health_score -= 35
        elif stop_distance_ratio < 0.75:
            health_score -= 18

        if entry > 0 and abs(current - entry) < (entry * 0.008):
            health_score -= 8

        if p.get("warning"):
            health_score -= 10

        if p.get("risk") in ["high", "HIGH", "elevated", "ELEVATED"]:
            health_score -= 12

        health_score = max(0, min(100, int(round(health_score))))

        if health_score >= 80:
            status = "Strong"
        elif health_score >= 60:
            status = "Healthy"
        elif health_score >= 40:
            status = "At Risk"
        else:
            status = "Weak"

        enriched.append({
            **p,
            "pnl": round(pnl, 2),
            "health_score": health_score,
            "status": status,
        })

    portfolio["positions"] = enriched
    return portfolio
