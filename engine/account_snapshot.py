from __future__ import annotations

from typing import Any, Dict

from engine.portfolio_summary import portfolio_summary


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return float(default)
        if isinstance(value, str):
            value = value.replace("$", "").replace(",", "").strip()
            if value == "":
                return float(default)
        return float(value)
    except Exception:
        return float(default)


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


def account_snapshot() -> Dict[str, Any]:
    portfolio = portfolio_summary()

    cash = round(_safe_float(portfolio.get("cash"), 0.0), 2)
    buying_power = round(_safe_float(portfolio.get("buying_power"), cash), 2)
    equity = round(_safe_float(portfolio.get("equity"), 0.0), 2)

    estimated_account_value = round(
        _safe_float(portfolio.get("estimated_account_value"), equity),
        2,
    )

    return {
        "cash": cash,
        "buying_power": buying_power,
        "equity": equity,
        "open_positions": _safe_int(portfolio.get("open_positions"), 0),
        "realized_pnl": round(_safe_float(portfolio.get("realized_pnl"), 0.0), 2),
        "unrealized_pnl": round(_safe_float(portfolio.get("unrealized_pnl"), 0.0), 2),
        "estimated_account_value": estimated_account_value,
        "gross_capital_open": round(_safe_float(portfolio.get("gross_capital_open"), 0.0), 2),
        "total_market_value_open": round(_safe_float(portfolio.get("total_market_value_open"), 0.0), 2),
        "vehicle_mix": portfolio.get("vehicle_mix", {}),
        "option_safety": portfolio.get("option_safety", {}),
        "account_math": portfolio.get("account_math", {}),
    }


def get_account_snapshot() -> Dict[str, Any]:
    return account_snapshot()


def build_account_snapshot() -> Dict[str, Any]:
    return account_snapshot()


def print_account_snapshot() -> None:
    snap = account_snapshot()

    print("ACCOUNT SNAPSHOT")
    print(f"Cash: {snap.get('cash')}")
    print(f"Buying Power: {snap.get('buying_power')}")
    print(f"Equity: {snap.get('equity')}")
    print(f"Open Positions: {snap.get('open_positions')}")
    print(f"Realized PnL: {snap.get('realized_pnl')}")
    print(f"Unrealized PnL: {snap.get('unrealized_pnl')}")
    print(f"Estimated Account Value: {snap.get('estimated_account_value')}")


__all__ = [
    "account_snapshot",
    "get_account_snapshot",
    "build_account_snapshot",
    "print_account_snapshot",
]
