from typing import Any, Dict, List, Optional

from engine.reserve_selector import diagnose_reserve_queue_fit


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    try:
        return str(value).strip()
    except Exception:
        return default


def _normalize_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _normalize_vehicle(value: Any) -> str:
    return _safe_str(value, "RESEARCH_ONLY").upper()


def _mode_reserve_floor(
    *,
    available_cash: float,
    mode_context: Optional[Dict[str, Any]] = None,
) -> float:
    mode_context = mode_context if isinstance(mode_context, dict) else {}
    reserve_floor_pct = _safe_float(mode_context.get("reserve_floor_pct"), 0.10)
    return round(max(0.0, available_cash * reserve_floor_pct), 2)


def _build_selector_debug_row(
    trade: Dict[str, Any],
    *,
    available_cash_before: float,
    reserve_floor: float,
    chosen: bool,
    reason: str,
    remaining_after: Optional[float] = None,
) -> Dict[str, Any]:
    score = _safe_float(trade.get("fused_score", trade.get("score", 0.0)), 0.0)
    capital_required = _safe_float(trade.get("capital_required"), 0.0)
    minimum_trade_cost = _safe_float(trade.get("minimum_trade_cost"), 0.0)
    estimated_cost = _safe_float(trade.get("estimated_cost"), 0.0)

    effective_cost = minimum_trade_cost
    if effective_cost <= 0:
        effective_cost = capital_required
    if effective_cost <= 0:
        effective_cost = estimated_cost

    if remaining_after is None:
        remaining_after = round(available_cash_before - effective_cost, 2)

    return {
        "symbol": _normalize_symbol(trade.get("symbol")),
        "vehicle_selected": _normalize_vehicle(
            trade.get("vehicle_selected") or trade.get("selected_vehicle")
        ),
        "score": round(score, 2),
        "capital_required": round(capital_required, 2),
        "minimum_trade_cost": round(minimum_trade_cost, 2),
        "estimated_cost": round(estimated_cost, 2),
        "effective_cost": round(effective_cost, 2),
        "available_cash_before": round(available_cash_before, 2),
        "reserve_floor": round(reserve_floor, 2),
        "remaining_after": round(remaining_after, 2),
        "chosen": chosen,
        "selector_reason": reason,
    }


def choose_execution_queue_option_b(
    execution_ready: List[Dict[str, Any]],
    *,
    limit: int = 3,
    available_cash: float = 0.0,
    trading_mode: str = "paper",
    mode_context: Optional[Dict[str, Any]] = None,
    allow_soft_reserve: bool = False,
) -> List[Dict[str, Any]]:
    mode_context = mode_context if isinstance(mode_context, dict) else {}
    limit = max(_safe_int(limit, 3), 0)
    available_cash = round(_safe_float(available_cash, 0.0), 2)

    reserve_floor = _mode_reserve_floor(
        available_cash=available_cash,
        mode_context=mode_context,
    )

    ranked_candidates = [
        candidate for candidate in execution_ready
        if isinstance(candidate, dict)
    ]
    ranked_candidates.sort(
        key=lambda trade: (
            _safe_float(trade.get("fused_score", trade.get("score", 0.0)), 0.0),
            _safe_float(trade.get("score", 0.0), 0.0),
        ),
        reverse=True,
    )

    print("OPTION B SELECTOR MODULE:", __file__)
    print("OPTION B SELECTOR START")
    print(
        {
            "trading_mode": _safe_str(trading_mode, "paper"),
            "available_cash": available_cash,
            "reserve_floor": reserve_floor,
            "candidate_count": len(ranked_candidates),
            "limit": limit,
            "allow_soft_reserve": allow_soft_reserve,
        }
    )

    diagnosis = diagnose_reserve_queue_fit(
        candidates=ranked_candidates,
        cash=available_cash,
        reserve_floor=reserve_floor,
        queue_limit=limit if limit > 0 else 1,
        allow_soft_reserve=allow_soft_reserve,
    )

    for row in diagnosis.get("selected", []):
        debug_row = _build_selector_debug_row(
            row.get("raw_candidate", {}),
            available_cash_before=_safe_float(row.get("running_cash_before_decision"), available_cash),
            reserve_floor=reserve_floor,
            chosen=True,
            reason=_safe_str(row.get("selection_reason"), "selected"),
            remaining_after=_safe_float(row.get("post_trade_cash_sequential"), available_cash),
        )
        print("OPTION B SELECTOR:", debug_row)

    for row in diagnosis.get("skipped", []):
        debug_row = _build_selector_debug_row(
            row.get("raw_candidate", {}),
            available_cash_before=_safe_float(row.get("running_cash_before_decision"), available_cash),
            reserve_floor=reserve_floor,
            chosen=False,
            reason=_safe_str(row.get("skip_reason"), "skipped"),
            remaining_after=_safe_float(
                row.get("post_trade_cash_sequential"),
                row.get("post_trade_cash_if_alone"),
            ),
        )
        print("OPTION B SELECTOR:", debug_row)

    selected = [row.get("raw_candidate", {}) for row in diagnosis.get("selected", [])]

    print(
        "OPTION B SELECTOR FINAL:",
        {
            "selected_symbols": [_normalize_symbol(t.get("symbol")) for t in selected],
            "ending_cash_after_selection": round(
                _safe_float(diagnosis.get("cash_after_selected_queue"), available_cash),
                2,
            ),
            "reserve_floor": reserve_floor,
        },
    )

    return selected
