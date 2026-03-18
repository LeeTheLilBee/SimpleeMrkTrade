from engine.data_utils import safe_download

def get_market_regime():
    spy = safe_download("SPY", period="6mo")

    if spy is None or spy.empty or len(spy) < 50:
        return "UNKNOWN"

    close = spy["Close"]

    ma50 = close.rolling(50).mean().iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]

    price = float(close.iloc[-1])
    ma50 = float(ma50)
    ma20 = float(ma20)

    if price > ma50 > ma20:
        return "BULL_TREND"

    if price < ma50:
        return "BEAR_TREND"

    return "NEUTRAL"
