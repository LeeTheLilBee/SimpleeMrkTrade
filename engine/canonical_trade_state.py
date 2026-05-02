from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional


OPTION_CONTRACT_MULTIPLIER = 100


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


def _first_positive_float(*values: Any, default: float = 0.0) -> float:
    for value in values:
        num = _safe_float(value, 0.0)
        if num > 0:
            return num
    return float(default)


def _derive_trade_id(symbol: str, strategy: str, opened_at: str) -> str:
    stamp = _safe_str(opened_at, _now_iso()).replace(":", "").replace("-", "").replace(".", "")
    return f"{symbol}-{strategy}-{stamp}"


def _vehicle(vehicle: Any) -> str:
    value = _safe_str(vehicle, "RESEARCH_ONLY").upper()
    if value not in {"OPTION", "STOCK", "RESEARCH_ONLY"}:
        return "RESEARCH_ONLY"
    return value


def _direction(strategy: str) -> str:
    return "SHORT" if "PUT" in _safe_str(strategy, "CALL").upper() else "LONG"


def _capital_buffer_after(capital_available: float, capital_required: float) -> float:
    return round(_safe_float(capital_available, 0.0) - _safe_float(capital_required, 0.0), 4)


def _option_price_from_obj(option_obj: Dict[str, Any], fallback: float = 0.0) -> float:
    option_obj = _safe_dict(option_obj)
    return round(
        _first_positive_float(
            option_obj.get("mark"),
            option_obj.get("last"),
            option_obj.get("price"),
            option_obj.get("mid"),
            option_obj.get("ask"),
            fallback,
            default=0.0,
        ),
        4,
    )


def _default_stock_stop(entry: float, direction: str) -> float:
    if entry <= 0:
        return 0.0
    return round(entry * (1.03 if direction == "SHORT" else 0.97), 4)


def _default_stock_target(entry: float, direction: str) -> float:
    if entry <= 0:
        return 0.0
    return round(entry * (0.90 if direction == "SHORT" else 1.10), 4)


def _default_option_stop(entry: float, direction: str) -> float:
    if entry <= 0:
        return 0.0
    return round(entry * (1.35 if direction == "SHORT" else 0.70), 4)


def _default_option_target(entry: float, direction: str) -> float:
    if entry <= 0:
        return 0.0
    return round(entry * (0.65 if direction == "SHORT" else 1.35), 4)


def _calc_unrealized_pnl(
    *,
    vehicle_selected: str,
    strategy: str,
    entry: float,
    current_price: float,
    shares: int,
    contracts: int,
) -> float:
    direction = _direction(strategy)
    if entry <= 0 or current_price <= 0:
        return 0.0

    delta = (entry - current_price) if direction == "SHORT" else (current_price - entry)
    if vehicle_selected == "OPTION":
        return round(delta * max(1, contracts) * OPTION_CONTRACT_MULTIPLIER, 4)
    if vehicle_selected == "STOCK":
        return round(delta * max(1, shares), 4)
    return 0.0


def build_open_trade_state(
    source_trade: Dict[str, Any],
    *,
    lifecycle: Optional[Dict[str, Any]] = None,
    execution_result: Optional[Dict[str, Any]] = None,
    mode: str = "",
    mode_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_trade = deepcopy(_safe_dict(source_trade))
    lifecycle = deepcopy(_safe_dict(lifecycle))
    execution_result = deepcopy(_safe_dict(execution_result))
    execution_record = _safe_dict(execution_result.get("execution_record"))
    mode_context = deepcopy(_safe_dict(mode_context))

    merged: Dict[str, Any] = {}
    merged.update(source_trade)
    merged.update(lifecycle)

    symbol = _norm_symbol(
        merged.get("symbol")
        or execution_record.get("symbol")
        or source_trade.get("symbol")
    )
    strategy = _safe_str(
        merged.get("strategy")
        or execution_record.get("strategy")
        or source_trade.get("strategy"),
        "CALL",
    ).upper()

    vehicle_selected = _vehicle(
        merged.get("vehicle_selected")
        or merged.get("selected_vehicle")
        or merged.get("vehicle")
        or source_trade.get("vehicle_selected")
        or "RESEARCH_ONLY"
    )
    direction = _direction(strategy)

    option_obj = _first_dict(
        merged.get("option"),
        merged.get("contract"),
        source_trade.get("option"),
        source_trade.get("contract"),
    )

    opened_at = _first_nonempty(
        merged.get("opened_at"),
        execution_record.get("opened_at"),
        merged.get("timestamp"),
        source_trade.get("timestamp"),
        _now_iso(),
    )
    timestamp = _first_nonempty(
        merged.get("timestamp"),
        source_trade.get("timestamp"),
        opened_at,
    )

    trade_id = _first_nonempty(
        merged.get("trade_id"),
        execution_record.get("trade_id"),
        source_trade.get("trade_id"),
        default=_derive_trade_id(symbol, strategy, opened_at),
    )

    underlying_price = round(
        _first_positive_float(
            merged.get("underlying_price"),
            merged.get("stock_price"),
            merged.get("price"),
            source_trade.get("underlying_price"),
            source_trade.get("stock_price"),
            source_trade.get("price"),
            default=0.0,
        ),
        4,
    )

    option_entry = _first_positive_float(
        execution_result.get("fill_price"),
        execution_record.get("fill_price"),
        execution_record.get("filled_price"),
        merged.get("option_entry"),
        merged.get("fill_price"),
        merged.get("entry"),
        merged.get("requested_price"),
        merged.get("current_price"),
        _option_price_from_obj(option_obj),
        default=0.0,
    )

    stock_entry = _first_positive_float(
        execution_result.get("fill_price"),
        execution_record.get("fill_price"),
        execution_record.get("filled_price"),
        merged.get("entry"),
        merged.get("requested_price"),
        merged.get("price"),
        underlying_price,
        default=0.0,
    )

    if vehicle_selected == "OPTION":
        entry = round(option_entry, 4)
        current_price = round(
            _first_positive_float(
                merged.get("option_current_price"),
                merged.get("current_option_price"),
                merged.get("current_price"),
                _option_price_from_obj(option_obj, entry),
                entry,
                default=entry,
            ),
            4,
        )
        requested_price = round(
            _first_positive_float(
                execution_record.get("requested_price"),
                merged.get("requested_price"),
                _option_price_from_obj(option_obj, entry),
                entry,
                default=entry,
            ),
            4,
        )
        fill_price = round(
            _first_positive_float(
                execution_result.get("fill_price"),
                execution_record.get("fill_price"),
                execution_record.get("filled_price"),
                entry,
                default=entry,
            ),
            4,
        )
    elif vehicle_selected == "STOCK":
        entry = round(stock_entry, 4)
        current_price = round(
            _first_positive_float(
                merged.get("current_price"),
                merged.get("underlying_price"),
                underlying_price,
                entry,
                default=entry,
            ),
            4,
        )
        requested_price = round(
            _first_positive_float(
                execution_record.get("requested_price"),
                merged.get("requested_price"),
                merged.get("price"),
                entry,
                default=entry,
            ),
            4,
        )
        fill_price = round(
            _first_positive_float(
                execution_result.get("fill_price"),
                execution_record.get("fill_price"),
                execution_record.get("filled_price"),
                entry,
                default=entry,
            ),
            4,
        )
    else:
        entry = 0.0
        current_price = 0.0
        requested_price = 0.0
        fill_price = 0.0

    shares = 0
    contracts = 0
    if vehicle_selected == "OPTION":
        contracts = max(
            1,
            _safe_int(
                execution_record.get("contracts", merged.get("contracts", 1)),
                1,
            ),
        )
    elif vehicle_selected == "STOCK":
        shares = max(
            1,
            _safe_int(
                execution_record.get("shares", merged.get("shares", merged.get("size", 1))),
                1,
            ),
        )

    size = contracts if vehicle_selected == "OPTION" else shares

    capital_required = round(
        _first_positive_float(
            merged.get("capital_required"),
            merged.get("estimated_cost"),
            execution_result.get("actual_cost"),
            0.0,
            default=0.0,
        ),
        4,
    )
    minimum_trade_cost = round(
        _first_positive_float(
            merged.get("minimum_trade_cost"),
            capital_required,
            default=0.0,
        ),
        4,
    )
    capital_available = round(
        _first_positive_float(
            merged.get("capital_available"),
            source_trade.get("capital_available"),
            0.0,
            default=0.0,
        ),
        4,
    )

    if vehicle_selected == "OPTION":
        stop = round(
            _safe_float(
                merged.get("stop", _default_option_stop(entry, direction)),
                _default_option_stop(entry, direction),
            ),
            4,
        )
        target = round(
            _safe_float(
                merged.get("target", _default_option_target(entry, direction)),
                _default_option_target(entry, direction),
            ),
            4,
        )
        monitoring_price_type = "OPTION_PREMIUM"
    elif vehicle_selected == "STOCK":
        stop = round(
            _safe_float(
                merged.get("stop", _default_stock_stop(entry, direction)),
                _default_stock_stop(entry, direction),
            ),
            4,
        )
        target = round(
            _safe_float(
                merged.get("target", _default_stock_target(entry, direction)),
                _default_stock_target(entry, direction),
            ),
            4,
        )
        monitoring_price_type = "UNDERLYING"
    else:
        stop = 0.0
        target = 0.0
        monitoring_price_type = "RESEARCH_ONLY"

    unrealized_pnl = _calc_unrealized_pnl(
        vehicle_selected=vehicle_selected,
        strategy=strategy,
        entry=entry,
        current_price=current_price,
        shares=shares,
        contracts=contracts,
    )

    v2 = _first_dict(merged.get("v2"), source_trade.get("v2"))
    v2_payload = _first_dict(merged.get("v2_payload"), source_trade.get("v2_payload"), v2)

    contract_symbol = _first_nonempty(
        merged.get("contract_symbol"),
        option_obj.get("contract_symbol"),
        option_obj.get("contractSymbol"),
    )
    expiry = _first_nonempty(
        merged.get("expiry"),
        option_obj.get("expiry"),
        option_obj.get("expiration"),
    )

    state = {
        "trade_id": trade_id,
        "symbol": symbol,
        "company_name": _first_nonempty(
            merged.get("company_name"),
            merged.get("company"),
            source_trade.get("company_name"),
            symbol,
        ),
        "sector": _first_nonempty(
            merged.get("sector"),
            source_trade.get("sector"),
            "UNKNOWN",
        ),
        "status": "OPEN",
        "timestamp": timestamp,
        "opened_at": opened_at,
        "closed_at": "",
        "execution_status": _safe_str(
            execution_result.get("status", execution_record.get("status", "FILLED")),
            "FILLED",
        ).upper(),
        "strategy": strategy,
        "direction": direction,
        "vehicle_selected": vehicle_selected,
        "selected_vehicle": vehicle_selected,
        "vehicle": vehicle_selected,
        "shares": shares,
        "contracts": contracts,
        "size": size,
        "price": underlying_price if vehicle_selected != "OPTION" else entry,
        "requested_price": requested_price,
        "fill_price": fill_price,
        "entry": entry,
        "current_price": current_price,
        "current": current_price,
        "option_entry": entry if vehicle_selected == "OPTION" else 0.0,
        "option_current_price": current_price if vehicle_selected == "OPTION" else 0.0,
        "underlying_price": underlying_price,
        "exit_price": 0.0,
        "stop": stop,
        "target": target,
        "commission": round(_safe_float(execution_record.get("commission", merged.get("commission", 0.0)), 0.0), 4),
        "pnl": 0.0,
        "unrealized_pnl": unrealized_pnl,
        "realized_pnl": 0.0,
        "capital_required": capital_required,
        "minimum_trade_cost": minimum_trade_cost,
        "capital_available": capital_available,
        "capital_buffer_after": _capital_buffer_after(capital_available, capital_required),
        "score": round(_safe_float(merged.get("score", 0.0), 0.0), 4),
        "base_score": round(_safe_float(merged.get("base_score", merged.get("score", 0.0)), 0.0), 4),
        "fused_score": round(_safe_float(merged.get("fused_score", merged.get("score", 0.0)), 0.0), 4),
        "confidence": _safe_str(merged.get("confidence", "LOW"), "LOW").upper(),
        "base_confidence": _safe_str(merged.get("base_confidence", merged.get("confidence", "LOW")), "LOW").upper(),
        "v2_confidence": _safe_str(merged.get("v2_confidence", merged.get("confidence", "LOW")), "LOW").upper(),
        "decision_reason": _first_nonempty(
            merged.get("decision_reason"),
            merged.get("final_reason"),
            source_trade.get("decision_reason"),
            "",
        ),
        "decision_reason_code": _first_nonempty(
            merged.get("decision_reason_code"),
            merged.get("final_reason_code"),
            "",
        ),
        "final_reason": _first_nonempty(
            merged.get("final_reason"),
            merged.get("decision_reason"),
            "executed",
        ),
        "final_reason_code": _first_nonempty(
            merged.get("final_reason_code"),
            merged.get("decision_reason_code"),
            "executed",
        ),
        "blocked_at": _safe_str(merged.get("blocked_at"), ""),
        "research_approved": _safe_bool(merged.get("research_approved", True), True),
        "execution_ready": _safe_bool(merged.get("execution_ready", True), True),
        "selected_for_execution": _safe_bool(merged.get("selected_for_execution", True), True),
        "mode": _first_nonempty(mode, merged.get("mode"), ""),
        "trading_mode": _first_nonempty(mode, merged.get("trading_mode"), ""),
        "execution_mode": _first_nonempty(mode, merged.get("execution_mode"), ""),
        "mode_context": mode_context,
        "monitoring_price_type": monitoring_price_type,
        "regime": _safe_str(merged.get("regime"), ""),
        "breadth": _safe_str(merged.get("breadth"), ""),
        "volatility_state": _safe_str(merged.get("volatility_state"), ""),
        "trend": _safe_str(merged.get("trend"), ""),
        "setup_type": _safe_str(merged.get("setup_type"), ""),
        "setup_family": _safe_str(merged.get("setup_family"), ""),
        "entry_quality": _safe_str(merged.get("entry_quality"), ""),
        "atr": round(_safe_float(merged.get("atr", 0.0), 0.0), 4),
        "rsi": round(_safe_float(merged.get("rsi", 0.0), 0.0), 4),
        "option": option_obj,
        "contract": option_obj,
        "contract_symbol": contract_symbol,
        "expiry": expiry,
        "strike": round(_safe_float(merged.get("strike", option_obj.get("strike", 0.0)), 0.0), 4),
        "right": _safe_str(merged.get("right", option_obj.get("right", strategy)), strategy).upper(),
        "mark": round(_safe_float(merged.get("mark", option_obj.get("mark", option_obj.get("last", 0.0))), 0.0), 4),
        "bid": round(_safe_float(merged.get("bid", option_obj.get("bid", 0.0)), 0.0), 4),
        "ask": round(_safe_float(merged.get("ask", option_obj.get("ask", 0.0)), 0.0), 4),
        "last": round(_safe_float(merged.get("last", option_obj.get("last", 0.0)), 0.0), 4),
        "volume": _safe_int(merged.get("volume", option_obj.get("volume", 0)), 0),
        "open_interest": _safe_int(merged.get("open_interest", option_obj.get("open_interest", option_obj.get("openInterest", 0))), 0),
        "dte": _safe_int(merged.get("dte", option_obj.get("dte", option_obj.get("daysToExpiration", 0))), 0),
        "option_contract_score": round(
            _safe_float(
                merged.get("option_contract_score", merged.get("option_score", option_obj.get("contract_score", 0.0))),
                0.0,
            ),
            4,
        ),
        "option_explanation": _first_list(merged.get("option_explanation"), option_obj.get("contract_notes")),
        "option_path": _first_dict(merged.get("option_path"), source_trade.get("option_path")),
        "stock_path": _first_dict(merged.get("stock_path"), source_trade.get("stock_path")),
        "reserve_check": _first_dict(merged.get("reserve_check"), source_trade.get("reserve_check")),
        "governor": _first_dict(merged.get("governor"), source_trade.get("governor")),
        "governor_blocked": _safe_bool(merged.get("governor_blocked", False), False),
        "governor_status": _safe_str(merged.get("governor_status"), ""),
        "governor_reason": _safe_str(merged.get("governor_reason"), ""),
        "governor_reasons": _safe_list(merged.get("governor_reasons")),
        "governor_warnings": _safe_list(merged.get("governor_warnings")),
        "why": _first_list(merged.get("why")),
        "supports": _first_list(merged.get("supports")),
        "blockers": _first_list(merged.get("blockers")),
        "rejection_reason": _safe_str(merged.get("rejection_reason"), ""),
        "rejection_analysis": _first_list(merged.get("rejection_analysis")),
        "stronger_competing_setups": _first_list(merged.get("stronger_competing_setups")),
        "v2": v2,
        "v2_payload": v2_payload,
        "v2_score": round(_safe_float(merged.get("v2_score", v2.get("score", 0.0)), 0.0), 4),
        "v2_quality": round(_safe_float(merged.get("v2_quality", v2.get("quality", 0.0)), 0.0), 4),
        "v2_reason": _safe_str(merged.get("v2_reason", v2.get("reason", "")), ""),
        "v2_regime_alignment": _safe_str(merged.get("v2_regime_alignment", v2.get("regime_alignment", "")), ""),
        "v2_signal_strength": round(_safe_float(merged.get("v2_signal_strength", v2.get("signal_strength", 0.0)), 0.0), 4),
        "v2_conviction_adjustment": round(_safe_float(merged.get("v2_conviction_adjustment", v2.get("conviction_adjustment", 0.0)), 0.0), 4),
        "v2_vehicle_bias": _safe_str(merged.get("v2_vehicle_bias", v2.get("vehicle_bias", "")), "").upper(),
        "v2_thesis": _safe_str(merged.get("v2_thesis", v2.get("thesis", "")), ""),
        "v2_notes": _first_list(merged.get("v2_notes"), v2.get("notes")),
        "v2_risk_flags": _first_list(merged.get("v2_risk_flags"), v2.get("risk_flags")),
        "readiness_score": round(_safe_float(merged.get("readiness_score", 0.0), 0.0), 4),
        "promotion_score": round(_safe_float(merged.get("promotion_score", 0.0), 0.0), 4),
        "rebuild_pressure": round(_safe_float(merged.get("rebuild_pressure", 0.0), 0.0), 4),
        "readiness_notes": _first_list(merged.get("readiness_notes")),
        "promotion_notes": _first_list(merged.get("promotion_notes")),
        "rebuild_notes": _first_list(merged.get("rebuild_notes")),
        "learning_notes": _first_list(merged.get("learning_notes")),
        "learning_exit_notes": _first_list(merged.get("learning_exit_notes")),
        "position_explanation": _first_dict(merged.get("position_explanation")),
        "soulaana": _first_dict(merged.get("soulaana")),
        "monitor_debug": _first_dict(merged.get("monitor_debug")),
        "capital_protection_mode": _safe_bool(merged.get("capital_protection_mode", False), False),
        "capital_protection_snapshot": _first_dict(merged.get("capital_protection_snapshot")),
        "close_reason": "",
        "exit_explanation": {},
        "execution_result": execution_result,
        "raw_source_trade": source_trade,
        "raw_lifecycle": lifecycle,
    }

    return state


def build_closed_trade_state(
    open_trade: Dict[str, Any],
    *,
    exit_price: float,
    close_reason: str,
    closed_at: Optional[str] = None,
    pnl: Optional[float] = None,
    exit_explanation: Optional[Dict[str, Any]] = None,
    capital_release: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    open_trade = deepcopy(_safe_dict(open_trade))
    closed = dict(open_trade)

    resolved_pnl = _safe_float(pnl, 0.0)
    closed["status"] = "CLOSED"
    closed["closed_at"] = _safe_str(closed_at, _now_iso())
    closed["exit_price"] = round(_safe_float(exit_price, 0.0), 4)
    closed["close_reason"] = _safe_str(close_reason, "manual")
    closed["reason"] = closed["close_reason"]
    closed["pnl"] = round(resolved_pnl, 4)
    closed["realized_pnl"] = round(resolved_pnl, 4)
    closed["unrealized_pnl"] = 0.0
    closed["exit_explanation"] = _safe_dict(exit_explanation)
    closed["capital_release"] = _safe_dict(capital_release)
    closed["execution_status"] = "CLOSED"
    return closed


def build_trade_log_row(
    trade_state: Dict[str, Any],
    *,
    event: str = "OPEN",
) -> Dict[str, Any]:
    trade_state = _safe_dict(trade_state)
    event = _safe_str(event, "OPEN").upper()

    return {
        "timestamp": _first_nonempty(trade_state.get("timestamp"), _now_iso()),
        "trade_id": _safe_str(trade_state.get("trade_id"), ""),
        "symbol": _norm_symbol(trade_state.get("symbol")),
        "strategy": _safe_str(trade_state.get("strategy"), "CALL").upper(),
        "vehicle_selected": _safe_str(trade_state.get("vehicle_selected"), "STOCK").upper(),
        "price": round(_safe_float(trade_state.get("price", 0.0), 0.0), 4),
        "requested_price": round(_safe_float(trade_state.get("requested_price", 0.0), 0.0), 4),
        "fill_price": round(_safe_float(trade_state.get("fill_price", 0.0), 0.0), 4),
        "entry": round(_safe_float(trade_state.get("entry", 0.0), 0.0), 4),
        "current_price": round(_safe_float(trade_state.get("current_price", 0.0), 0.0), 4),
        "exit_price": round(_safe_float(trade_state.get("exit_price", 0.0), 0.0), 4),
        "size": _safe_int(trade_state.get("size", 0), 0),
        "shares": _safe_int(trade_state.get("shares", 0), 0),
        "contracts": _safe_int(trade_state.get("contracts", 0), 0),
        "score": round(_safe_float(trade_state.get("score", 0.0), 0.0), 4),
        "fused_score": round(_safe_float(trade_state.get("fused_score", 0.0), 0.0), 4),
        "confidence": _safe_str(trade_state.get("confidence"), "LOW").upper(),
        "status": _safe_str(trade_state.get("status", event), event).upper(),
        "opened_at": _safe_str(trade_state.get("opened_at"), ""),
        "closed_at": _safe_str(trade_state.get("closed_at"), ""),
        "reason": _safe_str(
            trade_state.get("reason")
            or trade_state.get("close_reason")
            or trade_state.get("final_reason"),
            "",
        ),
        "pnl": round(_safe_float(trade_state.get("pnl", 0.0), 0.0), 4),
        "trading_mode": _safe_str(trade_state.get("trading_mode"), ""),
        "mode": _safe_str(trade_state.get("mode"), ""),
        "regime": _safe_str(trade_state.get("regime"), ""),
        "breadth": _safe_str(trade_state.get("breadth"), ""),
        "volatility_state": _safe_str(trade_state.get("volatility_state"), ""),
        "capital_required": round(_safe_float(trade_state.get("capital_required", 0.0), 0.0), 4),
        "minimum_trade_cost": round(_safe_float(trade_state.get("minimum_trade_cost", 0.0), 0.0), 4),
        "capital_available": round(_safe_float(trade_state.get("capital_available", 0.0), 0.0), 4),
        "research_approved": _safe_bool(trade_state.get("research_approved", False), False),
        "execution_ready": _safe_bool(trade_state.get("execution_ready", False), False),
        "selected_for_execution": _safe_bool(trade_state.get("selected_for_execution", False), False),
        "v2_score": round(_safe_float(trade_state.get("v2_score", 0.0), 0.0), 4),
        "v2_reason": _safe_str(trade_state.get("v2_reason"), ""),
        "readiness_score": round(_safe_float(trade_state.get("readiness_score", 0.0), 0.0), 4),
        "promotion_score": round(_safe_float(trade_state.get("promotion_score", 0.0), 0.0), 4),
        "rebuild_pressure": round(_safe_float(trade_state.get("rebuild_pressure", 0.0), 0.0), 4),
        "final_reason": _safe_str(trade_state.get("final_reason"), ""),
        "final_reason_code": _safe_str(trade_state.get("final_reason_code"), ""),
        "monitoring_price_type": _safe_str(trade_state.get("monitoring_price_type"), ""),
        "underlying_price": round(_safe_float(trade_state.get("underlying_price", 0.0), 0.0), 4),
        "option_current_price": round(_safe_float(trade_state.get("option_current_price", 0.0), 0.0), 4),
    }


def build_execution_audit_row(
    trade_state: Dict[str, Any],
    *,
    event_type: str,
    note: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    trade_state = _safe_dict(trade_state)
    extra = _safe_dict(extra)

    row = {
        "timestamp": _now_iso(),
        "event_type": _safe_str(event_type, "UNKNOWN").upper(),
        "trade_id": _safe_str(trade_state.get("trade_id"), ""),
        "symbol": _norm_symbol(trade_state.get("symbol")),
        "strategy": _safe_str(trade_state.get("strategy"), "CALL").upper(),
        "status": _safe_str(trade_state.get("status"), ""),
        "vehicle_selected": _safe_str(trade_state.get("vehicle_selected"), "STOCK").upper(),
        "trading_mode": _safe_str(trade_state.get("trading_mode"), ""),
        "final_reason": _safe_str(trade_state.get("final_reason"), ""),
        "final_reason_code": _safe_str(trade_state.get("final_reason_code"), ""),
        "note": _safe_str(note, ""),
        "payload": deepcopy(trade_state),
    }
    row.update(extra)
    return row


def summarize_trade_state(trade_state: Dict[str, Any]) -> Dict[str, Any]:
    trade_state = _safe_dict(trade_state)
    return {
        "trade_id": _safe_str(trade_state.get("trade_id"), ""),
        "symbol": _norm_symbol(trade_state.get("symbol")),
        "status": _safe_str(trade_state.get("status"), ""),
        "strategy": _safe_str(trade_state.get("strategy"), "CALL").upper(),
        "vehicle_selected": _safe_str(trade_state.get("vehicle_selected"), "STOCK").upper(),
        "entry": round(_safe_float(trade_state.get("entry", 0.0), 0.0), 4),
        "current_price": round(_safe_float(trade_state.get("current_price", 0.0), 0.0), 4),
        "stop": round(_safe_float(trade_state.get("stop", 0.0), 0.0), 4),
        "target": round(_safe_float(trade_state.get("target", 0.0), 0.0), 4),
        "pnl": round(_safe_float(trade_state.get("pnl", 0.0), 0.0), 4),
        "unrealized_pnl": round(_safe_float(trade_state.get("unrealized_pnl", 0.0), 0.0), 4),
        "research_approved": _safe_bool(trade_state.get("research_approved", False), False),
        "execution_ready": _safe_bool(trade_state.get("execution_ready", False), False),
        "selected_for_execution": _safe_bool(trade_state.get("selected_for_execution", False), False),
        "final_reason": _safe_str(trade_state.get("final_reason"), ""),
        "final_reason_code": _safe_str(trade_state.get("final_reason_code"), ""),
        "trading_mode": _safe_str(trade_state.get("trading_mode"), ""),
        "monitoring_price_type": _safe_str(trade_state.get("monitoring_price_type"), ""),
    }


__all__ = [
    "build_open_trade_state",
    "build_closed_trade_state",
    "build_trade_log_row",
    "build_execution_audit_row",
    "summarize_trade_state",
]
