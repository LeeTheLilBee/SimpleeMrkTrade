from typing import Any, Dict, List


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
        return int(value)
    except Exception:
        return int(default)


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    try:
        return str(value).strip()
    except Exception:
        return default


def _normalize_upper(value: Any, default: str = "") -> str:
    text = _safe_str(value, default)
    return text.upper() if text else default


def candidate_capital_need(candidate: Dict[str, Any]) -> float:
    minimum_trade_cost = _safe_float(candidate.get("minimum_trade_cost"), 0.0)
    capital_required = _safe_float(candidate.get("capital_required"), 0.0)
    estimated_cost = _safe_float(candidate.get("estimated_cost"), 0.0)

    for value in (minimum_trade_cost, capital_required, estimated_cost):
        if value > 0:
            return round(value, 2)
    return 0.0


def diagnose_reserve_queue_fit(
    candidates: List[Dict[str, Any]],
    cash: float,
    reserve_floor: float,
    queue_limit: int = 3,
    allow_soft_reserve: bool = False,
) -> Dict[str, Any]:
    print("RESERVE SELECTOR MODULE:", __file__)

    cash = round(_safe_float(cash, 0.0), 2)
    reserve_floor = round(_safe_float(reserve_floor, 0.0), 2)
    queue_limit = max(_safe_int(queue_limit, 3), 1)
    spendable_cash = round(max(cash - reserve_floor, 0.0), 2)

    enriched: List[Dict[str, Any]] = []

    for raw in candidates or []:
        candidate = raw if isinstance(raw, dict) else {}
        symbol = _safe_str(candidate.get("symbol"), "UNKNOWN")
        vehicle = _normalize_upper(
            candidate.get("vehicle_selected") or candidate.get("selected_vehicle"),
            "UNKNOWN",
        )
        score = _safe_float(
            candidate.get("fused_score", candidate.get("score", 0.0)),
            0.0,
        )
        confidence = _normalize_upper(candidate.get("confidence"), "UNKNOWN")
        capital_need = candidate_capital_need(candidate)
        post_trade_cash = round(cash - capital_need, 2)
        fits_alone_with_reserve = post_trade_cash >= reserve_floor

        enriched.append(
            {
                "symbol": symbol,
                "vehicle_selected": vehicle,
                "score": round(score, 2),
                "confidence": confidence,
                "capital_need": capital_need,
                "cash_before": cash,
                "reserve_floor": reserve_floor,
                "spendable_cash": spendable_cash,
                "post_trade_cash_if_alone": post_trade_cash,
                "fits_alone_with_reserve": fits_alone_with_reserve,
                "soft_fit_only": (not fits_alone_with_reserve and allow_soft_reserve),
                "raw_candidate": candidate,
            }
        )

    enriched.sort(
        key=lambda row: (
            -row["score"],
            row["capital_need"],
            row["symbol"],
        )
    )

    selected: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    running_cash = cash

    for item in enriched:
        if len(selected) >= queue_limit:
            skipped.append(
                {
                    **item,
                    "skip_reason": "queue_limit_reached",
                    "running_cash_before_decision": round(running_cash, 2),
                }
            )
            continue

        capital_need = _safe_float(item.get("capital_need"), 0.0)
        post_trade_cash = round(running_cash - capital_need, 2)
        preserves_reserve = post_trade_cash >= reserve_floor

        if capital_need <= 0:
            skipped.append(
                {
                    **item,
                    "skip_reason": "no_capital_need_found",
                    "running_cash_before_decision": round(running_cash, 2),
                    "post_trade_cash_sequential": post_trade_cash,
                }
            )
            continue

        if capital_need > running_cash:
            skipped.append(
                {
                    **item,
                    "skip_reason": "insufficient_cash",
                    "running_cash_before_decision": round(running_cash, 2),
                    "post_trade_cash_sequential": post_trade_cash,
                }
            )
            continue

        if not preserves_reserve and not allow_soft_reserve:
            skipped.append(
                {
                    **item,
                    "skip_reason": "would_violate_reserve_floor",
                    "running_cash_before_decision": round(running_cash, 2),
                    "post_trade_cash_sequential": post_trade_cash,
                    "reserve_gap_after_trade": round(reserve_floor - post_trade_cash, 2),
                }
            )
            continue

        selected.append(
            {
                **item,
                "running_cash_before_decision": round(running_cash, 2),
                "post_trade_cash_sequential": post_trade_cash,
                "selection_reason": (
                    "fits_with_reserve"
                    if preserves_reserve
                    else "soft_selected_despite_reserve"
                ),
            }
        )
        running_cash = post_trade_cash

    return {
        "cash": cash,
        "reserve_floor": reserve_floor,
        "spendable_cash": spendable_cash,
        "queue_limit": queue_limit,
        "allow_soft_reserve": allow_soft_reserve,
        "selected_symbols": [row["symbol"] for row in selected],
        "selected": selected,
        "skipped": skipped,
        "all_candidates_ranked": enriched,
        "cash_after_selected_queue": round(running_cash, 2),
    }


def select_reserve_safe_candidates(
    candidates: List[Dict[str, Any]],
    cash: float,
    reserve_floor: float,
    queue_limit: int = 3,
    allow_soft_reserve: bool = False,
) -> List[Dict[str, Any]]:
    debug = diagnose_reserve_queue_fit(
        candidates=candidates,
        cash=cash,
        reserve_floor=reserve_floor,
        queue_limit=queue_limit,
        allow_soft_reserve=allow_soft_reserve,
    )
    return [row["raw_candidate"] for row in debug["selected"]]
