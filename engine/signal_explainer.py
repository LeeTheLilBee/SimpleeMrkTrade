def explain_signal(score_or_trade, confidence=None, trend=None, volatility=None, regime=None):
    """
    Backward-compatible signal explainer.

    Supports:
    - explain_signal(trade_dict)
    - explain_signal(score, confidence, trend=None, volatility=None, regime=None)
    """

    if isinstance(score_or_trade, dict):
        trade = score_or_trade
        score = trade.get("score", 0)
        confidence = trade.get("confidence", "LOW")
        trend = trade.get("trend", trend)
        volatility = trade.get("volatility_state", trade.get("volatility", volatility))
        regime = trade.get("regime", regime)
    else:
        score = score_or_trade

    explanation = []

    if score >= 200:
        explanation.append("Extremely strong setup with multiple aligned factors.")
    elif score >= 150:
        explanation.append("Strong setup with multiple confirmations.")
    elif score >= 100:
        explanation.append("Developing setup with partial alignment.")
    else:
        explanation.append("Weak or early-stage setup.")

    if confidence == "HIGH":
        explanation.append("High conviction based on strong confirmation signals.")
    elif confidence == "MEDIUM":
        explanation.append("Moderate conviction; setup is valid but not fully confirmed.")
    else:
        explanation.append("Low conviction; requires caution.")

    if volatility and str(volatility).upper() == "ELEVATED":
        explanation.append("Volatility is elevated — expect faster moves and risk.")

    if regime:
        explanation.append(f"Market regime: {str(regime).replace('_', ' ').title()}.")

    if trend:
        explanation.append(f"Trend context: {str(trend).replace('_', ' ').title()}.")

    return explanation
