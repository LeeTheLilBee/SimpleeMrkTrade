from __future__ import annotations

"""
Observatory Position Monitor

Purpose:
    Monitor open paper positions and decide whether to hold, protect profit,
    cut weakness, stop out, or take profit.

Critical option-safety rule:
    OPTION positions are monitored using option premium / option mark only.
    Underlying stock price is preserved as context only and must never become
    the option current price.

Why this rewrite exists:
    The system previously allowed an OPTION entry premium like 4.35 to be
    compared against an underlying stock price like 99.62, causing fake instant
    TAKE_PROFIT closes.

Compatibility goals:
    - Keep show_positions(), replace_position(), and close_position() flow.
    - Preserve old field names like entry/current_price/stop/target for display.
    - Add safer canonical fields for options:
        entry_premium
        current_premium
        current_option_mark
        option_stop
        option_target
        underlying_price
        current_underlying_price
        monitoring_price_type = OPTION_PREMIUM
        price_review_basis = OPTION_PREMIUM_ONLY
    - For stock positions:
        current_price remains underlying/stock price.
    - For option positions:
        current_price is intentionally overwritten with premium-safe value,
        not underlying price.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import math

from engine.paper_portfolio import show_positions, replace_position
from engine.close_trade import close_position


OPTION_CONTRACT_MULTIPLIER = 100

VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"

ACTION_HOLD = "HOLD"
ACTION_STOP_LOSS = "STOP_LOSS"
ACTION_TAKE_PROFIT = "TAKE_PROFIT"
ACTION_CUT_WEAKNESS = "CUT_WEAKNESS"
ACTION_PROTECT_PROFIT = "PROTECT_PROFIT"
ACTION_INVALID = "INVALID_MONITOR"

DEFAULT_OPTION_STOP_LOSS_PCT = 0.35
DEFAULT_OPTION_TARGET_GAIN_PCT = 0.60

DEFAULT_STOCK_STOP_LOSS_PCT = 0.03
DEFAULT_STOCK_TARGET_GAIN_PCT = 0.10

OPTION_UNDERLYING_LEAK_MULTIPLE = 8.0
OPTION_UNDERLYING_LEAK_ABSOLUTE = 25.0
MIN_VALID_OPTION_PREMIUM = 0.01


# =============================================================================
# Basic safe helpers
# =============================================================================

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return float(default)
        if isinstance(value, bool):
            return float(default)
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return float(default)
            value = cleaned
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return float(default)
        return number
    except Exception:
        return float(default)


def _safe_optional_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return None
            value = cleaned
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return number
    except Exception:
        return None


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return int(default)
        if isinstance(value, bool):
            return int(default)
        if isinstance(value, str):
            cleaned = value.replace(",", "").strip()
            if cleaned == "":
                return int(default)
            value = cleaned
        return int(float(value))
    except Exception:
        return int(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value if value is not None else "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "").upper()


def _upper(value: Any, default: str = "") -> str:
    text = _safe_str(value, default).upper()
    return text or default


def _first_float(payload: Dict[str, Any], keys: List[str]) -> Optional[float]:
    for key in keys:
        value = _safe_optional_float(payload.get(key))
        if value is not None:
            return value
    return None


def _first_str(payload: Dict[str, Any], keys: List[str], default: str = "") -> str:
    for key in keys:
        value = payload.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


# =============================================================================
# Position shape helpers
# =============================================================================

def _vehicle(pos: Dict[str, Any]) -> str:
    raw = _upper(
        pos.get(
            "vehicle_selected",
            pos.get(
                "selected_vehicle",
                pos.get("vehicle", pos.get("asset_type", pos.get("instrument_type", "STOCK"))),
            ),
        ),
        "STOCK",
    )

    if raw in {"OPTION", "OPTIONS", "OPT"}:
        return VEHICLE_OPTION

    if raw in {"STOCK", "EQUITY", "SHARE", "SHARES"}:
        return VEHICLE_STOCK

    if raw in {"RESEARCH_ONLY", "RESEARCH"}:
        return VEHICLE_RESEARCH_ONLY

    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))

    contract_symbol = _first_str(
        pos,
        ["contract_symbol", "option_symbol", "option_contract_symbol", "selected_contract_symbol"],
        "",
    )

    if option or contract_symbol or contract:
        return VEHICLE_OPTION

    return VEHICLE_STOCK


def _strategy(pos: Dict[str, Any]) -> str:
    return _upper(pos.get("strategy", pos.get("direction", pos.get("side", "CALL"))), "CALL")


def _direction(strategy: str) -> str:
    strategy = _upper(strategy, "CALL")
    if "PUT" in strategy or "SHORT" in strategy:
        return "SHORT"
    return "LONG"


def _days_open(opened_at: Any) -> float:
    try:
        if not opened_at:
            return 0.0

        raw = str(opened_at).strip()
        if raw.endswith("Z"):
            raw = raw.replace("Z", "+00:00")

        dt = datetime.fromisoformat(raw)

        if dt.tzinfo is None:
            now = datetime.now()
        else:
            now = datetime.now(dt.tzinfo)

        return max((now - dt).total_seconds() / 86400.0, 0.0)
    except Exception:
        return 0.0


def _position_identifier(pos: Dict[str, Any]) -> str:
    return _safe_str(
        pos.get(
            "trade_id",
            pos.get("position_id", pos.get("id", pos.get("order_id", ""))),
        ),
        "",
    )


# =============================================================================
# Option contract extraction
# =============================================================================

def _extract_contract(pos: Dict[str, Any]) -> Dict[str, Any]:
    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))

    merged: Dict[str, Any] = {}
    merged.update(contract)
    merged.update(option)

    contract_symbol = (
        _first_str(
            pos,
            [
                "contract_symbol",
                "option_symbol",
                "option_contract_symbol",
                "selected_contract_symbol",
                "occ_symbol",
            ],
            "",
        )
        or _first_str(
            merged,
            [
                "contractSymbol",
                "contract_symbol",
                "option_symbol",
                "symbol",
                "occ_symbol",
                "selected_contract_symbol",
            ],
            "",
        )
    )

    expiry = (
        _first_str(
            pos,
            ["expiry", "expiration", "expiration_date", "contract_expiry"],
            "",
        )
        or _first_str(
            merged,
            ["expiration", "expiry", "expiration_date", "contract_expiry"],
            "",
        )
    )

    right = _upper(
        _first_str(
            pos,
            ["right", "option_type", "call_put", "contract_right"],
            "",
        )
        or _first_str(
            merged,
            ["right", "option_type", "call_put", "contract_right"],
            "",
        ),
        "",
    )

    if right in {"C", "CALLS"}:
        right = "CALL"
    elif right in {"P", "PUTS"}:
        right = "PUT"

    strike = _first_float(pos, ["strike", "strike_price", "contract_strike"])
    if strike is None:
        strike = _first_float(merged, ["strike", "strike_price", "contract_strike"])

    bid = _first_float(pos, ["option_bid", "bid"])
    if bid is None:
        bid = _first_float(merged, ["bid"])

    ask = _first_float(pos, ["option_ask", "ask"])
    if ask is None:
        ask = _first_float(merged, ["ask"])

    last = _first_float(pos, ["option_last", "last"])
    if last is None:
        last = _first_float(merged, ["last", "last_price"])

    mark = _first_float(
        pos,
        [
            "current_option_mark",
            "option_current_mark",
            "option_mark",
            "mark",
            "current_premium",
            "premium_current",
        ],
    )
    if mark is None:
        mark = _first_float(
            merged,
            [
                "current_option_mark",
                "option_current_mark",
                "option_mark",
                "current_mark",
                "mark",
                "mid",
                "selected_price_reference",
                "price_reference",
            ],
        )

    return {
        "contract_symbol": contract_symbol,
        "expiry": expiry,
        "expiration": expiry,
        "right": right,
        "strike": strike,
        "bid": bid,
        "ask": ask,
        "last": last,
        "mark": mark,
        "volume": _safe_int(pos.get("volume", merged.get("volume")), 0),
        "open_interest": _safe_int(
            pos.get("open_interest", merged.get("open_interest", merged.get("oi"))),
            0,
        ),
        "contract_score": _safe_float(
            pos.get("contract_score", merged.get("contract_score")),
            0.0,
        ),
        "monitoring_mode": _safe_str(
            pos.get("monitoring_mode", merged.get("monitoring_mode")),
            "OPTION_PREMIUM",
        ),
        "price_reference": _safe_float(
            pos.get("price_reference", merged.get("price_reference", merged.get("selected_price_reference"))),
            0.0,
        ),
    }


def _mid_from_bid_ask(bid: Optional[float], ask: Optional[float]) -> Optional[float]:
    if bid is None or ask is None:
        return None
    if bid <= 0 or ask <= 0:
        return None
    if ask < bid:
        return None
    return round((bid + ask) / 2.0, 4)


# =============================================================================
# Price basis helpers
# =============================================================================

def _underlying_price(pos: Dict[str, Any]) -> Optional[float]:
    return _first_float(
        pos,
        [
            "underlying_price",
            "current_underlying_price",
            "stock_price",
            "underlying_last",
            "underlying_mark",
            "spot_price",
            "last_underlying_price",
        ],
    )


def _looks_like_underlying_leak(
    option_entry: Optional[float],
    candidate_current: Optional[float],
    underlying_price: Optional[float],
) -> bool:
    if candidate_current is None:
        return False

    if underlying_price is not None and underlying_price > 0:
        tolerance = max(0.05, underlying_price * 0.002)
        if abs(candidate_current - underlying_price) <= tolerance:
            return True

    if option_entry is not None and option_entry > 0:
        if (
            candidate_current >= OPTION_UNDERLYING_LEAK_ABSOLUTE
            and candidate_current >= option_entry * OPTION_UNDERLYING_LEAK_MULTIPLE
        ):
            return True

    return False


def _option_entry_premium(pos: Dict[str, Any]) -> Optional[float]:
    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))

    # For options, entry/entry_price may be valid legacy premium fields.
    value = _first_float(
        pos,
        [
            "entry_premium",
            "premium_entry",
            "option_entry",
            "option_entry_price",
            "entry_option_mark",
            "contract_entry_price",
            "fill_premium",
            "average_premium",
            "avg_premium",
            "debit",
            "price_paid",
            "entry",
            "entry_price",
            "fill_price",
            "executed_price",
        ],
    )

    if value is not None and value > 0:
        return value

    value = _first_float(
        option,
        [
            "entry_premium",
            "premium_entry",
            "option_entry",
            "entry_price",
            "premium",
            "mark_at_entry",
            "fill_price",
            "executed_price",
            "selected_price_reference",
            "price_reference",
            "mark",
            "ask",
            "last",
        ],
    )

    if value is not None and value > 0:
        return value

    value = _first_float(
        contract,
        [
            "entry_premium",
            "premium_entry",
            "option_entry",
            "entry_price",
            "selected_price_reference",
            "price_reference",
            "mark",
            "ask",
            "last",
        ],
    )

    if value is not None and value > 0:
        return value

    return None


def _latest_option_price(pos: Dict[str, Any]) -> Tuple[float, str, bool]:
    """
    Returns:
        premium, source, leak_blocked

    This function must never blindly trust current_price for options.
    """
    option = _safe_dict(pos.get("option"))
    contract_obj = _safe_dict(pos.get("contract"))
    contract = _extract_contract(pos)

    entry = _option_entry_premium(pos)
    underlying = _underlying_price(pos)

    candidates: List[Tuple[str, Optional[float]]] = [
        ("current_option_mark", _safe_optional_float(pos.get("current_option_mark"))),
        ("option_current_mark", _safe_optional_float(pos.get("option_current_mark"))),
        ("option_mark", _safe_optional_float(pos.get("option_mark"))),
        ("current_premium", _safe_optional_float(pos.get("current_premium"))),
        ("premium_current", _safe_optional_float(pos.get("premium_current"))),
        ("option_current_price", _safe_optional_float(pos.get("option_current_price"))),
        ("current_option_price", _safe_optional_float(pos.get("current_option_price"))),
        ("contract_mark", _safe_optional_float(pos.get("contract_mark"))),
        ("mark_price", _safe_optional_float(pos.get("mark_price"))),

        ("option.mark", _safe_optional_float(option.get("mark"))),
        ("option.current_mark", _safe_optional_float(option.get("current_mark"))),
        ("option.selected_price_reference", _safe_optional_float(option.get("selected_price_reference"))),
        ("option.price_reference", _safe_optional_float(option.get("price_reference"))),
        ("option.last", _safe_optional_float(option.get("last"))),
        ("option.last_price", _safe_optional_float(option.get("last_price"))),

        ("contract.mark", _safe_optional_float(contract_obj.get("mark"))),
        ("contract.selected_price_reference", _safe_optional_float(contract_obj.get("selected_price_reference"))),
        ("contract.price_reference", _safe_optional_float(contract_obj.get("price_reference"))),
        ("contract.last", _safe_optional_float(contract_obj.get("last"))),
        ("contract.last_price", _safe_optional_float(contract_obj.get("last_price"))),

        ("extracted_contract.mark", _safe_optional_float(contract.get("mark"))),
        ("extracted_contract.price_reference", _safe_optional_float(contract.get("price_reference"))),
        ("extracted_contract.last", _safe_optional_float(contract.get("last"))),
    ]

    for source, value in candidates:
        if value is None or value < MIN_VALID_OPTION_PREMIUM:
            continue

        if _looks_like_underlying_leak(entry, value, underlying):
            continue

        return round(value, 4), source, False

    bid = contract.get("bid")
    ask = contract.get("ask")
    mid = _mid_from_bid_ask(bid, ask)
    if mid is not None and mid >= MIN_VALID_OPTION_PREMIUM:
        if not _looks_like_underlying_leak(entry, mid, underlying):
            return round(mid, 4), "bid_ask_midpoint", False

    # Legacy current_price is last resort only.
    legacy_current = _safe_optional_float(pos.get("current_price"))
    if legacy_current is not None and legacy_current >= MIN_VALID_OPTION_PREMIUM:
        if _looks_like_underlying_leak(entry, legacy_current, underlying):
            fallback = entry if entry is not None else 0.0
            return round(fallback, 4), "blocked_legacy_current_price_underlying_leak", True

        return round(legacy_current, 4), "safe_legacy_current_price", False

    if entry is not None and entry >= MIN_VALID_OPTION_PREMIUM:
        return round(entry, 4), "entry_premium_fallback", False

    return 0.0, "missing_option_premium", False


def _latest_stock_price(pos: Dict[str, Any]) -> Tuple[float, str]:
    for source, value in [
        ("current_price", pos.get("current_price")),
        ("current_underlying_price", pos.get("current_underlying_price")),
        ("underlying_price", pos.get("underlying_price")),
        ("market_price", pos.get("market_price")),
        ("stock_price", pos.get("stock_price")),
        ("price", pos.get("price")),
        ("entry", pos.get("entry")),
        ("entry_price", pos.get("entry_price")),
    ]:
        price = _safe_float(value, 0.0)
        if price > 0:
            return round(price, 4), source
    return 0.0, "missing_stock_price"


def _stock_entry_price(pos: Dict[str, Any]) -> float:
    return _safe_float(
        pos.get(
            "entry",
            pos.get(
                "entry_price",
                pos.get("avg_entry", pos.get("average_entry", pos.get("fill_price", pos.get("price", 0.0)))),
            ),
        ),
        0.0,
    )


# =============================================================================
# Stop / target defaults
# =============================================================================

def _normalize_option_stop_target(
    pos: Dict[str, Any],
    entry: float,
    direction: str,
    current: float,
) -> Tuple[float, float, List[str]]:
    notes: List[str] = []
    underlying = _underlying_price(pos)

    raw_stop = _first_float(
        pos,
        [
            "option_stop",
            "premium_stop",
            "stop_premium",
            "contract_stop",
            "stop_loss_premium",
            "stop",
            "stop_loss",
        ],
    )

    raw_target = _first_float(
        pos,
        [
            "option_target",
            "premium_target",
            "target_premium",
            "contract_target",
            "take_profit_premium",
            "target",
            "take_profit",
        ],
    )

    stop = raw_stop
    target = raw_target

    if stop is not None and _looks_like_underlying_leak(entry, stop, underlying):
        notes.append("ignored_stop_underlying_leak")
        stop = None

    if target is not None and _looks_like_underlying_leak(entry, target, underlying):
        notes.append("ignored_target_underlying_leak")
        target = None

    if entry <= 0:
        entry = current

    if direction == "SHORT":
        # Long put premium still profits when premium rises.
        # We monitor bought options as premium-long instruments.
        stop_default = entry * (1.0 - DEFAULT_OPTION_STOP_LOSS_PCT)
        target_default = entry * (1.0 + DEFAULT_OPTION_TARGET_GAIN_PCT)
    else:
        stop_default = entry * (1.0 - DEFAULT_OPTION_STOP_LOSS_PCT)
        target_default = entry * (1.0 + DEFAULT_OPTION_TARGET_GAIN_PCT)

    if stop is None or stop <= 0:
        stop = stop_default
        notes.append("rebuilt_option_stop_from_entry_premium")

    if target is None or target <= 0:
        target = target_default
        notes.append("rebuilt_option_target_from_entry_premium")

    stop = round(max(0.01, stop), 4)
    target = round(max(0.01, target), 4)

    return stop, target, notes


def _normalize_stock_stop_target(
    pos: Dict[str, Any],
    entry: float,
    direction: str,
    current: float,
) -> Tuple[float, float, List[str]]:
    notes: List[str] = []

    stop = _first_float(pos, ["stop", "stop_loss", "stock_stop"])
    target = _first_float(pos, ["target", "take_profit", "stock_target"])

    if entry <= 0:
        entry = current

    if direction == "SHORT":
        stop_default = entry * (1.0 + DEFAULT_STOCK_STOP_LOSS_PCT)
        target_default = entry * (1.0 - DEFAULT_STOCK_TARGET_GAIN_PCT)
    else:
        stop_default = entry * (1.0 - DEFAULT_STOCK_STOP_LOSS_PCT)
        target_default = entry * (1.0 + DEFAULT_STOCK_TARGET_GAIN_PCT)

    if stop is None or stop <= 0:
        stop = stop_default
        notes.append("rebuilt_stock_stop_from_entry_price")

    if target is None or target <= 0:
        target = target_default
        notes.append("rebuilt_stock_target_from_entry_price")

    return round(stop, 4), round(target, 4), notes


# =============================================================================
# Position normalization
# =============================================================================

def _ensure_monitor_defaults(pos: Dict[str, Any]) -> Dict[str, Any]:
    pos = dict(pos)
    vehicle = _vehicle(pos)

    if vehicle == VEHICLE_RESEARCH_ONLY:
        pos["monitoring_price_type"] = "RESEARCH_ONLY"
        pos["price_review_basis"] = "NO_POSITION"
        pos["monitor_ready"] = False
        return pos

    strategy = _strategy(pos)
    direction = _direction(strategy)

    if vehicle == VEHICLE_OPTION:
        contract = _extract_contract(pos)

        entry = _option_entry_premium(pos)
        current, source, leak_blocked = _latest_option_price(pos)

        if entry is None or entry <= 0:
            entry = current

        if current <= 0 and entry and entry > 0:
            current = round(entry, 4)
            source = "entry_premium_final_fallback"

        stop, target, stop_target_notes = _normalize_option_stop_target(
            pos,
            float(entry or 0.0),
            direction,
            current,
        )

        underlying = _underlying_price(pos)

        contracts = _safe_int(
            pos.get(
                "contracts",
                pos.get("contract_count", pos.get("quantity", pos.get("qty", 1))),
            ),
            1,
        )
        contracts = max(1, contracts)

        entry = round(float(entry or 0.0), 4)
        current = round(float(current or 0.0), 4)

        pnl = round((current - entry) * OPTION_CONTRACT_MULTIPLIER * contracts, 2) if entry > 0 and current > 0 else 0.0
        pnl_pct = round(((current - entry) / entry) * 100.0, 4) if entry > 0 and current > 0 else 0.0

        pos["vehicle"] = VEHICLE_OPTION
        pos["vehicle_selected"] = VEHICLE_OPTION

        # Canonical option fields
        pos["entry_premium"] = entry
        pos["premium_entry"] = entry
        pos["current_premium"] = current
        pos["premium_current"] = current
        pos["current_option_mark"] = current
        pos["option_current_price"] = current
        pos["option_stop"] = stop
        pos["premium_stop"] = stop
        pos["option_target"] = target
        pos["premium_target"] = target

        # Compatibility fields, intentionally premium-safe for options
        pos["entry"] = entry
        pos["entry_price"] = entry
        pos["current_price"] = current
        pos["stop"] = stop
        pos["target"] = target

        # Underlying context only
        if underlying is not None and underlying > 0:
            pos["underlying_price"] = round(underlying, 4)
            pos["current_underlying_price"] = round(underlying, 4)

        # Contract preservation
        if contract.get("contract_symbol"):
            pos["contract_symbol"] = contract.get("contract_symbol")
            pos["option_symbol"] = contract.get("contract_symbol")
        if contract.get("expiry"):
            pos["expiry"] = contract.get("expiry")
            pos["expiration"] = contract.get("expiry")
        if contract.get("strike") is not None:
            pos["strike"] = contract.get("strike")
        if contract.get("right"):
            pos["right"] = contract.get("right")

        pos["contracts"] = contracts
        pos["monitoring_price_type"] = "OPTION_PREMIUM"
        pos["price_review_basis"] = "OPTION_PREMIUM_ONLY"
        pos["underlying_price_used_for_close_decision"] = False
        pos["option_price_source"] = source
        pos["option_underlying_leak_blocked"] = bool(leak_blocked)
        pos["monitor_ready"] = entry > 0 and current > 0

        pos["unrealized_pnl"] = pnl
        pos["unrealized_pnl_pct"] = pnl_pct
        pos["pnl_basis"] = "option_premium_x_100"

        pos["monitor_normalization_notes"] = stop_target_notes

        return pos

    # Stock path
    entry = _stock_entry_price(pos)
    current, source = _latest_stock_price(pos)

    if current <= 0:
        current = entry

    if entry <= 0:
        entry = current

    stop, target, stop_target_notes = _normalize_stock_stop_target(pos, entry, direction, current)

    shares = _safe_int(pos.get("shares", pos.get("quantity", pos.get("qty", 1))), 1)
    shares = max(1, shares)

    entry = round(entry, 4)
    current = round(current, 4)

    if direction == "SHORT":
        pnl = round((entry - current) * shares, 2) if entry > 0 and current > 0 else 0.0
        pnl_pct = round(((entry - current) / entry) * 100.0, 4) if entry > 0 and current > 0 else 0.0
    else:
        pnl = round((current - entry) * shares, 2) if entry > 0 and current > 0 else 0.0
        pnl_pct = round(((current - entry) / entry) * 100.0, 4) if entry > 0 and current > 0 else 0.0

    pos["vehicle"] = VEHICLE_STOCK
    pos["vehicle_selected"] = VEHICLE_STOCK

    pos["entry"] = entry
    pos["entry_price"] = entry
    pos["current_price"] = current
    pos["underlying_price"] = current
    pos["current_underlying_price"] = current
    pos["stop"] = stop
    pos["target"] = target
    pos["shares"] = shares

    pos["monitoring_price_type"] = "UNDERLYING"
    pos["price_review_basis"] = "STOCK_PRICE"
    pos["underlying_price_used_for_close_decision"] = True
    pos["stock_price_source"] = source
    pos["monitor_ready"] = entry > 0 and current > 0

    pos["unrealized_pnl"] = pnl
    pos["unrealized_pnl_pct"] = pnl_pct
    pos["pnl_basis"] = "stock_price_x_shares"

    pos["monitor_normalization_notes"] = stop_target_notes

    return pos


# =============================================================================
# Action logic
# =============================================================================

def _pct_change(entry: float, current: float, strategy: str, vehicle: str) -> float:
    if entry <= 0 or current <= 0:
        return 0.0

    if vehicle == VEHICLE_OPTION:
        # Bought calls and bought puts both profit when premium rises.
        return round(((current - entry) / entry) * 100.0, 4)

    direction = _direction(strategy)

    if direction == "SHORT":
        return round(((entry - current) / entry) * 100.0, 4)

    return round(((current - entry) / entry) * 100.0, 4)


def _progress(entry: float, current: float, stop: float, target: float, strategy: str, vehicle: str) -> float:
    if entry <= 0 or current <= 0:
        return 0.0

    try:
        if vehicle == VEHICLE_OPTION:
            denominator = target - entry
            if denominator == 0:
                return 0.0
            return round((current - entry) / denominator, 4)

        direction = _direction(strategy)

        if direction == "SHORT":
            denominator = entry - target
            if denominator == 0:
                return 0.0
            return round((entry - current) / denominator, 4)

        denominator = target - entry
        if denominator == 0:
            return 0.0
        return round((current - entry) / denominator, 4)
    except Exception:
        return 0.0


def _action_for_position(pos: Dict[str, Any]) -> str:
    vehicle = _vehicle(pos)

    if vehicle == VEHICLE_RESEARCH_ONLY:
        return ACTION_HOLD

    strategy = _strategy(pos)
    direction = _direction(strategy)

    entry = _safe_float(pos.get("entry", 0.0), 0.0)
    current = _safe_float(pos.get("current_price", 0.0), 0.0)
    stop = _safe_float(pos.get("stop", 0.0), 0.0)
    target = _safe_float(pos.get("target", 0.0), 0.0)
    days_open = _days_open(pos.get("opened_at", pos.get("timestamp", pos.get("created_at"))))
    pct = _pct_change(entry, current, strategy, vehicle)

    if entry <= 0 or current <= 0:
        return ACTION_INVALID

    if vehicle == VEHICLE_OPTION:
        # Bought options are premium-long instruments.
        stop_hit = current <= stop if stop > 0 else False
        target_hit = current >= target if target > 0 else False

        if stop_hit:
            return ACTION_STOP_LOSS

        # Small anti-fake-close buffer remains.
        # Prevents same-moment closes from immediate stale entry/current writes.
        if target_hit and days_open >= 0.01:
            return ACTION_TAKE_PROFIT

        if pct <= -35:
            return ACTION_CUT_WEAKNESS

        if pct >= 45 and days_open >= 0.01:
            return ACTION_PROTECT_PROFIT

        return ACTION_HOLD

    # Stock path
    if direction == "SHORT":
        stop_hit = current >= stop if stop > 0 else False
        target_hit = current <= target if target > 0 else False
    else:
        stop_hit = current <= stop if stop > 0 else False
        target_hit = current >= target if target > 0 else False

    if stop_hit:
        return ACTION_STOP_LOSS

    if target_hit and days_open >= 0.01:
        return ACTION_TAKE_PROFIT

    if pct <= -1.5:
        return ACTION_CUT_WEAKNESS

    if pct >= 3.0 and days_open >= 0.01:
        return ACTION_PROTECT_PROFIT

    return ACTION_HOLD


def _close_reason_from_action(action: str) -> str:
    action = _upper(action, ACTION_HOLD)
    mapping = {
        ACTION_STOP_LOSS: "stop_loss",
        ACTION_TAKE_PROFIT: "take_profit",
        ACTION_CUT_WEAKNESS: "cut_weakness",
        ACTION_PROTECT_PROFIT: "protect_profit",
        ACTION_INVALID: "invalid_monitor",
    }
    return mapping.get(action, action.lower())


def _should_attempt_close(action: str) -> bool:
    return action in {
        ACTION_STOP_LOSS,
        ACTION_TAKE_PROFIT,
        ACTION_CUT_WEAKNESS,
        ACTION_PROTECT_PROFIT,
    }


def _close_price_for_position(pos: Dict[str, Any]) -> float:
    vehicle = _vehicle(pos)

    if vehicle == VEHICLE_OPTION:
        # For options, this must be premium.
        return _safe_float(
            pos.get(
                "current_premium",
                pos.get("current_option_mark", pos.get("option_current_price", pos.get("current_price", 0.0))),
            ),
            0.0,
        )

    return _safe_float(pos.get("current_price", 0.0), 0.0)


# =============================================================================
# Public monitor
# =============================================================================

def monitor_open_positions() -> List[Dict[str, Any]]:
    try:
        positions = show_positions()
    except Exception:
        positions = []

    actions: List[Dict[str, Any]] = []

    for raw_pos in positions if isinstance(positions, list) else []:
        if not isinstance(raw_pos, dict):
            continue

        pos = _ensure_monitor_defaults(raw_pos)

        symbol = _norm_symbol(pos.get("symbol"))
        trade_id = _position_identifier(pos)
        vehicle = _vehicle(pos)
        strategy = _strategy(pos)

        entry = _safe_float(pos.get("entry", 0.0), 0.0)
        current = _safe_float(pos.get("current_price", 0.0), 0.0)
        stop = _safe_float(pos.get("stop", 0.0), 0.0)
        target = _safe_float(pos.get("target", 0.0), 0.0)

        action = _action_for_position(pos)
        pct = _pct_change(entry, current, strategy, vehicle)
        progress = _progress(entry, current, stop, target, strategy, vehicle)

        close_price = _close_price_for_position(pos)

        pos["last_monitored_at"] = _now_iso()
        pos["monitor_action"] = action
        pos["monitor_close_price"] = close_price
        pos["monitor_close_price_basis"] = pos.get("price_review_basis", "")
        pos["monitor_debug"] = {
            "symbol": symbol,
            "trade_id": trade_id,
            "vehicle_selected": vehicle,
            "strategy": strategy,
            "monitoring_price_type": pos.get("monitoring_price_type", ""),
            "price_review_basis": pos.get("price_review_basis", ""),
            "entry": round(entry, 4),
            "current": round(current, 4),
            "stop": round(stop, 4),
            "target": round(target, 4),
            "underlying_price": pos.get("underlying_price"),
            "current_underlying_price": pos.get("current_underlying_price"),
            "current_premium": pos.get("current_premium"),
            "current_option_mark": pos.get("current_option_mark"),
            "option_price_source": pos.get("option_price_source", ""),
            "option_underlying_leak_blocked": bool(pos.get("option_underlying_leak_blocked", False)),
            "days_open": round(
                _days_open(pos.get("opened_at", pos.get("timestamp", pos.get("created_at")))),
                4,
            ),
            "pct_change": pct,
            "progress_to_target": progress,
            "unrealized_pnl": pos.get("unrealized_pnl", 0.0),
            "unrealized_pnl_pct": pos.get("unrealized_pnl_pct", 0.0),
            "pnl_basis": pos.get("pnl_basis", ""),
            "final_action": action,
        }

        if symbol:
            replace_position(symbol, pos)

        if vehicle == VEHICLE_OPTION:
            print(
                f"{symbol} | Vehicle: {vehicle} | MonitorPrice: {pos.get('monitoring_price_type', '')} | "
                f"PremiumCurrent: {round(current, 4)} | EntryPremium: {round(entry, 4)} | "
                f"PremiumStop: {round(stop, 4)} | PremiumTarget: {round(target, 4)} | "
                f"UnderlyingContext: {pos.get('underlying_price')} | Action: {action}"
            )
        else:
            print(
                f"{symbol} | Vehicle: {vehicle} | MonitorPrice: {pos.get('monitoring_price_type', '')} | "
                f"Current: {round(current, 4)} | Entry: {round(entry, 4)} | Stop: {round(stop, 4)} | "
                f"Target: {round(target, 4)} | Action: {action}"
            )

        if _should_attempt_close(action):
            if close_price <= 0:
                actions.append(
                    {
                        "symbol": symbol,
                        "trade_id": trade_id,
                        "vehicle": vehicle,
                        "reason": _close_reason_from_action(action),
                        "blocked": True,
                        "blocked_reason": "missing_valid_close_price",
                        "price_review_basis": pos.get("price_review_basis"),
                    }
                )
                print(f"BLOCKED CLOSE: {symbol} | Reason: missing_valid_close_price")
                continue

            result = close_position(
                symbol,
                close_price,
                reason=_close_reason_from_action(action),
                trade_id=trade_id,
            )

            action_payload = {
                "symbol": symbol,
                "trade_id": trade_id,
                "vehicle": vehicle,
                "reason": _close_reason_from_action(action),
                "close_price": close_price,
                "price_review_basis": pos.get("price_review_basis", ""),
                "monitoring_price_type": pos.get("monitoring_price_type", ""),
                "underlying_price_used_for_close_decision": bool(
                    pos.get("underlying_price_used_for_close_decision", vehicle != VEHICLE_OPTION)
                ),
                "result": result,
            }

            actions.append(action_payload)

            if isinstance(result, dict) and result.get("closed"):
                print(
                    f"CLOSED: {symbol} | Vehicle: {vehicle} | Reason: {action} | "
                    f"ClosePrice: {close_price} | Basis: {pos.get('price_review_basis')} | "
                    f"PnL: {result.get('pnl')}"
                )
            elif isinstance(result, dict) and result.get("blocked"):
                print(f"BLOCKED CLOSE: {symbol} | Reason: {result.get('reason')}")
            else:
                print(f"CLOSE RESULT: {symbol} | {result}")

    return actions


# Compatibility aliases
run_position_monitor = monitor_open_positions
monitor_positions = monitor_open_positions


if __name__ == "__main__":
    monitor_open_positions()
