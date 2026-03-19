def explain_signal(trade):
    explanations = []

    score = trade.get("score", 0)

    if score >= 200:
        explanations.append("Extremely high conviction setup")
    elif score >= 150:
        explanations.append("Strong alignment across multiple factors")
    elif score >= 100:
        explanations.append("Moderate quality setup with supportive structure")

    if trade.get("confidence") == "HIGH":
        explanations.append("High confidence signal confirmation")

    if trade.get("strategy") == "CALL":
        explanations.append("Bullish directional bias")
    elif trade.get("strategy") == "PUT":
        explanations.append("Bearish directional bias")

    return explanations
