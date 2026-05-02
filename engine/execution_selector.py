from __future__ import annotations

from typing import Any, Dict, List, Optional

from engine.reserve_selector import diagnose_reserve_queue_fit


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _norm_vehicle(value: Any) -> str:
    vehicle = _safe_str(value, "RESEARCH_ONLY").upper()
    if vehicle in {"OPTION", "STOCK", "RESEARCH_ONLY", "NONE"}:
        return vehicle
    return "RESEARCH_ONLY"


def _score_of(trade: Dict[str, Any]) -> float:
    return _safe_float(trade.get("fused_score", trade.get("score", 0.0)), 0.0)


def _effective_cost(trade: Dict[str, Any]) -> float:
    minimum_trade_cost = _safe_float(trade.get("minimum_trade_cost"), 0.0)
    capital_required = _safe_float(trade.get("capital_required"), 0.0)
    estimated_cost = _safe_float(trade.get("estimated_cost"), 0.0)

    if minimum_trade_cost > 0:
        return minimum_trade_cost
    if capital_required > 0:
        return capital_required
    if estimated_cost > 0:
        return estimated_cost
    return 0.0


def _mode_reserve_floor(
    *,
    available_cash: float,
    mode_context: Optional[Dict[str, Any]] = None,
) -> float:
    context = _safe_dict(mode_context)
    reserve_floor_pct = _safe_float(context.get("reserve_floor_pct"), 0.10)
    return round(max(0.0, available_cash * reserve_floor_pct), 2)


def _allow_soft_reserve_for_mode(
    *,
    trading_mode: str,
    mode_context: Optional[Dict[str, Any]] = None,
    explicit_allow_soft_reserve: bool = False,
) -> bool:
    context = _safe_dict(mode_context)
    mode = _safe_str(trading_mode, context.get("mode", "paper")).lower()

    if explicit_allow_soft_reserve:
        return True

    if bool(context.get("reserve_warning_only", False)):
        return True

    if bool(context.get("execution_warning_only", False)):
        return True

    if mode in {"survey", "deep_space"}:
        return True

    return False


def _debug_row(
    trade: Dict[str, Any],
    *,
    available_cash_before: float,
    reserve_floor: float,
    chosen: bool,
    reason: str,
    remaining_after: Optional[float] = None,
) -> Dict[str, Any]:
    cost = _effective_cost(trade)

    if remaining_after is None:
        remaining_after = available_cash_before - cost

    return {
        "symbol": _norm_symbol(trade.get("symbol")),
        "vehicle_selected": _norm_vehicle(
            trade.get("vehicle_selected")
            or trade.get("selected_vehicle")
            or trade.get("vehicle")
        ),
        "score": round(_score_of(trade), 2),
        "capital_required": round(_safe_float(trade.get("capital_required"), 0.0), 2),
        "minimum_trade_cost": round(_safe_float(trade.get("minimum_trade_cost"), 0.0), 2),
        "estimated_cost": round(_safe_float(trade.get("estimated_cost"), 0.0), 2),
        "effective_cost": round(cost, 2),
        "available_cash_before": round(available_cash_before, 2),
        "reserve_floor": round(reserve_floor, 2),
        "remaining_after": round(_safe_float(remaining_after, 0.0), 2),
        "chosen": bool(chosen),
        "selector_reason": _safe_str(reason, "unknown"),
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
    """
    Selects the final execution queue.

    Purpose:
    - Rank strongest execution-ready candidates first.
    - Respect the queue limit.
    - Spend sequentially from available cash.
    - Preserve reserve rules.
    - In warning-only paper/survey mode, allow soft reserve behavior when configured.
    """

    context = _safe_dict(mode_context)
    limit = max(_safe_int(limit, 3), 0)
    available_cash = round(_safe_float(available_cash, 0.0), 2)

    if limit <= 0:
        print("OPTION B SELECTOR FINAL:", {
            "selected_symbols": [],
            "reason": "limit_zero",
            "available_cash": available_cash,
        })
        return []

    reserve_floor = _mode_reserve_floor(
        available_cash=available_cash,
        mode_context=context,
    )

    soft_reserve = _allow_soft_reserve_for_mode(
        trading_mode=trading_mode,
        mode_context=context,
        explicit_allow_soft_reserve=allow_soft_reserve,
    )

    ranked_candidates = [
        dict(candidate)
        for candidate in execution_ready
        if isinstance(candidate, dict)
    ]

    ranked_candidates = [
        candidate for candidate in ranked_candidates
        if bool(candidate.get("research_approved", True))
        and bool(candidate.get("execution_ready", False))
        and _norm_vehicle(
            candidate.get("vehicle_selected")
            or candidate.get("selected_vehicle")
            or candidate.get("vehicle")
        ) not in {"RESEARCH_ONLY", "NONE"}
        and _effective_cost(candidate) > 0
    ]

    ranked_candidates.sort(
        key=lambda trade: (
            _score_of(trade),
            _safe_float(trade.get("option_contract_score", trade.get("contract_score", 0.0)), 0.0),
            -_effective_cost(trade),
        ),
        reverse=True,
    )

    print("OPTION B SELECTOR MODULE:", __file__)
    print("OPTION B SELECTOR START")
    print({
        "trading_mode": _safe_str(trading_mode, "paper"),
        "available_cash": available_cash,
        "reserve_floor": reserve_floor,
        "candidate_count": len(ranked_candidates),
        "limit": limit,
        "allow_soft_reserve": soft_reserve,
    })

    diagnosis = diagnose_reserve_queue_fit(
        candidates=ranked_candidates,
        cash=available_cash,
        reserve_floor=reserve_floor,
        queue_limit=limit,
        allow_soft_reserve=soft_reserve,
    )

    selected_rows = diagnosis.get("selected", []) if isinstance(diagnosis, dict) else []
    skipped_rows = diagnosis.get("skipped", []) if isinstance(diagnosis, dict) else []

    for row in selected_rows:
        row = _safe_dict(row)
        raw_candidate = _safe_dict(row.get("raw_candidate"))

        print("OPTION B SELECTOR:", _debug_row(
            raw_candidate,
            available_cash_before=_safe_float(
                row.get("running_cash_before_decision"),
                available_cash,
            ),
            reserve_floor=reserve_floor,
            chosen=True,
            reason=_safe_str(row.get("selection_reason"), "selected"),
            remaining_after=_safe_float(
                row.get("post_trade_cash_sequential"),
                available_cash,
            ),
        ))

    for row in skipped_rows:
        row = _safe_dict(row)
        raw_candidate = _safe_dict(row.get("raw_candidate"))

        print("OPTION B SELECTOR:", _debug_row(
            raw_candidate,
            available_cash_before=_safe_float(
                row.get("running_cash_before_decision"),
                available_cash,
            ),
            reserve_floor=reserve_floor,
            chosen=False,
            reason=_safe_str(row.get("skip_reason"), "skipped"),
            remaining_after=_safe_float(
                row.get("post_trade_cash_sequential"),
                row.get("post_trade_cash_if_alone", available_cash),
            ),
        ))

    selected: List[Dict[str, Any]] = []

    for row in selected_rows:
        row = _safe_dict(row)
        candidate = dict(_safe_dict(row.get("raw_candidate")))

        if not candidate:
            continue

        candidate["selected_for_execution"] = True
        candidate["execution_ready"] = True
        candidate["research_approved"] = True
        candidate["final_reason"] = "selected_for_execution"
        candidate["final_reason_code"] = "selected_for_execution"
        candidate["blocked_at"] = ""
        candidate["selector_reason"] = _safe_str(row.get("selection_reason"), "selected")
        candidate["selector_cash_before"] = round(
            _safe_float(row.get("running_cash_before_decision"), available_cash),
            2,
        )
        candidate["selector_cash_after"] = round(
            _safe_float(row.get("post_trade_cash_sequential"), available_cash),
            2,
        )
        candidate["selector_reserve_floor"] = reserve_floor
        candidate["selector_soft_reserve"] = soft_reserve

        selected.append(candidate)

    print("OPTION B SELECTOR FINAL:", {
        "selected_symbols": [_norm_symbol(t.get("symbol")) for t in selected],
        "ending_cash_after_selection": round(
            _safe_float(
                diagnosis.get("cash_after_selected_queue", available_cash)
                if isinstance(diagnosis, dict)
                else available_cash,
                available_cash,
            ),
            2,
        ),
        "reserve_floor": reserve_floor,
        "selected_count": len(selected),
    })

    return selected


__all__ = [
    "choose_execution_queue_option_b",
]
