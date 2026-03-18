from engine.universe import get_universe
from engine.data_utils import safe_download

def build_rotating_watchlist(limit=20):
    scored = []

    for symbol in get_universe():
        df = safe_download(symbol, period="1mo", auto_adjust=True, progress=False)

        if df is None or df.empty or len(df) < 10:
            continue

        try:
            last_close = float(df["Close"].iloc[-1].item())
            first_close = float(df["Close"].iloc[0].item())
            avg_volume = float(df["Volume"].rolling(10).mean().iloc[-1].item())
        except Exception:
            continue

        momentum = (last_close - first_close) / first_close
        scored.append((symbol, momentum, avg_volume))

    scored = sorted(scored, key=lambda x: (x[1], x[2]), reverse=True)
    return [x[0] for x in scored[:limit]]
