"""
SMART ALERT ENGINE
Ranks and classifies alerts with severity + priority
"""

def generate_alerts(positions):
    alerts = []

    for p in positions:
        h = p["health"]

        # ---------------------------
        # CRITICAL
        # ---------------------------
        if h["score"] < 40:
            alerts.append({
                "symbol": p["symbol"],
                "message": f"{p['symbol']} is in critical condition",
                "severity": "critical",
                "priority": 100,
                "type": "risk"
            })

        # ---------------------------
        # BREAKDOWN
        # ---------------------------
        if h["degradation"] == "sharp":
            alerts.append({
                "symbol": p["symbol"],
                "message": f"{p['symbol']} is breaking down rapidly",
                "severity": "high",
                "priority": 85,
                "type": "breakdown"
            })

        # ---------------------------
        # STOP RISK
        # ---------------------------
        if "Stop proximity warning" in h["events"]:
            alerts.append({
                "symbol": p["symbol"],
                "message": f"{p['symbol']} nearing stop level",
                "severity": "high",
                "priority": 80,
                "type": "risk"
            })

        # ---------------------------
        # EARLY WEAKNESS
        # ---------------------------
        if h["score"] < 60:
            alerts.append({
                "symbol": p["symbol"],
                "message": f"{p['symbol']} showing weakness",
                "severity": "medium",
                "priority": 60,
                "type": "warning"
            })

    # ---------------------------
    # SORT BY PRIORITY
    # ---------------------------
    alerts = sorted(alerts, key=lambda x: x["priority"], reverse=True)

    return alerts
