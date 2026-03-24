from datetime import datetime
from engine.account_state import load_state
from engine.performance_tracker import performance_summary
from engine.pdt_guard import pdt_status_preview

MAX_DAILY_ENTRIES = 3
MAX_DRAWDOWN_DOLLARS = 150
MIN_CASH_RESERVE = 100
MAX_OPEN_POSITIONS = 3
MAX_DAILY_LOSS = 250


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def governor_status(current_open_positions, executed_trades_today):
    state = load_state()
    perf = performance_summary()
    pdt = pdt_status_preview()

    cash = _safe_float(state.get("cash", 0))
    equity = _safe_float(state.get("equity", 0))
    buying_power = _safe_float(state.get("buying_power", 0))
    max_drawdown = _safe_float(perf.get("max_drawdown", 0))
    realized_pnl_today = _safe_float(perf.get("realized_pnl_today", 0))

    blocked = False
    reasons = []

    controls = {
        "daily_entry_cap": False,
        "max_drawdown_hit": False,
        "cash_reserve_too_low": False,
        "max_open_positions": False,
        "max_daily_loss_hit": False,
        "pdt_restricted": False,
        "kill_switch": False,
    }

    if executed_trades_today >= MAX_DAILY_ENTRIES:
        blocked = True
        controls["daily_entry_cap"] = True
        reasons.append("daily_entry_cap")

    if max_drawdown >= MAX_DRAWDOWN_DOLLARS:
        blocked = True
        controls["max_drawdown_hit"] = True
        reasons.append("max_drawdown_hit")

    if cash <= MIN_CASH_RESERVE:
        blocked = True
        controls["cash_reserve_too_low"] = True
        reasons.append("cash_reserve_too_low")

    if current_open_positions >= MAX_OPEN_POSITIONS:
        blocked = True
        controls["max_open_positions"] = True
        reasons.append("max_open_positions")

    if realized_pnl_today <= -MAX_DAILY_LOSS:
        blocked = True
        controls["max_daily_loss_hit"] = True
        reasons.append("max_daily_loss_hit")

    if pdt.get("pdt_restricted"):
        controls["pdt_restricted"] = True

    if controls["max_drawdown_hit"] and controls["max_daily_loss_hit"]:
        controls["kill_switch"] = True
        blocked = True
        if "kill_switch" not in reasons:
            reasons.append("kill_switch")

    return {
        "blocked": blocked,
        "reasons": reasons,
        "cash": cash,
        "equity": equity,
        "buying_power": buying_power,
        "max_drawdown": max_drawdown,
        "realized_pnl_today": realized_pnl_today,
        "current_open_positions": current_open_positions,
        "entries_today": perf.get("entries_today", executed_trades_today),
        "closes_today": perf.get("closes_today", 0),
        "round_trips_today": perf.get("round_trips_today", 0),
        "limits": {
            "max_daily_entries": MAX_DAILY_ENTRIES,
            "max_drawdown_dollars": MAX_DRAWDOWN_DOLLARS,
            "min_cash_reserve": MIN_CASH_RESERVE,
            "max_open_positions": MAX_OPEN_POSITIONS,
            "max_daily_loss": MAX_DAILY_LOSS,
        },
        "controls": controls,
        "pdt": pdt,
        "timestamp": datetime.now().isoformat(),
    }
