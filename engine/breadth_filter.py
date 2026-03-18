def breadth_allows_trade(strategy, breadth):
    if breadth == "BEARISH" and strategy == "CALL":
        return False
    if breadth == "BULLISH" and strategy == "PUT":
        return False
    return True
