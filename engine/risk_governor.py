from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from engine.account_state import load_state, resolve_min_cash_reserve
from engine.performance_tracker import performance_summary
from engine.pdt_guard import pdt_status_preview
from engine.observatory_mode import (
    normalize_mode,
    build_mode_context,
    resolve_governor_for_mode,
)

MAX_DAILY_ENTRIES = 3
MAX_DRAWDOWN_DOLLARS = 150
DEFAULT_MIN_CASH_RESERVE = 100
MAX_OPEN_POSITIONS = 3
MAX_DAILY_LOSS = 250


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        return bool(value)
    except Exception:
        return bool(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def _dedupe_keep_order(items: List[Any]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        text = _safe_str(item, "")
        if text and text not in seen:
            out.append(text)
            seen.add(text)
    return out


def _detect_trading_mode(kwargs: Dict[str, Any]) -> str:
    raw_mode = (
        kwargs.get("trading_mode")
        or kwargs.get("mode")
        or kwargs.get("execution_mode")
        or "paper"
    )
    return normalize_mode(raw_mode)


def _derive_limits_from_mode(
    mode_context: Dict[str, Any],
    max_daily_entries: Any,
    max_open_positions: Any,
) -> Dict[str, Any]:
    resolved_daily_entries = _safe_int(
        max_daily_entries if max_daily_entries is not None else mode_context.get("max_daily_entries", MAX_DAILY_ENTRIES),
        MAX_DAILY_ENTRIES,
    )
    resolved_open_positions = _safe_int(
        max_open_positions if max_open_positions is not None else mode_context.get("max_open_positions", MAX_OPEN_POSITIONS),
        MAX_OPEN_POSITIONS,
    )
    return {
        "max_daily_entries": resolved_daily_entries,
        "max_open_positions": resolved_open_positions,
    }


def _build_raw_controls() -> Dict[str, bool]:
    return {
        "daily_entry_cap": False,
        "max_drawdown_hit": False,
        "cash_reserve_too_low": False,
        "cash_reserve_warning_only": False,
        "max_open_positions": False,
        "max_daily_loss_hit": False,
        "pdt_restricted": False,
        "pdt_warning_only": False,
        "kill_switch": False,
        "session_unhealthy": False,
        "broker_unhealthy": False,
        "position_cap_warning_only": False,
        "daily_loss_warning_only": False,
    }


def _resolve_session_broker_health(kwargs: Dict[str, Any]) -> Dict[str, bool]:
    session_healthy = _safe_bool(kwargs.get("session_healthy", True), True)
    broker_healthy = _safe_bool(kwargs.get("broker_healthy", True), True)
    return {
        "session_healthy": session_healthy,
        "broker_healthy": broker_healthy,
    }


def governor_status(
    current_open_positions: int = 0,
    executed_entries_today: int = 0,
    executed_trades_today: Any = None,
    max_daily_entries: Any = None,
    max_drawdown_dollars: Any = None,
    min_cash_reserve: Any = None,
    max_open_positions: Any = None,
    max_daily_loss: Any = None,
    kill_switch: bool = False,
    **kwargs,
) -> Dict[str, Any]:
    state = load_state()
    perf = performance_summary()
    pdt = pdt_status_preview()

    state = _safe_dict(state)
    perf = _safe_dict(perf)
    pdt = _safe_dict(pdt)

    cash = _safe_float(state.get("cash", 0), 0.0)
    equity = _safe_float(state.get("equity", 0), 0.0)
    buying_power = _safe_float(state.get("buying_power", 0), 0.0)

    max_drawdown = _safe_float(perf.get("max_drawdown", 0), 0.0)
    realized_pnl_today = _safe_float(perf.get("realized_pnl_today", 0), 0.0)
    unrealized_pnl = _safe_float(perf.get("unrealized_pnl", 0), 0.0)

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

    trading_mode = _detect_trading_mode(kwargs)
    mode_context = build_mode_context(trading_mode)

    derived_limits = _derive_limits_from_mode(
        mode_context=mode_context,
        max_daily_entries=max_daily_entries,
        max_open_positions=max_open_positions,
    )

    max_daily_entries = derived_limits["max_daily_entries"]
    max_open_positions = derived_limits["max_open_positions"]

    max_drawdown_dollars = _safe_float(
        MAX_DRAWDOWN_DOLLARS if max_drawdown_dollars is None else max_drawdown_dollars,
        MAX_DRAWDOWN_DOLLARS,
    )
    max_daily_loss = _safe_float(
        MAX_DAILY_LOSS if max_daily_loss is None else max_daily_loss,
        MAX_DAILY_LOSS,
    )

    reserve_floor_pct = _safe_float(mode_context.get("reserve_floor_pct", 0.20), 0.20)
    reserve_floor_from_pct = round(max(equity, 0.0) * reserve_floor_pct, 2)

    if min_cash_reserve is not None:
        effective_min_cash_reserve = _safe_float(min_cash_reserve, DEFAULT_MIN_CASH_RESERVE)
    else:
        effective_min_cash_reserve = resolve_min_cash_reserve(
            state,
            fallback_amount=max(DEFAULT_MIN_CASH_RESERVE, reserve_floor_from_pct),
        )
        if effective_min_cash_reserve < reserve_floor_from_pct:
            effective_min_cash_reserve = reserve_floor_from_pct

    strict_reserve = _safe_bool(mode_context.get("strict_reserve", True), True)
    strict_pdt = _safe_bool(mode_context.get("strict_pdt", True), True)
    strict_position_cap = _safe_bool(mode_context.get("strict_position_cap", True), True)
    strict_daily_loss = _safe_bool(mode_context.get("strict_daily_loss", True), True)
    strict_drawdown = _safe_bool(mode_context.get("strict_drawdown", True), True)
    strict_kill_switch = _safe_bool(mode_context.get("strict_kill_switch", True), True)

    reserve_warning_only = _safe_bool(mode_context.get("reserve_warning_only", False), False)
    pdt_warning_only = _safe_bool(mode_context.get("pdt_warning_only", False), False)
    position_cap_warning_only = _safe_bool(mode_context.get("position_cap_warning_only", False), False)
    daily_loss_warning_only = _safe_bool(mode_context.get("daily_loss_warning_only", False), False)

    pdt_restricted = _safe_bool(pdt.get("pdt_restricted", False), False)

    health = _resolve_session_broker_health(kwargs)
    session_healthy = health["session_healthy"]
    broker_healthy = health["broker_healthy"]

    controls = _build_raw_controls()
    raw_reasons: List[str] = []
    raw_warnings: List[str] = []

    # daily entries
    if executed_entries_today >= max_daily_entries:
        controls["daily_entry_cap"] = True
        raw_reasons.append("daily_entry_cap")

    # drawdown
    if max_drawdown >= max_drawdown_dollars:
        controls["max_drawdown_hit"] = True
        if strict_drawdown:
            raw_reasons.append("max_drawdown_hit")
        else:
            raw_warnings.append("max_drawdown_hit")

    # reserve
    if cash <= effective_min_cash_reserve:
        controls["cash_reserve_too_low"] = True
        if strict_reserve and not reserve_warning_only:
            raw_reasons.append("cash_reserve_too_low")
        else:
            controls["cash_reserve_warning_only"] = True
            raw_warnings.append("cash_reserve_too_low")

    # open positions
    if current_open_positions >= max_open_positions:
        controls["max_open_positions"] = True
        if strict_position_cap and not position_cap_warning_only:
            raw_reasons.append("max_open_positions")
        else:
            controls["position_cap_warning_only"] = True
            raw_warnings.append("max_open_positions")

    # daily loss
    if realized_pnl_today <= -abs(max_daily_loss):
        controls["max_daily_loss_hit"] = True
        if strict_daily_loss and not daily_loss_warning_only:
            raw_reasons.append("max_daily_loss_hit")
        else:
            controls["daily_loss_warning_only"] = True
            raw_warnings.append("max_daily_loss_hit")

    # pdt
    if pdt_restricted:
        controls["pdt_restricted"] = True
        if strict_pdt and not pdt_warning_only:
            raw_reasons.append("pdt_restricted")
        else:
            controls["pdt_warning_only"] = True
            raw_warnings.append("pdt_restricted")

    # health
    if not session_healthy:
        controls["session_unhealthy"] = True
        raw_reasons.append("session_unhealthy")

    if not broker_healthy:
        controls["broker_unhealthy"] = True
        raw_reasons.append("broker_unhealthy")

    # kill switch
    kill_switch_triggered = _safe_bool(kill_switch, False) or (
        controls["max_drawdown_hit"] and controls["max_daily_loss_hit"]
    )
    if kill_switch_triggered:
        controls["kill_switch"] = True
        if strict_kill_switch:
            raw_reasons.append("kill_switch")
        else:
            raw_warnings.append("kill_switch")

    raw_reasons = _dedupe_keep_order(raw_reasons)
    raw_warnings = _dedupe_keep_order(raw_warnings)

    pre_mode_blocked = len(raw_reasons) > 0
    pre_mode_status_label = "BLOCKED" if pre_mode_blocked else ("CLEAR_WITH_WARNINGS" if raw_warnings else "CLEAR")

    base_snapshot = {
        "blocked": pre_mode_blocked,
        "ok_to_trade": not pre_mode_blocked,
        "status_label": pre_mode_status_label,
        "reasons": list(raw_reasons),
        "warnings": list(raw_warnings),

        "cash": cash,
        "equity": equity,
        "buying_power": buying_power,
        "max_drawdown": max_drawdown,
        "realized_pnl_today": realized_pnl_today,
        "unrealized_pnl": unrealized_pnl,

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

        # extra visibility
        "raw_triggers": {
            "daily_entry_cap": controls["daily_entry_cap"],
            "max_drawdown_hit": controls["max_drawdown_hit"],
            "cash_reserve_too_low": controls["cash_reserve_too_low"],
            "max_open_positions": controls["max_open_positions"],
            "max_daily_loss_hit": controls["max_daily_loss_hit"],
            "pdt_restricted": controls["pdt_restricted"],
            "kill_switch": controls["kill_switch"],
            "session_unhealthy": controls["session_unhealthy"],
            "broker_unhealthy": controls["broker_unhealthy"],
        },
        "raw_reasons": list(raw_reasons),
        "raw_warnings": list(raw_warnings),
        "health": {
            "session_healthy": session_healthy,
            "broker_healthy": broker_healthy,
        },
        "diagnostics": {
            "strict_reserve": strict_reserve,
            "strict_pdt": strict_pdt,
            "strict_position_cap": strict_position_cap,
            "strict_daily_loss": strict_daily_loss,
            "strict_drawdown": strict_drawdown,
            "strict_kill_switch": strict_kill_switch,
            "reserve_warning_only": reserve_warning_only,
            "pdt_warning_only": pdt_warning_only,
            "position_cap_warning_only": position_cap_warning_only,
            "daily_loss_warning_only": daily_loss_warning_only,
            "reserve_floor_pct": reserve_floor_pct,
            "reserve_floor_from_pct": reserve_floor_from_pct,
        },
        "pre_mode_status": {
            "blocked": pre_mode_blocked,
            "reasons": list(raw_reasons),
            "warnings": list(raw_warnings),
            "status_label": pre_mode_status_label,
        },
    }

    resolved = resolve_governor_for_mode(base_snapshot, trading_mode)
    resolved["post_mode_status"] = {
        "blocked": _safe_bool(resolved.get("blocked", False), False),
        "reasons": _safe_list(resolved.get("reasons")),
        "warnings": _safe_list(resolved.get("warnings")),
        "status_label": _safe_str(resolved.get("status_label"), "CLEAR"),
    }
    return resolved
