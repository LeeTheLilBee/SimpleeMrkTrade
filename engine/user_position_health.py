"""
===========================================================
ENGINE CORE
POSITION HEALTH ENGINE (V2 - STRONGER)
===========================================================
"""

def build_user_position_health(portfolio):

    positions = portfolio.get("positions", [])
    enriched = []

    for p in positions:
        entry = float(p.get("entry", 0))
        current = float(p.get("current_price", entry))
        stop = float(p.get("stop", entry * 0.95))
        size = float(p.get("size", 1))

        pnl = (current - entry) * size

        # --- Distance to stop ---
        stop_distance = abs(current - stop) / max(abs(entry - stop), 1e-6)

        health = 100

        if pnl < 0:
            health -= 25

        if stop_distance < 0.5:
            health -= 35
        elif stop_distance < 1:
            health -= 15

        if abs(current - entry) < entry * 0.01:
            health -= 10

        health = max(0, min(100, health))

        if health > 75:
            status = "Strong"
        elif health > 50:
            status = "Healthy"
        elif health > 30:
            status = "At Risk"
        else:
            status = "Weak"

        enriched.append({
            **p,
            "pnl": round(pnl, 2),
            "health_score": health,
            "status": status
        })

    portfolio["positions"] = enriched
    return portfolio
