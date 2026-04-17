from typing import Any, Dict
from engine.account_state import buying_power, load_state, resolve_min_cash_reserve
from engine.paper_portfolio import open_count
from engine.trade_history import executed_trade_count
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
    option_obj = trade.get("option")
    commission = _safe_float(trade.get("commission", 1.0), 1.0)

    if isinstance(option_obj, dict) and option_obj:
        contract_price = _safe_float(
            option_obj.get("ask", option_obj.get("last", option_obj.get("price", 0))),
            0.0,
        )
        contracts = max(1, _safe_int(trade.get("contracts", 1), 1))
        gross_cost = contract_price * 100 * contracts
        total_cost = gross_cost + commission
        return {
            "price": round(contract_price, 4),
            "size": float(contracts),
            "commission": round(commission, 4),
            "gross_cost": round(gross_cost, 4),
            "total_cost": round(total_cost, 4),
        }

    price = _safe_float(
        trade.get("current_price", trade.get("price", trade.get("entry", 0))),
        0.0,
    )
    size = _safe_float(trade.get("size", trade.get("shares", 1)), 1.0)
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


def can_execute_trade(trade: Dict[str, Any], available_buying_power: float | None = None) -> Dict[str, Any]:
    current_open_positions = _safe_int(open_count(), 0)
    executed_trades_today = _safe_int(executed_trade_count(), 0)

    gov = governor_status(
        current_open_positions=current_open_positions,
        executed_trades_today=executed_trades_today,
    )

    limits = gov.get("limits", {}) if isinstance(gov, dict) else {}
    controls = gov.get("controls", {}) if isinstance(gov, dict) else {}

    state = load_state()
    cash = _safe_float(gov.get("cash", state.get("cash", 0.0)), 0.0)
    equity = _safe_float(gov.get("equity", state.get("equity", 0.0)), 0.0)

    buying_power_now = _safe_float(
        available_buying_power if available_buying_power is not None else buying_power(),
        cash,
    )

    max_open_positions = _safe_int(limits.get("max_open_positions", 3), 3)
    min_cash_reserve = _safe_float(
        limits.get("min_cash_reserve", resolve_min_cash_reserve(state)),
        resolve_min_cash_reserve(state),
    )

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

    if controls.get("cash_reserve_too_low", False) and cash <= min_cash_reserve:
        return {
            "blocked": True,
            "reason": "cash_reserve_already_too_low",
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
