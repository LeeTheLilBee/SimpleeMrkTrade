"""
===========================================================
SYSTEM VOICE ENGINE
-----------------------------------------------------------
Creates a calm, intelligent narrative about the portfolio.
===========================================================
"""

def generate_system_voice(portfolio, alerts, positions):
    total = len(positions)

    if total == 0:
        return {
            "headline": "No active positions",
            "message": "There are currently no trades to evaluate.",
            "focus": None
        }

    # ---------------------------
    # HEADLINE
    # ---------------------------
    headline = portfolio.get("health", "Unknown condition")

    # ---------------------------
    # CORE MESSAGE
    # ---------------------------
    weak = portfolio.get("weak_positions", 0)
    avg = portfolio.get("avg_health", 0)

    if avg >= 75:
        tone = "Portfolio structure is strong."
    elif avg >= 55:
        tone = "Portfolio is stable but requires monitoring."
    else:
        tone = "Portfolio is weakening and needs attention."

    if weak > 0:
        detail = f"{weak} position(s) are showing deterioration."
    else:
        detail = "No significant structural breakdown detected."

    message = f"{tone} {detail}"

    # ---------------------------
    # FOCUS TARGET
    # ---------------------------
    focus = None

    if alerts:
        # highest priority alert
        focus = alerts[0]["symbol"]

    return {
        "headline": headline,
        "message": message,
        "focus": focus
    }
