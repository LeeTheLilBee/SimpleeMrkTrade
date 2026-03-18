def momentum_strategy(trend, score, rsi):
    if trend == "UPTREND" and score >= 60 and rsi < 80:
        return "CALL"
    if trend == "DOWNTREND" and score >= 40 and rsi > 20:
        return "PUT"
    return "NO_TRADE"

def mean_reversion_strategy(trend, rsi):
    if trend == "DOWNTREND" and rsi <= 30:
        return "CALL"
    if trend == "UPTREND" and rsi >= 75:
        return "PUT"
    return "NO_TRADE"

def defensive_strategy(volatility_state, trend):
    if volatility_state == "HIGH_VOLATILITY":
        return "NO_TRADE"
    if trend == "UPTREND":
        return "CALL"
    if trend == "DOWNTREND":
        return "PUT"
    return "NO_TRADE"
