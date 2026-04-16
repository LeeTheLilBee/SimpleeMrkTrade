from typing import Any, Dict

from engine.account_state import buying_power, load_state
from engine.paper_portfolio import open_count
from engine.trade_history import executed_trade_count_today
from engine.risk_governor import governor_status


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _estimate_trade_cost(trade: Dict[str, Any]) -> Dict[str, float]:
    price = _safe_float(
        trade.get("price", trade.get("entry", trade.get("current_price", 0))),
        0.0,
    )
    size = _safe_float(trade.get("size", trade.get("shares", 1)), 1.0)
    commission = _safe_float(trade.get("commission", 1.0), 1.0)

    if size <= 0:
        size = 1.0

    gross_cost = price * size
    total_cost = gross_cost + commission

    return {
        "price": round(price, 4),
        "size": round(size, 4),
        "commission": round(commission, 4),
        "gross_cost": round(gross_cost, 4),
        "total_cost": round(total_cost, 4),
    }


def _scaled_min_cash_reserve(cash: float, buying_power_now: float) -> float:
    """
    Reserve should scale off currently deployable funds,
    not total equity including already-committed capital.
    """
    base = max(min(cash, buying_power_now), 0.0)

    if base <= 500:
        reserve = base * 0.20
    elif base <= 2000:
        reserve = base * 0.15
    else:
        reserve = base * 0.10

    return round(max(25.0, reserve), 2)


def can_execute_trade(trade: Dict[str, Any], available_buying_power: float | None = None) -> Dict[str, Any]:
    current_open_positions = _safe_int(open_count(), 0)
    executed_entries_today = _safe_int(executed_trade_count_today(), 0)

    gov = governor_status(
        current_open_positions=current_open_positions,
        executed_entries_today=executed_entries_today,
    )

    state = load_state()

    limits = gov.get("limits", {}) if isinstance(gov, dict) else {}
    controls = gov.get("controls", {}) if isinstance(gov, dict) else {}

    cash = _safe_float(gov.get("cash", state.get("cash", 0.0)), 0.0)
    equity = _safe_float(gov.get("equity", state.get("equity", 0.0)), 0.0)
    buying_power_now = _safe_float(
        available_buying_power if available_buying_power is not None else buying_power(),
        cash,
    )

    max_open_positions = _safe_int(limits.get("max_open_positions", 3), 3)
    min_cash_reserve = _scaled_min_cash_reserve(cash, buying_power_now)

    estimate = _estimate_trade_cost(trade)
    total_cost = estimate["total_cost"]
    projected_cash_after = cash - total_cost
    projected_buying_power_after = buying_power_now - total_cost

    if controls.get("kill_switch", False):
        return {
            "blocked": True,
            "reason": "kill_switch_active",
            "cash": cash,
            "equity": equity,
            "buying_power": buying_power_now,
            "trade_cost": total_cost,
            "projected_cash_after": projected_cash_after,
            "projected_buying_power_after": projected_buying_power_after,
            "min_cash_reserve": min_cash_reserve,
        }

    if controls.get("max_open_positions", False) or current_open_positions >= max_open_positions:
        return {
            "blocked": True,
            "reason": "max_open_positions_reached",
            "cash": cash,
            "equity": equity,
            "buying_power": buying_power_now,
            "trade_cost": total_cost,
            "projected_cash_after": projected_cash_after,
            "projected_buying_power_after": projected_buying_power_after,
            "current_open_positions": current_open_positions,
            "max_open_positions": max_open_positions,
            "min_cash_reserve": min_cash_reserve,
        }

    if total_cost > buying_power_now:
        return {
            "blocked": True,
            "reason": "insufficient_buying_power",
            "cash": cash,
            "equity": equity,
            "buying_power": buying_power_now,
            "trade_cost": total_cost,
            "projected_cash_after": projected_cash_after,
            "projected_buying_power_after": projected_buying_power_after,
            "min_cash_reserve": min_cash_reserve,
        }

    if projected_cash_after < min_cash_reserve:
        return {
            "blocked": True,
            "reason": "cash_reserve_would_be_broken",
            "cash": cash,
            "equity": equity,
            "buying_power": buying_power_now,
            "trade_cost": total_cost,
            "projected_cash_after": projected_cash_after,
            "projected_buying_power_after": projected_buying_power_after,
            "min_cash_reserve": min_cash_reserve,
        }

    return {
        "blocked": False,
        "reason": "allowed",
        "cash": cash,
        "equity": equity,
        "buying_power": buying_power_now,
        "trade_cost": total_cost,
        "projected_cash_after": projected_cash_after,
        "projected_buying_power_after": projected_buying_power_after,
        "min_cash_reserve": min_cash_reserve,
    }
