def volume_surge(df):
    if df is None or df.empty or len(df) < 20:
        return False

    volume = float(df["Volume"].iloc[-1].item())
    avg_volume = float(df["Volume"].rolling(20).mean().iloc[-1].item())

    return volume > avg_volume * 1.5
