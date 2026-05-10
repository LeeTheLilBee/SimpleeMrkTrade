from __future__ import annotations

"""
🔭 Observatory Position Review

Canonical role:
    Reviews open positions and decides whether each one should HOLD, STOP_LOSS,
    TAKE_PROFIT, CUT_WEAKNESS, or PROTECT_PROFIT.

Important compatibility:
    Older notebook runners may call review_open_positions().
    Some later runners may call run_position_review() or position_review().
    This file keeps all of those aliases.

Option safety:
    OPTION positions are reviewed using option premium only.
    Underlying stock price is context only and must never trigger an option close.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import math

from engine.paper_portfolio import show_positions
from engine.data_utils import safe_download
from engine.exit_review import review_exit
from engine.close_trade import close_position


OPTION_CONTRACT_MULTIPLIER = 100

VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"
VEHICLE_UNKNOWN = "UNKNOWN"

ACTION_HOLD = "HOLD"
ACTION_STOP_LOSS = "STOP_LOSS"
ACTION_TAKE_PROFIT = "TAKE_PROFIT"
ACTION_CUT_WEAKNESS = "CUT_WEAKNESS"
ACTION_PROTECT_PROFIT = "PROTECT_PROFIT"
ACTION_INVALID = "INVALID_REVIEW"

MIN_VALID_OPTION_PREMIUM = 0.01
OPTION_UNDERLYING_LEAK_MULTIPLE = 8.0
OPTION_UNDERLYING_LEAK_ABSOLUTE = 25.0

# Prevents same-moment test/open positions from instantly taking profit
# because option marks can move immediately after creation.
SAME_MOMENT_CLOSE_GRACE_DAYS = 0.01

# Fresh-option behavior gate:
# A normal profit target should not close a brand-new paper option too quickly.
# This prevents the review layer from turning healthy execution tests into instant churn.
FRESH_OPTION_TAKE_PROFIT_GRACE_DAYS = 0.125      # 3 hours
FRESH_OPTION_PROTECT_PROFIT_GRACE_DAYS = 0.25    # 6 hours
EXTREME_OPTION_PROFIT_EXIT_PCT = 250.0           # allow urgent win capture
SUSPICIOUS_FRESH_OPTION_JUMP_PCT = 500.0         # hold + flag unless later confirmed


# =============================================================================
# SAFE HELPERS
# =============================================================================

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return float(default)

        if isinstance(value, str):
            value = value.replace("$", "").replace(",", "").strip()
            if value == "":
                return float(default)

        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return float(default)

        return number
    except Exception:
        return float(default)


def _safe_optional_float(value: Any) -> Optional[float]:
    try:
        if value is None or isinstance(value, bool):
            return None

        if isinstance(value, str):
            value = value.replace("$", "").replace(",", "").strip()
            if value == "":
                return None

        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None

        return number
    except Exception:
        return None


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or isinstance(value, bool):
            return int(default)

        if isinstance(value, str):
            value = value.replace(",", "").strip()
            if value == "":
                return int(default)

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


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _upper(value: Any, default: str = "") -> str:
    return _safe_str(value, default).upper()


def _norm_symbol(value: Any) -> str:
    return _upper(value, "")


def _first_float(payload: Dict[str, Any], keys: List[str]) -> Optional[float]:
    payload = _safe_dict(payload)

    for key in keys:
        value = _safe_optional_float(payload.get(key))
        if value is not None:
            return value

    return None


def _first_str(payload: Dict[str, Any], keys: List[str], default: str = "") -> str:
    payload = _safe_dict(payload)

    for key in keys:
        value = payload.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()

    return default


# =============================================================================
# POSITION DETECTION
# =============================================================================

def _vehicle(pos: Dict[str, Any]) -> str:
    pos = _safe_dict(pos)

    raw = _upper(
        pos.get(
            "vehicle_selected",
            pos.get(
                "selected_vehicle",
                pos.get(
                    "vehicle",
                    pos.get("asset_type", pos.get("instrument_type", "")),
                ),
            ),
        ),
        "",
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
        [
            "contract_symbol",
            "option_symbol",
            "option_contract_symbol",
            "selected_contract_symbol",
            "contractSymbol",
            "occ_symbol",
        ],
        "",
    )

    right = _upper(
        _first_str(pos, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_str(option, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_str(contract, ["right", "option_type", "call_put", "contract_right"], ""),
        "",
    )

    contracts = _safe_int(pos.get("contracts", pos.get("contract_count", 0)), 0)
    shares = _safe_int(pos.get("shares", pos.get("quantity", 0)), 0)

    if option or contract or contract_symbol or right in {"CALL", "PUT", "C", "P"} or contracts > 0:
        if shares <= 0 or contracts > 0:
            return VEHICLE_OPTION

    if shares > 0:
        return VEHICLE_STOCK

    return VEHICLE_STOCK


def _strategy(pos: Dict[str, Any]) -> str:
    return _upper(
        pos.get("strategy", pos.get("direction", pos.get("side", "CALL"))),
        "CALL",
    )


def _direction(strategy: str) -> str:
    strategy = _upper(strategy, "CALL")

    if "PUT" in strategy or "SHORT" in strategy:
        return "SHORT"

    return "LONG"


def _trade_id(pos: Dict[str, Any]) -> str:
    return _safe_str(
        pos.get(
            "trade_id",
            pos.get("position_id", pos.get("id", pos.get("order_id", ""))),
        ),
        "",
    )


def _days_open(opened_at: Any) -> float:
    try:
        if not opened_at:
            return 0.0

        raw = str(opened_at).strip()
        if raw.endswith("Z"):
            raw = raw.replace("Z", "+00:00")

        dt = datetime.fromisoformat(raw)
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()

        return max((now - dt).total_seconds() / 86400.0, 0.0)
    except Exception:
        return 0.0


# =============================================================================
# CONTRACT / PRICE EXTRACTION
# =============================================================================

def _extract_contract(pos: Dict[str, Any]) -> Dict[str, Any]:
    pos = _safe_dict(pos)

    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))
    selected_contract = _safe_dict(pos.get("selected_contract"))
    best_option = _safe_dict(pos.get("best_option"))
    best_option_preview = _safe_dict(pos.get("best_option_preview"))

    out: Dict[str, Any] = {}
    out.update(best_option_preview)
    out.update(best_option)
    out.update(selected_contract)
    out.update(contract)
    out.update(option)

    contract_symbol = (
        _first_str(
            pos,
            [
                "contract_symbol",
                "option_symbol",
                "option_contract_symbol",
                "selected_contract_symbol",
                "contractSymbol",
                "occ_symbol",
            ],
            "",
        )
        or _first_str(
            out,
            [
                "contractSymbol",
                "contract_symbol",
                "option_symbol",
                "selected_contract_symbol",
                "occ_symbol",
            ],
            "",
        )
    )

    expiry = (
        _first_str(pos, ["expiry", "expiration", "expiration_date", "contract_expiry"], "")
        or _first_str(out, ["expiry", "expiration", "expiration_date", "contract_expiry"], "")
    )

    right = _upper(
        _first_str(pos, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_str(out, ["right", "option_type", "call_put", "contract_right"], ""),
        "",
    )

    if right == "C":
        right = "CALL"
    elif right == "P":
        right = "PUT"

    out["contract_symbol"] = contract_symbol
    out["contractSymbol"] = contract_symbol
    out["option_symbol"] = contract_symbol
    out["expiry"] = expiry
    out["expiration"] = expiry
    out["expiration_date"] = expiry
    out["right"] = right
    out["option_type"] = right
    out["call_put"] = right

    out["strike"] = (
        _first_float(pos, ["strike", "strike_price", "contract_strike"])
        or _first_float(out, ["strike", "strike_price", "contract_strike"])
    )

    out["bid"] = (
        _first_float(pos, ["option_bid", "bid"])
        or _first_float(out, ["bid"])
    )

    out["ask"] = (
        _first_float(pos, ["option_ask", "ask"])
        or _first_float(out, ["ask"])
    )

    out["last"] = (
        _first_float(pos, ["option_last", "last"])
        or _first_float(out, ["last", "last_price"])
    )

    out["mark"] = (
        _first_float(
            pos,
            [
                "current_option_mark",
                "option_current_mark",
                "option_mark",
                "mark",
                "current_premium",
                "premium_current",
                "option_current_price",
                "current_option_price",
            ],
        )
        or _first_float(
            out,
            [
                "current_option_mark",
                "option_current_mark",
                "current_mark",
                "mark",
                "mid",
                "selected_price_reference",
                "price_reference",
            ],
        )
    )

    out["price_reference"] = (
        _first_float(pos, ["price_reference", "selected_price_reference"])
        or _first_float(out, ["price_reference", "selected_price_reference"])
        or out.get("mark")
    )

    out["volume"] = _safe_int(pos.get("volume", pos.get("option_volume", out.get("volume"))), 0)
    out["open_interest"] = _safe_int(
        pos.get(
            "open_interest",
            pos.get("option_open_interest", out.get("open_interest", out.get("oi"))),
        ),
        0,
    )
    out["contract_score"] = _safe_float(
        pos.get("contract_score", pos.get("option_contract_score", out.get("contract_score"))),
        0.0,
    )

    return out


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
            "market_price",
        ],
    )


def _looks_like_underlying_leak(
    entry_premium: Optional[float],
    candidate: Optional[float],
    underlying: Optional[float],
) -> bool:
    if candidate is None:
        return False

    if underlying is not None and underlying > 0:
        tolerance = max(0.05, underlying * 0.002)
        if abs(candidate - underlying) <= tolerance:
            return True

    if entry_premium is not None and entry_premium > 0:
        if (
            candidate >= OPTION_UNDERLYING_LEAK_ABSOLUTE
            and candidate >= entry_premium * OPTION_UNDERLYING_LEAK_MULTIPLE
        ):
            return True

    return False


def _option_entry_premium(pos: Dict[str, Any]) -> Optional[float]:
    pos = _safe_dict(pos)

    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))
    underlying = _underlying_price(pos)

    candidates = [
        pos.get("entry_premium"),
        pos.get("premium_entry"),
        pos.get("option_entry"),
        pos.get("option_entry_price"),
        pos.get("entry_option_mark"),
        pos.get("contract_entry_price"),
        pos.get("fill_premium"),
        pos.get("average_premium"),
        pos.get("avg_premium"),
        pos.get("debit"),
        pos.get("price_paid"),
        pos.get("entry"),
        pos.get("entry_price"),
        pos.get("fill_price"),
        pos.get("executed_price"),
        option.get("entry_premium"),
        option.get("premium_entry"),
        option.get("entry_price"),
        option.get("mark_at_entry"),
        option.get("fill_price"),
        option.get("executed_price"),
        option.get("selected_price_reference"),
        option.get("price_reference"),
        option.get("mark"),
        contract.get("entry_premium"),
        contract.get("premium_entry"),
        contract.get("entry_price"),
        contract.get("selected_price_reference"),
        contract.get("price_reference"),
        contract.get("mark"),
    ]

    for value in candidates:
        price = _safe_optional_float(value)

        if price is None or price < MIN_VALID_OPTION_PREMIUM:
            continue

        if _looks_like_underlying_leak(None, price, underlying):
            continue

        return round(price, 4)

    return None


def _mid_from_bid_ask(bid: Optional[float], ask: Optional[float]) -> Optional[float]:
    if bid is None or ask is None:
        return None

    if bid <= 0 or ask <= 0:
        return None

    if ask < bid:
        return None

    return round((bid + ask) / 2.0, 4)


def _option_current_premium(pos: Dict[str, Any]) -> Tuple[float, str, bool]:
    pos = _safe_dict(pos)

    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))
    extracted = _extract_contract(pos)

    entry = _option_entry_premium(pos)
    underlying = _underlying_price(pos)
    leak_blocked = False

    candidates: List[Tuple[str, Any]] = [
        ("current_premium", pos.get("current_premium")),
        ("premium_current", pos.get("premium_current")),
        ("current_option_mark", pos.get("current_option_mark")),
        ("option_current_mark", pos.get("option_current_mark")),
        ("option_current_price", pos.get("option_current_price")),
        ("current_option_price", pos.get("current_option_price")),
        ("option_mark", pos.get("option_mark")),
        ("contract_mark", pos.get("contract_mark")),
        ("mark", pos.get("mark")),
        ("option.current_premium", option.get("current_premium")),
        ("option.premium_current", option.get("premium_current")),
        ("option.current_mark", option.get("current_mark")),
        ("option.option_mark", option.get("option_mark")),
        ("option.mark", option.get("mark")),
        ("option.selected_price_reference", option.get("selected_price_reference")),
        ("option.price_reference", option.get("price_reference")),
        ("option.last", option.get("last")),
        ("option.last_price", option.get("last_price")),
        ("contract.current_premium", contract.get("current_premium")),
        ("contract.current_mark", contract.get("current_mark")),
        ("contract.option_mark", contract.get("option_mark")),
        ("contract.mark", contract.get("mark")),
        ("contract.selected_price_reference", contract.get("selected_price_reference")),
        ("contract.price_reference", contract.get("price_reference")),
        ("contract.last", contract.get("last")),
        ("contract.last_price", contract.get("last_price")),
        ("extracted.mark", extracted.get("mark")),
        ("extracted.price_reference", extracted.get("price_reference")),
        ("extracted.last", extracted.get("last")),
    ]

    for source, value in candidates:
        price = _safe_optional_float(value)

        if price is None or price < MIN_VALID_OPTION_PREMIUM:
            continue

        if _looks_like_underlying_leak(entry, price, underlying):
            leak_blocked = True
            continue

        return round(price, 4), source, leak_blocked

    mid = _mid_from_bid_ask(
        _safe_optional_float(extracted.get("bid")),
        _safe_optional_float(extracted.get("ask")),
    )

    if mid is not None:
        if _looks_like_underlying_leak(entry, mid, underlying):
            leak_blocked = True
        else:
            return round(mid, 4), "bid_ask_midpoint", leak_blocked

    legacy_current = _safe_optional_float(pos.get("current_price"))

    if legacy_current is not None and legacy_current >= MIN_VALID_OPTION_PREMIUM:
        if _looks_like_underlying_leak(entry, legacy_current, underlying):
            leak_blocked = True
        else:
            return round(legacy_current, 4), "safe_legacy_current_price", leak_blocked

    if entry is not None and entry >= MIN_VALID_OPTION_PREMIUM:
        source = "entry_premium_fallback_after_leak_block" if leak_blocked else "entry_premium_fallback"
        return round(entry, 4), source, leak_blocked

    return 0.0, "missing_option_premium", leak_blocked


# =============================================================================
# STOCK PRICE HELPERS
# =============================================================================

def _latest_underlying_price(symbol: str, fallback_price: Any) -> float:
    symbol = _safe_str(symbol, "").upper()
    fallback = _safe_float(fallback_price, 0.0)

    if not symbol:
        return fallback

    try:
        df = safe_download(symbol, period="5d", auto_adjust=True, progress=False)
        if df is None or getattr(df, "empty", True):
            return fallback

        close = df["Close"]

        if hasattr(close, "iloc"):
            value = close.iloc[-1]
            try:
                return float(value.item())
            except Exception:
                return float(value)

    except Exception:
        pass

    return fallback


def _stock_entry_price(pos: Dict[str, Any]) -> float:
    return _safe_float(
        pos.get(
            "entry",
            pos.get(
                "entry_price",
                pos.get(
                    "avg_entry",
                    pos.get(
                        "average_entry",
                        pos.get("fill_price", pos.get("price", 0.0)),
                    ),
                ),
            ),
        ),
        0.0,
    )


def _stock_current_price(pos: Dict[str, Any]) -> Tuple[float, str]:
    symbol = _norm_symbol(pos.get("symbol"))

    fallback = (
        pos.get("current_price")
        or pos.get("current_underlying_price")
        or pos.get("underlying_price")
        or pos.get("market_price")
        or pos.get("stock_price")
        or pos.get("price")
        or pos.get("entry")
        or pos.get("entry_price")
    )

    price = _latest_underlying_price(symbol, fallback)
    source = "safe_download" if price > 0 else "missing_stock_price"

    return round(price, 4), source


def _contracts(pos: Dict[str, Any]) -> int:
    return max(
        1,
        _safe_int(
            pos.get(
                "contracts",
                pos.get(
                    "contract_count",
                    pos.get("quantity", pos.get("qty", pos.get("size", 1))),
                ),
            ),
            1,
        ),
    )


def _shares(pos: Dict[str, Any]) -> int:
    return max(
        1,
        _safe_int(
            pos.get("shares", pos.get("quantity", pos.get("qty", pos.get("size", 1)))),
            1,
        ),
    )


# =============================================================================
# STOP / TARGET NORMALIZATION
# =============================================================================

def _option_stop_target(pos: Dict[str, Any], entry: float) -> Tuple[float, float, List[str]]:
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
        notes.append("ignored_option_stop_underlying_leak")
        stop = None

    if target is not None and _looks_like_underlying_leak(entry, target, underlying):
        notes.append("ignored_option_target_underlying_leak")
        target = None

    if stop is None or stop <= 0:
        stop = entry * 0.65
        notes.append("rebuilt_option_stop_from_entry_premium")

    if target is None or target <= 0:
        target = entry * 1.60
        notes.append("rebuilt_option_target_from_entry_premium")

    return (
        round(max(MIN_VALID_OPTION_PREMIUM, stop), 4),
        round(max(MIN_VALID_OPTION_PREMIUM, target), 4),
        notes,
    )


def _stock_stop_target(pos: Dict[str, Any], entry: float, direction: str) -> Tuple[float, float, List[str]]:
    notes: List[str] = []

    stop = _first_float(pos, ["stock_stop", "stop", "stop_loss"])
    target = _first_float(pos, ["stock_target", "target", "take_profit"])

    if direction == "SHORT":
        default_stop = entry * 1.03
        default_target = entry * 0.90
    else:
        default_stop = entry * 0.97
        default_target = entry * 1.10

    if stop is None or stop <= 0:
        stop = default_stop
        notes.append("rebuilt_stock_stop_from_entry_price")

    if target is None or target <= 0:
        target = default_target
        notes.append("rebuilt_stock_target_from_entry_price")

    return round(stop, 4), round(target, 4), notes


# =============================================================================
# REVIEW LOGIC
# =============================================================================

def _base_review_row(pos: Dict[str, Any]) -> Dict[str, Any]:
    symbol = _norm_symbol(pos.get("symbol"))
    vehicle = _vehicle(pos)
    strategy = _strategy(pos)

    return {
        "timestamp": _now_iso(),
        "symbol": symbol,
        "trade_id": _trade_id(pos),
        "vehicle": vehicle,
        "strategy": strategy,
        "action": ACTION_HOLD,
        "closed": False,
        "blocked": False,
        "reason": "",
        "price_review_basis": "",
        "monitoring_price_type": "",
        "underlying_price_used_for_close_decision": False,
        "underlying_price_used_for_pnl": False,
        "option_underlying_leak_blocked": False,
        "pnl": None,
        "pnl_pct": None,
        "close_result": None,
    }


def _should_close_option(action: str) -> bool:
    return action in {
        ACTION_STOP_LOSS,
        ACTION_TAKE_PROFIT,
        ACTION_CUT_WEAKNESS,
        ACTION_PROTECT_PROFIT,
    }


def _should_close_stock(action: str) -> bool:
    return action in {
        ACTION_STOP_LOSS,
        ACTION_TAKE_PROFIT,
        ACTION_CUT_WEAKNESS,
        ACTION_PROTECT_PROFIT,
    }


def _review_one_position(pos: Dict[str, Any], *, allow_closes: bool = True) -> Dict[str, Any]:
    pos = dict(pos)
    symbol = _norm_symbol(pos.get("symbol"))
    vehicle = _vehicle(pos)
    strategy = _strategy(pos)
    direction = _direction(strategy)
    days_open = _days_open(pos.get("opened_at", pos.get("timestamp", pos.get("created_at"))))

    result = _base_review_row(pos)

    if vehicle == VEHICLE_RESEARCH_ONLY:
        result.update(
            {
                "action": ACTION_HOLD,
                "reason": "research_only_no_open_position",
                "price_review_basis": "NO_POSITION",
                "monitoring_price_type": "RESEARCH_ONLY",
            }
        )
        return result

    if vehicle == VEHICLE_OPTION:
        entry = _option_entry_premium(pos)
        current, source, leak_blocked = _option_current_premium(pos)
        underlying = _underlying_price(pos)

        if entry is None or entry <= 0:
            entry = current

        entry = round(float(entry or 0.0), 4)
        current = round(float(current or 0.0), 4)

        if entry <= 0 or current <= 0:
            result.update(
                {
                    "action": ACTION_INVALID,
                    "blocked": True,
                    "reason": "missing_option_entry_or_current_premium",
                    "entry": entry,
                    "current": current,
                    "price_review_basis": "OPTION_PREMIUM_ONLY",
                    "monitoring_price_type": "OPTION_PREMIUM",
                    "underlying_price_used_for_close_decision": False,
                    "underlying_price_used_for_pnl": False,
                    "option_underlying_leak_blocked": bool(leak_blocked),
                }
            )
            return result

        stop, target, notes = _option_stop_target(pos, entry)
        contracts = _contracts(pos)

        pnl = round((current - entry) * OPTION_CONTRACT_MULTIPLIER * contracts, 2)
        pct = round(((current - entry) / entry) * 100.0, 4)

        stop_hit = current <= stop
        target_hit = current >= target

        action = ACTION_HOLD
        exit_gate_reason = "hold"
        exit_gate_notes: List[str] = []

        fresh_take_profit_window = days_open < FRESH_OPTION_TAKE_PROFIT_GRACE_DAYS
        fresh_protect_window = days_open < FRESH_OPTION_PROTECT_PROFIT_GRACE_DAYS
        extreme_profit = pct >= EXTREME_OPTION_PROFIT_EXIT_PCT
        suspicious_fresh_jump = fresh_take_profit_window and pct >= SUSPICIOUS_FRESH_OPTION_JUMP_PCT

        if suspicious_fresh_jump:
            action = ACTION_HOLD
            exit_gate_reason = "hold_suspicious_fresh_option_reprice"
            exit_gate_notes.append("fresh_option_jump_needs_confirmation_before_close")

        elif stop_hit:
            action = ACTION_STOP_LOSS
            exit_gate_reason = "stop_loss_confirmed"

        elif target_hit and (not fresh_take_profit_window or extreme_profit):
            action = ACTION_TAKE_PROFIT
            exit_gate_reason = "take_profit_confirmed"
            if extreme_profit and fresh_take_profit_window:
                exit_gate_notes.append("extreme_profit_allowed_inside_fresh_window")

        elif target_hit and fresh_take_profit_window:
            action = ACTION_HOLD
            exit_gate_reason = "hold_fresh_option_target_hit"
            exit_gate_notes.append("fresh_option_profit_waiting_for_confirmation")

        elif pct <= -35:
            action = ACTION_CUT_WEAKNESS
            exit_gate_reason = "cut_weakness_confirmed"

        elif pct >= 45 and not fresh_protect_window:
            action = ACTION_PROTECT_PROFIT
            exit_gate_reason = "protect_profit_confirmed"

        elif pct >= 45 and fresh_protect_window:
            action = ACTION_HOLD
            exit_gate_reason = "hold_fresh_option_protect_profit"
            exit_gate_notes.append("fresh_option_profit_protection_waiting_for_confirmation")

        result.update(
            {
                "entry": entry,
                "current": current,
                "stop": stop,
                "target": target,
                "contracts": contracts,
                "shares": 0,
                "underlying_price": underlying,
                "option_price_source": source,
                "option_underlying_leak_blocked": bool(leak_blocked),
                "underlying_price_used_for_close_decision": False,
                "underlying_price_used_for_pnl": False,
                "price_review_basis": "OPTION_PREMIUM_ONLY",
                "monitoring_price_type": "OPTION_PREMIUM",
                "pnl": pnl,
                "pnl_pct": pct,
                "pnl_basis": "option_premium_x_100",
                "days_open": round(days_open, 4),
                "normalization_notes": notes + exit_gate_notes,
                "fresh_option_exit_gate": {
                    "days_open": round(days_open, 4),
                    "fresh_take_profit_window": bool(fresh_take_profit_window),
                    "fresh_protect_profit_window": bool(fresh_protect_window),
                    "extreme_profit": bool(extreme_profit),
                    "suspicious_fresh_jump": bool(suspicious_fresh_jump),
                    "exit_gate_reason": exit_gate_reason,
                    "exit_gate_notes": exit_gate_notes,
                },
                "action": action,
                "reason": exit_gate_reason if action == ACTION_HOLD else action.lower(),
            }
        )

        if allow_closes and _should_close_option(action):
            close_reason = action.lower()
            trade_id = _trade_id(pos)

            # Critical:
            # Option closes receive option premium only.
            # Underlying price is never passed as the exit price for options.
            close_result = close_position(
                symbol,
                current,
                close_reason,
                trade_id=trade_id,
            )

            result["close_result"] = close_result
            result["closed"] = bool(isinstance(close_result, dict) and close_result.get("closed"))
            result["blocked"] = bool(isinstance(close_result, dict) and close_result.get("blocked"))
            result["close_reason"] = close_reason
            result["close_price"] = current
            result["exit_premium"] = current

        return result

    entry = _stock_entry_price(pos)
    current, source = _stock_current_price(pos)

    if entry <= 0:
        entry = current

    if entry <= 0 or current <= 0:
        result.update(
            {
                "action": ACTION_INVALID,
                "blocked": True,
                "reason": "missing_stock_entry_or_current_price",
                "entry": entry,
                "current": current,
                "price_review_basis": "STOCK_PRICE",
                "monitoring_price_type": "UNDERLYING",
                "underlying_price_used_for_close_decision": True,
                "underlying_price_used_for_pnl": True,
            }
        )
        return result

    stop, target, notes = _stock_stop_target(pos, entry, direction)
    shares = _shares(pos)

    if direction == "SHORT":
        pnl = round((entry - current) * shares, 2)
        pct = round(((entry - current) / entry) * 100.0, 4)
        stop_hit = current >= stop
        target_hit = current <= target
    else:
        pnl = round((current - entry) * shares, 2)
        pct = round(((current - entry) / entry) * 100.0, 4)
        stop_hit = current <= stop
        target_hit = current >= target

    action = ACTION_HOLD

    if stop_hit:
        action = ACTION_STOP_LOSS
    elif target_hit and days_open >= SAME_MOMENT_CLOSE_GRACE_DAYS:
        action = ACTION_TAKE_PROFIT
    elif pct <= -1.5:
        action = ACTION_CUT_WEAKNESS
    elif pct >= 3.0 and days_open >= SAME_MOMENT_CLOSE_GRACE_DAYS:
        action = ACTION_PROTECT_PROFIT

    result.update(
        {
            "entry": round(entry, 4),
            "current": round(current, 4),
            "stop": stop,
            "target": target,
            "shares": shares,
            "contracts": 0,
            "stock_price_source": source,
            "underlying_price": round(current, 4),
            "underlying_price_used_for_close_decision": True,
            "underlying_price_used_for_pnl": True,
            "price_review_basis": "STOCK_PRICE",
            "monitoring_price_type": "UNDERLYING",
            "pnl": pnl,
            "pnl_pct": pct,
            "pnl_basis": "stock_price_x_shares",
            "days_open": round(days_open, 4),
            "normalization_notes": notes,
            "action": action,
            "reason": action.lower(),
        }
    )

    if allow_closes and _should_close_stock(action):
        close_reason = action.lower()
        trade_id = _trade_id(pos)

        close_result = close_position(
            symbol,
            current,
            close_reason,
            trade_id=trade_id,
        )

        result["close_result"] = close_result
        result["closed"] = bool(isinstance(close_result, dict) and close_result.get("closed"))
        result["blocked"] = bool(isinstance(close_result, dict) and close_result.get("blocked"))
        result["close_reason"] = close_reason
        result["close_price"] = current

    return result


# =============================================================================
# PUBLIC REVIEW FUNCTIONS
# =============================================================================

def review_positions(allow_closes: bool = True) -> List[Dict[str, Any]]:
    try:
        positions = show_positions()
    except Exception as exc:
        print(f"OPEN POSITION REVIEW ERROR: {exc}")
        positions = []

    print("OPEN POSITION REVIEW")

    reviews: List[Dict[str, Any]] = []

    if not positions:
        print("No open positions.")
        return reviews

    for pos in positions:
        if not isinstance(pos, dict):
            continue

        review = _review_one_position(pos, allow_closes=allow_closes)
        reviews.append(review)

        symbol = review.get("symbol", "")
        vehicle = review.get("vehicle", "")
        action = review.get("action", ACTION_HOLD)

        if vehicle == VEHICLE_OPTION:
            print(
                f"{symbol} | Vehicle: {vehicle} | Current: {review.get('current')} | "
                f"Stop: {review.get('stop')} | Target: {review.get('target')} | "
                f"Basis: {review.get('price_review_basis')} | Action: {action}"
            )
        else:
            print(
                f"{symbol} | Vehicle: {vehicle} | Current: {review.get('current')} | "
                f"Entry: {review.get('entry')} | Stop: {review.get('stop')} | "
                f"Target: {review.get('target')} | Basis: {review.get('price_review_basis')} | "
                f"Action: {action}"
            )

        close_result = review.get("close_result")

        if isinstance(close_result, dict) and close_result.get("closed"):
            print(
                f"CLOSED: {symbol} | Reason: {review.get('close_reason')} | "
                f"ClosePrice: {review.get('close_price')} | PnL: {close_result.get('pnl')}"
            )

        elif isinstance(close_result, dict) and close_result.get("blocked"):
            print(f"BLOCKED CLOSE: {symbol} | Reason: {close_result.get('reason')}")

    return reviews


def review_open_positions(allow_closes: bool = True) -> List[Dict[str, Any]]:
    return review_positions(allow_closes=allow_closes)


def run_position_review(allow_closes: bool = True) -> List[Dict[str, Any]]:
    return review_positions(allow_closes=allow_closes)


def position_review(allow_closes: bool = True) -> List[Dict[str, Any]]:
    return review_positions(allow_closes=allow_closes)


def review_all_positions(allow_closes: bool = True) -> List[Dict[str, Any]]:
    return review_positions(allow_closes=allow_closes)


# =============================================================================
# OUTPUT BOX
# =============================================================================

def print_review_outcome_box(reviews: Optional[List[Dict[str, Any]]] = None) -> None:
    reviews = reviews if isinstance(reviews, list) else []

    print("\n" + "=" * 80)
    print("OBSERVATORY POSITION REVIEW OUTCOME")
    print("=" * 80)

    if not reviews:
        print("No reviews produced.")
        print("=" * 80)
        return

    total = len(reviews)
    closed = sum(1 for r in reviews if isinstance(r, dict) and r.get("closed"))
    blocked = sum(1 for r in reviews if isinstance(r, dict) and r.get("blocked"))
    holds = sum(1 for r in reviews if isinstance(r, dict) and r.get("action") == ACTION_HOLD)

    print(f"Reviews: {total}")
    print(f"Closed: {closed}")
    print(f"Blocked: {blocked}")
    print(f"Held: {holds}")
    print("-" * 80)

    for r in reviews:
        if not isinstance(r, dict):
            continue

        symbol = r.get("symbol", "")
        vehicle = r.get("vehicle", "")
        action = r.get("action", "")
        basis = r.get("price_review_basis", "")
        current = r.get("current", "")
        entry = r.get("entry", "")
        pnl = r.get("pnl", "")

        print(
            f"{symbol} | {vehicle} | {action} | Basis: {basis} | "
            f"Entry: {entry} | Current: {current} | PnL: {pnl}"
        )

        if vehicle == VEHICLE_OPTION:
            print(
                f"  Option safety: underlying used for decision = "
                f"{r.get('underlying_price_used_for_close_decision')} | "
                f"underlying used for pnl = {r.get('underlying_price_used_for_pnl')} | "
                f"leak blocked = {r.get('option_underlying_leak_blocked')}"
            )

        close_result = r.get("close_result")
        if isinstance(close_result, dict):
            print(
                f"  Close result: closed={close_result.get('closed')} | "
                f"blocked={close_result.get('blocked')} | "
                f"reason={close_result.get('reason')}"
            )

    print("=" * 80)


# =============================================================================
# LEGACY / UTILITY EXPORTS
# =============================================================================

def lock_profit(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Legacy compatibility stub.

    Older notebooks imported lock_profit from this file. The current canonical
    review path handles profit protection inside _review_one_position().
    """
    return {
        "ok": False,
        "reason": "lock_profit_legacy_stub",
        "message": "Profit protection is now handled by review_positions().",
        "args": args,
        "kwargs": kwargs,
    }


def trailing_stop(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Legacy compatibility stub.

    Older notebooks imported trailing_stop from this file. The current canonical
    review path handles trailing/protection decisions inside review_positions().
    """
    return {
        "ok": False,
        "reason": "trailing_stop_legacy_stub",
        "message": "Trailing/protection logic is now handled by review_positions().",
        "args": args,
        "kwargs": kwargs,
    }


__all__ = [
    "review_positions",
    "review_open_positions",
    "run_position_review",
    "position_review",
    "review_all_positions",
    "print_review_outcome_box",
    "show_positions",
    "safe_download",
    "review_exit",
    "close_position",
    "lock_profit",
    "trailing_stop",
]
