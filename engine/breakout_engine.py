def breakout(df):
    if df is None or df.empty or len(df) < 20:
        return False

    recent_high = float(df["High"].rolling(20).max().iloc[-2].item())
    price = float(df["Close"].iloc[-1].item())

    return price > recent_high
