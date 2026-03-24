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


def _health_label(score):
    if score >= 85:
        return "STRONG"
    if score >= 65:
        return "HEALTHY"
    if score >= 45:
        return "CAUTION"
    return "DANGER"


def _risk_state(current, stop, entry, target):
    if current <= stop:
        return "STOP_BREACH"
    if current >= target:
        return "TARGET_REACHED"
    if current < entry:
        return "UNDER_PRESSURE"
    return "NORMAL"


def _build_health_score(entry, current, stop, target, score, prev_score, days_open):
    health = 50

    if current > entry:
        health += 15
    elif current < entry:
        health -= 10

    if current > stop:
        health += 10
    else:
        health -= 35

    if target > entry:
        progress = (current - entry) / max((target - entry), 0.01)
    else:
        progress = 0.0

    if progress >= 0.75:
        health += 20
    elif progress >= 0.40:
        health += 10
    elif progress < 0:
        health -= 10

    if score > prev_score:
        health += 10
    elif score < prev_score:
        health -= 12

    if days_open > 2 and progress < 0.25:
        health -= 12
    elif days_open > 1 and progress < 0.15:
        health -= 8

    return max(0, min(100, int(round(health))))


def _action_bias(current, stop, target, score, prev_score, days_open, progress):
    if current <= stop:
        return "EXIT_NOW"
    if current >= target:
        return "TAKE_PROFIT"
    if days_open > 2 and progress < 0.5:
        return "TRIM_OR_EXIT"
    if days_open > 1 and progress < 0.2:
        return "REDUCE_RISK"
    if score < prev_score:
        return "TIGHTEN_UP"
    if progress > 0.6:
        return "PROTECT_PROFIT"
    return "HOLD"


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

        days = _days_open(opened_at)
        prog = _progress(entry, current, target)
        health_score = _build_health_score(entry, current, stop, target, score, prev_score, days)
        health_label = _health_label(health_score)
        risk_state = _risk_state(current, stop, entry, target)
        bias = _action_bias(current, stop, target, score, prev_score, days, prog)

        pos["current_price"] = round(current, 2)
        pos["days_open"] = round(days, 2)
        pos["position_progress"] = round(prog, 3)
        pos["health_score"] = health_score
        pos["health_label"] = health_label
        pos["risk_state"] = risk_state
        pos["action_bias"] = bias
        pos["position_explanation"] = explain_position_state(pos, current)

        replace_position(symbol, pos)

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

        print(
            f"{symbol} | Current: {round(current, 2)} | Stop: {round(stop, 2)} | "
            f"Health: {health_score} ({health_label}) | Bias: {bias} | Action: {action}"
        )

        if action != "HOLD":
            result = close_position(symbol, current, reason=action.lower())
            actions.append({
                "symbol": symbol,
                "reason": action.lower(),
                "health_score": health_score,
                "health_label": health_label,
                "action_bias": bias,
                "result": result,
            })

            if result.get("closed"):
                print(
                    f"CLOSED: {symbol} | Reason: {action} | "
                    f"PnL: {result.get('pnl')} | Health: {health_score}"
                )
            elif result.get("blocked"):
                print(f"BLOCKED CLOSE: {symbol} | Reason: {result.get('reason')}")

    return actions
