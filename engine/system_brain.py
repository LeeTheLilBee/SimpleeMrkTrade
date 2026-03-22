"""
SYSTEM BRAIN
Generates portfolio-level narration + attention focus
"""

def build_system_brain(positions, portfolio, alerts):
    if not positions:
        return {
            "summary": "No active positions.",
            "focus": None,
            "tone": "idle"
        }

    # ---------------------------
    # FIND MOST CRITICAL POSITION
    # ---------------------------
    most_critical = None
    lowest_health = 100

    for p in positions:
        h = p.get("health", {}).get("score", 100)
        if h < lowest_health:
            lowest_health = h
            most_critical = p

    # ---------------------------
    # PORTFOLIO STATE
    # ---------------------------
    avg = portfolio.get("avg_health", 0)
    weak = portfolio.get("weak_positions", 0)

    if avg >= 75:
        summary = "Portfolio structure is strong with stable positioning."
        tone = "confident"
    elif avg >= 55:
        summary = "Portfolio is stable but showing mixed strength."
        tone = "neutral"
    else:
        summary = f"Portfolio weakening with {weak} positions deteriorating."
        tone = "defensive"

    # ---------------------------
    # ALERT CONTEXT
    # ---------------------------
    if alerts:
        summary += f" {len(alerts)} active alerts require attention."

    # ---------------------------
    # FOCUS TARGET
    # ---------------------------
    if most_critical:
        focus = {
            "symbol": most_critical.get("symbol", "Unknown"),
            "message": f"{most_critical.get('symbol', 'This position')} requires immediate attention due to low health."
        }
    else:
        focus = None

    return {
        "summary": summary,
        "focus": focus,
        "tone": tone
    }
