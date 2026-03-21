
def explain_signal(score, confidence, trend=None, volatility=None, regime=None):
    explanation = []

    # Score meaning
    if score >= 200:
        explanation.append("Extremely strong setup with multiple aligned factors.")
    elif score >= 150:
        explanation.append("Strong setup with multiple confirmations.")
    elif score >= 100:
        explanation.append("Developing setup with partial alignment.")
    else:
        explanation.append("Weak or early-stage setup.")

    # Confidence meaning
    if confidence == "HIGH":
        explanation.append("High conviction based on strong confirmation signals.")
    elif confidence == "MEDIUM":
        explanation.append("Moderate conviction; setup is valid but not fully confirmed.")
    else:
        explanation.append("Low conviction; requires caution.")

    # Context
    if volatility == "ELEVATED":
        explanation.append("Volatility is elevated — expect faster moves and risk.")
    if regime:
        explanation.append(f"Market regime: {regime.replace('_', ' ').title()}.")

    return explanation
