from engine.paper_portfolio import show_positions
from engine.data_utils import safe_download
from engine.exit_review import review_exit
from engine.trailing_stop import trailing_stop
from engine.profit_lock import lock_profit
from engine.close_trade import close_position

def review_positions():
    positions = show_positions()

    print("OPEN POSITION REVIEW")
    if not positions:
        print("No open positions.")
        return

    for pos in positions:
        symbol = pos["symbol"]
        entry = pos["price"]
        atr = pos.get("atr", 0)

        df = safe_download(symbol, period="5d", auto_adjust=True, progress=False)
        if df is None or df.empty:
            print(symbol, "| No data")
            continue

        current = float(df["Close"].iloc[-1].item())

        trail = trailing_stop(entry, current, atr)
        locked = lock_profit(entry, current)
        stop_level = locked if locked is not None else trail
        target_level = entry * 1.10

        action = review_exit(current, stop_level, target_level)

        print(symbol, "| Current:", round(current, 2), "| Stop:", round(stop_level, 2), "| Action:", action)

        if action in ["STOP_LOSS", "TAKE_PROFIT"]:
            closed = close_position(symbol, current, action)
            if closed:
                print("CLOSED:", symbol, "| Reason:", action, "| PnL:", closed["pnl"])
