from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from engine.account_state import load_state, resolve_min_cash_reserve
from engine.performance_tracker import performance_summary
from engine.pdt_guard import pdt_status_preview
from engine.observatory_mode import (
    normalize_mode,
    build_mode_context,
)

MAX_DAILY_ENTRIES = 3
MAX_DRAWDOWN_DOLLARS = 150.0
DEFAULT_MIN_CASH_RESERVE = 100.0
MAX_OPEN_POSITIONS = 3
MAX_DAILY_LOSS = 250.0


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return int(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        return bool(value)
    except Exception:
        return bool(default)


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _detect_trading_mode(kwargs: Dict[str, Any]) -> str:
    raw_mode = (
        kwargs.get("trading_mode")
        or kwargs.get("mode")
        or kwargs.get("execution_mode")
        or "paper"
    )
    return normalize_mode(raw_mode)


def _resolve_account_type(state: Dict[str, Any], pdt: Dict[str, Any]) -> str:
    account_type = _safe_str(
        state.get("account_type") or pdt.get("account_type") or "margin",
        "margin",
    ).lower()
    return account_type if account_type in {"cash", "margin"} else "margin"


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        text = _safe_str(item, "")
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _apply_mode_softening(governor_status: Dict[str, Any], mode_context: Dict[str, Any]) -> Dict[str, Any]:
    governor_status = governor_status if isinstance(governor_status, dict) else {}
    mode_context = mode_context if isinstance(mode_context, dict) else {}

    blocked = bool(governor_status.get("blocked", False))
    reasons = list(governor_status.get("reasons", []) or [])
    warnings = list(governor_status.get("warnings", []) or [])

    reserve_warning_only = bool(mode_context.get("reserve_warning_only", False))
    pdt_warning_only = bool(mode_context.get("pdt_warning_only", False))
    execution_warning_only = bool(mode_context.get("execution_warning_only", False))
    position_cap_warning_only = bool(mode_context.get("position_cap_warning_only", False))
    daily_loss_warning_only = bool(mode_context.get("daily_loss_warning_only", False))
    soft_block_reasons = set(mode_context.get("soft_block_reasons", []) or [])

    converted_reasons: List[str] = []
    converted_warnings: List[str] = list(warnings)

    for reason in reasons:
        reason = _safe_str(reason, "")
        if not reason:
            continue

        reserve_reason = reason in {
            "cash_reserve_too_low",
            "governor_blocked:cash_reserve_too_low",
            "reserve_blocked",
            "insufficient_cash_after_reserve",
        }
        pdt_reason = reason in {
            "pdt_restricted",
            "governor_blocked:pdt_restricted",
        }
        position_reason = reason in {
            "max_open_positions",
            "max_open_positions_reached",
            "daily_entry_cap",
        }
        daily_loss_reason = reason in {
            "max_daily_loss_hit",
            "max_drawdown_hit",
        }
        execution_reason = reason in {
            "session_unhealthy",
            "broker_unhealthy",
            "kill_switch",
            "kill_switch_enabled",
        }

        if reserve_reason and reserve_warning_only:
            converted_warnings.append(reason)
            continue
        if pdt_reason and pdt_warning_only:
            converted_warnings.append(reason)
            continue
        if position_reason and position_cap_warning_only:
            converted_warnings.append(reason)
            continue
        if daily_loss_reason and daily_loss_warning_only:
            converted_warnings.append(reason)
            continue
        if execution_reason and execution_warning_only:
            converted_warnings.append(reason)
            continue
        if reason in soft_block_reasons:
            converted_warnings.append(reason)
            continue

        converted_reasons.append(reason)

    converted_reasons = _dedupe_keep_order(converted_reasons)
    converted_warnings = _dedupe_keep_order(converted_warnings)

    governor_status["reasons"] = converted_reasons
    governor_status["warnings"] = converted_warnings
    governor_status["blocked"] = len(converted_reasons) > 0
    governor_status["ok_to_trade"] = not governor_status["blocked"]
    governor_status["status_label"] = (
        "BLOCKED"
        if governor_status["blocked"]
        else "CAUTION"
        if converted_warnings
        else "OK"
    )

    controls = _safe_dict(governor_status.get("controls"))
    if reserve_warning_only and any(
        r in converted_warnings
        for r in {
            "cash_reserve_too_low",
            "governor_blocked:cash_reserve_too_low",
            "reserve_blocked",
            "insufficient_cash_after_reserve",
        }
    ):
        controls["cash_reserve_warning_only"] = True
    if pdt_warning_only and any(
        r in converted_warnings
        for r in {
            "pdt_restricted",
            "governor_blocked:pdt_restricted",
        }
    ):
        controls["pdt_warning_only"] = True
    if position_cap_warning_only and any(
        r in converted_warnings
        for r in {
            "max_open_positions",
            "max_open_positions_reached",
            "daily_entry_cap",
        }
    ):
        controls["position_cap_warning_only"] = True
    if daily_loss_warning_only and any(
        r in converted_warnings
        for r in {
            "max_daily_loss_hit",
            "max_drawdown_hit",
        }
    ):
        controls["daily_loss_warning_only"] = True

    governor_status["controls"] = controls
    return governor_status


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
    state = _safe_dict(load_state())
    perf = _safe_dict(performance_summary())
    pdt = _safe_dict(pdt_status_preview())

    cash = round(_safe_float(state.get("cash", 0.0), 0.0), 2)
    equity = round(_safe_float(state.get("equity", 0.0), 0.0), 2)
    buying_power = round(_safe_float(state.get("buying_power", cash), cash), 2)

    max_drawdown = round(_safe_float(perf.get("max_drawdown", 0.0), 0.0), 2)
    realized_pnl_today = round(_safe_float(perf.get("realized_pnl_today", 0.0), 0.0), 2)
    unrealized_pnl = round(_safe_float(perf.get("unrealized_pnl", 0.0), 0.0), 2)

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

    strict_reserve = _safe_bool(mode_context.get("strict_reserve", True), True)
    strict_pdt = _safe_bool(mode_context.get("strict_pdt", True), True)
    strict_position_cap = _safe_bool(mode_context.get("strict_position_cap", True), True)
    strict_daily_loss = _safe_bool(mode_context.get("strict_daily_loss", True), True)
    strict_drawdown = _safe_bool(mode_context.get("strict_drawdown", True), True)
    strict_kill_switch = _safe_bool(mode_context.get("strict_kill_switch", True), True)

    reserve_warning_only = _safe_bool(mode_context.get("reserve_warning_only", False), False)
    pdt_warning_only = _safe_bool(mode_context.get("pdt_warning_only", False), False)
    execution_warning_only = _safe_bool(mode_context.get("execution_warning_only", False), False)
    position_cap_warning_only = _safe_bool(mode_context.get("position_cap_warning_only", False), False)
    daily_loss_warning_only = _safe_bool(mode_context.get("daily_loss_warning_only", False), False)

    max_daily_entries = _safe_int(
        mode_context.get("max_daily_entries", MAX_DAILY_ENTRIES)
        if max_daily_entries is None
        else max_daily_entries,
        MAX_DAILY_ENTRIES,
    )
    max_drawdown_dollars = round(
        _safe_float(
            MAX_DRAWDOWN_DOLLARS if max_drawdown_dollars is None else max_drawdown_dollars,
            MAX_DRAWDOWN_DOLLARS,
        ),
        2,
    )
    max_open_positions = _safe_int(
        mode_context.get("max_open_positions", MAX_OPEN_POSITIONS)
        if max_open_positions is None
        else max_open_positions,
        MAX_OPEN_POSITIONS,
    )
    max_daily_loss = round(
        _safe_float(
            MAX_DAILY_LOSS if max_daily_loss is None else max_daily_loss,
            MAX_DAILY_LOSS,
        ),
        2,
    )

    reserve_floor_pct = _safe_float(mode_context.get("reserve_floor_pct", 0.20), 0.20)
    account_type = _resolve_account_type(state, pdt)
    pdt_restricted = _safe_bool(pdt.get("pdt_restricted", False), False) if account_type == "margin" else False

    reserve_floor_from_cash = round(cash * reserve_floor_pct, 2) if cash > 0 else 0.0
    configured_min_reserve = (
        round(_safe_float(min_cash_reserve, DEFAULT_MIN_CASH_RESERVE), 2)
        if min_cash_reserve is not None
        else round(resolve_min_cash_reserve(state, fallback_amount=DEFAULT_MIN_CASH_RESERVE), 2)
    )
    effective_min_cash_reserve = round(max(configured_min_reserve, reserve_floor_from_cash), 2)
    reserve_gap = round(cash - effective_min_cash_reserve, 2)

    health = {
        "session_healthy": _safe_bool(kwargs.get("session_healthy", True), True),
        "broker_healthy": _safe_bool(kwargs.get("broker_healthy", True), True),
    }

    raw_triggers = {
        "daily_entry_cap": False,
        "max_drawdown_hit": False,
        "cash_reserve_too_low": False,
        "max_open_positions": False,
        "max_daily_loss_hit": False,
        "pdt_restricted": False,
        "kill_switch": False,
        "session_unhealthy": False,
        "broker_unhealthy": False,
    }

    controls = {
        "daily_entry_cap": False,
        "max_drawdown_hit": False,
        "cash_reserve_too_low": False,
        "cash_reserve_warning_only": False,
        "max_open_positions": False,
        "position_cap_warning_only": False,
        "max_daily_loss_hit": False,
        "daily_loss_warning_only": False,
        "pdt_restricted": False,
        "pdt_warning_only": False,
        "kill_switch": False,
        "session_unhealthy": False,
        "broker_unhealthy": False,
    }

    reasons: List[str] = []
    warnings: List[str] = []

    def _add_reason(reason: str) -> None:
        reasons.append(reason)

    def _add_warning(warning: str) -> None:
        warnings.append(warning)

    if executed_entries_today >= max_daily_entries:
        raw_triggers["daily_entry_cap"] = True
        controls["daily_entry_cap"] = True
        if strict_position_cap:
            _add_reason("daily_entry_cap")
        elif position_cap_warning_only:
            controls["position_cap_warning_only"] = True
            _add_warning("daily_entry_cap")
        else:
            _add_reason("daily_entry_cap")

    if max_drawdown >= max_drawdown_dollars:
        raw_triggers["max_drawdown_hit"] = True
        controls["max_drawdown_hit"] = True
        if strict_drawdown:
            _add_reason("max_drawdown_hit")
        elif daily_loss_warning_only:
            controls["daily_loss_warning_only"] = True
            _add_warning("max_drawdown_hit")
        else:
            _add_reason("max_drawdown_hit")

    if cash < effective_min_cash_reserve:
        raw_triggers["cash_reserve_too_low"] = True
        controls["cash_reserve_too_low"] = True
        if strict_reserve:
            _add_reason("cash_reserve_too_low")
        elif reserve_warning_only:
            controls["cash_reserve_warning_only"] = True
            _add_warning("cash_reserve_too_low")
        else:
            _add_reason("cash_reserve_too_low")

    if current_open_positions >= max_open_positions:
        raw_triggers["max_open_positions"] = True
        controls["max_open_positions"] = True
        if strict_position_cap:
            _add_reason("max_open_positions")
        elif position_cap_warning_only:
            controls["position_cap_warning_only"] = True
            _add_warning("max_open_positions")
        else:
            _add_reason("max_open_positions")

    if realized_pnl_today <= -max_daily_loss:
        raw_triggers["max_daily_loss_hit"] = True
        controls["max_daily_loss_hit"] = True
        if strict_daily_loss:
            _add_reason("max_daily_loss_hit")
        elif daily_loss_warning_only:
            controls["daily_loss_warning_only"] = True
            _add_warning("max_daily_loss_hit")
        else:
            _add_reason("max_daily_loss_hit")

    if pdt_restricted:
        raw_triggers["pdt_restricted"] = True
        controls["pdt_restricted"] = True
        if strict_pdt:
            _add_reason("pdt_restricted")
        elif pdt_warning_only:
            controls["pdt_warning_only"] = True
            _add_warning("pdt_restricted")
        else:
            _add_reason("pdt_restricted")

    if kill_switch:
        raw_triggers["kill_switch"] = True
        controls["kill_switch"] = True
        if strict_kill_switch:
            _add_reason("kill_switch")
        elif execution_warning_only:
            _add_warning("kill_switch")
        else:
            _add_reason("kill_switch")

    if not health["session_healthy"]:
        raw_triggers["session_unhealthy"] = True
        controls["session_unhealthy"] = True
        if execution_warning_only:
            _add_warning("session_unhealthy")
        else:
            _add_reason("session_unhealthy")

    if not health["broker_healthy"]:
        raw_triggers["broker_unhealthy"] = True
        controls["broker_unhealthy"] = True
        if execution_warning_only:
            _add_warning("broker_unhealthy")
        else:
            _add_reason("broker_unhealthy")

    reasons = _dedupe_keep_order(reasons)
    warnings = _dedupe_keep_order(warnings)

    pre_mode_status = {
        "blocked": len(reasons) > 0,
        "reasons": list(reasons),
        "warnings": list(warnings),
        "status_label": "BLOCKED" if reasons else ("CAUTION" if warnings else "OK"),
    }

    governor = {
        "blocked": len(reasons) > 0,
        "ok_to_trade": len(reasons) == 0,
        "status_label": pre_mode_status["status_label"],
        "reasons": list(reasons),
        "warnings": list(warnings),
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
        "pdt": {
            **pdt,
            "account_type": account_type,
            "pdt_restricted": pdt_restricted,
        },
        "trading_mode": trading_mode,
        "mode_context": mode_context,
        "reserve_mode": state.get("reserve_mode", "percent"),
        "reserve_value": state.get("reserve_value", 20.0),
        "timestamp": datetime.now().isoformat(),
        "extra_kwargs_seen": list(kwargs.keys()),
        "raw_triggers": raw_triggers,
        "raw_reasons": list(reasons),
        "raw_warnings": list(warnings),
        "health": health,
        "diagnostics": {
            "strict_reserve": strict_reserve,
            "strict_pdt": strict_pdt,
            "strict_position_cap": strict_position_cap,
            "strict_daily_loss": strict_daily_loss,
            "strict_drawdown": strict_drawdown,
            "strict_kill_switch": strict_kill_switch,
            "reserve_warning_only": reserve_warning_only,
            "pdt_warning_only": pdt_warning_only,
            "execution_warning_only": execution_warning_only,
            "position_cap_warning_only": position_cap_warning_only,
            "daily_loss_warning_only": daily_loss_warning_only,
            "reserve_floor_pct": reserve_floor_pct,
            "reserve_floor_from_cash": reserve_floor_from_cash,
            "configured_min_reserve": configured_min_reserve,
            "effective_min_cash_reserve": effective_min_cash_reserve,
            "reserve_gap": reserve_gap,
            "account_type": account_type,
        },
        "pre_mode_status": pre_mode_status,
    }

    governor = _apply_mode_softening(governor, mode_context)

    governor["post_mode_status"] = {
        "blocked": governor.get("blocked", False),
        "reasons": list(governor.get("reasons", [])),
        "warnings": list(governor.get("warnings", [])),
        "status_label": governor.get("status_label", "OK"),
    }

    return governor
