from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional


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


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        if value is None:
            return bool(default)
        return bool(value)
    except Exception:
        return bool(default)


def _norm_symbol(value: Any) -> str:
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
            return list(value)
    return []


def _first_dict(*values: Any) -> Dict[str, Any]:
    for value in values:
        if isinstance(value, dict) and value:
            return dict(value)
    return {}


def _dedupe_keep_order(items: List[Any]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in _safe_list(items):
        text = _safe_str(item, "")
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _best_price(trade: Dict[str, Any]) -> float:
    trade = _safe_dict(trade)
    candidates = [
        trade.get("current_price"),
        trade.get("price"),
        trade.get("entry"),
        trade.get("fill_price"),
        trade.get("requested_price"),
        trade.get("underlying_price"),
        trade.get("market_price"),
        trade.get("latest_price"),
        _safe_dict(trade.get("option")).get("mark"),
        _safe_dict(trade.get("option")).get("last"),
    ]
    for value in candidates:
        price = _safe_float(value, 0.0)
        if price > 0:
            return price
    return 0.0


def _default_stop(price: float, strategy: str) -> float:
    if price <= 0:
        return 0.0
    strategy = _safe_str(strategy, "CALL").upper()
    return round(price * (1.03 if strategy == "PUT" else 0.97), 4)


def _default_target(price: float, strategy: str) -> float:
    if price <= 0:
        return 0.0
    strategy = _safe_str(strategy, "CALL").upper()
    return round(price * (0.90 if strategy == "PUT" else 1.10), 4)


def _derive_trade_id(symbol: str, strategy: str, timestamp: str) -> str:
    stamp = _safe_str(timestamp, _now_iso()).replace(":", "").replace("-", "").replace(".", "")
    return f"{symbol}-{strategy}-{stamp}"


def _derive_final_reason(
    trade: Dict[str, Any],
    *,
    status: str,
    reason: str,
    decision_reason: str,
) -> str:
    return _first_nonempty(
        trade.get("final_reason"),
        decision_reason,
        trade.get("decision_reason"),
        trade.get("rejection_reason"),
        reason,
        status,
        default=status or "candidate",
    )


def _derive_final_reason_code(
    trade: Dict[str, Any],
    *,
    status: str,
    reason: str,
    decision_reason: str,
) -> str:
    return _first_nonempty(
        trade.get("final_reason_code"),
        trade.get("decision_reason_code"),
        reason,
        decision_reason,
        trade.get("blocked_at"),
        status,
        default=status or "candidate",
    )


def _derive_blocked_at(trade: Dict[str, Any], status: str, final_reason_code: str) -> str:
    explicit = _safe_str(trade.get("blocked_at"), "")
    if explicit:
        return explicit

    status_l = _safe_str(status, "").lower()
    if status_l in {"selected", "execution_ready", "execution_ready_not_selected"}:
        return ""

    if status_l == "research_approved_not_execution_ready":
        return "execution_guard"

    if final_reason_code.startswith("failed_breadth"):
        return "breadth_guard"
    if final_reason_code.startswith("failed_score"):
        return "score_threshold"
    if final_reason_code.startswith("failed_volatility"):
        return "volatility_guard"
    if final_reason_code.startswith("reentry_blocked"):
        return "reentry_guard"
    if final_reason_code in {"already_open_position", "existing_open_position"}:
        return "duplicate_guard"
    if final_reason_code == "strategy_router_returned_no_trade":
        return "strategy_router"
    if final_reason_code in {"weak_option_contract", "option_validation_failed"}:
        return "option_executable"
    if "governor_blocked" in final_reason_code:
        return "execution_guard"

    return ""


def _derive_capital_buffer_after(capital_required: float, capital_available: float) -> float:
    return round(_safe_float(capital_available, 0.0) - _safe_float(capital_required, 0.0), 4)


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
    stronger_competing_setups: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    trade = deepcopy(_safe_dict(trade))
    stronger_competing_setups = _safe_list(stronger_competing_setups)

    symbol = _norm_symbol(trade.get("symbol"))
    strategy = _safe_str(trade.get("strategy"), "CALL").upper()
    timestamp = _first_nonempty(trade.get("timestamp"), _now_iso())

    price = round(_safe_float(trade.get("price", _best_price(trade)), _best_price(trade)), 4)
    entry = round(_safe_float(trade.get("entry", price), price), 4)
    current_price = round(_safe_float(trade.get("current_price", price), price), 4)
    requested_price = round(_safe_float(trade.get("requested_price", price), price), 4)
    fill_price = round(_safe_float(trade.get("fill_price", 0.0), 0.0), 4)

    stop = round(_safe_float(trade.get("stop", _default_stop(entry or price, strategy)), 0.0), 4)
    target = round(_safe_float(trade.get("target", _default_target(entry or price, strategy)), 0.0), 4)

    score = round(_safe_float(trade.get("score", trade.get("fused_score", 0.0)), 0.0), 4)
    fused_score = round(_safe_float(trade.get("fused_score", trade.get("score", 0.0)), 0.0), 4)
    base_score = round(_safe_float(trade.get("base_score", score), score), 4)

    confidence = _safe_str(trade.get("confidence"), "LOW").upper()
    base_confidence = _safe_str(trade.get("base_confidence", confidence), confidence).upper()
    v2_confidence = _safe_str(trade.get("v2_confidence", confidence), confidence).upper()

    option = _first_dict(trade.get("option"), trade.get("contract"))
    option_contract_score = round(
        _safe_float(
            trade.get("option_contract_score", trade.get("option_score", option.get("contract_score", 0.0))),
            0.0,
        ),
        4,
    )

    vehicle_selected = _safe_str(
        trade.get("vehicle_selected", trade.get("selected_vehicle", trade.get("vehicle", "RESEARCH_ONLY"))),
        "RESEARCH_ONLY",
    ).upper()

    resolved_capital_required = round(
        _safe_float(
            capital_required if capital_required is not None else trade.get("capital_required", 0.0),
            0.0,
        ),
        4,
    )
    resolved_capital_available = round(
        _safe_float(
            capital_available if capital_available is not None else trade.get("capital_available", 0.0),
            0.0,
        ),
        4,
    )
    minimum_trade_cost = round(_safe_float(trade.get("minimum_trade_cost", resolved_capital_required), 0.0), 4)

    final_reason = _derive_final_reason(
        trade,
        status=status,
        reason=reason,
        decision_reason=decision_reason,
    )
    final_reason_code = _derive_final_reason_code(
        trade,
        status=status,
        reason=reason,
        decision_reason=decision_reason,
    )
    blocked_at = _derive_blocked_at(trade, status, final_reason_code)

    research_approved = _safe_bool(
        trade.get("research_approved"),
        status in {
            "research_approved_not_execution_ready",
            "execution_ready",
            "execution_ready_not_selected",
            "selected",
        },
    )
    execution_ready = _safe_bool(
        trade.get("execution_ready"),
        status in {
            "execution_ready",
            "execution_ready_not_selected",
            "selected",
        },
    )
    selected_flag = _safe_bool(
        selected_for_execution or trade.get("selected_for_execution"),
        status == "selected",
    )

    why_lines = _dedupe_keep_order(
        _first_list(
            trade.get("why"),
            trade.get("rejection_analysis"),
            trade.get("pro_lines"),
        )
    )
    option_lines = _dedupe_keep_order(
        _first_list(
            trade.get("option_explanation"),
            trade.get("elite_lines"),
            option.get("contract_notes"),
        )
    )
    rejection_analysis = _dedupe_keep_order(_safe_list(trade.get("rejection_analysis")))
    supports = _dedupe_keep_order(_safe_list(trade.get("supports")))
    blockers = _dedupe_keep_order(_safe_list(trade.get("blockers")))

    v2 = _first_dict(trade.get("v2"), trade.get("v2_payload"))
    v2_payload = _first_dict(trade.get("v2_payload"), trade.get("v2"))

    if not why_lines:
        fallback = []
        if final_reason:
            fallback.append(final_reason)
        if _safe_str(trade.get("setup_family"), ""):
            fallback.append(f"Setup family: {_safe_str(trade.get('setup_family'))}")
        if _safe_str(trade.get("entry_quality"), ""):
            fallback.append(f"Entry quality: {_safe_str(trade.get('entry_quality'))}")
        if _safe_str(trade.get("v2_thesis", v2.get("thesis", "")), ""):
            fallback.append(f"V2: {_safe_str(trade.get('v2_thesis', v2.get('thesis', '')))}")
        why_lines = _dedupe_keep_order(fallback)

    trade_id = _safe_str(
        trade.get("trade_id"),
        _derive_trade_id(symbol, strategy, timestamp),
    )

    canonical = {
        "trade_id": trade_id,
        "symbol": symbol,
        "company_name": _first_nonempty(
            trade.get("company_name"),
            trade.get("company"),
            symbol,
        ),
        "sector": _safe_str(trade.get("sector"), "General"),

        "status": _safe_str(status, "candidate"),
        "source": _safe_str(trade.get("source"), "engine"),
        "timestamp": timestamp,

        "strategy": strategy,
        "direction": _safe_str(trade.get("direction"), strategy).upper(),
        "vehicle_selected": vehicle_selected,
        "selected_vehicle": vehicle_selected,
        "vehicle": vehicle_selected,
        "vehicle_reason": _safe_str(trade.get("vehicle_reason"), ""),

        "score": score,
        "base_score": base_score,
        "fused_score": fused_score,
        "confidence": confidence,
        "base_confidence": base_confidence,
        "v2_confidence": v2_confidence,
        "grade": _safe_str(trade.get("grade"), ""),

        "setup_type": _safe_str(trade.get("setup_type"), ""),
        "setup_family": _safe_str(trade.get("setup_family"), ""),
        "entry_quality": _safe_str(trade.get("entry_quality"), ""),
        "trend": _safe_str(trade.get("trend"), ""),
        "regime": _safe_str(trade.get("regime"), ""),
        "breadth": _first_nonempty(breadth, trade.get("breadth")),
        "volatility_state": _first_nonempty(volatility_state, trade.get("volatility_state")),
        "mode": _first_nonempty(mode, trade.get("mode")),
        "trading_mode": _safe_str(trade.get("trading_mode"), ""),
        "trading_mode_label": _safe_str(trade.get("trading_mode_label"), ""),
        "mode_context": _safe_dict(trade.get("mode_context")),

        "price": price,
        "entry": entry,
        "current_price": current_price,
        "requested_price": requested_price,
        "fill_price": fill_price,
        "stop": stop,
        "target": target,
        "atr": round(_safe_float(trade.get("atr", 0.0), 0.0), 4),
        "rsi": round(_safe_float(trade.get("rsi", 0.0), 0.0), 4),

        "shares": _safe_int(trade.get("shares", 0), 0),
        "contracts": _safe_int(trade.get("contracts", 0), 0),
        "size": _safe_int(trade.get("size", 0), 0),

        "capital_required": resolved_capital_required,
        "minimum_trade_cost": minimum_trade_cost,
        "capital_available": resolved_capital_available,
        "capital_buffer_after": _derive_capital_buffer_after(
            resolved_capital_required,
            resolved_capital_available,
        ),

        "decision_reason": _first_nonempty(
            decision_reason,
            trade.get("decision_reason"),
            final_reason,
            reason,
            default=final_reason,
        ),
        "decision_reason_code": _first_nonempty(
            trade.get("decision_reason_code"),
            final_reason_code,
            reason,
            default=final_reason_code,
        ),
        "decision_label": _first_nonempty(
            trade.get("decision_label"),
            reason,
            final_reason,
            status,
            default=status,
        ),
        "final_reason": final_reason,
        "final_reason_code": final_reason_code,
        "blocked_at": blocked_at,

        "research_approved": research_approved,
        "execution_ready": execution_ready,
        "selected_for_execution": selected_flag,

        "has_option": bool(option),
        "option": option if option else {},
        "contract": option if option else {},
        "option_contract_score": option_contract_score,
        "option_explanation": option_lines,
        "option_path": _safe_dict(trade.get("option_path")),
        "stock_path": _safe_dict(trade.get("stock_path")),

        "why": why_lines,
        "supports": supports,
        "blockers": blockers,
        "rejection_reason": _safe_str(trade.get("rejection_reason"), ""),
        "rejection_analysis": rejection_analysis,
        "stronger_competing_setups": stronger_competing_setups,

        "governor": _safe_dict(trade.get("governor")),
        "governor_blocked": _safe_bool(trade.get("governor_blocked"), False),
        "governor_status": _safe_str(trade.get("governor_status"), ""),
        "governor_reason": _safe_str(trade.get("governor_reason"), ""),
        "governor_reasons": _safe_list(trade.get("governor_reasons")),
        "governor_warnings": _safe_list(trade.get("governor_warnings")),

        "reserve_check": _safe_dict(trade.get("reserve_check")),
        "warnings": _safe_list(trade.get("warnings")),
        "rejection_reasons": _safe_list(trade.get("rejection_reasons")),

        "v2": v2,
        "v2_payload": v2_payload,
        "v2_score": round(_safe_float(trade.get("v2_score", v2.get("score", 0.0)), 0.0), 4),
        "v2_quality": round(_safe_float(trade.get("v2_quality", v2.get("quality", 0.0)), 0.0), 4),
        "v2_reason": _safe_str(trade.get("v2_reason", v2.get("reason", "")), ""),
        "v2_regime_alignment": _safe_str(
            trade.get("v2_regime_alignment", v2.get("regime_alignment", "")),
            "",
        ),
        "v2_signal_strength": round(
            _safe_float(trade.get("v2_signal_strength", v2.get("signal_strength", 0.0)), 0.0),
            4,
        ),
        "v2_conviction_adjustment": round(
            _safe_float(trade.get("v2_conviction_adjustment", v2.get("conviction_adjustment", 0.0)), 0.0),
            4,
        ),
        "v2_vehicle_bias": _safe_str(
            trade.get("v2_vehicle_bias", v2.get("vehicle_bias", "")),
            "",
        ).upper(),
        "v2_thesis": _safe_str(
            trade.get("v2_thesis", v2.get("thesis", "")),
            "",
        ),
        "v2_notes": _safe_list(trade.get("v2_notes", v2.get("notes", []))),
        "v2_risk_flags": _safe_list(trade.get("v2_risk_flags", v2.get("risk_flags", []))),

        "readiness_score": round(_safe_float(trade.get("readiness_score", 0.0), 0.0), 4),
        "promotion_score": round(_safe_float(trade.get("promotion_score", 0.0), 0.0), 4),
        "rebuild_pressure": round(_safe_float(trade.get("rebuild_pressure", 0.0), 0.0), 4),
        "execution_quality": round(_safe_float(trade.get("execution_quality", 0.0), 0.0), 4),

        "canonical_decision": _safe_dict(trade.get("canonical_decision")),
        "final_decision": _safe_dict(trade.get("final_decision")),

        "raw": trade,
    }

    return canonical


def summarize_canonical_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    candidate = _safe_dict(candidate)
    return {
        "trade_id": _safe_str(candidate.get("trade_id"), ""),
        "symbol": _norm_symbol(candidate.get("symbol")),
        "strategy": _safe_str(candidate.get("strategy"), "CALL").upper(),
        "status": _safe_str(candidate.get("status"), ""),
        "vehicle_selected": _safe_str(candidate.get("vehicle_selected"), "RESEARCH_ONLY").upper(),
        "score": round(_safe_float(candidate.get("fused_score", candidate.get("score", 0.0)), 0.0), 4),
        "confidence": _safe_str(candidate.get("confidence"), "LOW").upper(),
        "research_approved": _safe_bool(candidate.get("research_approved"), False),
        "execution_ready": _safe_bool(candidate.get("execution_ready"), False),
        "selected_for_execution": _safe_bool(candidate.get("selected_for_execution"), False),
        "final_reason": _safe_str(candidate.get("final_reason"), ""),
        "final_reason_code": _safe_str(candidate.get("final_reason_code"), ""),
        "blocked_at": _safe_str(candidate.get("blocked_at"), ""),
        "capital_required": round(_safe_float(candidate.get("capital_required", 0.0), 0.0), 4),
        "capital_available": round(_safe_float(candidate.get("capital_available", 0.0), 0.0), 4),
        "option_contract_score": round(_safe_float(candidate.get("option_contract_score", 0.0), 0.0), 4),
        "trading_mode": _safe_str(candidate.get("trading_mode"), ""),
        "mode": _safe_str(candidate.get("mode"), ""),
    }


__all__ = [
    "build_canonical_candidate",
    "summarize_canonical_candidate",
]
