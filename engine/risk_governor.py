from engine.account_state import load_state
from engine.performance_tracker import performance_summary

MAX_DAILY_TRADES = 3
MAX_DRAWDOWN_DOLLARS = 150
MIN_CASH_RESERVE = 100
MAX_OPEN_POSITIONS = 3

def governor_status(current_open_positions, executed_trades_today):
    state = load_state()
    perf = performance_summary()

    cash = float(state.get("cash", 0))
    max_drawdown = float(perf.get("max_drawdown", 0))

    blocked = False
    reasons = []

    if executed_trades_today >= MAX_DAILY_TRADES:
        blocked = True
        reasons.append("daily_trade_cap")

    if max_drawdown >= MAX_DRAWDOWN_DOLLARS:
        blocked = True
        reasons.append("max_drawdown_hit")

    if cash <= MIN_CASH_RESERVE:
        blocked = True
        reasons.append("cash_reserve_too_low")

    if current_open_positions >= MAX_OPEN_POSITIONS:
        blocked = True
        reasons.append("max_open_positions")

    return {
        "blocked": blocked,
        "reasons": reasons,
        "cash": cash,
        "max_drawdown": max_drawdown
    }
