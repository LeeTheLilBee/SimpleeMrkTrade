from engine.breadth_filter import breadth_allows_trade

def trade_filter(score, trend, regime, breadth, strategy):
    if regime == "HIGH_VOLATILITY":
        return False

    if not breadth_allows_trade(strategy, breadth):
        return False

    if score < 40:
        return False

    if strategy == "CALL" and trend == "UPTREND" and score >= 60:
        return True

    if strategy == "PUT" and trend == "DOWNTREND" and score >= 40:
        return True

    return False
