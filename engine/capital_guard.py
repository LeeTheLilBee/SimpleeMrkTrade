from __future__ import annotations
from typing import Any, Dict, List
from engine.account_state import buying_power


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _trade_cost(trade: Dict[str, Any]) -> float:
    if not isinstance(trade, dict):
        return 0.0

    minimum_trade_cost = _safe_float(trade.get("minimum_trade_cost"), 0.0)
    if minimum_trade_cost > 0:
        return round(minimum_trade_cost, 2)

    capital_required = _safe_float(trade.get("capital_required"), 0.0)
    if capital_required > 0:
        return round(capital_required, 2)

    vehicle_selected = _safe_str(
        trade.get("vehicle_selected", trade.get("vehicle", "RESEARCH_ONLY")),
        "RESEARCH_ONLY",
    ).upper()

    if vehicle_selected == "OPTION":
        option = trade.get("option") if isinstance(trade.get("option"), dict) else {}
        mark = _safe_float(
            option.get("mark", option.get("ask", option.get("last", option.get("price", 0.0)))),
            0.0,
        )
        contracts = int(_safe_float(trade.get("contracts", 1), 1))
        if mark > 0:
            return round((mark * 100 * max(contracts, 1)) + 1.0, 2)

    price = _safe_float(
        trade.get("price", trade.get("current_price", trade.get("entry", 0.0))),
        0.0,
    )
    shares = int(_safe_float(trade.get("shares", trade.get("size", 1)), 1))
    if price > 0:
        return round((price * max(shares, 1)) + 1.0, 2)

    return 0.0


def affordable_trade_count(trades):
    trades = trades if isinstance(trades, list) else []
    bp = _safe_float(buying_power(), 0.0)
    count = 0

    ranked = sorted(
        [t for t in trades if isinstance(t, dict)],
        key=lambda x: _trade_cost(x),
    )

    for trade in ranked:
        cost = _trade_cost(trade)
        if cost <= 0:
            continue
        if cost <= bp:
            count += 1
            bp -= cost

    return count
