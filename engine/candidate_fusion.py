from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

try:
    from engine.observatory_mode import build_mode_context, normalize_mode
except Exception:
    def normalize_mode(value: Any = None) -> str:
        raw = str(value or "paper").strip().lower()
        if raw in {"survey", "deep_space"}:
            return "survey"
        if raw in {"live", "observatory"}:
            return "live"
        return "paper"

    def build_mode_context(value: Any = None) -> Dict[str, Any]:
        mode = normalize_mode(value)
        if mode == "survey":
            return {
                "mode": "survey",
                "strict_execution_gate": False,
                "strict_reserve": False,
                "strict_pdt": False,
                "soft_block_reasons": [
                    "cash_reserve_too_low",
                    "governor_blocked:cash_reserve_too_low",
                    "reserve_blocked",
                    "insufficient_cash_after_reserve",
                    "pdt_restricted",
                    "governor_blocked:pdt_restricted",
                ],
                "hard_block_reasons": [],
            }
        if mode == "live":
            return {
                "mode": "live",
                "strict_execution_gate": True,
                "strict_reserve": True,
                "strict_pdt": True,
                "soft_block_reasons": [],
                "hard_block_reasons": [
                    "cash_reserve_too_low",
                    "governor_blocked:cash_reserve_too_low",
                    "reserve_blocked",
                    "insufficient_cash_after_reserve",
                    "pdt_restricted",
                    "governor_blocked:pdt_restricted",
                ],
            }
        return {
            "mode": "paper",
            "strict_execution_gate": True,
            "strict_reserve": True,
            "strict_pdt": True,
            "soft_block_reasons": [],
            "hard_block_reasons": [
                "cash_reserve_too_low",
                "governor_blocked:cash_reserve_too_low",
                "reserve_blocked",
                "insufficient_cash_after_reserve",
                "pdt_restricted",
                "governor_blocked:pdt_restricted",
            ],
        }


VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"

CONFIDENCE_ORDER = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if hasattr(value, "iloc"):
            try:
                return float(value.iloc[-1])
            except Exception:
                return float(value.iloc[0])
        if hasattr(value, "item"):
            try:
                return float(value.item())
            except Exception:
                pass
        if value in {"", None}:
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if hasattr(value, "iloc"):
            try:
                return int(value.iloc[-1])
            except Exception:
                return int(value.iloc[0])
        if hasattr(value, "item"):
            try:
                return int(value.item())
            except Exception:
                pass
        if value in {"", None}:
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        return bool(value)
    except Exception:
        return bool(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def _safe_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _dedupe_keep_order(values: List[Any]) -> List[Any]:
    out: List[Any] = []
    seen = set()
    for item in values:
        key = repr(item)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _confidence_rank(confidence: Any) -> int:
    return CONFIDENCE_ORDER.get(_safe_str(confidence, "LOW").upper(), 1)


def _vehicle_shape(vehicle: Any) -> Dict[str, int]:
    normalized = _safe_str(vehicle, VEHICLE_RESEARCH_ONLY).upper()
    if normalized == VEHICLE_OPTION:
        return {"shares": 0, "contracts": 1}
    if normalized == VEHICLE_STOCK:
        return {"shares": 1, "contracts": 0}
    return {"shares": 0, "contracts": 0}


def _apply_vehicle_shape(payload: Dict[str, Any], vehicle: Any) -> Dict[str, Any]:
    out = dict(payload or {})
    normalized = _safe_str(vehicle, VEHICLE_RESEARCH_ONLY).upper()
    shape = _vehicle_shape(normalized)
    out["vehicle_selected"] = normalized
    out["vehicle"] = normalized
    out["shares"] = shape["shares"]
    out["contracts"] = shape["contracts"]
    if normalized == VEHICLE_OPTION:
        out["size"] = shape["contracts"]
    elif normalized == VEHICLE_STOCK:
        out["size"] = shape["shares"]
    else:
        out["size"] = 0
    return out


def _estimate_stock_cost(row: Dict[str, Any], commission: float = 1.0) -> Dict[str, float]:
    price = _safe_float(
        row.get("price", row.get("current_price", row.get("entry", 0.0))),
        0.0,
    )
    shares = max(1, _safe_int(row.get("shares", row.get("size", 1)), 1))
    gross = round(price * shares, 2) if price > 0 else 0.0
    minimum = round(gross + _safe_float(commission, 1.0), 2) if gross > 0 else 0.0
    return {
        "price": round(price, 4),
        "shares": shares,
        "capital_required": gross,
        "minimum_trade_cost": minimum,
    }


def _estimate_option_cost(
    option_obj: Dict[str, Any],
    contracts: int = 1,
    commission: float = 1.0,
) -> Dict[str, float]:
    option_obj = _safe_dict(option_obj)
    mark = _safe_float(
        option_obj.get("mark", option_obj.get("ask", option_obj.get("last", option_obj.get("price", 0.0)))),
        0.0,
    )
    contracts = max(1, _safe_int(contracts, 1))
    gross = round(mark * 100.0 * contracts, 2) if mark > 0 else 0.0
    minimum = round(gross + _safe_float(commission, 1.0), 2) if gross > 0 else 0.0
    return {
        "mark": round(mark, 4),
        "contracts": contracts,
        "capital_required": gross,
        "minimum_trade_cost": minimum,
    }


def _normalize_v2_row(v2_row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    raw = _safe_dict(v2_row)
    notes = raw.get("notes", raw.get("signals", []))
    risk_flags = raw.get("risk_flags", raw.get("warnings", []))
    return {
        "regime_alignment": _safe_str(raw.get("regime_alignment", raw.get("alignment", "")), ""),
        "signal_strength": _safe_float(
            raw.get("signal_strength", raw.get("strength", raw.get("v2_score", raw.get("score", 0.0)))),
            0.0,
        ),
        "conviction_adjustment": _safe_float(
            raw.get("conviction_adjustment", raw.get("confidence_adjustment", 0.0)),
            0.0,
        ),
        "vehicle_bias": _safe_str(
            raw.get("vehicle_bias", raw.get("bias", raw.get("preferred_vehicle", ""))),
            "",
        ).upper(),
        "thesis": _safe_str(raw.get("thesis", raw.get("summary", raw.get("reason", ""))), ""),
        "notes": notes if isinstance(notes, list) else [],
        "risk_flags": risk_flags if isinstance(risk_flags, list) else [],
        "raw": raw,
    }


def apply_v2_overlay(candidate: Dict[str, Any], v2_row: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    out = dict(candidate or {})
    v2 = _normalize_v2_row(v2_row)

    base_score = _safe_float(out.get("score", 0.0), 0.0)
    base_confidence = _safe_str(out.get("confidence", "LOW"), "LOW").upper()

    v2_strength = _safe_float(v2.get("signal_strength", 0.0), 0.0)
    v2_adjustment = _safe_float(v2.get("conviction_adjustment", 0.0), 0.0)
    v2_bias = _safe_str(v2.get("vehicle_bias", ""), "").upper()
    v2_thesis = _safe_str(v2.get("thesis", ""), "")

    fused_score = round(base_score + v2_adjustment, 2)
    fused_confidence = base_confidence

    if v2_adjustment >= 15 and base_confidence == "MEDIUM":
        fused_confidence = "HIGH"
    elif v2_adjustment >= 10 and base_confidence == "LOW":
        fused_confidence = "MEDIUM"
    elif v2_adjustment <= -15 and base_confidence == "HIGH":
        fused_confidence = "MEDIUM"
    elif v2_adjustment <= -10 and base_confidence == "MEDIUM":
        fused_confidence = "LOW"

    why = _safe_list(out.get("why", []))
    if v2_thesis:
        why.append(f"V2: {v2_thesis}")

    out["base_score"] = round(base_score, 2)
    out["fused_score"] = fused_score
    out["base_confidence"] = base_confidence
    out["confidence"] = fused_confidence
    out["v2"] = v2
    out["v2_score"] = round(v2_strength, 2)
    out["v2_signal_strength"] = round(v2_strength, 2)
    out["v2_conviction_adjustment"] = round(v2_adjustment, 2)
    out["v2_vehicle_bias"] = v2_bias
    out["v2_thesis"] = v2_thesis
    out["v2_notes"] = _safe_list(v2.get("notes", []))
    out["v2_risk_flags"] = _safe_list(v2.get("risk_flags", []))
    out["why"] = _dedupe_keep_order(why)

    if v2_bias in {"OPTION", "OPTIONS"}:
        out["prefer_options"] = True
    elif v2_bias in {"STOCK", "UNDERLYING"}:
        out["prefer_options"] = False
    else:
        out.setdefault("prefer_options", True)

    return out


def _is_governor_reason_soft_for_mode(reason: str, mode_context: Dict[str, Any]) -> bool:
    soft = {_safe_str(x) for x in _safe_list(mode_context.get("soft_block_reasons", []))}
    return _safe_str(reason) in soft


def _is_governor_reason_hard_for_mode(reason: str, mode_context: Dict[str, Any]) -> bool:
    hard = {_safe_str(x) for x in _safe_list(mode_context.get("hard_block_reasons", []))}
    return _safe_str(reason) in hard


def _derive_governor_reason(governor: Dict[str, Any]) -> str:
    reasons = _safe_list(governor.get("reasons"))
    if reasons:
        first = _safe_str(reasons[0], "")
        if first:
            return f"governor_blocked:{first}"
    status_label = _safe_str(governor.get("status_label", ""), "")
    return status_label.lower() if status_label else "governor_blocked"


def _build_option_diagnostics(
    best_option: Optional[Dict[str, Any]],
    option_score: float,
    option_notes: Optional[List[str]],
    buying_power: float,
    commission: float,
) -> Dict[str, Any]:
    option = _safe_dict(best_option)
    score_value = _safe_float(option_score, -1.0)
    has_option = bool(option)

    if not has_option:
        return {
            "vehicle": VEHICLE_OPTION,
            "has_option": False,
            "affordable": False,
            "is_executable": False,
            "capital_required": 0.0,
            "minimum_trade_cost": 0.0,
            "contracts": 0,
            "score": -1.0,
            "dte": -1,
            "spread_pct": 999.0,
            "execution_reason": "no_option_contract",
            "notes": _safe_list(option_notes),
            "contract": None,
        }

    cost = _estimate_option_cost(option, contracts=1, commission=commission)
    dte = _safe_int(option.get("dte", -1), -1)
    spread_pct = _safe_float(option.get("spread_pct", 999.0), 999.0)
    exec_reason = _safe_str(option.get("execution_reason", ""), "")
    is_flagged_exec = _safe_bool(option.get("is_executable", False), False)
    affordable = cost["minimum_trade_cost"] > 0 and cost["minimum_trade_cost"] <= _safe_float(buying_power, 0.0)

    return {
        "vehicle": VEHICLE_OPTION,
        "has_option": True,
        "affordable": affordable,
        "is_executable": is_flagged_exec,
        "capital_required": cost["capital_required"],
        "minimum_trade_cost": cost["minimum_trade_cost"],
        "contracts": cost["contracts"],
        "score": round(score_value, 2),
        "dte": dte,
        "spread_pct": round(spread_pct, 4) if spread_pct < 999 else spread_pct,
        "execution_reason": exec_reason or ("ok" if is_flagged_exec else "not_executable"),
        "notes": _safe_list(option_notes) or _safe_list(option.get("contract_notes", [])),
        "contract": option,
        "mark": cost["mark"],
    }


def _build_stock_diagnostics(
    row: Dict[str, Any],
    buying_power: float,
    commission: float,
) -> Dict[str, Any]:
    cost = _estimate_stock_cost(row, commission=commission)
    affordable = cost["minimum_trade_cost"] > 0 and cost["minimum_trade_cost"] <= _safe_float(buying_power, 0.0)
    return {
        "vehicle": VEHICLE_STOCK,
        "has_stock": cost["capital_required"] > 0,
        "affordable": affordable,
        "capital_required": cost["capital_required"],
        "minimum_trade_cost": cost["minimum_trade_cost"],
        "shares": cost["shares"],
        "price": cost["price"],
    }


def choose_best_vehicle(
    base_trade: Dict[str, Any],
    best_option: Optional[Dict[str, Any]],
    option_score: float,
    buying_power: float,
    prefer_options: bool = True,
    commission: float = 1.0,
    allow_stock_fallback: bool = True,
    minimum_option_score: float = 60.0,
    max_option_spread_pct: float = 0.12,
    minimum_option_dte: int = 0,
) -> Dict[str, Any]:
    row = dict(base_trade or {})
    option_path = _build_option_diagnostics(
        best_option=best_option,
        option_score=option_score,
        option_notes=_safe_list(row.get("option_explanation", [])),
        buying_power=buying_power,
        commission=commission,
    )
    stock_path = _build_stock_diagnostics(
        row=row,
        buying_power=buying_power,
        commission=commission,
    )

    score = _safe_float(row.get("fused_score", row.get("score", 0.0)), 0.0)
    confidence = _safe_str(row.get("confidence", "LOW"), "LOW").upper()

    stock_score_ok = score >= 100
    stock_conf_ok = confidence in {"MEDIUM", "HIGH"}
    stock_executable = stock_path["affordable"] and stock_score_ok and stock_conf_ok

    option_quality_ok = option_path["has_option"] and option_path["score"] >= _safe_float(minimum_option_score, 60.0)
    option_spread_ok = option_path["spread_pct"] <= _safe_float(max_option_spread_pct, 0.12)
    option_dte_ok = option_path["dte"] >= _safe_int(minimum_option_dte, 0)
    option_exec_ok = _safe_bool(option_path.get("is_executable"), False)
    option_affordable = _safe_bool(option_path.get("affordable"), False)

    option_executable = (
        option_path["has_option"]
        and option_affordable
        and option_quality_ok
        and option_spread_ok
        and option_dte_ok
        and option_exec_ok
    )

    vehicle = VEHICLE_RESEARCH_ONLY
    vehicle_reason = "no_executable_vehicle"
    capital_required = 0.0
    minimum_trade_cost = 0.0

    if prefer_options and option_executable:
        vehicle = VEHICLE_OPTION
        vehicle_reason = "preferred_option_contract"
        capital_required = option_path["capital_required"]
        minimum_trade_cost = option_path["minimum_trade_cost"]
    elif stock_executable:
        vehicle = VEHICLE_STOCK
        if option_path["has_option"] and option_executable is False:
            if not option_affordable and option_path["minimum_trade_cost"] > 0:
                vehicle_reason = "option_too_expensive_stock_fallback"
            elif not option_quality_ok and option_path["score"] >= 0:
                vehicle_reason = "weak_option_contract_stock_fallback"
            elif not option_spread_ok:
                vehicle_reason = "wide_option_spread_stock_fallback"
            elif not option_dte_ok:
                vehicle_reason = "short_dte_option_stock_fallback"
            elif not option_exec_ok:
                vehicle_reason = option_path["execution_reason"] or "option_not_executable_stock_fallback"
            else:
                vehicle_reason = "stock_selected"
        else:
            vehicle_reason = "stock_selected"
        capital_required = stock_path["capital_required"]
        minimum_trade_cost = stock_path["minimum_trade_cost"]
    elif option_executable:
        vehicle = VEHICLE_OPTION
        vehicle_reason = "option_only_executable"
        capital_required = option_path["capital_required"]
        minimum_trade_cost = option_path["minimum_trade_cost"]
    elif option_path["has_option"] and option_path["minimum_trade_cost"] > 0 and not option_affordable:
        vehicle = VEHICLE_RESEARCH_ONLY
        vehicle_reason = "option_not_affordable"
        capital_required = option_path["capital_required"]
        minimum_trade_cost = option_path["minimum_trade_cost"]
    elif stock_path["minimum_trade_cost"] > 0 and not stock_path["affordable"]:
        vehicle = VEHICLE_RESEARCH_ONLY
        vehicle_reason = "stock_not_affordable"
        capital_required = stock_path["capital_required"]
        minimum_trade_cost = stock_path["minimum_trade_cost"]
    elif option_path["has_option"]:
        vehicle = VEHICLE_RESEARCH_ONLY
        vehicle_reason = option_path["execution_reason"] or "option_not_executable"
        capital_required = option_path["capital_required"]
        minimum_trade_cost = option_path["minimum_trade_cost"]
    elif stock_path["has_stock"]:
        vehicle = VEHICLE_RESEARCH_ONLY
        vehicle_reason = "stock_not_executable"
        capital_required = stock_path["capital_required"]
        minimum_trade_cost = stock_path["minimum_trade_cost"]

    if vehicle == VEHICLE_OPTION and not allow_stock_fallback and not option_executable:
        vehicle = VEHICLE_RESEARCH_ONLY
        vehicle_reason = "stock_fallback_disabled"
        capital_required = 0.0
        minimum_trade_cost = 0.0

    result = {
        "vehicle_selected": vehicle,
        "vehicle_reason": vehicle_reason,
        "capital_required": round(_safe_float(capital_required, 0.0), 2),
        "minimum_trade_cost": round(_safe_float(minimum_trade_cost, 0.0), 2),
        "stock_path": stock_path,
        "option_path": option_path,
        "stock_affordable": _safe_bool(stock_path.get("affordable"), False),
        "option_affordable": option_affordable,
        "stock_score_ok": stock_score_ok,
        "stock_conf_ok": stock_conf_ok,
        "stock_executable": stock_executable,
        "option_quality_ok": option_quality_ok,
        "option_spread_ok": option_spread_ok,
        "option_dte_ok": option_dte_ok,
        "option_exec_ok": option_exec_ok,
        "option_executable": option_executable,
        "prefer_options": bool(prefer_options),
        "allow_stock_fallback": bool(allow_stock_fallback),
        "minimum_option_score": _safe_float(minimum_option_score, 60.0),
        "max_option_spread_pct": _safe_float(max_option_spread_pct, 0.12),
        "minimum_option_dte": _safe_int(minimum_option_dte, 0),
    }
    return _apply_vehicle_shape(result, vehicle)


def _collapse_to_research_only(
    candidate: Dict[str, Any],
    *,
    reason: str,
    blocked_at: str,
    preserve_capital_diagnostics: bool = True,
) -> Dict[str, Any]:
    out = dict(candidate or {})
    old_capital_required = _safe_float(out.get("capital_required", 0.0), 0.0)
    old_minimum_trade_cost = _safe_float(out.get("minimum_trade_cost", 0.0), 0.0)

    out = _apply_vehicle_shape(out, VEHICLE_RESEARCH_ONLY)
    out["research_approved"] = False
    out["execution_ready"] = False
    out["selected_for_execution"] = False
    out["blocked_at"] = blocked_at
    out["final_reason"] = reason
    out["vehicle_reason"] = reason

    if preserve_capital_diagnostics:
        out["capital_required"] = old_capital_required
        out["minimum_trade_cost"] = old_minimum_trade_cost
    else:
        out["capital_required"] = 0.0
        out["minimum_trade_cost"] = 0.0

    return out


def finalize_candidate_state(candidate: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(candidate or {})

    vehicle = _safe_str(out.get("vehicle_selected", VEHICLE_RESEARCH_ONLY), VEHICLE_RESEARCH_ONLY).upper()
    blocked_at = _safe_str(out.get("blocked_at", ""), "")
    final_reason = _safe_str(out.get("final_reason", ""), "")
    research_approved = _safe_bool(out.get("research_approved", False), False)
    execution_ready = _safe_bool(out.get("execution_ready", False), False)
    selected_for_execution = _safe_bool(out.get("selected_for_execution", False), False)

    if blocked_at in {"strategy_router", "score_threshold", "duplicate_guard", "reentry_guard", "breadth_guard", "volatility_guard"}:
        return _collapse_to_research_only(
            out,
            reason=final_reason or f"{blocked_at}_blocked",
            blocked_at=blocked_at,
            preserve_capital_diagnostics=True,
        )

    if vehicle == VEHICLE_RESEARCH_ONLY:
        out = _apply_vehicle_shape(out, VEHICLE_RESEARCH_ONLY)
        out["execution_ready"] = False
        out["selected_for_execution"] = False
        if not blocked_at:
            out["blocked_at"] = "vehicle_selection"
        if not final_reason:
            out["final_reason"] = out.get("vehicle_reason") or "research_only"
        out["research_approved"] = bool(research_approved)
        return out

    if blocked_at == "governor":
        out = _apply_vehicle_shape(out, vehicle)
        out["research_approved"] = bool(research_approved)
        out["execution_ready"] = False
        out["selected_for_execution"] = False
        if not out.get("final_reason"):
            out["final_reason"] = out.get("governor_reason") or "governor_blocked"
        return out

    if blocked_at == "execution_guard":
        out = _apply_vehicle_shape(out, vehicle)
        out["research_approved"] = bool(research_approved)
        out["execution_ready"] = False
        out["selected_for_execution"] = False
        if not out.get("final_reason"):
            out["final_reason"] = "execution_guard_blocked"
        return out

    out = _apply_vehicle_shape(out, vehicle)
    out["research_approved"] = bool(research_approved)
    out["execution_ready"] = bool(execution_ready)
    out["selected_for_execution"] = bool(selected_for_execution)
    return out


def build_fused_candidate(
    trade: Dict[str, Any],
    *,
    best_option: Optional[Dict[str, Any]] = None,
    option_score: float = -1.0,
    option_notes: Optional[List[str]] = None,
    v2_row: Optional[Dict[str, Any]] = None,
    governor: Optional[Dict[str, Any]] = None,
    buying_power: float = 0.0,
    commission: float = 1.0,
) -> Dict[str, Any]:
    row = deepcopy(_safe_dict(trade))
    governor = _safe_dict(governor)

    row["symbol"] = _norm_symbol(row.get("symbol", "UNKNOWN"))
    row["strategy"] = _safe_str(row.get("strategy", "CALL"), "CALL").upper()
    row["score"] = round(_safe_float(row.get("score", 0.0), 0.0), 2)
    row["confidence"] = _safe_str(row.get("confidence", "LOW"), "LOW").upper()
    row["option_chain"] = _safe_list(row.get("option_chain", []))
    row["option_explanation"] = _safe_list(option_notes) or _safe_list(row.get("option_explanation", []))

    requested_trading_mode = normalize_mode(
        row.get("trading_mode")
        or row.get("mode")
        or governor.get("trading_mode")
        or "paper"
    )
    mode_context = build_mode_context(requested_trading_mode)

    row["trading_mode"] = requested_trading_mode
    row["mode"] = requested_trading_mode
    row["mode_context"] = mode_context

    row = apply_v2_overlay(row, v2_row=v2_row)

    allow_stock_fallback = _safe_bool(mode_context.get("allow_stock_fallback", True), True)
    prefer_options = _safe_bool(row.get("prefer_options", True), True)
    minimum_option_dte = _safe_int(mode_context.get("minimum_option_dte", 0), 0)

    vehicle_decision = choose_best_vehicle(
        base_trade=row,
        best_option=best_option,
        option_score=option_score,
        buying_power=buying_power,
        prefer_options=prefer_options,
        commission=commission,
        allow_stock_fallback=allow_stock_fallback,
        minimum_option_score=60.0,
        max_option_spread_pct=0.12,
        minimum_option_dte=minimum_option_dte,
    )
    row.update(vehicle_decision)

    if isinstance(best_option, dict) and best_option:
        row["option"] = best_option
        row["option_contract_score"] = round(_safe_float(option_score, -1.0), 2)
    else:
        row["option"] = None
        row["option_contract_score"] = -1.0

    governor_blocked = _safe_bool(governor.get("blocked", False), False)
    governor_reasons = _safe_list(governor.get("reasons", []))
    governor_warnings = _safe_list(governor.get("warnings", []))
    governor_reason = _derive_governor_reason(governor) if governor_blocked else ""

    row["governor"] = governor
    row["governor_blocked"] = governor_blocked
    row["governor_status"] = _safe_str(governor.get("status_label", ""), "")
    row["governor_reasons"] = governor_reasons
    row["governor_warnings"] = governor_warnings
    row["governor_reason"] = governor_reason

    vehicle_selected = _safe_str(row.get("vehicle_selected", VEHICLE_RESEARCH_ONLY), VEHICLE_RESEARCH_ONLY).upper()
    research_approved = vehicle_selected != VEHICLE_RESEARCH_ONLY
    execution_ready = False
    selected_for_execution = False
    blocked_at = ""
    final_reason = ""

    if not research_approved:
        blocked_at = "vehicle_selection"
        final_reason = _safe_str(row.get("vehicle_reason", "research_only"), "research_only")

    if research_approved and governor_blocked:
        strict_execution_gate = _safe_bool(mode_context.get("strict_execution_gate", True), True)
        strict_reserve = _safe_bool(mode_context.get("strict_reserve", True), True)
        strict_pdt = _safe_bool(mode_context.get("strict_pdt", True), True)

        hard_hit = any(_is_governor_reason_hard_for_mode(_safe_str(r), mode_context) for r in governor_reasons)
        soft_hit = any(_is_governor_reason_soft_for_mode(_safe_str(r), mode_context) for r in governor_reasons)

        allow_execution_despite_governor = False
        if not strict_execution_gate and soft_hit and not hard_hit:
            allow_execution_despite_governor = True

        if strict_reserve or strict_pdt:
            allow_execution_despite_governor = False

        if allow_execution_despite_governor:
            blocked_at = ""
            final_reason = _safe_str(row.get("vehicle_reason", "execution_ready"), "execution_ready")
            execution_ready = True
            selected_for_execution = True
        else:
            blocked_at = "governor"
            final_reason = governor_reason or "governor_blocked"
            execution_ready = False
            selected_for_execution = False

    if research_approved and not governor_blocked:
        blocked_at = ""
        final_reason = _safe_str(row.get("vehicle_reason", "execution_ready"), "execution_ready")
        execution_ready = True
        selected_for_execution = True

    row["research_approved"] = research_approved
    row["execution_ready"] = execution_ready
    row["selected_for_execution"] = selected_for_execution
    row["blocked_at"] = blocked_at
    row["final_reason"] = final_reason

    row["capital_affordable"] = bool(
        row.get("minimum_trade_cost", 0.0) > 0
        and _safe_float(row.get("minimum_trade_cost", 0.0), 0.0) <= _safe_float(buying_power, 0.0)
    )
    row["capital_available"] = round(_safe_float(buying_power, 0.0), 2)

    row["fusion_diagnostics"] = {
        "mode": requested_trading_mode,
        "strict_execution_gate": _safe_bool(mode_context.get("strict_execution_gate", True), True),
        "strict_reserve": _safe_bool(mode_context.get("strict_reserve", True), True),
        "strict_pdt": _safe_bool(mode_context.get("strict_pdt", True), True),
        "prefer_options": prefer_options,
        "allow_stock_fallback": allow_stock_fallback,
        "vehicle_selected": row.get("vehicle_selected"),
        "vehicle_reason": row.get("vehicle_reason"),
        "research_approved": row.get("research_approved"),
        "execution_ready": row.get("execution_ready"),
        "selected_for_execution": row.get("selected_for_execution"),
        "blocked_at": row.get("blocked_at"),
        "final_reason": row.get("final_reason"),
        "governor_blocked": governor_blocked,
        "governor_reasons": governor_reasons,
        "governor_warnings": governor_warnings,
        "capital_required": row.get("capital_required"),
        "minimum_trade_cost": row.get("minimum_trade_cost"),
        "capital_available": row.get("capital_available"),
        "option_score": row.get("option_contract_score"),
        "fused_score": row.get("fused_score"),
        "confidence": row.get("confidence"),
    }

    return finalize_candidate_state(row)
