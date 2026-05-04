from __future__ import annotations

"""
Observatory Position Review

This file reviews open positions and decides whether to hold, stop out,
or take profit.

Critical option rule:
    OPTION positions must be reviewed against option premium only.

This prevents the bug where an option entry like 5.25 gets compared against
the underlying stock price like 98.04 and falsely triggers TAKE_PROFIT.

Current limitation:
    We do not yet have a fully reliable live option quote refresh path for
    open positions. Until that repricer is built, option review uses stored
    option premium fields first, then falls back to the original option entry.
"""

from typing import Any, Dict, List, Optional, Tuple

from engine.paper_portfolio import show_positions
from engine.data_utils import safe_download
from engine.exit_review import review_exit
from engine.trailing_stop import trailing_stop
from engine.profit_lock import lock_profit
from engine.close_trade import close_position


OPTION_CONTRACT_MULTIPLIER = 100

VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        if isinstance(value, bool):
            return float(default)
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return float(default)
            value = cleaned
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
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


def _first_positive_float(*values: Any) -> float:
    for value in values:
        number = _safe_float(value, 0.0)
        if number > 0:
            return number
    return 0.0


def _first_nonempty(*values: Any, default: str = "") -> str:
    for value in values:
        text = _safe_str(value, "")
        if text:
            return text
    return default


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _norm_vehicle(pos: Dict[str, Any]) -> str:
    pos = _safe_dict(pos)

    vehicle = _safe_str(
        pos.get(
            "vehicle_selected",
            pos.get(
                "selected_vehicle",
                pos.get("vehicle", pos.get("asset_type", pos.get("instrument_type", ""))),
            ),
        ),
        "",
    ).upper()

    if vehicle in {"OPTION", "OPTIONS", "OPT"}:
        return VEHICLE_OPTION

    if vehicle in {"STOCK", "EQUITY", "SHARE", "SHARES"}:
        return VEHICLE_STOCK

    if vehicle in {"RESEARCH_ONLY", "RESEARCH"}:
        return VEHICLE_RESEARCH_ONLY

    contracts = _safe_int(pos.get("contracts", pos.get("contract_count", 0)), 0)
    shares = _safe_int(pos.get("shares", 0), 0)
    contract_symbol = _option_contract_symbol(pos)

    if contracts > 0 or contract_symbol:
        return VEHICLE_OPTION

    if shares > 0:
        return VEHICLE_STOCK

    return VEHICLE_STOCK


def _is_short_like(pos: Dict[str, Any]) -> bool:
    strategy = _safe_str(pos.get("strategy", pos.get("direction", "")), "").upper()
    right = _safe_str(pos.get("right", pos.get("option_type", pos.get("call_put", ""))), "").upper()

    return (
        "PUT" in strategy
        or "SHORT" in strategy
        or right in {"P", "PUT"}
    )


def _latest_underlying_price(symbol: str, fallback_price: Any) -> float:
    symbol = _safe_str(symbol, "").upper()

    if not symbol:
        return _safe_float(fallback_price, 0.0)

    try:
        df = safe_download(symbol, period="5d", auto_adjust=True, progress=False)
        if df is None or getattr(df, "empty", True):
            return _safe_float(fallback_price, 0.0)

        close = df["Close"]
        if hasattr(close, "iloc"):
            value = close.iloc[-1]
            try:
                return float(value.item())
            except Exception:
                return float(value)
    except Exception:
        pass

    return _safe_float(fallback_price, 0.0)


def _extract_option_contract(pos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pull the best available option/contract payload from the position.
    """
    pos = _safe_dict(pos)

    for key in ["option", "contract", "selected_contract", "best_option", "best_option_preview"]:
        obj = pos.get(key)
        if isinstance(obj, dict) and obj:
            return dict(obj)

    lifecycle = pos.get("lifecycle") if isinstance(pos.get("lifecycle"), dict) else {}
    for key in ["option", "contract", "selected_contract", "best_option", "best_option_preview"]:
        obj = lifecycle.get(key)
        if isinstance(obj, dict) and obj:
            return dict(obj)

    raw_lifecycle = pos.get("raw_lifecycle") if isinstance(pos.get("raw_lifecycle"), dict) else {}
    for key in ["option", "contract", "selected_contract", "best_option", "best_option_preview"]:
        obj = raw_lifecycle.get(key)
        if isinstance(obj, dict) and obj:
            return dict(obj)

    execution_result = pos.get("execution_result") if isinstance(pos.get("execution_result"), dict) else {}
    execution_record = execution_result.get("execution_record") if isinstance(execution_result.get("execution_record"), dict) else {}

    for source in [execution_result, execution_record]:
        for key in ["option", "contract", "selected_contract", "best_option", "best_option_preview"]:
            obj = source.get(key)
            if isinstance(obj, dict) and obj:
                return dict(obj)

    return {}


def _option_contract_symbol(pos: Dict[str, Any]) -> str:
    pos = _safe_dict(pos)
    contract = _extract_option_contract(pos)

    return _first_nonempty(
        pos.get("contract_symbol"),
        pos.get("option_symbol"),
        pos.get("option_contract_symbol"),
        pos.get("occ_symbol"),
        contract.get("contractSymbol"),
        contract.get("contract_symbol"),
        contract.get("option_symbol"),
        contract.get("symbol"),
        default="",
    )


def _option_expiry(pos: Dict[str, Any]) -> str:
    pos = _safe_dict(pos)
    contract = _extract_option_contract(pos)

    return _first_nonempty(
        pos.get("expiry"),
        pos.get("expiration"),
        pos.get("expiration_date"),
        pos.get("contract_expiry"),
        contract.get("expiration"),
        contract.get("expiry"),
        contract.get("expiration_date"),
        contract.get("contract_expiry"),
        default="",
    )


def _option_entry_price(pos: Dict[str, Any]) -> float:
    pos = _safe_dict(pos)
    contract = _extract_option_contract(pos)

    return round(
        _first_positive_float(
            pos.get("entry_premium"),
            pos.get("premium_entry"),
            pos.get("option_entry"),
            pos.get("option_entry_price"),
            pos.get("fill_price"),
            pos.get("executed_price"),
            pos.get("entry"),
            pos.get("entry_price"),
            contract.get("entry"),
            contract.get("fill_price"),
            contract.get("selected_price_reference"),
            contract.get("price_reference"),
            contract.get("mark"),
            contract.get("last"),
            contract.get("ask"),
        ),
        4,
    )


def _option_stored_market_price(pos: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    Option premium source order.

    This intentionally does NOT use:
        - underlying_price
        - stock_price
        - current_underlying_price

    Because those are stock prices, not option premiums.
    """
    pos = _safe_dict(pos)
    contract = _extract_option_contract(pos)
    entry = _option_entry_price(pos)

    bid = _first_positive_float(
        pos.get("option_bid"),
        pos.get("bid"),
        contract.get("bid"),
    )

    ask = _first_positive_float(
        pos.get("option_ask"),
        pos.get("ask"),
        contract.get("ask"),
    )

    last = _first_positive_float(
        pos.get("option_last"),
        pos.get("last"),
        contract.get("last"),
        contract.get("last_price"),
    )

    mark = _first_positive_float(
        pos.get("current_premium"),
        pos.get("premium_current"),
        pos.get("current_option_mark"),
        pos.get("option_current_mark"),
        pos.get("option_current_price"),
        pos.get("current_option_price"),
        pos.get("option_mark"),
        pos.get("mark"),
        contract.get("current_price"),
        contract.get("current_premium"),
        contract.get("current_option_mark"),
        contract.get("option_current_mark"),
        contract.get("mark"),
        contract.get("mid"),
        contract.get("selected_price_reference"),
        contract.get("price_reference"),
    )

    if mark <= 0 and bid > 0 and ask > 0 and ask >= bid:
        mark = round((bid + ask) / 2.0, 4)

    if mark <= 0:
        mark = _first_positive_float(last, ask, bid)

    if mark <= 0:
        mark = entry

    quote = {
        "price": round(mark, 4) if mark > 0 else 0.0,
        "bid": round(bid, 4) if bid > 0 else 0.0,
        "ask": round(ask, 4) if ask > 0 else 0.0,
        "last": round(last, 4) if last > 0 else 0.0,
        "entry": round(entry, 4) if entry > 0 else 0.0,
        "source": "stored_option_premium_or_entry",
        "price_basis": "OPTION_PREMIUM_ONLY",
        "contract_symbol": _option_contract_symbol(pos),
        "expiry": _option_expiry(pos),
        "underlying_price_used_for_close_decision": False,
    }

    return quote["price"], quote


def _option_market_price_from_position(pos: Dict[str, Any]) -> float:
    """
    Compatibility wrapper for older call sites.

    Returns option premium only.
    """
    price, _quote = _option_stored_market_price(pos)
    return price


def _position_market_price(pos: Dict[str, Any]) -> float:
    vehicle = _norm_vehicle(pos)
    symbol = _safe_str(pos.get("symbol"), "").upper()

    if vehicle == VEHICLE_OPTION:
        return _option_market_price_from_position(pos)

    fallback = pos.get(
        "current_price",
        pos.get(
            "underlying_price",
            pos.get("stock_price", pos.get("entry", pos.get("price", 0.0))),
        ),
    )
    return _latest_underlying_price(symbol, fallback)


def _ensure_option_stop(entry: float, raw_stop: float, pos: Dict[str, Any]) -> float:
    if raw_stop > 0:
        return round(raw_stop, 4)

    option_stop = _first_positive_float(
        pos.get("option_stop"),
        pos.get("premium_stop"),
        pos.get("stop_premium"),
        pos.get("contract_stop"),
    )

    if option_stop > 0:
        return round(option_stop, 4)

    if entry <= 0:
        return 0.0

    if _is_short_like(pos):
        return round(entry * 1.35, 4)

    return round(entry * 0.65, 4)


def _ensure_option_target(entry: float, raw_target: float, pos: Dict[str, Any]) -> float:
    if raw_target > 0:
        return round(raw_target, 4)

    option_target = _first_positive_float(
        pos.get("option_target"),
        pos.get("premium_target"),
        pos.get("target_premium"),
        pos.get("contract_target"),
    )

    if option_target > 0:
        return round(option_target, 4)

    if entry <= 0:
        return 0.0

    if _is_short_like(pos):
        return round(entry * 0.65, 4)

    return round(entry * 1.60, 4)


def _ensure_stock_stop(entry: float, raw_stop: float, current: float, atr: float) -> float:
    if raw_stop > 0:
        return round(raw_stop, 4)

    trail = _safe_float(trailing_stop(entry, current, atr), 0.0)
    locked = lock_profit(entry, current)
    locked_value = _safe_float(locked, 0.0) if locked is not None else 0.0

    if locked_value > 0:
        return round(locked_value, 4)
    if trail > 0:
        return round(trail, 4)

    if entry <= 0:
        return 0.0

    return round(entry * 0.97, 4)


def _ensure_stock_target(entry: float, raw_target: float) -> float:
    if raw_target > 0:
        return round(raw_target, 4)
    if entry <= 0:
        return 0.0
    return round(entry * 1.10, 4)


def _ensure_stop(entry: float, raw_stop: float, current: float, atr: float, vehicle: str, pos: Optional[Dict[str, Any]] = None) -> float:
    pos = _safe_dict(pos)

    if vehicle == VEHICLE_OPTION:
        return _ensure_option_stop(entry, raw_stop, pos)

    return _ensure_stock_stop(entry, raw_stop, current, atr)


def _ensure_target(entry: float, raw_target: float, vehicle: str, pos: Optional[Dict[str, Any]] = None) -> float:
    pos = _safe_dict(pos)

    if vehicle == VEHICLE_OPTION:
        return _ensure_option_target(entry, raw_target, pos)

    return _ensure_stock_target(entry, raw_target)


def _calculate_pnl(pos: Dict[str, Any], vehicle: str, exit_price: float) -> float:
    pos = _safe_dict(pos)

    if vehicle == VEHICLE_OPTION:
        entry = _option_entry_price(pos)
        contracts = max(1, _safe_int(pos.get("contracts", pos.get("contract_count", 1)), 1))

        if entry <= 0 or exit_price <= 0:
            return 0.0

        if _is_short_like(pos):
            return round((entry - exit_price) * contracts * OPTION_CONTRACT_MULTIPLIER, 4)

        return round((exit_price - entry) * contracts * OPTION_CONTRACT_MULTIPLIER, 4)

    entry = _first_positive_float(
        pos.get("entry"),
        pos.get("entry_price"),
        pos.get("fill_price"),
        pos.get("price"),
    )
    shares = max(1, _safe_int(pos.get("shares", pos.get("size", 1)), 1))

    if entry <= 0 or exit_price <= 0:
        return 0.0

    if _is_short_like(pos):
        return round((entry - exit_price) * shares, 4)

    return round((exit_price - entry) * shares, 4)


def _review_price_package(pos: Dict[str, Any]) -> Dict[str, Any]:
    pos = _safe_dict(pos)
    vehicle = _norm_vehicle(pos)
    symbol = _norm_symbol(pos.get("symbol"))

    if vehicle == VEHICLE_OPTION:
        current, quote = _option_stored_market_price(pos)
        entry = _option_entry_price(pos)

        underlying_context = _first_positive_float(
            pos.get("underlying_price"),
            pos.get("current_underlying_price"),
            pos.get("stock_price"),
        )

        return {
            "symbol": symbol,
            "vehicle": vehicle,
            "entry": round(entry, 4),
            "current": round(current, 4),
            "atr": _safe_float(pos.get("atr", 0.0), 0.0),
            "price_basis": "OPTION_PREMIUM_ONLY",
            "quote": quote,
            "underlying_price": round(underlying_context, 4) if underlying_context > 0 else 0.0,
            "underlying_price_used_for_close_decision": False,
        }

    fallback = pos.get(
        "current_price",
        pos.get(
            "underlying_price",
            pos.get("stock_price", pos.get("entry", pos.get("price", 0.0))),
        ),
    )
    current = _latest_underlying_price(symbol, fallback)
    entry = _first_positive_float(
        pos.get("entry"),
        pos.get("entry_price"),
        pos.get("fill_price"),
        pos.get("price"),
    )

    return {
        "symbol": symbol,
        "vehicle": vehicle,
        "entry": round(entry, 4),
        "current": round(current, 4),
        "atr": _safe_float(pos.get("atr", 0.0), 0.0),
        "price_basis": "STOCK_UNDERLYING",
        "quote": {
            "source": "safe_download_underlying",
            "price_basis": "STOCK_UNDERLYING",
        },
        "underlying_price": round(current, 4),
        "underlying_price_used_for_close_decision": True,
    }


def _print_review_line(
    *,
    symbol: str,
    vehicle: str,
    current: float,
    stop: float,
    target: float,
    action: str,
    basis: str,
) -> None:
    if vehicle == VEHICLE_OPTION:
        display_current = round(current, 4)
        display_stop = round(stop, 4)
        display_target = round(target, 4)
    else:
        display_current = round(current, 2)
        display_stop = round(stop, 2)
        display_target = round(target, 2)

    print(
        f"{symbol} | Vehicle: {vehicle} | "
        f"Current: {display_current} | Stop: {display_stop} | "
        f"Target: {display_target} | Basis: {basis} | Action: {action}"
    )


def _close_reviewed_position(
    *,
    pos: Dict[str, Any],
    symbol: str,
    vehicle: str,
    current: float,
    action: str,
    price_package: Dict[str, Any],
    stop_level: float,
    target_level: float,
) -> Any:
    pnl = _calculate_pnl(pos, vehicle, current)

    # close_trade.close_position in your system currently accepts:
    #     close_position(symbol, current, action)
    #
    # Keep that compatibility. If close_trade later supports pnl/trade_id/metadata,
    # that can be upgraded in engine/close_trade.py.
    closed = close_position(symbol, current, action)

    if isinstance(closed, dict):
        closed.setdefault("vehicle", vehicle)
        closed.setdefault("price_basis", price_package.get("price_basis"))
        closed.setdefault("calculated_review_pnl", pnl)
        closed.setdefault("underlying_price_used_for_close_decision", vehicle != VEHICLE_OPTION)
        closed.setdefault("review_exit_price", current)
        closed.setdefault("review_stop", stop_level)
        closed.setdefault("review_target", target_level)

    return closed


def review_positions() -> List[Dict[str, Any]]:
    positions = show_positions()
    print("OPEN POSITION REVIEW")

    reviews: List[Dict[str, Any]] = []

    if not positions:
        print("No open positions.")
        return reviews

    for pos in positions:
        if not isinstance(pos, dict):
            continue

        symbol = _safe_str(pos.get("symbol"), "").upper()
        if not symbol:
            continue

        vehicle = _norm_vehicle(pos)

        if vehicle == VEHICLE_RESEARCH_ONLY:
            print(f"{symbol} | Research-only position skipped.")
            continue

        price_package = _review_price_package(pos)

        entry = _safe_float(price_package.get("entry"), 0.0)
        current = _safe_float(price_package.get("current"), 0.0)
        atr = _safe_float(price_package.get("atr"), 0.0)
        basis = _safe_str(price_package.get("price_basis"), "")

        if entry <= 0:
            print(f"{symbol} | Vehicle: {vehicle} | Missing entry price")
            continue

        if current <= 0:
            print(f"{symbol} | Vehicle: {vehicle} | No usable current price")
            continue

        raw_stop = _safe_float(pos.get("stop", 0.0), 0.0)
        raw_target = _safe_float(pos.get("target", 0.0), 0.0)

        stop_level = _ensure_stop(
            entry=entry,
            raw_stop=raw_stop,
            current=current,
            atr=atr,
            vehicle=vehicle,
            pos=pos,
        )

        target_level = _ensure_target(
            entry=entry,
            raw_target=raw_target,
            vehicle=vehicle,
            pos=pos,
        )

        action = review_exit(current, stop_level, target_level)

        review = {
            "symbol": symbol,
            "trade_id": _safe_str(pos.get("trade_id"), ""),
            "vehicle": vehicle,
            "strategy": _safe_str(pos.get("strategy"), "").upper(),
            "entry": round(entry, 4),
            "current": round(current, 4),
            "current_price": round(current, 4),
            "stop": round(stop_level, 4),
            "target": round(target_level, 4),
            "action": action,
            "price_basis": basis,
            "quote": _safe_dict(price_package.get("quote")),
            "underlying_price": price_package.get("underlying_price"),
            "underlying_price_used_for_close_decision": price_package.get(
                "underlying_price_used_for_close_decision",
                vehicle != VEHICLE_OPTION,
            ),
            "contract_symbol": _option_contract_symbol(pos) if vehicle == VEHICLE_OPTION else "",
            "expiry": _option_expiry(pos) if vehicle == VEHICLE_OPTION else "",
            "calculated_pnl_if_closed": _calculate_pnl(pos, vehicle, current),
        }
        reviews.append(review)

        _print_review_line(
            symbol=symbol,
            vehicle=vehicle,
            current=current,
            stop=stop_level,
            target=target_level,
            action=action,
            basis=basis,
        )

        if action in {"STOP_LOSS", "TAKE_PROFIT"}:
            closed = _close_reviewed_position(
                pos=pos,
                symbol=symbol,
                vehicle=vehicle,
                current=current,
                action=action,
                price_package=price_package,
                stop_level=stop_level,
                target_level=target_level,
            )

            if isinstance(closed, dict) and closed.get("closed"):
                print(
                    f"CLOSED: {symbol} | Reason: {action} | "
                    f"PnL: {closed.get('pnl', closed.get('calculated_review_pnl'))}"
                )
            elif isinstance(closed, dict):
                print(
                    f"CLOSE ATTEMPTED: {symbol} | Reason: {action} | "
                    f"Result: {closed}"
                )
            else:
                print(f"CLOSE ATTEMPTED: {symbol} | Reason: {action}")

    return reviews


def print_review_outcome_box(reviews: Optional[List[Dict[str, Any]]] = None) -> None:
    reviews = reviews if isinstance(reviews, list) else []

    print("\n" + "=" * 80)
    print("OBSERVATORY POSITION REVIEW OUTCOME")
    print("=" * 80)

    if not reviews:
        print("No reviews produced.")
        print("=" * 80)
        return

    for review in reviews:
        print(
            f"{review.get('symbol', 'UNKNOWN')} | "
            f"{review.get('vehicle', '')} | "
            f"{review.get('action', '')} | "
            f"Entry: {review.get('entry', 0.0)} | "
            f"Current: {review.get('current_price', review.get('current', 0.0))} | "
            f"Stop: {review.get('stop', 0.0)} | "
            f"Target: {review.get('target', 0.0)} | "
            f"Basis: {review.get('price_basis', '')}"
        )

    print("=" * 80)


if __name__ == "__main__":
    outcome = review_positions()
    print_review_outcome_box(outcome)


__all__ = [
    "review_positions",
    "print_review_outcome_box",
]
