"""
SYSTEM BRAIN
Turns data into readable, decision-guiding narrative
"""

def build_system_brain(positions, portfolio, alerts):
    total = len(positions)
    weak = portfolio.get("weak_positions", 0)
    avg_health = portfolio.get("avg_health", 0)

    # ---------------------------
    # SYSTEM MOOD
    # ---------------------------
    if avg_health >= 75:
        mood = "confident"
    elif avg_health >= 55:
        mood = "balanced"
    else:
        mood = "defensive"

    # ---------------------------
    # PRIMARY FOCUS
    # ---------------------------
    focus_symbol = None

    if alerts:
        focus_symbol = alerts[0]["symbol"]

    # fallback if no alerts
    if not focus_symbol and positions:
        lowest = sorted(positions, key=lambda x: x["health"]["score"])[0]
        focus_symbol = lowest["symbol"]

    # ---------------------------
    # NARRATIVE
    # ---------------------------
    if mood == "confident":
        narrative = f"Portfolio is stable with strong structure across most positions. Only {weak} positions showing weakness."
    elif mood == "balanced":
        narrative = f"Portfolio
