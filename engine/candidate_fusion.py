from __future__ import annotations

from typing import Any, Dict, List, Optional


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
        return int(value)
    except Exception:
        return int(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _bool(value: Any, default: bool = False) -> bool:
    try:
        return bool(value)
    except Exception:
        return bool(default)


def _estimate_stock_cost(row: Dict[str, Any]) -> float:
    price = _safe_float(
        row.get("price", row.get("current_price", row.get("entry", 0.0))),
        0.0,
    )
    shares = max(1, _safe_int(row.get("size", row.get("shares", 1)), 1))
    return round(price * shares, 2)


def _estimate_option_cost(
    option_obj: Dict[str, Any],
    contracts: int = 1,
    commission: float = 1.0,
) -> float:
    option_obj = _safe_dict(option_obj)
    mark = _safe_float(
        option_obj.get(
            "mark",
            option_obj.get("ask", option_obj.get("last", option_obj.get("price", 0.0))),
        ),
        0.0,
    )
    contracts = max(1, _safe_int(contracts, 1))
    if mark <= 0:
        return 0.0
    return round((mark * 100 * contracts) + _safe_float(commission, 1.0), 2)


def _vehicle_shape(vehicle: str) -> Dict[str, int]:
    vehicle = _safe_str(vehicle, "RESEARCH_ONLY").upper()
    if vehicle == "OPTION":
        return {"shares": 0, "contracts": 1}
    if vehicle == "STOCK":
        return {"shares": 1, "contracts": 0}
    return {"shares": 0, "contracts": 0}


def _apply_vehicle_shape(candidate: Dict[str, Any], vehicle: str) -> Dict[str, Any]:
    out = dict(candidate or {})
    shape = _vehicle_shape(vehicle)
    out["vehicle_selected"] = _safe_str(vehicle, "RESEARCH_ONLY").upper()
    out["shares"] = shape["shares"]
    out["contracts"] = shape["contracts"]
    out["stock_position_size"] = shape["shares"] if out["vehicle_selected"] == "STOCK" else 0
    out["option_position_size"] = shape["contracts"] if out["vehicle_selected"] == "OPTION" else 0
    return out


def _set_vehicle_state(
    candidate: Dict[str, Any],
    vehicle: str,
    *,
    capital_required: Optional[float] = None,
    minimum_trade_cost: Optional[float] = None,
    vehicle_reason: Optional[str] = None,
) -> Dict[str, Any]:
    out = _apply_vehicle_shape(candidate, vehicle)
    vehicle = _safe_str(vehicle, "RESEARCH_ONLY").upper()

    out["capital_required"] = round(
        _safe_float(
            capital_required if capital_required is not None else out.get("capital_required", 0.0),
            0.0,
        ),
        2,
    )
    out["minimum_trade_cost"] = round(
        _safe_float(
            minimum_trade_cost if minimum_trade_cost is not None else out.get("minimum_trade_cost", 0.0),
            0.0,
        ),
        2,
    )
    out["vehicle_reason"] = _safe_str(
        vehicle_reason if vehicle_reason is not None else out.get("vehicle_reason", out.get("best_vehicle_reason", "")),
        "",
    )

    if vehicle == "RESEARCH_ONLY":
        out["capital_required"] = 0.0
        out["minimum_trade_cost"] = 0.0

    return out


def _collapse_to_research_only(
    candidate: Dict[str, Any],
    reason: str,
    blocked_at: str,
    reason_code: Optional[str] = None,
) -> Dict[str, Any]:
    out = dict(candidate or {})
    out = _set_vehicle_state(
        out,
        "RESEARCH_ONLY",
        capital_required=0.0,
        minimum_trade_cost=0.0,
        vehicle_reason=reason,
    )
    out["research_approved"] = False
    out["execution_ready"] = False
    out["selected_for_execution"] = False
    out["blocked_at"] = _safe_str(blocked_at, "research_gate")
    out["final_reason"] = _safe_str(reason, "not_research_approved")
    out["final_reason_code"] = _safe_str(reason_code or reason, "not_research_approved")
    out["decision_reason"] = out["final_reason"]
    out["decision_reason_code"] = out["final_reason_code"]
    return out


def _normalize_v2_row(v2_row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    v2_row = _safe_dict(v2_row)
    notes = v2_row.get("notes", v2_row.get("signals", []))
    risk_flags = v2_row.get("risk_flags", v2_row.get("warnings", []))
    return {
        "score": _safe_float(v2_row.get("score", v2_row.get("v2_score", 0.0)), 0.0),
        "quality": _safe_str(v2_row.get("quality", ""), ""),
        "reason": _safe_str(v2_row.get("reason", ""), ""),
        "regime_alignment": _safe_str(
            v2_row.get("regime_alignment", v2_row.get("alignment", "")),
            "",
        ),
        "signal_strength": _safe_float(
            v2_row.get(
                "signal_strength",
                v2_row.get("strength", v2_row.get("v2_score", v2_row.get("score", 0.0))),
            ),
            0.0,
        ),
        "conviction_adjustment": _safe_float(
            v2_row.get("conviction_adjustment", v2_row.get("confidence_adjustment", 0.0)),
            0.0,
        ),
        "vehicle_bias": _safe_str(
            v2_row.get("vehicle_bias", v2_row.get("bias", v2_row.get("preferred_vehicle", ""))),
            "",
        ).upper(),
        "thesis": _safe_str(
            v2_row.get("thesis", v2_row.get("summary", v2_row.get("reason", ""))),
            "",
        ),
        "notes": notes if isinstance(notes, list) else [],
        "risk_flags": risk_flags if isinstance(risk_flags, list) else [],
        "raw": dict(v2_row),
    }


def apply_v2_overlay(
    candidate: Dict[str, Any],
    v2_row: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    out = dict(candidate or {})
    normalized_v2 = _normalize_v2_row(v2_row)

    base_score = _safe_float(out.get("score", 0.0), 0.0)
    base_confidence = _safe_str(out.get("confidence", "LOW"), "LOW").upper()
    v2_conviction_adjustment = _safe_float(normalized_v2.get("conviction_adjustment", 0.0), 0.0)
    v2_bias = _safe_str(normalized_v2.get("vehicle_bias", ""), "").upper()
    v2_reason = _safe_str(normalized_v2.get("thesis", ""), "")

    fused_score = round(base_score + v2_conviction_adjustment, 2)
    fused_confidence = base_confidence

    if v2_conviction_adjustment >= 15 and base_confidence == "MEDIUM":
        fused_confidence = "HIGH"
    elif v2_conviction_adjustment >= 10 and base_confidence == "LOW":
        fused_confidence = "MEDIUM"
    elif v2_conviction_adjustment <= -15 and base_confidence == "HIGH":
        fused_confidence = "MEDIUM"
    elif v2_conviction_adjustment <= -10 and base_confidence == "MEDIUM":
        fused_confidence = "LOW"

    out["base_score"] = base_score
    out["fused_score"] = fused_score
    out["confidence"] = fused_confidence
    out["base_confidence"] = base_confidence

    out["v2"] = normalized_v2
    out["v2_score"] = _safe_float(normalized_v2.get("score", 0.0), 0.0)
    out["v2_quality"] = _safe_str(normalized_v2.get("quality", ""), "")
    out["v2_reason"] = _safe_str(normalized_v2.get("reason", ""), "")
    out["v2_regime_alignment"] = _safe_str(normalized_v2.get("regime_alignment", ""), "")
    out["v2_signal_strength"] = _safe_float(normalized_v2.get("signal_strength", 0.0), 0.0)
    out["v2_conviction_adjustment"] = _safe_float(normalized_v2.get("conviction_adjustment", 0.0), 0.0)
    out["v2_vehicle_bias"] = _safe_str(normalized_v2.get("vehicle_bias", ""), "").upper()
    out["v2_thesis"] = _safe_str(normalized_v2.get("thesis", ""), "")
    out["v2_notes"] = _safe_list(normalized_v2.get("notes", []))
    out["v2_risk_flags"] = _safe_list(normalized_v2.get("risk_flags", []))

    if v2_bias in {"OPTION", "OPTIONS"}:
        out["prefer_options"] = True
    elif v2_bias in {"STOCK", "UNDERLYING"}:
        out["prefer_options"] = False
    else:
        out.setdefault("prefer_options", True)

    why = _safe_list(out.get("why", []))
    if v2_reason:
        why.append(f"V2: {v2_reason}")
    out["why"] = why

    return out


def _score_stock_path(
    trade: Dict[str, Any],
    buying_power: float,
    commission: float,
) -> Dict[str, Any]:
    price = round(
        _safe_float(trade.get("price", trade.get("current_price", trade.get("entry", 0.0))), 0.0),
        2,
    )
    shares = max(1, _safe_int(trade.get("size", trade.get("shares", 1)), 1))
    capital_required = round(price * shares, 2)
    minimum_trade_cost = round(capital_required + commission, 2)

    score = _safe_float(trade.get("fused_score", trade.get("score", 0.0)), 0.0)
    confidence = _safe_str(trade.get("confidence", "LOW"), "LOW").upper()

    affordable = capital_required > 0 and minimum_trade_cost <= buying_power
    score_ok = score >= 100
    confidence_ok = confidence in {"MEDIUM", "HIGH"}

    executable = affordable and score_ok and confidence_ok

    if not affordable:
        reason = "stock_not_affordable"
    elif not score_ok:
        reason = "stock_score_too_low"
    elif not confidence_ok:
        reason = "stock_confidence_too_low"
    else:
        reason = "stock_executable"

    return {
        "vehicle": "STOCK",
        "capital_required": capital_required,
        "minimum_trade_cost": minimum_trade_cost,
        "affordable": affordable,
        "score_ok": score_ok,
        "confidence_ok": confidence_ok,
        "executable": executable,
        "shares": shares,
        "contracts": 0,
        "reason": reason,
    }


def _score_option_path(
    best_option: Optional[Dict[str, Any]],
    option_score: float,
    buying_power: float,
    commission: float,
) -> Dict[str, Any]:
    option_obj = _safe_dict(best_option)
    has_option = bool(option_obj)

    if not has_option:
        return {
            "vehicle": "OPTION",
            "capital_required": 0.0,
            "minimum_trade_cost": 0.0,
            "affordable": False,
            "score_ok": False,
            "spread_ok": False,
            "dte_ok": False,
            "flagged_executable": False,
            "executable": False,
            "shares": 0,
            "contracts": 0,
            "score": -1.0,
            "dte": -1,
            "spread_pct": 999.0,
            "execution_reason": "no_option_contract",
            "reason": "no_option_contract",
        }

    option_minimum_trade_cost = _estimate_option_cost(option_obj, contracts=1, commission=commission)
    option_capital_required = round(max(0.0, option_minimum_trade_cost - commission), 2)

    option_score_value = _safe_float(option_score, -1.0)
    option_dte = _safe_int(option_obj.get("dte", -1), -1)
    option_spread_pct = _safe_float(option_obj.get("spread_pct", 999.0), 999.0)
    option_exec_reason = _safe_str(option_obj.get("execution_reason", ""), "")
    option_flagged_executable = _bool(option_obj.get("is_executable", False), False)

    affordable = option_capital_required > 0 and option_minimum_trade_cost <= buying_power
    score_ok = option_score_value >= 60
    spread_ok = option_spread_pct <= 0.12
    dte_ok = option_dte >= 0

    executable = has_option and affordable and (
        option_flagged_executable or (score_ok and spread_ok and dte_ok)
    )

    if not affordable and option_capital_required > 0:
        reason = "option_not_affordable"
    elif not score_ok:
        reason = option_exec_reason or "option_score_too_low"
    elif not spread_ok:
        reason = option_exec_reason or "spread_too_wide"
    elif not dte_ok:
        reason = option_exec_reason or "invalid_option_dte"
    elif not executable:
        reason = option_exec_reason or "option_not_executable"
    else:
        reason = "option_executable"

    return {
        "vehicle": "OPTION",
        "capital_required": round(option_capital_required, 2),
        "minimum_trade_cost": round(option_minimum_trade_cost, 2),
        "affordable": affordable,
        "score_ok": score_ok,
        "spread_ok": spread_ok,
        "dte_ok": dte_ok,
        "flagged_executable": option_flagged_executable,
        "executable": executable,
        "shares": 0,
        "contracts": 1 if executable else 0,
        "score": round(option_score_value, 2),
        "dte": option_dte,
        "spread_pct": round(option_spread_pct, 4) if option_spread_pct < 999 else option_spread_pct,
        "execution_reason": option_exec_reason,
        "reason": reason,
    }


def choose_best_vehicle(
    base_trade: Dict[str, Any],
    best_option: Optional[Dict[str, Any]],
    option_score: float,
    buying_power: float,
    prefer_options: bool = True,
    commission: float = 1.0,
) -> Dict[str, Any]:
    trade = dict(base_trade or {})
    buying_power = _safe_float(buying_power, 0.0)
    commission = _safe_float(commission, 1.0)

    stock_path = _score_stock_path(trade, buying_power, commission)
    option_path = _score_option_path(best_option, option_score, buying_power, commission)

    has_option_contract = bool(_safe_dict(best_option))
    prefer_options = bool(prefer_options)

    vehicle = "RESEARCH_ONLY"
    reason = "no_executable_vehicle"
    capital_required = 0.0
    minimum_trade_cost = 0.0

    if prefer_options and option_path["executable"]:
        vehicle = "OPTION"
        reason = "preferred_option_contract"
        capital_required = option_path["capital_required"]
        minimum_trade_cost = option_path["minimum_trade_cost"]
    elif stock_path["executable"]:
        vehicle = "STOCK"
        capital_required = stock_path["capital_required"]
        minimum_trade_cost = stock_path["minimum_trade_cost"]
        if has_option_contract:
            if not option_path["affordable"] and option_path["capital_required"] > 0:
                reason = "option_too_expensive_stock_fallback"
            elif not option_path["score_ok"]:
                reason = "weak_option_contract_stock_fallback"
            elif not option_path["spread_ok"]:
                reason = "wide_option_spread_stock_fallback"
            elif not option_path["dte_ok"]:
                reason = "invalid_option_dte_stock_fallback"
            elif not option_path["executable"]:
                reason = option_path["reason"] or "option_not_executable_stock_fallback"
            else:
                reason = "stock_selected"
        else:
            reason = "stock_only_executable"
    elif option_path["executable"]:
        vehicle = "OPTION"
        reason = "option_only_executable"
        capital_required = option_path["capital_required"]
        minimum_trade_cost = option_path["minimum_trade_cost"]
    else:
        vehicle = "RESEARCH_ONLY"
        capital_required = 0.0
        minimum_trade_cost = 0.0
        if has_option_contract:
            reason = option_path["reason"] or stock_path["reason"] or "no_executable_vehicle"
        else:
            reason = stock_path["reason"] or "no_executable_vehicle"

    result = {
        "vehicle_selected": vehicle,
        "capital_required": round(capital_required, 2),
        "minimum_trade_cost": round(minimum_trade_cost, 2),
        "best_vehicle_reason": reason,
        "vehicle_reason": reason,
        "prefer_options": prefer_options,
        "stock_path": stock_path,
        "option_path": option_path,
        "stock_affordable": _bool(stock_path.get("affordable", False), False),
        "option_affordable": _bool(option_path.get("affordable", False), False),
        "stock_score_ok": _bool(stock_path.get("score_ok", False), False),
        "stock_conf_ok": _bool(stock_path.get("confidence_ok", False), False),
        "option_good": _bool(option_path.get("score_ok", False), False),
        "option_dte_ok": _bool(option_path.get("dte_ok", False), False),
        "option_spread_ok": _bool(option_path.get("spread_ok", False), False),
        "option_score_value": _safe_float(option_path.get("score", -1.0), -1.0),
        "option_dte": _safe_int(option_path.get("dte", -1), -1),
        "option_spread_pct": _safe_float(option_path.get("spread_pct", 999.0), 999.0),
        "option_execution_reason": _safe_str(option_path.get("execution_reason", ""), ""),
        "option_flagged_executable": _bool(option_path.get("flagged_executable", False), False),
        "trade_intent": _safe_str(
            _safe_dict(best_option).get("trade_intent", "GRIND"),
            "GRIND",
        ).upper(),
    }

    return _set_vehicle_state(
        result,
        vehicle,
        capital_required=capital_required,
        minimum_trade_cost=minimum_trade_cost,
        vehicle_reason=reason,
    )


def finalize_candidate_state(candidate: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(candidate or {})
    vehicle = _safe_str(out.get("vehicle_selected", "RESEARCH_ONLY"), "RESEARCH_ONLY").upper()
    blocked_at = _safe_str(out.get("blocked_at", ""), "")
    final_reason = _safe_str(out.get("final_reason", ""), "")
    final_reason_code = _safe_str(out.get("final_reason_code", final_reason), final_reason)

    research_approved = _bool(out.get("research_approved", False), False)
    execution_ready = _bool(out.get("execution_ready", False), False)
    selected_for_execution = _bool(out.get("selected_for_execution", False), False)

    hard_research_fail_blocks = {
        "strategy_router",
        "score_threshold",
        "reentry_guard",
        "duplicate_guard",
        "position_duplication_guard",
        "volatility_guard",
        "volatility_filter",
        "breadth_guard",
        "breadth_filter",
        "option_executable",
    }

    if blocked_at == "strategy_router" or final_reason_code == "strategy_router_returned_no_trade":
        return _collapse_to_research_only(
            out,
            reason=final_reason or "strategy_router_returned_no_trade",
            blocked_at="strategy_router",
            reason_code="strategy_router_returned_no_trade",
        )

    if blocked_at in hard_research_fail_blocks:
        return _collapse_to_research_only(
            out,
            reason=final_reason or f"{blocked_at}_blocked",
            blocked_at=blocked_at,
            reason_code=final_reason_code or f"{blocked_at}_blocked",
        )

    if vehicle == "RESEARCH_ONLY":
        out["research_approved"] = research_approved
        out["execution_ready"] = False
        out["selected_for_execution"] = False
        out["blocked_at"] = blocked_at or "vehicle_selection"
        out["final_reason"] = final_reason or "no_executable_vehicle_selected"
        out["final_reason_code"] = final_reason_code or "no_executable_vehicle_selected"
        out["decision_reason"] = _safe_str(out.get("decision_reason", out["final_reason"]), out["final_reason"])
        out["decision_reason_code"] = _safe_str(
            out.get("decision_reason_code", out["final_reason_code"]),
            out["final_reason_code"],
        )
        return _set_vehicle_state(
            out,
            "RESEARCH_ONLY",
            capital_required=0.0,
            minimum_trade_cost=0.0,
            vehicle_reason=out.get("vehicle_reason") or out.get("best_vehicle_reason") or "research_only",
        )

    if blocked_at in {"governor", "execution_guard"}:
        out["research_approved"] = research_approved
        out["execution_ready"] = False
        out["selected_for_execution"] = False
        out["final_reason_code"] = final_reason_code or final_reason
        out["decision_reason"] = _safe_str(out.get("decision_reason", final_reason), final_reason)
        out["decision_reason_code"] = _safe_str(
            out.get("decision_reason_code", out["final_reason_code"]),
            out["final_reason_code"],
        )
        return _set_vehicle_state(
            out,
            vehicle,
            capital_required=out.get("capital_required", 0.0),
            minimum_trade_cost=out.get("minimum_trade_cost", 0.0),
            vehicle_reason=(
                out.get("vehicle_reason")
                or out.get("best_vehicle_reason")
                or ("execution_blocked_by_governor" if blocked_at == "governor" else "execution_blocked_by_execution_guard")
            ),
        )

    if not research_approved:
        return _collapse_to_research_only(
            out,
            reason=final_reason or "not_research_approved",
            blocked_at=blocked_at or "research_gate",
            reason_code=final_reason_code or "not_research_approved",
        )

    out["research_approved"] = True
    out["execution_ready"] = execution_ready
    out["selected_for_execution"] = selected_for_execution

    if execution_ready and not out.get("final_reason"):
        out["final_reason"] = "execution_ready"
    if execution_ready and not out.get("final_reason_code"):
        out["final_reason_code"] = "execution_ready"

    out["decision_reason"] = _safe_str(
        out.get("decision_reason", out.get("final_reason", "")),
        out.get("final_reason", ""),
    )
    out["decision_reason_code"] = _safe_str(
        out.get("decision_reason_code", out.get("final_reason_code", "")),
        out.get("final_reason_code", ""),
    )

    return _set_vehicle_state(
        out,
        vehicle,
        capital_required=out.get("capital_required", 0.0),
        minimum_trade_cost=out.get("minimum_trade_cost", 0.0),
        vehicle_reason=out.get("vehicle_reason") or out.get("best_vehicle_reason") or "vehicle_selected",
    )


def build_fused_candidate(
    trade: Dict[str, Any],
    *,
    best_option: Optional[Dict[str, Any]] = None,
    option_score: float = -1,
    option_notes: Optional[List[str]] = None,
    v2_row: Optional[Dict[str, Any]] = None,
    governor: Optional[Dict[str, Any]] = None,
    buying_power: float = 0.0,
    commission: float = 1.0,
) -> Dict[str, Any]:
    row = dict(trade or {})
    governor = _safe_dict(governor)
    buying_power = _safe_float(buying_power, 0.0)
    commission = _safe_float(commission, 1.0)

    row["symbol"] = _norm_symbol(row.get("symbol", "UNKNOWN"))
    row["strategy"] = _safe_str(row.get("strategy", "CALL"), "CALL").upper()
    row["score"] = _safe_float(row.get("score", 0.0), 0.0)
    row["confidence"] = _safe_str(row.get("confidence", "LOW"), "LOW").upper()
    row["option_chain"] = _safe_list(row.get("option_chain", []))
    row["option_explanation"] = _safe_list(option_notes)

    row = apply_v2_overlay(row, v2_row=v2_row)

    row["option"] = dict(best_option) if isinstance(best_option, dict) and best_option else None
    row["option_contract_score"] = _safe_float(option_score, -1.0)

    vehicle = choose_best_vehicle(
        row,
        best_option=best_option,
        option_score=option_score,
        buying_power=buying_power,
        prefer_options=_bool(row.get("prefer_options", True), True),
        commission=commission,
    )

    row.update(vehicle)

    row["governor"] = governor
    row["governor_blocked"] = _bool(governor.get("blocked", False), False)
    row["governor_status"] = _safe_str(governor.get("status_label", ""), "")
    row["governor_reason"] = _safe_str((_safe_list(governor.get("reasons")) or [""])[0], "")
    row["governor_reasons"] = _safe_list(governor.get("reasons"))
    row["governor_warnings"] = _safe_list(governor.get("warnings"))

    row["research_approved"] = False
    row["execution_ready"] = False
    row["selected_for_execution"] = False
    row["blocked_at"] = _safe_str(row.get("blocked_at", ""), "")
    row["final_reason"] = _safe_str(row.get("final_reason", ""), "")
    row["final_reason_code"] = _safe_str(row.get("final_reason_code", row.get("final_reason", "")), "")
    row["decision_reason"] = _safe_str(row.get("decision_reason", row.get("final_reason", "")), "")
    row["decision_reason_code"] = _safe_str(row.get("decision_reason_code", row.get("final_reason_code", "")), "")

    row = _set_vehicle_state(
        row,
        row.get("vehicle_selected", "RESEARCH_ONLY"),
        capital_required=row.get("capital_required", 0.0),
        minimum_trade_cost=row.get("minimum_trade_cost", 0.0),
        vehicle_reason=row.get("vehicle_reason", row.get("best_vehicle_reason", "")),
    )

    return row
