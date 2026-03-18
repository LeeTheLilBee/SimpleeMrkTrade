def market_mode(regime, breadth):
    if regime == "HIGH_VOLATILITY":
        return "DEFENSIVE"
    if regime == "BULL_TREND" and breadth == "BULLISH":
        return "AGGRESSIVE_BULL"
    if regime == "BEAR_TREND" or breadth == "BEARISH":
        return "DEFENSIVE_BEAR"
    return "NEUTRAL"
