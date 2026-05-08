from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from engine.account_state import load_state, resolve_min_cash_reserve

try:
    from engine.account_state import get_daily_trade_counters
except Exception:
    get_daily_trade_counters = None

from engine.performance_tracker import performance_summary
from engine.pdt_guard import pdt_status_preview

try:
    from engine.observatory_mode import normalize_mode, build_mode_context
except Exception:
    def normalize_mode(value: Any) -> str:
        raw = str(value or "paper").strip().lower()
        return raw if raw in {"survey", "paper", "live"} else "paper"

    def build_mode_context(mode: str) -> Dict[str, Any]:
        mode = normalize_mode(mode)
        return {
            "mode": mode,
            "mode_label": f"{mode.title()} Mode",
            "mode_shell": "Solar System" if mode == "paper" else mode.title(),
            "mode_description": "",
            "theme_family": mode,
            "strict_reserve": False if mode == "paper" else True,
            "strict_pdt": False if mode == "paper" else True,
            "strict_execution_gate": True,
            "strict_position_cap": True,
            "strict_daily_loss": True,
            "strict_drawdown": True,
            "strict_kill_switch": True,
            "reserve_warning_only": True if mode == "paper" else False,
            "pdt_warning_only": True if mode == "paper" else False,
            "execution_warning_only": False,
            "position_cap_warning_only": False,
            "daily_loss_warning_only": False,
            "allow_stock_fallback": True,
            "options_first": True,
            "allow_same_day_high_risk_contracts": False,
            "minimum_option_dte": 1,
            "minimum_stock_cash_buffer_pct": 0.10,
            "minimum_live_like_cash_buffer_pct": 0.10,
            "reserve_floor_pct": 0.10 if mode == "paper" else 0.20,
            "max_daily_entries": 3,
            "max_open_positions": 3,
            "queue_limit": 3,
            "soft_block_reasons": [
                "cash_reserve_too_low",
                "governor_blocked:cash_reserve_too_low",
                "reserve_blocked",
                "insufficient_cash_after_reserve",
                "pdt_restricted",
                "governor_blocked:pdt_restricted",
            ],
            "hard_block_reasons": [
                "max_open_positions",
                "max_open_positions_reached",
                "max_daily_loss_hit",
                "daily_entry_cap",
                "rolling_5_business_day_entry_cap",
                "pdt_3_round_trips_5_business_days",
                "kill_switch",
                "kill_switch_enabled",
                "session_unhealthy",
                "broker_unhealthy",
                "max_drawdown_hit",
            ],
        }


try:
    from engine.trade_discipline import (
        DEFAULT_ROLLING_BUSINESS_DAYS,
        DEFAULT_MAX_ROUND_TRIPS_UNDER_25K,
    )
except Exception:
    DEFAULT_ROLLING_BUSINESS_DAYS = 5
    DEFAULT_MAX_ROUND_TRIPS_UNDER_25K = 3


PDT_EQUITY_THRESHOLD = 25000.0

UNDER_25K_MAX_DAILY_ENTRIES = 3
UNDER_25K_MAX_ROLLING_5_BUSINESS_DAY_ENTRIES = 3
UNDER_25K_MAX_OPEN_POSITIONS = 3
UNDER_25K_QUEUE_LIMIT = 3

OVER_25K_MAX_DAILY_ENTRIES = 6
OVER_25K_MAX_ROLLING_5_BUSINESS_DAY_ENTRIES = 12
OVER_25K_MAX_OPEN_POSITIONS = 6
OVER_25K_QUEUE_LIMIT = 5

MAX_DRAWDOWN_DOLLARS = 150.0
DEFAULT_MIN_CASH_RESERVE = 100.0
MAX_DAILY_LOSS = 250.0


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        if value is None:
            return bool(default)
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


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        text = _safe_str(item, "")
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


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


def _today_key() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _parse_dt(value: Any) -> Optional[datetime]:
    text = _safe_str(value, "")
    if not text:
        return None

    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00").replace("+00:00", ""))
    except Exception:
        return None


def _is_business_day(day: datetime) -> bool:
    return day.weekday() < 5


def _business_days_back(end_day: datetime, count: int) -> List[str]:
    days: List[str] = []
    cursor = end_day

    while len(days) < max(1, count):
        if _is_business_day(cursor):
            days.append(cursor.strftime("%Y-%m-%d"))
        cursor = cursor - timedelta(days=1)

    return days


def _event_date_key(event: Dict[str, Any]) -> str:
    dt = _parse_dt(event.get("timestamp"))
    if dt:
        return dt.strftime("%Y-%m-%d")
    return _safe_str(event.get("date_key"), "")


def _event_action(event: Dict[str, Any]) -> str:
    return _safe_str(event.get("action"), "").upper()


def _event_account(event: Dict[str, Any]) -> str:
    return _safe_str(event.get("account_id"), "default")


def _event_trade_id(event: Dict[str, Any]) -> str:
    return _safe_str(event.get("trade_id"), "")


def _load_trade_discipline_state() -> Dict[str, Any]:
    try:
        from engine.trade_discipline import _load_state
        state = _load_state()
        return state if isinstance(state, dict) else {}
    except Exception:
        return {}


def _discipline_events() -> List[Dict[str, Any]]:
    state = _load_trade_discipline_state()
    return [x for x in _safe_list(state.get("events", [])) if isinstance(x, dict)]


def _events_in_rolling_business_window(events: List[Dict[str, Any]], business_days: int) -> List[Dict[str, Any]]:
    valid_days = set(_business_days_back(datetime.now(), business_days))
    return [event for event in events if _event_date_key(event) in valid_days]


def _count_entries_from_events(
    events: List[Dict[str, Any]],
    account_id: str = "default",
    date_key: Optional[str] = None,
    rolling_business_days: Optional[int] = None,
) -> int:
    if rolling_business_days:
        events = _events_in_rolling_business_window(events, rolling_business_days)

    count = 0

    for event in events:
        if account_id and _event_account(event) != account_id:
            continue

        if date_key and _event_date_key(event) != date_key:
            continue

        if _event_action(event) in {"ENTRY", "OPEN", "BUY", "EXECUTED_ENTRY"}:
            count += 1

    return count


def _count_round_trips_from_events(
    events: List[Dict[str, Any]],
    account_id: str = "default",
    rolling_business_days: int = DEFAULT_ROLLING_BUSINESS_DAYS,
) -> int:
    window = _events_in_rolling_business_window(events, rolling_business_days)

    entries: Dict[str, Dict[str, Any]] = {}
    closes: List[Dict[str, Any]] = []

    for event in window:
        if account_id and _event_account(event) != account_id:
            continue

        action = _event_action(event)
        trade_id = _event_trade_id(event)

        if action in {"ENTRY", "OPEN", "BUY", "EXECUTED_ENTRY"} and trade_id:
            entries[trade_id] = event

        if action in {"CLOSE", "SELL", "EXIT", "EXECUTED_CLOSE"}:
            closes.append(event)

    round_trips = 0

    for close_event in closes:
        trade_id = _event_trade_id(close_event)
        entry_event = entries.get(trade_id)

        if not entry_event:
            continue

        if _event_date_key(entry_event) == _event_date_key(close_event):
            round_trips += 1

    return round_trips


def _load_reconciled_day_counters() -> Dict[str, Any]:
    if callable(get_daily_trade_counters):
        try:
            counters = _safe_dict(get_daily_trade_counters(_today_key()))
            if counters:
                return counters
        except Exception:
            pass

    return {
        "date_key": _today_key(),
        "entries_today": 0,
        "executed_entries_today": 0,
        "executed_trades_today": 0,
        "closes_today": 0,
        "round_trips_today": 0,
        "counter_source": "unavailable",
    }


def _build_equity_tier_limits(
    *,
    equity: float,
    mode_context: Dict[str, Any],
    max_daily_entries_override: Any = None,
    max_open_positions_override: Any = None,
) -> Dict[str, Any]:
    over_25k = equity >= PDT_EQUITY_THRESHOLD

    if over_25k:
        max_daily_entries = OVER_25K_MAX_DAILY_ENTRIES
        max_rolling_entries = OVER_25K_MAX_ROLLING_5_BUSINESS_DAY_ENTRIES
        max_open_positions = OVER_25K_MAX_OPEN_POSITIONS
        queue_limit = OVER_25K_QUEUE_LIMIT
        scale_profile = "expanded_over_25k"
    else:
        max_daily_entries = UNDER_25K_MAX_DAILY_ENTRIES
        max_rolling_entries = UNDER_25K_MAX_ROLLING_5_BUSINESS_DAY_ENTRIES
        max_open_positions = UNDER_25K_MAX_OPEN_POSITIONS
        queue_limit = UNDER_25K_QUEUE_LIMIT
        scale_profile = "protected_under_25k"

    mode_daily = _safe_int(mode_context.get("max_daily_entries", max_daily_entries), max_daily_entries)
    mode_open = _safe_int(mode_context.get("max_open_positions", max_open_positions), max_open_positions)
    mode_queue = _safe_int(mode_context.get("queue_limit", queue_limit), queue_limit)

    max_daily_entries = max(max_daily_entries, mode_daily) if over_25k else min(max_daily_entries, mode_daily)
    max_open_positions = max(max_open_positions, mode_open) if over_25k else min(max_open_positions, mode_open)
    queue_limit = max(queue_limit, mode_queue) if over_25k else min(queue_limit, mode_queue)

    if max_daily_entries_override is not None:
        max_daily_entries = _safe_int(max_daily_entries_override, max_daily_entries)

    if max_open_positions_override is not None:
        max_open_positions = _safe_int(max_open_positions_override, max_open_positions)

    return {
        "over_25k": over_25k,
        "scale_profile": scale_profile,
        "pdt_equity_threshold": PDT_EQUITY_THRESHOLD,
        "max_daily_entries": max_daily_entries,
        "max_rolling_5_business_day_entries": max_rolling_entries,
        "max_open_positions": max_open_positions,
        "queue_limit": queue_limit,
        "rolling_business_days": DEFAULT_ROLLING_BUSINESS_DAYS,
        "max_round_trips_under_25k": DEFAULT_MAX_ROUND_TRIPS_UNDER_25K,
    }


def _is_position_capacity_reason(reason: str) -> bool:
    return _safe_str(reason, "") in {
        "max_open_positions",
        "max_open_positions_reached",
        "governor_blocked:max_open_positions",
        "governor_blocked:max_open_positions_reached",
    }


def _is_daily_capacity_reason(reason: str) -> bool:
    return _safe_str(reason, "") in {
        "daily_entry_cap",
        "rolling_5_business_day_entry_cap",
        "pdt_3_round_trips_5_business_days",
        "governor_blocked:daily_entry_cap",
        "governor_blocked:rolling_5_business_day_entry_cap",
        "governor_blocked:pdt_3_round_trips_5_business_days",
    }


def _is_cash_reserve_reason(reason: str) -> bool:
    return _safe_str(reason, "") in {
        "cash_reserve_too_low",
        "governor_blocked:cash_reserve_too_low",
        "reserve_blocked",
        "insufficient_cash_after_reserve",
    }


def _build_governor_message(
    *,
    blocked: bool,
    reasons: List[str],
    warnings: List[str],
    current_open_positions: int,
    max_open_positions: int,
    trading_mode: str,
    mode_context: Dict[str, Any],
    entries_rolling_5_business_days: int,
    max_rolling_5_business_day_entries: int,
    round_trips_rolling_5_business_days: int,
    over_25k: bool,
) -> Dict[str, Any]:
    reasons = _dedupe_keep_order(reasons)
    warnings = _dedupe_keep_order(warnings)

    primary_reason = reasons[0] if reasons else ""
    mode_label = _safe_str(mode_context.get("mode_label"), trading_mode.title())

    execution_paused = bool(blocked)
    scan_can_continue = True

    if not blocked and warnings:
        headline = "Execution is allowed with warnings."
        summary = "The Observatory may still select trades, but the run should be reviewed before acting."
    elif not blocked:
        headline = "Execution is allowed."
        summary = "The Observatory can research, rank, and select trades normally."
    elif _is_position_capacity_reason(primary_reason):
        headline = "Portfolio full. Execution intentionally paused."
        summary = (
            f"The Observatory can keep researching, but it should not open another position because "
            f"the book already has {current_open_positions}/{max_open_positions} open positions."
        )
    elif primary_reason == "rolling_5_business_day_entry_cap":
        headline = "Rolling 5-business-day entry cap reached."
        summary = (
            f"The Observatory can keep researching, but execution is paused because this under-$25k "
            f"account already has {entries_rolling_5_business_days}/{max_rolling_5_business_day_entries} "
            "entries in the rolling 5-business-day window."
        )
    elif primary_reason == "pdt_3_round_trips_5_business_days":
        headline = "PDT-style round-trip brake active."
        summary = (
            f"The Observatory can keep researching, but execution is paused because this under-$25k "
            f"margin account already has {round_trips_rolling_5_business_days}/3 same-day round trips "
            "inside the rolling 5-business-day window."
        )
    elif primary_reason == "daily_entry_cap":
        headline = "Daily entry cap reached. Execution paused."
        summary = (
            "The Observatory can keep researching, but it should not open more entries today "
            "because the daily entry limit is already reached."
        )
    elif _is_cash_reserve_reason(primary_reason):
        headline = "Cash reserve protection active."
        summary = (
            "The Observatory can keep researching, but execution is paused because opening another "
            "position would violate the current reserve rule."
        )
    elif primary_reason in {"pdt_restricted", "governor_blocked:pdt_restricted"}:
        headline = "PDT guard active."
        summary = (
            "The Observatory can keep researching, but execution is paused because the account is "
            "under PDT-sensitive conditions."
        )
    elif primary_reason in {"kill_switch", "kill_switch_enabled"}:
        headline = "Kill switch active."
        summary = "Execution is paused because the kill switch is enabled."
        scan_can_continue = False
    elif primary_reason in {"session_unhealthy", "broker_unhealthy"}:
        headline = "Execution health check failed."
        summary = "Execution is paused because the session or broker connection is unhealthy."
        scan_can_continue = False
    elif primary_reason in {"max_daily_loss_hit", "max_drawdown_hit"}:
        headline = "Risk brake active."
        summary = "Execution is paused because loss or drawdown protection is active."
    else:
        headline = "Execution paused by governor."
        summary = f"The Observatory can keep researching, but execution is paused by: {primary_reason or 'unknown'}."

    return {
        "headline": headline,
        "summary": summary,
        "primary_reason": primary_reason,
        "reasons": reasons,
        "warnings": warnings,
        "execution_paused": execution_paused,
        "scan_can_continue": scan_can_continue,
        "mode": trading_mode,
        "mode_label": mode_label,
        "current_open_positions": current_open_positions,
        "max_open_positions": max_open_positions,
        "remaining_position_slots": max(0, max_open_positions - current_open_positions),
        "entries_rolling_5_business_days": entries_rolling_5_business_days,
        "max_rolling_5_business_day_entries": max_rolling_5_business_day_entries,
        "round_trips_rolling_5_business_days": round_trips_rolling_5_business_days,
        "over_25k": over_25k,
    }


def _apply_mode_softening(governor_status: Dict[str, Any], mode_context: Dict[str, Any]) -> Dict[str, Any]:
    governor_status = governor_status if isinstance(governor_status, dict) else {}
    mode_context = mode_context if isinstance(mode_context, dict) else {}

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

    hard_never_soften = {
        "max_open_positions",
        "max_open_positions_reached",
        "daily_entry_cap",
        "rolling_5_business_day_entry_cap",
        "pdt_3_round_trips_5_business_days",
        "kill_switch",
        "kill_switch_enabled",
        "session_unhealthy",
        "broker_unhealthy",
        "max_daily_loss_hit",
        "max_drawdown_hit",
    }

    for reason in reasons:
        reason = _safe_str(reason, "")
        if not reason:
            continue

        if reason in hard_never_soften:
            converted_reasons.append(reason)
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

    governor_status["controls"] = controls
    return governor_status


def governor_status(
    current_open_positions=0,
    executed_entries_today=None,
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
    reconciled = _load_reconciled_day_counters()

    account_id = _safe_str(kwargs.get("account_id"), "default")

    cash = round(_safe_float(state.get("cash", 0.0), 0.0), 2)
    equity = round(_safe_float(state.get("equity", 0.0), 0.0), 2)
    buying_power = round(_safe_float(state.get("buying_power", cash), cash), 2)

    max_drawdown = round(_safe_float(perf.get("max_drawdown", 0.0), 0.0), 2)
    realized_pnl_today = round(_safe_float(perf.get("realized_pnl_today", 0.0), 0.0), 2)
    unrealized_pnl = round(_safe_float(perf.get("unrealized_pnl", 0.0), 0.0), 2)

    current_open_positions = _safe_int(current_open_positions, 0)

    trading_mode = _detect_trading_mode(kwargs)
    mode_context = build_mode_context(trading_mode)

    tier_limits = _build_equity_tier_limits(
        equity=equity,
        mode_context=mode_context,
        max_daily_entries_override=max_daily_entries,
        max_open_positions_override=max_open_positions,
    )

    over_25k = bool(tier_limits["over_25k"])
    max_daily_entries_value = _safe_int(tier_limits["max_daily_entries"], UNDER_25K_MAX_DAILY_ENTRIES)
    max_open_positions_value = _safe_int(tier_limits["max_open_positions"], UNDER_25K_MAX_OPEN_POSITIONS)
    max_rolling_entries_value = _safe_int(
        tier_limits["max_rolling_5_business_day_entries"],
        UNDER_25K_MAX_ROLLING_5_BUSINESS_DAY_ENTRIES,
    )

    max_drawdown_dollars = round(
        _safe_float(
            MAX_DRAWDOWN_DOLLARS if max_drawdown_dollars is None else max_drawdown_dollars,
            MAX_DRAWDOWN_DOLLARS,
        ),
        2,
    )

    max_daily_loss = round(
        _safe_float(
            MAX_DAILY_LOSS if max_daily_loss is None else max_daily_loss,
            MAX_DAILY_LOSS,
        ),
        2,
    )

    discipline_events = _discipline_events()

    discipline_entries_today = _count_entries_from_events(
        discipline_events,
        account_id=account_id,
        date_key=_today_key(),
    )

    discipline_entries_rolling_5 = _count_entries_from_events(
        discipline_events,
        account_id=account_id,
        rolling_business_days=DEFAULT_ROLLING_BUSINESS_DAYS,
    )

    discipline_round_trips_rolling_5 = _count_round_trips_from_events(
        discipline_events,
        account_id=account_id,
        rolling_business_days=DEFAULT_ROLLING_BUSINESS_DAYS,
    )

    reconciled_entries_today = _safe_int(reconciled.get("entries_today", 0), 0)
    reconciled_executed_entries_today = _safe_int(
        reconciled.get("executed_entries_today", reconciled_entries_today),
        reconciled_entries_today,
    )
    reconciled_executed_trades_today = _safe_int(
        reconciled.get("executed_trades_today", reconciled_executed_entries_today),
        reconciled_executed_entries_today,
    )
    reconciled_closes_today = _safe_int(reconciled.get("closes_today", 0), 0)
    reconciled_round_trips_today = _safe_int(reconciled.get("round_trips_today", 0), 0)

    perf_entries_today = _safe_int(perf.get("entries_today", 0), 0)
    perf_closes_today = _safe_int(perf.get("closes_today", 0), 0)
    perf_round_trips_today = _safe_int(perf.get("round_trips_today", 0), 0)
    perf_executed_trades_today = _safe_int(
        perf.get("executed_trades_today", perf_entries_today),
        perf_entries_today,
    )

    counter_source = _safe_str(reconciled.get("counter_source"), "unavailable")
    using_reconciled = counter_source not in {"", "unavailable"}

    caller_executed_entries = (
        None if executed_entries_today is None else _safe_int(executed_entries_today, 0)
    )
    caller_executed_trades = (
        None if executed_trades_today is None else _safe_int(executed_trades_today, 0)
    )

    entries_today_value = max(
        discipline_entries_today,
        reconciled_entries_today if using_reconciled else 0,
        perf_entries_today,
        caller_executed_entries if caller_executed_entries is not None else 0,
    )

    executed_entries_today_value = max(
        discipline_entries_today,
        reconciled_executed_entries_today if using_reconciled else 0,
        perf_entries_today,
        caller_executed_entries if caller_executed_entries is not None else 0,
    )

    executed_trades_today_value = max(
        discipline_entries_today,
        reconciled_executed_trades_today if using_reconciled else 0,
        perf_executed_trades_today,
        caller_executed_trades if caller_executed_trades is not None else 0,
    )

    closes_today_value = max(
        reconciled_closes_today if using_reconciled else 0,
        perf_closes_today,
    )

    round_trips_today_value = max(
        reconciled_round_trips_today if using_reconciled else 0,
        perf_round_trips_today,
    )

    entries_today_source = "max(discipline_events, account_state, performance_summary, caller_override)"
    executed_entries_today_source = "max(discipline_events, account_state, performance_summary, caller_override)"
    executed_trades_today_source = "max(discipline_events, account_state, performance_summary, caller_override)"
    closes_today_source = "max(account_state, performance_summary)"
    round_trips_today_source = "max(account_state, performance_summary)"

    strict_reserve = _safe_bool(mode_context.get("strict_reserve", True), True)
    strict_pdt = _safe_bool(mode_context.get("strict_pdt", True), True)
    strict_position_cap = _safe_bool(mode_context.get("strict_position_cap", True), True)
    strict_daily_loss = _safe_bool(mode_context.get("strict_daily_loss", True), True)
    strict_drawdown = _safe_bool(mode_context.get("strict_drawdown", True), True)
    strict_kill_switch = _safe_bool(mode_context.get("strict_kill_switch", True), True)

    reserve_warning_only = _safe_bool(mode_context.get("reserve_warning_only", False), False)
    pdt_warning_only = _safe_bool(mode_context.get("pdt_warning_only", False), False)
    execution_warning_only = _safe_bool(mode_context.get("execution_warning_only", False), False)
    daily_loss_warning_only = _safe_bool(mode_context.get("daily_loss_warning_only", False), False)

    reserve_floor_pct = _safe_float(mode_context.get("reserve_floor_pct", 0.20), 0.20)
    account_type = _resolve_account_type(state, pdt)

    raw_pdt_restricted = _safe_bool(pdt.get("pdt_restricted", False), False) if account_type == "margin" else False
    pdt_sensitive = bool(account_type == "margin" and not over_25k and trading_mode in {"paper", "live"})

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
        "rolling_5_business_day_entry_cap": False,
        "pdt_3_round_trips_5_business_days": False,
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
        "rolling_5_business_day_entry_cap": False,
        "pdt_3_round_trips_5_business_days": False,
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

    if executed_entries_today_value >= max_daily_entries_value:
        raw_triggers["daily_entry_cap"] = True
        controls["daily_entry_cap"] = True
        _add_reason("daily_entry_cap")

    if not over_25k and discipline_entries_rolling_5 >= max_rolling_entries_value:
        raw_triggers["rolling_5_business_day_entry_cap"] = True
        controls["rolling_5_business_day_entry_cap"] = True
        _add_reason("rolling_5_business_day_entry_cap")

    if pdt_sensitive and discipline_round_trips_rolling_5 >= DEFAULT_MAX_ROUND_TRIPS_UNDER_25K:
        raw_triggers["pdt_3_round_trips_5_business_days"] = True
        controls["pdt_3_round_trips_5_business_days"] = True
        _add_reason("pdt_3_round_trips_5_business_days")

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

    if current_open_positions >= max_open_positions_value:
        raw_triggers["max_open_positions"] = True
        controls["max_open_positions"] = True
        if strict_position_cap:
            _add_reason("max_open_positions")
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

    if raw_pdt_restricted:
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

    mode_context = dict(mode_context)
    mode_context["max_daily_entries"] = max_daily_entries_value
    mode_context["max_open_positions"] = max_open_positions_value
    mode_context["queue_limit"] = tier_limits["queue_limit"]
    mode_context["equity_scale_profile"] = tier_limits["scale_profile"]
    mode_context["over_25k"] = over_25k
    mode_context["max_rolling_5_business_day_entries"] = max_rolling_entries_value

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
        "entries_today": entries_today_value,
        "executed_entries_today": executed_entries_today_value,
        "executed_trades_today": executed_trades_today_value,
        "closes_today": closes_today_value,
        "round_trips_today": round_trips_today_value,
        "entries_rolling_5_business_days": discipline_entries_rolling_5,
        "round_trips_rolling_5_business_days": discipline_round_trips_rolling_5,
        "pdt_sensitive": pdt_sensitive,
        "over_25k": over_25k,
        "equity_scale_profile": tier_limits["scale_profile"],
        "limits": {
            "max_daily_entries": max_daily_entries_value,
            "max_rolling_5_business_day_entries": max_rolling_entries_value,
            "max_drawdown_dollars": max_drawdown_dollars,
            "min_cash_reserve": effective_min_cash_reserve,
            "max_open_positions": max_open_positions_value,
            "max_daily_loss": max_daily_loss,
            "queue_limit": tier_limits["queue_limit"],
            "pdt_equity_threshold": PDT_EQUITY_THRESHOLD,
            "max_round_trips_under_25k": DEFAULT_MAX_ROUND_TRIPS_UNDER_25K,
            "rolling_business_days": DEFAULT_ROLLING_BUSINESS_DAYS,
        },
        "controls": controls,
        "pdt": {
            **pdt,
            "account_type": account_type,
            "pdt_restricted": raw_pdt_restricted,
            "pdt_sensitive": pdt_sensitive,
            "round_trips_rolling_5_business_days": discipline_round_trips_rolling_5,
            "max_round_trips_under_25k": DEFAULT_MAX_ROUND_TRIPS_UNDER_25K,
            "over_25k": over_25k,
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
        "counter_reconciliation": {
            "date_key": reconciled.get("date_key", _today_key()),
            "account_id": account_id,
            "counter_source": counter_source,
            "using_reconciled_counters": using_reconciled,
            "entries_today_source": entries_today_source,
            "executed_entries_today_source": executed_entries_today_source,
            "executed_trades_today_source": executed_trades_today_source,
            "closes_today_source": closes_today_source,
            "round_trips_today_source": round_trips_today_source,
            "discipline_event_count": len(discipline_events),
            "discipline_entries_today": discipline_entries_today,
            "discipline_entries_rolling_5_business_days": discipline_entries_rolling_5,
            "discipline_round_trips_rolling_5_business_days": discipline_round_trips_rolling_5,
            "caller_override": {
                "executed_entries_today": caller_executed_entries,
                "executed_trades_today": caller_executed_trades,
            },
            "reconciled_snapshot": reconciled,
            "performance_snapshot": {
                "entries_today": perf_entries_today,
                "executed_trades_today": perf_executed_trades_today,
                "closes_today": perf_closes_today,
                "round_trips_today": perf_round_trips_today,
            },
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
            "execution_warning_only": execution_warning_only,
            "daily_loss_warning_only": daily_loss_warning_only,
            "reserve_floor_pct": reserve_floor_pct,
            "reserve_floor_from_cash": reserve_floor_from_cash,
            "configured_min_reserve": configured_min_reserve,
            "effective_min_cash_reserve": effective_min_cash_reserve,
            "reserve_gap": reserve_gap,
            "account_type": account_type,
            "equity": equity,
            "over_25k": over_25k,
            "scale_profile": tier_limits["scale_profile"],
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

    governor["block_summary"] = _build_governor_message(
        blocked=bool(governor.get("blocked", False)),
        reasons=list(governor.get("reasons", [])),
        warnings=list(governor.get("warnings", [])),
        current_open_positions=current_open_positions,
        max_open_positions=max_open_positions_value,
        trading_mode=trading_mode,
        mode_context=mode_context,
        entries_rolling_5_business_days=discipline_entries_rolling_5,
        max_rolling_5_business_day_entries=max_rolling_entries_value,
        round_trips_rolling_5_business_days=discipline_round_trips_rolling_5,
        over_25k=over_25k,
    )

    governor["execution_pause"] = {
        "paused": bool(governor.get("blocked", False)),
        "primary_reason": governor["block_summary"].get("primary_reason", ""),
        "headline": governor["block_summary"].get("headline", ""),
        "summary": governor["block_summary"].get("summary", ""),
        "scan_can_continue": governor["block_summary"].get("scan_can_continue", True),
        "remaining_position_slots": governor["block_summary"].get("remaining_position_slots", 0),
        "entries_rolling_5_business_days": discipline_entries_rolling_5,
        "max_rolling_5_business_day_entries": max_rolling_entries_value,
        "round_trips_rolling_5_business_days": discipline_round_trips_rolling_5,
        "over_25k": over_25k,
    }

    return governor


__all__ = [
    "governor_status",
]
