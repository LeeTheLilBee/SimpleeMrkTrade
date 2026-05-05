from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import math

from engine.paper_portfolio import show_positions, replace_position
from engine.close_trade import close_position

try:
    from engine.option_repricing import (
        reprice_open_option_position,
        apply_option_reprice_to_position,
    )
except Exception:
    reprice_open_option_position = None
    apply_option_reprice_to_position = None


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

MIN_VALID_OPTION_PREMIUM = 0.01
OPTION_UNDERLYING_LEAK_MULTIPLE = 8.0
OPTION_UNDERLYING_LEAK_ABSOLUTE = 25.0

SAME_MOMENT_CLOSE_GRACE_DAYS = 0.01


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


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _upper(value: Any, default: str = "") -> str:
    text = _safe_str(value, default).upper()
    return text if text else default


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


def _vehicle(pos: Dict[str, Any]) -> str:
    pos = _safe_dict(pos)

    raw = _upper(
        pos.get(
            "vehicle_selected",
            pos.get(
                "selected_vehicle",
                pos.get("vehicle", pos.get("asset_type", pos.get("instrument_type", ""))),
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

    option_obj = _safe_dict(pos.get("option"))
    contract_obj = _safe_dict(pos.get("contract"))

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
        or _first_str(option_obj, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_str(contract_obj, ["right", "option_type", "call_put", "contract_right"], ""),
        "",
    )

    if contract_symbol or option_obj or contract_obj or right in {"CALL", "PUT", "C", "P"}:
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
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        return max((now - dt).total_seconds() / 86400.0, 0.0)
    except Exception:
        return 0.0


def _position_identifier(pos: Dict[str, Any]) -> str:
    return _safe_str(pos.get("trade_id", pos.get("position_id", pos.get("id", pos.get("order_id", "")))), "")


def _position_replace_key(pos: Dict[str, Any]) -> str:
    return _norm_symbol(pos.get("symbol"))


def _extract_contract(pos: Dict[str, Any]) -> Dict[str, Any]:
    pos = _safe_dict(pos)
    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))

    out: Dict[str, Any] = {}
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
        or _first_str(out, ["contractSymbol", "contract_symbol", "option_symbol", "selected_contract_symbol", "occ_symbol"], "")
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

    mark = _first_float(
        pos,
        [
            "current_option_mark",
            "option_current_mark",
            "option_mark",
            "mark",
            "current_premium",
            "premium_current",
            "option_current_price",
        ],
    )
    if mark is None:
        mark = _first_float(
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

    return {
        "contract_symbol": contract_symbol,
        "expiry": expiry,
        "expiration": expiry,
        "right": right,
        "strike": _first_float(pos, ["strike", "strike_price", "contract_strike"])
        or _first_float(out, ["strike", "strike_price", "contract_strike"]),
        "bid": _first_float(pos, ["option_bid", "bid"]) or _first_float(out, ["bid"]),
        "ask": _first_float(pos, ["option_ask", "ask"]) or _first_float(out, ["ask"]),
        "last": _first_float(pos, ["option_last", "last"]) or _first_float(out, ["last", "last_price"]),
        "mark": mark,
        "volume": _safe_int(pos.get("option_volume", pos.get("volume", out.get("volume"))), 0),
        "open_interest": _safe_int(pos.get("option_open_interest", pos.get("open_interest", out.get("open_interest", out.get("oi")))), 0),
        "contract_score": _safe_float(pos.get("contract_score", pos.get("option_contract_score", out.get("contract_score"))), 0.0),
        "price_reference": _safe_float(pos.get("price_reference", out.get("price_reference", out.get("selected_price_reference"))), 0.0),
    }


def _mid_from_bid_ask(bid: Optional[float], ask: Optional[float]) -> Optional[float]:
    if bid is None or ask is None:
        return None
    if bid <= 0 or ask <= 0:
        return None
    if ask < bid:
        return None
    return round((bid + ask) / 2.0, 4)


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
        if candidate_current >= OPTION_UNDERLYING_LEAK_ABSOLUTE and candidate_current >= option_entry * OPTION_UNDERLYING_LEAK_MULTIPLE:
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


def _latest_option_price(pos: Dict[str, Any]) -> Tuple[float, str, bool]:
    pos = _safe_dict(pos)
    option = _safe_dict(pos.get("option"))
    contract_obj = _safe_dict(pos.get("contract"))
    contract = _extract_contract(pos)

    entry = _option_entry_premium(pos)
    underlying = _underlying_price(pos)
    leak_blocked = False

    premium_candidates = [
        ("current_premium", pos.get("current_premium")),
        ("premium_current", pos.get("premium_current")),
        ("current_option_mark", pos.get("current_option_mark")),
        ("option_current_mark", pos.get("option_current_mark")),
        ("option_current_price", pos.get("option_current_price")),
        ("current_option_price", pos.get("current_option_price")),
        ("option_mark", pos.get("option_mark")),
        ("mark", pos.get("mark")),
        ("option.mark", option.get("mark")),
        ("option.current_mark", option.get("current_mark")),
        ("option.selected_price_reference", option.get("selected_price_reference")),
        ("option.price_reference", option.get("price_reference")),
        ("option.last", option.get("last")),
        ("contract.mark", contract_obj.get("mark")),
        ("contract.current_mark", contract_obj.get("current_mark")),
        ("contract.selected_price_reference", contract_obj.get("selected_price_reference")),
        ("contract.price_reference", contract_obj.get("price_reference")),
        ("contract.last", contract_obj.get("last")),
        ("extracted_contract.mark", contract.get("mark")),
        ("extracted_contract.price_reference", contract.get("price_reference")),
        ("extracted_contract.last", contract.get("last")),
    ]

    for source, value in premium_candidates:
        price = _safe_optional_float(value)
        if price is None or price < MIN_VALID_OPTION_PREMIUM:
            continue

        if _looks_like_underlying_leak(entry, price, underlying):
            leak_blocked = True
            continue

        return round(price, 4), source, leak_blocked

    mid = _mid_from_bid_ask(
        _safe_optional_float(contract.get("bid")),
        _safe_optional_float(contract.get("ask")),
    )
    if mid is not None and mid >= MIN_VALID_OPTION_PREMIUM:
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


def _stock_entry_price(pos: Dict[str, Any]) -> float:
    return _safe_float(
        pos.get(
            "entry",
            pos.get("entry_price", pos.get("avg_entry", pos.get("average_entry", pos.get("fill_price", pos.get("price", 0.0))))),
        ),
        0.0,
    )


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


def _normalize_option_stop_target(pos: Dict[str, Any], entry: float, current: float) -> Tuple[float, float, List[str]]:
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

    if stop is None or stop <= 0:
        stop = entry * (1.0 - DEFAULT_OPTION_STOP_LOSS_PCT)
        notes.append("rebuilt_option_stop_from_entry_premium")

    if target is None or target <= 0:
        target = entry * (1.0 + DEFAULT_OPTION_TARGET_GAIN_PCT)
        notes.append("rebuilt_option_target_from_entry_premium")

    return round(max(MIN_VALID_OPTION_PREMIUM, stop), 4), round(max(MIN_VALID_OPTION_PREMIUM, target), 4), notes


def _normalize_stock_stop_target(pos: Dict[str, Any], entry: float, direction: str, current: float) -> Tuple[float, float, List[str]]:
    notes: List[str] = []

    stop = _first_float(pos, ["stock_stop", "stop", "stop_loss"])
    target = _first_float(pos, ["stock_target", "target", "take_profit"])

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


def _apply_option_reprice(pos: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    reprice_payload: Dict[str, Any] = {
        "repriced": False,
        "reason": "option_repricing_not_available",
        "source": "",
        "old_current": pos.get("current_price"),
        "new_current": pos.get("current_price"),
        "leak_blocked": False,
    }

    if callable(reprice_open_option_position) and callable(apply_option_reprice_to_position):
        try:
            reprice_payload = reprice_open_option_position(pos)
            if not isinstance(reprice_payload, dict):
                reprice_payload = {
                    "repriced": False,
                    "reason": "option_reprice_returned_non_dict",
                    "source": "",
                    "old_current": pos.get("current_price"),
                    "new_current": pos.get("current_price"),
                    "leak_blocked": False,
                }
            else:
                updated = apply_option_reprice_to_position(pos, reprice_payload)
                if isinstance(updated, dict):
                    pos = updated
        except Exception as exc:
            reprice_payload = {
                "repriced": False,
                "reason": f"option_reprice_exception:{exc}",
                "source": "",
                "old_current": pos.get("current_price"),
                "new_current": pos.get("current_price"),
                "leak_blocked": False,
            }

    pos["option_reprice"] = reprice_payload
    pos["option_repriced"] = bool(reprice_payload.get("repriced"))
    pos["option_reprice_reason"] = reprice_payload.get("reason", "")
    pos["option_reprice_source"] = reprice_payload.get("source", "")
    pos["option_reprice_old_current"] = reprice_payload.get("old_current")
    pos["option_reprice_new_current"] = reprice_payload.get("new_current")

    return pos, reprice_payload


def _ensure_monitor_defaults(pos: Dict[str, Any]) -> Dict[str, Any]:
    pos = dict(pos) if isinstance(pos, dict) else {}
    vehicle = _vehicle(pos)

    if vehicle == VEHICLE_RESEARCH_ONLY:
        pos["monitoring_price_type"] = "RESEARCH_ONLY"
        pos["price_review_basis"] = "NO_POSITION"
        pos["monitor_ready"] = False
        return pos

    strategy = _strategy(pos)
    direction = _direction(strategy)

    if vehicle == VEHICLE_OPTION:
        pos, reprice_payload = _apply_option_reprice(pos)

        contract = _extract_contract(pos)

        entry = _option_entry_premium(pos)
        current, source, leak_blocked = _latest_option_price(pos)

        if bool(reprice_payload.get("leak_blocked")):
            leak_blocked = True

        if entry is None or entry <= 0:
            entry = current

        if current <= 0 and entry and entry > 0:
            current = round(entry, 4)
            source = "entry_premium_final_fallback"

        entry = round(float(entry or 0.0), 4)
        current = round(float(current or 0.0), 4)

        stop, target, stop_target_notes = _normalize_option_stop_target(pos, entry, current)

        underlying = _underlying_price(pos)
        contracts = max(1, _safe_int(pos.get("contracts", pos.get("contract_count", pos.get("quantity", pos.get("qty", 1)))), 1))

        unrealized_pnl = round((current - entry) * OPTION_CONTRACT_MULTIPLIER * contracts, 2) if entry > 0 and current > 0 else 0.0
        unrealized_pnl_pct = round(((current - entry) / entry) * 100.0, 4) if entry > 0 and current > 0 else 0.0

        pos["vehicle"] = VEHICLE_OPTION
        pos["vehicle_selected"] = VEHICLE_OPTION
        pos["selected_vehicle"] = VEHICLE_OPTION
        pos["asset_type"] = VEHICLE_OPTION
        pos["instrument_type"] = VEHICLE_OPTION

        pos["entry_premium"] = entry
        pos["premium_entry"] = entry
        pos["option_entry"] = entry
        pos["option_entry_price"] = entry
        pos["current_premium"] = current
        pos["premium_current"] = current
        pos["current_option_mark"] = current
        pos["option_current_mark"] = current
        pos["option_current_price"] = current
        pos["current_option_price"] = current
        pos["option_stop"] = stop
        pos["premium_stop"] = stop
        pos["option_target"] = target
        pos["premium_target"] = target

        pos["entry"] = entry
        pos["entry_price"] = entry
        pos["current_price"] = current
        pos["stop"] = stop
        pos["target"] = target

        if underlying is not None and underlying > 0:
            pos["underlying_price"] = round(underlying, 4)
            pos["current_underlying_price"] = round(underlying, 4)

        if contract.get("contract_symbol"):
            pos["contract_symbol"] = contract.get("contract_symbol")
            pos["option_symbol"] = contract.get("contract_symbol")
            pos["option_contract_symbol"] = contract.get("contract_symbol")
            pos["contractSymbol"] = contract.get("contract_symbol")
        if contract.get("expiry"):
            pos["expiry"] = contract.get("expiry")
            pos["expiration"] = contract.get("expiry")
        if contract.get("strike") is not None:
            pos["strike"] = contract.get("strike")
        if contract.get("right"):
            pos["right"] = contract.get("right")

        pos["contracts"] = contracts
        pos["shares"] = 0

        pos["monitoring_price_type"] = "OPTION_PREMIUM"
        pos["price_review_basis"] = "OPTION_PREMIUM_ONLY"
        pos["underlying_price_used_for_close_decision"] = False
        pos["option_price_source"] = source
        pos["option_underlying_leak_blocked"] = bool(leak_blocked)
        pos["monitor_ready"] = entry > 0 and current > 0

        pos["unrealized_pnl"] = unrealized_pnl
        pos["unrealized_pnl_pct"] = unrealized_pnl_pct
        pos["pnl_basis"] = "option_premium_x_100"
        pos["execution_position_shape"] = "OPTION_PREMIUM_POSITION"

        pos["monitor_normalization_notes"] = stop_target_notes
        pos["option_safety"] = {
            "premium_only": True,
            "legacy_current_price_allowed": source == "safe_legacy_current_price",
            "underlying_leak_blocked": bool(leak_blocked),
            "underlying_used_for_decision": False,
            "source": source,
            "repriced": bool(pos.get("option_repriced", False)),
            "reprice_reason": pos.get("option_reprice_reason", ""),
            "reprice_source": pos.get("option_reprice_source", ""),
        }

        return pos

    entry = _stock_entry_price(pos)
    current, source = _latest_stock_price(pos)

    if current <= 0:
        current = entry

    if entry <= 0:
        entry = current

    stop, target, stop_target_notes = _normalize_stock_stop_target(pos, entry, direction, current)

    shares = max(1, _safe_int(pos.get("shares", pos.get("quantity", pos.get("qty", 1))), 1))

    entry = round(entry, 4)
    current = round(current, 4)

    if direction == "SHORT":
        unrealized_pnl = round((entry - current) * shares, 2) if entry > 0 and current > 0 else 0.0
        unrealized_pnl_pct = round(((entry - current) / entry) * 100.0, 4) if entry > 0 and current > 0 else 0.0
    else:
        unrealized_pnl = round((current - entry) * shares, 2) if entry > 0 and current > 0 else 0.0
        unrealized_pnl_pct = round(((current - entry) / entry) * 100.0, 4) if entry > 0 and current > 0 else 0.0

    pos["vehicle"] = VEHICLE_STOCK
    pos["vehicle_selected"] = VEHICLE_STOCK
    pos["selected_vehicle"] = VEHICLE_STOCK
    pos["asset_type"] = VEHICLE_STOCK
    pos["instrument_type"] = VEHICLE_STOCK

    pos["entry"] = entry
    pos["entry_price"] = entry
    pos["current_price"] = current
    pos["underlying_price"] = current
    pos["current_underlying_price"] = current
    pos["stop"] = stop
    pos["target"] = target
    pos["shares"] = shares
    pos["contracts"] = 0

    pos["monitoring_price_type"] = "UNDERLYING"
    pos["price_review_basis"] = "STOCK_PRICE"
    pos["underlying_price_used_for_close_decision"] = True
    pos["stock_price_source"] = source
    pos["monitor_ready"] = entry > 0 and current > 0

    pos["unrealized_pnl"] = unrealized_pnl
    pos["unrealized_pnl_pct"] = unrealized_pnl_pct
    pos["pnl_basis"] = "stock_price_x_shares"
    pos["execution_position_shape"] = "STOCK_UNDERLYING_POSITION"

    pos["monitor_normalization_notes"] = stop_target_notes

    return pos


def _pct_change(entry: float, current: float, strategy: str, vehicle: str) -> float:
    if entry <= 0 or current <= 0:
        return 0.0

    if vehicle == VEHICLE_OPTION:
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
        if stop > 0 and current <= stop:
            return ACTION_STOP_LOSS

        if target > 0 and current >= target and days_open >= SAME_MOMENT_CLOSE_GRACE_DAYS:
            return ACTION_TAKE_PROFIT

        if pct <= -35:
            return ACTION_CUT_WEAKNESS

        if pct >= 45 and days_open >= SAME_MOMENT_CLOSE_GRACE_DAYS:
            return ACTION_PROTECT_PROFIT

        return ACTION_HOLD

    if direction == "SHORT":
        stop_hit = current >= stop if stop > 0 else False
        target_hit = current <= target if target > 0 else False
    else:
        stop_hit = current <= stop if stop > 0 else False
        target_hit = current >= target if target > 0 else False

    if stop_hit:
        return ACTION_STOP_LOSS

    if target_hit and days_open >= SAME_MOMENT_CLOSE_GRACE_DAYS:
        return ACTION_TAKE_PROFIT

    if pct <= -1.5:
        return ACTION_CUT_WEAKNESS

    if pct >= 3.0 and days_open >= SAME_MOMENT_CLOSE_GRACE_DAYS:
        return ACTION_PROTECT_PROFIT

    return ACTION_HOLD


def _close_reason_from_action(action: str) -> str:
    mapping = {
        ACTION_STOP_LOSS: "stop_loss",
        ACTION_TAKE_PROFIT: "take_profit",
        ACTION_CUT_WEAKNESS: "cut_weakness",
        ACTION_PROTECT_PROFIT: "protect_profit",
        ACTION_INVALID: "invalid_monitor",
    }
    return mapping.get(_upper(action, ACTION_HOLD), _safe_str(action, ACTION_HOLD).lower())


def _should_attempt_close(action: str) -> bool:
    return action in {ACTION_STOP_LOSS, ACTION_TAKE_PROFIT, ACTION_CUT_WEAKNESS, ACTION_PROTECT_PROFIT}


def _close_price_for_position(pos: Dict[str, Any]) -> float:
    vehicle = _vehicle(pos)

    if vehicle == VEHICLE_OPTION:
        return _safe_float(
            pos.get(
                "current_premium",
                pos.get("current_option_mark", pos.get("option_current_price", pos.get("current_price", 0.0))),
            ),
            0.0,
        )

    return _safe_float(pos.get("current_price", 0.0), 0.0)


def _build_close_audit_payload(pos: Dict[str, Any], action: str, close_price: float) -> Dict[str, Any]:
    return {
        "symbol": _norm_symbol(pos.get("symbol")),
        "trade_id": _position_identifier(pos),
        "vehicle": _vehicle(pos),
        "action": action,
        "reason": _close_reason_from_action(action),
        "close_price": close_price,
        "price_review_basis": pos.get("price_review_basis", ""),
        "monitoring_price_type": pos.get("monitoring_price_type", ""),
        "underlying_price": pos.get("underlying_price"),
        "current_underlying_price": pos.get("current_underlying_price"),
        "current_premium": pos.get("current_premium"),
        "current_option_mark": pos.get("current_option_mark"),
        "option_current_price": pos.get("option_current_price"),
        "option_repriced": bool(pos.get("option_repriced", False)),
        "option_reprice_reason": pos.get("option_reprice_reason", ""),
        "option_reprice_source": pos.get("option_reprice_source", ""),
        "option_reprice": pos.get("option_reprice", {}),
        "underlying_price_used_for_close_decision": bool(
            pos.get("underlying_price_used_for_close_decision", _vehicle(pos) != VEHICLE_OPTION)
        ),
        "option_underlying_leak_blocked": bool(pos.get("option_underlying_leak_blocked", False)),
        "pnl_basis": pos.get("pnl_basis", ""),
        "execution_position_shape": pos.get("execution_position_shape", ""),
    }


def monitor_open_positions() -> List[Dict[str, Any]]:
    try:
        positions = show_positions()
    except Exception as exc:
        print(f"POSITION MONITOR ERROR: could not load positions | {exc}")
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
        days_open_value = _days_open(pos.get("opened_at", pos.get("timestamp", pos.get("created_at"))))

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
            "option_current_price": pos.get("option_current_price"),
            "option_price_source": pos.get("option_price_source", ""),
            "option_repriced": bool(pos.get("option_repriced", False)),
            "option_reprice_reason": pos.get("option_reprice_reason", ""),
            "option_reprice_source": pos.get("option_reprice_source", ""),
            "option_reprice": pos.get("option_reprice", {}),
            "option_underlying_leak_blocked": bool(pos.get("option_underlying_leak_blocked", False)),
            "underlying_price_used_for_close_decision": bool(
                pos.get("underlying_price_used_for_close_decision", vehicle != VEHICLE_OPTION)
            ),
            "days_open": round(days_open_value, 4),
            "pct_change": pct,
            "progress_to_target": progress,
            "unrealized_pnl": pos.get("unrealized_pnl", 0.0),
            "unrealized_pnl_pct": pos.get("unrealized_pnl_pct", 0.0),
            "pnl_basis": pos.get("pnl_basis", ""),
            "execution_position_shape": pos.get("execution_position_shape", ""),
            "monitor_ready": bool(pos.get("monitor_ready", False)),
            "normalization_notes": _safe_list(pos.get("monitor_normalization_notes")),
            "final_action": action,
        }

        replace_key = _position_replace_key(pos)
        if replace_key:
            try:
                replace_position(replace_key, pos)
            except Exception as exc:
                print(f"POSITION MONITOR WARNING: replace_position failed for {replace_key} | {exc}")

        if vehicle == VEHICLE_OPTION:
            print(
                f"{symbol} | Vehicle: {vehicle} | MonitorPrice: {pos.get('monitoring_price_type', '')} | "
                f"PremiumCurrent: {round(current, 4)} | EntryPremium: {round(entry, 4)} | "
                f"PremiumStop: {round(stop, 4)} | PremiumTarget: {round(target, 4)} | "
                f"UnderlyingContext: {pos.get('underlying_price')} | Source: {pos.get('option_price_source')} | "
                f"Repriced: {bool(pos.get('option_repriced', False))} | "
                f"RepriceSource: {pos.get('option_reprice_source', '')} | "
                f"LeakBlocked: {bool(pos.get('option_underlying_leak_blocked', False))} | Action: {action}"
            )
        else:
            print(
                f"{symbol} | Vehicle: {vehicle} | MonitorPrice: {pos.get('monitoring_price_type', '')} | "
                f"Current: {round(current, 4)} | Entry: {round(entry, 4)} | Stop: {round(stop, 4)} | "
                f"Target: {round(target, 4)} | Action: {action}"
            )

        if not _should_attempt_close(action):
            continue

        if close_price <= 0:
            blocked_payload = _build_close_audit_payload(pos, action, close_price)
            blocked_payload.update(
                {
                    "blocked": True,
                    "blocked_reason": "missing_valid_close_price",
                    "result": None,
                }
            )
            actions.append(blocked_payload)
            print(f"BLOCKED CLOSE: {symbol} | Reason: missing_valid_close_price")
            continue

        if vehicle == VEHICLE_OPTION and bool(pos.get("underlying_price_used_for_close_decision", False)):
            blocked_payload = _build_close_audit_payload(pos, action, close_price)
            blocked_payload.update(
                {
                    "blocked": True,
                    "blocked_reason": "option_underlying_price_close_blocked",
                    "result": None,
                }
            )
            actions.append(blocked_payload)
            print(f"BLOCKED CLOSE: {symbol} | Reason: option_underlying_price_close_blocked")
            continue

        try:
            result = close_position(
                symbol,
                close_price,
                reason=_close_reason_from_action(action),
                trade_id=trade_id,
            )
        except TypeError:
            result = close_position(symbol, close_price, _close_reason_from_action(action))
        except Exception as exc:
            result = {
                "closed": False,
                "blocked": True,
                "reason": f"close_position_exception:{exc}",
            }

        action_payload = _build_close_audit_payload(pos, action, close_price)
        action_payload["result"] = result
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


run_position_monitor = monitor_open_positions
monitor_positions = monitor_open_positions


if __name__ == "__main__":
    monitor_open_positions()
