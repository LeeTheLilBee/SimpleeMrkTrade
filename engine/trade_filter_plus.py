def advanced_trade_filter(score, confidence, volatility_state, strategy):
    if strategy == "NO_TRADE":
        return False
    if volatility_state == "HIGH_VOLATILITY" and confidence not in ["HIGH", "ELITE"]:
        return False
    if score < 40:
        return False
    if confidence == "NONE":
        return False
    return True
