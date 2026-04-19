from __future__ import annotations

from typing import Any


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def stop_loss_price(entry_price, atr=None, percent=0.03):
    entry_price = _safe_float(entry_price, 0.0)
    atr = None if atr is None else _safe_float(atr, 0.0)
    percent = _safe_float(percent, 0.03)

    if entry_price <= 0:
        return 0.0

    if atr is not None and atr > 0:
        return round(max(0.0, entry_price - atr), 4)

    return round(max(0.0, entry_price * (1 - percent)), 4)


def take_profit_price(entry_price, atr=None, percent=0.08):
    entry_price = _safe_float(entry_price, 0.0)
    atr = None if atr is None else _safe_float(atr, 0.0)
    percent = _safe_float(percent, 0.08)

    if entry_price <= 0:
        return 0.0

    if atr is not None and atr > 0:
        return round(entry_price + (atr * 2), 4)

    return round(entry_price * (1 + percent), 4)
