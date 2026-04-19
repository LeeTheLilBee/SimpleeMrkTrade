from __future__ import annotations

from typing import Any
from engine.account_state import load_state


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def position_size(price, atr=None, risk_pct=0.01, min_size=1, max_size=None):
    state = load_state() if callable(load_state) else {}
    equity = _safe_float(state.get("equity", 1000), 1000.0)
    price = _safe_float(price, 0.0)
    atr = None if atr is None else _safe_float(atr, 0.0)
    risk_pct = _safe_float(risk_pct, 0.01)

    if equity <= 0 or price <= 0:
        return 0

    risk_budget = equity * risk_pct

    if atr is not None and atr > 0:
        raw_size = int(risk_budget / atr)
    else:
        raw_size = int(risk_budget / price)

    if raw_size < min_size:
        raw_size = min_size

    if isinstance(max_size, int) and max_size > 0:
        raw_size = min(raw_size, max_size)

    return max(0, int(raw_size))
    return max(1, size)
