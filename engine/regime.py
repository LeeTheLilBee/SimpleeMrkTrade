from engine.data_utils import safe_download

def _to_float(x):
    try:
        return float(x.item())
    except Exception:
        return float(x)

def get_market_regime():
    spy = safe_download("SPY", period="6mo", auto_adjust=True, progress=False)

    if spy is None or spy.empty or len(spy) < 50:
        return "UNKNOWN"

    close = spy["Close"]
    ma50_series = close.rolling(50).mean()
    ma20_series = close.rolling(20).mean()

    price = _to_float(close.iloc[-1])
    ma50 = _to_float(ma50_series.iloc[-1])
    ma20 = _to_float(ma20_series.iloc[-1])

    if price > ma50 > ma20:
        return "BULL_TREND"
    if price < ma50:
        return "BEAR_TREND"
    return "NEUTRAL"
