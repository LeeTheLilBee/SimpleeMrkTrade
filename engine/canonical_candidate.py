from __future__ import annotations
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        return bool(value)
    except Exception:
        return default


def _normalize_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _now_iso() -> str:
    return datetime.now().isoformat()


def _first_nonempty(*values: Any, default: str = "") -> str:
    for value in values:
        text = _safe_str(value, "")
        if text:
            return text
    return default


def _first_list(*values: Any) -> List[Any]:
    for value in values:
        if isinstance(value, list) and value:
            return value
    return []


def _best_price(trade: Dict[str, Any]) -> float:
    candidates = [
        trade.get("current_price"),
        trade.get("price"),
        trade.get("entry"),
        trade.get("fill_price"),
        trade.get("requested_price"),
        trade.get("underlying_price"),
        trade.get("market_price"),
        trade.get("latest_price"),
    ]
    for value in candidates:
        price = _safe_float(value, 0.0)
        if price > 0:
            return price
    return 0.0


def build_canonical_candidate(
    trade: Dict[str, Any],
    *,
    status: str = "candidate",
    reason: str = "",
    mode: str = "",
    breadth: str = "",
    volatility_state: str = "",
    decision_reason: str = "",
    selected_for_execution: bool = False,
    capital_required: float | None = None,
    capital_available: float | None = None,
    stronger_competing_setups: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    trade = _safe_dict(deepcopy(trade))
    stronger_competing_setups = (
        stronger_competing_setups if isinstance(stronger_competing_setups, list) else []
    )

    symbol = _normalize_symbol(trade.get("symbol"))
    strategy = _safe_str(trade.get("strategy"), "CALL").upper()
    score = round(_safe_float(trade.get("score"), 0.0), 2)
    confidence = _safe_str(trade.get("confidence"), "LOW").upper()

    base_price = _best_price(trade)
    entry = round(_safe_float(trade.get("entry", base_price), base_price), 2)
    current_price = round(_safe_float(trade.get("current_price", base_price), base_price), 2)

    stop_default = round(entry * (1.03 if strategy == "PUT" else 0.97), 2) if entry > 0 else 0.0
    target_default = round(entry * (0.90 if strategy == "PUT" else 1.10), 2) if entry > 0 else 0.0

    stop = round(_safe_float(trade.get("stop", stop_default), stop_default), 2)
    target = round(_safe_float(trade.get("target", target_default), target_default), 2)
    atr = round(_safe_float(trade.get("atr", 0.0), 0.0), 2)
    rsi = round(_safe_float(trade.get("rsi", 0.0), 0.0), 2)

    option = _safe_dict(trade.get("option"))
    has_option = bool(option)

    canonical = {
        "symbol": symbol,
        "company_name": _first_nonempty(
            trade.get("company_name"),
            trade.get("company"),
            symbol,
        ),
        "status": _safe_str(status, "candidate"),
        "strategy": strategy,
        "score": score,
        "confidence": confidence,
        "grade": _safe_str(trade.get("grade"), ""),
        "setup_type": _safe_str(trade.get("setup_type"), ""),
        "setup_family": _safe_str(trade.get("setup_family"), ""),
        "entry_quality": _safe_str(trade.get("entry_quality"), ""),
        "trend": _safe_str(trade.get("trend"), ""),
        "mode": _first_nonempty(mode, trade.get("mode")),
        "regime": _safe_str(trade.get("regime"), ""),
        "breadth": _first_nonempty(breadth, trade.get("breadth")),
        "volatility_state": _first_nonempty(volatility_state, trade.get("volatility_state")),
        "sector": _safe_str(trade.get("sector"), "General"),
        "entry": entry,
        "current_price": current_price,
        "stop": stop,
        "target": target,
        "atr": atr,
        "rsi": rsi,
        "price": round(_safe_float(trade.get("price", base_price), base_price), 2),
        "fill_price": round(_safe_float(trade.get("fill_price", 0.0), 0.0), 2),
        "requested_price": round(_safe_float(trade.get("requested_price", 0.0), 0.0), 2),
        "capital_required": round(_safe_float(capital_required, 0.0), 2)
        if capital_required is not None else None,
        "capital_available": round(_safe_float(capital_available, 0.0), 2)
        if capital_available is not None else None,
        "capital_buffer_after": (
            round(_safe_float(capital_available, 0.0) - _safe_float(capital_required, 0.0), 2)
            if capital_required is not None and capital_available is not None
            else None
        ),
        "decision_reason": _first_nonempty(
            decision_reason,
            trade.get("decision_reason"),
            trade.get("rejection_reason"),
            reason,
        ),
        "decision_label": _first_nonempty(
            reason,
            trade.get("decision_label"),
            trade.get("rejection_reason"),
            status,
        ),
        "selected_for_execution": _safe_bool(selected_for_execution, False),
        "has_option": has_option,
        "option_contract_score": round(_safe_float(trade.get("option_contract_score"), 0.0), 2),
        "option": option if has_option else {},
        "option_explanation": _first_list(
            trade.get("option_explanation"),
            trade.get("elite_lines"),
        ),
        "why": _first_list(
            trade.get("why"),
            trade.get("rejection_analysis"),
            trade.get("pro_lines"),
        ),
        "supports": _safe_list(trade.get("supports")),
        "blockers": _safe_list(trade.get("blockers")),
        "rejection_analysis": _safe_list(trade.get("rejection_analysis")),
        "stronger_competing_setups": stronger_competing_setups,
        "timestamp": _first_nonempty(trade.get("timestamp"), _now_iso()),
        "source": _safe_str(trade.get("source"), "engine"),
        "raw": trade,
    }

    if not canonical["why"]:
        fallback_lines = []
        if canonical["decision_reason"]:
            fallback_lines.append(canonical["decision_reason"])
        if canonical["setup_family"]:
            fallback_lines.append(f"Setup family: {canonical['setup_family']}")
        if canonical["entry_quality"]:
            fallback_lines.append(f"Entry quality: {canonical['entry_quality']}")
        canonical["why"] = fallback_lines

    return canonical
