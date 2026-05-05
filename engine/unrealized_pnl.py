from __future__ import annotations

"""
Observatory Unrealized PnL
==========================

Purpose:
- Calculate unrealized PnL from stored open positions only.
- Never fetch live underlying stock prices.
- Never use underlying stock price as option current price.
- Preserve compatibility with old imports/calls:
    from engine.unrealized_pnl import unrealized_pnl
    from engine.unrealized_pnl import calculate_unrealized_pnl

Important:
- OPTION PnL = (current_option_premium - entry_option_premium) * contracts * 100
- STOCK PnL  = (current_price - entry_price) * shares
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


OPEN_FILE = "data/open_positions.json"

VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"
VEHICLE_UNKNOWN = "UNKNOWN"


# =============================================================================
# Safe helpers
# =============================================================================

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


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _safe_optional_float(value: Any) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _round_money(value: Any, default: float = 0.0) -> float:
    return round(_safe_float(value, default), 2)


def _round4(value: Any, default: float = 0.0) -> float:
    return round(_safe_float(value, default), 4)


def _read_json(path_str: str, default: Any) -> Any:
    path = Path(path_str)
    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _open_positions() -> List[Dict[str, Any]]:
    rows = _read_json(OPEN_FILE, [])
    return [row for row in _safe_list(rows) if isinstance(row, dict)]


def _norm_vehicle(pos: Dict[str, Any]) -> str:
    vehicle = _safe_str(
        pos.get("vehicle_selected", pos.get("vehicle", VEHICLE_UNKNOWN)),
        VEHICLE_UNKNOWN,
    ).upper()

    if vehicle in {"OPTIONS", "OPTION_CONTRACT"}:
        return VEHICLE_OPTION

    if vehicle in {"EQUITY", "SHARES"}:
        return VEHICLE_STOCK

    if vehicle not in {VEHICLE_OPTION, VEHICLE_STOCK, VEHICLE_RESEARCH_ONLY}:
        return VEHICLE_UNKNOWN

    return vehicle


def _norm_strategy(pos: Dict[str, Any]) -> str:
    return _safe_str(pos.get("strategy", pos.get("direction", "")), "").upper()


def _direction(pos: Dict[str, Any]) -> str:
    raw = _safe_str(pos.get("direction", ""), "").upper()
    if raw in {"LONG", "SHORT"}:
        return raw

    strategy = _norm_strategy(pos)
    if strategy in {"PUT", "SHORT", "BEARISH"}:
        return "LONG"

    return "LONG"


def _nested_option(pos: Dict[str, Any]) -> Dict[str, Any]:
    for key in ("option", "best_option", "selected_option", "contract", "option_contract"):
        nested = pos.get(key)
        if isinstance(nested, dict):
            return nested
    return {}


def _contracts(pos: Dict[str, Any]) -> int:
    value = _safe_float(
        pos.get(
            "contracts",
            pos.get("contract_count", pos.get("quantity", 1)),
        ),
        1.0,
    )
    try:
        return max(0, int(value))
    except Exception:
        return 1


def _shares(pos: Dict[str, Any]) -> float:
    return max(
        0.0,
        _safe_float(
            pos.get("shares", pos.get("quantity", pos.get("size", 0.0))),
            0.0,
        ),
    )


# =============================================================================
# Option premium resolution
# =============================================================================

def _option_entry_premium(pos: Dict[str, Any]) -> Tuple[float, str]:
    option = _nested_option(pos)

    candidates = [
        ("entry_premium", pos.get("entry_premium")),
        ("option_entry_price", pos.get("option_entry_price")),
        ("option_entry_premium", pos.get("option_entry_premium")),
        ("premium_entry", pos.get("premium_entry")),
        ("fill_price", pos.get("fill_price")),
        ("entry", pos.get("entry")),
        ("entry_price", pos.get("entry_price")),
        ("price_reference", pos.get("price_reference")),
        ("selected_price_reference", pos.get("selected_price_reference")),
        ("option.price_reference", option.get("price_reference")),
        ("option.selected_price_reference", option.get("selected_price_reference")),
        ("option.mark", option.get("mark")),
        ("option.last", option.get("last")),
    ]

    for source, value in candidates:
        resolved = _safe_optional_float(value)
        if resolved is not None and resolved > 0:
            return round(resolved, 4), source

    return 0.0, "missing_option_entry_premium"


def _option_current_premium(pos: Dict[str, Any], entry: float) -> Tuple[float, str, bool]:
    """
    Returns:
        current premium,
        source,
        leak_blocked

    This intentionally refuses to use current_price when current_price looks like
    underlying stock price instead of option premium.
    """
    option = _nested_option(pos)

    candidates = [
        ("current_option_mark", pos.get("current_option_mark")),
        ("option_current_mark", pos.get("option_current_mark")),
        ("current_premium", pos.get("current_premium")),
        ("premium_current", pos.get("premium_current")),
        ("option_current_price", pos.get("option_current_price")),
        ("current_option_price", pos.get("current_option_price")),
        ("option.current_option_mark", option.get("current_option_mark")),
        ("option.option_current_mark", option.get("option_current_mark")),
        ("option.current_premium", option.get("current_premium")),
        ("option.option_current_price", option.get("option_current_price")),
        ("option.price_reference", option.get("price_reference")),
        ("option.selected_price_reference", option.get("selected_price_reference")),
        ("option.mark", option.get("mark")),
        ("option.last", option.get("last")),
    ]

    for source, value in candidates:
        resolved = _safe_optional_float(value)
        if resolved is not None and resolved > 0:
            return round(resolved, 4), source, False

    legacy_current = _safe_optional_float(pos.get("current_price"))
    underlying = _safe_optional_float(pos.get("underlying_price"))

    if legacy_current is not None and legacy_current > 0:
        # If current_price matches or resembles the underlying, block it.
        if underlying is not None and underlying > 0:
            near_underlying = abs(legacy_current - underlying) <= max(1.0, underlying * 0.03)
            impossible_vs_entry = entry > 0 and legacy_current > max(entry * 8.0, entry + 25.0)
            if near_underlying or impossible_vs_entry:
                return round(entry, 4), "blocked_legacy_current_price_underlying_leak", True

        # If no underlying is present, still reject absurd option jumps.
        if entry > 0 and legacy_current > max(entry * 8.0, entry + 25.0):
            return round(entry, 4), "blocked_legacy_current_price_suspicious_option_leak", True

        # Compatibility only: allowed when it still looks like a premium.
        return round(legacy_current, 4), "safe_legacy_current_price", False

    return round(entry, 4), "fallback_to_entry_premium", False


def _option_cost_basis(entry: float, contracts: int) -> float:
    return round(entry * max(contracts, 0) * 100.0, 2)


def _option_market_value(current: float, contracts: int) -> float:
    return round(current * max(contracts, 0) * 100.0, 2)


def _option_unrealized_pnl(pos: Dict[str, Any]) -> Dict[str, Any]:
    entry, entry_source = _option_entry_premium(pos)
    current, current_source, leak_blocked = _option_current_premium(pos, entry)

    contracts = _contracts(pos)
    direction = _direction(pos)

    cost_basis = _option_cost_basis(entry, contracts)
    market_value = _option_market_value(current, contracts)

    if direction == "SHORT":
        pnl = round((entry - current) * contracts * 100.0, 2)
    else:
        pnl = round((current - entry) * contracts * 100.0, 2)

    pnl_pct = round((pnl / cost_basis) * 100.0, 4) if cost_basis > 0 else 0.0

    return {
        "symbol": _safe_str(pos.get("symbol"), "UNKNOWN").upper(),
        "trade_id": _safe_str(pos.get("trade_id"), ""),
        "vehicle": VEHICLE_OPTION,
        "strategy": _norm_strategy(pos),
        "direction": direction,
        "entry": round(entry, 4),
        "current": round(current, 4),
        "entry_premium": round(entry, 4),
        "current_premium": round(current, 4),
        "underlying_price": _round4(pos.get("underlying_price"), 0.0),
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
        "valid": entry > 0 and contracts > 0,
    }


# =============================================================================
# Stock PnL resolution
# =============================================================================

def _stock_entry_price(pos: Dict[str, Any]) -> Tuple[float, str]:
    candidates = [
        ("entry", pos.get("entry")),
        ("entry_price", pos.get("entry_price")),
        ("price", pos.get("price")),
        ("fill_price", pos.get("fill_price")),
    ]

    for source, value in candidates:
        resolved = _safe_optional_float(value)
        if resolved is not None and resolved > 0:
            return round(resolved, 4), source

    return 0.0, "missing_stock_entry_price"


def _stock_current_price(pos: Dict[str, Any], entry: float) -> Tuple[float, str]:
    candidates = [
        ("current_price", pos.get("current_price")),
        ("current", pos.get("current")),
        ("market_price", pos.get("market_price")),
        ("last_price", pos.get("last_price")),
        ("price", pos.get("price")),
    ]

    for source, value in candidates:
        resolved = _safe_optional_float(value)
        if resolved is not None and resolved > 0:
            return round(resolved, 4), source

    return round(entry, 4), "fallback_to_entry_price"


def _stock_unrealized_pnl(pos: Dict[str, Any]) -> Dict[str, Any]:
    entry, entry_source = _stock_entry_price(pos)
    current, current_source = _stock_current_price(pos, entry)

    shares = _shares(pos)
    direction = _direction(pos)

    cost_basis = round(entry * shares, 2)
    market_value = round(current * shares, 2)

    if direction == "SHORT":
        pnl = round((entry - current) * shares, 2)
    else:
        pnl = round((current - entry) * shares, 2)

    pnl_pct = round((pnl / cost_basis) * 100.0, 4) if cost_basis > 0 else 0.0

    return {
        "symbol": _safe_str(pos.get("symbol"), "UNKNOWN").upper(),
        "trade_id": _safe_str(pos.get("trade_id"), ""),
        "vehicle": VEHICLE_STOCK,
        "strategy": _norm_strategy(pos),
        "direction": direction,
        "entry": round(entry, 4),
        "current": round(current, 4),
        "entry_premium": 0.0,
        "current_premium": 0.0,
        "underlying_price": round(current, 4),
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
        "option_underlying_leak_blocked": False,
        "entry_source": entry_source,
        "current_source": current_source,
        "valid": entry > 0 and shares > 0,
    }


def _empty_position_result(pos: Dict[str, Any], vehicle: str) -> Dict[str, Any]:
    return {
        "symbol": _safe_str(pos.get("symbol"), "UNKNOWN").upper(),
        "trade_id": _safe_str(pos.get("trade_id"), ""),
        "vehicle": vehicle,
        "strategy": _norm_strategy(pos),
        "direction": _direction(pos),
        "entry": 0.0,
        "current": 0.0,
        "entry_premium": 0.0,
        "current_premium": 0.0,
        "underlying_price": _round4(pos.get("underlying_price"), 0.0),
        "contracts": 0,
        "shares": 0,
        "pnl": 0.0,
        "unrealized_pnl": 0.0,
        "pnl_pct": 0.0,
        "cost_basis": 0.0,
        "market_value": 0.0,
        "pnl_basis": "not_tradeable_position",
        "price_review_basis": "NONE",
        "monitoring_price_type": "NONE",
        "underlying_price_used_for_pnl": False,
        "option_underlying_leak_blocked": False,
        "entry_source": "none",
        "current_source": "none",
        "valid": False,
    }


# =============================================================================
# Public API
# =============================================================================

def calculate_unrealized_pnl() -> Dict[str, Any]:
    positions = _open_positions()

    detail_rows: List[Dict[str, Any]] = []
    vehicle_mix = {
        VEHICLE_OPTION: 0,
        VEHICLE_STOCK: 0,
        VEHICLE_RESEARCH_ONLY: 0,
        VEHICLE_UNKNOWN: 0,
    }

    total_unrealized = 0.0
    total_cost_basis = 0.0
    total_market_value = 0.0

    option_positions = 0
    underlying_used_for_option_pnl = False
    leak_blocked_count = 0

    for pos in positions:
        vehicle = _norm_vehicle(pos)

        if vehicle not in vehicle_mix:
            vehicle = VEHICLE_UNKNOWN

        vehicle_mix[vehicle] += 1

        if vehicle == VEHICLE_OPTION:
            row = _option_unrealized_pnl(pos)
            option_positions += 1
            if row.get("underlying_price_used_for_pnl"):
                underlying_used_for_option_pnl = True
            if row.get("option_underlying_leak_blocked"):
                leak_blocked_count += 1

        elif vehicle == VEHICLE_STOCK:
            row = _stock_unrealized_pnl(pos)

        else:
            row = _empty_position_result(pos, vehicle)

        detail_rows.append(row)
        total_unrealized += _safe_float(row.get("unrealized_pnl"), 0.0)
        total_cost_basis += _safe_float(row.get("cost_basis"), 0.0)
        total_market_value += _safe_float(row.get("market_value"), 0.0)

    return {
        "total_unrealized": round(total_unrealized, 2),
        "total_cost_basis": round(total_cost_basis, 2),
        "total_market_value": round(total_market_value, 2),
        "positions": detail_rows,
        "open_positions": len(positions),
        "vehicle_mix": vehicle_mix,
        "option_safety": {
            "option_positions": option_positions,
            "underlying_used_for_option_pnl": bool(underlying_used_for_option_pnl),
            "leak_blocked_count": int(leak_blocked_count),
            "basis": "OPTION positions use premium math only.",
        },
    }


def unrealized_pnl() -> Dict[str, Any]:
    """
    Backward-compatible name used by engine/bot.py.
    """
    return calculate_unrealized_pnl()


def print_unrealized_pnl() -> Dict[str, Any]:
    result = calculate_unrealized_pnl()

    print("UNREALIZED PNL")
    print(f"Open Positions: {result.get('open_positions')}")
    print(f"Total Unrealized: {result.get('total_unrealized')}")
    print(f"Total Cost Basis: {result.get('total_cost_basis')}")
    print(f"Total Market Value: {result.get('total_market_value')}")
    print(f"Vehicle Mix: {result.get('vehicle_mix')}")
    print(f"Option Safety: {result.get('option_safety')}")

    for row in result.get("positions", []):
        print(
            f"{row.get('symbol')} | "
            f"Vehicle: {row.get('vehicle')} | "
            f"Entry: {row.get('entry')} | "
            f"Current: {row.get('current')} | "
            f"PnL: {row.get('unrealized_pnl')} | "
            f"Basis: {row.get('pnl_basis')} | "
            f"Source: {row.get('current_source')}"
        )

    return result


__all__ = [
    "calculate_unrealized_pnl",
    "unrealized_pnl",
    "print_unrealized_pnl",
]
