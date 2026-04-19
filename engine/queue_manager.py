from __future__ import annotations
from typing import Any, Dict, List

from engine.trade_queue import add_trade
from engine.sector_cap import sector_allowed


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _candidate_rank_key(trade: Dict[str, Any]):
    return _safe_float(trade.get("fused_score", trade.get("score", 0.0)), 0.0)


def queue_top_trades(trades, limit=3):
    trades = trades if isinstance(trades, list) else []
    limit = int(limit or 0)
    if limit <= 0:
        return []

    ranked = sorted(
        [t for t in trades if isinstance(t, dict)],
        key=_candidate_rank_key,
        reverse=True,
    )

    selected: List[Dict[str, Any]] = []

    for trade in ranked:
        if len(selected) >= limit:
            break

        symbol = str(trade.get("symbol", "") or "").upper().strip()
        if not symbol:
            continue

        if sector_allowed(selected, symbol):
            selected_trade = dict(trade)
            selected.append(selected_trade)
            add_trade(selected_trade)

    return selected
