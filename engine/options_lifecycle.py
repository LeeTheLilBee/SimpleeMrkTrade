from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from engine.observatory_mode import build_mode_context, normalize_mode
from engine.vehicle_selector import choose_vehicle

LIFECYCLE_NEW = "NEW"
LIFECYCLE_RESEARCH_APPROVED = "RESEARCH_APPROVED"
LIFECYCLE_RESEARCH_REJECTED = "RESEARCH_REJECTED"
LIFECYCLE_EXECUTION_BLOCKED = "EXECUTION_BLOCKED"
LIFECYCLE_EXECUTION_READY = "EXECUTION_READY"
LIFECYCLE_SELECTED = "SELECTED"
LIFECYCLE_ENTERED = "ENTERED"
LIFECYCLE_MANAGING = "MANAGING"
LIFECYCLE_EXIT_READY = "EXIT_READY"
LIFECYCLE_CLOSED = "CLOSED"

VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_NONE = "NONE"
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"

DECISION_APPROVE = "APPROVE"
DECISION_REJECT = "REJECT"
DECISION_WARN = "WARN"
DECISION_WATCH = "WATCH"


def _now_iso() -> str:
    return datetime.now().isoformat()


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


def _upper(value: Any, default: str = "") -> str:
    return _safe_str(value, default).upper()


def _dedupe(items: List[Any]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        text = _safe_str(item, "")
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _best_price(candidate: Dict[str, Any]) -> float:
    for key in [
        "underlying_price",
        "current_price",
        "price",
        "entry",
        "fill_price",
        "requested_price",
        "stock_price",
        "market_price",
        "latest_price",
    ]:
        value = _safe_float(candidate.get(key), 0.0)
        if value > 0:
            return value
    return 0.0


def _direction_from_strategy(strategy: str) -> str:
    strategy = _upper(strategy, "UNKNOWN")
    if strategy in {"CALL", "LONG_CALL"}:
        return "CALL"
    if strategy in {"PUT", "LONG_PUT"}:
        return "PUT"
    return "UNKNOWN"


def _normalize_vehicle(value: Any) -> str:
    vehicle = _upper(value, VEHICLE_NONE)
    if vehicle in {VEHICLE_OPTION, VEHICLE_STOCK, VEHICLE_NONE, VEHICLE_RESEARCH_ONLY}:
        return vehicle
    return VEHICLE_NONE


@dataclass
class LifecycleState:
    symbol: str = ""
    strategy: str = ""
    direction: str = "UNKNOWN"

    lifecycle_stage: str = LIFECYCLE_NEW

    selected_vehicle: str = VEHICLE_NONE
    vehicle_selected: str = VEHICLE_NONE
    fallback_vehicle: str = VEHICLE_NONE

    research_approved: bool = False
    execution_ready: bool = False
    selected_for_execution: bool = False

    research_decision: str = DECISION_REJECT
    execution_decision: str = DECISION_REJECT
    final_decision: str = DECISION_REJECT

    research_reason: str = ""
    execution_reason: str = ""
    final_reason: str = ""

    research_reason_code: str = ""
    execution_reason_code: str = ""
    final_reason_code: str = ""

    decision_reason: str = ""
    decision_reason_code: str = ""
    blocked_at: str = ""

    score: float = 0.0
    base_score: float = 0.0
    fused_score: float = 0.0
    confidence: str = "LOW"

    v2: Dict[str, Any] = field(default_factory=dict)
    v2_payload: Dict[str, Any] = field(default_factory=dict)
    v2_score: float = 0.0
    v2_quality: float = 0.0
    v2_reason: str = ""
    v2_vehicle_bias: str = ""
    v2_thesis: str = ""
    v2_notes: List[Any] = field(default_factory=list)
    v2_risk_flags: List[Any] = field(default_factory=list)

    readiness_score: float = 0.0
    promotion_score: float = 0.0
    rebuild_pressure: float = 0.0
    execution_quality: float = 0.0

    price: float = 0.0
    underlying_price: float = 0.0
    candidate_size_dollars: float = 0.0
    capital_required: float = 0.0
    minimum_trade_cost: float = 0.0
    capital_available: float = 0.0
    capital_buffer_after: float = 0.0
    estimated_cost: float = 0.0

    shares: int = 0
    contracts: int = 0

    option: Dict[str, Any] = field(default_factory=dict)
    contract: Dict[str, Any] = field(default_factory=dict)
    option_path: Dict[str, Any] = field(default_factory=dict)
    stock_path: Dict[str, Any] = field(default_factory=dict)
    reserve_check: Dict[str, Any] = field(default_factory=dict)
    vehicle_diagnostics: Dict[str, Any] = field(default_factory=dict)
    governor: Dict[str, Any] = field(default_factory=dict)
    mode_context: Dict[str, Any] = field(default_factory=dict)

    setup_type: str = ""
    setup_family: str = ""
    entry_quality: str = ""
    trend: str = ""
    regime: str = ""
    breadth: str = ""
    volatility_state: str = ""
    mode: str = ""
    trading_mode: str = ""
    execution_mode: str = ""

    why: List[Any] = field(default_factory=list)
    supports: List[Any] = field(default_factory=list)
    blockers: List[Any] = field(default_factory=list)
    warnings: List[Any] = field(default_factory=list)
    rejection_reasons: List[Any] = field(default_factory=list)
    rejection_analysis: List[Any] = field(default_factory=list)
    option_explanation: List[Any] = field(default_factory=list)
    stronger_competing_setups: List[Any] = field(default_factory=list)
    learning_notes: List[Any] = field(default_factory=list)

    trade_id: str = ""
    timestamp: str = ""
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    entered_at: str = ""
    exited_at: str = ""

    raw: Dict[str, Any] = field(default_factory=dict)


def _block(life: LifecycleState, reason: str, reason_code: str, blocked_at: str) -> Dict[str, Any]:
    life.lifecycle_stage = LIFECYCLE_EXECUTION_BLOCKED
    life.execution_ready = False
    life.selected_for_execution = False
    life.execution_decision = DECISION_REJECT
    life.execution_reason = reason
    life.execution_reason_code = reason_code
    life.final_decision = DECISION_REJECT
    life.final_reason = reason
    life.final_reason_code = reason_code
    life.decision_reason = reason
    life.decision_reason_code = reason_code
    life.blocked_at = blocked_at
    life.updated_at = _now_iso()

    if life.selected_vehicle in {"", VEHICLE_NONE}:
        life.selected_vehicle = VEHICLE_RESEARCH_ONLY
        life.vehicle_selected = VEHICLE_RESEARCH_ONLY

    return asdict(life)


def build_options_lifecycle(
    candidate: Dict[str, Any],
    option_chain: List[Dict[str, Any]],
    account_context: Dict[str, Any],
    mode: str = "paper",
    allow_stock_fallback: bool = True,
) -> Dict[str, Any]:
    candidate = _safe_dict(candidate)
    option_chain = _safe_list(option_chain)
    account_context = _safe_dict(account_context)

    trading_mode = normalize_mode(
        mode
        or candidate.get("trading_mode")
        or candidate.get("execution_mode")
        or candidate.get("mode")
        or "paper"
    )

    mode_context = build_mode_context(trading_mode)
    incoming_mode_context = _safe_dict(candidate.get("mode_context"))
    mode_context.update({k: v for k, v in incoming_mode_context.items() if v is not None})

    symbol = _upper(candidate.get("symbol"), "UNKNOWN")
    strategy = _upper(candidate.get("strategy"), "CALL")
    direction = _upper(candidate.get("direction"), _direction_from_strategy(strategy))

    price = _best_price(candidate)
    cash_available = _safe_float(
        account_context.get("cash_available", account_context.get("cash", candidate.get("capital_available", 0.0))),
        0.0,
    )

    reserve_floor_pct = _safe_float(mode_context.get("reserve_floor_pct"), 0.0)
    reserve_floor_dollars = round(cash_available * reserve_floor_pct, 2) if reserve_floor_pct > 0 else 0.0

    strict_execution_gate = _safe_bool(mode_context.get("strict_execution_gate"), True)
    reserve_warning_only = _safe_bool(mode_context.get("reserve_warning_only"), False)
    execution_warning_only = _safe_bool(mode_context.get("execution_warning_only"), False)
    warning_only_mode = reserve_warning_only or execution_warning_only or not strict_execution_gate

    life = LifecycleState(
        symbol=symbol,
        strategy=strategy,
        direction=direction,
        score=round(_safe_float(candidate.get("score"), 0.0), 4),
        base_score=round(_safe_float(candidate.get("base_score", candidate.get("score", 0.0)), 0.0), 4),
        fused_score=round(_safe_float(candidate.get("fused_score", candidate.get("score", 0.0)), 0.0), 4),
        confidence=_upper(candidate.get("confidence"), "LOW"),
        price=round(price, 4),
        underlying_price=round(price, 4),
        capital_available=round(cash_available, 4),
        capital_required=round(_safe_float(candidate.get("capital_required"), 0.0), 4),
        minimum_trade_cost=round(_safe_float(candidate.get("minimum_trade_cost"), 0.0), 4),
        candidate_size_dollars=round(_safe_float(candidate.get("candidate_size_dollars", candidate.get("capital_required", price)), 0.0), 4),
        v2=_safe_dict(candidate.get("v2")),
        v2_payload=_safe_dict(candidate.get("v2_payload")) or _safe_dict(candidate.get("v2")),
        v2_score=round(_safe_float(candidate.get("v2_score", _safe_dict(candidate.get("v2")).get("score", 0.0)), 0.0), 4),
        v2_quality=round(_safe_float(candidate.get("v2_quality", _safe_dict(candidate.get("v2")).get("quality", 0.0)), 0.0), 4),
        v2_reason=_safe_str(candidate.get("v2_reason", _safe_dict(candidate.get("v2")).get("reason", "")), ""),
        v2_vehicle_bias=_upper(candidate.get("v2_vehicle_bias", _safe_dict(candidate.get("v2")).get("vehicle_bias", "")), ""),
        v2_thesis=_safe_str(candidate.get("v2_thesis", _safe_dict(candidate.get("v2")).get("thesis", "")), ""),
        v2_notes=_safe_list(candidate.get("v2_notes", _safe_dict(candidate.get("v2")).get("notes", []))),
        v2_risk_flags=_safe_list(candidate.get("v2_risk_flags", _safe_dict(candidate.get("v2")).get("risk_flags", []))),
        readiness_score=round(_safe_float(candidate.get("readiness_score"), 0.0), 4),
        promotion_score=round(_safe_float(candidate.get("promotion_score"), 0.0), 4),
        rebuild_pressure=round(_safe_float(candidate.get("rebuild_pressure"), 0.0), 4),
        execution_quality=round(_safe_float(candidate.get("execution_quality"), 0.0), 4),
        setup_type=_safe_str(candidate.get("setup_type"), ""),
        setup_family=_safe_str(candidate.get("setup_family"), ""),
        entry_quality=_safe_str(candidate.get("entry_quality"), ""),
        trend=_safe_str(candidate.get("trend"), ""),
        regime=_safe_str(candidate.get("regime"), ""),
        breadth=_safe_str(candidate.get("breadth"), ""),
        volatility_state=_safe_str(candidate.get("volatility_state"), ""),
        mode=trading_mode,
        trading_mode=trading_mode,
        execution_mode=trading_mode,
        mode_context=mode_context,
        why=_safe_list(candidate.get("why")),
        supports=_safe_list(candidate.get("supports")),
        blockers=_safe_list(candidate.get("blockers")),
        warnings=_safe_list(candidate.get("warnings")),
        rejection_reasons=_safe_list(candidate.get("rejection_reasons")),
        rejection_analysis=_safe_list(candidate.get("rejection_analysis")),
        option_explanation=_safe_list(candidate.get("option_explanation")),
        stronger_competing_setups=_safe_list(candidate.get("stronger_competing_setups")),
        learning_notes=_safe_list(candidate.get("learning_notes")),
        governor=_safe_dict(candidate.get("governor")),
        trade_id=_safe_str(candidate.get("trade_id"), ""),
        timestamp=_safe_str(candidate.get("timestamp"), _now_iso()),
        raw=dict(candidate),
    )

    life.raw["trading_mode"] = trading_mode
    life.raw["execution_mode"] = trading_mode
    life.raw["mode"] = trading_mode
    life.raw["mode_context"] = mode_context

    if not _safe_bool(candidate.get("research_approved"), False):
        life.lifecycle_stage = LIFECYCLE_RESEARCH_REJECTED
        life.research_approved = False
        life.research_decision = DECISION_REJECT
        life.research_reason = _safe_str(candidate.get("research_reason"), "Research gate did not approve this setup.")
        life.research_reason_code = _safe_str(candidate.get("research_reason_code"), "research_rejected")
        life.final_decision = DECISION_REJECT
        life.final_reason = life.research_reason
        life.final_reason_code = life.research_reason_code
        life.decision_reason = life.final_reason
        life.decision_reason_code = life.final_reason_code
        life.blocked_at = "research_gate"
        return asdict(life)

    life.research_approved = True
    life.lifecycle_stage = LIFECYCLE_RESEARCH_APPROVED
    life.research_decision = DECISION_APPROVE
    life.research_reason = _safe_str(candidate.get("research_reason"), "Research gate approved the setup.")
    life.research_reason_code = _safe_str(candidate.get("research_reason_code"), "research_approved")

    preselected_vehicle = _normalize_vehicle(
        candidate.get("vehicle_selected") or candidate.get("selected_vehicle") or candidate.get("vehicle")
    )

    existing_option = _safe_dict(candidate.get("option")) or _safe_dict(candidate.get("contract"))
    preserve_existing_vehicle = (
        preselected_vehicle in {VEHICLE_OPTION, VEHICLE_STOCK}
        and _safe_bool(candidate.get("execution_ready"), False)
    )

    if preserve_existing_vehicle:
        life.selected_vehicle = preselected_vehicle
        life.vehicle_selected = preselected_vehicle
        life.vehicle_diagnostics = _safe_dict(candidate.get("vehicle_diagnostics"))
        life.option_path = _safe_dict(candidate.get("option_path"))
        life.stock_path = _safe_dict(candidate.get("stock_path"))
        life.contract = existing_option
        life.option = existing_option

        life.capital_required = round(_safe_float(candidate.get("capital_required"), 0.0), 4)
        life.minimum_trade_cost = round(_safe_float(candidate.get("minimum_trade_cost"), life.capital_required), 4)
        life.estimated_cost = life.minimum_trade_cost

        if preselected_vehicle == VEHICLE_OPTION:
            life.contracts = max(1, _safe_int(candidate.get("contracts"), 1))
            life.shares = 0
        else:
            life.shares = max(1, _safe_int(candidate.get("shares", candidate.get("size", 1)), 1))
            life.contracts = 0
    else:
        vehicle = choose_vehicle(
            symbol=symbol,
            strategy=strategy,
            trade_intent=_safe_str(candidate.get("trade_intent"), "GRIND"),
            option_chain=option_chain,
            stock_price=price,
            available_capital=cash_available,
            stock_allowed=bool(allow_stock_fallback),
            trading_mode=trading_mode,
        )

        vehicle = _safe_dict(vehicle)
        life.selected_vehicle = _normalize_vehicle(vehicle.get("vehicle_selected"))
        life.vehicle_selected = life.selected_vehicle
        life.vehicle_diagnostics = _safe_dict(vehicle.get("vehicle_diagnostics"))
        life.capital_required = round(_safe_float(vehicle.get("capital_required"), 0.0), 4)
        life.minimum_trade_cost = round(_safe_float(vehicle.get("minimum_trade_cost"), 0.0), 4)
        life.estimated_cost = life.minimum_trade_cost
        life.shares = _safe_int(vehicle.get("shares"), 0)
        life.contracts = _safe_int(vehicle.get("contracts"), 0)
        life.decision_reason = _safe_str(vehicle.get("vehicle_reason"), "")
        life.option_path = _safe_dict(vehicle.get("option_path"))
        life.stock_path = _safe_dict(vehicle.get("stock_path"))

        option_result = _safe_dict(vehicle.get("option_result"))
        option_preview = _safe_dict(option_result.get("best_option_preview"))

        if option_preview:
            life.option = option_preview
            life.contract = option_preview
            life.option_explanation = _dedupe(life.option_explanation + _safe_list(option_result.get("option_notes")))

        if _safe_str(option_result.get("option_reason"), ""):
            life.rejection_reasons = _dedupe(life.rejection_reasons + [option_result.get("option_reason")])

    life.capital_buffer_after = round(cash_available - life.minimum_trade_cost, 4)

    reserve_pressure = reserve_floor_dollars > 0 and life.capital_buffer_after < reserve_floor_dollars
    life.reserve_check = {
        "mode": trading_mode,
        "cash_available": round(cash_available, 4),
        "minimum_trade_cost": life.minimum_trade_cost,
        "capital_buffer_after": life.capital_buffer_after,
        "reserve_floor_pct": reserve_floor_pct,
        "reserve_floor_dollars": reserve_floor_dollars,
        "is_pressure": reserve_pressure,
        "warning_only": warning_only_mode,
        "hard_block": reserve_pressure and not warning_only_mode,
        "reason_code": "cash_reserve_would_be_broken" if reserve_pressure else "ok",
    }

    if life.selected_vehicle in {VEHICLE_NONE, VEHICLE_RESEARCH_ONLY, ""}:
        return _block(
            life,
            reason="No executable vehicle passed lifecycle rules.",
            reason_code=_safe_str(life.decision_reason, "no_vehicle_selected"),
            blocked_at="options_lifecycle",
        )

    if life.minimum_trade_cost <= 0:
        return _block(
            life,
            reason="Lifecycle could not determine a valid trade cost.",
            reason_code="invalid_trade_cost",
            blocked_at="options_lifecycle",
        )

    if cash_available <= 0:
        return _block(
            life,
            reason="No buying power available.",
            reason_code="no_buying_power",
            blocked_at="options_lifecycle",
        )

    if life.minimum_trade_cost > cash_available:
        return _block(
            life,
            reason="Not enough capital for selected vehicle.",
            reason_code="insufficient_capital",
            blocked_at="options_lifecycle",
        )

    if reserve_pressure:
        if warning_only_mode:
            life.warnings = _dedupe(life.warnings + ["cash_reserve_would_be_broken"])
        else:
            return _block(
                life,
                reason="Reserve protection blocked the selected vehicle.",
                reason_code="cash_reserve_would_be_broken",
                blocked_at="options_lifecycle",
            )

    if life.selected_vehicle == VEHICLE_OPTION and not life.option:
        return _block(
            life,
            reason="Option vehicle selected but no contract survived into lifecycle.",
            reason_code="missing_option_contract",
            blocked_at="options_lifecycle",
        )

    if life.selected_vehicle == VEHICLE_OPTION:
        life.contracts = max(1, life.contracts or 1)
        life.shares = 0
    elif life.selected_vehicle == VEHICLE_STOCK:
        life.shares = max(1, life.shares or 1)
        life.contracts = 0

    life.execution_ready = True
    life.blocked_at = ""

    if _safe_bool(candidate.get("selected_for_execution"), False):
        life.selected_for_execution = True
        life.lifecycle_stage = LIFECYCLE_SELECTED
        life.final_reason = "selected_for_execution"
        life.final_reason_code = "selected_for_execution"
    else:
        life.lifecycle_stage = LIFECYCLE_EXECUTION_READY
        life.final_reason = "Vehicle selected for execution."
        life.final_reason_code = life.decision_reason or "vehicle_selected"

    if life.warnings and warning_only_mode:
        life.execution_decision = DECISION_WARN
        life.execution_reason = "Vehicle selected with lifecycle warnings."
        life.execution_reason_code = "execution_warning_only"
        life.final_decision = DECISION_WARN
    else:
        life.execution_decision = DECISION_APPROVE
        life.execution_reason = "Vehicle selected for execution."
        life.execution_reason_code = life.final_reason_code
        life.final_decision = DECISION_APPROVE

    life.decision_reason = life.final_reason
    life.decision_reason_code = life.final_reason_code
    life.updated_at = _now_iso()

    return asdict(life)


def advance_lifecycle(
    lifecycle_obj: Dict[str, Any],
    new_stage: str,
    reason: str = "",
    reason_code: str = "",
    extra_updates: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    obj = dict(lifecycle_obj or {})
    obj["lifecycle_stage"] = new_stage
    obj["updated_at"] = _now_iso()

    if reason:
        obj["final_reason"] = reason
        obj["decision_reason"] = reason
    if reason_code:
        obj["final_reason_code"] = reason_code
        obj["decision_reason_code"] = reason_code

    if new_stage == LIFECYCLE_ENTERED and not obj.get("entered_at"):
        obj["entered_at"] = _now_iso()
    if new_stage == LIFECYCLE_CLOSED and not obj.get("exited_at"):
        obj["exited_at"] = _now_iso()

    if extra_updates:
        obj.update(extra_updates)

    return obj


def mark_selected(lifecycle_obj: Dict[str, Any]) -> Dict[str, Any]:
    obj = advance_lifecycle(
        lifecycle_obj,
        LIFECYCLE_SELECTED,
        reason="Candidate selected for execution queue.",
        reason_code="selected_for_execution",
    )
    obj["selected_for_execution"] = True
    obj["execution_ready"] = True
    return obj


def mark_entered(
    lifecycle_obj: Dict[str, Any],
    fill_price: float,
    quantity: int,
    extra_updates: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    updates = {
        "fill_price": round(_safe_float(fill_price), 4),
        "filled_quantity": _safe_int(quantity),
        "status": "OPEN",
        "execution_ready": True,
        "selected_for_execution": True,
    }
    if extra_updates:
        updates.update(extra_updates)

    return advance_lifecycle(
        lifecycle_obj,
        LIFECYCLE_ENTERED,
        reason="Position entered.",
        reason_code="entered",
        extra_updates=updates,
    )


def mark_managing(lifecycle_obj: Dict[str, Any], reason: str = "Position is active and under management.") -> Dict[str, Any]:
    return advance_lifecycle(
        lifecycle_obj,
        LIFECYCLE_MANAGING,
        reason=reason,
        reason_code="managing",
    )


def mark_exit_ready(lifecycle_obj: Dict[str, Any], exit_reason: str, exit_reason_code: str = "exit_ready") -> Dict[str, Any]:
    return advance_lifecycle(
        lifecycle_obj,
        LIFECYCLE_EXIT_READY,
        reason=exit_reason,
        reason_code=exit_reason_code,
    )


def mark_closed(
    lifecycle_obj: Dict[str, Any],
    exit_price: float,
    pnl: float,
    extra_updates: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    updates = {
        "exit_price": round(_safe_float(exit_price), 4),
        "pnl": round(_safe_float(pnl), 4),
        "status": "CLOSED",
    }
    if extra_updates:
        updates.update(extra_updates)

    return advance_lifecycle(
        lifecycle_obj,
        LIFECYCLE_CLOSED,
        reason="Position closed.",
        reason_code="closed",
        extra_updates=updates,
    )


def summarize_lifecycle(lifecycle_obj: Dict[str, Any]) -> Dict[str, Any]:
    obj = _safe_dict(lifecycle_obj)
    reserve = _safe_dict(obj.get("reserve_check"))

    return {
        "symbol": obj.get("symbol"),
        "trade_id": obj.get("trade_id"),
        "strategy": obj.get("strategy"),
        "lifecycle_stage": obj.get("lifecycle_stage"),
        "selected_vehicle": obj.get("selected_vehicle"),
        "research_approved": obj.get("research_approved"),
        "execution_ready": obj.get("execution_ready"),
        "selected_for_execution": obj.get("selected_for_execution"),
        "final_decision": obj.get("final_decision"),
        "final_reason": obj.get("final_reason"),
        "final_reason_code": obj.get("final_reason_code"),
        "score": obj.get("score"),
        "fused_score": obj.get("fused_score"),
        "v2_score": obj.get("v2_score"),
        "readiness_score": obj.get("readiness_score"),
        "promotion_score": obj.get("promotion_score"),
        "rebuild_pressure": obj.get("rebuild_pressure"),
        "vehicle_selected": obj.get("vehicle_selected"),
        "capital_required": obj.get("capital_required"),
        "minimum_trade_cost": obj.get("minimum_trade_cost"),
        "capital_available": obj.get("capital_available"),
        "capital_buffer_after": obj.get("capital_buffer_after"),
        "reserve_pressure": reserve.get("is_pressure", False),
        "reserve_warning_only": reserve.get("warning_only", False),
        "reserve_hard_block": reserve.get("hard_block", False),
        "warnings": obj.get("warnings", []),
        "rejection_reasons": obj.get("rejection_reasons", []),
        "trading_mode": obj.get("trading_mode") or obj.get("mode"),
    }


__all__ = [
    "LIFECYCLE_NEW",
    "LIFECYCLE_RESEARCH_APPROVED",
    "LIFECYCLE_RESEARCH_REJECTED",
    "LIFECYCLE_EXECUTION_BLOCKED",
    "LIFECYCLE_EXECUTION_READY",
    "LIFECYCLE_SELECTED",
    "LIFECYCLE_ENTERED",
    "LIFECYCLE_MANAGING",
    "LIFECYCLE_EXIT_READY",
    "LIFECYCLE_CLOSED",
    "VEHICLE_OPTION",
    "VEHICLE_STOCK",
    "VEHICLE_NONE",
    "VEHICLE_RESEARCH_ONLY",
    "DECISION_APPROVE",
    "DECISION_REJECT",
    "DECISION_WARN",
    "DECISION_WATCH",
    "LifecycleState",
    "build_options_lifecycle",
    "advance_lifecycle",
    "mark_selected",
    "mark_entered",
    "mark_managing",
    "mark_exit_ready",
    "mark_closed",
    "summarize_lifecycle",
]
