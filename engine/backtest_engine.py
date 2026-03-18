from engine.data_utils import safe_download

def simple_backtest(symbol):
    df = safe_download(symbol, period="6mo", auto_adjust=True, progress=False)

    if df is None or df.empty or len(df) < 2:
        return {"symbol": symbol, "trades": 0, "wins": 0}

    start = float(df["Close"].iloc[0].item())
    end = float(df["Close"].iloc[-1].item())

    win = 1 if end > start else 0

    return {
        "symbol": symbol,
        "trades": 1,
        "wins": win
    }
