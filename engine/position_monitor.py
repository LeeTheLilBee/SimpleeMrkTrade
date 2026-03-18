from datetime import datetime
from engine.paper_portfolio import show_positions
from engine.data_utils import safe_download
from engine.trailing_stop import trailing_stop
from engine.profit_lock import lock_profit
from engine.exit_review import review_exit

def _health_label(current, stop_level, target_level):
    if current <= stop_level:
        return "EXIT NOW"
    if current >= target_level:
        return "TARGET HIT"

    stop_gap = current - stop_level
    target_gap = target_level - current

    if stop_gap <= max(current * 0.01, 0.25):
        return "NEAR STOP"
    if target_gap <= max(current * 0.02, 0.25):
        return "NEAR TARGET"
    return "SAFE"

def monitor_open_positions():
    positions = show_positions()
    results = []

    for pos in positions:
        symbol = pos["symbol"]
        strategy = pos["strategy"]
        entry = float(pos["price"])
        atr = float(pos.get("atr", 0) or 0)

        df = safe_download(symbol, period="5d", auto_adjust=True, progress=False)
        if df is None or df.empty:
            results.append({
                "symbol": symbol,
                "strategy": strategy,
                "entry": round(entry, 2),
                "current": None,
                "stop": None,
                "target": None,
                "action": "NO DATA",
                "health": "UNKNOWN",
                "stop_distance": None,
                "target_distance": None,
                "last_checked": datetime.now().isoformat()
            })
            continue

        current = float(df["Close"].iloc[-1].item())

        trail = trailing_stop(entry, current, atr)
        locked = lock_profit(entry, current)
        stop_level = locked if locked is not None else trail
        target_level = entry * 1.1125 if strategy == "CALL" else entry * 0.8875

        action = review_exit(current, stop_level, target_level)
        health = _health_label(current, stop_level, target_level)

        if strategy == "CALL":
            stop_distance = current - stop_level
            target_distance = target_level - current
            pnl = current - entry
        else:
            stop_distance = stop_level - current
            target_distance = current - target_level
            pnl = entry - current

        results.append({
            "symbol": symbol,
            "strategy": strategy,
            "entry": round(entry, 2),
            "current": round(current, 2),
            "stop": round(stop_level, 2),
            "target": round(target_level, 2),
            "action": action,
            "health": health,
            "pnl": round(pnl, 2),
            "stop_distance": round(stop_distance, 2),
            "target_distance": round(target_distance, 2),
            "last_checked": datetime.now().isoformat()
        })

    return results
