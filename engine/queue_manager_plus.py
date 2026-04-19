from __future__ import annotations
from typing import Any, Dict, List
from engine.trade_queue import add_trade, clear_trade_queue
from engine.sector_cap import sector_allowed
from engine.correlation_filter import correlation_allowed


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


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


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _confidence_rank(value: str) -> int:
    return {"LOW": 1, "MEDIUM": 2, "HIGH": 3}.get(_safe_str(value, "LOW").upper(), 1)


def _vehicle_rank(value: str) -> int:
    return {"OPTION": 3, "STOCK": 2, "RESEARCH_ONLY": 1}.get(_safe_str(value, "RESEARCH_ONLY").upper(), 1)


def _candidate_rank_key(trade: Dict[str, Any]):
    fused_score = _safe_float(
        trade.get("fused_score", trade.get("score", 0.0)),
        0.0,
    )
    confidence = _safe_str(trade.get("confidence", "LOW"), "LOW").upper()
    readiness_score = _safe_float(trade.get("readiness_score", 0.0), 0.0)
    promotion_score = _safe_float(trade.get("promotion_score", 0.0), 0.0)
    rebuild_pressure = _safe_float(trade.get("rebuild_pressure", 0.0), 0.0)
    option_contract_score = _safe_float(trade.get("option_contract_score", 0.0), 0.0)
    vehicle_selected = _safe_str(
        trade.get("vehicle_selected", trade.get("vehicle", "RESEARCH_ONLY")),
        "RESEARCH_ONLY",
    ).upper()

    return (
        fused_score,
        _confidence_rank(confidence),
        readiness_score,
        promotion_score,
        option_contract_score,
        -rebuild_pressure,
        _vehicle_rank(vehicle_selected),
    )


def queue_top_trades_plus(trades, limit=3):
    trades = _safe_list(trades)
    limit = int(limit or 0)

    if limit <= 0:
        clear_trade_queue()
        return []

    ranked = sorted(
        [t for t in trades if isinstance(t, dict)],
        key=_candidate_rank_key,
        reverse=True,
    )

    clear_trade_queue()
    selected: List[Dict[str, Any]] = []

    for trade in ranked:
        if len(selected) >= limit:
            break

        symbol = _norm_symbol(trade.get("symbol"))
        if not symbol:
            continue

        if not sector_allowed(selected, symbol):
            continue

        if not correlation_allowed(selected, symbol):
            continue

        selected_trade = dict(trade)
        selected.append(selected_trade)
        add_trade(selected_trade)

    return selected
