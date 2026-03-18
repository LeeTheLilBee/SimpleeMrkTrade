def market_breadth(results):
    up = sum(1 for r in results if r["trend"] == "UPTREND")
    down = sum(1 for r in results if r["trend"] == "DOWNTREND")

    if up > down:
        return "BULLISH"
    if down > up:
        return "BEARISH"
    return "MIXED"
