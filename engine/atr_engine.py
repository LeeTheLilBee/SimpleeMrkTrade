import pandas as pd

def calculate_atr(df, period=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    high_low = high - low
    high_close = (high - close.shift()).abs()
    low_close = (low - close.shift()).abs()

    tr = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = tr.max(axis=1)
    atr = true_range.rolling(period).mean()

    val = atr.iloc[-1]
    return float(val.item()) if hasattr(val, "item") else float(val)
