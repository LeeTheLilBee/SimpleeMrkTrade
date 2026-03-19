from datetime import datetime
from engine.paper_portfolio import show_positions
from engine.data_utils import safe_download
from engine.trailing_stop import trailing_stop
from engine.profit_lock import lock_profit

def _health_label(score):
    if score >= 80:
        return "STRONG", "badge-green"
    if score >= 60:
        return "HEALTHY", "badge-green"
    if score >= 40:
        return "WEAKENING", "badge-yellow"
    if score >= 25:
        return "AT RISK", "badge-red"
    return "EXIT SOON", "badge-red"

def _health_score(current, stop, target):
    if current is None or stop is None or target is None:
        return 0

    risk = abs(current - stop)
    reward = abs(target - current)

    if reward <= 0:
        return 20

    ratio = reward / (risk + 1e-6)

    score = int(min(max(ratio * 40, 10), 95))
    return score

def _age_minutes(ts):
    if not ts:
        return None
    try:
        return round((datetime.now() - datetime.fromisoformat(ts)).total_seconds() / 60, 1)
    except:
        return None

def monitor_open_positions():
    positions = show_positions()
    results = []

    for pos in positions:
        symbol = pos.get("symbol")
        strategy = pos.get("strategy", "CALL")
        entry = float(pos.get("price", 0) or 0)
        atr = float(pos.get("atr", 0) or 0)
        ts = pos.get("timestamp")

        df = safe_download(symbol, period="5d", auto_adjust=True, progress=False)

        if df is None or df.empty:
            results.append({
                "symbol": symbol,
                "status": "NO DATA"
            })
            continue

        current = float(df["Close"].iloc[-1].item())

        trail = trailing_stop(entry, current, atr)
        locked = lock_profit(entry, current)
        stop = locked if locked else trail

        if strategy == "CALL":
            target = entry * 1.1125
            pnl = current - entry
        else:
            target = entry * 0.8875
            pnl = entry - current

        score = _health_score(current, stop, target)
        health, badge = _health_label(score)

        # 🔥 SMART WARNINGS
        warning = None
        if score < 40:
            warning = "DEGRADING"
        elif pnl < 0 and abs(pnl) > atr:
            warning = "LOSING MOMENTUM"
        elif pnl > 0 and pnl < atr * 0.5:
            warning = "WEAK PROFIT"

        results.append({
            "symbol": symbol,
            "strategy": strategy,
            "entry": round(entry, 2),
            "current": round(current, 2),
            "pnl": round(pnl, 2),
            "stop": round(stop, 2),
            "target": round(target, 2),
            "health": health,
            "badge_class": badge,
            "health_score": score,
            "warning": warning,
            "age_minutes": _age_minutes(ts),
            "last_checked": datetime.now().isoformat()
        })

    return results
