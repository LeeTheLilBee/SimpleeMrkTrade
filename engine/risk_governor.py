from datetime import datetime

from engine.account_state import load_state, resolve_min_cash_reserve
from engine.performance_tracker import performance_summary
from engine.pdt_guard import pdt_status_preview
from engine.observatory_mode import normalize_mode, build_mode_context

MAX_DAILY_ENTRIES = 3
MAX_DRAWDOWN_DOLLARS = 150
DEFAULT_MIN_CASH_RESERVE = 100
MAX_OPEN_POSITIONS = 3
MAX_DAILY_LOSS = 250


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return int(default)


def _safe_bool(value, default=False):
    try:
        return bool(value)
    except Exception:
        return bool(default)


def _detect_trading_mode(kwargs):
    raw_mode = (
        kwargs.get("trading_mode")
        or kwargs.get("mode")
        or kwargs.get("execution_mode")
        or "paper"
    )
    return normalize_mode(raw_mode)


def governor_status(
    current_open_positions=0,
    executed_entries_today=0,
    executed_trades_today=None,
    max_daily_entries=None,
    max_drawdown_dollars=None,
    min_cash_reserve=None,
    max_open_positions=None,
    max_daily_loss=None,
    kill_switch=False,
    **kwargs,
):
    state = load_state()
    perf = performance_summary()
    pdt = pdt_status_preview()

    cash = _safe_float(state.get("cash", 0), 0)
    equity = _safe_float(state.get("equity", 0), 0)
    buying_power = _safe_float(state.get("buying_power", 0), 0)
    max_drawdown = _safe_float(perf.get("max_drawdown", 0), 0)
    realized_pnl_today = _safe_float(perf.get("realized_pnl_today", 0), 0)

    current_open_positions = _safe_int(current_open_positions, 0)
    perf_entries_today = _safe_int(perf.get("entries_today", 0), 0)
    perf_closes_today = _safe_int(perf.get("closes_today", 0), 0)
    perf_round_trips_today = _safe_int(perf.get("round_trips_today", 0), 0)

    executed_entries_today = _safe_int(
        perf_entries_today if perf_entries_today > 0 else executed_entries_today,
        0,
    )

    executed_trades_today_value = _safe_int(
        perf.get(
            "executed_trades_today",
            executed_trades_today if executed_trades_today is not None else executed_entries_today,
        ),
        executed_entries_today,
    )

    max_daily_entries = _safe_int(
        MAX_DAILY_ENTRIES if max_daily_entries is None else max_daily_entries,
        MAX_DAILY_ENTRIES,
    )
    max_drawdown_dollars = _safe_float(
        MAX_DRAWDOWN_DOLLARS if max_drawdown_dollars is None else max_drawdown_dollars,
        MAX_DRAWDOWN_DOLLARS,
    )
    max_open_positions = _safe_int(
        MAX_OPEN_POSITIONS if max_open_positions is None else max_open_positions,
        MAX_OPEN_POSITIONS,
    )
    max_daily_loss = _safe_float(
        MAX_DAILY_LOSS if max_daily_loss is None else max_daily_loss,
        MAX_DAILY_LOSS,
    )

    effective_min_cash_reserve = (
        _safe_float(min_cash_reserve, DEFAULT_MIN_CASH_RESERVE)
        if min_cash_reserve is not None
        else resolve_min_cash_reserve(state, fallback_amount=DEFAULT_MIN_CASH_RESERVE)
    )

    trading_mode = _detect_trading_mode(kwargs)
    mode_context = build_mode_context(trading_mode)

    strict_reserve = _safe_bool(mode_context.get("strict_reserve", True), True)
    strict_pdt = _safe_bool(mode_context.get("strict_pdt", True), True)

    pdt_restricted = _safe_bool(pdt.get("pdt_restricted", False), False)

    blocked = False
    reasons = []
    warnings = []

    controls = {
        "daily_entry_cap": False,
        "max_drawdown_hit": False,
        "cash_reserve_too_low": False,
        "cash_reserve_warning_only": False,
        "max_open_positions": False,
        "max_daily_loss_hit": False,
        "pdt_restricted": False,
        "pdt_warning_only": False,
        "kill_switch": False,
    }

    if executed_entries_today >= max_daily_entries:
        blocked = True
        controls["daily_entry_cap"] = True
        reasons.append("daily_entry_cap")

    if max_drawdown >= max_drawdown_dollars:
        blocked = True
        controls["max_drawdown_hit"] = True
        reasons.append("max_drawdown_hit")

    if cash <= effective_min_cash_reserve:
        controls["cash_reserve_too_low"] = True
        if strict_reserve:
            blocked = True
            reasons.append("cash_reserve_too_low")
        else:
            controls["cash_reserve_warning_only"] = True
            warnings.append("cash_reserve_too_low")

    if current_open_positions >= max_open_positions:
        blocked = True
        controls["max_open_positions"] = True
        reasons.append("max_open_positions")

    if realized_pnl_today <= -max_daily_loss:
        blocked = True
        controls["max_daily_loss_hit"] = True
        reasons.append("max_daily_loss_hit")

    if pdt_restricted:
        controls["pdt_restricted"] = True
        if strict_pdt:
            blocked = True
            reasons.append("pdt_restricted")
        else:
            controls["pdt_warning_only"] = True
            warnings.append("pdt_restricted")

    if kill_switch or (controls["max_drawdown_hit"] and controls["max_daily_loss_hit"]):
        blocked = True
        controls["kill_switch"] = True
        reasons.append("kill_switch")

    deduped_reasons = []
    seen = set()
    for reason in reasons:
        if reason not in seen:
            deduped_reasons.append(reason)
            seen.add(reason)

    deduped_warnings = []
    seen_warnings = set()
    for warning in warnings:
        if warning not in seen_warnings:
            deduped_warnings.append(warning)
            seen_warnings.add(warning)

    status_label = "BLOCKED" if blocked else "CLEAR"
    if not blocked and deduped_warnings:
        status_label = "CLEAR_WITH_WARNINGS"

    return {
        "blocked": blocked,
        "ok_to_trade": not blocked,
        "status_label": status_label,
        "reasons": deduped_reasons,
        "warnings": deduped_warnings,
        "cash": cash,
        "equity": equity,
        "buying_power": buying_power,
        "max_drawdown": max_drawdown,
        "realized_pnl_today": realized_pnl_today,
        "current_open_positions": current_open_positions,
        "entries_today": executed_entries_today,
        "executed_entries_today": executed_entries_today,
        "executed_trades_today": executed_trades_today_value,
        "closes_today": perf_closes_today,
        "round_trips_today": perf_round_trips_today,
        "limits": {
            "max_daily_entries": max_daily_entries,
            "max_drawdown_dollars": max_drawdown_dollars,
            "min_cash_reserve": effective_min_cash_reserve,
            "max_open_positions": max_open_positions,
            "max_daily_loss": max_daily_loss,
        },
        "controls": controls,
        "pdt": pdt,
        "trading_mode": trading_mode,
        "mode_context": mode_context,
        "reserve_mode": state.get("reserve_mode", "percent"),
        "reserve_value": state.get("reserve_value", 20.0),
        "timestamp": datetime.now().isoformat(),
        "extra_kwargs_seen": list(kwargs.keys()),
    }
