def generate_alerts(positions):
    alerts = []

    for p in positions:
        h = p["health"]

        if h["score"] < 50:
            alerts.append(f"{p['symbol']} is in critical condition")

        if h["degradation"] == "sharp":
            alerts.append(f"{p['symbol']} is breaking down rapidly")

        if "Stop proximity warning" in h["events"]:
            alerts.append(f"{p['symbol']} is approaching stop")

    return alerts
