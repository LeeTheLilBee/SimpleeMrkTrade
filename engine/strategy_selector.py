def choose_strategy(regime, trend):
    if regime == "BULL_TREND" and trend == "UPTREND":
        return "CALL"
    if regime == "BEAR_TREND" and trend == "DOWNTREND":
        return "PUT"
    if regime == "BULL_TREND" and trend == "DOWNTREND":
        return "PUT"
    if regime == "BEAR_TREND" and trend == "UPTREND":
        return "CALL"
    return "NO_TRADE"
