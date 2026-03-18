from engine.paper_portfolio import show_positions
from engine.data_utils import safe_download

def unrealized_pnl():
    positions = show_positions()

    total = 0
    details = []

    for pos in positions:
        symbol = pos["symbol"]
        entry = pos["price"]

        df = safe_download(symbol, period="5d", auto_adjust=True, progress=False)

        if df is None or df.empty:
            continue

        current = float(df["Close"].iloc[-1].item())

        if pos["strategy"] == "CALL":
            pnl = current - entry
        else:
            pnl = entry - current

        total += pnl

        details.append({
            "symbol": symbol,
            "entry": entry,
            "current": current,
            "pnl": round(pnl, 2)
        })

    return {
        "total_unrealized": round(total, 2),
        "positions": details
    }
