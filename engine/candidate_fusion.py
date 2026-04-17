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


def _confidence_rank(confidence: str) -> int:
    mapping = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    return mapping.get(_safe_str(confidence, "LOW").upper(), 1)


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
    mark = _safe_float(
        option_obj.get("mark", option_obj.get("ask", option_obj.get("last", option_obj.get("price", 0.0)))),
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
    out["shares"] = shape["shares"]
    out["contracts"] = shape["contracts"]
    return out


def _collapse_to_research_only(
    candidate: Dict[str, Any],
    reason: str,
    blocked_at: str,
) -> Dict[str, Any]:
    out = dict(candidate or {})
    out["vehicle_selected"] = "RESEARCH_ONLY"
    out["capital_required"] = 0.0
    out["minimum_trade_cost"] = 0.0
    out["research_approved"] = False
    out["execution_ready"] = False
    out["selected_for_execution"] = False
    out["blocked_at"] = blocked_at
    out["final_reason"] = reason
    out["vehicle_reason"] = reason
    out = _apply_vehicle_shape(out, "RESEARCH_ONLY")
    return out


def choose_best_vehicle(
    base_trade: Dict[str, Any],
    best_option: Optional[Dict[str, Any]],
    option_score: float,
    buying_power: float,
    prefer_options: bool = True,
    commission: float = 1.0,
) -> Dict[str, Any]:
    stock_cost = _estimate_stock_cost(base_trade)
    stock_minimum_cost = round(stock_cost + _safe_float(commission, 1.0), 2) if stock_cost > 0 else 0.0

    has_option = isinstance(best_option, dict) and bool(best_option)
    best_option = _safe_dict(best_option)

    option_cost = 0.0
    option_dte = -1
    option_spread_pct = 999.0
    option_exec_reason = ""
    option_flagged_executable = False
    trade_intent = "GRIND"

    if has_option:
        option_cost = _estimate_option_cost(best_option, contracts=1, commission=commission)
        option_dte = int(_safe_float(best_option.get("dte", -1), -1))
        option_spread_pct = _safe_float(best_option.get("spread_pct", 999.0), 999.0)
        option_exec_reason = _safe_str(best_option.get("execution_reason", ""), "")
        option_flagged_executable = bool(best_option.get("is_executable", False))
        trade_intent = _safe_str(best_option.get("trade_intent", "GRIND"), "GRIND").upper()

    stock_affordable = stock_minimum_cost > 0 and stock_minimum_cost <= _safe_float(buying_power, 0.0)
    option_affordable = option_cost > 0 and option_cost <= _safe_float(buying_power, 0.0)

    option_score_value = _safe_float(option_score, -1.0)
    option_quality_ok = has_option and option_score_value >= 60
    option_spread_ok = option_spread_pct <= 0.12

    if trade_intent == "GRIND":
        option_dte_ok = option_dte >= 2
    elif trade_intent in {"MOMENTUM", "EXPLOSIVE"}:
        option_dte_ok = option_dte >= 1
    else:
        option_dte_ok = option_dte >= 1

    option_executable = (
        has_option
        and option_affordable
        and (
            option_flagged_executable
            or (
                option_quality_ok
                and option_spread_ok
                and option_dte_ok
            )
        )
    )

    stock_score_ok = _safe_float(
        base_trade.get("fused_score", base_trade.get("score", 0.0)),
        0.0,
    ) >= 100
    stock_conf_ok = _safe_str(base_trade.get("confidence", "LOW"), "LOW").upper() in {"MEDIUM", "HIGH"}
    stock_executable = stock_affordable and stock_score_ok and stock_conf_ok

    vehicle = "RESEARCH_ONLY"
    capital_required = 0.0
    minimum_trade_cost = 0.0
    best_vehicle_reason = "no_executable_vehicle"

    if prefer_options and option_executable:
        vehicle = "OPTION"
        capital_required = round(option_cost - _safe_float(commission, 1.0), 2)
        minimum_trade_cost = option_cost
        best_vehicle_reason = "preferred_option_contract"

    elif stock_executable:
        if has_option and not option_affordable and option_cost > 0:
            vehicle = "STOCK"
            capital_required = stock_cost
            minimum_trade_cost = stock_minimum_cost
            best_vehicle_reason = "option_too_expensive_stock_fallback"
        elif has_option and option_exec_reason == "spread_too_wide":
            vehicle = "STOCK"
            capital_required = stock_cost
            minimum_trade_cost = stock_minimum_cost
            best_vehicle_reason = "wide_option_spread_stock_fallback"
        elif has_option and option_exec_reason in {
            "expiry_too_close_for_grind",
            "expiry_too_close_for_momentum",
            "expiry_too_close_for_explosive",
        }:
            vehicle = "STOCK"
            capital_required = stock_cost
            minimum_trade_cost = stock_minimum_cost
            best_vehicle_reason = "expired_or_same_day_option_stock_fallback"
        elif has_option and not option_flagged_executable and option_score_value > 0:
            vehicle = "STOCK"
            capital_required = stock_cost
            minimum_trade_cost = stock_minimum_cost
            best_vehicle_reason = "weak_option_contract_stock_fallback"
        else:
            vehicle = "STOCK"
            capital_required = stock_cost
            minimum_trade_cost = stock_minimum_cost
            best_vehicle_reason = "stock_only_executable"

    elif option_executable:
        vehicle = "OPTION"
        capital_required = round(option_cost - _safe_float(commission, 1.0), 2)
        minimum_trade_cost = option_cost
        best_vehicle_reason = "option_only_executable"

    elif has_option and option_cost > 0 and not option_affordable:
        vehicle = "RESEARCH_ONLY"
        capital_required = round(option_cost - _safe_float(commission, 1.0), 2)
        minimum_trade_cost = option_cost
        best_vehicle_reason = "option_not_affordable"

    elif stock_minimum_cost > 0 and not stock_affordable:
        vehicle = "RESEARCH_ONLY"
        capital_required = stock_cost
        minimum_trade_cost = stock_minimum_cost
        best_vehicle_reason = "stock_not_affordable"

    elif has_option and option_score_value > 0:
        vehicle = "RESEARCH_ONLY"
        capital_required = 0.0
        minimum_trade_cost = 0.0
        best_vehicle_reason = option_exec_reason or "option_not_executable"

    result = {
        "vehicle_selected": vehicle,
        "capital_required": round(capital_required, 2),
        "minimum_trade_cost": round(minimum_trade_cost, 2),
        "stock_minimum_cost": round(stock_minimum_cost, 2),
        "option_minimum_cost": round(option_cost, 2),
        "stock_affordable": stock_affordable,
        "option_affordable": option_affordable,
        "best_vehicle_reason": best_vehicle_reason,
        "prefer_options": prefer_options,
        "option_good": option_quality_ok,
        "option_dte_ok": option_dte_ok,
        "option_spread_ok": option_spread_ok,
        "option_score_value": round(option_score_value, 2),
        "option_dte": option_dte,
        "option_spread_pct": round(option_spread_pct, 4) if option_spread_pct < 999 else option_spread_pct,
        "option_execution_reason": option_exec_reason,
        "option_flagged_executable": option_flagged_executable,
        "trade_intent": trade_intent,
        "stock_score_ok": stock_score_ok,
        "stock_conf_ok": stock_conf_ok,
    }
    result = _apply_vehicle_shape(result, vehicle)
    return result


def apply_v2_overlay(
    candidate: Dict[str, Any],
    v2_row: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    out = dict(candidate or {})
    v2_row = v2_row if isinstance(v2_row, dict) else {}

    v2_score = _safe_float(v2_row.get("v2_score", v2_row.get("score", 0.0)), 0.0)
    v2_confidence = _safe_str(v2_row.get("v2_confidence", v2_row.get("confidence", "")), "").upper()
    v2_reason = _safe_str(v2_row.get("v2_reason", v2_row.get("reason", "")), "")
    v2_bias = _safe_str(v2_row.get("bias", v2_row.get("vehicle_bias", "")), "").upper()
    v2_quality = _safe_float(v2_row.get("execution_quality", v2_row.get("quality", 0.0)), 0.0)

    base_score = _safe_float(out.get("score", 0.0), 0.0)
    base_confidence = _safe_str(out.get("confidence", "LOW"), "LOW").upper()

    fused_score = round((base_score * 0.65) + (v2_score * 0.35), 2) if v2_score > 0 else base_score
    fused_confidence = base_confidence

    if v2_confidence:
        if _confidence_rank(v2_confidence) > _confidence_rank(base_confidence):
            fused_confidence = v2_confidence
        elif _confidence_rank(v2_confidence) < _confidence_rank(base_confidence) and v2_score > 0:
            fused_confidence = base_confidence

    out["base_score"] = base_score
    out["v2_score"] = v2_score
    out["fused_score"] = fused_score
    out["confidence"] = fused_confidence
    out["base_confidence"] = base_confidence
    out["v2_confidence"] = v2_confidence or base_confidence
    out["v2_reason"] = v2_reason
    out["v2_quality"] = v2_quality
    out["v2_vehicle_bias"] = v2_bias

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


def finalize_candidate_state(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call this AFTER the approval pipeline has populated:
      - research_approved
      - execution_ready
      - selected_for_execution
      - blocked_at
      - final_reason

    This normalizes the final visible state so the candidate tells one story.
    """
    out = dict(candidate or {})

    vehicle = _safe_str(out.get("vehicle_selected", "RESEARCH_ONLY"), "RESEARCH_ONLY").upper()
    blocked_at = _safe_str(out.get("blocked_at", ""), "")
    final_reason = _safe_str(out.get("final_reason", ""), "")
    research_approved = bool(out.get("research_approved", False))
    execution_ready = bool(out.get("execution_ready", False))
    selected_for_execution = bool(out.get("selected_for_execution", False))

    if blocked_at == "strategy_router" or final_reason == "strategy_router_returned_no_trade":
        return _collapse_to_research_only(
            out,
            reason=final_reason or "strategy_router_returned_no_trade",
            blocked_at="strategy_router",
        )

    if blocked_at in {
        "score_threshold",
        "reentry_guard",
        "duplicate_guard",
        "position_duplication_guard",
        "volatility_guard",
        "volatility_filter",
        "breadth_guard",
        "breadth_filter",
        "option_executable",
    }:
        return _collapse_to_research_only(
            out,
            reason=final_reason or f"{blocked_at}_blocked",
            blocked_at=blocked_at,
        )

    if vehicle == "RESEARCH_ONLY":
        out["research_approved"] = bool(research_approved)
        out["execution_ready"] = False
        out["selected_for_execution"] = False

        if not out.get("blocked_at"):
            out["blocked_at"] = "vehicle_selection"

        if not out.get("final_reason"):
            out["final_reason"] = "no_executable_vehicle_selected"

        out["vehicle_reason"] = (
            out.get("vehicle_reason")
            or out.get("best_vehicle_reason")
            or "research_only"
        )
        out = _apply_vehicle_shape(out, "RESEARCH_ONLY")
        return out

    if blocked_at == "governor":
        out["research_approved"] = bool(research_approved)
        out["execution_ready"] = False
        out["selected_for_execution"] = False
        out["vehicle_reason"] = (
            out.get("vehicle_reason")
            or out.get("best_vehicle_reason")
            or "execution_blocked_by_governor"
        )
        out = _apply_vehicle_shape(out, vehicle)
        return out

    if blocked_at == "execution_guard":
        out["research_approved"] = bool(research_approved)
        out["execution_ready"] = False
        out["selected_for_execution"] = False
        out["vehicle_reason"] = (
            out.get("vehicle_reason")
            or out.get("best_vehicle_reason")
            or "execution_blocked_by_execution_guard"
        )
        out = _apply_vehicle_shape(out, vehicle)
        return out

    if research_approved and not blocked_at:
        out["research_approved"] = True
        out["execution_ready"] = bool(execution_ready)
        out["selected_for_execution"] = bool(selected_for_execution)
        out["vehicle_reason"] = (
            out.get("vehicle_reason")
            or out.get("best_vehicle_reason")
            or "vehicle_selected"
        )
        out = _apply_vehicle_shape(out, vehicle)
        return out

    if not research_approved:
        return _collapse_to_research_only(
            out,
            reason=final_reason or "not_research_approved",
            blocked_at=blocked_at or "research_gate",
        )

    out["vehicle_reason"] = (
        out.get("vehicle_reason")
        or out.get("best_vehicle_reason")
        or "vehicle_selected"
    )
    out = _apply_vehicle_shape(out, vehicle)
    return out


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

    row["symbol"] = _norm_symbol(row.get("symbol", "UNKNOWN"))
    row["strategy"] = _safe_str(row.get("strategy", "CALL"), "CALL").upper()
    row["score"] = _safe_float(row.get("score", 0.0), 0.0)
    row["confidence"] = _safe_str(row.get("confidence", "LOW"), "LOW").upper()
    row["option_chain"] = _safe_list(row.get("option_chain", []))
    row["option_explanation"] = _safe_list(option_notes)

    row = apply_v2_overlay(row, v2_row=v2_row)

    price = round(_safe_float(row.get("price", row.get("current_price", row.get("entry", 0.0))), 0.0), 2)
    stock_capital_required = price
    stock_minimum_trade_cost = round(stock_capital_required + commission, 2)
    stock_affordable = stock_capital_required > 0 and buying_power >= stock_minimum_trade_cost

    row["stock_path"] = {
        "vehicle": "STOCK",
        "capital_required": stock_capital_required,
        "minimum_trade_cost": stock_minimum_trade_cost,
        "affordable": stock_affordable,
        "shares": 1,
        "contracts": 0,
    }

    if isinstance(best_option, dict) and best_option:
        option_mark = _safe_float(
            best_option.get("mark", best_option.get("last", best_option.get("ask", 0.0))),
            0.0,
        )
        option_capital_required = round(option_mark * 100, 2)
        option_minimum_trade_cost = round(option_capital_required + commission, 2)
        option_affordable = option_capital_required > 0 and buying_power >= option_minimum_trade_cost

        row["option"] = best_option
        row["option_contract_score"] = _safe_float(option_score, -1.0)
        row["option_path"] = {
            "vehicle": "OPTION",
            "capital_required": option_capital_required,
            "minimum_trade_cost": option_minimum_trade_cost,
            "affordable": option_affordable,
            "contracts": 1,
            "shares": 0,
            "score": _safe_float(option_score, -1.0),
            "dte": int(_safe_float(best_option.get("dte", -1), -1)),
            "spread_pct": _safe_float(best_option.get("spread_pct", 999.0), 999.0),
        }
    else:
        row["option"] = None
        row["option_contract_score"] = -1.0
        row["option_path"] = {
            "vehicle": "OPTION",
            "capital_required": 0.0,
            "minimum_trade_cost": 0.0,
            "affordable": False,
            "contracts": 0,
            "shares": 0,
            "score": -1.0,
            "dte": -1,
            "spread_pct": 999.0,
        }

    vehicle = choose_best_vehicle(
        row,
        best_option=best_option,
        option_score=option_score,
        buying_power=buying_power,
        prefer_options=bool(row.get("prefer_options", True)),
        commission=commission,
    )
    row.update(vehicle)

    selected_vehicle = _safe_str(row.get("vehicle_selected", "RESEARCH_ONLY"), "RESEARCH_ONLY").upper()

    if selected_vehicle == "OPTION":
        option_path = row.get("option_path", {})
        stock_path = row.get("stock_path", {})
        option_dte = int(_safe_float(option_path.get("dte", -1), -1))
        option_quality = _safe_float(option_path.get("score", -1.0), -1.0)
        if option_path.get("affordable") is False or option_dte <= 0 or option_quality < 90:
            if stock_path.get("affordable"):
                row["vehicle_selected"] = "STOCK"
                row["capital_required"] = stock_path.get("capital_required", 0.0)
                row["minimum_trade_cost"] = stock_path.get("minimum_trade_cost", 0.0)
                row["vehicle_reason"] = (
                    f"stock_fallback_from_option:"
                    f"{'unaffordable' if option_path.get('affordable') is False else 'weak_contract'}"
                )
                row = _apply_vehicle_shape(row, "STOCK")
            else:
                row["vehicle_selected"] = "RESEARCH_ONLY"
                row["capital_required"] = 0.0
                row["minimum_trade_cost"] = 0.0
                row["vehicle_reason"] = "option_selected_no_stock_fallback"
                row = _apply_vehicle_shape(row, "RESEARCH_ONLY")
        else:
            row["vehicle_reason"] = row.get("vehicle_reason") or "option_selected"
            row = _apply_vehicle_shape(row, "OPTION")
    elif selected_vehicle == "STOCK":
        if not row.get("vehicle_reason"):
            row["vehicle_reason"] = "stock_selected"
        row = _apply_vehicle_shape(row, "STOCK")
    else:
        row["vehicle_selected"] = "RESEARCH_ONLY"
        row["capital_required"] = 0.0
        row["minimum_trade_cost"] = 0.0
        if not row.get("vehicle_reason"):
            row["vehicle_reason"] = "research_only"
        row = _apply_vehicle_shape(row, "RESEARCH_ONLY")

    row["governor"] = governor
    row["governor_blocked"] = bool(governor.get("blocked", False))
    row["governor_status"] = _safe_str(governor.get("status_label", ""), "")
    row["governor_reasons"] = _safe_list(governor.get("reasons"))
    row["governor_warnings"] = _safe_list(governor.get("warnings"))

    row["research_approved"] = False
    row["execution_ready"] = False
    row["selected_for_execution"] = False
    return row
