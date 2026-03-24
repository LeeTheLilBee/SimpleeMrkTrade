from datetime import datetime

from engine.paper_portfolio import show_positions, replace_position
from engine.close_trade import close_position
from engine.data_utils import safe_download
from engine.explainability_engine import explain_position_state


def _days_open(opened_at):
    try:
        dt = datetime.fromisoformat(opened_at)
        return (datetime.now() - dt).total_seconds() / 86400
    except Exception:
        return 0.0


def _progress(entry, current, target):
    if not entry or not target or target == entry:
        return 0.0
    return (current - entry) / (target - entry)


def _latest_price(symbol, fallback_price):
    df = safe_download(symbol, period="5d", auto_adjust=True, progress=False)
    if df is None or df.empty:
        return float(fallback_price or 0)

    try:
        close = df["Close"]
        if hasattr(close, "iloc"):
            val = close.iloc[-1]
            try:
                return float(val.item())
            except Exception:
                return float(val)
        return float(fallback_price or 0)
    except Exception:
        return float(fallback_price or 0)


def monitor_open_positions():
    positions = show_positions()
    actions = []

    for pos in positions:
        symbol = pos.get("symbol")
        entry = float(pos.get("entry", pos.get("price", 0)) or 0)
        current = _latest_price(symbol, pos.get("current_price", entry))
        target = float(pos.get("target", entry) or entry)
        stop = float(pos.get("stop", entry) or entry)
        score = float(pos.get("score", 0) or 0)
        prev_score = float(pos.get("previous_score", score) or score)
        opened_at = pos.get("opened_at")

        pos["current_price"] = round(current, 2)
        pos["position_explanation"] = explain_position_state(pos, current)
        replace_position(symbol, pos)

        days = _days_open(opened_at)
        prog = _progress(entry, current, target)

        action = "HOLD"

        if current <= stop:
            action = "STOP_LOSS"
        elif current >= target:
            action = "TAKE_PROFIT"
        elif days > 1 and prog < 0.2:
            action = "NO_FOLLOW_THROUGH"
        elif days > 2 and prog < 0.5:
            action = "TIME_EXIT"
        elif score < prev_score:
            action = "STRUCTURE_DETERIORATION"
        elif prog > 0.6 and current < (entry * 1.02):
            action = "PROFIT_PROTECT"

        print(f"{symbol} | Current: {round(current, 2)} | Stop: {round(stop, 2)} | Action: {action}")

        if action != "HOLD":
            result = close_position(symbol, current, reason=action.lower())
            actions.append({
                "symbol": symbol,
                "reason": action.lower(),
                "result": result,
            })
            if result.get("closed"):
                print(f"CLOSED: {symbol} | Reason: {action} | PnL: {result.get('pnl')}")
            elif result.get("blocked"):
                print(f"BLOCKED CLOSE: {symbol} | Reason: {result.get('reason')}")

    return actions
