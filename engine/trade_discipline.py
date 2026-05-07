from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


DISCIPLINE_FILE = Path("data/trade_discipline_state.json")

PDT_EQUITY_THRESHOLD = 25000.0
DEFAULT_MAX_ROUND_TRIPS_UNDER_25K = 3
DEFAULT_ROLLING_BUSINESS_DAYS = 5
DEFAULT_MAX_DAILY_ENTRIES_UNDER_25K = 3
DEFAULT_MAX_DAILY_ENTRIES_OVER_25K = 6
DEFAULT_MAX_OPEN_POSITIONS_UNDER_25K = 3
DEFAULT_MAX_OPEN_POSITIONS_OVER_25K = 6


def _now() -> datetime:
    return datetime.now()


def _now_iso() -> str:
    return _now().isoformat()


def _today_key() -> str:
    return _now().strftime("%Y-%m-%d")


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


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


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _norm_vehicle(value: Any) -> str:
    vehicle = _safe_str(value, "UNKNOWN").upper()
    if vehicle in {"OPTION", "OPTIONS"}:
        return "OPTION"
    if vehicle in {"STOCK", "EQUITY", "SHARES"}:
        return "STOCK"
    if vehicle in {"RESEARCH_ONLY", "WATCH", "OBSERVED_ONLY"}:
        return "RESEARCH_ONLY"
    return vehicle or "UNKNOWN"


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


def _load_state() -> Dict[str, Any]:
    try:
        if not DISCIPLINE_FILE.exists():
            return {
                "version": 1,
                "created_at": _now_iso(),
                "updated_at": _now_iso(),
                "events": [],
                "symbol_memory": {},
                "setup_memory": {},
                "account_memory": {},
            }

        with open(DISCIPLINE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, dict) else {}
    except Exception:
        return {
            "version": 1,
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "events": [],
            "symbol_memory": {},
            "setup_memory": {},
            "account_memory": {},
        }


def _save_state(state: Dict[str, Any]) -> Dict[str, Any]:
    DISCIPLINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = _now_iso()

    events = _safe_list(state.get("events"))
    if len(events) > 1500:
        state["events"] = events[-1500:]

    with open(DISCIPLINE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    return state


def _event_date_key(event: Dict[str, Any]) -> str:
    dt = _parse_dt(event.get("timestamp"))
    if dt:
        return dt.strftime("%Y-%m-%d")
    return _safe_str(event.get("date_key"), "")


def _same_day_entry_and_close(entry: Dict[str, Any], close: Dict[str, Any]) -> bool:
    entry_day = _event_date_key(entry)
    close_day = _event_date_key(close)
    return bool(entry_day and close_day and entry_day == close_day)


def _event_symbol(event: Dict[str, Any]) -> str:
    return _norm_symbol(event.get("symbol"))


def _event_action(event: Dict[str, Any]) -> str:
    return _safe_str(event.get("action"), "").upper()


def _event_account(event: Dict[str, Any]) -> str:
    return _safe_str(event.get("account_id"), "default")


def _event_trade_id(event: Dict[str, Any]) -> str:
    return _safe_str(event.get("trade_id"), "")


def _build_setup_fingerprint(candidate: Dict[str, Any]) -> str:
    symbol = _norm_symbol(candidate.get("symbol"))
    strategy = _safe_str(
        candidate.get("strategy", candidate.get("final_strategy", candidate.get("starting_strategy", ""))),
        "",
    ).upper()
    vehicle = _norm_vehicle(candidate.get("vehicle_selected", candidate.get("vehicle", "")))
    expiry = _safe_str(
        candidate.get("expiration", candidate.get("expiry", candidate.get("option_expiration", ""))),
        "",
    )
    strike = _safe_str(
        candidate.get("strike", candidate.get("option_strike", "")),
        "",
    )
    right = _safe_str(
        candidate.get("right", candidate.get("option_type", strategy)),
        "",
    ).upper()

    pieces = [symbol, strategy, vehicle, expiry, strike, right]
    return "|".join([p for p in pieces if p])


def _business_window_events(events: List[Dict[str, Any]], business_days: int) -> List[Dict[str, Any]]:
    valid_days = set(_business_days_back(_now(), business_days))
    return [event for event in events if _event_date_key(event) in valid_days]


def _count_round_trips(events: List[Dict[str, Any]], account_id: str, business_days: int) -> int:
    window = _business_window_events(events, business_days)

    entries: Dict[str, Dict[str, Any]] = {}
    closes: List[Dict[str, Any]] = []

    for event in window:
        if account_id and _event_account(event) != account_id:
            continue

        action = _event_action(event)
        trade_id = _event_trade_id(event)

        if action in {"ENTRY", "OPEN", "BUY", "EXECUTED_ENTRY"}:
            if trade_id:
                entries[trade_id] = event

        if action in {"CLOSE", "SELL", "EXIT", "EXECUTED_CLOSE"}:
            closes.append(event)

    round_trips = 0

    for close in closes:
        trade_id = _event_trade_id(close)
        if trade_id and trade_id in entries:
            if _same_day_entry_and_close(entries[trade_id], close):
                round_trips += 1

    return round_trips


def _count_entries_today(events: List[Dict[str, Any]], account_id: str) -> int:
    today = _today_key()
    count = 0

    for event in events:
        if account_id and _event_account(event) != account_id:
            continue

        if _event_date_key(event) != today:
            continue

        if _event_action(event) in {"ENTRY", "OPEN", "BUY", "EXECUTED_ENTRY"}:
            count += 1

    return count


def _last_symbol_event(
    events: List[Dict[str, Any]],
    symbol: str,
    account_id: str = "default",
    actions: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    allowed = {a.upper() for a in actions} if actions else None

    for event in reversed(events):
        if account_id and _event_account(event) != account_id:
            continue
        if _event_symbol(event) != symbol:
            continue
        if allowed and _event_action(event) not in allowed:
            continue
        return event

    return None


def _hours_since_event(event: Optional[Dict[str, Any]]) -> Optional[float]:
    if not event:
        return None

    dt = _parse_dt(event.get("timestamp"))
    if not dt:
        return None

    diff = _now() - dt
    return max(0.0, diff.total_seconds() / 3600.0)


def _has_duplicate_open_position(
    candidate: Dict[str, Any],
    open_positions: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    symbol = _norm_symbol(candidate.get("symbol"))
    requested_vehicle = _norm_vehicle(candidate.get("vehicle_selected", candidate.get("vehicle", "")))

    for pos in _safe_list(open_positions):
        pos = _safe_dict(pos)
        pos_symbol = _norm_symbol(pos.get("symbol"))
        pos_vehicle = _norm_vehicle(pos.get("vehicle", pos.get("vehicle_selected", "")))

        if pos_symbol != symbol:
            continue

        return {
            "duplicate": True,
            "reason": "duplicate_open_position",
            "detail": (
                f"{symbol} already has an open {pos_vehicle or 'position'} position. "
                f"The Observatory should not stack another {requested_vehicle or 'trade'} on the same symbol."
            ),
            "existing_trade_id": _safe_str(pos.get("trade_id", pos.get("id", "")), ""),
            "existing_vehicle": pos_vehicle,
        }

    return {
        "duplicate": False,
        "reason": "",
        "detail": "",
        "existing_trade_id": "",
        "existing_vehicle": "",
    }


def record_trade_event(
    *,
    symbol: str,
    action: str,
    trade_id: str = "",
    account_id: str = "default",
    vehicle: str = "",
    strategy: str = "",
    setup_fingerprint: str = "",
    notes: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    state = _load_state()

    event = {
        "timestamp": _now_iso(),
        "date_key": _today_key(),
        "symbol": _norm_symbol(symbol),
        "action": _safe_str(action, "").upper(),
        "trade_id": _safe_str(trade_id, ""),
        "account_id": _safe_str(account_id, "default"),
        "vehicle": _norm_vehicle(vehicle),
        "strategy": _safe_str(strategy, "").upper(),
        "setup_fingerprint": _safe_str(setup_fingerprint, ""),
        "notes": _safe_str(notes, ""),
        "metadata": _safe_dict(metadata),
    }

    state.setdefault("events", []).append(event)

    symbol_memory = state.setdefault("symbol_memory", {})
    sym = event["symbol"]

    if sym not in symbol_memory or not isinstance(symbol_memory.get(sym), dict):
        symbol_memory[sym] = {
            "symbol": sym,
            "first_seen": event["timestamp"],
            "last_seen": event["timestamp"],
            "entries": 0,
            "closes": 0,
            "rejects": 0,
            "last_action": "",
            "last_reason": "",
        }

    bucket = symbol_memory[sym]
    bucket["last_seen"] = event["timestamp"]
    bucket["last_action"] = event["action"]

    if event["action"] in {"ENTRY", "OPEN", "BUY", "EXECUTED_ENTRY"}:
        bucket["entries"] = int(bucket.get("entries", 0)) + 1
    elif event["action"] in {"CLOSE", "SELL", "EXIT", "EXECUTED_CLOSE"}:
        bucket["closes"] = int(bucket.get("closes", 0)) + 1
    elif event["action"] in {"REJECT", "SKIP", "BLOCK"}:
        bucket["rejects"] = int(bucket.get("rejects", 0)) + 1
        bucket["last_reason"] = event["notes"]

    _save_state(state)

    return {
        "saved": True,
        "event": event,
    }


def evaluate_trade_discipline(
    candidate: Dict[str, Any],
    *,
    account_id: str = "default",
    equity: float = 0.0,
    account_type: str = "margin",
    trading_mode: str = "paper",
    open_positions: Optional[List[Dict[str, Any]]] = None,
    max_open_positions: Optional[int] = None,
    max_daily_entries: Optional[int] = None,
    allow_over_25k_scaling: bool = True,
) -> Dict[str, Any]:
    """
    Beta-safe discipline evaluation.

    This does not place trades.
    It only says whether the candidate should be allowed, paused, or watched.
    """

    state = _load_state()
    events = _safe_list(state.get("events"))

    symbol = _norm_symbol(candidate.get("symbol"))
    vehicle = _norm_vehicle(candidate.get("vehicle_selected", candidate.get("vehicle", "")))
    strategy = _safe_str(
        candidate.get("final_strategy", candidate.get("strategy", candidate.get("starting_strategy", ""))),
        "",
    ).upper()

    equity_value = _safe_float(equity, 0.0)
    account_type_clean = _safe_str(account_type, "margin").lower()
    trading_mode_clean = _safe_str(trading_mode, "paper").lower()

    over_25k = equity_value >= PDT_EQUITY_THRESHOLD

    if max_open_positions is None:
        max_open_positions = (
            DEFAULT_MAX_OPEN_POSITIONS_OVER_25K
            if over_25k and allow_over_25k_scaling
            else DEFAULT_MAX_OPEN_POSITIONS_UNDER_25K
        )
    else:
        max_open_positions = _safe_int(max_open_positions, DEFAULT_MAX_OPEN_POSITIONS_UNDER_25K)

    if max_daily_entries is None:
        max_daily_entries = (
            DEFAULT_MAX_DAILY_ENTRIES_OVER_25K
            if over_25k and allow_over_25k_scaling
            else DEFAULT_MAX_DAILY_ENTRIES_UNDER_25K
        )
    else:
        max_daily_entries = _safe_int(max_daily_entries, DEFAULT_MAX_DAILY_ENTRIES_UNDER_25K)

    current_open_positions = len(_safe_list(open_positions))
    entries_today = _count_entries_today(events, account_id)

    round_trips_5_business_days = _count_round_trips(
        events=events,
        account_id=account_id,
        business_days=DEFAULT_ROLLING_BUSINESS_DAYS,
    )

    duplicate = _has_duplicate_open_position(candidate, open_positions=open_positions)

    setup_fingerprint = _build_setup_fingerprint(candidate)

    last_entry = _last_symbol_event(
        events,
        symbol,
        account_id=account_id,
        actions=["ENTRY", "OPEN", "BUY", "EXECUTED_ENTRY"],
    )
    last_close = _last_symbol_event(
        events,
        symbol,
        account_id=account_id,
        actions=["CLOSE", "SELL", "EXIT", "EXECUTED_CLOSE"],
    )
    last_reject = _last_symbol_event(
        events,
        symbol,
        account_id=account_id,
        actions=["REJECT", "SKIP", "BLOCK"],
    )

    hours_since_entry = _hours_since_event(last_entry)
    hours_since_close = _hours_since_event(last_close)
    hours_since_reject = _hours_since_event(last_reject)

    reasons: List[str] = []
    warnings: List[str] = []
    allowed = True

    if duplicate.get("duplicate"):
        allowed = False
        reasons.append("duplicate_open_position")

    if current_open_positions >= max_open_positions:
        allowed = False
        reasons.append("max_open_positions")

    if entries_today >= max_daily_entries:
        allowed = False
        reasons.append("daily_entry_cap")

    pdt_sensitive = (
        account_type_clean == "margin"
        and not over_25k
        and trading_mode_clean in {"paper", "live"}
    )

    if pdt_sensitive and round_trips_5_business_days >= DEFAULT_MAX_ROUND_TRIPS_UNDER_25K:
        allowed = False
        reasons.append("pdt_3_round_trips_5_business_days")

    if hours_since_close is not None and hours_since_close < 24:
        allowed = False
        reasons.append("recently_closed_cooldown")

    if hours_since_reject is not None and hours_since_reject < 12:
        allowed = False
        reasons.append("recently_rejected_cooldown")

    if hours_since_entry is not None and hours_since_entry < 24:
        warnings.append("recent_entry_symbol_fatigue")

    if vehicle == "RESEARCH_ONLY":
        allowed = False
        reasons.append("research_only_vehicle")

    if not symbol or symbol == "UNKNOWN":
        allowed = False
        reasons.append("missing_symbol")

    reasons = list(dict.fromkeys([r for r in reasons if r]))
    warnings = list(dict.fromkeys([w for w in warnings if w]))

    if allowed:
        status = "DISCIPLINE_ALLOWED"
        headline = "Trade discipline allows this candidate."
        detail = "No duplicate, PDT, daily entry, cooldown, or capacity block was found."
    else:
        status = "DISCIPLINE_BLOCKED"
        headline = "Trade discipline blocked this candidate."
        detail = " / ".join(reasons)

    return {
        "allowed": allowed,
        "blocked": not allowed,
        "status": status,
        "headline": headline,
        "detail": detail,
        "reasons": reasons,
        "warnings": warnings,
        "symbol": symbol,
        "vehicle": vehicle,
        "strategy": strategy,
        "setup_fingerprint": setup_fingerprint,
        "account_id": _safe_str(account_id, "default"),
        "equity": round(equity_value, 2),
        "over_25k": over_25k,
        "pdt_sensitive": pdt_sensitive,
        "account_type": account_type_clean,
        "trading_mode": trading_mode_clean,
        "entries_today": entries_today,
        "max_daily_entries": max_daily_entries,
        "round_trips_5_business_days": round_trips_5_business_days,
        "max_round_trips_under_25k": DEFAULT_MAX_ROUND_TRIPS_UNDER_25K,
        "current_open_positions": current_open_positions,
        "max_open_positions": max_open_positions,
        "hours_since_entry": hours_since_entry,
        "hours_since_close": hours_since_close,
        "hours_since_reject": hours_since_reject,
        "duplicate": duplicate,
        "timestamp": _now_iso(),
    }


def print_trade_discipline_summary(account_id: str = "default") -> Dict[str, Any]:
    state = _load_state()
    events = _safe_list(state.get("events"))

    entries_today = _count_entries_today(events, account_id)
    round_trips = _count_round_trips(events, account_id, DEFAULT_ROLLING_BUSINESS_DAYS)

    print("TRADE DISCIPLINE SUMMARY")
    print("Account:", account_id)
    print("Entries today:", entries_today)
    print("Round trips in rolling 5 business days:", round_trips)
    print("Events stored:", len(events))

    return {
        "account_id": account_id,
        "entries_today": entries_today,
        "round_trips_5_business_days": round_trips,
        "events_stored": len(events),
    }


__all__ = [
    "evaluate_trade_discipline",
    "record_trade_event",
    "print_trade_discipline_summary",
]
