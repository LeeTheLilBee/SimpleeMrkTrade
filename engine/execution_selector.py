from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


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


def _symbol(row: Dict[str, Any]) -> str:
    return _safe_str(row.get("symbol"), "").upper()


def select_for_execution(
    candidates: List[Dict[str, Any]] | None,
    *,
    available_cash: float,
    reserve_floor: float,
    limit: int = 3,
    current_open_positions: int = 0,
    max_open_positions: int = 3,
    allow_soft_reserve: bool = False,
) -> Dict[str, Any]:
    candidates = candidates if isinstance(candidates, list) else []
    working_cash = _safe_float(available_cash, 0.0)
    reserve_floor = _safe_float(reserve_floor, 0.0)
    current_open_positions = _safe_int(current_open_positions, 0)
    max_open_positions = _safe_int(max_open_positions, 0)

    remaining_slots = max(0, max_open_positions - current_open_positions)
    effective_limit = min(max(0, _safe_int(limit, 0)), remaining_slots)

    print("OPTION B SELECTOR START")
    print({
        "available_cash": working_cash,
        "reserve_floor": reserve_floor,
        "candidate_count": len(candidates),
        "limit": limit,
        "remaining_slots": remaining_slots,
        "effective_limit": effective_limit,
        "allow_soft_reserve": allow_soft_reserve,
    })

    ranked = []
    for row in candidates:
        item = deepcopy(_safe_dict(row))
        if not item:
            continue
        ranked.append(item)

    ranked.sort(
        key=lambda x: (
            _safe_float(x.get("fused_score", x.get("score", 0.0)), 0.0),
            _safe_float(x.get("score", 0.0), 0.0),
        ),
        reverse=True,
    )

    selected: List[Dict[str, Any]] = []
    decisions: List[Dict[str, Any]] = []

    for row in ranked:
        symbol = _symbol(row)
        vehicle_selected = _safe_str(row.get("vehicle_selected", "RESEARCH_ONLY"), "RESEARCH_ONLY").upper()
        capital_required = _safe_float(row.get("capital_required", 0.0), 0.0)
        minimum_trade_cost = _safe_float(row.get("minimum_trade_cost", capital_required), capital_required)
        effective_cost = minimum_trade_cost if minimum_trade_cost > 0 else capital_required
        remaining_after = round(working_cash - effective_cost, 4)

        decision = {
            "symbol": symbol,
            "vehicle_selected": vehicle_selected,
            "score": _safe_float(row.get("score", 0.0), 0.0),
            "capital_required": capital_required,
            "minimum_trade_cost": minimum_trade_cost,
            "effective_cost": effective_cost,
            "available_cash_before": round(working_cash, 4),
            "reserve_floor": round(reserve_floor, 4),
            "remaining_after": remaining_after,
            "chosen": False,
            "selector_reason": "",
        }

        if len(selected) >= effective_limit:
            decision["selector_reason"] = "queue_limit_or_position_cap_reached"
        elif vehicle_selected == "RESEARCH_ONLY":
            decision["selector_reason"] = "research_only_candidate"
        elif effective_cost <= 0:
            decision["selector_reason"] = "invalid_cost"
        elif remaining_after < reserve_floor and not allow_soft_reserve:
            decision["selector_reason"] = "fails_reserve"
        else:
            decision["chosen"] = True
            decision["selector_reason"] = "fits_with_reserve_and_slots"
            selected.append(row)
            working_cash = remaining_after

        print("OPTION B SELECTOR:", decision)
        decisions.append(decision)

    print("OPTION B SELECTOR FINAL:", {
        "selected_symbols": [_symbol(row) for row in selected],
        "ending_cash_after_selection": round(working_cash, 4),
        "reserve_floor": round(reserve_floor, 4),
        "remaining_slots": remaining_slots,
        "effective_limit": effective_limit,
    })

    return {
        "selected": selected,
        "selected_symbols": [_symbol(row) for row in selected],
        "decisions": decisions,
        "ending_cash_after_selection": round(working_cash, 4),
        "reserve_floor": round(reserve_floor, 4),
        "remaining_slots": remaining_slots,
        "effective_limit": effective_limit,
    }
