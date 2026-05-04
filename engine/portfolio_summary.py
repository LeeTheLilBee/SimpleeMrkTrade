from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


OPEN_FILE = "data/open_positions.json"
CLOSED_FILE = "data/closed_positions.json"
ACCOUNT_FILE = "data/account_state.json"

OPTION_CONTRACT_MULTIPLIER = 100

VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"
VEHICLE_UNKNOWN = "UNKNOWN"

MIN_VALID_OPTION_PREMIUM = 0.01
OPTION_UNDERLYING_LEAK_MULTIPLE = 8.0
OPTION_UNDERLYING_LEAK_ABSOLUTE = 25.0


# =============================================================================
# Safe helpers
# =============================================================================

def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return float(default)
        if isinstance(value, bool):
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
        if value is None:
            return None
        if isinstance(value, bool):
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
        if value is None:
            return int(default)
        if isinstance(value, bool):
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


def _upper(value: Any, default: str = "") -> str:
    return _safe_str(value, default).upper()


def _read_json(path_str: str, default: Any) -> Any:
    path = Path(path_str)
    if not path.exists():
        return default
    try:
        with open(path_str, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _round_price(value: Any) -> float:
    return round(_safe_float(value, 0.0), 4)


def _round_money(value: Any) -> float:
    return round(_safe_float(value, 0.0), 2)


# =============================================================================
# Position shape helpers
# =============================================================================

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

    contract_symbol = _safe_str(
        pos.get(
            "contract_symbol",
            pos.get(
                "option_symbol",
                pos.get(
                    "option_contract_symbol",
                    option_obj.get(
                        "contractSymbol",
                        contract_obj.get("contractSymbol", ""),
                    ),
                ),
            ),
        ),
        "",
    )

    right = _upper(
        pos.get("right", option_obj.get("right", contract_obj.get("right", ""))),
        "",
    )

    if contract_symbol or right in {"CALL", "PUT", "C", "P"}:
        return VEHICLE_OPTION

    return VEHICLE_UNKNOWN


def _strategy(pos: Dict[str, Any]) -> str:
    return _upper(pos.get("strategy", pos.get("direction", "CALL")), "CALL")


def _direction(pos: Dict[str, Any]) -> str:
    strategy = _strategy(pos)
    if "PUT" in strategy or "SHORT" in strategy:
        return "SHORT"
    return "LONG"


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
# Option premium safety
# =============================================================================

def _underlying_price(pos: Dict[str, Any]) -> Optional[float]:
    for value in [
        pos.get("underlying_price"),
        pos.get("current_underlying_price"),
        pos.get("stock_price"),
        pos.get("underlying_last"),
        pos.get("underlying_mark"),
        pos.get("spot_price"),
        pos.get("last_underlying_price"),
        pos.get("market_price"),
    ]:
        price = _safe_optional_float(value)
        if price is not None and price > 0:
            return round(price, 4)
    return None


def _looks_like_underlying_leak(
    *,
    option_entry: Optional[float],
    candidate_price: Optional[float],
    underlying_price: Optional[float],
) -> bool:
    if candidate_price is None:
        return False

    if underlying_price is not None and underlying_price > 0:
        tolerance = max(0.05, underlying_price * 0.002)
        if abs(candidate_price - underlying_price) <= tolerance:
            return True

    if option_entry is not None and option_entry > 0:
        if (
            candidate_price >= OPTION_UNDERLYING_LEAK_ABSOLUTE
            and candidate_price >= option_entry * OPTION_UNDERLYING_LEAK_MULTIPLE
        ):
            return True

    return False


def _option_entry_premium(pos: Dict[str, Any]) -> Tuple[float, str]:
    pos = _safe_dict(pos)
    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))
    underlying = _underlying_price(pos)

    candidates: List[Tuple[str, Any]] = [
        ("entry_premium", pos.get("entry_premium")),
        ("premium_entry", pos.get("premium_entry")),
        ("option_entry", pos.get("option_entry")),
        ("option_entry_price", pos.get("option_entry_price")),
        ("entry_option_mark", pos.get("entry_option_mark")),
        ("contract_entry_price", pos.get("contract_entry_price")),
        ("fill_premium", pos.get("fill_premium")),
        ("average_premium", pos.get("average_premium")),
        ("avg_premium", pos.get("avg_premium")),
        ("debit", pos.get("debit")),
        ("price_paid", pos.get("price_paid")),
        ("fill_price", pos.get("fill_price")),
        ("executed_price", pos.get("executed_price")),
        ("entry", pos.get("entry")),
        ("entry_price", pos.get("entry_price")),

        ("option.entry_premium", option.get("entry_premium")),
        ("option.premium_entry", option.get("premium_entry")),
        ("option.entry_price", option.get("entry_price")),
        ("option.mark_at_entry", option.get("mark_at_entry")),
        ("option.fill_price", option.get("fill_price")),
        ("option.executed_price", option.get("executed_price")),
        ("option.selected_price_reference", option.get("selected_price_reference")),
        ("option.price_reference", option.get("price_reference")),
        ("option.mark", option.get("mark")),

        ("contract.entry_premium", contract.get("entry_premium")),
        ("contract.premium_entry", contract.get("premium_entry")),
        ("contract.entry_price", contract.get("entry_price")),
        ("contract.selected_price_reference", contract.get("selected_price_reference")),
        ("contract.price_reference", contract.get("price_reference")),
        ("contract.mark", contract.get("mark")),
    ]

    for source, value in candidates:
        price = _safe_optional_float(value)
        if price is None or price < MIN_VALID_OPTION_PREMIUM:
            continue

        if _looks_like_underlying_leak(
            option_entry=None,
            candidate_price=price,
            underlying_price=underlying,
        ):
            continue

        return round(price, 4), source

    return 0.0, "missing_option_entry_premium"


def _option_current_premium(pos: Dict[str, Any], entry: float) -> Tuple[float, str, bool]:
    pos = _safe_dict(pos)
    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))
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
    ]

    for source, value in candidates:
        price = _safe_optional_float(value)
        if price is None or price < MIN_VALID_OPTION_PREMIUM:
            continue

        if _looks_like_underlying_leak(
            option_entry=entry,
            candidate_price=price,
            underlying_price=underlying,
        ):
            leak_blocked = True
            continue

        return round(price, 4), source, leak_blocked

    legacy_current = _safe_optional_float(pos.get("current_price"))
    if legacy_current is not None and legacy_current >= MIN_VALID_OPTION_PREMIUM:
        if _looks_like_underlying_leak(
            option_entry=entry,
            candidate_price=legacy_current,
            underlying_price=underlying,
        ):
            leak_blocked = True
        else:
            return round(legacy_current, 4), "safe_legacy_current_price", leak_blocked

    if entry > 0:
        source = "entry_premium_fallback_after_leak_block" if leak_blocked else "entry_premium_fallback"
        return round(entry, 4), source, leak_blocked

    return 0.0, "missing_option_current_premium", leak_blocked


# =============================================================================
# Stock price helpers
# =============================================================================

def _stock_entry_price(pos: Dict[str, Any]) -> float:
    return _round_price(
        pos.get(
            "entry",
            pos.get(
                "entry_price",
                pos.get(
                    "avg_entry",
                    pos.get("average_entry", pos.get("fill_price", pos.get("price", 0.0))),
                ),
            ),
        )
    )


def _stock_current_price(pos: Dict[str, Any]) -> Tuple[float, str]:
    for source, value in [
        ("current_price", pos.get("current_price")),
        ("current_underlying_price", pos.get("current_underlying_price")),
        ("underlying_price", pos.get("underlying_price")),
        ("market_price", pos.get("market_price")),
        ("stock_price", pos.get("stock_price")),
        ("price", pos.get("price")),
        ("entry", pos.get("entry")),
    ]:
        price = _safe_float(value, 0.0)
        if price > 0:
            return round(price, 4), source

    return 0.0, "missing_stock_current_price"


# =============================================================================
# Position valuation
# =============================================================================

def _position_cost_basis(pos: Dict[str, Any]) -> float:
    vehicle = _vehicle(pos)

    if vehicle == VEHICLE_OPTION:
        entry, _ = _option_entry_premium(pos)
        return round(entry * OPTION_CONTRACT_MULTIPLIER * _contracts(pos), 2) if entry > 0 else 0.0

    if vehicle == VEHICLE_STOCK:
        entry = _stock_entry_price(pos)
        return round(entry * _shares(pos), 2) if entry > 0 else 0.0

    return 0.0


def _position_unrealized(pos: Dict[str, Any]) -> Dict[str, Any]:
    pos = _safe_dict(pos)
    symbol = _upper(pos.get("symbol", "UNKNOWN"), "UNKNOWN")
    vehicle = _vehicle(pos)
    strategy = _strategy(pos)
    direction = _direction(pos)

    if vehicle == VEHICLE_OPTION:
        entry, entry_source = _option_entry_premium(pos)
        current, current_source, leak_blocked = _option_current_premium(pos, entry)
        contracts = _contracts(pos)
        underlying = _underlying_price(pos)

        if entry > 0 and current > 0:
            pnl = round((current - entry) * OPTION_CONTRACT_MULTIPLIER * contracts, 2)
            pnl_pct = round(((current - entry) / entry) * 100.0, 4)
            market_value = round(current * OPTION_CONTRACT_MULTIPLIER * contracts, 2)
            cost_basis = round(entry * OPTION_CONTRACT_MULTIPLIER * contracts, 2)
            valid = True
        else:
            pnl = 0.0
            pnl_pct = 0.0
            market_value = 0.0
            cost_basis = 0.0
            valid = False

        return {
            "symbol": symbol,
            "trade_id": _safe_str(pos.get("trade_id"), ""),
            "vehicle": VEHICLE_OPTION,
            "strategy": strategy,
            "direction": direction,
            "entry": entry,
            "current": current,
            "entry_premium": entry,
            "current_premium": current,
            "underlying_price": underlying,
            "contracts": contracts,
            "shares": 0,
            "pnl": pnl,
            "unrealized_pnl": pnl,
            "pnl_pct": pnl_pct,
            "cost_basis": cost_basis,
            "market_value": market_value,
            "pnl_basis": "option_premium_x_100",
            "price_review_basis": "OPTION_PREMIUM_ONLY",
            "monitoring_price_type": "OPTION_PREMIUM",
            "underlying_price_used_for_pnl": False,
            "option_underlying_leak_blocked": bool(leak_blocked),
            "entry_source": entry_source,
            "current_source": current_source,
            "valid": valid,
        }

    if vehicle == VEHICLE_STOCK:
        entry = _stock_entry_price(pos)
        current, current_source = _stock_current_price(pos)
        shares = _shares(pos)

        if entry > 0 and current > 0:
            if direction == "SHORT":
                pnl = round((entry - current) * shares, 2)
                pnl_pct = round(((entry - current) / entry) * 100.0, 4)
            else:
                pnl = round((current - entry) * shares, 2)
                pnl_pct = round(((current - entry) / entry) * 100.0, 4)

            cost_basis = round(entry * shares, 2)
            market_value = round(current * shares, 2)
            valid = True
        else:
            pnl = 0.0
            pnl_pct = 0.0
            cost_basis = 0.0
            market_value = 0.0
            valid = False

        return {
            "symbol": symbol,
            "trade_id": _safe_str(pos.get("trade_id"), ""),
            "vehicle": VEHICLE_STOCK,
            "strategy": strategy,
            "direction": direction,
            "entry": entry,
            "current": current,
            "underlying_price": current,
            "contracts": 0,
            "shares": shares,
            "pnl": pnl,
            "unrealized_pnl": pnl,
            "pnl_pct": pnl_pct,
            "cost_basis": cost_basis,
            "market_value": market_value,
            "pnl_basis": "stock_price_x_shares",
            "price_review_basis": "STOCK_PRICE",
            "monitoring_price_type": "UNDERLYING",
            "underlying_price_used_for_pnl": True,
            "current_source": current_source,
            "valid": valid,
        }

    return {
        "symbol": symbol,
        "trade_id": _safe_str(pos.get("trade_id"), ""),
        "vehicle": VEHICLE_UNKNOWN if vehicle == VEHICLE_UNKNOWN else VEHICLE_RESEARCH_ONLY,
        "strategy": strategy,
        "direction": direction,
        "entry": 0.0,
        "current": 0.0,
        "contracts": 0,
        "shares": 0,
        "pnl": 0.0,
        "unrealized_pnl": 0.0,
        "pnl_pct": 0.0,
        "cost_basis": 0.0,
        "market_value": 0.0,
        "pnl_basis": "no_position",
        "price_review_basis": "NO_POSITION",
        "monitoring_price_type": "RESEARCH_ONLY",
        "underlying_price_used_for_pnl": False,
        "valid": False,
    }


# =============================================================================
# Public API
# =============================================================================

def load_open_positions() -> List[Dict[str, Any]]:
    return _safe_list(_read_json(OPEN_FILE, []))


def load_closed_positions() -> List[Dict[str, Any]]:
    return _safe_list(_read_json(CLOSED_FILE, []))


def load_account_state() -> Dict[str, Any]:
    return _safe_dict(_read_json(ACCOUNT_FILE, {}))


def calculate_unrealized_pnl() -> Dict[str, Any]:
    open_positions = load_open_positions()
    position_rows = [
        _position_unrealized(pos)
        for pos in open_positions
        if isinstance(pos, dict)
    ]

    total_unrealized = round(
        sum(_safe_float(row.get("unrealized_pnl"), 0.0) for row in position_rows),
        2,
    )
    total_cost_basis = round(
        sum(_safe_float(row.get("cost_basis"), 0.0) for row in position_rows),
        2,
    )
    total_market_value = round(
        sum(_safe_float(row.get("market_value"), 0.0) for row in position_rows),
        2,
    )

    vehicle_mix = {
        VEHICLE_OPTION: 0,
        VEHICLE_STOCK: 0,
        VEHICLE_RESEARCH_ONLY: 0,
        VEHICLE_UNKNOWN: 0,
    }

    for row in position_rows:
        vehicle = _safe_str(row.get("vehicle"), VEHICLE_UNKNOWN).upper()
        if vehicle not in vehicle_mix:
            vehicle = VEHICLE_UNKNOWN
        vehicle_mix[vehicle] += 1

    leak_blocked_count = sum(
        1 for row in position_rows if bool(row.get("option_underlying_leak_blocked", False))
    )

    return {
        "total_unrealized": total_unrealized,
        "total_cost_basis": total_cost_basis,
        "total_market_value": total_market_value,
        "positions": position_rows,
        "open_positions": len(position_rows),
        "vehicle_mix": vehicle_mix,
        "option_safety": {
            "option_positions": vehicle_mix[VEHICLE_OPTION],
            "underlying_used_for_option_pnl": False,
            "leak_blocked_count": leak_blocked_count,
            "basis": "OPTION positions use premium math only.",
        },
    }


def unrealized_pnl() -> Dict[str, Any]:
    return calculate_unrealized_pnl()


def get_unrealized_pnl() -> Dict[str, Any]:
    return calculate_unrealized_pnl()


def portfolio_summary() -> Dict[str, Any]:
    open_positions = load_open_positions()
    closed_positions = load_closed_positions()
    account = load_account_state()

    realized = 0.0
    for pos in closed_positions:
        if isinstance(pos, dict):
            realized += _safe_float(pos.get("pnl", 0.0), 0.0)

    unrealized = calculate_unrealized_pnl()

    gross_capital_open = round(
        sum(_position_cost_basis(pos) for pos in open_positions if isinstance(pos, dict)),
        2,
    )

    cash = round(_safe_float(account.get("cash", 0.0), 0.0), 2)
    buying_power = round(_safe_float(account.get("buying_power", cash), cash), 2)
    equity = round(_safe_float(account.get("equity", 0.0), 0.0), 2)

    unrealized_total = round(_safe_float(unrealized.get("total_unrealized"), 0.0), 2)
    estimated_account_value = round(equity + unrealized_total, 2)

    return {
        "open_positions": len(open_positions),
        "closed_positions": len(closed_positions),
        "realized_pnl": round(realized, 2),
        "unrealized_pnl": unrealized_total,
        "gross_capital_open": gross_capital_open,
        "total_market_value_open": round(_safe_float(unrealized.get("total_market_value"), 0.0), 2),
        "cash": cash,
        "buying_power": buying_power,
        "equity": equity,
        "estimated_account_value": estimated_account_value,
        "vehicle_mix": unrealized.get("vehicle_mix", {
            VEHICLE_OPTION: 0,
            VEHICLE_STOCK: 0,
            VEHICLE_RESEARCH_ONLY: 0,
            VEHICLE_UNKNOWN: 0,
        }),
        "net_pnl": round(realized + unrealized_total, 2),
        "unrealized_detail": unrealized,
        "option_safety": unrealized.get("option_safety", {}),
    }


def get_portfolio_summary() -> Dict[str, Any]:
    return portfolio_summary()


def build_portfolio_summary() -> Dict[str, Any]:
    return portfolio_summary()


def print_portfolio_summary() -> None:
    summary = portfolio_summary()

    print("PORTFOLIO SUMMARY")
    print(f"Open Positions: {summary.get('open_positions')}")
    print(f"Closed Positions: {summary.get('closed_positions')}")
    print(f"Realized PnL: {summary.get('realized_pnl')}")
    print(f"Unrealized PnL: {summary.get('unrealized_pnl')}")
    print(f"Gross Capital Open: {summary.get('gross_capital_open')}")
    print(f"Market Value Open: {summary.get('total_market_value_open')}")
    print(f"Cash: {summary.get('cash')}")
    print(f"Buying Power: {summary.get('buying_power')}")
    print(f"Equity: {summary.get('equity')}")
    print(f"Estimated Account Value: {summary.get('estimated_account_value')}")
    print(f"Vehicle Mix: {summary.get('vehicle_mix')}")
    print(f"Option Safety: {summary.get('option_safety')}")


__all__ = [
    "portfolio_summary",
    "get_portfolio_summary",
    "build_portfolio_summary",
    "calculate_unrealized_pnl",
    "unrealized_pnl",
    "get_unrealized_pnl",
    "print_portfolio_summary",
]
