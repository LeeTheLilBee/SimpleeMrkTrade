def trend_strength(df):
    if df is None or df.empty or len(df) < 50:
        return 0

    close = df["Close"]
    sma20 = float(close.rolling(20).mean().iloc[-1].item())
    sma50 = float(close.rolling(50).mean().iloc[-1].item())
    price = float(close.iloc[-1].item())

    score = 0
    if price > sma20:
        score += 1
    if sma20 > sma50:
        score += 1
    return score
